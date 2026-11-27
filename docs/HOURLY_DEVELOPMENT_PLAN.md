# ProMathStudio — Hourly Development Plan

**Last updated:** 27 November 2026, 14:58 CET  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Development branch:** `dev` · **Release branch:** `main`

This is the living execution queue. The 26-Oct audit remains the frozen historical baseline; this file records current implementation and verification state without rewriting historical counts.

## Frozen baseline and accounting

- Historical audit: **166 gaps / 95 partial** (26 October 2026).
- Preserve the original feature IDs, scope and distinctions in `docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md`.
- Do not infer completion from module names, catalog entries or the ability to write a formula in Python.
- The unified roadmap and discipline catalogs contain overlapping aliases; count canonical calculations and user-visible workflows once.

## Current repository and release checkpoint

- Current `dev`: `b6c535854313b41406be355b4d06d633d003285b`; `main`: `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; compare: **107 ahead / 0 behind**.
- Existing PR [#191](https://github.com/saeedsai/ProMathStudio/pull/191): `dev` → `main`, open and mergeable, 107 commits ahead / 0 behind, 44 changed files, zero submitted independent reviews.
- Branch inventory: exactly `dev` and `main`; both currently report `protected: false`. Rulesets are empty; branch-protection GET returns HTTP 403 to the connected integration.
- Exact-head Quality on `b6c535854313b41406be355b4d06d633d003285b`: Push [#46006460898](https://github.com/saeedsai/ProMathStudio/actions/runs/46006460898) and PR [#46006469595](https://github.com/saeedsai/ProMathStudio/actions/runs/46006469595) both completed **218/218 steps, success, zero failures and zero skips**. The RK45 endpoint browser regression and all remaining Quality checks passed on this exact head.
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

**Status:** Exact-head Push and PR Quality are green on b6c5358 (218/218 steps each, zero failures/skips). Promotion remains blocked by zero independent reviews and unavailable/unverified enforceable main protection. The d4ff source/bundle assembly failure was corrected and the corrected head is fully certified.  
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

**Status:** Partial; bounded-stage recovery, subnormal-span initialization and repeated-stage diagnostics are implemented on dev. Exact-head Quality is green on b6c5358. This run corrects the result-panel wording: collision counters include repeated fractional timestamps and stages rounded to either endpoint, not only stages rounded to current t. Remaining overflow, attempt-budget and stale-export boundaries stay in the acceptance matrix.  
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

- Verified starting refs: dev `b6c535854313b41406be355b4d06d633d003285b`; main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; **107 ahead / 0 behind**. PR #191 is open/mergeable, 107 commits ahead, 44 changed files, zero independent reviews. Only dev/main branches exist; both report unprotected, rulesets are empty and branch-protection GET returns 403 to the integration.
- Exact-head Push Quality [#46006460898](https://github.com/saeedsai/ProMathStudio/actions/runs/46006460898) and PR Quality [#46006469595](https://github.com/saeedsai/ProMathStudio/actions/runs/46006469595) both completed **218/218 steps successfully**, with zero failures and zero skips on `b6c535854313b41406be355b4d06d633d003285b`. This includes the RK45 endpoint Chromium regression and all remaining browser, structural and numerical checks.
- The d4ff candidate's 20 structural failures were caused by source/bundle mismatch: the standalone ODE module advanced while `src/ode-tools.js` remained old. The corrective b6c5358 commit restored exact parity; both exact-head workflows are now fully green.
- Code review found a remaining user-facing diagnostic mismatch: `stageTimeCollisionAcceptedSteps` includes duplicate fractional-stage timestamps and stages rounded onto either endpoint, but the result panel said all such stages were “rounded to current t”. This iteration changes the message to “repeated or endpoint-collapsed RK45 stage times”, adds a registered Chromium UI assertion using the forward 20-ULP case near 1e12, and updates the numerical-method contract.
- The source change is synchronized into the standalone `index.html` module. The browser regression verifies that the accepted 20-ULP run displays the accurate wording and no longer displays the misleading “rounded to current t” phrase. Exact-head CI for this new commit is pending; the b6c5358 green runs do not certify the new commit.
- PR #191 remains blocked by zero independent reviews and no verified enforceable main protection. Both refs report unprotected and rulesets are empty; no merge or direct main update.
- Main Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) remain the latest successful production runs on 24-Nov-2026 at unchanged main. No new deployment or hosted verification.
- Status: RK45 collision warning copy and Chromium regression implemented on dev; new exact-head Push/PR Quality pending; not released. Historical inventory remains **166 gaps / 95 partial**.
- Next five: (1) safe PR #191 review/protection/release; (2) saved-project compatibility and stage-by-stage rollback; (3) Data Tables numerical/XLSX integrity; (4) seven-shape Truss FEM reference/boundary matrix; (5) RK45 difficult-workload boundaries and stale-export protection.

