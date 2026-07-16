"""
Tests for capability output profiles (steering-plan Phase 2+3):
frontier (slim stubs) vs verbose (full methodology bodies).
"""

from pathlib import Path

import pytest

from proto_gear_pkg.module_core import capability_profile as cp
from proto_gear_pkg.modules.engineering.templates import copy_capability_templates


class TestNormalizeProfile:
    def test_defaults_on_none(self):
        assert cp.normalize_profile(None) == cp.DEFAULT_PROFILE

    def test_defaults_on_unknown(self):
        assert cp.normalize_profile("gibberish") == cp.DEFAULT_PROFILE

    def test_case_insensitive(self):
        assert cp.normalize_profile("VERBOSE") == "verbose"
        assert cp.normalize_profile(" Frontier ") == "frontier"

    def test_default_is_frontier(self):
        # The plan: new inits default to the slim profile.
        assert cp.DEFAULT_PROFILE == "frontier"


class TestIsCapabilityBody:
    @pytest.mark.parametrize(
        "path",
        [
            "skills/testing/SKILL.template.md",
            "workflows/release/WORKFLOW.template.md",
            "commands/create-ticket/COMMAND.template.md",
        ],
    )
    def test_body_files(self, path):
        assert cp.is_capability_body(path) is True

    @pytest.mark.parametrize(
        "path",
        [
            "skills/testing/metadata.yaml",
            "INDEX.md",
            "skills/INDEX.md",
            "agents/some-agent.yaml",
            "skills/testing/README.template.md",
        ],
    )
    def test_non_body_files(self, path):
        assert cp.is_capability_body(path) is False


class TestRenderFrontierStub:
    def test_includes_description_and_triggers(self):
        stub = cp.render_frontier_stub(
            name="Test-Driven Development",
            cap_type="skill",
            description="TDD methodology",
            triggers=["write tests", "tdd"],
        )
        assert "# Test-Driven Development" in stub
        assert "TDD methodology" in stub
        assert "write tests" in stub
        assert "Frontier profile" in stub
        assert "pg init --profile verbose" in stub

    def test_short(self):
        stub = cp.render_frontier_stub("X", "skill", "desc", [])
        # A stub is a skim, not a manual.
        assert len(stub.splitlines()) < 15


class TestFrontierStubForCapability:
    def test_builds_from_sibling_metadata(self, tmp_path):
        capdir = tmp_path / "skills" / "testing"
        capdir.mkdir(parents=True)
        (capdir / "metadata.yaml").write_text(
            'name: "TDD"\ntype: "skill"\ndescription: "d"\n'
            "relevance:\n  triggers:\n    - tdd\n",
            encoding="utf-8",
        )
        body = capdir / "SKILL.template.md"
        body.write_text("full body", encoding="utf-8")
        stub = cp.frontier_stub_for_capability(body)
        assert stub is not None
        assert "# TDD" in stub
        assert "full body" not in stub

    def test_none_when_metadata_missing(self, tmp_path):
        body = tmp_path / "SKILL.template.md"
        body.write_text("x", encoding="utf-8")
        assert cp.frontier_stub_for_capability(body) is None


class TestCopyWithProfiles:
    def test_frontier_stubs_bodies_keeps_metadata(self, tmp_path):
        result = copy_capability_templates(
            tmp_path, "Proj", dry_run=False, profile="frontier"
        )
        assert result["status"] in ("success", "partial")
        assert result["profile"] == "frontier"
        pg = tmp_path / ".proto-gear"
        skill = pg / "skills" / "testing" / "SKILL.md"
        assert skill.exists()
        text = skill.read_text(encoding="utf-8")
        assert "Frontier profile" in text
        assert len(text.splitlines()) < 15
        # metadata + routing surfaces are preserved
        assert (pg / "skills" / "testing" / "metadata.yaml").exists()
        # profile marker recorded
        assert (pg / "PROFILE").read_text(encoding="utf-8").strip() == "frontier"

    def test_verbose_ships_full_bodies(self, tmp_path):
        copy_capability_templates(tmp_path, "Proj", dry_run=False, profile="verbose")
        skill = tmp_path / ".proto-gear" / "skills" / "testing" / "SKILL.md"
        text = skill.read_text(encoding="utf-8")
        assert "Frontier profile" not in text
        assert len(text.splitlines()) > 50  # full methodology preserved
        assert (tmp_path / ".proto-gear" / "PROFILE").read_text(
            encoding="utf-8"
        ).strip() == "verbose"

    def test_frontier_is_much_smaller_than_verbose(self, tmp_path):
        f_dir = tmp_path / "frontier"
        v_dir = tmp_path / "verbose"
        f_dir.mkdir()
        v_dir.mkdir()
        copy_capability_templates(f_dir, "P", dry_run=False, profile="frontier")
        copy_capability_templates(v_dir, "P", dry_run=False, profile="verbose")

        def total_body_chars(root):
            total = 0
            for p in (root / ".proto-gear").rglob("*.md"):
                if p.stem in ("SKILL", "WORKFLOW", "COMMAND"):
                    total += len(p.read_text(encoding="utf-8"))
            return total

        assert total_body_chars(f_dir) * 3 < total_body_chars(v_dir)

    def test_unknown_profile_falls_back_to_default(self, tmp_path):
        result = copy_capability_templates(
            tmp_path, "Proj", dry_run=False, profile="nonsense"
        )
        assert result["profile"] == cp.DEFAULT_PROFILE
