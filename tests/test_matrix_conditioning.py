"""Matrix pseudoinverse QR conditioning and standalone parity."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')
class MatrixConditioning(unittest.TestCase):
    def test_qr_rank_and_diagnostics(self):
        body=SRC[SRC.index('function pseudoinverse3x2(A){'):SRC.index('function pseudoinverse2x3(A){')]
        for part in ('first=norms[0]>=norms[1]?0:1','const correction=','const r11=Math.hypot(...u1)',
                     'const sMin=det/sMax','sMin>cutoff?2:1','matrix[first]=','matrix[second]=',
                     'rank===2?sMax/sMin:null','numerically unstable'):
            self.assertIn(part,body)
        self.assertNotIn('eval(',body)
        self.assertIn('Condition number: ',SRC)
    def test_bundle_parity(self):
        start=HTML.index('/* ProMathStudio small-matrix calculator:')
        end=HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SRC+'\n')
if __name__=='__main__':
    unittest.main()
