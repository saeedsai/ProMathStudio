"""RK45 stage-time collision diagnostics at floating-point time boundaries."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class RK45StageResolution(unittest.TestCase):
    def test_numerical_reference_and_collision_diagnostics(self):
        script = r"""
const assert=require('assert'),fs=require('fs');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;'+
 'const M={numerical:{evaluate:(expr,{t,y})=>expr==="one"?1:expr==="y"?y:expr==="stiff"?-30*y:NaN}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
for(const [t0,t1,y0,expected] of [[0,1,1,Math.E],[1,0,Math.E,1]]){
 const out=solve({expression:'y',t0,t1,y0,tolerance:1e-10});
 assert(Math.abs(out.rows.at(-1)[1]-expected)<1e-8);
 assert.equal(out.stageTimeCollisionAttempts,0);
 assert.equal(out.stageTimeCollisionAcceptedSteps,0);
}
const quantum=1/8192;
for(const [t0,t1,expected] of [[1e12-quantum,1e12,quantum],
 [1e12,1e12-quantum,-quantum]]){
 const out=solve({expression:'one',t0,t1,y0:0});
 assert.equal(out.rows.at(-1)[0],t1);
 assert(Math.abs(out.rows.at(-1)[1]-expected)<1e-12);
 assert(out.stageTimeCollisionAttempts>=1);
 assert(out.stageTimeCollisionAcceptedSteps>=1);
 assert(out.stageTimeCollisionAcceptedSteps<=out.stageTimeCollisionAttempts);
 assert(out.stageTimeCollisionAcceptedSteps<=out.steps);
 assert.equal(out.attempts,out.steps+out.rejected);
}
const stiff=solve({expression:'stiff',t0:0,t1:1,y0:1,tolerance:1e-9,maxSteps:5000});
assert(Math.abs(stiff.rows.at(-1)[1]-Math.exp(-30))<1e-7);
assert(stiff.rejected>0);
assert.equal(stiff.stageTimeCollisionAcceptedSteps,0);
assert.throws(()=>solve({expression:'stiff',t0:0,t1:1,y0:1,tolerance:1e-12,maxSteps:4}),
 /exceeded maximum attempts.*collapsed-stage attempts=0/);
assert.throws(()=>solve({expression:'one',t0:0,t1:0}),/End time/);
console.log('PASS RK45 stage-time resolution diagnostics');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS RK45", result.stdout)

    def test_standalone_parity_and_syntax(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("stageTimeCollisionAcceptedSteps", source)
        result = subprocess.run(["node", "--check", "src/ode-tools.js"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
