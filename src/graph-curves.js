/* ProMathStudio: implicit F(x,y)=0, parametric (x(t),y(t)) and polar r(theta) 2D curves.
   Expressions are evaluated only through MathStudio.numerical.evaluate (no eval/Function). */
(()=>{'use strict';
const M=window.MathStudio;
if(!M?.numerical?.evaluate)return;
const MAX_GRID=300,MIN_GRID=4,MAX_SAMPLES=20000,MIN_SAMPLES=2,MAX_EXPR=1500;

const fail=message=>{throw Error(message);};
const finite=(value,label)=>{const n=typeof value==='string'?(value.trim()?Number(value):NaN):Number(value);if(!Number.isFinite(n))fail(label+' must be a finite number.');return n;};
const intIn=(value,min,max,label)=>{const n=finite(value,label);if(!Number.isInteger(n)||n<min||n>max)fail(label+' must be an integer from '+min+' to '+max+'.');return n;};
const cleanExpr=(expr,label)=>{const s=String(expr??'').replace(/θ/g,'theta').trim();if(!s)fail(label+' is empty. Enter an expression.');if(s.length>MAX_EXPR)fail(label+' exceeds '+MAX_EXPR+' characters.');return s;};
const window2=(lo,hi,label)=>{const a=finite(lo,label+' minimum'),b=finite(hi,label+' maximum');if(!(b>a))fail(label+' maximum must be greater than its minimum.');if(Math.abs(a)>1e12||Math.abs(b)>1e12)fail(label+' bounds must be within ±1e12.');return [a,b];};

/* An unknown variable or syntax error must be reported, not silently rendered as a blank plot. */
const fatal=err=>/unknown variable|unexpected|syntax|unbalanced|parenthes|expected|maximum 1,500|unsupported|unknown function/i.test(String(err&&err.message));
function safeEval(expr,env){
 try{const v=M.numerical.evaluate(expr,env);return Number.isFinite(v)?v:NaN;}
 catch(err){if(fatal(err))throw err;return NaN;}
}

/* Implicit equations: "lhs = rhs" becomes F = lhs - rhs; a bare expression is F. */
function implicitFunction(expr){
 const s=cleanExpr(expr,'Implicit equation');
 const parts=s.split('=');
 if(parts.length>2||/==|<=|>=|!=/.test(s))fail('Use a single "=" in the implicit equation, for example x^2 + y^2 = 1.');
 if(parts.length===2){
  const lhs=parts[0].trim(),rhs=parts[1].trim();
  if(!lhs||!rhs)fail('Both sides of "=" need an expression.');
  return (x,y)=>{const a=safeEval(lhs,{x,y});if(!Number.isFinite(a))return NaN;const b=safeEval(rhs,{x,y});return a-b;};
 }
 return (x,y)=>safeEval(s,{x,y});
}

/* Refine a sign change of F on the segment P(s)=A+s(B-A), s in [0,1], with an Illinois
   false-position iteration safeguarded by periodic bisection so the bracket always shrinks. */
function refineEdge(F,ax,ay,bx,by,fa,fb){
 let lo=0,hi=1,flo=fa,fhi=fb,side=0,s=fa/(fa-fb),fs=NaN;
 const at=t=>F(ax+(bx-ax)*t,ay+(by-ay)*t);
 for(let it=0;it<48;it++){
  s=(it%3===2)?(lo+hi)/2:(lo*fhi-hi*flo)/(fhi-flo);
  if(!(s>lo&&s<hi))s=(lo+hi)/2;
  fs=at(s);
  if(!Number.isFinite(fs))return {s,residual:Infinity};
  if(fs===0||hi-lo<1e-15)break;
  if((fs>0)===(flo>0)){lo=s;flo=fs;if(side===-1)fhi/=2;side=-1;}
  else{hi=s;fhi=fs;if(side===1)flo/=2;side=1;}
  if(Math.abs(fs)<1e-15)break;
 }
 return {s,residual:Math.abs(fs)};
}

function implicit(expr,options={}){
 const F=implicitFunction(expr);
 const [xmin,xmax]=window2(options.xmin??-2,options.xmax??2,'x');
 const [ymin,ymax]=window2(options.ymin??-2,options.ymax??2,'y');
 const nx=intIn(options.nx??options.grid??160,MIN_GRID,MAX_GRID,'Grid cells in x');
 const ny=intIn(options.ny??options.grid??160,MIN_GRID,MAX_GRID,'Grid cells in y');
 const tolScale=Number.isFinite(options.tolerance)&&options.tolerance>0?options.tolerance:1e-6;
 const hx=(xmax-xmin)/nx,hy=(ymax-ymin)/ny,X=i=>xmin+i*hx,Y=j=>ymin+j*hy;
 const V=new Float64Array((nx+1)*(ny+1));let finiteCount=0;
 for(let j=0;j<=ny;j++)for(let i=0;i<=nx;i++){const v=F(X(i),Y(j));V[j*(nx+1)+i]=v;if(Number.isFinite(v))finiteCount++;}
 if(!finiteCount)fail('F(x, y) is not finite anywhere on the grid. Check the expression and the window.');
 const at=(i,j)=>V[j*(nx+1)+i];
 let rejected=0,maxResidual=0;
 /* One refined crossing per grid edge, shared by neighbouring cells. */
 const crossing=(i0,j0,i1,j1)=>{
  const a=at(i0,j0),b=at(i1,j1);
  if(!Number.isFinite(a)||!Number.isFinite(b)||(a>0)===(b>0))return null;
  const ax=X(i0),ay=Y(j0),bx=X(i1),by=Y(j1);
  const r=refineEdge(F,ax,ay,bx,by,a,b);
  const tol=tolScale*Math.max(1,Math.min(Math.abs(a),Math.abs(b)));
  if(!(r.residual<=tol)){rejected++;return false;}
  if(r.residual>maxResidual)maxResidual=r.residual;
  return [ax+(bx-ax)*r.s,ay+(by-ay)*r.s];
 };
 const H=new Array(nx*(ny+1)),Vt=new Array((nx+1)*ny);
 for(let j=0;j<=ny;j++)for(let i=0;i<nx;i++)H[j*nx+i]=crossing(i,j,i+1,j);
 for(let j=0;j<ny;j++)for(let i=0;i<=nx;i++)Vt[j*(nx+1)+i]=crossing(i,j,i,j+1);
 const segments=[];let ambiguous=0;
 for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
  const c=[at(i,j),at(i+1,j),at(i+1,j+1),at(i,j+1)];
  if(!c.every(Number.isFinite))continue;
  const e=[H[j*nx+i],Vt[j*(nx+1)+i+1],H[(j+1)*nx+i],Vt[j*(nx+1)+i]];/* bottom,right,top,left */
  const present=[0,1,2,3].filter(k=>e[k]!==null);
  let pairs;
  if(present.length===2)pairs=[present];
  else if(present.length===4){
   ambiguous++;
   const centre=(c[0]+c[1]+c[2]+c[3])/4;
   pairs=((centre>0)===(c[0]>0))?[[0,1],[2,3]]:[[3,0],[1,2]];
  }else continue;
  for(const [p,q] of pairs){if(e[p]&&e[q])segments.push([e[p][0],e[p][1],e[q][0],e[q][1]]);}
 }
 return {type:'implicit',segments,segmentCount:segments.length,rejected,maxResidual,ambiguousCells:ambiguous,
  grid:[nx,ny],window:{xmin,xmax,ymin,ymax},finiteFraction:finiteCount/V.length};
}

function sampleCount(n){
 const s=finite(n,'Samples');
 if(!Number.isInteger(s))fail('Samples must be an integer.');
 if(s>MAX_SAMPLES)fail('Too many samples: maximum is '+MAX_SAMPLES.toLocaleString('en-US')+'.');
 if(s<MIN_SAMPLES)fail('Samples must be at least '+MIN_SAMPLES+'.');
 return s;
}
function polylines(points){
 const lines=[];let current=[],breaks=0;
 for(const p of points){
  if(p&&Number.isFinite(p.x)&&Number.isFinite(p.y)){current.push(p);}
  else{if(current.length){lines.push(current);breaks++;}current=[];}
 }
 if(current.length)lines.push(current);
 return {lines,breaks};
}
function finish(type,points,extra){
 const finitePoints=points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y));
 if(!finitePoints.length)fail('The curve is not finite at any sample. Check the expressions and parameter range.');
 const {lines,breaks}=polylines(points);
 return Object.assign({type,points,polylines:lines,breaks,finiteCount:finitePoints.length,nonFinite:points.length-finitePoints.length},extra);
}
function parametric(xExpr,yExpr,options={}){
 const xs=cleanExpr(xExpr,'x(t)'),ys=cleanExpr(yExpr,'y(t)');
 const [t0,t1]=window2(options.t0??0,options.t1??2*Math.PI,'t');
 const n=sampleCount(options.samples??400);
 const points=[];
 for(let k=0;k<n;k++){const t=k===n-1?t1:t0+(t1-t0)*k/(n-1);const x=safeEval(xs,{t}),y=Number.isFinite(x)?safeEval(ys,{t}):NaN;points.push({t,x,y});}
 return finish('parametric',points,{range:[t0,t1],samples:n});
}
/* Negative r is plotted through the origin: (r cos theta, r sin theta) with signed r. */
function polar(rExpr,options={}){
 const rs=cleanExpr(rExpr,'r(θ)');
 const [a,b]=window2(options.theta0??0,options.theta1??2*Math.PI,'θ');
 const n=sampleCount(options.samples??720);
 const points=[];
 for(let k=0;k<n;k++){const theta=k===n-1?b:a+(b-a)*k/(n-1);const r=safeEval(rs,{theta});points.push({theta,r,x:r*Math.cos(theta),y:r*Math.sin(theta)});}
 return finish('polar',points,{range:[a,b],samples:n});
}

function bounds(result){
 if(result.type==='implicit'){const w=result.window;return [w.xmin,w.xmax,w.ymin,w.ymax];}
 let x0=Infinity,x1=-Infinity,y0=Infinity,y1=-Infinity;
 for(const p of result.points)if(Number.isFinite(p.x)&&Number.isFinite(p.y)){x0=Math.min(x0,p.x);x1=Math.max(x1,p.x);y0=Math.min(y0,p.y);y1=Math.max(y1,p.y);}
 const px=(x1-x0)*.06||Math.max(1,Math.abs(x0))*.1,py=(y1-y0)*.06||Math.max(1,Math.abs(y0))*.1;
 return [x0-px,x1+px,y0-py,y1+py];
}
function niceStep(span,count){
 const raw=span/Math.max(1,count),p=Math.pow(10,Math.floor(Math.log10(raw))),m=raw/p;
 return (m<=1?1:m<=2?2:m<=2.5?2.5:m<=5?5:10)*p;
}
const fmt=v=>{const a=Math.abs(v);if(a<1e-12)return '0';if(a>=1e5||a<1e-3)return v.toExponential(2);return String(Number(v.toPrecision(6)));};

/* Shared canvas renderer: axes, grid, tick labels and the curve. Returns the view transform. */
function draw(canvas,result,options={}){
 const ctx=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
 const pad={l:72,r:18,t:16,b:44};
 let [x0,x1,y0,y1]=bounds(result);
 const pw=w-pad.l-pad.r,ph=h-pad.t-pad.b;
 if(options.equal){
  const sx=pw/(x1-x0),sy=ph/(y1-y0),s=Math.min(sx,sy);
  const cx=(x0+x1)/2,cy=(y0+y1)/2,hw=pw/s/2,hh=ph/s/2;
  x0=cx-hw;x1=cx+hw;y0=cy-hh;y1=cy+hh;
 }
 const sx=pw/(x1-x0),sy=ph/(y1-y0);
 const px=x=>pad.l+(x-x0)*sx,py=y=>pad.t+(y1-y)*sy;
 ctx.save();
 ctx.clearRect(0,0,w,h);ctx.fillStyle='#ffffff';ctx.fillRect(0,0,w,h);
 ctx.font='17px system-ui,sans-serif';ctx.lineWidth=1;
 const stepX=niceStep(x1-x0,Math.max(3,Math.round(pw/90))),stepY=niceStep(y1-y0,Math.max(3,Math.round(ph/70)));
 ctx.strokeStyle='#e4ecee';ctx.fillStyle='#3d5960';
 ctx.textAlign='center';ctx.textBaseline='top';
 for(let v=Math.ceil(x0/stepX)*stepX;v<=x1+stepX*1e-9;v+=stepX){const X=px(v);ctx.beginPath();ctx.moveTo(X,pad.t);ctx.lineTo(X,h-pad.b);ctx.stroke();ctx.fillText(fmt(v),X,h-pad.b+6);}
 ctx.textAlign='right';ctx.textBaseline='middle';
 for(let v=Math.ceil(y0/stepY)*stepY;v<=y1+stepY*1e-9;v+=stepY){const Y=py(v);ctx.beginPath();ctx.moveTo(pad.l,Y);ctx.lineTo(w-pad.r,Y);ctx.stroke();ctx.fillText(fmt(v),pad.l-6,Y);}
 ctx.strokeStyle='#5d7c84';ctx.lineWidth=1.6;ctx.beginPath();
 if(y0<=0&&y1>=0){ctx.moveTo(pad.l,py(0));ctx.lineTo(w-pad.r,py(0));}
 if(x0<=0&&x1>=0){ctx.moveTo(px(0),pad.t);ctx.lineTo(px(0),h-pad.b);}
 ctx.stroke();
 ctx.strokeStyle='#9fb5ba';ctx.lineWidth=1;ctx.strokeRect(pad.l,pad.t,pw,ph);
 ctx.fillStyle='#27444b';ctx.textAlign='right';ctx.textBaseline='bottom';ctx.fillText('x',w-pad.r-4,h-pad.b-4);
 ctx.textAlign='left';ctx.textBaseline='top';ctx.fillText('y',pad.l+6,pad.t+4);
 ctx.beginPath();ctx.rect(pad.l,pad.t,pw,ph);ctx.clip();
 ctx.strokeStyle='#c2410c';ctx.lineWidth=2.6;ctx.lineJoin='round';ctx.lineCap='round';
 ctx.beginPath();
 if(result.type==='implicit'){for(const s of result.segments){ctx.moveTo(px(s[0]),py(s[1]));ctx.lineTo(px(s[2]),py(s[3]));}}
 else for(const line of result.polylines){
  ctx.moveTo(px(line[0].x),py(line[0].y));
  if(line.length===1)ctx.lineTo(px(line[0].x)+.01,py(line[0].y));
  for(let k=1;k<line.length;k++)ctx.lineTo(px(line[k].x),py(line[k].y));
 }
 ctx.stroke();ctx.restore();
 return {x0,x1,y0,y1};
}

/* Table rows for Data Tables export. */
function tableOf(result){
 if(result.type==='implicit'){const rows=[];result.segments.forEach((s,k)=>{rows.push([k+1,s[0],s[1]],[k+1,s[2],s[3]]);});return {headers:['segment','x','y'],rows};}
 if(result.type==='parametric')return {headers:['t','x','y'],rows:result.points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)).map(p=>[p.t,p.x,p.y])};
 return {headers:['theta','r','x','y'],rows:result.points.filter(p=>Number.isFinite(p.x)&&Number.isFinite(p.y)).map(p=>[p.theta,p.r,p.x,p.y])};
}

const api={implicit,parametric,polar,draw,table:tableOf,limits:{maxGrid:MAX_GRID,maxSamples:MAX_SAMPLES}};
M.graphCurves=api;

/* ---------- UI (static markup only; user text never reaches innerHTML) ---------- */
const panel=document.getElementById('graph-panel');
if(!panel||document.getElementById('curves-details'))return;
const style=document.createElement('style');style.id='graph-curves-style';
style.textContent='#curves-details{padding:15px 18px;margin:12px 0 20px;border:1px solid #cfdde8;border-radius:13px;background:#f8fbfd;max-width:100%;box-sizing:border-box;min-width:0}'+
'#curves-details>summary{font-weight:780;color:#1d5f86;cursor:pointer;font-size:15px;min-height:40px;display:flex;align-items:center}'+
'#curves-details .curves-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:14px 0}'+
'#curves-details label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:650;color:#31545a;min-width:0}'+
'#curves-details label.curves-wide{grid-column:span 2}'+
'#curves-details input:not([type=checkbox]),#curves-details select{width:100%;min-width:0;min-height:42px;box-sizing:border-box;padding:9px 10px;border:1px solid #bfd3dc;border-radius:9px;background:#fff;color:#24434b;font:inherit}'+
'#curves-details label.curves-check{flex-direction:row;align-items:center;min-height:42px}'+
'#curves-details input[type=checkbox]{width:22px;height:22px}'+
'#curves-details .curves-actions{display:flex;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px}'+
'#curves-details .curves-actions button{min-height:42px}'+
'#curves-status{font-size:13px;color:#3f5f68;overflow-wrap:anywhere}'+
'#curves-status.curves-error{color:#b42318;font-weight:650}'+
'#curves-canvas{display:block;width:100%;height:auto;aspect-ratio:3/2;background:#fff;border:1px solid #dce7e7;border-radius:12px}'+
'#curves-details [hidden]{display:none!important}'+
'@media(max-width:760px){#curves-details{padding:12px}#curves-details .curves-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'+
'@media(max-width:440px){#curves-details .curves-grid{grid-template-columns:minmax(0,1fr)}#curves-details label.curves-wide{grid-column:auto}}';
document.head.appendChild(style);
const root=document.createElement('details');root.id='curves-details';
root.innerHTML='<summary>Implicit, parametric &amp; polar curves · F(x,y)=0, (x(t), y(t)), r(θ)</summary>'+
'<p class="small-note">Implicit curves use marching squares with each edge crossing refined toward F = 0; sign changes across poles or jumps whose refined residual stays large are rejected and counted. Parametric and polar polylines break at non-finite samples. Polar r may be negative (plotted through the origin). Radian angles.</p>'+
'<div class="curves-grid">'+
'<label for="curves-type">Curve type<select id="curves-type"><option value="implicit">Implicit F(x, y) = 0</option><option value="parametric">Parametric x(t), y(t)</option><option value="polar">Polar r(θ)</option></select></label>'+
'<label for="curves-expr" class="curves-wide" data-curves="implicit">Equation F(x, y) = 0 or lhs = rhs<input id="curves-expr" type="text" spellcheck="false" autocomplete="off" value="x^2 + y^2 = 1"></label>'+
'<label for="curves-grid-n" data-curves="implicit">Grid cells per axis (4–300)<input id="curves-grid-n" type="number" min="4" max="300" step="1" value="160"></label>'+
'<label for="curves-xmin" data-curves="implicit">x min<input id="curves-xmin" type="number" step="any" value="-2"></label>'+
'<label for="curves-xmax" data-curves="implicit">x max<input id="curves-xmax" type="number" step="any" value="2"></label>'+
'<label for="curves-ymin" data-curves="implicit">y min<input id="curves-ymin" type="number" step="any" value="-2"></label>'+
'<label for="curves-ymax" data-curves="implicit">y max<input id="curves-ymax" type="number" step="any" value="2"></label>'+
'<label for="curves-xt" class="curves-wide" data-curves="parametric" hidden>x(t)<input id="curves-xt" type="text" spellcheck="false" autocomplete="off" value="sin(3*t)"></label>'+
'<label for="curves-yt" class="curves-wide" data-curves="parametric" hidden>y(t)<input id="curves-yt" type="text" spellcheck="false" autocomplete="off" value="sin(2*t)"></label>'+
'<label for="curves-r" class="curves-wide" data-curves="polar" hidden>r(θ) (use theta)<input id="curves-r" type="text" spellcheck="false" autocomplete="off" value="cos(3*theta)"></label>'+
'<label for="curves-p0" data-curves="parametric polar" hidden>Parameter start (t₀ or θ₀)<input id="curves-p0" type="number" step="any" value="0"></label>'+
'<label for="curves-p1" data-curves="parametric polar" hidden>Parameter end (t₁ or θ₁)<input id="curves-p1" type="number" step="any" value="6.283185307179586"></label>'+
'<label for="curves-samples" data-curves="parametric polar" hidden>Samples (2–20,000)<input id="curves-samples" type="number" min="2" max="20000" step="1" value="721"></label>'+
'<label for="curves-equal" class="curves-check"><input id="curves-equal" type="checkbox" checked> Equal aspect (1:1)</label>'+
'</div>'+
'<div class="curves-actions"><button id="curves-plot" type="button" class="primary">Plot curve</button><button id="curves-save" type="button" class="secondary" disabled>Save points to Data Tables</button></div>'+
'<p id="curves-status" role="status" aria-live="polite">Ready. Choose a curve type and press Plot curve.</p>'+
'<canvas id="curves-canvas" width="900" height="600" role="img" aria-label="Implicit, parametric or polar curve plot (not yet plotted)"></canvas>';
const anchor=document.getElementById('complex-graph-workbench');
if(anchor&&panel.contains(anchor))anchor.after(root);else (panel.querySelector('.graph-wrap')||panel).appendChild(root);

const $=id=>document.getElementById(id);
const canvas=$('curves-canvas'),status=$('curves-status');
let last=null;
const setStatus=(text,error)=>{status.textContent=text;status.classList.toggle('curves-error',!!error);};
const syncType=()=>{const type=$('curves-type').value;root.querySelectorAll('[data-curves]').forEach(el=>{el.hidden=!el.getAttribute('data-curves').split(' ').includes(type);});};
const g=v=>Number(v.toPrecision(4));
function plot(){
 const type=$('curves-type').value;
 try{
  let result,summary,label;
  if(type==='implicit'){
   result=implicit($('curves-expr').value,{xmin:$('curves-xmin').value,xmax:$('curves-xmax').value,ymin:$('curves-ymin').value,ymax:$('curves-ymax').value,grid:$('curves-grid-n').value});
   summary='Implicit curve: '+result.segmentCount+' segment'+(result.segmentCount===1?'':'s')+' on a '+result.grid[0]+'×'+result.grid[1]+' grid; max |F| at plotted points '+result.maxResidual.toExponential(2)+'; '+result.rejected+' pole/discontinuity sign change'+(result.rejected===1?'':'s')+' rejected.'+(result.segmentCount?'':' No zero contour found in this window.');
   label='Implicit curve '+$('curves-expr').value.trim()+' with '+result.segmentCount+' segments, x from '+g(result.window.xmin)+' to '+g(result.window.xmax)+', y from '+g(result.window.ymin)+' to '+g(result.window.ymax);
  }else if(type==='parametric'){
   result=parametric($('curves-xt').value,$('curves-yt').value,{t0:$('curves-p0').value,t1:$('curves-p1').value,samples:$('curves-samples').value});
   summary='Parametric curve: '+result.finiteCount+' finite of '+result.samples+' samples, '+result.polylines.length+' polyline piece'+(result.polylines.length===1?'':'s')+', t ∈ ['+g(result.range[0])+', '+g(result.range[1])+'].'+(result.nonFinite?' '+result.nonFinite+' non-finite sample'+(result.nonFinite===1?'':'s')+' break the curve.':'');
   label='Parametric curve x(t) = '+$('curves-xt').value.trim()+', y(t) = '+$('curves-yt').value.trim()+' for t from '+g(result.range[0])+' to '+g(result.range[1]);
  }else{
   result=polar($('curves-r').value,{theta0:$('curves-p0').value,theta1:$('curves-p1').value,samples:$('curves-samples').value});
   const rmax=Math.max(...result.points.filter(p=>Number.isFinite(p.r)).map(p=>Math.abs(p.r)));
   summary='Polar curve: '+result.finiteCount+' finite of '+result.samples+' samples, '+result.polylines.length+' polyline piece'+(result.polylines.length===1?'':'s')+', θ ∈ ['+g(result.range[0])+', '+g(result.range[1])+'], max |r| = '+g(rmax)+'.'+(result.nonFinite?' '+result.nonFinite+' non-finite sample'+(result.nonFinite===1?'':'s')+' break the curve.':'');
   label='Polar curve r(θ) = '+$('curves-r').value.trim()+' for θ from '+g(result.range[0])+' to '+g(result.range[1]);
  }
  draw(canvas,result,{equal:$('curves-equal').checked});
  canvas.setAttribute('aria-label',label.slice(0,400));
  last=result;$('curves-save').disabled=false;
  setStatus(summary,false);
 }catch(err){
  last=null;$('curves-save').disabled=true;
  setStatus('Error: '+err.message,true);
 }
}
$('curves-type').addEventListener('change',()=>{syncType();last=null;$('curves-save').disabled=true;
 setStatus('Ready. Press Plot curve.',false);});
$('curves-plot').addEventListener('click',plot);
$('curves-equal').addEventListener('change',()=>{if(last)draw(canvas,last,{equal:$('curves-equal').checked});});
root.querySelectorAll('input[type=text],input[type=number]').forEach(input=>input.addEventListener('keydown',ev=>{if(ev.key==='Enter'){ev.preventDefault();plot();}}));
$('curves-save').addEventListener('click',()=>{
 try{
  if(!last)fail('Plot a curve first.');
  if(!M.dataTables?.importData)fail('Data Tables are unavailable.');
  const t=tableOf(last);if(!t.rows.length)fail('There are no points to save.');
  if(t.rows.length>6000)fail('Too many points for one table ('+t.rows.length+' > 6,000). Reduce samples or grid cells.');
  const name=last.type==='implicit'?'Implicit_Curve':last.type==='parametric'?'Parametric_Curve':'Polar_Curve';
  M.dataTables.importData(t,name);
  setStatus('Saved '+t.rows.length+' points to Data Tables as '+name+'.',false);
 }catch(err){setStatus('Error: '+err.message,true);}
});
syncType();
api.plot=plot;
})();
