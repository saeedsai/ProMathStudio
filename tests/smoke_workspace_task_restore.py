"""Remember each workspace's task choice across tab changes (no persisted state)."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="calculator"]').click()
        page.locator("#workspace-task-select").select_option("matrix")
        assert page.locator("#matrix-tools").evaluate("(e) => e.open")
        assert page.locator("#workspace-task-select").input_value() == "matrix"
        page.locator('[data-workspace="graph"]').click()
        assert page.locator("#workspace-task-select").input_value() == "basic"
        page.locator("#workspace-task-select").select_option("axes")
        assert page.locator("#ui-graph-axes").evaluate("(e) => e.open")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#workspace-task-select").select_option("numerical")
        assert page.locator("#symbolic-panel .cas-wrap").is_hidden()
        page.locator('[data-workspace="calculator"]').click()
        assert page.locator("#workspace-task-select").input_value() == "matrix"
        assert page.locator("#matrix-tools").evaluate("(e) => e.open")
        assert "matrix" in page.locator("#task-description").inner_text().lower()
        page.locator('[data-workspace="editor"]').click()
        assert page.locator("#workspace-task-select").input_value() == "numerical"
        assert page.locator("#symbolic-panel .cas-wrap").is_hidden()
        page.locator("#workspace-task-select").select_option("basic")
        assert page.locator("#symbolic-panel .cas-wrap").is_visible()
        page.locator('[data-workspace="graph"]').click()
        assert page.locator("#workspace-task-select").input_value() == "axes"
        assert page.locator("#ui-graph-axes").evaluate("(e) => e.open")
        page.locator('[data-workspace="data"]').click()
        assert page.locator("#workspace-task-select").input_value() == "basic"
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator('[data-workspace="editor"]').click()
        assert page.locator("#workspace-task-select").input_value() == "basic"
        assert page.locator("#symbolic-panel .cas-wrap").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS per-workspace task restoration, Equation/CAS visibility and mobile navigation")

if __name__ == "__main__":
    main()
