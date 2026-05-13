"""
Tests for scripts/link_doctor.py

Covers: _should_skip, _is_broken, _render, _gather_links, and _check,
exercising pure helpers directly and using mocks/tmp dirs for I/O.
"""

from __future__ import annotations

import importlib.util
import socket
import ssl
import sys
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "link_doctor.py"


def _import_link_doctor():
    spec = importlib.util.spec_from_file_location("link_doctor", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["link_doctor"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


ld = _import_link_doctor()


# ─── _should_skip ────────────────────────────────────────────────────────────


class TestShouldSkip:
    def test_skip_shields_io(self):
        assert ld._should_skip("https://img.shields.io/badge/foo-bar.svg") is True

    def test_skip_shields_io_bare(self):
        assert ld._should_skip("https://shields.io/badge/x") is True

    def test_skip_icons8(self):
        assert ld._should_skip("https://img.icons8.com/color/96/bot.png") is True

    def test_skip_avatars_githubusercontent(self):
        assert ld._should_skip("https://avatars.githubusercontent.com/u/12345?v=4") is True

    def test_skip_gstatic(self):
        assert ld._should_skip("https://www.gstatic.com/some/asset.png") is True

    def test_skip_commit_url(self):
        url = "https://github.com/Moeabdelaziz007/aix-agent-skills/commit/abc123"
        assert ld._should_skip(url) is True

    def test_skip_pull_url(self):
        url = "https://github.com/Moeabdelaziz007/aix-agent-skills/pull/42"
        assert ld._should_skip(url) is True

    def test_do_not_skip_regular_github_url(self):
        assert ld._should_skip("https://github.com/Moeabdelaziz007/aix-agent-skills") is False

    def test_do_not_skip_other_host(self):
        assert ld._should_skip("https://example.com/page") is False

    def test_do_not_skip_github_issues(self):
        # issues/ is not a skip prefix
        assert ld._should_skip("https://github.com/Moeabdelaziz007/aix-agent-skills/issues/1") is False

    def test_shields_io_in_query_string_not_skipped(self):
        # Only the host is checked, not substring matches in query strings.
        # A URL whose HOST is not img.shields.io should not be skipped.
        assert ld._should_skip("https://example.com/?ref=img.shields.io") is False

    def test_commit_prefix_must_match_exactly(self):
        # A commit URL for a different repo must NOT be skipped.
        url = "https://github.com/OtherUser/other-repo/commit/abc123"
        assert ld._should_skip(url) is False

    def test_http_scheme_not_skipped_on_non_skip_host(self):
        assert ld._should_skip("http://example.com/") is False


# ─── _is_broken ──────────────────────────────────────────────────────────────


class TestIsBroken:
    def test_none_is_broken(self):
        assert ld._is_broken(None) is True

    def test_200_is_healthy(self):
        assert ld._is_broken(200) is False

    def test_301_is_healthy(self):
        assert ld._is_broken(301) is False

    def test_304_is_healthy(self):
        assert ld._is_broken(304) is False

    def test_400_is_broken(self):
        assert ld._is_broken(400) is True

    def test_404_is_broken(self):
        assert ld._is_broken(404) is True

    def test_500_is_broken(self):
        assert ld._is_broken(500) is True

    def test_399_is_healthy(self):
        # Boundary: exactly below 400
        assert ld._is_broken(399) is False

    def test_zero_is_healthy(self):
        # Unexpected status 0 should not be treated as broken (0 < 400)
        assert ld._is_broken(0) is False


# ─── _render ─────────────────────────────────────────────────────────────────


class TestRender:
    _date = date(2026, 5, 13)

    def test_all_healthy_no_broken_section(self):
        results = [
            ("https://example.com", ["README.md"], 200, ""),
            ("https://other.com", ["foo.md"], 301, ""),
        ]
        out = ld._render(self._date, results)
        assert "# Link Health: 2026-05-13" in out
        assert "Scanned **2**" in out
        assert "Found **0**" in out
        assert "_All links healthy._" in out
        assert "## Broken links" not in out

    def test_with_broken_links_shows_table(self):
        results = [
            ("https://example.com/good", ["a.md"], 200, ""),
            ("https://dead.example.com/bad", ["b.md", "c.md"], 404, "HTTP 404"),
        ]
        out = ld._render(self._date, results)
        assert "## Broken links" in out
        assert "https://dead.example.com/bad" in out
        assert "HTTP 404" in out
        assert "Scanned **2**" in out
        assert "Found **1**" in out

    def test_none_status_shown_as_unreachable(self):
        results = [
            ("https://gone.example.com", ["x.md"], None, ""),
        ]
        out = ld._render(self._date, results)
        assert "unreachable" in out

    def test_none_status_with_message_shows_message(self):
        results = [
            ("https://gone.example.com", ["x.md"], None, "URLError"),
        ]
        out = ld._render(self._date, results)
        assert "URLError" in out

    def test_files_truncated_after_five(self):
        files = [f"file{i}.md" for i in range(8)]
        results = [
            ("https://example.com/many", files, 404, "HTTP 404"),
        ]
        out = ld._render(self._date, results)
        assert "+3 more" in out

    def test_exactly_five_files_no_truncation(self):
        files = [f"file{i}.md" for i in range(5)]
        results = [
            ("https://example.com/five", files, 404, "HTTP 404"),
        ]
        out = ld._render(self._date, results)
        assert "more" not in out

    def test_report_ends_with_newline(self):
        results = [("https://x.com", ["a.md"], 200, "")]
        out = ld._render(self._date, results)
        assert out.endswith("\n")

    def test_zero_urls_scanned(self):
        out = ld._render(self._date, [])
        assert "Scanned **0**" in out
        assert "Found **0**" in out
        assert "_All links healthy._" in out

    def test_date_appears_in_header(self):
        results = []
        out = ld._render(date(2025, 1, 1), results)
        assert "2025-01-01" in out

    def test_broken_500_shown(self):
        results = [("https://error.example.com", ["a.md"], 500, "HTTP 500")]
        out = ld._render(self._date, results)
        assert "## Broken links" in out
        assert "HTTP 500" in out


# ─── _gather_links ───────────────────────────────────────────────────────────


class TestGatherLinks:
    def test_extracts_https_url_from_markdown(self, tmp_path, monkeypatch):
        md = tmp_path / "README.md"
        md.write_text("See https://example.com/page for details.", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert "https://example.com/page" in result

    def test_skips_skip_hosts(self, tmp_path, monkeypatch):
        md = tmp_path / "doc.md"
        md.write_text("Badge: https://img.shields.io/badge/x.svg", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert result == {}

    def test_strips_trailing_punctuation(self, tmp_path, monkeypatch):
        md = tmp_path / "a.md"
        md.write_text("Visit https://example.com/page.", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        # Trailing dot must be stripped
        assert "https://example.com/page" in result
        assert "https://example.com/page." not in result

    def test_skips_git_directory(self, tmp_path, monkeypatch):
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        md = git_dir / "COMMIT_EDITMSG"
        # .git/* should be skipped; but glob only matches *.md, so make a md
        git_md = git_dir / "fake.md"
        git_md.write_text("https://should-not-appear.example.com/", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert "https://should-not-appear.example.com/" not in result

    def test_multiple_files_referencing_same_url(self, tmp_path, monkeypatch):
        (tmp_path / "a.md").write_text("https://shared.example.com/", encoding="utf-8")
        (tmp_path / "b.md").write_text("https://shared.example.com/", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert len(result["https://shared.example.com/"]) == 2

    def test_file_list_is_sorted(self, tmp_path, monkeypatch):
        (tmp_path / "z.md").write_text("https://sorted.example.com/", encoding="utf-8")
        (tmp_path / "a.md").write_text("https://sorted.example.com/", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        files = result["https://sorted.example.com/"]
        assert files == sorted(files)

    def test_inline_markdown_link_url_extracted(self, tmp_path, monkeypatch):
        md = tmp_path / "inline.md"
        md.write_text("[link text](https://inline.example.com/path)", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert "https://inline.example.com/path" in result

    def test_skips_node_modules(self, tmp_path, monkeypatch):
        nm = tmp_path / "node_modules"
        nm.mkdir()
        (nm / "pkg.md").write_text("https://node-modules.example.com/", encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert "https://node-modules.example.com/" not in result

    def test_no_markdown_files_returns_empty(self, tmp_path, monkeypatch):
        (tmp_path / "data.json").write_text('{"url": "https://example.com"}', encoding="utf-8")
        monkeypatch.setattr(ld, "ROOT", tmp_path)
        result = ld._gather_links()
        assert result == {}


# ─── _check ──────────────────────────────────────────────────────────────────


class TestCheck:
    """
    Tests for _check() using mocked urllib.request.urlopen so we never
    make real network calls.
    """

    def _make_response(self, status: int):
        mock_resp = MagicMock()
        mock_resp.status = status
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_200_returns_ok(self):
        with patch("urllib.request.urlopen", return_value=self._make_response(200)):
            status, msg = ld._check("https://example.com/", 5)
        assert status == 200
        assert msg == ""

    def test_301_returns_redirect(self):
        with patch("urllib.request.urlopen", return_value=self._make_response(301)):
            status, msg = ld._check("https://example.com/", 5)
        assert status == 301
        assert msg == ""

    def test_404_http_error_returned(self):
        exc = urllib.error.HTTPError(
            url="https://example.com/",
            code=404,
            msg="Not Found",
            hdrs={},  # type: ignore[arg-type]
            fp=None,
        )
        with patch("urllib.request.urlopen", side_effect=exc):
            status, msg = ld._check("https://example.com/", 5)
        assert status == 404
        assert "404" in msg

    def test_403_retries_with_get(self):
        """On 403 HEAD, _check retries with GET; mock GET returning 200."""
        head_exc = urllib.error.HTTPError(
            url="https://example.com/",
            code=403,
            msg="Forbidden",
            hdrs={},  # type: ignore[arg-type]
            fp=None,
        )
        good_resp = self._make_response(200)

        call_count = [0]

        def urlopen_side_effect(req, timeout, context):
            call_count[0] += 1
            if call_count[0] == 1:
                raise head_exc
            return good_resp

        with patch("urllib.request.urlopen", side_effect=urlopen_side_effect):
            status, msg = ld._check("https://example.com/", 5)
        assert status == 200
        assert call_count[0] == 2

    def test_405_retries_with_get(self):
        """On 405 HEAD, _check retries with GET."""
        head_exc = urllib.error.HTTPError(
            url="https://example.com/",
            code=405,
            msg="Method Not Allowed",
            hdrs={},  # type: ignore[arg-type]
            fp=None,
        )
        good_resp = self._make_response(200)

        call_count = [0]

        def urlopen_side_effect(req, timeout, context):
            call_count[0] += 1
            if call_count[0] == 1:
                raise head_exc
            return good_resp

        with patch("urllib.request.urlopen", side_effect=urlopen_side_effect):
            status, msg = ld._check("https://example.com/", 5)
        assert status == 200

    def test_url_error_returns_none(self):
        exc = urllib.error.URLError("Name or service not known")
        with patch("urllib.request.urlopen", side_effect=exc):
            status, msg = ld._check("https://no-such-host.invalid/", 5)
        assert status is None
        assert msg == "URLError"

    def test_socket_timeout_returns_none(self):
        with patch("urllib.request.urlopen", side_effect=socket.timeout()):
            status, msg = ld._check("https://slow.example.com/", 1)
        assert status is None

    def test_connection_error_returns_none(self):
        with patch("urllib.request.urlopen", side_effect=ConnectionError("refused")):
            status, msg = ld._check("https://refused.example.com/", 5)
        assert status is None

    def test_403_retry_also_fails_returns_none(self):
        """When the GET retry after 403 also fails, returns (None, msg)."""
        head_exc = urllib.error.HTTPError(
            url="https://example.com/",
            code=403,
            msg="Forbidden",
            hdrs={},  # type: ignore[arg-type]
            fp=None,
        )

        call_count = [0]

        def urlopen_side_effect(req, timeout, context):
            call_count[0] += 1
            if call_count[0] == 1:
                raise head_exc
            raise ConnectionError("second attempt failed")

        with patch("urllib.request.urlopen", side_effect=urlopen_side_effect):
            status, msg = ld._check("https://example.com/", 5)
        assert status is None
        assert "403" in msg