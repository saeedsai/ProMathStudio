"""Regression checks for the computation-first interface refresh."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")

class ComputationFirstUIRegression(unittest.TestCase):
    def test_redesign_is_present_once_and_before_body(self):
        self.assertEqual(HTML.count('id="promath-computational-redesign"'), 1)
        self.assertLess(HTML.index('id="promath-computational-redesign"'), HTML.index("</head>"))

    def test_workstations_and_action_hooks_remain(self):
        for hook in ('id="calculator-panel"', 'id="calc-input"', 'id="calc-execute"',
                     'id="calc-result-math"', 'id="palette-nav"', 'id="palette-search"',
                     'id="workspace-subtitle"', 'id="help-btn"'):
            with self.subTest(hook=hook):
                self.assertIn(hook, HTML)
        self.assertRegex(HTML, r'data-workspace="(editor|calculator|graph)"')

    def test_accessibility_responsive_and_reduced_motion(self):
        css = HTML.split('<style id="promath-computational-redesign">',1)[1].split("</style>",1)[0]
        for selector in ("@media(max-width:760px)", "@media(max-width:440px)",
                         "@media(prefers-reduced-motion:reduce)",
                         "focus-visible", ".workspace-tab", "#calc-input",
                         ".calc-result", ".preview", ".palette-nav"):
            with self.subTest(selector=selector):
                self.assertIn(selector, css)
        self.assertIn('aria-label="Math symbol palette"', HTML)
        self.assertIn('aria-label="Math Studio tools"', HTML)
        self.assertNotIn("!important!important",css)

if __name__ == "__main__":
    unittest.main()
