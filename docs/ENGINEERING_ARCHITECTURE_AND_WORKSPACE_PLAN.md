**Five additional planned disciplines (11–15):** [Statistics (80)](STATISTICS_ENGINEERING_TOOLBOX_FEATURE_LIST.md), [Data Science (90)](DATA_SCIENCE_TOOLBOX_FEATURE_LIST.md), [Materials & Alloys (80)](MATERIALS_METALLURGY_ALLOYS_TOOLBOX_FEATURE_LIST.md), [Structural Engineering (80)](STRUCTURAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md), [AI & Machine Learning (80)](AI_MACHINE_LEARNING_TOOLBOX_FEATURE_LIST.md). Provide separate searchable catalogs but reuse shared statistical models, dataframe transformations, optimization, linear algebra, FEA and visualization. [22 further candidate engineering domains](ADDITIONAL_ENGINEERING_TOOLBOX_CANDIDATES.md) require scope review before inclusion. These entries are not an implementation claim.

**Tenth discipline — Electromagnetics:** [163-feature Electromagnetics Toolbox Catalog](ELECTROMAGNETICS_TOOLBOX_FEATURE_LIST.md). Provide a separate searchable electromagnetic engineering toolbox for fields, waves, RF/microwave, antennas, EMC/EMI, computational EM and material models. Reuse canonical PDE, vector-calculus, units, material-property, plotting and signal-processing engines; do not fork duplicate solvers. The existing nine disciplines remain.

**Ninth discipline — Cryptography & Security:** [145-feature cryptography catalog](CRYPTOGRAPHY_SECURITY_TOOLBOX_FEATURE_LIST.md). Add a separate searchable cryptography toolbox for hashes, encryption, signatures, key exchange, certificates, secure communication and Python interoperability. Use vetted libraries, shared math and encoding utilities, safe key handling and explicit security-status labels. Existing eight disciplines remain.

**Eighth discipline — Signal Engineering:** [177-feature signal processing catalog](SIGNAL_ENGINEERING_TOOLBOX_FEATURE_LIST.md). Provide a separate searchable toolbox for waveform types, generation, decoding, filtering, communications coding, spectral analysis, estimation and signal pipelines. Reuse shared FFT/filter/estimation/plotting services and preserve sample rate, units, timestamps, calibration and channel metadata. Existing seven disciplines remain.

**Seventh discipline — GNSS & Positioning:** [144-feature catalog](GNSS_POSITIONING_OBSERVATION_TOOLBOX_FEATURE_LIST.md). Add GNSS/GPS/observation/position estimation as a selectable Engineering Toolbox discipline. Reuse shared geodesy, matrix/optimization, state-estimation, signal-processing and visualization services; never duplicate Kalman filters or coordinate transforms. Existing six disciplines remain.

**Control Theory Toolbox:** [181-feature comprehensive control catalog](CONTROL_THEORY_TOOLBOX_FEATURE_LIST.md). The control toolbox is a shared cross-discipline category and must use canonical registry IDs and reusable solvers.

# ProMathStudio — Reusable Architecture and Engineering Workspace Specification

**Status:** Approved future refactor and UI work; **not implemented by this documentation commit**. Preserve all existing user-facing features, offline operation and the standalone `index.html` distribution. Adopt incrementally with behavior-preserving automated tests; no large untested rewrite.

## Engineering Toolbox workspace

Add a fifth top-level workspace **Engineering Toolbox** alongside existing Calculator, Equation, Graph and Data Tables. It is a navigation and composition layer, not a fork of the math engine.

- A single clear workspace entry; avoid duplicate navigation actions, duplicated Run/Plot/Export buttons and tool-specific copies of common editors.
- Inside the workspace provide a searchable, filterable discipline selector: **Physics, Mechanical Engineering, Electrical Engineering, Electronics Engineering, Fluid Mechanics, Aerospace Engineering**. Each discipline opens its own grouped tool catalog, searchable by name, synonyms and tags; display short descriptions and available/not-yet-implemented status.
- Shared features (unit conversion, equations, ODEs, graphing, matrix tools, statistics, control, etc.) have **one canonical tool ID** and implementation. They may appear in several discipline catalogs as links to the same tool with discipline-specific defaults, terminology, examples or presets.
- Support category breadcrumbs, favorites/recent tools, keyboard search, compact mobile navigation, and consistent input/validation/results panels. Do not render controls for unimplemented features as though functional.
- A tool opens within the engineering workspace with contextual help, editable assumptions, units, parameter validation, results, plots, copy/export and a path back to the selected discipline. Preserve input drafts when navigating.
- Each tool's shared `Run`, `Plot`, `Reset`, `Copy`, `Export` commands belong in one contextual toolbar; show only applicable actions. No duplicate toolbar rows or repeated headings.
- Accessibility: semantic navigation, descriptive labels, keyboard support, focus management, screen-reader status, sufficient contrast, 390px+ responsive layout and no unintended horizontal scroll.
- User settings and previously saved projects remain backward compatible; the Engineering Toolbox must not disrupt current workspaces.

## Shared source architecture

Prefer explicit small modules and dependency injection over a monolithic HTML file or class hierarchies without need. Maintain one distributable `index.html` through the existing build pipeline.

```text
src/
  core/             # expression and numerical contracts; math backends
  shared/           # units, validation, result types, errors, formatting, history
  visualization/    # plotting primitives, reusable graphs and chart adapters
  ui/               # workspace router, navigation, toolbar, forms, accessibility
  engineering/
    registry/       # canonical tool metadata and cross-discipline mappings
    common/         # reusable domain calculations (not duplicated by discipline)
    physics/
    mechanical/
    electrical/
    electronics/
    fluids/
    aerospace/
tests/
  core/             # numeric and contract tests
  engineering/      # per-tool references and registry integrity
  ui/               # navigation, keyboard, responsive and duplicate-action checks
```

This is a **target organization**, not an assertion these directories exist. Migrate existing modules in small commits, reusing the current `src/` conventions and `scripts/build.py` rather than inventing a second bundler. Prefer composition, pure functions and small interfaces; use classes when managing stateful solver/session instances or polymorphic backends materially improves clarity.

## Stable reusable contracts

- **Tool definition:** stable ID, title, concise description, disciplines, category, tags, status, input schema, unit dimensions, assumptions, result schema, visualization capabilities, reference examples, version and optional standards applicability.
- **Solver:** typed/validated inputs → deterministic domain result or structured domain error; no direct DOM manipulation. Separate computation, UI and rendering.
- **Unit/quantity layer:** one dimensional analysis and conversion service with absolute/gauge and temperature-offset semantics; avoid silently combining incompatible quantities.
- **Common services:** symbolic/numeric evaluation, matrix/ODE/control primitives, plotting, project serialization, uncertainty, formatting, safe math expression parsing, history, export and accessibility components.
- **Registry:** one canonical tool per behavior, many discipline associations. Explicitly distinguish `planned`, `partial`, `implemented` and `verified`; metadata alone cannot upgrade status.
- **Safety:** never evaluate untrusted arbitrary code in the UI; maintain existing sandbox boundaries. Engineering outputs must show domain assumptions and limitations; standard-based checks identify edition and jurisdiction and do not claim certification.

## Refactor quality and performance gates

1. Establish current size, duplication and regression baseline: bundled HTML bytes, source bytes, script count, initial parse/load time, offline boot, mobile navigation and major workflow smoke tests.
2. Build tool registry and validate uniqueness, category references, no missing tool implementations and no duplicate command controls; initially register existing implemented tools only.
3. Extract reusable calculation and validation logic without altering behavior. Keep a stable API adapter for legacy code and storage formats.
4. Extract common UI primitives and contextual action bar; migrate one existing workspace at a time, preserving state, keyboard behavior and existing buttons until replacements pass tests.
5. Introduce the Engineering Toolbox navigation and discipline catalog as a separate incremental feature; expose planned entries clearly as future scope, not clickable fake calculators.
6. Migrate each discipline tool to shared contracts. Compare numerical reference outputs, singularities, units, error paths and plots before/after extraction.
7. Measure before/after bundle size and startup/performance; do not assume more files alone reduces shipped size. Prefer minimal dependency footprint and lazy tool activation where supported by offline bundling.
8. Ensure no new circular imports, global namespace collisions, duplicated algorithms, generated artifacts checked into source, or broken source/bundle consistency.
9. Keep README, AGENTS, roadmap, changelog, examples and tests aligned. Preserve protected-branch CI/PR release requirements.

## Engineering catalog and counting rules

- [Engineering Toolbox Feature Catalog](ENGINEERING_TOOLBOX_FEATURE_CATALOG.md): **148 broad feature families** across six disciplines, including shared math capabilities.
- [Electrical/Electronics deferred backlog](ELECTRICAL_ELECTRONICS_FUTURE_BACKLOG.md): **19 detailed future items**, potentially overlapping the above.
- [Historical feature audit](FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md): **158 existing capabilities (63 complete for bounded scope, 95 partial)** plus **166 gap/improvement opportunities**. Gaps may overlap partial capabilities.
- Do **not** add 148 + 19 + 166 + 158 as a unique-feature total; these are different granularity and overlapping catalogs. A complete deduplicated individual-feature registry with audited status is a separate deliverable.
- Six source Markdown files contain finer-grained individual feature requests not yet imported item-by-item. Preserve their scope when creating the detailed registry.

## Next five bounded deliverables and acceptance criteria

1. **Inventory and baseline:** machine-readable map of existing tool entry points, duplicate actions and modules, with measured bundle bytes and smoke-test baseline; no feature regression.
2. **Shared tool registry:** stable unique IDs, discipline associations, status, schema validation and unit tests proving cross-discipline deduplication.
3. **Reusable UI command bar:** one shared Run/Plot/Export toolbar with no duplicate controls; keyboard, mobile and state-preservation browser tests.
4. **Engineering Toolbox shell:** accessible fifth workspace with six discipline cards, searchable catalog and planned/available badges; existing four workspaces remain intact.
5. **First calculation extraction:** refactor one existing engineering/math tool to pure solver + validated inputs + shared visualization; reference numerical tests and unchanged offline bundle.
