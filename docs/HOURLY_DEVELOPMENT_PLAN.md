# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 21:55 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this plan records implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- Count canonical calculations and user-visible workflows once; toolbox aliases are not separate implementations.

## Current repository and release checkpoint

- Starting `dev` for this checkpoint was `d4889c39745e962b3e851f9ebababb4e2efb2505`; `main` is `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`. Compare was **116 ahead / 0 behind**. Exactly two branches exist: `dev` and `main`. This run advances `dev` with one guarded atomic commit; its resulting SHA is verified from the branch ref after the update and reported with this checkpoint.
- Both branches report `protected:false`; repository rulesets are empty. Branch-protection reads return HTTP 403 (Resource not accessible by integration), so enforceable protection is not verified.
- PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191) is the sole `dev`→`main` release PR, open and mergeable at the starting head, with **zero submitted independent reviews**.
- Exact-head Push Quality [#46062475250](https://github.com/saeedsai/ProMathStudio/actions/runs/46062475250) and PR Quality [#46062482012](https://github.com/saeedsai/ProMathStudio/actions/runs/46062482012) both passed **218/218** on starting head `d4889c39745e962b3e851f9ebababb4e2efb2505`, with zero failed or skipped steps. This certifies the XLSX data-descriptor change on that head; the new Truss reaction change requires fresh exact-head runs.
- The browser regression already uses an ephemeral loopback HTTP server for real-origin localStorage checks; this repair opens the custom-function details panel by clicking its visible summary before filling editor controls and asserts the fields are visible. Production validation is also hardened consistently in editor save, direct restore and project preflight: a Python custom function must have exactly one synchronous top-level declaration of its saved name and its ordered positional parameters must match params. Duplicate definitions and async def are rejected because a later definition can replace the callable and an async function returns a coroutine the numeric worker cannot consume.
- Added Node schema, Chromium editor/import/direct-restore cases, updated the project-format contract, and preserved exact `src/project-schema.js` ↔ embedded `index.html` parity. Isolated V8 checks run before the atomic dev commit; full Python/Chromium/build certification must come from fresh exact-head Actions.
- Latest verified production evidence remains Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and GitHub Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251), both successful on 24-Nov-2026 at unchanged main. The new dev work is not released.
- The local checkout is absent (`git rev-parse --show-toplevel` returns “not a git repository”). The GitHub integration is used for repository access. The `index.html` content endpoint returns an empty body with a blob SHA, so this run deliberately changes only the adjacent `tools/truss-fem.js` script and its tests; no standalone bundle edit is required.

## Operating contract

1. Read root `AGENTS.md`, this plan, the frozen audit, unified master plan, relevant architecture/catalog contracts and exact-head CI before choosing work.
2. Work only on existing `dev`; preserve the standalone offline `index.html` and synchronize every modular source change with its embedded module.
3. Every source change has direct positive, negative and boundary regression coverage. Keep browser smoke registration and full Quality gates enabled.
4. Commit source, synchronized bundle, tests, documentation, this plan, execution ledger and changelog together in one bounded atomic dev commit.
5. Inspect exact-commit Push and PR checks; read failures and repair root causes without removing assertions or weakening checks.
6. Merge only through ordinary PR #191 after exact-head Quality, independent review and enforceable protections are verified. Then verify main Quality, Pages deployment and hosted critical paths.
7. Maintain the historical 166-gap / 95-partial baseline until a separately documented re-audit is supported by evidence.

## Next five features — NEXT FIVE priorities

### 1. P0 — Release PR #191 safely

**Status:** XLSX descriptor validation and the preceding reserved-name correction are certified by exact-head Push #46062475250 and PR #46062482012 (218/218 each, zero failures/skips) on `d4889c39745e962b3e851f9ebababb4e2efb2505`. This checkpoint adds a Truss FEM reaction-accumulation correction and requires fresh exact-head Quality. Promotion remains blocked by zero independent reviews and unverified branch protection/rulesets.  
**Acceptance tests:**
- Full Push and PR Quality pass on the exact candidate SHA with all required steps completed and zero skips.
- Inspect the complete PR diff and review threads; an eligible independent reviewer approves.
- Verify main rules require relevant Quality checks, disallow direct pushes and forbid force/deletion; documentation alone is not enforcement.
- Merge only through GitHub's ordinary PR merge operation. Verify resulting main SHA, main Quality, Pages deployment and hosted application boot plus project save/import smoke.

### 2. P1 — Complete saved-project compatibility and rollback

**Status:** Partial. Equation/Solver, Matrix, Graph datasets/overlays, Curve fit, Data Tables and Engineering selectors have focused validation. Custom-function preflight and direct restore reject reserved built-ins, blank formulas, mismatched positional signatures, duplicate top-level definitions and async functions before mutating state. The browser test now opens the editor through its actual disclosure control. Full restore-stage failure matrix and 390px mobile round-trip remain open.  
**Acceptance tests:**
- v1→v2 migration and v2 round-trips preserve notebook, calculator, Equation/Solver controls, assumptions, Matrix drafts, Graph primary/overlay datasets, Curve fit, Data Tables workbook/selection, Engineering filters and custom functions.
- Custom names `sin`, `cos`, `tan`, `sqrt`, `min`, `max`, `log`, `exp`, `abs`, `sum`, `if`, `pow`, `average`, `avg`, `count`, `median` and `product` reject in any casing; formula expressions must be nonblank; Python source must declare the matching function name and exact ordered positional parameter list. Valid legacy formula entries and valid Python source remain compatible.
- Invalid custom functions reject before confirmation and preserve all current workspace state; Python source is not executed during import. Direct restore calls reject malformed/reserved/duplicate lists atomically and preserve both active functions and localStorage.
- Inject failure after each restore stage and verify rollback; desktop and 390px mobile imports have no console errors and exact source/bundle parity.

### 3. P1 — Complete Data Tables numerical and file integrity

**Status:** Partial; PRODUCT signed-zero/nesting, 132,000-value MIN/MAX, compensated SUM/AVERAGE and A1:AF6000 reference handling are implemented on dev. XLSX signed/unsigned data-descriptor validation, bit-3 local/central consistency and descriptor overlap bounds passed exact-head Push/PR Quality on `d4889c39745e962b3e851f9ebababb4e2efb2505`. Remaining formula-token, corruption and workbook-integrity boundaries remain open.  
**Acceptance tests:**
- PRODUCT direct/nested/range, negative zero, exponent scaling, empty identity, overflow and underflow against binary64 references.
- MIN/MAX over 132,000 values; SUM/AVERAGE cancellation and subnormal residual references.
- A1:AF6000 references, mixed/absolute anchors, quoted names, sort/delete/undo integrity.
- XLSX ZIP metadata, CRC, size, signed/unsigned data descriptors, bit-3 local/central consistency, descriptor truncation/overlap, formula-token boundaries, corrupted archive rejection and preservation of the pre-import workbook.
- Browser, keyboard, 390px and source/bundle parity regressions pass.

### 4. P1 — Finish seven-shape Truss FEM numerical boundaries

**Status:** Partial; compensated stiffness and section-property boundary fixes are on dev. This checkpoint adds exact/compensated nodal reaction accumulation for a 1 N residual bracketed by ±1e16 N member-force terms, with Node and desktop/390px Chromium regressions. Fresh exact-head QA is pending; the complete seven-shape reference matrix and release evidence remain open.  
**Acceptance tests:**
- Independent area, centroid, Ixx/Iyy, section modulus and radius references for solid/hollow rectangles, solid/hollow circles, channel, I-section and L-angle.
- Thin-wall and cavity transitions, sub-ULP contributions, mixed-scale compensated stiffness, mechanism/singularity rejection and SI boundaries.
- Equilibrium residual, strain energy, displacement and member-force references; invalid-input rollback and 390px keyboard/mobile checks.

### 5. P1 — Harden adaptive RK45 difficult-workload boundaries

**Status:** Partial; bounded-stage recovery, subnormal-span initialization, repeated-stage detection and truthful singular/plural warning copy are implemented on dev. Exact c06 Push/PR Quality is green; further overflow, attempt-budget and stale-export boundaries remain.  
**Acceptance tests:**
- Recoverable stage-overflow retries preserve a finite solution when smaller steps succeed; unrecoverable overflow terminates diagnostically.
- Forward/backward sample times remain strictly monotone near ULP spacing and at large epochs.
- Smallest and two-subnormal intervals preserve exact endpoints, report collapsed stages and show the accuracy warning.
- At 1e12, 20-ULP forward/backward cases detect repeated c=4/5 and c=8/9 stage timestamps without changing the endpoint grid.
- Underflow, maximum attempts, exhausted retries, endpoint snapping and stale-export protection have direct numerical and browser regressions.

## Latest checkpoint — 27 November 2026, 17:21 CET

- Verified parent dev `c06bf13609304e616aec060c56424af4e0e844bf`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`, exactly two branches and sole open release PR #191.
- Prior exact-head Push and PR Quality both passed for c06 (runs #46023174963 and #46023187713). New custom-function schema regressions are committed on the new dev head; their exact-head full Quality is pending.
- Implemented custom-function project preflight: reserved built-ins, blank formula expressions and Python source without a matching `def name(...)` declaration now reject before confirmation. Added Node and Chromium regression coverage and documented that Python source is stored, not executed during import.
- Source and embedded standalone project-schema module are synchronized. The bounded local Git attempt failed due DNS; GitHub integration fallback is used.
- Main and Pages remain at the last verified successful evidence dated 24-Nov; the new change is not released.
- Historical inventory remains **166 gaps / 95 partial**, unchanged.


## Latest checkpoint — 27 November 2026, 18:58 CET

- Starting dev `0f0665b6d300fac4618e2bb71196b29dd3aa4eab`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`, compare 111 ahead / 0 behind; exactly dev/main refs.
- Exact-head Push #46038574233 and PR #46038582330 both failed only at project browser step 50. The trace is a localStorage SecurityError caused by the opaque origin created by `page.set_content()`; the test now uses an ephemeral loopback HTTP origin.
- Python custom functions now require their declared ordered positional parameters to equal saved `params` in the editor, project schema and public restore API. Node and Chromium positive/negative cases cover matching multi-argument functions, wrong names/order/count and defaulted arguments.
- Source/schema, standalone bundle, tests, project-format documentation, plan, full ledger and changelog are committed together on dev. Exact-head Push/PR Quality must complete before certification; no merge or deployment.
- PR #191 remains open; independent reviews 0, both branches unprotected, rulesets empty, branch-protection read 403. Main Quality and Pages last succeeded on 24-Nov-2026.
- Frozen historical inventory remains **166 gaps / 95 partial**, unchanged.


## Follow-up checkpoint — 27 November 2026, 18:58 CET

- Post-commit review of `c535d26e968f61ba5b728fe6b6a0eceabf6a97c8` found that the newly inserted editor assertions in `tests/smoke_project_schema.py` were indented outside the active Playwright context. The same-origin HTTP server and Python signature source changes were correct, but the browser test block needed to remain inside the page/browser scope.
- Corrected the assertion block indentation and changed the valid multi-argument fixture to contain a real newline in its Python source. This is a test-fixture correction, not a production behavior change. The c535 exact-head runs are not used to certify the follow-up commit; fresh Push/PR Quality will be required.
- The prior isolated V8 checks passed for the project schema, editor signature helper, direct-restore atomicity and source/bundle parity. Full Python/Chromium/build checks remain delegated to exact-head Actions.
- Historical inventory remains **166 gaps / 95 partial**, unchanged.


## Latest checkpoint — 27 November 2026, 19:19 CET

- Starting refs verified from GitHub: dev 229fd711759b565f01bc68b4ef2535e618dbe15e, main 0d8ac89f7c9177806a266e56b27980c83d2c3ff5; compare 113 ahead / 0 behind. Exactly two branches exist.
- Exact-head Push Quality [#46048195719](https://github.com/saeedsai/ProMathStudio/actions/runs/46048195719) and PR Quality [#46048204133](https://github.com/saeedsai/ProMathStudio/actions/runs/46048204133) failed at browser step 50. The Playwright log shows #cf-name is present but hidden because the native custom-function details panel was never opened. This is a browser-test setup defect; the existing Python compose smoke opens the same panel before interacting with its controls.
- This checkpoint clicks the panel summary and asserts editor visibility before exercising Python signature validation. Production editor/direct-restore/project-import validation now requires exactly one synchronous top-level definition for the saved function name and matching ordered parameters; duplicate and async definitions reject.
- Added Node schema and Chromium import/direct-restore cases for duplicate, async and sync-plus-async declarations. Updated the project-format contract, living plan, execution ledger and changelog; the project-schema source and standalone embedded module remain exactly synchronized.
- Isolated V8 and source/bundle checks are run before commit. Full Python/Chromium/build certification must come from fresh exact-head Push and PR Quality.
- PR #191 remains open at the same dev head, 113 commits ahead of main, with zero independent submitted reviews. Both branches report unprotected, rulesets are empty and branch-protection GET returns 403. No merge or direct main update.
- Latest verified main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages deployment [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) both succeeded on 24-Nov-2026 at unchanged main. This dev work is not released.
- Historical inventory remains 166 gaps / 95 partial, unchanged.


## Latest checkpoint — 27 November 2026, 20:01 CET

- Starting refs verified from GitHub: dev `1013d618bf925c9e005b98716b453feeab9aacb2`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare 114 ahead / 0 behind. Exactly two branches exist. Root AGENTS.md, this plan, frozen 26-Oct inventory, Unified Master Implementation Plan, Data Tables and project-format contracts, PR #191, exact-head workflows, reviews, rulesets and main/Pages evidence were inspected.
- Exact-head Push Quality [#46050272626](https://github.com/saeedsai/ProMathStudio/actions/runs/46050272626) and PR Quality [#46050278029](https://github.com/saeedsai/ProMathStudio/actions/runs/46050278029) both failed at step 85, `tests/smoke_sheet_numeric_hardening.py`. The browser fixture attempted to restore reserved `SUM`, `COUNT`, `MEDIAN` and `IF` names as custom functions; the atomic restore API correctly rejected the list. The fixture was stale after reserved-name hardening.
- A related production consistency gap was found: `AVERAGE`, `AVG`, `COUNT`, `MEDIAN` and `PRODUCT` were missing from the editor, direct-restore and project-schema reserved sets even though Data Tables resolves them as built-ins. The source and embedded standalone bundle now reserve all spreadsheet built-ins case-insensitively.
- The numeric-hardening browser regression now seeds only valid custom functions, verifies all 17 reserved names reject atomically without changing active functions, and continues to test built-in SUM/COUNT/MEDIAN/IF and custom-function composition. Node schema negatives cover the previously missing built-ins. Project-format and Data Tables docs now state the contract.
- Isolated V8 schema checks and exact source/embedded project-schema parity were run before the atomic dev commit. Native Python/Playwright/build checks are unavailable because the execution container has no checkout; fresh exact-head Push/PR Quality is the full browser/build gate.
- PR #191 remains open/mergeable, 114 commits ahead, 46 changed files, zero submitted independent reviews. Branches remain exactly dev/main; both report unprotected, rulesets empty, branch-protection GET 403. No merge or direct main update.
- Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) remain the latest verified successful production evidence on unchanged main from 24-Nov-2026. This change is dev-only pending exact-head CI and release governance.
- Historical inventory remains **166 gaps / 95 partial**, unchanged.


## Latest checkpoint — 27 November 2026, 21:03 CET

- Verified existing refs before editing: dev `fc92e7735836ff65ab86a25235c41a67a1aac723`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare 115 ahead / 0 behind; exactly dev/main branches.
- Re-read root AGENTS.md, the living plan, the complete frozen 26-Oct inventory (166 gaps / 95 partial), Unified Master Implementation Plan, Data Tables/XLSX contract, build script, Quality workflow, PR #191, reviews and current Actions/Pages evidence.
- Exact-head Push Quality [#46054477944](https://github.com/saeedsai/ProMathStudio/actions/runs/46054477944) and PR Quality [#46054483353](https://github.com/saeedsai/ProMathStudio/actions/runs/46054483353) both passed 218/218 on the starting SHA, with zero failed/skipped steps. PR #191 still has zero submitted independent reviews. Branch-protection read returns HTTP 403; rulesets are empty.
- Found an XLSX integrity gap: ZIP general-purpose bit 3 permits local-header CRC/sizes to be deferred to a data descriptor, but the importer skipped all descriptor validation and excluded descriptor bytes from overlap bounds. A malformed descriptor could therefore be accepted despite central-directory metadata being authoritative.
- Updated `src/xlsx-import.js` to accept bit-3 local fields only when zero or equal to central metadata; validate both signed and signatureless 12-byte data descriptors against central CRC/compressed/uncompressed sizes; reject truncated/mismatched descriptors; and include descriptor bytes in local-record overlap detection. Ordinary non-descriptor ZIP behavior is unchanged.
- Added a non-seekable Python ZIP fixture that emits valid bit-3 descriptors, plus browser negatives for corrupted descriptor CRC/size and contradictory bit-3 local metadata. Existing stored/DEFLATE, corruption, transactional rollback, formula and mobile assertions remain.
- Synchronized the standalone `index.html` embedded XLSX importer with `src/xlsx-import.js`; updated the XLSX integrity unittest, browser smoke, Data Tables docs, this plan, execution ledger and changelog.
- The local checkout is absent (bounded `git rev-parse` returns “not a git repository”). A Python non-seekable ZIP reproduction confirmed Python emits bit-3 local headers with zero local metadata and signed descriptors containing the exact central CRC/sizes. Full production-browser validation must come from fresh exact-head GitHub Actions.
- Current main remains unchanged; Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) are the latest verified successful production runs on 24-Nov-2026. No new dev change is live.
- Status: XLSX descriptor validation implemented on dev in this checkpoint; fresh Push/PR Quality pending; no merge or deployment. Historical inventory remains **166 gaps / 95 partial**, unchanged.


## Latest checkpoint — 27 November 2026, 21:55 CET

- Verified starting refs: dev d4889c39745e962b3e851f9ebababb4e2efb2505, main 0d8ac89f7c9177806a266e56b27980c83d2c3ff5; compare 116 ahead / 0 behind. Exactly two branches exist. Root AGENTS.md, this plan, the frozen 26-Oct inventory, Unified Master Implementation Plan, Engineering Architecture/Toolbox contracts, Structural Truss FEM contract, Quality workflow, PR #191, reviews and current Actions/Pages evidence were inspected.
- Exact-head Push Quality [#46062475250](https://github.com/saeedsai/ProMathStudio/actions/runs/46062475250) and PR Quality [#46062482012](https://github.com/saeedsai/ProMathStudio/actions/runs/46062482012) both completed successfully 218/218 on starting SHA d4889c39745e962b3e851f9ebababb4e2efb2505, with zero failures/skips. Fresh checks are required for this new commit.
- Found a support-reaction precision defect in solve(): the nodal resultant used ordinary left-to-right reduction of K[i][j]*u[j] - F[i]. A valid three-bar numerical stress fixture produces reaction terms -1, -1e16 and +1e16 N; the old order loses the -1 N term and reports a 1 N global force-balance residual.
- Replaced the row reduction with finiteSignedSum over the rounded internal-force terms and negative applied load. This uses the exact mixed-sign binary64 accumulator when available and the existing compensated fallback otherwise. FEM outputs remain binary64.
- Added a direct Node regression and a registered Chromium regression at 1280px and 390px. They assert the naive reduction is zero, the support reaction is -1 N, global force balance is zero, and free-DOF residual/energy checks remain below 1e-12.
- Updated the Structural Truss FEM numerical contract, NEXT FIVE plan, execution ledger and changelog. Truss FEM is loaded as an adjacent script; index.html was not changed. Its GitHub content fetch returned an empty body, so no standalone bundle edits were attempted.
- Local checkout is absent: git rev-parse --show-toplevel returned “not a git repository”. A bounded Node arithmetic reproduction confirmed the fixture stiffness is 1e20 N/m, displacements are 1e-20, +1e-4 and -1e-4 m, and the naive reaction sum loses 1 N. Full repository Node/Chromium checks must run on exact-head GitHub Actions.
- PR #191 remains open/mergeable; zero independent reviews. Only dev/main branches exist, both report unprotected; rulesets are empty and branch-protection GET returns HTTP 403. No merge or direct main update.
- Main Quality #45360386408 and Pages deployment #45360367251 remain the latest successful production evidence on unchanged main from 24-Nov-2026. This change is dev-only, not released.
- Historical inventory remains **166 gaps / 95 partial**, unchanged.
