"""Numerical Methods accessible controls, live errors, keyboard and mobile regression."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True,
            executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        assert page.locator("#num-output").get_attribute("role") == "status"
        assert page.locator("#num-output").get_attribute("aria-live") == "polite"

        for method in ("scalar", "system", "poisson", "heat", "quadrature"):
            page.locator("#num-method").select_option(method)
            for width in (390, 768, 1280):
                page.set_viewport_size({"width": width, "height": 844})
                audit = page.evaluate("""() => {
                    const root = document.getElementById('numerical-panel');
                    const all = [...root.querySelectorAll('input,select,button')];
                    const visible = all.filter(e => e.getClientRects().length &&
                        getComputedStyle(e).visibility !== 'hidden');
                    const ids = [...root.querySelectorAll('[id]')].map(e => e.id);
                    return {
                        count: visible.length,
                        short: visible.map(e => [e.id, e.getBoundingClientRect().height])
                            .filter(x => x[1] < 39.5),
                        unnamed: visible.filter(e => e.tagName === 'BUTTON'
                            ? !e.textContent.trim() && !e.getAttribute('aria-label')
                            : !e.labels?.length && !e.getAttribute('aria-label')).map(e => e.id),
                        duplicateIds: ids.filter((id,i) => ids.indexOf(id) !== i),
                        overflow: document.documentElement.scrollWidth > innerWidth + 1
                    };
                }""")
                assert audit["count"] >= 5, (method, width, audit)
                assert not audit["short"], (method, width, audit)
                assert not audit["unnamed"], (method, width, audit)
                assert not audit["duplicateIds"], (method, width, audit)
                assert not audit["overflow"], (method, width, audit)

        page.locator("#num-method").select_option("scalar")
        page.locator("#num-run").focus()
        page.keyboard.press("Enter")
        assert "Roots in" in page.locator("#num-output").inner_text()
        assert not page.locator("#num-output").evaluate("(el) => el.classList.contains('error')")
        page.locator("#num-start").fill("10")
        page.locator("#num-end").fill("-10")
        page.locator("#num-run").focus()
        page.keyboard.press("Space")
        assert page.locator("#num-output").evaluate("(el) => el.classList.contains('error')")
        assert "max > min" in page.locator("#num-output").inner_text()
        assert page.locator("#num-to-table").is_disabled()
        page.locator("#num-start").fill("-10")
        page.locator("#num-end").fill("10")
        page.locator("#num-run").focus()
        page.keyboard.press("Enter")
        assert "Roots in" in page.locator("#num-output").inner_text()
        assert not page.locator("#num-output").evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS Numerical Methods responsive 40px, accessible labels, keyboard, live errors and recovery")


if __name__ == "__main__":
    main()
