# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 14:01 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this file records current implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- The unified roadmap and discipline catalogs contain overlapping aliases; count canonical calculations and user-visible workflows once.

## Current repository and release checkpoint

- Starting `dev`: `d4ff4a8f7e042ac6c8dcbe5c44e6d725238f8d1a`; this run corrects the preceding multi-file assembly and advances the existing branch with one guarded atomic commit.
- `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare before this change: **106 ahead / 0 behind**.
- Existing PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191): `dev` → `main`, open and mergeable, 106 commits ahead / 0 behind, 44 changed files, zero submitted independent reviews.
- Branch inventory: exactly `dev` and `main`; both currently report `protected: false`. Rulesets are empty; branch-protection GET returns HTTP 403 to the connected integration.
- Exact starting-head Quality on `72e4400dbd05ebacdcc07efdae346bee297f0b75`: Push [#45992199344](https://github.com/saeedsai/ProMathStudio/actions/runs/45992199344) and PR [#45992207118](https://github.com/saeedsai/ProMathStudio/actions/runs/45992207118) both completed **218/218 steps, success, zero failures and zero skips**. These certify the starting head only; this commit needs fresh exact-head checks.
- The following candidate `d4ff4a8f7e042ac6c8dcbe5c44e6d725238f8d1a` failed structural step 7 in Push [#46005872653](https://github.com/saeedsai/ProMathStudio/actions/runs/46005872653) and PR [#46005881496](https://github.com/saeedsai/ProMathStudio/actions/runs/46005881496): the standalone module was updated but the modular src/ode-tools.js blob was accidentally left at its prior content. The resulting source/bundle parity and ODE extraction regressions are diagnosed; this correction copies the embedded module back to source and adds explicit fixture proofs. No test or workflow is being weakened.
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

**Status:** Blocked by zero independent reviews and unavailable/unverified enforceable branch protection. Exact-head CI on d4ff also exposed an incomplete source/bundle commit assembly; this run restores parity and reruns the focused regressions on a new exact head.  
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

**Status:** Partial; overflow advisories, bounded-stage recovery, subnormal-span initialization and repeated-stage diagnostics are implemented in the standalone bundle. The d4ff candidate failed source/bundle parity because the modular source blob was omitted; this run synchronizes it and strengthens the forward/backward 20-ULP fixture.  
**Acceptance tests:**
- Recoverable stage-overflow retries preserve a finite solution when smaller steps succeed; unrecoverable overflow terminates with a diagnostic.
- Forward/backward sample times are strictly monotone with no duplicate timestamps at large epochs or near-ULP spacing.
- When `span/20` underflows to zero but the requested endpoints are distinct, the solver uses one full representable span; smallest- and two-subnormal intervals in both directions preserve the endpoint, report collapsed stages and show the accuracy warning.
- At 1e12, a 20-ULP interval in both directions exercises a 5-ULP trial where c=4/5 and c=8/9 round to the same timestamp; both collision counters must report the accepted repeated-stage attempt without changing the endpoint grid.
- Underflow, maximum attempts, exhausted retries, endpoint snapping and stale-export protection have direct numerical and browser regressions.
- Data Tables/Graph exports, keyboard behavior and 390px layout remain correct.

## Following queue

After the five priorities above, continue shared-tool registry and canonical toolbox deduplication, then extend the verified engineering solver catalog without creating duplicate implementations or claiming planned entries as shipped.

## Latest checkpoint

- Starting refs: dev d4ff4a8f7e042ac6c8dcbe5c44e6d725238f8d1a; main 0d8ac89f7c9177806a266e56b27980c83d2c3ff5; 106 ahead / 0 behind. PR #191 is open/mergeable, 106 commits ahead, 44 changed files, zero independent reviews. Only dev/main branches exist; both report unprotected, rulesets are empty and branch-protection GET returns 403 to the integration.
- The previous exact-head RK45 browser assertion failure on 333124 was traced to multiplying two subnormal quantities in the monotonicity check; that check was corrected to signed direction times the timestamp difference.
- The subsequent candidate d4ff4a8f7e042ac6c8dcbe5c44e6d725238f8d1a failed structural step 7 in Push [#46005872653](https://github.com/saeedsai/ProMathStudio/actions/runs/46005872653) and PR [#46005881496](https://github.com/saeedsai/ProMathStudio/actions/runs/46005881496). Root cause: the Git tree updated index.html but accidentally retained the old src/ode-tools.js blob, producing source/bundle parity failures and dependent ODE extraction test failures (20 structural test failures total). This is an assembly omission, not a workflow problem; no tests were weakened.
- This correction sets src/ode-tools.js to the exact embedded promath-ode-tools module from index.html, so the existing standalone behavior and source become identical. Node and Chromium tests now also prove the forward/backward 5-ULP fixture really maps c=4/5 and c=8/9 to the same binary64 timestamp before asserting two collision reports.
- The previous d4ff tree already contains the synchronized standalone module, repaired subnormal monotonicity assertion, browser/Node collision assertions, docs, plan, ledger and changelog. This corrective commit updates the modular source and both focused tests plus the living records together; source/bundle parity is rechecked before commit.
- Isolated V8 checks on the embedded production module passed smallest/two-subnormal intervals and 20-ULP large-epoch forward/backward intervals, with exact endpoints, monotonic timestamps, two collision counts and one quantum-limited step in each direction. Native Python/Playwright/build remain unavailable without a checkout. New exact-head CI is required after this correction.
- Release remains blocked: PR #191 has zero independent reviews; main protection is not verifiable and both branches report unprotected. No merge or direct main update. Latest main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) remain successful on 24-Nov-2026 at unchanged main; no newer deployment/live verification.
- Next five: (1) exact-head Quality green and safe PR #191 review/protection/release; (2) saved-project compatibility/rollback matrix; (3) Data Tables numerical and XLSX integrity; (4) seven-shape Truss FEM reference/boundary matrix; (5) RK45 difficult-workload boundaries including repeated fractional-stage collisions, overflow recovery and stale-export protection.

