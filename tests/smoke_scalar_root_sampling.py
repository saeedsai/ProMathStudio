"""Oscillatory sampling density, finite jumps, accessible errors and mobile recovery."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def solve(expr, samples, lo=0, hi=1):
            return page.evaluate(
                """([expr,samples,lo,hi]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',lo,hi,{tolerance:1e-9,samples})""",
                [expr, samples, lo, hi])

        # The new quarter-grid probes can recover all 81 roots of this
        # 40-cycle reference even at 20 coarse intervals.
        quarter_aligned = solve("sin(2*pi*40*x)", 20)
        assert len(quarter_aligned["roots"]) >= 80, quarter_aligned
        # A higher-frequency reference still aliases at coarse density.
        # Preserve a strict fine > coarse test, rather than weakening it.
        coarse = solve("sin(2*pi*60*x)", 20)
        fine = solve("sin(2*pi*60*x)", 800)
        assert len(coarse["roots"]) >= 40, coarse
        assert len(fine["roots"]) >= 120 and len(fine["roots"]) > len(coarse["roots"]), (
            len(coarse["roots"]), len(fine["roots"]))
        assert math.isclose(coarse["sampleSpacing"], 0.05)
        assert math.isclose(fine["sampleSpacing"], 0.00125)
        assert "not globally complete" in fine["note"], fine
        assert all(math.isfinite(v) and v <= 1e-9 for v in fine["residuals"]), fine
        plateau = solve("x-x", 20)
        assert plateau["rootStatus"] == "sampled-zero-plateau" and "not globally complete" in plateau["note"], plateau
        jump = solve("0.00001*(x-0.12345)/sqrt((x-0.12345)^2)", 351, -1, 1)
        assert jump["roots"] == [], jump

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("x^2-2")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("2")
        page.locator("#num-tolerance").fill("1e-9")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#num-samples").is_visible(), width
        out = page.locator("#num-output")
        for invalid in ("19", "20.5", "1601", ""):
            page.locator("#num-samples").fill(invalid)
            page.locator("#num-run").click()
            assert out.evaluate("(el) => el.classList.contains('error')"), invalid
            assert page.locator("#num-samples").get_attribute("aria-invalid") == "true", invalid
            assert page.evaluate("document.activeElement.id") == "num-samples", invalid
        page.locator("#num-samples").fill("800")
        page.locator("#num-run").click()
        assert not out.evaluate("(el) => el.classList.contains('error')"), out.inner_text()
        assert "Sampling intervals: 800; grid spacing:" in out.inner_text(), out.inner_text()
        assert "not globally complete" in out.inner_text()
        page.locator("#num-method").select_option("system")
        assert not page.locator("#num-samples").is_visible()
        page.locator("#num-method").select_option("scalar")
        assert page.locator("#num-samples").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS scalar root oscillatory sampling, limits, responsive recovery")

if __name__ == "__main__":
    main()
