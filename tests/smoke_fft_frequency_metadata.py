"""FFT sample-rate validation, spectral bin resolution and Nyquist reference."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  for n,rate in [(4,100),(8,8),(256,1024)]:
   r=page.evaluate('p => MathStudio.fftTools.analyze(Array(p.n).fill(3),p.rate)',{'n':n,'rate':rate})
   assert r['binWidthHz']==rate/n and r['nyquistHz']==rate/2
   assert r['spectrum'][-1]['frequencyHz']==rate/2
   assert abs(r['spectrum'][0]['amplitude']-3)<1e-9
  for invalid in [True,False,None,[],{},' ',0,-4,1e13,'hello']:
   assert page.evaluate('v=>{try{MathStudio.fftTools.analyze([0,1,0,-1],v);return false;}catch(e){return true;}}',invalid),invalid
  page.locator('[data-workspace="editor"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-rate').fill('8')
  page.locator('#fft-run').click()
  assert 'Bin width 1 Hz' in page.locator('#fft-output').inner_text()
  assert 'Nyquist 4 Hz' in page.locator('#fft-output').inner_text()
  page.locator('#fft-rate').fill('')
  assert page.locator('#fft-to-table').is_disabled()
  page.locator('#fft-run').click()
  assert page.locator('#fft-output').evaluate('(e)=>e.classList.contains("error")')
  page.locator('#fft-rate').fill('16')
  page.locator('#fft-run').click()
  assert 'Bin width 2 Hz' in page.locator('#fft-output').inner_text()
  assert not errors,errors
  browser.close()
 print('PASS FFT rate validity, Nyquist, resolution and browser UI')
if __name__=='__main__':main()
