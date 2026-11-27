# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 19:19 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this plan records implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- Count canonical calculations and user-visible workflows once; toolbox aliases are not separate implementations.

## Current repository and release checkpoint

- Starting `dev` is `229fd711759b565f01bc68b4ef2535e618dbe15e`; `main` is `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`. Compare is **113 ahead / 0 behind**. Exactly two branches exist: `dev` and `main`.
- Both branches report `protected:false`; repository rulesets are empty. Branch-protection reads return HTTP 403 (Resource not accessible by integration), so enforceable protection is not verified.
- PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191) is the sole `dev`→`main` release PR, open and mergeable at the starting head, with **zero submitted independent reviews**.
- Exact-head Push Quality [#46048195719](https://github.com/saeedsai/ProMathStudio/actions/runs/46048195719) and PR Quality [#46048204133](https://github.com/saeedsai/ProMathStudio/actions/runs/46048204133) both failed at browser step 50, Project migration and rollback. The log pinpoints tests/smoke_project_schema.py line 98: #cf-name resolves but is not visible because its native custom-function details disclosure is closed. Earlier browser checks and structural tests passed. This is a missing UI interaction in the test, not a production editor failure.
- The browser regression already uses an ephemeral loopback HTTP server for real-origin localStorage checks; this repair opens the custom-function details panel by clicking its visible summary before filling editor controls and asserts the fields are visible. Production validation is also hardened consistently in editor save, direct restore and project preflight: a Python custom function must have exactly one synchronous top-level declaration of its saved name and its ordered positional parameters must match params. Duplicate definitions and async def are rejected because a later definition can replace the callable and an async function returns a coroutine the numeric worker cannot consume.
- Added Node schema, Chromium editor/import/direct-restore cases, updated the project-format contract, and preserved exact `src/project-schema.js` ↔ embedded `index.html` parity. Isolated V8 checks run before the atomic dev commit; full Python/Chromium/build certification must come from fresh exact-head Actions.
- Latest verified production evidence remains Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and GitHub Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251), both successful on 24-Nov-2026 at unchanged main. The new dev work is not released.
- The local checkout is absent and a bounded Git attempt fails with `Could not resolve host: github.com`; this run uses the connected GitHub integration and a guarded non-force fast-forward update of the existing `dev` ref.

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

**Status:** Exact-head Push #46048195719 and PR #46048204133 both failed at browser step 50 because the test filled #cf-name while its native details panel was closed. This run opens the panel through its summary, adds a visible-control assertion, and rejects duplicate/async Python definitions consistently across editor, direct restore and project preflight. Fresh exact-head Quality is pending. Promotion remains blocked by zero independent reviews and unverified branch protection/rulesets.  
**Acceptance tests:**
- Full Push and PR Quality pass on the exact candidate SHA with all required steps completed and zero skips.
- Inspect the complete PR diff and review threads; an eligible independent reviewer approves.
- Verify main rules require relevant Quality checks, disallow direct pushes and forbid force/deletion; documentation alone is not enforcement.
- Merge only through GitHub's ordinary PR merge operation. Verify resulting main SHA, main Quality, Pages deployment and hosted application boot plus project save/import smoke.

### 2. P1 — Complete saved-project compatibility and rollback

**Status:** Partial. Equation/Solver, Matrix, Graph datasets/overlays, Curve fit, Data Tables and Engineering selectors have focused validation. Custom-function preflight and direct restore reject reserved built-ins, blank formulas, mismatched positional signatures, duplicate top-level definitions and async functions before mutating state. The browser test now opens the editor through its actual disclosure control. Full restore-stage failure matrix and 390px mobile round-trip remain open.  
**Acceptance tests:**
- v1→v2 migration and v2 round-trips preserve notebook, calculator, Equation/Solver controls, assumptions, Matrix drafts, Graph primary/overlay datasets, Curve fit, Data Tables workbook/selection, Engineering filters and custom functions.
- Custom names `sin`, `cos`, `tan`, `sqrt`, `min`, `max`, `log`, `exp`, `abs`, `sum`, `if` and `pow` reject in any casing; formula expressions must be nonblank; Python source must declare the matching function name and exact ordered positional parameter list. Valid legacy formula entries and valid Python source remain compatible.
- Invalid custom functions reject before confirmation and preserve all current workspace state; Python source is not executed during import. Direct restore calls reject malformed/reserved/duplicate lists atomically and preserve both active functions and localStorage.
- Inject failure after each restore stage and verify rollback; desktop and 390px mobile imports have no console errors and exact source/bundle parity.

### 3. P1 — Complete Data Tables numerical and file integrity

**Status:** Partial; PRODUCT signed-zero/nesting, 132,000-value MIN/MAX, compensated SUM/AVERAGE, A1:AF6000 reference handling and XLSX local-header/CRC checks exist on dev; broad release evidence remains pending.  
**Acceptance tests:**
- PRODUCT direct/nested/range, negative zero, exponent scaling, empty identity, overflow and underflow against binary64 references.
- MIN/MAX over 132,000 values; SUM/AVERAGE cancellation and subnormal residual references.
- A1:AF6000 references, mixed/absolute anchors, quoted names, sort/delete/undo integrity.
- XLSX ZIP metadata, CRC, size, formula-token boundaries, corrupted archive rejection and preservation of the pre-import workbook.
- Browser, keyboard, 390px and source/bundle parity regressions pass.

### 4. P1 — Finish seven-shape Truss FEM numerical boundaries

**Status:** Partial; compensated stiffness and section-property boundary fixes are on dev, but the complete seven-shape reference matrix and release evidence remain open.  
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
