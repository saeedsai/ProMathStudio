"""Constant residual plateaus must not masquerade as isolated scalar roots."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarPlateauTests(unittest.TestCase):
    def test_offline_parity_and_plateau_contract(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("sampled.every(y=>Number.isFinite(y)&&y===sampled[0])", source)
        self.assertIn("[Math.SQRT1_2,Math.sqrt(3)/3].every", source)
        self.assertIn("sampled-zero-plateau", source)
        self.assertIn("sampled-nonzero-plateau", source)
        self.assertIn("non-isolated zeros possible", source)
        self.assertIn("A small residual alone does not certify a root.", source)


if __name__ == "__main__":
    unittest.main()
