"""Matrix rebuild focus targets and standalone bundle parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MatrixResizeFocusTests(unittest.TestCase):
    def test_wiring_and_bundle_parity(self):
        src = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)], src + "\n")
        for grid in ("grid", "gridB", "rhsGrid", "weightGrid"):
            self.assertIn(f"const focused=matrixGridFocusPosition({grid});", src)
            self.assertIn(f"restoreMatrixGridFocus({grid},focused,", src)
        self.assertIn("container.contains(active)", src)
        self.assertIn("if(!position)return;", src)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_clamp_and_invalid_focus_targets(self):
        js = r"""
const assert=require('node:assert/strict'),fs=require('node:fs');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
assert.doesNotThrow(()=>new Function(src));
const a=src.indexOf('function matrixResizeFocusTarget(');
const b=src.indexOf('function matrixGridFocusPosition(',a);
assert(a>0&&b>a);
const f=new Function(src.slice(a,b)+';return matrixResizeFocusTarget;')();
for(const [args,expected] of [
 [[2,2,3,3],[2,2]],[[2,2,2,2],[1,1]],[[1,2,2,2],[1,1]],
 [[0,0,2,3],[0,0]],[[2,0,2,1],[1,0]],
 [[-1,0,2,2],null],[[0,-1,2,2],null],[[0,0,0,2],null],
 [[0,0,2,0],null],[[0.5,0,2,2],null],[[0,0,2.5,2],null]
])assert.deepEqual(f(...args),expected);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
