"""Contextual Matrix result-transfer UI structural, compatibility and standalone parity."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MatrixContextualTransferTests(unittest.TestCase):
    def test_single_transfer_bar_and_all_operations(self):
        src = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index("/* ProMathStudio small-matrix calculator:")
        end = html.index("</script>", start)
        self.assertEqual(html[start:end], src + "\n")
        self.assertEqual(src.count('class="matrix-result-actions"'), 1)
        self.assertEqual(src.count('id="mat-send"'), 1)
        self.assertIn('role="group" aria-label="Result transfer options"', src)
        for operation in ("lu", "qr", "eigen", "svd"):
            self.assertEqual(src.count(f'data-mat-factor="{operation}" hidden'), 1)
            self.assertIn(f'id="mat-{operation}-factor"', src)
        for button in ("det", "transpose", "inverse", "add", "subtract", "multiply",
                       "solve", "lu", "qr", "least-squares", "weighted-least-squares",
                       "eigen", "svd", "pseudoinverse", "rref", "rank"):
            self.assertEqual(src.count(f'id="mat-{button}"'), 1)
        self.assertIn("syncFactorSelectors(operation);output.classList.remove('error')", src)
        self.assertIn("send.disabled=true;syncFactorSelectors(null)", src)
        self.assertIn(".matrix-result-actions [hidden]{display:none}", src)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_module_parses_and_preserves_math_public_api(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
assert.doesNotThrow(()=>new Function(src));
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const b=src.indexOf('/* Jacobi rotations for bounded real',a);
const {solve,conditionInfinity}=new Function(src.slice(a,b)+';return {solve,conditionInfinity};')();
const A=[[3,1],[1,2]],rhs=[9,8],before=JSON.stringify([A,rhs]);
const result=solve(A,rhs);
assert(Math.abs(result.solution[0]-2)<1e-12);
assert(Math.abs(result.solution[1]-3)<1e-12);
assert(Math.abs(conditionInfinity([[1,0],[0,1]])-1)<1e-12);
assert.equal(JSON.stringify([A,rhs]),before);
assert.throws(()=>solve([[1,2],[2,4]],[3,6]),/Singular/);
console.log('PASS contextual Matrix source syntax, solver reference and invalidity');
"""
        run = subprocess.run(["node", "-e", script], cwd=ROOT,
                             capture_output=True, text=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
