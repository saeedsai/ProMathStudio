# Numerical mathematics, calculator calculus, Data Tables filters and Python

This release extends the existing symbolic solver; **numerical algorithms approximate solutions under explicitly supplied conditions**. They do not prove that all solutions have been found and are not universal PDE solvers.

## Nonlinear real roots

Open **Symbolic Solver → Numerical methods / PDE**. Select **Real nonlinear roots** and enter an equation such as `sin(x)-x/2=0`, variable `x`, and an interval such as `-4` to `4`. The solver combines bracketed bisection with local Newton searches to catch some even-multiplicity roots. It returns real solutions found in the interval, not arbitrary complex roots or certified enumeration. The method can miss roots near poles, oscillatory behavior or beyond its sampling resolution.

## Nonlinear systems (2–3 unknowns)

Set **2–3 nonlinear equations**, enter one equation per line or semicolon, variables separated by commas, and initial guesses in the same order. Example:

```text
Equations: x^2+y^2=5; x-y=1
Variables: x,y
Guesses:   1,1
```

A damped Newton method with a numerical Jacobian seeks a local solution. It reports iterations, the residual norm and convergence status. If the Jacobian is singular, choose a different initial guess. **Convergence does not guarantee that the solution is unique.**

## First-order initial-value ODE (offline RK4)

Open **Symbolic Solver → Numerical methods / PDE → First-order ODE initial-value problem · RK4**. Enter a real-valued derivative **dy/dt = f(t,y)** using the same safe Calculator expression syntax. Specify initial time t₀, final time t₁, initial value y(t₀), and a fixed number of time steps (4–1000). Example:

- Derivative: y
- Initial time: 0; end time: 1; initial value: 1; steps: 40
- Reference: y(1) = exp(1) ≈ 2.718281828; reduce step size and compare results to check convergence.

The native classical fourth-order Runge–Kutta method computes a table of **t, y** values. **Save output to Data Tables** preserves a new table, while **Plot y(t) in Graphs** imports it and opens a 2D line chart. The derivative may depend on both t and y, e.g. t+y. All calculations run locally without Pyodide or a network connection.

**Scope and limitations (scalar RK4 mode):** This is a scalar first-order *forward* IVP solver only (t₁ > t₀), with real finite values and a magnitude safety bound of 1e12. It uses fixed steps; this scalar mode has no adaptive error estimator, stiffness handling, event detection, BVP, DAE or discontinuity detection. A separate bounded two-state RK4 mode is described below. Large or rapidly varying derivatives may require more steps, and numerical results are approximations rather than proofs. Errors reject non-finite derivatives/states and invalid inputs instead of silently exporting invalid tables. See the dedicated Playwright RK4 reference and integration regression in tests/smoke_ode.py.

## Coupled two-state initial-value ODE (offline RK4)

Choose **Coupled two-state RK4** in the ODE panel. Enter `dy/dt=f(t,y,z)` and `dz/dt=g(t,y,z)`, both initial values, forward interval and 4–1000 fixed steps. Example: `dy/dt=z`, `dz/dt=-y`, with `y(0)=0`, `z(0)=1`; at `t=pi/2`, the result approximates `y=1`, `z=0`. Both derivatives use the safe offline numerical evaluator, without executing arbitrary JavaScript. Output columns are `t,y,z` for Data Tables; Graphs plots y(t), while z remains available in the imported table. This method is real-valued, fixed-step, forward-only and nonstiff; it is not an adaptive or general N-state solver. The new `tests/smoke_ode_system.py` covers reference convergence, both-state coupling, invalid inputs and UI export.

## Adaptive first-order IVP (offline RK45)

In the same **First-order ODE initial-value problem** panel, choose **Adaptive RK45**. Enter the derivative, initial/final time, initial value, tolerance (1e-12 to 1e-2), and maximum integration attempts (4–10,000). The Dormand–Prince embedded Runge–Kutta 5(4) method accepts or rejects candidate steps based on a scaled local error estimate and reports accepted/rejected counts. The output is sampled at accepted time points, not at uniformly spaced intervals.

Example: dy/dt=y, t0=0, t1=1, y0=1, tolerance 1e-9 approximates e. Tighter tolerance normally increases the number of accepted steps and improves the reference result, but is not a global error guarantee. Both Data Tables and Graphs handoffs work with the variable-step output. Failed attempts, invalid tolerances, non-finite values and step-size underflow produce errors instead of partial exports. **Scope:** real scalar forward IVPs only; no stiff ODE guarantee, event handling, systems, backward integration or globally certified accuracy. RK4 remains the default and its fixed-step behavior is unchanged. See tests/smoke_ode_adaptive.py.

## Adaptive Simpson quadrature (offline, bounded)

In **Symbolic Solver → Numerical methods / PDE**, choose **Adaptive Simpson integral** and enter a real-valued integrand in `x`, finite start/end bounds (end greater than start), tolerance from 1e-12 to 1e-2, and maximum function evaluations from 16 to 20,000. For example, `sin(x)` on `[0, pi]` approximates 2; `x^2` on `[0,1]` approximates 1/3. The method recursively compares one Simpson panel with two half panels and reports an error estimate, evaluation count and refinement count. It uses the same safe native mathematical evaluator as the Calculator, and runs offline.

**Limitations:** Smooth real finite-interval functions only; the error estimate is heuristic, not a certified global bound. Discontinuities, singularities, and rapidly oscillatory integrands can be missed or fail. Exceeding evaluation/depth budgets, invalid bounds, non-real values, or non-finite results fails without exporting partial data. The integral is a scalar result, so table/graph export is disabled for this method. Fixed-step Calculator `int(...)` is unchanged. See `tests/smoke_quadrature_adaptive.py`.

## One-dimensional piecewise-linear interpolation (offline)

Open **Symbolic Solver → Numerical methods → 1D linear interpolation**. Enter 2–200 sorted, strictly increasing x/y sample pairs, one pair per line, and 1–1,000 query x values. You can load the first two columns of the active Data Table using **Load active table x/y**. The solver returns linearly interpolated real y values, sorted by query x, and can save them to Data Tables or plot them as a 2D line in Graphs.

Example: samples `0,1`, `1,3`, `2,5` and queries `0,0.5,1,1.5,2` yield y values `1,2,3,4,5`. Duplicate/unsorted x values, malformed pairs, non-finite or overly large numbers and out-of-domain queries fail without exporting stale results. **No extrapolation**, cubic spline, multidimensional interpolation or uncertainty estimates are provided. See `tests/smoke_interpolation_linear.py`.

## Shape-preserving cubic PCHIP interpolation (offline)

In Symbolic Solver → Numerical methods → 1D interpolation, select Shape-preserving cubic (PCHIP). Enter 2–200 strictly increasing sample pairs and 1–1,000 in-domain query x values. The piecewise cubic Hermite interpolant uses weighted harmonic-mean interior slopes and limited endpoint slopes; flat intervals remain flat. It is continuous with a continuous first derivative at interior knots and preserves monotonicity within each sample interval, subject to floating-point rounding. Exact knot values are returned without cancellation. Two samples reduce to a straight line.

Example: samples (0,0), (1,1), (2,1), (3,2), queries 0.5, 1.5, 2.5 stay within each local y interval without overshoot. Save to Data Tables and Plot in Graphs export the selected method. Switching methods or editing inputs invalidates stale export results. Duplicate/unsorted samples, non-finite slopes, out-of-domain queries and unsupported methods are rejected.

PCHIP is not a natural cubic spline, globally twice differentiable, a multidimensional interpolator or a statistical uncertainty estimate. No extrapolation is performed. See tests/smoke_interpolation_pchip.py.

## Barycentric polynomial interpolation (offline, bounded)

In **Symbolic Solver → Numerical methods → 1D interpolation**, choose **Polynomial (barycentric)**. Provide 2–16 strictly increasing real x/y sample points and up to 1,000 in-domain query values. This is a *single global interpolating polynomial*, distinct from piecewise-linear and shape-preserving PCHIP. The method uses scaled barycentric weights and a near-knot y anchor to reduce avoidable floating-point cancellation, returns exact sample values at knots, and supports Data Tables and Graphs exports. It rejects duplicate/unsorted or extremely close x values, non-finite intermediate results, out-of-domain queries and excessive node counts.

Example: samples (0,1), (1,2), (2,5), (3,10) interpolate the quadratic y=x²+1; query 1.5 yields 3.25. **Warning:** High-degree or equally spaced polynomial interpolation may oscillate severely between nodes (Runge phenomenon). This mode does not guarantee monotonicity, no overshoot, reliable conditioning, extrapolation, or an uncertainty estimate. Prefer PCHIP for shape-preserving data. See tests/smoke_interpolation_barycentric.py.

## One-dimensional Poisson equation

Select **1D Poisson**, where the implemented convention is:

\[-u''(x)=f(x),\qquad x\in[a,b],\qquad u(a)=L,\ u(b)=R.\]

Specify the source `f(x)`, domain, fixed endpoint values and number of **spatial intervals**. The implementation uses second-order centered finite differences and a tridiagonal Thomas solver. The generated table contains `x, u` and can be graphed as a 2D line. Example: `pi^2*sin(pi*x)`, domain `0`–`1`, and both endpoint values 0 approximates `sin(pi*x)`.

## One-dimensional heat equation

Select **1D heat** to solve:

\[u_t=\alpha u_{xx}\]

with a given initial profile `u(x,0)`, positive diffusivity `α`, domain, final time, and fixed Dirichlet endpoint values. The solver uses explicit **forward-time, centered-space (FTCS)** differences. It enforces the stability condition:

\[\alpha\,\frac{\Delta t}{(\Delta x)^2}\leq 0.5.\]

Choose more time steps if you see an instability warning. The generated table has `x, t, u` and can be plotted as a 3D grid using the existing Data Tables → Graphs mapping. Example: domain 0–1, `alpha=0.1`, initial expression `sin(pi*x)`, boundary values 0, 40 spatial intervals, 200 time steps, final time 0.1. The reported table may sample output time frames to limit its size.

**PDE limitations:** These numerical methods cover only the **one-dimensional** heat and Poisson models specified above. They do not infer equations, initial conditions, arbitrary geometries, mixed/Neumann boundaries, nonlinear PDEs or spatially varying diffusivity. The **SymPy analytical ODE/PDE** tools remain available separately for supported closed-form classes.

## Shared mathematics in Calculator

Calculator, Graphs and Numerical Solver use the same native mathematical AST parser and numeric evaluator. In **Calculator → Variable assignments & advanced numeric math**, add scalar values such as `x=2` and `y=3` (one per line), then evaluate expressions using the variables. Supported numerical calculus includes:

| Expression | Approximate value | Meaning |
|---|---:|---|
| `diff(sin(x),x,0)` | 1 | Central-difference derivative |
| `int(x^2,x,0,3)` | 9 | Composite Simpson definite integral |
| `sum(k^2,k,1,10)` | 385 | Discrete finite sum |
| `prod(k,k,1,5)` | 120 | Finite product |

For symbolic forms such as an **indefinite integral**, use Symbolic Solver. These numerical operations evaluate at specified values/bounds; they do not return a symbolic antiderivative or derivative.

## Data Tables menus and filters

The sheet remains the main workspace; functions are grouped in the **Table**, **Filter**, **Combine**, **Files** and **Python** submenus. Use the Filter submenu to select a column and condition: contains, starts with, equals/does not equal, numeric greater/less than (including inclusive variants), or empty. Click **Apply filter** to hide nonmatching rows. The filtered view does not alter the underlying workbook data or row numbers; use **Remove column filter** to restore all visible rows. Existing quick text search remains available inside the Filter submenu.

## Python data analysis with pandas

Select **Data Tables → Python** to open the code editor. On first use, Pyodide/pandas downloads from a CDN; Python is then executed **in a dedicated Web Worker** only when **Run Python** is pressed. This is **user-authored code**, not an unrestricted remote API. Workers do not get the parent page DOM, but Python scripts may still initiate network requests. **Run only scripts you trust.** Execution has a time limit and results are capped to the workbook's table limits.

The Python environment exposes:

- `tables`: a dictionary from table names to pandas `DataFrame` objects, with fully evaluated workbook cell values. Numeric columns are converted when all entries are numeric.
- `pd`: the pandas package.
- `result`: set this variable to a pandas `DataFrame`, or a dictionary mapping new table names to DataFrames, to import the returned data as **new tables**.
- `print(...)`: captured as text in the output area.

Example:

```python
import pandas as pd
name, df = next(iter(tables.items()))
print(name, len(df))
# Work on a copy; the source workbook remains unchanged.
result = df.select_dtypes(include='number').describe().reset_index()
```

A second example is available from **Example: groupby**. Python execution does **not** overwrite existing tables automatically; results are imported as new tables. Export a **Save project** JSON backup to retain them. Graph the new table using the existing 2D/3D/bar/pie chart controls.

## Security and verification

The native JS evaluator and numerical solvers do not use arbitrary JavaScript `eval()` or dynamic Function execution. The explicitly requested Python editor runs code in a worker on the user's own computer; code from unknown sources can be dangerous even in a worker. Imported CSV/JSON is interpreted as data, not Python code. The on-device browser workspaces do not have a server database.

Browser regressions cover nonlinear roots, local equation systems, heat/Poisson reference cases, CFL rejection, numerical calculus, menu/filter behavior, and Python worker script construction. **Live CDN loading and full pandas execution require online browser validation.**

### Native Equation Editor syntax in the calculator

Both calculator-style and Equation Editor-style forms are accepted. For example, `int(x^2,x,0,3)` and `int(0,3,x^2,x)` both evaluate to 9. `sum(k^2,k,1,10)` and `sum(k=1,10,k^2)` both evaluate to 385. The same applies to `prod`. The Python workspace also exposes `sp` for SymPy, loaded alongside pandas; `result` must still be a pandas DataFrame or a dictionary of DataFrames.

## Composing Python custom functions in Calculator (bounded)

Save a Python function under **Custom functions · Formula / Python**, e.g. `def myfun(x): return x*x`. Calculator accepts `2*myfun(3)+1` (19), `myfun(myfun(2)+1)` (25), and `if(1,myfun(3),myfun(100))` (9, without running the unused branch). Nested Python calls execute sequentially in an isolated Pyodide Web Worker; numeric AST operators remain in the native safe evaluator, never JavaScript eval. Arguments/results must be finite real numbers, calls are capped at 16 per expression, each worker call times out after 60 seconds, and a newer Calculator execution cancels any pending worker result. This is **not** Python support in Graphs, Data Tables, or formula-defined custom-function bodies; first-use CDN execution requires online QA. The focused Playwright regression mocks the worker transport and does not prove actual Pyodide downloads.


### Linear interpolation numerical precision

The bounded 1D piecewise-linear interpolator preserves exact supplied sample values when a query matches a sample x coordinate, even if neighboring y values differ greatly in magnitude. Between knots it uses ordinary binary64 linear interpolation; it does not extrapolate or guarantee exact decimal arithmetic.
