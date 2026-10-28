"""Graph symbol palette regression: caret replacement, editable templates and draft isolation."""
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
            browser = pw.chromium.launch(
                headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
                args=['--no-sandbox']
            )
            page = browser.new_page(viewport={'width': 1280, 'height': 850})
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.goto('http://127.0.0.1:%s/index.html' % server.server_port, wait_until='load')
            equation = page.locator('#equation-input')
            graph = page.locator('#graph-input')
            symbols = page.locator('#quick-symbols')
            search = page.locator('#palette-search')
            canvas = page.locator('#graph-canvas')
            equation.fill('x^2 + 5')
            page.locator('[data-workspace="graph"]').click()

            # Replace the selected x in a 2D draft; don't touch Equation or redraw.
            graph.fill('y = x^2 + 1')
            graph.evaluate('(el) => el.setSelectionRange(4, 5)')
            before = canvas.evaluate('(el) => el.toDataURL()')
            symbols.click()
            search.fill('Sine')
            page.locator('#palette-nav button[title="Insert Sine: sin(x)"]').click()
            assert graph.input_value() == 'y = sin(x)^2 + 1'
            assert graph.evaluate('(el) => document.activeElement === el')
            assert graph.evaluate('(el) => [el.selectionStart, el.selectionEnd]') == [8, 9]
            assert canvas.evaluate('(el) => el.toDataURL()') == before, 'Symbol insertion must not auto-plot'
            assert equation.input_value() == 'x^2 + 5', 'Graph palette overwrote Equation draft'
            assert symbols.get_attribute('aria-expanded') == 'false'

            # 3D uses a distinct draft and allows editing the inserted x placeholder.
            page.locator('[data-graph-mode="3d"]').click()
            graph.fill('z = x + y')
            graph.evaluate('(el) => el.setSelectionRange(4, 5)')
            before3d = canvas.evaluate('(el) => el.toDataURL()')
            symbols.click()
            search.fill('Cosine')
            page.locator('#palette-nav button[title="Insert Cosine: cos(x)"]').click()
            assert graph.input_value() == 'z = cos(x) + y'
            assert graph.evaluate('(el) => [el.selectionStart, el.selectionEnd]') == [8, 9]
            assert canvas.evaluate('(el) => el.toDataURL()') == before3d
            graph.type('y')
            assert graph.input_value() == 'z = cos(y) + y'

            page.locator('[data-graph-mode="2d"]').click()
            assert graph.input_value() == 'y = sin(x)^2 + 1'
            page.locator('[data-graph-mode="3d"]').click()
            assert graph.input_value() == 'z = cos(y) + y'
            assert equation.input_value() == 'x^2 + 5'

            # The same insertion and focus route works at mobile/tablet/desktop widths.
            for width in (390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 850})
                assert symbols.is_visible(), f'Symbols unavailable at {width}px'
                graph.fill('z = x')
                graph.evaluate('(el) => el.setSelectionRange(4, 5)')
                symbols.click()
                search.fill('Sine')
                page.locator('#palette-nav button[title="Insert Sine: sin(x)"]').click()
                assert graph.input_value() == 'z = sin(x)'
                assert graph.evaluate('(el) => document.activeElement === el')
                assert graph.evaluate('(el) => [el.selectionStart, el.selectionEnd]') == [8, 9]
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS graph symbols: 2D/3D selection, focus, drafts, no auto-plot, responsive')


if __name__ == '__main__':
    main()
