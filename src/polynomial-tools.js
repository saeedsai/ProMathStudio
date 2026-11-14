/* ProMathStudio: polynomial tools over real/complex coefficients (offline, no eval).
   Roots by Aberth-Ehrlich simultaneous iteration; Horner evaluation; calculus; arithmetic; numerical GCD. */
(()=>{'use strict';
const M=window.MathStudio;
if(!M)return;
const MAX_DEGREE=30,MAX_TERMS=64,MAX_TEXT=4000,EPS=Number.EPSILON;
/* Complex numbers are [re, im] pairs. */
const C=(re,im=0)=>[re,im];
const cadd=(a,b)=>[a[0]+b[0],a[1]+b[1]];
const csub=(a,b)=>[a[0]-b[0],a[1]-b[1]];
const cmul=(a,b)=>[a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]];
const cabs=a=>Math.hypot(a[0],a[1]);
const isZero=a=>a[0]===0&&a[1]===0;
function cdiv(a,b){ /* Smith's algorithm avoids needless overflow. */
 if(Math.abs(b[1])<=Math.abs(b[0])){const r=b[1]/b[0],d=b[0]+b[1]*r;return [(a[0]+a[1]*r)/d,(a[1]-a[0]*r)/d];}
 const r=b[0]/b[1],d=b[0]*r+b[1];return [(a[0]*r+a[1])/d,(a[1]*r-a[0])/d];
}

/* ---------- Parsing ---------- */
const NUM='(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?';
const RE_REAL=new RegExp('^[+-]?'+NUM+'$');
const RE_IMAG=new RegExp('^([+-]?)('+NUM+')?\\*?[ij]$');
const RE_CPLX=new RegExp('^([+-]?'+NUM+')([+-])('+NUM+')?\\*?[ij]$');
function finite(x,token){if(!Number.isFinite(x))throw Error('Coefficient "'+token+'" is outside the finite floating-point range.');return x;}
function parseComplex(value,what='Value'){
 if(typeof value==='number'){if(!Number.isFinite(value))throw Error(what+' must be a finite number.');return C(value);}
 if(Array.isArray(value)&&value.length===2&&value.every(v=>typeof v==='number'&&Number.isFinite(v)))return C(value[0],value[1]);
 if(value&&typeof value==='object'&&!Array.isArray(value)&&Number.isFinite(value.re)&&Number.isFinite(value.im??0))return C(value.re,value.im??0);
 const s=String(value??'').replace(/\s+/g,'').replace(/−/g,'-');
 if(!s)throw Error(what+' is empty; enter a number such as 2, -1.5, 3i or 1+2i.');
 let m;
 if(RE_REAL.test(s))return C(finite(Number(s),s));
 if((m=RE_IMAG.exec(s)))return C(0,finite((m[1]==='-'?-1:1)*(m[2]===undefined?1:Number(m[2])),s));
 if((m=RE_CPLX.exec(s)))return C(finite(Number(m[1]),s),finite((m[2]==='-'?-1:1)*(m[3]===undefined?1:Number(m[3])),s));
 throw Error(what+' "'+s.slice(0,40)+'" is not a number; use forms such as 2, -1.5e-3, 3i or 1-2i.');
}
function parseList(input,what){
 let items;
 if(Array.isArray(input))items=input;
 else{
  const s=String(input??'');
  if(s.length>MAX_TEXT)throw Error(what+' text is too long (limit '+MAX_TEXT+' characters).');
  if(!s.trim())throw Error(what+' is empty; enter comma-separated numbers, highest degree first.');
  items=s.split(/[,;\n]/).map(t=>t.trim());
  if(items.length&&items[items.length-1]==='')items.pop();
 }
 if(!items.length)throw Error(what+' is empty; enter comma-separated numbers, highest degree first.');
 if(items.length>MAX_TERMS)throw Error(what+' has too many entries (limit '+MAX_TERMS+').');
 return items.map((t,i)=>parseComplex(t,what+' entry '+(i+1)));
}
function trimLeading(a){let i=0;while(i<a.length-1&&isZero(a[i]))i++;return a.slice(i);}
/* Coefficients highest degree first; leading zeros are dropped; zero polynomial and degree > 30 are rejected. */
function parsePoly(input,what='Coefficients',maxDegree=MAX_DEGREE){
 const a=trimLeading(parseList(input,what));
 if(a.length===1&&isZero(a[0]))throw Error(what+' are all zero; the zero polynomial has no defined degree or roots.');
 if(a.length-1>maxDegree)throw Error(what+' give degree '+(a.length-1)+', which exceeds the supported maximum degree '+maxDegree+'.');
 return a;
}

/* ---------- Evaluation ---------- */
/* Horner with derivative and the running bound s = Σ|a_i||z|^i used for backward error. */
function hornerD(a,z){
 let p=a[0],d=C(0),s=cabs(a[0]);const az=cabs(z);
 for(let i=1;i<a.length;i++){d=cadd(cmul(d,z),p);p=cadd(cmul(p,z),a[i]);s=s*az+cabs(a[i]);}
 return {p,d,s};
}
/* Newton ratio p/p' and backward error; for |z|>1 the reversed polynomial avoids overflow. */
function newtonRatio(a,rev,z){
 const n=a.length-1;
 if(cabs(z)<=1){
  const h=hornerD(a,z);const berr=h.s>0?cabs(h.p)/h.s:0;
  return {ratio:isZero(h.p)?C(0):isZero(h.d)?null:cdiv(h.p,h.d),berr};
 }
 const w=cdiv(C(1),z),h=hornerD(rev,w);const berr=h.s>0?cabs(h.p)/h.s:0;
 if(isZero(h.p))return {ratio:C(0),berr};
 const den=csub(cmul(C(n),h.p),cmul(w,h.d));
 return {ratio:isZero(den)?null:cdiv(cmul(z,h.p),den),berr};
}
function backwardError(a,z){return newtonRatio(a,a.slice().reverse(),z).berr;}
function evaluate(coefficients,point){
 const a=parsePoly(coefficients),z=parseComplex(point,'Point x'),h=hornerD(a,z);
 if(![...h.p,...h.d].every(Number.isFinite))throw Error('Evaluation overflowed the floating-point range at this point.');
 return {value:obj(h.p),derivative:obj(h.d),point:obj(z),degree:a.length-1,
  conditionBound:h.s,relativeErrorBound:2*(a.length)*EPS*h.s/Math.max(cabs(h.p),Number.MIN_VALUE)};
}

/* ---------- Roots: Aberth-Ehrlich ---------- */
/* Unique positive root of Cauchy's polynomial |a0| x^n - Σ |a_i| x^(n-i): every root satisfies |z| ≤ it. */
function cauchyRadius(a){
 const n=a.length-1,b=a.map(cabs),f=x=>{let v=b[0];for(let i=1;i<=n;i++)v=v*x-b[i];return v;};
 let hi=1;while(f(hi)<0&&hi<1e300)hi*=2;let lo=hi/2;if(f(lo)>=0)lo=0;
 for(let k=0;k<200&&hi-lo>1e-15*hi;k++){const mid=(lo+hi)/2;if(f(mid)<0)lo=mid;else hi=mid;}
 return hi;
}
function roots(coefficients,options={}){
 const a0=parsePoly(coefficients);
 const clusterTol=options.clusterTolerance===undefined||options.clusterTolerance===''?1e-4:Number(options.clusterTolerance);
 if(!Number.isFinite(clusterTol)||clusterTol<0||clusterTol>=1)throw Error('Cluster tolerance must be a number in [0, 1).');
 const maxIterations=options.maxIterations===undefined?1000:Math.floor(Number(options.maxIterations));
 if(!Number.isFinite(maxIterations)||maxIterations<1||maxIterations>100000)throw Error('Maximum iterations must be between 1 and 100000.');
 /* Exact zero roots from trailing zero coefficients. */
 let zeroCount=0;while(a0.length-zeroCount>1&&isZero(a0[a0.length-1-zeroCount]))zeroCount++;
 const a=a0.slice(0,a0.length-zeroCount),n=a.length-1,rev=a.slice().reverse();
 let z=[],iterations=0,converged=true,radius=0;
 if(n===1)z=[cdiv(C(-a[1][0],-a[1][1]),a[0])];
 else if(n>1){
  radius=cauchyRadius(a);
  /* Initial circle: Cauchy radius, rotated off the real axis to break conjugate symmetry. */
  for(let k=0;k<n;k++){const t=2*Math.PI*k/n+0.4;z.push(C(radius*Math.cos(t),radius*Math.sin(t)));}
  const done=new Array(n).fill(false),stopB=4*(n+1)*EPS;
  converged=false;
  for(iterations=0;iterations<maxIterations;){
   iterations++;let active=0;
   for(let k=0;k<n;k++){
    if(done[k])continue;
    const nr=newtonRatio(a,rev,z[k]);
    if(nr.berr<=stopB){done[k]=true;continue;}
    active++;
    let S=C(0);
    for(let j=0;j<n;j++)if(j!==k){let diff=csub(z[k],z[j]);if(isZero(diff))diff=C(EPS*Math.max(1,cabs(z[k])),EPS);S=cadd(S,cdiv(C(1),diff));}
    let w;
    if(nr.ratio===null)w=C(EPS*Math.max(1,cabs(z[k])),EPS*Math.max(1,cabs(z[k]))); /* p'=0: nudge off the critical point */
    else{const den=csub(C(1),cmul(nr.ratio,S));w=isZero(den)?nr.ratio:cdiv(nr.ratio,den);}
    const next=csub(z[k],w);
    if(!next.every(Number.isFinite))throw Error('Aberth iteration overflowed; the coefficients may span too many orders of magnitude.');
    z[k]=next;
    if(cabs(w)<=EPS*cabs(z[k]))done[k]=true;
   }
   if(!active){converged=true;break;}
  }
  /* Polishing: up to three Newton steps per root, accepted only when the backward error does not grow. */
  for(let k=0;k<n;k++){
   for(let s=0;s<3;s++){
    const nr=newtonRatio(a,rev,z[k]);if(!nr.ratio||isZero(nr.ratio))break;
    const cand=csub(z[k],nr.ratio);if(!cand.every(Number.isFinite))break;
    if(newtonRatio(a,rev,cand).berr<=nr.berr)z[k]=cand;else break;
   }
  }
 }
 const all=z.concat(Array.from({length:zeroCount},()=>C(0)));
 const residuals=all.map(r=>backwardError(a0,r));
 /* Multiplicity by single-linkage clustering: |r_i - r_j| ≤ tol · max(1, |r_i|, |r_j|). */
 const parent=all.map((_,i)=>i),find=i=>parent[i]===i?i:(parent[i]=find(parent[i]));
 for(let i=0;i<all.length;i++)for(let j=i+1;j<all.length;j++)
  if(cabs(csub(all[i],all[j]))<=clusterTol*Math.max(1,cabs(all[i]),cabs(all[j])))parent[find(i)]=find(j);
 const groups=new Map();all.forEach((r,i)=>{const g=find(i);if(!groups.has(g))groups.set(g,[]);groups.get(g).push(i);});
 const distinct=[...groups.values()].map(ids=>{
  let centroid=ids.reduce((s,i)=>cadd(s,all[i]),C(0)).map(v=>v/ids.length);
  const spread=Math.max(0,...ids.map(i=>cabs(csub(all[i],centroid))));
  if(ids.length>1){
   /* A root of multiplicity m is a simple root of p^(m-1): refine the centroid by Newton there, staying inside the cluster. */
   let d=a0;for(let k=1;k<ids.length;k++)d=derivRaw(d);
   let x=centroid;
   for(let s=0;s<8&&d.length>1;s++){const h=hornerD(d,x);if(isZero(h.p)||isZero(h.d))break;const nx=csub(x,cdiv(h.p,h.d));if(!nx.every(Number.isFinite))break;const moved=cabs(csub(nx,x));x=nx;if(moved<=EPS*Math.max(1,cabs(x)))break;}
   if(cabs(csub(x,centroid))<=2*spread+EPS*Math.max(1,cabs(centroid)))centroid=x;
  }
  return {root:obj(centroid),multiplicity:ids.length,spread,backwardError:backwardError(a0,centroid)};
 }).sort((p,q)=>p.root.re-q.root.re||p.root.im-q.root.im);
 const order=all.map((_,i)=>i).sort((i,j)=>all[i][0]-all[j][0]||all[i][1]-all[j][1]);
 const sorted=order.map(i=>({root:obj(all[i]),backwardError:residuals[i],multiplicity:groups.get(find(i)).length}));
 return {degree:a0.length-1,roots:sorted,distinct,clusterTolerance:clusterTol,iterations,converged,
  cauchyRadius:radius,exactZeroRoots:zeroCount,maxBackwardError:Math.max(0,...residuals),
  method:'Aberth-Ehrlich simultaneous iteration (Cauchy-bound initial circle, Horner Newton correction, Newton polishing)',
  note:'Backward error |p(r)|/Σ|a_i||r|^i. Multiplicities come from clustering with relative tolerance '+clusterTol+
   ' and are numerical estimates: a multiple root of multiplicity m is perturbed by about (backward error)^(1/m).'};
}

/* ---------- Coefficient algebra ---------- */
function derivRaw(a){const n=a.length-1;return n===0?[C(0)]:a.slice(0,n).map((c,i)=>cmul(c,C(n-i)));}
function derivative(coefficients){
 const a=parsePoly(coefficients),n=a.length-1;
 if(n===0)return {coefficients:[obj(C(0))]};
 return {coefficients:a.slice(0,n).map((c,i)=>obj(cmul(c,C(n-i))))};
}
function integral(coefficients,constant=0){
 const a=parsePoly(coefficients),n=a.length-1,k=parseComplex(constant,'Integration constant');
 return {coefficients:a.map((c,i)=>obj(cdiv(c,C(n-i+1)))).concat([obj(k)])};
}
function addRaw(a,b){const n=Math.max(a.length,b.length),out=[];for(let i=0;i<n;i++){const x=a[i-(n-a.length)]||C(0),y=b[i-(n-b.length)]||C(0);out.push(cadd(x,y));}return trimLeading(out);}
function mulRaw(a,b){const out=Array.from({length:a.length+b.length-1},()=>C(0));a.forEach((x,i)=>b.forEach((y,j)=>{out[i+j]=cadd(out[i+j],cmul(x,y));}));return out;}
function divRaw(a,b){
 const r=a.slice(),nb=b.length-1;
 if(a.length<b.length)return {q:[C(0)],r:trimLeading(r)};
 const q=[];
 for(let i=0;i<=a.length-b.length;i++){
  const t=cdiv(r[i],b[0]);q.push(t);r[i]=C(0);
  for(let j=1;j<=nb;j++)r[i+j]=csub(r[i+j],cmul(t,b[j]));
 }
 const rem=nb===0?[C(0)]:trimLeading(r.slice(r.length-nb));
 return {q,r:rem};
}
function checkFinite(list,what){if(!list.every(c=>c.every(Number.isFinite)))throw Error(what+' overflowed the floating-point range.');return list;}
const out=list=>list.map(obj);
function add(p,q){return {coefficients:out(checkFinite(addRaw(parsePoly(p,'First polynomial'),parsePoly(q,'Second polynomial')),'Sum'))};}
function subtract(p,q){return {coefficients:out(checkFinite(addRaw(parsePoly(p,'First polynomial'),parsePoly(q,'Second polynomial').map(c=>C(-c[0],-c[1]))),'Difference'))};}
function multiply(p,q){return {coefficients:out(checkFinite(mulRaw(parsePoly(p,'First polynomial'),parsePoly(q,'Second polynomial')),'Product'))};}
function divide(p,q){
 const a=parsePoly(p,'Dividend'),b=parsePoly(q,'Divisor'),d=divRaw(a,b);
 checkFinite(d.q,'Quotient');checkFinite(d.r,'Remainder');
 return {quotient:out(d.q),remainder:out(d.r)};
}
const normInf=a=>Math.max(...a.map(cabs));
const scaleTo1=a=>{const s=normInf(a);return a.map(c=>[c[0]/s,c[1]/s]);};
const monic=a=>a.map(c=>cdiv(c,a[0]));
/* Numerical Euclid: operands are rescaled to unit max-norm each step and a remainder with max-norm ≤ tol is treated as zero. */
function gcd(p,q,options={}){
 const tol=options.tolerance===undefined||options.tolerance===''?1e-10:Number(options.tolerance);
 if(!Number.isFinite(tol)||tol<=0||tol>=1)throw Error('GCD tolerance must be a number in (0, 1).');
 let A=scaleTo1(parsePoly(p,'First polynomial')),B=scaleTo1(parsePoly(q,'Second polynomial')),steps=0;
 if(A.length<B.length)[A,B]=[B,A];
 while(B.length>1){
  steps++;
  let r=divRaw(A,B).r;
  let i=0;while(i<r.length&&cabs(r[i])<=tol)i++;
  r=r.slice(i);
  if(!r.length)break;
  A=B;B=scaleTo1(r);
 }
 const g=monic(B);
 const pa=parsePoly(p,'First polynomial'),qa=parsePoly(q,'Second polynomial');
 const relRem=x=>{const r=divRaw(x,g).r;return normInf(r)/normInf(x);};
 return {coefficients:out(g),degree:g.length-1,steps,tolerance:tol,
  cofactorResiduals:[relRem(pa),relRem(qa)],
  note:'Numerical GCD (Euclid with relative tolerance '+tol+'); monic result. Ill-conditioned for nearly common roots.'};
}
function fromRoots(list){
 const r=parseList(list,'Roots');
 if(r.length>MAX_DEGREE)throw Error('At most '+MAX_DEGREE+' roots are supported.');
 let a=[C(1)];for(const x of r)a=mulRaw(a,[C(1),C(-x[0],-x[1])]);
 return {coefficients:out(checkFinite(a,'Polynomial'))};
}

/* ---------- Formatting ---------- */
function obj(c){return {re:c[0]===0?0:c[0],im:c[1]===0?0:c[1]};}
function fmtReal(x){if(x===0)return '0';const t=Number(x.toPrecision(12));return Math.abs(t)>=1e12||Math.abs(t)<1e-6?t.toExponential():String(t);}
function formatComplex(c,chop=1e-13){
 let re=c.re,im=c.im;const m=Math.hypot(re,im);
 if(Math.abs(im)<=chop*m)im=0;if(Math.abs(re)<=chop*m)re=0;
 if(im===0)return fmtReal(re);
 const ims=(Math.abs(im)===1?'':fmtReal(Math.abs(im)))+'i';
 if(re===0)return (im<0?'-':'')+ims;
 return fmtReal(re)+(im<0?' - ':' + ')+ims;
}
function formatPolynomial(coefs){
 const n=coefs.length-1,parts=[];
 coefs.forEach((c,i)=>{
  const p=n-i,re=c.re,im=c.im;if(re===0&&im===0)return;
  const xs=p===0?'':p===1?'x':'x^'+p;
  let s,neg=false;
  if(im===0){neg=re<0;const v=Math.abs(re);s=(v===1&&p>0?'':fmtReal(v))+xs;}
  else if(re===0){neg=im<0;const v=Math.abs(im);s=(v===1?'':fmtReal(v))+'i'+(xs?'·'+xs:'');}
  else s='('+formatComplex(c)+')'+xs;
  parts.push({s,neg});
 });
 if(!parts.length)return '0';
 return parts.map((t,i)=>i===0?(t.neg?'-':'')+t.s:(t.neg?' - ':' + ')+t.s).join('');
}
const api=Object.freeze({parseComplex,parseCoefficients:x=>out(parsePoly(x)),roots,evaluate,derivative,integral,
 add,subtract,multiply,divide,gcd,fromRoots,backwardError:(p,r)=>backwardError(parsePoly(p),parseComplex(r,'Root')),
 formatComplex,formatPolynomial,maxDegree:MAX_DEGREE});
M.polynomials=api;

/* ---------- UI ---------- */
const panel=typeof document!=='undefined'&&document.getElementById('calculator-panel');
if(!panel)return;
const $=id=>document.getElementById(id);
const OPS=[['roots','All complex roots (Aberth-Ehrlich)'],['evaluate','Evaluate p(x) and p′(x) (Horner)'],['derivative','Derivative p′'],
 ['integral','Integral ∫p dx (constant 0)'],['add','Add p + q'],['multiply','Multiply p · q'],['divide','Long division p ÷ q'],
 ['gcd','Numerical GCD(p, q)'],['fromRoots','Build polynomial from roots']];
const area=document.createElement('details');area.id='poly-details';
area.innerHTML='<summary>Polynomial tools · roots, Horner, division, GCD · offline</summary>'+
 '<p class="small-note">Coefficients are listed highest degree first and separated by commas; complex values use a+bi (e.g. 1, -3, 2 is x^2 - 3x + 2; 1, 2-i, -2i is (x - i)(x + 2)). '+
 'Maximum degree 30. Floating-point (binary64) results; multiplicities and the GCD are numerical estimates with the stated tolerance.</p>'+
 '<div class="poly-fields"><label for="poly-op">Operation<select id="poly-op"></select></label>'+
 '<label for="poly-p" data-poly-field="p">Polynomial p coefficients<input id="poly-p" type="text" spellcheck="false" autocomplete="off" value="1, -3, 2"></label>'+
 '<label for="poly-q" data-poly-field="q">Polynomial q coefficients<input id="poly-q" type="text" spellcheck="false" autocomplete="off" value="1, -1"></label>'+
 '<label for="poly-x" data-poly-field="x">Point x<input id="poly-x" type="text" spellcheck="false" autocomplete="off" value="2"></label>'+
 '<label for="poly-roots-in" data-poly-field="r">Roots (comma-separated)<input id="poly-roots-in" type="text" spellcheck="false" autocomplete="off" value="1, 2, i, -i"></label>'+
 '<label for="poly-tol" data-poly-field="t">Tolerance (cluster / GCD)<input id="poly-tol" type="text" inputmode="decimal" spellcheck="false" autocomplete="off" value="1e-4"></label></div>'+
 '<div class="data-toolbar"><button id="poly-run" class="primary" type="button">Run</button>'+
 '<button id="poly-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="poly-output" role="status" aria-live="polite">Choose an operation, enter coefficients and press Run or Enter.</pre>';
panel.append(area);
const select=$('poly-op');
for(const [v,t] of OPS){const o=document.createElement('option');o.value=v;o.textContent=t;select.append(o);}
const style=document.createElement('style');style.textContent=
 '#poly-details{margin:16px 22px 22px;padding:14px;border:1px solid #dce4f6;border-radius:12px;background:#fbfcff;min-width:0;max-width:100%;box-sizing:border-box}'+
 '#poly-details summary{cursor:pointer;font-weight:750;color:#3c50ae;min-height:40px;display:flex;align-items:center}'+
 '.poly-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:12px 0}'+
 '.poly-fields label{display:flex;flex-direction:column;gap:5px;font-size:12px;color:#566784;font-weight:700;min-width:0}'+
 '.poly-fields label[hidden]{display:none}'+
 '.poly-fields input,.poly-fields select{min-width:0;width:100%;box-sizing:border-box;min-height:40px;border:1px solid #cdd8ec;border-radius:8px;padding:9px;background:white;font:inherit}'+
 '#poly-run,#poly-to-table{min-height:40px;min-width:40px}'+
 '#poly-output{white-space:pre-wrap;overflow-wrap:anywhere;background:white;border:1px solid #dce5f3;border-radius:9px;padding:12px;max-height:320px;overflow:auto}'+
 '#poly-output.error{color:#a82241;background:#fff2f4}'+
 '@media(max-width:600px){.poly-fields{grid-template-columns:1fr}#poly-details{margin:12px}}';
document.head.append(style);
const FIELDS={roots:['p','t'],evaluate:['p','x'],derivative:['p'],integral:['p'],add:['p','q'],multiply:['p','q'],divide:['p','q'],gcd:['p','q','t'],fromRoots:['r']};
const output=$('poly-output'),saveBtn=$('poly-to-table');let last=null;
function syncFields(){
 const show=FIELDS[select.value]||[];
 for(const label of area.querySelectorAll('[data-poly-field]'))label.hidden=!show.includes(label.dataset.polyField);
 const tol=$('poly-tol');
 if(select.value==='gcd'&&tol.value==='1e-4')tol.value='1e-10';
 if(select.value==='roots'&&tol.value==='1e-10')tol.value='1e-4';
}
const fc=formatComplex,cols=c=>[String(c.re),String(c.im)];
function coefTable(name,coefs){const n=coefs.length-1;return {name,headers:['power','re','im'],rows:coefs.map((c,i)=>[String(n-i),...cols(c)])};}
function run(){
 const op=select.value,p=$('poly-p').value,q=$('poly-q').value;
 try{
  let text,table;
  if(op==='roots'){
   const r=roots(p,{clusterTolerance:$('poly-tol').value.trim()});
   const lines=['p(x) = '+formatPolynomial(parsePoly(p).map(obj)),'Degree '+r.degree+' · '+r.roots.length+' roots · '+r.iterations+' Aberth iterations · '+(r.converged?'converged':'NOT converged; results are unreliable'),
    'Distinct roots (cluster tolerance '+r.clusterTolerance+'):'];
   r.distinct.forEach((d,i)=>lines.push('  r'+(i+1)+' = '+fc(d.root)+(d.multiplicity>1?'   multiplicity '+d.multiplicity+' (spread '+d.spread.toExponential(1)+')':'')+'   backward error '+d.backwardError.toExponential(2)));
   lines.push('Max individual backward error: '+r.maxBackwardError.toExponential(2),r.note);
   text=lines.join('\n');
   table={name:'Polynomial_Roots',headers:['k','re','im','backward_error','cluster_multiplicity'],rows:r.roots.map((x,i)=>[String(i+1),...cols(x.root),String(x.backwardError),String(x.multiplicity)])};
  }else if(op==='evaluate'){
   const r=evaluate(p,$('poly-x').value);
   text='p('+fc(r.point)+') = '+fc(r.value)+'\np′('+fc(r.point)+') = '+fc(r.derivative)+'\nRelative rounding-error bound ≈ '+r.relativeErrorBound.toExponential(2)+' (Horner)';
   table={name:'Polynomial_Evaluation',headers:['x_re','x_im','p_re','p_im','dp_re','dp_im'],rows:[[...cols(r.point),...cols(r.value),...cols(r.derivative)]]};
  }else if(op==='divide'){
   const r=divide(p,q);
   text='Quotient: '+formatPolynomial(r.quotient)+'\nRemainder: '+formatPolynomial(r.remainder)+'\nQuotient coefficients: '+r.quotient.map(fc).join(', ')+'\nRemainder coefficients: '+r.remainder.map(fc).join(', ');
   const nq=r.quotient.length-1,nr=r.remainder.length-1;
   table={name:'Polynomial_Division',headers:['part','power','re','im'],rows:r.quotient.map((c,i)=>['quotient',String(nq-i),...cols(c)]).concat(r.remainder.map((c,i)=>['remainder',String(nr-i),...cols(c)]))};
  }else{
   const r=op==='derivative'?derivative(p):op==='integral'?integral(p):op==='add'?add(p,q):op==='multiply'?multiply(p,q):op==='gcd'?gcd(p,q,{tolerance:$('poly-tol').value.trim()}):fromRoots($('poly-roots-in').value);
   const label={derivative:'p′(x)',integral:'∫p dx',add:'p + q',multiply:'p · q',gcd:'gcd(p, q)',fromRoots:'p(x)'}[op];
   text=label+' = '+formatPolynomial(r.coefficients)+'\nCoefficients: '+r.coefficients.map(fc).join(', ');
   if(op==='gcd')text+='\nDegree '+r.degree+' · '+r.steps+' Euclid steps · cofactor remainders '+r.cofactorResiduals.map(v=>v.toExponential(1)).join(', ')+'\n'+r.note;
   table=coefTable('Polynomial_'+op[0].toUpperCase()+op.slice(1),r.coefficients);
  }
  output.classList.remove('error');output.textContent=text;last=table;saveBtn.disabled=false;
 }catch(e){last=null;saveBtn.disabled=true;output.classList.add('error');output.textContent=e.message+'\nCorrect the input and press Run again.';}
}
function invalidate(){last=null;saveBtn.disabled=true;output.classList.remove('error');output.textContent='Inputs changed. Press Run or Enter.';}
select.addEventListener('change',()=>{syncFields();invalidate();});
$('poly-run').addEventListener('click',run);
for(const input of area.querySelectorAll('input')){
 input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run();}});
 input.addEventListener('input',invalidate);
}
saveBtn.addEventListener('click',()=>{
 try{if(!last)throw Error('Run an operation first.');M.dataTables.importData({headers:last.headers,rows:last.rows},last.name);output.textContent+='\nSaved to Data Tables as '+last.name+'.';}
 catch(e){output.classList.add('error');output.textContent=e.message;}
});
syncFields();
})();
