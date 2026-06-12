import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ReadmeTests(unittest.TestCase):
    def test_readme_is_bilingual_and_actionable(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")

        for phrase in [
            "## 中文版",
            "## English",
            "安装到 Claude Code",
            "Install for Claude Code",
            "使用方式",
            "Usage",
            "安全边界",
            "Safety boundaries",
            "cp -R",
            "python3 scripts/scan.py",
            "python3 scripts/server.py",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
