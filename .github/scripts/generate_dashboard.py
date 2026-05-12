#!/usr/bin/env python3
"""IQRA Agentic Marketplace — Live Dashboard Generator

Generates a dynamic metrics section for README.md by crawling:
- skills.json registry (counts, tiers)
- test results (pytest --json)
- git log (recent commits)
- Go engine build status
- TS runtime build status

Outputs to stdout; the GitHub workflow captures it and injects into README.
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
SKILLS_JSON = ROOT / "skills.json"
README = ROOT / "README.md"
GO_ENGINE = ROOT / "go-engine"
TS_RUNTIME = ROOT / "aix-constitutional-runtime"


def load_skills():
    if not SKILLS_JSON.exists():
        return []
    with open(SKILLS_JSON) as f:
        data = json.load(f)
    return data.get("skills", [])


def tier_from_skill_file(skill_name: str) -> str | None:
    """Read the skill markdown and extract its TIER header."""
    path = ROOT / "skills" / f"{skill_name}.md"
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"TIER:\s*(\S+)", content)
    return m.group(1) if m else None


def categorize_skills(skills: list[dict]) -> dict[str, list[str]]:
    tiers: dict[str, list[str]] = {}
    for s in skills:
        name = s["name"]
        tier = tier_from_skill_file(name) or "UNCLASSIFIED"
        tiers.setdefault(tier, []).append(name)
    return tiers


def git_log(count=5):
    try:
        res = subprocess.run(
            ["git", "log", f"--max-count={count}", "--pretty=format:%h|%s|%ar|%an"],
            capture_output=True, text=True, cwd=ROOT, timeout=15,
        )
        commits = []
        for line in res.stdout.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({"hash": parts[0], "msg": parts[1], "ago": parts[2], "author": parts[3]})
        return commits
    except Exception:
        return []


def _run(cmd, cwd=None, timeout=30):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, timeout=timeout)
        return res.returncode, res.stdout, res.stderr
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT", ""
    except FileNotFoundError:
        return -2, "", "NOT_FOUND"
    except Exception as e:
        return -3, "", str(e)


def build_status_go():
    rc, *_ = _run(["go", "build", "./..."], cwd=GO_ENGINE, timeout=30)
    return {0: "✅ Pass", -2: "⚠️  Go not installed", -1: "⏳ Timeout"}.get(rc, "❌ Fail")


def build_status_ts():
    rc, *_ = _run(["npx", "tsc", "--noEmit"], cwd=TS_RUNTIME, timeout=30)
    return {0: "✅ Pass", -2: "⚠️  Node/npx not installed", -1: "⏳ Timeout"}.get(rc, "❌ Fail")


def test_status_py():
    rc, stdout, _ = _run([sys.executable, "-m", "pytest", "tests/", "--tb=short", "-q"], cwd=ROOT, timeout=60)
    last = (stdout or "").strip().split("\n")[-1] if stdout else ""
    if rc == -2:
        return "⚠️  pytest not installed", ""
    if rc == -1:
        return "⏳ Timeout", ""
    return ("✅ Pass" if rc == 0 else "❌ Fail"), last


def test_status_ts():
    rc, stdout, _ = _run(["npx", "tsx", "--test", "tests/e2e.test.ts"], cwd=TS_RUNTIME, timeout=60)
    summary = ""
    if stdout:
        for line in stdout.split("\n"):
            if "tests" in line and ("pass" in line or "fail" in line):
                summary = line.strip()
                break
    if rc == -2:
        return "⚠️  npx/tsx not installed", ""
    if rc == -1:
        return "⏳ Timeout", ""
    return ("✅ Pass" if rc == 0 else "❌ Fail"), summary


def shield(label, message, colour):
    """Return a shields.io badge URL."""
    colour_map = {"green": "success", "red": "critical", "yellow": "yellow",
                  "blue": "blue", "gold": "gold", "purple": "blueviolet"}
    c = colour_map.get(colour, colour)
    return f"https://img.shields.io/badge/{label}-{message}-{c}?style=flat-square"


def tier_emoji(tier: str) -> str:
    return {
        "SOVEREIGN": "👑",
        "ADVANCED_INFRASTRUCTURE": "⚙️",
        "PRO": "🔧",
        "ADVANCED_TOOL": "🛠️",
        "BASIC_TOOL": "🔨",
    }.get(tier, "📦")


def generate_dashboard():
    skills = load_skills()
    by_tier = categorize_skills(skills)
    total = len(skills)
    unique_tiers = len(by_tier)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    commits = git_log(5)

    go_status = build_status_go()
    ts_status = build_status_ts()
    py_test_status, py_test_summary = test_status_py()
    ts_test_status, ts_test_summary = test_status_ts()

    lines = []
    lines.append("")
    lines.append("<!-- DASHBOARD_START -->")
    lines.append("<div align='center'>")
    lines.append("")
    lines.append("## 📊 Live Ecosystem Dashboard")
    lines.append("")
    lines.append(f"_Last updated: {now}_")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### 🏗️ Repository Health")
    lines.append("")
    lines.append("| Component | Type | Status |")
    lines.append("|---|---|---|")
    lines.append(f"| 🐍 Python Tests | `pytest` | {py_test_status} |")
    lines.append(f"| 🟦 TypeScript Runtime | `tsc --noEmit` | {ts_status} |")
    lines.append(f"| 🟦 TS E2E Tests | `node --test` | {ts_test_status} |")
    lines.append(f"| 🔷 Go Engine | `go build` | {go_status} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(f"### 🧩 Skill Registry — {total} Total Skills across {unique_tiers} Tiers")
    lines.append("")
    lines.append("| Tier | Count | Skills |")
    lines.append("|---|---|---|")
    tier_order = ["SOVEREIGN", "ADVANCED_INFRASTRUCTURE", "PRO", "ADVANCED_TOOL", "BASIC_TOOL"]
    for t in tier_order:
        if t in by_tier:
            names = ", ".join(f"`{n}`" for n in by_tier[t])
            emoji = tier_emoji(t)
            display_tier = t.replace("_", " ").title()
            lines.append(f"| {emoji} {display_tier} | {len(by_tier[t])} | {names} |")
    for t in sorted(by_tier):
        if t not in tier_order:
            names = ", ".join(f"`{n}`" for n in by_tier[t])
            lines.append(f"| 📦 {t} | {len(by_tier[t])} | {names} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("### 🔄 Recent Activity")
    lines.append("")
    lines.append("| Commit | Message | Author |")
    lines.append("|---|---|---|")
    for c in commits:
        lines.append(f"| [`{c['hash']}`](https://github.com/Moeabdelaziz007/aix-agent-skills/commit/{c['hash']}) | {c['msg']} | {c['author']} |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("<sub>🤖 Dashboard auto-generated by `.github/workflows/dashboard.yml`</sub>")
    lines.append("")
    lines.append("</div>")
    lines.append("<!-- DASHBOARD_END -->")
    lines.append("")

    return "\n".join(lines)


def inject_dashboard(readme_path: Path, dashboard: str) -> str:
    content = readme_path.read_text(encoding="utf-8", errors="replace")
    pattern = r"<!-- DASHBOARD_START -->.*?<!-- DASHBOARD_END -->"
    if re.search(pattern, content, re.DOTALL):
        return re.sub(pattern, dashboard.strip(), content, flags=re.DOTALL)
    else:
        return content + "\n" + dashboard


def main():
    dashboard = generate_dashboard()
    updated = inject_dashboard(README, dashboard)
    README.write_text(updated, encoding="utf-8")
    print("✅ Dashboard injected into README.md")


if __name__ == "__main__":
    main()
