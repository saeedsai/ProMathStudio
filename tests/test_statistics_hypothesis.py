"""Hypothesis tests and confidence intervals: Node numeric references, independent cross-checks, failure paths, safety and workflow registration."""
import json
import math
import re
import shutil
import subprocess
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "statistics-tools.js"

try:
    import mpmath
except ImportError:  # pragma: no cover - optional independent cross-check
    mpmath = None

NODE_SCRIPT = r"""
global.window={};global.document={getElementById:()=>null};
require(process.argv[1]);const S=window.MathStudio.statistics,out={};
const x=[5.1,4.9,5.6,5.8,6.0,5.2];
Object.assign(out,{
 t1:S.ttestOne(x,{mu:5}),t1g:S.ttestOne(x,{mu:5,alternative:'greater'}),t1l:S.ttestOne(x,{mu:5,alternative:'less',confidence:0.9}),
 welch:S.ttestTwo([1,2,3,4,5],[2,4,6,8,10]),pooled:S.ttestTwo([1,2,3,4,5],[2,4,6,8,10],{equalVariance:true}),
 paired:S.ttestPaired([1,2,3,4,5.5],[2,4,6,8,10]),
 ind0:S.chisqIndependence([[10,20],[20,40]]),ind23:S.chisqIndependence([[12,5,7],[3,9,11]]),indY:S.chisqIndependence([[3,1],[2,4]],{yates:true}),
 gofU:S.chisqGof([16,18,16,14,12,12]),gofE:S.chisqGof([16,18,16,14,12,12],[16,16,16,16,16,8]),gofP:S.chisqGof([16,18,16,14,12,12],[2,2,2,2,2,1]),
 prop:S.propZTest(81,263,{p0:0.25}),wilson:S.wilson(81,263),wilsonG:S.wilson(81,263,{alternative:'greater'}),
 b7:S.binomTest(7,20,{p:0.5}),b3:S.binomTest(3,30,{p:0.25}),b3l:S.binomTest(3,30,{p:0.25,alternative:'less'}),b25:S.binomTest(25,30,{p:0.75}),
 b10:S.binomTest(10,20,{p:0.5}),b0:S.binomTest(0,12,{p:0.3}),
 v:S.varianceTest(x,{sigma2:0.1}),vci:S.varianceTest(x),
 list:S.parseList(' 1, 2;3\t4.5e1 '),matrix:S.parseMatrix('1,2;3 4\n5,6'),
 dispatch:S.hypothesisTest('binom',{k:7,n:20,p0:0.5}).pValue});
const bad=[()=>S.ttestOne([1]),()=>S.ttestOne([2,2,2]),()=>S.ttestOne([1,2],{alternative:'up'}),()=>S.ttestOne([1,2,3],{confidence:1}),
 ()=>S.ttestTwo([1],[1,2]),()=>S.ttestTwo([3,3],[4,4]),()=>S.ttestPaired([1,2,3],[1,2]),()=>S.ttestOne([1,'abc',3]),
 ()=>S.chisqGof([3,-1,4]),()=>S.chisqGof([3,1],[0,1]),()=>S.chisqGof([5]),()=>S.chisqGof([1,2],[1,2,3]),()=>S.chisqGof([0,0]),
 ()=>S.chisqIndependence([[1,2]]),()=>S.chisqIndependence([[0,0],[3,4]]),()=>S.chisqIndependence([[1,2],[3]]),()=>S.chisqIndependence([[1,-2],[3,4]]),
 ()=>S.chisqIndependence(Array.from({length:11},()=>[1,2])),()=>S.chisqIndependence([[1,2,3,4,5,6,7,8,9,10,11],[1,2,3,4,5,6,7,8,9,10,11]]),
 ()=>S.binomTest(3,10,{p:0}),()=>S.binomTest(3,10,{p:1}),()=>S.binomTest(11,10),()=>S.binomTest(2.5,10),()=>S.propZTest(3,10,{p0:1.2}),()=>S.propZTest(3,0),
 ()=>S.varianceTest([4,4,4]),()=>S.varianceTest([1,2,3],{sigma2:0}),()=>S.parseList('1, 2+3'),()=>S.hypothesisTest('anova',{})];
out.bad=bad.map((f,i)=>{try{f();return 'no error '+i}catch(e){return e.message?'':'blank '+i}}).filter(Boolean);out.badTotal=bad.length;
console.log(JSON.stringify(out));
"""


def binom_two_sided(k, n, p):
    """Independent exact two-sided binomial p-value with rational arithmetic (scipy's minlike rule)."""
    p = Fraction(p).limit_denominator(10**9)
    pmf = [math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(n + 1)]
    d = pmf[k] * Fraction(1 + 10**-7)
    return float(min(1, sum(v for v in pmf if v <= d)))


class StatisticsHypothesisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not shutil.which("node"):
            raise unittest.SkipTest("Node.js required")
        cls.r = json.loads(subprocess.run(["node", "-e", NODE_SCRIPT, str(SOURCE)], check=True, capture_output=True, text=True, timeout=60).stdout)

    def close(self, a, b, tol):
        self.assertLessEqual(abs(a - b), tol * max(1.0, abs(b)), (a, b))

    def test_t_tests_match_scipy(self):
        r = self.r
        t1 = r["t1"]
        self.close(t1["statistic"], 2.456769074559979, 1e-12)
        self.assertEqual(t1["df"], 5)
        self.close(t1["pValue"], 0.057456265269132285, 1e-8)
        self.close(t1["ci"][0], 4.97992531587776, 1e-10)
        self.close(t1["ci"][1], 5.886741350788907, 1e-10)
        self.close(t1["effectSize"]["value"], 1.0029717747535982, 1e-12)
        self.close(r["t1g"]["pValue"], 0.028728132634566143, 1e-8)
        self.close(r["t1g"]["ci"][0], 5.077912208293039, 1e-10)
        self.assertIsNone(r["t1g"]["ci"][1])  # JSON encodes +Infinity as null
        self.close(r["t1l"]["pValue"], 1 - 0.028728132634566143, 1e-8)
        w = r["welch"]
        self.close(w["statistic"], -1.8973665961010275, 1e-12)
        self.close(w["df"], 5.882352941176471, 1e-12)
        self.close(w["pValue"], 0.10753119493062728, 1e-8)
        self.close(w["ci"][0], -6.887741643736975, 1e-10)
        self.close(w["ci"][1], 0.887741643736975, 1e-10)
        p = r["pooled"]
        self.assertEqual(p["df"], 8)
        self.close(p["pValue"], 0.09434977284243762, 1e-8)
        self.close(p["ci"][0], -6.646112680506018, 1e-10)
        pr = r["paired"]
        self.close(pr["statistic"], -4.529039094769575, 1e-12)
        self.close(pr["pValue"], 0.01058509303675222, 1e-8)
        self.close(pr["ci"][1], -1.1222077053006212, 1e-10)
        for key in ("t1", "welch", "pooled", "paired"):
            self.assertIn("Assumes", r[key]["assumptions"])

    def test_chi_square_tests_match_scipy(self):
        r = self.r
        self.assertEqual((r["ind0"]["statistic"], r["ind0"]["pValue"], r["ind0"]["df"]), (0, 1, 1))
        self.close(r["ind23"]["statistic"], 7.413825626869104, 1e-12)
        self.close(r["ind23"]["pValue"], 0.024553206717000394, 1e-8)
        self.close(r["ind23"]["expected"][0][0], 7.65957447, 1e-8)
        self.assertEqual(r["ind23"]["warnings"], [])
        self.assertIn("Yates", r["indY"]["test"])
        self.assertTrue(r["indY"]["warnings"] and "below 5" in r["indY"]["warnings"][0])
        # Yates for [[3,1],[2,4]]: E=[[2,2],[3,3]], |O-E|-0.5 = 0.5 everywhere.
        self.close(r["indY"]["statistic"], 0.25 * (1 / 2 + 1 / 2 + 1 / 3 + 1 / 3), 1e-14)
        self.close(r["gofU"]["statistic"], 2.0, 1e-14)
        self.assertEqual(r["gofU"]["df"], 5)
        self.close(r["gofU"]["pValue"], 0.8491450360846096, 1e-8)
        self.close(r["gofE"]["statistic"], 3.5, 1e-14)
        self.close(r["gofE"]["pValue"], 0.6233876277495822, 1e-8)
        self.close(r["gofP"]["statistic"], 3.5, 1e-13)  # proportions rescaled to the observed total

    def test_proportion_and_binomial_match_scipy(self):
        r = self.r
        self.close(r["prop"]["statistic"], 2.1716575062521595, 1e-12)
        self.close(r["prop"]["pValue"], 0.02988150597454649, 1e-8)
        self.close(r["wilson"][0], 0.2552885198782742, 1e-11)
        self.close(r["wilson"][1], 0.36620957698280004, 1e-11)
        self.assertEqual(r["wilsonG"][1], 1)
        self.close(r["b7"]["pValue"], 0.26317596435546875, 1e-8)
        self.close(r["b7"]["ci"][0], 0.15390920478454118, 1e-10)
        self.close(r["b7"]["ci"][1], 0.592188534532828, 1e-10)
        self.close(r["b3"]["pValue"], 0.059042966603656336, 1e-8)
        self.close(r["b3"]["ci"][0], 0.021117137029722566, 1e-10)
        self.close(r["b3l"]["pValue"], 0.03744932572380086, 1e-8)
        self.close(r["b25"]["pValue"], 0.39919143727262696, 1e-8)
        self.assertEqual(r["b10"]["pValue"], 1)
        self.assertEqual(r["b0"]["ci"][0], 0)
        self.close(r["dispatch"], r["b7"]["pValue"], 1e-15)
        # Independent exact rational cross-check of the two-sided rule.
        for key, (k, n, p) in {"b7": (7, 20, 0.5), "b3": (3, 30, 0.25), "b25": (25, 30, 0.75), "b0": (0, 12, 0.3)}.items():
            self.close(r[key]["pValue"], binom_two_sided(k, n, p), 1e-10)

    def test_variance_interval_matches_scipy(self):
        v = self.r["v"]
        self.close(v["estimate"], 0.1866666666666666, 1e-13)
        self.close(v["ci"][0], 0.07273198428237462, 1e-10)
        self.close(v["ci"][1], 1.1228588703402531, 1e-10)
        self.close(v["statistic"], 9.333333333333329, 1e-12)
        self.close(v["pValue"], 0.19296951894239756, 1e-8)
        self.assertIsNone(self.r["vci"]["statistic"])
        self.assertIn("NOT robust", v["assumptions"])

    @unittest.skipUnless(mpmath, "mpmath required for independent cross-check")
    def test_independent_mpmath_cross_check(self):
        mp = mpmath.mp
        mp.dps = 30
        # t survival by direct quadrature of the Student t density (independent of the incomplete beta).
        def t_sf(t, nu):
            c = mpmath.gamma((nu + 1) / 2) / (mpmath.sqrt(nu * mpmath.pi) * mpmath.gamma(nu / 2))
            return c * mpmath.quad(lambda u: (1 + u * u / nu) ** (-(nu + 1) / 2), [t, mpmath.inf])
        xs = [5.1, 4.9, 5.6, 5.8, 6.0, 5.2]
        m = mpmath.fsum(xs) / 6
        s = mpmath.sqrt(mpmath.fsum((v - m) ** 2 for v in xs) / 5)
        t = (m - 5) / (s / mpmath.sqrt(6))
        self.close(self.r["t1"]["statistic"], float(t), 1e-12)
        self.close(self.r["t1"]["pValue"], float(2 * t_sf(t, 5)), 1e-9)
        nu = mpmath.mpf(2.5) ** 2 / (mpmath.mpf(0.5) ** 2 / 4 + mpmath.mpf(2) ** 2 / 4)
        self.close(self.r["welch"]["pValue"], float(2 * t_sf(mpmath.mpf(3) / mpmath.sqrt(2.5), nu)), 1e-9)
        self.close(self.r["gofU"]["pValue"], float(mpmath.gammainc(2.5, 1, mpmath.inf, regularized=True)), 1e-10)
        z = mpmath.sqrt(2) * mpmath.erfinv(mpmath.mpf(0.95))
        ph, n = mpmath.mpf(81) / 263, 263
        centre = (ph + z * z / (2 * n)) / (1 + z * z / n)
        half = z / (1 + z * z / n) * mpmath.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n))
        self.close(self.r["wilson"][0], float(centre - half), 1e-11)
        self.close(self.r["wilson"][1], float(centre + half), 1e-11)

    def test_failure_paths_raise_messages(self):
        self.assertEqual(self.r["bad"], [])
        self.assertGreaterEqual(self.r["badTotal"], 29)

    def test_parsers(self):
        self.assertEqual(self.r["list"], [1, 2, 3, 45])
        self.assertEqual(self.r["matrix"], [[1, 2], [3, 4], [5, 6]])

    def test_safety_and_workflow(self):
        src = SOURCE.read_text(encoding="utf-8")
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"<!--", r"-->", r"<script", r"</script"):
            self.assertIsNone(re.search(pattern, src, flags=re.IGNORECASE), pattern)
        self.assertEqual(src.count("innerHTML"), 1)
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertIn(src.rstrip("\n"), html)
        self.assertIn('id="stats-ht-run"', src)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_statistics_tests.py", workflow)


if __name__ == "__main__":
    unittest.main()
