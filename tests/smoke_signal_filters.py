"""Digital filters: convolution/correlation, Butterworth SOS, FIR, filtfilt references, invalid inputs and responsive UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
# Independent references (numpy zpk bilinear transform; equals scipy.signal.butter(4, 0.2) and butter(4, 0.2, 'high')).
LP4_B = [0.004824343357716251, 0.019297373430865003, 0.028946060146297505, 0.019297373430865003, 0.004824343357716251]
LP4_A = [1.0, -2.369513007182037, 2.3139884144158795, -1.0546654058785672, 0.1873794923681848]
HP4_B = [0.4328466449902918, -1.7313865799611672, 2.5970798699417506, -1.7313865799611672, 0.4328466449902918]
LP3_B = [0.018098933007514383, 0.05429679902254315, 0.05429679902254315, 0.018098933007514383]
LP3_A = [1.0, -1.7600418803431692, 1.1828932620378307, -0.27805991763454646]


def near(a, b, tol=1e-9):
    assert abs(a - b) <= tol, (a, b)


def near_list(a, b, tol=1e-9):
    assert len(a) == len(b), (a, b)
    for x, y in zip(a, b):
        near(x, y, tol)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv('CHROMIUM_PATH') or None, args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 850})
        errors = []
        page.on('pageerror', lambda error: errors.append(str(error)))
        page.on('console', lambda msg: errors.append(msg.text) if msg.type == 'error' else None)
        page.set_content((ROOT / 'index.html').read_text(encoding='utf-8'), wait_until='load')
        r = page.evaluate("""() => {
            const F = MathStudio.signalFilters, err = f => {try {f(); return '';} catch(e) {return e.message;}};
            const lp = F.butter({order:4, cutoff:10, sampleRate:100});
            const hp = F.butter({order:4, cutoff:10, sampleRate:100, type:'high'});
            const lp3 = F.butter({order:3, cutoff:5, sampleRate:50});
            const resp = F.freqz(lp, {sampleRate:100, points:501});
            const sine = Array.from({length:500}, (_, i) => Math.sin(2*Math.PI*1*i/100));
            const zp = F.filtfilt(lp, sine), causal = F.apply(lp, sine);
            const lagOf = y => {const c = F.correlate(y.slice(100,400), sine.slice(100,400));
                let best = 0; c.values.forEach((v,i) => {if (v > c.values[best]) best = i;}); return c.lags[best];};
            const step = Array.from({length:12}, (_, i) => i < 4 ? 0 : 1);
            const fir = F.firwin({length:51, cutoff:10, sampleRate:100});
            const firResp = F.freqz(fir, {sampleRate:100, points:101});
            const firHigh = F.firwin({length:51, cutoff:10, sampleRate:100, type:'high', window:'blackman'});
            const band = F.firwin({length:101, cutoff:10, cutoff2:20, sampleRate:100, type:'band', window:'hann'});
            const bandResp = F.freqz(band, {sampleRate:100, points:101});
            const dcSig = Array.from({length:300}, (_, i) => 5 + Math.sin(2*Math.PI*25*i/100));
            const hpOut = F.filtfilt(hp, dcSig);
            const constant = F.filtfilt(lp, Array(100).fill(3));
            const firZp = F.filtfilt(fir, sine);
            return {
                conv: F.convolve([1,2,3],[0,1,0.5]), same: F.convolve([1,2,3],[0,1,0.5],'same'),
                valid: F.convolve([1,2,3,4],[1,1],'valid'),
                corr: F.correlate([1,2,3],[0,1,0.5]), ncorr: F.correlate([1,2,3],[1,2,3],'full',{normalized:true}),
                lpSos: lp.sos, lpB: lp.b, lpA: lp.a, hpB: hp.b, hpA: hp.a, lp3B: lp3.b, lp3A: lp3.a,
                sections: [lp.sos.length, lp3.sos.length],
                dc: resp[0].magnitude, fc: resp[100].magnitude, fcHz: resp[100].frequencyHz, ny: resp[500].magnitude,
                monotone: resp.every((p, i) => i === 0 || p.magnitude <= resp[i-1].magnitude + 1e-15),
                hpDc: F.freqz(hp, {sampleRate:100})[0].magnitude, hpNy: F.freqz(hp, {sampleRate:100}).at(-1).magnitude,
                zpErr: Math.max(...zp.slice(50,450).map((v,i) => Math.abs(v - sine[i+50]))),
                zpLag: lagOf(zp), causalLag: lagOf(causal),
                sosVsBa: Math.max(...F.sosfilt(lp.sos, sine).map((v,i) => Math.abs(v - F.lfilter(lp.b, lp.a, sine)[i]))),
                ma: F.apply(F.movingAverage(4), step),
                maFlat: F.movingAverage(3).b,
                firSum: fir.b.reduce((s,v) => s+v, 0), firSym: fir.b.every((v,i) => Math.abs(v - fir.b[50-i]) < 1e-15),
                firFc: firResp[20].magnitude, firStop: Math.max(...firResp.slice(30).map(p => p.magnitude)),
                firHighNy: F.freqz(firHigh,{sampleRate:100}).at(-1).magnitude, firHighDc: F.freqz(firHigh,{sampleRate:100})[0].magnitude,
                bandCentre: bandResp[30].magnitude, bandDc: bandResp[0].magnitude, bandNy: bandResp[100].magnitude,
                hpMean: hpOut.slice(30,270).reduce((s,v)=>s+v,0)/240,
                constantErr: Math.max(...constant.map(v => Math.abs(v-3))),
                firZpErr: Math.max(...firZp.slice(160,340).map((v,i) => Math.abs(v - sine[i+160]))),
                fftReuse: F.run({data: Array.from({length:64},(_, i) => Math.sin(2*Math.PI*4*i/64)+Math.sin(2*Math.PI*28*i/64)),
                    sampleRate:64, type:'butter-low', order:6, cutoff:10, zeroPhase:true}).spectrum,
                invalid: {
                    nyquist: err(() => F.butter({order:4, cutoff:50, sampleRate:100})),
                    above: err(() => F.firwin({length:31, cutoff:60, sampleRate:100})),
                    order0: err(() => F.butter({order:0, cutoff:10, sampleRate:100})),
                    order9: err(() => F.butter({order:9, cutoff:10, sampleRate:100})),
                    empty: err(() => F.apply(lp, [])),
                    emptyText: err(() => F.parseList('  ')),
                    nonfinite: err(() => F.convolve([1, NaN], [1])),
                    even: err(() => F.firwin({length:30, cutoff:10, sampleRate:100})),
                    long: err(() => F.firwin({length:503, cutoff:10, sampleRate:100})),
                    rate: err(() => F.butter({order:2, cutoff:1, sampleRate:0})),
                    band: err(() => F.firwin({length:31, cutoff:20, cutoff2:10, sampleRate:100, type:'band'})),
                    window: err(() => F.firwin({length:31, cutoff:10, sampleRate:100, window:'kaiser'})),
                    short: err(() => F.filtfilt(lp, Array(15).fill(1))),
                    valid: err(() => F.convolve([1],[1,2],'valid')),
                    mode: err(() => F.convolve([1],[1],'circular')),
                },
            };
        }""")
        near_list(r['conv'], [0, 1, 2.5, 4, 1.5])
        near_list(r['same'], [1, 2.5, 4])
        near_list(r['valid'], [3, 5, 7])
        near_list(r['corr']['values'], [0.5, 2, 3.5, 3, 0])
        assert r['corr']['lags'] == [-2, -1, 0, 1, 2]
        near(r['ncorr']['values'][2], 1)
        near_list(r['lpB'], LP4_B, 1e-12)
        near_list(r['lpA'], LP4_A, 1e-12)
        near_list(r['hpB'], HP4_B, 1e-12)
        near_list(r['hpA'], LP4_A, 1e-12)
        near_list(r['lp3B'], LP3_B, 1e-12)
        near_list(r['lp3A'], LP3_A, 1e-12)
        assert r['sections'] == [2, 2]
        assert all(len(s) == 6 and s[3] == 1 for s in r['lpSos'])
        near(r['dc'], 1)
        near(r['fcHz'], 10)
        near(r['fc'], 1 / math.sqrt(2))
        assert r['ny'] < 1e-12 and r['monotone']
        near(r['hpDc'], 0, 1e-12)
        near(r['hpNy'], 1)
        assert r['zpErr'] < 1e-3, r['zpErr']
        assert r['zpLag'] == 0 and r['causalLag'] > 0, (r['zpLag'], r['causalLag'])
        assert r['sosVsBa'] < 1e-10
        near_list(r['ma'], [0, 0, 0, 0, .25, .5, .75, 1, 1, 1, 1, 1])
        near_list(r['maFlat'], [1/3] * 3)
        near(r['firSum'], 1, 1e-12)
        assert r['firSym']
        assert 0.4 < r['firFc'] < 0.6 and r['firStop'] < 0.01, (r['firFc'], r['firStop'])
        near(r['firHighNy'], 1, 1e-12)
        assert r['firHighDc'] < 1e-3
        near(r['bandCentre'], 1, 1e-6)
        assert r['bandDc'] < 1e-3 and r['bandNy'] < 1e-3
        assert abs(r['hpMean']) < 1e-3, r['hpMean']
        assert r['constantErr'] < 1e-9
        # Zero-phase FIR scales a 1 Hz sine by |H(1 Hz)|^2 = 0.99765520501678^2 (numpy reference).
        near(r['firZpErr'], 0.004684091902919851, 1e-6)
        spec = r['fftReuse']
        assert spec and spec['inputPeak']['frequencyHz'] in (4, 28)
        assert spec['outputPeak']['frequencyHz'] == 4
        near(spec['output'][4]['amplitude'], 1, 1e-2)
        assert spec['output'][28]['amplitude'] < 1e-2
        inv = r['invalid']
        assert 'Nyquist' in inv['nyquist'] and 'Nyquist' in inv['above'], inv
        assert '1 to 8' in inv['order0'] and '1 to 8' in inv['order9'], inv
        assert 'at least' in inv['empty'] and 'empty' in inv['emptyText'], inv
        assert 'finite' in inv['nonfinite'] and 'odd' in inv['even'] and '501' in inv['long'], inv
        assert 'Sample rate' in inv['rate'] and 'Upper cutoff' in inv['band'] and 'Window' in inv['window'], inv
        assert 'padlen' in inv['short'] and 'Valid mode' in inv['valid'] and 'mode' in inv['mode'], inv

        # UI: typed list, Butterworth zero-phase, plot, save, error recovery, keyboard.
        page.locator('[data-workspace="editor"]').click()
        details = page.locator('#filters-details')
        assert details.evaluate('e => e.parentElement === document.getElementById("fft-details").parentElement')
        details.locator('summary').focus()
        page.keyboard.press('Enter')
        assert details.evaluate('e => e.open')
        assert page.locator('#flt-order').is_visible() and not page.locator('#flt-window').is_visible()
        page.locator('#flt-run').click()
        out = page.locator('#flt-output')
        text = out.inner_text()
        assert 'Butterworth IIR low-pass' in text and 'zero-phase' in text and '200 samples' in text, text
        assert 'Order 4' in text and '|H| at DC 1' in text, text
        assert '200 input samples' in page.locator('#flt-canvas').get_attribute('aria-label')
        assert page.locator('#flt-to-table').is_enabled()
        page.locator('#flt-to-table').click()
        table = page.evaluate('MathStudio.dataTables.active')
        assert table['columns'] == ['index', 'time_s', 'input', 'filtered'] and len(table['rows']) == 200
        tid = table['id']
        page.locator('[data-workspace="editor"]').click()
        details.evaluate('e => e.open = true')
        page.locator('#flt-cutoff').fill('60')
        assert page.locator('#flt-to-table').is_disabled()
        page.locator('#flt-run').click()
        assert 'error' in out.get_attribute('class') and 'Nyquist' in out.inner_text()
        page.locator('#flt-cutoff').fill('10')
        page.locator('#flt-type').select_option('fir-band')
        assert page.locator('#flt-window').is_visible() and page.locator('#flt-cutoff2').is_visible()
        assert not page.locator('#flt-order').is_visible()
        page.locator('#flt-source').select_option('table')
        page.locator('#flt-table').select_option(tid)
        page.locator('#flt-column').select_option('3')
        page.locator('#flt-mode').select_option('lfilter')
        page.locator('#flt-run').focus()
        page.keyboard.press('Enter')
        text = out.inner_text()
        assert 'error' not in (out.get_attribute('class') or ''), text
        assert 'band-pass' in text and 'causal' in text and 'column "filtered"' in text, text
        page.locator('#flt-type').select_option('moving-average')
        assert page.locator('#flt-length').input_value() == '5'
        assert not page.locator('#flt-cutoff').is_visible()
        page.locator('#flt-run').click()
        assert 'Moving-average' in out.inner_text()

        for width in (390, 1280):
            page.set_viewport_size({'width': width, 'height': 844})
            overflow = page.evaluate("""() => {
                const d = document.getElementById('filters-details'), r = d.getBoundingClientRect();
                const small = [...d.querySelectorAll('button,select,input')].filter(e => e.offsetParent && e.getBoundingClientRect().height < 40);
                return {page: document.documentElement.scrollWidth - window.innerWidth,
                        panel: r.right - window.innerWidth,
                        canvas: document.getElementById('flt-canvas').getBoundingClientRect().right - window.innerWidth,
                        small: small.map(e => e.id)};
            }""")
            assert overflow['panel'] <= 1 and overflow['canvas'] <= 1, (width, overflow)
            assert not overflow['small'], (width, overflow)
        assert not errors, errors
        browser.close()
    print('PASS signal filters: convolution, Butterworth SOS/BA references, |H(fc)|=1/sqrt2, filtfilt zero phase, FIR, MA, invalid inputs, UI 390/1280')


if __name__ == '__main__':
    main()
