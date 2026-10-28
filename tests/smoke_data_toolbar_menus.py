"""Keyboard and pointer dismissal for compact Data Tables action menus."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
 with sync_playwright() as pw:
  browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
  page = browser.new_page(accept_downloads=True, viewport={'width':1280,'height':850})
  errors = []
  page.on('pageerror', lambda error: errors.append(str(error)))
  page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
  page.locator('[data-workspace="data"]').click()
  nav = page.locator('#data-menu-navigation')
  menus = nav.locator(':scope > details')
  assert menus.count() == 5
  table, filt, combine, files, python = [menus.nth(i) for i in range(5)]

  table.locator(':scope > summary').focus()
  page.keyboard.press('Enter')
  assert table.evaluate('(e)=>e.open')
  filt.locator(':scope > summary').focus()
  page.keyboard.press('Space')
  assert filt.evaluate('(e)=>e.open')
  assert not table.evaluate('(e)=>e.open')

  search = page.locator('#dt-filter')
  search.fill('draft search')
  page.keyboard.press('Escape')
  assert not filt.evaluate('(e)=>e.open')
  assert filt.locator(':scope > summary').evaluate('(e)=>document.activeElement===e')
  filt.locator(':scope > summary').click()
  assert search.input_value() == 'draft search'
  search.fill('')
  page.locator('#dt-sortcol').select_option(index=0)
  page.locator('#dt-sortdir').select_option('asc')
  page.locator('#dt-sort').click()

  page.mouse.click(5, 5)  # Outside the fixed/absolute menu overlay.
  assert not filt.evaluate('(e)=>e.open')
  assert files.locator(':scope > summary').count() == 1  # Nested file-import disclosures must not match.
  files.locator(':scope > summary').click()
  assert files.evaluate('(e)=>e.open')
  with page.expect_download() as download:
   page.locator('#dt-export-csv').click()
  assert download.value.suggested_filename.endswith('.csv')
  python.locator(':scope > summary').click()
  assert python.evaluate('(e)=>e.open')
  assert not files.evaluate('(e)=>e.open')
  assert page.locator('#python-panel textarea').count() >= 1
  page.mouse.click(5, 5)  # Outside the fixed/absolute menu overlay.
  assert not python.evaluate('(e)=>e.open')

  for width in (390,768,1280):
   page.set_viewport_size({'width':width,'height':850})
   filt.locator(':scope > summary').click()
   assert filt.locator(':scope > summary').is_visible()
   assert search.is_visible()
   page.keyboard.press('Escape')
   assert not filt.evaluate('(e)=>e.open')
  assert not errors, errors
  browser.close()
 print('PASS Data Tables menus, keyboard focus, drafts, pointer dismissal, export and responsive layout')


if __name__ == '__main__':
 main()
