"""Guard spreadsheet numeric hardening and bundled/source parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class SpreadsheetNumericHardeningTests(unittest.TestCase):
    def test_cell_numeric_coercion_is_decimal_only(self):
        self.assertIn("const DECIMAL_CELL_NUMBER=", SOURCE)
        self.assertIn("const numericCellValue=v=>", SOURCE)
        self.assertIn("numericCellValue(v)", SOURCE)
        self.assertIn("numeric=numericCellValue(v)", SOURCE)
        smoke = (ROOT / "tests/smoke_sheet_numeric_hardening.py").read_text(encoding="utf-8")
        for literal in ("0x10", "0b10", "0o10", "2.5e+1", "MEDIAN(A1:G1)"):
            self.assertIn(literal, smoke)
        self.assertIn("python tests/smoke_sheet_numeric_hardening.py", WORKFLOW)

    def test_reserved_names_cannot_shadow_builtin_aggregates(self):
        self.assertIn("SUM|AVERAGE|AVG|MIN|MAX|COUNT|MEDIAN|PRODUCT", SOURCE)
        self.assertIn("test(name)?null:window.MathStudio.customFunctions?.find(name)", SOURCE)

    def test_product_uses_exponent_scaled_binary64_multiplication(self):
        self.assertIn("function stableProduct(values)", SOURCE)
        self.assertIn("x=stableProduct(nums);", SOURCE)
        self.assertIn("Object.is(value,-0)", SOURCE)
        self.assertIn("Multiply numeric cells with scale-safe binary64 arithmetic.", SOURCE)
        smoke = (ROOT / "tests/smoke_data_tables.py").read_text(encoding="utf-8")
        for formula in (
            "=PRODUCT(A1:E1)", "=PRODUCT(2,3,4)",
            "=PRODUCT(SUM(A1:B1),2)",
            "=PRODUCT(1e308,1e308,1e-308,1e-308)",
            "=PRODUCT(1e308,1e308)", "=PRODUCT(0,1e308,1e308)",
            "=PRODUCT(A3:A3)", "=PRODUCT(-0,2)",
        ):
            self.assertIn(formula, smoke)
        self.assertIn("python tests/smoke_data_tables.py", WORKFLOW)

    def test_mean_prefers_finite_compensated_sum_before_scaled_fallback(self):
        self.assertIn("const finiteSum=stableSum(values);", SOURCE)
        self.assertIn("if(Number.isFinite(finiteSum))return finiteSum/count;", SOURCE)
        smoke = (ROOT / "tests/smoke_sheet_numeric_hardening.py").read_text(encoding="utf-8")
        self.assertIn("AVERAGE(A1:G1)", smoke)
        self.assertIn("AVG(A1:G1)", smoke)
        self.assertIn("AVERAGE(16,25,1)", smoke)

    def test_overflow_is_an_error_and_average_is_scaled(self):
        self.assertIn("function stableMean(values)", SOURCE)
        self.assertIn("const normalized=value/scale;", SOURCE)
        self.assertIn("if(normalized===0&&value!==0)addCompensated(residual,value);", SOURCE)
        self.assertIn("x=nums.length?stableMean(nums):0;", SOURCE)
        self.assertNotIn("nums.reduce((a,b)=>a+b/nums.length,0)", SOURCE)
        self.assertIn("if(!Number.isFinite(x))throw Error('#NUM!')", SOURCE)
        self.assertNotIn("String(Number.isFinite(x)?x:0)", SOURCE)
        self.assertIn("catch(error){throw Error(error?.message?.startsWith('#')?error.message:'#VALUE');}", SOURCE)

    def test_sum_uses_original_unit_compensation_with_scaled_overflow_fallback(self):
        self.assertIn("function stableSum(values)", SOURCE)
        self.assertIn("const direct={sum:0,correction:0};", SOURCE)
        self.assertIn("if(!Number.isFinite(direct.sum+value))", SOURCE)
        self.assertIn("if(Number.isFinite(total))return total;", SOURCE)
        self.assertIn("const normalized=value/scale;", SOURCE)
        smoke = (ROOT / "tests/smoke_sheet_numeric_hardening.py").read_text(encoding="utf-8")
        self.assertIn("SUM(-7.847929071398543", smoke)
        self.assertIn("AVERAGE(-7.847929071398543", smoke)
        self.assertIn("SUM(1e308,1e308,-1e308)", smoke)
        self.assertIn("if(normalized===0&&value!==0)addCompensated(residual,value);", SOURCE)
        self.assertIn("x=stableSum(nums);", SOURCE)
        self.assertNotIn("x=nums.reduce((a,b)=>a+b,0);", SOURCE)
        self.assertIn("if(!Number.isFinite(x))throw Error('#NUM!')", SOURCE)

    def test_min_max_iterate_large_aggregates_without_argument_spread(self):
        self.assertIn("for(let i=1;i<nums.length;i++)", SOURCE)
        self.assertIn("Math.min(x,nums[i]):Math.max(x,nums[i])", SOURCE)
        self.assertNotIn("Math.min(...nums)", SOURCE)
        self.assertNotIn("Math.max(...nums)", SOURCE)
        smoke = (ROOT / "tests/smoke_sheet_numeric_hardening.py").read_text(encoding="utf-8")
        self.assertIn("['A1:A6000'] * 22", smoke)
        self.assertIn("formula(f'MIN({repeated_ranges})') == 1", smoke)
        self.assertIn("formula(f'MAX({repeated_ranges})') == 6000", smoke)

    def test_categorical_charts_use_scaled_totals_and_finite_geometry(self):
        self.assertIn("const total=stableSum(values);", SOURCE)
        self.assertIn("const otherTotal=stableSum(entries.slice(23).map(entry=>entry[1]));", SOURCE)
        self.assertIn("scale=Math.max(0,...entries.map(entry=>Math.abs(entry[1])));", SOURCE)
        self.assertIn("const weights=positive.map(entry=>entry[1]/scale),total=stableSum(weights);", SOURCE)
        self.assertIn("const y=100+(hi-normalizedValue)/span*(h-195);", SOURCE)
        self.assertIn("total exceeds finite numeric range.", SOURCE)
        self.assertIn("python tests/smoke_sheet_numeric_hardening.py", WORKFLOW)

    def test_even_median_uses_range_safe_midpoint(self):
        self.assertIn("function safeMidpoint(a,b)", SOURCE)
        self.assertIn("safeMidpoint(ordered[mid-1],ordered[mid])", SOURCE)
        self.assertIn("Math.max(-scale,Math.min(scale,midpoint))", SOURCE)

    def test_custom_arguments_are_bound_as_numbers_not_reparsed(self):
        self.assertIn("const env=Object.fromEntries(fn.params.map((key,i)=>[key,C(args[i])]))", HTML)
        self.assertIn("return numeric(parseRaw(fn.expression),env).re", HTML)
        self.assertNotIn("const expression=name+'('+args.map(v=>String(v))", HTML)

    def test_standalone_parity_and_browser_gate(self):
        start = HTML.index("/* ProMathStudio Data Tables workspace.")
        end = HTML.index("</script>", start)
        self.assertEqual(HTML[start:end], SOURCE)
        self.assertIn("python tests/smoke_sheet_numeric_hardening.py", WORKFLOW)


if __name__ == "__main__":
    unittest.main()
