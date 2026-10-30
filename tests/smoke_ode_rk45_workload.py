"""Chromium RK45 difficult-workload warning, recovery and 390px regression."""
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
        page.locator("#ode-expression").fill("-100*y")
        page.locator("#ode-tolerance").fill("1e-9")
        page.locator("#ode-run").click()
        output = page.locator("#ode-output").inner_text()
        assert "Repeated RK45 step rejections" in output, output
        assert "not diagnose stiffness" in output, output
        result = page.evaluate("""() => MathStudio.odeTools.solveAdaptive({
            expression:'-100*y',t0:0,t1:1,y0:1,tolerance:1e-9,maxSteps:5000
        })""")
        assert result["rejected"] >= 5, result
        assert result["maxConsecutiveRejected"] >= 1, result
        assert abs(result["rows"][-1][1] - math.exp(-100)) < 1e-7, result
        assert page.locator("#ode-to-table").is_enabled()
        assert page.locator("#ode-to-graph").is_enabled()

        page.locator("#ode-expression").fill("1/0")
        page.locator("#ode-run").click()
        assert "derivative failed" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_disabled()
        assert page.locator("#ode-to-graph").is_disabled()

        page.locator("#ode-expression").fill("1")
        page.locator("#ode-run").click()
        assert "Repeated RK45" not in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#ode-output").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS RK45 difficult workload advisory, recovery and mobile")


if __name__ == "__main__":
    main()
