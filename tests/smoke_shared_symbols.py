"""Shared Symbols palette: Solver, 2D/3D Graphs, session restore and keyboard focus."""
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
            symbols = page.locator('#quick-symbols')
            search = page.locator('#palette-search')
            equation = page.locator('#equation-input')
            graph = page.locator('#graph-input')

            # Solver shares the working equation editor and must expose the library.
            page.locator('[data-workspace="editor"]').click()
            assert page.locator('body').evaluate("(el) => el.classList.contains('ws-editor')")
            assert symbols.is_visible(), 'Symbols must be visible in Solver'
            equation.fill('x + ')
            equation.evaluate('(el) => el.setSelectionRange(el.value.length, el.value.length)')
            symbols.click()
            assert symbols.get_attribute('aria-expanded') == 'true'
            search.fill('Sine')
            page.locator('#palette-nav button[title="Insert Sine: sin(x)"]').click()
            assert equation.input_value() == 'x + sin(x)'
            assert equation.evaluate('(el) => document.activeElement === el')
            assert symbols.get_attribute('aria-expanded') == 'false'

            # Graph insertion must not overwrite the shared Solver/Editor equation.
            page.locator('[data-workspace="graph"]').click()
            assert page.locator('body').evaluate("(el) => el.classList.contains('ws-graph')")
            assert symbols.is_visible(), 'Symbols must be visible in Graphs'
            graph.fill('y = ')
            graph.evaluate('(el) => el.setSelectionRange(el.value.length, el.value.length)')
            symbols.click()
            search.fill('Sine')
            page.locator('#palette-nav button[title="Insert Sine: sin(x)"]').click()
            assert graph.input_value() == 'y = sin(x)'
            assert graph.evaluate('(el) => document.activeElement === el')
            assert equation.input_value() == 'x + sin(x)'

            # 3D mode retains a separate draft; insertion targets the 3D editor.
            page.locator('[data-graph-mode="3d"]').click()
            graph.fill('z = ')
            graph.evaluate('(el) => el.setSelectionRange(el.value.length, el.value.length)')
            symbols.click()
            search.fill('Cosine')
            page.locator('#palette-nav button[title="Insert Cosine: cos(x)"]').click()
            assert graph.input_value() == 'z = cos(x)'
            assert graph.evaluate('(el) => document.activeElement === el')

            # Keyboard dismissal restores focus to a visible trigger.
            symbols.click()
            assert search.evaluate('(el) => document.activeElement === el')
            page.keyboard.press('Escape')
            assert not page.locator('body').evaluate("(el) => el.classList.contains('library-open')")
            assert symbols.evaluate('(el) => document.activeElement === el')
            assert symbols.get_attribute('aria-expanded') == 'false'

            # Programmatic navigation and session restore must use the same classes.
            page.evaluate("() => window.MathStudio.advanced.mode('solver')")
            assert page.locator('[data-workspace="editor"]').get_attribute('aria-current') == 'page'
            assert symbols.is_visible()
            page.evaluate("() => window.MathStudio.advanced.mode('graph')")
            page.reload(wait_until='load')
            assert page.locator('[data-workspace="graph"]').get_attribute('aria-current') == 'page'
            assert symbols.is_visible()

            for width in (390, 768, 1280):
                page.set_viewport_size({'width': width, 'height': 850})
                assert symbols.is_visible(), 'Symbols hidden at %d px' % width
                symbols.click()
                assert search.is_visible()
                page.keyboard.press('Escape')
                assert symbols.evaluate('(el) => document.activeElement === el')

            page.locator('[data-workspace="data"]').click()
            assert not symbols.is_visible(), 'Data Tables has its own function library'
            assert not errors, errors
            browser.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    print('PASS shared Symbols in Solver/2D/3D, insertion, keyboard, restore and mobile')


if __name__ == '__main__':
    main()
