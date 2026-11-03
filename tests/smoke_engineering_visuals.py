"""Engineering Toolbox animations: analytic references through existing solvers, invalid-input
recovery, reduced motion, keyboard, 390/768/1280 layout and project round trip."""
import json
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def compute(kind, params):
            return page.evaluate("([k,p]) => MathStudio.engineeringVisuals.compute[k](p)", [kind, params])

        # Second-order step response vs analytic underdamped solution.
        zeta, wn = 0.2, 2.0
        spring = compute("spring", {"zeta": zeta, "wn": wn, "duration": 10})
        wd = wn * math.sqrt(1 - zeta ** 2)
        exact = lambda t: 1 - math.exp(-zeta * wn * t) * (math.cos(wd * t) + zeta / math.sqrt(1 - zeta ** 2) * math.sin(wd * t))
        assert max(abs(x - exact(t)) for t, x, _ in spring["rows"]) < 1e-5, "RK4 spring vs analytic"
        assert abs(spring["overshoot"] - math.exp(-math.pi * zeta / math.sqrt(1 - zeta ** 2))) < 2e-3, spring["overshoot"]
        critical = compute("spring", {"zeta": 1, "wn": 2, "duration": 10})
        assert critical["overshoot"] < 1e-9, critical["overshoot"]

        # Small-angle pendulum period and energy conservation.
        pend = compute("pendulum", {"theta0": 5, "length": 1, "duration": 6})
        rows = pend["rows"]
        crossings = [rows[i][0] - rows[i][1] * (rows[i + 1][0] - rows[i][0]) / (rows[i + 1][1] - rows[i][1])
                     for i in range(len(rows) - 1) if rows[i][1] > 0 >= rows[i + 1][1]]
        assert len(crossings) >= 2, crossings
        period = crossings[1] - crossings[0]
        assert abs(period - 2 * math.pi * math.sqrt(1 / 9.80665)) / period < 1e-3, period
        assert pend["relativeEnergyDrift"] < 1e-6, pend["relativeEnergyDrift"]

        # FFT amplitudes for bin-aligned tones (exact up to roundoff).
        spec = compute("spectrum", {"f1": 5, "f2": 12, "a1": 1, "a2": 0.5})
        amps = [b["amplitude"] for b in spec["bins"]]
        assert abs(amps[5] - 1) < 1e-12 and abs(amps[12] - 0.5) < 1e-12, amps[:14]
        assert max(a for k, a in enumerate(amps) if k not in (5, 12)) < 1e-12

        # Bisection: Wallis cubic root, width halves exactly.
        bis = compute("bisection", {"expression": "x^3-2*x-5", "lo": 1, "hi": 3, "steps": 14})
        root = 2.0945514815423265
        a, b = bis["brackets"][-1]
        assert a <= root <= b and abs((b - a) - 2 / 2 ** 14) < 1e-15, bis["brackets"][-1]
        assert all(x[0] <= root <= x[1] for x in bis["brackets"])

        quad = compute("quadrature", {"expression": "sin(x)", "a": 0, "b": math.pi})
        assert abs(quad["value"] - 2) < 1e-8, quad["value"]
        eig = compute("eigen", {"a": 2, "b": 1, "d": 1})
        phi = (1 + math.sqrt(5)) / 2
        assert abs(eig["values"][0] - phi ** 2) < 1e-12 and abs(eig["values"][1] - 1 / phi ** 2) < 1e-12, eig["values"]

        # Every visual is linked to an available catalog tool.
        tools = page.evaluate("Object.fromEntries(MathStudio.engineeringCatalog.tools.map(t=>[t.id,t.status]))")
        visuals = page.evaluate("MathStudio.engineeringVisuals.visuals")
        assert len(visuals) == 12 and all(tools[v["tool"]] == "available" for v in visuals), visuals

        page.locator('[data-workspace="engineering"]').click()
        assert page.locator("#eng-results [data-visual]").count() == 12
        assert page.locator("#eng-results .eng-card button[data-visual]").count() == 0
        status = page.locator("#eng-visual-status")
        assert status.get_attribute("aria-live") == "polite"
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            note = page.locator('#eng-results [data-tool-id="signals.fft.1d"] [data-visual]')
            assert note.inner_text().startswith("▶ Animation available: Two-tone signal")
            # Keyboard: open the disclosure, choose the visual and run it without a pointer.
            page.locator("#eng-visuals > summary").focus()
            if not page.locator("#eng-visuals").evaluate("el => el.open"):
                page.keyboard.press("Enter")
            page.locator("#eng-visual-select").focus()
            page.locator("#eng-visual-select").select_option("spectrum")
            page.locator("#eng-visual-run").focus()
            page.keyboard.press("Enter")
            assert status.inner_text().startswith("Two-tone signal"), status.inner_text()
            assert page.locator("#eng-visual-canvas").get_attribute("aria-label").startswith("Two-tone signal and FFT spectrum")
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            canvas_box = page.locator("#eng-visual-canvas").bounding_box()
            assert canvas_box["width"] <= width, canvas_box
            for button in ("#eng-visual-run", "#eng-visual-toggle", "#eng-visual-step"):
                assert page.locator(button).bounding_box()["height"] >= 40, button

        # Animation advances, pauses and steps.
        page.wait_for_function("() => MathStudio.engineeringVisuals.frame() > 5")
        page.locator("#eng-visual-toggle").click()
        assert page.locator("#eng-visual-toggle").get_attribute("aria-pressed") == "true"
        paused = page.evaluate("MathStudio.engineeringVisuals.frame()")
        page.wait_for_timeout(200)
        assert page.evaluate("MathStudio.engineeringVisuals.frame()") == paused
        page.locator("#eng-visual-step").click()
        assert page.evaluate("MathStudio.engineeringVisuals.frame()") > paused

        # Invalid inputs report an error and the next valid run recovers.
        page.locator("#eng-visual-select").select_option("bisection")
        page.locator("#eng-visual-lo").fill("3")
        page.locator("#eng-visual-hi").fill("4")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: f(min) and f(max) must have opposite signs"), status.inner_text()
        assert status.evaluate("el => el.classList.contains('error')")
        page.locator("#eng-visual-expression").fill("x^^2")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate:"), status.inner_text()
        page.locator("#eng-visual-select").select_option("spring")
        page.locator("#eng-visual-zeta").fill("-1")
        page.locator("#eng-visual-run").click()
        assert "Damping ratio" in status.inner_text()
        page.locator("#eng-visual-zeta").fill("0.5")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Mass–spring–damper unit step: ζ=0.5")
        assert not status.evaluate("el => el.classList.contains('error')")

        # Saved-project round trip keeps the visual module functional.
        saved = page.evaluate("MathStudio.bridge.export()")
        page.locator("#hub-project-file").set_input_files({"name": "p.json", "mimeType": "application/json",
                                                           "buffer": json.dumps(saved).encode("utf-8")})
        page.wait_for_function("() => document.querySelector('#hub-status').textContent.startsWith('Project imported.')")
        assert page.evaluate("MathStudio.engineeringVisuals.compute.eigen({a:1,b:0,d:3}).values") == [3, 1]

        # Reduced motion: no autoplay; final frame drawn immediately.
        reduced = browser.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        reduced.on("pageerror", lambda error: errors.append(str(error)))
        reduced.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        reduced.locator('[data-workspace="engineering"]').click()
        reduced.locator("#eng-visuals > summary").click()
        reduced.locator("#eng-visual-select").select_option("eigen")
        reduced.locator("#eng-visual-run").click()
        frames = reduced.evaluate("MathStudio.engineeringVisuals.frames")
        assert reduced.evaluate("MathStudio.engineeringVisuals.frame()") == frames
        assert reduced.locator("#eng-visual-toggle").get_attribute("aria-pressed") == "true"
        assert not errors, errors
        browser.close()
    print("PASS engineering animations: references, keyboard, reduced motion, 390/768/1280, recovery, project round trip")


if __name__ == "__main__":
    main()
