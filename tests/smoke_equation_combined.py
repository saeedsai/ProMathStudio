"""Combined Equation station: editor, CAS, numerical tools and legacy routing."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        assert page.locator('.workspace-bar button[data-workspace]').count() == 4
        assert page.locator('[data-workspace="solver"]').count() == 0
        assert page.locator('[data-workspace="editor"]').inner_text().strip().endswith('Equation')
        for selector in ('#equation-input','#preview','#symbolic-panel','#cas-operation',
                         '#cas-run','#cas-engine','#notebook','#examples','#workspace-task-select'):
            assert page.locator(selector).is_visible(), selector
        editor = page.locator('#equation-input')
        editor.fill('(x+1)^2')
        assert page.locator('#preview math').count() > 0
        page.locator('#cas-engine').select_option('offline')
        page.locator('#cas-operation').select_option('expand')
        page.locator('#cas-run').click()
        assert page.locator('#cas-results .cas-equation').count() > 0
        page.locator('#add-btn').click()
        assert page.locator('#counter').inner_text() == '(1)'
        # Adding a notebook entry intentionally clears the input; start a fresh draft.
        editor.fill('(x+1)^2')
        tasks = page.locator('#workspace-task-select')
        assert tasks.locator('option').evaluate_all('(xs)=>xs.map(e=>e.value)') == [
            'basic','examples','notebook','python','numerical','ode','assumptions']
        tasks.select_option('numerical')
        assert page.locator('#num-details').evaluate('(e)=>e.open')
        assert page.locator('#symbolic-panel .cas-wrap').is_hidden()
        tasks.select_option('ode')
        assert page.locator('#ode-details').evaluate('(e)=>e.open')
        tasks.select_option('assumptions')
        assert page.locator('#ui-solver-assumptions').evaluate('(e)=>e.open')
        tasks.select_option('basic')
        assert page.locator('#symbolic-panel .cas-wrap').is_visible()
        assert editor.input_value() == '(x+1)^2'
        page.evaluate("() => window.MathStudio.advanced.mode('solver')")
        assert page.locator('[data-workspace="editor"]').get_attribute('aria-current') == 'page'
        assert page.locator('#symbolic-panel').is_visible()
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert page.locator('#equation-input').is_visible(), width
            assert page.locator('#cas-run').is_visible(), width
            assert tasks.is_visible(), width
            assert page.locator('#symbolic-panel').is_visible(), width
        assert not errors, errors
        browser.close()
    print('PASS unified Equation editor, offline CAS, numerical/ODE/assumptions, legacy route and mobile')

if __name__ == '__main__':
    main()
