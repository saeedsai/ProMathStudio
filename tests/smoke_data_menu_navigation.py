"""Data Tables top-level menu traversal and quick-action focus regression."""
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
        page.locator('[data-workspace="data"]').click()
        nav = page.locator('#data-menu-navigation')
        menus = nav.locator(':scope > details')
        summaries = nav.locator(':scope > details > summary')
        assert menus.count() == summaries.count() == 5

        def focused(index):
            return summaries.nth(index).evaluate('(e) => document.activeElement === e')

        summaries.nth(0).focus()
        page.keyboard.press('ArrowRight')
        assert focused(1)
        assert not menus.nth(0).evaluate('(e) => e.open')
        assert not menus.nth(1).evaluate('(e) => e.open')
        page.keyboard.press('ArrowLeft')
        assert focused(0)
        page.keyboard.press('ArrowLeft')
        assert focused(4), 'ArrowLeft must wrap'
        page.keyboard.press('ArrowRight')
        assert focused(0), 'ArrowRight must wrap'
        page.keyboard.press('End')
        assert focused(4)
        page.keyboard.press('Home')
        assert focused(0)

        page.keyboard.press('Enter')
        assert menus.nth(0).evaluate('(e) => e.open')
        page.keyboard.press('ArrowRight')
        assert focused(1)
        assert menus.nth(0).evaluate('(e) => e.open'), 'Focus alone must not toggle'
        page.keyboard.press('Enter')
        assert menus.nth(1).evaluate('(e) => e.open')
        assert not menus.nth(0).evaluate('(e) => e.open')

        search = page.locator('#dt-filter')
        search.fill('unsaved filter draft')
        page.keyboard.press('ArrowRight')
        assert search.evaluate('(e) => document.activeElement === e'), 'Input arrows remain native'
        assert search.input_value() == 'unsaved filter draft'
        page.keyboard.press('Escape')
        assert not menus.nth(1).evaluate('(e) => e.open')
        assert focused(1)

        page.get_by_role('button', name='Filter rows', exact=True).click()
        assert menus.nth(1).evaluate('(e) => e.open')
        assert focused(1), 'Quick Filter must transfer focus to its summary'
        assert search.input_value() == 'unsaved filter draft'
        page.get_by_role('button', name='Python', exact=True).click()
        assert menus.nth(4).evaluate('(e) => e.open')
        assert not menus.nth(1).evaluate('(e) => e.open')
        assert focused(4), 'Quick Python must transfer focus to its summary'

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            summaries.nth(4).focus()
            page.keyboard.press('Home')
            assert focused(0), width
            page.keyboard.press('ArrowLeft')
            assert focused(4), width
            page.keyboard.press('Escape')
            assert not menus.nth(4).evaluate('(e) => e.open')
        assert not errors, errors
        browser.close()
    print('PASS Data Tables menu traversal, quick-action focus, drafts, input keys and mobile')


if __name__ == '__main__':
    main()
