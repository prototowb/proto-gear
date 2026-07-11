"""Tests for the bundled DevOps/SRE module (PROTO-059).

The DevOps module is the *third* engineering-discipline implementation of the
module contract — the standing proof that everything built for the department
seam (discovery, listings, on-disk install, per-module INDEX, gate audit, agent
visibility) holds for an *arbitrary* discipline, not just the two that shipped
with it. These tests assert that against the REAL bundled module, and that
adding it required **zero** edits to ``module_core/``, ``cli/``, or ``doctor``.
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


class TestBundledDevopsModule:
    def test_devops_module_is_discoverable(self):
        by_id = {m.module: m for m in discover_modules()}
        assert "devops" in by_id, "devops module must be discovered by the core"
        devops = by_id["devops"]
        assert devops.name == "DevOps / SRE"
        assert devops.state_surface == "DEPLOY_QUEUE.md"
        assert devops.context_manifest == "AGENT_CONTEXT.md"
        assert devops.handoff == "SESSION_HANDOFF.md"

    def test_three_disciplines_coexist(self):
        """The core hosts three independent engineering-discipline modules."""
        ids = {m.module for m in discover_modules()}
        assert {"engineering", "qa", "devops"} <= ids

    def test_manifest_has_state_surface_template(self):
        d = default_modules_root() / "devops"
        assert (d / "module.yaml").is_file()
        assert (d / "DEPLOY_QUEUE.template.md").is_file()

    def test_manifest_version_and_description(self):
        devops = {m.module: m for m in discover_modules()}["devops"]
        assert devops.version == "0.1.0"
        assert "devops" in devops.description.lower() or (
            "deploy" in devops.description.lower()
        )


class TestDevopsSurfaceValidation:
    def test_surfaces_present_in_synthetic_host(self, tmp_path):
        devops = {m.module: m for m in discover_modules()}["devops"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        (tmp_path / "DEPLOY_QUEUE.md").write_text("x", encoding="utf-8")
        (tmp_path / "SESSION_HANDOFF.md").write_text("x", encoding="utf-8")
        assert validate_manifest_surfaces(devops, tmp_path) == []

    def test_missing_deploy_queue_is_reported(self, tmp_path):
        devops = {m.module: m for m in discover_modules()}["devops"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        problems = validate_manifest_surfaces(devops, tmp_path)
        assert any("state_surface" in p and "DEPLOY_QUEUE.md" in p for p in problems)


class TestDoctorAcceptsDevopsModule:
    def test_devops_manifest_reported_valid(self):
        findings = doctor.check_modules(Path.cwd())
        by_target = {f.target: f for f in findings}
        target = "modules/devops/module.yaml"
        assert target in by_target, "doctor must audit the devops manifest"
        assert by_target[target].id == "module-manifest-valid"
        assert by_target[target].severity == "ok"

    def test_no_module_manifest_errors(self):
        findings = doctor.check_modules(Path.cwd())
        assert not [f for f in findings if f.severity == "error"]


class TestDevopsGateAudited:
    """The devops deploy workflow's prod-approval gate is discovered + audited."""

    def test_deploy_gate_is_ok(self, tmp_path):
        findings = doctor.check_supervision_gates(tmp_path)
        ok_targets = {f.target for f in findings if f.id == "gate-ok"}
        assert "devops/workflows/deploy" in ok_targets
        # namespaced by module, not colliding with any shared workflow
        assert not any(f.target == "workflows/deploy" for f in findings)
        assert not any(f.severity == "error" for f in findings)

    def test_devops_capabilities_are_a_source(self):
        by_module = {m: p for m, p in module_host.iter_capability_sources()}
        assert "devops" in by_module
        assert (by_module["devops"] / "workflows" / "deploy").is_dir()


class TestDevopsListedAcrossSurfaces:
    """The full S1 pipeline surfaces devops, namespaced devops/workflows/deploy."""

    def test_bundled_loader_includes_devops_namespaced(self):
        caps = module_host.load_bundled_capabilities()
        assert "devops/workflows/deploy" in caps
        assert "workflows/deploy" not in caps  # no bare leak

    def test_suggest_finds_deploy(self, tmp_path):
        from proto_gear_pkg.module_core import discovery

        results = discovery.suggest(tmp_path, "promote this change to production")
        assert any(r["id"] == "devops/workflows/deploy" for r in results)

    def test_capabilities_list_shows_devops(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_capabilities_list(_args(json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        ids = {c["id"] for c in data["capabilities"]}
        assert "devops/workflows/deploy" in ids

    def test_capabilities_show_resolves_bare_name(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_capabilities_show(_args(name="deploy"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Production Deploy" in out


class TestDevopsInstalledOnDisk:
    def test_copy_installs_devops_subtree(self, tmp_path):
        from proto_gear_pkg.modules.engineering.templates import (
            copy_capability_templates,
        )
        from proto_gear_pkg.module_core.capability_metadata import (
            load_all_capabilities,
        )

        res = copy_capability_templates(tmp_path, project_name="demo", version="9.9.9")
        assert res["status"] == "success"
        pg = tmp_path / ".proto-gear"
        assert (pg / "devops" / "workflows" / "deploy" / "WORKFLOW.md").is_file()
        assert (pg / "skills" / "code-review").is_dir()  # shared stays flat
        caps = load_all_capabilities(pg)
        assert "devops/workflows/deploy" in caps


class TestDevopsShipsAnAgent:
    """PROTO-067: adding a SECOND discipline agent required zero core edits —
    the core discovers and installs devops's agent through the same seam qa uses,
    and `pg init` (copy_capability_templates) lays it into the host."""

    def test_devops_agent_is_discovered(self):
        by_module = {m: p for m, p in module_host.iter_agent_sources()}
        assert "devops" in by_module
        assert (by_module["devops"] / "deploy-agent.yaml").is_file()

    def test_devops_agent_composes_its_own_workflow(self):
        from proto_gear_pkg.agent_config import AgentConfigParser, AgentManager
        from proto_gear_pkg.paths import package_root

        by_module = {m: p for m, p in module_host.iter_agent_sources()}
        agent = AgentConfigParser.parse_agent_file(
            by_module["devops"] / "deploy-agent.yaml"
        )
        assert "devops/workflows/deploy" in agent.capabilities.all_capabilities()
        mgr = AgentManager(Path("no-such-agents"), package_root() / "capabilities")
        errors, _ = mgr.validate_agent(agent)
        assert errors == [], f"devops agent should validate cleanly, got: {errors}"

    def test_pg_init_installs_devops_agent(self, tmp_path):
        from proto_gear_pkg.modules.engineering.templates import (
            copy_capability_templates,
        )

        res = copy_capability_templates(tmp_path, project_name="demo", version="9.9.9")
        assert res["status"] == "success"
        agent = tmp_path / ".proto-gear" / "agents" / "deploy-agent.yaml"
        assert agent.is_file()


class TestDevopsViaCLI:
    def test_module_list_includes_devops(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_list(_args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "devops" in out

    def test_module_show_devops(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(_args(name="devops", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "DEPLOY_QUEUE.md" in out

    def test_init_surface_writes_queue_verbatim(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(
            _args(module="devops", force=False, dry_run=False)
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Created DEPLOY_QUEUE.md" in out
        queue = (tmp_path / "DEPLOY_QUEUE.md").read_text(encoding="utf-8")
        assert "DEPLOY_QUEUE — Deployments & Incidents" in queue
        assert "{{" not in queue  # verbatim render
