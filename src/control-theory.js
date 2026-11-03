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
function draw(points,xlabel,ylabel,scatter=false,branches=null){const w=canvas.width,h=canvas.height;ctx.clearRect(0,0,w,h);ctx.fillStyle='#fff';ctx.fillRect(0,0,w,h);const finite=points.filter(p=>p.every(Number.isFinite));if(!finite.length)return;const xs=finite.map(p=>p[0]),ys=finite.map(p=>p[1]);let xmin=Math.min(...xs),xmax=Math.max(...xs),ymin=Math.min(...ys),ymax=Math.max(...ys);const dx=Math.max(xmax-xmin,1e-4),dy=Math.max(ymax-ymin,1e-4);xmin-=dx*.08;xmax+=dx*.08;ymin-=dy*.08;ymax+=dy*.08;const X=x=>55+(x-xmin)/(xmax-xmin)*(w-90),Y=y=>h-45-(y-ymin)/(ymax-ymin)*(h-85);ctx.strokeStyle='#dde8ea';ctx.lineWidth=1;for(let i=0;i<=5;i++){ctx.beginPath();ctx.moveTo(55+i*(w-90)/5,20);ctx.lineTo(55+i*(w-90)/5,h-45);ctx.moveTo(55,20+i*(h-85)/5);ctx.lineTo(w-35,20+i*(h-85)/5);ctx.stroke();}ctx.strokeStyle='#157e78';ctx.fillStyle='#157e78';ctx.lineWidth=2;if(branches){for(const branch of branches){ctx.beginPath();let started=false;for(const p of branch){if(!p.every(Number.isFinite)){started=false;continue;}if(started)ctx.lineTo(X(p[0]),Y(p[1]));else{ctx.moveTo(X(p[0]),Y(p[1]));started=true;}}ctx.stroke();}finite.forEach(p=>{ctx.beginPath();ctx.arc(X(p[0]),Y(p[1]),2.2,0,Math.PI*2);ctx.fill();});}else if(scatter){finite.forEach(p=>{ctx.beginPath();ctx.arc(X(p[0]),Y(p[1]),2.2,0,Math.PI*2);ctx.fill();});}else{ctx.beginPath();finite.forEach((p,i)=>i?ctx.lineTo(X(p[0]),Y(p[1])):ctx.moveTo(X(p[0]),Y(p[1])));ctx.stroke();}ctx.fillStyle='#25464f';ctx.font='14px system-ui';ctx.fillText(xlabel,w/2,h-12);ctx.fillText(ylabel,15,25);}
function analyze(){try{const n=coefficients(by('ct-num').value),d=coefficients(by('ct-den').value),k=Number(by('ct-gain').value);if(!Number.isFinite(k)||Math.abs(k)>1e6)throw Error('Gain must be finite and bounded.');const mode=by('ct-mode').value,closed=add(d,mul(n,k));let pts=[],message='G(s) = '+n.join(', ')+' / ('+d.join(', ')+'); gain '+k+'.\n';const samples=Array.from({length:220},(_,i)=>Math.pow(10,-2+5*i/219));
if(mode==='bode'){pts=samples.map(w=>{const z=response(n,d,k,w);return [Math.log10(w),20*Math.log10(Math.hypot(...z))];});const phases=samples.map(w=>Math.atan2(response(n,d,k,w)[1],response(n,d,k,w)[0])*180/Math.PI);message+='Bode magnitude (dB) vs log10(ω). Phase samples: '+phases[0].toFixed(2)+'° → '+phases.at(-1).toFixed(2)+'° (wrapped).';draw(pts,'log10(ω rad/s)','Gain (dB)');}
else if(mode==='nyquist'){pts=samples.map(w=>response(n,d,k,w));pts=pts.concat(pts.slice().reverse().map(p=>[p[0],-p[1]]));message+='Nyquist frequency response for ±ω; critical point is (-1,0). Stability must be confirmed with open-loop RHP pole count.';draw(pts,'Re G(jω)','Im G(jω)');}
else if(mode==='root'){const branches=rootLocus(n,d);pts=branches.flat();message+='Root locus for K from 0 to 100 with sampled, minimum-displacement pole branch tracking. Near repeated poles or branch crossings, verify numerically.';draw(pts,'Real pole','Imaginary pole',false,branches);}
else if(mode==='routh'){const result=routh(d);message+='Routh table:\n'+result.rows.map(row=>row.map(x=>Number(x.toPrecision(6))).join('    ')).join('\n')+'\nSign changes in first column: '+result.changes+(result.degenerate?' (special zero-row/pivot case; inspect separately)':'')+'.';draw(result.first.map((v,i)=>[i,v]),'Routh row','First-column value');}
else{const r=routh(closed);pts=samples.map(w=>{const z=div(evalPoly(mul(n,k),0,w),evalPoly(closed,0,w));return [Math.log10(w),20*Math.log10(Math.hypot(...z))];});message+='Unity negative feedback: T(s) = K N(s) / [D(s)+K N(s)]\nCharacteristic polynomial: '+closed.join(', ')+'\nRouth sign changes: '+r.changes+(r.degenerate?' (special-case caveat)':'')+'.';draw(pts,'log10(ω rad/s)','Closed-loop dB');}
by('ct-output').textContent=message;by('ct-status').textContent='Analysis completed for supported continuous-time SISO model.';}
catch(e){by('ct-status').textContent=e.message;by('ct-output').textContent='No valid result.';ctx.clearRect(0,0,canvas.width,canvas.height);}}
by('ct-run').addEventListener('click',analyze);
window.ProMathControlTheory={coefficients,routh,roots,response,assignRoots,rootLocus,analyze};
})();
