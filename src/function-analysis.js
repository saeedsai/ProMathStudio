/* ProMathStudio: numerical inequality solving and sampled real-function domain analysis on [a,b].
   Reuses the shared safe evaluator, scalar root finder (roots + pole/jump diagnostics) and the
   golden-section minimizer. No eval/Function; all results are numerical estimates, not proofs. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');
if(!M?.numerical?.evaluate||!M?.numerical?.scalarRoots||!M?.dataTables||!M?.advanced||!panel)return;
const $=id=>document.getElementById(id),LIMIT=1e12;
const OPS={'<':'<','>':'>','<=':'≤','>=':'≥','=':'=','≤':'≤','≥':'≥'};
const STRICT={'<':true,'>':true,'≤':false,'≥':false,'=':false};
function bound(value,label){
 const text=String(value??'').trim();if(!text)throw Error(label+' is required.');
 let n=Number(text);
 if(!Number.isFinite(n)){if(text.length>100)throw Error(label+' must be a finite number or constant expression.');try{n=M.numerical.evaluate(text,{});}catch{n=NaN;}}
 if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(label+' must be finite with magnitude at most 1e12 (for example 0, -5 or 2*pi).');
 return n;
}
function integer(value,min,max,label){const n=Number(value);if(!Number.isInteger(n)||n<min||n>max)throw Error(label+' must be an integer from '+min+' to '+max+'.');return n;}
/* Split "lhs op rhs" at a single top-level comparison; a bare expression means f(x) with no comparison. */
function parseComparison(input){
 const text=String(input??'').trim();
 if(!text||text.length>1000)throw Error('Enter an expression or comparison of 1–1000 characters, e.g. x^2-4 < 0.');
 if(/==|!=|<>|=<|=>/.test(text))throw Error('Use one comparison: <, <=, >, >=, ≤, ≥ or a single =.');
 const matches=[...text.matchAll(/<=|>=|≤|≥|<|>|=/g)];
 if(matches.length>1)throw Error('Use exactly one comparison operator (chained comparisons are not supported).');
 if(!matches.length)return {lhs:text,op:null,rhs:null};
 const m=matches[0],lhs=text.slice(0,m.index).trim(),rhs=text.slice(m.index+m[0].length).trim();
 if(!lhs||!rhs)throw Error('Both sides of the comparison need an expression.');
 return {lhs,op:OPS[m[0]],rhs};
}
function options(o){
 const lo=bound(o.lo??-5,'Lower bound'),hi=bound(o.hi??5,'Upper bound');
 if(!(hi>lo))throw Error('Upper bound must exceed lower bound.');
 const samples=integer(o.samples??400,20,1600,'Samples');
 const tolerance=Number(o.tolerance??1e-9);
 if(!Number.isFinite(tolerance)||tolerance<1e-12||tolerance>1e-3)throw Error('Tolerance must be between 1e-12 and 1e-3.');
 return {lo,hi,samples,tolerance};
}
const makeEval=expr=>x=>{try{const y=M.numerical.evaluate(expr,{x});return Number.isFinite(y)?y:NaN;}catch{return NaN;}};
const decimals=tol=>Math.min(15,Math.max(0,Math.ceil(-Math.log10(tol))));
const snap=(x,tol)=>{const s=Number(x.toFixed(decimals(tol)));return s===0?0:s;};
/* Shortest decimal within maxDist of x that passes accept (e.g. residual still within tolerance). */
function nice(x,maxDist,accept=()=>true){if(!Number.isFinite(x))return x;for(let k=0;k<=15;k++){const s=Number(x.toFixed(k));if(Math.abs(s-x)<=maxDist&&accept(s))return s===0?0:s;}return x;}
/* Bisect between a finite point and a nonfinite point; returns the finite-side point. */
function bisectBoundary(f,finiteX,badX,tol){
 let a=finiteX,b=badX;
 for(let i=0;i<200&&Math.abs(b-a)>tol*Math.max(1,Math.abs(a))/4;i++){const m=a+(b-a)/2;if(m===a||m===b)break;if(Number.isFinite(f(m)))a=m;else b=m;}
 return {finite:a,bad:b};
}
/* Heuristic: |f| keeps changing at comparable rate as the distance to the boundary shrinks
   geometrically (log or pole-like growth) → treat the limit as unbounded. */
function unboundedTowards(f,edge,dir,h){
 const v=[1e-2,1e-4,1e-6].map(d=>f(edge+dir*d*h));
 if(v.some(y=>!Number.isFinite(y)))return true;
 const d1=Math.abs(v[1]-v[0]),d2=Math.abs(v[2]-v[1]);
 return d2>0.8*d1&&d2>1e-9*Math.max(1,Math.abs(v[2]));
}
/* Sampled real domain of f: finite real evaluation, boundaries refined by bisection. */
function domainOf(f,lo,hi,samples,tol){
 const h=(hi-lo)/samples,xs=[],ys=[];
 for(let k=0;k<=samples;k++){const x=k===samples?hi:lo+k*h;xs.push(x);ys.push(f(x));}
 const intervals=[],excludedPoints=[];let start=null;
 const closedAt=(edge,inside,dir)=>{const s=snap(edge,tol);if(Math.abs(s-edge)<=Math.max(10*tol,1e-12)&&Number.isFinite(f(s)))return {x:s,closed:true};
  const closed=!unboundedTowards(f,edge,dir,h)&&Number.isFinite(f(edge))&&!inside;
  return {x:closed?edge:nice(edge,Math.max(10*tol,1e-12)),closed};};
 for(let k=0;k<=samples;k++){
  const ok=Number.isFinite(ys[k]);
  if(ok&&start===null){
   if(k===0)start={x:lo,closed:true};
   else{const r=bisectBoundary(f,xs[k],xs[k-1],tol);start=closedAt(r.finite,false,1);start.gap=r.bad;}
  }
  if(!ok&&start!==null){
   const r=bisectBoundary(f,xs[k-1],xs[k],tol);const end=closedAt(r.finite,false,-1);
   intervals.push({lo:start.x,hi:end.x,loClosed:start.closed,hiClosed:end.closed});start=null;
  }
 }
 if(start!==null)intervals.push({lo:start.x,hi:hi,loClosed:start.closed,hiClosed:true});
 // Two pieces separated by a gap narrower than tolerance exclude a single point (e.g. 1/(x-1) at 1).
 for(let i=1;i<intervals.length;i++){const p=intervals[i-1],q=intervals[i];
  if(q.lo-p.hi<=Math.max(100*tol*Math.max(1,Math.abs(q.lo)),1e-9)){p.hiClosed=false;q.loClosed=false;const mid=snap((p.hi+q.lo)/2,tol);p.hi=mid;q.lo=mid;excludedPoints.push(mid);}}
 return {intervals:intervals.filter(I=>I.hi>I.lo||(I.loClosed&&I.hiClosed)),excludedPoints,xs,ys,h};
}
const fmt=x=>{if(!Number.isFinite(x))return String(x);const r=Number(x.toPrecision(10));return Object.is(r,-0)?'0':String(r);};
function intervalText(I){if(I.lo===I.hi)return '{'+fmt(I.lo)+'}';return (I.loClosed?'[':'(')+fmt(I.lo)+', '+fmt(I.hi)+(I.hiClosed?']':')');}
function setText(list){return list.length?list.map(intervalText).join(' ∪ '):'∅';}
const satisfies=(v,op,tol)=>{if(!Number.isFinite(v))return false;const zero=Math.abs(v)<=tol;
 return op==='<'?v<0&&!zero:op==='>'?v>0&&!zero:op==='≤'?v<0||zero:op==='≥'?v>0||zero:zero;};
const niceRoots=(list,g,tol)=>list.map(x=>nice(x,1e-7*Math.max(1,Math.abs(x)),s=>Math.abs(g(s))<=tol));
const nicePoles=list=>list.map(x=>nice(x,1e-9*Math.max(1,Math.abs(x))));
function dedupeBreaks(points,tol){points.sort((a,b)=>a.x-b.x);const out=[];
 for(const p of points){const q=out[out.length-1];if(q&&Math.abs(p.x-q.x)<=Math.max(1e-7,1e-7*Math.abs(p.x))){if(p.kind!=='root')q.kind=p.kind;}else out.push({...p});}return out;}
/* Solve lhs op rhs on [lo,hi] as a union of intervals. */
function solve({expression='x^2-4 < 0',lo=-5,hi=5,samples=400,tolerance=1e-9}={}){
 const cmp=parseComparison(expression);if(!cmp.op)throw Error('Enter a comparison such as x^2-4 < 0 (operators <, <=, >, >=, =).');
 const o=options({lo,hi,samples,tolerance});
 const residual='('+cmp.lhs+')-('+cmp.rhs+')',h=makeEval(residual);
 const dom=domainOf(h,o.lo,o.hi,o.samples,o.tolerance);
 if(!dom.intervals.length)throw Error('The comparison is not real-valued and finite anywhere on the sampled interval.');
 const roots=M.numerical.scalarRoots(residual,'x',o.lo,o.hi,{samples:o.samples,tolerance:o.tolerance});
 const zeros=niceRoots(roots.roots,h,o.tolerance);
 const poles=nicePoles(roots.rejectedSignChanges.filter(r=>r.kind==='possible-pole').map(r=>r.x));
 const jumps=roots.rejectedSignChanges.filter(r=>r.kind==='possible-jump').map(r=>r.x);
 const solution=[];let uncertain=0;
 const push=I=>{const last=solution[solution.length-1];
  if(last&&last.hi===I.lo&&(last.hiClosed||I.loClosed)){last.hi=I.hi;last.hiClosed=I.hiClosed;}else solution.push({...I});};
 for(const D of dom.intervals){
  if(D.lo===D.hi){if(satisfies(h(D.lo),cmp.op,o.tolerance))push({...D});continue;}
  const inner=dedupeBreaks([...zeros.map(x=>({x,kind:'root'})),...poles.map(x=>({x,kind:'pole'})),...jumps.map(x=>({x,kind:'jump'}))]
   .filter(p=>p.x>D.lo&&p.x<D.hi),o.tolerance);
  const pts=[{x:D.lo,kind:'edge',closed:D.loClosed},...inner,{x:D.hi,kind:'edge',closed:D.hiClosed}];
  const pointOk=p=>p.kind==='pole'?false:p.kind==='edge'?p.closed&&satisfies(h(p.x),cmp.op,o.tolerance):p.kind==='root'?!STRICT[cmp.op]:satisfies(h(p.x),cmp.op,o.tolerance);
  for(let i=0;i<pts.length-1;i++){
   const a=pts[i],b=pts[i+1];
   // Classify the open piece from the grid samples inside it plus its midpoint.
   const vals=[h(a.x+(b.x-a.x)/2)];for(let k=0;k<dom.xs.length;k++)if(dom.xs[k]>a.x&&dom.xs[k]<b.x&&Number.isFinite(dom.ys[k]))vals.push(dom.ys[k]);
   const okCount=vals.filter(v=>satisfies(v,cmp.op,o.tolerance)).length,finiteCount=vals.filter(Number.isFinite).length;
   if(okCount&&okCount<finiteCount)uncertain++;
   const pieceOk=finiteCount>0&&okCount*2>finiteCount;
   const aOk=pointOk(a),bOk=pointOk(b);
   if(pieceOk)push({lo:a.x,hi:b.x,loClosed:aOk,hiClosed:bOk});
   else{if(i===0&&aOk)push({lo:a.x,hi:a.x,loClosed:true,hiClosed:true});if(bOk)push({lo:b.x,hi:b.x,loClosed:true,hiClosed:true});}
  }
 }
 // Remove point sets swallowed by an adjacent closed interval.
 const intervals=solution.filter((I,i)=>!(I.lo===I.hi&&solution.some((J,j)=>j!==i&&J.lo<=I.lo&&J.hi>=I.hi&&J.hi>J.lo&&((J.lo<I.lo&&J.hi>I.lo)||(J.lo===I.lo&&J.loClosed)||(J.hi===I.lo&&J.hiClosed)))));
 return {type:'inequality-solution',expression:String(expression).trim(),lhs:cmp.lhs,operator:cmp.op,rhs:cmp.rhs,domain:[o.lo,o.hi],
  samples:o.samples,tolerance:o.tolerance,intervals,notation:setText(intervals),roots:zeros,poles,jumps,
  domainIntervals:dom.intervals,excludedPoints:dom.excludedPoints,rootStatus:roots.rootStatus,uncertainPieces:uncertain,
  note:'Numerical solution on a '+o.samples+'-interval grid: endpoints come from the shared root finder (absolute residual ≤ '+o.tolerance+') and bisected domain boundaries. Pole/jump points are excluded by heuristic classification. Features narrower than the grid can be missed; this is not a symbolic proof.'+(uncertain?' '+uncertain+' piece(s) had mixed signs, so some crossings may be unresolved.':'')};
}
/* Sampled domain, zeros, poles, extrema, range, monotonicity and symmetry of f on [lo,hi]. */
function analyze({expression='x^3-3*x',lo=-3,hi=3,samples=400,tolerance=1e-9}={}){
 const fx=parseComparison(expression).lhs;
 const o=options({lo,hi,samples,tolerance}),f=makeEval(fx);
 const dom=domainOf(f,o.lo,o.hi,o.samples,o.tolerance);
 if(!dom.intervals.length)throw Error('f(x) is not real-valued and finite anywhere on the sampled interval.');
 const roots=M.numerical.scalarRoots(fx,'x',o.lo,o.hi,{samples:o.samples,tolerance:o.tolerance});
 const zeros=niceRoots(roots.roots,f,o.tolerance);
 const poles=nicePoles(roots.rejectedSignChanges.filter(r=>r.kind==='possible-pole').map(r=>r.x));
 const jumps=roots.rejectedSignChanges.filter(r=>r.kind==='possible-jump').map(r=>r.x);
 // Boundaries where |f| grows without bound (e.g. 1/x² at 0, ln at 0+) are also reported as poles.
 for(const D of dom.intervals){for(const [edge,dir,closed] of [[D.lo,1,D.loClosed],[D.hi,-1,D.hiClosed]]){
  if(!closed&&edge>o.lo&&edge<o.hi&&unboundedTowards(f,edge,dir,dom.h)&&!poles.some(p=>Math.abs(p-edge)<1e-6*Math.max(1,Math.abs(edge))))poles.push(nice(Number(edge.toPrecision(12)),Math.max(10*o.tolerance,1e-12)));}}
 poles.sort((a,b)=>a-b);
 const {xs,ys}=dom,step=dom.h,dx=x=>{const e=Math.max(1e-6,1e-6*Math.abs(x))*Math.max(1,step);const a=f(x-e),b=f(x+e);return (b-a)/(2*e);};
 const near=(x,list)=>list.some(p=>Math.abs(p-x)<=2*step);
 const ds=xs.map((x,k)=>Number.isFinite(ys[k])?dx(x):NaN);
 const extrema=[];
 const objective=(kind)=>kind==='minimum'?fx:'-('+fx+')';
 for(let k=1;k<xs.length;k++){
  const a=ds[k-1],b=ds[k];if(!Number.isFinite(a)||!Number.isFinite(b))continue;
  const kind=a<0&&b>=0?'minimum':a>0&&b<=0?'maximum':null;if(!kind)continue;
  const L=xs[Math.max(0,k-2)],R=xs[Math.min(xs.length-1,k+1)];
  if(near((L+R)/2,poles)||near((L+R)/2,jumps))continue;
  try{const r=M.minimizeTools?M.minimizeTools.minimize({expression:objective(kind),lo:L,hi:R,tolerance:1e-9,maxIterations:400}):null;
   if(!r||r.x===L||r.x===R)continue;
   const sign=kind==='minimum'?1:-1,y0=f(r.x),x=nice(Number(r.x.toPrecision(10)),1e-8*Math.max(1,Math.abs(r.x)),s=>sign*(f(s)-y0)<=1e-12*Math.max(1,Math.abs(y0))),y=f(x);
   if(!extrema.some(e=>Math.abs(e.x-x)<Math.max(1e-6,step/4)))extrema.push({x,value:y,kind});
  }catch{/* non-finite objective in bracket: skip */}
 }
 extrema.sort((a,b)=>a.x-b.x);
 const edgeVals=dom.intervals.flatMap(D=>[D.loClosed?f(D.lo):NaN,D.hiClosed?f(D.hi):NaN]);
 const finiteVals=ys.concat(edgeVals,extrema.map(e=>e.value)).filter(Number.isFinite);
 const range={min:Math.min(...finiteVals),max:Math.max(...finiteVals),unboundedNearPoles:poles.length>0,
  note:'Sampled estimate on the grid plus refined extrema; values between samples or near poles can exceed it.'};
 // Monotonic pieces between domain edges, poles, jumps and extrema.
 const monotonic=[];
 for(const D of dom.intervals){
  if(!(D.hi>D.lo))continue;
  const cuts=[D.lo,...extrema.map(e=>e.x),...poles,...jumps].filter(x=>x>D.lo&&x<D.hi);cuts.push(D.hi);cuts.sort((a,b)=>a-b);
  let prev=D.lo;
  for(const c of cuts){if(c-prev<=o.tolerance){prev=c;continue;}
   const probes=[0.25,0.5,0.75].map(t=>dx(prev+(c-prev)*t)).filter(Number.isFinite);
   const trend=probes.length&&probes.every(d=>Math.abs(d)<=1e-7*Math.max(1,range.max-range.min))?'constant':probes.every(d=>d>0)?'increasing':probes.every(d=>d<0)?'decreasing':'mixed';
   monotonic.push({lo:prev,hi:c,trend});prev=c;}
 }
 // Symmetry within tolerance on a symmetric interval, tested at sampled points where f(±x) are finite.
 let symmetry={applicable:false,even:false,odd:false,note:'Symmetry tests need an interval symmetric about 0 (a = -b).'};
 if(Math.abs(o.lo+o.hi)<=1e-12*Math.max(1,Math.abs(o.lo))){
  let evenErr=0,oddErr=0,count=0,scale=1;
  let mismatch=0;
  for(const x of xs){if(x<0)continue;const p=f(x),m=f(-x);if(Number.isFinite(p)!==Number.isFinite(m)){mismatch++;continue;}if(!Number.isFinite(p)||Math.abs(p)>1e8||Math.abs(m)>1e8)continue;count++;scale=Math.max(scale,Math.abs(p),Math.abs(m));evenErr=Math.max(evenErr,Math.abs(p-m));oddErr=Math.max(oddErr,Math.abs(p+m));}
  const tol=1e-8*scale;
  const ok=count>0&&!mismatch;
  symmetry={applicable:count>0,even:ok&&evenErr<=tol,odd:ok&&oddErr<=tol,maxEvenDeviation:evenErr,maxOddDeviation:oddErr,pointsTested:count,domainMismatches:mismatch,
   note:'Even/odd is checked at sampled points within relative tolerance 1e-8; it is evidence, not a proof.'};
 }
 return {type:'function-analysis',expression:fx,domain:[o.lo,o.hi],samples:o.samples,tolerance:o.tolerance,
  domainIntervals:dom.intervals,domainNotation:setText(dom.intervals),excludedPoints:dom.excludedPoints,
  zeros,rootStatus:roots.rootStatus,poles,jumps,extrema,range,monotonic,symmetry,
  note:'Real domain is where evaluation is finite and real at the '+o.samples+'-interval grid, with boundaries refined by bisection; endpoint inclusion uses an exact-evaluation and growth heuristic. Extrema come from sign changes of a central-difference derivative refined by golden-section search. All results are numerical estimates.'};
}
function plotPoints(expression,lo,hi,n=480){const f=makeEval(expression),pts=[];for(let i=0;i<=n;i++){const x=lo+(hi-lo)*i/n;pts.push([x,f(x)]);}return pts;}
const area=document.createElement('details');area.id='function-analysis-details';
area.innerHTML='<summary>Inequalities &amp; function domain analysis</summary>'+
 '<p class="graph-data-muted">Solve f(x) &lt; g(x), ≤, &gt;, ≥ or = on [a,b] as a union of intervals, or analyze a bare f(x): real domain, zeros, poles, extrema, sampled range, monotonicity and symmetry. Bounds accept constants such as 2*pi. Numerical estimates, not proofs.</p>'+
 '<div class="num-fields"><label>Expression or comparison<input id="fa-expression" value="x^2-4 < 0" spellcheck="false" autocomplete="off"></label>'+
 '<label>Lower bound a<input id="fa-lo" value="-5" inputmode="decimal"></label>'+
 '<label>Upper bound b<input id="fa-hi" value="5" inputmode="decimal"></label>'+
 '<label>Grid intervals (20–1600)<input id="fa-samples" type="number" min="20" max="1600" step="1" value="400"></label></div>'+
 '<div class="data-toolbar"><button id="fa-run" class="primary" type="button">Analyze</button>'+
 '<button id="fa-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="fa-output" role="status" aria-live="polite" style="white-space:pre-wrap;overflow-wrap:anywhere">Enter a comparison such as x^2-4 &lt; 0, or a function such as tan(x).</pre>'+
 '<canvas id="fa-canvas" width="640" height="300" role="img" aria-label="Function plot: run an analysis to draw f(x) with the solution set shaded." style="width:100%;max-width:640px;height:auto;display:block;border:1px solid #dce4f6;border-radius:9px;background:#fff"></canvas>';
panel.append(area);
let last=null;
const out=$('fa-output'),canvas=$('fa-canvas');
const invalidate=()=>{last=null;$('fa-to-table').disabled=true;out.classList.remove('error');};
// 'input' covers typing, paste and spinner steps; 'change' would re-fire on blur after Enter-to-run.
for(const input of area.querySelectorAll('input')){input.addEventListener('input',invalidate);
 input.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault();$('fa-run').click();}});}
function draw(result){
 const ctx=canvas.getContext('2d');if(!ctx)return;const W=canvas.width,H=canvas.height,pad=28;
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);
 const [lo,hi]=result.domain,lhs=plotPoints(result.analysis.expression,lo,hi),rhs=result.solution?plotPoints(result.solution.rhs,lo,hi):null;
 const vals=lhs.concat(rhs||[]).map(p=>p[1]).filter(Number.isFinite).sort((a,b)=>a-b);
 let ymin=vals.length?vals[Math.floor(vals.length*0.03)]:-1,ymax=vals.length?vals[Math.ceil(vals.length*0.97)-1]:1;
 if(!(ymax>ymin)){ymin-=1;ymax+=1;}const padY=(ymax-ymin)*0.1;ymin-=padY;ymax+=padY;
 const X=x=>pad+(x-lo)/(hi-lo)*(W-2*pad),Y=y=>H-pad-(y-ymin)/(ymax-ymin)*(H-2*pad);
 if(result.solution){ctx.fillStyle='rgba(46,139,87,0.18)';for(const I of result.solution.intervals){const x0=X(I.lo),x1=X(I.hi);ctx.fillRect(x0,pad,Math.max(2,x1-x0),H-2*pad);}}
 ctx.strokeStyle='#c8d2e4';ctx.lineWidth=1;ctx.beginPath();if(ymin<0&&ymax>0){ctx.moveTo(pad,Y(0));ctx.lineTo(W-pad,Y(0));}if(lo<0&&hi>0){ctx.moveTo(X(0),pad);ctx.lineTo(X(0),H-pad);}ctx.stroke();
 const line=(pts,color,dash)=>{ctx.strokeStyle=color;ctx.lineWidth=2;ctx.setLineDash(dash);ctx.beginPath();let pen=false,prev=null;
  for(const [x,y] of pts){if(!Number.isFinite(y)||y<ymin-(ymax-ymin)*5||y>ymax+(ymax-ymin)*5||(prev!==null&&Math.abs(y-prev)>(ymax-ymin)*2)){pen=false;prev=Number.isFinite(y)?y:null;continue;}
   const cy=Math.max(-H,Math.min(2*H,Y(y)));if(pen)ctx.lineTo(X(x),cy);else ctx.moveTo(X(x),cy);pen=true;prev=y;}
  ctx.stroke();ctx.setLineDash([]);};
 if(rhs)line(rhs,'#b5651d',[6,4]);line(lhs,'#2456a6',[]);
 ctx.fillStyle='#566784';ctx.font='11px sans-serif';ctx.fillText(fmt(lo),pad,H-8);ctx.fillText(fmt(hi),W-pad-40,H-8);
 canvas.setAttribute('aria-label','Plot of '+result.analysis.expression+' on ['+fmt(lo)+', '+fmt(hi)+']'+(result.solution?'; shaded solution set '+result.solution.notation:'; real domain '+result.analysis.domainNotation)+'.');
}
function report(r){
 const a=r.analysis,lines=[];
 if(r.solution){lines.push('Solution of '+r.solution.lhs+' '+r.solution.operator+' '+r.solution.rhs+' on ['+fmt(r.domain[0])+', '+fmt(r.domain[1])+']:','  '+r.solution.notation);
  if(r.solution.poles.length)lines.push('  Excluded possible poles: '+r.solution.poles.map(fmt).join(', '));}
 lines.push('Analysis of f(x) = '+a.expression+':','  Real domain (sampled): '+a.domainNotation,
  '  Zeros: '+(a.zeros.length?a.zeros.map(fmt).join(', '):'none found')+(a.rootStatus==='sampled-zero-plateau'?' (f ≈ 0 on all samples)':''),
  '  Poles / jumps: '+(a.poles.length?a.poles.map(fmt).join(', '):'none')+' / '+(a.jumps.length?a.jumps.map(fmt).join(', '):'none'),
  '  Local extrema: '+(a.extrema.length?a.extrema.map(e=>e.kind+' at x = '+fmt(e.x)+' (f = '+fmt(e.value)+')').join('; '):'none found'),
  '  Sampled range: ['+fmt(a.range.min)+', '+fmt(a.range.max)+']'+(a.range.unboundedNearPoles?' — unbounded near poles':'')+' (grid estimate)',
  '  Monotonic: '+(a.monotonic.length?a.monotonic.map(m=>m.trend+' on ['+fmt(m.lo)+', '+fmt(m.hi)+']').join('; '):'n/a'),
  '  Symmetry: '+(a.symmetry.applicable?(a.symmetry.even?'even':a.symmetry.odd?'odd':'neither even nor odd')+' (sampled, tolerance 1e-8)':'not tested (interval not symmetric about 0)'),
  (r.solution?r.solution.note:a.note));
 return lines.join('\n');
}
function run({expression,lo,hi,samples,tolerance}={}){
 const cmp=parseComparison(expression);
 const analysis=analyze({expression:cmp.lhs,lo,hi,samples,tolerance});
 const solution=cmp.op?solve({expression,lo,hi,samples,tolerance}):null;
 return {type:'function-analysis-run',domain:analysis.domain,analysis,solution};
}
$('fa-run').addEventListener('click',()=>{
 try{last=run({expression:$('fa-expression').value,lo:$('fa-lo').value,hi:$('fa-hi').value,samples:$('fa-samples').value});
  out.classList.remove('error');out.textContent=report(last);draw(last);$('fa-to-table').disabled=false;
 }catch(err){invalidate();out.classList.add('error');out.textContent=err.message+' Correct the input and press Analyze again.';}
});
$('fa-to-table').addEventListener('click',()=>{
 try{if(!last)throw Error('Run an analysis first.');const rows=[],a=last.analysis;
  if(last.solution)for(const I of last.solution.intervals)rows.push(['solution',I.lo,I.hi,intervalText(I)]);
  for(const I of a.domainIntervals)rows.push(['domain',I.lo,I.hi,intervalText(I)]);
  for(const z of a.zeros)rows.push(['zero',z,z,'']);for(const p of a.poles)rows.push(['pole',p,p,'']);
  for(const e of a.extrema)rows.push([e.kind,e.x,e.value,'f(x) value in third column']);
  for(const m of a.monotonic)rows.push([m.trend,m.lo,m.hi,'monotonic piece']);
  M.dataTables.importData({headers:['kind','x_or_lo','hi_or_value','notation'],rows},'Function_Analysis');M.advanced.mode('data');
 }catch(err){out.classList.add('error');out.textContent=err.message;}
});
M.functionAnalysis={solve,analyze,run,parseComparison,intervalText};
})();
