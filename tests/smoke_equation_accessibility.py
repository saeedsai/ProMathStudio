"""Equation CAS accessibility: one concise live result, errors, keyboard focus and responsive UI."""
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

        results = page.locator('#cas-results')
        status = page.locator('#cas-announcement')
        run = page.locator('#cas-run')
        editor = page.locator('#equation-input')
        tasks = page.locator('#workspace-task-select')
        assert results.get_attribute('role') == 'region'
        assert results.get_attribute('aria-label') == 'Symbolic results'
        assert results.get_attribute('aria-live') is None  # avoid duplicate MathML speech
        assert status.get_attribute('role') == 'status'
        assert status.get_attribute('aria-live') == 'polite'
        assert status.get_attribute('aria-atomic') == 'true'
        assert page.locator('#cas-status').get_attribute('role') is None
        assert run.get_attribute('aria-controls') == 'cas-results cas-status'

        # Keyboard execution keeps the button focused and announces an actual answer.
        page.locator('#cas-engine').select_option('offline')
        page.locator('#cas-operation').select_option('expand')
        editor.fill('(x+1)^2')
        run.focus()
        run.press('Enter')
        assert results.locator('.cas-equation').count() == 1
        assert '1 result' in status.text_content()
        assert 'First result:' in status.text_content()
        assert page.locator('#cas-status').get_attribute('class').endswith('success')
        assert page.evaluate('document.activeElement.id') == 'cas-run'
        assert run.get_attribute('aria-disabled') is None

        # Invalid input clears stale results and announces the actionable error.
        editor.fill('')
        run.press('Enter')
        assert results.locator('.cas-equation').count() == 0
        assert 'Type an equation first' in status.text_content()
        assert status.text_content().startswith('Unable to solve:')
        assert page.locator('#cas-save').is_disabled()
        assert run.get_attribute('aria-disabled') is None

        # Simulate a slow SymPy worker: keyboard focus survives the busy state,
        # and Enter cannot submit the same job twice while aria-disabled.
        page.evaluate("""() => {
          window.__casCalls = 0;
          window.Worker = class {
            postMessage(m) {
              window.__casCalls++;
              setTimeout(() => this.onmessage({data: {id:m.id, type:'result', data:{
                operation:'simplify', version:'1.14.0', note:'Simplified',
                items:[{plain:'x',latex:'x',mathml:'<math><mi>x</mi></math>',approx:''}]
              }}}), 350);
            }
            terminate() {}
          };
        }""")
        editor.fill('sqrt(x^2)')
        page.locator('#cas-engine').select_option('sympy')
        page.locator('#cas-operation').select_option('simplify')
        run.focus()
        run.press('Enter')
        page.wait_for_function("() => window.__casCalls === 1")
        assert run.get_attribute('aria-disabled') == 'true'
        assert run.is_enabled()  # aria-disabled keeps keyboard focus; JS guards reentry
        assert page.evaluate('document.activeElement.id') == 'cas-run'
        run.press('Enter')
        assert page.evaluate('window.__casCalls') == 1
        page.wait_for_function(
            "() => document.querySelector('#cas-announcement').textContent.includes('First result: x')"
            " && !document.querySelector('#cas-run').hasAttribute('aria-disabled')")
        assert page.evaluate('document.activeElement.id') == 'cas-run'
        assert results.locator('.cas-equation').count() == 1

        # Native task picker exposes all tools, restores focus to opened disclosures.
        tasks.select_option('assumptions')
        assert page.locator('#ui-solver-assumptions').evaluate('(e) => e.open')
        assert page.evaluate('document.activeElement.tagName') == 'SUMMARY'
        tasks.select_option('basic')
        assert run.is_visible()
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert run.is_visible(), width
            assert tasks.is_visible(), width
            assert results.is_visible(), width
            assert status.get_attribute('aria-live') == 'polite'
        assert not errors, errors
        browser.close()
    print('PASS Equation CAS live result/error summaries, keyboard busy focus and responsive UI')


if __name__ == '__main__':
    main()
