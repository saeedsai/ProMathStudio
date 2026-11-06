"""Uncertainty propagation module: bundle parity, safety rules, workflow registration and Node numeric references."""
import json
import math
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "uncertainty-tools.js"

# The Node harness stubs the shared evaluator with fixed JavaScript models (test-only; the module itself
# always evaluates through MathStudio.numerical.evaluate).
NODE_SCRIPT = r"""
const models={'a+b':e=>e.a+e.b,'a*b':e=>e.a*e.b,'x^2':e=>e.x*e.x,'x':e=>e.x,'a+b+c':e=>e.a+e.b+e.c,'log(x)':e=>{if(!(e.x>0))throw Error('log domain');return Math.log(e.x);}};
global.window={MathStudio:{numerical:{evaluate:(expr,vars)=>{const f=models[expr];if(!f)throw Error('unknown model');return f(vars);}}}};
global.document={getElementById:()=>null};
require(process.argv[1]);const U=window.MathStudio.uncertainty,out={};
const v=(name,mean,u,distribution='normal')=>distribution==='uniform'?{name,mean,halfWidth:u,distribution}:{name,mean,u,distribution};
out.sum=U.propagate({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)]});
out.prod=U.propagate({expression:'a*b',variables:[v('a',10,0.1),v('b',5,0.2)],k:3});
out.rho1=U.propagate({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:1}]}).uc;
out.rhoM1=U.propagate({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:-1}]}).uc;
out.uniform=U.propagate({expression:'x',variables:[v('x',0,1,'uniform')]}).uc;
const sq=U.run({expression:'x^2',variables:[v('x',0,1)],samples:100000,seed:11});
out.sq={lin:sq.linear.uc,mean:sq.monteCarlo.mean,std:sq.monteCarlo.std,flag:sq.comparison.nonlinear};
const mc=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],samples:100000,seed:5});
out.mc={mean:mc.monteCarlo.mean,std:mc.monteCarlo.std,flag:mc.comparison.nonlinear,sym:mc.monteCarlo.symmetric95,short:mc.monteCarlo.shortest95,n:mc.monteCarlo.samples};
const again=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],samples:100000,seed:5}),other=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],samples:100000,seed:6});
out.same=again.monteCarlo.mean===mc.monteCarlo.mean&&again.monteCarlo.std===mc.monteCarlo.std&&again.monteCarlo.shortest95[0]===mc.monteCarlo.shortest95[0];
out.differs=other.monteCarlo.mean!==mc.monteCarlo.mean;
const cor=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:0.5}],samples:100000,seed:9});
out.cor={lin:cor.linear.uc,mc:cor.monteCarlo.std};
const uni=U.run({expression:'x',variables:[v('x',2,1,'uniform')],samples:100000,seed:2});
out.uni={std:uni.monteCarlo.std,min:uni.monteCarlo.min,max:uni.monteCarlo.max,sym:uni.monteCarlo.symmetric95};
out.semidef=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:1}],samples:20000,seed:1}).monteCarlo.std;
out.parsed=U.parseCorrelations('a b 0.5\nb, c, -0.2; ');
const r=U.rng(42),r2=U.rng(42),seq=[r.u32(),r.u32(),r.u32()],seq2=[r2.u32(),r2.u32(),r2.u32()];out.rngSame=seq.join()===seq2.join();
const errs=[
 ['nonPD',()=>U.propagate({expression:'a+b+c',variables:[v('a',0,1),v('b',0,1),v('c',0,1)],correlations:[{a:'a',b:'b',rho:0.9},{a:'b',b:'c',rho:0.9},{a:'a',b:'c',rho:-0.9}]})],
 ['negU',()=>U.propagate({expression:'a+b',variables:[v('a',1,-0.1),v('b',2,0.4)]})],
 ['dup',()=>U.propagate({expression:'a+b',variables:[v('a',1,0.1),v('a',2,0.4)]})],
 ['badName',()=>U.propagate({expression:'a+b',variables:[v('1a',1,0.1)]})],
 ['reserved',()=>U.propagate({expression:'a+b',variables:[v('pi',1,0.1)]})],
 ['rho',()=>U.propagate({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:1.5}]})],
 ['unknownCorr',()=>U.propagate({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],correlations:[{a:'a',b:'z',rho:0.1}]})],
 ['self',()=>U.propagate({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],correlations:[{a:'a',b:'a',rho:0.1}]})],
 ['k',()=>U.propagate({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],k:0})],
 ['empty',()=>U.propagate({expression:'',variables:[v('a',1,0.1)]})],
 ['none',()=>U.propagate({expression:'x',variables:[]})],
 ['seven',()=>U.propagate({expression:'x',variables:'abcdefg'.split('').map(n=>v(n,0,1))})],
 ['N',()=>U.run({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],samples:500})],
 ['Nmax',()=>U.run({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],samples:200001})],
 ['seed',()=>U.run({expression:'a+b',variables:[v('a',1,0.1),v('b',2,0.4)],seed:-1})],
 ['uniformCorr',()=>U.run({expression:'a+b',variables:[v('a',1,0.1,'uniform'),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:0.3}],samples:1000})],
 ['domain',()=>U.run({expression:'log(x)',variables:[v('x',0.1,1)],samples:1000})],
 ['corrLine',()=>U.parseCorrelations('a b')],
];
out.errors={};for(const [name,f] of errs){try{f();out.errors[name]=null;}catch(e){out.errors[name]=e.message;}}
console.log(JSON.stringify(out));
"""


class UncertaintyToolsTests(unittest.TestCase):
    def test_source_is_embedded_and_registered(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-uncertainty-tools">\n'
        self.assertEqual(html.count(marker), 1)
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)].rstrip("\n"), SOURCE.read_text(encoding="utf-8").rstrip("\n"))
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-statistics-tools", "src/statistics-tools.js"),\n    ("promath-uncertainty-tools", "src/uncertainty-tools.js")', build)
        self.assertLess(html.index('<script id="promath-statistics-tools">'), html.index(marker))

    def test_no_dynamic_code_or_network(self):
        src = SOURCE.read_text(encoding="utf-8")
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"<!--", r"-->", r"<script", r"</script", r"Math\.random"):
            self.assertIsNone(re.search(pattern, src, flags=re.IGNORECASE), pattern)
        self.assertEqual(src.count("innerHTML"), 1, "only the static panel template may use innerHTML")
        self.assertIn("M.numerical?.evaluate", src)

    def test_workflow_runs_browser_smoke(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_uncertainty_tools.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_numeric_references(self):
        r = json.loads(subprocess.run(["node", "-e", NODE_SCRIPT, str(SOURCE)], check=True, capture_output=True, text=True, timeout=120).stdout)
        close = lambda a, b, tol: self.assertLessEqual(abs(a - b), tol * max(1.0, abs(b)), (a, b))
        close(r["sum"]["uc"], 0.5, 1e-9)
        close(r["sum"]["value"], 3, 1e-12)
        self.assertEqual(r["sum"]["k"], 2)
        close(r["sum"]["U"], 1.0, 1e-9)
        close(sum(c["percent"] for c in r["sum"]["contributions"]), 100, 1e-9)
        close(r["sum"]["contributions"][0]["percent"], 36, 1e-7)
        close(r["prod"]["uc"], math.sqrt((5 * 0.1) ** 2 + (10 * 0.2) ** 2), 1e-9)
        close(r["prod"]["uc"], 2.0615528128088303, 1e-9)
        close(r["prod"]["U"], 3 * 2.0615528128088303, 1e-9)
        close(r["prod"]["contributions"][0]["sensitivity"], 5, 1e-8)
        close(r["prod"]["contributions"][1]["sensitivity"], 10, 1e-8)
        close(r["rho1"], 0.7, 1e-9)
        close(r["rhoM1"], 0.1, 1e-9)
        close(r["uniform"], 1 / math.sqrt(3), 1e-12)
        self.assertEqual(r["sq"]["lin"], 0)
        close(r["sq"]["mean"], 1, 0.02)
        close(r["sq"]["std"], math.sqrt(2), 0.03)
        self.assertTrue(r["sq"]["flag"])
        self.assertEqual(r["mc"]["n"], 100000)
        self.assertLessEqual(abs(r["mc"]["std"] - 0.5) / 0.5, 0.01, r["mc"])
        self.assertLess(abs(r["mc"]["mean"] - 3), 0.01)
        self.assertFalse(r["mc"]["flag"])
        lo, hi = r["mc"]["sym"]
        close(lo, 3 - 1.959964 * 0.5, 0.005)
        close(hi, 3 + 1.959964 * 0.5, 0.005)
        # The shortest interval of a symmetric output slides along a flat objective, so it is noisier.
        lo, hi = r["mc"]["short"]
        self.assertLess(abs(lo - (3 - 1.959964 * 0.5)), 0.05)
        self.assertLess(abs(hi - (3 + 1.959964 * 0.5)), 0.05)
        self.assertLessEqual(hi - lo, r["mc"]["sym"][1] - r["mc"]["sym"][0])
        self.assertTrue(r["same"] and r["differs"] and r["rngSame"])
        close(r["cor"]["lin"], math.sqrt(0.09 + 0.16 + 2 * 0.5 * 0.12), 1e-9)
        self.assertLessEqual(abs(r["cor"]["mc"] - r["cor"]["lin"]) / r["cor"]["lin"], 0.01)
        self.assertLessEqual(abs(r["uni"]["std"] - 1 / math.sqrt(3)) / (1 / math.sqrt(3)), 0.01)
        self.assertTrue(1 <= r["uni"]["min"] and r["uni"]["max"] <= 3)
        close(r["uni"]["sym"][0], 1.05, 0.01)
        close(r["uni"]["sym"][1], 2.95, 0.01)
        self.assertLessEqual(abs(r["semidef"] - 0.7) / 0.7, 0.02)
        self.assertEqual(r["parsed"], [{"a": "a", "b": "b", "rho": "0.5"}, {"a": "b", "b": "c", "rho": "-0.2"}])
        e = r["errors"]
        self.assertTrue(all(e.values()), e)
        self.assertIn("positive semidefinite", e["nonPD"])
        self.assertIn("non-negative", e["negU"])
        self.assertIn("duplicated", e["dup"])
        self.assertIn("reserved", e["reserved"])
        self.assertIn("[−1, 1]", e["rho"])
        self.assertIn("1000", e["N"])
        self.assertIn("normal inputs", e["uniformCorr"])
        self.assertIn("undefined at Monte Carlo sample", e["domain"])


if __name__ == "__main__":
    unittest.main()
