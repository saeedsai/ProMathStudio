"""Structural guards for graph palette insertion routing and draft isolation."""
import unittest
from pathlib import Path

HTML = (Path(__file__).resolve().parents[1] / 'index.html').read_text(encoding='utf-8')


class GraphSymbolCaretTests(unittest.TestCase):
    def test_one_palette_insertion_path(self):
        self.assertIn("b.addEventListener('click',()=>insertText(code))", HTML)
        self.assertNotIn("input.setRangeText(code,start,end,'end')", HTML)
        self.assertIn("target.setRangeText(text,start,end,'end')", HTML)

    def test_graph_templates_select_placeholder(self):
        self.assertIn("const graphPlaceholder=graphMode&&/^[A-Za-z_][A-Za-z0-9_]*\\([xy]\\)$/.test(text)?text.length-2:undefined;", HTML)
        self.assertIn("const focusOffset=Number.isFinite(caret)?caret:graphPlaceholder;", HTML)
        self.assertIn("target.setSelectionRange(position,position+(Number.isFinite(focusOffset)?1:0));", HTML)

    def test_graph_drafts_do_not_refresh_equation(self):
        self.assertIn("if(!calculatorMode&&!graphMode)refresh();", HTML)
        self.assertIn("graphDrafts[graphMode]=$('graph-input').value", HTML)
        self.assertIn("target.dispatchEvent(new Event('input',{bubbles:true}));target.focus();", HTML)


if __name__ == '__main__':
    unittest.main()
