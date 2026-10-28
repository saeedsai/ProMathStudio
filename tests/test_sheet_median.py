"""Structural regression for the spreadsheet MEDIAN function and standalone parity."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / 'src/data-tables.js').read_text(encoding='utf-8')
HTML = (ROOT / 'index.html').read_text(encoding='utf-8')
WORKFLOW = (ROOT / '.github/workflows/quality.yml').read_text(encoding='utf-8')

class MedianFormulaTests(unittest.TestCase):
    def test_standalone_parity(self):
        self.assertIn(SOURCE, HTML)
    def test_library_and_aggregate_dispatch(self):
        self.assertIn("sample:'=MEDIAN(A1:A5)'", SOURCE)
        self.assertIn("(SUM|AVERAGE|AVG|MIN|MAX|COUNT|MEDIAN)", SOURCE)
        self.assertIn("if(upper==='MEDIAN')", SOURCE)
        self.assertIn("if(!nums.length)throw Error('#NUM!')", SOURCE)
    def test_invalid_reference_bounds_and_blank_handling(self):
        self.assertIn("r0<0||r1<0||r0>=MAX_ROWS||r1>=MAX_ROWS", SOURCE)
        self.assertIn("c0<0||c1<0||c0>=MAX_COLUMNS||c1>=MAX_COLUMNS", SOURCE)
        self.assertIn("String(v).trim()!==''", SOURCE)
    def test_browser_regression_is_mandatory(self):
        self.assertIn('python tests/smoke_sheet_median.py', WORKFLOW)

if __name__ == '__main__':
    unittest.main()
