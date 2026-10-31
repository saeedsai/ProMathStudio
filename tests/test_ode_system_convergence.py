"""Coupled two-state RK4 step-doubling diagnostic: references, boundary, backward and parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class SystemConvergenceTests(unittest.TestCase):
    def test_step_doubling_diagnostic(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const html=fs.readFileSync('index.html','utf8');
const tag='<script id="promath-ode-tools">\n';
const a=html.indexOf(tag)+tag.length,b=html.indexOf('</script>',a);
assert.strictEqual(html.slice(a,b).trimEnd(),src.trimEnd());       // standalone parity
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
const stop=src.indexOf('\nconst area=document');
const evalFn=(e,{t,y,z})=>e==='z'?z:e==='-y'?-y:e==='bad'?NaN:0;
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:'+evalFn.toString()+'}};'+
 src.slice(begin,end)+src.slice(end,stop)+';return solveSystem;')();
// Harmonic oscillator y'=z, z'=-y, y(0)=0, z(0)=1 has exact y=sin t, z=cos t.
for(const dir of [1,-1]){
 const o=dir>0?{t0:0,t1:1,y0:0,z0:1}:{t0:1,t1:0,y0:Math.sin(1),z0:Math.cos(1)};
 const ref=dir>0?[Math.sin(1),Math.cos(1)]:[0,1];
 const r=solve({expression:'z',expressionZ:'-y',steps:40,...o});
 const err=Math.max(Math.abs(r.rows.at(-1)[1]-ref[0]),Math.abs(r.rows.at(-1)[2]-ref[1]));
 assert.strictEqual(r.convergence.refinedSteps,80);
 assert(r.convergence.endpointDifference>0&&r.convergence.endpointDifference<1e-5);
 // RK4 is 4th order: |x_N - x_2N| ~ (15/16)*err_N, so the diagnostic tracks the true error.
 assert(err<=2*r.convergence.endpointDifference+1e-14 && err>=0.2*r.convergence.endpointDifference);
}
// Boundary: 500 refines, 501 reports no diagnostic and keeps the original trajectory.
assert(solve({expression:'z',expressionZ:'-y',steps:500}).convergence!==null);
const big=solve({expression:'z',expressionZ:'-y',steps:501});
assert.strictEqual(big.convergence,null);assert.strictEqual(big.rows.length,502);
// Original trajectory unchanged by the diagnostic.
const plain=solve({expression:'z',expressionZ:'-y',steps:40});
assert.strictEqual(plain.rows.length,41);assert.strictEqual(plain.steps,40);
// Failure paths unchanged: domain error and invalid steps still throw.
assert.throws(()=>solve({expression:'bad',expressionZ:'-y',steps:40}),/Derivative dy\/dt/);
assert.throws(()=>solve({expression:'z',expressionZ:'-y',steps:3}),/integer from 4 to 1000/);
// Refined grid collapsing at a huge time offset must not fail the original valid solve.
const huge=solve({expression:'z',expressionZ:'-y',t0:1e11,t1:1e11+2e-3,y0:0,z0:1,steps:40});
assert.strictEqual(huge.rows.length,41);
console.log('PASS coupled RK4 step-doubling diagnostic');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS coupled RK4", result.stdout)


if __name__ == "__main__":
    unittest.main()
