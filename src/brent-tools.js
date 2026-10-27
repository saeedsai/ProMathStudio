/* Offline bounded Brent-Dekker root refinement; uses the shared safe numeric evaluator. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');if(!M?.numerical?.evaluate||!M?.dataTables||!panel)return;
const $=id=>document.getElementById(id), LIMIT=1e12;
function number(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');const n=Number(value);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(name+' must be finite and at most 1e12 in magnitude.');return n;}
function refine({expression='x^3-x-2',lo=1,hi=2,tolerance=1e-9,maxIterations=120}={}){
 expression=String(expression).trim();if(!expression||expression.length>1000)throw Error('Enter a residual expression of 1–1000 characters.');
 lo=number(lo,'Lower bound');hi=number(hi,'Upper bound');if(!(hi>lo))throw Error('Upper bound must exceed lower bound.');
 tolerance=number(tolerance,'Tolerance');if(tolerance<1e-12||tolerance>1e-2)throw Error('Tolerance must be between 1e-12 and 1e-2.');
 maxIterations=number(maxIterations,'Maximum iterations');if(!Number.isInteger(maxIterations)||maxIterations<8||maxIterations>2000)throw Error('Maximum iterations must be an integer from 8 to 2000.');
 let evaluations=0;
 const f=x=>{const y=M.numerical.evaluate(expression,{x});evaluations++;if(!Number.isFinite(y)||Math.abs(y)>LIMIT)throw Error('Residual must be finite and at most 1e12 in magnitude.');return y;};
 let a=lo,b=hi,fa=f(a),fb=f(b),iterations=0;
 const result=(x,residual,bracket)=>({type:'root-brent',x,residual,iterations,evaluations,bracket,method:'Brent-Dekker bracketed root refinement',note:'Requires continuity and opposite endpoint signs; not a proof of uniqueness or exhaustive search.'});
 if(fa===0)return result(a,fa,[lo,hi]);if(fb===0)return result(b,fb,[lo,hi]);
 if(Math.sign(fa)===Math.sign(fb))throw Error('Endpoints must have opposite residual signs or an exact endpoint root.');
 const scale=Math.max(1,Math.min(Math.abs(fa),Math.abs(fb)));
 let c=a,fc=fa,d=b-a,e=d;
 for(let it=0;it<maxIterations;it++){
  if((fb>0&&fc>0)||(fb<0&&fc<0)){c=a;fc=fa;d=e=b-a;}
  if(Math.abs(fc)<Math.abs(fb)){const oldB=b,oldFb=fb;a=oldB;b=c;c=oldB;fa=oldFb;fb=fc;fc=oldFb;}
  const tol=2*Number.EPSILON*Math.abs(b)+tolerance/2,half=(c-b)/2;
  if(Math.abs(half)<=tol||fb===0){
   if(Math.abs(fb)>Math.sqrt(tolerance)*scale)throw Error('Bracket collapsed with a large residual; suspected discontinuity.');
   return result(b,fb,[Math.min(b,c),Math.max(b,c)]);
  }
  if(Math.abs(e)>=tol&&Math.abs(fa)>Math.abs(fb)){
   const s=fb/fa;let p,q;
   if(a===c){p=2*half*s;q=1-s;}
   else{const q0=fa/fc,r=fb/fc;p=s*(2*half*q0*(q0-r)-(b-a)*(r-1));q=(q0-1)*(r-1)*(s-1);}
   if(p>0)q=-q;p=Math.abs(p);
   if(q!==0&&Number.isFinite(p)&&Number.isFinite(q)&&2*p<Math.min(3*half*q-Math.abs(tol*q),Math.abs(e*q))){e=d;d=p/q;}
   else{d=half;e=half;}
  }else{d=half;e=half;}
  a=b;fa=fb;const step=Math.abs(d)>tol?d:(half>0?tol:-tol);
  if(b+step===b)throw Error('Root refinement reached machine precision.');b+=step;fb=f(b);iterations=it+1;
 }
 throw Error('Root refinement iteration budget exceeded.');
}
const area=document.createElement('details');area.id='brent-details';
area.innerHTML='<summary>Bracketed root · Brent-Dekker</summary><p>Find one real root of a continuous residual f(x)=0 with opposite endpoint signs.</p>'+
 '<div class="num-fields"><label>Residual f(x)<input id="brent-expression" value="x^3-x-2"></label>'+
 '<label>Lower bound<input id="brent-lo" type="number" step="any" value="1"></label>'+
 '<label>Upper bound<input id="brent-hi" type="number" step="any" value="2"></label>'+
 '<label>Tolerance<input id="brent-tolerance" type="number" step="any" value="0.000000001"></label>'+
 '<label>Maximum iterations<input id="brent-iterations" type="number" step="1" value="120"></label></div>'+
 '<div class="data-toolbar"><button id="brent-run" class="primary" type="button">Refine root</button>'+
 '<button id="brent-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="brent-output" role="status" aria-live="polite">Enter a sign-changing bracket.</pre>';
panel.append(area);let last=null;
const invalidate=()=>{last=null;$('brent-to-table').disabled=true;$('brent-output').classList.remove('error');};
for(const input of area.querySelectorAll('input')){input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);}
$('brent-run').addEventListener('click',()=>{
 try{last=refine({expression:$('brent-expression').value,lo:$('brent-lo').value,hi:$('brent-hi').value,tolerance:$('brent-tolerance').value,maxIterations:$('brent-iterations').value});
 $('brent-output').classList.remove('error');$('brent-output').textContent=last.method+'\nx = '+last.x.toPrecision(12)+'\nResidual = '+last.residual.toExponential(3)+'\nIterations: '+last.iterations+'; evaluations: '+last.evaluations+'\n'+last.note;$('brent-to-table').disabled=false;
 }catch(err){invalidate();$('brent-output').classList.add('error');$('brent-output').textContent=err.message;}
});
$('brent-to-table').addEventListener('click',()=>{try{if(!last)throw Error('Refine a root first.');M.dataTables.importData({headers:['x','residual'],rows:[[last.x,last.residual]]},'Numerical_Root_Brent');M.advanced.mode('data');}catch(err){$('brent-output').textContent=err.message;}});
M.brentTools={refine};
})();
