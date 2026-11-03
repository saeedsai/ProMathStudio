"""Unit conversion browser regression: API references, UI conversion, Enter key, errors, recovery and 390/1280 layout."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def rel(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(b))


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert (ROOT / "src/units-tools.js").read_text(encoding="utf-8").rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        conv = lambda v, a, b: page.evaluate("([v,a,b])=>MathStudio.units.convert(v,a,b).value", [v, a, b])
        assert rel(conv(1, "mi", "m"), 1609.344)
        assert rel(conv(1, "psi", "Pa"), 6894.757293168361)
        assert rel(conv(100, "degC", "degF"), 212)
        assert rel(conv(-40, "°C", "°F"), -40)
        assert rel(conv(60, "mph", "m/s"), 26.8224)
        assert page.evaluate("MathStudio.units.simplify('kg*m/s^2').named") == "N"
        assert page.evaluate("MathStudio.units.dimensions('N').text") == "M L T^-2"
        assert page.evaluate("Object.isFrozen(MathStudio.units)")
        for args in (["1", "m", "s"], ["1", "qux", "m"], ["1", "kg*/m", "N"], ["NaN", "m", "m"], ["25", "degC", "K*m/m"]):
            assert page.evaluate("a=>{try{MathStudio.units.convert(...a);return false}catch(e){return !!e.message}}", args), args

        page.locator('[data-workspace="calculator"]').first.click()
        details = page.locator("#calculator-panel #units-details")
        assert details.count() == 1
        details.locator("summary").click()
        assert details.evaluate("e=>e.open")
        for sel in ("#units-value", "#units-from", "#units-to"):
            label = page.evaluate("s=>document.querySelector(s).closest('label').textContent.trim()", sel)
            assert label, sel
        out = page.locator("#units-output")
        assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
        page.locator("#units-convert").click()
        assert out.inner_text().startswith("1609.344 m"), out.inner_text()
        assert "Dimension: L" in out.inner_text()

        page.fill("#units-value", "100")
        page.fill("#units-from", "°C")
        page.fill("#units-to", "degF")
        assert "Inputs changed" in out.inner_text()
        page.locator("#units-to").press("Enter")
        assert out.inner_text().startswith("212 degF"), out.inner_text()
        assert "Absolute temperature" in out.inner_text()

        page.locator("#units-delta").check()
        page.fill("#units-value", "10")
        page.locator("#units-value").press("Enter")
        assert out.inner_text().startswith("18 degF"), out.inner_text()
        page.locator("#units-delta").uncheck()

        page.fill("#units-value", "1")
        page.fill("#units-from", "m")
        page.fill("#units-to", "s")
        page.locator("#units-convert").click()
        assert "error" in (out.get_attribute("class") or "")
        assert "Dimension mismatch" in out.inner_text()
        page.fill("#units-to", "km")
        assert "error" not in (out.get_attribute("class") or "")
        page.locator("#units-to").press("Enter")
        assert out.inner_text().startswith("0.001 km"), out.inner_text()

        page.fill("#units-from", "kN/m^2")
        page.fill("#units-to", "")
        page.locator("#units-from").press("Enter")
        assert "1000 kg·m^-1·s^-2" in out.inner_text(), out.inner_text()
        assert "M L^-1 T^-2" in out.inner_text()

        page.fill("#units-from", "W/(m^2*degC)")
        page.fill("#units-to", "W/(m^2*K)")
        page.locator("#units-convert").click()
        assert out.inner_text().startswith("1 W/(m^2*K)"), out.inner_text()

        for width in (390, 1280):
            page.set_viewport_size({"width": width, "height": 844})
            page.locator("#units-convert").scroll_into_view_if_needed()
            for sel in ("#units-value", "#units-from", "#units-to", "#units-convert", "#units-details summary"):
                box = page.locator(sel).bounding_box()
                assert box and box["height"] >= 40 and box["x"] >= 0 and box["x"] + box["width"] <= width + 0.5, (width, sel, box)
            assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth"), width
        assert not errors, errors
        browser.close()
    print("PASS: unit conversion references, temperatures, simplification, keyboard, recovery and responsive layout")


if __name__ == "__main__":
    main()
