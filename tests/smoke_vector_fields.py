"""Vector fields, RK4 streamlines and slope fields: numerical references (rotation circle, radial ray,
e^x, circle via dy/dx = -x/y), candidate equilibria, pole handling, invalid inputs with recovery,
reduced-motion (no autoplay), Play/Pause aria-pressed, keyboard, click seeding, Data Tables export
and 390/1280 layouts without page errors."""
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


def open_page(browser, errors, reduced=False, width=1280):
    context = browser.new_context(viewport={"width": width, "height": 900},
                                  reduced_motion="reduce" if reduced else "no-preference")
    page = context.new_page()
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
    page.on("dialog", lambda dialog: dialog.accept())
    page.set_content(HTML, wait_until="load")
    return context, page


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        errors = []
        context, page = open_page(browser, errors)
        api = lambda script: page.evaluate(script)

        # Rotation field (-y, x): the streamline from (1, 0) stays on the unit circle for one revolution.
        rot = api("""() => { const r = MathStudio.vectorFields.streamline('-y', 'x', [1, 0]);
            let turn = 0; for (let k = 1; k < r.points.length; k++) { const a = r.points[k - 1], b = r.points[k];
              turn += Math.atan2(a[0] * b[1] - a[1] * b[0], a[0] * b[0] + a[1] * b[1]); }
            return {reason: r.forward.reason, len: r.forward.length, turn,
                    dev: Math.max(...r.points.map(p => Math.abs(Math.hypot(p[0], p[1]) - 1)))}; }""")
        assert rot["reason"] == "closed" and rot["dev"] < 1e-6, rot
        assert abs(rot["turn"] - 2 * math.pi) < 0.05 and abs(rot["len"] - 2 * math.pi) < 0.05, rot
        long_rot = api("""() => { const r = MathStudio.vectorFields.streamline('-y', 'x', [1.5, 0], {closed: false, maxLength: 30, direction: 'forward'});
            return {reason: r.forward.reason, dev: Math.max(...r.points.map(p => Math.abs(Math.hypot(p[0], p[1]) - 1.5)))}; }""")
        assert long_rot["reason"] == "max-length" and long_rot["dev"] < 1e-6, long_rot

        # Radial field (x, y): the streamline through (1, 0.5) is the ray y = x/2; forward hits the
        # corner (2, 1) and backward stagnates at the origin.
        rad = api("""() => { const r = MathStudio.vectorFields.streamline('x', 'y', [1, 0.5]);
            const z = r.points[r.points.length - 1], a = r.points[0];
            return {f: r.forward.reason, b: r.backward.reason, end: z, start: a,
                    ray: Math.max(...r.points.map(p => Math.abs(p[1] - 0.5 * p[0]))),
                    pos: r.points.every(p => p[0] > 0)}; }""")
        assert rad["f"] == "edge" and rad["b"] == "stagnation" and rad["ray"] < 1e-12 and rad["pos"], rad
        assert abs(rad["end"][0] - 2) < 1e-12 and abs(rad["end"][1] - 1) < 1e-12, rad
        assert math.hypot(*rad["start"]) < 0.05, rad

        # Slope field dy/dx = y through (0, 1) matches e^x at x = 1; dy/dx = -x/y traces the unit circle.
        exp = api("""() => { const s = MathStudio.vectorFields.solution('y', [0, 1], {ymax: 4});
            const p = s.points.find(q => Math.abs(q[0] - 1) < 1e-12), m = s.points.find(q => Math.abs(q[0] + 1) < 1e-12);
            const sorted = s.points.every((q, k) => k === 0 || q[0] > s.points[k - 1][0]);
            return {y1: p && p[1], ym1: m && m[1], sorted, f: s.forward.reason, b: s.backward.reason}; }""")
        assert abs(exp["y1"] - math.e) < 1e-6 and abs(exp["ym1"] - math.exp(-1)) < 1e-6, exp
        assert exp["sorted"] and exp["f"] == "edge" and exp["b"] == "edge", exp
        circ = api("""() => { const s = MathStudio.vectorFields.solution('-x/y', [0, 1]);
            const pts = s.points.filter(p => Math.abs(p[0]) <= 0.95);
            return {n: pts.length, dev: Math.max(...pts.map(p => Math.abs(Math.hypot(p[0], p[1]) - 1))),
                    f: s.forward.reason, b: s.backward.reason, x0: s.points[0][0], x1: s.points[s.points.length - 1][0]}; }""")
        assert circ["n"] > 180 and circ["dev"] < 1e-6, circ
        assert circ["f"] == "steep" and circ["b"] == "steep" and circ["x1"] > 0.95 and circ["x0"] < -0.95, circ

        # Candidate equilibria: origin for (-y, x) (centre), (1, 0) for (x - 1, y); odd grids dedupe.
        eq = api("""() => { const V = MathStudio.vectorFields;
            return {rot: V.equilibria('-y', 'x'), rotOdd: V.equilibria('-y', 'x', {grid: 21}), shift: V.equilibria('x - 1', 'y'),
                    none: V.equilibria('1', 'x'), saddle: V.equilibria('x', '-y', {grid: 7})}; }""")
        assert len(eq["rot"]) == 1 and math.hypot(eq["rot"][0]["x"], eq["rot"][0]["y"]) < 1e-9, eq["rot"]
        assert eq["rot"][0]["refined"] and eq["rot"][0]["kind"].startswith("center"), eq["rot"]
        assert len(eq["rotOdd"]) == 1 and math.hypot(eq["rotOdd"][0]["x"], eq["rotOdd"][0]["y"]) < 1e-9, eq["rotOdd"]
        assert len(eq["shift"]) == 1 and abs(eq["shift"][0]["x"] - 1) < 1e-9 and abs(eq["shift"][0]["y"]) < 1e-9, eq["shift"]
        assert eq["shift"][0]["kind"] == "unstable node", eq["shift"]
        assert eq["none"] == [] and eq["saddle"][0]["kind"] == "saddle", eq

        # Pole fields: non-finite grid points are skipped; a streamline across x = 0 stops, no crash.
        pole = api("""() => { const V = MathStudio.vectorFields; const q = V.quiver('1/x', '1', {grid: 21});
            const s = V.streamline('1/x', '0', [-1, 0.5]); const t = V.streamline('1/x', '1', [-0.5, 0]);
            const sf = V.slopeField('1/x', {grid: 21}); const sol = V.solution('1/x', [-1, 0], {ymin: -10});
            return {nf: q.nonFinite, arrows: q.arrows.length, b: s.backward.reason, f: s.forward.reason,
                    t: [t.forward.reason, t.backward.reason], sfnf: sf.nonFinite, sol: sol.forward.reason,
                    allFinite: [s, t, sol].every(r => r.points.every(p => Number.isFinite(p[0]) && Number.isFinite(p[1])))}; }""")
        assert pole["nf"] == 21 and pole["arrows"] == 441, pole
        assert pole["b"] in ("singular", "non-finite") and pole["f"] == "edge", pole
        assert pole["sfnf"] == 21 and pole["sol"] in ("steep", "non-finite") and pole["allFinite"], pole

        # API negative cases.
        for script, expected in [
            ("MathStudio.vectorFields.quiver('', 'x')", "empty"),
            ("MathStudio.vectorFields.quiver('x', 'y', {grid: 41})", "2 to 40"),
            ("MathStudio.vectorFields.quiver('x', 'y', {grid: 1})", "2 to 40"),
            ("MathStudio.vectorFields.quiver('x', 'y', {xmin: 1, xmax: 1})", "greater than"),
            ("MathStudio.vectorFields.quiver('x + q', 'y')", "Unknown variable"),
            ("MathStudio.vectorFields.quiver('x +', 'y')", "Complete the expression"),
            ("MathStudio.vectorFields.quiver('sqrt(-1-x^2)', 'y')", "not finite"),
            ("MathStudio.vectorFields.quiver('x = 1', 'y')", "not an equation"),
            ("MathStudio.vectorFields.streamline('x', 'y', [1, 0], {step: 0.5})", "Step fraction"),
            ("MathStudio.vectorFields.streamline('x', 'y', [NaN, 0])", "finite"),
            ("MathStudio.vectorFields.streamline('x', 'y', [1, 0], {direction: 'up'})", "Direction"),
            ("MathStudio.vectorFields.solution('y', [5, 0])", "outside the window"),
            ("MathStudio.vectorFields.solution('1/x', [0, 0])", "not finite"),
            ("MathStudio.vectorFields.parseSeeds('1, 2, 3')", "must be"),
        ]:
            message = api("() => { try { " + script + "; return 'NO ERROR'; } catch (e) { return e.message; } }")
            assert expected in message, (script, message)
        outside = api("() => MathStudio.vectorFields.streamline('x', 'y', [5, 5]).forward.reason")
        assert outside == "outside", outside

        # UI: the panel sits right after the curves panel; open by keyboard.
        page.locator('[data-workspace="graph"]').click()
        assert page.evaluate("document.getElementById('curves-details').nextElementSibling.id") == "fields-details"
        details = page.locator("#fields-details")
        details.locator("summary").focus()
        page.keyboard.press("Enter")
        assert details.evaluate("el => el.open")
        status, canvas, play = page.locator("#fields-status"), page.locator("#fields-canvas"), page.locator("#fields-play")
        assert status.get_attribute("role") == "status" and status.get_attribute("aria-live") == "polite"
        assert canvas.get_attribute("role") == "img" and play.get_attribute("aria-pressed") == "false"
        page.locator("#fields-plot").focus()
        page.keyboard.press("Enter")
        text = status.inner_text()
        assert text.startswith("Vector field: 400 finite of 400 arrows") and "17 streamlines" in text, text
        label = canvas.get_attribute("aria-label")
        assert "P = -y, Q = x" in label and "candidate equilibria at (0, 0)" in label, label
        assert "center" in page.locator("#fields-equilibria").inner_text()
        # Without reduced motion the particle animation autoplays and Pause toggles aria-pressed.
        page.wait_for_function("MathStudio.vectorFields.animation.frames > 3")
        assert play.get_attribute("aria-pressed") == "true" and play.inner_text() == "Pause particles"
        play.focus()
        page.keyboard.press("Enter")
        assert play.get_attribute("aria-pressed") == "false" and not page.evaluate("MathStudio.vectorFields.animation.playing")
        page.locator("#fields-plot").click()
        assert not page.evaluate("MathStudio.vectorFields.animation.playing"), "user pause must persist across replots"
        ink = page.evaluate("""() => { const c = document.getElementById('fields-canvas'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            let dark = 0, colour = 0; for (let i = 0; i < d.length; i += 4) { if (d[i] < 40 && d[i + 1] < 50 && d[i + 2] < 60) dark++;
              if (Math.max(d[i], d[i + 1], d[i + 2]) - Math.min(d[i], d[i + 1], d[i + 2]) > 80) colour++; } return {dark, colour}; }""")
        assert ink["dark"] > 1500 and ink["colour"] > 1500, ink

        # Click-to-seed adds a point and replots.
        box = canvas.bounding_box()
        canvas.click(position={"x": box["width"] * 0.3, "y": box["height"] * 0.4})
        assert page.locator("#fields-seeds").input_value().count(";") == 1, page.locator("#fields-seeds").input_value()
        assert "18 streamlines" in status.inner_text(), status.inner_text()

        # Invalid UI inputs then recovery.
        page.locator("#fields-p").fill("")
        page.locator("#fields-plot").click()
        assert "empty" in status.inner_text() and "fields-error" in status.get_attribute("class")
        assert page.locator("#fields-save").is_disabled() and play.is_disabled()
        page.locator("#fields-p").fill("-y")
        page.locator("#fields-grid-n").fill("60")
        page.locator("#fields-plot").click()
        assert "2 to 40" in status.inner_text(), status.inner_text()
        page.locator("#fields-grid-n").fill("20")
        page.locator("#fields-seeds").fill("1, 0; abc, 2")
        page.locator("#fields-plot").click()
        assert "Seed 2 x" in status.inner_text(), status.inner_text()
        page.locator("#fields-seeds").fill("1, 0")
        page.locator("#fields-auto").uncheck()
        page.locator("#fields-seeds").press("Enter")
        assert "1 streamline (ends: 1 closed orbit)" in status.inner_text(), status.inner_text()
        assert "fields-error" not in (status.get_attribute("class") or "")

        # Pole field through the UI.
        page.locator("#fields-p").fill("1/x")
        page.locator("#fields-q").fill("1")
        page.locator("#fields-grid-n").fill("21")
        page.locator("#fields-seeds").fill("-1, 0.5")
        page.locator("#fields-plot").click()
        assert "21 non-finite grid points skipped" in status.inner_text(), status.inner_text()

        # Save streamline points to Data Tables.
        page.locator("#fields-p").fill("-y")
        page.locator("#fields-q").fill("x")
        page.locator("#fields-seeds").fill("1, 0; 0.5, 0")
        page.locator("#fields-plot").click()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#fields-save").click()
        assert "Saved" in status.inner_text() and "Streamlines" in status.inner_text(), status.inner_text()
        table = page.evaluate("(() => { const t = MathStudio.dataTables.tables, l = t[t.length - 1]; return {n: t.length, cols: l.columns.map(c => c.name || c), rows: l.rows.length}; })()")
        assert table["n"] == before + 1 and table["rows"] > 600 and table["cols"][:3] == ["curve", "x", "y"], table
        page.locator('[data-workspace="graph"]').click()

        # Slope mode: solution curves through typed points.
        page.locator("#fields-mode").select_option("slope")
        assert page.locator("#fields-f").is_visible() and not page.locator("#fields-p").is_visible() and not play.is_visible()
        page.locator("#fields-f").fill("y")
        page.locator("#fields-seeds").fill("0, 1; 0, -1")
        page.locator("#fields-plot").click()
        assert status.inner_text().startswith("Slope field: 441 finite of 441 line elements; 2 solution curves (ends: 4 edge)"), status.inner_text()
        assert not page.evaluate("MathStudio.vectorFields.animation.playing")
        page.locator("#fields-seeds").fill("9, 9")
        page.locator("#fields-plot").click()
        assert "outside the window" in status.inner_text(), status.inner_text()
        page.locator("#fields-seeds").fill("0, 1")
        page.locator("#fields-plot").click()

        # Responsive layouts: no horizontal overflow and touch-sized controls.
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#fields-plot").click()
            assert status.inner_text().startswith("Slope field:"), status.inner_text()
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            for sel in ("#fields-plot", "#fields-save", "#fields-clear-seeds", "#fields-mode", "#fields-f", "#fields-seeds", "#fields-step"):
                b = page.locator(sel).bounding_box()
                assert b["height"] >= 40, (width, sel, b)
            cbox, dbox = canvas.bounding_box(), details.bounding_box()
            assert cbox["x"] + cbox["width"] <= dbox["x"] + dbox["width"] + 1, (width, cbox, dbox)
        context.close()

        # Reduced motion: no autoplay; explicit Play works and Pause stops.
        context, page = open_page(browser, errors, reduced=True, width=390)
        page.locator('[data-workspace="graph"]').click()
        page.locator("#fields-details summary").click()
        page.locator("#fields-plot").click()
        page.wait_for_timeout(250)
        assert page.evaluate("MathStudio.vectorFields.animation.frames") == 0
        assert page.locator("#fields-play").get_attribute("aria-pressed") == "false"
        page.locator("#fields-play").click()
        page.wait_for_function("MathStudio.vectorFields.animation.frames > 2")
        assert page.locator("#fields-play").get_attribute("aria-pressed") == "true"
        page.locator("#fields-play").click()
        assert not page.evaluate("MathStudio.vectorFields.animation.playing")
        overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
        assert overflow <= 1, overflow
        context.close()

        assert not errors, errors
        browser.close()
    print("PASS vector fields: rotation circle, radial ray, e^x, -x/y circle, equilibria, poles, negative cases, "
          "keyboard, click seeding, Data Tables, reduced motion, 390/1280")


if __name__ == "__main__":
    main()
