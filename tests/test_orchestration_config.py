"""Tests for orchestration paradigm parsing/validation (PROTO-091).

A paradigm is a declarative manifest describing how the overseer distributes and
coordinates sub-agents. The parser is small and independent of the capability
composition engine (paradigms compose nothing). These tests cover the bundled
pool plus good/bad manifest validation.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.orchestration_config import (
    OrchestrationParadigm,
    ParadigmRole,
    ParadigmValidationError,
    parse_paradigm_dict,
    load_paradigms,
)


def _valid():
    return {
        "id": "driver-reviewer",
        "name": "Driver–Reviewer",
        "description": "impl + review",
        "roles": [
            {"role": "driver", "model_tier": "balanced"},
            {"role": "reviewer", "agent": "code-review-agent", "model_tier": "deep"},
        ],
        "selectable_by": ["user", "agent"],
    }


class TestParadigmParsing:
    def test_parse_valid(self):
        p = parse_paradigm_dict(_valid())
        assert p.id == "driver-reviewer"
        assert [r.role for r in p.roles] == ["driver", "reviewer"]
        assert p.roles[1].agent == "code-review-agent"
        assert p.roles[1].model_tier == "deep"

    def test_defaults(self):
        p = parse_paradigm_dict({"id": "solo", "name": "Solo", "description": "d"})
        assert p.version == "1.0.0"
        assert p.status == "active"
        assert p.selectable_by == ["user", "agent"]
        assert p.roles == []

    @pytest.mark.parametrize("missing", ["id", "name", "description"])
    def test_missing_required_rejected(self, missing):
        data = {"id": "x", "name": "X", "description": "d"}
        del data[missing]
        with pytest.raises(ParadigmValidationError):
            parse_paradigm_dict(data)

    def test_bad_role_tier_rejected(self):
        data = _valid()
        data["roles"][0]["model_tier"] = "ultra"
        with pytest.raises(ParadigmValidationError):
            parse_paradigm_dict(data)

    def test_role_without_name_rejected(self):
        data = _valid()
        data["roles"].append({"model_tier": "fast"})
        with pytest.raises(ParadigmValidationError):
            parse_paradigm_dict(data)

    def test_bad_selectable_by_rejected(self):
        data = _valid()
        data["selectable_by"] = ["robot"]
        with pytest.raises(ParadigmValidationError):
            parse_paradigm_dict(data)

    def test_to_dict_roundtrip(self):
        p = parse_paradigm_dict(_valid())
        d = p.to_dict()
        again = parse_paradigm_dict(d)
        assert again.id == p.id
        assert [r.model_tier for r in again.roles] == [r.model_tier for r in p.roles]


class TestBundledPool:
    def test_pool_has_all_six(self):
        pool = {p.id for p in load_paradigms()}
        assert {
            "dynamic",
            "solo",
            "driver-reviewer",
            "core-flex",
            "pipeline",
            "fan-out",
        } <= pool

    def test_every_bundled_paradigm_parses(self):
        for p in load_paradigms():
            assert p.name and p.description
            for r in p.roles:
                assert r.model_tier in ("fast", "balanced", "deep")

    def test_installed_override_wins(self, tmp_path):
        # A project copy with the same id replaces the bundled one in the pool.
        d = tmp_path / ".proto-gear" / "orchestration"
        d.mkdir(parents=True)
        (d / "solo.yaml").write_text(
            "id: solo\nname: Solo Custom\ndescription: customised\n",
            encoding="utf-8",
        )
        pool = {p.id: p for p in load_paradigms(project_dir=tmp_path)}
        assert pool["solo"].name == "Solo Custom"
