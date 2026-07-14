"""Tests for the init engine — run_simple_protogear_init / setup_agent_framework_only
(PROTO-050 coverage).

Drives a full non-interactive `pg init` in a temp directory across flag
combinations, asserting on the generated files and the returned status. This
exercises the largest untested engine block in proto_gear.py.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import proto_gear as engine


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestRunSimpleInit:
    def test_dry_run_writes_nothing(self, workdir, capsys):
        result = engine.run_simple_protogear_init(dry_run=True, force=True)
        assert result["status"] == "success"
        assert result.get("dry_run")
        assert not (workdir / "AGENTS.md").exists()

    def test_real_init_creates_core_files(self, workdir, capsys):
        result = engine.run_simple_protogear_init(force=True)
        assert result["status"] == "success"
        assert (workdir / "AGENTS.md").exists()
        assert (workdir / "PROJECT_STATUS.md").exists()

    def test_with_branching(self, workdir, capsys):
        engine.run_simple_protogear_init(
            force=True, with_branching=True, ticket_prefix="APP"
        )
        assert (workdir / "BRANCHING.md").exists()

    def test_with_capabilities(self, workdir, capsys):
        engine.run_simple_protogear_init(force=True, with_capabilities=True)
        assert (workdir / ".proto-gear").is_dir()

    def test_with_all_core_templates(self, workdir, capsys):
        engine.run_simple_protogear_init(force=True, with_all=True)
        # --all generates the extended core template set
        assert (workdir / "AGENTS.md").exists()
        assert (workdir / "TESTING.md").exists()

    def test_ticket_prefix_applied_in_branching(self, workdir, capsys):
        engine.run_simple_protogear_init(
            force=True, with_branching=True, ticket_prefix="MYAPP"
        )
        branching = (workdir / "BRANCHING.md").read_text(encoding="utf-8")
        assert "MYAPP" in branching


class TestSetupAgentFrameworkOnly:
    def test_returns_status_dict(self, workdir, capsys):
        result = engine.setup_agent_framework_only(dry_run=True, force=True)
        assert "status" in result
        assert result["status"] == "success"
