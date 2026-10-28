"""Structural regression for bounded custom-function spreadsheet composition."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class CustomSpreadsheetCompositionTests(unittest.TestCase):
    def test_innermost_custom_and_aggregate_share_bounded_loop(self):
        start = SOURCE.index("const customPattern=")
        end = SOURCE.index("// Limited token grammar", start)
        code = SOURCE[start:end]
        self.assertIn("customFunctions?.find(name)", code)
        self.assertIn("customFunctions.evaluate(name,values)", code)
        self.assertIn("aggregatePattern.test(expr)", code)
        self.assertIn("if(!changed)break", code)
        self.assertIn("if(++compositionPasses>40)throw Error('#LIMIT')", code)
        self.assertIn("args.length!==fn.params.length", code)
        self.assertNotIn("eval(", code)
        self.assertNotIn("new Function(", code)

    def test_standalone_source_parity(self):
        start = HTML.index("/* ProMathStudio Data Tables workspace.")
        end = HTML.index("</script>", start)
        self.assertEqual(HTML[start:end], SOURCE)

    def test_browser_regression_is_mandatory(self):
        self.assertIn("python tests/smoke_sheet_custom_composition.py", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
