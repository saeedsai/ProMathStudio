"""FFT spectrum Hz units, validation and table/graph references."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os
ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  s=page.evaluate('() => MathStudio.fftTools.analyze([0,1,0,-1,0,1,0,-1],8)')
  assert s['spectrum'][2]['frequencyHz']==2 and abs(s['spectrum'][2]['amplitude']-1)<1e-12
  assert s['spectrum'][-1]['frequencyHz']==4
  assert page.evaluate('() => MathStudio.fftTools.analyze([1,1,1,1],100).spectrum[1].frequencyHz')==25
  for rate in [0,-1,1e13,'abc','']:
   assert page.evaluate('r=>{try{MathStudio.fftTools.analyze([1,0,0,0],r);return false;}catch(e){return true;}}',rate)
  page.locator('[data-workspace="solver"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-run').click()
  assert '2 Hz' in page.locator('#fft-output').inner_text()
  page.locator('#fft-to-table').click()
  table=page.evaluate('MathStudio.dataTables.active')
  assert table['columns'][:3]==['bin','frequency_Hz','amplitude']
  assert float(table['rows'][2][1])==2
  page.locator('[data-workspace="solver"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-to-graph').click()
  pts=page.evaluate('MathStudio.graphData.getState().points')
  assert abs(pts[2]['x']-2)<1e-12 and abs(pts[2]['y']-1)<1e-12,pts[2]
  page.locator('[data-workspace="solver"]').click()
  page.locator('#fft-details').evaluate('(e)=>e.open=true')
  page.locator('#fft-rate').fill('16')
  assert page.locator('#fft-to-table').is_disabled()
  page.locator('#fft-run').click()
  assert '4 Hz' in page.locator('#fft-output').inner_text()
  assert not errors,errors
  browser.close()
 print('PASS FFT Hz sample rate and graph/table integration')
if __name__=='__main__':main()
