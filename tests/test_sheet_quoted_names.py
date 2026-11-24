"""Structural regression for escaped-apostrophe spreadsheet sheet names."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class SpreadsheetQuotedSheetNameTests(unittest.TestCase):
    def test_escaped_apostrophes_are_supported_in_all_reference_paths(self):
        self.assertIn("const sheetNameFromQualifier=", SOURCE)
        self.assertIn("replace(/''/g", SOURCE)
        self.assertIn("replace(/[^a-zA-Z0-9_ ']/g,'_')", SOURCE)
        self.assertEqual(SOURCE.count(r"(?:'(?:[^']|'')+'|"), 5)
        self.assertIn("python tests/smoke_sheet_references.py", WORKFLOW)

    def test_standalone_bundle_matches_modular_source(self):
        start = HTML.index("/* ProMathStudio Data Tables workspace.")
        end = HTML.index("</script>", start)
        self.assertEqual(HTML[start:end], SOURCE)


if __name__ == "__main__":
    unittest.main()
