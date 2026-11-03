/* Engineering simulation kernels (pure, DOM-free, SI units). Each states its model
   assumptions; results are textbook-model estimates, not certified designs or code checks.
   SPDX-License-Identifier: MIT. */
(()=>{'use strict';
const M=window.MathStudio;
if(!M?.odeTools||!M?.numerical)return;
const num=(value,label,min,max)=>{
 const text=String(value??'').trim(),n=Number(text);
 if(!text||!Number.isFinite(n)||n<min||n>max)throw Error(label+' must be a number from '+min+' to '+max+'.');
 return n;
};
const choice=(value,allowed,label)=>{if(!allowed.includes(value))throw Error(label+' must be one of: '+allowed.join(', ')+'.');return value;};
const G0=9.80665;

/* Euler–Bernoulli prismatic beam: linear elastic, small deflection, no shear deformation.
   Deflection v is positive downward; loads act downward. Closed forms from standard tables. */
/* Statically determinate beam by superposition-free direct integration: reactions from statics,
   Macaulay bending moment, then EI·v'' = −M integrated twice (cumulative trapezoid, 2000 cells)
   with support conditions. Handles combined point loads + full-span UDL and an overhang. */
function beamGeneral({support='simply',length=4,supportB=null,loads=[],modulus=200,width=100,height=200}={}){
 support=choice(support,['simply','cantilever','overhang'],'Support');
 const L=num(length,'Span L (m)',0.1,200),E=num(modulus,'Elastic modulus E (GPa)',0.001,1500)*1e9;
 const b=num(width,'Section width b (mm)',1,5000)/1000,h=num(height,'Section depth h (mm)',1,5000)/1000;
 const xB=support==='overhang'?num(supportB,'Right support position (m)',0.05*L,0.95*L):L;
 if(!Array.isArray(loads)||!loads.length||loads.length>8)throw Error('Provide 1–8 loads.');
 const points=[],udl={w:0};
 for(const load of loads){
  if(load.type==='point')points.push({P:num(load.P,'Point load (kN)',-1e6,1e6)*1000,a:num(load.a,'Load position (m)',0,L)});
  else if(load.type==='udl')udl.w+=num(load.w,'Distributed load w (kN/m)',-1e6,1e6)*1000;
  else throw Error('Load type must be point or udl.');
 }
 const I=b*h**3/12,c=h/2,EI=E*I,n=2000,dx=L/n;
 const F=points.reduce((s,q)=>s+q.P,0)+udl.w*L,Mo=points.reduce((s,q)=>s+q.P*q.a,0)+udl.w*L*L/2;
 let reactions,M0=0;
 if(support==='cantilever'){reactions={left:F,right:0,moment:-Mo};M0=-Mo;}
 else{const RB=Mo/xB;reactions={left:F-RB,right:RB,rightAt:xB};}
 const mac=(x,a)=>x>a?x-a:0;
 const moment=x=>M0+reactions.left*x+(support==='cantilever'?0:reactions.right*mac(x,xB))-points.reduce((s,q)=>s+q.P*mac(x,q.a),0)-udl.w*x*x/2;
 const shear=x=>reactions.left+(support!=='cantilever'&&x>xB?reactions.right:0)-points.reduce((s,q)=>s+(x>q.a?q.P:0),0)-udl.w*x;
 const X=Array.from({length:n+1},(_,i)=>i*dx),Mx=X.map(moment);
 const theta=[0],v0=[0];
 for(let i=1;i<=n;i++){theta.push(theta[i-1]-dx*(Mx[i-1]+Mx[i])/(2*EI));v0.push(v0[i-1]+dx*(theta[i-1]+theta[i])/2);}
 let C1=0;
 if(support!=='cantilever'){const k=Math.min(n-1,Math.floor(xB/dx)),f=(xB-X[k])/dx,vB=v0[k]+f*(v0[k+1]-v0[k]);C1=-vB/xB;}
 const vFine=v0.map((v,i)=>v+C1*X[i]);
 const pick=arr=>arr.reduce((best,val,i)=>Math.abs(val)>Math.abs(best.value)?{value:val,index:i}:best,{value:0,index:0});
 const dmax=pick(vFine),mmax=pick(Mx),stress=Math.abs(mmax.value)*c/I,stride=10;
 const x=X.filter((_,i)=>i%stride===0);
 return {id:'beam',support,load:'combined',L,E,I,c,EI,supportB:xB,points,udl:udl.w,x,deflection:vFine.filter((_,i)=>i%stride===0),
  moment:Mx.filter((_,i)=>i%stride===0),shear:x.map(shear),reactions,
  maxDeflection:dmax.value,maxDeflectionAt:X[dmax.index],maxMoment:mmax.value,maxMomentAt:X[mmax.index],maxStress:stress,
  spanRatio:dmax.value===0?Infinity:L/Math.abs(dmax.value),method:'direct double integration (2000 cells)',
  assumptions:'Euler–Bernoulli prismatic rectangular beam, linear elastic, small deflection, statically determinate supports; no shear deformation, buckling or code checks.',
  summary:({simply:'Simply supported',cantilever:'Cantilever',overhang:'Overhanging'})[support]+' beam, '+points.length+' point load(s)'+(udl.w?' + UDL '+udl.w/1000+' kN/m':'')+
   ': max deflection '+(dmax.value*1000).toPrecision(4)+' mm at x = '+X[dmax.index].toPrecision(3)+' m, max moment '+(mmax.value/1000).toPrecision(4)+' kN·m, max bending stress '+(stress/1e6).toPrecision(4)+
   ' MPa; reactions '+(reactions.left/1000).toPrecision(4)+(support==='cantilever'?' kN, fixed-end moment '+(reactions.moment/1000).toPrecision(4)+' kN·m.':' / '+(reactions.right/1000).toPrecision(4)+' kN.')};
}
function beam({support='simply',load='point',length=4,position=2,force=10,modulus=200,width=100,height=200,supportB=3,force2=0,position2=1,udl=0}={}){
 if(load==='combined'||support==='overhang'){
  const loads=[];
  if(load==='udl')loads.push({type:'udl',w:force});
  else{loads.push({type:'point',P:force,a:position});if(load==='combined'){if(Number(force2))loads.push({type:'point',P:force2,a:position2});if(Number(udl))loads.push({type:'udl',w:udl});}}
  return beamGeneral({support,length,supportB,loads,modulus,width,height});
 }
 support=choice(support,['simply','cantilever'],'Support');load=choice(load,['point','udl'],'Load');
 const L=num(length,'Span L (m)',0.1,200);
 const E=num(modulus,'Elastic modulus E (GPa)',0.001,1500)*1e9;
 const b=num(width,'Section width b (mm)',1,5000)/1000,h=num(height,'Section depth h (mm)',1,5000)/1000;
 const q=num(force,load==='point'?'Point load P (kN)':'Distributed load w (kN/m)',-1e6,1e6)*1000;
 const a=load==='point'?num(position,'Load position a (m)',0,L):null;
 const I=b*h**3/12,c=h/2,EI=E*I,n=200;
 const x=Array.from({length:n+1},(_,i)=>L*i/n);
 let v,Mx,Vx,reactions;
 if(support==='simply'&&load==='point'){
  const bb=L-a;reactions={left:q*bb/L,right:q*a/L};
  v=x.map(s=>s<=a?q*bb*s*(L*L-bb*bb-s*s)/(6*L*EI):q*a*(L-s)*(L*L-a*a-(L-s)**2)/(6*L*EI));
  Mx=x.map(s=>s<=a?reactions.left*s:reactions.right*(L-s));
  Vx=x.map(s=>s<a?reactions.left:-reactions.right);
 }else if(support==='simply'){
  reactions={left:q*L/2,right:q*L/2};
  v=x.map(s=>q*s*(L**3-2*L*s*s+s**3)/(24*EI));
  Mx=x.map(s=>q*s*(L-s)/2);Vx=x.map(s=>q*(L/2-s));
 }else if(load==='point'){
  reactions={left:q,right:0,moment:-q*a};
  v=x.map(s=>s<=a?q*s*s*(3*a-s)/(6*EI):q*a*a*(3*s-a)/(6*EI));
  Mx=x.map(s=>s<a?-q*(a-s):0);Vx=x.map(s=>s<a?q:0);
 }else{
  reactions={left:q*L,right:0,moment:-q*L*L/2};
  v=x.map(s=>q*s*s*(6*L*L-4*L*s+s*s)/(24*EI));
  Mx=x.map(s=>-q*(L-s)**2/2);Vx=x.map(s=>q*(L-s));
 }
 const absMax=arr=>arr.reduce((best,val,i)=>Math.abs(val)>Math.abs(best.value)?{value:val,index:i}:best,{value:0,index:0});
 const dmax=absMax(v),mmax=absMax(Mx);
 const stress=Math.abs(mmax.value)*c/I;
 return {id:'beam',support,load,L,E,I,c,EI,force:q,position:a,x,deflection:v,moment:Mx,shear:Vx,reactions,
  maxDeflection:dmax.value,maxDeflectionAt:x[dmax.index],maxMoment:mmax.value,maxMomentAt:x[mmax.index],maxStress:stress,
  spanRatio:dmax.value===0?Infinity:L/Math.abs(dmax.value),
  assumptions:'Euler–Bernoulli prismatic rectangular beam, linear elastic, small deflection, no shear deformation, self-weight, buckling or code checks.',
  summary:(support==='simply'?'Simply supported':'Cantilever')+' beam, '+(load==='point'?'point load '+q/1000+' kN at '+a+' m':'UDL '+q/1000+' kN/m')+
   ': max deflection '+(dmax.value*1000).toPrecision(4)+' mm at x = '+x[dmax.index].toPrecision(3)+' m (L/'+Math.round(L/Math.max(Math.abs(dmax.value),1e-300))+'), max moment '+(mmax.value/1000).toPrecision(4)+
   ' kN·m, max bending stress '+(stress/1e6).toPrecision(4)+' MPa.'};
}

/* Two-body point-mass orbit around Earth, planar, propagated with symplectic velocity Verlet.
   No J2, drag, third bodies or relativity. */
const MU=398600.4418,RE=6378.137;
function orbit({altitude=500,eccentricity=0.1,orbits=1}={}){
 const hp=num(altitude,'Periapsis altitude (km)',100,100000),e=num(eccentricity,'Eccentricity e',0,0.95);
 const count=num(orbits,'Orbits',1,5);
 const rp=RE+hp,a=rp/(1-e),ra=a*(1+e),T=2*Math.PI*Math.sqrt(a**3/MU);
 const vp=Math.sqrt(MU*(1+e)/rp),steps=Math.round(4000*count),dt=count*T/steps;
 let x=rp,y=0,vx=0,vy=vp;
 const acc=(px,py)=>{const r3=Math.hypot(px,py)**3;return [-MU*px/r3,-MU*py/r3];};
 let [ax,ay]=acc(x,y);
 const energy=(px,py,qx,qy)=>0.5*(qx*qx+qy*qy)-MU/Math.hypot(px,py);
 const e0=energy(x,y,vx,vy),h0=x*vy-y*vx,stride=Math.max(1,Math.floor(steps/600)),path=[[0,x,y,vx,vy]];
 let maxEnergyDrift=0,maxMomentumDrift=0,minRadius=rp;
 for(let k=1;k<=steps;k++){
  vx+=0.5*dt*ax;vy+=0.5*dt*ay;x+=dt*vx;y+=dt*vy;[ax,ay]=acc(x,y);vx+=0.5*dt*ax;vy+=0.5*dt*ay;
  const r=Math.hypot(x,y);minRadius=Math.min(minRadius,r);
  if(r<RE)throw Error('Trajectory intersects Earth.');
  maxEnergyDrift=Math.max(maxEnergyDrift,Math.abs(energy(x,y,vx,vy)-e0)/Math.abs(e0));
  maxMomentumDrift=Math.max(maxMomentumDrift,Math.abs(x*vy-y*vx-h0)/Math.abs(h0));
  if(k%stride===0||k===steps)path.push([k*dt,x,y,vx,vy]);
 }
 const closure=Math.hypot(x-rp,y)/rp;
 return {id:'orbit',mu:MU,earthRadius:RE,rp,ra,a,e,period:T,orbits:count,path,vp,va:Math.sqrt(MU*(1-e)/ra),
  maxEnergyDrift,maxMomentumDrift,closure,apoapsisAltitude:ra-RE,
  assumptions:'Planar two-body point-mass Earth (μ = 398600.4418 km³/s²); no J2, drag, Moon/Sun or relativity.',
  summary:'Orbit e = '+e+', periapsis '+hp+' km, apoapsis '+(ra-RE).toFixed(1)+' km: period '+(T/60).toFixed(2)+' min (Kepler), speeds '+vp.toFixed(3)+' → '+Math.sqrt(MU*(1-e)/ra).toFixed(3)+
   ' km/s; Verlet energy drift '+maxEnergyDrift.toExponential(2)+', closure error '+closure.toExponential(2)+'.'};
}

/* Series RLC driven by a DC step at t = 0 from rest. Solved in dimensionless time τ = ω0·t
   with the existing two-state RK4 solver: v' = j, j' = 1 − v − 2ζ j, where v = vC/V and
   j = i/(V·√(C/L)). */
function rlc({resistance=4,inductance=10,capacitance=100,voltage=12}={}){
 const R=num(resistance,'Resistance R (Ω)',0,1e6),Lh=num(inductance,'Inductance L (mH)',1e-3,1e6)/1000;
 const C=num(capacitance,'Capacitance C (µF)',1e-3,1e7)/1e6,V=num(voltage,'Source voltage V (V)',-1e4,1e4);
 const w0=1/Math.sqrt(Lh*C),zeta=R/2*Math.sqrt(C/Lh);
 if(zeta>25)throw Error('Heavily overdamped (ζ = '+zeta.toFixed(1)+' > 25): too stiff for the fixed-step RK4 animation; reduce R or increase L.');
 const slow=zeta<1?zeta:zeta-Math.sqrt(zeta*zeta-1),tauEnd=Math.min(60,Math.max(4*Math.PI,7/Math.max(slow,1e-3)));
 const solved=M.odeTools.solveSystem({expression:'z',expressionZ:'1-y-'+(2*zeta).toFixed(15)+'*z',t0:0,t1:tauEnd,y0:0,z0:0,steps:1000});
 const iScale=V*Math.sqrt(C/Lh);
 const rows=solved.rows.map(([tau,vn,jn])=>[tau/w0,vn*V,jn*iScale]);
 const peak=rows.reduce((m,r)=>Math.abs(r[1])>Math.abs(m)?r[1]:m,0);
 const regime=zeta<1?'underdamped':zeta===1?'critically damped':'overdamped';
 return {id:'rlc',R,L:Lh,C,V,omega0:w0,zeta,regime,rows,duration:tauEnd/w0,overshoot:V===0?0:Math.max(0,peak/V-1),settled:Math.abs(rows.at(-1)[1]-V)<=0.02*Math.abs(V||1),
  assumptions:'Ideal lumped R, L, C and DC source switched on at t = 0 from rest; no parasitics or source resistance.',
  summary:'Series RLC step ('+regime+', ζ = '+zeta.toPrecision(3)+', f0 = '+(w0/2/Math.PI).toPrecision(4)+' Hz): capacitor overshoot '+(Math.max(0,peak/(V||1)-1)*100).toFixed(2)+'%, peak current '+
   (Math.max(...rows.map(r=>Math.abs(r[2])))*1000).toPrecision(4)+' mA.'};
}

/* Fixed-step classical RK4 for small native vector systems (used where the expression-based
   two-state solver cannot express four coupled states). */
function rk4Vector(f,y0,t0,t1,steps){
 const h=(t1-t0)/steps,rows=[[t0,...y0]];let y=y0.slice();
 for(let k=0;k<steps;k++){
  const t=t0+k*h,add=(u,s,d)=>u.map((ui,i)=>ui+s*d[i]);
  const k1=f(t,y),k2=f(t+h/2,add(y,h/2,k1)),k3=f(t+h/2,add(y,h/2,k2)),k4=f(t+h,add(y,h,k3));
  y=y.map((yi,i)=>yi+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6);
  if(y.some(v=>!Number.isFinite(v)))throw Error('Simulation exceeded finite range.');
  rows.push([t+h,...y]);
 }
 return rows;
}
/* Point-mass projectile over flat ground with quadratic drag F = ½ρCdA|v|v; no lift, wind or spin. */
function projectile({speed=50,angle=45,mass=0.145,diameter=74,drag=0.47,density=1.225}={}){
 const v0=num(speed,'Launch speed (m/s)',0.1,2000),th=num(angle,'Launch angle (°)',1,89)*Math.PI/180;
 const m=num(mass,'Mass (kg)',1e-4,1e5),d=num(diameter,'Diameter (mm)',0.1,5000)/1000,Cd=num(drag,'Drag coefficient Cd',0,3),rho=num(density,'Air density (kg/m³)',0,20);
 const A=Math.PI*d*d/4,k=0.5*rho*Cd*A/m;
 const vacuumTime=2*v0*Math.sin(th)/G0,duration=vacuumTime*1.05;
 const f=(t,[x,y,vx,vy])=>{const s=Math.hypot(vx,vy);return [vx,vy,-k*s*vx,-G0-k*s*vy];};
 const all=rk4Vector(f,[0,0,v0*Math.cos(th),v0*Math.sin(th)],0,duration,1200);
 let impact=all.findIndex((r,i)=>i>0&&r[2]<0);
 if(impact<0)throw Error('Projectile did not land within the simulated time.');
 const p=all[impact-1],q=all[impact],s=p[2]/(p[2]-q[2]);
 const land=p.map((v,i)=>v+s*(q[i]-v));
 const rows=all.slice(0,impact).concat([land]);
 const apex=rows.reduce((best,r)=>r[2]>best[2]?r:best,rows[0]);
 const vacuumRange=v0*v0*Math.sin(2*th)/G0;
 return {id:'projectile',rows,k,range:land[1],flightTime:land[0],apexHeight:apex[2],impactSpeed:Math.hypot(land[3],land[4]),vacuumRange,vacuumApex:(v0*Math.sin(th))**2/(2*G0),
  terminalVelocity:k>0?Math.sqrt(G0/k):Infinity,
  assumptions:'Point mass, flat ground, constant g and air density, quadratic drag only (no lift, spin, wind or Mach effects); RK4 with 1200 steps.',
  summary:'Projectile v0 = '+v0+' m/s at '+(th*180/Math.PI)+'°: range '+land[1].toFixed(2)+' m (vacuum '+vacuumRange.toFixed(2)+' m), apex '+apex[2].toFixed(2)+' m, flight '+land[0].toFixed(2)+' s, impact '+Math.hypot(land[3],land[4]).toFixed(2)+' m/s.'};
}

/* 1-D transient conduction in a rod with fixed end temperatures; reuses the existing
   explicit FTCS heat solver (CFL ≤ 0.5). */
const MATERIALS=Object.freeze({steel:11.7,aluminium:97,copper:111,glass:0.34,water:0.143});
function rodHeat({material='aluminium',length=0.5,initial=20,left=100,right=20,duration=600}={}){
 material=choice(material,Object.keys(MATERIALS),'Material');
 const L=num(length,'Rod length (m)',0.01,10),T0=num(initial,'Initial temperature (°C)',-273,3000);
 const TL=num(left,'Left end temperature (°C)',-273,3000),TR=num(right,'Right end temperature (°C)',-273,3000),t=num(duration,'Duration (s)',1,1e7);
 const alpha=MATERIALS[material]*1e-6,nx=40,dx=L/nx,nt=Math.ceil(alpha*t/(0.45*dx*dx));
 if(nt>1500)throw Error('Duration needs '+nt+' explicit steps (> 1500 for stability); shorten the duration or lengthen the rod.');
 const result=M.numerical.heat1D({a:0,b:L,nx,nt:Math.max(1,nt),alpha,endTime:t,initial:String(T0),left:TL,right:TR});
 const frames=[];
 for(const [x,time,u] of result.rows){let fr=frames.at(-1);if(!fr||fr.time!==time){fr={time,values:[]};frames.push(fr);}fr.values.push(u);}
 const fourier=t*alpha/(L*L);
 return {id:'rod',material,alpha,L,T0,TL,TR,duration:t,frames,dx,dt:result.dt,cfl:result.cfl,fourier,
  centre:frames.at(-1).values[nx/2],
  assumptions:'1-D conduction, constant diffusivity, perfectly insulated sides, fixed end temperatures; explicit FTCS (CFL ≤ 0.5).',
  summary:'Rod ('+material+', α = '+MATERIALS[material]+' mm²/s, L = '+L+' m) after '+t+' s: centre '+frames.at(-1).values[nx/2].toFixed(2)+' °C; Fourier number '+fourier.toPrecision(3)+(fourier<0.5?' (not yet near steady state)':' (approaching linear steady state)')+'; CFL '+result.cfl.toFixed(3)+'.'};
}
/* Harmonically forced, viscously damped SDOF oscillator m·x''+c·x'+k·x = F0·cos(ωt), from rest.
   Dimensionless time τ = ωn·t and x in units of the static deflection F0/k, solved with the existing
   RK4 solver: x'' + 2ζx' + x = cos(rτ). Steady amplitude and phase are least-squares fitted
   over the final forcing period and compared with the closed-form frequency response. */
function vibration({zeta=0.1,ratio=0.8,cycles=20}={}){
 const z=num(zeta,'Damping ratio ζ',0.01,2),r=num(ratio,'Frequency ratio r = ω/ωn',0.05,5),n=num(cycles,'Forcing cycles',2,60);
 const tauEnd=Math.min(n*2*Math.PI/r,300/Math.max(1,r));
 const solved=M.odeTools.solveSystem({expression:'z',expressionZ:'cos('+r.toFixed(15)+'*t)-y-'+(2*z).toFixed(15)+'*z',t0:0,t1:tauEnd,y0:0,z0:0,steps:1000});
 const rows=solved.rows,period=2*Math.PI/r,tail=rows.filter(([t])=>t>=tauEnd-period);
 // Fit x ≈ A cos(rτ) + B sin(rτ) over the final period (normal equations of a 2-term basis).
 let cc=0,ss=0,cs=0,xc=0,xs=0;
 for(const [t,x] of tail){const co=Math.cos(r*t),si=Math.sin(r*t);cc+=co*co;ss+=si*si;cs+=co*si;xc+=x*co;xs+=x*si;}
 const det=cc*ss-cs*cs,A=(xc*ss-xs*cs)/det,B=(xs*cc-xc*cs)/det;
 const measured=Math.hypot(A,B),phase=Math.atan2(B,A);
 const analytic=1/Math.sqrt((1-r*r)**2+(2*z*r)**2),analyticPhase=Math.atan2(2*z*r,1-r*r);
 const transientLeft=Math.exp(-z*tauEnd);
 const curve=Array.from({length:301},(_,i)=>{const q=i*3/300;return [q,1/Math.sqrt((1-q*q)**2+(2*z*q)**2)];});
 return {id:'vibration',zeta:z,ratio:r,rows,tauEnd,measuredAmplitude:measured,measuredPhase:phase,analyticAmplitude:analytic,analyticPhase,transientLeft,curve,
  assumptions:'Linear SDOF mass–spring–damper with viscous damping and harmonic force, starting from rest; dimensionless (x per static deflection F0/k, τ = ωn·t).',
  summary:'Forced vibration ζ = '+z+', r = '+r+': steady amplitude '+measured.toPrecision(5)+'×static (closed form '+analytic.toPrecision(5)+'), phase lag '+(phase*180/Math.PI).toFixed(2)+
   '° (closed form '+(analyticPhase*180/Math.PI).toFixed(2)+'°)'+(transientLeft>1e-3?'; transient not fully decayed (e^(−ζτ) = '+transientLeft.toExponential(1)+').':'.')};
}
M.engineeringSimulations=Object.freeze({beam,beamGeneral,vibration,orbit,rlc,projectile,rodHeat,rk4Vector,materials:MATERIALS,constants:Object.freeze({mu:MU,earthRadius:RE,g:G0})});
})();
