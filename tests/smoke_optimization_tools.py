"""Optimization (LP simplex + Nelder-Mead) references, failures, keyboard, responsive and export browser checks."""
from pathlib import Path
import os
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/optimization-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        lp = lambda text: page.evaluate("t=>MathStudio.optimization.linprog(t)", text)
        r = lp("max: 3x1 + 5x2\nx1 <= 4\n2x2 <= 12\n3x1 + 2x2 <= 18")
        assert r["status"] == "optimal" and abs(r["objective"] - 36) < 1e-9 and abs(r["x"][0] - 2) < 1e-9 and abs(r["x"][1] - 6) < 1e-9, r
        assert lp("max: x1+x2\nx1+x2 <= 1\nx1+x2 >= 3")["status"] == "infeasible"
        assert lp("max: x1+x2\nx1 - x2 <= 1")["status"] == "unbounded"
        nm = lambda o: page.evaluate("o=>MathStudio.optimization.nelderMead(o)", o)
        # Real calculator parser path (MathStudio.numerical.evaluate).
        ros = nm({"expression": "100*(y-x^2)^2+(1-x)^2", "start": "-1.2, 1"})
        assert ros["converged"] and abs(ros["x"][0] - 1) < 1e-5 and abs(ros["x"][1] - 1) < 1e-5, ros
        him = nm({"expression": "(x^2+y-11)^2+(x+y^2-7)^2", "start": "2.5, 2.5"})
        assert abs(him["x"][0] - 3) < 1e-5 and abs(him["x"][1] - 2) < 1e-5, him
        box = nm({"expression": "(x-3)^2+(y+1)^2", "start": "1,0", "lower": "0, -inf", "upper": "2, inf"})
        assert abs(box["x"][0] - 2) < 1e-7 and abs(box["x"][1] + 1) < 1e-5 and box["gradient"]["projectedNorm"] < 1e-4, box
        three = nm({"expression": "(x-1)^2+(y+2)^2+(z-0.5)^2", "start": "0,0,0"})
        assert all(abs(a - b) < 1e-5 for a, b in zip(three["x"], [1, -2, 0.5])), three
        for o in [{"expression": "x+", "start": "0,0"}, {"expression": "x^2+y^2", "start": "0"},
                  {"expression": "x^2+y^2", "start": "0,0", "lower": "1,0", "upper": "0,1"}]:
            assert page.evaluate("o=>{try{MathStudio.optimization.nelderMead(o);return false}catch(e){return !!e.message}}", o), o

        page.locator('[data-workspace="editor"]').click()
        page.locator("#optimization-details").evaluate("e=>e.open=true")
        page.locator("#opt-lp-run").click()
        out = page.locator("#opt-lp-output")
        assert "x1 = 2" in out.inner_text() and "x2 = 6" in out.inner_text() and "= 36" in out.inner_text(), out.inner_text()
        assert page.locator("#opt-lp-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#opt-lp-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.active.name").startswith("Optimization_LP")

        page.locator('[data-workspace="editor"]').click()
        page.locator("#optimization-details").evaluate("e=>e.open=true")
        # Malformed text: error class, export disabled, then recovery via keyboard (Ctrl+Enter).
        page.locator("#opt-lp-text").fill("max: 3x1 5x2\nx1 <= 4")
        assert page.locator("#opt-lp-to-table").is_disabled()
        page.locator("#opt-lp-run").click()
        assert "error" in out.get_attribute("class") and "separated" in out.inner_text(), out.inner_text()
        page.locator("#opt-lp-text").fill("max: x1+x2\nx1 - x2 <= 1")
        page.locator("#opt-lp-text").press("Control+Enter")
        assert "Unbounded" in out.inner_text() and "warn" in out.get_attribute("class")
        assert page.locator("#opt-lp-to-table").is_disabled()
        page.locator("#opt-lp-text").fill("min: 2x1+3x2\nx1+x2 >= 4\nx1-x2 = 1")
        page.locator("#opt-lp-text").press("Control+Enter")
        assert "= 9.5" in out.inner_text() and "error" not in (out.get_attribute("class") or ""), out.inner_text()

        page.locator("#opt-nm-run").focus()
        page.keyboard.press("Enter")
        nmout = page.locator("#opt-nm-output")
        assert "Status: converged" in nmout.inner_text() and re.search(r"x ≈ (1|0\.99999)", nmout.inner_text()), nmout.inner_text()
        assert page.locator("#opt-nm-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#opt-nm-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        page.locator('[data-workspace="editor"]').click()
        page.locator("#optimization-details").evaluate("e=>e.open=true")
        page.locator("#opt-nm-lower").fill("2, 0")
        page.locator("#opt-nm-upper").fill("1, 1")
        assert page.locator("#opt-nm-to-table").is_disabled()
        page.locator("#opt-nm-run").click()
        assert "error" in nmout.get_attribute("class") and "exceed" in nmout.inner_text()
        page.locator("#opt-nm-lower").fill("")
        page.locator("#opt-nm-upper").fill("")
        page.locator("#opt-nm-run").click()
        assert "Status: converged" in nmout.inner_text()

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#optimization-details").scroll_into_view_if_needed()
            assert page.locator("#opt-lp-run").is_visible() and page.locator("#opt-nm-run").is_visible()
            overflow = page.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            for sel in ("#opt-lp-run", "#opt-lp-to-table", "#opt-nm-run", "#opt-nm-to-table", "#opt-nm-start"):
                box_ = page.locator(sel).bounding_box()
                assert box_["height"] >= 40, (sel, box_)
            right = page.evaluate("Math.max(...[...document.querySelectorAll('#optimization-details *')].map(e=>e.getBoundingClientRect().right))")
            assert right <= width + 1, (width, right)
        assert page.locator("#opt-lp-output").get_attribute("role") == "status"
        assert page.locator("#opt-nm-output").get_attribute("aria-live") == "polite"
        assert not errors, errors
        browser.close()
    print("PASS: LP simplex (Wyndor, infeasible, unbounded), Nelder-Mead (Rosenbrock, Himmelblau, bounds), UI, keyboard, 390/1280 and export")


if __name__ == "__main__":
    main()
