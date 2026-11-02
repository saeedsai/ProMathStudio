"""Weighted least-squares guidance, scale invariance and rank rejection."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedLeastSquaresGuidanceTests(unittest.TestCase):
    def test_guidance_is_bound_to_weight_inputs_and_offline_bundle(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        self.assertEqual(
            source.rstrip("\n"),
            html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n"),
        )
        self.assertIn('id="mat-weight-guidance"', source)
        self.assertIn("'aria-describedby':'mat-weight-guidance'", source)
        for phrase in (
            "full-column-rank 3×2",
            "positive relative weights",
            "same positive factor",
            "weighted squared residual",
            "dimensionless relative priorities",
            "consistent units",
            "not certified inverse variances or uncertainty estimates",
        ):
            self.assertIn(phrase, source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for weighted numerical regression")
    def test_weight_scaling_rank_and_validation_reference(self):
        script = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync('src/matrix-tools.js','utf8');
const start = source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end = source.indexOf('const matrixRank=', start);
assert(start >= 0 && end > start, 'Pure solver extraction boundaries changed');
const {weightedLeastSquares} = new Function(
  source.slice(start,end) + ';return {weightedLeastSquares};'
)();
const A = [[1,0],[1,1],[1,2]], b = [1,2,9];
const snapshot = JSON.stringify([A,b]);
const first = weightedLeastSquares(A,b,[1,1,0.01]);
const scaled = weightedLeastSquares(A,b,[100,100,1]);
const tiny = weightedLeastSquares(A,b,[1e-10,1e-10,1e-12]);
for(let i=0;i<2;i++){
  assert(Math.abs(first.solution[i]-[33/35,41/35][i])<1e-10);
  assert(Math.abs(first.solution[i]-scaled.solution[i])<1e-10);
  assert(Math.abs(first.solution[i]-tiny.solution[i])<1e-10);
}
assert(Math.abs(first.weightedResidualSquared-12/35)<1e-10);
assert(Math.abs(scaled.weightedResidualSquared-100*first.weightedResidualSquared)<1e-8);
assert(Math.abs(tiny.weightedResidualSquared-1e-10*first.weightedResidualSquared)<1e-18);
assert.equal(JSON.stringify([A,b]),snapshot,'solver mutated input');
assert.throws(()=>weightedLeastSquares([[1,2],[2,4],[3,6]],b,[1,1,1]),/Rank-deficient/);
assert.throws(()=>weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares(A,b,[1,-1,1]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares(A,b,[1,1,1e-13]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares(A,b,[1,1,1e13]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares(A,b,[1,1]),/3 positive values/);
assert.throws(()=>weightedLeastSquares(A,b,['0x10',1,1]),/Invalid positive weight/);
console.log('PASS weighted least-squares scale, rank, domain, input immutability');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True,
            text=True, timeout=25,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
