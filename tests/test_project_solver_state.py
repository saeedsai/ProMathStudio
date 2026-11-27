"""Saved symbolic-solver controls are validated before project restore mutates workspaces."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ProjectSolverStateTests(unittest.TestCase):
    def test_project_schema_bundle_parity_and_solver_contract(self):
        source = (ROOT / "src/project-schema.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-project-schema">\n'
        start = html.index(marker) + len(marker)
        end = html.index("</script>", start)
        self.assertEqual(html[start:end].rstrip("\n"), source.rstrip("\n"))
        for contract in (
                "solver operation is invalid.",
                "solver engine is invalid.",
                "solver limit direction is invalid.",
                "short(solver.variable, 24",
                "solver variable is invalid.",
                "short(solver.limitPoint, 80,"):
            self.assertIn(contract, source)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_solver_enums_bounds_and_legacy_defaults(self):
        script = r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const context={window:{MathStudio:{}}};
vm.runInNewContext(fs.readFileSync('src/project-schema.js','utf8'),context);
const migrate=context.window.MathStudio.projectSchema.migrate;
const operations=['auto','expand','simplify','factor','solve','system','differentiate','integrate',
 'limit','numeric','laplace','inverse_laplace','fourier','inverse_fourier','ode','pde'];
const engines=['auto','sympy','offline'],directions=['+-','-','+'];
const base=()=>({format:'mathstudio-project',version:2,notebook:[]});
let count=0;
for(const operation of operations)for(const engine of engines)for(const limitDirection of directions){
 const data=base();data.solver={expression:'x^2',variable:'x'.repeat(24),operation,engine,
  limitPoint:'0'.repeat(80),limitDirection,odeInitialCondition:'y(0)=1'};
 const before=JSON.stringify(data),result=migrate(data);
 assert.equal(result.solver.operation,operation);assert.equal(result.solver.engine,engine);
 assert.equal(result.solver.limitDirection,limitDirection);
 assert.equal(JSON.stringify(data),before,'migration must not mutate project input');count++;
}
for(const [field,values] of [
 ['operation',['future',42,null,[],{}]],
 ['engine',['remote',42,null,[],{}]],
 ['limitDirection',['left','both',42,null,[],{}]]
])for(const value of values){
 const data=base();data.solver={[field]:value};
 assert.throws(()=>migrate(data),new RegExp('solver '+(field==='limitDirection'?'limit direction':field)));
}
for(const variable of ['x','theta_2','θ','θ_1','x'.repeat(24)]) {
 const data=base();data.solver={variable};assert.equal(migrate(data).solver.variable,variable);
}
for(const variable of ['1x','x y','x+y','x.y']) {
 const data=base();data.solver={variable};
 assert.throws(()=>migrate(data),/solver variable is invalid/);
}
for(const variable of [42,null,[],{}]) {
 const data=base();data.solver={variable};
 assert.throws(()=>migrate(data),/solver variable/);
}
for(const [field,value] of [['variable','x'.repeat(25)],['limitPoint','0'.repeat(81)]]){
 const data=base();data.solver={[field]:value};
 assert.throws(()=>migrate(data),new RegExp(field==='limitPoint'?'solver limit point':'solver variable'));
}
const empty=base();empty.solver={operation:'',engine:'',limitDirection:'',variable:'',limitPoint:''};
assert.equal(migrate(empty).version,2,'empty selectors retain legacy defaults');
const legacy=base();legacy.version=1;legacy.solver={};
assert.equal(migrate(legacy).version,2,'missing selectors retain legacy defaults');
const noSolver=base();noSolver.version=1;assert.equal(migrate(noSolver).version,2);
console.log('PASS saved solver selectors: '+count+' valid combinations, variable identifiers, invalid enums/types, bounds and legacy defaults');
"""
        result = subprocess.run(["node", "-e", script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS saved solver selectors: 144", result.stdout)


if __name__ == "__main__":
    unittest.main()
