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
    "control": "toolboxes/CONTROL_THEORY_TOOLBOX_FEATURE_LIST.md",
    "gnss": "toolboxes/GNSS_POSITIONING_OBSERVATION_TOOLBOX_FEATURE_LIST.md",
    "signals": "toolboxes/SIGNAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md",
    "cryptography": "toolboxes/CRYPTOGRAPHY_SECURITY_TOOLBOX_FEATURE_LIST.md",
    "electromagnetics": "toolboxes/ELECTROMAGNETICS_TOOLBOX_FEATURE_LIST.md",
    "statistics": "toolboxes/STATISTICS_ENGINEERING_TOOLBOX_FEATURE_LIST.md",
    "data-science": "toolboxes/DATA_SCIENCE_TOOLBOX_FEATURE_LIST.md",
    "materials": "toolboxes/MATERIALS_METALLURGY_ALLOYS_TOOLBOX_FEATURE_LIST.md",
    "structures": "toolboxes/STRUCTURAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md",
    "ai": "toolboxes/AI_MACHINE_LEARNING_TOOLBOX_FEATURE_LIST.md",
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



def alias_review_rows(registry):
    """Return cross-catalog title matches for human review, never solver aliases."""
    by_id = {item["id"]: item for item in registry["entries"]}
    rows = []
    for candidate in registry["aliasCandidates"]:
        matches = [by_id[fid] for fid in candidate["ids"]]
        catalogs = sorted({item["catalog"] for item in matches})
        if len(catalogs) < 2:
            continue
        rows.append({
            "normalizedTitle": candidate["normalizedTitle"],
            "catalogs": catalogs,
            "featureIds": candidate["ids"],
            "reviewStatus": "manual-review-required",
        })
    return rows


def alias_review_markdown(registry):
    """Deterministic, readable review queue for overlapping discipline catalogs."""
    rows = alias_review_rows(registry)
    lines = [
        "# Engineering toolbox title overlaps — manual review",
        "",
        "Matching titles are not evidence of equivalent numerical algorithms.",
        "No solver IDs or runtime aliases are created by this report.",
        "",
        f"Cross-catalog review groups: {len(rows)}",
        "",
    ]
    for row in rows:
        lines.append(f"## {row['normalizedTitle']}")
        lines.append("")
        lines.append("Catalogs: " + ", ".join(row["catalogs"]))
        lines.append("Review status: manual-review-required")
        lines.extend("- `" + fid + "`" for fid in row["featureIds"])
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--alias-review", action="store_true", help="Print cross-catalog title matches for manual review")
    parser.add_argument("--alias-review-json", action="store_true", help="Print machine-readable cross-catalog manual review queue")
    args = parser.parse_args()
    registry = build()
    if args.alias_review and args.alias_review_json:
        parser.error("Choose only one alias review output format")
    if args.alias_review_json:
        print(json.dumps({"status": "manual-review-required", "groups": alias_review_rows(registry)}, indent=2, ensure_ascii=False))
        return
    if args.alias_review:
        print(alias_review_markdown(registry))
        return
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
