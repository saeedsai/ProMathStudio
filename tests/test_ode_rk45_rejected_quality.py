"""RK45 rejected-step numerical quality and representable-time diagnostics."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class RK45RejectedQuality(unittest.TestCase):
    def test_rejected_error_ratio_and_time_resolution(self):
        script = r"""
const assert=require('assert'),fs=require('fs');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin);
const solve=new Function('const MAX=1e12;'+
 'const M={numerical:{evaluate:(expr,{t,y})=>expr==="stiff"?-30*y:expr==="one"?1:expr==="y"?y:NaN}};'+
 src.slice(begin,end)+';return solveAdaptive;')();
const stiff=solve({expression:'stiff',t0:0,t1:1,y0:1,tolerance:1e-9,maxSteps:5000});
assert(Math.abs(stiff.rows.at(-1)[1]-Math.exp(-30))<1e-7);
assert(stiff.rejected>0 && stiff.attempts===stiff.steps+stiff.rejected);
assert(stiff.maxRejectedErrorRatio>1);
assert(stiff.minRejectedStep>0 && Number.isFinite(stiff.minRejectedStep));
assert(stiff.maxAcceptedErrorRatio<=1+1e-12);
assert.equal(stiff.resolutionLimitedAttempts,0);
const smooth=solve({expression:'one',t0:0,t1:1,y0:0});
assert.equal(smooth.rejected,0);
assert.equal(smooth.maxRejectedErrorRatio,0);
assert.equal(smooth.minRejectedStep,null);
const epoch=solve({expression:'one',t0:1e12-1/8192,t1:1e12,y0:0});
assert.equal(epoch.rows.at(-1)[0],1e12);
assert(epoch.resolutionLimitedAttempts>=1);
assert.equal(epoch.minRejectedStep,null);
assert.throws(()=>solve({expression:'stiff',t0:0,t1:1,y0:1,tolerance:1e-12,maxSteps:4}),
 /max rejected local-error ratio=.*smallest rejected.*time-resolution-limited attempts=/);
const reverse=solve({expression:'y',t0:1,t1:0,y0:Math.E,tolerance:1e-10});
assert(Math.abs(reverse.rows.at(-1)[1]-1)<1e-8);
assert(reverse.maxAcceptedErrorRatio<=1+1e-12);
console.log('PASS RK45 rejected-step and time-resolution diagnostics');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS RK45", result.stdout)

    def test_standalone_parity_and_source_syntax(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("resolutionLimitedAttempts", source)
        self.assertIn("maxRejectedErrorRatio", source)
        result = subprocess.run(["node", "--check", "src/ode-tools.js"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
