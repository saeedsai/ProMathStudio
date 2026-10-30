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
  stabilityOutput.textContent='Perturbation stability: '+result.classification+'\\n'+
   'Eigenvalues of A: ['+result.eigenvalues.map(fmt).join(', ')+']\\n'+
   'Eigenanalysis residual: '+fmt(result.residual)+'\\n'+
   'Near-zero tolerance: '+fmt(result.tolerance)+'\\n'+
   'Only real symmetric 2×2/3×3 A is supported. Constant b does not change perturbation eigenvalues.\\n'+
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
function invalidate(){
 status.textContent='Inputs changed; recompute equilibrium.';
 output.textContent='No current result.';
 stabilityStatus.textContent='Inputs changed; recompute stability.';
 stabilityOutput.textContent='No current stability result.';
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
studio.controlEquilibrium=Object.freeze({parseMatrix,solve:solveEquilibrium,calculate,analyzeStability,calculateStability});
})();
