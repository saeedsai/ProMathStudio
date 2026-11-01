"""Scalar root local secant diagnostics remain heuristic, with offline bundle parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarRootConditioningTests(unittest.TestCase):
    def test_local_slope_diagnostics_are_explicitly_non_certifying(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("const localSlopeMagnitudes=roots.map(x=>", source)
        self.assertIn("const minLocalSlope=availableSlopes.length?Math.min(...availableSlopes):null;", source)
        self.assertIn("localSlopeMagnitudes:[],minLocalSlope:null", source)
        self.assertIn("not a certified root-position error bound", source)
        self.assertIn("Minimum local secant slope magnitude (heuristic):", source)
        self.assertIn('id="num-output" role="status" aria-live="polite"', source)


if __name__ == "__main__":
    unittest.main()
