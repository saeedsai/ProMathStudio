"""Canonical weighted least-squares Engineering route shares the QR solver."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EngineeringWeightedRouteTests(unittest.TestCase):
    def test_unique_focus_only_route_and_offline_bundle(self):
        source = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-engineering-catalog">\n'
        self.assertEqual(source, html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertEqual(source.count("['matrix.weighted-least-squares.real.3x2'"), 1)
        self.assertIn("'calculator','matrix','mat-weighted-least-squares']", source)
        self.assertIn("positive relative weights", source)
        self.assertIn("no uncertainty or statistical confidence intervals", source)
        self.assertIn("if(t.route.focusId)", source)
        self.assertNotIn("function weightedLeastSquares(", source)

    def test_existing_canonical_solver_and_mandatory_browser_gate(self):
        matrix = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        self.assertIn("function weightedLeastSquares(A,b,weights)", matrix)
        self.assertIn("['mat-weighted-least-squares','weightedLeastSquares']", matrix)
        self.assertIn("const result=leastSquares(transformed,transformedB)", matrix)
        self.assertIn("Weighted residual exceeded finite floating-point range.", matrix)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_engineering_weighted_route.py", workflow)


if __name__ == "__main__":
    unittest.main()
