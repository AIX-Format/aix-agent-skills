"""
Tests for the new skill Markdown files added in this PR.

Each new skill file should conform to the shared format used across the
skills/ directory:

  Line 1  : H1 heading that contains both the Arabic name, the English name
             in parentheses, and `TIER: <VALUE>`.
  Body    : At minimum an `## الجوهر` (Essence/Core) section.
  Encoding: UTF-8.
  Size    : Non-trivially small (> 100 bytes).

Files added in this PR that are covered by these tests:
  agent-division-loader.md, awesome-curator.md, blockchain-trading-kit.md,
  chain-tracer.md, ci-cd-ai-guard.md, circuit-breaker.md,
  community-support-layer.md, covenant-guard.md, cross-model-judge.md,
  data-alchemist.md, edge-whisperer.md, fine-tuned-vault.md,
  fractal-memory.md, hidden-topology.md, integration-packs.md,
  intent-dispatcher.md, mcts-simulator.md, memory-bridge.md,
  metamorphosis-loop.md, mission-control.md, model-council.md,
  multi-tool-exporter.md, multiverse-lab-pro.md
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

# Exact set of .md files added by this PR (scope of tests).
NEW_SKILL_FILES = [
    "agent-division-loader.md",
    "awesome-curator.md",
    "blockchain-trading-kit.md",
    "chain-tracer.md",
    "ci-cd-ai-guard.md",
    "circuit-breaker.md",
    "community-support-layer.md",
    "covenant-guard.md",
    "cross-model-judge.md",
    "data-alchemist.md",
    "edge-whisperer.md",
    "fine-tuned-vault.md",
    "fractal-memory.md",
    "hidden-topology.md",
    "integration-packs.md",
    "intent-dispatcher.md",
    "mcts-simulator.md",
    "memory-bridge.md",
    "metamorphosis-loop.md",
    "mission-control.md",
    "model-council.md",
    "multi-tool-exporter.md",
    "multiverse-lab-pro.md",
]

# Valid TIER tokens as they appear after "TIER: " in the heading.
VALID_TIERS = {
    "SOVEREIGN",
    "SOVEREIGN (META-PACK)",
    "ADVANCED_INFRASTRUCTURE",
    "PRO",
    "ADVANCED_TOOL",
    "BASIC_TOOL",
}

# Regex that matches the TIER portion of a heading line, capturing the value.
TIER_RE = re.compile(r"—\s*TIER:\s*(.+)$")

# Regex for an English name enclosed in parentheses.
ENGLISH_NAME_RE = re.compile(r"\(([A-Za-z][A-Za-z0-9 /\-&]+)\)")

# Minimum content length (bytes) for a skill file to be considered non-trivial.
MIN_FILE_SIZE = 200


def _read_file(filename: str) -> str:
    path = os.path.join(SKILLS_DIR, filename)
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class TestNewSkillFilesExist(unittest.TestCase):
    """Every new skill file must be present in the skills/ directory."""

    def test_all_new_files_exist(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                path = os.path.join(SKILLS_DIR, filename)
                self.assertTrue(
                    os.path.isfile(path),
                    f"Expected skill file not found: {filename}",
                )

    def test_files_are_not_empty(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                path = os.path.join(SKILLS_DIR, filename)
                size = os.path.getsize(path)
                self.assertGreater(
                    size,
                    0,
                    f"Skill file is empty: {filename}",
                )

    def test_files_are_non_trivially_sized(self):
        """Each skill file should contain meaningful content."""
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                path = os.path.join(SKILLS_DIR, filename)
                size = os.path.getsize(path)
                self.assertGreater(
                    size,
                    MIN_FILE_SIZE,
                    f"Skill file '{filename}' is suspiciously small ({size} bytes)",
                )

    def test_files_are_utf8_encoded(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                path = os.path.join(SKILLS_DIR, filename)
                try:
                    with open(path, encoding="utf-8") as fh:
                        fh.read()
                except UnicodeDecodeError as exc:
                    self.fail(f"'{filename}' is not valid UTF-8: {exc}")


class TestSkillFileTitleLine(unittest.TestCase):
    """Validate the H1 title line of each new skill file."""

    def _get_first_line(self, filename: str) -> str:
        content = _read_file(filename)
        return content.splitlines()[0]

    def test_first_line_is_h1_heading(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                first_line = self._get_first_line(filename)
                self.assertTrue(
                    first_line.startswith("# "),
                    f"'{filename}' first line is not an H1 heading: {first_line!r}",
                )

    def test_title_contains_tier_marker(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                first_line = self._get_first_line(filename)
                self.assertIn(
                    "TIER:",
                    first_line,
                    f"'{filename}' title does not contain 'TIER:': {first_line!r}",
                )

    def test_title_contains_english_name_in_parentheses(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                first_line = self._get_first_line(filename)
                match = ENGLISH_NAME_RE.search(first_line)
                self.assertIsNotNone(
                    match,
                    f"'{filename}' title does not contain an English name in "
                    f"parentheses: {first_line!r}",
                )

    def test_tier_value_is_valid(self):
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                first_line = self._get_first_line(filename)
                m = TIER_RE.search(first_line)
                self.assertIsNotNone(
                    m,
                    f"Cannot parse TIER value from '{filename}': {first_line!r}",
                )
                tier_value = m.group(1).strip()
                self.assertIn(
                    tier_value,
                    VALID_TIERS,
                    f"'{filename}' has unrecognised TIER value: '{tier_value}'",
                )

    def test_title_uses_em_dash_separator(self):
        """Convention is to separate name and TIER with ' — '."""
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                first_line = self._get_first_line(filename)
                self.assertIn(
                    "—",
                    first_line,
                    f"'{filename}' title should use em-dash (—) before TIER",
                )


class TestSkillFileSections(unittest.TestCase):
    """Each new skill file must contain the required Arabic section headings."""

    def test_has_jawhar_section(self):
        """Every skill file must have ## الجوهر (Essence/Core) section."""
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                content = _read_file(filename)
                self.assertIn(
                    "## الجوهر",
                    content,
                    f"'{filename}' is missing the '## الجوهر' section",
                )

    def test_jawhar_section_has_content(self):
        """The الجوهر section must contain at least one non-blank line of body."""
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                content = _read_file(filename)
                lines = content.splitlines()
                try:
                    idx = next(
                        i for i, ln in enumerate(lines) if ln.strip() == "## الجوهر"
                    )
                except StopIteration:
                    self.fail(f"'{filename}' missing ## الجوهر section")
                    return
                # Look for a non-blank, non-heading line after the section title.
                body_lines = [
                    ln
                    for ln in lines[idx + 1 :]
                    if ln.strip() and not ln.startswith("## ")
                ]
                self.assertGreater(
                    len(body_lines),
                    0,
                    f"'{filename}' ## الجوهر section appears to have no body text",
                )

    def test_has_at_least_two_sections(self):
        """Each file should have at minimum 2 ## sections (core + at least one more)."""
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                content = _read_file(filename)
                section_count = sum(
                    1 for ln in content.splitlines() if ln.startswith("## ")
                )
                self.assertGreaterEqual(
                    section_count,
                    2,
                    f"'{filename}' has fewer than 2 ## sections ({section_count})",
                )

    def test_no_raw_html_in_content(self):
        """Skill files should not contain raw HTML tags."""
        for filename in NEW_SKILL_FILES:
            with self.subTest(filename=filename):
                content = _read_file(filename)
                # A simple heuristic — look for opening HTML tags.
                html_tag_re = re.compile(r"<[a-zA-Z][^>]*>")
                matches = html_tag_re.findall(content)
                self.assertEqual(
                    [],
                    matches,
                    f"'{filename}' contains raw HTML: {matches[:5]}",
                )


class TestSpecificSkillFiles(unittest.TestCase):
    """Content-level spot-checks for individual new skill files."""

    # --- covenant-guard.md ---

    def test_covenant_guard_tier_is_sovereign(self):
        content = _read_file("covenant-guard.md")
        self.assertIn("TIER: SOVEREIGN", content.splitlines()[0])

    def test_covenant_guard_has_typescript_code_block(self):
        content = _read_file("covenant-guard.md")
        self.assertIn("```typescript", content)

    def test_covenant_guard_defines_covenant_signature_interface(self):
        content = _read_file("covenant-guard.md")
        self.assertIn("CovenantSignature", content)

    def test_covenant_guard_mentions_ed25519(self):
        content = _read_file("covenant-guard.md")
        self.assertIn("Ed25519", content)

    def test_covenant_guard_mentions_renewal_cycle(self):
        content = _read_file("covenant-guard.md")
        self.assertIn("49", content)

    # --- chain-tracer.md ---

    def test_chain_tracer_tier_is_pro(self):
        content = _read_file("chain-tracer.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_chain_tracer_has_json_code_block(self):
        content = _read_file("chain-tracer.md")
        self.assertIn("```json", content)

    def test_chain_tracer_span_structure_has_span_id(self):
        content = _read_file("chain-tracer.md")
        self.assertIn("span_id", content)

    def test_chain_tracer_span_structure_has_duration_ms(self):
        content = _read_file("chain-tracer.md")
        self.assertIn("duration_ms", content)

    def test_chain_tracer_span_structure_has_cost_usd(self):
        content = _read_file("chain-tracer.md")
        self.assertIn("cost_usd", content)

    def test_chain_tracer_mentions_data_lineage(self):
        content = _read_file("chain-tracer.md")
        self.assertIn("Lineage", content)

    # --- circuit-breaker.md ---

    def test_circuit_breaker_tier_is_advanced_infrastructure(self):
        content = _read_file("circuit-breaker.md")
        self.assertIn("TIER: ADVANCED_INFRASTRUCTURE", content.splitlines()[0])

    def test_circuit_breaker_lists_three_states(self):
        content = _read_file("circuit-breaker.md")
        self.assertIn("Closed", content)
        self.assertIn("Half-Open", content)
        self.assertIn("Open", content)

    def test_circuit_breaker_mentions_failure_threshold(self):
        content = _read_file("circuit-breaker.md")
        # File mentions "5 فشل متتالي" (5 consecutive failures)
        self.assertIn("5", content)

    # --- ci-cd-ai-guard.md ---

    def test_ci_cd_ai_guard_tier_is_pro(self):
        content = _read_file("ci-cd-ai-guard.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_ci_cd_ai_guard_mentions_pre_commit(self):
        content = _read_file("ci-cd-ai-guard.md")
        self.assertIn("Pre-commit", content)

    def test_ci_cd_ai_guard_mentions_pre_deploy(self):
        content = _read_file("ci-cd-ai-guard.md")
        self.assertIn("Pre-deploy", content)

    # --- cross-model-judge.md ---

    def test_cross_model_judge_tier_is_pro(self):
        content = _read_file("cross-model-judge.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_cross_model_judge_mentions_three_models(self):
        content = _read_file("cross-model-judge.md")
        self.assertIn("3", content)

    def test_cross_model_judge_references_trust_chain(self):
        content = _read_file("cross-model-judge.md")
        self.assertIn("trust-chain", content)

    # --- data-alchemist.md ---

    def test_data_alchemist_tier_is_basic_tool(self):
        content = _read_file("data-alchemist.md")
        self.assertIn("TIER: BASIC_TOOL", content.splitlines()[0])

    def test_data_alchemist_has_three_phases(self):
        content = _read_file("data-alchemist.md")
        self.assertIn("Transform", content)
        self.assertIn("Analyze", content)
        self.assertIn("Visualize", content)

    # --- edge-whisperer.md ---

    def test_edge_whisperer_tier_is_pro(self):
        content = _read_file("edge-whisperer.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_edge_whisperer_mentions_webgpu(self):
        content = _read_file("edge-whisperer.md")
        self.assertIn("WebGPU", content)

    def test_edge_whisperer_mentions_wasm(self):
        content = _read_file("edge-whisperer.md")
        self.assertIn("WASM", content)

    # --- fine-tuned-vault.md ---

    def test_fine_tuned_vault_tier_is_pro(self):
        content = _read_file("fine-tuned-vault.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_fine_tuned_vault_mentions_lazy_loading(self):
        content = _read_file("fine-tuned-vault.md")
        self.assertIn("Lazy Loading", content)

    # --- fractal-memory.md ---

    def test_fractal_memory_tier_is_pro(self):
        content = _read_file("fractal-memory.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_fractal_memory_has_compression_levels(self):
        """Should mention L0 through L4 compression levels."""
        content = _read_file("fractal-memory.md")
        for level in ("L0", "L1", "L2", "L3", "L4"):
            self.assertIn(
                level, content, f"fractal-memory.md missing compression level {level}"
            )

    # --- hidden-topology.md ---

    def test_hidden_topology_tier_is_pro(self):
        content = _read_file("hidden-topology.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_hidden_topology_has_api_endpoint(self):
        content = _read_file("hidden-topology.md")
        self.assertIn("/api/iqra/topology/hidden", content)

    def test_hidden_topology_mentions_graphml(self):
        content = _read_file("hidden-topology.md")
        self.assertIn("graphml", content)

    # --- integration-packs.md ---

    def test_integration_packs_tier_is_pro(self):
        content = _read_file("integration-packs.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_integration_packs_mentions_shopify(self):
        content = _read_file("integration-packs.md")
        self.assertIn("Shopify", content)

    def test_integration_packs_mentions_whatsapp(self):
        content = _read_file("integration-packs.md")
        self.assertIn("WhatsApp", content)

    # --- intent-dispatcher.md ---

    def test_intent_dispatcher_tier_is_advanced_tool(self):
        content = _read_file("intent-dispatcher.md")
        self.assertIn("TIER: ADVANCED_TOOL", content.splitlines()[0])

    def test_intent_dispatcher_has_four_steps(self):
        content = _read_file("intent-dispatcher.md")
        self.assertIn("4", content)

    def test_intent_dispatcher_mentions_pipeline_store(self):
        content = _read_file("intent-dispatcher.md")
        self.assertIn("pipeline-store", content)

    # --- mcts-simulator.md ---

    def test_mcts_simulator_tier_is_pro(self):
        content = _read_file("mcts-simulator.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_mcts_simulator_has_four_phases(self):
        content = _read_file("mcts-simulator.md")
        self.assertIn("Selection", content)
        self.assertIn("Expansion", content)
        self.assertIn("Simulation", content)
        self.assertIn("Backpropagation", content)

    # --- memory-bridge.md ---

    def test_memory_bridge_tier_is_advanced_infrastructure(self):
        content = _read_file("memory-bridge.md")
        self.assertIn("TIER: ADVANCED_INFRASTRUCTURE", content.splitlines()[0])

    def test_memory_bridge_has_five_tiers(self):
        content = _read_file("memory-bridge.md")
        self.assertIn("Hot", content)
        self.assertIn("Warm", content)
        self.assertIn("Cold", content)
        self.assertIn("Vector", content)
        self.assertIn("Archive", content)

    # --- metamorphosis-loop.md ---

    def test_metamorphosis_loop_tier_is_pro(self):
        content = _read_file("metamorphosis-loop.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_metamorphosis_loop_references_49_tasks(self):
        content = _read_file("metamorphosis-loop.md")
        self.assertIn("49", content)

    def test_metamorphosis_loop_has_json_log_structure(self):
        content = _read_file("metamorphosis-loop.md")
        self.assertIn("cycleNumber", content)
        self.assertIn("integrityScore", content)

    # --- mission-control.md ---

    def test_mission_control_tier_is_pro(self):
        content = _read_file("mission-control.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_mission_control_has_seven_phase_cycle(self):
        content = _read_file("mission-control.md")
        self.assertIn("7", content)

    def test_mission_control_has_worker_chain(self):
        content = _read_file("mission-control.md")
        self.assertIn("Planner", content)
        self.assertIn("Validator", content)

    # --- model-council.md ---

    def test_model_council_tier_is_pro(self):
        content = _read_file("model-council.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_model_council_mentions_three_model_levels(self):
        content = _read_file("model-council.md")
        self.assertIn("local", content.lower())
        self.assertIn("edge", content.lower())
        self.assertIn("cloud", content.lower())

    def test_model_council_mentions_fallback(self):
        content = _read_file("model-council.md")
        self.assertIn("Fallback", content)

    # --- multi-tool-exporter.md ---

    def test_multi_tool_exporter_tier_is_advanced_tool(self):
        content = _read_file("multi-tool-exporter.md")
        self.assertIn("TIER: ADVANCED_TOOL", content.splitlines()[0])

    def test_multi_tool_exporter_mentions_cli(self):
        content = _read_file("multi-tool-exporter.md")
        self.assertIn("CLI", content)

    def test_multi_tool_exporter_mentions_sovereign_constitution(self):
        content = _read_file("multi-tool-exporter.md")
        self.assertIn("sovereign-constitution", content)

    # --- multiverse-lab-pro.md ---

    def test_multiverse_lab_pro_tier_is_sovereign(self):
        content = _read_file("multiverse-lab-pro.md")
        first_line = content.splitlines()[0]
        self.assertIn("TIER: SOVEREIGN", first_line)

    def test_multiverse_lab_pro_mentions_shadow_forge(self):
        content = _read_file("multiverse-lab-pro.md")
        self.assertIn("Shadow Forge", content)

    def test_multiverse_lab_pro_mentions_three_topological_twins(self):
        content = _read_file("multiverse-lab-pro.md")
        self.assertIn("3", content)

    # --- agent-division-loader.md ---

    def test_agent_division_loader_tier_is_advanced_tool(self):
        content = _read_file("agent-division-loader.md")
        self.assertIn("TIER: ADVANCED_TOOL", content.splitlines()[0])

    def test_agent_division_loader_lists_divisions(self):
        content = _read_file("agent-division-loader.md")
        self.assertIn("Engineering", content)
        self.assertIn("Security", content)

    # --- awesome-curator.md ---

    def test_awesome_curator_tier_is_advanced_infrastructure(self):
        content = _read_file("awesome-curator.md")
        self.assertIn("TIER: ADVANCED_INFRASTRUCTURE", content.splitlines()[0])

    def test_awesome_curator_mentions_pull_request(self):
        content = _read_file("awesome-curator.md")
        self.assertIn("pull request", content.lower())

    def test_awesome_curator_mentions_skill_evaluator(self):
        content = _read_file("awesome-curator.md")
        self.assertIn("skill-evaluator", content)

    # --- blockchain-trading-kit.md ---

    def test_blockchain_trading_kit_tier_is_pro(self):
        content = _read_file("blockchain-trading-kit.md")
        self.assertIn("TIER: PRO", content.splitlines()[0])

    def test_blockchain_trading_kit_has_four_layer_architecture(self):
        content = _read_file("blockchain-trading-kit.md")
        self.assertIn("Data Layer", content)
        self.assertIn("Execution Layer", content)
        self.assertIn("Intelligence Layer", content)
        self.assertIn("Security Layer", content)

    def test_blockchain_trading_kit_mentions_ccxt(self):
        content = _read_file("blockchain-trading-kit.md")
        self.assertIn("CCXT", content)

    def test_blockchain_trading_kit_mentions_circuit_breaker_integration(self):
        content = _read_file("blockchain-trading-kit.md")
        self.assertIn("circuit-breaker", content)

    # --- community-support-layer.md ---

    def test_community_support_layer_tier_is_advanced_infrastructure(self):
        content = _read_file("community-support-layer.md")
        self.assertIn("TIER: ADVANCED_INFRASTRUCTURE", content.splitlines()[0])

    def test_community_support_layer_mentions_github_discussions(self):
        content = _read_file("community-support-layer.md")
        self.assertIn("GitHub Discussions", content)

    def test_community_support_layer_mentions_awesome_curator_integration(self):
        content = _read_file("community-support-layer.md")
        self.assertIn("awesome-curator", content)


class TestSkillFilesIntegrationReferences(unittest.TestCase):
    """Validate that cross-skill references in new files refer to skills
    that actually exist in the repository.

    Notes
    -----
    Some skill files (e.g. awesome-curator.md) use backticks for *example*
    list names such as `awesome-sales-skills` or `awesome-prompt-engineering`.
    Those are not real skill files — they are hypothetical examples used to
    illustrate the curator concept.  We exclude backtick tokens that start
    with `awesome-` (which is never a real standalone skill) to avoid false
    positives.
    """

    # Prefixes that are used for illustrative examples, not real skill names.
    _EXAMPLE_PREFIXES = ("awesome-sales-", "awesome-prompt-", "awesome-")

    def _extract_skill_references(self, content: str):
        """Return the set of skill names referenced via backtick notation,
        excluding known documentation-only example tokens."""
        candidates = set(re.findall(r"`([a-z][a-z0-9-]+[a-z0-9])`", content))
        # Filter out example tokens that are not real skills.
        return {
            ref
            for ref in candidates
            if not any(ref.startswith(pfx) for pfx in self._EXAMPLE_PREFIXES)
        }

    def test_referenced_skills_exist(self):
        """Every `skill-name` cross-reference inside a new file should have a
        matching .md file in skills/ (guards against typos)."""
        for filename in NEW_SKILL_FILES:
            content = _read_file(filename)
            references = self._extract_skill_references(content)
            for ref in references:
                ref_path = os.path.join(SKILLS_DIR, f"{ref}.md")
                with self.subTest(file=filename, reference=ref):
                    self.assertTrue(
                        os.path.isfile(ref_path),
                        f"'{filename}' references `{ref}` but "
                        f"skills/{ref}.md does not exist",
                    )

    def test_awesome_curator_example_references_are_excluded(self):
        """awesome-curator.md uses `awesome-sales-skills` and similar tokens as
        documentation examples — these must *not* be treated as skill names."""
        content = _read_file("awesome-curator.md")
        all_tokens = set(re.findall(r"`([a-z][a-z0-9-]+[a-z0-9])`", content))
        # These example names must appear in the raw token set.
        self.assertIn("awesome-sales-skills", all_tokens)
        self.assertIn("awesome-prompt-engineering", all_tokens)
        # But they must NOT exist as actual .md skill files.
        for example in ("awesome-sales-skills", "awesome-prompt-engineering"):
            path = os.path.join(SKILLS_DIR, f"{example}.md")
            self.assertFalse(
                os.path.isfile(path),
                f"'{example}.md' should not exist — it is a documentation example",
            )


if __name__ == "__main__":
    unittest.main()