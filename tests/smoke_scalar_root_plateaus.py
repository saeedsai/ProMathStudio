"""Constant-zero/nonzero root plateaus, smooth and tangent roots, and live UI."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")

        def solve(expr, lo=-1, hi=1):
            return page.evaluate(
                """([expr,lo,hi]) => window.MathStudio.numerical.scalarRoots(
                    expr,'x',lo,hi,{samples:350,tolerance:1e-9})""",
                [expr, lo, hi])

        zero = solve("x-x")
        assert zero["rootStatus"] == "sampled-zero-plateau", zero
        assert zero["roots"] == [] and zero["maxResidual"] is None, zero
        assert "non-isolated" in zero["note"], zero

        near_zero = solve("0*x+0.000000000001")
        assert near_zero["rootStatus"] == "sampled-nonzero-plateau", near_zero
        assert near_zero["roots"] == [] and near_zero["residuals"] == [], near_zero

        nonzero = solve("x*0+2")
        assert nonzero["rootStatus"] == "sampled-nonzero-plateau", nonzero
        assert nonzero["roots"] == [], nonzero

        smooth = solve("x^2-0.25")
        assert any(abs(x-0.5)<1e-5 for x in smooth["roots"]), smooth
        assert any(abs(x+0.5)<1e-5 for x in smooth["roots"]), smooth
        assert all(r<=1e-9 for r in smooth["residuals"]), smooth

        tangent = solve("(x-0.23)^2")
        assert any(abs(x-0.23)<1e-3 for x in tangent["roots"]), tangent
        assert all(r<=1e-9 for r in tangent["residuals"]), tangent

        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        page.locator("#num-expression").fill("x-x")
        page.locator("#num-start").fill("-1")
        page.locator("#num-end").fill("1")
        page.locator("#num-run").click()
        output = page.locator("#num-output")
        assert "non-isolated zeros possible" in output.inner_text(), output.inner_text()
        assert not output.evaluate("(el)=>el.classList.contains('error')")
        page.locator("#num-expression").fill("x^2-0.25")
        page.locator("#num-run").click()
        assert "Maximum absolute residual:" in output.inner_text()
        assert "non-isolated zeros possible" not in output.inner_text()
        assert not errors, errors
        browser.close()
    print("PASS sampled constant-zero/nonzero, smooth/tangent roots, UI recovery")


if __name__ == "__main__":
    main()
