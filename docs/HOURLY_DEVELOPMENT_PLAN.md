## 2026-11-03 — Parallel batch 142–149 (polynomials, nonlinear fit, filters, vector calculus, matrix extras, multivariate, vector fields, thermo cycles + DC circuits)

**Release checkpoint:** PR #188 into dev at 2c60767; release PR #189 to main is waiting on exact-head Quality.

**Implemented on branch (QA pending):** eight agents worked on disjoint modules, and all integrated without source conflicts. `thermal.cycle.analysis` and `circuits.network.analysis` move from planned to available under their narrowed scopes; `fluids.pipe.network`, `electronics.digital.logic`, `control.frequency.response` and `gnss.positioning.least.squares` stay planned. The frozen baseline is unchanged.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Release batches 135–149 (pending):** exact-head Quality, PRs to main, main Quality and Pages.
2. **P1 Pipe network (planned):** Hardy-Cross or Newton loop solver with Darcy–Weisbach/Colebrook; references from textbook loop networks.
3. **P1 Digital logic simulation (planned):** gate netlists with truth tables and an animated timing diagram.
4. **P1 Tool search favourites and recents (planned):** kept per viewer in try/catch localStorage.
5. **P2 Offline symbolic gaps (blocked by CDN):** define an offline scope for nonlinear symbolic systems and series.

## 2026-11-03 — Parallel batch 135–141 (hypothesis tests, curve overlays, simulation units, BVP shooting, uncertainty, splines, tool search)

**Release checkpoint:** PR #186 into dev at 657503c, then PR #187 to main at 70fc483. Main Quality 41730966059 and Pages 41730962844 succeeded.

**Implemented on branch (QA pending):**
- **Features:** six parallel features plus a global "Find a tool" search, built at the user's request for a modular, easy-to-find UI.
- **Integration:** branches were merged and append-only workflow conflicts resolved. Four agent tests that required their own CI step to be last now check that it is present. Locally, 388 structural tests pass.
- **Correction:** the statistics agent corrected two of the integrator's reference values against scipy/mpmath: the one-sample t p-value is 0.0574563 and the Welch p-value is 0.1075312.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Release batch 135–141 (pending):** exact-head Quality, PR to main, main Quality and Pages.
2. **P1 Wave 3 integration (in progress, parallel agents):**
   - polynomial roots;
   - Levenberg–Marquardt fitting;
   - digital filters;
   - vector calculus;
   - Cholesky and null space;
   - PCA and k-means;
   - vector and slope fields;
   - thermodynamic cycles and DC circuits.
3. **P1 Tool search ranking feedback (planned):** recent tools and pinned favourites in the search, kept per viewer in try/catch localStorage.
4. **P2 Symbolic CAS gaps (blocked offline):** nonlinear symbolic systems and series need the SymPy CDN; plan an offline fallback scope.
5. **P2 Docs (planned):** a user guide page listing every tool with an example input.

## 2026-11-03 — Parallel batch: statistics, curves, optimization, units, multiple integrals, stiff ODE (129–134) + ENG-SIM-EXT-126, Brent pole guard 127, QR pivot 128

**Releases since last entry:** PR #185 merged to main afd41a9 (simulations), with main Quality 41725388344 and Pages 41725387197 both successful.

**Implemented on branch (QA pending):**
- **Completed queue items:** forced vibration, beam combined loads and overhang, simulation Data Tables/Graph/PNG export, Control Theory module extraction, Brent pole/jump refusal and QR pivoting screen.
- **Parallel agents:** six agents produced independent modules for these baseline gaps:
  - probability distributions and descriptive statistics;
  - implicit, parametric and polar curves;
  - linear programming and Nelder–Mead;
  - units and dimensional analysis;
  - double/triple integrals and discrete-data integration;
  - stiff ODE (TR-BDF2).
- **Integration:** each module came with its own src file, unittest and smoke test; the integrator added the bundle slots and workflow steps.
- **Status:** the frozen baseline is unchanged; these features are partial at their stated scope until released.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Release this batch (pending):** exact-head Quality, ordinary PR to main, main Quality and Pages.
2. **P1 Hypothesis tests and confidence intervals (planned):** t/χ²/proportion tests on Data Tables columns, reusing `MathStudio.statistics`; scipy-reference p-values.
3. **P1 Polar/parametric overlay on the main 2D graph (planned):** route `graphCurves` points into the existing graph renderer; round-trip project save.
4. **P1 Units in Engineering simulations (planned):** accept unit-suffixed inputs via `MathStudio.units`; dimension mismatch errors.
5. **P1 Boundary-value ODE by shooting (planned):** reuse the RK4/TR-BDF2 solvers with Brent on the shooting parameter; analytic BVP references.
## 2026-11-03 — BUILD-INDEX-UTF8-126 (dev checkpoint; exact-head QA pending)

**Change:** Standalone HTML builder now identifies an invalid UTF-8 `index.html` input with an explicit path-specific diagnostic. A focused isolated subprocess regression writes invalid bytes and verifies that the original HTML is preserved byte-for-byte. No bundled runtime change.

**Execution ledger:** Inspected root AGENTS, frozen inventory, living plan, dev/main and latest CI/PR/Pages. PR #185 merged engineering simulations into main `afd41a93a1fdd154f120a8380951114f0fe200f2`. Exact-head dev Quality `41724175334` passed for `9a05fcb`; Pages `41725387197` passed for main; main Quality `41725388344` was in progress at inspection. Fast-forwarded dev from `9a05fcb` to main without force. Local checkout failed DNS resolution; local unit/Chromium not executed. New exact-head CI required before release. Historical frozen 166 gaps / 95 partial unchanged.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Exact-head BUILD-INDEX-UTF8 QA and safe release (pending):** Python structural and Chromium Quality green on exact dev and PR heads, ordinary PR with applicable review/protection checks, then main Quality and Pages confirmed.
2. **P1 Simulation-to-Data/Graphs transfer (planned):** time series exported through existing transfer bridge with stable column names; browser round-trip and malformed-data negative tests.
3. **P1 Forced vibration/resonance sweep (planned):** reuse RK4; verify steady-state amplitude ratio `1/sqrt((1-r²)²+(2ζr)²)` at multiple damping/frequency cases.
4. **P1 Beam multiple loads/overhang (planned):** equilibrium and independent superposition references; preserve stated linear-elastic scope.
5. **P1 Control Theory controller extraction (planned):** byte-identical standalone rebuild; existing control numerical/browser, keyboard and saved-project regressions green.

## 2026-11-03 — Engineering simulations with animation (ENG-SIMULATIONS-125; user request)

**Release checkpoint:** ENG-VISUALS-124 released via PR #183 at main eb62023; main Quality 41717592998 and Pages 41717592382 succeeded.

**Implemented on branch (QA pending):** The user clarified that "engineering animation" means engineering simulation with relevant animation. Added `src/engineering-simulations.js` with five physics simulations: beam, orbit, series RLC, projectile with drag, and rod conduction. Each states its assumptions and uses SI units. The simulations reuse the existing RK4 and FTCS solvers where they apply; a small native vector RK4 handles the four-state projectile. `structures.beam.deflection` and `aerospace.orbit.propagation` move from planned to available under their narrowed published scope; three new catalog tools were added. Tests: `tests/test_engineering_simulations.py`, `tests/smoke_engineering_simulations.py`.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Release ENG-SIMULATIONS-125 (pending):** exact-head Quality, ordinary PR to main, main Quality and Pages success.
2. **P1 Simulation export (planned):** send simulation time series to Data Tables and Graphs through the existing transfer bridge; round-trip and column-identity tests.
3. **P1 Forced vibration and resonance sweep (planned):** harmonic forcing on the existing RK4 system; amplitude-ratio reference 1/√((1−r²)²+(2ζr)²).
4. **P1 Beam: overhang and multiple loads by superposition (planned):** superposition references and equilibrium checks; no design-code claims.
5. **P1 Control Theory controller extraction (planned):** byte-identical rebuild; control smokes green.

## 2026-11-03 — BUILD-UTF8-DIAGNOSTIC-125 (dev checkpoint; exact-head CI pending)

**Change:** The standalone builder now identifies the offending module path when its bytes cannot be decoded as UTF-8. The focused subprocess regression writes a malformed source file, checks the diagnostic, and asserts the original standalone HTML is unchanged. No generated bundle or JavaScript runtime behavior changes. Exact-head Quality, PR review and main/Pages release remain unverified for this checkpoint.

**Execution ledger:** PR #180 merged at b3313657; main advanced to eb62023d93fb90241043576193af94d14c0a49a8 while dev was 3acae09e028b741a62bd73ac20ec7477d8191e5b. Fast-forwarded dev to main without force before editing. Local Python/Chromium tests unavailable in connector-only execution; CI must validate the new commit. Historical 166 gaps / 95 partial features unchanged.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Exact-head BUILD-UTF8 QA and safe release:** all structural and Chromium Quality checks pass on the exact dev and PR heads; merge only after reviews/protections, then verify main Quality and Pages.
2. **P1 Animation PNG export:** one contextual frame-export action, deterministic canvas PNG content and offline/keyboard/390px browser checks.
3. **P1 Control Theory controller extraction:** byte-identical standalone rebuild, control numerical/browser regressions and project round-trip.
4. **P1 Scalar-root pole-aware Brent handoff:** refuse possible pole brackets with explicit diagnostics and smooth-root controls.
5. **P1 QR column-pivoting screen:** permutation-invariant near-rank 3×2/3×3 references, documented tolerances.

## 2026-11-03 — Engineering animations (ENG-VISUALS-124; user request)

**Release checkpoint:** PR #181 (branch → dev) merged at 4cc0b1c; exact-head dev Quality 41712593561 and PR #180 Quality 41712600427 passed; PR #180 merged to main b3313657; Pages build 41713837001 succeeded.

**Implemented on branch (QA pending):** User asked for graphics and engineering animations for different tools and equations. Added `src/engineering-visuals.js` with six animated visuals built on existing canonical solvers (RK4 system, FFT, safe evaluator, adaptive Simpson, symmetric eigen). There are no new math kernels and no duplicate action buttons on catalog cards. Reduced motion, keyboard and mobile are covered. Tests: `tests/test_engineering_visuals.py`, `tests/smoke_engineering_visuals.py` (registered in Quality). Planned catalog tools (beam deflection, orbit, circuits) stay planned: no animation claims a new solver.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Release ENG-VISUALS-124 (pending):** exact-head Quality, ordinary PR to main, main Quality and Pages success.
2. **P1 Animation export (planned):** download the current frame as PNG from the canvas; deterministic frame test, no network.
3. **P1 Control Theory controller extraction (planned):** move inline `promath-control-theory` script to `src/control-theory.js`; byte-identical rebuild; control smokes green.
4. **P1 Scalar-root pole-aware Brent handoff (planned):** Brent refuses brackets classified as possible poles; tan(x) near π/2 and 1/(x−c) references.
5. **P1 QR column pivoting screen (planned):** pivot order reported for near-dependent 3×2/3×3 inputs; permutation-invariance references.

## 2026-11-03 — Plan NEXT FIVE completion batch (MATH-ROOT-DISCONTINUITY-120, MATH-QR-RANK-BOUNDARY-121, DATA-PROJECT-ATOMIC-122, ARCH-COMPLEX-GRAPH-MODULE-123)

**Ledger (implemented on session branch `claude/sharp-babbage-pqhvgr`, based on `dev` 579f7a1; exact-head CI pending):**
- **Done on branch — P0 QR rank-boundary references (MATH-QR-RANK-BOUNDARY-121):** `qr()` exposes `minIndependenceRatio`, `rankMargin` and near-threshold guidance in Calculator output. `tests/test_matrix_qr_rank_boundary.py` uses exact binary64 analytic references (c2=(1+e)c1+e(-1,0,1)) accepting e=2^-33/2^-36/2^-39, rejecting 2^-40/2^-45/singular/zero-column, plus orthogonal-complement (residual δ√6) and in-range (Δx2=δ/e) RHS perturbations with eps/ratio-scaled tolerances.
- **Done on branch — P1 Scalar-root discontinuity (MATH-ROOT-DISCONTINUITY-120):** bounded (≤20) rejected sign-change locations, pole/jump heuristic classification, nonfinite grid-sample screening, under-resolved oscillation interval counts and `rootStatus`. `tests/smoke_scalar_root_discontinuity.py` (1/(x-0.3), 1/x, tan x, step jumps, 1600-sample tan x on [-100,100], sin(1/x), smooth controls, 390/768/1280 UI recovery) plus structural test.
- **Done on branch — P1 Matrix/Data atomic import (DATA-PROJECT-ATOMIC-122):** stricter saved custom-function schema (duplicates, argument-less, non-distinct, type/source) and `tests/smoke_project_atomic_import.py` asserting full snapshots after 14 malformed v1/v2 fixtures and injected late-module failures; legacy v1 and v2 round trip still import. Node schema test added.
- **Done on branch — P1 UI controller extraction (ARCH-COMPLEX-GRAPH-MODULE-123):** Complex Graph controller moved to `src/complex-graph.js`; rebuild byte-identical (0-byte bundle delta). `tests/smoke_complex_graph_module.py` covers references, keyboard, mobile, recovery and project round trip.
- **Local evidence:** 308 structural tests OK; new and affected browser smokes (all scalar-root, QR, project schema/selection, Matrix project, Data Tables) pass with local Chromium. `smoke_project_schema.py` failed once then passed 4/4 reruns; treat as possible flake to watch in CI.
- **P0 release of dev head 579f7a1 + this batch (pending):** requires exact-head Quality, an ordinary PR to `main`, main Quality and Pages verification.

**NEXT FIVE (status / acceptance tests):**
1. **P0 Release this batch (pending):** exact-head Quality green for the candidate, ordinary PR merge to `main`, main Quality and Pages success, hosted page loads.
2. **P1 Control Theory controller extraction (planned):** move inline `promath-control-theory` script to `src/control-theory.js`; byte-identical rebuild, existing control smokes green, keyboard/mobile and project round trip.
3. **P1 Scalar-root pole-aware Brent handoff (planned):** Brent refinement refuses brackets classified as possible poles with explicit diagnostic; references for tan(x) near π/2 and 1/(x-c).
4. **P1 QR column pivoting screen (planned):** report pivoted column order for 3×2/3×3 near-dependent inputs; references with permuted columns give identical rank margin.
5. **P2 smoke_project_schema flake investigation (planned):** reproduce the one-off failure with repeated runs; fix wait condition without weakening assertions.

**Execution ledger:** Read AGENTS, plan, dev/main heads (dev 579f7a1 ahead of main ac32882 by 2 commits; PR #179 already merged). Session harness required branch `claude/sharp-babbage-pqhvgr` instead of committing directly to `dev`; noted as deviation from the two-branch policy. Frozen 166 gaps/95 partials unchanged. No force-push, bypass or deletion.

## 2026-11-03 — BUILD-HTML-CLOSER-119 (dev; exact-head QA pending)

**Change:** Reject HTML comment closing delimiters (`-->`) in inline module sources as well as opening delimiters, before rewriting standalone HTML. Direct subprocess regression checks a closing delimiter embedded in JavaScript and original HTML preservation. PR #179 was merged normally at ac3288250bee65c8f22230234f2699b6bb3bbde1 after exact-head push Quality 41698544956 and PR Quality 41698553402 succeeded at b48e800. New dev commit requires its own Quality run; local clone blocked by GitHub DNS.

**NEXT FIVE (status / acceptance tests):**
1. **P0 BUILD-HTML-CLOSER-119 QA/release (pending):** exact-head dev and PR Quality including structural/browser green; ordinary dev-to-main PR only after applicable gates; verify main Quality and Pages.
2. **P0 QR rank-boundary references (planned):** high-precision near-threshold matrices, perturbed RHS, singular rejection with deterministic tolerances.
3. **P1 UI controller extraction (planned):** offline source/bundle parity, keyboard/mobile smoke, project round-trip and bundle size delta.
4. **P1 Scalar-root discontinuity (planned):** pole and oscillatory negative fixtures, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed project fixture preserves state and v1/v2 compatibility.

**Execution ledger:** Inspected AGENTS, living plan, frozen inventory, exact dev/main heads, PR #179 reviews, rulesets and CI. Merged PR #179 through ordinary GitHub merge and fast-forwarded dev non-force. Added comment-closer guard, negative regression, changelog and plan. Local git clone unavailable (DNS); new exact-head CI and Pages pending. Frozen 166 gaps / 95 partials unchanged. No new branches or bypass.

## 2026-11-03 — BUILD-HTML-COMMENT-118 (dev; exact-head QA pending)

**Change:** Reject HTML comment openers in inline JavaScript module source before rebuilding standalone HTML. HTML script parsing treats `<!--` specially; a focused subprocess regression checks the rejection diagnostic and unchanged original index. Prior exact-head PR Quality 41689680817 passed at 5d273b3; new head needs fresh checks. Local checkout failed DNS resolution; no local suite claimed.

**NEXT FIVE (status / acceptance tests):**
1. **P0 PR #179 QA/release (pending):** exact-head dev/PR Quality structural and browser checks green; applicable protections/reviews verified; ordinary merge; main Quality and Pages verified.
2. **P0 QR rank-boundary references (planned):** high-precision near-threshold references, perturbed RHS and singular rejection with tolerances.
3. **P1 UI controller extraction (planned):** offline source/bundle parity, keyboard/mobile and saved-project round-trip with size delta.
4. **P1 Scalar-root discontinuity (planned):** pole and oscillatory negative cases, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed project fixtures preserve prior state and v1/v2 compatibility.

**Execution ledger:** Read root AGENTS, plan, frozen inventory, branch comparison, PR #179, reviews and exact-head Quality. Added source guard and focused regression; pending new exact-head CI. Frozen 166 gaps/95 partials unchanged. No new branch, force-push, bypass, merge or deletion.

## 2026-11-03 — BUILD-NUL-117 (dev; QA pending)

**Change:** Reject embedded NUL in standalone module source before writing HTML. Focused subprocess regression asserts diagnostic and original-index preservation. Previous exact-head dev and PR Quality runs 41679640777 and 41679647176 passed at 1748115; new commit needs exact-head CI. Branch protection read returned 403; no merge claimed.

**NEXT FIVE (status / acceptance tests):**
1. **P0 PR #179 and BUILD-NUL-117 QA/release (pending):** exact-head dev and PR Quality structural/browser green; protections/reviews verified; ordinary merge; main Quality and Pages success.
2. **P0 QR rank-boundary references (planned):** threshold-adjacent high-precision matrices, perturbed RHS, singular rejection and tolerances.
3. **P1 UI controller extraction (planned):** offline source/bundle parity, keyboard/mobile, project round-trip and size delta.
4. **P1 Scalar-root discontinuity (planned):** pole/oscillation negatives, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed projects preserve prior state and v1/v2 compatibility.

**Execution ledger:** Inspected root AGENTS, plan, inventory, dev/main, PR #179, reviews, latest CI and Pages. Committed NUL guard, regression, plan and changelog together. Historical 166 gaps/95 partial features unchanged. No bypass, new branch or force-push.

## 2026-11-03 — BUILD-BOM-116 (dev; QA pending)

**Change:** Reject UTF-8 BOM at the start of standalone JavaScript module sources before replacing embedded HTML, avoiding an unexpected encoding signature in inline scripts. Focused isolated subprocess regression checks diagnostic and byte-for-byte unchanged index. Previous exact-head PR Quality run 41669319024 succeeded at 69ff29a; new head requires its own checks. No release claimed.

**NEXT FIVE (status / acceptance tests):**
1. **P0 PR #179 and BUILD-BOM-116 QA/release (pending):** exact-head dev/PR Quality green including structural and browser tests; applicable protection/reviews verified; ordinary merge; main Quality and Pages success.
2. **P0 QR rank-boundary references (planned):** independent high-precision threshold-adjacent matrices, perturbed RHS and singular rejection with tolerances.
3. **P1 UI controller extraction (planned):** offline source/bundle parity, keyboard/mobile, saved-project round-trip and size delta.
4. **P1 Scalar-root discontinuity (planned):** pole/oscillation negative references, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed projects preserve prior state and v1/v2 compatibility.

**Execution ledger:** Read root AGENTS, living plan, frozen inventory, dev/main comparison and PR #179; checked exact-head PR Quality 41669319024 (passed). Added BOM guard and regression to dev; new exact-head checks, release and Pages remain pending. Historical 166 gaps/95 partial features unchanged. No branch creation, force-push, bypass or deletion.

## 2026-11-03 — BUILD-EMPTY-SOURCE-115 (dev; exact-head QA pending)

**Change:** Standalone builder rejects empty and whitespace-only modular JavaScript source before replacing embedded HTML. A focused isolated subprocess regression asserts diagnostic and unchanged original index for both inputs. Source commit b38e358; regression commits 01ae2dd and fixture correction 8ac8136. Previous exact-head dev Quality run 41658791993 succeeded at 9bd506ea; new commits require new CI. No merge or Pages deployment claimed.

**NEXT FIVE (status / acceptance tests):**
1. **P0 PR #179 and BUILD-EMPTY-SOURCE-115 QA/release (pending):** full exact dev and PR Quality green for candidate SHA, applicable protections/reviews satisfied, ordinary PR merge, main Quality and Pages confirmed.
2. **P0 QR rank-boundary references (planned):** independent high-precision near-threshold matrices, perturbed RHS, singular rejection and deterministic tolerances.
3. **P1 UI controller extraction (planned):** offline source/bundle parity, keyboard/mobile and project round-trip regression, bundle-size comparison.
4. **P1 Scalar-root discontinuity (planned):** pole and oscillatory negative fixtures, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed projects preserve prior state and legacy v1/v2 compatibility.

**Execution ledger:** Inspected AGENTS, living plan, frozen inventory, main/dev comparison, PR #179 and successful development Quality. Added empty-source guard and direct regression to dev. New exact-head CI, PR Quality, main Quality and Pages pending. Historical 166 gaps and 95 partial features remain frozen. No new branches, force-push, CI bypass, merge or deletion.

## 2026-11-03 — BUILD-SOURCE-OPENER-114 (dev; CI pending)

**Change:** Standalone builder rejects embedded HTML script opening tags in modular JS source, including mixed-case and tab-separated variants, before writing index. Focused subprocess regression checks rejection and unchanged original HTML. Previous PR #179 Quality run 41649964029 passed at 751f9d1; new dev head needs exact-head checks. Local clone unavailable (github.com DNS resolution failure). No release claimed.

**NEXT FIVE (status / acceptance tests):**
1. **P0 PR #179 and BUILD-SOURCE-OPENER-114 QA/release (pending):** exact dev and PR Quality at latest SHA green, applicable reviews/protections verified, ordinary dev-to-main PR merge, main Quality and Pages success.
2. **P0 QR rank boundary (planned):** high-precision near-threshold references, perturbed RHS and singular rejection with deterministic tolerances.
3. **P1 UI controller extraction (planned):** source/offline parity, keyboard/mobile and saved-project round-trip regression plus bundle size delta.
4. **P1 Scalar-root discontinuity (planned):** pole and oscillatory negative cases, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed project fixtures preserve prior state and legacy v1/v2 compatibility.

**Execution ledger:** Read AGENTS, living plan, frozen inventory, dev/main comparison, open PR #179 and successful PR Quality job. Added source guard and focused regression on dev; local GitHub DNS blocked test checkout. No merge, force-push, branch creation, bypass or deletion. Historical 166 gaps/95 partial features unchanged.

## 2026-11-03 — BUILD-MISSING-SOURCE-113 and PR #178 release checkpoint

**Release:** PR #178 merged normally at `1df9a6fbf69678268a937c06c39786c6a7fe3702` after exact-head PR Quality run 41640828944 passed, including structural and browser steps. No reviews recorded; GitHub accepted the ordinary merge. Dev was synchronized by non-force fast-forward. Main Quality, Pages and hosted behavior still require independent verification.

**Implemented on dev; exact-head CI pending:** `scripts/build.py` now raises a descriptive `Missing standalone module source: src/data-tables.js` error when a module source is absent. Focused subprocess regression verifies nonzero exit, diagnostic and unchanged original index. Source commit `6d40a50`, regression commit `e1091b7`. No full local Python/Chromium test pass claimed.

**NEXT FIVE (status / acceptance tests):**
1. **P0 BUILD-MISSING-SOURCE-113 QA/release (pending):** exact-head dev and PR Quality structural/browser checks green; applicable approvals/protections met; ordinary merge; main Quality and Pages and hosted smoke verified.
2. **P0 QR rank boundary (planned):** independent high-precision near-threshold matrices, perturbed RHS, singular rejection and deterministic tolerances.
3. **P1 UI controller extraction (planned):** source/offline parity, keyboard/mobile smoke, saved-project round-trip and bundle-size comparison.
4. **P1 Scalar-root discontinuity (planned):** pole/oscillatory negative references, bounded diagnostic and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed fixtures preserve state and v1/v2 legacy round trips.

**Execution ledger:** Inspected root AGENTS, living plan, frozen inventory, dev/main comparison, PR #178, exact-head successful Quality and reviews. Released verified PR via ordinary merge; added small build diagnostic and focused regression on dev. No force-push, branch creation or CI bypass. Historical 166 gaps/95 partial features remain frozen.

## 2026-11-03 — BUILD-MISSING-CLOSE-112 exact-head regression repair

**CI failure:** PR #178 Quality run 41631737725 failed 1/291 structural tests at dev 907b41a1820caf76adf3316af0f45df08c1e35b1. The truncated-script fixture encoded literal backslash-n, so the marker guard fired before the missing-close guard. Fixed fixture to use real newline (commit e8f07d9); builder validation unchanged. Full exact-head CI and browser QA pending. No merge or deployment claimed. Historical 166 gaps/95 partial features frozen.

**NEXT FIVE (status / acceptance):**
1. **P0 PR #178 release (pending):** corrected fixture passes 291+ structural tests, dev/PR exact-head Quality and browser suites green, required reviews/protections met, ordinary merge, main Quality and Pages success.
2. **P0 QR rank boundary (planned):** independent high-precision near-threshold matrices, perturbed RHS and singular rejection with deterministic numerical tolerances.
3. **P1 UI controller extraction (planned):** offline bundle parity, keyboard/mobile smoke, project round-trip and size delta.
4. **P1 Scalar-root discontinuity (planned):** poles and oscillatory counterexamples, bounded diagnostics and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed fixtures preserve state, legacy v1/v2 remain compatible.

**Execution log:** Read AGENTS, plan, historical inventory, dev/main comparison, open PR and exact-head failed job log; corrected focused regression on dev. No CI bypass, branch creation, force push or merge. Exact-head rerun pending.

## 2026-11-03 — BUILD-MISSING-CLOSE-112: truncated standalone module diagnostics

**Implemented on dev; exact-head CI pending.** The standalone builder now reports a specific missing closing-script error instead of an unhandled substring lookup when a module block is truncated. A focused isolated Python regression asserts the diagnostic and byte-for-byte preservation of the original index. Source/test commits e6aa29653c93f362d71be7ba3464304207b7b57b and 419a8851775a4e62159c5336f5ed609a92084fba. Previous exact-head development Quality run 41624502050 succeeded at 3880cbe8bd99301e8db89a7a7572face44bbe0e3; new head requires fresh verification. No release claimed. Historical 166 gaps and 95 partial features remain frozen.

**NEXT FIVE (status / acceptance tests):**
1. **P0 BUILD-MISSING-CLOSE-112 QA/release (pending):** focused structural and browser CI green at exact dev and PR heads; required review/protection checks; ordinary PR merge; verify main Quality and Pages.
2. **P0 QR rank-boundary references (planned):** independent high-precision threshold-adjacent matrices, perturbed RHS and singular rejection.
3. **P1 UI controller extraction (planned):** offline bundle parity, keyboard/mobile smoke, project round-trip and size measurements.
4. **P1 Scalar-root discontinuity (planned):** pole and oscillatory counterexamples, bounded warnings and recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed projects preserve state; legacy v1/v2 compatibility.

**Execution log:** Inspected AGENTS, living plan, frozen inventory, dev/main comparison and exact-head Quality jobs. Added bounded missing-close diagnostic and regression on dev. New CI, PR checks, main Quality and Pages pending; no force push, bypass or branch deletion.

## 2026-11-03 — BUILD-NESTED-CASE-111 exact-head CI repair

**CI failure diagnosed and corrected on dev; fresh exact-head QA pending.** PR #178's prior exact-head Quality run 41615609901 failed 4 of 290 structural tests: nested-script fixtures used literal backslash-n instead of newline, so marker detection failed first; the builder regex also used a doubled backslash in its raw whitespace class, missing actual tabs. Corrected both without relaxing the nested-script rejection or rollback assertions. Source commit e4f9d33f3d0ceab2fc2eaeebb7386180e3c0cee8; test fixes aec1072c02a8a65518d42413e042f581a60139ef and 5840bcf9972333b6c9d6c27625d80029d8217ab9. No full Python/Chromium pass or release claimed. Frozen 166 gaps/95 partials unchanged.

**NEXT FIVE (status / acceptance tests):**
1. **P0 BUILD-NESTED-CASE-111 QA/release (pending):** exact-head dev and PR Quality including all 290 structural tests and browser jobs green; required review/protection gates; ordinary PR merge; verify main Quality and Pages.
2. **P0 QR rank-boundary references (planned):** independent threshold-adjacent reference matrices, perturbed RHS, singular rejection.
3. **P1 UI controller extraction (planned):** source/offline parity, keyboard/mobile smoke, project round-trip and bundle size.
4. **P1 Scalar-root discontinuity (planned):** poles, oscillatory cases, bounded warning and browser recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed fixtures preserve state; legacy v1/v2 compatibility.

**Execution log:** Read AGENTS, living plan, frozen inventory, dev/main comparison, PR #178 and failing exact-head job logs. Corrected regex and fixture escapes on dev. Pending new exact-head CI; no merge or deployment attempted.

## 2026-11-03 — Case-insensitive standalone nested script protection (BUILD-NESTED-CASE-111)

**Implemented on dev; CI and release pending.** PR #177 exact-head dev Quality 41607093925 and PR Quality 41607109020 succeeded at dfb8fc25143ad34292b9a36a04c4c87e8367faf8; ordinary merge 57d762630046c629597c6e2daf6d11d0ab651efe; dev fast-forwarded without force. Main Quality 41606987001 and Pages 41606985903 for previous main 3d299ae84ecc0043bc5f821b01f633e100153c68 succeeded. New builder fix recognizes mixed-case, tabbed and unadorned nested script opening tags, preventing ambiguous inline module boundaries. Focused regression added on dev in e40bfa542dafff39a066775038140d8f27178e37; local clone/test blocked by DNS resolution of github.com. No full new exact-head CI pass or deployment claimed. Frozen 166 gaps/95 partials unchanged.

**NEXT FIVE (status / acceptance tests):**
1. **P0 BUILD-NESTED-CASE-111 QA/release (pending):** exact dev and PR Quality green including uppercase/tabbed opener regression; ordinary PR after required reviews/checks; verify main Quality and Pages.
2. **P0 QR rank-boundary numerical references (planned):** independent high-precision threshold-adjacent matrices, perturbed RHS and singular rejection.
3. **P1 reusable UI controller extraction (planned):** offline bundle parity, keyboard/mobile smoke, saved-project round trip and bundle-size measurement.
4. **P1 scalar-root discontinuity (planned):** pole and oscillatory negative fixtures, bounded sampling warnings and browser recovery.
5. **P1 Matrix/Data atomic import (planned):** malformed nested fixtures preserve existing state; legacy v1/v2 compatibility.

**Execution log:** Read root AGENTS, frozen inventory, living plan, dev/main refs, PR #177, exact-head checks, reviews and rulesets. Merged green PR #177, synchronized dev non-force. Updated source and focused regression on dev; local git clone failed DNS. New CI and Pages verification pending.

## 2026-11-03 — Nested inline-script boundary validation (BUILD-NESTED-SCRIPT-110)

**Implemented on dev; exact-head CI pending.** PR #176 exact-head PR Quality 41600054636 passed, merged normally as 3d299ae84ecc0043bc5f821b01f633e100153c68; dev fast-forwarded non-force. Builder now rejects a nested HTML script opener before the expected module closing tag, rather than replacing content across an ambiguous script boundary. Focused isolated regression asserts failure and byte-for-byte preservation of original index. Source and regression committed on dev; full Python/Chromium CI and post-merge main Quality/Pages not yet independently verified. Frozen 166 gaps/95 partials unchanged.

**NEXT FIVE (status / acceptance tests):**
1. **P0 BUILD-NESTED-SCRIPT-110 QA/release (pending):** focused Python and full dev/PR Quality pass on exact head, ordinary dev-to-main PR after applicable reviews/protections, main Quality and Pages verified.
2. **P0 QR rank-boundary references (planned):** high-precision coefficients and perturbed RHS near rank cutoff; singular rejection.
3. **P1 UI controller extraction (planned):** offline source parity, keyboard/mobile smoke, saved-project round trip and bundle-size delta.
4. **P1 scalar-root discontinuity (planned):** pole and oscillatory negative cases, bounded sampling warning.
5. **P1 Matrix/Data import atomicity (planned):** malformed nested fixtures preserve state; legacy v1/v2 compatibility.

**Execution log:** Inspected root AGENTS, living plan, frozen inventory, main/dev comparison, PR #176, exact-head PR CI job and reviews. Merged after PR Quality success and synchronized dev. Implemented builder guard and focused regression, without creating branches or bypassing CI. Local full test suite unavailable; awaiting exact-head CI.

## 2026-11-03 — Script terminator integrity (BUILD-SCRIPT-TERMINATOR-109)

**Implemented on dev; exact-head QA pending.** PR #175 exact-head PR Quality run 41593936573 passed (static and browser regression job); ordinary merge SHA 27dcda12154910d16b7170eec91c12e77ac359bc. Dev fast-forwarded non-force. Main Quality and Pages for this merge are not independently verified. Build now rejects case-insensitive embedded HTML script closing sequences in module source, which otherwise prematurely terminate inline scripts. Added focused negative regression asserting original index remains unchanged. Source and test are on dev; full new exact-head CI is pending. Historical 166 gaps / 95 partial features unchanged.

**NEXT FIVE (status / acceptance):**
1. **P0 BUILD-SCRIPT-TERMINATOR-109 QA/release (pending):** focused regression, full dev and PR Quality pass at exact head, ordinary PR merge, main Quality and Pages verified.
2. **P0 QR rank-boundary references (planned):** high-precision coefficients and perturbed RHS near rank threshold, plus singular rejection.
3. **P1 UI controller extraction (planned):** offline parity, keyboard/mobile browser smoke, project round trip, bundle-size delta.
4. **P1 scalar-root discontinuity (planned):** pole/oscillatory negative fixtures and bounded-sampling guidance.
5. **P1 Matrix/Data atomic rollback (planned):** malformed nested project fixtures preserve existing state and legacy migrations.

**Execution log:** Read AGENTS, plan, frozen inventory, dev/main comparison, PR #175, exact-head PR Quality and reviews. Merged only after successful PR Quality, synchronized dev, implemented bounded source/test follow-up. No local full test execution or hosted-browser verification; new exact-head CI pending. No new branch or force push.

## 2026-11-03 — Standalone build marker integrity (BUILD-MARKER-108)

**Implemented on dev; exact-head Quality pending.** Ordinary PR #174 merged after development and PR Quality jobs each completed successfully (180 steps); merge SHA `1e3744f7ee6217cf2bd59c3fbbc945172686a702`. Dev fast-forwarded non-force. Main Quality/Pages and hosted behavior for that merge remain to be verified. Builder now rejects missing or duplicate module script markers instead of silently replacing the wrong embedded script; a new isolated regression checks both failures leave index unchanged. Production app bundle unchanged. Source and regression were committed separately because GitHub Contents API writes one file per commit; both are now on dev. Full repository and browser suites await exact-head CI.

**NEXT FIVE (status / dependencies / acceptance):**
1. **P0 BUILD-MARKER-108 QA/release (pending):** exact-head development and PR Quality green, ordinary dev→main PR, main Quality and Pages confirmed; missing/duplicate marker regression green.
2. **P0 QR rank boundary references (planned; QR):** independent high-precision coefficients/residuals for threshold-adjacent matrices and perturbed RHS, plus singular rejection.
3. **P1 UI controller extraction (planned; build):** offline rebuild parity, keyboard/mobile smoke, saved-project round trip and size delta.
4. **P1 scalar-root discontinuity (planned; root):** pole and oscillatory counterexamples, bounded sampling warning and browser recovery.
5. **P1 Matrix/Data import rollback (planned; schema):** malformed nested fixtures preserve prior state and legacy v1/v2 migration.

**Execution log:** Read AGENTS, historical inventory, plan, PR #174 and current dev/main comparison. Verified PR Quality run 41587337661 and dev Quality run 41587326240 job success, ordinary merge and dev fast-forward. Added builder guard and isolated regression. Historical 166 gaps/95 partial features unchanged. Main release checks and new dev exact-head checks pending.

## 2026-11-03 — Data Tables column identity validation (DATA-COLUMN-IDENTITY-107)

**Implemented on dev, awaiting exact-head Quality and PR release.** Reject blank and case/trim-equivalent duplicate saved table column names before restoring a project. Preserve original display strings and legacy v1/v2 projects with unique columns. Focused Node/Python regression tests valid/invalid column names, both versions, source/bundle parity and input immutability. Main merge 0d9895eb68f8c7272f3730f9f247ce6b5ca70834 passed main Quality runs 41580854721/41580866391 and Pages 41580854451; hosted browser unverified.

**NEXT FIVE (status / dependencies / acceptance):**
1. **P0 DATA-COLUMN-IDENTITY-107 release (CI pending):** exact dev and PR Quality pass; ordinary dev→main PR; post-merge main Quality and Pages pass.
2. **P0 QR rank boundaries (planned):** 90-digit independent references for coefficients/residuals and perturbed RHS near threshold; singular rejection.
3. **P1 UI controller extraction (planned):** offline parity, keyboard/mobile smoke, project round trip, bundle-size comparison.
4. **P1 scalar-root discontinuity (planned):** pole and oscillation negative tests, bounded-sampling caveat and browser recovery.
5. **P1 atomic Matrix/Data import rollback (planned):** malformed nested fixtures, preserved prior state, legacy migration and responsive focus.

**Execution log:** Inspected dev/main, root AGENTS, frozen inventory, plan, PRs and latest CI/Pages. Prior release main and dev were both 0d9895eb68f8c7272f3730f9f247ce6b5ca70834; main Quality and Pages passed. Added bounded column identity validation with regression, retained 166 historical gaps and 95 partial features. Full CI and new Pages pending.

## 2026-11-03 — Repair exact-head CI regression for empty-workbook selection (DATA-PROJECT-EMPTY-SELECTION-106)

**Fix committed on dev; CI rerun pending.** PR #173 Quality run 41570028815 failed during structural Python/Node regression (1 failure in 286 tests): the older `tests/test_project_table_selection.py` expected a stale selection in an empty workbook to be accepted, contradicting the new intentional rejection. Updated that existing test to assert rejection of stale and explicit null selections for both v1/v2 and acceptance of legacy missing selection; the newer focused identity regression remains in place. No production solver or schema validation was weakened. Commit `36e982f9ba01fec730f4f62423f4888e7b222e88`; exact-head new Quality and Pages not yet verified.

**NEXT FIVE (status / dependencies / acceptance):**
1. **P0 PR #173 release (blocked on exact-head CI):** rerun all structural and Chromium tests for current dev and PR head, confirm green and applicable review/protection rules, ordinary PR merge, verify main Quality and Pages.
2. **P0 QR rank boundary references (planned; numerical core):** independent 90-digit coefficient/residual references around rank thresholds, perturbed RHS, singular rejection and responsive Chromium.
3. **P1 bounded UI controller extraction (planned; build):** preserve offline source parity, project round trip, keyboard/mobile focus and record bundle-size delta.
4. **P1 scalar-root discontinuity warnings (planned; root solver):** pole/oscillation and bounded-sampling tests with browser error recovery.
5. **P1 Matrix/Data atomic import rollback (planned; project schema):** legacy/current fixtures, malformed nested data, no state loss and responsive focus.

**Execution log:** Inspected root AGENTS, inventory, living plan, dev/main comparison, open PR #173 and exact-head PR CI. Read failing GitHub Actions job log and identified conflicting old regression expectation. Committed focused regression repair on existing dev, leaving validation strict. At inspection main was `6cdcb462f4be9c8d6e5fe14faa2784e6e25cfd4b`; new dev commit `36e982f9ba01fec730f4f62423f4888e7b222e88`. CI, PR merge and Pages for this head are pending; historical 166 gaps/95 partials unchanged.

## 2026-11-03 — Reject stale selected sheet in empty saved workbooks (DATA-PROJECT-EMPTY-SELECTION-106)

**Implemented on dev; exact-head CI/PR/Pages pending.** Project migration rejects explicit non-existent or null selected IDs even when the saved table list is empty; legacy empty workbooks without a selection remain valid. This prevents silent fallback to a different sheet after malformed backup import. Regression extends `tests/test_project_table_id_identity.py` for v1/v2, empty/nonexistent/null selection and legacy no-selection; synchronized `src/project-schema.js` and offline `index.html`. Release only after full Quality and PR checks.

**NEXT FIVE (status/dependencies/acceptance):**
1. **P0 release verification (pending):** exact-head dev and PR Quality green; ordinary dev→main PR; main Quality and Pages confirmed.
2. **P0 QR rank boundary references (planned):** 90-digit independent coefficients and residuals around rank threshold; singular rejection and responsive Chromium.
3. **P1 UI controller extraction (planned):** source/bundle parity, saved-project round trip, keyboard/mobile focus, bundle-size measurement.
4. **P1 scalar-root discontinuity warnings (planned):** pole/oscillation tests, bounded-sampling caveat and browser recovery.
5. **P1 Matrix/Data import atomic rollback (planned):** legacy/current fixtures, malformed nested data, no state loss and mobile focus.

**Execution log:** Read AGENTS, frozen inventory, plan, open PR and exact-head CI. PR #172 Quality 41563684929 passed; ordinary merge 6cdcb462f4be9c8d6e5fe14faa2784e6e25cfd4b; dev safely fast-forwarded. Implemented new empty-workbook selection validation with focused regression. New exact-head CI and post-merge Pages pending. Historical 166 gaps/95 partials unchanged.

## 2026-11-03 — Saved Data Tables ID collision rejection (DATA-PROJECT-ID-105)

**Implemented on dev; exact-head Quality and production release pending.** Project migration now rejects duplicate present Data Tables IDs, blank/non-string IDs and IDs longer than 120 characters. Legacy projects with omitted IDs remain accepted; valid selected IDs, display names, column order and cell values are preserved without mutation. This closes ambiguous selection/formula target identity for malformed imported backups. New Node/Python regression `tests/test_project_table_id_identity.py` covers both v1/v2, positive, duplicate, malformed, legacy, source/bundle parity and input immutability. Source `src/project-schema.js` and offline `index.html` were synchronized. Full Python and browser Quality are required before release.

**Prior release verification:** PR [#171](https://github.com/saeedsai/ProMathStudio/pull/171) merge `84d400394fe763928c1146102c50cd1aa4137bd4`; exact main [Quality 41557189814](https://github.com/saeedsai/ProMathStudio/actions/runs/41557189814) and [Pages 41557188535](https://github.com/saeedsai/ProMathStudio/actions/runs/41557188535) both succeeded; exact post-merge dev docs [Quality 41557224903](https://github.com/saeedsai/ProMathStudio/actions/runs/41557224903) succeeded. Independent hosted-browser interaction remains unverified.

**NEXT FIVE (status, dependencies and acceptance):**
1. **P0 DATA-PROJECT-ID-105 release QA (in progress):** exact-head Python/Node and responsive Chromium Quality green, verified ordinary dev→main PR, main Quality and Pages success.
2. **P0 QR rank-boundary reference audit (planned; QR):** 90-digit independent coefficient/residual references across tolerance margins, RHS perturbation, singular rejection and browser smoke.
3. **P1 bounded UI controller extraction (planned; build):** offline source parity, project round trip, keyboard focus and 390/768/1280 Chromium tests; measure bundle size.
4. **P1 scalar-root pole and aliasing guidance (planned; root solver):** oscillatory paired roots, poles, bounded sampling warning, browser error recovery.
5. **P1 Matrix/Data schema resilience (planned; project):** legacy/current fixtures, malformed nested imports, atomic rollback and no data loss.

**Execution log:** Inspected AGENTS, living plan, frozen inventory, dev/main SHAs, open PRs and exact-head CI/Pages. Confirmed PR #171 main Quality/Pages success. Existing dev was ahead of main by docs only. Added bounded saved-table-ID validation in modular and standalone source and focused regression on dev; GitHub-hosted full Quality and Pages are pending for new head. No new branch, direct main push, force, or bypass. Historical 166 gaps and 95 partials remain frozen baseline.

## 2026-11-03 — QR acceptance release reconciliation (MATH-QR-GATE-104)

**Released via [PR #171](https://github.com/saeedsai/ProMathStudio/pull/171)** after exact-head PR [Quality run 41549483017](https://github.com/saeedsai/ProMathStudio/actions/runs/41549483017) completed successfully. Merge SHA: `84d400394fe763928c1146102c50cd1aa4137bd4`. Existing `dev` safely fast-forwarded to merge SHA with non-force expected-head lease. Post-merge main Quality and Pages publishing are **not yet verified**; hosted behavior remains unverified. No additional feature implementation in this run; prioritize correctness and honest release evidence over untested source changes.

**NEXT FIVE (status / acceptance):**
1. **P0 post-merge release validation (pending):** verify exact main Quality, Pages publish, and hosted critical path; repair failures without bypass.
2. **P0 QR rank boundary audit (planned):** independent 90-digit coefficient/residual references at tolerance margins and perturbed RHS; singular rejection, Node and responsive Chromium.
3. **P1 reusable UI controller extraction (planned):** source/standalone parity, saved-project round trip, keyboard/mobile focus, bundle-size comparison.
4. **P1 scalar root aliasing/pole diagnostics (planned):** oscillatory paired roots, pole rejection, bounded-sampling warning, browser recovery.
5. **P1 Matrix/Data project migration (planned):** legacy/current fixtures, malformed nested import atomic rollback, responsive focus retention.

**Execution log:** Reviewed AGENTS, living plan, frozen inventory, dev/main comparison and PR #171. PR head `f2296b7505aebaaf4d77f86950956cba62b1bd55` passed PR Quality; merged via ordinary PR; synchronized dev. Historical 166 gaps/95 partials unchanged. No source changes or new regression committed in this release-focused checkpoint.

## 2026-11-03 — QR orthogonality acceptance transparency (MATH-QR-GATE-104)

**Implemented on dev; exact-head Quality/PR/Pages pending.** The existing QR least-squares acceptance gate now exposes its effective tolerance and whether the orthogonality check was deliberately skipped for a near-exact fit (relative residual at or below 1e-12); the skipped threshold is null, not an unbounded number. The Calculator displays “Orthogonality acceptance” and clear ordinary/roundoff-relaxed/near-exact guidance for ordinary and weighted 3×2 least squares. No numerical acceptance thresholds or solver decisions changed. New focused Node/Python regression covers ordinary 1e-8, near-rank relaxed threshold, near-exact skip, singular/invalid input and offline parity; existing 390/768/1280 Chromium smoke checks guidance and numerical output. The threshold is a floating-point acceptance heuristic, not a certified accuracy guarantee.

**Previous release evidence:** PR [#170](https://github.com/saeedsai/ProMathStudio/pull/170) passed exact-head [dev Quality 41543081907](https://github.com/saeedsai/ProMathStudio/actions/runs/41543081907) and [PR Quality 41543129569](https://github.com/saeedsai/ProMathStudio/actions/runs/41543129569), 180/180 job steps each. Ordinary merge SHA `21ff2ab0c21c47ac2eb818a9b4823ac684ac669f`; dev fast-forwarded to main without force. Earlier PR #169 main [Quality 41542580769](https://github.com/saeedsai/ProMathStudio/actions/runs/41542580769) and [Pages 41542580197](https://github.com/saeedsai/ProMathStudio/actions/runs/41542580197) succeeded. New post-merge Quality/Pages evidence must be checked before claiming #170 deployed.

**NEXT FIVE concrete features (status, dependencies and acceptance tests):**
1. **P0 — Orthogonality transparency exact-head QA/release (in progress; QR).** New Node/Python and responsive Chromium tests green for exact dev/PR head; ordinary PR merge, then main Quality and Pages evidence.
2. **P0 — Near-rank QR boundary and RHS perturbation audit (planned; QR).** Independent 90-digit references at rank tolerance ± margins, exact/perturbed RHS and extreme weights; reject genuinely singular inputs.
3. **P1 — Extract one bounded UI controller (planned; offline build).** Standalone rebuild parity, saved-project round-trip, keyboard/mobile focus and bundle-size measurement.
4. **P1 — Scalar-root aliasing and discontinuity regression (planned; root solver).** Oscillatory paired roots, pole rejection, bounded sampling guidance, 390/768/1280 browser recovery.
5. **P1 — Matrix/Data saved-project schema resilience (planned; projects).** Legacy/current fixtures, malformed nested import atomic rollback, 390px focus retention and no data loss.

**Execution log (2026-11-03 Europe/Stockholm):** Read AGENTS, frozen inventory, living plan, PR #170 and exact-head dev/PR/main/Pages CI. Merged #170 after both full Quality jobs passed; safely fast-forwarded dev. Implemented new QR gate transparency in shared source and self-contained bundle with focused Node/Python and responsive browser assertions. Full exact-head new CI and new production Pages pending. Historical 166 gaps/95 partial features unchanged.

## 2026-11-03 — Near-rank weighted QR orthogonality roundoff guard (MATH-QR-ORTHO-103)

**Implemented on dev; exact-head Quality/PR/Pages pending.** Corrected the shared QR least-squares orthogonality acceptance guard to account for binary64 cancellation in A·x−b when the fitted residual is small. Previously the fixed 1e-8 normalized check falsely rejected valid near-dependent 3×2 weighted fits with small nonzero residual. The new tolerance is max(1e-8, 32·epsilon/relativeResidual), with the existing near-exact residual skip retained; ordinary-size residuals keep the strict gate. This is a roundoff-aware numerical guard, **not** a certified coefficient accuracy or general rank guarantee. Independent 90-digit Decimal normal-equation references (test-only; production remains QR) cover d=1e-4..1e-11, three weight patterns including 1e-8, residuals, rank/weight rejection and input immutability. Added responsive Chromium regression of a previously falsely rejected near-rank fit; standalone bundle synchronized.

**Prior release reconciled:** [PR #169](https://github.com/saeedsai/ProMathStudio/pull/169) exact dev [Quality 41533768610](https://github.com/saeedsai/ProMathStudio/actions/runs/41533768610) and PR [Quality 41533824339](https://github.com/saeedsai/ProMathStudio/actions/runs/41533824339) both passed for head `48aacbaee4f8d24dfd89ac67ab7d3efecc33b681`; ordinary merge `f92bfda0ece73d8176607d84c8a9a15ee84aad7c`; dev fast-forwarded without force. Main Quality [41542580769](https://github.com/saeedsai/ProMathStudio/actions/runs/41542580769) and Pages [41542580197](https://github.com/saeedsai/ProMathStudio/actions/runs/41542580197) were in progress at inspection; verify final outcomes before claiming deployed.

**NEXT FIVE concrete features (status, dependencies and acceptance tests):**
1. **P0 — Orthogonality guard exact-head QA/release (in progress; QR).** Green full Python/Node and responsive Chromium on exact dev/PR SHA; ordinary authorized PR merge, then main Quality and Pages evidence.
2. **P0 — Near-rank QR tolerance boundary and perturbation audit (planned; QR).** Independent 90-digit references around the 1e-12 rank threshold, exact/perturbed RHS and extreme weights, explicit rank-failure paths, no false success.
3. **P1 — Extract one bounded UI controller (planned; offline build).** Byte-identical standalone rebuild, saved-project round-trip, keyboard/mobile focus and bundle-size benchmark.
4. **P1 — Scalar-root aliasing/discontinuity regression (planned; root solver).** Oscillatory paired roots, pole rejection, bounded sampling guidance and 390/768/1280 browser recovery.
5. **P1 — Matrix/Data saved-project schema resilience (planned; projects).** Legacy/current fixtures, malformed nested import atomic rollback, 390px focus retention and no data loss.

**Execution log (2026-11-03 Europe/Stockholm):** Inspected AGENTS, frozen inventory, plan, PR #169, dev/main, exact-head CI and Pages. PR #169 green and merged normally; dev fast-forwarded. Git clone unavailable due to github.com DNS; authenticated GitHub API used for source/tests/docs. V8 near-rank reproduction confirmed the fixed guard previously rejected valid fits and the corrected guard returns finite coefficients. New Decimal and browser tests registered; full exact-head CI/Pages pending. Historical 166 gaps/95 partial features unchanged.

## 2026-11-02 — Weighted normwise residual ratio (MATH-WLS-NORMRES-102)

**Implemented on dev; exact-head CI and deployment pending.** The bounded weighted 3×2 QR fit now exposes ||D(Ax-b)||₂/(||DA||F||x||₂+||Db||₂), D=diag(sqrt(w/max(w))), using the existing fitted residual and scaled design/RHS without a duplicate solver. For A=[[1,0],[1,1],[1,2]], b=[1,2,9], w=[1,1,.01], analytic ratio ≈0.11625798496246446. Positive common-weight scaling, exact and zero RHS, near-rank 1e-4..1e-10, invalid/rank-deficient and immutability covered by a new Node/Python test; standalone parity and registered 390/768/1280 Chromium numerical, keyboard and error-recovery gate extended. It is a descriptive fit-residual ratio, **not** a certified least-squares backward error, coefficient forward-error or statistical confidence bound.

**Release reconciliation:** [PR #168](https://github.com/saeedsai/ProMathStudio/pull/168) exact PR-head [Quality 41525568357](https://github.com/saeedsai/ProMathStudio/actions/runs/41525568357) passed; ordinary merge SHA `5f6a7342091f1465b5fb8f417874c0b8194736e0`. Dev fast-forwarded to that main merge without force. New main Quality and Pages deployment are pending independent verification, so do not claim the hosted release is live.

**NEXT FIVE concrete features (status, dependencies and acceptance tests):**
1. **P0 — Normwise residual exact-head QA and release (in progress; weighted QR).** Full Python/Node and responsive Chromium green on final dev and PR heads, authorized ordinary merge, verify main Quality and Pages.
2. **P0 — High-precision near-rank coefficient validation (planned; QR).** Compare coefficient and weighted residual against independent decimal/arbitrary-precision references for d=1e-4..1e-11 and extreme positive weights; reject singular inputs and document tolerance limits.
3. **P1 — Extract one bounded UI controller (planned; offline build).** Byte-identical generated standalone, saved-project round-trip, keyboard/mobile focus and bundle-size benchmark.
4. **P1 — Scalar root aliasing/discontinuity regression (planned; root solver).** Oscillatory paired roots, pole rejection, bounded sampling guidance and 390/768/1280 browser recovery.
5. **P1 — Matrix/Data project schema resilience (planned; saved projects).** Legacy/current fixtures, malformed nested import atomic rollback, 390px focus retention and no data loss.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, living plan, frozen inventory, branch diff and PR/CI. PR #168 exact-head Quality passed and merged normally; dev fast-forwarded. Git clone unavailable due to github.com DNS, so source/test/docs changes use the authenticated GitHub connector. New analytical reference and regression registered; full Python/Chromium and exact new-head CI require GitHub Actions. Historical 166 gaps/95 partial features unchanged.

## 2026-11-02 — Weighted fitted predictions and near-rank reference checks (MATH-WLS-FITTED-101)

**Implemented on dev; exact-head CI/PR/Pages pending.** The existing QR-based 3×2 weighted fit now reports predicted RHS values A·x in original observation units, sharing the exact values used for residuals (no duplicate solver). For A=[[1,0],[1,1],[1,2]], b=[1,2,9], w=[1,1,.01], fitted values are [33/35,74/35,23/7]. Independent analytic reference, common-weight invariance, near-rank d=1e-4 through 1e-11 coefficient/prediction checks, singular/invalid, immutability, standalone parity, and 390/768/1280 Chromium UI/keyboard recovery tests. Near-rank predictions can be stable while coefficients are sensitive; not a certified high-precision bound.

**Release reconciliation:** [PR #167](https://github.com/saeedsai/ProMathStudio/pull/167) merged MATH-WLS-ROUND-099 and MATH-WLS-SHARES-100 at `792fd8b914e9c65548a3548534ab2eee2ffb0bbc` after exact PR-head [Quality 41515977252](https://github.com/saeedsai/ProMathStudio/actions/runs/41515977252) passed all 180 workflow steps. Dev fast-forwarded to the merge commit without force. Post-merge main Quality and Pages not yet independently verified; do not mark hosted deployment confirmed.

**NEXT FIVE concrete features (dependencies and acceptance tests):**
1. **P0 — Exact-head fitted-value CI and safe promotion (in progress; depends on weighted QR).** All structural/Node/Chromium checks green for final dev SHA and PR head; ordinary PR merge only, verify main Quality and Pages.
2. **P0 — Independent high-precision weighted QR coefficient accuracy (planned; depends on shared QR).** Compare coefficients and weighted backward residuals against arbitrary-precision references at 1e-4…1e-11, extreme positive weights and rank failure; assert appropriate tolerances or explicit rejection.
3. **P1 — Bounded UI controller extraction (planned; offline build).** Byte-identical standalone rebuild, saved-project round-trip, keyboard/mobile focus and bundle-size benchmark.
4. **P1 — Scalar-root aliasing hardening (planned; numerical solver).** Paired oscillatory roots, discontinuity rejection, bounded-sampling guidance and responsive invalid-input tests.
5. **P1 — Matrix/Data saved-project compatibility (planned; schema).** Legacy/current fixture round-trip, malformed nested import atomic rollback and 390px keyboard focus.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, living plan, frozen inventory, current PR/diff and CI. PR #167 exact-head Quality passed and ordinary merge succeeded; dev fast-forwarded. Local clone unavailable due to github.com DNS resolution. Implemented fitted predictions with a focused Node regression and extended registered responsive Chromium test, synchronized standalone HTML, updated plan and changelog. Isolated V8 analytic and near-rank checks passed before commit; full Python/Chromium and new exact-head release require CI. Historical 166 gaps/95 partial features unchanged.

## 2026-11-02 — Weighted per-row residual shares (MATH-WLS-SHARES-100)

**Implemented on dev; exact-head CI/PR/Pages pending.** The bounded 3×2 weighted QR fit now reports each observation's share of normalized weighted squared residual (row order 1–3). Uses residuals and sqrt(w/max(w)) already computed by the solver; no new solver or button. For A=[[1,0],[1,1],[1,2]], b=[1,2,9], w=[1,1,.01], shares are [1/105,4/105,100/105]. Exact zero residual returns three zeros. Shares are invariant under common weight scaling and are **not** outlier probabilities or uncertainty estimates; near-exact fits can be dominated by floating-point roundoff. New Node analytical/near-rank/zero/invalid/immutability and source/bundle parity test; existing mandatory Chromium 390/768/1280 browser test extended with numerical and text assertions.

**Release/CI checkpoint:** Prior MATH-WLS-ROUND-099 source dev Quality [41505640524](https://github.com/saeedsai/ProMathStudio/actions/runs/41505640524) passed, and [PR #167](https://github.com/saeedsai/ProMathStudio/pull/167) was opened from dev to main. PR Quality was in progress when this compatible increment was prepared; any superseded CI must be rechecked against the **new exact dev/PR head**. Do not merge until final PR checks are green. Main remains at `ea925400886e6624963539b5c034493698a3da02` at discovery. GitHub Pages deployment of this feature not yet verified.

**NEXT FIVE concrete features (dependencies and acceptance tests):**
1. **P0 — Exact-head combined release QA (in progress; dev→main).** Verify final source+bundle+Python+Chromium Quality on dev and PR, inspect approvals/diff, merge only through authorized PR and verify main Quality/Pages.
2. **P0 — Independent near-rank QR coefficient accuracy (planned; shared QR).** High-precision reference coefficients and weighted backward residuals at 1e-4…1e-11, extreme positive weights, rank failure and mobile recovery.
3. **P1 — Bounded UI controller extraction (planned; offline build).** Byte-identical bundle rebuild, saved-project round-trip, keyboard/mobile focus and size benchmark.
4. **P1 — Scalar root aliasing hardening (planned; numerical roots).** Paired oscillatory roots and jump discontinuity references, bounded-sampling guidance, invalid input and Chromium tests.
5. **P1 — Matrix/Data saved-project compatibility (planned; project schema).** Legacy/current fixture round-trip, malformed nested import atomic rollback and 390px focus retention.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, frozen audit, plan, latest diff and exact-head Quality. Existing dev `9da587e6b5ebf35c5e258f7008e099c3a2404b32` was one commit ahead of main, PRs initially none. Prior dev Quality succeeded; PR #167 opened and PR Quality started. Git clone blocked by DNS; connected GitHub and isolated V8 used. Analytical shares, common-weight scaling, zero residual, input immutability and invalid-weight checks passed in V8; full Python/Chromium requires exact-head CI. Historical 166 gaps and 95 partial features unchanged.

## 2026-11-02 — Weighted coefficient numerical-resolution screen (MATH-WLS-ROUND-099)

**Implemented on dev; exact-head CI/PR/Pages pending.** Weighted 3×2 QR fit now reports κ₂(weighted design) × binary64 machine epsilon. At or above 1e-6, warn about possible coefficient digit loss and advise independent high-precision references. This is a *heuristic*, not a certified coefficient-error bound or statistical uncertainty. Reuses existing QR and spectral condition. New analytical, near-rank, common-weight scale, singular/invalid and offline-parity test; extended existing mandatory Chromium keyboard/mobile/recovery regression.

**Prior release reconciliation:** [PR #166](https://github.com/saeedsai/ProMathStudio/pull/166) merged; at discovery dev=main `ea925400886e6624963539b5c034493698a3da02`. [Main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41503596502) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41503596142) passed; [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41503619101) was in progress. Hosted interaction independently unverified; both branches unprotected.

**NEXT FIVE concrete features (dependencies and acceptance tests):**
1. **P0 — Exact-head numerical-resolution CI and safe release (in progress; QR).** Full Python and Chromium green for exact dev SHA, inspect PR diff/checks/approvals, ordinary dev→main merge only when eligible, then main Quality and Pages verification.
2. **P0 — Independent near-rank coefficient accuracy (planned; QR).** High-precision coefficient and backward residual references at 1e-4 through 1e-11 separations, explicit rank failure and mobile recovery.
3. **P1 — Bounded UI controller extraction (planned; standalone build).** Byte-identical rebuild, saved-project round-trip, keyboard/mobile focus and bundle-size benchmark.
4. **P1 — Scalar root aliasing hardening (planned; root solver).** Paired oscillatory roots, discontinuities, bounded sampling warnings, invalid inputs and Chromium.
5. **P1 — Saved-project Matrix/Data compatibility (planned; schema).** Legacy/current fixtures, malformed nested import atomic rollback, keyboard focus and 390px round-trip.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, inventory, living plan and latest CI. Started dev=main `ea925400886e6624963539b5c034493698a3da02`, exactly two unprotected branches, no open PR. Local clone blocked by DNS; GitHub connector used. Isolated V8 weighted numerical, near-rank and scale checks passed; full Python/Chromium unavailable locally. Exact-head CI pending. Historical 166 gaps/95 partial features unchanged.

## 2026-11-02 — Weighted proportional RHS coefficient sensitivity (MATH-WLS-RHS-PERCENT-098)

**Implemented on dev; exact-head CI/PR/Pages pending.** For the bounded weighted 3×2 fit, report the exact maximum absolute change in each coefficient if every RHS observation independently varies by ±1% of its own magnitude, with design A and weights fixed. Reuse existing QR RHS response, no normal-equation solver. Zero RHS entries remain fixed. Example A=[[1,0],[1,1],[1,2]], b=[1,2,9], w=[1,1,.01]: bounds 39/3500 and 109/3500. Deterministic box bound only, not a statistical confidence interval or design/weight-change bound. New analytical/eight-corner/near-rank/weight-scale/zero/singular/invalid tests and mandatory 390/768/1280 Chromium keyboard/error recovery test, standalone source parity.

**Prior release reconciliation:** [PR #165](https://github.com/saeedsai/ProMathStudio/pull/165) merged; dev=main `cb10009d8ce32a9af705464611a7235f851a0062`. [Source dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41496774146) and [PR Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41498011046) passed; [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41499760312) succeeded. [Main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41499762702) and [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41499815974) were in progress at inspection. Hosted behavior not independently verified; both branches unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Near-rank QR coefficient accuracy (planned; shared QR).** Independent high-precision references at 1e-4..1e-9 separations, weighted coefficients, backward residuals, explicit rank failure and browser recovery.
2. **P1 — Bounded UI controller extraction (planned; standalone build).** Byte-identical rebuild, saved-project round-trip, keyboard/mobile focus and bundle-size benchmark.
3. **P1 — Scalar root aliasing hardening (planned; root solver).** Paired oscillatory roots, discontinuities, bounded sampling warnings, invalid inputs and Chromium.
4. **P1 — Saved-project Matrix/Data compatibility (planned; schema).** Legacy/current fixtures, malformed nested import atomic rollback, keyboard focus and 390px round-trip.
5. **P1 — Engineering canonical solver catalog (planned; registry).** One audited source-backed tool with unique ID, truthful status, reused solver, no duplicated actions, offline and mobile tests.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, inventory, plan and CI/CD. Started dev=main `cb10009d8ce32a9af705464611a7235f851a0062`, two branches, no open PR. Git clone DNS failed; connected GitHub source edits and regression registration prepared. Exact-head CI/PR/Pages status must be checked after commit. Historical 166 gaps/95 partial features retained as baseline.

## 2026-11-02 — Weighted design singular values (MATH-WLS-SINGULAR-097)

**Implemented on dev; exact-head CI/PR/Pages pending.** The bounded 3×2 weighted least-squares calculator displays descending singular values of sqrt(w/max(w))·A, reusing existing scaled geometry and cross-product area. The smaller singular value uses a stable product identity rather than subtracting close Gram eigenvalues near rank deficiency. Common positive weight scaling leaves the values unchanged, but column units matter; not a coefficient-error or statistical uncertainty guarantee. No new action button or duplicate solver. New analytical near-rank, orthogonal, invalid-input and source/bundle tests, plus mandatory responsive Chromium keyboard/error-recovery test.

**Prior release reconciliation:** [PR #164](https://github.com/saeedsai/ProMathStudio/pull/164) merged; dev=main `de6afa3de143b83ea0d3f82ef8535fe363c47b48`. [Source dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41487322617) and [PR Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41488570843) passed; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41489685375) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/41489684886) succeeded for merge `de6afa3de143b83ea0d3f82ef8535fe363c47b48`. Post-merge dev Quality [41489704169](https://github.com/saeedsai/ProMathStudio/actions/runs/41489704169) was cancelled, not green. Hosted interaction not independently verified; branches unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Near-rank QR coefficient accuracy (planned; depends on shared QR).** Independent high-precision references for 1e-4..1e-9 separations, weighted coefficients and backward residuals, explicit rank failure and Chromium recovery.
2. **P1 — Bounded UI controller extraction (planned; depends on standalone build).** Preserve byte-identical bundle rebuild, saved-project round-trip, keyboard/mobile focus and size benchmark.
3. **P1 — Scalar root aliasing hardening (planned; depends on root solver).** Paired oscillatory roots and discontinuity references, bounded sampling warnings, invalid-input and responsive Chromium tests.
4. **P1 — Saved-project Matrix/Data compatibility (planned; depends on project schema).** Legacy/current fixtures, malformed nested import atomic rollback, focus and 390px browser round-trip.
5. **P1 — Engineering canonical solver catalog (planned; depends on shared registry).** One source-backed audited tool entry with unique ID, truthful status, reused solver, no duplicate buttons, offline and mobile/keyboard tests.

**Release gate:** Verify exact new dev Quality including mandatory Chromium, inspect PR diff and approvals, ordinary dev→main PR merge only if green; then main Quality, Pages and hosted behavior where possible.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, frozen inventory, living plan, architecture and latest CI/CD. Started dev=main `de6afa3de143b83ea0d3f82ef8535fe363c47b48`, only two branches, no open PR. Git clone unavailable (DNS); used connected GitHub repository. Isolated V8 near-rank/orthogonal/weight-scale references passed. Full local Python/Chromium unavailable; exact-head CI pending. Historical 166 gaps/95 partial features unchanged.

## 2026-11-02 — Weighted RHS independent box sensitivity (MATH-WLS-RHS-BOX-096)

**Implemented on dev; exact-head CI, PR and Pages pending.** The bounded real 3×2 weighted least-squares calculator now reports the exact maximum absolute change in each fitted coefficient when all three RHS observations may independently vary by at most ±1 unit. It reuses the QR-derived RHS response (no normal-equation solver), sums its absolute coefficients and verifies all eight box corners. For A=[[1,0],[1,1],[1,2]], b=[1,2,9], weights=[1,1,0.01], the bounds are 107/105 and 68/35. This is deterministic for fixed A and weights, not a statistical confidence interval or a bound for design/weight changes.

**Prior release reconciled:** [PR #163](https://github.com/saeedsai/ProMathStudio/pull/163) merged, dev=main `ef15565104ddf693ec403940ba8bc9f618fed8e4`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41485231835), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41485261929) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41485230375) succeeded. Hosted interaction remains independently unverified; branches are unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — RHS box sensitivity exact-head QA and repair (in progress; depends on QR).** Analytical 107/105 and 68/35, eight independent ±1 corners, common-weight scale invariance, singular/invalid rejection, source/bundle parity and responsive Chromium 390/768/1280 keyboard/error recovery.
2. **P0 — Quality-gated dev→main promotion (pending exact-head CI).** Confirm exact SHA, PR diff, approvals/checks, ordinary merge only when green; then verify main/dev Quality and Pages, hosted interaction when supported.
3. **P1 — Weighted QR near-rank coefficient accuracy (planned; depends on QR).** Independent high-precision coefficients and residual/backward references at multiple near-rank separations, extreme weights and explicit rank failure; browser recovery.
4. **P1 — Bounded UI controller extraction (planned; depends on standalone build).** Preserve byte-identical offline bundle, project round-trip, keyboard/mobile accessibility and benchmark size.
5. **P1 — Scalar root aliasing hardening (planned; depends on root solver).** Paired oscillatory roots and discontinuities with honest sampling guidance, invalid-input and Chromium tests.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, living plan, frozen inventory, latest CI/Pages and synchronized branch heads `ef15565104ddf693ec403940ba8bc9f618fed8e4`. No open PR, exactly dev/main. Local git clone blocked by github.com DNS; connected GitHub source used. Added deterministic QR-reused RHS box sensitivity, offline bundle, analytical/eight-corner/negative and responsive Chromium tests, mandatory Quality step, ledger and changelog. V8 analytical and eight-corner checks passed before commit; exact-head CI and promotion pending. Historical 166 gaps/95 partials unchanged.

## 2026-11-02 — Weighted column-normalized design condition (MATH-WLS-COLNORM-095)

**Implemented on dev; exact-head CI, PR and Pages pending.** The bounded real 3×2 weighted least-squares calculator now reports the 2-norm condition after independently normalizing both weighted design columns to unit Euclidean length. For absolute column cosine c and sine s, use the stable ratio (1+c)/s instead of subtracting nearly equal Gram eigenvalues. This geometric near-dependence measure is invariant to positive individual column rescaling and common positive weight scaling; unlike the raw spectral condition, it does not incorporate column units. It is **not** a certified coefficient-error bound or statistical uncertainty.

**Prior release reconciled:** [PR #162](https://github.com/saeedsai/ProMathStudio/pull/162) merged, dev=main `9c27a104d8cd43cbf67043aabe74700b22d008ba`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41481062296) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41481060885) succeeded. [Post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41481080429) in progress at discovery; hosted interaction independently unverified; both branches unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Column-normalized condition exact-head QA and repair (in progress; depends on QR).** Analytic near-rank and orthogonal references, column and common-weight scale invariance, invalid/rank rejection, source/bundle parity, keyboard and Chromium 390/768/1280 recovery without runtime errors.
2. **P0 — Quality-gated dev→main promotion (pending exact-head CI).** Verify candidate SHA, PR diff/checks/approvals, ordinary merge only when green; then verify main/dev Quality, Pages and hosted behavior when supported.
3. **P1 — Near-rank weighted QR coefficient accuracy (planned; depends on QR).** Independent high-precision reference coefficients, residual/backward checks at several separations, extreme weights and explicit rank failure, browser recovery.
4. **P1 — Bounded UI controller extraction (planned; depends on standalone build).** Byte-identical bundle, project round-trip, keyboard/mobile and size benchmark.
5. **P1 — Scalar root aliasing hardening (planned; depends on numerical solver).** Oscillatory paired-root/discontinuity references, honest sampling guidance, invalid inputs and Chromium regressions.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, living plan, frozen audit, unified/engineering plans, latest branch heads and CI/Pages. Started synchronized dev/main `9c27a104d8cd43cbf67043aabe74700b22d008ba`, no open PR. Local git clone blocked by github.com DNS; used connected GitHub source. Added bounded column-normalized condition, offline bundle, focused numerical/negative and responsive Chromium tests, mandatory Quality step, plan, execution ledger and changelog. V8 analytical and scale-invariance checks passed before commit; full exact-head CI and release pending. Historical 166 gaps/95 partials unchanged.

## 2026-11-02 — Weighted design spectral condition (MATH-WLS-SPECTRAL-094)

**Implemented on dev; exact-head CI, PR and Pages pending.** The bounded real 3×2 weighted least-squares fit now estimates the 2-norm condition of the weighted design sqrt(W/max(W))·A using scaled column norms and a stable cross-product, without subtracting nearly equal small Gram eigenvalues. This quantifies near-rank numerical sensitivity, but is not a certified coefficient-error bound or statistical uncertainty; it depends on parameter units and column scaling. Existing rank checks, saved projects and offline distribution remain unchanged.

**Prior release reconciled:** [PR #161](https://github.com/saeedsai/ProMathStudio/pull/161) merged; dev=main `aa49c2121c16b6b5d170e5fbd94dd44efd928375`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41470848664), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41470867553) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41470846607) succeeded. Hosted interaction independently unverified; branches unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Spectral condition exact-head QA and repair (in progress; depends on QR).** Orthogonal, weighted, near-rank, column-scaled and extreme-weight analytical references, singular/invalid rejection, source/bundle parity, keyboard and Chromium 390/768/1280 recovery without runtime errors.
2. **P0 — Quality-gated dev→main promotion (pending exact-head CI).** Inspect exact candidate, diff and PR required checks, merge normally only when green, verify main/dev Quality and Pages deployment and hosted behavior where supported.
3. **P1 — Weighted QR near-rank coefficient accuracy (planned; depends on QR).** Compare solutions and backward residuals against independent analytic/high-precision references at several separations, or explicit rank failure; browser recovery.
4. **P1 — Bounded UI controller extraction (planned; depends on standalone build).** Preserve byte-identical build, project round-trip, keyboard/mobile and bundle-size benchmark.
5. **P1 — Scalar root aliasing hardening (planned; depends on numerical solver).** Oscillatory paired-root and discontinuity references, honest sampling guidance, invalid input and Chromium tests.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, plan, frozen inventory, unified and engineering plans, exact dev/main and latest CI/Pages. Started synchronized `aa49c2121c16b6b5d170e5fbd94dd44efd928375`, no open PR, exactly two unprotected branches. Local git clone blocked by github.com DNS resolution. Implemented numerical/UI changes, source/bundle parity, analytical/negative and mandatory responsive browser regressions, living plan and changelog. Exact-head CI and release verification pending.

## 2026-11-02 — Weighted log-weight sensitivity (MATH-WLS-WEIGHT-093)

**Implemented on dev; exact-head CI, PR and Pages pending.** Existing bounded real 3×2 weighted least-squares now reports each observation's local fitted-coefficient derivative with respect to log(weight), holding A, b and the other weights fixed. Reuses QR RHS response: d x / d log(w_i) = -response_i × (A_i x - b_i). Not an exact finite-weight-change prediction, statistical uncertainty or error bound. Added independent closed-form, central finite-difference, scale-invariance, exact-fit, near-rank and failure references, mandatory responsive Chromium, and standalone parity; saved-project schema unchanged.

**Prior release reconciled:** [PR #160](https://github.com/saeedsai/ProMathStudio/pull/160), dev=main `477037373264c1fc23cb855c3634a114798a77a5`, [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41461521241), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41461543539) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41461520878) succeeded. Hosted interaction unverified; branches unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Weight-response exact-head QA/repair (in progress; depends on QR).** Independent derivative, finite-difference, weight-scale invariance, zero residual, near-rank finite-or-reject, invalid weights, source/bundle parity and Chromium keyboard/mobile/recovery at 390/768/1280 without runtime errors.
2. **P0 — Quality-gated dev→main PR (pending CI).** Inspect exact dev SHA, diff, required checks and approvals, merge normally only when green, then verify main/dev Quality, Pages and hosted behavior when available.
3. **P1 — Near-rank QR accuracy (planned; depends on QR).** Compare near-dependent solutions to independent references, finite backward residual or explicit rank failure, extreme positive weights and responsive recovery.
4. **P1 — Bounded controller extraction (planned; depends on build).** Preserve standalone byte parity, saved-project round-trip, keyboard/mobile and bundle-size benchmark.
5. **P1 — Scalar-root aliasing hardening (planned; depends on numerical solver).** Oscillatory/discontinuous reference cases, missed-root guidance, invalid input and Chromium regressions.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, living plan, frozen inventory, unified/architecture plans, latest exact-head CI and Pages. Started synchronized dev/main `477037373264c1fc23cb855c3634a114798a77a5`, no open PR. Local git clone unavailable (github.com DNS resolution). Implemented QR-reused log-weight derivative, numerical and browser tests, workflow gate, offline bundle, ledger and changelog. Exact-head CI and release verification pending.

## 2026-11-02 — Relative-weight effective count (MATH-WLS-EFFN-092)

**Implemented on dev; exact-head CI/PR/Pages pending.** The bounded 3×2 weighted least-squares result reports a Kish-style relative-weight effective count, computed as (sum(w/max(w)))² / sum((w/max(w))²) to avoid overflow for permitted weights. It ranges from 1 to 3; when below 2, an advisory flags concentration on fewer than two equally weighted observations. This is descriptive weight concentration, **not** a statistically validated sample size, model residual degrees of freedom, condition number or uncertainty estimate. It never rejects otherwise valid fits. Offline standalone, keyboard controls and saved-project format are preserved.

**Prior release reconciled:** [PR #159](https://github.com/saeedsai/ProMathStudio/pull/159) merged; dev=main `c681eca8846c8b1c731c4608ebe3c045dbd810d2`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41451648477), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41451668193), [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41451647440) passed. Hosted browser behavior independently unverified; branches unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Effective weight count exact-head QA/repair (in progress).** Verify 3 for equal weights, 2.01994900255 for [1,1,0.01], concentration close to 1 for [1e8,1,1], weight-scale invariance, 1e24 allowed weight ratio, invalid/rank-deficient rejection, immutability, source/bundle parity and Chromium keyboard/mobile/error recovery at 390/768/1280px without runtime errors.
2. **P0 — Quality-gated dev→main promotion (pending CI).** Inspect exact dev SHA, PR diff and green required checks/approvals; ordinary merge only, then confirm main/dev Quality, Pages and hosted behavior when available.
3. **P1 — Near-rank weighted QR perturbation references (planned; depends on QR).** Compare coefficients for nearly dependent 3×2 matrices against independent analytic solutions; assert finite backward residuals or explicit rank failure and browser recovery.
4. **P1 — Bounded controller extraction (planned; depends on standalone build).** Extract one UI controller into src with byte-identical build, saved-project round trip, keyboard/mobile tests and bundle-size check.
5. **P1 — Audited scalar-root aliasing improvement (planned; depends on numerical solver).** Add oscillatory/discontinuous numerical references, explicit missed-root guidance, invalid-input and Chromium tests.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, unified/architecture plans, living plan, frozen inventory, exact heads and latest CI/Pages. Started synchronized dev/main `c681eca8846c8b1c731c4608ebe3c045dbd810d2` with no open PR. Implemented relative-weight concentration in existing QR-based 3×2 WLS, synchronized standalone HTML, added Node/structural and responsive Chromium regressions, registered mandatory Quality gate, updated changelog and this ledger. Local git clone unavailable (DNS), so full suite delegated to GitHub exact-head CI; promotion pending verification.

## 2026-11-02 — Weighted design column independence (MATH-WLS-SINE-091)

**Released via PR #159; verified dev=main c681eca8846c8b1c731c4608ebe3c045dbd810d2, green main/dev Quality and Pages.** The existing QR-based 3×2 weighted least-squares panel now displays the sine of the angle between weighted design columns. A normalized cross product avoids cancellation for near-parallel columns; the value is invariant under positive column rescaling and common positive weight scaling. At sine ≤ 1e-4, warn of possible coefficient sensitivity without rejecting otherwise valid fits. This is a heuristic, not a certified condition number, statistical uncertainty or error bound. Offline HTML, saved-project schema and actions remain unchanged.

**Prior release reconciled:** [PR #158](https://github.com/saeedsai/ProMathStudio/pull/158), dev=main `d77714614a49b79f8086e4786e4fabc45f7abda2`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41446512427), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41446526651) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41446511714) passed. Hosted browser interaction not independently verified; branches remain unprotected.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Exact-head column-sine QA/repair (in progress).** Verify analytic reference sqrt(1.05/2.0904), 1e-4 near-parallel geometry, positive column and common weight scale invariance, singular and invalid inputs, immutability, source/bundle parity and Chromium keyboard/mobile/error recovery at 390/768/1280px without runtime errors.
2. **P0 — Quality-gated dev→main promotion (pending CI).** Inspect exact SHA and PR diff/checks/approvals; ordinary merge only after green, then verify main/dev Quality, Pages and hosted behavior when possible.
3. **P1 — Weighted QR near-rank accuracy (planned).** Compare nearly dependent coefficients with independent analytic references, verify finite residuals or explicit rank failure, include browser recovery.
4. **P1 — Bounded UI controller extraction (planned).** Extract one inline controller into src, verify byte-parity offline build, project round-trip, keyboard/mobile and bundle size.
5. **P1 — Audited numerical/symbolic gap closure (planned).** Add one reusable missing capability with analytic, boundary, invalid and Chromium references.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, plan, inventory, architecture, branch heads and latest CI/Pages. Started synchronized dev/main `d77714614a49b79f8086e4786e4fabc45f7abda2`, no open PR. Added weighted design column-sine diagnostic, new Node/structural and Chromium regressions, standalone bundle sync, mandatory Quality gate and changelog. Local git clone unavailable (DNS); exact-head CI and promotion pending.

## 2026-11-02 — Weighted leave-one-out retained-row reliability (MATH-WLS-AREA-090)

**Implemented on dev; exact-head CI, PR and Pages pending.** The 3×2 weighted least-squares panel now reports the normalized determinant magnitude (geometric area) of the two rows retained after each observation is removed. Values are in [0,1], independent of row magnitudes and weights. Deletion predictions, residuals and coefficient shifts are unavailable if the retained-row area is ≤ 1e-8, avoiding misleading near-singular results. This is a numerical screen, not a certified condition number or statistical interval. No new buttons or saved-project schema changes.

**Prior release reconciled:** [PR #157](https://github.com/saeedsai/ProMathStudio/pull/157) merged with dev=main `4921caaab9c03481f57cb95e285bbca7924b32de`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41442802414), [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41442818112) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41442800826) passed. Hosted browser interaction remains independently unverified.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Exact-head retained-row QA/repair (in progress).** Verify normalized-area analytic references, near-parallel 1e-9 deletion guard, singular rows, weight and row scale invariance, invalid inputs, no mutation, source/bundle parity and responsive Chromium keyboard/error recovery at 390/768/1280px without runtime errors.
2. **P0 — Quality-gated dev→main promotion (pending exact-head green).** Inspect candidate diff and checks, open one dev→main PR, merge only after green PR Quality and required approvals, verify main/dev Quality, Pages and hosted behavior when available.
3. **P1 — Near-rank weighted QR reliability (planned; existing solver).** Compare full-fit coefficients against independent analytic near-dependent references, check extreme weight ratios and explicit failure paths.
4. **P1 — Bounded UI controller extraction (planned; standalone build).** Move one inline controller into src; require byte-parity rebuild, project save/reload, keyboard/mobile and bundle-size regressions.
5. **P1 — Audited mathematical gap closure (planned; frozen inventory).** Implement one reusable numerical or symbolic capability with analytic, boundary, invalid and Chromium references.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, living plan, frozen 166-gap/95-partial inventory, architecture and exact CI/Pages. Started synchronized dev/main `4921caaab9c03481f57cb95e285bbca7924b32de`, no open PR. Implemented normalized retained-row geometry, conservative near-rank guard, standalone sync, numerical and Chromium regressions, mandatory Quality gate, changelog and ledger. Exact-head CI/PR/Pages pending. Local git network access unavailable; no force-push or bypass.

## 2026-11-02 — Weighted leave-one-out predicted observations (MATH-WLS-PREDICTION-089)

**Implemented on dev; exact-head CI, PR and Pages pending.** The bounded 3×2 weighted least-squares result now displays each excluded-row prediction in original observation units as b_i plus the existing fitted-minus-observed leave-one-out residual. It reuses the QR kernel, does not add an action button, and preserves singular/high-leverage unavailable status. The guidance explains residual sign and the non-statistical interpretation. Offline HTML and saved-project schema preserved.

**Prior release reconciled:** [PR #156](https://github.com/saeedsai/ProMathStudio/pull/156), dev=main `2409311ea4d60eb7031b633aa88017427e388e8b`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41435243729), [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41435260602), [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41435242998) succeeded. Hosted interaction not independently verified; prior checks do not certify this change.

**NEXT FIVE concrete features (priority, dependencies, acceptance tests):**
1. **P0 — Predicted-value exact-head QA/repair (pending).** Direct-deletion predictions [-5,5,3], sign convention, weight scaling, singular/unavailable, invalid inputs, no input mutation, source/bundle byte parity, mandatory Chromium 390/768/1280px keyboard, recovery and no page errors.
2. **P0 — Safe dev→main promotion (blocked on exact-head CI).** Inspect exact diff, require green dev/PR Quality and approvals, ordinary PR merge, then verify main Quality, Pages and hosted critical path if reachable.
3. **P1 — Weighted near-rank reliability (planned; QR references).** Near-dependent 3×2 and extreme-weight tests; require independent reference agreement or explicit unavailable/failure diagnostics.
4. **P1 — Bounded controller extraction (planned; offline baseline).** Move one inline controller into src with deterministic standalone rebuild, saved-project round-trip, keyboard/mobile and bundle-size tests.
5. **P1 — Audited mathematical gap closure (planned; frozen inventory).** Implement a reusable missing numerical/symbolic operation with analytic reference, boundary/singular/invalid-input and Chromium tests.

**Execution log (2026-11-02 Europe/Stockholm):** Read AGENTS, unified plan, living plan, frozen audit and latest CI/Pages; started synchronized dev/main `2409311ea4d60eb7031b633aa88017427e388e8b`, no open PR. Added source/UI, structural/Node and Chromium tests, mandatory Quality step, standalone HTML and changelog. Exact-head CI/PR/Pages pending. Historical 166 gaps/95 partial features remain frozen baseline.

## 2026-11-02 — Weighted leave-one-out coefficient influence (MATH-WLS-DELETE-088)

**Implemented on dev; exact-head CI, PR and Pages pending.** For the bounded 3×2 weighted least-squares fit, show the two coefficient changes caused by removing each observation. Reuse QR RHS response and existing leave-one-out residual: Δβ_{(-i)} = (R⁻¹Qᵀ)_i × eᵢ/(1−hᵢ), with original observation scaling. An unavailable leave-one-out residual also makes the corresponding coefficient shift unavailable. This is fixed-design influence, not a confidence interval. Preserve the existing fit, offline HTML, project schema, and contextual actions.

**Prior release reconciled:** [PR #155](https://github.com/saeedsai/ProMathStudio/pull/155) merged with dev=main=`e07b5db8aa7023a7d14d1587fdcaae38f8b9ef80`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41424235311), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41424253455), and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41424234339) succeeded. Hosted interaction remains independently unverified; these checks do not certify this new change.

**NEXT FIVE concrete features (priority, dependency, acceptance tests):**
1. **P0 — Exact-head delete-one influence QA/repair (in progress; new source/test).** Run full structural/unit and Chromium suite; reference shifts [-5.942857,5.828571], [0.057143,2.828571], [0.057143,-0.171429] against direct refits; weight scaling, singular deletion, invalid weight, input immutability, source/bundle byte parity, 390/768/1280 keyboard and no-console-error checks.
2. **P0 — Quality-gated dev→main promotion (blocked until exact-head CI green).** Inspect PR diff, approvals and exact SHA checks; ordinary merge only; verify main Quality, Pages and hosted critical paths when reachable.
3. **P1 — Weighted near-rank conditioning (planned; QR references).** Probe near-dependent 3×2 designs with extreme positive weight ratios; require finite reference agreement or explicit rank failure, no misleading certified uncertainty.
4. **P1 — Reusable controller extraction (planned; offline parity).** Move one bounded inline controller into src; test project round-trip, keyboard/390px, unchanged contextual actions, deterministic standalone rebuild and size delta.
5. **P1 — Audited mathematical gap closure (planned; frozen inventory).** Deliver a reusable missing numerical/symbolic operation with analytic reference, invalid/singular/boundary cases and Chromium integration.

**Execution checkpoint (2026-11-02 Europe/Stockholm):** Started dev=main `e07b5db8aa7023a7d14d1587fdcaae38f8b9ef80`, no open PR; latest main/dev Quality and Pages succeeded. Read AGENTS, frozen audit, living plan, source and latest CI. Connector-side V8 direct-refit and singular reference checks passed. Source, standalone HTML, focused Node/Python and Chromium tests, Quality gate, ledger and changelog updated. Exact new-head CI/PR/Pages verification pending; no force-push or bypass. Frozen 166 gaps/95 partial features remain historical baseline.

## 2026-11-02 — Weighted leave-one-out predictive residuals (MATH-WLS-LOO-087)

**Implemented on dev; exact-head CI, PR and Pages pending.** The existing 3×2 QR weighted least-squares calculator now reports per-observation leave-one-out prediction residuals eᵢ/(1−hᵢ) and weighted prediction sum of squares (PRESS), reusing its existing leverage and fit without a duplicate solver. When removal of a row makes the remaining fit singular or numerically unreliable (1−hᵢ ≤ 1e-10), that residual and aggregate PRESS are explicitly unavailable. This is deterministic fixed-design cross-validation, not statistical uncertainty or a certified forward-error bound. Inputs, project schema, offline distribution and contextual buttons are unchanged.

**Reconciled prior release:** [PR #154](https://github.com/saeedsai/ProMathStudio/pull/154) merged with synchronized dev/main `9d1fcd13b5670ffed1f70fe8eab7ab00d522118c`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41421081531), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41421098787) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/41421081071) succeeded. Hosted interaction was not independently verified. These prior-head runs do not certify MATH-WLS-LOO-087.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — LOO exact-head QA and repair (pending).** Structural/Node references [-6,3,-6], weighted PRESS 45.36, direct two-row refits, common weight scaling, singular row-removal unavailable handling, invalid inputs and immutability; mandatory Chromium 390/768/1280, keyboard, error recovery and no console errors; byte-identical source/bundle rebuild.
2. **P0 — Safe dev→main release (blocked on exact-head QA).** Require green dev and PR Quality, inspect changed files and approvals, ordinary PR merge only, verify new main Quality, Pages build/deployment and hosted critical paths when reachable.
3. **P1 — Bounded controller extraction (planned; depends on parity baseline).** Extract one inline controller to src without duplicate UI actions; validate saved-project round-trip, keyboard/mobile, offline byte parity and bundle-size delta.
4. **P1 — Weighted near-rank conditioning (planned; depends on QR references).** Add reference tests for nearly dependent columns and extreme positive weights; reject numerical failures explicitly and avoid claiming certified coefficient uncertainty.
5. **P1 — Audited numerical/symbolic gap (planned; depends on inventory review).** Implement one reusable missing capability with reference, boundary, singular/invalid-input and Chromium tests.

**Execution log (2026-11-02 Europe/Stockholm):** Read root AGENTS, frozen audit, living plan, engineering architecture, latest PR/CI/Pages and both refs. Started dev=main `9d1fcd13b5670ffed1f70fe8eab7ab00d522118c`, only dev/main, no open PR. Added QR-based leave-one-out prediction diagnostics, Node/structural and mandatory Chromium tests, synchronized standalone HTML, changelog and this next-five ledger. Exact new-head CI and promotion still require verification; historical 166 gaps/95 partial features are unchanged.

## 2026-11-02 — Quarter-grid scalar-root aliasing reduction (MATH-ROOT-QUARTER-086)

**Implemented on dev; exact-head CI, PR and Pages pending.** The scalar root solver now uses at most two additional quarter-grid probes per coarse interval (20–1600 intervals), refining sign-changing subintervals with existing residual-certified bisection. This recovers some paired roots invisible at the original grid and midpoints. Probe counts and sign-changing subintervals are displayed. Finite-jump rejection, plateau classification, offline operation, saved-project fields and Newton seeds remain unchanged. This is bounded sampling, not globally complete root finding.

**Reconciled prior release:** [PR #153](https://github.com/saeedsai/ProMathStudio/pull/153) merged; dev=main=`b6776a3edc25efd078e54b9fbe07b582078f22e8`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41415975645), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41415994508) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/41415975228) succeeded. Hosted interaction is independently unverified; previous-head runs do not certify this new feature.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Quarter-grid exact-head QA/repair (pending).** Structural and mandatory Chromium: 0.205/0.218 hidden pair, 40 quarter probes for 20 intervals, strict residuals, jump/plateau cases, source/bundle parity, keyboard/390–1280px and error recovery; repair failures.
2. **P0 — Authorized dev→main release (blocked on QA).** Require green exact dev/PR checks, inspect diff, ordinary PR merge only, verify main Quality, Pages and hosted critical paths if reachable.
3. **P1 — Bounded UI controller extraction (planned; depends on parity).** Move one inline controller into src, verify offline rebuild byte parity, project round-trip, keyboard/mobile and bundle-size delta.
4. **P1 — Weighted near-rank diagnostics (planned; depends on QR references).** Validate nearly dependent 3×2 designs, extreme positive weights and perturbation sensitivity; explicit failure-path and numerical-scope tests.
5. **P1 — Audited mathematical gap closure (planned; depends on inventory).** Implement one missing reusable numerical/symbolic capability with reference, boundary, invalid-input and Chromium tests.

**Execution log (2026-11-02, Europe/Stockholm):** First dev Quality [run 41418421689](https://github.com/saeedsai/ProMathStudio/actions/runs/41418421689) failed an existing sampling regression: quarter probes recovered all 81 roots at 40 cycles, invalidating its former strict coarse/fine inequality. Kept that case as a positive quarter-probe reference and moved the strict density comparison to 60 cycles (>=120 fine roots); added focused regression rather than weakening the gate. Recheck exact new head CI. Read AGENTS, frozen inventory, living plan, architecture, and exact-head CI/CD. Started synchronized dev/main `b6776a3edc25efd078e54b9fbe07b582078f22e8` with no open PR. Added quarter-grid root subdivision, counters/UI, structural and browser tests, mandatory Quality registration, standalone parity and changelog. New CI/Pages verification pending. Historical 166 gaps and 95 partial features remain the baseline.

## 2026-11-02 — Weighted least-squares fixed-design RHS response (MATH-WLS-RHS-085)

**Implemented on dev; exact-head CI/PR/Pages pending.** The 3×2 weighted least-squares solver now reuses its existing QR factor to report the two fitted coefficient changes per +1-unit change in each observation b, with A and positive weights held fixed. For A=[[1,0],[1,1],[1,2]], weights [1,1,0.01], the row responses are [104/105,-102/105], [2/105,99/105], [-1/105,3/105]. The response is a fixed-design linear map, not a probability, certified condition number, statistical uncertainty or error bound. No new action buttons, project fields or duplicated numerical engine.

**Last verified release before this change:** [PR #152](https://github.com/saeedsai/ProMathStudio/pull/152) merged at dev=main=`0b30b2dca183144dcb2a03eccf817e38a8e1ea33`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41404609732), [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41404622243) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/41404609367) succeeded. Hosted interaction remains independently unverified. These previous-head runs do not certify MATH-WLS-RHS-085.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — RHS-response exact-head QA/repair (pending).** New unit and mandatory Chromium tests: 104/105, -102/105, 2/105, 99/105, -1/105, 3/105 references; compare to actual perturbed b, positive weight-scale invariance, rank/weight rejection, input immutability, source/bundle parity, no page errors, keyboard and 390/768/1280px recovery.
2. **P0 — Authorized dev→main promotion (blocked on QA).** Require green exact dev and PR Quality, inspect diff and approvals, merge only via ordinary dev→main PR, verify main Quality, Pages deployment and hosted interaction if reachable.
3. **P1 — Bounded UI controller extraction (planned; depends on parity checks).** Move one inline controller into src without adding duplicate controls; byte-identical offline rebuild, saved-project round-trip, keyboard/mobile tests and size benchmark.
4. **P1 — Root aliasing diagnostics (planned; depends on root test baselines).** Add bounded oscillatory sampling guidance with paired-root/finite-jump reference tests, no global-completeness claims, and responsive recovery.
5. **P1 — Audited numerical gap closure (planned; depends on inventory review).** Implement one reusable missing numerical or symbolic capability with numerical reference, singular/boundary and invalid-input tests, Chromium integration and exact-head CI.

**Execution log (2026-11-02, Europe/Stockholm):** Read AGENTS, living plan, frozen inventory, architecture/catalog and latest Quality/Pages. Starting dev=main=`0b30b2dca183144dcb2a03eccf817e38a8e1ea33`, only dev/main, no open PR. Implemented QR-based response, structural/Node and browser regressions, mandatory Quality registration, offline bundle synchronization and changelog; awaiting exact-head CI before any release claim. Historical 166 gaps and 95 partial features remain the frozen audit baseline.

## 2026-11-02 — Weighted-design observation leverage (MATH-WLS-LEVERAGE-084)

**Released via PR #152; main/dev Quality and Pages succeeded at `0b30b2dca183144dcb2a03eccf817e38a8e1ea33`.** Reuses the existing reorthogonalized QR factor of the 3×2 weighted design to report each observation's diagonal projection leverage (Q-row squared norm). The three leverage values lie approximately in [0,1] and sum to the two fitted parameters; uniform positive weight scaling preserves them. This is a *fixed-design influence diagnostic*, not an outlier probability, coefficient uncertainty or certified conditioning bound. Existing relative weights, full-rank constraints, offline standalone build and saved-project behavior are unchanged.

**Last verified deployment:** [PR #151](https://github.com/saeedsai/ProMathStudio/pull/151) merged at dev=main=`8092022f5f558ca6b9056cb86fa1cb7c2becf163`; [Pages build/deployment 41402320026](https://github.com/saeedsai/ProMathStudio/actions/runs/41402320026) succeeded. Post-merge main/dev Quality runs 41402320481/41402334929 were in progress when this change began; these previous-head runs do not certify MATH-WLS-LEVERAGE-084. Hosted interactions remain independently unverified.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Weighted leverage exact-head QA/repair (pending).** Mandatory structural/unit and Chromium on exact dev SHA; 104/105, 101/105, 1/21 reference; leverages sum to 2, positive-scale invariance, extreme-weight finite values, rank/weight rejection, source/bundle parity, no page errors, keyboard and 390/768/1280px recovery.
2. **P0 — Authorized dev→main promotion (blocked on QA).** Inspect exact diff, require green dev and PR Quality plus required approvals, ordinary PR merge, verify main Quality and Pages for the merge SHA, attempt hosted critical path.
3. **P1 — Bounded UI controller extraction (planned).** Extract one inline controller into src; assert standalone build byte parity, saved-project round-trip, keyboard/mobile navigation and bundle size.
4. **P1 — Weighted least-squares perturbation experiments (planned).** Add reference RHS perturbation comparisons, near-rank/extreme-weight failure behavior, fixed-weight leverage interpretation and accessible warnings without uncertified error bounds.
5. **P1 — Audited mathematical gap closure (planned).** Select highest-priority reusable missing numerical/symbolic feature with reference, boundary, singularity, invalid-input and Chromium tests.

**Execution checkpoint (2026-11-02 07:54 Europe/Stockholm):** Read AGENTS, living plan, frozen inventory, latest CI/Pages and dev/main heads; only dev/main, no open PR, synchronized at `8092022f5f558ca6b9056cb86fa1cb7c2becf163`. Local git DNS unavailable; connector-side numerical JS references passed. New source, standalone bundle, focused Python/Node and Chromium tests, mandatory Quality step and documentation staged for atomic dev commit. No branch protections or checks bypassed. Historical 166 gaps/95 partials remain the audit baseline.

## 2026-11-02 — Bounded midpoint subgrid root recovery (MATH-ROOT-MIDPOINT-083)

**Implemented on dev; exact-head CI and release pending.** Scalar root sampling now probes one midpoint per coarse interval and bisects each finite half-interval independently, recovering some pairs of crossings hidden by equal-sign coarse endpoints. It reports midpoint probe and opposite-sign interval counts in the accessible Numerical Methods output. It retains finite-residual acceptance, discontinuity rejection, plateau classification, 20–1600 sampling bounds, offline standalone parity and saved-project compatibility. Midpoint probes cannot guarantee all roots, and additional evaluations are bounded by the configured interval count.

**Last verified release:** [PR #150](https://github.com/saeedsai/ProMathStudio/pull/150), dev=main=`86aedc4d01e3f49d8be01390de23e813e2a80d64`; [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41399058668), [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41399073563) and [Pages deployment](https://github.com/saeedsai/ProMathStudio/actions/runs/41399057924) succeeded on that previous SHA. Hosted interaction remains independently unverified. These runs do not certify MATH-ROOT-MIDPOINT-083.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Midpoint exact-head QA/repair (pending).** Full structural/unit and mandatory Chromium at exact dev SHA, paired roots 0.21/0.24 in one coarse interval, finite-jump rejection, plateau, ordinary/tiny roots, offline parity, no page errors, keyboard and 390/768/1280px recovery.
2. **P0 — Authorized dev→main promotion (blocked on QA).** Inspect exact diff, require green dev and PR Quality plus required approvals, ordinary PR merge, verify exact main Quality and Pages, attempt hosted critical path.
3. **P1 — Reusable bounded UI controller extraction (planned).** Extract one remaining inline controller into src, preserve offline build parity, saved-project round-trip, keyboard/mobile behavior and measure bundle/load budget.
4. **P1 — Weighted least-squares perturbation screening (planned).** Near-rank and extreme-weight reference tests, finite stable results or explicit failure, negative/recovery Chromium and no unsupported uncertainty claim.
5. **P1 — Next audited mathematical gap (planned).** Implement highest-priority feasible reusable numerical/symbolic capability with reference, singularity, invalid-input and responsive Chromium regressions.

**Regression reconciliation (2026-11-02):** [dev Quality 41400393150](https://github.com/saeedsai/ProMathStudio/actions/runs/41400393150) passed the new midpoint smoke and earlier checks, then exposed an outdated oscillatory regression assumption: the 20-interval coarse grid now finds 55 roots (previously fewer) and the 800-interval grid finds 81. Updated the existing regression to require at least 40 coarse roots and at least 80 fine roots with fine strictly greater than coarse, preserving numerical coverage while recognizing improved coarse-grid recovery. Exact-head full CI must be rerun.

**QA repair (2026-11-02):** [dev Quality 41399943211](https://github.com/saeedsai/ProMathStudio/actions/runs/41399943211) passed structural/unit and earlier Chromium steps but failed the new smoke's exact decimal text assertion: the valid 0.24 root displayed as 0.2399999976158 with residual 7.153e-11. Replaced the brittle display substring check with numeric tolerance checks on parsed displayed roots, preserving the direct reference and finite-residual tests. A new exact-head CI run is required before promotion.

**Execution checkpoint (2026-11-02 07:24 Europe/Stockholm):** Started dev=main=`86aedc4d01e3f49d8be01390de23e813e2a80d64`, no open PR, only dev/main. Read current AGENTS, living plan, frozen inventory and exact-head Quality/Pages evidence. Local GitHub DNS unavailable; connector-based atomic dev commit and GitHub Actions are the QA path. Historical 166 gaps/95 partial features remain the frozen baseline.

## 2026-11-02 — Underflow-safe scalar root bracketing (MATH-ROOT-SIGN-082)

**Released via PR #150 at `86aedc4d01e3f49d8be01390de23e813e2a80d64`.** Bisection compares signs of finite residuals directly rather than multiplying residuals, which can underflow to zero for very small nonzero function values and silently skip real roots. The existing absolute-residual gate still rejects finite jumps; no global completeness claim. Adds source/bundle parity and focused Chromium tiny-scale reference, discontinuity, keyboard/focus and 390/768/1280px recovery tests.

**Last verified release:** [PR #149](https://github.com/saeedsai/ProMathStudio/pull/149), dev=main=`185ec735ba66354999560b5e4bef4bb395ba3692`. [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41393095448), [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41393103474), [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41393094371) succeeded for this prior SHA; hosted interactions not independently certified.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Underflow-safe bracketing exact-head QA (pending).** Full mandatory Python and Chromium at the exact dev SHA; reference `10^(-100)*10^(-100)*(x-0.123456789)`, 1e-211 tolerance, finite jump rejection, ordinary roots, offline parity, accessible 390/768/1280px recovery and no page errors.
2. **P0 — Quality-gated dev→main promotion (blocked on QA).** Inspect exact diff, require green dev/PR checks and approvals, ordinary PR merge; confirm exact main Quality and Pages, attempt hosted critical path.
3. **P1 — Bounded UI controller extraction (planned).** Extract one controller into `src/`; verify offline rebuild parity, saved-project round-trip, keyboard/mobile navigation and bundle-size budget.
4. **P1 — Weighted least-squares perturbation screening (planned).** Near-rank and extreme-weight numerical reference tests; stable finite outputs or explicit failures, responsive UI and negative recovery.
5. **P1 — Oscillatory root subgrid diagnostics (planned).** Evaluate bounded midpoint probes against high-frequency aliasing, finite jumps and even roots; reference/negative/browser tests and explicit non-completeness messaging.

**Execution checkpoint (2026-11-02 06:57 Europe/Stockholm):** Started dev=main=`185ec735ba66354999560b5e4bef4bb395ba3692`, no open PR; verified prior Quality and Pages success, read AGENTS, plan and frozen audit. Local git DNS unavailable; GitHub connector used for atomic dev commit. Frozen 166 gaps/95 partial features remain baseline.

## 2026-11-02 — Two-scale cusp root diagnostics (MATH-ROOT-CUSP-081)

**Implemented on dev; exact-head CI and release pending.** Root diagnostics compare opposing one-sided secants at full and half step before flagging possible non-smooth cusps. Smooth tangential `x^2` is not flagged merely for opposite slopes; `abs(x)` and `sqrt(abs(x))` are screened. Per-root `localSlopeWarnings` and accessible UI count are heuristic, not differentiability certificates. Plateau metadata remains empty, one-sided domain estimates remain intact; global root completeness is not claimed.

**Last verified release:** [PR #148](https://github.com/saeedsai/ProMathStudio/pull/148), dev=main=`c232baaa8ace883fd0fddf0f65a8ee61e7133ff0`. [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41387579757), [post-merge dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41387588999), [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41387579556) succeeded for prior SHA only; hosted interactions not independently certified.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Cusp exact-head QA (pending).** Full structural and mandatory Chromium at precise dev SHA; `abs(x)`, `sqrt(abs(x))`, `x^2`, `x^4`, `sqrt(x)`, jump/plateau, offline parity, no page errors, 390/768/1280px recovery.
2. **P0 — Quality-gated dev→main release (blocked on QA).** Inspect exact diff, green dev/PR checks and required approvals; ordinary PR merge then exact main Quality and Pages verification.
3. **P1 — Bounded controller extraction (planned).** Modularize one UI controller with standalone rebuild, saved-project round-trip, keyboard/mobile and size budget tests.
4. **P1 — Weighted least-squares perturbation sensitivity (planned).** Near-rank/weight-scaling references, stable results or explicit error, negative and mobile tests.
5. **P1 — Audited numerical gap closure (planned).** Select reusable solver gap; numerical reference, singularity, invalid input and Chromium tests.

**Execution checkpoint (2026-11-02 06:01 Europe/Stockholm):** Started dev=main=`c232baaa8ace883fd0fddf0f65a8ee61e7133ff0`, no open PR, prior exact-head Quality/Pages green. Read AGENTS, plan, frozen audit and current source/tests. Local git DNS unavailable; GitHub connector used for atomic dev tree/commit. Historical 166 gaps/95 partial features remain baseline.

## 2026-11-02 — One-sided real-domain root sensitivity (MATH-ROOT-ONE-SIDED-080)

**Implemented on dev; exact-head CI and release pending.** Scalar root sensitivity now uses forward/backward secants where the opposite evaluation is outside the real-valued domain or at the search boundary. Per-root `localSlopeMethods` aligns with existing magnitudes, UI counts one-sided estimates, and guidance explicitly warns these are not differentiability proofs or certified root-position bounds. Constant sampled plateaus remain unclassified as discrete roots. Standalone parity and focused structural and mandatory Chromium positive/negative/mobile/recovery tests added.

**Last verified release:** [PR #147](https://github.com/saeedsai/ProMathStudio/pull/147), dev=main=`28e48d01f3c90b845bf29fa63d9525f55af61116`. [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41382316282), [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41382303540) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41382302511) succeeded for prior SHA only. Hosted interactions not independently verified.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — One-sided root exact-head QA (pending).** Full Python/Chromium green at precise dev SHA; `sqrt(x)`, `sqrt(-x)`, linear center, plateau/jump, offline parity, errors and 390/768/1280px recovery with no console errors.
2. **P0 — Quality-gated dev→main release (blocked on QA).** Review exact diff and approvals, green dev/PR checks, ordinary PR merge, verify main Quality, Pages and hosted keyboard path if reachable.
3. **P1 — Cusp root diagnostics (planned).** Detect misleading non-smooth secants without false positives on smooth tangential roots; test `abs(x)`, `x^2`, `sqrt(abs(x))`, invalid domains.
4. **P1 — Bounded controller extraction (planned).** Extract one inline controller to `src/`; offline parity, saved-project round-trip, keyboard/mobile, size/startup budget.
5. **P1 — Audited math gap closure (planned).** Highest-priority reusable missing numerical/symbolic capability with reference, singularity, invalid-input and Chromium regressions.

**Execution checkpoint (2026-11-02 04:59 Europe/Stockholm):** Began dev=main=`28e48d01f3c90b845bf29fa63d9525f55af61116`, no open PR and only dev/main; read AGENTS, living plan, frozen audit, engineering architecture and latest Quality/Pages. Local git DNS unavailable, so used GitHub connector for dev commit. Historical 166 gaps/95 partial capabilities unchanged.

## 2026-11-02 — Weighted least-squares sensitivity screening (MATH-WLS-CONDITION-079)

**Released via PR #147 at `28e48d01f3c90b845bf29fa63d9525f55af61116`.** Reuse the existing least-squares QR factorization to report the weighted design's QR diagonal spread (a screening heuristic, **not** a condition number), and the maximum/minimum positive relative-weight ratio. Extreme weights or a large QR diagonal spread trigger a sensitivity advisory without asserting coefficient-error bounds or statistical uncertainty. Existing weighted 3×2 full-rank scope, coefficient and residual calculations, standalone offline bundle, saved projects and exports are preserved. Added direct numerical, source/bundle and mandatory Chromium reference, scale-invariance, near-rank, extreme-weight, negative, keyboard and 390/768/1280px recovery regressions.

**Last verified release:** PR [#146](https://github.com/saeedsai/ProMathStudio/pull/146), dev=main=`3d69142c61f5ba3152ffba36cf7ddd75e0d8bd29`. [dev Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41376385760), [main Quality](https://github.com/saeedsai/ProMathStudio/actions/runs/41376371493) and [Pages](https://github.com/saeedsai/ProMathStudio/actions/runs/41376371189) succeeded on that earlier SHA. These do **not** certify this change. Hosted interaction unverified.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Exact-head weighted-conditioning QA and repairs (pending).** Full Python structural/numerical suite and all Chromium smoke tests green at precise dev SHA; verify extreme ratio 1e24, common-scale invariance, rank rejection, offline parity, no console errors and mobile recovery; fix failures without weakened assertions.
2. **P0 — Authorized dev→main release (blocked on QA).** Inspect exact diff, obtain green dev/PR Quality and required approvals, ordinary PR merge, verify main Quality, Pages deployment and hosted keyboard path when reachable.
3. **P1 — Bounded controller extraction (planned).** Extract one inline controller to src, preserve byte-identical standalone rebuild, saved-project round-trip, keyboard/mobile navigation and measure bundle/load budget.
4. **P1 — Root-conditioning robustness (planned).** Test near-flat and boundary roots, unavailable slopes and discontinuities; keep residual-vs-position-error warning and error recovery.
5. **P1 — Audited math gap closure (planned).** Select highest-priority reusable missing numerical/symbolic capability; reference, singularity, invalid-input and browser tests before release.

**Execution checkpoint (2026-11-02 04:00 Europe/Stockholm):** Began dev=main=`3d69142c61f5ba3152ffba36cf7ddd75e0d8bd29`, no open PR; inspected current AGENTS, plan, frozen audit, engineering architecture/catalog and successful prior exact-head Quality/Pages. Local git clone failed DNS resolution; GitHub connector used for source and CI. Source, standalone, tests, workflow, changelog and ledger prepared for dev. Historical 166 gaps and 95 partial capabilities remain baseline.

## 2026-11-02 — Configurable scalar root sampling and aliasing advisory (MATH-ROOT-SAMPLING-078)

**Implemented on dev; exact-head CI and release pending.** Numerical Methods scalar roots now expose 20–1600 integer sampling intervals (default 350), report actual grid spacing, and warn that oscillatory and even-multiplicity roots may be missed. Invalid/noninteger inputs focus the field and announce an error; other methods hide the scalar-only control. The existing solver, plateau classification, residual validation, offline bundle, table exports and saved-project schema remain unchanged. Added structural parity and mandatory Chromium coarse/fine oscillatory, finite-jump, negative, mobile and recovery regressions. No global completeness claim.

**Verified previous release:** PR [#145](https://github.com/saeedsai/ProMathStudio/pull/145) merged; dev=main=`5710613b028ba217d85f4e0dc96c86ff71c86620`; [dev Quality 41371585900](https://github.com/saeedsai/ProMathStudio/actions/runs/41371585900), [main Quality 41371574116](https://github.com/saeedsai/ProMathStudio/actions/runs/41371574116), and [Pages 41371573363](https://github.com/saeedsai/ProMathStudio/actions/runs/41371573363) succeeded at that prior SHA. These checks do not certify the new change. Hosted-site interaction unverified.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Sampling exact-head QA and repairs (pending).** Full Python and Chromium Quality at precise dev SHA; coarse/fine oscillatory reference, invalid integer/range/empty recovery, plateau/jump, 390/768/1280px, offline parity; fix without weakening tests.
2. **P0 — Quality-gated dev→main release (blocked on QA).** Inspect one PR diff/approvals, green dev/PR Quality, ordinary merge, exact-main Quality and Pages, hosted interaction if reachable.
3. **P1 — Bounded inline controller extraction (planned).** Move one UI controller to src; offline rebuild parity, saved-project round trip, keyboard/mobile and bundle-size budget.
4. **P1 — Weighted least-squares conditioning (planned).** Extreme positive weight ratios and nearly rank-deficient design references; finite validated coefficients or explicit failure, mobile recovery.
5. **P1 — Root-conditioning robustness (planned).** Near-flat/unavailable slopes, boundary roots and discontinuity references; avoid certified root-position claims.

**Execution log (2026-11-02 02:54 Europe/Stockholm):** Began dev=main=`5710613b028ba217d85f4e0dc96c86ff71c86620`, two branches, no open PR. Read AGENTS, frozen 166-gap/95-partial inventory, living plan, engineering architecture/catalog and latest Quality/Pages evidence. Local git DNS unavailable; source, standalone, focused tests, Quality registration, changelog and ledger prepared via GitHub connector. Exact-head CI and authorized PR/Pages verification required before release. Historical counts unchanged.

## 2026-11-02 — Residual-first scalar root bracket refinement (MATH-ROOT-BRACKET-077)

**Implemented on dev; exact-head CI and release pending.** Fixed a numerical false-negative for steep scalar functions: bisection no longer stops just because the x-interval width is smaller than the requested function-residual tolerance. It now refines until the actual residual meets tolerance or floating-point spacing prevents further progress. Residual certification after rounding is unchanged, so finite jumps cannot be accepted as roots merely because they have a narrow sign-change bracket. The existing plateau and slope heuristics, saved-project schema, numerical table export and offline bundle are preserved. Added direct source/bundle and mandatory Chromium regressions for steep off-grid roots, endpoint roots, smooth/tangential roots, finite-jump rejection, invalid-input recovery and responsive layouts. This does not certify global root completeness or root-position error.

**Latest verified baseline:** PR #144 merged; dev=main=`2683d3d1656ec79288801eac4cf004056801936b`; dev Quality [41366098559](https://github.com/saeedsai/ProMathStudio/actions/runs/41366098559), main Quality [41366085539](https://github.com/saeedsai/ProMathStudio/actions/runs/41366085539) and Pages [41366084962](https://github.com/saeedsai/ProMathStudio/actions/runs/41366084962) succeeded for that prior commit, not for this feature.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Exact-head root bracket QA and repairs (pending).** Python unit/structural and all Chromium regressions green at precise dev SHA, including steep root residual ≤1e-9, both endpoint roots, jump rejection, mobile recovery, offline rebuild parity; inspect failed steps and repair without weakening checks.
2. **P0 — Quality-gated dev→main promotion (blocked on exact-head QA).** One authorized PR, green candidate and PR checks, inspect diff and approvals, ordinary merge, verify main Quality and Pages for exact merge SHA and hosted interaction if reachable.
3. **P1 — Bounded inline controller extraction (planned).** Extract one source controller with identical standalone rebuild, saved-project round trip, keyboard/mobile behavior and measured bundle/load budget.
4. **P1 — Oscillatory root sampling advisory (planned).** Reference cases for high-frequency aliasing and finite jumps, clear UI sampling-limit message and regression tests; never claim all roots found.
5. **P1 — Weighted least-squares conditioning (planned).** Extreme positive weight ratios and nearly rank-deficient designs must yield finite validated coefficients/residuals or explicit failure; test recovery and do not imply statistical uncertainty estimates.

**Execution log (2026-11-02 02:00 Europe/Stockholm):** Starting dev/main at `2683d3d1656ec79288801eac4cf004056801936b`, two branches and no open PR. Local Git checkout could not resolve github.com; exact-head GitHub Actions is the full QA gate. New source, standalone bundle, focused structural and Chromium tests, Quality registration and changelog prepared as one dev commit. Do not mark Released until exact-head CI, PR and Pages evidence are recorded. Historical 166 gaps and 95 partial features remain audit baseline.

## 2026-11-02 — Weighted least-squares guidance and scale invariance (MATH-WLS-GUIDANCE-076)

**Implemented on dev; exact-head CI, PR and Pages pending.** The Matrix Calculator now explains the 3×2 full-column-rank requirement, strictly positive bounded relative weights, common-weight rescaling, units, and the distinction between relative priorities and certified uncertainty estimates. Weight fields refer to the guidance via `aria-describedby`. Added a direct Node numerical regression for 3×2 reference coefficients, positive common-weight scaling invariance (and corresponding weighted SSE scaling), rank-deficient rejection, invalid weights, and no input mutation. Added mandatory Chromium regression for accessible guidance at 390/768/1280px, scale invariance, rank error and recovery. The pure QR solver and saved-project schema are unchanged. Prior release MATH-ROOT-CONDITIONING-075 was verified: dev=main=`ac447b6d810267d1936e1608e88e3bf27d5c71c2`; dev Quality 41361274802, main Quality 41361263908, Pages 41361263801 all succeeded. These earlier runs do not certify this new feature.

**NEXT FIVE concrete features (status, dependencies, acceptance tests):**
1. **P0 — Exact-head WLS guidance QA and repair (pending).** Full Python structural/unit and Chromium suites green at precise dev SHA; verify Node scale/rank/invalid references and 390/768/1280px guidance, inspect failing logs and repair without weakened checks.
2. **P0 — Authorized dev→main release and Pages verification (blocked on QA).** Review diff, require green dev and PR checks and approvals, merge only through ordinary PR, verify main Quality, Pages on exact merge SHA and hosted keyboard path if reachable.
3. **P1 — Bounded inline controller extraction (planned).** Extract one source module, retain byte-identical offline rebuild, project round trip and keyboard/mobile behavior; compare bundle size and load timing.
4. **P1 — Root boundary and oscillatory sampling (planned).** Add boundary-root and off-grid oscillatory reference/negative tests, distinguish sampling limits and finite jumps, and maintain no global-completeness claim.
5. **P1 — Weighted least-squares numerical conditioning (planned).** Investigate highly unequal positive weights and near-rank-deficient designs; assert stable references or explicit failure, finite residuals, no false statistical confidence claims, and mobile recovery.

**Execution checkpoint:** Starting dev/main synchronized at `ac447b6d810267d1936e1608e88e3bf27d5c71c2`, no open PR. Local git checkout blocked by DNS, so exact-head GitHub Actions remains the full regression gate. No branch creation, protection change, force-push or deletion. Historical 166 gaps and 95 partial features remain frozen baseline.

## 2026-11-02 — Scalar root conditioning advisory (MATH-ROOT-CONDITIONING-075)

**Implemented on dev; exact-head Quality, PR and Pages pending.** Added aligned local finite-difference secant slope magnitudes to certified scalar root candidates, with a minimum finite slope summary and accessible UI output. This is a scale-dependent sensitivity heuristic, not a root-position error bound; discontinuities, flat roots, and missed roots remain limitations. Plateau and no-root cases report null/empty diagnostics. Existing absolute residual certification, saved projects, and numerical Data Tables export remain unchanged. Added structural source/bundle parity regression and mandatory Chromium reference tests for x²−2, x³, steep 10⁶(x−0.5), finite jump rejection, zero plateau, invalid-domain recovery and live status. Previous ENG-CATALOG-WLS-074 release verified on 2026-11-01: dev=main=`f47974b248eddea1b28b8361a42a03df20dd2727`, main Quality 41356207152, dev Quality 41356220030 and Pages 41356206798 all succeeded; those checks do not certify this new change.

**NEXT FIVE concrete features (status, dependencies and acceptance tests):**
1. **P0 — Verify exact-head conditioning QA (pending).** Full structural/unit suite and all Chromium tests pass for the new dev SHA, including residual, plateau, slope guidance, keyboard and mobile cases; diagnose and fix any failing step without weakening coverage.
2. **P0 — Quality-gated dev→main release (blocked on QA).** Review exact diff, confirm dev and PR checks plus any required approvals, merge only through authorized PR, verify main Quality and Pages on the merge SHA; hosted interaction test when reachable.
3. **P1 — Weighted least-squares input guidance (planned).** Explain positive relative weights, rank and units; test uniform weight scaling invariance, rank-deficient rejection and mobile error recovery.
4. **P1 — Extract another bounded inline controller (planned).** Keep offline index byte-identical to rebuild, preserve project round-trip and public API, verify keyboard/browser behavior and measured size budget.
5. **P1 — Root sampling/conditioning edge cases (planned).** Test boundary roots, oscillatory aliasing and discontinuity probes; do not assert completeness or location-error bounds.

**Execution checkpoint:** Existing dev/main heads and prior Quality/Pages verified; one bounded mathematical correctness advisory prepared. No branches or protection changes. Historical 166 gaps and 95 partial features remain the audit baseline.

## 2026-11-01 — Canonical weighted least-squares Engineering routing (ENG-CATALOG-WLS-074)

**Implemented on dev; exact-head CI, PR and Pages release pending.** Added unique `matrix.weighted-least-squares.real.3x2` to the Engineering Toolbox, focusing the existing `mat-weighted-least-squares` Matrix Calculator action without executing it or overwriting drafts. Reuses the QR-based weighted solver for real 3×2 full-column-rank systems with three strictly positive relative observation weights (1e-12 through 1e12); does not claim uncertainty estimates, statistical confidence intervals, or arbitrary matrix dimensions. Synchronized `src/engineering-catalog.js` and standalone `index.html`. New `tests/test_engineering_weighted_route.py` verifies unique metadata, offline parity and canonical solver reuse; new mandatory Chromium `tests/smoke_engineering_weighted_route.py` verifies 390/768/1280px keyboard routing, solution [33/35,41/35], weighted squared residual 12/35, zero-weight rejection, recovery and wrong-dimension rejection. Starting heads dev=main=`cb79b243535b8fae31c3b5bdb59e6c15676eb8f1`; previous Quality and Pages successful for that previous release only. Local Git access blocked by DNS; no claim of new-head full QA until GitHub confirms it.

**NEXT FIVE concrete features (dependencies and acceptance tests):**
1. **P0 — Exact-head weighted-route QA/repair (pending CI).** All Python unit/structural and Chromium steps green on precise dev SHA, including weighted 3×2 reference, invalid-weight and mobile recovery; fix failing root causes without weakening tests.
2. **P0 — Ordinary dev→main PR and Pages promotion (blocked on QA).** Review complete diff, require exact-head dev and PR Quality/approvals, merge only through authorized PR, verify main Quality and Pages deployment for merge SHA and hosted keyboard path when reachable.
3. **P1 — Root-conditioning advisory (planned).** Distinguish absolute function residual from root-position error; verify flat/steep functions, finite jumps and accessible diagnostic without false accuracy bounds.
4. **P1 — Bounded inline-controller extraction (planned).** Preserve byte-identical offline build, saved-project round trip, public API, keyboard/mobile behavior and measured bundle/load budget.
5. **P1 — Engineering least-squares input guidance (planned).** Explain relative weights and full-rank domain, add 3×2 rank-deficient/scale-invariance reference tests, error recovery and accessible inline guidance.

**Execution checkpoint:** one bounded route and focused tests prepared, no branch creation or protection changes; exact dev/main SHAs, Quality and Pages status to be reconciled after remote checks. Frozen 166 gaps and 95 partial features remain the historical audit, not completion evidence.

## 2026-11-01 — Canonical symmetric eigenanalysis focus routing (ENG-CATALOG-EIGEN-073)

**Implemented on dev; exact-head Quality/PR/Pages pending.** The existing matrix.eigen.symmetric.small Engineering Toolbox entry now focuses the real symmetric Jacobi eigenanalysis action mat-eigen in the Matrix Calculator. No solver is duplicated, no computation runs on navigation and calculator draft inputs are preserved. Scope remains real symmetric 2×2/3×3 only; general nonsymmetric/complex eigenproblems are not claimed. Synchronized src/engineering-catalog.js and offline index.html. New tests/test_engineering_eigen_route.py and mandatory Chromium tests/smoke_engineering_eigen_route.py cover unique route ID, Enter-to-focus, 390/768/1280px layouts, reference eigenvalues [4,3,1] for [[2,1,0],[1,2,0],[0,0,4]], residual/orthogonality, nonsymmetric and empty-input rejection, and recovery. Initial baseline: dev=main=b67741abf4df3ea8ab8d0766efbda1fa74ee1676, previous dev/main Quality 41345987694/41345977604 and Pages 41345977087 succeeded (prior release only). Connector-side source/bundle parity checked; full new commit CI and production deployment must be verified separately. Local git clone unavailable because github.com DNS resolution failed. Historical 166 gaps and 95 partial features remain frozen baseline.

**NEXT FIVE concrete features and acceptance tests:**
1. **P0 — Exact-head eigen QA and repair (in progress).** Require full Python structural/unit and all Chromium smokes green at precise dev SHA; inspect failures and repair root causes without weakening checks.
2. **P0 — Verified dev→main PR and Pages promotion (blocked until QA).** Check exact-head dev and PR Quality, approvals, reviewed diff, ordinary PR merge, main Quality and Pages success; hosted keyboard path if reachable.
3. **P1 — Root-conditioning diagnostic guidance (planned).** Distinguish |f(x)| residual from unknown root-position error, test flat/steep roots and discontinuity rejection with accessible status messaging.
4. **P1 — Bounded inline controller extraction (planned).** Preserve offline rebuild byte parity, public API, project round-trip, responsive keyboard and size/load budget with unit and Chromium tests.
5. **P1 — Canonical weighted least-squares Engineering route (planned).** Reuse existing solver and focus mat-weighted-least-squares; verify weighted 3×2 numerical reference, invalid weights, keyboard and 390/768/1280px recovery.

**Execution checkpoint:** source, tests, mandatory Quality registration, ledger and changelog prepared for dev commit; exact SHA, checks, PR and Pages must be recorded from GitHub before release claims. No branches or protection changes.

## 2026-11-01 — Canonical Engineering SVD routing (ENG-CATALOG-SVD-072)

**Implemented on dev; full exact-head Quality, PR and Pages release pending.** Added one stable `matrix.svd.real.small` Engineering Toolbox route to the existing Matrix Calculator SVD action (`mat-svd`), for real 2×2, 2×3, 3×2 and 3×3 matrices. The route focuses the canonical solver without computing on navigation, copying a solver, changing calculator drafts, or claiming arbitrary-sized/complex SVD. The numerical rank is threshold-based and may differ from exact symbolic rank; singular/rank-deficient inputs remain supported. Synchronized `src/engineering-catalog.js` and offline `index.html`. New `tests/test_engineering_svd_route.py` checks stable unique ID, source/bundle parity and solver reuse. New `tests/smoke_engineering_svd_route.py` checks keyboard navigation and focus, 390/768/1280px layouts, rank-deficient 2×3 SVD, empty-input rejection and recovery, diagonal singular-value reference [3,2], and reconstruction residual < 1e-10. Registered the Chromium smoke in mandatory Quality. The previous main Quality and Pages release were green for commit `35b075741eca06b79d5cdf250aaa1074c52a9132`, not evidence for this new change. Local git checkout is blocked by `Could not resolve host: github.com`; connector-side source/bundle and CI registration inspections are available. No release is claimed until exact-head CI, PR gates and Pages are verified.

**NEXT FIVE concrete features and acceptance tests:**
1. **P0 — Exact dev-head Quality verification and repairs.** Inspect full structural/unit and Chromium matrix for final dev SHA including SVD route and all prior root/zoom tests; fix failed root causes and rerun without reducing coverage.
2. **P0 — Safe dev→main PR and Pages release.** Review full dev diff, require exact-head dev and PR green checks/approvals, merge via ordinary PR only, verify new main Quality, Pages build/deploy and hosted SVD route when reachable.
3. **P1 — Root-conditioning diagnostics.** Distinguish certified |f(x)| residual from an unproven |x−x*| bound; test steep/flat smooth roots, finite jumps, and keyboard/live explanatory output.
4. **P1 — Bounded inline source extraction.** Move one small remaining inline controller into `src/`; acceptance: reproducible standalone byte parity, saved-project compatibility, responsive keyboard/browser tests and no load-size regression.
5. **P1 — Engineering numerical solver expansion.** Route the existing symmetric eigen or weighted least-squares solver by one unique canonical ID, preserving input and using reference/residual, invalid-domain, 390/768/1280 keyboard tests.

## 2026-11-01 — Constant scalar residual plateau classification (MATH-ROOT-PLATEAU-071)

**Implemented on dev; exact-head CI, PR promotion and Pages release not yet verified.** The scalar root finder previously treated each sampled point of `x-x` (or a tiny nonzero constant below tolerance) as a discrete root, potentially listing hundreds of false isolated roots. It now checks whether all finite grid samples have exactly equal residuals and confirms that equality at two off-grid irrationally spaced probes before reporting a **sampled-zero-plateau** or **sampled-nonzero-plateau** status. In these cases it returns no certified discrete roots; the zero case explicitly flags possible non-isolated zeros, and neither status claims a proof of global constancy. Existing sign-change, Newton and residual certification paths remain unchanged for varying functions. Numerical output announces the distinction in its live status region. The extra probes reduce, but cannot eliminate, sampling aliasing.

Synchronized `src/numerical-data.js` and standalone `index.html`. Added `tests/test_scalar_root_plateaus.py` for source/bundle parity and structural contract, `tests/smoke_scalar_root_plateaus.py` for zero/nonzero/near-zero constants, smooth ±0.5 roots, tangential root and UI recovery; registered the browser smoke in required Quality. Connector-side exact source/bundle parity and workflow registration passed; isolated execution of the actual JS root kernel with controlled reference evaluators passed all six cases. Full Python and Chromium regressions could not run locally because github.com DNS resolution failed; no green exact-head workflow was returned. Previous main Quality 41330144543 and Pages 41330143364 remain prior-release evidence only.

**NEXT FIVE concrete features and acceptance gates:**
1. **P0 — Verify exact-head dev Quality and repair:** full Python unit/structural suite and all Chromium smokes pass for precise final dev SHA, including zoom module and plateau classification; inspect failing step logs and add non-weakened regressions if needed.
2. **P0 — Quality-gated dev→main and Pages:** inspect full diff, open/reuse ordinary dev→main PR only after exact dev checks green, obtain required approvals and PR checks, merge, verify main Quality and Pages jobs plus hosted critical paths when reachable.
3. **P1 — Canonical Engineering solver routing:** add one already implemented numerical solver with unique stable ID and focus-only navigation, no duplicate engine; reference residual and 390/768/1280 keyboard/mobile tests.
4. **P1 — Root conditioning diagnostics:** distinguish absolute function residual from root-location error, avoid unwarranted x-error guarantees; smooth/steep/flat and discontinuity reference tests and accessible explanatory output.
5. **P1 — Another bounded inline module extraction:** preserve byte-identical offline build, public APIs, saved-project round-trip, keyboard behavior and a measured load/size budget; add Python and Chromium regressions.

## 2026-11-01 — Extract table zoom module and announce percentage (UI-ZOOM-MODULE-070)

**Implemented on dev; exact-head CI and release pending.** Extracted the previously inline 881-character Table zoom controller to `src/visual-controls.js`, registered it in `scripts/build.py` and synchronized the self-contained `index.html`. The slider now exposes its current 50–200% percentage through `aria-valuetext` after keyboard, button, public API and restore changes; zoom values, storage key, project API and offline behavior are unchanged. New `tests/test_visual_controls_module.py` verifies byte-identical module/bundle parity, rebuild registration and clamp/accessibility contracts. New `tests/smoke_visual_controls_module.py` verifies keyboard ArrowRight, button controls, clamp bounds, accessible percentage, responsive 390/768/1280px layout and runtime errors. Mandatory Quality step added. Connector-side source/bundle parity and CI registration verified; full Python/Chromium execution and Pages verification still require exact-head checks. Previous main Quality 41330144543 and Pages 41330143364 were green for the prior root-residual release; they do not certify this change.

**NEXT FIVE with acceptance tests:**
1. **P0 — Exact dev-head CI and repairs:** structural/unit suite and all Chromium smokes green for the precise final dev SHA, including new table zoom test; inspect and fix failures without weakening assertions.
2. **P0 — Safe dev→main PR and Pages:** review exact diff, green dev/PR checks and required approvals, merge only through ordinary PR, verify main Quality, Pages deployment and hosted zoom behavior when reachable.
3. **P1 — Scalar root plateau diagnostics:** distinguish near-zero residual intervals from isolated roots, with constant nonzero/identically zero/smooth/tangential reference cases and honest completeness messaging.
4. **P1 — Canonical Engineering solver route:** link one existing tested numerical solver through a unique tool ID, no duplicated implementation, numerical residual and keyboard/mobile regressions.
5. **P1 — Next bounded inline module extraction:** extract one remaining small inline script with byte-parity, build reproducibility, project round-trip, load budget and Chromium regressions.

## 2026-11-01 — Scalar root residual certification and discontinuity rejection (MATH-ROOT-RESIDUAL-069)

**Implemented on dev; exact-head Quality and Pages release pending.** The real scalar root search previously accepted bisection candidates with absolute residual below sqrt(tolerance), which can report false roots across a small finite jump. It also silently rounded every root with |x| < 1e-10 to zero. Candidate admission now requires finite |f(x)| <= requested tolerance after rounding, and no longer forcibly zeroes small nonzero roots. Returns aligned residuals and maximum absolute residual (null when no roots), and displays that diagnostic in the Numerical Methods status region. This is an *absolute residual* guarantee, not an x-error bound or proof that every root was found; near-constant functions, discontinuities, steep slopes and ill-conditioning still limit completeness. Reuses the existing solver and parser; no dynamic evaluation or project format change. Synchronized src/numerical-data.js and self-contained index.html. Added tests/test_scalar_root_residuals.py (strict gate, bundle parity) and tests/smoke_scalar_root_residuals.py (sqrt(2), tangential root, finite sign jump, small positive root, residual alignment and UI output), registered in mandatory Quality. Direct connector-side source/bundle parity and workflow registration verified; local checkout and Python/Chromium suite unavailable because github.com DNS resolution fails. Last verified main release: PR #137 merged at 53ba62c6062ec89d5fcecb4d40fc9c4fd295c54f, main Quality 41325599502 succeeded (149 steps) and Pages 41325598536 build/deploy jobs succeeded. These prior runs do not certify this change.

**NEXT FIVE concrete features and acceptance tests:**
1. **P0 — Exact-head QA and repair:** all Python structural/unit and Chromium browser checks green for final dev SHA, including scalar residual, numerical root validation, Engineering filter, Matrix and QR/LU regressions; diagnose failing job logs without weakening assertions.
2. **P0 — Ordinary dev→main release:** inspect full diff, exact dev CI and PR checks/approvals, merge only authorized green PR, verify new main SHA, Quality and Pages build/deploy, and hosted root/numerical interactions when reachable.
3. **P1 — Bounded inline script extraction:** extract one still-inline source block into src/; byte-identical offline bundle, unchanged saved projects, keyboard/browser behavior, and measured size/load budget.
4. **P1 — Canonical Engineering solver route:** add one already-implemented solver through unique stable ID and focus-only routing; reference numerical residual, invalid-domain recovery and 390/768/1280 keyboard/mobile regression, no duplicated engine.
5. **P1 — Scalar root conditioning and completeness UX:** explain residual versus x-error and investigate flat near-zero plateaus and even-multiplicity roots; add positive/negative reference cases, scale diagnostics and no-false-claim UI tests.

## 2026-11-01 — Scalar root tolerance and field-level validation (MATH-ROOT-VALIDATION-068)

**Implemented on dev; exact-head Quality and production release pending.** The scalar nonlinear-root method now exposes its existing tolerance input (previously hidden), passes it to the existing real-root solver and validates finite start/end/tolerance, strict max > min and 0 < tolerance ≤ 0.01. Invalid scalar fields receive `aria-invalid`, are focused and reference the existing polite live error region; editing clears the field marker. Nonlinear system solves no longer pre-parse irrelevant hidden scalar domain fields. The numerical kernel itself, system Newton solver, other numerical methods and standalone offline packaging are preserved. Synchronized `src/numerical-data.js` and `index.html`; added `tests/test_numerical_root_validation.py` (structural/parity and validation guards), `tests/smoke_numerical_root_validation.py` (sqrt(2) reference, invalid 0/0.1/empty tolerance, invalid bracket, focus/live errors, recovery, hidden-domain system isolation) and a mandatory Quality browser step. Connector-side source/bundle parity and expected code markers checked; local full Python/Chromium tests unavailable because github.com DNS resolution prevents checkout. Previous main Quality run 41314819488 and Pages run 41314818945 passed for QR release only; neither certifies this change. The frozen 166 gaps and 95 partial features remain the historical baseline, not a completed count.

**NEXT FIVE concrete features with acceptance tests:**
1. **P0 — Exact dev-head QA and failure repair:** all Python unit/structural and Chromium steps green for precise dev SHA, including Engineering filter and root-tolerance tests; inspect failed job logs and repair root causes without weakening checks.
2. **P0 — Ordinary dev→main PR and Pages verification:** inspect complete dev diff, required PR checks and approvals; merge only after green exact-head checks; verify main Quality, Pages build/deploy and hosted root/Engineering interactions if reachable.
3. **P1 — Bounded standalone script extraction:** extract one remaining inline block to `src/`; byte-identical rebuild, unchanged saved project and browser behavior, and a load/size budget regression.
4. **P1 — Scalar root discontinuity and residual diagnostics:** avoid misleading roots near poles or nonfinite brackets; add reference smooth/tangential roots, discontinuity rejection and residual/error-bound tests without implying global completeness.
5. **P1 — Reusable Engineering Toolbox solver routing:** add one audited implemented solver via stable unique tool ID and no duplicate computation; reference residual, invalid-input, source-parity and keyboard/mobile regressions.

## 2026-11-01 — Engineering Toolbox filter accessibility (UI-ENGINEERING-A11Y-067)

**Implemented on dev; exact-head Quality and release pending.** Engineering discipline and search controls now have 40px minimum touch targets and 3px keyboard focus outlines, preserving the existing live result count and canonical solver routes. Updated `src/engineering-catalog.js` and synchronized self-contained `index.html`. Added `tests/test_engineering_filters_a11y.py` (CSS, labels, live status and source/bundle parity) and `tests/smoke_engineering_filters_a11y.py` (390/768/1280 responsive target measurement, keyboard focus, zero-results live status, search recovery and QR canonical route); mandatory Quality step registered. Prior main Quality run 41314819488 passed 147/147 steps for QR release; no new head CI result is implied by that run. Local git checkout remains unavailable due github.com DNS; direct connector-side source parity and CI are used as available verification. Frozen 166 gaps and 95 partials remain unchanged.

**NEXT FIVE concrete features with acceptance tests:**
1. **P0 — Exact-head Engineering filter CI verification/repair:** all Python unit and Chromium Quality steps pass for the final dev SHA, including Engineering filter, keyboard and QR/LU smokes; investigate failed step logs and fix root causes without reducing assertions.
2. **P0 — Ordinary dev→main promotion and Pages verification:** inspect exact-head PR checks and required approvals; merge only green PR, confirm main Quality and Pages build/deploy plus hosted keyboard/mobile critical path if reachable.
3. **P1 — Bounded standalone script extraction:** extract one remaining inline script into `src/` with byte-identical standalone build, unchanged project state and a new browser/load-size regression.
4. **P1 — Numerical root validation UX:** invalid bracket/tolerance and nonfinite-domain feedback with keyboard/live error recovery; reference roots, negative-domain and error-case numerical regressions.
5. **P1 — Shared engineering solver coverage:** add one audited reusable numerical capability/route with unique ID and no duplicate math; verify reference residual, invalid inputs, source parity and responsive keyboard behavior.

## 2026-11-01 — Canonical Engineering QR routing (ENG-CATALOG-QR-066)

**Implemented on dev; full exact-head CI and release pending.** Added a unique `matrix.qr.real.small` Engineering Toolbox route to the existing Matrix Calculator economy QR operation (`mat-qr`) for full-column-rank real 2×2, 3×2 and 3×3 matrices. The route focuses the existing button without running the solver, duplicating its numerical engine, or replacing draft input. Scope explicitly excludes wide and rank-deficient matrices. Synced `src/engineering-catalog.js` and offline `index.html`; new `tests/test_engineering_qr_route.py` asserts unique metadata, canonical solver and source/bundle parity. New `tests/smoke_engineering_qr_route.py` checks keyboard Enter routing, 390/768/1280 responsive layout, preservation of calculator draft, 3×2 reconstruction and orthogonality residuals below 1e-10, rank-deficient rejection/recovery and wide-matrix rejection. Required Quality workflow now runs this smoke. Direct connector-side source/bundle parity and canonical solver presence checks passed. Local clone could not resolve github.com; full Python/Chromium execution and commit-specific CI are release gates. Prior main Quality 41310092029 (146 successful steps) and Pages 41310091759 (build/deploy jobs successful) refer to the previous release, not this change.

**NEXT FIVE concrete features with acceptance tests:**
1. **P0 — Verify and repair exact QR dev-head Quality:** full structural/unit and Chromium matrix including QR and previous LU smokes green for exact SHA; inspect failed logs and fix root causes without weakening assertions.
2. **P0 — Promote QR through verified dev→main PR:** required exact-head and PR checks/reviews satisfied, ordinary authorized merge, verify main Quality, Pages deploy and hosted critical route if available.
3. **P1 — Engineering catalog accessibility:** 40px discipline/search targets, responsive keyboard focus and status live announcements at 390/768/1280; add structural and Chromium tests.
4. **P1 — Bounded standalone script extraction:** move one still-inline script into `src/`, preserve offline byte parity, public API, saved state, and add browser plus load/size budget regression.
5. **P1 — Numerical root tolerance and domain UX:** field-level invalid bracket/tolerance guidance, live error recovery, numerical reference roots and negative-domain regressions without changing solver correctness.

## 2026-11-01 — Canonical Engineering LU routing (ENG-CATALOG-LU-065)

**Implemented on dev; full exact-head Quality and Pages release not yet verified.** Added one unique Engineering Toolbox entry `matrix.lu.real.small` for the existing 2×2/3×3 real LU decomposition (scaled pivoting, P·A=L·U, residual check). The catalog opens the existing Matrix task and focuses its `mat-lu` button without executing, replacing or duplicating the solver or overwriting matrix inputs. Route metadata supports an optional validated existing-control focus ID. Synced `src/engineering-catalog.js` and self-contained `index.html`. New `tests/test_engineering_lu_route.py` asserts unique ID, canonical solver reuse and source/bundle parity; `tests/smoke_engineering_lu_route.py` covers keyboard Enter routing, 390/1280px layouts, singular-input error and recovery to a row-pivoting reference matrix with reconstruction residual below 1e-10. Chromium smoke registered in required Quality. Connector-side parity and static invariants verified; local checkout remains unavailable due github.com DNS resolution. Prior main Quality run 41305310017 and Pages run 41305309689 reported successful jobs for release ae8777f; this change is not part of that release.

**NEXT FIVE concrete features and acceptance gates:**
1. **P0 — Exact-head Quality repair and release:** full Python/unit and Chromium matrix green for the final dev SHA; review PR checks/approvals, ordinary dev→main merge only when green, verify main Quality, Pages and hosted critical routes.
2. **P1 — Canonical Engineering QR routing:** reuse the existing Matrix QR solver through one unique tool ID and focus, with 3×2 numerical reconstruction/orthogonality reference, rank-deficient rejection and mobile keyboard regression.
3. **P1 — Engineering catalog accessibility:** 40px filters and controls, result count live announcements, keyboard search and focus restoration at 390/768/1280; source parity and Chromium regressions.
4. **P1 — One bounded standalone source extraction:** extract one unmodularized script to `src/` with build parity, unchanged browser state and size/load budget tests.
5. **P1 — Numerical root tolerance and domain UX:** field-local validation, live error recovery and reference root/negative-domain tests, without weakening solver checks.

## 2026-11-01 — Numerical Methods responsive accessibility (UI-NUMERICAL-A11Y-064)

**Implemented on dev; exact-head CI pending.** Numerical Methods inputs, method select and action buttons have 40px minimum touch targets with box sizing; the existing role=status result/error region now explicitly uses aria-live=polite. All five methods preserve their numerical engines and progressive-disclosure input logic. Synchronized src/numerical-data.js and standalone index.html; added tests/test_numerical_a11y.py for source/bundle parity and CSS/live-region invariants, and tests/smoke_numerical_a11y.py for 390/768/1280 measurements, accessible names, duplicate IDs, keyboard Enter/Space, invalid-domain announcement and recovery, across all five methods. Browser smoke registered in mandatory Quality. Connector-side source/bundle parity, selector and live-region checks passed. Local git clone cannot resolve github.com; full CI is the executable gate.

**Release progress:** PR #133 merged via ordinary merge with expected dev head e0233fb79cca8e8a5717110bde9b45e19fd774a0 after exact-head Quality run 41301111097 succeeded (144/144 steps). Main merge commit 32bda95f223bbad5d14b69faa200654dcfabeac7, dev fast-forwarded to merge commit before this new change. Pages run 41304268135 succeeded; main Quality run 41304268859 in progress at inspection, and hosted browser smoke inaccessible. No claim of full production QA until both gates are verified.

**NEXT FIVE concrete features and acceptance gates:**
1. **P0 — Verify and repair Numerical Methods exact-head Quality:** all structural/unit and 390/768/1280 Chromium steps green on the final dev SHA; inspect logs and fix any failure without weakening tests.
2. **P0 — Finish prior main release verification and promote next PR:** main Quality green for 32bda95f..., Pages success and hosted smoke if available; then ordinary dev→main PR for new work with exact-head CI, reviews and approvals; verify post-merge main and Pages.
3. **P1 — Canonical Engineering Toolbox routing:** link one implemented solver through one stable tool ID with no duplicate kernel; add keyboard/mobile navigation and source/bundle parity regression.
4. **P1 — One bounded inline source extraction:** move one remaining standalone script block to src/, preserve offline bundle and public APIs; assert byte parity, unchanged browser results and load-size budget.
5. **P1 — Numerical root failure recovery and precision UX:** show domain/tolerance validation at the relevant field and keep live output synchronized; add reference, negative-domain and keyboard regression without changing solver math.

## 2026-11-01 — Matrix accessible touch targets (UI-MATRIX-A11Y-063)

**Implemented on dev, full exact-head CI and release pending.** Matrix calculator dimension selectors, action buttons and A/B/RHS/weight grid cells now use minimum 40px height. Grid cells retain dedicated grid scrolling and arrow/Home/End keyboard navigation; mathematical kernels and draft persistence unchanged. Source and standalone bundle synchronized. New tests/test_matrix_touch_targets.py guards CSS/source parity; new Chromium tests/smoke_matrix_a11y.py verifies responsive 390/768/1280 controls, no unintended horizontal document overflow and arrow-key focus, registered in mandatory Quality. In-session structural and bundle-parity checks passed; full Python/Chromium execution still requires exact-head Quality verification.

**NEXT FIVE concrete features with acceptance tests:**
1. **P0 — Exact dev-head Quality and failure repair.** Full structural/unit and Chromium smoke green for exact SHA, including Matrix, Graph and Data Tables accessibility regressions; inspect failed steps and fix without weakening tests.
2. **P0 — Verified dev→main PR and Pages.** Inspect or update PR #133 as appropriate; required checks and reviews green on exact head, ordinary authorized merge, verify main Quality, Pages and hosted critical paths.
3. **P1 — Numerical Methods panel a11y.** Audit inputs, selects, buttons and live error regions at 390/768/1280; add keyboard, invalid-input and responsive browser regression without altering numerical algorithms.
4. **P1 — Engineering catalog canonical tool routing.** One additional existing tested solver linked by stable unique ID; desktop/mobile keyboard route regression, no duplicated calculation and honest statuses.
5. **P1 — Source modularization.** Extract one remaining inlined block into src/ without behavioral change; build byte-parity, smoke and load performance regressions.

## 2026-11-01 — Graph axis and dataset import touch targets (UI-GRAPH-A11Y-062)

**Implemented on dev; exact-head CI and Pages deployment pending.** The Graph workspace axis fields and the advanced CSV/JSON dataset import selects/buttons/file chooser previously inherited 37–38px or browser-default control heights. Added one shared scoped 40px min-height rule in src/data-tables.js and synchronized the offline index.html without altering graph plotting or dense spreadsheet cell layout. New focused Python structural regression tests/test_graph_controls_targets.py checks CSS and source/bundle parity; new Chromium tests/smoke_graph_controls_a11y.py checks visible graph axis fields and advanced import controls at 390/768/1280, keyboard editing/plotting, disclosure keyboard access and no horizontal overflow. Browser test is now a required Quality workflow step. Direct connector-side source/bundle parity, CSS selectors and CI workflow registration verified. Full Python and Chromium execution remains unverified because local git checkout cannot resolve github.com; commit-specific workflow runs/status were not visible. No release promoted without exact-head QA.

**NEXT FIVE (with acceptance gates):**
1. **P0 — Verify and repair exact dev-head CI:** inspect all Quality jobs for the precise SHA, including graph and Data Tables smokes, resolve failures without weakening assertions; acceptance: complete Python/Chromium matrix green.
2. **P0 — Promote verified dev to main and Pages:** create/review normal dev→main PR only after exact-head Quality green; acceptance: required checks/approvals satisfied, merged SHA confirmed, main Quality and Pages green and hosted smoke verified.
3. **P1 — Matrix workspace accessibility:** audit 390/768/1280 keyboard focus and target heights; acceptance: new Chromium regression plus no horizontal overflow outside intentional grid scroll.
4. **P1 — Numerical Methods accessibility:** label all interactive controls, preserve error live regions and numerical results; acceptance: keyboard/invalid-input Chromium smoke and existing numerical reference tests green.
5. **P1 — Canonical Engineering Toolbox routing:** reuse one implemented solver without duplicating computation or actions; acceptance: unique tool ID, truthful status, source/bundle parity and keyboard/mobile route smoke.

## 2026-11-01 — Data Tables toolbar touch targets (UI-DATA-TOOLBAR-A11Y-061)

**Implemented on dev, exact-head CI and deployment pending.** Data Tables primary toolbars previously styled buttons at 37px; updated toolbar buttons, inputs and selects to minimum 40px height, retaining responsive wrapping and spreadsheet cell density. Reuses existing Data Tables CSS; source and self-contained index.html are byte-identical for that module. New tests/test_data_toolbar_targets.py checks offline parity and minimum-height rules; new tests/smoke_data_toolbar_a11y.py measures visible toolbar controls at 390, 768 and 1280 pixels, keyboard filter, and horizontal overflow. The new browser smoke is mandatory in Quality. Direct source/bundle parity and structural guard checks passed; independent Chromium and full Python CI not yet verified.

**NEXT FIVE with dependencies and acceptance tests:**
1. **P0 — Exact-head dev CI verification and repair:** all Python unit/structural and Chromium smoke tests green for precise dev SHA including new toolbar case; inspect failed job logs and repair without weakening assertions.
2. **P0 — Ordinary dev→main PR and Pages release:** only after exact dev head and PR checks pass; inspect diff/reviews, authorized merge, verify main Quality and Pages plus hosted critical paths.
3. **P1 — Graph panel touch-target audit:** measure input/select/button controls at 390/768/1280; add new Chromium keyboard/focus, no-overflow and target-height regression, preserve graph plot layout.
4. **P1 — Matrix and Numerical panels touch targets:** source-backed keyboard labels and measured mobile targets; regression of matrix grid focus, numerical output and invalid-input recovery.
5. **P1 — Canonical Engineering Toolbox routing:** add one truthful link to an already implemented solver, ensure unique metadata IDs, no duplicate solver, browser/mobile/standalone parity tests.

## 2026-10-31 — Tiny form controls in Control and Data Library panels (UI-A11Y-TARGETS-060)

**Implemented on the working branch; dev push held while PR #131 runs; CI and release pending.** Probing the Data Tables, Graph and Control panels at 390px found no unnamed control and no duplicate ID, but real touch-target defects the earlier button-only Control test could not see: the Control equilibrium size select was 19×30px, the transient inputs (initial state, t0, t1, steps) 21px tall, the Code Library category select 19px and its search field 21px — all unstyled browser defaults. Fixed with `min-height:40px` for inputs/selects (plus `min-width:56px` for the Control select) in the Control style block, and `#dt-code-library input,#dt-code-library select{min-height:40px}` in the Data Tables module (source and bundle synchronized, parity green). `tests/smoke_control_a11y.py` now measures buttons, inputs, selects and textareas (height and width); new `tests/smoke_data_library_a11y.py` (added to Quality) checks Code Library names, IDs, Enter/Space disclosure and sizes. Both verified to fail before the fix and pass after; 11 Data Tables/Control/browser smokes re-run green. **Not done (still queued):** the Data Tables toolbar buttons (37px), snippet fields (35px), Graph panel inputs (37–39px) and the dense spreadsheet cells; these are above the 24px WCAG minimum and are tracked for the next slice rather than reflowing a dense grid blindly.

**NEXT FIVE:** (1) merge PR #131 on green and verify main; promote this change; (2) Data Tables toolbar and Graph panel 40px targets, measured against the spreadsheet layout at 390/768/1280; (3) Matrix calculator and Numerical methods panel accessibility audit; (4) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (5) extract remaining large inline script blocks in `index.html` into `src/` modules one bounded slice at a time, each guarded by the parity test.

## 2026-10-31 — ODE panel accessibility and touch targets (UI-ODE-A11Y-059)

**Implemented on the working branch; dev push held while PR #130 runs; CI and release pending.** New Chromium `tests/smoke_ode_a11y.py` (added to Quality) audits the ODE initial-value panel in all three methods (RK4, RK45, coupled two-state): every control has an accessible name, no duplicate IDs, the output is a polite `role=status` live region, a keyboard-activated Solve reports into it with Enter, an invalid input is announced there with error styling (Space), no horizontal overflow at 390px, and every visible control is at least 40px tall. Findings: names, IDs and the live region were already correct; the defect was touch size — at 390px the method select and Solve/Table/Graph buttons were 37px and the numeric inputs 35px. Fixed with `#ode-details button,#ode-details select,#ode-details input{min-height:40px}` in the module's existing style string (source and bundle synchronized, parity test green). Verified fail-before/pass-after; ODE, system, adaptive, workload and backward smokes re-run green. Verified releases today: #118–#129 (each main Quality + Pages); #130 (Control a11y) open.

**NEXT FIVE:** (1) merge PR #130 on green and verify main; promote this change; (2) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (3) the same accessibility audit for the Data Tables toolbar and Graph data panel; (4) the same audit for the Matrix calculator and Numerical methods panels; (5) extract remaining large inline script blocks in `index.html` into `src/` modules one bounded slice at a time, each guarded by the parity test.

## 2026-10-31 — Control Theory panel accessibility and touch targets (UI-CONTROL-A11Y-058)

**Implemented on the working branch; dev push held while PR #129 runs; CI and release pending.** New Chromium `tests/smoke_control_a11y.py` (added to Quality) audits the Control Theory toolbox: every input, select, textarea and button has an accessible name; no duplicate IDs; the three disclosures toggle with Enter and Space from the keyboard; all four status regions are live (`role=status`/`aria-live`); a keyboard-activated run reports through the status region; and at 390px there is no horizontal overflow and every visible button is at least 40px tall. Defect found by the test and fixed: the stability, transient run, transient save and transient plot buttons rendered 28px tall on mobile (unstyled buttons); `.control-theory-toolbox button{min-height:40px}` in the existing style block fixes it with no behaviour change. Control theory, equilibrium, stability and transient smokes re-run green. Verified releases today: #118–#128 (each main Quality + Pages); #129 (source/bundle repair) open.

**NEXT FIVE:** (1) merge PR #129 on green and verify main; promote this change; (2) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (3) ODE panel accessibility: output live region, labelled controls and 40px targets regression; (4) the same accessibility audit for the Data Tables toolbar and Graph data panel; (5) extract remaining large inline script blocks in `index.html` into `src/` modules one bounded slice at a time, each guarded by the parity test.

## 2026-10-31 — Source/bundle drift repair and all-module parity guard (ARCH-BUNDLE-PARITY-057)

**Defect found and fixed on the working branch; dev push held while PR #128 runs; CI and release pending.** Three modules — `src/advanced-features.js`, `src/numerical-data.js`, `src/context-actions.js` — were stale relative to the code shipped in `index.html` (for example the curve-fit residual export button `#fit-export`, a table action-menu focus-visible rule and a context-action status-area parameter existed only in the bundle). The shipped app was correct, but running `scripts/build.py` would have overwritten those features with the stale source and silently regressed them, and no test caught it because the existing reproducibility test only compared two rebuilds with each other. Fix: the three sources were re-extracted from the tested bundle (`index.html` is unchanged, 0 diff lines), and a rebuild is now byte-identical to the committed `index.html`. New `tests/test_bundle_source_parity.py` asserts (1) every `src/*.js` file is declared in `build.py` and equals its embedded copy for all 17 modules, (2) a rebuild reproduces `index.html` byte-for-byte, with a negative control; run against the pre-fix tree it fails both checks. Verified releases today: #118–#127 (each main Quality + Pages); #128 (changelog archive) open.

**NEXT FIVE:** (1) merge PR #128 on green and verify main; promote this repair; (2) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (3) keyboard/focus regression for the Control Theory panel disclosures; (4) ODE panel accessibility: output live region and labelled controls regression; (5) extract the remaining large inline script blocks in `index.html` into `src/` modules one bounded slice at a time, each guarded by this parity test.

## 2026-10-31 — Changelog archive split (DOCS-CHANGELOG-ARCHIVE-056)

**Docs-only change on the working branch; dev push held while PR #127 runs.** `CHANGELOG.md` (722 lines) now holds the recent flat entries (2026-10-29 onward, 67 lines) under a `# Changelog` title with a pointer to `docs/archive/CHANGELOG_ARCHIVE_2026-10-29.md`, which carries the older release notes verbatim (660 lines; no entry edited or dropped). No tests or scripts read the changelog; the new link is covered by `tests/test_docs_links.py`. Verified releases today: #118–#126 (each main Quality + Pages); #127 (scalar RK4 diagnostic) open.

**NEXT FIVE:** (1) merge PR #127 on green and verify main; promote this docs change; (2) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (3) keyboard/focus regression for the Control Theory panel disclosures; (4) ODE panel accessibility: output live region and labelled controls regression; (5) a repo-wide check that every `src/*.js` module is embedded in `index.html` exactly (build-parity test for all modules, not only per-feature tests).

## 2026-10-31 — Scalar fixed-step RK4 step-doubling diagnostic (MATH-ODE-RK4-CONVERGENCE-055)

**Implemented on the working branch; dev push held while PR #126 runs; CI and release pending.** Scalar fixed-step RK4 now reports `|y_N − y_2N|` from a 2N-step rerun (N ≤ 500), matching the coupled two-state and Control diagnostics, labelled a diagnostic and not a global error bound. Above 500 steps, or when the refined time grid is unresolvable, the original valid solution is returned unchanged with the diagnostic marked unavailable. Tests: `tests/test_ode_rk4_convergence.py` (forward and backward y′=y references with the 4th-order relation between diagnostic and true error, 500/501 boundary, trajectory unchanged, failure paths, huge-offset case, bundle parity); Chromium `tests/smoke_ode.py` extended; ODE/system/backward/adaptive smokes re-run green locally. Verified releases today: #118–#125 (each main Quality + Pages); #126 (Engineering a11y) open.

**NEXT FIVE:** (1) merge PR #126 on green and verify main; promote this change; (2) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (3) changelog/plan size hygiene with archive and link test; (4) keyboard/focus regression for the Control Theory panel disclosures; (5) ODE panel accessibility: output live region and labelled controls regression.

## 2026-10-31 — Engineering catalog accessible names and keyboard regression (UI-ENGINEERING-A11Y-054)

**Implemented on the working branch; dev push held while PR #125 runs; CI and release pending.** Defect found: every available card's button was announced only as "Open existing tool", so assistive-technology users could not tell tools apart. Each button now has `aria-label="Open existing tool: <title>"` (visible text unchanged). New Chromium `tests/smoke_engineering_keyboard.py` (added to Quality) asserts unique accessible names, no control on planned cards, polite live status, Tab reaching the first result button, a ≥2px focus outline, Enter and Space each routing to the real tool control, ≥40px targets and no horizontal overflow at 390px, and no page errors. Existing catalog and project-filter smokes re-run green. Verified releases today: #118–#124 (each main Quality + Pages); #125 (docs-link + sandbox-contract tests) open.

**NEXT FIVE:** (1) merge PR #125 on green and verify main; promote this change; (2) scalar fixed-step RK4 step-doubling diagnostic parity; (3) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (4) changelog/plan size hygiene with archive and link test; (5) keyboard/focus regression for the Control Theory panel disclosures.

## 2026-10-31 — Python sandbox contract regression (SECURITY-PYTHON-SANDBOX-053)

**Test added on the working branch; dev push held while PR #124 runs.** `tests/test_python_sandbox_contract.py` locks the existing isolation contract with no behaviour change: user Python runs only in a terminable Worker with a 60 s timeout and blob-URL revocation; the worker source has no access to `document`, `window`, storage, network APIs or `eval(`; user code gets a `{"math": math}` namespace and may only return a finite real number (re-validated on the main thread); every Pyodide load is pinned to one version (`v0.29.1`); and no direct `eval()` or `new Function()` exists in `index.html` or `src/*.js` code (comments stripped, with a stripper unit check and negative controls). Review finding: none; the existing design already satisfies the AGENTS.md rule that user Python never runs on the main thread. Limits: this is a structural guard — it does not exercise real Pyodide (CDN-dependent, not verified here).

**NEXT FIVE:** (1) merge PR #124 on green and verify main; promote docs-link and sandbox-contract tests; (2) scalar fixed-step RK4 step-doubling diagnostic parity; (3) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (4) changelog/plan size hygiene with archive and link test; (5) keyboard-accessibility regression for the Engineering catalog cards (Tab order, Enter/Space activation, visible focus).

## 2026-10-31 — Markdown link regression test (DOCS-LINKS-052)

**Test added on the working branch; dev push held while dev CI for `aa3dfd5` runs.** `tests/test_docs_links.py` walks every tracked Markdown file and fails on any relative link whose target file or directory does not exist (anchors and external URLs ignored), plus a negative control and a minimum-link-count sanity floor. It runs inside the existing mandatory unit step, so the `docs/toolboxes/` and `docs/archive/` reorganization cannot silently regress. Releases verified so far today: #118 `91ef7a6`, #119 `c92be4f`, #120 `794fb6e`, #121 `b67ee14`, #122 `3fee173`; #123 `04853db` merged, main verification pending at write time.

**NEXT FIVE:** (1) verify main for `04853db`; promote the Engineering filter commit; (2) Python sandbox regression review (offline behaviour, invalid import cases); (3) scalar fixed-step RK4 step-doubling diagnostic parity; (4) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (5) CHANGELOG/plan size hygiene: archive changelog entries older than the current month under docs/archive with a link test.

## 2026-10-31 — Engineering filter saved with the project (DATA-PROJECT-ENGINEERING-FILTER-051)

**Implemented on the working branch; dev push held until PR #123 merges; CI and release pending.** Project JSON gains an optional `engineering: {discipline, query}`. The schema accepts it only as a record with a lowercase discipline slug (≤32 chars) and a query string ≤200 chars; restore additionally requires the discipline to be a real catalog id or empty, and runs first in `applyProject`, so a bad value throws before other state changes and the existing rollback re-applies the previous project. Legacy projects without the field import unchanged and leave the live filter alone. Tests: `tests/test_project_engineering_filter.py` (reference, 200/201 boundary, negative shapes, v1 migration, bundle parity) and Chromium `tests/smoke_engineering_project_filter.py` (round-trip, legacy, unknown-discipline rollback, oversized refusal, 390px), added to Quality. Related project/Matrix/table/graph smokes re-run green locally.

**NEXT FIVE:** (1) merge PR #123 on green exact-head CI and verify main; promote this change; (2) Python sandbox regression review (offline behaviour, invalid import cases); (3) scalar fixed-step RK4 step-doubling diagnostic parity; (4) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes; (5) docs link-checker as a CI test so the reorganized docs cannot regress.

## 2026-10-31 — Engineering catalog routes for interpolation, quadrature and minimization (UI-ENGINEERING-NUMERIC-ROUTES-050)

**Implemented on the working branch; dev push held until PR #122 merges; CI and release pending.** Three existing tested tools are listed as available with honest scope notes and real routing: `numerical.interpolation.1d`, `numerical.quadrature.adaptive`, `numerical.minimize.golden`. No solver or action duplicated; `smoke_engineering_catalog.py` verifies one working button per card and that `#interp-run`, `#num-run`, `#minimize-run` become visible. Releases so far: #118 `91ef7a6`, #119 `c92be4f`, #120 `794fb6e`, #121 `b67ee14` (each main Quality + Pages verified); #122 (coupled ODE diagnostic) open.

**NEXT FIVE:** (1) merge PR #122 on green exact-head CI and verify main; promote this change; (2) project round-trip for Engineering search/filter state with rollback tests; (3) Python sandbox regression review (offline behaviour, invalid import cases); (4) scalar fixed-step RK4 step-doubling diagnostic parity; (5) catalog routes for remaining existing tools (curve fit, spreadsheet functions) with scope notes.

## 2026-10-31 — Coupled two-state RK4 step-doubling diagnostic (MATH-ODE-SYSTEM-CONVERGENCE-049)

**Implemented locally on the working branch; not yet pushed to dev, CI and release pending.** The ODE panel's coupled two-state RK4 now reports `|x_N − x_2N|∞` from a 2N-step rerun (N≤500), matching the Control transient diagnostic. It is explicitly *not* a global error bound; above 500 steps, or if the refined time grid is unresolvable, the original valid solution is returned with the diagnostic marked unavailable. Tests: `tests/test_ode_system_convergence.py` (harmonic-oscillator forward/backward references with the 4th-order relation between diagnostic and true error, 500/501 boundary, unchanged trajectory, failure paths, huge-offset case, bundle parity) and extended Chromium `tests/smoke_ode_system.py`.

**NEXT FIVE:** (1) merge PR #121 (round-trip test) and verify main, then promote this change; (2) catalog routes for interpolation, quadrature and minimize tools with scope notes; (3) project round-trip for Engineering search/filter state with rollback tests; (4) Python sandbox regression review (offline behaviour, invalid import cases); (5) scalar fixed-step RK4 step-doubling diagnostic parity.

## 2026-10-31 — Graph dataset round-trip identity regression (DATA-GRAPH-ROUNDTRIP-048)

**Test coverage added on dev; exact-head CI and release pending.** `tests/smoke_graph_dataset_roundtrip.py` (now in Quality) loads a mixed-text dataset plus an overlay series, exports, re-imports and asserts the stored dataset, column order, X/Y/Z mapping and overlay are identical; imports a project with number/boolean/null cells; confirms a duplicate-header project is refused atomically (previous dataset and marker preserved); and checks 390px layout with no page errors. No source change was needed. Releases so far: PR #118 `91ef7a6` and PR #119 `c92be4f` verified (main Quality + Pages success); PR #120 `794fb6e` merged, main verification pending at write time.

**NEXT FIVE:** (1) verify main Quality/Pages for `794fb6e`, then promote this test by ordinary PR; (2) two-state ODE convergence diagnostic parity with scalar RK45; (3) catalog routes for interpolation, quadrature and minimize tools with scope notes; (4) project round-trip for Engineering search/filter state with rollback tests; (5) Python/worker sandbox regression review: keep offline sandbox behaviour and add invalid-import cases.

## 2026-10-31 — Engineering catalog routes for FFT, Brent and symmetric eigen (UI-ENGINEERING-NUMERIC-ROUTES-047)

**Implemented on dev; exact-head CI and release pending.** Three existing, already-tested tools are now listed as available in the Engineering Toolbox with honest scope notes and real routing: `matrix.eigen.symmetric.small` (Calculator matrices), `signals.fft.1d` and `numerical.root.brent` (Numerical methods). No solver or action duplicated; `smoke_engineering_catalog.py` asserts a single working button per card and that the target control (`#fft-run`, `#brent-run`, `#matrix-tools`) becomes visible. Earlier queue item "show ODE overflow retries in UI" was verified already present (`ode-tools.js` output line) and is closed. Prior release: PR #118 `91ef7a6` (main Quality and Pages green) and PR #119 `c92be4f` (head CI green; main runs pending at write time).

**NEXT FIVE:** (1) verify main Quality/Pages for `c92be4f`, then promote this change through an ordinary PR; (2) Graph/Data Tables Chromium export→import identity for mixed cell types and 390px focus; (3) two-state ODE system convergence diagnostic parity with scalar RK45; (4) catalog routes for interpolation, quadrature and minimize tools with scope notes; (5) project round-trip for Engineering search/filter state with rollback tests.

## 2026-10-31 — RK45 near-resolution references and Engineering Control routes (MATH-ODE-RK45-NEAR-RESOLUTION-045, UI-ENGINEERING-CONTROL-ROUTES-046)

**Implemented on dev; exact-head CI pending.** (1) `tests/test_ode_rk45_near_resolution.py` asserts original-time vs rescaled-time agreement for autonomous y′=y forward/backward at offsets up to 1e11, exact landing on the end time, monotone time grids, and counted collapsed stage times when the span approaches float time resolution (no source change; behaviour already matched). (2) Engineering catalog gains two *available* entries for existing tools — `control.stability.symmetric` and `control.transient.two.state` — routed to their real Control panels (enclosing disclosures opened, summary focused); no new solver or action. `tests/smoke_engineering_catalog.py` verifies routing, focus and truthful status. Neither is released.

**NEXT FIVE:** (1) exact-head Quality for dev, then ordinary dev→main PR, main Quality and Pages; (2) Graph/Data Tables dataset round-trip: Chromium export→import identity for mixed cell types and focus at 390px; (3) show `stageOverflowRetries` and collapsed-stage counts in the ODE UI with browser assertions; (4) add catalog routes for existing FFT, Brent root and symmetric eigen tools with honest scope notes; (5) ODE system (two-state) RK45-style convergence diagnostic parity with scalar RK45.

## 2026-10-31 — Saved table selection validation (DATA-PROJECT-TABLE-SELECTION-044)

**Implemented on the working branch; exact-head CI not yet verified.** Project schema now refuses a `tables.selected` value that is not a string naming an existing table id, so a stale selection can no longer silently restore a different sheet. Column order, mixed primitive cells, v1→v2 migration and absent-selection projects are unchanged. Tests: `tests/test_project_table_selection.py` (reference, negative, boundary, bundle parity) and Chromium `tests/smoke_project_table_selection.py` (round-trip, rollback, 390px), added to Quality. PR #118 merged to main at `91ef7a6` (head CI green); main Quality and Pages not yet confirmed at write time.

# Hourly development plan — living queue

Current entries and the **Next five features** queue are kept here (newest first). Older execution entries are in [archive/HOURLY_DEVELOPMENT_LOG_ARCHIVE.md](archive/HOURLY_DEVELOPMENT_LOG_ARCHIVE.md); the frozen baseline is the [audited inventory](FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md).

## 2026-10-30 — Fixed-step RK4 time-resolution guard (MATH-ODE-RK4-TIME-GRID-043)

**Implemented on dev; exact-head CI and production not verified.** Fixed-step scalar and coupled two-state RK4 now reject unresolvable floating-point time grids before accepting output: consecutive output times must advance in the requested direction and RK4 midpoint stage time must remain distinct from the current/next output time. This prevents silently exporting duplicate timestamps or evaluating collapsed midpoint stages at large epochs. The existing time-step, derivative, solver, graph/export UI and offline bundle are retained. Error advises fewer steps or rescaling time. Added focused tests/test_ode_rk4_time_resolution.py with forward/backward constant derivative, exponential and oscillator references, positive representable ULP boundaries, rejected collapsed-stage boundaries and standalone parity. Added tests/smoke_ode_rk4_time_resolution.py with scalar/coupled UI, stale-export disabling, recovery, mobile and page-error assertions; registered browser test in Quality. Direct isolated JS evaluation passed 17/17 targeted checks; full repository Python/Chromium suite could not run because container cannot resolve GitHub checkout. Previous accessible Quality run 41119433137 passed but predates this feature; exact-head CI still unknown. No PR/main/Pages promotion without verification.

**NEXT FIVE concrete priorities, dependencies and acceptance tests:**
1. **P0 — Verify exact dev-head Quality and fix failures.** Retrieve full push/PR Quality run and precise SHA, require complete Python structural/unit and Chromium smoke suite including RK4 time-grid, RK45, Graph import and saved-project cases; inspect logs and fix any failure without weakening tests.
2. **P0 — Verified dev→main release and Pages.** Once #1 green, open/reuse ordinary reviewed dev-to-main PR, verify checks and required approvals, merge without bypass, verify main Quality, Pages deployment and hosted critical flows on desktop/mobile.
3. **P1 — Graph/Data Tables v1/v2 round-trip and mobile focus.** Preserve mixed primitive cell types, ordered columns, selected task and keyboard focus across import/export; reject malformed data atomically, with Node and 390px Chromium cases.
4. **P1 — RK45 near-resolution convergence.** Compare original-time vs rescaled-time numerical references forward/backward, assert local-error limits and explicit noncertification warnings, cover export invalidation on failure.
5. **P1 — Canonical Engineering Toolbox routing.** Connect approved existing solver IDs to source-backed metadata without duplicating math engines or controls; verify keyboard navigation, 390px layout, offline parity and truthful planned/partial states.

## 2026-10-30 — Canonical Graph dataset header identity (DATA-GRAPH-HEADER-CANONICAL-042)

**Implemented on dev, not yet released.** Saved Graph datasets now reject empty/whitespace-only header names and duplicate names after trimming/case-folding, preventing ambiguous restored column selectors while preserving valid original header strings, mixed primitive cells, row order and v1→v2 migration. Synchronized src/project-schema.js and standalone index.html. Added tests/test_graph_project_header_canonical.py with v1/v2, mixed cells, negative/invalid rows, nonmutation and offline parity; extended Chromium tests/smoke_project_schema.py with invalid import rollback cases. In-session JavaScript 12 positive/negative assertions and source/bundle parity passed. Full Python/Chromium suite unavailable locally (GitHub checkout network resolution failed). Last accessible known Quality job 41119433137 succeeded but is not exact new dev head; no current-head CI claim or release.

**NEXT FIVE concrete priorities and acceptance tests:**
1. **P0 — Exact-head CI and defect repair:** obtain GitHub Quality for precise dev SHA, require all Python/structural and Chromium tests green including new graph header regression, inspect and fix any failed logs without weakening tests.
2. **P0 — Safe release via dev→main PR:** only after #1 green, create/reuse ordinary reviewed PR, verify protections and required checks, merge, verify main Quality, Pages publish and hosted critical flows.
3. **P1 — Graph/Data Tables project v1/v2 round-trip and mobile focus:** import/export mixed primitive rows and ordered headers; test 390px layout, selected workspace/focus preservation and atomic rollback.
4. **P1 — RK45 near-ULP convergence reference:** compare results across rescaled-time and original-time problems, forward/backward monotonicity and explicit noncertification warning, with numerical and browser tests.
5. **P1 — Canonical Engineering Toolbox routing:** use existing solver IDs, truthful partial/planned metadata and reusable graph/export pipeline; keyboard, 390px and offline parity tests.

## 2026-10-30 — RK45 accepted time-grid integrity (MATH-ODE-RK45-ULP-GRID-041)

**Implemented on dev; exact-head full CI/release pending.** Adaptive scalar RK45 now asserts every accepted sample advances strictly toward target before appending to Data Tables/Graphs, and reports the count of accepted steps that advanced by only one representable time quantum. When near machine resolution the UI warns to rescale time and check convergence; this does not certify global accuracy or change solver step acceptance. Existing stage-collision and rejection diagnostics remain intact. Source and offline HTML synchronized. New tests/test_ode_rk45_monotonic_grid.py covers forward/backward near-ULP and exponential analytic references, exact endpoint, no duplicate times, error path and bundle parity. Extended tests/smoke_ode_rk45_stage_resolution.py with browser/mobile warning and forward/backward time-order tests. Full GitHub Quality/PR/main/Pages not yet verified.

**NEXT FIVE with acceptance tests:** (1) exact-head dev CI all structural/Python and Chromium smoke green, repair observed failures without weakened assertions; (2) ordinary dev-to-main PR with verified checks and reviews, main Quality, Pages and hosted verification; (3) project Graph/Data Tables v1/v2 mixed-primitive round-trip and mobile focus rollback; (4) RK45 numerical convergence comparisons under near-machine-precision regimes and explicit error budget tests; (5) Engineering Toolbox canonical solver metadata links, truthful planned states and keyboard/mobile regression.

## 2026-10-30 — Graph project duplicate headers (DATA-GRAPH-HEADER-IDENTITY-040)

**Implemented on dev; Quality pending.** Reject duplicate Graph dataset header names during import before mutation, preserving valid data, row order and v1/v2 project migration. Added tests/test_graph_project_header_identity.py and Chromium atomic rollback cases in tests/smoke_project_schema.py. Offline HTML synchronized. Concurrent Data Table name validation commits preserved.

**NEXT FIVE acceptance:** (1) Green exact-head Python/Chromium Quality including graph/table project imports. (2) Ordinary dev→main PR, green checks, main Quality and Pages deployment. (3) Graph and Data Table v1/v2 mobile round-trip and focus restoration. (4) RK45 near-ULP time monotonicity numerical references and error recovery. (5) Engineering Toolbox metadata/routing with accurate statuses and keyboard/mobile tests.

**Execution:** Started dev 863e00b917b4fa64e57d0fd5196214367605feab, main 220f7641f1358ea3fc706c5334c6c7d7493bef52. Previous dev Quality 41119433137 passed; new changes awaiting exact-head Quality. Historical 166/95 frozen baseline unchanged.

## 2026-10-30 — Saved Data Tables name identity (DATA-PROJECT-TABLE-NAMES-039)

**Implemented on dev, exact-head CI/Pages pending.** Project migration rejects blank or whitespace-only table names and names equivalent after trimming and lowercasing. Valid original display names are preserved, including v1/v2 migration. Source and offline index synced. Added test_project_table_name_identity.py (numeric/identity/negative cases) and smoke_project_schema.py browser rollback cases. Direct isolated JS cases and bundle parity passed; full Python/Chromium not yet independently verified.

**NEXT FIVE with acceptance tests:** (1) exact-head Quality full Python/Chromium green and failure repair; (2) ordinary reviewed dev-to-main PR, required checks, main Quality, Pages and hosted checks; (3) Graph/Data Table v1/v2 mixed primitive round-trip, malformed rollback, mobile focus tests; (4) RK45 forward/backward near-ULP monotonic time and stale-export tests; (5) Engineering solver routing with unique stable IDs, honest states, keyboard/mobile and bundle parity tests.

## 2026-10-30 — Matrix project finite draft validation (DATA-PROJECT-MATRIX-FINITE-038)

**Implemented on dev; exact-head CI and production pending.** Matrix project migration now rejects scientific-notation drafts that parse to nonfinite values (e.g. 1e999) or exceed the existing Matrix solver's 1e12 magnitude bound (e.g. 1e13). Applies to A, B, RHS and weights, preserving empty drafts, bounded decimals/scientific notation, v1→v2 migration and atomic import preflight. Source and offline HTML are synchronized. Added tests/test_matrix_project_finite_drafts.py with Node v1/v2 boundary, nonfinite/oversize and bundle parity coverage; extended tests/smoke_matrix_project_state.py with four 390px invalid-import rollback cases. Isolated predicate assertions (18) and source/offline parity passed; complete repository unit and Chromium suites could not run locally because repository checkout and browser executable were unavailable. Exact-head GitHub push CI results not exposed by connector. Do not claim release.

**NEXT FIVE concrete priorities, dependencies and acceptance tests:**
1. **P0 — Exact-head dev CI and failure repair (pending).** Obtain GitHub Quality run for precise dev SHA, verify all Python unit and Chromium smoke jobs (including finite Matrix drafts and prior RK45/Control cases), inspect failed logs, fix root causes without weakening tests.
2. **P0 — Verified PR promotion and Pages (blocked on #1).** Open/reuse dev→main PR only when checks can be verified, inspect diff, reviews and protections; merge via ordinary PR only with required checks/approvals, verify main Quality, Pages deployment and hosted critical paths.
3. **P1 — Saved-project Graph/Data Tables v1/v2 round-trip.** Preserve column types and sample order, reject malformed/nonfinite nested cells before any mutation; Node and Chromium rollback/focus/mobile tests.
4. **P1 — RK45 near-ULP time-grid correctness.** Forward/backward monotone sample times, no duplicate samples, stage-collision warnings and exhaustion context; analytical references and 390px stale-export tests.
5. **P1 — Engineering catalog canonical solver routing.** Approved source-backed entries, unique IDs and truthful planned status; desktop/mobile keyboard and offline parity tests, no duplicate solver engines.

**QA repair:** Updated the pre-existing RK45 workload failure-context regression for the additional bounded-overflow count field; all four targeted Node numerical snippets passed in isolated V8. No production release without full exact-head CI.

## 2026-10-30 — RK45 structured overflow classification and stage diagnostics (MATH-ODE-RK45-OVERFLOW-CLASSIFICATION-037)

**Implemented on dev, exact-head CI and production pending.** RK45 no longer infers recoverable intermediate overflow by searching an exception's English message. Its local bounded-stage validator attaches a structured code and stage identifier. Finite out-of-bounds intermediate derivatives/states can still retry by halving within the attempt budget; nonfinite derivative values (possible domain/singularity failures), untagged evaluator errors and k1 failures remain hard errors. Output and exhaustion context report the last overflow stage. Original local-error acceptance, solver limits, offline bundle, stale-export invalidation and existing non-RK45 solvers remain unchanged. New focused Node/Python regression tests forward/backward numerical references, stage tagging, max-attempt exhaustion, k1 failure, nonfinite k2, deceptive error text and smooth case; browser smoke now checks last-stage display and result property. Isolated V8 direct test passed; full GitHub Quality and Chromium not independently verified.

**NEXT FIVE concrete priorities and acceptance tests:**
1. **P0 — Verify exact-head dev Quality and repair failures:** all Python structural/unit tests and all Chromium smoke green for precise dev SHA; inspect failing job logs and fix without weakening assertions.
2. **P0 — Safe dev→main PR and Pages release:** one reviewed PR with exact dev/PR checks and approvals green, ordinary merge, main Quality, Pages deployment and hosted critical paths verified.
3. **P1 — Saved-project Matrix/Graph/Table compatibility:** v1/current fixture round trips, malformed import atomic rollback, focus preservation and 390px Chromium checks.
4. **P1 — RK45 time-resolution edge accuracy:** forward/backward near-ULP, nonfinite stage, underflow and error budget reference tests, stale export and mobile checks.
5. **P1 — Engineering catalog verified expansion:** approved discipline entries with unique IDs, truthful statuses, reusable canonical solver links and keyboard/mobile tests.

## 2026-10-30 — Control two-state trajectory plotting (CONTROL-TRANSIENT-PLOT-036)

**Implemented on dev; exact-head CI/PR/main/Pages pending.** Added a single contextual Plot both states in Graphs action beside the existing Data Tables export. It imports the already-computed RK4 trajectory through the canonical Data Tables service, draws x1(t) as a line with t on the horizontal axis, and overlays x2(t) through the existing Graph Data add-series service. No new plotting kernel, no solver changes and no duplicated global plot controls. Invalid/edited inputs disable both export actions. After plotting, graph state must contain the full original sample count and exactly one x2 overlay with x=0/y=2 mapping; mobile actions wrap and keyboard Enter activates the plot. Source and standalone HTML parity retained. Added tests/test_control_transient_plot.py with Node mocked DOM mapping, stale guard and parity; expanded mandatory Chromium tests/smoke_control_transient.py for real overlay, sample count, keyboard and 390px width. Full GitHub CI and hosted browser not independently verified; do not claim release.

**NEXT FIVE (priority, dependencies, acceptance tests):**
1. **P0 — Exact-head CI verification and repair.** Inspect latest dev Quality run; require full Python unittest and all Chromium smoke green at exact head, including RK45 overflow and Control plot, no weakened tests; fix root causes and rerun.
2. **P0 — Safe dev-to-main PR and Pages.** Only after exact dev QA green, inspect one PR, required checks/approvals, merge through normal PR, verify main Quality and Pages deployment and hosted critical paths.
3. **P1 — RK45 stage-overflow edge diagnostics.** Reference forward/backward near-ULP, attempt-budget exhaustion, k1 hard failure and non-overflow domain errors; unit/browser failure context and stale-export assertions.
4. **P1 — Saved-project Matrix/Graph/Table compatibility.** v1/current fixtures, malformed import atomic rollback, focus/keyboard and 390px browser round-trip.
5. **P1 — Engineering catalog source-backed expansion.** Add approved discipline catalog entries with unique IDs, truthful planned/available statuses and 390px keyboard tests; reuse shared solver registry.

**Execution checkpoint:** started dev 2f9c34cdc4b261389c2cd98aa32c3619bb36d541, main 220f7641f1358ea3fc706c5334c6c7d7493bef52. No open PR at start; GitHub connector exposes no push-run listing and old run-job lookup timed out. Source/test changes committed to dev, full local/browser execution not available from connector-only snapshot; exact-head checks pending. Historical 166 gaps and 95 partial features unchanged. No branch cleanup without verified safety evidence.

## 2026-10-30 — RK45 bounded stage-overflow recovery (MATH-ODE-RK45-OVERFLOW-035)

**Implemented on dev; full exact-head CI/Pages pending.** Adaptive scalar Dormand–Prince RK45 now retries bounded intermediate-stage state/derivative overflow by halving the attempted step, counting the retry as a rejection within the existing attempt budget. A step-independent k1 failure and non-overflow syntax/domain errors still fail immediately; exhausted floating-point time resolution raises contextual progress error. Retains original local-error acceptance, max-attempt bounds and forward/backward integration. Reports stage-overflow retry count in result and UI; source and offline HTML synchronized. Focused Node/Python numerical regression covers forward/backward guarded exponential, smooth control, rejection accounting and invalid k1; new mandatory Chromium regression covers a real -3000*y workload, recovery, disabled stale exports and 390px viewport. Direct isolated V8 tests passed: forward and backward 4 overflow retries each, 334 accepted, 18 rejected, terminal |y|<1e-8; -3000*y 1 overflow retry, 971 attempts, 939 accepted, 32 rejected. Full Python/Chromium CI not yet verified. Historical 166 gaps and 95 partial features remain baseline counts.

**NEXT FIVE concrete features (priority / acceptance tests):**
1. **P0 — Verify exact-head RK45 CI and repair failures.** Python structural/unit suite and all Chromium smoke tests green for precise dev SHA, including source/bundle parity, RK45 progress and new overflow cases; no weakened gates.
2. **P0 — Safe release and Pages verification.** With exact dev Quality and PR checks/approvals green, inspect diff, merge dev→main by ordinary PR, confirm new main Quality, Pages deploy and hosted critical path when possible; no direct main push.
3. **P1 — Control transient x1/x2 plot handoff.** Reuse Data Tables/Graphs chart pipeline; verify both state series, timestamps, disabled stale export, keyboard and 390px viewport; no duplicate plotting kernel.
4. **P1 — RK45 overflow underflow and pathological domain tests.** Verify near-ULP forward/backward failure context, attempt budget, nonrecoverable k1, invalid expressions and finite-state numerical reference in Node and Chromium.
5. **P1 — Saved-project Matrix/Graph/Table compatibility.** v1/v2 round-trip fixtures, malformed import atomic rollback, focus restoration and 390px Chromium tests.

**Execution checkpoint:** initial dev/main 220f7641f1358ea3fc706c5334c6c7d7493bef52 (identical); direct V8 reference checks passed; exact final dev SHA, CI/PR/Pages to be checked. No obsolete branch deletion without verified containment/protection checks.

## 2026-10-30 — Control RK4 transient convergence (CONTROL-TRANSIENT-CONVERGENCE-034)

**Implemented on dev, CI pending.** Compare base two-state RK4 endpoint against a 2N-step refined run, displaying maximum absolute endpoint difference. Refinement only attempted for N<=500 to retain solver limit (1000); when unavailable, preserve original trajectory and Data Tables export. This is a convergence diagnostic, not a global error bound. The existing coupled ODE solver and offline bundle are reused. Added focused structural parity tests and extended Chromium browser regression for N=500/501, invalidation, export and mobile.

**NEXT FIVE:** (1) exact-dev Quality: all Python and Chromium checks green at precise head, fix failures; (2) PR #117: verify PR approvals/checks and ordinary merge, main Quality and Pages; (3) RK45 stage overflow: bounded forward/backward numerical and underflow browser tests; (4) Control x1/x2 plot handoff via Data Tables/Graphs: samples, keyboard/mobile and invalidation tests; (5) Matrix/Graph/Table project compatibility: v1/v2 round-trips, rollback and focus tests.

**2026-10-30 CI repair checkpoint:** [Quality 41085865243](https://github.com/saeedsai/ProMathStudio/actions/runs/41085865243) failed 2 of 182 unit tests due solely to Control source/bundle trailing newline mismatch; new Control numerical tests passed. Restored expected exact bundle spacing and preserved disclosure-summary-first semantics. Exact-head full CI, PR/main Quality and Pages still required; no release claimed.

## 2026-10-30 — Control transient RK4 and Engineering search CI repair (CONTROL-TRANSIENT-TWO-STATE-033)

**Implemented on dev; exact-head full CI and release pending.** Added bounded real two-state transient response xdot=-Ax+b to the existing Control Theory state panel, using the canonical coupled RK4 ODE engine and Data Tables import. Strict 2x2 and decimal/scientific numeric validation, forward/backward time, singular-A support, invalidation and responsive output. Direct numerical references passed in isolated V8 (forward max 1.8e-9; backward max 1.44e-7; singular max 9e-10); new Python/Node and mandatory Chromium 390px/export regressions committed. No stiff solver or global accuracy guarantee. Previous exact-head Quality [41083127664](https://github.com/saeedsai/ProMathStudio/actions/runs/41083127664) failed at a stale `includes(q)` structural assertion, now repaired to check all-term semantics; new CI not yet verified. PR #117 remains open; no main or Pages promotion attempted.

**NEXT FIVE concrete features with acceptance tests:**
1. **P1 — Exact-head Control transient and Engineering search QA/release (in progress).** Require full Python unit/structural suite and Chromium smoke (including new transient and all-term search) green for exact dev SHA; inspect PR #117 checks/diff and approvals, ordinary merge, main Quality and Pages success, hosted critical-path check if available.
2. **P1 — RK45 stage overflow bounded recovery (planned).** Distinguish finite stage overflow from domain errors, reduce steps only when mathematically justified, preserve attempt limits and stale exports; analytic forward/backward/overflow/underflow numerical and Chromium tests.
3. **P1 — Control transient convergence and plotting (planned).** Compare two RK4 step counts against analytic diagonal and coupled references, add trajectory graph handoff through existing Data Tables chart pipeline, keyboard/mobile/error tests; no duplicated graph engine.
4. **P1 — Saved-project Matrix/Graph/Table compatibility (planned).** Round-trip current and v1 project fixtures, malformed import atomic rollback, focus preservation, 390px browser checks.
5. **P1 — Engineering catalog verified expansion (planned).** Add source-backed canonical Control/GNSS/Signals/Statistics entries with honest planned/available states, unique IDs, keyboard/390px and no duplicate Run/solver tests.

**Execution checkpoint:** baseline dev 43d56e3f0f39902f384578b2047a933c1b454eff, main 56d5eaebec9e15f2dcbeb9a36f1e1a9180cee313. Source, offline bundle, unit/browser tests, workflow and documentation committed to dev in small commits; exact final dev SHA and new CI pending. Historical 166 gaps/95 partial remain frozen. No branch cleanup without verified merged/unprotected candidates.

## 2026-10-30 — Engineering multiword search (UI-ENGINEERING-MULTIWORD-032)

**Implemented on dev; exact-head CI and release pending.** Catalog search now matches whitespace-separated query terms in any order across tool title, description, ID, tags and readable discipline names. No catalog statuses or runnable actions changed. Source and offline bundle synchronized. Added tests/test_engineering_multiword_search.py covering reference matches, negatives, empty query and source/bundle parity. Full Python and Chromium Quality, PR checks, main Quality and Pages must be verified before release.

**NEXT FIVE with acceptance tests:** (1) exact-head Quality and PR #117 check/merge safety; full Python+Chromium green and verified Pages; (2) Control two-state transient response using shared numerical ODE with analytical forward/backward and browser/mobile recovery; (3) RK45 stage overflow recovery with bounded numerical failure references and stale export; (4) Matrix/Graph/Table project round-trip and focus preservation including legacy imports; (5) engineering catalog source-backed Control/GNSS/Signals/Statistics expansion, unique IDs and 390px keyboard tests.

## 2026-10-30 — Search Engineering tools by readable discipline name (UI-ENGINEERING-SEARCH-031)

**Implemented on dev; exact-head QA pending.** Engineering Toolbox search now matches full user-facing discipline names (for example “Aerospace engineering” and “GNSS positioning”) as well as canonical tool IDs, titles, descriptions and tags. This is navigation only; planned entries remain unimplemented and never obtain fake Run actions. Offline bundle synchronized. Added direct source/bundle regression and extended Chromium search and planned-action checks. Do not claim released before exact-head development/PR CI, main Quality and Pages.

**NEXT FIVE with acceptance:** (1) finish current exact-head Quality and PR, fix failures, verify main Quality/Pages; (2) Control 2-state transient response reusing numerical ODE, analytic forward/backward references and browser/mobile tests; (3) RK45 bounded stage-overflow recovery with forward/backward failure references and disabled-export checks; (4) saved-project Matrix/Graph/Table migration round-trip and focus tests; (5) Engineering catalogs expand only source-backed status-labeled Control/GNSS/Signals/Statistics tools with unique IDs, keyboard/390px tests.

**Execution checkpoint:** Began with dev c4f9ab090e996f13a3113de0a593345c91efd637, main 56d5eaebec9e15f2dcbeb9a36f1e1a9180cee313. Development Quality 41076680148 green, PR #117 opened; its PR checks were underway when implementing follow-up on dev. New SHA Quality/PR and Pages pending. Historical 166/95 counts remain unchanged.

## 2026-10-30 — RK45 difficult-workload rejection advisory (MATH-ODE-RK45-WORKLOAD-030)

**Implemented on dev, exact-head QA pending.** Adaptive scalar RK45 now records the longest consecutive rejection streak, includes it in attempt-exhaustion diagnostics, and warns after at least five rejected steps or a streak of three. This is a workload/accuracy advisory, **not** a stiffness diagnosis or global-error guarantee; numerical integration and accepted/rejected step decisions are unchanged. The UI warning disappears on successful smooth reruns and stale export actions remain disabled after errors. Source and standalone HTML synchronized; focused Node/Python forward/backward -100/+100 exponential references, invalid-input and exhaustion tests, plus mandatory Chromium 390px/stale-export recovery regression added. The existing historical inventory counts remain frozen.

**NEXT FIVE (status, dependencies, acceptance tests):**
1. **P1 — Exact-head RK45 workload QA and safe release (in progress).** Structural/unit suite, Chromium desktop/390px and project/browser regressions green on exact dev SHA; PR checks green, ordinary dev-to-main merge, main Quality and Pages confirmed.
2. **P1 — Engineering Toolbox Control/GNSS/Signals catalog QA (in progress).** Confirm nine unique disciplines, truthful planned actions, keyboard search, responsive layout, no duplicated numerical kernels; fix any CI regressions.
3. **P1 — Control transient response (planned).** Reuse bounded numerical ODE backend for 2-state xdot=−Ax+b; analytical reference trajectories, singular/invalid inputs, stale result and mobile tests.
4. **P1 — RK45 stage overflow recovery (planned).** Safely retry bounded stage overflows with reduced step only when mathematically appropriate; forward/backward stiff-like analytic references, bounded retry exhaustion, preserve domain-error messages.
5. **P1 — Saved-project compatibility (planned).** Legacy Matrix/Graph/Table imports, atomic rollback, keyboard focus and 390px browser round-trips.

**Execution checkpoint:** Started dev 3a5bc90bcfdada223fef88470bf5c2af2f87ecac, main 56d5eaebec9e15f2dcbeb9a36f1e1a9180cee313, no open PR; earlier CI pending. Exact new SHA, QA and deployment status require verification. No branch creation, CI bypass or cleanup without evidence.
