/* Offline nonlinear least-squares curve fitting: Levenberg–Marquardt with a finite-difference Jacobian.
   Models are evaluated only through MathStudio.numerical.evaluate (no eval/Function). Local optimum only. */
(()=>{'use strict';
const M=window.MathStudio=window.MathStudio||{};
const LIMIT=1e12,MAX_PARAMS=6,MAX_POINTS=10000,RESERVED=new Set(['x','e','pi','i','inf','infinity','nan']);
const EPS=2.220446049250313e-16,H_REL=6.0554544523933395e-6;

/* ---------- validation ---------- */
function num(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');const n=Number(value);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(name+' must be finite and at most 1e12 in magnitude.');return n;}
function bound(value,name,fallback){if(value===null||value===undefined||String(value).trim()==='')return fallback;const s=String(value).trim().toLowerCase();
 if(s==='-inf'||s==='-infinity')return -Infinity;if(s==='inf'||s==='+inf'||s==='infinity')return Infinity;return num(value,name);}
function evaluator(){const f=M.numerical?.evaluate;if(typeof f!=='function')throw Error('The numerical evaluator is unavailable.');return f;}
function numbers(list,name){
 if(!Array.isArray(list))throw Error(name+' must be a list of numbers.');
 return list.map((v,i)=>{const n=typeof v==='number'?v:String(v??'').trim()===''?NaN:Number(v);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(name+' value '+(i+1)+' must be finite and at most 1e12 in magnitude.');return n;});
}
function normalize({expression,parameters,x,y,weights=null,maxIterations=200,confidence=0.95}={}){
 expression=String(expression??'').trim();if(!expression||expression.length>1000)throw Error('Enter a model expression in x and the parameters (1–1000 characters).');
 if(!Array.isArray(parameters)||parameters.length<1||parameters.length>MAX_PARAMS)throw Error('Define 1 to '+MAX_PARAMS+' parameters.');
 const seen=new Set();
 const params=parameters.map((p,i)=>{
  const label='Parameter '+(i+1),name=String(p?.name??'').trim();
  if(!/^[A-Za-z][A-Za-z0-9_]{0,15}$/.test(name))throw Error(label+' name must start with a letter and use at most 16 letters, digits or underscores.');
  if(RESERVED.has(name.toLowerCase()))throw Error(label+' name "'+name+'" is reserved (x is the independent variable; e, pi and i are constants).');
  if(seen.has(name))throw Error('Parameter name "'+name+'" is duplicated.');seen.add(name);
  const lower=bound(p?.lower,name+' lower bound',-Infinity),upper=bound(p?.upper,name+' upper bound',Infinity);
  if(!(lower<upper))throw Error(name+' lower bound must be less than its upper bound.');
  const given=num(p?.initial,name+' initial guess'),initial=Math.min(upper,Math.max(lower,given));
  return {name,initial,lower,upper,projected:initial!==given};
 });
 const xs=numbers(x,'x'),ys=numbers(y,'y');
 if(xs.length!==ys.length)throw Error('x and y must have the same number of values ('+xs.length+' vs '+ys.length+').');
 if(xs.length>MAX_POINTS)throw Error('At most '+MAX_POINTS+' data points are supported.');
 const n=xs.length,p=params.length;
 if(n<=p)throw Error('Nonlinear least squares needs more data points than parameters (n = '+n+', p = '+p+'; need n > p).');
 let ws=null;
 if(weights!==null&&weights!==undefined){ws=numbers(weights,'Weight');if(ws.length!==n)throw Error('Provide exactly one weight per data point.');
  if(ws.some(w=>!(w>0)))throw Error('Weights must be positive (use 1/σ² for known measurement standard deviations σ).');}
 maxIterations=num(maxIterations,'Iteration budget');if(!Number.isInteger(maxIterations)||maxIterations<1||maxIterations>5000)throw Error('Iteration budget must be an integer from 1 to 5000.');
 confidence=num(confidence,'Confidence level');if(!(confidence>0&&confidence<1))throw Error('Confidence level must be between 0 and 1.');
 return {expression,params,x:xs,y:ys,w:ws||xs.map(()=>1),weighted:!!ws,n,p,maxIterations,confidence};
}

/* ---------- model, residuals and Jacobian ---------- */
function modelOf(spec){
 const f=evaluator();let calls=0;
 const at=(xv,pv)=>{const env={x:xv};spec.params.forEach((q,j)=>{env[q.name]=pv[j];});calls++;const v=f(spec.expression,env);
  if(!Number.isFinite(v)||Math.abs(v)>LIMIT)throw Error('Model must return a finite real value at most 1e12 in magnitude.');return v;};
 return {get calls(){return calls;},at,
  values(pv){return spec.x.map((xv,i)=>{try{return at(xv,pv);}catch(err){const e=Error('Model cannot be evaluated at data point '+(i+1)+' (x = '+xv+') with '+spec.params.map((q,j)=>q.name+' = '+Number(pv[j].toPrecision(8))).join(', ')+': '+err.message);e.domain=true;throw e;}});}};
}
function costOf(spec,fv){let s=0;for(let i=0;i<spec.n;i++){const r=spec.y[i]-fv[i];s+=spec.w[i]*r*r;}return s;}
/** Central differences, one-sided when a bound blocks a side; step scaled by |p_j| (or 1e-4 near zero). */
function jacobian(spec,F,pv,fv){
 const J=spec.x.map(()=>new Array(spec.p).fill(0));
 for(let j=0;j<spec.p;j++){
  const q=spec.params[j],h=H_REL*Math.max(Math.abs(pv[j]),1e-4),up=pv.slice(),dn=pv.slice();
  const canUp=pv[j]+h<=q.upper,canDn=pv[j]-h>=q.lower;
  let fu=null,fd=null;
  const tryAt=(vec)=>{try{return F.values(vec);}catch{return null;}};
  if(canUp){up[j]=pv[j]+h;fu=tryAt(up);}
  if(canDn){dn[j]=pv[j]-h;fd=tryAt(dn);}
  if(fu&&fd){for(let i=0;i<spec.n;i++)J[i][j]=(fu[i]-fd[i])/(2*h);}
  else if(fu){for(let i=0;i<spec.n;i++)J[i][j]=(fu[i]-fv[i])/h;}
  else if(fd){for(let i=0;i<spec.n;i++)J[i][j]=(fv[i]-fd[i])/h;}
  else throw Error('The Jacobian column for '+q.name+' cannot be computed: the model is undefined on both sides of '+q.name+' = '+Number(pv[j].toPrecision(8))+'.');
 }
 return J;
}
function normalEquations(spec,J,fv){
 const p=spec.p,A=Array.from({length:p},()=>new Array(p).fill(0)),g=new Array(p).fill(0);
 for(let i=0;i<spec.n;i++){const w=spec.w[i],r=spec.y[i]-fv[i],row=J[i];
  for(let a=0;a<p;a++){const wa=w*row[a];g[a]+=wa*r;for(let b=a;b<p;b++)A[a][b]+=wa*row[b];}}
 for(let a=0;a<p;a++)for(let b=0;b<a;b++)A[a][b]=A[b][a];
 return {A,g};
}
/** Cholesky solve of a small symmetric positive-definite system; returns null when it is not positive definite. */
function choleskySolve(A,b){
 const n=A.length,L=A.map(()=>new Array(n).fill(0));
 for(let j=0;j<n;j++){let d=A[j][j];for(let k=0;k<j;k++)d-=L[j][k]*L[j][k];if(!(d>0)||!Number.isFinite(d))return null;L[j][j]=Math.sqrt(d);
  for(let i=j+1;i<n;i++){let s=A[i][j];for(let k=0;k<j;k++)s-=L[i][k]*L[j][k];L[i][j]=s/L[j][j];}}
 const z=new Array(n);for(let i=0;i<n;i++){let s=b[i];for(let k=0;k<i;k++)s-=L[i][k]*z[k];z[i]=s/L[i][i];}
 const x=new Array(n);for(let i=n-1;i>=0;i--){let s=z[i];for(let k=i+1;k<n;k++)s-=L[k][i]*x[k];x[i]=s/L[i][i];}
 return x;
}
/** Cyclic Jacobi eigen-decomposition of a small symmetric matrix. */
function symmetricEigen(S){
 const n=S.length,A=S.map(r=>r.slice()),V=A.map((_,i)=>A.map((_,j)=>i===j?1:0));
 for(let sweep=0;sweep<100;sweep++){
  let off=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)off+=A[i][j]*A[i][j];
  if(off<1e-36)break;
  for(let p=0;p<n;p++)for(let q=p+1;q<n;q++){
   if(Math.abs(A[p][q])<1e-300)continue;
   const th=(A[q][q]-A[p][p])/(2*A[p][q]),t=Math.sign(th||1)/(Math.abs(th)+Math.sqrt(th*th+1)),c=1/Math.sqrt(t*t+1),s=t*c;
   for(let k=0;k<n;k++){const akp=A[k][p],akq=A[k][q];A[k][p]=c*akp-s*akq;A[k][q]=s*akp+c*akq;}
   for(let k=0;k<n;k++){const apk=A[p][k],aqk=A[q][k];A[p][k]=c*apk-s*aqk;A[q][k]=s*apk+c*aqk;}
   for(let k=0;k<n;k++){const vkp=V[k][p],vkq=V[k][q];V[k][p]=c*vkp-s*vkq;V[k][q]=s*vkp+c*vkq;}
  }
 }
 return {values:A.map((r,i)=>r[i]),vectors:V};
}
function tQuantile(confidence,df){
 const S=M.statistics;if(!S||typeof S.distribution!=='function')return null;
 return S.distribution('t',{nu:df}).quantile(1-(1-confidence)/2);
}

/* ---------- Levenberg–Marquardt ---------- */
function fit(options={}){
 const spec=normalize(options),F=modelOf(spec),p=spec.p;
 const XTOL=1e-12,FTOL=1e-15,GTOL=1e-12;
 let pv=spec.params.map(q=>q.initial),fv;
 try{fv=F.values(pv);}catch(err){throw Error('Initial guess is invalid. '+err.message+' Check the expression, parameter names and initial guesses.');}
 let cost=costOf(spec,fv),lambda=1e-3,iterations=0,status='iteration-limit',reason='Iteration budget of '+spec.maxIterations+' reached before convergence; the result is the best point found so far, not a converged fit.';
 const initialCost=cost,yss=Math.max(1,spec.y.reduce((s,v,i)=>s+spec.w[i]*v*v,0)),floor=1e-30*yss;
 let J=jacobian(spec,F,pv,fv),{A,g}=normalEquations(spec,J,fv);
 outer:for(;iterations<spec.maxIterations;iterations++){
  if(cost<=floor){status='converged';reason='Residual sum of squares is at the floating-point roundoff level (exact fit).';break;}
  // Scaled gradient test (cosine between residual and each Jacobian column, as in MINPACK).
  let gmax=0;for(let j=0;j<p;j++){const cn=Math.sqrt(A[j][j]);if(cn>0)gmax=Math.max(gmax,Math.abs(g[j])/(cn*Math.sqrt(cost)));}
  if(gmax<=GTOL){status='converged';reason='Gradient condition satisfied (residuals are orthogonal to the Jacobian columns).';break;}
  const dmax=Math.max(...A.map((r,j)=>r[j]),0);
  for(;;){
   if(lambda>1e16){status='stalled';reason='No further decrease in the residual sum of squares is possible from this point (damping limit reached); the point may be a local minimum or the model may be poorly scaled.';break outer;}
   const B=A.map((r,a)=>r.map((v,b)=>a===b?v+lambda*Math.max(v,1e-12*dmax,1e-300):v));
   const step=choleskySolve(B,g);
   if(!step||step.some(v=>!Number.isFinite(v))){lambda*=10;continue;}
   const trial=pv.map((v,j)=>Math.min(spec.params[j].upper,Math.max(spec.params[j].lower,v+step[j])));
   let tf=null;try{tf=F.values(trial);}catch{tf=null;}
   const tc=tf?costOf(spec,tf):Infinity;
   if(tc<cost){
    const dp=Math.sqrt(trial.reduce((s,v,j)=>s+(v-pv[j])**2,0)),pn=Math.sqrt(trial.reduce((s,v)=>s+v*v,0));
    const rel=(cost-tc)/cost;
    pv=trial;fv=tf;cost=tc;lambda=Math.max(lambda/10,1e-12);
    J=jacobian(spec,F,pv,fv);({A,g}=normalEquations(spec,J,fv));
    if(dp<=XTOL*(pn+XTOL)){status='converged';reason='Relative parameter step below 1e-12.';iterations++;break outer;}
    if(rel<=FTOL){status='converged';reason='Relative reduction of the residual sum of squares below 1e-15.';iterations++;break outer;}
    break;
   }
   const dpTry=Math.sqrt(trial.reduce((s,v,j)=>s+(v-pv[j])**2,0)),pnTry=Math.sqrt(pv.reduce((s,v)=>s+v*v,0));
   if(tf&&dpTry<=XTOL*(pnTry+XTOL)){if(gmax<=1e-6||cost<=1e-20*yss){status='converged';reason='Relative parameter step below 1e-12 without further decrease (scaled gradient '+Number(gmax.toPrecision(2))+', SSR '+Number(cost.toPrecision(3))+').';}else{status='stalled';reason='Steps became negligible (below 1e-12 relative) while the scaled gradient is still '+Number(gmax.toPrecision(2))+'; the fit stalled and may not be a minimum.';}break outer;}
   lambda*=10;
  }
 }
 return summarize(spec,F,pv,fv,cost,{iterations,status,reason,initialCost,lambda});
}
function summarize(spec,F,pv,fv,cost,info){
 const {n,p}=spec,J=jacobian(spec,F,pv,fv),{A}=normalEquations(spec,J,fv);
 const residuals=spec.y.map((v,i)=>v-fv[i]),dof=n-p,s2=cost/dof;
 let ybar=0,wsum=0;for(let i=0;i<n;i++){ybar+=spec.w[i]*spec.y[i];wsum+=spec.w[i];}ybar/=wsum;
 let sst=0;for(let i=0;i<n;i++)sst+=spec.w[i]*(spec.y[i]-ybar)**2;
 const rss=residuals.reduce((s,r)=>s+r*r,0);
 const warnings=[];let condition=Infinity,cov=null;
 const d=A.map((r,j)=>r[j]);
 if(d.every(v=>v>0)){
  const sc=d.map(Math.sqrt),S=A.map((r,a)=>r.map((v,b)=>v/(sc[a]*sc[b]))),E=symmetricEigen(S);
  const emax=Math.max(...E.values),emin=Math.min(...E.values);
  condition=emin>0?emax/emin:Infinity;
  if(emin>emax*1e-14){
   cov=A.map((_,a)=>A.map((_,b)=>{let s=0;for(let k=0;k<p;k++)s+=E.vectors[a][k]*E.vectors[b][k]/E.values[k];return s/(sc[a]*sc[b]);}));
  }
 }
 const zero=spec.params.filter((_,j)=>!(d[j]>0)).map(q=>q.name);
 if(zero.length)warnings.push('The model does not depend on '+zero.join(', ')+' at the solution (zero Jacobian column); those parameters are not identifiable.');
 if(condition>1e10)warnings.push('JᵀWJ is near-singular (scaled condition number '+(Number.isFinite(condition)?Number(condition.toPrecision(3)):'∞')+'): the parameters are not identifiable from these data (strongly correlated or redundant)'+(cov?'; standard errors are unreliable.':'; standard errors are not reported.'));
 const tq=cov?tQuantile(spec.confidence,dof):null;
 if(cov&&tq===null)warnings.push('Statistics module unavailable: confidence intervals are not reported.');
 const atBound=[];
 const parameters=spec.params.map((q,j)=>{
  const value=pv[j],se=cov&&cov[j][j]>=0?Math.sqrt(s2*cov[j][j]):null,onBound=value===q.lower||value===q.upper;
  if(onBound)atBound.push(q.name);
  return {name:q.name,value,standardError:se,ci:se!==null&&tq!==null?[value-tq*se,value+tq*se]:null,lower:q.lower,upper:q.upper,atBound:onBound,initial:q.initial,projected:q.projected};
 });
 if(atBound.length)warnings.push('Parameter(s) '+atBound.join(', ')+' finished on a bound; standard errors and intervals assume an interior optimum and are only indicative there.');
 const projected=spec.params.filter(q=>q.projected).map(q=>q.name);
 if(projected.length)warnings.push('Initial guess for '+projected.join(', ')+' was projected into its bounds.');
 if(info.status!=='converged')warnings.push(info.reason);
 const correlation=cov?cov.map((r,a)=>r.map((v,b)=>v/Math.sqrt(cov[a][a]*cov[b][b]))):null;
 return {type:'nonlinear-fit',expression:spec.expression,parameters,converged:info.status==='converged',status:info.status,reason:info.reason,iterations:info.iterations,evaluations:F.calls,
  n,p,dof,weighted:spec.weighted,ssr:cost,initialSsr:info.initialCost,s2,residualStd:Math.sqrt(s2),rmse:Math.sqrt(rss/n),rSquared:sst>0?1-cost/sst:null,
  confidence:spec.confidence,tQuantile:tq,covariance:cov?cov.map(r=>r.map(v=>v*s2)):null,correlation,condition,identifiable:!!cov&&condition<=1e10&&!zero.length,
  x:spec.x.slice(),y:spec.y.slice(),fitted:fv.slice(),residuals,warnings,
  method:'Levenberg–Marquardt (Marquardt diagonal scaling, central-difference Jacobian, bounds by projection)',
  note:'Local least-squares optimum from the given initial guess; a global optimum is not guaranteed. Standard errors use the linearised covariance (JᵀWJ)⁻¹·s² with s² = SSR/(n−p).'};
}

/* ---------- data helpers ---------- */
function parseList(text){
 const parts=String(text??'').split(/[\s,;]+/).filter(Boolean);
 return parts.map((s,i)=>{const v=Number(s);if(!Number.isFinite(v))throw Error('List value '+(i+1)+' ("'+s.slice(0,20)+'") is not a number.');return v;});
}
function parseParameters(text){
 const out=[];for(const [i,raw] of String(text??'').split(/\n|;/).entries()){
  const line=raw.trim();if(!line)continue;const parts=line.split(/[\s,]+/).filter(Boolean);
  if(parts.length!==2&&parts.length!==4)throw Error('Parameter line '+(i+1)+' must read: name initial [lower upper].');
  out.push({name:parts[0],initial:parts[1],lower:parts[2],upper:parts[3]});
 }
 return out;
}
function tableData({table,xColumn,yColumn,weightColumn=null}={}){
 const T=M.dataTables;if(!T)throw Error('Data Tables are unavailable.');
 const t=T.tables.find(s=>s.id===table||s.name===table);if(!t)throw Error('Choose an existing data table.');
 const rows=typeof T.calculate==='function'?T.calculate(t):t.rows;
 const col=c=>{const i=typeof c==='number'?c:t.columns.indexOf(String(c??''));if(!(i>=0&&i<t.columns.length))throw Error('Choose an existing column.');return i;};
 const xi=col(xColumn),yi=col(yColumn),wi=weightColumn===null||weightColumn===undefined||weightColumn===''?-1:col(weightColumn);
 const toNum=v=>{if(typeof v==='number')return v;const s=String(v??'').trim();return s===''?NaN:Number(s);};
 const x=[],y=[],w=[];let skipped=0;
 for(const r of rows){const a=toNum(r?.[xi]),b=toNum(r?.[yi]),c=wi<0?1:toNum(r?.[wi]);
  if(Number.isFinite(a)&&Number.isFinite(b)&&Number.isFinite(c)){x.push(a);y.push(b);w.push(c);}else if(r&&r.some(v=>String(v??'').trim()!==''))skipped++;}
 return {x,y,weights:wi<0?null:w,skipped,table:t.name,columns:[t.columns[xi],t.columns[yi],wi<0?null:t.columns[wi]]};
}
function fitTable(options={}){const d=tableData(options),r=fit({...options,x:d.x,y:d.y,weights:d.weights});r.source=d;return r;}
function curve(result,count=200){
 const F=modelOf(normalize({expression:result.expression,parameters:result.parameters.map(q=>({name:q.name,initial:q.value})),x:result.x,y:result.y}));
 const lo=Math.min(...result.x),hi=Math.max(...result.x),pv=result.parameters.map(q=>q.value);
 return Array.from({length:count},(_,i)=>{const xv=lo+(hi-lo)*i/(count-1);let v=NaN;try{v=F.at(xv,pv);}catch{v=NaN;}return [xv,v];});
}

M.nonlinearFit={fit,fitTable,tableData,parseList,parseParameters,curve,normalize,symmetricEigen};

/* ---------- UI (static template only; user text is set via textContent/value) ---------- */
const panel=document.getElementById('graph-panel');if(!panel||!document.createElement||document.getElementById('nlfit-details'))return;
const $=id=>document.getElementById(id);
const fmt=v=>v===null||v===undefined?'—':Number.isFinite(v)?Number(v.toPrecision(10)).toString():String(v);
const area=document.createElement('details');area.id='nlfit-details';
area.innerHTML='<summary>Nonlinear least-squares fit · Levenberg–Marquardt</summary>'+
 '<style>#nlfit-details{padding:12px 16px;margin:12px 0 20px;border:1px solid #d8dfeb;border-radius:13px;background:#f9fbff;max-width:100%;box-sizing:border-box;min-width:0}'+
 '#nlfit-details>summary{font-weight:760;cursor:pointer;min-height:40px;display:flex;align-items:center}'+
 '#nlfit-details .nlfit-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,180px),1fr));gap:10px;margin:10px 0}'+
 '#nlfit-details label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:650;min-width:0}'+
 '#nlfit-details input,#nlfit-details select,#nlfit-details textarea{width:100%;min-width:0;min-height:42px;box-sizing:border-box;padding:9px 10px;border:1px solid #cdd8ec;border-radius:9px;background:#fff;font:inherit}'+
 '#nlfit-details button{min-height:42px}#nlfit-details .data-toolbar{display:flex;flex-wrap:wrap;gap:8px}'+
 '#nlfit-canvas{width:100%;max-width:520px;height:auto;display:block;border:1px solid #d8dfeb;border-radius:9px;background:#fff;margin-top:8px}'+
 '#nlfit-output{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;margin:8px 0}#nlfit-output.error{color:#a12020}</style>'+
 '<p>Fit y ≈ f(x; parameters) by weighted nonlinear least squares. Reports a local optimum from your initial guesses, with standard errors and confidence intervals.</p>'+
 '<div class="nlfit-grid"><label>Data source<select id="nlfit-source"><option value="lists">Typed lists</option><option value="table">Data Table columns</option></select></label>'+
 '<label class="nlfit-table">Table<select id="nlfit-table"></select></label>'+
 '<label class="nlfit-table">X column<select id="nlfit-x-col"></select></label>'+
 '<label class="nlfit-table">Y column<select id="nlfit-y-col"></select></label>'+
 '<label class="nlfit-table">Weight column (optional)<select id="nlfit-w-col"></select></label>'+
 '<label class="nlfit-list">x values<textarea id="nlfit-x" rows="2" spellcheck="false">0 1 2 3 4 5 6</textarea></label>'+
 '<label class="nlfit-list">y values<textarea id="nlfit-y" rows="2" spellcheck="false">3 2.213061319425 1.735758882343 1.446260320297 1.270670566473 1.164169997248 1.099574136736</textarea></label></div>'+
 '<div class="nlfit-grid"><label>Model y = f(x; parameters)<input id="nlfit-expression" value="a*exp(-b*x)+c" autocomplete="off" spellcheck="false"></label>'+
 '<label>Parameters (one per line: name initial [lower upper])<textarea id="nlfit-params" rows="3" spellcheck="false">a 1\nb 1\nc 0</textarea></label>'+
 '<label>Iteration budget<input id="nlfit-iterations" type="number" min="1" max="5000" step="1" value="200"></label>'+
 '<label>Confidence level<input id="nlfit-confidence" type="number" min="0.5" max="0.999" step="any" value="0.95"></label></div>'+
 '<div class="data-toolbar"><button id="nlfit-run" class="primary" type="button">Fit model</button>'+
 '<button id="nlfit-to-table" class="secondary" type="button" disabled>Save residuals to Data Tables</button></div>'+
 '<pre id="nlfit-output" role="status" aria-live="polite">Enter data, a model and initial guesses, then choose Fit model.</pre>'+
 '<canvas id="nlfit-canvas" width="520" height="220" role="img" aria-label="Nonlinear fit plot: not yet computed"></canvas>';
panel.append(area);let last=null;
const output=$('nlfit-output'),canvas=$('nlfit-canvas');
const invalidate=()=>{last=null;$('nlfit-to-table').disabled=true;output.classList.remove('error');};
function option(sel,value,text){const o=document.createElement('option');o.value=value;o.textContent=text;sel.append(o);}
function refreshTables(){
 const T=M.dataTables,sel=$('nlfit-table'),keep=sel.value;sel.replaceChildren();
 for(const t of T?.tables||[])option(sel,t.id,t.name);
 if([...sel.options].some(o=>o.value===keep))sel.value=keep;refreshColumns();
}
function refreshColumns(){
 const t=(M.dataTables?.tables||[]).find(s=>s.id===$('nlfit-table').value);
 for(const [id,optional] of [['nlfit-x-col',false],['nlfit-y-col',false],['nlfit-w-col',true]]){
  const sel=$(id),keep=sel.value;sel.replaceChildren();if(optional)option(sel,'','None (unweighted)');
  (t?.columns||[]).forEach((c,i)=>option(sel,String(i),c||('Column '+(i+1))));
  if([...sel.options].some(o=>o.value===keep))sel.value=keep;
 }
 if(t&&t.columns.length>1&&$('nlfit-y-col').value===$('nlfit-x-col').value)$('nlfit-y-col').value='1';
}
function syncSource(){const table=$('nlfit-source').value==='table';for(const e of area.querySelectorAll('.nlfit-table'))e.hidden=!table;for(const e of area.querySelectorAll('.nlfit-list'))e.hidden=table;if(table)refreshTables();}
function draw(r){
 const ctx=canvas.getContext&&canvas.getContext('2d');if(!ctx)return;const W=canvas.width,H=canvas.height,pad=34;
 const pts=curve(r),ys=r.y.concat(pts.map(q=>q[1]).filter(Number.isFinite));
 const x0=Math.min(...r.x),x1=Math.max(...r.x),y0=Math.min(...ys),y1=Math.max(...ys),sx=x1-x0||1,sy=y1-y0||1;
 const X=v=>pad+(W-pad-10)*(v-x0)/sx,Y=v=>H-pad+(-(H-pad-10))*(v-y0)/sy;
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
 ctx.strokeStyle='#c7d2e4';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(pad,10);ctx.lineTo(pad,H-pad);ctx.lineTo(W-10,H-pad);ctx.stroke();
 ctx.strokeStyle='#c0392b';ctx.lineWidth=2;ctx.beginPath();let pen=false;
 for(const [a,b] of pts){if(!Number.isFinite(b)){pen=false;continue;}if(pen)ctx.lineTo(X(a),Y(b));else{ctx.moveTo(X(a),Y(b));pen=true;}}ctx.stroke();
 ctx.fillStyle='#2f49b8';for(let i=0;i<r.x.length;i++){ctx.beginPath();ctx.arc(X(r.x[i]),Y(r.y[i]),3,0,2*Math.PI);ctx.fill();}
 ctx.fillStyle='#283752';ctx.font='11px sans-serif';ctx.fillText(fmt(x0),pad,H-pad+14);const t=fmt(x1);ctx.fillText(t,W-10-ctx.measureText(t).width,H-pad+14);ctx.fillText(fmt(y1),2,16);ctx.fillText(fmt(y0),2,H-pad);
 canvas.setAttribute('aria-label','Nonlinear fit plot: '+r.n+' data points (blue dots) and fitted curve y = '+r.expression+' (red line) for x from '+fmt(x0)+' to '+fmt(x1)+'; R² = '+fmt(r.rSquared)+'.');
}
function report(r){
 const pct=Math.round(r.confidence*1000)/10,lines=[r.method,(r.converged?'Converged':'NOT CONVERGED')+' after '+r.iterations+' iterations ('+r.evaluations+' model evaluations): '+r.reason,
  'n = '+r.n+', p = '+r.p+', degrees of freedom = '+r.dof+(r.weighted?' (weighted)':''),''];
 for(const q of r.parameters)lines.push(q.name+' = '+fmt(q.value)+(q.standardError!==null?' ± '+fmt(q.standardError)+' (SE)':'')+(q.ci?'; '+pct+'% CI ['+fmt(q.ci[0])+', '+fmt(q.ci[1])+']':'')+(q.atBound?' [at bound]':''));
 lines.push('','SSR = '+fmt(r.ssr)+'; s = '+fmt(r.residualStd)+'; RMSE = '+fmt(r.rmse)+'; R² = '+fmt(r.rSquared));
 if(r.tQuantile!==null)lines.push('Student t quantile (ν = '+r.dof+') = '+fmt(r.tQuantile));
 for(const w of r.warnings)lines.push('WARNING: '+w);
 lines.push('',r.note);return lines.join('\n');
}
$('nlfit-source').addEventListener('change',()=>{syncSource();invalidate();});
$('nlfit-table').addEventListener('change',()=>{refreshColumns();invalidate();});
$('nlfit-table').addEventListener('focus',()=>{const n=$('nlfit-table').options.length;if(n!==(M.dataTables?.tables||[]).length)refreshTables();});
area.addEventListener('toggle',()=>{if(area.open&&$('nlfit-source').value==='table')refreshTables();});
for(const el of area.querySelectorAll('input,textarea,select')){el.addEventListener('input',invalidate);el.addEventListener('change',invalidate);}
$('nlfit-run').addEventListener('click',()=>{
 try{
  const common={expression:$('nlfit-expression').value,parameters:parseParameters($('nlfit-params').value),maxIterations:$('nlfit-iterations').value,confidence:$('nlfit-confidence').value};
  let r;
  if($('nlfit-source').value==='table'){
   const wc=$('nlfit-w-col').value;
   r=fitTable({...common,table:$('nlfit-table').value,xColumn:Number($('nlfit-x-col').value),yColumn:Number($('nlfit-y-col').value),weightColumn:wc===''?null:Number(wc)});
  }else r=fit({...common,x:parseList($('nlfit-x').value),y:parseList($('nlfit-y').value)});
  output.classList.remove('error');output.textContent=report(r)+(r.source?.skipped?'\n'+r.source.skipped+' non-numeric row(s) skipped.':'');draw(r);
  last={headers:['x','y','fitted','residual'],rows:r.x.map((v,i)=>[v,r.y[i],r.fitted[i],r.residuals[i]])};$('nlfit-to-table').disabled=false;
 }catch(err){invalidate();output.classList.add('error');output.textContent=err.message+' Correct the input and fit again.';canvas.setAttribute('aria-label','Nonlinear fit plot: not computed because of an input error');}
});
$('nlfit-to-table').addEventListener('click',()=>{try{if(!last)throw Error('Fit a model first.');M.dataTables.importData({headers:last.headers,rows:last.rows},'NLFit_Residuals');}catch(err){output.classList.add('error');output.textContent=err.message;}});
syncSource();
})();
