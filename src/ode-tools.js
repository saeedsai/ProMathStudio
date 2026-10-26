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
function solve({expression='y',t0=0,t1=1,y0=1,steps=40}={}){
 expression=String(expression).trim();
 if(!expression||expression.length>1000)throw Error('Enter dy/dt as a mathematical expression (at most 1,000 characters).');
 t0=finite(t0,'Initial time');t1=finite(t1,'End time');y0=finite(y0,'Initial y');
 if(!(t1>t0))throw Error('End time must be greater than initial time (forward integration only).');
 steps=finite(steps,'Time steps');
 if(!Number.isInteger(steps)||steps<4||steps>1000)throw Error('Time steps must be an integer from 4 to 1000.');
 const h=(t1-t0)/steps;
 if(!Number.isFinite(h)||h<=0)throw Error('Invalid integration step size.');
 const f=(t,y)=>bounded(M.numerical.evaluate(expression,{t:bounded(t,'Time'),y:bounded(y,'State')}),'Derivative');
 let y=y0;const rows=[];
 for(let i=0;i<=steps;i++){
  const t=bounded(i===steps?t1:t0+i*h,'Time');
  rows.push([t,y]);
  if(i===steps)break;
  const k1=f(t,y);
  const k2=f(t+h/2,y+h*k1/2);
  const k3=f(t+h/2,y+h*k2/2);
  const k4=f(t+h,y+h*k3);
  y=bounded(y+(h/6)*(k1+2*k2+2*k3+k4),'State');
 }
 return {type:'ode-rk4',columns:['t','y'],rows,steps,h,
  method:'Classical fourth-order Runge–Kutta (RK4)',
  note:'Scalar first-order y\u2032=f(t,y), y(t0)=y0; fixed steps, forward only. Accuracy depends on smoothness and step size. Not an adaptive/stiff ODE solver.'};
}
const area=document.createElement('details');area.id='ode-details';
area.innerHTML='<summary>First-order ODE initial-value problem · RK4</summary>'+
 '<p class="graph-data-muted">Solve dy/dt = f(t,y) from an initial value. Example: f(t,y)=y, y(0)=1 gives y(1)≈e. Real finite solutions only; decrease the step size to check convergence.</p>'+
 '<div class="num-fields"><label>Derivative f(t,y)<input id="ode-expression" value="y" spellcheck="false"></label>'+
 '<label>Initial time t₀<input id="ode-start" type="number" step="any" value="0"></label>'+
 '<label>End time t₁<input id="ode-end" type="number" step="any" value="1"></label>'+
 '<label>Initial y(t₀)<input id="ode-initial" type="number" step="any" value="1"></label>'+
 '<label>Time steps (4–1000)<input id="ode-steps" type="number" min="4" max="1000" step="1" value="40"></label></div>'+
 '<div class="data-toolbar"><button id="ode-run" type="button" class="primary">Solve IVP (RK4)</button>'+
 '<button id="ode-to-table" type="button" class="secondary" disabled>Save output to Data Tables</button>'+
 '<button id="ode-to-graph" type="button" class="secondary" disabled>Plot y(t) in Graphs</button></div>'+
 '<pre id="ode-output" role="status" aria-live="polite">Enter the derivative and initial conditions.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#ode-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px}'+
 '#ode-details summary{cursor:pointer;color:#3c50ae;font-weight:750}'+
 '#ode-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px}'+
 '#ode-output.error{color:#a82241;background:#fff2f4}';
document.head.append(style);
let last=null;
function invalidate(){
 last=null;$('ode-to-table').disabled=true;$('ode-to-graph').disabled=true;
 $('ode-output').classList.remove('error');$('ode-output').textContent='Enter the derivative and initial conditions.';
}
for(const input of area.querySelectorAll('input')){input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);}
function run(){
 try{
  last=solve({expression:$('ode-expression').value,t0:$('ode-start').value,
   t1:$('ode-end').value,y0:$('ode-initial').value,steps:$('ode-steps').value});
  $('ode-output').classList.remove('error');
  const end=last.rows[last.rows.length-1];
  $('ode-output').textContent=last.method+'\n'+last.rows.length+' output rows; Δt='+last.h.toPrecision(8)+
   '\ny('+end[0].toPrecision(10)+') ≈ '+end[1].toPrecision(12)+'\n'+last.note;
  $('ode-to-table').disabled=false;$('ode-to-graph').disabled=false;
 }catch(error){
  last=null;$('ode-to-table').disabled=true;$('ode-to-graph').disabled=true;
  $('ode-output').classList.add('error');$('ode-output').textContent=error.message;
 }
}
$('ode-run').addEventListener('click',run);
function importRows(){
 if(!last)throw Error('Solve an initial-value problem first.');
 return M.dataTables.importData({headers:last.columns,rows:last.rows},'ODE_RK4');
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
M.odeTools={solve,run};
})();
