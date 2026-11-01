"""Matrix accessible control sizing and source/bundle identity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class MatrixTouchTargetsTests(unittest.TestCase):
    def test_css_and_standalone_parity(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn(".matrix-controls select,.matrix-actions button,.matrix-result-actions button{min-height:40px}", source)
        self.assertIn(".matrix-grid input{min-width:0;width:100%;min-height:40px;box-sizing:border-box;", source)

if __name__ == "__main__":
    unittest.main()
