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
    GATE_AUTHORITY_LADDER,
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
        "workflow": {
            "steps": 3,
            "estimated_duration": "1h",
            "outputs": ["type: release"],
        },
    }
    if gates is not None:
        d["workflow"]["gates"] = gates
    return d


class TestGateParsing:
    def test_gates_parsed(self):
        m = CapabilityMetadataParser._parse_metadata_dict(
            _workflow_dict(
                gates=[
                    {
                        "id": "release-approval",
                        "description": "approve before deploy",
                        "before": "deploy",
                        "approver": "human",
                        "required": True,
                    },
                ]
            )
        )
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
        m = CapabilityMetadataParser._parse_metadata_dict(
            _workflow_dict(
                gates=[
                    {"id": "g1", "description": "d"},
                ]
            )
        )
        g = m.workflow.gates[0]
        assert g.approver == "human"
        assert g.required is True
        assert g.before == ""

    def test_malformed_gate_is_lenient(self):
        # Parsing must not crash on a gate missing id/description; doctor flags it.
        m = CapabilityMetadataParser._parse_metadata_dict(
            _workflow_dict(
                gates=[
                    {"description": "no id here"},
                ]
            )
        )
        assert m.workflow.gates[0].id == ""
        assert m.workflow.gates[0].description == "no id here"

    def test_adr002_defaults_preserve_section4(self):
        """actor/authority default to unassigned/human — corpus unchanged."""
        m = CapabilityMetadataParser._parse_metadata_dict(
            _workflow_dict(gates=[{"id": "g1", "description": "d"}])
        )
        g = m.workflow.gates[0]
        assert g.actor == ""
        assert g.authority == "human"

    def test_actor_and_authority_parsed(self):
        m = CapabilityMetadataParser._parse_metadata_dict(
            _workflow_dict(
                gates=[
                    {
                        "id": "qa-signoff",
                        "description": "d",
                        "actor": "qa/qa-release-agent",
                        "authority": "human-on-recommendation",
                        "evidence": "Signed off by",
                    },
                ]
            )
        )
        g = m.workflow.gates[0]
        assert g.actor == "qa/qa-release-agent"
        assert g.authority == "human-on-recommendation"

    def test_authority_ladder_excludes_deferred_agent_rung(self):
        """ADR-002 PROTO-069 amendment: no `agent` clearing rung in the contract."""
        assert "agent" not in GATE_AUTHORITY_LADDER
        assert GATE_AUTHORITY_LADDER == ("human", "human-on-recommendation", "auto")

    def test_to_dict_includes_gates(self):
        m = CapabilityMetadataParser._parse_metadata_dict(
            _workflow_dict(
                gates=[
                    {"id": "g1", "description": "d"},
                ]
            )
        )
        wd = m.workflow.to_dict()
        assert "gates" in wd
        assert wd["gates"][0]["id"] == "g1"
        assert wd["gates"][0]["actor"] == ""
        assert wd["gates"][0]["authority"] == "human"


def _fake_workflow(outputs, gates):
    wf = WorkflowMetadata(outputs=outputs, gates=gates)
    return SimpleNamespace(type=CapabilityType.WORKFLOW, workflow=wf)


def _single_source(monkeypatch, tmp_path, caps):
    """Pin gate auditing to one fake capability source returning ``caps``.

    check_supervision_gates iterates every bundled source (shared root + each
    module's capabilities/); these unit tests want the gate *logic* in isolation,
    so we collapse to a single source and feed it a controlled capability dict.
    """
    monkeypatch.setattr(
        "proto_gear_pkg.module_core.module_host.iter_capability_sources",
        lambda modules_root=None: [(None, tmp_path)],
    )
    monkeypatch.setattr(
        "proto_gear_pkg.module_core.capability_metadata.load_all_capabilities",
        lambda _d: caps,
    )


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
        _single_source(
            monkeypatch,
            tmp_path,
            {"workflows/deployer": _fake_workflow(["type: deployment"], [])},
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert len(findings) == 1
        assert findings[0].id == "gate-missing"
        assert findings[0].severity == "warning"

    def test_non_risky_without_gate_is_silent(self, tmp_path, monkeypatch):
        _single_source(
            monkeypatch,
            tmp_path,
            {"workflows/docs": _fake_workflow(["type: documentation"], [])},
        )
        assert doctor.check_supervision_gates(tmp_path) == []

    def test_malformed_gate_is_error(self, tmp_path, monkeypatch):
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"], [Gate(id="", description="")]
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert any(f.id == "gate-malformed" and f.severity == "error" for f in findings)

    def test_declared_gate_reports_ok(self, tmp_path, monkeypatch):
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"], [Gate(id="g", description="approve")]
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert [f.id for f in findings] == ["gate-ok"]

    def test_deferred_agent_authority_is_error(self, tmp_path, monkeypatch):
        """The `agent` clearing rung is deferred (ADR-002 amendment) — rejected."""
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [Gate(id="g", description="d", authority="agent")],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        deferred = [f for f in findings if f.id == "gate-authority-deferred"]
        assert len(deferred) == 1
        assert deferred[0].severity == "error"
        assert "human-on-recommendation" in deferred[0].message

    def test_unknown_authority_is_error(self, tmp_path, monkeypatch):
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [Gate(id="g", description="d", authority="vibes")],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert any(
            f.id == "gate-authority-invalid" and f.severity == "error" for f in findings
        )

    def test_valid_authority_rungs_are_clean(self, tmp_path, monkeypatch):
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [
                        Gate(id="g1", description="d", authority="human"),
                        Gate(
                            id="g2",
                            description="d",
                            authority="human-on-recommendation",
                        ),
                        Gate(
                            id="g3",
                            description="d",
                            authority="auto",
                            evidence="Tests green",
                        ),
                    ],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert [f.id for f in findings] == ["gate-ok"]

    def test_auto_authority_without_evidence_is_error(self, tmp_path, monkeypatch):
        """An auto gate clears by its evidence predicate alone — evidence required."""
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [Gate(id="g", description="d", authority="auto")],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert any(
            f.id == "gate-auto-needs-evidence" and f.severity == "error"
            for f in findings
        )

    def test_known_discipline_agent_actor_is_clean(self, tmp_path, monkeypatch):
        """qa really ships qa-release-agent (PROTO-067) — a valid actor reference."""
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [Gate(id="g", description="d", actor="qa/qa-release-agent")],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert [f.id for f in findings] == ["gate-ok"]

    def test_unknown_namespaced_actor_warns(self, tmp_path, monkeypatch):
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [Gate(id="g", description="d", actor="docs/ghost-agent")],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        unknown = [f for f in findings if f.id == "gate-actor-unknown"]
        assert len(unknown) == 1
        assert unknown[0].severity == "warning"

    def test_human_role_actor_is_not_validated(self, tmp_path, monkeypatch):
        """A non-namespaced actor is a human role, not an agent reference."""
        _single_source(
            monkeypatch,
            tmp_path,
            {
                "workflows/x": _fake_workflow(
                    ["type: release"],
                    [Gate(id="g", description="d", actor="Release Manager")],
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert [f.id for f in findings] == ["gate-ok"]

    def test_module_source_namespaces_target(self, tmp_path, monkeypatch):
        """A gate from a department source is targeted <module>/<cap_id>."""
        monkeypatch.setattr(
            "proto_gear_pkg.module_core.module_host.iter_capability_sources",
            lambda modules_root=None: [("qa", tmp_path)],
        )
        monkeypatch.setattr(
            "proto_gear_pkg.module_core.capability_metadata.load_all_capabilities",
            lambda _d: {
                "workflows/release": _fake_workflow(
                    ["type: release"], [Gate(id="qa-signoff", description="ok")]
                )
            },
        )
        findings = doctor.check_supervision_gates(tmp_path)
        assert [f.target for f in findings] == ["qa/workflows/release"]
