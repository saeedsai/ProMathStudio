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
 '<p class="small-note">Real-number matrices. Determinant and inverse need a square matrix; transpose works for 2×3 and 3×2. Arithmetic uses approximately 12 significant digits.</p>'+
 '<div class="matrix-controls"><label>Rows <select id="mat-rows"><option value="2">2</option><option value="3">3</option></select></label>'+
 '<label>Columns <select id="mat-cols"><option value="2">2</option><option value="3">3</option></select></label></div>'+
 '<div id="mat-grid" class="matrix-grid" aria-label="Matrix entries"></div>'+
 '<div class="matrix-actions"><button type="button" id="mat-det" class="secondary">Determinant</button>'+
 '<button type="button" id="mat-transpose" class="secondary">Transpose</button>'+
 '<button type="button" id="mat-inverse" class="secondary">Inverse</button>'+
 '<button type="button" id="mat-send" class="secondary" disabled>Send result to Equation Editor</button></div>'+
 '<pre id="mat-result" role="status" aria-live="polite">Enter matrix values and choose an operation.</pre>';
panel.append(area);
const style=el('style',{},'.matrix-tools{border-top:1px solid #dfe5f0;padding:13px 20px 16px}.matrix-tools summary{cursor:pointer;font-weight:700;color:#304cbb}'+
 '.matrix-controls,.matrix-actions{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}.matrix-controls label{display:grid;gap:3px;font-size:13px}'+
 '.matrix-grid{display:grid;gap:7px;max-width:340px}.matrix-grid input{min-width:0;width:100%;padding:9px;border:1px solid #cdd8ec;border-radius:6px;text-align:center}'+
 '#mat-result{background:#f7f9ff;border:1px solid #dfe5f0;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;border-radius:8px}'+
 '#mat-result.error{color:#af2842;background:#fff5f5}');
document.head.append(style);
const grid=document.getElementById('mat-grid'),output=document.getElementById('mat-result'),send=document.getElementById('mat-send');
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
function invalidate(){last=null;send.disabled=true;output.classList.remove('error');output.textContent='Enter matrix values and choose an operation.';}
function read(){
 const rows=Number(document.getElementById('mat-rows').value),cols=Number(document.getElementById('mat-cols').value);
 return validate(Array.from({length:rows},(_,r)=>Array.from({length:cols},(_,c)=>grid.querySelector('[data-row="'+r+'"][data-col="'+c+'"]').value)));
}
function calculate(operation){
 try{
  const A=read(),value=operation==='determinant'?determinant(A):operation==='transpose'?transpose(A):inverse(A);
  last={operation,value};output.classList.remove('error');
  output.textContent=operation+':\n'+(typeof value==='number'?format(value):value.map(row=>'[ '+row.map(format).join('   ')+' ]').join('\n'));
  send.disabled=false;return last;
 }catch(error){last=null;send.disabled=true;output.classList.add('error');output.textContent=error.message;return null;}
}
for(const [id,op] of [['mat-det','determinant'],['mat-transpose','transpose'],['mat-inverse','inverse']])
 document.getElementById(id).addEventListener('click',()=>calculate(op));
for(const id of ['mat-rows','mat-cols'])document.getElementById(id).addEventListener('change',rebuild);
send.addEventListener('click',()=>{
 if(!last)return;
 try{M.bridge.transfer('editor',notation(last.value),{source:'matrix calculator'});}
 catch(error){output.classList.add('error');output.textContent=error.message;}
});
rebuild();
M.matrixTools={validate,determinant,transpose,inverse,notation,read,calculate};
})();