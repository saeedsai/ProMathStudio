"""Bounded offline exact decimal and rounded-division browser/reference regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
 html=(ROOT/'index.html').read_text(encoding='utf-8')
 assert '<script id="promath-precision-tools">' in html
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or '/usr/bin/chromium',args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content(html,wait_until='load')
  cases=[
   ({'a':'0.1','b':'0.2'},'0.3'),
   ({'a':'123456789012345678901234567890.12345','b':'0.00005'},'123456789012345678901234567890.1235'),
   ({'a':'2.5','b':'4','operation':'multiply'},'10'),
   ({'a':'1','b':'8','operation':'divide','precision':40},'0.125'),
   ({'a':'1','b':'3','operation':'divide','precision':40},'0.'+'3'*40),
   ({'a':'-2','b':'4','operation':'divide','precision':40},'-0.5'),
   ({'a':'0.00001','b':'3','operation':'divide','precision':16},'0.000003333333333333333'),
   ({'a':'5','b':'2','operation':'divide','precision':16},'2.5'),
   ({'a':'1.2345678901234565','b':'1','operation':'divide','precision':16},'1.234567890123456'),
   ({'a':'1.2345678901234575','b':'1','operation':'divide','precision':16},'1.234567890123458'),
   ({'a':'-1.2345678901234575','b':'1','operation':'divide','precision':16},'-1.234567890123458'),
   ({'a':'1','b':'2','operation':'subtract'},'-1'),
   ({'a':'0','b':'3','operation':'divide'},'0'),
  ]
  for args,expected in cases:
   actual=page.evaluate('a=>MathStudio.precisionTools.calculate(a).result',args)
   assert actual==expected,(args,actual,expected)
  for args in [
   {'a':'1','b':'0','operation':'divide'},
   {'a':'1e3','b':'2'},
   {'a':'1','b':'2','precision':81},
   {'a':'1','b':'2','precision':15},
   {'a':'1','b':'2','precision':40.5},
   {'a':'1','b':'2','operation':'sqrt'},
   {'a':'','b':'2'},
   {'a':'9'*301,'b':'2'},
   {'a':'NaN','b':'2'},
  ]:
   assert page.evaluate('a=>{try{MathStudio.precisionTools.calculate(a);return false;}catch(e){return !!e.message;}}',args),args
  page.locator('[data-workspace="calculator"]').click()
  assert page.locator('[data-workspace="calculator"].active').count() == 1
  page.locator('#workspace-task-guide .task-choice[data-task="precision"]').click()
  assert page.locator('#precision-details').evaluate('(e) => e.open')
  page.locator('#precision-a').fill('1')
  page.locator('#precision-b').fill('3')
  page.locator('#precision-op').select_option('divide')
  page.locator('#precision-run').click()
  assert '0.'+'3'*40 in page.locator('#precision-output').inner_text()
  page.locator('#precision-b').fill('0')
  assert 'Inputs changed' in page.locator('#precision-output').inner_text()
  page.locator('#precision-run').click()
  assert 'Division by zero' in page.locator('#precision-output').inner_text()
  assert page.locator('#precision-output').evaluate("(e)=>e.classList.contains('error')")
  page.set_viewport_size({'width':390,'height':844})
  assert page.locator('#precision-run').is_visible()
  assert not errors,errors
  browser.close()
 print('PASS: exact decimal, 40-digit division, errors, task navigation and mobile UI')

if __name__=='__main__':
 main()
