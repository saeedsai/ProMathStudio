"""Statistics distributions and descriptive statistics: references, validation, UI recovery, export and responsive layout."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def has_error(locator):
    return "error" in (locator.get_attribute("class") or "")


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/statistics-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(html, wait_until="load")
        ev = lambda o: page.evaluate("o=>MathStudio.statistics.evaluate(o)", o)
        n = ev({"dist": "normal", "params": {"mu": 0, "sigma": 1}, "x": 1.96, "p": 0.975})
        assert abs(n["cdf"] - 0.9750021048517795) < 1e-14 and abs(n["quantile"] - 1.959963984540054) < 1e-12, n
        t = ev({"dist": "t", "params": {"nu": 10}, "x": 2.228138851986, "p": 0.975})
        assert abs(t["cdf"] - 0.975) < 1e-11 and abs(t["quantile"] - 2.228138851986) < 1e-11, t
        c = ev({"dist": "chisquare", "params": {"k": 10}, "p": 0.95})
        assert abs(c["quantile"] - 18.307038053275146) < 1e-10, c
        c2 = ev({"dist": "chisquare", "params": {"k": 2}, "x": 3})
        assert abs(c2["cdf"] - (1 - 2.718281828459045 ** -1.5)) < 1e-14, c2
        e = ev({"dist": "exponential", "params": {"lambda": 2}, "p": 0.5})
        assert abs(e["quantile"] - 0.34657359027997264) < 1e-14, e
        b = ev({"dist": "binomial", "params": {"n": 10, "p": 0.3}, "x": 3, "p": 0.65})
        assert abs(b["cdf"] - 0.6496107184) < 1e-10 and b["quantile"] == 4, b
        po = ev({"dist": "poisson", "params": {"lambda": 4}, "x": 2, "p": 0.5})
        assert abs(po["density"] - 0.14652511110987343) < 1e-14 and po["quantile"] == 4, po
        invalid = [{"dist": "normal", "params": {"sigma": 0}, "x": 1}, {"dist": "binomial", "params": {"n": 5, "p": 1.2}, "x": 1},
                   {"dist": "t", "params": {"nu": 0}, "x": 1}, {"dist": "normal", "params": {}, "p": 2},
                   {"dist": "normal", "params": {}, "x": "", "p": ""}, {"dist": "bogus", "x": 1}]
        for o in invalid:
            assert page.evaluate("o=>{try{MathStudio.statistics.evaluate(o);return false}catch(e){return !!e.message}}", o), o

        # Descriptive statistics through Data Tables, including formula, blank and text cells.
        page.evaluate("""()=>MathStudio.dataTables.importData({headers:['a','b'],rows:[['1','2'],['2','4'],['3','6'],['4','8.5'],['','x'],['text','1'],['=A1+A4','']]},'StatsInput')""")
        r = page.evaluate("()=>MathStudio.statistics.describeTable({table:'StatsInput',column:'a',column2:'b'})")
        f = r["first"]
        assert (f["n"], f["blank"], f["nonNumeric"], f["median"], f["q1"], f["q3"]) == (5, 1, 1, 3, 2, 4), f
        assert abs(f["mean"] - 3) < 1e-15 and abs(f["sampleVariance"] - 2.5) < 1e-14 and abs(f["populationVariance"] - 2) < 1e-14, f
        assert abs(f["skewness"]) < 1e-14, f
        assert r["pair"]["pairs"] == 4 and abs(r["pair"]["pearson"] - 0.99838143945703) < 1e-12 and abs(r["pair"]["covariance"] - 3.5833333333333335) < 1e-13, r
        page.evaluate("""()=>MathStudio.dataTables.importData({headers:['empty'],rows:[[''],['abc']]},'StatsEmpty')""")
        assert page.evaluate("()=>{try{MathStudio.statistics.describeTable({table:'StatsEmpty',column:'empty'});return false}catch(e){return /no numeric/.test(e.message)}}")

        for width in (1280, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="editor"]').click()
            page.locator("#stats-details").evaluate("e=>{e.open=false;e.open=true}")
            page.wait_for_timeout(50)
            out = page.locator("#stats-output")
            page.select_option("#stats-dist", "normal")
            page.locator("#stats-dist-run").click()
            assert "0.975002104852" in out.inner_text() and "1.95996398454" in out.inner_text(), out.inner_text()
            assert page.locator("#stats-to-table").is_enabled()
            page.locator("#stats-param2").fill("-1")
            assert page.locator("#stats-to-table").is_disabled()
            page.locator("#stats-dist-run").click()
            assert "Standard deviation" in out.inner_text() and has_error(out)
            assert page.locator("#stats-to-table").is_disabled()
            page.select_option("#stats-dist", "binomial")
            assert page.locator("#stats-param2-name").inner_text() == "Success probability p"
            page.locator("#stats-dist-run").click()
            assert "P(X ≤ 3) = 0.6496107184" in out.inner_text() and not has_error(out), out.inner_text()
            page.select_option("#stats-dist", "poisson")
            assert page.locator("#stats-param2-label").is_hidden()
            page.select_option("#stats-table", "StatsInput")
            page.select_option("#stats-column", "a")
            page.select_option("#stats-column2", "b")
            page.locator("#stats-desc-run").click()
            text = out.inner_text()
            assert "Median: 3 | 4" in text and "Pearson r: 0.998381439457" in text and "Non-numeric cells ignored: 1 | 1" in text, text
            page.select_option("#stats-column2", "a")
            page.locator("#stats-desc-run").click()
            assert "different columns" in out.inner_text() and has_error(out)
            page.select_option("#stats-column2", "")
            page.locator("#stats-desc-run").click()
            assert not has_error(out) and "Q1 (type 7): 2" in out.inner_text(), out.inner_text()
            sizes = page.evaluate("""()=>[...document.querySelectorAll('#stats-details button,#stats-details input,#stats-details select')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)""")
            assert sizes and min(sizes) >= 40, sizes
            overflow = page.evaluate("()=>{const d=document.getElementById('stats-details').getBoundingClientRect();return document.documentElement.scrollWidth>window.innerWidth+1||d.right>window.innerWidth+1}")
            assert not overflow, width
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#stats-to-table").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            saved = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert saved["name"].startswith("Statistics_Descriptive") and saved["columns"] == ["statistic", "a"], saved
        assert not errors, errors
        browser.close()
    print("PASS: statistics distributions, descriptive stats, validation, recovery, export and 390/1280 layout")


if __name__ == "__main__":
    main()
