"""Regression: mobile workspace navigation must fit the viewport without horizontal scroll."""
from pathlib import Path
import re
import unittest

HTML = (Path(__file__).resolve().parents[1] / "index.html").read_text(encoding="utf-8")

class MobileWorkspaceGridTests(unittest.TestCase):
    def test_mobile_navigation_uses_two_equal_minmax_columns(self):
        css = HTML.split('<style id="promath-computational-redesign">', 1)[1].split('</style>', 1)[0]
        mobile = css.split('@media(max-width:760px)', 1)[1].split('@media(max-width:440px)', 1)[0]
        self.assertRegex(mobile, r'\.workspace-bar\s*\{[^}]*display:grid;[^}]*grid-template-columns:repeat\(2,minmax\(0,1fr\)\)')
        self.assertRegex(mobile, r'\.workspace-tab\s*\{[^}]*width:100%;min-width:0;')
        self.assertNotIn('overflow-x:auto', mobile)
        self.assertNotIn('flex:0 0 auto', mobile)

    def test_accessible_tabs_and_focus_navigation_preserved(self):
        self.assertIn('role="navigation" aria-label="Math Studio tools"', HTML)
        for name in ('calculator', 'editor', 'graph'):
            self.assertIn('data-workspace="'+name+'"', HTML)
        self.assertIn("event.key==='ArrowRight'", HTML)
        self.assertIn("event.key==='ArrowLeft'", HTML)
        self.assertIn("event.key==='Home'", HTML)
        self.assertIn("event.key==='End'", HTML)
        self.assertIn('.workspace-tab:focus-visible', HTML)

if __name__ == '__main__':
    unittest.main()
