"""Root-locus branch tracking numeric and browser-canvas regression (actual bundled JS)."""
from pathlib import Path
import os
import re
import subprocess
import unittest

HTML=(Path(__file__).resolve().parents[1]/'index.html').read_text(encoding='utf-8')
MATCH=re.search(r'<script id="promath-control-theory">([\s\S]*?)</script>',HTML)

class RootLocusBranchTracking(unittest.TestCase):
 def test_reference_poles_and_branch_rendering(self):
  self.assertIsNotNone(MATCH)
  js=r"""
const assert=require('node:assert/strict'),vm=require('node:vm');
const calls={lineTo:0,arc:0},ctx={};
for(const name of ['clearRect','fillRect','beginPath','moveTo','lineTo','stroke','fillText','arc','fill']){
 ctx[name]=()=>{if(name in calls)calls[name]++;};
}
const elements={};
const document={getElementById(id){
 return elements[id]||(elements[id]={value:'',textContent:'',width:900,height:390,
 addEventListener(){},getContext(){return ctx}});
}};
const window={};
vm.runInNewContext(process.env.CT_SCRIPT,{document,window,Math,Number,Array,Error,console});
const {rootLocus,assignRoots}=window.ProMathControlTheory;
const b=rootLocus([1],[1,3,2],8,17);
assert.equal(b.length,2);
assert(b.every(branch=>branch.length===17&&branch.every(p=>p.every(Number.isFinite))));
assert(Math.abs(b[0][0][0]+2)<1e-6&&Math.abs(b[1][0][0]+1)<1e-6);
for(const branch of b)assert(Math.abs(branch.at(-1)[0]+1.5)<1e-6);
assert(Math.abs(Math.abs(b[0].at(-1)[1])-Math.sqrt(7.75))<1e-6);
assert(Math.abs(b[0].at(-1)[1]+b[1].at(-1)[1])<1e-6);
const cancel=rootLocus([1,1],[1,3,2],2,11);
assert(cancel.some(branch=>Math.abs(branch.at(-1)[0]+1)<1e-6));
assert(cancel.some(branch=>Math.abs(branch.at(-1)[0]+4)<1e-6));
const cubic=rootLocus([1],[1,6,11,6],2,5);
assert.equal(cubic.length,3);
assert(cubic.every(branch=>branch.length===5));
assert.throws(()=>rootLocus([1,0,0],[1,1]),/numerator degree/);
assert.throws(()=>rootLocus([1],[1,1],-1),/sampling range/);
assert.throws(()=>rootLocus([1],[1,1],2,1),/sampling range/);
assert.throws(()=>assignRoots([[0,0]],[]),/pole count/);
elements['ct-num'].value='1';
elements['ct-den'].value='1, 3, 2';
elements['ct-gain'].value='1';
elements['ct-mode'].value='root';
window.ProMathControlTheory.analyze();
assert.match(elements['ct-status'].textContent,/completed/);
assert.match(elements['ct-output'].textContent,/branch tracking/);
assert(calls.lineTo>100,'must draw tracked branch lines, not only points');
assert(calls.arc>50,'must mark sampled poles');
console.log('root locus branch reference tests passed');
"""
  result=subprocess.run(['node','-e',js],env={**os.environ,'CT_SCRIPT':MATCH.group(1)},capture_output=True,text=True)
  self.assertEqual(result.returncode,0,result.stderr[:2500])

if __name__=='__main__':
 unittest.main()
