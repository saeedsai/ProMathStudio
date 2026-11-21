"""Hypothesis tests and confidence intervals: browser API references, Data Tables input, UI recovery, export and 390/1280 layout."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def has_error(locator):
    return "error" in (locator.get_attribute("class") or "")


def close(a, b, tol=1e-9):
    assert abs(a - b) <= tol * max(1.0, abs(b)), (a, b)


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/statistics-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        ht = lambda test, o: page.evaluate("([t,o])=>MathStudio.statistics.hypothesisTest(t,o)", [test, o])

        # Browser API references (scipy 1.x values).
        r = ht("t1", {"x": [5.1, 4.9, 5.6, 5.8, 6.0, 5.2], "mu": 5})
        close(r["statistic"], 2.456769074559979, 1e-12); close(r["pValue"], 0.057456265269132285, 1e-8)
        assert r["df"] == 5
        close(r["ci"][0], 4.97992531587776, 1e-10); close(r["ci"][1], 5.886741350788907, 1e-10)
        r = ht("welch", {"x": [1, 2, 3, 4, 5], "y": [2, 4, 6, 8, 10]})
        close(r["statistic"], -1.8973665961010275, 1e-12); close(r["df"], 5.882352941176471, 1e-12); close(r["pValue"], 0.10753119493062728, 1e-8)
        r = ht("independence", {"table": [[10, 20], [20, 40]]})
        assert r["statistic"] == 0 and r["pValue"] == 1 and r["df"] == 1, r
        r = ht("gof", {"x": [16, 18, 16, 14, 12, 12]})
        close(r["statistic"], 2.0, 1e-14); close(r["pValue"], 0.8491450360846096, 1e-8)
        r = ht("prop", {"k": 81, "n": 263, "p0": 0.25})
        close(r["ci"][0], 0.2552885198782742, 1e-10); close(r["ci"][1], 0.36620957698280004, 1e-10)
        r = ht("binom", {"k": 7, "n": 20, "p0": 0.5})
        close(r["pValue"], 0.26317596435546875, 1e-8)
        for test, o in [("t1", {"x": [1]}), ("t1", {"x": [2, 2, 2]}), ("gof", {"x": [3, -1, 4]}), ("gof", {"x": [3, 1], "y": [0, 1]}),
                        ("binom", {"k": 3, "n": 10, "p0": 1}), ("prop", {"k": 3, "n": 10, "p0": 0}), ("independence", {"table": [[0, 0], [3, 4]]})]:
            assert page.evaluate("([t,o])=>{try{MathStudio.statistics.hypothesisTest(t,o);return false}catch(e){return !!e.message}}", [test, o]), (test, o)

        page.evaluate("""()=>MathStudio.dataTables.importData({headers:['label','before','after'],rows:[['a','1','2'],['b','2','4'],['c','3','6'],['d','4','8'],['e','5.5','10'],['','','']]},'HTInput')""")
        for width in (1280, 390):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator('[data-workspace="editor"]').click()
            page.locator("#stats-details").evaluate("e=>{e.open=false;e.open=true}")
            page.wait_for_timeout(50)
            out = page.locator("#stats-output")
            run = page.locator("#stats-ht-run")
            page.select_option("#stats-test", "t1")
            run.click()
            text = out.inner_text()
            assert "One-sample t-test" in text and "t statistic = 2.45676907456" in text and "p-value (two-sided) = 0.0574562652691" in text and "Assumptions:" in text, text
            assert not has_error(out) and page.locator("#stats-to-table").is_enabled()
            # Negative input then recovery.
            page.locator("#stats-ht-a").fill("4, 4, 4")
            assert page.locator("#stats-to-table").is_disabled()
            run.click()
            assert "zero variance" in out.inner_text() and has_error(out)
            page.locator("#stats-ht-a").fill("1, abc")
            run.click()
            assert "not a finite number" in out.inner_text() and has_error(out)
            page.select_option("#stats-test", "welch")
            assert page.locator("#stats-ht-b-label").is_visible() and page.locator("#stats-ht-k-label").is_hidden()
            run.click()
            assert "Welch two-sample t-test" in out.inner_text() and "Degrees of freedom = 5.88235294118" in out.inner_text() and not has_error(out), out.inner_text()
            # Data Tables source: paired t-test on complete pairs.
            page.select_option("#stats-test", "paired")
            page.select_option("#stats-ht-source", "table")
            page.select_option("#stats-table", "HTInput")
            page.select_option("#stats-column", "before")
            page.select_option("#stats-column2", "after")
            run.click()
            text = out.inner_text()
            assert "Paired t-test" in text and "t statistic = -4.52903909477" in text and "n = 5" in text, text
            page.select_option("#stats-test", "independence")
            assert page.locator("#stats-ht-yates-label").is_visible() and page.locator("#stats-ht-alt-label").is_hidden()
            page.select_option("#stats-ht-source", "typed")
            page.locator("#stats-ht-a").fill("3, 1; 2, 4")
            run.click()
            assert "Warning:" in out.inner_text() and "below 5" in out.inner_text() and not has_error(out), out.inner_text()
            page.locator("#stats-ht-a").fill("0, 0; 2, 4")
            run.click()
            assert "expected count of 0" in out.inner_text() and has_error(out)
            page.select_option("#stats-test", "binom")
            assert page.locator("#stats-ht-a-label").is_hidden() and page.locator("#stats-ht-k-label").is_visible()
            page.locator("#stats-ht-param").fill("1.5")
            run.click()
            assert "strictly between 0 and 1" in out.inner_text() and has_error(out)
            page.locator("#stats-ht-param").fill("0.5")
            run.click()
            text = out.inner_text()
            assert "Exact binomial test" in text and "p-value (two-sided) = 0.263175964355" in text and "Clopper–Pearson" in text and not has_error(out), text
            sizes = page.evaluate("""()=>[...document.querySelectorAll('#stats-details button,#stats-details input,#stats-details select')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)""")
            assert sizes and min(sizes) >= 40, sizes
            overflow = page.evaluate("()=>{const d=document.getElementById('stats-details').getBoundingClientRect();return document.documentElement.scrollWidth>window.innerWidth+1||d.right>window.innerWidth+1}")
            assert not overflow, width
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#stats-to-table").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            saved = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert saved["name"].startswith("Statistics_HypothesisTest") and saved["columns"] == ["quantity", "value"], saved
            keys = [row[0] for row in saved["rows"]]
            assert "p_value" in keys and "ci_lower" in keys and "assumptions" in keys, keys
        assert not errors, errors
        browser.close()
    print("PASS: hypothesis tests and confidence intervals, Data Tables input, validation, recovery, export and 390/1280 layout")


if __name__ == "__main__":
    main()
