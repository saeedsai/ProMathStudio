#!/usr/bin/env python3
"""Validate the 2026-10-26 machine-readable feature audit import.

Usage: python3 scripts/validate_feature_ledger.py
This checks historical audit data integrity, not current implementation status.
"""
import json
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
    require(data.get("schemaVersion") == 1, "Expected feature ledger schemaVersion 1")
    require(data.get("sourceAudit") == "2026-10-26", "Unexpected source audit date")
    items = data.get("items")
    require(isinstance(items, list), "Feature ledger items must be an array")
    require(len(items) == 324, "Expected 158 existing and 166 gaps from frozen audit")
    require(all(isinstance(item, dict) for item in items), "Every feature ledger item must be an object")
    ids = [item.get("id") for item in items]
    require(len(ids) == len(set(ids)), "Duplicate feature IDs")
    counts = Counter(item.get("kind") for item in items)
    require(counts == {"existing": 158, "gap": 166}, f"Unexpected feature kinds/counts: {counts}")
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


def main():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    counts = validate(data)
    print(f"Feature ledger validated: {counts['existing']} existing, {counts['gap']} gaps")


if __name__ == "__main__":
    main()
