# Data Tables workspace

ProMathStudio provides an in-browser spreadsheet-style workbook. Open **Data tables** in the top workspace menu. Existing calculator, equation editor, solver, graphs, notebook and connected workspace remain available.

## Workbooks

Each project can hold up to **20 tables**, with up to **6,000 rows** and **32 columns** per table. Switch between tables using their tabs; add, duplicate, rename or delete a sheet. Edit any header or cell. The top filter searches computed values, and sorting can sort by a selected column. The editor renders the first 150 matching rows for performance (all rows are stored, processed and exported).

A plain cell is text or a number. A formula begins with `=`. The column headers appear above the numbered data rows. **Row 1 is the first data row**, so `A1` is the first data cell. Formula examples:

```
=A1*B1
=SUM(A1:A4)
=AVERAGE(B1:B5)
=COUNT(A1:A99)
=MIN(A1:A9)+MAX(B1:B9)
=IF(A1>2,B1,0)
=IF(A1>0,IF(B1>3,B1,0),0)
=SUM(IF(A1>0,2,0),IF(A1<0,9,3))
=Revenue!B1*1.2
```

The expression evaluator implements arithmetic `+ - * / ^`, parentheses, cell references (including `SheetName!A2`), aggregate functions SUM, AVERAGE/AVG, MIN, MAX, COUNT and IF conditions. Nested `IF` calls also work inside arithmetic and aggregates. `IF` evaluates only the chosen branch, so an unselected branch with `#REF!`, a cycle or a division by zero does not invalidate the result. Comparisons in nested conditions are scoped to their own parentheses. Malformed `IF` argument counts return `#IF`. Cyclic references display `#CYCLE`. Formula calculation is **not JavaScript eval**, and pasted source code cannot execute. Insert/delete row and column actions (toolbar or cell context menu) rewrite references in every workbook sheet, including `Sheet!A1`, `'Sheet Name'!A1`, and `$A$1` anchors, to keep pointing to the original cell. A deleted referenced cell yields `#REF!` rather than silently reading a different cell. `$` markers are accepted and retained in cell/range formulas; they do not prevent structural shifts. Deleting a row or column shrinks surviving aggregate ranges, preserving `$` anchors; deleting the entire referenced interval yields `#REF!`. Aggregate ranges may refer to another sheet using one qualifier before the first endpoint, e.g. `=SUM('My Data'!A1:B3)`. Two independently qualified endpoints are not supported. Stable row sorting preserves cell identities for single-cell references across sheets, including quoted sheet names and `$` anchors. A same-sheet aggregate range is remapped only when its referenced rows remain contiguous; otherwise the sort is rejected atomically without changing any workbook cells. Qualified cross-sheet aggregate ranges are remapped on sort when their rows stay contiguous; otherwise the sort is rejected atomically. Equal-key rows retain their original order. The current engine does not implement Excel's full formula language, date functions or array-spill functions. Use distinct table names for cross-sheet references.

## Relational operations

Choose **Left table**, **Right table** and **Operation**:

- INNER, LEFT, RIGHT or FULL OUTER JOIN match key columns (select each table's join key). Duplicate column names from the right side are prefixed with its table name. JOIN uses equality of the displayed cell values, so distinguish numeric strings carefully.
- UNION ALL appends all rows, including duplicates. UNION DISTINCT removes duplicates. INTERSECT returns rows present in both, and EXCEPT returns rows from the left not present in the right. These set operations require the **same number of columns**, comparing values by column position.

Every operation produces a **new table**, leaving the originals intact. The 6,000-row/32-column result limits still apply. There is no remote SQL database or user-authored SQL query execution.

## Import and export

Use Data Tables → **Import CSV / TSV / JSON**. The importer accepts headed CSV/TSV files and several JSON tabular layouts. Maximum source file size **1 MB**. Export the active sheet as CSV or JSON. Both exports use **calculated values**; for formulas and sheet links, save the **MathStudio project JSON** using the Connected Workspaces panel at the bottom. An advanced import preview and X/Y/Z mapping control also lives inside Data Tables, not Graphs.

## Graphs and charts

Use **Show in graphs** or open Graphs and choose a table, X/category column, Y/value column, optional Z column, and a chart type:

- 2D scatter or connected line; 3D scatter or regular grid mesh (requires numeric X, Y, Z).
- Bar chart: sums repeated category labels; supports positive/negative values.
- Pie chart: percentages of positive values; zero/negative values are excluded.

Charts with more than 24 categories group the remainder under **Other**. Bar/Pie export to PNG. Equation curves/surfaces can still be plotted with imported data in the original graph engine. Ranges/graph controls remain available there.

## Persistence and privacy

Tabs, raw cell entries, formulas, and source tables are saved to browser localStorage under `mathstudio-tables-v1`, when permitted by the browser. **Save project** includes optional `tables` state in project format version 1; older backups without `tables` continue to open and initialize a default data table. The app runs locally and does not transmit imported data to a server. Be mindful of browser quota and project JSON file-size limits: export smaller datasets if a project backup exceeds the 2 MB importer limit.