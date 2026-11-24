"""Seeded random tools: Monte Carlo/Halton references through the real evaluator, validation, UI recovery, keyboard, export and 390/1280 layout."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def has_error(locator):
    return "error" in (locator.get_attribute("class") or "")


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/random-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")

        r = page.evaluate("""()=>{const R=MathStudio.random,S=MathStudio.statistics;
          const g=R.pcg32(42,54),first=[g.u32(),g.u32(),g.u32()];
          const xy=R.integrate({expression:'x*y',n:10000,seed:7}),xy1=R.integrate({expression:'x1*x2',n:10000,seed:7});
          const smooth='exp(x+y)',mc=R.integrate({expression:smooth,n:10000,seed:7}),hal=R.integrate({expression:smooth,n:10000,method:'halton'}),sh=R.integrate({expression:smooth,n:10000,method:'halton-shift',seed:7});
          const pi=R.integrate({expression:'4*(x^2+y^2<1)',n:100000,seed:11});
          const d3=R.integrate({expression:'x1*x2*x3',dimension:3,lower:'0',upper:'2',n:20000,method:'halton'});
          const t0=performance.now(),conv=R.convergence({expression:'x*y',seed:3,budgetMs:3000}),ms=performance.now()-t0;
          const norm=R.sample({distribution:'normal',params:{mu:2,sigma:3},n:100000,seed:5}),st=S.describe(norm.values);
          const pois=R.sample({distribution:'poisson',params:{lambda:3},n:20000,seed:6}).values,c=new Array(10).fill(0);for(const v of pois)c[Math.min(9,v)]++;
          const pmf=k=>Math.exp(-3+k*Math.log(3)-S.logGamma(k+1)),p=Array.from({length:10},(_,k)=>pmf(k));p[9]=1-p.slice(0,9).reduce((s,x)=>s+x,0);
          return {first,xy:[xy.estimate,xy.standardError],same:xy.estimate===xy1.estimate,mc:mc.estimate,hal:hal.estimate,sh:sh.estimate,pi:[pi.estimate,pi.standardError],d3:d3.estimate,
            conv:conv.rows.map(x=>x.n),truncated:conv.truncated,ms,norm:[st.mean,st.sampleVariance],gof:S.chisqGof(c,p).pValue}}""")
        assert r["first"] == [0xA15C02B7, 0x7B47F409, 0xBA1D3330], r["first"]
        assert abs(r["xy"][0] - 0.25) < 3 * r["xy"][1] and r["same"], r
        exact = (math.e - 1) ** 2
        assert abs(r["hal"] - exact) < abs(r["mc"] - exact), (r["hal"], r["mc"], exact)
        assert abs(r["sh"] - exact) < abs(r["mc"] - exact), (r["sh"], r["mc"], exact)
        assert abs(r["pi"][0] - math.pi) < 3 * r["pi"][1], r["pi"]
        assert abs(r["d3"] - 8) / 8 < 0.01, r["d3"]
        assert r["conv"][:3] == [100, 1000, 10000] and r["ms"] < 6000, r
        assert abs(r["norm"][0] - 2) < 5 * 3 / math.sqrt(1e5) and abs(r["norm"][1] - 9) / 9 < 0.03, r["norm"]
        assert r["gof"] > 0.001, r["gof"]
        bad = page.evaluate("""()=>{const R=MathStudio.random,out={};const t={
            sigma:()=>R.sample({distribution:'normal',params:{mu:0,sigma:-1}}),p:()=>R.sample({distribution:'binomial',params:{n:5,p:-0.1}}),
            N:()=>R.sample({n:100001}),d:()=>R.integrate({expression:'x1',dimension:7}),unknown:()=>R.integrate({expression:'x1*x3',dimension:2}),
            pole:()=>R.integrate({expression:'1/x',dimension:1,lower:-1,upper:1,method:'halton',n:1000})};
          for(const [k,f] of Object.entries(t)){try{f();out[k]=null}catch(e){out[k]=e.message}}return out}""")
        assert all(bad.values()), bad
        assert "σ must be positive" in bad["sigma"] and "[0, 1]" in bad["p"] and "100000" in bad["N"] and "1 to 6" in bad["d"], bad
        assert "Integrand undefined" in bad["unknown"] and "Integrand undefined" in bad["pole"], bad

        for width in (1280, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="editor"]').click()
            page.locator("#random-details").evaluate("e=>{e.open=false;e.open=true;e.scrollIntoView()}")
            page.wait_for_timeout(50)
            out, mc_out, canvas = page.locator("#random-output"), page.locator("#random-mc-output"), page.locator("#random-canvas")
            for o in (out, mc_out):
                assert o.get_attribute("role") == "status" and o.get_attribute("aria-live") == "polite"
            assert canvas.get_attribute("role") == "img"
            page.locator("#random-distribution").select_option("normal")
            page.locator("#random-n").fill("5000")
            page.locator("#random-seed").fill("12345")
            page.locator("#random-generate").click()
            text = out.inner_text()
            assert "Normal" in text and "N = 5000" in text and "theory 0" in text and not has_error(out), text
            assert "5000" in canvas.get_attribute("aria-label"), canvas.get_attribute("aria-label")
            page.locator("#random-generate").click()
            assert out.inner_text() == text  # deterministic by seed through the UI
            # Invalid σ: error class, disabled export, then recovery.
            page.locator("#random-p2").fill("0")
            assert page.locator("#random-to-table").is_disabled()
            page.locator("#random-generate").click()
            assert has_error(out) and "σ must be positive" in out.inner_text(), out.inner_text()
            assert "input error" in canvas.get_attribute("aria-label")
            page.locator("#random-p2").fill("1")
            page.locator("#random-generate").click()
            assert not has_error(out) and out.inner_text() == text
            # Binomial with invalid p, chosen by keyboard.
            page.locator("#random-distribution").focus()
            page.locator("#random-distribution").select_option("binomial")
            assert "Success probability p" in page.locator("#random-p2-label").inner_text()
            page.locator("#random-p2").fill("1.5")
            page.locator("#random-generate").focus()
            page.keyboard.press("Enter")
            assert has_error(out) and "[0, 1]" in out.inner_text(), out.inner_text()
            page.locator("#random-p2").fill("0.3")
            page.keyboard.press("Tab")
            page.locator("#random-generate").focus()
            page.keyboard.press("Enter")
            assert not has_error(out) and "theory 3" in out.inner_text(), out.inner_text()
            page.locator("#random-n").fill("100001")
            page.locator("#random-generate").click()
            assert has_error(out) and "1 to 100000" in out.inner_text(), out.inner_text()
            # Large sample export wraps into ≤6,000-row columns.
            page.locator("#random-distribution").select_option("exponential")
            assert page.locator("#random-p2-label").is_hidden()
            page.locator("#random-n").fill("13000")
            page.locator("#random-generate").click()
            assert not has_error(out), out.inner_text()
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#random-to-table").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            saved = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert saved["name"].startswith("Random_exponential") and saved["columns"] == ["value_1", "value_2", "value_3"] and len(saved["rows"]) == 6000, saved["columns"]
            page.locator('[data-workspace="editor"]').click()
            page.locator("#random-details").evaluate("e=>{e.open=true;e.scrollIntoView()}")

            # Monte Carlo integration through the UI.
            page.locator("#random-mc-expression").fill("x1*x2")
            page.locator("#random-mc-dimension").fill("2")
            page.locator("#random-mc-n").fill("10000")
            page.locator("#random-mc-method").select_option("mc")
            page.locator("#random-mc-run").click()
            t = mc_out.inner_text()
            assert "∫ ≈ 0.25" in t and "(1 SE)" in t and not has_error(mc_out), t
            page.locator("#random-mc-dimension").fill("7")
            page.locator("#random-mc-run").click()
            assert has_error(mc_out) and "1 to 6" in mc_out.inner_text(), mc_out.inner_text()
            page.locator("#random-mc-dimension").fill("2")
            page.locator("#random-mc-method").select_option("halton")
            page.locator("#random-mc-run").focus()
            page.keyboard.press("Enter")
            assert "∫ ≈ 0.24" in mc_out.inner_text() and "no standard error" in mc_out.inner_text() and not has_error(mc_out), mc_out.inner_text()
            page.locator("#random-mc-convergence").click()
            ct = mc_out.inner_text()
            assert "N | plain MC" in ct and "\n100 |" in ct and "\n10000 |" in ct and not has_error(mc_out), ct
            assert page.locator("#random-mc-to-table").is_enabled()
            page.locator("#random-mc-to-table").click()
            conv = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert conv["name"].startswith("MC_Convergence") and conv["columns"] == ["N", "plain_MC", "standard_error", "Halton"], conv
            page.locator('[data-workspace="editor"]').click()
            page.locator("#random-details").evaluate("e=>{e.open=true;e.scrollIntoView()}")

            sizes = page.evaluate("""()=>[...document.querySelectorAll('#random-details button,#random-details input,#random-details select')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)""")
            assert sizes and min(sizes) >= 40, sizes
            overflow = page.evaluate("()=>{const d=document.getElementById('random-details').getBoundingClientRect();return document.documentElement.scrollWidth>window.innerWidth+1||d.right>window.innerWidth+1}")
            assert not overflow, width
        assert not errors, errors
        browser.close()
    print("PASS: random sampling (PCG32), MC/Halton integration references, validation, recovery, keyboard, export and 390/1280 layout")


if __name__ == "__main__":
    main()
