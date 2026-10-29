"""Numerical regression for the new reusable weighted least-squares API."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for numerical JS test")
class WeightedLeastSquaresTests(unittest.TestCase):
    def test_weighted_fit_and_failure_paths(self):
        script = r"""
const fs=require('fs'), assert=require('assert');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const start=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=source.indexOf('const matrixRank=A=>rref(A).rank;');
assert(start>=0&&end>start,'Math kernel extraction boundaries');
const api=new Function(source.slice(start,end)+';return {weightedLeastSquares,leastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9];
const fit=api.weightedLeastSquares(A,b,[1,1,0.01]);
const ordinary=api.leastSquares(A,b);
assert(fit.solution.every(Number.isFinite));
assert(Math.abs(fit.solution[0]-1)<0.2,'Weighted intercept should track first observation');
assert(fit.solution[1]<ordinary.solution[1],'Downweight outlier slope');
assert(fit.weightedResidualSquared>=0);
const exact=api.weightedLeastSquares(A,[2,5,8],[1,10,100]);
assert(Math.abs(exact.solution[0]-2)<1e-10);
assert(Math.abs(exact.solution[1]-3)<1e-10);
assert(exact.weightedResidualSquared<1e-20);
const scaled=api.weightedLeastSquares(A,b,[10,10,0.1]);
for(let j=0;j<2;j++)assert(Math.abs(scaled.solution[j]-fit.solution[j])<1e-10);
assert(Math.abs(scaled.weightedResidualSquared/fit.weightedResidualSquared-10)<1e-8);
for(const w of [[1,0,1],[1,-1,1],[1,Infinity,1],[1,1],[1,'0x10',1],[1,null,1]]){
 assert.throws(()=>api.weightedLeastSquares(A,b,w));
}
assert.throws(()=>api.weightedLeastSquares([[1,0],[1,0],[1,0]],b,[1,1,1]));
assert.throws(()=>api.weightedLeastSquares(A,[1,2,Infinity],[1,1,1]));
assert(source.includes('leastSquares,weightedLeastSquares,eigenSymmetric'),'Export missing');
console.log('weighted least squares numerical checks passed');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True, text=True, timeout=20
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
