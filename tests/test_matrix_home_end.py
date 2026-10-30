"""Regression: matrix Home/End targets and offline bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MatrixHomeEndTests(unittest.TestCase):
    def test_bundle_and_keyboard_wiring(self):
        src = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)], src + "\n")
        self.assertIn("matrixHomeEndTarget(row,col,rows,cols,event.key,event.ctrlKey)", src)
        self.assertIn("(arrow&&event.ctrlKey)", src)
        self.assertIn("'aria-label':'Matrix A row '", src)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_reference_boundaries_and_invalid_targets(self):
        js = r"""
const assert=require('node:assert/strict'),fs=require('node:fs');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
assert.doesNotThrow(()=>new Function(src));
const a=src.indexOf('function matrixHomeEndTarget(');
const b=src.indexOf('function enableMatrixArrowNavigation(',a);
assert(a>0&&b>a);
const f=new Function(src.slice(a,b)+';return matrixHomeEndTarget;')();
assert.deepEqual(f(1,1,3,3,'Home',false),[1,0]);
assert.deepEqual(f(1,0,3,3,'End',false),[1,2]);
assert.deepEqual(f(2,2,3,3,'Home',true),[0,0]);
assert.deepEqual(f(0,0,3,3,'End',true),[2,2]);
assert.deepEqual(f(1,0,3,1,'End',false),[1,0]);
assert.deepEqual(f(0,0,2,2,'End',false),[0,1]);
assert.deepEqual(f(0,0,2,2,'End',true),[1,1]);
for(const k of ['ArrowLeft','Tab','Escape'])assert.equal(f(0,0,2,2,k,false),null);
for(const args of [[-1,0,2,2,'Home',false],[2,0,2,2,'End',false],
 [0,2,2,2,'Home',false],[0,0,0,2,'End',true],
 [0.5,0,2,2,'End',false]])assert.equal(f(...args),null);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
