"""Tests for the bundled Content module (PROTO-047, ADR-001 Phase C entry).

The Content module is the *second* implementation of the module contract. Its
whole job is to prove the department-agnostic core discovers, loads, and audits
a brand-new department through the same interfaces as engineering — with zero
edits to ``module_core/``. These tests assert exactly that against the REAL
bundled module (not a tmp_path toy), which is the difference from the toy
acceptance test in ``test_module_manifest.py``.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core.module_manifest import (
    ModuleManifest,
    discover_modules,
    load_module_manifest,
    validate_manifest_surfaces,
    default_modules_root,
)
from proto_gear_pkg.module_core import doctor


class TestBundledContentModule:
    def test_content_module_is_discoverable(self):
        """discover_modules() finds content alongside engineering — no core edit."""
        by_id = {m.module: m for m in discover_modules()}
        assert "content" in by_id, "content module must be discovered by the core"
        content = by_id["content"]
        assert content.name == "Content"
        assert content.state_surface == "CONTENT_QUEUE.md"
        assert content.context_manifest == "AGENT_CONTEXT.md"
        assert content.handoff == "SESSION_HANDOFF.md"

    def test_content_and_engineering_coexist(self):
        """The core hosts two independent modules through one interface."""
        ids = {m.module for m in discover_modules()}
        assert {"content", "engineering"} <= ids

    def test_content_manifest_has_state_surface_template(self):
        """The declared state surface ships a template inside the module dir."""
        content_dir = default_modules_root() / "content"
        assert (content_dir / "module.yaml").is_file()
        assert (content_dir / "CONTENT_QUEUE.template.md").is_file()

    def test_content_manifest_version_and_description(self):
        by_id = {m.module: m for m in discover_modules()}
        content = by_id["content"]
        assert content.version == "0.1.0"
        assert "content" in content.description.lower()


class TestContentSurfaceValidation:
    """The manifest's declared surfaces validate against an initialised host."""

    def test_surfaces_present_in_synthetic_host(self, tmp_path):
        content = {m.module: m for m in discover_modules()}["content"]
        # Simulate a host project that has initialised the content module.
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        (tmp_path / "CONTENT_QUEUE.md").write_text("x", encoding="utf-8")
        (tmp_path / "SESSION_HANDOFF.md").write_text("x", encoding="utf-8")
        assert validate_manifest_surfaces(content, tmp_path) == []

    def test_missing_content_queue_is_reported(self, tmp_path):
        content = {m.module: m for m in discover_modules()}["content"]
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        # CONTENT_QUEUE.md deliberately absent
        problems = validate_manifest_surfaces(content, tmp_path)
        assert any("state_surface" in p and "CONTENT_QUEUE.md" in p for p in problems)


class TestDoctorAcceptsContentModule:
    """doctor.check_modules validates the content manifest with zero core edits."""

    def test_content_manifest_reported_valid(self):
        findings = doctor.check_modules(Path.cwd())
        by_target = {f.target: f for f in findings}
        content_target = "modules/content/module.yaml"
        assert content_target in by_target, "doctor must audit the content manifest"
        assert by_target[content_target].id == "module-manifest-valid"
        assert by_target[content_target].severity == "ok"

    def test_no_module_manifest_errors(self):
        findings = doctor.check_modules(Path.cwd())
        assert not [f for f in findings if f.severity == "error"]


class TestContentModuleViaCLI:
    """pg module list / show surface the content module generically."""

    def _args(self, **kw):
        import argparse

        return argparse.Namespace(**kw)

    def test_module_list_includes_content(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_list(self._args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "content" in out
        assert "Content" in out

    def test_module_show_content(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(self._args(name="content", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "CONTENT_QUEUE.md" in out
        assert "Contract surfaces" in out

    def test_module_show_content_json(self, capsys):
        import json
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(self._args(name="content", json=True))
        out = capsys.readouterr().out
        assert rc == 0
        data = json.loads(out)
        assert data["module"] == "content"
        assert data["state_surface"] == "CONTENT_QUEUE.md"
