"""Numerical Methods touch target CSS and standalone bundle parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class NumericalA11yTests(unittest.TestCase):
    def test_controls_and_live_status(self):
        source = (ROOT / "src/numerical-data.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-numerical-data">\n'
        self.assertIn(marker, html)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("#numerical-panel input,#numerical-panel select,#numerical-panel button{min-height:40px;box-sizing:border-box}", source)
        self.assertIn('<pre id="num-output" role="status" aria-live="polite">', source)
        self.assertIn("node.classList.add('error')", source)


if __name__ == "__main__":
    unittest.main()
