#!/usr/bin/env python3
"""
Skill Quality Gate: blocks stub skills from landing in the marketplace.

A skill is a stub when one or more of its four required sections
(Purpose, Constitutional Alignment, Operational Flow, Failure Modes)
is empty or contains placeholder text such as `TODO: Define ...`.

Modes:
- `--mode=changed` (default): only fails on skills modified relative to
  a base ref. Use in CI on pull requests so the existing stubs can be
  grandfathered while new contributions are held to the gate.
- `--mode=strict`: fails on any stub anywhere. Use in dedicated cleanup
  PRs that fill grandfathered stubs.

Changed files are read from stdin (one path per line) when stdin is not
a TTY, matching the convention used by `scripts/charter_check.py`. In
strict mode, stdin is ignored and every file under `skills/` is scanned.

Exit codes:
- 0: no enforced failures (warnings may still be emitted)
- 1: at least one enforced stub was found
- 2: invocation error
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

# Section name -> set of accepted header strings (case sensitive). The
# validator looks for any of these as a Markdown level-2 heading.
SECTION_ALIASES: dict[str, tuple[str, ...]] = {
    "purpose": ("Purpose", "الغرض", "الجوهر"),
    "constitutional_alignment": (
        "Constitutional Alignment",
        "التوافق الدستوري",
    ),
    "operational_flow": (
        "Operational Flow",
        "آليات التشغيل",
        "سير العمل",
    ),
    "failure_modes": ("Failure Modes", "أنماط الفشل"),
}

# Patterns that mark a section body as a stub. Matched after stripping
# leading whitespace from each line in the section body.
STUB_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^TODO:\s*Define\b", re.IGNORECASE),
    re.compile(r"^TBD\b", re.IGNORECASE),
    re.compile(r"^<fill in>", re.IGNORECASE),
    re.compile(r"^<placeholder>", re.IGNORECASE),
)


def annotate(level: str, msg: str, file: str | None = None, line: int | None = None) -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        loc = ""
        if file:
            loc = f" file={file}"
            if line:
                loc += f",line={line}"
        print(f"::{level}{loc}::{msg}")
    else:
        prefix = f"[{level}]"
        where = f" {file}:{line}" if file and line else (f" {file}" if file else "")
        print(f"{prefix}{where} {msg}")


def parse_sections(text: str) -> dict[int, tuple[str, list[str]]]:
    """
    Walk a markdown document and return a mapping of starting line number
    to (header_text, body_lines). Only level-2 headings are tracked.
    """
    sections: dict[int, tuple[str, list[str]]] = {}
    current_header: str | None = None
    current_start: int = 0
    current_body: list[str] = []
    for lineno, raw in enumerate(text.splitlines(), 1):
        if raw.startswith("## "):
            if current_header is not None:
                sections[current_start] = (current_header, current_body)
            current_header = raw[3:].strip()
            current_start = lineno
            current_body = []
        elif current_header is not None:
            current_body.append(raw)
    if current_header is not None:
        sections[current_start] = (current_header, current_body)
    return sections


def find_section(
    sections: dict[int, tuple[str, list[str]]],
    aliases: tuple[str, ...],
) -> tuple[int, list[str]] | None:
    for start, (header, body) in sections.items():
        if header in aliases:
            return start, body
    return None


def body_is_stub(body: list[str]) -> bool:
    """
    A section body is a stub when every non blank, non comment, non
    list-marker line matches one of the stub patterns, OR when the body
    is entirely whitespace.
    """
    meaningful = [
        line.strip()
        for line in body
        if line.strip()
        and not line.strip().startswith("<!--")
        and not line.strip().startswith("-->")
    ]
    if not meaningful:
        return True
    for line in meaningful:
        # Strip leading list markers (-, *, +, 1., a., etc.) before pattern matching
        normalized_line = re.sub(r"^[-*+]|\d+\.|[a-zA-Z]\.", "", line).strip()
        if not any(pat.match(normalized_line) for pat in STUB_PATTERNS):
            return False
    return True


def scan_skill(path: Path) -> list[tuple[int, str]]:
    """
    Return a list of (line, message) findings for one skill file. A
    finding means either a missing required section or a stub body.
    """
    findings: list[tuple[int, str]] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [(1, f"unable to read: {exc}")]
    sections = parse_sections(text)
    for key, aliases in SECTION_ALIASES.items():
        hit = find_section(sections, aliases)
        if hit is None:
            findings.append((1, f"missing required section: {aliases[0]}"))
            continue
        start, body = hit
        if body_is_stub(body):
            findings.append((start, f"section '{aliases[0]}' is a stub"))
    return findings


def collect_changed_skills() -> list[Path]:
    if sys.stdin.isatty():
        return []
    paths: list[Path] = []
    for raw in sys.stdin.read().splitlines():
        candidate = raw.strip()
        if not candidate:
            continue
        p = Path(candidate)
        if not p.is_absolute():
            p = ROOT / p
        if p.is_file() and p.suffix == ".md" and p.is_relative_to(SKILLS_DIR):
            paths.append(p)
    return paths


def collect_all_skills() -> list[Path]:
    if not SKILLS_DIR.is_dir():
        return []
    return sorted(
        p for p in SKILLS_DIR.rglob("*.md") if not p.name.startswith("_")
    )


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--mode",
        choices=("changed", "strict"),
        default="changed",
        help="changed: enforce only on stdin-listed files. strict: enforce on all skills.",
    )
    args = parser.parse_args(argv)

    all_skills = collect_all_skills()
    if args.mode == "strict":
        enforced = all_skills
        advisory: list[Path] = []
    else:
        changed = collect_changed_skills()
        enforced_set = {p.resolve() for p in changed}
        enforced = [p for p in all_skills if p.resolve() in enforced_set]
        advisory = [p for p in all_skills if p.resolve() not in enforced_set]

    hard_failures = 0
    total_findings = 0

    for path in enforced:
        findings = scan_skill(path)
        rel = path.relative_to(ROOT)
        for lineno, msg in findings:
            annotate("error", f"skill-quality: {msg}", str(rel), lineno)
            hard_failures += 1
            total_findings += 1

    advisory_stub_count = 0
    for path in advisory:
        findings = scan_skill(path)
        if findings:
            advisory_stub_count += 1
            rel = path.relative_to(ROOT)
            for lineno, msg in findings:
                annotate("warning", f"skill-quality (grandfathered): {msg}", str(rel), lineno)
                total_findings += 1

    print(
        f"Skill Quality: mode={args.mode} enforced={len(enforced)} "
        f"advisory={len(advisory)} findings={total_findings} "
        f"hard_failures={hard_failures} grandfathered_stubs={advisory_stub_count}"
    )
    return 1 if hard_failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
