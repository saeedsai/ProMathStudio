"""The standalone HTML builder must never leave a partial bundle on disk."""
import re
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build.py"


def make_fixture(root, builder_source):
    (root / "scripts").mkdir()
    (root / "src").mkdir()
    (root / "scripts" / "build.py").write_text(builder_source, encoding="utf-8")
    entries = re.findall(r'^    \("([^"]+)", "(src/[^"]+)"\),$', builder_source, re.M)
    if len(entries) < 20:
        raise AssertionError("Fixture could not discover standalone module mappings")
    parts = ["<!doctype html>\n"]
    for tag, path in entries:
        (root / path).write_text("window.fixture = true;\n", encoding="utf-8")
        parts.append(f'<script id="{tag}">\nwindow.fixture = false;\n</script>\n')
    index = root / "index.html"
    original = "".join(parts)
    index.write_text(original, encoding="utf-8")
    return index, original


class AtomicStandaloneBuildTests(unittest.TestCase):
    def test_failed_replace_keeps_original_and_removes_temporary_output(self):
        source = BUILDER.read_text(encoding="utf-8")
        anchor = "os.replace(staged, index)"
        self.assertEqual(source.count(anchor), 1)
        broken = source.replace(anchor, 'raise OSError("injected replace failure")', 1)
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index, original = make_fixture(root, broken)
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "build.py")],
                capture_output=True, text=True, timeout=15,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("injected replace failure", result.stderr)
            self.assertEqual(index.read_text(encoding="utf-8"), original)
            self.assertEqual(list(root.glob(".promath-index-*.tmp")), [])

    def test_successful_rebuild_keeps_permissions_and_cleans_temporary_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index, original = make_fixture(root, BUILDER.read_text(encoding="utf-8"))
            index.chmod(0o640)
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "build.py")],
                capture_output=True, text=True, timeout=15,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            rebuilt = index.read_text(encoding="utf-8")
            self.assertNotEqual(rebuilt, original)
            self.assertNotIn("window.fixture = false;", rebuilt)
            self.assertEqual(rebuilt.count("window.fixture = true;"), original.count("window.fixture = false;"))
            self.assertEqual(stat.S_IMODE(index.stat().st_mode), 0o640)
            self.assertEqual(list(root.glob(".promath-index-*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
