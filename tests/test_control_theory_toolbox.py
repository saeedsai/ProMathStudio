"""Regression checks for the control theory toolbox."""
from pathlib import Path
import unittest
HTML=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
class ControlToolboxRegression(unittest.TestCase):
 def test_controls_and_analysis_modes(self):
  for item in ('id="control-theory-toolbox"','id="ct-num"','id="ct-den"','id="ct-gain"','id="ct-mode"','id="ct-run"','id="ct-canvas"','id="ct-output"'):
   with self.subTest(item=item):self.assertIn(item,HTML)
  for mode in ('bode','nyquist','root','routh','feedback'):self.assertIn('value="'+mode+'"',HTML)
 def test_analysis_guards(self):
  js=HTML.split('<script id="promath-control-theory">',1)[1].split('</script>',1)[0]
  for token in ('function routh(','function roots(','function response(','Number.isFinite','Math.log10','evalPoly','addEventListener'):self.assertIn(token,js)
  self.assertNotIn('eval(',js)
 def test_existing_graph_preserved(self):
  self.assertIn('id="graph-input"',HTML)
  self.assertIn('id="complex-graph-workbench"',HTML)
  self.assertIn('data-graph-mode="3d"',HTML)
 def test_mobile_layout(self):
  css=HTML.split('<style id="control-theory-style">',1)[1].split('</style>',1)[0]
  self.assertIn('@media(max-width:760px)',css)
  self.assertIn('@media(max-width:420px)',css)
if __name__=='__main__':unittest.main()
