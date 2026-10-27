"""Regression: bounded curve-fit residual diagnostics, CSV export, and stale-state handling."""
import csv
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
        page = browser.new_page(viewport={"width": 1280, "height": 900}, accept_downloads=True)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"), wait_until="load")
        points = [[x, 2*x+3] for x in range(5)]
        fit = page.evaluate("(points) => MathStudio.curveFit.analyze(points, 'linear')", points)
        assert fit["used"] == 5 and fit["excluded"] == 0, fit
        assert abs(fit["r2"]-1) < 1e-12 and fit["rmse"] < 1e-10, fit
        assert fit["mae"] < 1e-10 and fit["sse"] < 1e-18, fit
        assert len(fit["residuals"]) == len(points)
        for (x,y,predicted,residual), (expected_x,expected_y) in zip(fit["residuals"], points):
            assert x == expected_x and y == expected_y
            assert math.isclose(predicted, expected_y, abs_tol=1e-10)
            assert math.isclose(residual, y-predicted, abs_tol=1e-12)
        omitted = page.evaluate("(points) => MathStudio.curveFit.analyze(points, 'linear')", points + [[None, 9]])
        assert omitted["used"] == 5 and omitted["excluded"] == 1, omitted
        noisy = page.evaluate("(points) => MathStudio.curveFit.analyze(points, 'linear')",
                              [[0,0],[1,2],[2,3],[3,5]])
        assert noisy["sse"] > 0 and noisy["mae"] > 0 and noisy["r2"] < 1
        assert math.isclose(noisy["sse"], sum(row[3]**2 for row in noisy["residuals"]), rel_tol=1e-12)
        assert math.isclose(noisy["mae"], sum(abs(row[3]) for row in noisy["residuals"])/4, rel_tol=1e-12)
        for bad in [[[0,1]], [[1,1],[1,2]], [[0,1],[float("inf"),2]]]:
            try:
                page.evaluate("(points) => MathStudio.curveFit.analyze(points, 'linear')", bad)
                assert False, f"Invalid or singular input accepted: {bad}"
            except Exception as error:
                if isinstance(error, AssertionError):
                    raise
        page.locator('[data-workspace="graph"]').click()
        page.get_by_role("button", name="Plot table data").click()
        page.locator("#dt-chart-type").select_option("scatter")
        page.locator("#fit-model").select_option("linear")
        assert page.locator("#fit-export").is_disabled()
        page.locator("#fit-run").click()
        assert page.locator("#fit-export").is_enabled()
        assert "MAE" in page.locator("#fit-result").inner_text()
        with page.expect_download() as download_info:
            page.locator("#fit-export").click()
        download = download_info.value
        assert download.suggested_filename == "ProMathStudio_fit_residuals.csv"
        with open(download.path(), newline="", encoding="utf-8") as stream:
            rows = list(csv.reader(stream))
        assert rows[0] == ["x","y","predicted","residual"], rows
        assert len(rows) >= 3
        for row in rows[1:]:
            assert len(row) == 4 and all(math.isfinite(float(x)) for x in row), row
            assert math.isclose(float(row[1])-float(row[2]), float(row[3]), abs_tol=1e-8)
        page.locator("#fit-model").select_option("poly")
        assert page.locator("#fit-export").is_disabled(), "Changing the model must invalidate previous residuals"
        page.locator("#fit-model").select_option("linear")
        page.locator("#fit-run").click()
        assert page.locator("#fit-export").is_enabled()
        page.locator("#fit-clear").click()
        assert page.locator("#fit-export").is_disabled()
        assert not errors, errors
        browser.close()
    print("PASS curve-fit residuals, MAE/SSE, CSV download, invalid inputs and clear state")

if __name__ == "__main__":
    main()
