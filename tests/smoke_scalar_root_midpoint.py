"""Bounded midpoint probes recover paired roots without accepting finite jumps."""
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

        def solve(expr, tol=1e-10):
            return page.evaluate(
                """([expr,tol]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',0,1,{samples:20,tolerance:tol})""", [expr, tol])

        # Both zeros fall within a single coarse grid interval [0.20, 0.25],
        # whose endpoints are positive; its midpoint is negative.
        paired = solve("(x-0.21)*(x-0.24)")
        assert paired["midpointProbes"] == 20, paired
        assert paired["midpointSignReversals"] >= 1, paired
        for target in (0.21, 0.24):
            assert any(abs(x-target) < 1e-5 for x in paired["roots"]), paired
        assert all(math.isfinite(r) and r <= 1e-10 for r in paired["residuals"]), paired
        assert "not globally complete" in paired["note"]

        # Two finite jumps produce the same sign pattern but must never be
        # promoted to roots without a small actual function residual.
        jump = solve("((x-0.21)*(x-0.24))/sqrt(((x-0.21)*(x-0.24))^2)")
        assert jump["midpointSignReversals"] >= 1, jump
        assert jump["roots"] == [] and jump["maxResidual"] is None, jump
        plateau = solve("x-x")
        assert plateau["rootStatus"] == "sampled-zero-plateau", plateau
        assert plateau["midpointProbes"] == 20 and plateau["roots"] == [], plateau
        ordinary = solve("x-0.123456789")
        assert any(abs(x-0.123456789) < 1e-5 for x in ordinary["roots"]), ordinary

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(e) => e.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("(x-0.21)*(x-0.24)")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("1")
        page.locator("#num-samples").fill("20")
        page.locator("#num-tolerance").fill("1e-10")
        output = page.locator("#num-output")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#num-run").focus()
            page.keyboard.press("Enter")
            text = output.inner_text()
            assert "Midpoint probes: 20; extra opposite-sign intervals:" in text, text
            # Parse displayed values numerically: a certified approximate root
            # need not print as the exact decimal 0.24.
            shown = [float(v.strip()) for v in text.splitlines()[0].split(":", 1)[1].split(",")]
            for target in (0.21, 0.24):
                assert any(abs(x-target) < 1e-5 for x in shown), (target, shown)
            assert not output.evaluate("(e) => e.classList.contains('error')"), text
            assert not page.evaluate("document.documentElement.scrollWidth > innerWidth + 1"), width
        page.locator("#num-samples").fill("19")
        page.locator("#num-run").click()
        assert output.evaluate("(e) => e.classList.contains('error')")
        assert page.evaluate("document.activeElement.id") == "num-samples"
        page.locator("#num-samples").fill("20")
        page.locator("#num-run").click()
        assert not output.evaluate("(e) => e.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS midpoint paired-root recovery, finite jumps, plateau and responsive UI")


if __name__ == "__main__":
    main()
