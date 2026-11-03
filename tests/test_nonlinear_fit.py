"""Nonlinear least-squares (Levenberg–Marquardt) module: bundle parity, safety rules, workflow registration and Node numeric references."""
import json
import math
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "nonlinear-fit.js"
STATS = ROOT / "src" / "statistics-tools.js"

# NIST StRD Misra1a (lower difficulty): y = b1*(1-exp(-b2*x)).
MISRA_X = [77.6, 114.9, 141.1, 190.8, 239.9, 289.0, 332.8, 378.4, 434.8, 477.3, 536.8, 593.1, 689.1, 760.0]
MISRA_Y = [10.07, 14.73, 17.94, 23.93, 29.61, 35.18, 40.02, 44.82, 50.76, 55.05, 61.01, 66.40, 75.47, 81.78]
MISRA_B = (2.3894212918e02, 5.5015643181e-04)
MISRA_SE = (2.7070075241e00, 7.2668688436e-06)
MISRA_SSR = 1.2455138894e-01

LIN_X = [0.5, 1.0, 2.0, 2.5, 3.5, 4.0, 5.5, 7.0]
LIN_Y = [1.9, 2.4, 4.2, 4.8, 6.9, 7.4, 10.6, 13.1]
LIN_W = [1.0, 2.0, 0.5, 1.0, 3.0, 1.0, 0.25, 2.0]

# The Node harness stubs the shared evaluator with fixed JavaScript models (test-only; the module itself
# always evaluates through MathStudio.numerical.evaluate). The real Student t quantile module is loaded.
NODE_SCRIPT = r"""
const models={'a*exp(-b*x)+c':e=>e.a*Math.exp(-e.b*e.x)+e.c,'b1*(1-exp(-b2*x))':e=>e.b1*(1-Math.exp(-e.b2*e.x)),'a+b*x':e=>e.a+e.b*e.x,'a*b*x':e=>e.a*e.b*e.x,'a+0*z':e=>e.a+0*e.z};
global.window={MathStudio:{numerical:{evaluate:(expr,vars)=>{const f=models[expr];if(!f)throw Error('Unknown function or symbol in '+expr);return f(vars);}}}};
global.document={getElementById:()=>null};
require(process.argv[1]);require(process.argv[2]);
const N=window.MathStudio.nonlinearFit,D=JSON.parse(process.argv[3]),out={};
const P=(name,initial,lower,upper)=>({name,initial,lower,upper});
const xs=[0,0.5,1,1.5,2,3,4,5,6,8];
const exact=N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',1),P('c',0)],x:xs,y:xs.map(x=>2*Math.exp(-0.5*x)+1)});
out.exact={values:exact.parameters.map(p=>p.value),converged:exact.converged,ssr:exact.ssr,r2:exact.rSquared};
const pick=r=>({values:r.parameters.map(p=>p.value),se:r.parameters.map(p=>p.standardError),ci:r.parameters.map(p=>p.ci),ssr:r.ssr,r2:r.rSquared,rmse:r.rmse,s2:r.s2,
 tq:r.tQuantile,dof:r.dof,converged:r.converged,identifiable:r.identifiable,warnings:r.warnings,residuals:r.residuals,atBound:r.parameters.map(p=>p.atBound),status:r.status});
out.lin=pick(N.fit({expression:'a+b*x',parameters:[P('a',0),P('b',0)],x:D.lx,y:D.ly}));
out.wls=pick(N.fit({expression:'a+b*x',parameters:[P('a',5),P('b',-1)],x:D.lx,y:D.ly,weights:D.lw}));
out.misra=pick(N.fit({expression:'b1*(1-exp(-b2*x))',parameters:[P('b1',500),P('b2',1e-4)],x:D.mx,y:D.my}));
out.nonid=pick(N.fit({expression:'a*b*x',parameters:[P('a',1),P('b',1)],x:[1,2,3,4],y:[2,4.1,5.9,8]}));
out.zero=pick(N.fit({expression:'a+0*z',parameters:[P('a',0),P('z',1)],x:[1,2,3,4],y:[1,2,3,4]}));
const noisy=xs.map((x,i)=>2*Math.exp(-0.5*x)+1+0.01*Math.sin(3*i));
out.bounded=pick(N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1,0,10),P('b',0.1,'0','0.4'),P('c',0,'-inf','inf')],x:xs,y:noisy}));
out.projected=pick(N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',5,0,1),P('c',0)],x:xs,y:noisy}));
out.budget=pick(N.fit({expression:'b1*(1-exp(-b2*x))',parameters:[P('b1',500),P('b2',1e-4)],x:D.mx,y:D.my,maxIterations:1}));
window.MathStudio.dataTables={tables:[{id:'t1',name:'Sheet',columns:['x','y','w'],rows:D.lx.map((x,i)=>[String(x),String(D.ly[i]),String(D.lw[i])]).concat([['text','1','1'],['','','']])}],calculate:t=>t.rows};
const tab=N.fitTable({expression:'a+b*x',parameters:[P('a',0),P('b',0)],table:'Sheet',xColumn:'x',yColumn:'y',weightColumn:'w'});
out.table={values:tab.parameters.map(p=>p.value),skipped:tab.source.skipped,n:tab.n,weighted:tab.weighted};
out.parsed=N.parseParameters('a 1\nb 2 0 inf; c -1');
out.list=N.parseList('1, 2;3\n4.5');
out.curveLen=N.curve(exact,50).length;
const errs=[
 ['nLeP',()=>N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',1),P('c',0)],x:[0,1,2],y:[3,2,1]})],
 ['badExpr',()=>N.fit({expression:'a*exp(-b*x',parameters:[P('a',1),P('b',1)],x:xs,y:xs})],
 ['unknownParam',()=>N.fit({expression:'a*exp(-b*x)+c',parameters:[P('a',1),P('b',1)],x:xs,y:xs})],
 ['dup',()=>N.fit({expression:'a+b*x',parameters:[P('a',1),P('a',1)],x:xs,y:xs})],
 ['reservedX',()=>N.fit({expression:'a+b*x',parameters:[P('x',1)],x:xs,y:xs})],
 ['badName',()=>N.fit({expression:'a+b*x',parameters:[P('2a',1)],x:xs,y:xs})],
 ['bounds',()=>N.fit({expression:'a+b*x',parameters:[P('a',1,2,1),P('b',1)],x:xs,y:xs})],
 ['weights',()=>N.fit({expression:'a+b*x',parameters:[P('a',1),P('b',1)],x:xs,y:xs,weights:xs.map(()=>-1)})],
 ['length',()=>N.fit({expression:'a+b*x',parameters:[P('a',1),P('b',1)],x:xs,y:[1,2,3]})],
 ['nonfinite',()=>N.fit({expression:'a+b*x',parameters:[P('a',1),P('b',1)],x:xs,y:xs.map(()=>'abc')})],
 ['seven',()=>N.fit({expression:'a+b*x',parameters:'abcdefg'.split('').map(n=>P(n,1)),x:xs,y:xs})],
 ['empty',()=>N.fit({expression:'',parameters:[P('a',1)],x:xs,y:xs})],
 ['budget',()=>N.fit({expression:'a+b*x',parameters:[P('a',1),P('b',1)],x:xs,y:xs,maxIterations:0})],
 ['paramLine',()=>N.parseParameters('a 1 0')],
 ['listValue',()=>N.parseList('1 two 3')],
 ['table',()=>N.fitTable({expression:'a+b*x',parameters:[P('a',1)],table:'missing',xColumn:'x',yColumn:'y'})],
];
out.errors={};for(const [name,f] of errs){try{f();out.errors[name]=null;}catch(e){out.errors[name]=e.message;}}
console.log(JSON.stringify(out));
"""


def ols(x, y, w=None):
    """Closed-form (weighted) straight-line least squares with standard errors."""
    w = w or [1.0] * len(x)
    sw = sum(w)
    xb = sum(wi * xi for wi, xi in zip(w, x)) / sw
    yb = sum(wi * yi for wi, yi in zip(w, y)) / sw
    sxx = sum(wi * (xi - xb) ** 2 for wi, xi in zip(w, x))
    sxy = sum(wi * (xi - xb) * (yi - yb) for wi, xi, yi in zip(w, x, y))
    b = sxy / sxx
    a = yb - b * xb
    ssr = sum(wi * (yi - a - b * xi) ** 2 for wi, xi, yi in zip(w, x, y))
    s2 = ssr / (len(x) - 2)
    se_b = math.sqrt(s2 / sxx)
    se_a = math.sqrt(s2 * (1 / sw + xb * xb / sxx))
    sst = sum(wi * (yi - yb) ** 2 for wi, yi in zip(w, y))
    return a, b, se_a, se_b, ssr, 1 - ssr / sst


class NonlinearFitTests(unittest.TestCase):
    def test_source_is_embedded_and_registered(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-nonlinear-fit">\n'
        self.assertEqual(html.count(marker), 1)
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)].rstrip("\n"), SOURCE.read_text(encoding="utf-8").rstrip("\n"))
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-uncertainty-tools", "src/uncertainty-tools.js"),\n    ("promath-nonlinear-fit", "src/nonlinear-fit.js")', build)
        uncertainty = html.index('<script id="promath-uncertainty-tools">')
        self.assertEqual(html.index("</script>\n", uncertainty) + len("</script>\n"), html.index(marker))
        self.assertLess(html.index('<script id="promath-statistics-tools">'), html.index(marker))

    def test_no_dynamic_code_or_network(self):
        src = SOURCE.read_text(encoding="utf-8")
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"<!--", r"-->", r"<script", r"</script", r"Math\.random", r"localStorage"):
            self.assertIsNone(re.search(pattern, src, flags=re.IGNORECASE), pattern)
        self.assertEqual(src.count("innerHTML"), 1, "only the static panel template may use innerHTML")
        self.assertIn("M.numerical?.evaluate", src)
        self.assertIn("S.distribution('t'", src)
        self.assertIn("global optimum is not guaranteed", src)

    def test_workflow_runs_browser_smoke(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_nonlinear_fit.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_numeric_references(self):
        data = json.dumps({"mx": MISRA_X, "my": MISRA_Y, "lx": LIN_X, "ly": LIN_Y, "lw": LIN_W})
        r = json.loads(subprocess.run(["node", "-e", NODE_SCRIPT, str(STATS), str(SOURCE), data], check=True, capture_output=True, text=True, timeout=120).stdout)
        rel = lambda a, b, tol: self.assertLessEqual(abs(a - b), tol * abs(b), (a, b))

        # Exact exponential data recovers (2, 0.5, 1).
        self.assertTrue(r["exact"]["converged"])
        for got, want in zip(r["exact"]["values"], (2, 0.5, 1)):
            self.assertLess(abs(got - want), 1e-8, r["exact"])
        self.assertLess(r["exact"]["ssr"], 1e-20)

        # Linear model equals closed-form OLS and WLS, including standard errors and t intervals.
        for key, w in (("lin", None), ("wls", LIN_W)):
            a, b, se_a, se_b, ssr, r2 = ols(LIN_X, LIN_Y, w)
            got = r[key]
            self.assertTrue(got["converged"] and got["identifiable"], got)
            rel(got["values"][0], a, 1e-8)
            rel(got["values"][1], b, 1e-8)
            rel(got["se"][0], se_a, 1e-6)
            rel(got["se"][1], se_b, 1e-6)
            rel(got["ssr"], ssr, 1e-8)
            rel(got["r2"], r2, 1e-10)
            self.assertEqual(got["dof"], 6)
            rel(got["tq"], 2.4469118511449692, 1e-8)  # t_{0.975, 6}
            rel(got["ci"][1][1], b + 2.4469118511449692 * se_b, 1e-6)
            self.assertEqual(got["warnings"], [])
        lin = r["lin"]
        resid = [yi - lin["values"][0] - lin["values"][1] * xi for xi, yi in zip(LIN_X, LIN_Y)]
        for g, want in zip(lin["residuals"], resid):
            self.assertLess(abs(g - want), 1e-9)
        rel(lin["rmse"], math.sqrt(sum(v * v for v in resid) / len(resid)), 1e-8)

        # NIST StRD Misra1a from start 1 (500, 1e-4).
        m = r["misra"]
        self.assertTrue(m["converged"], m)
        for got, want in zip(m["values"], MISRA_B):
            rel(got, want, 1e-6)
        for got, want in zip(m["se"], MISRA_SE):
            rel(got, want, 1e-6)
        rel(m["ssr"], MISRA_SSR, 1e-6)

        # Non-identifiable a*b*x and a parameter the model ignores both warn.
        self.assertFalse(r["nonid"]["identifiable"])
        self.assertTrue(any("not identifiable" in w for w in r["nonid"]["warnings"]), r["nonid"])
        self.assertLess(abs(r["nonid"]["values"][0] * r["nonid"]["values"][1] - 1.99666666666), 1e-6)
        self.assertFalse(r["zero"]["identifiable"])
        self.assertTrue(any("does not depend on z" in w for w in r["zero"]["warnings"]), r["zero"])

        # Bounds are respected and flagged; out-of-bounds initial guesses are projected.
        bnd = r["bounded"]
        self.assertTrue(0 <= bnd["values"][1] <= 0.4 and 0 <= bnd["values"][0] <= 10, bnd)
        self.assertEqual(bnd["values"][1], 0.4)
        self.assertEqual(bnd["atBound"], [False, True, False])
        self.assertTrue(any("finished on a bound" in w for w in bnd["warnings"]))
        self.assertTrue(any("projected" in w for w in r["projected"]["warnings"]))
        self.assertTrue(0 <= r["projected"]["values"][1] <= 1)

        # Iteration budget is reported honestly.
        self.assertFalse(r["budget"]["converged"])
        self.assertEqual(r["budget"]["status"], "iteration-limit")
        self.assertTrue(any("not a converged fit" in w for w in r["budget"]["warnings"]))

        # Data Tables source with weights skips non-numeric rows.
        self.assertEqual(r["table"]["n"], 8)
        self.assertEqual(r["table"]["skipped"], 1)
        self.assertTrue(r["table"]["weighted"])
        rel(r["table"]["values"][1], ols(LIN_X, LIN_Y, LIN_W)[1], 1e-8)
        self.assertEqual(r["parsed"], [{"name": "a", "initial": "1"}, {"name": "b", "initial": "2", "lower": "0", "upper": "inf"}, {"name": "c", "initial": "-1"}])
        self.assertEqual(r["list"], [1, 2, 3, 4.5])
        self.assertEqual(r["curveLen"], 50)

        e = r["errors"]
        self.assertTrue(all(e.values()), e)
        self.assertIn("n > p", e["nLeP"])
        self.assertIn("Initial guess is invalid", e["badExpr"])
        self.assertIn("Initial guess is invalid", e["unknownParam"])
        self.assertIn("duplicated", e["dup"])
        self.assertIn("reserved", e["reservedX"])
        self.assertIn("less than its upper bound", e["bounds"])
        self.assertIn("positive", e["weights"])
        self.assertIn("same number", e["length"])
        self.assertIn("must be finite", e["nonfinite"])
        self.assertIn("1 to 6", e["seven"])
        self.assertIn("1 to 5000", e["budget"])
        self.assertIn("name initial [lower upper]", e["paramLine"])
        self.assertIn("not a number", e["listValue"])
        self.assertIn("existing data table", e["table"])


if __name__ == "__main__":
    unittest.main()
