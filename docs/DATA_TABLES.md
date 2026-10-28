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
=IF(A1>0,2,3)+IF(B1>0,4,5)
=Revenue!B1*1.2
```

The expression evaluator implements arithmetic `+ - * / ^`, parentheses, cell references (including `SheetName!A2`), aggregate functions SUM, AVERAGE/AVG, MIN, MAX, COUNT and IF conditions. Nested `IF` calls also work inside arithmetic and aggregates. `IF` evaluates only the chosen branch, so an unselected branch with `#REF!`, a cycle or a division by zero does not invalidate the result. Comparisons in nested conditions are scoped to their own parentheses. Malformed `IF` argument counts return `#IF`. Cyclic references display `#CYCLE`. Formula calculation is **not JavaScript eval**, and pasted source code cannot execute. Insert/delete row and column actions (toolbar or cell context menu) rewrite references in every workbook sheet, including `Sheet!A1`, `'Sheet Name'!A1`, and `$A$1` anchors, to keep pointing to the original cell. A deleted referenced cell yields `#REF!` rather than silently reading a different cell. `$` markers are accepted and retained in cell/range formulas; they do not prevent structural shifts. Deleting a row or column shrinks surviving aggregate ranges, preserving `$` anchors; deleting the entire referenced interval yields `#REF!`. Aggregate ranges may refer to another sheet using one qualifier before the first endpoint, e.g. `=SUM('My Data'!A1:B3)`. Two independently qualified endpoints are not supported. Stable row sorting preserves cell identities for single-cell references across sheets, including quoted sheet names and `$` anchors. A same-sheet aggregate range is remapped only when its referenced rows remain contiguous; otherwise the sort is rejected atomically without changing any workbook cells. Qualified cross-sheet aggregate ranges are remapped on sort when their rows stay contiguous; otherwise the sort is rejected atomically. Equal-key rows retain their original order. The current engine does not implement Excel's full formula language, date functions or array-spill functions. Use distinct table names for cross-sheet references.

## Relational operations

Choose **Left table**, **Right table** and **Operation**:

- INNER, LEFT, RIGHT or FULL OUTER JOIN match key columns (select each table's join key). Duplicate column names from the right side are prefixed with its table name. JOIN uses equality of the displayed cell values, so distinguish numeric strings carefully.
- UNION ALL appends all rows, including duplicates. UNION DISTINCT removes duplicates. INTERSECT returns rows present in both, and EXCEPT returns rows from the left not present in the right. These set operations require the **same number of columns**, comparing values by column position.

JOIN uses an indexed right-hand key lookup to avoid quadratic comparisons for large tables. Duplicate keys still produce every matching pair in original left-then-right order, and empty keys match empty keys. Invalid join-key selections, outputs wider than 32 columns, or results exceeding 6,000 rows are rejected before creating a result sheet.

Every operation produces a **new table**, leaving the originals intact. The 6,000-row/32-column result limits still apply. There is no remote SQL database or user-authored SQL query execution.

## Import and export

Use Data Tables → **Import CSV / TSV / JSON**. The importer accepts headed CSV/TSV files and several JSON tabular layouts. Maximum source file size **1 MB**. Export the active sheet as CSV or JSON. Both exports use **calculated values**; for formulas and sheet links, save the **MathStudio project JSON** using the Connected Workspaces panel at the bottom. An advanced import preview and X/Y/Z mapping control also lives inside Data Tables, not Graphs.


### XLSX import and export (bounded offline scope)

**Export XLSX** downloads one or two selected sheets. **Import XLSX** accepts a workbook with one or two sheets, up to 1,000 data rows and 32 columns each. Import replaces the current Data Tables workbook **only after confirmation**. Save your existing project JSON first if you want to retain it. The importer validates ZIP central/local records, CRC-32, expanded sizes (12 MB aggregate, 5 MB per part), duplicate/path-traversal entries, workbook relationships, sheet names, and XML before modifying any table. It accepts stored and DEFLATE-compressed ZIP entries in browsers supporting the native \`DecompressionStream('deflate-raw')\` API; no network service is used. Errors leave the current tables unchanged.

The first Excel row contains column headers, so an XLSX formula reference \`A2\` maps to ProMathStudio's data cell \`A1\`; references to the Excel header row are rejected. Numeric/text cells, inline/shared strings, sparse rows, ordinary formulas and quoted sheet references are supported. Import **does not execute** formulas or macros. External workbook links, drawings, pivot tables, complex worksheet relationships, advanced formula types, unsupported XML/ZIP features and workbooks with more than two sheets are rejected rather than silently discarded. Importing a formula does not guarantee that the Data Tables expression evaluator can calculate every Excel function. Excel formatting is not imported.

## Graphs and charts

Use **Show in graphs** or open Graphs and choose a table, X/category column, Y/value column, optional Z column, and a chart type:

- 2D scatter or connected line; 3D scatter or regular grid mesh (requires numeric X, Y, Z).
- Bar chart: sums repeated category labels; supports positive/negative values.
- Pie chart: percentages of positive values; zero/negative values are excluded.

Charts with more than 24 categories group the remainder under **Other**. Bar/Pie export to PNG. Equation curves/surfaces can still be plotted with imported data in the original graph engine. Ranges/graph controls remain available there.

## Persistence and privacy

Tabs, raw cell entries, formulas, and source tables are saved to browser localStorage under `mathstudio-tables-v1`, when permitted by the browser. **Save project** includes optional `tables` state in project format version 1; older backups without `tables` continue to open and initialize a default data table. The app runs locally and does not transmit imported data to a server. Be mindful of browser quota and project JSON file-size limits: export smaller datasets if a project backup exceeds the 2 MB importer limit.
## XLSX export (bounded offline first increment)

Open **Data Tables → Excel XLSX export · offline** and choose one or two sheets. **Download XLSX** creates a standard uncompressed OpenXML ZIP entirely in the browser; no remote service or external dependency is required. The export preserves headers, numeric cells, text (including leading-zero identifiers), blanks and formulas. Data Tables treats the first data row as row 1; XLSX adds a header row, so cell and range references in formulas are shifted by one row while quoted string literals are left unchanged. Excel recalculates formulas on opening the workbook. The exported file is capped at 5 MB, 1,000 data rows and 32 columns per sheet, with Excel-compatible sheet names. Formula syntax supported by Excel can differ from the Data Tables evaluator; verify formulas in Excel before relying on results.

**Not yet implemented:** XLSX import, compressed ZIP/deflate parsing, external workbook compatibility and an end-to-end import/export round-trip. These remain the next P0-XLSX-ROUNDTRIP work item. This increment does not claim full Excel compatibility or transactional import rollback. See `tests/smoke_xlsx_export.py` for ZIP, XML, formula and UI tests.
