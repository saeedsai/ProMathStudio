"""Browser regression: canonical solver registry, both real Matrix UI consumers and mobile."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        page.locator("#matrix-tools").evaluate("(e) => e.open = true")
        metadata = page.evaluate("""() => {
          const r=MathStudio.engineeringSolvers;
          return {ids:r.list().map(x=>x.id),unknown:r.get('__proto__'),
                  result:r.execute('matrix.solve.real.small',{A:[[2,1],[1,3]],b:[5,7]}).solution,
                  schema:r.get('matrix.solve.real.small').inputSchema,
                  immutable:Object.isFrozen(r.get('matrix.solve.real.small').inputSchema.A.rows),
                  missing:r.executeResult('matrix.solve.real.small',{A:[[1,0],[0,1]]}),
                  singular:r.executeResult('matrix.solve.real.small',
                    {A:[[1,2],[2,4]],b:[3,6]}),
                  inverse:r.executeResult('matrix.inverse.real.small',
                    {A:[[2,0],[0,4]]})};
        }""")
        assert metadata["ids"] == ["matrix.solve.real.small", "matrix.inverse.real.small"]
        assert metadata["unknown"] is None
        assert abs(metadata["result"][0] - 1.6) < 1e-12
        assert metadata["schema"]["A"]["rows"] == [2, 3]
        assert metadata["schema"]["b"]["length"] == "A.rows"
        assert metadata["immutable"]
        assert metadata["missing"]["error"]["code"] == "MISSING_INPUT"
        assert metadata["singular"]["error"]["code"] == "SOLVER_REJECTED"
        assert metadata["inverse"]["ok"]
        assert abs(metadata["inverse"]["value"][1][1] - 0.25) < 1e-12

        matrix = page.locator("#mat-grid input")
        for i, value in enumerate(["2", "1", "1", "3"]):
            matrix.nth(i).fill(value)
        rhs = page.locator("#mat-rhs-grid input")
        for i, value in enumerate(["5", "7"]):
            rhs.nth(i).fill(value)
        page.locator("#mat-solve").click()
        assert "Relative residual" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_enabled()
        page.locator("#mat-inverse").click()
        assert "Infinity-norm condition number" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_enabled()

        for i, value in enumerate(["1", "2", "2", "4"]):
            matrix.nth(i).fill(value)
        for i, value in enumerate(["3", "6"]):
            rhs.nth(i).fill(value)
        page.locator("#mat-solve").click()
        assert "Singular" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()
        page.locator("#mat-inverse").click()
        assert "Singular" in page.locator("#mat-result").inner_text()
        assert page.locator("#mat-send").is_disabled()

        page.set_viewport_size({"width": 390, "height": 844})
        for i, value in enumerate(["2", "0", "0", "3"]):
            matrix.nth(i).fill(value)
        page.locator("#mat-inverse").click()
        assert page.locator("#mat-send").is_enabled()
        assert page.locator("#mat-inverse").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS canonical registry, two Matrix consumers, validation and mobile")


if __name__ == "__main__":
    main()
