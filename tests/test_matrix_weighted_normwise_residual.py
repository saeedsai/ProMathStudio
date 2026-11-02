"""Weighted QR normwise residual ratio numerical, edge and offline regression."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedNormwiseResidualTests(unittest.TestCase):
    def test_offline_bundle_and_browser_registration(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundle = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundle)
        self.assertIn("Weighted normwise residual ratio", source)
        smoke = (ROOT / "tests/smoke_matrix_weighted_spectral_condition.py").read_text(encoding="utf-8")
        self.assertIn("weightedNormwiseResidualRatio", smoke)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_reference_scale_zero_near_rank_invalid_and_immutability(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const r=fit(A,b,w);
const expected=Math.sqrt(12/35)/(Math.sqrt(61/20)*Math.sqrt(2770)/35+Math.sqrt(581)/10);
assert(Math.abs(r.weightedNormwiseResidualRatio-expected)<1e-12);
assert(r.weightedNormwiseResidualGuidance.includes('not a certified coefficient-error'));
assert(Math.abs(fit(A,b,[100,100,1]).weightedNormwiseResidualRatio-expected)<1e-12);
assert(Math.abs(fit(A,[1,2,3],w).weightedNormwiseResidualRatio)<1e-14);
assert.strictEqual(fit(A,[0,0,0],w).weightedNormwiseResidualRatio,0);
for(const d of [1e-4,1e-8,1e-10]){
 const nearA=[[1,1],[1,1+d],[1,1+2*d]];
 const nearB=nearA.map(row=>2*row[0]-row[1]);
 const near=fit(nearA,nearB,[1,1,.01]);
 assert(Number.isFinite(near.weightedNormwiseResidualRatio));
 assert(near.weightedNormwiseResidualRatio<1e-8);
}
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,[1,1,1]),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted normwise residual references');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
