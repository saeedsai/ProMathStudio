"""Looped pipe networks (Darcy–Weisbach, Colebrook/Swamee–Jain) and gate-level digital logic: hand and
independent references, residuals, invalid input, unit-aware fields, catalog routing, export, keyboard,
reduced motion and 390/1280 layouts."""
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
G = 9.80665
RHO, MU = 998.2, 1.002e-3


def colebrook(re, rel):
    # Independent Newton solve of 1/sqrt(f) = -2 log10(rel/3.7 + 2.51/(Re sqrt f)) in x = 1/sqrt(f).
    x = 7.0
    for _ in range(100):
        g = x + 2 * math.log10(rel / 3.7 + 2.51 * x / re)
        dg = 1 + 2 / math.log(10) * (2.51 / re) / (rel / 3.7 + 2.51 * x / re)
        x -= g / dg
    return 1 / (x * x)


def swamee(re, rel):
    return 0.25 / math.log10(rel / 3.7 + 5.74 / re ** 0.9) ** 2


def darcy(q, length, d, eps):
    area = math.pi * d * d / 4
    v = q / area
    re = RHO * abs(v) * d / MU
    return colebrook(re, eps / d) * length / d * v * abs(v) / (2 * G)


GRID = ("H A 60\nP1 A B 600 300 0.26\nP2 B C 500 250 0.26\nP3 A D 500 250 0.26\nP4 B E 600 200 0.26\n"
        "P5 C F 500 200 0.26\nP6 D E 600 200 0.26\nP7 E F 500 150 0.26\nD B 0.03\nD C 0.03\nD D 0.02\nD E 0.04\nD F 0.03")


def hardy_cross():
    """Independent Hardy–Cross loop iteration of the two-loop grid (Colebrook friction each pass)."""
    pipes = {"P1": (600, .3, .26e-3), "P2": (500, .25, .26e-3), "P3": (500, .25, .26e-3), "P4": (600, .2, .26e-3),
             "P5": (500, .2, .26e-3), "P6": (600, .2, .26e-3), "P7": (500, .15, .26e-3)}
    q = {"P1": .09, "P3": .06, "P6": .04, "P2": .04, "P4": .02, "P5": .01, "P7": .02}  # satisfies continuity
    loops = [[("P1", 1), ("P4", 1), ("P6", -1), ("P3", -1)], [("P2", 1), ("P5", 1), ("P7", -1), ("P4", -1)]]
    for _ in range(400):
        for loop in loops:
            num = sum(s * darcy(q[p], *pipes[p]) for p, s in loop)
            den = sum(2 * abs(darcy(q[p], *pipes[p]) / q[p]) for p, s in loop)
            for p, s in loop:
                q[p] -= s * num / den
    return q


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

        def pipe(result, name):
            return next(p for p in result["pipes"] if p["name"] == name)

        def head(result, name):
            return next(n["head"] for n in result["nodes"] if n["node"] == name)

        # --- Single pipe hand calculation: Q = 0.05 m³/s, D = 200 mm, L = 1000 m, ε = 0.05 mm.
        one = sim("pipeNetwork", {"netlist": "H A 50\nP1 A B 1000 200 0.05\nD B 0.05"})
        p1 = pipe(one, "P1")
        v = 0.05 / (math.pi * 0.01)
        re = RHO * v * 0.2 / MU
        f_ref = colebrook(re, 0.05 / 200)
        assert abs(p1["flow"] - 0.05) < 1e-14 and abs(p1["velocity"] - v) < 1e-12 and abs(p1["reynolds"] - re) < 1e-6 * re
        assert abs(p1["friction"] - f_ref) < 1e-12 * f_ref, (p1["friction"], f_ref)
        assert abs(p1["swameeJain"] - f_ref) < 0.01 * f_ref and abs(swamee(re, 0.05 / 200) - p1["swameeJain"]) < 1e-14
        hf = f_ref * 1000 / 0.2 * v * v / (2 * G)
        assert abs(p1["headloss"] - hf) < 1e-10 and abs(head(one, "B") - (50 - hf)) < 1e-10, (p1["headloss"], hf)
        assert p1["regime"] == "turbulent" and p1["direction"] == "A→B" and not one["warnings"]
        assert abs(one["supply"] - 0.05) < 1e-14 and one["loops"] == []
        sj = sim("pipeNetwork", {"netlist": "H A 50\nP1 A B 1000 200 0.05\nD B 0.05", "friction": "swamee"})
        assert abs(pipe(sj, "P1")["friction"] - swamee(re, 0.05 / 200)) < 1e-14
        assert abs(head(sj, "B") - head(one, "B")) < 0.01 * hf

        # Laminar Hagen–Poiseuille: f = 64/Re and hf = 32 μ L V / (ρ g D²).
        lam = pipe(sim("pipeNetwork", {"netlist": "H A 5\nP1 A B 10 10 0\nD B 1e-6"}), "P1")
        vl = 1e-6 / (math.pi * 0.01 ** 2 / 4)
        assert lam["regime"] == "laminar" and abs(lam["friction"] - 64 / lam["reynolds"]) < 1e-14
        assert abs(lam["headloss"] - 32 * MU * 10 * vl / (RHO * G * 0.01 ** 2)) < 1e-14
        # Transitional Reynolds number is flagged.
        tr = sim("pipeNetwork", {"netlist": "H A 5\nP1 A B 10 50 0\nD B 1.18e-4"})
        assert pipe(tr, "P1")["regime"] == "transitional" and "transitional" in tr["warnings"][0], tr["warnings"]
        assert "1 transitional pipe(s)" in tr["summary"]

        # --- Two identical parallel pipes split the flow equally.
        par = sim("pipeNetwork", {"netlist": "H A 30\nP1 A B 200 100 0.1\nP2 A B 200 100 0.1\nD B 0.02"})
        assert abs(pipe(par, "P1")["flow"] - 0.01) < 1e-14 and abs(pipe(par, "P2")["flow"] - 0.01) < 1e-14
        assert len(par["loops"]) == 1 and abs(par["loops"][0]["headSum"]) < 1e-12

        # --- Two-loop grid: continuity < 1e-9, loop head sums < 1e-6 m, agrees with independent Hardy–Cross.
        grid = sim("pipeNetwork", {"netlist": GRID})
        assert grid["continuityResidual"] < 1e-9 and grid["loopResidual"] < 1e-6, (grid["continuityResidual"], grid["loopResidual"])
        assert len(grid["loops"]) == 2 and abs(grid["supply"] - 0.15) < 1e-13 and abs(grid["totalDemand"] - 0.15) < 1e-15
        hc = hardy_cross()
        for name, q in hc.items():
            assert abs(pipe(grid, name)["flow"] - q) < 1e-9, (name, pipe(grid, name)["flow"], q)
        for p in grid["pipes"]:
            assert abs(head(grid, p["a"]) - head(grid, p["b"]) - p["headloss"]) < 1e-9
            assert abs(p["headloss"] - darcy(p["flow"], p["length"], p["diameter"], p["roughness"])) < 1e-9
        assert grid["summary"].startswith("Pipe network: 7 pipe(s), 6 node(s), 2 loop(s)"), grid["summary"]
        # Reversed pipe orientation: negative flow, same magnitude and the physical direction reported.
        flipped = sim("pipeNetwork", {"netlist": GRID.replace("P2 B C 500", "P2 C B 500")})
        assert abs(pipe(flipped, "P2")["flow"] + pipe(grid, "P2")["flow"]) < 1e-12
        assert pipe(flipped, "P2")["flow"] < 0 and pipe(flipped, "P2")["direction"] == "B→C" == pipe(grid, "P2")["direction"]
        assert abs(head(flipped, "F") - head(grid, "F")) < 1e-9
        # A supply node (negative demand) can push water back towards the reservoir.
        back = sim("pipeNetwork", {"netlist": "H A 20\nP1 A B 300 150 0.05\nD B -0.02"})
        assert pipe(back, "P1")["flow"] < 0 and pipe(back, "P1")["direction"] == "B→A" and head(back, "B") > 20

        fails("pipeNetwork", {"netlist": GRID + "\nP8 X Y 100 100 0.1"}, "Disconnected nodes X, Y")
        fails("pipeNetwork", {"netlist": "P1 A B 100 100 0.1\nD B 0.01"}, "fixed-head (reservoir)")
        fails("pipeNetwork", {"netlist": "H A 10\nP1 A B 100 100 0.1\nP1 B C 100 100 0.1"}, "duplicate pipe name")
        fails("pipeNetwork", {"netlist": "H A 10\nP1 A A 100 100 0.1"}, "cannot connect a node to itself")
        fails("pipeNetwork", {"netlist": "H A 10\nP1 A B 100 100"}, "expected NAME from to")
        fails("pipeNetwork", {"netlist": "H A 10\nP1 A B 1e3x 100 0.1"}, "length must be a decimal")
        fails("pipeNetwork", {"netlist": "H A 10\nP1 A B 100 0.5 0"}, "diameter must be from 1")
        fails("pipeNetwork", {"netlist": "H A 10\nP1 A B 100 100 20"}, "roughness must be")
        fails("pipeNetwork", {"netlist": "H A 10\nD A 0.1\nP1 A B 100 100 0.1"}, "has a fixed head")
        fails("pipeNetwork", {"netlist": "H A 10\nD Z 0.1\nP1 A B 100 100 0.1"}, "Node Z has a demand")
        fails("pipeNetwork", {"netlist": "H A 10\nX1 A B 1 1 0"}, "lines start with a pipe name")
        fails("pipeNetwork", {"netlist": "  "}, "Enter a pipe network")
        fails("pipeNetwork", {"netlist": GRID, "density": 0}, "Density")
        fails("pipeNetwork", {"netlist": GRID, "friction": "moody"}, "Friction law must be one of")
        fails("pipeNetwork", {"netlist": GRID, "maxIterations": 1}, "did not converge in 1 Newton iteration")
        many = "H N0 100\n" + "\n".join("P%d N%d N%d 10 100 0.1" % (i, i, i + 1) for i in range(41))
        fails("pipeNetwork", {"netlist": many}, "limited to 40 pipes")

        # Unit-aware fluid properties: g/cm³ → kg/m³, mPa·s → Pa·s.
        resolved = page.evaluate("MathStudio.engineeringVisuals.resolveInputs('pipes',{density:'0.9982 g/cm^3',viscosity:'1.002 mPa*s'}).params")
        assert abs(resolved["density"] - 998.2) < 1e-9 and abs(resolved["viscosity"] - 1.002e-3) < 1e-15, resolved
        bad = page.evaluate("()=>{try{MathStudio.engineeringVisuals.resolveInputs('pipes',{viscosity:'3 m'});return null}catch(e){return e.message}}")
        assert bad and "expected a unit compatible with Pa*s" in bad, bad

        # --- Digital logic.
        def table(result):
            return {tuple(row[1:1 + len(result["inputs"])]): row[1 + len(result["inputs"]):] for row in result["rows"]}

        half = sim("digitalLogic", {"netlist": "IN A B\nS = XOR A B\nC = AND A B\nOUT S C"})
        assert half["kind"] == "combinational" and half["signals"] == ["A", "B", "S", "C"]
        assert [r[1:] for r in half["rows"]] == [[0, 0, 0, 0], [0, 1, 1, 0], [1, 0, 1, 0], [1, 1, 0, 1]], half["rows"]
        full = sim("digitalLogic", {"netlist": "IN A B Cin\nAX = XOR A B\nS = XOR AX Cin\nC1 = AND A B\nC2 = AND AX Cin\nCout = OR C1 C2\nOUT S Cout"})
        for (a, b, c), (s, co) in table(full).items():
            assert s == (a + b + c) % 2 and co == (a + b + c) // 2, (a, b, c, s, co)
        assert len(full["rows"]) == 8 and full["depth"] == 3
        # 3-input XOR gate is odd parity; truth table also matches a single-gate full-adder sum.
        par3 = sim("digitalLogic", {"netlist": "IN A B Cin\nS = XOR A B Cin\nM = XNOR A B Cin"})
        assert [r[4] for r in par3["rows"]] == [r[4] for r in full["rows"]] and all(r[5] == 1 - r[4] for r in par3["rows"])
        # XOR built from four NANDs equals XOR.
        nand = sim("digitalLogic", {"netlist": "IN A B\nN1 = NAND A B\nN2 = NAND A N1\nN3 = NAND B N1\nY = NAND N2 N3\nX = XOR A B\nOUT Y X"})
        assert all(r[3] == r[4] for r in nand["rows"]) and [r[3] for r in nand["rows"]] == [0, 1, 1, 0]
        # Every gate type against Python references, including constants 0/1, NOT and BUF.
        allg = sim("digitalLogic", {"netlist": "IN A B\nG1 = AND A B\nG2 = OR A B\nG3 = NAND A B\nG4 = NOR A B\nG5 = XOR A B\nG6 = XNOR A B\nG7 = NOT A\nG8 = BUF B\nG9 = AND A 1\nG10 = OR B 0"})
        for row in allg["rows"]:
            a, b = row[1], row[2]
            assert row[3:] == [a & b, a | b, 1 - (a & b), 1 - (a | b), a ^ b, 1 - (a ^ b), 1 - a, b, a, b], row
        # Zero delay and unit delay give identical settled truth tables; unit delay exposes the static hazard.
        hz = "IN A\nNA = NOT A\nY = AND A NA"
        z, u = sim("digitalLogic", {"netlist": hz}), sim("digitalLogic", {"netlist": hz, "delay": "unit"})
        assert z["rows"] == u["rows"] and all(r[3] == 0 for r in u["rows"]) and u["glitches"] >= 1 and z["glitches"] == 0
        assert u["maxSettle"] == 2 and "unit delay" in u["summary"]
        fu = sim("digitalLogic", {"netlist": "IN A B Cin\nAX = XOR A B\nS = XOR AX Cin\nC1 = AND A B\nC2 = AND AX Cin\nCout = OR C1 C2\nOUT S Cout", "delay": "unit"})
        assert fu["rows"] == full["rows"] and fu["maxSettle"] <= fu["depth"]
        # 10-input parity: 1024 rows.
        ten = sim("digitalLogic", {"netlist": "IN A0 A1 A2 A3 A4 A5 A6 A7 A8 A9\nP = XOR A0 A1 A2 A3 A4 A5 A6 A7\nQ = XOR P A8 A9\nOUT Q"})
        assert len(ten["rows"]) == 1024 and all(r[-1] == sum(r[1:11]) % 2 for r in ten["rows"])
        # 2-bit synchronous counter counts 0 → 3 and wraps.
        counter = sim("digitalLogic", {"netlist": "Q0 = DFF D0 CLK\nD0 = NOT Q0\nQ1 = DFF D1 CLK\nD1 = XOR Q1 Q0\nOUT Q1 Q0\nCYCLES 8"})
        assert counter["kind"] == "sequential" and counter["flipFlops"] == 2 and counter["signals"] == ["Q1", "Q0"]
        assert [2 * r[1] + r[2] for r in counter["rows"]] == [0, 1, 2, 3, 0, 1, 2, 3], counter["rows"]
        assert counter["summary"].startswith("Sequential circuit: 8 clock cycle(s), 2 D flip-flop(s)")
        # Shift register driven by a stimulus: each stage delays by one clock.
        shift = sim("digitalLogic", {"netlist": "IN D 10110000\nQ1 = DFF D\nQ2 = DFF Q1\nOUT Q1 Q2"})
        d = [r[1] for r in shift["rows"]]
        assert [r[2] for r in shift["rows"]] == [0] + d[:-1] and [r[3] for r in shift["rows"]] == [0, 0] + d[:-2]
        assert len(shift["rows"]) == 8

        fails("digitalLogic", {"netlist": "IN A\nX = AND A Y\nY = OR X A"}, "Combinational loop through nets")
        fails("digitalLogic", {"netlist": "IN A\nX = NOT X"}, "Combinational loop")
        fails("digitalLogic", {"netlist": "IN A\nY = AND A B"}, "Undriven net B")
        fails("digitalLogic", {"netlist": "IN A\nY = NOT A\nOUT Z"}, "Undriven net Z listed in OUT")
        fails("digitalLogic", {"netlist": "IN A B\nY = AND A B\nY = OR A B"}, "driven twice")
        fails("digitalLogic", {"netlist": "IN A B\nY = MUX A B"}, "unknown gate MUX")
        fails("digitalLogic", {"netlist": "IN A B\nY = NOT A B"}, "NOT takes exactly one input")
        fails("digitalLogic", {"netlist": "IN A\nY = AND A"}, "AND takes 2 to 8 inputs")
        fails("digitalLogic", {"netlist": "IN CLK\nY = NOT CLK"}, "CLK is the reserved clock")
        fails("digitalLogic", {"netlist": "IN A B C D E F G H I J K\nY = XOR A B"}, "limited to 10 inputs")
        fails("digitalLogic", {"netlist": "IN A\nQ = DFF A"}, "give input A a stimulus")
        fails("digitalLogic", {"netlist": "Q = DFF Q\nCYCLES 65"}, "CYCLES must be an integer from 1 to 64")
        fails("digitalLogic", {"netlist": "IN A\nY A B"}, "expected \"net = GATE")
        fails("digitalLogic", {"netlist": "IN A"}, "Add at least one gate")
        fails("digitalLogic", {"netlist": ""}, "Enter a logic netlist")
        fails("digitalLogic", {"netlist": "IN A B\nY = AND A B", "delay": "slow"}, "Gate delay model must be one of")

        # --- Catalog status and search invariants.
        statuses = page.evaluate("Object.fromEntries(MathStudio.engineeringCatalog.tools.map(t=>[t.id,t.status]))")
        assert statuses["fluids.pipe.network"] == "available" and statuses["electronics.digital.logic"] == "available"
        for available in ("gnss.positioning.least.squares", "control.frequency.response"):
            assert statuses[available] == "available", available
        assert statuses["signals.spectral.analysis"] == "planned"
        assert page.evaluate("MathStudio.engineeringCatalog.filter('physics','ode').map(t=>t.id)") == ["ode.ivp.scalar"]
        assert page.evaluate("MathStudio.engineeringCatalog.filter('','control orbit').length") == 0
        assert page.evaluate("MathStudio.engineeringCatalog.filter('fluids','pipe').map(t=>t.id)") == ["fluids.pipe.network"]
        assert "electronics.digital.logic" in page.evaluate("MathStudio.engineeringCatalog.filter('electrical','flip-flop').map(t=>t.id)")

        # --- UI: catalog Open routing via keyboard, export, layout at 390 and 1280.
        page.locator('[data-workspace="engineering"]').click()
        status = page.locator("#eng-visual-status")
        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#eng-discipline").select_option("")
            page.locator("#eng-search").fill("colebrook")
            card = page.locator('#eng-results article[data-tool-id="fluids.pipe.network"]')
            assert card.count() == 1 and "planned" not in card.inner_text().lower() and card.locator("button").count() == 1
            assert card.locator("[data-visual]").count() == 1
            card.locator("button").focus()
            page.keyboard.press("Enter")
            assert page.locator("#eng-visual-select").input_value() == "pipes"
            assert status.inner_text().startswith("Pipe network: 7 pipe(s), 6 node(s), 2 loop(s)"), status.inner_text()
            assert page.evaluate("document.activeElement.id") == "eng-visual-netlist"
            page.locator("#eng-search").fill("truth table flip-flop")
            card = page.locator('#eng-results article[data-tool-id="electronics.digital.logic"]')
            assert card.count() == 1 and card.locator("button").count() == 1
            card.locator("button").focus()
            page.keyboard.press("Enter")
            assert page.locator("#eng-visual-select").input_value() == "logic"
            assert status.inner_text().startswith("Combinational circuit: truth table of 8 row(s) over 3 input(s)"), status.inner_text()
            assert page.evaluate("document.activeElement.tagName") == "TEXTAREA"
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            for sel in ("#eng-visual-canvas", "#eng-visual-netlist"):
                assert page.locator(sel).bounding_box()["width"] <= width, sel

        # Typed sequential netlist via keyboard, animation advances, export of the timing table.
        page.locator("#eng-visual-netlist").fill("Q0 = DFF D0 CLK\nD0 = NOT Q0\nQ1 = DFF D1 CLK\nD1 = XOR Q1 Q0\nOUT Q1 Q0\nCYCLES 8")
        page.locator("#eng-visual-run").focus()
        page.keyboard.press("Enter")
        assert status.inner_text().startswith("Sequential circuit: 8 clock cycle(s)"), status.inner_text()
        page.wait_for_function("() => MathStudio.engineeringVisuals.frame() > 5")
        logic_table = page.evaluate("MathStudio.engineeringVisuals.tableOf(MathStudio.engineeringVisuals.current())")
        assert logic_table["name"] == "SIM_LOGIC" and logic_table["headers"] == ["t_step", "Q1", "Q0"]
        assert [2 * r[1] + r[2] for r in logic_table["rows"]] == [0, 1, 2, 3, 0, 1, 2, 3]
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#eng-visual-table").click()
        tables = page.evaluate("MathStudio.dataTables.tables.map(t=>({name:t.name,rows:t.rows.length}))")
        assert len(tables) == before + 1 and tables[-1] == {"name": "SIM_LOGIC", "rows": 8}, tables[-1]
        # Invalid netlist shows an error and disables export; a valid run recovers.
        page.locator('[data-workspace="engineering"]').click()
        page.locator("#eng-visual-netlist").fill("IN A\nX = AND A Y\nY = OR X A")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: Combinational loop"), status.inner_text()
        assert status.evaluate("el => el.classList.contains('error')") and page.locator("#eng-visual-table").is_disabled()
        page.locator("#eng-visual-delay").select_option("unit")
        page.locator("#eng-visual-netlist").fill("IN A\nNA = NOT A\nY = AND A NA")
        page.locator("#eng-visual-run").click()
        assert "glitch transition(s)" in status.inner_text() and not page.locator("#eng-visual-table").is_disabled()

        page.locator("#eng-visual-select").select_option("pipes")
        page.locator("#eng-visual-viscosity").fill("1.002 mPa*s")
        page.locator("#eng-visual-run").click()
        text = status.inner_text()
        assert text.startswith("Pipe network: 7 pipe(s)") and "1.002 mPa*s → 0.001002 Pa*s" in text, text
        pipes_table = page.evaluate("MathStudio.engineeringVisuals.tableOf(MathStudio.engineeringVisuals.current())")
        assert pipes_table["name"] == "SIM_PIPES" and pipes_table["headers"][:4] == ["index", "flow_m3_s", "velocity_m_s", "headloss_m"]
        assert len(pipes_table["rows"]) == 7 and pipes_table["rows"][0][6] == "P1" and abs(pipes_table["rows"][0][1] - hc["P1"]) < 1e-9
        page.locator("#eng-visual-netlist").fill("H A 10\nP1 A B 100 100 0.1\nP2 C D 100 100 0.1")
        page.locator("#eng-visual-run").click()
        assert status.inner_text().startswith("Cannot animate: Disconnected nodes C, D"), status.inner_text()
        assert page.locator("#eng-visual-canvas").get_attribute("aria-label")

        # Reduced motion: final frame immediately, no autoplay.
        reduced = browser.new_page(viewport={"width": 390, "height": 844}, reduced_motion="reduce")
        reduced.on("pageerror", lambda error: errors.append(str(error)))
        reduced.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        reduced.locator('[data-workspace="engineering"]').click()
        for tool in ("fluids.pipe.network", "electronics.digital.logic"):
            reduced.evaluate("t => MathStudio.engineeringCatalog.open(t)", tool)
            assert reduced.evaluate("MathStudio.engineeringVisuals.frame()") == reduced.evaluate("MathStudio.engineeringVisuals.frames")
            assert reduced.locator("#eng-visual-toggle").get_attribute("aria-pressed") == "true"
        assert not errors, errors
        browser.close()
    print("PASS engineering pipe networks + digital logic: hand/Hardy–Cross references, residuals, truth tables, counter, invalid input, units, routing, export, keyboard, reduced motion, 390/1280")


if __name__ == "__main__":
    main()
