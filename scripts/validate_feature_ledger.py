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


def validate(data):
    assert data["schemaVersion"] == 1
    assert data["sourceAudit"] == "2026-10-26"
    items = data["items"]
    assert len(items) == 324, "Expected 158 existing and 166 gaps from frozen audit"
    ids = [x["id"] for x in items]
    assert len(ids) == len(set(ids)), "Duplicate feature IDs"
    counts = Counter(x["kind"] for x in items)
    assert counts == {"existing": 158, "gap": 166}, counts
    assert data["counts"] == {"existing": 158, "gaps": 166}
    assert Counter(x["status"] for x in items if x["kind"] == "existing") == {
        "bounded-complete": 63, "partial": 95
    }
    assert Counter(x["priority"] for x in items if x["kind"] == "gap") == {
        "P0": 22, "P1": 64, "P2": 53, "P3": 27
    }
    for item in items:
        assert all(item.get(k) for k in ("id", "title", "scope", "section", "source"))
        assert item["source"] == "docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md"
        if item["kind"] == "gap":
            assert item["status"] == "planned"
        else:
            assert "priority" not in item
    return counts


def main():
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    counts = validate(data)
    print(f"Feature ledger validated: {counts['existing']} existing, {counts['gap']} gaps")


if __name__ == "__main__":
    main()
