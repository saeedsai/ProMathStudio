"""Control Theory panel accessibility: control names, status regions, disclosure keyboard use, unique IDs, 390px."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

AUDIT = """() => {
  const root = document.getElementById('control-theory-toolbox');
  const name = el => (el.getAttribute('aria-label') || '').trim() ||
    ((el.getAttribute('aria-labelledby') || '').split(/\\s+/).map(id => (document.getElementById(id) || {}).textContent || '').join(' ').trim()) ||
    (el.labels && el.labels.length ? [...el.labels].map(l => l.textContent).join(' ').trim() : '') ||
    (el.tagName === 'BUTTON' ? el.textContent.trim() : '');
  const controls = [...root.querySelectorAll('input,select,textarea,button')];
  const unnamed = controls.filter(el => !name(el)).map(el => el.id || el.outerHTML.slice(0, 60));
  const ids = [...root.querySelectorAll('[id]')].map(e => e.id);
  const dupes = ids.filter((id, i) => ids.indexOf(id) !== i);
  const summaries = [...root.querySelectorAll('summary')].map(s => s.textContent.trim());
  const status = ['ct-status', 'ct-eq-status', 'ct-eq-stability-status', 'ct-eq-transient-status']
    .map(id => { const e = document.getElementById(id); return [id, !!e && (e.getAttribute('role') === 'status' || !!e.getAttribute('aria-live'))]; });
  return {count: controls.length, unnamed, dupes, summaries, status};
}"""


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="graph"]').click()
        page.evaluate("() => { for (const id of ['control-theory-toolbox', 'ct-equilibrium', 'ct-eq-transient']) document.getElementById(id).open = true; }")
        audit = page.evaluate(AUDIT)
        assert audit['count'] >= 15, audit
        assert audit['unnamed'] == [], 'controls without an accessible name: %s' % audit['unnamed']
        assert audit['dupes'] == [], 'duplicate ids: %s' % audit['dupes']
        assert len(audit['summaries']) == 3 and all(audit['summaries']), audit['summaries']
        assert all(ok for _, ok in audit['status']), 'status regions must be live: %s' % audit['status']

        # Disclosures: keyboard toggling with Enter and Space on each summary.
        for panel in ['ct-eq-transient', 'ct-equilibrium', 'control-theory-toolbox']:
            summary = page.locator('#%s > summary' % panel)
            summary.focus()
            assert page.evaluate("document.activeElement === document.querySelector('#%s > summary')" % panel)
            page.keyboard.press('Enter')
            assert page.evaluate("!document.getElementById('%s').open" % panel), panel + ' Enter should close'
            page.keyboard.press('Space')
            assert page.evaluate("document.getElementById('%s').open" % panel), panel + ' Space should reopen'

        # Keyboard-only run: focus a run button and activate it; the status region reports the result.
        run = page.locator('#ct-eq-run')
        run.focus()
        page.keyboard.press('Enter')
        assert 'Equilibrium computed' in page.locator('#ct-eq-status').inner_text()
        assert page.evaluate("getComputedStyle(document.getElementById('ct-eq-run')).outlineStyle") is not None

        # 390px: no horizontal overflow, controls remain reachable, targets are tappable.
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        small = page.evaluate("""() => [...document.querySelectorAll('#control-theory-toolbox button')]
            .filter(b => b.getClientRects().length).map(b => b.getBoundingClientRect().height).filter(h => h < 40).length""")
        assert small == 0, '%d visible buttons shorter than 40px' % small
        assert not errors, errors
        browser.close()
    print('PASS Control Theory accessibility: names, live regions, disclosure keyboard, mobile')


if __name__ == '__main__':
    main()
