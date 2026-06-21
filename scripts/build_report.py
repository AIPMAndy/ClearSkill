#!/usr/bin/env python3
"""Inject an analysis JSON into the HTML template -> a standalone report.

Usage:
    build_report.py <analysis.json> [output.html]

The analysis JSON is produced by Claude after interpreting scan.py output.
Schema (all sections optional except system):

{
  "generated_at": "2026-05-28 12:00:00",
  "scan_seconds": 42.1,
  "system": {os, build, arch, user, home, filesystem,
             disk_total, disk_used, disk_free, purgeable},
  "top5": [{rank, tier(green|yellow|red), size, type, name, path, note}],
  "green":  [{
      name, path, size_estimate, why, delete_effect, recommended_action,
      risk_level, kill_processes:[], trash_paths:[...], commands:[{label,cmd}]
  }],
  "yellow": [{
      name, path, size, content_profile, why_manual, disposal, risk,
      recommended_action, risk_level, trash_paths:[...]?, open_note?
  }],
  "red":    [{
      name, path, size, why_keep, indirect_release, recommended_action?,
      risk_level, auto_reclaim?, app_paths:[...]?
  }],
  "denied": ["/path/one", ...],
  "summary": {overview, tier_stats:{green,yellow,red}, priority:[...], long_term:[...]}
}
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "report_template.html")


def main():
    if len(sys.argv) < 2:
        print("用法: build_report.py <analysis.json> [output.html]")
        print("\n将分析结果生成为静态 HTML 报告（不带删除按钮）。")
        print("示例: python3 build_report.py /tmp/clearskill_analysis.json ~/Desktop/report.html")
        sys.exit(1)
    src = sys.argv[1]

    if not os.path.exists(src):
        print(f"❌ 错误: 找不到文件 {src}")
        print("请先运行 scan.py 并生成分析结果。")
        sys.exit(1)

    out = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser(
        "~/Desktop/clearskill-report.html")

    try:
        with open(src, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 错误: JSON 文件格式不正确")
        print(f"详细信息: {e}")
        sys.exit(1)

    with open(TEMPLATE, "r", encoding="utf-8") as f:
        tpl = f.read()

    blob = json.dumps(data, ensure_ascii=False)
    # 静态报告不带删除能力（DELETE=null），删除按钮只在 server.py 服务时出现
    html = tpl.replace("__REPORT_DATA__", blob).replace("__DELETE_CONFIG__", "null")

    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✓ 报告已生成: {out}")
    print(f"  用浏览器打开: open '{out}'")

    # 显示统计信息
    if 'summary' in data and 'tier_stats' in data['summary']:
        ts = data['summary']['tier_stats']
        print(f"\n📊 清理潜力:")
        print(f"  可清理: {ts.get('green', '-')}")
        print(f"  需确认: {ts.get('yellow', '-')}")
        print(f"  别乱动: {ts.get('red', '-')}")



if __name__ == "__main__":
    main()
