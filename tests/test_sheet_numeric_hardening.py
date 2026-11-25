"""Guard spreadsheet numeric hardening and bundled/source parity."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "src/data-tables.js").read_text(encoding="utf-8")
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/quality.yml").read_text(encoding="utf-8")


class SpreadsheetNumericHardeningTests(unittest.TestCase):
    def test_reserved_names_cannot_shadow_builtin_aggregates(self):
        self.assertIn("SUM|AVERAGE|AVG|MIN|MAX|COUNT|MEDIAN", SOURCE)
        self.assertIn("test(name)?null:window.MathStudio.customFunctions?.find(name)", SOURCE)

    def test_overflow_is_an_error_and_average_is_scaled(self):
        self.assertIn("function stableMean(values)", SOURCE)
        self.assertIn("const normalized=value/scale;", SOURCE)
        self.assertIn("if(normalized===0&&value!==0)addCompensated(residual,value);", SOURCE)
        self.assertIn("x=nums.length?stableMean(nums):0;", SOURCE)
        self.assertNotIn("nums.reduce((a,b)=>a+b/nums.length,0)", SOURCE)
        self.assertIn("if(!Number.isFinite(x))throw Error('#NUM!')", SOURCE)
        self.assertNotIn("String(Number.isFinite(x)?x:0)", SOURCE)
        self.assertIn("catch(error){throw Error(error?.message?.startsWith('#')?error.message:'#VALUE');}", SOURCE)

    def test_sum_uses_scaled_compensated_accumulation(self):
        self.assertIn("function stableSum(values)", SOURCE)
        self.assertIn("if(normalized===0&&value!==0)addCompensated(residual,value);", SOURCE)
        self.assertIn("x=stableSum(nums);", SOURCE)
        self.assertNotIn("x=nums.reduce((a,b)=>a+b,0);", SOURCE)
        self.assertIn("if(!Number.isFinite(x))throw Error('#NUM!')", SOURCE)

    def test_categorical_charts_use_scaled_totals_and_finite_geometry(self):
        self.assertIn("const total=stableSum(values);", SOURCE)
        self.assertIn("const otherTotal=stableSum(entries.slice(23).map(entry=>entry[1]));", SOURCE)
        self.assertIn("const scale=Math.max(0,...entries.map(entry=>Math.abs(entry[1])));", SOURCE)
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
