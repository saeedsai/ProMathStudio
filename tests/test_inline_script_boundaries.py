"""Guard against inserting new scripts inside the HTML-export string."""
from pathlib import Path
import re
import subprocess
import unittest

HTML=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")

class ScriptBoundaryRegression(unittest.TestCase):
 def test_export_html_literal_remains_closed(self):
  self.assertIn("+'</div></body></html>'",HTML)
  self.assertNotIn("+'</div>\n</body></html>'",HTML)
 def test_complex_control_scripts_are_top_level(self):
  self.assertEqual(HTML.count('<script id="promath-complex-graph">'),1)
  self.assertEqual(HTML.count('<script id="promath-control-theory">'),1)
  self.assertLess(HTML.index("+'</div></body></html>'"),HTML.index('<script id="promath-complex-graph">'))
  self.assertLess(HTML.index("+'</div></body></html>'"),HTML.index('<script id="promath-control-theory">'))
 def test_each_inline_script_parses_in_node(self):
  scripts=re.findall(r'<script([^>]*)>(.*?)</script>',HTML,re.S|re.I)
  for i,(attributes,code) in enumerate(scripts):
   if 'text/plain' in attributes:continue
   with self.subTest(index=i):
    proc=subprocess.run(['node','--check','-'],input=code,text=True,capture_output=True)
    self.assertEqual(proc.returncode,0,proc.stderr[:1000])
if __name__=='__main__':unittest.main()
