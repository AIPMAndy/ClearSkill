# ClearSkill

ClearSkill 是一个 Claude Code Skill，用来把“磁盘占用分析”变成清晰的“清理决策”。它不只告诉你哪个目录大，还会说明：为什么占空间、删了会怎样、推荐怎么处理、风险有多高。

ClearSkill is a Claude Code skill that turns disk usage analysis into practical cleanup decisions. It explains what is safe to clean, what needs review, and what should not be touched directly.

---

## 中文版

### 它解决什么问题

电脑空间不够时，普通磁盘工具通常只会告诉你“哪里大”。真正难的是判断：

- 这是缓存，还是用户数据？
- 删了会不会丢聊天记录、登录状态、项目文件？
- 应该直接删、移到废纸篓，还是去 App 里清？
- 哪些东西看起来大，但其实别手动碰？

ClearSkill 会把扫描结果分成三类：

| 分类 | 含义 | 典型动作 |
|---|---|---|
| `Safe Clean` / `可清理` | 可再生缓存、临时文件、安装包缓存、构建产物 | 可移到废纸篓；服务模式下可直接删除 |
| `Review First` / `需确认` | 桌面、下载、聊天记录、浏览器 Profile、App 数据 | 先打开目录或到 App 内清理 |
| `Do Not Touch` / `别乱动` | App 本体、系统数据、数据库、风险未知的大目录 | 只给正规卸载或应用内处理建议 |

每个清理项都会给出：

- 为什么占空间
- 删了会怎样
- 推荐动作
- 风险等级
- 可释放估算

### 安装到 Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R /path/to/ClearSkill ~/.claude/skills/clear-skill
```

安装后重启 Claude Code，让它重新加载技能列表。

### 使用方式

在 Claude Code 中直接说类似：

```text
帮我分析一下电脑哪些东西占空间，哪些可以清理
```

或者手动运行扫描：

```bash
cd ~/.claude/skills/clear-skill
python3 scripts/scan.py > /tmp/clearskill_scan.json
```

**减少权限弹窗**：如果你不想反复点击 macOS 权限提示，使用快速模式：

```bash
python3 scripts/scan.py --skip-protected > /tmp/clearskill_scan.json
```

快速模式会跳过 `Containers` 和 `Group Containers` 目录（这些通常会触发"Paseo 想访问其他 App 数据"的弹窗）。这样扫描更快，不会弹窗，但会漏掉部分应用数据（如微信、飞书的缓存）。

Agent 根据扫描结果生成 `/tmp/clearskill_analysis.json` 后，可以生成静态报告：

```bash
python3 scripts/build_report.py /tmp/clearskill_analysis.json ~/Desktop/clearskill-report.html
```

如果需要网页按钮处理白名单内路径，可以启动本地服务：

```bash
python3 scripts/server.py /tmp/clearskill_analysis.json
```

### 报告长什么样

报告首页按这个顺序组织：

1. 当前可用空间和可清理估算
2. 建议先做什么
3. 三组决策卡片：`可清理`、`需确认`、`别乱动`
4. 占用排行
5. 长期优化建议

界面刻意保持简单：优先显示推荐动作和风险，技术路径和命令折叠在详情里。

### 安全边界

ClearSkill 的扫描阶段是只读的。它只会读取大小和元数据，不会修改文件。

清理动作有额外护栏：

- 只允许处理 `green[].trash_paths` 白名单内路径。
- `Review First` 默认只能打开目录，除非有明确安全子路径。
- `Do Not Touch` 不提供删除按钮，只提供应用内清理或正规卸载建议。
- 本地服务只绑定 `127.0.0.1`，并使用一次性 token。
- ClearSkill 永远不会自动清空废纸篓。

### 测试

```bash
python3 -m unittest discover -s tests -v
```

### 常见问题

**Q: 扫描需要多久？**  
A: 通常 10-30 秒。大容量磁盘或大量文件时可能需要 1-2 分钟。扫描时会在终端显示进度。

**Q: 扫描会修改文件吗？**  
A: 不会。扫描阶段是只读的，只收集大小和元数据。只有在报告中主动点击"移到废纸篓"或"直接删除"按钮才会修改文件。

**Q: 为什么有些目录显示"权限不足"？**  
A: macOS 的系统保护机制会限制访问某些目录（如其他用户的文件、系统敏感路径）。这些目录会在报告末尾的"权限不足"列表中说明。

**Q: 扫描时一直弹"Paseo 想访问其他 App 的数据"怎么办？**  
A: 有两个解决方案：
1. **一次性授权（推荐）**：打开"系统设置" → "隐私与安全性" → "完全磁盘访问权限"，勾选 `Paseo` 或 `Claude Code`，然后重启 Claude Code。以后就不会再弹窗了。
2. **使用快速模式**：运行 `python3 scripts/scan.py --skip-protected`，会跳过受保护的应用容器目录，不会触发权限弹窗，但会漏掉部分应用数据。

**Q: "可清理"的东西真的安全吗？**  
A: 绿灯项目都是可再生的缓存和临时文件（如包管理器缓存、构建产物）。删除后工具会在需要时重新下载或生成，不会影响项目代码和用户数据。但仍建议先移到废纸篓，确认无问题后再清空。

**Q: 聊天记录、浏览器数据会被误删吗？**  
A: 不会。这些都被分类为"需确认"（黄灯），报告会建议在应用内清理或手动审查，不会提供直接删除按钮。

**Q: 可以定期自动运行吗？**  
A: 可以。在 Claude Code 中可以让 Claude 定期提醒你运行，或者自己设置 cron job。但删除动作始终需要人工确认。

**Q: 报告可以分享给别人吗？**  
A: 静态报告（`build_report.py` 生成的 HTML）可以。但注意报告中包含你的用户名和完整路径。服务器模式（`server.py`）的报告只能本地访问。

---

## English

### What It Solves

When your disk is full, most storage tools only show which folders are large.
The hard part is deciding what can actually be cleaned without losing data.

ClearSkill classifies cleanup candidates into three decision groups:

| Class | Meaning | Typical action |
|---|---|---|
| `Safe Clean` | Rebuildable caches, temporary files, installer caches, build outputs | Move to Trash; direct delete is available in guarded server mode |
| `Review First` | User data, downloads, chat/media, browser profiles, app-managed data | Review in Finder/Explorer or clean inside the app |
| `Do Not Touch` | App bundles, system data, live databases, risky unknown paths | Use app-native cleanup or official uninstall flows |

Each item explains:

- why it takes space
- what happens if it is removed
- the recommended action
- risk level
- estimated reclaimable space

### Install for Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R /path/to/ClearSkill ~/.claude/skills/clear-skill
```

Restart Claude Code after installation so the new skill is discovered.

### Usage

Ask Claude Code something like:

```text
Analyze my computer storage and tell me what is safe to clean.
```

Or run the scan manually:

```bash
cd ~/.claude/skills/clear-skill
python3 scripts/scan.py > /tmp/clearskill_scan.json
```

After an agent converts the scan into `/tmp/clearskill_analysis.json`, build a
static report:

```bash
python3 scripts/build_report.py /tmp/clearskill_analysis.json ~/Desktop/clearskill-report.html
```

For guarded local action buttons:

```bash
python3 scripts/server.py /tmp/clearskill_analysis.json
```

### Report Layout

The report is organized for action:

1. Current free space and safe-clean estimate
2. What to do first
3. Decision cards: `可清理`, `需确认`, `别乱动`
4. Top usage table
5. Long-term cleanup habits

The UI is intentionally plain: recommended actions and risk are visible first;
technical paths and commands stay folded until needed.

### Safety boundaries

The scan phase is read-only. It reads sizes and metadata only.

Cleanup actions are guarded:

- Only paths listed in `green[].trash_paths` can be deleted directly.
- `Review First` items only open folders unless a verified safe subpath exists.
- `Do Not Touch` items never receive delete buttons.
- The local server binds to `127.0.0.1` and uses a one-time token.
- ClearSkill never empties the Trash automatically.

### Tests

```bash
python3 -m unittest discover -s tests -v
```
