"""
Tests for README.md changes introduced in this PR.

This PR changed README.md in several ways:

1. Image src attributes no longer carry the "-v2" filename suffix:
     old: ./assets/aix-stack-header-v2.svg
     new: ./assets/aix-stack-header.svg

2. The "Extended Ecosystem" subsection (L0 root authority + L4/L5/L6 satellites)
   was removed entirely, including its satellite-layers table.

3. The "Sovereign Stack (the three core repos)" sub-heading was removed; the
   core stack table (L1/L2/L3) now appears directly under the section.

4. Several badges were removed: the "AIX STACK · Echo369" badge, the
   "SPEC · AIX/1.0" badge, the "version-v1.0.0" badge, and the LICENSE badge.

5. Footer and diagram image paths updated (no -v2 suffix).

6. "Quick Start: MCP Config" colon changed to em-dash.

These tests guard all five categories of changes against regression.
"""

import os
import re
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README_PATH = os.path.join(REPO_ROOT, "README.md")


def _read() -> str:
    with open(README_PATH, encoding="utf-8") as fh:
        return fh.read()


# ---------------------------------------------------------------------------
# Image path checks
# ---------------------------------------------------------------------------

class TestReadmeImagePaths(unittest.TestCase):
    """All image src attributes must reference the non-v2 asset filenames."""

    def test_header_image_src_no_v2_suffix(self):
        content = _read()
        self.assertNotIn(
            "aix-stack-header-v2.svg",
            content,
            "README must not reference the deleted aix-stack-header-v2.svg asset",
        )

    def test_header_image_uses_canonical_path(self):
        content = _read()
        self.assertIn(
            "aix-stack-header.svg",
            content,
            "README must reference aix-stack-header.svg (not the v2 variant)",
        )

    def test_diagram_image_src_no_v2_suffix(self):
        content = _read()
        self.assertNotIn(
            "aix-stack-diagram-v2.svg",
            content,
            "README must not reference the deleted aix-stack-diagram-v2.svg asset",
        )

    def test_diagram_image_uses_canonical_path(self):
        content = _read()
        self.assertIn(
            "aix-stack-diagram.svg",
            content,
            "README must reference aix-stack-diagram.svg (not the v2 variant)",
        )

    def test_footer_image_src_no_v2_suffix(self):
        content = _read()
        self.assertNotIn(
            "aix-footer-quote-v2.svg",
            content,
            "README must not reference the deleted aix-footer-quote-v2.svg asset",
        )

    def test_footer_image_uses_canonical_path(self):
        content = _read()
        self.assertIn(
            "aix-footer-quote.svg",
            content,
            "README must reference aix-footer-quote.svg (not the v2 variant)",
        )

    def test_no_svg_references_contain_v2_suffix(self):
        """Comprehensive check: no .svg reference in the document carries '-v2'."""
        content = _read()
        v2_refs = re.findall(r'["\']([^"\']*-v2\.svg)["\']', content)
        self.assertEqual(
            [],
            v2_refs,
            f"README must not reference any -v2 SVG files; found: {v2_refs}",
        )

    def test_mascot_svg_not_referenced(self):
        """axi-mascot.svg was deleted and must not be referenced in README."""
        content = _read()
        self.assertNotIn(
            "axi-mascot.svg",
            content,
            "README must not reference the deleted axi-mascot.svg",
        )


# ---------------------------------------------------------------------------
# Satellite / extended ecosystem removal
# ---------------------------------------------------------------------------

class TestReadmeExtendedEcosystemRemoved(unittest.TestCase):
    """The Extended Ecosystem table (L0/L4/L5/L6) was removed in this PR."""

    def test_extended_ecosystem_heading_absent(self):
        content = _read()
        self.assertNotIn(
            "Extended Ecosystem",
            content,
            "The 'Extended Ecosystem' subsection was removed and must not appear",
        )

    def test_alphaaxiom_not_in_stack_table(self):
        """AlphaAxiom was a satellite (L4) row; it must not appear in the stack table."""
        content = _read()
        # AlphaAxiom may appear in commit history or other prose; restrict to table rows
        table_rows = [
            ln for ln in content.splitlines()
            if ln.strip().startswith("|") and "AlphaAxiom" in ln
        ]
        self.assertEqual(
            [],
            table_rows,
            "AlphaAxiom (L4 satellite) must not appear in any table row",
        )

    def test_piworker_os_not_in_stack_table(self):
        content = _read()
        table_rows = [
            ln for ln in content.splitlines()
            if ln.strip().startswith("|") and "PiWorker" in ln
        ]
        self.assertEqual(
            [],
            table_rows,
            "PiWorker-OS (L5 satellite) must not appear in any table row",
        )

    def test_gemclaw_not_in_stack_table(self):
        content = _read()
        table_rows = [
            ln for ln in content.splitlines()
            if ln.strip().startswith("|") and "GemClaw" in ln
        ]
        self.assertEqual(
            [],
            table_rows,
            "GemClaw (L6 satellite) must not appear in any table row",
        )

    def test_axiomid_project_not_in_stack_table(self):
        """axiomid-project was the L0 root authority; its table row was removed."""
        content = _read()
        table_rows = [
            ln for ln in content.splitlines()
            if ln.strip().startswith("|") and "axiomid-project" in ln
        ]
        self.assertEqual(
            [],
            table_rows,
            "axiomid-project (L0 root authority) must not appear in any table row",
        )

    def test_core_stack_table_has_exactly_three_data_rows(self):
        """The surviving stack table should have exactly L1, L2, L3 data rows."""
        content = _read()
        # Locate the stack table: find the header row and count subsequent data rows
        lines = content.splitlines()
        in_table = False
        data_rows = []
        for ln in lines:
            stripped = ln.strip()
            if "|:---:" in stripped or ("|:---" in stripped and "Layer" in ln):
                # This is a separator row; mark that the next rows are data
                in_table = True
                continue
            if in_table:
                if not stripped.startswith("|"):
                    # Table ended
                    if data_rows:
                        break
                else:
                    # Skip pure separator rows (e.g. |---|---|)
                    if not re.match(r"^\|[-:\s|]+\|$", stripped):
                        data_rows.append(stripped)

        # We expect exactly 3 rows: L1, L2, L3
        self.assertEqual(
            3,
            len(data_rows),
            f"Stack table must have exactly 3 data rows (L1/L2/L3); found {len(data_rows)}: {data_rows}",
        )


# ---------------------------------------------------------------------------
# Badge changes
# ---------------------------------------------------------------------------

class TestReadmeBadgesRemovedAndRetained(unittest.TestCase):
    """Several badges were removed; the surviving ones must still be present."""

    def test_echo369_badge_removed(self):
        """The 'AIX STACK · Echo369' badge was removed."""
        content = _read()
        self.assertNotIn(
            "Echo369",
            content,
            "The Echo369 badge/reference was removed and must not appear in README",
        )

    def test_spec_aix_badge_removed(self):
        """The 'SPEC-AIX%2F1.0' shields badge was removed."""
        content = _read()
        self.assertNotIn(
            "SPEC-AIX",
            content,
            "The SPEC AIX/1.0 badge was removed and must not appear",
        )

    def test_version_badge_removed(self):
        """The 'version-v1.0.0' shields badge was removed."""
        content = _read()
        # The badge URL contained "version-v1.0.0"
        self.assertNotIn(
            "version-v1.0.0",
            content,
            "The version-v1.0.0 badge was removed and must not appear",
        )

    def test_license_badge_removed(self):
        """The 'LICENSE-Apache_2.0' badge was removed."""
        content = _read()
        self.assertNotIn(
            "LICENSE-Apache_2.0",
            content,
            "The LICENSE badge was removed and must not appear",
        )

    def test_layer_badge_still_present(self):
        """The L3 MARKETPLACE layer badge must still be present."""
        content = _read()
        self.assertIn(
            "LAYER-L3",
            content,
            "The L3 MARKETPLACE layer badge must remain",
        )

    def test_architecture_badge_still_present(self):
        content = _read()
        self.assertIn("ARCHITECTURE-7%20LAYERS", content)

    def test_stack_version_badge_present(self):
        """The replacement 'AIX STACK-v0.369.0' badge must be present."""
        content = _read()
        self.assertIn(
            "v0.369.0",
            content,
            "The replacement AIX STACK version badge (v0.369.0) must be present",
        )


# ---------------------------------------------------------------------------
# Section heading / subheading changes
# ---------------------------------------------------------------------------

class TestReadmeSectionHeadings(unittest.TestCase):
    """Structural heading changes introduced by this PR."""

    def test_sovereign_stack_three_repos_subheading_removed(self):
        """Old subheading '### Sovereign Stack (the three core repos)' was removed."""
        content = _read()
        self.assertNotIn(
            "Sovereign Stack (the three core repos)",
            content,
            "The 'Sovereign Stack (the three core repos)' subheading was removed",
        )

    def test_stack_section_still_present(self):
        """The parent THE STACK section must still be present."""
        content = _read()
        self.assertIn("THE STACK", content)

    def test_mcp_config_heading_uses_em_dash(self):
        """'Quick Start: MCP Config' was changed to 'Quick Start — MCP Config'."""
        content = _read()
        self.assertIn(
            "Quick Start — MCP Config",
            content,
            "The MCP config heading must use '—' (em-dash) not ':'",
        )

    def test_mcp_config_old_colon_heading_absent(self):
        content = _read()
        self.assertNotIn(
            "Quick Start: MCP Config",
            content,
            "Old colon form of the MCP Config heading must be replaced with em-dash",
        )


# ---------------------------------------------------------------------------
# Footer section
# ---------------------------------------------------------------------------

class TestReadmeFooter(unittest.TestCase):
    """The footer section was simplified (satellite sub-line removed)."""

    def test_footer_image_tag_present(self):
        content = _read()
        self.assertIn("aix-footer-quote.svg", content)

    def test_footer_satellite_subline_removed(self):
        """Old footer had a sub-line listing L0/L4/L5/L6 satellite links."""
        content = _read()
        # The satellite link that used to appear in the footer
        self.assertNotIn(
            "axiomid-project",
            content,
            "The footer satellite sub-line referencing axiomid-project was removed",
        )

    def test_footer_l3_marker_present(self):
        content = _read()
        self.assertIn("L3 · MARKETPLACE", content)


# ---------------------------------------------------------------------------
# Negative regression: content that existed before and still must exist
# ---------------------------------------------------------------------------

class TestReadmePreservedContent(unittest.TestCase):
    """Content that was NOT removed in this PR and must still be intact."""

    def test_agentic_marketplace_intro_present(self):
        content = _read()
        self.assertIn("Agentic Marketplace", content)

    def test_sovereign_stack_l3_description_present(self):
        content = _read()
        self.assertIn("L3", content)
        self.assertIn("aix-format", content)
        self.assertIn("iqra", content)

    def test_three_repos_one_project_note_present(self):
        content = _read()
        self.assertIn("one project in three layers", content)

    def test_l1_link_present(self):
        content = _read()
        self.assertIn("L1 · PROTOCOL", content)

    def test_l2_link_present(self):
        content = _read()
        self.assertIn("L2 · RUNTIME", content)

    def test_you_are_here_marker_present(self):
        content = _read()
        self.assertIn("YOU ARE HERE", content)


if __name__ == "__main__":
    unittest.main()