/* ProMathStudio: two-point boundary-value problems y''=f(x,y,y') by the shooting method.
   Reuses the existing RK4 system solver (odeTools.solveSystem) or the implicit TR-BDF2
   solver (stiffOde.solve); no new integrator. Expressions use the safe numeric AST evaluator. */
(()=>{'use strict';
const M=window.MathStudio, anchor=document.getElementById('stiff-ode-details')||document.getElementById('ode-details');
if(!M?.odeTools?.solveSystem||!M?.dataTables||!anchor)return;
const $=id=>document.getElementById(id), MAX=1e12;
function finite(value,label){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(label+' is required.');
 const n=Number(value);
 if(!Number.isFinite(n)||Math.abs(n)>MAX)throw Error(label+' must be finite with magnitude at most 1e12.');
 return n;
}
function integer(value,label,lo,hi){
 const n=finite(value,label);
 if(!Number.isInteger(n)||n<lo||n>hi)throw Error(label+' must be an integer from '+lo+' to '+hi+'.');
 return n;
}
// The user writes f with x (independent variable), y and yp (= y'). The existing system
// solver names them t, y, z, so rename identifier tokens only (exp, max etc. are untouched);
// t and z are therefore accepted aliases for x and yp.
function toSystemExpression(expression){
 expression=String(expression??'').trim();
 if(!expression||expression.length>1000)throw Error("Enter y'' = f(x, y, yp) as a mathematical expression (at most 1,000 characters).");
 return expression.replace(/\bx\b/g,'t').replace(/\byp\b/g,'z');
}
const TYPES={dirichlet:[1,0],neumann:[0,1]};
function boundary(spec,label){
 if(!spec||typeof spec!=='object')throw Error(label+' boundary condition is required.');
 const type=String(spec.type||'dirichlet').toLowerCase();
 let c0,c1;
 if(TYPES[type])[c0,c1]=TYPES[type];
 else if(type==='robin'){c0=finite(spec.c0,label+' coefficient c₀');c1=finite(spec.c1,label+' coefficient c₁');}
 else throw Error(label+' boundary type must be dirichlet, neumann or robin.');
 if(c0===0&&c1===0)throw Error(label+' Robin condition needs c₀ or c₁ nonzero.');
 return {type,c0,c1,gamma:finite(spec.value,label+' boundary value')};
}
function shoot({expression="-y",a=0,b=1,left={type:'dirichlet',value:0},right={type:'dirichlet',value:1},
 sMin=-10,sMax=10,scanCount=60,steps=200,method='rk4',tolerance=1e-10,maxIterations=80,maxSolutions=10}={}){
 const f=toSystemExpression(expression);
 a=finite(a,'Left endpoint a');b=finite(b,'Right endpoint b');
 if(!(b>a))throw Error('Right endpoint b must be greater than left endpoint a.');
 const L=boundary(left,'Left'), R=boundary(right,'Right');
 sMin=finite(sMin,'Scan minimum');sMax=finite(sMax,'Scan maximum');
 if(!(sMax>sMin))throw Error('Scan maximum must be greater than scan minimum.');
 scanCount=integer(scanCount,'Scan intervals',2,400);
 method=String(method);
 if(method!=='rk4'&&method!=='tr-bdf2')throw Error('Integrator must be rk4 or tr-bdf2.');
 if(method==='tr-bdf2'&&!M?.stiffOde?.solve)throw Error('The stiff TR-BDF2 solver is not available.');
 steps=integer(steps,'RK4 steps',10,500);
 tolerance=finite(tolerance,'Shooting tolerance');
 if(!(tolerance>=1e-14&&tolerance<=1e-3))throw Error('Shooting tolerance must be between 1e-14 and 1e-3.');
 maxIterations=integer(maxIterations,'Refinement iterations',5,200);
 // Shooting parameter s: y'(a) when the left condition fixes y(a) only, otherwise s=y(a).
 const parameter=L.c1===0?"y′(a)":'y(a)';
 const initial=s=>L.c1===0?[L.gamma/L.c0,s]:[s,(L.gamma-L.c0*s)/L.c1];
 let integrations=0;
 // fine=1: requested resolution; fine=2: step doubling (RK4) or 100x tighter tolerances (TR-BDF2).
 function integrate(s,fine=1){
  const [y0,z0]=initial(s);integrations++;
  if(method==='rk4')return M.odeTools.solveSystem({expression:'z',expressionZ:f,t0:a,t1:b,y0,z0,steps:steps*fine},true).rows;
  return M.stiffOde.solve({expression:'z',expressionZ:f,t0:a,t1:b,y0,z0,
   rtol:fine===1?1e-7:1e-9,atol:fine===1?1e-10:1e-12,maxSteps:20000}).rows;
 }
 const residualOf=rows=>{const e=rows.at(-1);return R.c0*e[1]+R.c1*e[2]-R.gamma;};
 const scaleOf=rows=>1+rows.reduce((m,r)=>Math.max(m,Math.abs(r[1]),Math.abs(r[2])),0);
 // Validate the expression once so syntax/domain errors are reported instead of skipped.
 const midS=(sMin+sMax)/2;
 let probe=null,firstError=null;
 for(const s of [midS,sMin,sMax]){try{probe=integrate(s);break;}catch(error){firstError=firstError||error;}}
 if(!probe)throw Error('Initial-value integration failed for every probe slope: '+firstError.message);
 const residual=(s,fine=1)=>{try{return residualOf(integrate(s,fine));}catch(e){return NaN;}};
 const grid=[],values=[];let failed=0;
 for(let k=0;k<=scanCount;k++){
  const s=k===scanCount?sMax:sMin+k*(sMax-sMin)/scanCount, r=residual(s);
  grid.push(s);values.push(r);if(!Number.isFinite(r))failed++;
 }
 // Degenerate (non-unique) problem: residual indistinguishable from discretization error
 // at the scan ends and centre, i.e. every probed trajectory satisfies the right condition.
 const degenerate=[sMin,midS,sMax].every(s=>{
  try{
   const coarse=integrate(s), r1=residualOf(coarse), r2=residualOf(integrate(s,2));
   return Number.isFinite(r1)&&Math.abs(r1)<=Math.max(10*Math.abs(r1-r2),1e-9*scaleOf(coarse));
  }catch(e){return false;}
 });
 // Illinois (modified regula falsi) on a sign-change bracket: bracketing, superlinear.
 function refine(lo,hi,flo,fhi,fine){
  let iterations=0,side=0;
  if(flo===0)return {s:lo,iterations};if(fhi===0)return {s:hi,iterations};
  while(iterations<maxIterations){
   iterations++;
   let s=hi-fhi*(hi-lo)/(fhi-flo);
   if(!(s>lo&&s<hi))s=lo+(hi-lo)/2;
   const fs=residual(s,fine);
   if(!Number.isFinite(fs)){ // integration failure inside the bracket: bisect instead
    const m=lo+(hi-lo)/2,fm=residual(m,fine);
    if(!Number.isFinite(fm))return {s:m,iterations,failed:true};
    if(Math.sign(fm)===Math.sign(flo)){lo=m;flo=fm;}else{hi=m;fhi=fm;}
    continue;
   }
   if(fs===0||hi-lo<=tolerance*(1+Math.abs(s)))return {s,iterations};
   if(Math.sign(fs)===Math.sign(fhi)){hi=s;fhi=fs;if(side===-1)flo/=2;side=-1;}
   else{lo=s;flo=fs;if(side===1)fhi/=2;side=1;}
   if(hi-lo<=tolerance*(1+Math.abs(lo)))return {s:Math.abs(flo)<Math.abs(fhi)?lo:hi,iterations};
  }
  return {s:Math.abs(flo)<Math.abs(fhi)?lo:hi,iterations,exhausted:true};
 }
 // Secant iteration on the refined residual for the step-doubling diagnostic only.
 function secant(s0,delta){
  let x0=s0,x1=s0+delta,f0=residual(x0,2),f1=residual(x1,2);
  for(let k=0;k<30;k++){
   if(!Number.isFinite(f0)||!Number.isFinite(f1))return null;
   if(f1===0)return x1;
   if(f0===f1)return Math.abs(f0)<Math.abs(f1)?x0:x1;
   const x2=x1-f1*(x1-x0)/(f1-f0);
   if(!Number.isFinite(x2))return null;
   x0=x1;f0=f1;x1=x2;f1=residual(x1,2);
   if(Math.abs(x1-x0)<=tolerance*(1+Math.abs(x1)))return x1;
  }
  return null;
 }
 const solutions=[],rejected=[];
 let brackets=0;
 if(!degenerate)for(let k=0;k<scanCount;k++){
  const f0=values[k],f1=values[k+1];
  if(!Number.isFinite(f0)||!Number.isFinite(f1))continue;
  const exactLeft=f0===0&&k===0, signChange=f0!==0&&(f1===0||Math.sign(f0)!==Math.sign(f1));
  if(!exactLeft&&!signChange)continue;
  brackets++;
  if(solutions.length>=maxSolutions)continue;
  const lo=grid[k],hi=grid[k+1], root=exactLeft?{s:lo,iterations:0}:refine(lo,hi,f0,f1,1);
  let rows;
  try{rows=integrate(root.s);}catch(e){rejected.push({s:root.s,reason:'integration failed'});continue;}
  const res=residualOf(rows), scale=scaleOf(rows);
  // A sign change through a blow-up (pole in R(s)) is not a solution.
  if(root.failed||!(Math.abs(res)<=Math.max(1e-6,1e3*tolerance)*scale)){
   rejected.push({s:root.s,residual:res,reason:'sign change without small residual (possible pole or blow-up)'});continue;
  }
  // Step-doubling estimate: re-shoot at 2N steps (or 100x tighter TR-BDF2 tolerances) by a
  // bounded secant iteration started at the accepted parameter (the root moves only slightly).
  let estimate=null;
  try{
   const fineRoot=secant(root.s,Math.max(1e-6,(hi-lo)*1e-3)*(1+Math.abs(root.s)));
   if(fineRoot!==null){
    const fineRows=integrate(fineRoot,2);
    let maxDiff=0;
    if(method==='rk4')rows.forEach((row,i)=>{maxDiff=Math.max(maxDiff,Math.abs(row[1]-fineRows[2*i][1]));});
    else maxDiff=Math.abs(rows.reduce((m,r)=>Math.max(m,r[1]),-Infinity)-fineRows.reduce((m,r)=>Math.max(m,r[1]),-Infinity));
    estimate={parameterDifference:Math.abs(fineRoot-root.s),solutionDifference:maxDiff,
     basis:method==='rk4'?'max |y_N − y_2N| on shared grid nodes':'change of max y with 100× tighter tolerances'};
   }
  }catch(e){estimate=null;}
  const start=initial(root.s);
  solutions.push({parameter:root.s,y0:start[0],slope0:start[1],residual:res,iterations:root.iterations,
   exhausted:!!root.exhausted,estimate,rows:rows.map(r=>[r[0],r[1],r[2]]),
   yMax:rows.reduce((m,r)=>Math.max(m,r[1]),-Infinity),yMin:rows.reduce((m,r)=>Math.min(m,r[1]),Infinity)});
 }
 const status=degenerate?'non-unique':solutions.length===0?'none-found':solutions.length===1?'unique-in-scan':'multiple';
 return {type:'bvp-shooting',status,degenerate,solutions,rejected,brackets,failedScanPoints:failed,
  scan:{sMin,sMax,scanCount,values:grid.map((s,i)=>[s,values[i]])},parameter,left:L,right:R,a,b,method,steps,integrations,
  columns:['x','y','dy/dx'],
  method_label:method==='rk4'?'Shooting with classical RK4 (odeTools.solveSystem)':'Shooting with implicit TR-BDF2 (stiffOde.solve)',
  note:'Solutions are found only where the boundary residual changes sign between scan points of the chosen '+parameter+
   ' range; touching (double) roots, roots between close scan points and roots outside the range can be missed. '+
   'The step-doubling estimate is a diagnostic, not a certified error bound.'};
}

const area=document.createElement('details');area.id='bvp-details';
area.innerHTML='<summary>Boundary-value problem · shooting y″ = f(x, y, y′)</summary>'+
 '<p class="graph-data-muted">Write f using x, y and yp (for y′). Boundary conditions are c₀·y + c₁·y′ = γ at each end (Dirichlet: y=γ, Neumann: y′=γ). The scan range is for y′(a) when the left condition is Dirichlet, otherwise for y(a). Example (Bratu): f = -exp(y), y(0)=0, y(1)=0, scan 0–15.</p>'+
 '<div class="num-fields">'+
 '<label>f(x, y, yp) = y″<input id="bvp-f" value="-exp(y)" spellcheck="false"></label>'+
 '<label>Left endpoint a<input id="bvp-a" type="number" step="any" value="0"></label>'+
 '<label>Right endpoint b<input id="bvp-b" type="number" step="any" value="1"></label>'+
 '<label>Left condition<select id="bvp-left-type"><option value="dirichlet">Dirichlet y(a)=γ</option><option value="neumann">Neumann y′(a)=γ</option><option value="robin">Robin c₀y+c₁y′=γ</option></select></label>'+
 '<label>Left γ<input id="bvp-left-value" type="number" step="any" value="0"></label>'+
 '<label class="bvp-robin-left" hidden>Left c₀<input id="bvp-left-c0" type="number" step="any" value="1"></label>'+
 '<label class="bvp-robin-left" hidden>Left c₁<input id="bvp-left-c1" type="number" step="any" value="1"></label>'+
 '<label>Right condition<select id="bvp-right-type"><option value="dirichlet">Dirichlet y(b)=γ</option><option value="neumann">Neumann y′(b)=γ</option><option value="robin">Robin c₀y+c₁y′=γ</option></select></label>'+
 '<label>Right γ<input id="bvp-right-value" type="number" step="any" value="0"></label>'+
 '<label class="bvp-robin-right" hidden>Right c₀<input id="bvp-right-c0" type="number" step="any" value="1"></label>'+
 '<label class="bvp-robin-right" hidden>Right c₁<input id="bvp-right-c1" type="number" step="any" value="1"></label>'+
 '<label>Scan minimum<input id="bvp-smin" type="number" step="any" value="0"></label>'+
 '<label>Scan maximum<input id="bvp-smax" type="number" step="any" value="15"></label>'+
 '<label>Scan intervals (2–400)<input id="bvp-scan" type="number" min="2" max="400" step="1" value="60"></label>'+
 '<label>RK4 steps (10–500)<input id="bvp-steps" type="number" min="10" max="500" step="1" value="200"></label>'+
 '<label>Integrator<select id="bvp-method"><option value="rk4">Fixed-step RK4</option><option value="tr-bdf2">Stiff TR-BDF2</option></select></label></div>'+
 '<div class="data-toolbar"><button id="bvp-run" type="button" class="primary">Solve BVP</button>'+
 '<button id="bvp-to-table" type="button" class="secondary" disabled>Save to Data Tables</button></div>'+
 '<pre id="bvp-output" role="status" aria-live="polite">Enter f, the interval, boundary conditions and the scan range.</pre>';
anchor.after(area);
const style=document.createElement('style');
style.textContent='#bvp-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px;max-width:100%;box-sizing:border-box}'+
 '#bvp-details summary{cursor:pointer;color:#3c50ae;font-weight:750;min-height:40px;display:flex;align-items:center}'+
 '#bvp-details .num-fields{min-width:0}#bvp-details label{min-width:0}'+
 '#bvp-details input,#bvp-details select{max-width:100%;box-sizing:border-box}'+
 '#bvp-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px;max-width:100%;box-sizing:border-box}'+
 '#bvp-output.error{color:#a82241;background:#fff2f4}'+
 '#bvp-details button,#bvp-details input,#bvp-details select{min-height:40px}'+
 '@media(max-width:480px){#bvp-details .num-fields{grid-template-columns:1fr}}';
document.head.append(style);
let last=null;
const output=$('bvp-output'), toTable=$('bvp-to-table'), IDLE='Enter f, the interval, boundary conditions and the scan range.';
function invalidate(){last=null;toTable.disabled=true;output.classList.remove('error');output.textContent=IDLE;}
function updateRobin(){
 for(const side of ['left','right']){
  const robin=$('bvp-'+side+'-type').value==='robin';
  for(const label of area.querySelectorAll('.bvp-robin-'+side))label.hidden=!robin;
 }
}
for(const input of area.querySelectorAll('input,select')){input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);}
$('bvp-left-type').addEventListener('change',updateRobin);$('bvp-right-type').addEventListener('change',updateRobin);updateRobin();
function fail(error){
 last=null;toTable.disabled=true;output.classList.add('error');
 output.textContent=error.message+'\nRecovery: check f (use x, y, yp), the interval a<b, the boundary conditions and the scan range, then press Solve BVP again.';
}
const p=v=>Number(v).toPrecision(10);
function describe(r){
 const lines=[r.method_label,'Shooting parameter s = '+r.parameter+', scanned '+r.scan.sMin+'…'+r.scan.sMax+' in '+r.scan.scanCount+
  ' intervals; '+r.integrations+' IVP integrations'+(r.failedScanPoints?', '+r.failedScanPoints+' scan points failed to integrate':'')];
 if(r.status==='non-unique')lines.push('No unique solution: the boundary residual vanishes (to discretization error) across the whole scan range, so a family of solutions satisfies both conditions (e.g. an eigenvalue/resonant linear problem).');
 else if(r.status==='none-found')lines.push('No solution found: the boundary residual does not change sign in the scan range. Widen the range or refine the scan; the problem may have no solution.');
 else lines.push(r.solutions.length+' solution'+(r.solutions.length>1?'s':'')+' bracketed in the scan range'+(r.status==='multiple'?' (the BVP is not unique)':'')+':');
 r.solutions.forEach((s,i)=>lines.push('#'+(i+1)+': y(a) = '+p(s.y0)+', y′(a) = '+p(s.slope0)+', residual at b = '+Number(s.residual).toExponential(3)+
  ', y range ['+p(s.yMin)+', '+p(s.yMax)+'], '+s.iterations+' refinement iterations'+(s.exhausted?' (iteration budget reached)':'')+
  (s.estimate?'; step-doubling '+s.estimate.basis+' = '+s.estimate.solutionDifference.toExponential(3):'; step-doubling estimate unavailable')));
 if(r.rejected.length)lines.push(r.rejected.length+' sign change(s) rejected as possible poles or integration failures.');
 lines.push(r.note);
 return lines.join('\n');
}
function run(){
 try{
  const side=s=>({type:$('bvp-'+s+'-type').value,value:$('bvp-'+s+'-value').value,c0:$('bvp-'+s+'-c0').value,c1:$('bvp-'+s+'-c1').value});
  last=shoot({expression:$('bvp-f').value,a:$('bvp-a').value,b:$('bvp-b').value,left:side('left'),right:side('right'),
   sMin:$('bvp-smin').value,sMax:$('bvp-smax').value,scanCount:$('bvp-scan').value,steps:$('bvp-steps').value,method:$('bvp-method').value});
  output.classList.remove('error');output.textContent=describe(last);
  toTable.disabled=!last.solutions.length;
 }catch(error){fail(error);}
}
$('bvp-run').addEventListener('click',run);
toTable.addEventListener('click',()=>{
 try{
  if(!last||!last.solutions.length)throw Error('Solve a boundary-value problem with at least one solution first.');
  last.solutions.forEach((s,i)=>M.dataTables.importData({headers:last.columns,rows:s.rows},'BVP_SHOOTING_'+(i+1)));
  M.advanced?.mode?.('data');
 }catch(error){fail(error);}
});
M.bvp={shoot,run};
})();
