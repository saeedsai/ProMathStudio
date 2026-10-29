"""Numerical control-theory references executed against the actual browser JavaScript."""
from pathlib import Path
import json
import re
import subprocess
import unittest

HTML=(Path(__file__).resolve().parents[1]/"index.html").read_text(encoding="utf-8")
MATCH=re.search(r'<script id="promath-control-theory">([\s\S]*?)</script>',HTML)
class ControlNumericalReference(unittest.TestCase):
 def test_continuous_time_references(self):
  self.assertIsNotNone(MATCH)
  js=r"""
const assert=require('node:assert/strict');
const vm=require('node:vm');
const script=process.env.CT_SCRIPT;
const elements={};
const ctx={};
for(const method of ['clearRect','fillRect','beginPath','moveTo','lineTo','stroke','fillText','arc','fill'])ctx[method]=()=>{};
const document={getElementById(id){
 if(!elements[id])elements[id]={value:'',textContent:'',addEventListener(){},getContext(){return ctx},width:900,height:390};
 return elements[id];
}};
const window={};
vm.runInNewContext(script,{document,window,Math,Number,Array,Error,console});
const {response,routh,roots,coefficients,analyze}=window.ProMathControlTheory;
const z=response([1],[1,1],1,1);
assert(Math.abs(z[0]-.5)<1e-12 && Math.abs(z[1]+.5)<1e-12);
assert(Math.abs(20*Math.log10(Math.hypot(...z))+3.01029995664)<1e-8);
const zn=response([1],[1,1],1,-1);
assert(Math.abs(zn[0]-z[0])<1e-12 && Math.abs(zn[1]+z[1])<1e-12);
assert.equal(routh([1,3,2]).changes,0);
assert.equal(routh([1,-1,-2]).changes,1);
const r=roots([1,3,2]).map(p=>p[0]).sort((a,b)=>a-b);
assert(Math.abs(r[0]+2)<1e-6 && Math.abs(r[1]+1)<1e-6);
assert.throws(()=>coefficients('1, Infinity'));
assert.throws(()=>coefficients('0 1 2'));
elements['ct-num'].value='1';
elements['ct-den'].value='1, 1';
elements['ct-gain'].value='1';
elements['ct-mode'].value='feedback';
analyze();
assert(elements['ct-output'].textContent.includes('Characteristic polynomial: 1, 2'));
assert(elements['ct-status'].textContent.includes('completed'));
console.log('control references passed');
"""
  import os
  env={**os.environ,'CT_SCRIPT':MATCH.group(1)}
  p=subprocess.run(['node','-e',js],capture_output=True,text=True,env=env)
  self.assertEqual(p.returncode,0,p.stderr[:1800])
if __name__=='__main__':unittest.main()
