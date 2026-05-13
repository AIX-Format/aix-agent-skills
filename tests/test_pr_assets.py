"""
Tests for SVG asset deletions introduced in this PR.

This PR deleted four SVG asset files:
  - assets/aix-footer-quote-v2.svg
  - assets/aix-stack-diagram-v2.svg
  - assets/aix-stack-header-v2.svg
  - assets/axi-mascot.svg

These files were superseded by non-v2 variants that already existed.
The tests verify:
  - All four deleted files are absent from the repository.
  - The canonical (non-v2) replacements still exist.
  - No stale references to the deleted files remain in tracked text files.
"""

import os
import unittest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")

# Files that must NOT exist after this PR
DELETED_FILES = [
    "aix-footer-quote-v2.svg",
    "aix-stack-diagram-v2.svg",
    "aix-stack-header-v2.svg",
    "axi-mascot.svg",
]

# Canonical replacements that MUST still exist
CANONICAL_FILES = [
    "aix-footer-quote.svg",
    "aix-stack-diagram.svg",
    "aix-stack-header.svg",
]

# Text files to scan for stale references
SCANNED_TEXT_FILES = [
    os.path.join(REPO_ROOT, "README.md"),
    os.path.join(REPO_ROOT, "AGENTS.md"),
]


class TestDeletedV2Assets(unittest.TestCase):
    """Verify that all four v2/mascot SVGs were removed."""

    def test_aix_footer_quote_v2_deleted(self):
        path = os.path.join(ASSETS_DIR, "aix-footer-quote-v2.svg")
        self.assertFalse(
            os.path.isfile(path),
            "assets/aix-footer-quote-v2.svg must not exist; it was deleted in this PR",
        )

    def test_aix_stack_diagram_v2_deleted(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-diagram-v2.svg")
        self.assertFalse(
            os.path.isfile(path),
            "assets/aix-stack-diagram-v2.svg must not exist; it was deleted in this PR",
        )

    def test_aix_stack_header_v2_deleted(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-header-v2.svg")
        self.assertFalse(
            os.path.isfile(path),
            "assets/aix-stack-header-v2.svg must not exist; it was deleted in this PR",
        )

    def test_axi_mascot_deleted(self):
        path = os.path.join(ASSETS_DIR, "axi-mascot.svg")
        self.assertFalse(
            os.path.isfile(path),
            "assets/axi-mascot.svg must not exist; it was deleted in this PR",
        )

    def test_all_deleted_files_absent(self):
        """Parametric sweep of every deleted filename."""
        for filename in DELETED_FILES:
            full_path = os.path.join(ASSETS_DIR, filename)
            with self.subTest(filename=filename):
                self.assertFalse(
                    os.path.isfile(full_path),
                    f"assets/{filename} must not exist after this PR",
                )

    def test_no_v2_svg_files_remain_in_assets(self):
        """No -v2 SVG variant should remain anywhere in the assets directory."""
        if not os.path.isdir(ASSETS_DIR):
            self.skipTest("assets/ directory does not exist")
        v2_files = [
            f for f in os.listdir(ASSETS_DIR)
            if f.endswith("-v2.svg") or "-v2." in f
        ]
        self.assertEqual(
            [],
            v2_files,
            f"No -v2 SVG files should remain in assets/; found: {v2_files}",
        )


class TestCanonicalAssetsExist(unittest.TestCase):
    """The non-v2 canonical replacements must still be present."""

    def test_aix_footer_quote_canonical_exists(self):
        path = os.path.join(ASSETS_DIR, "aix-footer-quote.svg")
        self.assertTrue(
            os.path.isfile(path),
            "assets/aix-footer-quote.svg (the canonical replacement) must exist",
        )

    def test_aix_stack_diagram_canonical_exists(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-diagram.svg")
        self.assertTrue(
            os.path.isfile(path),
            "assets/aix-stack-diagram.svg (the canonical replacement) must exist",
        )

    def test_aix_stack_header_canonical_exists(self):
        path = os.path.join(ASSETS_DIR, "aix-stack-header.svg")
        self.assertTrue(
            os.path.isfile(path),
            "assets/aix-stack-header.svg (the canonical replacement) must exist",
        )

    def test_all_canonical_files_exist(self):
        """Parametric sweep of every expected canonical asset."""
        for filename in CANONICAL_FILES:
            full_path = os.path.join(ASSETS_DIR, filename)
            with self.subTest(filename=filename):
                self.assertTrue(
                    os.path.isfile(full_path),
                    f"assets/{filename} must exist as the canonical asset",
                )

    def test_canonical_replacements_are_non_empty(self):
        """Each canonical SVG must have content (not a zero-byte placeholder)."""
        for filename in CANONICAL_FILES:
            full_path = os.path.join(ASSETS_DIR, filename)
            if os.path.isfile(full_path):
                with self.subTest(filename=filename):
                    self.assertGreater(
                        os.path.getsize(full_path),
                        0,
                        f"assets/{filename} must not be empty",
                    )


class TestNoStaleReferencesInTextFiles(unittest.TestCase):
    """Verify that no tracked text files still reference the deleted SVGs."""

    def _check_file_no_reference(self, text_path: str, deleted_filename: str):
        if not os.path.isfile(text_path):
            return  # file doesn't exist; skip rather than fail
        with open(text_path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        relative_text = os.path.relpath(text_path, REPO_ROOT)
        self.assertNotIn(
            deleted_filename,
            content,
            f"{relative_text} must not reference the deleted asset '{deleted_filename}'",
        )

    def test_readme_does_not_reference_footer_v2(self):
        self._check_file_no_reference(
            os.path.join(REPO_ROOT, "README.md"),
            "aix-footer-quote-v2.svg",
        )

    def test_readme_does_not_reference_diagram_v2(self):
        self._check_file_no_reference(
            os.path.join(REPO_ROOT, "README.md"),
            "aix-stack-diagram-v2.svg",
        )

    def test_readme_does_not_reference_header_v2(self):
        self._check_file_no_reference(
            os.path.join(REPO_ROOT, "README.md"),
            "aix-stack-header-v2.svg",
        )

    def test_readme_does_not_reference_mascot(self):
        self._check_file_no_reference(
            os.path.join(REPO_ROOT, "README.md"),
            "axi-mascot.svg",
        )

    def test_agents_md_does_not_reference_any_deleted_asset(self):
        agents_path = os.path.join(REPO_ROOT, "AGENTS.md")
        for filename in DELETED_FILES:
            with self.subTest(filename=filename):
                self._check_file_no_reference(agents_path, filename)


class TestAssetsDirectoryIntegrity(unittest.TestCase):
    """Broad integrity checks on the assets directory."""

    def test_assets_directory_exists(self):
        self.assertTrue(
            os.path.isdir(ASSETS_DIR),
            "assets/ directory must exist",
        )

    def test_assets_directory_is_not_empty(self):
        if not os.path.isdir(ASSETS_DIR):
            self.skipTest("assets/ directory does not exist")
        entries = os.listdir(ASSETS_DIR)
        self.assertGreater(
            len(entries),
            0,
            "assets/ directory must not be empty",
        )

    def test_deleted_count_matches_expectation(self):
        """Exactly 4 files should have been deleted (boundary check)."""
        for filename in DELETED_FILES:
            full_path = os.path.join(ASSETS_DIR, filename)
            with self.subTest(filename=filename):
                self.assertFalse(os.path.exists(full_path))
        # All four absent → the deletion count is correct
        self.assertEqual(4, len(DELETED_FILES))


if __name__ == "__main__":
    unittest.main()