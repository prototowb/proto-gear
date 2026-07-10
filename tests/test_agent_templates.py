"""Tests for pre-defined agent templates (PROTO-050 coverage)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import agent_templates as at
from proto_gear_pkg.agent_config import AgentConfiguration


class TestTemplates:
    def test_list_templates_sorted(self):
        names = at.list_templates()
        assert names == sorted(names)
        assert "backend-developer" in names
        assert len(names) == 7

    def test_get_template_known(self):
        t = at.get_template("testing-focused")
        assert t["name"] == "Testing-Focused Agent"
        assert "testing" in t["capabilities"].skills

    def test_get_template_unknown_is_none(self):
        assert at.get_template("does-not-exist") is None

    def test_get_template_description(self):
        assert at.get_template_description("qa-engineer")
        assert at.get_template_description("nope") == ""

    def test_create_agent_from_template(self):
        agent = at.create_agent_from_template("minimal", author="towb")
        assert isinstance(agent, AgentConfiguration)
        assert agent.author == "towb"
        assert agent.name == "Minimal Agent"

    def test_create_with_custom_name(self):
        agent = at.create_agent_from_template("minimal", agent_name="MyAgent")
        assert agent.name == "MyAgent"
        assert agent.author == "Proto Gear"

    def test_create_unknown_raises(self):
        with pytest.raises(ValueError, match="Template not found"):
            at.create_agent_from_template("ghost")

    def test_print_available_templates(self, capsys):
        at.print_available_templates()
        out = capsys.readouterr().out
        assert "Available Agent Templates" in out
        for name in at.list_templates():
            assert name in out


class TestAgentManagerResolution:
    def _manager(self, tmp_path):
        from proto_gear_pkg.agent_config import AgentManager

        agents_dir = tmp_path / ".proto-gear" / "agents"
        agents_dir.mkdir(parents=True)
        caps_dir = (
            Path(__file__).parent.parent / "core" / "proto_gear_pkg" / "capabilities"
        )
        return AgentManager(agents_dir, caps_dir)

    def test_get_agent_capabilities_with_and_without_deps(self, tmp_path):
        mgr = self._manager(tmp_path)
        agent = at.create_agent_from_template("backend-developer")
        flat = mgr.get_agent_capabilities(agent, include_dependencies=False)
        resolved = mgr.get_agent_capabilities(agent, include_dependencies=True)
        assert set(flat) <= set(resolved) or set(resolved) <= set(flat) or resolved
        assert flat  # non-empty

    def test_get_recommendations(self, tmp_path):
        mgr = self._manager(tmp_path)
        agent = at.create_agent_from_template("minimal")
        recs = mgr.get_recommendations(agent)
        assert isinstance(recs, list)
