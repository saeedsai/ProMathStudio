/* ProMathStudio: bounded, offline adaptive implicit TR-BDF2 solver for stiff scalar or
   coupled two-state first-order IVPs. Separate from the explicit RK4/RK45 solvers in
   ode-tools.js. Expressions use the existing safe numeric AST evaluator only. */
(()=>{'use strict';
const M=window.MathStudio, anchor=document.getElementById('ode-details');
if(!M?.numerical?.evaluate||!M?.dataTables||!anchor)return;
const $=id=>document.getElementById(id), MAX=1e12;
// TR-BDF2 (Bank et al. 1985; Hosea & Shampine 1996): gamma=2-sqrt(2), L-stable, order 2.
const GAMMA=2-Math.SQRT2, D=GAMMA/2, W=Math.SQRT2/4;
function finite(value,label){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(label+' is required.');
 const n=Number(value);
 if(!Number.isFinite(n)||Math.abs(n)>MAX)throw Error(label+' must be finite with magnitude at most 1e12.');
 return n;
}
function inRange(value,label,lo,hi){
 const n=finite(value,label);
 if(!(n>=lo&&n<=hi))throw Error(label+' must be between '+lo+' and '+hi+'.');
 return n;
}
function timeResolution(t){
 let delta=Math.max(Number.MIN_VALUE,Math.abs(t)*Number.EPSILON/2);
 while(t+delta===t)delta*=2;
 return (t+delta)-t;
}
const solve2=(a,b,c,d,r0,r1)=>{ // [[a,b],[c,d]] x = r
 const det=a*d-b*c;
 if(!Number.isFinite(det)||Math.abs(det)<1e-300)return null;
 return [(d*r0-b*r1)/det,(a*r1-c*r0)/det];
};
function solve({expression='-1000*(y-cos(t))',expressionZ='',t0=0,t1=1,y0=0,z0=0,
 rtol=1e-6,atol=1e-9,maxSteps=5000,minStep}={}){
 expression=String(expression??'').trim();expressionZ=String(expressionZ??'').trim();
 if(!expression||expression.length>1000)throw Error('Enter dy/dt as a mathematical expression (at most 1,000 characters).');
 if(expressionZ.length>1000)throw Error('dz/dt must be at most 1,000 characters.');
 const n=expressionZ?2:1;
 t0=finite(t0,'Initial time');t1=finite(t1,'End time');
 if(t1===t0)throw Error('End time must differ from initial time.');
 const y=[finite(y0,'Initial y')];if(n===2)y.push(finite(z0,'Initial z'));
 rtol=inRange(rtol,'Relative tolerance',1e-10,0.1);
 atol=inRange(atol,'Absolute tolerance',1e-14,1);
 maxSteps=finite(maxSteps,'Step budget');
 if(!Number.isInteger(maxSteps)||maxSteps<10||maxSteps>20000)throw Error('Step budget must be an integer from 10 to 20000.');
 const span=t1-t0, dir=Math.sign(span), absSpan=Math.abs(span);
 const hmin=Math.max(minStep===undefined||minStep===null||minStep===''?absSpan*1e-12:
  inRange(minStep,'Minimum step',1e-300,absSpan),timeResolution(Math.max(Math.abs(t0),Math.abs(t1)))*4);
 let evaluations=0;
 // Raw derivative; returns null for a non-finite or out-of-bounds value (caller decides).
 const rhs=(t,s)=>{
  evaluations++;
  const env={t,y:s[0],z:n===2?s[1]:0};
  const out=[M.numerical.evaluate(expression,env)];
  if(n===2)out.push(M.numerical.evaluate(expressionZ,env));
  return out.every(v=>Number.isFinite(v)&&Math.abs(v)<=MAX)?out:null;
 };
 let f0;
 try{f0=rhs(t0,y);}catch(error){throw Error('Derivative could not be evaluated at the initial point: '+error.message);}
 if(!f0)throw Error('Derivative is non-finite or exceeds magnitude 1e12 at the initial point.');
 const scale=(a,b)=>a.map((v,i)=>atol+rtol*Math.max(Math.abs(v),Math.abs(b?b[i]:v)));
 const norm=(v,sc)=>Math.sqrt(v.reduce((s,x,i)=>s+(x/sc[i])**2,0)/v.length);
 let jacobianEvaluations=0;
 function jacobian(t,s,fs){
  jacobianEvaluations++;
  const J=[[0,0],[0,0]];
  for(let j=0;j<n;j++){
   const delta=Math.sqrt(Number.EPSILON)*Math.max(1,Math.abs(s[j]));
   const p=s.slice();p[j]+=delta;
   const fp=rhs(t,p);
   if(!fp)return null;
   for(let i=0;i<n;i++)J[i][j]=(fp[i]-fs[i])/delta;
  }
  return J;
 }
 // Solve x = c + dh*f(tc,x) by modified Newton with matrix I - dh*J.
 function newton(tc,c,guess,dh,J,sc){
  const a=1-dh*J[0][0], b=-dh*J[0][1], cc=-dh*J[1][0], d=1-dh*J[1][1];
  let x=guess.slice(), prev=Infinity, fx=null;
  for(let k=0;k<10;k++){
   fx=rhs(tc,x);
   if(!fx)return {fail:'non-finite derivative in Newton iterate'};
   const r=x.map((v,i)=>-(v-c[i]-dh*fx[i]));
   let dx;
   if(n===1){if(!Number.isFinite(a)||Math.abs(a)<1e-300)return {fail:'singular Newton matrix'};dx=[r[0]/a];}
   else{dx=solve2(a,b,cc,d,r[0],r[1]);if(!dx)return {fail:'singular Newton matrix'};}
   x=x.map((v,i)=>v+dx[i]);
   if(!x.every(v=>Number.isFinite(v)&&Math.abs(v)<=MAX))return {fail:'Newton iterate became non-finite'};
   const size=norm(dx,sc), rate=k>0?size/prev:0;
   if(!Number.isFinite(size))return {fail:'Newton iterate became non-finite'};
   if(k>0&&rate>0.9)return {fail:'Newton iteration diverged'};
   if(size<=1e-3||(k>0&&size*rate/(1-rate)<=1e-2)){
    fx=rhs(tc,x);
    if(!fx)return {fail:'non-finite derivative at Newton solution'};
    return {x,fx};
   }
   prev=size;
  }
  return {fail:'Newton iteration did not converge in 10 iterations'};
 }
 let t=t0, s=y.slice(), fs=f0, J=jacobian(t,s,fs);
 if(!J)throw Error('Finite-difference Jacobian is non-finite at the initial point.');
 // Initial step heuristic (Hairer–Wanner style), bounded by span and minimum step.
 const sc0=scale(s), d0=norm(s,sc0), d1=norm(fs,sc0);
 let h=(d0<1e-5||d1<1e-5)?1e-6*absSpan:0.01*d0/d1;
 h=Math.min(Math.max(h,hmin),absSpan/10);
 const rows=[[t0,...s]];
 let accepted=0,rejected=0,newtonFailures=0,attempts=0,maxErrorRatio=0,maxLocalError=0,
  minAccepted=Infinity,maxAccepted=0,justRejected=false;
 while(dir*(t1-t)>0){
  if(attempts>=maxSteps)throw Error('Step budget of '+maxSteps+' attempts exhausted at t='+t.toPrecision(10)+
   ' (accepted '+accepted+', rejected '+rejected+'); raise the budget, loosen tolerances or shorten the interval.');
  attempts++;
  let step=Math.min(h,Math.abs(t1-t));
  if(Math.abs(t1-(t+dir*step))<hmin)step=Math.abs(t1-t); // avoid a sliver final step
  const hs=dir*step, tg=t+GAMMA*hs, tn=(Math.abs(t1-t)===step)?t1:t+hs;
  const sc=scale(s), dh=D*hs;
  // Stage 1: trapezoidal rule to t+gamma*h. Stage 2: BDF2 to t+h (same Newton matrix).
  const c1=s.map((v,i)=>v+dh*fs[i]);
  const st1=newton(tg,c1,s.map((v,i)=>v+GAMMA*hs*fs[i]),dh,J,sc);
  let st2=null;
  if(!st1.fail){
   const c2=s.map((v,i)=>v+hs*W*(fs[i]+st1.fx[i]));
   const guess=s.map((v,i)=>v+(st1.x[i]-v)/GAMMA);
   st2=newton(tn,c2,guess,dh,J,sc);
  }
  const fail=st1.fail||st2.fail;
  if(fail){
   newtonFailures++;rejected++;justRejected=true;
   if(step<=hmin)throw Error('Newton iteration failed at t='+t.toPrecision(10)+' with the minimum step '+
    hmin.toPrecision(3)+' ('+fail+'); the problem may blow up, be singular or need looser tolerances.');
   h=Math.max(step/4,hmin);continue;
  }
  const yn=st2.x, fn=st2.fx;
  // Embedded third-order comparison, filtered by (I - dh*J)^-1 to damp stiff components.
  const raw=s.map((_,i)=>hs*((1-4*W)/3*fs[i]+st1.fx[i]/3-2*D/3*fn[i]));
  let est;
  if(n===1){est=[raw[0]/(1-dh*J[0][0])];}
  else est=solve2(1-dh*J[0][0],-dh*J[0][1],-dh*J[1][0],1-dh*J[1][1],raw[0],raw[1])||raw;
  if(!est.every(Number.isFinite))est=raw;
  const ratio=norm(est,scale(s,yn));
  if(!Number.isFinite(ratio)){
   rejected++;justRejected=true;
   if(step<=hmin)throw Error('Non-finite local error estimate at t='+t.toPrecision(10)+' with the minimum step.');
   h=Math.max(step/4,hmin);continue;
  }
  if(ratio>1){
   rejected++;justRejected=true;
   if(step<=hmin)throw Error('Step size underflow at t='+t.toPrecision(10)+': the local error estimate still exceeds tolerance at the minimum step '+
    hmin.toPrecision(3)+'; the solution may be singular or blowing up.');
   h=Math.max(step*Math.max(0.2,0.9*ratio**(-1/3)),hmin);continue;
  }
  accepted++;
  maxErrorRatio=Math.max(maxErrorRatio,ratio);
  maxLocalError=Math.max(maxLocalError,...est.map(Math.abs));
  minAccepted=Math.min(minAccepted,step);maxAccepted=Math.max(maxAccepted,step);
  t=tn;s=yn;fs=fn;rows.push([t,...s]);
  const grow=ratio===0?5:Math.min(5,Math.max(0.2,0.9*ratio**(-1/3)));
  h=Math.max(step*(justRejected?Math.min(grow,1):grow),hmin);justRejected=false;
  if(dir*(t1-t)>0){J=jacobian(t,s,fs);if(!J)throw Error('Finite-difference Jacobian became non-finite at t='+t.toPrecision(10)+'.');}
 }
 return {type:'ode-tr-bdf2',columns:n===2?['t','y','z']:['t','y'],rows,states:n,
  accepted,rejected,newtonFailures,attempts,jacobianEvaluations,functionEvaluations:evaluations,
  maxErrorRatio,maxLocalError,minAcceptedStep:minAccepted,maxAcceptedStep:maxAccepted,
  rtol,atol,maxSteps,minStep:hmin,
  method:'Adaptive implicit TR-BDF2 (L-stable, order 2) with modified Newton on a finite-difference Jacobian',
  note:(n===2?'Two coupled real equations y′=f(t,y,z), z′=g(t,y,z)':'Scalar y′=f(t,y)')+
   '; forward or backward. Local error estimates are heuristic (filtered embedded order-3 comparison), not certified global error bounds.'};
}

const area=document.createElement('details');area.id='stiff-ode-details';
area.innerHTML='<summary>Stiff ODE initial-value problem · implicit adaptive TR-BDF2</summary>'+
 '<p class="graph-data-muted">For stiff problems where explicit RK4/RK45 need tiny steps. Leave dz/dt empty for a scalar equation. Example: dy/dt=-1000*(y-cos(t)), y(0)=0.</p>'+
 '<div class="num-fields">'+
 '<label>Derivative dy/dt<input id="stiff-ode-dy" value="-1000*(y-cos(t))" spellcheck="false"></label>'+
 '<label>Optional dz/dt (two-state system)<input id="stiff-ode-dz" value="" spellcheck="false" placeholder="leave empty for scalar"></label>'+
 '<label>Initial time t₀<input id="stiff-ode-t0" type="number" step="any" value="0"></label>'+
 '<label>End time t₁<input id="stiff-ode-t1" type="number" step="any" value="1"></label>'+
 '<label>Initial y(t₀)<input id="stiff-ode-y0" type="number" step="any" value="0"></label>'+
 '<label>Initial z(t₀)<input id="stiff-ode-z0" type="number" step="any" value="0"></label>'+
 '<label>Relative tolerance (1e-10–0.1)<input id="stiff-ode-rtol" type="number" step="any" value="0.000001"></label>'+
 '<label>Absolute tolerance (1e-14–1)<input id="stiff-ode-atol" type="number" step="any" value="0.000000001"></label>'+
 '<label>Step budget (10–20000)<input id="stiff-ode-max-steps" type="number" min="10" max="20000" step="1" value="5000"></label></div>'+
 '<div class="data-toolbar"><button id="stiff-ode-run" type="button" class="primary">Solve stiff IVP</button>'+
 '<button id="stiff-ode-to-table" type="button" class="secondary" disabled>Save to Data Tables</button></div>'+
 '<pre id="stiff-ode-output" role="status" aria-live="polite">Enter the derivative(s), initial values and tolerances.</pre>';
anchor.after(area);
const style=document.createElement('style');
style.textContent='#stiff-ode-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px;max-width:100%;box-sizing:border-box}'+
 '#stiff-ode-details summary{cursor:pointer;color:#3c50ae;font-weight:750;min-height:40px;display:flex;align-items:center}'+
 '#stiff-ode-details .num-fields{min-width:0}#stiff-ode-details label{min-width:0}'+
 '#stiff-ode-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px;max-width:100%;box-sizing:border-box}'+
 '#stiff-ode-output.error{color:#a82241;background:#fff2f4}'+
 '#stiff-ode-details button,#stiff-ode-details input{min-height:40px}'+
 '@media(max-width:480px){#stiff-ode-details .num-fields{grid-template-columns:1fr}}';
document.head.append(style);
let last=null;
const output=$('stiff-ode-output'), toTable=$('stiff-ode-to-table');
function invalidate(){
 last=null;toTable.disabled=true;
 output.classList.remove('error');output.textContent='Enter the derivative(s), initial values and tolerances.';
}
for(const input of area.querySelectorAll('input')){input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);}
function fail(error){
 last=null;toTable.disabled=true;
 output.classList.add('error');
 output.textContent=error.message+'\nRecovery: check the expressions and inputs, loosen the tolerances, raise the step budget or shorten the interval, then press Solve again.';
}
function run(){
 try{
  last=solve({expression:$('stiff-ode-dy').value,expressionZ:$('stiff-ode-dz').value,
   t0:$('stiff-ode-t0').value,t1:$('stiff-ode-t1').value,y0:$('stiff-ode-y0').value,
   z0:$('stiff-ode-z0').value,rtol:$('stiff-ode-rtol').value,atol:$('stiff-ode-atol').value,
   maxSteps:$('stiff-ode-max-steps').value});
  const end=last.rows[last.rows.length-1];
  output.classList.remove('error');
  output.textContent=last.method+'\n'+last.rows.length+' output rows; accepted '+last.accepted+', rejected '+last.rejected+
   ' (Newton failures '+last.newtonFailures+'), Jacobian evaluations '+last.jacobianEvaluations+
   ', derivative evaluations '+last.functionEvaluations+'\naccepted |Δt| '+last.minAcceptedStep.toPrecision(4)+'–'+
   last.maxAcceptedStep.toPrecision(4)+', max scaled local-error estimate '+last.maxErrorRatio.toPrecision(4)+
   ', max |local-error estimate| '+last.maxLocalError.toPrecision(4)+'\ny('+end[0].toPrecision(10)+') ≈ '+end[1].toPrecision(12)+
   (last.states===2?', z ≈ '+end[2].toPrecision(12):'')+'\n'+last.note;
  toTable.disabled=false;
 }catch(error){fail(error);}
}
$('stiff-ode-run').addEventListener('click',run);
toTable.addEventListener('click',()=>{
 try{
  if(!last)throw Error('Solve a stiff initial-value problem first.');
  M.dataTables.importData({headers:last.columns,rows:last.rows},last.states===2?'ODE_TRBDF2_SYSTEM':'ODE_TRBDF2');
  M.advanced?.mode?.('data');
 }catch(error){fail(error);}
});
M.stiffOde={solve,run,method:'tr-bdf2'};
})();
