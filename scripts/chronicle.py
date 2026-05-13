#!/usr/bin/env python3
"""
Chronicle — a monthly auto-generated history of the IQRA marketplace.

Aggregates structural stats from skills.json, the personas registry,
and the recent git log, and writes a single markdown document
(`CHRONICLE.md`) that can be committed back to a long-lived branch
or kept on main as a self-updating sirah of the system.

This script reads only; the calling workflow is responsible for
committing the output. It deliberately avoids any external service
calls or paid analytics: every input lives in the repo.

Sections produced:

  1. Header (month, generation timestamp, commit pin).
  2. Skill counts per tier and grand totals.
  3. Personas summary.
  4. Recent activity: last 20 commits to skills/ and personas/.
  5. Notable additions in the last 30 days.

Run with no arguments; writes to CHRONICLE.md at the repo root.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = ROOT / "skills.json"
PERSONAS_JSON = ROOT / "personas.json"
CHRONICLE = ROOT / "CHRONICLE.md"
SKILLS_DIR = ROOT / "skills"


def _git(*args: str) -> str:
    try:
        out = subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)
    except subprocess.CalledProcessError:
        return ""
    return out.strip()


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _tier_breakdown(skills: list[dict]) -> Counter:
    counter: Counter = Counter()
    for entry in skills:
        tier = entry.get("tier") or "UNCLASSIFIED"
        counter[tier] += 1
    return counter


def _recent_commits(paths: list[str], limit: int = 20) -> list[str]:
    fmt = "- `%h` %ad — %s"
    args = [
        "log",
        f"-n{limit}",
        f"--pretty=format:{fmt}",
        "--date=short",
        "--",
        *paths,
    ]
    out = _git(*args)
    return out.splitlines() if out else []


def _new_skills_last_30d() -> list[str]:
    # Use --diff-filter=A on the skills/ tree to find files added in the
    # last 30 days. Falls back to empty list if the history is shallow.
    out = _git(
        "log",
        "--since=30 days ago",
        "--diff-filter=A",
        "--name-only",
        "--pretty=format:",
        "--",
        "skills/",
    )
    added = sorted({line.strip() for line in out.splitlines() if line.strip().endswith(".md")})
    return added


def _render() -> str:
    now = datetime.now(timezone.utc)
    head = _git("rev-parse", "--short", "HEAD") or "unknown"
    skills_data = _load_json(SKILLS_JSON)
    personas_data = _load_json(PERSONAS_JSON)

    skills = skills_data.get("skills", [])
    personas = personas_data.get("personas", []) if isinstance(personas_data, dict) else []

    tiers = _tier_breakdown(skills)
    md_on_disk = sorted(p.name for p in SKILLS_DIR.glob("*.md")) if SKILLS_DIR.exists() else []
    recent = _recent_commits(["skills/", "personas/", "skills.json", "personas.json"])
    new_30d = _new_skills_last_30d()

    lines: list[str] = []
    lines.append("# IQRA Marketplace Chronicle")
    lines.append("")
    lines.append(
        f"_Generated {now.strftime('%Y-%m-%d %H:%M UTC')} from `{head}`._ "
        "This file is auto-written by `.github/workflows/chronicle.yml` on a "
        "monthly cadence. Do not hand-edit; changes will be overwritten."
    )
    lines.append("")

    lines.append("## Skill Registry")
    lines.append("")
    lines.append(f"- Skills in manifest: **{len(skills)}**")
    lines.append(f"- Markdown files on disk: **{len(md_on_disk)}**")
    lines.append(f"- Personas registered: **{len(personas)}**")
    lines.append("")
    lines.append("### By tier")
    lines.append("")
    lines.append("| Tier | Count |")
    lines.append("| --- | ---: |")
    for tier in sorted(tiers, key=lambda t: (-tiers[t], t)):
        lines.append(f"| {tier} | {tiers[tier]} |")
    lines.append("")

    lines.append("## Recent activity")
    lines.append("")
    if recent:
        lines.extend(recent)
    else:
        lines.append("- _No recent commits touching skills/ or personas/ in this window._")
    lines.append("")

    lines.append("## New skills in the last 30 days")
    lines.append("")
    if new_30d:
        for path in new_30d:
            lines.append(f"- `{path}`")
    else:
        lines.append("- _None._")
    lines.append("")

    lines.append("---")
    lines.append(
        "_The Chronicle is a deliberately minimal record. It does not_ "
        "_replace the README dashboard; it is a slower, narrative cadence_ "
        "_intended to be readable on its own a year from now._"
    )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    content = _render()
    CHRONICLE.write_text(content, encoding="utf-8")
    print(f"Chronicle: wrote {CHRONICLE.relative_to(ROOT)} ({len(content)} bytes)")
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        try:
            with open(gh_output, "a", encoding="utf-8") as fh:
                fh.write(f"bytes={len(content)}\n")
        except OSError:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
