"""Regression for the standalone builder's read-only consistency mode."""
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build.py"


class StandaloneCheckTests(unittest.TestCase):
    def test_rejects_unknown_arguments_without_writing(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            (root / "scripts" / "build.py").write_text(BUILDER.read_text(encoding="utf-8"), encoding="utf-8")
            index = root / "index.html"
            index.write_text("unchanged", encoding="utf-8")
            for extra in (["--unknown"], ["--check", "--unknown"]):
                result = subprocess.run([sys.executable, str(root / "scripts" / "build.py"), *extra], capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Usage:", result.stderr)
                self.assertEqual(index.read_text(encoding="utf-8"), "unchanged")

    def test_check_uses_original_index_snapshot(self):
        """A concurrent index move must not cause a second read in --check."""
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            script = BUILDER.read_text(encoding="utf-8")
            entries = re.findall(r'^    \("([^"]+)", "(src/[^"]+)"\),$', script, re.M)
            self.assertGreater(len(entries), 20)
            for _, source_path in entries:
                (root / source_path).write_text("window.fixture = true;\n", encoding="utf-8")
            index = root / "index.html"
            index.write_text("<!doctype html>\n" + "".join(
                f'<script id="{tag}">\nwindow.fixture = true;\n</script>\n'
                for tag, _ in entries), encoding="utf-8")
            instrumented = script.replace(
                "original_index_text = text",
                'original_index_text = text\nindex.rename(root / "moved.html")',
                1,
            )
            self.assertNotEqual(instrumented, script)
            (root / "scripts" / "build.py").write_text(instrumented, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "build.py"), "--check"],
                capture_output=True, text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("matches modular sources", result.stdout)
            self.assertFalse(index.exists())
            self.assertTrue((root / "moved.html").exists())

    def test_check_detects_drift_without_rewriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            script = BUILDER.read_text(encoding="utf-8")
            (root / "scripts" / "build.py").write_text(script, encoding="utf-8")
            entries = re.findall(r'^    \("([^"]+)", "(src/[^"]+)"\),$', script, re.M)
            self.assertGreater(len(entries), 20)
            parts = []
            for tag, path in entries:
                (root / path).write_text("window.fixture = true;\n", encoding="utf-8")
                parts.append(f'<script id="{tag}">\nwindow.fixture = true;\n</script>\n')
            index = root / "index.html"
            original = "<!doctype html>\n" + "".join(parts)
            index.write_text(original, encoding="utf-8")
            cmd = [sys.executable, str(root / "scripts" / "build.py"), "--check"]
            ok = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(ok.returncode, 0, ok.stderr)
            self.assertEqual(index.read_text(encoding="utf-8"), original)
            drift = original.replace("window.fixture = true;", "window.fixture = false;", 1)
            index.write_text(drift, encoding="utf-8")
            failed = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(failed.returncode, 0)
            self.assertIn("out of sync", failed.stderr)
            self.assertIn("near line 3, column 18", failed.stderr)
            self.assertIn("module: src/data-tables.js", failed.stderr)
            self.assertIn("mismatched modules: 1", failed.stderr)
            # A second independent module must be counted without modifying the file.
            second_drift = drift.replace("window.fixture = true;", "window.fixture = false;", 1)
            index.write_text(second_drift, encoding="utf-8")
            multiple = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(multiple.returncode, 0)
            self.assertIn("mismatched modules: 2", multiple.stderr)
            self.assertEqual(index.read_text(encoding="utf-8"), second_drift)
            index.write_text(drift, encoding="utf-8")
            self.assertEqual(index.read_text(encoding="utf-8"), drift)
            repaired = subprocess.run(cmd[:-1], capture_output=True, text=True)
            self.assertEqual(repaired.returncode, 0, repaired.stderr)
            self.assertEqual(index.read_text(encoding="utf-8"), original)
            # An unchanged normal build must not touch the file timestamp.
            os.utime(index, ns=(1_600_000_000_000_000_000, 1_600_000_000_000_000_000))
            before = index.stat().st_mtime_ns
            unchanged = subprocess.run(cmd[:-1], capture_output=True, text=True)
            self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
            self.assertIn("already up to date", unchanged.stdout)
            self.assertEqual(index.stat().st_mtime_ns, before)
            self.assertEqual(index.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
