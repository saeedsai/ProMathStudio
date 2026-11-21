"""docs/USER_GUIDE.md must exist, be linked from README and mention every tool panel and catalog tool.

The scan is deliberately simple: any `id="...-details"`, `id='...-details'` or `id:'...-details'`
literal in src/*.js counts as a tool panel, and every catalog row id in src/engineering-catalog.js
counts as a tool. Adding a panel or catalog entry without documenting it fails this test.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "USER_GUIDE.md"
PANEL_ID = re.compile(r"""\bid\s*[=:]\s*["']([a-z][a-z0-9-]*-details)["']""")
# Catalog tool ids are dotted (for example matrix.solve.real.small); discipline ids are not.
CATALOG_ROW = re.compile(r"""^\s*\['([a-z][a-z0-9-]*(?:\.[a-z0-9-]+)+)','""", re.MULTILINE)
# Matches of the pattern that are not tool panels.
NOT_PANELS = {
    "ui-details",  # Options -> "Advanced explanations" checkbox, not a <details> panel.
}
# Panels that do not end in "-details" but are user-facing tools, plus workspace task targets.
EXTRA_IDS = (
    "matrix-tools", "control-theory-toolbox", "ct-equilibrium", "ct-eq-transient",
    "complex-graph-workbench", "graph-data-panel", "graph-appearance", "dt-code-library",
    "dt-advanced", "eng-visuals", "calc-variable-panel", "ui-calc-settings", "ui-calc-history",
    "ui-solver-assumptions", "ui-graph-axes", "ui-graph-table", "ui-editor-python",
)


def panel_ids():
    found = set()
    for path in sorted((ROOT / "src").glob("*.js")):
        found.update(PANEL_ID.findall(path.read_text(encoding="utf-8")))
    return found - NOT_PANELS


def catalog_ids():
    return set(CATALOG_ROW.findall((ROOT / "src" / "engineering-catalog.js").read_text(encoding="utf-8")))


def visual_tool_ids():
    source = (ROOT / "src" / "engineering-visuals.js").read_text(encoding="utf-8")
    return set(re.findall(r"""\{id:'[a-z]+',tool:'([a-z][a-z0-9.-]+)'""", source))


class UserGuideTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.guide = GUIDE.read_text(encoding="utf-8")

    def test_guide_exists_and_is_linked_from_readme(self):
        self.assertTrue(GUIDE.is_file())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertRegex(readme, r"\]\(docs/USER_GUIDE\.md(#[a-z0-9-]+)?\)")
        for heading in ("## Getting started", "## Keyboard and accessibility"):
            self.assertIn(heading, self.guide)

    def test_scanner_finds_known_panels(self):
        ids = panel_ids()
        # Sanity floor and known members guard against a regex that silently matches nothing.
        self.assertGreaterEqual(len(ids), 20, ids)
        for known in ("brent-details", "num-details", "matrix-extras-details", "xlsx-import-details"):
            self.assertIn(known, ids)
        self.assertNotIn("ui-details", ids)
        self.assertGreaterEqual(len(catalog_ids()), 25)

    def test_every_details_panel_is_documented(self):
        missing = sorted(i for i in panel_ids() | set(EXTRA_IDS) if f"`{i}`" not in self.guide)
        self.assertEqual(missing, [], "panels missing from docs/USER_GUIDE.md: " + ", ".join(missing))

    def test_every_catalog_tool_is_documented(self):
        ids = catalog_ids() | visual_tool_ids()
        missing = sorted(i for i in ids if f"`{i}`" not in self.guide)
        self.assertEqual(missing, [], "catalog tools missing from docs/USER_GUIDE.md: " + ", ".join(missing))

    def test_workspace_tasks_are_documented(self):
        source = (ROOT / "src" / "workspace-tasks.js").read_text(encoding="utf-8")
        labels = re.findall(r"""\['[a-z]+','([^']+)','[^']*'(?:,'[^']*')?\]""", source)
        self.assertGreaterEqual(len(labels), 15, labels)
        missing = sorted(label for label in labels if label not in self.guide)
        self.assertEqual(missing, [], "workspace tasks missing from docs/USER_GUIDE.md: " + ", ".join(missing))

    def test_cited_tests_exist(self):
        cited = set(re.findall(r"`tests/([a-z0-9_]+\.py)`", self.guide))
        self.assertGreaterEqual(len(cited), 30)
        missing = sorted(name for name in cited if not (ROOT / "tests" / name).is_file())
        self.assertEqual(missing, [], "guide cites nonexistent tests: " + ", ".join(missing))

    def test_undocumented_panel_is_detected(self):
        # Negative control: the same membership rule flags an id that the guide does not mention.
        self.assertNotIn("`no-such-tool-details`", self.guide)
        self.assertEqual(PANEL_ID.findall("area.id='no-such-tool-details';"), ["no-such-tool-details"])


if __name__ == "__main__":
    unittest.main()
