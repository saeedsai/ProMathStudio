"""Matrix keyboard grid navigation: pure target logic and standalone parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MatrixKeyboardGridTests(unittest.TestCase):
    def test_grid_wiring_and_standalone_parity(self):
        src = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)], src + "\n")
        self.assertIn("for(const container of [grid,gridB,rhsGrid,weightGrid])enableMatrixArrowNavigation(container)", src)
        self.assertIn("event.preventDefault();", src)
        self.assertIn("event.altKey||event.ctrlKey||event.metaKey||event.shiftKey", src)
        for label in ("Right-hand side b row", "Observation weight row"):
            self.assertIn("'data-col':'0','aria-label':'" + label, src)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_arrow_targets_boundaries_and_invalid_keys(self):
        js = r"""
const assert=require('node:assert/strict'),fs=require('node:fs');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
assert.doesNotThrow(()=>new Function(src));
const a=src.indexOf('function matrixArrowTarget(');
const b=src.indexOf('function enableMatrixArrowNavigation(',a);
assert(a>0&&b>a);
const move=new Function(src.slice(a,b)+';return matrixArrowTarget;')();
assert.deepEqual(move(0,0,2,2,'ArrowRight'),[0,1]);
assert.deepEqual(move(0,0,2,2,'ArrowDown'),[1,0]);
assert.deepEqual(move(1,1,2,2,'ArrowLeft'),[1,0]);
assert.deepEqual(move(1,1,2,2,'ArrowUp'),[0,1]);
assert.deepEqual(move(1,2,3,3,'ArrowDown'),[2,2]);
assert.equal(move(0,0,2,2,'ArrowUp'),null);
assert.equal(move(0,0,2,2,'ArrowLeft'),null);
assert.equal(move(1,1,2,2,'ArrowRight'),null);
assert.equal(move(1,1,2,2,'ArrowDown'),null);
assert.deepEqual(move(0,0,3,1,'ArrowDown'),[1,0]);
assert.equal(move(1,0,3,1,'ArrowRight'),null);
assert.equal(move(0,0,2,2,'Tab'),null);
assert.equal(move(-1,0,2,2,'ArrowDown')?.[0]??null,0);
assert.equal(move(0,0,0,2,'ArrowDown'),null);
assert.equal(move(0.5,0,2,2,'ArrowRight'),null);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
