"""Polynomial tools browser regression: API references, UI operations, keyboard, errors, recovery, Data Tables and 390/1280 layout."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/polynomial-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")

        assert page.evaluate("Object.isFrozen(MathStudio.polynomials)")
        roots = page.evaluate("MathStudio.polynomials.roots('1,-3,2').roots.map(r=>[r.root.re,r.root.im])")
        assert all(abs(a - b) < 1e-13 and abs(im) < 1e-13 for (a, im), b in zip(roots, [1, 2])), roots
        wil = page.evaluate("""()=>{let w=[1];for(let k=1;k<=10;k++){const n=[...w,0];for(let i=1;i<n.length;i++)n[i]-=k*w[i-1];w=n;}
          return MathStudio.polynomials.roots(w).roots.map(r=>Math.hypot(r.root.re-Math.round(r.root.re),r.root.im))}""")
        assert len(wil) == 10 and max(wil) < 1e-6, wil
        cube = page.evaluate("MathStudio.polynomials.roots('1,-3,3,-1').distinct")
        assert len(cube) == 1 and cube[0]["multiplicity"] == 3
        for args in ("''", "'0,0'", "'1,q'", "Array(32).fill(1).join(',')"):
            assert page.evaluate(f"()=>{{try{{MathStudio.polynomials.roots({args});return false}}catch(e){{return !!e.message}}}}"), args

        page.locator('[data-workspace="calculator"]').first.click()
        details = page.locator("#calculator-panel #poly-details")
        assert details.count() == 1
        details.locator("summary").click()
        assert details.evaluate("e=>e.open")
        for sel in ("#poly-op", "#poly-p", "#poly-q", "#poly-x", "#poly-roots-in", "#poly-tol"):
            label = page.evaluate("s=>document.querySelector(s).closest('label').textContent.trim()", sel)
            assert label, sel
        out = page.locator("#poly-output")
        assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
        save = page.locator("#poly-to-table")
        assert save.is_disabled()

        # Roots of x^2 - 3x + 2 (default) via Run button.
        assert page.locator("#poly-q").is_hidden()
        page.locator("#poly-run").click()
        text = out.inner_text()
        assert "r1 = 1 " in text and "r2 = 2 " in text and "converged" in text, text
        assert not save.is_disabled()

        # Complex roots via Enter key; triple root multiplicity.
        page.fill("#poly-p", "1, 0, 1")
        assert "Inputs changed" in out.inner_text() and save.is_disabled()
        page.locator("#poly-p").press("Enter")
        text = out.inner_text()
        assert "= -i " in text and "= i " in text, text
        page.fill("#poly-p", "1, -3, 3, -1")
        page.locator("#poly-p").press("Enter")
        assert "multiplicity 3" in out.inner_text(), out.inner_text()

        # Save roots to Data Tables.
        before = page.evaluate("MathStudio.dataTables.tables.length")
        save.click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        table = page.evaluate("(()=>{const t=MathStudio.dataTables.tables.at(-1);return {name:t.name,cols:t.columns,rows:t.rows.length}})()")
        assert table["rows"] == 3 and "cluster_multiplicity" in table["cols"], table
        assert "Saved to Data Tables" in out.inner_text()

        # Long division via keyboard selection.
        page.locator("#poly-op").select_option("divide")
        assert page.locator("#poly-q").is_visible()
        page.fill("#poly-p", "1, 0, 0, -1")
        page.fill("#poly-q", "1, -1")
        page.locator("#poly-q").press("Enter")
        text = out.inner_text()
        assert "Quotient: x^2 + x + 1" in text and "Remainder: 0" in text, text

        page.locator("#poly-op").select_option("gcd")
        page.fill("#poly-p", "1, -3, 2")
        page.fill("#poly-q", "1, -4, 3")
        page.locator("#poly-run").click()
        assert "gcd(p, q) = x - 1" in out.inner_text(), out.inner_text()

        page.locator("#poly-op").select_option("evaluate")
        page.fill("#poly-p", "1, -3, 2")
        page.fill("#poly-x", "3")
        page.locator("#poly-x").press("Enter")
        assert "p(3) = 2" in out.inner_text() and "p′(3) = 3" in out.inner_text(), out.inner_text()

        page.locator("#poly-op").select_option("fromRoots")
        page.fill("#poly-roots-in", "1, 2, i, -i")
        page.locator("#poly-run").click()
        assert "x^4 - 3x^3 + 3x^2 - 3x + 2" in out.inner_text(), out.inner_text()

        page.locator("#poly-op").select_option("derivative")
        page.fill("#poly-p", "1, -3, 2")
        page.locator("#poly-run").click()
        assert "p′(x) = 2x - 3" in out.inner_text(), out.inner_text()

        # Error and recovery.
        page.locator("#poly-op").select_option("roots")
        page.fill("#poly-p", "1, abc")
        page.locator("#poly-run").click()
        assert "error" in (out.get_attribute("class") or "") and "not a number" in out.inner_text()
        assert save.is_disabled()
        page.fill("#poly-p", "0, 0")
        page.locator("#poly-run").click()
        assert "all zero" in out.inner_text()
        page.fill("#poly-p", "1, 0, 0, 0, 0, -1")
        assert "error" not in (out.get_attribute("class") or "")
        page.locator("#poly-run").click()
        assert out.inner_text().count("   backward error") == 5, out.inner_text()

        # Keyboard reachability of the operation select.
        page.locator("#poly-p").focus()
        page.keyboard.press("Shift+Tab")
        assert page.evaluate("document.activeElement.id") == "poly-op"

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#poly-run").scroll_into_view_if_needed()
            for sel in ("#poly-op", "#poly-p", "#poly-tol", "#poly-run", "#poly-to-table", "#poly-details summary"):
                box = page.locator(sel).bounding_box()
                assert box and box["height"] >= 40 and box["x"] >= 0 and box["x"] + box["width"] <= width + 0.5, (width, sel, box)
            assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth"), width
        assert not errors, errors
        browser.close()
    print("PASS: polynomial roots, multiplicity, Horner, division, GCD, Data Tables, keyboard, recovery and responsive layout")


if __name__ == "__main__":
    main()
