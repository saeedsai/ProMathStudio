/* Control equilibrium xdot = -A*x + b; shared scaled-pivot Matrix solver. */
(()=>{'use strict';
const studio=window.MathStudio,root=document.getElementById('ct-equilibrium');
if(!root||!studio||!studio.engineeringSolvers)return;
const by=id=>document.getElementById(id);
const size=by('ct-eq-size'),matrix=by('ct-eq-matrix'),forcing=by('ct-eq-forcing');
const status=by('ct-eq-status'),output=by('ct-eq-output');
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
function invalidate(){
 status.textContent='Inputs changed; recompute equilibrium.';
 output.textContent='No current result.';
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
studio.controlEquilibrium=Object.freeze({parseMatrix,solve:solveEquilibrium,calculate});
})();
