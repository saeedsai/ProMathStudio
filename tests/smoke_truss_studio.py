"""Standalone structural 2D truss studio: FEM references, equilibrium, singularity and UI."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

HTML = (Path(__file__).resolve().parents[1] / "tools" / "truss-studio.html").read_text(encoding="utf-8")

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844}, accept_downloads=True)
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content(HTML, wait_until="load")
        assert "Analysis complete" in page.locator("#status").inner_text()
        result = page.evaluate("() => TrussStudio.solve(TrussStudio.example)")
        assert result["residual"] < 1e-9, result
        forces = {m["id"]: m["force"] for m in result["members"]}
        assert abs(forces["AC"] + 10000 / 2**0.5) < 1e-7, forces
        assert abs(forces["BC"] + 10000 / 2**0.5) < 1e-7, forces
        assert abs(forces["AB"] - 5000) < 1e-7, forces
        reactions = {n["id"]: n for n in result["nodes"]}
        assert abs(reactions["A"]["ry"] - 5000) < 1e-7
        assert abs(reactions["B"]["ry"] - 5000) < 1e-7
        assert abs(reactions["A"]["rx"]) < 1e-7
        assert result["maxDisplacement"] > 0
        assert page.locator("#members tr").count() == 3
        assert page.locator("#joints tr").count() == 3
        assert page.locator("#drawing line").count() == 6
        assert page.locator("#export").is_enabled()
        with page.expect_download() as download:
            page.locator("#export").click()
        assert download.value.suggested_filename == "truss-members.csv"
        singular = {"nodes":[{"id":"A","x":0,"y":0,"fixX":True,"fixY":True},{"id":"B","x":1,"y":0,"fy":-10}],"members":[{"id":"AB","a":"A","b":"B","E":200e9,"A":0.001}]}
        page.locator("#model").fill(__import__("json").dumps(singular))
        page.locator("#run").click()
        assert "Unstable truss" in page.locator("#status").inner_text()
        assert page.locator("#export").is_disabled()
        page.locator("#example").click()
        assert "Analysis complete" in page.locator("#status").inner_text()
        invalid = page.evaluate("""() => {const x=structuredClone(TrussStudio.example);x.members[0].A=-1;try{TrussStudio.solve(x);return false;}catch(e){return e.message.includes('positive');}}""")
        assert invalid
        assert not errors, errors
        browser.close()
    print("Truss studio: reference forces, reactions, equilibrium, unstable model, validation, export, mobile UI PASS")

if __name__ == "__main__":
    main()
