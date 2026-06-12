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
