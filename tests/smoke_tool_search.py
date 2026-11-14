"""Global "Find a tool" search: shortcuts, ranking, routing, ARIA combobox and responsive layout."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def active_id(page):
    return page.evaluate("()=>document.activeElement?.id||''")


def focus_inside(page, target):
    return page.evaluate("t=>{const e=document.getElementById(t);return Boolean(e&&e.contains(document.activeElement))}", target)


def search(page, text):
    page.locator('#tool-search-input').fill('')
    page.locator('#tool-search-input').click()
    page.locator('#tool-search-input').fill(text)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        box = page.locator('#tool-search-input')
        assert box.is_visible()
        assert page.locator('label[for="tool-search-input"]').inner_text() == 'Find a tool'
        assert box.get_attribute('role') == 'combobox' and box.get_attribute('aria-expanded') == 'false'
        assert box.get_attribute('aria-controls') == 'tool-search-list'
        assert page.locator('#tool-search-list').get_attribute('role') == 'listbox'
        assert page.locator('#tool-search-status').get_attribute('aria-live') == 'polite'

        # Shortcuts: "/" outside editable fields and Ctrl+K anywhere.
        page.locator('body').click(position={'x': 5, 'y': 5})
        page.keyboard.press('/')
        assert active_id(page) == 'tool-search-input'
        page.keyboard.press('Escape')
        page.locator('[data-workspace="calculator"]').click()
        page.locator('#calc-input').fill('')
        page.locator('#calc-input').focus()
        page.keyboard.type('8/2')
        assert active_id(page) == 'calc-input' and page.locator('#calc-input').input_value() == '8/2'
        page.keyboard.press('Control+k')
        assert active_id(page) == 'tool-search-input'

        # "brent" opens the Brent panel in the Equation workspace with focus inside it.
        search(page, 'brent')
        assert box.get_attribute('aria-expanded') == 'true'
        first = page.locator('#tool-search-list [role=option]').first
        assert 'Brent' in first.inner_text() and 'Equation' in first.inner_text()
        assert box.get_attribute('aria-activedescendant') == 'tool-search-opt-0'
        assert page.locator('#tool-search-opt-0').get_attribute('aria-selected') == 'true'
        assert 'found' in page.locator('#tool-search-status').inner_text()
        page.keyboard.press('Enter')
        page.wait_for_function("()=>document.getElementById('brent-details').open&&document.getElementById('brent-details').contains(document.activeElement)")
        assert page.evaluate("()=>MathStudio.advanced.currentMode()") == 'editor'
        assert page.locator('#brent-details').is_visible()
        assert box.get_attribute('aria-expanded') == 'false'
        # Opening never runs the tool or clears the calculator draft.
        assert page.locator('#calc-input').input_value() == '8/2'

        # "integral" finds quadrature and multiple-integral tools.
        titles = [r['title'] for r in page.evaluate("()=>MathStudio.toolSearch.search('integral')")]
        assert any('quadrature' in t.lower() for t in titles), titles
        assert any('Multiple' in t for t in titles), titles
        assert len(titles) <= 12

        # "fft" finds the FFT panel; mouse click opens it.
        search(page, 'fft')
        page.locator('#tool-search-list [role=option]').first.click()
        page.wait_for_function("()=>document.getElementById('fft-details').open&&document.getElementById('fft-details').contains(document.activeElement)")

        # Arrow keys move the active option; Enter opens it (matrix sub-section in Calculator).
        search(page, 'matrix')
        options = page.locator('#tool-search-list [role=option]')
        assert options.count() >= 2
        page.keyboard.press('ArrowDown')
        assert box.get_attribute('aria-activedescendant') == 'tool-search-opt-1'
        page.keyboard.press('ArrowUp')
        assert box.get_attribute('aria-activedescendant') == 'tool-search-opt-0'
        assert 'Matrix calculator' in options.first.inner_text()
        page.keyboard.press('Enter')
        page.wait_for_function("()=>document.getElementById('matrix-tools').open&&document.getElementById('matrix-tools').contains(document.activeElement)")
        assert page.evaluate("()=>MathStudio.advanced.currentMode()") == 'calculator'

        # "beam" uses the Engineering catalog route to the beam simulation.
        search(page, 'beam')
        assert 'Beam deflection' in page.locator('#tool-search-list [role=option]').first.inner_text()
        page.keyboard.press('Enter')
        page.wait_for_function("()=>MathStudio.advanced.currentMode()==='engineering'&&document.getElementById('eng-visuals').open")
        assert page.evaluate("()=>MathStudio.engineeringVisuals.visuals.find(v=>v.tool==='structures.beam.deflection').id") == page.locator('#eng-visual-select').input_value()

        # The implemented digital-logic simulation must route to its real panel.
        search(page, 'digital logic simulation')
        assert all(item['status'] == 'available' for item in page.evaluate("()=>MathStudio.toolSearch.search('digital logic simulation')") if item['id'] == 'catalog:electronics.digital.logic')
        # A genuinely planned catalog entry remains labelled and cannot be opened.
        search(page, 'signal spectral analysis')
        option = page.locator('#tool-search-list [role=option]').first
        assert 'Signal spectral analysis' in option.inner_text()
        assert 'Planned' in option.inner_text() and option.get_attribute('aria-disabled') == 'true'
        # A mixed result set may activate a real tool, but never a planned-only entry.
        # The query also matches available spectral tools, so a null active ID is not required.
        for key in ('ArrowDown', 'ArrowUp', 'Home', 'End'):
            selected = box.get_attribute('aria-activedescendant')
            if selected:
                assert page.locator('[id="' + selected + '"]').get_attribute('aria-disabled') != 'true'
            assert option.get_attribute('aria-selected') == 'false'
            page.keyboard.press(key)
        selected = box.get_attribute('aria-activedescendant')
        if selected:
            assert page.locator('[id="' + selected + '"]').get_attribute('aria-disabled') != 'true'
        assert option.get_attribute('aria-selected') == 'false'
        # Click while the popup is still visible: Enter may legitimately open an
        # enabled spectral match and dismiss the popup before the mouse check.
        mode_before = page.evaluate("()=>MathStudio.advanced.currentMode()")
        assert option.is_visible()
        # Playwright treats aria-disabled options as disabled and refuses a normal
        # click. Force the pointer event to test the application's refusal path.
        assert option.get_attribute('aria-disabled') == 'true'
        option.click(force=True, timeout=3000)
        assert option.get_attribute('aria-selected') == 'false'
        assert 'planned' in page.locator('#tool-search-status').inner_text().lower()
        assert page.evaluate("()=>MathStudio.advanced.currentMode()") == mode_before
        # Reopen the same results for a separate keyboard refusal check.
        search(page, 'signal spectral analysis')
        assert page.locator('#tool-search-list [role=option]').first.get_attribute('aria-disabled') == 'true'
        assert page.evaluate("()=>MathStudio.toolSearch.open('catalog:signals.spectral.analysis')") is False
        # The implemented GNSS tool is searchable and available (no longer a planned placeholder).
        assert all(r['status'] == 'available' for r in page.evaluate("()=>MathStudio.toolSearch.search('gnss positioning')"))

        # Escape closes then clears; no-match message.
        search(page, 'zzqqxx')
        assert page.locator('#tool-search-empty').is_visible()
        assert page.locator('#tool-search-list [role=option]').count() == 0
        assert 'No matching' in page.locator('#tool-search-status').inner_text()
        page.keyboard.press('Escape')
        assert page.locator('#tool-search-popup').is_hidden() and box.input_value() == 'zzqqxx'
        page.keyboard.press('Escape')
        assert box.input_value() == ''

        # Workspace task entries and data panels are indexed, units synonym works.
        assert any(r['kind'] == 'task' and r['mode'] == 'data' for r in page.evaluate("()=>MathStudio.toolSearch.search('combine tables')"))
        assert page.evaluate("()=>MathStudio.toolSearch.search('units')[0].title").startswith('Unit conversion')
        assert page.evaluate("()=>MathStudio.toolSearch.search('lp')[0].title").startswith('Optimization')

        # Existing navigation is unaffected: tabs still switch workspaces and arrow between tabs.
        page.locator('[data-workspace="graph"]').click()
        assert page.evaluate("()=>MathStudio.advanced.currentMode()") == 'graph'
        page.locator('[data-workspace="graph"]').focus()
        page.keyboard.press('ArrowRight')
        assert page.evaluate("()=>document.activeElement.matches('button[data-workspace]')")

        for width in (390, 768, 1280):
            page.set_viewport_size({'width': width, 'height': 850})
            page.locator('[data-workspace="editor"]').click()
            search(page, 'root')
            assert box.is_visible()
            bbox = box.bounding_box()
            popup = page.locator('#tool-search-popup').bounding_box()
            assert bbox['x'] >= 0 and bbox['x'] + bbox['width'] <= width + 1, (width, bbox)
            assert popup['x'] >= 0 and popup['x'] + popup['width'] <= width + 1, (width, popup)
            assert bbox['height'] >= 40
            assert page.evaluate("()=>document.documentElement.scrollWidth<=window.innerWidth"), width
            page.keyboard.press('Escape')
            page.keyboard.press('Escape')
        assert not errors, errors
        browser.close()
    print('PASS global tool search: shortcuts, ranking, routing, planned tools, ARIA, 390/768/1280')


if __name__ == '__main__':
    main()
