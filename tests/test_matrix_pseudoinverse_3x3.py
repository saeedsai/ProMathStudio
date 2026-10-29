"""Bounded 3x3 one-sided Jacobi pseudoinverse and standalone parity contract."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')

class Matrix3x3Pseudoinverse(unittest.TestCase):
    def test_algorithm_and_ui_contract(self):
        body=SRC.split('function pseudoinverse3x3(A){',1)[1].split('function pseudoinverse(A){',1)[0]
        # The pseudoinverse now shares the residual-checked Jacobi SVD, rather
        # than carrying a duplicate rotation loop. Verify both layers.
        svd=SRC.split('function svd3x3(A){',1)[1].split('function pseudoinverse2x2(A){',1)[0]
        for token in ('sweep<64','Math.hypot(1,tau)','1e-12*values[order[0]]',
                      'orthogonalityU','orthogonalityV','reconstructed-A[i][j]'):
            self.assertIn(token,svd)
        for token in ('svd3x3(A)','1e-12*S[0]','if(S[k]>cutoff)',
                      'tripleA','triplePlus','symmetryResidual','Number.isFinite',
                      'numerically unstable','rank===3?'):
            self.assertIn(token,body)
        self.assertNotIn('eval(',body)
        self.assertIn('return pseudoinverse3x3(A)',SRC)
        self.assertIn('pseudoinverse3x3,pseudoinverse,notation',SRC)
        self.assertIn('Pseudoinverse (2×2 / 3×2 / 2×3 / 3×3 A)',SRC)
    def test_bundle_parity(self):
        marker='<script id="promath-matrix-tools">\n'
        self.assertEqual(HTML.split(marker,1)[1].split('</script>',1)[0],SRC+'\n')
if __name__=='__main__':
    unittest.main()
