"""Numerical resolution screen for near-rank weighted least squares."""
import shutil
import subprocess
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class WeightedRoundoffScreen(unittest.TestCase):
    def test_bundle_and_browser_registration(self):
        source=(ROOT/"src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html=(ROOT/"index.html").read_text(encoding="utf-8")
        bundle=html.split('<script id="promath-matrix-tools">\n',1)[1].split("</script>",1)[0].rstrip("\n")
        self.assertEqual(source,bundle)
        self.assertIn("Coefficient roundoff amplification screen",source)
        smoke=(ROOT/"tests/smoke_matrix_weighted_spectral_condition.py").read_text(encoding="utf-8")
        self.assertIn("Near-rank numerical warning",smoke)
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py",
            (ROOT/".github/workflows/quality.yml").read_text(encoding="utf-8"))
    @unittest.skipUnless(shutil.which("node"),"Node required")
    def test_reference_near_rank_scaling_and_invalid(self):
        js=r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],snapshot=JSON.stringify([A,b,w]);
const r=fit(A,b,w);
assert(Math.abs(r.coefficientRoundoffScreen-2.5904639930794775*Number.EPSILON)<1e-26);
assert(r.coefficientRoundoffGuidance.includes('not a certified coefficient-error bound'));
assert(Math.abs(fit(A,b,[100,100,1]).coefficientRoundoffScreen-r.coefficientRoundoffScreen)<1e-25);
const d=1e-10,near=fit([[1,1],[1,1+d],[1,1+2*d]],[1,1-d,1-2*d],[1,1,1]);
assert(near.coefficientRoundoffScreen>1e-6);
assert(near.coefficientRoundoffGuidance.includes('Near-rank numerical warning'));
assert(near.solution.every(Number.isFinite));
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,[1,1,1]),/Rank-deficient/);
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),snapshot);
console.log('PASS weighted roundoff screen');
"""
        result=subprocess.run(["node","-e",js],cwd=ROOT,capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
if __name__=="__main__":
    unittest.main()
