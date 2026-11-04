"""Ideal air-standard cycles and DC network nodal analysis: closed-form/hand references, energy and
KCL balances, invalid input, unit-aware fields, catalog routing, export, keyboard, reduced motion, 390/1280."""
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

        # --- Otto: η = 1 − r^(1−γ); r = 8, γ = 1.4 → 0.5647.
        k, cp = 1.4, 1005.0
        cv, R = cp / k, cp - cp / k
        otto = sim("thermoCycle", {"cycle": "otto", "ratio": 8, "spec": "heat", "heatIn": 1000, "T1": 300, "P1": 100})
        assert abs(otto["efficiency"] - (1 - 8 ** -0.4)) < 1e-12 and abs(otto["efficiency"] - 0.5647) < 1e-4, otto["efficiency"]
        assert abs(otto["formulaEfficiency"] - otto["efficiency"]) < 1e-12
        assert otto["balance"] < 1e-12 and rel(otto["wNet"], otto["qIn"] - otto["qOut"]) < 1e-12
        s1, s2, s3, s4 = otto["states"]
        assert rel(s2["T"], 300 * 8 ** 0.4) < 1e-12 and rel(s2["P"], 100e3 * 8 ** 1.4) < 1e-12
        assert rel(s3["T"], s2["T"] + 1e6 / cv) < 1e-12 and rel(s1["v"], R * 300 / 100e3) < 1e-12
        assert rel(otto["mep"], otto["wNet"] / (s1["v"] - s2["v"])) < 1e-12
        for proc, v, p_kpa, T, s in otto["path"]:
            assert rel(p_kpa * 1000 * v, R * T) < 1e-12
        assert abs(s2["s"] - s1["s"]) < 1e-9 * cp and abs(s4["s"] - s3["s"]) < 1e-9 * cp  # isentropic legs
        assert otto["summary"].startswith("Ideal Otto cycle (r = 8"), otto["summary"]

        # --- Diesel: η = 1 − r^(1−γ)·(rc^γ − 1)/(γ(rc − 1)).
        r, rc = 18, 2
        diesel = sim("thermoCycle", {"cycle": "diesel", "ratio": r, "spec": "cutoff", "cutoff": rc, "T1": 300, "P1": 100})
        ref = 1 - r ** (1 - k) * (rc ** k - 1) / (k * (rc - 1))
        assert abs(diesel["efficiency"] - ref) < 1e-12 and abs(ref - 0.6316) < 1e-4, (diesel["efficiency"], ref)
        assert diesel["balance"] < 1e-12 and abs(diesel["rc"] - rc) < 1e-12
        assert rel(diesel["states"][2]["P"], diesel["states"][1]["P"]) < 1e-12
        heat = sim("thermoCycle", {"cycle": "diesel", "ratio": 18, "spec": "heat", "heatIn": 1200})
        assert rel(heat["qIn"], 1.2e6) < 1e-12 and heat["balance"] < 1e-12
        assert abs(heat["efficiency"] - heat["formulaEfficiency"]) < 1e-12

        # --- Brayton: η = 1 − rp^((1−γ)/γ), back-work ratio = (T2 − T1)/(T3 − T4).
        bray = sim("thermoCycle", {"cycle": "brayton", "pressureRatio": 10, "spec": "tmax", "Tmax": 1400, "T1": 300, "P1": 100})
        assert abs(bray["efficiency"] - (1 - 10 ** (-0.4 / 1.4))) < 1e-12 and bray["balance"] < 1e-12
        b1, b2, b3, b4 = bray["states"]
        assert abs(bray["backWorkRatio"] - (b2["T"] - b1["T"]) / (b3["T"] - b4["T"])) < 1e-12
        assert bray["mep"] is None and b3["T"] == 1400 and rel(b4["P"], 100e3) < 1e-12
        assert "back-work ratio" in bray["summary"]
        # Custom γ and cp (helium-like): closed form still matches.
        he = sim("thermoCycle", {"cycle": "otto", "ratio": 6, "gamma": 1.667, "cp": 5193, "heatIn": 500})
        assert abs(he["efficiency"] - (1 - 6 ** (1 - 1.667))) < 1e-12 and he["balance"] < 1e-12

        fails("thermoCycle", {"cycle": "otto", "spec": "cutoff"}, "cutoff ratio applies only to the Diesel")
        fails("thermoCycle", {"cycle": "otto", "spec": "tmax", "Tmax": 500}, "must exceed the compression end temperature")
        fails("thermoCycle", {"cycle": "diesel", "ratio": 8, "spec": "cutoff", "cutoff": 9}, "must be below the compression ratio")
        fails("thermoCycle", {"cycle": "otto", "gamma": 0.9}, "Heat capacity ratio")
        fails("thermoCycle", {"cycle": "otto", "T1": -5}, "Inlet temperature")
        fails("thermoCycle", {"cycle": "otto", "ratio": 1}, "Compression ratio")
        fails("thermoCycle", {"cycle": "rankine"}, "Cycle must be one of")
        fails("thermoCycle", {"cycle": "brayton", "pressureRatio": ""}, "Pressure ratio")

        # Unit-aware inputs: °C → K, bar → kPa, MJ/kg → kJ/kg.
        resolved = page.evaluate("MathStudio.engineeringVisuals.resolveInputs('cycle',{cycle:'otto',T1:'26.85 °C',P1:'1 bar',heatIn:'1 MJ/kg',cp:'1.005 kJ/(kg*K)'}).params")
        assert abs(resolved["T1"] - 300) < 1e-9 and abs(resolved["P1"] - 100) < 1e-9 and abs(resolved["heatIn"] - 1000) < 1e-9
        assert abs(resolved["cp"] - 1005) < 1e-9
        bad = page.evaluate("()=>{try{MathStudio.engineeringVisuals.resolveInputs('cycle',{T1:'3 m'});return null}catch(e){return e.message}}")
        assert bad and "expected a unit compatible with K" in bad, bad

        # --- DC networks (MNA).
        def node(result, name):
            return next(n["voltage"] for n in result["nodes"] if n["node"] == name)

        def element(result, name):
            return next(e for e in result["elements"] if e["name"] == name)

        div = sim("dcNetwork", {"netlist": "V1 1 0 12\nR1 1 2 1000\nR2 2 0 2000"})
        assert abs(node(div, "2") - 8) < 1e-12 and abs(node(div, "1") - 12) < 1e-12
        assert abs(element(div, "R1")["current"] - 0.004) < 1e-15 and abs(element(div, "V1")["current"] + 0.004) < 1e-15
        assert abs(element(div, "V1")["power"] + 0.048) < 1e-14 and abs(div["supplied"] - 0.048) < 1e-14
        assert div["kclResidual"] < 1e-12 and div["powerBalance"] < 1e-12
        # Balanced Wheatstone bridge (R1/R2 = R3/R4): zero bridge current.
        wb = sim("dcNetwork", {"netlist": "V1 1 0 10\nR1 1 2 100\nR2 2 0 200\nR3 1 3 100\nR4 3 0 200\nR5 2 3 50"})
        assert abs(element(wb, "R5")["current"]) < 1e-15 and abs(node(wb, "2") - 20 / 3) < 1e-12
        unbalanced = sim("dcNetwork", {"netlist": "V1 1 0 10\nR1 1 2 100\nR2 2 0 200\nR3 1 3 200\nR4 3 0 100\nR5 2 3 50"})
        assert abs(element(unbalanced, "R5")["current"]) > 1e-3
        # Two sources: superposition 10·(4‖4)/(2+4‖4) + 5·(2‖4)/(4+2‖4) = 5 + 1.25 = 6.25 V.
        two = sim("dcNetwork", {"netlist": "V1 1 0 10; R1 1 2 2; R2 2 0 4; R3 2 3 4; V2 3 0 5"})
        assert abs(node(two, "2") - 6.25) < 1e-12 and two["kclResidual"] < 1e-12
        # Current source (0 → node 1) into two parallel 1 kΩ: 10 mA × 500 Ω = 5 V.
        par = sim("dcNetwork", {"netlist": "* comment line\nI1 0 1 0.01\nR1 1 0 1000\nR2 1 gnd 1000"})
        assert abs(node(par, "1") - 5) < 1e-12 and abs(element(par, "R2")["current"] - 0.005) < 1e-15
        assert abs(element(par, "I1")["power"] + 0.05) < 1e-14
        # Conductances spanning many decades are not misreported as singular.
        wide = sim("dcNetwork", {"netlist": "V1 1 0 1\nR1 1 2 0.001\nR2 2 0 1e12"})
        assert abs(node(wide, "2") - 1) < 1e-12
        # 30-element ladder accepted.
        ladder = "V1 1 0 29\n" + "\n".join("R%d %d %d 1" % (i, i, i + 1) for i in range(1, 29)) + "\nR29 29 0 1"
        assert abs(node(sim("dcNetwork", {"netlist": ladder}), "29") - 1) < 1e-12

        fails("dcNetwork", {"netlist": "V1 1 0 5\nR1 1 0 100\nR2 2 3 100"}, "Floating nodes 2, 3")
        fails("dcNetwork", {"netlist": "V1 1 0 5\nV2 1 0 6\nR1 1 0 10"}, "Singular network matrix")
        fails("dcNetwork", {"netlist": "I1 0 1 0.01\nI2 1 2 0.01\nR1 2 0 10"}, "Singular network matrix")
        fails("dcNetwork", {"netlist": "R1 1 2 100\nV1 1 2 5"}, "No element connects to ground")
        fails("dcNetwork", {"netlist": "C1 1 0 1e-6"}, "start with R, V or I")
        fails("dcNetwork", {"netlist": "R1 1 0 100\nR1 1 0 200"}, "duplicate element name")
        fails("dcNetwork", {"netlist": "R1 1 0 -5"}, "resistance must be greater than 0")
        fails("dcNetwork", {"netlist": "R1 1 0 1k"}, "decimal or scientific number")
        fails("dcNetwork", {"netlist": "V1 1 1 5"}, "cannot connect a node to itself")
        fails("dcNetwork", {"netlist": "R1 1 0"}, "expected NAME node+")
        fails("dcNetwork", {"netlist": "   "}, "Enter a netlist")
        fails("dcNetwork", {"netlist": ladder + "\nR30 1 0 5\nR31 2 0 5"}, "limited to 30 elements")

        # --- Catalog status, honest scope and search invariants.
        statuses = page.evaluate("Object.fromEntries(MathStudio.engineeringCatalog.tools.map(t=>[t.id,t.status]))")
        assert statuses["thermal.cycle.analysis"] == "available" and statuses["circuits.network.analysis"] == "available"
        # Frequency-response simulation is implemented; do not regress its catalog status.\n        assert statuses["control.frequency.response"] == "available"
        assert page.evaluate("MathStudio.engineeringCatalog.filter('physics','ode').map(t=>t.id)") == ["ode.ivp.scalar"]
        assert page.evaluate("MathStudio.engineeringCatalog.filter('','control orbit').length") == 0
        assert page.evaluate("MathStudio.engineeringCatalog.filter('physics','otto').length") == 0

        # --- UI: catalog Open routing, keyboard, export, layout.
        page.locator('[data-workspace="engineering"]').click()
        status = page.locator("#eng-visual-status")
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#eng-discipline").select_option("")
            page.locator("#eng-search").fill("otto brayton")
            card = page.locator('#eng-results article[data-tool-id="thermal.cycle.analysis"]')
            assert card.count() == 1 and "planned" not in card.inner_text().lower()
            assert card.locator("[data-visual]").count() == 1
            card.locator("button").focus()
            page.keyboard.press("Enter")
            assert page.locator("#eng-visual-select").input_value() == "cycle"
            assert status.inner_text().startswith("Ideal Otto cycle (r = 8"), status.inner_text()
            assert page.evaluate("document.activeElement.id") == "eng-visual-cycle"
            page.locator("#eng-search").fill("nodal netlist")
            card = page.locator('#eng-results article[data-tool-id="circuits.network.analysis"]')
            assert card.count() == 1
            card.locator("button").focus()
            page.keyboard.press("Enter")
            assert page.locator("#eng-visual-select").input_value() == "network"
            assert status.inner_text().startswith("DC network: 3 node(s) + ground, 6 element(s)"), status.inner_text()
            assert page.evaluate("document.activeElement.id") == "eng-visual-netlist"
            assert page.evaluate("document.activeElement.tagName") == "TEXTAREA"
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            assert page.locator("#eng-visual-canvas").bounding_box()["width"] <= width
            assert page.locator("#eng-visual-netlist").bounding_box()["width"] <= width

        # Typed netlist via keyboard, invalid netlist reports an error, valid run recovers.
        page.locator("#eng-visual-netlist").fill("V1 1 0 9\nR1 1 2 300\nR2 2 0 600")
        page.locator("#eng-visual-run").focus()
        page.keyboard.press("Enter")
        assert "V(2) = 6 V" in status.inner_text(), status.inner_text()
        page.wait_for_function("() => MathStudio.engineeringVisuals.frame() > 5")
        page.locator("#eng-visual-netlist").fill("V1 1 0 5\nR1 2 3 10")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: No element connects to ground") or "Floating" in status.inner_text(), status.inner_text()
        assert status.evaluate("el => el.classList.contains('error')") and page.locator("#eng-visual-table").is_disabled()
        page.locator("#eng-visual-netlist").fill("V1 1 0 12\nR1 1 2 1000\nR2 2 0 2000")
        page.locator("#eng-visual-run").click()
        assert "V(2) = 8 V" in status.inner_text()
        table = page.evaluate("MathStudio.engineeringVisuals.tableOf(MathStudio.engineeringVisuals.current())")
        assert table["name"] == "SIM_NETWORK" and table["headers"][:4] == ["index", "current_A", "voltage_V", "power_W"]
        assert table["rows"][1][5] == "R1" and abs(table["rows"][1][1] - 0.004) < 1e-15
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#eng-visual-table").click()
        tables = page.evaluate("MathStudio.dataTables.tables.map(t=>({name:t.name,columns:t.columns,rows:t.rows.length}))")
        assert len(tables) == before + 1 and tables[-1]["name"] == "SIM_NETWORK" and tables[-1]["rows"] == 3, tables[-1]

        page.locator('[data-workspace="engineering"]').click()
        page.locator("#eng-visual-select").select_option("cycle")
        page.locator("#eng-visual-cycle").select_option("brayton")
        page.locator("#eng-visual-spec").select_option("tmax")
        page.locator("#eng-visual-Tmax").fill("1126.85 °C")
        page.locator("#eng-visual-run").click()
        text = status.inner_text()
        assert text.startswith("Ideal Brayton cycle (rp = 10") and "T_max 1400.0 K" in text and "1126.85 °C → 1400 K" in text, text
        cyc = page.evaluate("MathStudio.engineeringVisuals.tableOf(MathStudio.engineeringVisuals.current())")
        assert cyc["name"] == "SIM_CYCLE" and cyc["headers"] == ["process", "v_m3_kg", "P_kPa", "T_K", "s_J_kgK"]
        assert len(cyc["rows"]) == 241 and cyc["rows"][0][3] == 300
        page.locator("#eng-visual-spec").select_option("cutoff")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: A cutoff ratio applies only to the Diesel"), status.inner_text()
        assert page.locator("#eng-visual-canvas").get_attribute("aria-label")

        # Reduced motion: final frame immediately, no autoplay.
        reduced = browser.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        reduced.on("pageerror", lambda error: errors.append(str(error)))
        reduced.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        reduced.locator('[data-workspace="engineering"]').click()
        reduced.evaluate("MathStudio.engineeringCatalog.open('circuits.network.analysis')")
        assert reduced.evaluate("MathStudio.engineeringVisuals.frame()") == reduced.evaluate("MathStudio.engineeringVisuals.frames")
        assert reduced.locator("#eng-visual-toggle").get_attribute("aria-pressed") == "true"
        assert not errors, errors
        browser.close()
    print("PASS engineering thermo cycles + DC networks: closed forms, energy/KCL balance, invalid input, units, routing, export, keyboard, reduced motion, 390/1280")


if __name__ == "__main__":
    main()
