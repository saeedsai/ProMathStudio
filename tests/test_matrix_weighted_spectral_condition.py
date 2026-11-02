"""Independent weighted 3x2 spectral condition references and offline parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class SpectralConditionTests(unittest.TestCase):
    def test_bundle_and_mandatory_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Weighted design spectral condition estimate (2-norm)", source)
        self.assertIn("not a certified coefficient-error", source)
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_analytic_near_rank_scaling_and_failures(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const {weightedLeastSquares}=new Function(src.slice(a,z)+';return {weightedLeastSquares};')();
const close=(x,y,t=1e-9)=>{assert(Number.isFinite(x));assert(Math.abs(x-y)<=t*Math.max(1,y),x+' vs '+y);};
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const fit=weightedLeastSquares(A,b,w);
close(fit.spectralCondition2,2.5904639930794775,1e-12);
close(weightedLeastSquares(A,b,[100,100,1]).spectralCondition2,fit.spectralCondition2,1e-12);
close(weightedLeastSquares([[1,0],[0,1],[0,0]],[0,0,0],[1,1,1]).spectralCondition2,1);
close(weightedLeastSquares([[1,0],[0,1e-6],[0,0]],[0,0,0],[1,1,1]).spectralCondition2,1e6);
close(weightedLeastSquares([[1,0],[0,1],[0,0]],[0,0,0],[1e12,1,1e-12]).spectralCondition2,1e6);
const near=[[1,1],[1,1.0001],[1,1.0002]],p=near.map(r=>r[0]),q=near.map(r=>r[1]);
const c00=p.reduce((s,x)=>s+x*x,0),c11=q.reduce((s,x)=>s+x*x,0);
const c01=p.reduce((s,x,i)=>s+x*q[i],0);
const lambdaMax=(c00+c11+Math.hypot(c00-c11,2*c01))/2;
const area=Math.hypot(p[1]*q[2]-p[2]*q[1],p[2]*q[0]-p[0]*q[2],p[0]*q[1]-p[1]*q[0]);
const nearFit=weightedLeastSquares(near,[2,2.0001,2.0002],[1,1,1]);
close(nearFit.spectralCondition2,lambdaMax/area,1e-9);
assert(nearFit.spectralCondition2>2e4);
assert(nearFit.spectralConditionGuidance.includes('not a certified'));
assert.throws(()=>weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted spectral conditioning references');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
