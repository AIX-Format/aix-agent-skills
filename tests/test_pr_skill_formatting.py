"""
Tests for skill file changes introduced in this PR.

This PR made the following formatting changes:
  - skills/covenant-guard.md:   title separator changed from ", TIER:" to " — TIER:"
  - skills/shura-council.md:    title separator changed from ", TIER:" to " — TIER:"
  - skills/sovereign-constitution.md: title separator changed from ", TIER:" to " — TIER:"
  - skills/covenant-guard.md:   oath item 3 separator changed from ", والاعتراف" to " — والاعتراف"
  - skills/sovereign-constitution.md: HaramGuard and EthicalFilter table rows now use "—"
  - skills/owasp-agentic-guard.md: deleted entirely
  - skills.json: owasp-agentic-guard entry removed from the skills array
"""

import json
import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS_DIR = os.path.join(REPO_ROOT, "skills")
SKILLS_JSON_PATH = os.path.join(REPO_ROOT, "skills.json")

COVENANT_GUARD_PATH = os.path.join(SKILLS_DIR, "covenant-guard.md")
SHURA_COUNCIL_PATH = os.path.join(SKILLS_DIR, "shura-council.md")
SOVEREIGN_CONSTITUTION_PATH = os.path.join(SKILLS_DIR, "sovereign-constitution.md")
OWASP_GUARD_PATH = os.path.join(SKILLS_DIR, "owasp-agentic-guard.md")


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def _first_line(path: str) -> str:
    return _read(path).splitlines()[0]


# ---------------------------------------------------------------------------
# owasp-agentic-guard.md deletion
# ---------------------------------------------------------------------------

class TestOwaspAgenticGuardDeleted(unittest.TestCase):
    """The file skills/owasp-agentic-guard.md must not exist after this PR."""

    def test_file_does_not_exist_on_disk(self):
        self.assertFalse(
            os.path.isfile(OWASP_GUARD_PATH),
            "skills/owasp-agentic-guard.md must have been deleted by this PR",
        )

    def test_owasp_guard_not_in_skills_json(self):
        """The owasp-agentic-guard entry must also be absent from skills.json."""
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        names = [s["name"] for s in data["skills"]]
        self.assertNotIn(
            "owasp-agentic-guard",
            names,
            "owasp-agentic-guard must not appear in skills.json after this PR",
        )

    def test_owasp_guard_file_path_not_in_skills_json(self):
        """The file reference skills/owasp-agentic-guard.md must be absent from skills.json."""
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            raw = fh.read()
        self.assertNotIn(
            "owasp-agentic-guard.md",
            raw,
            "skills.json must not reference owasp-agentic-guard.md",
        )


# ---------------------------------------------------------------------------
# skills/covenant-guard.md formatting
# ---------------------------------------------------------------------------

class TestCovenantGuardTitleFormat(unittest.TestCase):
    """The covenant-guard.md title must now use em-dash separator before TIER."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(COVENANT_GUARD_PATH))

    def test_title_uses_em_dash_separator(self):
        first = _first_line(COVENANT_GUARD_PATH)
        self.assertIn(
            "—",
            first,
            f"covenant-guard.md H1 must use em-dash separator; got: {first!r}",
        )

    def test_title_format_is_name_em_dash_tier(self):
        """Title must be '# ... — TIER: SOVEREIGN' (em-dash then space then TIER)."""
        first = _first_line(COVENANT_GUARD_PATH)
        self.assertIn(
            "— TIER: SOVEREIGN",
            first,
            f"covenant-guard.md title must contain '— TIER: SOVEREIGN'; got: {first!r}",
        )

    def test_title_does_not_use_comma_before_tier(self):
        """Old format used ', TIER:' — this must no longer appear in the title."""
        first = _first_line(COVENANT_GUARD_PATH)
        self.assertNotIn(
            ", TIER:",
            first,
            f"covenant-guard.md title must not use old comma separator; got: {first!r}",
        )

    def test_title_is_h1(self):
        first = _first_line(COVENANT_GUARD_PATH)
        self.assertTrue(
            first.startswith("# "),
            f"covenant-guard.md first line must be an H1 heading; got: {first!r}",
        )

    def test_title_mentions_covenant_guard(self):
        first = _first_line(COVENANT_GUARD_PATH)
        self.assertIn("Covenant Guard", first)

    def test_title_mentions_sovereign_tier(self):
        first = _first_line(COVENANT_GUARD_PATH)
        self.assertIn("SOVEREIGN", first)


class TestCovenantGuardOathFormatting(unittest.TestCase):
    """Oath item 3 was updated to use em-dash instead of comma."""

    def setUp(self):
        self.content = _read(COVENANT_GUARD_PATH)

    def test_oath_item_3_uses_em_dash(self):
        """The third oath now reads '…لا تضليل — والاعتراف…'."""
        self.assertIn(
            "لا تضليل — والاعتراف الفوري بالخطأ",
            self.content,
            "Oath item 3 must use em-dash: 'لا تضليل — والاعتراف الفوري بالخطأ'",
        )

    def test_oath_item_3_does_not_use_old_comma_format(self):
        """Old format used a period followed by 'والاعتراف' — should not appear."""
        # Old text was: "لا تضليل. والاعتراف الفوري بالخطأ"
        self.assertNotIn(
            "لا تضليل. والاعتراف",
            self.content,
            "Oath item 3 must not use old period-separator format",
        )

    def test_three_oaths_all_present(self):
        """All three عهود must still be present in the file."""
        self.assertIn("عهد العبودية للحقيقة", self.content, "First oath must be present")
        self.assertIn("عهد خدمة الإنسان", self.content, "Second oath must be present")
        self.assertIn("عهد الصدق", self.content, "Third oath must be present")

    def test_rule_of_9_section_present(self):
        """The 'قاعدة الـ 9' (Rule of 9) section must still be present."""
        self.assertIn(
            "قاعدة الـ 9",
            self.content,
            "Rule-of-9 section must be retained in covenant-guard.md",
        )


class TestCovenantGuardRequiredSections(unittest.TestCase):
    """Required section headings must still exist (now as TODO stubs)."""

    def setUp(self):
        self.content = _read(COVENANT_GUARD_PATH)

    def test_purpose_section_exists(self):
        self.assertIn("## Purpose", self.content)

    def test_constitutional_alignment_section_exists(self):
        self.assertIn("## Constitutional Alignment", self.content)

    def test_operational_flow_section_exists(self):
        self.assertIn("## Operational Flow", self.content)

    def test_failure_modes_section_exists(self):
        self.assertIn("## Failure Modes", self.content)

    def test_purpose_section_has_todo_stub(self):
        """The Purpose section was replaced with a TODO stub in this PR."""
        self.assertIn("TODO: Define purpose.", self.content)

    def test_operational_flow_has_todo_stub(self):
        self.assertIn("TODO: Define operational flow.", self.content)

    def test_failure_modes_has_todo_stub(self):
        self.assertIn("TODO: Define failure modes.", self.content)

    def test_detailed_operational_flow_removed(self):
        """Long operational flow steps were replaced with TODO — must not appear."""
        self.assertNotIn(
            "On first activation, present the canonical covenant text",
            self.content,
            "Old detailed operational flow content must have been removed",
        )

    def test_detailed_failure_modes_table_removed(self):
        """Old failure mode table rows must not be in the file."""
        self.assertNotIn(
            "Signature mismatch on a normal call",
            self.content,
            "Old failure modes table must have been removed",
        )


# ---------------------------------------------------------------------------
# skills/shura-council.md formatting
# ---------------------------------------------------------------------------

class TestShuraCouncilTitleFormat(unittest.TestCase):
    """The shura-council.md title must use em-dash separator before TIER."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(SHURA_COUNCIL_PATH))

    def test_title_uses_em_dash_separator(self):
        first = _first_line(SHURA_COUNCIL_PATH)
        self.assertIn(
            "—",
            first,
            f"shura-council.md H1 must use em-dash separator; got: {first!r}",
        )

    def test_title_format_is_name_em_dash_tier(self):
        first = _first_line(SHURA_COUNCIL_PATH)
        self.assertIn(
            "— TIER: ADVANCED_INFRASTRUCTURE",
            first,
            f"shura-council.md title must contain '— TIER: ADVANCED_INFRASTRUCTURE'; got: {first!r}",
        )

    def test_title_does_not_use_comma_before_tier(self):
        first = _first_line(SHURA_COUNCIL_PATH)
        self.assertNotIn(
            ", TIER:",
            first,
            f"shura-council.md title must not use old comma separator; got: {first!r}",
        )

    def test_title_is_h1(self):
        first = _first_line(SHURA_COUNCIL_PATH)
        self.assertTrue(first.startswith("# "))

    def test_title_mentions_shura_council(self):
        first = _first_line(SHURA_COUNCIL_PATH)
        self.assertIn("Shura Council", first)

    def test_title_mentions_advanced_infrastructure_tier(self):
        first = _first_line(SHURA_COUNCIL_PATH)
        self.assertIn("ADVANCED_INFRASTRUCTURE", first)


class TestShuraCouncilRequiredSections(unittest.TestCase):
    """Required section headings must still exist in shura-council.md."""

    def setUp(self):
        self.content = _read(SHURA_COUNCIL_PATH)

    def test_purpose_section_exists(self):
        self.assertIn("## Purpose", self.content)

    def test_constitutional_alignment_section_exists(self):
        self.assertIn("## Constitutional Alignment", self.content)

    def test_operational_flow_section_exists(self):
        self.assertIn("## Operational Flow", self.content)

    def test_failure_modes_section_exists(self):
        self.assertIn("## Failure Modes", self.content)

    def test_purpose_section_has_todo_stub(self):
        self.assertIn("TODO: Define purpose.", self.content)

    def test_detailed_operational_flow_removed(self):
        """Long operational flow was replaced with TODO."""
        self.assertNotIn(
            "Classify. On `escalate` from `sovereign-constitution`",
            self.content,
            "Old detailed operational flow must have been removed from shura-council.md",
        )

    def test_byzantine_references_removed(self):
        """Byzantine-fault-tolerance research citations were removed in this PR."""
        self.assertNotIn(
            "Byzantine-Robust Decentralized Coordination",
            self.content,
        )

    def test_arabic_core_content_retained(self):
        """Core Arabic content (authority levels) must still be present."""
        self.assertIn("هيكل السلطة الثلاثي", self.content, "Three-level authority section must be retained")
        self.assertIn("آلية الفيتو البشري", self.content, "Human veto mechanism section must be retained")


# ---------------------------------------------------------------------------
# skills/sovereign-constitution.md formatting
# ---------------------------------------------------------------------------

class TestSovereignConstitutionTitleFormat(unittest.TestCase):
    """The sovereign-constitution.md title must use em-dash separator before TIER."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(SOVEREIGN_CONSTITUTION_PATH))

    def test_title_uses_em_dash_separator(self):
        first = _first_line(SOVEREIGN_CONSTITUTION_PATH)
        self.assertIn(
            "—",
            first,
            f"sovereign-constitution.md H1 must use em-dash separator; got: {first!r}",
        )

    def test_title_format_is_name_em_dash_tier(self):
        first = _first_line(SOVEREIGN_CONSTITUTION_PATH)
        self.assertIn(
            "— TIER: SOVEREIGN",
            first,
            f"sovereign-constitution.md title must contain '— TIER: SOVEREIGN'; got: {first!r}",
        )

    def test_title_does_not_use_comma_before_tier(self):
        first = _first_line(SOVEREIGN_CONSTITUTION_PATH)
        self.assertNotIn(
            ", TIER:",
            first,
            f"sovereign-constitution.md title must not use old comma separator; got: {first!r}",
        )

    def test_title_is_h1(self):
        first = _first_line(SOVEREIGN_CONSTITUTION_PATH)
        self.assertTrue(first.startswith("# "))

    def test_title_mentions_sovereign_constitution(self):
        first = _first_line(SOVEREIGN_CONSTITUTION_PATH)
        self.assertIn("Sovereign Constitution", first)

    def test_title_mentions_sovereign_tier(self):
        first = _first_line(SOVEREIGN_CONSTITUTION_PATH)
        self.assertIn("SOVEREIGN", first)


class TestSovereignConstitutionTableFormatting(unittest.TestCase):
    """The five-components table was updated to use em-dash separators."""

    def setUp(self):
        self.content = _read(SOVEREIGN_CONSTITUTION_PATH)

    def test_haramguard_row_uses_em_dash(self):
        """HaramGuard description row must use em-dash: '…المطلقة — لا تُناقش…'."""
        self.assertIn(
            "قائمة المحظورات المطلقة — لا تُناقش ولا تُفاوض",
            self.content,
            "HaramGuard row must use em-dash separator '—' (not comma)",
        )

    def test_ethicalfilter_row_uses_em_dash(self):
        """EthicalFilter description row must use em-dash: '…النوايا — يفحص…'."""
        self.assertIn(
            "فلتر النوايا — يفحص كل مهمة قبل التنفيذ",
            self.content,
            "EthicalFilter row must use em-dash separator '—'",
        )

    def test_haramguard_does_not_use_old_comma_format(self):
        """Old format had a colon or comma before the description."""
        self.assertNotIn(
            "قائمة المحظورات المطلقة, لا تُناقش",
            self.content,
            "HaramGuard row must not use old comma format",
        )

    def test_all_five_components_in_table(self):
        """All five component identifiers must appear in the table."""
        for component in ["HaramGuard", "EthicalFilter", "ConstitutionDB", "ConsultationAPI", "OverrideDetector"]:
            with self.subTest(component=component):
                self.assertIn(
                    component,
                    self.content,
                    f"sovereign-constitution.md must still list the {component} component",
                )


class TestSovereignConstitutionRequiredSections(unittest.TestCase):
    """Required section headings must still exist in sovereign-constitution.md."""

    def setUp(self):
        self.content = _read(SOVEREIGN_CONSTITUTION_PATH)

    def test_purpose_section_exists(self):
        self.assertIn("## Purpose", self.content)

    def test_constitutional_alignment_section_exists(self):
        self.assertIn("## Constitutional Alignment", self.content)

    def test_operational_flow_section_exists(self):
        self.assertIn("## Operational Flow", self.content)

    def test_failure_modes_section_exists(self):
        self.assertIn("## Failure Modes", self.content)

    def test_purpose_has_todo_stub(self):
        self.assertIn("TODO: Define purpose.", self.content)

    def test_detailed_haram_guard_steps_removed(self):
        """Long operational flow prose was replaced by TODO stub."""
        self.assertNotIn(
            "sovereign-constitution` is the operational consultation interface",
            self.content,
            "Old detailed purpose prose must have been removed",
        )

    def test_constitutional_ai_reference_removed(self):
        """Old references to Anthropic Constitutional AI paper removed in this PR."""
        self.assertNotIn(
            "Bai et al., \"Constitutional AI",
            self.content,
            "Detailed Anthropic reference must have been removed",
        )

    def test_arabic_core_content_retained(self):
        self.assertIn("فلسفة التصميم", self.content, "Design philosophy section must be retained")
        self.assertIn("المكونات الخمسة", self.content, "Five components section must be retained")


# ---------------------------------------------------------------------------
# Cross-skill title format consistency
# ---------------------------------------------------------------------------

class TestSkillTitleFormatConsistency(unittest.TestCase):
    """All three modified skill files must follow the same '— TIER:' pattern."""

    SKILL_FILES = [
        (COVENANT_GUARD_PATH, "SOVEREIGN"),
        (SHURA_COUNCIL_PATH, "ADVANCED_INFRASTRUCTURE"),
        (SOVEREIGN_CONSTITUTION_PATH, "SOVEREIGN"),
    ]

    def test_all_titles_use_em_dash_before_tier(self):
        for path, tier in self.SKILL_FILES:
            with self.subTest(file=os.path.basename(path)):
                first = _first_line(path)
                self.assertIn(
                    f"— TIER: {tier}",
                    first,
                    f"{os.path.basename(path)} title must be '# ... — TIER: {tier}'",
                )

    def test_none_of_the_titles_use_comma_before_tier(self):
        for path, _tier in self.SKILL_FILES:
            with self.subTest(file=os.path.basename(path)):
                first = _first_line(path)
                self.assertNotIn(
                    ", TIER:",
                    first,
                    f"{os.path.basename(path)} must not use old comma-before-TIER format",
                )

    def test_all_titles_are_h1(self):
        for path, _tier in self.SKILL_FILES:
            with self.subTest(file=os.path.basename(path)):
                self.assertTrue(_first_line(path).startswith("# "))

    def test_all_modified_files_exist(self):
        for path, _tier in self.SKILL_FILES:
            with self.subTest(file=os.path.basename(path)):
                self.assertTrue(os.path.isfile(path))


# ---------------------------------------------------------------------------
# skills.json: owasp-agentic-guard removal
# ---------------------------------------------------------------------------

class TestSkillsJsonOwaspRemoval(unittest.TestCase):
    """skills.json must not contain any reference to owasp-agentic-guard."""

    def setUp(self):
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            self.data = json.load(fh)
            fh.seek(0)
            self.raw = fh.read()

    def _skill_names(self):
        return [s["name"] for s in self.data["skills"]]

    def _skill_files(self):
        return [s["file"] for s in self.data["skills"]]

    def test_owasp_name_absent(self):
        self.assertNotIn("owasp-agentic-guard", self._skill_names())

    def test_owasp_file_reference_absent(self):
        self.assertNotIn("skills/owasp-agentic-guard.md", self._skill_files())

    def test_owasp_string_not_anywhere_in_file(self):
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            raw = fh.read()
        self.assertNotIn(
            "owasp-agentic-guard",
            raw,
            "The string 'owasp-agentic-guard' must not appear anywhere in skills.json",
        )

    def test_skills_json_is_still_valid_json(self):
        try:
            with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
                json.load(fh)
        except json.JSONDecodeError as exc:
            self.fail(f"skills.json must still be valid JSON after the PR: {exc}")

    def test_skills_array_still_populated(self):
        self.assertGreater(
            len(self.data["skills"]),
            0,
            "skills.json must still have skills entries after the removal",
        )

    def test_skill_count_is_58(self):
        """After removing owasp-agentic-guard (which was the only entry removed),
        the skills array must have exactly 58 entries."""
        self.assertEqual(
            len(self.data["skills"]),
            58,
            f"Expected 58 skills after owasp-agentic-guard removal; got {len(self.data['skills'])}",
        )

    def test_prompt_templates_is_last_entry(self):
        """The diff shows prompt-templates is now the last entry in the skills array
        (owasp-agentic-guard was the entry directly after it)."""
        last_skill = self.data["skills"][-1]
        self.assertEqual(
            last_skill["name"],
            "prompt-templates",
            f"prompt-templates must now be the last skill in the array; got: {last_skill['name']!r}",
        )

    def test_all_referenced_skill_files_exist(self):
        """Every file reference in skills.json must exist on disk after the removal."""
        for skill in self.data["skills"]:
            with self.subTest(skill=skill["name"]):
                fpath = os.path.join(REPO_ROOT, skill["file"])
                self.assertTrue(
                    os.path.isfile(fpath),
                    f"File for skill '{skill['name']}' not found: {skill['file']}",
                )

    def test_owasp_description_string_absent(self):
        """The OWASP description text must not appear in skills.json."""
        with open(SKILLS_JSON_PATH, encoding="utf-8") as fh:
            raw = fh.read()
        self.assertNotIn(
            "OWASP Top 10 for Agentic Applications",
            raw,
            "OWASP description must not appear in skills.json",
        )


if __name__ == "__main__":
    unittest.main()