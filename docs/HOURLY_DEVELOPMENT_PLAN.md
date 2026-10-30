# Hourly development plan — living queue

Current entries and the **Next five features** queue are kept here (newest first). Older execution entries are in [archive/HOURLY_DEVELOPMENT_LOG_ARCHIVE.md](archive/HOURLY_DEVELOPMENT_LOG_ARCHIVE.md); the frozen baseline is the [audited inventory](FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md).

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
