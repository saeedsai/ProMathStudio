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

    def test_concurrent_index_edit_is_not_overwritten(self):
        source = BUILDER.read_text(encoding="utf-8")
        guard = 'with index.open("r", encoding="utf-8", newline="") as current_file:'
        self.assertEqual(source.count(guard), 1)
        # Simulate another editor saving after module assembly but before replace.
        instrumented = source.replace(
            guard,
            'index.write_text("newer external edit\\n", encoding="utf-8")\\n            ' + guard,
            1,
        ).replace('\\n            with index.open', '\n            with index.open')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index, _ = make_fixture(root, instrumented)
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "build.py")],
                capture_output=True, text=True, timeout=15,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("changed during rebuild", result.stderr)
            self.assertEqual(index.read_text(encoding="utf-8"), "newer external edit\\n".replace("\\n", "\n"))
            self.assertEqual(list(root.glob(".promath-index-*.tmp")), [])

    def test_concurrent_module_edit_does_not_publish_stale_bundle(self):
        source = BUILDER.read_text(encoding="utf-8")
        guard = "for source, snapshot in source_snapshots.items():"
        self.assertEqual(source.count(guard), 1)
        # Inject a module save after assembly, immediately before verification.
        instrumented = source.replace(
            guard,
            '(root / "src/data-tables.js").write_text('
            '"window.newer = true;\\\\n", encoding="utf-8")\\n    ' + guard,
            1,
        ).replace('\\n    for source, snapshot', '\n    for source, snapshot')
        # Fail at the fixture's syntax, not an incidental IndentationError.
        compile(instrumented, "<instrumented standalone builder>", "exec")
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index, original = make_fixture(root, instrumented)
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "build.py")],
                capture_output=True, text=True, timeout=15,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Standalone module changed during rebuild: src/data-tables.js", result.stderr)
            self.assertEqual(index.read_text(encoding="utf-8"), original)
            self.assertIn("window.newer = true;", (root / "src/data-tables.js").read_text(encoding="utf-8"))
            self.assertEqual(list(root.glob(".promath-index-*.tmp")), [])

    def test_check_rejects_module_changed_after_assembly_without_writing(self):
        source = BUILDER.read_text(encoding="utf-8")
        guard = 'if "--check" in sys.argv[1:]:'
        self.assertEqual(source.count(guard), 1)
        # Simulate an external save after module assembly and before check mode.
        instrumented = source.replace(
            guard,
            '(root / "src/data-tables.js").write_text("window.newer = true;\\n", encoding="utf-8")\n'
            + guard,
            1,
        )
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            index, original = make_fixture(root, instrumented)
            # Make the standalone fixture initially match the source modules.
            index.write_text(original.replace("window.fixture = false;", "window.fixture = true;"), encoding="utf-8")
            expected = index.read_bytes()
            result = subprocess.run(
                [sys.executable, str(root / "scripts" / "build.py"), "--check"],
                capture_output=True, text=True, timeout=15,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Standalone module changed during rebuild: src/data-tables.js", result.stderr)
            self.assertEqual(index.read_bytes(), expected)
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
