/* Offline single-epoch GNSS point positioning: weighted Gauss-Newton least squares, DOP and WGS-84 geodesy. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');if(!M||!panel)return;
const $=id=>document.getElementById(id);
const C=299792458,A=6378137,F=1/298.257223563,E2=F*(2-F),B=A*(1-F),LIMIT=1e9;
const WGS84=Object.freeze({a:A,f:F,b:B,e2:E2,c:C});
const SCOPE='Scope: single-epoch point positioning from given satellite ECEF positions. No ionosphere, troposphere, relativity or Earth-rotation (Sagnac) corrections and no ephemeris decoding.';
const deg=Math.PI/180;
function finite(value,name,limit=LIMIT){const n=Number(value);if(value===null||value===undefined||String(value).trim()===''||!Number.isFinite(n)||Math.abs(n)>limit)throw Error(name+' must be a finite number of magnitude at most '+limit.toExponential(0)+'.');return n;}
function geodeticToEcef(lat,lon,h=0){
 lat=finite(lat,'Latitude',90);lon=finite(lon,'Longitude',360);h=finite(h,'Height',1e8);
 const p=lat*deg,l=lon*deg,s=Math.sin(p),c=Math.cos(p),N=A/Math.sqrt(1-E2*s*s);
 return [(N+h)*c*Math.cos(l),(N+h)*c*Math.sin(l),(N*(1-E2)+h)*s];
}
function ecefToGeodetic(x,y,z){
 if(Array.isArray(x))[x,y,z]=x;
 x=finite(x,'x');y=finite(y,'y');z=finite(z,'z');
 const p=Math.hypot(x,y);if(Math.hypot(p,z)<1e5)throw Error('Point is within 100 km of the Earth centre; geodetic coordinates are not meaningful.');
 // Fixed-point iteration phi = atan2(z + e^2 N sin(phi), p); h from the pole-safe projection formula.
 let phi=Math.atan2(z,p*(1-E2)),k=0;
 for(;k<50;k++){const s=Math.sin(phi),N=A/Math.sqrt(1-E2*s*s),next=Math.atan2(z+E2*N*s,p);if(Math.abs(next-phi)<1e-15){phi=next;break;}phi=next;}
 if(k>=50)throw Error('Geodetic latitude iteration did not converge.');
 const s=Math.sin(phi),c=Math.cos(phi),h=p*c+z*s-A*Math.sqrt(1-E2*s*s);
 return {latitude:phi/deg,longitude:p===0?0:Math.atan2(y,x)/deg,height:h};
}
function enuRotation(lat,lon){
 const p=lat*deg,l=lon*deg,sp=Math.sin(p),cp=Math.cos(p),sl=Math.sin(l),cl=Math.cos(l);
 return [[-sl,cl,0],[-sp*cl,-sp*sl,cp],[cp*cl,cp*sl,sp]];
}
const mul=(R,v)=>R.map(r=>r[0]*v[0]+r[1]*v[1]+r[2]*v[2]);
function azEl(receiver,satellite){
 const g=ecefToGeodetic(receiver),d=[0,1,2].map(i=>satellite[i]-receiver[i]),r=Math.hypot(...d);
 if(!(r>0))throw Error('Satellite coincides with the receiver.');
 const [e,n,u]=mul(enuRotation(g.latitude,g.longitude),d);
 return {azimuth:(Math.atan2(e,n)/deg+360)%360,elevation:Math.asin(Math.max(-1,Math.min(1,u/r)))/deg,range:r};
}
// Symmetric Jacobi eigenvalues (n<=4) used only as a geometry/conditioning test.
function eigenvalues(S){
 const n=S.length,a=S.map(r=>r.slice());
 for(let sweep=0;sweep<60;sweep++){
  let off=0;for(let i=0;i<n;i++)for(let j=i+1;j<n;j++)off+=a[i][j]*a[i][j];
  if(off<1e-30*Math.max(1e-300,a.reduce((s,r,i)=>s+r[i]*r[i],0)))break;
  for(let p=0;p<n;p++)for(let q=p+1;q<n;q++){
   if(a[p][q]===0)continue;
   const th=(a[q][q]-a[p][p])/(2*a[p][q]),t=Math.sign(th||1)/(Math.abs(th)+Math.sqrt(th*th+1)),c=1/Math.sqrt(t*t+1),s=t*c;
   for(let k=0;k<n;k++){const akp=a[k][p],akq=a[k][q];a[k][p]=c*akp-s*akq;a[k][q]=s*akp+c*akq;}
   for(let k=0;k<n;k++){const apk=a[p][k],aqk=a[q][k];a[p][k]=c*apk-s*aqk;a[q][k]=s*apk+c*aqk;}
  }
 }
 return a.map((r,i)=>r[i]);
}
function inverse(S,what){
 const ev=eigenvalues(S),max=Math.max(...ev.map(Math.abs)),min=Math.min(...ev);
 if(!(max>0)||!(min>1e-12*max))throw Error('Singular satellite geometry ('+what+'): the line-of-sight design matrix is rank deficient or near-singular (relative eigenvalue '+(max>0?(min/max).toExponential(2):'0')+'). Coplanar or collinear line-of-sight directions, or satellites on one elevation cone, cannot separate position and clock.');
 const n=S.length,a=S.map((r,i)=>[...r,...Array.from({length:n},(_,j)=>i===j?1:0)]);
 for(let c=0;c<n;c++){
  let p=c;for(let r=c+1;r<n;r++)if(Math.abs(a[r][c])>Math.abs(a[p][c]))p=r;[a[c],a[p]]=[a[p],a[c]];
  const d=a[c][c];for(let k=0;k<2*n;k++)a[c][k]/=d;
  for(let r=0;r<n;r++)if(r!==c){const f=a[r][c];if(f)for(let k=0;k<2*n;k++)a[r][k]-=f*a[c][k];}
 }
 return a.map(r=>r.slice(n));
}
function normal(H,w){const N=[0,1,2,3].map(()=>[0,0,0,0]);for(let i=0;i<H.length;i++)for(let r=0;r<4;r++)for(let c=0;c<4;c++)N[r][c]+=w[i]*H[i][r]*H[i][c];return N;}
function parseObservations(text){
 const lines=String(text??'').split(/\r?\n/);if(lines.length>200)throw Error('Enter at most 200 lines.');
 const out=[];
 lines.forEach((line,i)=>{
  const t=line.trim();if(!t||t.startsWith('#'))return;
  const parts=t.split(/[\s,;]+/).filter(Boolean);
  if(parts.length<4||parts.length>5)throw Error('Line '+(i+1)+': expected "x y z pseudorange [sigma]" in metres.');
  const [x,y,z,rho]=parts.slice(0,4).map((v,k)=>finite(v,'Line '+(i+1)+' '+['x','y','z','pseudorange'][k]));
  const o={x,y,z,rho};if(parts.length===5)o.sigma=finite(parts[4],'Line '+(i+1)+' sigma',1e6);out.push(o);
 });
 return out;
}
function solve({observations,text,initial=null,maxIterations=20,tolerance=1e-6}={}){
 const obs=observations??parseObservations(text);
 if(!Array.isArray(obs))throw Error('Observations must be a list.');
 if(obs.length<4)throw Error('At least 4 satellites are required to solve for position and clock bias; got '+obs.length+'.');
 if(obs.length>16)throw Error('At most 16 satellites are supported; got '+obs.length+'.');
 const sats=obs.map((o,i)=>[finite(o.x,'Satellite '+(i+1)+' x'),finite(o.y,'Satellite '+(i+1)+' y'),finite(o.z,'Satellite '+(i+1)+' z')]);
 const rho=obs.map((o,i)=>finite(o.rho,'Satellite '+(i+1)+' pseudorange'));
 const hasSigma=obs.map(o=>o.sigma!==undefined&&o.sigma!==null&&o.sigma!=='');
 if(hasSigma.some(Boolean)&&!hasSigma.every(Boolean))throw Error('Give sigma for every satellite or for none.');
 const sigma=obs.map((o,i)=>{if(!hasSigma[i])return 1;const s=finite(o.sigma,'Satellite '+(i+1)+' sigma',1e6);if(!(s>0))throw Error('Satellite '+(i+1)+' sigma must be positive.');return s;});
 const w=sigma.map(s=>1/(s*s));
 maxIterations=finite(maxIterations,'Maximum iterations',1000);if(!Number.isInteger(maxIterations)||maxIterations<1||maxIterations>100)throw Error('Maximum iterations must be an integer from 1 to 100.');
 tolerance=finite(tolerance,'Tolerance',1);if(!(tolerance>=1e-9))throw Error('Tolerance must be between 1e-9 and 1 m.');
 let x=[0,0,0,0];
 if(initial!==null&&initial!==undefined&&!(typeof initial==='string'&&!initial.trim())){
  const g=typeof initial==='string'?initial.trim().split(/[\s,;]+/):Array.from(initial);
  if(g.length<3||g.length>4)throw Error('Initial guess must be "x y z" or "x y z clock-bias" in metres.');
  x=[...g.map((v,k)=>finite(v,'Initial guess '+['x','y','z','clock bias'][k])),0].slice(0,4);
 }
 const model=()=>{
  const H=[],v=[];
  for(let i=0;i<sats.length;i++){
   const d=[0,1,2].map(k=>x[k]-sats[i][k]),r=Math.hypot(...d);
   if(!(r>0))throw Error('Receiver estimate coincides with satellite '+(i+1)+'.');
   H.push([d[0]/r,d[1]/r,d[2]/r,1]);v.push(rho[i]-(r+x[3]));
  }
  return {H,v};
 };
 let iterations=0,converged=false,step=Infinity,last;
 for(;iterations<maxIterations;){
  last=model();
  const Q=inverse(normal(last.H,w),'iteration '+(iterations+1));
  const g=[0,1,2,3].map(r=>last.H.reduce((s,h,i)=>s+w[i]*h[r]*last.v[i],0));
  const dx=Q.map(row=>row.reduce((s,q,k)=>s+q*g[k],0));
  x=x.map((xi,k)=>xi+dx[k]);iterations++;step=Math.hypot(...dx);
  if(!x.every(Number.isFinite)||Math.hypot(x[0],x[1],x[2])>LIMIT)throw Error('Gauss-Newton iteration diverged after '+iterations+' steps; check the pseudoranges or give an initial guess.');
  if(step<tolerance){converged=true;break;}
 }
 if(!converged)throw Error('Did not converge in '+maxIterations+' iterations (last step '+step.toExponential(3)+' m); check the data or raise the iteration limit.');
 last=model();
 const Q=inverse(normal(last.H,w),'solution'),n=sats.length,redundancy=n-4;
 const vtpv=last.v.reduce((s,v,i)=>s+w[i]*v*v,0),sigma0=redundancy>0?Math.sqrt(vtpv/redundancy):null;
 const covariance=Q.map(r=>r.map(q=>(sigma0===null?1:sigma0*sigma0)*q));
 const D=inverse(normal(last.H,last.H.map(()=>1)),'DOP');
 const geodetic=ecefToGeodetic(x.slice(0,3)),R=enuRotation(geodetic.latitude,geodetic.longitude);
 const Qp=[0,1,2].map(i=>[0,1,2].map(j=>D[i][j]));
 const enu=R.map(ri=>R.map(rj=>[0,1,2].reduce((s,a)=>s+ri[a]*[0,1,2].reduce((t,b)=>t+Qp[a][b]*rj[b],0),0)));
 const dop={gdop:Math.sqrt(D[0][0]+D[1][1]+D[2][2]+D[3][3]),pdop:Math.sqrt(D[0][0]+D[1][1]+D[2][2]),
  hdop:Math.sqrt(enu[0][0]+enu[1][1]),vdop:Math.sqrt(enu[2][2]),tdop:Math.sqrt(D[3][3])};
 const sky=sats.map(s=>azEl(x.slice(0,3),s));
 const rms=Math.sqrt(last.v.reduce((s,v)=>s+v*v,0)/n);
 return {type:'gnss-position',method:'Weighted Gauss-Newton least squares (pseudorange)',position:x.slice(0,3),clockBiasMeters:x[3],clockBiasSeconds:x[3]/C,
  iterations,converged,lastStep:step,residuals:last.v,residualRms:rms,sigma0,redundancy,weighted:hasSigma[0],sigma,
  covariance,covarianceKind:sigma0===null?'a priori (unit-weight variance 1; no redundancy)':'a posteriori (scaled by sigma0^2)',
  dop,geodetic,satellites:sky,belowHorizon:sky.filter(s=>s.elevation<0).length,observations:sats.map((s,i)=>({x:s[0],y:s[1],z:s[2],rho:rho[i]})),note:SCOPE};
}
function synthesize({latitude=59.33,longitude=18.06,height=30,clockBiasSeconds=1e-4,geometry=[[0,60],[90,35],[180,45],[270,30],[45,15],[225,75],[315,20]],radius=26560e3,noise=null}={}){
 const r=geodeticToEcef(latitude,longitude,height),Rt=enuRotation(latitude,longitude);
 return geometry.map(([az,el],i)=>{
  const a=az*deg,e=el*deg,enu=[Math.cos(e)*Math.sin(a),Math.cos(e)*Math.cos(a),Math.sin(e)];
  const u=[0,1,2].map(k=>Rt[0][k]*enu[0]+Rt[1][k]*enu[1]+Rt[2][k]*enu[2]);
  const ru=r[0]*u[0]+r[1]*u[1]+r[2]*u[2],rr=r[0]*r[0]+r[1]*r[1]+r[2]*r[2],t=-ru+Math.sqrt(ru*ru-rr+radius*radius);
  const s=[0,1,2].map(k=>r[k]+t*u[k]);
  return {x:s[0],y:s[1],z:s[2],rho:t+C*clockBiasSeconds+(noise?noise[i]||0:0)};
 });
}
M.gnss=Object.freeze({solve,parseObservations,geodeticToEcef,ecefToGeodetic,enuRotation,azEl,synthesize,WGS84,scope:SCOPE});
if(!M.advanced||!M.dataTables)return;
const style=document.createElement('style');
style.textContent='#gnss-details textarea{width:100%;min-height:150px;box-sizing:border-box;font:12px/1.45 ui-monospace,monospace;padding:9px;border:1px solid #cdd8ec;border-radius:9px;resize:vertical}'+
 '#gnss-details .data-toolbar{display:flex;flex-wrap:wrap;gap:8px}#gnss-details button{min-height:40px;min-width:40px}'+
 '#gnss-details label{display:flex;flex-direction:column;gap:5px;min-width:0}#gnss-details textarea:focus-visible,#gnss-details input:focus-visible,#gnss-details button:focus-visible{outline:3px solid #3c50ae;outline-offset:2px}'+
 '#gnss-output{white-space:pre-wrap;overflow-wrap:anywhere;max-width:100%}#gnss-output.error{color:#b43543}'+
 '#gnss-sky{display:block;width:100%;max-width:300px;height:auto;aspect-ratio:1;margin:10px 0}';
document.head.append(style);
const area=document.createElement('details');area.id='gnss-details';
area.innerHTML='<summary>GNSS point positioning · least squares</summary><p>Solve receiver ECEF position and clock bias from 4–16 satellite positions and pseudoranges. '+SCOPE+'</p>'+
 '<label>Observations: one satellite per line, <code>x y z pseudorange [sigma]</code> in metres (ECEF)<textarea id="gnss-input" spellcheck="false" aria-describedby="gnss-help"></textarea></label>'+
 '<p id="gnss-help">Lines starting with # are ignored. Sigma (optional, all or none) weights each observation by 1/sigma².</p>'+
 '<div class="num-fields"><label>Initial guess x y z [m] (optional)<input id="gnss-guess" autocomplete="off" placeholder="0 0 0"></label>'+
 '<label>Maximum iterations<input id="gnss-iterations" type="number" step="1" value="20"></label></div>'+
 '<div class="data-toolbar"><button id="gnss-example" class="secondary" type="button">Load example</button>'+
 '<button id="gnss-run" class="primary" type="button">Solve position</button>'+
 '<button id="gnss-to-table" class="secondary" type="button" disabled>Residuals to Data Tables</button></div>'+
 '<canvas id="gnss-sky" width="300" height="300" role="img" aria-label="Sky plot: solve a position to show satellite azimuth and elevation."></canvas>'+
 '<pre id="gnss-output" role="status" aria-live="polite">Load the example or paste observations, then solve.</pre>';
panel.append(area);let last=null;
const out=$('gnss-output'),sky=$('gnss-sky');
function drawSky(result){
 const ctx=sky.getContext('2d');if(!ctx)return;const W=sky.width,c=W/2,R=W/2-22;ctx.clearRect(0,0,W,W);
 ctx.fillStyle='#ffffff';ctx.fillRect(0,0,W,W);ctx.strokeStyle='#c2cfdb';ctx.lineWidth=1;
 for(const el of [0,30,60]){ctx.beginPath();ctx.arc(c,c,R*(90-el)/90,0,2*Math.PI);ctx.stroke();}
 ctx.beginPath();ctx.moveTo(c-R,c);ctx.lineTo(c+R,c);ctx.moveTo(c,c-R);ctx.lineTo(c,c+R);ctx.stroke();
 ctx.fillStyle='#283752';ctx.font='12px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.fillText('N',c,10);ctx.fillText('S',c,W-10);ctx.fillText('E',W-10,c);ctx.fillText('W',10,c);
 if(!result){sky.setAttribute('aria-label','Sky plot: solve a position to show satellite azimuth and elevation.');return;}
 result.satellites.forEach((s,i)=>{
  const r=R*(90-Math.max(-10,s.elevation))/90,a=s.azimuth*deg,px=c+r*Math.sin(a),py=c-r*Math.cos(a);
  ctx.fillStyle=s.elevation<0?'#b43543':'#29817b';ctx.beginPath();ctx.arc(px,py,8,0,2*Math.PI);ctx.fill();
  ctx.fillStyle='#ffffff';ctx.font='bold 10px system-ui,sans-serif';ctx.fillText(String(i+1),px,py);
 });
 sky.setAttribute('aria-label','Sky plot of '+result.satellites.length+' satellites: '+result.satellites.map((s,i)=>'satellite '+(i+1)+' azimuth '+s.azimuth.toFixed(1)+'°, elevation '+s.elevation.toFixed(1)+'°').join('; ')+'.');
}
drawSky(null);
const invalidate=()=>{last=null;$('gnss-to-table').disabled=true;out.classList.remove('error');};
for(const input of area.querySelectorAll('input,textarea')){input.addEventListener('input',invalidate);input.addEventListener('change',invalidate);}
$('gnss-example').addEventListener('click',()=>{
 const rows=synthesize({noise:[0.8,-1.1,0.4,1.5,-0.6,0.2,-0.9]});
 $('gnss-input').value='# Synthetic: receiver near 59.33°N 18.06°E, 30 m; clock bias 1e-4 s; metre-level noise\n'+rows.map(o=>[o.x,o.y,o.z,o.rho].map(v=>v.toFixed(3)).join(' ')+' 1.0').join('\n');
 $('gnss-guess').value='';invalidate();out.textContent='Example loaded (7 satellites). Choose Solve position.';$('gnss-input').focus();
});
const f=(v,d=3)=>Number(v).toFixed(d);
$('gnss-run').addEventListener('click',()=>{
 try{
  last=solve({text:$('gnss-input').value,initial:$('gnss-guess').value,maxIterations:$('gnss-iterations').value});
  const g=last.geodetic,d=last.dop,p=last.position,cv=last.covariance;
  out.classList.remove('error');
  out.textContent=last.method+' · converged in '+last.iterations+' iterations (last step '+last.lastStep.toExponential(2)+' m)\n'+
   'ECEF x, y, z = '+p.map(v=>f(v)).join(', ')+' m\n'+
   'Latitude '+g.latitude.toFixed(9)+'°, longitude '+g.longitude.toFixed(9)+'°, height '+f(g.height)+' m (WGS-84)\n'+
   'Clock bias = '+f(last.clockBiasMeters)+' m = '+last.clockBiasSeconds.toExponential(6)+' s\n'+
   'Residual RMS = '+last.residualRms.toExponential(3)+' m; redundancy '+last.redundancy+'; sigma0 = '+(last.sigma0===null?'n/a (4 satellites)':last.sigma0.toExponential(3))+'\n'+
   'GDOP '+f(d.gdop,2)+' · PDOP '+f(d.pdop,2)+' · HDOP '+f(d.hdop,2)+' · VDOP '+f(d.vdop,2)+' · TDOP '+f(d.tdop,2)+'\n'+
   'Std dev x, y, z, clock = '+[0,1,2,3].map(i=>Math.sqrt(cv[i][i]).toExponential(2)).join(', ')+' m ('+last.covarianceKind+')\n'+
   (last.belowHorizon?last.belowHorizon+' satellite(s) below the horizon at the solution.\n':'')+last.note;
  drawSky(last);$('gnss-to-table').disabled=false;
 }catch(err){invalidate();drawSky(null);out.classList.add('error');out.textContent=err.message+' Correct the observations and solve again.';}
});
$('gnss-to-table').addEventListener('click',()=>{try{if(!last)throw Error('Solve a position first.');
 M.dataTables.importData({headers:['satellite','x_m','y_m','z_m','pseudorange_m','sigma_m','residual_m','azimuth_deg','elevation_deg'],
  rows:last.observations.map((o,i)=>[i+1,o.x,o.y,o.z,o.rho,last.sigma[i],last.residuals[i],last.satellites[i].azimuth,last.satellites[i].elevation])},'GNSS_Residuals');M.advanced.mode('data');}
 catch(err){out.classList.add('error');out.textContent=err.message;}});
})();
