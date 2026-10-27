/* ProMathStudio: bounded offline scalar golden-section minimization (unimodal functions). */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('numerical-panel');
if(!M?.numerical?.evaluate||!M?.dataTables||!M?.advanced||!panel)return;
const $=id=>document.getElementById(id), LIMIT=1e12;
function finite(value,label){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(label+' is required.');
 const n=Number(value);
 if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(label+' must be finite and have magnitude at most 1e12.');
 return n;
}
function minimize({expression='(x-2)^2+1',lo=0,hi=4,tolerance=1e-7,maxIterations=200}={}){
 expression=String(expression).trim();
 if(!expression||expression.length>1000)throw Error('Enter an objective expression (1–1000 characters).');
 lo=finite(lo,'Lower bound');hi=finite(hi,'Upper bound');
 if(!(hi>lo)||!Number.isFinite(hi-lo))throw Error('Upper bound must be greater than lower bound with a finite interval.');
 tolerance=finite(tolerance,'Tolerance');
 if(tolerance<1e-10||tolerance>1e-2)throw Error('Tolerance must be between 1e-10 and 1e-2.');
 maxIterations=finite(maxIterations,'Maximum iterations');
 if(!Number.isInteger(maxIterations)||maxIterations<8||maxIterations>2000)
  throw Error('Maximum iterations must be an integer from 8 to 2000.');
 let evaluations=0;
 const f=x=>{
  const y=M.numerical.evaluate(expression,{x});evaluations++;
  if(!Number.isFinite(y)||Math.abs(y)>LIMIT)throw Error('Objective must remain finite with magnitude at most 1e12 throughout the interval.');
  return y;
 };
 const originalMid=lo+(hi-lo)/2;
 const boundaryLeft={x:lo,y:f(lo)},boundaryRight={x:hi,y:f(hi)};
 let a=lo,b=hi;
 const ratio=(Math.sqrt(5)-1)/2;
 let c=b-ratio*(b-a),d=a+ratio*(b-a),fc=f(c),fd=f(d),iterations=0;
 while(b-a>tolerance*Math.max(1,Math.abs(a),Math.abs(b))){
  if(iterations>=maxIterations)throw Error('Minimization iteration budget exceeded; relax tolerance or increase the limit.');
  if(!(a<c&&c<d&&d<b))throw Error('Minimization interval underflow; adjust the bounds or tolerance.');
  if(fc===fd){a=c;b=d;c=b-ratio*(b-a);d=a+ratio*(b-a);fc=f(c);fd=f(d);}
  else if(fc<fd){b=d;d=c;fd=fc;c=b-ratio*(b-a);fc=f(c);}
  else{a=c;c=d;fc=fd;d=a+ratio*(b-a);fd=f(d);}
  iterations++;
 }
 const midpoint=a+(b-a)/2;
 const candidates=[boundaryLeft,boundaryRight,{x:c,y:fc},{x:d,y:fd},{x:midpoint,y:f(midpoint)}];
 candidates.sort((u,v)=>u.y-v.y||Math.abs(u.x-originalMid)-Math.abs(v.x-originalMid));
 const best=candidates[0];
 return {type:'minimize-golden',x:best.x,value:best.y,iterations,evaluations,bracket:[a,b],
  method:'Golden-section bounded scalar minimization',
  note:'Assumes a continuous unimodal objective on the interval. This is a local bounded search, not proof of a global minimum for multimodal/discontinuous functions.'};
}
const area=document.createElement('details');area.id='minimize-details';
area.innerHTML='<summary>1D minimization · golden-section search</summary>'+
 '<p class="graph-data-muted">Find an approximate minimum of a real, continuous, unimodal f(x) on [a,b]. Example: (x-2)^2+1 on [0,4]. Multimodal functions are not guaranteed.</p>'+
 '<div class="num-fields"><label>Objective f(x)<input id="minimize-expression" value="(x-2)^2+1" spellcheck="false"></label>'+
 '<label>Lower bound a<input id="minimize-lo" type="number" step="any" value="0"></label>'+
 '<label>Upper bound b<input id="minimize-hi" type="number" step="any" value="4"></label>'+
 '<label>Tolerance (1e-10–1e-2)<input id="minimize-tolerance" type="number" step="any" value="0.0000001"></label>'+
 '<label>Maximum iterations (8–2000)<input id="minimize-iterations" type="number" min="8" max="2000" step="1" value="200"></label></div>'+
 '<div class="data-toolbar"><button id="minimize-run" class="primary" type="button">Find minimum</button>'+
 '<button id="minimize-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="minimize-output" role="status" aria-live="polite">Enter an objective and finite interval.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#minimize-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px}'+
 '#minimize-details summary{cursor:pointer;color:#3c50ae;font-weight:750}'+
 '#minimize-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:white;border:1px solid #dce5f3;border-radius:10px}'+
 '#minimize-output.error{color:#a82241;background:#fff2f4}';
document.head.append(style);
let last=null;
function invalidate(){last=null;$('minimize-to-table').disabled=true;$('minimize-output').classList.remove('error');}
for(const input of area.querySelectorAll('input')){
 input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);
}
$('minimize-run').addEventListener('click',()=>{
 try{
  last=minimize({expression:$('minimize-expression').value,lo:$('minimize-lo').value,hi:$('minimize-hi').value,
   tolerance:$('minimize-tolerance').value,maxIterations:$('minimize-iterations').value});
  $('minimize-output').classList.remove('error');
  $('minimize-output').textContent=last.method+'\nx ≈ '+last.x.toPrecision(12)+
   '\nf(x) ≈ '+last.value.toPrecision(12)+'\nIterations: '+last.iterations+
   '; evaluations: '+last.evaluations+'\n'+last.note;
  $('minimize-to-table').disabled=false;
 }catch(e){invalidate();$('minimize-output').classList.add('error');$('minimize-output').textContent=e.message;}
});
$('minimize-to-table').addEventListener('click',()=>{
 try{
  if(!last)throw Error('Find a minimum first.');
  M.dataTables.importData({headers:['x','f(x)'],rows:[[last.x,last.value]]},'Numerical_Minimum');
  M.advanced.mode('data');
 }catch(e){$('minimize-output').classList.add('error');$('minimize-output').textContent=e.message;}
});
M.minimizeTools={minimize};
})();
