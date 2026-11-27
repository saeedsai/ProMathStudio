# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 10:57 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this file records current implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- The unified roadmap and discipline catalogs contain overlapping aliases; count canonical calculations and user-visible workflows once.

## Current repository and release checkpoint

- Starting `dev`: `905a864a480646849ef97b60792a0dc99f500306`.
- `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`.
- Existing PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191): `dev` → `main`, open and mergeable, 100 commits ahead / 0 behind, 38 changed files, zero submitted independent reviews.
- Branch inventory: exactly `dev` and `main`; no additional branch was found after pagination.
- Current exact-head candidate `905a864` is **failing**, not green: Push Quality [#45972027670](https://github.com/saeedsai/ProMathStudio/actions/runs/45972027670) and PR Quality [#45972038530](https://github.com/saeedsai/ProMathStudio/actions/runs/45972038530) both fail at step 50, Project migration and rollback browser regression.
- Failure diagnosis: the test compares rollback output to a stale `migrated['solver']` snapshot from an earlier SymPy limit import. Subsequent valid Graph imports use the legacy fixture and intentionally restore its original solver settings. The rollback expectation must snapshot the solver state immediately before the injected restore failure; the earlier valid solver round-trip assertions remain.
- This run also aligns saved `solver.variable` validation with the live CAS identifier grammar, adding a bounded Unicode identifier contract and negative cases.
- Branch-protection read returns HTTP 403 to the connected integration; repository rulesets read is empty. Do not merge until required exact-head checks, independent review and enforceable release safeguards are verified.
- Latest verified production runs remain Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251), both successful on 24-Nov-2026 at the unchanged main SHA. No newer main deployment is verified.

## Operating contract

1. Read root `AGENTS.md`, this plan, the frozen audit, unified master plan, relevant architecture/catalog contracts and exact-head CI before choosing work.
2. Work only on existing `dev`; preserve the standalone offline `index.html` and synchronize every modular source change with its embedded module via the canonical build contract.
3. Every source change has direct automated positive, negative and boundary regression coverage. Keep browser smoke registration and full Quality gates enabled.
4. Commit source, synchronized bundle where applicable, tests, documentation, this plan, execution ledger and changelog together in one bounded atomic dev commit.
5. Inspect exact-commit Push and PR checks; read failing logs and repair root causes without removing assertions or weakening checks.
6. Merge only through the ordinary `dev`→`main` PR after full exact-head Quality, required review and enforceable protections are verified. Then verify main Quality, Pages deployment and hosted critical paths.
7. Maintain the historical 166-gap / 95-partial baseline until evidence supports a separately documented re-audit.

## NEXT FIVE priorities

### 1. P0 — Repair and certify saved-project rollback / solver validation

**Status:** Implemented on dev in the current atomic checkpoint; exact-head CI pending.  
**Acceptance tests:**
- Node schema tests accept 144 valid operation/engine/direction combinations, valid 24-character and Unicode solver identifiers, and empty/missing legacy selectors.
- Reject invalid operation/engine/direction, non-identifier variables, wrong types, variable length 25, limit-point length 81 and contradictory assumptions.
- Chromium imports a valid Unicode solver variable and verifies its operation, engine, direction, expression and initial conditions.
- Inject a restore-stage failure after notebook mutation; compare the post-rollback solver snapshot to the actual pre-failure snapshot, while retaining notebook/workbook/Graph/Matrix/fit/custom-function rollback assertions.
- Exact-head Push and PR Quality both pass all required steps with zero failures/skips; specifically steps 7 and 50, then all remaining browser and Quality steps.

### 2. P0 — Release PR #191 safely

**Status:** Blocked by failing exact-head CI, zero independent reviews and unverified branch protection.  
**Acceptance tests:**
- Full Push and PR Quality pass on the exact PR head; no skipped required tests.
- Complete PR diff and review threads are inspected; an eligible independent reviewer approves.
- Main protection/rules require the relevant Quality checks and disallow direct pushes/force updates; verify through GitHub rather than documentation.
- Merge only via GitHub's ordinary PR merge operation. Verify resulting main SHA, main Quality, Pages build/deployment and live application boot plus project save/import smoke.

### 3. P1 — Complete saved-project compatibility

**Status:** Partial; several state slices have schema and rollback tests, but whole-workspace compatibility is not fully certified.  
**Acceptance tests:**
- v1→v2 migration and v2 round-trips preserve notebook, calculator, Equation/Solver, assumptions, Matrix drafts, Graph primary/overlay datasets, Curve fit, Data Tables workbook/selection, Engineering filters and custom functions.
- Missing optional legacy fields preserve documented defaults; unsupported enums/versions, malformed cells, invalid IDs and over-limit values reject before mutation.
- Inject failure after each restore stage and verify state rollback; test desktop and 390px mobile with no console errors and exact source/bundle parity.

### 4. P1 — Complete Data Tables numerical and file integrity

**Status:** Partial; recent PRODUCT, signed-zero, large MIN/MAX, compensated SUM/AVERAGE and XLSX import/export fixes are implemented on dev but release verification is pending.  
**Acceptance tests:**
- PRODUCT direct/nested/range, negative zero, exponent scaling, empty identity, overflow and underflow against independent binary64 references.
- MIN/MAX over 132,000 values; SUM/AVERAGE cancellation and subnormal residual references.
- A1:AF6000 structural references, mixed/absolute anchors, quoted names, sort/delete/undo reference integrity.
- XLSX ZIP metadata, CRC, size, formula-token boundaries, corrupted archive rejection and preservation of the pre-import workbook.
- Browser, keyboard, 390px and source/bundle parity regressions pass.

### 5. P1 — Finish seven-shape Truss FEM numerical boundaries

**Status:** Partial; numerical hardening exists, but the complete seven-shape acceptance matrix and release evidence remain open.  
**Acceptance tests:**
- Independent area, centroid, Ixx/Iyy, section modulus and radius references for solid/hollow rectangles, solid/hollow circles, channel, I-section and L-angle.
- Thin-wall and cavity-transition limits, sub-ULP contributions, mixed-scale compensated stiffness assembly, mechanism/singularity rejection and SI conversion boundaries.
- Equilibrium residual, strain energy, displacement and member-force references; invalid-input rollback and 390px keyboard/mobile checks.

## Following queue

After the five priorities above, continue adaptive RK45 hardening: recoverable stage-overflow retries, forward/backward monotone near-ULP sample times, duplicate-time prevention, underflow, exhaustion, stale-export protection and responsive browser tests.

## Latest checkpoint

- Starting heads and CI failure are recorded above; this run's resulting atomic commit SHA and new exact-head Actions results are reported in the execution ledger/PR progress comment.
- Main and Pages remain unchanged; no release is claimed.
- Historical baseline remains **166 gaps / 95 partial**.
