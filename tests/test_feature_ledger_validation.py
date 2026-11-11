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

    def test_cli_supports_explicit_export_and_actionable_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory) / "export.json"
            export.write_text(json.dumps(self.original), encoding="utf-8")
            good = subprocess.run([sys.executable, str(SCRIPT), str(export)],
                                  capture_output=True, text=True, check=False)
            self.assertEqual(good.returncode, 0, good.stderr)
            self.assertIn("158 existing, 166 gaps", good.stdout)
            export.write_text('{"items": [}', encoding="utf-8")
            bad = subprocess.run([sys.executable, str(SCRIPT), str(export)],
                                 capture_output=True, text=True, check=False)
            self.assertNotEqual(bad.returncode, 0)
            self.assertIn("Malformed feature ledger JSON at line", bad.stderr)
            self.assertNotIn("Traceback", bad.stderr)

    def test_cli_json_summary_is_machine_readable_and_validated(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory) / "export.json"
            export.write_text(json.dumps(self.original), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--json-summary", str(export)],
                capture_output=True, text=True, check=False, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout), {"existing": 158, "gaps": 166})
            self.assertEqual(result.stderr, "")
            export.write_text('{"items": [}', encoding="utf-8")
            invalid = subprocess.run(
                [sys.executable, str(SCRIPT), "--json-summary", str(export)],
                capture_output=True, text=True, check=False, timeout=10,
            )
            self.assertNotEqual(invalid.returncode, 0)
            self.assertEqual(invalid.stdout, "")
            self.assertIn("Malformed feature ledger JSON", invalid.stderr)

    def test_cli_quiet_is_silent_on_success_but_not_on_error(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory) / "export.json"
            export.write_text(json.dumps(self.original), encoding="utf-8")
            for extra in ([], ["--json-summary"]):
                good = subprocess.run(
                    [sys.executable, str(SCRIPT), "--quiet", *extra, str(export)],
                    capture_output=True, text=True, check=False, timeout=10,
                )
                self.assertEqual(good.returncode, 0, good.stderr)
                self.assertEqual((good.stdout, good.stderr), ("", ""))
            export.write_text('{"items": [}', encoding="utf-8")
            bad = subprocess.run(
                [sys.executable, str(SCRIPT), "--quiet", str(export)],
                capture_output=True, text=True, check=False, timeout=10,
            )
            self.assertNotEqual(bad.returncode, 0)
            self.assertEqual(bad.stdout, "")
            self.assertIn("Malformed feature ledger JSON", bad.stderr)

    def test_feature_ids_reject_surrounding_whitespace(self):
        # A visually identical ID with hidden spaces must not survive export.
        for malformed in (" " + self.original["items"][0]["id"],
                          self.original["items"][0]["id"] + " ",
                          "\t" + self.original["items"][0]["id"],
                          self.original["items"][0]["id"] + "\t",
                          "\n" + self.original["items"][0]["id"],
                          self.original["items"][0]["id"] + "\n"):
            with self.subTest(malformed=malformed):
                changed = copy.deepcopy(self.original)
                changed["items"][0]["id"] = malformed
                with self.assertRaisesRegex(ValueError, "surrounding whitespace \\(item 0\\)"):
                    validator.validate(changed)
        self.assertEqual(validator.validate(self.original)["gap"], 166)

    def test_feature_ids_reject_interior_invisible_characters(self):
        # strip() does not remove embedded format characters or controls.
        original_id = self.original["items"][0]["id"]
        for hidden in ("\u200b", "\u202e", "\x1f", "\u2060"):
            with self.subTest(hidden=repr(hidden)):
                changed = copy.deepcopy(self.original)
                changed["items"][0]["id"] = original_id[:2] + hidden + original_id[2:]
                with self.assertRaisesRegex(ValueError, r"invisible characters \(item 0\)"):
                    validator.validate(changed)
        self.assertEqual(validator.validate(self.original)["existing"], 158)

    def test_feature_ids_reject_interior_whitespace(self):
        original_id = self.original["items"][0]["id"]
        # Real Unicode whitespace characters, not literal backslash escapes.
        for separator in (" ", "\t", "\n", "\r", "\u00a0"):
            with self.subTest(separator=repr(separator)):
                changed = copy.deepcopy(self.original)
                changed["items"][0]["id"] = original_id[:5] + separator + original_id[5:]
                with self.assertRaisesRegex(ValueError, r"interior whitespace \(item 0\)"):
                    validator.validate(changed)
        # The validator still accepts canonical IDs after each negative case.
        self.assertEqual(validator.validate(self.original)["gap"], 166)

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

    def test_excessive_json_nesting_reports_a_validation_error(self):
        # Deeply nested JSON should fail as invalid audit input rather than
        # leaking an implementation-specific recursion exception.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text("[" * 12000 + "0" + "]" * 12000, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "nesting exceeds decoder limit"):
                validator.load_ledger(path)

    def test_oversized_ledger_is_rejected_before_json_decoding(self):
        # Bound memory usage even if an export is mostly whitespace.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_bytes(b" " * (8 * 1024 * 1024 + 1))
            with self.assertRaisesRegex(ValueError, "exceeds 8 MiB input limit"):
                validator.load_ledger(path)
            path.write_bytes(b'{"ok":true}')
            self.assertEqual(validator.load_ledger(path), {"ok": True})

    def test_missing_or_directory_ledger_reports_read_error(self):
        # Missing/unreadable audit inputs should fail with a stable diagnostic.
        with tempfile.TemporaryDirectory() as directory:
            missing = Path(directory) / "missing.json"
            with self.assertRaisesRegex(ValueError, "Cannot read feature ledger JSON"):
                validator.load_ledger(missing)
            with self.assertRaisesRegex(ValueError, "Cannot read feature ledger JSON"):
                validator.load_ledger(Path(directory))

    def test_invalid_utf8_is_reported_as_a_validation_error(self):
        # Strict UTF-8 input should give an actionable audit diagnostic.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            for payload in (bytes([0xff]), bytes([0xc3, 0x28])):
                with self.subTest(payload=payload):
                    path.write_bytes(payload)
                    with self.assertRaisesRegex(ValueError, "must be valid UTF-8"):
                        validator.load_ledger(path)
            path.write_text('{"title":"naive"}', encoding="utf-8")
            self.assertEqual(validator.load_ledger(path)["title"], "naive")

    def test_utf8_bom_export_is_accepted_without_relaxing_utf8_validation(self):
        # Spreadsheet JSON exports may prepend EF BB BF; internal BOMs remain
        # ordinary data and malformed UTF-8 still raises an audit error.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            for prefix in (b"", bytes.fromhex("efbbbf")):
                with self.subTest(prefix=prefix):
                    path.write_bytes(prefix + '{"title":"naïve"}'.encode("utf-8"))
                    self.assertEqual(validator.load_ledger(path), {"title": "naïve"})
            path.write_bytes(bytes.fromhex("efbbbf") + bytes.fromhex("ff"))
            with self.assertRaisesRegex(ValueError, "must be valid UTF-8"):
                validator.load_ledger(path)
            # Only a BOM at byte offset zero is a permitted transport marker.
            # A second BOM or a BOM after whitespace must not be stripped.
            for payload in (bytes.fromhex("efbbbfefbbbf") + b"{}",
                            b" " + bytes.fromhex("efbbbf") + b"{}"):
                with self.subTest(misplaced_bom=payload):
                    path.write_bytes(payload)
                    with self.assertRaisesRegex(ValueError, "Malformed feature ledger JSON at line"):
                        validator.load_ledger(path)

    def test_malformed_json_reports_line_and_column(self):
        # Parse diagnostics should identify the location without exposing raw
        # JSONDecodeError to callers; BOM and valid input still work.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            for payload in ('{"items": [1,}', '{\n"ok": true,\n"bad": }'):
                with self.subTest(payload=payload):
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, r"Malformed feature ledger JSON at line \d+, column \d+"):
                        validator.load_ledger(path)
            path.write_bytes(bytes.fromhex("efbbbf") + b'{"ok":true}')
            self.assertEqual(validator.load_ledger(path), {"ok": True})

    def test_nested_unicode_validation_is_iterative(self):
        # Decoder-accepted nesting must not overflow the post-parse validator.
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            for leaf, diagnostic in (('"ok"', None),
                                     ('"\\u0000"', "NUL character"),
                                     ('"\\ud800"', "Unpaired Unicode surrogate"),
                                     ('{"\\u0000key":"value"}', "NUL character")):
                with self.subTest(leaf=leaf):
                    payload = "[" * 400 + leaf + "]" * 400
                    path.write_text(payload, encoding="utf-8")
                    if diagnostic:
                        with self.assertRaisesRegex(ValueError, diagnostic):
                            validator.load_ledger(path)
                    else:
                        self.assertIsInstance(validator.load_ledger(path), list)

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
                    if payload in ('{"counts":{"gaps":0.000e-999}}',
                                   '{"extra":0e-999}', '{"extra":-0e-999}',
                                   '{"extra":0.000000e-999}'):
                        decoded = validator.load_ledger(path)
                        value = decoded["counts"]["gaps"] if "counts" in decoded else decoded["extra"]
                        self.assertEqual(value, 0.0)
                    else:
                        with self.assertRaisesRegex(ValueError, "Underflowed feature ledger JSON number"):
                            validator.load_ledger(path)

    def test_negative_zero_integer_is_not_silently_normalized(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            for payload in ('{"value":-0}', '{"nested":[1,-0]}'):
                with self.subTest(payload=payload):
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Negative-zero"):
                        validator.load_ledger(path)
            for payload in ('{"value":0}', '{"value":-1}', '{"value":-0.0}'):
                with self.subTest(valid=payload):
                    path.write_text(payload, encoding="utf-8")
                    self.assertIn("value", validator.load_ledger(path))

    def test_excessive_integer_digits_report_stable_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text('{"extra":' + '9' * 5000 + '}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "integer exceeds decoder digit limit"):
                validator.load_ledger(path)
            path.write_text('{"extra":9007199254740991}', encoding="utf-8")
            self.assertEqual(validator.load_ledger(path)["extra"], 9007199254740991)

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

    def test_fractional_json_precision_loss_is_rejected(self):
        # Non-integer binary64 rounding must not silently discard decimal digits.
        for payload in ('{"extra":0.10000000000000001}',
                        '{"nested":[-1.23456789012345678]}',
                        '{"counts":{"gaps":1.23456789012345678}}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "Rounded feature ledger JSON fractional precision"):
                        validator.load_ledger(path)

    def test_equivalent_fraction_notations_remain_accepted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text('{"a":0.1,"b":1e-1,"c":1.2345678901234567,'
                            '"subnormal":5e-324,"zero":-0.000e-999}', encoding="utf-8")
            decoded = validator.load_ledger(path)
            self.assertEqual(decoded["a"], decoded["b"])
            self.assertEqual(decoded["c"], 1.2345678901234567)
            self.assertEqual(decoded["subnormal"], 5e-324)
            self.assertEqual(decoded["zero"], 0.0)

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

    def test_nul_characters_are_rejected_in_keys_and_nested_values(self):
        # JSON permits escaped U+0000; audit text exports must not.
        for payload in (r'{"title":"\u0000"}',
                        r'{"nested":[{"value":"x\u0000y"}]}',
                        r'{"\u0000key":"value"}'):
            with self.subTest(payload=payload):
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ledger.json"
                    path.write_text(payload, encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "NUL character"):
                        validator.load_ledger(path)

    def test_non_nul_control_escapes_remain_supported(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(r'{"label":"line\nnext","tab":"a\tb"}', encoding="utf-8")
            self.assertEqual(validator.load_ledger(path),
                             {"label": "line\nnext", "tab": "a\tb"})

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
