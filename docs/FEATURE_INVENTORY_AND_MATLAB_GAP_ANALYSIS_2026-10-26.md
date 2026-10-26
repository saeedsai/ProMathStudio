# ProMathStudio — Verified Feature Inventory and Mathematics Software Gap Analysis

**Audit date:** 26 October 2026  
**Repository:** [saeedsai/ProMathStudio](https://github.com/saeedsai/ProMathStudio)  
**Audited branch/commit:** `main` / [`ee30466134ae004208d33c5fe64c83dcaa6d374a`](https://github.com/saeedsai/ProMathStudio/commit/ee30466134ae004208d33c5fe64c83dcaa6d374a)  
**Application:** https://saeedsai.github.io/ProMathStudio/  
**Comparison:** MATLAB R2026b and its *separately licensed toolboxes*, Simulink, Wolfram Language/Mathematica and mainstream scientific-computing software. Their entire ecosystems are **not** equivalent to base MATLAB.

## Reading this audit

This inventory distinguishes **a user-facing built-in feature** from **a mathematical expression that can merely be displayed**, or an algorithm that a skilled user could implement in the separate Python editor.

- **C — Complete for stated scope:** the specific, bounded function/UI is implemented in source and covered by available checks where feasible. This **does not** mean feature parity with MATLAB or perfect correctness for every possible input.
- **P — Partial:** implemented but constrained by equation family, input size, UI access, stability, output type, dependency, or incomplete verification. Where possible, the constraint is explicit.
- **N — Not built in:** no dedicated first-class UI/native workflow found in the audited source. Some functions **might** be implemented manually through Python/SymPy/pandas, but that is **not** counted as shipped UI capability.
- **Evidence:** `index.html` (canonical bundled application), modules under `src/`, `tests/`, guides under `docs/`, and the current repository tree. Older documentation sometimes contradicts the implementation; this report prioritizes executable source and regression tests. Most CI tests use mocked/stubbed browser workers or run embedded SymPy under CPython; actual first-use CDN downloads, cross-browser usability, Word round-trip, and complex numerical accuracy are **not comprehensively certified**.

The feature set is grouped at a practical user-visible level rather than treating every individual palette symbol, equation example, keyboard key or MATLAB toolbox function as a separate product feature.

---

# Part I — Features present in ProMathStudio today

## A. Workspace, equation editor and mathematical notation

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Five connected workspaces | C | Calculator, Equation Editor, Symbolic Solver, 2D/3D Graphs, Data Tables; the last tab is injected by the Data Tables module. |
| Shared Working Equation hub | C | Capture an input and route expressions/results among workspaces and notebook. Not every symbolic result is executable in every destination. |
| Live text-to-math preview | C | Browser MathML rendering of supported parsed notation. |
| Text mathematical parser / AST | P | Arithmetic, function calls, implicit multiplication, operators and many math layouts; **not** all LaTeX, arbitrary symbolic functions, or a proof assistant. |
| Arithmetic and grouping notation | C | `+ - * / ^`, parentheses, unary operators, fractions, negative/fractional powers. |
| Equality and comparison notation | P | `=`, `==`, `<`, `>`, `<=`, `>=`, `!=`; display support broader than numerical solving of inequalities. |
| Superscripts and subscripts | C | `x^2`, `x_1`, indexed notation. |
| Roots, fractions and factorial notation | C | `sqrt`, `root`, `frac`, `!`; evaluation depends on chosen workspace. |
| Greek letters and mathematical constants | C | Searchable library plus pi, e, imaginary unit, infinity notation. |
| Vectors, accents, sets, logic notation | P | `vec`, hats, overlines, set operators, logical glyphs, etc.; substantial portion is **typesetting only**. |
| Matrix/array/determinant notation | P | `matrix`, `pmatrix`, `array`, `vector`, `det` formatting; not a general matrix numeric/symbolic algebra UI. |
| Calculus notation | P | Derivatives, partial derivatives, integrals, limits, sums and products may be typeset; computational availability differs by method. |
| Piecewise/conditional notation | P | `if(condition,a,b)` works for native scalar numeric evaluation; `cases` displays piecewise forms. Not a general inequality/region solver. |
| Transform notation | C | Laplace, inverse Laplace, Fourier and inverse Fourier render in editor. Computational support separately below. |
| Differential-equation notation | C | Examples such as `diff(y(t),t)` and `pdiff(u(x,t),t)` in the editor. |
| Searchable Symbols menu | C | Nested category/subcategory symbols; insertion targets Editor or Calculator depending on active tool. |
| Searchable equation examples / reference catalog | C | General math examples and 72 additional reference physics/engineering equations in six categories. Examples are **not** physical-unit-checked simulations. |
| Notebook with saved equations | C | Add, edit, delete, reopen saved formula/text entries; browser local persistence. |
| MathML/LaTeX output generation | P | Good for supported AST, but not full macro compatibility/round-trip across math systems. |
| Generated Python/SymPy notation | P | Useful generated code for supported expressions/solver operations; not universal correct translation of arbitrary input. |
| Contextual Help, Examples, Options menus | C | Collapsible/floating UI with workspace guidance and display controls. |
| Keyboard and responsive interaction | P | Editor Enter/Shift+Enter, solver Ctrl+Enter, menus and shortcuts; comprehensive mobile/assistive-tech coverage remains unverified. |

## B. Scientific calculator and numerical math

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Real scalar arithmetic | C | Finite double-precision JavaScript numeric evaluation. |
| Complex arithmetic | P | Complex addition/subtraction/multiplication/division, powers, principal roots/logs and transcendental functions; branch cuts and floating accuracy apply. |
| Exponentiation and n-th roots | C | `^`, `pow`, `sqrt`, `root` within numeric domain. |
| Factorials | P | Scalar factorial on supported nonnegative integers; not generalized special-function coverage. |
| Trigonometry | C | `sin`, `cos`, `tan`, `cot`, `sec`, `csc`. |
| Inverse trigonometry | C | `asin/arcsin`, `acos/arccos`, `atan/arctan`, and `atan2`. |
| Hyperbolic functions | C | `sinh`, `cosh`, `tanh`. |
| Logarithms/exponentials | C | `ln`, common/base-specific `log`, `log10`, `log2`, `exp`. |
| Absolute value, norm, sign | P | Scalar modulus/norm/sign; not matrix/vector norm analysis. |
| Other scalar utilities | C | `min`, `max`, `floor`, `ceil`, `round`, `mod`, `sinc`. |
| Boolean/comparison and conditional numeric expressions | P | Comparisons, logical conjunction/disjunction, three-argument `if`/`piecewise`; limited boolean language. |
| Constants | C | `pi`, `e`, `i`, stored `Ans`; other notation constants vary by evaluator. |
| Radian/degree selector | C | Calculator trig calculation mode; graph angles remain radians. |
| Numeric display modes | C | Auto, fixed/decimal, scientific and engineering notation; configurable displayed digits. Not arbitrary-precision arithmetic. |
| Calculator keypad and history | C | Scientific keypad, 40 recent results, recall, clear, persistent browser history. |
| User-defined scalar variables | P | Assign numeric scalars in calculator advanced panel; not a full variable/workspace/kernel language. |
| Numerical first/partial derivatives | P | Central finite differences, e.g. `diff(sin(x),x,0)`; no automatic differentiation or error estimators. |
| Definite integration | P | Composite Simpson quadrature (fixed number of steps, e.g. `int(x^2,x,0,3)`); no general adaptive/multidimensional integration UI. |
| Finite sums | P | `sum(...,start,end)`, limited to up to 10,000 terms; not symbolic infinite summation. |
| Finite products | P | `prod(...,start,end)`, same bounded integer range; not symbolic infinite products. |
| DEC/BIN/HEX input and conversion | P | Binary/hex literals and output chips; exact large *single-literal* conversion via BigInt, general safe-integer arithmetic limited near 53 bits. |
| Bitwise integer functions | P | `band`, `bor`, `bxor`, `bnot`, `shl`, `shr`, with safe-integer and shift constraints. |
| Calculator-to-editor/solver routing | C | Send expression/result to another workspace; unsuitable symbolic types may require selection/conversion. |
| Full multistatement Python as Calculator language | P | Available **only through saved, directly called Python custom functions**, not by pasting arbitrary Python statements into main Calculator input. |

## C. Symbolic algebra, equations and transforms

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Operation and engine selectors | C | Auto, offline, SymPy; user chooses variable; worker-backed CAS starts on demand. |
| Polynomial expansion | P | Offline one-variable polynomial/rational cases and SymPy fallback; not arbitrary tensor/assumption-aware algebra. |
| Rational simplification | P | Cancel/simplify rational expressions; exclusions from original denominators need care. |
| Polynomial factorization | P | Built-in rational-polynomial scope; advanced cases depend on SymPy. |
| Solving a single algebraic equation | P | Polynomial/rational and supported SymPy equation classes; no universal closed-form solver. |
| Linear and quadratic equations | C | Standard supported one-variable cases, real or complex. |
| Higher-degree polynomial equations | P | SymPy may yield exact radicals for low-degree cases, or `RootOf`/numerical roots for high-degree cases. |
| Complex roots | P | Supported polynomial equations and principal-branch arithmetic; verify multiplicity/domain as needed. |
| Trigonometric/transcendental equations | P | SymPy attempts these and may return solution sets/conditions instead of enumerated finite roots. |
| Exact symbolic vs approximate roots | P | Distinct symbolic and numeric answer forms; not high-precision general numerical workbench. |
| Symbolic differentiation | P | Selected-variable derivatives via built-in polynomial support or SymPy for recognized expressions. |
| Symbolic indefinite integration | P | Offline polynomial integration and SymPy for supported integrands; not all antiderivatives have closed forms. |
| SymPy numerical polynomial roots | P | `nroots`/supported methods, fixed settings and result limits. |
| Solve a **linear** system of equations in UI | P | New **Solve system of equations** operation, one equation per line, comma-separated unknowns; uses SymPy `linsolve`, up to 12 equations / 10 unknown names. Shows free parameters or inconsistency. **Not** a general nonlinear symbolic system solver. |
| Underdetermined symbolic linear systems | P | Returns parameterized families (e.g. `x=-2z, y=-3z`) via `linsolve`; no dedicated matrix-rank or solution-space inspection panel. |
| Inconsistent linear systems | C | A “no solution” result for inconsistent `linsolve` systems. |
| Forward/inverse Laplace transforms | P | SymPy transform operations with specified input/output variables; convergence/assumptions require interpretation. |
| Forward/inverse Fourier transforms | P | SymPy Fourier convention `exp(-2*pi*i*k*x)`; not a numeric FFT/signal processing toolbox. |
| Analytical ODE solving | P | `sympy.dsolve` for recognized classes, including basic first-order/higher-order examples. No user-defined initial/boundary conditions UI. |
| Analytical PDE solving | P | `sympy.pdsolve` for supported classes (e.g. first-order transport); far from general PDE solving. |
| CAS result typesetting | C | MathML, LaTeX and approximate text where present; individual result lines. |
| Send/copy/save specific symbolic results | P | Notebook, Word, Latex, other workspaces; some CAS objects cannot be numerically re-evaluated in Calculator. |
| Equivalent SymPy code display | P | Generates code for many operations; system solver's code panel currently contains a *placeholder comment*, not a fully executable equivalent. |
| Worker isolation and operation guardrails | P | Structured AST to SymPy, limits (e.g. AST nodes/result counts/timeouts); first Pyodide download requires internet and web workers are not a blanket security guarantee. |

## D. Numerical equation solving and numerical PDEs

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Bounded real roots of nonlinear scalar equations | P | Bracket/bisection plus sampled local Newton search; may miss tangential/oscillatory roots, discontinuities or outside-range roots. |
| Initial interval and tolerance controls | C | Numeric domain, sampling and tolerance validation. |
| Numerical nonlinear systems (2–3 variables) | P | Damped Newton with numerical Jacobian, user initial guesses; local convergence, not exhaustive/certified. |
| Residual/iteration diagnostics | C | Reports convergence, iterations and residual within supported numeric methods. |
| 1D Poisson boundary-value solver | P | Finite differences for `-u''=f(x)` on interval with Dirichlet values at both ends; tridiagonal solver; not arbitrary PDE/geometry. |
| 1D heat initial-boundary-value solver | P | Explicit FTCS for `u_t=alpha*u_xx`, positive constant alpha, fixed Dirichlet ends, and CFL check. |
| Discretization and stability validation | P | Controls for grid/time-step counts; heat CFL warning, no adaptive discretization/error certification. |
| Numerical results as Data Tables | C | Generate tables with root/system or sampled Poisson/heat output as applicable. |
| Graph numerical output | C | Route generated tables to 2D/3D plotting workflows. |

## E. Graphing, visualization, charting and fitting

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Multiple explicit 2D curves | C | Several `y=f(x)` expressions on the same Cartesian canvas. |
| Multiple explicit 3D surfaces | P | Sampled `z=f(x,y)` meshes; not full 3D symbolic/implicit surfaces. |
| Constrained curve on a 3D surface | P | `y=f(x)` paired with `z=g(x,y)` highlights a parametric intersection-like trace. Not general surface-surface intersections. |
| 3D curve from `y=f(x)` | P | Graph can show the corresponding 3D curve with `z=0`; not general 3D parametric plotting. |
| Conditional/piecewise graph expressions | P | Supported `if(condition,true,false)` forms; sampling can misrepresent jumps/discontinuities. |
| Interactive axes | C | X/Y/Z min/max, panning (2D), rotation (3D), zoom, reset. |
| Curve sampling and basic discontinuity handling | P | Fixed canvas sampling; singularities, steep spikes and narrow features can be missed. |
| Equation-to-residual plotting | C | Transfer `f(x)=g(x)` to `y=f(x)-g(x)`. Not a true implicit curve solver. |
| Graph color palettes and primary color | C | Classic, bright, pastel, monochrome, custom; background color. |
| Per-equation color selection | C | Individual equation colors and legends, saved to project. |
| Line patterns and weights | P | Solid/dashed/dotted, width options; per-series settings where supported; options vary by chart/dataset. |
| Point marker option | P | UI offers circle/square/diamond, but imported dataset points presently remain circles in some paths. |
| Import tabular graph data | C | CSV/TSV/JSON, preview, X/Y/Z mapping, local plot data persistence in project export. |
| 2D scatter datasets | C | Numeric columns mapped to X/Y, plot with/without functions. |
| Connected line datasets | C | Connect valid X/Y coordinates in supplied row order. |
| 3D scatter datasets | P | X/Y/Z point cloud display; no spatial analytics/interpolation. |
| Rectangular 3D grid mesh | P | Requires complete grid of X/Y coordinates; not irregular triangulation. |
| Overlay datasets from multiple tables/mappings | P | **Add series** supports further 2D point/line and 3D scatter/grid series, with legends and colors; limited total extra series, not general chart composition. |
| Overlay equations and measured points | C | Both data and function layers can appear on graph canvas. |
| Axis auto-fit for imported data | C | Fit limits to valid plotted coordinates. |
| Bar chart | P | Group by category and sum values; not stacked/grouped/multiaxis statistical charting. |
| Pie chart | P | Positive category aggregates, grouping excess categories into Other; no advanced chart semantics. |
| Curve fitting: linear | P | Ordinary least squares for 2D X/Y data; not robust/weighted uncertainty-aware regression. |
| Curve fitting: polynomial | P | Degrees 2–6, numerical stabilizing transform; no generic degree-selection/regularization. |
| Curve fitting: exponential | P | Log-transformed positive Y; objective differs from original-space nonlinear least squares. |
| Curve fitting: logarithmic | P | Positive X only. |
| Curve fitting: power law | P | Positive X/Y, log-space estimation. |
| Curve fitting: Gaussian bell | P | Fit quadratic in log(Y), requires plausible negative quadratic curvature; not multi-peak or arbitrary nonlinear Gaussian fit. |
| Curve-fit diagnostics | P | Fitted formula, R², RMSE, valid/excluded sample counts; no confidence intervals, residual diagnostics/uncertainty propagation. |
| Fit-curve overlay and clear | C | Show/clear fitted model atop source data. |
| PNG export | C | Image download from graph and chart canvas; raster, not SVG/vector-graphics authoring. |

## F. Data Tables, spreadsheets and relational operations

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Multiple spreadsheet-like sheets | P | Up to 20 tables, 6,000 rows and 32 columns each; 150 visible rows rendered at a time. |
| Add/duplicate/rename/delete tables | C | UI and context-menu actions with confirmation for destructive actions. |
| Cell, row and column editing | C | Editable headers/cells; row/column add/delete/duplicate via menus. |
| Formula arithmetic and cell references | P | `=A1*B1`, grouping, numeric operators, local and cross-sheet references; **A1 is the first data row** in actual source. |
| Spreadsheet aggregates | P | SUM, AVERAGE/AVG, MIN, MAX, COUNT over ranges; not Excel's complete function catalog. |
| Spreadsheet conditional IF | P | Formula `IF` and comparisons; parser is intentionally limited, including nested-expression edge cases. |
| User-defined formula functions in sheets | P | Named *formula* functions callable in numeric sheet formulas; Python custom functions are not supported there. |
| Cycle/reference diagnostics | P | Indicates cyclic/bad references; not a full dependency-graph spreadsheet engine. |
| Text search and sort | C | Across computed values; ascending/descending by chosen column. |
| Per-column conditional filters | P | Contains/starts-with/equality/numeric comparisons/empty; filters hide rows without modifying underlying data. Persisted filter views are limited. |
| Table display zoom | C | 50–200% in 10% steps; local preference, not necessarily exported between devices. |
| INNER JOIN | C | Equality join on selected keys, new table. |
| LEFT/RIGHT/FULL OUTER JOIN | C | Equality joins; no arbitrary SQL join predicates. |
| UNION ALL / UNION DISTINCT | C | Combine rows with same column count, distinct handling. |
| INTERSECT / EXCEPT | C | Set-style operations on row values. |
| CSV/TSV import | P | Headered files/local parsing, size/row/column limits. |
| JSON tabular import | P | Supported records, column/rows and array layouts, not general nested JSON flattening. |
| CSV/JSON sheet export | C | Active sheet's **computed values** exported; preserve formulas in project JSON. |
| Data-to-graph mapping | C | Pick table, X/Y/Z columns and chart type from Graphs panel. |
| Table copy/cut/paste and TSV ranges | P | UI/context menus with clipboard fallback, browser permissions and formula-reference limitations. |

## G. Custom functions, Python and automation

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Named mathematical formula functions | P | Create/edit/delete 1–6 argument definitions, stored locally, listed in Symbols; recursion/nested cases and syntax can be limited. |
| Formula calls from Calculator | C | Numeric argument calls in native expression evaluator; no arbitrary symbolic function algebra. |
| Formula calls from Graphs/Data Tables | P | Native formula function integration; graph/worksheet parser can reject unsupported nesting/type combinations. |
| Multi-line user-defined Python functions | P | Save actual Python `def`, including control flow, but direct `name(real_args)` Calculator call only. Return type restricted to finite real number; no nested expression calls. |
| Pyodide Python runtime in worker | P | Browser download on first call, worker isolation, timeouts; full CDN execution not tested by offline CI. |
| Python script editor for tables | P | Execute real user code on pandas DataFrames with `tables` dictionary and captured print output; not an integrated general notebook. |
| pandas operations through user scripts | P | Supported when Python dependencies load: dataframe filtering/grouping/stats/joins as authored Python; **not** evidence of equivalent native UI commands. |
| SymPy accessible from Data Tables Python | P | Worker exposes `sp` in table script context; results must be returned as DataFrames for table import. |
| Python results imported as new tables | P | Worker import path exists for named DataFrames, with row/column caps, but live CDN/pandas round-trip is not exercised by offline CI. |
| Python run/stop/timeout controls | P | On-demand execution/stop and capped output, no step debugger, persistent kernel or package manager UI. |
| Python/math source security | P | Workers restrict DOM access but user-authored Python may access the network. Execute trusted scripts only. |

## H. Workflow, formats, portability, engineering quality

| Existing capability | Status | Exact scope / qualification |
|---|:---:|---|
| Working Expression source dropdown | C | Drafts, notebook equations, recent inputs, graph expressions and solver/calculator results. |
| Saved recent calculations/notebook | C | Browser localStorage; explicit delete/clear options. |
| Project JSON export/import | P | Version-1 projects with expression, notebooks, calculator, graph, tables, custom functions etc.; import replaces relevant current state, size ~2 MB. |
| Restore saved graph datasets/styles | P | Data series, graph appearance and main graph state; large projects may exceed import cap. |
| Editable Word equation DOCX | P | Generates Office Math; editing in installed Microsoft Word not independently verified for every expression. |
| Notebook Word DOCX export | P | Word document with saved equations where representable. |
| LaTeX copy and `.tex` document export | P | Supported equation syntax only, not complete LaTeX packages/macros. |
| MathML/rich-HTML clipboard / copy-image | P | Browser secure-context and Word/clipboard support vary. |
| Copy Python snippet | C | Generated SymPy script/text, subject to coverage limits. |
| Context menus | P | Cell/row/column/tab, Calculator, Editor, Solver, Graphs, Notebook; long-press and Shift+F10 supported but not full desktop-app parity. |
| Tool routing to 2D/3D graphs | C | Send expression/selected result to plotting with appropriate conversion. |
| Browser-only deployment | C | A single `index.html` application on GitHub Pages; no required application server for base UI. |
| Offline base functionality | P | Core JS UI works without an online engine; first remote Pyodide/SymPy/pandas/Python download requires connectivity. |
| Source modular maintenance | P | Several `src/*.js` modules exist but are bundled inline into the canonical ~390 kB `index.html`. |
| Open-source repository and license | C | GitHub-hosted MIT source. |
| Automated tests | P | Static/structural Python tests and Chromium smoke tests for multiple workspaces and embedded Python. Not an exhaustive numeric reliability suite. |
| CI and Pages deployment | C | GitHub Actions quality workflow and GitHub Pages deployment are configured; release verification still needs live-site checks. |

### Current mathematical problem classes, in one glance

| Problem class | Can the user solve it from the product UI today? | Important caveat |
|---|---|---|
| Elementary real/complex scalar expressions | **Yes** | Finite precision, domain/branch limits. |
| Univariate polynomial/rational equations | **Yes, partial** | Offline narrow scope; SymPy extension. |
| Higher-degree/transcendental symbolic equations | **Sometimes** | SymPy may return sets/RootOf or fail. |
| **Linear** simultaneous algebraic equations | **Yes, partial** | Dedicated system UI; `linsolve`, including free parameters; up to 12 equations and 10 unknowns. |
| **Nonlinear** simultaneous algebraic equations | **Numerically, partial** | Separate 2–3 variable Newton method with guesses; no universal symbolic-system UI. |
| Bounded nonlinear scalar real roots | **Yes, partial** | Heuristic sampling + root finders; no completeness certificate. |
| Polynomial differentiation/integration | **Yes** | Offline; more via SymPy. |
| General symbolic derivatives/antiderivatives | **Sometimes** | Symbolic engine class restrictions. |
| Numeric derivative/definite integral/finite sum/product | **Yes, partial** | Fixed finite-difference/Simpson approaches, term bounds. |
| Laplace and Fourier/inverses | **Yes, partial** | Symbolic SymPy, **not** sampled-signal FFT. |
| Analytical ODEs | **Sometimes** | SymPy-recognized classes; no initial-condition UI. |
| Analytical PDEs | **Sometimes** | SymPy-recognized PDEs; not a general PDE system. |
| Numerical PDEs | **Two narrow models only** | 1D Poisson/1D heat with Dirichlet boundary conditions. |
| Linear algebraic matrices/eigenproblems | **Not through general-purpose matrix UI** | Matrix **notation** exists; manually writing code in Python is different. |
| Ordinary descriptive statistics | **Limited / indirect** | Some spreadsheet aggregates, fitted curves and optional pandas; no broad statistics UI. |
| Constrained optimization/LP/QP/MILP | **No dedicated UI** | Not a built-in mathematical solver. |
| Symbolic inequalities/inequality systems | **No general solver** | Notation/comparisons and numeric conditionals are not `Reduce`. |
| Data regression/curve fitting | **Yes, partial** | Six fit families; no robust regression or inference. |
| 2D Cartesian functions/3D explicit surfaces | **Yes, partial** | Not general implicit/parametric/polar plotting. |

---

# Part II — Missing or materially incomplete features found in MATLAB and other major mathematical tools

The following rows describe **product gaps**, not a promise to recreate every MATLAB toolbox. **Priority** is a suggested roadmap: **P0** high-value foundation/correctness, **P1** broadly useful next capability, **P2** advanced or specialist, **P3** large ecosystem/industry platform. An item marked **Missing** has no comparable built-in UI; **Extend** means the current app has a small subset. Many mature MATLAB features require *separately purchased MathWorks products*, noted under the source column and references.

## 1. Algebra, symbolic computation and mathematical foundations

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| General **nonlinear symbolic equation systems** | Missing; system UI currently uses linear `linsolve`. | P0 |
| Numerical solution of larger nonlinear equation systems | Extend; current damped Newton works only on 2–3 unknowns. | P1 |
| Inequality systems and semialgebraic regions (`reduce`, `solve` inequalities) | Missing general solver; comparisons/plot `if` are not equivalents. | P1 |
| Assumptions (real/positive/integer/domains) and branch-choice controls | Missing structured assumption UI. | P0 |
| Domain/range, exclusions, poles, singularities and inequalities reporting | Extend; some denominator checks exist, no comprehensive domain tool. | P1 |
| Substitution, elimination, isolation, collect, coefficient extraction | Missing dedicated CAS operations. | P0 |
| Multivariate polynomial algorithms and Groebner bases | Missing. | P2 |
| Algebraic number fields and exact algebraic extensions | Missing dedicated workflows. | P2 |
| Multivariate systems solution classification, rank/degree/parameters | Extend linear-system outputs with a proper solution-space inspector. | P1 |
| Symbolic solving for complex domains with explicit domain selection | Extend current SymPy behavior with controllable domains. | P1 |
| Symbolic series: Taylor/Maclaurin, Laurent, Puiseux, Padé | Missing computation UI; notation alone insufficient. | P1 |
| Symbolic infinite sums and products | Missing computational solvers. | P2 |
| Limits including one-sided/multivariate limits | Missing dedicated compute operation, despite notation. | P0 |
| Piecewise symbolic algebra and conditions | Extend numeric conditional/typesetting; no robust symbolic simplification of cases. | P1 |
| Symbolic function composition/inversion and inverse functions | Missing first-class tools. | P1 |
| Recurrence and difference equation solvers | Missing. | P2 |
| Special functions (Gamma, Beta, Bessel, Airy, elliptic, Zeta, error functions) | Missing broad native library/analysis UI. | P2 |
| Exact arbitrary-precision and variable-precision arithmetic | Missing; base calculator is double precision. | P0 |
| Interval arithmetic / certified bounds / validated numerical proofs | Missing. | P2 |
| Detailed trustworthy step-by-step symbolic derivations | Missing proof/step display; CAS returns results, not audited derivations. | P1 |
| Equation equivalence, identity/constraint verification and counterexamples | Missing structured verification tools. | P1 |
| Automatic dimensional analysis and physical unit handling | Missing unit-aware computations/conversions. | P1 |
| Number theory, modular arithmetic, Diophantine equations | Missing dedicated solvers beyond simple integer/bitwise utilities. | P2 |
| Combinatorics/permutations/partitions/generating functions | Missing as general computing domain. | P2 |
| Tensor algebra, index notation and symbolic tensors | Missing numerical/symbolic tensor operations. | P2 |

## 2. Matrices and numerical linear algebra

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Interactive matrix/vector calculator with editable array grids | Missing (current editor formats matrix notation only). | P0 |
| Matrix arithmetic/multiplication, transpose/conjugate transpose | Missing native UI. | P0 |
| Determinants, inverses, traces, rank and null spaces | Missing native computational UI. | P0 |
| Gaussian elimination/RREF and detailed linear-system steps | Missing dedicated general UI; internal small Gaussian routine is not matrix tool. | P0 |
| Matrix equation solvers `Ax=b`, least-squares/pseudoinverse | Missing first-class workflows. | P0 |
| Eigenvalues/eigenvectors, characteristic/minimal polynomials | Missing computational UI. | P1 |
| SVD, QR, LU, Cholesky, Schur decompositions | Missing. | P1 |
| Sparse matrices and iterative solvers (CG/GMRES) | Missing. | P2 |
| Matrix functions (exponential, logarithm, sqrt) | Missing. | P2 |
| Conditioning, numerical stability, residual/error estimators | Missing systematic analysis. | P1 |
| General vector calculus (grad/div/curl/Laplacian) | Missing dedicated computation UI. | P1 |
| Jacobian, Hessian, directional derivatives, sensitivity analysis | Missing symbolic/numeric operator UI (internal numeric Jacobian alone is not enough). | P1 |
| Large/high-performance linear algebra, GPU acceleration | Missing. | P3 |

## 3. Numerical methods, calculus and integral equations

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Adaptive numerical quadrature with tolerances/errors | Extend fixed-step Simpson integration. | P1 |
| Multiple/double/triple/contour integrals | Missing general numerical computation. | P1 |
| Improper and oscillatory integrals | Missing numeric-specialized quadrature. | P2 |
| General-purpose differentiation with higher order, gradients and autodiff | Extend basic finite differences. | P1 |
| Root-finding algorithms selectable (Brent, secant, trust region, deflation) | Extend current scalar bracket/Newton heuristic. | P1 |
| Certified enumeration of polynomial/interval roots | Missing validated root isolation. | P2 |
| Error propagation, tolerance analysis and uncertainty quantification | Missing. | P1 |
| Interpolation: linear/cubic splines, PCHIP, Akima, B-splines | Missing (regression is not interpolation). | P1 |
| Multidimensional/scattered interpolation, triangulation | Missing. | P2 |
| Numerical integration of discrete measurement arrays | Missing UI (custom scripts possible). | P1 |
| Extrapolation controls/diagnostics | Missing. | P1 |
| Numerical conditioning/stiffness detection and solver comparison | Missing. | P2 |

## 4. Optimization, operations research and constrained solving

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Unconstrained scalar/multivariable minimization (`fminbnd`, `fminunc`) | Missing optimization UI. | P0 |
| Bound-constrained and general nonlinear programming | Missing. | P1 |
| Linear programming (LP) | Missing. | P1 |
| Mixed-integer and integer linear programming (MILP) | Missing. | P2 |
| Quadratic programming (QP) and cone programming (SOCP) | Missing. | P2 |
| Constrained/unconstrained nonlinear least squares | Extend six fixed regression models. | P1 |
| Robust global optimizers, multistart and evolutionary methods | Missing. | P2 |
| Multiobjective/Pareto optimization | Missing. | P2 |
| Convex analysis and constraint feasibility reports | Missing. | P2 |
| Optimization Jacobians, gradients, Hessians, scaling, termination diagnostics | Missing unified system. | P1 |
| Dedicated mixed-variable parameter fitting and model calibration | Missing. | P1 |
| Optimal control, trajectory optimization, dynamic programming | Missing. | P3 |

## 5. Differential equations, PDEs and simulation

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Numerical initial-value ODE solvers (RK4/RK45/variable-step) | Missing dedicated ODE integration UI. | P0 |
| Stiff ODE solvers (BDF/implicit Runge-Kutta) | Missing. | P1 |
| ODE systems and initial-condition interface | Extend analytical SymPy `dsolve`; no general IVP UI. | P0 |
| Numerical ODE boundary-value problems (shooting/collocation) | Missing. | P1 |
| Differential-algebraic equations (DAE) and index reduction | Missing. | P2 |
| Event detection, discontinuities, hybrid dynamics | Missing. | P2 |
| Delay differential equations and fractional-order DEs | Missing. | P2 |
| Apply ODE initial/boundary conditions in symbolic result UI | Missing, despite `dsolve` integration. | P0 |
| Boundary conditions for symbolic PDEs and arbitrary function constraints | Missing. | P1 |
| 2D/3D general finite element PDE engine | Missing; only 1D Poisson/heat finite difference. | P2 |
| PDE geometry builder/import (STL/CAD), mesh generation/refinement | Missing. | P2 |
| Neumann/Robin/mixed and curved-boundary PDE conditions | Missing. | P1 |
| Nonlinear, variable-coefficient, coupled PDEs | Missing general solvers. | P2 |
| Reaction-diffusion, wave, Navier–Stokes equation models | Missing first-class PDE templates/solvers. | P2 |
| Eigenvalue PDEs and modal analysis | Missing. | P2 |
| Structural mechanics/FEM, heat transfer, electromagnetics multiphysics | Missing specialist workflows. | P3 |
| PDE residual/error/adaptive refinement tools | Missing. | P2 |
| Time-dependent simulation monitoring, checkpoints and animation | Missing. | P2 |
| Block-diagram continuous/discrete dynamic simulations (Simulink-like) | Missing separate modeling environment. | P3 |

## 6. Statistics, probability, uncertainty and data science

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Probability distributions (PDF/CDF/quantiles/parameter fitting) | Missing dedicated UI; math templates alone do not compute distributions. | P1 |
| Random number generation, RNG seeds and Monte Carlo apps | Missing native math workflow. | P1 |
| Descriptive statistics dashboard (median/variance/std/quantiles/correlation) | Extend basic sheet aggregates; pandas can compute when scripted. | P1 |
| Covariance/correlation matrices and scatter-matrix displays | Missing. | P1 |
| Confidence/prediction intervals and uncertainty bands | Missing fitting inference. | P1 |
| Hypothesis testing, p-values, goodness-of-fit tests | Missing. | P1 |
| ANOVA/ANCOVA, experimental design (DOE) | Missing. | P2 |
| Generalized linear models, multivariate/multiple regression | Missing first-class modeling UI. | P1 |
| Robust/weighted/nonlinear regression and outlier diagnostics | Extend six predefined fitting families. | P1 |
| Time-series models (ARIMA, exponential smoothing, forecasting) | Missing. | P2 |
| Bayesian statistics, bootstrapping, resampling | Missing native workflow. | P2 |
| Multivariate analysis: PCA, ICA, factor analysis | Missing. | P2 |
| Classification and regression machine learning apps | Missing native workflows. | P3 |
| Clustering, anomaly detection, feature engineering | Missing. | P2 |
| Design-of-experiments, survival/reliability and process control | Missing. | P3 |
| Neural networks and deep learning model development | Missing. | P3 |

## 7. Signal processing, control and transforms

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Discrete FFT/IFFT and sampled-signal spectrum display | Missing; symbolic Fourier transform is **not** FFT. | P1 |
| Digital filters (FIR/IIR), filter design and frequency response | Missing. | P2 |
| Convolution/correlation, Hilbert transforms and wavelets | Missing native signal processing. | P2 |
| STFT, spectrogram, time–frequency analysis | Missing. | P2 |
| Z-transform and inverse Z-transform | Missing; only Laplace/Fourier operations are exposed. | P1 |
| Discrete-time dynamical systems and transfer-function manipulation | Missing. | P2 |
| Bode, Nyquist, Nichols, root-locus plots | Missing control-system visualization. | P2 |
| Stability (Routh–Hurwitz, poles/zeros, margins) | Missing analysis tools. | P2 |
| State-space models, controllability/observability | Missing. | P2 |
| PID tuning, LQR, Kalman filtering and observers | Missing. | P3 |
| Audio/sensor/time-series data ingestion and stream processing | Missing product-level workflow. | P2 |

## 8. Geometry, plotting and scientific visualization

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Implicit 2D curves and regions `F(x,y)=0` | Missing native implicit graph engine. | P0 |
| Explicit parametric 2D/3D curves/surfaces | Missing general form (special 3D constrained trace is not equivalent). | P0 |
| Polar/spherical/cylindrical coordinates | Missing plotting systems. | P1 |
| Inequality region/shaded feasible-set plots | Missing. | P1 |
| True implicit 3D isosurfaces and volume slices | Missing. | P2 |
| 2D contour/heatmap, vector field, quiver, streamlines | Missing. | P1 |
| Histograms, box/violin plots, error bars, confidence bands | Missing dedicated statistical charts. | P1 |
| Logarithmic axes, dual-axis charts, subplots/facets | Missing or not exposed as general UI options. | P1 |
| Per-point glyph styles and complete per-series 2D/3D style parity | Extend partially implemented marker choices/overlays. | P1 |
| Interactive sliders for parameters/time and animation | Missing generalized parameter exploration. | P1 |
| Large point-cloud rendering and irregular 3D triangulation | Missing. | P2 |
| Geometry construction, intersections, distances and CAD meshes | Missing. | P2 |
| Scientific vector exports SVG/PDF/EPS and publication themes | Missing; PNG is raster only. | P1 |
| 3D scene lighting/shaders/transparency and mesh diagnostics | Missing. | P2 |
| Image/video processing and computer vision toolboxes | Missing industry-scale domain. | P3 |
| Map/geospatial plots and coordinate projections | Missing. | P3 |

## 9. Data engineering, spreadsheets, import/export

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| XLSX/ODS import, export, formulas and styles | Missing; data import supports CSV/TSV/JSON. | P0 |
| SQL query editor and relational database connections | Missing; current joins/unions are UI operations. | P1 |
| Data frame pivot tables, group-by aggregation UI, reshaping | Missing first-class UI; may be scripted in pandas. | P1 |
| Excel-like full functions, lookups, dates, array formulas | Missing from limited sheet evaluator. | P1 |
| Automatic relative-reference rewriting when inserting/deleting/sorting rows | Missing; explicit warning in docs. | P0 |
| Spreadsheet dependency/recalculation engine and auditing | Extend lightweight formulas/cycle errors. | P1 |
| Import of HDF5, MAT, Parquet, Feather, NetCDF | Missing. | P2 |
| External REST/API ingest with connector management | Missing built-in data connectivity. | P2 |
| Data quality profiling, missing-value imputation, outlier filtering | Missing dedicated workflow. | P1 |
| Dataset metadata, units, schemas, reproducible pipelines | Missing. | P1 |
| Large/out-of-core data processing and streaming | Missing (20×6,000×32 sheet cap). | P3 |
| Native pivot/SQL query visualization and dataflow graph | Missing. | P2 |

## 10. Software engineering, collaboration and reproducibility

| Missing / expansion target | Gap | Priority |
|---|---|:---:|
| Full interactive Jupyter/Live Script-style notebook with code cells | Missing; saved equation notebook and table Python editor are different. | P1 |
| Unified typed variables, arrays and reusable computation session | Missing full programmable mathematical kernel. | P1 |
| Python custom functions callable inside nested calculator formulas, graphs and spreadsheet cells | Extend current direct Calculator-only Python calls. | P0 |
| Shared symbolic/non-scalar custom functions (complex, vectors, matrices, tables) | Missing general type support. | P1 |
| Package/environment manager for Python, deterministic dependencies | Missing. | P2 |
| Debugger/profiler, function breakpoints, performance trace | Missing. | P2 |
| Versioned computation/notebook history, cross-workspace undo/redo | Missing unified reproducibility. | P1 |
| Parameter sweep, batch experiments, reproducible run configurations | Missing. | P1 |
| Project schema migrations and robust large-project support | Extend current JSON v1/2 MB importer. | P0 |
| Server-side jobs, parallel/GPU/cloud computing | Missing. | P3 |
| Multiuser projects, accounts, real-time collaboration and sync | Missing. | P3 |
| Source-control-aware documents, diff/merge of notebooks | Missing. | P2 |
| Portable HTML/PDF interactive reporting | Missing dedicated reporting pipeline; DOCX/LaTeX/PNG exist. | P1 |
| MATLAB `.m`, MAT and Simulink `.slx` interoperability | Missing. | P3 |
| MATLAB/Simulink/C/C++/CUDA code generation | Missing. | P3 |
| Unit tests property-based numerical verification/regression corpus | Extend current smoke suite; no authoritative certified numerics corpus. | P0 |
| Production-grade first-use CDN, cross-browser/mobile, accessibility security QA | Extend existing smoke tests with end-to-end real runtime validation. | P0 |
| Complete offline installation/PWA with packaged numerical runtimes | Missing; core HTML offline but remote Python packages not bundled. | P1 |

## 11. Industry-specific scientific toolboxes (optional, high-effort ecosystem extensions)

These are **not** core algebra requirements, but their absence matters if the benchmark is the *whole* MATLAB/Simulink or Wolfram ecosystem.

| Missing application family | Examples found in mature products | Priority |
|---|---|:---:|
| Aerospace mechanics and flight dynamics | Aerospace Toolbox, flight dynamics, geodesy/coordinate frames | P3 |
| Robotics and autonomous systems | Rigid-body kinematics, trajectory planning, ROS, localization/SLAM | P3 |
| Structural and mechanical engineering | FE stress, vibration, modal, fatigue analysis | P3 |
| Electrical/EM/RF systems | Circuit simulation, field solving, antennas and RF design | P3 |
| Multiphysics and thermal engineering | Coupled heat/flow/structural physical models | P3 |
| Communications/radar | Modulation, coding, beamforming, radar detection | P3 |
| Computational finance | Portfolio risk, derivatives, term structures | P3 |
| Bioinformatics and computational biology | Genomic analysis, dynamical biological systems | P3 |
| Geographic/geospatial analysis | Mapping, GIS, projections, spatial statistics | P3 |
| Computer vision and image analytics | Filtering, segmentation, feature extraction, object detection | P3 |
| Optimization-driven vehicle/power systems | Powertrain, battery, energy system models and controls | P3 |
| Cryptography/formal theorem proving | Algebraic protocols, logic verification, theorem-proving tools | P3 |

## Proposed implementation order

1. **P0 — Fix mathematical foundations and correctness:** explicit assumptions/domains; true multivariable symbolic solve (including nonlinear systems); matrix calculator; limit evaluation; arbitrary precision; numerical ODE IVP; richer Python-function composition; XLSX import/export; spreadsheet reference updating; rigorous regression tests.
2. **P1 — Fill mainstream math-software gaps:** vector calculus; substitution/elimination; interpolation; adaptive quadrature; optimization with constraints; statistics/inference; distribution tools; FFT; parametric/polar/implicit/contour graphing; ODE conditions; better project/report workflows.
3. **P2 — Advanced scientific computing:** sparse LA, special functions, advanced transforms, BVP/DAE/stiff systems, 2D/3D FEM geometry/meshing, large datasets, control-theory and advanced signal tools.
4. **P3 — MATLAB-family breadth:** Simulink-like modeling, GPU/parallel/HPC, machine learning/deep learning, hardware integration, image processing and industry application toolboxes.

**Recommended product boundary:** First target a dependable *symbolic + numerical mathematics + tabular data + 2D/3D visualization* workspace. Attempting all MATLAB toolboxes simultaneously would undermine mathematical correctness and software quality.

## Evidence and external comparison references

### Audited repository (as of the commit above)

- [Canonical browser application](https://github.com/saeedsai/ProMathStudio/blob/ee30466134ae004208d33c5fe64c83dcaa6d374a/index.html) — actual UI, parser, calculator, SymPy worker, graph and project-export code.
- [Numerical solver/Python source](https://github.com/saeedsai/ProMathStudio/blob/ee30466134ae004208d33c5fe64c83dcaa6d374a/src/numerical-data.js), [Data Tables](https://github.com/saeedsai/ProMathStudio/blob/ee30466134ae004208d33c5fe64c83dcaa6d374a/src/data-tables.js), [curve fitting](https://github.com/saeedsai/ProMathStudio/blob/ee30466134ae004208d33c5fe64c83dcaa6d374a/src/advanced-features.js), [context menus](https://github.com/saeedsai/ProMathStudio/blob/ee30466134ae004208d33c5fe64c83dcaa6d374a/src/context-actions.js).
- [CI test suite](https://github.com/saeedsai/ProMathStudio/tree/ee30466134ae004208d33c5fe64c83dcaa6d374a/tests), [Quality workflow](https://github.com/saeedsai/ProMathStudio/blob/ee30466134ae004208d33c5fe64c83dcaa6d374a/.github/workflows/quality.yml).
- [Feature limits](https://github.com/saeedsai/ProMathStudio/blob/main/docs/FEATURES_AND_LIMITATIONS.md), [symbolic engine](https://github.com/saeedsai/ProMathStudio/blob/main/docs/SYMBOLIC_ENGINE.md), [advanced mathematics](https://github.com/saeedsai/ProMathStudio/blob/main/docs/ADVANCED_MATHEMATICS.md), [numerical mathematics/Python](https://github.com/saeedsai/ProMathStudio/blob/main/docs/NUMERICAL_AND_PYTHON.md), [graphing](https://github.com/saeedsai/ProMathStudio/blob/main/docs/GRAPHING.md), [tables](https://github.com/saeedsai/ProMathStudio/blob/main/docs/DATA_TABLES.md).
- [Tests and caveats](https://github.com/saeedsai/ProMathStudio/blob/main/docs/TESTING.md). The repo README/docs contain known stale descriptions (e.g. old workspace count and some old Python/Table formula examples); **the audited source is preferred**.

### External capability baselines (official vendor documentation)

- [MATLAB mathematics](https://www.mathworks.com/help/matlab/mathematics.html) — numeric LA, FFT, integration/ODEs, interpolation, sparse matrices, geometry, graph algorithms.
- [MATLAB Symbolic Math Toolbox](https://www.mathworks.com/help/symbolic/mathematics.html) and [Symbolic equation solving](https://www.mathworks.com/help/symbolic/equation-solving.html) — CAS, systems, ODEs, DAE workflow, exact algebra and high precision.
- [MATLAB symbolic calculus](https://www.mathworks.com/help/symbolic/calculus.html) — limits, vector calculus, series, integrals, Laplace/Fourier/Z/Hilbert transforms.
- [MATLAB Optimization Toolbox](https://www.mathworks.com/help/optim/index.html) — linear, nonlinear, quadratic, conic and integer programming.
- [MATLAB PDE Toolbox](https://www.mathworks.com/help/pde/) — 2D/3D finite-element geometry, meshes and linear/nonlinear PDEs.
- [MATLAB Statistics and Machine Learning Toolbox](https://www.mathworks.com/help/stats/index.html) — probability, inference, regression, classification, clustering.
- [MATLAB signal processing](https://www.mathworks.com/help/overview/signal-processing.html) — DSP, filters, spectrograms, transforms.
- [Simulink documentation](https://www.mathworks.com/help/simulink/) — block-diagram model-based simulation.
- [Full MathWorks product lineup](https://www.mathworks.com/products.html) — distinguish base MATLAB from optional toolboxes.
- [Wolfram equation solving](https://reference.wolfram.com/language/guide/EquationSolving) and [Wolfram Language documentation](https://reference.wolfram.com/) — symbolic/numeric systems, differential equations, inequalities, higher mathematics and visualization.

### Important accuracy caveats

- **An engine being available is not a promise a particular equation will have a closed-form answer.** Differentiation, integration, nonlinear solves, ODEs and PDEs depend on domains, assumptions and problem classes; some problems are mathematically undecidable or unsolvable in elementary functions.
- **Python scripts are a workaround, not native product coverage.** An analyst might import extra libraries or write numerical code in the Data Tables Python editor; that does not mean the UI implements the corresponding MATLAB toolbox functionality.
- **Test coverage is narrower than the inventory.** Structural/Playwright checks cover representative paths and embedded SymPy tests, not exhaustive live network/Pyodide, system stability at maximum sizes, scientific correctness/accuracy, or all export-client compatibility.
- **Potential first-use dependency:** full SymPy, Python custom functions and pandas Python scripts download Pyodide packages; offline-only claims apply to native functionality and cached dependencies where available.
- **Versioning and dates:** this is a **snapshot of commit `ee304661`** on 26 October 2026. Features added after that SHA are outside this inventory.
