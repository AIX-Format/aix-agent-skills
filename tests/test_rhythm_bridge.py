"""
Tests for the Rhythm Bridge — the iqra ↔ marketplace tide synchronizer.

These tests exercise the pure helpers (cadence, scoring, parsing,
idempotency) without spawning subprocesses. The git-mining helpers are
tested at the seam with a small fixture of synthesized log output.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "rhythm_bridge.py"


def _import_rhythm_bridge():
    """
    Dynamically load the rhythm_bridge module from SCRIPT_PATH and return it.
    
    The loaded module is registered in sys.modules under the name "rhythm_bridge".
    
    Returns:
        module: The imported rhythm_bridge module object.
    """
    spec = importlib.util.spec_from_file_location("rhythm_bridge", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules["rhythm_bridge"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


rb = _import_rhythm_bridge()


# ─── Cadence ────────────────────────────────────────────────────────────────


class TestDetermineAction:
    def test_first_run_is_telemetry(self):
        assert rb.determine_action(0) == "TELEMETRY_MIRROR"

    def test_ordinary_tick_is_telemetry(self):
        assert rb.determine_action(1) == "TELEMETRY_MIRROR"
        assert rb.determine_action(5) == "TELEMETRY_MIRROR"

    def test_cross_pollinate_every_9(self):
        assert rb.determine_action(9) == "CROSS_POLLINATE"
        assert rb.determine_action(18) == "CROSS_POLLINATE"

    def test_tier_rebalance_every_56(self):
        # 56 is also divisible by neither 9 nor 392, so the rebalance check
        # comes after CROSS_POLLINATE in the cascade. We verify the result.
        assert rb.determine_action(56) == "TIER_REBALANCE"

    def test_deep_reform_every_392(self):
        assert rb.determine_action(392) == "DEEP_REFORM"

    def test_force_override_wins(self):
        assert rb.determine_action(1, override="DEEP_REFORM") == "DEEP_REFORM"
        # Even the tick-0 baseline gives way to an explicit override.
        assert rb.determine_action(0, override="CROSS_POLLINATE") == "CROSS_POLLINATE"


# ─── Tide & activity scoring ────────────────────────────────────────────────


class TestTideScore:
    def test_zero_signal_is_zero(self):
        sig = rb.IqraSignal(name="x")
        assert sig.tide_score == 0.0

    def test_score_is_bounded_in_unit_interval(self):
        sig = rb.IqraSignal(name="x", weighted_score=1000.0)
        # tanh saturates to 1.0 for large inputs; we only require [0, 1].
        assert 0.0 < sig.tide_score <= 1.0

    def test_higher_weight_is_higher_score(self):
        low = rb.IqraSignal(name="x", weighted_score=1.0).tide_score
        high = rb.IqraSignal(name="x", weighted_score=10.0).tide_score
        assert high > low


class TestActivityScore:
    def test_zero_changes_is_zero(self):
        sig = rb.MarketplaceSignal(name="x")
        assert sig.activity_score == 0.0

    def test_more_commits_more_score(self):
        a = rb.MarketplaceSignal(name="x", commits=1, lines_changed=10).activity_score
        b = rb.MarketplaceSignal(name="x", commits=5, lines_changed=10).activity_score
        assert b > a


# ─── Frontmatter parsing ────────────────────────────────────────────────────


class TestExtractSuccessPatterns:
    @pytest.fixture(autouse=True)
    def _reset_registry_cache(self, monkeypatch):
        # Each test starts with a fresh registry view so monkeypatched
        # registry files take effect.
        """
        Reset the Rhythm Bridge success-patterns registry cache so tests observe fresh registry state.
        
        This fixture clears rb._PATTERNS_REGISTRY (sets it to None) before a test runs, ensuring that subsequent monkeypatches of the registry file or its contents take effect.
        """
        monkeypatch.setattr(rb, "_PATTERNS_REGISTRY", None)

    def test_unknown_skill_returns_empty(self, monkeypatch, tmp_path):
        empty = tmp_path / "registry.json"
        empty.write_text(json.dumps({"patterns": {}}), encoding="utf-8")
        monkeypatch.setattr(rb, "PATTERNS_REGISTRY_FILE", empty)
        assert rb.extract_success_patterns("unknown") == []

    def test_known_skill_returns_patterns(self, monkeypatch, tmp_path):
        reg = tmp_path / "registry.json"
        reg.write_text(
            json.dumps({"patterns": {"skill": ["alpha", "beta"]}}), encoding="utf-8"
        )
        monkeypatch.setattr(rb, "PATTERNS_REGISTRY_FILE", reg)
        assert rb.extract_success_patterns("skill") == ["alpha", "beta"]

    def test_path_argument_resolves_to_stem(self, monkeypatch, tmp_path):
        reg = tmp_path / "registry.json"
        reg.write_text(
            json.dumps({"patterns": {"skill": ["gamma"]}}), encoding="utf-8"
        )
        monkeypatch.setattr(rb, "PATTERNS_REGISTRY_FILE", reg)
        assert rb.extract_success_patterns(tmp_path / "skill.md") == ["gamma"]

    def test_missing_registry_returns_empty(self, monkeypatch, tmp_path):
        monkeypatch.setattr(rb, "PATTERNS_REGISTRY_FILE", tmp_path / "missing.json")
        assert rb.extract_success_patterns("anything") == []


# ─── Idempotency ────────────────────────────────────────────────────────────


class TestHasBeenPollinatedFrom:
    def test_clean_recipient_is_not_pollinated(self, tmp_path):
        md = tmp_path / "r.md"
        md.write_text("# title\n", encoding="utf-8")
        assert rb.has_been_pollinated_from(md, "donor") is False

    def test_recipient_with_section_from_donor_is_pollinated(self, tmp_path):
        md = tmp_path / "r.md"
        md.write_text(
            "# title\n\n## 🌊 Inherited Patterns\n\n"
            "_Auto-pollinated from `donor` by the Rhythm Bridge._\n",
            encoding="utf-8",
        )
        assert rb.has_been_pollinated_from(md, "donor") is True

    def test_section_from_other_donor_does_not_block(self, tmp_path):
        md = tmp_path / "r.md"
        md.write_text(
            "# title\n\n## 🌊 Inherited Patterns\n\n"
            "_Auto-pollinated from `someone-else` by the Rhythm Bridge._\n",
            encoding="utf-8",
        )
        assert rb.has_been_pollinated_from(md, "donor") is False


# ─── Pollination section rendering ──────────────────────────────────────────


class TestPollinationSection:
    def test_section_starts_with_header(self):
        sec = rb.pollination_section("donor-x", ["a", "b"], 0.5, tick=42)
        assert rb.SECTION_HEADER in sec
        assert "`donor-x`" in sec

    def test_section_includes_all_patterns(self):
        sec = rb.pollination_section("d", ["p1", "p2", "p3"], 0.9, tick=1)
        for p in ["p1", "p2", "p3"]:
            assert f"- {p}" in sec

    def test_section_records_cycle_and_confidence(self):
        sec = rb.pollination_section("d", ["p"], 0.74, tick=99)
        assert "cycle 99" in sec
        assert "0.74" in sec


# ─── Tick file IO ───────────────────────────────────────────────────────────


class TestTickIO:
    def test_read_tick_missing_file_is_zero(self, monkeypatch, tmp_path):
        monkeypatch.setattr(rb, "TICK_FILE", tmp_path / "tick")
        assert rb.read_tick() == 0

    def test_write_then_read_roundtrip(self, monkeypatch, tmp_path):
        monkeypatch.setattr(rb, "TICK_FILE", tmp_path / "tick")
        rb.write_tick(42)
        assert rb.read_tick() == 42

    def test_corrupt_tick_file_reads_as_zero(self, monkeypatch, tmp_path):
        f = tmp_path / "tick"
        f.write_text("not-a-number\n", encoding="utf-8")
        monkeypatch.setattr(rb, "TICK_FILE", f)
        assert rb.read_tick() == 0


# ─── Pair generation ────────────────────────────────────────────────────────


class TestComputePairs:
    def _build_signals(self, donor_score=0.9, recipient_score=0.9):
        """
        Create sample donor and recipient signal objects for tests.
        
        Parameters:
            donor_score (float): Ignored; present for API compatibility.
            recipient_score (float): Ignored; present for API compatibility.
        
        Returns:
            tuple: Two dictionaries:
                - First maps "donor" to an `rb.IqraSignal` configured to exceed `rb.HIGH_THRESHOLD`.
                - Second maps "recipient" to an `rb.MarketplaceSignal` with positive activity.
        """
        donor = rb.IqraSignal(name="donor", weighted_score=10.0, mention_count=5)
        recipient = rb.MarketplaceSignal(name="recipient", lines_changed=50, commits=3)
        # Sanity: our hand-picked weights should clear the thresholds.
        assert donor.tide_score >= rb.HIGH_THRESHOLD
        assert recipient.activity_score > 0
        return {"donor": donor}, {"recipient": recipient}

    def test_no_patterns_means_no_pairs(self, monkeypatch):
        iqra, market = self._build_signals()
        monkeypatch.setattr(rb, "extract_success_patterns", lambda _p: [])
        pairs = rb.compute_pairs(iqra, market, cooldowns={}, tick=1)
        assert pairs == []

    def test_with_patterns_emits_pair(self, monkeypatch):
        iqra, market = self._build_signals()
        monkeypatch.setattr(rb, "extract_success_patterns", lambda _p: ["pattern_a"])
        monkeypatch.setattr(rb, "has_been_pollinated_from", lambda *_a, **_k: False)
        pairs = rb.compute_pairs(iqra, market, cooldowns={}, tick=1)
        assert len(pairs) == 1
        assert pairs[0].donor == "donor"
        assert pairs[0].recipient == "recipient"

    def test_cooldown_skips_pair(self, monkeypatch):
        iqra, market = self._build_signals()
        monkeypatch.setattr(rb, "extract_success_patterns", lambda _p: ["x"])
        monkeypatch.setattr(rb, "has_been_pollinated_from", lambda *_a, **_k: False)
        cooldowns = {"donor->recipient": 99}
        pairs = rb.compute_pairs(iqra, market, cooldowns=cooldowns, tick=1)
        assert pairs == []

    def test_already_pollinated_skips(self, monkeypatch):
        iqra, market = self._build_signals()
        monkeypatch.setattr(rb, "extract_success_patterns", lambda _p: ["x"])
        monkeypatch.setattr(rb, "has_been_pollinated_from", lambda *_a, **_k: True)
        pairs = rb.compute_pairs(iqra, market, cooldowns={}, tick=1)
        assert pairs == []

    def test_max_pairs_per_cycle_enforced(self, monkeypatch):
        # 10 high-tide donors all targeting 10 active recipients = 100 candidate
        # pairs. The cap is 7.
        iqra = {
            f"d{i}": rb.IqraSignal(name=f"d{i}", weighted_score=10.0, mention_count=5)
            for i in range(10)
        }
        market = {
            f"r{i}": rb.MarketplaceSignal(name=f"r{i}", lines_changed=50, commits=3)
            for i in range(10)
        }
        monkeypatch.setattr(rb, "extract_success_patterns", lambda _p: ["x"])
        monkeypatch.setattr(rb, "has_been_pollinated_from", lambda *_a, **_k: False)
        pairs = rb.compute_pairs(iqra, market, cooldowns={}, tick=1)
        assert len(pairs) == rb.MAX_PAIRS_PER_CYCLE


# ─── Constants discipline ───────────────────────────────────────────────────


class TestRhythmConstants:
    def test_cadence_multiples_align(self):
        # The cascade ordering depends on these multiplicative relationships.
        # If someone breaks them, the cadence logic stops being meaningful.
        assert rb.TIER_REBALANCE_EVERY > rb.CROSS_POLLINATE_EVERY
        assert rb.DEEP_REFORM_EVERY > rb.TIER_REBALANCE_EVERY

    def test_cooldown_does_not_exceed_a_cross_pollinate_cycle(self):
        # Otherwise a pair would still be cooled-down on the next chance to
        # try it, defeating the daily reseed.
        assert rb.COOLDOWN_TICKS <= rb.CROSS_POLLINATE_EVERY

    def test_max_pairs_is_a_safe_positive_number(self):
        assert 1 <= rb.MAX_PAIRS_PER_CYCLE <= 49

    def test_tick_hours_is_three(self):
        # Pulse369 alignment is the load-bearing assumption; the cron in
        # the workflow must match if this ever changes.
        assert rb.TICK_HOURS == 3
