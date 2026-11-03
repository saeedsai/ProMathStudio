"""Pole, jump and oscillation screening for scalar roots, bounded diagnostics and UI recovery."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def solve(expr, lo=-1, hi=1, samples=350):
            return page.evaluate(
                """([expr,lo,hi,samples]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',lo,hi,{samples,tolerance:1e-9})""", [expr, lo, hi, samples])

        # Pole between grid points: no root, one pole location near 0.3.
        pole = solve("1/(x-0.3)")
        assert pole["roots"] == [], pole
        assert pole["rejectedSignChangeCount"] >= 1, pole
        assert any(abs(r["x"] - 0.3) < 1e-6 and r["kind"] == "possible-pole" for r in pole["rejectedSignChanges"]), pole
        assert pole["rootStatus"] == "discontinuity-screened", pole
        # Pole exactly on a grid point (nonfinite sample).
        grid_pole = solve("1/x")
        assert grid_pole["roots"] == [] and grid_pole["rejectedSignChanges"][0] == {"x": 0, "kind": "possible-pole"}, grid_pole
        # tan(x): true root at 0 retained; poles at +-pi/2 rejected.
        tan = solve("tan(x)", -2, 2)
        assert len(tan["roots"]) == 1 and abs(tan["roots"][0]) < 1e-9, tan
        poles = sorted(r["x"] for r in tan["rejectedSignChanges"])
        assert len(poles) == 2 and all(abs(abs(x) - math.pi / 2) < 1e-6 for x in poles), tan
        assert all(r["kind"] == "possible-pole" for r in tan["rejectedSignChanges"]), tan
        # Bounded jumps are classified as jumps, not poles.
        for expr in ("abs(x)/x", "(x-0.12345)/abs(x-0.12345)"):
            jump = solve(expr)
            assert jump["roots"] == [] and jump["rejectedSignChangeCount"] >= 1, jump
            assert all(r["kind"] == "possible-jump" for r in jump["rejectedSignChanges"]), jump
        # Diagnostic list is bounded even when many poles exist.
        many = solve("tan(x)", -100, 100, 1600)
        assert many["rejectedSignChangeCount"] >= 60 and len(many["rejectedSignChanges"]) == 20, many["rejectedSignChangeCount"]
        # Oscillation: sin(1/x) is under-resolved near 0; found roots still satisfy residual.
        osc = solve("sin(1/x)")
        assert osc["denseOscillationIntervals"] >= 1 and osc["rootStatus"] == "under-resolved-oscillation", osc
        assert 1 <= len(osc["denseOscillationLocations"]) <= 20, osc
        assert all(abs(x) < 0.1 for x in osc["denseOscillationLocations"]), osc
        assert max(osc["residuals"]) <= 1e-9 and "under-resolved" in osc["note"], osc
        # Smooth controls: no discontinuity or oscillation flags.
        for expr in ("x^2-0.25", "x-0.5", "sin(3*x)"):
            clean = solve(expr)
            assert clean["rejectedSignChangeCount"] == 0 and clean["denseOscillationIntervals"] == 0, clean
            assert clean["rootStatus"] == "screened", clean
        assert solve("x-x")["rejectedSignChanges"] == []

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-start").fill("-1")
        page.locator("#num-end").fill("1")
        output = page.locator("#num-output")
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#num-expression").fill("1/(x-0.3)")
            page.locator("#num-run").click()
            text = output.inner_text()
            assert "Rejected sign changes (possible pole/jump): 1 at 0.3 (pole)" in text, text
            assert output.get_attribute("aria-live") == "polite"
        page.locator("#num-expression").fill("sin(1/x)")
        page.locator("#num-run").click()
        assert "Under-resolved oscillation intervals: " in output.inner_text()
        assert "Under-resolved oscillation intervals: 0" not in output.inner_text()
        page.locator("#num-end").fill("-2")
        page.locator("#num-run").click()
        assert output.evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-end").fill("1")
        page.locator("#num-expression").fill("x-0.5")
        page.locator("#num-run").click()
        text = output.inner_text()
        assert "Rejected sign changes (possible pole/jump): 0" in text and "Under-resolved oscillation intervals: 0" in text, text
        assert not output.evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS scalar-root pole/jump/oscillation screening, bounded diagnostics and UI recovery")


if __name__ == "__main__":
    main()
