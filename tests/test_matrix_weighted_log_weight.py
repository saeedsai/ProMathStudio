"""First-order weighted log-weight response: numerical reference and source parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedLogWeightTests(unittest.TestCase):
    def test_parity_and_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Log-weight first-order coefficient responses", source)
        self.assertIn("not an exact finite-change prediction", source)
        self.assertIn("python tests/smoke_matrix_weighted_log_weight.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_independent_reference_and_finite_difference(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const {weightedLeastSquares}=new Function(src.slice(a,z)+';return {weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const fit=weightedLeastSquares(A,b,w);
const s00=w.reduce((s,wi,i)=>s+wi*A[i][0]**2,0);
const s01=w.reduce((s,wi,i)=>s+wi*A[i][0]*A[i][1],0);
const s11=w.reduce((s,wi,i)=>s+wi*A[i][1]**2,0);
const det=s00*s11-s01*s01,h=1e-4;assert(det>0);
for(let i=0;i<3;i++){
 const e=A[i][0]*fit.solution[0]+A[i][1]*fit.solution[1]-b[i];
 const expected=[-(s11*A[i][0]-s01*A[i][1])*w[i]*e/det,
                 -(-s01*A[i][0]+s00*A[i][1])*w[i]*e/det];
 const up=w.slice(),down=w.slice();up[i]*=Math.exp(h);down[i]*=Math.exp(-h);
 const plus=weightedLeastSquares(A,b,up),minus=weightedLeastSquares(A,b,down);
 for(let j=0;j<2;j++){
  assert(Math.abs(fit.logWeightResponseRows[i][j]-expected[j])<1e-11,'reference '+i+','+j);
  assert(Math.abs((plus.solution[j]-minus.solution[j])/(2*h)-expected[j])<1e-7,'perturbation '+i+','+j);
 }
}
const scaled=weightedLeastSquares(A,b,[100,100,1]);
for(let i=0;i<3;i++)for(let j=0;j<2;j++)
 assert(Math.abs(fit.logWeightResponseRows[i][j]-scaled.logWeightResponseRows[i][j])<1e-11);
const exact=weightedLeastSquares(A,[1,2,3],w);
assert(exact.logWeightResponseRows.flat().every(x=>Math.abs(x)<1e-10));
const near=weightedLeastSquares([[1,1],[1,1.0001],[1,1.0002]],[1,1.0001,1.0002],[1,1,1]);
assert(near.logWeightResponseRows.flat().every(Number.isFinite));
assert.throws(()=>weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS log-weight derivative numerical reference and finite difference');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
