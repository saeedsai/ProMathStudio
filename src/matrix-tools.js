/* ProMathStudio small-matrix calculator: deterministic 2x2/3x3 real arithmetic.
   No eval, external dependencies, stateful workers or mutation of other tools. */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('calculator-panel');
if(!M||!panel)return;
const el=(tag,attrs={},label)=>{const node=document.createElement(tag);
 for(const [key,value] of Object.entries(attrs))node.setAttribute(key,value);
 if(label!==undefined)node.textContent=String(label);return node;};
const limit=3,MAX_ENTRY=1e12;
function validate(A){
 if(!Array.isArray(A)||A.length<2||A.length>limit)throw Error('Matrix must have 2 or 3 rows.');
 const columns=Array.isArray(A[0])?A[0].length:0;
 if(columns<2||columns>limit||A.some(row=>!Array.isArray(row)||row.length!==columns))
  throw Error('Matrix must be rectangular with 2 or 3 columns.');
 return A.map((row,r)=>row.map((entry,c)=>{
  if(entry===null||typeof entry==='boolean'||String(entry).trim()==='')throw Error('Enter a number in row '+(r+1)+', column '+(c+1)+'.');
  const value=Number(entry);
  if(!Number.isFinite(value)||Math.abs(value)>MAX_ENTRY)throw Error('Matrix entries must be finite numbers with magnitude at most 1e12.');
  return value;
 }));
}
const requireSquare=A=>{if(A.length!==A[0].length)throw Error('This operation requires a square matrix.');};
const transpose=A=>{A=validate(A);return A[0].map((_,j)=>A.map(row=>row[j]));};
function binary(A,B,operation){
 A=validate(A);B=validate(B);
 const rows=A.length,cols=A[0].length;
 if(operation==='multiply'){
  if(cols!==B.length)throw Error('Multiplication requires Matrix A columns to equal Matrix B rows.');
  return Array.from({length:rows},(_,r)=>Array.from({length:B[0].length},(_,c)=>{
   const value=A[r].reduce((sum,entry,k)=>sum+entry*B[k][c],0);
   if(!Number.isFinite(value))throw Error('Result exceeded finite floating-point range.');
   return value;
  }));
 }
 if(rows!==B.length||cols!==B[0].length)throw Error('Addition and subtraction require the same matrix dimensions.');
 return A.map((row,r)=>row.map((entry,c)=>{
  const value=operation==='add'?entry+B[r][c]:entry-B[r][c];
  if(!Number.isFinite(value))throw Error('Result exceeded finite floating-point range.');
  return value;
 }));
}
/* Scaled partial pivoting: each original row supplies its own reference scale.
   This avoids discarding a small but independent row beside a large one. */
function rref(A){
 A=validate(A);
 const rows=A.map(row=>row.slice()),n=rows.length,cols=rows[0].length;
 const scales=rows.map(row=>Math.max(...row.map(Math.abs)));
 const tolerance=1e-12;
 let rank=0;
 for(let col=0;col<cols&&rank<n;col++){
  let pivot=rank,best=0;
  for(let r=rank;r<n;r++){
   const score=scales[r]?Math.abs(rows[r][col])/scales[r]:0;
   if(score>best){best=score;pivot=r;}
  }
  if(best<=tolerance){
   for(let r=rank;r<n;r++)if(Math.abs(rows[r][col])<=tolerance*scales[r])rows[r][col]=0;
   continue;
  }
  if(pivot!==rank){
   [rows[pivot],rows[rank]]=[rows[rank],rows[pivot]];
   [scales[pivot],scales[rank]]=[scales[rank],scales[pivot]];
  }
  const value=rows[rank][col];
  for(let c=0;c<cols;c++)rows[rank][c]/=value;
  rows[rank][col]=1;
  for(let r=0;r<n;r++){
   if(r===rank)continue;
   const factor=rows[r][col];
   for(let c=0;c<cols;c++)if(c!==col)rows[r][c]-=factor*rows[rank][c];
   rows[r][col]=0;
  }
  rank++;
 }
 for(const row of rows)for(let c=0;c<cols;c++){
  if(!Number.isFinite(row[c]))throw Error('RREF exceeded finite floating-point range.');
  if(Object.is(row[c],-0))row[c]=0;
 }
 return {matrix:rows,rank,tolerance};
}
/* Scaled partial-pivot solve for a square real A and vector b; no input mutation. */
function solve(A,b){
 A=validate(A);requireSquare(A);
 const n=A.length,tolerance=1e-12;
 if(!Array.isArray(b)||b.length!==n)throw Error('Right-hand side b must contain '+n+' values.');
 const rhs=b.map((entry,i)=>{
  if(entry===null||typeof entry==='boolean'||String(entry).trim()==='')throw Error('Enter a number in b row '+(i+1)+'.');
  const value=Number(entry);
  if(!Number.isFinite(value)||Math.abs(value)>MAX_ENTRY)throw Error('Right-hand side b must contain finite numbers with magnitude at most 1e12.');
  return value;
 });
 const rows=A.map((row,i)=>row.concat(rhs[i]));
 const scales=A.map(row=>Math.max(...row.map(Math.abs)));
 const rhsScales=scales.map((scale,i)=>Math.max(scale,Math.abs(rhs[i])));
 let rank=0;
 for(let col=0;col<n&&rank<n;col++){
  let pivot=rank,best=0;
  for(let r=rank;r<n;r++){
   const score=scales[r]?Math.abs(rows[r][col])/scales[r]:0;
   if(score>best){best=score;pivot=r;}
  }
  if(best<=tolerance)continue;
  if(pivot!==rank){
   [rows[pivot],rows[rank]]=[rows[rank],rows[pivot]];
   [scales[pivot],scales[rank]]=[scales[rank],scales[pivot]];
   [rhsScales[pivot],rhsScales[rank]]=[rhsScales[rank],rhsScales[pivot]];
  }
  for(let r=rank+1;r<n;r++){
   const factor=rows[r][col]/rows[rank][col];
   for(let c=col+1;c<=n;c++)rows[r][c]-=factor*rows[rank][c];
   rows[r][col]=0;
  }
  rank++;
 }
 if(rank<n){
  const inconsistent=rows.slice(rank).some((row,i)=>Math.abs(row[n])>tolerance*Math.max(rhsScales[rank+i],Number.MIN_VALUE));
  throw Error(inconsistent?'Inconsistent system: no solution.':'Singular or nearly singular system: no unique solution.');
 }
 const solution=Array(n).fill(0);
 for(let i=n-1;i>=0;i--){
  let value=rows[i][n];
  for(let j=i+1;j<n;j++)value-=rows[i][j]*solution[j];
  solution[i]=value/rows[i][i];
  if(!Number.isFinite(solution[i]))throw Error('Solution exceeded finite floating-point range.');
 }
 let residual=0;
 for(let i=0;i<n;i++){
  const actual=A[i].reduce((sum,a,j)=>sum+a*solution[j],0);
  const denominator=Math.abs(rhs[i])+A[i].reduce((sum,a,j)=>sum+Math.abs(a)*Math.abs(solution[j]),0);
  const error=Math.abs(actual-rhs[i])/Math.max(denominator,Number.MIN_VALUE);
  if(!Number.isFinite(error))throw Error('Solution residual exceeded finite floating-point range.');
  residual=Math.max(residual,error);
 }
 if(residual>1e-8)throw Error('Solution failed its numerical residual check.');
 return {solution,residual,rank:n};
}
/* Doolittle P*A=L*U with scaled partial row pivoting and row-relative
   reconstruction verification; no input mutation or external dependencies. */
function lu(A){
 A=validate(A);requireSquare(A);
 const n=A.length,tolerance=1e-12,U=A.map(row=>row.slice());
 const L=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>Number(i===j)));
 const permutation=Array.from({length:n},(_,i)=>i);
 const scales=A.map(row=>Math.max(...row.map(Math.abs)));
 for(let k=0;k<n;k++){
  let pivot=k,best=0;
  for(let r=k;r<n;r++){
   const score=scales[r]?Math.abs(U[r][k])/scales[r]:0;
   if(score>best){best=score;pivot=r;}
  }
  if(best<=tolerance)throw Error('Singular or nearly singular matrix: LU requires full rank.');
  if(pivot!==k){
   [U[k],U[pivot]]=[U[pivot],U[k]];
   [scales[k],scales[pivot]]=[scales[pivot],scales[k]];
   [permutation[k],permutation[pivot]]=[permutation[pivot],permutation[k]];
   for(let j=0;j<k;j++)[L[k][j],L[pivot][j]]=[L[pivot][j],L[k][j]];
  }
  for(let r=k+1;r<n;r++){
   const factor=U[r][k]/U[k][k];
   L[r][k]=factor;U[r][k]=0;
   for(let c=k+1;c<n;c++)U[r][c]-=factor*U[k][c];
  }
 }
 if([...L.flat(),...U.flat()].some(x=>!Number.isFinite(x)))throw Error('LU exceeded finite floating-point range.');
 const P=permutation.map(index=>Array.from({length:n},(_,j)=>Number(index===j)));
 let residual=0;
 for(let i=0;i<n;i++){
  const row=A[permutation[i]],scale=Math.max(Number.MIN_VALUE,...row.map(Math.abs));
  for(let j=0;j<n;j++){
   const reconstructed=L[i].reduce((sum,x,k)=>sum+x*U[k][j],0);
   const error=Math.abs(reconstructed-row[j])/scale;
   if(!Number.isFinite(error))throw Error('LU reconstruction exceeded finite floating-point range.');
   residual=Math.max(residual,error);
  }
 }
 if(residual>1e-8)throw Error('LU decomposition failed its numerical reconstruction check.');
 return {P,L,U,permutation,residual};
}
const matrixRank=A=>rref(A).rank;
const add=(A,B)=>binary(A,B,'add');
const subtract=(A,B)=>binary(A,B,'subtract');
const multiply=(A,B)=>binary(A,B,'multiply');
function determinant(A){
 A=validate(A);requireSquare(A);const n=A.length;
 let rows=A.map(row=>row.slice()),sign=1,result=1;
 for(let col=0;col<n;col++){
  let pivot=col;for(let r=col+1;r<n;r++)if(Math.abs(rows[r][col])>Math.abs(rows[pivot][col]))pivot=r;
  if(rows[pivot][col]===0)return 0;
  if(pivot!==col){[rows[pivot],rows[col]]=[rows[col],rows[pivot]];sign=-sign;}
  const p=rows[col][col];result*=p;
  for(let r=col+1;r<n;r++){const factor=rows[r][col]/p;
   for(let c=col+1;c<n;c++)rows[r][c]-=factor*rows[col][c];rows[r][col]=0;
  }
 }
 return sign*result;
}
function inverse(A){
 A=validate(A);requireSquare(A);const n=A.length;
 const maximum=Math.max(...A.flat().map(Math.abs));if(maximum===0)throw Error('Singular matrix: inverse does not exist.');
 const tolerance=1e-12*maximum;
 const B=A.map((row,i)=>row.concat(Array.from({length:n},(_,j)=>Number(i===j))));
 for(let col=0;col<n;col++){
  let pivot=col;for(let r=col+1;r<n;r++)if(Math.abs(B[r][col])>Math.abs(B[pivot][col]))pivot=r;
  if(Math.abs(B[pivot][col])<=tolerance)throw Error('Singular or nearly singular matrix: inverse is not reliable.');
  if(pivot!==col)[B[pivot],B[col]]=[B[col],B[pivot]];
  const scale=B[col][col];for(let j=0;j<2*n;j++)B[col][j]/=scale;
  for(let r=0;r<n;r++){if(r===col)continue;const factor=B[r][col];
   for(let j=0;j<2*n;j++)B[r][j]-=factor*B[col][j];
  }
 }
 const result=B.map(row=>row.slice(n));
 const residual=Math.max(...A.map((row,i)=>row.map((_,j)=>Math.abs(row.reduce((sum,x,k)=>sum+x*result[k][j],0)-(i===j?1:0)))).flat());
 if(!Number.isFinite(residual)||residual>1e-7)throw Error('Matrix inversion failed its numerical residual check.');
 return result;
}
function format(x){
 if(!Number.isFinite(x))throw Error('Result exceeded finite floating-point range.');
 if(Math.abs(x)<1e-13)return '0';
 return Number(x.toPrecision(12)).toString();
}
function notation(result){return typeof result==='number'?format(result):'matrix('+result.map(row=>'['+row.map(format).join(',')+']').join(',')+')';}
const area=el('details',{id:'matrix-tools',class:'matrix-tools'});
area.innerHTML='<summary>Matrix calculator · 2×2 / 3×3</summary>'+
 '<p class="small-note">Real-number matrices (2 or 3 rows/columns). Determinant and inverse require a square A; transpose, RREF/rank and binary arithmetic support rectangular shapes. LU requires a full-rank square A. Results display about 12 significant digits.</p>'+
 '<div class="matrix-controls"><label>Rows <select id="mat-rows"><option value="2">2</option><option value="3">3</option></select></label>'+
 '<label>Columns <select id="mat-cols"><option value="2">2</option><option value="3">3</option></select></label></div>'+
 '<div id="mat-grid" class="matrix-grid" aria-label="Matrix A entries"></div>'+
 '<p class="small-note">Right-hand side b (for A·x=b)</p>'+
 '<div id="mat-rhs-grid" class="matrix-grid" aria-label="Right-hand side b entries"></div>'+
 '<p class="small-note">Matrix B (for addition, subtraction and multiplication)</p>'+
 '<div class="matrix-controls"><label>B rows <select id="mat-b-rows"><option value="2">2</option><option value="3">3</option></select></label>'+
 '<label>B columns <select id="mat-b-cols"><option value="2">2</option><option value="3">3</option></select></label></div>'+
 '<div id="mat-b-grid" class="matrix-grid" aria-label="Matrix B entries"></div>'+
 '<div class="matrix-actions"><button type="button" id="mat-det" class="secondary">Determinant</button>'+
 '<button type="button" id="mat-transpose" class="secondary">Transpose</button>'+
 '<button type="button" id="mat-inverse" class="secondary">Inverse</button>'+
 '<button type="button" id="mat-add" class="secondary">A + B</button>'+
 '<button type="button" id="mat-subtract" class="secondary">A − B</button>'+
 '<button type="button" id="mat-multiply" class="secondary">A × B</button>'+
 '<button type="button" id="mat-solve" class="secondary">Solve A·x=b</button>'+
 '<button type="button" id="mat-lu" class="secondary">LU (P·A=L·U)</button>'+
 '<button type="button" id="mat-rref" class="secondary">RREF (A)</button>'+ 
 '<button type="button" id="mat-rank" class="secondary">Rank (A)</button>'+
 '<label>LU factor for editor <select id="mat-lu-factor"><option value="L">L</option><option value="U">U</option><option value="P">P</option></select></label>'+
 '<button type="button" id="mat-send" class="secondary" disabled>Send result to Equation Editor</button></div>'+
 '<pre id="mat-result" role="status" aria-live="polite">Enter matrix values and choose an operation.</pre>';
panel.append(area);
const style=el('style',{},'.matrix-tools{border-top:1px solid #dfe5f0;padding:13px 20px 16px}.matrix-tools summary{cursor:pointer;font-weight:700;color:#304cbb}'+
 '.matrix-controls,.matrix-actions{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}.matrix-controls label{display:grid;gap:3px;font-size:13px}'+
 '.matrix-grid{display:grid;gap:7px;max-width:340px}.matrix-grid input{min-width:0;width:100%;padding:9px;border:1px solid #cdd8ec;border-radius:6px;text-align:center}'+
 '#mat-result{background:#f7f9ff;border:1px solid #dfe5f0;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;border-radius:8px}'+
 '#mat-result.error{color:#af2842;background:#fff5f5}');
document.head.append(style);
const grid=document.getElementById('mat-grid'),gridB=document.getElementById('mat-b-grid'),rhsGrid=document.getElementById('mat-rhs-grid'),output=document.getElementById('mat-result'),send=document.getElementById('mat-send');
let last=null;
function rebuild(){
 const old=[...grid.querySelectorAll('input')].map(input=>({r:Number(input.dataset.row),c:Number(input.dataset.col),value:input.value}));
 const rows=Number(document.getElementById('mat-rows').value),cols=Number(document.getElementById('mat-cols').value);
 grid.style.gridTemplateColumns='repeat('+cols+', minmax(0, 1fr))';grid.replaceChildren();
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
  const value=old.find(x=>x.r===r&&x.c===c)?.value;
  const cell=el('input',{type:'number',step:'any','data-row':String(r),'data-col':String(c),'aria-label':'Matrix row '+(r+1)+' column '+(c+1)});
  cell.value=value===undefined?(r===c?'1':'0'):value;cell.addEventListener('input',invalidate);grid.append(cell);
 }
 invalidate();
}
function rebuildSecond(){
 const old=[...gridB.querySelectorAll('input')].map(input=>({r:Number(input.dataset.row),c:Number(input.dataset.col),value:input.value}));
 const rows=Number(document.getElementById('mat-b-rows').value),cols=Number(document.getElementById('mat-b-cols').value);
 gridB.style.gridTemplateColumns='repeat('+cols+', minmax(0, 1fr))';gridB.replaceChildren();
 for(let r=0;r<rows;r++)for(let c=0;c<cols;c++){
  const value=old.find(x=>x.r===r&&x.c===c)?.value;
  const cell=el('input',{type:'number',step:'any','data-row':String(r),'data-col':String(c),'aria-label':'Matrix B row '+(r+1)+' column '+(c+1)});
  cell.value=value===undefined?(r===c?'1':'0'):value;cell.addEventListener('input',invalidate);gridB.append(cell);
 }
 invalidate();
}
function rebuildRhs(){
 const old=[...rhsGrid.querySelectorAll('input')].map(input=>input.value);
 const rows=Number(document.getElementById('mat-rows').value);
 rhsGrid.style.gridTemplateColumns='minmax(0, 1fr)';rhsGrid.replaceChildren();
 for(let r=0;r<rows;r++){
  const cell=el('input',{type:'number',step:'any','aria-label':'Right-hand side b row '+(r+1)});
  cell.value=old[r]===undefined?'0':old[r];cell.addEventListener('input',invalidate);rhsGrid.append(cell);
 }
 invalidate();
}
function readRhs(){return [...rhsGrid.querySelectorAll('input')].map(input=>input.value);}
function invalidate(){last=null;send.disabled=true;output.classList.remove('error');output.textContent='Enter matrix values and choose an operation.';}
function read(){
 const rows=Number(document.getElementById('mat-rows').value),cols=Number(document.getElementById('mat-cols').value);
 return validate(Array.from({length:rows},(_,r)=>Array.from({length:cols},(_,c)=>grid.querySelector('[data-row="'+r+'"][data-col="'+c+'"]').value)));
}
function readSecond(){
 const rows=Number(document.getElementById('mat-b-rows').value),cols=Number(document.getElementById('mat-b-cols').value);
 return validate(Array.from({length:rows},(_,r)=>Array.from({length:cols},(_,c)=>gridB.querySelector('[data-row="'+r+'"][data-col="'+c+'"]').value)));
}
function calculate(operation){
 try{
  const A=read(),value=operation==='determinant'?determinant(A):
   operation==='transpose'?transpose(A):operation==='inverse'?inverse(A):
   operation==='add'?add(A,readSecond()):operation==='subtract'?subtract(A,readSecond()):
   operation==='rref'?rref(A):operation==='rank'?matrixRank(A):operation==='solve'?solve(A,readRhs()):operation==='lu'?lu(A):multiply(A,readSecond());
  last={operation,value};output.classList.remove('error');
  const display=operation==='rref'?value.matrix:operation==='solve'?value.solution.map(x=>[x]):value;
  const rowsText=rows=>rows.map(row=>'[ '+row.map(format).join('   ')+' ]').join('\n');
  output.textContent=operation==='lu'?
   'lu: P·A = L·U\nP:\n'+rowsText(value.P)+'\nL:\n'+rowsText(value.L)+'\nU:\n'+rowsText(value.U)+'\nRelative reconstruction residual: '+format(value.residual):
   operation+':\n'+(typeof display==='number'?format(display):rowsText(display))+
   (operation==='rref'?'\nRank: '+value.rank:operation==='solve'?'\nRelative residual: '+format(value.residual):'');
  send.disabled=false;return last;
 }catch(error){last=null;send.disabled=true;output.classList.add('error');output.textContent=error.message;return null;}
}
for(const [id,op] of [['mat-det','determinant'],['mat-transpose','transpose'],['mat-inverse','inverse'],['mat-add','add'],['mat-subtract','subtract'],['mat-multiply','multiply'],['mat-rref','rref'],['mat-rank','rank'],['mat-solve','solve'],['mat-lu','lu']])
 document.getElementById(id).addEventListener('click',()=>calculate(op));
for(const id of ['mat-rows','mat-cols'])document.getElementById(id).addEventListener('change',()=>{rebuild();rebuildRhs();});
for(const id of ['mat-b-rows','mat-b-cols'])document.getElementById(id).addEventListener('change',rebuildSecond);
send.addEventListener('click',()=>{
 if(!last)return;
 try{M.bridge.transfer('editor',notation(last.operation==='rref'?last.value.matrix:last.operation==='solve'?last.value.solution.map(x=>[x]):last.operation==='lu'?last.value[document.getElementById('mat-lu-factor').value]:last.value),{source:'matrix calculator'});}
 catch(error){output.classList.add('error');output.textContent=error.message;}
});
rebuild();rebuildSecond();rebuildRhs();
M.matrixTools={validate,determinant,transpose,inverse,add,subtract,multiply,rref,rank:matrixRank,solve,lu,notation,read,readSecond,readRhs,calculate};
})();