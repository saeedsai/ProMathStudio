# Symmetric matrix eigenanalysis (development candidate)

In **Calculator → Matrix calculator**, enter a real symmetric square 2×2 or 3×3 matrix A and choose **Eigen (symmetric A)**. The app reports eigenvalues in descending order and an orthonormal eigenvector matrix V, where each column corresponds to the eigenvalue in the same position. Select **Eigenvectors** or **Eigenvalues** under **Eigen output for editor**, then send the chosen matrix to Equation Editor.

Example: A = [[2,1],[1,2]] gives eigenvalues 3 and 1. A = diag(1,2,3) gives eigenvalues 3, 2, 1. Repeated eigenvalues are allowed; eigenvectors inside a repeated eigenspace are not unique.

The offline Jacobi method uses at most 64 plane rotations, scaled arithmetic, finite real entries of magnitude at most 1e12 and a symmetry tolerance of 1e-12 relative to the largest matrix entry. It verifies A·V ≈ V·diag(λ), A ≈ V·diag(λ)·Vᵀ and VᵀV ≈ I, with relative/absolute residual thresholds of 1e-8. A nonsymmetric or rectangular matrix is rejected rather than silently returning incorrect real-only eigenvectors. Near-degenerate eigenspaces and ill-conditioned scales have ordinary double-precision limitations. This is not a general nonsymmetric or complex eigensolver.

Numerical reference and Playwright regression are in `tests/smoke_matrix_eigen.py`; exact-head full Quality, PR, main and Pages deployment are required before marking released.
