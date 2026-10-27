"""Context menus, math-symbol routing, DEC/BIN/HEX and basic workbook actions."""
from pathlib import Path
import json, os
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(accept_downloads=True,viewport={'width':1360,'height':900})
  errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  page.locator('[data-workspace="calculator"]').click()
  assert page.locator('#quick-symbols').is_visible()
  page.locator('#quick-symbols').click()
  page.locator('#palette-search').fill('Arc sine')
  page.locator('.palette-button[title*="Arc sine"]').first.click()
  assert page.locator('#calc-input').input_value()=='asin(x)'
  assert not page.evaluate("document.body.classList.contains('library-open')")
  page.get_by_role('button',name='Number settings').click()
  assert page.locator('#ui-calc-settings').evaluate('(e)=>e.open')
  for expr,mode,expected in [('0b1010+0xF','dec','= 25'),('FF','hex','= 255'),('1010','bin','= 10'),('band(0xFF,0b1010)','dec','= 10'),('bxor(15,3)','dec','= 12'),('shl(3,2)','dec','= 12'),('sin(pi/2)','dec','= 1'),('0xFFFFFFFFFFFFFFFF','dec','= 18446744073709551615')]:
   page.locator('#calc-radix').select_option(mode)
   page.locator('#calc-input').fill(expr)
   page.locator('#calc-execute').click()
   assert page.locator('#calc-result-plain').inner_text()==expected,(expr,page.locator('#calc-result-plain').inner_text())
  page.locator('#calc-input').fill('0b102');page.locator('#calc-execute').click()
  assert 'Invalid binary/hexadecimal' in page.locator('#calc-result-plain').inner_text()
  page.locator('#calc-input').fill('3+4')
  page.locator('#calc-input').click(button='right')
  menu=page.locator('#workspace-context-menu')
  assert menu.is_visible()
  menu.get_by_text('Calculate expression').click()
  assert page.locator('#calc-result-plain').inner_text()=='= 7'
  page.locator('#calc-input').focus();page.keyboard.press('Shift+F10')
  assert menu.is_visible()
  page.keyboard.press('Escape');assert menu.is_hidden()
  with page.expect_download() as d:page.locator('#hub-export-project').click()
  assert json.loads(Path(d.value.path()).read_text())['calculator']['radix']=='dec'
  page.locator('[data-workspace="data"]').click()
  n=page.evaluate('MathStudio.dataTables.active.rows.length')
  page.locator('#dt-sheet tbody td').first.click(button='right')
  assert menu.get_by_text('Delete this row').is_visible()
  menu.get_by_text('Insert row below').click()
  assert page.evaluate('MathStudio.dataTables.active.rows.length')==n+1
  page.locator('#dt-sheet tbody td').first.click(button='right')
  menu.get_by_text('Copy cell (formula)').click()
  assert page.evaluate('MathStudio.contextActions.clipboard()')=='0'
  page.locator('#dt-sheet tbody tr').nth(1).locator('td').first.click(button='right')
  menu.get_by_text('Paste into cell / range').click()
  page.wait_for_function('()=>MathStudio.dataTables.active.rows[1][0]==="0"')
  page.locator('#dt-sheet thead th').nth(1).click(button='right')
  assert menu.get_by_text('Sort ascending').is_visible()
  page.locator('[data-workspace="editor"]').click()
  page.locator('#equation-input').fill('x^2-1')
  page.locator('#equation-input').click(button='right')
  menu.get_by_text('Send to Solver').click()
  assert page.locator('[data-workspace="solver"].active').count()==1
  page.locator('[data-workspace="graph"]').click()
  page.locator('#graph-canvas').click(button='right')
  assert menu.get_by_text('Export graph PNG').is_visible()
  page.set_viewport_size({'width':390,'height':844})
  page.locator('[data-workspace="data"]').click()
  page.evaluate('()=>MathStudio.contextActions.openAt(document.querySelector("#dt-sheet tbody td"),360,650)')
  rect=menu.bounding_box()
  assert rect and rect['x']>=0 and rect['x']+rect['width']<=391
  assert not errors,errors
  browser.close()
 print('PASS context menus, symbol routing, programmer bases, clipboard, responsive UI')
if __name__=='__main__':main()
