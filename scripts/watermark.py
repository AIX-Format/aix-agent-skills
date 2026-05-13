#!/usr/bin/env python3
"""
Steganographic Watermark — quiet tamper-detection for skill MDs.

Every skill markdown file may carry a single trailing HTML comment of the
form:

    <!-- @iqra_signature: sha256=<hex> -->

The signature is an HMAC-SHA256 over the file content with the watermark
line itself stripped, using a shared secret from the IQRA_WATERMARK_SECRET
environment variable (or empty for local dry-runs). This file is intended
to be invisible to readers but verifiable by CI: any out-of-band edit to
a signed skill will break its signature and surface as an annotation.

Modes:
  --verify           Verify every signed MD under skills/. Files without
                     a signature are skipped (phased rollout). Exit 1 if
                     any signature is present but invalid.
  --sign FILE        Compute and embed a signature on a single file.
  --sign-all         Sign every MD under skills/ that does not already
                     carry a valid signature. Useful for bootstrapping.
  --strict           When combined with --verify, treat unsigned files
                     as a violation as well. Off by default so the
                     workflow can be merged before files are signed.

Exit codes: 0 on success, 1 on any verification failure.
"""

from __future__ import annotations

import argparse
import hashlib
import hmac
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"

SIGNATURE_RE = re.compile(
    r"^<!--\s*@iqra_signature:\s*sha256=([0-9a-f]{64})\s*-->\s*$",
    re.MULTILINE,
)


def _secret() -> bytes:
    return os.environ.get("IQRA_WATERMARK_SECRET", "").encode("utf-8")


def _strip_signature(text: str) -> tuple[str, str | None]:
    """
    Return the file content with any signature line removed, plus the
    extracted hex signature (or None). The signature is expected to be the
    trailing block of the file, but we tolerate trailing whitespace.
    """
    match = SIGNATURE_RE.search(text)
    if not match:
        return text, None
    sig = match.group(1)
    # Remove the matched line and any extra trailing newlines so the
    # canonicalised payload is stable regardless of how the comment was
    # appended.
    stripped = SIGNATURE_RE.sub("", text).rstrip() + "\n"
    return stripped, sig


def _compute(text: str) -> str:
    return hmac.new(_secret(), text.encode("utf-8"), hashlib.sha256).hexdigest()


def _annotate(level: str, msg: str, file: Path | None = None) -> None:
    if os.environ.get("GITHUB_ACTIONS") == "true":
        if file is not None:
            try:
                rel = file.relative_to(ROOT)
            except ValueError:
                rel = file
            print(f"::{level} file={rel}::{msg}")
        else:
            print(f"::{level}::{msg}")
    else:
        marker = {"error": "X", "warning": "!", "notice": "i"}.get(level, "-")
        suffix = f" ({file})" if file else ""
        print(f"[{marker}] {msg}{suffix}")


def sign_file(path: Path) -> bool:
    """Sign a single file. Returns True if the file was modified."""
    text = path.read_text(encoding="utf-8")
    stripped, existing = _strip_signature(text)
    new_sig = _compute(stripped)
    if existing == new_sig:
        return False
    new_text = stripped + f"<!-- @iqra_signature: sha256={new_sig} -->\n"
    path.write_text(new_text, encoding="utf-8")
    return True


def verify_file(path: Path, strict: bool) -> tuple[bool, str]:
    """
    Verify a single file. Returns (ok, status) where status is one of
    "valid", "unsigned", "tampered", or "empty-secret".
    """
    text = path.read_text(encoding="utf-8")
    stripped, existing = _strip_signature(text)
    if existing is None:
        return (not strict, "unsigned")
    if not _secret():
        # Without a secret we cannot actually verify; treat as advisory.
        return (True, "empty-secret")
    expected = _compute(stripped)
    if hmac.compare_digest(expected, existing):
        return (True, "valid")
    return (False, "tampered")


def cmd_verify(strict: bool) -> int:
    failures = 0
    unsigned = 0
    valid = 0
    for md in sorted(SKILLS_DIR.glob("*.md")):
        ok, status = verify_file(md, strict)
        if status == "valid":
            valid += 1
        elif status == "unsigned":
            unsigned += 1
            if strict:
                _annotate("error", "skill MD is unsigned", md)
                failures += 1
        elif status == "tampered":
            _annotate("error", "watermark signature does not match content", md)
            failures += 1
        elif status == "empty-secret":
            # No secret available; just count as unsigned-equivalent.
            unsigned += 1
    if failures:
        _annotate("error", f"Watermark: {failures} violation(s) found")
        return 1
    print(f"Watermark: OK — {valid} signed, {unsigned} unsigned.")
    return 0


def cmd_sign(target: Path) -> int:
    if not _secret():
        _annotate("error", "IQRA_WATERMARK_SECRET is not set; refusing to sign")
        return 1
    if not target.is_file():
        _annotate("error", f"not a file: {target}")
        return 1
    changed = sign_file(target)
    print(f"Watermark: {'signed' if changed else 'unchanged'} {target.name}")
    return 0


def cmd_sign_all() -> int:
    if not _secret():
        _annotate("error", "IQRA_WATERMARK_SECRET is not set; refusing to sign")
        return 1
    changed = 0
    for md in sorted(SKILLS_DIR.glob("*.md")):
        if sign_file(md):
            changed += 1
    print(f"Watermark: signed/refreshed {changed} file(s).")
    # Expose count for downstream workflow steps.
    gh_output = os.environ.get("GITHUB_OUTPUT")
    if gh_output:
        try:
            with open(gh_output, "a", encoding="utf-8") as fh:
                fh.write(f"signed_count={changed}\n")
        except OSError:
            pass
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Skill watermark tool")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--verify", action="store_true", help="Verify all skill signatures")
    group.add_argument("--sign", metavar="FILE", help="Sign a single MD file")
    group.add_argument("--sign-all", action="store_true", help="Sign every skill MD")
    parser.add_argument("--strict", action="store_true", help="With --verify, treat unsigned files as failures")
    args = parser.parse_args()

    if args.verify:
        return cmd_verify(args.strict)
    if args.sign:
        return cmd_sign(Path(args.sign).resolve())
    if args.sign_all:
        return cmd_sign_all()
    return 0


if __name__ == "__main__":
    sys.exit(main())
