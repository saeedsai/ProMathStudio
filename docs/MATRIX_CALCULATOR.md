# Matrix calculator (bounded native functionality)

ProMathStudio offers a small **real-valued matrix calculator** inside the **Calculator** workspace. Open **Matrix calculator · 2×2 / 3×3**, choose 2 or 3 rows and columns, edit the numeric grid, then select **Determinant**, **Transpose**, **Inverse**, **A + B**, **A − B**, or **A × B**. Binary operations use independently sized Matrix B.

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

**Send result to Equation Editor** transfers a scalar or a `matrix([row],[row])` mathematical representation for further presentation/notation. This is **not** a general-purpose matrix algebra parser in the scientific Calculator input.

## Scope, precision and safeguards

- Real numbers only, dimension 2×2, 2×3, 3×2 or 3×3. No complex matrices, vectors, general sparse matrices or arbitrary large matrix dimensions.
- Determinant and inverse require square matrices. Transpose supports rectangular matrices. Addition/subtraction require equal dimensions; multiplication requires A columns = B rows.
- Uses browser double precision, Gaussian elimination with partial row pivoting, Gauss–Jordan inverse and an inverse residual check. The inverse rejects exact and near singular matrices based on a scaled tolerance; it is not a condition-number-certified solver.
- Nonempty finite numeric grid values required; magnitude cap `1e12` per entry. No arbitrary-precision exact rational arithmetic.
- Result display is rounded to approximately 12 significant digits; avoid making safety-critical engineering conclusions without independent validation.
- No Pyodide or network dependency for these six operations. No automatic project backup/persistence of the transient matrix grid in this first release.
- Tests: `tests/smoke_matrix.py`, `tests/smoke_matrix_arithmetic.py`, plus source-to-bundle check `tests/test_data_source.py`. GitHub CI runs the full surrounding regression suite; physical-device/mobile and independent numerical-library comparisons remain additional QA.

## Next enhancements

General-dimension arrays, row-reduced echelon form, `Ax=b` workflows, eigenvalues, SVD, QR, LU and sparse solvers remain distinct planned gaps in the frozen [feature inventory](FEATURE_INVENTORY_AND_MATLAB_GAP_ANALYSIS_2026-10-26.md). Do not count them as finished solely because matrix notation already exists in Equation Editor.
