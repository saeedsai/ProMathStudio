"""Real-domain scalar root secant fallbacks and offline parity."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class OneSidedRootTests(unittest.TestCase):
    def test_one_sided_metadata_and_standalone_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(source, html.split('<script id="promath-numerical-data">\n',1)[1].split("</script>",1)[0].rstrip("\n"))
        for value in ("const localSlopeMethods=[];", "method='forward'", "method='backward'", "method='unavailable'", "localSlopeMagnitudes:[],localSlopeMethods:[],minLocalSlope:null", "One-sided local slope estimates:", "not proof of differentiability"):
            self.assertIn(value, source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_one_sided_slopes.py", workflow)
if __name__ == "__main__":
    unittest.main()
