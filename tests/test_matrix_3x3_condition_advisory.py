"""Structural and standalone parity contract for 3x3 condition-risk advisory."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')

class Matrix3x3ConditionAdvisory(unittest.TestCase):
    def test_risk_categories_and_existing_stability_gates(self):
        body=SRC.split('function pseudoinverse3x3(A){',1)[1].split('function pseudoinverse(A){',1)[0]
        for token in ("conditionAssessment:'rank deficient'", "rank<3?'rank deficient'",
                      "ratio>=1e8?'ill-conditioned'", "ratio>=1e4?'moderately conditioned'",
                      "numerically unstable", "tripleA", "triplePlus", "symmetryResidual"):
            self.assertIn(token,body)
        self.assertNotIn('eval(',body)
        self.assertIn("Singular values: ",SRC)
        self.assertIn("Relative rank cutoff: ",SRC)
        self.assertIn("Condition assessment: ",SRC)
        self.assertIn("value.cutoff.toExponential(3)",SRC)
    def test_self_contained_bundle_parity(self):
        marker='<script id="promath-matrix-tools">\n'
        self.assertEqual(HTML.split(marker,1)[1].split('</script>',1)[0],SRC+'\n')

if __name__=='__main__':
    unittest.main()
