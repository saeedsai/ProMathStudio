#!/usr/bin/env python3
"""Validate the 2026-10-26 machine-readable feature audit import.

Usage: python3 scripts/validate_feature_ledger.py
This checks historical audit data integrity, not current implementation status.
"""
import json
import math
from decimal import Decimal
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "feature-ledger-audit-20261026.json"


def require(condition, message):
    """Enforce audit invariants even when Python is invoked with -O."""
    if not condition:
        raise ValueError(message)


def validate(data):
    require(isinstance(data, dict), "Feature ledger must be a JSON object")
    require(type(data.get("schemaVersion")) is int and data["schemaVersion"] == 1, "Expected feature ledger schemaVersion 1")
    require(data.get("sourceAudit") == "2026-10-26", "Unexpected source audit date")
    items = data.get("items")
    require(isinstance(items, list), "Feature ledger items must be an array")
    require(len(items) == 324, "Expected 158 existing and 166 gaps from frozen audit")
    require(all(isinstance(item, dict) for item in items), "Every feature ledger item must be an object")
    # Validate hash keys before Counter/set: malformed JSON can contain arrays or
    # objects here, which must raise a useful audit error rather than TypeError.
    for index, item in enumerate(items):
        for key in ("id", "kind", "status"):
            require(isinstance(item.get(key), str),
                    f"Feature ledger item {index} has invalid {key}")
        if "priority" in item:
            require(isinstance(item["priority"], str),
                    f"Feature ledger item {index} has invalid priority")
    # Reject invisible ID differences that make cross-file references ambiguous.
    for index, item in enumerate(items):
        require(bool(item["id"]) and item["id"] == item["id"].strip(),
                f"Feature IDs must not have surrounding whitespace (item {index})")
    ids = [item["id"] for item in items]
    require(len(ids) == len(set(ids)), "Duplicate feature IDs")
    counts = Counter(item["kind"] for item in items)
    require(counts == {"existing": 158, "gap": 166}, f"Unexpected feature kinds/counts: {counts}")
    require(isinstance(data.get("counts"), dict) and
            all(type(data["counts"].get(key)) is int for key in ("existing", "gaps")),
            "Frozen feature counts must be integer values")
    require(data.get("counts") == {"existing": 158, "gaps": 166}, "Frozen feature counts mismatch")
    statuses = Counter(item.get("status") for item in items if item["kind"] == "existing")
    require(statuses == {"bounded-complete": 63, "partial": 95}, f"Frozen feature statuses mismatch: {statuses}")
    priorities = Counter(item.get("priority") for item in items if item["kind"] == "gap")
    require(priorities == {"P0": 22, "P1": 64, "P2": 53, "P3": 27},
            f"Frozen gap priorities mismatch: {priorities}")
    for item in items:
        require(all(isinstance(item.get(k), str) and item[k].strip()
                    for k in ("id", "title", "scope", "section", "source")),
                f"Missing/invalid required feature field: {item.get('id')!r}")
        require(item["source"] == "docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md",
                f"Unexpected audit source for {item['id']}")
        if item["kind"] == "gap":
            require(item.get("status") == "planned", f"Gap must remain historically planned: {item['id']}")
        else:
            require("priority" not in item, f"Existing feature must not have gap priority: {item['id']}")
    return counts


def load_ledger(path):
    """Reject ambiguous duplicate JSON keys instead of silently using the last value."""
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate feature ledger JSON key: {key}")
            result[key] = value
        return result

    def reject_nonfinite(token):
        raise ValueError(f"Non-finite feature ledger JSON constant: {token}")

    def finite_float(token):
        value = float(token)
        if not math.isfinite(value):
            raise ValueError(f"Non-finite feature ledger JSON number: {token}")
        # JSON decimal/exponent notation can bypass parse_int and silently
        # round large integer-valued numbers in JavaScript consumers.
        if value.is_integer() and abs(value) > 9007199254740991:
            raise ValueError(f"Unsafe feature ledger JSON floating integer: {token}")
        # Preserve the more specific underflow diagnostic before the general
        # rounded-fraction check: tiny nonzero tokens also round to integer 0.
        # Decimal distinguishes exact zero from nonzero subnormal literals
        # without inspecting exponent digits or losing mantissa precision.
        if value == 0.0 and not Decimal(token).is_zero():
            raise ValueError(f"Underflowed feature ledger JSON number: {token}")
        # A decimal fraction can round to an integer in binary64 even when
        # the integer is inside the safe range (e.g. 1.0000000000000001).
        if value.is_integer() and Decimal(token) != Decimal(int(value)):
            raise ValueError(f"Rounded feature ledger JSON fraction to integer: {token}")
        # Also reject non-integer decimal tokens with more significant digits
        # than binary64 retains, rather than silently changing audit values.
        # str(value) is Python's shortest round-tripping decimal representation;
        # compare numeric Decimal values so equivalent exponent notation works.
        if not value.is_integer() and Decimal(token) != Decimal(str(value)):
            raise ValueError(f"Rounded feature ledger JSON fractional precision: {token}")
        return value

    def safe_integer(token):
        # JSON -0 silently loses its sign when decoded as Python int 0.
        # Preserve the audit's exact numeric representation instead.
        if token == "-0":
            raise ValueError("Negative-zero feature ledger JSON integer is ambiguous")
        # JSON integers beyond IEEE-754's exact integer range lose precision
        # when the audit is consumed by JavaScript or spreadsheet tooling.
        try:
            value = int(token)
        except ValueError as exc:
            # Python 3.11+ bounds decimal integer conversion; expose a stable
            # audit diagnostic instead of leaking the interpreter limit error.
            raise ValueError("Feature ledger JSON integer exceeds decoder digit limit") from exc
        if abs(value) > 9007199254740991:
            raise ValueError(f"Unsafe feature ledger JSON integer: {token}")
        return value

    def reject_invalid_unicode(value):
        # Walk iteratively: valid JSON can be nested deeply enough to exhaust
        # Python recursion while checking decoded strings.
        pending = [value]
        while pending:
            current = pending.pop()
            if isinstance(current, str):
                if "\x00" in current:
                    raise ValueError("NUL character in feature ledger JSON")
                if any(0xD800 <= ord(char) <= 0xDFFF for char in current):
                    raise ValueError("Unpaired Unicode surrogate in feature ledger JSON")
            elif isinstance(current, list):
                pending.extend(current)
            elif isinstance(current, dict):
                for key, item in current.items():
                    pending.append(key)
                    pending.append(item)

    try:
        # UTF-8 BOM is emitted by some spreadsheet exports; accept it only at the start.
        # Cap untrusted audit imports before decoding to avoid unbounded memory use.
        with Path(path).open("rb") as source:
            payload = source.read(8 * 1024 * 1024 + 1)
        if len(payload) > 8 * 1024 * 1024:
            raise ValueError("Feature ledger JSON exceeds 8 MiB input limit")
        data = json.loads(payload.decode("utf-8-sig"),
                          object_pairs_hook=unique_object,
                          parse_constant=reject_nonfinite,
                          parse_float=finite_float,
                          parse_int=safe_integer)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Malformed feature ledger JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc
    except UnicodeDecodeError as exc:
        raise ValueError("Feature ledger JSON must be valid UTF-8") from exc
    except OSError as exc:
        raise ValueError(f"Cannot read feature ledger JSON: {exc.strerror or exc}") from exc
    except RecursionError as exc:
        raise ValueError("Feature ledger JSON nesting exceeds decoder limit") from exc
    reject_invalid_unicode(data)
    return data


def main(argv=None):
    # Validate external exports without modifying the canonical audit.
    import argparse
    parser = argparse.ArgumentParser(description="Validate a historical feature-ledger JSON export")
    parser.add_argument("path", nargs="?", type=Path, default=LEDGER,
                        help="JSON export to validate (default: frozen audit ledger)")
    parser.add_argument("--json-summary", action="store_true",
                        help="Print validated historical counts as machine-readable JSON")
    parser.add_argument("--quiet", action="store_true",
                        help="Validate without success output (errors still go to stderr)")
    args = parser.parse_args(argv)
    try:
        counts = validate(load_ledger(args.path))
    except ValueError as exc:
        parser.error(str(exc))
    if args.quiet:
        return
    if args.json_summary:
        print(json.dumps({"existing": counts["existing"], "gaps": counts["gap"]}, sort_keys=True))
    else:
        print(f"Feature ledger validated: {counts['existing']} existing, {counts['gap']} gaps")


if __name__ == "__main__":
    main()
