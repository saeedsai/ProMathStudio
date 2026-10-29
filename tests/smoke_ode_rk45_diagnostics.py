"""Browser regression for RK45 derivative diagnostics and stale export safety."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 860})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(el) => el.open = true")
        page.locator("#ode-method").select_option("rk45")
        page.locator("#ode-expression").fill("y")
        page.locator("#ode-run").click()
        assert "RK45" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        assert page.locator("#ode-to-graph").is_enabled()
        for expression, initial, fragment in (
            ("1/0", "1", "RK45 k1 derivative failed at t="),
            ("1000000000000*y", "2", "RK45 k1 derivative failed at t="),
        ):
            page.locator("#ode-expression").fill(expression)
            page.locator("#ode-initial").fill(initial)
            page.locator("#ode-run").click()
            message = page.locator("#ode-output").inner_text()
            assert fragment in message and ", y=" in message, message
            assert page.locator("#ode-to-table").is_disabled()
            assert page.locator("#ode-to-graph").is_disabled()
        page.locator("#ode-expression").fill("y")
        page.locator("#ode-initial").fill("1")
        page.locator("#ode-run").click()
        result = page.evaluate("MathStudio.odeTools.solveAdaptive({expression:'y',t0:0,t1:1,y0:1,tolerance:1e-10})")
        assert abs(result["rows"][-1][1] - math.e) < 1e-8
        assert page.locator("#ode-to-table").is_enabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#ode-output").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: RK45 stage diagnostics, stale export protection, recovery, mobile")


if __name__ == "__main__":
    main()
