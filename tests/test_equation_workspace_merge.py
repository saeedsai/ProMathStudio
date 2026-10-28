"""Regression guard: Equation combines editor and solver without losing controls."""
import unittest
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")

class EquationWorkspaceMergeTests(unittest.TestCase):
    def test_single_equation_tab_and_legacy_solver_route(self):
        self.assertIn('data-workspace="editor"><span class="ws-emoji">∑</span> Equation</button>',HTML)
        self.assertNotIn('data-workspace="solver"><span class="ws-emoji">ƒ</span>',HTML)
        self.assertIn("if(mode==='solver')mode='editor';",HTML)
    def test_editor_solver_and_notebook_visible_together(self):
        self.assertIn("['editor','preview','solver','python','notebook','notebookTitle','examples','tip']",HTML)
        for token in ('id="equation-input"','id="symbolic-panel"','id="cas-run"','id="cas-operation"','id="cas-engine"','id="latex-preview"','id="notebook"'):
            self.assertIn(token,HTML)
    def test_numerical_panel_and_legacy_routes(self):
        self.assertIn("mode!=='editor'",HTML)
        self.assertIn("solver:'Expand, factor, solve",HTML)
        self.assertIn("editor:'Equation',solver:'Equation'",HTML)

if __name__=="__main__":
    unittest.main()
