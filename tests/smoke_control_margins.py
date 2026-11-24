"""Browser regression: control stability margins, Bode crossover markers, catalog routing and mobile layout."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')

        # Catalog: control.frequency.response is available and opens the frequency panel.
        status = page.evaluate("MathStudio.engineeringCatalog.tools.find(t=>t.id==='control.frequency.response').status")
        assert status == 'available', status
        assert page.evaluate("MathStudio.engineeringCatalog.filter('','control orbit').length") == 0
        page.locator('[data-workspace="engineering"]').click()
        page.locator('#eng-discipline').select_option('control')
        page.locator('#eng-search').fill('margin')
        card = page.locator('#eng-results article[data-tool-id="control.frequency.response"]')
        assert card.count() == 1
        assert 'loop-shaping' in card.inner_text()
        card.locator('button').click()
        page.wait_for_function("document.getElementById('ct-frequency').open && document.getElementById('control-theory-toolbox').open")
        page.wait_for_function("document.activeElement === document.querySelector('#ct-frequency > summary')")
        assert page.locator('#ct-frequency').is_visible()

        # Reference: G = 1/(s(s+1)(s+2)), K = 1.
        page.locator('#ct-num').fill('1')
        page.locator('#ct-den').fill('1, 3, 2, 0')
        page.locator('#ct-gain').fill('1')
        page.locator('#ct-margins-run').click()
        out = page.locator('#ct-margins-output').inner_text()
        assert 'Gain margin: %.5g dB' % (20 * math.log10(6)) in out, out
        assert 'ω = 1.4142 rad/s' in out, out
        assert 'Phase margin: 53.411° at gain crossover ω = 0.44575 rad/s' in out, out

        # Bode mode appends margins and draws crossover markers on the canvas.
        page.locator('#ct-mode').select_option('bode')
        page.locator('#ct-run').click()
        assert 'completed' in page.locator('#ct-status').inner_text()
        assert 'Gain margin: 15.563 dB' in page.locator('#ct-output').inner_text()
        marker_pixels = page.evaluate("""() => {
          const c=document.getElementById('ct-canvas'),d=c.getContext('2d').getImageData(0,0,c.width,c.height).data;
          let pm=0,gm=0;for(let i=0;i<d.length;i+=4){if(d[i]===0xb4&&d[i+1]===0x23&&d[i+2]===0x4a)pm++;if(d[i]===0x6a&&d[i+1]===0x3f&&d[i+2]===0xb5)gm++;}
          return {pm,gm};
        }""")
        assert marker_pixels['pm'] > 20 and marker_pixels['gm'] > 20, marker_pixels

        # First order: infinite gain margin, PM 180 at DC.
        page.locator('#ct-den').fill('1, 1')
        page.locator('#ct-margins-run').click()
        out = page.locator('#ct-margins-output').inner_text()
        assert 'Gain margin: infinite' in out and 'Phase margin: 180°' in out, out

        # Second-order resonance via T = 1/(s^2+0.2s+1).
        page.locator('#ct-den').fill('1, 0.2, 0')
        page.locator('#ct-margins-run').click()
        z = 0.1
        out = page.locator('#ct-margins-output').inner_text()
        assert 'Mr = %s' % format(float('%.5g' % (1 / (2 * z * math.sqrt(1 - z * z)))), 'g') in out, out

        # Invalid input then recovery.
        page.locator('#ct-den').fill('0, 1')
        page.locator('#ct-margins-run').click()
        assert 'first coefficient nonzero' in page.locator('#ct-margins-status').inner_text()
        assert page.locator('#ct-margins-output').inner_text() == 'No valid margins.'
        page.locator('#ct-den').fill('1, 3, 2, 0')
        page.locator('#ct-margins-run').click()
        assert 'computed' in page.locator('#ct-margins-status').inner_text()
        assert 'Phase margin: 53.411' in page.locator('#ct-margins-output').inner_text()

        for width in (390, 1280):
            page.set_viewport_size({'width': width, 'height': 800})
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1'), width
            assert page.locator('#ct-margins-run').is_visible()
            box = page.locator('#ct-margins-output').bounding_box()
            assert box and box['x'] >= 0 and box['x'] + box['width'] <= width + 1, (width, box)
        assert not errors, errors
        browser.close()
        print('control margins smoke passed')


if __name__ == '__main__':
    main()
