"""Midpoint subgrid bracketing preserves source/bundle parity and CI coverage."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarRootMidpointTests(unittest.TestCase):
    def test_bounded_probes_residual_gate_and_offline_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-numerical-data">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("midpointProbes=0,midpointSignReversals=0", source)
        self.assertIn("refineBracket(a,mid,fa,fm);", source)
        self.assertIn("refineBracket(mid,b,fm,fb);", source)
        self.assertIn("if(Number.isFinite(fr)&&Math.abs(fr)<=tolerance)", source)
        self.assertIn(".filter(x=>Number.isFinite(f(x))&&Math.abs(f(x))<=tolerance)", source)
        self.assertIn("Midpoint probes: ${result.midpointProbes}", source)
        self.assertIn("not globally complete", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_midpoint.py", workflow)


if __name__ == "__main__":
    unittest.main()
