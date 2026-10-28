"""Browser regression: versioned saved-snippet JSON import/export and rollback."""
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
            browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
            page = browser.new_page(accept_downloads=True, viewport={'width': 1280, 'height': 850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:%s/index.html' % server.server_port, wait_until='load')
            page.evaluate('localStorage.clear()')
            page.reload(wait_until='load')
            page.locator('[data-workspace="data"]').click()
            page.locator('#dt-code-library summary').click()
            name = page.locator('#dt-snippet-name')
            kind = page.locator('#dt-snippet-kind')
            code = page.locator('#dt-snippet-code')
            status = page.locator('#dt-library-message')
            file_input = page.locator('#dt-snippet-file')

            def save(title, typ, sample):
                name.fill(title)
                kind.select_option(typ)
                code.fill(sample)
                page.get_by_role('button', name='Save snippet').click()
                assert 'Saved ' + title in status.inner_text()

            def import_payload(payload):
                file_input.set_input_files({'name': 'snippets.json', 'mimeType': 'application/json',
                                            'buffer': json.dumps(payload).encode('utf-8')})

            def stored():
                return page.evaluate("JSON.parse(localStorage.getItem('promathstudio-data-snippets-v1') || '[]')")

            save('Total α', 'Formula', '=SUM(A1:A3)')
            save('Clean rows', 'Python', 'result = tables["Data1"].dropna()')
            original = stored()
            output_before = page.locator('#python-output-result').text_content()
            with page.expect_download() as download_info:
                page.get_by_role('button', name='Export snippets JSON').click()
            download = download_info.value
            assert download.suggested_filename == 'promathstudio-snippets.json'
            payload = json.loads(Path(download.path()).read_text(encoding='utf-8'))
            assert payload == {'format': 'promathstudio-snippets', 'version': 1,
                               'snippets': [{key: row[key] for key in ('name', 'kind', 'sample')} for row in original]}
            assert 'Exported 2' in status.inner_text()

            page.once('dialog', lambda dialog: dialog.accept())
            page.get_by_role('button', name='Delete snippet Clean rows').click()
            assert len(stored()) == 1
            import_payload(payload)
            assert 'Imported 1 snippets; 1 already saved.' in status.inner_text()
            assert stored() == original
            import_payload(payload)
            assert 'Imported 0 snippets; 2 already saved.' in status.inner_text()
            assert stored() == original
            assert page.locator('#python-output-result').text_content() == output_before

            conflict = dict(payload, snippets=[dict(payload['snippets'][0], sample='=MAX(A1:A3)')])
            import_payload(conflict)
            assert 'Name conflict' in status.inner_text()
            assert stored() == original

            for bad in (
                dict(payload, version=99),
                dict(payload, snippets=[payload['snippets'][0], payload['snippets'][0]]),
                dict(payload, snippets=[{'name': 'Bad', 'kind': 'Formula', 'sample': 'not a formula'}]),
                dict(payload, snippets=[{'name': 'Bad', 'kind': 'Python', 'sample': ''}]),
                dict(payload, snippets=[{'name': 'A' + str(i), 'kind': 'Formula', 'sample': '=1'} for i in range(41)]),
            ):
                import_payload(bad)
                assert 'rejected' in status.inner_text().lower()
                assert stored() == original
            file_input.set_input_files({'name': 'broken.json', 'mimeType': 'application/json', 'buffer': b'{broken'})
            assert 'rejected' in status.inner_text().lower()
            assert stored() == original
            file_input.set_input_files({'name': 'huge.json', 'mimeType': 'application/json', 'buffer': b'x' * 400001})
            assert '400 KB' in status.inner_text()
            assert stored() == original

            addition = dict(payload, snippets=[{'name': 'Extra', 'kind': 'Formula', 'sample': '=MEDIAN(A1:A5)'}])
            page.evaluate("() => { window.__originalSetItem = Storage.prototype.setItem; Storage.prototype.setItem = function(){throw Error('quota');}; }")
            import_payload(addition)
            assert 'Storage unavailable' in status.inner_text()
            assert stored() == original
            page.evaluate("() => { Storage.prototype.setItem = window.__originalSetItem; }")
            import_payload(addition)
            assert 'Imported 1 snippets' in status.inner_text()
            assert len(stored()) == 3

            page.reload(wait_until='load')
            page.locator('[data-workspace="data"]').click()
            page.locator('#dt-code-library summary').click()
            assert page.get_by_role('button', name='Edit snippet Extra').count() == 1
            assert page.get_by_role('button', name='Edit snippet Clean rows').count() == 1
            for width in (390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 850})
                assert page.locator('#dt-snippet-export').count() == 1
                assert page.locator('#dt-snippet-import').count() == 1
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS versioned snippet JSON round-trip, duplicate/idempotent import, malformed and quota rollback, no Python auto-run')


if __name__ == '__main__':
    main()
