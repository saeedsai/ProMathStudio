"""Engineering simulations (beam, orbit, RLC, projectile, rod conduction): analytic/series
references, invalid input, catalog routing, keyboard, reduced motion and responsive layout."""
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
MU, RE, G = 398600.4418, 6378.137, 9.80665


def rel(a, b):
    return abs(a - b) / max(abs(b), 1e-300)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def sim(kind, params):
            return page.evaluate("([k,p]) => MathStudio.engineeringSimulations[k](p)", [kind, params])

        def fails(kind, params, fragment):
            message = page.evaluate("([k,p]) => { try { MathStudio.engineeringSimulations[k](p); return null; } catch (e) { return e.message; } }", [kind, params])
            assert message and fragment in message, (kind, params, message)

        # --- Beam: standard closed-form maxima, equilibrium and curvature EI·v'' = ∓M.
        E, b, h, L, P, w = 200e9, 0.1, 0.2, 4.0, 10e3, 5e3
        EI = E * b * h ** 3 / 12
        base = {"length": 4, "modulus": 200, "width": 100, "height": 200}
        cases = [({"support": "simply", "load": "point", "force": 10, "position": 2}, P * L ** 3 / (48 * EI), P * L / 4),
                 ({"support": "simply", "load": "udl", "force": 5}, 5 * w * L ** 4 / (384 * EI), w * L ** 2 / 8),
                 ({"support": "cantilever", "load": "point", "force": 10, "position": 4}, P * L ** 3 / (3 * EI), P * L),
                 ({"support": "cantilever", "load": "udl", "force": 5}, w * L ** 4 / (8 * EI), w * L ** 2 / 2)]
        for extra, delta, moment in cases:
            r = sim("beam", {**base, **extra})
            assert rel(abs(r["maxDeflection"]), delta) < 1e-12, (extra, r["maxDeflection"], delta)
            assert rel(abs(r["maxMoment"]), moment) < 1e-12, (extra, r["maxMoment"])
            assert rel(r["maxStress"], moment * (h / 2) / (b * h ** 3 / 12)) < 1e-12
            total = P if extra["load"] == "point" else w * L
            assert rel(r["reactions"]["left"] + r["reactions"]["right"], total) < 1e-12, r["reactions"]
            x, v, m = r["x"], r["deflection"], r["moment"]
            dx = x[1] - x[0]
            for i in range(5, len(x) - 5, 17):
                curvature = (v[i + 1] - 2 * v[i] + v[i - 1]) / dx ** 2
                if extra["load"] == "point" and abs(x[i] - extra["position"]) < 2 * dx:
                    continue
                # Central-difference truncation is dx²·v⁗·EI/12 = dx²·w/12 for a UDL (0 for point loads).
                assert abs(EI * curvature + m[i]) <= 1e-3 * moment, (extra, i, EI * curvature, m[i])
        offcentre = sim("beam", {**base, "support": "simply", "load": "point", "force": 10, "position": 1})
        a, bb = 1.0, 3.0
        assert rel(offcentre["reactions"]["left"], P * bb / L) < 1e-12
        xm = L - math.sqrt(bb * (bb + 2 * a) / 3)  # max deflection lies in the longer segment (a < b)
        assert abs(offcentre["maxDeflectionAt"] - xm) <= L / 200 + 1e-12, offcentre["maxDeflectionAt"]
        zero = sim("beam", {**base, "support": "simply", "load": "udl", "force": 0})
        assert zero["maxDeflection"] == 0 and zero["maxStress"] == 0
        fails("beam", {**base, "support": "simply", "load": "point", "force": 10, "position": 5}, "Load position")
        fails("beam", {**base, "support": "pinned", "load": "point"}, "Support")
        fails("beam", {**base, "modulus": -1}, "Elastic modulus")

        # --- Orbit: Kepler period, vis-viva speeds, conservation and closure.
        o = sim("orbit", {"altitude": 500, "eccentricity": 0.3, "orbits": 1})
        rp = RE + 500; a_ = rp / 0.7
        assert rel(o["period"], 2 * math.pi * math.sqrt(a_ ** 3 / MU)) < 1e-12
        assert rel(o["vp"], math.sqrt(MU * (2 / rp - 1 / a_))) < 1e-12
        assert o["maxEnergyDrift"] < 1e-5 and o["maxMomentumDrift"] < 1e-9, (o["maxEnergyDrift"], o["maxMomentumDrift"])
        assert o["closure"] < 1e-3, o["closure"]
        radii = [math.hypot(p[1], p[2]) for p in o["path"]]
        assert rel(max(radii), o["ra"]) < 1e-4 and rel(min(radii), rp) < 1e-9
        circ = sim("orbit", {"altitude": 400, "eccentricity": 0, "orbits": 2})
        assert rel(circ["vp"], math.sqrt(MU / (RE + 400))) < 1e-12 and circ["closure"] < 1e-3
        fails("orbit", {"altitude": 50, "eccentricity": 0}, "Periapsis altitude")
        fails("orbit", {"altitude": 500, "eccentricity": 0.99}, "Eccentricity")

        # --- Series RLC: analytic underdamped vC(t), i(t).
        R, Lh, C, V = 4.0, 10e-3, 100e-6, 12.0
        c = sim("rlc", {"resistance": 4, "inductance": 10, "capacitance": 100, "voltage": 12})
        alpha, w0 = R / (2 * Lh), 1 / math.sqrt(Lh * C)
        wd = math.sqrt(w0 ** 2 - alpha ** 2)
        assert rel(c["zeta"], R / 2 * math.sqrt(C / Lh)) < 1e-12 and c["regime"] == "underdamped"
        for t, vc, i in c["rows"][::25]:
            ev = V * (1 - math.exp(-alpha * t) * (math.cos(wd * t) + alpha / wd * math.sin(wd * t)))
            ei = V / (Lh * wd) * math.exp(-alpha * t) * math.sin(wd * t)
            assert abs(vc - ev) < 1e-6 * V and abs(i - ei) < 1e-6 * V / (Lh * wd), (t, vc, ev, i, ei)
        assert rel(c["overshoot"], math.exp(-math.pi * c["zeta"] / math.sqrt(1 - c["zeta"] ** 2))) < 2e-3
        over = sim("rlc", {"resistance": 100, "inductance": 10, "capacitance": 100, "voltage": 12})
        assert over["regime"] == "overdamped" and over["overshoot"] < 1e-9 and over["settled"], over["overshoot"]
        fails("rlc", {"resistance": 1e5, "inductance": 10, "capacitance": 100, "voltage": 12}, "Heavily overdamped")
        fails("rlc", {"resistance": -1, "inductance": 10, "capacitance": 100, "voltage": 12}, "Resistance")

        # --- Projectile: drag-free limit equals the vacuum parabola; drag reduces range and energy.
        vac = sim("projectile", {"speed": 40, "angle": 30, "mass": 1, "diameter": 50, "drag": 0, "density": 1.225})
        assert rel(vac["range"], 40 ** 2 * math.sin(math.radians(60)) / G) < 1e-6, vac["range"]
        assert rel(vac["apexHeight"], (40 * 0.5) ** 2 / (2 * G)) < 1e-4 and rel(vac["impactSpeed"], 40) < 1e-6
        drag = sim("projectile", {"speed": 40, "angle": 30, "mass": 0.145, "diameter": 74, "drag": 0.47, "density": 1.225})
        assert drag["range"] < vac["range"] and drag["impactSpeed"] < 40
        k = 0.5 * 1.225 * 0.47 * math.pi * 0.074 ** 2 / 4 / 0.145
        assert rel(drag["terminalVelocity"], math.sqrt(G / k)) < 1e-12
        fails("projectile", {"speed": 40, "angle": 95}, "Launch angle")

        # --- Rod conduction vs Fourier-series solution of the same Dirichlet problem.
        r = sim("rodHeat", {"material": "aluminium", "length": 0.5, "initial": 20, "left": 100, "right": 20, "duration": 900})
        alpha_r, Lr, t_end = 97e-6, 0.5, 900.0

        def exact(x):
            steady = 100 + (20 - 100) * x / Lr
            total = steady
            for n in range(1, 400):
                # b_n = (2/L)∫(T0 - steady) sin(nπx/L) dx, evaluated analytically.
                bn = 2 / (n * math.pi) * ((20 - 100) * (1 - (-1) ** n) - (20 - 100) * (-1) ** (n + 1))
                total += bn * math.sin(n * math.pi * x / Lr) * math.exp(-alpha_r * (n * math.pi / Lr) ** 2 * t_end)
            return total
        final = r["frames"][-1]["values"]
        n = len(final) - 1
        err = max(abs(final[j] - exact(j * Lr / n)) for j in range(1, n))
        assert err < 0.25, err  # FTCS with 40 intervals vs 400-term series, °C
        assert r["cfl"] <= 0.5 and abs(r["frames"][-1]["time"] - t_end) < 1e-9
        fails("rodHeat", {"material": "copper", "length": 0.05, "duration": 100000}, "explicit steps")
        fails("rodHeat", {"material": "unobtainium"}, "Material")

        # --- Catalog routes: simulations are available tools; unrelated planned tools stay planned.
        statuses = page.evaluate("Object.fromEntries(MathStudio.engineeringCatalog.tools.map(t=>[t.id,t.status]))")
        for tool in ("structures.beam.deflection", "aerospace.orbit.propagation", "circuits.rlc.series.transient",
                     "mechanics.projectile.drag", "thermal.conduction.rod", "thermal.cycle.analysis",
                     "circuits.network.analysis", "fluids.pipe.network", "electronics.digital.logic"):
            assert statuses[tool] == "available", tool
        for tool in ("gnss.positioning.least.squares", "control.frequency.response", "signals.spectral.analysis"):
            assert statuses[tool] == "planned", tool
        page.locator('[data-workspace="engineering"]').click()
        status = page.locator("#eng-visual-status")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#eng-search").fill("beam")
            card = page.locator('#eng-results article[data-tool-id="structures.beam.deflection"]')
            assert card.locator("button").count() == 1 and "planned" not in card.inner_text().lower()
            card.locator("button").focus()
            page.keyboard.press("Enter")
            assert page.locator("#eng-visual-select").input_value() == "beam"
            assert status.inner_text().startswith("Simply supported beam"), status.inner_text()
            assert page.evaluate("document.activeElement.id") == "eng-visual-support"
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
        page.locator("#eng-visual-support").select_option("cantilever")
        page.locator("#eng-visual-load").select_option("udl")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cantilever beam, UDL 10 kN/m"), status.inner_text()
        page.locator("#eng-visual-length").fill("0")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: Span L"), status.inner_text()
        page.locator("#eng-visual-length").fill("4")
        page.locator("#eng-visual-run").click()
        assert not status.evaluate("el => el.classList.contains('error')")
        for tool, prefix in (("aerospace.orbit.propagation", "Orbit e = "), ("circuits.rlc.series.transient", "Series RLC step"),
                             ("mechanics.projectile.drag", "Projectile v0"), ("thermal.conduction.rod", "Rod (")):
            page.locator("#eng-search").fill(tool)
            page.locator('#eng-results article[data-tool-id="%s"] button' % tool).click()
            assert status.inner_text().startswith(prefix), (tool, status.inner_text())
        page.wait_for_function("() => MathStudio.engineeringVisuals.frame() > 10")

        reduced = browser.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        reduced.on("pageerror", lambda error: errors.append(str(error)))
        reduced.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        reduced.locator('[data-workspace="engineering"]').click()
        reduced.locator("#eng-search").fill("orbit")
        reduced.locator('#eng-results article[data-tool-id="aerospace.orbit.propagation"] button').click()
        assert reduced.evaluate("MathStudio.engineeringVisuals.frame()") == reduced.evaluate("MathStudio.engineeringVisuals.frames")
        assert not errors, errors
        browser.close()
    print("PASS engineering simulations: beam/orbit/RLC/projectile/rod references, routing, keyboard, reduced motion, responsive")


if __name__ == "__main__":
    main()
