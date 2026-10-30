"""Structured engineering solver contracts, numerical references and bundle parity."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class SolverContractTests(unittest.TestCase):
    def test_standalone_contract_parity(self):
        source = (ROOT / "src/matrix-tools.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-matrix-tools">\n'
        start = html.index(marker) + len(marker)
        self.assertEqual(html[start:html.index("</script>", start)], source + "\n")

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_contracts_errors_and_reference_solutions(self):
        js = r"""
const fs=require('node:fs'),assert=require('node:assert/strict');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const b=src.indexOf('/* Jacobi rotations',a);
assert(a>=0&&b>a);
const registry=new Function(src.slice(a,b)+';return engineeringSolvers;')();
const solve=registry.get('matrix.solve.real.small');
const inverse=registry.get('matrix.inverse.real.small');
assert(Object.isFrozen(solve)&&Object.isFrozen(solve.inputSchema));
assert(Object.isFrozen(solve.inputSchema.A)&&Object.isFrozen(solve.inputSchema.A.rows));
assert(Object.isFrozen(solve.assumptions));
assert.deepEqual([...solve.inputSchema.A.rows],[2,3]);
assert.equal(solve.inputSchema.A.columns,'rows');
assert.equal(solve.inputSchema.b.length,'A.rows');
assert.equal(solve.inputSchema.A.maxMagnitude,1e12);
assert.equal(inverse.inputSchema.b,undefined);
assert(solve.assumptions.some(s=>s.includes('units are not checked')));
assert.equal(registry.get('__proto__'),null);
const ids=registry.list().map(item=>item.id);
assert.equal(new Set(ids).size,2);
const A=[[2,1],[1,3]],rhs=[5,7],before=JSON.stringify([A,rhs]);
const solved=registry.executeResult('matrix.solve.real.small',{A,b:rhs});
assert.equal(solved.ok,true);assert(Object.isFrozen(solved));
assert(Math.abs(solved.value.solution[0]-1.6)<1e-12);
assert(Math.abs(solved.value.solution[1]-1.8)<1e-12);
assert(solved.value.residual<1e-12);
assert(solved.value.normwiseBackwardError<1e-12);
assert.equal(JSON.stringify([A,rhs]),before);
const inv=registry.executeResult('matrix.inverse.real.small',{A});
assert.equal(inv.ok,true);
assert(Math.abs(inv.value[0][0]-.6)<1e-12);
assert(Math.abs(inv.value[1][1]-.4)<1e-12);
const A3=[[2,0,0],[0,3,0],[0,0,4]],b3=[4,9,16];
assert.deepEqual(registry.executeResult('matrix.solve.real.small',{A:A3,b:b3}).value.solution,[2,3,4]);
for(const [id,params,code] of [
 ['__proto__',{},'UNKNOWN_SOLVER'],
 ['matrix.solve.real.small',null,'INVALID_INPUT_OBJECT'],
 ['matrix.solve.real.small',{A},'MISSING_INPUT'],
 ['matrix.inverse.real.small',{A,b:rhs},'UNEXPECTED_INPUT'],
 ['matrix.solve.real.small',{A:[[1,2],[2,4]],b:[3,6]},'SOLVER_REJECTED'],
 ['matrix.solve.real.small',{A:[[1,2],[2,4]],b:[3,7]},'SOLVER_REJECTED'],
 ['matrix.solve.real.small',{A:[[1,0],[0,1]],b:[Infinity,1]},'SOLVER_REJECTED'],
 ['matrix.inverse.real.small',{A:[[1,2,3],[4,5,6]]},'INVALID_MATRIX_SHAPE']
]){
 const result=registry.executeResult(id,params);
 assert.equal(result.ok,false,id);assert(Object.isFrozen(result));
 assert(Object.isFrozen(result.error));assert.equal(result.error.code,code,id);
 assert(result.error.message.length>0);
}
assert.equal(registry.execute('matrix.solve.real.small',{A,b:rhs}).solution[0],1.6);
assert.throws(()=>registry.execute('matrix.solve.real.small',{A}),/Missing engineering solver input/);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
