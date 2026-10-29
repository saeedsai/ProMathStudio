"""Regression for inverse reuse of the canonical scaled-pivot Ax=b solver."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for numerical regression")
class MatrixSharedSolveInverseTests(unittest.TestCase):
    def test_inverse_reuses_solver_with_reference_and_failure_paths(self):
        script = r"""
const fs = require('node:fs'), assert = require('node:assert/strict');
const source = fs.readFileSync('src/matrix-tools.js', 'utf8');
const start = source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end = source.indexOf('/* Jacobi rotations', start);
assert(start >= 0 && end > start, 'Matrix kernel boundaries');
const api = new Function(source.slice(start,end)+';return {solve,inverse};')();
const near = (a,b,tol=1e-10) => Math.abs(a-b) <= tol*Math.max(1,Math.abs(b));
for(const [A,expected] of [
  [[[1,2],[3,4]],[[-2,1],[1.5,-0.5]]],
  [[[0,2,0],[3,0,0],[0,0,4]],[[0,1/3,0],[1/2,0,0],[0,0,1/4]]],
  [[[1e-9,0],[0,1e9]],[[1e9,0],[0,1e-9]]],
  [[[1e-9,0,0],[0,2e9,0],[0,0,3]],[[1e9,0,0],[0,5e-10,0],[0,0,1/3]]],
]){
  const before=JSON.stringify(A), n=A.length, inverse=api.inverse(A);
  assert.equal(JSON.stringify(A),before,'Inverse must not mutate inputs');
  for(let col=0;col<n;col++){
    const rhs=Array.from({length:n},(_,i)=>Number(i===col));
    const solved=api.solve(A,rhs);
    assert(solved.residual<1e-10);
    for(let row=0;row<n;row++){
      assert(near(inverse[row][col],solved.solution[row]),'Inverse column differs from Ax=b');
      assert(near(inverse[row][col],expected[row][col]),'Inverse reference mismatch');
    }
  }
  for(let i=0;i<n;i++)for(let j=0;j<n;j++){
    const value=A[i].reduce((sum,x,k)=>sum+x*inverse[k][j],0);
    assert(near(value,Number(i===j)),'A * inverse(A) differs from identity');
  }
}
for(const A of [
  [[0,0],[0,0]],
  [[1,2],[2,4]],
  [[1,1],[1,1+1e-13]],
  [[1,2,3],[4,5,6]],
]){
  assert.throws(()=>api.inverse(A),/Singular or nearly singular|square/);
}
assert.throws(()=>api.inverse([[1,0],[true,1]]),/Enter a number/);
assert.throws(()=>api.inverse([[1,0],[Infinity,1]]),/finite numbers/);
const body=source.slice(source.indexOf('function inverse(A){'),source.indexOf('/* Jacobi rotations'));
assert(body.includes('solve(A,rhs).solution'),'Inverse must reuse canonical Ax=b solver');
assert(!body.includes('const B=A.map'),'No separate Gauss-Jordan elimination');
console.log('PASS shared Ax=b and inverse numerical references, scale and errors');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True,
            text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_standalone_bundle_parity(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index('/* ProMathStudio small-matrix calculator:')
        end = html.index("</script>", start)
        self.assertEqual(html[start:end], source + "\n")


if __name__ == "__main__":
    unittest.main()
