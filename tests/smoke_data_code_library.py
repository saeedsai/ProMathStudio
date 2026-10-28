"""Browser regression: Data Tables library insertion after blur, recipes, operations."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]

def main():
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True,executable_path=os.getenv('CHROMIUM_PATH') or None,args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':1280,'height':850})
  errors=[]
  page.on('pageerror',lambda e:errors.append(str(e)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'),wait_until='load')
  page.locator('[data-workspace="data"]').click()
  lib=page.locator('#dt-code-library')
  lib.locator('summary').click()
  assert lib.evaluate('(e)=>e.open')
  category=page.locator('#dt-library-category')
  search=page.locator('#dt-library-search')
  # A missing selection must not modify any workbook cell.
  initial=page.evaluate('JSON.stringify(MathStudio.dataTables.active.rows)')
  page.get_by_role('button',name='Insert SUM').click()
  assert 'Select a spreadsheet data cell first' in page.locator('#dt-library-message').inner_text()
  assert page.evaluate('JSON.stringify(MathStudio.dataTables.active.rows)')==initial
  # Preserve actual fixture values; the default workbook may contain examples.
  unchanged=page.evaluate('MathStudio.dataTables.active.rows[0].slice(0,2)')
  # Blur rebuilds the spreadsheet grid before the library button is clicked.
  cell=page.locator('#dt-sheet td input[data-row="0"][data-col="2"]')
  cell.click()
  search.fill('sum')
  page.get_by_role('button',name='Insert SUM').click()
  assert page.evaluate('MathStudio.dataTables.active.rows[0][2]')=='=SUM(A1:A5)'
  assert page.evaluate('MathStudio.dataTables.active.rows[0].slice(0,2)')==unchanged
  assert 'Inserted SUM into C1' in page.locator('#dt-library-message').inner_text()
  # Replacing a formula must not append a second equals sign.
  search.fill('IF')
  page.get_by_role('button',name='Insert IF').click()
  assert page.evaluate('MathStudio.dataTables.active.rows[0][2]')=='=IF(A1>0,B1,0)'
  # Category filter excludes formulas and only shows Python recipes.
  category.select_option('Python')
  search.fill('Filter rows')
  assert page.get_by_role('button',name='Insert SUM').count()==0
  before=page.locator('#python-output-result').text_content()
  page.get_by_role('button',name='Insert Filter rows').click()
  page.wait_for_function('()=>document.querySelector("#data-menu-navigation > details:nth-child(5)")?.open')
  assert ".query('value > 0')" in page.locator('#dt-python-code').input_value()
  assert page.locator('#python-output-result').text_content()==before
  assert page.locator('#dt-python-code').evaluate('(e)=>document.activeElement===e')
  # The Python editor lives in a popover; dismiss it before using the library.
  page.keyboard.press('Escape')
  assert not page.locator('#data-menu-navigation > details:nth-child(5)').evaluate('(e)=>e.open')
  # Operation chooser must not execute a join or create a new table.
  category.select_option('Operation')
  search.fill('UNION ALL')
  count=page.evaluate('MathStudio.dataTables.tables.length')
  assert page.get_by_role('button',name='Insert UNION ALL').count()==0
  page.get_by_role('button',name='Choose UNION ALL').click()
  page.wait_for_function('()=>document.querySelector("#data-menu-navigation > details:nth-child(3)")?.open')
  assert page.locator('#dt-op').input_value()=='unionall'
  assert page.evaluate('MathStudio.dataTables.tables.length')==count
  for width in (390,768,1280):
   page.set_viewport_size({'width':width,'height':850})
   assert page.locator('#dt-code-library summary').count()==1
   assert page.locator('#dt-library-search').count()==1
  assert not errors,errors
  browser.close()
 print('PASS Data Tables library formula/recipe/operation insertion, no auto-run, responsive')

if __name__=='__main__':main()
