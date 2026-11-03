"""Static contract for digital signal filters: bundle parity, placement, API, UI accessibility, safety and CI wiring."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src" / "signal-filters.js"


def embedded(html, tag):
    marker = f'<script id="{tag}">\n'
    start = html.index(marker) + len(marker)
    return html[start:html.index("</script>", start)]


class SignalFilterTests(unittest.TestCase):
    def setUp(self):
        self.src = SOURCE.read_text(encoding="utf-8")
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")

    def test_bundle_matches_source(self):
        self.assertEqual(embedded(self.html, "promath-signal-filters").rstrip("\n"), self.src.rstrip("\n"))

    def test_script_follows_fft_module_and_build_entry(self):
        fft = self.html.index('<script id="promath-fft-tools">\n')
        close = self.html.index("</script>\n", fft) + len("</script>\n")
        self.assertTrue(self.html.startswith('<script id="promath-signal-filters">\n', close))
        build = (ROOT / "scripts" / "build.py").read_text(encoding="utf-8")
        self.assertIn('("promath-fft-tools", "src/fft-tools.js"),\n    ("promath-signal-filters", "src/signal-filters.js"),', build)

    def test_public_api(self):
        self.assertIn("M.signalFilters={convolve,correlate,firwin,movingAverage,butter,sosToBa,lfilter,sosfilt,filtfilt,apply,freqz,design,run,", self.src)
        for mode in ("full", "same", "valid"):
            self.assertIn(f"'{mode}'", self.src)
        for window in ("hamming", "hann", "blackman"):
            self.assertIn(f'<option value="{window}">', self.src)
        self.assertIn("integer(order,1,8,'Butterworth order')", self.src)
        self.assertIn("MAX_TAPS=501", self.src)
        self.assertIn("Math.tan(Math.PI*fc/fs)", self.src)  # bilinear pre-warping
        self.assertIn("M.fftTools.analyze", self.src)  # reuse the existing FFT, no second FFT kernel
        self.assertNotIn("function fft(", self.src)

    def test_ui_accessibility_contract(self):
        self.assertIn("area.id='filters-details'", self.src)
        self.assertIn('<pre id="flt-output" role="status" aria-live="polite">', self.src)
        self.assertRegex(self.src, r'<canvas id="flt-canvas"[^>]*role="img" aria-label="')
        self.assertIn("min-height:40px", self.src)
        self.assertIn("#flt-output.error", self.src)
        self.assertIn("M.dataTables.importData(", self.src)

    def test_no_dynamic_code_network_or_markup_breakers(self):
        for pattern in (r"\beval\s*\(", r"new\s+Function", r"\bfetch\s*\(", r"XMLHttpRequest", r"WebSocket", r"import\s*\("):
            self.assertIsNone(re.search(pattern, self.src), pattern)
        for token in ("<!--", "-->", "<script", "</script"):
            self.assertNotIn(token, self.src.lower())
        self.assertEqual(self.src.count(".innerHTML="), 1)

    def test_workflow_runs_signal_filter_smoke(self):
        workflow = (ROOT / ".github" / "workflows" / "quality.yml").read_text(encoding="utf-8")
        self.assertIn("run: python tests/smoke_signal_filters.py", workflow)
        self.assertIn("python tests/smoke_fft.py", workflow)


if __name__ == "__main__":
    unittest.main()
