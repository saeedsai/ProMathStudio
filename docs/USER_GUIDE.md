# User guide

This guide lists every tool panel in ProMathStudio, grouped by workspace. For each tool it states
where to find it, what it computes (with the limitations the code and tests state), one worked
example whose expected output comes from that tool's own regression test in `tests/`, and how to
export results. The panel identifier in backticks (for example `brent-details`) is the HTML `id`
of the tool's collapsible panel; `tests/test_user_guide.py` checks that every panel and every
Engineering catalog entry is mentioned here, so the guide cannot silently fall behind the code.

Results are numerical or symbolic estimates within the stated scope. Nothing in ProMathStudio is a
certified engineering design check, a guaranteed global optimum or a proof of correctness.

## Getting started

1. **Open the app.** Open `index.html` directly from disk (it is one self-contained, offline file)
   or use the published GitHub Pages site. Use a current Chrome, Edge or Firefox with JavaScript.
   Only the optional SymPy engine and the Data Tables Python worker download code from a CDN on
   first use; everything else in this guide runs offline.
2. **Pick a workspace.** The workspace bar has five tabs: **Calculator**, **Equation**,
   **2D & 3D graphs**, **Data tables** and **Engineering Toolbox**.
3. **Pick a tool.** Each workspace has one **Workspace tools** dropdown that opens the matching
   panel. Each workspace remembers its last selected tool until the page reloads (this choice is not
   saved in the project). Most specialised tools are collapsible panels: click the panel title to
   open it.
4. **Find a tool by name.** Press `/` (when not typing in a field) or `Ctrl+K` / `⌘K` anywhere to
   focus **Find a tool**. Type words such as `integral`, `matrix`, `beam` or `units`, move through
   results with the arrow keys and press Enter to open one. Search only navigates: it never runs a
   computation or clears inputs. Every tool below is reachable this way.
5. **Move results between tools.** The **Working equation** panel at the bottom of each workspace
   holds one shared expression. Use **Send to** to route it, **Use open input** to capture the active
   tool's input, and **Add to current graph** to keep existing curves. Sending an equation such as
   `x^2=1` to a graph plots the residual `y=(x^2)-(1)`; sending an unsolved equation to Calculator does
   not pick a solution, so send an individual numeric root instead.
6. **Save your work.** **Save project** downloads one JSON file (equations, calculator history,
   graph settings, Data Tables and saved tool state); **Open project** restores it. Browser storage
   is not a backup. See [Workspaces and project format](PROJECT_FORMAT.md).

Most numerical tools have a **Save to Data Tables** button. From Data tables you can then export
CSV, formulas CSV, TSV, JSON or XLSX, or press **Show in graphs**. That is the common export path
referred to below as *Save to Data Tables → export*.

## Keyboard and accessibility

These shortcuts are implemented in the code (`src/tool-search.js`, `src/matrix-tools.js`,
`src/numerical-data.js`, `src/context-actions.js`, `src/optimization-tools.js`,
`src/graph-curves.js`, `src/vector-fields.js`, `src/polynomial-tools.js`, `src/units-tools.js`,
`src/precision-tools.js` and the inline workspace code in `index.html`).

| Where | Key | Action |
| --- | --- | --- |
| Anywhere (outside text fields) | `/` | Focus **Find a tool** |
| Anywhere | `Ctrl+K` / `⌘K` | Focus **Find a tool** |
| Find a tool | `↓` / `↑`, Enter, Escape | Choose a result, open it (or the first available match), close the list (a second Escape clears the query) |
| Workspace bar | `←` / `→`, Home, End | Move focus between workspace tabs (Enter/Space activates) |
| Calculator input | Enter | Calculate |
| Equation editor input | Enter / Shift+Enter | Add equation / insert a text line |
| Equation editor (editing a saved entry) | Escape | Cancel the edit |
| Equation workspace (CAS input) | `Ctrl+Enter` / `⌘Enter` | Execute the symbolic operation |
| Linear programming text box | `Ctrl+Enter` / `⌘Enter` | Solve the LP |
| Polynomial, Units, Decimal expression, Curves and Vector-field inputs | Enter | Run / Convert / Evaluate / Plot |
| Matrix grids | Arrow keys | Move between cells (never changes a value) |
| Matrix grids | Home / End, `Ctrl+Home` / `Ctrl+End` | First/last cell in the row, first/last cell of the grid |
| Data tables menu bar | `←` / `→`, Home, End | Move between the Table/Filter/Combine/Files/Python menus |
| Data tables menus and previews | Escape | Close the open menu or preview and return focus |
| Table cell, row/column header, tab, Calculator, Editor, Solver, Graph | Shift+F10 or the Menu key | Open the context menu (right-click / long-press also work) |
| Context menu, Symbols library | Escape | Close and return focus to the trigger |

Tab moves through all controls in order. Result areas are `role="status"` live regions, so screen
readers announce results and errors. Controls aim for at least 40 px touch targets and the layout
avoids horizontal scrolling at phone widths. Engineering animations respect the
`prefers-reduced-motion` setting (they render the final frame instead of animating). Some clipboard
features need HTTPS, localhost or browser permission; downloading the editable `.docx` is more
reliable than pasting clipboard HTML into Word.

---

## Calculator workspace

### Calculate (basic calculator)

- **Where:** Calculator → Workspace tools → *Calculate*.
- **Computes:** scalar numeric expressions (binary64), real or complex (`sqrt(-1)` shows `i`), with
  **Ans**, history, Radians/Degrees and display precision. Only numeric expressions are calculated;
  send equations with unknowns to the Equation workspace.
- **Example (`tests/smoke_browser.py`):** `5!+3^2` → `129`.
- **Export:** **Copy and send results** (`ui-calc-more-actions`) copies the result or sends it to the
  Working equation, Solver or 2D graph.

Related disclosures: **Angle, precision and number display** (`ui-calc-settings`, task
*Number settings*; example from `tests/smoke_visual_options.py`: with number format *Auto*, `1/2` → `= 0.5`),
and **History and examples** (`ui-calc-history`, task *History*).

### Variables and advanced numeric math

- **Where:** Calculator → Workspace tools → *Variables* (panel `calc-variable-panel`).
- **Computes:** one `name=value` assignment per line, plus `diff`, `int`, `sum` and `prod` with
  evaluation points and bounds. Results are numerical approximations.
- **Example (`tests/smoke_numerical_data.py`):** variables `x=2` and `y=3`, then `x^2+y^2` → `= 13`;
  `int(x^2,x,0,3)` → `9`, `sum(k^2,k,1,10)` → `385`.
- **Export:** as for Calculate.

### Binary · Hex · Bitwise tools

- **Where:** Calculator → **Binary · Hex · Bitwise tools** disclosure above the keypad; the DEC/BIN/HEX
  input radix is in **Angle, precision and number display**.
- **Computes:** `0b`/`0x` literals and `band`, `bor`, `bxor`, `bnot`, `shl`, `shr`. Binary/hex
  arithmetic is limited to exact 53-bit integers; standalone integer literal conversion uses BigInt.
- **Example (`tests/smoke_context_actions.py`):** in DEC mode `0b1010+0xF` → `= 25`;
  `bxor(15,3)` → `= 12`.
- **Export:** as for Calculate. See [Context menus and number bases](CONTEXT_MENUS.md).

### Matrix calculator · 2×2 / 3×3

- **Where:** Calculator → Workspace tools → *Matrices* (panel `matrix-tools`, with optional input
  sections `mat-rhs-section`, `mat-weight-section` and `mat-b-section`).
- **Computes:** determinant, transpose, inverse, A±B, A×B, solve A·x=b, LU (P·A=L·U), QR, least
  squares, weighted least squares, symmetric eigenanalysis, SVD, pseudoinverse, RREF and rank.
- **Limits (from the panel note):** real 2 or 3 rows/columns. Determinant and inverse need square A;
  LU needs a full-rank square A; QR needs rows ≥ columns and independent columns; least squares needs
  a full-rank tall 3×2 A; weighted least squares accepts three positive relative weights (1e-12 to
  1e12) that are *relative priorities, not certified inverse variances*; eigenanalysis needs a
  symmetric A; SVD and pseudoinverse support 2×2, 3×2, 2×3 and 3×3 with a relative 1e-12
  singular-value cutoff. Results show about 12 significant digits.
- **Example (`tests/smoke_matrix_solve.py`):** A = `[[1,2],[3,4]]`, b = `[5,11]`, **Solve A·x=b** →
  x = `[1, 2]` with relative residual ≤ 1e-8; the output reports `solve:` and `Relative residual:`.
- **Export:** **Send result to Equation Editor** puts `matrix([1],[2])` into the Working equation.
  See [Matrix calculator](MATRIX_CALCULATOR.md) and [Matrix eigenanalysis](MATRIX_EIGEN.md).

### Matrix extras · up to 8×8

- **Where:** Calculator → *Matrix extras* panel (`matrix-extras-details`).
- **Computes:** Cholesky A = L·Lᵀ, LDLᵀ, rank with null/column-space bases, determinant and trace
  (LU), characteristic polynomial, norms and condition number. Decimal entries only, one row per
  line; non-symmetric or non-positive-definite input is rejected for Cholesky.
- **Example (`tests/test_matrix_extras.py`):** Cholesky of
  `4 12 -16 / 12 37 -43 / -16 -43 98` → L = `[[2,0,0],[6,1,0],[-8,5,3]]`.
- **Export:** **Save to Data Tables** → export.

### High-precision decimal arithmetic

- **Where:** Calculator → Workspace tools → *High precision* (`precision-details`).
- **Computes:** exact decimal +, − and ×; division rounded to 16–80 significant digits (ties to
  even). The **Decimal expression** box adds parentheses, unary signs and exact `^` with integer
  exponents 0–20. Plain decimal operands only, up to 300 digits; no scientific-notation input,
  negative/fractional powers or transcendental functions. Separate from the binary64 Calculator.
- **Example (`tests/smoke_precision.py`):** `0.1` + `0.2` → `0.3`; `1 ÷ 3` at 40 digits →
  `0.3333333333333333333333333333333333333333`. Expression example
  (`tests/smoke_precision_expression.py`): `(2+3)/(5*2)` → `0.5`.
- **Export:** copy the shown result; optional *Also show scientific notation* adds an `e`-notation view.

### Polynomial tools

- **Where:** Calculator → *Polynomial tools* panel (`poly-details`).
- **Computes:** all complex roots (Aberth–Ehrlich) with multiplicity clustering, Horner evaluation
  of p and p′, derivative, integral, add, multiply, long division and numerical GCD. Coefficients
  are highest degree first; complex values use `a+bi`. Maximum degree 30; multiplicities and the GCD
  are numerical estimates with the stated tolerance.
- **Example (`tests/test_polynomial_tools.py`):** coefficients `1, -3, 2` → roots `1` and `2`
  (backward error < 1e-14); `1, 0, 1` → `±i`.
- **Export:** **Save to Data Tables** → export.

### Unit conversion and dimensional analysis

- **Where:** Calculator → *Unit conversion* panel (`units-details`).
- **Computes:** conversion between SI base, prefixed, derived and exact NIST US customary units, and
  dimensional analysis (leave *To unit* empty to simplify to SI base units). Absolute °C/°F applies to
  bare temperatures only; inside compound units temperatures are differences. Unit names are
  case-sensitive. Binary64 results.
- **Example (`tests/test_units_tools.py`):** `1` `mi` → `m` gives `1609.344`; `100 degC` → `degF`
  gives `212`; `1 m` → `s` is rejected with "Dimension mismatch".
- **Export:** copy the result text.

---

## Equation workspace

The Equation workspace combines the equation editor, live preview, symbolic solver, Python/SymPy
code, notebook and the numerical panels. Its Workspace tools dropdown groups tasks as *Write &
solve*, *Notebook & examples*, *Numerical & differential* and *Solver configuration*.

### Write or solve equation (editor and symbolic solver)

- **Where:** Equation → Workspace tools → *Write or solve equation*.
- **Computes:** live math preview and notebook entries; symbolic Auto, Expand, Simplify, Factor,
  Solve, Solve system, Differentiate, Integrate, plus SymPy-only Limit, Numerical roots,
  Laplace/Fourier transforms and their inverses, ODE (`dsolve`) and PDE (`pdsolve`). Engines: Auto
  (offline first), Built-in (offline only) or SymPy (needs internet on first load). SymPy may return
  `RootOf` or numerical roots rather than radicals.
- **Example (`tests/smoke_browser.py`):** input `(x-1)^2`, engine Built-in, operation **Expand** →
  at least one result equation is produced. Typical: `x^2=1` solves to ±1 and `x^2=-1` to ±i.
- **Export:** **Copy and export equation** (`ui-editor-export-actions`): Copy LaTeX, Copy for Word,
  Copy image, Word `.docx`, plus **Export .tex**; results have their own **Send to…** route. See
  [Exports](EXPORTS.md) and [Symbolic engines](SYMBOLIC_ENGINE.md).

The floating **∑ Symbols** button opens the searchable symbol library (also in Calculator and Graphs);
choose a template to insert it at the caret. Some notation is typesetting-only.

### Try examples, My equations, Python code

- **Where:** Equation → Workspace tools → *Try examples* (`examples`), *My equations* (`notebook`),
  *Python code* (`ui-editor-python`).
- **Computes:** example insertion, saved notebook entries and generated SymPy code. Review generated
  code before running it elsewhere.
- **Example (`tests/smoke_browser.py`):** add `(x-1)^2` with **Add equation** → the notebook counter
  shows `(1)`.
- **Export:** copy the generated Python; notebook entries are saved in the project file.

### Assumptions

- **Where:** Equation → Workspace tools → *Assumptions* (`ui-solver-assumptions`).
- **Computes:** optional real/positive/negative/integer restrictions passed to SymPy.
- **Example (`tests/smoke_symbolic_assumptions.py`):** `x^2=1` solved with *positive* →
  `Eq(x, 1)`; `sqrt(x^2)` simplified with *positive* → `x`.
- **Export:** as for the symbolic solver.

### Numerical methods · nonlinear equations and PDEs

- **Where:** Equation → Workspace tools → *Numerical methods* (`num-details`).
- **Computes:** real roots in an interval, small (2–3 equation) nonlinear systems from initial
  guesses, 1D Poisson −u″=f with Dirichlet ends, and explicit heat u_t=αu_xx. The heat method requires
  α·Δt/Δx² ≤ 0.5 and rejects unstable steps. Results are approximate, not general symbolic solutions.
- **Example (`tests/smoke_numerical_data.py`):** `sin(x)-x/2=0` on [−4, 4] → roots ≈ −1.895494267,
  0, 1.895494267; system `x^2+y^2=5; x-y=1` from guess `1,1` → (2, 1).
- **Export:** **Save output to Data Tables** or **Show numerical results in Graphs**. See
  [Numerical methods and Python](NUMERICAL_AND_PYTHON.md).

### Bracketed root · Brent–Dekker

- **Where:** Equation → Numerical methods panel → *Bracketed root* (`brent-details`).
- **Computes:** one real root of a continuous f(x)=0 inside a bracket whose endpoints have opposite
  signs. No root is claimed without a sign change; poles inside the bracket are guarded.
- **Example (`tests/smoke_root_brent.py`):** `x^3-x-2` on [1, 2] → x ≈ `1.5213797068045676`
  (|f| < 1e-7).
- **Export:** **Save to Data Tables** → export.

### 1D minimization · golden-section search

- **Where:** Equation → Numerical methods panel (`minimize-details`).
- **Computes:** an approximate minimum of a real, continuous, unimodal f(x) on [a, b]. Multimodal
  functions are not guaranteed; only a local minimum is found.
- **Example (`tests/smoke_minimize_golden.py`):** `(x-2)^2+1` on [0, 4] → x ≈ 2, f ≈ 1.
- **Export:** **Save to Data Tables** → export.

### Optimization · linear programming and Nelder–Mead

- **Where:** Equation → Numerical methods panel (`optimization-details`).
- **Computes:** linear programs (`max:`/`min:` objective in x1…x10, up to 10 variables and 10
  constraints, `<=`, `>=`, `=`; `#` comments) reporting optimal, infeasible or unbounded; and local
  derivative-free Nelder–Mead minimisation of 2–3 variables with optional bounds.
- **Example (`tests/test_optimization_tools.py`):** `max: 3x1 + 5x2`, `x1 <= 4`, `2x2 <= 12`,
  `3x1 + 2x2 <= 18` → optimal x = (2, 6), objective 36. Nelder–Mead on Rosenbrock from (−1.2, 1) →
  (1, 1).
- **Export:** **Save to Data Tables** (each method) → export.

### ODE initial-value problem · RK4 / RK45 / coupled RK4

- **Where:** Equation → Workspace tools → *ODE initial values* (`ode-details`).
- **Computes:** scalar dy/dt=f(t,y) by fixed-step RK4 or adaptive RK45, or two coupled equations by
  fixed-step RK4, with step-doubling error estimates. Not a stiff solver.
- **Example (`tests/smoke_ode.py`):** `dy/dt = y`, y(0)=1 on [0, 1] with 100 RK4 steps →
  y(1) = e within 1e-9; `dy/dt = t`, y(0)=0 → y(1) = 0.5.
- **Export:** **Save output to Data Tables** or **Plot y(t) in Graphs**.

### Stiff ODE · implicit adaptive TR-BDF2

- **Where:** Equation → ODE section, directly after the ODE panel (`stiff-ode-details`).
- **Computes:** stiff scalar or two-state IVPs with relative/absolute tolerances (implicit, adaptive
  TR-BDF2 with Newton iterations). Leave dz/dt empty for a scalar equation.
- **Example (`tests/test_stiff_ode.py`):** `dy/dt=-1000*(y-cos(t))`, y(0)=0 on [0, 1],
  rtol 1e-6, atol 1e-9 → relative error vs the exact solution below 1e-4 with fewer than 500
  accepted steps.
- **Export:** **Save to Data Tables** → export.

### Boundary-value problem · shooting

- **Where:** Equation → ODE section, after the stiff solver (`bvp-details`).
- **Computes:** y″ = f(x, y, y′) on [a, b] with Dirichlet, Neumann or Robin conditions by scanning
  and refining the unknown initial value. It reports whether the solution is unique, multiple,
  non-unique or not found within the scan range; it does not prove that no other solutions exist
  outside that range.
- **Example (`tests/test_bvp_tools.py`):** Bratu `f = -exp(y)`, y(0)=0, y(1)=0, scan 0–15 →
  status *multiple*, two solutions with y′(0) ≈ 0.549353 and ≈ 10.8469.
- **Export:** **Save to Data Tables** → export.

### Signal spectrum · offline FFT

- **Where:** Equation → Numerical methods panel (`fft-details`).
- **Computes:** FFT of 4–256 uniformly sampled real values (power-of-two length) with one-sided
  amplitude, correct DC/Nyquist scaling, sampling rate and optional periodic Hann window. Bin k means
  k cycles per window unless the sample rate is known.
- **Example (`tests/smoke_fft.py`):** default samples `0, 1, 0, -1, 0, 1, 0, -1` at 8 Hz →
  output contains `Peak bin 2`.
- **Export:** **Save spectrum to Data Tables** or **Plot amplitude in Graphs**. See [FFT](FFT.md).

### Digital filters

- **Where:** Equation → Numerical methods panel, next to the FFT (`filters-details`).
- **Computes:** Butterworth IIR low/high-pass (order 1–8, second-order sections, bilinear transform
  with pre-warping), windowed-sinc FIR low/high/band-pass (up to 501 taps) and moving average, causal
  or zero-phase (forward–backward). Causal filtering delays the signal.
- **Example (`tests/smoke_signal_filters.py`):** 64 samples of sin(2π·4t)+sin(2π·28t) at 64 Hz,
  6th-order Butterworth low-pass at 10 Hz, zero-phase → output peak at 4 Hz with amplitude ≈ 1 and
  the 28 Hz component below 0.01.
- **Export:** **Save filtered signal to Data Tables** → export.

### 1D interpolation

- **Where:** Equation → Numerical methods panel (`interp-details`).
- **Computes:** linear, PCHIP, barycentric polynomial (2–16 points), natural/clamped/not-a-knot/
  periodic cubic splines, Akima and modified Akima. Query values must lie inside the sample domain:
  interpolation is not extrapolation or smoothing.
- **Example (`tests/smoke_interpolation_linear.py`):** samples (0,1), (1,3), (2,5), queries
  `2, 0.5, 0, 1.5, 1` (linear) → sorted rows (0,1), (0.5,2), (1,3), (1.5,4), (2,5).
- **Export:** **Save to Data Tables** or **Plot in Graphs**; **Load active table x/y** reads samples from Data Tables.

### Multiple and discrete integrals

- **Where:** Equation → Numerical methods panel (`integration-details`).
- **Computes:** double integrals with variable y-limits, triple integrals over a box (adaptive
  Gauss–Kronrod G7-K15) and trapezoid/Simpson integration of two Data Table columns. The error
  estimate is *not a certified bound*; singular integrands and exhausted evaluation budgets are
  refused. Simpson is skipped for non-uniform or odd interval counts.
- **Example (`tests/smoke_integration_tools.py`):** ∫₀¹∫₀¹ `x*y` dy dx → 0.25; triple `x*y*z` over
  the unit cube → 0.125; discrete x = 0, 0.5, 1, 1.5, 2 with y = x² → trapezoid 2.75, Simpson 8/3.
- **Export:** **Save to Data Tables** → export.

### Numerical derivatives and vector calculus

- **Where:** Equation → Numerical methods panel (`vectorcalc-details`).
- **Computes:** derivatives up to higher order, gradient, Hessian, Jacobian, divergence, curl,
  Laplacian and directional derivatives at a point by Ridders extrapolation, with error estimates
  that are a heuristic, not certified.
- **Example (`tests/smoke_vector_calculus.py`):** derivative of `sin(x)` at x=1 → cos(1);
  gradient of `x^2*y+z^3` at (1, 2, 3) → (4, 1, 27); curl of `-y; x; 0` → (0, 0, 2).
- **Export:** **Save to Data Tables** → export.

### Statistics · distributions, descriptive statistics and hypothesis tests

- **Where:** Equation → Numerical methods panel (`stats-details`).
- **Computes:** density/mass, CDF, survival and quantile for normal, Student t, chi-square,
  exponential, binomial and Poisson; descriptive statistics of a Data Tables column; one-sample,
  Welch, pooled and paired t-tests, chi-square, proportion, binomial and variance tests with
  confidence intervals.
- **Example (`tests/test_statistics_tools.py`):** standard normal CDF at 1.96 →
  0.9750021048517795; describe `1…9, 100` → n 10, mean 14.5, median 5.5, IQR 4.5.
- **Export:** **Save to Data Tables** → export.

### Uncertainty · error propagation and Monte Carlo

- **Where:** Equation → Numerical methods panel (`uncertainty-details`).
- **Computes:** first-order GUM propagation (with optional correlations and coverage factor k) and
  seeded Monte Carlo sampling, flagging when the two disagree because the model is nonlinear.
- **Example (`tests/test_uncertainty_tools.py`):** y = `a+b`, a = 1 ± 0.3, b = 2 ± 0.4 (normal) →
  y = 3, u_c = 0.5, expanded U = 1.0 with k = 2; a's contribution is 36 %.
- **Export:** **Save samples summary to Data Tables** → export.

### Inequalities and function domain analysis

- **Where:** Equation → Numerical methods panel (`function-analysis-details`).
- **Computes:** solution sets of f(x) <, ≤, >, ≥ or = g(x) on [a, b] as a union of intervals with correct
  strict/non-strict endpoints, excluding poles found by the shared scalar root finder. It also reports the
  sampled real domain, zeros, poles, local extrema, a grid-estimated range, monotonic pieces and even/odd
  symmetry. All results are numerical estimates on a sampling grid.
- **Example (`tests/smoke_function_analysis.py`):** `x^2-4 < 0` on [−5, 5] → (−2, 2); with `<=` → [−2, 2];
  `sin(x) >= 0.5` on [0, 2π] → [π/6, 5π/6].
- **Export:** **Save to Data Tables**.

### Seeded random numbers and Monte Carlo integration

- **Where:** Equation → Numerical methods panel (`random-details`).
- **Computes:** PCG32-seeded samples (uniform, normal, exponential, gamma, beta, Poisson, binomial,
  weighted discrete, permutations, sampling without replacement; up to 100,000 values, saved as columns of
  at most 6,000 rows) and plain Monte Carlo (with standard error) or Halton quasi-Monte Carlo integration
  over boxes in up to 6 dimensions. The same seed always gives the same output.
- **Example (`tests/smoke_random_tools.py`):** ∫∫ x·y over the unit square ≈ 0.25 within 3 standard errors.
- **Export:** **Save to Data Tables** for samples and integration results.

### GNSS least-squares positioning

- **Where:** Equation → Numerical methods panel (`gnss-details`), also opened from the Engineering
  catalog entry `gnss.positioning.least.squares`.
- **Computes:** a weighted Gauss–Newton single-epoch fix from 4–16 satellite ECEF positions and
  pseudoranges. It reports receiver position, clock bias, residuals, σ0, covariance, GDOP/PDOP/HDOP/VDOP/TDOP,
  WGS-84 latitude/longitude/height and a sky plot. There are no ionosphere, troposphere, relativity or Sagnac
  corrections and no ephemeris decoding. Singular geometry is rejected.
- **Example (`tests/smoke_gnss_tools.py`):** exact synthetic pseudoranges around 59.33° N, 18.06° E, 30 m
  with a 1e-4 s clock bias recover the position to better than 1e-4 m.
- **Export:** **Residuals to Data Tables**.

---

## 2D & 3D graphs workspace

### Plot functions

- **Where:** 2D & 3D graphs → Workspace tools → *Plot functions*.
- **Computes:** one or more 2D curves `y=f(x)`, 3D surfaces `z=f(x,y)` and constrained 3D curves.
  Trigonometric inputs use radians. Pan/rotate with the pointer, zoom with the wheel, **Reset view**.
- **Example (`tests/smoke_browser.py`):** in 3D, `Y=x×x` and `z=sin(x×y)` on separate lines →
  status `1 surface(s) and 1 constrained 3D curve(s)`.
- **Export:** **Export PNG**; **Send graph function to another workspace**
  (`ui-graph-share-actions`). See [2D / 3D graphing](GRAPHING.md).

### Axis limits and advanced graph settings

- **Where:** 2D & 3D graphs → Workspace tools → *Axis limits* (`ui-graph-axes`, inside
  **Axis ranges and advanced graph settings**, `graph-controls-collapsible`), and **Axes & grid**
  next to the 2D/3D switch.
- **Computes:** X/Y/Z minimum and maximum and a shared grid spacing (blank = automatic).
- **Example (`tests/smoke_graph_import.py`):** after importing x = 0, 1, 2, **Fit axes to data** sets
  X max above 2.
- **Export:** settings are saved in the project.

### Appearance · colors and styles

- **Where:** 2D & 3D graphs → Workspace tools → *Appearance* (`graph-appearance`).
- **Computes:** palette, line style, width and per-series colours for equation plots and table charts.
- **Example (`tests/smoke_visual_options.py`):** palette *bright*, then plotting `y=x^2` → series 0
  colour `#536be8`; choosing `#ff8844` in the colour picker changes series 0 to `#ff8844`.
- **Export:** saved in the project; visible in **Export PNG**.

### Plot table data and curve-fit diagnostics

- **Where:** 2D & 3D graphs → Workspace tools → *Plot table data* (`ui-graph-table`).
- **Computes:** scatter/line charts of a numeric Data Table and least-squares fits with R², RMSE,
  MAE and the number of included measurements. Exponential/Gaussian need positive y;
  logarithmic/power also need positive x. Statistics describe the model and data, not significance
  or global optimality.
- **Example (`tests/smoke_fit_diagnostics.py`):** points (x, 2x+3) for x = 0…4, linear fit →
  5 points used, R² = 1, RMSE < 1e-10.
- **Export:** **Export residuals CSV** (`x,y,predicted,residual`, enabled only after a successful
  fit); the source table is unchanged.

### Nonlinear least-squares fit · Levenberg–Marquardt

- **Where:** 2D & 3D graphs → *Nonlinear least-squares fit* panel (`nlfit-details`).
- **Computes:** weighted nonlinear least squares for y ≈ f(x; parameters) from typed lists or Data
  Table columns, with optional bounds, standard errors and confidence intervals. It reports a local
  optimum from your initial guesses; a global optimum is not guaranteed, and non-identifiable or
  bound-limited parameters are warned about.
- **Example (`tests/test_nonlinear_fit.py`):** model `a*exp(-b*x)+c`, guesses a=1, b=1, c=0, exact
  data y = 2·e^(−0.5x)+1 → a = 2, b = 0.5, c = 1 (within 1e-8).
- **Export:** **Save residuals to Data Tables** → export.

### Complex numbers · Argand plane and |f(z)| surface

- **Where:** 2D & 3D graphs → *Complex numbers* panel (`complex-graph-workbench`).
- **Computes:** f(z) = z, z², 1/z or exp(z) for one point z = a+bi on the Argand plane, or |f(z)| as a
  3D surface. Separate from real-valued equation plots; 1/z at 0 is undefined.
- **Example (`tests/smoke_complex_graph_module.py`):** z = 1 + 2i with f(z) = z² → status
  `Plotted Argand point.` and `f(z) = -3 + 4i`.
- **Export:** **Export PNG** of the graph canvas.

### Implicit, parametric and polar curves

- **Where:** 2D & 3D graphs → *Implicit, parametric & polar curves* panel (`curves-details`).
- **Computes:** F(x, y) = 0 by marching squares with refined edge crossings (sign changes across
  poles or jumps are rejected and counted), parametric (x(t), y(t)) and polar r(θ) polylines that break
  at non-finite samples. Radian angles.
- **Example (`tests/smoke_graph_curves.py`):** `x^2 + y^2 = 1` on a 300-cell grid → more than 400
  segments, 0 rejected, every vertex within 1e-6 of radius 1.
- **Export:** **Save points to Data Tables** or **Overlay on main 2D graph**.

### Vector fields, streamlines and slope fields

- **Where:** 2D & 3D graphs → *Vector fields* panel (`fields-details`).
- **Computes:** normalised arrows coloured by |v|, RK4 streamlines from clicked seeds, slope-field
  solutions of dy/dx = f(x, y), animated particles and candidate equilibria. Equilibria are a
  sign-change heuristic refined by Newton: check them analytically.
- **Example (`tests/smoke_vector_fields.py`):** field (P, Q) = (−y, x) → one candidate equilibrium at
  the origin, classified as a centre.
- **Export:** **Save curve points to Data Tables** → export.

### Control Theory Toolbox

- **Where:** 2D & 3D graphs → *Control Theory Toolbox* panel (`control-theory-toolbox`).
- **Computes:** Bode, Nyquist, root locus, Routh–Hurwitz and unity-feedback response for
  continuous-time SISO transfer functions with real coefficients (highest power first). Bode/Nyquist
  sample ω = 0.01–1000 rad/s; root locus samples 0 ≤ K ≤ 100. A numerical analysis workspace, not a
  certified stability tool.
- **Example (`tests/test_control_numerical_reference.py`):** G(s) = 1/(s+1) at ω = 1 rad/s →
  0.5 − 0.5i, magnitude −3.0103 dB; Routh array of `1, 3, 2` → 0 sign changes.
- **Export:** the plot canvas and text output; see the state-space panels below for Data Tables export.

### State equilibrium · real 2×2 / 3×3

- **Where:** Control Theory Toolbox → *State equilibrium* (`ct-equilibrium`).
- **Computes:** x* with A·x* = b for ẋ = −A·x + b, using the shared matrix solver, and an optional
  stability check for *symmetric* A by real eigenvalues. A unique equilibrium does not establish
  stability; values are dimensionless.
- **Example (`tests/test_control_equilibrium.py`):** A = `[[2,1],[1,3]]`, b = `[5,7]` →
  x* = (1.6, 1.8); a singular A is rejected.
- **Export:** copy the text output.

### Two-state transient response · fixed-step RK4

- **Where:** Control Theory Toolbox → State equilibrium → *Two-state transient response*
  (`ct-eq-transient`).
- **Computes:** a fixed-step RK4 trajectory of ẋ = −A·x + b for a real 2×2 A using the shared ODE
  solver; not stiff or error-certified, so compare step counts.
- **Example (`tests/test_control_transient.py`):** A = diag(2, 3), b = (4, 9), x(0) = 0, t ∈ [0, 1],
  80 steps → 81 rows; final state ≈ (2(1−e⁻²), 3(1−e⁻³)) within 1e-7.
- **Export:** **Save trajectory to Data Tables** or **Plot both states in Graphs**.

---

## Data tables workspace

### Edit table and spreadsheet formulas

- **Where:** Data tables → Workspace tools → *Edit table*.
- **Computes:** a grid of up to 6,000 rows × 32 columns with formulas `SUM`, `AVERAGE`, `COUNT`,
  `MIN`, `MAX`, `MEDIAN`, lazy `IF`, and local or quoted cross-sheet references. Out-of-range
  references give `#REF!`; `MEDIAN` with no numeric values gives `#NUM!`. Not full Excel
  compatibility.
- **Example (`tests/smoke_sheet_median.py`):** `=MEDIAN(1,2,3,4)` → 2.5; with A1:A3 = 1, 4, 8,
  `=MEDIAN(A1:A3)` → 4.
- **Export:** Files menu → **Export CSV**, **Export formulas CSV**, **Export TSV**, **Export JSON**;
  **Show in graphs**. See [Data tables](DATA_TABLES.md).

### Filter and sort, Combine tables, Import / Export, Python

- **Where:** Data tables → Workspace tools → *Filter and sort*, *Combine tables*, *Import / Export*,
  *Python* (the five menus in the data menu bar).
- **Computes:** row filters (displayed rows only; source rows are unchanged) and sorting; inner, left,
  right and full joins, unions and comparisons into a new table; CSV/TSV/JSON import with a preview;
  and your own Python (pandas) in a sandboxed browser worker with no DOM access. Python downloads
  Pyodide from a CDN on first use and only runs when you click Run; only run trusted code.
- **Example (`tests/smoke_data_join_index.py`):** inner join on `key` of Left
  `[1,L1],[1,L2],[2,L3],['',L4]` with Right `[1,R1],[1,R2],[3,R3],['',R4]` → five rows:
  L1×R1, L1×R2, L2×R1, L2×R2 and the blank-key pair L4×R4.
- **Export:** results are new tables; use the Files menu exports. See
  [Data import](DATA_IMPORT.md).

### Functions and Code Library

- **Where:** Data tables → *Functions & Code Library* (`dt-code-library`).
- **Computes:** searchable formula and Python snippets inserted into the selected cell or the Python
  editor; user snippets can be saved and exchanged.
- **Example (`tests/smoke_data_code_library.py`):** select C1, search `sum` and insert →
  C1 = `=SUM(A1:A5)`, with the message `Inserted SUM into C1`.
- **Export:** saved snippets are kept in the project.

### Advanced dataset preview and CSV/JSON graph import

- **Where:** Data tables → *Advanced dataset preview / X, Y, Z mapping* (`dt-advanced`), which
  contains *Import CSV / JSON data to graph* (`graph-data-panel`).
- **Computes:** imports numeric CSV, TSV or JSON rows (up to 1 MB / 6,000 rows) and maps columns to
  X, Y and Z as scatter, connected path or 3D grid overlays on the equation plot.
- **Example (`tests/smoke_graph_import.py`):** `time,value,note` with three rows → 3 points imported;
  the quoted note `"a,b"` stays one cell.
- **Export:** **Remove data** / **Fit axes to data**; the plot is exported with **Export PNG**.

### Multivariate analysis · correlation, PCA and k-means

- **Where:** Data tables → *Multivariate analysis* panel (`multivariate-details`).
- **Computes:** covariance (n−1), Pearson and Spearman (average ranks for ties) correlation with a
  scatter matrix, PCA (symmetric Jacobi eigendecomposition, standardized or centred) and seeded
  k-means++ with Lloyd iterations, for 2–12 numeric columns. Rows with a blank or non-numeric
  selected cell are dropped and counted.
- **Example (`tests/test_multivariate_tools.py`):** table columns a = 1, 2, 3, 4, 5 and
  b = 2, (blank), 6, 8, 10 → n = 4, 1 row dropped, Pearson r = 1.
- **Export:** **Save results to Data Tables** → export.

### Excel XLSX export

- **Where:** Data tables → *Excel XLSX export* panel (`xlsx-export-details`).
- **Computes:** a `.xlsx` of one or two selected sheets (up to 1,000 data rows each) with text,
  numbers and formulas. Formula references shift by one row because the header occupies row 1.
- **Example (`tests/smoke_xlsx_export.py`):** sheets *Sales 2026* (formulas `=A1+B1`,
  `=SUM(A1:A2)`) and *Budget* → workbook sheets `Sales 2026`, `Budget` with formulas `A2+B2` and
  `SUM(A2:A3)`.
- **Export:** **Download XLSX**.

### Excel XLSX import

- **Where:** Data tables → *Excel XLSX import* panel (`xlsx-import-details`).
- **Computes:** imports up to two sheets and 1,000 rows per sheet (5 MB ZIP / 12 MB expanded),
  replacing current sheets after confirmation. Unsupported Excel features are rejected, not silently
  discarded.
- **Example (`tests/smoke_xlsx_import.py`):** round-trip of an exported workbook → sheets
  `Sales 2026` and `Budget`; first row `2, 3, =A1*B1`; text `001` stays `001`.
- **Export:** use the XLSX export panel or the Files menu.

---

## Engineering Toolbox workspace

### Engineering catalog (search by discipline)

- **Where:** Engineering Toolbox → Workspace tools → *Browse engineering tools* (*Discipline* and
  *Search tools* fields).
- **Computes:** nothing by itself. It lists unique tools across nine disciplines (Physics, Mechanical,
  Electrical, Electronics, Fluid mechanics, Aerospace, Control Theory, GNSS positioning and Signal
  engineering). **Open existing tool** routes to the one canonical implementation; planned tools have
  no runnable action. Units and engineering certification are not provided by the catalog.
- **Example (`tests/smoke_engineering_simulations.py`):** opening *Beam deflection and stress* opens
  the simulations panel with the beam preset selected and focus on the *Support* field.
- **Export:** the discipline/search filter is saved in the project.

| Catalog id | Title | Status | Opens |
| --- | --- | --- | --- |
| `matrix.solve.real.small` | Small real linear systems | Available | Calculator → Matrix calculator |
| `control.equilibrium.real.small` | Control state equilibrium | Available | Graphs → State equilibrium |
| `matrix.lu.real.small` | Small real LU factorization | Available | Calculator → Matrix calculator (LU) |
| `matrix.qr.real.small` | Small real QR factorization | Available | Calculator → Matrix calculator (QR) |
| `matrix.svd.real.small` | Small real singular value decomposition | Available | Calculator → Matrix calculator (SVD) |
| `matrix.weighted-least-squares.real.3x2` | Weighted least-squares fit | Available | Calculator → Matrix calculator (weighted LS) |
| `matrix.eigen.symmetric.small` | Symmetric eigenanalysis | Available | Calculator → Matrix calculator (Eigen) |
| `signals.fft.1d` | One-dimensional FFT | Available | Equation → Signal spectrum · FFT |
| `numerical.interpolation.1d` | One-dimensional interpolation | Available | Equation → 1D interpolation |
| `numerical.quadrature.adaptive` | Adaptive quadrature | Available | Equation → Numerical methods |
| `numerical.minimize.golden` | Bracketed 1-D minimization | Available | Equation → 1D minimization |
| `numerical.root.brent` | Bracketed root finding (Brent) | Available | Equation → Bracketed root |
| `control.stability.symmetric` | Control symmetric stability check | Available | Graphs → State equilibrium |
| `control.transient.two.state` | Control two-state transient | Available | Graphs → Two-state transient |
| `ode.ivp.scalar` | Scalar ODE initial-value solver | Available | Equation → ODE initial values |
| `thermal.cycle.analysis` | Thermodynamic cycle analysis | Available | Engineering simulations |
| `structures.beam.deflection` | Beam deflection and stress | Available | Engineering simulations |
| `circuits.network.analysis` | Circuit network analysis | Available | Engineering simulations |
| `aerospace.orbit.propagation` | Orbital propagation | Available | Engineering simulations |
| `circuits.rlc.series.transient` | Series RLC step response | Available | Engineering simulations |
| `mechanical.vibration.forced` | Forced vibration and resonance | Available | Engineering simulations |
| `mechanics.projectile.drag` | Projectile with air drag | Available | Engineering simulations |
| `thermal.conduction.rod` | Heat conduction in a rod | Available | Engineering simulations |
| `gnss.positioning.least.squares` | GNSS least-squares positioning | Available | Equation → Numerical methods → GNSS panel |
| `signals.spectral.analysis` | Signal spectral analysis | Planned · not implemented | — |
| `control.frequency.response` | Control frequency response | Available | Graphs → Control Theory Toolbox → Frequency response (`ct-frequency`): gain/phase margins, bandwidth, resonant peak |
| `electronics.digital.logic` | Digital logic simulation | Planned · not implemented | — |
| `fluids.pipe.network` | Pipe network pressure loss | Planned · not implemented | — |

Catalog entries that route to another workspace have their worked example in that tool's section
above. Overlapping discipline links are one tool, not separate features.

### Engineering simulations and animations

- **Where:** Engineering Toolbox → *Engineering simulations & animations* (`eng-visuals`); choose a
  preset from *Visualization*, edit the fields, then **Compute & animate**. **Pause** and
  **Step frame** control playback.
- **Computes:** physics-based textbook models and solver animations. Each states its model
  assumptions; results are textbook-model estimates, not certified designs or code checks.
- **Export (all presets):** **Send data to Data Tables**, **Plot in Graphs** and
  **Download frame (PNG)**.

| Preset | Model and limits (from the catalog) | Worked example (test) |
| --- | --- | --- |
| Beam deflection, moment and stress (`structures.beam.deflection`) | Euler–Bernoulli, simply supported, cantilever or overhanging rectangular beam with point, uniform or combined loads; linear elastic, small deflection; no shear deformation, buckling or design-standard checks | Simply supported, L = 4 m, P = 10 kN at 2 m, E = 200 GPa, b = 100 mm, h = 200 mm → max deflection PL³/(48EI) = 1.0 mm and max moment PL/4 = 10 kN·m (`tests/smoke_engineering_simulations.py`) |
| Forced vibration and resonance (`mechanical.vibration.forced`) | SDOF mass–spring–damper under harmonic forcing via the shared RK4 solver; linear viscous damping only | ζ = 0.1, r = 0.8 → steady amplitude matches 1/√((1−r²)² + (2ζr)²) and phase atan2(2ζr, 1−r²) (`tests/smoke_engineering_sim_extensions.py`) |
| Two-body Earth orbit (`aerospace.orbit.propagation`) | Planar two-body orbit by symplectic velocity Verlet; no J2, drag, third-body or relativistic effects | Periapsis altitude 500 km, e = 0.3 → period equals the Kepler value 2π√(a³/μ) ≈ 9,693 s, energy drift < 1e-5 (`tests/smoke_engineering_simulations.py`) |
| Series RLC step response (`circuits.rlc.series.transient`) | Ideal lumped series RLC on a DC source via the shared RK4 solver | R = 4 Ω, L = 10 mH, C = 100 µF, V = 12 V → ζ = 0.2, *underdamped*, capacitor voltage matches the closed form within 1e-6·V (`tests/smoke_engineering_simulations.py`) |
| Projectile with air drag (`mechanics.projectile.drag`) | Point mass over flat ground with quadratic drag vs the vacuum parabola; no lift, spin, wind or Mach effects | 40 m/s at 30° with Cd = 0 → range v²·sin(2θ)/g ≈ 141.3 m; with Cd = 0.47 the range and impact speed are smaller (`tests/smoke_engineering_simulations.py`) |
| Heat conduction in a rod (`thermal.conduction.rod`) | 1D transient conduction with fixed end temperatures using the shared explicit heat solver (stability limit enforced); insulated sides, constant properties | Aluminium, 0.5 m, initial 20 °C, ends 100 °C / 20 °C, 900 s → within 0.25 °C of the series solution, CFL ≤ 0.5 (`tests/smoke_engineering_simulations.py`) |
| Ideal Otto, Diesel and Brayton cycles (`thermal.cycle.analysis`) | Cold-air-standard cycles with constant specific heats; no friction, heat loss, combustion chemistry or variable specific heats | Otto, r = 8, q_in = 1000 kJ/kg, T1 = 300 K, P1 = 100 kPa → efficiency 1 − 8^−0.4 ≈ 0.5647 (`tests/smoke_engineering_thermo_circuits.py`) |
| DC resistive network (`circuits.network.analysis`) | DC modified nodal analysis of resistors with independent sources (up to 30 elements); floating nodes and singular networks are rejected; no capacitors, inductors, AC, dependent or nonlinear devices | Netlist `V1 1 0 12`, `R1 1 2 1000`, `R2 2 0 2000` → node 2 = 8 V, R1 current 4 mA, source supplies 48 mW, KCL residual < 1e-12 (`tests/smoke_engineering_thermo_circuits.py`) |
| Mass–spring–damper step response (`control.transient.two.state` link) | Coupled RK4 of a unit step response | ζ = 0.2, ωn = 2 rad/s → overshoot ≈ e^(−πζ/√(1−ζ²)) (`tests/smoke_engineering_visuals.py`) |
| Nonlinear pendulum (`ode.ivp.scalar` link) | Coupled RK4 of the full nonlinear pendulum | θ0 = 5°, L = 1 m → period ≈ 2π√(L/g) within 0.1 %, energy drift < 1e-6 (`tests/smoke_engineering_visuals.py`) |
| Two-tone signal and FFT spectrum (`signals.fft.1d` link) | Reuses the shared FFT | f1 = 5 Hz (a1 = 1), f2 = 12 Hz (a2 = 0.5) → amplitudes 1 at bin 5 and 0.5 at bin 12, all others < 1e-12 (`tests/smoke_engineering_visuals.py`) |
| Root bracket halving (`numerical.root.brent` link) | Animated bisection of a sign-changing bracket | `x^3-2*x-5` on [1, 3], 14 steps → every bracket contains 2.0945514815423265; final width 2/2¹⁴ (`tests/smoke_engineering_visuals.py`) |
| Integral as accumulated area (`numerical.quadrature.adaptive` link) | Reuses the adaptive quadrature | `sin(x)` on [0, π] → 2 within 1e-8 (`tests/smoke_engineering_visuals.py`) |
| Symmetric matrix transform and eigenvectors (`matrix.eigen.symmetric.small` link) | Reuses the symmetric eigen solver for a 2×2 matrix | A11 = 2, A12 = A21 = 1, A22 = 1 → eigenvalues φ² ≈ 2.618 and 1/φ² ≈ 0.382 (`tests/smoke_engineering_visuals.py`) |

---

## Panels that are not tools

`tests/test_user_guide.py` scans `src/*.js` for panel ids ending in `-details`. One match is
intentionally not a tool panel: `ui-details` is the **Options → Advanced explanations** checkbox. The
floating top buttons **Symbols**, **Examples**, **Options** and **Help** open sliding menus; Help
contains nested guides (curve fitting, ODE/PDE limits, right-click actions). See
[Advanced mathematics](ADVANCED_MATHEMATICS.md).

## More information

[Syntax reference](SYNTAX_REFERENCE.md) · [Features and limitations](FEATURES_AND_LIMITATIONS.md) ·
[Exports](EXPORTS.md) · [Visualization options](VISUALIZATION_OPTIONS.md) ·
[Troubleshooting](TROUBLESHOOTING.md)
