# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 17:57 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this plan records implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- Count canonical calculations and user-visible workflows once; toolbox aliases are not separate implementations.

## Current repository and release checkpoint

- Starting `dev` is `ba8432fac4d100a20173d6fa68b384cd23593720`; `main` is `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`. This atomic change advances only the existing `dev` ref; main remains unchanged.
- Starting compare is **110 ahead / 0 behind**. The resulting dev head is the commit containing this checkpoint, with the SHA recorded by the Git ref and exact-head Actions. No branch was created.
- Exactly two branches exist: `dev` and `main`; both report `protected:false`. Rulesets are empty. Branch-protection reads return HTTP 403 (Resource not accessible by integration), so enforceable protection is not verified.
- PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191) remains the sole `dev`→`main` release PR, open and mergeable, 110 commits ahead / 0 behind before this update, with zero submitted reviews.
- Exact-head Push Quality [#46034852119](https://github.com/saeedsai/ProMathStudio/actions/runs/46034852119) and PR Quality [#46034861653](https://github.com/saeedsai/ProMathStudio/actions/runs/46034861653) both failed at registered browser step 50, `Project migration and rollback browser regression`. The log points to the test's stale `migrated['customFunctions']` snapshot after later valid Graph imports had intentionally replaced that state; it did not demonstrate a production import mutation.
- This run fixes the test to compare every exported state field against a snapshot taken immediately before each rejected import. It also hardens the exposed custom-function restore API: the whole list is validated (reserved names, case-insensitive duplicates, argument grammar/count, type/body/source bounds and matching Python declaration) before any live or localStorage mutation. Direct invalid restores now reject atomically.
- Latest verified main evidence remains Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251), both successful on 24-Nov-2026 at unchanged main. No newer production deployment or hosted behavior is claimed.
- Local checkout is absent and a bounded Git attempt failed with `Could not resolve host: github.com`. Per the repository fallback, this run uses GitHub blobs/tree/commit and a guarded non-force fast-forward update of the existing `dev` ref.

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

**Status:** The current ba8432 exact-head Push and PR workflows failed at project migration step 50. Logs show a stale test snapshot, not a demonstrated production mutation. This run corrects the test and adds atomic direct-restore validation; fresh exact-head Quality is pending. Promotion remains blocked by zero independent reviews and unverified branch protection/rulesets.  
**Acceptance tests:**
- Full Push and PR Quality pass on the exact candidate SHA with all required steps completed and zero skips.
- Inspect the complete PR diff and review threads; an eligible independent reviewer approves.
- Verify main rules require relevant Quality checks, disallow direct pushes and forbid force/deletion; documentation alone is not enforcement.
- Merge only through GitHub's ordinary PR merge operation. Verify resulting main SHA, main Quality, Pages deployment and hosted application boot plus project save/import smoke.

### 2. P1 — Complete saved-project compatibility and rollback

**Status:** Partial. Equation/Solver, Matrix, Graph datasets/overlays, Curve fit, Data Tables and Engineering selectors have focused validation. Custom-function project preflight rejects reserved built-ins, blank formulas and mismatched Python declarations. This iteration also makes the exposed restore API validate the complete list before replacing live functions or localStorage. Full restore-stage failure matrix and 390px mobile round-trip remain open.  
**Acceptance tests:**
- v1→v2 migration and v2 round-trips preserve notebook, calculator, Equation/Solver controls, assumptions, Matrix drafts, Graph primary/overlay datasets, Curve fit, Data Tables workbook/selection, Engineering filters and custom functions.
- Custom names `sin`, `cos`, `tan`, `sqrt`, `min`, `max`, `log`, `exp`, `abs`, `sum`, `if` and `pow` reject in any casing; formula expressions must be nonblank; Python source must declare the matching function name. Valid legacy formula entries and valid Python source remain compatible.
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
