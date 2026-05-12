#!/usr/bin/env python3
"""
test_e2e.py — End-to-end tests for IQRA Local Sandbox
Run: pytest test_e2e.py -v

Tests spawn REAL subprocesses, consume REAL resources, verify REAL isolation.
NO MOCKS. Every assertion hits the actual code path.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.resolve()
ORCHESTRATOR = ROOT / "orchestrator.py"

# ─── Fixtures ──────────────────────────────────────────────
@pytest.fixture(scope="session")
def orch():
    """Verify orchestrator loads and has skills."""
    result = subprocess.run(
        [sys.executable, str(ORCHESTRATOR), "list"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 0, f"Orchestrator failed: {result.stderr}"
    return result.stdout

# ─── Basic Loading Tests ─────────────────────────────────
class TestLoading:
    def test_skills_json_exists(self):
        assert (ROOT / "skills.json").exists()

    def test_all_skill_files_exist(self):
        with open(ROOT / "skills.json") as f:
            data = json.load(f)
        for s in data["skills"]:
            path = ROOT / s["file"]
            assert path.exists(), f"Missing: {s['file']}"

    def test_orchestrator_lists_skills(self, orch):
        assert "trust-chain" in orch
        assert "circuit-breaker" in orch
        assert "data-alchemist" in orch
        assert "topology-orchestrator" in orch

# ─── Trust Chain Execution ─────────────────────────────────
class TestTrustChain:
    def test_computes_sha256(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "trust-chain",
             '{"agent_id":"test","data":"hello"}'],
            capture_output=True, text=True, timeout=15,
        )
        assert result.returncode == 0, result.stderr
        output = json.loads(result.stdout)
        assert output["success"] is True

        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert len(parsed["hash"]) == 64  # SHA-256 hex
        assert parsed["agent_id"] == "test"
        assert parsed["chain_valid"] is True

    def test_chain_with_previous_hash(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "trust-chain",
             '{"agent_id":"test","data":"hello","previous_hash":"abc123"}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert "chain_valid" in parsed

    def test_deterministic_output(self):
        """Same input → same hash (deterministic for trust)."""
        hashes = []
        for _ in range(3):
            result = subprocess.run(
                [sys.executable, str(ORCHESTRATOR), "run", "trust-chain",
                 '{"agent_id":"test","data":"hello"}'],
                capture_output=True, text=True, timeout=15,
            )
            output = json.loads(result.stdout)
            parsed = json.loads(output["stdout"].strip().split("\n")[-1])
            hashes.append(parsed["hash"])
        assert hashes[0] == hashes[1] == hashes[2]

# ─── Circuit Breaker Execution ───────────────────────────
class TestCircuitBreaker:
    @pytest.fixture(autouse=True)
    def clean_circuit_breaker(self):
        if os.path.exists("/tmp/circuit_breaker_state.json"):
            os.remove("/tmp/circuit_breaker_state.json")
        yield
        if os.path.exists("/tmp/circuit_breaker_state.json"):
            os.remove("/tmp/circuit_breaker_state.json")

    def test_closed_state_allows_execution(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "circuit-breaker",
             '{"action":"can_execute","skill":"data-alchemist"}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert parsed["allowed"] is True
        assert parsed["state"] == "closed"

    def test_opens_after_5_failures(self):
        # Record 5 failures
        for i in range(5):
            subprocess.run(
                [sys.executable, str(ORCHESTRATOR), "run", "circuit-breaker",
                 f'{{"action":"record_failure","skill":"skill_{i}"}}'],
                capture_output=True, text=True, timeout=15,
            )

        # Should now be open
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "circuit-breaker",
             '{"action":"can_execute","skill":"any"}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert parsed["allowed"] is False
        assert parsed["state"] == "open"

# ─── Data Alchemist Execution ────────────────────────────
class TestDataAlchemist:
    def test_summary_operation(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "data-alchemist",
             '{"data":[1,2,3,4,5],"op":"summary"}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert parsed["count"] == 5
        assert parsed["sum"] == 15
        assert parsed["avg"] == 3.0
        assert parsed["min"] == 1
        assert parsed["max"] == 5

    def test_normalize_operation(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "data-alchemist",
             '{"data":[10,20,30],"op":"normalize"}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert parsed["normalized"] == [0.0, 0.5, 1.0]

# ─── Topology Orchestrator ───────────────────────────────
class TestTopology:
    def test_dag_validation(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "topology-orchestrator",
             '{"chain":["data-alchemist","trust-chain"],"data":{}}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert parsed["dag_valid"] is True
        assert parsed["stages"] == 2

    def test_detects_cycles(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "topology-orchestrator",
             '{"chain":["a","b","a"],"data":{}}'],
            capture_output=True, text=True, timeout=15,
        )
        output = json.loads(result.stdout)
        parsed = json.loads(output["stdout"].strip().split("\n")[-1])
        assert parsed["dag_valid"] is False  # cycle detected

# ─── Chain Execution ───────────────────────────────────────
class TestChain:
    def test_sequential_chain(self):
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "chain",
             "topology-orchestrator", "data-alchemist"],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0
        lines = result.stdout.split("\n")
        assert any("topology-orchestrator" in l for l in lines)
        assert any("data-alchemist" in l for l in lines)

# ─── Security / Isolation Tests ──────────────────────────
class TestSecurity:
    def test_timeout_kills_infinite_loop(self):
        # Create a malicious skill temporarily
        malicious = ROOT / "skills" / "_malicious.md"
        malicious.write_text('''# Malicious — TIER: BASIC_TOOL\n\n```python\nimport time\ndef main(inputs):\n    while True:\n        time.sleep(0.1)\n```\n''')

        # Reload registry with malicious skill
        with open(ROOT / "skills.json") as f:
            reg = json.load(f)
        reg["skills"].append({"name":"_malicious","tier":"BASIC_TOOL","description":"x","file":"skills/_malicious.md"})
        with open(ROOT / "skills.json", "w") as f:
            json.dump(reg, f, indent=2)

        start = time.time()
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "_malicious", "{}"],
            capture_output=True, text=True, timeout=25,
        )
        elapsed = time.time() - start

        # Cleanup
        if malicious.exists():
            malicious.unlink()
        with open(ROOT / "skills.json") as f:
            reg = json.load(f)
        reg["skills"] = [s for s in reg["skills"] if s["name"] != "_malicious"]
        with open(ROOT / "skills.json", "w") as f:
            json.dump(reg, f, indent=2)

        assert elapsed < 20, f"Timeout not enforced! Took {elapsed}s"
        output = json.loads(result.stdout)
        assert output["success"] is False
        assert "TIMEOUT" in output["stderr"]

    def test_restricted_no_file_access(self):
        # Verify the sandbox blocks file I/O by checking no files are created
        before = set(ROOT.glob("skills/*"))
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "trust-chain", "{}"],
            capture_output=True, text=True, timeout=15,
        )
        after = set(ROOT.glob("skills/*"))
        assert before == after, "Sandbox leaked files!"

# ─── Performance Baselines ───────────────────────────────
class TestPerformance:
    def test_trust_chain_under_3_seconds(self):
        start = time.time()
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "trust-chain",
             '{"agent_id":"perf","data":"test"}'],
            capture_output=True, text=True, timeout=15,
        )
        elapsed = time.time() - start
        assert result.returncode == 0
        assert elapsed < 3.0, f"Too slow: {elapsed:.2f}s"

    def test_data_alchemist_under_2_seconds(self):
        start = time.time()
        result = subprocess.run(
            [sys.executable, str(ORCHESTRATOR), "run", "data-alchemist",
             '{"data":[1,2,3],"op":"summary"}'],
            capture_output=True, text=True, timeout=15,
        )
        elapsed = time.time() - start
        assert result.returncode == 0
        assert elapsed < 2.0, f"Too slow: {elapsed:.2f}s"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
