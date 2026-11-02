"""Weighted design column sine numerical references and offline parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedColumnSineTests(unittest.TestCase):
    def test_parity_and_mandatory_browser(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundle = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundle)
        self.assertIn("Weighted design column independence (sine):", source)
        self.assertIn("not a certified condition number", source)
        self.assertIn("python tests/smoke_matrix_weighted_column_sine.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required for numeric references")
    def test_analytic_near_rank_and_failures(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const {weightedLeastSquares}=new Function(src.slice(a,z)+';return {weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const fit=weightedLeastSquares(A,b,w),expected=Math.sqrt(1.05/(2.01*1.04));
assert(Math.abs(fit.designColumnSine-expected)<1e-12,fit.designColumnSine);
const scaled=weightedLeastSquares(A,b,[100,100,1]);
assert(Math.abs(fit.designColumnSine-scaled.designColumnSine)<1e-12);
const colScaled=weightedLeastSquares(A.map(row=>[row[0],row[1]*5]),b,w);
assert(Math.abs(fit.designColumnSine-colScaled.designColumnSine)<1e-12);
const near=weightedLeastSquares([[1,1],[1,1.0001],[1,1.0002]],[1,1.0001,1.0002],[1,1,1]);
assert(near.designColumnSine>0&&near.designColumnSine<1e-4);
assert(/nearly parallel/.test(near.designColumnGuidance));
assert(/not a certified condition number/.test(near.designColumnGuidance));
assert.throws(()=>weightedLeastSquares(A,b,[0,1,1]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted column sine analytic references');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
