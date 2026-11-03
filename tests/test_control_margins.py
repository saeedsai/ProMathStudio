"""Stability margins, bandwidth and resonant peak checked against independent Python references."""
from pathlib import Path
import json
import math
import os
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SOURCE = (ROOT / "src/control-theory.js").read_text(encoding="utf-8")
MATCH = re.search(r'<script id="promath-control-theory">([\s\S]*?)</script>', HTML)

RUNNER = r"""
const vm=require('node:vm');
const ctx={};for(const m of ['clearRect','fillRect','beginPath','moveTo','lineTo','stroke','fillText','arc','fill'])ctx[m]=()=>{};
const el={};const document={getElementById(id){return el[id]||(el[id]={value:'',textContent:'',addEventListener(){},getContext(){return ctx},width:900,height:390});}};
const window={};vm.runInNewContext(process.env.CT_SCRIPT,{document,window,Math,Number,Array,Error,console});
const C=window.ProMathControlTheory,cases=JSON.parse(process.env.CT_CASES),out={};
for(const [name,n,d,k] of cases){const r=C.margins(n,d,k);out[name]={...r,text:C.marginText(r)};}
for(const id of ['ct-num','ct-den','ct-gain','ct-mode','ct-output','ct-status','ct-margins-output','ct-margins-status'])document.getElementById(id);
el['ct-num'].value='1';el['ct-den'].value='1, 3, 2, 0';el['ct-gain'].value='1';el['ct-mode'].value='bode';C.analyze();
out.bode={output:el['ct-output'].textContent,margins:el['ct-margins-output'].textContent,status:el['ct-status'].textContent};
el['ct-den'].value='1, nope';C.analyzeMargins();out.invalid={status:el['ct-margins-status'].textContent,output:el['ct-margins-output'].textContent};
el['ct-den'].value='1, 1';el['ct-gain'].value='0';C.analyzeMargins();out.zero={status:el['ct-margins-status'].textContent};
el['ct-gain'].value='1';C.analyzeMargins();out.recovered={status:el['ct-margins-status'].textContent,output:el['ct-margins-output'].textContent};
console.log(JSON.stringify(out));
"""

CASES = [
    ["third", [1], [1, 3, 2, 0], 1],
    ["first", [1], [1, 1], 1],
    ["first2", [1], [1, 1], 2],
    ["type1", [1], [1, 0.2, 0], 1],
    ["second", [1], [1, 0.2, 1], 1],
    ["cubic10", [1], [1, 3, 3, 1], 10],
    ["unstable_plant", [1], [1, -1], 2],
]


def poly(c, s):
    v = 0
    for x in c:
        v = v * s + x
    return v


def bisect(f, a, b, it=200):
    fa = f(a)
    for _ in range(it):
        m = (a + b) / 2
        fm = f(m)
        if (fm < 0) == (fa < 0):
            a, fa = m, fm
        else:
            b = m
    return (a + b) / 2


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class ControlMargins(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        assert MATCH, "control-theory script must be bundled"
        env = {**os.environ, "CT_SCRIPT": MATCH.group(1), "CT_CASES": json.dumps(CASES)}
        p = subprocess.run(["node", "-e", RUNNER], capture_output=True, text=True, env=env, cwd=ROOT)
        assert p.returncode == 0, p.stdout + p.stderr
        cls.r = json.loads(p.stdout)

    def test_bundle_matches_source(self):
        self.assertEqual(MATCH.group(1).strip("\n"), SOURCE.strip("\n"))
        for bad in ("eval(", "new Function", "innerHTML", "fetch("):
            self.assertNotIn(bad, SOURCE)

    def test_third_order_reference(self):
        # G = 1/(s(s+1)(s+2)): phase -90-atan(w)-atan(w/2) = -180 at w = sqrt(2); |G| = 1/6 there.
        r = self.r["third"]
        self.assertAlmostEqual(r["gm"]["w"], math.sqrt(2), delta=1e-7)
        self.assertAlmostEqual(r["gm"]["gm"], 20 * math.log10(6), delta=1e-6)
        wgc = bisect(lambda w: w * w * (w * w + 1) * (w * w + 4) - 1, 0.1, 1)
        pm = 180 - 90 - math.degrees(math.atan(wgc)) - math.degrees(math.atan(wgc / 2))
        self.assertAlmostEqual(r["pm"]["w"], wgc, delta=1e-7)
        self.assertAlmostEqual(r["pm"]["pm"], pm, delta=1e-6)
        self.assertAlmostEqual(wgc, 0.4457, delta=1e-4)
        self.assertAlmostEqual(pm, 53.41, delta=0.01)
        self.assertTrue(r["closedStable"])
        # Bandwidth: |T(jw)| = 1/sqrt(2) for T = 1/(s^3+3s^2+2s+1), T(0)=1.
        T = lambda w: abs(1 / poly([1, 3, 2, 1], 1j * w))
        bw = bisect(lambda w: T(w) - 1 / math.sqrt(2), 0.5, 1.5)
        self.assertAlmostEqual(r["bandwidth"], bw, delta=1e-7)

    def test_first_order_infinite_gain_margin_and_dc_phase_margin(self):
        r = self.r["first"]
        self.assertIsNone(r["gm"])
        self.assertIn("Gain margin: infinite", r["text"])
        self.assertEqual(r["pm"]["w"], 0)
        self.assertEqual(r["pm"]["pm"], 180)
        self.assertAlmostEqual(r["bandwidth"], 2, delta=1e-8)  # T = 1/(s+2)
        self.assertIsNone(r["peak"])
        r2 = self.r["first2"]  # |2/(jw+1)| = 1 at w = sqrt(3), phase -60 deg.
        self.assertAlmostEqual(r2["pm"]["w"], math.sqrt(3), delta=1e-8)
        self.assertAlmostEqual(r2["pm"]["pm"], 120, delta=1e-6)
        self.assertIsNone(r2["gm"])

    def test_resonant_peak_references(self):
        # G = 1/(s(s+0.2)) closes to T = 1/(s^2+0.2s+1): zeta=0.1, wn=1.
        z = 0.1
        r = self.r["type1"]
        self.assertAlmostEqual(r["peak"]["mr"], 1 / (2 * z * math.sqrt(1 - z * z)), delta=1e-8)
        self.assertAlmostEqual(r["peak"]["w"], math.sqrt(1 - 2 * z * z), delta=1e-6)
        # G = 1/(s^2+0.2s+1) closes to 1/(s^2+0.2s+2): wn=sqrt(2), zeta=0.1/sqrt(2), normalized by T(0)=1/2.
        wn, z = math.sqrt(2), 0.1 / math.sqrt(2)
        r = self.r["second"]
        self.assertAlmostEqual(r["t0"], 0.5, delta=1e-12)
        self.assertAlmostEqual(r["peak"]["mr"], 1 / (2 * z * math.sqrt(1 - z * z)), delta=1e-8)
        self.assertAlmostEqual(r["peak"]["w"], wn * math.sqrt(1 - 2 * z * z), delta=1e-6)
        self.assertIsNone(r["gm"])

    def test_unstable_and_negative_margins(self):
        # 10/(s+1)^3: phase -180 at sqrt(3), |G| = 10/8 -> GM = -1.938 dB; closed loop unstable.
        r = self.r["cubic10"]
        self.assertAlmostEqual(r["gm"]["w"], math.sqrt(3), delta=1e-7)
        self.assertAlmostEqual(r["gm"]["gm"], -20 * math.log10(10 / 8), delta=1e-6)
        wgc = math.sqrt(10 ** (2 / 3) - 1)
        self.assertAlmostEqual(r["pm"]["w"], wgc, delta=1e-7)
        self.assertAlmostEqual(r["pm"]["pm"], 180 - 3 * math.degrees(math.atan(wgc)), delta=1e-6)
        self.assertFalse(r["closedStable"])
        self.assertIn("not shown stable", r["text"])
        # 2/(s-1): unwrapped phase -180+atan(w) (RHP pole), PM 60 at sqrt(3), DC phase crossover GM -6.02 dB.
        r = self.r["unstable_plant"]
        g = 2 / poly([1, -1], 0)  # DC gain -2
        self.assertAlmostEqual(r["pm"]["w"], math.sqrt(3), delta=1e-8)
        self.assertAlmostEqual(r["pm"]["pm"], 60, delta=1e-6)
        self.assertEqual(r["gm"]["w"], 0)
        self.assertAlmostEqual(r["gm"]["gm"], -20 * math.log10(abs(g)), delta=1e-9)
        self.assertTrue(r["closedStable"])

    def test_bode_output_invalid_input_and_recovery(self):
        b = self.r["bode"]
        self.assertIn("Gain margin: 15.563 dB", b["output"])
        self.assertIn("Phase margin: 53.411", b["output"])
        self.assertIn("0.01–1000 rad/s", b["margins"])
        self.assertIn("completed", b["status"])
        self.assertIn("finite coefficients", self.r["invalid"]["status"])
        self.assertEqual(self.r["invalid"]["output"], "No valid margins.")
        self.assertIn("nonzero gain", self.r["zero"]["status"])
        self.assertIn("computed", self.r["recovered"]["status"])
        self.assertIn("Phase margin: 180", self.r["recovered"]["output"])

    def test_markup_catalog_and_workflow(self):
        for item in ('id="ct-frequency"', 'id="ct-margins-run"', 'id="ct-margins-status"', 'id="ct-margins-output"'):
            self.assertIn(item, HTML)
        catalog = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        row = next(x for x in catalog.splitlines() if x.strip().startswith("['control.frequency.response'"))
        self.assertTrue(row.rstrip(",]").endswith("'graph','ct-frequency'"))
        self.assertIn("not a full loop-shaping suite", row)
        self.assertNotIn("not yet implemented", row)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_control_margins.py", workflow)


if __name__ == "__main__":
    unittest.main()
