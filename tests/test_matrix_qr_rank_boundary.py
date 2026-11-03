"""QR rank-boundary references: near-threshold acceptance, perturbed RHS and singular rejection.

References are analytic. With columns c1=(1,1,1) and c2=(1,1+e,1+2e), where e is a
power of two (all entries exact in binary64), c2 = (1+e)c1 + e(-1,0,1), so the exact
orthogonalized-column ratio is e*sqrt(2)/||c2|| and R[1][1] = e*sqrt(2).
"""
import json
import math
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SCRIPT = r"""
const fs=require('fs');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const api=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return {qr,leastSquares};')();
const cases=JSON.parse(process.argv[1]),out=[];
for(const c of cases){
 try{
  const r=c.op==='qr'?api.qr(c.A):api.leastSquares(c.A,c.b);
  out.push({ok:true,R:r.R,ratio:r.minIndependenceRatio,margin:r.rankMargin,guidance:r.rankGuidance,solution:r.solution,residual:r.residual});
 }catch(e){out.push({ok:false,error:String(e.message)});}
}
process.stdout.write(JSON.stringify(out));
"""


def design(e):
    return [[1, 1], [1, 1 + e], [1, 1 + 2 * e]]


@unittest.skipUnless(shutil.which("node"), "Node required")
class QrRankBoundaryReferences(unittest.TestCase):
    def run_cases(self, cases):
        done = subprocess.run(["node", "-e", SCRIPT, json.dumps(cases)], cwd=ROOT,
                              capture_output=True, text=True, check=True, timeout=60)
        return json.loads(done.stdout)

    def test_near_threshold_acceptance_matches_analytic_reference(self):
        # Ratios straddle 1e-12: 2^-33 (well above), 2^-39 (~1.5e-12, just above).
        exponents = (33, 36, 39)
        results = self.run_cases([{"op": "qr", "A": design(2.0 ** -k)} for k in exponents])
        for k, result in zip(exponents, results):
            e = 2.0 ** -k
            self.assertTrue(result["ok"], result)
            exact_r22 = e * math.sqrt(2)
            exact_ratio = exact_r22 / math.sqrt(1 + (1 + e) ** 2 + (1 + 2 * e) ** 2)
            # Roundoff in the cancelled column scales like eps / ratio.
            rel_tol = 50 * 2.0 ** -52 / exact_ratio
            self.assertLess(abs(abs(result["R"][1][1]) - exact_r22) / exact_r22, rel_tol, (k, result))
            self.assertLess(abs(result["ratio"] - exact_ratio) / exact_ratio, rel_tol, (k, result))
            self.assertAlmostEqual(result["margin"], result["ratio"] / 1e-12, delta=1e-9 * result["margin"])
            self.assertIn("Near rank threshold", result["guidance"])
            self.assertIn("not a certified bound", result["guidance"])

    def test_singular_and_sub_threshold_rejection(self):
        results = self.run_cases([
            {"op": "qr", "A": design(2.0 ** -40)},  # ratio ~7.4e-13 < 1e-12
            {"op": "qr", "A": design(2.0 ** -45)},
            {"op": "qr", "A": design(0.0)},          # exactly dependent
            {"op": "qr", "A": [[0, 1], [0, 2], [0, 3]]},  # zero column
            {"op": "leastSquares", "A": design(2.0 ** -40), "b": [1, 2, 3]},
        ])
        for result in results:
            self.assertFalse(result["ok"], result)
            self.assertIn("ank-deficient", result["error"])

    def test_well_separated_guidance(self):
        result = self.run_cases([{"op": "qr", "A": [[1, 0], [1, 1], [1, 2]]}])[0]
        self.assertTrue(result["ok"], result)
        self.assertAlmostEqual(result["ratio"], math.sqrt(2) / math.sqrt(5), places=12)
        self.assertIn("well separated", result["guidance"])

    def test_perturbed_rhs_near_threshold(self):
        e = 2.0 ** -33
        x1, x2 = 2.0, -3.0
        exact_b = [x1 + x2, x1 + x2 * (1 + e), x1 + x2 * (1 + 2 * e)]
        delta = 1e-3
        # (1,-2,1) is orthogonal to range(A): solution unchanged, residual = delta*sqrt(6).
        orth_b = [exact_b[0] + delta, exact_b[1] - 2 * delta, exact_b[2] + delta]
        # (-1,0,1) = (c2-(1+e)c1)/e lies in range(A): dx2 = delta/e, dx1 = -delta(1+e)/e.
        small = 2.0 ** -50
        range_b = [exact_b[0] - small, exact_b[1], exact_b[2] + small]
        exact, orth, ranged = self.run_cases([
            {"op": "leastSquares", "A": design(e), "b": exact_b},
            {"op": "leastSquares", "A": design(e), "b": orth_b},
            {"op": "leastSquares", "A": design(e), "b": range_b},
        ])
        ratio = e * math.sqrt(2) / math.sqrt(3)
        tol = 1e3 * 2.0 ** -52 / ratio  # conditioning-aware absolute tolerance on O(1) solution
        for result in (exact, orth, ranged):
            self.assertTrue(result["ok"], result)
        self.assertLess(abs(exact["solution"][0] - x1), tol, exact)
        self.assertLess(abs(exact["solution"][1] - x2), tol, exact)
        self.assertLess(abs(orth["solution"][0] - x1), tol, orth)
        self.assertLess(abs(orth["solution"][1] - x2), tol, orth)
        self.assertLess(abs(orth["residual"] - delta * math.sqrt(6)) / (delta * math.sqrt(6)), 1e-6, orth)
        self.assertLess(abs(ranged["solution"][1] - (x2 + small / e)), tol, ranged)
        self.assertLess(abs(ranged["solution"][0] - (x1 - small * (1 + e) / e)), tol, ranged)

    def test_offline_parity_and_ui_text(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Minimum column independence ratio: ", source)


if __name__ == "__main__":
    unittest.main()
