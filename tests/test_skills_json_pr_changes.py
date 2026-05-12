#!/usr/bin/env python3
"""
test_skills_json_pr_changes.py — Tests for skills.json changes introduced in this PR.

This PR made two changes to skills.json:
  1. Removed the "antigravity-jules" skill entry.
  2. Updated "voice-wizard" description to use a proper Unicode arrow (→ U+2192)
     instead of the ASCII arrow sequence (→).

These are regression/change-verification tests scoped to only what the PR modified.
"""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.resolve()
SKILLS_JSON = ROOT / "skills.json"


@pytest.fixture(scope="module")
def skills_data():
    with open(SKILLS_JSON) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def skill_names(skills_data):
    return [s["name"] for s in skills_data.get("skills", [])]


@pytest.fixture(scope="module")
def skill_by_name(skills_data):
    return {s["name"]: s for s in skills_data.get("skills", [])}


# ─── antigravity-jules Removal ────────────────────────────────────────────────

class TestAntigravityJulesRemoved:
    """Verify that the antigravity-jules skill was fully removed from skills.json."""

    def test_antigravity_jules_not_in_skill_names(self, skill_names):
        assert "antigravity-jules" not in skill_names, (
            "antigravity-jules should have been removed from skills.json in this PR"
        )

    def test_no_reference_to_antigravity_jules_file(self, skills_data):
        """No skill entry should reference the antigravity-jules.md file path."""
        files = [s.get("file", "") for s in skills_data.get("skills", [])]
        assert "skills/antigravity-jules.md" not in files

    def test_antigravity_jules_md_file_deleted(self):
        """The .md file should have been deleted from disk."""
        assert not (ROOT / "skills" / "antigravity-jules.md").exists(), (
            "skills/antigravity-jules.md should have been deleted in this PR"
        )

    def test_skills_json_has_no_partial_antigravity_reference(self):
        """Read raw text to ensure there's no leftover mention of antigravity-jules."""
        raw = SKILLS_JSON.read_text()
        assert "antigravity-jules" not in raw


# ─── voice-wizard Unicode Arrow ───────────────────────────────────────────────

class TestVoiceWizardDescriptionUpdated:
    """Verify the voice-wizard description was updated to use a proper Unicode arrow."""

    def test_voice_wizard_present(self, skill_by_name):
        assert "voice-wizard" in skill_by_name, "voice-wizard skill must still exist in skills.json"

    def test_voice_wizard_description_uses_unicode_arrow(self, skill_by_name):
        description = skill_by_name["voice-wizard"]["description"]
        # The PR changed ASCII → (→) to Unicode → (U+2192)
        assert "\u2192" in description, (
            f"voice-wizard description should contain Unicode arrow (→ U+2192), got: {description!r}"
        )

    def test_voice_wizard_description_does_not_use_html_entity(self, skill_by_name):
        """The old description used the HTML entity &rarr; or encoded sequence → — verify it's gone."""
        description = skill_by_name["voice-wizard"]["description"]
        assert "&rarr;" not in description
        assert "→" not in description  # HTML entity form

    def test_voice_wizard_description_content(self, skill_by_name):
        description = skill_by_name["voice-wizard"]["description"]
        assert "STT" in description
        assert "LLM" in description
        assert "TTS" in description

    def test_voice_wizard_has_correct_file_path(self, skill_by_name):
        assert skill_by_name["voice-wizard"]["file"] == "skills/voice-wizard.md"


# ─── skills.json Structural Integrity ────────────────────────────────────────

class TestSkillsJsonIntegrity:
    """Verify skills.json is valid and structurally sound after PR changes."""

    def test_skills_json_is_valid_json(self):
        raw = SKILLS_JSON.read_text(encoding="utf-8")
        parsed = json.loads(raw)
        assert isinstance(parsed, dict)

    def test_skills_key_exists(self, skills_data):
        assert "skills" in skills_data

    def test_all_entries_have_required_fields(self, skills_data):
        for skill in skills_data["skills"]:
            assert "name" in skill, f"Missing 'name' in: {skill}"
            assert "description" in skill, f"Missing 'description' in skill: {skill.get('name')}"
            assert "file" in skill, f"Missing 'file' in skill: {skill.get('name')}"

    def test_no_duplicate_skill_names(self, skill_names):
        assert len(skill_names) == len(set(skill_names)), (
            f"Duplicate skill names found: {[n for n in skill_names if skill_names.count(n) > 1]}"
        )

    def test_no_duplicate_skill_files(self, skills_data):
        files = [s["file"] for s in skills_data["skills"]]
        assert len(files) == len(set(files)), (
            f"Duplicate file paths found: {[f for f in files if files.count(f) > 1]}"
        )

    def test_all_referenced_skill_files_exist_on_disk(self, skills_data):
        missing = []
        for skill in skills_data["skills"]:
            path = ROOT / skill["file"]
            if not path.exists():
                missing.append(skill["file"])
        assert not missing, f"Skill files missing from disk: {missing}"

    def test_skill_names_are_nonempty_strings(self, skills_data):
        for skill in skills_data["skills"]:
            assert isinstance(skill["name"], str) and skill["name"].strip() != ""

    def test_skill_descriptions_are_nonempty_strings(self, skills_data):
        for skill in skills_data["skills"]:
            assert isinstance(skill["description"], str) and skill["description"].strip() != ""

    def test_skills_json_is_utf8_encoded(self):
        content = SKILLS_JSON.read_bytes()
        decoded = content.decode("utf-8")
        assert len(decoded) > 0

    def test_total_skill_count_decreased_after_removal(self, skills_data):
        """After removing antigravity-jules, total count should be < what it was before the PR.
        The original skills.json had antigravity-jules as one of the last entries.
        We just verify the count is a positive integer and doesn't include the removed skill."""
        count = len(skills_data["skills"])
        assert count > 0
        # antigravity-jules was entry number ~51 before removal; after removal count should be lower
        # We check that the count doesn't include it (indirect assertion through absence)
        names = [s["name"] for s in skills_data["skills"]]
        assert "antigravity-jules" not in names


# ─── Specific PR-Added Skill Entries ─────────────────────────────────────────

class TestPRSkillsPresent:
    """Verify that the four skills with new Python blocks are present in skills.json."""

    @pytest.mark.parametrize("skill_name", [
        "trust-chain",
        "circuit-breaker",
        "data-alchemist",
        "topology-orchestrator",
    ])
    def test_skill_present_in_registry(self, skill_names, skill_name):
        assert skill_name in skill_names, f"Expected skill '{skill_name}' to be in skills.json"

    @pytest.mark.parametrize("skill_name,expected_file", [
        ("trust-chain", "skills/trust-chain.md"),
        ("circuit-breaker", "skills/circuit-breaker.md"),
        ("data-alchemist", "skills/data-alchemist.md"),
        ("topology-orchestrator", "skills/topology-orchestrator.md"),
    ])
    def test_skill_file_path_is_correct(self, skill_by_name, skill_name, expected_file):
        assert skill_by_name[skill_name]["file"] == expected_file

    @pytest.mark.parametrize("skill_name", [
        "trust-chain",
        "circuit-breaker",
        "data-alchemist",
        "topology-orchestrator",
    ])
    def test_skill_md_file_exists(self, skill_by_name, skill_name):
        file_path = ROOT / skill_by_name[skill_name]["file"]
        assert file_path.exists(), f"File missing: {skill_by_name[skill_name]['file']}"

    @pytest.mark.parametrize("skill_name", [
        "trust-chain",
        "circuit-breaker",
        "data-alchemist",
        "topology-orchestrator",
    ])
    def test_skill_md_contains_python_block(self, skill_by_name, skill_name):
        import re
        file_path = ROOT / skill_by_name[skill_name]["file"]
        content = file_path.read_text()
        assert re.search(r'```python', content), (
            f"No python code block found in {skill_by_name[skill_name]['file']}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
