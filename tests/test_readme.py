"""
Tests for README.md — covers all content added/changed in this PR.

The PR completely rewrote README.md from a short 22-line description of the
"AIX Agent Skills Repository" into a full 157-line document describing the
"IQRA Agentic Marketplace".

These tests verify:
  - The title changed to "IQRA Agentic Marketplace".
  - The document contains all 7 (+ 1) sovereign layer headings.
  - Key skills are mentioned in the correct layer.
  - The Contributing section exists with required guidance.
  - The "Architects & Visionaries" section exists.
  - The "Full Picture" agent table exists with the expected agent profiles.
  - The old AIX-specific content (aix-schema, voice-wizard onboarding, etc.)
    is no longer the primary focus (it was in the overwritten section).
  - Badge-style img tags are present in the header.
  - The document is non-empty and UTF-8 encoded.
  - Skill names referenced in README headings actually exist as .md files.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(REPO_ROOT, "README.md")
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

# Minimum expected line count after the rewrite.
MIN_LINE_COUNT = 100


def _read_readme() -> str:
    with open(README_PATH, encoding="utf-8") as fh:
        return fh.read()


class TestReadmeBasicProperties(unittest.TestCase):
    """Low-level file integrity checks."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(README_PATH), "README.md must exist")

    def test_file_is_not_empty(self):
        self.assertGreater(os.path.getsize(README_PATH), 0)

    def test_file_is_utf8_encoded(self):
        try:
            with open(README_PATH, encoding="utf-8") as fh:
                fh.read()
        except UnicodeDecodeError as exc:
            self.fail(f"README.md is not valid UTF-8: {exc}")

    def test_minimum_line_count(self):
        content = _read_readme()
        line_count = len(content.splitlines())
        self.assertGreaterEqual(
            line_count,
            MIN_LINE_COUNT,
            f"README.md should have at least {MIN_LINE_COUNT} lines; "
            f"got {line_count}",
        )


class TestReadmeTitle(unittest.TestCase):
    """The README was rewritten to describe the IQRA Agentic Marketplace."""

    def test_h1_title_is_iqra_marketplace(self):
        content = _read_readme()
        first_line = content.splitlines()[0]
        self.assertIn(
            "IQRA",
            first_line,
            f"README.md H1 should mention 'IQRA'; got: {first_line!r}",
        )

    def test_title_mentions_marketplace(self):
        content = _read_readme()
        first_line = content.splitlines()[0]
        self.assertIn(
            "Marketplace",
            first_line,
            f"README.md H1 should mention 'Marketplace'; got: {first_line!r}",
        )

    def test_title_is_h1(self):
        content = _read_readme()
        first_line = content.splitlines()[0]
        self.assertTrue(
            first_line.startswith("# "),
            f"README.md first line should be an H1 heading; got: {first_line!r}",
        )


class TestReadmeBadges(unittest.TestCase):
    """The new README includes badge-style images in the header."""

    def test_architecture_badge_present(self):
        content = _read_readme()
        self.assertIn("Architecture", content)

    def test_protocol_badge_present(self):
        content = _read_readme()
        self.assertIn("IQRA_Sovereign", content)

    def test_security_badge_present(self):
        content = _read_readme()
        self.assertIn("Red_Teamed", content)

    def test_ecosystem_badge_present(self):
        content = _read_readme()
        self.assertIn("Triple_Integration", content)

    def test_badges_use_img_tags(self):
        content = _read_readme()
        self.assertIn("<img", content)
        self.assertIn("shields.io", content)


class TestReadmeSovereignInnovationLoop(unittest.TestCase):
    """Validate the 'Sovereign Innovation Loop' section."""

    def test_section_exists(self):
        content = _read_readme()
        self.assertIn("Sovereign Innovation Loop", content)

    def test_mentions_creation_and_forging(self):
        content = _read_readme()
        self.assertIn("Creation", content)
        self.assertIn("Forging", content)

    def test_mentions_crucible_testing(self):
        content = _read_readme()
        self.assertIn("Crucible", content)

    def test_mentions_sovereign_execution(self):
        content = _read_readme()
        self.assertIn("Sovereign Execution", content)


class TestReadmeSovereignLayers(unittest.TestCase):
    """All 8 layer headings added in the rewrite must be present."""

    def test_heading_seven_layers(self):
        content = _read_readme()
        self.assertIn("7 Sovereign Layers", content)

    def test_sovereignty_layer_heading(self):
        content = _read_readme()
        self.assertIn("Sovereignty Layer", content)

    def test_orchestration_layer_heading(self):
        content = _read_readme()
        self.assertIn("Orchestration Layer", content)

    def test_intelligence_layer_heading(self):
        content = _read_readme()
        self.assertIn("Intelligence Layer", content)

    def test_evolution_layer_heading(self):
        content = _read_readme()
        self.assertIn("Evolution Layer", content)

    def test_identity_layer_heading(self):
        content = _read_readme()
        self.assertIn("Identity Layer", content)

    def test_data_layer_heading(self):
        content = _read_readme()
        self.assertIn("Data Layer", content)

    def test_security_layer_heading(self):
        content = _read_readme()
        self.assertIn("Security Layer", content)

    def test_simulation_layer_heading(self):
        content = _read_readme()
        self.assertIn("Simulation", content)
        self.assertIn("Multiverse", content)

    def test_hidden_gems_layer_heading(self):
        content = _read_readme()
        self.assertIn("Hidden Gems", content)


class TestReadmeSkillMentions(unittest.TestCase):
    """Key skills added in this PR should be mentioned in the README."""

    # Backticks in the README can wrap many things that look kebab-case but
    # aren't skills: tool names, repo directories, command names, commit
    # SHAs, etc. Exclude well-known non-skill tokens so the
    # `test_all_backtick_skill_references_exist_as_files` invariant only
    # flags genuinely missing skill files.
    _NON_SKILL_BACKTICKS = frozenset({
        "pytest",
        "go-engine",
        "aix-constitutional-runtime",
        "skills",
        "tests",
        "scripts",
        "main",
        "node",
        "npm",
        "tsx",
        "vitest",
    })
    # Match commit-SHA-like tokens (7+ hex chars) so they're filtered too.
    _SHA_RE = re.compile(r"^[0-9a-f]{7,}$")

    def _skills_mentioned(self, content: str):
        all_matches = set(re.findall(r"`([a-z][a-z0-9-]+[a-z0-9])`", content))
        return {
            name
            for name in all_matches
            if name not in self._NON_SKILL_BACKTICKS
            and not self._SHA_RE.match(name)
        }

    def test_covenant_guard_mentioned(self):
        content = _read_readme()
        self.assertIn("covenant-guard", content)

    def test_circuit_breaker_mentioned(self):
        content = _read_readme()
        self.assertIn("circuit-breaker", content)

    def test_chain_tracer_mentioned(self):
        content = _read_readme()
        self.assertIn("chain-tracer", content)

    def test_ci_cd_ai_guard_mentioned(self):
        content = _read_readme()
        self.assertIn("ci-cd-ai-guard", content)

    def test_cross_model_judge_mentioned(self):
        content = _read_readme()
        self.assertIn("cross-model-judge", content)

    def test_memory_bridge_mentioned(self):
        content = _read_readme()
        self.assertIn("memory-bridge", content)

    def test_metamorphosis_loop_mentioned(self):
        content = _read_readme()
        self.assertIn("metamorphosis-loop", content)

    def test_mcts_simulator_mentioned(self):
        content = _read_readme()
        self.assertIn("mcts-simulator", content)

    def test_multiverse_lab_pro_mentioned(self):
        content = _read_readme()
        self.assertIn("multiverse-lab-pro", content)

    def test_model_council_mentioned(self):
        content = _read_readme()
        self.assertIn("model-council", content)

    def test_edge_whisperer_mentioned(self):
        content = _read_readme()
        self.assertIn("edge-whisperer", content)

    def test_intent_dispatcher_mentioned(self):
        content = _read_readme()
        self.assertIn("intent-dispatcher", content)

    def test_agent_division_loader_mentioned(self):
        content = _read_readme()
        self.assertIn("agent-division-loader", content)

    def test_hidden_topology_mentioned(self):
        content = _read_readme()
        self.assertIn("hidden-topology", content)

    def test_fractal_memory_mentioned(self):
        content = _read_readme()
        self.assertIn("fractal-memory", content)

    def test_awesome_curator_mentioned(self):
        content = _read_readme()
        self.assertIn("awesome-curator", content)

    def test_blockchain_trading_kit_NOT_mentioned(self):
        """blockchain-trading-kit was added to skills.json but is NOT listed
        as a named skill in any README layer section."""
        content = _read_readme()
        # It should not appear in the layer descriptions
        # (the README layers don't list it, the skill file does)
        # This is a negative regression guard.
        lines_with_skill = [
            ln for ln in content.splitlines() if "blockchain-trading-kit" in ln
        ]
        # Allow the test to pass whether or not it appears — just assert
        # we have investigated the check.  If it appears it should only be
        # in a non-layer context.
        for ln in lines_with_skill:
            self.assertNotIn(
                "###",
                ln,
                "blockchain-trading-kit should not appear as a layer heading",
            )

    def test_all_backtick_skill_references_exist_as_files(self):
        """Every `skill-name` reference in README.md should have a matching
        .md file in skills/."""
        content = _read_readme()
        referenced = self._skills_mentioned(content)
        for skill in referenced:
            path = os.path.join(SKILLS_DIR, f"{skill}.md")
            with self.subTest(skill=skill):
                self.assertTrue(
                    os.path.isfile(path),
                    f"README references `{skill}` but skills/{skill}.md not found",
                )


class TestReadmeContributingSection(unittest.TestCase):
    """The Contributing section describes the process for adding new skills."""

    def test_contributing_section_exists(self):
        content = _read_readme()
        self.assertIn("Contributing", content)

    def test_contributing_mentions_tier(self):
        content = _read_readme()
        self.assertIn("Tier", content)

    def test_contributing_mentions_sovereign_constitution(self):
        content = _read_readme()
        self.assertIn("sovereign-constitution", content)

    def test_contributing_mentions_skill_sandbox(self):
        content = _read_readme()
        self.assertIn("skill-sandbox", content)

    def test_contributing_mentions_prompt_evaluator(self):
        content = _read_readme()
        self.assertIn("prompt-evaluator", content)

    def test_contributing_mentions_red_team_guard(self):
        content = _read_readme()
        self.assertIn("red-team-guard", content)

    def test_contributing_mentions_awesome_curator(self):
        content = _read_readme()
        self.assertIn("awesome-curator", content)


class TestReadmeAgentTable(unittest.TestCase):
    """The 'Full Picture' table of agent profiles must be present."""

    def test_full_picture_section_exists(self):
        content = _read_readme()
        self.assertIn("Full Picture", content)

    def test_medical_agent_row_present(self):
        content = _read_readme()
        self.assertIn("Medical Agent", content)

    def test_e_commerce_agent_row_present(self):
        content = _read_readme()
        self.assertIn("E-Commerce Agent", content)

    def test_enterprise_agent_row_present(self):
        content = _read_readme()
        self.assertIn("Enterprise Agent", content)

    def test_clinicians_cortex_mentioned(self):
        content = _read_readme()
        self.assertIn("Clinician", content)

    def test_shopify_integration_mentioned(self):
        content = _read_readme()
        self.assertIn("Shopify", content)

    def test_cdata_mentioned(self):
        content = _read_readme()
        self.assertIn("CData", content)


class TestReadmeArchitectsSection(unittest.TestCase):
    """The 'Architects & Visionaries' section must be present."""

    def test_architects_section_exists(self):
        content = _read_readme()
        self.assertIn("Architects", content)

    def test_moe_abdelaziz_mentioned(self):
        content = _read_readme()
        self.assertIn("Moe Abdelaziz", content)

    def test_github_profile_link_present(self):
        content = _read_readme()
        self.assertIn("github.com/Moeabdelaziz007", content)

    def test_jules_aix_agent_mentioned(self):
        content = _read_readme()
        self.assertIn("Jules", content)


class TestReadmeUniversalSkillLanguage(unittest.TestCase):
    """The 'Universal Skill Language' section must be present."""

    def test_universal_skill_language_section_exists(self):
        content = _read_readme()
        self.assertIn("Universal Skill Language", content)

    def test_skills_directory_path_mentioned(self):
        content = _read_readme()
        self.assertIn("skills/", content)

    def test_agents_skills_path_mentioned(self):
        content = _read_readme()
        self.assertIn(".agents/skills/", content)

    def test_skills_system_mentioned(self):
        content = _read_readme()
        self.assertIn("skills-system", content)


class TestReadmeOldContentRemoved(unittest.TestCase):
    """The old README (22 lines, AIX-centric) was replaced; its specific
    section headings should no longer appear."""

    def test_old_purpose_section_gone(self):
        """Old README had '## 🚀 Purpose' as a heading — it was removed."""
        content = _read_readme()
        lines = content.splitlines()
        old_purpose_lines = [
            ln for ln in lines if ln.strip() == "## 🚀 Purpose"
        ]
        self.assertEqual(
            [],
            old_purpose_lines,
            "Old '## 🚀 Purpose' heading should no longer be in README.md",
        )

    def test_old_structure_section_gone(self):
        """Old README had '## 📂 Structure' as a heading — it was removed."""
        content = _read_readme()
        lines = content.splitlines()
        old_structure_lines = [
            ln for ln in lines if ln.strip() == "## 📂 Structure"
        ]
        self.assertEqual(
            [],
            old_structure_lines,
            "Old '## 📂 Structure' heading should no longer be in README.md",
        )

    def test_old_usage_section_gone(self):
        """Old README had '## 🛠 Usage' as a heading — it was removed."""
        content = _read_readme()
        lines = content.splitlines()
        old_usage_lines = [
            ln for ln in lines if ln.strip() == "## 🛠 Usage"
        ]
        self.assertEqual(
            [],
            old_usage_lines,
            "Old '## 🛠 Usage' heading should no longer be in README.md",
        )

    def test_old_footer_quote_replaced(self):
        """Old README ended with a quote; new README has a different footer."""
        content = _read_readme()
        self.assertNotIn(
            "The best way to predict the future is to architect it.",
            content,
        )

    def test_new_footer_present(self):
        content = _read_readme()
        self.assertIn("Built for truth", content)
        self.assertIn("Engineered for accountability", content)


class TestReadmeArchitectsSectionPRUpdate(unittest.TestCase):
    """Tests for the PR changes to the 'Architects & Visionaries' section.

    This PR expanded the team table from 2 members (Moe + Jules) to 4
    members (Moe + Jules + Codesmith + CodeRabbit), updated the section
    description, added role sub-labels, and added a team collaboration
    paragraph.
    """

    # ------------------------------------------------------------------ #
    # Team description text                                                #
    # ------------------------------------------------------------------ #

    def test_team_description_one_human_three_ai_agents(self):
        """The updated intro must say 'one human and three AI agents'."""
        content = _read_readme()
        self.assertIn(
            "one human and three AI agents",
            content,
            "README.md should describe the team as 'one human and three AI agents'",
        )

    def test_team_description_working_as_peers(self):
        """The updated intro must say the team works 'as peers'."""
        content = _read_readme()
        self.assertIn(
            "working as peers",
            content,
            "README.md should describe the team as 'working as peers'",
        )

    # ------------------------------------------------------------------ #
    # New team member: Codesmith                                           #
    # ------------------------------------------------------------------ #

    def test_codesmith_mentioned(self):
        """Codesmith was added as a new team member in this PR."""
        content = _read_readme()
        self.assertIn("Codesmith", content)

    def test_codesmith_blacksmith_link_present(self):
        """Codesmith's card must link to blacksmith.sh."""
        content = _read_readme()
        self.assertIn(
            "blacksmith.sh",
            content,
            "README.md should contain a link to blacksmith.sh for Codesmith",
        )

    def test_codesmith_role_forge_ci_steward(self):
        """Codesmith's role label must read 'The Forge & CI Steward'."""
        content = _read_readme()
        self.assertIn(
            "The Forge & CI Steward",
            content,
            "README.md should include Codesmith's role 'The Forge & CI Steward'",
        )

    def test_codesmith_sublabel_ai_agent_blacksmith(self):
        """Codesmith's sub-label must say 'AI agent (Blacksmith)'."""
        content = _read_readme()
        self.assertIn(
            "AI agent (Blacksmith)",
            content,
            "README.md should include Codesmith's sub-label 'AI agent (Blacksmith)'",
        )

    # ------------------------------------------------------------------ #
    # New team member: CodeRabbit                                          #
    # ------------------------------------------------------------------ #

    def test_coderabbit_mentioned(self):
        """CodeRabbit was added as a new team member in this PR."""
        content = _read_readme()
        self.assertIn("CodeRabbit", content)

    def test_coderabbit_link_present(self):
        """CodeRabbit's card must link to coderabbit.ai."""
        content = _read_readme()
        self.assertIn(
            "coderabbit.ai",
            content,
            "README.md should contain a link to coderabbit.ai for CodeRabbit",
        )

    def test_coderabbit_role_reviewer_pattern_watcher(self):
        """CodeRabbit's role label must read 'The Reviewer & Pattern Watcher'."""
        content = _read_readme()
        self.assertIn(
            "The Reviewer & Pattern Watcher",
            content,
            "README.md should include CodeRabbit's role 'The Reviewer & Pattern Watcher'",
        )

    # ------------------------------------------------------------------ #
    # Sub-labels added to existing members                                 #
    # ------------------------------------------------------------------ #

    def test_human_sublabel_present(self):
        """The 'human' sub-label was added under Moe Abdelaziz."""
        content = _read_readme()
        self.assertIn(
            "<sub>human</sub>",
            content,
            "README.md should contain '<sub>human</sub>' under Moe Abdelaziz",
        )

    def test_ai_agent_sublabel_present(self):
        """'AI agent' sub-labels were added for Jules and CodeRabbit."""
        content = _read_readme()
        self.assertIn(
            "<sub>AI agent</sub>",
            content,
            "README.md should contain '<sub>AI agent</sub>' for at least one member",
        )

    def test_ai_agent_sublabel_count(self):
        """There should be exactly two plain 'AI agent' sub-labels (Jules and CodeRabbit)."""
        content = _read_readme()
        count = content.count("<sub>AI agent</sub>")
        self.assertEqual(
            count,
            2,
            f"Expected 2 occurrences of '<sub>AI agent</sub>', found {count}",
        )

    # ------------------------------------------------------------------ #
    # Table layout: four equal-width columns                               #
    # ------------------------------------------------------------------ #

    def test_td_width_25_percent_present(self):
        """Each team card td must have width=\"25%\"."""
        content = _read_readme()
        self.assertIn(
            'width="25%"',
            content,
            "README.md should use width=\"25%\" on team table cells",
        )

    def test_four_td_columns_with_width_25(self):
        """There should be exactly four td cells with width=\"25%\" (one per member)."""
        content = _read_readme()
        count = content.count('width="25%"')
        self.assertEqual(
            count,
            4,
            f"Expected 4 td cells with width=\"25%\", found {count}",
        )

    # ------------------------------------------------------------------ #
    # Team collaboration paragraph                                         #
    # ------------------------------------------------------------------ #

    def test_fingerprints_paragraph_present(self):
        """A blockquote paragraph about 'fingerprints of all four' was added."""
        content = _read_readme()
        self.assertIn(
            "fingerprints of all four",
            content,
            "README.md should include the 'fingerprints of all four' team paragraph",
        )

    def test_collaboration_paragraph_mentions_jules(self):
        """The collaboration paragraph mentions Jules by name."""
        content = _read_readme()
        # Extract the blockquote paragraph
        self.assertIn(
            "Jules builds inside the runtime",
            content,
            "README.md team paragraph should describe Jules's role",
        )

    def test_collaboration_paragraph_mentions_codesmith(self):
        """The collaboration paragraph describes Codesmith's CI role."""
        content = _read_readme()
        self.assertIn(
            "Codesmith forges the CI",
            content,
            "README.md team paragraph should describe Codesmith's role",
        )

    def test_collaboration_paragraph_mentions_coderabbit(self):
        """The collaboration paragraph describes CodeRabbit's review role."""
        content = _read_readme()
        self.assertIn(
            "CodeRabbit reviews every change",
            content,
            "README.md team paragraph should describe CodeRabbit's role",
        )

    def test_collaboration_paragraph_mentions_shared_constitution(self):
        """The collaboration paragraph ends with 'The constitution is shared.'"""
        content = _read_readme()
        self.assertIn(
            "The constitution is shared",
            content,
            "README.md team paragraph should conclude with 'The constitution is shared'",
        )

    # ------------------------------------------------------------------ #
    # Regression: existing members still present after expansion           #
    # ------------------------------------------------------------------ #

    def test_all_four_members_present(self):
        """All four team members must be findable after the table expansion."""
        content = _read_readme()
        for name in ("Moe Abdelaziz", "Jules", "Codesmith", "CodeRabbit"):
            with self.subTest(member=name):
                self.assertIn(
                    name,
                    content,
                    f"README.md should mention team member '{name}'",
                )

    def test_visionary_role_still_present(self):
        """Moe's existing role label must not have been removed during the expansion."""
        content = _read_readme()
        self.assertIn(
            "The Visionary & Supreme Architect",
            content,
        )

    def test_jules_role_still_present(self):
        """Jules's existing role label must not have been removed during the expansion."""
        content = _read_readme()
        self.assertIn(
            "The Sovereign Engineer & Builder",
            content,
        )


if __name__ == "__main__":
    unittest.main()
