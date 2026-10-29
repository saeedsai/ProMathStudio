"""Graph Symbols expansion must only expose templates supported by numeric()."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class GraphPaletteExpansionTests(unittest.TestCase):
    def test_numeric_templates_are_enabled_and_equation_notation_stays_gated(self):
        palette = HTML[HTML.index("const graphNumericTemplates=new Set("):
                       HTML.index("function mathMatrix(")]
        for code in ("'root(3,x)'", "'frac(a,b)'", "'5!'"):
            self.assertIn(code, palette)
        self.assertIn("if(graphMode&&!graphPaletteSupported(code))", palette)
        self.assertIn("b.disabled=true", palette)
        self.assertIn("b.addEventListener('click',()=>insertText(code))", palette)
        # Do not allow all symbols through the gate or execute expressions.
        self.assertNotIn("graphPaletteSupported=code=>true", palette)
        self.assertNotIn("eval(", palette)
        self.assertNotIn("new Function(", palette)

    def test_templates_match_existing_numeric_grammar(self):
        numeric = HTML[HTML.index("function numeric(ast,"):HTML.index("window.MathStudio.customFunctions.evaluate=")]
        self.assertIn("case 'root':v=pow(a[1],div(C(1),a0))", numeric)
        self.assertIn("case 'frac':v=div(a0,a[1])", numeric)
        self.assertIn("case 'postfix':if(ast.op==='!')v=factorial(go(ast.value))", numeric)

    def test_browser_regression_is_mandatory(self):
        self.assertIn("python tests/smoke_graph_palette_expansion.py", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
