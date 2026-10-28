"""Golden-section bounded minimization: reference, boundary, invalid, UI and table regression."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    source = (ROOT / "src/minimize-tools.js").read_text(encoding="utf-8")
    assert source.rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content(html, wait_until="load")
        run = lambda options: page.evaluate("o => MathStudio.minimizeTools.minimize(o)", options)
        quadratic = run({"expression": "(x-2)^2+1", "lo": 0, "hi": 4})
        assert abs(quadratic["x"]-2) < 1e-5 and abs(quadratic["value"]-1) < 1e-9, quadratic
        assert quadratic["iterations"] < 200 and quadratic["evaluations"] <= 205
        lower = run({"expression": "x^2", "lo": 1, "hi": 5})
        assert lower["x"] == 1 and lower["value"] == 1, lower
        upper = run({"expression": "-x", "lo": 0, "hi": 3})
        assert upper["x"] == 3 and upper["value"] == -3, upper
        flat = run({"expression": "5", "lo": 0, "hi": 3})
        assert abs(flat["x"]-1.5) < 1e-5 and flat["value"] == 5, flat
        for invalid in [
            {"expression": ""}, {"expression": "x", "lo": 1, "hi": 1},
            {"expression": "x", "lo": 2, "hi": 1},
            {"expression": "x", "lo": "NaN", "hi": 1},
            {"expression": "x", "lo": 0, "hi": 1, "tolerance": 0},
            {"expression": "x", "lo": 0, "hi": 1, "tolerance": 0.1},
            {"expression": "x", "lo": 0, "hi": 1, "maxIterations": 2},
            {"expression": "(x-2)^2", "lo": 0, "hi": 4, "maxIterations": 8, "tolerance": 1e-10},
            {"expression": "1/0", "lo": 0, "hi": 1},
            {"expression": "sqrt(-1)", "lo": 0, "hi": 1},
        ]:
            assert page.evaluate("""o => {
                try {MathStudio.minimizeTools.minimize(o);return false;}
                catch(e){return !!e.message;}
            }""", invalid), invalid
        page.locator('[data-workspace="editor"]').click()
        page.locator("#minimize-details").evaluate("(e) => e.open=true")
        page.locator("#minimize-run").click()
        assert "Golden-section" in page.locator("#minimize-output").inner_text()
        assert page.locator("#minimize-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#minimize-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before+1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).name").startswith("Numerical_Minimum")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#minimize-details").evaluate("(e) => e.open=true")
        page.locator("#minimize-lo").fill("4")
        assert page.locator("#minimize-to-table").is_disabled()
        page.locator("#minimize-run").click()
        assert "Upper bound" in page.locator("#minimize-output").inner_text()
        assert page.locator("#minimize-to-table").is_disabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#minimize-run").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: golden-section numerical references, boundaries, flat, invalid and browser table export")

if __name__ == "__main__":
    main()
