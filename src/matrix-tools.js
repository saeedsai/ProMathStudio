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
  if((typeof entry!=='number'&&typeof entry!=='string')||String(entry).trim()==='')throw Error('Enter a number in row '+(r+1)+', column '+(c+1)+'.');
  // Matrix input accepts decimal/scientific notation, not JS numeric prefixes (0x, 0b, 0o).
  if(typeof entry==='string'&&!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(entry.trim()))
   throw Error('Matrix entries must use decimal or scientific notation.');
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
  if((typeof entry!=='number'&&typeof entry!=='string')||String(entry).trim()==='')throw Error('Enter a number in b row '+(i+1)+'.');
  if(typeof entry==='string'&&!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(entry.trim()))
   throw Error('Right-hand side b must use decimal or scientific notation.');
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
/* Reorthogonalized modified Gram-Schmidt economy QR for 2<=n<=m<=3. */
function qr(A){
 A=validate(A);
 const m=A.length,n=A[0].length,tolerance=1e-12;
 if(m<n)throw Error('QR requires Matrix A rows to be at least its columns.');
 const Q=Array.from({length:m},()=>Array(n).fill(0));
 const R=Array.from({length:n},()=>Array(n).fill(0));
 for(let j=0;j<n;j++){
  const v=A.map(row=>row[j]),columnNorm=Math.hypot(...v);
  if(!Number.isFinite(columnNorm)||columnNorm===0)
   throw Error('Rank-deficient matrix: QR requires independent columns.');
  for(let pass=0;pass<2;pass++)for(let k=0;k<j;k++){
   let projection=0;
   for(let i=0;i<m;i++)projection+=Q[i][k]*v[i];
   R[k][j]+=projection;
   for(let i=0;i<m;i++)v[i]-=projection*Q[i][k];
  }
  const norm=Math.hypot(...v);
  if(!Number.isFinite(norm)||norm<=tolerance*columnNorm)
   throw Error('Rank-deficient or nearly rank-deficient matrix: QR requires independent columns.');
  R[j][j]=norm;
  for(let i=0;i<m;i++)Q[i][j]=v[i]/norm;
 }
 const magnitude=Math.max(Number.MIN_VALUE,Math.hypot(...A.flat()));
 let residual=0,orthogonality=0;
 for(let i=0;i<m;i++)for(let j=0;j<n;j++){
  let reconstructed=0;
  for(let k=0;k<n;k++)reconstructed+=Q[i][k]*R[k][j];
  residual=Math.max(residual,Math.abs(reconstructed-A[i][j])/magnitude);
 }
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){
  let dot=0;for(let k=0;k<m;k++)dot+=Q[k][i]*Q[k][j];
  orthogonality=Math.max(orthogonality,Math.abs(dot-Number(i===j)));
 }
 if(!Number.isFinite(residual)||!Number.isFinite(orthogonality)||residual>1e-8||orthogonality>1e-8)
  throw Error('QR decomposition failed its numerical reconstruction or orthogonality check.');
 return {Q,R,residual,orthogonality};
}
/* Shared strict RHS parsing for ordinary and weighted least squares.
   Do not let Number() silently accept hexadecimal, binary or array coercion. */
function parseLeastSquaresRhs(b,m){
 if(!Array.isArray(b)||b.length!==m)throw Error('Right-hand side b must contain '+m+' values.');
 return b.map((entry,i)=>{
  if(entry===null||typeof entry==='boolean'||
     (typeof entry!=='number'&&typeof entry!=='string')||String(entry).trim()==='')
   throw Error('Enter a number in b row '+(i+1)+'.');
  if(typeof entry==='string'&&!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(entry.trim()))
   throw Error('Right-hand side b must use decimal or scientific notation at row '+(i+1)+'.');
  const value=Number(entry);
  if(!Number.isFinite(value)||Math.abs(value)>MAX_ENTRY)
   throw Error('Right-hand side b must contain finite numbers with magnitude at most 1e12.');
  return value;
 });
}
/* Bounded full-rank tall 3x2 least squares via existing QR; no normal-equation solve. */
function leastSquares(A,b){
 A=validate(A);
 const m=A.length,n=A[0].length;
 if(m<=n)throw Error('Least squares requires a tall matrix (3 rows, 2 columns).');
 const rhs=parseLeastSquaresRhs(b,m);
 const {Q,R}=qr(A);
 const projected=Array.from({length:n},(_,j)=>Q.reduce((sum,row,i)=>sum+row[j]*rhs[i],0));
 const solution=Array(n).fill(0);
 for(let i=n-1;i>=0;i--){
  let value=projected[i];
  for(let j=i+1;j<n;j++)value-=R[i][j]*solution[j];
  solution[i]=value/R[i][i];
  if(!Number.isFinite(solution[i]))throw Error('Least-squares solution exceeded finite floating-point range.');
 }
 const errors=A.map((row,i)=>row.reduce((sum,entry,j)=>sum+entry*solution[j],0)-rhs[i]);
 const residual=Math.hypot(...errors);
 const aNorm=Math.hypot(...A.flat()),xNorm=Math.hypot(...solution),bNorm=Math.hypot(...rhs);
 const relativeResidual=residual/Math.max(Number.MIN_VALUE,bNorm+aNorm*xNorm);
 // When the fit is already at rounding-error scale, normalizing by its
 // vanishing residual magnifies cancellation and gives a false rejection.
 let normalResidual=0;
 if(relativeResidual>1e-12)for(let j=0;j<n;j++){
  let dot=0;
  for(let i=0;i<m;i++)dot+=A[i][j]*errors[i];
  normalResidual=Math.max(normalResidual,Math.abs(dot)/Math.max(Number.MIN_VALUE,aNorm*residual));
 }
 if(![residual,relativeResidual,normalResidual].every(Number.isFinite))
  throw Error('Least-squares residual exceeded finite floating-point range.');
 if(normalResidual>1e-8)throw Error('Least-squares solution failed its orthogonality check.');
 return {solution,residual,relativeResidual,normalResidual,rank:n};
}
/* Weighted least squares for three observations and two parameters.
   Positive observation weights express relative confidence. Reuse the existing
   QR-based least-squares kernel; do not form ill-conditioned normal equations. */
function weightedLeastSquares(A,b,weights){
 A=validate(A);
 const m=A.length,n=A[0].length;
 if(m!==3||n!==2)throw Error('Weighted least squares requires a 3×2 matrix.');
 if(!Array.isArray(weights)||weights.length!==m)throw Error('Weights must contain 3 positive values.');
 const rhs=parseLeastSquaresRhs(b,m);
 const w=weights.map((v,i)=>{
  if(v===null||typeof v==='boolean'||(typeof v!=='number'&&typeof v!=='string')||String(v).trim()===''||
    typeof v==='string'&&!/^[+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(v.trim()))
   throw Error('Invalid positive weight at row '+(i+1)+'.');
  const x=Number(v);if(!Number.isFinite(x)||x<=0||x>1e12||x<1e-12)
   throw Error('Weights must be finite and between 1e-12 and 1e12.');
  return x;
 });
 // A common positive scale factor does not change the fitted parameters.
 const maxWeight=Math.max(...w);
 const scales=w.map(x=>Math.sqrt(x/maxWeight));
 const transformed=A.map((row,i)=>row.map(x=>x*scales[i]));
 const transformedB=rhs.map((x,i)=>x*scales[i]);
 const result=leastSquares(transformed,transformedB);
 const errors=A.map((row,i)=>row.reduce((sum,x,j)=>sum+x*result.solution[j],0)-rhs[i]);
 const weightedResidual=Math.hypot(...errors.map((e,i)=>e*scales[i]));
 const weightedResidualSquared=weightedResidual*weightedResidual*maxWeight;
 if(!Number.isFinite(weightedResidualSquared))
  throw Error('Weighted residual exceeded finite floating-point range.');
 return {...result,weightedResidualSquared,weightScale:maxWeight,
  residuals:errors,weights:w.slice()};
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
/* Jacobi rotations for bounded real symmetric 2x2/3x3 matrices. Columns of
   vectors are orthonormal eigenvectors; eigenvalues are descending. */
function eigenSymmetric(A){
 A=validate(A);requireSquare(A);
 const n=A.length,scale=Math.max(...A.flat().map(Math.abs));
 for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)
  if(Math.abs(A[i][j]-A[j][i])>1e-12*scale)
   throw Error('Eigenanalysis requires a real symmetric matrix.');
 const B=A.map(row=>row.map(x=>scale?x/scale:0));
 const V=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>Number(i===j)));
 let iterations=0;
 for(;iterations<64;iterations++){
  let p=0,q=1,off=Math.abs(B[0][1]);
  for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)
   if(Math.abs(B[i][j])>off){p=i;q=j;off=Math.abs(B[i][j]);}
  if(off<=1e-14)break;
  const apq=B[p][q],tau=(B[q][q]-B[p][p])/(2*apq);
  const t=(tau<0?-1:1)/(Math.abs(tau)+Math.hypot(1,tau));
  const c=1/Math.hypot(1,t),s=t*c;
  const app=B[p][p],aqq=B[q][q];
  B[p][p]=app-t*apq;B[q][q]=aqq+t*apq;B[p][q]=0;B[q][p]=0;
  for(let k=0;k<n;k++)if(k!==p&&k!==q){
   const bkp=B[k][p],bkq=B[k][q];
   B[k][p]=B[p][k]=c*bkp-s*bkq;
   B[k][q]=B[q][k]=s*bkp+c*bkq;
  }
  for(let k=0;k<n;k++){
   const vkp=V[k][p],vkq=V[k][q];
   V[k][p]=c*vkp-s*vkq;V[k][q]=s*vkp+c*vkq;
  }
 }
 if(iterations===64)throw Error('Symmetric eigenanalysis did not converge.');
 const order=Array.from({length:n},(_,i)=>i).sort((i,j)=>B[j][j]-B[i][i]||i-j);
 const values=order.map(i=>B[i][i]*scale);
 const vectors=V.map(row=>order.map(i=>row[i]));
 for(let j=0;j<n;j++){
  let pivot=0;
  for(let i=1;i<n;i++)if(Math.abs(vectors[i][j])>Math.abs(vectors[pivot][j]))pivot=i;
  if(vectors[pivot][j]<0)for(let i=0;i<n;i++)vectors[i][j]=-vectors[i][j];
 }
 let residual=0,reconstructionResidual=0,orthogonality=0;
 const denom=Math.max(scale,Number.MIN_VALUE);
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){
  let av=0,reconstruction=0,vtv=0;
  for(let k=0;k<n;k++){
   av+=A[i][k]*vectors[k][j];
   reconstruction+=vectors[i][k]*values[k]*vectors[j][k];
   vtv+=vectors[k][i]*vectors[k][j];
  }
  residual=Math.max(residual,Math.abs(av-values[j]*vectors[i][j])/denom);
  reconstructionResidual=Math.max(reconstructionResidual,Math.abs(reconstruction-A[i][j])/denom);
  orthogonality=Math.max(orthogonality,Math.abs(vtv-Number(i===j)));
 }
 if(![...values,...vectors.flat(),residual,reconstructionResidual,orthogonality].every(Number.isFinite)
  ||residual>1e-8||reconstructionResidual>1e-8||orthogonality>1e-8)
  throw Error('Symmetric eigenanalysis failed numerical residual or orthogonality checks.');
 return {values,vectors,residual,reconstructionResidual,orthogonality,iterations};
}
/* Scaled one-sided Jacobi SVD for real 2×2 matrices. The small singular
   value uses the determinant to avoid cancellation in AᵀA near rank loss. */
function svd2x2(A){
 A=validate(A);
 if(A.length!==2||A[0].length!==2)throw Error('SVD requires a 2×2 real matrix.');
 const scale=Math.max(...A.flat().map(Math.abs));
 if(scale===0)return {U:[[1,0],[0,1]],S:[0,0],V:[[1,0],[0,1]],rank:0,conditionNumber:null,residual:0,orthogonalityU:0,orthogonalityV:0};
 const [[a,b],[c,d]]=A.map(row=>row.map(x=>x/scale));
 const g00=a*a+c*c,g11=b*b+d*d,g01=a*b+c*d;
 let co=1,si=0;
 if(g01!==0){
  const tau=(g11-g00)/(2*g01);
  const t=(tau<0?-1:1)/(Math.abs(tau)+Math.hypot(1,tau));
  co=1/Math.hypot(1,t);si=t*co;
 }
 let V=[[co,si],[-si,co]];
 let b0=[a*co-b*si,c*co-d*si],b1=[a*si+b*co,c*si+d*co];
 let s0=Math.hypot(...b0),s1=Math.hypot(...b1);
 if(s1>s0){[s0,s1]=[s1,s0];[b0,b1]=[b1,b0];V=V.map(row=>[row[1],row[0]]);}
 const det=a*d-b*c;
 const sSmall=Math.abs(det)/s0;
 const U0=b0.map(x=>x/s0);
 const detV=V[0][0]*V[1][1]-V[0][1]*V[1][0];
 const sign=det===0?1:(det*detV<0?-1:1);
 const U=[[U0[0],-sign*U0[1]],[U0[1],sign*U0[0]]];
 const S=[s0*scale,sSmall*scale];
 const rank=S[1]>1e-12*S[0]?2:1;
 let residual=0,orthogonalityU=0,orthogonalityV=0;
 for(let i=0;i<2;i++)for(let j=0;j<2;j++){
  const reconstructed=U[i][0]*S[0]*V[j][0]+U[i][1]*S[1]*V[j][1];
  residual=Math.max(residual,Math.abs(reconstructed-A[i][j])/scale);
  let dotU=0,dotV=0;
  for(let k=0;k<2;k++){dotU+=U[k][i]*U[k][j];dotV+=V[k][i]*V[k][j];}
  orthogonalityU=Math.max(orthogonalityU,Math.abs(dotU-Number(i===j)));
  orthogonalityV=Math.max(orthogonalityV,Math.abs(dotV-Number(i===j)));
 }
 if(![...S,...U.flat(),...V.flat(),residual,orthogonalityU,orthogonalityV].every(Number.isFinite)||residual>1e-8||orthogonalityU>1e-8||orthogonalityV>1e-8)
  throw Error('SVD failed numerical reconstruction or orthogonality checks.');
 const ratio=S[1]>0?S[0]/S[1]:Infinity;
 return {U,S,V,rank,conditionNumber:Number.isFinite(ratio)?ratio:null,residual,orthogonalityU,orthogonalityV};
}
/* One-sided Jacobi SVD for bounded real 3×3 matrices, including rank loss.
   Rotate columns directly, avoiding squaring the condition number via AᵀA.
   Complete null-space directions orthogonally and verify reconstruction. */
function svd3x3(A){
 A=validate(A);
 if(A.length!==3||A[0].length!==3)throw Error('SVD requires a 3×3 real matrix.');
 const identity=()=>Array.from({length:3},(_,i)=>Array.from({length:3},(_,j)=>Number(i===j)));
 const scale=Math.max(...A.flat().map(Math.abs));
 if(scale===0)return {U:identity(),S:[0,0,0],V:identity(),rank:0,cutoff:0,conditionNumber:null,conditionAssessment:'rank deficient',residual:0,orthogonalityU:0,orthogonalityV:0};
 const B=A.map(row=>row.map(x=>x/scale)),V=identity();
 let converged=false;
 for(let sweep=0;sweep<64;sweep++){
  let changed=false;
  for(let p=0;p<2;p++)for(let q=p+1;q<3;q++){
   let aa=0,bb=0,ab=0;
   for(let i=0;i<3;i++){aa+=B[i][p]*B[i][p];bb+=B[i][q]*B[i][q];ab+=B[i][p]*B[i][q];}
   if(aa===0||bb===0||Math.abs(ab)<=1e-14*Math.sqrt(aa)*Math.sqrt(bb))continue;
   changed=true;
   const tau=(bb-aa)/(2*ab),t=(tau<0?-1:1)/(Math.abs(tau)+Math.hypot(1,tau));
   const c=1/Math.hypot(1,t),sn=c*t;
   for(let i=0;i<3;i++){
    const bp=B[i][p],bq=B[i][q],vp=V[i][p],vq=V[i][q];
    B[i][p]=c*bp-sn*bq;B[i][q]=sn*bp+c*bq;
    V[i][p]=c*vp-sn*vq;V[i][q]=sn*vp+c*vq;
   }
  }
  if(!changed){converged=true;break;}
 }
 if(!converged)throw Error('3×3 SVD Jacobi rotations did not converge.');
 const values=Array.from({length:3},(_,j)=>Math.hypot(...B.map(row=>row[j])));
 const order=[0,1,2].sort((i,j)=>values[j]-values[i]||i-j);
 const S=order.map(k=>values[k]*scale),cutoff=1e-12*values[order[0]];
 const rank=order.filter(k=>values[k]>cutoff).length;
 const sortedV=V.map(row=>order.map(k=>row[k]));
 let U=Array.from({length:3},()=>[0,0,0]);
 for(let j=0;j<rank;j++){
  const k=order[j];
  for(let i=0;i<3;i++)U[i][j]=B[i][k]/values[k];
 }
 const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
 if(rank===0)U=identity();
 else if(rank<3){
  if(rank===1){
   const u=U.map(row=>row[0]);
   const axis=[0,1,2].sort((a,b)=>Math.abs(u[a])-Math.abs(u[b]))[0];
   const v=[0,1,2].map(i=>Number(i===axis)-u[axis]*u[i]);
   const norm=Math.hypot(...v);
   for(let i=0;i<3;i++)U[i][1]=v[i]/norm;
  }
  const a=U.map(row=>row[0]),b=U.map(row=>row[1]);
  const v=cross(a,b),norm=Math.hypot(...v);
  if(norm===0)throw Error('3×3 SVD null-space completion failed.');
  for(let i=0;i<3;i++)U[i][2]=v[i]/norm;
 }
 let residual=0,orthogonalityU=0,orthogonalityV=0;
 for(let i=0;i<3;i++)for(let j=0;j<3;j++){
  let reconstructed=0,uu=0,vv=0;
  for(let k=0;k<3;k++){
   reconstructed+=U[i][k]*S[k]*sortedV[j][k];
   uu+=U[k][i]*U[k][j];vv+=sortedV[k][i]*sortedV[k][j];
  }
  residual=Math.max(residual,Math.abs(reconstructed-A[i][j])/scale);
  orthogonalityU=Math.max(orthogonalityU,Math.abs(uu-Number(i===j)));
  orthogonalityV=Math.max(orthogonalityV,Math.abs(vv-Number(i===j)));
 }
 if(![...S,...U.flat(),...sortedV.flat(),residual,orthogonalityU,orthogonalityV].every(Number.isFinite)
  ||residual>1e-8||orthogonalityU>1e-8||orthogonalityV>1e-8)
  throw Error('3×3 SVD failed numerical reconstruction or orthogonality checks.');
 // The scaled singular-value ratio avoids overflow/underflow in the
 // condition estimate for tiny or very large, but otherwise well-scaled A.
 const conditionNumber=rank===3?values[order[0]]/values[order[2]]:Infinity;
 const conditionAssessment=rank<3?'rank deficient':conditionNumber>=1e8?'ill-conditioned':
  conditionNumber>=1e4?'moderately conditioned':'well-conditioned';
 return {U,S,V:sortedV,rank,cutoff:cutoff*scale,
  conditionNumber:Number.isFinite(conditionNumber)?conditionNumber:null,conditionAssessment,
  residual,orthogonalityU,orthogonalityV};
}
/* Thin real 3×2 SVD using scaled, pivoted and reorthogonalized QR followed
   by the existing 2×2 SVD. Q has two orthonormal columns; singular vectors
   are returned as U(3×2), S(2), V(2×2), including rank-deficient cases. */
function svd3x2(A){
 A=validate(A);
 if(A.length!==3||A[0].length!==2)throw Error('SVD requires a 3×2 real matrix.');
 const scale=Math.max(...A.flat().map(Math.abs));
 if(scale===0)return {U:[[1,0],[0,1],[0,0]],S:[0,0],V:[[1,0],[0,1]],
  rank:0,cutoff:0,conditionNumber:null,conditionAssessment:'rank deficient',residual:0,orthogonalityU:0,orthogonalityV:0};
 const C=A.map(row=>row.map(x=>x/scale));
 const norms=[Math.hypot(...C.map(row=>row[0])),Math.hypot(...C.map(row=>row[1]))];
 const first=norms[0]>=norms[1]?0:1,second=1-first;
 const r00=norms[first],q0=C.map(row=>row[first]/r00);
 let r01=q0.reduce((sum,x,i)=>sum+x*C[i][second],0);
 let u1=C.map((row,i)=>row[second]-r01*q0[i]);
 // Reorthogonalize to preserve the small singular direction.
 for(let pass=0;pass<2;pass++){
  const correction=q0.reduce((sum,x,i)=>sum+x*u1[i],0);
  u1=u1.map((x,i)=>x-correction*q0[i]);r01+=correction;
 }
 const r11=Math.hypot(...u1);
 let q1;
 if(r11>0)q1=u1.map(x=>x/r11);
 else{
  const axis=[0,1,2].sort((i,j)=>Math.abs(q0[i])-Math.abs(q0[j]))[0];
  const v=q0.map((x,i)=>Number(i===axis)-q0[axis]*x),norm=Math.hypot(...v);
  q1=v.map(x=>x/norm);
 }
 const R=[[r00,r01],[0,r11]];
 const factors=svd2x2(R);
 const U=Array.from({length:3},(_,i)=>[
  q0[i]*factors.U[0][0]+q1[i]*factors.U[1][0],
  q0[i]*factors.U[0][1]+q1[i]*factors.U[1][1]]);
 const V=Array.from({length:2},()=>[0,0]);
 V[first]=factors.V[0].slice();V[second]=factors.V[1].slice();
 // Rank cutoff and condition ratio use normalized QR singular values, avoiding
 // unnecessary scale-dependent loss in the diagnostic for tiny/large inputs.
 const S=factors.S.map(x=>x*scale),rank=factors.rank,cutoff=1e-12*factors.S[0]*scale;
 let residual=0,orthogonalityU=0,orthogonalityV=0;
 for(let i=0;i<3;i++)for(let j=0;j<2;j++){
  const reconstructed=U[i][0]*S[0]*V[j][0]+U[i][1]*S[1]*V[j][1];
  residual=Math.max(residual,Math.abs(reconstructed-A[i][j])/scale);
 }
 for(let i=0;i<2;i++)for(let j=0;j<2;j++){
  let uu=0,vv=0;
  for(let k=0;k<3;k++)uu+=U[k][i]*U[k][j];
  for(let k=0;k<2;k++)vv+=V[k][i]*V[k][j];
  orthogonalityU=Math.max(orthogonalityU,Math.abs(uu-Number(i===j)));
  orthogonalityV=Math.max(orthogonalityV,Math.abs(vv-Number(i===j)));
 }
 if(![...S,...U.flat(),...V.flat(),residual,orthogonalityU,orthogonalityV].every(Number.isFinite)
  ||residual>1e-8||orthogonalityU>1e-8||orthogonalityV>1e-8)
  throw Error('3×2 SVD failed numerical reconstruction or orthogonality checks.');
 const ratio=rank===2?factors.S[0]/factors.S[1]:Infinity;
 const conditionAssessment=rank<2?'rank deficient':ratio>=1e8?'ill-conditioned':ratio>=1e4?'moderately conditioned':'well-conditioned';
 return {U,S,V,rank,cutoff,conditionNumber:Number.isFinite(ratio)?ratio:null,
  conditionAssessment,residual,orthogonalityU,orthogonalityV};
}
/* Thin wide 2×3 SVD by transposing the validated 3×2 SVD.
   If Aᵀ=Uₜ·diag(S)·Vₜᵀ, then A=Vₜ·diag(S)·Uₜᵀ.
   Swap both factor shapes and orthogonality diagnostics without rounding. */
function svd2x3(A){
 A=validate(A);
 if(A.length!==2||A[0].length!==3)throw Error('SVD requires a 2×3 real matrix.');
 const tall=A[0].map((_,j)=>A.map(row=>row[j]));
 const factors=svd3x2(tall);
 return {...factors,U:factors.V.map(row=>row.slice()),V:factors.U.map(row=>row.slice()),
  orthogonalityU:factors.orthogonalityV,orthogonalityV:factors.orthogonalityU};
}
/* Moore-Penrose pseudoinverse of a real 2×2 matrix, including rank-deficient
   inputs. Reuse the scaled SVD and its relative 1e-12 rank threshold. */
function pseudoinverse2x2(A){
 A=validate(A);
 if(A.length!==2||A[0].length!==2)throw Error('Pseudoinverse requires a 2×2 real matrix.');
 const {U,S,V,rank,conditionNumber}=svd2x2(A);
 const cutoff=1e-12*S[0];
 const reciprocal=S.map(value=>value>cutoff?1/value:0);
 const matrix=Array.from({length:2},(_,i)=>Array.from({length:2},(_,j)=>
  V[i][0]*reciprocal[0]*U[j][0]+V[i][1]*reciprocal[1]*U[j][1]));
 if(!matrix.flat().every(Number.isFinite))throw Error('Pseudoinverse exceeded finite floating-point range.');
 // Verify all four Moore-Penrose identities without routing large inverse
 // entries through the input validator (which is bounded to 1e12).
 const matmul=(X,Y)=>X.map(row=>Y[0].map((_,j)=>row.reduce((sum,x,k)=>sum+x*Y[k][j],0)));
 const AAplus=matmul(A,matrix),AplusA=matmul(matrix,A);
 const tripleA=matmul(AAplus,A),triplePlus=matmul(AplusA,matrix);
 const normA=Math.max(Number.MIN_VALUE,...A.flat().map(Math.abs));
 const normPlus=Math.max(Number.MIN_VALUE,...matrix.flat().map(Math.abs));
 let residual=0,symmetryResidual=0;
 for(let i=0;i<2;i++)for(let j=0;j<2;j++){
  residual=Math.max(residual,Math.abs(tripleA[i][j]-A[i][j])/normA,
   Math.abs(triplePlus[i][j]-matrix[i][j])/normPlus);
  symmetryResidual=Math.max(symmetryResidual,Math.abs(AAplus[i][j]-AAplus[j][i]),
   Math.abs(AplusA[i][j]-AplusA[j][i]));
 }
 if(!Number.isFinite(residual)||!Number.isFinite(symmetryResidual)||residual>1e-8||symmetryResidual>1e-8)
  throw Error('Pseudoinverse failed its Moore-Penrose residual check.');
 // Report finite conditioning only when both singular directions pass the rank cutoff.
 return {matrix,rank,cutoff,conditionNumber:rank===2?conditionNumber:null,
  singularValues:S.slice(),residual,symmetryResidual};
}
/* Scaled pivoted QR pseudoinverse for real 3×2 matrices. The smaller singular
   value comes from det(R)/sigmaMax(R), avoiding cancellation in nearly equal
   columns. Reorthogonalization and all four Moore-Penrose checks protect QA. */
function pseudoinverse3x2(A){
 A=validate(A);
 if(A.length!==3||A[0].length!==2)throw Error('Pseudoinverse requires a 3×2 real matrix.');
 const scale=Math.max(...A.flat().map(Math.abs));
 if(scale===0)return {matrix:[[0,0,0],[0,0,0]],rank:0,cutoff:0,conditionNumber:null,singularValues:[0,0],residual:0,symmetryResidual:0};
 const C=A.map(row=>row.map(x=>x/scale));
 const norms=[Math.hypot(...C.map(row=>row[0])),Math.hypot(...C.map(row=>row[1]))];
 const first=norms[0]>=norms[1]?0:1,second=1-first;
 const r00=norms[first],q0=C.map(row=>row[first]/r00);
 let r01=q0.reduce((sum,x,i)=>sum+x*C[i][second],0);
 let u1=C.map((row,i)=>row[second]-r01*q0[i]);
 const correction=q0.reduce((sum,x,i)=>sum+x*u1[i],0);
 u1=u1.map((x,i)=>x-correction*q0[i]);r01+=correction;
 const r11=Math.hypot(...u1),frob2=r00*r00+r01*r01+r11*r11,det=r00*r11;
 const sMax=Math.sqrt((frob2+Math.sqrt(Math.max(0,frob2*frob2-4*det*det)))/2);
 const sMin=det/sMax,cutoff=1e-12*sMax,rank=sMin>cutoff?2:1;
 let matrix;
 if(rank===1){
  matrix=Array.from({length:2},(_,i)=>C.map(row=>row[i]/(frob2*scale)));
 }else{
  const q1=u1.map(x=>x/r11);
  matrix=Array.from({length:2},()=>Array(3).fill(0));
  matrix[first]=q0.map((x,j)=>(x/r00-(r01/(r00*r11))*q1[j])/scale);
  matrix[second]=q1.map(x=>x/(r11*scale));
 }
 if(!matrix.flat().every(Number.isFinite))throw Error('Pseudoinverse exceeded finite floating-point range.');
 const matmul=(X,Y)=>X.map(row=>Y[0].map((_,j)=>row.reduce((sum,x,k)=>sum+x*Y[k][j],0)));
 const AAplus=matmul(A,matrix),AplusA=matmul(matrix,A);
 const tripleA=matmul(AAplus,A),triplePlus=matmul(AplusA,matrix);
 const normA=Math.max(Number.MIN_VALUE,...A.flat().map(Math.abs));
 const normPlus=Math.max(Number.MIN_VALUE,...matrix.flat().map(Math.abs));
 let residual=0,symmetryResidual=0;
 for(let i=0;i<3;i++)for(let j=0;j<2;j++){
  residual=Math.max(residual,Math.abs(tripleA[i][j]-A[i][j])/normA,
   Math.abs(triplePlus[j][i]-matrix[j][i])/normPlus);
 }
 for(let i=0;i<3;i++)for(let j=0;j<3;j++)
  symmetryResidual=Math.max(symmetryResidual,Math.abs(AAplus[i][j]-AAplus[j][i]));
 for(let i=0;i<2;i++)for(let j=0;j<2;j++)
  symmetryResidual=Math.max(symmetryResidual,Math.abs(AplusA[i][j]-AplusA[j][i]));
 if(!Number.isFinite(residual)||!Number.isFinite(symmetryResidual)||residual>1e-8||symmetryResidual>1e-8)
  throw Error('Pseudoinverse is numerically unstable for this ill-conditioned matrix; rescale or use higher precision.');
 return {matrix,rank,cutoff:cutoff*scale,conditionNumber:rank===2?sMax/sMin:null,
  singularValues:[sMax*scale,sMin*scale],residual,symmetryResidual};
}
/* Wide 2×3 Moore–Penrose inverse via (Aᵀ)⁺ᵀ. This uses the same
   scaled QR rank cutoff and four-identity verification as 3×2. */
function pseudoinverse2x3(A){
 A=validate(A);
 if(A.length!==2||A[0].length!==3)throw Error('Pseudoinverse requires a 2×3 real matrix.');
 const tall=A[0].map((_,j)=>A.map(row=>row[j]));
 const result=pseudoinverse3x2(tall);
 const matrix=result.matrix[0].map((_,j)=>result.matrix.map(row=>row[j]));
 return {...result,matrix};
}
/* Scaled one-sided Jacobi SVD for bounded real 3×3 Moore–Penrose inverse.
   Rotate columns directly (not AᵀA) to preserve small singular directions.
   Reject unstable results using all four Moore–Penrose identities. */
function pseudoinverse3x3(A){
 A=validate(A);
 if(A.length!==3||A[0].length!==3)throw Error('Pseudoinverse requires a 3×3 real matrix.');
 const scale=Math.max(...A.flat().map(Math.abs));
 if(scale===0)return {matrix:Array.from({length:3},()=>[0,0,0]),rank:0,cutoff:0,conditionNumber:null,conditionAssessment:'rank deficient',singularValues:[0,0,0],residual:0,symmetryResidual:0};
 // Reuse the independently residual-checked 3×3 Jacobi SVD instead of
 // maintaining a second, potentially divergent singular-vector iteration.
 const {U,S,V,rank,conditionNumber}=svd3x3(A);
 const cutoff=1e-12*S[0];
 const matrix=Array.from({length:3},(_,i)=>Array.from({length:3},(_,j)=>{
  let value=0;
  for(let k=0;k<3;k++)if(S[k]>cutoff)value+=(V[i][k]/S[k])*U[j][k];
  return value;
 }));
 if(!matrix.flat().every(Number.isFinite))throw Error('Pseudoinverse exceeded finite floating-point range.');
 const matmul=(X,Y)=>X.map(row=>Y[0].map((_,j)=>row.reduce((sum,x,k)=>sum+x*Y[k][j],0)));
 const AAplus=matmul(A,matrix),AplusA=matmul(matrix,A);
 const tripleA=matmul(AAplus,A),triplePlus=matmul(AplusA,matrix);
 const normA=Math.max(Number.MIN_VALUE,...A.flat().map(Math.abs));
 const normPlus=Math.max(Number.MIN_VALUE,...matrix.flat().map(Math.abs));
 let residual=0,symmetryResidual=0;
 for(let i=0;i<3;i++)for(let j=0;j<3;j++){
  residual=Math.max(residual,Math.abs(tripleA[i][j]-A[i][j])/normA,
   Math.abs(triplePlus[i][j]-matrix[i][j])/normPlus);
  symmetryResidual=Math.max(symmetryResidual,Math.abs(AAplus[i][j]-AAplus[j][i]),
   Math.abs(AplusA[i][j]-AplusA[j][i]));
 }
 if(!Number.isFinite(residual)||!Number.isFinite(symmetryResidual)||residual>1e-8||symmetryResidual>1e-8)
  throw Error('Pseudoinverse is numerically unstable for this ill-conditioned 3×3 matrix; rescale or use higher precision.');
 const ratio=rank===3?conditionNumber:Infinity;
 // Advisory only: a full-rank but large condition number amplifies rounding.
 // Do not weaken the four Moore-Penrose identity gates to accept unstable inputs.
 const conditionAssessment=rank<3?'rank deficient':ratio>=1e8?'ill-conditioned':ratio>=1e4?'moderately conditioned':'well-conditioned';
 return {matrix,rank,cutoff,conditionNumber:rank===3?conditionNumber:null,
  singularValues:S.slice(),conditionAssessment,residual,symmetryResidual};
}
function pseudoinverse(A){
 A=validate(A);
 if(A.length===2&&A[0].length===2)return pseudoinverse2x2(A);
 if(A.length===3&&A[0].length===2)return pseudoinverse3x2(A);
 if(A.length===2&&A[0].length===3)return pseudoinverse2x3(A);
 if(A.length===3&&A[0].length===3)return pseudoinverse3x3(A);
 throw Error('Pseudoinverse requires a 2×2, 3×2, 2×3 or 3×3 real matrix.');
}
function format(x){
 if(!Number.isFinite(x))throw Error('Result exceeded finite floating-point range.');
 if(x===0)return '0';
 return Number(x.toPrecision(12)).toString();
}
function notation(result){return typeof result==='number'?format(result):'matrix('+result.map(row=>'['+row.map(format).join(',')+']').join(',')+')';}
const area=el('details',{id:'matrix-tools',class:'matrix-tools'});
area.innerHTML='<summary>Matrix calculator · 2×2 / 3×3</summary>'+
 '<p class="small-note">Real-number matrices (2 or 3 rows/columns). Determinant and inverse require a square A; transpose, RREF/rank and binary arithmetic support rectangular shapes. LU requires a full-rank square A; QR requires rows ≥ columns and independent columns. Least squares requires a full-rank tall 3×2 A; weighted least squares also accepts three positive relative observation weights (1e-12 to 1e12). Eigenanalysis requires symmetric square A. SVD supports real 2×2, 3×2, 2×3 and 3×3 A; pseudoinverse supports real 2×2, 3×2, 2×3 and 3×3 A, including singular/zero matrices, with a relative 1e-12 singular-value cutoff, condition diagnostics and verified Moore–Penrose residuals. SVD reports U, singular values and V with reconstruction/orthogonality residuals. Results display about 12 significant digits.</p>'+
 '<div class="matrix-controls"><label>Rows <select id="mat-rows"><option value="2">2</option><option value="3">3</option></select></label>'+
 '<label>Columns <select id="mat-cols"><option value="2">2</option><option value="3">3</option></select></label></div>'+
 '<div id="mat-grid" class="matrix-grid" aria-label="Matrix A entries"></div>'+
 '<p class="small-note">Right-hand side b (for A·x=b or least squares)</p>'+
 '<div id="mat-rhs-grid" class="matrix-grid" aria-label="Right-hand side b entries"></div>'+
 '<p class="small-note">Observation weights w (weighted least squares, 3 positive values; default 1 each)</p>'+
 '<div id="mat-weight-grid" class="matrix-grid" aria-label="Observation weights"></div>'+
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
 '<button type="button" id="mat-qr" class="secondary">QR (A=Q·R)</button>'+
 '<button type="button" id="mat-least-squares" class="secondary">Least squares (A·x≈b)</button>'+
 '<button type="button" id="mat-weighted-least-squares" class="secondary">Weighted least squares (A·x≈b)</button>'+
 '<button type="button" id="mat-eigen" class="secondary">Eigen (symmetric A)</button>'+ 
 '<button type="button" id="mat-svd" class="secondary">SVD (2×2 / 3×2 / 2×3 / 3×3 A)</button>'+ 
 '<button type="button" id="mat-pseudoinverse" class="secondary">Pseudoinverse (2×2 / 3×2 / 2×3 / 3×3 A)</button>'+
 '<button type="button" id="mat-rref" class="secondary">RREF (A)</button>'+ 
 '<button type="button" id="mat-rank" class="secondary">Rank (A)</button>'+
 '<label>LU factor for editor <select id="mat-lu-factor"><option value="L">L</option><option value="U">U</option><option value="P">P</option></select></label>'+ 
 '<label>QR factor for editor <select id="mat-qr-factor"><option value="Q">Q</option><option value="R">R</option></select></label>'+
 '<label>Eigen output for editor <select id="mat-eigen-factor"><option value="vectors">Eigenvectors</option><option value="values">Eigenvalues</option></select></label>'+ 
 '<label>SVD factor for editor <select id="mat-svd-factor"><option value="U">U</option><option value="S">Singular values</option><option value="V">V</option></select></label>'+
 '<button type="button" id="mat-send" class="secondary" disabled>Send result to Equation Editor</button></div>'+
 '<pre id="mat-result" role="status" aria-live="polite">Enter matrix values and choose an operation.</pre>';
panel.append(area);
const style=el('style',{},'.matrix-tools{border-top:1px solid #dfe5f0;padding:13px 20px 16px}.matrix-tools summary{cursor:pointer;font-weight:700;color:#304cbb}'+
 '.matrix-controls,.matrix-actions{display:flex;flex-wrap:wrap;gap:10px;margin:12px 0}.matrix-controls label{display:grid;gap:3px;font-size:13px}'+
 '.matrix-grid{display:grid;gap:7px;max-width:340px}.matrix-grid input{min-width:0;width:100%;padding:9px;border:1px solid #cdd8ec;border-radius:6px;text-align:center}'+
 '#mat-result{background:#f7f9ff;border:1px solid #dfe5f0;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;border-radius:8px}'+
 '#mat-result.error{color:#af2842;background:#fff5f5}');
document.head.append(style);
const grid=document.getElementById('mat-grid'),gridB=document.getElementById('mat-b-grid'),rhsGrid=document.getElementById('mat-rhs-grid'),weightGrid=document.getElementById('mat-weight-grid'),output=document.getElementById('mat-result'),send=document.getElementById('mat-send');
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
function rebuildWeights(){
 const old=[...weightGrid.querySelectorAll('input')].map(input=>input.value);
 const rows=Number(document.getElementById('mat-rows').value);
 weightGrid.style.gridTemplateColumns='minmax(0, 1fr)';weightGrid.replaceChildren();
 for(let r=0;r<rows;r++){
  const cell=el('input',{type:'number',step:'any',min:'1e-12',max:'1e12','aria-label':'Observation weight row '+(r+1)});
  cell.value=old[r]===undefined?'1':old[r];cell.addEventListener('input',invalidate);weightGrid.append(cell);
 }
 invalidate();
}
function readWeights(){return [...weightGrid.querySelectorAll('input')].map(input=>input.value);}
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
   operation==='rref'?rref(A):operation==='rank'?matrixRank(A):operation==='solve'?solve(A,readRhs()):operation==='lu'?lu(A):operation==='qr'?qr(A):operation==='leastSquares'?leastSquares(A,readRhs()):operation==='weightedLeastSquares'?weightedLeastSquares(A,readRhs(),readWeights()):operation==='eigen'?eigenSymmetric(A):operation==='svd'?(A.length===2&&A[0].length===3?svd2x3(A):A.length===3&&A[0].length===2?svd3x2(A):A.length===3?svd3x3(A):svd2x2(A)):operation==='pseudoinverse'?pseudoinverse(A):multiply(A,readSecond());
  last={operation,value};output.classList.remove('error');
  const display=operation==='rref'?value.matrix:(operation==='solve'||operation==='leastSquares'||operation==='weightedLeastSquares')?value.solution.map(x=>[x]):value;
  const rowsText=rows=>rows.map(row=>'[ '+row.map(format).join('   ')+' ]').join('\n');
  output.textContent=operation==='pseudoinverse'?
   'pseudoinverse: A⁺ (Moore-Penrose, relative cutoff 1e-12)\n'+rowsText(value.matrix)+'\nNumerical rank: '+value.rank+'\nCondition number: '+(value.conditionNumber===undefined?'not available':value.conditionNumber===null?'rank deficient':format(value.conditionNumber))+'\nSingular values: '+value.singularValues.map(x=>x.toExponential(6)).join(', ')+'\nRank cutoff (absolute): '+value.cutoff.toExponential(3)+(value.conditionAssessment===undefined?'':'\nCondition assessment: '+value.conditionAssessment)+'\nRelative Moore-Penrose residual: '+format(value.residual)+'\nProjector symmetry residual: '+format(value.symmetryResidual):
   operation==='svd'?
   'svd: A = U·diag(σ)·Vᵀ\nSingular values (descending): '+value.S.map(format).join(', ')+'\nNumerical rank: '+value.rank+'\nCondition number: '+(value.conditionNumber===null?'undefined / outside finite range':format(value.conditionNumber))+(value.cutoff===undefined?'':'\nRank cutoff (absolute): '+value.cutoff.toExponential(3))+(value.conditionAssessment===undefined?'':'\nCondition assessment: '+value.conditionAssessment)+'\nU:\n'+rowsText(value.U)+'\nV:\n'+rowsText(value.V)+'\nRelative reconstruction residual: '+format(value.residual)+'\nU orthogonality residual: '+format(value.orthogonalityU)+'\nV orthogonality residual: '+format(value.orthogonalityV):
   operation==='eigen'?
   'eigen: symmetric A = V·diag(λ)·Vᵀ\nEigenvalues (descending): '+value.values.map(format).join(', ')+'\nEigenvectors (columns of V):\n'+rowsText(value.vectors)+'\nRelative residual: '+format(value.residual)+'\nReconstruction residual: '+format(value.reconstructionResidual)+'\nOrthogonality residual: '+format(value.orthogonality):
   operation==='lu'?
   'lu: P·A = L·U\nP:\n'+rowsText(value.P)+'\nL:\n'+rowsText(value.L)+'\nU:\n'+rowsText(value.U)+'\nRelative reconstruction residual: '+format(value.residual):operation==='qr'?
   'qr: A = Q·R\nQ:\n'+rowsText(value.Q)+'\nR:\n'+rowsText(value.R)+'\nRelative reconstruction residual: '+format(value.residual)+'\nOrthogonality residual: '+format(value.orthogonality):
   operation+':\n'+(typeof display==='number'?format(display):rowsText(display))+
   (operation==='rref'?'\nRank: '+value.rank:operation==='solve'?'\nRelative residual: '+format(value.residual):operation==='leastSquares'?'\nResidual norm: '+format(value.residual)+'\nRelative residual: '+format(value.relativeResidual)+'\nNormal-equation orthogonality: '+format(value.normalResidual):operation==='weightedLeastSquares'?'\nWeighted squared residual: '+format(value.weightedResidualSquared)+'\nNormalized weighted residual: '+format(value.residual)+'\nRelative weighted residual: '+format(value.relativeResidual)+'\nWeighted orthogonality: '+format(value.normalResidual):'');
  send.disabled=false;return last;
 }catch(error){last=null;send.disabled=true;output.classList.add('error');output.textContent=error.message;return null;}
}
for(const [id,op] of [['mat-det','determinant'],['mat-transpose','transpose'],['mat-inverse','inverse'],['mat-add','add'],['mat-subtract','subtract'],['mat-multiply','multiply'],['mat-rref','rref'],['mat-rank','rank'],['mat-solve','solve'],['mat-lu','lu'],['mat-qr','qr'],['mat-least-squares','leastSquares'],['mat-weighted-least-squares','weightedLeastSquares'],['mat-eigen','eigen'],['mat-svd','svd'],['mat-pseudoinverse','pseudoinverse']])
 document.getElementById(id).addEventListener('click',()=>calculate(op));
for(const id of ['mat-rows','mat-cols'])document.getElementById(id).addEventListener('change',()=>{rebuild();rebuildRhs();rebuildWeights();});
for(const id of ['mat-b-rows','mat-b-cols'])document.getElementById(id).addEventListener('change',rebuildSecond);
send.addEventListener('click',()=>{
 if(!last)return;
 try{M.bridge.transfer('editor',notation(last.operation==='rref'?last.value.matrix:(last.operation==='solve'||last.operation==='leastSquares'||last.operation==='weightedLeastSquares')?last.value.solution.map(x=>[x]):last.operation==='lu'?last.value[document.getElementById('mat-lu-factor').value]:last.operation==='qr'?last.value[document.getElementById('mat-qr-factor').value]:last.operation==='eigen'?(document.getElementById('mat-eigen-factor').value==='values'?last.value.values.map(x=>[x]):last.value.vectors):last.operation==='svd'?(document.getElementById('mat-svd-factor').value==='S'?last.value.S.map(x=>[x]):last.value[document.getElementById('mat-svd-factor').value]):last.operation==='pseudoinverse'?last.value.matrix:last.value),{source:'matrix calculator'});}
 catch(error){output.classList.add('error');output.textContent=error.message;}
});
rebuild();rebuildSecond();rebuildRhs();rebuildWeights();
M.matrixTools={validate,determinant,transpose,inverse,add,subtract,multiply,rref,rank:matrixRank,solve,lu,qr,leastSquares,weightedLeastSquares,eigenSymmetric,svd2x2,svd3x2,svd2x3,svd3x3,pseudoinverse2x2,pseudoinverse3x2,pseudoinverse2x3,pseudoinverse3x3,pseudoinverse,notation,read,readSecond,readRhs,readWeights,calculate};
})();