"""Statistics module: bundle parity, safety rules, workflow registration and Node numeric references."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "statistics-tools.js"

NODE_SCRIPT = r"""
global.window={};global.document={getElementById:()=>null};
require(process.argv[1]);const S=window.MathStudio.statistics;
const d=(n,p)=>S.distribution(n,p),out={};
const N=d('normal',{}),T=d('t',{nu:10}),C2=d('chisquare',{k:2}),C10=d('chisquare',{k:10}),E=d('exponential',{lambda:2}),B=d('binomial',{n:10,p:0.3}),P=d('poisson',{lambda:4});
Object.assign(out,{phi196:N.cdf(1.96),phiInv:N.quantile(0.975),phiInvTail:N.quantile(1e-10),phiSf:N.sf(5),
 shifted:d('normal',{mu:3,sigma:2}).quantile(0.975),t10:T.cdf(2.228138851986),t10q:T.quantile(0.975),cauchyQ:d('t',{nu:1}).quantile(0.9),
 c2:C2.cdf(3),c2sf:C2.sf(30),c10q:C10.quantile(0.95),eq:E.quantile(0.5),ecdf:E.cdf(1),b3:B.cdf(3),bpmf:B.pdf(3),bq:B.quantile(0.6496107184),bq2:B.quantile(0.65),
 p2:P.pdf(2),pc:P.cdf(2),pq:P.quantile(0.5),erf05:S.erf(0.5),erfc5:S.erfc(5),lg:S.logGamma(101),betaHalf:S.betaI(2,3,0.4),
 desc:S.describe([1,2,3,4,5,6,7,8,9,100]),corr:S.correlate([1,2,3,4],[2,4,6,8.5]),
 cols:S.describeColumns([['1','x'],['','2'],['abc','3'],['4','5'],['7','9']],0,1)});
const bad=[()=>d('normal',{sigma:0}),()=>d('normal',{sigma:-1}),()=>d('t',{nu:0}),()=>d('chisquare',{k:-2}),()=>d('binomial',{n:10,p:1.5}),()=>d('binomial',{n:2.5,p:0.5}),
 ()=>d('poisson',{lambda:0}),()=>d('exponential',{lambda:'abc'}),()=>N.quantile(-0.1),()=>N.quantile(1.1),()=>S.describe([]),()=>d('gamma',{}),()=>S.describeColumns([[''],['x']],0)];
out.badCount=bad.filter(f=>{try{f();return false}catch(e){return !!e.message}}).length;out.badTotal=bad.length;
out.p0=N.quantile(0);out.p1=E.quantile(1);
console.log(JSON.stringify(out));
"""


class StatisticsToolsTests(unittest.TestCase):
    def test_source_is_embedded_and_registered(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-statistics-tools">\n'
        self.assertEqual(html.count(marker), 1)
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)].rstrip("\n"), SOURCE.read_text(encoding="utf-8").rstrip("\n"))
        self.assertIn('("promath-statistics-tools", "src/statistics-tools.js")', (ROOT / "scripts/build.py").read_text(encoding="utf-8"))
        self.assertLess(html.index('<script id="promath-brent-tools">'), html.index(marker))

    def test_no_dynamic_code_or_network(self):
        src = SOURCE.read_text(encoding="utf-8")
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"<!--", r"-->", r"<script", r"</script"):
            self.assertIsNone(re.search(pattern, src, flags=re.IGNORECASE), pattern)
        self.assertEqual(src.count("innerHTML"), 1, "only the static panel template may use innerHTML")

    def test_workflow_runs_browser_smoke(self):
        self.assertIn("run: python tests/smoke_statistics_tools.py", (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_numeric_references(self):
        r = json.loads(subprocess.run(["node", "-e", NODE_SCRIPT, str(SOURCE)], check=True, capture_output=True, text=True, timeout=60).stdout)
        close = lambda a, b, tol: self.assertLessEqual(abs(a - b), tol * max(1.0, abs(b)), (a, b))
        close(r["phi196"], 0.9750021048517795, 1e-14)
        close(r["phiInv"], 1.959963984540054, 1e-12)
        close(r["phiInvTail"], -6.361340902404056, 1e-11)
        self.assertLessEqual(abs(r["phiSf"] - 2.866515718791939e-07) / 2.866515718791939e-07, 1e-12)
        close(r["shifted"], 3 + 2 * 1.959963984540054, 1e-12)
        close(r["t10"], 0.975, 1e-11)
        close(r["t10q"], 2.228138851986, 1e-11)
        close(r["cauchyQ"], 3.0776835371752536, 1e-12)
        close(r["c2"], 1 - 2.718281828459045 ** -1.5, 1e-14)
        self.assertLessEqual(abs(r["c2sf"] - 3.059023205018258e-07) / 3.059023205018258e-07, 1e-12)
        close(r["c10q"], 18.307038053275146, 1e-12)
        close(r["eq"], 0.34657359027997264, 1e-14)
        close(r["ecdf"], 0.8646647167633873, 1e-14)
        close(r["b3"], 0.6496107184, 1e-10)
        close(r["bpmf"], 0.266827932, 1e-9)
        self.assertEqual((r["bq"], r["bq2"]), (3, 4))
        close(r["p2"], 0.14652511110987343, 1e-14)
        close(r["pc"], 13 * 2.718281828459045 ** -4, 1e-14)
        self.assertEqual(r["pq"], 4)
        close(r["erf05"], 0.5204998778130465, 1e-14)
        self.assertLessEqual(abs(r["erfc5"] - 1.5374597944280349e-12) / 1.5374597944280349e-12, 1e-12)
        close(r["lg"], 363.73937555556347, 1e-14)
        close(r["betaHalf"], 0.5248, 1e-13)
        desc = r["desc"]
        self.assertEqual((desc["n"], desc["median"], desc["q1"], desc["q3"], desc["iqr"], desc["min"], desc["max"]), (10, 5.5, 3.25, 7.75, 4.5, 1, 100))
        close(desc["mean"], 14.5, 1e-15)
        close(desc["sampleVariance"], 909.1666666666666, 1e-14)
        close(desc["populationVariance"], 818.25, 1e-14)
        close(desc["skewness"], 3.1188957452390875, 1e-12)
        close(r["corr"]["covariance"], 3.5833333333333335, 1e-14)
        close(r["corr"]["pearson"], 0.99838143945703, 1e-12)
        cols = r["cols"]
        self.assertEqual((cols["first"]["n"], cols["first"]["blank"], cols["first"]["nonNumeric"]), (3, 1, 1))
        self.assertEqual((cols["second"]["n"], cols["second"]["nonNumeric"], cols["pair"]["pairs"]), (4, 1, 2))
        self.assertEqual(r["badCount"], r["badTotal"])
        self.assertIsNone(r["p0"])  # -Infinity serializes as null
        self.assertIsNone(r["p1"])


if __name__ == "__main__":
    unittest.main()
