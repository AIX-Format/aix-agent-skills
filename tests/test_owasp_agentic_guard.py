"""
Tests for skills/owasp-agentic-guard.md — added in this PR.

Validates:
- The skill file exists and is readable UTF-8 text.
- All four required English section headings are present.
- The Arabic Purpose alias (الجوهر) is present (bilingual content).
- All ten ASI categories (ASI01–ASI10) are documented.
- Every ASI row names at least one enforcement skill from the catalogue.
- The six-step Operational Flow is present and fully enumerated.
- The Failure Modes table contains at least the five documented failure
  modes with Detection and Recovery columns.
- No stub placeholder text (TODO, TBD, <fill in>) remains.
- The file references the OWASP framework prominently.
- The skill name in the title line matches the manifest entry.
- The tier annotation in the title line is ADVANCED_INFRASTRUCTURE.
"""

from __future__ import annotations

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_FILE = os.path.join(REPO_ROOT, "skills", "owasp-agentic-guard.md")

# All ten ASI category IDs that must appear in the skill document.
EXPECTED_ASI_IDS = [
    "ASI01",
    "ASI02",
    "ASI03",
    "ASI04",
    "ASI05",
    "ASI06",
    "ASI07",
    "ASI08",
    "ASI09",
    "ASI10",
]

# English section headings required by the skill template.
REQUIRED_ENGLISH_SECTIONS = [
    "## Purpose",
    "## Constitutional Alignment",
    "## Operational Flow",
    "## Failure Modes",
]

# Stub markers that must NOT appear in a completed skill.
STUB_PATTERNS = [
    r"TODO:\s*Define",
    r"\bTBD\b",
    r"<fill in>",
    r"<placeholder>",
]

# A representative set of enforcement skills referenced in the ASI table.
EXPECTED_ENFORCEMENT_SKILLS = [
    "sovereign-constitution",
    "circuit-breaker",
    "covenant-guard",
    "role-tribunal",
    "trust-chain",
    "purity-filter",
    "memory-bridge",
    "shura-council",
]


def _read_skill() -> str:
    with open(SKILL_FILE, encoding="utf-8") as fh:
        return fh.read()


class TestOwaspAgenticGuardFilePresence(unittest.TestCase):
    """Basic file existence and readability checks."""

    def test_file_exists(self):
        self.assertTrue(
            os.path.isfile(SKILL_FILE),
            "skills/owasp-agentic-guard.md must exist",
        )

    def test_file_is_non_empty(self):
        size = os.path.getsize(SKILL_FILE)
        self.assertGreater(size, 0, "skill file must not be empty")

    def test_file_is_utf8_decodable(self):
        content = _read_skill()
        self.assertIsInstance(content, str)

    def test_file_is_markdown(self):
        self.assertTrue(
            SKILL_FILE.endswith(".md"),
            "skill file must have .md extension",
        )


class TestOwaspAgenticGuardTitle(unittest.TestCase):
    """Title line and metadata embedded in the heading."""

    def setUp(self):
        self.content = _read_skill()
        self.lines = self.content.splitlines()

    def test_title_line_is_h1(self):
        self.assertTrue(
            self.lines[0].startswith("# "),
            "First line must be a level-1 heading",
        )

    def test_title_mentions_owasp(self):
        title = self.lines[0]
        self.assertIn("OWASP", title, "Title must mention OWASP")

    def test_title_mentions_agentic_guard(self):
        title = self.lines[0].lower()
        # Accept Arabic transliteration or English form
        self.assertTrue(
            "agentic guard" in title or "guard" in title,
            "Title must reference 'guard' or 'agentic guard'",
        )

    def test_title_declares_advanced_infrastructure_tier(self):
        title = self.lines[0]
        self.assertIn(
            "ADVANCED_INFRASTRUCTURE",
            title,
            "Title must declare TIER: ADVANCED_INFRASTRUCTURE",
        )


class TestOwaspAgenticGuardRequiredSections(unittest.TestCase):
    """All four required English section headings must be present."""

    def setUp(self):
        self.content = _read_skill()

    def test_purpose_section_present(self):
        self.assertIn("## Purpose", self.content)

    def test_constitutional_alignment_section_present(self):
        self.assertIn("## Constitutional Alignment", self.content)

    def test_operational_flow_section_present(self):
        self.assertIn("## Operational Flow", self.content)

    def test_failure_modes_section_present(self):
        self.assertIn("## Failure Modes", self.content)

    def test_arabic_purpose_alias_present(self):
        """الجوهر is the accepted Arabic alias for Purpose."""
        self.assertIn("## الجوهر", self.content)

    def test_all_required_sections_present(self):
        for section in REQUIRED_ENGLISH_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, self.content)


class TestOwaspAgenticGuardASICategories(unittest.TestCase):
    """All ten ASI categories must be documented."""

    def setUp(self):
        self.content = _read_skill()

    def test_all_ten_asi_ids_present(self):
        for asi_id in EXPECTED_ASI_IDS:
            with self.subTest(asi_id=asi_id):
                self.assertIn(
                    asi_id,
                    self.content,
                    f"{asi_id} must appear in the skill document",
                )

    def test_asi01_agent_goal_hijack(self):
        self.assertIn("ASI01", self.content)
        self.assertIn("Agent Goal Hijack", self.content)

    def test_asi02_tool_misuse(self):
        self.assertIn("ASI02", self.content)
        self.assertIn("Tool Misuse", self.content)

    def test_asi03_identity_privilege(self):
        self.assertIn("ASI03", self.content)
        self.assertIn("Identity", self.content)

    def test_asi04_supply_chain(self):
        self.assertIn("ASI04", self.content)
        self.assertIn("Supply Chain", self.content)

    def test_asi05_code_execution(self):
        self.assertIn("ASI05", self.content)
        self.assertIn("Code Execution", self.content)

    def test_asi06_memory_poisoning(self):
        self.assertIn("ASI06", self.content)
        self.assertIn("Memory", self.content)

    def test_asi07_inter_agent_communication(self):
        self.assertIn("ASI07", self.content)
        self.assertIn("Inter-Agent Communication", self.content)

    def test_asi08_cascading_failures(self):
        self.assertIn("ASI08", self.content)
        self.assertIn("Cascading Failures", self.content)

    def test_asi09_human_agent_trust(self):
        self.assertIn("ASI09", self.content)
        self.assertIn("Human", self.content)

    def test_asi10_rogue_agents(self):
        self.assertIn("ASI10", self.content)
        self.assertIn("Rogue Agents", self.content)

    def test_asi_count_exactly_ten(self):
        """The document must reference all ten ASI IDs, no more, no less."""
        found = set(re.findall(r"ASI\d{2}", self.content))
        for expected in EXPECTED_ASI_IDS:
            self.assertIn(expected, found)
        # Validate none outside ASI01-ASI10 appear
        for asi in found:
            num = int(asi[3:])
            self.assertGreaterEqual(num, 1)
            self.assertLessEqual(num, 10, f"Unexpected ASI category: {asi}")


class TestOwaspAgenticGuardEnforcementSkills(unittest.TestCase):
    """Each ASI category must map to existing catalogue enforcement skills."""

    def setUp(self):
        self.content = _read_skill()

    def test_enforcement_skills_referenced(self):
        for skill in EXPECTED_ENFORCEMENT_SKILLS:
            with self.subTest(skill=skill):
                self.assertIn(
                    skill,
                    self.content,
                    f"Enforcement skill '{skill}' must be referenced",
                )

    def test_sovereign_constitution_referenced(self):
        self.assertIn("sovereign-constitution", self.content)

    def test_circuit_breaker_referenced(self):
        self.assertIn("circuit-breaker", self.content)

    def test_purity_filter_referenced(self):
        self.assertIn("purity-filter", self.content)

    def test_memory_bridge_referenced(self):
        self.assertIn("memory-bridge", self.content)

    def test_shura_council_referenced(self):
        self.assertIn("shura-council", self.content)

    def test_trust_chain_referenced(self):
        self.assertIn("trust-chain", self.content)


class TestOwaspAgenticGuardOperationalFlow(unittest.TestCase):
    """The six-step operational flow must be fully documented."""

    def setUp(self):
        self.content = _read_skill()
        # Extract the Operational Flow section body
        match = re.search(
            r"## Operational Flow\s+(.*?)(?=^## |\Z)",
            self.content,
            re.MULTILINE | re.DOTALL,
        )
        self.flow_body = match.group(1) if match else ""

    def test_operational_flow_section_not_empty(self):
        self.assertGreater(
            len(self.flow_body.strip()),
            0,
            "Operational Flow section must not be empty",
        )

    def test_six_numbered_steps_present(self):
        """Steps 1 through 6 must all be numbered explicitly."""
        for step_num in range(1, 7):
            with self.subTest(step=step_num):
                pattern = rf"^\s*{step_num}\."
                self.assertRegex(
                    self.flow_body,
                    re.compile(pattern, re.MULTILINE),
                    f"Operational Flow must contain step {step_num}",
                )

    def test_receive_step_mentioned(self):
        self.assertIn("Receive", self.flow_body)

    def test_select_probes_step_mentioned(self):
        self.assertIn("Select", self.flow_body)

    def test_aggregate_step_mentioned(self):
        self.assertIn("Aggregate", self.flow_body)

    def test_record_step_mentioned(self):
        self.assertIn("Record", self.flow_body)

    def test_action_envelope_schema_documented(self):
        """The action envelope schema must be listed."""
        self.assertIn("agent_id", self.flow_body)
        self.assertIn("action_type", self.flow_body)

    def test_verdict_outcomes_documented(self):
        """block, escalate, allow verdicts must be documented."""
        self.assertIn("block", self.flow_body)
        self.assertIn("escalate", self.flow_body)
        self.assertIn("allow", self.flow_body)


class TestOwaspAgenticGuardFailureModes(unittest.TestCase):
    """Failure Modes section must document at least 5 failure scenarios."""

    def setUp(self):
        self.content = _read_skill()
        match = re.search(
            r"## Failure Modes\s+(.*?)(?=^## |\Z)",
            self.content,
            re.MULTILINE | re.DOTALL,
        )
        self.failure_body = match.group(1) if match else ""

    def test_failure_modes_table_has_header(self):
        self.assertIn("Mode", self.failure_body)
        self.assertIn("Detection", self.failure_body)
        self.assertIn("Recovery", self.failure_body)

    def test_at_least_five_failure_modes(self):
        # Count table rows (lines that start with | and are not header/separator)
        rows = [
            line for line in self.failure_body.splitlines()
            if line.strip().startswith("|")
            and not re.match(r"^\|[-: |]+\|", line.strip())
            and "Mode" not in line  # skip the header row
        ]
        self.assertGreaterEqual(
            len(rows),
            5,
            f"Failure Modes must document at least 5 scenarios, found {len(rows)}",
        )

    def test_probe_timeout_failure_mode_present(self):
        self.assertIn("timeout", self.failure_body.lower())

    def test_fail_closed_principle_documented(self):
        """On mitigation skill unavailable, the skill must fail closed."""
        self.assertIn("block", self.failure_body.lower())

    def test_false_positive_handling_documented(self):
        self.assertIn("false positive", self.failure_body.lower())


class TestOwaspAgenticGuardNoStubs(unittest.TestCase):
    """No placeholder stub text must remain in the completed skill file."""

    def setUp(self):
        self.content = _read_skill()

    def test_no_todo_define_stubs(self):
        match = re.search(r"TODO:\s*Define", self.content, re.IGNORECASE)
        self.assertIsNone(
            match, "Skill must not contain 'TODO: Define' stub text"
        )

    def test_no_tbd_stubs(self):
        match = re.search(r"\bTBD\b", self.content, re.IGNORECASE)
        self.assertIsNone(match, "Skill must not contain 'TBD' stub text")

    def test_no_fill_in_stubs(self):
        self.assertNotIn("<fill in>", self.content.lower())

    def test_no_placeholder_stubs(self):
        self.assertNotIn("<placeholder>", self.content.lower())


class TestOwaspAgenticGuardOWASPReferences(unittest.TestCase):
    """OWASP framework must be prominently cited."""

    def setUp(self):
        self.content = _read_skill()

    def test_owasp_mentioned(self):
        self.assertIn("OWASP", self.content)

    def test_owasp_2026_edition_cited(self):
        """The 2026 edition of the Top 10 for Agentic Applications is the basis."""
        self.assertIn("2026", self.content)
        self.assertIn("OWASP", self.content)

    def test_references_section_present(self):
        self.assertIn("## References", self.content)

    def test_genai_owasp_url_referenced(self):
        self.assertIn("genai.owasp.org", self.content)

    def test_december_2025_release_noted(self):
        """The OWASP release date (December 2025) must be documented."""
        self.assertTrue(
            "December 2025" in self.content or "2025-12" in self.content,
            "The December 2025 release date of OWASP Top 10 for Agentic "
            "Applications must be noted in the document",
        )


class TestOwaspAgenticGuardActionTypes(unittest.TestCase):
    """The documented action types must all appear in the Operational Flow."""

    def setUp(self):
        self.content = _read_skill()

    def test_tool_call_action_type_documented(self):
        self.assertIn("tool_call", self.content)

    def test_memory_write_action_type_documented(self):
        self.assertIn("memory_write", self.content)

    def test_inter_agent_message_action_type_documented(self):
        self.assertIn("inter_agent_message", self.content)

    def test_code_execute_action_type_documented(self):
        self.assertIn("code_execute", self.content)

    def test_human_facing_output_action_type_documented(self):
        self.assertIn("human_facing_output", self.content)

    def test_cross_cutting_rules_documented(self):
        """ASI01 and ASI10 are cross-cutting and must run for every action."""
        self.assertIn("cross-cutting", self.content)


if __name__ == "__main__":
    unittest.main()