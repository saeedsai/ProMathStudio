/* ProMathStudio: bounded, offline scalar first-order IVP solver (classical RK4).
   Uses the existing safe numeric AST evaluator, not eval or user code. */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('numerical-panel');
if(!M?.numerical?.evaluate||!M?.dataTables||!panel)return;
const $=id=>document.getElementById(id), MAX=1e12;
function finite(value,label){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(label+' is required.');
 const n=Number(value);
 if(!Number.isFinite(n)||Math.abs(n)>MAX)throw Error(label+' must be finite with magnitude at most 1e12.');
 return n;
}
function bounded(value,label){
 if(!Number.isFinite(value)||Math.abs(value)>MAX)throw Error(label+' became non-finite or exceeded magnitude 1e12; shorten the interval or change the initial value.');
 return value;
}
function timeResolution(t,direction){
 let delta=Math.max(Number.MIN_VALUE,Math.abs(t)*Number.EPSILON/2);
 while(t+direction*delta===t)delta*=2;
 return Math.abs((t+direction*delta)-t);
}
function rk4TimeGrid(t,next,h){
 const direction=Math.sign(h), midpoint=t+h/2;
 if(!(direction*(next-t)>0)||midpoint===t||midpoint===next)
  throw Error('Fixed-step RK4 time resolution is insufficient: output times or midpoint stages collapse; use fewer steps or rescale time.');
}
function solve({expression='y',t0=0,t1=1,y0=1,steps=40}={},refining=false){
 expression=String(expression).trim();
 if(!expression||expression.length>1000)throw Error('Enter dy/dt as a mathematical expression (at most 1,000 characters).');
 t0=finite(t0,'Initial time');t1=finite(t1,'End time');y0=finite(y0,'Initial y');
 if(t1===t0)throw Error('End time must differ from initial time.');
 steps=finite(steps,'Time steps');
 if(!Number.isInteger(steps)||steps<4||steps>1000)throw Error('Time steps must be an integer from 4 to 1000.');
 const h=(t1-t0)/steps;
 if(!Number.isFinite(h)||h===0)throw Error('Invalid integration step size.');
 const f=(t,y)=>bounded(M.numerical.evaluate(expression,{t:bounded(t,'Time'),y:bounded(y,'State')}),'Derivative');
 let y=y0;const rows=[];
 for(let i=0;i<=steps;i++){
  const t=bounded(i===steps?t1:t0+i*h,'Time');
  if(i<steps)rk4TimeGrid(t,bounded(i+1===steps?t1:t0+(i+1)*h,'Time'),h);
  rows.push([t,y]);
  if(i===steps)break;
  const k1=f(t,y);
  const k2=f(t+h/2,y+h*k1/2);
  const k3=f(t+h/2,y+h*k2/2);
  const k4=f(t+h,y+h*k3);
  y=bounded(y+(h/6)*(k1+2*k2+2*k3+k4),'State');
 }
 // Step-doubling diagnostic (not a global error bound): compare against a 2N-step run, N<=500.
 let convergence=null;
 if(!refining&&steps<=500){
  try{
   const fine=solve({expression,t0,t1,y0,steps:steps*2},true).rows.at(-1);
   convergence={refinedSteps:steps*2,endpointDifference:Math.abs(rows.at(-1)[1]-fine[1])};
  }catch(refinementError){convergence=null;} // an unresolvable refined grid must not fail a valid solve
 }
 return {type:'ode-rk4',columns:['t','y'],rows,steps,h,convergence,
  method:'Classical fourth-order Runge–Kutta (RK4)',
  note:'Scalar first-order y\u2032=f(t,y), y(t0)=y0; fixed steps, forward or backward. Accuracy depends on smoothness and step size. Not an adaptive/stiff ODE solver.'};
}

function solveAdaptive({expression='y',t0=0,t1=1,y0=1,tolerance=1e-7,maxSteps=1000}={}){
 expression=String(expression).trim();
 if(!expression||expression.length>1000)throw Error('Enter dy/dt as a mathematical expression (at most 1,000 characters).');
 t0=finite(t0,'Initial time');t1=finite(t1,'End time');y0=finite(y0,'Initial y');
 if(t1===t0)throw Error('End time must differ from initial time.');
 tolerance=finite(tolerance,'Tolerance');
 if(tolerance<1e-12||tolerance>1e-2)throw Error('Tolerance must be between 1e-12 and 1e-2.');
 maxSteps=finite(maxSteps,'Maximum attempts');
 if(!Number.isInteger(maxSteps)||maxSteps<4||maxSteps>10000)throw Error('Maximum attempts must be an integer from 4 to 10000.');
 const span=t1-t0, direction=Math.sign(span);
 if(!Number.isFinite(span)||!direction)throw Error('Invalid integration interval.');
 function stageBound(value,label,stage){
  if(!Number.isFinite(value)||Math.abs(value)>MAX){
   const error=Error(label+' became non-finite or exceeded magnitude 1e12; shorten the interval or change the initial value.');
   // A nonfinite derivative may be a domain/singularity error: never retry it.
   error.code=label==='Derivative'&&!Number.isFinite(value)?'RK45_DOMAIN_NONFINITE':'RK45_STAGE_BOUND';
   error.stage=stage;
   throw error;
  }
  return value;
 }
 const f=(t,y,stage)=>{
  try{
   return stageBound(M.numerical.evaluate(expression,{t:stageBound(t,'Time',stage),y:stageBound(y,'State',stage)}),'Derivative',stage);
  }catch(error){
   const wrapped=Error('RK45 '+stage+' derivative failed at t='+Number(t).toPrecision(10)+
    ', y='+Number(y).toPrecision(10)+': '+(error?.message||String(error)));
   wrapped.code=error?.code;wrapped.stage=stage;
   throw wrapped;
  }
 };
 let t=t0,y=y0,h=span/20,attempts=0,rejected=0,accepted=0;
 let minAcceptedStep=Infinity,maxAcceptedStep=0,maxAcceptedErrorRatio=0;
 let maxRejectedErrorRatio=0,minRejectedStep=Infinity,resolutionLimitedAttempts=0;
 let stageTimeCollisionAttempts=0,stageTimeCollisionAcceptedSteps=0;
 let quantumLimitedAcceptedSteps=0;
 let consecutiveRejected=0,maxConsecutiveRejected=0,stageOverflowRejected=0,lastOverflowStage=null;
 // Include the last representable time and accepted/rejected work in failure reports.
 // This is deliberately a diagnostic only: it does not change RK45 step selection.
 const progressError=reason=>Error(reason+'; at t='+t.toPrecision(16)+
  ', target='+t1.toPrecision(16)+', attempted step='+h.toPrecision(8)+
  '; attempts='+attempts+'/'+maxSteps+', accepted='+accepted+
  ', rejected='+rejected+', tolerance='+tolerance+
  (rejected?', max rejected local-error ratio='+maxRejectedErrorRatio.toPrecision(6)+
   ', smallest rejected |Δt|='+minRejectedStep.toPrecision(8):'')+
  ', time-resolution-limited attempts='+resolutionLimitedAttempts+
  ', collapsed-stage attempts='+stageTimeCollisionAttempts+
  ', longest rejection streak='+maxConsecutiveRejected+
  ', bounded stage-overflow retries='+stageOverflowRejected+
  (lastOverflowStage?', last bounded stage='+lastOverflowStage:'')+'.');
 const rows=[[t,y]];
 while(direction*(t1-t)>0){
  if(attempts>=maxSteps)throw progressError('Adaptive solver exceeded maximum attempts; relax tolerance or increase the limit');
  const remaining=t1-t;
  h=direction*Math.min(Math.abs(h),Math.abs(remaining));
  if(!(direction*h>0))throw progressError('Adaptive step size underflow; shorten the interval or relax tolerance');
  const quantum=timeResolution(t,direction);
  let nextT=t+h;
  if(nextT===t){nextT=t+direction*quantum;resolutionLimitedAttempts++;}
  if(direction*(nextT-t1)>0)nextT=t1;
  h=nextT-t;
  if(!(direction*h>0))throw progressError('Adaptive step size underflow at current time resolution; rescale time or relax tolerance');
  // Fractional Dormand–Prince stages may round back to t even when t+h advances.
  // Keep the numerical result but flag this loss of representable stage times.
  const stageTimesCollapsed=(t+h/5===t||t+3*h/10===t||
   t+4*h/5===t||t+8*h/9===t);
  if(stageTimesCollapsed)stageTimeCollisionAttempts++;
  attempts++;
  let y5,y4;
  try{
  const k1=f(t,y,'k1');
  const k2=f(t+h/5,y+h*k1/5,'k2');
  const k3=f(t+3*h/10,y+h*(3*k1/40+9*k2/40),'k3');
  const k4=f(t+4*h/5,y+h*(44*k1/45-56*k2/15+32*k3/9),'k4');
  const k5=f(t+8*h/9,y+h*(19372*k1/6561-25360*k2/2187+64448*k3/6561-212*k4/729),'k5');
  const k6=f(t+h,y+h*(9017*k1/3168-355*k2/33+46732*k3/5247+49*k4/176-5103*k5/18656),'k6');
  y5=stageBound(y+h*(35*k1/384+500*k3/1113+125*k4/192-2187*k5/6784+11*k6/84),'State','y5');
  const k7=f(t+h,y5,'k7');
  y4=stageBound(y+h*(5179*k1/57600+7571*k3/16695+393*k4/640-92097*k5/339200+187*k6/2100+k7/40),'State','y4');
  }catch(error){
   // Structured bounds tagging prevents parser/domain messages that happen to
   // contain the same words from being mistaken for recoverable overflow.
   if(error?.code!=='RK45_STAGE_BOUND'||error.stage==='k1')throw error;
   lastOverflowStage=error.stage||'intermediate state';
   rejected++;stageOverflowRejected++;consecutiveRejected++;
   minRejectedStep=Math.min(minRejectedStep,Math.abs(h));
   maxConsecutiveRejected=Math.max(maxConsecutiveRejected,consecutiveRejected);
   if(Math.abs(h)<=quantum)throw progressError('Adaptive stage overflow at current time resolution; rescale state or shorten the interval');
   h*=0.5;
   continue;
  }
  const error=Math.abs(y5-y4),scale=tolerance*(1+Math.max(Math.abs(y),Math.abs(y5)));
  const errorRatio=error/scale;
  if(!Number.isFinite(errorRatio))throw progressError('RK45 local-error estimate is not finite');
  if(errorRatio<=1){
   consecutiveRejected=0;
   const acceptedStep=Math.abs(h);
   minAcceptedStep=Math.min(minAcceptedStep,acceptedStep);
   maxAcceptedStep=Math.max(maxAcceptedStep,acceptedStep);
   maxAcceptedErrorRatio=Math.max(maxAcceptedErrorRatio,errorRatio);
   // Never publish duplicate or non-monotone times to Data Tables/Graphs.
   if(!(direction*(nextT-t)>0))throw progressError('RK45 accepted time grid failed to advance');
   if(Math.abs(nextT-t)<=quantum)quantumLimitedAcceptedSteps++;
   t=nextT;
   y=y5;rows.push([t,y]);accepted++;
   if(stageTimesCollapsed)stageTimeCollisionAcceptedSteps++;
  }else{
   rejected++;
   consecutiveRejected++;
   maxConsecutiveRejected=Math.max(maxConsecutiveRejected,consecutiveRejected);
   maxRejectedErrorRatio=Math.max(maxRejectedErrorRatio,errorRatio);
   minRejectedStep=Math.min(minRejectedStep,Math.abs(h));
   if(Math.abs(h)<=quantum)throw progressError('Adaptive step size underflow at current time resolution; rescale time or relax tolerance');
  }
  const factor=error===0?5:Math.max(0.2,Math.min(5,0.9*Math.pow(scale/error,0.2)));
  h=bounded(h*factor,'Step size');
 }
 return {type:'ode-rk45',columns:['t','y'],rows,steps:accepted,attempts,rejected,tolerance,
  minAcceptedStep,maxAcceptedStep,maxAcceptedErrorRatio,maxRejectedErrorRatio,
  minRejectedStep:rejected?minRejectedStep:null,resolutionLimitedAttempts,
  stageTimeCollisionAttempts,stageTimeCollisionAcceptedSteps,quantumLimitedAcceptedSteps,
  maxConsecutiveRejected,stageOverflowRejected,lastOverflowStage,
  rejectionWarning:rejected>=5||maxConsecutiveRejected>=3?
   'Repeated RK45 step rejections: verify accuracy with tighter tolerance or a stiff-capable solver; rejection alone does not diagnose stiffness.':null,
  method:'Adaptive Dormand–Prince Runge–Kutta 5(4) (RK45)',
  note:'Scalar first-order y\u2032=f(t,y), forward or backward. Local error controlled; not stiff, vector-valued or globally error-certified.'};
}


function solveSystem({expression='z',expressionZ='-y',t0=0,t1=1,y0=0,z0=1,steps=80}={},refining=false){
 expression=String(expression).trim();expressionZ=String(expressionZ).trim();
 if(!expression||!expressionZ||expression.length>1000||expressionZ.length>1000)
  throw Error('Enter both dy/dt and dz/dt expressions (1–1,000 characters each).');
 t0=finite(t0,'Initial time');t1=finite(t1,'End time');
 y0=finite(y0,'Initial y');z0=finite(z0,'Initial z');
 if(t1===t0)throw Error('End time must differ from initial time.');
 steps=finite(steps,'Time steps');
 if(!Number.isInteger(steps)||steps<4||steps>1000)throw Error('Time steps must be an integer from 4 to 1000.');
 const h=(t1-t0)/steps;
 if(!Number.isFinite(h)||h===0)throw Error('Invalid integration step size.');
 const f=(t,y,z)=>{
  const variables={t:bounded(t,'Time'),y:bounded(y,'State y'),z:bounded(z,'State z')};
  return [
   bounded(M.numerical.evaluate(expression,variables),'Derivative dy/dt'),
   bounded(M.numerical.evaluate(expressionZ,variables),'Derivative dz/dt')
  ];
 };
 let y=y0,z=z0;const rows=[];
 for(let i=0;i<=steps;i++){
  const t=bounded(i===steps?t1:t0+i*h,'Time');
  if(i<steps)rk4TimeGrid(t,bounded(i+1===steps?t1:t0+(i+1)*h,'Time'),h);
  rows.push([t,y,z]);
  if(i===steps)break;
  const k1=f(t,y,z);
  const k2=f(t+h/2,y+h*k1[0]/2,z+h*k1[1]/2);
  const k3=f(t+h/2,y+h*k2[0]/2,z+h*k2[1]/2);
  const k4=f(t+h,y+h*k3[0],z+h*k3[1]);
  y=bounded(y+h*(k1[0]+2*k2[0]+2*k3[0]+k4[0])/6,'State y');
  z=bounded(z+h*(k1[1]+2*k2[1]+2*k3[1]+k4[1])/6,'State z');
 }
 // Step-doubling diagnostic (not a global error bound): compare against a 2N-step run, N<=500.
 let convergence=null;
 if(!refining&&steps<=500){
  try{
   const fine=solveSystem({expression,expressionZ,t0,t1,y0,z0,steps:steps*2},true).rows.at(-1);
   const end=rows.at(-1);
   convergence={refinedSteps:steps*2,endpointDifference:Math.max(Math.abs(end[1]-fine[1]),Math.abs(end[2]-fine[2]))};
  }catch(refinementError){
   // The refined grid can be unresolvable even when the requested one is valid; never fail the solve for a diagnostic.
   convergence=null;
  }
 }
 return {type:'ode-rk4-system',columns:['t','y','z'],rows,steps,h,convergence,
  method:'Coupled two-state classical Runge–Kutta (RK4)',
  note:'Two real first-order equations y\u2032=f(t,y,z), z\u2032=g(t,y,z); fixed-step forward or backward IVP. Not adaptive, stiff or error-certified.'};
}

const area=document.createElement('details');area.id='ode-details';
area.innerHTML='<summary>ODE initial-value problem · scalar RK4 / RK45 or coupled RK4</summary>'+
 '<p class="graph-data-muted">Solve scalar dy/dt=f(t,y), or two coupled equations dy/dt=f(t,y,z), dz/dt=g(t,y,z). RK4 uses fixed steps; scalar RK45 adapts its step size. Example: dy/dt=z, dz/dt=-y, y(0)=0, z(0)=1.</p>'+
 '<div class="num-fields"><label>Method<select id="ode-method"><option value="rk4">Fixed-step RK4</option><option value="rk45">Adaptive RK45</option><option value="rk4-system">Coupled two-state RK4</option></select></label>'+ 
 '<label>Derivative dy/dt<input id="ode-expression" value="y" spellcheck="false"></label>'+ 
 '<label id="ode-system-derivative-label" hidden>Derivative dz/dt<input id="ode-system-derivative" value="-y" spellcheck="false"></label>'+
 '<label>Initial time t₀<input id="ode-start" type="number" step="any" value="0"></label>'+
 '<label>End time t₁<input id="ode-end" type="number" step="any" value="1"></label>'+
 '<label>Initial y(t₀)<input id="ode-initial" type="number" step="any" value="1"></label>'+ 
 '<label id="ode-system-initial-label" hidden>Initial z(t₀)<input id="ode-system-initial" type="number" step="any" value="1"></label>'+
 '<label>RK4 steps (4–1000)<input id="ode-steps" type="number" min="4" max="1000" step="1" value="40"></label>'+ 
 '<label>RK45 tolerance (1e-12–1e-2)<input id="ode-tolerance" type="number" step="any" value="0.0000001"></label>'+ 
 '<label>RK45 max attempts (4–10000)<input id="ode-max-steps" type="number" min="4" max="10000" step="1" value="1000"></label></div>'+
 '<div class="data-toolbar"><button id="ode-run" type="button" class="primary">Solve IVP</button>'+
 '<button id="ode-to-table" type="button" class="secondary" disabled>Save output to Data Tables</button>'+
 '<button id="ode-to-graph" type="button" class="secondary" disabled>Plot y(t) in Graphs</button></div>'+
 '<pre id="ode-output" role="status" aria-live="polite">Enter the derivative and initial conditions.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#ode-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px}'+
 '#ode-details summary{cursor:pointer;color:#3c50ae;font-weight:750}'+
 '#ode-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px}'+
 '#ode-output.error{color:#a82241;background:#fff2f4}'+
 '#ode-details button,#ode-details select,#ode-details input{min-height:40px}';
document.head.append(style);
let last=null;
function invalidate(){
 last=null;$('ode-to-table').disabled=true;$('ode-to-graph').disabled=true;
 $('ode-output').classList.remove('error');$('ode-output').textContent='Enter the derivative and initial conditions.';
}
function updateSystemFields(){
 const system=$('ode-method').value==='rk4-system';
 $('ode-system-derivative-label').hidden=!system;
 $('ode-system-initial-label').hidden=!system;
}
for(const input of area.querySelectorAll('input,select')){input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);}
$('ode-method').addEventListener('change',updateSystemFields);updateSystemFields();
function run(){
 try{
  const mode=$('ode-method').value;
  const solver=mode==='rk45'?solveAdaptive:mode==='rk4-system'?solveSystem:solve;
  last=solver({expression:$('ode-expression').value,expressionZ:$('ode-system-derivative').value,
   t0:$('ode-start').value,t1:$('ode-end').value,y0:$('ode-initial').value,
   z0:$('ode-system-initial').value,steps:$('ode-steps').value,
   tolerance:$('ode-tolerance').value,maxSteps:$('ode-max-steps').value});
  $('ode-output').classList.remove('error');
  const end=last.rows[last.rows.length-1];
  const detail=last.type==='ode-rk45'?'accepted '+last.steps+', rejected '+last.rejected+
   ', tolerance '+last.tolerance+', accepted |Δt| '+last.minAcceptedStep.toPrecision(5)+
   '–'+last.maxAcceptedStep.toPrecision(5)+', max accepted local-error ratio '+
   last.maxAcceptedErrorRatio.toPrecision(5)+
   (last.rejected?', max rejected local-error ratio '+last.maxRejectedErrorRatio.toPrecision(5)+
    ', smallest rejected |Δt| '+last.minRejectedStep.toPrecision(5):'')+
   (last.stageOverflowRejected?', bounded stage-overflow retries '+last.stageOverflowRejected+
    ', last bounded stage '+last.lastOverflowStage:'')+
   (last.resolutionLimitedAttempts?', time-resolution-limited attempts '+last.resolutionLimitedAttempts:'')+
   (last.quantumLimitedAcceptedSteps?', warning: '+last.quantumLimitedAcceptedSteps+
    ' accepted time steps advanced by only one representable time increment; rescale time and verify convergence':'')+
   (last.stageTimeCollisionAcceptedSteps?', warning: '+last.stageTimeCollisionAcceptedSteps+
    ' accepted steps had RK45 stage times rounded to current t; rescale time for reliable accuracy':'')+
   (last.rejectionWarning?', warning: '+last.rejectionWarning:''):
   'Δt='+last.h.toPrecision(8)+(last.type==='ode-rk4-system'||last.type==='ode-rk4'?(last.convergence?
    '; RK4 step-doubling |x_N − x_2N|∞ '+last.convergence.endpointDifference.toPrecision(5)+
    ' (diagnostic only, not a global error bound)':'; step-doubling unavailable (more than 500 steps or unresolvable refined grid)'):'');
  const endState='y('+end[0].toPrecision(10)+') ≈ '+end[1].toPrecision(12)+
   (last.type==='ode-rk4-system'?', z ≈ '+end[2].toPrecision(12):'');
  $('ode-output').textContent=last.method+'\n'+last.rows.length+' output rows; '+detail+
   '\n'+endState+'\n'+last.note;
  $('ode-to-table').disabled=false;$('ode-to-graph').disabled=false;
 }catch(error){
  last=null;$('ode-to-table').disabled=true;$('ode-to-graph').disabled=true;
  $('ode-output').classList.add('error');$('ode-output').textContent=error.message;
 }
}
$('ode-run').addEventListener('click',run);
function importRows(){
 if(!last)throw Error('Solve an initial-value problem first.');
 return M.dataTables.importData({headers:last.columns,rows:last.rows},last.type==='ode-rk45'?'ODE_RK45':last.type==='ode-rk4-system'?'ODE_RK4_SYSTEM':'ODE_RK4');
}
function fail(error){$('ode-output').classList.add('error');$('ode-output').textContent=error.message;}
$('ode-to-table').addEventListener('click',()=>{try{importRows();M.advanced.mode('data');}catch(e){fail(e);}});
$('ode-to-graph').addEventListener('click',()=>{
 try{
  const table=importRows();M.advanced.mode('graph');
  $('dt-graph-table').value=table.id;
  $('dt-graph-table').dispatchEvent(new Event('change',{bubbles:true}));
  $('dt-chart-type').value='line';$('dt-graph-x').value='0';$('dt-graph-y').value='1';
  $('dt-plot-table').click();
 }catch(e){fail(e);}
});
M.odeTools={solve,solveAdaptive,solveSystem,run};
})();
