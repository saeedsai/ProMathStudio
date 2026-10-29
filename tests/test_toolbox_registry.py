"""Regression tests for deterministic, planning-only toolbox catalog registry."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_toolbox_registry.py"
SPEC = importlib.util.spec_from_file_location("build_toolbox_registry", SCRIPT)
registry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(registry)


class ToolboxRegistryTests(unittest.TestCase):
    def test_stable_catalog_scoped_ids(self):
        a = registry.feature_id("control", "Step response")
        self.assertEqual(a, registry.feature_id("control", "Step response"))
        self.assertNotEqual(a, registry.feature_id("signals", "Step response"))
        self.assertTrue(a.startswith("catalog:control:step-response-"))

    def test_normalized_titles(self):
        self.assertEqual(registry.normalized_title(" **Root-Locus** "), "root locus")
        self.assertEqual(registry.normalized_title("FFT / Spectrum"), "fft spectrum")

    def test_table_parser_ignores_headers_and_counts(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "catalog.md").write_text(
                "# Sample\n## Group A\n| Feature | Description |\n"
                "|---|---|\n| FFT | Frequency transform |\n"
                "| FFT | Frequency transform |\n| Total | 10 |\n"
                "## Group B\n| Feature | Description |\n"
                "| Matrix solver | Linear systems |\n", encoding="utf-8"
            )
            with patch.object(registry, "DOCS", folder):
                result = registry.parse_catalog("sample", "catalog.md")
        self.assertEqual([item["title"] for item in result], ["FFT", "Matrix solver"])
        self.assertEqual(result[0]["section"], "Group A")
        self.assertEqual(result[1]["section"], "Group B")
        self.assertTrue(all(item["status"] == "planned-unverified" for item in result))

    def test_escaped_markdown_pipe_preserves_description(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "catalog.md").write_text(
                "| Feature | Description |\n|---|---|\n"
                "| Filter | Accept A \\| B without splitting the cell |\n",
                encoding="utf-8",
            )
            with patch.object(registry, "DOCS", folder):
                entries = registry.parse_catalog("sample", "catalog.md")
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["title"], "Filter")
        self.assertEqual(entries[0]["description"], "Accept A | B without splitting the cell")

    def test_alignment_delimiters_are_not_catalog_features(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "catalog.md").write_text(
                "| Feature | Description |\n"
                "| :--- | ---: |\n"
                "| :-----: | :------: |\n"
                "| FFT | Transform samples |\n",
                encoding="utf-8",
            )
            with patch.object(registry, "DOCS", folder):
                entries = registry.parse_catalog("sample", "catalog.md")
        self.assertEqual([item["title"] for item in entries], ["FFT"])

    def test_catalogs_are_present_and_registry_deterministic(self):
        for filename in registry.CATALOGS.values():
            self.assertTrue((registry.DOCS / filename).is_file(), filename)
        first = registry.build()
        second = registry.build()
        self.assertEqual(first, second)
        self.assertEqual(first["catalogCount"], len(registry.CATALOGS))
        self.assertEqual(first["entryCount"], len(first["entries"]))
        self.assertEqual(first["candidateAliasGroupCount"], len(first["aliasCandidates"]))
        ids = [item["id"] for item in first["entries"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(item["status"] == "planned-unverified" for item in first["entries"]))
        for candidate in first["aliasCandidates"]:
            self.assertGreater(len(candidate["ids"]), 1)
            self.assertEqual(candidate["ids"], sorted(candidate["ids"]))


if __name__ == "__main__":
    unittest.main()
