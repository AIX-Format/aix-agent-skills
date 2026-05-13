"""
Tests for scripts/schema_sentinel.py

Focuses on the change in `autofix_orphans`: the exception handler was
broadened from `except (OSError, UnicodeDecodeError):` to `except Exception:`,
meaning any exception raised while reading an orphan's .md file is now caught
and falls back to using the orphan name as the description.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "schema_sentinel.py"


def _import_schema_sentinel():
    spec = importlib.util.spec_from_file_location("schema_sentinel", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["schema_sentinel"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


ss = _import_schema_sentinel()


# ─── autofix_orphans ─────────────────────────────────────────────────────────


class TestAutofixOrphans:
    """
    Tests for autofix_orphans(), exercising the broadened `except Exception:`
    handler introduced in this PR. All tests patch SKILLS_DIR and SKILLS_JSON
    to use a tmp_path so no real files are touched.
    """

    def _setup(self, tmp_path, monkeypatch):
        """
        Point SKILLS_DIR and SKILLS_JSON at tmp_path subdirs and return
        (skills_dir, skills_json_path).
        """
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skills_json = tmp_path / "skills.json"
        monkeypatch.setattr(ss, "SKILLS_DIR", skills_dir)
        monkeypatch.setattr(ss, "SKILLS_JSON", skills_json)
        return skills_dir, skills_json

    # ── happy path ──────────────────────────────────────────────────────────

    def test_reads_description_from_md_file(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        (skills_dir / "my-skill.md").write_text("# My Skill\nSome body.", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"my-skill"}, data)
        entry = data["skills"][0]
        assert entry["name"] == "my-skill"
        assert entry["description"] == "My Skill"

    def test_strips_leading_hash_from_description(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        (skills_dir / "cool-tool.md").write_text("# Cool Tool\n", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"cool-tool"}, data)
        assert data["skills"][0]["description"] == "Cool Tool"

    def test_file_field_set_correctly(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        (skills_dir / "my-skill.md").write_text("# My Skill", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"my-skill"}, data)
        assert data["skills"][0]["file"] == "skills/my-skill.md"

    def test_writes_updated_skills_json(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        (skills_dir / "alpha.md").write_text("# Alpha Skill\n", encoding="utf-8")
        data: dict = {"skills": []}
        ss.autofix_orphans({"alpha"}, data)
        saved = json.loads(skills_json.read_text(encoding="utf-8"))
        assert any(e["name"] == "alpha" for e in saved["skills"])

    def test_no_orphans_does_nothing(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        data: dict = {"skills": []}
        ss.autofix_orphans(set(), data)
        # skills.json should not have been written
        assert not skills_json.exists()

    def test_multiple_orphans_all_registered(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        for name in ("alpha", "beta", "gamma"):
            (skills_dir / f"{name}.md").write_text(f"# {name.title()}\n", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"alpha", "beta", "gamma"}, data)
        names = [e["name"] for e in data["skills"]]
        assert sorted(names) == ["alpha", "beta", "gamma"]

    def test_description_truncated_at_160_chars(self, tmp_path, monkeypatch):
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        long_title = "A" * 200
        (skills_dir / "verbose.md").write_text(f"# {long_title}\n", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"verbose"}, data)
        assert len(data["skills"][0]["description"]) <= 160

    # ── exception-handling (the changed line) ───────────────────────────────

    def test_oserror_falls_back_to_orphan_name(self, tmp_path, monkeypatch):
        """OSError was caught before; still caught with `except Exception:`."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        # Do NOT create the .md file — reading it raises FileNotFoundError (OSError subclass).
        data: dict = {}
        ss.autofix_orphans({"missing-skill"}, data)
        entry = data["skills"][0]
        assert entry["name"] == "missing-skill"
        # description falls back to the orphan name itself
        assert entry["description"] == "missing-skill"

    def test_unicode_decode_error_falls_back_to_orphan_name(self, tmp_path, monkeypatch):
        """UnicodeDecodeError was caught before; still caught."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        # Write binary garbage that is not valid UTF-8
        (skills_dir / "bad-encoding.md").write_bytes(b"\xff\xfe invalid utf-8 \x80\x81")
        data: dict = {}
        ss.autofix_orphans({"bad-encoding"}, data)
        entry = data["skills"][0]
        assert entry["name"] == "bad-encoding"
        assert entry["description"] == "bad-encoding"

    def test_permission_error_falls_back_to_orphan_name(self, tmp_path, monkeypatch):
        """PermissionError was NOT caught before; now caught by `except Exception:`."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        md = skills_dir / "locked.md"
        md.write_text("# Locked\n", encoding="utf-8")

        original_read_text = Path.read_text

        def raising_read_text(self, *args, **kwargs):
            if self == md:
                raise PermissionError("access denied")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", raising_read_text)
        data: dict = {}
        # Should not raise; PermissionError is now swallowed.
        ss.autofix_orphans({"locked"}, data)
        entry = data["skills"][0]
        assert entry["description"] == "locked"

    def test_arbitrary_exception_falls_back_to_orphan_name(self, tmp_path, monkeypatch):
        """Any exception during read is now caught (regression guard)."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        md = skills_dir / "exploding.md"
        md.write_text("# Exploding\n", encoding="utf-8")

        original_read_text = Path.read_text

        def raising_read_text(self, *args, **kwargs):
            if self == md:
                raise ValueError("unexpected parser state")
            return original_read_text(self, *args, **kwargs)

        monkeypatch.setattr(Path, "read_text", raising_read_text)
        data: dict = {}
        ss.autofix_orphans({"exploding"}, data)
        entry = data["skills"][0]
        assert entry["description"] == "exploding"

    def test_fallback_description_when_empty_md(self, tmp_path, monkeypatch):
        """Empty .md file: first_line is '' → falls back to 'Auto-registered orphan: <name>'."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        (skills_dir / "empty-skill.md").write_text("", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"empty-skill"}, data)
        entry = data["skills"][0]
        assert entry["description"] == "Auto-registered orphan: empty-skill"

    def test_orphans_processed_in_sorted_order(self, tmp_path, monkeypatch):
        """Orphans are sorted before processing, so output order is deterministic."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        for name in ("zebra", "apple", "mango"):
            (skills_dir / f"{name}.md").write_text(f"# {name}\n", encoding="utf-8")
        data: dict = {}
        ss.autofix_orphans({"zebra", "apple", "mango"}, data)
        names = [e["name"] for e in data["skills"]]
        assert names == sorted(names)

    def test_existing_skills_list_is_extended(self, tmp_path, monkeypatch):
        """autofix_orphans appends to an existing skills list rather than replacing it."""
        skills_dir, skills_json = self._setup(tmp_path, monkeypatch)
        (skills_dir / "new-skill.md").write_text("# New Skill\n", encoding="utf-8")
        pre_existing = {"name": "old-skill", "description": "Old", "file": "skills/old-skill.md"}
        data: dict = {"skills": [pre_existing]}
        ss.autofix_orphans({"new-skill"}, data)
        names = [e["name"] for e in data["skills"]]
        assert "old-skill" in names
        assert "new-skill" in names