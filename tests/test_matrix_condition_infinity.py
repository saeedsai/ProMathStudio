"""Numerical reference and standalone parity for infinity-norm conditioning."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for numerical regression")
class MatrixConditionInfinityTests(unittest.TestCase):
    def test_condition_number_reference_scaling_and_failure_paths(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const start=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=source.indexOf('/* Jacobi rotations for bounded real',start);
assert(start>=0&&end>start);
const {solve,inverse,conditionInfinity}=new Function(source.slice(start,end)+';return {solve,inverse,conditionInfinity};')();
const cases=[
 {A:[[1,0],[0,1]],b:[2,3],condition:1},
 {A:[[2,1],[0,3]],b:[3,6],condition:2},
 {A:[[2,0,0],[0,3,0],[0,0,4]],b:[2,6,12],condition:2},
 {A:[[1e-9,0],[0,1e9]],b:[2e-9,3e9],condition:1e18},
];
for(const {A,b,condition} of cases){
 const beforeA=JSON.stringify(A),beforeB=JSON.stringify(b);
 const k=conditionInfinity(A);
 assert(Number.isFinite(k)&&k>=1,'finite nonnegative condition');
 assert(Math.abs(k-condition)/condition<1e-12,'infinity norm condition reference');
 const x=solve(A,b).solution;
 assert(x.every(Number.isFinite),'valid Ax=b solution');
 const inv=inverse(A);
 assert(inv.flat().every(Number.isFinite),'valid inverse');
 assert.equal(JSON.stringify(A),beforeA,'matrix input preserved');
 assert.equal(JSON.stringify(b),beforeB,'RHS input preserved');
}
const near=[[1,1],[1,1+1e-10]];
const k=conditionInfinity(near);
assert(k>1e10&&k<1e11,'near-singular condition is large');
assert.throws(()=>conditionInfinity([[1,2],[2,4]]),/Singular/);
assert.throws(()=>conditionInfinity([[1,0,0],[0,1,0]]),/square matrix/);
assert.throws(()=>conditionInfinity([[1,true],[0,1]]),/number/);
assert.throws(()=>conditionInfinity([[0,0],[0,0]]),/Singular/);
console.log('PASS exact infinity-norm condition references, scaling, singularity and immutability');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True,
            text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_standalone_parity_and_both_consumers(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("/* ProMathStudio small-matrix calculator:")
        end = html.index("</script>", start)
        self.assertEqual(html[start:end], source + "\n")
        self.assertIn("function conditionInfinity(A)", source)
        self.assertIn("operation==='solve'||operation==='inverse'", source)
        self.assertIn("Infinity-norm condition number:", source)
        self.assertIn("M.matrixTools={validate,determinant,transpose,inverse,add", source)
        self.assertIn("pseudoinverse,conditionInfinity,notation", source)


if __name__ == "__main__":
    unittest.main()
