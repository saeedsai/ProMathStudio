"""Complex graph feature regression: UI and numerical mapping."""
from pathlib import Path
import re
import unittest

HTML=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")

class ComplexGraphTest(unittest.TestCase):
    def test_controls_and_canvas(self):
        for value in ('id="complex-graph-workbench"','id="complex-canvas"','id="complex-real"',
                      'id="complex-imag"','id="complex-view"','id="complex-function"',
                      'id="complex-plot"','id="complex-status"','id="promath-complex-graph"'):
            with self.subTest(value=value): self.assertIn(value,HTML)
    def test_bounded_and_safe_numeric_operations(self):
        code=HTML.split('<script id="promath-complex-graph">',1)[1].split('</script>',1)[0]
        for fragment in ("kind==='square'","kind==='inverse'","kind==='exp'",
                         'Number.isFinite','Math.hypot','Math.exp','addEventListener'):
            with self.subTest(fragment=fragment): self.assertIn(fragment,code)
        self.assertNotIn('eval(',code)
        self.assertNotIn('new Function(',code)
    def test_responsive_and_separate_from_real_graph(self):
        self.assertIn('id="graph-input"',HTML)
        self.assertIn('data-graph-mode="2d"',HTML)
        self.assertIn('data-graph-mode="3d"',HTML)
        style=HTML.split('<style id="complex-graph-style">',1)[1].split('</style>',1)[0]
        self.assertIn('@media(max-width:760px)',style)
    def test_3d_surface_uses_modulus(self):
        code=HTML.split('<script id="promath-complex-graph">',1)[1].split('</script>',1)[0]
        self.assertIn('Math.hypot(...v)',code)
        self.assertIn('Math.min(8,',code)
        self.assertIn('get(\'complex-plot\').addEventListener',code)

if __name__=="__main__": unittest.main()
