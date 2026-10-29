"""Static contract for strict decimal Ax=b RHS and synchronized standalone bundle."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
WORKFLOW=(ROOT/'.github/workflows/quality.yml').read_text(encoding='utf-8')

class MatrixRhsDecimalTests(unittest.TestCase):
    def test_rhs_checks_syntax_before_conversion(self):
        start=SOURCE.index('const rhs=b.map(')
        end=SOURCE.index('const rows=A.map(',start)
        rhs=SOURCE[start:end]
        self.assertIn("typeof entry==='string'",rhs)
        self.assertIn("entry.trim()",rhs)
        self.assertIn('Right-hand side b must use decimal or scientific notation.',rhs)
        self.assertLess(rhs.index("typeof entry==='string'"),rhs.index('Number(entry)'))
        self.assertIn('Number.isFinite(value)',rhs)
        self.assertIn('MAX_ENTRY',rhs)

    def test_bundle_parity_and_browser_gate(self):
        start=HTML.index('/* ProMathStudio small-matrix calculator:')
        end=HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SOURCE+'\n')
        self.assertIn('python tests/smoke_matrix_rhs_decimal.py',WORKFLOW)

if __name__=='__main__':
    unittest.main()
