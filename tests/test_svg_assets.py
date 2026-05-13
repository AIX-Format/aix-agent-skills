"""
Tests for new SVG asset files added in this PR.

Four SVG files were added:
  - assets/aix-footer-quote-v2.svg  (900×240)
  - assets/aix-stack-diagram-v2.svg (1100×560)
  - assets/aix-stack-header-v2.svg  (1100×340)
  - assets/axi-mascot.svg           (200×220)

Tests verify:
  - Files exist on disk
  - Files are well-formed XML/SVG
  - Correct SVG dimensions (width/height/viewBox)
  - Required SVG namespace
  - Content presence (text labels, elements, brand identifiers)
  - Accessibility attributes (for axi-mascot.svg)
  - Brand palette consistency (#39FF14 neon green)
  - Animation elements present where expected
"""

import os
import unittest
import xml.etree.ElementTree as ET

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

SVG_NS = "http://www.w3.org/2000/svg"

# Paths to the four new SVG files
FOOTER_QUOTE_V2 = os.path.join(ASSETS_DIR, "aix-footer-quote-v2.svg")
STACK_DIAGRAM_V2 = os.path.join(ASSETS_DIR, "aix-stack-diagram-v2.svg")
STACK_HEADER_V2 = os.path.join(ASSETS_DIR, "aix-stack-header-v2.svg")
AXI_MASCOT = os.path.join(ASSETS_DIR, "axi-mascot.svg")


def _parse_svg(path: str) -> ET.Element:
    """Parse an SVG file and return its root element."""
    tree = ET.parse(path)
    return tree.getroot()


def _svg_text_content(root: ET.Element) -> str:
    """Return all text content inside the SVG as a single concatenated string."""
    return " ".join(
        (elem.text or "") + (elem.tail or "")
        for elem in root.iter()
    )


class TestSvgFilesExist(unittest.TestCase):
    """All four new SVG files must exist in assets/."""

    def test_footer_quote_v2_exists(self):
        self.assertTrue(
            os.path.isfile(FOOTER_QUOTE_V2),
            "assets/aix-footer-quote-v2.svg must exist",
        )

    def test_stack_diagram_v2_exists(self):
        self.assertTrue(
            os.path.isfile(STACK_DIAGRAM_V2),
            "assets/aix-stack-diagram-v2.svg must exist",
        )

    def test_stack_header_v2_exists(self):
        self.assertTrue(
            os.path.isfile(STACK_HEADER_V2),
            "assets/aix-stack-header-v2.svg must exist",
        )

    def test_axi_mascot_exists(self):
        self.assertTrue(
            os.path.isfile(AXI_MASCOT),
            "assets/axi-mascot.svg must exist",
        )

    def test_all_svg_files_are_non_empty(self):
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2, AXI_MASCOT]:
            with self.subTest(file=os.path.basename(path)):
                self.assertGreater(
                    os.path.getsize(path),
                    0,
                    f"{os.path.basename(path)} must not be empty",
                )


class TestSvgWellFormedness(unittest.TestCase):
    """All four SVG files must be valid, parseable XML."""

    def _assert_parseable(self, path: str):
        try:
            _parse_svg(path)
        except ET.ParseError as exc:
            self.fail(f"{os.path.basename(path)} is not valid XML: {exc}")

    def test_footer_quote_v2_is_valid_xml(self):
        self._assert_parseable(FOOTER_QUOTE_V2)

    def test_stack_diagram_v2_is_valid_xml(self):
        self._assert_parseable(STACK_DIAGRAM_V2)

    def test_stack_header_v2_is_valid_xml(self):
        self._assert_parseable(STACK_HEADER_V2)

    def test_axi_mascot_is_valid_xml(self):
        self._assert_parseable(AXI_MASCOT)

    def _assert_root_is_svg(self, path: str):
        root = _parse_svg(path)
        # ElementTree parses namespaced tags as {ns}tag
        self.assertIn(
            "svg",
            root.tag.lower(),
            f"{os.path.basename(path)} root element must be <svg>",
        )

    def test_footer_quote_v2_root_is_svg(self):
        self._assert_root_is_svg(FOOTER_QUOTE_V2)

    def test_stack_diagram_v2_root_is_svg(self):
        self._assert_root_is_svg(STACK_DIAGRAM_V2)

    def test_stack_header_v2_root_is_svg(self):
        self._assert_root_is_svg(STACK_HEADER_V2)

    def test_axi_mascot_root_is_svg(self):
        self._assert_root_is_svg(AXI_MASCOT)


class TestSvgNamespace(unittest.TestCase):
    """All SVG files must declare the SVG namespace."""

    def _assert_has_svg_namespace(self, path: str):
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn(
            "http://www.w3.org/2000/svg",
            content,
            f"{os.path.basename(path)} must declare the SVG namespace",
        )

    def test_footer_quote_v2_has_svg_namespace(self):
        self._assert_has_svg_namespace(FOOTER_QUOTE_V2)

    def test_stack_diagram_v2_has_svg_namespace(self):
        self._assert_has_svg_namespace(STACK_DIAGRAM_V2)

    def test_stack_header_v2_has_svg_namespace(self):
        self._assert_has_svg_namespace(STACK_HEADER_V2)

    def test_axi_mascot_has_svg_namespace(self):
        self._assert_has_svg_namespace(AXI_MASCOT)


class TestFooterQuoteV2Dimensions(unittest.TestCase):
    """aix-footer-quote-v2.svg must have exact 900×240 dimensions."""

    def setUp(self):
        self.root = _parse_svg(FOOTER_QUOTE_V2)

    def test_width_is_900(self):
        self.assertEqual(
            self.root.get("width"),
            "900",
            "aix-footer-quote-v2.svg width must be 900",
        )

    def test_height_is_240(self):
        self.assertEqual(
            self.root.get("height"),
            "240",
            "aix-footer-quote-v2.svg height must be 240",
        )

    def test_viewbox_matches_dimensions(self):
        viewbox = self.root.get("viewBox")
        self.assertEqual(
            viewbox,
            "0 0 900 240",
            "aix-footer-quote-v2.svg viewBox must be '0 0 900 240'",
        )


class TestFooterQuoteV2Content(unittest.TestCase):
    """aix-footer-quote-v2.svg must contain the right brand text and elements."""

    def setUp(self):
        with open(FOOTER_QUOTE_V2, encoding="utf-8") as fh:
            self.raw = fh.read()
        self.root = _parse_svg(FOOTER_QUOTE_V2)

    def test_echo369_text_present(self):
        self.assertIn(
            "ECHO369",
            self.raw,
            "aix-footer-quote-v2.svg must contain ECHO369 text",
        )

    def test_king_quote_present(self):
        self.assertIn(
            "King isn't Born",
            self.raw,
            "aix-footer-quote-v2.svg must contain the canonical quote 'King isn't Born, he is Made.'",
        )

    def test_spec_aix_1_0_present(self):
        self.assertIn(
            "AIX/1.0",
            self.raw,
            "aix-footer-quote-v2.svg must include 'SPEC AIX/1.0'",
        )

    def test_neon_green_color_used(self):
        self.assertIn(
            "#39FF14",
            self.raw,
            "aix-footer-quote-v2.svg must use the brand neon-green color #39FF14",
        )

    def test_all_stack_layers_listed(self):
        """Footer must list L0–L3 core layers and satellite repos."""
        for token in ["L0", "L1", "L2", "L3"]:
            with self.subTest(token=token):
                self.assertIn(token, self.raw, f"Footer must mention {token}")

    def test_satellite_repos_listed(self):
        for repo in ["alphaaxiom", "piworker-os", "gemclaw"]:
            with self.subTest(repo=repo):
                self.assertIn(
                    repo,
                    self.raw.lower(),
                    f"Footer SVG must list satellite repo '{repo}'",
                )

    def test_animated_pulse_circle_present(self):
        """Footer SVG has a pulsing circle animation element."""
        animate_elements = list(self.root.iter("{http://www.w3.org/2000/svg}animate"))
        # May also appear without namespace if ElementTree strips it
        if not animate_elements:
            animate_elements = list(self.root.iter("animate"))
        self.assertGreater(
            len(animate_elements),
            0,
            "aix-footer-quote-v2.svg must contain an <animate> element (pulsing circle)",
        )

    def test_gradient_defined(self):
        self.assertIn(
            "linearGradient",
            self.raw,
            "aix-footer-quote-v2.svg must define a linearGradient",
        )

    def test_end_of_transmission_marker(self):
        self.assertIn(
            "END_OF_TRANSMISSION",
            self.raw,
            "Footer SVG must include END_OF_TRANSMISSION marker",
        )


class TestStackDiagramV2Dimensions(unittest.TestCase):
    """aix-stack-diagram-v2.svg must have exact 1100×560 dimensions."""

    def setUp(self):
        self.root = _parse_svg(STACK_DIAGRAM_V2)

    def test_width_is_1100(self):
        self.assertEqual(
            self.root.get("width"),
            "1100",
            "aix-stack-diagram-v2.svg width must be 1100",
        )

    def test_height_is_560(self):
        self.assertEqual(
            self.root.get("height"),
            "560",
            "aix-stack-diagram-v2.svg height must be 560",
        )

    def test_viewbox_matches_dimensions(self):
        self.assertEqual(
            self.root.get("viewBox"),
            "0 0 1100 560",
            "aix-stack-diagram-v2.svg viewBox must be '0 0 1100 560'",
        )


class TestStackDiagramV2Content(unittest.TestCase):
    """aix-stack-diagram-v2.svg must describe the full 7-layer topology."""

    def setUp(self):
        with open(STACK_DIAGRAM_V2, encoding="utf-8") as fh:
            self.raw = fh.read()

    def test_echo369_codename_present(self):
        self.assertIn("ECHO369", self.raw)

    def test_l0_root_authority_present(self):
        self.assertIn("ROOT AUTHORITY", self.raw, "Diagram must label the L0 root authority")

    def test_axiomid_project_labeled(self):
        self.assertIn("AXIOMID-PROJECT", self.raw)

    def test_l1_protocol_labeled(self):
        self.assertIn("L1", self.raw)
        self.assertIn("PROTOCOL", self.raw)

    def test_aix_format_labeled(self):
        self.assertIn("AIX-FORMAT", self.raw)

    def test_l2_runtime_labeled(self):
        self.assertIn("L2", self.raw)
        self.assertIn("RUNTIME", self.raw)

    def test_iqra_labeled(self):
        self.assertIn("IQRA", self.raw)

    def test_l3_marketplace_labeled(self):
        self.assertIn("L3", self.raw)
        self.assertIn("MARKETPLACE", self.raw)

    def test_agent_skills_labeled(self):
        self.assertIn("AGENT-SKILLS", self.raw)

    def test_l4_satellite_trading_present(self):
        self.assertIn("L4", self.raw)
        self.assertIn("ALPHAAXIOM", self.raw)

    def test_l5_satellite_pi_present(self):
        self.assertIn("L5", self.raw)
        self.assertIn("PIWORKER-OS", self.raw)

    def test_l6_satellite_voice_present(self):
        self.assertIn("L6", self.raw)
        self.assertIn("GEMCLAW", self.raw)

    def test_money_flow_annotation_present(self):
        """Diagram must annotate satellite→L3 money flow (x402 / USDC / Pi)."""
        self.assertIn(
            "x402",
            self.raw,
            "Diagram must annotate the x402 payment flow from satellites to L3",
        )

    def test_identity_flow_annotation_present(self):
        self.assertIn(
            "identity",
            self.raw.lower(),
            "Diagram must annotate the identity flow from L0 down to all layers",
        )

    def test_neon_green_color_used(self):
        self.assertIn("#39FF14", self.raw)

    def test_gold_color_for_l0(self):
        """L0 root authority uses gold (#FFD700) to distinguish it from sovereign core."""
        self.assertIn(
            "#FFD700",
            self.raw,
            "L0 root authority box must use gold color #FFD700",
        )

    def test_topological_invariants_present(self):
        self.assertIn(
            "TOPOLOGICAL INVARIANTS",
            self.raw,
            "Diagram must include topological invariants legend",
        )

    def test_spec_aix_1_0_present(self):
        self.assertIn("AIX/1.0", self.raw)

    def test_filter_glow_defined(self):
        """Diagram defines glow filters for sovereign core elements."""
        self.assertIn("feGaussianBlur", self.raw)


class TestStackHeaderV2Dimensions(unittest.TestCase):
    """aix-stack-header-v2.svg must have exact 1100×340 dimensions."""

    def setUp(self):
        self.root = _parse_svg(STACK_HEADER_V2)

    def test_width_is_1100(self):
        self.assertEqual(
            self.root.get("width"),
            "1100",
            "aix-stack-header-v2.svg width must be 1100",
        )

    def test_height_is_340(self):
        self.assertEqual(
            self.root.get("height"),
            "340",
            "aix-stack-header-v2.svg height must be 340",
        )

    def test_viewbox_matches_dimensions(self):
        self.assertEqual(
            self.root.get("viewBox"),
            "0 0 1100 340",
            "aix-stack-header-v2.svg viewBox must be '0 0 1100 340'",
        )


class TestStackHeaderV2Content(unittest.TestCase):
    """aix-stack-header-v2.svg must present the complete stack branding."""

    def setUp(self):
        with open(STACK_HEADER_V2, encoding="utf-8") as fh:
            self.raw = fh.read()

    def test_echo369_codename_present(self):
        self.assertIn("ECHO369", self.raw)

    def test_spec_aix_1_0_present(self):
        self.assertIn("AIX/1.0", self.raw)

    def test_l0_root_authority_labeled(self):
        self.assertIn("ROOT AUTHORITY", self.raw)
        self.assertIn("L0", self.raw)

    def test_axiomid_project_present(self):
        self.assertIn("AXIOMID-PROJECT", self.raw)

    def test_l1_aix_format_present(self):
        self.assertIn("AIX-FORMAT", self.raw)

    def test_l2_iqra_present(self):
        self.assertIn("IQRA", self.raw)

    def test_l3_marketplace_present(self):
        self.assertIn("AGENT-SKILLS", self.raw)

    def test_l4_alphaaxiom_present(self):
        self.assertIn("ALPHAAXIOM", self.raw)

    def test_l5_piworker_os_present(self):
        self.assertIn("PIWORKER-OS", self.raw)

    def test_l6_gemclaw_present(self):
        self.assertIn("GEMCLAW", self.raw)

    def test_live_pulse_animation_present(self):
        """Header SVG has a 'LIVE' animated pulse indicator."""
        self.assertIn(
            "LIVE",
            self.raw,
            "Header SVG must have a LIVE label for the pulse animation",
        )
        self.assertIn(
            "<animate",
            self.raw,
            "Header SVG must contain an <animate> element for the live pulse",
        )

    def test_neon_green_brand_color(self):
        self.assertIn("#39FF14", self.raw)

    def test_gold_color_for_l0(self):
        self.assertIn("#FFD700", self.raw)

    def test_gradient_defined(self):
        self.assertIn("linearGradient", self.raw)

    def test_glow_filter_defined(self):
        self.assertIn("feGaussianBlur", self.raw)

    def test_money_flow_annotation_present(self):
        """Header must annotate the M2M money flow from satellites up to L3."""
        self.assertIn(
            "M2M",
            self.raw,
            "Header SVG must annotate M2M money flow from satellite layers",
        )

    def test_satellite_section_visually_dimmed(self):
        """Satellite layers use #666666 stroke to visually distinguish from core."""
        self.assertIn(
            "#666666",
            self.raw,
            "Satellite layer boxes must use #666666 (dim) stroke color",
        )


class TestAxiMascotDimensions(unittest.TestCase):
    """axi-mascot.svg must have exact 200×220 dimensions."""

    def setUp(self):
        self.root = _parse_svg(AXI_MASCOT)

    def test_width_is_200(self):
        self.assertEqual(
            self.root.get("width"),
            "200",
            "axi-mascot.svg width must be 200",
        )

    def test_height_is_220(self):
        self.assertEqual(
            self.root.get("height"),
            "220",
            "axi-mascot.svg height must be 220",
        )

    def test_viewbox_matches_dimensions(self):
        self.assertEqual(
            self.root.get("viewBox"),
            "0 0 200 220",
            "axi-mascot.svg viewBox must be '0 0 200 220'",
        )


class TestAxiMascotAccessibility(unittest.TestCase):
    """axi-mascot.svg has accessibility attributes required for SVG images."""

    def setUp(self):
        self.root = _parse_svg(AXI_MASCOT)
        with open(AXI_MASCOT, encoding="utf-8") as fh:
            self.raw = fh.read()

    def test_role_img_attribute_present(self):
        self.assertEqual(
            self.root.get("role"),
            "img",
            "axi-mascot.svg must have role='img' for accessibility",
        )

    def test_aria_label_present(self):
        aria_label = self.root.get("aria-label")
        self.assertIsNotNone(
            aria_label,
            "axi-mascot.svg must have an aria-label attribute",
        )
        self.assertGreater(
            len(aria_label),
            0,
            "axi-mascot.svg aria-label must not be empty",
        )

    def test_aria_label_mentions_axi_mascot(self):
        aria_label = self.root.get("aria-label") or ""
        self.assertIn(
            "AXI Mascot",
            aria_label,
            "aria-label must mention 'AXI Mascot'",
        )

    def test_aria_label_mentions_l0(self):
        aria_label = self.root.get("aria-label") or ""
        self.assertIn(
            "L0",
            aria_label,
            "aria-label must mention L0 (AxiomID root authority)",
        )

    def test_title_element_present(self):
        """SVG <title> element is used by screen readers."""
        ns_title = "{http://www.w3.org/2000/svg}title"
        titles = list(self.root.iter(ns_title))
        if not titles:
            titles = list(self.root.iter("title"))
        self.assertGreater(
            len(titles),
            0,
            "axi-mascot.svg must have a <title> element for screen reader support",
        )

    def test_title_text_content(self):
        self.assertIn(
            "AXI Mascot",
            self.raw,
            "<title> text must mention 'AXI Mascot'",
        )

    def test_desc_element_present(self):
        """SVG <desc> element provides extended description for assistive technology."""
        ns_desc = "{http://www.w3.org/2000/svg}desc"
        descs = list(self.root.iter(ns_desc))
        if not descs:
            descs = list(self.root.iter("desc"))
        self.assertGreater(
            len(descs),
            0,
            "axi-mascot.svg must have a <desc> element",
        )

    def test_desc_mentions_axiomid(self):
        self.assertIn(
            "axiomid-project",
            self.raw,
            "<desc> must mention the axiomid-project source",
        )


class TestAxiMascotVisualElements(unittest.TestCase):
    """axi-mascot.svg must contain the expected visual elements."""

    def setUp(self):
        with open(AXI_MASCOT, encoding="utf-8") as fh:
            self.raw = fh.read()
        self.root = _parse_svg(AXI_MASCOT)

    def test_neon_green_palette_used(self):
        self.assertIn(
            "#00ff41",
            self.raw,
            "Mascot must use the native neon-green palette #00ff41",
        )

    def test_cyan_accent_color_used(self):
        self.assertIn(
            "#00d4ff",
            self.raw,
            "Mascot must use the cyan accent color #00d4ff",
        )

    def test_body_gradient_defined(self):
        self.assertIn("linearGradient", self.raw)

    def test_glow_gradient_defined(self):
        self.assertIn("radialGradient", self.raw)

    def test_body_ellipse_present(self):
        """The mascot body is drawn as an ellipse."""
        ns_ellipse = "{http://www.w3.org/2000/svg}ellipse"
        ellipses = list(self.root.iter(ns_ellipse))
        if not ellipses:
            ellipses = list(self.root.iter("ellipse"))
        self.assertGreater(
            len(ellipses),
            0,
            "Mascot SVG must contain ellipse elements for the body",
        )

    def test_eyes_present(self):
        """Mascot has two eye ellipses at documented cx positions (78 and 122)."""
        ns_ellipse = "{http://www.w3.org/2000/svg}ellipse"
        ellipses = list(self.root.iter(ns_ellipse))
        if not ellipses:
            ellipses = list(self.root.iter("ellipse"))
        cx_values = {e.get("cx") for e in ellipses}
        self.assertIn("78", cx_values, "Left eye ellipse must have cx='78'")
        self.assertIn("122", cx_values, "Right eye ellipse must have cx='122'")

    def test_smile_path_present(self):
        """Mascot has a smile rendered as an SVG path."""
        ns_path = "{http://www.w3.org/2000/svg}path"
        paths = list(self.root.iter(ns_path))
        if not paths:
            paths = list(self.root.iter("path"))
        self.assertGreater(
            len(paths),
            0,
            "Mascot SVG must contain a path element (smile)",
        )

    def test_smile_uses_quadratic_bezier(self):
        """The smile is a quadratic Bézier curve (Q command in path data)."""
        self.assertIn(
            " Q",
            self.raw,
            "Mascot smile path must use a quadratic Bézier curve (Q command)",
        )

    def test_defs_block_present(self):
        self.assertIn("<defs>", self.raw)

    def test_axi_body_grad_id_present(self):
        self.assertIn(
            'id="axiBodyGrad"',
            self.raw,
            "Mascot must define the 'axiBodyGrad' gradient id",
        )

    def test_axi_body_fill_id_present(self):
        self.assertIn(
            'id="axiBodyFill"',
            self.raw,
            "Mascot must define the 'axiBodyFill' radial gradient id",
        )

    def test_axi_glow_id_present(self):
        self.assertIn(
            'id="axiGlow"',
            self.raw,
            "Mascot must define the 'axiGlow' radial gradient id",
        )


class TestSvgBrandConsistency(unittest.TestCase):
    """Cross-file brand consistency: all three v2 banner SVGs share the same palette."""

    def test_all_v2_banners_use_neon_green(self):
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2]:
            with self.subTest(file=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn(
                    "#39FF14",
                    content,
                    f"{os.path.basename(path)} must use brand neon-green #39FF14",
                )

    def test_all_v2_banners_use_dark_background(self):
        """All v2 banners use a very dark (#050505 or similar) background."""
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2]:
            with self.subTest(file=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn(
                    "#050505",
                    content,
                    f"{os.path.basename(path)} must use the dark background color #050505",
                )

    def test_all_v2_banners_reference_echo369(self):
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2]:
            with self.subTest(file=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn(
                    "ECHO369",
                    content,
                    f"{os.path.basename(path)} must reference the Echo369 codename",
                )

    def test_all_v2_banners_reference_spec(self):
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2]:
            with self.subTest(file=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn(
                    "AIX/1.0",
                    content,
                    f"{os.path.basename(path)} must reference the AIX/1.0 spec",
                )

    def test_all_v2_banners_use_consolas_font(self):
        """Brand font is Consolas (monospace)."""
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2]:
            with self.subTest(file=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn(
                    "Consolas",
                    content,
                    f"{os.path.basename(path)} must use Consolas as the brand monospace font",
                )

    def test_all_v2_banners_have_rounded_corners(self):
        """All banner SVGs use rx=12 rounded corners on their background rect."""
        for path in [FOOTER_QUOTE_V2, STACK_DIAGRAM_V2, STACK_HEADER_V2]:
            with self.subTest(file=os.path.basename(path)):
                with open(path, encoding="utf-8") as fh:
                    content = fh.read()
                self.assertIn(
                    'rx="12"',
                    content,
                    f"{os.path.basename(path)} must use rx='12' rounded corners",
                )


if __name__ == "__main__":
    unittest.main()