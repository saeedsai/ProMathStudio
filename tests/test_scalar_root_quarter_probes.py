"""Quarter-grid probes: residual gate, source parity and mandatory browser coverage."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

class QuarterProbeTests(unittest.TestCase):
    def test_source_bundle_and_quality(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-numerical-data">\n',1)[1].split("</script>",1)[0].rstrip("\n")
        self.assertEqual(source,bundled)
        for token in ("quarterProbes=0,quarterSignReversals=0","quarterProbes+=2",
                      "refineBracket(points[i],points[i+1],values[i],values[i+1])",
                      "if(Number.isFinite(fr)&&Math.abs(fr)<=tolerance)",
                      ".filter(x=>Number.isFinite(f(x))&&Math.abs(f(x))<=tolerance)",
                      "Quarter-grid probes: "):
            self.assertIn(token,source)
        self.assertIn("not globally complete",source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_quarter_probes.py",workflow)

if __name__ == "__main__":
    unittest.main()
