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
- [Roadmap](docs/ROADMAP.md) · [Changelog](CHANGELOG.md)
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

## Licensing

No open-source license has been selected for this repository. A public GitHub repository is **not automatically open source**; contributors should not assume reuse rights until the owner adds a license.

**3D paired-equation example:** enter `Y=x×x` and `z=sin(x×y)` on separate lines to show the surface and its highlighted curve `(x,x²,sin(x³))`. See [Graphing](docs/GRAPHING.md).

**Shared panel location:** The Connected Workspaces / Working equation panel is at the bottom of each workspace. Use its Send buttons to transfer math; the view scrolls to the destination tool.
