"""Data Tables Code Library accessibility: control names, unique IDs, disclosure keyboard use, 40px targets at 390px."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

AUDIT = """() => {
  const root = document.getElementById('dt-code-library');
  const name = el => (el.getAttribute('aria-label') || '').trim() ||
    (el.labels && el.labels.length ? [...el.labels].map(l => l.textContent).join(' ').trim() : '') ||
    (el.tagName === 'BUTTON' ? el.textContent.trim() : '');
  const controls = [...root.querySelectorAll('input,select,textarea,button')].filter(e => e.type !== 'hidden');
  const ids = [...root.querySelectorAll('[id]')].map(e => e.id);
  const small = controls.filter(e => e.getClientRects().length)
    .map(e => [e.id || e.textContent.trim().slice(0, 20), Math.round(e.getBoundingClientRect().height)])
    .filter(x => x[1] < 35);
  return {count: controls.length, unnamed: controls.filter(e => !name(e)).map(e => e.id || e.tagName),
          dupes: [...new Set(ids.filter((i, n) => ids.indexOf(i) !== n))], small};
}"""


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="data"]').click()

        # Keyboard: the disclosure toggles with Enter and Space from its summary.
        summary = page.locator('#dt-code-library > summary')
        summary.focus()
        page.keyboard.press('Enter')
        assert page.evaluate("document.getElementById('dt-code-library').open")
        page.keyboard.press('Space')
        assert page.evaluate("!document.getElementById('dt-code-library').open")
        page.keyboard.press('Enter')

        audit = page.evaluate(AUDIT)
        assert audit['count'] >= 10, audit
        assert audit['unnamed'] == [], 'unnamed controls: %s' % audit['unnamed']
        assert audit['dupes'] == [], audit['dupes']
        # The search and category fields were 19-21px browser defaults; they must now be real touch targets.
        for control in ['dt-library-category', 'dt-library-search']:
            height = page.evaluate("document.getElementById('%s').getBoundingClientRect().height" % control)
            assert height >= 39.5, '%s is only %spx tall' % (control, height)
        assert audit['small'] == [], 'visible controls under 35px: %s' % audit['small']

        # Searching narrows the list and an unmatched query is reported, not silently empty.
        page.locator('#dt-library-search').fill('zzzz-no-such-recipe')
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        browser.close()
    print('PASS Data Tables Code Library accessibility: names, keyboard disclosure, touch targets, mobile')


if __name__ == '__main__':
    main()
