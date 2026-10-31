"""Engineering catalog keyboard operation, accessible names and focus visibility (desktop and 390px)."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="engineering"]').click()

        # Every available card has a unique accessible name; planned cards expose no control.
        names = page.eval_on_selector_all(
            '#eng-results article button', 'els => els.map(e => e.getAttribute("aria-label"))')
        assert names and all(n and n.startswith('Open existing tool: ') for n in names), names
        assert len(set(names)) == len(names), 'accessible names must be unique'
        planned_buttons = page.locator('#eng-results article:has-text("Planned") button').count()
        assert planned_buttons == 0, 'planned cards must not offer a fake control'
        assert page.locator('#eng-status').get_attribute('aria-live') == 'polite'

        # Keyboard-only: search by typing, Tab to the first result button, activate with Enter.
        page.locator('#eng-search').fill('fft')
        page.locator('#eng-search').focus()
        page.keyboard.press('Tab')
        focused = page.evaluate('document.activeElement.getAttribute("aria-label")')
        assert focused == 'Open existing tool: One-dimensional FFT', focused
        outline = page.evaluate('getComputedStyle(document.activeElement).outlineWidth')
        assert outline in ('3px', '3.0px') or float(outline.replace('px', '')) >= 2, outline
        page.keyboard.press('Enter')
        page.wait_for_function("(() => { const e = document.querySelector('#fft-run'); return e && e.getClientRects().length > 0; })()")

        # Space activates a different tool the same way.
        page.locator('[data-workspace="engineering"]').click()
        page.locator('#eng-search').fill('brent')
        page.locator('#eng-search').focus()
        page.keyboard.press('Tab')
        page.keyboard.press('Space')
        page.wait_for_function("(() => { const e = document.querySelector('#brent-run'); return e && e.getClientRects().length > 0; })()")

        # 390px: targets stay at least 40px tall and nothing overflows horizontally.
        page.set_viewport_size({'width': 390, 'height': 844})
        page.locator('[data-workspace="engineering"]').click()
        page.locator('#eng-search').fill('')
        heights = page.eval_on_selector_all(
            '#eng-results article button', 'els => els.map(e => e.getBoundingClientRect().height)')
        assert heights and min(heights) >= 39.5, heights
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        browser.close()
    print('PASS Engineering catalog keyboard, accessible names, focus visibility, mobile targets')


if __name__ == '__main__':
    main()
