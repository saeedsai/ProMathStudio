"""Regression coverage for Quality smoke registration and stale/duplicate paths."""
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_quality_tests as audit


class QualityAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'tests').mkdir()
        (self.root / 'tests' / 'smoke_alpha.py').write_text('pass\n')
        (self.root / 'tests' / 'smoke_beta.py').write_text('pass\n')
        (self.root / 'tests' / 'test_math.py').write_text('pass\n')
        self.workflow = """jobs:
  check:
    steps:
      - name: Structural tests
        run: python -m unittest discover -s tests -p 'test_*.py' -v
      - name: A
        run: python tests/smoke_alpha.py
      - name: B
        run: python tests/smoke_beta.py
"""

    def test_valid_smokes_and_discovery(self):
        summary = audit.audit(self.root, self.workflow)
        self.assertEqual(summary['smoke_registered'], 2)
        self.assertEqual(summary['direct_test_commands'], 2)
        self.assertTrue(summary['python_unittest_discovery'])

    def test_nonverbose_discovery_remains_valid(self):
        self.assertTrue(audit.audit(self.root, self.workflow.replace("'test_*.py' -v", "'test_*.py'"))['python_unittest_discovery'])

    def test_long_verbose_discovery_valid(self):
        self.assertTrue(audit.audit(self.root, self.workflow.replace(' -v\n', ' --verbose\n'))['python_unittest_discovery'])

    def test_missing_referenced_file(self):
        (self.root / 'tests' / 'smoke_beta.py').unlink()
        with self.assertRaisesRegex(ValueError, 'missing files referenced by Quality'):
            audit.audit(self.root, self.workflow)

    def test_unregistered_smoke_file(self):
        (self.root / 'tests' / 'smoke_gamma.py').write_text('pass\n')
        with self.assertRaisesRegex(ValueError, 'unregistered smoke files: tests/smoke_gamma.py'):
            audit.audit(self.root, self.workflow)

    def test_duplicate_ci_run(self):
        with self.assertRaisesRegex(ValueError, 'duplicate test runs: tests/smoke_alpha.py'):
            audit.audit(self.root, self.workflow + '        run: python tests/smoke_alpha.py\n')

    def test_removed_python_unittest_discovery(self):
        with self.assertRaisesRegex(ValueError, 'unittest discovery step is missing'):
            audit.audit(self.root, self.workflow.replace('python -m unittest discover', 'python -m unittest test_math'))

    def test_missing_js_test_reference(self):
        with self.assertRaisesRegex(ValueError, 'missing files referenced by Quality: tests/test_truss.js'):
            audit.audit(self.root, self.workflow + '        run: node --test tests/test_truss.js\n')

    def test_unregistered_still_fails_if_many_runs_exist(self):
        (self.root / 'tests' / 'smoke_gamma.py').write_text('pass\n')
        with self.assertRaisesRegex(ValueError, 'unregistered smoke files'):
            audit.audit(self.root, self.workflow + '        run: node --test tests/test_math.js\n')


if __name__ == '__main__':
    unittest.main()
