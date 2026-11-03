/* ProMathStudio: bounded offline double/triple integrals (nested adaptive Gauss-Kronrod G7-K15) and discrete-data integration. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');
if(!M?.numerical?.evaluate||!M?.dataTables||!panel)return;
const $=id=>document.getElementById(id);
const LIMIT=1e12,MAX_SUBINTERVALS=200,MAX_POINTS=6000;
const NOTE='Estimated error is a heuristic Gauss-Kronrod difference, not a certified bound; singularities, discontinuities or oscillations between nodes may be missed.';
function number(value,label){
 if(value===null||value===undefined||String(value).trim()==='')throw Error(label+' is required.');
 const n=Number(value);
 if(!Number.isFinite(n)||Math.abs(n)>LIMIT)throw Error(label+' must be finite with magnitude at most 1e12.');
 return n;
}
function expression(text,label){
 text=String(text??'').trim();
 if(!text||text.length>1000)throw Error(label+' must contain 1–1000 characters.');
 return text;
}
function settings(tolerance,maxEvaluations){
 tolerance=number(tolerance,'Tolerance');
 if(tolerance<1e-12||tolerance>1e-2)throw Error('Tolerance must be between 1e-12 and 0.01.');
 maxEvaluations=number(maxEvaluations,'Maximum evaluations');
 if(!Number.isInteger(maxEvaluations)||maxEvaluations<1000||maxEvaluations>500000)throw Error('Maximum evaluations must be an integer from 1000 to 500000.');
 return {tolerance,maxEvaluations};
}
function interval(a,b,lo,hi){
 a=number(a,lo);b=number(b,hi);
 if(!(b>a))throw Error(hi+' must exceed '+lo.toLowerCase()+'.');
 return [a,b];
}
// Gauss-Kronrod 7-15 nodes (positive half) and weights.
const XK=[0.991455371120812639206854697526329,0.949107912342758524526189684047851,0.864864423359769072789712788640926,0.741531185599394439863864773280788,0.586087235467691130294144845693013,0.405845151377397166906606412076961,0.207784955007898467600689403773245,0];
const WK=[0.022935322010529224963732008058970,0.063092092629978553290700663189204,0.104790010322250183839876322541518,0.140653259715525918745189590510238,0.169004726639267902826583426598550,0.190350578064785409913256402421014,0.204432940075298892414161999234649,0.209482141084727828012999174891714];
const WG=[0.129484966168869693270611432679082,0.279705391489276667901467771423780,0.381830050505118944950369775488975,0.417959183673469387755102040816327];
function gk15(f,a,b){
 const c=(a+b)/2,h=(b-a)/2;let k=0,g=0,side=0;
 for(let i=0;i<8;i++){
  const pts=i===7?[c]:[c-h*XK[i],c+h*XK[i]];
  for(const x of pts){
   const [v,e]=f(x);k+=WK[i]*v;side+=WK[i]*e;
   if(i%2===1)g+=WG[(i-1)/2]*v;else if(i===7)g+=WG[3]*v;
  }
 }
 return {value:k*h,error:Math.abs((k-g)*h),side:Math.abs(side*h)};
}
// Global adaptive GK15 on [a,b]; f returns [value, inner error estimate]. Throws if the target cannot be met.
function adaptive(f,a,b,tol,state){
 const first={a,b,...gk15(f,a,b)},list=[first];
 const sum=key=>list.reduce((s,p)=>s+p[key],0);
 for(;;){
  const value=sum('value'),error=sum('error');
  if(!Number.isFinite(value)||!Number.isFinite(error))throw Error('Non-finite integral estimate; the integrand may be singular or overflow in the domain.');
  if(error<=Math.max(tol,tol*Math.abs(value)))return {value,error,side:sum('side'),panels:list.length};
  if(list.length>=MAX_SUBINTERVALS)throw Error('Tolerance could not be met within '+MAX_SUBINTERVALS+' subintervals per level; the integrand may be singular, discontinuous or too oscillatory. Relax the tolerance.');
  let worst=0;for(let i=1;i<list.length;i++)if(list[i].error>list[worst].error)worst=i;
  const p=list[worst],m=(p.a+p.b)/2;
  if(!(m>p.a&&m<p.b))throw Error('Subinterval width reached machine precision; suspected singularity.');
  list.splice(worst,1,{a:p.a,b:m,...gk15(f,p.a,m)},{a:m,b:p.b,...gk15(f,m,p.b)});
  state.subdivisions++;
 }
}
function counter(expr,maxEvaluations,state){
 return env=>{
  if(++state.evaluations>maxEvaluations)throw Error('Evaluation budget of '+maxEvaluations+' exceeded; relax the tolerance or raise the budget.');
  let v;
  try{v=M.numerical.evaluate(expr,env);}
  catch(err){throw Error('Integrand is not finite and real at '+Object.entries(env).map(([k,x])=>k+'='+(+x.toPrecision(8))).join(', ')+' (possible singularity): '+err.message);}
  if(!Number.isFinite(v)||Math.abs(v)>1e150)throw Error('Integrand is not finite at '+JSON.stringify(env)+'.');
  return v;
 };
}
function limitAt(expr,x,label){
 let v;try{v=M.numerical.evaluate(expr,{x});}catch(err){throw Error(label+' is not finite and real at x='+(+x.toPrecision(8))+': '+err.message);}
 if(!Number.isFinite(v)||Math.abs(v)>LIMIT)throw Error(label+' must be finite at x='+x+'.');
 return v;
}
function double({expression:f='x*y',a=0,b=1,lower='0',upper='1',tolerance=1e-8,maxEvaluations=200000}={}){
 f=expression(f,'Integrand f(x,y)');lower=expression(lower,'Inner lower limit g1(x)');upper=expression(upper,'Inner upper limit g2(x)');
 [a,b]=interval(a,b,'Outer lower limit a','Outer upper limit b');
 ({tolerance,maxEvaluations}=settings(tolerance,maxEvaluations));
 const state={evaluations:0,subdivisions:0},fx=counter(f,maxEvaluations,state);
 const innerTol=Math.max(1e-15,tolerance/(4*(b-a)));
 const outer=adaptive(x=>{
  const g1=limitAt(lower,x,'Inner lower limit g1(x)'),g2=limitAt(upper,x,'Inner upper limit g2(x)');
  if(g1===g2)return [0,0];
  const lo=Math.min(g1,g2),hi=Math.max(g1,g2),sign=g2>g1?1:-1;
  const r=adaptive(y=>[fx({x,y}),0],lo,hi,innerTol,state);
  return [sign*r.value,r.error];
 },a,b,tolerance/2,state);
 return {type:'integral-double',value:outer.value,estimatedError:outer.error+outer.side,evaluations:state.evaluations,subdivisions:state.subdivisions,
  tolerance,method:'Nested adaptive Gauss-Kronrod G7-K15 (dy inner, dx outer)',
  region:'x∈['+a+', '+b+'], y∈['+lower+', '+upper+']',note:NOTE};
}
function triple({expression:f='x*y*z',a=0,b=1,c=0,d=1,e=0,g=1,tolerance=1e-8,maxEvaluations=200000}={}){
 f=expression(f,'Integrand f(x,y,z)');
 [a,b]=interval(a,b,'x lower limit','x upper limit');[c,d]=interval(c,d,'y lower limit','y upper limit');[e,g]=interval(e,g,'z lower limit','z upper limit');
 ({tolerance,maxEvaluations}=settings(tolerance,maxEvaluations));
 const state={evaluations:0,subdivisions:0},fx=counter(f,maxEvaluations,state);
 const yTol=Math.max(1e-15,tolerance/(4*(b-a))),zTol=Math.max(1e-15,yTol/(4*(d-c)));
 const outer=adaptive(x=>{
  const mid=adaptive(y=>{const r=adaptive(z=>[fx({x,y,z}),0],e,g,zTol,state);return [r.value,r.error];},c,d,yTol,state);
  return [mid.value,mid.error+mid.side];
 },a,b,tolerance/2,state);
 return {type:'integral-triple',value:outer.value,estimatedError:outer.error+outer.side,evaluations:state.evaluations,subdivisions:state.subdivisions,
  tolerance,method:'Nested adaptive Gauss-Kronrod G7-K15 over a box (dz, dy, dx)',
  region:'['+a+', '+b+']×['+c+', '+d+']×['+e+', '+g+']',note:NOTE};
}
// Discrete-data integration: x strictly ascending, finite y; blanks are skipped and reported.
function discrete({x=[],y=[]}={}){
 if(!Array.isArray(x)||!Array.isArray(y)||x.length!==y.length)throw Error('X and Y columns must have the same length.');
 const xs=[],ys=[];let ignored=0;
 for(let i=0;i<x.length;i++){
  const bx=String(x[i]??'').trim()==='',by=String(y[i]??'').trim()==='';
  if(bx||by){ignored++;continue;}
  xs.push(number(x[i],'X row '+(i+1)));ys.push(number(y[i],'Y row '+(i+1)));
 }
 if(xs.length<2)throw Error('At least two numeric (x, y) points are required.');
 if(xs.length>MAX_POINTS)throw Error('At most '+MAX_POINTS+' points are supported.');
 for(let i=1;i<xs.length;i++)if(!(xs[i]>xs[i-1]))throw Error('X must be strictly ascending (row '+(i+1)+' of the numeric data is not greater than the previous value).');
 const cumulative=[0];let trapezoid=0;
 for(let i=1;i<xs.length;i++){trapezoid+=(xs[i]-xs[i-1])*(ys[i]+ys[i-1])/2;cumulative.push(trapezoid);}
 if(!Number.isFinite(trapezoid))throw Error('Trapezoid sum overflowed.');
 const n=xs.length-1,h=(xs[n]-xs[0])/n;
 const uniform=xs.every((v,i)=>i===0||Math.abs((v-xs[i-1])-h)<=1e-9*Math.max(Math.abs(h),Math.abs(v)));
 let simpson=null,simpsonNote;
 if(!uniform)simpsonNote='Simpson not applied: X spacing is non-uniform; use the trapezoid value.';
 else if(n%2)simpsonNote='Simpson not applied: an odd number of intervals ('+n+'); use the trapezoid value.';
 else{let s=ys[0]+ys[n];for(let i=1;i<n;i++)s+=(i%2?4:2)*ys[i];simpson=s*h/3;simpsonNote='Composite Simpson 1/3 rule on '+n+' uniform intervals (exact for cubics).';}
 return {type:'integral-discrete',trapezoid,simpson,uniform,points:xs.length,ignored,simpsonNote,
  columns:['x','y','cumulative_trapezoid'],rows:xs.map((v,i)=>[v,ys[i],cumulative[i]]),
  method:'Composite trapezoid (non-uniform allowed); Simpson when uniform with even intervals',
  note:'Accuracy depends on sampling density; no error bound is available from samples alone.'};
}
function discreteFromTable({table,xColumn=0,yColumn=1}={}){
 const list=M.dataTables.tables,t=table===undefined||table===null||table===''?M.dataTables.active:list.find(s=>s.id===table||s.name===table);
 if(!t)throw Error('Select an existing Data Table.');
 const xc=Number(xColumn),yc=Number(yColumn);
 if(!Number.isInteger(xc)||!Number.isInteger(yc)||xc<0||yc<0||xc>=t.columns.length||yc>=t.columns.length)throw Error('Choose valid X and Y columns.');
 if(xc===yc)throw Error('X and Y must be different columns.');
 const rows=M.dataTables.calculate(t);
 const r=discrete({x:rows.map(row=>row[xc]),y:rows.map(row=>row[yc])});
 r.table=t.name;r.columns=[String(t.columns[xc]),String(t.columns[yc]),'cumulative_trapezoid'];return r;
}
const area=document.createElement('details');area.id='integration-details';
const field=(id,label,value,type='text')=>'<label>'+label+'<input id="'+id+'" type="'+type+'"'+(type==='number'?' step="any"':'')+' value="'+value+'"></label>';
area.innerHTML='<summary>Multiple and discrete integrals</summary>'+
 '<p class="graph-data-muted">Double integral ∫ₐᵇ∫_{g1(x)}^{g2(x)} f dy dx, triple integral over a box, or trapezoid/Simpson integration of two Data Table columns.</p>'+
 '<div class="data-toolbar"><label>Integral type<select id="int-mode"><option value="double">Double ∫∫ f(x,y) dy dx</option><option value="triple">Triple ∫∫∫ f(x,y,z) over a box</option><option value="discrete">Discrete data (table columns)</option></select></label></div>'+
 '<div class="num-fields" id="int-continuous">'+field('int-expression','Integrand f','x*y')+
 field('int-a','x lower a','0','number')+field('int-b','x upper b','1','number')+
 '<span class="int-double">'+field('int-g1','y lower g1(x)','0')+'</span><span class="int-double">'+field('int-g2','y upper g2(x)','1')+'</span>'+
 '<span class="int-triple" hidden>'+field('int-c','y lower c','0','number')+'</span><span class="int-triple" hidden>'+field('int-d','y upper d','1','number')+'</span>'+
 '<span class="int-triple" hidden>'+field('int-e','z lower e','0','number')+'</span><span class="int-triple" hidden>'+field('int-f','z upper f','1','number')+'</span>'+
 field('int-tolerance','Tolerance','0.00000001','number')+field('int-budget','Maximum evaluations','200000','number')+'</div>'+
 '<div class="num-fields" id="int-discrete" hidden><label>Data Table<select id="int-table"></select></label><label>X column (ascending)<select id="int-x"></select></label><label>Y column<select id="int-y"></select></label></div>'+
 '<div class="data-toolbar"><button id="int-run" class="primary" type="button">Integrate</button>'+
 '<button id="int-refresh" class="secondary" type="button" hidden>Refresh tables</button>'+
 '<button id="int-to-table" class="secondary" type="button" disabled>Save cumulative to Data Tables</button></div>'+
 '<pre id="int-output" role="status" aria-live="polite">Choose an integral type and press Integrate.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#integration-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px}'+
 '#integration-details summary{cursor:pointer;color:#3c50ae;font-weight:750;min-height:40px;display:flex;align-items:center}'+
 '#integration-details span[hidden],#integration-details [hidden]{display:none!important}'+
 '#integration-details .num-fields span{display:contents}'+
 '#integration-details .data-toolbar select{max-width:100%}'+
 '#int-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px;font:12px/1.6 Consolas,monospace;max-width:100%;box-sizing:border-box}'+
 '#int-output.error{color:#a82241;background:#fff2f4}';
document.head.append(style);
let last=null;
const out=$('int-output');
function invalidate(){last=null;$('int-to-table').disabled=true;out.classList.remove('error');}
function fail(err){invalidate();out.classList.add('error');out.textContent=err.message+'\nAdjust the inputs and press Integrate again.';}
function option(select,value,text){const o=document.createElement('option');o.value=value;o.textContent=text;select.append(o);}
function fillColumns(){
 const t=M.dataTables.tables.find(s=>s.id===$('int-table').value);
 for(const id of ['int-x','int-y']){const s=$(id);s.replaceChildren();if(t)t.columns.forEach((c,i)=>option(s,String(i),String(c)));}
 if(t&&t.columns.length>1)$('int-y').value='1';
}
function fillTables(){
 const s=$('int-table'),prev=s.value;s.replaceChildren();
 for(const t of M.dataTables.tables)option(s,t.id,t.name);
 if([...s.options].some(o=>o.value===prev))s.value=prev;else if(M.dataTables.active)s.value=M.dataTables.active.id;
 fillColumns();
}
function mode(){
 const m=$('int-mode').value;
 $('int-continuous').hidden=m==='discrete';$('int-discrete').hidden=m!=='discrete';$('int-refresh').hidden=m!=='discrete';
 for(const e of area.querySelectorAll('.int-double'))e.hidden=m!=='double';
 for(const e of area.querySelectorAll('.int-triple'))e.hidden=m!=='triple';
 if(m==='discrete')fillTables();
 invalidate();out.textContent=m==='discrete'?'Choose a table and two numeric columns.':'Enter limits and press Integrate.';
}
$('int-mode').addEventListener('change',mode);
$('int-table').addEventListener('change',()=>{fillColumns();invalidate();});
$('int-refresh').addEventListener('click',()=>{fillTables();invalidate();out.textContent='Table list refreshed.';});
for(const el of area.querySelectorAll('input,#int-x,#int-y'))el.addEventListener('input',invalidate);
const fmt=v=>Number.isFinite(v)?(+v.toPrecision(12)).toString():String(v);
$('int-run').addEventListener('click',()=>{
 try{
  const m=$('int-mode').value,v=id=>$(id).value;
  if(m==='discrete'){
   const r=discreteFromTable({table:v('int-table'),xColumn:v('int-x'),yColumn:v('int-y')});
   out.classList.remove('error');
   out.textContent=r.method+'\nTable '+r.table+': '+r.points+' points'+(r.ignored?'; '+r.ignored+' blank row(s) ignored':'')+
    '\nTrapezoid: '+fmt(r.trapezoid)+'\nSimpson: '+(r.simpson===null?'n/a':fmt(r.simpson))+'\n'+r.simpsonNote+'\n'+r.note;
   last=r;$('int-to-table').disabled=false;return;
  }
  const common={expression:v('int-expression'),a:v('int-a'),b:v('int-b'),tolerance:v('int-tolerance'),maxEvaluations:v('int-budget')};
  const r=m==='triple'?triple({...common,c:v('int-c'),d:v('int-d'),e:v('int-e'),g:v('int-f')}):double({...common,lower:v('int-g1'),upper:v('int-g2')});
  invalidate();
  out.textContent=r.method+'\nRegion: '+r.region+'\nIntegral ≈ '+fmt(r.value)+'\nEstimated error: '+r.estimatedError.toExponential(2)+
   '\nEvaluations: '+r.evaluations+'; subdivisions: '+r.subdivisions+'\n'+r.note;
 }catch(err){fail(err);}
});
$('int-to-table').addEventListener('click',()=>{
 try{if(!last)throw Error('Run a discrete integration first.');M.dataTables.importData({headers:last.columns,rows:last.rows.map(r=>r.map(String))},'Integration_Cumulative');M.advanced?.mode?.('data');}
 catch(err){fail(err);}
});
M.integration={double,triple,discrete,discreteFromTable,gk15:f=>(a,b)=>gk15(x=>[f(x),0],a,b)};
})();
