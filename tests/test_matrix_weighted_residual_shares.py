"""Per-row weighted residual shares: analytical references and offline parity."""
import shutil
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class WeightedResidualShareTests(unittest.TestCase):
    def test_bundle_and_browser_gate(self):
        src=(ROOT/"src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        bundle=html.split('<script id="promath-matrix-tools">\n',1)[1].split("</script>",1)[0].rstrip("\n")
        self.assertEqual(src,bundle)
        self.assertIn("Relative weighted squared-residual shares",src)
        smoke=(ROOT/"tests/smoke_matrix_weighted_spectral_condition.py").read_text(encoding="utf-8")
        self.assertIn("weightedResidualShares",smoke)
        workflow=(ROOT/".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py",workflow)

    @unittest.skipUnless(shutil.which("node"),"Node required")
    def test_analytical_scale_zero_near_rank_and_invalid(self):
        js=r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const r=fit(A,b,w),expected=[1/105,4/105,100/105];
expected.forEach((v,i)=>assert(Math.abs(r.weightedResidualShares[i]-v)<1e-12));
assert(Math.abs(r.weightedResidualShares.reduce((a,b)=>a+b,0)-1)<1e-12);
const scaled=fit(A,b,[100,100,1]);
expected.forEach((v,i)=>assert(Math.abs(scaled.weightedResidualShares[i]-v)<1e-12));
assert(r.weightedResidualShareGuidance.includes('not outlier probabilities'));
const exact=fit([[1,0],[0,1],[0,0]],[1,2,0],[1,1,1]);
assert.deepStrictEqual(exact.weightedResidualShares,[0,0,0]);
const d=1e-10,near=fit([[1,1],[1,1+d],[1,1+2*d]],[1,1-d,1-2*d],[1,1,1]);
assert(near.weightedResidualShares.every(x=>Number.isFinite(x)&&x>=0&&x<=1+1e-12));
assert(Math.abs(near.weightedResidualShares.reduce((a,b)=>a+b,0)-1)<1e-10);
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,[1,1,1]),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted residual shares');
"""
        result=subprocess.run(["node","-e",js],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=="__main__":
    unittest.main()
