"""ODE panel accessibility: control names, live output, unique IDs, keyboard run, 40px targets at 390px."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

AUDIT = """() => {
  const root = document.getElementById('ode-details');
  const name = el => (el.getAttribute('aria-label') || '').trim() ||
    (el.labels && el.labels.length ? [...el.labels].map(l => l.textContent).join(' ').trim() : '') ||
    (el.tagName === 'BUTTON' ? el.textContent.trim() : '');
  const controls = [...root.querySelectorAll('input,select,textarea,button')];
  const ids = [...root.querySelectorAll('[id]')].map(e => e.id);
  const out = document.getElementById('ode-output');
  const small = controls.filter(e => e.getClientRects().length)
    .map(e => [e.id, Math.round(e.getBoundingClientRect().height)]).filter(x => x[1] < 40);
  return {count: controls.length, unnamed: controls.filter(e => !name(e)).map(e => e.id),
          dupes: ids.filter((i, n) => ids.indexOf(i) !== n),
          live: [out.getAttribute('role'), out.getAttribute('aria-live')], small};
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
        page.locator('[data-workspace="editor"]').click()
        page.evaluate("() => { document.getElementById('ode-details').open = true; }")

        # Hidden coupled-system fields still carry names; switch method so they are audited visible too.
        for method in ['rk4', 'rk45', 'rk4-system']:
            page.locator('#ode-method').select_option(method)
            audit = page.evaluate(AUDIT)
            assert audit['count'] >= 12, audit
            assert audit['unnamed'] == [], 'unnamed controls (%s): %s' % (method, audit['unnamed'])
            assert audit['dupes'] == [], audit['dupes']
            assert audit['live'] == ['status', 'polite'], audit['live']
            assert audit['small'] == [], '%s: controls under 40px: %s' % (method, audit['small'])

        # Keyboard-only: focus Solve, press Enter, result lands in the live output region.
        page.locator('#ode-method').select_option('rk4')
        page.locator('#ode-run').focus()
        page.keyboard.press('Enter')
        assert 'Runge' in page.locator('#ode-output').inner_text()
        # An invalid input is announced through the same live region (error styling, not a dialog).
        page.locator('#ode-steps').fill('3')
        page.locator('#ode-run').focus()
        page.keyboard.press('Space')
        assert page.locator('#ode-output').evaluate("e => e.classList.contains('error')")
        assert 'integer from 4 to 1000' in page.locator('#ode-output').inner_text()

        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        browser.close()
    print('PASS ODE panel accessibility: names, live output, keyboard run, 40px targets, mobile')


if __name__ == '__main__':
    main()
