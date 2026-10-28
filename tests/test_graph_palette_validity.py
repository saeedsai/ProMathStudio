"""Static graph palette gating and mandatory browser coverage."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class GraphPaletteValidityTests(unittest.TestCase):
    def test_graph_numeric_whitelist_and_equation_fallback(self):
        start = HTML.index("const graphNumericTemplates=new Set(")
        end = HTML.index("function mathMatrix(", start)
        section = HTML[start:end]
        for template in ("'pi'", "'sin(x)'", "'cos(x)'", "'sqrt(x)'", "'x^2'"):
            self.assertIn(template, section)
        self.assertIn("const graphMode=['graph','graph2d','graph3d']", section)
        self.assertIn("if(graphMode&&!graphPaletteSupported(code))", section)
        self.assertIn("b.disabled=true", section)
        self.assertIn("search.addEventListener('focus',draw)", section)
        self.assertIn("b.addEventListener('click',()=>insertText(code))", section)
        self.assertNotIn("eval(", section)
        self.assertNotIn("new Function(", section)

    def test_context_hint_and_mandatory_browser(self):
        self.assertIn('id="palette-graph-hint"', HTML)
        self.assertIn("python tests/smoke_graph_palette_validity.py", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
