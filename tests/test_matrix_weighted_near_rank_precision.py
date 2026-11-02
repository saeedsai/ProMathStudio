"""Near-rank weighted QR: independent high-precision Decimal reference and browser parity."""
import json
import shutil
import subprocess
import unittest
from decimal import Decimal, localcontext
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def decimal_reference(delta, weight_text):
    """Solve the independent 2x2 normal equations in 90-digit Decimal.

    Normal equations are used ONLY for the independent high-precision oracle;
    the production code continues to use reorthogonalized QR.
    """
    with localcontext() as ctx:
        ctx.prec = 90
        d = Decimal(delta)
        A = [[Decimal(1), Decimal(1)],
             [Decimal(1), Decimal(1) + d],
             [Decimal(1), Decimal(1) + 2*d]]
        b = [Decimal(1), Decimal(1)-d, Decimal(1)-2*d+d/5]
        w = [Decimal(x) for x in weight_text]
        gram = [[sum(w[i]*A[i][j]*A[i][k] for i in range(3))
                 for k in range(2)] for j in range(2)]
        rhs = [sum(w[i]*A[i][j]*b[i] for i in range(3)) for j in range(2)]
        det = gram[0][0]*gram[1][1]-gram[0][1]*gram[1][0]
        assert det > 0
        x0 = (rhs[0]*gram[1][1]-rhs[1]*gram[0][1])/det
        x1 = (gram[0][0]*rhs[1]-gram[1][0]*rhs[0])/det
        residual = (sum((w[i]/max(w))*
                        (A[i][0]*x0+A[i][1]*x1-b[i])**2
                        for i in range(3))).sqrt()
        return (A, b, w), (float(x0), float(x1)), float(residual)


class NearRankWeightedQRPrecision(unittest.TestCase):
    def test_offline_bundle_and_registered_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundle = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundle)
        self.assertIn("orthogonalityTolerance", source)
        smoke = (ROOT / "tests/smoke_matrix_weighted_spectral_condition.py").read_text(encoding="utf-8")
        self.assertIn("near_fit", smoke)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_independent_decimal_near_rank_extreme_weights_and_failures(self):
        cases = []
        for d in ("1e-4", "1e-6", "1e-8", "1e-10", "1e-11"):
            for weights in (("1", "1", "1"), ("1", "1", "0.01"), ("1", "1e-8", "1")):
                (A, b, w), expected_x, expected_residual = decimal_reference(d, weights)
                cases.append({
                    "d": d, "A": [[float(v) for v in row] for row in A],
                    "b": [float(v) for v in b], "w": [float(v) for v in w],
                    "x": expected_x, "residual": expected_residual,
                })
        js = r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const cases=JSON.parse(process.argv[1]);
const results=cases.map(c=>{
 const before=JSON.stringify([c.A,c.b,c.w]);
 const r=fit(c.A,c.b,c.w);
 assert.strictEqual(JSON.stringify([c.A,c.b,c.w]),before);
 assert(r.solution.every(Number.isFinite));
 assert(Number.isFinite(r.residual));
 return {solution:r.solution,residual:r.residual,normalResidual:r.normalResidual};
});
assert.throws(()=>fit([[1,1],[1,1],[1,1]],[1,2,3],[1,1,1]),/Rank-deficient/);
assert.throws(()=>fit([[1,1],[1,2],[1,3]],[1,2,3],[1,0,1]),/Weights must be finite/);
console.log(JSON.stringify(results));
"""
        run = subprocess.run(["node", "-e", js, json.dumps(cases)],
                             cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        results = json.loads(run.stdout)
        self.assertEqual(len(results), len(cases))
        for case, result in zip(cases, results):
            # Binary64 input rounding is magnified by near-rank condition;
            # the tolerance scales with 1/d and is NOT a certified error bound.
            tol = max(1e-9, 2e-15/float(case["d"]))
            for actual, expected in zip(result["solution"], case["x"]):
                self.assertLess(abs(actual-expected), tol, (case, result))
            self.assertLess(abs(result["residual"]-case["residual"]),
                            max(1e-13, 2e-4*case["residual"]), (case, result))
            self.assertGreaterEqual(result["normalResidual"], 0)


if __name__ == "__main__":
    unittest.main()
