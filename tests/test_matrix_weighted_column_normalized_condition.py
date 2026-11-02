"""Column-normalized weighted 3x2 condition: analytical and source/bundle regressions."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ColumnNormalizedConditionTests(unittest.TestCase):
    def test_bundle_and_quality_registration(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Column-normalized weighted design condition (2-norm)", source)
        self.assertIn("not a certified coefficient-error", source)
        self.assertIn("python tests/smoke_matrix_weighted_column_normalized_condition.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_independent_analytic_reference_and_scale_invariance(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
const fit=new Function(src.slice(a,z)+';return weightedLeastSquares;')();
const close=(a,b,t=1e-8)=>assert(Math.abs(a-b)<=t*Math.max(1,Math.abs(b)),a+' vs '+b);
const A=[[1,1],[1,1.0001],[1,1.0002]],b=[2,2.0001,2.0002],w=[1,1,1];
const before=JSON.stringify([A,b,w]);
const result=fit(A,b,w);
// Independent 3D cross-product area and column dot product reference.
const p=A.map(row=>row[0]),q=A.map(row=>row[1]);
const pn=Math.hypot(...p),qn=Math.hypot(...q);
const cosine=Math.abs(p.reduce((sum,x,i)=>sum+x*q[i],0))/(pn*qn);
const area=Math.hypot(p[1]*q[2]-p[2]*q[1],p[2]*q[0]-p[0]*q[2],p[0]*q[1]-p[1]*q[0]);
const expected=(pn*qn+Math.abs(p.reduce((sum,x,i)=>sum+x*q[i],0)))/area;
close(result.columnNormalizedCondition2,expected,1e-8);
assert(result.columnNormalizedCondition2>2e4);
close(fit(A.map(row=>[row[0]*1e5,row[1]*.01]),b,w).columnNormalizedCondition2,expected,1e-8);
close(fit(A,b,[100,100,100]).columnNormalizedCondition2,expected,1e-8);
const orth=fit([[1,0],[0,1e-6],[0,0]],[1,2,0],w);
close(orth.columnNormalizedCondition2,1,1e-12);
close(orth.spectralCondition2,1e6,1e-10);
assert(result.columnNormalizedConditionGuidance.includes('not a certified'));
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS column-normalized condition references');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
