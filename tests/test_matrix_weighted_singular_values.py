"""Weighted 3x2 singular values, near-rank references and bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedSingularValueTests(unittest.TestCase):
    def test_bundle_and_quality_registration(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        bundled = html.split('<script id="promath-matrix-tools">\n', 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source, bundled)
        self.assertIn("Weighted design singular values (max, min", source)
        self.assertIn("do not certify coefficient accuracy", source)
        self.assertIn("python tests/smoke_matrix_weighted_singular_values.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node required")
    def test_near_rank_orthogonal_weight_scale_and_rejections(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const s=fs.readFileSync('src/matrix-tools.js','utf8');
const fit=new Function(s.slice(s.indexOf('const limit=3,MAX_ENTRY=1e12;'),s.indexOf('const matrixRank=A=>rref(A).rank;'))+';return weightedLeastSquares;')();
const close=(x,y,t=1e-8)=>assert(Number.isFinite(x)&&Math.abs(x-y)<=t*Math.max(Math.abs(y),1e-15),x+' vs '+y);
const A=[[1,1],[1,1.000001],[1,1.000002]],b=[1,.999999,.999998],w=[1,1,1],before=JSON.stringify([A,b,w]);
const r=fit(A,b,w);close(r.weightedDesignSingularValues[1],1e-6,1e-6);
close(r.solution[0],2);close(r.solution[1],-1);
const orth=fit([[3,0],[0,4],[0,0]],[3,8,0],w);
close(orth.weightedDesignSingularValues[0],4,1e-12);close(orth.weightedDesignSingularValues[1],3,1e-12);
fit(A,b,[100,100,100]).weightedDesignSingularValues.forEach((x,j)=>close(x,r.weightedDesignSingularValues[j],1e-10));
const scaled=fit([[3,0],[0,1e-6],[0,0]],[3,1e-6,0],w);
close(scaled.weightedDesignSingularValues[0],3,1e-12);close(scaled.weightedDesignSingularValues[1],1e-6,1e-12);
assert(r.weightedDesignSingularValues[0]>r.weightedDesignSingularValues[1]);
assert(r.weightedDesignSingularGuidance.includes('do not certify'));
assert.throws(()=>fit([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>fit(A,b,[1,0,1]),/Weights must be finite/);
assert.strictEqual(JSON.stringify([A,b,w]),before);
console.log('PASS weighted singular values');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True,
                                text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
