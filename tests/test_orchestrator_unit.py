#!/usr/bin/env python3
"""
test_orchestrator_unit.py — Unit tests for orchestrator.py

Tests the orchestrator functions directly without spawning subprocesses,
covering edge cases and error paths not exercised in test_e2e.py.
"""

import json
import os
import sys
import tempfile
import subprocess
from io import StringIO
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock

import pytest

# Add the root to sys.path so we can import orchestrator
ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(ROOT))

import orchestrator


# ─── TestExtractPython ────────────────────────────────────────────────────────

class TestExtractPython:
    """Unit tests for orchestrator.extract_python()"""

    def test_extracts_code_block(self, tmp_path):
        md = tmp_path / "skill.md"
        md.write_text("# Skill\n\n```python\ndef main(inputs):\n    pass\n```\n")
        result = orchestrator.extract_python(md)
        assert result is not None
        assert "def main(inputs):" in result

    def test_returns_none_when_no_python_block(self, tmp_path):
        md = tmp_path / "skill.md"
        md.write_text("# Skill\n\nNo code here.\n")
        result = orchestrator.extract_python(md)
        assert result is None

    def test_extracts_only_first_python_block(self, tmp_path):
        md = tmp_path / "skill.md"
        md.write_text(
            "# Skill\n\n"
            "```python\ndef first():\n    pass\n```\n\n"
            "```python\ndef second():\n    pass\n```\n"
        )
        result = orchestrator.extract_python(md)
        assert "def first():" in result
        # The regex only captures first match
        assert "def second():" not in result

    def test_extracts_multiline_code(self, tmp_path):
        code = "import json\nimport os\n\ndef main(inputs):\n    print('hello')\n"
        md = tmp_path / "skill.md"
        md.write_text(f"# Skill\n\n```python\n{code}```\n")
        result = orchestrator.extract_python(md)
        assert result == code

    def test_non_python_block_not_extracted(self, tmp_path):
        md = tmp_path / "skill.md"
        md.write_text("# Skill\n\n```json\n{\"key\": \"value\"}\n```\n")
        result = orchestrator.extract_python(md)
        assert result is None

    def test_empty_python_block(self, tmp_path):
        md = tmp_path / "skill.md"
        md.write_text("# Skill\n\n```python\n```\n")
        result = orchestrator.extract_python(md)
        # Empty block — regex captures empty string
        assert result == ""

    def test_code_block_with_arabic_content_before(self, tmp_path):
        """Validates extraction works even with Arabic/Unicode text in the markdown."""
        md = tmp_path / "skill.md"
        md.write_text(
            "# مهارة\n\n## الجوهر\nنص عربي هنا.\n\n```python\ndef main(inputs):\n    pass\n```\n"
        )
        result = orchestrator.extract_python(md)
        assert result is not None
        assert "def main(inputs):" in result


# ─── TestGetSkillFile ─────────────────────────────────────────────────────────

class TestGetSkillFile:
    """Unit tests for orchestrator.get_skill_file()"""

    def test_returns_none_when_skills_json_missing(self, tmp_path, monkeypatch):
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", tmp_path / "nonexistent.json")
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)
        result = orchestrator.get_skill_file("some-skill")
        assert result is None

    def test_returns_path_for_known_skill(self, tmp_path, monkeypatch):
        skills_data = {
            "skills": [
                {"name": "my-skill", "file": "skills/my-skill.md", "description": "Test"}
            ]
        }
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        result = orchestrator.get_skill_file("my-skill")
        assert result == tmp_path / "skills/my-skill.md"

    def test_returns_none_for_unknown_skill(self, tmp_path, monkeypatch):
        skills_data = {
            "skills": [
                {"name": "existing-skill", "file": "skills/existing.md", "description": "Test"}
            ]
        }
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        result = orchestrator.get_skill_file("nonexistent-skill")
        assert result is None

    def test_empty_skills_list_returns_none(self, tmp_path, monkeypatch):
        skills_data = {"skills": []}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        result = orchestrator.get_skill_file("any-skill")
        assert result is None

    def test_missing_skills_key_returns_none(self, tmp_path, monkeypatch):
        skills_data = {}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        result = orchestrator.get_skill_file("any-skill")
        assert result is None

    def test_name_match_is_exact(self, tmp_path, monkeypatch):
        """Partial name should not match — name lookup is exact equality."""
        skills_data = {
            "skills": [
                {"name": "trust-chain", "file": "skills/trust-chain.md", "description": "x"}
            ]
        }
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        assert orchestrator.get_skill_file("trust") is None
        assert orchestrator.get_skill_file("trust-chain-extra") is None
        assert orchestrator.get_skill_file("trust-chain") == tmp_path / "skills/trust-chain.md"


# ─── TestListSkills ───────────────────────────────────────────────────────────

class TestListSkills:
    """Unit tests for orchestrator.list_skills()"""

    def test_prints_skill_names(self, tmp_path, monkeypatch, capsys):
        skills_data = {
            "skills": [
                {"name": "skill-a", "file": "skills/a.md", "description": "A"},
                {"name": "skill-b", "file": "skills/b.md", "description": "B"},
            ]
        }
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)

        orchestrator.list_skills()
        captured = capsys.readouterr()
        lines = captured.out.strip().split("\n")
        assert "skill-a" in lines
        assert "skill-b" in lines

    def test_prints_empty_bracket_when_json_missing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", tmp_path / "nonexistent.json")
        orchestrator.list_skills()
        captured = capsys.readouterr()
        assert captured.out.strip() == "[]"

    def test_single_skill_output(self, tmp_path, monkeypatch, capsys):
        skills_data = {"skills": [{"name": "only-one", "file": "skills/only-one.md", "description": "x"}]}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)

        orchestrator.list_skills()
        captured = capsys.readouterr()
        assert captured.out.strip() == "only-one"

    def test_empty_skills_list_produces_empty_output(self, tmp_path, monkeypatch, capsys):
        skills_data = {"skills": []}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)

        orchestrator.list_skills()
        captured = capsys.readouterr()
        assert captured.out.strip() == ""


# ─── TestRunSkill ─────────────────────────────────────────────────────────────

class TestRunSkill:
    """Unit tests for orchestrator.run_skill()"""

    def test_unknown_skill_prints_error_json(self, tmp_path, monkeypatch, capsys):
        skills_data = {"skills": []}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        orchestrator.run_skill("nonexistent", "{}")
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is False
        assert "nonexistent" in result["stderr"]
        assert result["stdout"] == ""

    def test_skill_file_with_no_python_block(self, tmp_path, monkeypatch, capsys):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "no-python.md"
        skill_file.write_text("# No Python\n\nJust some text.\n")

        skills_data = {"skills": [{"name": "no-python", "file": "skills/no-python.md", "description": "x"}]}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        orchestrator.run_skill("no-python", "{}")
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is False
        assert "No python code" in result["stderr"]

    def test_successful_skill_execution(self, tmp_path, monkeypatch, capsys):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "hello.md"
        skill_file.write_text(
            "# Hello\n\n```python\nimport json\ndef main(inputs):\n    print(json.dumps({'ok': True}))\n```\n"
        )
        skills_data = {"skills": [{"name": "hello", "file": "skills/hello.md", "description": "x"}]}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        orchestrator.run_skill("hello", "{}")
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is True
        inner = json.loads(result["stdout"].strip())
        assert inner["ok"] is True

    def test_skill_with_syntax_error_returns_failure(self, tmp_path, monkeypatch, capsys):
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "broken.md"
        skill_file.write_text(
            "# Broken\n\n```python\ndef main(inputs):\n    this is not valid python !!!\n```\n"
        )
        skills_data = {"skills": [{"name": "broken", "file": "skills/broken.md", "description": "x"}]}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        orchestrator.run_skill("broken", "{}")
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is False
        assert result["stderr"] != ""

    def test_skill_receives_inputs(self, tmp_path, monkeypatch, capsys):
        """Validates that inputs_json is correctly passed to the skill's main()."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "echo.md"
        skill_file.write_text(
            "# Echo\n\n```python\nimport json\ndef main(inputs):\n    print(json.dumps({'received': inputs.get('value')}))\n```\n"
        )
        skills_data = {"skills": [{"name": "echo", "file": "skills/echo.md", "description": "x"}]}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        orchestrator.run_skill("echo", '{"value": 42}')
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["success"] is True
        inner = json.loads(result["stdout"].strip())
        assert inner["received"] == 42

    def test_temp_file_is_cleaned_up_after_execution(self, tmp_path, monkeypatch):
        """Verifies the temp file is removed even on successful execution."""
        skills_dir = tmp_path / "skills"
        skills_dir.mkdir()
        skill_file = skills_dir / "clean.md"
        skill_file.write_text(
            "# Clean\n\n```python\nimport json\ndef main(inputs):\n    print(json.dumps({'done': True}))\n```\n"
        )
        skills_data = {"skills": [{"name": "clean", "file": "skills/clean.md", "description": "x"}]}
        json_path = tmp_path / "skills.json"
        json_path.write_text(json.dumps(skills_data))
        monkeypatch.setattr(orchestrator, "SKILLS_JSON", json_path)
        monkeypatch.setattr(orchestrator, "ROOT", tmp_path)

        import glob
        before = set(glob.glob("/tmp/tmp*.py"))
        orchestrator.run_skill("clean", "{}")
        after = set(glob.glob("/tmp/tmp*.py"))
        # No new temp files should persist
        assert after == before or not (after - before)


# ─── TestCLIDispatch ──────────────────────────────────────────────────────────

class TestCLIDispatch:
    """Tests for the CLI dispatch in orchestrator __main__"""

    def _run_orch(self, args, timeout=10):
        orch_path = ROOT / "orchestrator.py"
        return subprocess.run(
            [sys.executable, str(orch_path)] + args,
            capture_output=True, text=True, timeout=timeout
        )

    def test_no_args_exits_with_error(self):
        result = self._run_orch([])
        assert result.returncode != 0

    def test_list_command_returns_zero(self):
        result = self._run_orch(["list"])
        assert result.returncode == 0

    def test_run_with_missing_args_exits_with_error(self):
        # run requires skill_name and inputs_json
        result = self._run_orch(["run", "trust-chain"])
        assert result.returncode != 0

    def test_run_unknown_skill(self):
        result = self._run_orch(["run", "definitely-not-a-real-skill", "{}"])
        assert result.returncode == 0  # orchestrator exits 0 but prints error JSON
        output = json.loads(result.stdout)
        assert output["success"] is False

    def test_chain_command_prints_skill_names(self):
        result = self._run_orch(["chain", "skill-alpha", "skill-beta"])
        assert result.returncode == 0
        assert "skill-alpha" in result.stdout
        assert "skill-beta" in result.stdout

    def test_chain_single_skill(self):
        result = self._run_orch(["chain", "only-one"])
        assert result.returncode == 0
        assert "only-one" in result.stdout

    def test_chain_no_skills_produces_no_output(self):
        result = self._run_orch(["chain"])
        assert result.returncode == 0
        assert result.stdout.strip() == ""

    def test_unknown_command_produces_no_crash(self):
        # Undefined commands fall through silently
        result = self._run_orch(["bogus-command"])
        assert result.returncode == 0


# ─── TestExtractPythonEdgeCases ───────────────────────────────────────────────

class TestExtractPythonRealSkills:
    """Validate extract_python works on the actual skill files modified in this PR."""

    @pytest.mark.parametrize("skill_filename", [
        "circuit-breaker.md",
        "data-alchemist.md",
        "topology-orchestrator.md",
        "trust-chain.md",
    ])
    def test_skill_has_extractable_python(self, skill_filename):
        path = ROOT / "skills" / skill_filename
        assert path.exists(), f"Skill file missing: {skill_filename}"
        result = orchestrator.extract_python(path)
        assert result is not None, f"No python block found in {skill_filename}"
        assert "def main" in result, f"No main() function in {skill_filename}"
        assert len(result.strip()) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])