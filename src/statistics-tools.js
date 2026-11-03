/* Offline probability distributions, special functions and descriptive statistics (no dependencies). */
(()=>{'use strict';
const M=window.MathStudio=window.MathStudio||{};
const EPS=1e-16,FPMIN=1e-300,MAX_ITER=100000,LN_SQRT_2PI=0.9189385332046728,SQRT2=Math.SQRT2;
const LANCZOS=[0.99999999999980993,676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-0.13857109526572012,9.9843695780195716e-6,1.5056327351493116e-7];

/* ---------- special functions ---------- */
function logGamma(x){
 if(!Number.isFinite(x))throw Error('logGamma requires a finite argument.');
 if(x<=0&&Number.isInteger(x))return Infinity;
 if(x<0.5)return Math.log(Math.PI/Math.abs(Math.sin(Math.PI*x)))-logGamma(1-x);
 x-=1;let a=LANCZOS[0];const t=x+7.5;
 for(let i=1;i<9;i++)a+=LANCZOS[i]/(x+i);
 return LN_SQRT_2PI+(x+0.5)*Math.log(t)-t+Math.log(a);
}
function gammaArgs(a,x){if(!(a>0)||!Number.isFinite(a))throw Error('Incomplete gamma shape must be positive and finite.');if(!(x>=0))throw Error('Incomplete gamma argument must be non-negative.');}
function gammaSeries(a,x){
 let ap=a,del=1/a,sum=del;
 for(let i=0;i<MAX_ITER;i++){ap+=1;del*=x/ap;sum+=del;if(Math.abs(del)<Math.abs(sum)*EPS)return sum*Math.exp(-x+a*Math.log(x)-logGamma(a));}
 throw Error('Incomplete gamma series did not converge.');
}
function gammaFraction(a,x){
 let b=x+1-a,c=1/FPMIN,d=1/b,h=d;
 for(let i=1;i<=MAX_ITER;i++){
  const an=-i*(i-a);b+=2;d=an*d+b;if(Math.abs(d)<FPMIN)d=FPMIN;c=b+an/c;if(Math.abs(c)<FPMIN)c=FPMIN;d=1/d;const del=d*c;h*=del;
  if(Math.abs(del-1)<EPS)return Math.exp(-x+a*Math.log(x)-logGamma(a))*h;
 }
 throw Error('Incomplete gamma continued fraction did not converge.');
}
/** Regularized lower incomplete gamma P(a,x). */
function gammaP(a,x){gammaArgs(a,x);if(x===0)return 0;if(x===Infinity)return 1;return x<a+1?gammaSeries(a,x):1-gammaFraction(a,x);}
/** Regularized upper incomplete gamma Q(a,x)=1-P(a,x), computed without cancellation in the tail. */
function gammaQ(a,x){gammaArgs(a,x);if(x===0)return 1;if(x===Infinity)return 0;return x<a+1?1-gammaSeries(a,x):gammaFraction(a,x);}
function betaFraction(a,b,x){
 const qab=a+b,qap=a+1,qam=a-1;let c=1,d=1-qab*x/qap;if(Math.abs(d)<FPMIN)d=FPMIN;d=1/d;let h=d;
 for(let m=1;m<=MAX_ITER;m++){
  const m2=2*m;let aa=m*(b-m)*x/((qam+m2)*(a+m2));
  d=1+aa*d;if(Math.abs(d)<FPMIN)d=FPMIN;c=1+aa/c;if(Math.abs(c)<FPMIN)c=FPMIN;d=1/d;h*=d*c;
  aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2));
  d=1+aa*d;if(Math.abs(d)<FPMIN)d=FPMIN;c=1+aa/c;if(Math.abs(c)<FPMIN)c=FPMIN;d=1/d;const del=d*c;h*=del;
  if(Math.abs(del-1)<EPS)return h;
 }
 throw Error('Incomplete beta continued fraction did not converge.');
}
/** Regularized incomplete beta I_x(a,b); optional y=1-x supplied exactly to avoid cancellation. */
function betaI(a,b,x,y=1-x){
 if(!(a>0)||!(b>0)||!Number.isFinite(a)||!Number.isFinite(b))throw Error('Incomplete beta parameters must be positive and finite.');
 if(!(x>=0&&x<=1))throw Error('Incomplete beta argument must be in [0, 1].');
 if(x===0)return 0;if(y<=0)return 1;
 const bt=Math.exp(logGamma(a+b)-logGamma(a)-logGamma(b)+a*Math.log(x)+b*Math.log(y));
 return x<(a+1)/(a+b+2)?bt*betaFraction(a,b,x)/a:1-bt*betaFraction(b,a,y,x)/b;
}
function erf(x){if(Number.isNaN(x))return NaN;if(x===0)return x;const s=x<0?-1:1,z=x*x;return s*(z<1.5?gammaP(0.5,z):1-gammaQ(0.5,z));}
function erfc(x){if(Number.isNaN(x))return NaN;if(x<0)return 2-erfc(-x);const z=x*x;return z<1.5?1-gammaP(0.5,z):gammaQ(0.5,z);}

/* ---------- validation ---------- */
function num(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');const n=Number(value);if(!Number.isFinite(n))throw Error(name+' must be a finite number.');return n;}
function positive(value,name){const n=num(value,name);if(!(n>0))throw Error(name+' must be greater than 0.');if(n>1e12)throw Error(name+' must be at most 1e12.');return n;}
function probability(value,name='Probability p'){const n=num(value,name);if(n<0||n>1)throw Error(name+' must be in [0, 1].');return n;}
function count(value,name,max){const n=num(value,name);if(!Number.isInteger(n)||n<0||n>max)throw Error(name+' must be an integer from 0 to '+max+'.');return n;}

/* ---------- quantile solvers ---------- */
function continuousQuantile(d,p,lo,hi,lower,upper){
 p=probability(p);if(p===0)return lower;if(p===1)return upper;
 const up=p<=0.5,q=1-p,F=x=>up?d.cdf(x)-p:q-d.sf(x);
 let guard=0;
 while(F(lo)>0){if(++guard>2000)throw Error('Quantile bracket expansion failed.');const w=hi-lo;hi=lo;lo=Math.max(lower,lo-2*w);if(lo===lower&&F(lo)>0)break;}
 while(F(hi)<0){if(++guard>4000)throw Error('Quantile bracket expansion failed.');const w=hi-lo;lo=hi;hi=hi+2*w;if(!Number.isFinite(hi))throw Error('Quantile is outside the finite range.');}
 for(let i=0;i<3000;i++){
  const mid=lo+(hi-lo)/2;if(mid===lo||mid===hi)return mid;
  const v=F(mid);if(v===0)return mid;if(v<0)lo=mid;else hi=mid;
 }
 return lo+(hi-lo)/2;
}
/** Smallest integer k in [lo, ∞) with CDF(k) ≥ p, using a tiny relative tolerance for CDF rounding. */
function discreteQuantile(d,p,max){
 p=probability(p);if(p===0)return 0;if(p===1)return max;
 const target=p*(1-64*Number.EPSILON),ok=k=>d.cdf(k)>=target;
 let lo=-1,hi=Math.max(1,Math.ceil(d.mean||1));
 while(!ok(hi)){lo=hi;hi*=2;if(hi>=max){hi=max;break;}}
 while(hi-lo>1){const mid=Math.floor((lo+hi)/2);if(ok(mid))hi=mid;else lo=mid;}
 return hi;
}

/* ---------- distributions ---------- */
const normalStd={pdf:z=>Math.exp(-0.5*z*z-LN_SQRT_2PI),cdf:z=>0.5*erfc(-z/SQRT2),sf:z=>0.5*erfc(z/SQRT2)};
const builders={
 normal({mu=0,sigma=1}={}){
  mu=num(mu,'Mean μ');if(Math.abs(mu)>1e12)throw Error('Mean μ must be at most 1e12 in magnitude.');sigma=positive(sigma,'Standard deviation σ');
  const z=x=>(num(x,'x')-mu)/sigma;
  const d={name:'Normal',label:'Normal(μ='+mu+', σ='+sigma+')',discrete:false,params:{mu,sigma},mean:mu,variance:sigma*sigma,
   pdf:x=>normalStd.pdf(z(x))/sigma,cdf:x=>normalStd.cdf(z(x)),sf:x=>normalStd.sf(z(x))};
  d.quantile=p=>{const s=continuousQuantile(normalStd,p,-1,1,-Infinity,Infinity);return Number.isFinite(s)?mu+sigma*s:s;};
  return d;
 },
 t({nu=1}={}){
  nu=positive(nu,'Degrees of freedom ν');
  const tail=t=>{const t2=t*t;return 0.5*betaI(nu/2,0.5,nu/(nu+t2),t2/(nu+t2));};
  const cdf=x=>{x=num(x,'x');if(x===0)return 0.5;const v=tail(x);return x>0?1-v:v;};
  const sf=x=>{x=num(x,'x');if(x===0)return 0.5;const v=tail(x);return x>0?v:1-v;};
  const lc=logGamma((nu+1)/2)-logGamma(nu/2)-0.5*Math.log(nu*Math.PI);
  const d={name:'Student t',label:'Student t(ν='+nu+')',discrete:false,params:{nu},mean:nu>1?0:null,variance:nu>2?nu/(nu-2):nu>1?Infinity:null,
   pdf:x=>{x=num(x,'x');return Math.exp(lc-(nu+1)/2*Math.log1p(x*x/nu));},cdf,sf};
  d.quantile=p=>continuousQuantile(d,p,-1,1,-Infinity,Infinity);
  return d;
 },
 chisquare({k=1}={}){
  k=positive(k,'Degrees of freedom k');const h=k/2,lc=-h*Math.LN2-logGamma(h);
  const d={name:'Chi-square',label:'Chi-square(k='+k+')',discrete:false,params:{k},mean:k,variance:2*k,
   pdf:x=>{x=num(x,'x');if(x<0)return 0;if(x===0)return k<2?Infinity:k===2?0.5:0;return Math.exp(lc+(h-1)*Math.log(x)-x/2);},
   cdf:x=>{x=num(x,'x');return x<=0?0:gammaP(h,x/2);},sf:x=>{x=num(x,'x');return x<=0?1:gammaQ(h,x/2);}};
  d.quantile=p=>continuousQuantile(d,p,0,Math.max(1,k),0,Infinity);
  return d;
 },
 exponential({lambda=1}={}){
  lambda=positive(lambda,'Rate λ');
  return {name:'Exponential',label:'Exponential(λ='+lambda+')',discrete:false,params:{lambda},mean:1/lambda,variance:1/(lambda*lambda),
   pdf:x=>{x=num(x,'x');return x<0?0:lambda*Math.exp(-lambda*x);},cdf:x=>{x=num(x,'x');return x<=0?0:-Math.expm1(-lambda*x);},
   sf:x=>{x=num(x,'x');return x<=0?1:Math.exp(-lambda*x);},quantile:p=>{p=probability(p);return p===1?Infinity:-Math.log1p(-p)/lambda;}};
 },
 binomial({n=10,p=0.5}={}){
  n=count(n,'Trials n',1e7);p=probability(p,'Success probability p');
  const lnC=k=>logGamma(n+1)-logGamma(k+1)-logGamma(n-k+1);
  const pmf=x=>{x=num(x,'k');if(!Number.isInteger(x)||x<0||x>n)return 0;if(p===0)return x===0?1:0;if(p===1)return x===n?1:0;return Math.exp(lnC(x)+x*Math.log(p)+(n-x)*Math.log1p(-p));};
  const cdf=x=>{x=Math.floor(num(x,'k'));if(x<0)return 0;if(x>=n)return 1;if(p===0)return 1;if(p===1)return 0;return betaI(n-x,x+1,1-p,p);};
  const d={name:'Binomial',label:'Binomial(n='+n+', p='+p+')',discrete:true,params:{n,p},mean:n*p,variance:n*p*(1-p),pdf:pmf,cdf,sf:x=>1-cdf(x)};
  d.quantile=q=>discreteQuantile(d,q,n);
  return d;
 },
 poisson({lambda=1}={}){
  lambda=positive(lambda,'Rate λ');if(lambda>1e7)throw Error('Rate λ must be at most 1e7.');
  const pmf=x=>{x=num(x,'k');if(!Number.isInteger(x)||x<0)return 0;return Math.exp(x*Math.log(lambda)-lambda-logGamma(x+1));};
  const cdf=x=>{x=Math.floor(num(x,'k'));return x<0?0:gammaQ(x+1,lambda);};
  const sf=x=>{x=Math.floor(num(x,'k'));return x<0?1:gammaP(x+1,lambda);};
  const d={name:'Poisson',label:'Poisson(λ='+lambda+')',discrete:true,params:{lambda},mean:lambda,variance:lambda,pdf:pmf,cdf,sf};
  d.quantile=q=>discreteQuantile(d,q,Infinity);
  return d;
 }
};
function distribution(name,params){const b=builders[String(name||'').toLowerCase()];if(!b)throw Error('Unknown distribution: '+name+'. Choose normal, t, chisquare, exponential, binomial or poisson.');return b(params||{});}
function evaluate({dist='normal',params={},x='',p=''}={}){
 const d=distribution(dist,params),hasX=String(x??'').trim()!=='',hasP=String(p??'').trim()!=='';
 if(!hasX&&!hasP)throw Error('Enter a value x (or k) and/or a probability p.');
 const out={type:'distribution',name:d.name,label:d.label,discrete:d.discrete,params:d.params,mean:d.mean,variance:d.variance};
 if(hasX){out.x=num(x,d.discrete?'k':'x');out.density=d.pdf(out.x);out.cdf=d.cdf(out.x);out.sf=d.sf(out.x);}
 if(hasP){out.p=probability(p);out.quantile=d.quantile(out.p);}
 return out;
}

/* ---------- descriptive statistics ---------- */
function toNumber(cell){if(typeof cell==='number')return Number.isFinite(cell)?cell:null;const s=String(cell??'').trim();if(!s)return null;const n=Number(s);return Number.isFinite(n)?n:null;}
function quantile7(sorted,q){const h=(sorted.length-1)*q,lo=Math.floor(h),hi=Math.min(lo+1,sorted.length-1);return sorted[lo]+(h-lo)*(sorted[hi]-sorted[lo]);}
function meanOf(v){let s=0;for(const x of v)s+=x;let m=s/v.length,c=0;for(const x of v)c+=x-m;return m+c/v.length;}
function describe(values){
 const v=Array.from(values||[],x=>{if(typeof x!=='number'||!Number.isFinite(x))throw Error('Descriptive statistics need finite numbers.');return x;});
 const n=v.length;if(!n)throw Error('Column has no numeric values.');
 const sorted=[...v].sort((a,b)=>a-b),mean=meanOf(v);let m2=0,m3=0;for(const x of v){const d=x-mean;m2+=d*d;m3+=d*d*d;}
 const popVar=m2/n,sampleVar=n>1?m2/(n-1):null,q1=quantile7(sorted,0.25),q3=quantile7(sorted,0.75);
 let skewness=null;if(n>=3&&m2>0){const g1=(m3/n)/Math.pow(m2/n,1.5);skewness=g1*Math.sqrt(n*(n-1))/(n-2);}
 return {n,mean,median:quantile7(sorted,0.5),sampleVariance:sampleVar,populationVariance:popVar,sampleStd:sampleVar===null?null:Math.sqrt(sampleVar),populationStd:Math.sqrt(popVar),min:sorted[0],max:sorted[n-1],q1,q3,iqr:q3-q1,skewness};
}
function correlate(xs,ys){
 if(xs.length!==ys.length)throw Error('Paired samples must have equal length.');const n=xs.length;if(n<2)throw Error('Correlation needs at least two complete numeric pairs.');
 const mx=meanOf(xs),my=meanOf(ys);let sxy=0,sxx=0,syy=0;for(let i=0;i<n;i++){const dx=xs[i]-mx,dy=ys[i]-my;sxy+=dx*dy;sxx+=dx*dx;syy+=dy*dy;}
 return {pairs:n,covariance:sxy/(n-1),populationCovariance:sxy/n,pearson:sxx>0&&syy>0?Math.max(-1,Math.min(1,sxy/Math.sqrt(sxx*syy))):null};
}
function columnValues(cells){let blank=0,nonNumeric=0;const values=[];for(const cell of cells){const n=toNumber(cell);if(n!==null)values.push(n);else if(String(cell??'').trim()==='')blank++;else nonNumeric++;}return {values,blank,nonNumeric};}
function describeColumns(rows,c1,c2=null){
 if(!Array.isArray(rows))throw Error('Rows must be an array.');
 const first=columnValues(rows.map(r=>r?.[c1])),out={type:'descriptive',first:{...describe(first.values),blank:first.blank,nonNumeric:first.nonNumeric}};
 if(c2!==null&&c2!==undefined&&c2!==''){
  const second=columnValues(rows.map(r=>r?.[c2]));out.second={...describe(second.values),blank:second.blank,nonNumeric:second.nonNumeric};
  const xs=[],ys=[];for(const r of rows){const a=toNumber(r?.[c1]),b=toNumber(r?.[c2]);if(a!==null&&b!==null){xs.push(a);ys.push(b);}}
  out.pair=correlate(xs,ys);
 }
 return out;
}
function describeTable({table,column,column2=null}={}){
 const T=M.dataTables;if(!T)throw Error('Data Tables are unavailable.');
 const t=T.tables.find(s=>s.name===table||s.id===table);if(!t)throw Error('Choose an existing data table.');
 const idx=name=>{if(name===null||name===undefined||name==='')return null;const i=t.columns.indexOf(String(name));if(i<0)throw Error('Unknown column: '+name+'.');return i;};
 const c1=idx(column);if(c1===null)throw Error('Choose a column.');const c2=idx(column2);if(c2!==null&&c2===c1)throw Error('Choose two different columns.');
 const rows=typeof T.calculate==='function'?T.calculate(t):t.rows;
 const out=describeColumns(rows,c1,c2);out.table=t.name;out.column=t.columns[c1];out.column2=c2===null?null:t.columns[c2];return out;
}

M.statistics={logGamma,gammaP,gammaQ,betaI,erf,erfc,distribution,evaluate,describe,correlate,describeColumns,describeTable,quantile7};

/* ---------- UI ---------- */
const panel=document.getElementById('numerical-panel');if(!panel)return;
const $=id=>document.getElementById(id);
const fmt=v=>v===null||v===undefined?'undefined':typeof v==='number'?(Number.isFinite(v)?(Number.isInteger(v)&&Math.abs(v)<1e15?String(v):Number(v.toPrecision(12)).toString()):String(v)):String(v);
const PARAMS={normal:[['mu','Mean μ','0'],['sigma','Standard deviation σ','1']],t:[['nu','Degrees of freedom ν','10']],chisquare:[['k','Degrees of freedom k','2']],exponential:[['lambda','Rate λ','1']],binomial:[['n','Trials n','10'],['p','Success probability p','0.3']],poisson:[['lambda','Rate λ','4']]};
const area=document.createElement('details');area.id='stats-details';
area.innerHTML='<summary>Statistics · distributions and descriptive statistics</summary>'+
 '<p>Density/mass, CDF, survival and quantile for common distributions; summary statistics for Data Tables columns.</p>'+
 '<div class="num-fields"><label>Distribution<select id="stats-dist"><option value="normal">Normal</option><option value="t">Student t</option><option value="chisquare">Chi-square</option><option value="exponential">Exponential</option><option value="binomial">Binomial</option><option value="poisson">Poisson</option></select></label>'+
 '<label id="stats-param1-label"><span id="stats-param1-name">Mean μ</span><input id="stats-param1" type="number" step="any" value="0"></label>'+
 '<label id="stats-param2-label"><span id="stats-param2-name">Standard deviation σ</span><input id="stats-param2" type="number" step="any" value="1"></label>'+
 '<label><span id="stats-x-name">Value x</span><input id="stats-x" type="number" step="any" value="1.96"></label>'+
 '<label>Probability p (quantile)<input id="stats-p" type="number" step="any" min="0" max="1" value="0.975"></label></div>'+
 '<div class="data-toolbar"><button id="stats-dist-run" class="primary" type="button">Evaluate distribution</button></div>'+
 '<div class="num-fields"><label>Data table<select id="stats-table"></select></label>'+
 '<label>Column<select id="stats-column"></select></label>'+
 '<label>Second column (optional)<select id="stats-column2"></select></label></div>'+
 '<div class="data-toolbar"><button id="stats-desc-run" class="primary" type="button">Describe column</button>'+
 '<button id="stats-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="stats-output" role="status" aria-live="polite" style="white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%">Choose a distribution or a data column.</pre>';
panel.append(area);let last=null;
const output=$('stats-output');
const invalidate=()=>{last=null;$('stats-to-table').disabled=true;output.classList.remove('error');};
const option=(select,value,text)=>{const o=document.createElement('option');o.value=value;o.textContent=text;select.append(o);};
function syncParams(){
 const spec=PARAMS[$('stats-dist').value];
 for(const i of [1,2]){const s=spec[i-1],label=$('stats-param'+i+'-label');label.hidden=!s;if(s){$('stats-param'+i+'-name').textContent=s[1];$('stats-param'+i).value=s[2];}}
 const discrete=$('stats-dist').value==='binomial'||$('stats-dist').value==='poisson';
 $('stats-x-name').textContent=discrete?'Count k':'Value x';$('stats-x').value=discrete?'3':'1.96';
}
function syncTables(){
 const T=M.dataTables,tableSel=$('stats-table');if(!T)return;
 const keep=tableSel.value;tableSel.replaceChildren();for(const t of T.tables)option(tableSel,t.name,t.name);
 if([...tableSel.options].some(o=>o.value===keep))tableSel.value=keep;syncColumns();
}
function syncColumns(){
 const T=M.dataTables,t=T?.tables.find(s=>s.name===$('stats-table').value),c1=$('stats-column'),c2=$('stats-column2'),k1=c1.value,k2=c2.value;
 c1.replaceChildren();c2.replaceChildren();option(c2,'','(none)');
 for(const name of t?.columns||[]){option(c1,name,name);option(c2,name,name);}
 if([...c1.options].some(o=>o.value===k1))c1.value=k1;if([...c2.options].some(o=>o.value===k2))c2.value=k2;
}
$('stats-dist').addEventListener('change',()=>{syncParams();invalidate();});
$('stats-table').addEventListener('change',()=>{syncColumns();invalidate();});
area.addEventListener('toggle',()=>{if(area.open)syncTables();});
for(const id of ['stats-table','stats-column','stats-column2'])$(id).addEventListener('focus',()=>{if(id==='stats-table')syncTables();else syncColumns();});
for(const el of area.querySelectorAll('input,select')){el.addEventListener('input',invalidate);el.addEventListener('change',invalidate);}
const fail=err=>{invalidate();output.classList.add('error');output.textContent=err.message;};
$('stats-dist-run').addEventListener('click',()=>{
 try{
  const dist=$('stats-dist').value,spec=PARAMS[dist],params={};spec.forEach((s,i)=>{params[s[0]]=$('stats-param'+(i+1)).value;});
  const r=evaluate({dist,params,x:$('stats-x').value,p:$('stats-p').value}),lines=[r.label,'Mean = '+fmt(r.mean)+'; variance = '+fmt(r.variance)];
  const rows=[['distribution',r.label],['mean',fmt(r.mean)],['variance',fmt(r.variance)]];
  if('x' in r){const k=r.discrete?'k':'x',f=r.discrete?'P(X = '+r.x+')':'pdf('+r.x+')';lines.push(f+' = '+fmt(r.density),'P(X ≤ '+r.x+') = '+fmt(r.cdf),'P(X > '+r.x+') = '+fmt(r.sf));rows.push([k,r.x],[r.discrete?'pmf':'pdf',r.density],['cdf',r.cdf],['sf',r.sf]);}
  if('p' in r){lines.push((r.discrete?'Quantile (smallest k with CDF ≥ p)':'Quantile F⁻¹(p)')+' at p = '+r.p+': '+fmt(r.quantile));rows.push(['p',r.p],['quantile',fmt(r.quantile)]);}
  last={headers:['quantity','value'],rows,name:'Statistics_Distribution'};output.classList.remove('error');output.textContent=lines.join('\n');$('stats-to-table').disabled=false;
 }catch(err){fail(err);}
});
$('stats-desc-run').addEventListener('click',()=>{
 try{
  const r=describeTable({table:$('stats-table').value,column:$('stats-column').value,column2:$('stats-column2').value||null});
  const keys=[['n','n'],['mean','Mean'],['median','Median'],['sampleVariance','Sample variance'],['populationVariance','Population variance'],['sampleStd','Sample std'],['populationStd','Population std'],['min','Min'],['max','Max'],['q1','Q1 (type 7)'],['q3','Q3 (type 7)'],['iqr','IQR'],['skewness','Skewness (adjusted)'],['blank','Blank cells ignored'],['nonNumeric','Non-numeric cells ignored']];
  const cols=[r.first].concat(r.second?[r.second]:[]),names=[r.column].concat(r.second?[r.column2]:[]);
  const lines=['Table '+r.table+' · '+names.join(' vs ')];
  for(const [k,label] of keys)lines.push(label+': '+cols.map(c=>fmt(c[k])).join(' | '));
  const rows=keys.map(([k,label])=>[label].concat(cols.map(c=>c[k]===null?'':c[k])));
  if(r.pair){lines.push('Complete pairs: '+r.pair.pairs,'Sample covariance: '+fmt(r.pair.covariance),'Pearson r: '+fmt(r.pair.pearson)+(r.pair.pearson===null?' (zero variance)':''));rows.push(['Complete pairs',r.pair.pairs,''],['Sample covariance',r.pair.covariance,''],['Pearson r',r.pair.pearson===null?'':r.pair.pearson,'']);}
  last={headers:['statistic'].concat(names),rows,name:'Statistics_Descriptive'};output.classList.remove('error');output.textContent=lines.join('\n');$('stats-to-table').disabled=false;
 }catch(err){fail(err);}
});
$('stats-to-table').addEventListener('click',()=>{try{if(!last)throw Error('Run a statistics calculation first.');M.dataTables.importData({headers:last.headers,rows:last.rows},last.name);if(M.advanced?.mode)M.advanced.mode('data');}catch(err){output.classList.add('error');output.textContent=err.message;}});
syncParams();syncTables();
})();
