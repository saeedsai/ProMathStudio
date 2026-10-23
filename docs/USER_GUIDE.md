# User guide

## Open the application

Open `index.html` directly, or use the GitHub Pages site after it is enabled. Use Chrome, Edge or Firefox with JavaScript. The application has four tabs and a connected **Working equation** panel at the bottom of each active workspace.

### 1 — Calculator

Open **Calculator**, type an expression and press **Calculate** or Enter. Supported examples: `5!+3^2`, `asin(0.5)`, `sqrt(-1)`, `ln(e^2)`. Change angle units from **Radians** to **Degrees** when needed. Adjust precision from the adjacent menu. Use **Ans** to refer to the prior calculated value. Reopen a history entry by clicking it. Complex values display using `i`.

Only scalar expressions with numeric input can be calculated. For an equation involving unknowns, send it to Symbolic solver instead.

### 2 — Equation editor

Open **Equation editor**, type `x^2=(x/(x-1))^(-1/2)` and inspect **Live preview**. Press Enter or **Add equation** to save it to the notebook; Shift+Enter adds a text line. You can edit previously saved entries. The palette sidebar groups symbols, Greek letters, matrices, calculus and more; its search finds templates. **Copy LaTeX**, **Copy for Word**, **Copy image**, **Word .docx** and **Export .tex** are available. The **Python / SymPy** panel produces corresponding code (which you should review before running elsewhere).

### 3 — Symbolic solver

Use **Send to → Solve** from the connected bar or open **Symbolic solver** and enter the expression in its displayed equation input.

1. Choose operation: Auto, Expand, Simplify, Factor, Solve, Differentiate, Integrate, or Numerical roots.
2. Choose the variable (initially `x`).
3. Choose engine: Auto (offline first), Built-in (offline only), or SymPy.
4. Press **Execute** or Ctrl+Enter; inspect the result list, generated SymPy code and messages.
5. Send a *specific result* to Calculator/Editor/Graph using its **Send to…** control, or save the result to notebook.

`x^2=1` has ±1 and `x^2=-1` has ±i. For `x^9-x-1=0`, SymPy may produce `RootOf` or numerical roots rather than radicals. The first full SymPy run needs internet access and may load for longer than the built-in engine.

### 4 — Graph generator

Open **2D & 3D graphs**. Choose 2D for one or multiple lines such as `y=sin(x)` and `y=cos(x)`; choose 3D for `z=x^2-y^2`. Click **Plot functions** after editing functions. Set axis ranges, pan/rotate with the pointer, zoom with the wheel, reset the view, or **Export PNG**. Trig graph inputs always use radians.

### 5 — Connected workflow

1. Type in **Working equation** or choose an entry in **Select an input, saved equation or result**.
2. Click **Send to** the destination, or **Use open input** to capture the active tool's input.
3. From a symbolic result or notebook card, use its own route dropdown.
4. Choose **Add to current graph** to preserve curves already plotted.
5. Export a **Save project** JSON backup before closing or clearing browser data; use **Open project** to restore it.

Sending an equality to a graph may plot the *residual*, for example `x^2=1` is graphed as `y=(x^2)-(1)`. Sending an unsolved equation to calculator does not automatically choose a solution. Send an individual numeric root instead.

## Keyboard/accessibility notes

Tab navigates controls; Enter in the editor adds/saves an equation, Shift+Enter inserts a newline, Escape cancels edit, Ctrl+Enter invokes symbolic execution. Some browser clipboard APIs require HTTPS, localhost, or permission. For Word, downloading the editable `.docx` is more reliable than pasting clipboard HTML.

## More information

[Syntax reference](SYNTAX_REFERENCE.md) · [Exports](EXPORTS.md) · [Troubleshooting](TROUBLESHOOTING.md)

## Advanced mathematics and floating menus

Floating top buttons show **Symbols**, **Examples**, **Options** and **Help**. The searchable Math Library and example categories open in sliding menus. Options toggles history, Python code and detailed explanations. Help provides nested guides, including curve fitting and ODE/PDE limitations. The Connected Workspaces panel remains at the bottom. Graph axes have an optional collapsible advanced menu. See [Advanced mathematics](ADVANCED_MATHEMATICS.md).

## Numerical methods and spreadsheet Python

In **Symbolic Solver**, press **Numerical methods / PDE** to open a collapsed solver with four methods. Enter a real equation and bracket; a small system and guesses; or a 1D Poisson/heat source/initial expression with domain and boundary conditions. The heat solver rejects unstable time steps. Use **Save output to Data Tables** or **Show numerical results in Graphs** for plots.

In **Calculator → Variable assignments & advanced numeric math**, assign scalars and use `diff`, `int`, `sum`, and `prod` with evaluation points and bounds.

In **Data Tables**, keep the sheet visible and open Table, Filter, Combine, Files or Python as needed. Filter conditions apply to displayed rows only. The Python editor runs your own code with pandas in a browser worker; new `result` DataFrames become new tables. For syntax, method assumptions, limitations and examples, see [Numerical methods and Python](NUMERICAL_AND_PYTHON.md).

## Right-click / long-press actions and numeric bases

Right-click or long-press a table cell, row number, header, table tab, Calculator, Editor, Solver or Graph to open item-specific actions. Use Shift+F10 on a focused control and Escape to close. Calculator has DEC/BIN/HEX modes plus mixed `0x`/`0b` expressions; the Symbols drawer is available in Calculator and inserts into its expression window. For precise limits and details see [Context menus and number bases](CONTEXT_MENUS.md).
