import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillMetadataTests(unittest.TestCase):
    def test_skill_is_named_clear_skill(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("name: clear-skill", text)
        self.assertIn("# ClearSkill", text)

    def test_skill_requires_explicit_cleanup_decision_fields(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")

        for phrase in [
            "为什么占空间",
            "删了会怎样",
            "推荐动作",
            "风险等级",
            "Safe Clean",
            "Review First",
            "Do Not Touch",
        ]:
            self.assertRegex(text, re.escape(phrase))


if __name__ == "__main__":
    unittest.main()
