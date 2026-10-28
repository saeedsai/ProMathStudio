"""Regression coverage for the shared symbol palette workspace routing."""
import unittest
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")

class SharedSymbolWorkspaceTests(unittest.TestCase):
    def test_palette_visible_across_math_workspaces(self):
        for workspace in ("editor","calculator","solver","graph"):
            self.assertIn("body.ws-"+workspace+" #quick-symbols",HTML)
    def test_workspace_classes_follow_central_navigation(self):
        self.assertIn("for(const workspace of ['editor','calculator','solver','graph','data'])",HTML)
        self.assertIn("document.body.classList.toggle('ws-'+workspace,mode===workspace)",HTML)
        self.assertIn("setAttribute('aria-expanded',String(next))",HTML)
        self.assertIn("if(wasOpen){e.preventDefault();$('quick-symbols').focus();}",HTML)

    def test_graph_insertion_routes_to_graph_editor(self):
        self.assertIn("activeWorkspace==='graph'",HTML)
        self.assertIn("document.getElementById('graph-input'):input",HTML)
        self.assertIn("target.setRangeText(text,start,end,'end')",HTML)
        self.assertIn("target.dispatchEvent(new Event('input',{bubbles:true}))",HTML)
    def test_solver_retains_working_equation_insertion(self):
        self.assertIn("const target=calculatorMode?document.getElementById('calc-input')",HTML)
        self.assertIn("graphMode?document.getElementById('graph-input'):input",HTML)

if __name__=="__main__":
    unittest.main()
