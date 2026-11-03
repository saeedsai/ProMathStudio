"""Brent refinement refuses pole and jump brackets with explicit, located diagnostics; true roots
still refine; UI shows the refusal and recovers."""
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

        def refuse(o):
            return page.evaluate("o=>{try{MathStudio.brentTools.refine(o);return null}catch(e){return e.message}}", o)

        def located(message, x, tol=1e-6):
            value = float(message.split("x ≈ ", 1)[1].split(":", 1)[0])
            return abs(value - x) < tol

        # The 1e12 magnitude cap stops refinement at distance ~1e-12^(1/order) from an order-k pole.
        for expr, lo, hi, x, tol in (("tan(x)", 1, 2, math.pi / 2, 1e-6), ("1/(x-0.3)", 0, 1, 0.3, 1e-6),
                                     ("1/(x-1)", 0, 2, 1.0, 1e-6), ("-1/(x+2)^3", -3, 0, -2.0, 2e-4)):
            message = refuse({"expression": expr, "lo": lo, "hi": hi})
            assert message and message.startswith("Suspected pole near x ≈ "), (expr, message)
            assert located(message, x, tol) and "No root is claimed" in message, (expr, message)
        for expr, x in (("abs(x-0.4)/(x-0.4)", 0.4), ("(x-0.25)/sqrt((x-0.25)^2)*0.5", 0.25)):
            message = refuse({"expression": expr, "lo": 0, "hi": 1})
            assert message and message.startswith("Suspected jump discontinuity near x ≈ "), (expr, message)
            assert located(message, x), (expr, message)
        # True roots, including tan(x) through 0 and a steep but continuous function, still refine.
        assert abs(page.evaluate("MathStudio.brentTools.refine({expression:'tan(x)',lo:-1,hi:1}).x")) < 1e-9
        steep = page.evaluate("MathStudio.brentTools.refine({expression:'1000*(x-0.123)',lo:0,hi:1})")
        assert abs(steep["x"] - 0.123) < 1e-9, steep
        assert abs(page.evaluate("MathStudio.brentTools.refine({expression:'x^3-x-2',lo:1,hi:2}).x") - 1.5213797068045676) < 1e-8

        page.locator('[data-workspace="editor"]').click()
        page.locator("#brent-details").evaluate("(e)=>e.open=true")
        page.locator("#brent-expression").fill("tan(x)")
        page.locator("#brent-lo").fill("1")
        page.locator("#brent-hi").fill("2")
        page.locator("#brent-run").click()
        out = page.locator("#brent-output")
        assert out.inner_text().startswith("Suspected pole near x ≈ 1.57079"), out.inner_text()
        assert out.evaluate("e=>e.classList.contains('error')") and page.locator("#brent-to-table").is_disabled()
        page.locator("#brent-lo").fill("-1")
        page.locator("#brent-hi").fill("1")
        page.locator("#brent-run").click()
        assert "Brent-Dekker" in out.inner_text() and page.locator("#brent-to-table").is_enabled()
        assert not errors, errors
        browser.close()
    print("PASS Brent pole/jump refusal with located diagnostics, true-root refinement and UI recovery")


if __name__ == "__main__":
    main()
