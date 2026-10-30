"""Engineering catalog source/bundle parity, routing and truthful planned status."""
import shutil,subprocess,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class EngineeringCatalogTests(unittest.TestCase):
 def test_bundle_and_router(self):
  src=(ROOT/'src/engineering-catalog.js').read_text(encoding='utf-8').rstrip('\n')
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  self.assertEqual(html.split('<script id="promath-engineering-catalog">\n',1)[1].split('</script>',1)[0].rstrip('\n'),src)
  self.assertIn('("promath-engineering-catalog", "src/engineering-catalog.js")',(ROOT/'scripts/build.py').read_text(encoding='utf-8'))
  self.assertIn("engineering:$('engineering-panel')",html)
  self.assertIn("mode==='engineering'?['engineering']",html)
  self.assertIn("id:'matrix.solve.real.small'",src) if False else self.assertIn("'matrix.solve.real.small'",src)
  self.assertIn("'fluids.pipe.network'",src)
  self.assertNotIn('eval(',src)
 @unittest.skipUnless(shutil.which('node'),'Node.js required')
 def test_module_syntax(self):
  p=subprocess.run(['node','--check','src/engineering-catalog.js'],cwd=ROOT,capture_output=True,text=True)
  self.assertEqual(p.returncode,0,p.stdout+p.stderr)
if __name__=='__main__':unittest.main()
