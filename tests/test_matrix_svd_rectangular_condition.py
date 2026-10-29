"""Structural guard for rectangular SVD condition diagnostics and standalone parity."""
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML = (ROOT/'index.html').read_text(encoding='utf-8')

class RectangularSVDConditionTests(unittest.TestCase):
    def test_scale_safe_rank_cutoff_and_advisory(self):
        section = SOURCE.split('function svd3x2(A){',1)[1].split('function svd2x3(A){',1)[0]
        self.assertIn('cutoff=1e-12*factors.S[0]*scale',section)
        self.assertIn('factors.S[0]/factors.S[1]',section)
        self.assertIn("conditionAssessment=rank<2?'rank deficient'",section)
        self.assertIn('orthogonalityU>1e-8||orthogonalityV>1e-8',section)
        self.assertIn("const factors=svd3x2(tall)",SOURCE)
        self.assertIn('SVD (2×2 / 3×2 / 2×3 / 3×3 A)',SOURCE)

    def test_standalone_parity_and_syntax(self):
        start = HTML.index('/* ProMathStudio small-matrix calculator:')
        end = HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SOURCE+'\n')
        result = subprocess.run(['node','--check',str(ROOT/'src/matrix-tools.js')],
                                capture_output=True,text=True,check=False)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__ == '__main__':
    unittest.main()
