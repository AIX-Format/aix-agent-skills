"""
Tests for README.md changes introduced in this PR.

This PR updated README.md with:
  - Asset references changed to v2 versions (aix-stack-header-v2.svg,
    aix-stack-diagram-v2.svg, aix-footer-quote-v2.svg)
  - New badges: AIX Stack Echo369, Spec AIX/1.0, Version v1.0.0, License Apache_2.0
  - Expanded ecosystem table (L0 root authority + L4-L6 satellite layers)
  - Simplified Architects section (1 human + 3 AI agents)
  - Colon formatting replacing em-dash in headings ("Quick Start: MCP Config")
  - Stack description updated to include root authority and satellites
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(REPO_ROOT, "README.md")
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")


def _read_readme() -> str:
    with open(README_PATH, encoding="utf-8") as fh:
        return fh.read()


class TestReadmeV2AssetReferences(unittest.TestCase):
    """README must now reference the v2 SVG assets added in this PR."""

    def test_header_v2_svg_referenced(self):
        content = _read_readme()
        self.assertIn(
            "aix-stack-header-v2.svg",
            content,
            "README.md must reference aix-stack-header-v2.svg (not the old v1)",
        )

    def test_diagram_v2_svg_referenced(self):
        content = _read_readme()
        self.assertIn(
            "aix-stack-diagram-v2.svg",
            content,
            "README.md must reference aix-stack-diagram-v2.svg (not the old v1)",
        )

    def test_footer_quote_v2_svg_referenced(self):
        content = _read_readme()
        self.assertIn(
            "aix-footer-quote-v2.svg",
            content,
            "README.md must reference aix-footer-quote-v2.svg (not the old v1)",
        )

    def test_old_header_svg_not_used(self):
        """The old aix-stack-header.svg (no version suffix) must not be the img src."""
        content = _read_readme()
        # Pattern: src="./assets/aix-stack-header.svg" — the non-v2 file
        old_ref = re.search(r'src="[^"]*assets/aix-stack-header\.svg"', content)
        self.assertIsNone(
            old_ref,
            "README.md img src should not point to the old aix-stack-header.svg; use the v2 version",
        )

    def test_old_diagram_svg_not_used(self):
        content = _read_readme()
        old_ref = re.search(r'src="[^"]*assets/aix-stack-diagram\.svg"', content)
        self.assertIsNone(
            old_ref,
            "README.md img src should not point to the old aix-stack-diagram.svg; use the v2 version",
        )

    def test_old_footer_quote_svg_not_used(self):
        content = _read_readme()
        old_ref = re.search(r'src="[^"]*assets/aix-footer-quote\.svg"', content)
        self.assertIsNone(
            old_ref,
            "README.md img src should not point to the old aix-footer-quote.svg; use the v2 version",
        )

    def test_v2_asset_files_exist_on_disk(self):
        for filename in [
            "aix-stack-header-v2.svg",
            "aix-stack-diagram-v2.svg",
            "aix-footer-quote-v2.svg",
        ]:
            with self.subTest(asset=filename):
                self.assertTrue(
                    os.path.isfile(os.path.join(ASSETS_DIR, filename)),
                    f"Asset file {filename} must exist in assets/ directory",
                )

    def test_header_v2_alt_text_mentions_echo369(self):
        """The updated img alt text for the header must mention Echo369."""
        content = _read_readme()
        # Find the <img> tag for the header
        match = re.search(r'<img[^>]*aix-stack-header-v2\.svg[^>]*>', content)
        self.assertIsNotNone(match, "Could not find img tag with aix-stack-header-v2.svg")
        self.assertIn("Echo369", match.group(0), "Header img alt text must mention Echo369")

    def test_diagram_v2_alt_text_mentions_echo369(self):
        content = _read_readme()
        match = re.search(r'<img[^>]*aix-stack-diagram-v2\.svg[^>]*>', content)
        self.assertIsNotNone(match, "Could not find img tag with aix-stack-diagram-v2.svg")
        self.assertIn("Echo369", match.group(0), "Diagram img alt text must mention Echo369")

    def test_footer_v2_alt_text_mentions_echo369(self):
        content = _read_readme()
        match = re.search(r'<img[^>]*aix-footer-quote-v2\.svg[^>]*>', content)
        self.assertIsNotNone(match, "Could not find img tag with aix-footer-quote-v2.svg")
        self.assertIn("Echo369", match.group(0), "Footer img alt text must mention Echo369")


class TestReadmeNewBadges(unittest.TestCase):
    """New badges added in this PR must be present."""

    def test_aix_stack_echo369_badge_present(self):
        content = _read_readme()
        self.assertIn(
            "Echo369",
            content,
            "README must contain an Echo369 badge or reference",
        )

    def test_spec_aix_1_0_badge_present(self):
        content = _read_readme()
        self.assertIn(
            "AIX%2F1.0",
            content,
            "README must contain an AIX/1.0 spec badge (URL-encoded as AIX%2F1.0)",
        )

    def test_version_v1_0_0_badge_present(self):
        content = _read_readme()
        self.assertIn(
            "v1.0.0",
            content,
            "README must reference version v1.0.0 in a badge",
        )

    def test_license_apache_2_0_badge_present(self):
        content = _read_readme()
        self.assertIn(
            "Apache_2.0",
            content,
            "README must contain an Apache_2.0 license badge",
        )

    def test_badges_link_to_axiom_md(self):
        content = _read_readme()
        self.assertIn(
            "AXIOM.md",
            content,
            "README must link to AXIOM.md from at least one badge",
        )

    def test_badge_label_color_is_neon_green(self):
        """Neon green (#39FF14) is the brand label color used across all new badges."""
        content = _read_readme()
        self.assertIn(
            "39FF14",
            content,
            "README badges must use the neon-green brand color 39FF14",
        )


class TestReadmeEcosystemLayers(unittest.TestCase):
    """The PR added L0 root authority and L4-L6 satellite layer entries."""

    def test_l0_root_authority_section_present(self):
        content = _read_readme()
        self.assertIn(
            "L0",
            content,
            "README must describe the L0 Root Authority layer",
        )

    def test_axiomid_project_mentioned(self):
        content = _read_readme()
        self.assertIn(
            "axiomid-project",
            content,
            "README must mention axiomid-project (L0 root authority repo)",
        )

    def test_l4_alphaaxiom_mentioned(self):
        content = _read_readme()
        self.assertIn(
            "AlphaAxiom",
            content,
            "README must mention AlphaAxiom (L4 satellite trading layer)",
        )

    def test_l5_piworker_os_mentioned(self):
        content = _read_readme()
        self.assertIn(
            "PiWorker-OS",
            content,
            "README must mention PiWorker-OS (L5 satellite Pi layer)",
        )

    def test_l6_gemclaw_mentioned(self):
        content = _read_readme()
        self.assertIn(
            "GemClaw",
            content,
            "README must mention GemClaw (L6 satellite voice layer)",
        )

    def test_extended_ecosystem_table_present(self):
        content = _read_readme()
        self.assertIn(
            "Extended Ecosystem",
            content,
            "README must have an 'Extended Ecosystem' section for L0 + L4-L6",
        )

    def test_sovereign_stack_core_table_present(self):
        content = _read_readme()
        self.assertIn(
            "Sovereign Stack",
            content,
            "README must retain the core Sovereign Stack (L1/L2/L3) table section",
        )

    def test_satellite_layers_labeled(self):
        content = _read_readme()
        self.assertIn(
            "satellite",
            content.lower(),
            "README must describe L4-L6 as satellite layers",
        )

    def test_x402_payment_flow_mentioned(self):
        """The PR added a note about satellites buying skills via x402."""
        content = _read_readme()
        self.assertIn(
            "x402",
            content,
            "README must mention x402 payment flow between satellites and L3",
        )

    def test_l0_axiomid_link_present(self):
        content = _read_readme()
        self.assertIn(
            "axiomid-project",
            content,
        )
        # Confirm it's a real link (href or markdown link)
        self.assertTrue(
            "github.com/Moeabdelaziz007/axiomid-project" in content,
            "README must link to the axiomid-project GitHub repo",
        )

    def test_all_seven_layers_mentioned(self):
        """L0 through L6 must each appear in the README."""
        content = _read_readme()
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            with self.subTest(layer=layer):
                self.assertIn(layer, content, f"README must mention {layer}")


class TestReadmeArchitectsSection(unittest.TestCase):
    """Architects section was simplified in this PR: 1 human + 3 AI agents."""

    def test_architects_section_still_exists(self):
        content = _read_readme()
        self.assertIn("Architects", content)

    def test_moe_abdelaziz_still_present(self):
        content = _read_readme()
        self.assertIn("Moe Abdelaziz", content)

    def test_jules_aix_agent_still_present(self):
        content = _read_readme()
        self.assertIn("Jules", content)

    def test_codesmith_present(self):
        content = _read_readme()
        self.assertIn("Codesmith", content)

    def test_coderabbit_present(self):
        content = _read_readme()
        self.assertIn("CodeRabbit", content)

    def test_four_team_members_in_table(self):
        """The new table has exactly 4 columns (1 human + 3 agents)."""
        content = _read_readme()
        # Each team member has a width="25%" td
        td_25_count = content.count('width="25%"')
        self.assertEqual(
            td_25_count,
            4,
            f"Architects table should have 4 members (width=25% each); found {td_25_count}",
        )

    def test_old_five_agent_roster_link_removed(self):
        """The PR removed the old '12-agent roster' link."""
        content = _read_readme()
        self.assertNotIn(
            "12-agent roster",
            content,
            "Old '12-agent roster' link should have been removed in this PR",
        )

    def test_description_says_one_human_three_agents(self):
        content = _read_readme()
        self.assertIn(
            "one human and three AI agents",
            content,
            "Architects intro must say 'one human and three AI agents'",
        )

    def test_human_label_present(self):
        content = _read_readme()
        self.assertIn("human", content)

    def test_ai_agent_label_present(self):
        content = _read_readme()
        self.assertIn("AI agent", content)


class TestReadmeFormattingChanges(unittest.TestCase):
    """This PR replaced em-dash (—) separators with colons in section headings."""

    def test_mcp_quick_start_uses_colon(self):
        content = _read_readme()
        self.assertIn(
            "Quick Start: MCP Config",
            content,
            "Heading must use colon: 'Quick Start: MCP Config' (not em-dash)",
        )

    def test_mcp_quick_start_no_em_dash(self):
        content = _read_readme()
        lines = [ln for ln in content.splitlines() if "Quick Start" in ln]
        for ln in lines:
            self.assertNotIn(
                "—",
                ln,
                f"Quick Start heading must not use em-dash; got: {ln!r}",
            )

    def test_stack_description_uses_colon(self):
        """'Welcome to the Agentic Marketplace for IQRA:' uses colon (not em-dash)."""
        content = _read_readme()
        self.assertIn(
            "for [IQRA]",
            content,
        )
        # Find the line and verify it uses colon, not em-dash
        for ln in content.splitlines():
            if "IQRA" in ln and "Agentic Marketplace" in ln:
                self.assertNotIn(
                    "—",
                    ln,
                    f"Stack intro line must not use em-dash separator; got: {ln!r}",
                )
                break

    def test_skill_registry_heading_uses_colon(self):
        content = _read_readme()
        self.assertIn(
            "Skill Registry:",
            content,
            "Skill Registry heading must use colon separator (not em-dash)",
        )


class TestReadmeNavigationLinks(unittest.TestCase):
    """The PR updated navigation links to include L0 and L4-L6."""

    def test_l1_nav_link_present(self):
        content = _read_readme()
        self.assertIn(
            "aix-format",
            content,
        )

    def test_l2_nav_link_present(self):
        content = _read_readme()
        self.assertIn(
            "iqra",
            content,
        )

    def test_you_are_here_marker_present(self):
        content = _read_readme()
        self.assertIn(
            "YOU ARE HERE",
            content,
            "README navigation must include a 'YOU ARE HERE' marker for L3",
        )

    def test_l0_root_authority_nav_link(self):
        content = _read_readme()
        self.assertIn(
            "Root Authority",
            content,
            "README must label L0 as 'Root Authority'",
        )

    def test_satellites_sub_nav_present(self):
        """The PR added a sub-nav line showing L4/L5/L6 satellite links."""
        content = _read_readme()
        self.assertIn(
            "L4",
            content,
        )
        self.assertIn(
            "L5",
            content,
        )
        self.assertIn(
            "L6",
            content,
        )


if __name__ == "__main__":
    unittest.main()