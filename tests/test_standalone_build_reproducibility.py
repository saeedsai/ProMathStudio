"""Reproducible standalone build regression.

Runs scripts/build.py in a temporary copy, never modifying the checkout.
Checks idempotence and embedded-source parity for every registered module.
"""
import ast
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build.py"


def declared_modules():
    tree = ast.parse(BUILD.read_text(encoding="utf-8"))
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "modules"
            for target in statement.targets
        ):
            return ast.literal_eval(statement.value)
    raise AssertionError("No declared module list in scripts/build.py")


class StandaloneBuildReproducibilityTests(unittest.TestCase):
    def test_module_source_mapping_is_unique(self):
        modules = declared_modules()
        self.assertTrue(modules)
        self.assertEqual(len(modules), len(set(tag for tag, _ in modules)))
        self.assertEqual(len(modules), len(set(path for _, path in modules)))
        for tag, path in modules:
            self.assertTrue(re.fullmatch(r"[a-z0-9-]+", tag), tag)
            self.assertTrue((ROOT / path).is_file(), path)

    def test_rebuild_twice_is_identical_and_embeds_sources(self):
        modules = declared_modules()
        with tempfile.TemporaryDirectory() as folder:
            dest = Path(folder)
            (dest / "scripts").mkdir()
            (dest / "src").mkdir()
            shutil.copy2(BUILD, dest / "scripts" / "build.py")
            shutil.copy2(ROOT / "index.html", dest / "index.html")
            for _, path in modules:
                target = dest / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / path, target)
            command = [sys.executable, str(dest / "scripts" / "build.py")]
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
            first = (dest / "index.html").read_bytes()
            subprocess.run(command, check=True, capture_output=True, text=True, timeout=30)
            self.assertEqual(first, (dest / "index.html").read_bytes())
            html = first.decode("utf-8")
            for tag, path in modules:
                marker = f'<script id="{tag}">\\n'.replace("\\n", "\n")
                self.assertEqual(html.count(marker), 1, tag)
                embedded = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
                source = (dest / path).read_text(encoding="utf-8").rstrip("\n")
                self.assertEqual(embedded, source, path)


if __name__ == "__main__":
    unittest.main()
