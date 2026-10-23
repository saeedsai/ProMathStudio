# Advanced mathematics: curve fitting, integral transforms and differential equations

ProMathStudio has six **2D curve-fitting models**, integral transforms in its editor and SymPy solver, and analytical ODE/PDE solving for supported differential equations. A simplified interface offers floating **Symbols**, **Examples**, **Options**, and **Help** menus. All basic graphing and curve fitting runs in the browser without a network connection. SymPy requires its first Pyodide/SymPy download from a CDN.

## Fit measured data to a function

1. Open **Data tables**, create a table or import CSV/TSV/JSON, and fill numeric X and Y columns.
2. Open **Graphs** and select that table, the X/Y columns, and **2D scatter** or **2D line**. Press **Plot table** to see the measurements.
3. In **Curve fitting**, select a model. For polynomial, choose degree 2–6. Press **Fit and show on graph**.
4. A fitted blue curve overlays the raw points; a report shows the formula, R², RMSE, number of retained points and exclusions. **Clear fit curve** removes the fitted equation without changing the dataset.
5. The fitted formula is also visible in the function field, so it can be sent to the Equation Editor or Symbolic Solver. Project JSON saves that graph expression, the selected fit model/degree and all table data.

| Model | Formula | Notes |
|---|---|---|
| Linear | `y=a+b*x` | Ordinary least squares |
| Polynomial | `y=c0+c1*x+...+cn*x^n` | Degree 2–6; internally centers and scales X to improve stability |
| Exponential | `y=a*exp(b*x)` | Fits log(Y); requires Y positive; R² and RMSE calculated on original Y |
| Logarithmic | `y=a+b*ln(x)` | Requires X positive |
| Power-law | `y=a*x^b` | Fits log(X), log(Y); requires X and Y positive |
| Gaussian | `y=A*exp(-((x-mu)/sigma)^2)` | Fits a quadratic in log(Y); requires positive Y and a negative quadratic coefficient |

**Interpretation:** Fitting does not prove physical causation or extrapolation quality. Polynomial overfitting is possible. R² can be negative for some nonlinear models when computed on original Y. Invalid/nonfinite coordinates are excluded; a model requiring positive values may exclude additional rows. Large ill-conditioned or singular systems return a useful error rather than imaginary coefficients. Fits are supported for 2D scatter/line, not bar/pie charts or 3D surfaces.

## Laplace / inverse Laplace transforms

In **Equation Editor**, type `laplace(exp(-2*t),t,s)` for professionally typeset transform notation and generated LaTeX/Python. The library has symbols for the forward and inverse operators. For actual calculation, **send the expression** (without the `laplace` wrapper) to **Symbolic Solver**, select **Laplace transform**, choose input variable `t`, and output variable `s`, then **Execute** (SymPy engine).

Example:

```text
Input: exp(-2*t)
Operation: Laplace
Variable: t
Output variable: s
Result: 1/(s+2)
```

For inverse, enter `1/(s+2)`, choose inverse Laplace, input `s`, output `t`. Causal inverse transforms may include a `Heaviside(t)` factor. Use the SymPy-equivalent code panel if you want to run it in your own Python environment.

## Fourier / inverse Fourier transforms

Use `fourier(exp(-x^2),x,k)` and `inverse_fourier(exp(-pi^2*k^2),k,x)` for typeset editor notation. In **Symbolic Solver**, select Fourier/inverse Fourier, set the input/output variables, and execute. The application uses **SymPy’s Fourier convention** with kernel `exp(-2*pi*i*k*x)`; it is not the angular-frequency convention with `exp(-i*omega*t)` without normalization. The transform of `exp(-x^2)` is `sqrt(pi)*exp(-pi^2*k^2)` under this convention. Results depend on convergence and assumptions.

## Ordinary differential equations (ODEs)

In the Equation Editor or Symbolic Solver enter:

```text
diff(y(t),t) + y(t) = 0
```

Select **Solve ODE**, enter symbolic variable `t`, and choose Auto/SymPy. The browser SymPy worker calls `sympy.dsolve`, producing a general solution such as `y(t)=C1*exp(-t)`. Higher-order example:

```text
diffn(y(t),t,2)+4*y(t)=0
```

Unknown functions such as `y(t)` are treated as symbolic functions, not ordinary variables. ODE solving is limited to classes SymPy can solve analytically, and **does not yet apply user-entered initial or boundary conditions**. Results may contain arbitrary constants.

## Partial differential equations (PDEs)

Example first-order transport equation:

```text
pdiff(u(x,t),t)+pdiff(u(x,t),x)=0
```

Select **Solve PDE** (SymPy). The result may be a family involving an arbitrary function of `x-t`. This uses `sympy.pdsolve` and only supports PDE types SymPy recognizes; **general nonlinear or multidimensional PDEs, arbitrary initial/boundary-value problems, and numeric PDE solvers are not provided**. An unsupported problem is reported explicitly rather than invented.

## Physics reference library

Open **Equation Editor → ★ Examples**. Topics include **Physics · Mechanics (16)**, **Electromagnetism (14)**, **Thermodynamics (10)**, **Waves & optics (10)**, **Quantum & relativity (11)**, **Fluids & engineering (11)**: **72 added examples**. The catalog includes familiar laws, wave/heat/diffusion PDE notation and aerospace engineering formulas. Examples are reference notation; constants, units, coordinate assumptions and applicability are not automatically verified.

## Contextual interface and Help

- **∑ Symbols** opens the slide-out, searchable math library and nested category/subcategory menu. Use the background or Escape to close it.
- **★ Examples** opens a slide-in sample menu with category selector. Physics subjects appear alongside algebra, calculus and other topics.
- **⚙ Options** controls optional history, Python output and advanced explanations.
- **? Help** opens the Help dialog with nested guides for five workspaces, fitting, transforms, ODE/PDE solving and physics references, plus the full syntax reference.
- The **Connected Workspaces** panel remains at the **bottom of every page**, supporting movement of equations and data between tools.
- Graph axis bounds are available under **Axis ranges and advanced graph settings** rather than displayed constantly.

## Tests and maintenance

The `tests/smoke_advanced_math.py` check runs a real Chromium browser locally and uses the same embedded Python SymPy evaluator for transform and ODE/PDE regression. The workflow installs Python dependencies (`playwright` and `sympy`) and Chromium. The single-file offline app in `index.html` contains both the existing Data Tables module and the new `src/advanced-features.js` source as a bundled inline script.