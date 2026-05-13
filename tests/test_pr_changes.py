"""
Tests for changes introduced in this pull request.

Covers:
  - package.json: removal of the "aix" metadata block; core fields preserved.
  - assets/: v2 SVG files deleted; non-v2 counterparts still exist.
  - README.md: image references updated from *-v2.svg to *.svg.
  - AGENTS.md: naming convention updated to snake_case.
  - skills/mcts-simulator.md: stub sections replaced with real content.
  - skills/prompt-evaluator.md: stub sections replaced with real content.
  - skills/prompt-weaver.md: stub sections replaced with real content.
  - skills/resonance-engine.md: stub sections replaced with real content.
"""

import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PACKAGE_JSON_PATH = os.path.join(REPO_ROOT, "package.json")
README_PATH = os.path.join(REPO_ROOT, "README.md")
AGENTS_MD_PATH = os.path.join(REPO_ROOT, "AGENTS.md")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

# Skill files modified in this PR
CHANGED_SKILLS = [
    "mcts-simulator.md",
    "prompt-evaluator.md",
    "prompt-weaver.md",
    "resonance-engine.md",
]

# Required section headings (English) that must be present and non-stub
REQUIRED_SECTIONS = [
    "## Purpose",
    "## Constitutional Alignment",
    "## Operational Flow",
    "## Failure Modes",
]

# Stub markers that must NOT appear in any required section body
STUB_MARKERS = [
    "TODO: Define purpose",
    "TODO: Define constitutional alignment",
    "TODO: Define operational flow",
    "TODO: Define failure modes",
    "TODO:",
    "TBD",
    "<fill in>",
]


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _load_package_json() -> dict:
    with open(PACKAGE_JSON_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# ─────────────────────────────────────────────────────────────────────────────
# package.json
# ─────────────────────────────────────────────────────────────────────────────


class TestPackageJsonAixBlockRemoved(unittest.TestCase):
    """The 'aix' metadata block was removed in this PR."""

    def setUp(self):
        self.pkg = _load_package_json()

    def test_aix_field_does_not_exist(self):
        self.assertNotIn(
            "aix",
            self.pkg,
            "package.json must not contain an 'aix' metadata block after this PR",
        )

    def test_name_field_still_present(self):
        self.assertIn("name", self.pkg)
        self.assertEqual(self.pkg["name"], "aix-agent-skills")

    def test_version_field_still_present(self):
        self.assertIn("version", self.pkg)

    def test_description_field_still_present(self):
        self.assertIn("description", self.pkg)
        self.assertGreater(len(self.pkg["description"]), 0)

    def test_license_field_still_present(self):
        self.assertIn("license", self.pkg)
        self.assertEqual(self.pkg["license"], "Apache-2.0")

    def test_scripts_field_still_present(self):
        self.assertIn("scripts", self.pkg)
        self.assertIsInstance(self.pkg["scripts"], dict)

    def test_test_script_still_defined(self):
        scripts = self.pkg.get("scripts", {})
        self.assertIn("test", scripts, "package.json must still have a 'test' script")
        self.assertGreater(len(scripts["test"]), 0)

    def test_no_stack_codename_field(self):
        """stackCodename was inside the removed aix block."""
        self.assertNotIn("stackCodename", self.pkg)

    def test_no_stack_version_field(self):
        """stackVersion was inside the removed aix block."""
        self.assertNotIn("stackVersion", self.pkg)


# ─────────────────────────────────────────────────────────────────────────────
# assets — deleted v2 files, remaining non-v2 files
# ─────────────────────────────────────────────────────────────────────────────


class TestDeletedV2Assets(unittest.TestCase):
    """The v2 SVG assets were deleted in this PR."""

    DELETED_FILES = [
        "aix-footer-quote-v2.svg",
        "aix-stack-diagram-v2.svg",
        "aix-stack-header-v2.svg",
        "axi-mascot.svg",
    ]

    def test_aix_footer_quote_v2_deleted(self):
        path = os.path.join(ASSETS_DIR, "aix-footer-quote-v2.svg")
        self.assertFalse(
            os.path.isfile(path),
            "aix-footer-quote-v2.svg must be deleted in this PR",
        )

    def test_aix_stack_diagram_v2_deleted(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-diagram-v2.svg")
        self.assertFalse(
            os.path.isfile(path),
            "aix-stack-diagram-v2.svg must be deleted in this PR",
        )

    def test_aix_stack_header_v2_deleted(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-header-v2.svg")
        self.assertFalse(
            os.path.isfile(path),
            "aix-stack-header-v2.svg must be deleted in this PR",
        )

    def test_axi_mascot_deleted(self):
        path = os.path.join(ASSETS_DIR, "axi-mascot.svg")
        self.assertFalse(
            os.path.isfile(path),
            "axi-mascot.svg must be deleted in this PR",
        )


class TestRemainingNonV2Assets(unittest.TestCase):
    """The non-v2 SVG assets must still exist."""

    def test_aix_footer_quote_svg_exists(self):
        path = os.path.join(ASSETS_DIR, "aix-footer-quote.svg")
        self.assertTrue(
            os.path.isfile(path),
            "assets/aix-footer-quote.svg must still exist",
        )

    def test_aix_stack_diagram_svg_exists(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-diagram.svg")
        self.assertTrue(
            os.path.isfile(path),
            "assets/aix-stack-diagram.svg must still exist",
        )

    def test_aix_stack_header_svg_exists(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-header.svg")
        self.assertTrue(
            os.path.isfile(path),
            "assets/aix-stack-header.svg must still exist",
        )

    def test_non_v2_svgs_are_not_empty(self):
        for name in ("aix-footer-quote.svg", "aix-stack-diagram.svg", "aix-stack-header.svg"):
            path = os.path.join(ASSETS_DIR, name)
            with self.subTest(file=name):
                self.assertGreater(
                    os.path.getsize(path),
                    0,
                    f"assets/{name} must not be empty",
                )


# ─────────────────────────────────────────────────────────────────────────────
# README.md — image references updated from v2 to non-v2
# ─────────────────────────────────────────────────────────────────────────────


class TestReadmeImageReferences(unittest.TestCase):
    """README.md must reference the non-v2 SVG assets, not the deleted v2 ones."""

    def setUp(self):
        self.content = _read(README_PATH)

    def test_header_svg_references_non_v2(self):
        self.assertIn(
            "aix-stack-header.svg",
            self.content,
            "README.md must reference aix-stack-header.svg",
        )

    def test_header_svg_does_not_reference_v2(self):
        self.assertNotIn(
            "aix-stack-header-v2.svg",
            self.content,
            "README.md must not reference the deleted aix-stack-header-v2.svg",
        )

    def test_diagram_svg_references_non_v2(self):
        self.assertIn(
            "aix-stack-diagram.svg",
            self.content,
            "README.md must reference aix-stack-diagram.svg",
        )

    def test_diagram_svg_does_not_reference_v2(self):
        self.assertNotIn(
            "aix-stack-diagram-v2.svg",
            self.content,
            "README.md must not reference the deleted aix-stack-diagram-v2.svg",
        )

    def test_footer_svg_references_non_v2(self):
        self.assertIn(
            "aix-footer-quote.svg",
            self.content,
            "README.md must reference aix-footer-quote.svg",
        )

    def test_footer_svg_does_not_reference_v2(self):
        self.assertNotIn(
            "aix-footer-quote-v2.svg",
            self.content,
            "README.md must not reference the deleted aix-footer-quote-v2.svg",
        )

    def test_axi_mascot_not_referenced(self):
        self.assertNotIn(
            "axi-mascot.svg",
            self.content,
            "README.md must not reference the deleted axi-mascot.svg",
        )

    def test_readme_removed_echo369_badge(self):
        """The Echo369-branded badge was removed in this PR."""
        self.assertNotIn(
            "Echo369",
            self.content,
            "README.md must no longer reference Echo369 in a badge",
        )

    def test_readme_stack_section_no_extended_ecosystem(self):
        """The 'Extended Ecosystem' subsection (L0/L4-L6 table) was removed."""
        self.assertNotIn(
            "Extended Ecosystem",
            self.content,
        )

    def test_readme_stack_section_no_l0_root_authority(self):
        """The explicit L0 Root Authority row was removed from the stack table."""
        self.assertNotIn(
            "axiomid-project",
            self.content,
        )

    def test_readme_l3_layer_badge_present(self):
        """The L3 MARKETPLACE badge must still be present."""
        self.assertIn("LAYER-L3", self.content)


# ─────────────────────────────────────────────────────────────────────────────
# AGENTS.md — naming convention updated to snake_case
# ─────────────────────────────────────────────────────────────────────────────


class TestAgentsMdNamingConvention(unittest.TestCase):
    """AGENTS.md now documents snake_case naming, not kebab-case."""

    def setUp(self):
        self.content = _read(AGENTS_MD_PATH)

    def test_skill_names_convention_is_snake_case(self):
        self.assertIn(
            "snake_case",
            self.content,
            "AGENTS.md must document snake_case as the skill naming convention",
        )

    def test_snake_case_pattern_mentioned(self):
        self.assertIn(
            "^[a-z0-9_]+$",
            self.content,
            "AGENTS.md must include the snake_case regex pattern ^[a-z0-9_]+$",
        )

    def test_no_longer_primarily_kebab_case_for_skill_ids(self):
        """The old text 'kebab-case for the catalogue' was removed."""
        self.assertNotIn(
            "kebab-case for the catalogue",
            self.content,
        )

    def test_title_has_em_dash(self):
        """Title was updated to use an em-dash (—) separator."""
        first_line = self.content.splitlines()[0]
        self.assertIn(
            "—",
            first_line,
            "AGENTS.md title must use an em-dash (—) separator",
        )

    def test_skills_dir_entry_uses_em_dash(self):
        """The skills/ directory bullet now uses an em-dash separator."""
        self.assertIn(
            "`skills/` —",
            self.content,
        )

    def test_conventions_license_is_apache(self):
        self.assertIn("Apache-2.0", self.content)


# ─────────────────────────────────────────────────────────────────────────────
# Skill files — stub sections replaced with real content
# ─────────────────────────────────────────────────────────────────────────────


class TestChangedSkillsHaveRequiredSections(unittest.TestCase):
    """Each changed skill must contain all four required section headings."""

    def _skill_path(self, filename):
        return os.path.join(SKILLS_DIR, filename)

    def test_mcts_simulator_has_purpose(self):
        content = _read(self._skill_path("mcts-simulator.md"))
        self.assertIn("## Purpose", content)

    def test_mcts_simulator_has_constitutional_alignment(self):
        content = _read(self._skill_path("mcts-simulator.md"))
        self.assertIn("## Constitutional Alignment", content)

    def test_mcts_simulator_has_operational_flow(self):
        content = _read(self._skill_path("mcts-simulator.md"))
        self.assertIn("## Operational Flow", content)

    def test_mcts_simulator_has_failure_modes(self):
        content = _read(self._skill_path("mcts-simulator.md"))
        self.assertIn("## Failure Modes", content)

    def test_prompt_evaluator_has_purpose(self):
        content = _read(self._skill_path("prompt-evaluator.md"))
        self.assertIn("## Purpose", content)

    def test_prompt_evaluator_has_constitutional_alignment(self):
        content = _read(self._skill_path("prompt-evaluator.md"))
        self.assertIn("## Constitutional Alignment", content)

    def test_prompt_evaluator_has_operational_flow(self):
        content = _read(self._skill_path("prompt-evaluator.md"))
        self.assertIn("## Operational Flow", content)

    def test_prompt_evaluator_has_failure_modes(self):
        content = _read(self._skill_path("prompt-evaluator.md"))
        self.assertIn("## Failure Modes", content)

    def test_prompt_weaver_has_purpose(self):
        content = _read(self._skill_path("prompt-weaver.md"))
        self.assertIn("## Purpose", content)

    def test_prompt_weaver_has_constitutional_alignment(self):
        content = _read(self._skill_path("prompt-weaver.md"))
        self.assertIn("## Constitutional Alignment", content)

    def test_prompt_weaver_has_operational_flow(self):
        content = _read(self._skill_path("prompt-weaver.md"))
        self.assertIn("## Operational Flow", content)

    def test_prompt_weaver_has_failure_modes(self):
        content = _read(self._skill_path("prompt-weaver.md"))
        self.assertIn("## Failure Modes", content)

    def test_resonance_engine_has_purpose(self):
        content = _read(self._skill_path("resonance-engine.md"))
        self.assertIn("## Purpose", content)

    def test_resonance_engine_has_constitutional_alignment(self):
        content = _read(self._skill_path("resonance-engine.md"))
        self.assertIn("## Constitutional Alignment", content)

    def test_resonance_engine_has_operational_flow(self):
        content = _read(self._skill_path("resonance-engine.md"))
        self.assertIn("## Operational Flow", content)

    def test_resonance_engine_has_failure_modes(self):
        content = _read(self._skill_path("resonance-engine.md"))
        self.assertIn("## Failure Modes", content)


class TestChangedSkillsHaveNoStubContent(unittest.TestCase):
    """All four required sections in each changed skill must be non-stub."""

    def _skill_path(self, filename):
        return os.path.join(SKILLS_DIR, filename)

    def _assert_no_stubs(self, filename):
        content = _read(self._skill_path(filename))
        for marker in STUB_MARKERS:
            with self.subTest(skill=filename, marker=marker):
                self.assertNotIn(
                    marker,
                    content,
                    f"{filename} must not contain stub marker: {repr(marker)}",
                )

    def test_mcts_simulator_no_stubs(self):
        self._assert_no_stubs("mcts-simulator.md")

    def test_prompt_evaluator_no_stubs(self):
        self._assert_no_stubs("prompt-evaluator.md")

    def test_prompt_weaver_no_stubs(self):
        self._assert_no_stubs("prompt-weaver.md")

    def test_resonance_engine_no_stubs(self):
        self._assert_no_stubs("resonance-engine.md")


class TestMctsSimulatorContent(unittest.TestCase):
    """Specific content checks for mcts-simulator.md."""

    def setUp(self):
        self.content = _read(os.path.join(SKILLS_DIR, "mcts-simulator.md"))

    def test_purpose_mentions_monte_carlo_tree_search(self):
        self.assertIn("Monte Carlo Tree Search", self.content)

    def test_purpose_mentions_mission_control_integration(self):
        self.assertIn("mission-control", self.content)

    def test_purpose_mentions_skill_bank_evolution(self):
        self.assertIn("skill-bank-evolution", self.content)

    def test_constitutional_alignment_mentions_sovereign_constitution(self):
        self.assertIn("sovereign-constitution", self.content)

    def test_constitutional_alignment_mentions_shura_council(self):
        self.assertIn("shura-council", self.content)

    def test_operational_flow_has_numbered_steps(self):
        # Should have at least steps 1 through 5
        for step in ("1.", "2.", "3.", "4.", "5."):
            with self.subTest(step=step):
                self.assertIn(step, self.content)

    def test_operational_flow_mentions_ucb1(self):
        self.assertIn("UCB1", self.content)

    def test_failure_modes_table_present(self):
        # A markdown table has at least a header separator row
        self.assertIn("|---", self.content)

    def test_failure_modes_mentions_low_confidence_flag(self):
        self.assertIn("low_confidence", self.content)

    def test_failure_modes_mentions_no_compliant_plan(self):
        self.assertIn("no_compliant_plan", self.content)

    def test_references_section_present(self):
        self.assertIn("## References", self.content)

    def test_title_uses_comma_not_em_dash_before_tier(self):
        first_line = self.content.splitlines()[0]
        # Should be ", TIER:" not "— TIER:"
        self.assertIn(", TIER:", first_line)
        self.assertNotIn("— TIER:", first_line)

    def test_self_play_section_described(self):
        self.assertIn("Self-play", self.content)

    def test_backpropagation_step_described(self):
        self.assertIn("Backpropagation", self.content)


class TestPromptEvaluatorContent(unittest.TestCase):
    """Specific content checks for prompt-evaluator.md."""

    def setUp(self):
        self.content = _read(os.path.join(SKILLS_DIR, "prompt-evaluator.md"))

    def test_purpose_mentions_five_criteria(self):
        # The five criteria are listed explicitly
        for criterion in ("clarity", "accuracy", "safety", "efficiency", "ethics"):
            with self.subTest(criterion=criterion):
                self.assertIn(criterion, self.content)

    def test_purpose_mentions_llm_as_judge(self):
        self.assertIn("LLM-as-Judge", self.content)

    def test_purpose_mentions_validity_certificate(self):
        self.assertIn("validity certificate", self.content.lower())

    def test_constitutional_alignment_mentions_sovereign_constitution(self):
        self.assertIn("sovereign-constitution", self.content)

    def test_constitutional_alignment_three_judge_requirement(self):
        self.assertIn("three-judge", self.content)

    def test_operational_flow_mentions_weave_envelope(self):
        self.assertIn("Weave envelope", self.content)

    def test_operational_flow_mentions_deterministic_checks(self):
        self.assertIn("deterministic checks", self.content.lower())

    def test_operational_flow_mentions_score_threshold(self):
        self.assertIn("0.8", self.content)

    def test_operational_flow_mentions_three_strike_escalation(self):
        self.assertIn("Three-strike", self.content)

    def test_failure_modes_table_present(self):
        self.assertIn("|---", self.content)

    def test_failure_modes_mentions_judge_pool_insufficient(self):
        self.assertIn("judge_pool_insufficient", self.content)

    def test_failure_modes_mentions_certificate_replay(self):
        self.assertIn("Certificate replay", self.content)

    def test_title_uses_comma_not_em_dash_before_tier(self):
        first_line = self.content.splitlines()[0]
        self.assertIn(", TIER:", first_line)
        self.assertNotIn("— TIER:", first_line)

    def test_references_section_present(self):
        self.assertIn("## References", self.content)


class TestPromptWeaverContent(unittest.TestCase):
    """Specific content checks for prompt-weaver.md."""

    def setUp(self):
        self.content = _read(os.path.join(SKILLS_DIR, "prompt-weaver.md"))

    def test_purpose_mentions_seven_layer(self):
        self.assertIn("seven-layer", self.content)

    def test_purpose_mentions_weave_envelope(self):
        self.assertIn("Weave envelope", self.content)

    def test_constitutional_alignment_mentions_sovereign_constitution(self):
        self.assertIn("sovereign-constitution", self.content)

    def test_constitutional_alignment_mentions_shura_council(self):
        self.assertIn("shura-council", self.content)

    def test_operational_flow_mentions_persona_forge(self):
        self.assertIn("persona-forge", self.content)

    def test_operational_flow_mentions_role_tribunal(self):
        self.assertIn("role-tribunal", self.content)

    def test_operational_flow_mentions_memory_bridge(self):
        self.assertIn("memory-bridge", self.content)

    def test_operational_flow_mentions_trust_chain(self):
        self.assertIn("trust-chain", self.content)

    def test_failure_modes_table_present(self):
        self.assertIn("|---", self.content)

    def test_failure_modes_mentions_persona_unavailable(self):
        self.assertIn("persona_unavailable", self.content)

    def test_failure_modes_mentions_role_denied(self):
        self.assertIn("role_denied", self.content)

    def test_failure_modes_mentions_constitutional_block(self):
        self.assertIn("constitutional_block", self.content)

    def test_title_uses_comma_not_em_dash_before_tier(self):
        first_line = self.content.splitlines()[0]
        self.assertIn(", TIER:", first_line)
        self.assertNotIn("— TIER:", first_line)

    def test_references_section_present(self):
        self.assertIn("## References", self.content)

    def test_advanced_techniques_mentioned(self):
        for technique in ("Progressive Disclosure", "Silent Mirror"):
            with self.subTest(technique=technique):
                self.assertIn(technique, self.content)


class TestResonanceEngineContent(unittest.TestCase):
    """Specific content checks for resonance-engine.md."""

    def setUp(self):
        self.content = _read(os.path.join(SKILLS_DIR, "resonance-engine.md"))

    def test_purpose_mentions_resonance_score(self):
        self.assertIn("resonance score", self.content.lower())

    def test_purpose_mentions_path_multiplier(self):
        self.assertIn("path multiplier", self.content.lower())

    def test_purpose_mentions_intent_dispatcher(self):
        self.assertIn("intent-dispatcher", self.content)

    def test_purpose_read_only_stated(self):
        self.assertIn("read-only", self.content)

    def test_constitutional_alignment_mentions_sovereign_constitution(self):
        self.assertIn("sovereign-constitution", self.content)

    def test_constitutional_alignment_mentions_rule_of_9(self):
        self.assertIn("rule-of-9", self.content)

    def test_constitutional_alignment_mentions_covenant_guard(self):
        self.assertIn("covenant-guard", self.content)

    def test_operational_flow_mentions_path_multipliers(self):
        # pristine=2.0, repeated=0.8, stale=0.5
        for val in ("2.0", "0.8", "0.5"):
            with self.subTest(multiplier=val):
                self.assertIn(val, self.content)

    def test_operational_flow_mentions_fractal_depth(self):
        self.assertIn("Fractal depth", self.content)

    def test_operational_flow_mentions_embedding_model(self):
        self.assertIn("embedding model", self.content.lower())

    def test_failure_modes_table_present(self):
        self.assertIn("|---", self.content)

    def test_failure_modes_mentions_confidence_below_floor(self):
        self.assertIn("confidence_below_floor", self.content)

    def test_failure_modes_mentions_multiplier_abuse(self):
        self.assertIn("Multiplier abuse", self.content)

    def test_title_uses_comma_not_em_dash_before_tier(self):
        first_line = self.content.splitlines()[0]
        self.assertIn(", TIER:", first_line)
        self.assertNotIn("— TIER:", first_line)

    def test_references_section_present(self):
        self.assertIn("## References", self.content)

    def test_numerology_table_uses_comma_not_em_dash(self):
        """In the Arabic numerology table, em-dashes were replaced with commas."""
        # The old format was "التثليث — استقرار داخلي"
        # The new format is "التثليث, استقرار داخلي"
        # We check that the em-dash variant is gone from these rows
        numerology_section = self.content
        # Look for the numeric rows — they should use commas now
        self.assertIn("التثليث, استقرار داخلي", numerology_section)
        self.assertNotIn("التثليث — استقرار داخلي", numerology_section)


# ─────────────────────────────────────────────────────────────────────────────
# Regression: all changed skills are non-empty files
# ─────────────────────────────────────────────────────────────────────────────


class TestChangedSkillFilesAreNotEmpty(unittest.TestCase):
    """Changed skill files must exist and be non-empty."""

    def test_mcts_simulator_exists_and_non_empty(self):
        path = os.path.join(SKILLS_DIR, "mcts-simulator.md")
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_prompt_evaluator_exists_and_non_empty(self):
        path = os.path.join(SKILLS_DIR, "prompt-evaluator.md")
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_prompt_weaver_exists_and_non_empty(self):
        path = os.path.join(SKILLS_DIR, "prompt-weaver.md")
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 0)

    def test_resonance_engine_exists_and_non_empty(self):
        path = os.path.join(SKILLS_DIR, "resonance-engine.md")
        self.assertTrue(os.path.isfile(path))
        self.assertGreater(os.path.getsize(path), 0)


if __name__ == "__main__":
    unittest.main()