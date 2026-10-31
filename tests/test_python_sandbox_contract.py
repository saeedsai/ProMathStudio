"""Structural contract for user-Python isolation: Worker-only, bounded, pinned, no page access, no JS eval."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")


def strip_js_comments(text):
    """Remove /* */ blocks and whitespace-led // comments (URLs like https:// are kept)."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"(?m)(^|\s)//[^\n]*", r"\1", text)


def template_literal(name):
    match = re.search(r"const " + name + r"=`(.*?)`;", HTML, re.S)
    assert match, name + " not found"
    return match.group(1)


class PythonSandboxContractTests(unittest.TestCase):
    def test_custom_python_runs_only_in_a_terminable_worker_with_timeout(self):
        self.assertIn("new Worker(customPyUrl)", HTML)
        self.assertIn("customPyWorker.terminate()", HTML)
        self.assertIn("setTimeout(()=>finish(Error('Python timed out (60 seconds).')),60000)", HTML)
        self.assertIn("URL.revokeObjectURL(customPyUrl)", HTML)

    def test_worker_source_cannot_touch_the_page_or_network(self):
        for name in ("customPySource",):
            source = template_literal(name)
            for forbidden in ("document", "window", "localStorage", "sessionStorage",
                              "XMLHttpRequest", "fetch(", "indexedDB", "WebSocket", "eval("):
                self.assertNotIn(forbidden, source, name + " must not reference " + forbidden)

    def test_user_code_gets_a_minimal_namespace_and_numeric_only_results(self):
        source = template_literal("customPySource")
        self.assertIn('namespace={"math":math}', source)
        self.assertIn("finite real number", source)
        self.assertIn("math.isfinite(value)", source)
        self.assertIn("isinstance(value,bool)", source)
        # The main thread re-validates the worker reply instead of trusting it.
        self.assertIn("typeof data.value!=='number'||!Number.isFinite(data.value)", HTML)

    def test_pyodide_is_pinned_to_one_vetted_version_everywhere(self):
        urls = set(re.findall(r"https://cdn\.jsdelivr\.net/pyodide/(v[0-9.]+)/full/", HTML))
        self.assertEqual(urls, {"v0.29.1"}, "all Pyodide loads must share one pinned version")
        # No unpinned or foreign script hosts for the Python runtime.
        self.assertNotIn("pyodide/latest", HTML)
        self.assertNotIn("cdn.jsdelivr.net/pyodide/dev", HTML)

    def test_no_javascript_eval_of_user_math_or_code(self):
        sources = [HTML] + [p.read_text(encoding="utf-8") for p in (ROOT / "src").glob("*.js")]
        for text in map(strip_js_comments, sources):
            self.assertIsNone(re.search(r"(?<![\w.])eval\s*\(", text), "direct eval() is forbidden")
            self.assertIsNone(re.search(r"\bnew\s+Function\s*\(", text), "new Function() is forbidden")

    def test_comment_stripper_removes_comments_but_not_code(self):
        sample = "// no eval() here\nconst u='https://cdn.example/x';\n/* eval( */ run(eval('1'));"
        stripped = strip_js_comments(sample)
        self.assertIn("https://cdn.example/x", stripped)
        self.assertEqual(len(re.findall(r"(?<![\w.])eval\s*\(", stripped)), 1)

    def test_negative_control_detects_a_forbidden_pattern(self):
        self.assertIsNotNone(re.search(r"(?<![\w.])eval\s*\(", "x = eval('1+1')"))
        self.assertIsNone(re.search(r"(?<![\w.])eval\s*\(", "evaluate(expr)"))


if __name__ == "__main__":
    unittest.main()
