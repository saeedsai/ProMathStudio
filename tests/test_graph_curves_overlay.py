"""Main-graph curve overlays: renderer hook, project persistence, schema validation and CI."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
SOURCE = (ROOT / "src" / "graph-curves.js").read_text(encoding="utf-8")
SCHEMA = (ROOT / "src" / "project-schema.js").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")


def embedded(tag):
    marker = '<script id="%s">\n' % tag
    return HTML.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")


class GraphCurvesOverlayTest(unittest.TestCase):
    def test_bundles_match_sources(self):
        self.assertEqual(embedded("promath-graph-curves"), SOURCE.rstrip("\n"))
        self.assertEqual(embedded("promath-project-schema"), SCHEMA.rstrip("\n"))

    def test_overlay_api_is_public(self):
        self.assertIn("M.graphOverlays=overlayApi", SOURCE)
        for name in ("add(def)", "clear(redraw=true)", "draw:drawOverlays", "exportState:", "restoreState(list)",
                     "rendered:", "legend:", "hasOverlays:"):
            with self.subTest(name=name):
                self.assertIn(name, SOURCE)

    def test_renderer_hook_is_minimal_and_2d(self):
        self.assertEqual(HTML.count("window.MathStudio.graphOverlays?.draw(ctx,{mode:'2d',range,w,h})"), 1)
        draw2d = HTML.split("  function draw2D(){", 1)[1].split("  function persp(", 1)[0]
        self.assertIn("graphOverlays?.draw", draw2d)
        self.assertIn("if(!props||props.mode!=='2d')", SOURCE)

    def test_graph_state_persists_definitions(self):
        self.assertIn("curves:window.MathStudio.graphOverlays?.exportState()||[]", HTML)
        self.assertIn("window.MathStudio.graphOverlays?.restoreState(data.curves??null);", HTML)
        # Overlays are restored before the redraw, after the dataset.
        restore = HTML.split("restoreGraphState:data=>{", 1)[1].split("\n    }\n", 1)[0]
        self.assertLess(restore.index("graphOverlays?.restoreState"), restore.index("plot();"))

    def test_polylines_break_and_implicit_follows_view(self):
        self.assertIn("ctx.moveTo(X,Y);else ctx.lineTo(X,Y)", SOURCE)
        self.assertIn("entry.cacheKey!==key", SOURCE)
        self.assertIn("implicit(entry.def.expression,{xmin:range.xmin", SOURCE)

    def test_schema_validates_overlays_before_restore(self):
        for fragment in ("data.graph?.curves", "curves.length > 8", "graph curve overlay type is invalid.",
                         "graph curve overlay fields are invalid.", "duplicate graph curve overlays.",
                         "value >= 4 && value <= 300", "value >= 2 && value <= 20000", "Math.abs(value) <= 1e12"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SCHEMA)

    def test_restore_is_atomic(self):
        restore = SOURCE.split(" restoreState(list){", 1)[1].split("\n },", 1)[0]
        self.assertLess(restore.index("const next=list.map"), restore.index("overlays=next"))

    def test_accessible_controls(self):
        for fragment in ('id="curves-overlay" type="button"', 'id="curves-overlay-clear" type="button"',
                         'id="curves-overlay-status" class="small-note" role="status" aria-live="polite"',
                         'aria-describedby="curves-overlay-status"', "#curves-details .curves-actions button{min-height:42px}"):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, SOURCE)

    def test_no_dynamic_code(self):
        for banned in ("eval(", "new Function", "fetch(", "<!--", "-->", "<script", "</script"):
            with self.subTest(banned=banned):
                self.assertNotIn(banned, SOURCE)
                self.assertNotIn(banned, SCHEMA)
        self.assertEqual(SOURCE.count("innerHTML="), 1)

    def test_workflow_registers_smoke_last(self):
        self.assertTrue((ROOT / "tests" / "smoke_graph_curves_overlay.py").is_file())
        self.assertTrue(WORKFLOW.rstrip().endswith("run: python tests/smoke_graph_curves_overlay.py"))


if __name__ == "__main__":
    unittest.main()
