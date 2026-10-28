"""Equation task families: accessible grouping, no duplicate actions, task behavior."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        picker = page.locator('#workspace-task-select')
        groups = picker.locator('optgroup')
        assert groups.evaluate_all('(items)=>items.map(x=>[x.label,...Array.from(x.children).map(y=>y.value)])') == [
            ['Write & solve', 'basic'],
            ['Notebook & examples', 'examples', 'notebook', 'python'],
            ['Numerical & differential', 'numerical', 'ode'],
            ['Solver configuration', 'assumptions']
        ]
        for selector in ('#cas-run', '#add-btn', '#export-btn', '#cas-operation', '#cas-engine'):
            assert page.locator(selector).count() == 1, selector
        editor = page.locator('#equation-input')
        editor.fill('(x+2)^2')
        page.locator('#cas-engine').select_option('offline')
        page.locator('#cas-operation').select_option('expand')
        page.locator('#cas-run').click()
        assert page.locator('#cas-results .cas-equation').count() > 0
        picker.select_option('notebook')
        assert page.locator('#notebook').is_visible()
        assert editor.input_value() == '(x+2)^2'
        picker.select_option('numerical')
        assert page.locator('#num-details').evaluate('(el)=>el.open')
        picker.select_option('ode')
        assert page.locator('#ode-details').evaluate('(el)=>el.open')
        picker.select_option('assumptions')
        assert page.locator('#ui-solver-assumptions').evaluate('(el)=>el.open')
        picker.select_option('basic')
        assert page.locator('#cas-run').is_visible()
        assert editor.input_value() == '(x+2)^2'
        page.locator('[data-workspace="calculator"]').click()
        assert picker.locator('optgroup').count() == 0
        page.locator('[data-workspace="editor"]').click()
        assert picker.locator('optgroup').count() == 4
        assert editor.input_value() == '(x+2)^2'
        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            assert picker.is_visible(), width
            assert page.locator('#cas-run').is_visible(), width
            assert picker.evaluate('(e)=>e.scrollWidth<=e.clientWidth+2'), width
        assert not errors, errors
        browser.close()
    print('PASS categorized Equation task picker, CAS, notebook, numerical/ODE, assumptions, mobile')

if __name__ == '__main__':
    main()
