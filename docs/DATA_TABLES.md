# Data Tables workspace

ProMathStudio provides an in-browser spreadsheet-style workbook. Open **Data tables** in the top workspace menu. Existing calculator, equation editor, solver, graphs, notebook and connected workspace remain available.

## Workbooks

Each project can hold up to **20 tables**, with up to **6,000 rows** and **32 columns** per table. Switch between tables using their tabs; add, duplicate, rename or delete a sheet. Edit any header or cell. The top filter searches computed values, and sorting can sort by a selected column. The editor renders the first 150 matching rows for performance (all rows are stored, processed and exported).

A plain cell is text or a number. A formula begins with `=`. Row **1** contains column headers, so `A2` is the first data cell. Formula examples:

```
=A2*B2
=SUM(A2:A5)
=AVERAGE(B2:B6)
=COUNT(A2:A100)
=MIN(A2:A10)+MAX(B2:B10)
=IF(A2>2,B2,0)
=Revenue!B2*1.2
```

The expression evaluator implements arithmetic `+ - * / ^`, parentheses, cell references (including `SheetName!A2`), aggregate functions SUM, AVERAGE/AVG, MIN, MAX, COUNT and IF conditions. Cyclic references display `#CYCLE`. Formula calculation is **not JavaScript eval**, and pasted source code cannot execute. The current engine does not implement Excel's full formula language, date functions, array-spill functions, or formula-relative reference adjustment when sorting. Use distinct table names for cross-sheet references.

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