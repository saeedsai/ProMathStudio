"""Regression for scalar spreadsheet references outside the supported grid."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SMOKE = (ROOT / "tests/smoke_sheet_references.py").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class SpreadsheetReferenceBoundsTests(unittest.TestCase):
    def test_scalar_parser_rejects_coordinates_outside_the_workbook_grid(self):
        self.assertIn("const row=Number(m[4])-1,column=colIndex(m[2]);", SOURCE)
        self.assertIn(
            "if(row<0||row>=MAX_ROWS||column<0||column>=MAX_COLUMNS)throw Error('#REF!');",
            SOURCE,
        )
        for formula in ("=A0", "=A6001", "=AG1", "=AF6000", "=SUM(AG1:AG1)", "=SUM(AF6000:AF6000)"):
            self.assertIn(formula, SMOKE)
        self.assertIn("python tests/smoke_sheet_references.py", WORKFLOW)

    def test_structural_edits_do_not_revive_out_of_grid_references(self):
        self.assertIn("const isSupportedReference=ref=>", SOURCE)
        self.assertIn("if(!isSupportedReference(left)||!isSupportedReference(right))return match;", SOURCE)
        self.assertIn("if(!isSupportedReference(colAnchor+letters+rowAnchor+digits))return match;", SOURCE)
        smoke = (ROOT / "tests/smoke_sheet_range_delete.py").read_text(encoding="utf-8")
        for formula in ("=Data!A6001", "=SUM(Data!A6001:A6001)", "=Data!AG1", "=SUM(Data!AG1:AG1)"):
            self.assertIn(formula, smoke)
        self.assertIn("python tests/smoke_sheet_range_delete.py", WORKFLOW)

    def test_row_insert_materializes_values_before_rewriting_references(self):
        preflight = SOURCE.index("const insertedRow=axis==='row'&&delta>0")
        rewrite = SOURCE.index("shiftReferences(t,axis,index,delta);", preflight)
        self.assertLess(preflight, rewrite)
        self.assertIn("Array.isArray(values)", SOURCE)
        smoke = (ROOT / "tests/smoke_sheet_range_delete.py").read_text(encoding="utf-8")
        self.assertIn("conversion failed", smoke)
        self.assertIn("JSON.stringify(MathStudio.dataTables.exportState())", smoke)
        self.assertIn("python tests/smoke_sheet_range_delete.py", WORKFLOW)

    def test_standalone_bundle_matches_the_modular_source(self):
        start = HTML.index("/* ProMathStudio Data Tables workspace.")
        end = HTML.index("</script>", start)
        self.assertEqual(HTML[start:end], SOURCE)


if __name__ == "__main__":
    unittest.main()
