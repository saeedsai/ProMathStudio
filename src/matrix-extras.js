/* Larger-matrix (up to 8x8) linear algebra extras: Cholesky/LDLt, SVD rank and bases, LU determinant,
   characteristic polynomial, norms and conditioning. Pure math core; the DOM panel is optional. */
(()=>{'use strict';
const root=typeof window!=='undefined'?window:globalThis;
const M=root.MathStudio=root.MathStudio||{};
const MAX=8, LIMIT=1e100, EPS=Number.EPSILON;
// Symmetry tolerance: |a_ij - a_ji| <= SYM_TOL * max|a|. Rank tolerance: sigma <= max(m,n)*eps*sigma_max.
const SYM_TOL=1e-10;
const DECIMAL=/^[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/;

function parseMatrix(text){
 if(typeof text!=='string')throw Error('Matrix text must be a string.');
 if(text.length>20000)throw Error('Matrix text is too long.');
 const lines=text.split(/\r?\n|;/).map(line=>line.trim()).filter(line=>line!=='');
 if(!lines.length)throw Error('Enter at least one matrix row.');
 if(lines.length>MAX)throw Error('At most '+MAX+' rows are supported (got '+lines.length+').');
 const rows=lines.map((line,i)=>{
  const parts=line.split(/[\s,]+/).filter(part=>part!=='');
  if(parts.length>MAX)throw Error('Row '+(i+1)+' has '+parts.length+' entries; at most '+MAX+' columns are supported.');
  return parts.map((part,j)=>{
   if(!DECIMAL.test(part))throw Error('Row '+(i+1)+', column '+(j+1)+': "'+part.slice(0,24)+'" is not a decimal number.');
   const value=Number(part);
   if(!Number.isFinite(value)||Math.abs(value)>LIMIT)throw Error('Row '+(i+1)+', column '+(j+1)+' must be finite and at most 1e100 in magnitude.');
   return value;
  });
 });
 const n=rows[0].length;
 rows.forEach((row,i)=>{if(row.length!==n)throw Error('Ragged rows: row '+(i+1)+' has '+row.length+' entries but row 1 has '+n+'.');});
 return rows;
}
function asMatrix(input){
 if(typeof input==='string')return parseMatrix(input);
 if(!Array.isArray(input)||!input.length||input.length>MAX)throw Error('Matrix must have 1 to '+MAX+' rows.');
 const n=Array.isArray(input[0])?input[0].length:0;
 if(!n||n>MAX)throw Error('Matrix must have 1 to '+MAX+' columns.');
 return input.map((row,i)=>{
  if(!Array.isArray(row)||row.length!==n)throw Error('Ragged rows: row '+(i+1)+' does not have '+n+' entries.');
  return row.map(v=>{if(typeof v!=='number'||!Number.isFinite(v)||Math.abs(v)>LIMIT)throw Error('Matrix entries must be finite numbers.');return v;});
 });
}
const zeros=(m,n)=>Array.from({length:m},()=>Array(n).fill(0));
const eye=n=>Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?1:0));
const transpose=A=>A[0].map((_,j)=>A.map(row=>row[j]));
const mul=(A,B)=>A.map(row=>B[0].map((_,j)=>row.reduce((s,a,k)=>s+a*B[k][j],0)));
const frob=A=>Math.sqrt(A.reduce((s,row)=>s+row.reduce((t,v)=>t+v*v,0),0));
const sub=(A,B)=>A.map((row,i)=>row.map((v,j)=>v-B[i][j]));
const relResidual=(A,B)=>{const nA=frob(A);const r=frob(sub(A,B));return nA>0?r/nA:r;};
const maxAbs=A=>A.reduce((s,row)=>Math.max(s,...row.map(Math.abs)),0);
function requireSquare(A,what){if(A.length!==A[0].length)throw Error(what+' requires a square matrix (got '+A.length+'×'+A[0].length+').');}
function requireSymmetric(A,what){
 requireSquare(A,what);const scale=maxAbs(A);
 for(let i=0;i<A.length;i++)for(let j=i+1;j<A.length;j++){
  if(Math.abs(A[i][j]-A[j][i])>SYM_TOL*scale)throw Error(what+' requires a symmetric matrix: a'+(i+1)+(j+1)+' = '+A[i][j]+' but a'+(j+1)+(i+1)+' = '+A[j][i]+' (relative tolerance '+SYM_TOL+').');
 }
}

function cholesky(input){
 const A=asMatrix(input);requireSymmetric(A,'Cholesky');
 const n=A.length,L=zeros(n,n);
 for(let j=0;j<n;j++){
  let d=A[j][j];for(let k=0;k<j;k++)d-=L[j][k]*L[j][k];
  if(!(d>0)||d<=n*EPS*Math.abs(A[j][j]))throw Error('Matrix is not positive definite: pivot '+(j+1)+' is '+d.toPrecision(6)+' (must be > 0). Try LDLᵀ for symmetric indefinite matrices.');
  L[j][j]=Math.sqrt(d);
  for(let i=j+1;i<n;i++){let s=A[i][j];for(let k=0;k<j;k++)s-=L[i][k]*L[j][k];L[i][j]=s/L[j][j];}
 }
 const residual=relResidual(A,mul(L,transpose(L)));
 return {type:'cholesky',n,L,residual,detA:L.reduce((p,row,i)=>p*row[i]*row[i],1),method:'Cholesky A = L·Lᵀ (lower triangular, positive diagonal)'};
}
function ldlt(input){
 const A=asMatrix(input);requireSymmetric(A,'LDLᵀ');
 const n=A.length,L=eye(n),D=Array(n).fill(0),scale=maxAbs(A);
 for(let j=0;j<n;j++){
  let d=A[j][j];for(let k=0;k<j;k++)d-=L[j][k]*L[j][k]*D[k];
  if(Math.abs(d)<=n*EPS*scale)throw Error('LDLᵀ without pivoting broke down: pivot '+(j+1)+' is '+d.toPrecision(6)+' (numerically zero).');
  D[j]=d;
  for(let i=j+1;i<n;i++){let s=A[i][j];for(let k=0;k<j;k++)s-=L[i][k]*L[j][k]*D[k];L[i][j]=s/d;}
 }
 const LD=L.map(row=>row.map((v,k)=>v*D[k]));
 const residual=relResidual(A,mul(LD,transpose(L)));
 const positive=D.filter(d=>d>0).length;
 return {type:'ldlt',n,L,D,residual,inertia:{positive,negative:n-positive,zero:0},method:'LDLᵀ (unit lower L, diagonal D, no pivoting)'};
}

// One-sided Jacobi SVD (Hestenes). Wide matrices are padded with zero rows so V is a full n×n basis.
function svd(input){
 const A=asMatrix(input),m=A.length,n=A[0].length,rows=Math.max(m,n);
 const U=Array.from({length:rows},(_,i)=>i<m?A[i].slice():Array(n).fill(0)),V=eye(n);
 // Columns already at round-off level relative to ‖A‖F are left alone so rank-deficient input converges.
 const fA=frob(A),tiny=(EPS*fA)*(EPS*fA);
 let sweeps=0,converged=false;
 for(;sweeps<80&&!converged;sweeps++){
  converged=true;
  for(let p=0;p<n-1;p++)for(let q=p+1;q<n;q++){
   let alpha=0,beta=0,gamma=0;
   for(let i=0;i<rows;i++){alpha+=U[i][p]*U[i][p];beta+=U[i][q]*U[i][q];gamma+=U[i][p]*U[i][q];}
   if(gamma===0||alpha<=tiny||beta<=tiny||Math.abs(gamma)<=EPS*Math.sqrt(alpha*beta))continue;
   converged=false;
   const zeta=(beta-alpha)/(2*gamma),t=(zeta>=0?1:-1)/(Math.abs(zeta)+Math.sqrt(1+zeta*zeta)),c=1/Math.sqrt(1+t*t),s=c*t;
   for(let i=0;i<rows;i++){const up=U[i][p],uq=U[i][q];U[i][p]=c*up-s*uq;U[i][q]=s*up+c*uq;}
   for(let i=0;i<n;i++){const vp=V[i][p],vq=V[i][q];V[i][p]=c*vp-s*vq;V[i][q]=s*vp+c*vq;}
  }
 }
 if(!converged)throw Error('Jacobi SVD did not converge within 80 sweeps.');
 const norms=Array.from({length:n},(_,j)=>{let s=0;for(let i=0;i<rows;i++)s+=U[i][j]*U[i][j];return Math.sqrt(s);});
 const order=norms.map((_,j)=>j).sort((a,b)=>norms[b]-norms[a]);
 const sigma=order.map(j=>norms[j]),Vs=V.map(row=>order.map(j=>row[j]));
 const Us=Array.from({length:m},(_,i)=>order.map(j=>norms[j]>0?U[i][j]/norms[j]:0));
 const tol=Math.max(m,n)*EPS*(sigma[0]||0);
 const rank=sigma.filter(s=>s>tol).length;
 return {A,m,n,sigma,U:Us,V:Vs,rank,tol,sweeps};
}
function rankBases(input){
 const S=svd(input),{A,m,n,rank}=S;
 const columnBasis=Array.from({length:m},(_,i)=>S.U[i].slice(0,rank));
 const nullBasis=S.V.map(row=>row.slice(rank));
 const nullity=n-rank;
 const AN=nullity?mul(A,nullBasis):[[0]];
 const orth=B=>{if(!B[0]||!B[0].length)return 0;const G=mul(transpose(B),B);return frob(sub(G,eye(G.length)));};
 return {type:'rank',m,n,rank,nullity,singularValues:S.sigma.slice(0,Math.min(m,n)),tolerance:S.tol,columnBasis,nullBasis,
  nullResidual:nullity?frob(AN):0,nullResidualRelative:nullity&&frob(A)>0?frob(AN)/frob(A):0,
  orthogonality:{column:orth(columnBasis),null:orth(nullBasis)},sweeps:S.sweeps,
  method:'One-sided Jacobi SVD; rank counts σ > max(m,n)·eps·σ₁'};
}
function lu(input){
 const A=asMatrix(input);requireSquare(A,'Determinant');
 const n=A.length,U=A.map(r=>r.slice()),L=eye(n),perm=[...Array(n).keys()];let sign=1;
 for(let k=0;k<n;k++){
  let p=k;for(let i=k+1;i<n;i++)if(Math.abs(U[i][k])>Math.abs(U[p][k]))p=i;
  if(p!==k){[U[p],U[k]]=[U[k],U[p]];[perm[p],perm[k]]=[perm[k],perm[p]];for(let j=0;j<k;j++)[L[p][j],L[k][j]]=[L[k][j],L[p][j]];sign=-sign;}
  if(U[k][k]===0)continue;
  for(let i=k+1;i<n;i++){const f=U[i][k]/U[k][k];L[i][k]=f;for(let j=k;j<n;j++)U[i][j]-=f*U[k][j];U[i][k]=0;}
 }
 const PA=perm.map(i=>A[i]);
 return {A,L,U,perm,sign,residual:relResidual(PA,mul(L,U))};
}
function determinant(input){
 const F=lu(input),n=F.A.length;
 const det=F.U.reduce((p,row,i)=>p*row[i],F.sign);
 const trace=F.A.reduce((s,row,i)=>s+row[i],0);
 return {type:'determinant',n,det,trace,L:F.L,U:F.U,perm:F.perm.map(i=>i+1),residual:F.residual,method:'LU with partial pivoting, P·A = L·U'};
}
// Faddeev-LeVerrier: exact in exact arithmetic; loses accuracy for ill-conditioned or badly scaled
// matrices, so the constant term is cross-checked against the LU determinant.
function charpoly(input){
 const A=asMatrix(input);requireSquare(A,'Characteristic polynomial');
 const n=A.length,coeffs=Array(n+1).fill(0);coeffs[0]=1;let Mk=zeros(n,n);
 for(let k=1;k<=n;k++){
  const AM=mul(A,Mk);Mk=AM.map((row,i)=>row.map((v,j)=>i===j?v+coeffs[k-1]:v));
  const AMk=mul(A,Mk);coeffs[k]=-AMk.reduce((s,row,i)=>s+row[i],0)/k;
 }
 const det=determinant(A).det,fromPoly=(n%2?-1:1)*coeffs[n];
 const detCheck=Math.abs(fromPoly-det)/Math.max(1,Math.abs(det));
 return {type:'charpoly',n,coefficients:coeffs,trace:-coeffs[1],det,detCheck,
  method:'Faddeev–LeVerrier, det(λI − A) = Σ cₖ λⁿ⁻ᵏ (c₀ = 1)',
  note:'Coefficients can lose accuracy for ill-conditioned or badly scaled matrices; do not compute eigenvalues from them for n > 4 without care.'};
}
function norms(input){
 const S=svd(input),{A,m,n}=S,k=Math.min(m,n);
 const one=Math.max(...A[0].map((_,j)=>A.reduce((s,row)=>s+Math.abs(row[j]),0)));
 const inf=Math.max(...A.map(row=>row.reduce((s,v)=>s+Math.abs(v),0)));
 const smin=S.sigma[k-1],two=S.sigma[0];
 return {type:'norms',m,n,frobenius:frob(A),one,infinity:inf,two,singularValues:S.sigma.slice(0,k),
  condition2:smin>S.tol?two/smin:Infinity,rank:S.rank,method:'2-norm and κ₂ = σ₁/σₘᵢₙ from one-sided Jacobi SVD'};
}
const OPS={cholesky,ldlt,rank:rankBases,determinant,charpoly,norms};
function compute(input,operation){
 const fn=OPS[operation];if(!fn)throw Error('Unknown matrix operation: '+operation+'.');
 return fn(input);
}

const fmt=v=>!Number.isFinite(v)?String(v):Math.abs(v)<1e-15&&v!==0?v.toExponential(3):Number(v.toPrecision(10)).toString();
const showMatrix=(name,A)=>name+' =\n'+(A.length&&A[0].length?A.map(row=>'  [ '+row.map(v=>fmt(v).padStart(12)).join(' ')+' ]').join('\n'):'  (empty)');
function polyText(c){
 const n=c.length-1;return c.map((v,k)=>{const p=n-k;if(v===0&&k>0)return '';const mag=fmt(Math.abs(v));const term=p===0?mag:(Math.abs(v)===1?'':mag+'·')+'λ'+(p>1?'^'+p:'');return (k===0?(v<0?'−':''):(v<0?' − ':' + '))+term;}).join('');
}
function describe(r){
 switch(r.type){
  case 'cholesky':return [r.method,showMatrix('L',r.L),'det(A) = '+fmt(r.detA),'Reconstruction ‖A − L·Lᵀ‖F/‖A‖F = '+r.residual.toExponential(3)].join('\n');
  case 'ldlt':return [r.method,showMatrix('L',r.L),'D = diag('+r.D.map(fmt).join(', ')+')','Inertia: '+r.inertia.positive+' positive, '+r.inertia.negative+' negative','Reconstruction ‖A − L·D·Lᵀ‖F/‖A‖F = '+r.residual.toExponential(3)].join('\n');
  case 'rank':return [r.method,'Size '+r.m+'×'+r.n+'; rank = '+r.rank+'; nullity = '+r.nullity,'Singular values: '+r.singularValues.map(fmt).join(', '),'Tolerance: '+r.tolerance.toExponential(3),showMatrix('Column-space orthonormal basis (columns)',r.columnBasis),showMatrix('Null-space orthonormal basis (columns)',r.nullBasis),'Verification ‖A·N‖F = '+r.nullResidual.toExponential(3)+'; ‖NᵀN − I‖F = '+r.orthogonality.null.toExponential(3)].join('\n');
  case 'determinant':return [r.method,'det(A) = '+fmt(r.det),'trace(A) = '+fmt(r.trace),'Row permutation: '+r.perm.join(' '),showMatrix('U',r.U),'Reconstruction ‖P·A − L·U‖F/‖A‖F = '+r.residual.toExponential(3)].join('\n');
  case 'charpoly':return [r.method,'p(λ) = '+polyText(r.coefficients),'Coefficients c₀…cₙ: '+r.coefficients.map(fmt).join(', '),'trace = '+fmt(r.trace)+'; det = '+fmt(r.det),'Consistency |(−1)ⁿcₙ − det_LU|/max(1,|det|) = '+r.detCheck.toExponential(3),r.note].join('\n');
  case 'norms':return [r.method,'‖A‖F = '+fmt(r.frobenius),'‖A‖₁ = '+fmt(r.one),'‖A‖∞ = '+fmt(r.infinity),'‖A‖₂ = '+fmt(r.two),'κ₂(A) = '+fmt(r.condition2)+(Number.isFinite(r.condition2)?'':' (rank deficient)'),'Singular values: '+r.singularValues.map(fmt).join(', ')].join('\n');
 }
 return '';
}
function toTable(r){
 const matrixTable=(A,prefix)=>({headers:A[0].map((_,j)=>prefix+(j+1)),rows:A.map(row=>row.slice())});
 switch(r.type){
  case 'cholesky':return {name:'Matrix_Cholesky_L',...matrixTable(r.L,'L_col')};
  case 'ldlt':return {name:'Matrix_LDLt',headers:[...r.L[0].map((_,j)=>'L_col'+(j+1)),'D'],rows:r.L.map((row,i)=>[...row,r.D[i]])};
  case 'rank':return r.nullity?{name:'Matrix_Null_Space',...matrixTable(r.nullBasis,'n')}:{name:'Matrix_Rank',headers:['rank','nullity'],rows:[[r.rank,0]]};
  case 'determinant':return {name:'Matrix_Determinant',headers:['det','trace','lu_residual'],rows:[[r.det,r.trace,r.residual]]};
  case 'charpoly':return {name:'Matrix_Char_Poly',headers:['power','coefficient'],rows:r.coefficients.map((c,k)=>[r.n-k,c])};
  case 'norms':return {name:'Matrix_Norms',headers:['norm','value'],rows:[['frobenius',r.frobenius],['one',r.one],['infinity',r.infinity],['two',r.two],['condition2',Number.isFinite(r.condition2)?r.condition2:'Infinity']]};
 }
 return null;
}
M.matrixExtras={parseMatrix,cholesky,ldlt,svd,rank:rankBases,determinant,charpoly,norms,compute,describe,toTable,operations:Object.keys(OPS),limits:{maxSize:MAX,symmetryTolerance:SYM_TOL}};

const doc=root.document,panel=doc&&doc.getElementById('calculator-panel');
if(!panel)return;
const $=id=>doc.getElementById(id);
const make=(tag,attrs,text)=>{const node=doc.createElement(tag);for(const [k,v] of Object.entries(attrs||{}))node.setAttribute(k,v);if(text!==undefined)node.textContent=text;return node;};
const area=make('details',{id:'matrix-extras-details',class:'matrix-extras'});
area.append(make('summary',{},'Matrix extras · up to 8×8 (Cholesky, rank & bases, det, char. polynomial, norms)'));
area.append(make('p',{},'Enter one row per line; separate entries with spaces or commas. Decimal numbers only.'));
const label=make('label',{for:'matrix-extras-input'},'Matrix A');
const input=make('textarea',{id:'matrix-extras-input',rows:'6',spellcheck:'false',autocomplete:'off'});
input.value='4 12 -16\n12 37 -43\n-16 -43 98';
const opLabel=make('label',{for:'matrix-extras-op'},'Operation');
const select=make('select',{id:'matrix-extras-op'});
for(const [value,text] of [['cholesky','Cholesky A = L·Lᵀ'],['ldlt','LDLᵀ (symmetric)'],['rank','Rank, null space and column space'],['determinant','Determinant and trace (LU)'],['charpoly','Characteristic polynomial'],['norms','Norms and condition number']])select.append(make('option',{value},text));
const bar=make('div',{class:'matrix-extras-bar'});
const run=make('button',{id:'matrix-extras-run',type:'button',class:'primary'},'Run');
const save=make('button',{id:'matrix-extras-to-table',type:'button',class:'secondary',disabled:''},'Save to Data Tables');
bar.append(run,save);
const output=make('pre',{id:'matrix-extras-output',role:'status','aria-live':'polite'},'Choose an operation and press Run.');
area.append(label,input,opLabel,select,bar,output);
panel.append(area);
const style=make('style',{id:'matrix-extras-style'});
style.textContent='.matrix-extras{border-top:1px solid #dfe5f0;padding:13px 20px 16px}.matrix-extras summary{cursor:pointer;font-weight:700;color:#304cbb;min-height:40px;display:flex;align-items:center}'+
 '.matrix-extras label{display:block;font-weight:650;font-size:12px;color:#51617d;margin:10px 0 5px}'+
 '.matrix-extras textarea{width:100%;max-width:100%;box-sizing:border-box;font-family:ui-monospace,monospace;min-height:120px;border:1px solid #d3dbec;border-radius:8px;padding:9px}'+
 '.matrix-extras select{min-height:40px;max-width:100%;box-sizing:border-box;border:1px solid #d3dbec;border-radius:8px;padding:8px}'+
 '.matrix-extras-bar{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0}.matrix-extras-bar button{min-height:40px;min-width:40px}'+
 '#matrix-extras-output{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;overflow-x:auto;box-sizing:border-box;background:#f7f9fd;border:1px solid #e1e7f2;border-radius:8px;padding:10px;font-size:12px}'+
 '#matrix-extras-output.error{color:#a0202a;border-color:#e7a7ad;background:#fff4f5}';
doc.head.append(style);
let last=null;
const invalidate=()=>{last=null;save.disabled=true;output.classList.remove('error');};
input.addEventListener('input',invalidate);select.addEventListener('change',invalidate);
run.addEventListener('click',()=>{
 try{last=compute(input.value,select.value);output.classList.remove('error');output.textContent=describe(last);save.disabled=false;}
 catch(err){invalidate();output.classList.add('error');output.textContent=err.message+'\nFix the matrix text or choose another operation, then press Run again.';}
});
save.addEventListener('click',()=>{
 try{if(!last)throw Error('Run an operation first.');if(!M.dataTables?.importData)throw Error('Data Tables are unavailable.');
  const table=toTable(last);M.dataTables.importData({headers:table.headers,rows:table.rows},table.name);M.advanced?.mode?.('data');}
 catch(err){output.classList.add('error');output.textContent=err.message;}
});
})();
