"""Multivariate analysis browser regression: references, determinism, validation, recovery, keyboard, export, 390/1280 layout."""
from pathlib import Path
import math
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def has_error(locator):
    return "error" in (locator.get_attribute("class") or "")


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/multivariate-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    assert "python tests/smoke_multivariate_tools.py" in (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        area = page.locator("#data-panel #multivariate-details")
        assert area.count() == 1

        # API references in the real bundle (including Data Tables formulas through calculate()).
        r = page.evaluate("""()=>{const V=MathStudio.multivariate,T=MathStudio.dataTables;
          T.create('MV_Data',['x','y','z','label'],[['1','2','10','a'],['2','4','7','b'],['3','=A3*2+1','9','c'],['4','8','3','d'],['5','9','1','e'],['','1','1','f'],['oops','2','2','g']]);
          const c=V.analyze({table:'MV_Data',columns:['x','y','z'],analysis:'correlation'});
          const p=V.pca([[1,2],[2,4],[3,6],[4,8]]);
          const a=V.kmeans([[0,0],[0.1,0],[0,0.1],[9,9],[9.1,9],[9,9.1]],{k:2,seed:3}),b=V.kmeans([[0,0],[0.1,0],[0,0.1],[9,9],[9.1,9],[9,9.1]],{k:2,seed:3});
          return {n:c.n,dropped:c.dropped,cov:c.covariance,pearson:c.pearson[0][1],expl:p.explained,labels:a.labels,same:JSON.stringify(a)===JSON.stringify(b)};}""")
        assert r["n"] == 5 and r["dropped"] == 2, r
        assert abs(r["cov"][0][1] - 4.5) < 1e-12 and abs(r["cov"][2][2] - 15) < 1e-12, r
        assert abs(r["pearson"] - 4.5 / math.sqrt(2.5 * 8.5)) < 1e-12, r
        assert abs(r["expl"][0] - 1) < 1e-12 and abs(r["expl"][1]) < 1e-12, r
        assert r["labels"] == [1, 1, 1, 2, 2, 2] and r["same"], r

        page.locator('[data-workspace="data"]').first.click()
        for width in (1280, 390):
            page.set_viewport_size({"width": width, "height": 844})
            area.evaluate("e=>{e.open=false;e.open=true;e.scrollIntoView()}")
            page.wait_for_timeout(50)
            page.locator("#mv-table").select_option("MV_Data")
            out = page.locator("#mv-output")
            assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
            boxes = page.locator("#mv-column-list input.mv-col")
            assert boxes.count() == 4
            boxes.nth(3).uncheck()  # text column
            page.locator("#mv-analysis").select_option("correlation")
            page.locator("#mv-run").click()
            text = out.inner_text()
            assert not has_error(out), text
            assert "5 complete row(s) used, 2 dropped" in text and "Pearson correlation" in text and "Spearman" in text, text
            canvas = page.locator("#mv-canvas")
            label = canvas.get_attribute("aria-label")
            assert canvas.get_attribute("role") == "img" and "Scatter matrix of 5 rows across 3 columns" in label, label
            assert canvas.is_visible()
            assert page.locator("#mv-save").is_enabled()
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#mv-save").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            saved = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert saved["name"].startswith("Multivariate_Correlation") and saved["columns"] == ["matrix", "variable", "x", "y", "z"], saved
            assert len(saved["rows"]) == 9 and float(saved["rows"][0][2]) == 2.5, saved["rows"]
            area.evaluate("e=>e.scrollIntoView()")
            page.locator("#mv-table").select_option("MV_Data")
            boxes = page.locator("#mv-column-list input.mv-col")
            if boxes.nth(3).is_checked():
                boxes.nth(3).uncheck()

            # Error and recovery: a text column makes every row non-numeric.
            boxes.nth(3).check()
            assert page.locator("#mv-save").is_disabled()
            page.locator("#mv-run").click()
            assert has_error(out) and "At least 2 complete numeric rows" in out.inner_text(), out.inner_text()
            boxes.nth(3).uncheck()
            boxes.nth(1).uncheck(); boxes.nth(2).uncheck()
            page.locator("#mv-run").click()
            assert has_error(out) and "between 2 and 12" in out.inner_text(), out.inner_text()
            boxes.nth(1).check(); boxes.nth(2).check()

            # PCA via keyboard.
            page.locator("#mv-analysis").select_option("pca")
            assert page.locator("#mv-scaling-label").is_visible() and not page.locator("#mv-k-label").is_visible()
            page.locator("#mv-run").focus()
            page.keyboard.press("Enter")
            text = out.inner_text()
            assert not has_error(out) and "PC1: eigenvalue" in text and "cumulative 100%" in text, text
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#mv-save").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 2
            scores = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert scores["name"].startswith("PCA_Scores") and scores["columns"] == ["row", "PC1", "PC2", "PC3"] and len(scores["rows"]) == 5, scores
            assert [row[0] for row in scores["rows"]] == ["1", "2", "3", "4", "5"], scores["rows"]
            area.evaluate("e=>e.scrollIntoView()")
            page.locator("#mv-table").select_option("MV_Data")
            boxes = page.locator("#mv-column-list input.mv-col")
            if boxes.nth(3).is_checked():
                boxes.nth(3).uncheck()

            # k-means: invalid k then recovery, deterministic by seed, labels exported.
            page.locator("#mv-analysis").select_option("kmeans")
            page.locator("#mv-k").fill("6")
            page.locator("#mv-run").click()
            assert has_error(out) and "cannot exceed" in out.inner_text(), out.inner_text()
            page.locator("#mv-k").fill("2")
            page.locator("#mv-std").check()
            page.locator("#mv-run").click()
            first = out.inner_text()
            assert not has_error(out) and "k-means: k = 2" in first and "standardized" in first, first
            assert "coloured by k-means cluster" in page.locator("#mv-canvas").get_attribute("aria-label")
            page.locator("#mv-run").click()
            assert out.inner_text() == first
            before = page.evaluate("MathStudio.dataTables.tables.length")
            page.locator("#mv-save").click()
            assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
            km = page.evaluate("MathStudio.dataTables.tables.at(-1)")
            assert km["name"].startswith("KMeans_Labels") and km["columns"][-1] == "cluster" and len(km["rows"]) == 5, km
            assert set(row[-1] for row in km["rows"]) == {"1", "2"}, km["rows"]
            area.evaluate("e=>e.scrollIntoView()")
            page.locator("#mv-table").select_option("MV_Data")

            sizes = page.evaluate("""()=>[...document.querySelectorAll('#multivariate-details button,#multivariate-details input:not([type=checkbox]),#multivariate-details select,#multivariate-details summary,#multivariate-details label:has(> input[type=checkbox])')].filter(e=>e.offsetParent).map(e=>e.getBoundingClientRect().height)""")
            assert sizes and min(sizes) >= 40, sizes
            overflow = page.evaluate("()=>{const d=document.getElementById('multivariate-details').getBoundingClientRect();return document.documentElement.scrollWidth>window.innerWidth+1||d.right>window.innerWidth+1}")
            assert not overflow, width
        assert not errors, errors
        browser.close()
    print("PASS: multivariate covariance/correlation, PCA, k-means references, determinism, validation, recovery, keyboard, export and 390/1280 layout")


if __name__ == "__main__":
    main()
