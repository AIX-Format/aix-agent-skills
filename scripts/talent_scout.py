#!/usr/bin/env python3
"""
Talent Scout: maintain a self-updating CONTRIBUTORS.md from git
history.

Reads `git log` once, tallies per-author commits and lines changed,
and rebuilds `CONTRIBUTORS.md` deterministically. Re-running on the
same git state produces the same file (byte-identical sort key on
ties: commit count desc, then alphabetical login). The workflow
commits the result only when it actually changes.

Bots and obviously machine-generated identities (anything with
`[bot]` in the name or in @users.noreply addresses on a known bot
domain) are listed in a separate trailing table so the contributor
ranking reads as humans-first.

Zero external dependencies. Pure git + stdlib.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "CONTRIBUTORS.md"

# Identities we always treat as bots in the output split.
# Match anything that ends in `-bot` (case-insensitive) or carries the
# canonical `[bot]` suffix that GitHub applies to App actors. The name
# check covers `iqra-*-bot` identities that use human-looking emails.
BOT_NAME_RE = re.compile(r"(?:\[bot\]|-bot)\s*$", re.IGNORECASE)
BOT_EMAILS = (
    "actions@github.com",
    "noreply@github.com",
    "github-actions",
    "coderabbit",
    "codesmith-bot",
    "iqra-sentinel-bot",
    "iqra-dashboard-bot",
    "iqra-marketplace-bot",
    "dependabot",
    "@iqra.sovereign",
)


def _git(*args: str) -> str:
    """
    Run a git subcommand and return stdout. Raises RuntimeError on
    non-zero exit so callers cannot silently produce an empty or
    inaccurate CONTRIBUTORS.md from a broken git invocation.
    """
    cp = subprocess.run(
        ["git", "-C", str(ROOT), *args],
        text=True,
        capture_output=True,
        check=False,
    )
    if cp.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {cp.stderr.strip()}")
    return cp.stdout


def _normalize_identity(name: str) -> str:
    """
    Canonical form of a git author display name for grouping.

    Applies NFKC normalisation so visually identical glyphs collapse
    onto the same string, then strips Unicode format characters
    (category Cf, e.g. U+202C `POP DIRECTIONAL FORMATTING`,
    U+200B `ZERO WIDTH SPACE`). Without this two commits from the
    same person with a stray invisible char produce two rows in the
    contributor table.
    """
    normalized = unicodedata.normalize("NFKC", name)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Cf").strip()


def _is_bot(name: str, email: str) -> bool:
    if BOT_NAME_RE.search(name):
        return True
    e = email.lower()
    return any(snippet in e for snippet in BOT_EMAILS)


def _collect() -> tuple[dict, dict]:
    """
    Walk `git log --shortstat` and accumulate per-identity stats.
    Returns (humans, bots) where each maps identity -> dict.
    """
    raw = _git(
        "log",
        "--no-merges",
        "--pretty=format:COMMIT%x09%an%x09%ae%x09%ad",
        "--date=short",
        "--shortstat",
    )
    humans: dict[str, dict] = defaultdict(lambda: {"commits": 0, "added": 0, "removed": 0, "first": "", "last": ""})
    bots: dict[str, dict] = defaultdict(lambda: {"commits": 0, "added": 0, "removed": 0, "first": "", "last": ""})

    current_name: str | None = None
    current_email: str | None = None
    current_date: str | None = None

    for line in raw.splitlines():
        if line.startswith("COMMIT\t"):
            _, raw_name, email, date = line.split("\t", 3)
            name = _normalize_identity(raw_name)
            current_name = name
            current_email = email
            current_date = date
            bucket = bots if _is_bot(name, email) else humans
            stats = bucket[name]
            stats["commits"] += 1
            if not stats["first"] or date < stats["first"]:
                stats["first"] = date
            if not stats["last"] or date > stats["last"]:
                stats["last"] = date
        elif "file changed" in line or "files changed" in line:
            if current_name is None:
                continue
            bucket = bots if _is_bot(current_name, current_email or "") else humans
            stats = bucket[current_name]
            m_add = re.search(r"(\d+) insertion", line)
            m_del = re.search(r"(\d+) deletion", line)
            if m_add:
                stats["added"] += int(m_add.group(1))
            if m_del:
                stats["removed"] += int(m_del.group(1))
    return humans, bots


def _row(identity: str, stats: dict) -> str:
    return (
        f"| {identity} | {stats['commits']} | {stats['added']} | "
        f"{stats['removed']} | {stats['first']} | {stats['last']} |"
    )


def _render(humans: dict, bots: dict) -> str:
    sort_key = lambda kv: (-kv[1]["commits"], kv[0].lower())
    ordered_humans = sorted(humans.items(), key=sort_key)
    ordered_bots = sorted(bots.items(), key=sort_key)

    out: list[str] = []
    out.append("# Contributors")
    out.append("")
    out.append(
        "Auto-generated from `git log` by `scripts/talent_scout.py`. "
        "Do not hand-edit; changes will be overwritten on the next run. "
        "If a name should be merged or excluded, fix it at the git level "
        "(via `.mailmap` or by amending the relevant commits)."
    )
    out.append("")
    out.append(f"## Humans ({len(ordered_humans)})")
    out.append("")
    if not ordered_humans:
        out.append("_No human contributors recorded yet._")
    else:
        out.append("| Name | Commits | Lines added | Lines removed | First | Latest |")
        out.append("| --- | ---: | ---: | ---: | --- | --- |")
        for name, stats in ordered_humans:
            out.append(_row(name, stats))
    out.append("")
    if ordered_bots:
        out.append(f"## Bots ({len(ordered_bots)})")
        out.append("")
        out.append("| Name | Commits | Lines added | Lines removed | First | Latest |")
        out.append("| --- | ---: | ---: | ---: | --- | --- |")
        for name, stats in ordered_bots:
            out.append(_row(name, stats))
        out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    try:
        humans, bots = _collect()
    except RuntimeError as exc:
        print(f"Talent Scout: {exc}", file=sys.stderr)
        return 1
    body = _render(humans, bots)
    TARGET.write_text(body, encoding="utf-8")
    print(f"Talent Scout: wrote {TARGET.relative_to(ROOT)} ({len(humans)} humans, {len(bots)} bots)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
