"""Regression for strict 2x2/3x3 matrix and Ax=b numeric input contracts."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required for matrix numerical regression")
class MatrixStrictTypesTests(unittest.TestCase):
    def test_numeric_reference_and_non_numeric_coercion_rejection(self):
        script = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const source = fs.readFileSync('src/matrix-tools.js', 'utf8');
const start = source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end = source.indexOf('/* Doolittle P*A=L*U', start);
assert(start >= 0 && end > start, 'Expected matrix solver extraction boundaries');
const api = new Function(source.slice(start, end) + ';return {validate,solve};')();
const A2 = [[1,0],[0,1]];
const good = api.solve([[' 1e0 ',0],[0,'1.0']],['2e0','-3.']);
assert.deepEqual(good.solution, [2,-3]);
assert(good.residual < 1e-12);
const A3 = [[3,1,0],[0,2,1],[0,0,4]], b3 = [5,7,12];
const beforeA = JSON.stringify(A3), beforeB = JSON.stringify(b3);
const solved = api.solve(A3,b3);
solved.solution.forEach((x,i)=>assert(Math.abs(x-[1,2,3][i]) < 1e-12));
assert(solved.residual < 1e-12);
assert.equal(JSON.stringify(A3), beforeA);
assert.equal(JSON.stringify(b3), beforeB);
const invalid = [[1],new Number(1),1n,{valueOf:()=>1},true,null,undefined,Symbol('x')];
for(const value of invalid) {
 assert.throws(()=>api.validate([[1,0],[value,1]]), /Enter a number in row 2, column 1/,
               'Matrix accepted coercible nonprimitive');
 assert.throws(()=>api.solve(A2,[value,3]), /Enter a number in b row 1/,
               'RHS accepted coercible nonprimitive');
}
for(const value of ['0x10','0b11','0o7','1_000','Infinity','NaN','1e','']) {
 assert.throws(()=>api.solve(A2,[value,3]), /decimal or scientific|Enter a number/);
 assert.throws(()=>api.validate([[1,0],[value,1]]), /decimal or scientific|Enter a number/);
}
for(const value of [Infinity,NaN,1e13]) {
 assert.throws(()=>api.solve(A2,[value,3]), /finite numbers/);
 assert.throws(()=>api.validate([[1,0],[value,1]]), /finite numbers/);
}
assert.throws(()=>api.solve([[1,1],[1,1]],[2,3]), /Inconsistent system/);
assert.throws(()=>api.solve([[1,1],[1,1]],[2,2]), /Singular or nearly singular/);
console.log('PASS strict matrix and Ax=b type validation with 2x2/3x3 references');
"""
        result = subprocess.run(
            ["node", "-e", script], cwd=ROOT, capture_output=True,
            text=True, timeout=20,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_standalone_bundle_is_synchronized(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        start = html.index('/* ProMathStudio small-matrix calculator:')
        end = html.index("</script>", start)
        self.assertEqual(html[start:end], source + "\n")


if __name__ == "__main__":
    unittest.main()
