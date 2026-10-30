"""RK45 intermediate-stage overflow recovery: bounded retries, domain errors stay fatal."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RK45StageOverflowTests(unittest.TestCase):
    def test_standalone_parity(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_overflow_recovery_forward_backward_and_failures(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(e,{t,y})=>'+
 'e==="decay"?-1e5*y:e==="grow"?1e5*y:e==="square"?y*y:NaN}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
// Exact solutions exp(-1000) ~ 0: first trial step overflows 1e12 in a stage, then recovers.
for(const o of [{expression:'decay',t0:0,t1:0.01,y0:1},{expression:'grow',t0:0.01,t1:0,y0:1}]){
 const r=solve({...o,tolerance:1e-6,maxSteps:10000});
 assert(r.stageOverflowRetries>=1 && r.rejected>=r.stageOverflowRetries);
 assert(Math.abs(r.rows.at(-1)[1])<1e-5);
 assert.equal(r.rows.at(-1)[0],o.t1);
 assert.equal(r.attempts,r.steps+r.rejected);
}
// Genuine finite-time blow-up y'=y^2 (y(0)=1 blows up at t=1): recovery stays bounded by the attempt limit.
assert.throws(()=>solve({expression:'square',t0:0,t1:2,y0:1,maxSteps:200}),
 /exceeded maximum attempts.*stage-overflow retries=\d+/);
// Domain errors are not retried.
assert.throws(()=>solve({expression:'bad',t0:0,t1:1,y0:1}),/derivative failed/);
// Smooth problem reports no overflow retries.
assert.equal(solve({expression:'grow',t0:0,t1:1e-6,y0:1}).stageOverflowRetries,0);
console.log('PASS RK45 stage overflow recovery');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK45 stage overflow", result.stdout)


if __name__ == "__main__":
    unittest.main()
