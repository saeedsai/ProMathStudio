"""RK45 large-epoch representable-time, endpoint, and underflow browser regression."""
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
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        # At 1e12, 1/8192 is one representable time quantum.
        # Previously both directions falsely raised step underflow.
        for direction in (1, -1):
            t0 = 1e12 - 1 / 8192 if direction == 1 else 1e12
            t1 = 1e12 if direction == 1 else 1e12 - 1 / 8192
            result = page.evaluate("""opts => MathStudio.odeTools.solveAdaptive(opts)""",
                                   {"expression": "1", "t0": t0, "t1": t1, "y0": 0})
            self_span = t1 - t0
            assert result["rows"][0][0] == t0
            assert result["rows"][-1][0] == t1
            assert abs(result["rows"][-1][1] - self_span) < 1e-15, result
            assert result["attempts"] == result["steps"] + result["rejected"]
            assert all(direction * (b[0] - a[0]) > 0
                       for a, b in zip(result["rows"], result["rows"][1:]))

        # Prevent endpoint snapping from silently skipping part of the interval.
        for direction in (1, -1):
            t0 = 1e12 - 0.01 if direction == 1 else 1e12
            t1 = 1e12 if direction == 1 else 1e12 - 0.01
            result = page.evaluate("""opts => MathStudio.odeTools.solveAdaptive(opts)""",
                                   {"expression": "1", "t0": t0, "t1": t1, "y0": 0})
            assert result["rows"][-1][0] == t1
            assert abs(result["rows"][-1][1] - (t1 - t0)) < 1e-12, result
            assert all(direction * (b[0] - a[0]) > 0
                       for a, b in zip(result["rows"], result["rows"][1:]))

        # A too-stiff problem cannot be accepted below the time resolution.
        underflow = page.evaluate("""() => {
            try {
                MathStudio.odeTools.solveAdaptive({
                    expression:'10000*y',t0:1e12-1/8192,t1:1e12,y0:1,
                    tolerance:1e-12,maxSteps:100
                });
                return '';
            } catch(e) { return e.message; }
        }""")
        assert "underflow" in underflow.lower() and "time resolution" in underflow.lower(), underflow

        # Ordinary forward/backward references remain accurate.
        for t0, t1, y0, expected in ((0, 1, 1, math.e), (1, 0, math.e, 1)):
            result = page.evaluate("""opts => MathStudio.odeTools.solveAdaptive(opts)""",
                                   {"expression": "y", "t0": t0, "t1": t1,
                                    "y0": y0, "tolerance": 1e-10})
            assert abs(result["rows"][-1][1] - expected) < 1e-8, result

        tiny = page.evaluate("""() => MathStudio.odeTools.solveAdaptive(
            {expression:'1',t0:0,t1:1e-300,y0:0}).rows.at(-1)""")
        assert tiny[0] == 1e-300 and abs(tiny[1] / 1e-300 - 1) < 1e-10, tiny

        # The smallest binary64 subnormal is a distinct endpoint even though span/20 rounds to zero.
        subnormal = math.ulp(0.0)
        for t0, t1, quantum_steps in ((0.0, subnormal, 1),
                                      (subnormal, 0.0, 1),
                                      (0.0, 2 * subnormal, 0),
                                      (2 * subnormal, 0.0, 0)):
            result = page.evaluate("""opts => MathStudio.odeTools.solveAdaptive(opts)""",
                                   {"expression": "1", "t0": t0, "t1": t1, "y0": 0})
            assert result["rows"][0][0] == t0
            assert result["rows"][-1][0] == t1
            assert result["rows"][-1][1] == t1 - t0, result
            assert result["steps"] == result["attempts"] == 1 and result["rejected"] == 0
            assert result["stageTimeCollisionAttempts"] == 1, result
            assert result["stageTimeCollisionAcceptedSteps"] == 1, result
            assert result["quantumLimitedAcceptedSteps"] == quantum_steps, result
            direction = 1 if t1 > t0 else -1
            assert all(direction * (b[0] - a[0]) > 0
                       for a, b in zip(result["rows"], result["rows"][1:]))


        # At a 20-ULP interval near 1e12, a later 5-ULP trial makes c=4/5
        # and c=8/9 round to the same timestamp; report the repeated fractional stage.
        ulp = 1 / 8192
        for direction in (1, -1):
            t0 = 1e12 - 20 * ulp if direction == 1 else 1e12
            t1 = 1e12 if direction == 1 else 1e12 - 20 * ulp
            result = page.evaluate("""opts => MathStudio.odeTools.solveAdaptive(opts)""",
                                   {"expression": "1", "t0": t0, "t1": t1, "y0": 0})
            assert result["rows"][0][0] == t0
            assert result["rows"][-1][0] == t1
            assert result["attempts"] == result["steps"] == 3 and result["rejected"] == 0
            assert result["stageTimeCollisionAttempts"] == 2, result
            assert result["stageTimeCollisionAcceptedSteps"] == 2, result
            assert result["quantumLimitedAcceptedSteps"] == 1, result
            assert all(direction * (b[0] - a[0]) > 0
                       for a, b in zip(result["rows"], result["rows"][1:]))



        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(el) => el.open = true")
        page.locator("#ode-method").select_option("rk45")
        page.locator("#ode-expression").fill("1")
        page.locator("#ode-start").fill(str(1e12 - 0.01))
        page.locator("#ode-end").fill("1000000000000")
        page.locator("#ode-initial").fill("0")
        page.locator("#ode-run").click()
        assert "RK45" in page.locator("#ode-output").inner_text()
        assert page.locator("#ode-to-table").is_enabled()
        page.locator("#ode-to-table").click()
        times = page.evaluate("""() => MathStudio.dataTables.tables.at(-1).rows
            .map(row => Number(row[0]))""")
        assert times[0] == 1e12 - 0.01 and times[-1] == 1e12, times
        assert all(a < b for a, b in zip(times, times[1:]))

        page.locator('[data-workspace="editor"]').click()
        page.locator("#ode-details").evaluate("(el) => el.open = true")
        page.locator("#ode-expression").fill("10000*y")
        page.locator("#ode-start").fill(str(1e12 - 1 / 8192))
        page.locator("#ode-initial").fill("1")
        page.locator("#ode-tolerance").fill("1e-12")
        page.locator("#ode-run").click()
        assert "underflow" in page.locator("#ode-output").inner_text().lower()
        assert page.locator("#ode-to-table").is_disabled()
        assert page.locator("#ode-to-graph").is_disabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert not errors, errors
        browser.close()
    print("PASS: RK45 large-epoch, subnormal, repeated-stage, exact endpoint, stiffness, UI and mobile")


if __name__ == "__main__":
    main()
