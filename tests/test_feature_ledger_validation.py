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

    def test_frozen_counts_reject_float_and_boolean_coercion(self):
        # Python considers 166.0 == 166 and True == 1; frozen counts
        # must remain explicitly integral rather than coercible.
        for key, value in (("gaps", 166.0), ("existing", 158.0),
                           ("gaps", True), ("existing", False)):
            with self.subTest(key=key, value=value):
                changed = copy.deepcopy(self.original)
                changed["counts"][key] = value
                with self.assertRaisesRegex(ValueError, "integer values"):
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

    def test_overflowed_json_float_is_rejected_at_any_depth(self):
        # 1e999 is syntactically JSON but Python float parsing yields infinity.
        for payload in ('{"extra":1e999}', '{"nested":[-1e999]}',
                        '{"counts":{"gaps":1e999}}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Non-finite feature ledger JSON number"):
                        validator.load_ledger(path)

    def test_underflowed_json_float_is_rejected_at_any_depth(self):
        for payload in ('{"extra":1e-999}', '{"nested":[-1e-999]}',
                        '{"extra":1e-324}', '{"nested":[-1e-324]}',
                        '{"counts":{"gaps":0.000e-999}}', '{"extra":0e-999}',
                        '{"extra":-0e-999}', '{"extra":0.000000e-999}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    if "0.000e-999" in payload or "0e-999" in payload:
                        decoded = validator.load_ledger(path)
                        value = decoded["counts"]["gaps"] if "counts" in decoded else decoded["extra"]
                        self.assertEqual(value, 0.0)
                    else:
                        with self.assertRaisesRegex(ValueError, "Underflowed feature ledger JSON number"):
                            validator.load_ledger(path)

    def test_unsafe_json_integers_are_rejected_at_any_depth(self):
        for payload in ('{"extra":9007199254740992}',
                        '{"nested":[-9007199254740992]}',
                        '{"counts":{"gaps":999999999999999999999}}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Unsafe feature ledger JSON integer"):
                        validator.load_ledger(path)

    def test_unsafe_integer_valued_json_floats_are_rejected(self):
        # Decimal/exponent syntax routes through parse_float, not parse_int.
        for payload in ('{"extra":9007199254740992.0}',
                        '{"nested":[-9007199254740992e0]}',
                        '{"counts":{"gaps":1e20}}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Unsafe feature ledger JSON floating integer"):
                        validator.load_ledger(path)

    def test_fractional_json_numbers_must_not_round_to_integers(self):
        # Binary64 silently rounds these non-integral decimal tokens to ints.
        for payload in ('{"extra":1.0000000000000001}',
                        '{"nested":[-2.0000000000000001]}',
                        '{"counts":{"gaps":9007199254740991.1}}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Rounded feature ledger JSON fraction"):
                        validator.load_ledger(path)

    def test_safe_integer_valued_json_floats_and_fractions(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text('{"max":9007199254740991.0,"min":-9007199254740991e0,'
                            '"fraction":1.5,"tiny":0.001}', encoding="utf-8")
            self.assertEqual(validator.load_ledger(path),
                             {"max":9007199254740991.0, "min":-9007199254740991.0,
                              "fraction":1.5, "tiny":0.001})

    def test_safe_json_integer_boundaries_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text('{"max":9007199254740991,"min":-9007199254740991,"zero":0}',
                            encoding="utf-8")
            self.assertEqual(validator.load_ledger(path),
                             {"max":9007199254740991, "min":-9007199254740991, "zero":0})

    def test_unpaired_unicode_surrogates_are_rejected_recursively(self):
        # Python accepts escaped lone UTF-16 surrogate code points in JSON.
        for payload in (r'{"title":"\ud800"}',
                        r'{"nested":[{"value":"\udfff"}]}',
                        r'{"\ud800":"invalid key"}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Unpaired Unicode surrogate"):
                        validator.load_ledger(path)

    def test_valid_unicode_surrogate_pair_is_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(r'{"symbol":"\ud83d\ude80"}', encoding="utf-8")
            self.assertEqual(validator.load_ledger(path)["symbol"], "🚀")

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
