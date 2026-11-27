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

- Starting `dev`: `33312475c844d31e45ea531a2ea5b5c460ec2e9a`; this run advances the existing branch with one guarded atomic multi-file commit.
- `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare before this change: **105 ahead / 0 behind**.
- Existing PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191): `dev` → `main`, open and mergeable, 105 commits ahead / 0 behind, 44 changed files, zero submitted independent reviews.
- Branch inventory: exactly `dev` and `main`; both currently report `protected: false`. Rulesets are empty; branch-protection GET returns HTTP 403 to the connected integration.
- Exact starting-head Quality on `72e4400dbd05ebacdcc07efdae346bee297f0b75`: Push [#45992199344](https://github.com/saeedsai/ProMathStudio/actions/runs/45992199344) and PR [#45992207118](https://github.com/saeedsai/ProMathStudio/actions/runs/45992207118) both completed **218/218 steps, success, zero failures and zero skips**. These certify the starting head only; this commit needs fresh exact-head checks.
- Exact-head starting commit `33312475c844d31e45ea531a2ea5b5c460ec2e9a` fails the RK45 browser smoke at step 177 in Push [#45996382595](https://github.com/saeedsai/ProMathStudio/actions/runs/45996382595) and PR [#45996390506](https://github.com/saeedsai/ProMathStudio/actions/runs/45996390506). The arithmetic-underflow assertion root cause is diagnosed and corrected in this run; steps 1–176 passed and 178–215 were skipped after the failure.
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

**Status:** Blocked by zero independent reviews and unavailable/unverified enforceable branch protection. The starting head also had an RK45 endpoint-smoke assertion failure; its arithmetic-underflow root cause is corrected in this run and fresh exact-head CI is pending.  
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

**Status:** Partial; overflow advisories, bounded-stage recovery, subnormal-span initialization and near-ULP diagnostics exist. This run extends collision reporting to repeated fractional-stage timestamps and repairs the subnormal monotonicity assertion; exact-head CI is pending.  
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

- Starting refs: dev 33312475c844d31e45ea531a2ea5b5c460ec2e9a; main 0d8ac89f7c9177806a266e56b27980c83d2c3ff5; 105 ahead / 0 behind. PR #191 is open/mergeable, 105 commits ahead, 44 changed files, zero independent reviews. Only dev/main branches exist; both report unprotected, rulesets are empty and branch-protection GET returns 403 to the integration.
- Exact-head Push Quality [#45996382595](https://github.com/saeedsai/ProMathStudio/actions/runs/45996382595) and PR Quality [#45996390506](https://github.com/saeedsai/ProMathStudio/actions/runs/45996390506) both failed at step 177, RK45 large-epoch endpoint precision and underflow browser regression. The browser assertion multiplied the tiny interval by its tiny timestamp increment; for the smallest subnormal this product underflowed to zero despite strictly increasing timestamps. Steps 1–176 passed; steps 178–215 were skipped after the failure. No production solver failure was shown by this assertion.
- The same investigation found a real diagnostic gap: the solver counted fractional stages rounded back to the current time, but not two fractional stages rounded to the same intermediate timestamp or a stage rounded to the next endpoint. The source now reuses exact stage-time variables for evaluation and counts collisions against both endpoints and preceding fractional stages. Endpoint derivative stages use the selected nextT directly.
- Added a Node regression and registered Chromium case for forward/backward 20-ULP intervals near 1e12. A later 5-ULP trial makes c=4/5 and c=8/9 coincide; expected accepted collision counters are 2. Corrected the subnormal browser monotonicity assertion to multiply the signed direction (±1) by the timestamp difference, avoiding underflow while retaining strict monotonicity.
- Updated src/ode-tools.js, its standalone index.html module, both RK45 tests, docs/NUMERICAL_AND_PYTHON.md, this plan, the full execution ledger and CHANGELOG.md in one atomic commit. Frozen inventory remains 166 gaps / 95 partial.
- Isolated V8 executed the actual modified solver kernel: smallest/two-smallest subnormal intervals passed in both directions; 20-ULP forward/backward cases each reported exactly two accepted stage-collision attempts and one quantum-limited step; endpoint monotonicity and work counters passed. Modular source and embedded standalone module matched exactly. Native Python/Playwright/build commands remain unavailable without a checkout; new exact-head Actions must certify the committed browser regression.
- Release remains blocked: PR #191 has zero independent reviews; main protection is not verifiable and both branches report unprotected. No merge or direct main update. Latest main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) remain successful on 24-Nov-2026 at unchanged main; no newer deployment/live verification.
- Next five remain: (1) complete exact-head CI and safe PR #191 governance/release; (2) finish saved-project compatibility/rollback matrix; (3) Data Tables numerical and XLSX integrity; (4) seven-shape Truss FEM reference/boundary matrix; (5) RK45 difficult-workload boundaries including repeated fractional-stage collisions, overflow recovery and stale-export protection.

