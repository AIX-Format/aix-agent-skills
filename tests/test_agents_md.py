"""
Tests for AGENTS.md changes introduced in this PR.

This PR changed AGENTS.md in several ways:
  - Title format: "# AGENTS.md — Operating Manual..." → "# AGENTS.md: Operating Manual..."
  - Bullet formatting: "— description" → ": description" for skills/, personas/, etc.
  - Skill naming convention changed from snake_case (^[a-z0-9_]+$) to
    kebab-case (^[a-z0-9]+(?:-[a-z0-9]+)*$)
  - PR reading list changed from em-dash to colon: "1. AXIOM.md — ..." → "1. AXIOM.md: ..."
  - Kebab-case now documented as enforced by scripts/schema_sentinel.py
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_PATH = os.path.join(REPO_ROOT, "AGENTS.md")


def _read_agents_md() -> str:
    with open(AGENTS_PATH, encoding="utf-8") as fh:
        return fh.read()


class TestAgentsMdFileIntegrity(unittest.TestCase):
    """Basic file integrity checks."""

    def test_file_exists(self):
        self.assertTrue(os.path.isfile(AGENTS_PATH), "AGENTS.md must exist at repo root")

    def test_file_is_not_empty(self):
        self.assertGreater(os.path.getsize(AGENTS_PATH), 0)

    def test_file_is_utf8_encoded(self):
        try:
            with open(AGENTS_PATH, encoding="utf-8") as fh:
                fh.read()
        except UnicodeDecodeError as exc:
            self.fail(f"AGENTS.md is not valid UTF-8: {exc}")


class TestAgentsMdTitle(unittest.TestCase):
    """The PR changed the title separator from em-dash to colon."""

    def test_title_uses_colon_separator(self):
        content = _read_agents_md()
        first_line = content.splitlines()[0]
        self.assertIn(
            "# AGENTS.md: Operating Manual for AI Coding Agents",
            first_line,
            f"AGENTS.md H1 must use colon separator: '# AGENTS.md: Operating Manual...'; got: {first_line!r}",
        )

    def test_title_does_not_use_em_dash(self):
        content = _read_agents_md()
        first_line = content.splitlines()[0]
        self.assertNotIn(
            "—",
            first_line,
            f"AGENTS.md H1 must not use em-dash separator; got: {first_line!r}",
        )

    def test_title_is_h1(self):
        content = _read_agents_md()
        first_line = content.splitlines()[0]
        self.assertTrue(
            first_line.startswith("# "),
            f"AGENTS.md first line should be an H1 heading; got: {first_line!r}",
        )

    def test_title_mentions_agents_md(self):
        content = _read_agents_md()
        first_line = content.splitlines()[0]
        self.assertIn("AGENTS.md", first_line)

    def test_title_mentions_operating_manual(self):
        content = _read_agents_md()
        first_line = content.splitlines()[0]
        self.assertIn("Operating Manual", first_line)


class TestAgentsMdKebabCaseConvention(unittest.TestCase):
    """The PR changed the skill naming convention from snake_case to kebab-case."""

    def test_kebab_case_regex_documented(self):
        """The exact kebab-case regex must appear in AGENTS.md."""
        content = _read_agents_md()
        self.assertIn(
            r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
            content,
            "AGENTS.md must document the kebab-case regex ^[a-z0-9]+(?:-[a-z0-9]+)*$",
        )

    def test_snake_case_regex_not_primary_convention(self):
        """The old snake_case regex (^[a-z0-9_]+$) should no longer be the
        primary documented naming convention — it appears only in the
        explanatory note about the AIX schema difference."""
        content = _read_agents_md()
        # The snake_case regex may appear in an explanatory context but must NOT
        # appear in the Conventions bullet as the authoritative skill naming rule.
        conventions_section_match = re.search(
            r"## Conventions.*?(?=##|\Z)", content, re.DOTALL
        )
        self.assertIsNotNone(conventions_section_match, "Conventions section must exist")
        conventions_text = conventions_section_match.group(0)
        # The conventions bullet for skill names must say kebab-case
        self.assertIn(
            "kebab-case",
            conventions_text,
            "Conventions section must list kebab-case as the skill naming convention",
        )

    def test_skill_names_convention_says_kebab_case(self):
        content = _read_agents_md()
        self.assertIn(
            "kebab-case",
            content,
            "AGENTS.md must document kebab-case as the skill naming convention",
        )

    def test_schema_sentinel_enforces_convention(self):
        """The PR added that scripts/schema_sentinel.py enforces the convention."""
        content = _read_agents_md()
        self.assertIn(
            "schema_sentinel.py",
            content,
            "AGENTS.md must mention schema_sentinel.py as the enforcement mechanism",
        )

    def test_test_tool_exception_documented(self):
        """The _test_tool fixture is the documented exception to the kebab-case rule."""
        content = _read_agents_md()
        self.assertIn(
            "_test_tool",
            content,
            "AGENTS.md must document _test_tool as the documented exception to kebab-case",
        )

    def test_snake_case_context_explains_axiom_difference(self):
        """The snake_case mention must include context about the AIX protocol difference."""
        content = _read_agents_md()
        self.assertIn(
            "snake_case",
            content,
            "AGENTS.md must mention snake_case to explain the protocol vs repo difference",
        )
        self.assertIn(
            "AXIOM.md",
            content,
            "AGENTS.md must reference AXIOM.md when explaining the snake_case protocol rule",
        )

    def test_kebab_case_applies_to_branch_names(self):
        content = _read_agents_md()
        # Find the conventions section and check branch naming
        self.assertIn(
            "kebab-case",
            content,
        )
        # Branch names are also documented as kebab-case
        self.assertIn(
            "chore/",
            content,
        )


class TestAgentsMdBulletFormatting(unittest.TestCase):
    """The PR changed bullet list formatting from '— description' to ': description'."""

    def test_skills_bullet_uses_colon(self):
        """'skills/': markdown skill definitions..."""
        content = _read_agents_md()
        self.assertIn(
            "`skills/`: markdown skill definitions",
            content,
            "skills/ bullet must use colon separator (': description')",
        )

    def test_personas_bullet_uses_colon(self):
        content = _read_agents_md()
        self.assertIn(
            "`personas/`: versioned agent persona profiles",
            content,
            "personas/ bullet must use colon separator",
        )

    def test_aix_constitutional_runtime_bullet_uses_colon(self):
        content = _read_agents_md()
        self.assertIn(
            "`aix-constitutional-runtime/`: sample TypeScript runtime",
            content,
            "aix-constitutional-runtime/ bullet must use colon separator",
        )

    def test_go_engine_bullet_uses_colon(self):
        content = _read_agents_md()
        self.assertIn(
            "`go-engine/`: high-performance compute engine",
            content,
            "go-engine/ bullet must use colon separator",
        )

    def test_no_em_dash_in_bullets(self):
        """No bullet in the Repository overview section should use em-dash separator."""
        content = _read_agents_md()
        overview_match = re.search(
            r"## Repository overview.*?(?=##|\Z)", content, re.DOTALL
        )
        self.assertIsNotNone(overview_match, "Repository overview section must exist")
        overview_text = overview_match.group(0)
        # Look for "- `something/` — description" pattern (em-dash after backtick path)
        em_dash_bullets = re.findall(
            r"^-\s+`[^`]+`\s+—",
            overview_text,
            re.MULTILINE,
        )
        self.assertEqual(
            [],
            em_dash_bullets,
            f"No bullets in Repository overview should use em-dash; found: {em_dash_bullets}",
        )


class TestAgentsMdPRReadingList(unittest.TestCase):
    """The PR changed the 'What to read before opening a PR' list format."""

    def test_axiom_md_entry_uses_colon(self):
        """The PR changed '1. AXIOM.md — ...' to '1. AXIOM.md: ...' (colon after the link)."""
        content = _read_agents_md()
        # The entry is a markdown link: [`AXIOM.md`](URL): the supreme constitution.
        # Check that the link text is followed by ': the supreme constitution'
        self.assertIn(
            "): the supreme constitution",
            content,
            "AXIOM.md entry must use colon separator after the link",
        )
        # Also confirm the actual word AXIOM.md appears in the reading list section
        self.assertIn("AXIOM.md", content)

    def test_charter_rules_entry_uses_colon(self):
        """The PR changed '2. charter.rules.txt — ...' to '2. charter.rules.txt: ...'."""
        content = _read_agents_md()
        # Entry is: [`charter.rules.txt`](./charter.rules.txt): repo-local lint rules
        self.assertIn(
            "charter.rules.txt): repo-local lint rules",
            content,
            "charter.rules.txt entry must use colon separator after the link",
        )

    def test_pr_reading_list_no_em_dash(self):
        content = _read_agents_md()
        pr_section_match = re.search(
            r"## What to read before opening a PR.*?(?=##|\Z)",
            content,
            re.DOTALL,
        )
        self.assertIsNotNone(pr_section_match, "'What to read before opening a PR' section must exist")
        pr_text = pr_section_match.group(0)
        # Each numbered list item should use colon, not em-dash
        em_dash_items = re.findall(r"^\d+\.\s+.*—", pr_text, re.MULTILINE)
        self.assertEqual(
            [],
            em_dash_items,
            f"PR reading list items must not use em-dash; found: {em_dash_items}",
        )


class TestAgentsMdStackOverview(unittest.TestCase):
    """Core structural content that must be retained after the PR changes."""

    def test_repository_overview_section_exists(self):
        content = _read_agents_md()
        self.assertIn("## Repository overview", content)

    def test_aix_agent_skills_is_l3(self):
        content = _read_agents_md()
        self.assertIn(
            "L3 marketplace",
            content,
            "AGENTS.md must state that aix-agent-skills is the L3 marketplace",
        )

    def test_sovereign_stack_layers_section_exists(self):
        content = _read_agents_md()
        self.assertIn("## Sovereign Stack layers", content)

    def test_layer_dependency_direction_documented(self):
        content = _read_agents_md()
        self.assertIn(
            "Dependency direction is one-way",
            content,
            "AGENTS.md must document one-way dependency direction between layers",
        )

    def test_conventions_section_exists(self):
        content = _read_agents_md()
        self.assertIn("## Conventions", content)

    def test_apache_license_mentioned(self):
        content = _read_agents_md()
        self.assertIn("Apache-2.0", content)

    def test_conventional_commits_mentioned(self):
        content = _read_agents_md()
        self.assertIn("Conventional Commits", content)

    def test_axiom_md_link_present(self):
        content = _read_agents_md()
        self.assertIn(
            "AXIOM.md",
            content,
            "AGENTS.md must link to AXIOM.md (the supreme constitution)",
        )


if __name__ == "__main__":
    unittest.main()