"""LOO predictions from QR identity match independent deleted-row fits."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedPredictionsTests(unittest.TestCase):
    def test_bundle_parity_and_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(source, html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertIn("looPredictions", source)
        self.assertIn("predicted minus observed", source)
        self.assertIn("python tests/smoke_matrix_weighted_predictions.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required for numerical references")
    def test_refits_scaling_singular_and_invalid(self):
        js = r"""
const fs=require('fs'),assert=require('assert'),src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const api=new Function(src.slice(a,z)+';return {weightedLeastSquares,solve};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const fit=api.weightedLeastSquares(A,b,w);
for(let i=0;i<3;i++){
 const keep=[0,1,2].filter(j=>j!==i);
 const x=api.solve(keep.map(j=>A[j]),keep.map(j=>b[j])).solution;
 const direct=A[i].reduce((sum,v,j)=>sum+v*x[j],0);
 assert(Math.abs(fit.looPredictions[i]-[-5,5,3][i])<1e-9);
 assert(Math.abs(fit.looPredictions[i]-direct)<1e-9);
 assert(Math.abs(fit.looPredictions[i]-b[i]-fit.looResiduals[i])<1e-9);
}
const scaled=api.weightedLeastSquares(A,b,[10,10,.1]);
fit.looPredictions.forEach((v,i)=>assert(Math.abs(v-scaled.looPredictions[i])<1e-9));
const singular=api.weightedLeastSquares([[1,0],[0,1],[0,1]],[2,3,4],[1,1,1]);
assert.strictEqual(singular.looPredictions[0],null);
assert(singular.looPredictions.slice(1).every(Number.isFinite));
assert.throws(()=>api.weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted LOO predicted values');
"""
        p = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == "__main__":
    unittest.main()
