"""Numerical sensitivity advisory regression and standalone parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class MatrixConditionGuidanceTests(unittest.TestCase):
    def test_reference_threshold_and_invalid_inputs(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const b=src.indexOf('/* Jacobi rotations for bounded real',a);
assert(a>=0&&b>a);
const {conditionInfinity,conditionGuidance,solve}=new Function(src.slice(a,b)+';return {conditionInfinity,conditionGuidance,solve};')();
assert.equal(conditionInfinity([[1,0],[0,1]]),1);
assert.match(conditionGuidance(1),/Below the 1e8/);
assert.match(conditionGuidance(1e8-1),/Below the 1e8/);
assert.match(conditionGuidance(1e8),/High sensitivity/);
const A=[[1e-9,0],[0,1e9]],rhs=[2e-9,3e9];
const snapshot=JSON.stringify([A,rhs]);
assert.equal(conditionInfinity(A),1e18);
assert.match(conditionGuidance(conditionInfinity(A)),/small residual does not certify accuracy/);
const x=solve(A,rhs).solution;
assert(Math.abs(x[0]-2)<1e-12&&Math.abs(x[1]-3)<1e-12);
assert.equal(JSON.stringify([A,rhs]),snapshot);
assert(conditionInfinity([[1,1],[1,1+1e-10]])>1e10);
for(const bad of [NaN,Infinity,-Infinity,-1,0,'1',true,null,{},[]])
 assert.throws(()=>conditionGuidance(bad),/finite condition number/);
assert.throws(()=>conditionInfinity([[1,2],[2,4]]),/Singular/);
console.log('PASS matrix condition guidance threshold, reference, invalid and immutability');
"""
        run = subprocess.run(["node", "-e", script], cwd=ROOT,
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_standalone_and_both_consumers(self):
        src = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("/* ProMathStudio small-matrix calculator:")
        end = html.index("</script>", start)
        self.assertEqual(html[start:end], src + "\n")
        self.assertIn("function conditionGuidance(k)", src)
        self.assertIn("operation==='solve'||operation==='inverse'", src)
        self.assertIn("conditionGuidance(k)", src)
        self.assertIn("small residual does not certify accuracy", src)


if __name__ == "__main__":
    unittest.main()
