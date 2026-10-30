"""Control equilibrium shares canonical matrix solve and invalidates stale results."""
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
class ControlEquilibriumTests(unittest.TestCase):
 def test_bundle_and_registry_reuse(self):
  source=(ROOT/'src/control-equilibrium.js').read_text(encoding='utf-8')
  html=(ROOT/'index.html').read_text(encoding='utf-8')
  tag='<script id="promath-control-equilibrium">\n'
  start=html.index(tag)+len(tag)
  self.assertEqual(html[start:html.index('</script>',start)],source+'\n')
  self.assertIn('("promath-control-equilibrium", "src/control-equilibrium.js")',(ROOT/'scripts/build.py').read_text(encoding='utf-8'))
  self.assertIn("studio.engineeringSolvers.execute('matrix.solve.real.small',{A,b})",source)
  self.assertIn("disciplines:['mathematics','control-theory']",(ROOT/'src/matrix-tools.js').read_text(encoding='utf-8'))
  self.assertNotIn('function solve(',source)
  self.assertIn('id="ct-equilibrium"',html)
  self.assertIn('ẋ = −A·x + b',html)
 @unittest.skipUnless(shutil.which('node'),'Node.js required')
 def test_numerical_references_singular_and_recovery(self):
  js=r"""
const fs=require('node:fs'),assert=require('node:assert/strict'),vm=require('node:vm');
const matrix=fs.readFileSync('src/matrix-tools.js','utf8');
const kernel=matrix.slice(matrix.indexOf('const limit=3,MAX_ENTRY=1e12;'),matrix.indexOf('/* Jacobi rotations'));
const registry=new Function(kernel+';return engineeringSolvers;')();
const nodes=Object.create(null);
for(const id of ['ct-equilibrium','ct-eq-size','ct-eq-matrix','ct-eq-forcing','ct-eq-status','ct-eq-output','ct-eq-run'])
 nodes[id]={value:'',textContent:'',events:{},addEventListener(k,fn){this.events[k]=fn;}};
nodes['ct-eq-size'].value='2';
nodes['ct-eq-matrix'].value='2,0;0,3';
nodes['ct-eq-forcing'].value='4,9';
const studio={engineeringSolvers:registry};
vm.runInNewContext(fs.readFileSync('src/control-equilibrium.js','utf8'),{
 window:{MathStudio:studio},document:{getElementById:id=>nodes[id]}
});
const api=studio.controlEquilibrium;
assert(Object.isFrozen(api));
assert(registry.get('matrix.solve.real.small').disciplines.includes('control-theory'));
const A=[[2,1],[1,3]],b=[5,7],before=JSON.stringify([A,b]);
const r=api.solve(A,b);
assert(Math.abs(r.solution[0]-1.6)<1e-12&&Math.abs(r.solution[1]-1.8)<1e-12);
assert(r.residual<1e-12&&r.normwiseBackwardError<1e-12);
assert.equal(JSON.stringify([A,b]),before);
assert.deepEqual(Array.from(api.solve([[2,0,0],[0,3,0],[0,0,4]],[4,9,16]).solution),[2,3,4]);
assert.equal(api.parseMatrix('2, 0; 0, 3',2).length,2);
assert.throws(()=>api.parseMatrix('1,2;3',2),/exactly 2 values/);
assert.throws(()=>api.parseMatrix('1,2;3,4;5,6',2),/exactly 2 rows/);
assert.throws(()=>api.parseMatrix('1,2;3,4',4),/State dimension/);
assert.throws(()=>api.solve([[1,2],[2,4]],[3,6]),/Singular/);
assert.throws(()=>api.solve([[1,2],[2,4]],[3,7]),/Inconsistent/);
assert.throws(()=>api.solve([[true,0],[0,1]],[1,1]),/Enter a number/);
nodes['ct-eq-run'].events.click();
assert.match(nodes['ct-eq-output'].textContent,/Equilibrium x\* = \[2, 3\]/);
nodes['ct-eq-matrix'].value='1,2;2,4';
nodes['ct-eq-matrix'].events.input();
assert.equal(nodes['ct-eq-output'].textContent,'No current result.');
nodes['ct-eq-run'].events.click();
assert.equal(nodes['ct-eq-output'].textContent,'No valid equilibrium.');
assert.match(nodes['ct-eq-status'].textContent,/Singular/);
nodes['ct-eq-matrix'].value='2,0;0,3';
nodes['ct-eq-run'].events.click();
assert.match(nodes['ct-eq-output'].textContent,/Equilibrium x\* = \[2, 3\]/);
"""
  result=subprocess.run(['node','-e',js],cwd=ROOT,capture_output=True,text=True,timeout=20)
  self.assertEqual(result.returncode,0,result.stdout+result.stderr)
if __name__=='__main__':unittest.main()
