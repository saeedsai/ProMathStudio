"""Matrix extras browser regression: numerical references vs numpy, failures and responsive keyboard UI."""
from pathlib import Path
import os
import numpy as np
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
API = "MathStudio.matrixExtras"


def main():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or "/usr/bin/chromium",
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.set_content(html, wait_until="load")
        call = lambda name, arg: page.evaluate(f"([n, a]) => {API}[n](a)", [name, arg])
        fail = lambda name, arg: page.evaluate(
            f"([n, a]) => {{ try {{ {API}[n](a); return null; }} catch (e) {{ return e.message; }} }}", [name, arg])

        r = call("cholesky", "4 12 -16\n12 37 -43\n-16 -43 98")
        assert r["L"] == [[2, 0, 0], [6, 1, 0], [-8, 5, 3]], r
        hilbert = [[1 / (i + j + 1) for j in range(4)] for i in range(4)]
        r = call("cholesky", hilbert)
        assert r["residual"] < 1e-12, r
        assert np.allclose(r["L"], np.linalg.cholesky(np.array(hilbert)), atol=1e-13)
        assert "pivot 2" in fail("cholesky", "1 2\n2 1")
        assert "symmetric" in fail("cholesky", "1 2\n3 1")

        # Rank and bases on a 5x5 rank-3 matrix; compare against numpy rank and projectors.
        rng = np.random.default_rng(7)
        A5 = rng.integers(-3, 4, (5, 3)) @ rng.integers(-3, 4, (3, 5))
        r = call("rank", A5.astype(float).tolist())
        assert r["rank"] == np.linalg.matrix_rank(A5) == 3 and r["nullity"] == 2, r
        N = np.array(r["nullBasis"])
        Q = np.array(r["columnBasis"])
        assert np.linalg.norm(A5 @ N) / np.linalg.norm(A5) < 1e-12
        assert np.allclose(N.T @ N, np.eye(2), atol=1e-12) and np.allclose(Q.T @ Q, np.eye(3), atol=1e-12)
        # The column-space projector must leave A unchanged.
        assert np.allclose(Q @ Q.T @ A5, A5, atol=1e-10)
        assert np.allclose(r["singularValues"], np.linalg.svd(A5, compute_uv=False), atol=1e-10)
        r = call("rank", "1 2 3\n2 4 6\n1 1 1")
        n = np.array(r["nullBasis"])[:, 0]
        assert r["rank"] == 2 and np.allclose(abs(n @ np.array([1, -2, 1]) / 6 ** 0.5), 1, atol=1e-12), r

        # Determinant of a 6x6 matrix needing pivoting, vs numpy.
        A6 = np.array([[0, 2, 1, 0, 3, 1], [1, 0, 4, 2, 0, 1], [3, 1, 0, 1, 2, 0],
                       [2, 5, 1, 0, 1, 4], [1, 1, 1, 3, 0, 2], [0, 4, 2, 1, 1, 0]], dtype=float)
        r = call("determinant", A6.tolist())
        assert abs(r["det"] - np.linalg.det(A6)) <= 1e-10 * abs(np.linalg.det(A6)), (r["det"], np.linalg.det(A6))
        assert r["trace"] == np.trace(A6) and r["residual"] < 1e-14
        r = call("charpoly", [[2, 1], [1, 2]])
        assert r["coefficients"] == [1, -4, 3], r
        r = call("charpoly", A6.tolist())
        assert np.allclose(r["coefficients"], np.poly(A6), rtol=1e-9, atol=1e-8), (r["coefficients"], np.poly(A6))
        r = call("norms", "3 0 0\n0 -5 0\n0 0 1")
        assert abs(r["two"] - 5) < 1e-13 and r["one"] == 5 and r["infinity"] == 5 and abs(r["condition2"] - 5) < 1e-12
        r = call("norms", A6.tolist())
        assert abs(r["two"] - np.linalg.norm(A6, 2)) < 1e-12 and abs(r["condition2"] - np.linalg.cond(A6)) < 1e-9 * np.linalg.cond(A6)

        for bad, needle in [("1 2\n3", "Ragged"), ("\n".join(["1"] * 9), "At most 8 rows"),
                            ("1 2\n3 abc", "not a decimal"), ("1e400", "finite")]:
            assert needle in fail("parseMatrix", bad), bad

        # UI at 1280 px: keyboard Run, output, Save to Data Tables.
        page.locator('[data-workspace="calculator"]').click()
        details = page.locator("#matrix-extras-details")
        details.locator("summary").focus()
        page.keyboard.press("Enter")
        assert details.evaluate("e => e.open")
        page.locator("#matrix-extras-input").fill("1 2 3\n2 4 6\n1 1 1")
        page.locator("#matrix-extras-op").select_option("rank")
        assert page.locator("#matrix-extras-to-table").is_disabled()
        page.locator("#matrix-extras-run").focus()
        page.keyboard.press("Enter")
        out = page.locator("#matrix-extras-output")
        assert out.get_attribute("role") == "status" and out.get_attribute("aria-live") == "polite"
        text = out.inner_text()
        assert "rank = 2; nullity = 1" in text and "Verification ‖A·N‖F" in text, text
        before = page.evaluate("MathStudio.dataTables.tables.length")
        page.locator("#matrix-extras-to-table").click()
        assert page.evaluate("MathStudio.dataTables.tables.length") == before + 1
        assert page.evaluate("MathStudio.dataTables.tables.at(-1).name").startswith("Matrix_Null_Space")

        # Error state and recovery.
        page.locator('[data-workspace="calculator"]').click()
        details.evaluate("e => e.open = true")
        page.locator("#matrix-extras-input").fill("1 2\n3")
        page.locator("#matrix-extras-run").click()
        assert "Ragged rows" in out.inner_text() and "error" in out.get_attribute("class")
        assert page.locator("#matrix-extras-to-table").is_disabled()
        page.locator("#matrix-extras-input").fill("4 12 -16\n12 37 -43\n-16 -43 98")
        assert "error" not in (out.get_attribute("class") or "")
        page.locator("#matrix-extras-op").select_option("cholesky")
        page.locator("#matrix-extras-run").click()
        assert "Cholesky" in out.inner_text() and "error" not in (out.get_attribute("class") or "")
        assert page.locator("#matrix-extras-to-table").is_enabled()

        # 390 px: no horizontal overflow, controls at least 40 px tall.
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#matrix-extras-input").fill("\n".join(" ".join(str(-1234.5678 * (i + j)) for j in range(8)) for i in range(8)))
        page.locator("#matrix-extras-op").select_option("determinant")
        page.locator("#matrix-extras-run").click()
        width = page.evaluate("document.documentElement.scrollWidth")
        assert width <= 391, width
        for sel in ("#matrix-extras-op", "#matrix-extras-run", "#matrix-extras-to-table", "#matrix-extras-details summary"):
            box = page.locator(sel).bounding_box()
            assert box["height"] >= 40 and box["x"] + box["width"] <= 391, (sel, box)
        assert not errors, errors
        browser.close()
    print("PASS: matrix extras references (Cholesky, SVD rank/bases, LU det, char poly, norms), failures and responsive UI")


if __name__ == "__main__":
    main()
