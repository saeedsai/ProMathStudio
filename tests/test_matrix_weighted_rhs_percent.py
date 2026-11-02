"""Weighted proportional RHS box: analytical, corners, near-rank, failures."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class WeightedPercentBox(unittest.TestCase):
    def test_bundle_and_browser_gate(self):
        source=(ROOT/"src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        bundled=html.split('<script id="promath-matrix-tools">\n',1)[1].split("</script>",1)[0].rstrip("\n")
        self.assertEqual(source,bundled)
        self.assertIn("RHS independent ±1% proportional box sensitivity",source)
        self.assertIn("python tests/smoke_matrix_weighted_rhs_percent.py",
                      (ROOT/".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"),"Node required")
    def test_reference_and_eight_corners(self):
        js=r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const close=(a,b,t=1e-8)=>assert(Number.isFinite(a)&&Math.abs(a-b)<=t*Math.max(1,Math.abs(b)),a+' vs '+b);
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],snapshot=JSON.stringify([A,b,w]);
const r=fit(A,b,w),bound=r.rhsOnePercentBoxSensitivity;
close(bound[0],39/3500);close(bound[1],109/3500);
const maxima=[0,0];
for(let mask=0;mask<8;mask++){
 const bp=b.map((x,i)=>x+((mask>>i)&1?1:-1)*.01*Math.abs(x));
 const p=fit(A,bp,w);
 for(let j=0;j<2;j++)maxima[j]=Math.max(maxima[j],Math.abs(p.solution[j]-r.solution[j]));
}
maxima.forEach((x,j)=>close(x,bound[j]));
fit(A,b,[100,100,1]).rhsOnePercentBoxSensitivity.forEach((x,j)=>close(x,bound[j]));
fit(A,[0,0,0],w).rhsOnePercentBoxSensitivity.forEach(x=>close(x,0));
const near=fit([[1,1],[1,1.000001],[1,1.000002]],[1,.999999,.999998],[1,1,1]);
assert(near.rhsOnePercentBoxSensitivity.every(x=>Number.isFinite(x)&&x>1000));
assert(r.rhsOnePercentBoxGuidance.includes('not a statistical confidence interval'));
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),snapshot);
console.log('PASS weighted 1 percent RHS box');
"""
        result=subprocess.run(["node","-e",js],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

if __name__=="__main__":
    unittest.main()
