(function(){
'use strict';
const by=id=>document.getElementById(id),canvas=by('ct-canvas'),ctx=canvas.getContext('2d');
function coefficients(text){const v=text.split(/[ ,;]+/).filter(Boolean).map(Number);if(!v.length||v.length>7||v.some(x=>!Number.isFinite(x)||Math.abs(x)>1e8)||v[0]===0)throw Error('Use 1–7 finite coefficients, first coefficient nonzero, |value| ≤ 1e8.');return v;}
function pad(a,n){return Array(n-a.length).fill(0).concat(a);}
function add(a,b){const n=Math.max(a.length,b.length),x=pad(a,n),y=pad(b,n);return x.map((v,i)=>v+y[i]);}
function mul(a,k){return a.map(v=>v*k);}
function evalPoly(poly,re,im){let x=0,y=0;for(const c of poly){const next=x*re-y*im+c;y=x*im+y*re;x=next;}return [x,y];}
function div(a,b){const d=b[0]*b[0]+b[1]*b[1];return d>1e-25?[(a[0]*b[0]+a[1]*b[1])/d,(a[1]*b[0]-a[0]*b[1])/d]:[NaN,NaN];}
function response(n,d,k,w){const z=div(evalPoly(n,0,w),evalPoly(d,0,w));return z.map(v=>v*k);}
function routh(p){let c=p.slice();const n=c.length-1,size=Math.ceil(c.length/2),rows=Array.from({length:n+1},()=>Array(size).fill(0));
for(let j=0;j<size;j++){rows[0][j]=c[2*j]||0;if(n)rows[1][j]=c[2*j+1]||0;}
let degenerate=false;for(let i=2;i<=n;i++){if(rows[i-1].every(x=>Math.abs(x)<1e-11)){degenerate=true;const power=n-(i-2);for(let j=0;j<size;j++)rows[i-1][j]=rows[i-2][j]*(power-2*j);}if(Math.abs(rows[i-1][0])<1e-11){rows[i-1][0]=1e-9;degenerate=true;}for(let j=0;j<size-1;j++)rows[i][j]=(rows[i-1][0]*rows[i-2][j+1]-rows[i-2][0]*rows[i-1][j+1])/rows[i-1][0];}
const first=rows.map(r=>r[0]);const changes=first.slice(1).reduce((n,x,i)=>n+(x*first[i]<0?1:0),0);return {rows,first,changes,degenerate};}
function roots(poly){let p=poly.slice();while(p.length>1&&Math.abs(p[0])<1e-12)p.shift();const degree=p.length-1;if(!degree)return [];const norm=p.map(v=>v/p[0]),radius=1+Math.max(...norm.slice(1).map(Math.abs));let z=Array.from({length:degree},(_,i)=>[radius*Math.cos(2*Math.PI*(i+.2)/degree),radius*Math.sin(2*Math.PI*(i+.2)/degree)]);
for(let iteration=0;iteration<160;iteration++){let delta=0;for(let i=0;i<degree;i++){let den=[1,0];for(let j=0;j<degree;j++)if(i!==j){const a=z[i][0]-z[j][0],b=z[i][1]-z[j][1];den=[den[0]*a-den[1]*b,den[0]*b+den[1]*a];}const step=div(evalPoly(norm,...z[i]),den);if(!Number.isFinite(step[0]))continue;const length=Math.hypot(...step);delta=Math.max(delta,length);z[i]=[z[i][0]-step[0],z[i][1]-step[1]];}if(delta<1e-9)break;}return z;}
// Minimum-total-displacement matching avoids drawing false connections between independently ordered roots.
function assignRoots(previous,next){
 const count=previous.length;if(next.length!==count)throw Error('Root-locus pole count changed.');
 let best=Infinity,assignment=null;
 function visit(i,used,cost,order){
  if(cost>=best)return;
  if(i===count){best=cost;assignment=order.slice();return;}
  for(let j=0;j<count;j++)if(!(used&(1<<j))){
   const dx=previous[i][0]-next[j][0],dy=previous[i][1]-next[j][1];
   visit(i+1,used|(1<<j),cost+dx*dx+dy*dy,order.concat([next[j]]));
  }
 }
 visit(0,0,0,[]);
 if(!assignment)throw Error('Unable to track root-locus branches.');
 return assignment;
}
function rootLocus(n,d,maxGain=100,steps=90){
 if(n.length>d.length)throw Error('Root locus requires numerator degree no greater than denominator degree.');
 if(!Number.isFinite(maxGain)||maxGain<=0||maxGain>1e6||!Number.isInteger(steps)||steps<2||steps>1000)throw Error('Invalid root-locus sampling range.');
 const branches=[];
 for(let i=0;i<steps;i++){
  const k=maxGain*i/(steps-1),found=roots(add(d,mul(n,k)));
  if(found.length!==d.length-1||found.some(p=>p.some(v=>!Number.isFinite(v))))throw Error('Root-locus poles failed to converge; inspect transfer function.');
  const ordered=i?assignRoots(branches.map(b=>b[i-1]),found):found.slice().sort((a,b)=>a[0]-b[0]||a[1]-b[1]);
  ordered.forEach((p,j)=>(branches[j]||(branches[j]=[])).push(p));
 }
 return branches;
}
// Stability margins reuse evalPoly/response/roots. Phase is unwrapped by aligning the wrapped
// atan2 value with a continuous root-angle sum, so the −180° branch is meaningful at every ω.
const W_MIN=0.01,W_MAX=1000;
function rootAngle(r,w){const a=r[0],b=r[1];return Math.abs(a)<1e-10*(1+Math.hypot(a,b))?(w>b?Math.PI/2:w<b?-Math.PI/2:0):a<0?Math.atan2(w-b,-a):Math.PI-Math.atan2(w-b,a);}
function phaseModel(n,d,k){const zs=roots(n),ps=roots(d),lead=k*n[0]/d[0],base=lead<0?Math.PI:0;
 return w=>{const z=response(n,d,k,w);if(!z.every(Number.isFinite))return NaN;let ref=base;for(const r of zs)ref+=rootAngle(r,w);for(const r of ps)ref-=rootAngle(r,w);const wrapped=Math.atan2(z[1],z[0]);return (wrapped+2*Math.PI*Math.round((ref-wrapped)/(2*Math.PI)))*180/Math.PI;};}
function bisect(f,a,b,fa){for(let i=0;i<80&&b-a>1e-14;i++){const m=(a+b)/2,fm=f(m);if(!Number.isFinite(fm))return NaN;if(fm===0)return m;if((fm<0)===(fa<0)){a=m;fa=fm;}else b=m;}return (a+b)/2;}
function goldenMax(f,a,b){const g=(Math.sqrt(5)-1)/2;let c=b-g*(b-a),e=a+g*(b-a),fc=f(c),fe=f(e);for(let i=0;i<100&&b-a>1e-13;i++){if(fc>fe){b=e;e=c;fe=fc;c=b-g*(b-a);fc=f(c);}else{a=c;c=e;fc=fe;e=a+g*(b-a);fe=f(e);}}return (a+b)/2;}
function margins(n,d,k,grid=2001){
 if(!Number.isFinite(k)||k===0)throw Error('Stability margins need a finite nonzero gain K.');
 const u0=Math.log10(W_MIN),u1=Math.log10(W_MAX),us=Array.from({length:grid},(_,i)=>u0+(u1-u0)*i/(grid-1));
 const mag=u=>20*Math.log10(Math.hypot(...response(n,d,k,Math.pow(10,u)))),phase=phaseModel(n,d,k),ph=u=>phase(Math.pow(10,u));
 const M=us.map(mag),P=us.map(ph),gain=[],phaseX=[];
 for(let i=1;i<grid;i++){
  if(Number.isFinite(M[i-1])&&Number.isFinite(M[i])&&(M[i-1]<0)!==(M[i]<0)){const u=bisect(mag,us[i-1],us[i],M[i-1]);if(Number.isFinite(u)){const w=Math.pow(10,u),p=ph(u);let pm=((p+180)%360+360)%360;if(pm>180)pm-=360;gain.push({w,phase:p,pm});}}
  const a=P[i-1],b=P[i];if(!Number.isFinite(a)||!Number.isFinite(b)||Math.abs(b-a)>90)continue;
  for(let m=Math.ceil((Math.min(a,b)+180)/360);m<=Math.floor((Math.max(a,b)+180)/360);m++){const target=-180+360*m;if(a===target&&i>1)continue;if(a===b)continue;
   const u=bisect(x=>ph(x)-target,us[i-1],us[i],a-target);if(!Number.isFinite(u))continue;const w=Math.pow(10,u),db=mag(u);if(Number.isFinite(db))phaseX.push({w,phase:target,gm:-db});}
 }
 // A DC gain of exactly one is a gain crossover at ω = 0, as for K/(s+K); it lies below the sampled range.
 // Likewise a negative real DC gain is a −180° phase crossover at ω = 0 (e.g. K/(s−1)).
 let dcPM=null;const d0=d.at(-1),n0=n.at(-1);
 if(Math.abs(d0)>1e-300){const g0=k*n0/d0;if(!gain.length&&Math.abs(Math.abs(g0)-1)<1e-9)dcPM={w:0,phase:g0>0?0:-180,pm:g0>0?180:0};
  if(g0<0&&!phaseX.some(x=>x.w<=W_MIN*1.0001))phaseX.unshift({w:0,phase:-180,gm:-20*Math.log10(-g0),dc:true});}
 const pmList=dcPM?[dcPM]:gain,pm=pmList.length?pmList.reduce((x,y)=>Math.abs(y.pm)<Math.abs(x.pm)?y:x):null;
 const gm=phaseX.length?phaseX.reduce((x,y)=>Math.abs(y.gm)<Math.abs(x.gm)?y:x):null;
 // Closed loop T = KN/(D+KN): bandwidth is the first −3 dB point below |T(0)|; Mr is the peak |T|/|T(0)|.
 const closed=add(d,mul(n,k)),kn=mul(n,k),T=w=>Math.hypot(...div(evalPoly(kn,0,w),evalPoly(closed,0,w)));
 const c0=closed.at(-1),t0=Math.abs(c0)>1e-300?Math.abs(k*n0/c0):NaN,stable=routh(closed).changes===0&&closed.length>1&&closed.every(c=>c*closed[0]>0);
 let bandwidth=null,peak=null,closedNote='';
 if(!Number.isFinite(t0)||t0===0)closedNote='Closed-loop DC gain is '+(t0===0?'zero':'undefined')+'; bandwidth and resonant peak are not defined.';
 else{const lvl=t0/Math.SQRT2,f=u=>20*Math.log10(T(Math.pow(10,u))/lvl);let prev=f(us[0]);
  if(prev<0)closedNote='|T| is already below the −3 dB level at 0.01 rad/s.';
  else for(let i=1;i<grid;i++){const cur=f(us[i]);if(Number.isFinite(cur)&&cur<0){bandwidth=Math.pow(10,bisect(f,us[i-1],us[i],prev));break;}prev=cur;}
  const tl=us.map(u=>T(Math.pow(10,u)));let j=0;for(let i=1;i<grid;i++)if(tl[i]>tl[j])j=i;
  if(j>0&&j<grid-1&&tl[j]>t0*(1+1e-9)){const u=goldenMax(x=>T(Math.pow(10,x)),us[j-1],us[j+1]),w=Math.pow(10,u),mr=T(w)/t0;peak={w,mr,db:20*Math.log10(mr)};}
  else if(j===grid-1)closedNote='|T| is still rising at 1000 rad/s; any resonant peak lies outside the sampled range.';
 }
 return {range:[W_MIN,W_MAX],gain,phase:phaseX,pm,gm,dcPM,bandwidth,peak,t0,closedStable:stable,closedNote};
}
function fmt(x,p=5){return Number(x.toPrecision(p)).toString();}
function marginText(r){const lines=['Stability margins (unity negative feedback, ω sampled 0.01–1000 rad/s, 2001-point log grid + bisection):'];
 lines.push(r.gm?'Gain margin: '+fmt(r.gm.gm)+' dB at phase crossover ω = '+(r.gm.w===0?'0 (negative real DC gain)':fmt(r.gm.w)+' rad/s')+(r.phase.length>1?' (smallest of '+r.phase.length+' crossovers)':'')+'.':'Gain margin: infinite (no −180° phase crossover in 0.01–1000 rad/s).');
 lines.push(r.pm?'Phase margin: '+fmt(r.pm.pm)+'° at gain crossover ω = '+(r.pm.w===0?'0 (DC gain exactly 1; no crossover for ω > 0)':fmt(r.pm.w)+' rad/s')+(r.gain.length>1?' (smallest of '+r.gain.length+' crossovers)':'')+'.':'Phase margin: infinite (|KG(jω)| never crosses 0 dB in 0.01–1000 rad/s).');
 lines.push(r.bandwidth?'Closed-loop bandwidth (−3 dB below |T(0)| = '+fmt(r.t0)+'): '+fmt(r.bandwidth)+' rad/s.':'Closed-loop bandwidth: not found in 0.01–1000 rad/s.');
 lines.push(r.peak?'Resonant peak Mr = '+fmt(r.peak.mr)+' ('+fmt(r.peak.db,4)+' dB) at ωr = '+fmt(r.peak.w)+' rad/s.':'Resonant peak: none in range (|T| ≤ |T(0)|).');
 if(r.closedNote)lines.push(r.closedNote);
 lines.push(r.closedStable?'Closed-loop characteristic polynomial passes the Routh test.':'Warning: the closed loop is not shown stable by the Routh test; margins describe the frequency response only.');
 lines.push('Crossings outside 0.01–1000 rad/s are not detected; margins are numerical estimates, not a certified loop-shaping design.');
 return lines.join('\n');}
function draw(points,xlabel,ylabel,scatter=false,branches=null,markers=null){const w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);const finite=points.filter(p=>p.every(Number.isFinite));if(!finite.length)return;const xs=finite.map(p=>p[0]),ys=finite.map(p=>p[1]);let xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);const dx=Math.max(xmax-xmin,1e-4),dy=Math.max(ymax-ymin,1e-4);xmin-=dx*.08;xmax+=dx*.08;ymin-=dy*.08;ymax+=dy*.08;const X=x=>55+(x-xmin)/(xmax-xmin)*(w-90),Y=y=>h-45-(y-ymin)/(ymax-ymin)*(h-85);ctx.strokeStyle='#dde8ea';ctx.lineWidth=1;for(let i=0;i<=5;i++){ctx.beginPath();ctx.moveTo(55+i*(w-90)/5,20);ctx.lineTo(55+i*(w-90)/5,h-45);ctx.moveTo(55,20+i*(h-85)/5);ctx.lineTo(w-35,20+i*(h-85)/5);ctx.stroke();}ctx.strokeStyle='#157e78';ctx.fillStyle='#157e78';ctx.lineWidth=2;if(branches){for(const branch of branches){ctx.beginPath();let started=false;for(const p of branch){if(!p.every(Number.isFinite)){started=false;continue;}if(started)ctx.lineTo(X(p[0]),Y(p[1]));else{ctx.moveTo(X(p[0]),Y(p[1]));started=true;}}ctx.stroke();}finite.forEach(p=>{ctx.beginPath();ctx.arc(X(p[0]),Y(p[1]),2.2,0,Math.PI*2);ctx.fill();});}else if(scatter){finite.forEach(p=>{ctx.beginPath();ctx.arc(X(p[0]),Y(p[1]),2.2,0,Math.PI*2);ctx.fill();});}else{ctx.beginPath();finite.forEach((p,i)=>i?ctx.lineTo(X(p[0]),Y(p[1])):ctx.moveTo(X(p[0]),Y(p[1])));ctx.stroke();}if(markers)for(const m of markers){if(!Number.isFinite(m.x)||!Number.isFinite(m.y))continue;ctx.fillStyle=m.color;ctx.beginPath();ctx.arc(X(m.x),Y(m.y),6,0,Math.PI*2);ctx.fill();ctx.font='13px system-ui';ctx.fillText(m.label,Math.min(X(m.x)+9,w-150),Math.max(Y(m.y)-9,34));}ctx.fillStyle='#25464f';ctx.font='14px system-ui';ctx.fillText(xlabel,w/2,h-12);ctx.fillText(ylabel,15,25);}
function analyze(){try{const n=coefficients(by('ct-num').value),d=coefficients(by('ct-den').value),k=Number(by('ct-gain').value);if(!Number.isFinite(k)||Math.abs(k)>1e6)throw Error('Gain must be finite and bounded.');const mode=by('ct-mode').value,closed=add(d,mul(n,k));let pts=[],message='G(s) = '+n.join(', ')+' / ('+d.join(', ')+'); gain '+k+'.\n';const samples=Array.from({length:220},(_,i)=>Math.pow(10,-2+5*i/219));
if(mode==='bode'){pts=samples.map(w=>{const z=response(n,d,k,w);return [Math.log10(w),20*Math.log10(Math.hypot(...z))];});const phases=samples.map(w=>Math.atan2(response(n,d,k,w)[1],response(n,d,k,w)[0])*180/Math.PI);const mr=k?margins(n,d,k):null,marks=[];if(mr&&mr.pm&&mr.pm.w>0)marks.push({x:Math.log10(mr.pm.w),y:0,color:'#b4234a',label:'PM '+fmt(mr.pm.pm,4)+'°'});if(mr&&mr.gm&&mr.gm.w>0)marks.push({x:Math.log10(mr.gm.w),y:-mr.gm.gm,color:'#6a3fb5',label:'GM '+fmt(mr.gm.gm,4)+' dB'});message+='Bode magnitude (dB) vs log10(ω). Phase samples: '+phases[0].toFixed(2)+'° → '+phases.at(-1).toFixed(2)+'° (wrapped).\n'+(mr?marginText(mr):'Stability margins need a nonzero gain K.');if(mr)by('ct-margins-output').textContent=marginText(mr);draw(pts,'log10(ω rad/s)','Gain (dB)',false,null,marks);}
else if(mode==='nyquist'){pts=samples.map(w=>response(n,d,k,w));pts=pts.concat(pts.slice().reverse().map(p=>[p[0],-p[1]]));message+='Nyquist frequency response for ±ω; critical point is (-1,0). Stability must be confirmed with open-loop RHP pole count.';draw(pts,'Re G(jω)','Im G(jω)');}
else if(mode==='root'){const branches=rootLocus(n,d);pts=branches.flat();message+='Root locus for K from 0 to 100 with sampled, minimum-displacement pole branch tracking. Near repeated poles or branch crossings, verify numerically.';draw(pts,'Real pole','Imaginary pole',false,branches);}
else if(mode==='routh'){const result=routh(d);message+='Routh table:\n'+result.rows.map(row=>row.map(x=>Number(x.toPrecision(6))).join('    ')).join('\n')+'\nSign changes in first column: '+result.changes+(result.degenerate?' (special zero-row/pivot case; inspect separately)':'')+'.';draw(result.first.map((v,i)=>[i,v]),'Routh row','First-column value');}
else{const r=routh(closed);pts=samples.map(w=>{const z=div(evalPoly(mul(n,k),0,w),evalPoly(closed,0,w));return [Math.log10(w),20*Math.log10(Math.hypot(...z))];});message+='Unity negative feedback: T(s) = K N(s) / [D(s)+K N(s)]\nCharacteristic polynomial: '+closed.join(', ')+'\nRouth sign changes: '+r.changes+(r.degenerate?' (special-case caveat)':'')+'.';draw(pts,'log10(ω rad/s)','Closed-loop dB');}
by('ct-output').textContent=message;by('ct-status').textContent='Analysis completed for supported continuous-time SISO model.';}
catch(e){by('ct-status').textContent=e.message;by('ct-output').textContent='No valid result.';ctx.clearRect(0,0,canvas.width,canvas.height);}}
function analyzeMargins(){const out=by('ct-margins-output');try{const n=coefficients(by('ct-num').value),d=coefficients(by('ct-den').value),k=Number(by('ct-gain').value);if(!Number.isFinite(k)||Math.abs(k)>1e6)throw Error('Gain must be finite and bounded.');out.textContent=marginText(margins(n,d,k));by('ct-margins-status').textContent='Margins computed for the current transfer function.';}catch(e){by('ct-margins-status').textContent=e.message;out.textContent='No valid margins.';}}
by('ct-run').addEventListener('click',analyze);
by('ct-margins-run').addEventListener('click',analyzeMargins);
window.ProMathControlTheory={coefficients,routh,roots,response,assignRoots,rootLocus,margins,marginText,analyze,analyzeMargins};
})();
