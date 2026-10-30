"""Engineering registry dimension contracts and shared consumers."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("node"), "Node.js required")
class EngineeringShapeContracts(unittest.TestCase):
    def test_dimension_errors_and_numerical_recovery(self):
        js = r"""
const fs=require('fs'),assert=require('assert');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const start=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const end=src.indexOf('/* Jacobi rotations',start);
assert(start>=0 && end>start);
const registry=new Function(src.slice(start,end)+';return engineeringSolvers;')();
const code=(id,params)=>registry.executeResult(id,params).error?.code;
for(const A of [[],[[1]],[[1,2]],[[1,2],[3,4],[5,6]],[[1,2,3],[4,5,6]],'bad',null]){
 assert.equal(code('matrix.inverse.real.small',{A}),'INVALID_MATRIX_SHAPE');
}
const A=[[2,0],[0,3]],before=JSON.stringify(A);
for(const b of [[],[1],[1,2,3],'1,2',null]){
 assert.equal(code('matrix.solve.real.small',{A,b}),'INVALID_VECTOR_LENGTH');
}
assert.equal(JSON.stringify(A),before,'registry must not mutate source matrix');
assert.equal(registry.executeResult('matrix.solve.real.small',{A,b:[4,9]}).value.solution.join(','),'2,3');
assert.equal(registry.executeResult('matrix.inverse.real.small',{A}).ok,true);
assert.equal(code('matrix.solve.real.small',{A:[[1,2],[2,4]],b:[3,7]}),'SOLVER_REJECTED');
assert.throws(()=>registry.execute('matrix.solve.real.small',{A,b:[1]}),/must match the number/);
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
