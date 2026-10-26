# Symbolic solving and SymPy

## Two execution engines

**Built-in (offline):** optimized for basic one-variable polynomial/rational operations, including quadratic equations and complex roots.

**SymPy (browser Web Worker):** uses Pyodide with Python/SymPy to attempt additional operations including higher-degree equations and exact/numerical algebraic roots. Auto mode tries the offline solver first and may fall back to SymPy.

The browser loads Pyodide from `https://cdn.jsdelivr.net/pyodide/v0.29.1/full/` during first SymPy use and calls `loadPackage('sympy')`. This requires connectivity initially. It is not an unrestricted Python REPL.

## Operations

| Operation | Meaning |
|---|---|
| Auto | Solve equalities or transform an expression according to implementation rules |
| Expand | Distribute products and powers, e.g. `(x-1)^2` |
| Simplify | Simplify algebraic expressions, being mindful of domains |
| Factor | Factor polynomial expressions |
| Solve | Find zero/equality roots for chosen variable |
| Differentiate | Symbolic derivative with respect to selected variable |
| Integrate | Symbolic antiderivative with respect to selected variable |
| Numerical roots | Approximate roots via SymPy when supported |

## Examples

- `(x-1)^2` → `x^2-2*x+1` when expanded.
- `x^2=1` → roots `-1` and `1`.
- `x^2=-1` → `-i` and `i`.
- `x^9-x-1=0` → nine complex/algebraic roots; exact forms may be expressed via `RootOf`.
- `(x^2-1)/(x-1)` → expression `x+1` only where original denominator is nonzero (`x != 1`).

Mathematical result types vary. A general trigonometric equation may yield a set/family, a difficult polynomial may give root objects, and some operations are unsupported. Complex approximations can be routed to Calculator; symbolic RootOf is not directly a numeric calculator input.

## Simultaneous symbolic systems (linear and bounded nonlinear)

Choose **Symbolic Solver → Operation → Solve system of equations**. Enter one equation per line, choose comma-separated unknowns, and select **Method**:

- **Auto** (default): classify the equations using SymPy's linear-equation test. Use `linsolve` for linear systems and `nonlinsolve` for supported polynomial nonlinear systems.
- **Linear only**: solve linear equations and report an error for nonlinear input.
- **Nonlinear polynomial**: allows the bounded nonlinear solver when necessary; linear input still uses the exact linear path.

Example nonlinear input: `x^2+y^2=5` and `x-y=1`, unknowns `x,y`. The real solutions are `(-1,-2)` and `(2,1)`; output shows paired solution tuples. Linear underdetermined example: `x=2x+2z`, `y=x-z`, unknowns `x,y,z` produces `x=-2z, y=-3z` with free parameter `z`.

Safety and scope: max **12 linear equations and 10 linear unknowns**; nonlinear max **6 equations and 3 unknowns**; the nonlinear operation accepts only polynomial expressions of total degree at most 4 and at most 80 polynomial terms per equation. It can return complex solutions; a result is not implicitly restricted to reals. Some large or difficult polynomial systems may still exhaust the SymPy worker time limit; the feature is not a general symbolic `Reduce` / Gröbner / nonlinear transcendental solver. Symbolic expressions are parsed from safe math AST, not arbitrary Python code. Initial SymPy download requires internet. Numerical nonlinear systems (2–3 variables, local Newton method) are separate under Numerical methods.

## Python code panel

The editor and symbolic solver provide Python/SymPy code corresponding to the selected expression/operation. This is an **export artifact** for use in your own Python environment and not evidence that arbitrary Python statements are executed in the app.

## Validation/guardrails

The Python evaluator is embedded in a `type="text/plain"` script tag and receives structured AST JSON. It enforces a maximum AST-node count and limits root/result counts. MathML/LaTeX from CAS results require proper sanitization; do not replace restricted parsing with arbitrary Python `eval`. Test denominator restrictions, complex branches and numerical accuracy after changes.

## Troubleshooting

- **Offline and advanced solver not loading:** use built-in mode or connect to the internet to load Pyodide.
- **Degree 9 has no rational root:** choose SymPy, which can express non-elementary roots via RootOf or approximations.
- **An expected radical is missing:** switch operation/engine or use numerical roots; not all polynomials admit radicals.
- **Huge expressions hang:** reduce expression size or simplify in stages.

[Full limitations](FEATURES_AND_LIMITATIONS.md)

## Laplace/Fourier transforms and differential equation solving

The Equation Editor can render `laplace(exp(-2*t),t,s)`, `inverse_laplace(1/(s+2),s,t)`, `fourier(exp(-x^2),x,k)` and inverse Fourier notation as MathML/LaTeX/Word-ready equations. In Symbolic Solver, choose the corresponding operation and provide the input and output variables; the SymPy worker executes the transformation. Fourier uses SymPy's `exp(-2*pi*i*k*x)` convention.

Solve ODE uses `sympy.dsolve` for recognized ODEs such as `diff(y(t),t)+y(t)=0`; Solve PDE uses `sympy.pdsolve` for recognized classes such as `pdiff(u(x,t),t)+pdiff(u(x,t),x)=0`. Arbitrary initial/boundary conditions, unsupported equations, and numerical PDE solvers are **not** supported. The solver will report an error rather than invent a result. See [Advanced mathematics](ADVANCED_MATHEMATICS.md).
