# Matrix calculator (bounded native functionality)

**Keyboard grid navigation:** When a numeric matrix cell is focused, unmodified arrow keys move focus to the adjacent cell within that grid (Matrix A, Matrix B, RHS b or weights w). At a grid edge, focus stays put; arrows do not increment numeric values. Tab and modified shortcuts keep their browser behavior. Typing edits numbers normally, and changing 2×2/3×3 dimensions retains supported drafts. Arrow navigation works with the existing input disclosures and on mobile with an attached keyboard. This is a bounded UI convenience, not a change to matrix algorithms. Tests: `tests/test_matrix_grid_keyboard.py` and `tests/smoke_matrix_grid_keyboard.py`.

Matrix A is the primary labeled section. Matrix B, right-hand side b and observation weights w are independently collapsible using mouse or keyboard. Initially expanded for compatibility, they preserve input drafts while collapsed and automatically reopen when a selected operation needs them. All 16 operations and Equation Editor transfer remain available.

ProMathStudio offers a small **real-valued matrix calculator** inside the **Calculator** workspace. Open **Matrix calculator · 2×2 / 3×3**, choose 2 or 3 rows and columns, edit the numeric grid, then select **Determinant**, **Transpose**, **Inverse**, **A + B**, **A − B**, or **A × B**, **RREF (A)**, **Rank (A)**, **Solve A·x=b**, **LU (P·A=L·U)**, **QR (A=Q·R)**, **Least squares (A·x≈b)**, **SVD (2×2 A)**, or **Pseudoinverse (2×2 / 3×2 A)**. Binary operations use independently sized Matrix B.

## Operations and examples

| Input matrix | Operation | Expected output |
|---|---|---|
| `[[1,2],[3,4]]` | Determinant | `-2` |
| `[[1,2],[3,4]]` | Inverse | `[[-2,1],[1.5,-0.5]]` |
| `[[0,1],[1,0]]` | Determinant | `-1` (row pivoting) |
| `[[1,2,3],[0,1,4],[5,6,0]]` | Determinant | `1` |
| `[[1,2,3],[4,5,6]]` | Transpose | `[[1,4],[2,5],[3,6]]` |
| `[[1,2],[2,4]]` | Inverse | Error: singular matrix |
| A=`[[1,2],[3,4]]`, B=`[[5,6],[7,8]]` | A + B | `[[6,8],[10,12]]` |
| Same A, B | A − B | `[[-4,-4],[-4,-4]]` |
| Same A, B | A × B | `[[19,22],[43,50]]` |
| A=`[[1,2,3],[4,5,6]]`, B=`[[7,8],[9,10],[11,12]]` | A × B | `[[58,64],[139,154]]` |

**Solve A·x=b** uses a separate right-hand-side vector b (one entry per row of square A). Example: A=`[[1,2],[3,4]]`, b=`[5,11]` gives x=`[1,2]` with a row-relative residual. Scaled pivoting and singularity tests apply; inconsistent systems report no solution and singular/near-singular systems report no unique solution. This bounded 2×2/3×3 real solver is not least squares. Send its column-vector solution to Equation Editor. Tests: `tests/smoke_matrix_solve.py`.

**Ax=b residual diagnostics:** For a successful 2×2/3×3 solve, the Matrix result now shows (1) the existing maximum row-wise relative residual, (2) maximum absolute residual `||Ax-b||∞`, and (3) normwise backward error `||Ax-b||∞/(||A||∞||x||∞+||b||∞)`. The latter uses the infinity norm and indicates the size of a relative perturbation consistent with the computed solution; it is **not** a condition-number estimate or a bound on forward solution error. The zero right-hand-side case yields zero diagnostics for a full-rank system. Inputs are not mutated; singular and inconsistent systems still report errors and disable Equation Editor transfer. Node and browser coverage: `tests/test_matrix_solve_backward_error.py`, `tests/smoke_matrix_solve_backward_error.py`.

**Infinity-norm condition number:** Both **Solve A·x=b** and **Inverse** now report `κ∞(A) = ||A||∞ × ||A⁻¹||∞` for supported nonsingular 2×2/3×3 real matrices. The inverse is computed through the shared scaled-partial-pivot solver; no second elimination kernel or normal equations are introduced. For `diag(1e-9,1e9)`, κ∞ is `1e18`, indicating that small relative input perturbations can greatly affect the solution. This is a matrix sensitivity measure, **not** a residual or a guarantee of forward accuracy. When the condition diagnostic cannot be evaluated, a successful Ax=b result remains available and the condition is labeled unavailable; singular matrices continue to reject solve/inverse. Node and Chromium regressions: `tests/test_matrix_condition_infinity.py` and `tests/smoke_matrix_condition_infinity.py`.

**Shared inverse solver:** The inverse now solves `A·x=e_j` for each identity column using the same scaled-partial-pivot kernel as **Solve A·x=b**, rather than a separate Gauss–Jordan implementation. For example, `A=[[1e-9,0],[0,1e9]]` has inverse `[[1e9,0],[0,1e-9]]`: independent rows are retained despite large differences in scale. Exact and near-singular matrices are rejected; both operations remain bounded to 2×2/3×3 real inputs and use floating-point residual checks. See `tests/test_matrix_shared_solve_inverse.py` and `tests/smoke_matrix_shared_solve_inverse.py`.

**Send result to Equation Editor** transfers a scalar or a `matrix([row],[row])` mathematical representation for further presentation/notation. This is **not** a general-purpose matrix algebra parser in the scientific Calculator input.

## RREF and rank (bounded real matrices)

The **RREF (A)** action computes reduced row-echelon form and displays the numerical rank for the 2×2 through 3×3/rectangular supported shapes. **Rank (A)** returns the scalar rank. Both support Equation Editor transfer. A scaled partial-pivot algorithm uses a relative tolerance of `1e-12` against each row's original maximum magnitude; near-dependent rows can be treated as zero. Results are approximate floating-point results, not exact rational row reduction. Example: `[[1,2,3],[2,4,6]]` gives RREF `[[1,2,3],[0,0,0]]`, rank 1; `[[1e12,0],[0,1]]` remains rank 2. Tests: `tests/smoke_matrix_rref.py`.

## Pivoted LU decomposition (bounded real square matrices)

**LU (P·A=L·U)** decomposes a full-rank real 2×2 or 3×3 Matrix A using Doolittle elimination and scaled partial row pivoting. P is the permutation matrix (P·A reorders A's rows), L has unit diagonal and is lower triangular, and U is upper triangular. The result shows all three factors and a row-relative reconstruction residual; the **LU factor for editor** selector lets you transfer L, U, or P individually to Equation Editor. Example: A=`[[0,1],[1,0]]` produces P=`[[0,1],[1,0]]`, L=I, U=I. Singular and nearly singular inputs (relative pivot tolerance `1e-12`) are rejected rather than returning misleading factors. The implementation does not compute a condition number, complex LU, or arbitrary matrix sizes. Test: `tests/smoke_matrix_lu.py`.

## Thin QR decomposition (bounded real matrices)

**QR (A=Q·R)** computes an economy-size decomposition of full-column-rank real 2×2, 3×2 and 3×3 matrices. Reorthogonalized modified Gram–Schmidt returns Q with orthonormal columns and upper-triangular R, along with reconstruction and orthogonality residuals. The QR factor selector transfers Q or R to Equation Editor. Wide 2×3 matrices and dependent/nearly dependent columns (relative tolerance 1e-12) are rejected. This QR action only displays factors; the separate least-squares action uses those factors to solve 3×2 tall systems. Neither supports pivoted or general-dimensional QR. Test: `tests/smoke_matrix_qr.py`.

## Least squares for tall real systems (bounded 3×2)

**Least squares (A·x≈b)** computes the unique minimum-residual solution of a full-column-rank 3×2 real system, using thin QR and triangular back substitution (not normal equations). Enter three values in the right-hand-side b grid. For A=`[[1,0],[0,1],[1,1]]` and b=`[1,2,4]`, the solution is x=`[4/3,7/3]`, with Euclidean residual norm `sqrt(1/3)`. An exactly consistent b=`[2,-1,1]` gives x=`[2,-1]` and zero residual. The output includes residual norm, relative residual and normalized Aᵀ(Ax−b) orthogonality; the solution transfers to Equation Editor as a column vector. Rank-deficient or nearly dependent matrices, square/wide shapes, and missing/nonfinite b are rejected. This is not a general rectangular, weighted or robust least-squares solver. Test: `tests/smoke_matrix_least_squares.py`.

## Scope, precision and safeguards

- Real numbers only, dimension 2×2, 2×3, 3×2 or 3×3. No complex matrices, vectors, general sparse matrices or arbitrary large matrix dimensions.
- Determinant and inverse require square matrices. Transpose supports rectangular matrices. Addition/subtraction require equal dimensions; multiplication requires A columns = B rows.
- Uses browser double precision and one shared scaled-partial-pivot Ax=b solver for both direct linear-system solutions and the inverse (solving against identity columns), with independent inverse residual verification. The inverse rejects exact and near singular matrices based on a scaled tolerance; it is not a condition-number-certified solver.
- Nonempty finite numeric grid values required; magnitude cap `1e12` per entry. No arbitrary-precision exact rational arithmetic.
- Result display is rounded to approximately 12 significant digits; avoid making safety-critical engineering conclusions without independent validation.
- No Pyodide or network dependency for these native matrix operations. No automatic project backup/persistence of the transient matrix grid in this first release.
- Tests: `tests/smoke_matrix.py`, `tests/smoke_matrix_arithmetic.py`, plus source-to-bundle check `tests/test_data_source.py`. GitHub CI runs the full surrounding regression suite; physical-device/mobile and independent numerical-library comparisons remain additional QA.

## Next enhancements

General-dimension arrays, larger/weighted least-squares and underdetermined systems, eigenvalues, SVD, pivoted/general-dimensional QR and sparse solvers remain distinct planned gaps in the frozen [feature inventory](FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md). Do not count them as finished solely because matrix notation already exists in Equation Editor.

## Real 2×2 singular-value decomposition

**SVD (2×2 A)** computes A=U·diag(σ)·Vᵀ for a finite real 2×2 matrix, including rank-deficient and zero matrices. Singular values are nonnegative and descending. The method scales entries before a one-sided Jacobi rotation, uses the determinant to recover a small singular value without cancellation, and returns orthonormal U/V, reconstruction/orthogonality residuals, and a **numerical** rank at a relative 1e-12 cutoff. A null condition number means singular or not representable as a finite number; a tiny but nonzero singular value may still be reported even if the numerical rank is 1. Example A=[[1,2],[3,4]] has singular values approximately 5.464985704219 and 0.365966190626. The SVD factor selector transfers U, singular values as a column, or V to Equation Editor. This is not general-size/complex SVD or a pseudoinverse. Browser regression: `tests/smoke_matrix_svd.py`. Previously released with exact-head CI and Pages verification.

## Rectangular 3×2 Moore–Penrose pseudoinverse

**Pseudoinverse (2×2 / 3×2 A)** also supports tall real 3×2 matrices, including full-rank, rank-one and all-zero inputs. It returns a 2×3 matrix A⁺, numerical rank, and residual diagnostics for all four Moore–Penrose identities. A scaled two-column Jacobi rotation and relative 1e-12 singular-value cutoff avoid squaring the condition number through unscaled normal equations. For A=`[[1,0],[0,1],[1,1]]`, A⁺=`[[2/3,-1/3,1/3],[-1/3,2/3,1/3]]`; multiplying A⁺ by b=`[1,2,4]` yields the least-squares x=`[4/3,7/3]`. Rank-deficient A=`[[1,2],[2,4],[3,6]]` yields A⁺=`[[1,2,3],[2,4,6]]/70`, giving the minimum-norm solution. Near-singular inputs that fail the numerical identity checks are rejected rather than silently accepted. Wide 2×3 and 3×3 pseudoinverses remain out of scope. Test: `tests/smoke_matrix_pseudoinverse_rectangular.py`.

## Condition-number sensitivity guidance

Solve Ax=b and Inverse now show a heuristic warning when κ∞(A) ≥ 1e8 for supported real 2×2/3×3 matrices. This is a practical binary64 sensitivity warning threshold, not a strict mathematical boundary. A=diag(1e-9,1e9) has κ∞=1e18 and is flagged; A=I has κ∞=1 and is not flagged. A small residual or normwise backward error measures how well the computed solution satisfies the supplied equations, not guaranteed forward accuracy for an ill-conditioned matrix. Values below the threshold are **not** accuracy-certified. The shared scaled-pivot solver, singular checks and Equation Editor transfer are unchanged. Reference, threshold, invalid-input, standalone and browser/mobile regressions: `tests/test_matrix_condition_guidance.py` and `tests/smoke_matrix_condition_guidance.py`.


## Contextual Equation Editor transfer controls

The Matrix Calculator now separates operation buttons from the result-transfer action row. LU, QR, symmetric Eigen and SVD factor/output selectors appear **only after a successful result of the corresponding operation**; the other three selectors stay hidden. Editing an input, changing dimensions, or producing an invalid/singular result hides every factor selector and disables stale result transfer. This is a presentation change, not a new numerical algorithm: all 16 matrix operations, saved input values, factor choices, keyboard focus, and Equation Editor transfer remain available. The transfer button stays visible and disabled until a successful calculation. Regression coverage: `tests/test_matrix_contextual_transfer.py`, `tests/smoke_matrix_contextual_transfer.py`.
