"""Delete-one coefficient shifts: direct QR refits, singular guard and scale invariance."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedLeaveOneOutShiftTests(unittest.TestCase):
    def test_offline_parity_and_required_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertEqual(source, html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertIn("looCoefficientShifts", source)
        self.assertIn("Leave-one-out coefficient shifts (rows 1–3", source)
        self.assertIn("not a statistical confidence interval", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_loo_shifts.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for direct QR numerical references")
    def test_direct_refits_scale_singular_and_invalid(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const api=new Function(src.slice(a,z)+';return {weightedLeastSquares,solve};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01];
const before=JSON.stringify([A,b,w]);
const fit=api.weightedLeastSquares(A,b,w);
assert.strictEqual(fit.looCoefficientShifts.length,3);
const expected=[[-5.942857142857143,5.828571428571429],
 [0.057142857142857,2.828571428571429],
 [0.057142857142857,-0.171428571428571]];
for(let i=0;i<3;i++){
 const keep=[0,1,2].filter(j=>j!==i);
 const direct=api.solve(keep.map(j=>A[j]),keep.map(j=>b[j])).solution;
 for(let j=0;j<2;j++){
  assert(Math.abs(fit.looCoefficientShifts[i][j]-expected[i][j])<1e-9);
  assert(Math.abs(fit.looCoefficientShifts[i][j]-(direct[j]-fit.solution[j]))<1e-9);
 }
}
const scaled=api.weightedLeastSquares(A,b,[10,10,.1]);
fit.looCoefficientShifts.forEach((row,i)=>row.forEach((v,j)=>
 assert(Math.abs(v-scaled.looCoefficientShifts[i][j])<1e-9)));
const singular=api.weightedLeastSquares([[1,0],[0,1],[0,1]],[2,3,4],[1,1,1]);
assert.strictEqual(singular.looCoefficientShifts[0],null);
assert(singular.looCoefficientShifts.slice(1).every(row=>row.every(Number.isFinite)));
assert.throws(()=>api.weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS leave-one-out coefficient influence');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
