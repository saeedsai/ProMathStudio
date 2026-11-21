"""Shooting BVP module: bundle parity, registration, safety, reuse and Node numerical reference."""
from pathlib import Path
import json
import math
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/bvp-tools.js"


class BvpToolsModule(unittest.TestCase):
    def setUp(self):
        self.source = SOURCE.read_text(encoding="utf-8")

    def test_bundle_parity_and_order(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-bvp-tools">\n'
        self.assertEqual(html.count(marker), 1)
        embedded = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(self.source.rstrip("\n"), embedded)
        stiff = html.index('<script id="promath-stiff-ode">')
        self.assertLess(stiff, html.index(marker))
        # Immediately after the stiff ODE script.
        self.assertTrue(html[stiff:].split("</script>\n", 1)[1].startswith(marker))
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-stiff-ode", "src/stiff-ode.js"),\n    ("promath-bvp-tools", "src/bvp-tools.js"),', build)

    def test_registration_and_ui_contract(self):
        self.assertIn("M.bvp={shoot,run}", self.source)
        for token in ("area.id='bvp-details'", 'role="status" aria-live="polite"', "bvp-run", "bvp-to-table",
                      "anchor.after(area)", "M.dataTables.importData({headers:last.columns,rows:s.rows}",
                      "min-height:40px", "Recovery:"):
            self.assertIn(token, self.source)

    def test_reuses_existing_integrators(self):
        self.assertIn("M.odeTools.solveSystem(", self.source)
        self.assertIn("M.stiffOde.solve(", self.source)
        for forbidden in (r"\bk[1-4]\s*=", "GAMMA", r"M\.numerical\.evaluate"):
            self.assertIsNone(re.search(forbidden, self.source), forbidden)

    def test_no_dynamic_code_network_or_html_delimiters(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", "XMLHttpRequest",
                        "WebSocket", "<!--", "-->", "<script", "</script", "importScripts"):
            self.assertIsNone(re.search(pattern, self.source, flags=re.IGNORECASE), pattern)
        self.assertEqual(self.source.count(".innerHTML"), 1)  # static template only
        self.assertIn("output.textContent=describe(last)", self.source)

    @unittest.skipUnless(shutil.which("node"), "node is required")
    def test_node_syntax(self):
        result = subprocess.run(["node", "--check", str(SOURCE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "node is required")
    def test_node_numerical_reference(self):
        script = r"""
const fs=require('fs');
const bvp=fs.readFileSync(process.argv[1],'utf8'), ode=fs.readFileSync(process.argv[2],'utf8');
const odeCode=ode.slice(ode.indexOf('function finite('),ode.indexOf('function solveAdaptive'))+
 ode.slice(ode.indexOf('function solveSystem'),ode.indexOf('const area='));
const fns={'z':e=>e.z,'-y':e=>-e.y,'6*t':e=>6*e.t,'y':e=>e.y,'-exp(y)':e=>-Math.exp(e.y),
 'bad':()=>{throw Error('Unknown symbol q');}};
const N={numerical:{evaluate:(x,env)=>{if(!(x in fns))throw Error('no mock '+x);return fns[x](env);}}};
const solveSystem=(new Function('M','const MAX=1e12;'+odeCode+';return solveSystem;'))(N);
const M={odeTools:{solveSystem},dataTables:{}};
const shoot=(new Function('M','const MAX=1e12;'+bvp.slice(bvp.indexOf('function finite('),bvp.indexOf('const area='))+';return shoot;'))(M);
const D=v=>({type:'dirichlet',value:v});
const out={};
const pick=r=>({status:r.status,sol:r.solutions.map(s=>({s:s.parameter,y0:s.y0,z0:s.slope0,res:s.residual,
 est:s.estimate,mid:s.rows[Math.floor(s.rows.length/2)],end:s.rows.at(-1)})),param:r.parameter});
out.sin=pick(shoot({expression:'-y',a:0,b:Math.PI/2,left:D(0),right:D(1),sMin:-5,sMax:5}));
out.cubic=pick(shoot({expression:'6*x',a:0,b:1,left:D(0),right:D(1),sMin:-5,sMax:5}));
out.neumann=pick(shoot({expression:'y',a:0,b:1,left:D(0),right:{type:'neumann',value:Math.cosh(1)},sMin:-5,sMax:5}));
out.robin=pick(shoot({expression:'y',a:0,b:1,left:{type:'robin',c0:1,c1:1,value:1},right:D(Math.sinh(1)),sMin:-5,sMax:5}));
out.family=pick(shoot({expression:'-y',a:0,b:Math.PI,left:D(0),right:D(0),sMin:-5,sMax:5}));
out.none=pick(shoot({expression:'-y',a:0,b:Math.PI,left:D(0),right:D(1),sMin:-5,sMax:5}));
out.bratu=pick(shoot({expression:'-exp(y)',a:0,b:1,left:D(0),right:D(0),sMin:0,sMax:15}));
out.errors=[];
for(const o of [{a:1,b:1},{a:2,b:1},{left:{type:'cauchy',value:0}},{right:{type:'robin',c0:0,c1:0,value:1}},
 {expression:'bad'},{expression:''},{sMin:3,sMax:3},{steps:5},{scanCount:1},{method:'euler'},{method:'tr-bdf2'},
 {left:{type:'dirichlet',value:'abc'}}]){
 try{shoot(Object.assign({expression:'-y'},o));out.errors.push(null);}catch(e){out.errors.push(e.message);}
}
console.log(JSON.stringify(out));
"""
        result = subprocess.run(["node", "-e", script, str(SOURCE), str(ROOT / "src/ode-tools.js")],
                                capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        sin = out["sin"]
        self.assertEqual(sin["status"], "unique-in-scan")
        self.assertEqual(sin["param"], "y′(a)")
        self.assertAlmostEqual(sin["sol"][0]["z0"], 1.0, delta=1e-8)
        mid = sin["sol"][0]["mid"]
        self.assertAlmostEqual(mid[1], math.sin(mid[0]), delta=1e-8)
        self.assertLess(sin["sol"][0]["est"]["solutionDifference"], 1e-8)
        cubic = out["cubic"]["sol"]
        self.assertEqual(len(cubic), 1)
        self.assertAlmostEqual(cubic[0]["z0"], 0.0, delta=1e-10)
        self.assertAlmostEqual(cubic[0]["mid"][1], 0.125, delta=1e-10)
        for key in ("neumann", "robin"):
            sol = out[key]["sol"]
            self.assertEqual(len(sol), 1, key)
            self.assertAlmostEqual(sol[0]["y0"], 0.0, delta=1e-8)
            self.assertAlmostEqual(sol[0]["z0"], 1.0, delta=1e-8)
            self.assertAlmostEqual(sol[0]["mid"][1], math.sinh(0.5), delta=1e-8)
        self.assertEqual(out["robin"]["param"], "y(a)")
        self.assertAlmostEqual(out["neumann"]["sol"][0]["end"][2], math.cosh(1), delta=1e-10)
        self.assertEqual(out["family"]["status"], "non-unique")
        self.assertEqual(out["family"]["sol"], [])
        self.assertEqual(out["none"]["status"], "none-found")
        bratu = out["bratu"]
        self.assertEqual(bratu["status"], "multiple")
        slopes = sorted(s["z0"] for s in bratu["sol"])
        self.assertEqual(len(slopes), 2)
        self.assertAlmostEqual(slopes[0], 0.549353, delta=1e-4)
        self.assertAlmostEqual(slopes[1], 10.8469, delta=1e-3)
        for s in bratu["sol"]:
            self.assertLess(abs(s["res"]), 1e-9)
            self.assertIsNotNone(s["est"])
        errors = out["errors"]
        expected = ["greater than left", "greater than left", "boundary type", "c₀ or c₁", "every probe",
                    "f(x, y, yp)", "Scan maximum", "RK4 steps", "Scan intervals", "Integrator",
                    "TR-BDF2 solver is not available", "Left boundary value"]
        for message, word in zip(errors, expected):
            self.assertIsNotNone(message, word)
            self.assertIn(word, message)


if __name__ == "__main__":
    unittest.main()
