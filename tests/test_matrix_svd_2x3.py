"""Structural contract for wide 2x3 SVD dispatch, factor export and bundle parity."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')

class WideSVDContract(unittest.TestCase):
    def test_transpose_factor_contract(self):
        self.assertIn('function svd2x3(A){',SOURCE)
        self.assertIn('const factors=svd3x2(tall);',SOURCE)
        self.assertIn('U:factors.V.map(row=>row.slice()),V:factors.U.map(row=>row.slice())',SOURCE)
        self.assertIn('orthogonalityU:factors.orthogonalityV,orthogonalityV:factors.orthogonalityU',SOURCE)
        self.assertIn('A.length===2&&A[0].length===3?svd2x3(A)',SOURCE)
        self.assertIn('svd2x2,svd3x2,svd2x3,svd3x3,',SOURCE)
    def test_ui_and_standalone_parity(self):
        self.assertIn('SVD supports real 2×2, 3×2, 2×3 and 3×3 A',SOURCE)
        start=HTML.index('/* ProMathStudio small-matrix calculator:')
        end=HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SOURCE+'\n')

if __name__=='__main__':
    unittest.main()
