# ClearSkill

ClearSkill is a Claude Code skill for disk cleanup decisions on macOS and
Windows. It scans storage usage, explains what is safe to clean, what needs
manual review, and what should not be touched directly.

## What It Does

- Finds large storage users across home folders, app data, caches, downloads,
  containers, applications, and development caches.
- Classifies cleanup candidates as:
  - `Safe Clean` / `可清理`: rebuildable caches and temporary files.
  - `Review First` / `需确认`: user data or app-managed data.
  - `Do Not Touch` / `别乱动`: apps, system data, databases, and risky paths.
- Generates a simple HTML report with recommended actions, risk level, and
  copyable commands.
- Optionally serves the report locally with guarded one-click actions for
  allowlisted paths.

## Install For Claude Code

```bash
mkdir -p ~/.claude/skills
cp -R /path/to/ClearSkill ~/.claude/skills/clear-skill
```

Restart Claude Code after installing.

## Manual Run

```bash
cd ~/.claude/skills/clear-skill
python3 scripts/scan.py > /tmp/clearskill_scan.json
```

After an agent turns the scan into `/tmp/clearskill_analysis.json`:

```bash
python3 scripts/build_report.py /tmp/clearskill_analysis.json ~/Desktop/clearskill-report.html
```

For local guarded actions:

```bash
python3 scripts/server.py /tmp/clearskill_analysis.json
```

## Safety

The scan is read-only. Cleanup actions are restricted to paths listed in
`green[].trash_paths`, and the server only accepts local token-authenticated
requests. ClearSkill never clears the Trash automatically.

## Tests

```bash
python3 -m unittest discover -s tests -v
```
