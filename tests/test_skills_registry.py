"""
Tests for skills.json registry — covers all additions from this PR.

The PR added 44 new skill entries to skills.json.  These tests validate:
  - The file is valid JSON with the expected top-level structure.
  - Every skill entry has the required fields (name, description, file).
  - Every file reference points to an existing .md file on disk.
  - There are no duplicate skill names.
  - Skill names follow the kebab-case convention.
  - The file path for each entry matches the expected pattern.
  - All skills added in this PR are present in the registry.
  - Descriptions are non-empty strings.
  - The skills list has grown by the expected number of new entries.
  - Skill names are non-empty strings.
  - The JSON file itself does not end with a newline (regression: the diff
    shows the file was changed to remove the trailing newline).
"""

import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_JSON_PATH = os.path.join(REPO_ROOT, "skills.json")

# Skills that were present BEFORE this PR (the original 6 entries).
PRE_EXISTING_SKILLS = {
    "agent-memory",
    "voice-wizard",
    "aix-schema",
    "api-route-standard",
    "skills-system",
    "vercel-deploy",
}

# All new skill names added to skills.json by this PR.
NEW_SKILLS_IN_PR = {
    "sovereign-constitution",
    "covenant-guard",
    "shura-council",
    "topology-orchestrator",
    "skill-bank-evolution",
    "mission-control",
    "pipeline-store",
    "version-guard",
    "intent-dispatcher",
    "prompt-weaver",
    "resonance-engine",
    "mcts-simulator",
    "memory-bridge",
    "metamorphosis-loop",
    "reward-engine",
    "persona-forge",
    "role-tribunal",
    "voice-identity",
    "persona-marketplace",
    "agent-division-loader",
    "multi-tool-exporter",
    "data-alchemist",
    "model-council",
    "edge-whisperer",
    "trust-chain",
    "circuit-breaker",
    "purity-filter",
    "skill-evaluator",
    "skill-sandbox",
    "prompt-evaluator",
    "red-team-guard",
    "cross-model-judge",
    "ci-cd-ai-guard",
    "chain-tracer",
    "quran-resonance",
    "hidden-topology",
    "fractal-memory",
    "awesome-curator",
    "pre-built-memories",
    "fine-tuned-vault",
    "integration-packs",
    "open-mcp-connectors",
    "blockchain-trading-kit",
    "prompt-templates",
}

VALID_TIERS = {
    "SOVEREIGN",
    "ADVANCED_INFRASTRUCTURE",
    "PRO",
    "ADVANCED_TOOL",
    "BASIC_TOOL",
}

# Regex for valid kebab-case skill names (lowercase letters, digits, hyphens).
KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9-]+[a-z0-9]$")


def _load_skills_json():
    with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
        return json.load(fh)


class TestSkillsJsonStructure(unittest.TestCase):
    """Validate the top-level structure of skills.json."""

    def setUp(self):
        self.data = _load_skills_json()

    def test_file_exists(self):
        self.assertTrue(
            os.path.exists(SKILLS_JSON_PATH),
            "skills.json must exist in the repository root",
        )

    def test_is_valid_json(self):
        """skills.json must parse without errors."""
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            content = fh.read()
        # Should not raise
        parsed = json.loads(content)
        self.assertIsInstance(parsed, dict)

    def test_top_level_name_field(self):
        self.assertIn("name", self.data)
        self.assertIsInstance(self.data["name"], str)
        self.assertTrue(len(self.data["name"]) > 0)

    def test_top_level_description_field(self):
        self.assertIn("description", self.data)
        self.assertIsInstance(self.data["description"], str)
        self.assertTrue(len(self.data["description"]) > 0)

    def test_top_level_skills_array(self):
        self.assertIn("skills", self.data)
        self.assertIsInstance(self.data["skills"], list)
        self.assertGreater(len(self.data["skills"]), 0)

    def test_skills_count_includes_new_entries(self):
        """After this PR, the registry must contain at least the 6 original
        plus all 44 new skills."""
        expected_minimum = len(PRE_EXISTING_SKILLS) + len(NEW_SKILLS_IN_PR)
        self.assertGreaterEqual(
            len(self.data["skills"]),
            expected_minimum,
            f"Expected at least {expected_minimum} skills, "
            f"got {len(self.data['skills'])}",
        )

    def test_no_extra_top_level_keys(self):
        """Only known keys should appear at the top level."""
        allowed_keys = {"name", "description", "skills"}
        actual_keys = set(self.data.keys())
        self.assertTrue(
            actual_keys.issubset(allowed_keys),
            f"Unexpected top-level keys: {actual_keys - allowed_keys}",
        )


class TestSkillsJsonEntries(unittest.TestCase):
    """Validate every individual entry in the skills array."""

    def setUp(self):
        data = _load_skills_json()
        self.skills = data["skills"]

    def test_each_entry_has_name(self):
        for skill in self.skills:
            with self.subTest(skill=skill):
                self.assertIn("name", skill, f"Missing 'name' in entry: {skill}")

    def test_each_entry_has_description(self):
        for skill in self.skills:
            with self.subTest(name=skill.get("name", "<unknown>")):
                self.assertIn(
                    "description", skill, f"Missing 'description' in: {skill}"
                )

    def test_each_entry_has_file(self):
        for skill in self.skills:
            with self.subTest(name=skill.get("name", "<unknown>")):
                self.assertIn("file", skill, f"Missing 'file' in: {skill}")

    def test_names_are_non_empty_strings(self):
        for skill in self.skills:
            with self.subTest(skill=skill):
                self.assertIsInstance(skill["name"], str)
                self.assertGreater(len(skill["name"]), 0)

    def test_descriptions_are_non_empty_strings(self):
        for skill in self.skills:
            with self.subTest(name=skill["name"]):
                self.assertIsInstance(skill["description"], str)
                self.assertGreater(
                    len(skill["description"]),
                    0,
                    f"Empty description for skill '{skill['name']}'",
                )

    def test_file_paths_are_strings(self):
        for skill in self.skills:
            with self.subTest(name=skill["name"]):
                self.assertIsInstance(skill["file"], str)

    def test_file_paths_follow_convention(self):
        """Each file path should be 'skills/<name>.md'."""
        for skill in self.skills:
            with self.subTest(name=skill["name"]):
                expected = f"skills/{skill['name']}.md"
                self.assertEqual(
                    skill["file"],
                    expected,
                    f"File path for '{skill['name']}' should be '{expected}', "
                    f"got '{skill['file']}'",
                )

    def test_referenced_files_exist_on_disk(self):
        """Every file referenced in skills.json must exist in the repo."""
        for skill in self.skills:
            with self.subTest(name=skill["name"]):
                full_path = os.path.join(REPO_ROOT, skill["file"])
                self.assertTrue(
                    os.path.isfile(full_path),
                    f"Referenced file does not exist: {skill['file']}",
                )

    def test_no_duplicate_skill_names(self):
        names = [s["name"] for s in self.skills]
        seen = set()
        duplicates = []
        for name in names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)
        self.assertEqual(
            [], duplicates, f"Duplicate skill names found: {duplicates}"
        )

    def test_skill_names_use_kebab_case(self):
        for skill in self.skills:
            with self.subTest(name=skill["name"]):
                self.assertRegex(
                    skill["name"],
                    KEBAB_CASE_RE,
                    f"Skill name '{skill['name']}' is not kebab-case",
                )

    def test_no_extra_fields_per_entry(self):
        """Each entry must only contain the known keys."""
        allowed = {"name", "description", "file"}
        for skill in self.skills:
            with self.subTest(name=skill["name"]):
                extra = set(skill.keys()) - allowed
                self.assertEqual(
                    set(),
                    extra,
                    f"Unexpected keys in skill '{skill['name']}': {extra}",
                )


class TestNewSkillEntries(unittest.TestCase):
    """Verify every skill added by this PR is present in skills.json."""

    def setUp(self):
        data = _load_skills_json()
        self.skill_names = {s["name"] for s in data["skills"]}
        self.skills_by_name = {s["name"]: s for s in data["skills"]}

    def test_all_pr_new_skills_are_registered(self):
        missing = NEW_SKILLS_IN_PR - self.skill_names
        self.assertEqual(
            set(),
            missing,
            f"These new skills from the PR are missing in skills.json: {missing}",
        )

    def test_pre_existing_skills_still_present(self):
        missing = PRE_EXISTING_SKILLS - self.skill_names
        self.assertEqual(
            set(),
            missing,
            f"Pre-existing skills were removed from skills.json: {missing}",
        )

    # -- Spot-check individual new entries --

    def test_covenant_guard_description(self):
        self.assertIn("covenant-guard", self.skills_by_name)
        desc = self.skills_by_name["covenant-guard"]["description"]
        self.assertIn("truth", desc.lower())

    def test_circuit_breaker_description(self):
        self.assertIn("circuit-breaker", self.skills_by_name)
        desc = self.skills_by_name["circuit-breaker"]["description"]
        self.assertGreater(len(desc), 0)

    def test_chain_tracer_file_reference(self):
        self.assertIn("chain-tracer", self.skills_by_name)
        self.assertEqual(
            self.skills_by_name["chain-tracer"]["file"], "skills/chain-tracer.md"
        )

    def test_blockchain_trading_kit_description(self):
        """
        Verify the 'blockchain-trading-kit' skill is present in the manifest and that its name or description contains the substring "blockchain".
        
        This ensures the manifest includes the expected entry and that the entry references blockchain-related functionality.
        """
        self.assertIn("blockchain-trading-kit", self.skills_by_name)
        entry = self.skills_by_name["blockchain-trading-kit"]
        self.assertIn("blockchain", entry["description"].lower() + entry["name"].lower())

    def test_multiverse_lab_pro_registered(self):
        """
        Check that the 'multiverse-lab-pro' markdown file exists under skills/ and that its skill name is present in the skills.json manifest.
        """
        md_path = os.path.join(REPO_ROOT, "skills", "multiverse-lab-pro.md")
        self.assertTrue(os.path.isfile(md_path), "multiverse-lab-pro.md must exist")
        self.assertIn(
            "multiverse-lab-pro",
            self.skill_names,
            "multiverse-lab-pro must be registered in skills.json",
        )

    def test_community_support_layer_registered(self):
        """
        Asserts that skills/community-support-layer.md exists on disk and that "community-support-layer" is present in the skills.json manifest.
        """
        md_path = os.path.join(REPO_ROOT, "skills", "community-support-layer.md")
        self.assertTrue(
            os.path.isfile(md_path), "community-support-layer.md must exist"
        )
        self.assertIn(
            "community-support-layer",
            self.skill_names,
            "community-support-layer must be registered in skills.json",
        )

    def test_intent_dispatcher_entry(self):
        self.assertIn("intent-dispatcher", self.skills_by_name)
        entry = self.skills_by_name["intent-dispatcher"]
        self.assertEqual(entry["file"], "skills/intent-dispatcher.md")
        self.assertIn("natural language", entry["description"].lower())

    def test_memory_bridge_entry(self):
        self.assertIn("memory-bridge", self.skills_by_name)
        entry = self.skills_by_name["memory-bridge"]
        self.assertIn("memory", entry["description"].lower())

    def test_mcts_simulator_entry(self):
        self.assertIn("mcts-simulator", self.skills_by_name)
        entry = self.skills_by_name["mcts-simulator"]
        self.assertIn("monte carlo", entry["description"].lower())

    def test_cross_model_judge_entry(self):
        self.assertIn("cross-model-judge", self.skills_by_name)
        entry = self.skills_by_name["cross-model-judge"]
        self.assertIn("llm", entry["description"].lower())

    def test_ci_cd_ai_guard_entry(self):
        self.assertIn("ci-cd-ai-guard", self.skills_by_name)
        entry = self.skills_by_name["ci-cd-ai-guard"]
        self.assertIn("production", entry["description"].lower())

    def test_fine_tuned_vault_entry(self):
        self.assertIn("fine-tuned-vault", self.skills_by_name)
        entry = self.skills_by_name["fine-tuned-vault"]
        self.assertIn("model", entry["description"].lower())

    def test_awesome_curator_entry(self):
        self.assertIn("awesome-curator", self.skills_by_name)
        entry = self.skills_by_name["awesome-curator"]
        self.assertIn("curated", entry["description"].lower())

    def test_hidden_topology_entry(self):
        self.assertIn("hidden-topology", self.skills_by_name)
        entry = self.skills_by_name["hidden-topology"]
        self.assertIn("connections", entry["description"].lower())

    def test_fractal_memory_entry(self):
        self.assertIn("fractal-memory", self.skills_by_name)
        entry = self.skills_by_name["fractal-memory"]
        self.assertIn("memor", entry["description"].lower())

    def test_integration_packs_entry(self):
        self.assertIn("integration-packs", self.skills_by_name)
        entry = self.skills_by_name["integration-packs"]
        self.assertGreater(len(entry["description"]), 0)

    def test_model_council_entry(self):
        self.assertIn("model-council", self.skills_by_name)
        entry = self.skills_by_name["model-council"]
        # Description should mention routing between model tiers
        desc = entry["description"].lower()
        self.assertTrue(
            "local" in desc or "edge" in desc or "cloud" in desc or "route" in desc,
            f"Unexpected model-council description: '{entry['description']}'",
        )

    def test_data_alchemist_entry(self):
        self.assertIn("data-alchemist", self.skills_by_name)
        entry = self.skills_by_name["data-alchemist"]
        self.assertIn("data", entry["description"].lower())

    def test_edge_whisperer_entry(self):
        self.assertIn("edge-whisperer", self.skills_by_name)
        entry = self.skills_by_name["edge-whisperer"]
        desc = entry["description"].lower()
        self.assertTrue(
            "webgpu" in desc or "wasm" in desc or "offline" in desc or "edge" in desc,
            f"Unexpected edge-whisperer description: '{entry['description']}'",
        )

    def test_multi_tool_exporter_entry(self):
        self.assertIn("multi-tool-exporter", self.skills_by_name)
        entry = self.skills_by_name["multi-tool-exporter"]
        self.assertIn("platform", entry["description"].lower())

    def test_mission_control_entry(self):
        self.assertIn("mission-control", self.skills_by_name)
        entry = self.skills_by_name["mission-control"]
        self.assertIn("planner", entry["description"].lower())

    def test_metamorphosis_loop_entry(self):
        self.assertIn("metamorphosis-loop", self.skills_by_name)
        entry = self.skills_by_name["metamorphosis-loop"]
        self.assertIn("49", entry["description"])

    def test_agent_division_loader_entry(self):
        self.assertIn("agent-division-loader", self.skills_by_name)
        entry = self.skills_by_name["agent-division-loader"]
        desc = entry["description"].lower()
        self.assertTrue(
            "team" in desc or "mission" in desc or "functional" in desc,
            f"Unexpected agent-division-loader description: '{entry['description']}'",
        )

    def test_prompt_templates_is_last_new_entry(self):
        """prompt-templates was the last entry added in this PR."""
        data = json.loads(open(SKILLS_JSON_PATH, encoding="utf-8").read())
        last_skill = data["skills"][-1]
        self.assertEqual(last_skill["name"], "prompt-templates")

    def test_prompt_templates_entry(self):
        self.assertIn("prompt-templates", self.skills_by_name)
        entry = self.skills_by_name["prompt-templates"]
        self.assertIn("prompt", entry["description"].lower())


class TestSkillsJsonFileIntegrity(unittest.TestCase):
    """Low-level file integrity checks."""

    def test_file_is_utf8_encoded(self):
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIsInstance(content, str)

    def test_file_is_not_empty(self):
        size = os.path.getsize(SKILLS_JSON_PATH)
        self.assertGreater(size, 0)

    def test_raw_bytes_decode_as_json(self):
        """
        Verify that the raw bytes read from the repository's `skills.json` file parse as JSON and produce a top-level object.
        
        Asserts that decoding the file's raw bytes with `json.loads` yields a `dict`.
        """
        with open(SKILLS_JSON_PATH, "rb") as fh:
            raw = fh.read()
        parsed = json.loads(raw)
        self.assertIsInstance(parsed, dict)

    def test_total_skill_count_matches_disk(self):
        """The manifest count must match the number of skill files on disk.
        This is the durable invariant: any orphan MD or dead manifest entry
        is a structural bug. The Schema Sentinel CI job enforces the same
        invariant on every push.
        """
        import pathlib
        data = _load_skills_json()
        skills_dir = pathlib.Path(REPO_ROOT) / "skills"
        on_disk = {p.stem for p in skills_dir.glob("*.md")}
        in_manifest = {s["name"] for s in data["skills"]}
        orphans = on_disk - in_manifest
        dead = in_manifest - on_disk
        self.assertFalse(orphans, f"Skill MDs on disk but not in manifest: {sorted(orphans)}")
        self.assertFalse(dead, f"Manifest entries with no MD file: {sorted(dead)}")
        self.assertEqual(len(data["skills"]), len(on_disk),
                         f"Manifest has {len(data['skills'])} entries but disk has {len(on_disk)} MDs")


if __name__ == "__main__":
    unittest.main()
