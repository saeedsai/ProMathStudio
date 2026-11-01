"""Scalar root candidates require finite residuals after normalization."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarResidualTests(unittest.TestCase):
    def test_root_residual_contract_and_offline_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Math.abs(fr)<=tolerance", source)
        self.assertIn("Math.abs(f(x))<=tolerance", source)
        self.assertIn(".filter(x=>Number.isFinite(f(x))&&Math.abs(f(x))<=tolerance)", source)
        self.assertIn("const maxResidual=residuals.length?Math.max(...residuals):null;", source)
        self.assertIn("Maximum absolute residual:", source)
        self.assertNotIn("Math.abs(x)<1e-10?0:normalizeRoot(x,tolerance)", source)


if __name__ == "__main__":
    unittest.main()
