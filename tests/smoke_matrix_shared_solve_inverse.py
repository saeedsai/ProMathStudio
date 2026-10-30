"""Browser regression: shared matrix inverse solver, UI recovery and mobile controls."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"],
        )
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        panel = page.locator("#matrix-tools")
        panel.evaluate("(e)=>e.open=true")

        result = page.evaluate("""() => {
          const m=MathStudio.matrixTools, A=[[0,2,0],[3,0,0],[0,0,4]];
          const inv=m.inverse(A);
          return [0,1,2].map(j=>({
            column:inv.map(row=>row[j]),
            solved:m.solve(A,[0,1,2].map(i=>Number(i===j))).solution
          }));
        }""")
        for item in result:
            assert all(abs(a-b) < 1e-12 for a,b in zip(item["column"], item["solved"])), item

        inputs = page.locator("#mat-grid input")
        for i, value in enumerate(["1e-9", "0", "0", "1e9"]):
            inputs.nth(i).fill(value)
        page.locator("#mat-inverse").click()
        output = page.locator("#mat-result").inner_text()
        assert "1000000000" in output and "1e-9" in output, output
        assert page.locator("#mat-send").is_enabled()

        for i, value in enumerate(["1", "2", "2", "4"]):
            inputs.nth(i).fill(value)
        page.locator("#mat-inverse").click()
        assert "Singular" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()

        for i, value in enumerate(["0", "1", "1", "0"]):
            inputs.nth(i).fill(value)
        page.locator("#mat-inverse").click()
        assert page.locator("#mat-send").is_enabled()
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.locator("#mat-inverse").is_visible()
        assert page.locator("#mat-send").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS shared inverse solver, scaled UI, singular recovery and mobile")


if __name__ == "__main__":
    main()
