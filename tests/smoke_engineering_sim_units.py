"""Unit-aware Engineering simulation inputs: conversions match plain-SI references, dimension
mismatch and unknown units fail with field-specific messages, recovery, responsive layout."""
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
        page = browser.new_page(viewport={"width": 1280, "height": 850}, reduced_motion="reduce")
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def resolved(kind, params):
            return page.evaluate("([k,p]) => MathStudio.engineeringVisuals.resolveInputs(k,p)", [kind, params])

        def run(kind, params):
            return page.evaluate("""([k,p]) => { const V=MathStudio.engineeringVisuals, r=V.resolveInputs(k,p);
                return V.compute[k](r.params); }""", [kind, params])

        def fails(kind, params, *fragments):
            msg = page.evaluate("([k,p]) => { try { MathStudio.engineeringVisuals.resolveInputs(k,p); return null; } "
                                "catch (e) { return e.message; } }", [kind, params])
            assert msg and all(f in msg for f in fragments), (kind, params, msg)
            return msg

        base = {"support": "simply", "load": "point", "length": "4", "position": "2", "force": "10",
                "modulus": "200", "width": "100", "height": "200", "supportB": "3", "force2": "0",
                "position2": "1", "udl": "0"}
        ref = run("beam", base)
        # Plain numbers are passed through unchanged (backward compatible).
        plain = resolved("beam", base)
        assert plain["conversions"] == [] and plain["params"] == base, plain
        # Span in feet equals the 4 m result.
        ft = run("beam", dict(base, length="13.123359580052493 ft", position="2 m"))
        assert rel(ft["maxDeflection"], ref["maxDeflection"]) < 1e-9, (ft["maxDeflection"], ref["maxDeflection"])
        assert rel(ft["maxMoment"], ref["maxMoment"]) < 1e-9
        # Force in lbf vs kN gives the same deflection.
        a = run("beam", dict(base, force="10 kN"))
        b = run("beam", dict(base, force="2248.0894309971 lbf"))
        assert rel(a["maxDeflection"], ref["maxDeflection"]) < 1e-12
        assert rel(b["maxDeflection"], a["maxDeflection"]) < 1e-9, (a["maxDeflection"], b["maxDeflection"])
        # Modulus in ksi and Pa.
        k = resolved("beam", dict(base, modulus="29007.547546041 ksi"))["params"]["modulus"]
        assert rel(k, 200) < 1e-9, k
        assert rel(resolved("beam", dict(base, modulus="200e9 Pa"))["params"]["modulus"], 200) < 1e-12
        # Section depth in inches.
        h = resolved("beam", dict(base, height="4 in"))["params"]["height"]
        assert abs(h - 101.6) < 1e-9, h
        # UDL expects kN/m: lbf/ft converts, a bare force is a dimension mismatch.
        w = resolved("beam", dict(base, load="udl", force="30 lbf/ft"))["params"]["force"]
        assert rel(w, 30 * 4.4482216152605 / 0.3048 / 1000) < 1e-12, w
        fails("beam", dict(base, load="udl", force="10 kN"), "Load P1 (kN) or w (kN/m)", "kN/m", "dimension")
        # RLC: henry, farad, ohm and millivolt give the identical response.
        rlc_ref = run("rlc", {"resistance": "4", "inductance": "10", "capacitance": "100", "voltage": "12"})
        rlc_si = run("rlc", {"resistance": "4 ohm", "inductance": "0.01 H", "capacitance": "0.0001 F", "voltage": "12000 mV"})
        ind = resolved("rlc", {"resistance": "4", "inductance": "0.01 H", "capacitance": "100", "voltage": "12"})
        assert abs(ind["params"]["inductance"] - 10) < 1e-12, ind
        assert rlc_si["summary"] == rlc_ref["summary"], (rlc_si["summary"], rlc_ref["summary"])
        # Rod: absolute temperatures and other units.
        rod = resolved("rod", {"material": "aluminium", "length": "50 cm", "initial": "293.15 K", "left": "212 °F",
                               "right": "68 degF", "duration": "15 min"})["params"]
        assert abs(rod["left"] - 100) < 1e-12 and abs(rod["right"] - 20) < 1e-12 and abs(rod["initial"] - 20) < 1e-9, rod
        assert abs(rod["length"] - 0.5) < 1e-12 and rod["duration"] == 900, rod
        fails("rod", {"material": "aluminium", "length": "0.5", "initial": "-500 °C", "left": "100", "right": "20",
                      "duration": "900"}, "Initial temperature (°C)", "absolute zero")
        # Orbit altitude in miles; projectile speed in mph.
        alt = resolved("orbit", {"altitude": "500 mi", "eccentricity": "0.3", "orbits": "1"})["params"]["altitude"]
        assert abs(alt - 804.672) < 1e-9, alt
        spd = resolved("projectile", {"speed": "100 mph", "angle": "45", "mass": "0.145", "diameter": "74",
                                      "drag": "0.47", "density": "1.225"})["params"]["speed"]
        assert rel(spd, 44.704) < 1e-12, spd
        # Negative paths name the field and dimensions.
        fails("beam", dict(base, force="10 kg"), "Load P1 (kN) or w (kN/m)", "compatible with kN", "dimension M")
        fails("beam", dict(base, length="4 furlong"), "Span L (m)", "Unknown unit")

        # --- UI: placeholders, status summary conversions, errors and recovery.
        page.locator('[data-workspace="engineering"]').click()
        page.evaluate("document.getElementById('eng-visuals').open = true")
        page.select_option("#eng-visual-select", "beam")
        length = page.locator("#eng-visual-length")
        assert length.get_attribute("type") == "text"
        assert "default m" in length.get_attribute("placeholder")
        assert "kN or kN/m" in page.locator("#eng-visual-force").get_attribute("placeholder")
        assert "default mm" in page.locator("#eng-visual-height").get_attribute("placeholder")
        status = page.locator("#eng-visual-status")
        page.evaluate("MathStudio.engineeringVisuals.run()")
        plain_text = status.inner_text()
        assert plain_text.startswith("Simply supported") and "Unit inputs" not in plain_text, plain_text
        length.fill("13.123359580052493 ft")
        page.evaluate("MathStudio.engineeringVisuals.run()")
        assert "Unit inputs: Span L (m) 13.123359580052493 ft → 4 m" in status.inner_text(), status.inner_text()
        assert "error" not in (status.get_attribute("class") or "")
        page.locator("#eng-visual-force").fill("10 kg")
        page.evaluate("MathStudio.engineeringVisuals.run()")
        assert status.inner_text().startswith(
            "Cannot animate: Load P1 (kN) or w (kN/m): expected a unit compatible with kN"), status.inner_text()
        assert "error" in status.get_attribute("class")
        assert page.locator("#eng-visual-table").is_disabled()
        page.locator("#eng-visual-force").fill("2248.0894309971 lbf")
        page.evaluate("MathStudio.engineeringVisuals.run()")
        assert "→ 10 kN" in status.inner_text() and "error" not in (status.get_attribute("class") or ""), status.inner_text()
        assert not page.locator("#eng-visual-table").is_disabled()
        page.select_option("#eng-visual-select", "rod")
        page.locator("#eng-visual-left").fill("212 °F")
        page.evaluate("MathStudio.engineeringVisuals.run()")
        assert "Left end (°C) 212 °F → 100 °C" in status.inner_text(), status.inner_text()

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
        assert not errors, errors
        browser.close()
        print("Engineering simulation unit inputs smoke passed")


if __name__ == "__main__":
    main()
