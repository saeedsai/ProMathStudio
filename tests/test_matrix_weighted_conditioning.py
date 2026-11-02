"""Weighted least-squares QR screening diagnostics, numerical references and bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedConditioningTests(unittest.TestCase):
    def test_standalone_parity_and_mandatory_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("qrDiagonalSpread", source)
        self.assertIn("weightRatio=maxWeight/Math.min(...w)", source)
        self.assertIn("not a certified coefficient-error or uncertainty bound", source)
        self.assertIn("QR diagonal spread is only a screening heuristic", source)
        self.assertIn("Weighted design QR diagonal spread (heuristic)", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_conditioning.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for numerical regression")
    def test_numerical_references_weight_invariance_and_failures(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const start=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=source.indexOf('const matrixRank=A=>rref(A).rank;');
assert(start>=0&&end>start,'Kernel boundaries');
const api=new Function(source.slice(start,end)+';return {weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,0.01];
const before=JSON.stringify([A,b,w]);
const a=api.weightedLeastSquares(A,b,w);
const scaled=api.weightedLeastSquares(A,b,[10,10,0.1]);
assert(Math.abs(a.solution[0]-33/35)<1e-10);
assert(Math.abs(a.solution[1]-41/35)<1e-10);
assert(Math.abs(a.weightedResidualSquared-12/35)<1e-10);
assert(a.weightRatio===100&&Math.abs(scaled.weightRatio-100)<1e-10);
assert(Number.isFinite(a.qrDiagonalSpread)&&a.qrDiagonalSpread>=1);
assert(Math.abs(a.qrDiagonalSpread-scaled.qrDiagonalSpread)<1e-10);
assert(a.solution.every((v,j)=>Math.abs(v-scaled.solution[j])<1e-10));
assert(Math.abs(scaled.weightedResidualSquared/a.weightedResidualSquared-10)<1e-10);
assert(JSON.stringify([A,b,w])===before,'Inputs must not mutate');
const extreme=api.weightedLeastSquares([[1,0],[0,1],[1,1]],[2,3,5],[1e-12,1,1e12]);
assert(extreme.solution.every(Number.isFinite));
assert(extreme.weightRatio===1e24);
assert(extreme.conditioningAdvisory.includes('Potential sensitivity'));
const near=[[1,1],[1,1+1e-9],[1,1+2e-9]];
try{
 const fit=api.weightedLeastSquares(near,[2,2+1e-9,2+2e-9],[1,1,1]);
 assert(fit.solution.every(Number.isFinite));
 assert(fit.qrDiagonalSpread>1e8);
 assert(fit.conditioningAdvisory.includes('Potential sensitivity'));
}catch(error){
 assert(/Rank-deficient|orthogonality|finite floating-point/.test(error.message),error.message);
}
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],[2,2,2],[1,1,1]),/Rank-deficient/);
assert.throws(()=>api.weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
console.log('PASS weighted QR sensitivity and numerical reference');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
