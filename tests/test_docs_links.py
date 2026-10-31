"""Every relative Markdown link in the repository must resolve to an existing file or directory."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\]\(([^)\s]+)\)")
SKIP_DIRS = {".git", "node_modules", "__pycache__"}


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_DIRS.intersection(path.relative_to(ROOT).parts):
            yield path


class DocsLinkTests(unittest.TestCase):
    def test_relative_links_resolve(self):
        broken = []
        checked = 0
        for path in markdown_files():
            for target in LINK.findall(path.read_text(encoding="utf-8")):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                checked += 1
                local = target.split("#", 1)[0]
                if local and not (path.parent / local).resolve().exists():
                    broken.append(f"{path.relative_to(ROOT)} -> {target}")
        self.assertGreater(checked, 50, "link scan found suspiciously few links")
        self.assertEqual(broken, [], "broken Markdown links: " + "; ".join(broken))

    def test_checker_detects_a_missing_target(self):
        # Negative control: the same resolution rule must flag a nonexistent file.
        self.assertFalse((ROOT / "docs" / "NO_SUCH_DOCUMENT_EVER.md").exists())
        sample = "[x](docs/NO_SUCH_DOCUMENT_EVER.md)"
        target = LINK.findall(sample)[0]
        self.assertFalse((ROOT / target).resolve().exists())


if __name__ == "__main__":
    unittest.main()
