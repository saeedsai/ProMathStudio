"""Barycentric polynomial interpolation numerical, conditioning and browser regression."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    source = (ROOT / "src/interpolation-tools.js").read_text(encoding="utf-8")
    assert "function barycentricWeights(samples)" in source
    assert source.rstrip("\n") in html
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content(html, wait_until="load")
        quadratic = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1],[1,2],[2,5],[3,10]],queries:[0,0.5,1.5,2.5,3],
            method:'barycentric'
        })""")
        assert quadratic["type"] == "interpolation-barycentric", quadratic
        for x,y in quadratic["rows"]:
            assert abs(y-(x*x+1)) < 1e-10, (x,y)
        cubic = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[-1,2],[0,1],[1,0],[2,5]],
            queries:[-1,-0.5,0.5,1.5,2],method:'barycentric'
        })""")
        for x,y in cubic["rows"]:
            assert abs(y-(x**3-2*x+1)) < 1e-10, (x,y)
        exact = page.evaluate("""() => MathStudio.interpolationTools.interpolate({
            points:[[0,1e12],[1,0.000001]],queries:[0,1],method:'barycentric'
        })""")
        assert exact["rows"] == [[0,1e12],[1,1e-6]], exact
        for invalid in [
            {"points":[[0,0],[0,1]],"queries":[0],"method":"barycentric"},
            {"points":[[1,0],[0,1]],"queries":[0],"method":"barycentric"},
            {"points":[[0,0],[1,1]],"queries":[-0.1],"method":"barycentric"},
            {"points":[[0,0],[1,1]],"queries":[1.1],"method":"barycentric"},
            {"points":[[0,0],[1,1]],"queries":[float("inf")],"method":"barycentric"},
            {"points":[[0,0],[1e-15,1],[1,2]],"queries":[0.5],"method":"barycentric"},
            {"points":[[i,i] for i in range(17)],"queries":[1],"method":"barycentric"},
            {"points":[[0,0],[1,1]],"queries":[],"method":"barycentric"},
        ]:
            assert page.evaluate("""o => {
                try {MathStudio.interpolationTools.interpolate(o);return false;}
                catch(e){return !!e.message;}
            }""", invalid), invalid
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-method").select_option("barycentric")
        page.locator("#interp-samples").fill("0,1\n1,2\n2,5\n3,10")
        page.locator("#interp-queries").fill("0.5,1.5,2.5")
        page.locator("#interp-run").click()
        assert "Barycentric polynomial" in page.locator("#interp-output").inner_text()
        assert "oscillate" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-table").is_enabled()
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#interp-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before+1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).name").startswith("Interpolation_Barycentric")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-run").click()
        page.locator("#interp-to-graph").click()
        assert page.locator("#graph-panel .graph-canvas-wrap").is_visible()
        assert page.evaluate("MathStudio.graphData.getState().points.length") == 3
        page.locator('[data-workspace="editor"]').click()
        page.locator("#interp-details").evaluate("(e) => e.open=true")
        page.locator("#interp-queries").fill("4")
        assert page.locator("#interp-to-table").is_disabled()
        page.locator("#interp-run").click()
        assert "outside sample domain" in page.locator("#interp-output").inner_text()
        assert page.locator("#interp-to-graph").is_disabled()
        page.set_viewport_size({"width":390,"height":844})
        assert page.locator("#interp-method").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS: barycentric polynomial references, exact knots, limits, invalid input and exports")

if __name__ == "__main__":
    main()
