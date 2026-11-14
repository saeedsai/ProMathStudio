"""Global tool search module: source/bundle parity, safety, load order, ARIA and CI registration."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/tool-search.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


class ToolSearchModuleTests(unittest.TestCase):
    def test_bundle_parity_and_last_module(self):
        marker = '<script id="promath-tool-search">\n'
        self.assertEqual(HTML.count(marker), 1)
        bundled = HTML.split(marker, 1)[1].split("</script>", 1)[0].rstrip("\n")
        self.assertEqual(SOURCE.rstrip("\n"), bundled)
        # Loads after every module whose panels or catalog entries it indexes.
        position = HTML.index(marker)
        for tag in ("promath-workspace-tasks", "promath-engineering-catalog", "promath-engineering-visuals"):
            self.assertLess(HTML.index('<script id="' + tag + '">'), position)
        self.assertEqual(re.findall(r'<script id="([^"]+)">', HTML)[-1], "promath-tool-search")
        build = (ROOT / "scripts/build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-tool-search", "src/tool-search.js"),\n]', build)

    def test_safety(self):
        for forbidden in ("eval(", "new Function(", "innerHTML", "fetch(", "XMLHttpRequest", "<!--", "-->", "<script", "</script", "localStorage"):
            self.assertNotIn(forbidden, SOURCE)

    def test_combobox_aria_and_public_api(self):
        for needle in ("'role','combobox'", "'aria-expanded'", "'aria-controls','tool-search-list'",
                       "'aria-activedescendant'", "'role','listbox'", "'role','option'", "'aria-live','polite'",
                       "'aria-disabled','true'", "textContent='Find a tool'", "Planned", "min-height:40px", "focus-visible"):
            self.assertIn(needle, SOURCE)
        self.assertIn("M.toolSearch=Object.freeze(", SOURCE)
        # Reuses public routing instead of duplicating tool implementations.
        self.assertIn("M.engineeringCatalog?.open?.(", SOURCE)
        self.assertIn("M.workspaceTasks?.list?.()", SOURCE)
        self.assertIn("M.advanced.mode(", SOURCE)
        catalog = (ROOT / "src/engineering-catalog.js").read_text(encoding="utf-8")
        self.assertIn("open:openById", catalog)
        tasks = (ROOT / "src/workspace-tasks.js").read_text(encoding="utf-8")
        self.assertIn("current:()=>activeMode,list}", tasks)

    def test_planned_click_does_not_activate_disabled_option(self):
        # Mouse clicks on unavailable catalog entries must not leave aria-selected
        # on a disabled option, even after keyboard navigation selected a valid tool.
        blocked = "if(item.status!=='available'){status.textContent=item.title+' is planned and not yet available.';return;}"
        self.assertIn(blocked, SOURCE)
        self.assertNotIn("setActive(n);return;}", SOURCE)
        self.assertIn(blocked, HTML)

    def test_home_end_navigation_skips_planned_results(self):
        self.assertIn("if(e.key==='Home'||e.key==='End')", SOURCE)
        self.assertIn("item.status==='available'?i:-1", SOURCE)
        self.assertIn("setActive(e.key==='Home'?available[0]:available[available.length-1])", SOURCE)
        self.assertIn("if(e.key==='Home'||e.key==='End')", HTML)

    def test_synonym_map_is_small_and_data_only(self):
        block = SOURCE.split("const SYNONYMS=Object.freeze({", 1)[1].split("});", 1)[0]
        self.assertNotIn("=>", block)
        self.assertLessEqual(block.count(":["), 40)
        for key in ("integral", "root", "units", "beam", "stats", "spline", "ode", "lp", "curve"):
            self.assertRegex(block, r"\b" + key + r":\[")

    def test_ci_registration_is_last_step(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8").rstrip()
        self.assertIn("run: python tests/smoke_tool_search.py", workflow)


if __name__ == "__main__":
    unittest.main()
