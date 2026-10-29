"""Structural guard for 2x2 pseudoinverse conditioning and bundle parity."""
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
SRC = (ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML = (ROOT/'index.html').read_text(encoding='utf-8')
class Matrix2x2ConditionTests(unittest.TestCase):
    def test_condition_uses_svd_rank_and_keeps_moore_penrose_checks(self):
        body = SRC.split('function pseudoinverse2x2(A){', 1)[1].split('function pseudoinverse3x2(A){', 1)[0]
        for token in ('const {U,S,V,rank,conditionNumber}=svd2x2(A);',
                      'conditionNumber:rank===2?conditionNumber:null',
                      'singularValues:S.slice()', '1e-12*S[0]', 'tripleA',
                      'triplePlus', 'symmetryResidual'):
            self.assertIn(token, body)
        self.assertNotIn('eval(', body)
    def test_standalone_module_parity(self):
        marker = '<script id="promath-matrix-tools">\n'
        self.assertEqual(HTML.split(marker,1)[1].split('</script>',1)[0], SRC+'\n')
if __name__ == '__main__':
    unittest.main()
