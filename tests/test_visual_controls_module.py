"""Offline table-zoom module parity and accessible percentage regression."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VisualControlsModuleTests(unittest.TestCase):
    def test_standalone_bundle_and_rebuild_registration(self):
        source = (ROOT / "src/visual-controls.js").read_text(encoding="utf-8").rstrip("\n")
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        marker = '<script id="promath-visual-controls">\n'
        self.assertEqual(html.count(marker), 1)
        bundled = html.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(bundled, source)
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-visual-controls", "src/visual-controls.js")', build)

    def test_zoom_percent_is_accessible_and_clamped(self):
        source = (ROOT / "src/visual-controls.js").read_text(encoding="utf-8")
        self.assertIn("slider.setAttribute('aria-valuetext',v+'%')", source)
        self.assertIn("Math.max(50,Math.min(200,Number(value)||100))", source)
        self.assertIn("window.MathStudio.tableZoom={value:", source)


if __name__ == "__main__":
    unittest.main()
