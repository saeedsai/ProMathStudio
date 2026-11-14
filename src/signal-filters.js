/* ProMathStudio: offline digital filters, convolution and correlation for uniformly sampled real signals. No eval or network. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');
if(!M?.dataTables||!panel)return;
const $=id=>document.getElementById(id),MAX_ABS=1e12,MAX_SAMPLES=100000,MAX_TAPS=501,MAX_WORK=2e7;
const WINDOWS=['hamming','hann','blackman'];
const TYPES={
 'butter-low':'Butterworth IIR low-pass','butter-high':'Butterworth IIR high-pass',
 'fir-low':'Windowed-sinc FIR low-pass','fir-high':'Windowed-sinc FIR high-pass','fir-band':'Windowed-sinc FIR band-pass',
 'moving-average':'Moving-average FIR'
};
function signal(values,label='Signal',min=1){
 if(!Array.isArray(values)&&!(ArrayBuffer.isView(values)&&!(values instanceof DataView)))throw Error(label+' must be a numeric list.');
 const out=Array.from(values);
 if(out.length<min)throw Error(label+' needs at least '+min+' sample'+(min===1?'':'s')+'.');
 if(out.length>MAX_SAMPLES)throw Error(label+' allows at most '+MAX_SAMPLES+' samples.');
 if(!out.every(v=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<=MAX_ABS))throw Error(label+' samples must be finite numbers with magnitude at most 1e12.');
 return out;
}
function parseList(text,label='Signal'){
 if(typeof text!=='string'||text.length>400000)throw Error(label+': enter at most 400,000 characters.');
 const tokens=text.trim().split(/[\s,;]+/).filter(Boolean);
 if(!tokens.length)throw Error(label+' is empty; enter numeric samples.');
 if(tokens.some(t=>!/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?$/i.test(t)))throw Error(label+': enter real numbers separated by commas or whitespace.');
 return signal(tokens.map(Number),label);
}
function rate(value){
 if(typeof value!=='number'&&(typeof value!=='string'||!value.trim()))throw Error('Sample rate must be a positive number in Hz.');
 const fs=Number(value);
 if(!Number.isFinite(fs)||fs<=0||fs>1e12)throw Error('Sample rate must be positive and at most 1e12 Hz.');
 return fs;
}
function cutoffHz(value,fs,label='Cutoff'){
 if(typeof value!=='number'&&(typeof value!=='string'||!value.trim()))throw Error(label+' must be a number in Hz.');
 const f=Number(value);
 if(!Number.isFinite(f)||f<=0)throw Error(label+' must be positive.');
 if(f>=fs/2)throw Error(label+' must be below the Nyquist frequency '+fs/2+' Hz.');
 return f;
}
function integer(value,lo,hi,label){
 const n=typeof value==='string'&&value.trim()?Number(value):value;
 if(typeof n!=='number'||!Number.isInteger(n)||n<lo||n>hi)throw Error(label+' must be an integer from '+lo+' to '+hi+'.');
 return n;
}
const finite=(arr,what)=>{if(!arr.every(Number.isFinite))throw Error(what+' exceeded the finite numeric range.');return arr;};
// ---- Convolution and correlation ----
function convolve(x,h,mode='full'){
 const a=signal(x,'First sequence'),b=signal(h,'Second sequence');
 if(!['full','same','valid'].includes(mode))throw Error('Convolution mode must be full, same or valid.');
 if(a.length*b.length>MAX_WORK)throw Error('Convolution is too large (length product above 2e7).');
 const n=a.length,m=b.length,full=new Array(n+m-1).fill(0);
 for(let i=0;i<n;i++){const ai=a[i];if(ai)for(let j=0;j<m;j++)full[i+j]+=ai*b[j];}
 finite(full,'Convolution');
 // "same" follows the SciPy convention: centred, length of the first input, start index floor((m-1)/2).
 if(mode==='same'){const s=Math.floor((m-1)/2);return full.slice(s,s+n);}
 if(mode==='valid'){if(n<m)throw Error('Valid mode needs the first sequence at least as long as the second.');return full.slice(m-1,n);}
 return full;
}
function correlate(x,y,mode='full',options={}){
 const a=signal(x,'First sequence'),b=signal(y,'Second sequence');
 const values=convolve(a,b.slice().reverse(),mode);
 const n=a.length,m=b.length;
 // Full-mode lag of value index i is i-(m-1): r[k]=Σ x[t+k]·y[t].
 const first=mode==='full'?-(m-1):mode==='same'?Math.floor((m-1)/2)-(m-1):0;
 const lags=values.map((_,i)=>first+i);
 let scale=1;
 if(options.normalized){
  const ex=a.reduce((s,v)=>s+v*v,0),ey=b.reduce((s,v)=>s+v*v,0);
  if(!(ex>0)||!(ey>0))throw Error('Normalized correlation needs nonzero-energy sequences.');
  scale=1/Math.sqrt(ex*ey);
 }
 return {values:values.map(v=>v*scale),lags,mode,normalized:!!options.normalized};
}
// ---- FIR design ----
function windowWeights(n,type){
 if(!WINDOWS.includes(type))throw Error('Window must be hamming, hann or blackman.');
 const m=n-1;
 return Array.from({length:n},(_,i)=>{
  const c=Math.cos(2*Math.PI*i/m);
  return type==='hamming'?0.54-0.46*c:type==='hann'?0.5-0.5*c:0.42-0.5*c+0.08*Math.cos(4*Math.PI*i/m);
 });
}
const sinc=x=>x===0?1:Math.sin(Math.PI*x)/(Math.PI*x);
function gainAt(b,f){let re=0,im=0;for(let k=0;k<b.length;k++){re+=b[k]*Math.cos(2*Math.PI*f*k);im-=b[k]*Math.sin(2*Math.PI*f*k);}return Math.hypot(re,im);}
function firwin({length=31,cutoff,cutoff2,type='low',window='hamming',sampleRate=1}={}){
 const fs=rate(sampleRate),n=integer(length,3,MAX_TAPS,'FIR length');
 if(n%2!==1)throw Error('FIR length must be odd (symmetric type I filter).');
 if(!['low','high','band'].includes(type))throw Error('FIR type must be low, high or band.');
 const f1=cutoffHz(cutoff,fs,type==='band'?'Lower cutoff':'Cutoff')/fs;
 let f2=null;
 if(type==='band'){f2=cutoffHz(cutoff2,fs,'Upper cutoff')/fs;if(f2<=f1)throw Error('Upper cutoff must exceed the lower cutoff.');}
 const w=windowWeights(n,window),mid=(n-1)/2;
 const ideal=k=>type==='low'?2*f1*sinc(2*f1*k):type==='high'?sinc(k)-2*f1*sinc(2*f1*k):2*f2*sinc(2*f2*k)-2*f1*sinc(2*f1*k);
 let b=w.map((wi,i)=>wi*ideal(i-mid));
 // Scale like SciPy firwin: unit gain at DC (low), Nyquist (high) or band centre (band).
 const ref=type==='low'?0:type==='high'?0.5:(f1+f2)/2,g=gainAt(b,ref);
 if(!(g>1e-12))throw Error('Filter gain at the reference frequency vanished; widen the band or lengthen the filter.');
 b=b.map(v=>v/g);
 return {kind:'fir',type,window,length:n,b,a:[1],sampleRate:fs,cutoffHz:f1*fs,cutoff2Hz:f2===null?null:f2*fs};
}
function movingAverage(length=5){
 const n=integer(length,1,MAX_TAPS,'Moving-average length');
 return {kind:'fir',type:'moving-average',length:n,b:Array(n).fill(1/n),a:[1]};
}
// ---- Butterworth IIR via analog prototype + bilinear transform with pre-warping ----
function butter({order=4,cutoff,type='low',sampleRate=1}={}){
 const fs=rate(sampleRate),n=integer(order,1,8,'Butterworth order');
 if(!['low','high'].includes(type))throw Error('Butterworth type must be low or high.');
 const fc=cutoffHz(cutoff,fs);
 // Pre-warp: analog cutoff Ωc=2fs·tan(π fc/fs); with s=2fs(1-z⁻¹)/(1+z⁻¹), s/Ωc=(1/K)(1-z⁻¹)/(1+z⁻¹).
 const K=Math.tan(Math.PI*fc/fs),K2=K*K,sos=[];
 for(let k=0;k<Math.floor(n/2);k++){
  const a1=2*Math.sin(Math.PI*(2*k+1)/(2*n));// prototype pair s²+a1·s+1
  const d0=1+a1*K+K2,den=[1,(2*K2-2)/d0,(1-a1*K+K2)/d0];
  const num=type==='low'?[K2/d0,2*K2/d0,K2/d0]:[1/d0,-2/d0,1/d0];
  sos.push([...num,...den]);
 }
 if(n%2){// prototype real pole s=-1
  const d0=1+K,den=[1,(K-1)/d0,0];
  const num=type==='low'?[K/d0,K/d0,0]:[1/d0,-1/d0,0];
  sos.push([...num,...den]);
 }
 const ba=sosToBa(sos);
 return {kind:'iir',type,order:n,sos,b:ba.b,a:ba.a,sampleRate:fs,cutoffHz:fc,warpedAnalogCutoffRadPerS:2*fs*K};
}
function polymul(p,q){const r=new Array(p.length+q.length-1).fill(0);p.forEach((x,i)=>q.forEach((y,j)=>{r[i+j]+=x*y;}));return r;}
function sosToBa(sos){
 let b=[1],a=[1];
 for(const s of sos){b=polymul(b,s.slice(0,3));a=polymul(a,s.slice(3,6));}
 const order=sos.reduce((t,s)=>t+(s[2]===0&&s[5]===0?1:2),0);
 return {b:b.slice(0,order+1),a:a.slice(0,order+1)};
}
// ---- Filtering ----
function coefficients(b,a){
 const bb=signal(b,'Numerator b'),aa=signal(a,'Denominator a');
 if(aa[0]===0)throw Error('Leading denominator coefficient a[0] must be nonzero.');
 if(bb.length>1024||aa.length>1024)throw Error('At most 1024 coefficients are allowed.');
 const len=Math.max(bb.length,aa.length),a0=aa[0];
 return {b:Array.from({length:len},(_,i)=>(bb[i]||0)/a0),a:Array.from({length:len},(_,i)=>(aa[i]||0)/a0)};
}
function dfiit(b,a,x,zi){// direct form II transposed; b,a normalised, equal length
 const order=b.length-1,z=zi?zi.slice():new Array(order).fill(0),y=new Array(x.length);
 for(let t=0;t<x.length;t++){
  const xt=x[t],yt=b[0]*xt+(order?z[0]:0);
  for(let i=0;i<order-1;i++)z[i]=b[i+1]*xt-a[i+1]*yt+z[i+1];
  if(order)z[order-1]=b[order]*xt-a[order]*yt;
  y[t]=yt;
 }
 return {y,z};
}
function steadyState(b,a){// zi for a unit constant input in direct form II transposed
 const order=b.length-1,den=a.reduce((s,v)=>s+v,0);
 if(Math.abs(den)<1e-14)throw Error('Filter has a pole at z=1; steady-state initial conditions are undefined.');
 const g=b.reduce((s,v)=>s+v,0)/den,z=new Array(order).fill(0);
 for(let i=order-1;i>=0;i--)z[i]=b[i+1]-a[i+1]*g+(i+1<order?z[i+1]:0);
 return {z,gain:g};
}
function lfilter(b,a,x){
 const c=coefficients(b,a),data=signal(x,'Signal');
 if(data.length*c.b.length>MAX_WORK)throw Error('Filtering work is too large.');
 return finite(dfiit(c.b,c.a,data).y,'Filtered signal');
}
function checkSos(sos){
 if(!Array.isArray(sos)||!sos.length||sos.length>32)throw Error('SOS must contain 1 to 32 sections.');
 return sos.map(s=>{const r=signal(s,'SOS section');if(r.length!==6||r[3]===0)throw Error('Each SOS section must be [b0,b1,b2,a0,a1,a2] with a0 ≠ 0.');return r.map(v=>v/r[3]);});
}
function sosfilt(sos,x,zi){
 const S=checkSos(sos);let y=signal(x,'Signal');
 S.forEach((s,i)=>{y=dfiit(s.slice(0,3),s.slice(3),y,zi?zi[i]:null).y;});
 return finite(y,'Filtered signal');
}
function sections(filter){
 if(filter&&Array.isArray(filter.sos))return checkSos(filter.sos).map(s=>({b:s.slice(0,3),a:s.slice(3)}));
 if(filter&&Array.isArray(filter.b)){const c=coefficients(filter.b,filter.a||[1]);return [c];}
 throw Error('Filter must provide sos sections or b/a coefficients.');
}
function cascade(secs,x,level){// level scales steady-state initial conditions (null = zero state)
 let y=x;
 for(const s of secs){
  let zi=null;
  if(level!==null){const ss=steadyState(s.b,s.a);zi=ss.z.map(v=>v*level);level*=ss.gain;}
  y=dfiit(s.b,s.a,y,zi).y;
 }
 return y;
}
function padLength(secs){// SciPy-style 3·ntaps; ntaps = coefficients of the cascaded filter (first-order sections count once)
 const taps=secs.reduce((t,s)=>t+s.b.length-1,0)+1-secs.filter(s=>s.b.length===3&&s.b[2]===0&&s.a[2]===0).length;
 return 3*taps;
}
function filtfilt(filter,x){
 const secs=sections(filter),data=signal(x,'Signal'),pad=padLength(secs);
 if(data.length<=pad)throw Error('Zero-phase filtering needs more than '+pad+' samples (padlen = 3·ntaps) for this filter.');
 if(data.length*secs.reduce((t,s)=>t+s.b.length,0)*3>MAX_WORK)throw Error('Filtering work is too large.');
 const n=data.length,x0=data[0],xn=data[n-1];
 const ext=[...Array.from({length:pad},(_,i)=>2*x0-data[pad-i]),...data,...Array.from({length:pad},(_,i)=>2*xn-data[n-2-i])];
 let y=cascade(secs,ext,ext[0]).reverse();
 y=cascade(secs,y,y[0]).reverse();
 return finite(y.slice(pad,pad+n),'Filtered signal');
}
function apply(filter,x,{zeroPhase=false}={}){
 if(zeroPhase)return filtfilt(filter,x);
 const secs=sections(filter),data=signal(x,'Signal');
 if(data.length*secs.reduce((t,s)=>t+s.b.length,0)>MAX_WORK)throw Error('Filtering work is too large.');
 return finite(cascade(secs,data,null),'Filtered signal');
}
function freqz(filter,{sampleRate=1,points=256}={}){
 const fs=rate(sampleRate),n=integer(points,2,8192,'Frequency points'),secs=sections(filter);
 const response=[];
 let previous=0,unwrap=0;
 for(let k=0;k<n;k++){
  const f=k*(fs/2)/(n-1),w=2*Math.PI*f/fs;
  let hr=1,hi=0;
  for(const s of secs){
   let nr=0,ni=0,dr=0,di=0;
   for(let i=0;i<s.b.length;i++){const c=Math.cos(w*i),sn=-Math.sin(w*i);nr+=s.b[i]*c;ni+=s.b[i]*sn;dr+=s.a[i]*c;di+=s.a[i]*sn;}
   const d=dr*dr+di*di;
   if(d===0)throw Error('Frequency response is singular on the unit circle.');
   const qr=(nr*dr+ni*di)/d,qi=(ni*dr-nr*di)/d,tr=hr*qr-hi*qi;hi=hr*qi+hi*qr;hr=tr;
  }
  const magnitude=Math.hypot(hr,hi),phase=Math.atan2(hi,hr);
  if(k){let d=phase-previous;while(d>Math.PI){d-=2*Math.PI;}while(d<-Math.PI){d+=2*Math.PI;}unwrap+=d;}else unwrap=phase;
  previous=phase;
  response.push({frequencyHz:f,magnitude,magnitudeDb:magnitude>0?20*Math.log10(magnitude):-Infinity,phase,unwrappedPhase:unwrap});
 }
 return response;
}
function design(spec={}){
 const fs=rate(spec.sampleRate??1),type=spec.type||'butter-low';
 if(!TYPES[type])throw Error('Unknown filter type.');
 if(type==='butter-low'||type==='butter-high')return butter({order:spec.order,cutoff:spec.cutoff,type:type==='butter-low'?'low':'high',sampleRate:fs});
 if(type==='moving-average')return {...movingAverage(spec.length),sampleRate:fs};
 return firwin({length:spec.length,cutoff:spec.cutoff,cutoff2:spec.cutoff2,type:type.slice(4),window:spec.window||'hamming',sampleRate:fs});
}
function columnFromTable(table,column){
 const list=M.dataTables.tables,t=table===undefined||table===null||table===''?M.dataTables.active:list.find(s=>s.id===table||s.name===table);
 if(!t)throw Error('Select an existing Data Table.');
 const c=Number(column);
 if(!Number.isInteger(c)||c<0||c>=t.columns.length)throw Error('Choose a valid column.');
 const rows=M.dataTables.calculate(t);
 const values=rows.map(r=>r[c]).filter(v=>!(v===''||v===null||v===undefined));
 if(!values.length)throw Error('The selected column is empty.');
 const nums=values.map(v=>typeof v==='number'?v:typeof v==='string'&&v.trim()?Number(v):NaN);
 if(!nums.every(Number.isFinite))throw Error('Column "'+t.columns[c]+'" contains non-numeric cells.');
 return {values:signal(nums,'Column'),table:t.name,column:String(t.columns[c])};
}
function run(spec={}){
 const fs=rate(spec.sampleRate??1),input=signal(spec.data,'Signal',2),filter=design({...spec,sampleRate:fs});
 const zeroPhase=!!spec.zeroPhase,output=apply(filter,input,{zeroPhase}),response=freqz(filter,{sampleRate:fs,points:spec.points||256});
 let spectrum=null;
 const n=input.length;
 if(M.fftTools&&n>=4&&n<=256&&!(n&(n-1))){
  const peak=r=>r.spectrum.reduce((p,q)=>q.amplitude>p.amplitude?q:p);
  const si=M.fftTools.analyze(input,fs),so=M.fftTools.analyze(output,fs);
  spectrum={input:si.spectrum,output:so.spectrum,inputPeak:peak(si),outputPeak:peak(so)};
 }
 return {filter,input,output,response,zeroPhase,sampleRate:fs,spectrum};
}
// ---- UI ----
const area=document.createElement('details');area.id='filters-details';
const field=(id,label,value,extra='')=>'<label for="'+id+'">'+label+'<input id="'+id+'" type="number" step="any" value="'+value+'"'+extra+'></label>';
area.innerHTML='<summary>Digital filters · Butterworth IIR, windowed-sinc FIR, moving average</summary>'+
 '<p class="graph-data-muted">Filter a uniformly sampled real signal. Butterworth filters use second-order sections (bilinear transform with pre-warping); zero-phase mode runs forward and backward with odd reflection padding (3·ntaps). Causal filtering delays the signal.</p>'+
 '<div class="num-fields">'+
 '<label for="flt-source">Signal source<select id="flt-source"><option value="list">Typed list</option><option value="table">Data Table column</option></select></label>'+
 '<label for="flt-table" class="flt-table-only" hidden>Data Table<select id="flt-table"></select></label>'+
 '<label for="flt-column" class="flt-table-only" hidden>Column<select id="flt-column"></select></label>'+
 field('flt-rate','Sample rate (Hz)','100',' min="0"')+
 '<label for="flt-type">Filter type<select id="flt-type">'+Object.entries(TYPES).map(([k,v])=>'<option value="'+k+'">'+v+'</option>').join('')+'</select></label>'+
 field('flt-order','Butterworth order (1–8)','4',' min="1" max="8" step="1"')+
 field('flt-length','FIR length (odd ≤ 501)','31',' min="1" max="501" step="1"')+
 '<label for="flt-window">FIR window<select id="flt-window"><option value="hamming">Hamming</option><option value="hann">Hann</option><option value="blackman">Blackman</option></select></label>'+
 field('flt-cutoff','Cutoff / lower cutoff (Hz)','10',' min="0"')+
 field('flt-cutoff2','Upper cutoff (Hz, band-pass)','20',' min="0"')+
 '<label for="flt-mode">Filtering<select id="flt-mode"><option value="filtfilt">Zero-phase (filtfilt)</option><option value="lfilter">Causal (lfilter)</option></select></label>'+
 '</div>'+
 '<label for="flt-samples" class="flt-list-only">Signal samples (comma/space separated)</label>'+
 '<textarea id="flt-samples" class="flt-list-only" rows="3" spellcheck="false"></textarea>'+
 '<div class="data-toolbar"><button type="button" id="flt-run" class="primary">Run filter</button>'+
 '<button type="button" id="flt-refresh" class="secondary flt-table-only" hidden>Refresh tables</button>'+
 '<button type="button" id="flt-to-table" class="secondary" disabled>Save filtered signal to Data Tables</button></div>'+
 '<canvas id="flt-canvas" width="640" height="340" role="img" aria-label="Filter plot: run a filter to draw the input and filtered signals and the magnitude response."></canvas>'+
 '<pre id="flt-output" role="status" aria-live="polite">Choose a filter and press Run filter.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#filters-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px;max-width:100%;box-sizing:border-box}'+
 '#filters-details summary{cursor:pointer;color:#3c50ae;font-weight:750;min-height:40px;display:flex;align-items:center}'+
 '#filters-details [hidden]{display:none!important}'+
 '#filters-details input,#filters-details select,#filters-details button{min-height:40px;max-width:100%;box-sizing:border-box}'+
 '#filters-details input,#filters-details select{display:block;width:100%}'+
 '#flt-samples{display:block;width:100%;max-width:900px;min-height:65px;margin-top:6px;box-sizing:border-box}'+
 '#flt-canvas{display:block;width:100%;max-width:640px;height:auto;margin:8px 0;border:1px solid #dce5f3;border-radius:10px;background:#fff}'+
 '#flt-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:#fff;border:1px solid #dce5f3;border-radius:10px;font:12px/1.6 Consolas,monospace;max-width:100%;box-sizing:border-box}'+
 '#flt-output.error{color:#a82241;background:#fff2f4}';
document.head.append(style);
$('flt-samples').value=Array.from({length:200},(_,i)=>+(Math.sin(2*Math.PI*2*i/100)+0.4*Math.sin(2*Math.PI*30*i/100)).toFixed(6)).join(', ');
const out=$('flt-output'),canvas=$('flt-canvas');
let last=null;
function option(select,value,text){const o=document.createElement('option');o.value=value;o.textContent=text;select.append(o);}
function fillColumns(){
 const t=M.dataTables.tables.find(s=>s.id===$('flt-table').value),s=$('flt-column');s.replaceChildren();
 if(t)t.columns.forEach((c,i)=>option(s,String(i),String(c)));
}
function fillTables(){
 const s=$('flt-table'),prev=s.value;s.replaceChildren();
 for(const t of M.dataTables.tables)option(s,t.id,t.name);
 if([...s.options].some(o=>o.value===prev))s.value=prev;else if(M.dataTables.active)s.value=M.dataTables.active.id;
 fillColumns();
}
function invalidate(){last=null;$('flt-to-table').disabled=true;out.classList.remove('error');}
function fail(e){invalidate();out.classList.add('error');out.textContent=e.message+'\nAdjust the inputs and press Run filter again.';}
function layout(){
 const table=$('flt-source').value==='table',type=$('flt-type').value;
 for(const e of area.querySelectorAll('.flt-table-only'))e.hidden=!table;
 for(const e of area.querySelectorAll('.flt-list-only'))e.hidden=table;
 $('flt-order').closest('label').hidden=!type.startsWith('butter');
 $('flt-length').closest('label').hidden=type.startsWith('butter');
 $('flt-window').closest('label').hidden=!type.startsWith('fir');
 $('flt-cutoff').closest('label').hidden=type==='moving-average';
 $('flt-cutoff2').closest('label').hidden=type!=='fir-band';
 if(table)fillTables();
}
$('flt-source').addEventListener('change',()=>{layout();invalidate();});
$('flt-type').addEventListener('change',()=>{if($('flt-type').value==='moving-average'&&$('flt-length').value==='31')$('flt-length').value='5';layout();invalidate();});
$('flt-table').addEventListener('change',()=>{fillColumns();invalidate();});
$('flt-refresh').addEventListener('click',()=>{fillTables();invalidate();out.textContent='Table list refreshed.';});
for(const e of area.querySelectorAll('input,textarea,#flt-column,#flt-window,#flt-mode'))e.addEventListener(e.tagName==='SELECT'?'change':'input',invalidate);
function draw(r){
 const ctx=canvas.getContext('2d');if(!ctx)return;
 const W=canvas.width,H=canvas.height,top={x:44,y:12,w:W-56,h:H*0.52-24},bot={x:44,y:H*0.52+14,w:W-56,h:H*0.48-34};
 ctx.clearRect(0,0,W,H);ctx.fillStyle='#fff';ctx.fillRect(0,0,W,H);ctx.font='11px sans-serif';ctx.lineWidth=1;
 const frame=(b,label)=>{ctx.strokeStyle='#c8d3e8';ctx.strokeRect(b.x,b.y,b.w,b.h);ctx.fillStyle='#4a5676';ctx.fillText(label,b.x+4,b.y+12);};
 const lo=Math.min(...r.input,...r.output),hi=Math.max(...r.input,...r.output),span=hi-lo||1,n=r.input.length;
 const line=(vals,color,width)=>{ctx.strokeStyle=color;ctx.lineWidth=width;ctx.beginPath();vals.forEach((v,i)=>{const x=top.x+(n>1?i/(n-1):0)*top.w,y=top.y+top.h-(v-lo)/span*top.h;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();};
 frame(top,'Signal: input (grey) vs filtered (blue)');line(r.input,'#9aa4b8',1);line(r.output,'#2f56d0',2);
 frame(bot,'Magnitude response |H(f)|, 0 to '+r.sampleRate/2+' Hz');
 const mags=r.response.map(p=>p.magnitude),mmax=Math.max(1,...mags);
 ctx.strokeStyle='#e2e8f3';ctx.lineWidth=1;const yh=bot.y+bot.h-(Math.SQRT1_2/mmax)*bot.h;ctx.beginPath();ctx.moveTo(bot.x,yh);ctx.lineTo(bot.x+bot.w,yh);ctx.stroke();
 ctx.strokeStyle='#c23b5a';ctx.lineWidth=2;ctx.beginPath();
 r.response.forEach((p,i)=>{const x=bot.x+i/(r.response.length-1)*bot.w,y=bot.y+bot.h-p.magnitude/mmax*bot.h;i?ctx.lineTo(x,y):ctx.moveTo(x,y);});ctx.stroke();
 ctx.fillStyle='#4a5676';ctx.fillText('1/√2',6,yh+4);ctx.lineWidth=1;
}
const fmt=v=>Number.isFinite(v)?(+v.toPrecision(8)).toString():String(v);
$('flt-run').addEventListener('click',()=>{
 try{
  let data,source;
  if($('flt-source').value==='table'){const c=columnFromTable($('flt-table').value,$('flt-column').value);data=c.values;source='column "'+c.column+'" of '+c.table;}
  else{data=parseList($('flt-samples').value);source='typed list';}
  const type=$('flt-type').value;
  const r=run({data,sampleRate:$('flt-rate').value,type,order:$('flt-order').value,length:$('flt-length').value,window:$('flt-window').value,cutoff:$('flt-cutoff').value,cutoff2:$('flt-cutoff2').value,zeroPhase:$('flt-mode').value==='filtfilt'});
  last=r;out.classList.remove('error');
  const f=r.filter,dc=r.response[0].magnitude,ny=r.response[r.response.length-1].magnitude;
  const lines=[TYPES[type]+' · '+(r.zeroPhase?'zero-phase filtfilt':'causal lfilter')+' · '+r.input.length+' samples from '+source+'.',
   f.kind==='iir'?'Order '+f.order+', cutoff '+fmt(f.cutoffHz)+' Hz, '+f.sos.length+' second-order section(s).':'FIR length '+f.length+(f.window?', '+f.window+' window':'')+(f.cutoffHz?', cutoff '+fmt(f.cutoffHz)+(f.cutoff2Hz?'–'+fmt(f.cutoff2Hz):'')+' Hz':'')+'.',
   '|H| at DC '+fmt(dc)+' · at Nyquist '+fmt(ny)+'.',
   'Output range '+fmt(Math.min(...r.output))+' to '+fmt(Math.max(...r.output))+'.'];
  if(r.spectrum)lines.push('FFT peak (fftTools): input '+fmt(r.spectrum.inputPeak.frequencyHz)+' Hz amplitude '+fmt(r.spectrum.inputPeak.amplitude)+' → output '+fmt(r.spectrum.outputPeak.frequencyHz)+' Hz amplitude '+fmt(r.spectrum.outputPeak.amplitude)+'.');
  out.textContent=lines.join('\n');
  draw(r);
  canvas.setAttribute('aria-label','Filter plot: '+r.input.length+' input samples and filtered output; magnitude response '+fmt(dc)+' at DC and '+fmt(ny)+' at Nyquist.');
  $('flt-to-table').disabled=false;
 }catch(e){fail(e);}
});
$('flt-to-table').addEventListener('click',()=>{
 try{
  if(!last)throw Error('Run a valid filter first.');
  if(last.input.length>6000)throw Error('Data Tables hold at most 6,000 rows; use the API for longer signals.');
  M.dataTables.importData({headers:['index','time_s','input','filtered'],rows:last.input.map((v,i)=>[i,i/last.sampleRate,v,last.output[i]])},'Filtered_Signal');
  M.advanced?.mode?.('data');
 }catch(e){fail(e);}
});
layout();
M.signalFilters={convolve,correlate,firwin,movingAverage,butter,sosToBa,lfilter,sosfilt,filtfilt,apply,freqz,design,run,parseList,columnFromTable,windowWeights,types:Object.keys(TYPES)};
})();
