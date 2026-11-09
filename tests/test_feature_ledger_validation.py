"""Historical feature ledger validation must not be disabled by Python -O."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_feature_ledger.py"
LEDGER = ROOT / "docs" / "feature-ledger-audit-20261026.json"

spec = importlib.util.spec_from_file_location("feature_ledger_validator", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


class FrozenFeatureLedgerValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = json.loads(LEDGER.read_text(encoding="utf-8"))

    def test_historical_inventory_is_accepted(self):
        counts = validator.validate(self.original)
        self.assertEqual((counts["existing"], counts["gap"]), (158, 166))

    def test_invalid_frozen_data_is_rejected(self):
        cases = [
            ("wrong schema", lambda d: d.update(schemaVersion=2)),
            ("wrong count", lambda d: d["counts"].update(gaps=165)),
            ("duplicate id", lambda d: d["items"][1].update(id=d["items"][0]["id"])),
            ("missing scope", lambda d: d["items"][0].update(scope="")),
            ("invalid kind", lambda d: d["items"][0].update(kind="unknown")),
            ("wrong source", lambda d: d["items"][0].update(source="unverified.md")),
            ("unhashable id", lambda d: d["items"][0].update(id=["not-an-id"])),
            ("unhashable kind", lambda d: d["items"][0].update(kind={"bad": "kind"})),
            ("unhashable status", lambda d: d["items"][0].update(status=["partial"])),
            ("unhashable priority", lambda d: d["items"][158].update(priority=["P0"])),
            ("boolean schema", lambda d: d.update(schemaVersion=True)),
        ]
        for label, mutate in cases:
            with self.subTest(label=label):
                changed = copy.deepcopy(self.original)
                mutate(changed)
                with self.assertRaises(ValueError):
                    validator.validate(changed)

    def test_duplicate_json_keys_are_rejected_before_validation(self):
        # json.loads normally silently accepts the final duplicate key.
        cases = [
            '{"schemaVersion":1,"schemaVersion":2}',
            '{"items":[{"id":"first","id":"shadow"}]}',
            '{"counts":{"gaps":166,"gaps":165}}',
        ]
        for content in cases:
            with self.subTest(content=content):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(content, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Duplicate feature ledger JSON key"):
                        validator.load_ledger(path)

    def test_nonfinite_json_constants_are_rejected(self):
        # Python's JSON decoder accepts these non-standard constants by default.
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text('{"counts":{"gaps":' + token + '}}', encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Non-finite feature ledger JSON constant"):
                        validator.load_ledger(path)

    def test_optimized_python_still_rejects_corruption(self):
        # Under -O, the former assert-based validator silently accepted invalid data.
        script = (
            "import json,sys;"
            "sys.path.insert(0,sys.argv[1]);"
            "from validate_feature_ledger import validate;"
            "data=json.load(open(sys.argv[2],encoding='utf-8'));"
            "data['counts']['gaps']=165;"
            "validate(data)"
        )
        result = subprocess.run(
            [sys.executable, "-O", "-c", script, str(SCRIPT.parent), str(LEDGER)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Frozen feature counts mismatch", result.stderr)


if __name__ == "__main__":
    unittest.main()
