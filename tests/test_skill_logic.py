#!/usr/bin/env python3
"""
test_skill_logic.py — Direct unit tests for Python logic embedded in skill markdown files.

Tests execute the skill code directly in-process (no subprocesses) to verify
logic correctness with fine-grained edge-case coverage.

Skills tested (added/modified in this PR):
  - circuit-breaker.md
  - data-alchemist.md
  - topology-orchestrator.md
  - trust-chain.md
"""

import hashlib
import json
import os
import sys
import types
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).parent.parent.resolve()


def load_skill_module(skill_filename):
    """
    Extract the Python code block from a skill markdown file and
    return it as an importable module object.
    """
    import re
    path = ROOT / "skills" / skill_filename
    content = path.read_text()
    match = re.search(r'```python\n(.*?)```', content, re.DOTALL)
    assert match, f"No python block found in {skill_filename}"
    code = match.group(1)

    module = types.ModuleType(skill_filename.replace(".md", "").replace("-", "_"))
    exec(compile(code, skill_filename, "exec"), module.__dict__)
    return module


# ─── Circuit Breaker Logic ────────────────────────────────────────────────────

class TestCircuitBreakerLogic:
    """Direct tests for circuit-breaker.md Python logic."""

    STATE_FILE = "/tmp/circuit_breaker_state.json"

    @pytest.fixture(autouse=True)
    def cleanup_state(self):
        if os.path.exists(self.STATE_FILE):
            os.remove(self.STATE_FILE)
        yield
        if os.path.exists(self.STATE_FILE):
            os.remove(self.STATE_FILE)

    @pytest.fixture
    def cb(self):
        return load_skill_module("circuit-breaker.md")

    def test_load_state_returns_default_when_no_file(self, cb):
        state = cb.load_state()
        assert state == {"failures": 0, "state": "closed"}

    def test_load_state_reads_existing_file(self, cb):
        existing = {"failures": 3, "state": "closed"}
        with open(self.STATE_FILE, "w") as f:
            json.dump(existing, f)
        state = cb.load_state()
        assert state["failures"] == 3
        assert state["state"] == "closed"

    def test_save_state_persists_to_file(self, cb):
        state = {"failures": 2, "state": "closed"}
        cb.save_state(state)
        with open(self.STATE_FILE) as f:
            loaded = json.load(f)
        assert loaded == state

    def test_can_execute_on_fresh_state_is_allowed(self, cb, capsys):
        cb.main({"action": "can_execute", "skill": "test-skill"})
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["allowed"] is True
        assert result["state"] == "closed"

    def test_record_failure_increments_counter(self, cb, capsys):
        cb.main({"action": "record_failure", "skill": "test-skill"})
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["recorded"] is True
        assert result["state"] == "closed"

        # Verify persisted state
        state = cb.load_state()
        assert state["failures"] == 1

    def test_four_failures_keeps_circuit_closed(self, cb, capsys):
        """Boundary: 4 failures should NOT open the circuit (threshold is 5)."""
        for _ in range(4):
            cb.main({"action": "record_failure", "skill": "s"})
        capsys.readouterr()  # flush

        cb.main({"action": "can_execute", "skill": "s"})
        result = json.loads(capsys.readouterr().out)
        assert result["allowed"] is True
        assert result["state"] == "closed"

    def test_fifth_failure_opens_circuit(self, cb, capsys):
        """Boundary: exactly 5 failures opens the circuit."""
        for _ in range(5):
            cb.main({"action": "record_failure", "skill": "s"})
        capsys.readouterr()  # flush

        cb.main({"action": "can_execute", "skill": "s"})
        result = json.loads(capsys.readouterr().out)
        assert result["allowed"] is False
        assert result["state"] == "open"

    def test_sixth_failure_stays_open(self, cb, capsys):
        for _ in range(6):
            cb.main({"action": "record_failure", "skill": "s"})
        capsys.readouterr()

        state = cb.load_state()
        assert state["state"] == "open"
        assert state["failures"] == 6

    def test_unknown_action_returns_error(self, cb, capsys):
        cb.main({"action": "bogus_action", "skill": "s"})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_missing_action_key_returns_error(self, cb, capsys):
        cb.main({})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_state_persists_across_multiple_calls(self, cb, capsys):
        """Each main() call reads and writes state — verify accumulation."""
        for i in range(3):
            cb.main({"action": "record_failure", "skill": f"skill-{i}"})
        capsys.readouterr()

        state = cb.load_state()
        assert state["failures"] == 3
        assert state["state"] == "closed"


# ─── Data Alchemist Logic ─────────────────────────────────────────────────────

class TestDataAlchemistLogic:
    """Direct tests for data-alchemist.md Python logic."""

    @pytest.fixture
    def da(self):
        return load_skill_module("data-alchemist.md")

    def test_summary_basic(self, da, capsys):
        da.main({"data": [1, 2, 3, 4, 5], "op": "summary"})
        result = json.loads(capsys.readouterr().out)
        assert result["count"] == 5
        assert result["sum"] == 15
        assert result["avg"] == 3.0
        assert result["min"] == 1
        assert result["max"] == 5

    def test_summary_single_element(self, da, capsys):
        da.main({"data": [42], "op": "summary"})
        result = json.loads(capsys.readouterr().out)
        assert result["count"] == 1
        assert result["sum"] == 42
        assert result["avg"] == 42.0
        assert result["min"] == 42
        assert result["max"] == 42

    def test_summary_empty_data_returns_error(self, da, capsys):
        da.main({"data": [], "op": "summary"})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_summary_negative_numbers(self, da, capsys):
        da.main({"data": [-3, -1, 0, 1, 3], "op": "summary"})
        result = json.loads(capsys.readouterr().out)
        assert result["sum"] == 0
        assert result["min"] == -3
        assert result["max"] == 3
        assert result["avg"] == 0.0

    def test_summary_returns_float_avg(self, da, capsys):
        da.main({"data": [1, 2], "op": "summary"})
        result = json.loads(capsys.readouterr().out)
        assert isinstance(result["avg"], float)
        assert result["avg"] == 1.5

    def test_normalize_basic(self, da, capsys):
        da.main({"data": [10, 20, 30], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        assert result["normalized"] == [0.0, 0.5, 1.0]

    def test_normalize_already_normalized(self, da, capsys):
        da.main({"data": [0, 0.5, 1.0], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        normalized = result["normalized"]
        assert len(normalized) == 3
        assert normalized[0] == pytest.approx(0.0)
        assert normalized[-1] == pytest.approx(1.0)

    def test_normalize_all_same_values_returns_zeros(self, da, capsys):
        """When min == max, all outputs should be 0.0."""
        da.main({"data": [7, 7, 7], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        assert result["normalized"] == [0.0, 0.0, 0.0]

    def test_normalize_all_zeros_returns_zeros(self, da, capsys):
        """Edge case: max == 0, code returns [0.0, ...]."""
        da.main({"data": [0, 0, 0], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        assert result["normalized"] == [0.0, 0.0, 0.0]

    def test_normalize_empty_data_returns_error(self, da, capsys):
        da.main({"data": [], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_normalize_single_element_is_zero(self, da, capsys):
        """Single element: min == max, returns [0.0]."""
        da.main({"data": [99], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        assert result["normalized"] == [0.0]

    def test_unknown_op_returns_error(self, da, capsys):
        da.main({"data": [1, 2, 3], "op": "unknown_op"})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_missing_op_returns_error(self, da, capsys):
        da.main({"data": [1, 2, 3]})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_missing_data_defaults_to_empty(self, da, capsys):
        """When data key is missing, defaults to []; should return error on summary."""
        da.main({"op": "summary"})
        result = json.loads(capsys.readouterr().out)
        assert "error" in result

    def test_normalize_two_elements(self, da, capsys):
        da.main({"data": [0, 100], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        assert result["normalized"] == [0.0, 1.0]

    def test_normalize_preserves_order(self, da, capsys):
        da.main({"data": [30, 10, 20], "op": "normalize"})
        result = json.loads(capsys.readouterr().out)
        normalized = result["normalized"]
        assert normalized == [pytest.approx(1.0), pytest.approx(0.0), pytest.approx(0.5)]


# ─── Topology Orchestrator Logic ──────────────────────────────────────────────

class TestTopologyOrchestratorLogic:
    """Direct tests for topology-orchestrator.md Python logic."""

    @pytest.fixture
    def to(self):
        return load_skill_module("topology-orchestrator.md")

    def test_valid_chain_two_nodes(self, to, capsys):
        to.main({"chain": ["a", "b"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is True
        assert result["stages"] == 2

    def test_valid_chain_four_nodes(self, to, capsys):
        to.main({"chain": ["data-alchemist", "trust-chain", "circuit-breaker", "topology-orchestrator"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is True
        assert result["stages"] == 4

    def test_cycle_detected_first_repeated(self, to, capsys):
        to.main({"chain": ["a", "b", "a"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is False
        assert result["stages"] == 0

    def test_cycle_at_beginning(self, to, capsys):
        to.main({"chain": ["x", "x", "y"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is False
        assert result["stages"] == 0

    def test_empty_chain(self, to, capsys):
        to.main({"chain": []})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is True
        assert result["stages"] == 0

    def test_single_node_chain(self, to, capsys):
        to.main({"chain": ["solo"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is True
        assert result["stages"] == 1

    def test_missing_chain_defaults_to_empty(self, to, capsys):
        to.main({})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is True
        assert result["stages"] == 0

    def test_all_unique_nodes_valid(self, to, capsys):
        chain = [f"node-{i}" for i in range(10)]
        to.main({"chain": chain})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is True
        assert result["stages"] == 10

    def test_cycle_at_end_of_long_chain(self, to, capsys):
        to.main({"chain": ["a", "b", "c", "d", "e", "c"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is False
        assert result["stages"] == 0

    def test_stages_is_zero_when_cycle_detected(self, to, capsys):
        """stages must be 0 when dag_valid is False."""
        to.main({"chain": ["x", "y", "x"]})
        result = json.loads(capsys.readouterr().out)
        assert result["dag_valid"] is False
        assert result["stages"] == 0


# ─── Trust Chain Logic ────────────────────────────────────────────────────────

class TestTrustChainLogic:
    """Direct tests for trust-chain.md Python logic."""

    @pytest.fixture
    def tc(self):
        return load_skill_module("trust-chain.md")

    def test_produces_sha256_hash(self, tc, capsys):
        tc.main({"agent_id": "agent-1", "data": "hello"})
        result = json.loads(capsys.readouterr().out)
        assert "hash" in result
        assert len(result["hash"]) == 64  # SHA-256 hex digest length
        assert all(c in "0123456789abcdef" for c in result["hash"])

    def test_chain_valid_always_true(self, tc, capsys):
        tc.main({"agent_id": "x", "data": "y"})
        result = json.loads(capsys.readouterr().out)
        assert result["chain_valid"] is True

    def test_agent_id_echoed_in_output(self, tc, capsys):
        tc.main({"agent_id": "my-agent", "data": "payload"})
        result = json.loads(capsys.readouterr().out)
        assert result["agent_id"] == "my-agent"

    def test_deterministic_same_input_same_hash(self, tc, capsys):
        inputs = {"agent_id": "agent-a", "data": "test-data"}
        hashes = []
        for _ in range(3):
            tc.main(inputs)
            result = json.loads(capsys.readouterr().out)
            hashes.append(result["hash"])
        assert hashes[0] == hashes[1] == hashes[2]

    def test_different_agent_id_different_hash(self, tc, capsys):
        tc.main({"agent_id": "agent-1", "data": "same-data"})
        hash1 = json.loads(capsys.readouterr().out)["hash"]

        tc.main({"agent_id": "agent-2", "data": "same-data"})
        hash2 = json.loads(capsys.readouterr().out)["hash"]

        assert hash1 != hash2

    def test_different_data_different_hash(self, tc, capsys):
        tc.main({"agent_id": "same-agent", "data": "data-version-1"})
        hash1 = json.loads(capsys.readouterr().out)["hash"]

        tc.main({"agent_id": "same-agent", "data": "data-version-2"})
        hash2 = json.loads(capsys.readouterr().out)["hash"]

        assert hash1 != hash2

    def test_previous_hash_changes_output(self, tc, capsys):
        tc.main({"agent_id": "a", "data": "d", "previous_hash": ""})
        hash_without = json.loads(capsys.readouterr().out)["hash"]

        tc.main({"agent_id": "a", "data": "d", "previous_hash": "abc123"})
        hash_with = json.loads(capsys.readouterr().out)["hash"]

        assert hash_without != hash_with

    def test_empty_strings_produce_valid_hash(self, tc, capsys):
        tc.main({"agent_id": "", "data": ""})
        result = json.loads(capsys.readouterr().out)
        assert len(result["hash"]) == 64
        assert result["chain_valid"] is True

    def test_missing_keys_use_defaults(self, tc, capsys):
        """Missing agent_id/data/previous_hash default to empty strings."""
        tc.main({})
        result = json.loads(capsys.readouterr().out)
        assert len(result["hash"]) == 64
        assert result["agent_id"] == ""
        assert result["chain_valid"] is True

    def test_hash_matches_manual_sha256(self, tc, capsys):
        """Verify the hash computation matches a manually computed SHA-256."""
        agent_id = "verify-agent"
        data = "verify-data"
        previous_hash = "abc"

        tc.main({"agent_id": agent_id, "data": data, "previous_hash": previous_hash})
        result = json.loads(capsys.readouterr().out)

        # Manually compute expected hash
        hasher = hashlib.sha256()
        hasher.update(agent_id.encode())
        hasher.update(data.encode())
        hasher.update(previous_hash.encode())
        expected = hasher.hexdigest()

        assert result["hash"] == expected

    def test_hash_without_previous_matches_manual(self, tc, capsys):
        agent_id = "no-prev"
        data = "some-data"

        tc.main({"agent_id": agent_id, "data": data})
        result = json.loads(capsys.readouterr().out)

        hasher = hashlib.sha256()
        hasher.update(agent_id.encode())
        hasher.update(data.encode())
        expected = hasher.hexdigest()

        assert result["hash"] == expected

    def test_chain_with_chained_previous_hashes(self, tc, capsys):
        """Simulate a real chain: output hash of one becomes previous_hash of next."""
        tc.main({"agent_id": "a1", "data": "block1"})
        hash1 = json.loads(capsys.readouterr().out)["hash"]

        tc.main({"agent_id": "a2", "data": "block2", "previous_hash": hash1})
        hash2 = json.loads(capsys.readouterr().out)["hash"]

        tc.main({"agent_id": "a3", "data": "block3", "previous_hash": hash2})
        hash3 = json.loads(capsys.readouterr().out)["hash"]

        # All hashes should be unique 64-char hex strings
        assert len({hash1, hash2, hash3}) == 3
        assert all(len(h) == 64 for h in [hash1, hash2, hash3])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])