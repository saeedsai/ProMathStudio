/* Offline measurement-uncertainty propagation: first-order GUM law and seeded Monte Carlo (GUM-S1 style). */
(()=>{'use strict';
const M=window.MathStudio=window.MathStudio||{};
const LIMIT=1e12,MAX_VARS=6,MAX_SAMPLES=200000,RESERVED=new Set(['e','pi','i','inf','infinity','nan']);

/* ---------- validation ---------- */
function num(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');const n=Number(value);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(name+' must be finite and at most 1e12 in magnitude.');return n;}
function evaluator(){const f=M.numerical?.evaluate;if(typeof f!=='function')throw Error('The numerical evaluator is unavailable.');return f;}
function normalize({expression,variables,correlations=[],k=2}={}){
 expression=String(expression??'').trim();if(!expression||expression.length>1000)throw Error('Enter a model expression f of 1–1000 characters.');
 if(!Array.isArray(variables)||variables.length<1||variables.length>MAX_VARS)throw Error('Define 1 to '+MAX_VARS+' input variables.');
 const seen=new Set();
 const vars=variables.map((v,i)=>{
  const label='Variable '+(i+1),name=String(v?.name??'').trim();
  if(!/^[A-Za-z][A-Za-z0-9_]{0,15}$/.test(name))throw Error(label+' name must start with a letter and use at most 16 letters, digits or underscores.');
  if(RESERVED.has(name.toLowerCase()))throw Error(label+' name "'+name+'" is reserved for a constant.');
  if(seen.has(name))throw Error('Variable name "'+name+'" is duplicated.');seen.add(name);
  const distribution=String(v?.distribution||'normal').toLowerCase();
  if(distribution!=='normal'&&distribution!=='uniform')throw Error(name+' distribution must be normal or uniform.');
  const mean=num(v?.mean,name+' mean');
  if(distribution==='normal'){const u=num(v?.u??v?.spread,name+' standard uncertainty u');if(u<0)throw Error(name+' standard uncertainty u must be non-negative.');return {name,mean,u,distribution};}
  const a=num(v?.halfWidth??v?.spread,name+' half-width a');if(a<0)throw Error(name+' half-width a must be non-negative.');
  return {name,mean,u:a/Math.sqrt(3),halfWidth:a,distribution};
 });
 const n=vars.length,R=vars.map((_,i)=>vars.map((_,j)=>i===j?1:0)),index=new Map(vars.map((v,i)=>[v.name,i]));
 if(!Array.isArray(correlations))throw Error('Correlations must be a list.');
 for(const c of correlations){
  const a=String(c?.a??'').trim(),b=String(c?.b??'').trim();
  if(!index.has(a)||!index.has(b))throw Error('Correlation refers to an unknown variable: '+(index.has(a)?b:a)+'.');
  if(a===b)throw Error('A variable cannot be correlated with itself.');
  const rho=num(c?.rho,'Correlation '+a+'–'+b);if(rho<-1||rho>1)throw Error('Correlation '+a+'–'+b+' must be in [−1, 1].');
  const i=index.get(a),j=index.get(b);if(R[i][j]!==0&&R[i][j]!==rho)throw Error('Correlation '+a+'–'+b+' is given twice with different values.');
  R[i][j]=R[j][i]=rho;
 }
 k=num(k,'Coverage factor k');if(k<=0||k>10)throw Error('Coverage factor k must be in (0, 10].');
 const L=cholesky(R);
 return {expression,vars,R,L,k,n};
}
/** Lower-triangular factor of a correlation matrix; accepts positive semidefinite (e.g. ρ=±1) and rejects indefinite matrices. */
function cholesky(R){
 const n=R.length,L=R.map(()=>new Array(n).fill(0)),TOL=1e-10;
 for(let j=0;j<n;j++){
  let d=R[j][j];for(let m=0;m<j;m++)d-=L[j][m]*L[j][m];
  if(d<-TOL)throw Error('Correlation matrix is not positive semidefinite; the coefficients are mutually inconsistent.');
  const s=d>TOL?Math.sqrt(d):0;L[j][j]=s;
  for(let i=j+1;i<n;i++){let v=R[i][j];for(let m=0;m<j;m++)v-=L[i][m]*L[j][m];
   if(s===0){if(Math.abs(v)>1e-8)throw Error('Correlation matrix is not positive semidefinite; the coefficients are mutually inconsistent.');L[i][j]=0;}else L[i][j]=v/s;}
 }
 return L;
}
function model(spec){
 const f=evaluator();let calls=0;
 return {get calls(){return calls;},at(x){const env={};spec.vars.forEach((v,i)=>{env[v.name]=x[i];});calls++;const y=f(spec.expression,env);if(!Number.isFinite(y)||Math.abs(y)>LIMIT)throw Error('Model must return a finite real value at most 1e12 in magnitude.');return y;}};
}

/* ---------- first-order (GUM linear) propagation ---------- */
function linear(spec){
 const F=model(spec),x0=spec.vars.map(v=>v.mean),y=F.at(x0);
 const c=spec.vars.map((v,i)=>{
  if(v.u===0)return 0;
  const h=1e-5*Math.max(Math.abs(v.mean),v.u,1e-8),a=x0.slice(),b=x0.slice();a[i]+=h;b[i]-=h;
  let fa,fb;try{fa=F.at(a);fb=F.at(b);}catch(err){throw Error('Sensitivity for '+v.name+' failed near the mean: '+err.message);}
  return (fa-fb)/(2*h);
 });
 let variance=0;const terms=spec.vars.map((v,i)=>c[i]*v.u);
 for(let i=0;i<spec.n;i++)for(let j=0;j<spec.n;j++)variance+=terms[i]*terms[j]*spec.R[i][j];
 if(variance<0)variance=0;const uc=Math.sqrt(variance),diag=terms.reduce((s,t)=>s+t*t,0);
 const contributions=spec.vars.map((v,i)=>({name:v.name,mean:v.mean,u:v.u,distribution:v.distribution,sensitivity:c[i],contribution:terms[i],percent:variance>0?100*terms[i]*terms[i]/variance:0}));
 return {type:'uncertainty-linear',value:y,uc,k:spec.k,U:spec.k*uc,interval:[y-spec.k*uc,y+spec.k*uc],contributions,correlationPercent:variance>0?100*(variance-diag)/variance:0,evaluations:F.calls,
  method:'First-order GUM law of propagation (central-difference sensitivities)'};
}

/* ---------- seeded PRNG and normals ---------- */
function rng(seed){
 // splitmix32 seeding of xoshiro128**; deterministic for a given 32-bit seed.
 let z=seed>>>0;const next=()=>{z=(z+0x9e3779b9)>>>0;let t=z;t=Math.imul(t^(t>>>16),0x21f0aaad);t=Math.imul(t^(t>>>15),0x735a2d97);return (t^(t>>>15))>>>0;};
 let a=next(),b=next(),c=next(),d=next();if((a|b|c|d)===0)a=1;
 const u32=()=>{const r=Math.imul(((Math.imul(b,5)<<7)|(Math.imul(b,5)>>>25)),9)>>>0,t=b<<9;c^=a;d^=b;b^=c;a^=d;c^=t;d=((d<<11)|(d>>>21))>>>0;a>>>=0;b>>>=0;c>>>=0;return r;};
 // Open interval (0,1) with 53-bit resolution.
 const uniform=()=>((u32()>>>5)*67108864+(u32()>>>6)+0.5)/9007199254740992;
 let spare=null;
 const normal=()=>{if(spare!==null){const s=spare;spare=null;return s;}const r=Math.sqrt(-2*Math.log(uniform())),t=2*Math.PI*uniform();spare=r*Math.sin(t);return r*Math.cos(t);};
 return {u32,uniform,normal};
}
function seedOf(value){const s=num(value,'Seed');if(!Number.isInteger(s)||s<0||s>4294967295)throw Error('Seed must be an integer from 0 to 4294967295.');return s;}

/* ---------- Monte Carlo propagation ---------- */
function monteCarlo(spec,{samples=100000,seed=1,timeBudgetMs=8000,keep=false}={}){
 samples=num(samples,'Number of samples N');if(!Number.isInteger(samples)||samples<1000||samples>MAX_SAMPLES)throw Error('Number of samples N must be an integer from 1000 to '+MAX_SAMPLES+'.');
 seed=seedOf(seed);timeBudgetMs=num(timeBudgetMs,'Time budget');
 for(let i=0;i<spec.n;i++)for(let j=0;j<spec.n;j++)if(i!==j&&spec.R[i][j]!==0&&(spec.vars[i].distribution!=='normal'||spec.vars[j].distribution!=='normal'))
  throw Error('Monte Carlo supports correlations only between normal inputs ('+spec.vars[i].name+'–'+spec.vars[j].name+' involves a uniform input).');
 const F=model(spec),R=rng(seed),L=spec.L,n=spec.n,ys=new Float64Array(samples),z=new Array(n),x=new Array(n),start=Date.now();
 let count=0,truncated=false;
 for(;count<samples;count++){
  if((count&1023)===0&&count>0&&Date.now()-start>timeBudgetMs){truncated=true;break;}
  for(let i=0;i<n;i++)z[i]=spec.vars[i].distribution==='normal'?R.normal():R.uniform();
  for(let i=0;i<n;i++){const v=spec.vars[i];
   if(v.distribution==='uniform'){x[i]=v.mean+v.halfWidth*(2*z[i]-1);continue;}
   let s=0;for(let m=0;m<=i;m++)if(spec.vars[m].distribution==='normal')s+=L[i][m]*z[m];
   x[i]=v.mean+v.u*s;}
  try{ys[count]=F.at(x);}catch(err){throw Error('Model is undefined at Monte Carlo sample '+(count+1)+' ('+spec.vars.map((v,i)=>v.name+'='+Number(x[i].toPrecision(6))).join(', ')+'): '+err.message);}
 }
 if(count<1000)throw Error('Monte Carlo time budget allowed fewer than 1000 samples.');
 const y=ys.subarray(0,count);let mean=0;for(let i=0;i<count;i++)mean+=(y[i]-mean)/(i+1);
 let ss=0;for(let i=0;i<count;i++){const d=y[i]-mean;ss+=d*d;}const std=Math.sqrt(ss/(count-1));
 const sorted=Float64Array.from(y).sort(),p=0.95,q=Math.round(p*count);
 const low=Math.max(0,Math.floor((1-p)/2*count)),symmetric=[sorted[low],sorted[Math.min(count-1,low+q-1)]];
 let best=0;for(let r=1;r+q-1<count;r++)if(sorted[r+q-1]-sorted[r]<sorted[best+q-1]-sorted[best])best=r;
 const out={type:'uncertainty-monte-carlo',samples:count,requested:samples,truncated,seed,mean,std,symmetric95:symmetric,shortest95:[sorted[best],sorted[best+q-1]],min:sorted[0],max:sorted[count-1],
  histogram:histogram(sorted,40),elapsedMs:Date.now()-start,method:'Monte Carlo propagation of distributions (GUM Supplement 1 style), xoshiro128** seeded PRNG'};
 if(keep)out.values=Array.from(y);
 return out;
}
function histogram(sorted,bins){
 const lo=sorted[0],hi=sorted[sorted.length-1],counts=new Array(bins).fill(0);
 if(!(hi>lo)){counts[0]=sorted.length;return {lo,hi,counts};}
 const w=(hi-lo)/bins;for(const v of sorted)counts[Math.min(bins-1,Math.floor((v-lo)/w))]++;
 return {lo,hi,counts};
}
function compare(lin,mc){
 const scale=Math.max(lin.uc,mc.std),stdDiff=scale>0?Math.abs(mc.std-lin.uc)/scale:0,meanShift=scale>0?Math.abs(mc.mean-lin.value)/scale:0;
 const nonlinear=stdDiff>0.1||meanShift>0.1;
 return {stdRelativeDifference:stdDiff,meanShiftInUnits:meanShift,nonlinear,
  note:nonlinear?'Linear and Monte Carlo results differ by more than 10%: the model is significantly non-linear (or non-Gaussian) over the input uncertainty; prefer the Monte Carlo result.':'Linear and Monte Carlo results agree within 10%.'};
}
function propagate(options){return linear(normalize(options));}
function run(options={}){
 const spec=normalize(options),lin=linear(spec),mc=monteCarlo(spec,options);
 return {type:'uncertainty',expression:spec.expression,linear:lin,monteCarlo:mc,comparison:compare(lin,mc),
  note:'Assumes independent inputs unless correlations are given; first-order results need a model that is approximately linear over ±u. Monte Carlo accuracy depends on N; not a validated metrology certificate.'};
}
function parseCorrelations(text){
 const out=[];for(const [i,raw] of String(text??'').split(/\n|;/).entries()){
  const line=raw.trim();if(!line)continue;const parts=line.split(/[\s,]+/).filter(Boolean);
  if(parts.length!==3)throw Error('Correlation line '+(i+1)+' must read: name name ρ.');
  out.push({a:parts[0],b:parts[1],rho:parts[2]});
 }
 return out;
}

M.uncertainty={normalize,cholesky,propagate,monteCarlo:(options={})=>monteCarlo(normalize(options),options),run,rng,parseCorrelations};

/* ---------- UI ---------- */
const panel=document.getElementById('numerical-panel');if(!panel||!document.createElement)return;
const $=id=>document.getElementById(id);
const fmt=v=>Number.isFinite(v)?Number(v.toPrecision(8)).toString():String(v);
const area=document.createElement('details');area.id='uncertainty-details';
area.innerHTML='<summary>Uncertainty · error propagation and Monte Carlo</summary>'+
 '<p>Propagate input uncertainties through y = f(variables) by the first-order GUM law and by seeded Monte Carlo sampling.</p>'+
 '<style>#uncertainty-details fieldset{border:1px solid #d8dfeb;border-radius:9px;margin:8px 0;padding:6px 10px;min-width:0}#uncertainty-details label{min-width:0}#uncertainty-details textarea{min-height:64px;width:100%;box-sizing:border-box;padding:9px;border:1px solid #cdd8ec;border-radius:9px;font:inherit}#uncertainty-canvas{width:100%;max-width:480px;height:auto;display:block;border:1px solid #d8dfeb;border-radius:9px;background:#fff}#uncertainty-output{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%}</style>'+
 '<div class="num-fields"><label>Model y = f(…)<input id="uncertainty-expression" value="a*b" autocomplete="off" spellcheck="false"></label>'+
 '<label>Coverage factor k<input id="uncertainty-k" type="number" step="any" value="2"></label>'+
 '<label>Monte Carlo samples N<input id="uncertainty-samples" type="number" step="1" min="1000" max="200000" value="100000"></label>'+
 '<label>Seed<input id="uncertainty-seed" type="number" step="1" min="0" value="1"></label></div>'+
 '<div id="uncertainty-vars"></div>'+
 '<div class="data-toolbar"><button id="uncertainty-add" class="secondary" type="button">Add variable</button><button id="uncertainty-remove" class="secondary" type="button">Remove last variable</button></div>'+
 '<label>Correlations (one pair per line: name name ρ)<textarea id="uncertainty-correlations" rows="2" spellcheck="false" placeholder="a b 0.5"></textarea></label>'+
 '<div class="data-toolbar"><button id="uncertainty-run" class="primary" type="button">Propagate uncertainty</button>'+
 '<button id="uncertainty-to-table" class="secondary" type="button" disabled>Save samples summary to Data Tables</button></div>'+
 '<pre id="uncertainty-output" role="status" aria-live="polite">Define the model and its input uncertainties.</pre>'+
 '<canvas id="uncertainty-canvas" width="480" height="160" role="img" aria-label="Monte Carlo histogram: not yet computed"></canvas>';
panel.append(area);let last=null;
const output=$('uncertainty-output'),varsBox=$('uncertainty-vars'),canvas=$('uncertainty-canvas');
const invalidate=()=>{last=null;$('uncertainty-to-table').disabled=true;output.classList.remove('error');};
function field(labelText,input){const l=document.createElement('label');l.append(document.createTextNode(labelText),input);return l;}
function addVariable(name,mean,spread,dist='normal'){
 const i=varsBox.children.length;if(i>=MAX_VARS)return;
 const fs=document.createElement('fieldset');fs.className='uncertainty-var';
 const lg=document.createElement('legend');lg.textContent='Variable '+(i+1);fs.append(lg);
 const box=document.createElement('div');box.className='num-fields';
 const mk=(type,value,cls)=>{const e=document.createElement('input');e.type=type;if(type==='number')e.step='any';e.value=value;e.className=cls;e.autocomplete='off';return e;};
 const sel=document.createElement('select');sel.className='uv-dist';
 for(const [v,t] of [['normal','Normal (u)'],['uniform','Uniform (half-width a)']]){const o=document.createElement('option');o.value=v;o.textContent=t;sel.append(o);}sel.value=dist;
 const spreadInput=mk('number',spread,'uv-spread'),spreadLabel=field(dist==='uniform'?'Half-width a':'Standard uncertainty u',spreadInput);
 sel.addEventListener('change',()=>{spreadLabel.firstChild.textContent=sel.value==='uniform'?'Half-width a':'Standard uncertainty u';});
 box.append(field('Name',mk('text',name,'uv-name')),field('Mean',mk('number',mean,'uv-mean')),field('Distribution',sel),spreadLabel);
 fs.append(box);varsBox.append(fs);
 for(const el of fs.querySelectorAll('input,select')){el.addEventListener('input',invalidate);el.addEventListener('change',invalidate);}
 syncButtons();
}
function syncButtons(){const n=varsBox.children.length;$('uncertainty-add').disabled=n>=MAX_VARS;$('uncertainty-remove').disabled=n<=1;}
function readVariables(){return [...varsBox.children].map(fs=>({name:fs.querySelector('.uv-name').value,mean:fs.querySelector('.uv-mean').value,distribution:fs.querySelector('.uv-dist').value,spread:fs.querySelector('.uv-spread').value}));}
function draw(mc){
 const ctx=canvas.getContext&&canvas.getContext('2d');if(!ctx)return;const W=canvas.width,H=canvas.height,c=mc.histogram.counts,top=Math.max(...c);
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);const bw=(W-20)/c.length;
 ctx.fillStyle='#4f63d2';c.forEach((v,i)=>{const h=(H-30)*v/top;ctx.fillRect(10+i*bw,H-20-h,Math.max(1,bw-1),h);});
 const span=mc.histogram.hi-mc.histogram.lo||1,xAt=v=>10+(W-20)*(v-mc.histogram.lo)/span;
 ctx.strokeStyle='#c0392b';ctx.lineWidth=2;for(const v of mc.symmetric95){ctx.beginPath();ctx.moveTo(xAt(v),5);ctx.lineTo(xAt(v),H-20);ctx.stroke();}
 ctx.fillStyle='#283752';ctx.font='11px sans-serif';ctx.fillText(fmt(mc.histogram.lo),10,H-6);const t=fmt(mc.histogram.hi);ctx.fillText(t,W-10-ctx.measureText(t).width,H-6);
 canvas.setAttribute('aria-label','Monte Carlo histogram of '+mc.samples+' samples from '+fmt(mc.histogram.lo)+' to '+fmt(mc.histogram.hi)+'; mean '+fmt(mc.mean)+', standard deviation '+fmt(mc.std)+'; 95% interval '+fmt(mc.symmetric95[0])+' to '+fmt(mc.symmetric95[1])+' marked in red.');
}
$('uncertainty-add').addEventListener('click',()=>{const n=varsBox.children.length;addVariable(String.fromCharCode(97+n),'1','0.1');invalidate();});
$('uncertainty-remove').addEventListener('click',()=>{if(varsBox.children.length>1)varsBox.lastElementChild.remove();syncButtons();invalidate();});
for(const el of area.querySelectorAll('#uncertainty-expression,#uncertainty-k,#uncertainty-samples,#uncertainty-seed,#uncertainty-correlations')){el.addEventListener('input',invalidate);el.addEventListener('change',invalidate);}
$('uncertainty-run').addEventListener('click',()=>{
 try{
  const r=run({expression:$('uncertainty-expression').value,variables:readVariables(),correlations:parseCorrelations($('uncertainty-correlations').value),k:$('uncertainty-k').value,samples:$('uncertainty-samples').value,seed:$('uncertainty-seed').value});
  const L=r.linear,C=r.monteCarlo,lines=[L.method,'y = '+fmt(L.value)+'; combined standard uncertainty u_c = '+fmt(L.uc),'Expanded U = k·u_c = '+fmt(L.U)+' (k = '+fmt(L.k)+'); interval ['+fmt(L.interval[0])+', '+fmt(L.interval[1])+']'];
  for(const c of L.contributions)lines.push('  '+c.name+': ∂f/∂'+c.name+' = '+fmt(c.sensitivity)+', u = '+fmt(c.u)+' ('+c.distribution+'), contribution '+fmt(c.percent)+'%');
  if(Math.abs(L.correlationPercent)>1e-9)lines.push('  correlation terms: '+fmt(L.correlationPercent)+'% of u_c²');
  lines.push('','Monte Carlo · N = '+C.samples+(C.truncated?' (time budget reached before '+C.requested+')':'')+', seed '+C.seed,'mean = '+fmt(C.mean)+'; std = '+fmt(C.std),
   'Probabilistically symmetric 95%: ['+fmt(C.symmetric95[0])+', '+fmt(C.symmetric95[1])+']','Shortest 95%: ['+fmt(C.shortest95[0])+', '+fmt(C.shortest95[1])+']','',(r.comparison.nonlinear?'NON-LINEARITY FLAG: ':'')+r.comparison.note,r.note);
  output.classList.remove('error');output.textContent=lines.join('\n');draw(C);
  const rows=[['expression',r.expression],['linear value',L.value],['linear u_c',L.uc],['k',L.k],['expanded U',L.U],['MC samples',C.samples],['MC seed',C.seed],['MC mean',C.mean],['MC std',C.std],
   ['MC symmetric 95% low',C.symmetric95[0]],['MC symmetric 95% high',C.symmetric95[1]],['MC shortest 95% low',C.shortest95[0]],['MC shortest 95% high',C.shortest95[1]],['MC min',C.min],['MC max',C.max],['non-linearity flag',r.comparison.nonlinear?'yes':'no']];
  for(const c of L.contributions)rows.push(['sensitivity '+c.name,c.sensitivity],['contribution % '+c.name,c.percent]);
  last={headers:['quantity','value'],rows};$('uncertainty-to-table').disabled=false;
 }catch(err){invalidate();output.classList.add('error');output.textContent=err.message+' Correct the input and run again.';canvas.setAttribute('aria-label','Monte Carlo histogram: not computed because of an input error');}
});
$('uncertainty-to-table').addEventListener('click',()=>{try{if(!last)throw Error('Propagate uncertainty first.');M.dataTables.importData({headers:last.headers,rows:last.rows},'Uncertainty_Summary');if(M.advanced?.mode)M.advanced.mode('data');}catch(err){output.classList.add('error');output.textContent=err.message;}});
addVariable('a','10','0.1');addVariable('b','5','0.2');
})();
