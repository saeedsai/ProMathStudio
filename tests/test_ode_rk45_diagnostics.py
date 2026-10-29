"""RK45 stage-specific numerical failure regression and standalone consistency."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class RK45DerivativeDiagnostics(unittest.TestCase):
    def test_reference_and_stage_failures(self):
        script = r"""
const fs = require('fs'), assert = require('assert');
const source = fs.readFileSync('src/ode-tools.js', 'utf8');
const start = source.indexOf('function finite(');
const end = source.indexOf('function solveSystem(');
assert(start >= 0 && end > start, 'solver boundaries');
const code = source.slice(start, end);
const solve = new Function(
  'const MAX=1e12;const M={numerical:{evaluate:(expr,{t,y})=>'+
  'expr==="y"?y:expr==="invalid"?Infinity:'+
  'expr==="overflow"?2e12:expr==="stage2"?(t===0?1:NaN):1}};'+
  code+';return solveAdaptive;'
)();
const forward = solve({expression:'y',t0:0,t1:1,y0:1,tolerance:1e-10});
const backward = solve({expression:'y',t0:1,t1:0,y0:Math.E,tolerance:1e-10});
assert(Math.abs(forward.rows.at(-1)[1]-Math.E)<1e-8);
assert(Math.abs(backward.rows.at(-1)[1]-1)<1e-8);
for (const [expr,stage] of [['invalid','k1'],['overflow','k1'],['stage2','k2']]) {
  assert.throws(
    ()=>solve({expression:expr,t0:0,t1:1,y0:1}),
    e=>e.message.includes('RK45 '+stage+' derivative failed at t=') &&
       e.message.includes(', y=') && e.message.includes('Derivative'),
    expr+' must report derivative stage and state'
  );
}
console.log('PASS: RK45 forward/backward references, k1/k2 domain and overflow');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("PASS:", result.stdout)

    def test_standalone_parity_and_syntax(self):
        source = (ROOT / "src/ode-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        embedded = html.split('<script id="promath-ode-tools">\n', 1)[1].split(
            "</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, embedded)
        adaptive = source.split("function solveAdaptive(", 1)[1].split(
            "function solveSystem(", 1)[0]
        self.assertEqual(adaptive.count("derivative failed at t="), 1)
        for stage in ("k1", "k2", "k3", "k4", "k5", "k6", "k7"):
            self.assertIn("'" + stage + "'", adaptive)
        result = subprocess.run(["node", "--check", "src/ode-tools.js"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
