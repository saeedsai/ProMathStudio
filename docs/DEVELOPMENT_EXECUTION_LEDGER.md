## 2026-11-25 — Data Tables sort validator regex CI repair

Starting dev `09cfeb6e971b67f390f4390d9f8cd280a1f2f2b2`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`. Exact Quality #45522925339 failed structural step 7: Node syntax validation rejected the new sort helper's over-escaped regex (one failure in 600 tests; browser steps skipped after the structural job failed). The failure was read from the exact job log, not inferred.

Corrected the regex to the same single-backslash JavaScript literal used by the existing spreadsheet reference validator. Added a structural assertion for the exact regex spelling. Preserved the range/blank-row behavior and synchronized standalone index.html with src/data-tables.js. The previous starting-head Quality #45515170826 was green 218/218.

Corrected regex cases: A1, $A$1 and AF6000 accepted; AG1, A6001 and A0 rejected. Remote source/bundle parity checked. Local checkout is absent; full local tests unavailable. New exact-head Quality pending; no test weakening or release bypass. Historical inventory unchanged at 166 gaps / 95 partial.

**NEXT FIVE:** (1) P0 release governance: enforceable main protections, independent review, ordinary PR, exact checks and Pages verification. (2) P1 spreadsheet structural correctness: corrected sort CI, row-6000/column-AF boundaries, #REF!, blank/reversed/mixed-anchor ranges, failed-insert and noncontiguous-sort atomicity, desktop/390px. (3) P1 current/legacy Matrix/Graph/Table round-trips and malformed-import rollback. (4) P1 ODE analytical forward/backward references, convergence, unsupported classes, stale exports and mobile recovery. (5) P1 seven-shape Truss thin-wall/subnormal/high-scale references, invalid rollback and desktop/390px.

## 2026-11-25 — Data Tables sort preserves invalid and blank-grid references

Starting dev `a7251d6cf2650b778db8d9abc15fba998ecf021d`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; dev Quality [#45515170826](https://github.com/saeedsai/ProMathStudio/actions/runs/45515170826) passed 218/218 with zero failures/skips. Main Quality #45360386408 passed 218/218; Pages #45360367251 build/status/deploy all succeeded. No open PRs; only dev/main. Rulesets empty; main protection read HTTP 403.

Fixed Data Tables stable sorting at the supported grid boundary. Sort now leaves invalid scalar/range references outside A1:AF6000 unchanged, keeps valid blank cells beyond the materialized table at fixed coordinates, and still rejects a range whose mapped rows become noncontiguous. Added a registered browser regression for full-grid and blank ranges, invalid AG/A6001 references, reversed mixed-anchor ranges and calculated values; added a structural unittest and clarified DATA_TABLES.md. Updated both modular source and standalone index.html in one tree.

Isolated V8 range-mapping checks passed for full-grid, blank-cell, invalid-reference, reversed-anchor and noncontiguous cases. Local Python/Chromium and build checks are unavailable because this execution runtime has no Git checkout; new exact-head Quality is pending. Implemented on dev only, not released. Frozen inventory unchanged at 166 gaps / 95 partial.

**NEXT FIVE:** (1) P0 release governance: enforceable main protection, independent review, ordinary PR, exact checks and Pages verification. (2) P1 spreadsheet structural correctness: row-6000/column-AF edges, #REF!, blank-grid and reversed/mixed-anchor sorting, failed-insert and noncontiguous-sort atomic rollback, desktop/390px. (3) P1 current/legacy Matrix/Graph/Table project round-trips and malformed-import rollback. (4) P1 ODE analytical forward/backward references, convergence, unsupported classes, stale exports and mobile recovery. (5) P1 remaining seven-shape Truss thin-wall/subnormal/high-scale property references and desktop/390px tests.

## 2026-11-25 — Data Tables row-insertion preflight atomicity

Starting dev `58a5f8d008268413080cc2594665fb9277bf2c32`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; exact starting dev Quality [#45506851043](https://github.com/saeedsai/ProMathStudio/actions/runs/45506851043) passed 218/218 with zero failures/skips. Main Quality #45360386408 and Pages #45360367251 succeeded on current main. No open PRs; only dev/main. Rulesets empty; protection reads HTTP 403.

Fixed a partial-mutation path in Data Tables row insertion: caller cell values are now converted/truncated into a complete row before workbook-wide formula-reference rewriting. A throwing value conversion or invalid row shape therefore cannot shift cross-sheet formulas without inserting the row. Added a Chromium regression asserting the error and exact exported-workbook rollback, plus a structural unittest for preflight ordering. Updated Data Tables guide, living plan and changelog; root standalone bundle remains synchronized with `src/data-tables.js`.

The local runtime has no Git checkout, so local Python/Chromium commands were unavailable. Current dev Quality is green; the new exact-head run is pending. Implemented on dev, not released. Historical inventory remains frozen at 166 gaps / 95 partial.

**NEXT FIVE:** (1) P0 release governance: verifiable main protections, independent review, ordinary PR, exact checks and Pages verification. (2) P1 spreadsheet structural correctness: row-6000/column-AF edges, #REF!, reversed ranges, mixed anchors, failed-insert atomicity, rejected-sort rollback and 390px. (3) P1 current/legacy Matrix/Graph/Table project round-trips with malformed-import rollback and focus/mobile checks. (4) P1 ODE forward/backward references, convergence, unsupported classes, stale exports and mobile recovery. (5) P1 remaining seven-shape Truss thin-wall/subnormal/high-scale property references and desktop/390px checks.

## 2026-11-24 — TRUSS-COMPOSITE-AXIS-SEPARATED-SCALE-RECOVERY

Starting dev `540d86ad81b6b92269c2bb4b26a04b767fa289d8`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; exact starting dev Quality #45487505257 green **218/218**, zero failures/skips; main Quality #45360386408 and Pages #45360367251 successful. No open PRs; only dev/main; dev 16 ahead/0 behind. Both branches unprotected, rulesets empty, protection reads HTTP 403.

Fixed channel/I-section extreme-aspect property loss when max(B,H)-only normalized Ixx underflowed despite representable physical subnormal Ixx, rx and Sx. Added an axis-separated x/B, y/H normalized rectangle tensor fallback only when the common-scale area/inertias fall below normal binary64; dimensional area/inertias and ordinary common-scale paths remain unchanged. Exponent-scaled products restore Sx/Sy without intermediate range loss. Added direct Node and mandatory 1280px/390px Chromium exact-binary64/120-digit Decimal regressions for B=1e150, H=1e-154, tw=1e-154, tf=4.9e-155; old rx/Sx errors >1e-11 are reproduced and corrected rx/ry/Sx/Sy match within 5e-13. Input immutability/frozen outputs and ordinary I/c parity covered. Actual modified production module passed isolated V8 checks within 2.3e-16; full Node/Chromium awaits new exact-head Quality. Updated Structural Truss guide, living plan and changelog. Implemented on dev, not released. Historical baseline unchanged at 166 gaps / 95 partial.

**NEXT FIVE (priority, status and acceptance tests):**
1. **P0 — Release governance (blocked):** obtain admin-verifiable main protection requiring exact-head Quality and forbidding direct push/force/deletion, plus eligible independent approval; then use one ordinary dev→main PR and verify PR checks, main Quality, Pages deployment and hosted critical paths.
2. **P1 — Finish seven-shape Truss property audit (in progress):** complete remaining thin-wall/subnormal/high-scale references across rectangle, hollow rectangle, circles, channel, I-section and L-angle; verify area, centroid, inertias, principal properties, Sx/Sy and rx/ry, invalid rollback, selected-member isolation and 1280px/390px Chromium.
3. **P1 — Spreadsheet grid-edge structural references:** row 6000/column AF insertion/deletion and #REF! recovery, reversed ranges, mixed anchors, rejected-sort byte-for-byte rollback and desktop/390px checks.
4. **P1 — Saved-project compatibility:** current/legacy Matrix, Graph and Table round-trips; malformed imports preserve all workspaces, selections and prior results at desktop/390px.
5. **P1 — ODE solver verification:** analytical forward/backward IVPs, unsupported-class diagnostics, tolerance/step convergence, stale-export invalidation and desktop/390px recovery.

## 2026-11-24 — TRUSS-COMPOSITE-SUBNORMAL-SECTION-MODULUS

Starting dev `de0ccc300fd81ceb72dfaecbd55aef1a46780f78`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; exact dev Quality #45477244278 green **218/218**, zero failures/skips; main Quality #45360386408 and Pages #45360367251 successful. No open PRs; only dev/main; dev 15 ahead/0 behind. Both refs unprotected, rulesets empty, protection reads HTTP 403.

Fixed channel/I-section Sx/Sy precision when dimensional Ixx/Iyy are subnormal. Reuse normalized composite inertias and normalized extreme-fibre distances to evaluate L³·I/c without dividing quantized physical inertias. Old errors: Sx -5.15% for both, channel Sy +23.90%, I-section Sy -6.85%. Added Node and registered Chromium 1280px/390px exact-binary64/120-digit Decimal regressions, immutability and frozen-output checks. Updated Truss guide, living plan and changelog. Independent Decimal and isolated V8 normalized calculations matched references within 5e-16; full Node/Chromium run awaits exact-head GitHub Quality because no local checkout is available. Implemented on dev, not released. Historical baseline unchanged at 166 gaps / 95 partial.

**NEXT FIVE:** (1) P0 release governance: verifiable main protections, eligible independent review, ordinary PR, exact checks and Pages verification. (2) P1 finish seven-shape Truss thin-wall/subnormal/high-scale audit with independent references, invalid rollback, selected-member isolation and desktop/390px tests. (3) P1 spreadsheet row-6000/column-AF grid-edge insert/delete, #REF! recovery, mixed anchors, reversed ranges and atomic rollback. (4) P1 current/legacy Matrix/Graph/Table round-trips with malformed-import rollback and focus/mobile checks. (5) P1 ODE analytical forward/backward references, convergence, unsupported classes, stale exports and mobile recovery.

## 2026-11-24 — TRUSS-CIRCULAR-SUBNORMAL-SECTION-MODULUS

Starting dev b433c0db406e72a74488fd2c20fd4d473af81b29, main 0d8ac89f7c9177806a266e56b27980c83d2c3ff5; exact starting dev Quality #45467047779 green 218/218; main Quality #45360386408 and Pages #45360367251 successful. No open PRs; only dev/main; dev 14 ahead/0 behind. Both refs unprotected, rulesets empty, protection read HTTP 403.

Fixed solid/hollow circle Sx/Sy when I is subnormal: use (π/32)·Do³·inertiaFactor with the existing factored annulus term only below the normal-inertia threshold. Old I/c overestimated the solid and hollow references by 24.3% and 32.5%; corrected production-module results match independent 120-digit Decimal values. Ordinary 40 mm circle path unchanged. Added Node and registered Chromium 1280px/390px regressions; source, tests, Structural Truss guide, living plan and changelog updated atomically. Actual modified module passed isolated V8 checks for subnormal cases, ordinary circle parity, immutability and invalid annulus rejection. New exact-head Quality pending; no local full Node/Chromium suite. Implemented on dev, not released. Historical inventory unchanged at 166 gaps / 95 partial.

**NEXT FIVE:**
1. P0 release governance — required main protections, independent review, ordinary PR, exact-head checks and Pages verification.
2. P1 seven-shape Truss boundary audit — independent thin-wall/subnormal/high-scale references, invalid rollback and desktop/390px.
3. P1 spreadsheet grid edges — row 6000/column AF, #REF!, mixed anchors, reversed ranges, atomic rollback.
4. P1 saved-project compatibility — current/legacy Matrix/Graph/Table round-trip and malformed-import rollback.
5. P1 ODE verification — analytical forward/backward IVPs, convergence, unsupported classes and mobile recovery.
## 2026-11-24 — TRUSS-RECTANGULAR-SUBNORMAL-SECTION-MODULUS

Starting dev `9f07a13caa491175a466cd32e8484039e6d6a4e0`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; exact starting dev Quality #45457066031 green 218/218; main Quality #45360386408 green; Pages #45360367251 successful. No open PRs; only dev/main; dev 13 ahead/0 behind. Both branches unprotected, rulesets empty, protection read HTTP 403; integration exposes no protection-write action.

Fixed solid/hollow rectangle Sx/Sy precision when Ixx/Iyy are subnormal but section moduli are representable. Use existing dimensionless factors directly only on affected subnormal-inertia axes rather than dividing rounded I/c; normal-inertia paths remain unchanged. Added Node and registered Chromium 1280px/390px regressions with exact-binary64/120-digit Decimal references, old-error reproduction, and immutability checks. Updated Structural Truss guide, hourly plan and changelog. Isolated actual-source V8 checks passed for both new cases and ordinary 40×60 mm rectangle. Full local Node/Chromium unavailable without checkout; new exact-head Quality pending. Implemented on dev, not released. Historical inventory unchanged at 166 gaps / 95 partial.

**NEXT FIVE (priority, status, acceptance tests):**
1. **P0 — Release governance (blocked):** obtain admin-verifiable main protection requiring Quality, prohibiting direct pushes/force/deletion, and eligible independent review; then use one ordinary dev→main PR, verify exact-head PR checks, merge normally, and confirm new main SHA, main Quality, Pages deployment and hosted critical paths.
2. **P1 — Finish the seven-shape Truss property-boundary audit:** for rectangle, hollow rectangle, solid/hollow circle, channel, I-section and L-angle, verify area, centroid, Ixx/Iyy/Ixy, principal moments/axis, Sx/Sy and rx/ry against independent high-precision thin-wall/subnormal/high-scale references; invalid/unrepresentable geometry must reject without member mutation; Chromium must pass at 1280px/390px.
3. **P1 — Spreadsheet grid-edge structural references:** insert at row 6000/column AF and delete/recover #REF!, cover reversed ranges and mixed absolute anchors, and assert byte-for-byte workbook rollback after invalid/noncontiguous sort at desktop/390px.
4. **P1 — Saved-project compatibility:** current/legacy Matrix, Graph and Table round-trips; malformed-import rollback must preserve every workspace, selection and prior result; verify desktop/390px browser behavior.
5. **P1 — ODE solver verification:** analytical forward/backward IVP references, unsupported-class diagnostics, tolerance/step convergence, stale-export invalidation and desktop/390px error recovery.



---

