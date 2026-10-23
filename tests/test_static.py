"""Dependency-free structural regression checks for ProMathStudio."""
from pathlib import Path
import ast
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'


class StaticChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = HTML.read_text(encoding='utf-8')

    def test_html_document_is_present(self):
        self.assertIn('<!DOCTYPE html>', self.text)
        self.assertIn('</html>', self.text)
        self.assertIn('<title>', self.text)

    def test_every_workspace_and_shared_hub_is_present(self):
        for section in ['calculator', 'editor', 'solver', 'graph']:
            with self.subTest(section=section):
                self.assertRegex(self.text, rf'data-workspace="{section}"')
        for identifier in ['connected-hub', 'hub-expression', 'hub-export-project',
                           'hub-import-project', 'calc-input', 'cas-operation',
                           'cas-engine', 'graph-input', 'graph-canvas',
                           'equation-input', 'preview', 'notebook']:
            with self.subTest(element=identifier):
                self.assertIn(f'id="{identifier}"', self.text)

    def test_connected_hub_is_footer_after_workspace_content(self):
        # Keep a single shared panel below every workspace, not a top toolbar.
        self.assertEqual(self.text.count('id="connected-hub"'), 1)
        self.assertGreater(self.text.index('id="connected-hub"'),
                           self.text.index('id="examples-list"'))
        self.assertLess(self.text.index('id="connected-hub"'),
                        self.text.index('  </main>'))

    def test_routing_exists(self):
        for target in ['editor', 'calculator', 'solver', 'graph2d', 'graph3d', 'notebook']:
            self.assertIn(f'data-hub-to="{target}"', self.text)

    def test_sympy_is_ast_based_and_has_guards(self):
        self.assertIn('MS_MAX_NODES', self.text)
        self.assertIn('MS_MAX_RESULTS', self.text)
        self.assertIn('function sympyJob(', self.text)
        m = re.search(r'<script id="mathstudio-sympy-python" type="text/plain">(.*?)</script>',
                      self.text, re.S)
        self.assertIsNotNone(m)
        ast.parse(m.group(1))  # Parses embedded Python without requiring SymPy.

    def test_exports_and_backups(self):
        for identifier in ['copy-word', 'export-word', 'export-all-word', 'export-btn',
                           'cas-word', 'graph-save', 'hub-project-file']:
            self.assertIn(f'id="{identifier}"', self.text)
        self.assertIn("format:'mathstudio-project'", self.text)


if __name__ == '__main__':
    unittest.main()
