"""Chromium RK45 floating-point stage-time collision, recovery and mobile regression."""
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
        page.locator("#ode-expression").fill("1")
        page.locator("#ode-start").fill("999999999999.9999")
        page.locator("#ode-end").fill("1000000000000")
        page.locator("#ode-initial").fill("0")
        page.locator("#ode-run").click()
        output = page.locator("#ode-output").inner_text()
        assert "stage times rounded to current t" in output, output
        assert "rescale time" in output, output
        result = page.evaluate('''() => MathStudio.odeTools.solveAdaptive({
            expression:'1',t0:1e12-1/8192,t1:1e12,y0:0
        })''')
        assert result["stageTimeCollisionAttempts"] >= 1, result
        assert result["stageTimeCollisionAcceptedSteps"] >= 1, result
        assert result['quantumLimitedAcceptedSteps'] >= 1, result
        assert all(result['rows'][i][0] > result['rows'][i-1][0]
                   for i in range(1, len(result['rows']))), result
        assert 'one representable time increment' in output, output
        assert abs(result["rows"][-1][1] - 1/8192) < 1e-12, result
        assert page.locator("#ode-to-table").is_enabled()
        assert page.locator("#ode-to-graph").is_enabled()

        page.locator("#ode-expression").fill("1/0")
        page.locator("#ode-run").click()
        assert "derivative failed" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_disabled()
        assert page.locator("#ode-to-graph").is_disabled()

        page.locator("#ode-expression").fill("1")
        page.locator("#ode-start").fill("1000000000000")
        page.locator("#ode-end").fill("999999999999.9999")
        page.locator("#ode-run").click()
        assert "stage times rounded to current t" in page.locator("#ode-output").inner_text()
        assert page.locator('#ode-to-table').is_enabled()
        backward = page.evaluate("""() => MathStudio.odeTools.solveAdaptive({
            expression:'1',t0:1e12,t1:1e12-1/8192,y0:0
        })""")
        assert backward['quantumLimitedAcceptedSteps'] >= 1
        assert all(backward['rows'][i][0] < backward['rows'][i-1][0]
                   for i in range(1, len(backward['rows']))), backward
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#ode-output").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS RK45 stage-time precision warning, recovery and mobile")


if __name__ == "__main__":
    main()
