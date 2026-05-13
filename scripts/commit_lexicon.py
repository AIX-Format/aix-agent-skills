#!/usr/bin/env python3
"""
Commit Lexicon: distil the top words from the last calendar month's
commit messages and append them to `signals/lexicon-YYYY-MM.md`.

The point isn't analytics; it's a slow, append-only signal channel.
When a new word starts trending in commits ("rhythm", "vortex",
"persona"), the lexicon notices before any human has to. The Chronicle
script can later cite this file when summarising a quarter.

Output is deterministic for a given month, so running twice in the
same month is idempotent (overwrites the same file). Stopwords are
hard-coded (no nltk dependency) and skewed toward English/Arabic mix.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "signals"

STOPWORDS = {
    # English glue words
    "the", "a", "an", "and", "or", "but", "if", "then", "else", "of",
    "for", "to", "in", "on", "at", "by", "with", "from", "as", "is",
    "are", "was", "were", "be", "been", "being", "this", "that", "it",
    "its", "we", "i", "you", "he", "she", "they", "them", "our", "their",
    "not", "no", "yes", "do", "does", "did", "have", "has", "had", "will",
    "would", "should", "can", "could", "may", "might", "must", "so", "than",
    # Commit-message boilerplate
    "fix", "feat", "chore", "docs", "test", "refactor", "wip", "merge",
    "branch", "pull", "request", "pr", "ci", "update", "add", "remove",
    "change", "use", "make", "new", "set", "get", "via", "main", "into",
    "from", "files", "file", "code", "now", "via", "support", "ref",
    # Arabic glue
    "في", "على", "إلى", "من", "عن", "مع", "هذا", "هذه", "اللي", "ده",
    "كل", "أو", "ثم", "لـ", "هو", "هي", "بعد", "قبل", "بدون", "إن",
}
TOKEN_RE = re.compile(r"[A-Za-z\u0600-\u06FF]{3,}")


def _git(*args: str) -> str:
    """
    Run a git command in the repository root and return its standard output.
    
    Parameters:
        *args (str): Arguments to pass to the `git` command (e.g., "log", "--since=...").
    
    Returns:
        str: The command's stdout with surrounding whitespace removed, or an empty string if the git command fails.
    """
    try:
        return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True).strip()
    except subprocess.CalledProcessError:
        return ""


def _previous_month_window(today: date) -> tuple[date, date, str]:
    """
    Compute the start, exclusive end, and YYYY-MM label for the calendar month immediately preceding `today`.
    
    Returns:
        since (date): First day of the previous month.
        until (date): First day of the current month (exclusive upper bound).
        label (str): Previous month formatted as "YYYY-MM".
    """
    first_of_this = today.replace(day=1)
    last_of_prev = first_of_this - timedelta(days=1)
    first_of_prev = last_of_prev.replace(day=1)
    label = first_of_prev.strftime("%Y-%m")
    return first_of_prev, first_of_this, label


def _collect_messages(since: date, until: date) -> list[str]:
    """
    Collect commit message lines (subject and body) from the repository between two dates.
    
    Runs `git log` for the given date window using `--pretty=format:%s%n%b` and returns a list of non-blank lines from the subjects and bodies of matching commits.
    
    Parameters:
        since (date): Inclusive lower bound for `git --since`.
        until (date): Upper bound for `git --until` (the calling code treats this as an exclusive upper bound for the desired window).
    
    Returns:
        list[str]: Non-empty lines extracted from commit subjects and bodies within the specified window.
    """
    raw = _git(
        "log",
        f"--since={since.isoformat()}",
        f"--until={until.isoformat()}",
        "--pretty=format:%s%n%b",
    )
    return [line for line in raw.splitlines() if line.strip()]


def _tally(lines: list[str]) -> Counter:
    """
    Build a frequency counter of normalized tokens extracted from commit message lines.
    
    Parameters:
        lines (list[str]): Iterable of commit message lines to tokenize and count.
    
    Returns:
        Counter: Mapping of token -> occurrence count (tokens are lowercased and exclude configured stopwords).
    """
    counter: Counter = Counter()
    for line in lines:
        for tok in TOKEN_RE.findall(line.lower()):
            if tok in STOPWORDS:
                continue
            counter[tok] += 1
    return counter


def main() -> int:
    """
    Builds a monthly commit-token lexicon from git commit messages for the previous calendar month and writes it to signals/lexicon-YYYY-MM.md.
    
    Scans commit subject and body lines for the calendar month immediately before today, tokenizes and filters tokens using the module's rules, selects the top 50 tokens by frequency, and writes a Markdown file containing a header, a brief summary of the window and scanned line count, and either a table of tokens with counts or an explicit "no commits" marker. The target file is created under the `signals` directory and is overwritten if it already exists for the same month.
    
    Returns:
        int: Exit code `0` on success.
    """
    today = date.today()
    since, until, label = _previous_month_window(today)
    lines = _collect_messages(since, until)
    counter = _tally(lines)
    top = counter.most_common(50)

    SIGNALS.mkdir(parents=True, exist_ok=True)
    target = SIGNALS / f"lexicon-{label}.md"

    out: list[str] = []
    out.append(f"# Commit Lexicon: {label}")
    out.append("")
    out.append(
        f"Top tokens from commit messages between {since.isoformat()} and "
        f"{until.isoformat()} ({len(lines)} commit body lines scanned)."
    )
    out.append("")
    if not top:
        out.append("_No commits in this window._")
    else:
        out.append("| Token | Count |")
        out.append("| --- | ---: |")
        for tok, n in top:
            out.append(f"| `{tok}` | {n} |")
    out.append("")
    target.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"Commit Lexicon: wrote {target.relative_to(ROOT)} ({len(top)} tokens)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
