"""Weighted 3x2 leave-one-out prediction residuals: QR leverage identity and safeguards."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedLeaveOneOutTests(unittest.TestCase):
    def test_source_bundle_and_required_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(source, html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertIn("looResiduals", source)
        self.assertIn("remaining<=1e-10", source)
        self.assertIn("Leave-one-out prediction residuals (rows 1–3)", source)
        self.assertIn("Weighted leave-one-out PRESS:", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_loo.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for QR numerical references")
    def test_direct_refit_references_weight_scaling_and_unavailable_cases(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const start=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=source.indexOf('const matrixRank=A=>rref(A).rank;');
assert(start>=0&&end>start);
const api=new Function(source.slice(start,end)+';return {weightedLeastSquares,solve};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,0.01];
const frozen=JSON.stringify([A,b,w]);
const fit=api.weightedLeastSquares(A,b,w);
const expected=[-6,3,-6];
fit.looResiduals.forEach((x,i)=>assert(Math.abs(x-expected[i])<1e-9));
assert(Math.abs(fit.looWeightedPress-45.36)<1e-9);
for(let i=0;i<3;i++){
 const keep=[0,1,2].filter(j=>j!==i);
 const coeff=api.solve(keep.map(j=>A[j]),keep.map(j=>b[j])).solution;
 const prediction=A[i].reduce((s,a,j)=>s+a*coeff[j],0)-b[i];
 assert(Math.abs(fit.looResiduals[i]-prediction)<1e-9,'direct leave-one-out refit '+i);
}
const scaled=api.weightedLeastSquares(A,b,[10,10,0.1]);
fit.looResiduals.forEach((x,i)=>assert(Math.abs(x-scaled.looResiduals[i])<1e-9));
assert(Math.abs(scaled.looWeightedPress/fit.looWeightedPress-10)<1e-9);
const singularRemoval=api.weightedLeastSquares([[1,0],[0,1],[0,1]],[2,3,4],[1,1,1]);
assert.strictEqual(singularRemoval.looResiduals[0],null);
assert.strictEqual(singularRemoval.looWeightedPress,null);
assert(singularRemoval.looResiduals.slice(1).every(Number.isFinite));
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>api.weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),frozen,'input immutability');
console.log('PASS weighted leave-one-out reference, direct refits, scale, singular removal');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
