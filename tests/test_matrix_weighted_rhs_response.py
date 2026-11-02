"""Fixed-design weighted RHS response: QR reference, perturbation and invariance."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedRhsResponseTests(unittest.TestCase):
    def test_source_bundle_and_required_browser_gate(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        self.assertEqual(source, html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertIn("const rhsResponseRows=Q.map(", source)
        self.assertIn("RHS +1-unit response (rows 1–3", source)
        self.assertIn("not a statistical uncertainty or error bound", source)
        self.assertIn("python tests/smoke_matrix_weighted_rhs_response.py",
                      (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8"))

    @unittest.skipUnless(shutil.which("node"), "Node.js required for numerical reference")
    def test_reference_perturbation_scale_and_failures(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const start=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=source.indexOf('const matrixRank=A=>rref(A).rank;');
assert(start>=0&&end>start);
const api=new Function(source.slice(start,end)+';return {weightedLeastSquares,leastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,0.01];
const before=JSON.stringify([A,b,w]);
const fit=api.weightedLeastSquares(A,b,w);
const expected=[[104/105,-102/105],[2/105,99/105],[-1/105,3/105]];
const scaled=api.weightedLeastSquares(A,b,[10,10,0.1]);
for(let i=0;i<3;i++)for(let j=0;j<2;j++){
 assert(Math.abs(fit.rhsResponseRows[i][j]-expected[i][j])<1e-11);
 assert(Math.abs(fit.rhsResponseRows[i][j]-scaled.rhsResponseRows[i][j])<1e-11);
 const perturbed=b.slice();perturbed[i]+=0.01;
 const changed=api.weightedLeastSquares(A,perturbed,w);
 assert(Math.abs(changed.solution[j]-fit.solution[j]-0.01*expected[i][j])<1e-10);
}
const ordinary=api.leastSquares(A,b);
for(let i=0;i<3;i++){
 const perturbed=b.slice();perturbed[i]+=0.01;
 const changed=api.leastSquares(A,perturbed);
 for(let j=0;j<2;j++)
  assert(Math.abs(changed.solution[j]-ordinary.solution[j]-0.01*ordinary.rhsResponseRows[i][j])<1e-10);
}
assert(JSON.stringify([A,b,w])===before,'Inputs mutated');
const extreme=api.weightedLeastSquares([[1,0],[0,1],[1,1]],[2,3,5],[1e-12,1,1e12]);
assert(extreme.rhsResponseRows.flat().every(Number.isFinite));
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],b,w),/Rank-deficient/);
assert.throws(()=>api.weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
console.log('PASS weighted RHS response references and perturbations');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
