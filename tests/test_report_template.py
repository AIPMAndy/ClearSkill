import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


SAMPLE_REPORT = {
    "generated_at": "2026-06-12 18:30:00",
    "scan_seconds": 12.4,
    "system": {
        "os": "macOS 26.5.1",
        "build": "25F80",
        "arch": "Apple Silicon",
        "user": "andy",
        "home": "/Users/andy",
        "filesystem": "APFS",
        "disk_total": "228.3 GB",
        "disk_used": "186.1 GB",
        "disk_free": "42.2 GB",
        "disk_name": "Macintosh HD",
        "disks": [
            {"name": "Macintosh HD", "total": "228.3 GB", "used": "186.1 GB", "free": "42.2 GB"}
        ],
    },
    "top5": [
        {
            "rank": 1,
            "tier": "green",
            "size": "约 2.4 GB",
            "type": "开发缓存",
            "name": "pnpm store",
            "path": "/Users/andy/Library/pnpm",
            "note": "包缓存，可再生",
        }
    ],
    "green": [
        {
            "name": "pnpm 包缓存",
            "path": "/Users/andy/Library/pnpm",
            "size_estimate": "约 2.4 GB",
            "kill_processes": [],
            "why": "pnpm 保存下载过的包以便复用。",
            "delete_effect": "删除后项目下次安装依赖会重新下载包，不会删除项目代码。",
            "recommended_action": "优先移到废纸篓；确认项目依赖安装正常后再清空废纸篓。",
            "risk_level": "低",
            "trash_paths": ["/Users/andy/Library/pnpm"],
            "commands": [{"label": "官方清理", "cmd": "pnpm store prune"}],
        }
    ],
    "yellow": [
        {
            "name": "微信数据",
            "path": "/Users/andy/Library/Containers/com.tencent.xinWeChat",
            "size": "约 3.0 GB",
            "content_profile": "聊天记录、文件缓存和设置。",
            "why_manual": "包含用户数据和数据库文件，无法按文件名可靠判断。",
            "disposal": "打开微信的储存空间管理，在应用内清理缓存和聊天文件。",
            "risk": "手动删除可能损坏聊天记录数据库。",
            "recommended_action": "应用内清理",
            "risk_level": "高",
        }
    ],
    "red": [
        {
            "name": "Xcode.app",
            "path": "/Applications/Xcode.app",
            "size": "约 5.1 GB",
            "why_keep": "应用本体不属于垃圾文件，可能仍被开发工具链使用。",
            "indirect_release": "确认不用后从访达或 App Store 正规卸载。",
            "risk_level": "高",
            "app_paths": ["/Applications/Xcode.app"],
        }
    ],
    "summary": {
        "overview": "优先清理可再生开发缓存，应用数据先审查。",
        "tier_stats": {"green": "约 2.4 GB", "yellow": "约 3.0 GB", "red": "约 5.1 GB"},
        "priority": ["先处理 pnpm 包缓存。"],
        "long_term": ["定期清理包管理器缓存。"],
    },
}


class ReportTemplateTests(unittest.TestCase):
    def build_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "analysis.json"
            out = Path(tmp) / "report.html"
            src.write_text(json.dumps(SAMPLE_REPORT, ensure_ascii=False), encoding="utf-8")
            subprocess.run(
                ["python3", str(ROOT / "scripts" / "build_report.py"), str(src), str(out)],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            return out.read_text(encoding="utf-8")

    def test_report_is_branded_as_clear_skill(self):
        html = self.build_report()

        self.assertIn("<title>ClearSkill", html)
        self.assertIn("<h1>ClearSkill</h1>", html)
        self.assertNotIn("<h1>存储分析报告</h1>", html)

    def test_report_surfaces_cleanup_decision_fields(self):
        html = self.build_report()

        for text in [
            "推荐动作",
            "为什么占空间",
            "删了会怎样",
            "风险",
            "可清理",
            "需确认",
            "别乱动",
            "优先清理可再生开发缓存",
        ]:
            self.assertIn(text, html)


if __name__ == "__main__":
    unittest.main()
