"""Standalone builder must fail safely on ambiguous module markers."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuildMarkerValidationTests(unittest.TestCase):
    def test_missing_and_duplicate_markers_do_not_overwrite_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        module = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        for html in ('<html></html>', marker + module + '</script>' + marker + module + '</script>'):
            with self.subTest(html_length=len(html)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "src").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "src/data-tables.js").write_text(module, encoding="utf-8")
                (root / "index.html").write_text(html, encoding="utf-8")
                result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Expected exactly one standalone script marker', result.stderr)
                self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_embedded_script_terminator_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text(
                'const unsafe = "</ScRiPt>";\n', encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsafe script closing sequence", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_case_insensitive_and_tabbed_nested_script_openers_are_rejected(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        for opener in ('<SCRIPT id="unexpected">', '<script\tid="unexpected">', '<ScRiPt>'):
            with self.subTest(opener=opener), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "src").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "src/data-tables.js").write_text("const safe = 1;\n", encoding="utf-8")
                html = marker + '/* original */\n' + opener + '\n</script>\n'
                (root / "index.html").write_text(html, encoding="utf-8")
                result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Nested script opening", result.stderr)
                self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_nested_script_opener_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n<script id="unexpected">\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text("const safe = 1;\n", encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Nested script opening", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

if __name__ == '__main__':
    unittest.main()
