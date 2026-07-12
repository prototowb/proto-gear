"""Tests for pg capabilities / pg agent handlers (PROTO-050 coverage).

The capabilities handlers read the real package capability catalog; the agent
handlers operate on a temp `.proto-gear/agents` directory. All are driven with
argparse.Namespace + capsys, exactly as the CLI dispatch calls them.
"""

import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import cli_commands as cc


def _args(**kw):
    return argparse.Namespace(**kw)


def _cap_args(**kw):
    kw.setdefault("type", None)
    kw.setdefault("tag", None)
    kw.setdefault("role", None)
    kw.setdefault("status", None)
    kw.setdefault("json", False)
    return argparse.Namespace(**kw)


class TestCapabilitiesList:
    def test_list_all(self, capsys):
        rc = cc.cmd_capabilities_list(_cap_args())
        out = capsys.readouterr().out
        assert rc == 0
        assert "Capabilities" in out
        assert "SKILLS" in out and "WORKFLOWS" in out

    def test_filter_type_skill(self, capsys):
        rc = cc.cmd_capabilities_list(_cap_args(type="skill"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "SKILLS" in out
        assert "WORKFLOWS" not in out

    def test_json(self, capsys):
        rc = cc.cmd_capabilities_list(_cap_args(json=True))
        data = json.loads(capsys.readouterr().out)
        assert "capabilities" in data
        assert any(c["type"] == "skill" for c in data["capabilities"])

    def test_filter_tag(self, capsys):
        rc = cc.cmd_capabilities_list(_cap_args(tag="testing"))
        assert rc == 0

    def test_no_match_filter(self, capsys):
        rc = cc.cmd_capabilities_list(_cap_args(tag="zzz-nonexistent-tag"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "No capabilities match" in out

    def test_no_match_json(self, capsys):
        rc = cc.cmd_capabilities_list(_cap_args(status="experimental", json=True))
        # experimental may or may not exist; if empty, prints empty list
        out = capsys.readouterr().out
        assert rc == 0
        json.loads(out)  # valid JSON either way


class TestCapabilitiesSearch:
    def test_match(self, capsys):
        rc = cc.cmd_capabilities_search(_args(query="test"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Search Results" in out

    def test_no_match(self, capsys):
        rc = cc.cmd_capabilities_search(_args(query="zzzznope"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "No capabilities found" in out


class TestCapabilitiesShow:
    def test_show_short_name(self, capsys):
        rc = cc.cmd_capabilities_show(_args(name="testing"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "testing" in out.lower()

    def test_show_full_id(self, capsys):
        rc = cc.cmd_capabilities_show(_args(name="skills/testing"))
        assert rc == 0

    def test_not_found_suggests(self, capsys):
        rc = cc.cmd_capabilities_show(_args(name="testng"))  # typo
        out = capsys.readouterr().out
        assert "not found" in out.lower()
        assert "Did you mean" in out  # fuzzy suggestion

    def test_show_workflow_with_gates_and_deps(self, capsys):
        # A workflow exercises the dependencies / composable / gates detail blocks.
        rc = cc.cmd_capabilities_show(_args(name="release"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Supervision Gates" in out
        assert "release-approval" in out


class TestCapabilitiesTree:
    def test_tree_found(self, capsys):
        rc = cc.cmd_capabilities_tree(_args(capability_id="testing"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Dependency Tree" in out

    def test_tree_not_found(self, capsys):
        rc = cc.cmd_capabilities_tree(_args(capability_id="nope-xyz"))
        out = capsys.readouterr().out
        assert rc == 1
        assert "not found" in out.lower()


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / ".proto-gear" / "agents").mkdir(parents=True)
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _agent_create_args(name=None, **kw):
    kw.setdefault("name", name)
    kw.setdefault("template", None)
    kw.setdefault("capabilities", None)
    kw.setdefault("description", None)
    kw.setdefault("author", None)
    kw.setdefault("list_templates", False)
    return argparse.Namespace(**kw)


class TestAgentCommands:
    def test_list_empty(self, project, capsys):
        rc = cc.cmd_agent_list(_args())
        out = capsys.readouterr().out
        assert rc == 0
        assert "No agents" in out or "agents" in out.lower()

    def test_create_list_templates(self, project, capsys):
        rc = cc.cmd_agent_create(_agent_create_args(list_templates=True))
        out = capsys.readouterr().out
        assert rc == 0
        assert "backend-developer" in out

    def test_create_from_template_then_list_show(self, project, capsys):
        rc = cc.cmd_agent_create(
            _agent_create_args(name="my-backend", template="backend-developer")
        )
        assert rc == 0
        capsys.readouterr()

        rc = cc.cmd_agent_list(_args())
        out = capsys.readouterr().out
        assert rc == 0
        assert "my-backend" in out

        rc = cc.cmd_agent_show(_args(name="my-backend"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "my-backend" in out

    def test_create_quick_from_capabilities(self, project, capsys):
        rc = cc.cmd_agent_create(
            _agent_create_args(name="quicky", capabilities="testing,debugging")
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert (project / ".proto-gear" / "agents" / "quicky.yaml").exists()

    def test_validate(self, project, capsys):
        cc.cmd_agent_create(
            _agent_create_args(name="val-agent", template="qa-engineer")
        )
        capsys.readouterr()
        rc = cc.cmd_agent_validate(_args(name="val-agent", no_recommendations=True))
        assert rc == 0

    def test_clone(self, project, capsys):
        cc.cmd_agent_create(_agent_create_args(name="orig", template="minimal"))
        capsys.readouterr()
        rc = cc.cmd_agent_clone(
            _args(source="orig", destination="copy", description=None)
        )
        assert rc == 0
        assert (project / ".proto-gear" / "agents" / "copy.yaml").exists()

    def test_delete(self, project, capsys):
        cc.cmd_agent_create(_agent_create_args(name="doomed", template="minimal"))
        capsys.readouterr()
        rc = cc.cmd_agent_delete(_args(name="doomed", force=True))
        assert rc == 0
        assert not (project / ".proto-gear" / "agents" / "doomed.yaml").exists()

    def test_show_missing(self, project, capsys):
        rc = cc.cmd_agent_show(_args(name="ghost"))
        assert rc == 1

    def test_validate_with_recommendations(self, project, capsys):
        cc.cmd_agent_create(_agent_create_args(name="rec-agent", template="minimal"))
        capsys.readouterr()
        rc = cc.cmd_agent_validate(_args(name="rec-agent", no_recommendations=False))
        assert rc == 0

    def test_validate_missing(self, project, capsys):
        rc = cc.cmd_agent_validate(_args(name="ghost", no_recommendations=True))
        assert rc == 1

    def test_delete_missing(self, project, capsys):
        rc = cc.cmd_agent_delete(_args(name="ghost", force=True))
        assert rc == 1

    def test_clone_missing_source(self, project, capsys):
        rc = cc.cmd_agent_clone(
            _args(source="ghost", destination="x", description=None)
        )
        assert rc == 1

    def test_show_missing_suggests(self, project, capsys):
        cc.cmd_agent_create(_agent_create_args(name="realagent", template="minimal"))
        capsys.readouterr()
        rc = cc.cmd_agent_show(_args(name="realagen"))  # typo → fuzzy suggest
        out = capsys.readouterr().out
        assert rc == 1
        assert "not found" in out.lower()


class TestAgentSurfacing:
    """PROTO-076: pg agent list surfaces installable bundled agents;
    pg agent install pulls one in on demand."""

    def test_list_shows_available_section_without_agents_dir(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_agent_list(argparse.Namespace(available=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Available bundled agents" in out
        assert "qa-release-agent" in out
        assert "[qa]" in out  # discipline attribution
        assert "pg agent install" in out

    def test_list_available_filter(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_agent_list(argparse.Namespace(available=True))
        out = capsys.readouterr().out
        assert rc == 0
        assert "qa-release-agent" in out
        assert "Configured Agents" not in out

    def test_installed_agents_leave_available_section(
        self, tmp_path, monkeypatch, capsys
    ):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".proto-gear").mkdir()
        rc = cc.cmd_agent_install(argparse.Namespace(name="qa-release-agent"))
        assert rc == 0
        capsys.readouterr()  # flush the install output
        cc.cmd_agent_list(argparse.Namespace(available=True))
        out = capsys.readouterr().out
        assert "qa-release-agent" not in out
        assert "deploy-agent" in out  # others remain available

    def test_install_requires_initialised_host(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)  # no .proto-gear/
        rc = cc.cmd_agent_install(argparse.Namespace(name="qa-release-agent"))
        out = capsys.readouterr().out
        assert rc == 1
        assert "pg init" in out

    def test_install_unknown_agent_fails_with_hint(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".proto-gear").mkdir()
        rc = cc.cmd_agent_install(argparse.Namespace(name="ghost-agent"))
        out = capsys.readouterr().out
        assert rc == 1
        assert "No bundled agent" in out
        assert "--available" in out

    def test_install_writes_agent_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".proto-gear").mkdir()
        rc = cc.cmd_agent_install(argparse.Namespace(name="devops/deploy-agent"))
        assert rc == 0
        assert (tmp_path / ".proto-gear" / "agents" / "deploy-agent.yaml").is_file()
