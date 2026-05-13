#!/usr/bin/env python3
"""
Link Doctor: weekly broken-link crawler for the marketplace.

Extracts every http(s) URL from markdown files under the repo root,
de-duplicates, and HEADs each one with a short timeout. Writes a
report to `signals/link-health-YYYY-MM-DD.md` listing only the
broken URLs and which files reference them. Healthy URLs are not
listed (the report stays short and readable).

Zero external dependencies: stdlib `urllib.request` is used directly.
Per-request timeout caps the total run time even when many links
are stale.

Exit code 0 if the script completed; non-zero only on infrastructure
errors (cannot read files, etc.). Broken-link counts are reported in
the markdown output and printed to stdout; CI can decide whether to
fail on a threshold.
"""

from __future__ import annotations

import argparse
import re
import socket
import ssl
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SIGNALS = ROOT / "signals"

# URL extractor with two shapes:
#   1. Markdown inline link `[text](url)` where `url` may contain a
#      single level of balanced parentheses. Wikipedia URLs like
#      `https://en.wikipedia.org/wiki/Foo_(disambiguation)` need
#      this so they are not truncated at the first `)`.
#   2. Bare URL outside a markdown link, terminated at whitespace,
#      angle brackets, quotes, or backticks.
#
# `_BALANCED` matches characters that are either non-paren and
# non-whitespace, or a `(...)` pair with no nested parens. One level
# of balance handles every URL we have seen in the corpus; adding
# deeper nesting would require the `regex` module's recursive
# patterns and the marginal gain is not worth the dependency.
_BALANCED = r"(?:[^\s<>\"'`()]+|\([^()]*\))+"
URL_RE = re.compile(
    rf"\]\((?P<md>https?://{_BALANCED})\)"
    r"|"
    rf"(?P<bare>https?://{_BALANCED})",
)

# Hosts and host+path-prefix combinations we never check. Badges and
# image hosts habitually 403 on HEAD; commit/pull URLs are noisy
# self-references that don't need health checks.
SKIP_HOSTS = frozenset({
    "img.shields.io",
    "shields.io",
    "img.icons8.com",
    "avatars.githubusercontent.com",
    "www.gstatic.com",
})
# (host, path_prefix) pairs that should also be skipped. Matched with
# `parsed.path.startswith(prefix)`, never substring-matched against
# the raw URL.
SKIP_HOST_PREFIXES = (
    ("github.com", "/Moeabdelaziz007/aix-agent-skills/commit/"),
    ("github.com", "/Moeabdelaziz007/aix-agent-skills/pull/"),
)


def _should_skip(url: str) -> bool:
    """
    Decide whether to skip an URL using parsed host/path rather than
    substring matching against the raw URL. Substring matching gave
    false negatives (e.g. an unrelated link with "shields.io" in a
    query string would be skipped) and could hide genuine breakage.
    """
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    if host in SKIP_HOSTS:
        return True
    for skip_host, prefix in SKIP_HOST_PREFIXES:
        if host == skip_host and path.startswith(prefix):
            return True
    return False


def _gather_links() -> dict[str, list[str]]:
    """
    Return {url: [file paths that reference it]}, sorted file lists.

    Excludes generated signal reports under `signals/` so a broken
    URL listed in a prior `link-health.md` cannot bounce back into
    the crawl as a self-referential input and produce a persistent
    false positive after the original source reference has been
    removed.
    """
    by_url: dict[str, set[str]] = defaultdict(set)
    skip_dirs = (".git", "node_modules", ".compost", "signals")
    for md in ROOT.rglob("*.md"):
        if any(part in skip_dirs for part in md.parts):
            continue
        try:
            text = md.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        rel = str(md.relative_to(ROOT))
        for match in URL_RE.finditer(text):
            raw = match.group("md") or match.group("bare") or ""
            url = raw.rstrip(".,;:")
            if not url:
                continue
            if _should_skip(url):
                continue
            by_url[url].add(rel)
    return {u: sorted(files) for u, files in by_url.items()}


def _check(url: str, timeout: float) -> tuple[int | None, str]:
    """
    Return (status, message). status is the HTTP status if reachable,
    None on network/SSL/timeout failure. message is empty on 2xx/3xx,
    otherwise a short reason string.
    """
    req = urllib.request.Request(
        url,
        method="HEAD",
        headers={
            "User-Agent": "iqra-link-doctor/1.0",
            # Some endpoints reject HEAD; we fall back below.
            "Accept": "*/*",
        },
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.status, ""
    except urllib.error.HTTPError as exc:
        # HEAD not allowed: retry with a tiny GET.
        if exc.code in (403, 405, 501):
            try:
                req2 = urllib.request.Request(url, method="GET",
                                              headers={"User-Agent": "iqra-link-doctor/1.0",
                                                       "Range": "bytes=0-0"})
                with urllib.request.urlopen(req2, timeout=timeout, context=ctx) as resp:
                    return resp.status, ""
            except Exception as inner:
                return None, f"{exc.code} then {type(inner).__name__}"
        return exc.code, f"HTTP {exc.code}"
    except (urllib.error.URLError, socket.timeout, ssl.SSLError, ConnectionError, OSError) as exc:
        return None, type(exc).__name__


def _is_broken(status: int | None) -> bool:
    if status is None:
        return True
    return status >= 400


def _render(report_date: date, results: list[tuple[str, list[str], int | None, str]]) -> str:
    broken = [r for r in results if _is_broken(r[2])]
    total = len(results)
    out: list[str] = []
    out.append(f"# Link Health: {report_date.isoformat()}")
    out.append("")
    out.append(
        f"Scanned **{total}** unique URL(s) across the repo. "
        f"Found **{len(broken)}** unreachable or 4xx/5xx."
    )
    out.append("")
    if not broken:
        out.append("_All links healthy._")
        out.append("")
        return "\n".join(out) + "\n"
    out.append("## Broken links")
    out.append("")
    out.append("| URL | Status | Referenced in |")
    out.append("| --- | --- | --- |")
    for url, files, status, msg in broken:
        status_str = msg if msg else (str(status) if status else "unreachable")
        files_str = ", ".join(f"`{f}`" for f in files[:5])
        if len(files) > 5:
            files_str += f", +{len(files) - 5} more"
        out.append(f"| {url} | {status_str} | {files_str} |")
    out.append("")
    return "\n".join(out) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Link health crawler")
    parser.add_argument("--timeout", type=float, default=8.0,
                        help="Per-request HTTP timeout (seconds, default 8)")
    parser.add_argument("--fail-on-broken", action="store_true",
                        help="Exit 1 if any broken links are found")
    args = parser.parse_args()

    by_url = _gather_links()
    urls = sorted(by_url)

    # Parallelise HEAD requests so a few slow/timing-out hosts do not
    # dominate the run time. With 8s per-request timeout and 10
    # workers, a corpus of 100 URLs with worst-case timeouts settles
    # in under 90 seconds instead of 800.
    results: list[tuple[str, list[str], int | None, str]] = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(_check, url, args.timeout): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            status, msg = future.result()
            results.append((url, by_url[url], status, msg))
    # Re-sort so the report is deterministic regardless of completion order.
    results.sort(key=lambda r: r[0])

    SIGNALS.mkdir(parents=True, exist_ok=True)
    # Static filename, deliberately. The report's history lives in
    # git already; per-day files would clutter signals/ without
    # adding signal. Overwriting on every run keeps the directory
    # small and the latest state always at a known path.
    target = SIGNALS / "link-health.md"
    target.write_text(_render(date.today(), results), encoding="utf-8")
    broken = sum(1 for r in results if _is_broken(r[2]))
    print(f"Link Doctor: scanned {len(results)} URLs, {broken} broken. Wrote {target.relative_to(ROOT)}")
    return 1 if (args.fail_on_broken and broken) else 0


if __name__ == "__main__":
    sys.exit(main())
