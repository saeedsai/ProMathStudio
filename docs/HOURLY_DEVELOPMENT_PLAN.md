# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 12:54 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this file records current implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- The unified roadmap and discipline catalogs contain overlapping aliases; count canonical calculations and user-visible workflows once.

## Current repository and release checkpoint

- Starting `dev`: `72e4400dbd05ebacdcc07efdae346bee297f0b75`; this run advances the existing branch with one guarded atomic multi-file commit.
- `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare before this change: **104 ahead / 0 behind**.
- Existing PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191): `dev` → `main`, open and mergeable, 104 commits ahead / 0 behind, 40 changed files, zero submitted independent reviews.
- Branch inventory: exactly `dev` and `main`; both currently report `protected: false`. Rulesets are empty; branch-protection GET returns HTTP 403 to the connected integration.
- Exact starting-head Quality on `72e4400dbd05ebacdcc07efdae346bee297f0b75`: Push [#45992199344](https://github.com/saeedsai/ProMathStudio/actions/runs/45992199344) and PR [#45992207118](https://github.com/saeedsai/ProMathStudio/actions/runs/45992207118) both completed **218/218 steps, success, zero failures and zero skips**. These certify the starting head only; this commit needs fresh exact-head checks.
- The previous exact-head failures on `905a864` (project rollback step 50) and `3139890` (structural delivery-plan heading step 7) were diagnosed and corrected in the current starting head; no current failing check remains.
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

**Status:** Blocked by zero independent reviews and unavailable/unverified enforceable branch protection; current starting-head CI is green.  
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

**Status:** Partial; overflow advisories, bounded-stage recovery and near-ULP diagnostics exist. This run fixes the distinct representable-subnormal-span case where the initial `span/20` split rounded to zero; candidate CI remains pending.  
**Acceptance tests:**
- Recoverable stage-overflow retries preserve a finite solution when smaller steps succeed; unrecoverable overflow terminates with a diagnostic.
- Forward/backward sample times are strictly monotone with no duplicate timestamps at large epochs or near-ULP spacing.
- When `span/20` underflows to zero but the requested endpoints are distinct, the solver uses one full representable span; smallest- and two-subnormal intervals in both directions preserve the endpoint, report collapsed stages and show the accuracy warning.
- Underflow, maximum attempts, exhausted retries, endpoint snapping and stale-export protection have direct numerical and browser regressions.
- Data Tables/Graph exports, keyboard behavior and 390px layout remain correct.

## Following queue

After the five priorities above, continue shared-tool registry and canonical toolbox deduplication, then extend the verified engineering solver catalog without creating duplicate implementations or claiming planned entries as shipped.

## Latest checkpoint

- Starting `dev`: `72e4400dbd05ebacdcc07efdae346bee297f0b75`; starting `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`. The branch comparison is 104 ahead / 0 behind. The existing PR #191 is open and mergeable with 104 commits, 40 changed files and zero independent submitted reviews.
- Exact starting-head Push Quality [#45992199344](https://github.com/saeedsai/ProMathStudio/actions/runs/45992199344) and PR Quality [#45992207118](https://github.com/saeedsai/ProMathStudio/actions/runs/45992207118) both completed all 218 steps successfully, with zero failed or skipped steps. No starting-head CI failure remains to repair.
- Main and dev are the only branches; both report `protected: false`, and the repository rulesets endpoint returns an empty list. PR #191 remains blocked by missing independent review and enforceable main protection. No merge is authorized.
- Found an RK45 initial-step defect: for a distinct representable subnormal interval such as `[0, Number.MIN_VALUE]`, `span/20` rounded to zero and the solver returned step underflow before its first attempt. It now falls back to the full representable span only in that case. Existing stage-collision diagnostics remain visible; this is not an accuracy guarantee for a time-varying derivative.
- Added direct Node regression for smallest- and two-subnormal forward/backward intervals, exact endpoints, monotonicity, attempt counts and collision warnings; extended the registered Chromium endpoint smoke with the same cases. Updated numerical-method documentation. Source and embedded standalone `index.html` module are synchronized.
- Isolated V8 execution of the actual modified solver kernel reproduced the old failure and passed all four new intervals plus the constant-state check. Candidate exact-head Push/PR Quality must still run; browser certification is pending.
- Latest main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages deployment [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) remain successful on 24-Nov-2026 at unchanged main. No newer deployment or live hosted verification is claimed.
- Historical baseline remains **166 gaps / 95 partial**. No inventory counts were changed.
