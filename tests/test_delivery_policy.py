"""Delivery-policy regression: preserve dev/main discipline and complete quality gates.

Tests document source-controlled workflow rules, not GitHub admin settings,
which must be verified separately. These checks cannot substitute for Actions.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DeliveryPolicyTests(unittest.TestCase):
    def test_durable_agent_contract_and_five_feature_plan(self):
        agent = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        plan = (ROOT / "docs/HOURLY_DEVELOPMENT_PLAN.md").read_text(encoding="utf-8")
        for required in ("dev", "main", "next five", "regression", "Pages",
                         "security", "PR", "CI", "CD"):
            self.assertIn(required.lower(), agent.lower(), required)
        self.assertIn("Next five features", plan)
        for feature_id in ("P0-SYMBOLIC-SYSTEMS", "P0-MATRIX-UI",
                           "P0-NUMERIC-ODE", "P0-CUSTOM-PY-COMPOSE",
                           "P0-SHEET-REFERENCE"):
            self.assertIn(feature_id, plan)

    def test_quality_checks_dev_and_main_with_regressions(self):
        workflow = (ROOT / ".github/workflows/quality.yml").read_text()
        self.assertIn("branches: [dev, main]", workflow)
        self.assertIn("pull_request:", workflow)
        for script in ("smoke_browser.py", "smoke_graph_import.py",
                       "smoke_data_tables.py", "smoke_advanced_math.py",
                       "smoke_numerical_data.py", "smoke_context_actions.py",
                       "smoke_visual_options.py"):
            self.assertIn(script, workflow)
        self.assertIn("unittest discover", workflow)

    def test_cleanup_never_deletes_unmerged_or_permanent_refs(self):
        workflow = (ROOT / ".github/workflows/branch-hygiene.yml").read_text()
        self.assertIn("branches: [main]", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertIn("new Set(['main','dev'])", workflow)
        self.assertIn("branch.protected", workflow)
        self.assertIn("inOpenPR.has", workflow)
        self.assertIn("compareCommits", workflow)
        self.assertIn("['ahead','identical']", workflow)
        self.assertIn("deleteRef", workflow)

    def test_data_tables_guide_has_single_structure_and_current_sort_contract(self):
        guide = (ROOT / "docs/DATA_TABLES.md").read_text(encoding="utf-8")
        self.assertEqual(guide.count("# Data Tables workspace"), 1)
        for heading in ("## Workbooks", "## Relational operations",
                        "## Import and export", "## Persistence and privacy"):
            self.assertEqual(guide.count(heading), 1, heading)
        self.assertIn("sort is rejected atomically", guide)
        self.assertNotIn("Sorting/reordering rows with formulas is **not** yet reference-safe", guide)

if __name__ == "__main__":
    unittest.main()
