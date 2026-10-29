"""Strict decimal least-squares RHS and weight validation, with QR scale references."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for QR regression")
class LeastSquaresInputHardeningTests(unittest.TestCase):
    def test_rhs_types_decimal_format_and_weight_bounds(self):
        script = r"""
const fs = require('fs'), assert = require('assert');
const source = fs.readFileSync('src/matrix-tools.js', 'utf8');
const start = source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end = source.indexOf('const matrixRank=A=>rref(A).rank;');
assert(start >= 0 && end > start, 'QR kernel extraction boundaries');
const api = new Function(source.slice(start, end) +
    ';return {leastSquares,weightedLeastSquares};')();
const A = [[1,0],[1,1],[1,2]], b = [1,2,9], w = [1,1,0.01];
const reference = api.weightedLeastSquares(A, b, w);
assert(Math.abs(reference.solution[0] - 33/35) < 1e-11);
assert(Math.abs(reference.solution[1] - 41/35) < 1e-11);
assert(Math.abs(reference.weightedResidualSquared - 12/35) < 1e-11);
const decimal = [' +1.0 ', '2e0', '9.'];
for (const method of ['leastSquares', 'weightedLeastSquares']) {
 const fit = method === 'leastSquares' ?
    api.leastSquares(A, decimal) : api.weightedLeastSquares(A, decimal, w);
 assert(fit.solution.every(Number.isFinite), method + ' decimal RHS');
 for (const invalid of ['0x10','0b10','0o10','2_000','Infinity','1e309','NaN',
                        '', ' ', [2], {valueOf:()=>2}, true, null, 1e13]) {
  const bad = [1, invalid, 9];
  assert.throws(() => method === 'leastSquares' ?
    api.leastSquares(A, bad) : api.weightedLeastSquares(A, bad, w),
    /row 2|finite numbers/, method + ' accepted ' + String(invalid));
 }
}
for (const invalid of [[1], {valueOf:()=>1}, null, 0, -1, 1e-13, 1e13, '0x1']) {
 assert.throws(() => api.weightedLeastSquares(A,b,[1,invalid,0.01]),
    /weight|Weights/, 'weight accepted ' + String(invalid));
}
const big = api.weightedLeastSquares(
    A.map(row=>row.map(x=>x*1e9)), b.map(x=>x*1e9),
    [1e12,1e12,1e10]);
for (let j=0;j<2;j++)assert(Math.abs(big.solution[j]-reference.solution[j])<1e-10);
assert(Math.abs(big.weightedResidualSquared/(reference.weightedResidualSquared*1e30)-1)<1e-10);
const tiny = api.weightedLeastSquares(
    A.map(row=>row.map(x=>x*1e-9)), b.map(x=>x*1e-9),w);
for (let j=0;j<2;j++)assert(Math.abs(tiny.solution[j]-reference.solution[j])<1e-10);
for (const rankLoss of [
    [[1,1],[1,1],[1,1]],
    [[1,1],[1,1+1e-13],[1,1+2e-13]]
]) {
 assert.throws(() => api.weightedLeastSquares(rankLoss,b,w),
    /rank-deficient|Rank-deficient/);
}
assert.deepStrictEqual(b,[1,2,9]);
assert.deepStrictEqual(w,[1,1,0.01]);
console.log('PASS: strict RHS, weight types, scaling and near-rank loss');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT,
            capture_output=True, text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
