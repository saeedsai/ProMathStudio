"""PCHIP reference, monotonicity, invalid input, stale export and browser integration."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert '<script id="promath-interpolation-tools">' in html
    assert "function pchipSlopes(samples)" in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content(html, wait_until="load")
        straight = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1],[1,3],[2,5],[3,7]],queries:[0,0.5,1.5,2.5,3],method:'pchip'
        })""")
        assert straight["type"] == "interpolation-pchip", straight
        for x,y in straight["rows"]:
            assert abs(y-(2*x+1)) < 1e-10, straight
        two = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1],[2,5]],queries:[0,0.5,1,1.5,2],method:'pchip'
        })""")
        assert two["rows"] == [[0,1],[0.5,2],[1,3],[1.5,4],[2,5]], two
        shape = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,0],[1,1],[2,1],[3,2]],
            queries:[0,0.25,0.5,0.75,1,1.25,1.5,1.75,2,2.25,2.5,2.75,3],
            method:'pchip'
        })""")
        assert shape["rows"][0] == [0,0] and shape["rows"][-1] == [3,2]
        for x,y in shape["rows"]:
            if x < 1:
                assert 0 <= y <= 1, (x,y)
            elif x <= 2:
                assert y == 1, (x,y)
            else:
                assert 1 <= y <= 2, (x,y)
        extrema = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,0],[1,2],[2,0]],queries:[0.25,0.5,0.75,1.25,1.5,1.75],
            method:'pchip'
        })""")
        assert all(0 <= y <= 2 for _,y in extrema["rows"]), extrema
        exact = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1e12],[1,0.000001],[2,0.000002]],queries:[0,1,2],
            method:'pchip'
        })""")
        assert exact["rows"] == [[0,1e12],[1,1e-6],[2,2e-6]], exact
        for invalid in [
            {"points":[[0,0],[0,1]],"queries":[0],"method":"pchip"},
            {"points":[[2,0],[1,1]],"queries":[1],"method":"pchip"},
            {"points":[[0,0],[1,1]],"queries":[-1],"method":"pchip"},
            {"points":[[0,0],[1,1]],"queries":[2],"method":"pchip"},
            {"points":[[0,0],[1,1]],"queries":[0],"method":"spline"},
            {"points":[[0,0],[1,1]],"queries":[],"method":"pchip"},
            {"points":[[0,0],[1,1]],"queries":[""],"method":"pchip"},
        ]:
            assert page.evaluate("""o => {
                try {MathStudio.interpolationTools.interpolate(o);return false;}
                catch(e){return !!e.message;}
            }""", invalid), invalid
        page.locator('[data-workspace="solver"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-method").select_option("pchip")
        page.locator("#interp-samples").fill("0,0\n1,1\n2,1\n3,2")
        page.locator("#interp-queries").fill("0.5,1.5,2.5")
        page.locator("#interp-run").click()
        assert "PCHIP" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#interp-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before+1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).name").startswith("Interpolation_PCHIP")
        page.locator('[data-workspace="solver"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-run").click()
        page.locator("#interp-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") == 3
        page.locator('[data-workspace="solver"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-method").select_option("linear")
        assert page.locator("#interp-to-table").is_disabled()
        page.locator("#interp-run").click()
        assert "Piecewise-linear" in page.locator("#interp-output").inner_text()
        page.locator("#interp-queries").fill("4")
        assert page.locator("#interp-to-graph").is_disabled()
        page.locator("#interp-run").click()
        assert "outside sample domain" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-table").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#interp-method").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: PCHIP references, monotonicity, extrema, invalid inputs, table and graph UI")

if __name__ == "__main__":
    main()
