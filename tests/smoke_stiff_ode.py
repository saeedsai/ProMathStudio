"""Stiff TR-BDF2 solver: analytic references, budgets, failures and responsive/keyboard UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

SOLVE = """o => { try { const r = MathStudio.stiffOde.solve(o);
  return {end: r.rows.at(-1), rows: r.rows.length, accepted: r.accepted, rejected: r.rejected,
   jac: r.jacobianEvaluations, ratio: r.maxErrorRatio, local: r.maxLocalError, columns: r.columns,
   monotone: r.rows.every((row, i) => i === 0 || (o.t1 > o.t0 ? row[0] > r.rows[i-1][0] : row[0] < r.rows[i-1][0]))};
 } catch (e) { return {error: e.message}; } }"""


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 860})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        solve = lambda **o: page.evaluate(SOLVE, o)

        # Stiff scalar y'=-1000(y-cos t), y(0)=0: analytic solution with e^{-1000t} transient.
        a = 1000.0
        ref = (a * a * math.cos(1) + a * math.sin(1)) / (a * a + 1) - a * a / (a * a + 1) * math.exp(-a)
        r = solve(expression="-1000*(y-cos(t))", t0=0, t1=1, y0=0, rtol=1e-6, atol=1e-9)
        assert "error" not in r, r
        assert r["end"][0] == 1 and abs(r["end"][1] - ref) / abs(ref) < 1e-4, (r, ref)
        assert r["accepted"] < 500 and r["monotone"] and r["jac"] >= r["accepted"], r
        assert 0 < r["ratio"] <= 1 and r["local"] > 0, r
        # A stiffer rate (explicit stability needs >1e5 steps) stays cheap.
        r6 = solve(expression="-1000000*(y-cos(t))", t0=0, t1=1, y0=0, rtol=1e-6, atol=1e-9)
        assert "error" not in r6 and r6["accepted"] < 500, r6
        assert abs(r6["end"][1] - math.cos(1)) < 1e-5, r6

        # Linear 2x2 system with eigenvalues -2 and -2000: y=e^{-2t}+e^{-2000t}, z=e^{-2t}-e^{-2000t}.
        s = solve(expression="-1001*y+999*z", expressionZ="999*y-1001*z", t0=0, t1=1, y0=2, z0=0,
                  rtol=1e-6, atol=1e-9)
        assert s["columns"] == ["t", "y", "z"] and s["accepted"] < 500, s
        assert abs(s["end"][1] - math.exp(-2)) < 1e-4 and abs(s["end"][2] - math.exp(-2)) < 1e-4, s
        mid = page.evaluate("""() => { const r = MathStudio.stiffOde.solve({expression:'-1001*y+999*z',
            expressionZ:'999*y-1001*z',t0:0,t1:0.002,y0:2,z0:0,rtol:1e-7,atol:1e-10}); return r.rows.at(-1); }""")
        assert abs(mid[1] - (math.exp(-0.004) + math.exp(-4))) < 1e-4, mid
        assert abs(mid[2] - (math.exp(-0.004) - math.exp(-4))) < 1e-4, mid

        # Van der Pol mu=1000 on a short interval: slow manifold y' ~ -y/(mu(y^2-1)).
        v = solve(expression="z", expressionZ="1000*(1-y^2)*z-y", t0=0, t1=3, y0=2, z0=0,
                  rtol=1e-4, atol=1e-7)
        assert "error" not in v and v["accepted"] < 1000, v
        assert abs(v["end"][1] - 1.998) < 1e-3 and abs(v["end"][2] + 2 / 3000) < 1e-4, v

        # Non-stiff exponential decay, forward and backward.
        e = solve(expression="-y", t0=0, t1=2, y0=1, rtol=1e-6, atol=1e-10)
        assert abs(e["end"][1] - math.exp(-2)) / math.exp(-2) < 1e-4, e
        b = solve(expression="-y", t0=2, t1=0, y0=math.exp(-2), rtol=1e-6, atol=1e-10)
        assert b["end"][0] == 0 and abs(b["end"][1] - 1) < 1e-4 and b["monotone"], b

        # Explicit failures.
        bad = [
            (dict(expression="y^2", t0=0, t1=2, y0=1), ("Newton", "underflow", "non-finite", "budget")),
            (dict(expression="-y", t0=1, t1=1), ("differ",)),
            (dict(expression="-y", rtol=0), ("Relative tolerance",)),
            (dict(expression="-y", atol=-1), ("Absolute tolerance",)),
            (dict(expression="2*+"), ("initial point",)),
            (dict(expression=""), ("dy/dt",)),
            (dict(expression="-y", y0="abc"), ("Initial y",)),
            (dict(expression="-1000*(y-cos(t))", maxSteps=10), ("Step budget",)),
            (dict(expression="-y", maxSteps=2.5), ("Step budget",)),
            (dict(expression="sqrt(-1)"), ("non-finite", "initial point")),
        ]
        for options, words in bad:
            out = solve(**options)
            assert "error" in out and any(w in out["error"] for w in words), (options, out)

        # UI: panel follows the existing ODE panel in the Equation workspace.
        page.locator('[data-workspace="editor"]').click()
        page.locator("#workspace-task-select").select_option("ode")
        assert page.evaluate("document.getElementById('ode-details').nextElementSibling.id") == "stiff-ode-details"
        panel = page.locator("#stiff-ode-details")
        panel.locator("summary").focus()
        page.keyboard.press("Enter")
        assert panel.evaluate("(e) => e.open")
        out = page.locator("#stiff-ode-output")
        assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
        assert page.locator("#stiff-ode-to-table").is_disabled()
        for sel in ("#stiff-ode-dy", "#stiff-ode-dz", "#stiff-ode-t0", "#stiff-ode-t1", "#stiff-ode-y0",
                    "#stiff-ode-z0", "#stiff-ode-rtol", "#stiff-ode-atol"):
            assert page.evaluate("s => !!document.querySelector(s).closest('label')", sel), sel
        page.locator("#stiff-ode-run").focus()
        page.keyboard.press("Enter")
        text = out.inner_text()
        assert "TR-BDF2" in text and "accepted" in text and "Jacobian evaluations" in text, text
        assert "not certified" in text and not page.locator("#stiff-ode-output.error").count(), text
        assert page.locator("#stiff-ode-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#stiff-ode-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).columns") == ["t", "y"]

        # System through the UI, then error + recovery.
        page.locator('[data-workspace="editor"]').click()
        panel.evaluate("(e) => e.open = true")
        page.locator("#stiff-ode-dy").fill("-1001*y+999*z")
        page.locator("#stiff-ode-dz").fill("999*y-1001*z")
        page.locator("#stiff-ode-y0").fill("2")
        page.locator("#stiff-ode-z0").fill("0")
        page.locator("#stiff-ode-run").click()
        assert "z ≈" in out.inner_text(), out.inner_text()
        page.locator("#stiff-ode-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).columns") == ["t", "y", "z"]
        page.locator('[data-workspace="editor"]').click()
        panel.evaluate("(e) => e.open = true")
        page.locator("#stiff-ode-rtol").fill("5")
        assert page.locator("#stiff-ode-to-table").is_disabled()
        page.locator("#stiff-ode-run").click()
        assert page.locator("#stiff-ode-output.error").is_visible()
        assert "Recovery" in out.inner_text() and page.locator("#stiff-ode-to-table").is_disabled()
        page.locator("#stiff-ode-rtol").fill("0.000001")
        page.locator("#stiff-ode-run").click()
        assert not page.locator("#stiff-ode-output.error").count()

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            assert page.locator("#stiff-ode-run").is_visible(), width
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 0, (width, overflow)
            box = panel.bounding_box()
            assert box["x"] >= 0 and box["x"] + box["width"] <= width + 0.5, (width, box)
            for sel in ("#stiff-ode-run", "#stiff-ode-to-table", "#stiff-ode-dy", "#stiff-ode-rtol"):
                h = page.locator(sel).bounding_box()["height"]
                assert h >= 40, (sel, width, h)
        assert not errors, errors
        browser.close()
    print("PASS: stiff TR-BDF2 references (scalar, 2x2, Van der Pol, decay), failures and UI")


if __name__ == "__main__":
    main()
