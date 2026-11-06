/* Offline numerical differentiation and vector calculus at a point (Ridders-Richardson
   extrapolation). Expressions are evaluated only by the shared safe numerical evaluator. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');if(!M?.numerical?.evaluate||!M?.dataTables||!panel)return;
const $=id=>document.getElementById(id),NAMES=['x','y','z'],LIMIT=1e8,CON=1.4,CON2=CON*CON,NTAB=12,SAFE=2;
const fmt=v=>Number.isFinite(v)?(Math.abs(v)<5e-15?'0':String(Number(v.toPrecision(12)))):String(v);
const fmtErr=e=>e===0?'0':e.toExponential(1);
function number(value,name){if(value===null||value===undefined||String(value).trim()==='')throw Error(name+' is required.');const n=Number(value);if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(name+' must be finite and at most 1e8 in magnitude.');return n;}
function expression(value,name){const s=String(value??'').trim();if(!s||s.length>1000)throw Error(name+' must be 1–1000 characters.');return s;}
function point(value,minDim=1){
 const raw=Array.isArray(value)?value:String(value??'').split(',');
 if(raw.length<minDim||raw.length>3)throw Error('The point must have '+(minDim===3?'3':minDim+'–3')+' coordinates (x, y, z).');
 return raw.map((v,i)=>number(v,'Coordinate '+NAMES[i]));
}
function components(value){
 const raw=Array.isArray(value)?value:String(value??'').split(';');
 const list=raw.map(s=>String(s).trim());
 if(list.length<2||list.length>3||list.some(s=>!s))throw Error('Enter a vector field with 2 or 3 non-empty components separated by semicolons (P; Q; R).');
 return list.map((s,i)=>expression(s,'Component '+(i+1)));
}
function tolerance(value){if(value===undefined||value===null||value==='')return 1e-6;const t=number(value,'Relative error threshold');if(t<1e-12||t>1e-1)throw Error('Relative error threshold must be between 1e-12 and 0.1.');return t;}
// Scalar function of the point; refuses non-finite values with the offending location.
function scalar(expr,dim,counter){
 return p=>{const env={};for(let i=0;i<dim;i++)env[NAMES[i]]=p[i];counter.n++;
  let v;try{v=M.numerical.evaluate(expr,env);}catch(err){throw Error('Evaluation failed at ('+p.map(fmt).join(', ')+'): '+err.message);}
  if(!Number.isFinite(v))throw Error('Non-finite value at ('+p.map(fmt).join(', ')+').');return v;};
}
// Ridders' polynomial extrapolation of stencil(h) to h→0 (even-power error series).
function ridders(stencil,h0,label){
 let h=h0,first,tries=0;
 for(;;){try{first=stencil(h);break;}catch(err){if(++tries>8)throw Error(label+': '+err.message);h/=4;}}
 const a=[[first]];let best=first,err=Infinity;
 for(let i=1;i<NTAB;i++){
  h/=CON;let next;try{next=stencil(h);}catch(e){if(err<Infinity)break;throw Error(label+': '+e.message);}
  a[i]=[next];let fac=CON2;
  for(let j=1;j<=i;j++){a[i][j]=(a[i][j-1]*fac-a[i-1][j-1])/(fac-1);fac*=CON2;
   const e=Math.max(Math.abs(a[i][j]-a[i][j-1]),Math.abs(a[i][j]-a[i-1][j-1]));
   if(e<=err){err=e;best=a[i][j];}}
  if(Math.abs(a[i][i]-a[i-1][i-1])>=SAFE*err)break;
 }
 if(!Number.isFinite(best)||!Number.isFinite(err))throw Error(label+': the difference quotients are not finite.');
 return {value:best,error:err};
}
const STENCILS={
 1:(g,h)=>(g(h)-g(-h))/(2*h),
 2:(g,h,g0)=>(g(h)-2*g0+g(-h))/(h*h),
 3:(g,h)=>(g(2*h)-2*g(h)+2*g(-h)-g(-2*h))/(2*h*h*h),
 4:(g,h,g0)=>(g(2*h)-4*g(h)+6*g0-4*g(-h)+g(-2*h))/(h*h*h*h)
};
const H0={1:0.1,2:0.2,3:0.3,4:0.4};
const scaleOf=v=>Math.max(1,Math.abs(v));
function shifted(p,i,t){const q=p.slice();q[i]+=t;return q;}
// Oscillatory or rapidly varying functions may need a smaller starting step: retry twice, keep the best estimate.
function refined(stencil,h0,label,threshold){
 let best=null;
 for(const shrink of [1,1e-2,1e-4]){
  const r=ridders(stencil,h0*shrink,label);
  if(!best||r.error<best.error)best=r;
  if(best.error<=threshold*Math.max(1,Math.abs(best.value)))break;
 }
 return best;
}
function partial(f,p,i,order,f0,label,threshold){
 const s=scaleOf(p[i]),g=t=>f(shifted(p,i,t));
 return refined(h=>STENCILS[order](g,h*s,f0),H0[order],label,threshold);
}
function mixed(f,p,i,j,label,threshold){
 const si=scaleOf(p[i]),sj=scaleOf(p[j]);
 const at=(a,b)=>{const q=p.slice();q[i]+=a;q[j]+=b;return f(q);};
 return refined(h=>{const a=h*si,b=h*sj;return (at(a,b)-at(a,-b)-at(-a,b)+at(-a,-b))/(4*a*b);},0.1,label,threshold);
}
// One-sided slope comparison: smooth functions close the gap ~h, kinks and jumps do not.
function smoothness(f,p,i,f0,label){
 let h=1e-3*scaleOf(p[i]);
 for(let k=0;k<4;k++,h/=10){
  try{
   const fp1=f(shifted(p,i,h)),fm1=f(shifted(p,i,-h)),fp2=f(shifted(p,i,h/10)),fm2=f(shifted(p,i,-h/10));
   const d1p=(fp1-f0)/h,d1m=(f0-fm1)/h,d2p=(fp2-f0)/(h/10),d2m=(f0-fm2)/(h/10);
   const gap1=Math.abs(d1p-d1m),gap2=Math.abs(d2p-d2m);
   const noise=1e3*Number.EPSILON*Math.max(Math.abs(f0),Math.abs(fp2),Math.abs(fm2),1e-300)/(h/10);
   if(gap2>1e-6*Math.max(1,Math.abs(d2p),Math.abs(d2m))+noise&&gap2>0.3*gap1)
    throw Error('Suspected non-differentiable point in '+NAMES[i]+' ('+label+'): one-sided slopes '+fmt(d2m)+' and '+fmt(d2p)+' do not converge (kink, cusp or jump). No derivative is reported (heuristic check).');
   return;
  }catch(err){if(/non-differentiable/.test(err.message)||k===3)throw err.message.startsWith('Suspected')?err:Error(label+': '+err.message+' The point may be on or next to a domain boundary.');}
 }
}
function check(entry,threshold,label){
 if(entry.error>threshold*Math.max(1,Math.abs(entry.value)))
  throw Error(label+': estimated error '+fmtErr(entry.error)+' exceeds the threshold '+fmtErr(threshold*Math.max(1,Math.abs(entry.value)))+'. The point is likely non-differentiable, discontinuous or badly scaled; no result is reported.');
 return entry;
}
function prepare(expr,p,counter,label,threshold){
 const f=scalar(expr,p.length,counter),f0=f(p);
 for(let i=0;i<p.length;i++)smoothness(f,p,i,f0,label);
 return {f,f0};
}
function gradientOf(expr,p,counter,threshold,label='f'){
 const {f,f0}=prepare(expr,p,counter,label,threshold);
 return {f0,entries:p.map((_,i)=>check(partial(f,p,i,1,f0,'∂'+label+'/∂'+NAMES[i],threshold),threshold,'∂'+label+'/∂'+NAMES[i]))};
}
function result(type,payload,counter,extra){
 return Object.assign({type,method:'Central differences with Ridders–Richardson extrapolation (step scaled to max(1,|coordinate|))',evaluations:counter.n,
  note:'Error estimates come from the extrapolation tableau and are heuristic, not certified bounds. Smoothness is screened by one-sided first-derivative slopes only; higher-order non-smoothness can escape central stencils. Thresholds relax by 10× per derivative order.'},payload,extra||{});
}
function derivative({expression:e='sin(x)',x=1,order=1,tolerance:t}={}){
 const expr=expression(e,'Expression'),x0=number(x,'Point x'),n=Number(order),thr=tolerance(t),counter={n:0};
 if(!Number.isInteger(n)||n<1||n>4)throw Error('Derivative order must be an integer from 1 to 4.');
 const label='d'+(n>1?'^'+n:'')+'f/dx'+(n>1?'^'+n:'');
 const {f,f0}=prepare(expr,[x0],counter,'f',thr);
 const limit=thr*Math.pow(10,n-1),entry=check(partial(f,[x0],0,n,f0,label,limit),limit,label);
 return result('derivative',{order:n,point:[x0],value:entry.value,error:entry.error,f:f0,rows:[[label,entry.value,entry.error]]},counter);
}
function gradient({expression:e='x^2*y+z^3',point:pt=[1,2,3],tolerance:t}={}){
 const expr=expression(e,'Expression'),p=point(pt),thr=tolerance(t),counter={n:0};
 const g=gradientOf(expr,p,counter,thr);
 return result('gradient',{point:p,f:g.f0,values:g.entries.map(v=>v.value),errors:g.entries.map(v=>v.error),
  rows:g.entries.map((v,i)=>['∂f/∂'+NAMES[i],v.value,v.error])},counter);
}
function hessianOf(expr,p,counter,thr,diagonalOnly){
 const {f,f0}=prepare(expr,p,counter,'f',thr),n=p.length,V=[],E=[];
 for(let i=0;i<n;i++){V[i]=Array(n).fill(0);E[i]=Array(n).fill(0);}
 for(let i=0;i<n;i++){const lab='∂²f/∂'+NAMES[i]+'²',d=check(partial(f,p,i,2,f0,lab,thr*10),thr*10,lab);V[i][i]=d.value;E[i][i]=d.error;}
 if(!diagonalOnly)for(let i=0;i<n;i++)for(let j=i+1;j<n;j++){const lab='∂²f/∂'+NAMES[i]+'∂'+NAMES[j],d=check(mixed(f,p,i,j,lab,thr*10),thr*10,lab);V[i][j]=V[j][i]=d.value;E[i][j]=E[j][i]=d.error;}
 return {f0,V,E};
}
function hessian({expression:e='x^2*y',point:pt=[1,2],tolerance:t}={}){
 const expr=expression(e,'Expression'),p=point(pt),thr=tolerance(t),counter={n:0},h=hessianOf(expr,p,counter,thr,false),rows=[];
 h.V.forEach((r,i)=>r.forEach((v,j)=>rows.push(['H['+(i+1)+','+(j+1)+'] ∂²f/∂'+NAMES[i]+'∂'+NAMES[j],v,h.E[i][j]])));
 return result('hessian',{point:p,f:h.f0,matrix:h.V,errors:h.E,symmetric:true,rows},counter);
}
function laplacian({expression:e='x^2+y^2+z^2',point:pt=[1,1,1],tolerance:t}={}){
 const expr=expression(e,'Expression'),p=point(pt),thr=tolerance(t),counter={n:0},h=hessianOf(expr,p,counter,thr,true);
 const value=h.V.reduce((s,r,i)=>s+r[i],0),error=h.E.reduce((s,r,i)=>s+r[i],0);
 return result('laplacian',{point:p,f:h.f0,value,error,rows:[['∇²f',value,error]].concat(p.map((_,i)=>['∂²f/∂'+NAMES[i]+'²',h.V[i][i],h.E[i][i]]))},counter);
}
function jacobianOf(field,p,counter,thr){
 const comps=components(field),V=[],E=[];
 comps.forEach((c,r)=>{const g=gradientOf(c,p,counter,thr,'F'+(r+1));V[r]=g.entries.map(v=>v.value);E[r]=g.entries.map(v=>v.error);});
 return {comps,V,E};
}
function jacobian({field='x*y; x+y',point:pt=[1,2],tolerance:t}={}){
 const p=point(pt),thr=tolerance(t),counter={n:0},J=jacobianOf(field,p,counter,thr),rows=[];
 J.V.forEach((r,i)=>r.forEach((v,j)=>rows.push(['J['+(i+1)+','+(j+1)+'] ∂F'+(i+1)+'/∂'+NAMES[j],v,J.E[i][j]])));
 return result('jacobian',{point:p,matrix:J.V,errors:J.E,rows},counter);
}
function divergence({field='x; y; z',point:pt=[1,2,3],tolerance:t}={}){
 const p=point(pt,2),thr=tolerance(t),comps=components(field);
 if(comps.length!==p.length)throw Error('Divergence needs as many field components ('+comps.length+') as point coordinates ('+p.length+').');
 const counter={n:0},J=jacobianOf(comps,p,counter,thr),value=J.V.reduce((s,r,i)=>s+r[i],0),error=J.E.reduce((s,r,i)=>s+r[i],0);
 return result('divergence',{point:p,value,error,rows:[['∇·F',value,error]]},counter);
}
function curl({field='-y; x; 0',point:pt=[1,2,3],tolerance:t}={}){
 const p=point(pt,2),thr=tolerance(t),comps=components(field);
 if(comps.length!==p.length)throw Error('Curl needs 2 components at a 2D point (scalar curl) or 3 components at a 3D point.');
 const counter={n:0},J=jacobianOf(comps,p,counter,thr),V=J.V,E=J.E;
 if(p.length===2){const value=V[1][0]-V[0][1],error=E[1][0]+E[0][1];
  return result('curl',{point:p,scalar:true,value,error,rows:[['∂Q/∂x − ∂P/∂y',value,error]]},counter);}
 const values=[V[2][1]-V[1][2],V[0][2]-V[2][0],V[1][0]-V[0][1]],errors=[E[2][1]+E[1][2],E[0][2]+E[2][0],E[1][0]+E[0][1]];
 return result('curl',{point:p,scalar:false,values,errors,rows:['(∇×F)x','(∇×F)y','(∇×F)z'].map((l,i)=>[l,values[i],errors[i]])},counter);
}
function directional({expression:e='x^2*y+z^3',point:pt=[1,2,3],direction=[1,1,1],tolerance:t}={}){
 const expr=expression(e,'Expression'),p=point(pt),thr=tolerance(t);
 const raw=Array.isArray(direction)?direction:String(direction??'').split(',');
 if(raw.length!==p.length)throw Error('The direction must have '+p.length+' components to match the point.');
 const u=raw.map((v,i)=>number(v,'Direction component '+(i+1))),len=Math.hypot(...u);
 if(!(len>0))throw Error('The direction vector must be non-zero.');
 const unit=u.map(v=>v/len),counter={n:0},g=gradientOf(expr,p,counter,thr);
 const value=g.entries.reduce((s,v,i)=>s+v.value*unit[i],0),error=g.entries.reduce((s,v,i)=>s+v.error*Math.abs(unit[i]),0);
 return result('directional',{point:p,unit,value,error,gradient:g.entries.map(v=>v.value),rows:[['D_u f',value,error]].concat(g.entries.map((v,i)=>['∂f/∂'+NAMES[i],v.value,v.error]))},counter);
}
const OPS={derivative,gradient,hessian,jacobian,divergence,curl,laplacian,directional};
function compute(op,options){const fn=OPS[op];if(!fn)throw Error('Unknown operation: '+op+'.');return fn(options||{});}
function matrixText(V,E){
 const cells=V.map((r,i)=>r.map((v,j)=>fmt(v)+' ± '+fmtErr(E[i][j]))),w=Math.max(...cells.flat().map(s=>s.length));
 return cells.map(r=>'[ '+r.map(s=>s.padStart(w)).join('   ')+' ]').join('\n');
}
function describe(r){
 const at='at ('+r.point.map(fmt).join(', ')+')',lines=[];
 if(r.type==='derivative')lines.push('Derivative of order '+r.order+' '+at,'Value = '+fmt(r.value)+' ± '+fmtErr(r.error));
 else if(r.type==='gradient')lines.push('Gradient ∇f '+at,'('+r.values.map(fmt).join(', ')+')',...r.rows.map(x=>x[0]+' = '+fmt(x[1])+' ± '+fmtErr(x[2])));
 else if(r.type==='hessian')lines.push('Hessian (symmetric) '+at,matrixText(r.matrix,r.errors));
 else if(r.type==='jacobian')lines.push('Jacobian ('+r.matrix.length+'×'+r.point.length+') '+at,matrixText(r.matrix,r.errors));
 else if(r.type==='curl'&&!r.scalar)lines.push('Curl ∇×F '+at,'('+r.values.map(fmt).join(', ')+')',...r.rows.map(x=>x[0]+' = '+fmt(x[1])+' ± '+fmtErr(x[2])));
 else {const name={divergence:'Divergence ∇·F',curl:'Scalar curl ∂Q/∂x − ∂P/∂y',laplacian:'Laplacian ∇²f',directional:'Directional derivative D_u f'}[r.type];
  lines.push(name+' '+at,'Value = '+fmt(r.value)+' ± '+fmtErr(r.error));
  if(r.unit)lines.push('Unit direction u = ('+r.unit.map(fmt).join(', ')+')');}
 lines.push('Evaluations: '+r.evaluations,r.method,r.note);return lines.join('\n');
}
const area=document.createElement('details');area.id='vectorcalc-details';
area.innerHTML='<summary>Numerical derivatives and vector calculus · Ridders extrapolation</summary>'+
 '<p class="graph-data-muted">Derivatives, gradient, Hessian, Jacobian, divergence, curl, Laplacian and directional derivatives at a point. Variables x, y, z; vector fields as P; Q; R.</p>'+
 '<div class="num-fields"><label>Operation<select id="vc-op"><option value="derivative">Derivative dⁿf/dxⁿ (n = 1–4)</option><option value="gradient">Gradient ∇f</option><option value="hessian">Hessian matrix</option><option value="jacobian">Jacobian of vector field</option><option value="divergence">Divergence ∇·F</option><option value="curl">Curl ∇×F (3D) / scalar curl (2D)</option><option value="laplacian">Laplacian ∇²f</option><option value="directional">Directional derivative</option></select></label>'+
 '<label id="vc-expression-label">Scalar f(x, y, z)<input id="vc-expression" value="sin(x)" spellcheck="false"></label>'+
 '<label id="vc-field-label" hidden>Vector field P; Q; R<input id="vc-field" value="-y; x; 0" spellcheck="false"></label>'+
 '<label id="vc-order-label">Order n<select id="vc-order"><option>1</option><option>2</option><option>3</option><option>4</option></select></label>'+
 '<label id="vc-dim-label" hidden>Dimension<select id="vc-dim"><option value="2">2 (x, y)</option><option value="3" selected>3 (x, y, z)</option></select></label>'+
 '<label>Point x<input id="vc-x" type="number" step="any" value="1"></label>'+
 '<label id="vc-y-label" hidden>Point y<input id="vc-y" type="number" step="any" value="2"></label>'+
 '<label id="vc-z-label" hidden>Point z<input id="vc-z" type="number" step="any" value="3"></label>'+
 '<label id="vc-direction-label" hidden>Direction (comma-separated)<input id="vc-direction" value="1, 1, 1" spellcheck="false"></label>'+
 '<label>Relative error threshold<input id="vc-tolerance" type="number" step="any" value="0.000001"></label></div>'+
 '<div class="data-toolbar"><button id="vc-run" class="primary" type="button">Compute</button>'+
 '<button id="vc-to-table" class="secondary" type="button" disabled>Save to Data Tables</button></div>'+
 '<pre id="vc-output" role="status" aria-live="polite">Choose an operation, enter the expression and point, then Compute.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#vectorcalc-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px;max-width:100%;box-sizing:border-box}'+
 '#vectorcalc-details summary{cursor:pointer;color:#3c50ae;font-weight:750;min-height:40px;display:flex;align-items:center}'+
 '#vectorcalc-details .num-fields{min-width:0}#vectorcalc-details label{min-width:0}#vectorcalc-details label[hidden]{display:none!important}'+
 '#vc-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px;max-width:100%;box-sizing:border-box}'+
 '#vc-output.error{color:#a82241;background:#fff2f4}'+
 '#vectorcalc-details button,#vectorcalc-details input,#vectorcalc-details select{min-height:40px}'+
 '@media(max-width:480px){#vectorcalc-details .num-fields{grid-template-columns:1fr}}';
document.head.append(style);
let last=null;const output=$('vc-output'),toTable=$('vc-to-table');
const FIELD_OPS=new Set(['jacobian','divergence','curl']);
function sync(){
 const op=$('vc-op').value,field=FIELD_OPS.has(op),dim=op==='derivative'?1:Number($('vc-dim').value);
 $('vc-expression-label').hidden=field;$('vc-field-label').hidden=!field;$('vc-order-label').hidden=op!=='derivative';
 $('vc-dim-label').hidden=op==='derivative';$('vc-y-label').hidden=dim<2;$('vc-z-label').hidden=dim<3;$('vc-direction-label').hidden=op!=='directional';
}
function invalidate(){last=null;toTable.disabled=true;output.classList.remove('error');}
for(const el of area.querySelectorAll('input,select')){el.addEventListener('input',invalidate);el.addEventListener('change',()=>{invalidate();sync();});}
$('vc-run').addEventListener('click',()=>{
 try{
  const op=$('vc-op').value,dim=op==='derivative'?1:Number($('vc-dim').value),p=[$('vc-x').value,$('vc-y').value,$('vc-z').value].slice(0,dim);
  const opts={expression:$('vc-expression').value,field:$('vc-field').value,point:p,tolerance:$('vc-tolerance').value,direction:$('vc-direction').value};
  if(op==='derivative'){opts.x=p[0];opts.order=$('vc-order').value;}
  last=compute(op,opts);output.classList.remove('error');output.textContent=describe(last);toTable.disabled=false;
 }catch(err){invalidate();output.classList.add('error');output.textContent=err.message+'\nAdjust the expression, point or threshold and compute again.';}
});
toTable.addEventListener('click',()=>{try{if(!last)throw Error('Compute a result first.');
 M.dataTables.importData({headers:['quantity','value','estimated_error'],rows:last.rows.map(r=>[r[0],r[1],r[2]])},'VectorCalculus_'+last.type);M.advanced.mode('data');}catch(err){output.classList.add('error');output.textContent=err.message;}});
sync();
M.vectorCalculus={derivative,gradient,hessian,jacobian,divergence,curl,laplacian,directional,compute};
})();
