"""Matrix extras browser regression: fixed numerical references (precomputed once with numpy; CI has no
numpy), exact integer determinant/characteristic polynomial, identity checks, failures and responsive UI."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
API = "MathStudio.matrixExtras"



def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))] for i in range(len(a))]


def transpose(a):
    return [list(r) for r in zip(*a)]


def frob(a):
    return sum(v * v for r in a for v in r) ** 0.5


def max_abs_diff(a, b):
    return max(abs(x - y) for ra, rb in zip(a, b) for x, y in zip(ra, rb))


def identity(n):
    return [[float(i == j) for j in range(n)] for i in range(n)]


# Reference constants computed once with numpy 2.x (linalg cholesky / svd / 2-norm / cond).
HILB_L = [[1.0, 0.0, 0.0, 0.0], [0.5, 0.28867513459481287, 0.0, 0.0],
          [0.3333333333333333, 0.2886751345948129, 0.07453559924999305, 0.0],
          [0.25, 0.2598076211353316, 0.11180339887498901, 0.018898223650463678]]
A5 = [[6.0, -7.0, 5.0, -11.0, 2.0], [4.0, -4.0, 5.0, -11.0, 2.0], [6.0, -13.0, 6.0, -2.0, -4.0],
      [-12.0, 14.0, 0.0, 7.0, -4.0], [0.0, -6.0, 9.0, -3.0, -6.0]]  # integer rank-3 product
A5_SV = [30.843068438363595, 13.079668664310484, 11.073725522075845, 0.0, 0.0]
A6_NORM2 = 9.275837550078808
A6_COND = 5.27836307072968

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
        assert max_abs_diff(r["L"], HILB_L) < 1e-13
        assert "pivot 2" in fail("cholesky", "1 2\n2 1")
        assert "symmetric" in fail("cholesky", "1 2\n3 1")

        # Rank and bases on a 5x5 rank-3 integer matrix.
        r = call("rank", A5)
        assert r["rank"] == 3 and r["nullity"] == 2, r
        N, Q = r["nullBasis"], r["columnBasis"]
        assert frob(matmul(A5, N)) / frob(A5) < 1e-12
        assert max_abs_diff(matmul(transpose(N), N), identity(2)) < 1e-12
        assert max_abs_diff(matmul(transpose(Q), Q), identity(3)) < 1e-12
        # The column-space projector must leave A unchanged.
        assert max_abs_diff(matmul(matmul(Q, transpose(Q)), A5), A5) < 1e-10
        assert max(abs(a - b) for a, b in zip(r["singularValues"], A5_SV)) < 1e-10
        r = call("rank", "1 2 3\n2 4 6\n1 1 1")
        n = [row[0] for row in r["nullBasis"]]
        assert r["rank"] == 2 and abs(abs(n[0] - 2 * n[1] + n[2]) / 6 ** 0.5 - 1) < 1e-12, r

        # Determinant of a 6x6 integer matrix needing pivoting: exact integer reference.
        A6 = [[0, 2, 1, 0, 3, 1], [1, 0, 4, 2, 0, 1], [3, 1, 0, 1, 2, 0],
              [2, 5, 1, 0, 1, 4], [1, 1, 1, 3, 0, 2], [0, 4, 2, 1, 1, 0]]
        r = call("determinant", A6)
        assert abs(r["det"] - (-1693)) <= 1e-10 * 1693, r["det"]
        assert r["trace"] == sum(A6[i][i] for i in range(6)) and r["residual"] < 1e-14
        r = call("charpoly", [[2, 1], [1, 2]])
        assert r["coefficients"] == [1, -4, 3], r
        r = call("charpoly", A6)
        exact = [1, 0, -38, -189, -502, -1236, -1693]
        assert all(abs(a - b) <= 1e-9 * max(1, abs(b)) + 1e-8 for a, b in zip(r["coefficients"], exact)), r["coefficients"]
        r = call("norms", "3 0 0\n0 -5 0\n0 0 1")
        assert abs(r["two"] - 5) < 1e-13 and r["one"] == 5 and r["infinity"] == 5 and abs(r["condition2"] - 5) < 1e-12
        r = call("norms", A6)
        assert abs(r["two"] - A6_NORM2) < 1e-12 and abs(r["condition2"] - A6_COND) < 1e-9 * A6_COND

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
