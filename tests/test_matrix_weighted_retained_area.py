"""Retained-row geometric independence in 3x2 weighted leave-one-out fits."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedRetainedAreaTests(unittest.TestCase):
    def test_standalone_parity_and_mandatory_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("looRetainedAreas", source)
        self.assertIn("Retained-row independence (LOO normalized area", source)
        self.assertIn("not a certified condition number", source)
        self.assertIn("python tests/smoke_matrix_weighted_retained_area.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required for analytic numerical references")
    def test_analytic_areas_near_rank_weight_scaling_and_failures(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const {weightedLeastSquares}=new Function(src.slice(a,z)+';return {weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const fit=weightedLeastSquares(A,b,w);
const expected=[1/Math.sqrt(10),2/Math.sqrt(5),1/Math.sqrt(2)];
fit.looRetainedAreas.forEach((v,i)=>assert(Math.abs(v-expected[i])<1e-12));
assert(fit.looPredictions.every(Number.isFinite));
const scaled=weightedLeastSquares(A,b,[10,10,.1]);
fit.looRetainedAreas.forEach((v,i)=>assert(Math.abs(v-scaled.looRetainedAreas[i])<1e-12));
const rowScaled=weightedLeastSquares([[100,0],[1,1],[1,2]],b,w);
fit.looRetainedAreas.forEach((v,i)=>assert(Math.abs(v-rowScaled.looRetainedAreas[i])<1e-12));
const near=weightedLeastSquares([[1,0],[1,1e-9],[1,1]],[1,2,3],[1,1,1]);
assert(near.looRetainedAreas[2]>0&&near.looRetainedAreas[2]<1e-8);
assert.strictEqual(near.looPredictions[2],null);
assert.strictEqual(near.looResiduals[2],null);
assert.strictEqual(near.looCoefficientShifts[2],null);
const singular=weightedLeastSquares([[1,0],[0,1],[0,1]],[2,3,4],[1,1,1]);
assert.strictEqual(singular.looRetainedAreas[0],0);
assert.strictEqual(singular.looPredictions[0],null);
assert.throws(()=>weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS retained-row area numerical references');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
