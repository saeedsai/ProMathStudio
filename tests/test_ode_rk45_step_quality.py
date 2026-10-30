"""RK45 accepted-step and embedded local-error diagnostics regression."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class RK45StepQuality(unittest.TestCase):
    def test_numerical_reference_and_step_statistics(self):
        script = r"""
const assert=require('assert'),fs=require('fs');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;'+
 'const M={numerical:{evaluate:(expr,{t,y})=>expr==="y"?y:expr==="one"?1:NaN}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
for(const [t0,t1,y0,expected] of [[0,1,1,Math.E],[1,0,Math.E,1]]){
 const result=solve({expression:'y',t0,t1,y0,tolerance:1e-10});
 assert(Math.abs(result.rows.at(-1)[1]-expected)<1e-8);
 assert(result.steps>0&&result.attempts===result.steps+result.rejected);
 const deltas=result.rows.slice(1).map((row,i)=>Math.abs(row[0]-result.rows[i][0]));
 assert(Math.abs(result.minAcceptedStep-Math.min(...deltas))<1e-14);
 assert(Math.abs(result.maxAcceptedStep-Math.max(...deltas))<1e-14);
 assert(result.minAcceptedStep>0&&result.maxAcceptedStep>=result.minAcceptedStep);
 assert(Number.isFinite(result.maxAcceptedErrorRatio));
 assert(result.maxAcceptedErrorRatio>=0&&result.maxAcceptedErrorRatio<=1+1e-12);
}
const constant=solve({expression:'one',t0:0,t1:1,y0:0,tolerance:1e-10});
assert(Math.abs(constant.rows.at(-1)[1]-1)<1e-12);
assert(constant.maxAcceptedErrorRatio<=1);
const quantum=solve({expression:'one',t0:1e12-1/8192,t1:1e12,y0:0});
assert.equal(quantum.rows.at(-1)[0],1e12);
assert.equal(quantum.minAcceptedStep,1/8192);
assert.equal(quantum.maxAcceptedStep,1/8192);
assert.throws(()=>solve({expression:'y',t0:0,t1:1,y0:1,tolerance:0}),/Tolerance/);
assert.throws(()=>solve({expression:'y',t0:0,t1:10,y0:1,tolerance:1e-12,maxSteps:4}),/exceeded maximum attempts/);
console.log('PASS RK45 accepted-step diagnostics and reference cases');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS RK45", result.stdout)

    def test_source_bundle_parity_and_syntax(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("maxAcceptedErrorRatio", source)
        result = subprocess.run(["node", "--check", "src/ode-tools.js"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
