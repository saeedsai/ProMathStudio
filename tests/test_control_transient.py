"""Control two-state transient simulation reuses coupled RK4, with numerical references."""
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ControlTransientTests(unittest.TestCase):
    def test_bundle_parity_and_shared_solver(self):
        source = (ROOT / "src/control-equilibrium.js").read_text(encoding="utf-8")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-control-equilibrium">\n'
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(source.rstrip("\n"), bundled)
        self.assertIn("studio.odeTools.solveSystem(", source)
        self.assertIn('id="ct-eq-transient-run"', html)
        self.assertIn('id="ct-eq-transient-table"', html)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_forward_backward_singular_and_invalid(self):
        js = r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const ode=fs.readFileSync('src/ode-tools.js','utf8');
const kernel=ode.slice(ode.indexOf('function finite('),ode.indexOf('const area='));
const evaluate=(expr,{y,z})=>{
 const m=/^-\(([^)]+)\)\*y-\(([^)]+)\)\*z\+\(([^)]+)\)$/.exec(expr);
 assert(m,'unexpected derivative expression: '+expr);
 return -Number(m[1])*y-Number(m[2])*z+Number(m[3]);
};
const solveSystem=new Function('evaluate','const MAX=1e12;const M={numerical:{evaluate}};'+
 kernel+';return solveSystem;')(evaluate);
"""
        js += r"""
const nodes={};
const ids=['ct-equilibrium','ct-eq-size','ct-eq-matrix','ct-eq-forcing',
 'ct-eq-status','ct-eq-output','ct-eq-run','ct-eq-stability-run',
 'ct-eq-stability-status','ct-eq-stability-output','ct-eq-initial',
 'ct-eq-t0','ct-eq-t1','ct-eq-steps','ct-eq-transient-run',
 'ct-eq-transient-table','ct-eq-transient-status','ct-eq-transient-output'];
for(const id of ids)nodes[id]={value:'',textContent:'',disabled:false,events:{},
 addEventListener(k,fn){this.events[k]=fn;}};
nodes['ct-eq-size'].value='2';nodes['ct-eq-matrix'].value='2,0;0,3';
nodes['ct-eq-forcing'].value='4,9';nodes['ct-eq-initial'].value='0,0';
nodes['ct-eq-t0'].value='0';nodes['ct-eq-t1'].value='1';nodes['ct-eq-steps'].value='80';
const studio={engineeringSolvers:{},odeTools:{solveSystem}};
vm.runInNewContext(fs.readFileSync('src/control-equilibrium.js','utf8'),{
 window:{MathStudio:studio},document:{getElementById:id=>nodes[id]}
});
const api=studio.controlEquilibrium;
const r=api.simulateTransient([[2,0],[0,3]],[4,9],[0,0],0,1,80);
assert.equal(r.rows.length,81);
assert(Math.abs(r.rows.at(-1)[1]-2*(1-Math.exp(-2)))<1e-7);
assert(Math.abs(r.rows.at(-1)[2]-3*(1-Math.exp(-3)))<1e-7);
const back=api.simulateTransient([[2,0],[0,3]],[4,9],
 [2*(1-Math.exp(-2)),3*(1-Math.exp(-3))],1,0,80);
assert(Math.abs(back.rows.at(-1)[1])<1e-7);
assert(Math.abs(back.rows.at(-1)[2])<2e-7);
const singular=api.simulateTransient([[0,0],[0,2]],[1,0],[0,1],0,1,80);
assert(Math.abs(singular.rows.at(-1)[1]-1)<1e-9);
assert(Math.abs(singular.rows.at(-1)[2]-Math.exp(-2))<1e-7);
assert.throws(()=>api.simulateTransient([[1,0,0],[0,1,0]],[1,2],[0,0]),/2×2/);
assert.throws(()=>api.simulateTransient([[1,0],[0,1]],['0x10',2],[0,0]),/decimal or scientific/);
assert.throws(()=>api.simulateTransient([[1,0],[0,1]],[1,2],[0,0],0,1,3),/4 to 1000/);
nodes['ct-eq-transient-run'].events.click();
assert.match(nodes['ct-eq-transient-output'].textContent,/trajectory samples/);
assert.equal(nodes['ct-eq-transient-table'].disabled,false);
nodes['ct-eq-matrix'].value='0x10,0;0,1';nodes['ct-eq-matrix'].events.input();
assert.equal(nodes['ct-eq-transient-table'].disabled,true);
nodes['ct-eq-transient-run'].events.click();
assert.match(nodes['ct-eq-transient-status'].textContent,/decimal or scientific/);
console.log('PASS Control transient numerical references and invalidation');
"""
        result = subprocess.run(["node", "-e", js], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS Control transient", result.stdout)


if __name__ == "__main__":
    unittest.main()
