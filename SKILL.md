---
name: clear-skill
description: >
  Use when the user wants to analyze or clean disk/storage space on macOS or
  Windows, including "磁盘满了", "清理空间", "哪些东西占地方", "storage cleanup",
  "disk cleanup", "clear cache", or when they ask what can be safely deleted.
  Do not use for RAM/process memory questions.
---

# ClearSkill

ClearSkill turns a disk scan into a cleanup decision list. It does not merely
rank large folders; it explains whether each item is safe waste, user data that
needs review, or something that should not be touched directly.

## Safety Rules

- Scan first, read-only. Use `df`, `du`, `diskutil`, `stat`, `ls`, and metadata
  inspection only until the user explicitly confirms a cleanup action.
- Never clear Trash automatically. Moving to Trash is reversible; emptying Trash
  is a separate user decision.
- Never delete paths outside an allowlist generated from `green[].trash_paths`.
- Keep paths and commands exactly as-is. Do not translate filesystem paths.
- Mark all reclaimable space as estimated.

## Workflow

### Step 1: Scan

```bash
python3 scripts/scan.py > /tmp/clearskill_scan.json
```

The script detects macOS or Windows and outputs:
- `system`: OS, disk totals, filesystem, home directory, and disks.
- `groups`: size-sorted directories from home, app data, caches, downloads,
  applications, containers, and development caches.
- `denied`: directories that could not be read.

### Step 2: Classify With Cleanup Decisions

Read the platform reference first:
- macOS: `references/macos.md`
- Windows: `references/windows.md`

Then inspect `/tmp/clearskill_scan.json`. Do not put every large thing into the
cleanup list. Only list items where a human has a cleanup decision to make.
System files and normal active application data can stay in "system and other".

Use these three decision classes:

| Class | Report label | Meaning | Allowed action |
|---|---|---|---|
| Safe Clean | 可清理 | Rebuildable cache, temporary file, installer cache, generated build output | `trash_paths`; optionally direct delete in server mode |
| Review First | 需确认 | User data, app-managed data, downloads, chat/media, projects, browser profiles | open folder or app instructions; Trash only for verified safe subpaths |
| Do Not Touch | 别乱动 | System files, app bundles, live databases, core app state, risky unknowns | explain safe indirect action only |

For every listed item, write the cleanup decision clearly:

- **为什么占空间**: what this directory stores and why it grew.
- **删了会怎样**: the user-visible effect after removal.
- **推荐动作**: one concrete next action, not generic advice.
- **风险等级**: `低`, `中`, or `高`.
- **可释放估算**: use `size_estimate` for Safe Clean and `size` elsewhere.

Required item fields:

```json
{
  "name": "pnpm 包缓存",
  "path": "/Users/andy/Library/pnpm",
  "size_estimate": "约 2.4 GB",
  "why": "pnpm 保存下载过的包以便复用。",
  "delete_effect": "删除后下次安装依赖会重新下载包，不会删除项目代码。",
  "recommended_action": "先移到废纸篓；确认项目安装依赖正常后再清空废纸篓。",
  "risk_level": "低",
  "trash_paths": ["/Users/andy/Library/pnpm"],
  "commands": [{"label": "官方清理", "cmd": "pnpm store prune"}]
}
```

Compatibility field mapping:
- Safe Clean uses `green[]`; include `why`, `delete_effect`,
  `recommended_action`, `risk_level`, `trash_paths`, and `commands`.
- Review First uses `yellow[]`; include `content_profile`, `why_manual`,
  `disposal`, `risk`, plus `recommended_action` and `risk_level`.
- Do Not Touch uses `red[]`; include `why_keep`, `indirect_release`, plus
  `recommended_action` when useful and `risk_level`.

### Step 3: Generate The Report

Create `/tmp/clearskill_analysis.json`, then choose mode:

```bash
# Static, shareable, no one-click file actions
python3 scripts/build_report.py /tmp/clearskill_analysis.json ~/Desktop/clearskill-report.html

# Interactive local server with guarded actions
python3 scripts/server.py /tmp/clearskill_analysis.json
```

Use the server mode when the user wants buttons for cleanup. It binds to
`127.0.0.1`, generates a per-session token, and only accepts allowlisted paths.

### Step 4: Summarize

In chat, give a short conclusion:
- total Safe Clean estimate
- the first 2-3 actions to take
- the riskiest Review First / Do Not Touch item
- the report path or local URL

## Classification Guide

### Safe Clean / 可清理

Use only when deletion is normally recoverable by regeneration or re-download:
- package caches: npm, pnpm, pip, uv, cargo registry/cache, Homebrew cache
- Playwright/browser binaries used by test tools
- Xcode DerivedData and build products
- updater caches and installer remnants
- temporary files with no user-authored content

If in doubt, downgrade to Review First.

### Review First / 需确认

Use when the bytes may contain user intent or app state:
- `Desktop`, `Downloads`, documents, media, archives
- chat apps such as WeChat, Feishu/Lark, Slack, Discord
- browser profile folders, extension data, cookies, history
- app containers, UUID containers, unknown hidden folders
- project folders with `node_modules`, build outputs mixed with source

Prefer app-native cleanup instructions for app-managed data. Only provide
`trash_paths` for a verified safe subfolder.

### Do Not Touch / 别乱动

Use when manual deletion is likely to break software or hide a better workflow:
- application bundles in `/Applications`
- system directories, APFS snapshots, swap, protected OS data
- live databases and app core state
- unknown large paths that cannot be identified confidently

Give an indirect action: uninstall via Finder/App Store/vendor uninstaller,
clear inside the app, restart, or change app retention settings.

## Report Shape

The report should read in this order:
1. Current disk state and Safe Clean estimate.
2. "Start here" priorities.
3. Three decision groups: 可清理, 需确认, 别乱动.
4. Top usage table for orientation.
5. Long-term habits.

The UI is intentionally simple: plain cards, visible recommended action,
folded technical details, no decorative hero layout, and no dense table as the
first screen.

## Dependencies

All scripts use Python 3 standard library only. macOS includes the required
`du`, `diskutil`, and `osascript` commands. On Windows, use `python` or `py -3`
instead of `python3` if needed.
