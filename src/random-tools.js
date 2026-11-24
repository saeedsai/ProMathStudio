/* Offline seeded random numbers (PCG32), distribution samplers and Monte Carlo / Halton quasi-Monte Carlo integration.
   Deterministic by seed; never uses the platform's unseeded generator. Integrands use the shared safe numeric evaluator. */
(()=>{'use strict';
const M=window.MathStudio=window.MathStudio||{};
const TWO32=4294967296,TWO53=9007199254740992,MUL_HI=0x5851f42d,MUL_LO=0x4c957f2d,MAX_SAMPLES=100000,TABLE_ROWS=6000,MAX_MC=1000000,LIMIT=1e12;
const PRIMES=[2,3,5,7,11,13];
const now=()=>typeof performance!=='undefined'&&performance.now?performance.now():Date.now();

/* ---------- PCG32 (XSH-RR 64/32, O'Neill 2014): 64-bit LCG state held as two uint32 halves; period 2^64 per stream ---------- */
// Exact 64-bit product modulo 2^64 using 16-bit limbs for the low word and Math.imul for the cross terms.
function mul64(ah,al,bh,bl){
 const a0=al&0xffff,a1=al>>>16,b0=bl&0xffff,b1=bl>>>16,mid=a1*b0+a0*b1,lo=a0*b0+(mid%65536)*65536;
 return [(a1*b1+Math.floor(mid/65536)+Math.floor(lo/TWO32)+Math.imul(ah,bl)+Math.imul(al,bh))>>>0,(lo%TWO32)>>>0];
}
function seedValue(value,name='Seed'){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');
 const n=Number(value);if(!Number.isSafeInteger(n)||n<0)throw Error(name+' must be an integer from 0 to 2^53−1.');return n;
}
function pcg32(seed=0,stream=54){
 seed=seedValue(seed);stream=seedValue(stream,'Stream');
 let sh=0,sl=0;const qh=Math.floor(stream/TWO32),ql=stream%TWO32;
 const ih=((qh<<1)|(ql>>>31))>>>0,il=((ql<<1)|1)>>>0;
 const step=()=>{const [h,l]=mul64(sh,sl,MUL_HI,MUL_LO),nl=l+il;sl=nl>>>0;sh=(h+ih+(nl>=TWO32?1:0))>>>0;};
 const u32=()=>{
  const h=sh,l=sl;step();
  const yh=(h^(h>>>18))>>>0,yl=(l^((l>>>18)|(h<<14)))>>>0,xs=((yl>>>27)|(yh<<5))>>>0,rot=h>>>27;
  return ((xs>>>rot)|(xs<<((32-rot)&31)))>>>0;
 };
 step();{const nl=sl+seed%TWO32;sl=nl>>>0;sh=(sh+Math.floor(seed/TWO32)+(nl>=TWO32?1:0))>>>0;}step();
 let spare=null;
 const g={
  u32,
  /** 53-bit uniform double in [0,1). */
  float:()=>((u32()>>>5)*67108864+(u32()>>>6))/TWO53,
  /** 53-bit uniform double in the open interval (0,1), safe for logarithms. */
  open:()=>((u32()>>>5)*67108864+(u32()>>>6)+0.5)/TWO53,
  /** Unbiased integer in [0,n) by rejection, 1 ≤ n ≤ 2^32. */
  int:n=>{if(!Number.isInteger(n)||n<1||n>TWO32)throw Error('Integer range must be 1 to 2^32.');const threshold=(TWO32-n)%n;for(;;){const r=u32();if(r>=threshold)return r%n;}},
  /** Standard normal by the Box–Muller transform (pairs cached). */
  normal:()=>{if(spare!==null){const z=spare;spare=null;return z;}const r=Math.sqrt(-2*Math.log(g.open())),t=2*Math.PI*g.float();spare=r*Math.sin(t);return r*Math.cos(t);},
  state:()=>({hi:sh,lo:sl,incHi:ih,incLo:il})
 };
 return g;
}

/* ---------- parameter checks ---------- */
function num(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');const n=Number(value);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(name+' must be finite and at most 1e12 in magnitude.');return n;}
function positive(value,name){const n=num(value,name);if(!(n>0))throw Error(name+' must be positive.');return n;}
function integer(value,name,lo,hi){const n=num(value,name);if(!Number.isInteger(n)||n<lo||n>hi)throw Error(name+' must be an integer from '+lo+' to '+hi+'.');return n;}
function probability(value,name='p'){const n=num(value,name);if(n<0||n>1)throw Error(name+' must be in [0, 1].');return n;}
function parseWeights(value){
 const list=Array.isArray(value)?value:String(value??'').split(/[\s,;]+/).filter(Boolean);
 if(list.length<1||list.length>1000)throw Error('Provide 1 to 1000 weights.');
 const w=list.map((x,i)=>{const n=Number(x);if(!Number.isFinite(n)||n<0)throw Error('Weight '+(i+1)+' must be a finite non-negative number.');return n;});
 if(!(w.reduce((s,x)=>s+x,0)>0))throw Error('Weights must have a positive sum.');return w;
}
function logGamma(x){if(!M.statistics?.logGamma)throw Error('Statistics module is required for this sampler.');return M.statistics.logGamma(x);}

/* ---------- samplers (each takes a generator g) ---------- */
function gammaSample(g,k){
 // Marsaglia–Tsang (2000) squeeze; k<1 uses the boost X·U^(1/k) with X~Gamma(k+1).
 if(k<1)return gammaSample(g,k+1)*Math.pow(g.open(),1/k);
 const d=k-1/3,c=1/Math.sqrt(9*d);
 for(;;){let x,v;do{x=g.normal();v=1+c*x;}while(v<=0);v=v*v*v;const u=g.open(),x2=x*x;
  if(u<1-0.0331*x2*x2||Math.log(u)<0.5*x2+d*(1-v+Math.log(v)))return d*v;}
}
function poissonSample(g,lambda){
 if(lambda<10){// sequential-search inversion
  let x=0,p=Math.exp(-lambda),F=p;const u=g.float();
  while(u>F&&x<1000){x++;p*=lambda/x;F+=p;}return x;
 }
 // PTRS transformed rejection with squeeze (Hörmann 1993).
 const slam=Math.sqrt(lambda),loglam=Math.log(lambda),b=0.931+2.53*slam,a=-0.059+0.02483*b,invalpha=1.1239+1.1328/(b-3.4),vr=0.9277-3.6224/(b-2);
 for(;;){const U=g.float()-0.5,V=g.open(),us=0.5-Math.abs(U),k=Math.floor((2*a/us+b)*U+lambda+0.43);
  if(us>=0.07&&V<=vr)return k;if(k<0||(us<0.013&&V>us))continue;
  if(Math.log(V)+Math.log(invalpha)-Math.log(a/(us*us)+b)<=-lambda+k*loglam-logGamma(k+1))return k;}
}
function binomialSample(g,n,p){
 if(p===0||n===0)return 0;if(p===1)return n;
 if(p>0.5)return n-binomialSample(g,n,1-p);
 const q=1-p;
 if(n*p<10){// inversion by sequential search
  const s=p/q,a=(n+1)*s;let r=Math.pow(q,n),u=g.float(),x=0;
  while(u>r){u-=r;x++;if(x>n)return n;r*=a/x-s;}return x;
 }
 // BTRS transformed rejection (Hörmann 1993).
 const spq=Math.sqrt(n*p*q),b=1.15+2.53*spq,a=-0.0873+0.0248*b+0.01*p,c=n*p+0.5,vr=0.92-4.2/b,alpha=(2.83+5.1/b)*spq,lpq=Math.log(p/q),m=Math.floor((n+1)*p),h=logGamma(m+1)+logGamma(n-m+1);
 for(;;){const U=g.float()-0.5,V=g.open(),us=0.5-Math.abs(U),k=Math.floor((2*a/us+b)*U+c);
  if(k<0||k>n)continue;if(us>=0.07&&V<=vr)return k;
  if(Math.log(V*alpha/(a/(us*us)+b))<=h-logGamma(k+1)-logGamma(n-k+1)+(k-m)*lpq)return k;}
}
/** Vose alias table for O(1) sampling of categories 0..m-1 with the given weights. */
function aliasTable(weights){
 const w=parseWeights(weights),m=w.length,total=w.reduce((s,x)=>s+x,0),prob=new Float64Array(m),alias=new Int32Array(m),scaled=w.map(x=>x*m/total),small=[],large=[];
 scaled.forEach((x,i)=>(x<1?small:large).push(i));
 while(small.length&&large.length){const s=small.pop(),l=large.pop();prob[s]=scaled[s];alias[s]=l;scaled[l]=scaled[l]+scaled[s]-1;(scaled[l]<1?small:large).push(l);}
 for(const i of large)prob[i]=1;for(const i of small)prob[i]=1;
 return {prob,alias,weights:w,sample:g=>{const i=g.int(m);return g.float()<prob[i]?i:alias[i];}};
}
/** In-place Fisher–Yates shuffle of an array copy. */
function shuffle(values,seed=0){const g=typeof seed==='object'?seed:pcg32(seed),a=Array.from(values);for(let i=a.length-1;i>0;i--){const j=g.int(i+1),t=a[i];a[i]=a[j];a[j]=t;}return a;}
function permutation(n,seed=0){n=integer(n,'Permutation size n',1,MAX_SAMPLES);return shuffle(Array.from({length:n},(_,i)=>i+1),seed);}
/** k distinct values from 1..n by a sparse partial Fisher–Yates shuffle (memory O(k)). */
function withoutReplacement(n,k,seed=0){
 n=integer(n,'Population size n',1,1e9);k=integer(k,'Sample size k',1,MAX_SAMPLES);if(k>n)throw Error('Sample size k must not exceed population size n without replacement.');
 const g=typeof seed==='object'?seed:pcg32(seed),swap=new Map(),out=new Array(k);
 for(let i=0;i<k;i++){const j=i+g.int(n-i),vj=swap.has(j)?swap.get(j):j,vi=swap.has(i)?swap.get(i):i;swap.set(j,vi);out[i]=vj+1;}
 return out;
}

const DISTRIBUTIONS={
 uniform:{label:'Uniform U(a, b)',params:[['a','Lower a','0'],['b','Upper b','1']],check:p=>{const a=num(p.a,'Lower a'),b=num(p.b,'Upper b');if(!(b>a))throw Error('Upper b must exceed lower a.');return {a,b};},draw:(g,p)=>p.a+(p.b-p.a)*g.float(),moments:p=>[(p.a+p.b)/2,(p.b-p.a)**2/12]},
 normal:{label:'Normal N(μ, σ)',params:[['mu','Mean μ','0'],['sigma','Standard deviation σ','1']],check:p=>({mu:num(p.mu,'Mean μ'),sigma:positive(p.sigma,'Standard deviation σ')}),draw:(g,p)=>p.mu+p.sigma*g.normal(),moments:p=>[p.mu,p.sigma*p.sigma]},
 exponential:{label:'Exponential(λ)',params:[['lambda','Rate λ','1']],check:p=>({lambda:positive(p.lambda,'Rate λ')}),draw:(g,p)=>-Math.log(g.open())/p.lambda,moments:p=>[1/p.lambda,1/(p.lambda*p.lambda)]},
 gamma:{label:'Gamma(k, θ) · Marsaglia–Tsang',params:[['k','Shape k','2'],['theta','Scale θ','1']],check:p=>{const k=positive(p.k,'Shape k');if(k>1e6)throw Error('Shape k must be at most 1e6.');return {k,theta:positive(p.theta,'Scale θ')};},draw:(g,p)=>p.theta*gammaSample(g,p.k),moments:p=>[p.k*p.theta,p.k*p.theta*p.theta]},
 beta:{label:'Beta(α, β) via gamma ratio',params:[['alpha','Shape α','2'],['beta','Shape β','5']],check:p=>{const alpha=positive(p.alpha,'Shape α'),beta=positive(p.beta,'Shape β');if(alpha>1e6||beta>1e6)throw Error('Beta shapes must be at most 1e6.');return {alpha,beta};},
  draw:(g,p)=>{const x=gammaSample(g,p.alpha),y=gammaSample(g,p.beta);return x/(x+y);},moments:p=>{const s=p.alpha+p.beta;return [p.alpha/s,p.alpha*p.beta/(s*s*(s+1))];}},
 poisson:{label:'Poisson(λ) · inversion / PTRS',discrete:true,params:[['lambda','Rate λ','4']],check:p=>{const lambda=positive(p.lambda,'Rate λ');if(lambda>1e7)throw Error('Rate λ must be at most 1e7.');return {lambda};},draw:(g,p)=>poissonSample(g,p.lambda),moments:p=>[p.lambda,p.lambda]},
 binomial:{label:'Binomial(n, p) · inversion / BTRS',discrete:true,params:[['n','Trials n','10'],['p','Success probability p','0.3']],check:p=>({n:integer(p.n,'Trials n',0,1e9),p:probability(p.p,'Success probability p')}),draw:(g,p)=>binomialSample(g,p.n,p.p),moments:p=>[p.n*p.p,p.n*p.p*(1-p.p)]},
 discrete:{label:'Discrete weights · alias method',discrete:true,params:[['weights','Weights for 0, 1, 2, …','1 2 3 4']],check:p=>({weights:parseWeights(p.weights)}),
  moments:p=>{const W=p.weights.reduce((s,x)=>s+x,0);let m=0,m2=0;p.weights.forEach((w,i)=>{m+=i*w/W;m2+=i*i*w/W;});return [m,m2-m*m];}},
 permutation:{label:'Random permutation of 1..n (Fisher–Yates)',discrete:true,params:[],check:()=>({}),moments:(p,n)=>[(n+1)/2,(n*n-1)/12]},
 withoutReplacement:{label:'Sample without replacement from 1..n',discrete:true,params:[['population','Population size n','100']],check:p=>({population:integer(p.population,'Population size n',1,1e9)}),moments:p=>[(p.population+1)/2,(p.population**2-1)/12]}
};

/** Draw N samples. Returns values with sample and theoretical moments (marginal moments for permutations/without replacement). */
function sample({distribution='normal',params={},n=1000,seed=12345}={}){
 const spec=DISTRIBUTIONS[distribution];if(!spec)throw Error('Unknown distribution: '+distribution+'.');
 n=integer(n,'Sample count N',1,MAX_SAMPLES);seed=seedValue(seed);const p=spec.check({...Object.fromEntries(spec.params.map(q=>[q[0],q[2]])),...(params||{})}),g=pcg32(seed);let values;
 if(distribution==='permutation')values=permutation(n,g);
 else if(distribution==='withoutReplacement')values=withoutReplacement(p.population,n,g);
 else{values=new Array(n);const table=distribution==='discrete'?aliasTable(p.weights):null;for(let i=0;i<n;i++)values[i]=table?table.sample(g):spec.draw(g,p);}
 const [theoreticalMean,theoreticalVariance]=spec.moments(p,n);
 const stats=M.statistics?.describe?M.statistics.describe(values):null;
 return {type:'random-sample',distribution,label:spec.label,params:p,n,seed,values,discrete:!!spec.discrete,theoreticalMean,theoreticalVariance,
  mean:stats?stats.mean:values.reduce((s,x)=>s+x,0)/n,variance:stats?stats.sampleVariance:null,min:stats?stats.min:Math.min(...values),max:stats?stats.max:Math.max(...values),
  generator:'PCG32 XSH-RR 64/32, stream 54, period 2^64',note:'Deterministic pseudo-random numbers for simulation; not suitable for cryptography.'};
}
/** Column-major Data Tables layout: at most 6,000 rows per column, ⌈N/6000⌉ ≤ 17 value columns. */
function toTable(result){
 if(!result?.values?.length)throw Error('Generate samples first.');const v=result.values,cols=Math.ceil(v.length/TABLE_ROWS),rows=Math.min(v.length,TABLE_ROWS);
 const headers=cols===1?['value']:Array.from({length:cols},(_,c)=>'value_'+(c+1)),out=[];
 for(let r=0;r<rows;r++){const row=[];for(let c=0;c<cols;c++){const i=c*TABLE_ROWS+r;row.push(i<v.length?String(Number(v[i].toPrecision(12))):'');}out.push(row);}
 return {headers,rows:out};
}

/* ---------- Monte Carlo and Halton quasi-Monte Carlo integration over a box ---------- */
function radicalInverse(i,base){let f=1/base,r=0;while(i>0){r+=f*(i%base);i=Math.floor(i/base);f/=base;}return r;}
function halton(index,dimension){index=integer(index,'Halton index',0,1e9);dimension=integer(dimension,'Dimension d',1,6);return PRIMES.slice(0,dimension).map(b=>radicalInverse(index,b));}
function bounds(value,d,name){
 const list=Array.isArray(value)?value:String(value??'').split(/[\s,;]+/).filter(Boolean);
 if(list.length===1)return Array(d).fill(num(list[0],name));
 if(list.length!==d)throw Error(name+' needs 1 or '+d+' values (one per dimension).');return list.map((x,i)=>num(x,name+' '+(i+1)));
}
const ALIASES=['x','y','z','u','v','w'];
function setup({expression='x1*x2',dimension=2,lower=0,upper=1}={}){
 expression=String(expression??'').trim();if(!expression||expression.length>1000)throw Error('Enter an integrand of 1–1000 characters.');
 if(!M.numerical?.evaluate)throw Error('The numerical evaluator is unavailable.');
 const d=integer(dimension,'Dimension d',1,6),lo=bounds(lower,d,'Lower bound'),hi=bounds(upper,d,'Upper bound');
 lo.forEach((a,i)=>{if(!(hi[i]>a))throw Error('Upper bound '+(i+1)+' must exceed lower bound '+(i+1)+'.');});
 const volume=lo.reduce((s,a,i)=>s*(hi[i]-a),1),env={};
 const f=(u,index)=>{for(let i=0;i<d;i++){const x=lo[i]+(hi[i]-lo[i])*u[i];env['x'+(i+1)]=x;env[ALIASES[i]]=x;}
  let y;try{y=M.numerical.evaluate(expression,env);}catch(err){throw Error('Integrand undefined at sample '+index+' ('+lo.map((_,i)=>'x'+(i+1)+'='+Number(env['x'+(i+1)].toPrecision(6))).join(', ')+'): '+err.message);}
  if(!Number.isFinite(y))throw Error('Integrand is not finite at sample '+index+'.');return y;};
 f(lo.map(()=>0.5),0);return {expression,d,lo,hi,volume,f};
}
function makeStreams(s,seed,scramble){
 const g=pcg32(seed,54),shiftGen=pcg32(seed,55),shift=scramble?Array.from({length:s.d},()=>shiftGen.float()):null,u=new Array(s.d),q=new Array(s.d);
 return {mc:i=>{for(let k=0;k<s.d;k++)u[k]=g.float();return s.f(u,i);},
  halton:i=>{for(let k=0;k<s.d;k++){let x=radicalInverse(i,PRIMES[k]);if(shift){x+=shift[k];if(x>=1)x-=1;}q[k]=x;}return s.f(q,i);}};
}
/** Single estimate. method: 'mc' (plain, with standard error), 'halton' or 'halton-shift' (Cranley–Patterson random shift). */
function integrate({expression,dimension=2,lower=0,upper=1,n=10000,method='mc',seed=12345,budgetMs=8000}={}){
 if(!['mc','halton','halton-shift'].includes(method))throw Error('Method must be mc, halton or halton-shift.');
 const s=setup({expression,dimension,lower,upper});n=integer(n,'Sample count N',100,MAX_MC);seed=seedValue(seed);
 const streams=makeStreams(s,seed,method==='halton-shift'),draw=method==='mc'?streams.mc:streams.halton,start=now();
 let mean=0,m2=0,i=0,truncated=false;
 for(;i<n;i++){if((i&1023)===1023&&now()-start>budgetMs){truncated=true;break;}const y=draw(i+1),dlt=y-mean;mean+=dlt/(i+1);m2+=dlt*(y-mean);}
 const estimate=s.volume*mean,se=method==='mc'&&i>1?s.volume*Math.sqrt(m2/(i-1)/i):null;
 return {type:'monte-carlo-integral',method,expression:s.expression,dimension:s.d,lower:s.lo,upper:s.hi,volume:s.volume,n:i,requested:n,estimate,standardError:se,truncated,seed,
  milliseconds:now()-start,note:method==='mc'?'Plain Monte Carlo: error ≈ standard error·O(1) with probability; SE assumes finite integrand variance.':'Halton quasi-Monte Carlo (bases 2,3,5,7,11,13'+(method==='halton-shift'?', seeded random shift':'')+'): no standard error is reported for a deterministic point set.'};
}
/** Convergence table for plain MC and Halton at N = 10^2 … 10^6 (≤ maxN), stopped when the time budget is spent. */
function convergence({expression,dimension=2,lower=0,upper=1,maxN=MAX_MC,seed=12345,scramble=false,budgetMs=5000}={}){
 const s=setup({expression,dimension,lower,upper});maxN=integer(maxN,'Maximum N',100,MAX_MC);seed=seedValue(seed);
 budgetMs=num(budgetMs,'Time budget');if(budgetMs<10||budgetMs>60000)throw Error('Time budget must be 10 to 60000 ms.');
 const streams=makeStreams(s,seed,scramble),checks=[100,1000,10000,100000,1000000].filter(x=>x<=maxN),rows=[],start=now();
 let mean=0,m2=0,hsum=0,i=0,truncated=false;
 for(const target of checks){
  for(;i<target;i++){if((i&1023)===1023&&now()-start>budgetMs){truncated=true;break;}const y=streams.mc(i+1),dlt=y-mean;mean+=dlt/(i+1);m2+=dlt*(y-mean);hsum+=streams.halton(i+1);}
  if(truncated)break;
  rows.push({n:target,mc:s.volume*mean,standardError:s.volume*Math.sqrt(m2/(target-1)/target),halton:s.volume*hsum/target});
 }
 return {type:'monte-carlo-convergence',expression:s.expression,dimension:s.d,volume:s.volume,rows,truncated,skipped:checks.slice(rows.length),seed,scramble,milliseconds:now()-start};
}

M.random={pcg32,sample,toTable,aliasTable,shuffle,permutation,withoutReplacement,halton,radicalInverse,integrate,convergence,distributions:Object.fromEntries(Object.entries(DISTRIBUTIONS).map(([k,v])=>[k,{label:v.label,discrete:!!v.discrete,params:v.params.map(p=>p[0])}])),maxSamples:MAX_SAMPLES,tableRows:TABLE_ROWS};

/* ---------- UI ---------- */
const panel=typeof document!=='undefined'&&document.getElementById('numerical-panel');if(!panel||!document.createElement)return;
const $=id=>document.getElementById(id),fmt=v=>v===null||v===undefined?'—':Number.isFinite(v)?Number(v.toPrecision(8)).toString():String(v);
const area=document.createElement('details');area.id='random-details';
area.innerHTML='<summary>Random numbers · seeded sampling and Monte Carlo integration</summary>'+
 '<style>#random-details label{min-width:0}#random-canvas{width:100%;max-width:480px;height:auto;display:block;border:1px solid #d8dfeb;border-radius:9px;background:#fff}#random-details pre{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%}#random-details h4{margin:14px 0 4px}</style>'+
 '<p>Deterministic PCG32 pseudo-random samples (period 2^64; not cryptographic). Up to 100,000 samples; Data Tables hold at most 6,000 rows per column, so larger samples are wrapped into value_1…value_17 columns.</p>'+
 '<div class="num-fields"><label>Distribution<select id="random-distribution"></select></label>'+
 '<label id="random-p1-label"><span>Parameter 1</span><input id="random-p1" autocomplete="off"></label>'+
 '<label id="random-p2-label"><span>Parameter 2</span><input id="random-p2" autocomplete="off"></label>'+
 '<label>Samples N (1–100000)<input id="random-n" type="number" step="1" min="1" max="100000" value="1000"></label>'+
 '<label>Seed<input id="random-seed" type="number" step="1" min="0" value="12345"></label></div>'+
 '<div class="data-toolbar"><button id="random-generate" class="primary" type="button">Generate samples</button>'+
 '<button id="random-to-table" class="secondary" type="button" disabled>Save samples to Data Tables</button></div>'+
 '<pre id="random-output" role="status" aria-live="polite">Choose a distribution, parameters, N and seed.</pre>'+
 '<canvas id="random-canvas" width="480" height="160" role="img" aria-label="Sample histogram: not yet generated"></canvas>'+
 '<h4>Monte Carlo integration over a box</h4>'+
 '<div class="num-fields"><label>Integrand f(x1…xd) or f(x,y,z,u,v,w)<input id="random-mc-expression" value="x1*x2" autocomplete="off" spellcheck="false"></label>'+
 '<label>Dimension d (1–6)<input id="random-mc-dimension" type="number" step="1" min="1" max="6" value="2"></label>'+
 '<label>Lower bounds<input id="random-mc-lower" value="0" autocomplete="off"></label>'+
 '<label>Upper bounds<input id="random-mc-upper" value="1" autocomplete="off"></label>'+
 '<label>Samples N (100–1000000)<input id="random-mc-n" type="number" step="1" min="100" max="1000000" value="10000"></label>'+
 '<label>Method<select id="random-mc-method"><option value="mc">Plain Monte Carlo (with SE)</option><option value="halton">Halton quasi-Monte Carlo</option><option value="halton-shift">Halton, seeded random shift</option></select></label></div>'+
 '<div class="data-toolbar"><button id="random-mc-run" class="primary" type="button">Integrate</button>'+
 '<button id="random-mc-convergence" class="secondary" type="button">Convergence table</button>'+
 '<button id="random-mc-to-table" class="secondary" type="button" disabled>Save convergence to Data Tables</button></div>'+
 '<pre id="random-mc-output" role="status" aria-live="polite">Integrate over the box [lower, upper]^d; one bound value applies to every dimension. Convergence runs are limited to about 5 s.</pre>';
panel.append(area);
const select=$('random-distribution'),out=$('random-output'),mcOut=$('random-mc-output'),canvas=$('random-canvas');let last=null,lastConv=null;
for(const [key,spec] of Object.entries(DISTRIBUTIONS)){const o=document.createElement('option');o.value=key;o.textContent=spec.label;select.append(o);}
select.value='normal';
const syncParams=()=>{const spec=DISTRIBUTIONS[select.value];[1,2].forEach(k=>{const p=spec.params[k-1],label=$('random-p'+k+'-label'),input=$('random-p'+k);label.hidden=!p;if(p){label.firstChild.textContent=p[1];input.value=p[2];input.dataset.param=p[0];}});};
const invalidate=()=>{last=null;$('random-to-table').disabled=true;out.classList.remove('error');};
const invalidateMc=()=>{lastConv=null;$('random-mc-to-table').disabled=true;mcOut.classList.remove('error');};
select.addEventListener('change',()=>{syncParams();invalidate();});syncParams();
for(const input of area.querySelectorAll('input')){const fn=input.id.startsWith('random-mc')?invalidateMc:invalidate;input.addEventListener('input',fn);}
$('random-mc-method').addEventListener('change',invalidateMc);
function draw(result){
 const ctx=canvas.getContext&&canvas.getContext('2d');if(!ctx)return;const W=canvas.width,H=canvas.height,v=result.values;
 let lo=result.min,hi=result.max,bins;
 if(result.discrete&&hi-lo<=60){bins=hi-lo+1;hi=lo+bins;}else{bins=Math.max(5,Math.min(50,Math.round(Math.sqrt(v.length))));if(hi===lo)hi=lo+1;}
 const counts=new Array(bins).fill(0),w=(hi-lo)/bins;for(const x of v)counts[Math.min(bins-1,Math.floor((x-lo)/w))]++;
 const top=Math.max(...counts),bw=(W-20)/bins;ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
 ctx.fillStyle='#4f63d2';counts.forEach((c,i)=>{const h=(H-30)*c/top;ctx.fillRect(10+i*bw,H-20-h,Math.max(1,bw-1),h);});
 ctx.fillStyle='#283752';ctx.font='11px sans-serif';ctx.fillText(fmt(result.min),10,H-6);const t=fmt(result.max);ctx.fillText(t,W-10-ctx.measureText(t).width,H-6);
 canvas.setAttribute('aria-label','Histogram of '+result.n+' '+result.label+' samples in '+bins+' bins from '+fmt(result.min)+' to '+fmt(result.max)+'; sample mean '+fmt(result.mean)+', theoretical mean '+fmt(result.theoreticalMean)+'.');
}
$('random-generate').addEventListener('click',()=>{
 try{const spec=DISTRIBUTIONS[select.value],params={};spec.params.forEach((p,i)=>{params[p[0]]=$('random-p'+(i+1)).value;});
  last=sample({distribution:select.value,params,n:$('random-n').value,seed:$('random-seed').value});
  out.classList.remove('error');
  out.textContent=last.label+' · N = '+last.n+' · seed '+last.seed+'\nSample mean = '+fmt(last.mean)+' (theory '+fmt(last.theoreticalMean)+')\nSample variance = '+fmt(last.variance)+' (theory '+fmt(last.theoreticalVariance)+')\nRange '+fmt(last.min)+' … '+fmt(last.max)+'\nFirst values: '+last.values.slice(0,8).map(fmt).join(', ')+'\n'+last.generator+'. '+last.note;
  draw(last);$('random-to-table').disabled=false;
 }catch(err){invalidate();out.classList.add('error');out.textContent=err.message+' Correct the input and generate again.';canvas.setAttribute('aria-label','Sample histogram: not generated because of an input error');}
});
$('random-to-table').addEventListener('click',()=>{try{if(!last)throw Error('Generate samples first.');M.dataTables.importData(toTable(last),'Random_'+last.distribution);if(M.advanced?.mode)M.advanced.mode('data');}catch(err){out.classList.add('error');out.textContent=err.message;}});
const mcInput=()=>({expression:$('random-mc-expression').value,dimension:$('random-mc-dimension').value,lower:$('random-mc-lower').value,upper:$('random-mc-upper').value,seed:$('random-seed').value});
$('random-mc-run').addEventListener('click',()=>{
 try{const r=integrate({...mcInput(),n:$('random-mc-n').value,method:$('random-mc-method').value});invalidateMc();
  mcOut.textContent='∫ ≈ '+fmt(r.estimate)+(r.standardError!==null?' ± '+fmt(r.standardError)+' (1 SE)':'')+'\nMethod: '+r.method+' · N = '+r.n+(r.truncated?' (time budget reached before '+r.requested+')':'')+' · d = '+r.dimension+' · box volume '+fmt(r.volume)+'\n'+r.note;
 }catch(err){invalidateMc();mcOut.classList.add('error');mcOut.textContent=err.message+' Correct the input and run again.';}
});
$('random-mc-convergence').addEventListener('click',()=>{
 try{const r=convergence({...mcInput(),scramble:$('random-mc-method').value==='halton-shift'});invalidateMc();lastConv=r;
  mcOut.textContent='N | plain MC ± SE | Halton'+(r.scramble?' (shifted)':'')+'\n'+r.rows.map(x=>x.n+' | '+fmt(x.mc)+' ± '+fmt(x.standardError)+' | '+fmt(x.halton)).join('\n')+(r.skipped.length?'\nSkipped (time budget): N = '+r.skipped.join(', '):'')+'\nElapsed '+Math.round(r.milliseconds)+' ms.';
  $('random-mc-to-table').disabled=!r.rows.length;
 }catch(err){invalidateMc();mcOut.classList.add('error');mcOut.textContent=err.message+' Correct the input and run again.';}
});
$('random-mc-to-table').addEventListener('click',()=>{try{if(!lastConv)throw Error('Run the convergence table first.');M.dataTables.importData({headers:['N','plain_MC','standard_error','Halton'],rows:lastConv.rows.map(x=>[x.n,x.mc,x.standardError,x.halton])},'MC_Convergence');if(M.advanced?.mode)M.advanced.mode('data');}catch(err){mcOut.classList.add('error');mcOut.textContent=err.message;}});
})();
