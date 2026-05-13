"""
Tests for the three sovereignty-layer skill files updated in this PR.

PR context: covenant-guard.md, shura-council.md, and sovereign-constitution.md
had their four required sections (Purpose, Constitutional Alignment, Operational
Flow, Failure Modes) filled in with real content, replacing TODO stubs. This file
verifies that:

  - All four required sections exist in each skill file.
  - No stub patterns (TODO, TBD, <fill in>, <placeholder>) remain.
  - Each section has substantive, non-empty content.
  - Key domain-specific content is present (Ed25519, Byzantine fault tolerance,
    Constitutional AI references, etc.).
  - The skill file header format uses the new comma-separated TIER notation.
  - The files are parseable UTF-8 Markdown.
  - Cross-skill references between the three skills are intact.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")

COVENANT_GUARD_PATH = os.path.join(SKILLS_DIR, "covenant-guard.md")
SHURA_COUNCIL_PATH = os.path.join(SKILLS_DIR, "shura-council.md")
SOVEREIGN_CONSTITUTION_PATH = os.path.join(SKILLS_DIR, "sovereign-constitution.md")

# Required section headers that every skill MUST contain.
REQUIRED_SECTIONS = [
    "## Purpose",
    "## Constitutional Alignment",
    "## Operational Flow",
    "## Failure Modes",
]

# Patterns that indicate a section is still a stub.
STUB_PATTERNS = [
    re.compile(r"TODO:\s*Define\b", re.IGNORECASE),
    re.compile(r"^\s*TBD\s*$", re.MULTILINE),
    re.compile(r"<fill in>", re.IGNORECASE),
    re.compile(r"<placeholder>", re.IGNORECASE),
]

# The old header format used em-dash; the new format uses a comma.
OLD_TIER_PATTERN = re.compile(r"TIER:.*—")


def _read_skill(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _extract_section_body(content: str, header: str) -> str:
    """Return the text between `header` and the next ## heading (or end of file)."""
    escaped = re.escape(header)
    pattern = rf"{escaped}\s*\n(.*?)(?=\n## |\Z)"
    match = re.search(pattern, content, re.DOTALL)
    if match is None:
        return ""
    return match.group(1).strip()


class TestCovenantGuardFileIntegrity(unittest.TestCase):
    """Basic file-level checks for covenant-guard.md."""

    def setUp(self):
        self.path = COVENANT_GUARD_PATH
        self.content = _read_skill(self.path)

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.path), "covenant-guard.md must exist")

    def test_file_is_not_empty(self):
        self.assertGreater(len(self.content), 0, "covenant-guard.md must not be empty")

    def test_file_is_utf8(self):
        # If setUp succeeded, the file decoded as UTF-8 without errors.
        self.assertIsInstance(self.content, str)

    def test_header_contains_tier_sovereign(self):
        first_line = self.content.splitlines()[0]
        self.assertIn("TIER: SOVEREIGN", first_line)

    def test_header_uses_comma_not_em_dash(self):
        """The PR changed '— TIER:' to ', TIER:' in the heading."""
        first_line = self.content.splitlines()[0]
        self.assertNotRegex(
            first_line,
            OLD_TIER_PATTERN,
            "Header must use comma notation, not em-dash before TIER",
        )
        self.assertIn(",", first_line, "Comma must precede TIER in the header")


class TestCovenantGuardRequiredSections(unittest.TestCase):
    """Verify all four required sections are present in covenant-guard.md."""

    def setUp(self):
        self.content = _read_skill(COVENANT_GUARD_PATH)

    def test_has_purpose_section(self):
        self.assertIn("## Purpose", self.content)

    def test_has_constitutional_alignment_section(self):
        self.assertIn("## Constitutional Alignment", self.content)

    def test_has_operational_flow_section(self):
        self.assertIn("## Operational Flow", self.content)

    def test_has_failure_modes_section(self):
        self.assertIn("## Failure Modes", self.content)

    def test_all_required_sections_present(self):
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, self.content)


class TestCovenantGuardNoStubs(unittest.TestCase):
    """Verify no stub placeholders remain in covenant-guard.md."""

    def setUp(self):
        self.content = _read_skill(COVENANT_GUARD_PATH)

    def test_no_todo_define_in_purpose(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertNotRegex(body, STUB_PATTERNS[0])

    def test_no_todo_define_in_constitutional_alignment(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertNotRegex(body, STUB_PATTERNS[0])

    def test_no_todo_define_in_operational_flow(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertNotRegex(body, STUB_PATTERNS[0])

    def test_no_todo_define_in_failure_modes(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertNotRegex(body, STUB_PATTERNS[0])

    def test_no_stub_pattern_anywhere(self):
        for pat in STUB_PATTERNS:
            with self.subTest(pattern=pat.pattern):
                self.assertNotRegex(self.content, pat)


class TestCovenantGuardSectionContent(unittest.TestCase):
    """Spot-check key domain content within covenant-guard.md sections."""

    def setUp(self):
        self.content = _read_skill(COVENANT_GUARD_PATH)

    def test_purpose_mentions_ed25519(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertIn("Ed25519", body)

    def test_purpose_mentions_cryptographic_binding(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertTrue(
            "cryptographic" in body.lower() or "binding" in body.lower(),
            "Purpose should mention the cryptographic binding function",
        )

    def test_purpose_mentions_marketplace(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertIn("marketplace", body.lower())

    def test_purpose_is_substantive(self):
        body = _extract_section_body(self.content, "## Purpose")
        # Minimum meaningful length; a stub would be very short.
        self.assertGreater(len(body), 100)

    def test_constitutional_alignment_mentions_ed25519(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertIn("Ed25519", body)

    def test_constitutional_alignment_references_external_standards(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        # Should reference at least one of the known external standards.
        has_reference = any(
            term in body
            for term in ["IETF", "AIVS", "Agent Passport", ".agent"]
        )
        self.assertTrue(has_reference, "Constitutional Alignment should cite external agent standards")

    def test_constitutional_alignment_is_substantive(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertGreater(len(body), 100)

    def test_operational_flow_has_numbered_steps(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        # Expect numbered steps 1–5.
        for step_num in range(1, 6):
            with self.subTest(step=step_num):
                self.assertRegex(body, rf"{step_num}\.")

    def test_operational_flow_mentions_49_cycle(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("49", body)

    def test_operational_flow_mentions_trust_chain(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("trust-chain", body)

    def test_operational_flow_mentions_revocation(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertTrue(
            "revoc" in body.lower() or "revoke" in body.lower(),
            "Operational Flow should describe revocation",
        )

    def test_failure_modes_is_a_table(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        # Markdown table rows contain |
        self.assertIn("|", body)

    def test_failure_modes_covers_signature_mismatch(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "mismatch" in body.lower() or "signature" in body.lower(),
            "Failure Modes must address signature mismatch",
        )

    def test_failure_modes_covers_renewal_cycle(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "renewal" in body.lower() or "covenant_expired" in body.lower() or "cycle" in body.lower(),
            "Failure Modes must address renewal cycle expiry",
        )

    def test_failure_modes_covers_rule_of_9(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "rule-of-9" in body.lower() or "self-justification" in body.lower()
            or "9 consecutive" in body.lower(),
            "Failure Modes should cover the rule-of-9 loop",
        )

    def test_has_references_section(self):
        self.assertIn("## References", self.content)

    def test_references_mentions_rfc_8032(self):
        self.assertIn("RFC 8032", self.content)

    def test_references_mentions_ietf_aivs(self):
        self.assertIn("AIVS", self.content)


class TestShuraCouncilFileIntegrity(unittest.TestCase):
    """Basic file-level checks for shura-council.md."""

    def setUp(self):
        self.path = SHURA_COUNCIL_PATH
        self.content = _read_skill(self.path)

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.path))

    def test_file_is_not_empty(self):
        self.assertGreater(len(self.content), 0)

    def test_header_contains_tier_advanced_infrastructure(self):
        first_line = self.content.splitlines()[0]
        self.assertIn("TIER: ADVANCED_INFRASTRUCTURE", first_line)

    def test_header_uses_comma_not_em_dash(self):
        first_line = self.content.splitlines()[0]
        self.assertNotRegex(first_line, OLD_TIER_PATTERN)
        self.assertIn(",", first_line)


class TestShuraCouncilRequiredSections(unittest.TestCase):
    """Verify all four required sections are present in shura-council.md."""

    def setUp(self):
        self.content = _read_skill(SHURA_COUNCIL_PATH)

    def test_all_required_sections_present(self):
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, self.content)


class TestShuraCouncilNoStubs(unittest.TestCase):
    """Verify no stub placeholders remain in shura-council.md."""

    def setUp(self):
        self.content = _read_skill(SHURA_COUNCIL_PATH)

    def test_no_stub_pattern_anywhere(self):
        for pat in STUB_PATTERNS:
            with self.subTest(pattern=pat.pattern):
                self.assertNotRegex(self.content, pat)

    def test_purpose_section_not_stub(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertGreater(len(body), 100)

    def test_constitutional_alignment_section_not_stub(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertGreater(len(body), 100)

    def test_operational_flow_section_not_stub(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertGreater(len(body), 100)

    def test_failure_modes_section_not_stub(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertGreater(len(body), 50)


class TestShuraCouncilSectionContent(unittest.TestCase):
    """Spot-check key domain content within shura-council.md sections."""

    def setUp(self):
        self.content = _read_skill(SHURA_COUNCIL_PATH)

    def test_purpose_mentions_consensus_protocol(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertTrue(
            "consensus" in body.lower() or "voting" in body.lower(),
            "Purpose must describe the consensus/voting function",
        )

    def test_purpose_mentions_sovereign_constitution(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertIn("sovereign-constitution", body)

    def test_purpose_mentions_byzantine(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertIn("Byzantine", body)

    def test_purpose_mentions_trust_chain(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertIn("trust-chain", body)

    def test_constitutional_alignment_mentions_shura(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertTrue(
            "شورى" in body or "shura" in body.lower() or "consultation" in body.lower(),
            "Constitutional Alignment should reference the shura/consultation principle",
        )

    def test_constitutional_alignment_mentions_green_yellow_red(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertTrue(
            ("green" in body.lower() or "yellow" in body.lower()) and "red" in body.lower(),
            "Constitutional Alignment should describe green/yellow/red proposal classes",
        )

    def test_operational_flow_has_numbered_steps(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        for step_num in range(1, 7):
            with self.subTest(step=step_num):
                self.assertRegex(body, rf"{step_num}\.")

    def test_operational_flow_mentions_48_hour_deadline(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("48", body)

    def test_operational_flow_mentions_two_thirds_majority(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertTrue(
            "two-thirds" in body.lower() or "2/3" in body,
            "Operational Flow must describe the two-thirds quorum requirement",
        )

    def test_operational_flow_mentions_covenant_guard(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("covenant-guard", body)

    def test_operational_flow_mentions_human_signatures(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertTrue(
            "human" in body.lower() and ("sign" in body.lower() or "Ed25519" in body),
            "Operational Flow must describe human Ed25519 signing for red proposals",
        )

    def test_failure_modes_is_a_table(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertIn("|", body)

    def test_failure_modes_covers_byzantine_voters(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "byzantine" in body.lower() or "Byzantine" in body,
            "Failure Modes must address Byzantine voter attacks",
        )

    def test_failure_modes_covers_no_quorum(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "quorum" in body.lower() or "no_consensus" in body,
            "Failure Modes must address no-quorum scenarios",
        )

    def test_failure_modes_covers_red_timeout(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "timed out" in body.lower() or "timeout" in body.lower() or "48" in body,
            "Failure Modes must address red-proposal timeout",
        )

    def test_failure_modes_covers_single_agent_dominance(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "dominat" in body.lower() or "1/3" in body or "cap" in body.lower(),
            "Failure Modes must address single-agent dominance",
        )

    def test_has_references_section(self):
        self.assertIn("## References", self.content)

    def test_references_mentions_bft(self):
        self.assertTrue(
            "Byzantine" in self.content or "BFT" in self.content,
            "References should cite Byzantine Fault Tolerance literature",
        )

    def test_references_mentions_castro_liskov(self):
        """Castro & Liskov PBFT is the foundational reference cited in the skill."""
        self.assertIn("Castro", self.content)


class TestSovereignConstitutionFileIntegrity(unittest.TestCase):
    """Basic file-level checks for sovereign-constitution.md."""

    def setUp(self):
        self.path = SOVEREIGN_CONSTITUTION_PATH
        self.content = _read_skill(self.path)

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(self.path))

    def test_file_is_not_empty(self):
        self.assertGreater(len(self.content), 0)

    def test_header_contains_tier_sovereign(self):
        first_line = self.content.splitlines()[0]
        self.assertIn("TIER: SOVEREIGN", first_line)

    def test_header_uses_comma_not_em_dash(self):
        first_line = self.content.splitlines()[0]
        self.assertNotRegex(first_line, OLD_TIER_PATTERN)
        self.assertIn(",", first_line)


class TestSovereignConstitutionRequiredSections(unittest.TestCase):
    """Verify all four required sections are present in sovereign-constitution.md."""

    def setUp(self):
        self.content = _read_skill(SOVEREIGN_CONSTITUTION_PATH)

    def test_all_required_sections_present(self):
        for section in REQUIRED_SECTIONS:
            with self.subTest(section=section):
                self.assertIn(section, self.content)


class TestSovereignConstitutionNoStubs(unittest.TestCase):
    """Verify no stub placeholders remain in sovereign-constitution.md."""

    def setUp(self):
        self.content = _read_skill(SOVEREIGN_CONSTITUTION_PATH)

    def test_no_stub_pattern_anywhere(self):
        for pat in STUB_PATTERNS:
            with self.subTest(pattern=pat.pattern):
                self.assertNotRegex(self.content, pat)

    def test_purpose_section_not_stub(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertGreater(len(body), 100)

    def test_constitutional_alignment_section_not_stub(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertGreater(len(body), 100)

    def test_operational_flow_section_not_stub(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertGreater(len(body), 100)

    def test_failure_modes_section_not_stub(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertGreater(len(body), 50)


class TestSovereignConstitutionSectionContent(unittest.TestCase):
    """Spot-check key domain content within sovereign-constitution.md sections."""

    def setUp(self):
        self.content = _read_skill(SOVEREIGN_CONSTITUTION_PATH)

    def test_purpose_mentions_approved_blocked_escalate(self):
        body = _extract_section_body(self.content, "## Purpose")
        for verdict in ("approved", "blocked", "escalate"):
            with self.subTest(verdict=verdict):
                self.assertIn(verdict, body)

    def test_purpose_mentions_governance(self):
        body = _extract_section_body(self.content, "## Purpose")
        self.assertTrue(
            "governance" in body.lower() or "principles" in body.lower(),
            "Purpose must describe the governance/principles function",
        )

    def test_purpose_does_not_execute_itself(self):
        """The skill gates work; it does not execute work itself."""
        body = _extract_section_body(self.content, "## Purpose")
        self.assertIn("gates", body.lower())

    def test_constitutional_alignment_references_anthropic(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertIn("Anthropic", body)

    def test_constitutional_alignment_references_bai_et_al(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertIn("Bai", body)

    def test_constitutional_alignment_describes_four_layers(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertTrue(
            "four-layer" in body.lower() or "Absolute Layer" in body,
            "Constitutional Alignment must describe the four-layer constitution",
        )

    def test_constitutional_alignment_mentions_override_detector(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertIn("OverrideDetector", body)

    def test_constitutional_alignment_is_substantive(self):
        body = _extract_section_body(self.content, "## Constitutional Alignment")
        self.assertGreater(len(body), 200)

    def test_operational_flow_has_numbered_steps(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        for step_num in range(1, 7):
            with self.subTest(step=step_num):
                self.assertRegex(body, rf"{step_num}\.")

    def test_operational_flow_mentions_haram_guard(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("HaramGuard", body)

    def test_operational_flow_mentions_ethical_filter(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("EthicalFilter", body)

    def test_operational_flow_mentions_shura_council_escalation(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("shura-council", body)

    def test_operational_flow_mentions_trust_chain(self):
        body = _extract_section_body(self.content, "## Operational Flow")
        self.assertIn("trust-chain", body)

    def test_failure_modes_is_a_table(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertIn("|", body)

    def test_failure_modes_covers_db_corruption(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "corruption" in body.lower() or "tamper" in body.lower(),
            "Failure Modes must address DB corruption or tampering",
        )

    def test_failure_modes_covers_override_attempt(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "override" in body.lower() or "Override" in body,
            "Failure Modes must address override attempts",
        )

    def test_failure_modes_covers_unsigned_context(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "unsigned" in body.lower() or "no_covenant" in body,
            "Failure Modes must address unsigned/covenant-less callers",
        )

    def test_failure_modes_covers_latency_timeout(self):
        body = _extract_section_body(self.content, "## Failure Modes")
        self.assertTrue(
            "latency" in body.lower() or "timeout" in body.lower(),
            "Failure Modes must address latency/timeout scenarios",
        )

    def test_has_references_section(self):
        self.assertIn("## References", self.content)

    def test_references_mentions_constitutional_ai(self):
        self.assertTrue(
            "Constitutional AI" in self.content or "constitutional-ai" in self.content.lower(),
            "References should cite Constitutional AI (Bai et al., 2022)",
        )

    def test_references_mentions_owasp(self):
        self.assertIn("OWASP", self.content)


class TestCrossSkillReferences(unittest.TestCase):
    """
    Verify that the cross-skill references between the three sovereignty-layer
    skills are intact after the PR content fill.
    """

    def setUp(self):
        self.covenant = _read_skill(COVENANT_GUARD_PATH)
        self.shura = _read_skill(SHURA_COUNCIL_PATH)
        self.constitution = _read_skill(SOVEREIGN_CONSTITUTION_PATH)

    def test_shura_council_references_sovereign_constitution(self):
        """shura-council's Purpose says it acts when sovereign-constitution escalates."""
        self.assertIn("sovereign-constitution", self.shura)

    def test_shura_council_references_covenant_guard(self):
        """shura-council's Operational Flow rejects agents without covenant-guard sig."""
        self.assertIn("covenant-guard", self.shura)

    def test_covenant_guard_references_shura_council(self):
        """covenant-guard escalates covenant tampering to shura-council."""
        self.assertIn("shura-council", self.covenant)

    def test_covenant_guard_references_trust_chain(self):
        self.assertIn("trust-chain", self.covenant)

    def test_sovereign_constitution_references_shura_council(self):
        """sovereign-constitution escalates ambiguous proposals to shura-council."""
        self.assertIn("shura-council", self.constitution)

    def test_sovereign_constitution_references_covenant_guard(self):
        """sovereign-constitution requires covenant signatures (no_covenant verdict)."""
        self.assertIn("covenant-guard", self.constitution)

    def test_sovereign_constitution_references_trust_chain(self):
        self.assertIn("trust-chain", self.constitution)

    def test_all_three_skills_mention_ed25519(self):
        """Ed25519 is the shared cryptographic primitive across all three skills."""
        for name, content in (
            ("covenant-guard", self.covenant),
            ("shura-council", self.shura),
            ("sovereign-constitution", self.constitution),
        ):
            with self.subTest(skill=name):
                self.assertIn(
                    "Ed25519",
                    content,
                    f"{name} should reference the Ed25519 signing primitive",
                )


class TestPackageJsonAixFieldRemoved(unittest.TestCase):
    """
    Verify that the `aix` metadata block was removed from package.json in this PR.
    The block contained stackVersion, stackCodename, spec, layer, layerName, and
    authority fields. This test guards against accidental reintroduction.
    """

    def setUp(self):
        import json
        pkg_path = os.path.join(REPO_ROOT, "package.json")
        with open(pkg_path, encoding="utf-8") as fh:
            self.pkg = json.load(fh)

    def test_aix_field_not_present(self):
        self.assertNotIn(
            "aix",
            self.pkg,
            "package.json must not contain the 'aix' metadata block",
        )

    def test_stack_version_not_present(self):
        """stackVersion was nested inside the removed aix block."""
        self.assertNotIn("stackVersion", self.pkg)

    def test_stack_codename_not_present(self):
        self.assertNotIn("stackCodename", self.pkg)

    def test_spec_not_present_at_top_level(self):
        self.assertNotIn("spec", self.pkg)

    def test_authority_not_present(self):
        self.assertNotIn("authority", self.pkg)

    def test_required_fields_still_present(self):
        """Core npm fields must survive the aix block removal."""
        for field in ("name", "version", "description", "license", "scripts"):
            with self.subTest(field=field):
                self.assertIn(field, self.pkg)

    def test_name_is_unchanged(self):
        self.assertEqual(self.pkg["name"], "aix-agent-skills")

    def test_version_is_unchanged(self):
        self.assertEqual(self.pkg["version"], "1.0.0")

    def test_license_is_unchanged(self):
        self.assertEqual(self.pkg["license"], "Apache-2.0")

    def test_no_unexpected_top_level_fields(self):
        allowed = {"name", "version", "description", "license", "scripts"}
        extra = set(self.pkg.keys()) - allowed
        self.assertEqual(
            set(),
            extra,
            f"Unexpected top-level keys in package.json: {extra}",
        )


if __name__ == "__main__":
    unittest.main()