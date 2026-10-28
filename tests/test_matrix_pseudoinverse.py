"""Structural guard for 2x2 pseudoinverse wiring and standalone module parity."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML = (ROOT/'index.html').read_text(encoding='utf-8')

class PseudoinverseStructureTests(unittest.TestCase):
    def test_bounded_svd_and_moore_penrose_guard(self):
        start = SRC.index('function pseudoinverse2x2(A){')
        end = SRC.index('function format(x){', start)
        body = SRC[start:end]
        self.assertIn('svd2x2(A)', body)
        self.assertIn('1e-12*S[0]', body)
        self.assertIn('tripleA', body)
        self.assertIn('triplePlus', body)
        self.assertIn('symmetryResidual', body)
        self.assertNotIn('eval(', body)
    def test_ui_and_editor_transfer(self):
        self.assertIn('id="mat-pseudoinverse"', SRC)
        self.assertIn("['mat-pseudoinverse','pseudoinverse']", SRC)
        self.assertIn("last.operation==='pseudoinverse'?last.value.matrix", SRC)
    def test_standalone_parity(self):
        start = HTML.index('/* ProMathStudio small-matrix calculator:')
        end = HTML.index('</script>', start)
        self.assertEqual(HTML[start:end], SRC+'\n')

if __name__ == '__main__':
    unittest.main()
