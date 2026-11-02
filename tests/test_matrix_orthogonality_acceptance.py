"""Regression for visible QR orthogonality acceptance and near-exact skip semantics."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class OrthogonalityAcceptanceRegression(unittest.TestCase):
    def test_offline_parity_and_registered_browser(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Orthogonality acceptance: ", source)
        smoke = (ROOT / "tests/smoke_matrix_weighted_spectral_condition.py").read_text(encoding="utf-8")
        self.assertIn('near_fit["orthogonalityTolerance"] > 1e-8', smoke)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_normal_relaxed_near_exact_and_invalid(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const api=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return {leastSquares,weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]];
const ordinary=api.weightedLeastSquares(A,[1,2,9],[1,1,.01]);
assert.strictEqual(ordinary.orthogonalityCheckSkipped,false);
assert.strictEqual(ordinary.orthogonalityTolerance,1e-8);
assert(ordinary.orthogonalityGuidance.includes('ordinary 1e-8'));
const exact=api.weightedLeastSquares(A,[1,2,3],[1,1,1]);
assert.strictEqual(exact.orthogonalityCheckSkipped,true);
assert(exact.orthogonalityGuidance.includes('not evaluated'));
const near=api.weightedLeastSquares([[1,1],[1,1.00000001],[1,1.00000002]],[1,.99999999,.999999982],[1,1,1]);
assert.strictEqual(near.orthogonalityCheckSkipped,false);
assert(near.orthogonalityTolerance>1e-8 && near.orthogonalityTolerance<1);
assert(near.normalResidual<=near.orthogonalityTolerance);
assert(near.orthogonalityGuidance.includes('relaxed'));
const plain=api.leastSquares(A,[1,2,9]);
assert.strictEqual(plain.orthogonalityTolerance,1e-8);
assert.throws(()=>api.weightedLeastSquares(A,[1,2,3],[1,0,1]),/Weights must be finite/);
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],[1,2,3],[1,1,1]),/Rank-deficient/);
console.log(JSON.stringify({normal:ordinary.orthogonalityTolerance,near:near.orthogonalityTolerance,skip:exact.orthogonalityCheckSkipped}));
"""
        run = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result["normal"], 1e-8)
        self.assertGreater(result["near"], 1e-8)
        self.assertTrue(result["skip"])


if __name__ == "__main__":
    unittest.main()
