"""Static contract for the multiple/discrete integration module: registration, parity and safety."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "integration-tools.js"


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


class IntegrationToolsTests(unittest.TestCase):
    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_registered_in_build_after_interpolation(self):
        build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
        interp = build.index('("promath-interpolation-tools", "src/interpolation-tools.js"),')
        integ = build.index('("promath-integration-tools", "src/integration-tools.js"),')
        self.assertLess(interp, integ)
        self.assertLess(self.html.index('<script id="promath-interpolation-tools">'),
                        self.html.index('<script id="promath-integration-tools">'))

    def test_bundle_matches_source(self):
        self.assertEqual(embedded(self.html, "promath-integration-tools").rstrip("\n"), self.src.rstrip("\n"))

    def test_no_dynamic_code_network_or_markup_breakers(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"import\s*\("):
            self.assertIsNone(re.search(pattern, self.src), pattern)
        for token in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(token, self.src.lower())
        # Expressions are only evaluated by the shared safe numerical evaluator.
        self.assertIn("M.numerical.evaluate(", self.src)
        # innerHTML only receives the static template (no concatenated user values).
        self.assertEqual(self.src.count(".innerHTML="), 1)

    def test_public_api_and_accessible_ui(self):
        self.assertIn("M.integration={double,triple,discrete,discreteFromTable", self.src)
        self.assertIn("details');area.id='integration-details'", self.src)
        self.assertIn('id="int-output" role="status" aria-live="polite"', self.src)
        self.assertIn("G7-K15", self.src)
        self.assertIn("not a certified bound", self.src)

    def test_quality_workflow_runs_browser_smoke(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_integration_tools.py", workflow)


if __name__ == "__main__":
    unittest.main()
