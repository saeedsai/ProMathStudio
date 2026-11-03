"""Uncertainty propagation: references through the real evaluator, Monte Carlo determinism, UI recovery, keyboard, export and responsive layout."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def has_error(locator):
    return "error" in (locator.get_attribute("class") or "")


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/uncertainty-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")

        # API references through the shared MathStudio.numerical.evaluate parser.
        r = page.evaluate("""()=>{const U=MathStudio.uncertainty,v=(name,mean,u)=>({name,mean,u});
          const sum=U.propagate({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)]});
          const prod=U.propagate({expression:'a*b',variables:[v('a',10,0.1),v('b',5,0.2)]});
          const p1=U.propagate({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:1}]}).uc;
          const m1=U.propagate({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],correlations:[{a:'a',b:'b',rho:-1}]}).uc;
          const uni=U.propagate({expression:'x',variables:[{name:'x',mean:0,halfWidth:1,distribution:'uniform'}]}).uc;
          const t0=performance.now(),mc=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],samples:100000,seed:5}),ms=performance.now()-t0;
          const mc2=U.run({expression:'a+b',variables:[v('a',1,0.3),v('b',2,0.4)],samples:100000,seed:5});
          const sq=U.run({expression:'x^2',variables:[v('x',0,1)],samples:100000,seed:3});
          const sinx=U.propagate({expression:'sin(x)*exp(y)',variables:[v('x',0.5,0.01),v('y',1,0.02)]});
          return {sum:sum.uc,prod:prod.uc,p1,m1,uni,mcStd:mc.monteCarlo.std,mcN:mc.monteCarlo.samples,same:mc.monteCarlo.std===mc2.monteCarlo.std&&mc.monteCarlo.mean===mc2.monteCarlo.mean,ms,
            sq:[sq.linear.uc,sq.monteCarlo.mean,sq.monteCarlo.std,sq.comparison.nonlinear],sinx:sinx.uc}}""")
        assert abs(r["sum"] - 0.5) < 1e-9, r
        assert abs(r["prod"] - 2.0615528128088303) < 1e-8, r
        assert abs(r["p1"] - 0.7) < 1e-9 and abs(r["m1"] - 0.1) < 1e-9, r
        assert abs(r["uni"] - 1 / math.sqrt(3)) < 1e-12, r
        assert r["mcN"] == 100000 and abs(r["mcStd"] - 0.5) / 0.5 < 0.01 and r["same"], r
        assert r["ms"] < 8000, r
        assert r["sq"][0] == 0 and abs(r["sq"][1] - 1) < 0.03 and abs(r["sq"][2] - math.sqrt(2)) < 0.05 and r["sq"][3], r
        ref = math.hypot(math.cos(0.5) * math.e * 0.01, math.sin(0.5) * math.e * 0.02)
        assert abs(r["sinx"] - ref) < 1e-8 * max(1, ref), (r["sinx"], ref)
        bad = page.evaluate("""()=>{const U=MathStudio.uncertainty,v=(name,mean,u)=>({name,mean,u}),out=[];
          const tries=[()=>U.propagate({expression:'a+b+c',variables:[v('a',0,1),v('b',0,1),v('c',0,1)],correlations:[{a:'a',b:'b',rho:0.9},{a:'b',b:'c',rho:0.9},{a:'a',b:'c',rho:-0.9}]}),
            ()=>U.propagate({expression:'a+b',variables:[v('a',1,-1),v('b',1,1)]}),()=>U.propagate({expression:'a+q',variables:[v('a',1,1)]}),
            ()=>U.run({expression:'sqrt(x)',variables:[v('x',0.01,1)],samples:1000})];
          for(const f of tries){try{f();out.push(null)}catch(e){out.push(e.message)}}return out}""")
        assert all(bad), bad
        assert "positive semidefinite" in bad[0] and "non-negative" in bad[1], bad

        for width in (1280, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="editor"]').click()
            page.locator("#uncertainty-details").evaluate("e=>{e.open=false;e.open=true;e.scrollIntoView()}")
            page.wait_for_timeout(50)
            out = page.locator("#uncertainty-output")
            assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
            page.locator("#uncertainty-samples").fill("20000")
            page.locator("#uncertainty-run").click()
            text = out.inner_text()
            assert "u_c = 2.0615528" in text and "Monte Carlo · N = 20000" in text and not has_error(out), text
            assert "contribution 94.117647%" in text, text
            label = page.locator("#uncertainty-canvas").get_attribute("aria-label")
            assert page.locator("#uncertainty-canvas").get_attribute("role") == "img" and "20000 samples" in label, label
            assert page.locator("#uncertainty-to-table").is_enabled()
            # Deterministic by seed through the UI.
            page.locator("#uncertainty-run").click()
            assert out.inner_text() == text
            # Error and recovery: negative uncertainty.
            page.locator("#uncertainty-vars .uv-spread").first.fill("-0.1")
            assert page.locator("#uncertainty-to-table").is_disabled()
            page.locator("#uncertainty-run").click()
            assert has_error(out) and "non-negative" in out.inner_text(), out.inner_text()
            assert "not computed" in page.locator("#uncertainty-canvas").get_attribute("aria-label")
            page.locator("#uncertainty-vars .uv-spread").first.fill("0.1")
            # Inconsistent correlation text is rejected, then corrected.
            page.locator("#uncertainty-correlations").fill("a b 2")
            page.locator("#uncertainty-run").click()
            assert has_error(out) and "[−1, 1]" in out.inner_text(), out.inner_text()
            page.locator("#uncertainty-correlations").fill("a b 0.5")
            page.locator("#uncertainty-run").click()
            assert not has_error(out), out.inner_text()
            assert "u_c = " + str(round(math.sqrt(0.25 + 4 + 2 * 0.5 * 0.5 * 2), 6))[:7] in out.inner_text(), out.inner_text()
            page.locator("#uncertainty-correlations").fill("")
            # Add a uniform variable via keyboard and use it in the model.
            page.locator("#uncertainty-add").focus()
            page.keyboard.press("Enter")
            assert page.locator("#uncertainty-vars fieldset").count() == 3
            third = page.locator("#uncertainty-vars fieldset").nth(2)
            third.locator(".uv-dist").select_option("uniform")
            assert "Half-width a" in third.inner_text()
            third.locator(".uv-mean").fill("0")
            third.locator(".uv-spread").fill("1")
            page.locator("#uncertainty-expression").fill("c")
            page.locator("#uncertainty-run").focus()
            page.keyboard.press("Enter")
            assert "u_c = 0.57735027" in out.inner_text() and not has_error(out), out.inner_text()
            # Non-linear model raises the flag.
            page.locator("#uncertainty-expression").fill("c^2")
            third.locator(".uv-dist").select_option("normal")
            page.locator("#uncertainty-run").click()
            assert "NON-LINEARITY FLAG" in out.inner_text(), out.inner_text()
            page.locator("#uncertainty-remove").click()
            assert page.locator("#uncertainty-vars fieldset").count() == 2
            page.locator("#uncertainty-expression").fill("a*b")
            page.locator("#uncertainty-run").click()
            assert not has_error(out)
            sizes = page.evaluate("""()=>[...document.querySelectorAll('#uncertainty-details button,#uncertainty-details input,#uncertainty-details select,#uncertainty-details textarea')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)""")
            assert sizes and min(sizes) >= 40, sizes
            overflow = page.evaluate("()=>{const d=document.getElementById('uncertainty-details').getBoundingClientRect();return document.documentElement.scrollWidth>window.innerWidth+1||d.right>window.innerWidth+1}")
            assert not overflow, width
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#uncertainty-to-table").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            saved = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert saved["name"].startswith("Uncertainty_Summary") and saved["columns"] == ["quantity", "value"], saved
            assert any(row[0] == "MC std" for row in saved["rows"]), saved["rows"]
        assert not errors, errors
        browser.close()
    print("PASS: uncertainty GUM linear/Monte Carlo references, determinism, validation, recovery, keyboard, export and 390/1280 layout")


if __name__ == "__main__":
    main()
