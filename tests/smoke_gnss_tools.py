"""GNSS least-squares positioning: browser API references, keyboard UI, sky plot, export, catalog route and responsive layout."""
from pathlib import Path
import math
import os
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_gnss_tools import GEOMETRY, satellites, llh_to_ecef  # noqa: E402  (shared independent reference synthesis)


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert '<script id="promath-gnss-tools">' in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")

        # In-browser reference: exact pseudoranges recover position and clock bias.
        truth, rows = satellites(59.33, 18.06, 30, 1e-4, GEOMETRY)
        r = page.evaluate("(o) => MathStudio.gnss.solve({observations: o})", rows)
        assert math.dist(r["position"], truth) < 1e-4, r["position"]
        assert abs(r["clockBiasSeconds"] - 1e-4) < 1e-15
        assert abs(r["geodetic"]["height"] - 30) < 1e-4
        fail = "(o) => {try {MathStudio.gnss.solve({observations: o}); return '';} catch (e) {return e.message;}}"
        assert "At least 4 satellites" in page.evaluate(fail, rows[:3])
        _, cone = satellites(59.33, 18.06, 30, 0, [[0, 30], [72, 30], [144, 30], [216, 30], [288, 30]])
        assert "Singular satellite geometry" in page.evaluate(fail, cone)
        ecef = page.evaluate("() => MathStudio.gnss.geodeticToEcef(-90, 0, 12)")
        assert math.dist(ecef, llh_to_ecef(-90, 0, 12)) < 1e-6

        # UI via keyboard: open, load example, solve.
        page.locator('[data-workspace="editor"]').click()
        details = page.locator("#gnss-details")
        details.locator("summary").focus()
        page.keyboard.press("Enter")
        assert details.evaluate("e => e.open")
        output = page.locator("#gnss-output")
        assert output.get_attribute("role") == "status" and output.get_attribute("aria-live") == "polite"
        page.locator("#gnss-example").focus()
        page.keyboard.press("Enter")
        assert page.evaluate("() => document.activeElement.id") == "gnss-input"
        assert len([l for l in page.locator("#gnss-input").input_value().splitlines() if l and not l.startswith("#")]) == 7
        assert "Example loaded" in output.inner_text()
        page.locator("#gnss-run").focus()
        page.keyboard.press("Enter")
        text = output.inner_text()
        assert "converged in" in text and "GDOP" in text and "HDOP" in text and "Latitude 59.3" in text and "Sagnac" in text, text
        assert "Clock bias = 2997" in text and "e-5 s" in text, text
        sky = page.locator("#gnss-sky")
        assert sky.get_attribute("role") == "img"
        label = sky.get_attribute("aria-label")
        assert "7 satellites" in label and "elevation 60.0°" in label, label
        painted = page.evaluate("""() => {const c = document.getElementById('gnss-sky'), d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data;
            let n = 0; for (let i = 0; i < d.length; i += 4) if (d[i] < 80 && d[i + 1] > 100) n++; return n;}""")
        assert painted > 50, painted

        # Error and recovery.
        page.locator("#gnss-input").fill("1 2 3 4\n5 6 7 8\n9 10 11 12")
        page.locator("#gnss-run").click()
        assert "error" in (output.get_attribute("class") or "") and "At least 4 satellites" in output.inner_text()
        assert page.locator("#gnss-to-table").is_disabled()
        assert "Sky plot: solve" in sky.get_attribute("aria-label")
        page.locator("#gnss-input").fill("\n".join("%r %r %r %r" % (o["x"], o["y"], o["z"], o["rho"]) for o in rows))
        assert "error" not in (output.get_attribute("class") or "")
        page.locator("#gnss-run").click()
        assert "error" not in (output.get_attribute("class") or ""), output.inner_text()
        page.locator("#gnss-to-table").click()
        exported = page.evaluate("() => MathStudio.dataTables.tables.find(t => t.name.startsWith('GNSS_Residuals'))")
        assert exported and exported["columns"][0] == "satellite" and "residual_m" in exported["columns"] and len(exported["rows"]) == 7, exported
        residual = exported["columns"].index("residual_m")
        assert max(abs(float(row[residual])) for row in exported["rows"]) < 1e-5
        assert page.evaluate("() => MathStudio.advanced.currentMode()") == "data"

        # Engineering catalog routes to the real Solve control.
        assert page.evaluate("() => MathStudio.engineeringCatalog.tools.find(t => t.id === 'gnss.positioning.least.squares').status") == "available"
        page.evaluate("() => document.getElementById('gnss-details').open = false")
        assert page.evaluate("() => MathStudio.engineeringCatalog.open('gnss.positioning.least.squares')") is True
        page.wait_for_function("() => document.activeElement && document.activeElement.id === 'gnss-run'")
        assert page.evaluate("() => document.getElementById('gnss-details').open")

        # Responsive: no overflow and >=40px controls at 390 and 1280.
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#gnss-run").is_visible()
            overflow = page.evaluate("() => document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            small = page.evaluate("""() => [...document.querySelectorAll('#gnss-details input, #gnss-details textarea, #gnss-details button')]
                .filter(e => e.offsetParent !== null && e.getBoundingClientRect().height < 40).map(e => e.id)""")
            assert not small, (width, small)
            for sel in ("#gnss-output", "#gnss-sky", "#gnss-input"):
                box = page.locator(sel).bounding_box()
                assert box["x"] >= 0 and box["x"] + box["width"] <= width + 1, (width, sel, box)
        assert not errors, errors
        browser.close()
    print("PASS: GNSS least-squares positioning references, refusals, keyboard UI, sky plot, residual export, catalog route and responsive layout")


if __name__ == "__main__":
    main()
