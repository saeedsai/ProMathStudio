/* Offline multivariate data analysis: covariance/correlation, scatter matrix, PCA (Jacobi) and seeded k-means. */
(()=>{'use strict';
const M=window.MathStudio=window.MathStudio||{};
const MAX_COLS=12,MIN_COLS=2,MAX_ROWS=6000,JACOBI_SWEEPS=100;
const NUMERIC=/^[+-]?(?:\d+\.?\d*|\.\d+)(?:e[+-]?\d+)?$/i;

/* ---------- data extraction ---------- */
function toNumber(v){
 if(typeof v==='number')return Number.isFinite(v)?v:null;
 if(v===null||v===undefined)return null;
 const s=String(v).trim();if(!s||!NUMERIC.test(s))return null;
 const n=Number(s);return Number.isFinite(n)?n:null;
}
/** Build an n×p numeric matrix from raw rows; rows with any blank or non-numeric selected cell are dropped. */
function matrixFromRows(rows,indices){
 const X=[],kept=[];let dropped=0;
 (rows||[]).forEach((row,r)=>{const v=indices.map(i=>toNumber(row?.[i]));if(v.some(x=>x===null))dropped++;else{X.push(v);kept.push(r+1);}});
 return {X,rowNumbers:kept,dropped};
}
function tableData(table,columns){
 const T=M.dataTables;if(!T)throw Error('Data Tables are unavailable.');
 const t=T.tables.find(s=>s.name===table||s.id===table);if(!t)throw Error('Choose an existing data table.');
 const names=Array.from(columns||[],String);
 if(names.length<MIN_COLS||names.length>MAX_COLS)throw Error('Select between 2 and 12 numeric columns.');
 if(new Set(names).size!==names.length)throw Error('Each column may be selected only once.');
 const idx=names.map(n=>{const i=t.columns.indexOf(n);if(i<0)throw Error('Unknown column: '+n+'.');return i;});
 const rows=typeof T.calculate==='function'?T.calculate(t):t.rows;
 return {table:t.name,names,...matrixFromRows(rows,idx),total:rows.length};
}
function checkMatrix(X,minRows=2){
 if(!Array.isArray(X)||!X.length)throw Error('At least '+minRows+' complete numeric rows are required.');
 const p=X[0].length;if(p<MIN_COLS||p>MAX_COLS)throw Error('Select between 2 and 12 numeric columns.');
 for(const r of X){if(!Array.isArray(r)||r.length!==p)throw Error('Rows must all have the same number of columns.');for(const v of r)if(typeof v!=='number'||!Number.isFinite(v))throw Error('Data must contain only finite numbers.');}
 if(X.length<minRows)throw Error('At least '+minRows+' complete numeric rows are required (found '+X.length+').');
 if(X.length>MAX_ROWS)throw Error('At most 6,000 rows are supported.');
 return p;
}

/* ---------- basic statistics ---------- */
function means(X){const p=X[0].length,m=new Array(p).fill(0);for(const r of X)for(let j=0;j<p;j++)m[j]+=r[j];return m.map(v=>v/X.length);}
/** Sample covariance matrix (n−1 denominator), two-pass for accuracy. */
function covariance(X){
 const p=checkMatrix(X),n=X.length,m=means(X),C=Array.from({length:p},()=>new Array(p).fill(0));
 for(const r of X)for(let i=0;i<p;i++){const di=r[i]-m[i];for(let j=i;j<p;j++)C[i][j]+=di*(r[j]-m[j]);}
 for(let i=0;i<p;i++)for(let j=i;j<p;j++){C[i][j]/=n-1;C[j][i]=C[i][j];}
 return C;
}
/** Pearson correlation; entries involving a zero-variance column are NaN and reported. */
function correlationFromCov(C){
 const p=C.length,s=C.map((r,i)=>Math.sqrt(r[i])),R=Array.from({length:p},()=>new Array(p).fill(NaN));
 for(let i=0;i<p;i++)for(let j=0;j<p;j++){if(s[i]>0&&s[j]>0){const v=i===j?1:C[i][j]/(s[i]*s[j]);R[i][j]=Math.max(-1,Math.min(1,v));}}
 return R;
}
/** Average ranks (ties share the mean of their positions, 1-based). */
function ranks(values){
 const o=values.map((v,i)=>[v,i]).sort((a,b)=>a[0]-b[0]),r=new Array(values.length);
 for(let i=0;i<o.length;){let j=i;while(j+1<o.length&&o[j+1][0]===o[i][0])j++;const avg=(i+j)/2+1;for(let k=i;k<=j;k++)r[o[k][1]]=avg;i=j+1;}
 return r;
}
function rankMatrix(X){const p=X[0].length,cols=[];for(let j=0;j<p;j++)cols.push(ranks(X.map(r=>r[j])));return X.map((_,i)=>cols.map(c=>c[i]));}
function correlation(X,{method='pearson'}={}){
 checkMatrix(X);if(method!=='pearson'&&method!=='spearman')throw Error('Correlation method must be pearson or spearman.');
 return correlationFromCov(covariance(method==='spearman'?rankMatrix(X):X));
}
function constantColumns(C,names){return C.map((r,i)=>r[i]>0?null:names[i]).filter(x=>x!==null);}
function correlationAnalysis(X,names){
 const p=checkMatrix(X);names=names||Array.from({length:p},(_,i)=>'x'+(i+1));
 const cov=covariance(X),pearson=correlationFromCov(cov),spearman=correlationFromCov(covariance(rankMatrix(X)));
 const constant=constantColumns(cov,names),warnings=[];
 if(constant.length)warnings.push('Zero-variance column(s) '+constant.join(', ')+': correlation is undefined (NaN) for those entries.');
 let best=null;for(let i=0;i<p;i++)for(let j=i+1;j<p;j++){const r=pearson[i][j];if(Number.isFinite(r)&&(!best||Math.abs(r)>Math.abs(best.r)))best={a:names[i],b:names[j],r};}
 return {type:'correlation',n:X.length,names,covariance:cov,pearson,spearman,constant,warnings,strongest:best};
}

/* ---------- symmetric Jacobi eigen-decomposition ---------- */
/** Cyclic Jacobi rotations for a real symmetric matrix. Returns eigenvalues (descending) and eigenvectors as columns. */
function jacobiEigen(A){
 const n=A.length;if(!n||A.some(r=>!Array.isArray(r)||r.length!==n))throw Error('Eigen-decomposition requires a square matrix.');
 for(let i=0;i<n;i++)for(let j=0;j<n;j++){if(!Number.isFinite(A[i][j]))throw Error('Matrix must contain finite numbers.');if(Math.abs(A[i][j]-A[j][i])>1e-12*Math.max(1,Math.abs(A[i][j])))throw Error('Matrix must be symmetric.');}
 const a=A.map(r=>r.slice()),V=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?1:0));
 let scale=0;for(const r of a)for(const v of r)scale=Math.max(scale,Math.abs(v));
 let sweeps=0,converged=false;
 for(;sweeps<JACOBI_SWEEPS;sweeps++){
  let off=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)off+=a[i][j]*a[i][j];
  if(off<=(1e-30*scale*scale)||off===0){converged=true;break;}
  for(let p=0;p<n;p++)for(let q=p+1;q<n;q++){
   const apq=a[p][q];if(apq===0)continue;
   const theta=(a[q][q]-a[p][p])/(2*apq),t=(theta>=0?1:-1)/(Math.abs(theta)+Math.sqrt(theta*theta+1)),c=1/Math.sqrt(t*t+1),s=t*c;
   for(let k=0;k<n;k++){const akp=a[k][p],akq=a[k][q];a[k][p]=c*akp-s*akq;a[k][q]=s*akp+c*akq;}
   for(let k=0;k<n;k++){const apk=a[p][k],aqk=a[q][k];a[p][k]=c*apk-s*aqk;a[q][k]=s*apk+c*aqk;}
   a[p][q]=a[q][p]=0;
   for(let k=0;k<n;k++){const vkp=V[k][p],vkq=V[k][q];V[k][p]=c*vkp-s*vkq;V[k][q]=s*vkp+c*vkq;}
  }
 }
 if(!converged)throw Error('Jacobi eigen-decomposition did not converge.');
 const order=a.map((r,i)=>i).sort((x,y)=>a[y][y]-a[x][x]||x-y);
 return {values:order.map(i=>a[i][i]),vectors:V.map(r=>order.map(i=>r[i])),sweeps};
}

/* ---------- PCA ---------- */
function pca(X,{scaling='standardize',names}={}){
 const p=checkMatrix(X);names=names||Array.from({length:p},(_,i)=>'x'+(i+1));
 if(scaling!=='standardize'&&scaling!=='center')throw Error('PCA scaling must be standardize or center.');
 const m=means(X),C=covariance(X),sd=C.map((r,i)=>Math.sqrt(r[i]));
 if(scaling==='standardize'){const c=constantColumns(C,names);if(c.length)throw Error('Cannot standardize zero-variance column(s): '+c.join(', ')+'. Deselect them or use centered PCA.');}
 const Z=X.map(r=>r.map((v,j)=>scaling==='standardize'?(v-m[j])/sd[j]:v-m[j]));
 const S=scaling==='standardize'?correlationFromCov(C):C,eig=jacobiEigen(S);
 const tol=1e-12*Math.max(1,Math.abs(eig.values[0]));
 const values=eig.values.map(v=>Math.abs(v)<=tol?0:v),total=values.reduce((s,v)=>s+Math.max(v,0),0);
 if(!(total>0))throw Error('All selected columns are constant; PCA is undefined.');
 // Sign convention: in each component the loading with the largest magnitude is positive (first index wins ties).
 const loadings=names.map(()=>new Array(p));
 for(let k=0;k<p;k++){
  let big=0;for(let j=1;j<p;j++)if(Math.abs(eig.vectors[j][k])>Math.abs(eig.vectors[big][k])+1e-12)big=j;
  const sign=eig.vectors[big][k]<0?-1:1;for(let j=0;j<p;j++)loadings[j][k]=sign*eig.vectors[j][k]+0;
 }
 const scores=Z.map(r=>loadings[0].map((_,k)=>{let s=0;for(let j=0;j<p;j++)s+=r[j]*loadings[j][k];return s;}));
 const ratio=values.map(v=>Math.max(v,0)/total);let acc=0;const cumulative=ratio.map(v=>acc+=v);
 return {type:'pca',scaling,n:X.length,names,means:m,std:sd,eigenvalues:values,explained:ratio,cumulative,loadings,scores,sweeps:eig.sweeps};
}

/* ---------- seeded k-means ---------- */
function rng(seed){let s=(seed>>>0)||0x9e3779b9;return ()=>{s=(s+0x6D2B79F5)>>>0;let t=s;t=Math.imul(t^(t>>>15),t|1);t^=t+Math.imul(t^(t>>>7),t|61);return ((t^(t>>>14))>>>0)/4294967296;};}
const dist2=(a,b)=>{let s=0;for(let i=0;i<a.length;i++){const d=a[i]-b[i];s+=d*d;}return s;};
function intIn(v,name,lo,hi){const n=Number(v);if(String(v).trim()===''||!Number.isInteger(n)||n<lo||n>hi)throw Error(name+' must be an integer from '+lo+' to '+hi+'.');return n;}
function plusPlus(Z,k,rand){
 const n=Z.length,centers=[Z[Math.floor(rand()*n)].slice()],d=Z.map(z=>dist2(z,centers[0]));
 while(centers.length<k){
  const total=d.reduce((s,v)=>s+v,0);let idx;
  if(!(total>0))idx=Math.floor(rand()*n);
  else{let r=rand()*total;idx=n-1;for(let i=0;i<n;i++){r-=d[i];if(r<0){idx=i;break;}}}
  const c=Z[idx].slice();centers.push(c);for(let i=0;i<n;i++)d[i]=Math.min(d[i],dist2(Z[i],c));
 }
 return centers;
}
function lloyd(Z,centers,maxIter,tol){
 const n=Z.length,k=centers.length,p=Z[0].length,labels=new Array(n).fill(0);let iter=0,converged=false;
 for(;iter<maxIter;){
  iter++;
  for(let i=0;i<n;i++){let best=0,bd=Infinity;for(let c=0;c<k;c++){const d=dist2(Z[i],centers[c]);if(d<bd){bd=d;best=c;}}labels[i]=best;}
  const sums=Array.from({length:k},()=>new Array(p).fill(0)),cnt=new Array(k).fill(0);
  for(let i=0;i<n;i++){cnt[labels[i]]++;for(let j=0;j<p;j++)sums[labels[i]][j]+=Z[i][j];}
  for(let c=0;c<k;c++)if(!cnt[c]){ // empty cluster: move it to the point farthest from its centre
   let far=0,fd=-1;for(let i=0;i<n;i++){const d=dist2(Z[i],centers[labels[i]]);if(d>fd&&cnt[labels[i]]>1){fd=d;far=i;}}
   cnt[labels[far]]--;for(let j=0;j<p;j++)sums[labels[far]][j]-=Z[far][j];labels[far]=c;cnt[c]=1;sums[c]=Z[far].slice();
  }
  let shift=0;for(let c=0;c<k;c++){const nc=sums[c].map(v=>v/cnt[c]);shift+=dist2(nc,centers[c]);centers[c]=nc;}
  if(shift<=tol){converged=true;break;}
 }
 for(let i=0;i<n;i++){let best=0,bd=Infinity;for(let c=0;c<k;c++){const d=dist2(Z[i],centers[c]);if(d<bd){bd=d;best=c;}}labels[i]=best;}
 let inertia=0;for(let i=0;i<n;i++)inertia+=dist2(Z[i],centers[labels[i]]);
 return {labels,centers,inertia,iterations:iter,converged};
}
function kmeans(X,{k=3,nInit=10,maxIter=300,seed=1,standardize=false,names}={}){
 const p=checkMatrix(X,1);names=names||Array.from({length:p},(_,i)=>'x'+(i+1));
 k=intIn(k,'Number of clusters k',2,10);nInit=intIn(nInit,'Restarts n_init',1,50);maxIter=intIn(maxIter,'Maximum iterations',1,1000);seed=intIn(seed,'Seed',0,4294967295);
 const n=X.length;if(k>n)throw Error('Number of clusters k ('+k+') cannot exceed the number of complete rows ('+n+').');
 const distinct=new Set(X.map(r=>r.join(','))).size;if(k>distinct)throw Error('Only '+distinct+' distinct row(s); choose k ≤ '+distinct+'.');
 const m=means(X),sd=n>1?covariance(X).map((r,i)=>Math.sqrt(r[i])):new Array(p).fill(0);
 const sc=sd.map(s=>standardize&&s>0?s:1),Z=standardize?X.map(r=>r.map((v,j)=>(v-m[j])/sc[j])):X;
 const rand=rng(seed),tol=1e-12*Math.max(1,Z.reduce((s,r)=>s+dist2(r,new Array(p).fill(0)),0)/n);
 let best=null;
 for(let run=0;run<nInit;run++){const r=lloyd(Z,plusPlus(Z,k,rand),maxIter,tol);if(!best||r.inertia<best.inertia-1e-12*Math.max(1,best.inertia))best=r;}
 // Canonical labels: clusters are numbered 1..k in order of first appearance in the data.
 const map=new Map();for(const l of best.labels)if(!map.has(l))map.set(l,map.size);
 const labels=best.labels.map(l=>map.get(l)+1),centers=new Array(k),sizes=new Array(k).fill(0);
 for(const [old,nw] of map)centers[nw]=best.centers[old].map((v,j)=>standardize?v*sc[j]+m[j]:v);
 for(const l of labels)sizes[l-1]++;
 return {type:'kmeans',k,nInit,seed,standardize,n,names,labels,sizes,centers,inertia:best.inertia,iterations:best.iterations,converged:best.converged};
}

/* ---------- table-level entry point ---------- */
function analyze({table,columns,analysis='correlation',scaling='standardize',k=3,nInit=10,seed=1,standardize=false}={}){
 const d=tableData(table,columns);
 if(d.X.length<2)throw Error('At least 2 complete numeric rows are required (found '+d.X.length+'; '+d.dropped+' row(s) dropped).');
 let r;
 if(analysis==='correlation')r=correlationAnalysis(d.X,d.names);
 else if(analysis==='pca')r=pca(d.X,{scaling,names:d.names});
 else if(analysis==='kmeans')r=kmeans(d.X,{k,nInit,seed,standardize,names:d.names});
 else throw Error('Unknown analysis: '+analysis+'.');
 return {...r,table:d.table,dropped:d.dropped,total:d.total,rowNumbers:d.rowNumbers,X:d.X};
}

M.multivariate={toNumber,matrixFromRows,tableData,covariance,correlation,ranks,correlationAnalysis,jacobiEigen,pca,kmeans,rng,analyze};

/* ---------- UI ---------- */
const panel=typeof document!=='undefined'&&document.getElementById('data-panel');if(!panel)return;
const $=id=>document.getElementById(id);
const fmt=v=>typeof v!=='number'?String(v):Number.isNaN(v)?'NaN':Number.isFinite(v)?(Math.abs(v)<1e-14?'0':Number(v.toPrecision(6)).toString()):String(v);
const area=document.createElement('details');area.id='multivariate-details';
const box='display:inline-flex;align-items:center;gap:6px;min-height:40px;padding:0 8px;margin:2px;border:1px solid #d5dbe6;border-radius:8px;cursor:pointer';
area.innerHTML='<summary style="min-height:40px">Multivariate analysis · correlation matrix, PCA and k-means</summary>'+
 '<p>Select 2–12 numeric columns. Rows with any blank or non-numeric selected cell are dropped and counted. Covariance uses the n−1 denominator; Spearman uses average ranks for ties; PCA uses a symmetric Jacobi eigen-decomposition; k-means uses seeded k-means++ with Lloyd iterations.</p>'+
 '<div class="num-fields"><label>Data table<select id="mv-table" style="min-height:40px"></select></label>'+
 '<label>Analysis<select id="mv-analysis" style="min-height:40px"><option value="correlation">Covariance &amp; correlation + scatter matrix</option><option value="pca">Principal component analysis</option><option value="kmeans">k-means clustering</option></select></label>'+
 '<label id="mv-scaling-label">PCA scaling<select id="mv-scaling" style="min-height:40px"><option value="standardize">Standardized (correlation matrix)</option><option value="center">Centered only (covariance matrix)</option></select></label>'+
 '<label id="mv-k-label">Clusters k (2–10)<input id="mv-k" type="number" min="2" max="10" step="1" value="3" style="min-height:40px"></label>'+
 '<label id="mv-ninit-label">Restarts n_init (1–50)<input id="mv-ninit" type="number" min="1" max="50" step="1" value="10" style="min-height:40px"></label>'+
 '<label id="mv-seed-label">Seed<input id="mv-seed" type="number" min="0" step="1" value="1" style="min-height:40px"></label>'+
 '<label id="mv-std-label" style="'+box+'"><input id="mv-std" type="checkbox"> Standardize before clustering</label></div>'+
 '<fieldset id="mv-columns" style="border:1px solid #d5dbe6;border-radius:8px;padding:6px;margin:8px 0;max-width:100%;min-width:0"><legend>Columns (2–12)</legend><div id="mv-column-list" role="group" aria-label="Columns to analyse" style="display:flex;flex-wrap:wrap"></div></fieldset>'+
 '<div class="data-toolbar"><button id="mv-run" class="primary" type="button" style="min-height:40px">Run analysis</button>'+
 '<button id="mv-save" class="secondary" type="button" style="min-height:40px" disabled>Save results to Data Tables</button></div>'+
 '<pre id="mv-output" role="status" aria-live="polite" style="white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;overflow-x:auto">Choose a table and at least two numeric columns.</pre>'+
 '<canvas id="mv-canvas" width="720" height="720" role="img" aria-label="Scatter matrix not yet drawn." style="display:none;width:100%;max-width:720px;height:auto;border:1px solid #d5dbe6;border-radius:8px;background:#fff"></canvas>';
panel.append(area);
let last=null;const output=$('mv-output');
const option=(select,value,text)=>{const o=document.createElement('option');o.value=value;o.textContent=text;select.append(o);};
const invalidate=()=>{last=null;$('mv-save').disabled=true;output.classList.remove('error');};
function syncAnalysis(){
 const a=$('mv-analysis').value;$('mv-scaling-label').hidden=a!=='pca';
 for(const id of ['mv-k-label','mv-ninit-label','mv-seed-label','mv-std-label'])$(id).hidden=a!=='kmeans';
}
function syncColumns(){
 const t=M.dataTables?.tables.find(s=>s.name===$('mv-table').value),list=$('mv-column-list');
 const keep=new Set([...list.querySelectorAll('input:checked')].map(i=>i.value)),fresh=!list.children.length||list.dataset.table!==(t?.name||'');
 list.replaceChildren();list.dataset.table=t?.name||'';
 (t?.columns||[]).forEach((name,i)=>{
  const label=document.createElement('label');label.setAttribute('style',box);
  const cb=document.createElement('input');cb.type='checkbox';cb.value=name;cb.className='mv-col';cb.checked=fresh?i<MAX_COLS:keep.has(name);
  cb.addEventListener('change',invalidate);label.append(cb,document.createTextNode(' '+name));list.append(label);
 });
}
function syncTables(){
 const T=M.dataTables,sel=$('mv-table');if(!T)return;const keep=sel.value;sel.replaceChildren();
 for(const t of T.tables)option(sel,t.name,t.name);
 if([...sel.options].some(o=>o.value===keep))sel.value=keep;else if(T.active&&T.tables.includes(T.active))sel.value=T.active.name;
 syncColumns();
}
const matrixLines=(title,names,A,cols=names)=>{const w=Math.max(8,...names.map(n=>n.length),...cols.map(n=>n.length))+1,pad=s=>String(s).padStart(w);return [title,pad('')+cols.map(pad).join('')].concat(A.map((r,i)=>pad(names[i])+r.map(v=>pad(fmt(v))).join('')));};
const cellOf=v=>typeof v==='number'&&Number.isFinite(v)?v:fmt(v);
function drawScatter(r,colors){
 const c=$('mv-canvas'),ctx=c.getContext&&c.getContext('2d'),X=r.X,p=r.names.length,n=X.length;
 c.style.display='block';
 const pearson=r.pearson||correlationFromCov(covariance(X)),best=(()=>{let b=null;for(let i=0;i<p;i++)for(let j=i+1;j<p;j++){const v=pearson[i][j];if(Number.isFinite(v)&&(!b||Math.abs(v)>Math.abs(b.r)))b={a:r.names[i],b:r.names[j],r:v};}return b;})();
 c.setAttribute('aria-label','Scatter matrix of '+n+' rows across '+p+' columns ('+r.names.join(', ')+'); diagonal cells show histograms'+(best?'; strongest Pearson correlation '+best.a+'–'+best.b+' r = '+fmt(best.r):'')+(colors?'; points coloured by k-means cluster':'')+'.');
 if(!ctx)return;
 const W=c.width,cell=W/p,pad=Math.max(2,cell*0.08),palette=['#2f6fda','#d9534f','#3a9d5d','#e69a28','#8e5bd0','#1aa3a3','#c2477f','#6b7a8f','#9c7b2a','#3f4fb5'];
 ctx.clearRect(0,0,W,W);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,W);
 const lo=[],hi=[];for(let j=0;j<p;j++){let a=Infinity,b=-Infinity;for(const row of X){a=Math.min(a,row[j]);b=Math.max(b,row[j]);}if(a===b){a-=0.5;b+=0.5;}lo.push(a);hi.push(b);}
 const step=Math.max(1,Math.ceil(n/2000)),dot=Math.max(1,Math.min(3,cell/40));
 for(let i=0;i<p;i++)for(let j=0;j<p;j++){
  const x0=j*cell+pad,y0=i*cell+pad,s=cell-2*pad;ctx.strokeStyle='#c9d1de';ctx.lineWidth=1;ctx.strokeRect(x0,y0,s,s);
  if(i===j){
   const bins=Math.max(3,Math.min(30,Math.ceil(Math.log2(n)+1))),h=new Array(bins).fill(0);
   for(const row of X)h[Math.min(bins-1,Math.floor((row[j]-lo[j])/(hi[j]-lo[j])*bins))]++;
   const top=Math.max(...h);ctx.fillStyle='#8fb0e6';
   h.forEach((v,b)=>{const bh=(s-14)*v/top;ctx.fillRect(x0+b*s/bins+0.5,y0+s-bh,s/bins-1,bh);});
   ctx.fillStyle='#1f2a3c';ctx.font=Math.max(8,Math.min(13,cell/7))+'px sans-serif';ctx.fillText(r.names[j].slice(0,14),x0+3,y0+12);
  }else{
   for(let k=0;k<n;k+=step){const row=X[k];ctx.fillStyle=colors?palette[(colors[k]-1)%palette.length]:'#2f6fda';
    ctx.fillRect(x0+(row[j]-lo[j])/(hi[j]-lo[j])*s-dot/2,y0+s-(row[i]-lo[i])/(hi[i]-lo[i])*s-dot/2,dot,dot);}
  }
 }
}
function report(r){
 const head=['Table '+r.table+' · '+r.n+' complete row(s) used, '+r.dropped+' dropped (blank or non-numeric) of '+r.total+'.'];
 if(r.type==='correlation'){
  const lines=head.concat(matrixLines('Sample covariance (n−1)',r.names,r.covariance),'',matrixLines('Pearson correlation',r.names,r.pearson),'',matrixLines('Spearman rank correlation (average ranks for ties)',r.names,r.spearman),r.warnings.map(w=>'Warning: '+w));
  const rows=[];for(const [label,A] of [['covariance',r.covariance],['pearson',r.pearson],['spearman',r.spearman]])A.forEach((row,i)=>rows.push([label,r.names[i]].concat(row.map(cellOf))));
  return {lines,saves:[{name:'Multivariate_Correlation',headers:['matrix','variable'].concat(r.names),rows}],colors:null};
 }
 if(r.type==='pca'){
  const pcs=r.names.map((_,k)=>'PC'+(k+1)),lines=head.concat('PCA ('+(r.scaling==='standardize'?'standardized data, correlation matrix':'centered data, covariance matrix')+'), Jacobi sweeps: '+r.sweeps);
  r.eigenvalues.forEach((v,k)=>lines.push(pcs[k]+': eigenvalue '+fmt(v)+', explained '+fmt(r.explained[k]*100)+'%, cumulative '+fmt(r.cumulative[k]*100)+'%'));
  lines.push('',...matrixLines('Loadings (columns = components; largest |loading| positive)',r.names,r.loadings,pcs));
  lines.push('','Scores are available via Save results (one row per complete data row).');
  const summary=[['eigenvalue'].concat(r.eigenvalues),['explained_ratio'].concat(r.explained),['cumulative_ratio'].concat(r.cumulative)].concat(r.loadings.map((row,j)=>['loading_'+r.names[j]].concat(row)));
  return {lines,saves:[{name:'PCA_Summary',headers:['quantity'].concat(pcs),rows:summary},{name:'PCA_Scores',headers:['row'].concat(pcs),rows:r.scores.map((s,i)=>[r.rowNumbers[i]].concat(s))}],colors:null};
 }
 const lines=head.concat('k-means: k = '+r.k+', n_init = '+r.nInit+', seed = '+r.seed+(r.standardize?', standardized':', raw units')+'; best inertia = '+fmt(r.inertia)+' ('+r.iterations+' Lloyd iteration(s)'+(r.converged?'':', iteration limit reached')+').');
 r.sizes.forEach((s,c)=>lines.push('Cluster '+(c+1)+': '+s+' row(s); centre ['+r.centers[c].map(fmt).join(', ')+']'));
 return {lines,saves:[{name:'KMeans_Labels',headers:['row'].concat(r.names,['cluster']),rows:r.X.map((x,i)=>[r.rowNumbers[i]].concat(x,[r.labels[i]]))}],colors:r.labels};
}
$('mv-table').addEventListener('change',()=>{syncColumns();invalidate();});
$('mv-table').addEventListener('focus',syncTables);
$('mv-analysis').addEventListener('change',()=>{syncAnalysis();invalidate();});
area.addEventListener('toggle',()=>{if(area.open)syncTables();});
for(const el of area.querySelectorAll('input,select')){el.addEventListener('input',invalidate);el.addEventListener('change',invalidate);}
$('mv-run').addEventListener('click',()=>{
 try{
  const columns=[...$('mv-column-list').querySelectorAll('input.mv-col:checked')].map(i=>i.value);
  if(columns.length<MIN_COLS||columns.length>MAX_COLS)throw Error('Select between 2 and 12 numeric columns (currently '+columns.length+').');
  const r=analyze({table:$('mv-table').value,columns,analysis:$('mv-analysis').value,scaling:$('mv-scaling').value,k:$('mv-k').value,nInit:$('mv-ninit').value,seed:$('mv-seed').value,standardize:$('mv-std').checked});
  const out=report(r);last=out;output.classList.remove('error');output.textContent=out.lines.join('\n');$('mv-save').disabled=false;
  if(r.type==='pca')$('mv-canvas').style.display='none';else drawScatter(r,out.colors);
 }catch(err){invalidate();output.classList.add('error');output.textContent=err.message+' Adjust the selection or options and run again.';}
});
$('mv-save').addEventListener('click',()=>{
 try{if(!last)throw Error('Run an analysis first.');const names=last.saves.map(s=>M.dataTables.importData({headers:s.headers,rows:s.rows},s.name).name);
  output.classList.remove('error');output.textContent+='\nSaved to Data Tables: '+names.join(', ')+'.';syncTables();}
 catch(err){output.classList.add('error');output.textContent=err.message;}
});
syncAnalysis();syncTables();
})();
