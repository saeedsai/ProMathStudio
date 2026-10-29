"""3x3 SVD scale-safe conditioning and bundled-source invariants."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8')
HTML=(ROOT/'index.html').read_text(encoding='utf-8')

class MatrixSVD3x3ConditionTests(unittest.TestCase):
    def test_scaled_condition_estimate_and_advisory(self):
        start=SOURCE.index('function svd3x3(A){')
        end=SOURCE.index('function svd3x2(A){',start)
        section=SOURCE[start:end]
        self.assertIn('values[order[0]]/values[order[2]]',section)
        self.assertIn('cutoff:cutoff*scale',section)
        self.assertIn("conditionAssessment=rank<3?'rank deficient'",section)
        self.assertIn("conditionNumber>=1e8?'ill-conditioned'",section)
        self.assertIn("conditionNumber>=1e4?'moderately conditioned'",section)
        self.assertIn('residual>1e-8||orthogonalityU>1e-8||orthogonalityV>1e-8',section)
        self.assertIn("conditionAssessment:'rank deficient'",section)
    def test_ui_displays_rank_cutoff_and_condition_risk(self):
        self.assertIn("'\\nRank cutoff (absolute): '+value.cutoff.toExponential(3)",SOURCE)
        self.assertIn("'\\nCondition assessment: '+value.conditionAssessment",SOURCE)
    def test_standalone_parity(self):
        start=HTML.index('/* ProMathStudio small-matrix calculator:')
        end=HTML.index('</script>',start)
        self.assertEqual(HTML[start:end],SOURCE+'\n')

if __name__=='__main__': unittest.main()
