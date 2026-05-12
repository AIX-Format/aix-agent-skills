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
    """
    Emit a GitHub Actions annotation when running inside Actions; otherwise print a human-readable log marker.
    
    Parameters:
        level (str): Annotation level such as "error", "warning", or "notice". Unknown levels are allowed and will use a generic marker.
        msg (str): The message text to include in the annotation or log.
        file (Path | None): Optional path related to the message. When running under GitHub Actions, the path will be converted to a repository-relative path when possible and included in the annotation; otherwise it is appended to the human-readable log output.
    """
    if os.environ.get("GITHUB_ACTIONS") == "true":
        # Workflow command syntax requires no space before the closing `::`
        # when there is no metadata; when a file is included it goes
        # between a single space and the closing `::`.
        # See https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/workflow-commands-for-github-actions
        if file is not None:
            try:
                rel = file.relative_to(ROOT)
            except ValueError:
                rel = file
            print(f"::{level} file={rel}::{msg}")
        else:
            print(f"::{level}::{msg}")
    else:
        marker = {"error": "❌", "warning": "⚠️ ", "notice": "ℹ️ "}.get(level, "•")
        suffix = f" ({file})" if file else ""
        print(f"{marker} {msg}{suffix}")


def load_manifest() -> dict:
    """
    Load and parse the repository's skills.json manifest.
    
    Reads SKILLS_JSON as UTF-8 and returns the decoded JSON object. If the file is missing or contains invalid JSON, emits an error annotation and terminates the process with exit code 1.
    
    Returns:
        dict: The parsed JSON object from skills.json.
    """
    if not SKILLS_JSON.exists():
        annotate("error", f"skills.json not found at {SKILLS_JSON}")
        sys.exit(1)
    try:
        return json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        annotate("error", f"skills.json is not valid JSON: {exc}", SKILLS_JSON)
        sys.exit(1)


def check_top_level(data: dict, errors: list[str]) -> None:
    """
    Validate the top-level structure of a parsed skills.json manifest and record any schema violations.
    
    Checks that the manifest is a JSON object, that it contains a top-level "skills" key, and that "skills" is a list when present. Appends human-readable error messages to `errors` for each detected violation.
    
    Parameters:
        data (dict): Parsed JSON value from skills.json.
        errors (list[str]): Mutable list to which validation error messages will be appended.
    """
    if not isinstance(data, dict):
        errors.append("skills.json top-level must be a JSON object")
        return
    if "skills" not in data:
        errors.append("skills.json must contain a 'skills' array")
    elif not isinstance(data["skills"], list):
        errors.append("'skills' must be a list")


def check_entries(data: dict, errors: list[str]) -> None:
    """
    Validate each entry in the manifest's "skills" list and append human-readable error messages to `errors`.
    
    Per-entry validations include presence of required fields ("name", "description", "file"), that "name" and "description" are non-empty strings, that "name" matches the kebab-case pattern, that skill names and referenced file paths are unique across the manifest, that "file" is under `skills/` and ends with `.md`, and that the referenced file exists on disk. Each detected problem is added to `errors` with an index-aware context (e.g., `skills[0]`).
    
    Parameters:
        data (dict): Parsed manifest object; expected to contain a "skills" list of entries.
        errors (list[str]): Mutable list that will be appended with descriptive error strings for any violations.
    """
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

        # Validate name shape, only inserting into the dedup set when it is
        # a non-empty string; otherwise a list/dict `name` would crash the
        # set operation with TypeError on unhashable types.
        name_is_valid_str = isinstance(name, str) and name.strip() != ""
        if not name_is_valid_str:
            errors.append(f"{ctx}: 'name' must be a non-empty string")
        elif not is_valid_skill_name(name):
            errors.append(
                f"{ctx} ({name}): name must be kebab-case "
                f"(a-z0-9, dash-separated) or `_` + snake_case for internal skills"
            )
        if name_is_valid_str:
            if name in seen_names:
                errors.append(f"{ctx} ({name}): duplicate skill name")
            seen_names.add(name)

        if not isinstance(desc, str) or not desc.strip():
            errors.append(f"{ctx} ({name}): 'description' must be a non-empty string")

        # Same guard for file_path: must be a non-empty string before
        # joining or set-inserting.
        file_is_valid_str = isinstance(file_path, str) and file_path.strip() != ""
        if not file_is_valid_str:
            errors.append(f"{ctx} ({name}): 'file' must be a non-empty string")
            continue

        # When we have a valid name, the file path must match exactly
        # `skills/<name>.md`. Swapped references (e.g. two entries pointing
        # at the same MD) silently corrupt the marketplace; enforce strict
        # equality so they are caught here.
        if name_is_valid_str:
            expected_file = f"skills/{name}.md"
            if file_path != expected_file:
                errors.append(
                    f"{ctx} ({name}): 'file' must equal {expected_file!r}, "
                    f"got {file_path!r}"
                )
        elif not file_path.startswith("skills/") or not file_path.endswith(".md"):
            errors.append(
                f"{ctx}: 'file' must be under skills/ and end with .md, "
                f"got {file_path!r}"
            )

        if file_path in seen_files:
            errors.append(f"{ctx} ({name}): duplicate file path {file_path!r}")
        seen_files.add(file_path)
        abs_path = ROOT / file_path
        if not abs_path.is_file():
            errors.append(f"{ctx} ({name}): referenced file does not exist on disk: {file_path}")


def check_orphans(data: dict, errors: list[str]) -> set[str]:
    """
    Identify Markdown files in the skills directory that are not registered in the manifest.
    
    Parameters:
        data (dict): Parsed manifest (expected to contain a "skills" list of entry objects).
        errors (list[str]): Mutable list to which an error message is appended for each orphan file found.
    
    Returns:
        orphans (set[str]): Set of filename stems (without extension) for markdown files present under `skills/` but not listed in `data["skills"]`.
    """
    if not SKILLS_DIR.exists():
        return set()
    on_disk = {p.stem for p in SKILLS_DIR.glob("*.md")}
    # Guard against non-string / unhashable name fields; malformed entries
    # are already flagged by check_entries, so silently dropping them here
    # is correct.
    in_manifest = {
        s["name"]
        for s in data.get("skills", [])
        if isinstance(s, dict)
        and isinstance(s.get("name"), str)
        and s["name"].strip()
    }
    orphans = on_disk - in_manifest
    for orphan in sorted(orphans):
        errors.append(
            f"Orphan MD file: skills/{orphan}.md is on disk but not registered in skills.json"
        )
    return orphans


def check_md_headings(errors: list[str]) -> None:
    """
    Validate that each Markdown file in the `skills/` directory begins with a level-1 heading.
    
    Checks every `*.md` file under SKILLS_DIR (sorted). For each file, ensures the file is valid UTF-8, skips an optional YAML frontmatter block delimited by `---` on the first line, and verifies that the first non-empty line after that frontmatter starts with `# ` (a level-1 heading). For any violation, appends a descriptive message to `errors`.
    
    Parameters:
        errors (list[str]): Mutable list to which human-readable error messages will be appended (one per violation).
    """
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
    """
    Add manifest entries for orphan Markdown files and write the updated manifest.
    
    For each name in `orphans` (sorted), reads the corresponding `skills/<name>.md` file and extracts the first non-empty line (stripping a leading `# ` if present) to use as the entry's `description` (truncated to 160 characters). If the file cannot be read or no non-empty line is found, uses the stem as the description fallback or a descriptive fallback string. Appends a dict with `name`, `description`, and `file` to `data["skills"]` (creating the list if missing), emits a notice annotation for each auto-registered orphan, and writes the updated manifest back to `SKILLS_JSON` using UTF-8, JSON indentation, and a trailing newline.
    
    Parameters:
        orphans (set[str]): Set of Markdown filename stems (without `.md`) to auto-register.
        data (dict): Parsed manifest object to be mutated in-place; the function ensures `data["skills"]` exists and appends new entries.
    """
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
    """
    Validate the skills manifest and corresponding Markdown files, optionally auto-registering orphan MD files.
    
    Performs a series of structural checks on SKILLS_JSON and files in SKILLS_DIR, emits annotations for any violations, and can auto-add orphan Markdown files to the manifest when run with the `--fix` flag.
    
    Returns:
        int: `0` on success (no violations, or after successfully auto-registering orphans with `--fix`), `1` if one or more validation violations were found.
    """
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
            # Only the orphan-related errors are resolved by autofix; any
            # other validation failures (bad headings, duplicates, etc.)
            # must still cause a non-zero exit so the CI job fails loudly.
            errors = [e for e in errors if not e.startswith("Orphan MD file:")]

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
