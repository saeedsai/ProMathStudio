/* ProMathStudio: offline radix-2 FFT for uniformly sampled real signals. No eval or network. */
(()=>{'use strict';
const M=window.MathStudio,panel=document.getElementById('numerical-panel');
if(!M?.dataTables||!M?.advanced||!panel)return;
const $=id=>document.getElementById(id),MAX=1e9;
function fft(values,inverse=false){
 if(!Array.isArray(values)||values.length<4||values.length>256||(values.length&(values.length-1)))
  throw Error('FFT length must be a power of two from 4 to 256.');
 const n=values.length;
 const a=values.map(v=>{
  const re=typeof v==='number'?v:v?.re,im=typeof v==='number'?0:v?.im;
  if(typeof re!=='number'||typeof im!=='number'||!Number.isFinite(re)||!Number.isFinite(im)||Math.abs(re)>MAX||Math.abs(im)>MAX)
   throw Error('FFT samples must be finite numbers with magnitude at most 1e9.');
  return {re,im};
 });
 for(let i=1,j=0;i<n;i++){
  let bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;
  if(i<j)[a[i],a[j]]=[a[j],a[i]];
 }
 for(let size=2;size<=n;size*=2){
  const angle=(inverse?2:-2)*Math.PI/size,wr=Math.cos(angle),wi=Math.sin(angle);
  for(let start=0;start<n;start+=size){
   let ur=1,ui=0;
   for(let k=0;k<size/2;k++){
    const p=a[start+k],q=a[start+k+size/2];
    const tr=ur*q.re-ui*q.im,ti=ur*q.im+ui*q.re;
    a[start+k]={re:p.re+tr,im:p.im+ti};
    a[start+k+size/2]={re:p.re-tr,im:p.im-ti};
    const nextR=ur*wr-ui*wi;ui=ur*wi+ui*wr;ur=nextR;
   }
  }
 }
 if(inverse)for(const v of a){v.re/=n;v.im/=n;}
 if(a.some(v=>!Number.isFinite(v.re)||!Number.isFinite(v.im)))throw Error('FFT result exceeded finite range.');
 return a;
}
function parse(text){
 if(typeof text!=='string'||text.length>5000)throw Error('Enter at most 5,000 characters of real samples.');
 const tokens=text.trim().split(/[\s,;]+/);
 if(tokens.some(t=>!t||!/^[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[-+]?\d+)?$/i.test(t)))
  throw Error('Enter real numeric samples separated by commas or whitespace.');
 const values=tokens.map(Number);
 fft(values);
 return values;
}
function analyze(samples,sampleRate=1,windowType='rectangular'){
 if(typeof sampleRate!=='number'&&(typeof sampleRate!=='string'||!sampleRate.trim()))throw Error('Sample rate must be a positive numeric value in Hz.');
 const rate=Number(sampleRate);
 if(!Number.isFinite(rate)||rate<=0||rate>1e12)throw Error('Sample rate must be positive and at most 1e12 Hz.');
 const values=Array.isArray(samples)?samples:parse(samples);
 if(!values.every(v=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<=MAX))
  throw Error('FFT analysis requires real finite samples with magnitude at most 1e9.');
 if(windowType!=='rectangular'&&windowType!=='hann')throw Error('Window must be rectangular or Hann.');
 // Periodic Hann uses N in the cosine denominator for DFT analysis.
 // Coherent-gain correction restores bin-centred amplitudes; it does not
 // eliminate leakage or correct arbitrary off-bin frequency amplitudes.
 const n=values.length;
 const weights=values.map((_,i)=>windowType==='hann'?0.5-0.5*Math.cos(2*Math.PI*i/n):1);
 const coherentGain=weights.reduce((sum,w)=>sum+w,0)/n;
 const windowedSamples=values.map((v,i)=>v*weights[i]);
 const transformed=fft(windowedSamples),recovered=fft(transformed,true);
 const maxError=Math.max(...recovered.map((v,i)=>Math.hypot(v.re-windowedSamples[i],v.im)));
 const scale=Math.max(1,...windowedSamples.map(Math.abs));
 if(!Number.isFinite(maxError)||maxError>1e-8*scale)throw Error('Inverse FFT round-trip residual is too large.');
 const spectrum=transformed.slice(0,n/2+1).map((z,k)=>({
  bin:k,frequencyHz:k*rate/n,amplitude:Math.hypot(z.re,z.im)*(k===0||k===n/2?1:2)/(n*coherentGain),
  phase:Math.atan2(z.im,z.re),real:z.re,imag:z.im
 }));
 return {samples:values.slice(),windowedSamples,window:windowType,coherentGain,sampleRate:rate,binWidthHz:rate/n,nyquistHz:rate/2,transformed,recovered,spectrum,maxError};
}
const area=document.createElement('details');area.id='fft-details';
area.innerHTML='<summary>Signal spectrum · offline FFT (4–256 samples)</summary>'+
 '<p class="graph-data-muted">Enter a uniformly sampled real signal (power-of-two length). One-sided amplitude includes the correct DC/Nyquist scaling. Bin k means k cycles per sample window, not Hz unless you know the sample rate.</p>'+
 '<label for="fft-rate">Sampling rate (Hz)<input id="fft-rate" type="number" min="0.000001" step="any" value="8"></label>'+ 
 '<label for="fft-window">Window <select id="fft-window"><option value="rectangular">Rectangular (none)</option><option value="hann">Hann (periodic)</option></select></label>'+ 
 '<label for="fft-samples">Real samples (comma/space separated)</label>'+
 '<textarea id="fft-samples" rows="3" spellcheck="false">0, 1, 0, -1, 0, 1, 0, -1</textarea>'+
 '<div class="data-toolbar"><button type="button" id="fft-run" class="primary">Analyze FFT</button>'+
 '<button type="button" id="fft-to-table" class="secondary" disabled>Save spectrum to Data Tables</button>'+
 '<button type="button" id="fft-to-graph" class="secondary" disabled>Plot amplitude in Graphs</button></div>'+
 '<pre id="fft-output" role="status" aria-live="polite">Analyze samples to view the frequency bins.</pre>';
panel.append(area);
const style=document.createElement('style');
style.textContent='#fft-details{border-top:1px solid #dce4f6;margin-top:15px;padding-top:13px}#fft-details summary{cursor:pointer;color:#3c50ae;font-weight:750}#fft-rate,#fft-window{display:block;width:180px;max-width:100%;margin:5px 0 12px;padding:7px;border:1px solid #cdd8ec;border-radius:7px}#fft-samples{display:block;width:100%;min-height:65px;max-width:900px;margin-top:6px}#fft-output{white-space:pre-wrap;overflow-wrap:anywhere;padding:12px;background:white;border:1px solid #dce5f3;border-radius:10px}#fft-output.error{color:#a82241;background:#fff2f4}';
document.head.append(style);
let last=null;
function invalidate(){last=null;$('fft-to-table').disabled=true;$('fft-to-graph').disabled=true;$('fft-output').classList.remove('error');$('fft-output').textContent='Analyze samples to view the frequency bins.';}
$('fft-samples').addEventListener('input',invalidate);
$('fft-rate').addEventListener('input',invalidate);
$('fft-window').addEventListener('change',invalidate);
$('fft-run').addEventListener('click',()=>{
 try{
  last=analyze($('fft-samples').value,$('fft-rate').value,$('fft-window').value);
  $('fft-output').classList.remove('error');
  const top=last.spectrum.slice().sort((a,b)=>b.amplitude-a.amplitude)[0];
  $('fft-output').textContent='FFT: '+last.samples.length+' real samples; '+last.spectrum.length+' nonnegative-frequency bins.\nPeak bin '+top.bin+' ('+top.frequencyHz+' Hz), amplitude '+top.amplitude.toPrecision(10)+'\nWindow '+last.window+' · coherent gain '+last.coherentGain.toPrecision(6)+'.\nInverse round-trip max error: '+last.maxError.toExponential(3)+'\nBin width '+last.binWidthHz+' Hz · Nyquist '+last.nyquistHz+' Hz.'+'\nOne-sided amplitude spectrum; frequency Hz = bin × sample rate / N.';
  $('fft-to-table').disabled=false;$('fft-to-graph').disabled=false;
 }catch(e){invalidate();$('fft-output').classList.add('error');$('fft-output').textContent=e.message;}
});
function importSpectrum(){
 if(!last)throw Error('Analyze a valid signal first.');
 return M.dataTables.importData({headers:['bin','frequency_Hz','amplitude','phase_rad','real','imag'],rows:last.spectrum.map(p=>[p.bin,p.frequencyHz,p.amplitude,p.phase,p.real,p.imag])},'FFT_Spectrum');
}
function fail(e){$('fft-output').classList.add('error');$('fft-output').textContent=e.message;}
$('fft-to-table').addEventListener('click',()=>{try{importSpectrum();M.advanced.mode('data');}catch(e){fail(e);}});
$('fft-to-graph').addEventListener('click',()=>{
 try{
  const table=importSpectrum();M.advanced.mode('graph');
  $('dt-graph-table').value=table.id;
  $('dt-graph-table').dispatchEvent(new Event('change',{bubbles:true}));
  $('dt-chart-type').value='line';$('dt-graph-x').value='1';$('dt-graph-y').value='2';
  $('dt-plot-table').click();
 }catch(e){fail(e);}
});
M.fftTools={fft,parse,analyze};
})();
