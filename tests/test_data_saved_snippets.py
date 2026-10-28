"""Regression checks for Data Tables saved snippets."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/"src/data-tables.js").read_text(encoding="utf-8")
HTML=(ROOT/"index.html").read_text(encoding="utf-8")

class DataSavedSnippetsTest(unittest.TestCase):
    def test_standalone_bundle_matches_module(self):
        self.assertIn(SOURCE,HTML)
    def test_bounded_storage_and_safe_catalog(self):
        for expected in ("promathstudio-data-snippets-v1","stored.filter(","slice(0,40)","sample.length<=8000","customDataSnippets.length>=40","localStorage.setItem(snippetStorageKey","dataLibrary.concat(customDataSnippets)"):
            self.assertIn(expected,SOURCE)
    def test_no_automatic_python_execution(self):
        block=SOURCE.split("const snippetStorageKey=",1)[1].split("// Store the logical cell coordinates:",1)[0]
        self.assertNotIn("eval(",block)
        self.assertNotIn("new Function(",block)
        self.assertNotIn("dt-python-run",block)
    def test_formula_validation_and_user_feedback(self):
        self.assertIn("kind==='Formula'&&!sample.startsWith('=')",SOURCE)
        self.assertIn("Storage unavailable; snippet was not saved.",SOURCE)

if __name__=="__main__":
    unittest.main()
