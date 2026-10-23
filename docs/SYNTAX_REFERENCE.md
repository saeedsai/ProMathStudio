# Typed mathematics syntax

**Principle:** use text syntax with `^` for powers, `_` for indices, function calls with parentheses, and explicit grouping for fractions and negative powers.

| Type | Example | Meaning |
|---|---|---|
| Arithmetic | `2+3*4`, `(a+b)/c` | Sum/product/division |
| Power | `x^2`, `x^(-1/2)` | Superscript, fractional exponent |
| Subscript | `x_1`, `a_ij` | Subscript |
| Roots | `sqrt(x)`, `root(3,x)` | Square and n-th root notation |
| Constants | `pi`, `e`, `i`, `infty` | π, Euler's number, imaginary unit, infinity |
| Greek | `alpha`, `beta`, `gamma`, `theta`, `lambda`, `sigma`, `omega` | Greek symbols; see palette for more |
| Trig | `sin(x)`, `cos(x)`, `tan(x)` | Trigonometric functions |
| Inverse trig | `asin(x)`, `acos(x)`, `atan(x)` | Inverse functions (not reciprocals) |
| Logs | `ln(x)`, `log(x)`, `exp(x)` | Logarithmic/exponential notation |
| Factorial | `n!`, `factorial(n)` | Factorial, including scalar calculator |
| Abs and vectors | `abs(x)`, `norm(v)`, `vec(v)` | Absolute value, norm, vector accent |
| Equality | `x^2=1` | Solve for chosen variable |
| Comparison | `x<=1`, `x>=0`, `a!=b` | Inequality/inequality syntax |
| Sums | `sum(i=1,n,i^2)` | Summation notation |
| Integral | `int(0,1,x^2,x)` | Definite integral notation |
| Derivative | `diff(x^3,x)`, `diffn(f,x,2)` | Derivative/higher derivative notation |
| Partial | `pdiff(f,x)` | Partial derivative notation |
| Limit | `lim(x->0,sin(x)/x)` | Limit notation |
| Matrix | `matrix([a,b],[c,d])` | Two rows of a matrix |
| Array | `array([a,b],[c,d])` | Array-style layout |
| Parenthesized matrix | `pmatrix([1,2],[3,4])` | Matrix with parentheses |
| Determinant | `det([a,b],[c,d])` | Determinant notation |
| Piecewise | `cases([x,x>=0],[-x,x<0])` | Two conditions |
| Vector | `vector(x,y,z)` | Column vector |
| Binomial | `binom(n,k)` | Binomial coefficient |
| Double integral | `iint(D,f,x,y)` | Two-variable integral |
| Statistics | `expect(X)`, `variance(X)`, `prob(A)` | Probability symbols |

**Important distinctions**

- `x/x-1` means `(x/x)-1`. Type `x/(x-1)` to group the denominator.
- `sin^-1(x)` in a palette may be typeset as inverse sine; for evaluation use `asin(x)`. `1/sin(x)` is the reciprocal.
- Equation editor is a **typesetter**; a typed derivative is not automatically evaluated unless passed to Symbolic solver with a supported operation.
- Calculator's degree/radian selector does not change the graph engine's radians convention.
- The rich palette offers additional syntax beyond the examples here, but not every notation template has executable numerical semantics.
- Implicit multiplication such as `2x` can work in math parsing; when in doubt use explicit `*` for calculator/graph inputs.

## Working examples

- Enter `(x-1)^2` in solver, select Expand → `x^2-2x+1`.
- Enter `x^2=-1` in solver, select Solve → two imaginary roots.
- Enter `(x^2-1)/(x-1)` in solver; note `x=1` is excluded from the original domain.
- Enter `y=if(x<0,-x,x)` in the 2D graph for absolute-value-like piecewise behavior.

[Back to user guide](USER_GUIDE.md)
