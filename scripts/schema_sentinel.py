#!/usr/bin/env python3
"""
Schema Sentinel — guardian of the skills marketplace structural invariants.

Runs on every push and pull request. Verifies that:

  1. `skills.json` is well-formed JSON with the expected top-level shape.
  2. Every entry in `skills.json` has `name`, `description`, `file` and the
     `file` path exists on disk.
  3. Every `skills/*.md` file is registered in `skills.json` (no orphans).
  4. Every `name` is unique, kebab-case, non-empty.
  5. Every `file` is unique and points under `skills/`.
  6. Every MD file has a level-1 heading on its first non-empty line.

Exit code 0 on success; 1 on any failure. Failures print as `::error::`
GitHub annotations so they surface inline on the PR's Files Changed tab.

Auto-fix mode (`--fix`): when an orphan MD is detected, this script will
append a stub entry to `skills.json`. Intended for use by a separate
"sentinel autofix" workflow that opens a follow-up PR; the default mode
remains strict (no writes).
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
SKILLS_DIR = ROOT / "skills"

# Public skill names are strict kebab-case (a-z0-9 with dash separators).
# Names that start with a leading underscore are treated as internal/test-only
# and may use snake_case (e.g. `_test_tool`); the prefix is the opt-out marker.
KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INTERNAL_RE = re.compile(r"^_[a-z0-9]+(?:_[a-z0-9]+)*$")


def is_valid_skill_name(name: str) -> bool:
    return bool(KEBAB_RE.match(name) or INTERNAL_RE.match(name))


def annotate(level: str, msg: str, file: Path | None = None) -> None:
    """Emit a GitHub Actions annotation if running under Actions, otherwise plain log."""
    if os.environ.get("GITHUB_ACTIONS") == "true":
        prefix = f"::{level} "
        if file is not None:
            try:
                rel = file.relative_to(ROOT)
            except ValueError:
                rel = file
            prefix += f"file={rel}::"
        else:
            prefix += "::"
        print(f"{prefix}{msg}")
    else:
        marker = {"error": "❌", "warning": "⚠️ ", "notice": "ℹ️ "}.get(level, "•")
        suffix = f" ({file})" if file else ""
        print(f"{marker} {msg}{suffix}")


def load_manifest() -> dict:
    if not SKILLS_JSON.exists():
        annotate("error", f"skills.json not found at {SKILLS_JSON}")
        sys.exit(1)
    try:
        return json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        annotate("error", f"skills.json is not valid JSON: {exc}", SKILLS_JSON)
        sys.exit(1)


def check_top_level(data: dict, errors: list[str]) -> None:
    if not isinstance(data, dict):
        errors.append("skills.json top-level must be a JSON object")
        return
    if "skills" not in data:
        errors.append("skills.json must contain a 'skills' array")
    elif not isinstance(data["skills"], list):
        errors.append("'skills' must be a list")


def check_entries(data: dict, errors: list[str]) -> None:
    seen_names: set[str] = set()
    seen_files: set[str] = set()
    for i, entry in enumerate(data.get("skills", [])):
        ctx = f"skills[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{ctx}: must be an object, got {type(entry).__name__}")
            continue
        for required in ("name", "description", "file"):
            if required not in entry:
                errors.append(f"{ctx}: missing required field '{required}'")
        name = entry.get("name", "")
        desc = entry.get("description", "")
        file_path = entry.get("file", "")
        if not isinstance(name, str) or not name.strip():
            errors.append(f"{ctx}: 'name' must be a non-empty string")
        elif not is_valid_skill_name(name):
            errors.append(
                f"{ctx} ({name}): name must be kebab-case "
                f"(a-z0-9, dash-separated) or `_` + snake_case for internal skills"
            )
        if name in seen_names:
            errors.append(f"{ctx} ({name}): duplicate skill name")
        seen_names.add(name)
        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{ctx} ({name}): 'description' must be a non-empty string")
        if not isinstance(file_path, str) or not file_path.strip():
            errors.append(f"{ctx} ({name}): 'file' must be a non-empty string")
            continue
        if not file_path.startswith("skills/") or not file_path.endswith(".md"):
            errors.append(f"{ctx} ({name}): 'file' must be 'skills/<name>.md' form, got {file_path!r}")
        if file_path in seen_files:
            errors.append(f"{ctx} ({name}): duplicate file path {file_path!r}")
        seen_files.add(file_path)
        abs_path = ROOT / file_path
        if not abs_path.is_file():
            errors.append(f"{ctx} ({name}): referenced file does not exist on disk: {file_path}")


def check_orphans(data: dict, errors: list[str]) -> set[str]:
    """Return the set of orphan stems so callers (e.g. --fix) can act on them."""
    if not SKILLS_DIR.exists():
        return set()
    on_disk = {p.stem for p in SKILLS_DIR.glob("*.md")}
    in_manifest = {s.get("name", "") for s in data.get("skills", []) if isinstance(s, dict)}
    orphans = on_disk - in_manifest
    for orphan in sorted(orphans):
        errors.append(
            f"Orphan MD file: skills/{orphan}.md is on disk but not registered in skills.json"
        )
    return orphans


def check_md_headings(errors: list[str]) -> None:
    if not SKILLS_DIR.exists():
        return
    for md in sorted(SKILLS_DIR.glob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            errors.append(f"{md.name}: not valid UTF-8")
            continue
        lines = text.splitlines()
        # Skip YAML frontmatter delimited by `---` markers
        i = 0
        if lines and lines[0].strip() == "---":
            i = 1
            while i < len(lines) and lines[i].strip() != "---":
                i += 1
            i += 1  # consume the closing `---`
        first_nonempty = next((ln for ln in lines[i:] if ln.strip()), "")
        if not first_nonempty.startswith("# "):
            errors.append(f"{md.name}: first non-empty line (after optional YAML frontmatter) must be a level-1 heading (# Title)")


def autofix_orphans(orphans: set[str], data: dict) -> None:
    if not orphans:
        return
    for orphan in sorted(orphans):
        md_path = SKILLS_DIR / f"{orphan}.md"
        first_line = ""
        try:
            for ln in md_path.read_text(encoding="utf-8").splitlines():
                if ln.strip():
                    first_line = ln.lstrip("# ").strip()
                    break
        except Exception:
            first_line = orphan
        data.setdefault("skills", []).append({
            "name": orphan,
            "description": first_line[:160] or f"Auto-registered orphan: {orphan}",
            "file": f"skills/{orphan}.md",
        })
        annotate("notice", f"Auto-registered orphan {orphan}")
    SKILLS_JSON.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Skills marketplace Schema Sentinel")
    parser.add_argument("--fix", action="store_true", help="Auto-register orphan MDs in skills.json")
    args = parser.parse_args()

    data = load_manifest()
    errors: list[str] = []
    check_top_level(data, errors)
    if not errors:
        check_entries(data, errors)
        orphans = check_orphans(data, errors)
        check_md_headings(errors)
        if args.fix and orphans:
            autofix_orphans(orphans, data)
            return 0

    if errors:
        for err in errors:
            annotate("error", err)
        annotate("error", f"Schema Sentinel: {len(errors)} violation(s) found")
        return 1

    skill_count = len(data.get("skills", []))
    md_count = len(list(SKILLS_DIR.glob("*.md"))) if SKILLS_DIR.exists() else 0
    print(f"Schema Sentinel: OK — {skill_count} skills registered, {md_count} MDs on disk, no violations.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
