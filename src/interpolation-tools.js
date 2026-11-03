/* ProMathStudio: bounded offline one-dimensional linear, PCHIP, barycentric, cubic spline and Akima interpolation. */
(()=>{'use strict';
const M=window.MathStudio, panel=document.getElementById('numerical-panel');
if(!M?.dataTables||!M?.advanced||!panel)return;
const $=id=>document.getElementById(id);
const LIMIT=1e12, MAX_POINTS=200, MAX_QUERIES=1000;
function number(value,label){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(label+' is required.');
 const n=Number(value);
 if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(label+' must be finite with magnitude at most 1e12.');
 return n;
}
function pchipSlopes(samples){
 const n=samples.length,h=[],delta=[];
 for(let i=0;i<n-1;i++){
  const width=samples[i+1][0]-samples[i][0],secant=(samples[i+1][1]-samples[i][1])/width;
  if(!(width>0)||!Number.isFinite(width)||!Number.isFinite(secant))
   throw Error('Sample spacing or values cause a non-finite interpolation slope.');
  h.push(width);delta.push(secant);
 }
 if(n===2)return [delta[0],delta[0]];
 const slopes=Array(n).fill(0);
 const endpoint=(h0,h1,d0,d1)=>{
  let m=((2*h0+h1)*d0-h0*d1)/(h0+h1);
  if(!Number.isFinite(m))throw Error('Endpoint interpolation slope is non-finite.');
  if(Math.sign(m)!==Math.sign(d0))return 0;
  if(Math.sign(d0)!==Math.sign(d1)&&Math.abs(m)>3*Math.abs(d0))m=3*d0;
  return m;
 };
 slopes[0]=endpoint(h[0],h[1],delta[0],delta[1]);
 slopes[n-1]=endpoint(h[n-2],h[n-3],delta[n-2],delta[n-3]);
 for(let i=1;i<n-1;i++){
  const left=delta[i-1],right=delta[i];
  if(!left||!right||Math.sign(left)!==Math.sign(right))continue;
  const a=(2*h[i]+h[i-1])/(3*(h[i-1]+h[i]));
  const denominator=a/left+(1-a)/right;
  slopes[i]=Number.isFinite(denominator)&&denominator!==0?1/denominator:0;
 }
 return slopes;
}
function barycentricWeights(samples){
 // Global polynomial interpolation is deliberately capped to avoid high-degree instability.
 if(samples.length>16)throw Error('Barycentric polynomial interpolation accepts at most 16 sample points.');
 const logs=[],signs=[];
 for(let i=0;i<samples.length;i++){
  let logWeight=0,sign=1;
  for(let j=0;j<samples.length;j++){
   if(i===j)continue;
   const dx=samples[i][0]-samples[j][0];
   if(!Number.isFinite(dx)||Math.abs(dx)<=32*Number.EPSILON*Math.max(1,Math.abs(samples[i][0]),Math.abs(samples[j][0])))
    throw Error('Sample x spacing is too small for stable polynomial interpolation.');
   logWeight-=Math.log(Math.abs(dx));
   if(dx<0)sign=-sign;
  }
  logs.push(logWeight);signs.push(sign);
 }
 const max=Math.max(...logs);
 return logs.map((v,i)=>signs[i]*Math.exp(v-max));
}
const SPLINE_METHODS={
 natural:{min:2,label:'Natural cubic spline (zero end second derivatives)',name:'Natural'},
 clamped:{min:2,label:'Clamped cubic spline (user end slopes)',name:'Clamped'},
 notaknot:{min:4,label:'Not-a-knot cubic spline (continuous third derivative at x1 and x(n-2))',name:'NotAKnot'},
 periodic:{min:3,label:'Periodic cubic spline (matching end value, slope and curvature)',name:'Periodic'},
 akima:{min:3,label:'Akima (1970) local cubic interpolation',name:'Akima'},
 makima:{min:3,label:'Modified Akima (makima) local cubic interpolation',name:'Makima'}
};
const METHODS=['linear','pchip','barycentric',...Object.keys(SPLINE_METHODS)];
function thomas(sub,diag,sup,rhs){
 // Tridiagonal solve without pivoting; callers supply diagonally dominant systems.
 const n=diag.length,c=Array(n),d=Array(n);
 let pivot=diag[0];
 if(!(Math.abs(pivot)>0))throw Error('Spline system is singular.');
 c[0]=n>1?sup[0]/pivot:0;d[0]=rhs[0]/pivot;
 for(let i=1;i<n;i++){
  pivot=diag[i]-sub[i]*c[i-1];
  if(!(Math.abs(pivot)>0)||!Number.isFinite(pivot))throw Error('Spline system is singular.');
  c[i]=i<n-1?sup[i]/pivot:0;d[i]=(rhs[i]-sub[i]*d[i-1])/pivot;
 }
 for(let i=n-2;i>=0;i--)d[i]-=c[i]*d[i+1];
 return d;
}
function cyclicThomas(sub,diag,sup,rhs){
 // Sherman-Morrison solve of a cyclic tridiagonal system; sub[0] and sup[n-1] are the corner entries.
 const n=diag.length;
 if(n===2){
  const a=diag[0],b=sup[0]+sub[0],c=sub[1]+sup[1],d=diag[1],det=a*d-b*c;
  if(!(Math.abs(det)>0))throw Error('Periodic spline system is singular.');
  return [(rhs[0]*d-b*rhs[1])/det,(a*rhs[1]-c*rhs[0])/det];
 }
 const alpha=sub[0],beta=sup[n-1],gamma=-diag[0];
 const b=diag.slice();b[0]-=gamma;b[n-1]-=alpha*beta/gamma;
 const s=sub.slice(),p=sup.slice();s[0]=0;p[n-1]=0;
 const x=thomas(s,b,p,rhs);
 const u=Array(n).fill(0);u[0]=gamma;u[n-1]=beta;
 const z=thomas(s,b,p,u);
 const factor=(x[0]+alpha*x[n-1]/gamma)/(1+z[0]+alpha*z[n-1]/gamma);
 if(!Number.isFinite(factor))throw Error('Periodic spline system is singular.');
 return x.map((v,i)=>v-factor*z[i]);
}
function segments(samples){
 const h=[],delta=[];
 for(let i=0;i<samples.length-1;i++){
  const width=samples[i+1][0]-samples[i][0],secant=(samples[i+1][1]-samples[i][1])/width;
  if(!(width>0)||!Number.isFinite(width)||!Number.isFinite(secant))
   throw Error('Sample spacing or values cause a non-finite interpolation slope.');
  h.push(width);delta.push(secant);
 }
 return {h,delta};
}
function splineSlopes(samples,method,endSlopes){
 // All cubic methods are stored as node slopes and evaluated in cubic Hermite form.
 const n=samples.length,{h,delta}=segments(samples);
 if(method==='akima'||method==='makima'){
  // Akima (1970): extend the secants by two linearly extrapolated values at each end.
  const d=[0,0,...delta,0,0],k=n-1;
  d[1]=2*d[2]-d[3];d[0]=2*d[1]-d[2];
  d[k+2]=2*d[k+1]-d[k];d[k+3]=2*d[k+2]-d[k+1];
  const slopes=[];
  for(let i=0;i<n;i++){
   const a=d[i],b=d[i+1],c=d[i+2],e=d[i+3];
   let w1=Math.abs(e-c),w2=Math.abs(b-a);
   if(method==='makima'){w1+=Math.abs(e+c)/2;w2+=Math.abs(b+a)/2;}
   const sum=w1+w2;
   const m=sum>0?(w1*b+w2*c)/sum:(method==='makima'?0:(b+c)/2);
   if(!Number.isFinite(m))throw Error('Akima slope is non-finite.');
   slopes.push(m);
  }
  return slopes;
 }
 // Interior C2 condition: h_i m_(i-1) + 2(h_(i-1)+h_i) m_i + h_(i-1) m_(i+1) = 3(h_i d_(i-1) + h_(i-1) d_i).
 const interior=i=>[h[i],2*(h[i-1]+h[i]),h[i-1],3*(h[i]*delta[i-1]+h[i-1]*delta[i])];
 if(method==='periodic'){
  const N=n-1,sub=[],diag=[],sup=[],rhs=[];
  for(let i=0;i<N;i++){
   const hp=h[(i-1+N)%N],hc=h[i],dp=delta[(i-1+N)%N],dc=delta[i];
   sub.push(hc);diag.push(2*(hp+hc));sup.push(hp);rhs.push(3*(hc*dp+hp*dc));
  }
  const m=cyclicThomas(sub,diag,sup,rhs);
  return [...m,m[0]];
 }
 if(method==='notaknot'){
  // Eliminate the two not-a-knot end rows so the reduced interior system stays diagonally dominant.
  const d0=h[0]+h[1],r0=((h[0]+2*d0)*h[1]*delta[0]+h[0]*h[0]*delta[1])/d0;
  const dl=h[n-3]+h[n-2],rl=(h[n-2]*h[n-2]*delta[n-3]+(2*dl+h[n-2])*h[n-3]*delta[n-2])/dl;
  const sub=[],diag=[],sup=[],rhs=[];
  for(let i=1;i<n-1;i++){const [a,b,c,r]=interior(i);sub.push(a);diag.push(b);sup.push(c);rhs.push(r);}
  diag[0]-=d0;rhs[0]-=r0;sub[0]=0;
  const L=diag.length-1;diag[L]-=dl;rhs[L]-=rl;sup[L]=0;
  const m=thomas(sub,diag,sup,rhs);
  return [(r0-d0*m[0])/h[1],...m,(rl-dl*m[L])/h[n-3]];
 }
 const sub=[0],diag=[],sup=[],rhs=[];
 if(method==='clamped'){diag.push(1);sup.push(0);rhs.push(endSlopes[0]);}
 else{diag.push(2);sup.push(1);rhs.push(3*delta[0]);}
 for(let i=1;i<n-1;i++){const [a,b,c,r]=interior(i);sub.push(a);diag.push(b);sup.push(c);rhs.push(r);}
 if(method==='clamped'){sub.push(0);diag.push(1);rhs.push(endSlopes[1]);}
 else{sub.push(1);diag.push(2);rhs.push(3*delta[n-2]);}
 sup.push(0);
 return thomas(sub,diag,sup,rhs);
}
function hermiteIntegral(y0,y1,m0,m1,h,t){
 // Exact integral of the cubic Hermite piece from its left knot to t in [0,1].
 const t2=t*t,t3=t2*t,t4=t3*t;
 return h*((t4/2-t3+t)*y0+(t4/4-2*t3/3+t2/2)*h*m0+(t3-t4/2)*y1+(t4/4-t3/3)*h*m1);
}
function prepareSpline(samples,method,endSlopes){
 const spec=SPLINE_METHODS[method];
 if(samples.length<spec.min)throw Error(spec.label+' needs at least '+spec.min+' sample points.');
 let ends=null;
 if(method==='clamped'){
  if(!Array.isArray(endSlopes)||endSlopes.length!==2)throw Error('Clamped spline needs start and end slopes.');
  ends=[number(endSlopes[0],'Start slope'),number(endSlopes[1],'End slope')];
 }
 if(method==='periodic'){
  const y0=samples[0][1],yn=samples[samples.length-1][1];
  const scale=Math.max(1,...samples.map(p=>Math.abs(p[1])));
  if(!(Math.abs(y0-yn)<=1e-9*scale))
   throw Error('Periodic spline requires the first and last y values to match (|y0 - yn| <= 1e-9 x max(1, max|y|)).');
  samples=samples.map((p,i)=>i===samples.length-1?[p[0],y0]:p);
 }
 const slopes=splineSlopes(samples,method,ends);
 const cumulative=[0];
 for(let i=0;i<samples.length-1;i++){
  const h=samples[i+1][0]-samples[i][0];
  cumulative.push(cumulative[i]+h*(samples[i][1]+samples[i+1][1])/2+h*h*(slopes[i]-slopes[i+1])/12);
 }
 if(!slopes.every(Number.isFinite)||!cumulative.every(Number.isFinite))throw Error('Spline coefficients are non-finite.');
 return {samples,slopes,cumulative};
}
function evaluateSpline(spline,lo,hi,x){
 const {samples,slopes,cumulative}=spline,[x0,y0]=samples[lo],[x1,y1]=samples[hi];
 const h=x1-x0,t=(x-x0)/h,t2=t*t,t3=t2*t,m0=slopes[lo],m1=slopes[hi];
 // Return exact sample values at knots; elsewhere evaluate the cubic Hermite form.
 const y=x===x0?y0:x===x1?y1:(2*t3-3*t2+1)*y0+(t3-2*t2+t)*h*m0+(3*t2-2*t3)*y1+(t3-t2)*h*m1;
 const d1=x===x0?m0:x===x1?m1:((6*t2-6*t)*(y0-y1)+(3*t2-4*t+1)*h*m0+(3*t2-2*t)*h*m1)/h;
 const d2=((12*t-6)*(y0-y1)+(6*t-4)*h*m0+(6*t-2)*h*m1)/(h*h);
 const integral=x===x1?cumulative[hi]:cumulative[lo]+hermiteIntegral(y0,y1,m0,m1,h,t);
 return [x,number(y,'Interpolated y'),number(d1,'First derivative'),number(d2,'Second derivative'),number(integral,'Integral')];
}
function interpolate({points,queries,method='linear'}={}){
 // Optional clamped end slopes are read separately so the established signature stays unchanged.
 const endSlopes=arguments[0]?.endSlopes;
 if(!METHODS.includes(method))throw Error('Interpolation method must be linear, pchip, barycentric, natural, clamped, notaknot, periodic, akima or makima.');
 if(!Array.isArray(points)||points.length<2||points.length>MAX_POINTS)throw Error('Provide 2–200 sample points.');
 if(!Array.isArray(queries)||queries.length<1||queries.length>MAX_QUERIES)throw Error('Provide 1–1000 query x values.');
 const samples=points.map((pair,i)=>{
  if(!Array.isArray(pair)||pair.length!==2)throw Error('Each sample must have exactly x and y.');
  return [number(pair[0],'Sample x '+(i+1)),number(pair[1],'Sample y '+(i+1))];
 });
 for(let i=1;i<samples.length;i++)if(!(samples[i][0]>samples[i-1][0]))
  throw Error('Sample x values must be strictly increasing; duplicates and unsorted points are not allowed.');
 const spec=SPLINE_METHODS[method];
 const spline=spec?prepareSpline(samples,method,endSlopes):null;
 const slopes=method==='pchip'?pchipSlopes(samples):null;
 const weights=method==='barycentric'?barycentricWeights(samples):null;
 const xs=queries.map((x,i)=>number(x,'Query x '+(i+1))).sort((a,b)=>a-b);
 const min=samples[0][0],max=samples[samples.length-1][0];
 if(spline){
  const rows=xs.map(x=>{
   if(x<min||x>max)throw Error('Query x='+x+' is outside sample domain ['+min+', '+max+']; extrapolation is disabled.');
   let lo=0,hi=samples.length-1;
   while(hi-lo>1){const mid=Math.floor((lo+hi)/2);if(samples[mid][0]<=x)lo=mid;else hi=mid;}
   return evaluateSpline(spline,lo,hi,x);
  });
  const local=method==='akima'||method==='makima';
  return {type:'interpolation-'+method,columns:['x','y','dy/dx','d2y/dx2','integral from x0'],rows,domain:[min,max],
   method:spec.label,tableName:'Interpolation_'+spec.name,slopes:spline.slopes.slice(),
   note:(local?'Local C1 cubic (second derivative may jump at knots); ':'Global C2 cubic spline; ')+
    'derivatives and the integral are exact for the piecewise cubic, not for the unknown source function; no extrapolation or uncertainty estimate.'};
 }
 const rows=xs.map(x=>{
  if(x<min||x>max)throw Error('Query x='+x+' is outside sample domain ['+min+', '+max+']; extrapolation is disabled.');
  let lo=0,hi=samples.length-1;
  while(hi-lo>1){const mid=Math.floor((lo+hi)/2);if(samples[mid][0]<=x)lo=mid;else hi=mid;}
  const [x0,y0]=samples[lo],[x1,y1]=samples[hi];
  // Return exact sample values at knots; subtraction can lose small endpoint values.
  if(x===x0)return [x,y0];
  if(x===x1)return [x,y1];
  const fraction=(x-x0)/(x1-x0);
  let y;
  if(method==='barycentric'){
   const terms=samples.map((p,i)=>weights[i]/(x-p[0]));
   const scale=Math.max(...terms.map(Math.abs));
   if(!(scale>0)||!Number.isFinite(scale))throw Error('Barycentric evaluation is numerically unstable.');
   const scaled=terms.map(t=>t/scale);
   const denominator=scaled.reduce((a,b)=>a+b,0);
   const sumAbs=scaled.reduce((a,b)=>a+Math.abs(b),0);
   if(!Number.isFinite(denominator)||Math.abs(denominator)<=1e-12*sumAbs)
    throw Error('Barycentric evaluation is ill-conditioned; use fewer or better-spaced nodes.');
   // Evaluate around a nearby y value to reduce cancellation, especially near knots.
   const anchor=Math.abs(x-x0)<=Math.abs(x-x1)?y0:y1;
   const correction=scaled.reduce((sum,t,i)=>sum+t*(samples[i][1]-anchor),0);
   y=number(anchor+correction/denominator,'Interpolated y');
  }else if(method==='pchip'){
   const t=fraction,t2=t*t,t3=t2*t,h=x1-x0;
   const h00=2*t3-3*t2+1,h10=t3-2*t2+t,h01=-2*t3+3*t2,h11=t3-t2;
   y=number(h00*y0+h10*h*slopes[lo]+h01*y1+h11*h*slopes[hi],'Interpolated y');
   // Guard tiny floating-point overshoots at monotone knots.
   y=Math.max(Math.min(y0,y1),Math.min(Math.max(y0,y1),y));
  }else y=number(y0+(y1-y0)*fraction,'Interpolated y');
  return [x,y];
 });
 return {type:method==='barycentric'?'interpolation-barycentric':method==='pchip'?'interpolation-pchip':'interpolation-linear',columns:['x','y'],rows,domain:[min,max],
  method:method==='barycentric'?'Barycentric polynomial interpolation (global; at most 16 nodes)':method==='pchip'?'Shape-preserving cubic Hermite interpolation (PCHIP)':'Piecewise-linear interpolation (sorted finite real samples)',
  note:method==='barycentric'?'Global polynomial can oscillate between nodes, especially for equally spaced/high-degree samples; no extrapolation or uncertainty estimate.':method==='pchip'?'Piecewise monotone cubic interpolation; no extrapolation, global smoothness or uncertainty estimate.':'Interpolates only within the supplied domain; no extrapolation, spline smoothing or uncertainty estimate.'};
}
function parsePairs(text){
 text=String(text);
 if(text.length>16000)throw Error('Sample text is too long.');
 const lines=text.split(/\r?\n/).map(s=>s.trim()).filter(Boolean);
 if(lines.length<2||lines.length>MAX_POINTS)throw Error('Enter 2–200 sample lines, each x,y.');
 return lines.map((line,i)=>{
  const parts=line.split(/[,;\t ]+/).filter(Boolean);
  if(parts.length!==2)throw Error('Sample line '+(i+1)+' must contain exactly x,y.');
  return parts;
 });
}
function parseQueries(text){
 text=String(text);
 if(text.length>16000)throw Error('Query text is too long.');
 const parts=text.trim().split(/[,;\s]+/).filter(Boolean);
 if(!parts.length||parts.length>MAX_QUERIES)throw Error('Enter 1–1000 query x values.');
 return parts;
}
const area=document.createElement('details');area.id='interp-details';
area.innerHTML='<summary>1D interpolation · Linear / PCHIP / Polynomial / Cubic splines / Akima · Data Tables / Graphs</summary>'+
 '<p class="graph-data-muted">Enter sorted sample pairs (x,y), one per line, or load the first two columns of the active Data Table. Query values must be inside the sample domain.</p>'+
 '<div class="data-toolbar"><label>Interpolation method <select id="interp-method"><option value="linear">Linear</option><option value="pchip">Shape-preserving cubic (PCHIP)</option><option value="barycentric">Polynomial (barycentric, 2–16 points)</option>'+
 '<option value="natural">Natural cubic spline</option><option value="clamped">Clamped cubic spline (end slopes)</option>'+
 '<option value="notaknot">Not-a-knot cubic spline (4+ points)</option><option value="periodic">Periodic cubic spline (y0 = yn)</option>'+
 '<option value="akima">Akima (1970)</option><option value="makima">Modified Akima (makima)</option></select></label>'+
 '<label id="interp-slopes" hidden>Clamped end slopes <input id="interp-slope-start" type="text" inputmode="decimal" value="0" aria-label="Clamped start slope dy/dx at x0" size="8">'+
 '<input id="interp-slope-end" type="text" inputmode="decimal" value="0" aria-label="Clamped end slope dy/dx at xn" size="8"></label></div>'+
 '<div class="interp-fields"><label>Sample pairs (x,y)<textarea id="interp-samples" rows="5" spellcheck="false">0,0\n1,2\n2,4</textarea></label>'+
 '<label>Query x values (comma, space or newline separated)<textarea id="interp-queries" rows="5" spellcheck="false">0,0.5,1,1.5,2</textarea></label></div>'+
 '<div class="data-toolbar"><button id="interp-from-table" class="secondary" type="button">Load active table x/y</button>'+
 '<button id="interp-run" class="primary" type="button">Interpolate</button>'+
 '<button id="interp-to-table" class="secondary" type="button" disabled>Save to Data Tables</button>'+
 '<button id="interp-to-graph" class="secondary" type="button" disabled>Plot in Graphs</button></div>'+
 '<pre id="interp-output" role="status" aria-live="polite">Enter sorted samples and query values.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#interp-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px}'+
 '#interp-details summary{cursor:pointer;color:#3c50ae;font-weight:750}'+
 '.interp-fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin:12px 0}'+
 '.interp-fields label{display:flex;flex-direction:column;gap:6px;font-size:12px;font-weight:700;color:#566784}'+
 '.interp-fields textarea{width:100%;padding:10px;border:1px solid #cdd8ec;border-radius:9px;font:13px Consolas,monospace}'+
 '#interp-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:white;border:1px solid #dce5f3;border-radius:10px}'+
 '#interp-output.error{color:#a82241;background:#fff2f4}'+
 '#interp-slopes[hidden]{display:none}#interp-slopes input{width:6.5em;margin-left:6px;padding:6px;border:1px solid #cdd8ec;border-radius:7px;font:13px Consolas,monospace}'+
 '@media(max-width:600px){.interp-fields{grid-template-columns:1fr}#interp-slopes input{width:5.5em}}';
document.head.append(style);
let last=null;
function invalidate(){
 last=null;$('interp-to-table').disabled=$('interp-to-graph').disabled=true;
 $('interp-output').classList.remove('error');
}
function fail(error){
 invalidate();$('interp-output').classList.add('error');$('interp-output').textContent=error.message;
}
for(const id of ['interp-samples','interp-queries','interp-slope-start','interp-slope-end'])$(id).addEventListener('input',invalidate);
$('interp-method').addEventListener('change',()=>{invalidate();$('interp-slopes').hidden=$('interp-method').value!=='clamped';});
$('interp-from-table').addEventListener('click',()=>{
 try{
  const t=M.dataTables.active;
  if(!t||t.columns.length<2)throw Error('Select a Data Table with at least two columns.');
  const rows=M.dataTables.calculate(t).filter(r=>r.some(v=>String(v??'').trim()));
  if(rows.length<2||rows.length>MAX_POINTS)throw Error('Active table must have 2–200 nonblank rows.');
  const pairs=rows.map(r=>[number(r[0],'Table x'),number(r[1],'Table y')]);
  $('interp-samples').value=pairs.map(p=>p.join(',')).join('\n');
  invalidate();$('interp-output').textContent='Loaded '+pairs.length+' sample pairs from '+t.name+'.';
 }catch(e){fail(e);}
});
$('interp-run').addEventListener('click',()=>{
 try{
  const method=$('interp-method').value;
  last=interpolate({points:parsePairs($('interp-samples').value),queries:parseQueries($('interp-queries').value),method,
   endSlopes:method==='clamped'?[$('interp-slope-start').value,$('interp-slope-end').value]:undefined});
  $('interp-output').classList.remove('error');
  const fmt=v=>String(Number(v.toPrecision(12)));
  $('interp-output').textContent=last.method+'\n'+last.rows.length+' query results; domain ['+last.domain.join(', ')+']\n'+
   (last.columns.length>2?'x → y | dy/dx | d2y/dx2 | integral from x0\n':'')+
   last.rows.slice(0,12).map(r=>r[0]+' → '+(r.length>2?r.slice(1).map(fmt).join(' | '):r[1])).join('\n')+
   (last.rows.length>12?'\n… '+(last.rows.length-12)+' more':'')+'\n'+last.note;
  $('interp-to-table').disabled=$('interp-to-graph').disabled=false;
 }catch(e){fail(e);}
});
function exportTable(){
 if(!last)throw Error('Run interpolation first.');
 return M.dataTables.importData({headers:last.columns,rows:last.rows},last.tableName||(last.type==='interpolation-barycentric'?'Interpolation_Barycentric':last.type==='interpolation-pchip'?'Interpolation_PCHIP':'Interpolation_Linear'));
}
$('interp-to-table').addEventListener('click',()=>{try{exportTable();M.advanced.mode('data');}catch(e){fail(e);}});
$('interp-to-graph').addEventListener('click',()=>{
 try{
  const t=exportTable();M.advanced.mode('graph');
  $('dt-graph-table').value=t.id;
  $('dt-graph-table').dispatchEvent(new Event('change',{bubbles:true}));
  $('dt-chart-type').value='line';$('dt-graph-x').value='0';$('dt-graph-y').value='1';
  $('dt-plot-table').click();
 }catch(e){fail(e);}
});
M.interpolationTools={interpolate,parsePairs,parseQueries,methods:METHODS.slice(),splineMethods:Object.keys(SPLINE_METHODS)};
})();