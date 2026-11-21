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

/* ---------- hypothesis tests and confidence intervals ---------- */
const ALTERNATIVES=['two-sided','less','greater'];
function alternativeOf(a){a=String(a||'two-sided').toLowerCase();if(!ALTERNATIVES.includes(a))throw Error('Alternative must be two-sided, less or greater.');return a;}
function confidenceOf(c){const v=num(c??0.95,'Confidence level');if(!(v>0&&v<1))throw Error('Confidence level must be strictly between 0 and 1.');return v;}
function sample(values,name,min=2){
 const v=Array.from(values||[],x=>{const n=toNumber(x);if(n===null)throw Error(name+' must contain only finite numbers.');return n;});
 if(v.length<min)throw Error(name+' needs at least '+min+' values.');if(v.length>1e6)throw Error(name+' may contain at most 1,000,000 values.');
 const mean=meanOf(v);let m2=0;for(const x of v){const d=x-mean;m2+=d*d;}return {n:v.length,mean,variance:m2/(v.length-1)};
}
/** p-value of a statistic under a symmetric (t/normal) reference distribution. */
function pValue(d,stat,alt){if(alt==='less')return d.cdf(stat);if(alt==='greater')return d.sf(stat);return Math.min(1,2*d.sf(Math.abs(stat)));}
function symmetricInterval(d,est,se,alt,conf){
 if(alt==='less')return [-Infinity,est+d.quantile(conf)*se];if(alt==='greater')return [est-d.quantile(conf)*se,Infinity];
 const q=d.quantile(1-(1-conf)/2);return [est-q*se,est+q*se];
}
const T_NOTE='Assumes independent observations from (approximately) normal populations; the t procedure is robust to moderate non-normality for larger n but not to outliers or dependence.';
function tResult(test,stat,df,alt,conf,est,se,extra){
 const d=builders.t({nu:df});
 return Object.assign({type:'hypothesis',test,statisticName:'t',statistic:stat,df,pValue:pValue(d,stat,alt),alternative:alt,confidence:conf,estimate:est,standardError:se,ci:symmetricInterval(d,est,se,alt,conf),warnings:[]},extra);
}
function ttestOne(values,{mu=0,alternative,confidence}={}){
 const s=sample(values,'Sample');mu=num(mu,'Hypothesized mean μ0');const alt=alternativeOf(alternative),conf=confidenceOf(confidence);
 if(!(s.variance>0))throw Error('Sample has zero variance; the t statistic is undefined.');
 const sd=Math.sqrt(s.variance),se=sd/Math.sqrt(s.n);
 return tResult('One-sample t-test',(s.mean-mu)/se,s.n-1,alt,conf,s.mean,se,{n:s.n,mu,sampleStd:sd,ciLabel:'Confidence interval for the mean',effectSize:{name:"Cohen's d",value:(s.mean-mu)/sd},assumptions:T_NOTE});
}
function ttestTwo(x,y,{equalVariance=false,mu=0,alternative,confidence}={}){
 const a=sample(x,'Sample 1'),b=sample(y,'Sample 2');mu=num(mu,'Hypothesized difference Δ0');const alt=alternativeOf(alternative),conf=confidenceOf(confidence);
 if(!(a.variance>0)&&!(b.variance>0))throw Error('Both samples have zero variance; the t statistic is undefined.');
 const diff=a.mean-b.mean;let se,df,effect,test,note;
 if(equalVariance){
  df=a.n+b.n-2;const sp2=((a.n-1)*a.variance+(b.n-1)*b.variance)/df;se=Math.sqrt(sp2*(1/a.n+1/b.n));effect={name:"Cohen's d (pooled SD)",value:diff/Math.sqrt(sp2)};test='Pooled-variance two-sample t-test';
  note=T_NOTE+' The pooled test additionally assumes equal population variances; prefer Welch when unsure.';
 }else{
  const va=a.variance/a.n,vb=b.variance/b.n;se=Math.sqrt(va+vb);df=(va+vb)*(va+vb)/(va*va/(a.n-1)+vb*vb/(b.n-1));effect={name:"Cohen's d (average-variance SD)",value:diff/Math.sqrt((a.variance+b.variance)/2)};test='Welch two-sample t-test';
  note=T_NOTE+' The Welch test does not assume equal variances; df is the Welch–Satterthwaite approximation.';
 }
 return tResult(test,(diff-mu)/se,df,alt,conf,diff,se,{n:a.n,n2:b.n,mean1:a.mean,mean2:b.mean,variance1:a.variance,variance2:b.variance,mu,ciLabel:'Confidence interval for mean1 − mean2',effectSize:effect,assumptions:note});
}
function ttestPaired(x,y,{mu=0,alternative,confidence}={}){
 x=Array.from(x||[]);y=Array.from(y||[]);if(x.length!==y.length)throw Error('Paired samples must have equal length.');
 const d=x.map((v,i)=>{const a=toNumber(v),b=toNumber(y[i]);if(a===null||b===null)throw Error('Paired samples must contain only finite numbers.');return a-b;});
 const r=ttestOne(d,{mu,alternative,confidence});
 return Object.assign(r,{test:'Paired t-test',ciLabel:'Confidence interval for the mean difference (sample 1 − sample 2)',effectSize:{name:"Cohen's d_z",value:r.effectSize.value},
  assumptions:'Assumes independent pairs whose differences are (approximately) normal; observations within a pair may be dependent.'});
}
function counts(values,name){
 return Array.from(values||[],x=>{const n=toNumber(x);if(n===null)throw Error(name+' must contain only finite numbers.');if(n<0)throw Error(name+' must not contain negative counts.');return n;});
}
const CHI_NOTE='Assumes independent observations, each counted in exactly one cell; the chi-square approximation needs expected counts ≥ 5 in (nearly) all cells.';
function chisqGof(observed,expected=null,{ddof=0}={}){
 const o=counts(observed,'Observed counts');if(o.length<2)throw Error('Goodness-of-fit needs at least two categories.');if(o.length>1000)throw Error('At most 1,000 categories are supported.');
 const total=o.reduce((s,x)=>s+x,0);if(!(total>0))throw Error('Observed counts must have a positive total.');
 let e;
 if(expected===null||expected===undefined||(Array.isArray(expected)&&!expected.length))e=o.map(()=>total/o.length);
 else{
  const raw=counts(expected,'Expected counts');if(raw.length!==o.length)throw Error('Expected counts must have the same number of categories as observed counts.');
  if(raw.some(x=>x===0))throw Error('Expected counts must be positive; an expected count of 0 makes the statistic undefined.');
  const sum=raw.reduce((s,x)=>s+x,0);e=raw.map(x=>x*total/sum);
 }
 ddof=count(ddof,'ddof',o.length-2);const df=o.length-1-ddof;let stat=0;for(let i=0;i<o.length;i++){const d=o[i]-e[i];stat+=d*d/e[i];}
 const warnings=e.some(x=>x<5)?['Some expected counts are below 5; the chi-square approximation may be unreliable.']:[];
 return {type:'hypothesis',test:'Chi-square goodness-of-fit',statisticName:'χ²',statistic:stat,df,pValue:builders.chisquare({k:df}).sf(stat),alternative:'greater',n:total,categories:o.length,observed:o,expected:e,
  effectSize:{name:"Cohen's w",value:Math.sqrt(stat/total)},ci:null,warnings,assumptions:CHI_NOTE+' Expected values are rescaled proportionally to the observed total (blank = uniform).'};
}
function chisqIndependence(table,{yates=false}={}){
 if(!Array.isArray(table)||table.length<2)throw Error('Contingency table needs at least two rows.');if(table.length>10)throw Error('Contingency table may have at most 10 rows.');
 const rows=table.map((r,i)=>counts(r,'Row '+(i+1))),c=rows[0].length;
 if(c<2)throw Error('Contingency table needs at least two columns.');if(c>10)throw Error('Contingency table may have at most 10 columns.');
 if(rows.some(r=>r.length!==c))throw Error('Every contingency-table row must have the same number of columns.');
 const rs=rows.map(r=>r.reduce((s,x)=>s+x,0)),cs=rows[0].map((_,j)=>rows.reduce((s,r)=>s+r[j],0)),N=rs.reduce((s,x)=>s+x,0);
 if(rs.some(x=>x===0)||cs.some(x=>x===0))throw Error('A row or column total is 0, giving an expected count of 0; remove empty rows/columns.');
 const df=(rows.length-1)*(c-1),correct=!!yates&&df===1,expected=rows.map((_,i)=>cs.map(cj=>rs[i]*cj/N));let stat=0;
 for(let i=0;i<rows.length;i++)for(let j=0;j<c;j++){let d=Math.abs(rows[i][j]-expected[i][j]);if(correct)d-=Math.min(0.5,d);stat+=d*d/expected[i][j];}
 const warnings=expected.some(r=>r.some(x=>x<5))?['Some expected counts are below 5; the chi-square approximation may be unreliable (consider an exact test).']:[];
 return {type:'hypothesis',test:'Chi-square test of independence'+(correct?' (Yates continuity correction)':''),statisticName:'χ²',statistic:stat,df,pValue:builders.chisquare({k:df}).sf(stat),alternative:'greater',n:N,rows:rows.length,columns:c,expected,
  effectSize:{name:"Cramér's V",value:Math.sqrt(stat/(N*Math.min(rows.length-1,c-1)))},ci:null,warnings,assumptions:CHI_NOTE+' Tests independence of the row and column classifications.'};
}
function successes(k,n){n=count(n,'Trials n',1e7);if(n<1)throw Error('Trials n must be at least 1.');k=count(k,'Successes k',1e7);if(k>n)throw Error('Successes k cannot exceed trials n.');return [k,n];}
function nullProportion(p){const v=num(p,'Null proportion p0');if(!(v>0&&v<1))throw Error('Null proportion p0 must be strictly between 0 and 1.');return v;}
/** Wilson score interval; one-sided alternatives give the matching one-sided bound. */
function wilson(k,n,{confidence,alternative}={}){
 [k,n]=successes(k,n);const conf=confidenceOf(confidence),alt=alternativeOf(alternative),N=builders.normal({});
 const z=N.quantile(alt==='two-sided'?1-(1-conf)/2:conf),ph=k/n,z2=z*z,den=1+z2/n,centre=(ph+z2/(2*n))/den,half=z/den*Math.sqrt(ph*(1-ph)/n+z2/(4*n*n));
 const lo=Math.max(0,centre-half),hi=Math.min(1,centre+half);return alt==='less'?[0,hi]:alt==='greater'?[lo,1]:[lo,hi];
}
function propZTest(k,n,{p0=0.5,alternative,confidence}={}){
 [k,n]=successes(k,n);p0=nullProportion(p0);const alt=alternativeOf(alternative),conf=confidenceOf(confidence),ph=k/n,se=Math.sqrt(p0*(1-p0)/n),z=(ph-p0)/se;
 const warnings=n*p0<10||n*(1-p0)<10?['n·p0 or n·(1 − p0) is below 10; the normal approximation may be poor — prefer the exact binomial test.']:[];
 return {type:'hypothesis',test:'One-proportion z-test',statisticName:'z',statistic:z,df:null,pValue:pValue(builders.normal({}),z,alt),alternative:alt,confidence:conf,estimate:ph,k,n,p0,standardError:se,
  ci:wilson(k,n,{confidence:conf,alternative:alt}),ciLabel:'Wilson score interval for p',effectSize:{name:"Cohen's h",value:2*Math.asin(Math.sqrt(ph))-2*Math.asin(Math.sqrt(p0))},warnings,
  assumptions:'Assumes n independent Bernoulli trials with constant success probability; the z statistic uses the null standard error and a normal approximation.'};
}
function bisect(f,lo,hi){for(let i=0;i<200;i++){const mid=(lo+hi)/2;if(mid===lo||mid===hi)break;if(f(mid))hi=mid;else lo=mid;}return (lo+hi)/2;}
/** Clopper–Pearson exact interval by bisection on regularized incomplete beta tail probabilities. */
function clopperPearson(k,n,conf=0.95,alt='two-sided'){
 [k,n]=successes(k,n);conf=confidenceOf(conf);alt=alternativeOf(alt);const a=alt==='two-sided'?(1-conf)/2:1-conf;
 const lower=k===0?0:bisect(p=>betaI(k,n-k+1,p,1-p)>=a,0,1),upper=k===n?1:bisect(p=>betaI(n-k,k+1,1-p,p)<=a,0,1);
 return alt==='less'?[0,upper]:alt==='greater'?[lower,1]:[lower,upper];
}
function binomTest(k,n,{p=0.5,alternative,confidence}={}){
 [k,n]=successes(k,n);if(n>1e6)throw Error('Exact binomial test supports at most 1,000,000 trials.');
 const p0=nullProportion(p),alt=alternativeOf(alternative),conf=confidenceOf(confidence),B=builders.binomial({n,p:p0});
 const upperTail=x=>x<0?1:x>=n?0:betaI(x+1,n-x,p0,1-p0);let pv;
 if(alt==='less')pv=B.cdf(k);else if(alt==='greater')pv=upperTail(k-1);
 else{
  const d=B.pdf(k)*(1+1e-7),mode=n*p0;
  if(k===mode)pv=1;
  else if(k<mode){let lo=Math.ceil(mode),hi=n+1;while(lo<hi){const m=Math.floor((lo+hi)/2);if(B.pdf(m)<=d)hi=m;else lo=m+1;}pv=B.cdf(k)+upperTail(lo-1);}
  else{/* pmf is non-decreasing on 0..floor(np): y = count of those outcomes with pmf ≤ d. */
   let y=0,hi=Math.floor(mode)+1;while(y<hi){const m=Math.floor((y+hi)/2);if(B.pdf(m)<=d)y=m+1;else hi=m;}
   pv=(y>0?B.cdf(y-1):0)+upperTail(k-1);}
  pv=Math.min(1,pv);
 }
 return {type:'hypothesis',test:'Exact binomial test',statisticName:'k',statistic:k,df:null,pValue:pv,alternative:alt,confidence:conf,estimate:k/n,k,n,p0,ci:clopperPearson(k,n,conf,alt),ciLabel:'Clopper–Pearson exact interval for p',
  effectSize:{name:"Cohen's h",value:2*Math.asin(Math.sqrt(k/n))-2*Math.asin(Math.sqrt(p0))},warnings:[],
  assumptions:'Assumes n independent Bernoulli trials with constant success probability. The two-sided p sums all outcomes no more likely than k (relative tolerance 1 + 1e-7); the Clopper–Pearson interval is conservative.'};
}
function varianceTest(values,{sigma2=null,alternative,confidence}={}){
 const s=sample(values,'Sample'),alt=alternativeOf(alternative),conf=confidenceOf(confidence);if(!(s.variance>0))throw Error('Sample has zero variance; a variance interval needs spread in the data.');
 const df=s.n-1,C=builders.chisquare({k:df}),ss=df*s.variance;let ci;
 if(alt==='less')ci=[0,ss/C.quantile(1-conf)];else if(alt==='greater')ci=[ss/C.quantile(conf),Infinity];else ci=[ss/C.quantile(1-(1-conf)/2),ss/C.quantile((1-conf)/2)];
 const has=sigma2!==null&&sigma2!==undefined&&String(sigma2).trim()!=='';let stat=null,pv=null,s2=null;
 if(has){s2=positive(sigma2,'Null variance σ0²');stat=ss/s2;pv=alt==='less'?C.cdf(stat):alt==='greater'?C.sf(stat):Math.min(1,2*Math.min(C.cdf(stat),C.sf(stat)));}
 return {type:'hypothesis',test:'Chi-square variance test / interval',statisticName:'χ²',statistic:stat,df,pValue:pv,alternative:alt,confidence:conf,estimate:s.variance,n:s.n,sigma2:s2,ci,ciLabel:'Confidence interval for σ²',
  effectSize:has?{name:'Variance ratio s²/σ0²',value:s.variance/s2}:null,warnings:[],
  assumptions:'Assumes independent observations from a normal population; unlike the t-test, this interval is NOT robust to non-normality.'};
}
/** Parse a comma/space/semicolon separated list of numbers (plain numeric literals only, no expression evaluation). */
function parseList(text,name='List'){
 return String(text??'').split(/[\s,;]+/).filter(Boolean).map(s=>{const n=Number(s);if(!Number.isFinite(n))throw Error(name+': "'+s.slice(0,24)+'" is not a finite number.');return n;});
}
/** Parse a contingency table: rows separated by ';' or newlines, cells by commas or spaces. */
function parseMatrix(text){return String(text??'').split(/[;\n]+/).map(r=>r.trim()).filter(Boolean).map((r,i)=>parseList(r,'Row '+(i+1)));}
function tableOf(name){const T=M.dataTables;if(!T)throw Error('Data Tables are unavailable.');const t=T.tables.find(s=>s.name===name||s.id===name);if(!t)throw Error('Choose an existing data table.');return {t,rows:typeof T.calculate==='function'?T.calculate(t):t.rows};}
/** Numeric values of a Data Tables column (blank and text cells ignored, as in describeTable). */
function tableColumn(table,column){const {t,rows}=tableOf(table),i=t.columns.indexOf(String(column??''));if(i<0)throw Error('Choose an existing column.');return columnValues(rows.map(r=>r?.[i])).values;}
/** Complete numeric pairs from two Data Tables columns. */
function tablePairs(table,c1,c2){
 const {t,rows}=tableOf(table),i=t.columns.indexOf(String(c1??'')),j=t.columns.indexOf(String(c2??''));
 if(i<0||j<0)throw Error('Choose two existing columns.');if(i===j)throw Error('Choose two different columns.');
 const xs=[],ys=[];for(const r of rows){const a=toNumber(r?.[i]),b=toNumber(r?.[j]);if(a!==null&&b!==null){xs.push(a);ys.push(b);}}return [xs,ys];
}
/** Contingency table from every numeric column of a Data Table (text label columns and blank rows skipped). */
function tableMatrix(table){
 const {t,rows}=tableOf(table),cols=t.columns.map((_,j)=>j).filter(j=>{let any=false;for(const r of rows){const s=String(r?.[j]??'').trim();if(!s)continue;if(toNumber(s)===null)return false;any=true;}return any;});
 if(cols.length<2)throw Error('The table needs at least two numeric columns for a contingency table.');
 return rows.filter(r=>cols.some(j=>String(r?.[j]??'').trim()!=='')).map((r,i)=>cols.map(j=>{const n=toNumber(r?.[j]);if(n===null)throw Error('Contingency cell in row '+(i+1)+' is blank.');return n;}));
}
const TESTS={
 t1:o=>ttestOne(o.x,o),welch:o=>ttestTwo(o.x,o.y,{...o,equalVariance:false}),pooled:o=>ttestTwo(o.x,o.y,{...o,equalVariance:true}),paired:o=>ttestPaired(o.x,o.y,o),
 gof:o=>chisqGof(o.x,o.y,o),independence:o=>chisqIndependence(o.table,o),prop:o=>propZTest(o.k,o.n,o),binom:o=>binomTest(o.k,o.n,{...o,p:o.p0}),variance:o=>varianceTest(o.x,o)
};
function hypothesisTest(test,options={}){const f=TESTS[test];if(!f)throw Error('Unknown test: '+test+'.');return f(options||{});}

M.statistics={logGamma,gammaP,gammaQ,betaI,erf,erfc,distribution,evaluate,describe,correlate,describeColumns,describeTable,quantile7,
 ttestOne,ttestTwo,ttestPaired,chisqGof,chisqIndependence,propZTest,wilson,binomTest,clopperPearson,varianceTest,parseList,parseMatrix,tableColumn,tablePairs,tableMatrix,hypothesisTest};

/* ---------- UI ---------- */
const panel=document.getElementById('numerical-panel');if(!panel)return;
const $=id=>document.getElementById(id);
const fmt=v=>v===null||v===undefined?'undefined':typeof v==='number'?(Number.isFinite(v)?(Number.isInteger(v)&&Math.abs(v)<1e15?String(v):Number(v.toPrecision(12)).toString()):String(v)):String(v);
const PARAMS={normal:[['mu','Mean μ','0'],['sigma','Standard deviation σ','1']],t:[['nu','Degrees of freedom ν','10']],chisquare:[['k','Degrees of freedom k','2']],exponential:[['lambda','Rate λ','1']],binomial:[['n','Trials n','10'],['p','Success probability p','0.3']],poisson:[['lambda','Rate λ','4']]};
const area=document.createElement('details');area.id='stats-details';
area.innerHTML='<summary>Statistics · distributions, descriptive statistics and hypothesis tests</summary>'+
 '<p>Density/mass, CDF, survival and quantile for common distributions; summary statistics for Data Tables columns; t, chi-square, proportion, binomial and variance tests with confidence intervals.</p>'+
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
 '<h4 id="stats-ht-heading">Hypothesis test</h4>'+
 '<div class="num-fields" role="group" aria-labelledby="stats-ht-heading"><label>Test<select id="stats-test"><option value="t1">One-sample t-test (mean)</option><option value="welch">Welch two-sample t-test</option><option value="pooled">Pooled-variance two-sample t-test</option><option value="paired">Paired t-test</option>'+
 '<option value="gof">Chi-square goodness-of-fit</option><option value="independence">Chi-square independence (r×c)</option><option value="prop">One-proportion z-test (Wilson CI)</option><option value="binom">Exact binomial test</option><option value="variance">Variance interval / chi-square test</option></select></label>'+
 '<label id="stats-ht-source-label">Data source<select id="stats-ht-source"><option value="typed">Typed lists</option><option value="table">Data table and columns above</option></select></label>'+
 '<label id="stats-ht-a-label"><span id="stats-ht-a-name">Sample</span><input id="stats-ht-a" type="text" autocomplete="off" spellcheck="false"></label>'+
 '<label id="stats-ht-b-label"><span id="stats-ht-b-name">Sample 2</span><input id="stats-ht-b" type="text" autocomplete="off" spellcheck="false"></label>'+
 '<label id="stats-ht-k-label">Successes k<input id="stats-ht-k" type="number" step="1" min="0"></label>'+
 '<label id="stats-ht-n-label">Trials n<input id="stats-ht-n" type="number" step="1" min="1"></label>'+
 '<label id="stats-ht-param-label"><span id="stats-ht-param-name">Hypothesized mean μ0</span><input id="stats-ht-param" type="number" step="any"></label>'+
 '<label id="stats-ht-alt-label">Alternative<select id="stats-ht-alt"><option value="two-sided">Two-sided (≠)</option><option value="less">Less (&lt;)</option><option value="greater">Greater (&gt;)</option></select></label>'+
 '<label id="stats-ht-conf-label">Confidence level<input id="stats-ht-conf" type="number" step="any" min="0" max="1" value="0.95"></label>'+
 '<label id="stats-ht-yates-label">Continuity correction<select id="stats-ht-yates"><option value="">None</option><option value="yates">Yates (2×2 only)</option></select></label></div>'+
 '<div class="data-toolbar"><button id="stats-ht-run" class="primary" type="button">Run test</button></div>'+
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
const HT={
 t1:{a:['Sample (comma-separated)','5.1, 4.9, 5.6, 5.8, 6.0, 5.2'],param:['Hypothesized mean μ0','5'],alt:1,source:1},
 welch:{a:['Sample 1','1, 2, 3, 4, 5'],b:['Sample 2','2, 4, 6, 8, 10'],param:['Hypothesized difference Δ0','0'],alt:1,source:1},
 pooled:{a:['Sample 1','1, 2, 3, 4, 5'],b:['Sample 2','2, 4, 6, 8, 10'],param:['Hypothesized difference Δ0','0'],alt:1,source:1},
 paired:{a:['Sample 1 (before)','1, 2, 3, 4, 5.5'],b:['Sample 2 (after)','2, 4, 6, 8, 10'],param:['Hypothesized mean difference Δ0','0'],alt:1,source:1},
 gof:{a:['Observed counts','16, 18, 16, 14, 12, 12'],b:['Expected counts or proportions (blank = uniform)',''],source:1,noConf:1},
 independence:{a:['Contingency table (rows separated by ;)','10, 20; 20, 40'],source:1,yates:1,noConf:1},
 prop:{kn:['81','263'],param:['Null proportion p0','0.25'],alt:1},
 binom:{kn:['7','20'],param:['Null proportion p0','0.5'],alt:1},
 variance:{a:['Sample (comma-separated)','5.1, 4.9, 5.6, 5.8, 6.0, 5.2'],param:['Null variance σ0² (optional)',''],alt:1,source:1}
};
function syncTest(){
 const s=HT[$('stats-test').value],show=(id,on)=>{$(id).hidden=!on;};
 show('stats-ht-a-label',s.a);show('stats-ht-b-label',s.b);show('stats-ht-k-label',s.kn);show('stats-ht-n-label',s.kn);show('stats-ht-param-label',s.param);
 show('stats-ht-alt-label',s.alt);show('stats-ht-conf-label',!s.noConf);show('stats-ht-yates-label',s.yates);show('stats-ht-source-label',s.source);
 if(s.a){$('stats-ht-a-name').textContent=s.a[0];$('stats-ht-a').value=s.a[1];}if(s.b){$('stats-ht-b-name').textContent=s.b[0];$('stats-ht-b').value=s.b[1];}
 if(s.param){$('stats-ht-param-name').textContent=s.param[0];$('stats-ht-param').value=s.param[1];}if(s.kn){$('stats-ht-k').value=s.kn[0];$('stats-ht-n').value=s.kn[1];}
 if(!s.source)$('stats-ht-source').value='typed';$('stats-ht-alt').value='two-sided';
}
function testInputs(test){
 const s=HT[test],fromTable=s.source&&$('stats-ht-source').value==='table',table=$('stats-table').value,c1=$('stats-column').value,c2=$('stats-column2').value;
 const o={alternative:$('stats-ht-alt').value,confidence:$('stats-ht-conf').value,yates:$('stats-ht-yates').value==='yates'};
 if(s.param){const v=$('stats-ht-param').value;if(test==='prop'||test==='binom')o.p0=v;else if(test==='variance')o.sigma2=v;else o.mu=v;}
 if(s.kn){o.k=$('stats-ht-k').value;o.n=$('stats-ht-n').value;return o;}
 if(test==='independence'){o.table=fromTable?tableMatrix(table):parseMatrix($('stats-ht-a').value);return o;}
 if(!fromTable){o.x=parseList($('stats-ht-a').value,s.a[0]);if(s.b){const b=parseList($('stats-ht-b').value,s.b[0]);o.y=test==='gof'&&!b.length?null:b;}return o;}
 if(test==='paired'||(test==='gof'&&c2)){[o.x,o.y]=tablePairs(table,c1,c2);return o;}
 o.x=tableColumn(table,c1);if(test==='welch'||test==='pooled'){if(!c2)throw Error('Choose a second column for sample 2.');if(c2===c1)throw Error('Choose two different columns.');o.y=tableColumn(table,c2);}
 return o;
}
const cell=v=>typeof v==='number'&&Number.isFinite(v)?v:fmt(v);
$('stats-test').addEventListener('change',()=>{syncTest();invalidate();});
$('stats-ht-run').addEventListener('click',()=>{
 try{
  const test=$('stats-test').value,r=hypothesisTest(test,testInputs(test)),lines=[r.test],rows=[['test',r.test]];
  const add=(label,key,v)=>{lines.push(label+' = '+fmt(v));rows.push([key,cell(v)]);};
  if(r.n!==undefined)add(r.n2!==undefined?'n1':'n','n',r.n);if(r.n2!==undefined)add('n2','n2',r.n2);
  if(r.statistic!==null)add(r.statisticName+' statistic','statistic_'+r.statisticName,r.statistic);if(r.df!==null&&r.df!==undefined)add('Degrees of freedom','df',r.df);
  if(r.pValue!==null){lines.push('p-value ('+r.alternative+') = '+fmt(r.pValue));rows.push(['alternative',r.alternative],['p_value',r.pValue]);}
  if(r.estimate!==undefined)add('Estimate','estimate',r.estimate);
  if(r.ci){const pct=Number((r.confidence*100).toPrecision(10))+'%';lines.push(r.ciLabel+' ('+pct+') = ['+fmt(r.ci[0])+', '+fmt(r.ci[1])+']');rows.push(['confidence',r.confidence],['ci_lower',cell(r.ci[0])],['ci_upper',cell(r.ci[1])]);}
  if(r.effectSize)add('Effect size '+r.effectSize.name,'effect_size',r.effectSize.value);
  for(const w of r.warnings){lines.push('Warning: '+w);rows.push(['warning',w]);}
  lines.push('Assumptions: '+r.assumptions);rows.push(['assumptions',r.assumptions]);
  last={headers:['quantity','value'],rows,name:'Statistics_HypothesisTest'};output.classList.remove('error');output.textContent=lines.join('\n');$('stats-to-table').disabled=false;
 }catch(err){fail(err);}
});
syncTest();
syncParams();syncTables();
})();
