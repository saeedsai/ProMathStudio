"""Root residual vs location-error guidance: flat, steep, jumps and UI recovery."""
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

        def solve(expr, lo, hi, tol=1e-9, samples=350):
            return page.evaluate(
                """([expr,lo,hi,tol,samples]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',lo,hi,{tolerance:tol,samples})""",
                [expr, lo, hi, tol, samples])

        smooth = solve("x^2-2=0", 0, 2)
        assert any(abs(x-math.sqrt(2)) < 1e-5 for x in smooth["roots"]), smooth
        assert len(smooth["roots"]) == len(smooth["localSlopeMagnitudes"]), smooth
        assert smooth["minLocalSlope"] is not None and 2.7 < smooth["minLocalSlope"] < 2.9, smooth
        assert all(math.isfinite(r) and r <= 1e-9 for r in smooth["residuals"]), smooth
        assert "not a certified root-position error bound" in smooth["note"], smooth

        flat = solve("x^3", -1, 1)
        assert any(abs(x) < 1e-4 for x in flat["roots"]), flat
        assert flat["minLocalSlope"] is not None and flat["minLocalSlope"] < 1e-6, flat

        steep = solve("1000000*(x-0.5)", 0, 1)
        assert any(abs(x-0.5) < 1e-8 for x in steep["roots"]), steep
        assert steep["minLocalSlope"] is not None and 9e5 < steep["minLocalSlope"] < 1.1e6, steep

        jump = solve("0.00001*(x-0.12345)/sqrt((x-0.12345)^2)", -1, 1, 1e-9, 351)
        assert jump["roots"] == [] and jump["minLocalSlope"] is None, jump

        plateau = solve("x-x", -1, 1)
        assert plateau["rootStatus"] == "sampled-zero-plateau", plateau
        assert plateau["localSlopeMagnitudes"] == [] and plateau["minLocalSlope"] is None, plateau

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("x^2-2=0")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("2")
        page.locator("#num-tolerance").fill("1e-9")
        page.locator("#num-run").click()
        out = page.locator("#num-output")
        assert "Minimum local secant slope magnitude (heuristic):" in out.inner_text()
        assert "not a certified root-position error bound" in out.inner_text()
        assert out.get_attribute("aria-live") == "polite"
        page.locator("#num-start").fill("3")
        page.locator("#num-run").click()
        assert out.evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-start").fill("0")
        page.locator("#num-run").click()
        assert not out.evaluate("(el) => el.classList.contains('error')")
        assert "Minimum local secant slope magnitude" in out.inner_text()
        assert not errors, errors
        browser.close()
    print("PASS scalar conditioning heuristic, residual disclaimer, jump/plateau, UI recovery")


if __name__ == "__main__":
    main()
