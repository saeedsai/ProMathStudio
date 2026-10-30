"""RK45 rejection workload advisory, numerical references and standalone parity."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RK45WorkloadTests(unittest.TestCase):
    def test_standalone_parity(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_forward_backward_rejections_and_recovery(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(expr,{t,y})=>'+
 'expr==="stiff"?-100*y:expr==="reverse"?100*y:expr==="one"?1:NaN}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
for(const options of [
 {expression:'stiff',t0:0,t1:1,y0:1,tolerance:1e-9,maxSteps:5000},
 {expression:'reverse',t0:1,t1:0,y0:1,tolerance:1e-9,maxSteps:5000}
]){
 const r=solve(options);
 assert(Math.abs(r.rows.at(-1)[1]-Math.exp(-100))<1e-7);
 assert(r.rejected>=5 && r.rejectionWarning.includes('not diagnose stiffness'));
 assert(r.maxConsecutiveRejected>=1 && r.maxConsecutiveRejected<=r.rejected);
 assert.equal(r.attempts,r.steps+r.rejected);
 assert(r.maxAcceptedErrorRatio<=1+1e-12);
 assert.equal(r.rows.at(-1)[0],options.t1);
}
const smooth=solve({expression:'one',t0:0,t1:1,y0:0});
assert.equal(smooth.rejected,0);assert.equal(smooth.maxConsecutiveRejected,0);
assert.equal(smooth.rejectionWarning,null);
assert(Math.abs(smooth.rows.at(-1)[1]-1)<1e-12);
assert.throws(()=>solve({expression:'stiff',t0:0,t1:1,y0:1,tolerance:1e-12,maxSteps:4}),
 /longest rejection streak=\d+\./);
assert.throws(()=>solve({expression:'invalid',t0:0,t1:1,y0:1}),/derivative failed/);
console.log('PASS RK45 workload advisory and forward/backward references');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK45 workload", result.stdout)


if __name__ == "__main__":
    unittest.main()
