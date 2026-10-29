"""Matrix input rejects JavaScript-only numeric prefixes and accepts scientific notation."""
import re
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/"src/matrix-tools.js").read_text(encoding="utf-8")
HTML=(ROOT/"index.html").read_text(encoding="utf-8")
class MatrixDecimalInputTests(unittest.TestCase):
    def test_reject_nondecimal_input(self):
        self.assertIn("Matrix entries must use decimal or scientific notation.",SOURCE)
        self.assertIn("typeof entry==='string'",SOURCE)
        self.assertIn("entry.trim()",SOURCE)
        self.assertIn("Number.isFinite(value)",SOURCE)
    def test_standalone_parity(self):
        start=HTML.index("/* ProMathStudio small-matrix calculator:")
        end=HTML.index("</script>",start)
        self.assertEqual(HTML[start:end],SOURCE+"\\n")
if __name__=="__main__": unittest.main()
