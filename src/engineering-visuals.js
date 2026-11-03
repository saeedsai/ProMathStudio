/* Engineering Toolbox animated visuals. Each visual reuses an existing canonical solver
   (RK4 system, FFT, safe numeric evaluator, adaptive Simpson, symmetric eigen); none adds
   a new math kernel. Illustrations, not certified engineering analyses. SPDX-License-Identifier: MIT. */
(()=>{'use strict';
const M=window.MathStudio,host=document.getElementById('engineering-panel');
if(!M?.engineeringCatalog||!M?.engineeringSimulations||!M?.odeTools||!M?.fftTools||!M?.numerical||!M?.matrixTools||!host)return;
const S=M.engineeringSimulations;
const G=9.80665;
const num=(value,label,min,max)=>{
 const text=String(value??'').trim(),n=Number(text);
 if(!text||!Number.isFinite(n)||n<min||n>max)throw Error(label+' must be a number from '+min+' to '+max+'.');
 return n;
};
// Pure computations returning plain data; drawing never recomputes the mathematics.
function springMassDamper({zeta=0.2,wn=2,duration=10}={}){
 zeta=num(zeta,'Damping ratio ζ',0,3);wn=num(wn,'Natural frequency ωn',0.1,20);duration=num(duration,'Duration',1,60);
 // Unit-step forced m·x''+c·x'+k·x=k·u, written as x'=v, v'=ωn²(1−x)−2ζωn·v (existing RK4 system solver).
 const solved=M.odeTools.solveSystem({expression:'z',expressionZ:(wn*wn)+'*(1-y)-'+(2*zeta*wn)+'*z',t0:0,t1:duration,y0:0,z0:0,steps:400});
 const rows=solved.rows.map(([t,x,v])=>[t,x,v]);
 const peak=Math.max(...rows.map(r=>r[1]));
 return {id:'spring',rows,zeta,wn,duration,overshoot:Math.max(0,peak-1),convergence:solved.convergence,
  summary:'Mass–spring–damper unit step: ζ='+zeta+', ωn='+wn+' rad/s; peak overshoot '+(Math.max(0,peak-1)*100).toFixed(2)+'% (RK4, 400 steps).'};
}
function pendulum({theta0=30,length=1,duration=6}={}){
 theta0=num(theta0,'Initial angle (degrees)',-170,170);length=num(length,'Length (m)',0.05,50);duration=num(duration,'Duration',0.5,60);
 const solved=M.odeTools.solveSystem({expression:'z',expressionZ:'-'+(G/length)+'*sin(y)',t0:0,t1:duration,y0:theta0*Math.PI/180,z0:0,steps:600});
 const energy=([,th,om])=>0.5*length*length*om*om+G*length*(1-Math.cos(th));
 const e0=energy(solved.rows[0]),drift=Math.max(...solved.rows.map(r=>Math.abs(energy(r)-e0)))/Math.max(e0,1e-300);
 return {id:'pendulum',rows:solved.rows,theta0,length,duration,smallAnglePeriod:2*Math.PI*Math.sqrt(length/G),relativeEnergyDrift:drift,
  summary:'Nonlinear pendulum θ″=−(g/L)sin θ, θ0='+theta0+'°, L='+length+' m; small-angle period '+(2*Math.PI*Math.sqrt(length/G)).toFixed(4)+' s; RK4 relative energy drift '+drift.toExponential(2)+'.'};
}
function spectrum({f1=5,f2=12,a1=1,a2=0.5}={}){
 const rate=64,n=64;
 f1=num(f1,'Frequency 1 (Hz)',0,31);f2=num(f2,'Frequency 2 (Hz)',0,31);a1=num(a1,'Amplitude 1',0,10);a2=num(a2,'Amplitude 2',0,10);
 const samples=Array.from({length:n},(_,i)=>a1*Math.sin(2*Math.PI*f1*i/rate)+a2*Math.sin(2*Math.PI*f2*i/rate));
 const bins=M.fftTools.fft(samples).slice(0,n/2+1).map((c,k)=>({frequency:k*rate/n,amplitude:(k===0||k===n/2?1:2)*Math.hypot(c.re,c.im)/n}));
 return {id:'spectrum',samples,bins,rate,n,f1,f2,a1,a2,
  summary:'Two-tone signal sampled at 64 Hz (64 samples, 1 Hz bins, Nyquist 32 Hz); one-sided FFT amplitude via the existing FFT. Non-integer frequencies leak into neighbouring bins.'};
}
function bisection({expression='x^3-2*x-5',lo=1,hi=3,steps=14}={}){
 expression=String(expression||'').trim();if(!expression||expression.length>300)throw Error('Enter f(x) (maximum 300 characters).');
 lo=num(lo,'Bracket min',-1e6,1e6);hi=num(hi,'Bracket max',-1e6,1e6);steps=num(steps,'Iterations',1,40);
 if(!(hi>lo))throw Error('Bracket max must exceed bracket min.');
 const f=x=>M.numerical.evaluate(expression,{x});
 let a=lo,b=hi,fa=f(a),fb=f(b);
 if(Math.sign(fa)===Math.sign(fb)&&fa!==0&&fb!==0)throw Error('f(min) and f(max) must have opposite signs for a bracket.');
 const brackets=[[a,b]];
 for(let i=0;i<Math.round(steps)&&fa!==0&&fb!==0;i++){
  const m=a+(b-a)/2,fm=f(m);
  if(fm===0){a=b=m;brackets.push([a,b]);break;}
  if(Math.sign(fm)===Math.sign(fa)){a=m;fa=fm;}else{b=m;fb=fm;}
  brackets.push([a,b]);
 }
 const curve=Array.from({length:201},(_,i)=>{const x=lo+(hi-lo)*i/200;let y;try{y=f(x);}catch{y=NaN;}return [x,y];});
 const last=brackets.at(-1);
 return {id:'bisection',expression,lo,hi,brackets,curve,estimate:(last[0]+last[1])/2,width:last[1]-last[0],
  summary:'Bisection bracket for '+expression+' on ['+lo+', '+hi+']: width '+(last[1]-last[0]).toExponential(2)+' after '+(brackets.length-1)+' halvings. Brent refinement uses the same sign-change requirement.'};
}
function quadrature({expression='sin(x)',a=0,b=Math.PI}={}){
 expression=String(expression||'').trim();if(!expression||expression.length>300)throw Error('Enter f(x) (maximum 300 characters).');
 a=num(a,'Lower limit',-1e6,1e6);b=num(b,'Upper limit',-1e6,1e6);if(!(b>a))throw Error('Upper limit must exceed lower limit.');
 const result=M.numerical.adaptiveSimpson({expression,a,b,tolerance:1e-8,maxEvaluations:4096});
 const curve=Array.from({length:201},(_,i)=>{const x=a+(b-a)*i/200;let y;try{y=M.numerical.evaluate(expression,{x});}catch{y=NaN;}return [x,y];});
 return {id:'quadrature',expression,a,b,value:result.value,curve,
  summary:'Adaptive Simpson estimate ∫'+expression+' dx on ['+a+', '+b+'] ≈ '+Number(result.value.toPrecision(10))+' (estimate, not a certified bound).'};
}
function eigenMorph({a=2,b=1,d=1}={}){
 a=num(a,'A11',-10,10);b=num(b,'A12 = A21',-10,10);d=num(d,'A22',-10,10);
 const e=M.matrixTools.eigenSymmetric([[a,b],[b,d]]);
 return {id:'eigen',A:[[a,b],[b,d]],values:e.values,vectors:e.vectors,
  summary:'Symmetric A=[['+a+', '+b+'], ['+b+', '+d+']] maps the unit circle to an ellipse; eigenvalues '+e.values.map(v=>Number(v.toPrecision(6))).join(', ')+' stretch the orthogonal eigenvector directions.'};
}
const visuals=Object.freeze([
 {id:'beam',tool:'structures.beam.deflection',title:'Simulation · Beam deflection, moment and stress',compute:S.beam,fields:[['support','Support','simply','select',[['simply','Simply supported'],['cantilever','Cantilever (fixed left)']]],['load','Load','point','select',[['point','Point load'],['udl','Uniform load']]],['length','Span L (m)','4'],['force','Load P (kN) or w (kN/m)','10'],['position','Point-load position a (m)','2'],['modulus','E (GPa)','200'],['width','Section width b (mm)','100'],['height','Section depth h (mm)','200']]},
 {id:'orbit',tool:'aerospace.orbit.propagation',title:'Simulation · Two-body Earth orbit',compute:S.orbit,fields:[['altitude','Periapsis altitude (km)','500'],['eccentricity','Eccentricity e','0.3'],['orbits','Orbits','1']]},
 {id:'rlc',tool:'circuits.rlc.series.transient',title:'Simulation · Series RLC step response',compute:S.rlc,fields:[['resistance','R (Ω)','4'],['inductance','L (mH)','10'],['capacitance','C (µF)','100'],['voltage','Source V (V)','12']]},
 {id:'projectile',tool:'mechanics.projectile.drag',title:'Simulation · Projectile with air drag',compute:S.projectile,fields:[['speed','Launch speed (m/s)','40'],['angle','Launch angle (°)','45'],['mass','Mass (kg)','0.145'],['diameter','Diameter (mm)','74'],['drag','Drag coefficient Cd','0.47'],['density','Air density (kg/m³)','1.225']]},
 {id:'rod',tool:'thermal.conduction.rod',title:'Simulation · Heat conduction in a rod',compute:S.rodHeat,fields:[['material','Material','aluminium','select',[['aluminium','Aluminium'],['copper','Copper'],['steel','Steel'],['glass','Glass'],['water','Water (still)']]],['length','Rod length (m)','0.5'],['initial','Initial temperature (°C)','20'],['left','Left end (°C)','100'],['right','Right end (°C)','20'],['duration','Duration (s)','900']]},
 {id:'spring',tool:'control.transient.two.state',title:'Mass–spring–damper step response',compute:springMassDamper,fields:[['zeta','Damping ratio ζ','0.2'],['wn','Natural frequency ωn (rad/s)','2'],['duration','Duration (s)','10']]},
 {id:'pendulum',tool:'ode.ivp.scalar',title:'Nonlinear pendulum (coupled RK4)',compute:pendulum,fields:[['theta0','Initial angle (°)','30'],['length','Length L (m)','1'],['duration','Duration (s)','6']]},
 {id:'spectrum',tool:'signals.fft.1d',title:'Two-tone signal and FFT spectrum',compute:spectrum,fields:[['f1','Frequency 1 (Hz)','5'],['a1','Amplitude 1','1'],['f2','Frequency 2 (Hz)','12'],['a2','Amplitude 2','0.5']]},
 {id:'bisection',tool:'numerical.root.brent',title:'Root bracket halving',compute:bisection,fields:[['expression','f(x)','x^3-2*x-5','text'],['lo','Bracket min','1'],['hi','Bracket max','3'],['steps','Iterations','14']]},
 {id:'quadrature',tool:'numerical.quadrature.adaptive',title:'Integral as accumulated area',compute:quadrature,fields:[['expression','f(x)','sin(x)','text'],['a','Lower limit','0'],['b','Upper limit','3.141592653589793']]},
 {id:'eigen',tool:'matrix.eigen.symmetric.small',title:'Symmetric matrix transform and eigenvectors',compute:eigenMorph,fields:[['a','A11','2'],['b','A12 = A21','1'],['d','A22','1']]}
].map(Object.freeze));
const toolIds=new Set(M.engineeringCatalog.tools.filter(t=>t.status==='available').map(t=>t.id));
for(const v of visuals)if(!toolIds.has(v.tool))throw Error('Engineering visual references an unavailable tool: '+v.tool);

const style=document.createElement('style');
style.textContent='#eng-visuals{border:1px solid #d8e4e8;border-radius:12px;padding:13px;margin:12px 0}'+
 '#eng-visuals summary{cursor:pointer;font-weight:700;min-height:40px;display:flex;align-items:center}'+
 '#eng-visual-fields{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:10px 0}'+
 '#eng-visuals .eng-visual-actions{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}'+
 '#eng-visuals .eng-visual-actions button{min-height:40px;padding:8px 14px;border:1px solid #29817b;border-radius:9px;background:#e6f5f2;color:#174b48;cursor:pointer}'+
 '#eng-visuals button:focus-visible,#eng-visuals summary:focus-visible{outline:3px solid #29817b;outline-offset:2px}'+
 '#eng-visual-canvas{display:block;width:100%;height:auto;max-width:100%;border:1px solid #e1eaee;border-radius:10px;background:#fff}'+
 '#eng-visual-status.error{color:#a3262a}#eng-visual-status{font-size:13px;overflow-wrap:anywhere}';
document.head.append(style);
const area=document.createElement('details');area.id='eng-visuals';
area.innerHTML='<summary>Engineering simulations &amp; animations</summary>'+
 '<p class="small-note">Physics-based engineering simulations (beam, orbit, circuit, projectile, heat) and solver animations. Each states its model assumptions; results are textbook-model estimates, not certified designs or code checks. Animations respect reduced-motion preferences.</p>'+
 '<label>Visualization<select id="eng-visual-select"></select></label><div id="eng-visual-fields"></div>'+
 '<div class="eng-visual-actions"><button type="button" id="eng-visual-run">Compute &amp; animate</button><button type="button" id="eng-visual-toggle" aria-pressed="false">Pause</button><button type="button" id="eng-visual-step">Step frame</button></div>'+
 '<canvas id="eng-visual-canvas" width="720" height="320" role="img" aria-label="Engineering animation"></canvas>'+
 '<p id="eng-visual-status" role="status" aria-live="polite">Choose a visualization and press Compute &amp; animate.</p>';
host.append(area); // After results: keeps filter → result keyboard order.
const $=id=>document.getElementById(id),picker=$('eng-visual-select'),fields=$('eng-visual-fields');
const canvas=$('eng-visual-canvas'),ctx=canvas.getContext('2d'),status=$('eng-visual-status'),toggle=$('eng-visual-toggle');
for(const v of visuals){const o=document.createElement('option');o.value=v.id;o.textContent=v.title;picker.append(o);}
const reduced=()=>window.matchMedia?.('(prefers-reduced-motion: reduce)').matches===true;
let current=null,frame=0,playing=false,handle=0;
const FRAMES=180;
function buildFields(){
 const v=visuals.find(x=>x.id===picker.value);fields.replaceChildren();
 for(const [key,label,value,type,options] of v.fields){
  const wrap=document.createElement('label');wrap.textContent=label;
  let input;
  if(type==='select'){input=document.createElement('select');for(const [val,text] of options){const o=document.createElement('option');o.value=val;o.textContent=text;input.append(o);}}
  else{input=document.createElement('input');input.type=type||'number';input.step='any';}
  input.id='eng-visual-'+key;input.value=value;input.dataset.key=key;
  wrap.append(input);fields.append(wrap);
 }
}
function params(){return Object.fromEntries([...fields.querySelectorAll('input,select')].map(i=>[i.dataset.key,i.value]));}
const heat=t=>'hsl('+Math.round(240*(1-Math.max(0,Math.min(1,t))))+',80%,48%)';
function arrow(x1,y1,x2,y2,color){ctx.strokeStyle=color;ctx.fillStyle=color;ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();const a=Math.atan2(y2-y1,x2-x1);ctx.beginPath();ctx.moveTo(x2,y2);ctx.lineTo(x2-8*Math.cos(a-0.4),y2-8*Math.sin(a-0.4));ctx.lineTo(x2-8*Math.cos(a+0.4),y2-8*Math.sin(a+0.4));ctx.closePath();ctx.fill();}
// Shared plotting helpers.
function frameBox(x0,y0,w,h){ctx.strokeStyle='#e1eaee';ctx.lineWidth=1;ctx.strokeRect(x0,y0,w,h);}
function polyline(points,xr,yr,box,color,width=2,limit=points.length){
 const [x0,y0,w,h]=box;ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();let pen=false;
 for(let i=0;i<limit;i++){const [x,y]=points[i];if(!Number.isFinite(y)){pen=false;continue;}
  const px=x0+(x-xr[0])/(xr[1]-xr[0])*w,py=y0+h-(Math.max(yr[0],Math.min(yr[1],y))-yr[0])/(yr[1]-yr[0])*h;
  if(pen)ctx.lineTo(px,py);else{ctx.moveTo(px,py);pen=true;}}
 ctx.stroke();
}
const range=values=>{const f=values.filter(Number.isFinite);let lo=Math.min(...f),hi=Math.max(...f);if(!(hi>lo)){lo-=1;hi+=1;}const pad=(hi-lo)*0.08;return [lo-pad,hi+pad];};
const text=(s,x,y,color='#27444b')=>{ctx.fillStyle=color;ctx.fillText(s,x,y);};
function draw(){
 const W=canvas.width,H=canvas.height,p=frame/FRAMES;
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);ctx.font='13px system-ui,sans-serif';
 if(!current)return;
 const c=current;
 if(c.id==='beam'){
  const s=Math.min(1,p*1.25),x0=60,x1=660,by=100,X=x=>x0+(x1-x0)*x/c.L;
  const dmax=Math.max(1e-300,...c.deflection.map(Math.abs)),k=55/dmax,mmax=Math.max(1e-300,...c.moment.map(Math.abs));
  ctx.lineWidth=7;
  for(let i=0;i<c.x.length-1;i++){ctx.strokeStyle=heat(Math.abs(c.moment[i])/mmax*s);ctx.beginPath();ctx.moveTo(X(c.x[i]),by+s*k*c.deflection[i]);ctx.lineTo(X(c.x[i+1]),by+s*k*c.deflection[i+1]);ctx.stroke();}
  ctx.lineWidth=1;ctx.setLineDash([4,4]);ctx.strokeStyle='#8ebfb8';ctx.beginPath();ctx.moveTo(x0,by);ctx.lineTo(x1,by);ctx.stroke();ctx.setLineDash([]);
  ctx.fillStyle='#597b82';
  if(c.support==='simply'){for(const x of [x0,x1]){ctx.beginPath();ctx.moveTo(x,by+5);ctx.lineTo(x-10,by+22);ctx.lineTo(x+10,by+22);ctx.closePath();ctx.fill();}}
  else{ctx.fillRect(x0-16,by-40,12,80);ctx.strokeStyle='#597b82';for(let yy=by-40;yy<by+40;yy+=10){ctx.beginPath();ctx.moveTo(x0-16,yy+10);ctx.lineTo(x0-26,yy);ctx.stroke();}}
  const sign=c.force>=0?1:-1,len=10+28*s;
  if(c.load==='point'){const i=Math.round(c.position/c.L*200),y=by+s*k*c.deflection[i]-6;arrow(X(c.position),y-len*sign,X(c.position),y,'#ec824f');}
  else for(let i=0;i<=200;i+=20){const y=by+s*k*c.deflection[i]-6;arrow(X(c.x[i]),y-len*sign,X(c.x[i]),y,'#ec824f');}
  const box=[x0,200,x1-x0,90];frameBox(...box);const my=box[1]+box[3]/2,mk=(box[3]/2-6)/mmax;
  ctx.fillStyle='rgba(83,107,232,0.25)';ctx.beginPath();ctx.moveTo(X(0),my);c.x.forEach((x,i)=>ctx.lineTo(X(x),my+s*mk*c.moment[i]));ctx.lineTo(X(c.L),my);ctx.closePath();ctx.fill();
  text('bending moment (sagging plotted downward)',box[0]+6,box[1]+14);
  text('load '+(s*100).toFixed(0)+'%: deflection '+(s*Math.abs(c.maxDeflection)*1000).toPrecision(3)+' mm, σmax '+(s*c.maxStress/1e6).toPrecision(3)+' MPa (shape exaggerated)',x0,22);
 }else if(c.id==='orbit'){
  const b=c.a*Math.sqrt(1-c.e*c.e),sc=Math.min(640/(2*c.a),280/(2*b)),cx=360+c.a*c.e*sc,cy=160,P=(x,y)=>[cx+x*sc,cy-y*sc];
  ctx.fillStyle='#2f6fb3';ctx.beginPath();ctx.arc(cx,cy,c.earthRadius*sc,0,Math.PI*2);ctx.fill();
  ctx.strokeStyle='#c8d6dc';ctx.setLineDash([4,4]);ctx.beginPath();ctx.ellipse(cx-c.a*c.e*sc,cy,c.a*sc,b*sc,0,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
  const k=Math.min(c.path.length-1,Math.round(p*(c.path.length-1)));
  ctx.strokeStyle='#188b81';ctx.lineWidth=2;ctx.beginPath();for(let i=Math.max(0,k-120);i<=k;i++){const [px,py]=P(c.path[i][1],c.path[i][2]);if(i===Math.max(0,k-120))ctx.moveTo(px,py);else ctx.lineTo(px,py);}ctx.stroke();
  const [t,x,y,vx,vy]=c.path[k],[px,py]=P(x,y),speed=Math.hypot(vx,vy);
  arrow(px,py,px+vx/c.vp*40,py-vy/c.vp*40,'#ec824f');ctx.fillStyle='#27444b';ctx.beginPath();ctx.arc(px,py,5,0,Math.PI*2);ctx.fill();
  text('t = '+(t/60).toFixed(1)+' min, altitude '+(Math.hypot(x,y)-c.earthRadius).toFixed(0)+' km, speed '+speed.toFixed(3)+' km/s',20,22);
  text('period '+(c.period/60).toFixed(2)+' min',20,306);
 }else if(c.id==='rlc'){
  const k=Math.min(c.rows.length-1,Math.round(p*(c.rows.length-1))),[t,vc,i]=c.rows[k];
  const vmax=Math.max(1e-300,...c.rows.map(r=>Math.abs(r[1]))),imax=Math.max(1e-300,...c.rows.map(r=>Math.abs(r[2])));
  const L0=40,T0=60,R0=280,B0=260;ctx.strokeStyle='#385d66';ctx.lineWidth=2;ctx.strokeRect(L0,T0,R0-L0,B0-T0);
  ctx.fillStyle='#fff';ctx.fillRect(L0-6,140,12,40);ctx.fillRect(R0-6,145,12,30);ctx.fillRect(95,T0-6,60,12);ctx.fillRect(180,T0-6,70,12);
  ctx.strokeStyle='#385d66';ctx.beginPath();ctx.moveTo(L0-14,150);ctx.lineTo(L0+14,150);ctx.moveTo(L0-7,170);ctx.lineTo(L0+7,170);ctx.stroke();text('V',L0+18,165);
  ctx.beginPath();ctx.moveTo(95,T0);for(let j=1;j<=6;j++)ctx.lineTo(95+j*10,T0+(j%2?-8:8));ctx.lineTo(155,T0);ctx.stroke();text('R',120,T0-14);
  ctx.beginPath();for(let j=0;j<4;j++)ctx.arc(189+j*17,T0,8.5,Math.PI,0);ctx.stroke();text('L',210,T0-14);
  const fill=Math.abs(vc)/vmax;ctx.fillStyle=heat(fill);ctx.fillRect(R0-16,145,32,5);ctx.fillRect(R0-16,170,32,5);text('C',R0+20,165);
  const perim=2*((R0-L0)+(B0-T0)),q=vc/vmax,dots=14;
  for(let j=0;j<dots;j++){let d=((j/dots+q*0.5)%1+1)%1*perim;let px,py;
   if(d<R0-L0){px=L0+d;py=T0;}else if((d-=R0-L0)<B0-T0){px=R0;py=T0+d;}else if((d-=B0-T0)<R0-L0){px=R0-d;py=B0;}else{d-=R0-L0;px=L0;py=B0-d;}
   ctx.fillStyle='#ec824f';ctx.beginPath();ctx.arc(px,py,3.5,0,Math.PI*2);ctx.fill();}
  const box=[320,20,380,270];frameBox(...box);
  polyline(c.rows.map(r=>[r[0],r[1]/vmax]),[0,c.duration],[-1.1,1.1],box,'#188b81',2,k+1);
  polyline(c.rows.map(r=>[r[0],r[2]/imax]),[0,c.duration],[-1.1,1.1],box,'#536be8',2,k+1);
  text('vC(t) / '+vmax.toPrecision(3)+' V',box[0]+6,box[1]+14,'#188b81');text('i(t) / '+(imax*1000).toPrecision(3)+' mA',box[0]+6,box[1]+30,'#536be8');
  text('t = '+(t*1000).toPrecision(4)+' ms, vC = '+vc.toPrecision(4)+' V, i = '+(i*1000).toPrecision(4)+' mA',20,300);
 }else if(c.id==='projectile'){
  const xr=Math.max(c.range,c.vacuumRange)*1.05,yr=Math.max(c.apexHeight,c.vacuumApex)*1.15,box=[40,30,650,250];
  const sc=Math.min(box[2]/xr,box[3]/yr),P=(x,y)=>[box[0]+x*sc,box[1]+box[3]-y*sc];
  ctx.strokeStyle='#597b82';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(box[0],box[1]+box[3]);ctx.lineTo(box[0]+box[2],box[1]+box[3]);ctx.stroke();
  const v0=Math.hypot(c.rows[0][3],c.rows[0][4]),th=Math.atan2(c.rows[0][4],c.rows[0][3]);
  ctx.strokeStyle='#c8d6dc';ctx.setLineDash([5,4]);ctx.beginPath();
  for(let j=0;j<=100;j++){const x=c.vacuumRange*j/100,y=x*Math.tan(th)-9.80665*x*x/(2*v0*v0*Math.cos(th)**2);const [px,py]=P(x,Math.max(0,y));if(j)ctx.lineTo(px,py);else ctx.moveTo(px,py);}ctx.stroke();ctx.setLineDash([]);
  const k=Math.min(c.rows.length-1,Math.round(p*(c.rows.length-1)));
  ctx.strokeStyle='#188b81';ctx.lineWidth=2;ctx.beginPath();for(let j=0;j<=k;j++){const [px,py]=P(c.rows[j][1],c.rows[j][2]);if(j)ctx.lineTo(px,py);else ctx.moveTo(px,py);}ctx.stroke();
  const [t,x,y,vx,vy]=c.rows[k],[px,py]=P(x,y);arrow(px,py,px+vx/v0*45,py-vy/v0*45,'#ec824f');
  ctx.fillStyle='#27444b';ctx.beginPath();ctx.arc(px,py,6,0,Math.PI*2);ctx.fill();
  text('t = '+t.toFixed(2)+' s, x = '+x.toFixed(1)+' m, y = '+y.toFixed(1)+' m, |v| = '+Math.hypot(vx,vy).toFixed(1)+' m/s',40,20);
  text('dashed: vacuum parabola (range '+c.vacuumRange.toFixed(1)+' m)',box[0]+6,box[1]+box[3]+20);
 }else if(c.id==='rod'){
  const k=Math.min(c.frames.length-1,Math.round(p*(c.frames.length-1))),fr=c.frames[k],n=fr.values.length;
  const lo=Math.min(c.T0,c.TL,c.TR),hi=Math.max(c.T0,c.TL,c.TR),span=Math.max(1e-9,hi-lo),x0=60,w=600;
  for(let j=0;j<n;j++){ctx.fillStyle=heat((fr.values[j]-lo)/span);ctx.fillRect(x0+w*j/n,40,w/n+1,40);}
  ctx.strokeStyle='#385d66';ctx.strokeRect(x0,40,w,40);
  text(c.TL+' °C',x0-50,65);text(c.TR+' °C',x0+w+6,65);
  const box=[x0,110,w,170];frameBox(...box);const xs=fr.values.map((_,j)=>j*c.L/(n-1));
  ctx.setLineDash([4,4]);polyline(xs.map((x,j)=>[x,c.TL+(c.TR-c.TL)*j/(n-1)]),[0,c.L],[lo-span*0.05,hi+span*0.05],box,'#c8d6dc',1);ctx.setLineDash([]);
  polyline(xs.map((x,j)=>[x,fr.values[j]]),[0,c.L],[lo-span*0.05,hi+span*0.05],box,'#e7543f',2);
  text('T(x) at t = '+fr.time.toFixed(1)+' s (dashed: steady linear profile)',box[0]+6,box[1]+14);
  text('centre '+fr.values[Math.floor(n/2)].toFixed(2)+' °C',x0,30);
 }else if(c.id==='spring'||c.id==='pendulum'){
  const k=Math.min(c.rows.length-1,Math.round(p*(c.rows.length-1))),row=c.rows[k],box=[300,20,400,270];
  frameBox(...box);
  const ys=c.rows.map(r=>r[1]),yr=range(c.id==='spring'?[...ys,0,1]:ys);
  polyline(c.rows.map(r=>[r[0],r[1]]),[0,c.duration],yr,box,'#188b81',2,k+1);
  text(c.id==='spring'?'x(t)':'θ(t) rad',box[0]+6,box[1]+16);text('t = '+row[0].toFixed(2)+' s',box[0]+box[2]-100,box[1]+box[3]+20);
  if(c.id==='spring'){
   const x=row[1],wallX=40,rest=150,scale=60,massX=wallX+rest+x*scale,cy=160;
   ctx.fillStyle='#597b82';ctx.fillRect(wallX-12,90,12,140);
   ctx.strokeStyle='#385d66';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(wallX,cy-15);
   for(let i=1;i<=12;i++)ctx.lineTo(wallX+(massX-wallX)*i/13,cy-15+(i%2?-10:10));ctx.lineTo(massX,cy-15);ctx.stroke();
   ctx.beginPath();ctx.moveTo(wallX,cy+20);ctx.lineTo(wallX+(massX-wallX)*0.6,cy+20);ctx.stroke();
   ctx.strokeRect(wallX+(massX-wallX)*0.6-2,cy+10,(massX-wallX)*0.4-6,20);
   ctx.fillStyle='#ec824f';ctx.fillRect(massX,cy-35,50,70);text('m',massX+20,cy+5,'#fff');
   ctx.setLineDash([4,4]);ctx.strokeStyle='#8ebfb8';ctx.beginPath();ctx.moveTo(wallX+rest+scale,80);ctx.lineTo(wallX+rest+scale,250);ctx.stroke();ctx.setLineDash([]);
   text('x = '+x.toFixed(3),40,270);text('target x = 1',wallX+rest+scale-30,74);
  }else{
   const th=row[1],px=150,py=40,len=200,bx=px+len*Math.sin(th),by=py+len*Math.cos(th);
   ctx.fillStyle='#597b82';ctx.fillRect(px-40,py-8,80,8);
   ctx.strokeStyle='#385d66';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(px,py);ctx.lineTo(bx,by);ctx.stroke();
   ctx.fillStyle='#ec824f';ctx.beginPath();ctx.arc(bx,by,14,0,Math.PI*2);ctx.fill();
   text('θ = '+(th*180/Math.PI).toFixed(1)+'°',40,290);
  }
 }else if(c.id==='spectrum'){
  const top=[30,20,660,120],bottom=[30,180,660,110];frameBox(...top);frameBox(...bottom);
  const pts=c.samples.map((y,i)=>[i/c.rate,y]),yr=range(c.samples);
  polyline(pts,[0,(c.n-1)/c.rate],yr,top,'#536be8',2);
  const cursor=top[0]+p*top[2];ctx.strokeStyle='#ec824f';ctx.beginPath();ctx.moveTo(cursor,top[1]);ctx.lineTo(cursor,top[1]+top[3]);ctx.stroke();
  const maxA=Math.max(1e-12,...c.bins.map(b=>b.amplitude)),bw=bottom[2]/c.bins.length;
  c.bins.forEach((b,i)=>{const hgt=b.amplitude/maxA*(bottom[3]-14)*Math.min(1,p*1.5);ctx.fillStyle='#188b81';ctx.fillRect(bottom[0]+i*bw+1,bottom[1]+bottom[3]-hgt,Math.max(1,bw-2),hgt);});
  text('signal (1 s)',top[0]+6,top[1]+14);text('one-sided amplitude spectrum, 0–32 Hz',bottom[0]+6,bottom[1]+14);
 }else if(c.id==='bisection'||c.id==='quadrature'){
  const box=[40,20,640,250],xs=c.curve.map(r=>r[0]),yr=range([...c.curve.map(r=>r[1]),0]),xr=[xs[0],xs.at(-1)];
  frameBox(...box);const zy=box[1]+box[3]-(0-yr[0])/(yr[1]-yr[0])*box[3];
  ctx.strokeStyle='#597b82';ctx.beginPath();ctx.moveTo(box[0],zy);ctx.lineTo(box[0]+box[2],zy);ctx.stroke();
  const X=x=>box[0]+(x-xr[0])/(xr[1]-xr[0])*box[2];
  if(c.id==='quadrature'){
   const k=Math.round(p*(c.curve.length-1));ctx.fillStyle='rgba(24,139,129,0.25)';ctx.beginPath();ctx.moveTo(X(c.curve[0][0]),zy);
   for(let i=0;i<=k;i++){const [x,y]=c.curve[i];if(Number.isFinite(y))ctx.lineTo(X(x),box[1]+box[3]-(Math.max(yr[0],Math.min(yr[1],y))-yr[0])/(yr[1]-yr[0])*box[3]);}
   ctx.lineTo(X(c.curve[k][0]),zy);ctx.closePath();ctx.fill();
   text('accumulated to x = '+c.curve[k][0].toPrecision(4)+'; total ≈ '+Number(c.value.toPrecision(8)),box[0]+6,box[1]+box[3]+20);
  }
  polyline(c.curve,xr,yr,box,'#536be8',2);
  if(c.id==='bisection'){
   const k=Math.min(c.brackets.length-1,Math.floor(p*c.brackets.length)),[a,b]=c.brackets[k];
   ctx.fillStyle='rgba(236,130,79,0.25)';ctx.fillRect(X(a),box[1],Math.max(2,X(b)-X(a)),box[3]);
   ctx.strokeStyle='#ec824f';ctx.lineWidth=2;for(const x of [a,b]){ctx.beginPath();ctx.moveTo(X(x),box[1]);ctx.lineTo(X(x),box[1]+box[3]);ctx.stroke();}
   text('iteration '+k+': ['+a.toPrecision(8)+', '+b.toPrecision(8)+']',box[0]+6,box[1]+box[3]+20);
  }
  text('f(x) = '+c.expression,box[0]+6,box[1]+14);
 }else if(c.id==='eigen'){
  const cx=360,cy=160,s=Math.min(110/Math.max(1e-9,...c.values.map(Math.abs)),60),t=Math.min(1,p*1.4);
  const T=[[1+(c.A[0][0]-1)*t,c.A[0][1]*t],[c.A[1][0]*t,1+(c.A[1][1]-1)*t]];
  ctx.strokeStyle='#e6eef0';for(let g=-4;g<=4;g++){ctx.beginPath();ctx.moveTo(cx+g*s,20);ctx.lineTo(cx+g*s,300);ctx.moveTo(60,cy-g*s);ctx.lineTo(660,cy-g*s);ctx.stroke();}
  ctx.strokeStyle='#8ebfb8';ctx.setLineDash([4,4]);ctx.beginPath();ctx.arc(cx,cy,s,0,Math.PI*2);ctx.stroke();ctx.setLineDash([]);
  ctx.strokeStyle='#188b81';ctx.lineWidth=2;ctx.beginPath();
  for(let i=0;i<=120;i++){const a=2*Math.PI*i/120,u=Math.cos(a),v=Math.sin(a),x=T[0][0]*u+T[0][1]*v,y=T[1][0]*u+T[1][1]*v;if(i)ctx.lineTo(cx+x*s,cy-y*s);else ctx.moveTo(cx+x*s,cy-y*s);}
  ctx.stroke();
  c.values.forEach((lam,j)=>{const vx=c.vectors[0][j],vy=c.vectors[1][j],sc=1+(lam-1)*t;ctx.strokeStyle=j?'#536be8':'#ec824f';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(cx,cy);ctx.lineTo(cx+vx*sc*s,cy-vy*sc*s);ctx.stroke();text('λ'+(j+1)+' = '+Number(lam.toPrecision(5)),cx+vx*sc*s+6,cy-vy*sc*s);});
  text('t = '+t.toFixed(2)+' (I → A)',70,300);
 }
 canvas.setAttribute('aria-label',visuals.find(v=>v.id===c.id).title+': '+c.summary);
}
function stop(){playing=false;cancelAnimationFrame(handle);toggle.textContent='Play';toggle.setAttribute('aria-pressed','true');}
function tick(){if(!playing)return;frame=Math.min(FRAMES,frame+1);draw();if(frame>=FRAMES){stop();return;}handle=requestAnimationFrame(tick);}
function play(){if(!current)return;if(frame>=FRAMES)frame=0;playing=true;toggle.textContent='Pause';toggle.setAttribute('aria-pressed','false');handle=requestAnimationFrame(tick);}
function run(){
 stop();
 try{
  const v=visuals.find(x=>x.id===picker.value);current=v.compute(params());status.classList.remove('error');
  status.textContent=current.summary;
  if(reduced()){frame=FRAMES;draw();}else{frame=0;draw();play();}
 }catch(error){current=null;frame=0;draw();status.classList.add('error');status.textContent='Cannot animate: '+error.message;}
 return current;
}
function select(id){if(!visuals.some(v=>v.id===id))throw Error('Unknown engineering visual: '+id);area.open=true;picker.value=id;buildFields();current=null;stop();draw();}
// Catalog "Open existing tool" entry point for simulation tools: select, run, focus first input.
function open(toolId){
 const v=visuals.find(x=>x.tool===toolId);if(!v)throw Error('No simulation for tool: '+toolId);
 select(v.id);run();area.scrollIntoView({block:'nearest'});fields.querySelector('input,select')?.focus({preventScroll:true});return v.id;
}
picker.addEventListener('change',()=>select(picker.value));
$('eng-visual-run').addEventListener('click',run);
toggle.addEventListener('click',()=>{if(playing)stop();else play();});
$('eng-visual-step').addEventListener('click',()=>{if(!current)return;stop();frame=Math.min(FRAMES,frame+Math.ceil(FRAMES/20));draw();});
// Cards keep their single canonical action button; a text note points to the animation panel.
function decorate(){
 for(const card of document.querySelectorAll('#eng-results .eng-card')){
  const v=visuals.find(x=>x.tool===card.dataset.toolId);if(!v||card.querySelector('[data-visual]'))continue;
  const note=document.createElement('p');note.dataset.visual=v.id;note.className='eng-visual-note';
  note.textContent='▶ Animation available: '+v.title+' (Engineering animations panel).';
  card.append(note);
 }
}
new MutationObserver(decorate).observe($('eng-results'),{childList:true});decorate();
buildFields();draw();stop();
M.engineeringVisuals=Object.freeze({visuals:visuals.map(v=>Object.freeze({id:v.id,tool:v.tool,title:v.title})),
 compute:Object.freeze({spring:springMassDamper,pendulum,spectrum,bisection,quadrature,eigen:eigenMorph,beam:S.beam,orbit:S.orbit,rlc:S.rlc,projectile:S.projectile,rod:S.rodHeat}),
 select,open,run,play,pause:stop,frame:()=>frame,frames:FRAMES,current:()=>current});
})();
