"""Unit conversion / dimensional analysis: exact NIST references, temperature semantics, strict parser failures."""
from pathlib import Path
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/units-tools.js"

HARNESS = r"""
const fs=require('node:fs'),vm=require('node:vm');
const ctx={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
const U=ctx.window.MathStudio.units;
const cases=JSON.parse(process.argv[2]);
const out=cases.map(([fn,args])=>{try{return {ok:U[fn](...args)}}catch(e){return {error:e.message}}});
out.push({ok:U._collisions()});
process.stdout.write(JSON.stringify(out));
"""


def run(cases):
    proc = subprocess.run(["node", "-e", HARNESS, str(SOURCE), json.dumps(cases)],
                          capture_output=True, text=True, check=True, cwd=ROOT)
    return json.loads(proc.stdout)


class UnitsStaticTests(unittest.TestCase):
    def test_bundle_registration_and_safety(self):
        source = SOURCE.read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        tag = '<script id="promath-units-tools">\n'
        start = html.index(tag) + len(tag)
        self.assertEqual(html[start:html.index("</script>", start)], source.rstrip("\n") + "\n")
        self.assertLess(html.index('<script id="promath-precision-tools">'), html.index(tag))
        self.assertIn('("promath-units-tools", "src/units-tools.js")', (ROOT / "scripts/build.py").read_text(encoding="utf-8"))
        for forbidden in ("eval(", "new Function", "fetch(", "XMLHttpRequest", "<!--", "-->", "</script"):
            self.assertNotIn(forbidden, source)
        self.assertIn("M.units=api", source)
        self.assertIn("python tests/smoke_units_tools.py", (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class UnitsNumericalTests(unittest.TestCase):
    def assertRel(self, actual, expected, tol=1e-12):
        self.assertLessEqual(abs(actual - expected), tol * max(1.0, abs(expected)), (actual, expected))

    def test_reference_conversions(self):
        refs = [
            (1, "mi", "m", 1609.344), (1, "psi", "Pa", 6894.757293168361), (1, "kWh", "J", 3.6e6),
            (100, "degC", "degF", 212), (100, "°C", "K", 373.15), (212, "°F", "K", 373.15),
            (-40, "degC", "degF", -40), (-40, "°F", "℃", -40), (0, "K", "degR", 0), (491.67, "R", "degC", 0),
            (1, "hp", "W", 745.6998715822702), (1, "N·m", "J", 1), (1, "N*m", "J", 1), (1, "kg*m/s^2", "N", 1),
            (1, "W/(m^2*degC)", "W/(m^2*K)", 1), (60, "mph", "m/s", 26.8224), (1, "atm", "Pa", 101325),
            (1, "µm", "m", 1e-6), (1, "μm", "nm", 1000), (1, "um", "mm", 1e-3), (1e6, "mm^3", "L", 1),
            (1, "kN/m^2", "kPa", 1), (1, "ft", "in", 12), (1, "yd", "ft", 3), (1, "lb", "kg", 0.45359237),
            (1, "lbf", "N", 4.4482216152605), (1, "gal", "L", 3.785411784), (1, "BTU", "J", 1055.05585262),
            (1, "eV", "J", 1.602176634e-19), (1, "cal", "J", 4.184), (1, "bar", "Pa", 1e5), (1, "day", "h", 24),
            (1, "h", "min", 60), (180, "deg", "rad", 3.141592653589793), (1, "kΩ", "V/A", 1000),
            (1, "ohm", "Ω", 1), (1, "Wb", "T*m^2", 1), (1, "F", "C/V", 1), (1, "H", "Wb/A", 1), (1, "S", "1/ohm", 1),
            (1, "Hz^(1/2)", "s^(-1/2)", 1), (1, "m²", "m^2", 1), (1, "s⁻¹", "Hz", 1), (1, "dam", "m", 10),
            (1, "Qm", "m", 1e30), (1, "qg", "kg", 1e-33), (1, "ksi", "psi", 1000), (1, "MeV", "J", 1.602176634e-13),
        ]
        results = run([["convert", [v, a, b]] for v, a, b, _ in refs])
        for (v, a, b, expected), r in zip(refs, results):
            with self.subTest(frm=a, to=b):
                self.assertIn("ok", r, r)
                self.assertRel(r["ok"]["value"], expected)

    def test_temperature_semantics(self):
        r = run([["convert", [100, "degC", "degF"]], ["convert", [10, "degC", "degF", {"difference": True}]],
                 ["convert", [1, "W/(m^2*degC)", "W/(m^2*K)"]], ["convert", [300, "K", "K*m/m"]],
                 ["convert", [25, "degC", "K*m/m"]], ["convert", [25, "degC*m/m", "K"]],
                 ["convert", [-300, "degC", "K"]], ["convert", [-273.15, "degC", "K"]], ["convert", [-459.67, "degF", "K"]]])
        self.assertEqual(r[0]["ok"]["mode"], "absolute")
        self.assertEqual(r[1]["ok"]["mode"], "difference")
        self.assertRel(r[1]["ok"]["value"], 18)
        self.assertEqual(r[2]["ok"]["mode"], "difference")
        self.assertRel(r[3]["ok"]["value"], 300)
        self.assertIn("Absolute temperature conversion", r[4]["error"])
        self.assertIn("Absolute temperature conversion", r[5]["error"])
        self.assertIn("below absolute zero", r[6]["error"])
        self.assertLess(abs(r[7]["ok"]["value"]), 1e-12)
        self.assertLess(abs(r[8]["ok"]["value"]), 1e-12)

    def test_simplify_and_dimensions(self):
        r = run([["simplify", ["kg*m/s^2"]], ["simplify", ["kN/m^2"]], ["dimensions", ["W/(m^2*K)"]],
                 ["dimensions", ["rad"]], ["simplify", ["J/s"]], ["dimensions", ["mol/(L*s)"]]])
        self.assertEqual(r[0]["ok"]["si"], "kg·m·s^-2")
        self.assertEqual(r[0]["ok"]["dimension"], "M L T^-2")
        self.assertEqual(r[0]["ok"]["named"], "N")
        self.assertEqual(r[0]["ok"]["vector"], [1, 1, -2, 0, 0, 0, 0])
        self.assertRel(r[1]["ok"]["factor"], 1000)
        self.assertIsNone(r[1]["ok"]["named"])
        self.assertEqual(r[2]["ok"]["text"], "M T^-3 Θ^-1")
        self.assertEqual(r[3]["ok"]["text"], "1 (dimensionless)")
        self.assertEqual(r[4]["ok"]["named"], "W")
        self.assertEqual(r[5]["ok"]["vector"], [-3, 0, -1, 0, 0, 1, 0])

    def test_failures_are_explicit(self):
        bad = [
            (["convert", [1, "m", "s"]], "Dimension mismatch"),
            (["convert", [1, "foo", "m"]], "Unknown unit \"foo\""),
            (["convert", [1, "KG", "kg"]], "Unknown unit"),
            (["convert", [1, "hz", "Hz"]], "case-sensitive"),
            (["convert", [1, "kft", "m"]], "cannot be applied"),
            (["convert", [1, "kg*/m", "N"]], "Expected a unit"),
            (["convert", [1, "kg*", "kg"]], "at the end"),
            (["convert", [1, "(m", "m"]], "Expected \")\""),
            (["convert", [1, "m)", "m"]], "Unexpected"),
            (["convert", [1, "m m", "m^2"]], "join units"),
            (["convert", [1, "m^2^3", "m"]], "Chained"),
            (["convert", [1, "m^1/2", "m"]], "rational exponents"),
            (["convert", [1, "m^(1/0)", "m"]], "denominator"),
            (["convert", [1, "m^99", "m"]], "outside"),
            (["convert", [1, "2*m", "m"]], "Numeric factor"),
            (["convert", [1, "m+s", "m"]], "Unexpected character"),
            (["convert", [1, "ton", "kg"]], "Ambiguous"),
            (["convert", [1, "oz", "kg"]], "Ambiguous"),
            (["convert", [1, "", "m"]], "Enter a unit"),
            (["convert", ["abc", "m", "m"]], "finite decimal"),
            (["convert", ["1e999", "m", "m"]], "finite"),
            (["convert", ["Infinity", "m", "m"]], "finite"),
            (["convert", [1e308, "km", "mm"]], "overflows"),
        ]
        results = run([case for case, _ in bad])
        for (case, needle), r in zip(bad, results):
            with self.subTest(case=case):
                self.assertIn("error", r, r)
                self.assertIn(needle, r["error"])
        mismatch = results[0]["error"]
        self.assertIn("(1, 0, 0, 0, 0, 0, 0)", mismatch)
        self.assertIn("(0, 0, 1, 0, 0, 0, 0)", mismatch)

    def test_no_prefix_collisions_in_registry(self):
        self.assertEqual(run([])[-1]["ok"], [])


if __name__ == "__main__":
    unittest.main()
