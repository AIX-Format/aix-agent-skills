"""
Tests for the sovereignty layer skills and PR-level changes introduced in
"feat(skills): fill sovereignty layer with research-backed content".

This PR:
1. Filled the stub sections in skills/covenant-guard.md,
   skills/shura-council.md, and skills/sovereign-constitution.md with
   real, research-backed content.
2. Removed the `aix` metadata block from package.json.
3. Deleted several infrastructure files: scripts/validate_skill_quality.py,
   rules/skills.md, templates/skill-template.md, hooks/repo/pre-commit,
   and the v2 SVG assets.

Tests verify:
- Each of the three sovereignty-layer skills has all four required
  sections present and filled with substantive content (no stubs).
- No placeholder text (TODO: Define, TBD, <fill in>) remains in any
  of the three files.
- The Failure Modes section in each file contains a markdown table with
  real rows.
- The Operational Flow section has numbered steps.
- The Purpose section mentions the canonical skill name.
- package.json no longer carries the `aix` field.
- package.json retains the expected core fields (name, version, description,
  license, scripts).
- All infrastructure files deleted by the PR are truly absent.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

# Required section headers as they appear in the skill files.
REQUIRED_SECTIONS = [
    "Purpose",
    "Constitutional Alignment",
    "Operational Flow",
    "Failure Modes",
]

# Stub patterns that must NOT appear in any section body.
STUB_PATTERNS = [
    re.compile(r"TODO:\s*Define", re.IGNORECASE),
    re.compile(r"^TBD\b", re.IGNORECASE | re.MULTILINE),
    re.compile(r"<fill in>", re.IGNORECASE),
    re.compile(r"<placeholder>", re.IGNORECASE),
]

# The three skill files changed in this PR.
SOVEREIGNTY_SKILLS = [
    "covenant-guard.md",
    "shura-council.md",
    "sovereign-constitution.md",
]

# Canonical skill identifiers expected inside the Purpose section.
SKILL_ID_IN_PURPOSE = {
    "covenant-guard.md": "covenant-guard",
    "shura-council.md": "shura-council",
    "sovereign-constitution.md": "sovereign-constitution",
}

# Files deleted by this PR — none of them should exist.
DELETED_FILES = [
    REPO_ROOT / "scripts" / "validate_skill_quality.py",
    REPO_ROOT / "rules" / "skills.md",
    REPO_ROOT / "templates" / "skill-template.md",
    REPO_ROOT / "hooks" / "repo" / "pre-commit",
    REPO_ROOT / "assets" / "aix-footer-quote-v2.svg",
    REPO_ROOT / "assets" / "aix-stack-diagram-v2.svg",
    REPO_ROOT / "assets" / "aix-stack-header-v2.svg",
    REPO_ROOT / "assets" / "axi-mascot.svg",
]


# ─── helpers ─────────────────────────────────────────────────────────────────


def _read_skill(filename: str) -> str:
    """Return the full text of a skill file."""
    return (SKILLS_DIR / filename).read_text(encoding="utf-8")


def _extract_section_body(text: str, section_header: str) -> str | None:
    """
    Return the body text of a level-2 Markdown section whose header
    matches *section_header* exactly.  Returns None if not found.
    The body ends at the next level-2 heading or at end-of-file.
    """
    pattern = re.compile(
        r"^## " + re.escape(section_header) + r"\s*\n(.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1) if m else None


def _meaningful_lines(body: str) -> list[str]:
    """Strip blanks and HTML comment lines from a section body."""
    return [
        line.strip()
        for line in body.splitlines()
        if line.strip()
        and not line.strip().startswith("<!--")
        and not line.strip().startswith("-->")
    ]


# ─── parameterised fixture ────────────────────────────────────────────────────


@pytest.fixture(params=SOVEREIGNTY_SKILLS)
def skill_file(request) -> tuple[str, str]:
    """Yield (filename, file_text) for each sovereignty-layer skill."""
    filename = request.param
    path = SKILLS_DIR / filename
    assert path.exists(), f"Skill file missing: {path}"
    return filename, path.read_text(encoding="utf-8")


# ─── section-presence tests ──────────────────────────────────────────────────


class TestRequiredSectionsPresent:
    """Every required level-2 section must appear in each skill file."""

    @pytest.mark.parametrize("section", REQUIRED_SECTIONS)
    def test_section_present(self, skill_file, section):
        filename, text = skill_file
        assert f"## {section}" in text, (
            f"{filename}: required section '## {section}' is missing"
        )

    def test_all_four_sections_in_one_pass(self, skill_file):
        """Convenience: fail fast with a list of ALL missing sections."""
        filename, text = skill_file
        missing = [s for s in REQUIRED_SECTIONS if f"## {s}" not in text]
        assert not missing, (
            f"{filename}: missing sections: {missing}"
        )


# ─── no-stub tests ────────────────────────────────────────────────────────────


class TestNoStubContent:
    """Stub placeholder text must not appear anywhere in the file."""

    @pytest.mark.parametrize("pat", STUB_PATTERNS, ids=[p.pattern for p in STUB_PATTERNS])
    def test_no_stub_pattern_in_file(self, skill_file, pat):
        filename, text = skill_file
        assert not pat.search(text), (
            f"{filename}: stub pattern {pat.pattern!r} still present"
        )

    def test_purpose_body_is_not_empty(self, skill_file):
        filename, text = skill_file
        body = _extract_section_body(text, "Purpose")
        assert body is not None, f"{filename}: '## Purpose' section not found"
        meaningful = _meaningful_lines(body)
        assert len(meaningful) >= 2, (
            f"{filename}: '## Purpose' body has fewer than 2 meaningful lines; "
            f"got {len(meaningful)}"
        )

    def test_constitutional_alignment_body_not_empty(self, skill_file):
        filename, text = skill_file
        body = _extract_section_body(text, "Constitutional Alignment")
        assert body is not None, (
            f"{filename}: '## Constitutional Alignment' section not found"
        )
        meaningful = _meaningful_lines(body)
        assert len(meaningful) >= 2, (
            f"{filename}: '## Constitutional Alignment' body has fewer than 2 "
            f"meaningful lines; got {len(meaningful)}"
        )

    def test_operational_flow_body_not_empty(self, skill_file):
        filename, text = skill_file
        body = _extract_section_body(text, "Operational Flow")
        assert body is not None, (
            f"{filename}: '## Operational Flow' section not found"
        )
        meaningful = _meaningful_lines(body)
        assert len(meaningful) >= 3, (
            f"{filename}: '## Operational Flow' body has fewer than 3 "
            f"meaningful lines; got {len(meaningful)}"
        )

    def test_failure_modes_body_not_empty(self, skill_file):
        filename, text = skill_file
        body = _extract_section_body(text, "Failure Modes")
        assert body is not None, (
            f"{filename}: '## Failure Modes' section not found"
        )
        meaningful = _meaningful_lines(body)
        assert len(meaningful) >= 2, (
            f"{filename}: '## Failure Modes' body has fewer than 2 meaningful lines; "
            f"got {len(meaningful)}"
        )


# ─── content-quality tests ────────────────────────────────────────────────────


class TestContentQuality:
    """Verify that the filled-in content meets structural quality expectations."""

    def test_operational_flow_has_numbered_steps(self, skill_file):
        """Operational Flow must contain at least three numbered list items."""
        filename, text = skill_file
        body = _extract_section_body(text, "Operational Flow")
        assert body is not None
        # Match lines starting with a digit and a dot (e.g. "1. ", "2. ")
        numbered = re.findall(r"^\s*\d+\.\s+\S", body, re.MULTILINE)
        assert len(numbered) >= 3, (
            f"{filename}: '## Operational Flow' should have at least 3 numbered steps; "
            f"found {len(numbered)}"
        )

    def test_failure_modes_has_markdown_table(self, skill_file):
        """Failure Modes must contain a Markdown table with at least one data row."""
        filename, text = skill_file
        body = _extract_section_body(text, "Failure Modes")
        assert body is not None
        # Table rows start with '|'
        table_rows = [
            ln for ln in body.splitlines()
            if ln.strip().startswith("|") and not re.match(r"^\s*\|[-:| ]+\|\s*$", ln)
        ]
        # At least 2 rows: header + one data row
        assert len(table_rows) >= 2, (
            f"{filename}: '## Failure Modes' must have a table with header + at least "
            f"one data row; found {len(table_rows)} pipe-delimited rows"
        )

    def test_failure_modes_table_has_minimum_entries(self, skill_file):
        """Failure Modes table must have at least 3 data rows (excluding header)."""
        filename, text = skill_file
        body = _extract_section_body(text, "Failure Modes")
        assert body is not None
        lines = body.splitlines()
        # Data rows: start with '|' and are not the header separator
        data_rows = [
            ln for ln in lines
            if ln.strip().startswith("|") and not re.match(r"^\s*\|[-:| ]+\|\s*$", ln)
        ]
        # Subtract one for the header row itself
        non_header_rows = [r for r in data_rows if not re.search(r"\*\*Mode\*\*|Mode\s*\|", r)]
        assert len(non_header_rows) >= 3, (
            f"{filename}: Failure Modes table should have at least 3 data rows "
            f"(excluding header); found {len(non_header_rows)}"
        )

    def test_purpose_mentions_skill_name(self, skill_file):
        """Purpose section must mention the canonical skill identifier."""
        filename, text = skill_file
        skill_id = SKILL_ID_IN_PURPOSE[filename]
        body = _extract_section_body(text, "Purpose")
        assert body is not None
        assert skill_id in body, (
            f"{filename}: '## Purpose' section does not mention the skill id "
            f"'{skill_id}'"
        )

    def test_constitutional_alignment_not_single_word(self, skill_file):
        """Constitutional Alignment must contain a substantive paragraph, not just a label."""
        filename, text = skill_file
        body = _extract_section_body(text, "Constitutional Alignment")
        assert body is not None
        # The body should contain at least 50 words of real text.
        words = re.findall(r"\b\w+\b", body)
        assert len(words) >= 50, (
            f"{filename}: '## Constitutional Alignment' is too short "
            f"({len(words)} words); expected at least 50"
        )

    def test_purpose_not_single_line(self, skill_file):
        """Purpose must span more than one sentence / line of prose."""
        filename, text = skill_file
        body = _extract_section_body(text, "Purpose")
        assert body is not None
        words = re.findall(r"\b\w+\b", body)
        assert len(words) >= 20, (
            f"{filename}: '## Purpose' is too short ({len(words)} words); "
            "expected at least 20"
        )

    def test_no_arabic_only_purpose(self, skill_file):
        """Purpose must include English prose (not just Arabic)."""
        filename, text = skill_file
        body = _extract_section_body(text, "Purpose")
        assert body is not None
        # Check for at least 10 ASCII word characters (Latin alphabet)
        ascii_words = re.findall(r"[A-Za-z]{3,}", body)
        assert len(ascii_words) >= 10, (
            f"{filename}: '## Purpose' should contain English prose; "
            f"found only {len(ascii_words)} ASCII words"
        )


# ─── per-skill specific tests ─────────────────────────────────────────────────


class TestCovenantGuardSpecific:
    """Content checks specific to skills/covenant-guard.md."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.text = _read_skill("covenant-guard.md")

    def test_purpose_mentions_ed25519(self):
        body = _extract_section_body(self.text, "Purpose")
        assert body is not None
        assert "Ed25519" in body, (
            "covenant-guard Purpose should mention 'Ed25519' signing"
        )

    def test_operational_flow_issue_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "Issue" in body, (
            "covenant-guard Operational Flow should describe the Issue step"
        )

    def test_operational_flow_verify_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "Verify" in body, (
            "covenant-guard Operational Flow should describe the Verify step"
        )

    def test_operational_flow_revoke_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        # Either "Revoke" or "revoke" should appear
        assert re.search(r"\bRevoke\b|\brevoke\b", body), (
            "covenant-guard Operational Flow should describe the Revoke step"
        )

    def test_failure_modes_includes_signature_mismatch(self):
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert "Signature mismatch" in body or "signature mismatch" in body, (
            "covenant-guard Failure Modes should include a 'Signature mismatch' entry"
        )

    def test_failure_modes_includes_renewal_cycle(self):
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert "Renewal cycle" in body or "renewal cycle" in body, (
            "covenant-guard Failure Modes should include a 'Renewal cycle exceeded' entry"
        )

    def test_references_section_exists(self):
        assert "## References" in self.text, (
            "covenant-guard.md should have a '## References' section"
        )

    def test_references_mentions_ed25519_rfc(self):
        body = _extract_section_body(self.text, "References")
        assert body is not None
        assert "RFC 8032" in body, (
            "covenant-guard References should cite RFC 8032 (EdDSA)"
        )

    def test_tier_label_present(self):
        first_line = self.text.splitlines()[0]
        assert "SOVEREIGN" in first_line, (
            "covenant-guard first line should declare TIER: SOVEREIGN"
        )

    def test_rule_of_nine_mentioned(self):
        """The rule-of-9 is a key business rule that should appear in Failure Modes."""
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert re.search(r"\b9\b|rule.of.9|rule-of-9", body, re.IGNORECASE), (
            "covenant-guard Failure Modes should reference the rule-of-9 circuit breaker"
        )


class TestShuraCouncilSpecific:
    """Content checks specific to skills/shura-council.md."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.text = _read_skill("shura-council.md")

    def test_purpose_mentions_consensus(self):
        body = _extract_section_body(self.text, "Purpose")
        assert body is not None
        assert "consensus" in body.lower(), (
            "shura-council Purpose should mention consensus protocol"
        )

    def test_purpose_mentions_sovereign_constitution(self):
        body = _extract_section_body(self.text, "Purpose")
        assert body is not None
        assert "sovereign-constitution" in body, (
            "shura-council Purpose should reference 'sovereign-constitution' as caller"
        )

    def test_operational_flow_classify_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "Classify" in body or "classify" in body, (
            "shura-council Operational Flow should include a Classify step"
        )

    def test_operational_flow_commit_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "Commit" in body or "commit" in body, (
            "shura-council Operational Flow should include a Commit step"
        )

    def test_operational_flow_record_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "Record" in body or "record" in body, (
            "shura-council Operational Flow should include a Record step"
        )

    def test_failure_modes_byzantine_voters(self):
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert "Byzantine" in body, (
            "shura-council Failure Modes should include a Byzantine voters entry"
        )

    def test_failure_modes_red_proposal_timeout(self):
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert "timeout" in body.lower() or "timed out" in body.lower(), (
            "shura-council Failure Modes should address red proposal timeout"
        )

    def test_constitutional_alignment_mentions_layers(self):
        body = _extract_section_body(self.text, "Constitutional Alignment")
        assert body is not None
        assert "Absolute" in body and "Consensus" in body, (
            "shura-council Constitutional Alignment should mention Absolute and Consensus layers"
        )

    def test_references_section_exists(self):
        assert "## References" in self.text, (
            "shura-council.md should have a '## References' section"
        )

    def test_references_mentions_bft(self):
        body = _extract_section_body(self.text, "References")
        assert body is not None
        assert "Byzantine" in body or "BFT" in body, (
            "shura-council References should cite BFT research"
        )

    def test_tier_label_present(self):
        first_line = self.text.splitlines()[0]
        assert "ADVANCED_INFRASTRUCTURE" in first_line, (
            "shura-council first line should declare TIER: ADVANCED_INFRASTRUCTURE"
        )

    def test_two_thirds_majority_rule(self):
        """Two-thirds majority is the stated quorum rule and must appear in the flow."""
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert re.search(r"two.thirds|2/3", body, re.IGNORECASE), (
            "shura-council Operational Flow should state the two-thirds majority rule"
        )

    def test_48_hour_red_deadline(self):
        """48-hour timeout for red proposals must appear in Operational Flow."""
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "48" in body, (
            "shura-council Operational Flow should specify the 48-hour deadline for red proposals"
        )


class TestSovereignConstitutionSpecific:
    """Content checks specific to skills/sovereign-constitution.md."""

    @pytest.fixture(autouse=True)
    def _load(self):
        self.text = _read_skill("sovereign-constitution.md")

    def test_purpose_mentions_verdicts(self):
        body = _extract_section_body(self.text, "Purpose")
        assert body is not None
        # The three possible verdicts
        assert "approved" in body and "blocked" in body and "escalate" in body, (
            "sovereign-constitution Purpose should describe the three verdicts: "
            "approved, blocked, escalate"
        )

    def test_operational_flow_haram_guard_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "HaramGuard" in body, (
            "sovereign-constitution Operational Flow should reference the HaramGuard step"
        )

    def test_operational_flow_ethical_filter_step(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "EthicalFilter" in body, (
            "sovereign-constitution Operational Flow should reference EthicalFilter"
        )

    def test_operational_flow_trust_chain_record(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "trust-chain" in body, (
            "sovereign-constitution Operational Flow should record decisions in trust-chain"
        )

    def test_failure_modes_override_attempt(self):
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert "Override" in body or "override" in body, (
            "sovereign-constitution Failure Modes should address override attempts"
        )

    def test_failure_modes_unsigned_context(self):
        body = _extract_section_body(self.text, "Failure Modes")
        assert body is not None
        assert "unsigned" in body.lower() or "no_covenant" in body, (
            "sovereign-constitution Failure Modes should address unsigned/no_covenant callers"
        )

    def test_constitutional_alignment_references_anthropic(self):
        body = _extract_section_body(self.text, "Constitutional Alignment")
        assert body is not None
        assert "Anthropic" in body, (
            "sovereign-constitution Constitutional Alignment should reference Constitutional AI (Anthropic)"
        )

    def test_references_section_exists(self):
        assert "## References" in self.text, (
            "sovereign-constitution.md should have a '## References' section"
        )

    def test_references_bai_et_al_2022(self):
        body = _extract_section_body(self.text, "References")
        assert body is not None
        assert "Bai" in body and "2022" in body, (
            "sovereign-constitution References should cite Bai et al. 2022 (Constitutional AI)"
        )

    def test_tier_label_present(self):
        first_line = self.text.splitlines()[0]
        assert "SOVEREIGN" in first_line, (
            "sovereign-constitution first line should declare TIER: SOVEREIGN"
        )

    def test_four_layer_constitution_described(self):
        """The four constitutional layers must be mentioned in the file."""
        assert "Absolute" in self.text, "sovereign-constitution should mention the Absolute Layer"
        assert "Interpretive" in self.text, "sovereign-constitution should mention the Interpretive Layer"
        assert "Consensus" in self.text, "sovereign-constitution should mention the Consensus Layer"
        assert "Experimental" in self.text, "sovereign-constitution should mention the Experimental Layer"

    def test_shura_council_referenced_in_flow(self):
        body = _extract_section_body(self.text, "Operational Flow")
        assert body is not None
        assert "shura-council" in body, (
            "sovereign-constitution Operational Flow must escalate to 'shura-council'"
        )


# ─── package.json tests ───────────────────────────────────────────────────────


class TestPackageJsonChanges:
    """Verify the package.json changes introduced by this PR."""

    @pytest.fixture(autouse=True)
    def _load(self):
        pkg_path = REPO_ROOT / "package.json"
        assert pkg_path.exists(), "package.json must exist"
        self.pkg = json.loads(pkg_path.read_text(encoding="utf-8"))

    def test_aix_field_removed(self):
        """The `aix` metadata block was removed in this PR."""
        assert "aix" not in self.pkg, (
            "package.json should no longer contain the 'aix' field after this PR"
        )

    def test_name_field_preserved(self):
        assert self.pkg.get("name") == "aix-agent-skills", (
            "package.json 'name' field must remain 'aix-agent-skills'"
        )

    def test_version_field_preserved(self):
        assert "version" in self.pkg, "package.json 'version' field must still exist"
        assert isinstance(self.pkg["version"], str), (
            "package.json 'version' must be a string"
        )

    def test_license_field_preserved(self):
        assert self.pkg.get("license") == "Apache-2.0", (
            "package.json 'license' must remain 'Apache-2.0'"
        )

    def test_description_field_preserved(self):
        assert "description" in self.pkg, "package.json 'description' field must still exist"
        assert len(self.pkg["description"]) > 0, "package.json 'description' must not be empty"

    def test_scripts_field_preserved(self):
        assert "scripts" in self.pkg, "package.json 'scripts' field must still exist"
        assert "test" in self.pkg["scripts"], (
            "package.json 'scripts.test' must still be defined"
        )

    def test_no_stack_version_in_aix(self):
        """stackVersion was inside the removed `aix` block and must not appear at root level."""
        assert "stackVersion" not in self.pkg, (
            "stackVersion must not appear at the root of package.json"
        )

    def test_no_stack_codename_at_root(self):
        """stackCodename (Echo369) was inside the removed `aix` block."""
        assert "stackCodename" not in self.pkg, (
            "stackCodename must not appear at the root of package.json"
        )


# ─── deleted-files tests ──────────────────────────────────────────────────────


class TestDeletedFiles:
    """Infrastructure files removed in this PR must not exist in the repo."""

    @pytest.mark.parametrize(
        "deleted_path",
        DELETED_FILES,
        ids=[str(p.relative_to(REPO_ROOT)) for p in DELETED_FILES],
    )
    def test_file_does_not_exist(self, deleted_path):
        assert not deleted_path.exists(), (
            f"File should have been deleted by this PR but still exists: "
            f"{deleted_path.relative_to(REPO_ROOT)}"
        )

    def test_validate_skill_quality_script_absent(self):
        """Explicit test: the Python quality-gate script was replaced by other mechanisms."""
        target = REPO_ROOT / "scripts" / "validate_skill_quality.py"
        assert not target.exists(), (
            "scripts/validate_skill_quality.py should have been deleted in this PR"
        )

    def test_rules_skills_md_absent(self):
        target = REPO_ROOT / "rules" / "skills.md"
        assert not target.exists(), (
            "rules/skills.md should have been deleted in this PR"
        )

    def test_skill_template_absent(self):
        target = REPO_ROOT / "templates" / "skill-template.md"
        assert not target.exists(), (
            "templates/skill-template.md should have been deleted in this PR"
        )

    def test_pre_commit_hook_absent(self):
        target = REPO_ROOT / "hooks" / "repo" / "pre-commit"
        assert not target.exists(), (
            "hooks/repo/pre-commit should have been deleted in this PR"
        )

    def test_v2_footer_svg_absent(self):
        target = REPO_ROOT / "assets" / "aix-footer-quote-v2.svg"
        assert not target.exists(), (
            "assets/aix-footer-quote-v2.svg should have been deleted in this PR"
        )

    def test_v2_diagram_svg_absent(self):
        target = REPO_ROOT / "assets" / "aix-stack-diagram-v2.svg"
        assert not target.exists(), (
            "assets/aix-stack-diagram-v2.svg should have been deleted in this PR"
        )

    def test_v2_header_svg_absent(self):
        target = REPO_ROOT / "assets" / "aix-stack-header-v2.svg"
        assert not target.exists(), (
            "assets/aix-stack-header-v2.svg should have been deleted in this PR"
        )

    def test_mascot_svg_absent(self):
        target = REPO_ROOT / "assets" / "axi-mascot.svg"
        assert not target.exists(), (
            "assets/axi-mascot.svg should have been deleted in this PR"
        )


# ─── cross-skill integration checks ──────────────────────────────────────────


class TestCrossSkillIntegration:
    """Verify that the three skills correctly reference each other."""

    def test_covenant_guard_referenced_in_shura_council(self):
        """shura-council must require a covenant-guard signature on panel members."""
        text = _read_skill("shura-council.md")
        assert "covenant-guard" in text, (
            "shura-council should reference covenant-guard for panel membership validation"
        )

    def test_sovereign_constitution_references_shura_council(self):
        """sovereign-constitution escalates to shura-council for red-class proposals."""
        text = _read_skill("sovereign-constitution.md")
        assert "shura-council" in text, (
            "sovereign-constitution should reference shura-council for escalation"
        )

    def test_covenant_guard_references_shura_council(self):
        """covenant-guard freezes agents and notifies shura-council on violations."""
        text = _read_skill("covenant-guard.md")
        assert "shura-council" in text, (
            "covenant-guard should reference shura-council for violation escalation"
        )

    def test_sovereign_constitution_references_covenant_guard(self):
        """sovereign-constitution should reference covenant-guard for signed callers."""
        text = _read_skill("sovereign-constitution.md")
        assert "covenant-guard" in text, (
            "sovereign-constitution should reference covenant-guard for caller verification"
        )

    def test_all_three_skills_reference_trust_chain(self):
        """All three sovereignty-layer skills must write their decisions to trust-chain."""
        for filename in SOVEREIGNTY_SKILLS:
            text = _read_skill(filename)
            assert "trust-chain" in text, (
                f"{filename} should reference 'trust-chain' for audit persistence"
            )
