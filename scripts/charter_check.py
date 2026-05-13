#!/usr/bin/env python3
"""
Charter Compliance: light grep-based PR linter.

Reads `charter.rules.txt` (one rule per line, format `LEVEL\tNAME\tREGEX`)
and scans every file passed on stdin (one path per line, or all tracked
files if none supplied) for hits. Annotates GitHub Actions with
::warning:: or ::error:: per finding so reviewers see the hits inline
on the Files Changed tab without the workflow having to fail the PR.

Rules ship in `charter.rules.txt` at the repo root. Each line is:

    LEVEL<TAB>RULE_NAME<TAB>REGEX

LEVEL is one of `warn` or `error`. Rules with `error` exit the script
with status 1; `warn` always returns 0. Lines starting with `#` and
blank lines are ignored.

Examples:

    warn  todo-marker  (TODO|FIXME):
    warn  hardcoded-tmp  /tmp/[a-zA-Z0-9]+
    error  aws-key  AKIA[0-9A-Z]{16}

Run via:

    git diff --name-only origin/main... | python3 scripts/charter_check.py
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES_FILE = ROOT / "charter.rules.txt"


def load_rules() -> list[tuple[str, str, re.Pattern]]:
    """
    Load and compile rules from the repository's charter.rules.txt file.
    
    Reads RULES_FILE, parses non-empty, non-comment lines as tab-delimited
    LEVEL, NAME, REGEX entries, and returns a list of (level, name, compiled regex)
    for rules whose level is `warn` or `error`. Lines with the wrong field count
    or with invalid regular expressions are skipped. If RULES_FILE is missing,
    an informational message is written to stderr and an empty list is returned.
    Malformed-line and invalid-regex diagnostics are written to stderr.
    
    Returns:
        rules (list[tuple[str, str, re.Pattern]]): Parsed rule entries where the
        first element is the normalized level (`"warn"` or `"error"`), the second
        is the rule name, and the third is the compiled regular expression.
    """
    if not RULES_FILE.is_file():
        print(f"[!] no charter.rules.txt at {RULES_FILE}; nothing to check", file=sys.stderr)
        return []
    rules: list[tuple[str, str, re.Pattern]] = []
    for lineno, raw in enumerate(RULES_FILE.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            print(f"[!] charter.rules.txt:{lineno}: expected LEVEL<TAB>NAME<TAB>REGEX", file=sys.stderr)
            continue
        level, name, pattern = parts
        level = level.strip().lower()
        if level not in ("warn", "error"):
            continue
        try:
            rules.append((level, name.strip(), re.compile(pattern)))
        except re.error as exc:
            print(f"[!] charter.rules.txt:{lineno}: invalid regex {pattern!r}: {exc}", file=sys.stderr)
    return rules


def annotate(level: str, msg: str, file: str | None = None, line: int | None = None) -> None:
    """
    Emit a GitHub Actions workflow annotation when running in that environment, otherwise print a plain bracketed message.
    
    Parameters:
        level (str): Annotation severity; typically "warning" or "error".
        msg (str): The annotation message text.
        file (str | None): Optional filename to attach to the annotation.
        line (int | None): Optional line number to attach to the annotation.
    """
    if os.environ.get("GITHUB_ACTIONS") == "true":
        loc = ""
        if file:
            loc = f" file={file}"
            if line:
                loc += f",line={line}"
        print(f"::{level}{loc}::{msg}")
    else:
        print(f"[{level}] {file or ''}{':' + str(line) if line else ''} {msg}")


def iter_targets() -> list[Path]:
    # If stdin has data, treat each non-empty line as a path; else
    # fall back to every tracked text file under the repo root.
    """
    Select target file paths for charter scanning.
    
    When standard input provides a list of paths (stdin is not a TTY), each non-empty line is treated as a candidate path; otherwise the repository is scanned for files with extensions .md, .py, .ts, .go, .yml, and .yaml. Paths inside `node_modules` or `.git` are excluded in the fallback scan.
    
    Returns:
        targets (list[Path]): Existing file paths to be scanned.
    """
    if not sys.stdin.isatty():
        paths = [Path(p.strip()) for p in sys.stdin.read().splitlines() if p.strip()]
    else:
        paths = []
    if paths:
        return [p for p in paths if p.is_file()]
    # Fallback: scan all .md/.py/.ts/.go/.yml under the repo (small set).
    out: list[Path] = []
    for ext in ("*.md", "*.py", "*.ts", "*.go", "*.yml", "*.yaml"):
        out.extend(ROOT.glob(f"**/{ext}"))
    return [p for p in out if "node_modules" not in p.parts and ".git" not in p.parts]


def main() -> int:
    """
    Scan repository targets using rules loaded from the charter rules file, emit annotations for each match, and return an exit status reflecting whether any error-level rules were found.
    
    Loads rules, determines target files (stdin-provided paths or a fallback glob), scans each file line-by-line for rule regex matches, emits GitHub Actions annotations (or bracketed console messages) for each match, and prints a summary of findings.
    
    Returns:
        int: exit code 1 if any `error`-level rule matched, otherwise 0.
    """
    rules = load_rules()
    if not rules:
        return 0
    targets = iter_targets()
    hard_failures = 0
    findings = 0
    for path in targets:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for level, name, pattern in rules:
                if pattern.search(line):
                    rel = str(path.relative_to(ROOT)) if path.is_absolute() else str(path)
                    annotate(
                        "error" if level == "error" else "warning",
                        f"charter[{name}]: {line.strip()[:120]}",
                        rel,
                        lineno,
                    )
                    findings += 1
                    if level == "error":
                        hard_failures += 1
    print(f"Charter Compliance: {findings} finding(s), {hard_failures} hard failure(s).")
    return 1 if hard_failures else 0


if __name__ == "__main__":
    sys.exit(main())
