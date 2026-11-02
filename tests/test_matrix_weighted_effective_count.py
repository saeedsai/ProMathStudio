"""Relative-weight concentration diagnostic, exact references and standalone parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedEffectiveCountTests(unittest.TestCase):
    def test_offline_parity_and_mandatory_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Relative-weight effective count (Kish-style):", source)
        self.assertIn("not statistical sample size", source)
        self.assertIn("python tests/smoke_matrix_weighted_effective_count.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required for numerical references")
    def test_balanced_concentrated_scale_invariance_and_rejections(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;'),z=src.indexOf('const matrixRank=A=>rref(A).rank;');
assert(a>=0&&z>a);
const {weightedLeastSquares}=new Function(src.slice(a,z)+';return {weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,.01],before=JSON.stringify([A,b,w]);
const fit=weightedLeastSquares(A,b,w);
const expected=2.01**2/(2+.01**2);
assert(Math.abs(fit.effectiveWeightCount-expected)<1e-12,fit.effectiveWeightCount);
assert(fit.effectiveWeightCount>=1&&fit.effectiveWeightCount<=3);
const balanced=weightedLeastSquares(A,b,[1,1,1]);
assert(Math.abs(balanced.effectiveWeightCount-3)<1e-12);
const scaled=weightedLeastSquares(A,b,[100,100,1]);
assert(Math.abs(fit.effectiveWeightCount-scaled.effectiveWeightCount)<1e-12);
const concentrated=weightedLeastSquares(A,b,[1e8,1,1]);
assert(concentrated.effectiveWeightCount>1&&concentrated.effectiveWeightCount<1.000001);
assert(/fewer than two/.test(concentrated.effectiveWeightGuidance));
const extreme=weightedLeastSquares(A,b,[1e12,1e-12,1e-12]);
assert(Number.isFinite(extreme.effectiveWeightCount)&&extreme.effectiveWeightCount>=1);
assert.throws(()=>weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
assert.throws(()=>weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS relative-weight effective count numerical references');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
