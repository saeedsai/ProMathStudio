"""Implicit, parametric and polar 2D curves: numerical references, pole rejection, negative
inputs with recovery, keyboard activation, Data Tables export and 390/768/1280 layouts."""
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


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

        api = lambda script, arg=None: page.evaluate(script, arg)

        # Unit circle: every refined vertex lies on r = 1 and all four quadrants are covered.
        circle = api("""() => { const r = MathStudio.graphCurves.implicit('x^2 + y^2 = 1', {grid: 300});
            const pts = r.segments.flatMap(s => [[s[0], s[1]], [s[2], s[3]]]);
            const q = [0, 0, 0, 0]; pts.forEach(([x, y]) => { q[(x >= 0 ? 0 : 1) + (y >= 0 ? 0 : 2)]++; });
            return {n: r.segmentCount, rej: r.rejected, res: r.maxResidual, q,
                    dev: Math.max(...pts.map(([x, y]) => Math.abs(Math.hypot(x, y) - 1)))}; }""")
        assert circle["n"] > 400 and circle["rej"] == 0, circle
        assert circle["dev"] < 1e-6 and circle["res"] < 1e-9, circle
        assert all(c > 50 for c in circle["q"]), circle

        # Ellipse x^2/4 + y^2 = 1 and hyperbola x^2 - y^2 = 1 references.
        ellipse = api("""() => { const r = MathStudio.graphCurves.implicit('(x^2)/4 + y^2 - 1', {xmin: -3, xmax: 3, ymin: -2, ymax: 2, grid: 200});
            const pts = r.segments.flatMap(s => [[s[0], s[1]], [s[2], s[3]]]);
            return {n: r.segmentCount, dev: Math.max(...pts.map(([x, y]) => Math.abs(x * x / 4 + y * y - 1))),
                    xmax: Math.max(...pts.map(p => p[0])), ymax: Math.max(...pts.map(p => p[1]))}; }""")
        assert ellipse["n"] > 100 and ellipse["dev"] < 1e-9, ellipse
        assert abs(ellipse["xmax"] - 2) < 1e-3 and abs(ellipse["ymax"] - 1) < 1e-3, ellipse
        hyper = api("""() => { const r = MathStudio.graphCurves.implicit('x^2 - y^2 = 1', {xmin: -3, xmax: 3, ymin: -3, ymax: 3});
            const pts = r.segments.flatMap(s => [[s[0], s[1]], [s[2], s[3]]]);
            return {n: r.segmentCount, minAbsX: Math.min(...pts.map(p => Math.abs(p[0]))),
                    dev: Math.max(...pts.map(([x, y]) => Math.abs(x * x - y * y - 1))),
                    left: pts.some(p => p[0] < -1), right: pts.some(p => p[0] > 1)}; }""")
        assert hyper["n"] > 100 and hyper["dev"] < 1e-9 and hyper["left"] and hyper["right"], hyper
        assert hyper["minAbsX"] >= 1 - 1e-9, hyper

        # Lemniscate of Bernoulli (x^2+y^2)^2 = 2(x^2-y^2): self-crossing at the origin, |x| <= sqrt(2).
        lem = api("""() => { const r = MathStudio.graphCurves.implicit('(x^2+y^2)^2 = 2*(x^2-y^2)', {xmin: -2, xmax: 2.03, ymin: -1.01, ymax: 1.02, grid: 220});
            const pts = r.segments.flatMap(s => [[s[0], s[1]], [s[2], s[3]]]);
            return {n: r.segmentCount, rej: r.rejected, res: r.maxResidual, xmax: Math.max(...pts.map(p => Math.abs(p[0]))),
                    nearOrigin: pts.some(p => Math.hypot(p[0], p[1]) < 0.05)}; }""")
        assert lem["n"] > 150 and lem["rej"] == 0 and lem["res"] < 1e-9, lem
        assert abs(lem["xmax"] - math.sqrt(2)) < 1e-3 and lem["nearOrigin"], lem

        # Pole sign changes of 1/(x-y) are rejected and counted, never drawn.
        pole = api("() => MathStudio.graphCurves.implicit('1/(x-y)', {xmin: -2.05, xmax: 2, ymin: -2, ymax: 2.05, grid: 41})")
        assert pole["segmentCount"] == 0 and pole["rejected"] > 40, pole
        tan = api("() => MathStudio.graphCurves.implicit('y = tan(x)', {xmin: -4, xmax: 4, ymin: -4, ymax: 4, grid: 120})")
        assert tan["segmentCount"] > 100 and tan["rejected"] > 0 and tan["maxResidual"] < 1e-9, tan

        # Parametric circle closes; Lissajous (sin 3t, sin 2t) stays in the unit square with |x|max = 1.
        para = api("""() => { const C = MathStudio.graphCurves; const c = C.parametric('cos(t)', 'sin(t)', {t0: 0, t1: 2*pi, samples: 400});
            const a = c.points[0], z = c.points[c.points.length - 1];
            const l = C.parametric('sin(3*t)', 'sin(2*t)', {t0: 0, t1: 2*pi, samples: 2001});
            const b = C.parametric('t', '1/t', {t0: -1, t1: 1, samples: 3});
            return {close: Math.hypot(a.x - z.x, a.y - z.y), dev: Math.max(...c.points.map(p => Math.abs(Math.hypot(p.x, p.y) - 1))),
                    lx: Math.max(...l.points.map(p => Math.abs(p.x))), ly: Math.max(...l.points.map(p => Math.abs(p.y))),
                    breakLines: b.polylines.length, breakNonFinite: b.nonFinite}; }""".replace("2*pi", str(2 * math.pi)))
        assert para["close"] < 1e-12 and para["dev"] < 1e-12, para
        assert abs(para["lx"] - 1) < 1e-5 and abs(para["ly"] - 1) < 1e-5, para
        assert para["breakLines"] == 2 and para["breakNonFinite"] == 1, para

        # Polar rose r = cos(3θ): 3 petals, max r = 1, negative r plotted through the origin.
        rose = api("""() => { const r = MathStudio.graphCurves.polar('cos(3*theta)', {theta0: 0, theta1: Math.PI, samples: 1801});
            // Petal tips are the samples with |r| = 1; over [0, π] the tips at θ = 0 and θ = π coincide.
            const tips = new Set(r.points.filter(p => Math.abs(p.r) > 1 - 1e-9).map(p => (Math.round(p.x * 1000) + 0) + ',' + (Math.round(p.y * 1000) + 0)));
            const petals = tips.size;
            const neg = r.points.find(p => p.r < -0.5);
            return {max: Math.max(...r.points.map(p => p.r)), petals, negOk: Math.abs(neg.x - neg.r * Math.cos(neg.theta)) < 1e-15 && Math.hypot(neg.x, neg.y) > 0.5}; }""")
        assert abs(rose["max"] - 1) < 1e-12 and rose["petals"] == 3 and rose["negOk"], rose
        card = api("""() => { const r = MathStudio.graphCurves.polar('1 + cos(θ)', {samples: 721});
            return {xmax: Math.max(...r.points.map(p => p.x)), xmin: Math.min(...r.points.map(p => p.x)), lines: r.polylines.length}; }""")
        assert abs(card["xmax"] - 2) < 1e-12 and abs(card["xmin"] + 0.25) < 1e-3 and card["lines"] == 1, card

        # API negative cases.
        for script, expected in [
            ("MathStudio.graphCurves.implicit('')", "empty"),
            ("MathStudio.graphCurves.parametric('t', 't', {t0: 1, t1: 1})", "greater than"),
            ("MathStudio.graphCurves.polar('1', {samples: 20001})", "Too many samples"),
            ("MathStudio.graphCurves.parametric('sqrt(-1-t^2)', 't', {})", "not finite"),
            ("MathStudio.graphCurves.implicit('sqrt(-1-x^2-y^2)')", "not finite"),
            ("MathStudio.graphCurves.implicit('x + q')", "Unknown variable"),
            ("MathStudio.graphCurves.implicit('x = y = 1')", 'single "="'),
            ("MathStudio.graphCurves.implicit('x+y', {grid: 301})", "4 to 300"),
        ]:
            message = api("() => { try { " + script + "; return 'NO ERROR'; } catch (e) { return e.message; } }")
            assert expected in message, (script, message)

        # UI: open via keyboard in the Graph workspace.
        page.locator('[data-workspace="graph"]').click()
        details = page.locator("#curves-details")
        assert page.locator("#graph-panel #curves-details").count() == 1
        details.locator("summary").focus()
        page.keyboard.press("Enter")
        assert details.evaluate("el => el.open")
        status, canvas = page.locator("#curves-status"), page.locator("#curves-canvas")
        assert status.get_attribute("aria-live") == "polite" and status.get_attribute("role") == "status"
        assert canvas.get_attribute("role") == "img"

        page.locator("#curves-plot").focus()
        page.keyboard.press("Enter")
        text = status.inner_text()
        assert text.startswith("Implicit curve:") and "0 pole/discontinuity" in text, text
        assert "segments" in canvas.get_attribute("aria-label"), canvas.get_attribute("aria-label")
        ink = page.evaluate("""() => { const c = document.getElementById('curves-canvas'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] > 150 && d[i + 1] < 110 && d[i + 2] < 60) n++; return n; }""")
        assert ink > 500, ink

        # Pole case through the UI reports the rejected count.
        page.locator("#curves-expr").fill("1/(x-y)")
        page.locator("#curves-xmin").fill("-2.05")
        page.locator("#curves-ymax").fill("2.05")
        page.locator("#curves-grid-n").fill("41")
        page.locator("#curves-plot").click()
        assert "0 segments" in status.inner_text() and "rejected" in status.inner_text(), status.inner_text()

        # Negative UI cases then recovery.
        page.locator("#curves-expr").fill("")
        page.locator("#curves-plot").click()
        assert "empty" in status.inner_text() and "curves-error" in status.get_attribute("class"), status.inner_text()
        assert page.locator("#curves-save").is_disabled()
        page.locator("#curves-expr").fill("x^2 + y^2 = 1")
        page.locator("#curves-xmin").fill("-2")
        page.locator("#curves-ymax").fill("2")
        page.locator("#curves-grid-n").fill("120")
        page.locator("#curves-expr").press("Enter")
        assert status.inner_text().startswith("Implicit curve:"), status.inner_text()
        assert "curves-error" not in (status.get_attribute("class") or "")

        page.locator("#curves-type").select_option("parametric")
        assert page.locator("#curves-xt").is_visible() and not page.locator("#curves-expr").is_visible()
        page.locator("#curves-p1").fill("0")
        page.locator("#curves-plot").click()
        assert "greater than" in status.inner_text() and "curves-error" in status.get_attribute("class")
        page.locator("#curves-p1").fill("6.283185307179586")
        page.locator("#curves-samples").fill("50000")
        page.locator("#curves-plot").click()
        assert "Too many samples" in status.inner_text(), status.inner_text()
        page.locator("#curves-samples").fill("721")
        page.locator("#curves-xt").fill("sqrt(-1-t^2)")
        page.locator("#curves-plot").click()
        assert "not finite" in status.inner_text(), status.inner_text()
        page.locator("#curves-xt").fill("sin(3*t)")
        page.locator("#curves-plot").click()
        assert status.inner_text().startswith("Parametric curve: 721 finite of 721"), status.inner_text()

        page.locator("#curves-type").select_option("polar")
        page.locator("#curves-r").fill("cos(3*theta)")
        page.locator("#curves-plot").click()
        assert "max |r| = 1" in status.inner_text(), status.inner_text()

        # Save points to Data Tables.
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#curves-save").click()
        assert "Saved 721 points" in status.inner_text(), status.inner_text()
        table = page.evaluate("(() => { const t = MathStudio.dataTables.tables; const last = t[t.length - 1]; return {n: t.length, name: last.name, cols: last.columns.map(c => c.name || c), rows: last.rows.length}; })()")
        assert table["n"] == before + 1 and table["rows"] == 721, table
        page.locator('[data-workspace="graph"]').click()

        # Responsive layouts: no horizontal overflow, touch-sized controls.
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#curves-plot").click()
            assert status.inner_text().startswith("Polar curve:"), status.inner_text()
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            for sel in ("#curves-plot", "#curves-save", "#curves-type", "#curves-r", "#curves-samples"):
                box = page.locator(sel).bounding_box()
                assert box["height"] >= 40, (width, sel, box)
            cbox, dbox = canvas.bounding_box(), details.bounding_box()
            assert cbox["x"] + cbox["width"] <= dbox["x"] + dbox["width"] + 1, (width, cbox, dbox)

        page.locator("#curves-equal").uncheck()
        page.locator("#curves-equal").check()
        assert not errors, errors
        browser.close()
    print("PASS graph curves: implicit circle/ellipse/hyperbola/lemniscate, pole rejection, parametric, polar, "
          "negative cases, keyboard, Data Tables, 390/768/1280")


if __name__ == "__main__":
    main()
