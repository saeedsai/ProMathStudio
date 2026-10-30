"""Control stability uses shared symmetric eigenanalysis, numerical and UI contracts."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ControlStabilityTests(unittest.TestCase):
    def test_standalone_parity(self):
        source = (ROOT / 'src/control-equilibrium.js').read_text(encoding='utf-8')
        html = (ROOT / 'index.html').read_text(encoding='utf-8')
        tag = '<script id="promath-control-equilibrium">\\n'
        start = html.index(tag) + len(tag)
        self.assertEqual(html[start:html.index('</script>', start)], source + '\\n')
        self.assertIn('id="ct-eq-stability-run"', html)
        self.assertIn('studio.matrixTools.eigenSymmetric(A)', source)

    @unittest.skipUnless(shutil.which('node'), 'Node.js required')
    def test_reference_eigenvalues_boundaries_and_recovery(self):
        js = r"""
const fs=require('fs'),assert=require('assert/strict'),vm=require('vm');
const src=fs.readFileSync('src/matrix-tools.js','utf8');
const a=src.indexOf('const limit=3,MAX_ENTRY=1e12;');
const b=src.indexOf('/* Scaled one-sided Jacobi SVD',a);
assert(a>=0&&b>a);
const shared=new Function(src.slice(a,b)+';return {engineeringSolvers,eigenSymmetric};')();
const nodes=Object.create(null);
for(const id of ['ct-equilibrium','ct-eq-size','ct-eq-matrix','ct-eq-forcing',
 'ct-eq-status','ct-eq-output','ct-eq-run','ct-eq-stability-run',
 'ct-eq-stability-status','ct-eq-stability-output'])
 nodes[id]={value:'',textContent:'',events:{},addEventListener(k,fn){this.events[k]=fn;}};
nodes['ct-eq-size'].value='2';
nodes['ct-eq-matrix'].value='2,0;0,3';
nodes['ct-eq-forcing'].value='4,9';
const studio={engineeringSolvers:shared.engineeringSolvers,
 matrixTools:{eigenSymmetric:shared.eigenSymmetric}};
vm.runInNewContext(fs.readFileSync('src/control-equilibrium.js','utf8'),{
 window:{MathStudio:studio},document:{getElementById:id=>nodes[id]}
});
const api=studio.controlEquilibrium;
const cases=[
 [[[2,0],[0,3]],'asymptotically stable',[3,2]],
 [[[-2,0],[0,3]],'unstable',[3,-2]],
 [[[0,0],[0,2]],'marginal',[2,0]],
 [[[1e-14,0],[0,2]],'indeterminate',[2,1e-14]],
 [[[2,1],[1,2]],'asymptotically stable',[3,1]],
 [[[3,0,0],[0,2,0],[0,0,1]],'asymptotically stable',[3,2,1]]
];
for(const [A,expected,values] of cases){
 const before=JSON.stringify(A),r=api.analyzeStability(A);
 assert.equal(r.classification,expected);
 assert.equal(JSON.stringify(A),before);
 assert(r.residual<=1e-8);
 assert.equal(r.eigenvalues.length,values.length);
 for(let i=0;i<values.length;i++)
  assert(Math.abs(r.eigenvalues[i]-values[i])<=1e-10*Math.max(1,Math.abs(values[i])));
}
assert.throws(()=>api.analyzeStability([[1,2],[0,3]]),/symmetric/);
assert.throws(()=>api.analyzeStability([[1,2,3],[4,5,6]]),/square/);
assert.throws(()=>api.analyzeStability([[Infinity,0],[0,1]]),/finite/);
nodes['ct-eq-stability-run'].events.click();
assert.match(nodes['ct-eq-stability-output'].textContent,/asymptotically stable/);
assert.match(nodes['ct-eq-stability-output'].textContent,/Equilibrium existence/);
nodes['ct-eq-matrix'].value='1,2;0,3';
nodes['ct-eq-matrix'].events.input();
assert.equal(nodes['ct-eq-stability-output'].textContent,'No current stability result.');
nodes['ct-eq-stability-run'].events.click();
assert.match(nodes['ct-eq-stability-status'].textContent,/symmetric/);
assert.equal(nodes['ct-eq-stability-output'].textContent,'No valid stability classification.');
nodes['ct-eq-matrix'].value='0,0;0,2';
nodes['ct-eq-stability-run'].events.click();
assert.match(nodes['ct-eq-stability-output'].textContent,/marginal/);
nodes['ct-eq-run'].events.click();
assert.equal(nodes['ct-eq-output'].textContent,'No valid equilibrium.');
"""
        p = subprocess.run(['node', '-e', js], cwd=ROOT, capture_output=True,
                           text=True, timeout=20)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == '__main__':
    unittest.main()
