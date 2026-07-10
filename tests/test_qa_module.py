"""Tests for the bundled QA/Test module (PROTO-054, ADR-001 Phase C).

The QA module is the *second* engineering-discipline implementation of the
module contract. Its whole job is to prove the department-agnostic core
discovers, loads, and audits a brand-new discipline through the same interfaces
as engineering — with **zero** edits to ``module_core/``. These tests assert
that against the REAL bundled module (not a tmp_path toy), and additionally that
its own bundled, gated workflow is picked up by the multi-source gate audit
(PROTO-052).
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core.module_manifest import (
    discover_modules,
    validate_manifest_surfaces,
    default_modules_root,
)
from proto_gear_pkg.module_core import doctor, module_host


def _args(**kw):
    return argparse.Namespace(**kw)


class TestBundledQaModule:
    def test_qa_module_is_discoverable(self):
        """discover_modules() finds qa alongside engineering — no core edit."""
        by_id = {m.module: m for m in discover_modules()}
        assert "qa" in by_id, "qa module must be discovered by the core"
        qa = by_id["qa"]
        assert qa.name == "QA / Test"
        assert qa.state_surface == "QA_QUEUE.md"
        assert qa.context_manifest == "AGENT_CONTEXT.md"
        assert qa.handoff == "SESSION_HANDOFF.md"

    def test_qa_and_engineering_coexist(self):
        """The core hosts two independent engineering-discipline modules."""
        ids = {m.module for m in discover_modules()}
        assert {"qa", "engineering"} <= ids

    def test_qa_manifest_has_state_surface_template(self):
        qa_dir = default_modules_root() / "qa"
        assert (qa_dir / "module.yaml").is_file()
        assert (qa_dir / "QA_QUEUE.template.md").is_file()

    def test_qa_manifest_version_and_description(self):
        qa = {m.module: m for m in discover_modules()}["qa"]
        assert qa.version == "0.1.0"
        assert "qa" in qa.description.lower() or "quality" in qa.description.lower()


class TestQaSurfaceValidation:
    def test_surfaces_present_in_synthetic_host(self, tmp_path):
        qa = {m.module: m for m in discover_modules()}["qa"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        (tmp_path / "QA_QUEUE.md").write_text("x", encoding="utf-8")
        (tmp_path / "SESSION_HANDOFF.md").write_text("x", encoding="utf-8")
        assert validate_manifest_surfaces(qa, tmp_path) == []

    def test_missing_qa_queue_is_reported(self, tmp_path):
        qa = {m.module: m for m in discover_modules()}["qa"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        problems = validate_manifest_surfaces(qa, tmp_path)
        assert any("state_surface" in p and "QA_QUEUE.md" in p for p in problems)


class TestDoctorAcceptsQaModule:
    def test_qa_manifest_reported_valid(self):
        findings = doctor.check_modules(Path.cwd())
        by_target = {f.target: f for f in findings}
        target = "modules/qa/module.yaml"
        assert target in by_target, "doctor must audit the qa manifest"
        assert by_target[target].id == "module-manifest-valid"
        assert by_target[target].severity == "ok"

    def test_no_module_manifest_errors(self):
        findings = doctor.check_modules(Path.cwd())
        assert not [f for f in findings if f.severity == "error"]


class TestQaGateAudited:
    """PROTO-052: the qa module's own gated workflow is discovered + audited."""

    def test_release_signoff_gate_is_ok(self, tmp_path):
        findings = doctor.check_supervision_gates(tmp_path)
        ok_targets = {f.target for f in findings if f.id == "gate-ok"}
        assert "qa/workflows/release-signoff" in ok_targets
        # namespaced by module, not colliding with the shared root
        assert not any(f.target == "workflows/release-signoff" for f in findings)
        assert not any(f.severity == "error" for f in findings)

    def test_qa_capabilities_are_a_source(self):
        by_module = {m: p for m, p in module_host.iter_capability_sources()}
        assert "qa" in by_module
        assert (by_module["qa"] / "workflows" / "release-signoff").is_dir()


class TestQaModuleViaCLI:
    def test_module_list_includes_qa(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_list(_args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "qa" in out

    def test_module_show_qa(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(_args(name="qa", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "QA_QUEUE.md" in out
        assert "Contract surfaces" in out

    def test_module_show_qa_json(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(_args(name="qa", json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert data["module"] == "qa"
        assert data["state_surface"] == "QA_QUEUE.md"


class TestQaInitSurface:
    def test_init_surface_writes_queue_verbatim(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(
            _args(module="qa", force=False, dry_run=False)
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Created QA_QUEUE.md" in out
        queue = (tmp_path / "QA_QUEUE.md").read_text(encoding="utf-8")
        assert "QA_QUEUE — Test Plans & Defects" in queue
        # verbatim render — no unresolved placeholders left behind
        assert "{{" not in queue
