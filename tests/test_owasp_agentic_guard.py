"""
Tests for skills/owasp-agentic-guard.md added in this PR.

Covers:
- File existence and encoding
- All four required English section headers
- Arabic section alias for Purpose (الجوهر)
- TIER declaration in the title
- All ten ASI category identifiers (ASI01-ASI10)
- Canonical OWASP category names
- Referenced mitigation skills in the category map
- Operational flow structure (numbered steps, verdict outcomes)
- Failure modes table with expected failure scenarios
- No stub/placeholder content
- References section with OWASP sources
"""

from __future__ import annotations

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_PATH = os.path.join(REPO_ROOT, "skills", "owasp-agentic-guard.md")


def _read_skill() -> str:
    with open(SKILL_PATH, encoding="utf-8") as fh:
        return fh.read()


class TestOwaspAgenticGuardFileBasics(unittest.TestCase):
    """File existence and encoding sanity checks."""

    def test_file_exists(self):
        self.assertTrue(
            os.path.isfile(SKILL_PATH),
            "skills/owasp-agentic-guard.md must exist in the repository",
        )

    def test_file_is_not_empty(self):
        self.assertGreater(
            os.path.getsize(SKILL_PATH),
            0,
            "owasp-agentic-guard.md must not be empty",
        )

    def test_file_is_utf8_encoded(self):
        content = _read_skill()
        self.assertIsInstance(content, str)

    def test_file_is_markdown(self):
        self.assertTrue(SKILL_PATH.endswith(".md"), "skill file must have a .md extension")


class TestOwaspAgenticGuardRequiredSections(unittest.TestCase):
    """The four required English section headers must be present."""

    def setUp(self):
        self.content = _read_skill()

    def test_purpose_section_present(self):
        self.assertIn(
            "## Purpose",
            self.content,
            "owasp-agentic-guard.md must contain '## Purpose' section",
        )

    def test_constitutional_alignment_section_present(self):
        self.assertIn(
            "## Constitutional Alignment",
            self.content,
            "owasp-agentic-guard.md must contain '## Constitutional Alignment' section",
        )

    def test_operational_flow_section_present(self):
        self.assertIn(
            "## Operational Flow",
            self.content,
            "owasp-agentic-guard.md must contain '## Operational Flow' section",
        )

    def test_failure_modes_section_present(self):
        self.assertIn(
            "## Failure Modes",
            self.content,
            "owasp-agentic-guard.md must contain '## Failure Modes' section",
        )


class TestOwaspAgenticGuardArabicSections(unittest.TestCase):
    """Arabic section aliases accepted by the skill quality validator."""

    def setUp(self):
        self.content = _read_skill()

    def test_arabic_purpose_alias_present(self):
        # الجوهر is an accepted alias for the Purpose section
        self.assertIn(
            "الجوهر",
            self.content,
            "Arabic Purpose alias '## الجوهر' must be present",
        )

    def test_arabic_section_has_heading_marker(self):
        self.assertIn(
            "## الجوهر",
            self.content,
            "Arabic Purpose alias must appear as a level-2 heading '## الجوهر'",
        )


class TestOwaspAgenticGuardTitle(unittest.TestCase):
    """Title-line conventions."""

    def setUp(self):
        self.content = _read_skill()
        self.first_line = self.content.splitlines()[0]

    def test_title_is_level_one_heading(self):
        self.assertTrue(
            self.first_line.startswith("# "),
            "The first line must be a level-1 Markdown heading",
        )

    def test_title_mentions_owasp(self):
        self.assertIn(
            "OWASP",
            self.first_line,
            "The title must mention 'OWASP'",
        )

    def test_tier_declared_in_title(self):
        self.assertIn(
            "ADVANCED_INFRASTRUCTURE",
            self.first_line,
            "The title must declare TIER: ADVANCED_INFRASTRUCTURE",
        )

    def test_title_mentions_agentic_guard(self):
        self.assertIn(
            "Agentic Guard",
            self.first_line,
            "The title must include 'Agentic Guard'",
        )


class TestOwaspAgenticGuardASICategories(unittest.TestCase):
    """All ten ASI category identifiers must be present and correctly mapped."""

    def setUp(self):
        self.content = _read_skill()

    def _assert_asi(self, asi_id: str, expected_name_fragment: str = ""):
        self.assertIn(
            asi_id,
            self.content,
            f"{asi_id} must be referenced in the skill file",
        )
        if expected_name_fragment:
            self.assertIn(
                expected_name_fragment,
                self.content,
                f"Expected to find '{expected_name_fragment}' near {asi_id}",
            )

    def test_asi01_agent_goal_hijack(self):
        self._assert_asi("ASI01", "Agent Goal Hijack")

    def test_asi02_tool_misuse(self):
        self._assert_asi("ASI02", "Tool Misuse")

    def test_asi03_identity_privilege_abuse(self):
        self._assert_asi("ASI03", "Identity")

    def test_asi04_supply_chain(self):
        self._assert_asi("ASI04", "Supply Chain")

    def test_asi05_unexpected_code_execution(self):
        self._assert_asi("ASI05", "Code Execution")

    def test_asi06_memory_poisoning(self):
        self._assert_asi("ASI06", "Memory")

    def test_asi07_inter_agent_communication(self):
        self._assert_asi("ASI07", "Inter-Agent Communication")

    def test_asi08_cascading_failures(self):
        self._assert_asi("ASI08", "Cascading Failures")

    def test_asi09_human_agent_trust(self):
        self._assert_asi("ASI09", "Human-Agent Trust")

    def test_asi10_rogue_agents(self):
        self._assert_asi("ASI10", "Rogue Agents")

    def test_all_ten_asi_ids_present(self):
        for i in range(1, 11):
            asi_id = f"ASI{i:02d}"
            with self.subTest(asi_id=asi_id):
                self.assertIn(asi_id, self.content, f"{asi_id} must be referenced")

    def test_asi_ids_are_sequential(self):
        """Verify ASI01 through ASI10 appear (in any order) — none skipped."""
        missing = [
            f"ASI{i:02d}" for i in range(1, 11) if f"ASI{i:02d}" not in self.content
        ]
        self.assertEqual(
            [],
            missing,
            f"These ASI category IDs are missing from the skill: {missing}",
        )


class TestOwaspAgenticGuardMitigationSkills(unittest.TestCase):
    """Referenced mitigation/enforcer skills must be named in the category map."""

    def setUp(self):
        self.content = _read_skill()

    def test_sovereign_constitution_referenced(self):
        self.assertIn("sovereign-constitution", self.content)

    def test_prompt_weaver_referenced(self):
        self.assertIn("prompt-weaver", self.content)

    def test_role_tribunal_referenced(self):
        self.assertIn("role-tribunal", self.content)

    def test_circuit_breaker_referenced(self):
        self.assertIn("circuit-breaker", self.content)

    def test_covenant_guard_referenced(self):
        self.assertIn("covenant-guard", self.content)

    def test_version_guard_referenced(self):
        self.assertIn("version-guard", self.content)

    def test_trust_chain_referenced(self):
        self.assertIn("trust-chain", self.content)

    def test_purity_filter_referenced(self):
        self.assertIn("purity-filter", self.content)

    def test_memory_bridge_referenced(self):
        self.assertIn("memory-bridge", self.content)

    def test_shura_council_referenced(self):
        self.assertIn("shura-council", self.content)

    def test_reward_engine_referenced(self):
        self.assertIn("reward-engine", self.content)

    def test_voice_identity_referenced(self):
        self.assertIn("voice-identity", self.content)


class TestOwaspAgenticGuardOperationalFlow(unittest.TestCase):
    """Operational Flow section must describe all six numbered steps."""

    def setUp(self):
        self.content = _read_skill()
        # Extract just the Operational Flow section body
        match = re.search(
            r"## Operational Flow\s*(.*?)(?=\n## |\Z)", self.content, re.DOTALL
        )
        self.flow_body = match.group(1) if match else ""

    def test_step_1_receive(self):
        self.assertIn("Receive", self.flow_body, "Step 1 'Receive' must be in Operational Flow")

    def test_step_2_select_probes(self):
        self.assertIn("Select probes", self.flow_body, "Step 2 'Select probes' must be in Operational Flow")

    def test_step_3_run_probes(self):
        self.assertIn("Run probes", self.flow_body, "Step 3 'Run probes' must be in Operational Flow")

    def test_step_4_aggregate(self):
        self.assertIn("Aggregate", self.flow_body, "Step 4 'Aggregate' must be in Operational Flow")

    def test_step_5_hand_off(self):
        self.assertIn("Hand off", self.flow_body, "Step 5 'Hand off' must be in Operational Flow")

    def test_step_6_record(self):
        self.assertIn("Record", self.flow_body, "Step 6 'Record' must be in Operational Flow")

    def test_action_envelope_fields_described(self):
        self.assertIn("agent_id", self.flow_body)
        self.assertIn("action_type", self.flow_body)
        self.assertIn("payload", self.flow_body)

    def test_verdict_outcomes_described(self):
        """block, escalate, and allow verdicts must all be mentioned."""
        self.assertIn("block", self.flow_body)
        self.assertIn("escalate", self.flow_body)
        self.assertIn("allow", self.flow_body)

    def test_action_types_described(self):
        self.assertIn("tool_call", self.flow_body)
        self.assertIn("memory_write", self.flow_body)
        self.assertIn("code_execute", self.flow_body)

    def test_severity_levels_described(self):
        self.assertIn("critical", self.flow_body)
        self.assertIn("high", self.flow_body)
        self.assertIn("info", self.flow_body)


class TestOwaspAgenticGuardFailureModes(unittest.TestCase):
    """Failure Modes section must document expected failure scenarios."""

    def setUp(self):
        self.content = _read_skill()
        match = re.search(
            r"## Failure Modes\s*(.*?)(?=\n## |\Z)", self.content, re.DOTALL
        )
        self.failure_body = match.group(1) if match else ""

    def test_failure_modes_table_present(self):
        self.assertIn("|", self.failure_body, "Failure Modes must include a Markdown table")

    def test_failure_modes_table_has_mode_column(self):
        self.assertIn("Mode", self.failure_body)

    def test_failure_modes_table_has_detection_column(self):
        self.assertIn("Detection", self.failure_body)

    def test_failure_modes_table_has_recovery_column(self):
        self.assertIn("Recovery", self.failure_body)

    def test_probe_timeout_failure_mode_present(self):
        self.assertIn(
            "latency",
            self.failure_body.lower(),
            "Probe latency failure mode must be documented",
        )

    def test_fail_closed_on_unavailable_mitigation_skill(self):
        self.assertIn(
            "Fail closed",
            self.failure_body,
            "Skill must fail closed when mitigation skill is unavailable",
        )

    def test_false_positive_failure_mode_present(self):
        self.assertIn(
            "False positive",
            self.failure_body,
            "False positive storm failure mode must be documented",
        )

    def test_novel_attack_failure_mode_present(self):
        self.assertIn(
            "Novel attack",
            self.failure_body,
            "Novel attack (outside ten categories) failure mode must be documented",
        )

    def test_probe_disagreement_failure_mode_present(self):
        self.assertIn(
            "disagrees",
            self.failure_body.lower(),
            "Probe replica disagreement failure mode must be documented",
        )


class TestOwaspAgenticGuardNoStubs(unittest.TestCase):
    """The skill must not contain stub placeholder content."""

    def setUp(self):
        self.content = _read_skill()

    def test_no_todo_define_placeholder(self):
        self.assertNotIn(
            "TODO: Define",
            self.content,
            "Skill must not contain 'TODO: Define' placeholder text",
        )

    def test_no_tbd_placeholder(self):
        # Match standalone TBD (not part of a larger word)
        has_tbd = bool(re.search(r"\bTBD\b", self.content))
        self.assertFalse(has_tbd, "Skill must not contain 'TBD' placeholder text")

    def test_no_fill_in_placeholder(self):
        self.assertNotIn(
            "<fill in>",
            self.content,
            "Skill must not contain '<fill in>' placeholder text",
        )

    def test_purpose_section_body_is_substantive(self):
        """Purpose body must have more than one non-blank line."""
        match = re.search(
            r"## Purpose\s*(.*?)(?=\n## |\Z)", self.content, re.DOTALL
        )
        self.assertIsNotNone(match)
        body_lines = [
            line for line in match.group(1).splitlines() if line.strip()
        ]
        self.assertGreater(
            len(body_lines),
            1,
            "Purpose section must contain substantive content (more than one line)",
        )

    def test_constitutional_alignment_body_is_substantive(self):
        match = re.search(
            r"## Constitutional Alignment\s*(.*?)(?=\n## |\Z)", self.content, re.DOTALL
        )
        self.assertIsNotNone(match)
        body_lines = [
            line for line in match.group(1).splitlines() if line.strip()
        ]
        self.assertGreater(
            len(body_lines),
            1,
            "Constitutional Alignment section must contain substantive content",
        )


class TestOwaspAgenticGuardReferences(unittest.TestCase):
    """References section must cite OWASP sources."""

    def setUp(self):
        self.content = _read_skill()

    def test_references_section_present(self):
        self.assertIn(
            "## References",
            self.content,
            "owasp-agentic-guard.md must contain a '## References' section",
        )

    def test_owasp_2026_framework_cited(self):
        self.assertIn(
            "2026",
            self.content,
            "References must mention the 2026 OWASP framework",
        )

    def test_owasp_genai_project_cited(self):
        self.assertIn(
            "OWASP GenAI Security Project",
            self.content,
            "References must cite the OWASP GenAI Security Project",
        )

    def test_real_incident_cited(self):
        """At least one real-world incident must be cited to ground the taxonomy."""
        real_incidents = ["EchoLeak", "Amazon Q", "AutoGPT", "Gemini Memory"]
        cited = any(incident in self.content for incident in real_incidents)
        self.assertTrue(
            cited,
            f"At least one real incident must be cited (checked: {real_incidents})",
        )

    def test_owasp_url_present(self):
        self.assertIn(
            "genai.owasp.org",
            self.content,
            "References must include a link to genai.owasp.org",
        )


if __name__ == "__main__":
    unittest.main()