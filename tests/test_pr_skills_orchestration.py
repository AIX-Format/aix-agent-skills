"""
Tests for skill files changed in this PR.

This PR filled in stub placeholders for four orchestration skills:
  - skills/intent-dispatcher.md
  - skills/mission-control.md
  - skills/role-tribunal.md
  - skills/topology-orchestrator.md

For all four files the PR:
  1. Changed the heading tier separator from "— TIER:" to ", TIER:".
  2. Replaced "TODO: Define purpose." with real content in ## Purpose.
  3. Replaced "TODO: Define constitutional alignment." with real content.
  4. Replaced "TODO: Define operational flow." with real content.
  5. Replaced "TODO: Define failure modes." with a real failure-mode table.

In addition, topology-orchestrator.md had one Arabic sentence updated:
  old: تُسجَّل "بصمة رنين" — تردد النجاح بين المهارات.
  new: تُسجَّل "بصمة رنين": تردد النجاح بين المهارات.

These tests cover all five categories plus skill-specific content assertions.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

CHANGED_SKILLS = [
    "intent-dispatcher",
    "mission-control",
    "role-tribunal",
    "topology-orchestrator",
]

REQUIRED_SECTIONS = [
    "## Purpose",
    "## Constitutional Alignment",
    "## Operational Flow",
    "## Failure Modes",
]

TODO_STUBS = [
    "TODO: Define purpose.",
    "TODO: Define constitutional alignment.",
    "TODO: Define operational flow.",
    "TODO: Define failure modes.",
]


def _skill_path(name: str) -> str:
    return os.path.join(SKILLS_DIR, f"{name}.md")


def _read(name: str) -> str:
    with open(_skill_path(name), encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Shared tests applied to all four skills
# ---------------------------------------------------------------------------

class TestAllChangedSkillsExist(unittest.TestCase):
    """Basic existence check for each file."""

    def test_all_four_skill_files_exist(self):
        for name in CHANGED_SKILLS:
            with self.subTest(skill=name):
                self.assertTrue(
                    os.path.isfile(_skill_path(name)),
                    f"skills/{name}.md must exist",
                )


class TestHeadingTierSeparator(unittest.TestCase):
    """All four headings must use ', TIER:' (comma) not '— TIER:' (em-dash)."""

    def test_intent_dispatcher_heading_comma(self):
        content = _read("intent-dispatcher")
        self.assertIn(
            "(Intent Dispatcher), TIER:",
            content,
            "intent-dispatcher.md heading must use ', TIER:' separator",
        )

    def test_mission_control_heading_comma(self):
        content = _read("mission-control")
        self.assertIn(
            "(Mission Control), TIER:",
            content,
            "mission-control.md heading must use ', TIER:' separator",
        )

    def test_role_tribunal_heading_comma(self):
        content = _read("role-tribunal")
        self.assertIn(
            "(Role Tribunal), TIER:",
            content,
            "role-tribunal.md heading must use ', TIER:' separator",
        )

    def test_topology_orchestrator_heading_comma(self):
        content = _read("topology-orchestrator")
        self.assertIn(
            "(Topology Orchestrator), TIER:",
            content,
            "topology-orchestrator.md heading must use ', TIER:' separator",
        )

    def test_no_em_dash_before_tier_in_any_changed_skill(self):
        """None of the four headings may use the old '— TIER:' pattern."""
        for name in CHANGED_SKILLS:
            content = _read(name)
            with self.subTest(skill=name):
                # Match exactly the old pattern: ) — TIER:
                self.assertNotIn(
                    ") — TIER:",
                    content,
                    f"skills/{name}.md must not use the old '— TIER:' heading separator",
                )


class TestNoStubsRemain(unittest.TestCase):
    """No TODO stub placeholders may survive in any of the four files."""

    def test_no_todo_stubs_in_intent_dispatcher(self):
        content = _read("intent-dispatcher")
        for stub in TODO_STUBS:
            with self.subTest(stub=stub):
                self.assertNotIn(stub, content, f"intent-dispatcher.md must not contain stub: {stub!r}")

    def test_no_todo_stubs_in_mission_control(self):
        content = _read("mission-control")
        for stub in TODO_STUBS:
            with self.subTest(stub=stub):
                self.assertNotIn(stub, content, f"mission-control.md must not contain stub: {stub!r}")

    def test_no_todo_stubs_in_role_tribunal(self):
        content = _read("role-tribunal")
        for stub in TODO_STUBS:
            with self.subTest(stub=stub):
                self.assertNotIn(stub, content, f"role-tribunal.md must not contain stub: {stub!r}")

    def test_no_todo_stubs_in_topology_orchestrator(self):
        content = _read("topology-orchestrator")
        for stub in TODO_STUBS:
            with self.subTest(stub=stub):
                self.assertNotIn(stub, content, f"topology-orchestrator.md must not contain stub: {stub!r}")


class TestRequiredSectionsPresent(unittest.TestCase):
    """All four required sections must be present in each skill file."""

    def _assert_sections(self, name: str):
        content = _read(name)
        for section in REQUIRED_SECTIONS:
            with self.subTest(skill=name, section=section):
                self.assertIn(
                    section,
                    content,
                    f"skills/{name}.md must contain '{section}'",
                )

    def test_intent_dispatcher_has_all_sections(self):
        self._assert_sections("intent-dispatcher")

    def test_mission_control_has_all_sections(self):
        self._assert_sections("mission-control")

    def test_role_tribunal_has_all_sections(self):
        self._assert_sections("role-tribunal")

    def test_topology_orchestrator_has_all_sections(self):
        self._assert_sections("topology-orchestrator")


class TestFailureModesHaveTable(unittest.TestCase):
    """The Failure Modes section must contain a markdown table (pipe characters)."""

    def _get_section(self, content: str, heading: str) -> str:
        """Return the text from the given heading to the next ## heading."""
        idx = content.find(heading)
        if idx == -1:
            return ""
        rest = content[idx + len(heading):]
        next_h2 = re.search(r"\n## ", rest)
        return rest[: next_h2.start()] if next_h2 else rest

    def _assert_failure_table(self, name: str):
        content = _read(name)
        section = self._get_section(content, "## Failure Modes")
        self.assertGreater(len(section), 10, f"Failure Modes section in {name}.md is too short")
        self.assertIn(
            "|",
            section,
            f"Failure Modes section in skills/{name}.md must contain a markdown table",
        )

    def test_intent_dispatcher_failure_table(self):
        self._assert_failure_table("intent-dispatcher")

    def test_mission_control_failure_table(self):
        self._assert_failure_table("mission-control")

    def test_role_tribunal_failure_table(self):
        self._assert_failure_table("role-tribunal")

    def test_topology_orchestrator_failure_table(self):
        self._assert_failure_table("topology-orchestrator")


class TestOperationalFlowHasSteps(unittest.TestCase):
    """The Operational Flow section must contain numbered steps."""

    def _get_section(self, content: str, heading: str) -> str:
        idx = content.find(heading)
        if idx == -1:
            return ""
        rest = content[idx + len(heading):]
        next_h2 = re.search(r"\n## ", rest)
        return rest[: next_h2.start()] if next_h2 else rest

    def _assert_numbered_steps(self, name: str):
        content = _read(name)
        section = self._get_section(content, "## Operational Flow")
        # At minimum step "1." must appear
        self.assertRegex(
            section,
            r"1\.",
            f"Operational Flow section in skills/{name}.md must contain numbered steps",
        )

    def test_intent_dispatcher_flow_has_steps(self):
        self._assert_numbered_steps("intent-dispatcher")

    def test_mission_control_flow_has_steps(self):
        self._assert_numbered_steps("mission-control")

    def test_role_tribunal_flow_has_steps(self):
        self._assert_numbered_steps("role-tribunal")

    def test_topology_orchestrator_flow_has_steps(self):
        self._assert_numbered_steps("topology-orchestrator")


class TestSubstantiveContentMinLength(unittest.TestCase):
    """Each required section must have enough text to be non-trivial (> 100 chars)."""

    def _section_length(self, content: str, heading: str) -> int:
        idx = content.find(heading)
        if idx == -1:
            return 0
        rest = content[idx + len(heading):]
        next_h2 = re.search(r"\n## ", rest)
        section = rest[: next_h2.start()] if next_h2 else rest
        return len(section.strip())

    def _assert_min_length(self, name: str, section: str, min_len: int = 100):
        content = _read(name)
        length = self._section_length(content, section)
        self.assertGreater(
            length,
            min_len,
            f"skills/{name}.md '{section}' section must have > {min_len} chars of content "
            f"(got {length}); it appears to be a stub",
        )

    def test_intent_dispatcher_purpose_substantive(self):
        self._assert_min_length("intent-dispatcher", "## Purpose")

    def test_mission_control_purpose_substantive(self):
        self._assert_min_length("mission-control", "## Purpose")

    def test_role_tribunal_purpose_substantive(self):
        self._assert_min_length("role-tribunal", "## Purpose")

    def test_topology_orchestrator_purpose_substantive(self):
        self._assert_min_length("topology-orchestrator", "## Purpose")

    def test_intent_dispatcher_flow_substantive(self):
        self._assert_min_length("intent-dispatcher", "## Operational Flow", 200)

    def test_mission_control_flow_substantive(self):
        self._assert_min_length("mission-control", "## Operational Flow", 200)

    def test_role_tribunal_flow_substantive(self):
        self._assert_min_length("role-tribunal", "## Operational Flow", 200)

    def test_topology_orchestrator_flow_substantive(self):
        self._assert_min_length("topology-orchestrator", "## Operational Flow", 200)


# ---------------------------------------------------------------------------
# Skill-specific content assertions
# ---------------------------------------------------------------------------

class TestIntentDispatcherContent(unittest.TestCase):
    """Key domain concepts that must appear in intent-dispatcher.md."""

    def test_sixty_percent_threshold_mentioned(self):
        content = _read("intent-dispatcher")
        self.assertIn("60%", content, "The 60% match threshold must be documented")

    def test_pipeline_yaml_mentioned(self):
        content = _read("intent-dispatcher")
        self.assertIn("pipeline.yaml", content, "pipeline.yaml must be referenced")

    def test_version_guard_mentioned(self):
        content = _read("intent-dispatcher")
        self.assertIn("version-guard", content, "version-guard dependency must be mentioned")

    def test_pipeline_store_mentioned(self):
        content = _read("intent-dispatcher")
        self.assertIn("pipeline-store", content, "pipeline-store must be referenced")

    def test_trust_chain_mentioned(self):
        content = _read("intent-dispatcher")
        self.assertIn("trust-chain", content, "trust-chain must be referenced in constitutional alignment")

    def test_no_pipeline_found_failure_mode(self):
        content = _read("intent-dispatcher")
        self.assertIn(
            "no_pipeline_found",
            content,
            "The no_pipeline_found failure mode must be documented",
        )

    def test_learning_loop_history_file_referenced(self):
        content = _read("intent-dispatcher")
        self.assertIn(
            "dispatcher-history.jsonl",
            content,
            "The learning-loop history file must be referenced",
        )

    def test_abstract_workflow_concept_present(self):
        content = _read("intent-dispatcher")
        self.assertIn("abstract", content.lower(), "Abstract workflow concept must be present")

    def test_ranked_list_concept_present(self):
        content = _read("intent-dispatcher")
        self.assertIn("ranked", content.lower(), "Ranked pipeline list concept must be present")


class TestMissionControlContent(unittest.TestCase):
    """Key domain concepts that must appear in mission-control.md."""

    def test_sovereign_constitution_referenced(self):
        content = _read("mission-control")
        self.assertIn("sovereign-constitution", content)

    def test_seven_stage_cycle_mentioned(self):
        content = _read("mission-control")
        # The content describes seven stages (Read/Evaluate/Plan/Verify/Prioritize/Fix/Evolve)
        self.assertIn("seven-stage", content, "The seven-stage IQRA cycle must be mentioned")

    def test_worker_chain_documented(self):
        content = _read("mission-control")
        self.assertIn("Planner", content)
        self.assertIn("Validator", content)
        self.assertIn("Reporter", content)

    def test_topology_orchestrator_referenced(self):
        content = _read("mission-control")
        self.assertIn("topology-orchestrator", content)

    def test_memory_bridge_referenced(self):
        content = _read("mission-control")
        self.assertIn("memory-bridge", content)

    def test_shura_council_referenced(self):
        content = _read("mission-control")
        self.assertIn("shura-council", content)

    def test_rule_of_nine_mentioned(self):
        content = _read("mission-control")
        self.assertIn("nine", content.lower(), "The rule-of-9 from covenant-guard must be mentioned")

    def test_trust_chain_audit_mentioned(self):
        content = _read("mission-control")
        self.assertIn("trust-chain", content)

    def test_mission_envelope_concept_present(self):
        content = _read("mission-control")
        self.assertIn("Mission Envelope", content)

    def test_self_approval_prohibition_documented(self):
        """No worker may approve its own output — this must be documented."""
        content = _read("mission-control")
        self.assertTrue(
            "self-approv" in content.lower() or "no worker may approve" in content.lower(),
            "The self-approval prohibition must be documented in mission-control.md",
        )


class TestRoleTribunalContent(unittest.TestCase):
    """Key domain concepts that must appear in role-tribunal.md."""

    def test_permit_deny_escalate_verdicts_documented(self):
        content = _read("role-tribunal")
        self.assertIn("permit", content)
        self.assertIn("deny", content)
        self.assertIn("escalate", content)

    def test_hourglass_gate_referenced(self):
        content = _read("role-tribunal")
        self.assertIn("Hourglass Gate", content, "The Hourglass Gate concept must be documented")

    def test_covenant_guard_referenced(self):
        content = _read("role-tribunal")
        self.assertIn("covenant-guard", content)

    def test_sixty_minute_ceiling_documented(self):
        content = _read("role-tribunal")
        self.assertIn("60-minute", content, "The 60-minute work ceiling must be documented")

    def test_five_hundred_decision_trigger_documented(self):
        content = _read("role-tribunal")
        self.assertIn("500", content, "The 500-decision audit trigger must be documented")

    def test_nine_error_escalation_documented(self):
        content = _read("role-tribunal")
        self.assertIn("9", content, "The 9-error escalation must be documented")

    def test_requires_human_approval_flow_documented(self):
        content = _read("role-tribunal")
        self.assertIn("requiresHumanApproval", content)

    def test_quota_rate_limiting_documented(self):
        content = _read("role-tribunal")
        self.assertIn("quota", content.lower())
        self.assertIn("rate", content.lower())

    def test_unsigned_agent_rejection_documented(self):
        content = _read("role-tribunal")
        self.assertIn("unsigned", content.lower(), "Rejection of unsigned agents must be documented")

    def test_time_window_check_documented(self):
        content = _read("role-tribunal")
        self.assertIn("time window", content.lower(), "Time-window check must be in operational flow")

    def test_references_section_present(self):
        content = _read("role-tribunal")
        self.assertIn("## References", content)

    def test_oso_rbac_reference_present(self):
        content = _read("role-tribunal")
        self.assertIn("RBAC", content, "RBAC industry reference must be documented")


class TestTopologyOrchestratorContent(unittest.TestCase):
    """Key domain concepts that must appear in topology-orchestrator.md."""

    def test_five_execution_modes_documented(self):
        content = _read("topology-orchestrator")
        for mode in ("sequential", "parallel", "conditional", "hierarchical", "swarm"):
            with self.subTest(mode=mode):
                self.assertIn(mode, content, f"Execution mode '{mode}' must be documented")

    def test_resonance_fingerprint_mentioned(self):
        content = _read("topology-orchestrator")
        self.assertIn("resonance fingerprint", content)

    def test_skills_json_referenced(self):
        content = _read("topology-orchestrator")
        self.assertIn("skills.json", content)

    def test_sovereign_constitution_referenced(self):
        content = _read("topology-orchestrator")
        self.assertIn("sovereign-constitution", content)

    def test_role_tribunal_referenced(self):
        content = _read("topology-orchestrator")
        self.assertIn("role-tribunal", content)

    def test_covenant_guard_referenced(self):
        content = _read("topology-orchestrator")
        self.assertIn("covenant-guard", content)

    def test_cycle_detection_documented(self):
        content = _read("topology-orchestrator")
        self.assertIn("cycle", content.lower(), "Cycle detection must be documented in operational flow")

    def test_fallback_strategies_documented(self):
        content = _read("topology-orchestrator")
        for strategy in ("halt", "retry", "skip", "divert"):
            with self.subTest(strategy=strategy):
                self.assertIn(strategy, content, f"Fallback strategy '{strategy}' must be documented")

    def test_constitutional_block_failure_mode_documented(self):
        content = _read("topology-orchestrator")
        self.assertIn("constitutional_block", content)

    def test_arabic_resonance_line_uses_colon_not_em_dash(self):
        """
        The Arabic resonance sentence was changed in this PR:
          old: تُسجَّل "بصمة رنين" — تردد النجاح بين المهارات.
          new: تُسجَّل "بصمة رنين": تردد النجاح بين المهارات.
        """
        content = _read("topology-orchestrator")
        self.assertIn(
            '"بصمة رنين":',
            content,
            "The Arabic resonance sentence must use ':' (colon) not '—' (em-dash)",
        )
        # The old em-dash form must be absent
        self.assertNotIn(
            '"بصمة رنين" —',
            content,
            "The old em-dash form of the Arabic resonance sentence must be removed",
        )

    def test_trust_chain_checkpointing_referenced(self):
        content = _read("topology-orchestrator")
        self.assertIn("trust-chain", content)

    def test_references_section_present(self):
        content = _read("topology-orchestrator")
        self.assertIn("## References", content)

    def test_langgraph_reference_present(self):
        content = _read("topology-orchestrator")
        self.assertIn("LangGraph", content)


if __name__ == "__main__":
    unittest.main()
