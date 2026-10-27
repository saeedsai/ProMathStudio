/* ProMathStudio: bounded offline one-dimensional linear and PCHIP interpolation. */
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
function interpolate({points,queries,method='linear'}={}){
 if(method!=='linear'&&method!=='pchip')throw Error('Interpolation method must be linear or pchip.');
 if(!Array.isArray(points)||points.length<2||points.length>MAX_POINTS)throw Error('Provide 2–200 sample points.');
 if(!Array.isArray(queries)||queries.length<1||queries.length>MAX_QUERIES)throw Error('Provide 1–1000 query x values.');
 const samples=points.map((pair,i)=>{
  if(!Array.isArray(pair)||pair.length!==2)throw Error('Each sample must have exactly x and y.');
  return [number(pair[0],'Sample x '+(i+1)),number(pair[1],'Sample y '+(i+1))];
 });
 for(let i=1;i<samples.length;i++)if(!(samples[i][0]>samples[i-1][0]))
  throw Error('Sample x values must be strictly increasing; duplicates and unsorted points are not allowed.');
 const slopes=method==='pchip'?pchipSlopes(samples):null;
 const xs=queries.map((x,i)=>number(x,'Query x '+(i+1))).sort((a,b)=>a-b);
 const min=samples[0][0],max=samples[samples.length-1][0];
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
  if(method==='pchip'){
   const t=fraction,t2=t*t,t3=t2*t,h=x1-x0;
   const h00=2*t3-3*t2+1,h10=t3-2*t2+t,h01=-2*t3+3*t2,h11=t3-t2;
   y=number(h00*y0+h10*h*slopes[lo]+h01*y1+h11*h*slopes[hi],'Interpolated y');
   // Guard tiny floating-point overshoots at monotone knots.
   y=Math.max(Math.min(y0,y1),Math.min(Math.max(y0,y1),y));
  }else y=number(y0+(y1-y0)*fraction,'Interpolated y');
  return [x,y];
 });
 return {type:method==='pchip'?'interpolation-pchip':'interpolation-linear',columns:['x','y'],rows,domain:[min,max],
  method:method==='pchip'?'Shape-preserving cubic Hermite interpolation (PCHIP)':'Piecewise-linear interpolation (sorted finite real samples)',
  note:method==='pchip'?'Piecewise monotone cubic interpolation; no extrapolation, global smoothness or uncertainty estimate.':'Interpolates only within the supplied domain; no extrapolation, spline smoothing or uncertainty estimate.'};
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
area.innerHTML='<summary>1D interpolation · Linear / PCHIP · Data Tables / Graphs</summary>'+
 '<p class="graph-data-muted">Enter sorted sample pairs (x,y), one per line, or load the first two columns of the active Data Table. Query values must be inside the sample domain.</p>'+
 '<div class="data-toolbar"><label>Interpolation method <select id="interp-method"><option value="linear">Linear</option><option value="pchip">Shape-preserving cubic (PCHIP)</option></select></label></div>'+ 
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
 '@media(max-width:600px){.interp-fields{grid-template-columns:1fr}}';
document.head.append(style);
let last=null;
function invalidate(){
 last=null;$('interp-to-table').disabled=$('interp-to-graph').disabled=true;
 $('interp-output').classList.remove('error');
}
function fail(error){
 invalidate();$('interp-output').classList.add('error');$('interp-output').textContent=error.message;
}
for(const id of ['interp-samples','interp-queries'])$(id).addEventListener('input',invalidate);
$('interp-method').addEventListener('change',invalidate);
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
  last=interpolate({points:parsePairs($('interp-samples').value),queries:parseQueries($('interp-queries').value),method:$('interp-method').value});
  $('interp-output').classList.remove('error');
  $('interp-output').textContent=last.method+'\n'+last.rows.length+' query results; domain ['+last.domain.join(', ')+']\n'+
   last.rows.slice(0,12).map(r=>r[0]+' → '+r[1]).join('\n')+
   (last.rows.length>12?'\n… '+(last.rows.length-12)+' more':'')+'\n'+last.note;
  $('interp-to-table').disabled=$('interp-to-graph').disabled=false;
 }catch(e){fail(e);}
});
function exportTable(){
 if(!last)throw Error('Run interpolation first.');
 return M.dataTables.importData({headers:last.columns,rows:last.rows},last.type==='interpolation-pchip'?'Interpolation_PCHIP':'Interpolation_Linear');
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
M.interpolationTools={interpolate,parsePairs,parseQueries};
})();