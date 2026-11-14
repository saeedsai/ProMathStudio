"""Multivariate tools: bundle parity, safety rules, workflow registration and Node numerical references vs numpy."""
import json
import math
import re
import shutil
import subprocess
import unittest
from pathlib import Path

try:
    import numpy as np
except ImportError:  # pragma: no cover - hand-derived references are used instead
    np = None

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "multivariate-tools.js"

SMALL = [[1, 2, 10], [2, 4, 7], [3, 7, 9], [4, 8, 3], [5, 9, 1]]
TIES = [[1, 5], [2, 5], [2, 3], [3, 1], [4, 1]]
IRIS = [[5.1, 3.5, 1.4, 0.2], [4.9, 3.0, 1.4, 0.2], [4.7, 3.2, 1.3, 0.2], [5.0, 3.6, 1.4, 0.2], [5.4, 3.9, 1.7, 0.4],
        [7.0, 3.2, 4.7, 1.4], [6.4, 3.2, 4.5, 1.5], [6.9, 3.1, 4.9, 1.5], [5.5, 2.3, 4.0, 1.3], [6.5, 2.8, 4.6, 1.5],
        [6.3, 3.3, 6.0, 2.5], [5.8, 2.7, 5.1, 1.9], [7.1, 3.0, 5.9, 2.1], [6.3, 2.9, 5.6, 1.8], [6.5, 3.0, 5.8, 2.2]]
BLOBS = [[0.0, 0.1], [0.2, -0.1], [-0.1, 0.0], [0.1, 0.2], [10.0, 10.1], [10.2, 9.9], [9.9, 10.0], [10.1, 10.2]]

NODE_SCRIPT = r"""
const data=JSON.parse(process.argv[2]);
const sheet={id:'s1',name:'Mixed',columns:['a','b','c'],rows:[['1','2','x'],['2','','3'],['3','6','4'],['4','8','5'],['5','10','6']]};
const sparse={id:'s2',name:'Sparse',columns:['p','q'],rows:[['1',''],['2','3'],['','4'],['n/a','5']]};
global.window={MathStudio:{dataTables:{tables:[sheet,sparse],calculate:t=>t.rows}}};
global.document={getElementById:()=>null};
require(process.argv[1]);const V=window.MathStudio.multivariate,out={};
out.cov=V.covariance(data.small);out.pearson=V.correlation(data.small);out.spearman=V.correlation(data.ties,{method:'spearman'});
out.ranks=V.ranks([10,20,20,30,20]);
const lin=V.pca([[1,2],[2,4],[3,6],[4,8],[5,10]],{scaling:'center'});out.lin={explained:lin.explained,loadings:lin.loadings};
const linStd=V.pca([[1,2],[2,4],[3,6],[4,8],[5,10]]);out.linStd=linStd.explained;
const ir=V.pca(data.iris,{scaling:'center'});out.iris={values:ir.eigenvalues,loadings:ir.loadings,scores:ir.scores,explained:ir.explained};
const irs=V.pca(data.iris);out.irisStd={values:irs.eigenvalues,loadings:irs.loadings};
const k1=V.kmeans(data.blobs,{k:2,seed:7,nInit:5}),k2=V.kmeans(data.blobs,{k:2,seed:7,nInit:5}),k3=V.kmeans(data.blobs,{k:2,seed:123,nInit:5,standardize:true});
out.km={labels:k1.labels,sizes:k1.sizes,inertia:k1.inertia,centers:k1.centers,same:JSON.stringify(k1)===JSON.stringify(k2),std:k3.labels};
out.km3=V.kmeans(data.iris,{k:3,seed:1,nInit:10}).inertia;
out.eig=V.jacobiEigen([[2,1],[1,2]]);
const tab=V.analyze({table:'Mixed',columns:['a','b'],analysis:'correlation'});
out.tab={n:tab.n,dropped:tab.dropped,rows:tab.rowNumbers,r:tab.pearson[0][1]};
const c=V.correlationAnalysis([[1,5],[2,5],[3,5]],['x','y']);out.constant={r:String(c.pearson[0][1]),diag:String(c.pearson[1][1]),warn:c.warnings,cov:c.covariance};
const errs=[
 ['oneRow',()=>V.covariance([[1,2]])],
 ['tableOneRow',()=>V.analyze({table:'Sparse',columns:['p','q'],analysis:'correlation'})],
 ['kBig',()=>V.kmeans([[1,2],[3,4]],{k:3})],
 ['kRange',()=>V.kmeans(data.blobs,{k:11})],
 ['kDistinct',()=>V.kmeans([[1,1],[1,1],[1,1]],{k:2})],
 ['pcaConst',()=>V.pca([[1,5],[2,5],[3,5]])],
 ['oneCol',()=>V.analyze({table:'Mixed',columns:['a']})],
 ['unknownCol',()=>V.analyze({table:'Mixed',columns:['a','zz']})],
 ['noTable',()=>V.analyze({table:'Nope',columns:['a','b']})],
 ['badAnalysis',()=>V.analyze({table:'Mixed',columns:['a','b'],analysis:'lda'})],
 ['nonSym',()=>V.jacobiEigen([[1,2],[3,4]])],
 ['nonFinite',()=>V.covariance([[1,NaN],[2,3]])],
];
out.errors={};for(const [n,f] of errs){try{f();out.errors[n]=null;}catch(e){out.errors[n]=e.message;}}
out.centeredConst=V.pca([[1,5],[2,5],[3,5]],{scaling:'center'}).explained;
console.log(JSON.stringify(out));
"""


def avg_ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


class MultivariateToolsTests(unittest.TestCase):
    def test_source_is_embedded_and_registered(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-multivariate-tools">\n'
        self.assertEqual(html.count(marker), 1)
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)].rstrip("\n"), SOURCE.read_text(encoding="utf-8").rstrip("\n"))
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-xlsx-import", "src/xlsx-import.js"),\n    ("promath-multivariate-tools", "src/multivariate-tools.js")', build)
        xlsx = html.index('<script id="promath-xlsx-import">')
        self.assertEqual(html.index("</script>\n", xlsx) + len("</script>\n"), html.index(marker))

    def test_no_dynamic_code_or_network(self):
        src = SOURCE.read_text(encoding="utf-8")
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"<!--", r"-->", r"<script", r"</script", r"Math\.random", r"localStorage"):
            self.assertIsNone(re.search(pattern, src, flags=re.IGNORECASE), pattern)
        self.assertEqual(src.count("innerHTML"), 1, "only the static panel template may use innerHTML")
        for needle in ("area.id='multivariate-details'", 'role="status" aria-live="polite"', 'role="img"', "importData", "calculate"):
            self.assertIn(needle, src)

    def test_workflow_runs_browser_smoke(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_multivariate_tools.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_numeric_references(self):
        data = {"small": SMALL, "ties": TIES, "iris": IRIS, "blobs": BLOBS}
        r = json.loads(subprocess.run(["node", "-e", NODE_SCRIPT, str(SOURCE), json.dumps(data)], check=True,
                                      capture_output=True, text=True, timeout=120).stdout)

        def mclose(a, b, tol):
            self.assertEqual(len(a), len(b))
            for ra, rb in zip(a, b):
                self.assertEqual(len(ra), len(rb))
                for x, y in zip(ra, rb):
                    self.assertLessEqual(abs(x - y), tol, (a, b))

        # Hand-derived covariance of SMALL (columns x, y, z): mean (3, 6, 6).
        cov_ref = [[2.5, 4.5, -5.5], [4.5, 8.5, -9.0], [-5.5, -9.0, 15.0]]
        mclose(r["cov"], cov_ref, 1e-12)
        pear_ref = [[cov_ref[i][j] / math.sqrt(cov_ref[i][i] * cov_ref[j][j]) for j in range(3)] for i in range(3)]
        mclose(r["pearson"], pear_ref, 1e-12)
        if np is not None:
            mclose(r["cov"], np.cov(np.array(SMALL, float), rowvar=False).tolist(), 1e-12)
            mclose(r["pearson"], np.corrcoef(np.array(SMALL, float), rowvar=False).tolist(), 1e-12)
        self.assertEqual(r["ranks"], [1, 3, 3, 5, 3])
        rx, ry = avg_ranks([t[0] for t in TIES]), avg_ranks([t[1] for t in TIES])
        mx, my = sum(rx) / 5, sum(ry) / 5
        rho = sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
        self.assertAlmostEqual(r["spearman"][0][1], rho, delta=1e-12)
        # ranks [1, 2.5, 2.5, 4, 5] vs [4.5, 4.5, 3, 1.5, 1.5]
        # deviations [-2, -.5, -.5, 1, 2] and [1.5, 1.5, 0, -1.5, -1.5]: rho = -8.25 / sqrt(9.5 * 9)
        self.assertAlmostEqual(rho, -8.25 / math.sqrt(9.5 * 9), delta=1e-12)
        self.assertEqual((rx, ry), ([1, 2.5, 2.5, 4, 5], [4.5, 4.5, 3, 1.5, 1.5]))
        self.assertAlmostEqual(r["spearman"][1][1], 1.0, delta=1e-15)

        # Perfectly collinear data: one component explains everything.
        mclose([r["lin"]["explained"]], [[1.0, 0.0]], 1e-12)
        mclose([r["linStd"]], [[1.0, 0.0]], 1e-12)
        mclose(r["lin"]["loadings"], [[1 / math.sqrt(5), 2 / math.sqrt(5)], [2 / math.sqrt(5), -1 / math.sqrt(5)]], 1e-12)

        # Deterministic sign convention: the largest |loading| of each component is positive.
        for L in (r["iris"]["loadings"], r["irisStd"]["loadings"], r["lin"]["loadings"]):
            for k in range(len(L[0])):
                col = [row[k] for row in L]
                self.assertGreater(col[max(range(len(col)), key=lambda j: abs(col[j]))], 0)
        self.assertAlmostEqual(sum(r["iris"]["explained"]), 1, delta=1e-12)
        vals = r["iris"]["values"]
        self.assertEqual(vals, sorted(vals, reverse=True))
        if np is not None:
            X = np.array(IRIS, float)
            for key, S in (("iris", np.cov(X, rowvar=False)), ("irisStd", np.corrcoef(X, rowvar=False))):
                w, v = np.linalg.eigh(S)
                w, v = w[::-1], v[:, ::-1]
                mclose([r[key]["values"]], [w.tolist()], 1e-10)
                mclose(np.abs(np.array(r[key]["loadings"])).tolist(), np.abs(v).tolist(), 1e-10)
            sc = np.array(r["iris"]["scores"])
            mclose(sc.tolist(), ((X - X.mean(0)) @ np.array(r["iris"]["loadings"])).tolist(), 1e-10)
            mclose(np.cov(sc, rowvar=False).tolist(), np.diag(r["iris"]["values"]).tolist(), 1e-10)
        mclose([r["eig"]["values"]], [[3, 1]], 1e-14)

        # k-means: two well-separated blobs are recovered exactly and deterministically.
        self.assertEqual(r["km"]["labels"], [1, 1, 1, 1, 2, 2, 2, 2])
        self.assertEqual(r["km"]["std"], [1, 1, 1, 1, 2, 2, 2, 2])
        self.assertEqual(r["km"]["sizes"], [4, 4])
        self.assertTrue(r["km"]["same"])
        mclose(r["km"]["centers"], [[0.05, 0.05], [10.05, 10.05]], 1e-12)
        centres = [[0.05, 0.05]] * 4 + [[10.05, 10.05]] * 4
        ref_inertia = sum((x - c[0]) ** 2 + (y - c[1]) ** 2 for (x, y), c in zip(BLOBS, centres))
        self.assertAlmostEqual(r["km"]["inertia"], ref_inertia, delta=1e-12)
        self.assertGreater(r["km3"], 0)

        # Table extraction drops rows with any blank/non-numeric selected cell.
        self.assertEqual(r["tab"]["n"], 4)
        self.assertEqual(r["tab"]["dropped"], 1)
        self.assertEqual(r["tab"]["rows"], [1, 3, 4, 5])
        self.assertAlmostEqual(r["tab"]["r"], 1.0, delta=1e-12)
        self.assertEqual(r["constant"]["r"], "NaN")
        self.assertEqual(r["constant"]["diag"], "NaN")
        self.assertIn("y", r["constant"]["warn"][0])
        self.assertEqual(r["constant"]["cov"][1][1], 0)
        mclose([r["centeredConst"]], [[1.0, 0.0]], 1e-12)

        e = r["errors"]
        self.assertTrue(all(e.values()), e)
        self.assertIn("At least 2", e["oneRow"])
        self.assertIn("found 1; 3 row(s) dropped", e["tableOneRow"])
        self.assertIn("cannot exceed", e["kBig"])
        self.assertIn("2 to 10", e["kRange"])
        self.assertIn("distinct", e["kDistinct"])
        self.assertIn("zero-variance", e["pcaConst"])
        self.assertIn("between 2 and 12", e["oneCol"])
        self.assertIn("Unknown column", e["unknownCol"])
        self.assertIn("existing data table", e["noTable"])
        self.assertIn("Unknown analysis", e["badAnalysis"])
        self.assertIn("symmetric", e["nonSym"])
        self.assertIn("finite", e["nonFinite"])


if __name__ == "__main__":
    unittest.main()
