#!/usr/bin/env python3
"""Audit Quality workflow smoke registration without skipping any existing regression.

A smoke test is a tests/smoke_*.py file. All must be explicitly run exactly
once by Quality; Python unittest tests are run by the workflow's discover step.
This intentionally fails closed when the workflow layout changes unexpectedly.
"""
from collections import Counter
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DIRECT_RUN = re.compile(r"^\s*run:\s*((?:python(?:3)?|node\s+--test)\s+tests/[\w.-]+\.(?:py|js))\s*$", re.MULTILINE)
TEST_PATH = re.compile(r"tests/[\w.-]+\.(?:py|js)$")
DISCOVERY = re.compile(r"^\s*run:\s*python\s+-m\s+unittest\s+discover\s+-s\s+tests\s+-p\s+['\"]?test_\*\.py['\"]?(?:\s+(?:-v|--verbose))?\s*$", re.MULTILINE)


def audit(root: Path, workflow_text: str) -> dict:
    """Return coverage summary or raise ValueError listing all registration defects."""
    tests_dir = root / "tests"
    smoke = {f"tests/{p.name}" for p in tests_dir.glob("smoke_*.py") if p.is_file()}
    if not smoke:
        raise ValueError("No browser smoke tests found; refusing empty CI registration")
    commands = DIRECT_RUN.findall(workflow_text)
    paths = [TEST_PATH.search(command).group(0) for command in commands]
    counts = Counter(paths)
    missing_files = sorted(p for p in counts if not (root / p).is_file())
    unregistered_smoke = sorted(smoke.difference(counts))
    duplicate_tests = sorted(p for p, count in counts.items() if count > 1)
    missing_discovery = not DISCOVERY.search(workflow_text)
    problems = []
    if missing_files:
        problems.append("missing files referenced by Quality: " + ", ".join(missing_files))
    if unregistered_smoke:
        problems.append("unregistered smoke files: " + ", ".join(unregistered_smoke))
    if duplicate_tests:
        problems.append("duplicate test runs: " + ", ".join(duplicate_tests))
    if missing_discovery:
        problems.append("Python unittest discovery step is missing or changed")
    if problems:
        raise ValueError("Quality test registration audit failed:\n" + "\n".join(problems))
    return {"smoke_registered": len(smoke), "direct_test_commands": len(commands),
            "python_unittest_discovery": True}


def main():
    workflow = ROOT / ".github" / "workflows" / "quality.yml"
    try:
        result = audit(ROOT, workflow.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Quality audit passed: {result['smoke_registered']} distinct smoke files registered, "
          f"{result['direct_test_commands']} direct test commands, unittest discovery present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
