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

