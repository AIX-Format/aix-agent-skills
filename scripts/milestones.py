#!/usr/bin/env python3
"""
Numerology Milestones: let the marketplace celebrate its own pulse.

Counts merged PRs touching `main` and emits a milestone markdown
whenever the count crosses one of the sacred multiples (7, 49, 369).
State is persisted in `signals/cycles.json` so each crossing fires
exactly once; the workflow commits the milestone file and updated
state back to main with `[skip ci]`.

Layers:
  - Every 7 PRs → `milestones/7-{n}.md` (small note)
  - Every 49 PRs → `milestones/49-{n}.md` (medium reflection)
  - Every 369 PRs → `milestones/369-{n}.md` (large checkpoint)

The milestones reference the last 7/49/369 commits respectively, so
they are self-documenting time capsules with no human effort. The
script is idempotent: re-running with the same git state and same
state file is a no-op.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "signals"
STATE = SIGNALS / "cycles.json"
MILESTONES = ROOT / "milestones"

TIERS = (
    ("7", 7),
    ("49", 49),
    ("369", 369),
)


def _git(*args: str) -> str:
    """
    Run `git` with the given arguments in the repository root and return the command output.
    
    Parameters:
        *args (str): Arguments to pass to the `git` command (e.g., `"log"`, `"--first-parent"`).
    
    Returns:
        str: The command's stdout with leading/trailing whitespace removed, or an empty string if the git command fails.
    """
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def _count_merges_on_main() -> int:
    """
    Count merge commits on the `main` branch using first-parent history.
    
    Returns:
        int: The number of merge commits found on `main`. Returns 0 if no merges are found or the underlying git command produced no output.
    """
    raw = _git("log", "--first-parent", "--merges", "main", "--pretty=format:%H")
    if not raw:
        return 0
    return len(raw.splitlines())


def _recent_log(n: int) -> list[str]:
    """
    Fetch the most recent merge commit log entries from `main`, formatted and limited to `n` entries.
    
    Parameters:
        n (int): Maximum number of merge commits to include.
    
    Returns:
        list[str]: Formatted log lines (each like "- `<short-hash>` YYYY-MM-DD: message"); empty list if no output is available.
    """
    raw = _git(
        "log",
        f"-n{n}",
        "--first-parent",
        "--merges",
        "main",
        "--pretty=format:- `%h` %ad: %s",
        "--date=short",
    )
    return raw.splitlines() if raw else []


def _load_state() -> dict:
    """
    Load and sanitize persisted milestone firing state from signals/cycles.json.
    
    If the file is missing or malformed (invalid JSON, non-object root, or invalid values) this returns an empty dict. The returned mapping contains a non-negative integer counter for each tier label defined in TIERS. When present and valid, the mapping also includes "last_total" (an int >= 0) and "last_run" (an ISO timestamp string).
    
    Returns:
        dict: Mapping of tier labels to non-negative integer counters; may include
        "last_total" (int >= 0) and "last_run" (str) when available and valid.
    """
    if not STATE.is_file():
        return {}
    try:
        raw = json.loads(STATE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    if not isinstance(raw, dict):
        return {}
    cleaned: dict = {}
    for label, _ in TIERS:
        value = raw.get(label, 0)
        cleaned[label] = value if isinstance(value, int) and value >= 0 else 0
    last_total = raw.get("last_total", 0)
    if isinstance(last_total, int) and last_total >= 0:
        cleaned["last_total"] = last_total
    if isinstance(raw.get("last_run"), str):
        cleaned["last_run"] = raw["last_run"]
    return cleaned


def _save_state(state: dict) -> None:
    """
    Persist the given state mapping to the signals cycles JSON file.
    
    Ensures the signals directory exists, then writes `state` as pretty-printed JSON (two-space indent) encoded as UTF-8 with a trailing newline to the module's `STATE` path.
    
    Parameters:
        state (dict): Mapping containing per-tier counters and optional metadata (e.g., `last_total`, `last_run`) to persist.
    """
    SIGNALS.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _emit(tier_label: str, ordinal: int, total_merges: int, recent: list[str]) -> Path:
    """
    Create or update a milestone Markdown file for the given tier and ordinal.
    
    The file records the emission timestamp, the current short HEAD, the total merge count at emission time,
    and a "Last <tier> merges leading here" section populated from `recent`.
    
    Parameters:
    	tier_label (str): Tier label used in the filename and headings (e.g. "7", "49", "369").
    	ordinal (int): Ordinal number for this milestone within the tier (1-based).
    	total_merges (int): Total number of merge commits on `main` at the time of emission.
    	recent (list[str]): Lines describing recent merge commits to include under the "Last <tier> merges" section.
    
    Returns:
    	target (Path): Path to the Markdown file written under the milestones directory.
    """
    MILESTONES.mkdir(parents=True, exist_ok=True)
    target = MILESTONES / f"{tier_label}-{ordinal}.md"
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    head = _git("rev-parse", "--short", "HEAD") or "unknown"

    body: list[str] = []
    body.append(f"# Milestone {tier_label}: #{ordinal}")
    body.append("")
    body.append(f"_Marketplace crossed {ordinal * int(tier_label)} merged PRs at {now}, HEAD `{head}`._")
    body.append(f"_Total merges on main at this point: {total_merges}._")
    body.append("")
    body.append(f"## Last {tier_label} merges leading here")
    body.append("")
    if recent:
        body.extend(recent)
    else:
        body.append("- _(no merge history available)_")
    body.append("")
    body.append("---")
    body.append("_Auto-generated by `scripts/milestones.py`. Do not hand-edit._")
    body.append("")
    target.write_text("\n".join(body), encoding="utf-8")
    return target


def main() -> int:
    """
    Emit milestone Markdown files for tiers when the merge commit count on `main` crosses their thresholds and persist per-tier progress.
    
    When one or more new milestones are generated this run, writes milestone files under the `milestones/` directory and updates `signals/cycles.json` with per-tier ordinals plus `last_total` and `last_run`. If no milestones are generated, no files or state are modified.
    
    Returns:
        int: Exit code `0` on successful completion.
    """
    total = _count_merges_on_main()
    state = _load_state()
    fired: list[str] = []

    for label, modulus in TIERS:
        already = state.get(label, 0)
        target_ordinal = total // modulus
        while already < target_ordinal:
            already += 1
            recent = _recent_log(modulus)
            path = _emit(label, already, total, recent)
            fired.append(str(path.relative_to(ROOT)))
        state[label] = already

    # Only persist state when at least one milestone fired. Otherwise
    # the file would change (last_run timestamp) on every workflow run
    # and pollute the git history with no-op commits. Idempotency is
    # the contract: same merge count + same state -> no writes.
    if fired:
        state["last_total"] = total
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        _save_state(state)
        print("Milestones: fired " + ", ".join(fired))
    else:
        print(f"Milestones: nothing to fire (total merges = {total})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
