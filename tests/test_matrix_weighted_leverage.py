"""Weighted least-squares row leverage: fixed-weight design influence, not uncertainty."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WeightedLeverageTests(unittest.TestCase):
    def test_bundle_and_browser_registration(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        self.assertEqual(source, html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n"))
        self.assertIn("const rowLeverages=Q.map(", source)
        self.assertIn("Weighted design leverage (rows 1–3):", source)
        self.assertIn("not an outlier probability or a coefficient-uncertainty bound", source)
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
        self.assertIn("python tests/smoke_matrix_weighted_leverage.py", workflow)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for numerical reference")
    def test_leverage_reference_invariance_and_rank_rejection(self):
        script = r"""
const fs=require('fs'),assert=require('assert');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const start=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=source.indexOf('const matrixRank=A=>rref(A).rank;');
assert(start>=0&&end>start);
const api=new Function(source.slice(start,end)+';return {leastSquares,weightedLeastSquares};')();
const A=[[1,0],[1,1],[1,2]],b=[1,2,9],w=[1,1,0.01];
const before=JSON.stringify([A,b,w]);
const fit=api.weightedLeastSquares(A,b,w);
const scaled=api.weightedLeastSquares(A,b,[10,10,0.1]);
const expected=[104/105,101/105,1/21];
for(let i=0;i<3;i++){
 assert(Math.abs(fit.rowLeverages[i]-expected[i])<1e-11);
 assert(Math.abs(fit.rowLeverages[i]-scaled.rowLeverages[i])<1e-12);
 assert(fit.rowLeverages[i]>=0&&fit.rowLeverages[i]<=1+1e-12);
}
assert(Math.abs(fit.rowLeverages.reduce((a,b)=>a+b,0)-2)<1e-12);
assert(JSON.stringify([A,b,w])===before,'Inputs must remain immutable');
const ordinary=api.leastSquares(A,b);
for(let i=0;i<3;i++)assert(Math.abs(ordinary.rowLeverages[i]-[5/6,1/3,5/6][i])<1e-12);
const extreme=api.weightedLeastSquares([[1,0],[0,1],[1,1]],[2,3,5],[1e-12,1,1e12]);
assert(extreme.rowLeverages.every(x=>Number.isFinite(x)&&x>=0&&x<=1+1e-12));
assert(Math.abs(extreme.rowLeverages.reduce((a,b)=>a+b,0)-2)<1e-8);
assert.throws(()=>api.weightedLeastSquares([[1,1],[1,1],[1,1]],[2,2,2],[1,1,1]),/Rank-deficient/);
assert.throws(()=>api.weightedLeastSquares(A,b,[1,0,1]),/Weights must be finite/);
console.log('PASS weighted leverage references, invariance, invalid inputs');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
