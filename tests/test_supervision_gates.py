"""Tests for supervision gates as data (PROTO-043, contract item 5).

Covers gate parsing in workflow metadata and the doctor check that enforces
structural validity + coverage (release/deploy workflows must declare a gate).
"""

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core.capability_metadata import (
    CapabilityMetadataParser,
    CapabilityType,
    WorkflowMetadata,
    Gate,
)
from proto_gear_pkg.module_core import doctor


def _workflow_dict(gates=None):
    d = {
        "name": "Demo Workflow",
        "type": "workflow",
        "version": "1.0.0",
        "description": "demo",
        "category": "release",
        "tags": ["release"],
        "status": "stable",
        "author": "t",
        "last_updated": "2026-07-09",
        "dependencies": {"required": [], "optional": [], "suggested": []},
        "conflicts": [],
        "composable_with": [],
        "agent_roles": [],
        "workflow": {"steps": 3, "estimated_duration": "1h", "outputs": ["type: release"]},
    }
    if gates is not None:
        d["workflow"]["gates"] = gates
    return d


class TestGateParsing:
    def test_gates_parsed(self):
        m = CapabilityMetadataParser._parse_metadata_dict(_workflow_dict(gates=[
            {"id": "release-approval", "description": "approve before deploy",
             "before": "deploy", "approver": "human", "required": True},
        ]))
        assert len(m.workflow.gates) == 1
        g = m.workflow.gates[0]
        assert isinstance(g, Gate)
        assert g.id == "release-approval"
        assert g.description == "approve before deploy"
        assert g.before == "deploy"
        assert g.approver == "human"
        assert g.required is True

    def test_no_gates_defaults_empty(self):
        m = CapabilityMetadataParser._parse_metadata_dict(_workflow_dict())
        assert m.workflow.gates == []

    def test_gate_defaults(self):
        m = CapabilityMetadataParser._parse_metadata_dict(_workflow_dict(gates=[
            {"id": "g1", "description": "d"},
        ]))
        g = m.workflow.gates[0]
        assert g.approver == "human"
        assert g.required is True
        assert g.before == ""

    def test_malformed_gate_is_lenient(self):
        # Parsing must not crash on a gate missing id/description; doctor flags it.
        m = CapabilityMetadataParser._parse_metadata_dict(_workflow_dict(gates=[
            {"description": "no id here"},
        ]))
        assert m.workflow.gates[0].id == ""
        assert m.workflow.gates[0].description == "no id here"

    def test_to_dict_includes_gates(self):
        m = CapabilityMetadataParser._parse_metadata_dict(_workflow_dict(gates=[
            {"id": "g1", "description": "d"},
        ]))
        wd = m.workflow.to_dict()
        assert "gates" in wd
        assert wd["gates"][0]["id"] == "g1"


def _fake_workflow(outputs, gates):
    wf = WorkflowMetadata(outputs=outputs, gates=gates)
    return SimpleNamespace(type=CapabilityType.WORKFLOW, workflow=wf)


class TestCheckSupervisionGates:
    def test_real_package_is_green(self, tmp_path):
        """The bundled workflows declare their gates; no warnings or errors."""
        findings = doctor.check_supervision_gates(tmp_path)
        assert not any(f.severity == "error" for f in findings)
        assert not any(f.id == "gate-missing" for f in findings)
        ok = [f for f in findings if f.id == "gate-ok"]
        targets = {f.target for f in ok}
        assert "workflows/release" in targets
        assert "workflows/code-review-process" in targets

    def test_risky_output_without_gate_warns(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "proto_gear_pkg.module_core.capability_metadata.load_all_capabilities",
            lambda _d: {"workflows/deployer": _fake_workflow(["type: deployment"], [])},
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert len(findings) == 1
        assert findings[0].id == "gate-missing"
        assert findings[0].severity == "warning"

    def test_non_risky_without_gate_is_silent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "proto_gear_pkg.module_core.capability_metadata.load_all_capabilities",
            lambda _d: {"workflows/docs": _fake_workflow(["type: documentation"], [])},
        )
        assert doctor.check_supervision_gates(tmp_path) == []

    def test_malformed_gate_is_error(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "proto_gear_pkg.module_core.capability_metadata.load_all_capabilities",
            lambda _d: {"workflows/x": _fake_workflow(
                ["type: release"], [Gate(id="", description="")])},
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert any(f.id == "gate-malformed" and f.severity == "error" for f in findings)

    def test_declared_gate_reports_ok(self, tmp_path, monkeypatch):
        monkeypatch.setattr(
            "proto_gear_pkg.module_core.capability_metadata.load_all_capabilities",
            lambda _d: {"workflows/x": _fake_workflow(
                ["type: release"], [Gate(id="g", description="approve")])},
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert [f.id for f in findings] == ["gate-ok"]
