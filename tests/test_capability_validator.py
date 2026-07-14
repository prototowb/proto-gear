"""Tests for CapabilityValidator, relevance matching, and discovery fallback
(PROTO-050 coverage)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core.capability_metadata import (
    CapabilityMetadata,
    CapabilityType,
    CapabilityStatus,
    CapabilityDependencies,
    CapabilityRelevance,
    CapabilityValidator,
    WorkflowMetadata,
)
from proto_gear_pkg.module_core import discovery
from proto_gear_pkg.module_core.capability_metadata import load_all_capabilities


def _meta(**kw):
    defaults = dict(
        name="X",
        type=CapabilityType.SKILL,
        version="1.0.0",
        description="d",
        category="c",
        tags=["t"],
        status=CapabilityStatus.STABLE,
        author="a",
        last_updated="2026-01-01",
        dependencies=CapabilityDependencies(),
        conflicts=[],
        composable_with=[],
        agent_roles=["r"],
    )
    defaults.update(kw)
    return CapabilityMetadata(**defaults)


class TestValidateMetadata:
    def test_clean_metadata_has_only_soft_warnings(self):
        m = _meta(tags=["t"], agent_roles=["r"])
        assert CapabilityValidator.validate_metadata(m) == []

    def test_empty_required_fields_warn(self):
        m = _meta(name="", description="", category="")
        warns = CapabilityValidator.validate_metadata(m)
        assert any("Name" in w for w in warns)
        assert any("Description" in w for w in warns)
        assert any("Category" in w for w in warns)

    def test_workflow_without_metadata_warns(self):
        m = _meta(type=CapabilityType.WORKFLOW, tags=["t"], agent_roles=["r"])
        warns = CapabilityValidator.validate_metadata(m)
        assert any("no workflow metadata" in w for w in warns)

    def test_workflow_zero_steps_warns(self):
        m = _meta(
            type=CapabilityType.WORKFLOW,
            tags=["t"],
            agent_roles=["r"],
            workflow=WorkflowMetadata(steps=0),
        )
        warns = CapabilityValidator.validate_metadata(m)
        assert any("0 steps" in w for w in warns)

    def test_command_without_metadata_warns(self):
        m = _meta(type=CapabilityType.COMMAND, tags=["t"], agent_roles=["r"])
        warns = CapabilityValidator.validate_metadata(m)
        assert any("no command metadata" in w for w in warns)


class TestToDict:
    def test_workflow_to_dict_includes_type_fields(self):
        from proto_gear_pkg.module_core.capability_metadata import CommandMetadata

        wf = _meta(type=CapabilityType.WORKFLOW, workflow=WorkflowMetadata(steps=3))
        d = wf.to_dict()
        assert d["type"] == "workflow"
        assert d["status"] == "stable"
        assert "workflow" in d

        cmd = _meta(type=CapabilityType.COMMAND, command=CommandMetadata())
        assert cmd.to_dict()["type"] == "command"


class TestValidateDependencies:
    def test_missing_dependency_is_error(self):
        m = _meta(dependencies=CapabilityDependencies(required=["skills/ghost"]))
        errors = CapabilityValidator.validate_dependencies("skills/x", m, {})
        assert any("not found" in e for e in errors)

    def test_present_dependency_ok(self):
        dep = _meta(name="Dep")
        m = _meta(dependencies=CapabilityDependencies(required=["skills/dep"]))
        errors = CapabilityValidator.validate_dependencies(
            "skills/x", m, {"skills/dep": dep}
        )
        assert errors == []


class TestRelevanceMatching:
    def test_matches_trigger_substring(self):
        r = CapabilityRelevance(triggers=["write tests", "tdd"])
        assert r.matches_trigger("tdd")
        assert r.matches_trigger("please write tests now")
        assert not r.matches_trigger("deploy")


class TestDiscoveryFallback:
    def test_project_caps_preferred_when_present(self, tmp_path, monkeypatch):
        # A project-local .proto-gear with a capability should win over package.
        caps = tmp_path / ".proto-gear" / "skills" / "custom"
        caps.mkdir(parents=True)
        (caps / "metadata.yaml").write_text(
            'name: "Custom"\ntype: "skill"\nversion: "1.0.0"\n'
            'description: "d"\ncategory: "c"\ntags: ["custom"]\n'
            'status: "stable"\nauthor: "me"\nlast_updated: "2026-01-01"\n',
            encoding="utf-8",
        )
        result = discovery.load_capabilities_for_suggest(tmp_path)
        assert "skills/custom" in result

    def test_falls_back_to_package(self, tmp_path):
        # No project .proto-gear → package catalog is used.
        result = discovery.load_capabilities_for_suggest(tmp_path)
        assert any(cid.startswith("skills/") for cid in result)


class TestLoadAllCapabilities:
    def test_command_capability_and_bad_file(self, tmp_path, capsys):
        good = tmp_path / "commands" / "make-thing"
        good.mkdir(parents=True)
        (good / "metadata.yaml").write_text(
            'name: "Make Thing"\ntype: "command"\nversion: "1.0.0"\n'
            'description: "d"\ncategory: "c"\ntags: ["x"]\nstatus: "stable"\n'
            'author: "a"\nlast_updated: "2026-01-01"\n'
            "command:\n  idempotent: true\n  side_effects: []\n",
            encoding="utf-8",
        )
        bad = tmp_path / "skills" / "broken"
        bad.mkdir(parents=True)
        (bad / "metadata.yaml").write_text("name: only-a-name\n", encoding="utf-8")

        caps = load_all_capabilities(tmp_path)
        # The command loaded; the broken one was skipped with a warning.
        assert "commands/make-thing" in caps
        assert caps["commands/make-thing"].command is not None
        assert "skills/broken" not in caps
        assert "Warning" in capsys.readouterr().out
