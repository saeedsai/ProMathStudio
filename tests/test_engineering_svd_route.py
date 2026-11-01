"""Canonical Engineering SVD route reuses the existing real-matrix solver."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringSvdRouteTests(unittest.TestCase):
    def test_unique_route_and_offline_parity(self):
        source = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertEqual(source.count("['matrix.svd.real.small'"), 1)
        self.assertIn("'calculator','matrix','mat-svd']", source)
        self.assertIn("including rank-deficient inputs", source)
        self.assertIn("if(t.route.focusId)", source)
        self.assertNotIn("function svd2x3(", source)
        self.assertNotIn("function svd3x3(", source)
        matrix = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        self.assertIn("['mat-svd','svd']", matrix)
        self.assertIn("function svd2x3(A)", matrix)
        self.assertIn("function svd3x3(A)", matrix)
        self.assertIn("Relative reconstruction residual:", matrix)


if __name__ == "__main__":
    unittest.main()
