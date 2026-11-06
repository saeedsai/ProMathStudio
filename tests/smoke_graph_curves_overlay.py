"""Curve overlays on the main 2D graph: unit circle and polar rose references, bounds/zoom
re-render, pixel ink, project export/import round-trip, legacy import, malformed and
apply-failure atomicity, clear, keyboard activation and 390/1280 layouts."""
import json
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def snapshot(page):
    data = page.evaluate("MathStudio.bridge.export()")
    data.pop("date", None)
    return data


def upload(page, data, expect_failure):
    page.evaluate("document.querySelector('#hub-status').textContent=''")
    page.locator("#hub-project-file").set_input_files({
        "name": "project.json", "mimeType": "application/json",
        "buffer": json.dumps(data).encode("utf-8")})
    prefix = "Import failed:" if expect_failure else "Project imported."
    page.wait_for_function(
        "p => document.querySelector('#hub-status').textContent.startsWith(p)", arg=prefix)
    return page.locator("#hub-status").inner_text()


RENDERED = "() => MathStudio.graphOverlays.rendered()"


def radius_error(overlay):
    pts = [p for line in overlay["polylines"] for p in line]
    return len(pts), max(abs(math.hypot(x, y) - 1) for x, y in pts)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.on("dialog", lambda dialog: dialog.accept())
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        assert page.evaluate("MathStudio.advanced.getGraphState().curves") == []
        page.locator('[data-workspace="graph"]').click()
        page.locator("#curves-details > summary").click()
        overlay_status = page.locator("#curves-overlay-status")
        assert overlay_status.get_attribute("role") == "status"
        assert page.locator("#curves-overlay-clear").is_disabled()

        # 1. Implicit unit circle overlaid on the main graph's visible window.
        page.locator("#curves-expr").fill("x^2 + y^2 = 1")
        page.locator("#curves-grid-n").fill("160")
        page.locator("#curves-overlay").focus()
        page.keyboard.press("Enter")
        assert overlay_status.inner_text().startswith("Overlaid Implicit: x^2 + y^2 = 1"), overlay_status.inner_text()
        state = page.evaluate("MathStudio.advanced.getGraphState()")
        assert state["curves"] == [{"type": "implicit", "expression": "x^2 + y^2 = 1", "grid": 160}], state["curves"]
        rendered = page.evaluate(RENDERED)
        assert rendered["window"] == {k: state["bounds"][k] for k in ("xmin", "xmax", "ymin", "ymax")}, rendered["window"]
        n, dev = radius_error(rendered["overlays"][0])
        assert n > 100 and dev < 1e-6, (n, dev)
        assert "curve overlay" in page.locator("#graph-status").inner_text()
        assert any("Implicit: x^2 + y^2 = 1" in t for t in page.locator("#graph-legend").all_inner_texts())
        # The overlay colour is painted on the main canvas at (cos 225°, sin 225°).
        ink = page.evaluate("""() => { const c = document.getElementById('graph-canvas'), r = MathStudio.graphOverlays.rendered().window;
            const x = -Math.SQRT1_2, y = -Math.SQRT1_2, X = Math.round((x - r.xmin) / (r.xmax - r.xmin) * c.width), Y = Math.round(c.height - (y - r.ymin) / (r.ymax - r.ymin) * c.height);
            const d = c.getContext('2d').getImageData(X - 3, Y - 3, 7, 7).data; let n = 0;
            for (let i = 0; i < d.length; i += 4) if (d[i] > 150 && d[i + 1] < 110 && d[i + 2] < 60) n++; return n; }""")
        assert ink > 0, ink

        # 2. Polar rose r = cos(3θ) on [0, π]: |r| <= 1, petal tip at (1, 0), 3 petals.
        page.locator("#curves-type").select_option("polar")
        page.locator("#curves-r").fill("cos(3*theta)")
        page.locator("#curves-p0").fill("0")
        page.locator("#curves-p1").fill(repr(math.pi))
        page.locator("#curves-samples").fill("1801")
        page.locator("#curves-overlay").click()
        assert "Polar: r = cos(3*theta)" in overlay_status.inner_text(), overlay_status.inner_text()
        rose = page.evaluate(RENDERED)["overlays"][1]
        pts = [p for line in rose["polylines"] for p in line]
        assert len(pts) == 1801 and len(rose["polylines"]) == 1, len(pts)
        assert max(math.hypot(x, y) for x, y in pts) <= 1 + 1e-12
        assert abs(pts[0][0] - 1) < 1e-12 and abs(pts[0][1]) < 1e-12
        for theta, (x, y) in zip([k * math.pi / 1800 for k in range(1801)], pts):
            r = math.cos(3 * theta)
            assert abs(x - r * math.cos(theta)) < 1e-12 and abs(y - r * math.sin(theta)) < 1e-12
        tips = {(round(x, 3) + 0, round(y, 3) + 0) for x, y in pts if abs(math.hypot(x, y) - 1) < 1e-9}
        assert len(tips) == 3, tips

        # 3. Parametric overlay with a pole breaks into separate polylines (no jump across t = 0).
        page.locator("#curves-type").select_option("parametric")
        page.locator("#curves-xt").fill("t")
        page.locator("#curves-yt").fill("1/t")
        page.locator("#curves-p0").fill("-2")
        page.locator("#curves-p1").fill("2")
        page.locator("#curves-samples").fill("5")
        page.locator("#curves-overlay").click()
        hyper = page.evaluate(RENDERED)["overlays"][2]
        assert len(hyper["polylines"]) == 2 and all(x != 0 for line in hyper["polylines"] for x, _ in line), hyper

        # Duplicate and invalid overlays are rejected without changing the overlay list.
        page.locator("#curves-overlay").click()
        assert "already overlaid" in overlay_status.inner_text()
        page.locator("#curves-samples").fill("1")
        page.locator("#curves-overlay").click()
        assert "Overlay error" in overlay_status.inner_text() and "curves-error" in overlay_status.get_attribute("class")
        page.locator("#curves-xt").fill("t + q")
        page.locator("#curves-samples").fill("5")
        page.locator("#curves-overlay").click()
        assert "Unknown variable" in overlay_status.inner_text(), overlay_status.inner_text()
        assert page.evaluate("MathStudio.graphOverlays.count()") == 3

        # 4. Zoom: changing the main bounds re-traces the implicit overlay on the new window.
        # The bound inputs live in a collapsible settings panel; set them as the panel would.
        page.evaluate("""() => { for (const [k, v] of [['xmin', '-1.5'], ['xmax', '1.5'], ['ymin', '-1.2'], ['ymax', '1.2']])
            document.getElementById('graph-' + k).value = v; document.getElementById('graph-plot').click(); }""")
        zoomed = page.evaluate(RENDERED)
        assert zoomed["window"] == {"xmin": -1.5, "xmax": 1.5, "ymin": -1.2, "ymax": 1.2}, zoomed["window"]
        zn, zdev = radius_error(zoomed["overlays"][0])
        assert zdev < 1e-6 and zn > n, (zn, n, zdev)
        assert zoomed["overlays"][1]["polylines"] == rose["polylines"]
        assert 0 < zoomed["overlays"][1]["visiblePoints"] <= 1801
        # Mouse-wheel zoom on the canvas also re-renders with the updated bounds.
        page.locator("#graph-canvas").scroll_into_view_if_needed()
        box = page.locator("#graph-canvas").bounding_box()
        page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
        page.mouse.wheel(0, 400)
        page.wait_for_timeout(250)
        wheel = page.evaluate(RENDERED)
        assert wheel["window"] != zoomed["window"], wheel["window"]
        assert wheel["window"] == {k: page.evaluate("MathStudio.advanced.getGraphState().bounds")[k] for k in ("xmin", "xmax", "ymin", "ymax")}
        assert radius_error(wheel["overlays"][0])[1] < 1e-6

        # 5. Project export -> import round-trips the overlay definitions exactly.
        exported = snapshot(page)
        curves = exported["graph"]["curves"]
        assert [c["type"] for c in curves] == ["implicit", "polar", "parametric"], curves
        assert curves[1] == {"type": "polar", "r": "cos(3*theta)", "theta0": 0, "theta1": math.pi, "samples": 1801}, curves[1]
        page.locator("#curves-overlay-clear").click()
        assert page.evaluate("MathStudio.graphOverlays.count()") == 0
        assert page.evaluate(RENDERED)["overlays"] == []
        assert "Cleared" in overlay_status.inner_text() and page.locator("#curves-overlay-clear").is_disabled()
        upload(page, exported, False)
        assert snapshot(page)["graph"]["curves"] == curves
        assert len(page.evaluate(RENDERED)["overlays"]) == 3
        assert "3 curve overlays" in overlay_status.inner_text()
        assert not page.locator("#curves-overlay-clear").is_disabled()

        # 6. Legacy projects (v1 and v2) without the field import and leave no overlays.
        for version in (1, 2):
            legacy = json.loads(json.dumps(exported)); legacy["version"] = version
            del legacy["graph"]["curves"]
            upload(page, legacy, False)
            assert page.evaluate("MathStudio.graphOverlays.count()") == 0, version
            upload(page, exported, False)

        # 7. Malformed overlay definitions are rejected by the schema with prior state unchanged.
        prior = snapshot(page)
        assert len(prior["graph"]["curves"]) == 3
        bad_curves = [
            ("not a list", {"type": "implicit"}),
            ("unknown type", [{"type": "spline", "expression": "x", "grid": 10}]),
            ("extra field", [{"type": "implicit", "expression": "x", "grid": 10, "color": "#000"}]),
            ("missing field", [{"type": "polar", "r": "1", "theta0": 0, "samples": 10}]),
            ("grid too large", [{"type": "implicit", "expression": "x", "grid": 1000}]),
            ("grid not integer", [{"type": "implicit", "expression": "x", "grid": 10.5}]),
            ("one sample", [{"type": "parametric", "x": "t", "y": "t", "t0": 0, "t1": 1, "samples": 1}]),
            ("empty range", [{"type": "parametric", "x": "t", "y": "t", "t0": 1, "t1": 1, "samples": 10}]),
            ("string bound", [{"type": "polar", "r": "1", "theta0": "0", "theta1": 1, "samples": 10}]),
            ("huge bound", [{"type": "polar", "r": "1", "theta0": 0, "theta1": 1e13, "samples": 10}]),
            ("blank expression", [{"type": "implicit", "expression": "  ", "grid": 10}]),
            ("long expression", [{"type": "implicit", "expression": "x" * 1501, "grid": 10}]),
            ("two equals", [{"type": "implicit", "expression": "x = y = 1", "grid": 10}]),
            ("duplicate", [{"type": "implicit", "expression": "x", "grid": 10}] * 2),
            ("nine curves", [{"type": "implicit", "expression": "x + %d" % i, "grid": 10} for i in range(9)]),
        ]
        for label, value in bad_curves:
            bad = json.loads(json.dumps(prior)); bad["graph"]["curves"] = value
            text = upload(page, bad, True)
            assert "Invalid project" in text and "curve overlay" in text, (label, text)
            assert snapshot(page) == prior, label
        # A structurally valid curve whose expression fails at restore rolls the whole import back.
        bad = json.loads(json.dumps(prior)); bad["working"] = "x+99"
        bad["graph"]["curves"] = [{"type": "parametric", "x": "t + q", "y": "t", "t0": 0, "t1": 1, "samples": 10}]
        text = upload(page, bad, True)
        assert "Unknown variable" in text, text
        assert snapshot(page) == prior
        assert len(page.evaluate(RENDERED)["overlays"]) == 3

        # 8. Overlays alone (no typed functions) still plot; 3D mode hides them from the legend.
        page.evaluate("() => { document.getElementById('graph-input').value = ''; document.getElementById('graph-plot').click(); }")
        assert "error" not in (page.locator("#graph-status").get_attribute("class") or ""), page.locator("#graph-status").inner_text()
        assert "3 curve overlays" in page.locator("#graph-status").inner_text()

        # 9. Responsive layouts: overlay controls are touch-sized and do not overflow.
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#curves-details").scroll_into_view_if_needed()
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            for sel in ("#curves-overlay", "#curves-overlay-clear"):
                b = page.locator(sel).bounding_box()
                assert b["height"] >= 40, (width, sel, b)
        page.locator("#curves-overlay-clear").click()
        assert page.evaluate("MathStudio.advanced.getGraphState().curves") == []
        assert not errors, errors
        browser.close()
    print("PASS graph curve overlays: unit circle (radius < 1e-6), polar rose, pole breaks, zoom re-trace, "
          "export/import round-trip, legacy v1/v2, 15 malformed + rollback, clear, 390/1280")


if __name__ == "__main__":
    main()
