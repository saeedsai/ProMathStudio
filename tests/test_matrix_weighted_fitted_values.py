"""Weighted QR fitted values and near-rank prediction numerical references."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedFittedValuesTests(unittest.TestCase):
    def test_offline_parity_and_registered_browser(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundle = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundle)
        self.assertIn("Weighted fitted values (rows 1–3)", source)
        smoke = (ROOT / "tests/smoke_matrix_weighted_spectral_condition.py").read_text(encoding="utf-8")
        self.assertIn("fittedValues", smoke)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_spectral_condition.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_analytic_near_rank_weights_and_failures(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const r=fit(A,b,w),expected=[33/35,74/35,23/7];
expected.forEach((v,i)=>{
 assert(Math.abs(r.fittedValues[i]-v)<1e-12);
 assert(Math.abs(r.fittedValues[i]-b[i]-r.residuals[i])<1e-12);
});
assert(r.fittedValueGuidance.includes('not a high-precision guarantee'));
const scaled=fit(A,b,[100,100,1]);
expected.forEach((v,i)=>assert(Math.abs(scaled.fittedValues[i]-v)<1e-12));
for(const d of [1e-4,1e-8,1e-10,1e-11]){
 const nearA=[[1,1],[1,1+d],[1,1+2*d]],nearB=nearA.map(row=>2*row[0]-row[1]);
 const near=fit(nearA,nearB,[1,1,.01]);
 assert(near.fittedValues.every(Number.isFinite));
 near.fittedValues.forEach((v,i)=>assert(Math.abs(v-nearB[i])<1e-12));
 assert(Math.abs(near.solution[0]-2)<1e-3);
 assert(Math.abs(near.solution[1]+1)<1e-3);
}
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,[1,1,1]),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted fitted values and near-rank references');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
