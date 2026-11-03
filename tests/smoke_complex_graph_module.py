"""Extracted Complex Graph controller: numerical references, keyboard, mobile, invalid recovery
and project round-trip after moving the inline script to src/complex-graph.js."""
import json
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
                                     args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("dialog", lambda dialog: dialog.accept())
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")

        def ev(a, b, kind):
            return page.evaluate("([a,b,k]) => window.ProMathComplexGraph.evaluate(a,b,k)", [a, b, kind])

        assert ev(1, 2, "square") == [-3, 4]
        inv = ev(3, 4, "inverse")
        assert abs(inv[0] - 0.12) < 1e-15 and abs(inv[1] + 0.16) < 1e-15, inv
        ex = ev(1, math.pi, "exp")
        assert abs(ex[0] + math.e) < 1e-12 and abs(ex[1]) < 1e-12, ex
        assert ev(2, -3, "identity") == [2, -3]
        assert page.evaluate("window.ProMathComplexGraph.evaluate(0,0,'inverse').every(Number.isNaN)")

        page.locator('[data-workspace="graph"]').click()
        page.locator("#complex-graph-workbench > summary").focus()
        page.keyboard.press("Enter")
        assert page.locator("#complex-graph-workbench").evaluate("(el) => el.open")
        status, detail = page.locator("#complex-status"), page.locator("#complex-detail")
        assert status.get_attribute("aria-live") == "polite"
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#complex-real").fill("1")
            page.locator("#complex-imag").fill("2")
            page.locator("#complex-function").select_option("square")
            page.locator("#complex-plot").focus()
            page.keyboard.press("Enter")
            assert status.inner_text() == "Plotted Argand point.", status.inner_text()
            assert "f(z) = -3 + 4i" in detail.inner_text(), detail.inner_text()
            overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
            assert overflow <= 1, (width, overflow)
            box = page.locator("#complex-plot").bounding_box()
            assert box["height"] >= 24, box
        page.locator("#complex-view").select_option("3d")
        assert status.inner_text() == "Plotted magnitude surface."
        page.locator("#complex-view").select_option("2d")

        # Invalid inputs are reported and the next valid plot recovers.
        page.locator("#complex-real").fill("")
        page.locator("#complex-plot").click()
        assert status.inner_text().startswith("Enter finite real and imaginary values"), status.inner_text()
        page.locator("#complex-real").fill("2e6")
        page.locator("#complex-plot").click()
        assert status.inner_text().startswith("Enter finite real and imaginary values")
        page.locator("#complex-real").fill("0")
        page.locator("#complex-imag").fill("0")
        page.locator("#complex-function").select_option("inverse")
        assert status.inner_text() == "Function undefined or overflows at this point."
        page.locator("#complex-real").fill("3")
        page.locator("#complex-imag").fill("4")
        page.locator("#complex-plot").click()
        assert "f(z) = 0.12 − 0.16i" in detail.inner_text(), detail.inner_text()

        # A saved-project round trip leaves the extracted controller functional.
        saved = page.evaluate("MathStudio.bridge.export()")
        page.locator("#hub-project-file").set_input_files({
            "name": "p.json", "mimeType": "application/json", "buffer": json.dumps(saved).encode("utf-8")})
        page.wait_for_function("() => document.querySelector('#hub-status').textContent.startsWith('Project imported.')")
        page.locator("#complex-function").select_option("exp")
        page.locator("#complex-real").fill("0")
        page.locator("#complex-imag").fill("0")
        page.locator("#complex-plot").click()
        assert "f(z) = 1 + 0i" in detail.inner_text(), detail.inner_text()
        assert not errors, errors
        browser.close()
    print("PASS extracted complex graph module: references, keyboard, 390/768/1280, recovery, project round trip")


if __name__ == "__main__":
    main()
