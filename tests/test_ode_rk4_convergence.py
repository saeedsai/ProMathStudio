"""Scalar fixed-step RK4 step-doubling diagnostic: references, boundary, backward and parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class ScalarConvergenceTests(unittest.TestCase):
    def test_step_doubling_diagnostic(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const tag='<script id="promath-ode-tools">\n';
const a=html.indexOf(tag)+tag.length,b=html.indexOf('</script>',a);
assert.strictEqual(html.slice(a,b).trimEnd(),src.trimEnd());       // standalone parity
const begin=src.indexOf('function finite('),end=src.indexOf('function solveAdaptive(');
assert(begin>=0&&end>begin);
const evalFn=(e,{t,y})=>e==='y'?y:e==='bad'?NaN:0;
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:'+evalFn.toString()+'}};'+
 src.slice(begin,end)+';return solve;')();
// y'=y: forward exp(1) from y(0)=1; backward from y(1)=e returns to 1.
for(const [o,ref] of [[{t0:0,t1:1,y0:1},Math.E],[{t0:1,t1:0,y0:Math.E},1]]){
 const r=solve({expression:'y',steps:20,...o});
 const err=Math.abs(r.rows.at(-1)[1]-ref);
 assert.strictEqual(r.convergence.refinedSteps,40);
 assert(r.convergence.endpointDifference>0&&r.convergence.endpointDifference<1e-5);
 // 4th-order scheme: |y_N - y_2N| ~ (15/16) err_N, so the diagnostic tracks the true error.
 assert(err<=2*r.convergence.endpointDifference+1e-14&&err>=0.2*r.convergence.endpointDifference,err+' vs '+r.convergence.endpointDifference);
}
// Boundary: 500 refines, 501 reports no diagnostic and keeps the original trajectory.
assert(solve({expression:'y',steps:500}).convergence!==null);
const big=solve({expression:'y',steps:501});
assert.strictEqual(big.convergence,null);assert.strictEqual(big.rows.length,502);
// The diagnostic does not alter the original trajectory.
const plain=solve({expression:'y',steps:40});
assert.strictEqual(plain.rows.length,41);assert.strictEqual(plain.steps,40);
// Failure paths unchanged.
assert.throws(()=>solve({expression:'bad',steps:40}),/Derivative/);
assert.throws(()=>solve({expression:'y',steps:3}),/integer from 4 to 1000/);
// Refined grid collapsing at a huge offset must not fail the valid original solve.
const huge=solve({expression:'y',t0:1e11,t1:1e11+2e-3,y0:1,steps:40});
assert.strictEqual(huge.rows.length,41);
console.log('PASS scalar RK4 step-doubling diagnostic');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS scalar RK4", result.stdout)


if __name__ == "__main__":
    unittest.main()
