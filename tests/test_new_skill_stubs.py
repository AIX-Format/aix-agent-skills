"""
Tests for skills added in this PR.

This PR:
  1. Added 17 new skill entries to skills.json with non-standard name formats
     (UPPERCASE, snake_case, PascalCase) whose file paths use kebab-case.
  2. Added 17 new skill stub markdown files under skills/.
  3. Removed the "tier" field from 8 existing skill entries.
  4. Updated the README.md dashboard (total count 58→75, UNCLASSIFIED 7→24).

Covers:
  - All 17 new skill entries are registered in skills.json.
  - Each entry has the required fields: name, description, file.
  - Each entry's file reference resolves to an existing .md on disk.
  - New skill file paths use kebab-case regardless of the skill name format.
  - Skills whose "tier" was removed in this PR no longer carry that field.
  - All 17 new stub .md files exist on disk.
  - Each stub .md contains the four required section headings.
  - Stubs that have a real purpose description (non-TODO) are verified.
  - README dashboard reflects the updated skill total (75) and UNCLASSIFIED count (24).
"""

from __future__ import annotations

import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_JSON_PATH = os.path.join(REPO_ROOT, "skills.json")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
README_PATH = os.path.join(REPO_ROOT, "README.md")

# ---------------------------------------------------------------------------
# Exact set of new skill entries added by this PR.
# Each tuple is (name_in_json, filename_on_disk).
# ---------------------------------------------------------------------------
NEW_SKILLS_IN_PR: list[tuple[str, str]] = [
    ("DATA_GUARDIAN", "data-guardian.md"),
    ("TOPOLOGICAL_CURIOSITY", "topological-curiosity.md"),
    ("compute_router", "compute-router.md"),
    ("damir_check", "damir-check.md"),
    ("memory_management", "memory-management.md"),
    ("opportunity_hunter", "opportunity-hunter.md"),
    ("pattern_validate", "pattern-validate.md"),
    ("quran_deep_analysis", "quran-deep-analysis.md"),
    ("quran_search", "quran-search.md"),
    ("sovereign_identity", "sovereign-identity.md"),
    ("sovereign_reasoning", "sovereign-reasoning.md"),
    ("trading_skill", "trading-skill.md"),
    ("SKILLS", "skills.md"),
    ("TrustChain", "trustchain.md"),
    ("CavemanSkill", "caveman-skill.md"),
    ("FatihaTopology", "fatiha-topology.md"),
    ("Go_Engine", "go-engine.md"),
]

# Skills whose "tier" field was removed in this PR.
SKILLS_WITH_TIER_REMOVED = {
    "local-journal",
    "community-support-layer",
    "multiverse-lab-pro",
    "shadow-exchange",
    "shadow-hospital",
    "topology-fork-engine",
    "_test_tool",
    "antigravity-jules",
}

# Required markdown section headings in every stub file.
REQUIRED_MD_SECTIONS = [
    "## Purpose",
    "## Constitutional Alignment",
    "## Operational Flow",
    "## Failure Modes",
]

# New skills that carry a meaningful (non-TODO) purpose description.
SKILLS_WITH_REAL_DESCRIPTION: dict[str, str] = {
    "TrustChain": "Immutable SHA-256 ledger for agent accountability",
    "CavemanSkill": "Basic foundational problem-solving skill, highly resilient",
    "FatihaTopology": "Mathematical and topological routing based on Quranic patterns",
    "Go_Engine": "Independent HTTP server and optimized execution engine",
}


def _load_skills_json() -> dict:
    with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def _skills_by_name() -> dict[str, dict]:
    data = _load_skills_json()
    return {s["name"]: s for s in data["skills"]}


def _read_readme() -> str:
    with open(README_PATH, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# 1. New skill entries registered in skills.json
# ---------------------------------------------------------------------------

class TestNewSkillsRegistered(unittest.TestCase):
    """All 17 new skill entries must be present in skills.json."""

    def setUp(self):
        self.by_name = _skills_by_name()

    def test_data_guardian_registered(self):
        self.assertIn("DATA_GUARDIAN", self.by_name)

    def test_topological_curiosity_registered(self):
        self.assertIn("TOPOLOGICAL_CURIOSITY", self.by_name)

    def test_compute_router_registered(self):
        self.assertIn("compute_router", self.by_name)

    def test_damir_check_registered(self):
        self.assertIn("damir_check", self.by_name)

    def test_memory_management_registered(self):
        self.assertIn("memory_management", self.by_name)

    def test_opportunity_hunter_registered(self):
        self.assertIn("opportunity_hunter", self.by_name)

    def test_pattern_validate_registered(self):
        self.assertIn("pattern_validate", self.by_name)

    def test_quran_deep_analysis_registered(self):
        self.assertIn("quran_deep_analysis", self.by_name)

    def test_quran_search_registered(self):
        self.assertIn("quran_search", self.by_name)

    def test_sovereign_identity_registered(self):
        self.assertIn("sovereign_identity", self.by_name)

    def test_sovereign_reasoning_registered(self):
        self.assertIn("sovereign_reasoning", self.by_name)

    def test_trading_skill_registered(self):
        self.assertIn("trading_skill", self.by_name)

    def test_skills_meta_registered(self):
        self.assertIn("SKILLS", self.by_name)

    def test_trustchain_registered(self):
        self.assertIn("TrustChain", self.by_name)

    def test_caveman_skill_registered(self):
        self.assertIn("CavemanSkill", self.by_name)

    def test_fatiha_topology_registered(self):
        self.assertIn("FatihaTopology", self.by_name)

    def test_go_engine_registered(self):
        self.assertIn("Go_Engine", self.by_name)

    def test_all_17_new_skills_present(self):
        """All new entries from the PR must be in the manifest."""
        missing = [
            name for name, _ in NEW_SKILLS_IN_PR if name not in self.by_name
        ]
        self.assertEqual(
            [], missing,
            f"New skill(s) missing from skills.json: {missing}",
        )


# ---------------------------------------------------------------------------
# 2. Required fields on new entries
# ---------------------------------------------------------------------------

class TestNewSkillEntryFields(unittest.TestCase):
    """Each new skill entry must have name, description, and file."""

    def setUp(self):
        self.by_name = _skills_by_name()

    def _entry(self, name: str) -> dict:
        self.assertIn(name, self.by_name, f"Skill '{name}' not in registry")
        return self.by_name[name]

    def test_each_new_skill_has_name(self):
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self._entry(name)
                self.assertIn("name", entry)
                self.assertEqual(entry["name"], name)

    def test_each_new_skill_has_description(self):
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self._entry(name)
                self.assertIn("description", entry)
                self.assertIsInstance(entry["description"], str)
                self.assertGreater(len(entry["description"]), 0)

    def test_each_new_skill_has_file(self):
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self._entry(name)
                self.assertIn("file", entry)
                self.assertIsInstance(entry["file"], str)
                self.assertGreater(len(entry["file"]), 0)

    def test_new_skills_have_no_extra_unknown_fields(self):
        """New skill entries may only carry name, description, file, and optionally tier."""
        allowed = {"name", "description", "file", "tier"}
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self._entry(name)
                extra = set(entry.keys()) - allowed
                self.assertEqual(set(), extra, f"Unexpected key(s) in '{name}': {extra}")

    def test_new_skills_have_no_tier_field(self):
        """The new stub entries in this PR were added without a 'tier' field."""
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self._entry(name)
                self.assertNotIn(
                    "tier", entry,
                    f"Skill '{name}' should not have a 'tier' field in this PR",
                )


# ---------------------------------------------------------------------------
# 3. File references resolve to existing .md files
# ---------------------------------------------------------------------------

class TestNewSkillFileReferences(unittest.TestCase):
    """Each new skill entry must point to an existing .md file."""

    def setUp(self):
        self.by_name = _skills_by_name()

    def test_each_new_skill_file_exists_on_disk(self):
        for name, expected_filename in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                if not entry:
                    self.skipTest(f"Skill '{name}' not in registry")
                full_path = os.path.join(REPO_ROOT, entry["file"])
                self.assertTrue(
                    os.path.isfile(full_path),
                    f"File '{entry['file']}' for skill '{name}' does not exist on disk",
                )

    def test_file_paths_use_skills_prefix(self):
        """All new skill file paths must start with 'skills/'."""
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                if not entry:
                    self.skipTest(f"Skill '{name}' not in registry")
                self.assertTrue(
                    entry["file"].startswith("skills/"),
                    f"File path for '{name}' must start with 'skills/', got '{entry['file']}'",
                )

    def test_file_paths_end_with_md(self):
        """All new skill file paths must end with '.md'."""
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                if not entry:
                    self.skipTest(f"Skill '{name}' not in registry")
                self.assertTrue(
                    entry["file"].endswith(".md"),
                    f"File path for '{name}' must end with '.md', got '{entry['file']}'",
                )

    def test_new_skills_use_kebab_case_filenames(self):
        """
        New skill names may be UPPERCASE, snake_case, or PascalCase,
        but their on-disk filenames must use kebab-case.
        This verifies the name→file mapping introduced in this PR.
        """
        kebab_re = re.compile(r"^skills/[a-z][a-z0-9-]*\.md$")
        for name, expected_filename in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                if not entry:
                    self.skipTest(f"Skill '{name}' not in registry")
                self.assertRegex(
                    entry["file"],
                    kebab_re,
                    f"File path for '{name}' must be kebab-case, got '{entry['file']}'",
                )

    def test_file_reference_matches_expected_filename(self):
        """Verify each new skill's file path matches the expected kebab filename."""
        for name, expected_filename in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                if not entry:
                    self.skipTest(f"Skill '{name}' not in registry")
                self.assertEqual(
                    entry["file"],
                    f"skills/{expected_filename}",
                    f"Skill '{name}' expected file 'skills/{expected_filename}', "
                    f"got '{entry['file']}'",
                )


# ---------------------------------------------------------------------------
# 4. Tier field removed from specific existing skills
# ---------------------------------------------------------------------------

class TestTierFieldRemoved(unittest.TestCase):
    """
    This PR removed the 'tier' field from 8 existing skill entries.
    These skills must still exist but must not have a 'tier' key.
    """

    def setUp(self):
        self.by_name = _skills_by_name()

    def test_skills_with_tier_removed_still_present(self):
        for name in SKILLS_WITH_TIER_REMOVED:
            with self.subTest(name=name):
                self.assertIn(
                    name, self.by_name,
                    f"Skill '{name}' was removed entirely (it should still exist, just without 'tier')",
                )

    def test_local_journal_has_no_tier(self):
        entry = self.by_name.get("local-journal", {})
        self.assertNotIn("tier", entry, "local-journal should not have 'tier' after this PR")

    def test_community_support_layer_has_no_tier(self):
        entry = self.by_name.get("community-support-layer", {})
        self.assertNotIn("tier", entry, "community-support-layer should not have 'tier' after this PR")

    def test_multiverse_lab_pro_has_no_tier(self):
        entry = self.by_name.get("multiverse-lab-pro", {})
        self.assertNotIn("tier", entry, "multiverse-lab-pro should not have 'tier' after this PR")

    def test_shadow_exchange_has_no_tier(self):
        entry = self.by_name.get("shadow-exchange", {})
        self.assertNotIn("tier", entry, "shadow-exchange should not have 'tier' after this PR")

    def test_shadow_hospital_has_no_tier(self):
        entry = self.by_name.get("shadow-hospital", {})
        self.assertNotIn("tier", entry, "shadow-hospital should not have 'tier' after this PR")

    def test_topology_fork_engine_has_no_tier(self):
        entry = self.by_name.get("topology-fork-engine", {})
        self.assertNotIn("tier", entry, "topology-fork-engine should not have 'tier' after this PR")

    def test_test_tool_has_no_tier(self):
        entry = self.by_name.get("_test_tool", {})
        self.assertNotIn("tier", entry, "_test_tool should not have 'tier' after this PR")

    def test_antigravity_jules_has_no_tier(self):
        entry = self.by_name.get("antigravity-jules", {})
        self.assertNotIn("tier", entry, "antigravity-jules should not have 'tier' after this PR")

    def test_skills_with_tier_still_have_required_fields(self):
        """After removing 'tier', the entries must still have name, description, file."""
        for name in SKILLS_WITH_TIER_REMOVED:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                for field in ("name", "description", "file"):
                    self.assertIn(field, entry, f"'{field}' missing from '{name}' after tier removal")

    def test_prompt_templates_retains_tier(self):
        """
        prompt-templates was NOT affected by tier removal in this PR —
        it still carries tier: BASIC_TOOL.
        """
        entry = self.by_name.get("prompt-templates", {})
        self.assertIn("tier", entry, "prompt-templates should still have 'tier': BASIC_TOOL")
        self.assertEqual(entry["tier"], "BASIC_TOOL")


# ---------------------------------------------------------------------------
# 5. New skill stub markdown files exist on disk
# ---------------------------------------------------------------------------

class TestNewSkillMdFilesExist(unittest.TestCase):
    """All 17 new stub .md files added by this PR must be present on disk."""

    def _md_path(self, filename: str) -> str:
        return os.path.join(SKILLS_DIR, filename)

    def test_data_guardian_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("data-guardian.md")))

    def test_topological_curiosity_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("topological-curiosity.md")))

    def test_compute_router_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("compute-router.md")))

    def test_damir_check_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("damir-check.md")))

    def test_memory_management_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("memory-management.md")))

    def test_opportunity_hunter_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("opportunity-hunter.md")))

    def test_pattern_validate_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("pattern-validate.md")))

    def test_quran_deep_analysis_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("quran-deep-analysis.md")))

    def test_quran_search_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("quran-search.md")))

    def test_sovereign_identity_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("sovereign-identity.md")))

    def test_sovereign_reasoning_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("sovereign-reasoning.md")))

    def test_trading_skill_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("trading-skill.md")))

    def test_skills_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("skills.md")))

    def test_trustchain_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("trustchain.md")))

    def test_caveman_skill_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("caveman-skill.md")))

    def test_fatiha_topology_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("fatiha-topology.md")))

    def test_go_engine_md_exists(self):
        self.assertTrue(os.path.isfile(self._md_path("go-engine.md")))

    def test_all_17_stub_files_exist(self):
        """Bulk check: every expected stub file must exist."""
        missing = []
        for _, filename in NEW_SKILLS_IN_PR:
            path = self._md_path(filename)
            if not os.path.isfile(path):
                missing.append(filename)
        self.assertEqual(
            [], missing,
            f"Missing stub MD file(s): {missing}",
        )


# ---------------------------------------------------------------------------
# 6. Stub markdown file structure
# ---------------------------------------------------------------------------

class TestSkillStubMdStructure(unittest.TestCase):
    """
    Each new stub .md must contain the four required section headings
    and a layer metadata line.
    """

    def _read_stub(self, filename: str) -> str:
        path = os.path.join(SKILLS_DIR, filename)
        if not os.path.isfile(path):
            self.skipTest(f"Stub file '{filename}' does not exist")
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def test_all_stubs_have_purpose_section(self):
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                self.assertIn("## Purpose", content, f"Missing '## Purpose' in {filename}")

    def test_all_stubs_have_constitutional_alignment_section(self):
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                self.assertIn(
                    "## Constitutional Alignment", content,
                    f"Missing '## Constitutional Alignment' in {filename}",
                )

    def test_all_stubs_have_operational_flow_section(self):
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                self.assertIn(
                    "## Operational Flow", content,
                    f"Missing '## Operational Flow' in {filename}",
                )

    def test_all_stubs_have_failure_modes_section(self):
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                self.assertIn(
                    "## Failure Modes", content,
                    f"Missing '## Failure Modes' in {filename}",
                )

    def test_all_stubs_have_h1_title(self):
        """Each stub must begin with an H1 heading (# SkillName)."""
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                first_line = content.splitlines()[0]
                self.assertTrue(
                    first_line.startswith("# "),
                    f"First line of {filename} must be an H1 heading; got: {first_line!r}",
                )

    def test_all_stubs_have_layer_metadata(self):
        """Each stub must contain a layer metadata line starting with '> Layer:'."""
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                self.assertIn(
                    "> Layer:", content,
                    f"Missing '> Layer:' metadata in {filename}",
                )

    def test_all_stubs_are_utf8(self):
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                path = os.path.join(SKILLS_DIR, filename)
                if not os.path.isfile(path):
                    self.skipTest(f"File '{filename}' not found")
                try:
                    with open(path, encoding="utf-8") as fh:
                        fh.read()
                except UnicodeDecodeError as exc:
                    self.fail(f"{filename} is not valid UTF-8: {exc}")

    def test_all_stubs_non_empty(self):
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                path = os.path.join(SKILLS_DIR, filename)
                if not os.path.isfile(path):
                    self.skipTest(f"File '{filename}' not found")
                self.assertGreater(os.path.getsize(path), 0, f"{filename} must not be empty")

    def test_section_ordering(self):
        """
        Required sections must appear in the canonical order:
        Purpose → Constitutional Alignment → Operational Flow → Failure Modes.
        """
        for _, filename in NEW_SKILLS_IN_PR:
            with self.subTest(file=filename):
                content = self._read_stub(filename)
                positions = [content.find(sec) for sec in REQUIRED_MD_SECTIONS]
                # All must be present
                for sec, pos in zip(REQUIRED_MD_SECTIONS, positions):
                    if pos == -1:
                        self.fail(f"Section '{sec}' not found in {filename}")
                # Must be in strictly increasing position order
                self.assertEqual(
                    positions, sorted(positions),
                    f"Sections out of order in {filename}: {list(zip(REQUIRED_MD_SECTIONS, positions))}",
                )


# ---------------------------------------------------------------------------
# 7. Stub-specific content checks
# ---------------------------------------------------------------------------

class TestSkillStubContent(unittest.TestCase):
    """
    Spot-check the content of specific stub files that have real descriptions.
    """

    def _read(self, filename: str) -> str:
        path = os.path.join(SKILLS_DIR, filename)
        if not os.path.isfile(path):
            self.skipTest(f"File '{filename}' not found")
        with open(path, encoding="utf-8") as fh:
            return fh.read()

    def test_trustchain_title_matches(self):
        content = self._read("trustchain.md")
        self.assertIn("# TrustChain", content)

    def test_trustchain_purpose_describes_ledger(self):
        content = self._read("trustchain.md")
        self.assertIn("SHA-256", content)
        self.assertIn("ledger", content)

    def test_trustchain_layer_is_security(self):
        content = self._read("trustchain.md")
        self.assertIn("Security", content)

    def test_caveman_skill_title_matches(self):
        content = self._read("caveman-skill.md")
        self.assertIn("# CavemanSkill", content)

    def test_caveman_skill_purpose_mentions_resilience(self):
        content = self._read("caveman-skill.md")
        self.assertIn("resilient", content)

    def test_caveman_skill_layer_is_workers(self):
        content = self._read("caveman-skill.md")
        self.assertIn("Workers", content)

    def test_fatiha_topology_title_matches(self):
        content = self._read("fatiha-topology.md")
        self.assertIn("# FatihaTopology", content)

    def test_fatiha_topology_purpose_mentions_quran(self):
        content = self._read("fatiha-topology.md")
        # Should mention Quranic or topological routing
        content_lower = content.lower()
        self.assertTrue(
            "quran" in content_lower or "topological" in content_lower,
            f"fatiha-topology.md purpose should reference Quranic or topological concepts",
        )

    def test_fatiha_topology_layer_is_quran(self):
        content = self._read("fatiha-topology.md")
        self.assertIn("Quran", content)

    def test_go_engine_title_matches(self):
        content = self._read("go-engine.md")
        self.assertIn("# Go_Engine", content)

    def test_go_engine_purpose_mentions_http(self):
        content = self._read("go-engine.md")
        self.assertIn("HTTP", content)

    def test_go_engine_layer_is_core(self):
        content = self._read("go-engine.md")
        self.assertIn("Core", content)

    def test_data_guardian_layer_is_security(self):
        content = self._read("data-guardian.md")
        self.assertIn("Security", content)

    def test_damir_check_layer_is_ethics(self):
        content = self._read("damir-check.md")
        self.assertIn("Ethics", content)

    def test_sovereign_identity_layer_is_core(self):
        content = self._read("sovereign-identity.md")
        self.assertIn("Core", content)

    def test_opportunity_hunter_layer_is_evolution(self):
        content = self._read("opportunity-hunter.md")
        self.assertIn("Evolution", content)

    def test_trading_skill_layer_is_evolution(self):
        content = self._read("trading-skill.md")
        self.assertIn("Evolution", content)

    def test_memory_management_layer_is_memory(self):
        content = self._read("memory-management.md")
        self.assertIn("Memory", content)

    def test_pattern_validate_layer_is_memory(self):
        content = self._read("pattern-validate.md")
        self.assertIn("Memory", content)

    def test_compute_router_layer_is_core(self):
        content = self._read("compute-router.md")
        self.assertIn("Core", content)

    def test_skills_meta_is_meta_layer(self):
        content = self._read("skills.md")
        self.assertIn("Meta", content)

    def test_quran_deep_analysis_layer_is_quran(self):
        content = self._read("quran-deep-analysis.md")
        self.assertIn("Quran", content)

    def test_quran_search_layer_is_quran(self):
        content = self._read("quran-search.md")
        self.assertIn("Quran", content)

    def test_topological_curiosity_layer_is_quran(self):
        content = self._read("topological-curiosity.md")
        self.assertIn("Quran", content)

    def test_sovereign_reasoning_layer_is_workers(self):
        content = self._read("sovereign-reasoning.md")
        self.assertIn("Workers", content)


# ---------------------------------------------------------------------------
# 8. skills.json manifest count after this PR
# ---------------------------------------------------------------------------

class TestSkillsJsonCount(unittest.TestCase):
    """The manifest must contain exactly the expected number of skills."""

    def setUp(self):
        self.data = _load_skills_json()
        self.skills = self.data["skills"]

    def test_total_skill_count_is_at_least_75(self):
        """README dashboard shows 75 total skills after this PR."""
        self.assertGreaterEqual(
            len(self.skills), 75,
            f"Expected at least 75 skills, got {len(self.skills)}",
        )

    def test_last_skill_is_go_engine(self):
        """Go_Engine was the last entry added in this PR."""
        self.assertEqual(
            self.skills[-1]["name"], "Go_Engine",
            f"Expected last skill to be 'Go_Engine', got '{self.skills[-1]['name']}'",
        )

    def test_no_duplicate_new_skill_names(self):
        """None of the 17 new skill names may appear more than once."""
        names = [s["name"] for s in self.skills]
        for name, _ in NEW_SKILLS_IN_PR:
            with self.subTest(name=name):
                count = names.count(name)
                self.assertEqual(
                    1, count,
                    f"Skill '{name}' appears {count} times in skills.json (expected 1)",
                )


# ---------------------------------------------------------------------------
# 9. README dashboard changes
# ---------------------------------------------------------------------------

class TestReadmeDashboardChanges(unittest.TestCase):
    """
    The README live ecosystem dashboard was updated in this PR.
    Verify the key metrics changed correctly.
    """

    def setUp(self):
        self.content = _read_readme()

    def test_skill_registry_shows_75_total(self):
        """Dashboard now reads '75 Total Skills'."""
        self.assertIn("75 Total Skills", self.content)

    def test_unclassified_count_shows_24(self):
        """UNCLASSIFIED tier now lists 24 skills."""
        self.assertIn("24", self.content)

    def test_new_skill_names_listed_in_unclassified(self):
        """
        The new skill names must appear in the UNCLASSIFIED row of the dashboard.
        Check a representative sample.
        """
        for name in ("DATA_GUARDIAN", "TrustChain", "CavemanSkill", "FatihaTopology", "Go_Engine"):
            with self.subTest(name=name):
                self.assertIn(
                    name, self.content,
                    f"Expected '{name}' to appear in README (UNCLASSIFIED listing)",
                )

    def test_python_tests_status_is_fail(self):
        """
        The PR changed the Python Tests status from ✅ Pass to ❌ Fail.
        The README must reflect the failure state.
        """
        # Find the Python Tests row in the dashboard table
        for line in self.content.splitlines():
            if "Python Tests" in line and "pytest" in line:
                self.assertIn(
                    "Fail", line,
                    f"Python Tests row should show 'Fail', got: {line!r}",
                )
                break
        else:
            self.fail("Could not find the 'Python Tests' row in README dashboard")

    def test_readme_updated_timestamp_present(self):
        """The dashboard header shows a 'Last updated' timestamp."""
        self.assertIn("Last updated:", self.content)

    def test_readme_unclassified_row_contains_snake_case_skills(self):
        """Snake-case skill names from this PR are listed in the UNCLASSIFIED row."""
        for name in ("compute_router", "damir_check", "memory_management",
                     "opportunity_hunter", "pattern_validate"):
            with self.subTest(name=name):
                self.assertIn(name, self.content)

    def test_readme_unclassified_row_contains_quran_skills(self):
        """Quran-related skill names from this PR appear in UNCLASSIFIED row."""
        for name in ("quran_deep_analysis", "quran_search"):
            with self.subTest(name=name):
                self.assertIn(name, self.content)


# ---------------------------------------------------------------------------
# 10. Regression / boundary tests
# ---------------------------------------------------------------------------

class TestRegressionChecks(unittest.TestCase):
    """
    Extra checks to guard against regressions and boundary conditions
    introduced or exposed by this PR.
    """

    def setUp(self):
        self.data = _load_skills_json()
        self.by_name = {s["name"]: s for s in self.data["skills"]}

    def test_skills_json_is_valid_json_after_pr(self):
        """skills.json must still parse as valid JSON."""
        with open(SKILLS_JSON_PATH, "rb") as fh:
            raw = fh.read()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            self.fail(f"skills.json is not valid JSON: {exc}")
        self.assertIsInstance(parsed, dict)

    def test_skills_array_is_not_empty(self):
        self.assertGreater(len(self.data["skills"]), 0)

    def test_pre_existing_skills_not_removed(self):
        """Skills that existed before this PR must still be present."""
        pre_existing = {
            "sovereign-constitution", "covenant-guard", "trust-chain",
            "circuit-breaker", "intent-dispatcher", "prompt-templates",
        }
        for name in pre_existing:
            with self.subTest(name=name):
                self.assertIn(
                    name, self.by_name,
                    f"Pre-existing skill '{name}' was inadvertently removed",
                )

    def test_go_engine_description_contains_http(self):
        """Go_Engine description must mention 'HTTP' (not just 'server')."""
        entry = self.by_name.get("Go_Engine", {})
        self.assertIn("HTTP", entry.get("description", ""))

    def test_trustchain_description_contains_sha256(self):
        """TrustChain description must reference SHA-256."""
        entry = self.by_name.get("TrustChain", {})
        self.assertIn("SHA-256", entry.get("description", ""))

    def test_fatiha_topology_description_mentions_quranic(self):
        """FatihaTopology description must reference Quranic."""
        entry = self.by_name.get("FatihaTopology", {})
        self.assertIn("Quranic", entry.get("description", ""))

    def test_caveman_skill_description_mentions_resilient(self):
        """CavemanSkill description must mention 'resilient'."""
        entry = self.by_name.get("CavemanSkill", {})
        self.assertIn("resilient", entry.get("description", ""))

    def test_skills_json_top_level_structure_intact(self):
        """The top-level 'name', 'description', 'skills' keys must still be present."""
        for key in ("name", "description", "skills"):
            self.assertIn(key, self.data, f"Top-level key '{key}' missing from skills.json")

    def test_stub_auto_description_format(self):
        """
        Stub entries with auto-generated descriptions follow the format
        'Auto-generated stub for <name>'.
        """
        auto_stub_names = [
            name for name, _ in NEW_SKILLS_IN_PR
            if name not in SKILLS_WITH_REAL_DESCRIPTION
        ]
        for name in auto_stub_names:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                desc = entry.get("description", "")
                self.assertTrue(
                    desc.startswith("Auto-generated stub for "),
                    f"Expected auto-generated description for '{name}', got: {desc!r}",
                )

    def test_skills_with_real_description_do_not_use_auto_format(self):
        """Skills with curated descriptions must NOT use the auto-stub prefix."""
        for name in SKILLS_WITH_REAL_DESCRIPTION:
            with self.subTest(name=name):
                entry = self.by_name.get(name, {})
                desc = entry.get("description", "")
                self.assertFalse(
                    desc.startswith("Auto-generated stub for "),
                    f"Skill '{name}' should have a real description, not auto-stub format",
                )


if __name__ == "__main__":
    unittest.main()
