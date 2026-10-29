"""Guard 3x2 pseudoinverse and standalone source parity."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')

class RectangularPseudoinverseStructure(unittest.TestCase):
    def test_numeric_guards_and_dispatch(self):
        body=SRC[SRC.index('function pseudoinverse3x2(A){'):SRC.index('function pseudoinverse(A){')]
        for token in ('1e-12*sMax','sMin>cutoff?2:1','tripleA','triplePlus','symmetryResidual','Number.isFinite','const correction='):
            self.assertIn(token,body)
        self.assertNotIn('eval(',body)
        self.assertIn("operation==='pseudoinverse'?pseudoinverse(A)",SRC)
        self.assertIn('pseudoinverse3x2,pseudoinverse2x3,pseudoinverse3x3,pseudoinverse,notation',SRC)
    def test_standalone_parity(self):
        start=HTML.index('/* ProMathStudio small-matrix calculator:')
        end=HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SRC+'\n')

if __name__=='__main__':
    unittest.main()
