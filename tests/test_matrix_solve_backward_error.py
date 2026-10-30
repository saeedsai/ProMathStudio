"""Numerical regression: infinity-norm backward error for bounded Ax=b."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for numerical regression")
class MatrixSolveBackwardErrorTests(unittest.TestCase):
    def test_reference_scaling_and_failure_paths(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const start=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=src.indexOf('/* Doolittle P*A=L*U',start);
assert(start>=0&&end>start);
const {solve}=new Function(src.slice(start,end)+';return {solve};')();
for(const [A,b,expected] of [
 [[[3,1],[1,7]],[1,2],[5/20,5/20]],
 [[[1e-9,0],[0,1e9]],[2e-9,3e9],[2,3]],
 [[[2,1,0],[0,3,1],[1,0,4]],[4,9,13],[1,2,3]]
]){
 const beforeA=JSON.stringify(A),beforeB=JSON.stringify(b);
 const result=solve(A,b),x=result.solution;
 assert.equal(JSON.stringify(A),beforeA);
 assert.equal(JSON.stringify(b),beforeB);
 assert.equal(result.rank,A.length);
 x.forEach((v,i)=>assert(Math.abs(v-expected[i])<1e-9,'solution reference'));
 const errors=A.map((row,i)=>Math.abs(row.reduce((sum,a,j)=>sum+a*x[j],0)-b[i]));
 const absolute=Math.max(...errors);
 const normA=Math.max(...A.map(row=>row.reduce((sum,a)=>sum+Math.abs(a),0)));
 const normX=Math.max(...x.map(Math.abs)),normB=Math.max(...b.map(Math.abs));
 const backward=absolute/Math.max(Number.MIN_VALUE,normA*normX+normB);
 assert.equal(result.absoluteResidual,absolute);
 assert.equal(result.normwiseBackwardError,backward);
 assert(result.residual>=0&&result.normwiseBackwardError>=0);
 assert(result.normwiseBackwardError<=1e-10);
 assert(Number.isFinite(result.absoluteResidual));
 assert(Number.isFinite(result.normwiseBackwardError));
}
const zero=solve([[1,0],[0,1]],[0,0]);
assert.equal(zero.absoluteResidual,0);
assert.equal(zero.normwiseBackwardError,0);
assert.throws(()=>solve([[1,2],[2,4]],[3,6]),/Singular/);
assert.throws(()=>solve([[1,2],[2,4]],[3,7]),/Inconsistent/);
assert.throws(()=>solve([[1,0],[0,1]],[true,1]),/Enter a number/);
assert(!('conditionNumber' in zero),'backward error is not a condition estimate');
console.log('PASS Ax=b backward error references, scale, singular and validation');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True,
            text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_standalone_parity_and_visible_diagnostics(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("/* ProMathStudio small-matrix calculator:")
        end = html.index("</script>", start)
        self.assertEqual(html[start:end], source + "\n")
        self.assertIn("Normwise backward error (∞):", source)
        self.assertIn("Max absolute residual:", source)


if __name__ == "__main__":
    unittest.main()
