"""Engineering Toolbox responsive filters, keyboard focus, live results and canonical routing."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 390, 'height': 844})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'),
                         wait_until='load')
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 844})
            page.locator('[data-workspace="engineering"]').click()
            filters = page.evaluate("""() => {
                const ids = ['eng-discipline','eng-search'];
                return ids.map(id => {
                    const el = document.getElementById(id);
                    const r = el.getBoundingClientRect();
                    const label = el.closest('label');
                    return {id, height:r.height, visible:r.width>0,
                        named:!!label && !!label.textContent.trim(),
                        overflow:document.documentElement.scrollWidth>innerWidth+1};
                });
            }""")
            assert all(f['height'] >= 39.5 and f['visible'] and f['named']
                       and not f['overflow'] for f in filters), (width, filters)
            for field in ('eng-discipline', 'eng-search'):
                page.locator('#' + field).focus()
                outline = page.locator('#' + field).evaluate(
                    '(e) => parseFloat(getComputedStyle(e).outlineWidth)')
                assert outline >= 2.5, (width, field, outline)

            page.locator('#eng-discipline').select_option('aerospace')
            page.locator('#eng-search').fill('unlikely-no-match-987654')
            assert '0 unique tools' in page.locator('#eng-status').inner_text()
            assert page.locator('#eng-status').get_attribute('aria-live') == 'polite'
            assert 'No matching tools' in page.locator('#eng-results').inner_text()
            page.locator('#eng-search').fill('QR factorization')
            card = page.locator('#eng-results article[data-tool-id="matrix.qr.real.small"]')
            assert card.count() == 1, width
            assert '1 unique tools' in page.locator('#eng-status').inner_text()
            page.locator('#eng-search').focus()
            page.keyboard.press('Tab')
            assert card.locator('button').evaluate(
                '(e) => document.activeElement === e'), width
            page.keyboard.press('Enter')
            page.wait_for_function("document.activeElement?.id === 'mat-qr'")
            assert page.locator('#calculator-panel').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS Engineering 40px filters, focus, live status and QR route at 390/768/1280')


if __name__ == '__main__':
    main()
