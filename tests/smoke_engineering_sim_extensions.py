"""Forced vibration, general/overhang/combined beam superposition, simulation export to Data
Tables/Graphs and PNG frame download: references, invalid input and responsive UI."""
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850}, accept_downloads=True)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def sim(kind, params):
            return page.evaluate("([k,p]) => MathStudio.engineeringSimulations[k](p)", [kind, params])

        def fails(kind, params, fragment):
            message = page.evaluate("([k,p]) => { try { MathStudio.engineeringSimulations[k](p); return null; } catch (e) { return e.message; } }", [kind, params])
            assert message and fragment in message, (kind, params, message)

        # --- Forced vibration: steady amplitude/phase vs closed-form frequency response.
        for zeta, r in ((0.1, 0.8), (0.05, 1.0), (0.3, 2.0), (0.7, 0.5)):
            v = sim("vibration", {"zeta": zeta, "ratio": r, "cycles": 40})
            amp = 1 / math.sqrt((1 - r * r) ** 2 + (2 * zeta * r) ** 2)
            phase = math.atan2(2 * zeta * r, 1 - r * r)
            assert rel(v["analyticAmplitude"], amp) < 1e-12
            tol = 1e-3 if v["transientLeft"] < 1e-4 else 0.05
            assert rel(v["measuredAmplitude"], amp) < tol, (zeta, r, v["measuredAmplitude"], amp, v["transientLeft"])
            assert abs(v["measuredPhase"] - phase) < 10 * tol, (zeta, r, v["measuredPhase"], phase)
        fails("vibration", {"zeta": 0, "ratio": 1}, "Damping ratio")
        fails("vibration", {"zeta": 0.1, "ratio": 9}, "Frequency ratio")

        # --- General beam solver reproduces closed forms (O(dx²) integration).
        base = {"length": 4, "modulus": 200, "width": 100, "height": 200}
        EI = 200e9 * 0.1 * 0.2 ** 3 / 12
        for support, loads, closed in (
                ("simply", [{"type": "point", "P": 10, "a": 2}], 10e3 * 4 ** 3 / (48 * EI)),
                ("simply", [{"type": "udl", "w": 5}], 5 * 5e3 * 4 ** 4 / (384 * EI)),
                ("cantilever", [{"type": "point", "P": 10, "a": 4}], 10e3 * 4 ** 3 / (3 * EI)),
                ("cantilever", [{"type": "udl", "w": 5}], 5e3 * 4 ** 4 / (8 * EI))):
            g = sim("beamGeneral", {**base, "support": support, "loads": loads})
            assert rel(abs(g["maxDeflection"]), closed) < 1e-5, (support, loads, g["maxDeflection"], closed)
        # Superposition: combined = sum of the closed-form single-load fields.
        parts = [sim("beam", {**base, "support": "simply", "load": "point", "force": 10, "position": 1}),
                 sim("beam", {**base, "support": "simply", "load": "point", "force": -4, "position": 3}),
                 sim("beam", {**base, "support": "simply", "load": "udl", "force": 2})]
        combo = sim("beam", {**base, "support": "simply", "load": "combined", "force": 10, "position": 1,
                             "force2": -4, "position2": 3, "udl": 2})
        summed = [sum(p_["deflection"][i] for p_ in parts) for i in range(201)]
        scale = max(abs(x) for x in summed)
        assert max(abs(combo["deflection"][i] - summed[i]) for i in range(201)) < 1e-5 * scale
        assert rel(combo["reactions"]["left"], sum(p_["reactions"]["left"] for p_ in parts)) < 1e-12
        momsum = [sum(p_["moment"][i] for p_ in parts) for i in range(201)]
        assert max(abs(combo["moment"][i] - momsum[i]) for i in range(201)) < 1e-6 * max(map(abs, momsum))
        # Overhang with tip load P at x = L, supports at 0 and xB: δtip = P c²(xB + c)/(3EI), c = L − xB.
        P, L, xB = 10e3, 4.0, 3.0
        c = L - xB
        o = sim("beam", {**base, "support": "overhang", "load": "point", "force": 10, "position": 4, "supportB": 3})
        assert rel(o["deflection"][-1], P * c * c * (xB + c) / (3 * EI)) < 1e-5, o["deflection"][-1]
        assert rel(o["reactions"]["left"], -P * c / xB) < 1e-12 and rel(o["reactions"]["right"], P * L / xB) < 1e-12
        assert abs(o["deflection"][150]) < 1e-9 * abs(o["deflection"][-1])  # zero at roller x = 3 m
        assert rel(abs(o["maxMoment"]), P * c) < 1e-9
        fails("beamGeneral", {**base, "support": "overhang", "supportB": 4, "loads": [{"type": "point", "P": 1, "a": 1}]}, "Right support")
        fails("beamGeneral", {**base, "support": "simply", "loads": []}, "1–8 loads")
        fails("beamGeneral", {**base, "support": "simply", "loads": [{"type": "moment", "P": 1}]}, "Load type")

        # --- UI: run vibration via catalog, export to Data Tables and Graphs, download PNG.
        page.locator('[data-workspace="engineering"]').click()
        status = page.locator("#eng-visual-status")
        assert page.locator("#eng-visual-table").is_disabled()
        page.locator("#eng-search").fill("vibration")
        page.locator('#eng-results article[data-tool-id="mechanical.vibration.forced"] button').click()
        assert status.inner_text().startswith("Forced vibration ζ = 0.1, r = 0.8"), status.inner_text()
        assert not page.locator("#eng-visual-table").is_disabled()
        with page.expect_download() as info:
            page.locator("#eng-visual-png").click()
        path = info.value.path()
        assert info.value.suggested_filename.startswith("ProMathStudio_vibration_frame")
        assert Path(path).read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#eng-visual-table").click()
        assert page.evaluate("MathStudio.advanced.currentMode()") == "data"
        tables = page.evaluate("MathStudio.dataTables.tables.map(t=>({name:t.name,columns:t.columns,rows:t.rows.length}))")
        assert len(tables) == before + 1 and tables[-1]["name"] == "SIM_VIBRATION", tables[-1]
        assert tables[-1]["columns"] == ["tau", "x_per_static", "dx_dtau"] and tables[-1]["rows"] == 1001
        page.locator('[data-workspace="engineering"]').click()
        page.locator("#eng-search").fill("beam")
        page.locator('#eng-results article[data-tool-id="structures.beam.deflection"] button').click()
        page.locator("#eng-visual-graph").click()
        assert page.locator("#graph-panel").is_visible()
        names = page.evaluate("MathStudio.dataTables.tables.map(t=>t.name)")
        assert "SIM_BEAM" in names, names
        beam_table = page.evaluate("MathStudio.dataTables.tables.find(t=>t.name==='SIM_BEAM')")
        assert beam_table["columns"] == ["x_m", "deflection_mm", "moment_kNm", "shear_kN"]
        assert abs(float(beam_table["rows"][100][1]) - 1.0) < 1e-9  # centre deflection 1.000 mm
        state = page.evaluate("MathStudio.graphData.getState()")
        assert state and len(state["points"]) == 201, state and len(state["points"])

        # Invalid run disables exports; recovery re-enables them; overhang via UI.
        page.locator('[data-workspace="engineering"]').click()
        page.locator("#eng-visual-support").select_option("overhang")
        page.locator("#eng-visual-supportB").fill("5")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: Right support position"), status.inner_text()
        assert page.locator("#eng-visual-table").is_disabled() and page.locator("#eng-visual-png").is_disabled()
        page.locator("#eng-visual-supportB").fill("3")
        page.locator("#eng-visual-position").fill("4")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Overhanging beam, 1 point load(s)"), status.inner_text()
        assert not page.locator("#eng-visual-table").is_disabled()
        for width in (390, 768):
            page.set_viewport_size({"width": width, "height": 844})
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            for button in ("#eng-visual-table", "#eng-visual-graph", "#eng-visual-png"):
                assert page.locator(button).bounding_box()["height"] >= 40, button
        assert not errors, errors
        browser.close()
    print("PASS forced vibration, beam superposition/overhang, Data Tables/Graph export and PNG download")


if __name__ == "__main__":
    main()
