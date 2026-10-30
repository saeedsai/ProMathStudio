"""Canonical Matrix solver registry: numerical references, schema, errors and bundle parity."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class EngineeringSolverRegistryTests(unittest.TestCase):
    def test_standalone_and_real_ui_consumers(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        tag = '<script id="promath-matrix-tools">\n'
        start = html.index(tag) + len(tag)
        self.assertEqual(html[start:html.index("</script>", start)], source + "\n")
        self.assertIn("M.engineeringSolvers=engineeringSolvers;", source)
        self.assertIn("engineeringSolvers.execute('matrix.solve.real.small',{A,b:readRhs()})", source)
        self.assertIn("engineeringSolvers.execute('matrix.inverse.real.small',{A})", source)
        self.assertIn("run:({A,b})=>solve(A,b)", source)
        self.assertIn("run:({A})=>inverse(A)", source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required for numerical references")
    def test_registry_numerics_validation_and_uniqueness(self):
        js = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const source=fs.readFileSync('src/matrix-tools.js','utf8');
const a=source.indexOf('const limit=3,MAX_ENTRY=1e12;');
const b=source.indexOf('/* Jacobi rotations',a);
assert(a>=0&&b>a);
const kernel=source.slice(a,b);
const registry=new Function(kernel+';return engineeringSolvers;')();
const ids=registry.list().map(x=>x.id);
assert.deepEqual(ids,['matrix.solve.real.small','matrix.inverse.real.small']);
assert.equal(new Set(ids).size,ids.length);
assert.equal(registry.get('__proto__'),null);
assert.equal(registry.get('matrix.solve.real.small').status,'implemented');
assert.deepEqual([...registry.get('matrix.solve.real.small').inputs],['A','b']);
assert(Object.isFrozen(registry.get('matrix.solve.real.small').disciplines));
assert(Object.isFrozen(registry.list()));
const A=[[2,1],[1,3]],bvec=[5,7],before=JSON.stringify([A,bvec]);
const solved=registry.execute('matrix.solve.real.small',{A,b:bvec});
assert(Math.abs(solved.solution[0]-1.6)<1e-12);
assert(Math.abs(solved.solution[1]-1.8)<1e-12);
assert(solved.residual<1e-12);
const inverse=registry.execute('matrix.inverse.real.small',{A});
assert(Math.abs(inverse[0][0]-.6)<1e-12);
assert(Math.abs(inverse[0][1]+.2)<1e-12);
assert.equal(JSON.stringify([A,bvec]),before);
const three=registry.execute('matrix.solve.real.small',{A:[[2,0,0],[0,3,0],[0,0,4]],b:[4,9,16]});
assert.deepEqual([...three.solution],[2,3,4]);
for(const [id,params,pattern] of [
 ['__proto__',{A},/Unknown engineering solver ID/],
 ['matrix.solve.real.small',{A},/Missing engineering solver input: b/],
 ['matrix.inverse.real.small',{A,b:bvec},/Unexpected engineering solver input: b/],
 ['matrix.solve.real.small',null,/must be an object/],
 ['matrix.solve.real.small',{A:[[1,2],[2,4]],b:[3,6]},/Singular/],
 ['matrix.inverse.real.small',{A:[[1,2],[2,4]]},/Singular/],
 ['matrix.inverse.real.small',{A:[[1,0],[true,1]]},/Enter a number/]
])assert.throws(()=>registry.execute(id,params),pattern);
const duplicate=kernel.replace("id:'matrix.inverse.real.small'","id:'matrix.solve.real.small'");
assert.notEqual(duplicate,kernel);
assert.throws(()=>new Function(duplicate+';return engineeringSolvers;')(),/Invalid or duplicate engineering solver ID/);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT, capture_output=True,
                                text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
