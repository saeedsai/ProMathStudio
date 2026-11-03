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
/* Ideal cold-air-standard Otto, Diesel and Brayton cycles: closed-system (Otto/Diesel) or
   steady-flow (Brayton) ideal gas with constant cp, cv = cp/γ and R = cp − cv; isentropic
   compression/expansion, heat addition at constant volume (Otto) or pressure (Diesel, Brayton).
   Net work is summed process by process and checked against q_in − q_out. */
function thermoCycle({cycle='otto',ratio=8,pressureRatio=10,spec='heat',heatIn=1000,Tmax=1800,cutoff=2,T1=300,P1=100,gamma=1.4,cp=1005}={}){
 cycle=choice(cycle,['otto','diesel','brayton'],'Cycle');spec=choice(spec,['heat','tmax','cutoff'],'Heat addition');
 const k=num(gamma,'Heat capacity ratio γ',1.01,1.8),Cp=num(cp,'cp (J/kg·K)',100,20000),Cv=Cp/k,R=Cp-Cv;
 const Ta=num(T1,'Inlet temperature T1 (K)',50,2000),Pa=num(P1,'Inlet pressure P1 (kPa)',1,20000)*1000;
 if(spec==='cutoff'&&cycle!=='diesel')throw Error('A cutoff ratio applies only to the Diesel cycle; choose heat input or maximum temperature.');
 const r=cycle==='brayton'?null:num(ratio,'Compression ratio r',1.01,40),rp=cycle==='brayton'?num(pressureRatio,'Pressure ratio rp',1.01,100):null;
 const v1=R*Ta/Pa;
 let T2,P2,v2;
 if(cycle==='brayton'){P2=Pa*rp;T2=Ta*rp**((k-1)/k);v2=R*T2/P2;}else{v2=v1/r;T2=Ta*r**(k-1);P2=Pa*r**k;}
 const cAdd=cycle==='otto'?Cv:Cp;
 let T3;
 if(spec==='heat')T3=T2+num(heatIn,'Heat input q_in (kJ/kg)',0.001,1e5)*1000/cAdd;
 else if(spec==='tmax'){T3=num(Tmax,'Maximum temperature T3 (K)',50,5000);if(!(T3>T2))throw Error('Maximum temperature T3 must exceed the compression end temperature T2 = '+T2.toPrecision(5)+' K.');}
 else T3=T2*num(cutoff,'Diesel cutoff ratio rc',1.0001,40);
 if(!(T3<=1e5))throw Error('Peak temperature '+T3.toPrecision(4)+' K is outside the model range (≤ 100000 K); reduce the heat input.');
 let P3,v3,T4,P4,v4;
 if(cycle==='otto'){v3=v2;P3=R*T3/v3;v4=v1;T4=T3*(v3/v4)**(k-1);P4=R*T4/v4;}
 else if(cycle==='diesel'){P3=P2;v3=R*T3/P3;if(!(v3<v1))throw Error('Cutoff ratio rc = '+(v3/v2).toPrecision(4)+' must be below the compression ratio r = '+r+'; reduce the heat input.');v4=v1;T4=T3*(v3/v4)**(k-1);P4=R*T4/v4;}
 else{P3=P2;v3=R*T3/P3;P4=Pa;T4=T3*(P4/P3)**((k-1)/k);v4=R*T4/P4;}
 const qIn=cAdd*(T3-T2),qOut=(cycle==='brayton'?Cp:Cv)*(T4-Ta);
 // Process works (by the gas, or shaft work for Brayton), summed independently of q_in − q_out.
 let wCompress,wExpand;
 if(cycle==='brayton'){wCompress=Cp*(T2-Ta);wExpand=Cp*(T3-T4);}
 else{wCompress=Cv*(T2-Ta);wExpand=Cv*(T3-T4)+(cycle==='diesel'?P2*(v3-v2):0);}
 const wNet=wExpand-wCompress,balance=Math.abs(wNet-(qIn-qOut))/Math.abs(qIn);
 const efficiency=wNet/qIn,rc=cycle==='diesel'?v3/v2:null;
 const formula=cycle==='otto'?1-r**(1-k):cycle==='diesel'?1-r**(1-k)*(rc**k-1)/(k*(rc-1)):1-rp**((1-k)/k);
 const entropy=(T,P)=>Cp*Math.log(T/Ta)-R*Math.log(P/Pa);
 const states=[[Ta,Pa,v1],[T2,P2,v2],[T3,P3,v3],[T4,P4,v4]].map(([T,P,v],i)=>Object.freeze({state:i+1,T,P,v,s:entropy(T,P)}));
 // Sampled process paths; every point satisfies P·v = R·T.
 const n=60,path=[];
 const isentropic=(a,b,proc)=>{for(let j=0;j<n;j++){const f=j/n;let T,P,v;
  if(cycle==='brayton'){P=a.P*(b.P/a.P)**f;T=a.T*(P/a.P)**((k-1)/k);v=R*T/P;}else{v=a.v+(b.v-a.v)*f;T=a.T*(a.v/v)**(k-1);P=R*T/v;}
  path.push([proc,v,P/1000,T,entropy(T,P)]);}};
 const heatLeg=(a,b,proc,constVolume)=>{for(let j=0;j<n;j++){const T=a.T+(b.T-a.T)*j/n;let P,v;if(constVolume){v=a.v;P=R*T/v;}else{P=a.P;v=R*T/P;}path.push([proc,v,P/1000,T,entropy(T,P)]);}};
 const [s1,s2,s3,s4]=states;
 isentropic(s1,s2,1);heatLeg(s2,s3,2,cycle==='otto');isentropic(s3,s4,3);heatLeg(s4,s1,4,cycle!=='brayton');
 path.push([4,s1.v,s1.P/1000,s1.T,0]);
 const swept=v1-v2,mep=cycle==='brayton'?null:wNet/swept,bwr=wCompress/wExpand;
 const names={otto:'Otto',diesel:'Diesel',brayton:'Brayton'};
 return {id:'cycle',cycle,gamma:k,cp:Cp,cv:Cv,R,r,rp,rc,states,path,qIn,qOut,wNet,wCompress,wExpand,efficiency,formulaEfficiency:formula,balance,mep,backWorkRatio:bwr,carnot:1-Ta/T3,
  assumptions:'Ideal cold-air-standard cycle: ideal gas with constant cp and cv, reversible isentropic compression and expansion, ideal heat addition/rejection; no friction, heat loss, combustion chemistry, dissociation or variable specific heats.',
  summary:'Ideal '+names[cycle]+' cycle ('+(cycle==='brayton'?'rp = '+rp:'r = '+r)+(rc?', rc = '+rc.toPrecision(4):'')+', γ = '+k+'): thermal efficiency '+(efficiency*100).toFixed(2)+'% (closed form '+(formula*100).toFixed(2)+'%), q_in '+(qIn/1000).toPrecision(5)+
   ' kJ/kg, q_out '+(qOut/1000).toPrecision(5)+' kJ/kg, w_net '+(wNet/1000).toPrecision(5)+' kJ/kg, '+(cycle==='brayton'?'back-work ratio '+bwr.toPrecision(4):'MEP '+(mep/1000).toPrecision(5)+' kPa')+', T_max '+T3.toPrecision(5)+' K; energy balance error '+balance.toExponential(1)+'.'};
}

/* DC modified nodal analysis of linear resistive networks with independent sources.
   Netlist lines "NAME n+ n− value": R (Ω), V (volts, n+ minus n−), I (amperes flowing from n+
   through the source to n−). Node 0 (or gnd) is ground. Dense Gaussian elimination with partial pivoting. */
function solveDense(A,b){
 // Scaled partial pivoting: rows are compared relative to their own largest original entry, so
 // conductances spanning many decades are not mistaken for singularity.
 const n=b.length,a=A.map((row,i)=>row.concat(b[i])),s=A.map(row=>Math.max(0,...row.map(Math.abs)));
 for(let c=0;c<n;c++){
  let p=-1,best=0;for(let r=c;r<n;r++){const q=s[r]?Math.abs(a[r][c])/s[r]:0;if(q>best){best=q;p=r;}}
  if(p<0||!(best>1e-13))return {singular:c};
  [a[c],a[p]]=[a[p],a[c]];[s[c],s[p]]=[s[p],s[c]];
  for(let r=c+1;r<n;r++){const f=a[r][c]/a[c][c];if(f)for(let j=c;j<=n;j++)a[r][j]-=f*a[c][j];}
 }
 const x=Array(n).fill(0);
 for(let i=n-1;i>=0;i--){let s=a[i][n];for(let j=i+1;j<n;j++)s-=a[i][j]*x[j];x[i]=s/a[i][i];}
 if(x.some(v=>!Number.isFinite(v)))throw Error('Circuit solution exceeded finite floating-point range.');
 return {x};
}
function parseNetlist(netlist){
 const text=String(netlist??'');if(text.length>4000)throw Error('Netlist is limited to 4000 characters.');
 const lines=text.split(/[\n;]/).map(s=>s.trim()).filter(s=>s&&!s.startsWith('*')&&!s.startsWith('#'));
 if(!lines.length)throw Error('Enter a netlist: one element per line, e.g. "R1 1 2 100".');
 if(lines.length>30)throw Error('Netlist is limited to 30 elements ('+lines.length+' given).');
 const names=new Set(),elements=[];
 lines.forEach((line,i)=>{
  const tok=line.split(/\s+/),where='Line '+(i+1)+' ("'+line.slice(0,40)+'")';
  if(tok.length!==4)throw Error(where+': expected NAME node+ node− value.');
  const [name,na,nb,raw]=tok,type=name[0].toUpperCase();
  if(!/^[RVI][A-Za-z0-9_]{0,15}$/i.test(name))throw Error(where+': element names start with R, V or I (letters, digits, _).');
  if(names.has(name.toUpperCase()))throw Error(where+': duplicate element name '+name+'.');
  names.add(name.toUpperCase());
  for(const node of [na,nb])if(!/^[A-Za-z0-9_]{1,16}$/.test(node))throw Error(where+': node names use letters, digits or _ (0 or gnd = ground).');
  if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/.test(raw))throw Error(where+': value must be a decimal or scientific number (e.g. 1e3).');
  const value=Number(raw),g=n=>/^(0|gnd)$/i.test(n)?'0':n,a=g(na),b=g(nb);
  if(type==='R'&&!(value>0&&value<=1e12))throw Error(where+': resistance must be greater than 0 and at most 1e12 Ω.');
  if(type!=='R'&&!(Math.abs(value)<=1e6))throw Error(where+': source value must have magnitude at most 1e6.');
  if(type==='V'&&a===b)throw Error(where+': a voltage source cannot connect a node to itself.');
  elements.push({name,type,a,b,value});
 });
 return elements;
}
function dcNetwork({netlist='V1 1 0 12\nR1 1 2 1000\nR2 2 0 2000'}={}){
 const elements=parseNetlist(netlist);
 const nodes=['0',...[...new Set(elements.flatMap(e=>[e.a,e.b]))].filter(n=>n!=='0')];
 if(!elements.some(e=>e.a==='0'||e.b==='0'))throw Error('No element connects to ground node 0 (or gnd).');
 // Connectivity to ground (union–find over all elements).
 const parent=new Map(nodes.map(n=>[n,n])),find=n=>{while(parent.get(n)!==n)n=parent.get(n);return n;};
 for(const e of elements)parent.set(find(e.a),find(e.b));
 const floating=nodes.filter(n=>find(n)!==find('0'));
 if(floating.length)throw Error('Floating node'+(floating.length>1?'s ':' ')+floating.join(', ')+': no path to ground node 0, so the voltages are undefined.');
 const index=new Map(nodes.slice(1).map((n,i)=>[n,i])),N=nodes.length-1,vs=elements.filter(e=>e.type==='V'),size=N+vs.length;
 const A=Array.from({length:size},()=>Array(size).fill(0)),rhs=Array(size).fill(0);
 const stamp=(r,c,v)=>{if(r!==undefined&&c!==undefined)A[r][c]+=v;};
 for(const e of elements){
  const i=index.get(e.a),j=index.get(e.b);
  if(e.type==='R'){const g=1/e.value;stamp(i,i,g);stamp(j,j,g);stamp(i,j,-g);stamp(j,i,-g);}
  else if(e.type==='I'){if(i!==undefined)rhs[i]-=e.value;if(j!==undefined)rhs[j]+=e.value;}
  else{const k=N+vs.indexOf(e);stamp(i,k,1);stamp(k,i,1);stamp(j,k,-1);stamp(k,j,-1);rhs[k]=e.value;}
 }
 const solved=solveDense(A,rhs);
 if(solved.singular!==undefined)throw Error('Singular network matrix: no unique DC solution. Check for a node fed only by current sources, current sources in series, or a loop of voltage sources.');
 const x=solved.x,volt=n=>n==='0'?0:x[index.get(n)];
 const out=elements.map(e=>{
  const v=volt(e.a)-volt(e.b);
  const current=e.type==='R'?v/e.value:e.type==='I'?e.value:x[N+vs.indexOf(e)];
  return Object.freeze({name:e.name,type:e.type,a:e.a,b:e.b,value:e.value,voltage:v,current,power:v*current});
 });
 // KCL: net current leaving every node (current flows from terminal a to terminal b through each element).
 const imax=Math.max(1e-300,...out.map(e=>Math.abs(e.current)));
 const kcl=nodes.map(n=>out.reduce((s,e)=>s+(e.a===n?e.current:0)-(e.b===n?e.current:0),0));
 const kclResidual=Math.max(...kcl.map(Math.abs))/imax;
 const pmax=Math.max(1e-300,...out.map(e=>Math.abs(e.power))),powerBalance=Math.abs(out.reduce((s,e)=>s+e.power,0))/pmax;
 const voltages=nodes.map(n=>Object.freeze({node:n,voltage:volt(n)}));
 const supplied=-out.filter(e=>e.type!=='R').reduce((s,e)=>s+e.power,0);
 return {id:'network',nodes:voltages,elements:out,unknowns:size,kclResidual,powerBalance,supplied,
  assumptions:'Linear DC resistive network: ideal resistors and independent ideal voltage/current sources, steady state; no capacitors, inductors, AC, dependent or nonlinear devices.',
  summary:'DC network: '+(nodes.length-1)+' node(s) + ground, '+out.length+' element(s), '+size+' MNA unknowns; '+voltages.slice(1,5).map(v=>'V('+v.node+') = '+Number(v.voltage.toPrecision(6))+' V').join(', ')+(voltages.length>5?', …':'')+
   '; sources supply '+Number(supplied.toPrecision(6))+' W; KCL residual '+kclResidual.toExponential(1)+', power balance '+powerBalance.toExponential(1)+'.'};
}
/* Steady incompressible looped pipe network: Darcy–Weisbach head loss, friction factor from the
   iterated Colebrook–White equation (or explicit Swamee–Jain), laminar f = 64/Re below Re 2000 and
   a linear blend to the turbulent value across 2000–4000 (flagged). Global Newton (gradient) method
   on pipe flows and unknown node heads; continuity rows are linear, energy rows use a central-
   difference head-loss derivative, with residual-halving line search. Netlist lines:
   "P1 A B length_m diameter_mm roughness_mm", "D node m³/s" (demand > 0, supply < 0), "H node head_m". */
const VALUE=/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$/,NAME=/^[A-Za-z0-9_]{1,16}$/;
function swameeJain(Re,rel){return 0.25/Math.log10(rel/3.7+5.74/Re**0.9)**2;}
function colebrook(Re,rel){
 // Fixed-point iteration on x = 1/√f started from Swamee–Jain; contraction is fast for Re ≥ 2000.
 let x=1/Math.sqrt(swameeJain(Re,rel));
 for(let k=0;k<100;k++){const next=-2*Math.log10(rel/3.7+2.51*x/Re);const done=Math.abs(next-x)<=1e-15*Math.abs(x);x=next;if(done)break;}
 return 1/(x*x);
}
function frictionFactor(Re,rel,law='colebrook'){
 if(!(Re>0))throw Error('Reynolds number must be positive.');
 const turbulent=r=>law==='swamee'?swameeJain(r,rel):colebrook(r,rel);
 if(Re<2000)return 64/Re;
 if(Re<4000){const w=(Re-2000)/2000;return (1-w)*0.032+w*turbulent(4000);}
 return turbulent(Re);
}
function parsePipeNetlist(netlist){
 const text=String(netlist??'');if(text.length>4000)throw Error('Pipe network description is limited to 4000 characters.');
 const lines=text.split(/[\n;]/).map(s=>s.trim()).filter(s=>s&&!s.startsWith('*')&&!s.startsWith('#'));
 if(!lines.length)throw Error('Enter a pipe network: e.g. "P1 A B 300 200 0.05", "D B 0.02", "H A 50".');
 if(lines.length>80)throw Error('Pipe network is limited to 80 lines ('+lines.length+' given).');
 const pipes=[],demand=new Map(),fixed=new Map(),names=new Set();
 lines.forEach((line,i)=>{
  const tok=line.split(/\s+/),where='Line '+(i+1)+' ("'+line.slice(0,40)+'")',key=tok[0].toUpperCase();
  const val=(raw,label)=>{if(!VALUE.test(raw||''))throw Error(where+': '+label+' must be a decimal or scientific number.');return Number(raw);};
  const node=n=>{if(!NAME.test(n||''))throw Error(where+': node names use 1–16 letters, digits or _.');return n;};
  if(key==='D'||key==='H'){
   if(tok.length!==3)throw Error(where+': expected "'+key+' node value".');
   const n=node(tok[1]),v=val(tok[2],key==='D'?'demand (m³/s)':'head (m)');
   if(key==='D'){if(!(Math.abs(v)<=100))throw Error(where+': demand magnitude must be at most 100 m³/s.');demand.set(n,(demand.get(n)||0)+v);}
   else{if(!(Math.abs(v)<=1e5))throw Error(where+': head must be within ±100000 m.');if(fixed.has(n))throw Error(where+': duplicate fixed head for node '+n+'.');fixed.set(n,v);}
   return;
  }
  if(!/^P[A-Za-z0-9_]{0,15}$/i.test(tok[0]))throw Error(where+': lines start with a pipe name P…, D (demand) or H (fixed head).');
  if(tok.length!==6)throw Error(where+': expected NAME from to length_m diameter_mm roughness_mm.');
  if(names.has(key))throw Error(where+': duplicate pipe name '+tok[0]+'.');
  names.add(key);
  const a=node(tok[1]),b=node(tok[2]);
  if(a===b)throw Error(where+': a pipe cannot connect a node to itself.');
  const L=val(tok[3],'length'),Dmm=val(tok[4],'diameter'),eps=val(tok[5],'roughness');
  if(!(L>0&&L<=1e5))throw Error(where+': length must be greater than 0 and at most 100000 m.');
  if(!(Dmm>=1&&Dmm<=5000))throw Error(where+': diameter must be from 1 to 5000 mm.');
  if(!(eps>=0&&eps<Dmm/10))throw Error(where+': roughness must be at least 0 and below a tenth of the diameter.');
  pipes.push({name:tok[0],a,b,L,D:Dmm/1000,eps:eps/1000});
 });
 if(!pipes.length)throw Error('Add at least one pipe line "P1 from to length_m diameter_mm roughness_mm".');
 if(pipes.length>40)throw Error('Pipe network is limited to 40 pipes ('+pipes.length+' given).');
 if(!fixed.size)throw Error('Add a fixed-head (reservoir) node, e.g. "H A 50": heads are otherwise undetermined.');
 for(const n of demand.keys())if(fixed.has(n))throw Error('Node '+n+' has a fixed head, so its inflow is a result; remove its D line.');
 return {pipes,demand,fixed};
}
function pipeNetwork({netlist='H A 50\nP1 A B 500 300 0.26\nP2 B C 400 250 0.26\nP3 A D 600 250 0.26\nP4 D C 400 200 0.26\nD B 0.04\nD C 0.05\nD D 0.03',density=998.2,viscosity=1.002e-3,friction='colebrook',maxIterations=200}={}){
 friction=choice(friction,['colebrook','swamee'],'Friction law');
 const rho=num(density,'Density ρ (kg/m³)',1,20000),mu=num(viscosity,'Dynamic viscosity μ (Pa·s)',1e-7,100),limit=Math.round(num(maxIterations,'Newton iteration limit',1,500));
 const {pipes,demand,fixed}=parsePipeNetlist(netlist);
 const nodes=[...new Set(pipes.flatMap(p=>[p.a,p.b]))];
 for(const n of [...demand.keys(),...fixed.keys()])if(!nodes.includes(n))throw Error('Node '+n+' has a demand or head but no connected pipe.');
 if(nodes.length>41)throw Error('Pipe network is limited to 41 nodes.');
 const parent=new Map(nodes.map(n=>[n,n])),find=n=>{while(parent.get(n)!==n)n=parent.get(n);return n;};
 for(const p of pipes)parent.set(find(p.a),find(p.b));
 const fedRoots=new Set([...fixed.keys()].map(find)),cut=nodes.filter(n=>!fedRoots.has(find(n)));
 if(cut.length)throw Error('Disconnected node'+(cut.length>1?'s ':' ')+cut.join(', ')+': no pipe path to a fixed-head node, so the heads are undefined.');
 const free=nodes.filter(n=>!fixed.has(n)),hIndex=new Map(free.map((n,i)=>[n,i])),np=pipes.length,size=np+free.length;
 const area=p=>Math.PI*p.D*p.D/4;
 // Head loss h(Q) = f·(L/D)·V|V|/(2g), sign follows Q (from → to).
 const loss=(p,Q)=>{const V=Q/area(p),Re=rho*Math.abs(V)*p.D/mu;
  if(Re<2000)return 32*mu*p.L*V/(rho*G0*p.D*p.D); // Hagen–Poiseuille: exact laminar loss, including Q = 0
  return frictionFactor(Re,p.eps/p.D,friction)*p.L/p.D*V*Math.abs(V)/(2*G0);};
 const Qs=Math.max(1e-6,...pipes.map(area)),Hfix=[...fixed.values()],Hs=Math.max(1,...Hfix.map(Math.abs));
 const Q=pipes.map(p=>area(p)*0.5),H=free.map(()=>Hfix.reduce((s,v)=>s+v,0)/Hfix.length);
 const head=(n,Hv)=>fixed.has(n)?fixed.get(n):Hv[hIndex.get(n)];
 const residual=(Qv,Hv)=>{
  const r=pipes.map((p,i)=>head(p.a,Hv)-head(p.b,Hv)-loss(p,Qv[i]));
  for(const n of free){let s=-(demand.get(n)||0);pipes.forEach((p,i)=>{if(p.b===n)s+=Qv[i];if(p.a===n)s-=Qv[i];});r.push(s);}
  return r;};
 const norm=r=>Math.max(0,...r.slice(0,np).map(v=>Math.abs(v)/Hs),...r.slice(np).map(v=>Math.abs(v)/Qs));
 let r=residual(Q,H),iterations=0,converged=false;
 for(;iterations<=limit;iterations++){
  if(norm(r)<1e-12){converged=true;break;}
  if(iterations===limit)break;
  const J=Array.from({length:size},()=>Array(size).fill(0));
  pipes.forEach((p,i)=>{const d=1e-7*Math.max(Math.abs(Q[i]),1e-4*area(p));J[i][i]=-(loss(p,Q[i]+d)-loss(p,Q[i]-d))/(2*d);
   if(hIndex.has(p.a)){J[i][np+hIndex.get(p.a)]+=1;J[np+hIndex.get(p.a)][i]-=1;}
   if(hIndex.has(p.b)){J[i][np+hIndex.get(p.b)]-=1;J[np+hIndex.get(p.b)][i]+=1;}});
  const solved=solveDense(J,r.map(v=>-v));
  if(solved.singular!==undefined)throw Error('Singular hydraulic Jacobian: the network has no unique steady solution.');
  let t=1,trialQ,trialH,trialR;
  for(let k=0;k<30;k++){trialQ=Q.map((q,i)=>q+t*solved.x[i]);trialH=H.map((h,i)=>h+t*solved.x[np+i]);trialR=residual(trialQ,trialH);if(norm(trialR)<norm(r)||k===29)break;t/=2;}
  Q.splice(0,np,...trialQ);H.splice(0,H.length,...trialH);r=trialR;
  if(!Q.every(Number.isFinite)||!H.every(Number.isFinite))break;
 }
 if(!converged)throw Error('Pipe network did not converge in '+limit+' Newton iteration(s) (scaled residual '+norm(r).toExponential(2)+'); check demands, sizes and fixed heads.');
 const warnings=[];
 const outPipes=pipes.map((p,i)=>{
  const V=Q[i]/area(p),Re=rho*Math.abs(V)*p.D/mu,hf=loss(p,Q[i]),rel=p.eps/p.D;
  const regime=Re<2000?'laminar':Re<4000?'transitional':'turbulent';
  if(regime==='transitional')warnings.push(p.name+' is transitional (Re = '+Re.toFixed(0)+'); friction factor blended and uncertain.');
  return Object.freeze({name:p.name,a:p.a,b:p.b,length:p.L,diameter:p.D,roughness:p.eps,flow:Q[i],velocity:V,reynolds:Re,friction:Re>0?frictionFactor(Re,rel,friction):null,headloss:hf,regime,
   direction:Q[i]>=0?p.a+'→'+p.b:p.b+'→'+p.a,swameeJain:Re>=4000?swameeJain(Re,rel):null,colebrook:Re>=4000?colebrook(Re,rel):null});
 });
 const inflow=n=>outPipes.reduce((s,p)=>s+(p.b===n?p.flow:0)-(p.a===n?p.flow:0),0);
 const nodeOut=nodes.map(n=>Object.freeze({node:n,head:head(n,H),fixed:fixed.has(n),demand:fixed.has(n)?inflow(n):(demand.get(n)||0)}));
 // Continuity residual at every free node (m³/s) and fundamental-loop head-loss sums (m).
 const continuity=Math.max(0,...free.map(n=>Math.abs(inflow(n)-(demand.get(n)||0))));
 const adj=new Map(nodes.map(n=>[n,[]]));pipes.forEach((p,i)=>{adj.get(p.a).push([p.b,i,1]);adj.get(p.b).push([p.a,i,-1]);});
 const up=new Map(),depth=new Map(),tree=new Set();
 for(const root of nodes){if(depth.has(root))continue;depth.set(root,0);const queue=[root];
  while(queue.length){const n=queue.shift();for(const [m,i,s] of adj.get(n))if(!depth.has(m)){depth.set(m,depth.get(n)+1);up.set(m,[n,i,s]);tree.add(i);queue.push(m);}}}
 const pathTo=n=>{const out=[n];while(up.has(out.at(-1)))out.push(up.get(out.at(-1))[0]);return out;};
 const loops=[];
 pipes.forEach((p,i)=>{if(tree.has(i))return;
  // Loop: pipe a→b, tree path b → common ancestor, then common → a. Signed sum of head losses.
  const pa=pathTo(p.a),pb=pathTo(p.b),common=pa.find(n=>pb.includes(n)),members=[[i,1]];
  const climb=(start,sign)=>{let n=start;while(n!==common){const [par,j,s]=up.get(n);members.push([j,-sign*s]);n=par;}};
  climb(p.b,1);climb(p.a,-1);
  loops.push(Object.freeze({pipes:members.map(([j,sg])=>(sg>0?'+':'−')+pipes[j].name),headSum:members.reduce((s,[j,sg])=>s+sg*outPipes[j].headloss,0)}));
 });
 const loopResidual=Math.max(0,...loops.map(l=>Math.abs(l.headSum)));
 const supply=-nodeOut.filter(n=>n.fixed).reduce((s,n)=>s+n.demand,0),total=[...demand.values()].reduce((s,v)=>s+v,0);
 const layers=nodes.map(n=>depth.get(n));
 return {id:'pipes',pipes:outPipes,nodes:nodeOut,layers,loops,iterations,continuityResidual:continuity,loopResidual,supply,totalDemand:total,rho,mu,friction,warnings,
  maxVelocity:Math.max(...outPipes.map(p=>Math.abs(p.velocity))),
  assumptions:'Steady incompressible single-phase flow in full circular pipes; Darcy–Weisbach friction with Colebrook–White (or Swamee–Jain) turbulent factor, laminar f = 64/Re below Re 2000 and a blended, uncertain transition up to Re 4000; heads are total heads; minor losses, elevations, pumps, valves and transients are not modelled.',
  summary:'Pipe network: '+pipes.length+' pipe(s), '+nodes.length+' node(s), '+loops.length+' loop(s); Newton converged in '+iterations+' iteration(s); reservoir supply '+Number((supply*1000).toPrecision(6))+' L/s; '+
   outPipes.slice(0,4).map(p=>p.name+' '+Number((Math.abs(p.flow)*1000).toPrecision(5))+' L/s '+p.direction).join(', ')+(outPipes.length>4?', …':'')+
   '; lowest head '+Number(Math.min(...nodeOut.map(n=>n.head)).toPrecision(6))+' m; continuity residual '+continuity.toExponential(1)+' m³/s, loop residual '+loopResidual.toExponential(1)+' m'+(warnings.length?'; '+warnings.length+' transitional pipe(s)':'')+'.'};
}

/* Gate-level digital logic: AND, OR, NOT, NAND, NOR, XOR (odd parity), XNOR, BUF and rising-edge
   D flip-flops on the implicit clock CLK (reset to 0). Netlist lines: "IN A [stimulus bits]",
   "OUT X Y", "CYCLES n", "net = GATE in1 in2 …", "Q = DFF D [CLK]"; literals 0/1 are constants.
   Combinational circuits give a full truth table (≤ 10 inputs); circuits with flip-flops give a
   clocked timing table (≤ 64 cycles). Zero delay evaluates in topological order; unit delay updates
   every gate simultaneously each step until stable and counts glitch transitions. */
const GATES=Object.freeze({AND:v=>v.every(Boolean),OR:v=>v.some(Boolean),NAND:v=>!v.every(Boolean),NOR:v=>!v.some(Boolean),
 XOR:v=>v.reduce((s,x)=>s^x,0)===1,XNOR:v=>v.reduce((s,x)=>s^x,0)===0,NOT:v=>!v[0],BUF:v=>Boolean(v[0])});
function parseLogicNetlist(netlist){
 const text=String(netlist??'');if(text.length>4000)throw Error('Logic netlist is limited to 4000 characters.');
 const lines=text.split(/[\n;]/).map(s=>s.trim()).filter(s=>s&&!s.startsWith('*')&&!s.startsWith('#'));
 if(!lines.length)throw Error('Enter a logic netlist: e.g. "IN A B", "S = XOR A B".');
 if(lines.length>80)throw Error('Logic netlist is limited to 80 lines ('+lines.length+' given).');
 const inputs=[],stimulus=new Map(),gates=[],outputs=[],driver=new Map();let cycles=null;
 const netName=(n,where)=>{
  if(!/^[A-Za-z_][A-Za-z0-9_]{0,15}$/.test(n||''))throw Error(where+': net names start with a letter or _ (letters, digits, _; at most 16).');
  if(/^CLK$/i.test(n))throw Error(where+': CLK is the reserved clock and cannot be driven or used as data.');
  if(n==='t_step')throw Error(where+': t_step is reserved for the table index.');
  return n;};
 const drive=(n,by,where)=>{if(driver.has(n))throw Error(where+': net '+n+' is driven twice ('+driver.get(n)+' and '+by+').');driver.set(n,by);};
 lines.forEach((line,i)=>{
  const where='Line '+(i+1)+' ("'+line.slice(0,40)+'")',tok=line.split(/\s+/),key=tok[0].toUpperCase();
  if(key==='IN'||key==='INPUT'){
   if(tok.length<2)throw Error(where+': expected "IN name [stimulus bits]".');
   const rest=tok.slice(1);
   if(rest.length===2&&/^[01]+$/.test(rest[1])){
    if(rest[1].length>64)throw Error(where+': stimulus is limited to 64 bits.');
    const n=netName(rest[0],where);drive(n,'input',where);inputs.push(n);stimulus.set(n,rest[1]);
   }else for(const r of rest){const n=netName(r,where);drive(n,'input',where);inputs.push(n);}
  }else if(key==='OUT'||key==='OUTPUT'){if(tok.length<2)throw Error(where+': expected "OUT net …".');for(const r of tok.slice(1))outputs.push(netName(r,where));}
  else if(key==='CYCLES'){if(tok.length!==2||!/^\d+$/.test(tok[1])||+tok[1]<1||+tok[1]>64)throw Error(where+': CYCLES must be an integer from 1 to 64.');cycles=+tok[1];}
  else{
   if(tok[1]!=='='||tok.length<4)throw Error(where+': expected "net = GATE input …" (or IN, OUT, CYCLES).');
   const out=netName(tok[0],where),type=tok[2].toUpperCase();let ins=tok.slice(3);
   if(type==='DFF'){if(ins.length===2&&/^CLK$/i.test(ins[1]))ins=[ins[0]];if(ins.length!==1)throw Error(where+': DFF takes one data input (optionally followed by CLK).');}
   else if(!GATES[type])throw Error(where+': unknown gate '+tok[2]+' (use AND, OR, NOT, NAND, NOR, XOR, XNOR, BUF or DFF).');
   else if((type==='NOT'||type==='BUF')&&ins.length!==1)throw Error(where+': '+type+' takes exactly one input.');
   else if(type!=='NOT'&&type!=='BUF'&&(ins.length<2||ins.length>8))throw Error(where+': '+type+' takes 2 to 8 inputs.');
   ins=ins.map(n=>/^[01]$/.test(n)?n:netName(n,where));
   drive(out,type,where);gates.push({out,type,ins});
  }
 });
 if(!gates.length)throw Error('Add at least one gate, e.g. "Y = AND A B".');
 if(gates.length>60)throw Error('Logic netlist is limited to 60 gates ('+gates.length+' given).');
 for(const g of gates)for(const n of g.ins)if(n!=='0'&&n!=='1'&&!driver.has(n))throw Error('Undriven net '+n+' (input of the '+g.type+' driving '+g.out+'): declare it with IN or drive it with a gate.');
 for(const n of outputs)if(!driver.has(n))throw Error('Undriven net '+n+' listed in OUT.');
 return {inputs,stimulus,gates,outputs,cycles};
}
function digitalLogic({netlist='IN A B Cin\nAX = XOR A B\nS = XOR AX Cin\nC1 = AND A B\nC2 = AND AX Cin\nCout = OR C1 C2\nOUT S Cout',delay='zero'}={}){
 delay=choice(delay,['zero','unit'],'Gate delay model');
 const {inputs,stimulus,gates,outputs,cycles}=parseLogicNetlist(netlist);
 const flops=gates.filter(g=>g.type==='DFF'),comb=gates.filter(g=>g.type!=='DFF'),sequential=flops.length>0;
 // Topological order of combinational gates (depth-first); inputs and flip-flop outputs are sources.
 const byOut=new Map(comb.map(g=>[g.out,g])),order=[],state=new Map();
 const visit=(g,stack)=>{
  if(state.get(g)===2)return;
  if(state.get(g)===1){const k=stack.indexOf(g);throw Error('Combinational loop through nets '+stack.slice(k).map(x=>x.out).join(' → ')+' → '+g.out+': feedback must pass through a DFF.');}
  state.set(g,1);stack.push(g);for(const n of g.ins){const d=byOut.get(n);if(d)visit(d,stack);}stack.pop();state.set(g,2);order.push(g);};
 for(const g of comb)visit(g,[]);
 const level=new Map();for(const g of order)level.set(g.out,1+Math.max(0,...g.ins.map(n=>level.get(n)||0)));
 const depth=Math.max(0,...level.values());
 if(!sequential&&!inputs.length)throw Error('Declare at least one input with IN for a combinational truth table.');
 if(!sequential&&inputs.length>10)throw Error('A truth table is limited to 10 inputs ('+inputs.length+' given).');
 if(sequential&&inputs.length>16)throw Error('A sequential simulation is limited to 16 inputs.');
 if(sequential)for(const n of inputs)if(!stimulus.has(n))throw Error('Sequential circuit: give input '+n+' a stimulus bit string, e.g. "IN '+n+' 0110".');
 const nets=[...inputs,...flops.map(f=>f.out),...order.map(g=>g.out)];
 const shown=outputs.length?[...new Set([...inputs,...outputs])]:nets;
 const bit=(vals,n)=>n==='1'?1:n==='0'?0:vals.get(n);
 let glitches=0,maxSettle=0;
 const settle=vals=>{
  if(delay==='zero'){for(const g of order)vals.set(g.out,GATES[g.type](g.ins.map(n=>bit(vals,n)))?1:0);return 0;}
  // Unit delay: every gate updates simultaneously from the previous step's values until stable.
  const changes=new Map();let steps=0;
  for(;steps<=comb.length+1;steps++){
   const moved=comb.map(g=>[g.out,GATES[g.type](g.ins.map(n=>bit(vals,n)))?1:0]).filter(([n,v])=>vals.get(n)!==v);
   if(!moved.length)break;
   for(const [n,v] of moved){vals.set(n,v);changes.set(n,(changes.get(n)||0)+1);}
  }
  for(const c of changes.values())if(c>1)glitches+=c-1;
  maxSettle=Math.max(maxSettle,steps);return steps;};
 const rows=[],settleSteps=[],vals=new Map(nets.map(n=>[n,0]));
 if(delay==='unit'){settle(vals);glitches=0;maxSettle=0;} // Power-on: settle the all-zero state first.
 if(!sequential){
  for(let k=0;k<2**inputs.length;k++){
   inputs.forEach((n,j)=>vals.set(n,(k>>(inputs.length-1-j))&1));
   settleSteps.push(settle(vals));rows.push([k,...shown.map(n=>vals.get(n))]);
  }
 }else{
  const N=cycles||Math.max(8,...[...stimulus.values()].map(s=>s.length));
  for(let k=0;k<N;k++){
   inputs.forEach(n=>{const s=stimulus.get(n);vals.set(n,+s[k%s.length]);});
   settleSteps.push(settle(vals));rows.push([k,...shown.map(n=>vals.get(n))]);
   // Rising CLK edge ending cycle k: every D flip-flop samples its input simultaneously.
   const sampled=flops.map(f=>[f.out,bit(vals,f.ins[0])]);for(const [n,v] of sampled)vals.set(n,v);
  }
 }
 const outsShown=outputs.length?outputs:shown.filter(n=>!inputs.includes(n));
 return {id:'logic',kind:sequential?'sequential':'combinational',delay,inputs,outputs:outsShown,signals:shown,rows,gates:gates.length,flipFlops:flops.length,depth,settleSteps,maxSettle,glitches,
  assumptions:'Ideal binary gate-level logic: zero-delay gates in topological order, or unit delay with synchronous gate updates; rising-edge D flip-flops on one ideal clock CLK, reset to 0; no setup/hold timing, metastability, tri-state, analogue levels or wire delays.',
  summary:(sequential?'Sequential circuit: '+rows.length+' clock cycle(s), '+flops.length+' D flip-flop(s)':'Combinational circuit: truth table of '+rows.length+' row(s) over '+inputs.length+' input(s)')+', '+gates.length+' gate(s), logic depth '+depth+
   (delay==='unit'?' (unit delay: settles within '+maxSettle+' step(s), '+glitches+' glitch transition(s))':' (zero delay)')+'; outputs '+outsShown.join(', ')+'.'};
}
M.engineeringSimulations=Object.freeze({beam,beamGeneral,vibration,orbit,rlc,projectile,rodHeat,thermoCycle,dcNetwork,parseNetlist,pipeNetwork,parsePipeNetlist,frictionFactor,colebrook,swameeJain,digitalLogic,parseLogicNetlist,rk4Vector,materials:MATERIALS,constants:Object.freeze({mu:MU,earthRadius:RE,g:G0})});
})();
