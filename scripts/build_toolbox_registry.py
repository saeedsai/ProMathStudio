#!/usr/bin/env python3
"""Build a deterministic *planning-only* cross-toolbox feature registry.

Run: python scripts/build_toolbox_registry.py
Check: python scripts/build_toolbox_registry.py --check

Never equate title matches with mathematical equivalence; alias candidates are
for manual review. The audit and catalog status must remain separate.
"""
import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "toolbox-feature-registry.json"
CATALOGS = {
    "physics-mechanical-electrical-electronics-fluids-aerospace": "ENGINEERING_TOOLBOX_FEATURE_CATALOG.md",
    "control": "CONTROL_THEORY_TOOLBOX_FEATURE_LIST.md",
    "gnss": "GNSS_POSITIONING_OBSERVATION_TOOLBOX_FEATURE_LIST.md",
    "signals": "SIGNAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md",
    "cryptography": "CRYPTOGRAPHY_SECURITY_TOOLBOX_FEATURE_LIST.md",
    "electromagnetics": "ELECTROMAGNETICS_TOOLBOX_FEATURE_LIST.md",
    "statistics": "STATISTICS_ENGINEERING_TOOLBOX_FEATURE_LIST.md",
    "data-science": "DATA_SCIENCE_TOOLBOX_FEATURE_LIST.md",
    "materials": "MATERIALS_METALLURGY_ALLOYS_TOOLBOX_FEATURE_LIST.md",
    "structures": "STRUCTURAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md",
    "ai": "AI_MACHINE_LEARNING_TOOLBOX_FEATURE_LIST.md",
}


def normalized_title(value):
    value = re.sub(r"[*`]", "", value).strip().lower()
    return re.sub(r"[^a-z0-9]+", " ", value).strip()


def feature_id(catalog, title):
    slug = re.sub(r"[^a-z0-9]+", "-", normalized_title(title)).strip("-")[:55]
    digest = hashlib.sha256((catalog + "\0" + title).encode("utf-8")).hexdigest()[:10]
    return "catalog:" + catalog + ":" + slug + "-" + digest


def parse_catalog(key, filename):
    path = DOCS / filename
    lines = path.read_text(encoding="utf-8").splitlines()
    section = ""
    results = []
    seen = set()
    for line in lines:
        if line.startswith("## "):
            section = line[3:].strip()
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [re.sub(r"\\([|\\])", r"\1", cell.strip()) for cell in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if len(cells) < 2:
            continue
        # Ignore Markdown alignment rows, including :--- and ---: variants.
        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue
        title, description = cells[:2]
        if normalized_title(title) in {"feature", "tool", "capability", "name", "category", "area", "discipline", "toolbox"}:
            continue
        if not title or not description or all(c in ":- " for c in title):
            continue
        # Reject summary/navigation tables and count/priority metadata.
        if re.fullmatch(r"[\d,]+", description) or description.startswith("[") and "](" in description:
            continue
        # Summary rows are metadata, not implementable engineering tools.
        if normalized_title(title) in {"total", "subtotal", "grand total", "count", "total features", "number of features"}:
            continue
        fid = feature_id(key, title)
        if fid in seen:
            continue
        seen.add(fid)
        results.append({
            "id": fid, "catalog": key, "title": title,
            "description": description, "section": section,
            "source": "docs/" + filename, "status": "planned-unverified",
        })
    return results


def build():
    entries = []
    for key, filename in CATALOGS.items():
        entries.extend(parse_catalog(key, filename))
    by_name = defaultdict(list)
    for item in entries:
        by_name[normalized_title(item["title"])].append(item["id"])
    alias_candidates = [
        {"normalizedTitle": name, "ids": sorted(ids)}
        for name, ids in sorted(by_name.items())
        if name and len(ids) > 1
    ]
    return {
        "schemaVersion": 1,
        "status": "catalog-import-planning-only",
        "warning": "Title matches are review candidates, NOT deduplicated algorithms or verified implementations. Broad original-six catalog also includes navigation tables.",
        "auditLedger": "docs/feature-ledger-audit-20261026.json",
        "catalogCount": len(CATALOGS),
        "entryCount": len(entries),
        "candidateAliasGroupCount": len(alias_candidates),
        "entries": entries,
        "aliasCandidates": alias_candidates,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    registry = build()
    encoded = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != encoded:
            parser.error("Toolbox registry is stale; run python scripts/build_toolbox_registry.py")
    else:
        OUTPUT.write_text(encoded, encoding="utf-8")
    print(f"Registry {'verified' if args.check else 'generated'}: "
          f"{registry['entryCount']} planning entries; "
          f"{registry['candidateAliasGroupCount']} possible title-alias groups")


if __name__ == "__main__":
    main()
