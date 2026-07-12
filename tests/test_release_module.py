"""Tests for the bundled Release-Management/PM module (PROTO-077).

The fifth engineering-discipline module — added, like qa/devops/security, by
dropping ``modules/release/`` in with **zero** edits to ``module_core/``,
``cli/``, or ``doctor``. It is the first ``modules/`` discipline to declare a
**release-scoped** gate (``go-no-go``, PROTO-066 semantics): its state surface
keys rows by the release *label*, so ``pg release <label>`` evidences the go
decision once for the whole candidate. It also ships its own agent through the
PROTO-067 seam (``release-coordinator-agent``).
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
from proto_gear_pkg.module_core import (
    doctor,
    module_host,
    pipeline,
    trace,
    release as release_trace,
)


def _args(**kw):
    return argparse.Namespace(**kw)


class TestBundledReleaseModule:
    def test_discoverable(self):
        by_id = {m.module: m for m in discover_modules()}
        assert "release" in by_id
        r = by_id["release"]
        assert r.name == "Release Management / PM"
        assert r.state_surface == "RELEASE_QUEUE.md"

    def test_five_disciplines_coexist(self):
        ids = {m.module for m in discover_modules()}
        assert {"engineering", "qa", "devops", "security", "release"} <= ids

    def test_manifest_has_state_surface_template(self):
        d = default_modules_root() / "release"
        assert (d / "module.yaml").is_file()
        assert (d / "RELEASE_QUEUE.template.md").is_file()


class TestReleaseSurfaceValidation:
    def test_surfaces_present_in_synthetic_host(self, tmp_path):
        r = {m.module: m for m in discover_modules()}["release"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        (tmp_path / "RELEASE_QUEUE.md").write_text("x", encoding="utf-8")
        (tmp_path / "SESSION_HANDOFF.md").write_text("x", encoding="utf-8")
        assert validate_manifest_surfaces(r, tmp_path) == []


class TestDoctorAcceptsReleaseModule:
    def test_manifest_reported_valid(self):
        findings = doctor.check_modules(Path.cwd())
        by_target = {f.target: f for f in findings}
        target = "modules/release/module.yaml"
        assert target in by_target
        assert by_target[target].id == "module-manifest-valid"

    def test_go_no_go_gate_is_ok(self, tmp_path):
        findings = doctor.check_supervision_gates(tmp_path)
        ok = {f.target for f in findings if f.id == "gate-ok"}
        assert "release/workflows/go-no-go" in ok
        assert not any(f.severity == "error" for f in findings)


class TestReleaseListedAndInstalled:
    def test_bundled_loader_includes_release_namespaced(self):
        caps = module_host.load_bundled_capabilities()
        assert "release/workflows/go-no-go" in caps

    def test_suggest_finds_go_no_go(self, tmp_path):
        from proto_gear_pkg.module_core import discovery

        results = discovery.suggest(tmp_path, "release readiness decision")
        assert any(r["id"] == "release/workflows/go-no-go" for r in results)

    def test_copy_installs_release_subtree(self, tmp_path):
        from proto_gear_pkg.modules.engineering.templates import (
            copy_capability_templates,
        )
        from proto_gear_pkg.module_core.capability_metadata import (
            load_all_capabilities,
        )

        copy_capability_templates(tmp_path, project_name="demo", version="9.9.9")
        pg = tmp_path / ".proto-gear"
        assert (pg / "release" / "workflows" / "go-no-go" / "WORKFLOW.md").is_file()
        assert "release/workflows/go-no-go" in load_all_capabilities(pg)

    def test_agent_ships_with_the_module(self):
        by_module = {m: p for m, p in module_host.iter_agent_sources()}
        assert "release" in by_module
        records = module_host.list_bundled_agents()
        assert any(
            r["qualified"] == "release/release-coordinator-agent" for r in records
        )


class TestReleaseJoinsOrchestration:
    """The 5th discipline lights up pipeline + trace + release automatically —
    and go-no-go is the first modules/ gate at release scope."""

    def test_release_action_is_a_three_way_convergence(self):
        stages = pipeline.build_pipeline()
        stage = next(s for s in stages if s["action"] == "release")
        disciplines = {g["discipline"] for g in stage["gates"]}
        assert {"qa", "security", "release"} <= disciplines

    def test_go_no_go_is_release_scoped_and_human(self):
        records = pipeline.collect_supervision_gates()
        g = next(r for r in records if r["gate"] == "go-no-go")
        assert g["scope"] == "release"
        assert g["authority"] == "human"  # pure-human, per the ADR-002 posture
        assert g["evidence"] == "Signed off by"

    def _write_surfaces(self, root: Path):
        (root / "PROJECT_STATUS.md").write_text(
            "| ID | Title | Type | Status | Branch | Assignee |\n"
            "|----|-------|------|--------|--------|----------|\n"
            "| PROTO-054 | x | feature | DONE | - | towb |\n",
            encoding="utf-8",
        )
        (root / "RELEASE_QUEUE.md").write_text(
            "| ID | Ref | Stage | Owner | Window | Signed off by |\n"
            "|----|-----|-------|-------|--------|---------------|\n"
            "| v0.11 | PROTO-054 | go | rex | 2026-07-15 | tobias |\n",
            encoding="utf-8",
        )

    def test_trace_shows_the_candidate_a_change_rides_in(self, tmp_path):
        self._write_surfaces(tmp_path)
        hits = {h["discipline"]: h for h in trace.trace_change("PROTO-054", tmp_path)}
        assert hits["release"]["id"] == "v0.11"
        assert hits["release"]["approval_state"] == "cleared"

    def test_pg_release_evidences_go_no_go_once(self, tmp_path):
        # The gate is release-scoped: gate_checklist(label) reads the
        # RELEASE_QUEUE row keyed by the label itself.
        self._write_surfaces(tmp_path)
        by_gate = {g["gate"]: g for g in trace.gate_checklist("v0.11", tmp_path)}
        assert by_gate["go-no-go"]["status"] == "cleared"
        assert by_gate["go-no-go"]["scope"] == "release"
        assert by_gate["go-no-go"]["signed_by"] == ["tobias"]
        assert by_gate["go-no-go"]["authority_ok"] is True

    def test_missing_go_decision_blocks_the_release(self, tmp_path):
        # A candidate with tickets but no go decision is not ready — the
        # discipline's entire point.
        (tmp_path / "PROJECT_STATUS.md").write_text(
            "| ID | Title | Completed | PR/Commit |\n"
            "|----|-------|-----------|-----------|\n"
            "| PROTO-A | first | 2026-07-11 | v0.11 |\n",
            encoding="utf-8",
        )
        report = release_trace.trace_release("v0.11", tmp_path)
        assert report["ready"] is False
        blocking = {g["gate"] for g in report["release_gates"]["blocking"]}
        assert "go-no-go" in blocking


class TestReleaseViaCLI:
    def test_module_show_release(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(_args(name="release", json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert data["module"] == "release"
        assert data["state_surface"] == "RELEASE_QUEUE.md"

    def test_init_surface_writes_queue_verbatim(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(
            _args(module="release", force=False, dry_run=False)
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Created RELEASE_QUEUE.md" in out
        queue = (tmp_path / "RELEASE_QUEUE.md").read_text(encoding="utf-8")
        assert "RELEASE_QUEUE — Release Candidates & Go/No-Go" in queue
        assert "{{" not in queue
