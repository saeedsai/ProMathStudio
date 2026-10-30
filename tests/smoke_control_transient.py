"""Chromium Control transient reference, export, invalidation and mobile regression."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        page.locator('[data-workspace="graph"]').click()
        page.locator("#control-theory-toolbox").evaluate("(e) => e.open=true")
        page.locator("#ct-equilibrium").evaluate("(e) => e.open=true")
        page.locator("#ct-eq-transient").evaluate("(e) => e.open=true")
        run = page.locator("#ct-eq-transient-run")
        run.click()
        assert "trajectory samples" in page.locator("#ct-eq-transient-output").inner_text()
        output = page.locator("#ct-eq-transient-output")
        assert "RK4 step-doubling |x_N - x_2N|∞:" in output.inner_text()
        # A finer trajectory should agree more closely on smooth linear systems.
        page.locator("#ct-eq-steps").fill("500")
        run.click()
        assert "RK4 step-doubling |x_N - x_2N|∞:" in output.inner_text()
        page.locator("#ct-eq-steps").fill("501")
        run.click()
        assert "Step-doubling comparison unavailable" in output.inner_text()
        assert page.locator("#ct-eq-transient-table").is_enabled()
        page.locator("#ct-eq-steps").fill("80")
        run.click()

        result = page.evaluate("""() => MathStudio.controlEquilibrium.simulateTransient(
            [[2,0],[0,3]],[4,9],[0,0],0,1,80)""")
        assert len(result["rows"]) == 81
        assert abs(result["rows"][-1][1] - 2*(1-math.exp(-2))) < 1e-7
        assert abs(result["rows"][-1][2] - 3*(1-math.exp(-3))) < 1e-7
        backward = page.evaluate("""() => MathStudio.controlEquilibrium.simulateTransient(
            [[2,0],[0,3]],[4,9],[2*(1-Math.exp(-2)),3*(1-Math.exp(-3))],1,0,80)""")
        assert max(abs(v) for v in backward["rows"][-1][1:]) < 2e-7
        singular = page.evaluate("""() => MathStudio.controlEquilibrium.simulateTransient(
            [[0,0],[0,2]],[1,0],[0,1],0,1,80)""")
        assert abs(singular["rows"][-1][1] - 1) < 1e-9
        assert abs(singular["rows"][-1][2] - math.exp(-2)) < 1e-7
        page.locator("#ct-eq-matrix").fill("0x10,0;0,1")
        assert page.locator("#ct-eq-transient-table").is_disabled()
        run.click()
        assert "decimal or scientific" in page.locator("#ct-eq-transient-status").inner_text()
        assert "No current trajectory" in page.locator("#ct-eq-transient-output").inner_text()
        page.locator("#ct-eq-matrix").fill("2,0;0,3")
        page.locator("#ct-eq-size").select_option("3")
        run.click()
        assert "exactly two states" in page.locator("#ct-eq-transient-status").inner_text()
        page.locator("#ct-eq-size").select_option("2")
        run.click()
        assert page.locator("#ct-eq-transient-table").is_enabled()
        plot = page.locator("#ct-eq-transient-plot")
        assert plot.is_enabled()
        plot.focus()
        page.keyboard.press('Enter')
        state = page.evaluate("MathStudio.graphData.getState()")
        assert state["headers"] == ["t", "x1", "x2"], state
        assert len(state["points"]) == 81, state
        assert len(state["extra"]) == 1, state
        assert state["extra"][0]["mapping"]["x"] == 0, state
        assert state["extra"][0]["mapping"]["y"] == 2, state
        assert state["extra"][0]["mapping"]["style"] == "line", state
        assert abs(state["points"][-1]["y"] - result["rows"][-1][1]) < 1e-9
        assert "Plotted x1(t) and x2(t)" in page.locator("#ct-eq-transient-status").inner_text()
        page.set_viewport_size({"width": 390, "height": 844})
        assert run.is_visible()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth+1")
        page.locator("#ct-eq-transient-table").click()
        assert page.evaluate("MathStudio.advanced.currentMode()") == "data"
        assert not errors, errors
        browser.close()
    print("PASS Control transient forward/backward, singular, errors, export, mobile")


if __name__ == "__main__":
    main()
