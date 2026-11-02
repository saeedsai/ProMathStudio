"""Steep scalar root brackets, endpoints, finite jumps and responsive UI recovery."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def solve(expr, lo=0, hi=1, samples=351):
            return page.evaluate(
                """([expr,lo,hi,samples]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',lo,hi,{tolerance:1e-9,samples})""",
                [expr, lo, hi, samples])

        steep = solve("1000000*(x-0.123456789123)")
        assert any(abs(x-0.123456789123)<1e-11 for x in steep["roots"]), steep
        assert steep["residuals"] and max(steep["residuals"]) <= 1e-9, steep
        assert len(steep["roots"]) == len(steep["residuals"]), steep

        left = solve("1000000*x")
        right = solve("1000000*(x-1)")
        assert any(abs(x)<1e-12 for x in left["roots"]), left
        assert any(abs(x-1)<1e-12 for x in right["roots"]), right
        assert all(r<=1e-9 for r in left["residuals"]+right["residuals"])

        smooth = solve("x^2-2", 0, 2)
        assert any(abs(x-math.sqrt(2))<1e-5 for x in smooth["roots"]), smooth
        tangent = solve("(x-0.83)^2", 0, 2)
        assert any(abs(x-0.83)<1e-3 for x in tangent["roots"]), tangent
        jump = solve("0.00001*(x-0.12345)/sqrt((x-0.12345)^2)", -1, 1)
        assert jump["roots"] == [] and jump["maxResidual"] is None, jump

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("1000000*(x-0.123456789123)")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("1")
        page.locator("#num-tolerance").fill("1e-9")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#num-run").is_visible()
        page.locator("#num-run").click()
        out = page.locator("#num-output")
        assert "Maximum absolute residual:" in out.inner_text(), out.inner_text()
        assert not out.evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-start").fill("2")
        page.locator("#num-run").click()
        assert out.evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-start").fill("0")
        page.locator("#num-run").click()
        assert not out.evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS residual-first steep bracket, endpoints, jump rejection and responsive UI recovery")


if __name__ == "__main__":
    main()
