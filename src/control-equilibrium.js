/* Control equilibrium xdot = -A*x + b; shared scaled-pivot Matrix solver. */
(()=>{'use strict';
const studio=window.MathStudio,root=document.getElementById('ct-equilibrium');
if(!root||!studio||!studio.engineeringSolvers)return;
const by=id=>document.getElementById(id);
const size=by('ct-eq-size'),matrix=by('ct-eq-matrix'),forcing=by('ct-eq-forcing');
const status=by('ct-eq-status'),output=by('ct-eq-output');
const stabilityStatus=by('ct-eq-stability-status'),stabilityOutput=by('ct-eq-stability-output');
function values(text,count,label){
 if(typeof text!=='string'||text.length>512)throw Error(label+' input is too long.');
 const raw=text.trim(),parts=raw.includes(',')?raw.split(',').map(x=>x.trim()):raw.split(/\s+/);
 if(parts.length!==count||parts.some(x=>!x))throw Error(label+' requires exactly '+count+' values.');
 return parts;
}
function parseMatrix(text,n){
 if(typeof text!=='string'||text.length>512)throw Error('Matrix A input is too long.');
 if(n!==2&&n!==3)throw Error('State dimension must be 2 or 3.');
 const rows=text.trim().split(/\s*;\s*|\n+/);
 if(rows.length!==n)throw Error('Matrix A requires exactly '+n+' rows.');
 return rows.map((row,i)=>values(row,n,'Matrix A row '+(i+1)));
}
function solveEquilibrium(A,b){
 return studio.engineeringSolvers.execute('matrix.solve.real.small',{A,b});
}
/* Perturbation stability for xdot = -A*x+b. Reuse the bounded symmetric
   Jacobi eigenanalysis; equilibrium existence is a separate question.
   Near-zero eigenvalues cannot be classified reliably at this precision. */
function analyzeStability(A){
 const eigen=studio.matrixTools.eigenSymmetric(A);
 const eigenvalues=eigen.values.slice();
 const scale=Math.max(...eigenvalues.map(Math.abs));
 const tolerance=1e-12*scale;
 let classification;
 if(eigenvalues.some(x=>x < -tolerance))classification='unstable';
 else if(eigenvalues.some(x=>x!==0&&Math.abs(x)<=tolerance))classification='indeterminate';
 else if(eigenvalues.some(x=>x===0))classification='marginal';
 else classification='asymptotically stable';
 return {classification,eigenvalues,tolerance,residual:eigen.residual};
}
function calculateStability(){
 try{
  const n=Number(size.value);
  if(n!==2&&n!==3)throw Error('State dimension must be 2 or 3.');
  const result=analyzeStability(parseMatrix(matrix.value,n));
  const fmt=x=>Number(x.toPrecision(10)).toString();
  stabilityOutput.textContent='Perturbation stability: '+result.classification+'\n'+
   'Eigenvalues of A: ['+result.eigenvalues.map(fmt).join(', ')+']\n'+
   'Eigenanalysis residual: '+fmt(result.residual)+'\n'+
   'Near-zero tolerance: '+fmt(result.tolerance)+'\n'+
   'Only real symmetric 2×2/3×3 A is supported. Constant b does not change perturbation eigenvalues.\n'+
   'Equilibrium existence/uniqueness is not established by stability analysis. '+
   'Marginal means an exact zero eigenvalue; near-zero modes are indeterminate.';
  stabilityStatus.textContent='Symmetric-system stability analyzed for '+n+' states.';
  return result;
 }catch(error){
  stabilityOutput.textContent='No valid stability classification.';
  stabilityStatus.textContent=error.message;
  return null;
 }
}
/* Bounded two-state trajectory; use the existing safe coupled RK4 engine. */
function numericValues(parts,label){
 return parts.map((part,i)=>{
  if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?$/i.test(part))
   throw Error(label+' value '+(i+1)+' must be decimal or scientific notation.');
  const n=Number(part);
  if(!Number.isFinite(n)||Math.abs(n)>1e12)
   throw Error(label+' value '+(i+1)+' must be finite with magnitude at most 1e12.');
  return n;
 });
}
let lastTransient=null;
const transientStatus=by('ct-eq-transient-status'),transientOutput=by('ct-eq-transient-output');
const transientTable=by('ct-eq-transient-table');
function simulateTransient(A,b,x0,t0=0,t1=1,steps=80){
 if(!Array.isArray(A)||A.length!==2||A.some(row=>!Array.isArray(row)||row.length!==2))
  throw Error('Transient response requires a 2×2 matrix A.');
 if(!Array.isArray(b)||b.length!==2||!Array.isArray(x0)||x0.length!==2)
  throw Error('Transient response requires two forcing and initial-state values.');
 if(!studio.odeTools?.solveSystem)throw Error('Shared coupled ODE solver is unavailable.');
 const a=A.map((row,i)=>numericValues(row.map(String),'Matrix A row '+(i+1)));
 const forcing=numericValues(b.map(String),'Forcing b');
 const initial=numericValues(x0.map(String),'Initial state');
 const expr=i=>'-('+a[i][0]+')*y-('+a[i][1]+')*z+('+forcing[i]+')';
 return studio.odeTools.solveSystem({expression:expr(0),expressionZ:expr(1),
  t0,t1,y0:initial[0],z0:initial[1],steps});
}
function calculateTransient(){
 try{
  if(Number(size.value)!==2)throw Error('Transient response currently supports exactly two states.');
  const A=parseMatrix(matrix.value,2),b=values(forcing.value,2,'Forcing b');
  const x0=values(by('ct-eq-initial').value,2,'Initial state');
  lastTransient=simulateTransient(A,b,x0,by('ct-eq-t0').value,
   by('ct-eq-t1').value,by('ct-eq-steps').value);
  const fmt=n=>Number(n.toPrecision(10)).toString();
  const end=lastTransient.rows.at(-1);
  // Step-doubling diagnostic, not a certified global error bound.
  let convergence='Step-doubling comparison unavailable (more than 500 base steps).';
  if(lastTransient.steps<=500){
   try{
    const finer=simulateTransient(A,b,x0,by('ct-eq-t0').value,
     by('ct-eq-t1').value,lastTransient.steps*2);
    const fineEnd=finer.rows.at(-1);
    const discrepancy=Math.max(Math.abs(end[1]-fineEnd[1]),Math.abs(end[2]-fineEnd[2]));
    convergence='RK4 step-doubling |x_N - x_2N|∞: '+fmt(discrepancy)+
     ' (diagnostic only; not a global error bound).';
   }catch(error){convergence='Step-doubling comparison unavailable: '+error.message;}
  }
  transientOutput.textContent='Coupled RK4 · '+lastTransient.steps+' fixed steps, '+
   lastTransient.rows.length+' trajectory samples\n'+
   'x('+fmt(end[0])+') ≈ ['+fmt(end[1])+', '+fmt(end[2])+']\n'+
   'First samples (t, x1, x2):\n'+lastTransient.rows.slice(0,5)
    .map(row=>row.map(fmt).join(', ')).join('\n')+'\n'+
   convergence+'\n'+
   'Fixed-step RK4 is not stiff or globally error-certified. Compare step counts for convergence.';
  transientStatus.textContent='Two-state trajectory computed.';
  transientTable.disabled=false;
  return lastTransient;
 }catch(error){
  lastTransient=null;
  if(transientTable)transientTable.disabled=true;
  if(transientOutput)transientOutput.textContent='No current trajectory.';
  if(transientStatus)transientStatus.textContent=error.message;
  return null;
 }
}
function invalidate(){
 status.textContent='Inputs changed; recompute equilibrium.';
 output.textContent='No current result.';
 stabilityStatus.textContent='Inputs changed; recompute stability.';
 stabilityOutput.textContent='No current stability result.';
 lastTransient=null;
 if(transientTable)transientTable.disabled=true;
 if(transientStatus)transientStatus.textContent='Inputs changed; recompute trajectory.';
 if(transientOutput)transientOutput.textContent='No current trajectory.';
}
function calculate(){
 try{
  const n=Number(size.value);
  if(n!==2&&n!==3)throw Error('State dimension must be 2 or 3.');
  const result=solveEquilibrium(parseMatrix(matrix.value,n),values(forcing.value,n,'Forcing b'));
  const fmt=x=>Number(x.toPrecision(10)).toString();
  output.textContent='Equilibrium x* = ['+result.solution.map(fmt).join(', ')+']\n'+
   'Maximum row-relative residual: '+fmt(result.residual)+'\n'+
   'Maximum absolute residual: '+fmt(result.absoluteResidual)+'\n'+
   'Normwise backward error (infinity norm): '+fmt(result.normwiseBackwardError);
  status.textContent='Equilibrium computed for '+n+' states.';
  return result;
 }catch(error){
  output.textContent='No valid equilibrium.';
  status.textContent=error.message;
  return null;
 }
}
for(const control of [size,matrix,forcing]){
 control.addEventListener('input',invalidate);
 control.addEventListener('change',invalidate);
}
by('ct-eq-run').addEventListener('click',calculate);
by('ct-eq-stability-run').addEventListener('click',calculateStability);
by('ct-eq-transient-run')?.addEventListener('click',calculateTransient);
for(const id of ['ct-eq-initial','ct-eq-t0','ct-eq-t1','ct-eq-steps']){
 const control=by(id);
 control?.addEventListener('input',invalidate);
 control?.addEventListener('change',invalidate);
}
transientTable?.addEventListener('click',()=>{
 try{
  if(!lastTransient)throw Error('Compute a trajectory before exporting.');
  studio.dataTables.importData({headers:['t','x1','x2'],rows:lastTransient.rows},'CONTROL_TRANSIENT');
  studio.advanced.mode('data');
 }catch(error){transientStatus.textContent=error.message;}
});
studio.controlEquilibrium=Object.freeze({parseMatrix,solve:solveEquilibrium,calculate,analyzeStability,calculateStability,simulateTransient,calculateTransient});
})();
