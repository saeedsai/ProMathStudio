"""Standalone builder must fail safely on ambiguous module markers."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class BuildMarkerValidationTests(unittest.TestCase):
    def test_symlinked_index_rejected_without_touching_target(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            target = root / "external.html"
            original = b"<html>external data must remain unchanged</html>"
            target.write_bytes(original)
            (root / "index.html").symlink_to(target)
            result = subprocess.run(["python3", str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Refusing to rewrite symlinked standalone index.html", result.stderr)
            self.assertTrue((root / "index.html").is_symlink())
            self.assertEqual(target.read_bytes(), original)

    def test_index_ascii_controls_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        for control in (b"\x01", b"\x08", b"\x0c", b"\x1f"):
            with self.subTest(control=control), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                original = b'<script id="mathstudio-data-tables">\n' + control + b'\n</script>\n'
                (root / "index.html").write_bytes(original)
                result = subprocess.run(["python3", str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unexpected ASCII control character in standalone index.html", result.stderr)
                self.assertEqual((root / "index.html").read_bytes(), original)

    def test_module_ascii_controls_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        original = b'<script id="mathstudio-data-tables">\n/* original */\n</script>\n'
        for control in (b"\x01", b"\x08", b"\x0c", b"\x1f"):
            with self.subTest(control=control), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "src").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "src/data-tables.js").write_bytes(b"const safe = 1;" + control + b"\n")
                (root / "index.html").write_bytes(original)
                result = subprocess.run(["python3", str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unexpected ASCII control character in standalone module source: src/data-tables.js", result.stderr)
                self.assertEqual((root / "index.html").read_bytes(), original)

    def test_module_carriage_returns_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        original = b'<script id="mathstudio-data-tables">\n/* original */\n</script>\n'
        for source in (b"const a=1;\r\n", b"const a=1;\rconst b=2;\n"):
            with self.subTest(source=source), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "src").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "src/data-tables.js").write_bytes(source)
                (root / "index.html").write_bytes(original)
                result = subprocess.run(["python3", str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unexpected carriage return in standalone module source: src/data-tables.js", result.stderr)
                self.assertEqual((root / "index.html").read_bytes(), original)

    def test_mixed_line_endings_rejected_before_module_access(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        for original in (b"<html>line\rline</html>", b"<html>line\nnext\r\n</html>"):
            with self.subTest(original=original), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "index.html").write_bytes(original)
                result = subprocess.run(["python3", str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unexpected carriage return in standalone index.html", result.stderr)
                self.assertEqual((root / "index.html").read_bytes(), original)

    def test_crlf_index_rejected_without_overwrite(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        original = b'<script id="mathstudio-data-tables">\r\n/* original */\r\n</script>\r\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "index.html").write_bytes(original)
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected carriage return in standalone index.html", result.stderr)
            self.assertEqual((root / "index.html").read_bytes(), original)

    def test_index_utf8_bom_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        html = '\ufeff<script id="mathstudio-data-tables">\n/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected UTF-8 BOM in standalone index.html", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

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

    def test_empty_module_source_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* existing module */\n</script>\n'
        for source in ('', '  \n\t  '):
            with self.subTest(source=repr(source)), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "src").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "src/data-tables.js").write_text(source, encoding="utf-8")
                (root / "index.html").write_text(html, encoding="utf-8")
                result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Empty standalone module source: src/data-tables.js", result.stderr)
                self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_nul_module_source_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text("const a = 1;\x00const b = 2;\n", encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected NUL byte in standalone module source", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_utf8_bom_module_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text("\ufeffconst safe = 1;\n", encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected UTF-8 BOM in standalone module source", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_missing_module_source_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* existing module */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing standalone module source: src/data-tables.js", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_missing_closing_script_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* truncated module */\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text("const safe = 1;\\n", encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing standalone script closing tag", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_embedded_script_opener_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        for opener in ('<SCRIPT id="unexpected">', '<script\tid="unexpected">', '<ScRiPt>'):
            with self.subTest(opener=opener), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "scripts").mkdir()
                (root / "src").mkdir()
                (root / "scripts/build.py").write_text(builder, encoding="utf-8")
                (root / "src/data-tables.js").write_text(
                    'const unsafe = "' + opener + '";\n', encoding="utf-8")
                (root / "index.html").write_text(html, encoding="utf-8")
                result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                        capture_output=True, text=True, timeout=10)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Unsafe script opening sequence", result.stderr)
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

    def test_html_comment_opener_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text('const unsafe = "<!--";\n', encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsafe HTML comment delimiter in module", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_invalid_utf8_module_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_bytes(b"const valid = 1;\n\xff")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid UTF-8 in standalone module source: src/data-tables.js", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_html_comment_closer_rejected_without_overwriting_index(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        marker = '<script id="mathstudio-data-tables">\n'
        html = marker + '/* original */\n</script>\n'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "src").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "src/data-tables.js").write_text('const unsafe = "-->";\n', encoding="utf-8")
            (root / "index.html").write_text(html, encoding="utf-8")
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unsafe HTML comment delimiter in module", result.stderr)
            self.assertEqual((root / "index.html").read_text(encoding="utf-8"), html)

    def test_nul_index_rejected_without_overwrite(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        original = b'<html>before\\x00after</html>'.replace(b'\\x00', bytes([0]))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            (root / "index.html").write_bytes(original)
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unexpected NUL character in standalone index.html", result.stderr)
            self.assertEqual((root / "index.html").read_bytes(), original)

    def test_invalid_utf8_index_rejected_without_overwrite(self):
        builder = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "scripts").mkdir()
            (root / "scripts/build.py").write_text(builder, encoding="utf-8")
            original = b'<html>\xff</html>'
            (root / "index.html").write_bytes(original)
            result = subprocess.run(['python3', str(root / "scripts/build.py")],
                                    capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid UTF-8 in standalone index.html", result.stderr)
            self.assertEqual((root / "index.html").read_bytes(), original)

if __name__ == '__main__':
    unittest.main()
