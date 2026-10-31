"""RK45 exhaustion and floating-time-resolution diagnostics regression."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for numerical regression")
class RK45ProgressDiagnostics(unittest.TestCase):
    def test_forward_backward_exhaustion_and_resolution(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/ode-tools.js','utf8');
const begin=src.indexOf('function finite('),end=src.indexOf('function solveSystem(');
assert(begin>=0&&end>begin,'RK45 source extraction');
const solve=new Function(
 'const MAX=1e12;const M={numerical:{evaluate:(expr,{t,y})=>'+
 'expr==="y"?y:expr==="steep"?1e4*y:expr==="one"?1:Infinity}};'+
 src.slice(begin,end)+';return solveAdaptive;'
)();
const normal=solve({expression:'y',t0:0,t1:1,y0:1,tolerance:1e-10});
assert(Math.abs(normal.rows.at(-1)[1]-Math.E)<1e-8);
assert.equal(normal.attempts,normal.steps+normal.rejected);
const reverse=solve({expression:'one',t0:1,t1:0,y0:1,tolerance:1e-10});
assert(Math.abs(reverse.rows.at(-1)[1])<1e-12);
function failure(input,phrase,attempts,accepted,rejected){
 let message;
 try{solve(input)}catch(e){message=e.message}
 assert(message&&message.includes(phrase),message||'expected failure');
 for(const part of ['at t=','target=','attempted step=',
  'attempts='+attempts,'accepted='+accepted,'rejected='+rejected,
  'tolerance='+input.tolerance]){
   assert(message.includes(part),'missing '+part+': '+message);
 }
 return message;
}
failure({expression:'y',t0:0,t1:10,y0:1,tolerance:1e-12,maxSteps:4},
 'exceeded maximum attempts','4/4',1,3);
const backward=failure(
 {expression:'y',t0:10,t1:0,y0:1,tolerance:1e-12,maxSteps:4},
 'exceeded maximum attempts','4/4',1,3);
assert(backward.includes('attempted step=-'));
failure({expression:'steep',t0:999999999999.9998,t1:1e12,
 y0:1,tolerance:1e-12,maxSteps:1000},
 'underflow at current time resolution','1/1000',0,1);
console.log('PASS RK45 progress diagnostics and forward/backward references');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS RK45", result.stdout)

    def test_standalone_bundle_parity(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)
        self.assertIn("const progressError=", source)
        self.assertEqual(source.count("throw progressError("), 7)  # includes bounded stage overflow exhaustion and monotonic-grid guard
        self.assertIn("RK45 local-error estimate is not finite", source)
        self.assertIn("max rejected local-error ratio=", source)


if __name__ == "__main__":
    unittest.main()
