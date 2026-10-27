"""Offline FFT numerical references, negative paths, UI and table/graph handoffs."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[]
  page.on('pageerror',lambda error:errors.append(str(error)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  cases=page.evaluate("""() => {
   const f=MathStudio.fftTools;
   return {
    dc:f.analyze(Array(8).fill(3)),
    impulse:f.analyze([1,0,0,0,0,0,0,0]),
    sine:f.analyze([0,1,0,-1,0,1,0,-1]),
    nyquist:f.analyze([1,-1,1,-1,1,-1,1,-1]),
    large:f.analyze(Array.from({length:256},(_,i)=>Math.sin(2*Math.PI*17*i/256)+0.25*Math.cos(2*Math.PI*3*i/256)))
   };
  }""")
  def near(x,y):assert abs(x-y)<1e-9,(x,y)
  for k,p in enumerate(cases['dc']['spectrum']):near(p['amplitude'],3 if k==0 else 0)
  for k,p in enumerate(cases['impulse']['spectrum']):near(p['amplitude'],1/8 if k in (0,4) else 1/4)
  for k,p in enumerate(cases['sine']['spectrum']):near(p['amplitude'],1 if k==2 else 0)
  for k,p in enumerate(cases['nyquist']['spectrum']):near(p['amplitude'],1 if k==4 else 0)
  near(cases['large']['spectrum'][17]['amplitude'],1)
  near(cases['large']['spectrum'][3]['amplitude'],0.25)
  assert cases['large']['maxError']<1e-11
  assert all(abs(p['imag'])<1e-10 for p in cases['large']['recovered'])
  result=page.evaluate("""() => {
   const f=MathStudio.fftTools,signal=[1,2,3,4],copy=signal.slice();
   const back=f.fft(f.fft(signal),true);
   const bad=[[],[1,2,3],Array(512).fill(1),[1,2,NaN,4],[1,2,Infinity,4],[1,2,1e10,4],[1,2,true,4],[{re:1,im:1},0,0,0]];
   const strings=['','1 2 3','1,2,foo,4','1,2,3,4,','1,2,3,4;5','1,2,3,1e309'];
   return {unchanged:JSON.stringify(signal)===JSON.stringify(copy),back,
    bad:bad.map(a=>{try{f.analyze(a);return ''}catch(e){return e.message}}),
    strings:strings.map(s=>{try{f.parse(s);return ''}catch(e){return e.message}})};
  }""")
  assert result['unchanged'] and all(result['bad']) and all(result['strings']),result
  assert all(abs(z['re']-i)<1e-10 and abs(z['im'])<1e-10 for i,z in enumerate(result['back'],start=1))
  page.locator('[data-workspace="solver"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-run').click()
  assert 'Peak bin 2' in page.locator('#fft-output').inner_text()
  assert page.locator('#fft-to-table').is_enabled()
  before=page.evaluate('MathStudio.dataTables.tables.length')
  page.locator('#fft-to-table').click()
  assert page.locator('#data-panel').is_visible()
  assert page.evaluate('MathStudio.dataTables.tables.length')==before+1
  assert page.locator('#dt-sheet tbody tr').count()==5
  page.locator('[data-workspace="solver"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-run').click()
  page.locator('#fft-to-graph').click()
  assert page.locator('#graph-panel .graph-canvas-wrap').is_visible()
  assert page.evaluate('MathStudio.graphData.getState().points.length')==5
  page.locator('[data-workspace="solver"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-samples').fill('1,2,3')
  assert page.locator('#fft-to-table').is_disabled() and page.locator('#fft-to-graph').is_disabled()
  page.locator('#fft-run').click()
  assert 'power of two' in page.locator('#fft-output').inner_text()
  page.set_viewport_size({'width':390,'height':844})
  assert page.locator('#fft-run').is_visible()
  assert not errors,errors
  browser.close()
 print('PASS FFT DC/impulse/sine/Nyquist, inverse, invalid inputs, UI/table/graph')
if __name__=='__main__':main()
