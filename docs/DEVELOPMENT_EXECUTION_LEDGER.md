## 2026-11-27 12:22 CET — PREVALIDATE ENGINEERING DISCIPLINE IDS

- Starting refs: `dev` 27971dc78f5bdaf293e643404d8942c11ddb8a68; `main` 0d8ac89f7c9177806a266e56b27980c83d2c3ff5; compare main...dev = 102 ahead / 0 behind. Only `dev` and `main` branches exist; both report `protected: false`.
- Re-read root `AGENTS.md`, this living plan, the frozen 26-Oct inventory, Unified Master Implementation Plan, Engineering Architecture/Toolbox catalog, project-format contract, project schema, Engineering catalog and project filter Node/Chromium regressions.
- Exact starting-head Push Quality [#45980025915](https://github.com/saeedsai/ProMathStudio/actions/runs/45980025915) and PR Quality [#45980033277](https://github.com/saeedsai/ProMathStudio/actions/runs/45980033277) both completed all 218 steps successfully, with zero failed or skipped steps. No current exact-head CI failure remains. These runs certify only the starting SHA.
- Found a preflight/runtime mismatch: `src/project-schema.js` accepted any syntactically valid lowercase/hyphen Engineering discipline, but `src/engineering-catalog.js` only exposes nine stable IDs. An unknown ID such as `nosuchfield` therefore passed schema validation, displayed the confirmation prompt, and failed later in `engineeringCatalog.restoreState()` after the importer had begun its transactional path.
- Changed project-schema validation to allow only the empty all-disciplines selection or the nine catalog IDs: physics, mechanical, electrical, electronics, fluids, aerospace, control, gnss and signals. Legacy omitted/null Engineering state and query length 0–200 remain compatible.
- Extended the Node schema regression to compare the schema's ID set exactly against the canonical catalog and accept all nine IDs; unknown syntactically valid IDs now reject, along with existing shape/type/query-boundary cases. Extended the registered Chromium smoke to assert that an unknown ID fails before the confirmation prompt and leaves the previous project/filter unchanged.
- Updated `docs/PROJECT_FORMAT.md`, the living plan, this ledger and `CHANGELOG.md`. Synchronized `src/project-schema.js` byte-for-byte into the `promath-project-schema` block in standalone `index.html`.
- A bounded local Git check confirmed no checkout is mounted and `git ls-remote` failed because the execution container could not resolve github.com. No repeated network retry was attempted; GitHub integration is used for the atomic dev update.
- The actual schema passed an isolated V8 regression for all nine canonical IDs, unknown IDs, legacy null/omitted values and the 200/201 query boundary. Full Python/Chromium/build certification must come from fresh exact-head GitHub Actions.
- PR #191 remains open/mergeable, 102 commits ahead / 0 behind, 38 changed files, zero submitted independent reviews. Branch-protection read returns HTTP 403; rulesets are empty. No merge or direct main update.
- Latest production evidence remains Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251), successful on unchanged main on 24-Nov-2026; no newer deployment/live verification.
- Frozen historical inventory remains **166 gaps / 95 partial**, unchanged. New work is implemented on dev and not released.

---

undefined