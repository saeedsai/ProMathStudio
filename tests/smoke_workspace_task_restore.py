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
        page.get_by_role("button", name="Matrices", exact=True).click()
        assert page.locator("#matrix-tools").evaluate("(e) => e.open")
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Matrices"
        page.locator('[data-workspace="graph"]').click()
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Plot functions"
        page.get_by_role("button", name="Axis limits", exact=True).click()
        assert page.locator("#ui-graph-axes").evaluate("(e) => e.open")
        page.locator('[data-workspace="solver"]').click()
        page.get_by_role("button", name="Numerical methods", exact=True).click()
        assert page.locator("#symbolic-panel .cas-wrap").is_hidden()
        page.locator('[data-workspace="calculator"]').click()
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Matrices"
        assert page.locator("#matrix-tools").evaluate("(e) => e.open")
        assert "matrix" in page.locator("#task-description").inner_text().lower()
        page.locator('[data-workspace="solver"]').click()
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Numerical methods"
        assert page.locator("#symbolic-panel .cas-wrap").is_hidden()
        page.get_by_role("button", name="Symbolic solve", exact=True).click()
        assert page.locator("#symbolic-panel .cas-wrap").is_visible()
        page.locator('[data-workspace="graph"]').click()
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Axis limits"
        assert page.locator("#ui-graph-axes").evaluate("(e) => e.open")
        page.locator('[data-workspace="data"]').click()
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Edit table"
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator('[data-workspace="solver"]').click()
        assert page.locator('.task-choice[aria-pressed="true"]').inner_text() == "Symbolic solve"
        assert page.locator("#symbolic-panel .cas-wrap").is_visible()
        assert not errors, errors
        browser.close()
    print("PASS per-workspace task restoration, default isolation, solver visibility and mobile navigation")

if __name__ == "__main__":
    main()
