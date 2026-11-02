"""Bisection must not equate x-width with the absolute function-residual tolerance."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ScalarBracketPrecisionTests(unittest.TestCase):
    def test_residual_first_bracket_and_offline_parity(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("if(Math.abs(fm)<=tolerance){a=b=mid;break;}", source)
        self.assertIn("if(mid===a||mid===b)break;", source)
        self.assertNotIn("b-a<tolerance", source)
        self.assertIn("Math.abs(fr)<=tolerance", source)
        self.assertIn(".filter(x=>Number.isFinite(f(x))&&Math.abs(f(x))<=tolerance)", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_scalar_root_bracket_precision.py", workflow)


if __name__ == "__main__":
    unittest.main()
