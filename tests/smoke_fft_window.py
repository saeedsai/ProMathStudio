"""Periodic Hann FFT window: coherent gain, leakage, bounds and UI export."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def near(a, b, tol=1e-9):
    assert abs(a-b) <= tol, (a, b)

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None,
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.set_content((ROOT/'index.html').read_text(encoding='utf-8'), wait_until='load')
        results = page.evaluate("""() => {
            const f = MathStudio.fftTools, n = 32;
            const signal = Array.from({length:n},(_,i)=>Math.sin(2*Math.PI*5*i/n));
            const original = signal.slice();
            return {
                hann:f.analyze(signal,32,'hann'),
                rectangular:f.analyze(signal,32),
                dc:f.analyze(Array(n).fill(3),32,'hann'),
                nyquist:f.analyze(Array.from({length:n},(_,i)=>i%2?-1:1),32,'hann'),
                unchanged:signal.every((x,i)=>x===original[i]),
                invalid:['hamming','HANN','',null,true,0].map(w=>{
                    try {f.analyze(signal,32,w);return '';} catch(e){return e.message;}
                }),
                oversized:(()=>{try {
                    f.analyze([1e10,...Array(n-1).fill(0)],32,'hann');
                    return '';
                }catch(e){return e.message;}})()
            };
        }""")
        h, r = results['hann'], results['rectangular']
        assert results['unchanged']
        assert all('Window must' in msg for msg in results['invalid'])
        assert '1e9' in results['oversized']
        assert h['window'] == 'hann' and r['window'] == 'rectangular'
        near(h['coherentGain'], 0.5)
        near(r['coherentGain'], 1)
        near(h['spectrum'][5]['amplitude'], 1)
        near(h['spectrum'][4]['amplitude'], 0.5)
        near(h['spectrum'][6]['amplitude'], 0.5)
        near(h['spectrum'][9]['amplitude'], 0, 1e-10)
        near(r['spectrum'][5]['amplitude'], 1)
        near(r['spectrum'][4]['amplitude'], 0)
        near(results['dc']['spectrum'][0]['amplitude'], 3)
        near(results['nyquist']['spectrum'][16]['amplitude'], 1)
        assert h['maxError'] < 1e-11
        near(h['windowedSamples'][0], 0)
        assert len(h['samples']) == 32 and len(h['windowedSamples']) == 32
        page.locator('[data-workspace="editor"]').click()
        page.locator('#fft-details').evaluate('(e)=>e.open=true')
        page.locator('#fft-window').select_option('hann')
        page.locator('#fft-samples').fill(','.join(
            str(math.sin(2*math.pi*5*i/32)) for i in range(32)))
        page.locator('#fft-rate').fill('32')
        page.locator('#fft-run').click()
        output = page.locator('#fft-output').inner_text()
        assert 'Peak bin 5' in output and 'Window hann' in output, output
        assert 'coherent gain 0.500000' in output, output
        assert page.locator('#fft-to-table').is_enabled()
        page.locator('#fft-to-table').click()
        table = page.evaluate('MathStudio.dataTables.active')
        assert table['columns'][:3] == ['bin','frequency_Hz','amplitude']
        near(float(table['rows'][5][2]), 1)
        page.locator('[data-workspace="editor"]').click()
        page.locator('#fft-details').evaluate('(e)=>e.open=true')
        page.locator('#fft-window').select_option('rectangular')
        assert page.locator('#fft-to-table').is_disabled()
        assert page.locator('#fft-to-graph').is_disabled()
        page.locator('#fft-run').click()
        assert 'Window rectangular' in page.locator('#fft-output').inner_text()
        page.set_viewport_size({'width': 390, 'height': 844})
        assert page.locator('#fft-window').is_visible()
        assert not errors, errors
        browser.close()
    print('PASS Hann FFT coherent gain, leakage, DC/Nyquist, invalid bounds, UI and table')

if __name__ == '__main__':
    main()
