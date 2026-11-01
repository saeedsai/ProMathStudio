"""Root residual reference, jump rejection, tiny-root and UI diagnostics."""
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
                """([expr,lo,hi,tol,samples]) =>
                    window.MathStudio.numerical.scalarRoots(
                        expr, 'x', lo, hi, {tolerance:tol,samples})""",
                [expr, lo, hi, tol, samples])

        smooth = solve("x^2-2=0", 0, 2)
        assert any(abs(x - math.sqrt(2)) < 1e-5 for x in smooth["roots"]), smooth
        assert smooth["residuals"] and len(smooth["roots"]) == len(smooth["residuals"])
        assert all(math.isfinite(r) and r <= 1e-9 for r in smooth["residuals"]), smooth
        assert smooth["maxResidual"] == max(smooth["residuals"]), smooth

        tangent = solve("(x-0.83)^2", 0, 2)
        assert any(abs(x-0.83) < 1e-3 for x in tangent["roots"]), tangent
        assert all(r <= 1e-9 for r in tangent["residuals"]), tangent

        # A finite jump changes sign but never reaches zero; the old
        # sqrt(tolerance) bisection gate reported a false positive.
        jump = solve("0.00001*(x-0.12345)/sqrt((x-0.12345)^2)", -1, 1, 1e-9, 351)
        assert jump["roots"] == [], jump
        assert jump["residuals"] == [] and jump["maxResidual"] is None, jump

        tiny = solve("x-0.00000000001", -0.01, 0.01, 1e-13, 351)
        assert any(x > 0 and abs(x-1e-11) < 5e-12 for x in tiny["roots"]), tiny
        assert all(r <= 1e-13 for r in tiny["residuals"]), tiny

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("x^2-2=0")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("2")
        page.locator("#num-tolerance").fill("1e-9")
        page.locator("#num-run").click()
        out = page.locator("#num-output")
        assert "Maximum absolute residual:" in out.inner_text(), out.inner_text()
        assert not out.evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS root reference, tangent, jump rejection, tiny root and UI residuals")


if __name__ == "__main__":
    main()
