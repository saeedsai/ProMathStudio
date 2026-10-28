"""Bounded offline 1D linear interpolation numerical, negative, table and graph regression."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    assert '<script id="promath-interpolation-tools">' in html
    assert "function interpolate({points,queries,method=\'linear\'}" in html
    assert "method===\'pchip\'?pchipSlopes(samples):null" in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium", args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(html, wait_until="load")
        result = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1],[1,3],[2,5]], queries:[2,0.5,0,1.5,1]
        })""")
        assert result["rows"] == [[0,1],[0.5,2],[1,3],[1.5,4],[2,5]], result
        assert result["domain"] == [0,2]
        # Exact knots must retain the supplied value even with severe cancellation.
        knot = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1e12],[1,0.000001]],queries:[0,1]
        })""")
        assert knot["rows"] == [[0,1e12],[1,1e-6]], knot
        for invalid in [
            {"points":[[0,0]],"queries":[0]},
            {"points":[[0,0],[0,1]],"queries":[0]},
            {"points":[[1,1],[0,0]],"queries":[0]},
            {"points":[[0,0],[1,1]],"queries":[-0.1]},
            {"points":[[0,0],[1,1]],"queries":[1.1]},
            {"points":[[0,0],[1,1]],"queries":[float("inf")]},
            {"points":[[0,0],[1,1]],"queries":[]},
            {"points":[[0,0],[1,1]],"queries":[0,""]},
            {"points":[[0,0],[1,1]],"queries":[0,1e13]},
        ]:
            assert page.evaluate("""o => {
                try {MathStudio.interpolationTools.interpolate(o);return false;}
                catch(e){return !!e.message;}
            }""", invalid), invalid
        assert page.evaluate("""() => {
            try {MathStudio.interpolationTools.parsePairs('0,1,2\\n1,2');return false;}
            catch(e){return /exactly/.test(e.message);}
        }""")
        assert page.evaluate("""() => MathStudio.interpolationTools.parsePairs('0,0\\n1,1')""") == [["0","0"],["1","1"]]
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-run").click()
        assert "5 query results" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#interp-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).columns") == ["x","y"]
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.evaluate("""() => MathStudio.dataTables.importData({
            headers:['x','y'],rows:[[0,0],[1,3],[2,6]]
        },'InterpolationSamples')""")
        page.locator("#interp-from-table").click()
        assert "1,3" in page.locator("#interp-samples").input_value()
        page.locator("#interp-queries").fill("0 0.5 1 1.5 2")
        assert page.locator("#interp-to-graph").is_disabled()
        page.locator("#interp-run").click()
        assert "1.5 → 4.5" in page.locator("#interp-output").inner_text()
        page.locator("#interp-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") == 5
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-queries").fill("3")
        assert page.locator("#interp-to-table").is_disabled()
        page.locator("#interp-run").click()
        assert "outside sample domain" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-graph").is_disabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#interp-run").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: 1D interpolation references, invalid samples, domain, table and graph handoff")

if __name__ == "__main__":
    main()
