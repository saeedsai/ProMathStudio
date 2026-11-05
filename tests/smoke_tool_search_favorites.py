"""Find a tool: recent and pinned tools, Browse all tools, per-viewer persistence and storage failures."""
import functools
import http.server
import os
import threading
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
KEY = 'promath-tool-search-prefs-v1'


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        # The app is a single offline file; answer the browser's automatic favicon probe quietly.
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
            return
        super().do_GET()


def serve():
    handler = functools.partial(QuietHandler, directory=str(ROOT))
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def watch(page, errors):
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)


def search(page, text):
    box = page.locator('#tool-search-input')
    box.fill('')
    box.click()
    box.fill(text)


def quick(page):
    """Focus the empty field and return the quick view state."""
    page.locator('body').click(position={'x': 5, 'y': 5})
    page.locator('#tool-search-input').fill('')
    page.locator('#tool-search-input').focus()
    page.wait_for_selector('#tool-search-popup:not([hidden])')
    return page.evaluate("""()=>{
     const g=k=>[...document.querySelectorAll('#tool-search-list [role=group][data-group="'+k+'"] [role=option]')].map(o=>o.dataset.toolId);
     return {recent:g('recent'),pinned:g('pinned')};
    }""")


def wait_open(page, panel):
    page.wait_for_function("id=>{const d=document.getElementById(id);return d&&d.open&&d.contains(document.activeElement)}", arg=panel)


def main():
    server = serve()
    url = 'http://127.0.0.1:%d/index.html' % server.server_address[1]
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        errors = []
        ctx = browser.new_context(viewport={'width': 1280, 'height': 850})
        page = ctx.new_page()
        watch(page, errors)
        page.goto(url, wait_until='load')
        box = page.locator('#tool-search-input')
        assert 'Alt+P' in box.get_attribute('aria-keyshortcuts')

        # Empty field: no recents or pins yet, an explanatory note and a collapsed Browse all tools.
        state = quick(page)
        assert state == {'recent': [], 'pinned': []}, state
        assert box.get_attribute('aria-expanded') == 'true'
        assert page.locator('#tool-search-empty').is_visible()
        assert 'No recent or pinned' in page.locator('#tool-search-empty').inner_text()
        browse = page.locator('#tool-search .ts-browse')
        assert browse.is_visible() and browse.get_attribute('open') is None
        mode_before = page.evaluate("()=>MathStudio.advanced.currentMode()")
        page.keyboard.press('Enter')  # Nothing active: Enter in the empty field opens nothing.
        assert page.evaluate("()=>MathStudio.advanced.currentMode()") == mode_before
        assert page.locator('#tool-search-popup').is_visible()

        # Open three tools through search; recents list them most recent first.
        search(page, 'brent')
        page.keyboard.press('Enter')
        wait_open(page, 'brent-details')
        search(page, 'fft')
        page.locator('#tool-search-list [role=option]').first.click()
        wait_open(page, 'fft-details')
        search(page, 'matrix')
        page.keyboard.press('Enter')
        wait_open(page, 'matrix-tools')
        state = quick(page)
        assert state['recent'] == ['panel:matrix-tools', 'panel:fft-details', 'panel:brent-details'], state
        group = page.locator('#tool-search-list [role=group][data-group="recent"]')
        label_id = group.get_attribute('aria-labelledby')
        assert page.locator('#' + label_id).inner_text().lower() == 'recent tools'
        assert page.locator('#tool-search-list').get_attribute('role') == 'listbox'
        # Reopening an existing recent moves it to the front without duplicating it.
        search(page, 'brent')
        page.keyboard.press('Enter')
        wait_open(page, 'brent-details')
        state = quick(page)
        assert state['recent'] == ['panel:brent-details', 'panel:matrix-tools', 'panel:fft-details'], state

        # Arrow keys move through the quick view; Enter opens the active recent tool.
        page.keyboard.press('ArrowDown')
        assert box.get_attribute('aria-activedescendant') == 'tool-search-opt-0'
        page.keyboard.press('ArrowDown')
        page.keyboard.press('Enter')
        wait_open(page, 'matrix-tools')

        # Pin with the mouse: the toggle is a pressed button with an accessible name, out of the Tab order.
        quick(page)
        pin = page.locator('#tool-search-list [data-group="recent"] [data-tool-id="panel:fft-details"] .ts-pin')
        assert pin.get_attribute('aria-label').startswith('Pin ') and pin.get_attribute('aria-pressed') == 'false'
        assert pin.get_attribute('tabindex') == '-1'
        bb = pin.bounding_box()
        assert bb['width'] >= 40 and bb['height'] >= 40, bb
        pin.click()
        assert page.evaluate("()=>document.activeElement.id") == 'tool-search-input'
        state = quick(page)
        assert state['pinned'] == ['panel:fft-details'], state
        pinned_btn = page.locator('#tool-search-list [data-group="pinned"] [data-tool-id="panel:fft-details"] .ts-pin')
        assert pinned_btn.get_attribute('aria-pressed') == 'true'
        assert pinned_btn.get_attribute('aria-label').startswith('Unpin ')
        assert page.evaluate("()=>MathStudio.advanced.currentMode()") == 'calculator'  # Pin click did not open the tool.

        # Pin with the keyboard: Alt+P on the active search result, then Enter still opens it.
        search(page, 'beam')
        assert box.get_attribute('aria-activedescendant') == 'tool-search-opt-0'
        page.keyboard.press('Alt+p')
        first_pin = page.locator('#tool-search-opt-0 .ts-pin')
        assert first_pin.get_attribute('aria-pressed') == 'true'
        assert 'Pinned' in page.locator('#tool-search-status').inner_text()
        page.keyboard.press('Enter')
        page.wait_for_function("()=>MathStudio.advanced.currentMode()==='engineering'&&document.getElementById('eng-visuals').open")
        state = quick(page)
        assert state['pinned'] == ['panel:fft-details', 'catalog:structures.beam.deflection'], state
        assert state['recent'][0] == 'catalog:structures.beam.deflection', state
        # Unpin with the keyboard from the Pinned group (last option is the beam pin).
        total = page.locator('#tool-search-list [role=option]').count()
        page.keyboard.press('ArrowUp')
        assert box.get_attribute('aria-activedescendant') == 'tool-search-opt-%d' % (total - 1)
        page.keyboard.press('Alt+p')
        assert 'Unpinned' in page.locator('#tool-search-status').inner_text()
        state = quick(page)
        assert state['pinned'] == ['panel:fft-details'], state
        page.keyboard.press('Escape')
        assert page.locator('#tool-search-popup').is_hidden()

        # Bounds: 8 recents, 20 pins; planned or unknown tools cannot be pinned.
        ids = page.evaluate("()=>MathStudio.toolSearch.browse().flatMap(g=>g.items.map(i=>i.id)).slice(0,30)")
        assert len(ids) == 30
        for tool_id in ids[:10]:
            assert page.evaluate("id=>MathStudio.toolSearch.open(id)", tool_id)
        recent = [r['id'] for r in page.evaluate("()=>MathStudio.toolSearch.recent()")]
        assert recent == list(reversed(ids[:10]))[:8], recent
        page.evaluate("()=>MathStudio.toolSearch.pin('panel:fft-details',false)")
        results = [page.evaluate("id=>MathStudio.toolSearch.pin(id)", tool_id) for tool_id in ids[:21]]
        assert results[:20] == [True] * 20 and results[20] is None, results
        assert len(page.evaluate("()=>MathStudio.toolSearch.pinned()")) == 20
        # GNSS is implemented: a full pin list must reject it for capacity, not status.
        assert page.evaluate("()=>MathStudio.toolSearch.pin('catalog:gnss.positioning.least.squares')") is None
        # The genuinely planned spectral-analysis catalog entry is never pinnable.
        assert page.evaluate("()=>MathStudio.toolSearch.pin('catalog:signals.spectral.analysis')") is False
        assert page.evaluate("()=>MathStudio.toolSearch.pin('panel:no-such-tool')") is False
        for tool_id in ids[5:20]:
            page.evaluate("id=>MathStudio.toolSearch.pin(id,false)", tool_id)
        pins_before = [r['id'] for r in page.evaluate("()=>MathStudio.toolSearch.pinned()")]
        assert pins_before == ids[:5], pins_before

        # Persistence across reload and into a new browser context with the saved storage state.
        page.reload(wait_until='load')
        assert [r['id'] for r in page.evaluate("()=>MathStudio.toolSearch.recent()")] == recent
        assert [r['id'] for r in page.evaluate("()=>MathStudio.toolSearch.pinned()")] == pins_before
        state = quick(page)
        assert state['recent'] == recent and state['pinned'] == pins_before, state
        saved = ctx.storage_state()
        ctx2 = browser.new_context(viewport={'width': 1280, 'height': 850}, storage_state=saved)
        page2 = ctx2.new_page()
        watch(page2, errors)
        page2.goto(url, wait_until='load')
        assert [r['id'] for r in page2.evaluate("()=>MathStudio.toolSearch.pinned()")] == pins_before
        ctx2.close()

        # Corrupt JSON, wrong types, duplicates and missing tools fall back without exceptions.
        page.evaluate("k=>localStorage.setItem(k,'{not json')", KEY)
        page.reload(wait_until='load')
        assert page.evaluate("()=>MathStudio.toolSearch.recent().length") == 0
        assert page.evaluate("()=>MathStudio.toolPrefs.persisted()") is False
        assert quick(page) == {'recent': [], 'pinned': []}
        assert page.evaluate("()=>MathStudio.toolSearch.open('panel:brent-details')")
        assert page.evaluate("k=>JSON.parse(localStorage.getItem(k)).recents", KEY) == ['panel:brent-details']
        assert page.evaluate("()=>MathStudio.toolPrefs.persisted()") is True
        page.evaluate("""k=>localStorage.setItem(k,JSON.stringify({recents:[1,null,'panel:brent-details','panel:brent-details',
            'panel:no-such-tool','  ','panel:brent-details\\n',{x:1}],pins:'nope'}))""", KEY)
        page.reload(wait_until='load')
        assert [r['id'] for r in page.evaluate("()=>MathStudio.toolSearch.recent()")] == ['panel:brent-details']
        assert page.evaluate("()=>MathStudio.toolSearch.pinned()") == []
        assert page.evaluate("()=>MathStudio.toolPrefs.addRecent('  ')") is False
        assert page.evaluate("()=>MathStudio.toolPrefs.setPinned('panel:fft-details\\n',true)") is False
        for bad in ('null', '[]', '"text"', '42'):
            page.evaluate("([k,v])=>localStorage.setItem(k,v)", [KEY, bad])
            page.reload(wait_until='load')
            assert page.evaluate("()=>MathStudio.toolSearch.recent()") == [], bad
            assert page.evaluate("()=>MathStudio.toolPrefs.persisted()") is False, bad
            assert page.evaluate("()=>MathStudio.toolSearch.open('panel:brent-details')"), bad
            assert page.evaluate("()=>MathStudio.toolPrefs.persisted()") is True, bad
        ctx.close()

        # Storage that throws on every access: the session still keeps recents and pins in memory.
        ctx3 = browser.new_context(viewport={'width': 1280, 'height': 850})
        ctx3.add_init_script("""(()=>{const fail=()=>{throw new DOMException('blocked','SecurityError')};
            Storage.prototype.getItem=fail;Storage.prototype.setItem=fail;})()""")
        page3 = ctx3.new_page()
        watch(page3, errors)
        page3.goto(url, wait_until='load')
        assert page3.evaluate("()=>MathStudio.toolSearch.recent()") == []
        assert page3.evaluate("()=>MathStudio.toolPrefs.persisted()") is False
        search(page3, 'fft')
        page3.keyboard.press('Alt+p')
        assert 'session only' in page3.locator('#tool-search-status').inner_text().lower()
        page3.keyboard.press('Enter')
        wait_open(page3, 'fft-details')
        assert quick(page3) == {'recent': ['panel:fft-details'], 'pinned': ['panel:fft-details']}
        assert page3.evaluate("()=>MathStudio.toolPrefs.persisted()") is False
        ctx3.close()

        # A failed write followed by a successful pin save must announce recovery.
        ctx_recover = browser.new_context(viewport={'width': 390, 'height': 850})
        ctx_recover.add_init_script("""(()=>{let blocked=true;const original=Storage.prototype.setItem;
            Storage.prototype.setItem=function(...args){if(blocked){blocked=false;throw new DOMException('full','QuotaExceededError');}
                return original.apply(this,args);};})()""")
        recover_page = ctx_recover.new_page()
        watch(recover_page, errors)
        recover_page.goto(url, wait_until='load')
        search(recover_page, 'fft')
        recover_page.keyboard.press('Alt+p')
        assert 'session only' in recover_page.locator('#tool-search-status').inner_text().lower()
        recover_page.keyboard.press('Alt+p')
        assert 'now saved to this browser' in recover_page.locator('#tool-search-status').inner_text().lower()
        assert recover_page.evaluate("()=>MathStudio.toolPrefs.persisted()") is True
        ctx_recover.close()

        # Browse all tools: collapsed workspace groups contain known tools and open them.
        ctx4 = browser.new_context(viewport={'width': 1280, 'height': 850})
        page4 = ctx4.new_page()
        watch(page4, errors)
        page4.goto(url, wait_until='load')
        quick(page4)
        # Keyboard: Tab from the field reaches the disclosure and keeps the popup open.
        page4.keyboard.press('Tab')
        assert page4.evaluate("()=>document.activeElement.matches('#tool-search .ts-browse>summary')")
        page4.keyboard.press('Enter')
        assert page4.locator('#tool-search-popup').is_visible()
        # The native <details> toggle event is asynchronous: wait for the browse
        # groups to be populated instead of racing its render callback.
        page4.wait_for_function("()=>document.querySelectorAll('#tool-search .ts-browse-group').length >= 5")
        groups = page4.locator('#tool-search .ts-browse-group')
        modes = [groups.nth(i).get_attribute('data-mode') for i in range(groups.count())]
        for mode in ('calculator', 'editor', 'graph', 'data', 'engineering'):
            assert mode in modes, modes
        assert all(groups.nth(i).get_attribute('open') is None for i in range(groups.count()))
        api = {g['mode']: [i['id'] for i in g['items']] for g in page4.evaluate("()=>MathStudio.toolSearch.browse()")}
        assert 'panel:brent-details' in api['editor'] and 'panel:fft-details' in api['editor'], api['editor']
        assert 'panel:matrix-tools' in api['calculator']
        assert 'catalog:structures.beam.deflection' in api['engineering']
        assert 'catalog:gnss.positioning.least.squares' in api['engineering']  # Implemented GNSS is openable.
        assert 'catalog:signals.spectral.analysis' not in api['engineering']  # Planned-only entries remain excluded.
        # Keyboard: open the Equation group and a tool inside it.
        page4.keyboard.press('Tab')
        page4.keyboard.press('Tab')
        assert page4.evaluate("()=>document.activeElement.closest('.ts-browse-group')?.dataset.mode") == 'editor'
        page4.keyboard.press('Enter')
        brent = page4.locator('.ts-browse-group[data-mode="editor"] [data-tool-id="panel:brent-details"]')
        assert brent.is_visible()
        brent.focus()
        page4.keyboard.press('Enter')
        wait_open(page4, 'brent-details')
        assert page4.evaluate("()=>MathStudio.advanced.currentMode()") == 'editor'
        # Mouse: open the Engineering group and the beam tool.
        quick(page4)
        assert page4.locator('#tool-search .ts-browse').get_attribute('open') is not None  # Stays expanded.
        page4.locator('.ts-browse-group[data-mode="engineering"]>summary').click()
        page4.locator('.ts-browse-group[data-mode="engineering"] [data-tool-id="catalog:structures.beam.deflection"]').click()
        page4.wait_for_function("()=>MathStudio.advanced.currentMode()==='engineering'&&document.getElementById('eng-visuals').open")
        assert [r['id'] for r in page4.evaluate("()=>MathStudio.toolSearch.recent()")][:2] == [
            'catalog:structures.beam.deflection', 'panel:brent-details']
        # Escape inside the browse list closes the popup and returns focus to the field.
        quick(page4)
        page4.locator('#tool-search .ts-browse>summary').focus()
        page4.keyboard.press('Escape')
        assert page4.locator('#tool-search-popup').is_hidden()
        assert page4.evaluate("()=>document.activeElement.id") == 'tool-search-input'

        # Responsive: no horizontal overflow at 390 and 1280 with the quick view and groups expanded.
        for width in (390, 1280):
            page4.set_viewport_size({'width': width, 'height': 850})
            quick(page4)
            if page4.locator('#tool-search .ts-browse').get_attribute('open') is None:
                page4.locator('#tool-search .ts-browse>summary').click()
            for i in range(page4.locator('.ts-browse-group').count()):
                g = page4.locator('.ts-browse-group').nth(i)
                if g.get_attribute('open') is None:
                    g.locator(':scope>summary').click()
            popup = page4.locator('#tool-search-popup').bounding_box()
            assert popup['x'] >= 0 and popup['x'] + popup['width'] <= width + 1, (width, popup)
            item = page4.locator('.ts-browse-item').first.bounding_box()
            assert item['height'] >= 40, item
            assert page4.evaluate("()=>document.documentElement.scrollWidth<=window.innerWidth"), width
            assert page4.evaluate("()=>{const p=document.getElementById('tool-search-popup');return p.scrollWidth<=p.clientWidth+1}"), width
            page4.keyboard.press('Escape')
        ctx4.close()
        assert not errors, errors
        browser.close()
    server.shutdown()
    print('PASS tool search favourites: recents, pins (mouse/Alt+P), browse all, persistence, corrupt/blocked storage, 390/1280')


if __name__ == '__main__':
    main()
