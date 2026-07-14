"""Tests for multi-module hosting (PROTO-048, ADR-001 Phase B → C).

Covers ``module_host`` — engineering-department resolution via ``--module`` and
the generic state-surface render seam — plus the ``pg --module <name>
init-surface`` CLI handler.
"""

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core import module_host
from proto_gear_pkg.module_core.module_manifest import (
    ModuleManifest,
    ModuleManifestError,
    MANIFEST_FILENAME,
)


def _write_module(root: Path, module_id: str, template=None, **fields) -> Path:
    mod_dir = root / module_id
    mod_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"module: {module_id}", f"name: {fields.pop('name', module_id.title())}"]
    for k, v in fields.items():
        lines.append(f"{k}: {v}")
    (mod_dir / MANIFEST_FILENAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
    if template is not None:
        stem = Path(fields.get("state_surface", "STATE.md")).stem
        (mod_dir / f"{stem}.template.md").write_text(template, encoding="utf-8")
    return mod_dir


class TestResolveModule:
    def test_default_is_engineering(self):
        m = module_host.resolve_module(None)
        assert m.module == module_host.DEFAULT_MODULE == "engineering"

    def test_explicit_module(self, tmp_path):
        _write_module(tmp_path, "qa", state_surface="QA_QUEUE.md")
        m = module_host.resolve_module("qa", modules_root=tmp_path)
        assert m.module == "qa"
        assert m.state_surface == "QA_QUEUE.md"

    def test_unknown_raises_with_available(self):
        with pytest.raises(ModuleManifestError, match="unknown module 'bogus'"):
            module_host.resolve_module("bogus")

    def test_custom_root(self, tmp_path):
        _write_module(tmp_path, "toy", state_surface="TOY.md")
        m = module_host.resolve_module("toy", modules_root=tmp_path)
        assert m.module == "toy"


class TestIterCapabilitySources:
    def test_includes_shared_root_first(self):
        sources = module_host.iter_capability_sources()
        assert sources, "expected at least the shared capabilities root"
        module, path = sources[0]
        assert module is None
        assert path.name == "capabilities"
        assert path.is_dir()

    def test_includes_module_with_own_capabilities(self, tmp_path):
        # PROTO-052: a department that ships its own capabilities/ is a source.
        _write_module(tmp_path, "qa", state_surface="QA_QUEUE.md")
        (tmp_path / "qa" / "capabilities" / "workflows" / "audit").mkdir(parents=True)
        sources = module_host.iter_capability_sources(modules_root=tmp_path)
        by_module = {m: p for m, p in sources}
        assert None in by_module  # shared root always first
        assert "qa" in by_module
        assert by_module["qa"].name == "capabilities"

    def test_skips_modules_without_capabilities(self, tmp_path):
        # A department with no capabilities/ dir contributes no source.
        _write_module(tmp_path, "qa", state_surface="QA_QUEUE.md")
        sources = module_host.iter_capability_sources(modules_root=tmp_path)
        assert "qa" not in {m for m, _ in sources}


class TestLoadBundledCapabilities:
    """Seam S1 (listing side): capabilities merged across all modules, keyed by
    the same ``<module>/<cap_id>`` convention the doctor gate audit uses."""

    def test_shared_caps_keep_bare_ids(self):
        caps = module_host.load_bundled_capabilities()
        # A known shared/engineering capability keeps its bare, un-namespaced id.
        assert "skills/testing" in caps
        assert "workflows/release" in caps

    def test_module_caps_are_namespaced(self):
        caps = module_host.load_bundled_capabilities()
        # qa's own bundled capability surfaces, namespaced by its module id —
        # matching doctor.check_supervision_gates' target format.
        assert "qa/workflows/release-signoff" in caps
        # ...and never leaks in as a bare id that could collide with a shared cap.
        assert "workflows/release-signoff" not in caps

    @staticmethod
    def _write_cap(dir_: Path, name: str):
        dir_.mkdir(parents=True, exist_ok=True)
        (dir_ / "metadata.yaml").write_text(
            f'name: "{name}"\n'
            'type: "workflow"\n'
            'version: "0.1.0"\n'
            'description: "test"\n'
            'category: "test"\n'
            'tags: ["t"]\n'
            'status: "beta"\n'
            'author: "test"\n'
            'last_updated: "2026-07-10"\n',
            encoding="utf-8",
        )

    def test_merge_shared_first_module_cannot_clobber(self, tmp_path):
        # Two sources declaring the same bare cap id: shared (None) is iterated
        # first, the module's copy lands under its namespace — no collision.
        self._write_cap(tmp_path / "shared" / "workflows" / "release", "Shared Release")
        self._write_cap(tmp_path / "mod" / "workflows" / "release", "QA Release")
        merged = module_host.merge_capability_sources(
            [(None, tmp_path / "shared"), ("qa", tmp_path / "mod")]
        )
        assert merged["workflows/release"].name == "Shared Release"
        assert merged["qa/workflows/release"].name == "QA Release"


class TestInstallModuleCapabilities:
    """Seam S1 (on-disk): a module's own capabilities install under
    ``.proto-gear/<module>/`` so their id stays ``<module>/<cap_id>``."""

    @staticmethod
    def _module_with_cap(root: Path, module_id: str, template_body: str):
        _write_module(root, module_id, state_surface="STATE.md")
        cap = root / module_id / "capabilities" / "workflows" / "audit"
        cap.mkdir(parents=True)
        (cap / "metadata.yaml").write_text(
            'name: "Audit"\ntype: "workflow"\nversion: "0.1.0"\n'
            'description: "d"\ncategory: "c"\ntags: ["t"]\n'
            'status: "beta"\nauthor: "a"\nlast_updated: "2026-07-10"\n',
            encoding="utf-8",
        )
        (cap / "WORKFLOW.template.md").write_text(template_body, encoding="utf-8")

    def test_installs_under_module_namespace(self, tmp_path):
        self._module_with_cap(tmp_path, "qa", "audit for {{PROJECT_NAME}}\n")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_module_capabilities(
            proto, replacements={"PROJECT_NAME": "demo"}, modules_root=tmp_path
        )
        assert res["errors"] == []
        # Laid down under the module namespace, .template.md renamed to .md,
        # placeholder substituted.
        wf = proto / "qa" / "workflows" / "audit" / "WORKFLOW.md"
        assert wf.is_file()
        assert wf.read_text(encoding="utf-8") == "audit for demo\n"
        assert (proto / "qa" / "workflows" / "audit" / "metadata.yaml").is_file()

    def test_subtree_layout_yields_namespaced_id(self, tmp_path):
        from proto_gear_pkg.module_core.capability_metadata import (
            load_all_capabilities,
        )

        self._module_with_cap(tmp_path, "qa", "body\n")
        proto = tmp_path / "host" / ".proto-gear"
        module_host.install_module_capabilities(proto, modules_root=tmp_path)
        caps = load_all_capabilities(proto)
        assert "qa/workflows/audit" in caps

    def test_dry_run_writes_nothing(self, tmp_path):
        self._module_with_cap(tmp_path, "qa", "body\n")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_module_capabilities(
            proto, dry_run=True, modules_root=tmp_path
        )
        assert res["files_created"]  # reported…
        assert not proto.exists()  # …but nothing written

    def test_module_without_capabilities_installs_nothing(self, tmp_path):
        _write_module(tmp_path, "qa", state_surface="STATE.md")  # no capabilities/
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_module_capabilities(proto, modules_root=tmp_path)
        assert res["files_created"] == []


class TestIterAgentSources:
    """Seam S1 (agent side, PROTO-067): a module's own agents/ is a source,
    alongside the shared capabilities/agents/ root."""

    @staticmethod
    def _module_with_agent(root: Path, module_id: str, filename="a-agent.yaml"):
        _write_module(root, module_id, state_surface="STATE.md")
        agents = root / module_id / "agents"
        agents.mkdir(parents=True)
        (agents / filename).write_text(
            'name: "A"\nversion: "1.0.0"\ndescription: "d"\n'
            'created: "2026-07-11"\ncapabilities:\n  skills: ["testing"]\n',
            encoding="utf-8",
        )

    def test_includes_shared_agents_root_first(self):
        sources = module_host.iter_agent_sources()
        assert sources, "expected at least the shared capabilities/agents root"
        module, path = sources[0]
        assert module is None
        assert path.name == "agents"
        assert path.parent.name == "capabilities"
        assert path.is_dir()

    def test_includes_module_with_own_agents(self, tmp_path):
        self._module_with_agent(tmp_path, "qa")
        sources = module_host.iter_agent_sources(modules_root=tmp_path)
        by_module = {m: p for m, p in sources}
        assert None in by_module  # shared root always first
        assert "qa" in by_module
        assert by_module["qa"].name == "agents"

    def test_skips_modules_without_agents(self, tmp_path):
        _write_module(tmp_path, "qa", state_surface="STATE.md")  # no agents/
        sources = module_host.iter_agent_sources(modules_root=tmp_path)
        assert "qa" not in {m for m, _ in sources}

    def test_real_qa_and_devops_agents_are_discovered(self):
        # The real bundled discipline agents show up with zero core edits.
        by_module = {m: p for m, p in module_host.iter_agent_sources()}
        assert "qa" in by_module
        assert "devops" in by_module


class TestInstallModuleAgents:
    """Seam S1 (agent side, on-disk): a module's agents install *flat* under
    ``.proto-gear/agents/`` so ``AgentManager``'s non-recursive glob sees them."""

    @staticmethod
    def _module_with_agent(root: Path, module_id: str, filename):
        _write_module(root, module_id, state_surface="STATE.md")
        agents = root / module_id / "agents"
        agents.mkdir(parents=True)
        (agents / filename).write_text(
            'name: "A"\nversion: "1.0.0"\ndescription: "for {{PROJECT_NAME}}"\n'
            'created: "2026-07-11"\ncapabilities:\n  skills: ["testing"]\n',
            encoding="utf-8",
        )

    def test_installs_flat_with_substitution(self, tmp_path):
        self._module_with_agent(tmp_path, "qa", "qa-agent.yaml")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_module_agents(
            proto, replacements={"PROJECT_NAME": "demo"}, modules_root=tmp_path
        )
        assert res["errors"] == []
        agent = proto / "agents" / "qa-agent.yaml"
        assert agent.is_file()
        assert "for demo" in agent.read_text(encoding="utf-8")

    def test_collision_keeps_existing_and_reports(self, tmp_path):
        self._module_with_agent(tmp_path, "qa", "qa-agent.yaml")
        proto = tmp_path / "host" / ".proto-gear"
        module_host.install_module_agents(proto, modules_root=tmp_path)
        res = module_host.install_module_agents(proto, modules_root=tmp_path)
        assert res["files_created"] == []
        assert any("collision" in e for e in res["errors"])

    def test_dry_run_writes_nothing(self, tmp_path):
        self._module_with_agent(tmp_path, "qa", "qa-agent.yaml")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_module_agents(
            proto, dry_run=True, modules_root=tmp_path
        )
        assert res["files_created"]
        assert not proto.exists()

    def test_module_without_agents_installs_nothing(self, tmp_path):
        _write_module(tmp_path, "qa", state_surface="STATE.md")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_module_agents(proto, modules_root=tmp_path)
        assert res["files_created"] == []


class TestStateSurfaceTemplatePath:
    def test_template_in_module_dir(self, tmp_path):
        _write_module(tmp_path, "qa", template="queue\n", state_surface="QA_QUEUE.md")
        m = module_host.resolve_module("qa", modules_root=tmp_path)
        p = module_host.state_surface_template_path(m)
        assert p is not None
        assert p.name == "QA_QUEUE.template.md"
        assert p.parent.name == "qa"

    def test_engineering_template_in_package_root(self):
        m = module_host.resolve_module("engineering")
        p = module_host.state_surface_template_path(m)
        assert p is not None
        assert p.name == "PROJECT_STATUS.template.md"

    def test_none_when_no_state_surface(self):
        m = ModuleManifest(module="x", name="X", state_surface=None)
        assert module_host.state_surface_template_path(m) is None

    def test_none_when_template_missing(self, tmp_path):
        mod_dir = _write_module(tmp_path, "toy", state_surface="TOY.md")  # no template
        m = module_host.resolve_module("toy", modules_root=tmp_path)
        assert m.source_path == mod_dir / MANIFEST_FILENAME
        assert module_host.state_surface_template_path(m) is None


class TestRenderStateSurface:
    def _toy(self, tmp_path, template="hello\n", state_surface="TOY.md"):
        _write_module(tmp_path, "toy", template=template, state_surface=state_surface)
        return module_host.resolve_module("toy", modules_root=tmp_path)

    def test_create_verbatim(self, tmp_path):
        m = self._toy(tmp_path, template="ready to use\n")
        host = tmp_path / "host"
        host.mkdir()
        res = module_host.render_state_surface(m, host)
        assert res["status"] == "created"
        assert res["target"] == "TOY.md"
        assert (host / "TOY.md").read_text(encoding="utf-8") == "ready to use\n"
        assert res["unresolved"] == []

    def test_exists_without_force(self, tmp_path):
        m = self._toy(tmp_path)
        host = tmp_path / "host"
        host.mkdir()
        (host / "TOY.md").write_text("keep me", encoding="utf-8")
        res = module_host.render_state_surface(m, host)
        assert res["status"] == "exists"
        assert (host / "TOY.md").read_text(encoding="utf-8") == "keep me"

    def test_force_overwrites(self, tmp_path):
        m = self._toy(tmp_path, template="fresh\n")
        host = tmp_path / "host"
        host.mkdir()
        (host / "TOY.md").write_text("old", encoding="utf-8")
        res = module_host.render_state_surface(m, host, force=True)
        assert res["status"] == "overwritten"
        assert (host / "TOY.md").read_text(encoding="utf-8") == "fresh\n"

    def test_dry_run_does_not_write(self, tmp_path):
        m = self._toy(tmp_path)
        host = tmp_path / "host"
        host.mkdir()
        res = module_host.render_state_surface(m, host, dry_run=True)
        assert res["status"] == "would-create"
        assert not (host / "TOY.md").exists()

    def test_substitutions_applied(self, tmp_path):
        m = self._toy(tmp_path, template="owner: {{OWNER}}\n")
        host = tmp_path / "host"
        host.mkdir()
        res = module_host.render_state_surface(m, host, substitutions={"OWNER": "towb"})
        assert (host / "TOY.md").read_text(encoding="utf-8") == "owner: towb\n"
        assert res["unresolved"] == []

    def test_unresolved_placeholders_reported(self, tmp_path):
        m = self._toy(tmp_path, template="a {{X}} and {{Y}}\n")
        host = tmp_path / "host"
        host.mkdir()
        res = module_host.render_state_surface(m, host, substitutions={"X": "1"})
        assert res["status"] == "created"
        assert res["unresolved"] == ["{{Y}}"]

    def test_no_state_surface(self, tmp_path):
        m = ModuleManifest(module="x", name="X", state_surface=None)
        res = module_host.render_state_surface(m, tmp_path)
        assert res["status"] == "no-state-surface"

    def test_no_template(self, tmp_path):
        _write_module(tmp_path, "toy", state_surface="TOY.md")  # no template file
        m = module_host.resolve_module("toy", modules_root=tmp_path)
        res = module_host.render_state_surface(m, tmp_path / "host")
        assert res["status"] == "no-template"


class TestInitSurfaceCLI:
    def _args(self, **kw):
        kw.setdefault("module", None)
        kw.setdefault("force", False)
        kw.setdefault("dry_run", False)
        return argparse.Namespace(**kw)

    def test_engineering_creates_surface(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(self._args(module="engineering"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Created PROJECT_STATUS.md" in out
        assert (tmp_path / "PROJECT_STATUS.md").is_file()

    def test_exists_returns_1(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        (tmp_path / "PROJECT_STATUS.md").write_text("x", encoding="utf-8")
        rc = cli_commands.cmd_module_init_surface(self._args(module="engineering"))
        out = capsys.readouterr().out
        assert rc == 1
        assert "already exists" in out

    def test_force_overwrites(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        (tmp_path / "PROJECT_STATUS.md").write_text("x", encoding="utf-8")
        rc = cli_commands.cmd_module_init_surface(
            self._args(module="engineering", force=True)
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Overwrote PROJECT_STATUS.md" in out
        assert (tmp_path / "PROJECT_STATUS.md").read_text(encoding="utf-8") != "x"

    def test_unknown_module_returns_1(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(self._args(module="bogus"))
        out = capsys.readouterr().out
        assert rc == 1
        assert "unknown module 'bogus'" in out

    def test_engineering_warns_unresolved(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_module_init_surface(
            self._args(module="engineering", dry_run=True)
        )
        out = capsys.readouterr().out
        assert rc == 0
        assert "Would create PROJECT_STATUS.md" in out
        assert "unresolved placeholders" in out


class TestListBundledAgents:
    """PROTO-076: browse every installable bundled agent, pre-install."""

    def test_real_shared_and_discipline_agents_are_listed(self):
        records = module_host.list_bundled_agents()
        by_qualified = {r["qualified"]: r for r in records}
        # shared agents keep bare ids; discipline agents are namespaced.
        assert "code-review-agent" in by_qualified
        assert by_qualified["code-review-agent"]["module"] is None
        assert "qa/qa-release-agent" in by_qualified
        assert by_qualified["qa/qa-release-agent"]["module"] == "qa"
        assert by_qualified["qa/qa-release-agent"]["name"] == "qa-release-agent"

    def test_descriptions_are_read_best_effort(self):
        records = module_host.list_bundled_agents()
        qa = next(r for r in records if r["qualified"] == "qa/qa-release-agent")
        assert "sign-off" in qa["description"]

    def test_custom_root_module_agent_listed(self, tmp_path):
        TestIterAgentSources._module_with_agent(tmp_path, "qa")
        records = module_host.list_bundled_agents(modules_root=tmp_path)
        assert any(r["qualified"] == "qa/a-agent" for r in records)


class TestInstallBundledAgent:
    """PROTO-076: pull ONE discovered agent into a host on demand."""

    def test_installs_by_bare_name(self, tmp_path):
        TestIterAgentSources._module_with_agent(tmp_path, "qa")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_bundled_agent("a-agent", proto, modules_root=tmp_path)
        assert res["errors"] == []
        assert (proto / "agents" / "a-agent.yaml").is_file()

    def test_installs_by_qualified_name(self, tmp_path):
        TestIterAgentSources._module_with_agent(tmp_path, "qa")
        proto = tmp_path / "host" / ".proto-gear"
        res = module_host.install_bundled_agent(
            "qa/a-agent", proto, modules_root=tmp_path
        )
        assert res["errors"] == []
        assert res["installed"].endswith("a-agent.yaml")

    def test_unknown_name_errors(self, tmp_path):
        proto = tmp_path / ".proto-gear"
        res = module_host.install_bundled_agent(
            "no-such-agent", proto, modules_root=tmp_path
        )
        assert res["installed"] is None
        assert any("No bundled agent" in e for e in res["errors"])

    def test_ambiguous_bare_name_requires_qualification(self, tmp_path):
        TestIterAgentSources._module_with_agent(tmp_path, "qa", "dup-agent.yaml")
        TestIterAgentSources._module_with_agent(tmp_path, "devops", "dup-agent.yaml")
        proto = tmp_path / ".proto-gear"
        res = module_host.install_bundled_agent(
            "dup-agent", proto, modules_root=tmp_path
        )
        assert res["installed"] is None
        assert any("Ambiguous" in e for e in res["errors"])
        # the qualified form resolves it
        res2 = module_host.install_bundled_agent(
            "qa/dup-agent", proto, modules_root=tmp_path
        )
        assert res2["errors"] == []

    def test_never_overwrites_existing(self, tmp_path):
        TestIterAgentSources._module_with_agent(tmp_path, "qa")
        proto = tmp_path / ".proto-gear"
        module_host.install_bundled_agent("a-agent", proto, modules_root=tmp_path)
        marker = (proto / "agents" / "a-agent.yaml").read_text(encoding="utf-8")
        res = module_host.install_bundled_agent("a-agent", proto, modules_root=tmp_path)
        assert res["installed"] is None
        assert any("already installed" in e for e in res["errors"])
        assert (proto / "agents" / "a-agent.yaml").read_text(encoding="utf-8") == marker
