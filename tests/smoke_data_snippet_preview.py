"""Browser regression: preview, cancel, explicit conflict skipping and atomic snippet import."""
import json
import os
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
                                         args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1280, 'height': 850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html', wait_until='load')
            page.evaluate('localStorage.clear()')
            page.reload(wait_until='load')
            page.locator('[data-workspace="data"]').click()
            page.locator('#dt-code-library summary').click()
            status = page.locator('#dt-library-message')
            preview = page.locator('#dt-snippet-preview')
            summary = page.locator('#dt-snippet-preview-summary')
            apply = page.locator('#dt-snippet-apply')
            cancel = page.locator('#dt-snippet-cancel')
            skip = page.locator('#dt-snippet-skip-conflicts')
            file_input = page.locator('#dt-snippet-file')

            def stored():
                return page.evaluate("JSON.parse(localStorage.getItem('promathstudio-data-snippets-v1') || '[]')")

            def upload(entries):
                payload = {'format': 'promathstudio-snippets', 'version': 1, 'snippets': entries}
                file_input.set_input_files({'name': 'saved.json', 'mimeType': 'application/json',
                                            'buffer': json.dumps(payload).encode('utf-8')})
                page.wait_for_function("() => document.querySelector('#dt-snippet-file').value === ''")

            def snippet(name, kind='Formula', sample='=SUM(A1:A3)'):
                return {'name': name, 'kind': kind, 'sample': sample}

            # First import previews but does not persist until Apply.
            upload([snippet('Alpha')])
            assert preview.is_visible()
            assert '1 new' in summary.inner_text()
            assert stored() == []
            cancel.click()
            assert not preview.is_visible()
            assert stored() == []
            assert 'canceled' in status.inner_text().lower()

            upload([snippet('Alpha')])
            apply.click()
            assert len(stored()) == 1
            original = stored()
            output_before = page.locator('#python-output-result').text_content()

            # A name conflict blocks Apply until the user explicitly chooses to skip it.
            upload([snippet('Alpha', sample='=MAX(A1:A3)'),
                    snippet('Beta', 'Python', 'result = 42'),
                    snippet('Gamma', sample='=MEDIAN(A1:A5)')])
            assert '2 new' in summary.inner_text()
            assert '1 name conflicts' in summary.inner_text()
            preview_entries = page.locator('#dt-snippet-preview-list li')
            assert preview_entries.count() == 3
            assert 'Alpha (Formula)' in preview_entries.nth(0).inner_text()
            assert 'name conflict' in preview_entries.nth(0).inner_text()
            assert 'Beta (Python)' in preview_entries.nth(1).inner_text()
            assert apply.is_disabled()
            assert stored() == original
            skip.check()
            assert apply.is_enabled()
            apply.click()
            rows = stored()
            assert len(rows) == 3
            assert next(x for x in rows if x['name'] == 'Alpha')['sample'] == '=SUM(A1:A3)'
            assert {x['name'] for x in rows} == {'Alpha', 'Beta', 'Gamma'}
            assert '1 conflicts skipped' in status.inner_text()
            assert page.locator('#python-output-result').text_content() == output_before

            # A preview becomes invalid when another UI action changes the saved library.
            upload([snippet('Delta')])
            page.locator('#dt-snippet-name').fill('External')
            page.locator('#dt-snippet-kind').select_option('Formula')
            page.locator('#dt-snippet-code').fill('=COUNT(A1:A3)')
            page.locator('#dt-snippet-save').click()
            assert len(stored()) == 4
            apply.click()
            assert 'changed during preview' in status.inner_text()
            assert len(stored()) == 4
            assert all(x['name'] != 'Delta' for x in stored())

            # Storage quota errors must not partially commit previewed imports.
            upload([snippet('Quota')])
            page.evaluate("""() => {
                window.__savedSetItem = Storage.prototype.setItem;
                Storage.prototype.setItem = function(){throw Error('quota');};
            }""")
            apply.click()
            assert 'Storage unavailable' in status.inner_text()
            page.evaluate("() => { Storage.prototype.setItem = window.__savedSetItem; }")
            assert all(x['name'] != 'Quota' for x in stored())

            upload([snippet(f'Over{i}') for i in range(41)])
            assert 'rejected' in status.inner_text().lower()
            assert not preview.is_visible()
            assert len(stored()) == 4

            for width in (390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 850})
                upload([snippet('Responsive')])
                assert preview.is_visible()
                assert apply.is_visible()
                assert cancel.is_visible()
                cancel.click()
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS snippet preview/cancel, conflict skipping, stale preview, storage rollback, no Python auto-run, mobile')


if __name__ == '__main__':
    main()
