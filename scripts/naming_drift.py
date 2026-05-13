#!/usr/bin/env python3
"""
Naming Drift Police: flag skills whose names violate marketplace
conventions even though `skema_sentinel.py` already lets them through.

Sentinel enforces the *minimum*: strict kebab-case for public skills,
`_snake_case` for internal ones. This script extends the check with
softer-but-real conventions:

  1. No double dashes (`--`), no trailing dash.
  2. Public skills must have between 2 and 6 dash-separated tokens.
     Single-token names (`foo`) are too vague; 7+ tokens are noisy.
  3. Reserved prefixes (`test-`, `tmp-`, `scratch-`, `draft-`) only
     allowed on internal `_`-prefixed skills.
  4. Tokens that look like initials of common words (e.g. `mgr`, `cfg`,
     `tmp`, `xyz`) get a warning to encourage expansion.
  5. No digits at the end of a token unless paired with a unit (`v2`,
     `7day`, `40c` are fine; trailing meaningless digits like `purity1`
     are warned).

Exit code 0 on success, 1 on hard failure. Most checks emit warnings
(annotations) rather than errors so this can be wired as advisory in
CI without blocking PRs while the conventions settle.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_JSON = ROOT / "skills.json"

# Tokens that look like cryptic abbreviations: flag for expansion.
SUSPECT_TOKENS = {"mgr", "cfg", "tmp", "xyz", "abc", "foo", "bar", "baz", "util", "utils", "misc"}
RESERVED_PREFIXES = ("test-", "tmp-", "scratch-", "draft-", "wip-")
# Digits at end of token, but allow a hint of a unit/suffix already present.
TRAILING_DIGIT_RE = re.compile(r"[a-z][0-9]+$")
UNIT_SUFFIX_RE = re.compile(r"(?:v\d+|\d+d|\d+h|\d+c|\d+vcpu)$")


def annotate(level: str, msg: str) -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print(f"::{level}::{msg}")
    else:
        marker = {"error": "X", "warning": "!", "notice": "i"}.get(level, "-")
        print(f"[{marker}] {msg}")


def check_name(name: str) -> list[tuple[str, str]]:
    """Return a list of (level, message) findings for one skill name."""
    findings: list[tuple[str, str]] = []
    is_internal = name.startswith("_")

    if "--" in name:
        findings.append(("error", f"{name}: contains a double dash"))
    if name.endswith("-") or name.endswith("_"):
        findings.append(("error", f"{name}: trailing separator"))

    if not is_internal:
        tokens = name.split("-")
        if len(tokens) < 2:
            findings.append(("warning", f"{name}: single-token public skill name (too vague)"))
        elif len(tokens) > 6:
            findings.append(("warning", f"{name}: name has {len(tokens)} tokens, consider tightening"))
        for prefix in RESERVED_PREFIXES:
            if name.startswith(prefix):
                findings.append(
                    ("error", f"{name}: reserved prefix {prefix!r} requires a leading underscore")
                )
        for tok in tokens:
            if tok in SUSPECT_TOKENS:
                findings.append(("warning", f"{name}: token {tok!r} is cryptic, prefer a full word"))
            if TRAILING_DIGIT_RE.search(tok) and not UNIT_SUFFIX_RE.search(tok):
                findings.append(("warning", f"{name}: token {tok!r} ends in digits without a unit"))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Naming drift checks for the skills manifest")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures (exit 1 on any finding).",
    )
    args = parser.parse_args()

    try:
        data = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        annotate("error", f"cannot read skills.json: {exc}")
        return 1

    skills = data.get("skills", [])
    errors = 0
    warnings = 0
    for entry in skills:
        name = entry.get("name")
        if not isinstance(name, str) or not name:
            continue
        for level, msg in check_name(name):
            annotate(level, msg)
            if level == "error":
                errors += 1
            else:
                warnings += 1

    summary = f"Naming Drift: {errors} error(s), {warnings} warning(s) across {len(skills)} skill(s)."
    print(summary)
    if errors or (args.strict and warnings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
