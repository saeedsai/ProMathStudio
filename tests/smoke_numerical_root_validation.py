"""Scalar root tolerance, invalid input focus, recovery and hidden-domain isolation."""
import math
import os
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 390, "height": 844})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        page.locator('[data-workspace="editor"]').click()
        page.locator("#num-details").evaluate("(el) => el.open=true")
        page.locator("#num-method").select_option("scalar")
        tolerance = page.locator("#num-tolerance")
        assert tolerance.is_visible(), "Scalar roots must expose the tolerance control"
        page.locator("#num-expression").fill("x^2-2=0")
        page.locator("#num-start").fill("0")
        page.locator("#num-end").fill("2")
        tolerance.fill("1e-9")
        page.locator("#num-run").click()
        output = page.locator("#num-output")
        assert not output.evaluate("(el) => el.classList.contains('error')")
        roots_line = output.inner_text().splitlines()[0]
        assert roots_line.startswith("Roots in [0, 2]: "), roots_line
        roots = [float(value.strip()) for value in roots_line.split(": ", 1)[1].split(",")]
        assert any(abs(root - math.sqrt(2)) < 1e-5 for root in roots), roots
        assert not page.locator("#num-to-table").is_disabled()

        for invalid in ("0", "0.1", ""):
            tolerance.fill(invalid)
            page.locator("#num-run").click()
            assert output.evaluate("(el) => el.classList.contains('error')")
            assert tolerance.get_attribute("aria-invalid") == "true"
            assert tolerance.get_attribute("aria-describedby") == "num-output"
            assert tolerance.evaluate("(el) => document.activeElement === el")
            assert page.locator("#num-to-table").is_disabled()
        tolerance.fill("1e-9")
        page.locator("#num-end").fill("0")
        page.locator("#num-run").click()
        assert page.locator("#num-end").get_attribute("aria-invalid") == "true"
        assert "max > min" in output.inner_text()
        page.locator("#num-end").fill("2")
        page.locator("#num-run").click()
        assert not output.evaluate("(el) => el.classList.contains('error')")
        assert tolerance.get_attribute("aria-invalid") is None
        assert page.locator("#num-end").get_attribute("aria-invalid") is None

        # Hidden scalar domain fields must not block a valid nonlinear system solve.
        page.locator("#num-start").fill("10")
        page.locator("#num-end").fill("-10")
        page.locator("#num-method").select_option("system")
        page.locator("#num-expression").fill("x^2+y^2=5; x-y=1")
        page.locator("#num-variable").fill("x,y")
        page.locator("#num-guess").fill("1,1")
        page.locator("#num-run").click()
        assert "Converged: true" in output.inner_text(), output.inner_text()
        assert not output.evaluate("(el) => el.classList.contains('error')")
        assert not errors, errors
        browser.close()
    print("PASS scalar tolerance, root reference, invalid focus, recovery and hidden system fields")


if __name__ == "__main__":
    main()
