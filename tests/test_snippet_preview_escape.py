"""Regression: Escape dismisses snippet preview without applying an import."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=(ROOT/"src/data-tables.js").read_text(encoding="utf-8")
HTML=(ROOT/"index.html").read_text(encoding="utf-8")
class SnippetPreviewEscapeTests(unittest.TestCase):
    def test_keyboard_cancel_has_no_storage_mutation(self):
        start=SOURCE.index("snippetPreview.addEventListener('keydown'")
        end=SOURCE.index("snippetSkipConflicts.addEventListener('change'",start)
        handler=SOURCE[start:end]
        self.assertIn("event.key!=='Escape'||snippetPreview.hidden",handler)
        self.assertIn("event.preventDefault();closeSnippetPreview();",handler)
        self.assertIn("$('dt-snippet-import').focus();",handler)
        self.assertNotIn("persistDataSnippets(",handler)
    def test_preview_is_focusable_and_receives_focus_on_open(self):
        self.assertIn('id="dt-snippet-preview" hidden tabindex="-1" role="group"', SOURCE)
        self.assertIn('snippetPreview.hidden=false;\\n      snippetPreview.focus();', SOURCE)

    def test_standalone_matches_module(self):
        start=HTML.index("/* ProMathStudio Data Tables workspace.")
        end=HTML.index("</script>",start)
        self.assertEqual(HTML[start:end],SOURCE)
if __name__=="__main__":
    unittest.main()
