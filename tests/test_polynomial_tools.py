"""Polynomial tools: bundle parity, safety, and Node numerical references (Aberth roots, Horner, algebra, GCD)."""
from pathlib import Path
import cmath
import json
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src/polynomial-tools.js"

HARNESS = r"""
const fs=require('node:fs'),vm=require('node:vm');
const ctx={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),ctx);
const P=ctx.window.MathStudio.polynomials;
const cases=JSON.parse(process.argv[2]);
const out=cases.map(([fn,args])=>{try{return {ok:P[fn](...args)}}catch(e){return {error:e.message}}});
process.stdout.write(JSON.stringify(out));
"""


def run(cases):
    proc = subprocess.run(["node", "-e", HARNESS, str(SOURCE), json.dumps(cases)],
                          capture_output=True, text=True, check=True, cwd=ROOT)
    return json.loads(proc.stdout)


def cx(d):
    return complex(d["re"], d["im"])


def wilkinson(n):
    coefs = [1.0]
    for k in range(1, n + 1):
        nxt = coefs + [0.0]
        for i in range(1, len(nxt)):
            nxt[i] -= k * coefs[i - 1]
        coefs = nxt
    return coefs


class PolynomialStaticTests(unittest.TestCase):
    def test_bundle_registration_and_safety(self):
        source = SOURCE.read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        tag = '<script id="promath-polynomial-tools">\n'
        start = html.index(tag) + len(tag)
        self.assertEqual(html[start:html.index("</script>", start)], source.rstrip("\n") + "\n")
        units_end = html.index("</script>\n", html.index('<script id="promath-units-tools">')) + len("</script>\n")
        self.assertEqual(html.index(tag), units_end)
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-units-tools", "src/units-tools.js"),\n    ("promath-polynomial-tools", "src/polynomial-tools.js"),', build)
        for forbidden in ("eval(", "new Function", "fetch(", "XMLHttpRequest", "<!--", "-->", "<script", "</script"):
            self.assertNotIn(forbidden, source)
        self.assertIn("M.polynomials=api", source)
        self.assertIn("python tests/smoke_polynomial_tools.py", (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    def test_inner_html_is_static_markup_only(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertEqual(source.count("innerHTML"), 1)
        statement = source[source.index("area.innerHTML="):source.index("panel.append(area)")]
        self.assertNotIn(".value", statement)


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class PolynomialNumericalTests(unittest.TestCase):
    def assertRootsMatch(self, got, expected, tol):
        got = sorted(got, key=lambda z: (round(z.real, 6), round(z.imag, 6)))
        expected = sorted(expected, key=lambda z: (round(z.real, 6), round(z.imag, 6)))
        self.assertEqual(len(got), len(expected))
        for g, e in zip(got, expected):
            self.assertLessEqual(abs(g - e), tol, (got, expected))

    def test_reference_roots(self):
        unity = [cmath.exp(2j * cmath.pi * k / 5) for k in range(5)]
        cases = [
            ("1, -3, 2", [1, 2], 1e-13),
            ("1, 0, 1", [1j, -1j], 1e-13),
            ("1,0,0,0,0,-1", unity, 1e-13),
            ("1, 2-i, -2i", [1j, -2], 1e-13),
            (wilkinson(10), list(range(1, 11)), 1e-6),
        ]
        results = run([["roots", [c]] for c, _, _ in cases])
        for (coefs, expected, tol), r in zip(cases, results):
            with self.subTest(coefs=coefs):
                self.assertIn("ok", r, r)
                self.assertTrue(r["ok"]["converged"])
                self.assertRootsMatch([cx(x["root"]) for x in r["ok"]["roots"]], [complex(e) for e in expected], tol)
                self.assertLess(r["ok"]["maxBackwardError"], 1e-14)
                self.assertTrue(all(x["multiplicity"] == 1 for x in r["ok"]["distinct"]))

    def test_multiplicity_clustering(self):
        r = run([["roots", ["1, -3, 3, -1"]], ["roots", ["1, -3, 3, -1", {"clusterTolerance": 1e-9}]],
                 ["roots", ["1, 0, 0"]], ["roots", ["1, -2, 1, 0"]]])
        cube = r[0]["ok"]
        self.assertEqual(len(cube["roots"]), 3)
        self.assertEqual(len(cube["distinct"]), 1)
        self.assertEqual(cube["distinct"][0]["multiplicity"], 3)
        self.assertEqual(cube["clusterTolerance"], 1e-4)
        self.assertLess(abs(cx(cube["distinct"][0]["root"]) - 1), 1e-12)
        self.assertIn("numerical estimates", cube["note"])
        # Individual approximations are only accurate to ~eps^(1/3); a tight tolerance splits the cluster.
        self.assertEqual(len(r[1]["ok"]["distinct"]), 3)
        self.assertEqual(r[2]["ok"]["exactZeroRoots"], 2)
        self.assertEqual(r[2]["ok"]["distinct"][0]["multiplicity"], 2)
        mixed = r[3]["ok"]["distinct"]
        self.assertEqual([d["multiplicity"] for d in mixed], [1, 2])
        self.assertLess(abs(cx(mixed[1]["root"]) - 1), 1e-12)

    def test_backward_error_definition(self):
        r = run([["backwardError", ["1, -3, 2", 1.5]], ["backwardError", ["1, -3, 2", 2]]])
        self.assertAlmostEqual(r[0]["ok"], 0.25 / (2.25 + 4.5 + 2), places=15)
        self.assertEqual(r[1]["ok"], 0)

    def test_evaluation_calculus_and_algebra(self):
        r = run([
            ["evaluate", ["1, -3, 2", "3"]], ["evaluate", ["1, 0, 1", "i"]], ["evaluate", ["2, 0, -1", "1+i"]],
            ["derivative", ["1, -3, 2"]], ["derivative", ["7"]], ["integral", ["3, 2, 1"]], ["integral", ["2", "5"]],
            ["divide", ["1, 0, 0, -1", "1, -1"]], ["divide", ["1, 0, 1", "1, 1"]], ["divide", ["1, 2", "1, 0, 0"]],
            ["add", ["1, 2, 3", "-1, 0"]], ["subtract", ["1, 2", "1, 2"]], ["multiply", ["1, -1", "1, 1"]],
            ["multiply", ["1, -i", "1, 2"]],
            ["gcd", ["1, -3, 2", "1, -4, 3"]], ["gcd", ["1, -3, 2", "1, 1"]],
            ["fromRoots", ["1, 2, i, -i"]], ["fromRoots", ["2-i"]],
        ])
        ok = [x.get("ok") for x in r]
        coef = lambda res: [cx(c) for c in res["coefficients"]]
        self.assertEqual(cx(ok[0]["value"]), 2)
        self.assertEqual(cx(ok[0]["derivative"]), 3)
        self.assertEqual(cx(ok[1]["value"]), 0)
        self.assertEqual(cx(ok[1]["derivative"]), 2j)
        self.assertLess(abs(cx(ok[2]["value"]) - (2 * (1 + 1j) ** 2 - 1)), 1e-15)
        self.assertEqual(coef(ok[3]), [2, -3])
        self.assertEqual(coef(ok[4]), [0])
        self.assertEqual(coef(ok[5]), [1, 1, 1, 0])
        self.assertEqual(coef(ok[6]), [2, 5])
        self.assertEqual([cx(c) for c in ok[7]["quotient"]], [1, 1, 1])
        self.assertEqual([cx(c) for c in ok[7]["remainder"]], [0])
        self.assertEqual([cx(c) for c in ok[8]["quotient"]], [1, -1])
        self.assertEqual([cx(c) for c in ok[8]["remainder"]], [2])
        self.assertEqual([cx(c) for c in ok[9]["quotient"]], [0])
        self.assertEqual([cx(c) for c in ok[9]["remainder"]], [1, 2])
        self.assertEqual(coef(ok[10]), [1, 1, 3])
        self.assertEqual(coef(ok[11]), [0])
        self.assertEqual(coef(ok[12]), [1, 0, -1])
        self.assertEqual(coef(ok[13]), [1, 2 - 1j, -2j])
        g = coef(ok[14])
        self.assertEqual(len(g), 2)
        self.assertLess(abs(g[0] - 1) + abs(g[1] + 1), 1e-12)
        self.assertEqual(ok[14]["degree"], 1)
        self.assertIn("Numerical GCD", ok[14]["note"])
        self.assertEqual(coef(ok[15]), [1])
        self.assertEqual(coef(ok[16]), [1, -3, 3, -3, 2])
        self.assertEqual(coef(ok[17]), [1, -2 + 1j])

    def test_from_roots_round_trip(self):
        roots = ["-2.5", "0.5", "1+2i", "1-2i", "3i", "4"]
        built = run([["fromRoots", [roots]]])[0]["ok"]["coefficients"]
        back = run([["roots", [[[c["re"], c["im"]] for c in built]]]])[0]["ok"]
        self.assertRootsMatch([cx(x["root"]) for x in back["roots"]], [complex(s.replace("i", "j")) for s in roots], 1e-12)

    def test_degree_limit_and_high_degree(self):
        r = run([["roots", [[1] + [0] * 29 + [-1]]]])[0]["ok"]
        self.assertEqual(len(r["roots"]), 30)
        self.assertTrue(r["converged"])
        for x in r["roots"]:
            self.assertLess(abs(abs(cx(x["root"])) - 1), 1e-13)

    def test_invalid_inputs(self):
        bad = [
            (["roots", [""]], "empty"),
            (["roots", ["   "]], "empty"),
            (["roots", ["0, 0, 0"]], "all zero"),
            (["roots", ["1, abc"]], "not a number"),
            (["roots", ["1, , 2"]], "empty"),
            (["roots", ["1, NaN"]], "not a number"),
            (["roots", ["1, Infinity"]], "not a number"),
            (["roots", ["1, 1e999"]], "finite"),
            (["roots", [",".join(["1"] * 32)]], "exceeds the supported maximum degree 30"),
            (["roots", ["1, 2", {"clusterTolerance": "x"}]], "Cluster tolerance"),
            (["evaluate", ["1, 2", "2+"]], "not a number"),
            (["divide", ["1, 2", "0"]], "all zero"),
            (["gcd", ["1, 2", "1, 3", {"tolerance": 0}]], "GCD tolerance"),
            (["fromRoots", [",".join(["1"] * 31)]], "At most 30"),
            (["roots", ["1, x"]], "not a number"),
        ]
        results = run([c for c, _ in bad])
        for (case, needle), r in zip(bad, results):
            with self.subTest(case=case):
                self.assertIn("error", r, r)
                self.assertIn(needle, r["error"])

    def test_formatting(self):
        r = run([["formatPolynomial", [[{"re": 1, "im": 0}, {"re": -3, "im": 0}, {"re": 2, "im": 0}]]],
                 ["formatPolynomial", [[{"re": 1, "im": 0}, {"re": 2, "im": -1}, {"re": 0, "im": -2}]]],
                 ["formatComplex", [{"re": 0, "im": -1}]], ["formatComplex", [{"re": 1, "im": 1e-30}]]])
        self.assertEqual(r[0]["ok"], "x^2 - 3x + 2")
        self.assertEqual(r[1]["ok"], "x^2 + (2 - i)x - 2i")
        self.assertEqual(r[2]["ok"], "-i")
        self.assertEqual(r[3]["ok"], "1")


if __name__ == "__main__":
    unittest.main()
