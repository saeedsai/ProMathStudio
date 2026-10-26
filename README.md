# ProMathStudio

**One connected mathematics workspace** for scientific calculation, live equation typesetting, symbolic algebra, and interactive 2D/3D graphs.

The application runs from a single, readable `index.html`. A web server and build process are **not required** to use the core app. Full SymPy support uses Pyodide in a Web Worker and downloads Python/SymPy on its first use.

## Start here

- **Use locally:** download `index.html` and open it in a modern browser.
- **Host online:** enable GitHub Pages (details: [Deployment](docs/DEPLOYMENT.md)). Expected Pages URL after successful deployment: https://saeedsai.github.io/ProMathStudio/
- **Try it:** in Equation editor enter `(x-1)^2`, then send it to Symbolic solver and choose **Expand**.
- **Move math between tools:** edit the **Working equation** field or select a saved/recent expression, then choose **Send to → Editor / Calculate / Solve / Graph 2D / Graph 3D / Notebook**.

## What it does

| Workspace | Functions |
|---|---|
| Advanced calculator | Real and complex arithmetic; factorials; trigonometry and inverse trig; degrees/radians; constants e, pi and i; history |
| Equation editor | Plain-text math to live MathML; symbol library; LaTeX and executable Python/SymPy equivalents; Word .docx; notebook |
| Symbolic solver | Expand, simplify, factor, solve, differentiate, integrate; offline polynomial/rational engine; optional SymPy exact and numerical results |
| Graph generator | Multiple `y=f(x)` curves and `z=f(x,y)` surfaces, adjustable bounds, zoom/pan/rotation, PNG export |
| Connected hub | Working expression, result routing, recent inputs, notebook, JSON backup/restore |

The current implementation has limits: it is not an arbitrary Python interpreter or a complete MATLAB replacement, and its native graph engine plots functions rather than general implicit/parametric curves. See [Known limitations](docs/FEATURES_AND_LIMITATIONS.md).

## Examples

| Input | Where to use |
|---|---|
| `5! + sin(pi/2)` | Calculator (radians → 121) |
| `sqrt(-1)` | Calculator → i |
| `(x-1)^2` | Solver → Expand |
| `x^2=-1` | Solver → Solve |
| `x^9-x-1=0` | Solver → SymPy (may return RootOf/numerical approximations) |
| `diff(x^3,x)` | Editor notation; use solver operation for differentiation |
| `matrix([a,b],[c,d])` | Equation editor |
| `y=sin(x)` and `y=cos(x)` on separate lines | 2D Graph |
| `z=sin(sqrt(x^2+y^2))` | 3D Graph |

**Ambiguous division:** `x/x-1` is not `x/(x-1)`. Use explicit parentheses. Symbolic solving of rational equations must respect denominator restrictions.

## Documentation

- [User guide](docs/USER_GUIDE.md) · [Syntax and examples](docs/SYNTAX_REFERENCE.md)
- [Features and limitations](docs/FEATURES_AND_LIMITATIONS.md) · [Symbolic engines](docs/SYMBOLIC_ENGINE.md)
- [2D / 3D graphing](docs/GRAPHING.md) · [Workspaces and project format](docs/PROJECT_FORMAT.md)
- [Word, LaTeX and other exports](docs/EXPORTS.md) · [Architecture](docs/ARCHITECTURE.md)
- [Development](docs/DEVELOPMENT.md) · [Testing](docs/TESTING.md)
- [GitHub Pages deployment](docs/DEPLOYMENT.md) · [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Full feature inventory and MATLAB/other-tool gap analysis (26 Oct 2026)](docs/FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md) — each feature classified complete/partial and missing capabilities prioritized.\n- [Hourly development agent operating rules](AGENTS.md) · [Living hourly feature plan + next five](docs/HOURLY_DEVELOPMENT_PLAN.md)\n- [Roadmap](docs/ROADMAP.md) · [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md) · [Security](SECURITY.md)

## Run the checks

```sh
python -m unittest discover -s tests -p 'test_*.py' -v
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
python tests/smoke_browser.py
```

The repository also includes a GitHub Actions workflow for automated regression tests. Browser smoke tests cover the offline engine, not the initial CDN download for SymPy.

## Browser, data and privacy

Local notebook, calculator history and the working expression are saved in browser localStorage (subject to storage availability); a project backup can be exported as JSON. Full SymPy is fetched from a Pyodide CDN, then executes in the browser. Do not assume browser storage is permanent—export backups. See [Project format](docs/PROJECT_FORMAT.md).

## Author and license

Created by **Saeed Mohammad Salehi**. Contact: **Saeedmsalehi1990@gmail.com**. Licensed under the [MIT License](LICENSE).

**3D paired-equation example:** enter `Y=x×x` and `z=sin(x×y)` on separate lines to show the surface and its highlighted curve `(x,x²,sin(x³))`. See [Graphing](docs/GRAPHING.md).

**Shared panel location:** The Connected Workspaces / Working equation panel is at the bottom of each workspace. Use its Send buttons to transfer math; the view scrolls to the destination tool.

### Plot imported CSV / JSON datasets

Under **2D & 3D Graphs → Import CSV / JSON data to graph**, upload local data, select X/Y/Z columns, plot points/lines or a rectangular 3D grid, and **Fit axes to data**. Imported datasets overlay equations and are included in the project JSON backup. See [Data import](docs/DATA_IMPORT.md) and the [sample files](examples/).

## Data Tables workspace

Use **Data tables** to edit multiple spreadsheet-like tables, enter safe formulas (for example `=A1*B1`, `=SUM(A1:A9)`, `=IF(A1>0,B1,0)`), filter and sort, join two tables (INNER/LEFT/RIGHT/FULL) or combine tables with UNION ALL/DISTINCT, INTERSECT and EXCEPT. Import or export **CSV, TSV and JSON** here, then send a table to **Graphs** for 2D and 3D scatter/grid/line plots, **bar charts** or **pie charts**. Your tables and raw formulas are saved inside the shared project JSON. [Read the Data Tables guide](docs/DATA_TABLES.md).

## Advanced mathematics and simpler interface

New features: **linear/polynomial (degree 2–6), exponential, logarithmic, power and Gaussian curve fitting**, with R² and RMSE displayed on the 2D graph alongside data. The Equation Editor typesets **Laplace/Fourier and inverse transforms**; SymPy computes these plus analytical ODE/PDE solutions for supported classes. The physics example library includes **72 new examples**. Floating **Symbols**, **Examples**, **Options** and **Help** replace the always-open palette; axis bounds are tucked into an expandable menu. The shared Working Equation remains at the bottom. See [Advanced mathematics and Help](docs/ADVANCED_MATHEMATICS.md).

## Numerical solvers, calculator calculus and Python data analysis

- **Numerical nonlinear equations:** search real roots on a specified interval using bracketed bisection and local Newton searches. For systems of 2–3 equations, use damped Newton with initial guesses and residual diagnostics.
- **Numerical PDEs with stated assumptions:** finite-difference **1D Poisson** (`-u_xx=f(x)`, fixed Dirichlet endpoints) and **1D heat** (`u_t=αu_xx`, initial profile and fixed endpoints), including CFL stability checks. These are not arbitrary PDE solvers.
- **Harmonized calculator:** numerical `diff(sin(x),x,0)`, `int(x^2,x,0,3)`, `sum(k^2,k,1,10)` and `prod(k,k,1,5)` use the shared expression parser, with optional scalar variable assignments.
- **Simpler Data Tables:** the grid remains central; Table, Filter, Combine, Files and Python submenus contain advanced actions. Non-destructive column filters support text/numeric conditions.
- **Python with pandas:** write code against a `tables` dictionary of DataFrames in a browser worker; set `result` to a DataFrame to import a **new** table. Initial Pyodide/pandas loading requires internet, and user-written Python code may make network requests. Run only code you trust.

[Complete numerical/Python guide](docs/NUMERICAL_AND_PYTHON.md).


### Right-click actions and binary/hex calculator

Context menus are available for cells, rows, column headings and tabs in Data Tables, plus Calculator, Editor, Solver and Graphs. Use **right-click**, **Shift+F10**, or long-press. New Calculator input modes DEC/BIN/HEX accept `0b1010`, `0xFF`, base arithmetic and safe-integer bitwise functions; click an output chip to copy a representation. Math Library insertion now targets Calculator when it is active. [Complete guide](docs/CONTEXT_MENUS.md).

**Hosting:** GitHub Pages publishes automatically from `main` through its branch-based Pages build. The optional explicit Pages workflow is manual-only to avoid duplicate deployments; automatic CI quality checks still run on each push. See [Deployment](docs/DEPLOYMENT.md).

## Custom functions and multi-series plots

Open **Custom functions · Formula / Python**, enter a function name, argument list, and mathematical definition, then select **Save function**. Saved definitions appear under **Symbols → Custom functions** and can be used in the calculator, graph expressions, and numeric Data Tables formulas. For example, define `squareplus(x) = x^2+1`, then use `squareplus(3)` or `=squareplus(A1)`.

The **Python code (Pyodide)** option saves real multi-line Python, including `if`, `elif`, loops, and multiple `return` statements. Enter `def myfun(x):\n    if x > 1:\n        return x**2\n    return 0`, save, and call `myfun(2)` directly from **Calculator**. The first call downloads Python using Pyodide; the function executes in a separate worker and must return a finite real number. Only execute trusted code. **Graph and Data Tables currently support formula-based custom functions only**; Python calls there are not yet supported. Python calls nested inside other Calculator expressions are not yet supported.

To compare multiple data series on one plot, go to **2D / 3D Graphs → Table / Graph type / X, Y, Z**, choose a column mapping, and click **Add series**. Repeat with another Y column or a different table. Supported overlays include 2D scatter and lines and 3D scatter/grid data. Use **Clear added series** to remove additional datasets; plotted series and custom functions are included in project backups. **Plot table** retains its original replace-plot behavior.
