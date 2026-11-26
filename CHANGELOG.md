## 2026-11-26 — Align direct Matrix restore with finite solver bounds

- Hardened `MathStudio.matrixTools.restoreState()` so nonempty decimal/scientific drafts must convert to finite values with absolute magnitude at most `1e12`, matching project import; blank unfinished cells and the 80-character limit remain supported.
- Invalid A/B/RHS/weights arrays reject before any grid mutation. Added Chromium coverage for exact ±1e12 boundaries, ±1e999 overflow and ±1e13 out-of-bound values, plus structural standalone source/bundle parity.
- Implemented on dev; exact-head Push/PR Quality required; not released.

## 2026-11-26 — Validate and restore saved Graph datasets before application

- Align primary saved Graph dataset validation with the live importer: 2–32 columns, names at most 100 characters, 1–6,000 rows, and at least one finite numeric point for the persisted axes (including Z in 3D).
- Reject empty, one-column, overlong-header and unrenderable datasets before import confirmation instead of failing during restore.
- Apply saved X/Y/Z selectors before the initial series build, so valid non-default mappings work even when header-derived default columns contain text.
- Added Chromium atomic-import/round-trip regressions; legacy projects without selectors retain header-derived defaults.
- Implemented on dev; exact-head Push/PR Quality required; not released.

## 2026-11-26 — Compensated Truss preview aggregate totals

- Replaced naive member-length and SI-volume reductions in the Truss JSON preview with the existing Neumaier compensated sum, preserving low-order contributions from small members in mixed-scale models.
- Added Node and registered Chromium regressions using one 1e16 m member plus twenty 1 m members; exact aggregate length and volume remain correctly rounded while naive reductions demonstrably lose or distort the contributions.
- Existing legacy totals and genuine overflow rejection remain covered. Implemented on dev; new exact-head Push/PR Quality required; not released.

## 2026-11-26 — Data Tables stable-mean exact-rounding repair

- Fixed an exact-head CI regression where AVERAGE over numeric cells 16, 25 and 1 returned 13.999999999999998 due to divide-then-rescale rounding.
- Prefer the compensated finite total and divide once; retain normalized compensated fallback when the total overflows but the mean remains finite.
- Added exact AVERAGE/AVG range and scalar regressions plus a structural guard. Updated Data Tables numerical documentation and synchronized source with standalone index.html.
- Implemented on dev; fresh exact-head Push/PR Quality required; not released.

## 2026-11-26 — Data Tables decimal-cell CI repair

- Fixed a duplicate const declaration in range aggregation that prevented the standalone embedded Data Tables script from parsing.
- Updated the MEDIAN structural regression to verify the shared decimal-only cell parser, blank scalar compatibility and blank range exclusion.
- Re-synchronized index.html from src/data-tables.js; no test assertions or CI gates were removed. Fresh exact-head Push/PR Quality required; not released.

## 2026-11-26 — Decimal-only Data Tables cell coercion

- Prevent JavaScript radix-prefixed strings (`0x10`, `0b10`, `0o10`) from being silently treated as decimal spreadsheet numbers in direct cell arithmetic and aggregate ranges.
- Share one decimal/scientific numeric-cell parser; preserve finite numeric primitives, surrounding whitespace and blank-cell behavior. Aggregate ranges ignore radix strings as text; direct arithmetic references reject them as nonnumeric.
- Added Chromium and structural regressions while preserving existing extreme-value aggregation tests and standalone source/bundle parity.

## 2026-11-26 — Bound raw Truss numeric-string input

- Enforce the 256 UTF-16 code-unit limit before trimming, so oversized whitespace padding cannot bypass the FEM decimal/scientific input bound.
- Preserve valid padded decimal input at the exact 256-unit boundary; reject 257-unit whitespace- and zero-padded values in model parsing, solving and section-property calculations.
- Added matching Node and registered Chromium regressions, retaining all prior numeric syntax and engineering reference checks.

## 2026-11-26 — Bound Truss decimal numeric strings and repair scientific-notation regression

- Bound trimmed decimal/scientific FEM numeric strings to 256 characters before regex matching and conversion; overlong values retain the established finite-number diagnostic.
- Corrected the Node and Chromium scientific-notation reference: 1e3 kN applied to a 1e3 mm², 2 m, 200 GPa bar produces 0.01 m displacement. Radix-prefix rejection and normal decimal/scientific acceptance remain fully tested.
- Added an otherwise-finite 257-character decimal rejection regression in parse, solve and section-property inputs.
- Implemented on dev; fresh exact-head Push/PR Quality required; not released.

## 2026-11-26 — Preserve saved-table selection diagnostics while rejecting empty workbooks

- Reordered project validation so stale/null selected-sheet references retain the established error, while a zero-sheet workbook with no selection is rejected before restore.
- Updated Node table-ID/selection and Chromium atomic-import regressions; no assertions or CI gates were removed.
- Exact-head failure diagnosed and repaired on dev; fresh Push/PR Quality pending; not released.

## 2026-11-26 — Reject empty saved Data Tables workbooks

- A present saved Data Tables workspace must contain at least one sheet; malformed zero-sheet workbooks are rejected before import instead of leaving the workspace blank.
- Legacy projects that omit the optional tables object remain supported. Added Node v1/v2 and Chromium atomic-import regressions for absent/stale/null selection cases.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Reject ambiguous Graph overlay column headers

- Live Graph overlay imports and saved-project validation now reject blank or duplicate headers after trimming and case-folding, consistent with primary Graph datasets.
- Added Node and Chromium regressions for duplicate and whitespace-only names, including preservation of existing Graph data on failed live add/import.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Preserve small-cavity hollow-circle binary64 rounding

- For inner/outer diameter ratios up to 0.5, hollow-circle area and inertia factors now use the well-conditioned direct forms 1 - q² and 1 - q⁴; thin-wall ratios retain the factored radial-gap path.
- Fixes a reproducible one-ulp loss for a cavity below half an ulp of the outer-envelope properties while preserving the existing thin-wall, overflow and subnormal paths.
- Added Node and registered Chromium regressions proving the previous one-ulp result and requiring area, Ixx/Iyy, Sx/Sy and rx/ry to match the solid-circle envelope.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Correct Graph mapping regression fixture declaration

- Fixed the exact-head CI failure caused by the new Node regression reusing an existing top-level `const valid2d` identifier; the new 2D fixture is now named `dormant2d`.
- The production schema and all regression assertions are unchanged. Fresh Push/PR Quality runs are required to verify the fix.

## 2026-11-26 — Reject invalid primary Graph dataset mappings in saved projects

- Added pre-import validation for saved Graph mode, primary X/Y/Z selectors and plot style. Invalid explicit selectors no longer silently fall back to header-based defaults during restore.
- Preserved legacy projects that omit selector/style fields and the dormant 2D Z selector; 3D mappings require distinct axes.
- Added Node schema and Chromium atomic-import/round-trip regressions, synchronized the standalone project-schema script, and documented the backup contract.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Reject malformed Graph dataset overlays in saved projects

- Added pre-import validation for additional graph series: overlay count, table dimensions/cells, X/Y/Z mappings, 2D/3D mode, plot style and at least one numeric point.
- Invalid overlays now fail project validation instead of being silently truncated or dropped during restore; missing/null legacy overlay lists remain supported.
- Added Node schema and Chromium atomic-import regressions; synchronized the inline standalone project-schema module and documented the project-format contract.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Preserve full precision in Data Tables formulas

- Formula evaluation now returns the full finite binary64 result instead of rounding intermediate cell values to 13 significant digits.
- Kept the existing compact 13-digit presentation as display-only formatting; dependent formulas, aggregates, graph handoff and computed exports retain the full numeric value.
- Added Chromium coverage for 1/7, dependent multiplication, SUM/AVERAGE/MEDIAN, aggregate chaining and 390px visibility; strengthened static source/bundle checks.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Correct hollow-rectangle small-cavity rounding

- Small cavities now use a direct, well-conditioned area difference; Ixx/Iyy use finite outer-minus-inner moment terms when safe, while the factored wall-gap path remains for thin walls and overflow cases.
- Small-cavity radii use a stable ratio identity to avoid one-ulp errors from independently rounded area/inertia factors.
- Added Node and registered Chromium regressions for area, Ixx/Iyy, radii, below-half-ulp behavior and BigInt-disabled fallback at desktop/390px.
- Implemented on dev; fresh exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Preserve Truss section sums without BigInt

- Same-sign finite sums now use Neumaier compensation in original units when the BigInt exact accumulator is unavailable, avoiding an extra scale-normalization rounding in L-angle, channel and I-section properties.
- Mixed-sign fallback and BigInt exact accumulation remain unchanged; non-finite final sums still reject.
- Added Node and registered Chromium regressions that disable BigInt and verify L-angle area/centroid/inertias, sub-ulp channel/I-section flange areas and channel/I-section inertia values at 1280px/390px.
- Implemented on dev; fresh exact-head Push/PR Quality pending; not released.

## 2026-11-26 — L-angle section-property exact summation

- L-angle area, first moments, Ixx/Iyy and Ixy now use the existing exact binary64 section-property accumulator when BigInt is available, avoiding a one-ulp area error from scale normalization and order-dependent local/parallel-axis inertia sums.
- Added two direct Node numerical regressions and extended Chromium coverage for both high-aspect-ratio fixtures at 1280px and 390px; existing channel/I-section checks remain.
- Implemented on dev; fresh exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Exact composite-section centroid and inertia sums

- Composite channel and I-section area, first moments and local-plus-parallel-axis inertias now sum already-rounded finite binary64 terms exactly when BigInt is available, with the existing scaled compensated compatibility fallback.
- Added direct Node and Chromium regressions for a sub-ulp channel centroid/Ixx/Iyy case and an order-sensitive I-section Ixx case; browser checks run at 1280px and 390px.
- Implemented on dev; fresh exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Compensated composite-section area totals

- Channel and I-section rectangle-area totals now use the existing scaled compensated accumulator, preserving combined flange contributions when each flange is individually below half an ulp of the dominant web area.
- Added a direct Node regression proving the naive total rounds to 1.0 mm² while the correctly rounded web-plus-two-flange area is 1.0000000000000002 mm² for both channel and I-section fixtures.
- Implemented on dev; fresh exact-head Push/PR Quality pending; not released.

## 2026-11-26 — Reject Truss Euler CSV unit underflow

- Exact-head Push/PR CI exposed a stale Euler CSV expectation: the computed binary64 kN value serializes as 493.48022005446785, not the older rounded 493.4802200544678. Updated Node and Chromium regressions to require shortest-round-trip fidelity.
- Hardened material CSV export against a positive finite Euler load in N becoming zero when converted to kN; the exporter now reports an explicit underflow error instead of emitting a misleading zero.
- Added a direct numerical regression for positive-N/zero-kN conversion. Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Guard exact binary64 values in Truss material CSV

- The material CSV serializer now verifies that every finite numeric cell reparses to the identical binary64 value and refuses non-finite numeric cells.
- Corrected stale Node/Chromium expectations: the bar UI rounds mass to 15.7 kg, while CSV preserves the exact computed value 15.700000000000001 kg for 0.002 m³ × 7850 kg/m³.
- Added exact parsed-value and volume×density regression assertions. Existing UI display behavior is unchanged.
- Exact-head Push/PR Quality pending on the new dev candidate; not released.

## 2026-11-25 — Correct Truss CSV round-trip regression row delimiter

- Corrected the new Node regression to split the exported CSV on actual CRLF characters rather than a double-escaped literal; numeric round-trip assertions are unchanged.
- Exact-head Push/PR Quality must pass on the corrected follow-up commit; not released.

## 2026-11-25 — Truss material CSV preserves exact binary64 numeric values

- Replaced fixed 16-significant-digit rounding with shortest round-trippable decimal output for finite numeric cells; negative zero is emitted as `-0`.
- Added a regression for density `0.10000000000000002` and derived mass `0.00020000000000000004`, both previously rounded to different numeric values.
- Updated the Structural Truss numerical/export contract. Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Truss channel safely handles a negligible underflowed web

- A channel web whose area rounds to zero is accepted only when exponent-scaled upper bounds prove its area, first moments, local/offset inertias, Ixy and both normalized-path contributions are below binary64 significance, and the remaining section properties are normal.
- Non-negligible off-axis underflowed webs remain explicitly rejected; the existing centered I-section web rule is unchanged.
- Added exact-binary64 Decimal-backed Node and Chromium regressions for a finite flange-dominated channel, including 1280px and 390px browser coverage.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Truss FEM mixed-sign resultants preserve exact binary64 cancellation

- Added an exact integer accumulator for mixed-sign finite binary64 force and moment terms, with a single nearest/ties-to-even binary64 conversion; same-sign reductions retain the scale-normalized compensated path.
- Fixed a reproducible 79-node cross-scale cancellation error: applied force now returns `9.99937827510621e-11 N` instead of `9.99875737761613e-11 N`, with the corresponding signed origin moment corrected.
- Added direct Node and registered Chromium desktop/390px regressions; existing huge cancellation, subnormal residual, true-overflow and solved force-balance coverage remains.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Truss FEM force-balance diagnostics preserve finite cancellation

- Combined applied nodal loads and support reactions before compensated summation, preventing separate overflowing totals from producing a NaN force-balance diagnostic when the true equilibrium residual is finite.
- Added Node and registered Chromium regressions with +1e308, +1e308, -1e308 N applied loads and corresponding reactions; the previous separate totals were +Infinity/-Infinity while the corrected balance is exactly zero.
- Corrected the signed-moment test fixture to explicitly initialize the appended node's zero Fx, so its naive overflow assertion proves the intended overflow rather than accidental NaN.
- Restored the empty dev living plan from the complete main-branch historical plan, preserving the prior history and adding the current dated entry and next five.
- Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Quality acceptance criteria follow the current workflow

- Removed a fixed 218-step count from the newest living-plan and execution-ledger acceptance criteria; the current exact-head workflow exposes 217 steps.
- The gate remains unchanged in substance: every required step must pass, with zero failed or skipped required checks. No CI checks were removed or weakened.

## 2026-11-25 — Truss signed-resultant summation retains subnormal normalized terms

- Extended the separate residual path to every normalized quotient below the smallest normal binary64 value, not only quotients that underflow to zero.
- Added a regression for a 1e-10 N term between +1e308 N and -1e308 N; the previous path lost about 1.25 ppm due to subnormal quotient quantization.
- Preserved minimum-subnormal residual, x/y force and moment cancellation, and genuine final-overflow rejection coverage. Exact-head Quality pending; not released.

## 2026-11-25 — Truss preview preserves finite signed resultants after cancellation

- Replaced naive applied-force and global-origin moment reductions with scale-normalized Neumaier accumulation, retaining terms that underflow only after normalization in a separately compensated residual.
- Finite x/y force totals and signed moment resultants no longer fail solely because an overflowing intermediate partial sum is later cancelled; individually non-finite moment products and genuinely non-finite final resultants remain rejected.
- Added Node and registered Chromium regressions for horizontal/vertical cancellation, a minimum-subnormal residual between large cancelling loads, moment cancellation and true final overflow at 1280px/390px.
- No FEM stiffness/displacement solver or root bundle change; Truss Studio uses adjacent JS assets. Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Data Tables chart regression assertion matches combined declaration

- Repaired a brittle structural assertion that expected `const scale=...` as a standalone declaration even though production correctly declares `const margin=90,scale=...` in one statement.
- The assertion still requires the exact scale-normalization expression; no source behavior or numerical/browser coverage was weakened.
- Exact-head Push and PR Quality must rerun the structural suite and registered Chromium chart regressions. Not released.

## 2026-11-25 — Data Tables categorical charts avoid numeric overflow

- Replaced naive repeated-category addition with scale-normalized compensated accumulation, including the grouped Other category; genuinely unrepresentable category totals now produce an explicit error.
- Normalized positive pie weights before computing percentages and normalized mixed-sign bar values before axis mapping, preventing infinite totals/ranges and non-finite canvas coordinates for finite binary64 inputs.
- Added registered Chromium regressions for large-value category cancellation, finite equal pie slices, finite mixed-sign bar rectangles and true category overflow; added structural source assertions.
- Synchronized `src/data-tables.js` with the embedded standalone `index.html`. Implemented on dev; exact-head Push/PR Quality pending; not released.

## 2026-11-25 — Data Tables SUM preserves finite results after cancellation

- Replaced naive left-to-right SUM accumulation with scale-normalized compensated summation, retaining terms whose normalized quotient underflows so they survive cancellation of much larger values.
- Preserved the existing #NUM! behavior when the final sum is genuinely non-finite.
- Added Chromium regressions for finite cancellation after an overflowing partial sum, 1e-300 and minimum-subnormal residuals, and true final overflow; added structural source assertions.
- Synchronized `src/data-tables.js` with the embedded standalone `index.html`. Implemented on dev; exact-head Quality pending; not released.

## 2026-11-25 — Data Tables action menus expose explicit disclosure relationships

- Added unique content-region IDs and `aria-controls` links to the five native Table, Filter, Combine, Files and Python disclosure summaries while retaining their accessible names.
- Corrected the registered Chromium regression to exercise the native summary control directly, assert its accessible name/control target, and verify Rename visibility before atomic rollback/recovery.
- Synchronized `src/numerical-data.js` with the embedded standalone `index.html`. Exact-head Push/PR Quality is required; not released.

## 2026-11-25 — Data Tables insertion at the grid edge invalidates shifted references

- Structural insertion now rewrites previously valid scalar references and ranges to explicit `#REF!` when a shifted coordinate would leave A1:AF6000; already-invalid references remain unchanged.
- Added row-6000 and column-AF scalar/range Chromium regressions and structural source assertions.
- Repaired the sheet-rename regression setup by explicitly activating the Data Tables workspace before clicking Rename; the visibility assertion prevents a hidden-control timeout.
- Updated modular source and standalone `index.html` together. Implemented on dev; exact-head Quality pending. Not released.

## 2026-11-25 — Data Tables sheet renames commit references atomically

- Sheet renaming now stages every workbook-wide formula rewrite before mutating any cell or changing the sheet name; a late cell-conversion failure cannot leave earlier formulas partially renamed.
- Added a registered Chromium regression for late cross-sheet conversion failure, unchanged workbook state, successful retry, quoted new sheet names and preserved double-quoted formula literals.
- Updated the modular source and standalone index.html bundle together, plus the Data Tables guide, living plan, execution ledger and changelog.
- Implemented on dev; exact-head Push/PR Quality required before promotion. Not released.

## 2026-11-25 — DATA-TABLES-ROLLBACK-RECOVERY-ASSERTION-CORRECTION

Review of the new browser regression caught an assertion-index issue before treating the run as green: after a successful insertion at row 1, the original formula row correctly moves from index 0 to index 1. Updated the recovery assertion to inspect that moved row. No product logic or test coverage was weakened; exact-head Quality on the corrected dev/PR head is required.

## 2026-11-25 — Data Tables structural reference rewrites commit atomically

- Structural formula rewrites are staged across every workbook sheet and committed only after all cell conversions and rewrites succeed.
- Added a Chromium regression for a late conversion failure after local and cross-sheet references have been visited; it verifies unchanged workbook export, unchanged formulas/row count, and successful recovery after the bad cell is corrected.
- Added a structural unittest and clarified the Data Tables guide. Synchronized `src/data-tables.js` with the standalone `index.html` bundle.
- Implemented on dev; exact-head Push/PR Quality pending. Not released.

## 2026-11-25 — TRUSS-L-ANGLE-SIGNED-ZERO-CI-REPAIR

Starting refs: dev `183c6500a9d7fc04620d08e385051254c60f76a1`, main `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; release PR #191 remains open.

Exact-head Push Quality [#45603581050](https://github.com/saeedsai/ProMathStudio/actions/runs/45603581050) and PR Quality [#45603598028](https://github.com/saeedsai/ProMathStudio/actions/runs/45603598028) both failed at step 214, **2D truss FEM analytical references, scaling and mechanism rejection**. The Truss Node suite reported 90/91 passing. The failing L-angle regression expected dimensional Ixy to be zero, but the normalized result restored the correctly signed binary64 underflow value `-0`; the normalized tensor still produced the correct 45° principal-axis angle. This is a signed-zero representation defect, not a loss of principal-axis information.

Fix on dev: canonicalize only a zero-valued restored dimensional Ixy to positive zero. Keep the normalized signed Ixy for the principal-axis calculation. Tighten the Node regression with `Object.is(value, 0)` and the registered Chromium regression with a positive-zero sign check. Update the Truss numerical contract, living plan, execution ledger and changelog. No `index.html` edit is needed because Truss Studio loads the adjacent `tools/truss-fem.js` asset.

Local repository checkout is absent in this execution workspace, so local Node/Playwright commands cannot run here. Fresh exact-head Push and PR Quality must validate the committed candidate; pending until GitHub Actions completes. No test assertions are weakened.

Main remains `0d8ac89f7c9177806a266e56b27980c83d2c3ff5`; its Quality [#45360386408](https://github.com/saeedsai/ProMathStudio/actions/runs/45360386408) previously passed 218/218 and Pages [#45360367251](https://github.com/saeedsai/ProMathStudio/actions/runs/45360367251) completed build/status/deploy successfully. PR #191 has no independent reviews; both branches report unprotected, rulesets are empty, and the connected integration receives HTTP 403 for branch-protection reads. Do not merge until eligible approval and verifiable required protections are available. Frozen historical inventory remains **166 gaps / 95 partial**.

## Next five features

1. **P0 — Exact-head Truss CI and release governance:** require the new dev Push and PR Quality to pass every required step on the same exact SHA; obtain eligible independent PR #191 approval and verifiable main protection for required checks/no direct push/force/deletion; inspect the full diff, merge only through the ordinary PR process, then verify main Quality, Pages and hosted critical paths. Acceptance: zero failed/skipped required checks on the candidate and successful post-merge main/Pages verification.
2. **P1 — Complete the seven-shape Truss numerical audit:** thin-wall, subnormal and high-scale references for rectangle, hollow rectangle, solid/hollow circle, channel, I-section and L-angle. Acceptance: exact-binary64 Decimal references, genuine final overflow/underflow rejection, invalid rollback and selected-member isolation in Node plus 1280px/390px Chromium.
3. **P1 — Data Tables grid-boundary edits:** row 6000/column AF insertion/deletion, valid-to-invalid #REF! transitions, blank-grid and reversed/mixed-anchor ranges. Acceptance: unchanged out-of-grid references, correct recalculation, byte-identical rejected-operation rollback and desktop/390px Chromium.
4. **P1 — Saved-project compatibility:** current and legacy Matrix/Graph/Table round-trips. Acceptance: malformed imports preserve every workspace, selection and prior result; desktop/390px browser tests.
5. **P1 — ODE solver verification:** analytical forward/backward IVPs, tolerance/step convergence, unsupported-class diagnostics and stale-export invalidation. Acceptance: independent numerical references, failure/recovery and desktop/390px browser tests.

---

## 2026-11-25 — CI-DELIVERY-PLAN-HEADING-REPAIR

Exact-head Push Quality #45602917742 and PR Quality #45602928273 on b37084214b0bce42fb2d2af88c45e4fa120dc975 failed only in structural step 7: tests/test_delivery_policy.py requires the literal heading "Next five features" in docs/HOURLY_DEVELOPMENT_PLAN.md. The five priorities were present under uppercase NEXT FIVE, but the exact compatibility heading was missing. Restored the full historical plan from the preceding b9f00f9 version and added the required heading without changing the five priorities or weakening any assertion. Re-run exact-head Push and PR Quality after this documentation repair.

## 2026-11-25 — TRUSS-L-ANGLE-Ixy-UNDERFLOW-CANDIDATE-SYNTAX-CHECKPOINT

The first candidate commit b05ff5ee250cf90ac65342de6d6a17db40b12696 contained a duplicated continuation of the normalized-candidate guard after a multi-line source replacement. A bounded isolated V8 syntax check caught the malformed source before claiming validation. The duplicate lines were removed without changing the numerical condition or weakening the new regression. The preceding source/test commit remains intact; this follow-up is a compile correction. Re-run actual production-module syntax and the new L-angle underflow regression, then require fresh exact-head Push and PR Quality. No release or main update.

## 2026-11-25 — L-angle retains principal-axis results when dimensional Ixy underflows (dev; exact-head QA pending)

- L-angle section properties no longer reject solely because the dimensional product of inertia rounds below binary64 range while area, diagonal inertias and principal properties remain representable.
- The existing normalized two-rectangle tensor path now also runs for zero-rounded dimensional Ixy; it retains normalized orientation while the exported dimensional product correctly remains zero. Positive determinant/principal-property guards remain.
- Added exact-binary64 Decimal-reference Node coverage and registered 1280px/390px Chromium coverage for the 45° principal axis, principal moments, moduli and radii.
- Updated the Structural Truss guide, hourly plan and execution ledger. Implemented on dev only; not released pending exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — I-section accepts a centered web whose area is below binary64 range (dev; exact-head QA pending)

- The I-section helper now permits only its exactly centered central web to have a zero rounded area when both web dimensions are below 1 mm; its local inertias and parallel-axis contributions are then also below binary64 range.
- All other composite-piece area-underflow rejection and final positive total-area/inertia checks remain unchanged; the same underflowed web is still rejected for a channel.
- Added exact-binary64 Decimal-reference Node and registered 1280px/390px Chromium regressions for area, Ixx/Iyy, Sx/Sy and rx/ry, plus a channel negative control.
- Updated the Structural Truss numerical contract. Implemented on dev only; not released pending exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — L-angle mixed-axis subnormal precision (dev; exact-head QA pending)

- L-angle section-property evaluation now uses independent width/depth normalization when only one centroidal inertia is subnormal, preserving geometric section modulus and radius precision for that axis.
- Added exact-binary64 Decimal-reference Node coverage and registered 1280px/390px Chromium coverage; ordinary sections and reported dimensional inertia remain unchanged.
- Updated the Structural Truss numerical contract. Implemented on dev only; not released pending exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — Truss rejects positive final member mass that underflows to zero (dev; exact-head QA pending)

- A positive density/geometry combination can no longer be reported as zero mass when the final L·A·ρ product itself underflows; the diagnostic identifies the member.
- Explicit zero density remains valid, representable mass after intermediate volume underflow remains supported, and genuine final overflow remains rejected.
- Added Node and registered 1280px/390px Chromium regressions for final underflow, zero density and retained representable mass. No FEM equations or standalone UI bundle changes.
- Updated the Structural Truss numerical contract. Implemented on dev only; not released pending exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — Truss preview rejects an unrepresentable positive member volume instead of reporting zero (dev; exact-head QA pending)

- Pre-solve inspection now rejects positive L·A products that underflow to zero, while preserving the independently representable scale-safe mass; existing volume overflow rejection remains.
- Reuses each validated member volume for total and per-member preview metrics, preventing divergent checks.
- Added Node and registered 1280px/390px Chromium regressions for preview and material-CSV rejection; FEM parsing, stiffness, mass and solve paths are unchanged.
- Updated the Structural Truss numerical contract. Implemented on dev only; not released pending exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — Truss Euler critical load preserves representable results across intermediate range limits (dev; exact-head QA pending)

- Optional Pcr now retains the existing direct calculation for ordinary values and falls back to binary-exponent product/quotient evaluation when π²·E·I, K·L or (K·L)² overflows/underflows.
- Added Node Decimal-reference cases for simultaneous overflow and underflow, a finite result with Number.MAX_VALUE I, and genuine final overflow/underflow rejection; the registered 1280px/390px Chromium smoke exercises both representable extremes.
- Updated the Structural Truss numerical contract. Implemented on dev only; not released pending fresh exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — Truss member mass preserves representable L·A·density across volume range limits (dev; exact-head QA pending)

- Optional mass calculation now uses a scale-safe three-factor product when intermediate member volume L·A overflows or underflows, while retaining ordinary left-to-right arithmetic for normal finite values.
- Added Node and registered 1280px/390px Chromium regressions for a zero-underflow volume with finite 9.88131291682493e-28 kg mass and an overflowing volume with finite 9.999999999999968e299 kg mass; zero density and genuinely overflowing final mass remain covered.
- Updated the Truss numerical contract. Implemented on dev only; not released pending fresh exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — Truss axial stiffness retains representable EA/L across intermediate range limits (dev; exact-head QA pending)

- Preserve the ordinary direct E*A/L path while using binary exponent scaling when the intermediate product overflows/underflows or the quotient is otherwise lost.
- Added Node Decimal-reference regressions for a finite ~1e302 N/m quotient with an overflowing product and a positive ~2.5e-316 N/m quotient with a zero product; true final overflow/underflow and ordinary bit-level behavior remain guarded.
- Extended the registered standalone Truss Chromium smoke at 1280px/390px and documented the numerical contract. Implemented on dev only; not released pending exact-head Push/PR Quality and ordinary reviewed promotion.

## 2026-11-25 — Hollow section cavity underflow no longer rejects representable net properties (dev; exact-head QA pending)

- Hollow rectangle and hollow circle helpers no longer require the cavity area / inner-diameter square to be representable when the positive contained geometry and all net section properties are representable.
- Added direct Node and registered Chromium regressions at 1280px/390px for zero-underflow cavity intermediates, finite positive net properties, solid-envelope binary64 parity, input immutability and frozen results.
- Updated the Structural Truss guide and restored the full historical execution ledger on dev (all main history plus seven unique dev entries). The frozen MATLAB inventory remains 166 gaps / 95 partial. Not released pending exact-head Quality and ordinary reviewed promotion.

## 2026-11-25 — Repair over-escaped Data Tables sort validator after exact-head CI failure

- Exact Quality #45522925339 exposed an invalid regex in the new sort guard during Node inline-script syntax validation (step 7). Corrected the literal to match the existing single-backslash reference validator.
- Added a structural regression asserting the exact regex spelling; preserved the invalid-reference/blank-grid sort behavior and the existing browser regression.
- Synchronized src/data-tables.js and index.html. This corrective dev commit awaits a fresh exact-head Quality run; no tests were weakened and no release bypass occurred.

## 2026-11-25 — Data Tables sorting preserves invalid and blank-grid references (dev; exact-head QA pending)

- Stable row sorting now leaves references outside the supported A1:AF6000 grid unchanged and invalid, while valid blank rows beyond the current materialized table retain fixed coordinates in range-contiguity checks.
- Added a registered Chromium regression for full-grid/blank ranges, invalid AG/A6001 references, reversed mixed-anchor ranges and calculated values; existing noncontiguous-range rollback remains covered.
- Added structural coverage and clarified Data Tables documentation. Updated src/data-tables.js and the standalone index.html module together. Implemented on dev; not released pending exact-head Quality and ordinary reviewed promotion.

## 2026-11-25 — Data Tables row insertion preflights cell conversion (dev; exact-head QA pending)

- Row insertion now validates and materializes supplied cell strings before workbook-wide formula rewrites, preventing a thrown conversion from shifting cross-sheet references without inserting a row.
- Added a registered Chromium rollback regression and a structural unittest; the browser asserts identical exported workbook state, formula and row count after failure.
- Updated the Data Tables guide, living plan and execution ledger. The standalone Data Tables module in `index.html` remains synchronized with `src/data-tables.js`. Implemented on dev; not released pending exact-head Quality and ordinary reviewed promotion.

## 2026-11-24 — Composite section properties retain accuracy at extreme aspect ratios (dev; exact-head QA pending)

- Channel and I-section now fall back from max-dimension normalization to independent x/B and y/H coordinate scales when a normalized area/inertia loses normal binary64 range; physical area/inertias and ordinary paths remain unchanged.
- Added Node and 1280px/390px Chromium regressions for a 1e304 aspect ratio, reproducing >1e-11 thin-axis rx/Sx error and checking exact-binary64 120-digit Decimal rx/ry/Sx/Sy references within 5e-13.
- Updated the Structural Truss guide, living development plan and execution ledger. Implemented on dev; not released pending exact-head Quality and ordinary reviewed promotion.

## 2026-11-24 — Composite section moduli preserve subnormal-inertia precision (dev; exact-head QA pending)

- Channel and I-section Sx/Sy now reuse normalized inertia and normalized extreme-fibre geometry when the corresponding physical Ixx/Iyy is subnormal; ordinary I/c behavior and dimensional area/inertias remain unchanged.
- Added direct Node and registered 1280px/390px Chromium regressions with exact-binary64 120-digit Decimal references; former I/c errors of 5–24% are reproduced and corrected results are checked within 5e-13 relative error.
- Updated the Structural Truss guide, living plan and execution ledger. Implemented on dev; not released pending exact-head Quality and ordinary reviewed promotion.

## 2026-11-24 — Circular section moduli avoid subnormal-inertia quantization (dev; exact-head QA pending)

- Solid and concentric hollow circle Sx/Sy now use the factored analytic (π/32)·Do³·inertiaFactor only when dimensional inertia is subnormal; ordinary sections retain I/c.
- Added direct Node and registered 1280px/390px Chromium regressions for exact-binary64 thin solid/annular circles. The old I/c path reproduced >20% error; corrected values match independent 120-digit Decimal references within 5e-13 relative error.
- Updated the Structural Truss guide, hourly plan and execution ledger. Implemented on dev; not released pending exact-head Quality and reviewed promotion.
## 2026-11-24 — Truss rectangular section moduli avoid subnormal-inertia precision loss (dev; exact-head QA pending)

- Solid and concentric hollow rectangle Sx/Sy now use dimensionless geometry factors only when the corresponding Ixx/Iyy is subnormal, avoiding 2–4% errors from dividing rounded inertia by extreme-fibre distance while preserving the ordinary I/c path.
- Added direct Node and 1280px/390px Chromium regressions with independent 120-digit Decimal references; prior I/c errors are reproduced and corrected values match within 5e-13 relative error.
- Updated the Structural Truss guide, living development plan and execution ledger. Implemented on dev; not released pending exact-head Quality and ordinary reviewed promotion.

## 2026-11-24 — L-angle subnormal inertia and principal-property precision (dev; exact-head QA pending)

- L-angle sections whose physical inertia tensor is subnormal now recompute the same two rectangles at normalized length scale before restoring Ixx/Iyy/Ixy, principal moments/axis, section moduli and radii. Ordinary and extreme-aspect fallback paths are retained.
- Added exact-binary64/120-digit Decimal Node and 1280px/390px Chromium regressions; the prior path reproduced >1% radius and >1° principal-axis errors.
- Updated the Structural Truss guide, hourly plan and execution ledger. Implemented on dev; not released until exact-head Quality and ordinary reviewed release gates pass.

## 2026-11-24 — Composite section radii avoid subnormal I/A quantization (dev; exact-head QA pending)

- Channel and I-section radii now recompute the composite area, centroid and inertias at a normalized length scale, then restore the scale once. Existing dimensional area and Ixx/Iyy outputs are unchanged.
- Added Node and 1280px/390px Chromium regressions proving subnormal physical inertias previously distorted both radii by more than 1%, with independent high-precision references and input immutability checks.
- Updated the Structural Truss guide, living plan and execution ledger. Implemented on dev; not released until exact-head Quality and ordinary reviewed release gates pass.

## 2026-11-24 — Truss circular radii avoid subnormal-inertia precision loss (dev; exact-head QA pending)

- Solid-circle radii now use Do/4; concentric hollow-circle radii use (Do/4)·sqrt(1+(Di/Do)^2), avoiding large relative error from a rounded subnormal I/A quotient.
- Added direct Node and 1280px/390px Chromium regressions for solid and hollow circles; both reproduce the old >10% radius error while retaining a positive subnormal inertia.
- Updated the Structural Truss guide, living plan and execution ledger. Implemented on dev; not released.

## 2026-11-24 — Truss rectangular radii avoid subnormal-inertia precision loss (dev; exact-head QA pending)

- Solid and concentric hollow rectangle radii of gyration now use dimensionless geometry factors instead of the rounded binary64 I/A quotient. This preserves accurate rx/ry when a representable Ixx is subnormal.
- Added Node and 1280px/390px Chromium regressions for solid and hollow rectangles; the tests demonstrate the prior >10% radius error and verify independent geometric references.
- Updated the Truss FEM guide, hourly plan and execution ledger. Implemented on dev; not released.

## 2026-11-24 — Spreadsheet structural edits preserve invalid grid references (dev; exact-head QA pending)

- Row/column deletion no longer shifts an already out-of-grid scalar or aggregate reference into a valid cell (for example, A6001 stays #REF! after deleting row 1, and AG1 stays #REF! after deleting column A).
- Added cross-sheet Chromium regressions with valid-reference controls and structural assertions; retained the existing registered range-deletion smoke and source/standalone-bundle parity check.
- Updated the Data Tables guide, living plan and execution ledger. Implemented on dev; not released.

## 2026-11-24 — Spreadsheet scalar references enforce grid bounds (dev; exact-head QA pending)

- Scalar references outside the supported `A1:AF6000` grid now return `#REF!` instead of silently reading as zero; valid empty cells inside the grid remain blank.
- Added Chromium coverage for row 0, row 6001, column AG, the maximum valid AF6000 coordinate, aggregate-range consistency and arithmetic on an empty in-grid cell.
- Added structural coverage for the bounds guard and exact source/standalone-bundle parity. Updated the Data Tables guide, plan and execution ledger.
- Candidate is on dev only; exact-head Quality is required before promotion. Not released.

**Follow-up fixture check:** the protected formula literal intentionally remains ="Obrien!A1" after rename, sort and row/column insertion; corrected both post-sort/post-column expected rows to match the unchanged literal. No behavior assertion was removed.

## 2026-11-24 — Spreadsheet rename keeps qualified formulas valid (dev; exact-head QA pending)

- Renaming a sheet now rewrites matching qualified scalar and aggregate-range references across the workbook; both quoted and unquoted old names are recognized case-insensitively.
- New names that require quoting are emitted with doubled embedded apostrophes. Double-quoted formula string literals are protected from rewriting.
- Expanded the registered Chromium smoke to verify rename, scalar/range calculations, sorting, structural edits, and literal preservation. Fixed its invalid JavaScript slice expression (rows[0][:4] to rows[0].slice(0,4)) without weakening assertions.
- Synchronized src/data-tables.js with its inline standalone index.html module and updated the Data Tables guide, plan and execution ledger. Full exact-head Quality is required; not released.

## 2026-11-24 — Spreadsheet sheet names with escaped apostrophes (dev; exact-head QA pending)

- Table rename now preserves internal apostrophes; formulas refer to those names using doubled apostrophes inside single quotes, e.g. `='O''Brien'!A1` and `=SUM('O''Brien'!A1:A3)`.
- Applied the same qualifier grammar/decoder to scalar cells, aggregate ranges, structural row/column edits and sorting. Mixed anchors, reversed cross-sheet ranges and quoted formula literals are covered.
- Extended the registered Chromium spreadsheet-reference smoke and added structural/source-bundle parity coverage. Updated the Data Tables guide and synchronized modular source with standalone `index.html`.
- Implemented on dev only; exact-head full Quality and the ordinary protected, independently reviewed PR gate are still required before release.

## 2026-11-24 — Spreadsheet aggregate structural-test recovery (dev; exact-head QA pending)

- Updated the numeric-hardening structural test to match the new scaled compensated AVERAGE/AVG and safe MEDIAN midpoint implementation rather than asserting the retired expression.
- Added direct structural checks for underflow-residual preservation, scaled midpoint dispatch and the retained finite-result error guard. Exact source/bundle parity and browser-gate assertions remain mandatory.
- Root cause of Quality #45382903210 step 7 failure was a stale test expectation; production code was not weakened. Fresh exact-head Quality required.

## 2026-11-24 — Spreadsheet subnormal and cancellation-safe aggregates (dev; exact-head QA pending)

- AVERAGE/AVG now use scaled compensated accumulation and preserve separately accumulated terms whose normalized quotient underflows; small residuals survive cancellation of large positive/negative values.
- Even-count MEDIAN now uses a scaled midpoint, preserving minimum/adjacent subnormal values without overflowing large same-sign inputs.
- Added browser regressions for raw workbook subnormal ranges, maximum-finite average, cancellation residuals, negative/adjacent subnormal medians and workbook round-trip.
- Updated the modular Data Tables source and synchronized inline standalone bundle, plus the Data Tables guide and hourly execution records. Not released until exact-head Quality and the normal protected, independently reviewed PR gate pass.

## 2026-11-24 — Truss radius precision and exact-head CI recovery (dev; QA pending)

- Use `sqrt(I/A)` when the quotient is finite and positive, with the previous split-square-root calculation as overflow/underflow fallback. The 40 mm solid-circle reference now returns 10 mm exactly without losing the extreme L-angle range case.
- Added a focused Node regression for both the finite quotient and overflowing L-angle quotient/fallback path.
- Diagnosed exact-head Quality #45361913324: step 214 failed on a one-ULP strict reference discrepancy (`9.999999999999998` vs `10`). New candidate requires full exact-head Quality; not released.

## 2026-11-24 — Truss L-angle radius-of-gyration overflow safety (dev; exact-head QA pending)

- Radius of gyration now evaluates `sqrt(I)/sqrt(A)`, avoiding an overflowing `I/A` intermediate when the final radius is finite.
- Added a 120-digit Decimal-backed Node regression and Chromium desktop/390px coverage for a slender L-angle (`B=1e200 mm`, `H=1e100 mm`, `t=1e-293 mm`); the former code reproduced a finite-range rejection.
- Other section properties and the explicit positive/finite result guards remain. Not released until exact-head Quality and the normal reviewed PR gate pass.

## 2026-11-24 — Truss solid-circle high-range inertia safety (dev; exact-head QA pending)

- Solid-circle inertia now applies π/64 before the final multiplication of the diameter-squared terms, avoiding an unnecessary overflowing Do⁴ intermediate when the final moment is finite.
- Added 120-digit Decimal-backed Node coverage and desktop/390px Chromium preview/application coverage for Do=2.45e77 mm, including selected-member isolation and preservation of other member fields.
- Existing final finite guard, ordinary 40 mm result, hollow-circle path and tiny-diameter underflow rejection remain. Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-24 — Truss hollow-rectangle high-range inertia safety (dev; exact-head QA pending)

- Hollow-rectangle Ixx/Iyy no longer construct overflowing outer/inner solid-rectangle fourth-power intermediates before applying the thin-wall factor. The dimensionless factor is split across the repeated depth/width terms.
- Added exact-binary64 100-digit Decimal Node references and Chromium engine coverage at desktop/390px for finite area, Ixx/Iyy, section moduli and radii despite both old Ixx intermediates overflowing.
- Existing area cancellation protection, geometry validation, selected-member application behavior and composite/L-angle calculations remain; not released until exact-head Push/PR Quality passes.

## 2026-11-24 — Truss L-angle subnormal principal-moment recovery (dev; exact-head QA pending)

- Recover a positive representable L-angle minor principal moment when the normalized inertia determinant underflows, using the unscaled determinant only when finite and positive; retain explicit rejection when neither path is representable.
- Added 100-digit Decimal-backed Node coverage and Chromium engine coverage at desktop/390px for a synthetic extreme-aspect L-angle whose I2 rounds to 8.35e-322 mm⁴.
- Added the required Python math import to the new browser smoke assertion.
- No geometry, FEM solver, or member-application behavior changed. Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-24 — Truss hollow-circle fourth-power range safety (dev; exact-head QA pending)

- Hollow-circle inertia no longer eagerly forms outer/inner diameter fourth powers. A very thin annulus can now retain finite area and Ixx/Iyy even when both fourth-power intermediates overflow.
- The solid-circle calculation retains its direct fourth-power finite guard; existing annulus cancellation, geometry validation and underflow checks remain.
- Added 120-digit Decimal-backed Node coverage and desktop/390px Chromium selected-member application coverage for an extreme synthetic floating-range annulus.
- Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-24 — Truss channel/I-section sub-pixel preview detail (dev; exact-head QA pending)

- Added a separately labelled web/flange detail inset when a channel or I-section's true-scale web/flange would be below 2 SVG pixels; the measured outline remains at true scale and is never distorted.
- Synchronized the live caption, SVG accessible name and SVG description with the explicit “not to scale” notice.
- Added desktop/390px Chromium coverage for normal/no-inset and extreme/sub-pixel channel/I-section previews, Iyy application to a selected member, and solid-circle application. Preserves other members and E/density/K.
- Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-24 — Truss composite-section local inertia overflow safety (dev; exact-head QA pending)

- Reordered local rectangle Ixx/Iyy evaluation to divide by 12 before the final dimension multiplication, preventing intermediate overflow when the final local moment is finite.
- Applied the shared calculation to channel, I-section and L-angle decompositions; no solver or ordinary-size geometry behavior changed.
- Added high-precision Node references for synthetic extreme-range channel, I-section and L-angle cases, including a check that the old operation order overflows.
- Fresh exact-head Push/PR Quality required; not released.

## 2026-11-24 — Truss section-application result freshness (dev; exact-head QA pending)

- Clear the previous “applied to member” result when section geometry/shape, selected member, axis, member ID/area/I or loaded model changes; do not rewrite member values until the user explicitly reapplies.
- Added desktop and 390px browser regression for stale-result clearing after axis changes, an actual AC→AB→AC target switch, and geometry edits; member snapshots stay unchanged, reapplication restores the success result, and invalid/overflow rollback remains covered.
- Updated the Structural Truss contract and living development records. Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-24 — Truss extreme-aspect L-angle preview detail (dev; exact-head QA pending)

- Added a separately labelled leg-detail inset when an L-angle's true-scale thickness would be below 2 SVG pixels; the measured outline remains at true scale and is never distorted.
- Synchronized the live caption, SVG accessible name and description with the explicit “not to scale” notice.
- Added Chromium coverage at desktop and 390px for normal/no-inset and extreme-aspect/inset behavior, exact dimension metadata, principal-axis selection, major-principal application reference and preservation of E/density/K/other members.
- SVG `<desc>` and `<text>` regression assertions use `text_content()` for SVG-node compatibility.
- Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-23 — Truss section disclosure state and accessible controlled region (dev; exact-head QA pending)

- Linked the native “Member materials and section properties” summary to a stable `#member-material-content` region using `aria-controls`; the wrapper contains the metrics table and section helper, and the disclosure remains collapsed by default.
- Fixed the repeated browser scenario to open the disclosure only when currently closed. The first scenario intentionally leaves it open; a blind second summary click had correctly collapsed it and caused FEM browser step 215 to fail.
- Added desktop/390px assertions for the hidden collapsed region, ARIA target, expansion and repeat-open idempotence. Existing numerical and member-preservation assertions are unchanged.
- Exact-head Push/PR Quality required; not released.

## 2026-11-23 — Truss section-helper disclosure discoverability and CI recovery

- Renamed the collapsed member-details disclosure to “Member materials and section properties” so the nested section helper is discoverable; it remains intentionally collapsed by default.
- Fixed the FEM browser regression to open the native disclosure before selecting its hidden member control, and assert closed→open visibility at 1280px and 390px before exercising hollow-circle preview/application and member-preservation references.
- Root cause of exact-head Push/PR Quality failure: step 215 attempted to select `#section-member` while its parent details disclosure was closed. The preceding Node suite passed 68/68 in both failed runs. No test assertion was weakened.
- Fresh exact-head Push/PR Quality required; not released.

## 2026-11-23 — Thin-walled hollow-rectangle section stability (dev; exact-head QA pending)

- Replaced cancellation-prone outer-minus-inner area and inertia subtraction with algebraically equivalent dimensionless gap factors for hollow rectangles.
- Added high-precision Node references for net area, Ixx/Iyy, section moduli and radii of gyration; added Chromium desktop/390px coverage proving one-member application preserves E, density, K and all other members.
- Existing finite/positive guards and solid-rectangle behavior remain unchanged. Requires exact-head Push/PR Quality; not released.

## 2026-11-23 — Truss import race settlement and Analyze cancellation (dev; exact-head QA pending)

- Analyze now explicitly reports when it cancels a pending JSON import and confirms that the current displayed model was analyzed; cancellation context is retained on solve failure.
- Added Chromium regressions for an older pending read released after a newer malformed-file rejection, and for late success/rejection after Analyze cancellation. Assert unchanged complete model/solution snapshots, status and settled busy state at desktop and 390px.
- Preserved the existing stale-success/stale-rejection, strict UTF-8, BOM/1 MiB, short/long-read, rollback and export regressions. Requires fresh exact-head Push/PR Quality; not released.

## 2026-11-23 — Truss L-angle stable principal moments (dev; exact-head QA pending)

- Fixed avoidable floating-point cancellation in L-angle principal inertia: normalize the inertia tensor and calculate the minor eigenvalue as det(I)/I1 rather than mean − radius.
- Added a direct Node reference regression for a valid 1,000,000 × 1 × 0.001 mm L-angle whose positive I2 previously rounded to zero.
- Preserved strict finite/positive guards and existing standard/asymmetric section references. Full exact-head Quality required; not released.

## 2026-11-23 — Truss import CI recovery and declared-size validation

- Fixed the exact-head browser regression failure: Truss Studio's short-read test now expects the validator's direction-specific `fewer bytes than declared` diagnostic and exact expected/received counts.
- Hardened the FEM byte validator to distinguish invalid declared File.size metadata from a safe file exceeding 1 MiB; added Node regression coverage for undefined/null/negative/fractional/non-finite/unsafe sizes.
- Preserved the existing actual-read invalid-length, short/long mismatch, UTF-8, BOM and 1 MiB browser-import regressions. Fresh exact-head Push/PR Quality is required; not released.

## 2026-11-23 — Truss short/long read diagnostics

- Distinguish shorter-than-declared and longer-than-declared Truss file reads while retaining exact expected/received byte counts.
- Add Node assertions for both directions and a Chromium real-File over-read regression using one extra JSON whitespace byte; verify the active model/results remain unchanged and busy state clears.
- Preserve the short-read, malformed UTF-8, BOM and 1 MiB boundary regressions. Fresh exact-head Quality is required; not released.

## 2026-11-23 — TRUSS-BOM-BROWSER-FIXTURE-CORRECTION

A post-commit GitHub readback caught an escaping defect in the new Python browser fixture: its byte literal contained doubled backslashes and therefore encoded the characters “\\xef” instead of the actual EF BB BF bytes. Replaced it with the unambiguous bytes tuple `bytes((0xEF, 0xBB, 0xBF))`. The test still constructs a real 1 MiB File, checks the BOM prefix and both byte lengths, and verifies exact-limit success plus pre-read rejection at 1 MiB+1. The preceding candidate's full Quality result is not used to certify this corrected fixture; fresh exact-head Push/PR Quality is required.

## 2026-11-23 — Clarify Truss read-byte diagnostics and verify actual BOM at the 1 MiB boundary

- validateImportByteLength now distinguishes invalid actual byte-length metadata from a valid payload exceeding 1 MiB; existing exact mismatch diagnostics remain unchanged.
- Added Node regressions for undefined/null/negative/fractional/non-finite/unsafe actual lengths and safe over-limit bytes.
- Added a real Chromium File-input regression for EF BB BF + JSON at exactly 1 MiB, proving BOM bytes count in File.size and ArrayBuffer.byteLength; a 1 MiB+1 file is rejected before reading and preserves the active model/results.
- Added browser rollback coverage for a malformed read result with no byteLength. Desktop and 390px coverage remain mandatory.
- Parent exact-head Push/PR Quality passed 218/218 steps. New candidate requires fresh exact-head Quality; not released.

## 2026-11-23 — Centralize strict UTF-8 decoding for Truss model imports

- Added the FEM-kernel `decodeImportBytes` boundary for ArrayBuffer/typed-array input, shared 1 MiB enforcement and fatal UTF-8 decoding; counted BOM bytes remain visible to the canonical JSON importer.
- The browser UI now uses the same decoder after File.size/ArrayBuffer length equality validation.
- Added direct Node cases for valid input, BOM, malformed/truncated 2/3/4-byte sequences, invalid types and oversized bytes; added a real malformed-byte File-input rollback/recovery regression for desktop and 390px.
- Parent exact-head Push/PR Quality passed 218/218 steps. New candidate requires fresh exact-head Quality; not released.

## 2026-11-23 — Reject unsupported Truss section-axis selections

- Validate the selected section axis before writing area or second moment: rectangular/composite profiles accept width/depth, L-angles additionally accept principal-major/principal-minor, and circles do not use the selector.
- Added a Chromium regression that injects an unsupported selector value, checks the exact diagnostic and complete member-state rollback, then restores Ixx and continues existing FEM tests.
- Previous parent Push/PR Quality passed 218/218 steps; exact-head Quality for this change is pending. Not released.

## 2026-11-23 — Reject ambiguous Truss section-helper targets and repair browser fixture

- Exact-head Push Quality #45162019117 and PR Quality #45162337628 both failed at Truss FEM browser step 215 because the test attempted to select a control inside the intentionally collapsed `details#member-material-details`. Opened the disclosure in the browser regression and asserted the helper is visible before interaction; no production visibility behavior or assertions were weakened.
- Hardened section application to reject duplicate member IDs instead of silently updating the first matching row.
- Added a Chromium regression for ambiguous-ID rejection and complete member-state preservation before restoring a unique ID and continuing existing section-property tests.
- Updated the Structural Truss contract, living plan and execution ledger. New exact-head Quality is pending; not released.

## 2026-11-23 — Make Truss section-property application atomic

- Preflight the selected member's area and second-moment controls before writing either value, preventing partial updates when the editor row is incomplete.
- Added a 1280px/390px Chromium regression for selected-member-only updates, preservation of E/density/K and other members, invalid/overflow geometry rollback, and missing-field atomicity.
- Parent exact-head Push/PR Quality passed all 218 steps; the new candidate requires fresh exact-head Quality and is not released.

## 2026-11-23 — Centralize Truss file byte-count validation

- Added a shared FEM-kernel validator for safe declared File.size and actual ArrayBuffer.byteLength values, using one 1 MiB constant.
- The browser now rejects shorter or longer reads with exact expected/received byte counts before UTF-8 decoding.
- Added Node boundary/negative coverage and a Chromium short-read regression that verifies the active model and solved results remain unchanged.
- Parent exact-head Push/PR Quality passed all 218 steps; this new candidate requires fresh exact-head Quality and is not released.

## 2026-11-23 — Normalize optional legacy SI truss properties consistently

- Unified the FEM parser and legacy SI converter's optional-value rule for density, second moment I and effective-length factor K: undefined, null and whitespace-only values are absent; numeric zero remains present.
- Legacy conversion now omits absent optional values instead of leaking null/blank density or K into normalized Studio member records.
- Preserved valid zero density and independent I-only/K-only inputs; the Euler estimate remains unavailable unless both positive I and K are supplied.
- Added direct Node regression coverage and updated the Structural Truss compatibility contract. New exact-head Push/PR Quality is pending; not released.

## 2026-11-23 — Prevent stale blur events from cancelling a newly selected Truss import

- Made bubbling `input` events the authoritative model-edit signal for Truss node/member controls; member-ID selector synchronization now occurs on member-ID input.
- Removed duplicate change-driven invalidation so a delayed blur `change` from an already edited field cannot cancel a newer pending file import.
- Added Chromium regressions proving delayed change events do not cancel a valid legacy SI import, while a genuine density input edit still cancels a pending read and survives late bytes.
- Exact-head Push/PR Quality is pending; not released.

## 2026-11-23 — Spreadsheet string-literal safety and Truss CI fixture correction

- Fixed the Truss browser preflight fixture by assigning legacy density, I and K before asserting normalized values.
- Added a shared Data Tables formula-string shield so row/column insert/delete and stable sorting preserve double-quoted text, including doubled-quote escapes, while still rewriting actual references.
- Extended spreadsheet structural and sort browser regressions for literal preservation and updated the Data Tables contract.
- Synchronized `src/data-tables.js` with the standalone `index.html` bundle. Exact-head Quality is pending; not released.

## 2026-11-23 — Truss legacy import regression and immutable compatibility reference

- Recursively froze the private canonical legacy SI example while preserving fresh editable copies from `TrussStudio.example`.
- Added direct Node coverage for legacy JSON imports with density, second moment I and effective-length factor K, including mass, Euler critical load and solver residual references.
- Restored native `File.prototype.arrayBuffer` behavior in the Chromium smoke after temporary test overrides, added an actual size/byte-length probe and a browser-side legacy import preflight.
- Improved the final import assertion to surface the settled status message instead of hiding an import rejection behind a timeout. Exact-head Quality is pending; not released.

## 2026-11-23 — Truss legacy example isolation and browser assertion correction

- Fixed both Truss Studio latest-import assertions to match the canonical modern triangle member order: AB, AC, BC.
- Changed the legacy `TrussStudio.example` property to return a fresh editable SI-unit model copy on each read, preventing cross-caller mutation of the compatibility reference.
- Added a Node regression for independent legacy copies, canonical SI values and successful legacy solving. Exact-head Push/PR Quality is required before certification; not released.

## 2026-11-23 — TRUSS-EXAMPLE-ISOLATION-AND-CI-FIXTURE (implemented on dev; exact-head Quality pending)

Started from dev `04540961065d129ca008f583440a7b8f3a6693af` and main `70fc483cb1cec3d2372d37484e4a8ef7942343da`. Re-read root `AGENTS.md`, this plan, the frozen 2026-10-26 inventory, Structural Truss contract/source/tests, current branch refs, PR #189/reviews, exact-head Actions and Pages evidence.

Prioritized the actual exact-head failure. Push Quality [#45103425722](https://github.com/saeedsai/ProMathStudio/actions/runs/45103425722) and PR Quality [#45103430982](https://github.com/saeedsai/ProMathStudio/actions/runs/45103430982) both completed with failure at mandatory browser step 212, `tests/smoke_truss_studio.py:730`. Earlier browser regressions passed. The failing assertion expected `total member length 11.21 m` but the test supplied the wrong model. `prior = TrussStudio.example` intentionally refers to the legacy 2 × 1 m SI triangle (4.828 m total), which is later used to verify legacy SI/BOM import, while the latest-file ordering assertion expects the modern 4 × 3 m triangle (11.21 m). The assertion is valid for the intended model; the fixture mixed two distinct compatibility examples.

Added a safe built-in-example API in `tools/truss-fem.js`: canonical `examples` are recursively frozen, and `getExample(name)` returns a fresh JSON-safe editable copy for the supported `triangle` and `bar` models. Unknown names (including inherited object keys such as `toString`) are rejected. Updated the standalone editor to use copies on initial load, example selection and reset, so UI callers cannot mutate shared reference models. A direct Node regression verifies deep immutability, independent nested copies, mutable returned copies and invalid-name rejection.

Corrected the browser fixture in `tests/smoke_truss_studio.py`: the concurrent successful import now serializes `ProMathTrussFEM.getExample('triangle')`, matching its 11.21 m and member-ID assertions. Kept `prior = TrussStudio.example` and its subsequent legacy SI/BOM tests intact; those correctly expect the 2 × 1 m model and 4.828 m total. No assertion was weakened, no solver calculations or import limits changed, and no compatibility model was silently replaced.

Updated the Structural Truss contract, living plan, execution ledger and changelog in this same source/test/docs commit. The standalone Truss page loads adjacent JavaScript assets; no root `index.html` synchronization is required. Frozen historical inventory remains **166 gaps / 95 partial**.

The local checkout is absent and bounded local Git cannot resolve `github.com`; full local Node/Playwright execution is unavailable. Before commit, the complete FEM source and UI source are syntax-compiled in the V8 runtime; the new API is exercised directly for immutable templates, independent copies, editable values and invalid-name rejection; geometry totals are checked directly from member endpoints; source/test fixture anchors are checked. Exact-head GitHub Actions must execute the complete Node and browser suites on the new SHA.

**NEXT FIVE (status and acceptance tests):**
1. **P0 — Exact-head Quality certification.** Both Push and PR Quality green on the new SHA. Verify browser step 212 uses the modern 4 × 3 m example for stale-import ordering while the subsequent legacy SI/BOM case still reports 2 × 1 m, 4.828 m and converted N/Pa/m² values; then require FEM Node step 214 and browser step 215, all 59 analytical checks, CSV/SVG, mobile and zero-console-error assertions.
2. **P1 — Remaining JSON boundary audit.** Cover null/blank/zero density, independent I-only/K-only in Studio and legacy SI documents, malformed UTF-8, real BOM bytes, exact/over-1-MiB limits, byte mismatch and failed-read rollback; preserve IDs, units and physical quantities.
3. **P1 — Selected-member isolation and export audit.** Applying section properties changes only the selected member's A/I while preserving every other member and E/density/K; verify CSV quoting/units/BOM/CRLF and SVG XML/accessibility/semantic geometry.
4. **P0 — Spreadsheet formula-reference rewriting.** Test relative, absolute and mixed references through row insertion, deletion and sorting. Formulas must follow logical cells, or unsafe operations must be rejected transactionally with all data unchanged.
5. **Release governance and promotion.** Obtain an eligible independent PR #189 review and authorized verification of enforceable main protection and required checks. Only after exact-head CI and all release gates pass, merge through the ordinary dev-to-main PR and verify exact-main Quality, Pages and hosted behavior.

## 2026-11-23 — TRUSS-IMPORT-RENDER-GUARD-AND-CI-FIXTURE (implemented on dev; exact-head Quality pending)

Started from dev `686d7604e1b04e4245992f21b7d113bb667c1402` and main `70fc483cb1cec3d2372d37484e4a8ef7942343da`. Re-read root `AGENTS.md`, this living plan, the frozen 2026-10-26 inventory, Structural Truss contract/source/tests, current refs, PR #189/reviews and exact-head Push/PR Quality. Both exact-head workflows [Push #45098309605](https://github.com/saeedsai/ProMathStudio/actions/runs/45098309605) and [PR #45098314362](https://github.com/saeedsai/ProMathStudio/actions/runs/45098314362) failed in mandatory browser step 212, `tests/smoke_truss_studio.py:713`. The failure is a test-fixture `NameError: triangle_json is not defined` (Python suggests the intended `triangle_bytes`); preceding structural tests and other browser smoke tests passed. Both runs stop before the Truss FEM Node/browser steps, so those are not certified on the failed head.

Fixed the fixture by deriving `triangle_bytes = json.dumps(prior).encode('utf-8')` from the already loaded triangle example before the deferred-read test, using that exact valid payload for the newer successful import, and reusing the same bytes for the later oversized-file test. Removed the second undefined `triangle_json` reference. Added a source-backed regression in the same mandatory browser smoke: `renderModel(model, request)` must verify the request token before replacing either DOM table and return false for a stale request; the importer must stop when that guard returns false.

Production hardening: `renderModel()` now rechecks a supplied import token at the DOM mutation boundary and returns a boolean. The import handler checks that return before settling the pending request. This is defense in depth against stale requests reaching the renderer if an asynchronous/re-entrant boundary is introduced later; ordinary model/example/edit calls omit the token and preserve their existing cancellation behavior. No solver math, JSON validation, file-size limits or prior assertions were relaxed.

Updated the Structural Truss contract, living plan, execution ledger and changelog in the same atomic source/test/docs commit. The standalone Truss page loads adjacent JavaScript assets, so `index.html` synchronization is not required. Historical inventory remains frozen at **166 gaps / 95 partial**. No merge, production deployment or inventory reclassification is claimed.

The local checkout is absent and bounded local Git cannot resolve `github.com`; no full local Playwright or repository suite is claimed. The changed JavaScript is syntax-compiled in the V8 execution runtime, source/test invariants are checked before writing, and GitHub Actions must execute the full browser regression on the new exact SHA.

**NEXT FIVE (status and acceptance tests):**
1. **P0 — Exact-head Quality recovery.** Both Push and PR Quality green on the new SHA. The Truss Studio browser suite must pass the deterministic stale-import test, verify the render guard runs before DOM mutation, and complete exact-1-MiB, over-limit, BOM, UTF-8, CSV/SVG, mobile and no-console-error assertions; all FEM Node/browser checks must also pass.
2. **P1 — Remaining JSON boundary audit.** Cover null/blank/zero density, independent I-only/K-only in Studio and legacy SI documents, malformed UTF-8, actual BOM bytes, exact/over-1-MiB limits, byte mismatch and failed-read rollback; preserve IDs, units and physical quantities.
3. **P1 — Selected-member isolation and export audit.** Applying section properties changes only the selected member's A/I while preserving every other member and E/density/K; verify CSV quoting/units/BOM/CRLF and SVG XML/accessibility/semantic geometry.
4. **P0 — Spreadsheet formula-reference rewriting.** Add direct regression for relative, absolute and mixed references through row insertion/deletion/sorting; formulas must follow the same logical cells or unsafe mutations must be rejected transactionally with all data unchanged.
5. **Release governance and promotion.** Obtain an eligible independent PR #189 review and authorized verification of enforceable main protection/required checks. Only after exact-head checks and all release gates pass, merge through the ordinary dev-to-main PR and verify exact-main Quality, Pages and hosted behavior.

## 2026-11-23 — TRUSS-IMPORT-SELF-CANCELLATION-CI-FIX (dev; exact-head QA pending)

Started from dev `21c94497506f63b4e2f4e7accc9cac65d9fe2faa` and main `70fc483cb1cec3d2372d37484e4a8ef7942343da`. Re-read root `AGENTS.md`, this plan, the frozen 2026-10-26 inventory, Structural Truss contract/source/tests, current branch refs, PR #189/reviews, exact-head Actions, rulesets and Pages evidence.

Prioritized the observed exact-head failure. Push Quality [#45092387908](https://github.com/saeedsai/ProMathStudio/actions/runs/45092387908) and PR Quality [#45092393490](https://github.com/saeedsai/ProMathStudio/actions/runs/45092393490) both fail in mandatory Static and browser regression step 212, `tests/smoke_truss_studio.py:701`, after the latest-file import-ordering wait times out. The logs show the structural/static suite and tool-search browser check passed before the Truss Studio browser regression timed out; both workflows fail at the same test line.

Root cause: the importer correctly validates the latest request token, but the successful import then calls `renderModel(model)`. `renderModel()` calls `invalidate()`, and `invalidate()` unconditionally invokes `cancelPendingImport()`. That increments the request token and clears pending state for the very import currently being rendered. The following `finishCurrentImport(request)` therefore rejects its own current request, leaving the new model unanalyzed and the status/busy-state acceptance wait unsatisfied.

Fixed the lifecycle without weakening cancellation: `renderModel(model, preserveImportRequest)` passes the active token to `invalidate(preserveImportRequest)`; invalidation skips cancellation only when the supplied token still matches the latest pending request. All normal calls omit the token and retain the existing behavior that edits, examples and unrelated model replacement cancel pending imports. The importer still calls `finishCurrentImport(request)` after rendering, then analyzes. Stale older requests remain rejected by the monotonic token.

Reworked the Truss Studio latest-file regression in `tests/smoke_truss_studio.py` to use a deterministic per-File deferred read instead of a timer and shared `File.prototype.arrayBuffer` override. It starts an older invalid file, waits until that exact read is pending, imports the valid triangle, and requires the analysis status, `aria-busy=false`, A/B/C joint IDs, AC/BC/AB member IDs, 11.21 m total length and three material rows. Only then does it release the older invalid bytes; the exact success status, model IDs, metrics and busy state must remain unchanged. This directly catches the self-cancellation defect and proves stale failure isolation.

Updated the Structural Truss contract, living plan, execution ledger and changelog in the same atomic source/test/docs commit. The standalone Truss page loads adjacent JavaScript assets, so no `index.html` synchronization is needed. Frozen historical inventory remains **166 gaps / 95 partial**. No merge, production deployment or inventory reclassification is claimed.

The local checkout remains absent and bounded local Git cannot resolve `github.com`; no full local Playwright/Node suite is claimed. The changed JS is syntax-compiled in the execution runtime and the regression anchors are verified before commit. Fresh exact-head Push and PR Quality must execute the new deterministic browser regression, all 59 FEM Node tests, Truss exports/mobile checks and the rest of the full workflow.

**NEXT FIVE (status and acceptance tests):**
1. **P0 — Exact-head Quality certification.** Both Push and PR Quality green on this new SHA. Truss Studio step 212 must complete the deterministic deferred-read test, and Truss FEM steps 214/215 must pass all 59 numerical tests, stale-success/stale-failure tests, cancellation, byte integrity, BOM, CSV/SVG, responsive and console-error checks.
2. **P1 — Remaining JSON boundary audit.** Cover null/blank/zero density, independent I-only/K-only in Studio and legacy SI files, malformed UTF-8, actual BOM bytes, exact/over-1-MiB limits, byte mismatch and failed-read rollback; preserve IDs, units and physical quantities.
3. **P1 — Selected-member isolation and export audit.** Applying section properties changes only the selected member's A/I while preserving other members and E/density/K; verify CSV quoting/units/BOM/CRLF and SVG XML/accessibility/semantic geometry.
4. **P0 — Spreadsheet formula-reference rewriting.** Directly test relative, absolute and mixed references through row insertion/deletion/sorting; formulas must follow logical cells or unsafe mutations must fail transactionally with all data unchanged.
5. **Release governance and promotion.** Obtain an eligible independent PR #189 review and authorized verification of enforceable main protection/required checks. Only after all exact-head gates pass, merge through the ordinary dev-to-main PR and verify exact-main Quality, Pages and hosted behavior.

## 2026-11-23 — Truss latest-import request ordering (dev; exact-head QA pending)

- Centralized current-request validation and pending-state settlement so only the latest still-pending file import can update the model, busy state or error status.
- Added Chromium regressions for an older valid read resolving after a newer successful import and an older read failing after a newer successful import; both require latest model, status, solved result and `aria-busy=false` to remain unchanged.
- Starting SHA `397c349d981157343b0665443c6227cd74429087` had green exact-head Push Quality #45087003921 and PR Quality #45087008879, including Truss browser step 215. New commit requires fresh exact-head certification; not released.

## 2026-11-23 — Truss byte-count unit follow-up (dev; exact-head QA pending)

- Added the missing bytes unit after the received count in the production mismatch diagnostic.
- Strengthened the Chromium regression to require the exact terminal (expected N bytes, received M bytes). suffix and stable diagnostic prefix.
- The a19 exact-head Push/PR workflows were still running; fresh final-head Quality is required. Not released.

## 2026-11-23 — Truss byte-mismatch diagnostic prefix CI fix (dev; exact-head QA pending)

- Diagnosed Push Quality #45081246742 and PR Quality #45081250517: both passed 59/59 FEM Node tests but failed at Truss browser step 215 because the wait expected the stable diagnostic prefix to end with a period before the detailed byte counts.
- Restored the stable `Model JSON file size does not match the bytes read.` prefix while retaining exact expected/received byte counts; strengthened the browser assertion to require the prefix and detailed values.
- Updated the Structural Truss contract, hourly plan and execution ledger. Fresh exact-head Push/PR Quality remains required; not released.

## 2026-11-22 — Truss JSON byte-mismatch regression isolation (dev; exact-head QA pending)

- Diagnosed Push Quality [#45075912260](https://github.com/saeedsai/ProMathStudio/actions/runs/45075912260) and PR Quality [#45075916799](https://github.com/saeedsai/ProMathStudio/actions/runs/45075916799): both passed the 59-test FEM Node suite but timed out at Truss browser step 215 waiting for the mismatch status.
- Replaced the second shared `File.prototype.arrayBuffer` patch with an instance-only override on a real File, installed through DataTransfer. The browser now asserts correct immutable File.size, a read ten bytes shorter, exact diagnostics and model/result preservation.
- Snapshot declared file size before the asynchronous read and use it consistently for the 1 MiB preflight and post-read equality check. No solver/schema/limit behavior changed; final-head Push/PR Quality pending; not released.

## 2026-11-22 — Truss import BOM fixture and byte-count diagnostics (dev; exact-head QA pending)

- Diagnosed both exact-head failures [Push #45069666650](https://github.com/saeedsai/ProMathStudio/actions/runs/45069666650) and [PR #45069672010](https://github.com/saeedsai/ProMathStudio/actions/runs/45069672010): the BOM test added three bytes to `File.arrayBuffer()` without changing immutable `File.size`, so the correct byte-integrity guard rejected an impossible synthetic file.
- The Chromium BOM regression now uploads a real BOM-prefixed byte buffer; `File.size` and the actual read agree. Import mismatch errors report expected/received byte counts, with an exact-count browser assertion for a truncated but valid JSON prefix.
- Updated the Structural Truss contract, living plan and execution ledger. No FEM math or import limits changed; exact-head Push/PR Quality pending; not released.

## 2026-11-22 — Truss JSON file-byte integrity (dev; exact-head QA pending)

- The browser importer now requires the actual `ArrayBuffer.byteLength` to match the selected `File.size`, in addition to the existing 1 MiB bounds. A truncated or unexpectedly expanded read is rejected before decoding/parsing.
- Added a Chromium regression where the returned bytes are a valid JSON prefix but shorter than the file's declared size; the previous model, 3 m edit and 0.015 mm solved result must remain unchanged.
- Updated the Structural Truss contract, living plan and execution ledger. Source, browser test and docs are committed atomically on dev; exact-head Push/PR Quality must certify the new regression. Not released.

## 2026-11-22 — Truss import-cancellation status persistence (dev; exact-head QA pending)

- Diagnosed both exact-head failures at mandatory Truss browser step 215: Push [#45058847230](https://github.com/saeedsai/ProMathStudio/actions/runs/45058847230) and PR [#45058851780](https://github.com/saeedsai/ProMathStudio/actions/runs/45058851780). Both fail because preview refresh overwrites the pending-import cancellation status after a model edit; 59/59 FEM Node tests pass in both runs.
- Updated the status helper so preview-only ready/unavailable updates preserve the cancellation notice until an explicit action replaces it. Import tokens, cancellation and solver behavior are unchanged.
- Strengthened the delayed-file Chromium regression with a second explicit `change` event to prove the notice survives repeated input/change invalidations, then verifies the stale read cannot replace the edited model and the 3 m analytical displacement remains 0.015 mm.
- Updated the Structural Truss contract, living plan and execution ledger. Source/test/docs are committed atomically on dev; exact-head Push/PR Quality must rerun. Not released.

## 2026-11-22 — Truss pending JSON import cancellation on model edits (dev)
- Exact-head Push Quality #45058592621 and PR Quality #45058597071 started on commit 57075990cc303ee0d0d5e822f929113fbcec0929; each has 217 steps, with 6 successful and structural tests active at the latest inspection. Full browser/FEM certification remains pending.
- Initial exact-head Quality runs for the implementation-only commit were cancelled when the required living-plan/ledger checkpoint advanced dev; full Quality for the final checkpoint remains pending.



- A pending asynchronous file read is now cancelled when the user edits the active truss model or explicitly analyzes it; a late import can no longer overwrite those changes.
- Cancellation increments the import request token, clears the busy state and reports a non-error status. Successful imports clear pending state before rendering their own model.
- Added a real Chromium regression that delays File.arrayBuffer(), changes the active bar length from 2 m to 3 m, releases the pending read, verifies the edited A/B/AB model remains, and checks the 0.015 mm analytical displacement.
- Updated the Structural Truss compatibility contract, living plan and execution ledger. Exact-head Quality pending; not released.

## 2026-11-22 — Truss JSON optional-property unit provenance (dev)

- Extended the immutable Truss JSON unit descriptor with density (kg/m³), second moment I (legacy m⁴ / Studio mm⁴) and dimensionless effective-length factor K.
- Successful JSON imports now show these optional-property file units in the status message for both legacy SI and Studio formats.
- Added Node descriptor assertions for both formats and Chromium assertions against real legacy/current JSON file imports. FEM calculations, saved-model schema and IDs are unchanged. Exact-head Quality pending; not released.

## 2026-11-22 — Truss seven-shape invalid-preview accessibility (dev; exact-head QA pending)

Updated the section-preview invalid path so the SVG `<desc>` referenced by `aria-labelledby` reports the same unavailable message as the live caption and root `aria-label`. Added mandatory Chromium coverage for all seven section shapes across zero, negative, NaN/empty-number and arithmetic-overflow inputs, asserting stale outline/centroid/axis/dimension metadata is removed and valid recovery restores geometry and accessible description. No FEM equations or saved-model schema changed. Exact-head Push/PR Quality pending.

## 2026-11-22 — Correct CSV helper regression capture scope

Post-commit readback caught the new terminal-byte/empty-Blob fields attached to the existing results/material/SVG aggregate capture rather than the dedicated helper fixture. Restored the aggregate capture unchanged and moved the assertions into the direct helper test. No production export behavior or existing result assertions changed. Exact-head CI must verify the corrected test.

## 2026-11-22 — Truss CSV terminal-record hardening and CI regression repair

Diagnosed both exact-head Quality failures at the direct Truss CSV serializer browser assertion: the test compared decoded Blob text against over-escaped BOM/CRLF strings even though Blob.text() consumes the leading UTF-8 BOM. Corrected the decoded-text assertion while retaining raw-byte checks for exactly one BOM. The production CSV helper now ensures non-empty normalized CSV ends in CRLF, while empty CSV remains BOM-only. Added browser checks for mixed newline input without a terminal separator, final CRLF bytes and empty content. Full exact-head Push/PR Quality remains pending.

## 2026-11-22 — Truss SVG semantic geometry metadata

Repaired the exact-head Truss browser regression by replacing a stale six-line expectation for the imported one-member model with an exact semantic assertion: one original member, one deformed member, one load-vector shaft and two arrowhead segments. The exported SVG now carries stable geometry-role, member/node, force-state and load-component metadata. Existing visual geometry, FEM calculations and CSV/SVG accessibility assertions remain unchanged. Full Push/PR Quality is pending on the new dev head.

## 2026-11-22 — TRUSS-CSV-SERIALIZER-DIRECT-REGRESSION

Added a direct Chromium regression for the production CSV serializer's new normalization behavior. The browser harness exposes the otherwise private helper only in its injected test copy (the shipped UI remains scoped), feeds a fixture containing a pre-existing UTF-8 BOM plus LF, lone CR and CRLF separators, and captures the actual generated Blob. Acceptance requires exactly one EF BB BF sequence, preserved CSV MIME type and canonical CRLF output. This complements the actual results/material-schedule exports and their current-model/SI assertions. The previous material-schedule correction is explicit: 1000 mm² in the editor exports as 0.001 m² in the SI schedule. The isolated V8 helper fixture already passed; the fresh exact-head browser workflows must execute this committed test.

## 2026-11-22 — TRUSS-MATERIAL-CSV-SI-AREA-ASSERTION

A final source-level review of `exportMaterialCSV` confirmed that the material schedule intentionally exports physical area in SI m², while the editor field is mm². Corrected the new browser assertion accordingly: the imported editor value remains 1000 mm², and the material CSV must contain 0.001 m². Added independent checks for 0.002 m³ member volume, 100 kN/mm EA/L and 15.7 kg mass, preserving the existing density/I/K assertions. This prevents a unit-system mismatch in the regression itself; the canonical FEM and export implementation are unchanged. The corrected exact-head Push and PR Quality must execute the browser check.

## 2026-11-22 — TRUSS-CSV-STATEFUL-EXPORT-CI-FIX

Inspected both exact-head failures for dev `b1c0890850d159c11e4930faa46f401e43ea7f26`: Push Quality [#45025447623](https://github.com/saeedsai/ProMathStudio/actions/runs/45025447623) and PR Quality [#45025452461](https://github.com/saeedsai/ProMathStudio/actions/runs/45025452461). Both fail only in `tests/smoke_truss_fem.py` at the CSV assertions after the browser test has deliberately imported a one-member legacy-SI bar (AB). The old assertions still expected four seven-column result rows and four material CSV rows from the earlier three-member triangle fixture. The actual export correctly reflects the current AB model; the 59/59 canonical FEM Node tests pass in both runs. Corrected the regression to require exactly the CSV header plus one AB member row, check its 1 kN axial force and 1 MPa stress, and require the material header plus one AB/A/B row with the imported 2 m, 0.001 m² (1000 mm² in the editor), 200 GPa, density, I and K values. These are model-specific assertions, not weakened counts.

Also hardened the real CSV download source: the shared serializer strips any existing leading BOM, normalizes CRLF/lone-CR/lone-LF record separators to CRLF, then prepends exactly one UTF-8 BOM. Chromium now counts BOM byte sequences in each raw downloaded Blob and requires exactly one, while retaining CRLF-only, final-CRLF, exact headers, units, parsed field counts, and SVG checks. This is a production source behavior change plus focused browser regression. No FEM solver or model schema changed.

The local workspace has no repository checkout, so full Playwright execution remains unavailable locally. Source/test/docs were prepared as one atomic dev commit; fresh exact-head Push and PR Quality must execute the browser suite. Historical inventory remains frozen at 166 gaps / 95 partial. Main remains unchanged; PR #189 has no submitted independent reviews, branches report unprotected, rulesets are empty, and branch-protection read is unavailable to the connected integration. No merge, direct main update, force push or safeguard bypass.

**NEXT FIVE (acceptance):**
1. Verify both exact-head Push and PR Quality for this commit; require all 218 steps green, especially the imported one-member CSV assertions, exactly-one-BOM raw bytes, CRLF, SVG export, all 59 FEM Node tests and 390px responsive coverage.
2. Complete the seven-shape invalid-state/accessibility audit: zero, negative, NaN and overflow dimensions clear stale previews and recover; dimension/axis labels remain keyboard and screen-reader accessible at 390px and desktop.
3. Finish JSON compatibility boundaries: blank/zero density, independent I/K presence, Unicode/BOM and malformed/oversized rollback; preserve physical quantities and IDs.
4. Obtain an eligible independent review of PR #189 and authorized verification of enforceable main protection and required checks; do not self-approve or bypass unavailable administration.
5. Only after every gate passes, merge through the ordinary dev-to-main PR and verify exact-main Quality, GitHub Pages deployment and hosted relative assets/downloads.

## 2026-11-22 — TRUSS-JSON-ANALYZE-EVENT-GUARD

Follow-up to the unit-provenance UI notice: the Analyze button registers `analyze` as a DOM event listener, so the browser supplies a MouseEvent argument. Hardened the optional notice parameter to append text only when it is a non-empty string; ordinary Analyze clicks therefore retain the plain analysis-complete status rather than rendering an event object. Added a Chromium assertion that the status never contains `[object`. The actual legacy/current JSON import notices and their file-input round-trip assertions remain unchanged. This follow-up is committed to dev; exact-head CI is required.

## 2026-11-22 — Truss Studio JSON import unit provenance and UI round-trip
- Successful imports now report whether legacy SI values were converted to Studio editor units or Studio units were retained; failed analysis continues to display its error.
- Added a Chromium file-input regression for legacy N/Pa/m²/m⁴ conversion, density/I/K preservation, the 0.01 mm bar reference, current JSON export/re-import and mixed-unit rollback without changing the prior model.
- Dev-only; exact-head Push/PR Quality pending. No FEM equations or main application bundle changed.

## 2026-11-22 — Truss SVG export CI repair and deterministic aspect ratio
- Fixed the Chromium regression to parse the actual SVG download (third Blob), not the material-schedule CSV; added an explicit SVG MIME assertion.
- Exported standalone SVG now declares `preserveAspectRatio="xMidYMid meet"`; browser regression verifies the 620×380 viewBox remains proportionally fitted in the 1240×760 output.
- Retained all XML, accessibility, geometry, CSV and FEM assertions. Previous exact-head Push/PR workflows exposed the test-index defect; corrected candidate requires fresh full Quality. Dev-only, not released.

## 2026-11-22 — Truss CSV BOM regression hardening
- Assert the UTF-8 BOM from actual Blob prefix bytes instead of assuming Blob.text() preserves U+FEFF; parse decoded CSV after optional BOM stripping.
- No application behavior change; exact-head Quality pending.

## 2026-11-22 — Truss Studio UTF-8 CSV downloads

- Added a shared CSV download helper that prepends a UTF-8 BOM to both results and material-schedule exports, improving spreadsheet detection of Unicode engineering unit symbols.
- Preserved existing quoted fields, doubled quote escaping, CRLF records, final CRLF and CSV MIME type; SVG downloads are unchanged.
- Added Chromium coverage of actual Blob prefix bytes and Python CSV parsing for result/material headers, units and field counts. Implemented on dev; exact-head Quality pending, not released.

## 2026-11-22 — Truss Studio UTF-8 import byte-boundary hardening
- Centralized the standalone UI's 1 MiB byte budget and validate both File.size before reading and actual ArrayBuffer.byteLength after reading.
- Added exact 1 MiB multibyte acceptance, +1-byte rejection, pre-read ASCII/multibyte rejection, and underreported-size fallback regressions; rejected imports preserve the current model.
- Added Node and Chromium regression coverage plus compatibility documentation. Exact-head Quality pending; dev-only, not released.

## 2026-11-22 — Truss Studio strict UTF-8 model import
- Read bounded model files as bytes and decode with fatal UTF-8 validation; malformed byte sequences are rejected instead of silently replacing bytes inside node/member identifiers.
- Preserve a leading UTF-8 BOM for the canonical importer to strip; keep the 1 MiB file-size guard and stale-import request ordering.
- Updated Chromium regressions for byte-read race ordering, real BOM bytes, invalid UTF-8 rejection and model rollback. Exact-head Quality pending; dev-only, not released.

## 2026-11-22 — Truss Studio seven-shape canonical preview metadata
- 2026-11-22 — TRUSS-SEVEN-SHAPE-DIMENSION-LABEL-ACCESSIBILITY: centralized all SVG section-dimension labels across seven previews with explicit text roles and value-bearing accessible names; added exact expected-label/value-parity Chromium assertions for every shape. FEM calculations unchanged; exact-head Quality pending.

- Standardized bounding width/height, area and centroid metadata across all seven supported section outlines; added circle diameters and hollow-section inner dimensions.
- Added canonical centroid coordinates to the centroid marker and centroidal/principal axis lines.
- Added explicit accessible names and text roles to Ixx/Iyy axis labels.
- Added a Chromium regression for all seven shapes covering independent area/centroid references, metadata parity, SVG title/description/caption synchronization, accessible labels and 390px no-overflow.
- Dev-only; exact-head Push/PR Quality pending. No FEM formulas changed and no release claimed.

## 2026-11-22 — Truss Studio L-angle second reference and canonical outline metadata

- Added machine-readable L-angle SVG outline metadata for B/H/t, area and canonical centroid.
- Added independent analytical references for an asymmetric 120×70×12 mm section and a near-limit valid 120×70×69.9 mm section; the exact 70 mm boundary remains rejected.
- Extended Chromium coverage for both principal-axis angles/centroid, accessible caption parity, metadata, invalid clearing/recovery and 390px no-overflow. Exact-head Quality pending; dev-only, not released.

## 2026-11-22 — Truss Studio L-angle principal-axis caption precision and regression

- Fixed the observed exact-head browser failure by formatting both L-angle principal-axis caption angles to a consistent three decimal places (57.953° / 147.953°); the prior five-significant-digit formatter displayed the minor angle as 147.95°.
- Added machine-readable `data-axis-angle-deg` metadata to both SVG principal-axis labels and Chromium assertions that label angles match their corresponding axis lines.
- Preserved FEM mathematics, accessible names, centroid/orthogonality checks and invalid-input recovery. Exact-head Quality pending; not released.

## 2026-11-22 — Truss Studio L-angle SVG label accessibility and CI correction

- Fixed the exact-head Chromium regression by reading SVG I1/I2 `<text>` content with Playwright `text_content()` instead of HTMLElement-only `inner_text()`.
- Added explicit accessible names and text roles to the major/minor principal-axis SVG labels; added assertions for the visible I₁/I₂ glyphs and their accessible names.
- Preserved the independent centroid, orthogonality, invalid clearing and recovery checks. No FEM formulas or test requirements were weakened. Exact-head Quality pending; not released.

## 2026-11-22 — Truss Studio L-angle principal-axis CI repair and centroid metadata

- Fixed the observed exact-head browser regression: Playwright-evaluated SVG endpoint/centroid objects are Python dictionaries, so assertions now use keyed access rather than attribute access.
- Added canonical FEM centroid coordinates in millimetres to both principal-axis SVG lines (data-centroid-x-mm, data-centroid-y-mm) for machine-readable geometry.
- Strengthened the Chromium regression to verify both axis midpoints and both axes' canonical centroid metadata against the asymmetric L-angle reference. Existing mathematical, orthogonality and invalid-recovery assertions remain.
- Updated the Truss FEM contract, hourly plan and execution ledger. Exact-head Quality pending; not released.

## 2026-11-22 — Truss Studio L-angle dual principal-axis preview

- Extended the live L-angle SVG to draw both perpendicular principal axes through the canonical centroid: major I1 at the FEM helper angle and minor I2 at +90°.
- Added distinct axis metadata/labels and synchronized SVG description/accessibility caption.
- Added Chromium regression for orthogonality, centroid intersection, I1/I2 labels, invalid clearing and valid-input recovery. Exact-head Quality pending; not released.

## 2026-11-22 — Truss Studio I-section preview

- Added a live accessible symmetric I-section SVG using canonical FEM properties: two full-width equal flanges, centered web, B/H/tw/tf dimensions, centroid and perpendicular Ixx/Iyy axes.
- Added immediate web/flange thickness updates and invalid tw >= B / 2·tf >= H clearing with accessible guidance and valid-input recovery.
- Added a focused 390px Chromium regression for outline geometry, dimensions, centroid, axes, accessibility, live edits and invalid recovery. FEM solver formulas and the main standalone bundle are unchanged; exact-head Quality pending.
## 2026-11-21 — Truss Studio open-channel preview

- Added a live accessible open-channel SVG using canonical FEM section properties: web-left/flanges-right geometry, B/H/tw/tf dimensions, offset centroid and perpendicular Ixx/Iyy centroidal axes.
- Added live web/flange thickness updates and invalid tw >= B / 2·tf >= H clearing with accessible guidance and valid-input recovery.
- Added a focused 390px Chromium regression for path orientation, dimensions, centroid, axes, live edits, invalid recovery and caption/accessibility parity. No FEM solver formulas changed; exact-head Quality pending.

## 2026-11-21 — Truss Studio hollow-rectangle preview

- Added a live accessible SVG for concentric hollow rectangles using canonical FEM section properties: outer/inner outlines, B/H/bi/hi dimensions, centroid and centroidal Ixx/Iyy axes.
- Added immediate inner-dimension updates and invalid wall-thickness clearing/recovery with synchronized visible and accessible status.
- Added a focused 390px Chromium regression for dimensions, centroid, visible void fill, inner dimension guides, live edits, invalid geometry and accessibility. No FEM solver formulas changed.
- Follow-up source review corrected inner-guide coordinate scope before exact-head Quality; the test now asserts both guides and the visible void fill.

- 2026-11-21 — TRUSS-HOLLOW-CIRCLE-SVG-PREVIEW-414: Added a live accessible concentric hollow-circle preview using canonical section properties, with outer/inner outlines, Do/Di dimensions, centroid, Ixx/Iyy axes, live updates, invalid/overflow clearing and recovery. Added 390px browser regressions for geometry, centroid, labels, resizing, invalid wall thickness, accessible-name parity and recovery. Existing Node tests retain analytical hollow-circle and underflow/overflow coverage; exact-head Quality pending.
- 2026-11-21 — TRUSS-SOLID-CIRCLE-SVG-PREVIEW-413: Added frozen canonical centroids for solid/concentric hollow circles and a live accessible solid-circle SVG preview with D dimension, centroid, perpendicular Ixx/Iyy axes, live edits and invalid-state recovery. Added analytical Node centroid/immutability regressions and 390px browser coverage for outline, axes, labels, live update, invalid clearing, accessibility and recovery. Exact-head Quality pending.
- 2026-11-21 — TRUSS-RECTANGLE-CENTROID-CI-FIX-412: Fixed the canonical section-properties contract to return immutable centroid coordinates for solid and concentric hollow rectangles; added analytical Node regressions. Repairs exact-head Truss Studio browser step 212 where the rectangle SVG dereferenced a missing centroid before drawing; existing browser coverage remains intact. Exact-head QA pending.
- 2026-11-21 — TRUSS-RECTANGLE-SVG-PREVIEW-411: Extended the accessible live section sketch to solid rectangles using canonical section properties; shows B/H dimensions, centroid and Ixx/Iyy centroidal axes, updates on edits, and clears invalid geometry. Added 390px browser coverage for analytical centroid, axis/label presence, live update, invalid clearing, accessible-name parity and recovery. Previous exact-head Push/PR Quality for the L-angle fix passed all 431 steps; new-head QA pending.
- 2026-11-21 — TRUSS-LANGLE-PREVIEW-INVALID-STATE-CI-FIX-410: Made invalid L-angle dimensions consistently announce “Preview unavailable” in both the visible caption and SVG accessible name; strengthened the 390px browser regression for invalid t=80 mm, stale-outline removal and accessible-name parity. Fixes exact-head Quality step 212 failures #44922195676/#44922200989 without changing FEM mathematics.
- 2026-11-21 — TRUSS-LANGLE-SVG-PREVIEW-AND-CI-REGRESSION-409: Added an accessible live L-angle cross-section SVG with B/H/t dimensions, centroid and major principal axis; invalid dimensions clear the preview. Repaired the exact-head browser regression by checking native option hidden state and actual selection instead of rendered visibility. Added 390px preview/rollback coverage; exact-head Quality pending.
- 2026-11-21 — TRUSS-SECTION-MODULUS-RADIUS-OF-GYRATION-406: Added validated Sx/Sy, extreme-fibre distances cX/cY and rx/ry to all six supported Truss Studio section shapes; displays geometric values in the standalone UI and adds analytical Node plus 390px Chromium regressions. FEM/Euler solver unchanged; exact-head Quality pending.
- 2026-11-21 — TRUSS-OPEN-SECTION-PROPERTIES-405: Added canonical open-channel and I-section area, centroid and centroidal Ixx/Iyy using non-overlapping rectangles and the parallel-axis theorem; added selected-axis UI application, analytical Node regressions, 390px browser coverage and corrected the stale hollow-section rollback expectation that failed exact-head Quality #44902015247/#44902019224.
- 2026-11-21 — TRUSS-HOLLOW-SECTION-PROPERTIES-404: Added validated concentric hollow rectangular/circular section helpers; rectangles report both centroidal Ixx/Iyy and allow the UI to apply either axis, while circular moments remain equal. Added analytical, invalid-wall-thickness, overflow/underflow, member-isolation and 390px browser regressions. Exact-head Quality pending.
- 2026-11-21 — TRUSS-OPTIONAL-EULER-PREVIEW-UX-CI-FIX-403: Kept valid geometry/material previews available when only I or K is supplied, while clearly explaining that Euler Pcr requires both; added Chromium I-only/K-only preview, blank-Pcr and completed-pair restoration regressions. Fixes observed exact-head Quality failures #44892693133/#44892698250 without weakening assertions.
- 2026-11-21 — TRUSS-SECTION-PROPERTY-HELPERS-402: Added validated solid rectangle and solid circle section-property helpers (area mm², centroidal I mm⁴) to the canonical Truss FEM API and a standalone UI to apply both values to one selected member; added analytical Node and 390px Chromium regressions for reference values, invalid-input rollback, member isolation and I-only preview with K left unspecified. I/K are independently optional; Euler Pcr is calculated only when both are supplied. Exact-head Quality pending.
- 2026-11-21 — TRUSS-EULER-UI-PRECISION-CI-FIX-394: Fixed the observed browser mismatch by displaying Euler Pcr in kN to five significant digits (493.48 kN for the pinned 2 m reference); added K=2 → 123.37 kN and K=1 restoration regression. Solver and full-precision CSV output unchanged.
- 2026-11-21 — TRUSS-SECTION-MOMENT-DISPLAY-CI-FIX-393: Fixed the exact-head Truss Studio browser mismatch by rendering safe integer second moments as full decimal mm⁴ values while retaining compact significant-digit formatting for fractional values; added a fractional/integer Chromium regression.
- 2026-11-21 — TRUSS-LEGACY-API-SHAPE-392: Preserved the documented legacy `TrussStudio.solve` member object shape while keeping compression-only Euler metrics on the canonical FEM API; added an exact-key regression.
- 2026-11-21 — TRUSS-RESULTS-CSV-CRLF-FIX-391: Corrected the post-solve results CSV exporter to emit actual CRLF rather than a double-escaped literal, and added a browser regression for the results CSV terminator.
- 2026-11-21 — TRUSS-EULER-POST-SOLVE-COMPARISON-390: Added compression-only ideal Euler utilization Pcomp/Pcr and load ratio Pcr/Pcomp to solved member results/table/CSV, with explicit tension, zero-demand and missing-I/K states that avoid division. Fixed the exact-head browser regression to assert the current 13-column material schedule; added Node and Chromium below/above-critical-load coverage.
- 2026-11-21 — TRUSS-EULER-CSV-PRECISION-FIX-389: Corrected the browser CSV regression's 16-significant-digit Euler reference to match the production JavaScript numeric formatter; production behavior unchanged.
- 2026-11-21 — TRUSS-EULER-CSV-TEST-ESCAPE-FIX-388: Corrected the new Node Euler CSV regression to split on actual CRLF characters; production behavior unchanged.
- 2026-11-21 — TRUSS-EULER-CRITICAL-LOAD-387: Added optional I/K-driven ideal Euler critical-load estimates (Pcr = π²EI/(KL)²) to the non-solving Truss Studio material preview and CSV, with current/legacy SI conversion, guarded validation, analytical and responsive regressions. No buckling utilization or code-compliant design check is claimed.
- 2026-11-21 — TRUSS-MATERIAL-CSV-REGRESSION-ASSERTION-FIX-386: Corrected an over-escaped literal in the new Node CSV regression to assert quoted cells directly; the existing contract regression still verifies CRLF. Production CSV formatting unchanged.
- 2026-11-21 — TRUSS-MATERIAL-CSV-NUMERIC-FORMATTING-CI-REPAIR-385: Fixed the exact-head Truss Studio browser failure by serializing finite CSV numeric cells to 16 significant digits, removing binary floating-point tails without materially reducing engineering precision. Added Node regression for the 15.7 kg analytical bar mass and a 16-digit 2/3 m length. Existing Chromium CSV assertion retained.
# Changelog

- 2026-11-21 — TRUSS-MATERIAL-DENSITY-MASS-384: Added optional per-member density (kg/m³) and derived mass (kg) to the validated non-solving truss inspector, legacy SI import, editable standalone member table and material CSV. Unspecified density remains blank; negative/non-finite density and mass overflow are rejected. Added analytical, legacy, CSV, invalid-input and responsive regressions.

- 2026-11-21 (dev, exact-head QA pending): Truss Studio model imports now ignore stale asynchronous file reads/errors when a newer selection supersedes them. Added a delayed-malformed/fast-valid overlapping-import Chromium regression and an explicit terminal-status wait to remove a timing-dependent CI assertion. No solver behavior or validation was weakened.
## 2026-11-21 — Truss material elasticity and axial stiffness\n- Extended the validated pre-solve member schedule with elastic modulus (GPa) and axial stiffness EA/L (kN/mm), reusing the solver's canonical validated stiffness in SI. Added analytical bar/triangle, legacy-SI, immutable metric, CSV and browser-table regressions.\n\n- 2026-11-21 — TRUSS-MATERIAL-SCHEDULE-CSV-TEST-FIX-381: Corrected the browser regression to assert the actual CRLF terminator using `chr(13) + chr(10)`; this fixes an over-escaped test literal without changing the exported CSV or weakening validation.
- 2026-11-21 — TRUSS-MATERIAL-SCHEDULE-CSV-380: Added a validated, non-solving per-member material schedule CSV export in explicit SI units (member/joint IDs, centreline length, cross-sectional area and axial volume), with RFC-style quoted cells and CRLF records. Added analytical/legacy-SI/unstable/invalid Node regressions and keyboard-driven browser download, exact data/header and invalid-model refusal checks.
- 2026-11-20 — TRUSS-CI-LEGACY-AND-MEMBER-METRICS-377: Corrected the failing legacy-SI browser fixture expectations to match its actual 2 × 1 m geometry (4.828 m total member length, 0.004828 m³ axial volume); added immutable per-member SI metrics to the validated inspector and an accessible Truss Studio material-breakdown table. Added Node analytical/legacy parity and Chromium member-row, invalid-recovery and 390px overflow regressions; per-member mapping runs after the existing aggregate overflow guard to preserve diagnostic precedence.
- 2026-11-20 — TRUSS-PREVIEW-MATERIAL-METRICS-376: The pre-solve Truss Studio summary now shows total centreline member length (m) and summed axial-member volume Σ(L·A) (m³), using the validated SI inspector without invoking the solver. Browser regressions cover analytical bar/triangle values, legacy-SI import parity and 390px wrapping.
- 2026-11-20 — TRUSS-PIVOT-ASSERTION-REGEX-FIX-375: Corrected the new singular-stiffness regression's literal-parenthesis regex so it matches the solver's diagnostic exactly.
- 2026-11-20 — TRUSS-SCALED-PIVOT-MECHANISM-FIX-374: Corrected scaled partial pivoting to compare each candidate pivot with its original row scale, detecting rank-deficient trusses whose free DOFs all have nonzero stiffness diagonals. Added an analytical triangular-mechanism regression; stable reference tests retained.
- 2026-11-20 — TRUSS-PRE-SOLVE-GEOMETRY-PREVIEW-373: Added a non-solving, accessible SVG geometry preview for valid truss models, including unstable models. The preview shows joints, members, supports, applied-load arrows, topology counts, isolated joints, geometry bounds and resultant loads; invalid edits clear stale geometry. Added keyboard and 390px browser regressions for preview, instability, validation and recovery.
- 2026-11-20 — TRUSS-IMPORT-ASYNC-STATUS-CI-FIX-372: Truss Studio now announces pending JSON imports with an accessible busy state. Added deterministic browser coverage for pending reads, malformed-file errors and transactional model preservation; fixes the async File.text() race in the prior browser regression.
- 2026-11-20 — TRUSS-JSON-UI-VALIDATION-371: Truss Studio now uses the canonical validated JSON importer/exporter, including BOM and 1 MiB safeguards; invalid model exports are blocked and malformed imports leave the current model intact. Added focused 390px browser regression coverage. Exact-head CI for the new commit pending.
- 2026-11-20 — TRUSS-FREE-LOAD-DOF-370 (implemented on dev, exact-head CI pending): Added freeLoadedDofCount to validated non-solving truss JSON preview, separating loads at free translations from restrained loads. Regression covers free/restrained partition, zero loads, legacy SI, malformed JSON and analytical bar. Previous head 728d429dec6a69be0d6d0406d692b6e5ebc5c2a0 had PR Quality #44769546700 green; PR #189 still unreviewed, main/Pages unverified. Frozen inventory remains 166 gaps / 95 partial. NEXT FIVE acceptance: (1) exact-head push/PR Quality including truss Node and browser checks green; (2) eligible independent PR #189 approval and branch-protection verification; (3) ordinary authorized PR merge and exact-main Quality green; (4) Pages main-SHA publication and hosted desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with malformed-file, keyboard and mobile regressions.
- 2026-11-20 — TRUSS-RESTRAINED-LOADS-CI-FIX-369: Exact-head Quality #44759092143 failed at Node truss step 214 with `ReferenceError: Cannot access 'test' before initialization` because the new regression was prepended above its `node:test` import. Moved it below imports and added explicit zero-valued restrained-load regression without weakening assertions. Baseline dev 95e40043f0d97828d7b7cc8123eb2318e4990b28; full new-head CI pending; PR #189 still has no reviews, main/Pages unverified. Historical inventory remains frozen at 166 gaps / 95 partial. NEXT FIVE acceptance: (1) corrected exact-head push and PR Quality green including Node truss test and browser suites; (2) independent eligible PR #189 approval and protection verification; (3) ordinary authorized PR merge with exact-main Quality green; (4) Pages publication tied to main SHA and hosted desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with malformed-file, keyboard and mobile regressions.
- 2026-11-20 — TRUSS-RESTRAINED-LOADS-368: Added `restrainedLoadedDofCount` to the non-solving truss JSON preview so supported-node loads can be distinguished from free-DOF loads. Focused Node regression covers fixed X/Y loads, mixed free/restrained loads, legacy SI parity, malformed JSON and analytical displacement. Baseline dev `578d13dea98d4a18e6bc1eaccfd768a6b36d65b2`; prior exact-head PR Quality #44749285451 passed; new-head CI pending. PR #189 remains open with no reviews, main/Pages unverified. Historical inventory frozen at 166 gaps / 95 partial. NEXT FIVE acceptance: (1) new-head push/PR Quality green including restrained-load regression; (2) independent eligible PR #189 approval and verified protection requirements; (3) ordinary authorized PR merge and exact-main Quality green; (4) Pages publication tied to main SHA and hosted desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with malformed-file, keyboard and mobile regressions.
- 2026-11-20 — TRUSS-ISOLATED-NODES-367: Added `isolatedNodeCount` to validated non-solving truss JSON preview, distinguishing disconnected members from nodes with no incident members; retains legacy SI compatibility. New focused Node regression covers connected bar, isolated nodes, separate bars, legacy import, malformed JSON and analytical displacement. Baseline dev 9240959119f548b18cc8a77e3259cdd3620de79e; exact-head PR Quality #44741050253 passed before this change. Full new-head Quality pending; PR #189 still has zero reviews and main/Pages release unverified. Historical 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) new-head push/PR Quality all green including isolated-node regression; (2) eligible independent PR #189 review and verified protections; (3) ordinary authorized dev-to-main merge and exact-main Quality green; (4) Pages main-SHA publication and hosted desktop/390px browser smoke; (5) synchronized browser truss JSON import/preview/export/solve with malformed-file, keyboard and mobile regressions.
- 2026-11-20 — TRUSS-TOPOLOGY-COMPONENTS-366 (implemented on dev; exact-head CI pending): Non-solving truss JSON inspector now reports connectedComponentCount from validated member adjacency, counting isolated nodes as separate components. Focused Node regression covers a connected axial bar, two disjoint bars plus isolated node, reconnection, legacy SI parity, malformed JSON and analytical displacement. Baseline dev d908681313eba0acd801a825ed0c0f889ace3f02; prior exact-head PR Quality #44732523060 succeeded; PR #189 has no submitted reviews; Pages publication not verified. Frozen historical inventory 166 gaps / 95 partial unchanged. NEXT FIVE with acceptance: (1) exact new-head push and PR Quality green including topology regression; (2) eligible independent PR #189 approval and protection verification; (3) ordinary authorized dev-to-main PR merge with exact-main Quality green; (4) Pages publication of main SHA and hosted desktop/390px browser smoke; (5) synchronized browser truss JSON import/preview/export/solve UI with malformed-file and keyboard regressions.
- 2026-11-20 — TRUSS-LOADED-DOF-PREVIEW-365: Added loadedDofCount to non-solving truss JSON preview, counting independently nonzero x/y applied-load components including restrained DOFs. Node regression covers supported loads, Studio/legacy parity, zero-load unstable preview, analytical bar and malformed JSON. Baseline dev 7712f05ab2c0a003f9e62387bbd28caa79bae42d; PR Quality #44723556875 green; new-head Quality pending; PR #189 has zero reviews, Pages unverified. Frozen historical 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) exact new-head push/PR Quality green including loaded-DOF regression; (2) independent eligible PR #189 review and branch protection verification; (3) ordinary authorized PR merge with main Quality green; (4) Pages publication at main SHA plus desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard regressions.
- 2026-11-20 — TRUSS-DOF-PREVIEW-364: Added freeDofCount to non-solving truss JSON preview, complementary to fixedDofCount; counts x/y translational DOFs without claiming structural stability. Focused regression covers axial bar, unstable bar, legacy SI, analytical displacement and malformed JSON. Baseline dev b076f7f510312e5b41fc868825a4fb4db8b55d51; exact-head PR Quality #44715379182 passed; PR #189 has no submitted reviews; Pages unverified. Frozen inventory 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) exact new-head push/PR Quality green including DOF regression; (2) independent eligible PR #189 approval and protections verified; (3) authorized ordinary PR merge and exact-main Quality green; (4) Pages main-SHA publication and hosted desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard regressions.
- 2026-11-20 — TRUSS-MEMBER-VOLUME-CI-FIX-363: Exact-head push/PR Quality #44706773481/#44706781292 failed in truss test at line 570: fixture area=1e308 mm² caused stiffness overflow during validation before preview volume overflow. Corrected fixture to 1e308 m length, 1e12 mm² area, valid E*A/L=2e-291 N/m and non-finite L*A; explicitly validate per-member volume before summing. Isolated Node arithmetic check passed; full exact-head Quality pending. dev baseline 915d70f1673d9dc5c3a7e25db19d775e7a906988; main 70fc483cb1cec3d2372d37484e4a8ef7942343da; PR #189 lacks eligible approval, Pages not verified. Historical 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) new exact-head push and PR Quality pass focused truss plus browser suite; (2) eligible independent PR #189 approval and branch-protection confirmation; (3) authorized ordinary PR merge with exact-main Quality green; (4) Pages main-SHA publication and desktop/390px hosted smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard tests.
- 2026-11-20 — TRUSS-MEMBER-VOLUME-362: Added totalMemberVolume (m³) to validated non-solving truss JSON preview, using SI member lengths and cross-sections with finite-result guard. Regression covers analytical bar, triangle, legacy SI parity, unstable preview, overflow and malformed JSON. Baseline dev bc6d7de265812aabbb969004a8dbe4e453380cf8; exact-head push Quality #44699123988 and PR Quality #44699130977 passed. New-head QA pending; PR #189 has zero reviews; Pages/main publication not verified. Frozen historical 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) exact new-head push and PR Quality green including volume regression; (2) eligible independent PR #189 approval and verified protections; (3) ordinary approved PR merge and exact-main Quality green; (4) Pages published main SHA and desktop/390px hosted smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard regressions.
- 2026-11-20 — TRUSS-MEMBER-LENGTH-361: Added SI-metre totalMemberLength to validated, non-solving truss JSON preview; finite-sum guard rejects overflow. Regression covers analytical bar, triangle perimeter, legacy SI parity, oversized sum and invalid JSON. Baseline dev ae93ac4666fd221f5ceaf92d52f4568f697a49f4; exact-head PR Quality #44691329168 passed; new-head CI pending. PR #189 unreviewed, main Pages unverified. Frozen historical 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) exact new-head push/PR Quality green including length test; (2) independent eligible PR #189 approval and protection verification; (3) ordinary authorized PR merge and exact-main Quality green; (4) Pages main-SHA verification and hosted desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard regressions.
- 2026-11-20 — TRUSS-FRAME-DIAGONAL-360-FIX: Correct the diagonal-overflow fixture: each finite span is 1.5e308 m, so hypot exceeds Number.MAX_VALUE while member AB remains valid. Prior fixture 1.1e308 m spans did not overflow. Exact-head CI for this correction pending; frozen inventory 166 gaps / 95 partial unchanged.

- 2026-11-20 — TRUSS-FRAME-DIAGONAL-360: Added finite geometry diagonal (metres) to immutable truss JSON preview bounds for automatic viewport fitting; reject overflow of combined valid width/height. Focused regression covers horizontal and diagonal geometry, overflow, analytical bar and invalid JSON. Baseline dev bbc6eee0f72d022e00a1f35148ad0a094093668b; main 70fc483cb1cec3d2372d37484e4a8ef7942343da. Exact baseline PR Quality #44685050935 passed; new-head CI pending. PR #189 has zero submitted reviews; Pages unverified. Frozen historical inventory 166 gaps / 95 partial unchanged. NEXT FIVE acceptance: (1) new exact-head push/PR Quality green including diagonal regression; (2) independent eligible PR #189 review and protections verified; (3) ordinary authorized PR merge and main Quality green; (4) Pages published main SHA plus desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard regressions.

- 2026-11-20 — TRUSS-FRAME-CENTER-359 (dev QA pending): Added finite geometry centerX/centerY in SI metres to inspectJSON bounds using validated spans (avoids naive min+max overflow); updated exact bounds regression and added extreme-coordinate/flat-shape test. Previous dev a14361d333967b51a421f68fdfa884c46c3760c2, main 70fc483cb1cec3d2372d37484e4a8ef7942343da. Prior exact-head PR Quality #44678470866 green; new exact-head CI pending; local full suite unavailable. PR #189 open with zero reviews; Pages unverified. Frozen historical 166 gaps / 95 partial unchanged. NEXT FIVE with acceptance: (1) new exact-head push/PR Quality green including center tests; (2) eligible independent PR #189 approval and protection verification; (3) ordinary authorized PR merge and main Quality green; (4) Pages publication SHA plus desktop/390px smoke; (5) synchronized browser truss JSON import/preview/export/solve with invalid-file and keyboard regressions.

- 2026-11-20 — TRUSS-SPANS-CI-FIX-358: Fix exact-head Quality #44671902011 failure (step 214): overflow fixture had invalid member length before reaching bounds. Retain valid AB member and add two distant fixed, unconnected nodes; verify width overflow without relaxing parser. Source comment clarifies bounds include all validated nodes. Baseline dev 5cb6eb967c5c1ff79fec29ee307d5c1d0ffa1a7c; main 70fc483cb1cec3d2372d37484e4a8ef7942343da. Local full Node/Chromium unavailable; new exact-head CI pending. PR #189 zero reviews, Pages unverified. Frozen 166 gaps / 95 partial. NEXT FIVE (acceptance): (1) exact-head push/PR Quality green including truss Node regression; (2) eligible independent PR #189 approval and protection verification; (3) ordinary approved PR merge and main Quality green; (4) Pages SHA publication plus desktop/390px smoke; (5) synchronized truss JSON browser workflow with invalid-file and keyboard tests.

- 2026-11-20 — TRUSS-JSON-SPANS-357 (dev QA pending): Add finite immutable width/height in metres to non-solving truss JSON preview; reject coordinate-span overflow. Regression covers signed bounds, flat model, legacy SI parity, overflow, analytical bar and invalid JSON. Baseline dev 85ebf65d3f601606b8a898fcc95258c57e6fe304; main 70fc483cb1cec3d2372d37484e4a8ef7942343da. Prior exact-head PR Quality #44665054401 passed; PR #189 zero reviews; Pages unverified. Frozen historical inventory 166 gaps / 95 partial unchanged. NEXT FIVE (acceptance): (1) new exact-head push/PR Quality green with spans Node and browser regressions; (2) independent eligible PR #189 review and verified protections; (3) ordinary authorized PR merge and exact-main Quality green; (4) Pages publication verified at main SHA and hosted desktop/390px smoke; (5) synchronized browser truss JSON preview/import/export/solve UI with invalid-file and keyboard tests.
- 2026-11-20 — TRUSS-JSON-BOUNDS-356: Add immutable metre-based geometry bounds to non-solving truss JSON preview for future canvas framing; focused Node regression covers signed coordinates, Studio/legacy parity, unstable model, analytical bar and invalid JSON. Baseline dev 3580972af27166bebf21acb158c49efcdd068c68; main 70fc483cb1cec3d2372d37484e4a8ef7942343da. Prior exact-head PR Quality #44657806431 passed; new exact-head CI pending. PR #189 zero reviews; no merge or Pages verification. Frozen historical inventory 166 gaps / 95 partial unchanged. NEXT FIVE (acceptance): (1) exact-new-head push and PR Quality green including bounds Node and browser regressions; (2) eligible independent PR #189 review and verified protections; (3) ordinary authorized dev-to-main PR merge with exact-main Quality green; (4) Pages publication verified at main SHA and desktop/390px hosted smoke; (5) synchronized truss JSON preview/import/export/solve browser UI with invalid-file and keyboard tests.
- 2026-11-20 — TRUSS-JSON-FORCE-RANGE-355 (dev QA pending): Reject non-finite resultant force components from extreme but finite nodal loads; add signed/analytical/invalid Node regression. Baseline exact-head push #44650390185 and PR #44650398950 passed; new exact-head QA pending, PR #189 unreviewed, Pages unverified. Frozen 166 gaps/95 partial.
- 2026-11-20 — TRUSS-JSON-MOMENT-RANGE-354 (dev QA pending): Reject non-finite SI moment preview from finite extreme loads/coordinates; Node regression includes overflow, normal zero moment, malformed JSON and analytical bar. Prior Quality #44642722037 green; new exact-head CI pending, PR #189 unreviewed, Pages unverified; frozen 166 gaps/95 partial.
- 2026-11-20 (TRUSS-JSON-MOMENT-353; dev QA pending): Truss JSON preview reports signed global-origin applied moment in SI N·m without solving; regression covers Studio/legacy equivalence, translation, zero-load instability and invalid input. Release gated by exact-head CI and PR #189 review.
- 2026-11-20 — TRUSS-JSON-RESULTANT-352: Add immutable SI-newton applied-load resultant to validated truss JSON preview with Studio/legacy signed-load, unstable/zero-load, malformed-file and analytical Node regression. Prior Quality #44624231778 passed; new-head CI pending; PR #189 unreviewed; Pages unverified; frozen 166 gaps/95 partial.
- 2026-11-19 — TRUSS-JSON-PREVIEW-COUNTS-351: Add constrained-DOF and loaded-node counts to validated truss JSON preview, including legacy SI, unstable/unloaded and invalid-input regression. Previous exact-head PR Quality #44614114148 green; new-head CI pending; PR #189 unreviewed, Pages unverified; frozen 166 gaps / 95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-PREVIEW-CI-FIX-350 (dev; QA pending): Repair failing inspectJSON BOM regression fixture (actual U+FEFF rather than literal backslash-u) and explicitly assert escaped-prefix rejection; previous Quality #44604888254 failed at truss Node test, new exact-head full CI pending. No release; historical 166 gaps/95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-PREVIEW-349: Add validated non-solving truss JSON preview with unit metadata and counts, plus positive/negative Node regression; CI pending, PR #189 unreviewed, Pages unverified; historical 166 gaps/95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-SOLVE-ENTRY-348: Add standalone solveJSON(text) to validate and solve Studio/legacy truss JSON with SI results and unit metadata; analytical/negative Node regressions. Exact-head CI pending, PR #189 unreviewed, Pages unverified; frozen 166 gaps/95 partial.
- 2026-11-19 — TRUSS-JSON-SOLVE-DOCUMENT-347: Add unit-aware standalone truss JSON solveDocument API with immutable input-unit labels and SI results, plus analytical/invalid/legacy Node regressions. Baseline exact-head Quality green; new-head CI pending; PR #189 unreviewed; Pages unverified; frozen 166 gaps/95 partial.
- 2026-11-19 — TRUSS-JSON-UNIT-DESCRIPTOR-346 (dev; exact-head CI pending): Add validated immutable current/legacy public unit labels for future JSON browser workflows; Node regression covers both formats, invalid/mixed units and axial reference. Previous Quality #44560212231 green; new-head CI pending; PR #189 unreviewed; Pages unverified. Frozen 166 gaps/95 partial.\n- 2026-11-19 — TRUSS-JSON-SERIALIZE-ERROR-345 (dev; exact-head CI pending): Reject root toJSON returning undefined and cyclic JSON exports with stable domain errors rather than native TextEncoder/JSON exceptions. Add focused negative regressions and positive axial-bar round-trip/analytical reference. Baseline dev 6451e8faa086e95bad34a48ae0f1f1024bc6702d, main 70fc483cb1cec3d2372d37484e4a8ef7942343da; baseline PR Quality #44550353350 succeeded; PR #189 zero reviews. No local checkout/Node/Chromium execution; new-head CI and Pages pending. Frozen historical inventory 166 gaps / 95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-SERIALIZED-344: Validate actual serialized truss JSON after toJSON hooks, add negative and analytical Node regressions. Baseline exact-head Quality #44539689966 passed; new-head CI pending, PR #189 unreviewed, Pages unverified; frozen 166 gaps/95 partial.
- 2026-11-19 — TRUSS-JSON-EXPORT-LIMIT-343: Enforce 1 MiB UTF-8 export/import compatibility for standalone truss JSON with positive Unicode round-trip, analytical and oversized negative Node regressions; exact-head CI and PR release pending. Historical 166 gaps/95 partial frozen.
- 2026-11-19 — TRUSS-JSON-EXPORT-342: Add validated truss JSON export preserving modern/legacy units and focused round-trip/invalid-input Node regression; new-head CI and PR release pending.
- 2026-11-19 — TRUSS-JSON-BOM-341: Accept leading UTF-8 BOM in truss JSON imports, retaining byte limit and strict parse validation; add focused positive/negative Node regressions. Baseline push/PR Quality green; new-head CI pending; PR #189 unreviewed; no Pages release. Frozen 166 gaps/95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-UTF8-340: Enforce 1 MiB truss JSON import size in UTF-8 bytes, covering multibyte Unicode bypass with Node regressions. Prior exact-head PR Quality #44501337459 green; new-head CI pending, PR #189 unreviewed, no Pages release; frozen 166 gaps/95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-BOUND-339: Bound truss JSON imports to 1 MiB before parsing; add positive/negative Node regressions. Prior Quality #44492914124 green, new-head CI pending; PR #189 unreviewed, no Pages release. Frozen 166 gaps/95 partial unchanged.
- 2026-11-19 — TRUSS-JSON-IMPORT-338: Add validated, lossless truss JSON import API with current/legacy unit round-trip regression; new-head CI pending; no release. Frozen 166 gaps / 95 partial.\n- 2026-11-19 — CI-SMOKE-AUDIT-FIX-337: Repair exact-head push/PR Quality #44486379155/#44486386237 failures in newly added smoke-registration preflight. Root cause: unittest discovery invocation in Quality uses `-v`, while the new auditor initially recognized only the version without flags. Preserve unittest discovery and all 205 browser smoke files; accept standard `-v` or `--verbose` switches without weakening existence/duplicate/orphan checks. Update regression fixture to the exact Quality invocation, add positive controls for no flag and `--verbose`. Local `python -m unittest discover -s /mnt/data/promath_ci/tests -p test_quality_audit.py -v` passed 9 tests; Python compile check passed. Previous dev 32d7cb8fb5143b32b5b35bc82010fa9288c324a5, main 70fc483cb1cec3d2372d37484e4a8ef7942343da; new exact-head CI pending, PR #189 unreviewed; Pages unverified. Historical 166 gaps /95 partial unchanged.
- 2026-11-19 — CI-SMOKE-AUDIT-336: Audited Quality workflow after concern that outdated tests caused failures. Verified current exact dev 4d86afc41ab94082d86d6347462aaaa741d76ed9 and main 70fc483cb1cec3d2372d37484e4a8ef7942343da; exact-head PR Quality #44484188871 passed; push Quality #44484180412 was still in progress at initial inspection. Inspected 205 smoke_*.py files: all registered exactly once; no missing/duplicated registrations. 206 direct smoke/Node test commands; Python unittest discovery still covers test_*.py. Prior observed failures were mismatched fixtures/diagnostics subsequently repaired, not proof of obsolete tests. Kept all coverage. Added scripts/audit_quality_tests.py to detect deleted or renamed test files, unregistered new smoke files, duplicate direct test commands and missing unittest discovery, plus seven focused Python unit regressions and an early fail-fast Quality preflight. Local seven test cases passed; full exact-new-head Quality pending. PR #189 has no reviews; main/Pages unchanged/unverified. Historical 166 gaps/95 partial unchanged.
- 2026-11-19 — TRUSS-NUMERIC-TYPES-335: Reject bigint and symbol numeric values before coercion in current/legacy truss parsers; focused negative/positive Node regression. Prior exact-head push/PR Quality #44469474017/#44469481239 green at d3a4516ae1bb7283f4eb7cc8654b88ce80fbde23; new-head CI pending, PR #189 review and Pages unverified. Historical 166 gaps / 95 partial frozen.
- 2026-11-19 — TRUSS-IDENTIFIER-TYPES-334: Reject coerced non-string node/member IDs, preserve trimmed strings and analytical single-bar behavior; focused Node regression and living plan/ledger. Prior exact-head push/PR Quality #44455608715/#44455614729 green at 7fb5dfcc7da6e3595ddf6e5068a788c20ccd40e9; new-head CI pending, PR #189 review and Pages unverified. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-19 — TRUSS-ENDPOINT-TYPES-333: Reject non-string member endpoint IDs before lookup (including arrays coercing to valid IDs); preserve trimmed string endpoints and analytical bar physics. Focused Node regression, living plan and ledger. Previous exact-head Quality #44448599356 succeeded at 656fdd891480f13a7a66c7349a7f68970f21e770; new-head CI pending, PR #189 review and Pages unverified. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-19 — TRUSS-STIFFNESS-UNDERFLOW-332: Reject positive E/area combinations whose EA/L stiffness underflows to zero; provide actionable member-specific error and focused Node regression preserving analytical bar displacement. Previous exact-head PR Quality #44397046757 passed on rerun for 2016a8b663bc3ae59d73c77c91814fb2978dbd6f; new-head CI pending, PR #189 eligible review and Pages unverified. Historical 166 gaps / 95 partial frozen.
- 2026-11-18 — TRUSS-WHITESPACE-FIXTURE-331: Correct newly added whitespace regression to test actual tab and newline values, not literal backslash sequences; update plan/ledger. Previous source fix 4cf8f127bb921aa6a996de3cde38c08451c3d1f0, new-head Quality pending. PR #189 review/Pages unverified; frozen 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-WHITESPACE-NUMERIC-330: Reject whitespace-only numeric inputs in modern and legacy truss parsing rather than silently coercing to zero; preserve valid trimmed numeric strings. Focused positive/negative Node regression and updated living plan/ledger. Previous exact-head push/PR Quality #44375158127/#44375171973 passed at 5824a19c0beb4dbfd6e3e0783f44a529031544fd; new-head CI pending, PR #189 review and Pages unverified. Historical 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-SUPPORT-FLAGS-329: Reject ambiguous support fixX/fixY inputs rather than silently treating them as free; accept explicit booleans and lowercase string booleans, with omitted flags defaulting to false. Add positive/negative Node regression, plan and execution ledger. Prior exact-head Quality #44365528635 green at c1f2f3c2fd237f918e6161eb1c6143cb355f12fd; new-head CI and PR #189 eligible review pending. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-LEGACY-AREA-328: Reject overflow in legacy m²→mm² area conversion with finiteScaled, preserving valid analytical bar results; focused Node regression, plan and ledger update. Prior exact-head Quality #44331313464 passed; new CI and PR review pending. Historical 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-SI-OVERFLOW-327: Reject finite inputs that overflow kN→N and GPa→Pa conversion before FEM assembly; add positive/negative Node regression. Prior dev 0be7525f348136ac2e7bb28cbe57196536380c47 Quality #44318660075 success; new-head CI pending, PR #189 review and Pages pending. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-CI-326: Repair failing exact-head truss regression fixture (invalid Node 1 masked intended Node 2 assertion), retain indexed validation coverage; reject object/array coercion in numeric model fields and test positive/negative cases. Prior dev 30cca85763e593ddb897f47d179b26b1638745bb; push #44308706690 and PR #44308715188 failed at Node regression. New-head CI pending; PR #189 review and Pages pending; historical 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-MODEL-325: Reject null, array and primitive modern truss node/member entries with indexed validation errors rather than TypeError; add positive single-bar and negative row-type Node regressions. Prior dev 7aca18035c758a37b0a18d0909668dec7c626b6b; prior Quality #44290125690 passed. New exact-head Quality pending, PR #189 review/protections and Pages pending; frozen 166 gaps / 95 partial unchanged.
- 2026-11-18 — TRUSS-LEGACY-324: Harden legacy truss model conversion against malformed nodes, mixed SI/current member schemas and nonfinite legacy values. Add analytical single-bar and negative-input Node regressions. Prior dev 2a452444b44cbd9eabcedd6192f7363c29eeb28f; new-head CI and PR review pending; no release. Historical inventory unchanged (166 gaps / 95 partial).
- 2026-11-18 — TRUSS-STUDIO-323: Upgrade newly added basic 2D truss studio into a complete editable engineering UI with tabular joint/member inputs, direct stiffness FEM solver split into reusable pure JS, diagonal-scaled solution, residual and energy checks, tension/compression SVG deformation visualization, amplification, labels, two example models, model JSON import/export, results CSV/SVG, accessible responsive keyboard/mobile layout. Preserve legacy TrussStudio.solve(...) SI-unit API and legacy JSON (N, Pa, m²) imports while new form uses kN, GPa, mm². Source/data and regression tests updated atomically. Previous dev 047d18925452405792f219af2b0c26a8a29a5c3a, main 70fc483cb1cec3d2372d37484e4a8ef7942343da; local node --test tests/test_truss_fem.js (5 passed); CHROMIUM_PATH=/usr/bin/chromium python tests/smoke_truss_fem.py and tests/smoke_truss_studio.py (both passed). Exact-new-head CI, PR #189 approval/protection and Pages release pending. Root index.html and modular bundle unchanged. Historical 166 gaps/95 partials remain frozen.
- 2026-11-18 — TRUSS-STUDIO-322: Add offline structural 2D truss finite-element studio with JSON editor, validated solver, reaction/displacement/stress tables, deformation SVG, CSV export, mobile UI and CI browser regression. Pending exact-head CI and protected release; historical inventory unchanged.
- 2026-11-18 — AUDIT-SYMLINK-DIAGNOSTIC-321: Repair exact-head PR Quality #44226742388 failure (FIFO symlink expected `not a regular file`, O_NOFOLLOW raised ELOOP). Normalize ELOOP to the existing non-regular-file diagnostic without weakening O_NOFOLLOW or descriptor checks; strengthen symlink-to-regular-file regression to require the same diagnostic. Previous dev eb3deadf79f714a3a23a01fbd1df5a03bc457bb6, main 70fc483cb1cec3d2372d37484e4a8ef7942343da. Local isolated errno/symlink check only; exact-new-head Python/Chromium CI pending. PR #189 review/protections and Pages unverified. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-18 — AUDIT-SYMLINK-OPEN-320: Previous dev 8f6231ecef7afb5653d8238617e6c5e68e189683, main 70fc483cb1cec3d2372d37484e4a8ef7942343da; exact-head push/PR Quality #44220306832/#44220313073 successful. Harden historical ledger file opening with O_NOFOLLOW where available, rejecting symlinked exports at open time while preserving ordinary regular-file imports and size checks; add focused positive/negative symlink regression. Local Python/Chromium not run; new-head CI pending. PR #189 open with zero submitted reviews; Pages unverified; frozen 166 gaps / 95 partial unchanged.
- 2026-11-18 — AUDIT-GAP-SCOPE-SECTION-IDS-319: Verified dev 6fd96119704ec418604bf865b2feda01df448667, main 70fc483cb1cec3d2372d37484e4a8ef7942343da, push/PR Quality #44203585687/#44203592193 green; PR #189 has zero reviews. Add opt-in sorted historical gap IDs grouped by scope and section, with focused CLI regression for all 166 unique IDs, default compatibility, invalid flag and malformed input. Local Python/Chromium not run; new exact-head CI pending. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-18 — AUDIT-GAP-SECTION-IDS-318: Baseline dev cf7fdfcdcc5bf318a07759b96d3af5aa733398fc, main 70fc483cb1cec3d2372d37484e4a8ef7942343da; exact-head Quality #44131480700 green, PR #189 open without reviews. Add opt-in sorted historical gap IDs grouped by audit section and focused regression (166 unique IDs, compatibility, invalid flag, malformed JSON). Local Python/Chromium not run; new-head CI pending, no release/Pages claim. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-17 — AUDIT-GAP-SCOPE-IDS-317: Added opt-in sorted historical gap IDs by scope with CLI regression for 166 unique IDs, default compatibility, invalid flags and malformed exports. Prior exact-head Quality #44110137048 green; new-head CI pending. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-17 — AUDIT-GAP-IDS-316: Verified dev 81371cb2e4c693f46c5ae34a5acc517b4708705a, main 70fc483cb1cec3d2372d37484e4a8ef7942343da, exact-head Quality #44069735130 green, PR #189 open without reviews. Added opt-in sorted historical gap IDs by priority with regression for 22/64/53/27, uniqueness, coverage, compatibility and error handling. New-head CI pending; no release. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-17 — AUDIT-PROVENANCE-315: Verified dev f2e088484ce732fe1f686b07061725ff107f84f5, main 70fc483cb1cec3d2372d37484e4a8ef7942343da, exact-head Quality #44050992618 green, PR #189 open with zero submitted reviews. Add opt-in validated audit provenance JSON metadata (schema version/source date) and regression for default compatibility, required flag and invalid schema. New-head CI pending; no release. Historical 166 gaps / 95 partial unchanged.
- 2026-11-17 (dev, new-head CI pending): Add opt-in validated gap priority-by-scope-and-section JSON report with deterministic P0–P3 zero cells, focused CLI regression for 22/64/53/27 totals, default compatibility and invalid/malformed input guards. Prior exact-head PR Quality #44028359618 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-17 (dev, new-head CI pending): Add optional validated existing/gap kind-by-scope-and-section JSON report with deterministic zero-count cells, focused CLI regression for 158/166 totals, default compatibility, invalid flag and malformed export. Previous exact-head PR Quality #44020817654 passed; frozen 166 gaps / 95 partial unchanged. No release.
- 2026-11-17 (dev, new-head CI pending): Add opt-in validated existing-feature status-by-scope-and-section JSON report with zero-count cells, focused CLI regression for 63/95 totals, default compatibility, flag guard and malformed export. Prior exact-head Quality #44014588989 green. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-17 (dev, exact-new-head CI pending): Add optional `--json-summary --include-scope-sections` validated frozen gap cross-tab with deterministic ordering, focused CLI regression, backward-compatible default, invalid-flag and malformed-export coverage. Prior head Quality #44007157110 green; frozen 166 gaps / 95 partial unchanged. No Pages release claimed.
- 2026-11-17 (dev, exact-head CI pending): Repair the legacy quiet CLI regression after failed Quality #43992701386: assert quiet-only silence and JSON-only output separately, retaining the explicit conflict rejection regression. No validator logic or frozen 166-gap/95-partial audit changes; PR #189 still awaits approval and no Pages release is claimed.
- 2026-11-17 (dev, new-head CI pending): Reject conflicting --quiet and --json-summary audit CLI flags to prevent silently empty machine-readable reports; focused regression covers error and independent valid modes. Previous exact-head Quality #43984767253 passed; PR #189 lacks review. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-17 (dev, exact-head CI pending): Add opt-in historical existing/gap counts by scope with explicit zero cells and CLI regression for 158/166 totals, combined output, default compatibility, invalid flag and malformed exports. Previous exact-head PR Quality #43933888057 passed; PR #189 still lacks review. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in historical existing/gap counts by audit section with zero cells and focused CLI regression; previous exact-head PR Quality #43924868849 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in existing-feature status-by-audit-section JSON summary, regression for 63 bounded-complete / 95 partial, default compatibility, invalid flag and malformed exports. Previous exact-head PR Quality #43912773386 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in validated existing-feature status-by-scope JSON summary (63 bounded-complete / 95 partial), with CLI regressions for totals, default compatibility, invalid flags and malformed exports. Previous exact-head PR Quality #43905802802 passed. Historical 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in validated gap priority-by-scope cross-tab with zero cells, 166 total, default compatibility, invalid-flag and malformed export regression. Previous exact-head PR Quality #43892649430 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in validated gap priority-by-section cross-tab JSON summary with explicit zero cells, 166 total, default compatibility, invalid flag and malformed export regression. Previous exact-head PR Quality #43884954650 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in validated historical gap counts by audit section to JSON summary; regress computed totals, default/combined output, invalid flag and malformed export. Previous exact-head PR Quality #43872799526 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, new-head CI pending): Add opt-in validated gap counts by scope to JSON summary, with computed-count, default/combined output, invalid flag and malformed export CLI regression. Previous exact-head PR Quality #43864383935 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Add opt-in validated historical gap-priority JSON summary (P0 22 / P1 64 / P2 53 / P3 27) with default/combined output, flag misuse and malformed export regressions. Previous exact-head push/PR Quality #43856296755/#43856305567 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Add opt-in validated status counts (63 bounded-complete / 95 partial) to feature-ledger JSON summary without breaking the default two-key contract; test counts, flag misuse and malformed input. Previous exact-head push/PR Quality #43846518103/#43846529171 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Centralize historical feature-ledger 8 MiB input bound across descriptor preflight and bounded read; test inclusive exact-limit JSON acceptance and one-byte-over rejection. Prior exact-head push/PR Quality #43837245478/#43837254391 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Close raw audit descriptor if os.fdopen stream wrapping fails; add mocked failure/closure regression and valid JSON control. Prior exact-head push/PR Quality #43829231889/#43829238011 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Preflight oversized/sparse feature-ledger JSON exports with opened-descriptor fstat before bounded read, preserving growth-race protection; add sparse 8 MiB+1 regression and valid control. Previous exact-head push/PR Quality #43821384375/#43821390905 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Close audit import stat/open FIFO replacement race using nonblocking descriptor open and fstat, with FIFO symlink timeout regression and valid JSON control. Previous exact-head push/PR Quality #43814324785/#43814330146 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Reject non-regular audit JSON input paths before opening to avoid blocking on FIFOs or reading devices; add bounded subprocess FIFO regression and regular-file control. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-16 (dev, exact-head CI pending): Correct audit diagnostic regression to assert raw-control absence and escaped key representation for all key classes.
- 2026-11-16 (dev, exact-head CI pending): Escape duplicate/non-NFC audit JSON keys in parser diagnostics to prevent terminal-control and newline log injection; add focused negative and valid-key regression. Historical 166 gaps / 95 partial unchanged; no release.
- 2026-11-15 (dev, exact-head CI pending): Correct invalid UTF-8 raw byte offsets when a leading BOM is stripped by utf-8-sig; add BOM/non-BOM CRLF and multibyte regression with valid control. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-15 (dev, exact-head CI pending): Add physical-line coordinates to malformed JSON diagnostics for CR, CRLF and LF, preserving Python character-line coordinates; add negative and valid regression. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-15 (dev, exact-head CI pending): Align malformed UTF-8 audit diagnostics with CR, CRLF and LF physical byte lines/columns; add focused regression and valid control. Previous exact-head Quality #43727773583 passed. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-15 (dev, exact-head CI pending): Repair malformed JSON CR/LF byte-column validator's accidentally escaped comment that hid byte_column assignment; add CR/CRLF/LF error and line-number regression assertions; update living execution ledger and next five. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-15 (dev, CI pending): Clarify bare-CR byte-column semantics versus Python JSONDecodeError character-line numbering; isolated three-case Python check passed.\n- 2026-11-15 (dev, CI pending): Correct CR/LF regression fixture to use real line-ending bytes, not backslash text.
- 2026-11-15 (dev, CI pending): Align malformed JSON byte-column diagnostics with CR, CRLF and LF line endings; add focused negative cases and valid control. Frozen 166 gaps / 95 partial unchanged; no main/Pages release.\n- 2026-11-15 (dev, CI pending): Correct malformed JSON coordinate regression fixture to use real UTF-8 BOM and newline bytes; retain positive Unicode control.
- 2026-11-15 (dev, CI pending): Report UTF-8 byte offset/column for malformed JSON syntax, including multibyte text and initial BOM; preserve character coordinates, add negative and positive regressions. Frozen 166 gaps / 95 partial unchanged; no main/Pages release.
- 2026-11-15 (dev, CI pending): Correct byte-coordinate regression fixture to write an actual newline and invalid 0xFF byte, preserving line-2/byte-column-14 assertions; no release.
- 2026-11-15 (dev, CI pending): Add byte-based line and column diagnostics for malformed UTF-8 historical JSON imports; regression covers multibyte UTF-8 before a later-line invalid byte and a valid control. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-14 (dev, CI pending): Repair UTF-8 positive Unicode assertion from failed Quality #43640573911; include offending raw bytes in invalid UTF-8 diagnostics with leading/truncated regressions. Frozen 166 gaps / 95 partial unchanged; no release.
- 2026-11-14 (dev, CI pending): Correct malformed UTF-8 regression fixtures to use raw invalid bytes, retaining decoder-reason and offset assertions. No release.
- 2026-11-14 (dev, CI pending): Include the UTF-8 decoder reason alongside exact malformed byte offsets in historical audit imports; test invalid leading bytes, truncated multibyte sequences and valid Unicode. Frozen 166 gaps / 95 partial unchanged; no main/Pages release.
- 2026-11-14 (dev, CI pending): Report first invalid UTF-8 byte offset in historical JSON imports; add two malformed raw-byte regressions and a valid initial BOM control. Frozen 166 gaps / 95 partial unchanged; no main/Pages release.
- 2026-11-14 (dev, CI pending): Reject Unicode combining grapheme joiner and variation selectors in nested historical JSON keys/values, with 12 escaped/literal negative cases and canonical positive control; frozen 166 gaps / 95 partial unchanged. No main/Pages release.
- 2026-11-14 (dev, CI pending): Reject private-use Unicode U+E000 and U+F0000 in nested historical audit JSON keys/values (literal/escaped), with assigned NFC Unicode acceptance; frozen 166 gaps / 95 partial unchanged. Exact-head Quality pending; no main/Pages release.
- 2026-11-14 (dev, CI pending): Reject unassigned Unicode U+0378 in nested audit JSON keys/values, escaped and literal; preserve canonical positive control, noncharacter diagnostics and frozen 166 gaps / 95 partial. Previous exact-head Quality #43592939434 passed; no main/Pages release claimed.
- 2026-11-14 (dev, CI pending): Correct surrogate-pair positive test expectation to decoded U+1F600 scalar after exact-head Quality #43582928342 failed one of 545 structural tests; retain four negative lone-surrogate checks. Frozen 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Repair failed surrogate-pair positive fixture by serializing the actual U+1F600 scalar to JSON; preserve four lone-surrogate negative cases. Exact-head PR Quality #43578315570 failed 545 structural tests (one failure). Frozen 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Report exact U+XXXX for lone UTF-16 surrogate values/keys in audit JSON; four negative regression cases and valid escaped surrogate-pair positive control. Frozen 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Include exact U+2028/U+2029 in nested audit JSON line-separator errors; strengthen eight escaped/literal key/value regression cases. Frozen 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Identify exact U+XXXX code point in nested audit JSON Unicode noncharacter diagnostics; six escaped/literal negative regressions and printable positive control. Frozen 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Fix format-control regression diagnostic regex to match literal U+XXXX code points; preserve negative and positive assertions. No release claimed.
- 2026-11-14 (dev, CI pending): Include U+XXXX in nested audit JSON Unicode format-control diagnostics; add six escaped/literal regression cases and safe positive control. Frozen 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Repair NFC CI regression: distinguish nested key/value errors, reject formerly accepted decomposed nested value, retain canonical positive control; value diagnostic now explicitly identifies string value. Quality #43530946098 failed 542 structural tests (2 failures, 1 error). Historical 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-14 (dev, CI pending): Reject non-NFC Unicode in nested feature-ledger JSON values as well as keys, including escaped/literal JSON regression and canonical positive control; historical 166 gaps / 95 partial unchanged, no release claimed.
- 2026-11-13 (dev, CI pending): Repair failing Unicode-space JSON fixtures using actual characters with escaped/literal nested key/value cases; report U+XXXX in validator errors. Isolated 12-case JSON check passed; full CI pending. Historical 166 gaps / 95 partial unchanged; no release claimed.
- 2026-11-13 (dev, CI pending): Reject visually ambiguous non-ASCII Unicode spaces in nested audit JSON keys/values, preserving ordinary spaces; add focused positive/negative regression. Historical 166 gaps / 95 partial unchanged; no main/Pages release claimed.
- 2026-11-13 (dev, CI pending): Audit JSON float parsing now reports stable validation errors for decimal exponents beyond the Decimal decoder limit, with negative/positive regression; frozen 166 gaps / 95 partial unchanged, release not claimed.
- 2026-11-13 (dev, CI pending): Audit JSON import rejects U+2028/U+2029 in nested keys/values (escaped or literal), with focused negative and positive regression. Frozen 166 gaps / 95 partial remain historical; release not claimed.
- 2026-11-13: Reject Unicode format controls in nested audit JSON metadata keys and values; add positive/negative regression; frozen 166 gaps / 95 partial unchanged; new exact-head CI pending.
- 2026-11-13: Repair three failing Unicode noncharacter regression fixtures (U+FDD0, U+FFFE, U+10FFFF) without weakening validator assertions; exact-head CI pending; frozen 166 gaps / 95 partial unchanged.
- 2026-11-13: Correct Unicode noncharacter JSON regression fixtures to decode real noncharacters rather than literal escape strings; exact-head CI pending.
- 2026-11-13: Reject Unicode noncharacters in nested historical audit JSON strings and keys, with focused negative and canonical positive regression; frozen 166 gaps / 95 partial unchanged; exact-head CI pending.
- 2026-11-13: Preserve historical JSON-control diagnostic prefix while adding literal U+XXXX code points; fix escaped-regex assertions for exact-head structural CI. Frozen 166 gaps / 95 partial unchanged; new CI pending.
- 2026-11-12: Repair exact-head CI failure caused by stale escaped-control positive fixture; assert C0/C1 rejection in nested keys/values with explicit U+XXXX diagnostics and preserve printable-string acceptance. Frozen 166 gaps / 95 partial unchanged; new exact-head CI pending.
- 2026-11-12: Reject decoded C0/C1 control characters in historical audit JSON strings, including nested keys and values; add focused regression while preserving NUL/BOM diagnostics. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending.
- 2026-11-12: Reject invisible embedded U+FEFF BOM characters in historical audit JSON strings (including nested keys/values), preserving leading UTF-8 BOM compatibility; add positive/negative regression. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending.
- 2026-11-12: Repair audit-label NFC regression fixture escaping so the negative test uses an actual decomposed Unicode accent and correctly matches literal diagnostic parentheses; validator unchanged, exact-head CI pending.
- 2026-11-12 — AUDIT-LABEL-NFC-254: Require NFC Unicode normalization for historical audit title/scope/section export labels, preserving printable/trimmed checks; add decomposed-label negative and frozen canonical positive regressions. Historical 166 gaps / 95 partial unchanged; new exact-head CI pending; no main or Pages release.
- 2026-11-12: Reject non-NFC Unicode object keys in imported historical feature-ledger JSON, including nested keys, before duplicate checks; test decomposed/aliased keys, canonical Unicode and frozen audit acceptance. Historical 166 gaps / 95 partial unchanged; exact-head CI pending.
- 2026-11-12: Reject non-NFC feature IDs in historical audit exports to prevent canonically equivalent identifiers bypassing duplicate checks; focused negative and canonical-positive regression. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending.
- 2026-11-12: Corrected historical-ledger edge-label test expectations for the established plural `Feature titles` invisible-character diagnostic (tab/newline), preserving validator protections; exact-head structural/Chromium CI pending. Frozen inventory remains 166 gaps / 95 partial.
- 2026-11-12 — AUDIT-EXPORT-DIAGNOSTIC-CI-249: Repair six edge-label regression diagnostic expectations for tabs/LF versus ordinary spaces; preserve invisible-control and surrounding-whitespace rejection, canonical inventory and frozen 166 gaps / 95 partial. Exact-head CI pending; no release claimed.
- 2026-11-12 — AUDIT-EXPORT-EDGE-LABELS-248: Reject surrounding whitespace on exported title/scope/section labels while preserving interior spaces and the canonical historical ledger. Add negative leading/trailing space, tab and newline regression fixtures. Frozen inventory remains 166 gaps / 95 partial. Local checkout unavailable (github.com DNS); exact-head CI pending; no release claimed.
- 2026-11-11: Correct the newline test fixture to a valid escaped Python string before exact-head CI; no production change.
- 2026-11-11: Repair literal backslash-n source corruption in audit validator and scope/section regression; restore executable IDs assignment and real Unicode negative fixtures. Frozen 166 gaps / 95 partial unchanged; exact-head Quality pending, no release claim.
- 2026-11-11: Reject invisible/control characters in historical audit scope and section labels; add 10 negative cases and canonical positive control. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending, no release claim.\n- 2026-11-11: Correct test fixture escape syntax before exact-head CI; exercise actual invisible characters and match diagnostic parentheses literally.
- 2026-11-11: Reject invisible/control characters in historical audit feature titles, with direct regression and canonical acceptance. Frozen 166 gaps / 95 partial unchanged; exact-head Quality pending, no release claim.
- 2026-11-11: Reject negative-zero floating JSON tokens in frozen ledger exports (including exponent notation), with nested negative cases and positive-zero controls; maintain 166 gaps / 95 partial. Exact-head QA pending; no release claim.
- 2026-11-11: Restore readable validator comments and extend invisible-ID regressions to DEL U+007F and zero-width joiner U+200D. Frozen 166 gaps / 95 partial unchanged; exact-head QA pending, no release claim.
- 2026-11-11: Repair feature-ledger CI classification for ASCII information separators U+001C–U+001F; preserve invisible-control rejection and add regression coverage. Exact-head QA pending.
## 2026-11-11 — Repair interior-whitespace regression fixtures and diagnostics
- Use real tab/LF/CR/NBSP fixture characters and correctly escaped regex; validate whitespace before other invisible characters to preserve a stable diagnostic. Keep canonical acceptance and non-whitespace invisible rejection. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending, no Pages release.

## 2026-11-11 — Reject interior whitespace in historical audit feature IDs
- Reject embedded whitespace that can make external feature-ID references ambiguous, with space/tab/newline/CR/NBSP regressions and frozen ledger acceptance. No app bundle changes; 166 gaps / 95 partial unchanged. Exact-head Quality pending; no release or Pages claim.

## 2026-11-11 — Reject invisible interior feature-ID characters
- Reject zero-width, bidirectional format, control and word-joiner characters in historical audit IDs; focused regression plus valid canonical control. Frozen 166 gaps / 95 partial unchanged; no application bundle change. Exact-head Quality pending; no merge or Pages claim.

## 2026-11-10 — Repair whitespace-ID CI fixture and improve diagnostics
- Replace literal backslash-t fixture with real tab, add trailing tab/newline negative cases, and include offending item index in validator error. Frozen 166 gaps / 95 partial unchanged. Exact-head CI pending; no app bundle, main release or Pages claim.

## 2026-11-10 — Reject whitespace-ambiguous historical feature IDs
- Require canonical feature IDs without surrounding whitespace; add positive and negative regression cases. Historical 166 gaps / 95 partial unchanged; no application bundle changes. Exact-head QA pending; no merge or Pages deployment.

## 2026-11-10 — Quiet historical audit validation for CI
- Add opt-in `--quiet` to suppress successful validator output without hiding invalid-input diagnostics. Add subprocess regression for quiet default/JSON-summary success and malformed failure. Frozen 166 gaps / 95 partial unchanged; no app bundle or Pages release. Exact-head QA pending.

## 2026-11-10 — Machine-readable validated historical ledger summary
- Add opt-in `--json-summary` CLI output for automation consumers, retaining existing default text output and failing closed for malformed exports. Add subprocess success/error regression. Frozen 166 gaps / 95 partial unchanged; no application bundle or Pages release. Exact-head CI pending.

## 2026-11-10 — Validate external historical audit exports from CLI
- Accept optional ledger JSON path while retaining canonical default; report malformed exports without tracebacks. Add subprocess acceptance/rejection regression. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending. No application bundle or Pages release.

## 2026-11-10 — Reject ambiguous negative-zero JSON integers in frozen audit
- Reject JSON integer -0 before Python silently converts it to zero; add nested negative cases and valid zero/negative-one/negative-zero-float controls. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending. No runtime bundle or Pages deployment.

## 2026-11-10 — Normalize excessive JSON integer digit errors
- Convert Python 3.11+ integer digit-limit failures to a stable audit ValueError; test 5,000-digit rejection and safe integer acceptance. No application bundle change. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending.

## 2026-11-10 — Restore decoded NUL detection and deep Unicode CI regressions
- Fix iterative historical JSON Unicode validation to inspect actual U+0000 rather than literal backslash-x-zero; repair deep JSON escape fixtures and test nested NUL keys. Exact-head Quality pending; frozen 166 gaps / 95 partial unchanged. No application bundle or Pages deployment.

## 2026-11-10 — Iterative Unicode validation for nested historical JSON
- Replace recursive NUL and surrogate walks with one iterative post-decode traversal; test 400-deep valid and invalid Unicode inputs. No app bundle change. Frozen 166 gaps / 95 partial unchanged; new exact-head CI pending.

## 2026-11-10 — Correct malformed JSON regression regex
- Fix line/column regex escaping in the newly added regression; no validator behavior or application bundle change. Exact-head CI pending.

## 2026-11-10 — Actionable malformed historical JSON diagnostics
- Report malformed JSON as ValueError with line/column context; add malformed fixture regressions and preserve BOM handling. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending. No application bundle or Pages change.

## 2026-11-10 — Bound historical audit JSON input size
- Limit untrusted ledger JSON input to 8 MiB before UTF-8 decoding, with oversized-file rejection and valid-small regression. Frozen 166 gaps / 95 partial unchanged; new exact-head CI pending. No application bundle or Pages release.

## 2026-11-09 — Normalize missing historical ledger read errors
- Convert missing/unreadable JSON audit path errors to actionable ValueError, with missing-path and directory regressions. New exact-head CI pending; no runtime bundle, release or Pages change. Historical 166 gaps / 95 partial unchanged.

## 2026-11-09 — Restore BOM validator syntax and reject misplaced BOMs
- Correct invalid Python assignment introduced by UTF-8 BOM support; preserve one JSON parse call. Add double-BOM and whitespace-before-BOM negative regressions. Exact-head CI pending; no application bundle change, main merge or Pages deployment. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-09 — Correct BOM regression malformed-byte fixture
- Ensure the negative UTF-8 regression appends a real FF byte after BOM; preserve strict error assertion. New exact-head CI pending; frozen audit unchanged.

## 2026-11-09 — Accept optional UTF-8 BOM in historical JSON exports
- Historical feature-ledger loader accepts UTF-8 BOM at the start of JSON exports while retaining strict malformed UTF-8 rejection; added plain/BOM Unicode and invalid post-BOM regression cases. No runtime JS/index.html changes. Frozen 166 gaps / 95 partial unchanged; exact-head QA pending.

## 2026-11-09 — Report malformed UTF-8 in historical audit input
- Convert invalid UTF-8 ledger input to actionable ValueError; two malformed-byte regression cases and valid UTF-8 acceptance. Frozen 166 gaps / 95 partial unchanged; exact-head QA pending. No app JS/index.html changes.

## 2026-11-09 — Report deeply nested historical JSON as invalid audit input
- Converted JSON decoder recursion failures into explicit ValueError and added a 12,000-level nesting regression; no app JavaScript or standalone HTML changed. Exact-head CI and Pages pending; frozen 166 gaps / 95 partial unchanged.

## 2026-11-09 — Repair valid-control JSON regression fixture
- Corrected the escaped newline/tab fixture so the parser receives JSON control escapes rather than double-escaped literal backslashes. Preserved the positive assertions and existing NUL rejection. Exact-head CI pending; no application JS/index.html or Pages change. Historical 166 gaps / 95 partial unchanged.

## 2026-11-09 — Reject NUL escapes in historical JSON audit data
- Feature-ledger JSON loader rejects U+0000 in nested values or object keys to prevent truncated audit exports. Added negative and valid-control regression cases; historical 166 gaps / 95 partial unchanged. New exact-head QA pending; no application bundle or Pages change.

## 2026-11-09 — Reject silently rounded fractional JSON audit numbers
- Historical feature-ledger loader now rejects decimal fractional tokens with discarded significant digits (such as 0.10000000000000001) while accepting equivalent exponent notation, exact-decimal zero and subnormal boundary literals. Added focused positive/negative regressions; frozen 166 gaps / 95 partial unchanged. New exact-head CI pending; no runtime JS/HTML or Pages change.

## 2026-11-09 — Correct zero-mantissa regression fixture selection
- Included extended zero-mantissa literal in the valid-zero test branch, before CI completion. No validator algorithm or application bundle change; new exact-head QA pending. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-09 — Repair zero-literal CI fixture and exact decimal underflow check
- Fixed exact-head CI KeyError in valid-zero JSON test by reading the field actually present in each fixture; added signed-zero and extended zero-mantissa regression cases. The validator now distinguishes exact decimal zero using Decimal rather than a digit heuristic. Historical 166 gaps / 95 partial unchanged; new exact-head CI pending. No application JS/index.html or Pages changes.

## 2026-11-09 — Restore underflow-specific audit validation after CI failure
- Fixed exact-head Quality regression in the historical JSON loader: check nonzero-to-zero underflow before the rounded-to-integer guard, retaining both validations. Added subnormal underflow and valid zero-exponent regression cases. Historical 166 gaps / 95 partial unchanged; new CI pending. No application JS/HTML or Pages changes.

## 2026-11-09 — Correct audit fraction-check Python source formatting
- Replaced accidental literal newline escapes in the newly added validator guard with actual Python newlines; behavior and regression intent unchanged. Full exact-head QA pending.

## 2026-11-09 — Reject JSON decimal fractions silently rounded to integers
- Historical audit loader now compares integer-valued binary64 floats with the original decimal token to reject fractional inputs rounded into integers. Added three nested/boundary regressions; frozen 166 gaps / 95 partial unchanged. Exact-head CI pending; no application JS/HTML or Pages changes.

## 2026-11-09 — Reject precision-losing integer-valued JSON floats in frozen audit
- JSON decimal/exponent forms above the JavaScript safe integer boundary now fail strict feature-ledger loading instead of bypassing parse_int. Added nested negative cases and safe boundary/fractional positive regression. Historical 166 gaps / 95 partial unchanged; new exact-head CI pending. No runtime JS/HTML or Pages change.

## 2026-11-09 — Require integer types for frozen historical counts
- Historical feature-ledger validation now rejects float or boolean count fields even when Python equality would accept the numeric value. Added four direct regression cases. Frozen 166 gaps / 95 partial unchanged. New exact-head CI pending; no runtime bundle or Pages change.

## 2026-11-09 — Reject precision-losing JSON integers in frozen feature audit
- Reject integer literals outside JavaScript's safe integer range (including nested values) to preserve audit fidelity in browser/spreadsheet consumers. Added negative and boundary-positive regressions. Frozen 166 gaps / 95 partial unchanged; exact-head CI pending. No runtime bundle or Pages change.

## 2026-11-09 — Correct Unicode regression fixture escaping
- Ensure JSON test fixtures decode surrogate escapes instead of escaping the backslash itself; validator behavior unchanged. Exact-head CI pending.

## 2026-11-09 — Reject unpaired Unicode surrogate escapes in frozen feature audit
- Strict historical JSON decoding now rejects lone UTF-16 surrogate escapes in nested keys and values while accepting valid surrogate pairs. Added four focused cases. Frozen 166 gaps / 95 partial unchanged. New exact-head CI pending; no JS/HTML or Pages changes.

## 2026-11-09 — Reject underflowed nonzero JSON floats in historical audit
- Strict feature-ledger JSON loading rejects nonzero float literals silently rounded to zero (including nested fields), while accepting genuine zero. Added focused regression cases. Frozen 166 gaps/95 partial unchanged; exact-head CI pending. No runtime bundle, merge or Pages change.

## 2026-11-09 — Reject overflowed non-finite JSON floats in historical audit
- Strict JSON loading now rejects float literals such as 1e999 and -1e999 that decode to infinity, even in nested unused fields. Added three negative regressions. Frozen 166 gaps/95 partial unchanged; new exact-head QA pending, no JS/HTML, merge or Pages deployment.

## 2026-11-09 — Reject nonstandard non-finite JSON constants in historical feature ledger
- The audit loader now rejects NaN, Infinity and -Infinity (including nested JSON), with three negative temporary-file regressions. Historical 166 gaps/95 partial preserved. New exact-head CI pending; no application JS/HTML, release or Pages change.

## 2026-11-09 — Reject ambiguous duplicate JSON keys in frozen feature ledger
- Added a duplicate-key-safe JSON loader for the historical inventory, including nested objects, and focused regression coverage. The original audit remains 166 gaps / 95 partial; new exact-head CI pending. No application bundle, release or Pages change.

## 2026-11-08 — Reject malformed historical audit field types
- Hardened `scripts/validate_feature_ledger.py` to reject non-string ID/kind/status/priority before set/Counter processing and to reject boolean `schemaVersion` values, with descriptive `ValueError` instead of incidental `TypeError`. Added five negative regressions in `tests/test_feature_ledger_validation.py`. Historical inventory remains unchanged (166 gaps / 95 partial). Exact-commit CI pending; no application bundle changes, release or deployment.

## 2026-11-08 — Enforce frozen audit validation even with optimized Python
- Replaced optimization-removable `assert` checks in the historical feature-ledger validator with explicit, diagnostic validation failures. Added regression coverage for malformed audit records and a `python -O` subprocess to prove that the frozen inventory cannot silently pass when assertions are disabled. Historical 166 gaps / 95 partial unchanged. Exact-head CI pending; no application bundle, release or Pages change.

## 2026-11-08 — Recover cleanly from module removal during standalone verification
- Standalone build snapshot verification now reports a consistent actionable concurrent-source error when a module is deleted or becomes undecodable between assembly and final check. Added a subprocess regression for deleted module in read-only check mode with unchanged HTML and no temporary files. Previous exact-head push/PR Quality passed; new exact-head full QA pending. No application JavaScript or bundled HTML changes, release or Pages deployment. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-08 — Correct injected builder fixture indentation
- Corrected the concurrent-index test's guard targeting to preserve Python indentation while selecting the first of two matching destination reads. This preflight follow-up preserves the regression's failure and cleanup checks; no application code changed. Exact-head CI pending.

## 2026-11-08 — Repair concurrent-index regression fixtures
- Fixed two structural test-only failures reported by exact-head push/PR Quality #42517673686/#42517679751. The publish-path injection now targets its uniquely indented guard rather than also matching the no-op path, and the no-op fixture expects a real newline written by the injected editor. Rollback and temporary cleanup assertions remain strict. No production source or bundle change; new exact-head CI pending.

## 2026-11-08 — Reject stale destination on no-op standalone rebuild
- The normal no-op builder now checks that `index.html` is still a regular unchanged file after assembling and verifying module snapshots. This prevents false "already up to date" reports when an external editor changes the destination. Added a subprocess regression for an injected concurrent index edit. Existing `--check` snapshot behavior is preserved. Exact-head CI pending; no application runtime changes or production release.

## 2026-11-08 — Preserve externally introduced index symlinks during rebuild
- The standalone builder now checks for a destination symlink immediately before publishing, preserving an independently replaced path instead of overwriting it. Added a subprocess regression simulating the symlink swap, verifying failure, external-target preservation and temporary-file cleanup. Best-effort guard, not a full interprocess lock. Exact-head CI pending; no application JS or Pages release.

## 2026-11-08 — Verify source snapshots on no-op standalone builds
- Fixed a normal-build race where an initially unchanged `index.html` skipped module freshness verification and could report success despite a concurrent source edit. Added an injected no-op regression covering failure, preservation of the existing bundle and no staging artifacts. Exact-head CI pending; no runtime JS or Pages release.

## 2026-11-08 — Complete concurrent-module fixture newline repair
- Corrected the injected literal-newline conversion to use the actual four-space function indentation. This supplements the earlier test-only syntax fix; exact-head CI pending, no production changes or release.

## 2026-11-08 — Repair concurrent-module-edit regression fixture
- Exact-head CI exposed an indentation error in the subprocess-instrumented test builder, not in production `scripts/build.py`. Corrected the injected loop indentation and added explicit Python compilation of the fixture. Retained the original strict stale-module, index-preservation and cleanup assertions. New exact-head CI pending; no release.

## 2026-11-08 — Detect concurrent source changes in read-only bundle check
- Reused the standalone builder's source-snapshot verification in `--check`, preventing a false consistency success when a modular source changes during the check. Added an injected concurrent-edit subprocess regression that verifies failure and unchanged `index.html`. Previous exact-head push/PR Quality #42492393106/#42492396772 passed; new commit CI pending. No runtime bundle change or Pages release.

## 2026-11-08 — Detect concurrent module edits before publishing standalone HTML
- The standalone builder now snapshots modular source files and checks they have not changed before replacing `index.html`. If a source file is edited or replaced by a symlink during assembly, rebuilding aborts without publishing stale JavaScript. Added subprocess rollback/cleanup regression for an intervening source edit. This is a best-effort race guard, not a cross-process lock. Prior exact-head push/PR Quality #42487293944/#42487298107 succeeded; new commit QA pending. No runtime module change, merge or Pages release.

## 2026-11-08 — Preserve concurrent standalone HTML edits during rebuild
- The atomic standalone builder now checks that `index.html` still matches the snapshot read before module assembly; on an intervening external edit, it aborts and cleans the staged file rather than overwriting newer changes. Added a focused concurrent-edit subprocess regression. This detects ordinary lost-update races but does not implement an interprocess lock. Prior exact-head push/PR Quality #42485007089/#42485010736 passed; new commit CI pending. No runtime module change or production release.

## 2026-11-08 — Atomic standalone HTML rebuild and failure rollback
- `scripts/build.py` now writes the complete LF-normalized bundle to a same-directory temporary file and atomically replaces `index.html` only after a successful write, preserving original file mode and cleaning abandoned temporary files on failures. Previously it could truncate `index.html` if writing failed. Added focused `tests/test_build_atomic_write.py` for failed replacement rollback and successful rebuild. Isolated prototype passed locally; exact-commit full CI pending. No application runtime change, main promotion or Pages release.

## 2026-11-06 — Project import polling and explicit future-schema reset API
- Fixed Chromium project migration regression's unsafe wait predicate when graph.dataset is temporarily null; preserved two-row success and added imported-header verification.
- Added opt-in `MathStudio.toolPrefs.resetUnsupported(true)` API. Unsupported newer schema stays intact on ordinary operations and on failed reset writes; explicit successful reset stores v1. Focused Node regression exercises all transitions; standalone bundle synchronized. Reset UI is not yet implemented.
- Prior exact-head push Quality #42159635636 failed in project schema browser smoke; PR Quality #42159640300 was cancelled. New exact-head CI pending, no local Chromium execution, PR #189 remains review-gated; no main/Pages deployment. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-06 — Repair incomplete v1 tool preferences and unblock structural Quality
- Corrected a stale structural assertion for the now-extended preference state declaration; the assertion still requires persistence initialization before storage reads. Saved v1 preferences missing recents or pins are marked as needing repair, preserving valid sibling entries until a successful write. Added focused executable Node repair/recovery assertions and synchronized standalone HTML. Exact-head CI pending after previous push #42154342867 and PR #42154352048 failed at this structural assertion. No release; frozen 166 gaps / 95 partial unchanged.

## 2026-11-06 — Preserve unknown preference schemas and migrate legacy data
- Saved tool preferences with an unsupported schema version no longer risk silent overwrite by an older client. Session-only recents and pins continue working; unversioned legacy data is readable and migrates to v1 after a successful save. Node and Chromium regressions cover both behaviors; offline standalone module synchronized. Prior dev exact-head push/PR Quality passed (#42147267403/#42147271856), new commit's QA pending. PR #189 still lacks reviews; Pages not redeployed. Historical 166 gaps / 95 partial unchanged.

## 2026-11-06 — Search preferences repair malformed nested IDs
- Invalid, repeated and over-limit nested saved recent/pinned IDs are now flagged as requiring repair rather than silently treated as fully persisted. Valid sibling IDs remain available in memory; a successful save writes sanitized lists and restores persistence. Focused Node and Chromium regression cases plus synchronized standalone HTML were committed with the living plan.
- Prior exact-head dev push Quality #42140368695 and PR Quality #42140374316 passed; new head CI and full local Chromium pending. PR #189 still lacks reviews, no merge/Pages release; historical 166 gaps / 95 partial unchanged.

## 2026-11-06 — Bound restored search preference payloads
- Preference restore now rejects payloads over 16,384 UTF-16 code units and non-string storage results before JSON parsing, reporting session-only status until a successful rewrite. Added Node and Chromium oversized-payload/recovery regressions; synchronized modular source and standalone HTML. Previous exact-head push #42133233110 and PR #42133237537 passed; new exact-head QA pending, PR #189 review-blocked. Historical 166 gaps / 95 partial unchanged.

## 2026-11-06 — Salvage valid preferences when one stored list is malformed
- A valid JSON preferences object with a non-array recent/pin field now reports non-persistent status until a successful rewrite, while retaining the other valid list. This avoids falsely claiming damaged stored preferences are fully restored. Node state-transition and Chromium corrupted-list assertions added; standalone HTML synchronized.
- Previous exact-head dev push Quality #42126789186 and PR Quality #42126793454 passed for f80ff900; new exact-head CI pending, PR #189 review-gated and production Pages unchanged. Frozen historical 166 gaps / 95 partial unchanged.

## 2026-11-06 — Stabilize quota-recovery Chromium regression
- Fixed a test-only one-shot quota simulation that could be consumed by unrelated startup storage writes. The browser test now arms a failure specifically for the tool-search preferences key immediately before pinning and verifies session-only state before recovery. Production JavaScript and standalone HTML are unchanged. Both previous exact-head Quality runs #42117774224 and #42117785366 failed at this browser assertion; new CI is pending. PR #189 remains review-gated. Historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Search preferences announce recovered persistence
- Pin/unpin now announces when a previously session-only preference successfully saves to browser storage; existing failure message remains. Added structural and 390px Chromium quota-recovery regressions and synchronized the standalone HTML. Prior exact-head push/PR Quality green; new CI and review-gated release pending. Historical 166 gaps/95 partial unchanged.

## 2026-11-05 — Reject malformed saved tool IDs
- Search favourites now discard whitespace-only and control-character IDs from corrupted storage and reject them in the preferences API. Valid IDs, limits and legacy preferences remain supported. Added executable Node negative/boundary cases and Chromium restore assertions; synchronized standalone HTML. Prior dev/PR Quality for 5ced1f4 passed; new exact-head QA and review-gated release pending. Historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Invalid search-preferences root reports session-only state
- Fixed a follow-on persistence-state defect: valid JSON with unsupported top-level types (null, array, number or string) now reports session-only until a successful rewrite, instead of incorrectly claiming preferences were saved. Expanded executable Node and Chromium recovery regressions and kept the standalone HTML synchronized. Exact-head CI pending; PR #189 still requires review and passing checks; historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Search preferences session-only persistence accuracy
- When browser storage cannot be read (blocked or corrupt), tool preferences immediately report non-persistent state instead of falsely reporting success. The in-memory recent and pinned lists still work; successful subsequent writes restore persisted status. Pin actions announce session-only behavior to assistive technology through the existing live region.
- New focused executable Node storage-state transitions and extended Chromium corrupt/blocked-storage assertions; synchronized source and offline standalone HTML. Previous dev Quality #42070115621 passed while PR Quality #42070125639 was cancelled; new exact-head CI, review-gated PR #189 and Pages release remain pending. Historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Deterministic LF standalone output
- Builder explicitly writes LF line endings across operating systems; regression checks generated HTML bytes and unchanged rebuild timestamp. Previous exact-head Quality #42051332141 was cancelled, not passing. PR #189 remains review-blocked; historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Standalone drift diagnostic lists source paths
- Read-only --check lists up to three mismatched module paths, total count and first mismatch position; focused regression asserts two source paths. Exact-head CI pending, previous run cancelled. PR #189 review-blocked; Pages unverified. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-05 — Standalone drift diagnostics count mismatched modules
- Read-only `python scripts/build.py --check` now reports the number of embedded modules that differ from modular sources, while retaining first module and line/column details. Added focused two-module drift and no-rewrite regression. Previous exact-head Quality #42023181030 passed; new head CI and local tests pending. PR #189 remains review-gated, Pages unverified; historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Consistent standalone check snapshot
- Read-only build consistency checking now compares against the original index.html snapshot rather than reopening it after modular source processing. Added isolated regression simulating a concurrent index move; local test execution and new exact-head CI pending. Previous Quality #42014883879 passed. PR #189 remains review-gated; no release. Historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Idempotent standalone rebuild
- Normal `python scripts/build.py` no longer rewrites already synchronized index.html; preserves modification time and avoids unnecessary rebuild churn. Focused isolated subprocess regression checks unchanged bytes, mtime and successful no-op output. Prior exact-head Quality #41999177480 passed; new-head QA pending. No release; frozen historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Standalone drift diagnostics identify source module
- `scripts/build.py --check` now names the first mismatched modular source alongside line and column; focused regression verifies the module hint without rewriting output. Previous exact-head Quality #41990683493 passed; new-head checks pending. No release; historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Standalone builder reports drift column
- Read-only `python scripts/build.py --check` now reports the first mismatched line and 1-based column; focused regression checks an embedded module change at line 3, column 18. Previous exact-head Quality #41984214066 passed; new head QA pending. No release; frozen 166 gaps / 95 partial unchanged.

## 2026-11-05 — Standalone builder identifies drift line
- Read-only --check now identifies the first mismatched line to help repair stale standalone bundles. Added a focused line-number regression. Previous head Quality #41977921641 passed; new exact-head Quality pending. No release; frozen 166 gaps / 95 partial unchanged.

## 2026-11-05 — Standalone builder rejects unsupported CLI arguments
- Reject unknown or extra flags before any index.html read/write; preserve normal build and --check modes. Added focused regression asserting no output mutation on invalid invocation. Previous head Quality #41971023436 green; new exact-head checks pending. No release; historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Read-only standalone bundle consistency check
- Added `python scripts/build.py --check` to report out-of-sync standalone HTML without rewriting it; normal build behavior retained. Added isolated regression for matching content, drift detection, byte-preserving failure and ordinary repair. New exact-head CI pending; PR #189 review-gated; no Pages release. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-05 — Latest exact-head Quality confirmed; checkout unavailable
- Quality [41945883245](https://github.com/saeedsai/ProMathStudio/actions/runs/41945883245) succeeded for dev `20c89b114d47f3d9fd09c929392b26fae7919325`. PR #189 remains review-gated. Local git checkout failed DNS resolution, preventing safe standalone source/bundle and browser-test edits; no application feature or regression was committed. Main Quality and Pages not verified. Historical 166 gaps / 95 partial unchanged.

## 2026-11-05 — Exact-head Quality green; release still review-gated
- Quality [41937533190](https://github.com/saeedsai/ProMathStudio/actions/runs/41937533190) completed successfully for dev 262ba648be1fa99959a4a79a84d6bf5231275f1f, including structural and Chromium checks. PR #189 has no submitted reviews. Local git checkout remains unavailable (GitHub DNS failure), so no application source/test was changed in this checkpoint; main Quality and Pages remain unverified. Ledger/changelog updates require their own exact-head Quality before promotion. Frozen 166 gaps / 95 partial unchanged.

## 2026-11-05 — Browse All Tools GNSS catalog regression
- 2026-11-05 (CI-PIPE-CATALOG-167; dev QA pending): corrected engineering pipe/digital-logic browser catalog assertions for implemented GNSS least-squares positioning and control frequency response; retained planned spectral-analysis negative assertion. Exact-head Quality/Pages pending; no application source feature in this iteration.

- Exact-head Quality [41921062294](https://github.com/saeedsai/ProMathStudio/actions/runs/41921062294) passed structural and browser steps through 209, then failed at step 210 because a stale browse assertion excluded implemented GNSS. The regression now requires canonical `catalog:gnss.positioning.least.squares` while excluding planned-only `catalog:signals.spectral.analysis`. Browser rerun pending; no application source change or release.

## 2026-11-04 — CI browse disclosure timing regression

- CI [41911514968](https://github.com/saeedsai/ProMathStudio/actions/runs/41911514968) passed structural and browser checks through step 209, then failed at browse-group assertion in `tests/smoke_tool_search_favorites.py:239`. The native `<details>` toggle event populates groups asynchronously. The browser test now waits for populated groups without relaxing any browse navigation, keyboard, storage or route assertions. Exact-head CI and release remain pending; no application source feature added.

## Unreleased — 2026-11-04
- 2026-11-04 (CI-PINS-GNSS-164; QA pending): corrected the tool-search favourites regression to treat implemented GNSS positioning as available; at full pin capacity it must refuse a new pin, while genuinely planned spectral analysis remains unpinnable. Exact-head Chromium and release remain pending; frozen 166 gaps / 95 partial unchanged.
- CI search regression: use Playwright forced pointer click to exercise refusal on an aria-disabled planned-only search result; preserve accessibility and workspace invariants. Exact-head browser QA pending.

- 2026-11-04 (CI-SEARCH-VISIBILITY-161; exact-head QA pending): repaired browser regression ordering for mixed planned/available tool-search results. The planned result is now clicked while the popup remains visible, preserving disabled-result status and no-navigation checks; the preceding Enter had legitimately opened an available result and dismissed the popup. Source behavior unchanged; local Chromium unavailable; PR #189 and Pages remain gated. Frozen 166 gaps / 95 partial unchanged.\n- 2026-11-04 (CI-CANCELLED-160; QA pending): exact-head Quality run 41863330816 was cancelled during browser dependency installation after structural checks passed. No Chromium verification, source change, or release this iteration; recorded blocker and next five acceptance gates in the living plan. Frozen 166 gaps / 95 partial unchanged.
- 2026-11-04 (CI-CATALOG-STATUS-157; exact-head CI pending): the consolidated branch's structural tests passed, but browser Quality failed because an old catalog smoke treated implemented control.frequency.response as planned. Updated its assertion to require an Open action and no planned label, while retaining the genuine planned-tool negative regression. Reconciled history-only main ancestry without changing released code. Full Quality and Pages release are still pending; frozen 166-gap/95-partial inventory unchanged.

- QA (dev): strengthen global tool-search regression for mixed planned/available matches, verifying arrow/Home/End never select disabled planned entries; exact-head Chromium recheck pending ([3f9fbf4](https://github.com/saeedsai/ProMathStudio/commit/3f9fbf4809dbfc12c092c162e641d26512cd8a8b)).
- Fixed global tool-search browser regression to recognize implemented digital logic and preserve disabled/keyboard refusal coverage for planned signal spectral analysis (CI run 41831603088; dev QA pending).
- 2026-11-04 (BRANCH-CONSOLIDATION-156; exact-head CI pending): reconciled the existing Claude engineering-feature branch into dev without discarding either history; preserved 11 additional JavaScript modules, source/bundle consistency, toolbar favourites and recent tools, disabled-result keyboard/Home/End improvements, builder security guards, all existing tests and both development ledgers. PR #189 to main remains gated by exact-head structural/browser QA, reviews and Pages confirmation. Historical 166 gaps / 95 partial unchanged.
- 2026-11-04 (CI-SYMLINK-FIX-155; dev QA pending): repaired malformed literal-newline symlink regression fixture responsible for failed exact-head Quality #41817935010; builder now also rejects modules reached via symlinked `src` directory, with isolated external-file/index byte-preservation regression. Local tests unavailable (GitHub DNS); exact-head CI and release pending. Historical 166 gaps / 95 partial unchanged.
- 2026-11-04 (BUILD-MODULE-SYMLINK-154; dev QA pending): refuse symlinked JavaScript module sources before standalone bundling; focused subprocess regression asserts symlink, external target and index bytes remain untouched. Exact-head CI and release pending; historical 166-gap/95-partial audit unchanged.
- 2026-11-04 (BUILD-SYMLINK-153; dev QA pending): reject symlinked standalone index.html before reading or writing it; isolated subprocess regression verifies the symlink and external target remain unchanged. Exact-head Quality pending; no release claimed.
- 2026-11-04 (UI-SEARCH-HOME-END-152; dev QA pending): Home/End navigates to first/last enabled search result without selecting planned-only tools; focused source/bundle regression. Exact-head CI and release pending.
- 2026-11-04 (UI-SEARCH-DISABLED-151; dev QA pending): planned-only tool search mouse clicks now announce unavailable status without marking disabled results active; focused source/bundle regression. Exact-head Quality and release pending.
- 2026-11-04 (UI-SEARCH-KEYBOARD-150; dev QA pending): tool-search ArrowUp/Down skips disabled planned entries, with browser regression for planned-only results; exact-head Quality and release pending.
- BUILD-INDEX-CONTROL-149 (dev, QA pending): reject unexpected ASCII controls in index.html before rewrite; subprocess regression asserts original bytes preserved.\n## 2026-11-04 — BUILD-MODULE-CRLF-147

- BUILD-MODULE-CONTROL-148 (dev, QA pending): fail fast when JavaScript modules contain nonprinting ASCII control characters other than TAB/LF; subprocess regression checks four controls and unchanged standalone HTML. Exact-head CI and release pending; frozen 166-gap/95-partial baseline unchanged.
- Preserve raw newlines when reading standalone JavaScript modules; reject CRLF/lone CR module input before HTML rewrite, preventing silent newline normalization. Add focused subprocess regression for diagnostic and unchanged index. Exact-head CI pending; no release claimed.

## 2026-11-04 — CI-CRLF-146
- Fix standalone builder carriage-return validation by disabling Python universal-newline translation when reading `index.html`. Prevents CRLF/lone-CR HTML from bypassing the fail-fast guard.
- Add subprocess regression for lone CR and mixed newline files, asserting diagnostic and byte-for-byte preservation. Exact-head CI pending; no release claimed.

- 2026-11-04 (BUILD-INDEX-CRLF-145; dev QA pending): reject carriage returns in standalone index before Python newline normalization can silently rewrite CRLF input; subprocess regression verifies unchanged bytes. Prior PR Quality 41751753649 passed; new head QA and release pending.
- 2026-11-04 (BUILD-INDEX-BOM-144; dev QA pending): reject leading UTF-8 BOM in standalone index before rewriting; isolated subprocess regression asserts diagnostic and unchanged input. Exact-head CI and release pending.
- 2026-11-04 (BUILD-INDEX-NUL-143; dev QA pending): standalone builder rejects embedded NUL in index.html before rewriting; isolated subprocess regression verifies diagnostic and byte-preserving failure. Exact-head CI and release pending.
- 2026-11-03 (parallel batch 150–155; branch QA pending). Fourth round of parallel agents, plus a CI repair:
  - **CTRL-MARGINS-150:** gain/phase margins, crossover frequencies, closed-loop bandwidth and resonant peak in a new Control Theory Frequency response panel, with crossover markers on the Bode plot. `control.frequency.response` is now available in the catalog.
  - **GNSS-151:** weighted Gauss–Newton single-epoch positioning with clock bias, DOPs, WGS-84 coordinates and a sky plot. No atmospheric, relativistic or Sagnac corrections. `gnss.positioning.least.squares` is now available.
  - **FUNC-ANALYSIS-152:** numerical inequality solving over intervals and function domain analysis (zeros, poles, extrema, monotonicity, symmetry), reusing the shared root finder.
  - **RANDOM-153:** PCG32-seeded samplers, plus plain Monte Carlo and Halton quasi-Monte Carlo integration with a convergence table.
  - **SEARCH-FAVS-154:** "Find a tool" adds Recent and Pinned tools (Alt+P to pin) and a collapsed "Browse all tools" list grouped by workspace. Preferences are stored per viewer with safe fallbacks.
  - **DOCS-GUIDE-155:** `docs/USER_GUIDE.md` covers every tool with a worked example taken from its regression test. `tests/test_user_guide.py` fails if a panel or catalog tool is left undocumented.
  - **CI-NUMPY-FIX:** Quality runs 41734137142/41734143560 failed because `smoke_interpolation_splines.py` imported numpy, which CI does not install. `smoke_matrix_extras.py` had the same problem. Both now use pure-Python or fixed references with unchanged tolerances.
- 2026-11-03 (parallel batch 142–149; branch QA pending). Eight features from a third round of parallel agents:
  - **POLY-142 polynomial tools:** Aberth–Ehrlich complex roots with backward errors and multiplicity clustering, plus Horner evaluation, derivative/integral, add/multiply/divide, numerical GCD and build-from-roots.
  - **NLFIT-143 nonlinear fitting:** Levenberg–Marquardt with standard errors and t intervals, verified against NIST Misra1a, with warnings for parameters that cannot be identified.
  - **FILTERS-144 digital filters:** convolution and correlation, windowed-sinc FIR, Butterworth IIR (order 1–8, second-order sections), zero-phase filtfilt and frequency response.
  - **VECCALC-145 vector calculus:** Ridders derivatives of order 1–4, gradient, Hessian, Jacobian, divergence, curl, Laplacian and directional derivatives, with error estimates; kinks are refused.
  - **MATRIX-EXTRAS-146:** for matrices up to 8×8, Cholesky and LDLᵀ, Jacobi-SVD rank with null-space and column-space bases, determinant, characteristic polynomial, norms and κ₂.
  - **MULTIVAR-147 multivariate analysis:** covariance and Pearson/Spearman matrices, a scatter matrix, PCA and seeded k-means++ on Data Tables columns.
  - **FIELDS-148 vector fields:** quiver plots, RK4 streamlines, slope fields with solution curves, heuristic equilibria and reduced-motion-aware particle animation.
  - **ENG-THERMO-CIRCUITS-149:** `thermal.cycle.analysis` (Otto, Diesel and Brayton with animated P–v/T–s diagrams) and `circuits.network.analysis` (a DC modified-nodal-analysis netlist solver with animated current flow) are now available.
  - **Tests:** each feature has reference, negative, keyboard and 390/1280 px tests registered in Quality.
- 2026-11-03 (CI-SPLINE-NUMPY-142; dev QA pending): removed undeclared NumPy dependency from cubic spline browser smoke's independent dense numerical reference; pure-Python partial-pivot solver retains nonuniform spline checks and adds pivot/singular controls. Production spline code unchanged; exact-head CI pending.
- 2026-11-03 (UI-TOOL-SEARCH-141; branch QA pending): global "Find a tool" search in the workspace bar (`/` or Ctrl/Cmd+K). It indexes every tool panel, workspace task and Engineering catalog tool at runtime, matches a small synonym map, and opens the chosen tool in the right workspace without clearing inputs. Results use an accessible combobox with keyboard navigation and announced counts. Planned tools are marked "Planned". Works at 390px.
- 2026-11-03 (parallel batch 135–140; branch QA pending). Six features from a second round of parallel agents, integrated onto one branch:
  - **STATS-TESTS-135:** hypothesis tests with confidence intervals: one-sample, Welch, pooled and paired t-tests; chi-square goodness-of-fit and r×c independence (optional Yates); one-proportion z-test with Wilson interval; exact binomial with Clopper–Pearson; chi-square variance interval. Results include effect sizes and assumptions, and values match scipy within 1e-8.
  - **GRAPH-OVERLAY-136:** implicit, parametric and polar curves can be overlaid on the main 2D graph (up to 8). Implicit curves are re-traced on zoom and pan, and overlays persist in projects with schema validation before import.
  - **ENG-SIM-UNITS-137:** Engineering simulation inputs accept units (e.g. `12 ft`, `3.5 kN`, `212 °F`) through the shared units module. Field-specific errors report dimension mismatches.
  - **BVP-SHOOT-138:** two-point boundary-value problems solved by shooting on the existing RK4/TR-BDF2 solvers, with Dirichlet, Neumann or Robin conditions. Every bracketed solution is reported (for example both Bratu solutions), as are non-unique and no-solution cases.
  - **UNCERTAINTY-139:** GUM first-order propagation with correlations and contributions, and seeded deterministic Monte Carlo with symmetric/shortest intervals, a histogram and a non-linearity flag.
  - **SPLINES-140:** natural, clamped, not-a-knot and periodic cubic splines plus Akima and modified Akima, with derivatives and the exact spline integral.
  - **Tests:** each feature adds reference, negative, keyboard and responsive browser tests, registered in Quality.
- 2026-11-03 (parallel batch 129–134; branch QA pending). Six new modules were built by parallel agents and integrated onto one branch:
  - **STATS-DIST-129:** Normal, Student t, chi-square, exponential, binomial and Poisson pdf/pmf, CDF, survival and quantile functions, built on in-house log-gamma, incomplete gamma/beta and erf. Also descriptive statistics for Data Tables columns (type-7 quartiles, skewness, Pearson r, covariance). There are no hypothesis tests or confidence intervals.
  - **GRAPH-CURVES-130:** implicit F(x,y)=0 curves via marching squares with refined crossings; pole and jump crossings are rejected and counted. Also parametric and polar curves, equal-aspect axes and Data Tables export.
  - **OPT-LP-NM-131:** two-phase simplex with Bland's rule for linear programs of up to 10×10, reporting optimal, infeasible or unbounded with residuals checked. Also bounded Nelder–Mead for f(x,y[,z]) with budgets and a heuristic gradient diagnostic.
  - **UNITS-132:** unit conversion with exact SI and NIST factors and dimension vectors, using a strict parser that does not use eval. Absolute temperatures apply to bare units only; inside compound units they are differences.
  - **INT-MULTI-133:** double integrals with x-dependent inner limits and triple integrals over boxes, using nested adaptive Gauss–Kronrod G7–K15 with an error estimate and an evaluation budget. Also trapezoid/Simpson integration of Data Tables columns with a cumulative column export.
  - **ODE-STIFF-134:** adaptive L-stable TR-BDF2 for scalar and two-state stiff initial-value problems (Newton with a finite-difference Jacobian, rtol/atol control, explicit failure messages).
  - **Tests:** each module ships reference, negative, keyboard and 390/1280 px browser tests, plus a structural/Node test, all registered in Quality. Error figures are estimates, not certified bounds.
- 2026-11-03 (QA-SCHEMA-FLAKE): `smoke_project_schema.py` was not reproduced in 15/15 isolated reruns. The earlier single failure is treated as transient and no assertions were changed.
- 2026-11-03 (MATH-BRENT-POLE-127; branch QA pending): Brent refinement refuses sign-changing brackets without a small residual, with a located diagnostic: "Suspected pole near x ≈ …" when |f| grows above 10× the endpoint values or overflows, and "Suspected jump discontinuity" otherwise. Undefined midpoints (0/0 at a step) probe both neighbours before classifying. References: tan(x) on [1, 2], 1/(x−0.3), 1/(x−1), the cubic pole −1/(x+2)³ located within the cap-limited 2e-4, and step jumps; true roots still refine.
- 2026-11-03 (MATH-QR-PIVOT-128; branch QA pending): QR output adds a column-pivoting screen (classic largest-residual-norm greedy Gram–Schmidt) with pivot order and a pivoted minimum independence ratio. Node regression: invariance under all six column permutations of a near-dependent 3×3, exact sin 45° ratio, orthogonal and dependent references.
- 2026-11-03 (ENG-SIM-EXT-126; branch QA pending):
  - **Forced vibration:** new `mechanical.vibration.forced` simulation of a forced SDOF oscillator with an animated resonance curve, solved with the existing RK4 solver. Steady amplitude and phase are least-squares fitted and compared with 1/√((1−r²)²+(2ζr)²).
  - **General beam solver:** handles combined loads (P1 + P2 + UDL) and an overhanging span, using statics plus double integration of −M/EI. It is verified against the closed forms (1e-5), superposition, equilibrium and the overhang tip deflection Pc²(xB+c)/3EI.
  - **Exports:** every simulation/animation can send its time series to Data Tables (unit-named columns), plot it in Graphs, or download the current canvas frame as a PNG.
  - **Control Theory module:** the controller was extracted to `src/control-theory.js` with a byte-identical rebuild.
  - **Tests:** `tests/smoke_engineering_sim_extensions.py`, `tests/test_control_theory_module.py`.
- 2026-11-03 (BUILD-INDEX-UTF8-126; dev QA pending): Standalone builder now identifies invalid UTF-8 in index.html and preserves its bytes; isolated subprocess regression checks the diagnostic and unchanged input. Exact-head Quality and release pending.
- 2026-11-03 (ENG-SIMULATIONS-125; branch QA pending): Added engineering simulations with physics-driven animation in the renamed "Engineering simulations & animations" panel. A new DOM-free kernel module (`src/engineering-simulations.js`, SI units, stated assumptions) provides five simulations:
  - **Euler–Bernoulli beam** (`structures.beam.deflection`, now available): simply supported or cantilever, point or uniform load; deflection, moment, shear, reactions and bending stress; the animated load ramp colours the beam by moment.
  - **Two-body Earth orbit** (`aerospace.orbit.propagation`, now available): velocity-Verlet propagation checked against Kepler period, energy and angular momentum.
  - **Series RLC step response** (new `circuits.rlc.series.transient`): dimensionless form on the existing RK4 solver; current dots and capacitor charge are animated.
  - **Projectile with quadratic drag** (new `mechanics.projectile.drag`): compared against the vacuum parabola.
  - **1-D heat conduction in a rod** (new `thermal.conduction.rod`): material presets on the existing FTCS solver; heat-map animation.

  Catalog "Open existing tool" opens and runs each simulation. Pipe networks, general circuit networks and thermodynamic cycles stay planned. `tests/smoke_engineering_simulations.py` covers:
  - **Beam:** four closed-form maxima to 1e-12, equilibrium, EI·v″ = −M and the off-centre maximum location.
  - **Orbit:** vis-viva speed, period and closure.
  - **RLC:** analytic underdamped vC and i within 1e-6·V.
  - **Projectile:** drag-free range and apex.
  - **Rod:** within 0.25 °C of a 400-term Fourier series.
  - **Other:** invalid inputs, keyboard routing, select inputs, 390/768/1280 layout and reduced motion.

  These are textbook-model estimates, not certified designs or code checks.
- 2026-11-03 (BUILD-UTF8-DIAGNOSTIC-125; dev QA pending): Standalone builder reports the module path on invalid UTF-8 instead of an opaque decoding traceback; subprocess regression verifies the failure and unchanged HTML. Exact-head CI and release pending.
- 2026-11-03 (ENG-VISUALS-124; branch QA pending): Engineering Toolbox gains an "Engineering animations" panel (`src/engineering-visuals.js`) with six animated canvas visuals, each linked to an available catalog tool and computed by its existing solver. They cover: mass–spring–damper step response (RK4 system; `control.transient.two.state`), nonlinear pendulum with energy-drift report (RK4; `ode.ivp.scalar`), two-tone signal with live FFT spectrum (`signals.fft.1d`), root bracket halving (`numerical.root.brent`), integral as accumulated area (adaptive Simpson; `numerical.quadrature.adaptive`) and symmetric matrix circle→ellipse transform with eigenvectors (`matrix.eigen.symmetric.small`). Controls include Play/Pause (aria-pressed) and Step, with live text summaries and a canvas aria-label. With prefers-reduced-motion the final frame is shown without autoplay. Catalog cards keep a single action button and gain a text note. The regression checks analytic references: underdamped step response within 1e-5 and overshoot e^(−πζ/√(1−ζ²)); small-angle period within 0.1%; energy drift below 1e-6; FFT bin amplitudes within 1e-12; Wallis cubic bracket width 2/2^14; ∫₀^π sin = 2; golden-ratio eigenvalues. It also covers invalid-input recovery, keyboard use, 390/768/1280 layout and a project round trip. These are illustrations, not certified engineering designs.
- 2026-11-03 (ARCH-COMPLEX-GRAPH-MODULE-123; branch QA pending): Extracted the inline Complex Graph UI controller to canonical `src/complex-graph.js`, declared in `scripts/build.py`; the rebuilt standalone `index.html` is byte-identical (md5 unchanged, bundle size delta 0 bytes; one extra 3.9 KB source file). New Chromium regression checks z², 1/z and exp(z) references, keyboard activation, 390/768/1280 layout without horizontal overflow, invalid/overflow recovery and a saved-project round trip.
- 2026-11-03 (DATA-PROJECT-ATOMIC-122; branch QA pending): Saved custom functions are validated as strictly as the editor (unique case-insensitive identifiers ≤64 chars, 1–6 distinct arguments, bounded expression/source, formula/python type) before any module is touched; previously restore silently dropped such entries after other state changed. New cross-module browser regression imports malformed v1/v2 fixtures (duplicate columns, bad/duplicate/argument-less/61 functions, short weights) and schema-valid fixtures with injected Data Tables/curve-fit apply failures, asserting the full project snapshot (Matrix, tables, notebook, functions, graph) is unchanged; legacy v1 without Matrix keys and v2 round trips still import.
- 2026-11-03 (MATH-ROOT-DISCONTINUITY-120; branch QA pending): Scalar root search records bounded (20-location) rejected sign changes, classifying them heuristically as possible poles (residual grows during bisection, or a nonfinite grid sample between opposite-sign neighbours) or jumps, and counts grid intervals with multiple quarter-probe sign changes as under-resolved oscillation. Calculator output lists both; new `rootStatus` values `discontinuity-screened` and `under-resolved-oscillation`. Browser regression covers 1/(x-0.3), 1/x, tan(x), step jumps, bounded tan(x) on [-100,100], sin(1/x), smooth controls and 390/768/1280 UI recovery.
- 2026-11-03 (MATH-QR-RANK-BOUNDARY-121; branch QA pending): QR reports minimum orthogonalized-column independence ratio, margin to the 1e-12 rejection cutoff and near-threshold guidance. Node regression uses exact binary64 analytic references straddling the cutoff (2^-33, 2^-36, 2^-39 accepted; 2^-40, 2^-45, singular and zero-column rejected) plus range/orthogonal-complement RHS perturbations with conditioning-aware tolerances.
- 2026-11-03 (BUILD-HTML-CLOSER-119; dev QA pending): Reject HTML comment closing delimiter in standalone JS module sources before writing index; focused subprocess negative regression checks diagnostic and unchanged original HTML. PR #179 merged after exact-head CI; new head QA/release pending.
- 2026-11-03 (BUILD-HTML-COMMENT-118; dev QA pending): Reject HTML comment openers inside standalone inline module sources; subprocess regression asserts rejection and original HTML preservation. Exact-head Quality and release pending.
- 2026-11-03 (BUILD-NUL-117, dev; QA pending): Reject NUL-containing module sources before standalone HTML write; focused rollback regression; exact-head CI pending.
- 2026-11-03 (BUILD-BOM-116, dev; CI pending): Reject UTF-8 BOM-prefixed standalone JS modules before overwriting bundled HTML; isolated subprocess regression asserts error and unchanged original HTML. Prior PR Quality 41669319024 passed at previous dev head; new exact-head QA and Pages pending.
- 2026-11-03: Standalone build rejects empty or whitespace-only module source before replacing HTML; focused rollback regression (BUILD-EMPTY-SOURCE-115; dev, QA pending).
## 2026-11-03 — Reject script openers in standalone module sources (dev QA pending)

- BUILD-SOURCE-OPENER-114: reject mixed-case and whitespace-delimited HTML script openers inside modular JavaScript before writing standalone HTML; focused subprocess regression verifies diagnostic and atomic rollback. Exact-head Quality, PR release, main Quality and Pages pending. Historical 166 gaps/95 partial features unchanged.

## 2026-11-03 — Missing standalone module source diagnostic (dev QA pending)

- BUILD-MISSING-SOURCE-113: fail with an explicit missing-source path before writing standalone HTML when a module file is absent; add subprocess regression asserting diagnostic and original-index preservation. Exact-head Quality and Pages pending.
- PR #178 merged normally at `1df9a6fbf69678268a937c06c39786c6a7fe3702` after successful exact-head Quality run 41640828944; post-merge main Quality and Pages verification pending.

## 2026-11-03 — Build missing-close regression correction

- Fixed a truncated standalone script fixture to use actual newlines, allowing the existing missing-close diagnostic to be tested. CI run 41631737725 previously failed 1/291 structural tests due to the fixture; new exact-head CI pending. No production release claimed.

- 2026-11-03 (BUILD-MISSING-CLOSE-112; dev QA pending): Standalone builder now raises an explicit error for a truncated inline module without a closing script tag; isolated regression checks failure and original HTML preservation. New exact-head CI and deployment pending.
- 2026-11-03 BUILD-NESTED-CASE-111 (dev QA pending): Detect uppercase, tabbed and bare nested script openers during standalone rebuild; focused negative regression preserves original index. PR #177 merged after exact-head dev/PR Quality success; new exact-head CI/Pages pending. Frozen 166 gaps/95 partials unchanged.
- 2026-11-03 BUILD-NESTED-SCRIPT-110: reject nested `<script ` opening tags inside standalone module boundaries; isolated regression confirms rejection without modifying HTML. PR #176 merged after green PR Quality; new exact-head CI and release pending. Historical 166 gaps/95 partials unchanged.
- 2026-11-03 (BUILD-SCRIPT-TERMINATOR-109; dev QA pending): Reject case-insensitive HTML script closing sequences embedded in modular JavaScript before writing standalone index; regression verifies failure leaves index unchanged. PR #175 merged after exact-head PR Quality success; main Quality/Pages pending verification.
- 2026-11-03 (BUILD-MARKER-108; dev QA pending): Fail standalone build when a module script marker is missing or duplicated; isolated regression verifies no index overwrite. PR #174 merged after exact-head development and PR Quality success; main Quality/Pages for merge pending verification.
- 2026-11-03 (DATA-COLUMN-IDENTITY-107; dev QA pending): Reject blank and case/trim-equivalent duplicate saved Data Tables column names in v1/v2 projects; preserve unique legacy columns, add focused Node/Python and offline parity regression. Release requires exact-head Quality and Pages. Prior PR #173 main Quality and Pages succeeded.
- Fixed the saved-project empty-workbook regression fixture: legacy workbooks without a selected sheet remain accepted, while stale or null selected IDs are rejected in both v1/v2; restores consistency with strict import validation and addresses PR #173 Quality failure.
- 2026-11-03 (DATA-PROJECT-EMPTY-SELECTION-106; dev CI pending): Reject explicit stale/null selected sheet in empty saved Data Tables workbooks; preserve valid legacy empty workbook without selected ID; v1/v2 regression and standalone parity.
- 2026-11-03 (PR #172 merged): Saved table ID identity validation released via ordinary PR merge 6cdcb462f4be9c8d6e5fe14faa2784e6e25cfd4b after PR Quality 41563684929 passed; post-merge main Quality/Pages pending.
- **Unreleased (DATA-PROJECT-ID-105):** Validate unique, bounded saved Data Tables IDs during project migration to reject ambiguous duplicate targets while retaining legacy missing-ID compatibility; add focused v1/v2 regression and offline parity coverage. Release pending CI and Pages verification.
- 2026-11-03 (MATH-QR-GATE-104, implemented on dev; CI pending): Expose effective QR orthogonality tolerance, near-exact skip state and transparent ordinary/relaxed guidance in Calculator for weighted and unweighted least squares; focused Node/Python and responsive Chromium regression, offline parity. Acceptance heuristic, not certified accuracy.
- 2026-11-03 (PR #170 merged): Near-rank QR guard exact dev Quality 41543081907 and PR Quality 41543129569 passed; ordinary merge 21ff2ab0c21c47ac2eb818a9b4823ac684ac669f; dev fast-forwarded; post-merge Quality/Pages pending verification.
- 2026-11-03 (MATH-QR-ORTHO-103, implemented on dev; CI pending): Roundoff-aware QR orthogonality gate prevents false rejection of near-rank weighted fits with small nonzero residual; independent 90-digit Decimal references for 1e-4..1e-11 and extreme weights, responsive Chromium recovery, offline parity. Not a certified coefficient-error bound.
- 2026-11-03 (PR #169 merged): Weighted normwise residual ratio passed dev Quality 41533768610 and PR Quality 41533824339 at exact head 48aacbaee4f8d24dfd89ac67ab7d3efecc33b681; ordinary merge f92bfda0ece73d8176607d84c8a9a15ee84aad7c; main Quality/Pages pending verification.
- 2026-11-02 (MATH-WLS-NORMRES-102, implemented on dev; exact-head CI/Pages pending): QR-reused weighted normwise fit-residual ratio, analytic 0.11625798496246446, scale/zero/near-rank/invalid tests, standalone parity and responsive Chromium gate. Not a certified least-squares backward error or coefficient accuracy bound.
- 2026-11-02 (PR #168 merged): Weighted fitted predictions passed exact PR Quality 41525568357; merge 5f6a7342091f1465b5fb8f417874c0b8194736e0; post-merge main Quality/Pages pending verification.
- 2026-11-02 (MATH-WLS-FITTED-101, implemented on dev; exact-head CI/Pages pending): Weighted fitted RHS predictions in original units, reused for residuals; analytic [33/35,74/35,23/7], near-rank 1e-4..1e-11, scale/invalid/singular/immutability, offline parity and responsive Chromium regression. Near-rank coefficients may be sensitive despite stable predictions.
- 2026-11-02 (PR #167, merged): MATH-WLS-ROUND-099 and MATH-WLS-SHARES-100 passed exact PR Quality 41515977252; merge SHA 792fd8b914e9c65548a3548534ab2eee2ffb0bbc. Main Quality/Pages post-merge pending independent verification.
- 2026-11-02 (MATH-WLS-SHARES-100, implemented on dev; CI/release pending): Per-observation relative-weighted squared-residual shares, analytic [1/105,4/105,100/105], scale invariance, zero/near-rank/invalid and mandatory responsive browser regression, standalone parity. Not outlier probabilities or statistical uncertainty.
- 2026-11-02 (MATH-WLS-ROUND-099, implemented on dev; release pending): Weighted coefficient numerical-resolution screen κ₂×binary64 epsilon, near-rank warning, numerical/invalid and Chromium keyboard/mobile recovery regressions, standalone parity; not a certified error bound.
- 2026-11-02 (MATH-WLS-RHS-PERCENT-098, implemented on dev; CI/release pending): QR-reused exact independent ±1% proportional RHS coefficient sensitivity, eight-corner/near-rank/scale/zero/invalid references, source parity and mandatory responsive Chromium keyboard/recovery. Fixed design and weights only; no statistical uncertainty claim.
- 2026-11-02 (MATH-WLS-SINGULAR-097, released via PR #165): dev=main cb10009d8ce32a9af705464611a7235f851a0062; source dev Quality 41496774146 and PR Quality 41498011046 passed, Pages 41499760312 succeeded; post-merge main/dev Quality 41499762702/41499815974 still running at inspection.
- 2026-11-02 (MATH-WLS-SINGULAR-097, implemented on dev; exact-head CI/PR/Pages pending): Stable 3×2 weighted design singular values via scaled cross-product geometry, analytical near-rank/orthogonal, invalid, offline parity and mandatory responsive Chromium regressions. Not a coefficient-error or uncertainty guarantee.
- 2026-11-02 (MATH-WLS-RHS-BOX-096, released via PR #164): dev=main de6afa3de143b83ea0d3f82ef8535fe363c47b48; main Quality 41489685375 and Pages 41489684886 passed; post-merge dev Quality 41489704169 cancelled; hosted behavior unverified.
- 2026-11-02 (MATH-WLS-RHS-BOX-096, implemented on dev; exact-head CI/PR/Pages pending): Added exact QR-reused fixed-design RHS independent ±1 box coefficient sensitivity, analytical/eight-corner/negative and mandatory responsive Chromium regressions, offline bundle parity. Deterministic bound only; not statistical uncertainty or a bound for design/weight changes.
- 2026-11-02 (MATH-WLS-COLNORM-095, implemented on dev; exact-head CI/PR/Pages pending): Added stable column-normalized weighted design 2-norm condition using cross-product geometry, invariant to positive individual column scales; analytical/invalid and mandatory responsive Chromium regressions, standalone parity. Not a certified error or uncertainty bound.
- 2026-11-02 (MATH-WLS-SPECTRAL-094, released via PR #162): dev=main 9c27a104d8cd43cbf67043aabe74700b22d008ba; main Quality 41481062296 and Pages 41481060885 passed; post-merge dev Quality 41481080429 pending at discovery, hosted behavior independently unverified.
- 2026-11-02 (MATH-WLS-SPECTRAL-094, implemented on dev; exact-head CI/PR/Pages pending): Added scale-safe weighted 3×2 spectral 2-norm condition estimate using cross-product geometry, near-rank advisory, numerical/invalid and responsive Chromium regressions, offline bundle parity. Not a certified error or statistical uncertainty bound.
- 2026-11-02 (MATH-WLS-WEIGHT-093, released via PR #161): dev=main aa49c2121c16b6b5d170e5fbd94dd44efd928375; main/dev Quality 41470848664/41470867553 and Pages 41470846607 passed; hosted interaction unverified.
- 2026-11-02 (MATH-WLS-WEIGHT-093, implemented on dev; CI/PR/Pages pending): Added QR-reused first-order log-weight coefficient sensitivity, independent analytic/finite-difference and mandatory responsive Chromium regressions, source parity; no finite-change or uncertainty certification.
- 2026-11-02 (MATH-WLS-EFFN-092, released via PR #160): dev=main 477037373264c1fc23cb855c3634a114798a77a5; main/dev Quality 41461521241/41461543539 and Pages 41461520878 succeeded; hosted interaction unverified.
- 2026-11-02 (MATH-WLS-EFFN-092, implemented on dev; exact-head CI/release pending): Added overflow-safe Kish-style relative-weight effective count and concentration advisory to bounded 3×2 weighted least squares; no statistical sample-size or uncertainty claim. Added numerical/negative, standalone-parity and mandatory responsive Chromium regressions.
- 2026-11-02 (MATH-WLS-SINE-091, released via PR #159): Verified dev=main c681eca8846c8b1c731c4608ebe3c045dbd810d2; main/dev Quality 41451648477/41451668193 and Pages 41451647440 passed; hosted interaction unverified.
- 2026-11-02 (MATH-WLS-SINE-091, implemented on dev; CI/release pending): Added scale-independent weighted design column sine and near-parallel warning, analytic/negative and mandatory responsive Chromium regressions, offline bundle parity. No certified condition number claim.
- 2026-11-02 (MATH-WLS-AREA-090, released via PR #158): Verified dev=main d77714614a49b79f8086e4786e4fabc45f7abda2, main/dev Quality 41446512427/41446526651 and Pages 41446511714 passed; hosted behavior unverified.
- 2026-11-02 (MATH-WLS-AREA-090, implemented on dev; CI/release pending): Added scale-independent retained-row normalized area diagnostic for weighted 3×2 leave-one-out fits, with conservative near-dependent deletion guard (≤1e-8) and explicit non-certifying guidance; analytic, singular, invalid, offline parity and mandatory responsive Chromium regressions.
- 2026-11-02 (MATH-WLS-PREDICTION-089, released via PR #157): Verified dev=main 4921caaab9c03481f57cb95e285bbca7924b32de; main/dev Quality 41442802414/41442818112 and Pages 41442800826 passed; hosted interaction independently unverified.
- 2026-11-02 (MATH-WLS-PREDICTION-089, implemented on dev; CI/release pending): Added weighted excluded-row predicted values using existing QR leave-one-out residuals, explicit sign convention and singular-unavailable handling; direct-refit numerical references, offline parity and mandatory responsive Chromium regression.
- 2026-11-02 (MATH-WLS-DELETE-088, released via PR #156): Synchronized dev/main 2409311ea4d60eb7031b633aa88017427e388e8b; main/dev Quality and Pages succeeded, hosted interaction unverified.

# Changelog

- 2026-11-02 (MATH-WLS-DELETE-088, implemented on dev; CI/release pending): Added QR-reused weighted leave-one-out coefficient influence shifts for 3×2 fits, explicit singular-unavailable and fixed-design limitations; direct-refit/weight-scale numerical references, source/bundle parity and mandatory responsive Chromium regression.
- 2026-11-02 (MATH-WLS-LOO-087, released via PR #155): Verified synchronized dev/main e07b5db8aa7023a7d14d1587fdcaae38f8b9ef80, green main/dev Quality and successful Pages deployment; hosted interaction independently unverified.

- 2026-11-02 (MATH-WLS-LOO-087, implemented on dev; CI/release pending): Added weighted 3×2 QR-based leave-one-out prediction residuals and weighted PRESS, with unavailable classification for singular/high-leverage row removal; direct refit, weight scaling, offline parity and mandatory responsive Chromium regressions. No uncertainty certification.
- 2026-11-02 (MATH-ROOT-QUARTER-086, released via PR #154): Verified synchronized dev/main 9d1fcd13b5670ffed1f70fe8eab7ab00d522118c, green main/dev Quality and successful Pages deployment; hosted interaction independently unverified.

- 2026-11-02 (MATH-ROOT-QUARTER-086, implemented on dev; QA/release pending; existing sampling test updated for stronger 60-cycle density reference after initial CI failure): Bounded quarter-grid probes reduce paired-root aliasing beyond midpoint sampling, retaining strict residual checks, jump rejection and plateau behavior. Adds diagnostics, source/bundle parity and mandatory responsive Chromium regressions; not globally exhaustive.
- 2026-11-02 (MATH-WLS-RHS-085, released via PR #153): Verified synchronized dev/main b6776a3edc25efd078e54b9fbe07b582078f22e8, green Quality and successful Pages deployment; hosted interaction unverified.

- 2026-11-02 (MATH-WLS-RHS-085, implemented on dev; exact-head QA/release pending): Reused weighted 3×2 QR to report per-observation +1-unit RHS coefficient responses; fixed-design linear sensitivity only, not uncertainty. Adds numerical perturbation and scale-invariance references, source/bundle parity, mandatory responsive Chromium recovery regression.
- 2026-11-02 (MATH-WLS-LEVERAGE-084, released via PR #152): Weighted 3×2 least squares reports per-observation design leverage via the existing QR orthonormal basis; 104/105, 101/105, 1/21 numerical reference, scale invariance, invalid/rank failures, source/bundle parity and mandatory responsive Chromium regression. Leverage is not an outlier probability or coefficient uncertainty.

Recent entries are listed here (newest first). Earlier release notes through 2026-10-29 are kept verbatim in [docs/archive/CHANGELOG_ARCHIVE_2026-10-29.md](docs/archive/CHANGELOG_ARCHIVE_2026-10-29.md). Entries marked *unreleased* or *dev* are not yet confirmed live; see [the living plan](docs/HOURLY_DEVELOPMENT_PLAN.md) for verification evidence.

- 2026-11-02 (MATH-ROOT-MIDPOINT-083, implemented on dev; exact-head CI/release pending): One bounded midpoint probe per coarse scalar-root interval reveals some paired crossings hidden by equal-sign endpoints, with independent half-bracket refinement, strict finite-residual certification, midpoint counts, offline parity and mandatory Chromium paired-root/jump/plateau/mobile regressions. Not globally exhaustive.
- 2026-11-02 (MATH-ROOT-SIGN-082, released via PR #150): Avoid underflow in scalar-root sign-change and bisection decisions by comparing finite residual signs directly; retain strict absolute-residual acceptance and finite-jump rejection. Adds offline parity and mandatory Chromium tiny-scale, invalid and responsive recovery regressions.
- 2026-11-02 (MATH-ROOT-CUSP-081, implemented on dev; CI/release pending): Two-scale secant screening flags possible cusps without conflating smooth tangencies, adds per-root warning metadata, accessible count, source parity and mandatory Chromium regressions. No differentiability certificate.
- 2026-11-02 (MATH-ROOT-ONE-SIDED-080, implemented on dev; CI/release pending): One-sided real-domain secants, per-root method metadata, accessible count, non-certifying guidance, offline parity, and structural/mandatory Chromium reference, negative and responsive regressions.
- 2026-11-02 (MATH-WLS-CONDITION-079, released via PR #147): Weighted 3×2 least squares now reports relative-weight ratio and reusable QR diagonal spread with explicit non-certifying sensitivity guidance. Adds numerical scale/near-rank/extreme-weight tests, standalone parity and mandatory responsive Chromium recovery regression. No claim of statistical uncertainty or full 2-norm conditioning.
- 2026-11-02 (MATH-ROOT-SAMPLING-078, implemented on dev; QA/release pending): Added configurable 20–1600 scalar root sampling intervals, grid spacing and oscillatory/even-root aliasing warnings; accessible invalid/fractional/empty-input recovery, scalar-only UI, source/bundle parity and mandatory Chromium coarse/fine numerical, plateau, jump and mobile tests. No global completeness guarantee.
- 2026-11-02 (MATH-ROOT-BRACKET-077, implemented on dev; QA/release pending): Bisection now refines steep sign-change brackets until actual residual tolerance or floating-point resolution, rather than treating a narrow x-interval as sufficient. Preserves post-rounding residual validation and jump rejection. Adds offline source parity and mandatory Chromium steep/endpoint/smooth/tangent/jump/mobile recovery regression.

- 2026-11-02 (MATH-WLS-GUIDANCE-076, implemented on dev; exact-head QA/release pending): Clarified 3×2 weighted least-squares scope, positive relative weights, common-scale invariance, units and uncertainty limitations in accessible input guidance. Added direct numerical rank/scale/negative tests and mandatory responsive Chromium guidance/recovery regression; offline standalone parity preserved.
- 2026-11-02 (MATH-ROOT-CONDITIONING-075, implemented on dev; exact-head QA/release pending): Scalar roots now expose local secant slope magnitudes as heuristic conditioning guidance, explicitly separate function residual from uncertified root-position error, and announce a minimum finite slope. Added offline parity, flat/steep/smooth/jump/plateau and browser recovery regressions in mandatory Quality.
- 2026-11-01 (ENG-CATALOG-WLS-074, implemented on dev; exact-head QA/release pending): Canonical Engineering route focuses existing real 3×2 QR-based weighted least-squares solver without duplicated math or draft changes. Adds offline parity, 3×2 numerical reference, invalid weights/dimensions, recovery and mandatory keyboard/mobile Chromium regression.
- 2026-11-01 (ENG-CATALOG-EIGEN-073, implemented on dev; exact-head QA/release pending): Symmetric eigenanalysis Engineering route focuses existing Matrix Jacobi solver without duplicate math or draft overwrites; adds 3×3 eigenvalue/residual references, invalid symmetry/empty-input recovery, source/bundle parity and required 390/768/1280 Chromium keyboard tests.
- 2026-11-01 (ENG-CATALOG-SVD-072, implemented on dev; exact-head QA/release pending): Engineering Toolbox now routes to the existing real small-matrix SVD without duplicating numerical kernels or changing drafts. Includes rank-deficient support, explicit threshold-based rank scope, offline parity, focused structural/Chromium keyboard, reference residual and error-recovery regressions, and a mandatory Quality step.
- 2026-11-01 (MATH-ROOT-PLATEAU-071, implemented on dev; CI/release pending): Classifies sampled zero/nonzero scalar residual plateaus instead of reporting hundreds of false discrete roots. Uses two off-grid probes, conservative non-isolation messaging, source/bundle parity, new structural and Chromium regression tests, and a mandatory Quality step. Does not claim global constancy or root completeness.
- 2026-11-01 (UI-ZOOM-MODULE-070, implemented on dev; QA/release pending): Extracted table zoom controller into reusable src/visual-controls.js with offline build parity; the range slider now announces its current percentage through aria-valuetext. Added structural and Chromium keyboard, clamp and responsive regression gates.
- 2026-11-01 (MATH-ROOT-RESIDUAL-069, implemented on dev; CI/release pending): Scalar root search now requires a finite absolute residual at or below requested tolerance after rounding, rejects false roots across small finite jumps, preserves tiny nonzero candidates and reports maximum absolute residual. Added source/bundle structural regression and Chromium smooth/tangential/jump/tiny-root/UI tests; registered required Quality step.

- 2026-11-01 (MATH-ROOT-VALIDATION-068, dev QA pending): Scalar nonlinear roots expose a configurable tolerance (0 < tolerance ≤ 0.01) with focused, announced invalid-field feedback and recovery; nonlinear systems ignore hidden scalar domain fields. Added source parity and reference-root/negative/keyboard Chromium regressions; release not yet verified.

- 2026-11-01 (UI-ENGINEERING-A11Y-067, dev QA pending): Engineering Toolbox search and discipline filters now have 40px minimum touch targets and visible keyboard focus; added responsive 390/768/1280 Chromium live-status/QR-route regression, structural parity guard and required Quality step.

- 2026-11-01 (ENG-CATALOG-QR-066, dev QA pending): Engineering Toolbox adds one canonical QR factorization route to the existing real 2×2/3×2/3×3 Matrix solver, focusing the existing operation without duplicate math. Added structural parity and responsive Chromium numerical/rank/shape/keyboard regressions, mandatory Quality step; production release not yet verified.

- 2026-11-01 (ENG-CATALOG-LU-065, dev QA pending): Engineering Toolbox now links to the existing LU factorization (2×2/3×3 real, scaled pivoting) via one canonical route with focused operation button. Added singular-input/recovery and numerical residual Chromium regression, structural source parity test and required Quality step; no duplicate solver.

- 2026-11-01 (UI-NUMERICAL-A11Y-064, dev QA pending): Numerical Methods controls now use 40px minimum touch targets and live result/error announcements; responsive keyboard/error-recovery Chromium smoke and source parity test added. PR #133 for earlier accessibility slices merged; final production verification pending.
- 2026-11-01 (UI-MATRIX-A11Y-063, dev QA pending): Matrix calculator selectors, buttons and input grids now use 40px minimum touch targets, with responsive keyboard/browser regression and offline source parity coverage.
- 2026-11-01 (UI-GRAPH-A11Y-062, dev QA pending): Graph axes and advanced dataset import controls now have 40px minimum touch targets; added source/bundle parity and responsive Chromium keyboard/accessibility tests, registered in Quality.
- 2026-11-01 (UI-DATA-TOOLBAR-A11Y-061, dev QA pending): Data Tables toolbar buttons, inputs and selects now use 40px minimum touch targets; added structural bundle-parity and desktop/mobile Chromium regression checks. Dense spreadsheet cells remain unchanged.
- 2026-10-31 (UI-A11Y-TARGETS-060, unreleased): Control equilibrium/transient inputs and size select (19–21px) and the Data Tables Code Library category/search fields (19–21px) are now at least 40px tall; accessibility regressions measure all control kinds.
- 2026-10-31 (UI-ODE-A11Y-059, unreleased): ODE panel controls are at least 40px tall on mobile (were 35–37px); added an accessibility regression (names, live output, keyboard run, error announcement, touch targets).
- 2026-10-31 (UI-CONTROL-A11Y-058, unreleased): Control Theory toolbox buttons are at least 40px tall on mobile (four were 28px); added an accessibility audit regression (names, live regions, keyboard disclosures, touch targets).
- 2026-10-31 (ARCH-BUNDLE-PARITY-057, unreleased): Re-synced three stale source modules from the shipped bundle (no change to index.html) so a rebuild can no longer regress features, and added an all-module source/bundle parity and byte-identical rebuild test.
- 2026-10-31 (DOCS-CHANGELOG-ARCHIVE-056, unreleased): Older release notes moved verbatim to docs/archive/CHANGELOG_ARCHIVE_2026-10-29.md; this file keeps the recent entries.
- 2026-10-31 (MATH-ODE-RK4-CONVERGENCE-055, unreleased): Scalar fixed-step RK4 reports a step-doubling endpoint difference (≤500 steps) as a diagnostic, never as a global error bound.
- 2026-10-31 (UI-ENGINEERING-A11Y-054, unreleased): Engineering catalog buttons have unique accessible names (aria-label per tool); keyboard, focus-visibility and 390px target-size regression added.
- 2026-10-31 (SECURITY-PYTHON-SANDBOX-053, unreleased): Structural regression for Python isolation (Worker-only, 60 s timeout, no page/network access, minimal namespace, finite-real results, pinned Pyodide) and a ban on JS eval/new Function in app code.
- 2026-10-31 (DOCS-LINKS-052, unreleased): Unit test fails on any broken relative Markdown link, protecting the docs reorganization.
- 2026-10-31 (DATA-PROJECT-ENGINEERING-FILTER-051, unreleased): Projects save and restore the Engineering Toolbox discipline and search filter; invalid values are refused with rollback and legacy projects import unchanged.
- 2026-10-31 (UI-ENGINEERING-NUMERIC-ROUTES-050, unreleased): Engineering Toolbox lists existing interpolation, adaptive quadrature and golden-section minimization tools as available with real routing and honest scope notes.
- 2026-10-31 (MATH-ODE-SYSTEM-CONVERGENCE-049, unreleased): Coupled two-state RK4 reports a step-doubling endpoint difference (≤500 steps) as a diagnostic, never as a global error bound.
- 2026-10-31 (DATA-GRAPH-ROUNDTRIP-048, unreleased): Chromium regression for Graph dataset export→import identity, mixed cell types, atomic duplicate-header rejection and 390px layout.
- 2026-10-31 (UI-ENGINEERING-NUMERIC-ROUTES-047, unreleased): Engineering Toolbox lists existing symmetric eigen, FFT and Brent root tools as available with real routing and honest scope notes.
- 2026-10-31 (UI-ENGINEERING-CONTROL-ROUTES-046 / MATH-ODE-RK45-NEAR-RESOLUTION-045, unreleased): Engineering Toolbox lists existing Control stability and transient tools as available with real routing; RK45 near-time-resolution reference tests added.
- 2026-10-31 (DATA-PROJECT-TABLE-SELECTION-044, unreleased): Project import rejects a saved Data Tables selection that names no table, preserving column order and mixed cell types; direct and Chromium regressions added.
- 2026-10-30 (DOCS-REORG-037, unreleased): Toolbox feature lists and candidate/backlog catalogs moved to docs/toolboxes/; older hourly plan entries archived under docs/archive/; stale QA report removed; generated toolbox registry git-ignored. Links, AGENTS.md and registry script updated.
- Fixed-step scalar and coupled RK4 now reject unresolvable time grids and collapsed midpoint stages near machine precision instead of silently exporting misleading timestamps; new numerical and Chromium regressions committed on dev (MATH-ODE-RK4-TIME-GRID-043; CI/Pages pending).
- Graph saved-project import rejects blank and case/whitespace-equivalent duplicate dataset headers without modifying valid names, preserving v1/v2 and mixed-cell round trips (dev QA pending).
- RK45 now guards strictly advancing accepted time samples and reports accepted machine-resolution time steps for near-ULP intervals. No global accuracy certification; dev CI pending.
- 2026-10-30 (DATA-GRAPH-HEADER-IDENTITY-040, dev QA): Reject duplicate Graph dataset column headers on project import, preserving valid v1/v2 data and atomic rollback; focused Node and browser regressions. CI/Pages pending.
- Saved-project Data Tables names now reject blanks and whitespace/case-equivalent duplicates without modifying valid display names. Regression tests committed; release QA pending.
- Saved-project Matrix draft validation rejects overflowed scientific notation and values exceeding the 1e12 solver bound in A/B/RHS/weights, while preserving v1/v2 and empty drafts (DATA-PROJECT-MATRIX-FINITE-038; dev QA pending).
- RK45 now distinguishes recoverable bounded intermediate-stage overflow using explicit error tags instead of message text, reports the last affected stage, and rejects nonfinite derivative/domain failures without unsafe retries (dev QA pending).
- 2026-10-30 (CONTROL-TRANSIENT-PLOT-036, dev QA): Control two-state RK4 trajectory now has a contextual Graphs action plotting both x1(t) and x2(t) through the existing Data Tables/Graph Data pipeline; adds Node contract and Chromium/mobile/keyboard regressions. Full CI and deployment pending.
- 2026-10-30 (MATH-ODE-RK45-OVERFLOW-035, dev QA): Adaptive RK45 now retries bounded intermediate-stage overflow with halved step, counts/report retries, preserves k1 hard failures and attempt/time-resolution bounds. Added Node numerical and mandatory Chromium/mobile regression; full CI and release pending.
- Control transient RK4 now reports optional step-doubling endpoint difference for up to 500 base steps, retaining original export and honest non-certified accuracy warning (dev QA pending).
- 2026-10-30 (CONTROL-TRANSIENT-TWO-STATE-033, dev QA): Added two-state Control transient trajectory for xdot=-Ax+b using existing coupled RK4, including forward/backward and singular-A references, strict numeric inputs, stale-export invalidation, Data Tables export and responsive UI. Added direct numerical test and mandatory Chromium regression. Release pending.
- 2026-10-30 (CI-ENGINEERING-SEARCH-REPAIR-034, dev QA): Corrected stale structural search assertion after all-term matching; [Quality 41083127664](https://github.com/saeedsai/ProMathStudio/actions/runs/41083127664) failed solely on obsolete `includes(q)` expectation. Retained all-term matching and added browser positive/negative regression. Exact new-head CI pending.
- Engineering Toolbox: search now matches multiple keywords in any order, preserving planned tool labels and offline support (UI-ENGINEERING-MULTIWORD-032; dev QA pending).
- 2026-10-30 (UI-ENGINEERING-SEARCH-031, dev QA): Engineering Toolbox search includes readable discipline display names, retaining canonical IDs, truthful planned status, offline parity, and browser/mobile navigation checks. Exact-head CI and deployment pending.
- 2026-10-30 (MATH-ODE-RK45-WORKLOAD-030, dev QA): Adaptive scalar RK45 reports longest consecutive rejected-step streak and warns on repeated rejections without claiming stiffness; adds exponential forward/backward numerical tests and mandatory Chromium mobile/error-recovery coverage. Exact-head CI and release pending.
- 2026-10-30 (UI-ENGINEERING-CATALOG-029, dev QA): Added Control Theory, GNSS Positioning and Signal Engineering to searchable Engineering Toolbox; truthful planned cards without fake actions, shared existing Control equilibrium route, source/bundle and Chromium regressions. Exact-head CI/PR/Pages pending.
- 2026-10-30 (ARCH-ENGINEERING-SHAPE-CODES-028, dev QA): Canonical solver registry rejects invalid 2x2/3x3 A dimensions and b vector sizes with structured INVALID_MATRIX_SHAPE / INVALID_VECTOR_LENGTH errors; added reference and recovery tests, standalone parity, exact release checks pending.
- 2026-10-30 (CONTROL-STABILITY-SYMMETRIC-027, dev QA): Added symmetric 2×2/3×3 Control perturbation stability action reusing Matrix Jacobi eigenanalysis, stable/unstable/marginal/near-zero-indeterminate classification, eigen residual and explicit equilibrium/nonsymmetric limitations. Added numerical and desktop/mobile browser regressions; exact-head CI/PR/Pages pending.
- 2026-10-30 (ARCH-ENGINEERING-CONTRACTS-026, dev QA): Canonical Matrix/Control solver registry now exposes immutable bounded input schemas, explicit physical-unit/full-rank assumptions and a nonthrowing structured execution result with stable registry error codes. Preserves existing throwing API and standalone bundle. New Node/Python numerical, negative and parity test plus extended Chromium browser regression; exact-head release verification pending.
- 2026-10-30 (UI-MATRIX-PROJECT-ROUNDTRIP-025, dev QA): Matrix calculator project backups now preserve A/B dimensions, cell drafts, right-hand side and weights; restore validates shape and bounded decimal strings, preserves keyboard focus, clears stale results, and supports older projects without Matrix state. Added schema and mandatory Chromium round-trip/mobile/rollback regression. Exact-head Quality and Pages release pending.
- 2026-10-30 (DATA-PROJECT-TABLE-FINITE-024, dev QA): Refuse nonfinite Data Table numeric cells on project import, including overflowing JSON number literals; preserve valid scalar cells, legacy migration and atomic rollback. Added Node/Python and Chromium regression coverage; exact CI/PR/Pages pending.
- 2026-10-30 (DATA-PROJECT-GRAPH-CELLS-023, dev QA): Reject nested object/array and nonfinite numeric cells in imported graph datasets; retain bounded valid scalar cells and v1 project migration. Added Node/Python regression with standalone parity. Exact-head CI, PR and Pages release pending.
- 2026-10-30 (MATH-ODE-RK45-STAGE-RESOLUTION-022, dev QA candidate): Warn when RK45 intermediate stage times collapse to current representable time at large epochs; count affected attempts/accepted steps, include failure context, preserve integration and exports. Added forward/backward one-ULP numerical and Chromium/mobile recovery regressions. Exact CI/PR/Pages pending.
- 2026-10-30 (UI-ENGINEERING-CATALOG-021, dev QA candidate): Added fifth Engineering Toolbox workspace with six discipline filters, searchable canonical entries, truthful available/planned labels and navigation to existing Matrix, Control and ODE tools without duplicate solvers or fake planned actions. Preserved offline bundle, original four workspaces and drafts; added source/bundle, keyboard, routing, search and mobile regressions. Exact dev CI/PR/main/Pages pending.
- 2026-10-30 (ARCH-CONTROL-EQUILIBRIUM-020, dev QA): Bounded Control equilibrium xdot=-Ax+b reuses canonical Matrix solver for 2×2/3×3, with residual diagnostics, stability/unit caveats, stale-result invalidation and responsive UI. New Node/Python and mandatory Chromium regression; exact-head CI/PR/Pages pending.
- 2026-10-30 (ARCH-ENGINEERING-SOLVER-REGISTRY-019, dev QA candidate): Added stable immutable runtime solver IDs for Matrix Ax=b and Inverse with strict input contract and metadata validation; both real UI buttons execute through the shared registry and existing scaled-pivot kernels. Added numerical, duplicate-ID, invalid/singular, standalone-parity and mandatory Chromium/mobile regressions. Cross-discipline toolbox UI is still planned; exact-head CI/PR/main/Pages pending.
- 2026-10-30 (UI-MATRIX-RESIZE-FOCUS-018, dev QA candidate): Preserve numeric-cell focus across Matrix A/B/RHS/weight grid rebuilds and clamp focus when dimensions shrink, without stealing focus from dimension selectors or altering surviving values. Added Node target/boundary and mandatory Chromium desktop/mobile regressions, standalone parity, and living roadmap update. Exact-head CI/PR/main/Pages pending.
- 2026-10-30 (UI-MATRIX-HOME-END-017, dev QA candidate): Added Home/End row-local and Ctrl+Home/End first/last-cell navigation across Matrix A/B/RHS/weight numeric grids. Matrix A labels now include matrix name. Preserved numeric values, arrows, Tab, all algorithms, transfer and offline bundle; added direct Node negative/target and mandatory Chromium mobile tests. Exact-head CI/PR/main/Pages pending.
- 2026-10-30 (UI-MATRIX-GRID-KEYBOARD-016, dev QA candidate): Added unmodified arrow-key focus movement in Matrix A/B/RHS/weight numeric grids, including 2×2/3×3 and single-column boundaries without accidentally stepping number values. Preserved Tab/modified shortcuts, input drafts, numerical algorithms, Equation Editor transfer and offline parity. Added Node target/boundary and mandatory Chromium keyboard/mobile regressions. Exact-head CI/PR/main/Pages verification pending.
- 2026-10-30 (UI-MATRIX-INPUT-GROUPS-015, dev QA candidate): Added collapsible Matrix B/RHS/weight sections, labeled Matrix A and operation-aware reopening without deleting input drafts. Preserved 16 actions and Equation Editor transfer; new structural, numerical, standalone and Chromium regression. Exact-head CI and promotion pending.
- 2026-10-30 (UI-MATRIX-CONTEXT-014, dev QA candidate): Split Matrix operation buttons from contextual Equation Editor result-transfer actions; show only the relevant LU/QR/Eigen/SVD selector for a successful calculation, hide all on edit/error, preserve 16 operations, factor choices and transfer. Added structural/parity and mandatory Chromium keyboard/mobile/transfer/error regression. Exact-head CI/PR/main/Pages pending.
- 2026-10-30 (MATH-MATRIX-CONDITION-GUIDANCE-013, dev QA candidate): Added heuristic κ∞ ≥ 1e8 numerical sensitivity guidance to 2×2/3×3 Ax=b and Inverse, explicitly distinguishing conditioning from residual and backward error. Reuses existing scaled-pivot solver; preserves singular recovery, editor transfer and offline parity. Added Node numerical/threshold/negative regression and mandatory Chromium two-consumer/mobile regression. Exact dev CI, PR, main Quality and Pages pending.
- 2026-10-30 (MATH-ODE-RK45-REJECTION-012, dev QA candidate): Added maximum rejected normalized local-error ratio, minimum rejected |Δt| and representable-time adjustment count to scalar RK45 diagnostics, including attempt-limit/underflow messages. Preserved adaptive acceptance logic, derivative guards, stale-export invalidation and offline standalone parity. Added Node stiff/nonstiff/reference/one-ULP/negative test `tests/test_ode_rk45_rejected_quality.py`, mandatory Chromium success/failure/recovery/mobile test `tests/smoke_ode_rk45_rejected_quality.py`, and numerical documentation. Local full checkout blocked by GitHub DNS; exact dev CI, PR/main Quality and Pages verification pending. The local-error ratio is not a global error guarantee.
- 2026-10-30 (MATH-ODE-RK45-STEP-QUALITY-011, dev QA candidate): Added minimum/maximum accepted absolute time-step and maximum accepted normalized embedded local-error ratio to scalar forward/backward RK45 output and UI, using actual rounded accepted steps (not rejected trials). Preserved existing local error acceptance, endpoint handling, stale export invalidation and offline standalone parity. Added Node numerical/reference/one-ULP/negative regression `tests/test_ode_rk45_step_quality.py`, mandatory Chromium success/failure/recovery/mobile regression `tests/smoke_ode_rk45_step_quality.py`, and updated numerical documentation. The ratio is an estimate, not a global error bound. Exact dev CI, PR, main Quality and Pages pending.
- 2026-10-30 (MATH-MATRIX-CONDITION-INF-010, dev QA candidate): Added infinity-norm condition number κ∞(A)=||A||∞·||A⁻¹||∞ to 2×2/3×3 Matrix Solve Ax=b and Inverse, reusing the existing scaled-pivot inverse. This is distinct from backward error and is not a forward-error guarantee. Valid solves retain editor transfer if the diagnostic is unavailable; singular and invalid input behavior unchanged. Added Node numerical/negative/scale/parity regression `tests/test_matrix_condition_infinity.py` and mandatory Chromium two-consumer/mobile/error-recovery regression `tests/smoke_matrix_condition_infinity.py`. Source and standalone HTML synchronized. Preserved the full legacy `M.matrixTools` export after structural CI failures; new API is added by a separate assignment without weakening existing compatibility tests. Exact-head CI, PR, main and Pages pending.
- 2026-10-30 (MATH-MATRIX-SHARED-INVERSE-008, dev QA candidate): Reused the existing scaled-partial-pivot Ax=b numerical solver for 2×2/3×3 matrix inversion by solving against identity columns, removing duplicate Gauss–Jordan elimination. Retained inverse residual and singular checks, no input mutation, UI/Equation transfer and offline standalone parity. Added Node reference/scaled/singular regression `tests/test_matrix_shared_solve_inverse.py`, registered Chromium scaled inverse, error recovery and 390px mobile smoke `tests/smoke_matrix_shared_solve_inverse.py`. Direct V8 numerical/negative smoke passed; exact-head CI/PR/main/Pages pending.
- 2026-10-29 (MATH-MATRIX-STRICT-TYPES-007, dev QA candidate): Rejected coercible nonprimitive matrix and Ax=b RHS inputs (arrays, objects, boxed numbers, BigInts, symbols, booleans) before Number() conversion; preserved valid decimal/scientific inputs, finite magnitude bounds and scaled partial-pivot solve. Added direct 2×2/3×3 reference, negative, singular/inconsistent and standalone bundle parity regression `tests/test_matrix_strict_types.py`; source and standalone synchronized. Exact-head CI, dev→main PR, main and Pages release pending.
- 2026-10-29 (MATH-ODE-RK45-PROGRESS-006, dev QA candidate): Added RK45 attempt-exhaustion and floating-time-resolution failure diagnostics with last time, target, attempted step, attempts, accepted/rejected counts and tolerance. Retained the Dormand–Prince algorithm, forward/backward behavior and stale-export invalidation. Added Node reference/boundary regression and Chromium failure/recovery regression; synchronized standalone HTML. Exact-head CI/PR/Pages pending.
- 2026-10-29 (MATH-ODE-RK45-DIAG-005, dev QA candidate): Added stage-aware scalar RK45 derivative failure diagnostics (k1–k7, time, state), preserving bounded numerical behavior and stale table/graph export invalidation. Added Node reference/invalid/overflow and Chromium recovery/mobile regressions to mandatory Quality. Source and standalone bundle synchronized; exact-head CI, PR, main and Pages pending.
- 2026-10-29 (MATH-MATRIX-WLS-RHS-002, dev QA candidate): Hardened both QR least-squares operations to accept only finite decimal/scientific RHS values (numbers or strings), rejecting Number()-coerced hexadecimal/binary/octal literals, arrays and objects. Weighted fitting now rejects array/object weight coercion. Added focused numerical regression with 51 assertions covering reference coefficients, weighted SSE, malformed input, positive weight bounds, 1e-9/1e9 scaling and near-rank loss. Updated standalone HTML; exact-head CI, PR and Pages require verification.
- 2026-10-29 (release checkpoint): Weighted 3×2 least-squares UI and prior dev changes merged through PR #95 to main at 352c1dd8549beb8cb0707012b7bd466d1fcd25c1; dev/main Quality and Pages runs succeeded. Independent live-browser confirmation was not available.
- 2026-10-29 (dev QA candidate, MATH-MATRIX-WLS-UI-001): Exposed bounded 3×2 QR weighted least squares in the Matrix calculator with three editable relative observation weights, weighted residual diagnostics and Equation Editor transfer. Preserved unweighted least squares, added Chromium reference/invalid-input/mobile regression and CI gate; exact-head CI, PR and Pages release require verification.\n- 2026-10-29 (dev QA candidate): Fixed scalar adaptive RK45 false step underflow at large time epochs and early endpoint snapping. RK45 now uses representable time increments and the actual rounded step, preserves forward/backward integration, and rejects impossible time-resolution tolerances explicitly. Added numerical/reference/static and Chromium UI/table/mobile regressions; exact-head CI/Pages pending.
- 2026-10-29 (dev QA candidate): Backward-time coupled two-state RK4, reverse oscillator and nonautonomous references, UI/table/graph regression, signed steps and forward compatibility; exact-head CI and release pending.
- 2026-10-29 (dev candidate; QA pending): Added signed-direction backward adaptive Dormand–Prince RK45 for scalar IVPs, preserving forward behavior, local-error rejection and ordered Data Tables/Graphs export. Added reverse exponential/nonautonomous reference, refinement/rejection, invalid-input and browser UI/mobile regression; coupled RK4 remains forward-only. No dependencies added.
- 2026-10-29 (dev candidate, CI/Pages pending): Enabled backward-time scalar fixed-step RK4 integration with signed step sizes, analytic reference/convergence tests, invalid-input checks, UI and Data Tables export. Adaptive RK45 and coupled RK4 remain forward-only; no new runtime dependencies.\n- 2026-10-29 (dev, full CI pending): Improved the Control Theory root-locus graph from unconnected sampled pole markers to continuous *sampled* branch trajectories using minimum-total-displacement pole assignment. Added guarded root-locus inputs, second/third-order reference checks, cancellation and invalid-input regressions, and a canvas path test (`tests/test_root_locus_tracking.py`). Near repeated poles and crossings remain approximate; no production deployment claimed.
- 2026-10-29 (dev, CI pending): Added mandatory Chromium Control Theory workbench regression covering Bode, Nyquist, root locus, Routh–Hurwitz, unity feedback, validation and responsive layout; integrated it into Quality workflow. This is a test/QA improvement, not a new controller algorithm. Deployment unverified.
- 2026-10-29 (dev, QA pending): Repaired 390px mobile workspace navigation overflow caused by unwrapped horizontal tabs in the computation-first redesign. The four workspace tabs now form a two-column responsive grid while preserving keyboard focus/activation. Added `tests/test_mobile_workspace_grid.py`; exact-head browser/Quality and production deployment remain unverified.
- 2026-10-29 (dev, pending exact-head CI): Repaired the app-startup JavaScript parsing regression caused by graph scripts inserted into the HTML-export literal; all inline executable scripts now parse. Added inline-script Node syntax regression and corrected sampled root-locus results to render as discrete points instead of false continuous branches. Production deployment unverified.
- 2026-10-29 (dev / CI pending): Added bounded continuous-time control analysis in Graphs with polynomial SISO transfer-function inputs, sampled Bode/Nyquist/root locus plots, Routh–Hurwitz table, and unity negative feedback. Structural regression added. Controller tuning, feedforward design and symbolic Laplace integration remain planned; release unverified.
- 2026-10-29 (dev, CI pending): Added a dedicated complex-number Graph workbench with 2D Argand plots and sampled 3D |f(z)| magnitude surfaces, presets z, z², inverse and exp, finite-input validation, accessible status and responsive canvas. Preserved existing real graph workflows. Structural regression added; deployment not yet confirmed.
- 2026-10-29 (dev, pending CI): Refreshed the entire interface with an original computational math-first design: stronger input/result hierarchy, teal navigation, palette/sidebar, consistent panels, focus visibility, mobile and reduced-motion refinements; added structural UI regression coverage. Deployment not yet verified.

- 2026-11-04: Corrected stale control-frequency-response status assertion in thermo/circuit browser smoke (implemented tool is available); exact-head CI recheck pending. No application feature or release claimed.
- 2026-11-21 (dev, exact-head QA pending): Fixed Truss Studio results CSV export to terminate the final record with CRLF, matching the existing material-schedule CSV contract. Strengthened Chromium coverage to assert one CRLF per parsed record and reject bare CR/LF. No numeric, quoting or FEM behavior changed.
- 2026-11-22 (dev, exact-head QA pending): Made Truss Studio SVG downloads self-describing and accessible with a native title/description, image role and aria-labelledby references while preserving the viewBox and solved plot. Chromium regression now parses the generated SVG Blob and checks XML validity, namespace, dimensions, accessible-name references, background and solved geometry.

- 2026-11-23 (dev, exact-head QA pending): Stabilized hollow-circle section properties for thin annulus walls using factored diameter-gap expressions instead of cancellation-prone squared/fourth-power subtraction. Added independent high-precision Node references and real Chromium preview/application regression at 1280px and 390px, including selected-member isolation and E/density/K preservation.


## 2026-11-25

- Data Tables: added explicit accessible names to the five native action-menu triggers (Table, Filter, Combine, Files, Python). Corrected the registered sheet-rename browser regression to open the collapsed Table actions menu through its accessible role/name before exercising rollback and recovery. No workbook calculation or persistence behavior changed; exact-head Quality pending.

- Data Tables follow-up: synchronized the new accessible action-menu names in `src/numerical-data.js` with the standalone `index.html` after exact-head structural CI exposed a source/bundle parity mismatch. The browser regression remains enabled; no checks were weakened.

- 2026-11-26 (dev, exact-head QA pending): Truss FEM numeric-string parsing now accepts only trimmed decimal/scientific syntax instead of JavaScript radix coercion. Hexadecimal, binary and octal strings reject consistently in model parsing, solve and section dimensions; finite numeric values and ordinary decimal/scientific strings remain compatible. Added Node and Chromium desktop/mobile regressions; no standalone bundle change because Truss FEM is an adjacent script.


## 2026-11-26

- Saved Graph project validation: primary and overlay axis selectors now require bounded base-10 integer strings or safe integer numbers. Rejects radix-prefixed, exponent-form, fractional, negative and overlong raw string indices instead of relying on JavaScript `Number()` coercion. Preserves omitted legacy selectors, bounded whitespace/plus decimal strings, dormant 2D Z mappings and project version 2. Added Node structural and Chromium atomic-import rollback regressions; synchronized `src/project-schema.js` into standalone `index.html`. Implemented on dev; exact-head Quality and release pending.
