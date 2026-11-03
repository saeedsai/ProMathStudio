"""Static contract for cubic spline and Akima interpolation: parity, API, UI options, safety and CI wiring."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "interpolation-tools.js"
SPLINES = ("natural", "clamped", "notaknot", "periodic", "akima", "makima")


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


class InterpolationSplineTests(unittest.TestCase):
    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_bundle_matches_source(self):
        self.assertEqual(embedded(self.html, "promath-interpolation-tools").rstrip("\n"), self.src.rstrip("\n"))

    def test_methods_registered_in_select_and_api(self):
        for method in SPLINES:
            self.assertIn(f'<option value="{method}">', self.src)
            self.assertRegex(self.src, rf"\b{method}:\{{min:\d")
        for existing in ("linear", "pchip", "barycentric"):
            self.assertIn(f'<option value="{existing}">', self.src)
        self.assertIn("methods:METHODS.slice(),splineMethods:Object.keys(SPLINE_METHODS)", self.src)
        self.assertIn("M.interpolationTools={interpolate,parsePairs,parseQueries,", self.src)

    def test_minimum_points_and_solvers(self):
        self.assertIn("notaknot:{min:4", self.src)
        self.assertIn("periodic:{min:3", self.src)
        self.assertIn("akima:{min:3", self.src)
        self.assertIn("function thomas(sub,diag,sup,rhs)", self.src)
        self.assertIn("function cyclicThomas(sub,diag,sup,rhs)", self.src)
        self.assertIn("function hermiteIntegral(", self.src)
        # Spline evaluation keeps the module-wide extrapolation refusal.
        self.assertGreaterEqual(self.src.count("extrapolation is disabled."), 2)

    def test_clamped_slope_inputs_are_labelled(self):
        for ident in ("interp-slope-start", "interp-slope-end"):
            self.assertRegex(self.src, rf'id="{ident}"[^>]*aria-label="')
        self.assertIn("#interp-slopes[hidden]{display:none}", self.src)

    def test_no_dynamic_code_network_or_markup_breakers(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"import\s*\("):
            self.assertIsNone(re.search(pattern, self.src), pattern)
        for token in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(token, self.src.lower())
        self.assertEqual(self.src.count(".innerHTML="), 1)

    def test_workflow_runs_spline_smoke_last(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertTrue(workflow.rstrip().endswith("run: python tests/smoke_interpolation_splines.py"))
        for smoke in ("linear", "pchip", "barycentric"):
            self.assertIn(f"python tests/smoke_interpolation_{smoke}.py", workflow)


if __name__ == "__main__":
    unittest.main()
