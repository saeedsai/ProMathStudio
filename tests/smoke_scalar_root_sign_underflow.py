"""Finite tiny residual sign changes must not disappear through product underflow."""
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

        def solve(expr, tol=1e-211, samples=351):
            return page.evaluate(
                """([expr,tol,samples]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',0,1,{samples,tolerance:tol})""",
                [expr, tol, samples])

        # The bracket's residuals are around 1e-200, but their product
        # underflows to zero in binary64. Direct sign comparison must refine it.
        tiny = solve("10^(-100)*10^(-100)*(x-0.123456789)")
        assert any(abs(root-0.123456789) < 2e-8 for root in tiny["roots"]), tiny
        assert tiny["residuals"] and all(0 <= r <= 1e-211 for r in tiny["residuals"]), tiny
        assert tiny["maxResidual"] == max(tiny["residuals"]), tiny

        # A tiny finite jump has opposite signs but no zero; residual validation
        # must still reject it rather than treating the sign change as a root.
        jump = solve("10^(-100)*10^(-100)*(x-0.12345)/sqrt((x-0.12345)^2)")
        assert jump["roots"] == [] and jump["maxResidual"] is None, jump
        regular = solve("x-0.123456789", 1e-9)
        assert any(abs(x-0.123456789) < 2e-8 for x in regular["roots"]), regular

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("10^(-100)*10^(-100)*(x-0.123456789)")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("1")
        page.locator("#num-samples").fill("351")
        page.locator("#num-tolerance").fill("1e-211")
        output = page.locator("#num-output")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#num-run").click()
            assert "0.123456789" in output.inner_text(), output.inner_text()
            assert "Maximum absolute residual:" in output.inner_text()
            assert not output.evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-tolerance").fill("0")
        page.locator("#num-run").click()
        assert output.evaluate("(el) => el.classList.contains('error')")
        assert page.evaluate("document.activeElement.id") == "num-tolerance"
        page.locator("#num-tolerance").fill("1e-211")
        page.locator("#num-run").click()
        assert not output.evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS tiny-residual sign bracketing, finite jump rejection and responsive recovery")


if __name__ == "__main__":
    main()
