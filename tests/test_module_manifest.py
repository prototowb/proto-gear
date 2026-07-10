"""Tests for the departmental module manifest system (ADR-001 Phase B).

Covers manifest parsing/validation, discovery, surface validation, the bundled
engineering module, and the Phase B exit criterion: a toy second module loads
with zero core edits.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core.module_manifest import (
    ModuleManifest,
    ModuleManifestError,
    MANIFEST_FILENAME,
    parse_module_manifest,
    load_module_manifest,
    discover_modules,
    default_modules_root,
    validate_manifest_surfaces,
)


def _write_module(root: Path, module_id: str, **fields) -> Path:
    """Create a modules/<id>/module.yaml under root; return the module dir."""
    mod_dir = root / module_id
    mod_dir.mkdir(parents=True, exist_ok=True)
    lines = [f"module: {module_id}", f"name: {fields.pop('name', module_id.title())}"]
    for k, v in fields.items():
        lines.append(f"{k}: {v}")
    (mod_dir / MANIFEST_FILENAME).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return mod_dir


class TestParseManifest:
    def test_minimal_valid(self):
        m = parse_module_manifest({"module": "qa", "name": "QA"})
        assert m.module == "qa"
        assert m.name == "QA"
        assert m.version == "0.0.0"
        assert m.capabilities_root == ".proto-gear"
        assert m.context_manifest == "AGENT_CONTEXT.md"
        assert m.state_surface is None

    def test_missing_module_raises(self):
        with pytest.raises(ModuleManifestError, match="module"):
            parse_module_manifest({"name": "No Module"})

    def test_missing_name_raises(self):
        with pytest.raises(ModuleManifestError, match="name"):
            parse_module_manifest({"module": "x"})

    def test_non_mapping_raises(self):
        with pytest.raises(ModuleManifestError):
            parse_module_manifest(["not", "a", "mapping"])

    def test_flat_surface_fields(self):
        m = parse_module_manifest(
            {
                "module": "ops",
                "name": "Ops",
                "state_surface": "OPS_QUEUE.md",
                "handoff": "HANDOFF.md",
            }
        )
        assert m.state_surface == "OPS_QUEUE.md"
        assert m.handoff == "HANDOFF.md"

    def test_nested_contract_block(self):
        m = parse_module_manifest(
            {
                "module": "ops",
                "name": "Ops",
                "contract": {
                    "state_surface": "OPS_QUEUE.md",
                    "capabilities_root": ".ops",
                },
            }
        )
        assert m.state_surface == "OPS_QUEUE.md"
        assert m.capabilities_root == ".ops"

    def test_flat_overrides_nested(self):
        m = parse_module_manifest(
            {
                "module": "ops",
                "name": "Ops",
                "state_surface": "FLAT.md",
                "contract": {"state_surface": "NESTED.md"},
            }
        )
        assert m.state_surface == "FLAT.md"

    def test_bad_contract_type_raises(self):
        with pytest.raises(ModuleManifestError, match="contract"):
            parse_module_manifest({"module": "x", "name": "X", "contract": "nope"})

    def test_to_dict_serializes_source_path(self, tmp_path):
        m = parse_module_manifest(
            {"module": "x", "name": "X"}, source_path=tmp_path / "module.yaml"
        )
        d = m.to_dict()
        assert d["source_path"] == str(tmp_path / "module.yaml")
        assert d["module"] == "x"


class TestLoadManifest:
    def test_load_roundtrip(self, tmp_path):
        mod_dir = _write_module(
            tmp_path,
            "qa",
            name="QA",
            version="1.2.3",
            state_surface="QUEUE.md",
        )
        m = load_module_manifest(mod_dir / MANIFEST_FILENAME)
        assert m.module == "qa"
        assert m.version == "1.2.3"
        assert m.state_surface == "QUEUE.md"
        assert m.source_path == mod_dir / MANIFEST_FILENAME

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ModuleManifestError, match="not found"):
            load_module_manifest(tmp_path / "nope.yaml")

    def test_empty_file_raises(self, tmp_path):
        p = tmp_path / "module.yaml"
        p.write_text("", encoding="utf-8")
        with pytest.raises(ModuleManifestError, match="empty"):
            load_module_manifest(p)

    def test_invalid_yaml_raises(self, tmp_path):
        p = tmp_path / "module.yaml"
        p.write_text("module: x\n  bad: : indentation:\n", encoding="utf-8")
        with pytest.raises(ModuleManifestError):
            load_module_manifest(p)


class TestDiscoverModules:
    def test_missing_root_is_empty(self, tmp_path):
        assert discover_modules(tmp_path / "does-not-exist") == []

    def test_discovers_and_sorts(self, tmp_path):
        _write_module(tmp_path, "engineering")
        _write_module(tmp_path, "qa")
        mods = discover_modules(tmp_path)
        assert [m.module for m in mods] == ["engineering", "qa"]

    def test_ignores_dirs_without_manifest(self, tmp_path):
        _write_module(tmp_path, "qa")
        (tmp_path / "not_a_module").mkdir()
        mods = discover_modules(tmp_path)
        assert [m.module for m in mods] == ["qa"]


class TestSurfaceValidation:
    def test_all_surfaces_present(self, tmp_path):
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        (tmp_path / "PROJECT_STATUS.md").write_text("x", encoding="utf-8")
        m = parse_module_manifest(
            {
                "module": "eng",
                "name": "Eng",
                "state_surface": "PROJECT_STATUS.md",
            }
        )
        assert validate_manifest_surfaces(m, tmp_path) == []

    def test_missing_required_surface_reported(self, tmp_path):
        m = parse_module_manifest({"module": "eng", "name": "Eng"})
        problems = validate_manifest_surfaces(m, tmp_path)
        # capabilities_root + context_manifest missing
        assert any("capabilities_root" in p for p in problems)
        assert any("context_manifest" in p for p in problems)

    def test_declared_optional_surface_must_exist(self, tmp_path):
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        m = parse_module_manifest(
            {
                "module": "eng",
                "name": "Eng",
                "state_surface": "MISSING.md",
            }
        )
        problems = validate_manifest_surfaces(m, tmp_path)
        assert any("state_surface" in p and "MISSING.md" in p for p in problems)

    def test_undeclared_optional_surface_is_fine(self, tmp_path):
        (tmp_path / ".proto-gear").mkdir()
        (tmp_path / "AGENT_CONTEXT.md").write_text("x", encoding="utf-8")
        m = parse_module_manifest({"module": "eng", "name": "Eng"})  # no state_surface
        problems = validate_manifest_surfaces(m, tmp_path)
        assert not any("state_surface" in p for p in problems)


class TestBundledEngineeringModule:
    def test_engineering_module_is_discoverable(self):
        mods = discover_modules()  # package default root
        by_id = {m.module: m for m in mods}
        assert "engineering" in by_id
        eng = by_id["engineering"]
        assert eng.name == "Engineering"
        assert eng.state_surface == "PROJECT_STATUS.md"
        assert eng.context_manifest == "AGENT_CONTEXT.md"
        assert eng.handoff == "SESSION_HANDOFF.md"

    def test_default_modules_root_exists(self):
        assert default_modules_root().is_dir()


class TestModuleCommands:
    """pg module list / show handlers (cli_commands)."""

    def _args(self, **kw):
        import argparse

        return argparse.Namespace(**kw)

    def test_list_shows_engineering(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_list(self._args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "engineering" in out
        assert "Engineering" in out

    def test_list_json(self, capsys):
        import json
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_list(self._args(json=True))
        out = capsys.readouterr().out
        assert rc == 0
        data = json.loads(out)
        assert any(m["module"] == "engineering" for m in data)

    def test_show_engineering(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(self._args(name="engineering", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "PROJECT_STATUS.md" in out
        assert "Contract surfaces" in out

    def test_show_missing_returns_1(self, capsys):
        from proto_gear_pkg import cli_commands

        rc = cli_commands.cmd_module_show(self._args(name="nope", json=False))
        out = capsys.readouterr().out
        assert rc == 1
        assert "not found" in out


class TestZeroCoreEditAcceptance:
    """ADR-001 Phase B exit criterion: a toy second module loads unmodified."""

    def test_toy_second_module_loads_with_zero_core_edits(self, tmp_path):
        # Simulate the package modules/ dir with the real engineering module
        # plus a brand-new toy module — added purely by dropping files in.
        modules_root = tmp_path / "modules"
        _write_module(
            modules_root,
            "engineering",
            name="Engineering",
            state_surface="PROJECT_STATUS.md",
        )
        _write_module(
            modules_root,
            "toy",
            name="Toy Department",
            description="A second module proving the contract",
            state_surface="TOY_QUEUE.md",
        )

        mods = discover_modules(modules_root)
        by_id = {m.module: m for m in mods}

        # The core discovered BOTH modules through the same interface, with no
        # code change — composition, not a fork.
        assert set(by_id) == {"engineering", "toy"}
        assert by_id["toy"].name == "Toy Department"
        assert by_id["toy"].state_surface == "TOY_QUEUE.md"
        # The toy module satisfies the same manifest contract as engineering.
        assert isinstance(by_id["toy"], ModuleManifest)
