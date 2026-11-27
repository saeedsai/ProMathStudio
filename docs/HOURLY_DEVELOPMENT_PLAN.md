# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 16:03 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this file records current implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- The unified roadmap and discipline catalogs contain overlapping aliases; count canonical calculations and user-visible workflows once.

## Current repository and release checkpoint

- Current `dev`: `820d5c03c9e8b0e544f427a89cc328c6350ce2c4`; `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare: **108 ahead / 0 behind**.
- Existing PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191): `dev` → `main`, open and mergeable, 108 commits ahead / 0 behind, 44 changed files, zero submitted independent reviews.
- Branch inventory: exactly `dev` and `main`; both currently report `protected: false`. Rulesets are empty; branch-protection GET returns HTTP 403 to the connected integration.
- Previous-head Quality on `b6c535854313b41406be355b4d06d633d003285b`: Push [#46006460898](https://github.com/saeedsai/ProMathStudio/actions/runs/46006460898) and PR [#46006469595](https://github.com/saeedsai/ProMathStudio/actions/runs/46006469595) both completed **218/218 steps, success, zero failures and zero skips**. New exact-head Quality on `820d5c03c9e8b0e544f427a89cc328c6350ce2c4` failed in both Push [#46014476843](https://github.com/saeedsai/ProMathStudio/actions/runs/46014476843) and PR [#46014485667](https://github.com/saeedsai/ProMathStudio/actions/runs/46014485667) at step 181: `tests/smoke_ode_rk45_stage_resolution.py` still expected the obsolete warning text. The implementation wording is correct; this run updates the stale browser assertion and adds singular/plural checks.
- The earlier `d4ff4a8` candidate's structural failure was caused by an omitted modular `src/ode-tools.js` blob while the standalone `index.html` module had advanced. Commit `b6c5358` restored exact source/bundle parity; the corrected candidate is now fully green. See the execution ledger for the failure diagnosis and correction.
- Latest verified production runs remain Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251), both successful on 24-Nov-2026 at unchanged main. No newer main deployment or live hosted verification is claimed.

## Operating contract

1. Read root `AGENTS.md`, this plan, the frozen audit, unified master plan, relevant architecture/catalog contracts and exact-head CI before choosing work.
2. Work only on existing `dev`; preserve the standalone offline `index.html` and synchronize every modular source change with its embedded module via the canonical build contract.
3. Every source change has direct automated positive, negative and boundary regression coverage. Keep browser smoke registration and full Quality gates enabled.
4. Commit source, synchronized bundle where applicable, tests, documentation, this plan, execution ledger and changelog together in one bounded atomic dev commit.
5. Inspect exact-commit Push and PR checks; read failing logs and repair root causes without removing assertions or weakening checks.
6. Merge only through the ordinary `dev`→`main` PR after full exact-head Quality, required review and enforceable protections are verified. Then verify main Quality, Pages deployment and hosted critical paths.
7. Maintain the historical 166-gap / 95-partial baseline until evidence supports a separately documented re-audit.

## Next five features — NEXT FIVE priorities

### 1. P0 — Release PR #191 safely

**Status:** The prior b6c5358 head is fully green (218/218 Push and PR). Current 820d5c0 exact-head runs both failed at step 181 because the stage-resolution browser test still expected the old warning wording; the result-panel copy is intentionally broader and accurate. This iteration updates the stale assertion and adds singular/plural grammar coverage. Promotion remains blocked by zero independent reviews and unverified main protection.  
**Acceptance tests:**
- Full Push and PR Quality pass on the exact candidate head with all required steps completed and zero skips.
- Complete PR diff and review threads are inspected; an eligible independent reviewer approves.
- Main protection/rules require relevant Quality checks and disallow direct pushes/force updates; verify through GitHub rather than documentation.
- Merge only through GitHub's ordinary PR merge operation. Verify resulting main SHA, main Quality, Pages build/deployment and hosted application boot plus project save/import smoke.

### 2. P1 — Complete saved-project compatibility

**Status:** Partial; Equation/Solver, Matrix, Graph, Curve fit, Data Tables and Engineering filters have individual schema/round-trip tests. This run closes the Engineering discipline preflight gap on dev; whole-workspace stage-by-stage rollback is not fully certified.  
**Acceptance tests:**
- v1→v2 migration and v2 round-trips preserve notebook, calculator, Equation/Solver, assumptions, Matrix drafts, Graph primary/overlay datasets, Curve fit, Data Tables workbook/selection, Engineering filters and custom functions.
- The nine Engineering discipline IDs match the catalog exactly; unknown IDs, wrong types and 201-character queries reject before confirmation, while empty, known IDs, null/omitted legacy state and a 200-character query remain compatible.
- Unsupported enums/versions, malformed cells, invalid IDs and over-limit values reject before mutation; inject failure after each restore stage and verify rollback.
- Desktop and 390px mobile project import/export have no console errors and exact source/bundle parity.

### 3. P1 — Complete Data Tables numerical and file integrity

**Status:** Partial; PRODUCT signed-zero/nesting, large MIN/MAX, compensated SUM/AVERAGE and XLSX import/export hardening exist on dev; release verification remains pending.  
**Acceptance tests:**
- PRODUCT direct/nested/range, negative zero, exponent scaling, empty identity, overflow and underflow against independent binary64 references.
- MIN/MAX over 132,000 values; SUM/AVERAGE cancellation and subnormal residual references.
- A1:AF6000 structural references, mixed/absolute anchors, quoted names, sort/delete/undo reference integrity.
- XLSX ZIP metadata, CRC, size, formula-token boundaries, corrupted archive rejection and preservation of the pre-import workbook.
- Browser, keyboard, 390px and source/bundle parity regressions pass.

### 4. P1 — Finish seven-shape Truss FEM numerical boundaries

**Status:** Partial; compensated stiffness and section-property boundary fixes are on dev, but the complete seven-shape acceptance matrix and release evidence remain open.  
**Acceptance tests:**
- Independent area, centroid, Ixx/Iyy, section modulus and radius references for solid/hollow rectangles, solid/hollow circles, channel, I-section and L-angle.
- Thin-wall and cavity-transition limits, sub-ULP contributions, mixed-scale compensated stiffness assembly, mechanism/singularity rejection and SI conversion boundaries.
- Equilibrium residual, strain energy, displacement and member-force references; invalid-input rollback and 390px keyboard/mobile checks.

### 5. P1 — Harden adaptive RK45 difficult-workload boundaries

**Status:** Partial; bounded-stage recovery, subnormal-span initialization and repeated-stage diagnostics are implemented on dev. The 820d5c0 browser warning-copy change exposed a stale assertion at step 181 in both exact-head workflows. This iteration fixes that test and verifies singular/plural count wording for one and two accepted collision steps. Remaining overflow, attempt-budget and stale-export boundaries stay in the acceptance matrix.  
**Acceptance tests:**
- Recoverable stage-overflow retries preserve a finite solution when smaller steps succeed; unrecoverable overflow terminates with a diagnostic.
- Forward/backward sample times are strictly monotone with no duplicate timestamps at large epochs or near-ULP spacing.
- When `span/20` underflows to zero but the requested endpoints are distinct, the solver uses one full representable span; smallest- and two-subnormal intervals in both directions preserve the endpoint, report collapsed stages and show the accuracy warning.
- At 1e12, a 20-ULP interval in both directions exercises a 5-ULP trial where c=4/5 and c=8/9 round to the same timestamp; both collision counters must report the accepted repeated-stage attempt without changing the endpoint grid.
- Underflow, maximum attempts, exhausted retries, endpoint snapping and stale-export protection have direct numerical and browser regressions.
- Data Tables/Graph exports, keyboard behavior and 390px layout remain correct.

## Following queue

After the five priorities above, continue shared-tool registry and canonical toolbox deduplication, then extend the verified engineering solver catalog without creating duplicate implementations or claiming planned entries as shipped.

## Latest checkpoint — 27 November 2026, 16:03 CET

- Verified refs: dev `820d5c03c9e8b0e544f427a89cc328c6350ce2c4`; main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare **108 ahead / 0 behind**. Exactly two branches exist: dev and main; both report `protected:false`; repository rulesets are empty.
- Re-read root `AGENTS.md`, this plan, frozen 26-Oct inventory, Unified Master Implementation Plan, RK45 source and registered browser regressions. Historical baseline remains **166 gaps / 95 partial**.
- P0 exact-head failure: Push Quality [#46014476843](https://github.com/saeedsai/ProMathStudio/actions/runs/46014476843) and PR Quality [#46014485667](https://github.com/saeedsai/ProMathStudio/actions/runs/46014485667) both failed at step 181, `RK45 stage-time precision warning, recovery and mobile regression`. The failing assertion in `tests/smoke_ode_rk45_stage_resolution.py` expected obsolete text `stage times rounded to current t`; actual output correctly says `repeated or endpoint-collapsed RK45 stage times`. Other RK45 endpoint/diagnostic browser steps passed.
- The previous exact-head `b6c5358` was green in both Push and PR Quality (218/218, zero failures/skips). This does not certify `820d5c0`.
- Correction on dev: pluralize the UI warning as `1 accepted step had` versus `2 accepted steps had`; update the stale forward/backward browser assertions and assert the 20-ULP case uses the plural form. Source and standalone `index.html` are updated together; docs, this plan, ledger and changelog record the change. No solver numerics, collision counts, CI gates or test scope are weakened.
- Release PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191) remains open/mergeable, 108 commits ahead / 0 behind, 44 changed files, zero independent reviews. No branch protection/rulesets are verifiably enabled; no merge or direct main update.
- Main remains `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`. Latest known successful production Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) are from 24-Nov-2026; no newer main deployment/live verification is claimed.
- Status: warning grammar and stale test repair implemented on dev; fresh exact-head Push/PR Quality required. Native local Python/Playwright/build remain unavailable because the execution container has no checkout; isolated V8 and source/bundle parity checks are performed for this commit.
- NEXT FIVE remain: (1) safe PR #191 review/protection/release; (2) saved-project compatibility and stage-by-stage rollback; (3) Data Tables numerical/XLSX integrity; (4) seven-shape Truss FEM reference/boundary matrix; (5) RK45 difficult-workload boundaries and stale-export protection.
