#!/usr/bin/env python3
"""
🌊 Rhythm Bridge — iqra ↔ marketplace tide synchronizer.

Runs every 3 hours from a scheduled GitHub Action. Lives entirely in this
repo; the iqra repo is cloned read-only on each tick. The bridge keeps no
runtime dependency on iqra emitting telemetry — it derives the per-skill
"tide" signal from git activity proxies.

Outputs (when CROSS_POLLINATE action fires and pairs are found):
  - `.rhythm/pr_body.md`   — human-readable PR description.
  - `.rhythm/patches.json` — machine-readable list of patches to apply.
  - Modified `skills/*.md` files with an appended `## 🌊 Inherited Patterns`
    section.

Outputs always:
  - `.rhythm/tick_counter` — incremented.
  - `.rhythm/history.jsonl` — appended with this tick's summary.

Sets GitHub Actions outputs:
  - `action`           — the cadence action this tick ran.
  - `pairs_count`      — number of cross-pollination patches generated.
  - `tick`             — current tick number.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

# ─── Paths & Constants ───────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = ROOT / "skills.json"
SKILLS_DIR = ROOT / "skills"
RHYTHM_DIR = ROOT / ".rhythm"
TICK_FILE = RHYTHM_DIR / "tick_counter"
HISTORY_FILE = RHYTHM_DIR / "history.jsonl"
PR_BODY_FILE = RHYTHM_DIR / "pr_body.md"
PATCHES_FILE = RHYTHM_DIR / "patches.json"
COOLDOWN_FILE = RHYTHM_DIR / "cooldowns.json"
PATTERNS_REGISTRY_FILE = RHYTHM_DIR / "patterns_registry.json"

# Cadence — modular alignment with iqra's Pulse369 (3-6-9 day, 7-49 week)
TICK_HOURS = 3
CROSS_POLLINATE_EVERY = 9      # ~ daily
TIER_REBALANCE_EVERY = 56      # ~ weekly
DEEP_REFORM_EVERY = 392        # ~ quarterly

# Thresholds
HIGH_THRESHOLD = 0.65          # iqra tide score
ACTIVE_WINDOW_HOURS = 3        # marketplace activity lookback
IQRA_LOOKBACK_DAYS = 7
COOLDOWN_TICKS = 9             # same pair locked for 9 ticks (~27h)
MAX_PAIRS_PER_CYCLE = 7        # DASTUR seven

# Section marker — used for idempotency (skip if already pollinated).
SECTION_HEADER = "## 🌊 Inherited Patterns"

# ─── Data classes ────────────────────────────────────────────────────────────


@dataclass
class IqraSignal:
    """Per-skill activity signal derived from iqra git log."""

    name: str
    mention_count: int = 0
    weighted_score: float = 0.0
    last_seen_iso: Optional[str] = None
    touched_files: list[str] = field(default_factory=list)

    @property
    def tide_score(self) -> float:
        """Normalize to [0, 1]. mentions×decay → squashed by tanh."""
        # tanh keeps the curve well-behaved as mentions grow.
        return math.tanh(self.weighted_score / 5.0)


@dataclass
class MarketplaceSignal:
    """Per-skill activity in the marketplace itself."""

    name: str
    lines_changed: int = 0
    commits: int = 0
    last_touched_iso: Optional[str] = None

    @property
    def activity_score(self) -> float:
        # tanh squash so very-large diffs don't dominate.
        return math.tanh((self.lines_changed + self.commits * 10) / 50.0)


@dataclass
class CrossPollination:
    donor: str
    recipient: str
    confidence: float
    patterns: list[str]
    reason: str


# ─── Helpers ─────────────────────────────────────────────────────────────────


def log(msg: str) -> None:
    print(f"[rhythm] {msg}", flush=True)


def run(cmd: list[str], cwd: Optional[Path] = None) -> str:
    """Run a subprocess, return stdout. Raise on failure with full context."""
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            f"Command failed ({proc.returncode}): {' '.join(cmd)}\n"
            f"stderr: {proc.stderr}"
        )
    return proc.stdout


def read_tick() -> int:
    if not TICK_FILE.exists():
        return 0
    raw = TICK_FILE.read_text(encoding="utf-8").strip() or "0"
    try:
        return int(raw)
    except ValueError:
        log(f"Warning: invalid tick file content {raw!r}, resetting to 0.")
        return 0


def write_tick(value: int) -> None:
    TICK_FILE.write_text(f"{value}\n", encoding="utf-8")


def load_skill_names() -> list[str]:
    """Authoritative list of skills, taken from the manifest."""
    data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    return [
        s["name"]
        for s in data.get("skills", [])
        if isinstance(s, dict) and isinstance(s.get("name"), str)
    ]


def determine_action(tick: int, override: Optional[str] = None) -> str:
    if override:
        return override
    if tick == 0:
        # First-ever run: emit telemetry only so the bridge has a baseline.
        return "TELEMETRY_MIRROR"
    if tick % DEEP_REFORM_EVERY == 0:
        return "DEEP_REFORM"
    if tick % TIER_REBALANCE_EVERY == 0:
        return "TIER_REBALANCE"
    if tick % CROSS_POLLINATE_EVERY == 0:
        return "CROSS_POLLINATE"
    return "TELEMETRY_MIRROR"


# ─── iqra signal extraction ──────────────────────────────────────────────────


def sample_iqra_signals(iqra_repo: Path, skill_names: list[str]) -> dict[str, IqraSignal]:
    """Build a tide signal for each skill by mining iqra's recent git history.

    We look at the last IQRA_LOOKBACK_DAYS of commits and count:
      1. References to the skill name in commit messages (weight 2.0)
      2. References to the skill name in changed file paths (weight 3.0)
      3. References to the skill name in diff content (weight 1.0)
    Each reference is decayed by age: weight × exp(-age_days / lookback).
    """
    signals: dict[str, IqraSignal] = {n: IqraSignal(name=n) for n in skill_names}

    since = (datetime.now(timezone.utc) - timedelta(days=IQRA_LOOKBACK_DAYS)).isoformat()
    fmt = "%H%x09%aI%x09%s"

    log(f"Sampling iqra git log since {since}...")
    try:
        log_output = run(
            ["git", "log", "--no-merges", f"--since={since}", f"--pretty=format:{fmt}", "--name-only"],
            cwd=iqra_repo,
        )
    except RuntimeError as exc:
        log(f"iqra git log failed (treating as empty signal): {exc}")
        return signals

    # Stream-parse: blocks are <sha>\t<iso>\t<subject>\n<file>\n<file>\n\n
    blocks = re.split(r"\n\n+", log_output.strip())
    now = datetime.now(timezone.utc)

    for block in blocks:
        lines = block.split("\n")
        if not lines:
            continue
        head = lines[0]
        parts = head.split("\t", 2)
        if len(parts) < 3:
            continue
        sha, iso, subject = parts
        files = [ln for ln in lines[1:] if ln.strip()]
        try:
            ts = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        except ValueError:
            continue
        age_days = max(0.0, (now - ts).total_seconds() / 86400.0)
        decay = math.exp(-age_days / IQRA_LOOKBACK_DAYS)

        subject_lower = subject.lower()
        for name in skill_names:
            # Token boundary so `circuit-breaker` doesn't match `super-circuit-breaker-x`
            pattern = re.compile(rf"(?<![a-z0-9-]){re.escape(name)}(?![a-z0-9-])")
            sig = signals[name]
            hit = False
            if pattern.search(subject_lower):
                sig.weighted_score += 2.0 * decay
                hit = True
            for f in files:
                if pattern.search(f.lower()):
                    sig.weighted_score += 3.0 * decay
                    sig.touched_files.append(f)
                    hit = True
            if hit:
                sig.mention_count += 1
                if sig.last_seen_iso is None or iso > sig.last_seen_iso:
                    sig.last_seen_iso = iso

    return signals


# ─── marketplace signal extraction ───────────────────────────────────────────


def sample_marketplace_signals(skill_names: list[str]) -> dict[str, MarketplaceSignal]:
    """Active marketplace skills = MDs touched within ACTIVE_WINDOW_HOURS."""
    signals: dict[str, MarketplaceSignal] = {
        n: MarketplaceSignal(name=n) for n in skill_names
    }
    since = (
        datetime.now(timezone.utc) - timedelta(hours=ACTIVE_WINDOW_HOURS)
    ).isoformat()

    log(f"Sampling marketplace git log since {since}...")
    try:
        log_output = run(
            [
                "git",
                "log",
                "--no-merges",
                f"--since={since}",
                "--numstat",
                "--pretty=format:COMMIT %H %aI",
                "--",
                "skills/",
            ],
            cwd=ROOT,
        )
    except RuntimeError as exc:
        log(f"marketplace git log failed: {exc}")
        return signals

    current_iso = None
    for line in log_output.splitlines():
        if line.startswith("COMMIT "):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                current_iso = parts[2]
            continue
        if not line.strip() or not current_iso:
            continue
        # Format: "added\tdeleted\tpath"
        tokens = line.split("\t")
        if len(tokens) < 3:
            continue
        added, deleted, path = tokens[0], tokens[1], tokens[2]
        # Binary diffs use "-" instead of numbers
        try:
            net = int(added) + int(deleted)
        except ValueError:
            net = 1
        m = re.match(r"skills/([^/]+)\.md$", path)
        if not m:
            continue
        name = m.group(1)
        if name not in signals:
            continue
        sig = signals[name]
        sig.lines_changed += net
        sig.commits += 1
        if sig.last_touched_iso is None or current_iso > sig.last_touched_iso:
            sig.last_touched_iso = current_iso

    return signals


# ─── Cooldown tracking ───────────────────────────────────────────────────────


def load_cooldowns() -> dict[str, int]:
    if not COOLDOWN_FILE.exists():
        return {}
    try:
        return json.loads(COOLDOWN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def save_cooldowns(cooldowns: dict[str, int]) -> None:
    COOLDOWN_FILE.write_text(
        json.dumps(cooldowns, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def pair_key(donor: str, recipient: str) -> str:
    return f"{donor}->{recipient}"


# ─── Cross-pollination logic ─────────────────────────────────────────────────


def _load_patterns_registry() -> dict[str, list[str]]:
    """Read the donor patterns registry. Returns an empty mapping if missing.

    Keeping patterns in a separate JSON file (instead of MD frontmatter)
    means the existing structural tests on skills/*.md stay green. The
    registry is the source of truth for the Rhythm Bridge.
    """
    if not PATTERNS_REGISTRY_FILE.is_file():
        return {}
    try:
        data = json.loads(PATTERNS_REGISTRY_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log(f"patterns_registry.json is malformed ({exc}); treating as empty.")
        return {}
    patterns = data.get("patterns", {})
    return {k: list(v) for k, v in patterns.items() if isinstance(v, list)}


# Cached at module import; re-read between cycles is unnecessary because the
# script runs as a one-shot in CI.
_PATTERNS_REGISTRY: Optional[dict[str, list[str]]] = None


def extract_success_patterns(skill_or_path) -> list[str]:
    """Return the success_patterns for a skill.

    Accepts either a skill name (string) or a Path to a skill MD file —
    the Path form is convenient when callers already hold the MD path
    elsewhere in the pipeline.
    """
    global _PATTERNS_REGISTRY
    if _PATTERNS_REGISTRY is None:
        _PATTERNS_REGISTRY = _load_patterns_registry()

    if isinstance(skill_or_path, Path):
        name = skill_or_path.stem
    else:
        name = str(skill_or_path)
    return list(_PATTERNS_REGISTRY.get(name, []))


def pollination_section(
    donor: str, patterns: list[str], confidence: float, tick: int
) -> str:
    """Render the markdown section to append to the recipient MD."""
    lines = [
        "",
        SECTION_HEADER,
        "",
        f"_Auto-pollinated from `{donor}` by the Rhythm Bridge "
        f"(cycle {tick}, confidence {confidence:.2f})._",
        "",
    ]
    for p in patterns:
        lines.append(f"- {p}")
    lines.append("")
    return "\n".join(lines)


def has_been_pollinated_from(md_path: Path, donor: str) -> bool:
    """Idempotency check: skip if this donor already pollinated this recipient."""
    if not md_path.is_file():
        return False
    text = md_path.read_text(encoding="utf-8")
    return SECTION_HEADER in text and f"`{donor}`" in text


def compute_pairs(
    iqra: dict[str, IqraSignal],
    market: dict[str, MarketplaceSignal],
    cooldowns: dict[str, int],
    tick: int,
) -> list[CrossPollination]:
    """Match HIGH iqra × ACTIVE marketplace, ranked by combined score."""
    candidates: list[CrossPollination] = []
    high_donors = [s for s in iqra.values() if s.tide_score >= HIGH_THRESHOLD]
    active_recipients = [s for s in market.values() if s.activity_score > 0]

    log(f"Donors above HIGH_THRESHOLD: {len(high_donors)}")
    log(f"Active recipients in market: {len(active_recipients)}")

    for donor in high_donors:
        donor_patterns = extract_success_patterns(SKILLS_DIR / f"{donor.name}.md")
        if not donor_patterns:
            # Nothing to transfer; skip cleanly.
            continue
        for recipient in active_recipients:
            if recipient.name == donor.name:
                continue
            key = pair_key(donor.name, recipient.name)
            unlock_at = cooldowns.get(key, 0)
            if tick < unlock_at:
                continue
            recipient_md = SKILLS_DIR / f"{recipient.name}.md"
            if has_been_pollinated_from(recipient_md, donor.name):
                continue
            confidence = donor.tide_score * recipient.activity_score
            if confidence < 0.10:
                continue
            candidates.append(
                CrossPollination(
                    donor=donor.name,
                    recipient=recipient.name,
                    confidence=round(confidence, 3),
                    patterns=donor_patterns,
                    reason=(
                        f"donor tide={donor.tide_score:.2f} "
                        f"({donor.mention_count} iqra mentions), "
                        f"recipient activity={recipient.activity_score:.2f} "
                        f"({recipient.commits} commits, {recipient.lines_changed} lines)"
                    ),
                )
            )

    candidates.sort(key=lambda c: c.confidence, reverse=True)
    return candidates[:MAX_PAIRS_PER_CYCLE]


def apply_patches(pairs: list[CrossPollination], tick: int) -> int:
    """Append pollination sections to recipient MDs. Returns number applied."""
    applied = 0
    for pair in pairs:
        recipient_md = SKILLS_DIR / f"{pair.recipient}.md"
        if not recipient_md.is_file():
            continue
        section = pollination_section(pair.donor, pair.patterns, pair.confidence, tick)
        text = recipient_md.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        text += section
        recipient_md.write_text(text, encoding="utf-8")
        applied += 1
    return applied


# ─── PR body & history ───────────────────────────────────────────────────────


def render_pr_body(tick: int, action: str, pairs: list[CrossPollination]) -> str:
    next_rebalance = TIER_REBALANCE_EVERY - (tick % TIER_REBALANCE_EVERY)
    next_reform = DEEP_REFORM_EVERY - (tick % DEEP_REFORM_EVERY)
    lines = [
        f"# 🌊 Tide-Sync Cycle {tick}",
        "",
        f"**Action**: `{action}`  ",
        f"**Tick**: {tick}  ",
        f"**Next rebalance**: in {next_rebalance} ticks "
        f"(~{next_rebalance * TICK_HOURS}h)  ",
        f"**Next deep reform**: in {next_reform} ticks "
        f"(~{next_reform * TICK_HOURS // 24}d)",
        "",
    ]
    if not pairs:
        lines += [
            "No cross-pollination pairs reached the threshold this cycle. "
            "The bridge ran cleanly; the marketplace and iqra are in steady state.",
        ]
        return "\n".join(lines) + "\n"

    lines += [
        f"## {len(pairs)} cross-pollination(s)",
        "",
        "| Donor (iqra HIGH) | Recipient (active in market) | Confidence | Patterns transferred |",
        "|---|---|---|---|",
    ]
    for p in pairs:
        patterns_summary = ", ".join(f"`{x}`" for x in p.patterns[:5])
        if len(p.patterns) > 5:
            patterns_summary += f", +{len(p.patterns) - 5} more"
        lines.append(
            f"| `{p.donor}` | `{p.recipient}` | {p.confidence:.2f} | {patterns_summary} |"
        )

    lines += [
        "",
        "## Reasoning (per pair)",
        "",
    ]
    for p in pairs:
        lines.append(f"- **{p.donor} → {p.recipient}**: {p.reason}")

    lines += [
        "",
        "## Safety",
        "",
        "- Each pair is cooldown-locked for the next "
        f"{COOLDOWN_TICKS} ticks (~{COOLDOWN_TICKS * TICK_HOURS}h).",
        "- Patches only **append** a new `## 🌊 Inherited Patterns` section; "
        "no existing content is overwritten.",
        f"- Cycle hard-capped at {MAX_PAIRS_PER_CYCLE} pairs (the DASTUR seven).",
        "- The `needs-tribunal` label blocks merge until SwarmTribunal-in-CI approves.",
        "",
    ]
    return "\n".join(lines) + "\n"


def append_history(
    tick: int,
    action: str,
    pairs: list[CrossPollination],
    iqra_high: int,
    market_active: int,
) -> None:
    entry = {
        "tick": tick,
        "ts": datetime.now(timezone.utc).isoformat(),
        "action": action,
        "iqra_high_count": iqra_high,
        "market_active_count": market_active,
        "pairs_proposed": len(pairs),
        "pairs": [{"donor": p.donor, "recipient": p.recipient, "confidence": p.confidence} for p in pairs],
    }
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


# ─── Output helpers ──────────────────────────────────────────────────────────


def emit_github_output(key: str, value: str) -> None:
    out_file = os.environ.get("GITHUB_OUTPUT")
    if out_file:
        with open(out_file, "a", encoding="utf-8") as f:
            f.write(f"{key}={value}\n")
    print(f"[output] {key}={value}")


# ─── Main entry ──────────────────────────────────────────────────────────────


def main() -> int:
    parser = argparse.ArgumentParser(description="Rhythm Bridge tick runner")
    parser.add_argument(
        "--iqra-repo",
        default=os.environ.get("IQRA_REPO_PATH", "../iqra"),
        help="Path to a locally cloned iqra repository (default: ../iqra).",
    )
    parser.add_argument(
        "--force-action",
        default=os.environ.get("FORCE_ACTION") or None,
        help="Override the cadence and run a specific action.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Compute everything but write no files (no tick increment, no patches).",
    )
    args = parser.parse_args()

    iqra_repo = Path(args.iqra_repo).resolve()
    if not iqra_repo.is_dir():
        log(f"iqra repo not found at {iqra_repo}; running with empty iqra signal.")
        iqra_repo = None

    RHYTHM_DIR.mkdir(exist_ok=True)
    tick = read_tick() + (0 if args.dry_run else 1)
    action = determine_action(tick, args.force_action)
    log(f"Cycle starting: tick={tick}, action={action}")

    skill_names = load_skill_names()
    log(f"Skills in manifest: {len(skill_names)}")

    iqra_signals = (
        sample_iqra_signals(iqra_repo, skill_names) if iqra_repo else {n: IqraSignal(n) for n in skill_names}
    )
    market_signals = sample_marketplace_signals(skill_names)

    pairs: list[CrossPollination] = []
    if action in ("CROSS_POLLINATE", "TIER_REBALANCE", "DEEP_REFORM"):
        cooldowns = load_cooldowns()
        # Garbage-collect cooldown entries that have already expired.
        cooldowns = {k: v for k, v in cooldowns.items() if v > tick}
        pairs = compute_pairs(iqra_signals, market_signals, cooldowns, tick)
        if not args.dry_run and pairs:
            apply_patches(pairs, tick)
            for p in pairs:
                cooldowns[pair_key(p.donor, p.recipient)] = tick + COOLDOWN_TICKS
            save_cooldowns(cooldowns)
    else:
        log(f"Action {action} does not produce pairs this tick.")

    body = render_pr_body(tick, action, pairs)
    if not args.dry_run:
        PR_BODY_FILE.write_text(body, encoding="utf-8")
        PATCHES_FILE.write_text(
            json.dumps([asdict(p) for p in pairs], indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        write_tick(tick)
        append_history(
            tick,
            action,
            pairs,
            iqra_high=sum(1 for s in iqra_signals.values() if s.tide_score >= HIGH_THRESHOLD),
            market_active=sum(1 for s in market_signals.values() if s.activity_score > 0),
        )

    emit_github_output("action", action)
    emit_github_output("tick", str(tick))
    emit_github_output("pairs_count", str(len(pairs)))

    log(f"Done. action={action}, pairs={len(pairs)}, dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
