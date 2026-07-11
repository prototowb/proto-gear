"""Tests for the bundled Security/AppSec module (PROTO-063).

The fourth engineering-discipline module — the standing proof that the whole
department seam (discovery, listings, on-disk install, per-module INDEX, gate
audit, agents, `pg pipeline`, `pg trace` + gate checklist) generalises to an
*arbitrary* discipline. Adding it required **zero** edits to `module_core/`,
`cli/`, or `doctor`. Its `security-signoff` gate guards `release` alongside qa's
`qa-signoff`, creating a new cross-discipline convergence point automatically.
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
from proto_gear_pkg.module_core import doctor, module_host, pipeline, trace


def _args(**kw):
    return argparse.Namespace(**kw)


class TestBundledSecurityModule:
    def test_discoverable(self):
        by_id = {m.module: m for m in discover_modules()}
        assert "security" in by_id
        s = by_id["security"]
        assert s.name == "Security / AppSec"
        assert s.state_surface == "SECURITY_QUEUE.md"

    def test_four_disciplines_coexist(self):
        ids = {m.module for m in discover_modules()}
        assert {"engineering", "qa", "devops", "security"} <= ids

    def test_manifest_has_state_surface_template(self):
        d = default_modules_root() / "security"
        assert (d / "module.yaml").is_file()
        assert (d / "SECURITY_QUEUE.template.md").is_file()


class TestSecuritySurfaceValidation:
    def test_surfaces_present_in_synthetic_host(self, tmp_path):
        s = {m.module: m for m in discover_modules()}["security"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        (tmp_path / "SECURITY_QUEUE.md").write_text("x", encoding="utf-8")
        (tmp_path / "SESSION_HANDOFF.md").write_text("x", encoding="utf-8")
        assert validate_manifest_surfaces(s, tmp_path) == []


class TestDoctorAcceptsSecurityModule:
    def test_manifest_reported_valid(self):
        findings = doctor.check_modules(Path.cwd())
        by_target = {f.target: f for f in findings}
        target = "modules/security/module.yaml"
        assert target in by_target
        assert by_target[target].id == "module-manifest-valid"

    def test_security_gate_is_ok(self, tmp_path):
        findings = doctor.check_supervision_gates(tmp_path)
        ok = {f.target for f in findings if f.id == "gate-ok"}
        assert "security/workflows/security-review" in ok
        assert not any(f.severity == "error" for f in findings)


class TestSecurityListedAndInstalled:
    def test_bundled_loader_includes_security_namespaced(self):
        caps = module_host.load_bundled_capabilities()
        assert "security/workflows/security-review" in caps

    def test_suggest_finds_security_review(self, tmp_path):
        from proto_gear_pkg.module_core import discovery

        results = discovery.suggest(tmp_path, "clear security for release")
        assert any(r["id"] == "security/workflows/security-review" for r in results)

    def test_copy_installs_security_subtree(self, tmp_path):
        from proto_gear_pkg.modules.engineering.templates import (
            copy_capability_templates,
        )
        from proto_gear_pkg.module_core.capability_metadata import (
            load_all_capabilities,
        )

        copy_capability_templates(tmp_path, project_name="demo", version="9.9.9")
        pg = tmp_path / ".proto-gear"
        assert (
            pg / "security" / "workflows" / "security-review" / "WORKFLOW.md"
        ).is_file()
        assert "security/workflows/security-review" in load_all_capabilities(pg)


class TestSecurityJoinsOrchestration:
    """The 4th discipline lights up pipeline + trace + checklist automatically."""

    def test_release_is_a_qa_security_convergence(self):
        stages = pipeline.build_pipeline()
        release = next(s for s in stages if s["action"] == "release")
        disciplines = {g["discipline"] for g in release["gates"]}
        assert {"qa", "security"} <= disciplines

    def _write_surfaces(self, root: Path):
        (root / "PROJECT_STATUS.md").write_text(
            "| ID | Title | Type | Status | Branch | Assignee |\n"
            "|----|-------|------|--------|--------|----------|\n"
            "| PROTO-054 | x | feature | DONE | - | towb |\n",
            encoding="utf-8",
        )
        (root / "SECURITY_QUEUE.md").write_text(
            "| ID | Ref | Finding | Severity | Stage | Owner | Signed off by | Target |\n"
            "|----|-----|---------|----------|-------|-------|---------------|--------|\n"
            "| SEC-001 | PROTO-054 | XSS | high | signed-off | dana | dana | v0.11 |\n",
            encoding="utf-8",
        )

    def test_trace_includes_security(self, tmp_path):
        self._write_surfaces(tmp_path)
        hits = {h["discipline"]: h for h in trace.trace_change("PROTO-054", tmp_path)}
        assert hits["security"]["id"] == "SEC-001"
        assert hits["security"]["approval_state"] == "cleared"

    def test_gate_checklist_evidences_security_signoff(self, tmp_path):
        self._write_surfaces(tmp_path)
        by_gate = {
            g["gate"]: g["status"] for g in trace.gate_checklist("PROTO-054", tmp_path)
        }
        assert by_gate["security-signoff"] == "cleared"


class TestSecurityViaCLI:
    def test_module_show_security(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(_args(name="security", json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert data["module"] == "security"
        assert data["state_surface"] == "SECURITY_QUEUE.md"

    def test_init_surface_writes_queue_verbatim(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(
            _args(module="security", force=False, dry_run=False)
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Created SECURITY_QUEUE.md" in out
        queue = (tmp_path / "SECURITY_QUEUE.md").read_text(encoding="utf-8")
        assert "SECURITY_QUEUE — Findings & Remediations" in queue
        assert "{{" not in queue
