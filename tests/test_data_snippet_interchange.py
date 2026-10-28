"""Static invariants for versioned Data Tables snippet JSON interchange."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
QUALITY = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class DataSnippetInterchangeTests(unittest.TestCase):
    def test_bundle_parity(self):
        self.assertIn(SOURCE, HTML)

    def test_versioned_data_only_schema_and_bounds(self):
        for token in (
            "SNIPPET_FILE_FORMAT='promathstudio-snippets'",
            "SNIPPET_FILE_VERSION=1",
            "MAX_SNIPPET_FILE_BYTES=400000",
            "payload.snippets.length>40",
            "entry.name.length>60",
            "entry.sample.length>8000",
            "Duplicate snippet names in import.",
            "Name conflict:",
            "Maximum 40 saved snippets",
        ):
            with self.subTest(token=token):
                self.assertIn(token, SOURCE)

    def test_import_transaction_and_no_code_execution(self):
        segment = SOURCE.split("// Versioned, data-only interchange.", 1)[1].split(
            "$('dt-snippet-save').addEventListener", 1
        )[0]
        self.assertIn("persistDataSnippets(plan.next)", segment)
        self.assertIn("snapshot!==JSON.stringify(customDataSnippets)", segment)
        self.assertIn("plan.conflicts.length&&!snippetSkipConflicts.checked", segment)
        self.assertIn("renderDataLibrary()", segment)
        self.assertNotIn("eval(", segment)
        self.assertNotIn("new Function(", segment)
        self.assertNotIn("dt-python-run", segment)
        self.assertIn("JSON.parse(await file.text())", segment)
        self.assertIn("event.target.value=''", segment)

    def test_browser_regression_is_mandatory(self):
        self.assertIn("python tests/smoke_data_snippet_interchange.py", QUALITY)


if __name__ == "__main__":
    unittest.main()
