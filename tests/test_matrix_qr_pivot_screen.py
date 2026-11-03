"""QR column-pivoting screen: permutation invariance, near-dependence ordering and parity."""
import itertools
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = r"""
const fs=require('fs');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const api=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return {qr,qrPivotScreen};')();
const out=[];for(const c of JSON.parse(process.argv[1])){try{const r=c.op==='qr'?api.qr(c.A):api.qrPivotScreen(c.A);out.push({ok:true,order:r.pivotOrder,ratios:r.pivotRatios,min:r.pivotedMinRatio,plain:r.minIndependenceRatio});}catch(e){out.push({ok:false,error:e.message});}}
process.stdout.write(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "Node required")
class QrPivotScreenTests(unittest.TestCase):
    def run_cases(self, cases):
        done = subprocess.run(["node", "-e", SCRIPT, json.dumps(cases)], cwd=ROOT, capture_output=True, text=True, check=True, timeout=60)
        return json.loads(done.stdout)

    def test_permutation_invariant_min_ratio(self):
        e = 2.0 ** -20
        base = [[1, 1, 0], [1, 1 + e, 0], [1, 1 + 2 * e, 1]]  # c1, c2 nearly dependent; c3 independent
        cases = []
        perms = list(itertools.permutations(range(3)))
        for perm in perms:
            cases.append({"op": "qr", "A": [[row[j] for j in perm] for row in base]})
        results = self.run_cases(cases)
        mins = [r["min"] for r in results]
        self.assertTrue(all(r["ok"] for r in results), results)
        self.assertLess(max(mins) - min(mins), 1e-12 * max(mins), mins)
        # The plain (unpivoted) ratio depends on input order; the screen does not.
        plains = [r["plain"] for r in results]
        self.assertGreater(max(plains) / min(plains), 1.0 + 1e-9, plains)
        # The two near-dependent columns (original 1 and 2) are never both chosen first:
        for perm, r in zip(perms, results):
            first_two = {perm[r["order"][0] - 1], perm[r["order"][1] - 1]}
            self.assertNotEqual(first_two, {0, 1}, (perm, r))
            self.assertEqual(sorted(r["order"]), [1, 2, 3])
            self.assertEqual(r["ratios"][0], 1.0)

    def test_reference_ratios(self):
        # Orthogonal columns: every pivot ratio is 1.
        ortho = self.run_cases([{"op": "screen", "A": [[1, 0], [0, 2], [0, 0]]}])[0]
        self.assertEqual(ortho["ratios"], [1.0, 1.0])
        # c2 = (1,1) vs c1 = (1,0): residual ratio of the second pick is sin(45°).
        two = self.run_cases([{"op": "screen", "A": [[1, 1], [0, 1]]}])[0]
        self.assertAlmostEqual(two["min"], 2 ** -0.5, places=15)
        dep = self.run_cases([{"op": "screen", "A": [[1, 2], [2, 4], [3, 6]]}])[0]
        self.assertLess(dep["min"], 1e-15)

    def test_parity_and_ui_text(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Column pivot order (screen): ", source)


if __name__ == "__main__":
    unittest.main()
