"""Exact fixed-design weighted RHS box sensitivity and bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedRhsBoxTests(unittest.TestCase):
    def test_source_bundle_and_ci_registration(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)
        self.assertIn("RHS ±1-unit box sensitivity", source)
        self.assertIn("not a statistical confidence interval", source)
        self.assertIn("python tests/smoke_matrix_weighted_rhs_box.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_analytic_reference_and_all_eight_box_corners(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
const fit=new Function(src.slice(a,z)+';return weightedLeastSquares;')();
const close=(x,y,t=1e-8)=>assert(Number.isFinite(x)&&Math.abs(x-y)<=t*Math.max(1,Math.abs(y)),x+' vs '+y);
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const base=fit(A,b,w);
close(base.rhsUnitBoxSensitivity[0],107/105);
close(base.rhsUnitBoxSensitivity[1],68/35);
const maxima=[0,0];
for(let mask=0;mask<8;mask++){
 const delta=[0,1,2].map(i=>(mask&(1<<i))?1:-1);
 const perturbed=fit(A,b.map((x,i)=>x+delta[i]),w);
 for(let j=0;j<2;j++){
  const actual=perturbed.solution[j]-base.solution[j];
  const predicted=delta.reduce((sum,d,i)=>sum+d*base.rhsResponseRows[i][j],0);
  close(actual,predicted);
  maxima[j]=Math.max(maxima[j],Math.abs(actual));
 }
}
maxima.forEach((x,j)=>close(x,base.rhsUnitBoxSensitivity[j]));
fit(A,b,[10,10,.1]).rhsUnitBoxSensitivity.forEach((x,j)=>close(x,base.rhsUnitBoxSensitivity[j]));
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
assert(base.rhsUnitBoxGuidance.includes('not a statistical confidence interval'));
console.log('PASS weighted RHS box analytic and corner references');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
