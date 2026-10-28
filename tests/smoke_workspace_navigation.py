"""Workspace navigation keyboard focus, activation, live labels and responsive regressions."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')

        nav = page.locator('.workspace-bar')
        buttons = nav.locator('button[data-workspace]')
        assert nav.get_attribute('role') == 'navigation'
        assert buttons.count() == 5  # Includes dynamically injected Data Tables.
        assert page.locator('#workspace-subtitle').get_attribute('aria-live') == 'polite'
        assert page.locator('[data-workspace="editor"]').get_attribute('aria-current') == 'page'

        def focused():
            return page.evaluate('document.activeElement.dataset.workspace || null')

        def current():
            return page.locator('.workspace-bar [aria-current="page"]').get_attribute('data-workspace')

        page.locator('[data-workspace="editor"]').focus()
        page.keyboard.press('ArrowRight')
        assert focused() == 'solver'
        assert current() == 'editor', 'Arrows must not silently change the workspace'
        assert page.evaluate('getComputedStyle(document.activeElement).outlineStyle') != 'none'
        page.keyboard.press('ArrowRight')
        assert focused() == 'graph'
        page.keyboard.press('ArrowRight')
        assert focused() == 'data'
        page.keyboard.press('ArrowRight')
        assert focused() == 'calculator', 'Right arrow wraps around'
        page.keyboard.press('ArrowLeft')
        assert focused() == 'data', 'Left arrow wraps around'
        page.keyboard.press('Home')
        assert focused() == 'calculator'
        page.keyboard.press('End')
        assert focused() == 'data'
        page.keyboard.press('Enter')
        assert current() == 'data'
        assert page.locator('#data-panel').is_visible()
        assert page.locator('#workspace-subtitle').inner_text().strip()

        page.locator('[data-workspace="graph"]').focus()
        page.keyboard.press('Space')
        assert current() == 'graph'
        graph_input = page.locator('#graph-input')
        graph_input.fill('y = x^2')
        page.locator('[data-workspace="graph"]').focus()
        page.keyboard.press('Home')
        assert focused() == 'calculator'
        assert current() == 'graph'
        page.keyboard.press('Enter')
        assert current() == 'calculator'
        assert page.locator('#calc-input').is_visible()
        page.locator('[data-workspace="graph"]').click()
        assert graph_input.input_value() == 'y = x^2', 'Navigation must preserve drafts'

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            page.locator('[data-workspace="editor"]').focus()
            page.keyboard.press('End')
            assert focused() == 'data', width
            page.keyboard.press('ArrowRight')
            assert focused() == 'calculator', width
            assert buttons.count() == 5
            assert nav.evaluate('(e) => e.scrollWidth <= e.clientWidth + 1'), width
        assert not errors, errors
        browser.close()
    print('PASS workspace keyboard navigation, focus, activation, drafts and responsive widths')


if __name__ == '__main__':
    main()
