"""Browser regression: reserved aggregates, finite means, nonfinite errors and scale-safe charts."""
import math
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, executable_path=os.getenv("CHROMIUM_PATH") or None,
            args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1280, "height": 850})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.set_content((ROOT / "index.html").read_text(encoding="utf-8"),
                         wait_until="load")
        page.locator('[data-workspace="data"]').click()
        page.evaluate("""() => {
          MathStudio.customFunctions.restore([
            {name:'SUM',params:['x','y'],expression:'99',type:'formula'},
            {name:'COUNT',params:['x','y'],expression:'99',type:'formula'},
            {name:'MEDIAN',params:['x','y'],expression:'99',type:'formula'},
            {name:'IF',params:['a','b','c'],expression:'99',type:'formula'},
            {name:'TWICE',params:['x'],expression:'2*x',type:'formula'},
            {name:'IDENTITY',params:['x'],expression:'x',type:'formula'},
            {name:'BROKEN',params:['x'],expression:'x/0',type:'formula'}
          ]);
          MathStudio.dataTables.restoreState({
            version:1,selected:'sheet-1',tables:[{
              id:'sheet-1',name:'Data1',
              columns:['A','B','C','D','E','F'],
              rows:[['1','=SUM(1e308,1e308)',
                     '=AVERAGE(1e308,1e308)',
                     '=IF(0,SUM(1e308,1e308),TWICE(4))',
                     '=BROKEN(2)',
                     '=SUM(TWICE(2),3)']]
            }]
          });
        }""")
        values = page.evaluate("MathStudio.dataTables.calculate()")
        assert values == [['1', '#NUM!', 1e308, 8, '#VALUE', 7]], values

        def formula(expression):
            return page.evaluate(
                "(expr) => MathStudio.dataTables.formula(expr,'Data1')",
                expression)

        def failure(expression):
            return page.evaluate("""(expr) => {
              try { MathStudio.dataTables.formula(expr,'Data1'); }
              catch(error) { return error.message; }
              return 'NO_ERROR';
            }""", expression)

        # Imported/saved names must not override spreadsheet built-ins.
        assert formula('SUM(2,3)') == 5
        assert formula('COUNT(2,3)') == 2
        assert formula('MEDIAN(1,3)') == 2
        assert formula('IF(1,COUNT(2,3),BROKEN(1))') == 2
        assert formula('SUM(TWICE(2),SUM(1,2))') == 7
        # Numeric arguments must not be stringified into unsupported 1e+308 notation.
        assert formula('IDENTITY(1e308)') == 1e308
        assert abs(formula('TWICE(1e-100)') - 2e-100) < 1e-110

        # Finite averages stay finite even if an intermediate sum would overflow.
        assert formula('AVERAGE(1e308,1e308)') == 1e308
        assert formula('AVG(1e308,1e308)') == 1e308
        assert formula('AVERAGE(1e308,-1e308)') == 0
        assert formula('MEDIAN(1e308,1e308)') == 1e308
        assert formula('SUM(1e308,-1e308)') == 0
        assert failure('SUM(1e308,1e308)') == '#NUM!'
        nested_overflow = failure('SUM(TWICE(1e308),2)')
        assert nested_overflow == '#VALUE', nested_overflow
        assert failure('BROKEN(2)') == '#VALUE'
        assert failure('COUNT(BROKEN(1))') == '#VALUE'
        assert formula('IF(0,BROKEN(1),SUM(1,2))') == 3

        # Exercise raw workbook cells so binary64 subnormals and the true maximum
        # finite value reach the aggregate engine without the expression parser's display rounding.
        original_state = page.evaluate("MathStudio.dataTables.exportState()")
        # Cell references use decimal/scientific syntax only; JS radix prefixes stay text.
        page.evaluate("""() => MathStudio.dataTables.restoreState({
          version:1,selected:'sheet-1',tables:[{
            id:'sheet-1',name:'Data1',columns:['A','B','C','D','E','F','G'],
            rows:[['0x10','0b10','0o10','16',' 2.5e+1 ',' ','1.']]
          }]
        })""")
        for expression, expected in (
            ('A1+1','Not numeric: 0x10'),
            ('B1+1','Not numeric: 0b10'),
            ('C1+1','Not numeric: 0o10')
        ):
            assert failure(expression) == expected
        assert formula('SUM(A1:C1)') == 0
        assert formula('COUNT(A1:C1)') == 0
        assert failure('MEDIAN(A1:C1)') == '#NUM!'
        assert formula('D1+E1') == 41
        assert formula('F1') == 0
        assert formula('G1') == 1
        assert formula('SUM(A1:G1)') == 42
        assert formula('AVERAGE(A1:G1)') == 14
        assert formula('AVG(A1:G1)') == 14
        assert formula('AVERAGE(16,25,1)') == 14
        assert formula('COUNT(A1:G1)') == 3
        assert formula('MEDIAN(A1:G1)') == 16
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", original_state)
        assert page.evaluate("MathStudio.dataTables.calculate()") == values
        page.evaluate("""() => MathStudio.dataTables.restoreState({
          version:1,selected:'sheet-1',tables:[{
            id:'sheet-1',name:'Data1',columns:['A'],rows:[
              ['5e-324'],['5e-324'],
              ['1.7976931348623157e308'],['1.7976931348623157e308'],['1.7976931348623157e308'],
              ['1e308'],['1e-300'],['-1e308'],
              ['-5e-324'],['-5e-324'],
              ['5e-324'],['1e-323'],
              ['1e308'],['1e308'],['-1e308'],
              ['1.7976931348623157e308'],['5e-324'],['-1.7976931348623157e308']
            ]
          }]
        })""")
        assert formula('AVERAGE(A1:A2)') == 5e-324
        assert formula('AVG(A1:A2)') == 5e-324
        assert formula('MEDIAN(A1:A2)') == 5e-324
        assert formula('MEDIAN(A9:A10)') == -5e-324
        assert formula('MEDIAN(A11:A12)') == 1e-323
        largest_average = formula('AVERAGE(A3:A5)')
        assert math.isfinite(largest_average) and largest_average > 1.7e308, largest_average
        cancellation_average = formula('AVERAGE(A6:A8)')
        expected_cancellation_average = 1e-300 / 3
        assert abs(cancellation_average - expected_cancellation_average) <= expected_cancellation_average * 1e-12, (
            cancellation_average, expected_cancellation_average)
        # SUM must preserve finite results after overflowing partial sums or cancellation.
        assert formula('SUM(A6:A8)') == 1e-300
        assert formula('SUM(A13:A15)') == 1e308
        assert formula('SUM(A16:A18)') == 5e-324
        assert formula('SUM(1e308,1e308,-1e308)') == 1e308
        assert failure('SUM(A3:A5)') == '#NUM!'
        aggregate_state = page.evaluate("MathStudio.dataTables.exportState()")
        aggregate_values = page.evaluate("MathStudio.dataTables.calculate()")
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", aggregate_state)
        assert page.evaluate("MathStudio.dataTables.calculate()") == aggregate_values
        page.evaluate("(state) => MathStudio.dataTables.restoreState(state)", original_state)
        assert page.evaluate("MathStudio.dataTables.calculate()") == values
        for width in (390, 768, 1280):
            page.set_viewport_size({"width": width, "height": 850})
            assert page.locator('#dt-sheet').count() == 1
        # Repeated-category aggregation and chart geometry must remain finite at extreme scales.
        page.evaluate("""() => {
          MathStudio.dataTables.restoreState({
            version:1,selected:'chart',tables:[{id:'chart',name:'Chart',
              columns:['Category','Value'],rows:[
                ['A','1e308'],['A','1e308'],['A','-1e308'],['B','1e308']
              ]}]
          });
          document.getElementById('dt-graph-table').value='sheet-1';
          document.getElementById('dt-graph-x').value='0';
          document.getElementById('dt-graph-y').value='1';
          document.getElementById('dt-chart-type').value='pie';
          window.__dtPieSpans=[];
          const proto=CanvasRenderingContext2D.prototype;
          window.__dtOriginalArc=proto.arc;
          proto.arc=function(...args){
            if(this.canvas?.id==='dt-chart-canvas')window.__dtPieSpans.push([args[3],args[4]]);
            return window.__dtOriginalArc.apply(this,args);
          };
          MathStudio.dataTables.plot();
          proto.arc=window.__dtOriginalArc;
        }""")
        pie_spans = page.evaluate("window.__dtPieSpans")
        assert len(pie_spans) == 2, pie_spans
        assert all(math.isfinite(start) and math.isfinite(end) for start, end in pie_spans), pie_spans
        assert all(abs((end - start) - math.pi) < 1e-12 for start, end in pie_spans), pie_spans

        page.evaluate("""() => {
          MathStudio.dataTables.restoreState({
            version:1,selected:'chart',tables:[{id:'chart',name:'Chart',
              columns:['Category','Value'],rows:[['Positive','1e308'],['Negative','-1e308']]}]
          });
          document.getElementById('dt-graph-table').value='sheet-1';
          document.getElementById('dt-graph-x').value='0';
          document.getElementById('dt-graph-y').value='1';
          document.getElementById('dt-chart-type').value='bar';
          window.__dtBarRects=[];
          const proto=CanvasRenderingContext2D.prototype;
          window.__dtOriginalFillRect=proto.fillRect;
          proto.fillRect=function(...args){
            if(this.canvas?.id==='dt-chart-canvas')window.__dtBarRects.push(args);
            return window.__dtOriginalFillRect.apply(this,args);
          };
          MathStudio.dataTables.plot();
          proto.fillRect=window.__dtOriginalFillRect;
        }""")
        bar_rects = page.evaluate("window.__dtBarRects")
        assert len(bar_rects) >= 3, bar_rects
        assert all(math.isfinite(value) for rect in bar_rects for value in rect), bar_rects

        page.evaluate("""() => {
          MathStudio.dataTables.restoreState({
            version:1,selected:'chart',tables:[{id:'chart',name:'Chart',
              columns:['Category','Value'],rows:[['Overflow','1e308'],['Overflow','1e308']]}]
          });
          document.getElementById('dt-graph-table').value='sheet-1';
          document.getElementById('dt-graph-x').value='0';
          document.getElementById('dt-graph-y').value='1';
          document.getElementById('dt-chart-type').value='pie';
        }""")
        chart_overflow = page.evaluate("""() => {
          try { MathStudio.dataTables.plot(); return 'NO_ERROR'; }
          catch(error) { return error.message; }
        }""")
        assert chart_overflow == 'Category "Overflow" total exceeds finite numeric range.', chart_overflow

        assert not errors, errors
        browser.close()
    print("PASS spreadsheet built-in priority, cancellation-safe SUM/AVERAGE, subnormal residuals, median and true overflow errors")


if __name__ == "__main__":
    main()
