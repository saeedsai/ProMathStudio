"""Stiff TR-BDF2 module: bundle parity, registration, safety and Node numerical reference."""
from pathlib import Path
import json
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/stiff-ode.js"


class StiffOdeModule(unittest.TestCase):
    def setUp(self):
        self.source = SOURCE.read_text(encoding="utf-8")

    def test_bundle_parity_and_order(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-stiff-ode">\n'
        self.assertEqual(html.count(marker), 1)
        embedded = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(self.source.rstrip("\n"), embedded)
        self.assertLess(html.index('<script id="promath-ode-tools">'), html.index(marker))
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-ode-tools", "src/ode-tools.js"),\n    ("promath-stiff-ode", "src/stiff-ode.js"),', build)

    def test_registration_and_ui_contract(self):
        self.assertIn("M.stiffOde={solve,run", self.source)
        self.assertIn("document.getElementById('ode-details')", self.source)
        self.assertIn("anchor.after(area)", self.source)
        for token in ("area.id='stiff-ode-details'", 'role="status" aria-live="polite"', "stiff-ode-run",
                      "stiff-ode-to-table", "M.dataTables.importData({headers:last.columns,rows:last.rows}",
                      "M.numerical.evaluate(expression,env)", "M.numerical.evaluate(expressionZ,env)"):
            self.assertTrue(token in self.source, token)

    def test_no_dynamic_code_network_or_html_delimiters(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", "XMLHttpRequest",
                        "WebSocket", "<!--", "-->", "<script", "</script", "importScripts"):
            self.assertIsNone(re.search(pattern, self.source, flags=re.IGNORECASE), pattern)
        # The single innerHTML assignment is a static template; user values only reach textContent.
        self.assertEqual(self.source.count(".innerHTML"), 1)
        self.assertNotIn("innerHTML+=", self.source)
        self.assertIn("output.textContent=", self.source)

    def test_does_not_duplicate_explicit_runge_kutta(self):
        self.assertNotIn("function solveAdaptive", self.source)
        self.assertNotIn("k4", self.source)
        self.assertIn("TR-BDF2", self.source)

    def test_node_syntax(self):
        result = subprocess.run(["node", "--check", str(SOURCE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    @unittest.skipUnless(shutil.which("node"), "node is required")
    def test_node_numerical_reference(self):
        script = r"""
const fs=require('fs');
const src=fs.readFileSync(process.argv[1],'utf8');
const code=src.slice(src.indexOf('const GAMMA='),src.indexOf('const area='));
const fns={
 'stiff':(e)=>-1000*(e.y-Math.cos(e.t)),
 'blow':(e)=>e.y*e.y,
 'lin-y':(e)=>-1001*e.y+999*e.z,'lin-z':(e)=>999*e.y-1001*e.z,
 'bad':()=>{throw Error('Unknown symbol');}
};
const M={numerical:{evaluate:(x,env)=>fns[x](env)}};
const solve=(new Function('M','const MAX=1e12;'+code+';return solve;'))(M);
const out={};
const a=1000,t=1,ref=(a*a*Math.cos(t)+a*Math.sin(t))/(a*a+1)-a*a/(a*a+1)*Math.exp(-a*t);
const r=solve({expression:'stiff',t0:0,t1:1,y0:0,rtol:1e-6,atol:1e-9});
out.stiff={rel:Math.abs(r.rows.at(-1)[1]-ref)/Math.abs(ref),acc:r.accepted,t:r.rows.at(-1)[0]};
const s=solve({expression:'lin-y',expressionZ:'lin-z',t0:0,t1:1,y0:2,z0:0,rtol:1e-6,atol:1e-9});
const e=s.rows.at(-1);
out.lin={ey:Math.abs(e[1]-(Math.exp(-2)+Math.exp(-2000))),ez:Math.abs(e[2]-(Math.exp(-2)-Math.exp(-2000))),cols:s.columns};
const errs=[];
for(const o of [{expression:'blow',t0:0,t1:2,y0:1},{expression:'stiff',t0:1,t1:1},
 {expression:'stiff',rtol:0},{expression:'stiff',atol:2},{expression:'bad'},{expression:''},
 {expression:'stiff',maxSteps:10}]){
 try{solve(o);errs.push(null);}catch(err){errs.push(err.message);}
}
out.errs=errs;
console.log(JSON.stringify(out));
"""
        result = subprocess.run(["node", "-e", script, str(SOURCE)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertLess(out["stiff"]["rel"], 1e-4)
        self.assertLess(out["stiff"]["acc"], 500)
        self.assertEqual(out["stiff"]["t"], 1)
        self.assertLess(out["lin"]["ey"], 1e-4)
        self.assertLess(out["lin"]["ez"], 1e-4)
        self.assertEqual(out["lin"]["cols"], ["t", "y", "z"])
        blow, same, rtol, atol, bad, empty, budget = out["errs"]
        self.assertTrue(blow and ("Newton" in blow or "underflow" in blow or "non-finite" in blow), blow)
        self.assertIn("differ", same)
        self.assertIn("Relative tolerance", rtol)
        self.assertIn("Absolute tolerance", atol)
        self.assertIn("initial point", bad)
        self.assertIn("dy/dt", empty)
        self.assertIn("Step budget", budget)


if __name__ == "__main__":
    unittest.main()
