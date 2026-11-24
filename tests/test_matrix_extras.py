"""Matrix extras (up to 8x8): bundle parity, safety, CI wiring and Node numerical references."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "matrix-extras.js"


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


NODE_SCRIPT = r"""
require(process.argv[1]);
const X = globalThis.MathStudio.matrixExtras;
const out = {};
out.chol = X.cholesky("4 12 -16\n12 37 -43\n-16 -43 98");
const H = [...Array(4)].map((_, i) => [...Array(4)].map((_, j) => 1 / (i + j + 1)));
out.hilbert = X.cholesky(H).residual;
out.rank = X.rank("1 2 3\n2 4 6\n1 1 1");
// 5x5 rank-3 matrix: B (5x3) times C (3x5).
const B = [[1,0,2],[0,1,-1],[3,1,0],[2,-2,1],[1,1,1]], C = [[1,2,0,-1,3],[0,1,1,2,-1],[2,0,1,1,0]];
const A5 = B.map(r => C[0].map((_, j) => r.reduce((s, b, k) => s + b * C[k][j], 0)));
out.rank5 = X.rank(A5);
out.poly = X.charpoly([[2, 1], [1, 2]]).coefficients;
const T = [...Array(6)].map((_, i) => [...Array(6)].map((_, j) => i === j ? 2 : Math.abs(i - j) === 1 ? -1 : 0));
out.det6 = X.determinant(T);
out.norm = X.norms("3 0 0\n0 -5 0\n0 0 1");
out.ldlt = X.ldlt("1 2\n2 1");
out.errors = {};
for (const [k, fn] of Object.entries({
  ragged: () => X.parseMatrix("1 2\n3"),
  big: () => X.parseMatrix(Array(9).fill("1").join("\n")),
  wide: () => X.parseMatrix("1 2 3 4 5 6 7 8 9"),
  nonnumeric: () => X.parseMatrix("1 2\n3 0x10"),
  nonpd: () => X.cholesky("1 2\n2 1"),
  nonsym: () => X.cholesky("1 2\n3 1"),
  unknown: () => X.compute("1", "inverse"),
})) { try { fn(); out.errors[k] = null; } catch (e) { out.errors[k] = e.message; } }
console.log(JSON.stringify(out));
"""


class MatrixExtrasTests(unittest.TestCase):
    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_bundle_matches_source_and_order(self):
        self.assertEqual(embedded(self.html, "promath-matrix-extras").rstrip("\n"), self.src.rstrip("\n"))
        self.assertLess(self.html.index('<script id="promath-matrix-tools">'), self.html.index('<script id="promath-matrix-extras">'))
        build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-matrix-tools", "src/matrix-tools.js"),\n    ("promath-matrix-extras", "src/matrix-extras.js"),', build)

    def test_no_dynamic_code_network_markup_or_innerhtml(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"import\s*\(", r"innerHTML"):
            self.assertIsNone(re.search(pattern, self.src), pattern)
        for token in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(token, self.src.lower())

    def test_ui_contract(self):
        for ident in ("matrix-extras-details", "matrix-extras-input", "matrix-extras-op", "matrix-extras-run",
                      "matrix-extras-to-table", "matrix-extras-output"):
            self.assertIn(f"'{ident}'", self.src)
        self.assertIn("role:'status','aria-live':'polite'", self.src)
        self.assertIn("getElementById('calculator-panel')", self.src)
        self.assertIn("M.dataTables.importData(", self.src)
        self.assertIn("min-height:40px", self.src)

    def test_workflow_runs_smoke(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_matrix_extras.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "node is required")
    def test_node_numerical_references(self):
        result = subprocess.run(["node", "-e", NODE_SCRIPT, str(SOURCE)], capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out["chol"]["L"], [[2, 0, 0], [6, 1, 0], [-8, 5, 3]])
        self.assertLess(out["chol"]["residual"], 1e-15)
        self.assertLess(out["hilbert"], 1e-12)
        rank = out["rank"]
        self.assertEqual((rank["rank"], rank["nullity"]), (2, 1))
        n = [row[0] for row in rank["nullBasis"]]
        sign = 1 if n[0] > 0 else -1
        expected = [1 / 6 ** 0.5, -2 / 6 ** 0.5, 1 / 6 ** 0.5]
        for got, ref in zip(n, expected):
            self.assertAlmostEqual(sign * got, ref, places=12)
        self.assertLess(rank["nullResidual"], 1e-12)
        r5 = out["rank5"]
        self.assertEqual((r5["rank"], r5["nullity"]), (3, 2))
        self.assertLess(r5["nullResidualRelative"], 1e-12)
        self.assertLess(r5["orthogonality"]["null"], 1e-12)
        self.assertLess(r5["orthogonality"]["column"], 1e-12)
        self.assertEqual(out["poly"], [1, -4, 3])
        self.assertAlmostEqual(out["det6"]["det"], 7, places=11)
        self.assertEqual(out["det6"]["trace"], 12)
        self.assertLess(out["det6"]["residual"], 1e-14)
        self.assertAlmostEqual(out["norm"]["two"], 5, places=13)
        self.assertAlmostEqual(out["norm"]["condition2"], 5, places=12)
        self.assertEqual(out["ldlt"]["D"], [1, -3])
        errors = out["errors"]
        self.assertIn("Ragged rows", errors["ragged"])
        self.assertIn("At most 8 rows", errors["big"])
        self.assertIn("at most 8 columns", errors["wide"])
        self.assertIn("not a decimal number", errors["nonnumeric"])
        self.assertIn("pivot 2", errors["nonpd"])
        self.assertIn("symmetric", errors["nonsym"])
        self.assertIn("Unknown matrix operation", errors["unknown"])


if __name__ == "__main__":
    unittest.main()
