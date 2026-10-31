"""Engineering filter project round-trip, legacy import, atomic rejection and 390px layout."""
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def upload(page, data):
    page.locator('#hub-project-file').set_input_files({
        'name': 'backup.json', 'mimeType': 'application/json',
        'buffer': json.dumps(data).encode('utf-8')})


def count(page):
    return page.locator('#eng-results article').count()


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
                                     executable_path=os.getenv('CHROMIUM_PATH') or None,
                                     args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 900})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('dialog', lambda d: d.accept())
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        page.locator('[data-workspace="engineering"]').click()
        page.locator('#eng-discipline').select_option('control')
        page.locator('#eng-search').fill('stability')
        filtered = count(page)
        assert 0 < filtered < page.evaluate('MathStudio.engineeringCatalog.tools.length')
        exported = page.evaluate('window.MathStudio.bridge.export()')
        assert exported['engineering'] == {'discipline': 'control', 'query': 'stability'}

        # Change the filter, then import our own export: the saved filter returns exactly.
        page.locator('#eng-discipline').select_option('')
        page.locator('#eng-search').fill('')
        upload(page, dict(exported, working='ENG_RT'))
        page.wait_for_function("window.MathStudio.bridge.export().working === 'ENG_RT'")
        assert page.locator('#eng-discipline').input_value() == 'control'
        assert page.locator('#eng-search').input_value() == 'stability'
        assert count(page) == filtered

        # Legacy project without the field imports and leaves the current filter alone.
        legacy = {k: v for k, v in exported.items() if k != 'engineering'}
        legacy['working'] = 'ENG_LEGACY'
        upload(page, legacy)
        page.wait_for_function("window.MathStudio.bridge.export().working === 'ENG_LEGACY'")
        assert page.locator('#eng-search').input_value() == 'stability'

        # Unknown discipline passes syntax checks but is refused by restore; prior state is rolled back.
        bad = dict(exported, working='ENG_BAD', engineering={'discipline': 'nosuchfield', 'query': 'zzz'})
        upload(page, bad)
        page.wait_for_function(
            "document.querySelector('#hub-status').textContent.includes('Engineering filter')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'ENG_LEGACY'
        assert page.locator('#eng-discipline').input_value() == 'control'
        assert page.locator('#eng-search').input_value() == 'stability'

        # Oversized query is refused by the schema before any mutation.
        big = dict(exported, working='ENG_BIG', engineering={'discipline': '', 'query': 'x' * 201})
        upload(page, big)
        page.wait_for_function(
            "document.querySelector('#hub-status').textContent.includes('Engineering filter is invalid')")
        assert page.evaluate('window.MathStudio.bridge.export().working') == 'ENG_LEGACY'

        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
        assert not errors, errors
        browser.close()
    print('PASS Engineering filter project round-trip, legacy, rollback, mobile')


if __name__ == '__main__':
    main()
