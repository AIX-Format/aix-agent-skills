"""
Tests for scripts/talent_scout.py

Covers: _normalize_identity, _is_bot, _git, _collect (via mocked git),
_row, and _render — exercising pure helpers directly and using mocks for
subprocess calls.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "talent_scout.py"


def _import_talent_scout():
    spec = importlib.util.spec_from_file_location("talent_scout", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["talent_scout"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


ts = _import_talent_scout()


# ─── _normalize_identity ─────────────────────────────────────────────────────


class TestNormalizeIdentity:
    def test_plain_ascii_unchanged(self):
        assert ts._normalize_identity("Alice") == "Alice"

    def test_strips_leading_trailing_whitespace(self):
        assert ts._normalize_identity("  Bob  ") == "Bob"

    def test_nfkc_collapses_ligatures(self):
        # U+FB01 (ﬁ) → f + i under NFKC
        assert ts._normalize_identity("\ufb01le") == "file"

    def test_strips_zero_width_space(self):
        # U+200B ZERO WIDTH SPACE is category Cf
        name_with_zwsp = "Alice\u200BBob"
        result = ts._normalize_identity(name_with_zwsp)
        assert result == "AliceBob"

    def test_strips_pop_directional_formatting(self):
        # U+202C POP DIRECTIONAL FORMATTING is category Cf
        name = "Moe\u202cAbdelaziz"
        result = ts._normalize_identity(name)
        assert "\u202c" not in result
        assert result == "MoeAbdelaziz"

    def test_strips_zero_width_no_break_space(self):
        # U+FEFF BOM/ZWNBSP — also category Cf
        name = "\ufeffLeading"
        result = ts._normalize_identity(name)
        assert result == "Leading"

    def test_two_visually_identical_names_become_equal(self):
        # Same person with a stray invisible char should collapse to same key
        name_a = "Mohamed Abdelaziz"
        name_b = "Mohamed\u200b Abdelaziz"
        assert ts._normalize_identity(name_a) == ts._normalize_identity(name_b)

    def test_empty_string_returns_empty(self):
        assert ts._normalize_identity("") == ""

    def test_unicode_letters_preserved(self):
        # Non-ASCII letters that are NOT format chars should be kept
        assert ts._normalize_identity("Ñoño") == "Ñoño"


# ─── _is_bot ─────────────────────────────────────────────────────────────────


class TestIsBot:
    def test_bracket_bot_suffix_is_bot(self):
        assert ts._is_bot("coderabbitai[bot]", "app@example.com") is True

    def test_dash_bot_suffix_is_bot(self):
        assert ts._is_bot("iqra-dashboard-bot", "bot@iqra.io") is True

    def test_suffix_case_insensitive(self):
        assert ts._is_bot("My-BOT", "me@example.com") is True
        assert ts._is_bot("Some[BOT]", "me@example.com") is True

    def test_actions_email_is_bot(self):
        assert ts._is_bot("GitHub Actions", "actions@github.com") is True

    def test_noreply_github_email_is_bot(self):
        assert ts._is_bot("Someone", "41898282+github-actions[bot]@users.noreply.github.com") is True

    def test_coderabbit_email_is_bot(self):
        assert ts._is_bot("CodeRabbit", "support@coderabbit.ai") is True

    def test_dependabot_email_is_bot(self):
        assert ts._is_bot("dependabot[bot]", "dependabot@github.com") is True

    def test_iqra_sovereign_email_is_bot(self):
        assert ts._is_bot("Sentinel", "sentinel@iqra.sovereign") is True

    def test_human_name_and_email_is_not_bot(self):
        assert ts._is_bot("Alice Smith", "alice@example.com") is False

    def test_name_containing_bot_as_word_prefix_is_not_bot(self):
        # "robotics" ends in "tics", not "-bot" or "[bot]"
        assert ts._is_bot("robotics-team", "team@example.com") is False

    def test_email_with_bot_substring_only_matches_known_snippet(self):
        # "mybot.io" does not contain any of the BOT_EMAILS snippets
        assert ts._is_bot("Alice", "alice@mybot.io") is False

    def test_iqra_dashboard_bot_name_is_bot(self):
        assert ts._is_bot("iqra-dashboard-bot", "dashboard@iqra.io") is True

    def test_human_with_bot_elsewhere_in_name_not_bot(self):
        # "aboutme" contains neither [bot] nor -bot suffix
        assert ts._is_bot("aboutme", "user@example.com") is False


# ─── _git ─────────────────────────────────────────────────────────────────────


class TestGit:
    def test_returns_stdout_on_success(self):
        mock_cp = MagicMock()
        mock_cp.returncode = 0
        mock_cp.stdout = "abc123 commit message\n"
        mock_cp.stderr = ""
        with patch("subprocess.run", return_value=mock_cp) as mock_run:
            result = ts._git("log", "--oneline")
        assert result == "abc123 commit message\n"
        # Ensure git -C <ROOT> was called
        args = mock_run.call_args[0][0]
        assert args[0] == "git"
        assert "-C" in args
        assert "log" in args

    def test_raises_runtime_error_on_nonzero_exit(self):
        mock_cp = MagicMock()
        mock_cp.returncode = 128
        mock_cp.stdout = ""
        mock_cp.stderr = "fatal: not a git repository"
        with patch("subprocess.run", return_value=mock_cp):
            with pytest.raises(RuntimeError, match="fatal: not a git repository"):
                ts._git("log")

    def test_error_message_includes_subcommand(self):
        mock_cp = MagicMock()
        mock_cp.returncode = 1
        mock_cp.stdout = ""
        mock_cp.stderr = "some error"
        with patch("subprocess.run", return_value=mock_cp):
            with pytest.raises(RuntimeError, match="log"):
                ts._git("log", "--all")


# ─── _row ─────────────────────────────────────────────────────────────────────


class TestRow:
    def test_row_format(self):
        stats = {"commits": 5, "added": 100, "removed": 20, "first": "2026-01-01", "last": "2026-05-13"}
        row = ts._row("Alice", stats)
        assert row == "| Alice | 5 | 100 | 20 | 2026-01-01 | 2026-05-13 |"

    def test_row_with_zero_lines(self):
        stats = {"commits": 1, "added": 0, "removed": 0, "first": "2026-01-01", "last": "2026-01-01"}
        row = ts._row("Bob", stats)
        assert "| 0 |" in row
        assert row.startswith("| Bob |")


# ─── _render ─────────────────────────────────────────────────────────────────


class TestRender:
    def _make_humans(self, *names_and_commits):
        """Helper: returns dict of {name: stats} ordered by (name, commits)."""
        from collections import defaultdict
        d = {}
        for name, commits in names_and_commits:
            d[name] = {"commits": commits, "added": 0, "removed": 0, "first": "2026-01-01", "last": "2026-05-01"}
        return d

    def test_header_always_present(self):
        out = ts._render({}, {})
        assert "# Contributors" in out

    def test_auto_generated_notice_present(self):
        out = ts._render({}, {})
        assert "Auto-generated from `git log`" in out
        assert "scripts/talent_scout.py" in out

    def test_humans_count_in_section_header(self):
        humans = self._make_humans(("Alice", 3), ("Bob", 1))
        out = ts._render(humans, {})
        assert "## Humans (2)" in out

    def test_no_humans_shows_placeholder(self):
        out = ts._render({}, {})
        assert "_No human contributors recorded yet._" in out

    def test_bots_section_omitted_when_empty(self):
        humans = self._make_humans(("Alice", 1))
        out = ts._render(humans, {})
        assert "## Bots" not in out

    def test_bots_section_present_when_bots_exist(self):
        bots = self._make_humans(("github-actions[bot]", 2))
        out = ts._render({}, bots)
        assert "## Bots (1)" in out

    def test_humans_sorted_by_commits_descending(self):
        humans = self._make_humans(("Charlie", 1), ("Alice", 5), ("Bob", 3))
        out = ts._render(humans, {})
        idx_alice = out.index("Alice")
        idx_bob = out.index("Bob")
        idx_charlie = out.index("Charlie")
        assert idx_alice < idx_bob < idx_charlie

    def test_humans_sorted_alphabetically_on_tie(self):
        humans = self._make_humans(("Zara", 2), ("Alice", 2))
        out = ts._render(humans, {})
        idx_alice = out.index("| Alice |")
        idx_zara = out.index("| Zara |")
        assert idx_alice < idx_zara

    def test_output_ends_with_newline(self):
        out = ts._render({}, {})
        assert out.endswith("\n")

    def test_table_header_present_for_humans(self):
        humans = self._make_humans(("Alice", 1))
        out = ts._render(humans, {})
        assert "| Name | Commits | Lines added | Lines removed | First | Latest |" in out

    def test_bots_count_in_section_header(self):
        bots = self._make_humans(("bot-a", 3), ("bot-b", 1), ("bot-c", 2))
        out = ts._render({}, bots)
        assert "## Bots (3)" in out

    def test_human_name_appears_in_table(self):
        humans = {"Mohamed": {"commits": 10, "added": 500, "removed": 50, "first": "2026-01-01", "last": "2026-05-13"}}
        out = ts._render(humans, {})
        assert "| Mohamed |" in out
        assert "| 10 |" in out


# ─── _collect (integration via mocked _git) ──────────────────────────────────


class TestCollect:
    """
    Tests for _collect() using a synthesized git log --shortstat output.
    The output format expected by the parser is:
        COMMIT\t<name>\t<email>\t<date>
        [blank line]
         N files changed, M insertions(+), K deletions(-)
    """

    _SAMPLE_LOG = (
        "COMMIT\tAlice\talice@example.com\t2026-01-15\n"
        "\n"
        " 3 files changed, 50 insertions(+), 10 deletions(-)\n"
        "COMMIT\tAlice\talice@example.com\t2026-02-01\n"
        "\n"
        " 1 file changed, 5 insertions(+)\n"
        "COMMIT\tgithub-actions[bot]\t41898282+github-actions[bot]@users.noreply.github.com\t2026-02-10\n"
        "\n"
        " 1 file changed, 3 insertions(+), 3 deletions(-)\n"
    )

    def test_human_commit_count(self):
        with patch.object(ts, "_git", return_value=self._SAMPLE_LOG):
            humans, bots = ts._collect()
        assert humans["Alice"]["commits"] == 2

    def test_human_added_lines_accumulated(self):
        with patch.object(ts, "_git", return_value=self._SAMPLE_LOG):
            humans, _ = ts._collect()
        assert humans["Alice"]["added"] == 55  # 50 + 5

    def test_human_removed_lines_accumulated(self):
        with patch.object(ts, "_git", return_value=self._SAMPLE_LOG):
            humans, _ = ts._collect()
        assert humans["Alice"]["removed"] == 10

    def test_bot_is_classified_correctly(self):
        with patch.object(ts, "_git", return_value=self._SAMPLE_LOG):
            humans, bots = ts._collect()
        assert "github-actions[bot]" not in humans
        assert "github-actions[bot]" in bots

    def test_bot_stats_accumulated(self):
        with patch.object(ts, "_git", return_value=self._SAMPLE_LOG):
            _, bots = ts._collect()
        assert bots["github-actions[bot]"]["added"] == 3
        assert bots["github-actions[bot]"]["removed"] == 3

    def test_first_and_last_dates_tracked(self):
        with patch.object(ts, "_git", return_value=self._SAMPLE_LOG):
            humans, _ = ts._collect()
        assert humans["Alice"]["first"] == "2026-01-15"
        assert humans["Alice"]["last"] == "2026-02-01"

    def test_empty_log_returns_empty_dicts(self):
        with patch.object(ts, "_git", return_value=""):
            humans, bots = ts._collect()
        assert humans == {}
        assert bots == {}

    def test_commit_without_stat_lines(self):
        log = "COMMIT\tBob\tbob@example.com\t2026-03-01\n"
        with patch.object(ts, "_git", return_value=log):
            humans, _ = ts._collect()
        assert humans["Bob"]["commits"] == 1
        assert humans["Bob"]["added"] == 0
        assert humans["Bob"]["removed"] == 0

    def test_git_error_propagates_as_runtime_error(self):
        with patch.object(ts, "_git", side_effect=RuntimeError("fatal: not a repo")):
            with pytest.raises(RuntimeError, match="fatal: not a repo"):
                ts._collect()

    def test_single_file_changed_line(self):
        """'1 file changed' (singular) must be parsed correctly."""
        log = (
            "COMMIT\tCarol\tcarol@example.com\t2026-04-01\n"
            "\n"
            " 1 file changed, 7 insertions(+), 2 deletions(-)\n"
        )
        with patch.object(ts, "_git", return_value=log):
            humans, _ = ts._collect()
        assert humans["Carol"]["added"] == 7
        assert humans["Carol"]["removed"] == 2

    def test_normalized_name_deduplication(self):
        """Two log entries with same name but invisible char collapse to one."""
        log = (
            "COMMIT\tMoe\u200b\tmoe@example.com\t2026-01-01\n"
            "\n"
            " 1 file changed, 10 insertions(+)\n"
            "COMMIT\tMoe\tmoe@example.com\t2026-01-02\n"
            "\n"
            " 1 file changed, 5 insertions(+)\n"
        )
        with patch.object(ts, "_git", return_value=log):
            humans, _ = ts._collect()
        # Both should collapse onto "Moe"
        assert "Moe" in humans
        assert humans["Moe"]["commits"] == 2
        assert humans["Moe"]["added"] == 15

    def test_no_insertions_line(self):
        """Stat line with only deletions (no insertions) should not raise."""
        log = (
            "COMMIT\tDave\tdave@example.com\t2026-05-01\n"
            "\n"
            " 2 files changed, 3 deletions(-)\n"
        )
        with patch.object(ts, "_git", return_value=log):
            humans, _ = ts._collect()
        assert humans["Dave"]["added"] == 0
        assert humans["Dave"]["removed"] == 3


# ─── main ─────────────────────────────────────────────────────────────────────


class TestMain:
    """
    Tests for main() using mocked _collect and filesystem I/O so we never
    touch the real git repo or write to the actual CONTRIBUTORS.md.
    """

    _HUMANS = {
        "Alice": {"commits": 5, "added": 100, "removed": 20, "first": "2026-01-01", "last": "2026-05-13"},
    }
    _BOTS = {
        "github-actions[bot]": {"commits": 2, "added": 10, "removed": 5, "first": "2026-02-01", "last": "2026-04-01"},
    }

    def test_success_returns_zero(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", return_value=(self._HUMANS, self._BOTS)):
            rc = ts.main()
        assert rc == 0

    def test_success_writes_contributors_file(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", return_value=(self._HUMANS, self._BOTS)):
            ts.main()
        assert target.exists()
        content = target.read_text(encoding="utf-8")
        assert "# Contributors" in content

    def test_success_output_contains_human_and_bot_counts(self, tmp_path, monkeypatch, capsys):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", return_value=(self._HUMANS, self._BOTS)):
            ts.main()
        captured = capsys.readouterr()
        assert "1 humans" in captured.out
        assert "1 bots" in captured.out

    def test_runtime_error_returns_one(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", side_effect=RuntimeError("git failed")):
            rc = ts.main()
        assert rc == 1

    def test_runtime_error_prints_to_stderr(self, tmp_path, monkeypatch, capsys):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", side_effect=RuntimeError("fatal: broken repo")):
            ts.main()
        captured = capsys.readouterr()
        assert "fatal: broken repo" in captured.err

    def test_runtime_error_does_not_write_file(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", side_effect=RuntimeError("git failed")):
            ts.main()
        assert not target.exists()

    def test_empty_humans_and_bots_writes_placeholder(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", return_value=({}, {})):
            ts.main()
        content = target.read_text(encoding="utf-8")
        assert "_No human contributors recorded yet._" in content

    def test_written_file_includes_human_name(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", return_value=(self._HUMANS, {})):
            ts.main()
        content = target.read_text(encoding="utf-8")
        assert "Alice" in content

    def test_zero_bots_no_bots_section(self, tmp_path, monkeypatch):
        target = tmp_path / "CONTRIBUTORS.md"
        monkeypatch.setattr(ts, "ROOT", tmp_path)
        monkeypatch.setattr(ts, "TARGET", target)
        with patch.object(ts, "_collect", return_value=(self._HUMANS, {})):
            ts.main()
        content = target.read_text(encoding="utf-8")
        assert "## Bots" not in content
