/* ProMathStudio: offline optimization — dense two-phase simplex LP (Bland's rule) and bounded Nelder-Mead. */
(()=>{'use strict';
const M=window.MathStudio;if(!M)return;
const LP_LIMIT=1e9,LIMIT=1e12,MAX_LP=10,EPS=1e-9;

/* ---------- Linear programming: strict text format ----------
   First line:  max: 3x1 + 5x2      (or min:, maximize:, minimize:)
   Then one constraint per line:  2x1 - x2 <= 12   (operators <=, >=, =, ≤, ≥)
   Variables are x1..x10, implicitly x >= 0; right-hand sides are plain numbers; '#' starts a comment. */
const NUM='(?:\\d+(?:\\.\\d*)?|\\.\\d+)(?:[eE][+-]?\\d+)?';
const TERM=new RegExp('\\s*([+-])?\\s*(?:('+NUM+')\\s*\\*?\\s*)?x(\\d+)(?![\\d.])\\s*','y');
function parseLinear(source,where,coefs){
 const s=source.trim();
 if(!s)throw Error(where+': expected a linear expression such as 3x1+5x2.');
 let pos=0,count=0;
 while(pos<s.length){
  TERM.lastIndex=pos;const m=TERM.exec(s);
  if(!m)throw Error(where+': cannot read "'+s.slice(pos,pos+12).trim()+'"; use terms like 3x1, -2.5*x2 or x3.');
  if(count>0&&!m[1])throw Error(where+': terms must be separated by + or -.');
  if(!/^[1-9]\d*$/.test(m[3]))throw Error(where+': variable names are x1 to x10.');
  const index=Number(m[3]);
  if(index>MAX_LP)throw Error(where+': at most 10 variables (x1 to x10) are supported.');
  const value=(m[1]==='-'?-1:1)*(m[2]===undefined?1:Number(m[2]));
  if(!Number.isFinite(value)||Math.abs(value)>LP_LIMIT)throw Error(where+': coefficients must be finite with magnitude at most 1e9.');
  coefs.set(index,(coefs.get(index)||0)+value);
  pos=TERM.lastIndex;count++;
 }
 return coefs;
}
function parseLP(text){
 if(typeof text!=='string'||!text.trim())throw Error('Enter a linear program: an objective line such as "max: 3x1+5x2" followed by constraints.');
 if(text.length>5000)throw Error('Linear program text is limited to 5000 characters.');
 const lines=text.split(/\r?\n/).map((line,i)=>({no:i+1,text:line.replace(/#.*$/,'').trim()})).filter(l=>l.text);
 if(!lines.length)throw Error('Enter an objective line such as "max: 3x1+5x2".');
 const head=/^(max|min)(?:imi[sz]e)?\s*:(.*)$/i.exec(lines[0].text);
 if(!head)throw Error('Line '+lines[0].no+': the first line must start with "max:" or "min:".');
 const objective=parseLinear(head[2],'Objective (line '+lines[0].no+')',new Map());
 const rows=[];
 for(const line of lines.slice(1)){
  const where='Line '+line.no,ops=line.text.match(/<=|>=|=<|=>|==|≤|≥|<|>|=/g)||[];
  if(ops.length!==1)throw Error(where+': each constraint needs exactly one of <=, >= or =.');
  const op=ops[0];
  if(op==='<'||op==='>'||op==='=='||op==='=<'||op==='=>')throw Error(where+': use <=, >= or = (strict < and > are not supported).');
  const [lhs,rhs]=line.text.split(op);
  const rhsText=rhs.trim();
  if(!new RegExp('^[+-]?'+NUM+'$').test(rhsText))throw Error(where+': the right-hand side must be a single number.');
  const b=Number(rhsText);
  if(!Number.isFinite(b)||Math.abs(b)>LP_LIMIT)throw Error(where+': the right-hand side must be finite with magnitude at most 1e9.');
  rows.push({coefs:parseLinear(lhs,where,new Map()),type:op==='≤'?'<=':op==='≥'?'>=':op,b});
 }
 if(!rows.length)throw Error('Add at least one constraint line below the objective.');
 if(rows.length>MAX_LP)throw Error('At most 10 constraints are supported.');
 let n=0;for(const map of [objective,...rows.map(r=>r.coefs)])for(const k of map.keys())n=Math.max(n,k);
 const vector=map=>Array.from({length:n},(_,j)=>map.get(j+1)||0);
 return {sense:head[1].toLowerCase(),c:vector(objective),A:rows.map(r=>vector(r.coefs)),b:rows.map(r=>r.b),types:rows.map(r=>r.type)};
}
function checkProblem(p){
 if(!p||typeof p!=='object')throw Error('Provide a linear program.');
 const sense=String(p.sense||'').toLowerCase();
 if(sense!=='max'&&sense!=='min')throw Error('Sense must be "max" or "min".');
 const num=(v,label)=>{if(typeof v!=='number'||!Number.isFinite(v)||Math.abs(v)>LP_LIMIT)throw Error(label+' must be a finite number with magnitude at most 1e9.');return v;};
 if(!Array.isArray(p.c)||p.c.length<1||p.c.length>MAX_LP)throw Error('Use 1 to 10 variables.');
 const n=p.c.length,c=p.c.map((v,j)=>num(v,'Objective coefficient '+(j+1)));
 if(!Array.isArray(p.A)||!Array.isArray(p.b)||!Array.isArray(p.types)||p.A.length<1||p.A.length>MAX_LP||p.b.length!==p.A.length||p.types.length!==p.A.length)
  throw Error('Use 1 to 10 constraints with matching A rows, b values and types.');
 const A=p.A.map((row,i)=>{if(!Array.isArray(row)||row.length!==n)throw Error('Constraint '+(i+1)+' must have exactly '+n+' coefficients.');return row.map((v,j)=>num(v,'A['+(i+1)+']['+(j+1)+']'));});
 const b=p.b.map((v,i)=>num(v,'Right-hand side '+(i+1)));
 const types=p.types.map((t,i)=>{if(t!=='<='&&t!=='>='&&t!=='=')throw Error('Constraint '+(i+1)+' type must be <=, >= or =.');return t;});
 return {sense,c,A,b,types};
}
function pivot(T,z,basis,r,col){
 const W=T[r].length,p=T[r][col];
 for(let j=0;j<W;j++)T[r][j]/=p;T[r][col]=1;
 for(let i=0;i<T.length;i++){if(i===r)continue;const f=T[i][col];if(f!==0){for(let j=0;j<W;j++)T[i][j]-=f*T[r][j];T[i][col]=0;}}
 const f=z[col];if(f!==0){for(let j=0;j<W;j++)z[j]-=f*T[r][j];z[col]=0;}
 basis[r]=col;
}
function reducedCosts(T,basis,cost){
 const W=T.length?T[0].length:cost.length+1,z=new Array(W).fill(0);
 for(let j=0;j<W-1;j++)z[j]=cost[j];
 for(let i=0;i<T.length;i++){const cb=cost[basis[i]];if(cb)for(let j=0;j<W;j++)z[j]-=cb*T[i][j];}
 return z;
}
/* Bland's rule: lowest-index improving column enters; ties in the ratio test leave by lowest basic index. */
function simplexPhase(T,basis,cost,allowed,state){
 const z=reducedCosts(T,basis,cost),W=z.length;
 for(;;){
  let enter=-1;for(let j=0;j<W-1;j++)if(allowed(j)&&z[j]<-EPS){enter=j;break;}
  if(enter<0)return {status:'optimal',value:-z[W-1]};
  let leave=-1,best=Infinity;
  for(let i=0;i<T.length;i++){
   const a=T[i][enter];if(a<=EPS)continue;
   const ratio=Math.max(0,T[i][W-1])/a;
   if(leave<0||ratio<best-1e-12*(1+Math.abs(best))){best=ratio;leave=i;}
   else if(Math.abs(ratio-best)<=1e-12*(1+Math.abs(best))&&basis[i]<basis[leave]){leave=i;}
  }
  if(leave<0)return {status:'unbounded',column:enter};
  if(++state.iterations>5000)throw Error('Simplex pivot budget exceeded (5000); the problem may be badly scaled.');
  pivot(T,z,basis,leave,enter);
 }
}
function linprog(problem){
 const p=typeof problem==='string'?parseLP(problem):checkProblem(problem&&typeof problem.text==='string'?parseLP(problem.text):problem);
 const {sense,c,A,b,types}=p,n=c.length,m=A.length;
 // Normalise every row to a non-negative right-hand side.
 const rows=A.map((row,i)=>b[i]<0?{a:row.map(v=>-v),b:-b[i],type:types[i]==='<='?'>=':types[i]==='>='?'<=':'='}:{a:row.slice(),b:b[i],type:types[i]});
 const slackCount=rows.filter(r=>r.type!=='=').length,artCount=rows.filter(r=>r.type!=='<=').length;
 const slackStart=n,artStart=n+slackCount,W=artStart+artCount+1;
 const T=[],basis=[];let s=0,a=0;
 rows.forEach(r=>{
  const line=new Array(W).fill(0);r.a.forEach((v,j)=>line[j]=v);line[W-1]=r.b;
  if(r.type==='<='){line[slackStart+s]=1;basis.push(slackStart+s);s++;}
  else{if(r.type==='>='){line[slackStart+s]=-1;s++;}line[artStart+a]=1;basis.push(artStart+a);a++;}
  T.push(line);
 });
 const state={iterations:0},scale=1+b.reduce((t,v)=>t+Math.abs(v),0);
 let phase1Iterations=0,removedRows=0;
 if(artCount){
  const cost1=new Array(W-1).fill(0);for(let j=artStart;j<W-1;j++)cost1[j]=1;
  const r1=simplexPhase(T,basis,cost1,()=>true,state);phase1Iterations=state.iterations;
  if(r1.value>1e-8*scale)return finish({status:'infeasible',message:'Infeasible: no x ≥ 0 satisfies all constraints (phase-1 infeasibility '+r1.value.toExponential(3)+').'});
  // Drive remaining (zero-level) artificials out of the basis; drop redundant equality rows.
  for(let i=T.length-1;i>=0;i--){
   if(basis[i]<artStart)continue;
   let col=-1;for(let j=0;j<artStart;j++)if(Math.abs(T[i][j])>EPS){col=j;break;}
   if(col>=0)pivot(T,new Array(W).fill(0),basis,i,col);else{T.splice(i,1);basis.splice(i,1);removedRows++;}
  }
 }
 const cost2=new Array(W-1).fill(0);c.forEach((v,j)=>cost2[j]=sense==='max'?-v:v);
 const r2=simplexPhase(T,basis,cost2,j=>j<artStart,state);
 if(r2.status==='unbounded')return finish({status:'unbounded',message:'Unbounded: the objective can be '+(sense==='max'?'increased':'decreased')+' without limit along a feasible ray (x'+(r2.column<n?r2.column+1:'slack')+' enters with no blocking constraint).'});
 const x=new Array(n).fill(0);basis.forEach((col,i)=>{if(col<n)x[col]=T[i][W-1];});
 // Verify the returned point against the original constraints before reporting it.
 const tolFor=i=>1e-7*(1+Math.abs(b[i])+A[i].reduce((t,v,j)=>t+Math.abs(v*x[j]),0));
 for(let j=0;j<n;j++){if(x[j]<-1e-9*scale)throw Error('Numerical verification failed: x'+(j+1)+' is negative.');if(x[j]<0||Math.abs(x[j])<1e-13)x[j]=0;}
 const constraints=A.map((row,i)=>{
  const activity=row.reduce((t,v,j)=>t+v*x[j],0),residual=activity-b[i],tol=tolFor(i);
  const slack=types[i]==='<='?b[i]-activity:types[i]==='>='?activity-b[i]:Math.abs(residual);
  if(slack<-tol||(types[i]==='='&&slack>tol))throw Error('Numerical verification failed on constraint '+(i+1)+' (residual '+residual.toExponential(3)+').');
  return {index:i+1,type:types[i],rhs:b[i],activity,slack:Math.abs(slack)<=tol?0:slack,binding:Math.abs(slack)<=tol};
 });
 const objective=c.reduce((t,v,j)=>t+v*x[j],0);
 return finish({status:'optimal',x,objective,constraints,binding:constraints.filter(r=>r.binding).map(r=>r.index),
  maxViolation:Math.max(0,...constraints.map(r=>r.type==='='?r.slack:Math.max(0,-r.slack)))});
 function finish(out){return Object.assign({type:'linprog',sense,variables:n,constraintCount:m,iterations:state.iterations,phase1Iterations,removedRedundantRows:removedRows,
  method:'Dense two-phase simplex with Bland\'s anti-cycling rule (x ≥ 0)',
  note:'Floating-point simplex with tolerance 1e-9; the reported point is re-checked against the original constraints. Alternative optima may exist.'},out);}
}

/* ---------- Nelder-Mead with projection onto optional box bounds ---------- */
function finiteNumber(v,label){
 if(v===null||v===undefined||String(v).trim()==='')throw Error(label+' is required.');
 const n=Number(v);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(label+' must be finite with magnitude at most 1e12.');return n;
}
function integerIn(v,label,lo,hi){const n=finiteNumber(v,label);if(!Number.isInteger(n)||n<lo||n>hi)throw Error(label+' must be an integer from '+lo+' to '+hi+'.');return n;}
function parseVector(value,label,{allowInfinite=false,length=null}={}){
 let items=value;
 if(typeof value==='string'){const t=value.trim();items=t?t.split(/\s*[,;]\s*|\s+/):[];}
 if(!Array.isArray(items))throw Error(label+' must be a comma-separated list of numbers.');
 const out=items.map((v,i)=>{
  const where=label+' entry '+(i+1);
  if(allowInfinite&&(v===null||v===Infinity||v===-Infinity||(typeof v==='string'&&/^([+-]?inf(inity)?|∞|-∞|\+∞)?$/i.test(v.trim()))))
   return typeof v==='number'?v:null;
  if(typeof v==='string'&&!new RegExp('^[+-]?'+NUM+'$').test(v.trim()))throw Error(where+' is not a number.');
  return finiteNumber(v,where);
 });
 if(length!==null&&out.length!==length)throw Error(label+' must have exactly '+length+' entries (one per variable).');
 return out;
}
function minimizeFunction(f,start,options={}){
 const n=start.length;
 const lower=options.lower||new Array(n).fill(-Infinity),upper=options.upper||new Array(n).fill(Infinity);
 const xTol=options.xTol??1e-8,fTol=options.fTol??1e-10,maxIterations=options.maxIterations??4000,maxEvaluations=options.maxEvaluations??8000;
 const adaptive=options.adaptive!==false,restarts=options.restarts??1;
 const alpha=1,gamma=adaptive?1+2/n:2,rho=adaptive?0.75-1/(2*n):0.5,sigma=adaptive?1-1/n:0.5;
 const project=p=>p.map((v,i)=>Math.min(upper[i],Math.max(lower[i],v)));
 let evaluations=0,rejected=0,iterations=0;const BUDGET={};
 const value=p=>{
  if(evaluations>=maxEvaluations)throw BUDGET;evaluations++;
  let y;try{y=f(p);}catch(e){y=Infinity;}
  if(!Number.isFinite(y)||Math.abs(y)>LIMIT){rejected++;return Infinity;}
  if(y<best.f)best={x:p.slice(),f:y};return y;
 };
 const x0=project(start.slice());
 let f0;try{f0=f(x0);}catch(e){f0=NaN;}evaluations++;
 if(!Number.isFinite(f0)||Math.abs(f0)>LIMIT)throw Error('The objective must be finite (magnitude ≤ 1e12) at the start point.');
 let best={x:x0,f:f0},status='converged',runs=0;
 const run=(origin,fOrigin)=>{
  const simplex=[{x:origin,f:fOrigin}];
  for(let i=0;i<n;i++){
   const step=origin[i]!==0?0.05*Math.abs(origin[i]):0.00025,v=origin.slice();
   v[i]=origin[i]+step<=upper[i]?origin[i]+step:origin[i]-step>=lower[i]?origin[i]-step:(origin[i]-lower[i]>upper[i]-origin[i]?lower[i]:upper[i]);
   simplex.push({x:v,f:value(v)});
  }
  for(;;){
   simplex.sort((p,q)=>p.f-q.f);
   const b=simplex[0],scaleX=Math.max(1,...b.x.map(Math.abs));
   let size=0,spread=0;for(const v of simplex.slice(1)){spread=Math.max(spread,Math.abs(v.f-b.f));for(let i=0;i<n;i++)size=Math.max(size,Math.abs(v.x[i]-b.x[i]));}
   if(size<=xTol*scaleX&&spread<=fTol*Math.max(1,Math.abs(b.f)))return 'converged';
   if(iterations>=maxIterations)return 'iteration budget exhausted';
   iterations++;
   const worst=simplex[n],centroid=new Array(n).fill(0);
   for(let k=0;k<n;k++)for(let i=0;i<n;i++)centroid[i]+=simplex[k].x[i]/n;
   const along=(t,p)=>project(centroid.map((c,i)=>c+t*(p[i]-c)));
   const xr=along(-alpha,worst.x),fr=value(xr);
   if(fr<b.f){const xe=along(-alpha*gamma,worst.x),fe=value(xe);simplex[n]=fe<fr?{x:xe,f:fe}:{x:xr,f:fr};continue;}
   if(fr<simplex[n-1].f){simplex[n]={x:xr,f:fr};continue;}
   if(fr<worst.f){const xc=along(-alpha*rho,worst.x),fc=value(xc);if(fc<=fr){simplex[n]={x:xc,f:fc};continue;}}
   else{const xc=along(rho,worst.x),fc=value(xc);if(fc<worst.f){simplex[n]={x:xc,f:fc};continue;}}
   for(let k=1;k<=n;k++){const xs=project(b.x.map((v,i)=>v+sigma*(simplex[k].x[i]-v)));simplex[k]={x:xs,f:value(xs)};}
  }
 };
 try{
  for(let r=0;r<=restarts;r++){
   runs++;const before=best.f;
   status=run(best.x,best.f);
   if(status!=='converged')break;
   if(r>0&&!(best.f<before-fTol*Math.max(1,Math.abs(before))))break;
  }
 }catch(e){if(e!==BUDGET)throw e;status='evaluation budget exhausted';}
 return {x:best.x,f:best.f,status,converged:status==='converged',iterations,evaluations,rejectedEvaluations:rejected,runs,
  gradient:gradientDiagnostic(f,best.x,best.f,lower,upper)};
}
function gradientDiagnostic(f,x,fx,lower,upper){
 const n=x.length,g=new Array(n),active=[];let evaluations=0;
 for(let i=0;i<n;i++){
  const h=1e-6*Math.max(1,Math.abs(x[i])),at=(t)=>{const p=x.slice();p[i]=t;evaluations++;return f(p);};
  let gi;
  try{
   if(x[i]+h<=upper[i]&&x[i]-h>=lower[i])gi=(at(x[i]+h)-at(x[i]-h))/(2*h);
   else if(x[i]-h>=lower[i])gi=(fx-at(x[i]-h))/h;
   else gi=(at(x[i]+h)-fx)/h;
  }catch(e){gi=NaN;}
  g[i]=gi;
  const tolB=1e-9*Math.max(1,Math.abs(x[i]));
  if(x[i]<=lower[i]+tolB)active.push({variable:i,bound:'lower'});
  if(x[i]>=upper[i]-tolB)active.push({variable:i,bound:'upper'});
 }
 if(!g.every(Number.isFinite))return {gradient:null,norm:null,projectedNorm:null,activeBounds:active,evaluations};
 const projected=g.map((v,i)=>{const lo=active.some(a=>a.variable===i&&a.bound==='lower'),hi=active.some(a=>a.variable===i&&a.bound==='upper');return (lo&&v>0)||(hi&&v<0)?0:v;});
 const norm=v=>Math.sqrt(v.reduce((t,u)=>t+u*u,0));
 return {gradient:g,norm:norm(g),projectedNorm:norm(projected),activeBounds:active,evaluations};
}
function nelderMead({expression='(x-1)^2+(y-2)^2',start=[0,0],lower=null,upper=null,xTol=1e-8,fTol=1e-10,maxIterations=4000,maxEvaluations=8000,adaptive=true,restarts=1}={}){
 if(!M.numerical?.evaluate)throw Error('The numerical evaluator is unavailable.');
 expression=String(expression).trim();
 if(!expression||expression.length>1000)throw Error('Enter an objective expression of 1–1000 characters.');
 const x0=parseVector(start,'Start point');
 if(x0.length<2||x0.length>3)throw Error('Start point must have 2 (x, y) or 3 (x, y, z) entries.');
 const n=x0.length,names=['x','y','z'].slice(0,n);
 const bound=(v,label,fallback)=>{if(v===null||v===undefined||(typeof v==='string'&&!v.trim()))return new Array(n).fill(fallback);
  return parseVector(v,label,{allowInfinite:true,length:n}).map(u=>u===null?fallback:u);};
 const lo=bound(lower,'Lower bounds',-Infinity),hi=bound(upper,'Upper bounds',Infinity);
 for(let i=0;i<n;i++){
  if(lo[i]===Infinity||hi[i]===-Infinity)throw Error('Bounds for '+names[i]+' are inverted.');
  if(!(hi[i]>lo[i]))throw Error('Upper bound for '+names[i]+' must exceed its lower bound.');
 }
 xTol=finiteNumber(xTol,'Simplex size tolerance');if(xTol<1e-14||xTol>1e-2)throw Error('Simplex size tolerance must be between 1e-14 and 1e-2.');
 fTol=finiteNumber(fTol,'Function spread tolerance');if(fTol<1e-16||fTol>1e-2)throw Error('Function spread tolerance must be between 1e-16 and 1e-2.');
 maxIterations=integerIn(maxIterations,'Maximum iterations',10,20000);
 maxEvaluations=integerIn(maxEvaluations,'Maximum evaluations',20,50000);
 const f=p=>M.numerical.evaluate(expression,Object.fromEntries(names.map((k,i)=>[k,p[i]])));
 const projectedStart=x0.map((v,i)=>Math.min(hi[i],Math.max(lo[i],v)));
 try{const y=f(projectedStart);if(!Number.isFinite(y))throw Error('non-finite value');}
 catch(e){throw Error('Objective could not be evaluated at the start point: '+e.message);}
 const r=minimizeFunction(f,x0,{lower:lo,upper:hi,xTol,fTol,maxIterations,maxEvaluations,adaptive,restarts:integerIn(restarts,'Restarts',0,5)});
 return Object.assign(r,{type:'nelder-mead',expression,variables:names,lower:lo,upper:hi,start:x0,startProjected:projectedStart.some((v,i)=>v!==x0[i]),
  method:'Nelder-Mead simplex'+(adaptive?' (adaptive Gao-Han parameters)':'')+(lo.some(Number.isFinite)||hi.some(Number.isFinite)?' with box bounds by projection':''),
  note:'Derivative-free local search: convergence is judged by simplex size and f-spread. The finite-difference gradient norm is a heuristic diagnostic, not a certificate of a (global) minimum.'});
}
M.optimization=Object.freeze({linprog,parseLP,nelderMead,minimizeFunction,parseVector});

/* ---------- UI (Numerical panel) ---------- */
const panel=document.getElementById('numerical-panel');
if(!panel||!M.dataTables||!M.numerical?.evaluate)return;
const $=id=>document.getElementById(id),fmt=v=>Number.isFinite(v)?Number(v.toPrecision(12)).toString():String(v);
const area=document.createElement('details');area.id='optimization-details';
area.innerHTML='<summary>Optimization · linear programming &amp; Nelder-Mead</summary>'+
 '<h4 id="opt-lp-heading">Linear program (x ≥ 0)</h4>'+
 '<p class="graph-data-muted" id="opt-lp-help">First line "max:" or "min:" with a linear objective in x1…x10; then one constraint per line using &lt;=, &gt;= or = and a numeric right-hand side. Up to 10 variables and 10 constraints. "#" starts a comment. Ctrl+Enter solves.</p>'+
 '<label for="opt-lp-text">LP text</label>'+
 '<textarea id="opt-lp-text" rows="6" spellcheck="false" aria-describedby="opt-lp-help">max: 3x1 + 5x2\nx1 &lt;= 4\n2x2 &lt;= 12\n3x1 + 2x2 &lt;= 18</textarea>'+
 '<div class="data-toolbar"><button id="opt-lp-run" class="primary" type="button">Solve LP</button>'+
 '<button id="opt-lp-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="opt-lp-output" class="opt-output" role="status" aria-live="polite">Enter a linear program.</pre>'+
 '<h4>Minimize f(x, y[, z]) · Nelder-Mead</h4>'+
 '<p class="graph-data-muted">Local derivative-free minimization. Use 2 or 3 start values; leave bounds empty (or write -inf / inf) for unbounded variables.</p>'+
 '<div class="num-fields"><label>Objective f(x, y[, z])<input id="opt-nm-expression" value="100*(y-x^2)^2+(1-x)^2" spellcheck="false"></label>'+
 '<label>Start point (comma-separated)<input id="opt-nm-start" value="-1.2, 1" spellcheck="false"></label>'+
 '<label>Lower bounds (optional)<input id="opt-nm-lower" value="" placeholder="e.g. 0, -inf" spellcheck="false"></label>'+
 '<label>Upper bounds (optional)<input id="opt-nm-upper" value="" placeholder="e.g. 2, inf" spellcheck="false"></label>'+
 '<label>Simplex size tolerance<input id="opt-nm-xtol" type="number" step="any" value="0.00000001"></label>'+
 '<label>f-spread tolerance<input id="opt-nm-ftol" type="number" step="any" value="0.0000000001"></label>'+
 '<label>Maximum evaluations (20–50000)<input id="opt-nm-maxeval" type="number" step="1" min="20" max="50000" value="8000"></label></div>'+
 '<div class="data-toolbar"><button id="opt-nm-run" class="primary" type="button">Minimize</button>'+
 '<button id="opt-nm-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="opt-nm-output" class="opt-output" role="status" aria-live="polite">Enter an objective and start point.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#optimization-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px;max-width:100%;box-sizing:border-box}'+
 '#optimization-details summary{cursor:pointer;color:#3c50ae;font-weight:750;min-height:40px;display:flex;align-items:center}'+
 '#optimization-details h4{margin:14px 0 6px;font-size:14px;color:#33415e}'+
 '#optimization-details>label{display:block;font-size:12px;font-weight:700;color:#566784;margin:6px 0 4px}'+
 '#opt-lp-text{width:100%;max-width:100%;box-sizing:border-box;min-height:120px;padding:9px;border:1px solid #cdd8ec;border-radius:9px;font:13px/1.5 Consolas,monospace;resize:vertical}'+
 '#optimization-details .data-toolbar{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}'+
 '#optimization-details button{min-height:40px;min-width:40px}'+
 '.opt-output{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%;box-sizing:border-box;padding:12px;background:white;border:1px solid #dce5f3;border-radius:10px;font:12px/1.6 Consolas,monospace}'+
 '.opt-output.error{color:#a82241;background:#fff2f4}.opt-output.warn{color:#8a5a00;background:#fff8e8}';
document.head.append(style);
let lastLP=null,lastNM=null;
const show=(id,text,cls)=>{const o=$(id);o.classList.remove('error','warn');if(cls)o.classList.add(cls);o.textContent=text;};
const invalidateLP=()=>{lastLP=null;$('opt-lp-to-table').disabled=true;$('opt-lp-output').classList.remove('error','warn');};
const invalidateNM=()=>{lastNM=null;$('opt-nm-to-table').disabled=true;$('opt-nm-output').classList.remove('error','warn');};
$('opt-lp-text').addEventListener('input',invalidateLP);
$('opt-lp-text').addEventListener('keydown',e=>{if(e.key==='Enter'&&(e.ctrlKey||e.metaKey)){e.preventDefault();$('opt-lp-run').click();}});
for(const input of area.querySelectorAll('.num-fields input')){input.addEventListener('input',invalidateNM);input.addEventListener('change',invalidateNM);}
$('opt-lp-run').addEventListener('click',()=>{
 invalidateLP();
 try{
  const r=linprog($('opt-lp-text').value);
  if(r.status!=='optimal'){show('opt-lp-output',r.method+'\n'+r.message+'\nPivots: '+r.iterations,'warn');return;}
  lastLP=r;
  show('opt-lp-output',r.method+'\nStatus: optimal\n'+r.x.map((v,j)=>'x'+(j+1)+' = '+fmt(v)).join('\n')+
   '\nObjective ('+r.sense+') = '+fmt(r.objective)+
   '\nConstraints:\n'+r.constraints.map(k=>'  #'+k.index+' '+k.type+' '+fmt(k.rhs)+': activity '+fmt(k.activity)+', slack '+fmt(k.slack)+(k.binding?' (binding)':'')).join('\n')+
   '\nBinding: '+(r.binding.length?r.binding.map(i=>'#'+i).join(', '):'none')+'; max violation '+r.maxViolation.toExponential(2)+
   '\nPivots: '+r.iterations+' (phase 1: '+r.phase1Iterations+')'+(r.removedRedundantRows?'; redundant rows removed: '+r.removedRedundantRows:'')+'\n'+r.note);
  $('opt-lp-to-table').disabled=false;
 }catch(e){show('opt-lp-output',e.message+'\nFix the highlighted line and press Solve LP again.','error');}
});
$('opt-nm-run').addEventListener('click',()=>{
 invalidateNM();
 try{
  const r=nelderMead({expression:$('opt-nm-expression').value,start:$('opt-nm-start').value,lower:$('opt-nm-lower').value,upper:$('opt-nm-upper').value,
   xTol:$('opt-nm-xtol').value,fTol:$('opt-nm-ftol').value,maxEvaluations:$('opt-nm-maxeval').value});
  lastNM=r;const gd=r.gradient,bounded=r.lower.some(Number.isFinite)||r.upper.some(Number.isFinite);
  show('opt-nm-output',r.method+'\nStatus: '+r.status+'\n'+r.variables.map((k,i)=>k+' ≈ '+fmt(r.x[i])).join('\n')+'\nf ≈ '+fmt(r.f)+
   '\nIterations: '+r.iterations+'; evaluations: '+r.evaluations+(r.rejectedEvaluations?' ('+r.rejectedEvaluations+' non-finite trial points rejected)':'')+
   '\nFinite-difference ‖∇f‖ ≈ '+(gd.norm===null?'unavailable':gd.norm.toExponential(3))+
   (bounded&&gd.projectedNorm!==null?'; projected ‖∇f‖ ≈ '+gd.projectedNorm.toExponential(3):'')+
   (gd.activeBounds.length?'\nActive bounds: '+gd.activeBounds.map(a=>r.variables[a.variable]+' at '+a.bound).join(', '):'')+
   (r.startProjected?'\nStart point was projected onto the bounds.':'')+'\n'+r.note,r.converged?null:'warn');
  $('opt-nm-to-table').disabled=false;
 }catch(e){show('opt-nm-output',e.message+'\nCorrect the input and press Minimize again.','error');}
});
$('opt-lp-to-table').addEventListener('click',()=>{
 try{
  if(!lastLP)throw Error('Solve a linear program first.');
  const rows=lastLP.x.map((v,j)=>['x'+(j+1),v,'','']).concat([['objective',lastLP.objective,'','']],
   lastLP.constraints.map(k=>['constraint '+k.index+' ('+k.type+' '+k.rhs+')',k.activity,k.slack,k.binding?'yes':'no']));
  M.dataTables.importData({headers:['name','value','slack','binding'],rows},'Optimization_LP');M.advanced?.mode?.('data');
 }catch(e){show('opt-lp-output',e.message,'error');}
});
$('opt-nm-to-table').addEventListener('click',()=>{
 try{
  if(!lastNM)throw Error('Run a minimization first.');
  M.dataTables.importData({headers:[...lastNM.variables,'f','status','gradient_norm'],rows:[[...lastNM.x,lastNM.f,lastNM.status,lastNM.gradient.norm??'']]},'Optimization_NelderMead');M.advanced?.mode?.('data');
 }catch(e){show('opt-nm-output',e.message,'error');}
});
})();
