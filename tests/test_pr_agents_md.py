"""
Tests for AGENTS.md changes introduced in this PR.

This PR changed AGENTS.md in three ways:
1. Title separator changed from ":" to "—":
     old: "# AGENTS.md: Operating Manual for AI Coding Agents"
     new: "# AGENTS.md — Operating Manual for AI Coding Agents"
2. Directory listing bullets changed from ": description" to "— description"
   (e.g. "`skills/`: markdown…" → "`skills/` — markdown…").
3. Skill naming convention changed from kebab-case to snake_case:
     old: kebab-case (`^[a-z0-9]+(?:-[a-z0-9]+)*$`)
     new: snake_case (`^[a-z0-9_]+$`)

These tests verify all three changes and guard against regression.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_PATH = os.path.join(REPO_ROOT, "AGENTS.md")


def _read() -> str:
    with open(AGENTS_PATH, encoding="utf-8") as fh:
        return fh.read()


class TestAgentsMdBasic(unittest.TestCase):
    """File integrity checks."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(AGENTS_PATH), "AGENTS.md must exist at repo root")

    def test_file_is_not_empty(self):
        self.assertGreater(os.path.getsize(AGENTS_PATH), 0)

    def test_file_is_utf8(self):
        try:
            _read()
        except UnicodeDecodeError as exc:
            self.fail(f"AGENTS.md is not valid UTF-8: {exc}")


class TestAgentsMdTitle(unittest.TestCase):
    """The PR updated the H1 title separator from ':' to '—'."""

    def test_title_uses_em_dash_separator(self):
        """New title: '# AGENTS.md — Operating Manual for AI Coding Agents'"""
        content = _read()
        self.assertIn(
            "# AGENTS.md — Operating Manual",
            content,
            "AGENTS.md H1 must use '—' (em-dash) as separator",
        )

    def test_title_does_not_use_colon_separator(self):
        """Old title used ':' which must no longer appear as the title separator."""
        content = _read()
        first_h1 = next(
            (ln for ln in content.splitlines() if ln.startswith("# AGENTS.md")),
            None,
        )
        self.assertIsNotNone(first_h1, "AGENTS.md must have an H1 starting with '# AGENTS.md'")
        self.assertNotIn(
            "# AGENTS.md:",
            first_h1,
            "The old colon separator in the H1 must be replaced with '—'",
        )

    def test_title_mentions_operating_manual(self):
        content = _read()
        self.assertIn("Operating Manual", content)

    def test_title_mentions_ai_coding_agents(self):
        content = _read()
        self.assertIn("AI Coding Agents", content)


class TestAgentsMdDirectoryListFormat(unittest.TestCase):
    """The PR changed directory bullet separators from ':' to '—'."""

    def test_skills_entry_uses_em_dash(self):
        content = _read()
        self.assertIn(
            "`skills/` —",
            content,
            "The skills/ directory entry must use '—' as separator",
        )

    def test_personas_entry_uses_em_dash(self):
        content = _read()
        self.assertIn(
            "`personas/` —",
            content,
            "The personas/ directory entry must use '—' as separator",
        )

    def test_templates_entry_uses_em_dash(self):
        content = _read()
        self.assertIn(
            "`templates/` —",
            content,
            "The templates/ directory entry must use '—' as separator",
        )

    def test_rules_entry_uses_em_dash(self):
        content = _read()
        self.assertIn(
            "`rules/` —",
            content,
            "The rules/ directory entry must use '—' as separator",
        )

    def test_go_engine_entry_uses_em_dash(self):
        content = _read()
        self.assertIn(
            "`go-engine/` —",
            content,
            "The go-engine/ directory entry must use '—' as separator",
        )

    def test_directory_bullets_do_not_use_old_colon_format(self):
        """Old format was '`skills/`: markdown …'; verify that specific pattern is gone."""
        content = _read()
        # Pattern: backtick-wrapped path ending with slash, then `: `
        old_style = re.compile(r"`[a-z][^`]+/`:")
        matches = old_style.findall(content)
        self.assertEqual(
            [],
            matches,
            f"Old '`path/`: description' format must be replaced with '`path/` — description'; "
            f"found: {matches}",
        )

    def test_pre_pr_section_bullets_use_em_dash(self):
        """The 'What to read before opening a PR' section items also use '—'."""
        content = _read()
        # Check that AXIOM.md entry link is present in the numbered list
        self.assertIn("AXIOM.md`]", content)
        # Find lines in the numbered list and verify they use — not :
        lines = content.splitlines()
        axiom_lines = [ln for ln in lines if "AXIOM.md" in ln and ln.strip().startswith("1.")]
        self.assertTrue(len(axiom_lines) > 0, "Must have a numbered list item for AXIOM.md")
        for ln in axiom_lines:
            self.assertIn(
                " — ",
                ln,
                f"AXIOM.md list entry must use '—' separator; got: {ln!r}",
            )


class TestAgentsMdNamingConvention(unittest.TestCase):
    """The PR changed the stated skill naming convention from kebab-case to snake_case."""

    def test_skill_names_convention_mentions_snake_case(self):
        content = _read()
        self.assertIn(
            "snake_case",
            content,
            "AGENTS.md must state the snake_case naming convention",
        )

    def test_snake_case_regex_pattern_is_present(self):
        content = _read()
        self.assertIn(
            "^[a-z0-9_]+$",
            content,
            "The snake_case regex pattern '^[a-z0-9_]+$' must be present in AGENTS.md",
        )

    def test_old_kebab_case_regex_is_absent(self):
        """Old convention stated kebab-case pattern; it must no longer be in Conventions."""
        content = _read()
        # The specific old regex that enforced kebab-case for the Conventions bullet
        self.assertNotIn(
            "^[a-z0-9]+(?:-[a-z0-9]+)*$",
            content,
            "The old kebab-case regex '^[a-z0-9]+(?:-[a-z0-9]+)*$' must be removed "
            "from the Conventions section",
        )

    def test_conventions_section_exists(self):
        content = _read()
        self.assertIn("## Conventions", content)

    def test_skill_names_bullet_references_aix_schema(self):
        """New convention bullet references 'AIX schema' for authority."""
        content = _read()
        self.assertIn(
            "AIX schema",
            content,
            "The Conventions bullet for skill names must reference the AIX schema",
        )

    def test_branches_still_kebab_case(self):
        """Branch names remain kebab-case — verify this convention is still documented."""
        content = _read()
        self.assertIn("kebab-case", content, "Branch naming (kebab-case) must still be documented")

    def test_license_convention_is_apache(self):
        content = _read()
        self.assertIn("Apache-2.0", content)

    def test_conventional_commits_still_mentioned(self):
        content = _read()
        self.assertIn("Conventional Commits", content)


class TestAgentsMdStructure(unittest.TestCase):
    """High-level structural checks that must survive all edits."""

    def test_repository_overview_section_exists(self):
        content = _read()
        self.assertIn("## Repository overview", content)

    def test_sovereign_stack_layers_section_exists(self):
        content = _read()
        self.assertIn("Sovereign Stack layers", content)

    def test_axiom_md_link_present(self):
        content = _read()
        self.assertIn("AXIOM.md", content)

    def test_what_to_read_section_exists(self):
        content = _read()
        self.assertIn("What to read before opening a PR", content)

    def test_rules_skills_md_referenced(self):
        content = _read()
        self.assertIn("rules/skills.md", content)

    def test_charter_rules_referenced(self):
        content = _read()
        self.assertIn("charter.rules.txt", content)

    def test_skill_template_referenced(self):
        content = _read()
        self.assertIn("templates/skill-template.md", content)


if __name__ == "__main__":
    unittest.main()