"""2×3 pseudoinverse duality, dispatcher, UI, and standalone parity guards."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML = (ROOT/'index.html').read_text(encoding='utf-8')

class WidePseudoinverseStructure(unittest.TestCase):
    def test_transpose_duality_and_dispatch(self):
        body = SRC[SRC.index('function pseudoinverse2x3(A){'):SRC.index('function pseudoinverse(A){')]
        for fragment in ("A.length!==2||A[0].length!==3",
                         "pseudoinverse3x2(tall)",
                         "result.matrix[0].map",
                         "return {...result,matrix}"):
            self.assertIn(fragment,body)
        self.assertNotIn('eval(',body)
        self.assertIn('return pseudoinverse2x3(A)',SRC)
        self.assertIn('pseudoinverse3x2,pseudoinverse2x3,pseudoinverse3x3,pseudoinverse',SRC)
        self.assertIn('Pseudoinverse (2×2 / 3×2 / 2×3 / 3×3 A)',SRC)

    def test_standalone_module_parity(self):
        start = HTML.index('/* ProMathStudio small-matrix calculator:')
        end = HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SRC+'\n')

if __name__ == '__main__':
    unittest.main()
