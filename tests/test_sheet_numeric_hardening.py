"""Guard spreadsheet numeric hardening and bundled/source parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class SpreadsheetNumericHardeningTests(unittest.TestCase):
    def test_reserved_names_cannot_shadow_builtin_aggregates(self):
        self.assertIn("SUM|AVERAGE|AVG|MIN|MAX|COUNT|MEDIAN", SOURCE)
        self.assertIn("test(name)?null:window.MathStudio.customFunctions?.find(name)", SOURCE)

    def test_overflow_is_an_error_and_average_is_scaled(self):
        self.assertIn("nums.reduce((a,b)=>a+b/nums.length,0)", SOURCE)
        self.assertIn("if(!Number.isFinite(x))throw Error('#NUM!')", SOURCE)
        self.assertNotIn("String(Number.isFinite(x)?x:0)", SOURCE)
        self.assertIn("catch(error){throw Error(error?.message?.startsWith('#')?error.message:'#VALUE');}", SOURCE)

    def test_standalone_parity_and_browser_gate(self):
        start = HTML.index("/* ProMathStudio Data Tables workspace.")
        end = HTML.index("</script>", start)
        self.assertEqual(HTML[start:end], SOURCE)
        self.assertIn("python tests/smoke_sheet_numeric_hardening.py", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
