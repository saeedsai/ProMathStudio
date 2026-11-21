/* ProMathStudio: 2-D vector fields (quiver), RK4 streamlines, slope fields dy/dx = f(x, y)
   with solution curves, heuristic candidate equilibria and optional particle advection.
   Expressions are evaluated only through MathStudio.numerical.evaluate (no eval/Function). */
(()=>{'use strict';
const M=window.MathStudio;
if(!M?.numerical?.evaluate)return;
const MAX_GRID=40,MIN_GRID=2,MAX_SEEDS=50,MAX_AUTO=12,MAX_EXPR=1500,MAX_STEPS=20000,MAX_ROWS=6000;

const fail=message=>{throw Error(message);};
const finite=(value,label)=>{const n=typeof value==='string'?(value.trim()?Number(value):NaN):Number(value);if(!Number.isFinite(n))fail(label+' must be a finite number.');return n;};
const intIn=(value,min,max,label)=>{const n=finite(value,label);if(!Number.isInteger(n)||n<min||n>max)fail(label+' must be an integer from '+min+' to '+max+'.');return n;};
const cleanExpr=(expr,label)=>{const s=String(expr??'').trim();if(!s)fail(label+' is empty. Enter an expression in x and y.');if(s.length>MAX_EXPR)fail(label+' exceeds '+MAX_EXPR+' characters.');if(/[=<>]/.test(s))fail(label+' must be an expression, not an equation.');return s;};
function windowOf(o={}){
 const w={xmin:finite(o.xmin??-2,'x minimum'),xmax:finite(o.xmax??2,'x maximum'),ymin:finite(o.ymin??-2,'y minimum'),ymax:finite(o.ymax??2,'y maximum')};
 if(!(w.xmax>w.xmin))fail('x maximum must be greater than x minimum.');
 if(!(w.ymax>w.ymin))fail('y maximum must be greater than y minimum.');
 if([w.xmin,w.xmax,w.ymin,w.ymax].some(v=>Math.abs(v)>1e9))fail('Window bounds must be within ±1e9.');
 return w;
}
const stepFraction=v=>{const s=finite(v??0.0025,'Step fraction');if(!(s>=1e-4&&s<=0.05))fail('Step fraction must be from 0.0001 to 0.05 of the window.');return s;};

/* Syntax errors and unknown names are reported; domain errors (1/0, log 0) become NaN. */
const fatal=err=>/unknown variable|unknown function|unexpected|syntax|unbalanced|parenthes|expected|complete the expression|maximum 1,500|unsupported/i.test(String(err&&err.message));
function safeEval(expr,env){
 try{const v=M.numerical.evaluate(expr,env);return Number.isFinite(v)?v:NaN;}
 catch(err){if(fatal(err))throw err;return NaN;}
}
/* Field F(x,y) -> [u, v] or null where either component is non-finite. */
function fieldOf(pExpr,qExpr){
 const p=cleanExpr(pExpr,'P(x, y)'),q=cleanExpr(qExpr,'Q(x, y)');
 const F=(x,y)=>{const u=safeEval(p,{x,y});if(!Number.isFinite(u))return null;const v=safeEval(q,{x,y});return Number.isFinite(v)?[u,v]:null;};
 F.p=p;F.q=q;F(0.1234567,0.7654321);/* surface syntax / unknown-variable errors early */
 return F;
}
function slopeOf(fExpr){
 const s=cleanExpr(fExpr,'f(x, y)');
 const f=(x,y)=>safeEval(s,{x,y});f.expr=s;f(0.1234567,0.7654321);
 return f;
}
const gridSize=(o,key)=>intIn(o[key]??o.grid??20,MIN_GRID,MAX_GRID,'Grid arrows per axis');
/* Sample points at cell centres of an nx x ny lattice covering the window. */
const lattice=(w,nx,ny)=>({hx:(w.xmax-w.xmin)/nx,hy:(w.ymax-w.ymin)/ny,X:i=>w.xmin+(i+.5)*(w.xmax-w.xmin)/nx,Y:j=>w.ymin+(j+.5)*(w.ymax-w.ymin)/ny});

function quiverOf(F,o={}){
 const w=windowOf(o),nx=gridSize(o,'nx'),ny=gridSize(o,'ny'),L=lattice(w,nx,ny);
 const arrows=[];let nonFinite=0,minMag=Infinity,maxMag=0;
 for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){
  const x=L.X(i),y=L.Y(j),f=F(x,y);
  if(!f){nonFinite++;arrows.push({i,j,x,y,u:NaN,v:NaN,mag:NaN});continue;}
  const mag=Math.hypot(f[0],f[1]);if(!Number.isFinite(mag)){nonFinite++;arrows.push({i,j,x,y,u:NaN,v:NaN,mag:NaN});continue;}
  minMag=Math.min(minMag,mag);maxMag=Math.max(maxMag,mag);arrows.push({i,j,x,y,u:f[0],v:f[1],mag});
 }
 if(nonFinite===arrows.length)fail('The field is not finite at any grid point. Check P, Q and the window.');
 return {type:'quiver',arrows,nonFinite,minMag,maxMag,grid:[nx,ny],window:w};
}
function quiver(pExpr,qExpr,o={}){return quiverOf(fieldOf(pExpr,qExpr),o);}

/* Streamline of the direction field v/|v| (arc-length parameter s) with classical RK4 and a fixed
   step h = stepFraction x window diagonal. Stops: window edge (clipped onto the boundary),
   stagnation (|v| -> 0 or reversal next to a slow point), singular (direction reversal at speed,
   e.g. across a pole), non-finite field, closed orbit (returns within 0.6 h of the seed),
   maximum length or maximum steps. */
function traceStream(F,x0,y0,dir,w,o){
 const h=o.h,pts=[[x0,y0]];let x=x0,y=y0,len=0,reason='max-steps',maxSpeed=0;
 const unit=(px,py)=>{const f=F(px,py);if(!f)return null;const m=Math.hypot(f[0],f[1]);if(!Number.isFinite(m))return null;if(m>maxSpeed)maxSpeed=m;return {u:dir*f[0]/m,v:dir*f[1]/m,m};};
 const inside=(px,py)=>px>=w.xmin&&px<=w.xmax&&py>=w.ymin&&py<=w.ymax;
 if(!inside(x0,y0))return {points:pts,reason:'outside',length:0};
 for(let step=0;step<o.maxSteps;step++){
  const f0=F(x,y);
  if(!f0){reason='non-finite';break;}
  const m0=Math.hypot(f0[0],f0[1]);
  if(!(m0>1e-12*Math.max(1,maxSpeed))){reason='stagnation';break;}
  const k1=unit(x,y),k2=k1&&unit(x+h/2*k1.u,y+h/2*k1.v),k3=k2&&unit(x+h/2*k2.u,y+h/2*k2.v),k4=k3&&unit(x+h*k3.u,y+h*k3.v);
  if(!k4){reason='non-finite';break;}
  if([k2,k3,k4].some(k=>k1.u*k.u+k1.v*k.v<0)){reason=k1.m<0.05*maxSpeed?'stagnation':'singular';break;}
  let nx=x+h/6*(k1.u+2*k2.u+2*k3.u+k4.u),ny=y+h/6*(k1.v+2*k2.v+2*k3.v+k4.v);
  if(!inside(nx,ny)){
   let t=1;const dx=nx-x,dy=ny-y;
   if(nx>w.xmax)t=Math.min(t,(w.xmax-x)/dx);if(nx<w.xmin)t=Math.min(t,(w.xmin-x)/dx);
   if(ny>w.ymax)t=Math.min(t,(w.ymax-y)/dy);if(ny<w.ymin)t=Math.min(t,(w.ymin-y)/dy);
   t=Math.max(0,Math.min(1,t));nx=x+t*dx;ny=y+t*dy;
   len+=Math.hypot(nx-x,ny-y);pts.push([nx,ny]);reason='edge';break;
  }
  len+=Math.hypot(nx-x,ny-y);x=nx;y=ny;pts.push([x,y]);
  if(len>=o.maxLength){reason='max-length';break;}
  if(o.closed&&len>8*h&&Math.hypot(x-x0,y-y0)<0.6*h){reason='closed';break;}
 }
 return {points:pts,reason,length:len};
}
function streamOptions(w,o){
 const diag=Math.hypot(w.xmax-w.xmin,w.ymax-w.ymin),frac=stepFraction(o.step);
 const maxLength=o.maxLength===undefined?3*diag:finite(o.maxLength,'Maximum length');
 if(!(maxLength>0))fail('Maximum length must be positive.');
 const h=frac*diag;
 const maxSteps=Math.min(MAX_STEPS,Math.ceil(maxLength/h)+2);
 return {h,maxLength,maxSteps,closed:o.closed!==false};
}
function directionOf(o){const d=o.direction??'both';if(!['forward','backward','both'].includes(d))fail('Direction must be forward, backward or both.');return d;}
function streamlineOf(F,seed,o={}){
 const w=windowOf(o),opt=streamOptions(w,o),d=directionOf(o);
 const x0=finite(seed?.[0],'Seed x'),y0=finite(seed?.[1],'Seed y');
 const fwd=d!=='backward'?traceStream(F,x0,y0,1,w,opt):null;
 const bwd=d!=='forward'&&!(fwd&&fwd.reason==='closed')?traceStream(F,x0,y0,-1,w,opt):null;
 const points=(bwd?bwd.points.slice(1).reverse():[]).concat(fwd?fwd.points:[[x0,y0]]);
 return {type:'streamline',seed:[x0,y0],points,forward:fwd&&{reason:fwd.reason,length:fwd.length,count:fwd.points.length},
  backward:bwd&&{reason:bwd.reason,length:bwd.length,count:bwd.points.length},step:opt.h};
}
function streamline(pExpr,qExpr,seed,o={}){return streamlineOf(fieldOf(pExpr,qExpr),seed,o);}
function autoSeeds(w,n){
 const k=intIn(n,MIN_GRID,MAX_AUTO,'Auto seed grid'),L=lattice(w,k,k),out=[];
 for(let j=0;j<k;j++)for(let i=0;i<k;i++)out.push([L.X(i),L.Y(j)]);
 return out;
}
function seedList(seeds,w,o){
 const list=(Array.isArray(seeds)?seeds:[]).slice();
 if(o.autoSeeds)list.push(...autoSeeds(w,o.autoSeeds));
 if(list.length>MAX_SEEDS+MAX_AUTO*MAX_AUTO)fail('Too many seeds.');
 return list;
}
function streamlines(pExpr,qExpr,seeds,o={}){
 const F=fieldOf(pExpr,qExpr),w=windowOf(o);
 return seedList(seeds,w,o).map(s=>streamlineOf(F,s,o));
}

/* Slope field dy/dx = f(x, y): unit line elements at cell centres. */
function slopeFieldOf(f,o={}){
 const w=windowOf(o),nx=gridSize(o,'nx'),ny=gridSize(o,'ny'),L=lattice(w,nx,ny);
 const marks=[];let nonFinite=0;
 for(let j=0;j<ny;j++)for(let i=0;i<nx;i++){const x=L.X(i),y=L.Y(j),s=f(x,y);if(!Number.isFinite(s))nonFinite++;marks.push({x,y,slope:s});}
 if(nonFinite===marks.length)fail('f(x, y) is not finite at any grid point. Check the expression and the window.');
 return {type:'slope',marks,nonFinite,grid:[nx,ny],window:w};
}
function slopeField(fExpr,o={}){return slopeFieldOf(slopeOf(fExpr),o);}
/* Solution through (x0, y0) by classical RK4 in x with h = stepFraction x (x span), x_k = x0 + k h.
   Stops: window edge (clipped), non-finite slope, steep (|f| h above 2% of the y span: the curve is
   leaving the graph of a function, e.g. a vertical tangent) or maximum steps. */
function traceSlope(f,x0,y0,dir,w,h){
 const pts=[[x0,y0]],span=w.ymax-w.ymin;let x=x0,y=y0,reason='max-steps';
 const steps=Math.min(MAX_STEPS,Math.ceil((w.xmax-w.xmin)/h)+2);
 for(let k=1;k<=steps;k++){
  const s=dir*h,k1=f(x,y),k2=f(x+s/2,y+s/2*k1),k3=f(x+s/2,y+s/2*k2),k4=f(x+s,y+s*k3);
  if(![k1,k2,k3,k4].every(Number.isFinite)){reason='non-finite';break;}
  if(Math.max(Math.abs(k1),Math.abs(k2),Math.abs(k3),Math.abs(k4))*h>0.02*span){reason='steep';break;}
  let nx=x0+dir*k*h,ny=y+s/6*(k1+2*k2+2*k3+k4);
  const xEdge=dir>0?w.xmax:w.xmin;
  let t=1;
  if(dir>0?nx>xEdge:nx<xEdge)t=(xEdge-x)/(nx-x);
  if(ny>w.ymax)t=Math.min(t,(w.ymax-y)/(ny-y));if(ny<w.ymin)t=Math.min(t,(w.ymin-y)/(ny-y));
  if(t<1){t=Math.max(0,t);nx=x+t*(nx-x);ny=y+t*(ny-y);pts.push([nx,ny]);reason='edge';break;}
  x=nx;y=ny;pts.push([x,y]);
  if(x===xEdge){reason='edge';break;}
 }
 return {points:pts,reason};
}
function solutionOf(f,point,o={}){
 const w=windowOf(o),h=stepFraction(o.step)*(w.xmax-w.xmin);
 const x0=finite(point?.[0],'Point x'),y0=finite(point?.[1],'Point y');
 if(x0<w.xmin||x0>w.xmax||y0<w.ymin||y0>w.ymax)fail('The point ('+x0+', '+y0+') is outside the window.');
 if(!Number.isFinite(f(x0,y0)))fail('f is not finite at ('+x0+', '+y0+').');
 const fwd=traceSlope(f,x0,y0,1,w,h),bwd=traceSlope(f,x0,y0,-1,w,h);
 return {type:'solution',seed:[x0,y0],points:bwd.points.slice(1).reverse().concat(fwd.points),
  forward:{reason:fwd.reason,count:fwd.points.length},backward:{reason:bwd.reason,count:bwd.points.length},step:h};
}
function solution(fExpr,point,o={}){return solutionOf(slopeOf(fExpr),point,o);}

/* Heuristic candidate equilibria: lattice cells whose four corner samples bracket zero in both
   P and Q, refined by damped Newton with a central-difference Jacobian and kept only if the
   refined point stays near the cell. Linearization type is indicative only. */
function equilibriaOf(F,o={}){
 const w=windowOf(o),nx=gridSize(o,'nx'),ny=gridSize(o,'ny'),L=lattice(w,nx,ny);
 const V=[];for(let j=0;j<ny;j++)for(let i=0;i<nx;i++)V.push(F(L.X(i),L.Y(j)));
 const at=(i,j)=>V[j*nx+i];
 const scale=Math.max(1,...V.filter(Boolean).map(v=>Math.hypot(v[0],v[1])));
 const jac=(x,y)=>{const dx=1e-6*Math.max(1,Math.abs(x),L.hx),dy=1e-6*Math.max(1,Math.abs(y),L.hy);
  const a=F(x+dx,y),b=F(x-dx,y),c=F(x,y+dy),d=F(x,y-dy);if(!a||!b||!c||!d)return null;
  return [[(a[0]-b[0])/(2*dx),(c[0]-d[0])/(2*dy)],[(a[1]-b[1])/(2*dx),(c[1]-d[1])/(2*dy)]];};
 const found=[];
 for(let j=0;j<ny-1;j++)for(let i=0;i<nx-1;i++){
  const c=[at(i,j),at(i+1,j),at(i+1,j+1),at(i,j+1)];
  if(!c.every(Boolean))continue;
  const brackets=k=>Math.min(...c.map(v=>v[k]))<=0&&Math.max(...c.map(v=>v[k]))>=0;
  if(!brackets(0)||!brackets(1))continue;
  const cx=L.X(i)+L.hx/2,cy=L.Y(j)+L.hy/2;
  let x=cx,y=cy,refined=false,res=NaN;
  for(let it=0;it<30;it++){
   const f=F(x,y),J=f&&jac(x,y);if(!J)break;
   res=Math.hypot(f[0],f[1]);
   if(res<=1e-10*scale){refined=true;break;}
   const det=J[0][0]*J[1][1]-J[0][1]*J[1][0];if(!Number.isFinite(det)||Math.abs(det)<1e-300)break;
   x-=(J[1][1]*f[0]-J[0][1]*f[1])/det;y-=(-J[1][0]*f[0]+J[0][0]*f[1])/det;
   if(!Number.isFinite(x)||!Number.isFinite(y))break;
  }
  const near=refined&&Math.abs(x-cx)<=1.5*L.hx&&Math.abs(y-cy)<=1.5*L.hy;
  const px=near?x:cx,py=near?y:cy;
  if(found.some(e=>Math.abs(e.x-px)<=L.hx/2&&Math.abs(e.y-py)<=L.hy/2))continue;
  let kind='unclassified';
  const J=near&&jac(px,py);
  if(J){const tr=J[0][0]+J[1][1],det=J[0][0]*J[1][1]-J[0][1]*J[1][0],disc=tr*tr-4*det,tol=1e-6*Math.max(1,Math.abs(tr),Math.abs(det));
   if(det<-tol)kind='saddle';else if(Math.abs(det)<=tol)kind='degenerate';
   else if(Math.abs(tr)<=tol)kind='center (linearization)';else kind=(tr<0?'stable ':'unstable ')+(disc<0?'spiral':'node');}
  found.push({x:px,y:py,refined:near,residual:near?res:NaN,cell:[i,j],kind});
  if(found.length>=50)break;
 }
 return found;
}
function equilibria(pExpr,qExpr,o={}){return equilibriaOf(fieldOf(pExpr,qExpr),o);}

/* ---------- Rendering ---------- */
const PAD={l:72,r:86,t:16,b:44};
function niceStep(span,count){const raw=span/Math.max(1,count),p=Math.pow(10,Math.floor(Math.log10(raw))),m=raw/p;return (m<=1?1:m<=2?2:m<=2.5?2.5:m<=5?5:10)*p;}
const fmt=v=>{const a=Math.abs(v);if(a<1e-12)return '0';if(a>=1e5||a<1e-3)return v.toExponential(2);return String(Number(v.toPrecision(6)));};
const STOPS=[[0,[37,52,148]],[.35,[44,127,184]],[.6,[26,152,80]],[.8,[217,95,2]],[1,[178,24,43]]];
function colorAt(t){
 t=Math.max(0,Math.min(1,Number.isFinite(t)?t:0));
 for(let k=1;k<STOPS.length;k++)if(t<=STOPS[k][0]){const [a,ca]=STOPS[k-1],[b,cb]=STOPS[k],s=(t-a)/(b-a);return 'rgb('+ca.map((c,i)=>Math.round(c+(cb[i]-c)*s)).join(',')+')';}
 return 'rgb(178,24,43)';
}
function view(canvas,w){
 const W=canvas.width,H=canvas.height,pw=W-PAD.l-PAD.r,ph=H-PAD.t-PAD.b;
 const sx=pw/(w.xmax-w.xmin),sy=ph/(w.ymax-w.ymin);
 return {W,H,pw,ph,sx,sy,px:x=>PAD.l+(x-w.xmin)*sx,py:y=>PAD.t+(w.ymax-y)*sy,
  toWorld:(X,Y)=>[w.xmin+(X-PAD.l)/sx,w.ymax-(Y-PAD.t)/sy],inPlot:(X,Y)=>X>=PAD.l&&X<=PAD.l+pw&&Y>=PAD.t&&Y<=PAD.t+ph};
}
function axes(ctx,v,w){
 ctx.clearRect(0,0,v.W,v.H);ctx.fillStyle='#ffffff';ctx.fillRect(0,0,v.W,v.H);
 ctx.font='17px system-ui,sans-serif';ctx.lineWidth=1;
 const stepX=niceStep(w.xmax-w.xmin,Math.max(3,Math.round(v.pw/90))),stepY=niceStep(w.ymax-w.ymin,Math.max(3,Math.round(v.ph/70)));
 ctx.strokeStyle='#e4ecee';ctx.fillStyle='#3d5960';ctx.textAlign='center';ctx.textBaseline='top';
 for(let t=Math.ceil(w.xmin/stepX)*stepX;t<=w.xmax+stepX*1e-9;t+=stepX){const X=v.px(t);ctx.beginPath();ctx.moveTo(X,PAD.t);ctx.lineTo(X,v.H-PAD.b);ctx.stroke();ctx.fillText(fmt(t),X,v.H-PAD.b+6);}
 ctx.textAlign='right';ctx.textBaseline='middle';
 for(let t=Math.ceil(w.ymin/stepY)*stepY;t<=w.ymax+stepY*1e-9;t+=stepY){const Y=v.py(t);ctx.beginPath();ctx.moveTo(PAD.l,Y);ctx.lineTo(v.W-PAD.r,Y);ctx.stroke();ctx.fillText(fmt(t),PAD.l-6,Y);}
 ctx.strokeStyle='#5d7c84';ctx.lineWidth=1.6;ctx.beginPath();
 if(w.ymin<=0&&w.ymax>=0){ctx.moveTo(PAD.l,v.py(0));ctx.lineTo(v.W-PAD.r,v.py(0));}
 if(w.xmin<=0&&w.xmax>=0){ctx.moveTo(v.px(0),PAD.t);ctx.lineTo(v.px(0),v.H-PAD.b);}
 ctx.stroke();ctx.strokeStyle='#9fb5ba';ctx.lineWidth=1;ctx.strokeRect(PAD.l,PAD.t,v.pw,v.ph);
 ctx.fillStyle='#27444b';ctx.textAlign='right';ctx.textBaseline='bottom';ctx.fillText('x',v.W-PAD.r-4,v.H-PAD.b-4);
 ctx.textAlign='left';ctx.textBaseline='top';ctx.fillText('y',PAD.l+6,PAD.t+4);
}
function colorBar(ctx,v,lo,hi){
 const x=v.W-PAD.r+20,y0=PAD.t+44,hgt=Math.min(260,v.ph-90);
 for(let k=0;k<hgt;k++){ctx.fillStyle=colorAt(1-k/hgt);ctx.fillRect(x,y0+k,16,1.5);}
 ctx.strokeStyle='#5d7c84';ctx.lineWidth=1;ctx.strokeRect(x,y0,16,hgt);
 ctx.fillStyle='#27444b';ctx.font='13px system-ui,sans-serif';ctx.textAlign='left';ctx.textBaseline='bottom';
 ctx.fillText('|v|',x,y0-22);ctx.fillText(fmt(Number(hi.toPrecision(4))),x-4,y0-4);
 ctx.textBaseline='top';ctx.fillText(fmt(Number(lo.toPrecision(4))),x-4,y0+hgt+4);
}
function polyline(ctx,v,pts){if(!pts||!pts.length)return;ctx.moveTo(v.px(pts[0][0]),v.py(pts[0][1]));for(let k=1;k<pts.length;k++)ctx.lineTo(v.px(pts[k][0]),v.py(pts[k][1]));}
/* scene: {mode:'vector', quiver, lines:[streamline], equilibria} or {mode:'slope', field, lines:[solution]} */
function draw(canvas,scene){
 const ctx=canvas.getContext('2d'),w=(scene.quiver||scene.field).window,v=view(canvas,w);
 ctx.save();axes(ctx,v,w);
 ctx.save();ctx.beginPath();ctx.rect(PAD.l,PAD.t,v.pw,v.ph);ctx.clip();
 if(scene.mode==='vector'){
  const q=scene.quiver,cw=v.pw/q.grid[0],ch=v.ph/q.grid[1],len=0.42*Math.min(cw,ch),span=q.maxMag-q.minMag;
  ctx.lineWidth=1.8;ctx.lineCap='round';
  for(const a of q.arrows){
   if(!Number.isFinite(a.mag))continue;
   const X=v.px(a.x),Y=v.py(a.y),c=colorAt(span>0?(a.mag-q.minMag)/span:.5);
   ctx.strokeStyle=c;ctx.fillStyle=c;
   let dx=a.u*v.sx,dy=-a.v*v.sy;const m=Math.hypot(dx,dy);
   if(!(m>0)){ctx.beginPath();ctx.arc(X,Y,2,0,2*Math.PI);ctx.fill();continue;}
   dx=dx/m*len;dy=dy/m*len;
   ctx.beginPath();ctx.moveTo(X-dx,Y-dy);ctx.lineTo(X+dx,Y+dy);ctx.stroke();
   const hx=X+dx,hy=Y+dy,ux=dx/len,uy=dy/len,s=Math.min(7,len*.55);
   ctx.beginPath();ctx.moveTo(hx,hy);ctx.lineTo(hx-s*ux+s*.5*uy,hy-s*uy-s*.5*ux);ctx.lineTo(hx-s*ux-s*.5*uy,hy-s*uy+s*.5*ux);ctx.closePath();ctx.fill();
  }
  ctx.strokeStyle='#111827';ctx.lineWidth=2.2;ctx.lineJoin='round';ctx.beginPath();
  for(const s of scene.lines)polyline(ctx,v,s.points);
  ctx.stroke();
 }else{
  const f=scene.field,cw=v.pw/f.grid[0],ch=v.ph/f.grid[1],len=0.36*Math.min(cw,ch);
  ctx.strokeStyle='#5b7f99';ctx.lineWidth=1.6;ctx.lineCap='round';ctx.beginPath();
  for(const m of f.marks){
   if(!Number.isFinite(m.slope))continue;
   let dx=v.sx,dy=-m.slope*v.sy;const n=Math.hypot(dx,dy);dx=dx/n*len;dy=dy/n*len;
   const X=v.px(m.x),Y=v.py(m.y);ctx.moveTo(X-dx,Y-dy);ctx.lineTo(X+dx,Y+dy);
  }
  ctx.stroke();
  ctx.strokeStyle='#c2410c';ctx.lineWidth=2.6;ctx.lineJoin='round';ctx.beginPath();
  for(const s of scene.lines)polyline(ctx,v,s.points);
  ctx.stroke();
 }
 ctx.fillStyle='#111827';
 for(const s of scene.lines){ctx.beginPath();ctx.arc(v.px(s.seed[0]),v.py(s.seed[1]),3.5,0,2*Math.PI);ctx.fill();}
 if(scene.equilibria){ctx.strokeStyle='#b91c1c';ctx.lineWidth=2.4;for(const e of scene.equilibria){ctx.beginPath();ctx.arc(v.px(e.x),v.py(e.y),8,0,2*Math.PI);ctx.stroke();}}
 ctx.restore();
 if(scene.mode==='vector')colorBar(ctx,v,scene.quiver.minMag,scene.quiver.maxMag);
 ctx.restore();
 return v;
}

/* Data Tables rows: one row per curve point; thinned evenly (keeping endpoints) above 6,000 rows. */
function tableOf(scene){
 const total=scene.lines.reduce((n,s)=>n+s.points.length,0);
 const stride=Math.max(1,Math.ceil(total/MAX_ROWS));
 const rows=[];
 scene.lines.forEach((s,k)=>{s.points.forEach((p,i)=>{if(i%stride===0||i===s.points.length-1)rows.push([k+1,p[0],p[1]]);});});
 return {headers:['curve','x','y'],rows:rows.slice(0,MAX_ROWS),stride};
}

const api={quiver,streamline,streamlines,slopeField,solution,equilibria,draw,table:tableOf,fieldOf,slopeOf,
 limits:{maxGrid:MAX_GRID,maxSeeds:MAX_SEEDS,maxAutoSeeds:MAX_AUTO,maxSteps:MAX_STEPS}};
M.vectorFields=api;

/* ---------- UI (static markup only; user text never reaches innerHTML) ---------- */
const panel=document.getElementById('graph-panel');
if(!panel||document.getElementById('fields-details'))return;
const style=document.createElement('style');style.id='vector-fields-style';
style.textContent='#fields-details{padding:15px 18px;margin:12px 0 20px;border:1px solid #cfdde8;border-radius:13px;background:#f8fbfd;max-width:100%;box-sizing:border-box;min-width:0}'+
'#fields-details>summary{font-weight:780;color:#1d5f86;cursor:pointer;font-size:15px;min-height:40px;display:flex;align-items:center}'+
'#fields-details .fields-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px;margin:14px 0}'+
'#fields-details label{display:flex;flex-direction:column;gap:5px;font-size:12px;font-weight:650;color:#31545a;min-width:0}'+
'#fields-details label.fields-wide{grid-column:span 2}'+
'#fields-details input:not([type=checkbox]),#fields-details select{width:100%;min-width:0;min-height:42px;box-sizing:border-box;padding:9px 10px;border:1px solid #bfd3dc;border-radius:9px;background:#fff;color:#24434b;font:inherit}'+
'#fields-details label.fields-check{flex-direction:row;align-items:center;gap:8px;min-height:42px}'+
'#fields-details input[type=checkbox]{width:22px;height:22px}'+
'#fields-details .fields-actions{display:flex;align-items:center;flex-wrap:wrap;gap:12px;margin-bottom:12px}'+
'#fields-details .fields-actions button{min-height:42px}'+
'#fields-play[aria-pressed=true]{outline:2px solid #1d5f86;outline-offset:1px}'+
'#fields-status,#fields-equilibria{font-size:13px;color:#3f5f68;overflow-wrap:anywhere}'+
'#fields-status.fields-error{color:#b42318;font-weight:650}'+
'#fields-canvas{display:block;width:100%;height:auto;aspect-ratio:3/2;background:#fff;border:1px solid #dce7e7;border-radius:12px;cursor:crosshair}'+
'#fields-details [hidden]{display:none!important}'+
'@media(max-width:760px){#fields-details{padding:12px}#fields-details .fields-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}'+
'@media(max-width:440px){#fields-details .fields-grid{grid-template-columns:minmax(0,1fr)}#fields-details label.fields-wide{grid-column:auto}}';
document.head.appendChild(style);
const root=document.createElement('details');root.id='fields-details';
root.innerHTML='<summary>Vector fields, streamlines &amp; slope fields · (P, Q), dy/dx = f(x, y)</summary>'+
'<p class="small-note">Arrows are normalized to equal length and coloured by |v|. Streamlines follow the direction field with fixed-step RK4 (step = fraction × window diagonal) and stop at the window edge, near stagnation points, at direction reversals (poles), at non-finite values, on returning to the seed, or at the length limit. Slope-field solutions use RK4 in x forward and backward and stop where the slope becomes too steep. Candidate equilibria are a sign-change heuristic refined by Newton; check them analytically. Click the plot to add a seed.</p>'+
'<div class="fields-grid">'+
'<label for="fields-mode">Plot type<select id="fields-mode"><option value="vector">Vector field (P, Q) + streamlines</option><option value="slope">Slope field dy/dx = f(x, y)</option></select></label>'+
'<label for="fields-p" data-fields="vector">P(x, y) (x-component)<input id="fields-p" type="text" spellcheck="false" autocomplete="off" value="-y"></label>'+
'<label for="fields-q" data-fields="vector">Q(x, y) (y-component)<input id="fields-q" type="text" spellcheck="false" autocomplete="off" value="x"></label>'+
'<label for="fields-f" class="fields-wide" data-fields="slope" hidden>f(x, y) in dy/dx = f(x, y)<input id="fields-f" type="text" spellcheck="false" autocomplete="off" value="x - y"></label>'+
'<label for="fields-grid-n">Grid per axis (2–40)<input id="fields-grid-n" type="number" min="2" max="40" step="1" value="20"></label>'+
'<label for="fields-xmin">x min<input id="fields-xmin" type="number" step="any" value="-2"></label>'+
'<label for="fields-xmax">x max<input id="fields-xmax" type="number" step="any" value="2"></label>'+
'<label for="fields-ymin">y min<input id="fields-ymin" type="number" step="any" value="-2"></label>'+
'<label for="fields-ymax">y max<input id="fields-ymax" type="number" step="any" value="2"></label>'+
'<label for="fields-seeds" class="fields-wide">Seed points x, y; x, y (or click the plot)<input id="fields-seeds" type="text" spellcheck="false" autocomplete="off" value="1, 0"></label>'+
'<label for="fields-step">Step (fraction of window, 0.0001–0.05)<input id="fields-step" type="number" min="0.0001" max="0.05" step="any" value="0.0025"></label>'+
'<label for="fields-auto-n" data-fields="vector">Auto seed grid (2–12)<input id="fields-auto-n" type="number" min="2" max="12" step="1" value="4"></label>'+
'<label for="fields-auto" class="fields-check" data-fields="vector"><input id="fields-auto" type="checkbox" checked> Auto seed streamlines</label>'+
'<label for="fields-eq" class="fields-check" data-fields="vector"><input id="fields-eq" type="checkbox" checked> Show candidate equilibria</label>'+
'</div>'+
'<div class="fields-actions"><button id="fields-plot" type="button" class="primary">Plot field</button><button id="fields-play" type="button" class="secondary" aria-pressed="false" data-fields="vector" disabled>Play particles</button><button id="fields-clear-seeds" type="button" class="secondary">Clear seeds</button><button id="fields-save" type="button" class="secondary" disabled>Save curve points to Data Tables</button></div>'+
'<p id="fields-status" role="status" aria-live="polite">Ready. Enter a field and press Plot field.</p>'+
'<p id="fields-equilibria" class="small-note"></p>'+
'<canvas id="fields-canvas" width="900" height="600" role="img" aria-label="Vector or slope field plot (not yet plotted)"></canvas>';
const anchor=document.getElementById('curves-details');
if(anchor&&panel.contains(anchor))anchor.after(root);else (panel.querySelector('.graph-wrap')||panel).appendChild(root);

const $=id=>document.getElementById(id);
const canvas=$('fields-canvas'),status=$('fields-status'),playBtn=$('fields-play');
let last=null,lastView=null,base=null,userPaused=false;
const setStatus=(text,error)=>{status.textContent=text;status.classList.toggle('fields-error',!!error);};
const mode=()=>$('fields-mode').value;
const syncMode=()=>{root.querySelectorAll('[data-fields]').forEach(el=>{el.hidden=el.getAttribute('data-fields')!==mode();});};
const g=v=>Number(Number(v).toPrecision(4));
/* Point coordinates: round-off below 1e-9 of the window span prints as 0. */
const pt=(e,w)=>{const c=(v,span)=>Math.abs(v)<1e-9*span?0:g(v);return '('+c(e.x,w.xmax-w.xmin)+', '+c(e.y,w.ymax-w.ymin)+')';};
function parseSeeds(text){
 const s=String(text??'').trim();if(!s)return [];
 const parts=s.split(/[;\n]+/).map(p=>p.trim()).filter(Boolean);
 if(parts.length>MAX_SEEDS)fail('At most '+MAX_SEEDS+' seed points.');
 return parts.map((p,k)=>{const xy=p.replace(/[()]/g,'').split(',').map(t=>t.trim());
  if(xy.length!==2)fail('Seed '+(k+1)+' must be "x, y" (separate points with ";").');
  return [finite(xy[0],'Seed '+(k+1)+' x'),finite(xy[1],'Seed '+(k+1)+' y')];});
}
const reasonText=r=>({edge:'edge','non-finite':'non-finite','stagnation':'stagnation',singular:'singular',closed:'closed orbit','max-length':'length limit','max-steps':'step limit',steep:'steep',outside:'outside window'}[r]||r);
const countReasons=lines=>{const c={};for(const s of lines)for(const d of [s.forward,s.backward])if(d)c[d.reason]=(c[d.reason]||0)+1;return Object.keys(c).map(k=>c[k]+' '+reasonText(k)).join(', ');};

/* ---------- Particle advection (user-controlled; no autoplay under prefers-reduced-motion) ---------- */
const reducedMotion=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches===true;
const MAX_FRAMES=900,PARTICLES=80;
const anim={raf:0,playing:false,frames:0,particles:[],rng:1};
const rand=()=>{anim.rng=(anim.rng*1664525+1013904223)>>>0;return anim.rng/4294967296;};
function spawn(w){return {x:w.xmin+rand()*(w.xmax-w.xmin),y:w.ymin+rand()*(w.ymax-w.ymin),age:Math.floor(rand()*120)};}
function setPlaying(on){anim.playing=on;playBtn.setAttribute('aria-pressed',String(on));playBtn.textContent=on?'Pause particles':'Play particles';}
function stopAnim(){if(anim.raf)cancelAnimationFrame(anim.raf);anim.raf=0;setPlaying(false);if(base&&last)canvas.getContext('2d').drawImage(base,0,0);}
function frame(){
 anim.raf=0;
 if(!anim.playing||!last||last.mode!=='vector'||!base){stopAnim();return;}
 anim.frames++;
 const w=last.quiver.window,F=last.F,h=0.006*Math.hypot(w.xmax-w.xmin,w.ymax-w.ymin),ctx=canvas.getContext('2d');
 ctx.drawImage(base,0,0);ctx.save();ctx.beginPath();ctx.rect(PAD.l,PAD.t,lastView.pw,lastView.ph);ctx.clip();ctx.fillStyle='rgba(17,24,39,.82)';
 for(let k=0;k<anim.particles.length;k++){
  let p=anim.particles[k];const a=F(p.x,p.y),ma=a&&Math.hypot(a[0],a[1]);
  let ok=a&&ma>0&&Number.isFinite(ma);
  if(ok){const mx=p.x+h/2*a[0]/ma,my=p.y+h/2*a[1]/ma,b=F(mx,my),mb=b&&Math.hypot(b[0],b[1]);ok=b&&mb>0&&Number.isFinite(mb);if(ok){p.x+=h*b[0]/mb;p.y+=h*b[1]/mb;}}
  p.age++;
  if(!ok||p.age>160||p.x<w.xmin||p.x>w.xmax||p.y<w.ymin||p.y>w.ymax){p=anim.particles[k]=spawn(w);p.age=0;}
  ctx.beginPath();ctx.arc(lastView.px(p.x),lastView.py(p.y),2.6,0,2*Math.PI);ctx.fill();
 }
 ctx.restore();
 if(anim.frames>=MAX_FRAMES){stopAnim();setStatus(status.textContent.replace(/ Particles.*$/,'')+' Particles paused after '+MAX_FRAMES+' frames; press Play to continue.',false);return;}
 anim.raf=requestAnimationFrame(frame);
}
function playAnim(){
 if(!last||last.mode!=='vector')return;
 const w=last.quiver.window;anim.rng=12345;anim.frames=0;anim.particles=Array.from({length:PARTICLES},()=>spawn(w));
 setPlaying(true);if(!anim.raf)anim.raf=requestAnimationFrame(frame);
}

function plot(){
 if(anim.playing){if(anim.raf)cancelAnimationFrame(anim.raf);anim.raf=0;setPlaying(false);}
 try{
  const o={xmin:$('fields-xmin').value,xmax:$('fields-xmax').value,ymin:$('fields-ymin').value,ymax:$('fields-ymax').value,grid:$('fields-grid-n').value,step:$('fields-step').value};
  const w=windowOf(o),seeds=parseSeeds($('fields-seeds').value);
  let scene,summary,label;
  if(mode()==='vector'){
   const F=fieldOf($('fields-p').value,$('fields-q').value);
   const q=quiverOf(F,o);
   const all=seeds.concat($('fields-auto').checked?autoSeeds(w,$('fields-auto-n').value):[]);
   const lines=all.filter(s=>s[0]>=w.xmin&&s[0]<=w.xmax&&s[1]>=w.ymin&&s[1]<=w.ymax).map(s=>streamlineOf(F,s,o));
   const eq=$('fields-eq').checked?equilibriaOf(F,o):null;
   scene={mode:'vector',F,quiver:q,lines,equilibria:eq};
   summary='Vector field: '+(q.arrows.length-q.nonFinite)+' finite of '+q.arrows.length+' arrows on a '+q.grid[0]+'×'+q.grid[1]+' grid; |v| from '+g(q.minMag)+' to '+g(q.maxMag)+'; '+lines.length+' streamline'+(lines.length===1?'':'s')+(lines.length?' (ends: '+countReasons(lines)+')':'')+'.'+
    (q.nonFinite?' '+q.nonFinite+' non-finite grid point'+(q.nonFinite===1?'':'s')+' skipped.':'')+(all.length>lines.length?' '+(all.length-lines.length)+' seed(s) outside the window ignored.':'');
   label='Vector field P = '+F.p+', Q = '+F.q+' for x from '+g(w.xmin)+' to '+g(w.xmax)+', y from '+g(w.ymin)+' to '+g(w.ymax)+': '+q.arrows.length+' arrows, magnitude '+g(q.minMag)+' to '+g(q.maxMag)+', '+lines.length+' streamlines'+(eq&&eq.length?', candidate equilibria at '+eq.slice(0,4).map(e=>pt(e,w)).join(', '):'');
   $('fields-equilibria').textContent=eq?(eq.length?'Candidate equilibria (heuristic): '+eq.slice(0,8).map(e=>pt(e,w)+(e.refined?' '+e.kind:' unrefined cell centre')).join('; ')+(eq.length>8?'; …':'')+'.':'No candidate equilibria found on this grid.'):'';
  }else{
   const f=slopeOf($('fields-f').value),field=slopeFieldOf(f,o);
   const lines=seeds.map(s=>solutionOf(f,s,o));
   scene={mode:'slope',field,lines};
   summary='Slope field: '+(field.marks.length-field.nonFinite)+' finite of '+field.marks.length+' line elements; '+lines.length+' solution curve'+(lines.length===1?'':'s')+(lines.length?' (ends: '+countReasons(lines)+')':'')+'.'+(field.nonFinite?' '+field.nonFinite+' non-finite grid point'+(field.nonFinite===1?'':'s')+' skipped.':'')+(lines.length?'':' Add points to draw solution curves.');
   label='Slope field dy/dx = '+f.expr+' for x from '+g(w.xmin)+' to '+g(w.xmax)+', y from '+g(w.ymin)+' to '+g(w.ymax)+' with '+lines.length+' solution curves';
   $('fields-equilibria').textContent='';
  }
  lastView=draw(canvas,scene);
  base=document.createElement('canvas');base.width=canvas.width;base.height=canvas.height;base.getContext('2d').drawImage(canvas,0,0);
  canvas.setAttribute('aria-label',label.slice(0,400));
  last=scene;
  $('fields-save').disabled=!scene.lines.length;
  playBtn.disabled=scene.mode!=='vector';
  setStatus(summary,false);
  if(scene.mode==='vector'&&!userPaused&&!reducedMotion())playAnim();
 }catch(err){
  last=null;base=null;$('fields-save').disabled=true;playBtn.disabled=true;
  setStatus('Error: '+err.message,true);
 }
}
$('fields-mode').addEventListener('change',()=>{stopAnim();syncMode();last=null;base=null;$('fields-save').disabled=true;playBtn.disabled=true;$('fields-equilibria').textContent='';
 $('fields-seeds').value=mode()==='slope'?'0, 1; 0, -1':'1, 0';setStatus('Ready. Press Plot field.',false);});
$('fields-plot').addEventListener('click',plot);
playBtn.addEventListener('click',()=>{if(anim.playing){userPaused=true;stopAnim();}else{userPaused=false;playAnim();}});
$('fields-clear-seeds').addEventListener('click',()=>{$('fields-seeds').value='';plot();});
root.addEventListener('toggle',()=>{if(!root.open&&anim.playing)stopAnim();});
root.querySelectorAll('input[type=text],input[type=number]').forEach(input=>input.addEventListener('keydown',ev=>{if(ev.key==='Enter'){ev.preventDefault();plot();}}));
canvas.addEventListener('click',ev=>{
 if(!last||!lastView)return;
 const r=canvas.getBoundingClientRect(),X=(ev.clientX-r.left)*canvas.width/r.width,Y=(ev.clientY-r.top)*canvas.height/r.height;
 if(!lastView.inPlot(X,Y))return;
 const [x,y]=lastView.toWorld(X,Y),cur=$('fields-seeds').value.trim();
 if(cur.split(';').filter(s=>s.trim()).length>=MAX_SEEDS){setStatus('Error: At most '+MAX_SEEDS+' seed points. Clear seeds first.',true);return;}
 $('fields-seeds').value=(cur?cur+'; ':'')+g(x)+', '+g(y);plot();
});
$('fields-save').addEventListener('click',()=>{
 try{
  if(!last||!last.lines.length)fail('Plot curves first.');
  if(!M.dataTables?.importData)fail('Data Tables are unavailable.');
  const t=tableOf(last),name=last.mode==='vector'?'Streamlines':'Slope_Solutions';
  M.dataTables.importData({headers:t.headers,rows:t.rows},name);
  setStatus('Saved '+t.rows.length+' points from '+last.lines.length+' curve'+(last.lines.length===1?'':'s')+' to Data Tables as '+name+(t.stride>1?' (every '+t.stride+'th point kept to stay within 6,000 rows).':'.'),false);
 }catch(err){setStatus('Error: '+err.message,true);}
});
syncMode();
api.plot=plot;api.play=()=>{userPaused=false;playAnim();};api.pause=()=>{userPaused=true;stopAnim();};
api.animation={get playing(){return anim.playing;},get frames(){return anim.frames;}};
api.parseSeeds=parseSeeds;
})();
