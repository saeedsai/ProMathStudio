"""Browser regression: RK4 scalar/coupled time-resolution failure and recovery."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(el) => el.open = true")
        page.locator("#ode-method").select_option("rk4-system")
        page.locator("#ode-expression").fill("1")
        page.locator("#ode-system-derivative").fill("-y")
        page.locator("#ode-initial").fill("0")
        page.locator("#ode-system-initial").fill("0")
        page.locator("#ode-steps").fill("4")

        for mode in ("rk4", "rk4-system"):
            page.locator("#ode-method").select_option(mode)
            for start, end in (("999999999999.9999", "1000000000000"),
                               ("1000000000000", "999999999999.9999")):
                page.locator("#ode-start").fill(start)
                page.locator("#ode-end").fill(end)
                page.locator("#ode-run").click()
                assert "time resolution is insufficient" in page.locator(
                    "#ode-output").inner_text()
                assert page.locator("#ode-to-table").is_disabled()
                assert page.locator("#ode-to-graph").is_disabled()

            # Valid, representable time grid must still run after a failure.
            page.locator("#ode-start").fill("0")
            page.locator("#ode-end").fill("1")
            page.locator("#ode-steps").fill("40")
            page.locator("#ode-run").click()
            assert "time resolution is insufficient" not in page.locator(
                "#ode-output").inner_text()
            assert page.locator("#ode-to-table").is_enabled()
            assert page.locator("#ode-to-graph").is_enabled()
            result = page.evaluate("""(mode) => mode === 'rk4'
                ? MathStudio.odeTools.solve({expression:'1',t0:0,t1:1,y0:0,steps:40})
                : MathStudio.odeTools.solveSystem({
                    expression:'1',expressionZ:'-y',t0:0,t1:1,y0:0,z0:0,steps:40
                  })""", mode)
            assert abs(result["rows"][-1][1] - 1) < 1e-10

        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#ode-output").is_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1")
        assert not errors, errors
        browser.close()
    print("PASS fixed RK4 time-resolution guard, stale-export invalidation and mobile")


if __name__ == "__main__":
    main()
