"""RK45 bounded intermediate-stage overflow retries and numerical regression."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class RK45StageOverflowTests(unittest.TestCase):
    def test_offline_bundle_parity(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)
        self.assertIn("stageOverflowRejected", source)
        self.assertIn("message.includes('RK45 k1 derivative failed')", source)
        self.assertIn("h*=0.5;", source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_forward_backward_recovery_and_hard_domain_error(self):
        js = r"""
const fs=require('fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;const M={numerical:{evaluate:(expr,{y})=>'+
 'expr==="guard"?(y>10?1e13:-1000*y):'+
 'expr==="reverse"?(y>10?1e13:1000*y):expr==="bad"?NaN:1}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
for(const o of [
 {expression:'guard',t0:0,t1:1,y0:1,tolerance:1e-7,maxSteps:5000},
 {expression:'reverse',t0:1,t1:0,y0:1,tolerance:1e-7,maxSteps:5000}
]){
 const r=solve(o);
 assert(r.stageOverflowRejected>=1,'bounded stage retries occurred');
 assert.equal(r.attempts,r.steps+r.rejected);
 assert(r.rejected>=r.stageOverflowRejected);
 assert(Number.isFinite(r.minRejectedStep)&&r.minRejectedStep>0);
 assert.equal(r.rows.at(-1)[0],o.t1);
 assert(Math.abs(r.rows.at(-1)[1])<1e-6);
}
const smooth=solve({expression:'one',t0:0,t1:1,y0:0});
assert.equal(smooth.stageOverflowRejected,0);
assert(Math.abs(smooth.rows.at(-1)[1]-1)<1e-12);
assert.throws(()=>solve({expression:'bad',t0:0,t1:1,y0:1}),/RK45 k1 derivative failed/);
console.log('PASS RK45 bounded overflow retry forward/backward, smooth and hard-error');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS RK45 bounded overflow", result.stdout)


if __name__ == "__main__":
    unittest.main()
