"""Guard XLSX ZIP local-header metadata validation and standalone parity."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/xlsx-import.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SMOKE = (ROOT / "tests/smoke_xlsx_import.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class XlsxImportIntegrityTests(unittest.TestCase):
    def test_local_header_crc_and_sizes_match_central_directory(self):
        self.assertIn(
            "const localCrc=u32(view,local+14),localCompressed=u32(view,local+18),localPlain=u32(view,local+22);",
            SOURCE,
        )
        self.assertIn(
            "if(!(flags&8)&&(localCrc!==crc||localCompressed!==compressed||localPlain!==plain))",
            SOURCE,
        )
        for mutation in (
            "local_crc[local + 14] ^= 1",
            "local_compressed_size[local + 18] ^= 1",
            "local_uncompressed_size[local + 22] ^= 1",
        ):
            self.assertIn(mutation, SMOKE)
        self.assertIn("python tests/smoke_xlsx_import.py", WORKFLOW)

    def test_standalone_import_module_matches_source(self):
        marker = '<script id="promath-xlsx-import">\n'
        start = HTML.index(marker) + len(marker)
        end = HTML.index("</script>", start)
        self.assertEqual(HTML[start:end].rstrip("\n"), SOURCE.rstrip("\n"))


if __name__ == "__main__":
    unittest.main()
