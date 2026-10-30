"""Matrix input sections: structure, standalone parity and numerical regression."""
import shutil
import subprocess
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
class MatrixInputSectionsTests(unittest.TestCase):
    def test_disclosure_and_standalone(self):
        src = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)], src + "\n")
        self.assertIn('aria-label="Matrix A inputs"', src)
        for name in ("rhs", "weight", "b"):
            self.assertEqual(src.count('id="mat-' + name + '-section"'), 1)
        self.assertIn("document.getElementById(id).open=true", src)
        for name in ("det", "transpose", "inverse", "add", "subtract", "multiply", "solve",
                     "lu", "qr", "least-squares", "weighted-least-squares", "eigen",
                     "svd", "pseudoinverse", "rref", "rank"):
            self.assertEqual(src.count('id="mat-' + name + '"'), 1)
    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_numerical_api(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
assert.doesNotThrow(()=>new Function(src));
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const b=src.indexOf('/* Jacobi rotations for bounded real',a);
const {solve,add}=new Function(src.slice(a,b)+';return {solve,add};')();
assert.deepEqual(add([[1,2],[3,4]],[[4,3],[2,1]]),[[5,5],[5,5]]);
const s=solve([[3,1],[1,2]],[9,8]);
assert(Math.abs(s.solution[0]-2)<1e-12);
assert(Math.abs(s.solution[1]-3)<1e-12);
assert.throws(()=>solve([[1,2],[2,4]],[3,6]),/Singular/);
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
if __name__ == "__main__":
    unittest.main()
