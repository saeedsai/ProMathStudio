"""Canonical Engineering symmetric-eigen route reuses the existing Jacobi solver."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringEigenRouteTests(unittest.TestCase):
    def test_unique_route_and_standalone_parity(self):
        source = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertEqual(source.count("['matrix.eigen.symmetric.small'"), 1)
        self.assertIn("'calculator','matrix','mat-eigen']", source)
        self.assertIn("not a general or complex eigensolver", source)
        self.assertIn("if(t.route.focusId)", source)
        self.assertNotIn("function eigenSymmetric(", source)
        matrix = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        self.assertIn("['mat-eigen','eigen']", matrix)
        self.assertIn("function eigenSymmetric(A)", matrix)
        self.assertIn("Eigenanalysis requires a real symmetric matrix.", matrix)
        self.assertIn("Reconstruction residual:", matrix)


if __name__ == "__main__":
    unittest.main()
