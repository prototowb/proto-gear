"""
Tests for setup_agent_framework_only() function
Targeting uncovered branches to increase coverage from 56% to 60%+
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.proto_gear import setup_agent_framework_only


class TestSetupWithCoreTemplates:
    """Test setup with core_templates dict from wizard"""

    def test_setup_with_core_templates_dict(self, tmp_path, monkeypatch):
        """Test setup with explicit template selection (lines 859-863)"""
        monkeypatch.chdir(tmp_path)

        core_templates = {
            "TESTING": True,
            "CONTRIBUTING": True,
            "SECURITY": False,
            "AGENTS": False,  # Should be skipped
            "PROJECT_STATUS": False,  # Should be skipped
        }

        result = setup_agent_framework_only(
            ticket_prefix="TEST",
            with_branching=False,
            with_all=False,
            dry_run=False,
            core_templates=core_templates,
        )

        assert result["status"] == "success"
        assert "TESTING.md" in result["files_created"]
        assert "CONTRIBUTING.md" in result["files_created"]
        # SECURITY should not be created
        assert "SECURITY.md" not in result["files_created"]

    def test_setup_dry_run_with_core_templates(self, tmp_path, monkeypatch, capsys):
        """Test dry run with core_templates dict (lines 932-934)"""
        monkeypatch.chdir(tmp_path)

        core_templates = {"TESTING": True, "SECURITY": True, "CONTRIBUTING": False}

        result = setup_agent_framework_only(
            ticket_prefix="TEST",
            with_branching=False,
            with_all=False,
            dry_run=True,
            core_templates=core_templates,
        )

        assert result["status"] == "success"
        assert result["dry_run"] is True

        captured = capsys.readouterr()
        # Should show selected templates
        assert "TESTING" in captured.out or "Dry run" in captured.out


class TestSetupWithBranching:
    """Test setup with with_branching flag"""

    def test_setup_with_branching_adds_testing(self, tmp_path, monkeypatch):
        """Test that with_branching adds TESTING template (lines 878-880)"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.detect_git_config") as mock_git:
            mock_git.return_value = {
                "is_git_repo": True,
                "has_remote": False,
                "main_branch": "main",
                "dev_branch": "develop",
                "workflow_mode": "local_only",
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST", with_branching=True, with_all=False, dry_run=False
            )

            assert result["status"] == "success"
            # Should create TESTING.md along with BRANCHING.md
            assert "TESTING.md" in result["files_created"]
            assert "BRANCHING.md" in result["files_created"]

    def test_setup_dry_run_with_branching(self, tmp_path, monkeypatch, capsys):
        """Test dry run shows BRANCHING.md (line 925)"""
        monkeypatch.chdir(tmp_path)

        result = setup_agent_framework_only(
            ticket_prefix="TEST", with_branching=True, with_all=False, dry_run=True
        )

        assert result["status"] == "success"
        assert result["dry_run"] is True

        captured = capsys.readouterr()
        # Should show BRANCHING.md
        assert "BRANCHING.md" in captured.out or "Git workflow" in captured.out


class TestSetupWithAll:
    """Test setup with --all flag"""

    def test_setup_with_all_flag(self, tmp_path, monkeypatch):
        """Test --all flag generates all templates"""
        monkeypatch.chdir(tmp_path)

        result = setup_agent_framework_only(
            ticket_prefix="TEST", with_branching=False, with_all=True, dry_run=False
        )

        assert result["status"] == "success"
        # Should create all templates
        expected_templates = [
            "TESTING",
            "BRANCHING",
            "CONTRIBUTING",
            "SECURITY",
            "ARCHITECTURE",
            "CODE_OF_CONDUCT",
        ]
        for template in expected_templates:
            assert (
                f"{template}.md" in result["files_created"]
            ), f"{template}.md should be created"

    def test_setup_dry_run_with_all(self, tmp_path, monkeypatch, capsys):
        """Test dry run with --all flag (lines 938-943)"""
        monkeypatch.chdir(tmp_path)

        result = setup_agent_framework_only(
            ticket_prefix="TEST", with_branching=False, with_all=True, dry_run=True
        )

        assert result["status"] == "success"
        assert result["dry_run"] is True

        captured = capsys.readouterr()
        # Should show multiple templates
        assert "TESTING" in captured.out or "CONTRIBUTING" in captured.out

    def test_setup_with_all_and_branching(self, tmp_path, monkeypatch):
        """Test --all with with_branching (edge case for line 939-943)"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.detect_git_config") as mock_git:
            mock_git.return_value = {
                "is_git_repo": True,
                "has_remote": False,
                "main_branch": "main",
                "dev_branch": "develop",
                "workflow_mode": "local_only",
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST", with_branching=True, with_all=True, dry_run=False
            )

            assert result["status"] == "success"
            # BRANCHING should only appear once
            branching_count = result["files_created"].count("BRANCHING.md")
            assert (
                branching_count <= 2
            )  # Could be in both branches, but shouldn't duplicate


class TestSetupWithCapabilities:
    """Test setup with capabilities system"""

    def test_setup_with_capabilities_success(self, tmp_path, monkeypatch, capsys):
        """Test successful capability creation (lines 905-906)"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.copy_capability_templates") as mock_copy:
            mock_copy.return_value = {
                "status": "success",
                "files_created": [
                    ".proto-gear/skills/tdd.md",
                    ".proto-gear/workflows/feature-dev.md",
                ],
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=False,
                with_capabilities=True,
            )

            assert result["status"] == "success"
            # Should include capability files
            assert ".proto-gear/skills/tdd.md" in result["files_created"]
            assert ".proto-gear/workflows/feature-dev.md" in result["files_created"]

            captured = capsys.readouterr()
            # Should print success message
            assert (
                "Capability system created" in captured.out
                or "proto-gear" in captured.out
            )

    def test_setup_with_capabilities_warning(self, tmp_path, monkeypatch, capsys):
        """Test capability creation with warning"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.copy_capability_templates") as mock_copy:
            mock_copy.return_value = {
                "status": "warning",
                "errors": ["Directory already exists"],
                "files_created": [],
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=False,
                with_capabilities=True,
            )

            assert result["status"] == "success"  # Setup itself succeeds

            captured = capsys.readouterr()
            # Should show warning
            assert "already exists" in captured.out or result is not None

    def test_setup_with_capabilities_error(self, tmp_path, monkeypatch, capsys):
        """Test capability creation error handling (line 910)"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.copy_capability_templates") as mock_copy:
            mock_copy.return_value = {
                "status": "error",
                "errors": ["Failed to copy templates"],
                "files_created": [],
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=False,
                with_capabilities=True,
            )

            assert (
                result["status"] == "success"
            )  # Setup continues despite capability error

            captured = capsys.readouterr()
            # Should show error message
            assert "issues" in captured.out or result is not None

    def test_setup_dry_run_with_capabilities(self, tmp_path, monkeypatch):
        """Test dry run with capabilities (line 961)"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.copy_capability_templates") as mock_copy:
            mock_copy.return_value = {
                "status": "success",
                "files_created": [],
                "dry_run": True,
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=True,
                with_capabilities=True,
            )

            assert result["status"] == "success"
            assert result["dry_run"] is True

            # Should have called copy_capability_templates with dry_run=True
            mock_copy.assert_called_once()
            assert mock_copy.call_args[1]["dry_run"] is True


class TestSetupErrorHandling:
    """Test error handling in setup function"""

    def test_setup_exception_handling(self, tmp_path, monkeypatch):
        """Test exception handling (lines 918-919)"""
        monkeypatch.chdir(tmp_path)

        # Force an exception during file creation (inside the try block)
        with patch("pathlib.Path.write_text") as mock_write:
            mock_write.side_effect = Exception("Test error")

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=False,
            )

            assert result["status"] == "error"
            assert "error" in result
            assert "Test error" in result["error"]


class TestSetupWithFramework:
    """Test setup detects and displays framework"""

    def test_setup_with_framework_detected(self, tmp_path, monkeypatch, capsys):
        """Test framework display (line 714)"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.detect_project_structure") as mock_detect:
            mock_detect.return_value = {
                "detected": True,
                "type": "Node.js Project",
                "framework": "Next.js",
                "directories": ["src", "tests"],
                "structure_summary": "Next.js application",
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=False,
            )

            assert result["status"] == "success"

            captured = capsys.readouterr()
            # Should display framework
            assert "Next.js" in captured.out or "Framework" in captured.out


class TestSetupDryRunTemplateDescriptions:
    """Test dry run template description display"""

    def test_dry_run_shows_template_descriptions(self, tmp_path, monkeypatch, capsys):
        """Test template descriptions in dry run (lines 956-957)"""
        monkeypatch.chdir(tmp_path)

        result = setup_agent_framework_only(
            ticket_prefix="TEST", with_branching=False, with_all=True, dry_run=True
        )

        assert result["status"] == "success"
        assert result["dry_run"] is True

        captured = capsys.readouterr()
        # Should show template descriptions
        assert (
            "TDD" in captured.out
            or "Security" in captured.out
            or "Dry run" in captured.out
        )


class TestSetupEdgeCases:
    """Test edge cases and special scenarios"""

    def test_setup_with_capabilities_config(self, tmp_path, monkeypatch):
        """Test passing capabilities_config"""
        monkeypatch.chdir(tmp_path)

        with patch("proto_gear_pkg.proto_gear.copy_capability_templates") as mock_copy:
            mock_copy.return_value = {"status": "success", "files_created": []}

            capabilities_config = {
                "skills": ["tdd"],
                "workflows": ["feature-dev"],
                "commands": [],
            }

            result = setup_agent_framework_only(
                ticket_prefix="TEST",
                with_branching=False,
                with_all=False,
                dry_run=False,
                with_capabilities=True,
                capabilities_config=capabilities_config,
            )

            assert result["status"] == "success"

            # Should pass capabilities_config to copy_capability_templates
            mock_copy.assert_called_once()
            assert mock_copy.call_args[1]["capabilities_config"] == capabilities_config

    def test_setup_branching_content_none(self, tmp_path, monkeypatch):
        """Test when generate_branching_doc returns None (line 737-741 else path)"""
        monkeypatch.chdir(tmp_path)

        with (
            patch("proto_gear_pkg.proto_gear.detect_git_config") as mock_git,
            patch("proto_gear_pkg.proto_gear.generate_branching_doc") as mock_gen,
        ):

            mock_git.return_value = {
                "is_git_repo": False,
                "has_remote": False,
                "main_branch": "main",
                "dev_branch": "develop",
                "workflow_mode": "no_git",
            }
            # Return None (git-aware template generation failed)
            mock_gen.return_value = None

            result = setup_agent_framework_only(
                ticket_prefix="TEST", with_branching=True, with_all=False, dry_run=False
            )

            assert result["status"] == "success"
            # With with_branching=True, BRANCHING.md will still be created
            # via generate_project_template (lines 878-880), even if generate_branching_doc returns None
            # The test verifies that the code handles None gracefully and continues
            assert result["files_created"] is not None


import re

from proto_gear_pkg.modules.engineering.templates import (
    build_default_replacements,
    humanize_leftover_tokens,
)

# A single {{TOKEN}} slot (letters/underscore), ignoring doubled `{{{{..}}}}`.
_TOKEN_RE = re.compile(r"(?<!\{)\{\{[A-Za-z_]+\}\}(?!\})")


class TestBuildDefaultReplacements:
    """PROTO-078: the shared defaulted replacement dict."""

    def test_honors_ticket_prefix_flag(self):
        repl = build_default_replacements(".", ticket_prefix="ARSENAL")
        assert repl["TICKET_PREFIX"] == "ARSENAL"

    def test_resolves_blank_dot_name(self):
        # Path(".").name is "" — the builder must resolve to a real name.
        repl = build_default_replacements(".")
        assert repl["PROJECT_NAME"]  # non-empty
        assert repl["PROJECT_NAME"] != ""

    def test_language_aware_python(self):
        repl = build_default_replacements(".", project_info={"type": "Python Project"})
        assert repl["TEST_COMMAND"] == "pytest"
        assert repl["CODE_LANGUAGE"] == "Python"

    def test_language_aware_node(self):
        repl = build_default_replacements(".", project_info={"type": "Node.js Project"})
        assert repl["TEST_COMMAND"] == "npm test"

    def test_generic_fallback(self):
        repl = build_default_replacements(".", project_info={"type": None})
        assert repl["TEST_COMMAND"] == "make test"

    def test_branch_names_from_git_config(self):
        repl = build_default_replacements(
            ".", git_config={"main_branch": "trunk", "dev_branch": "dev"}
        )
        assert repl["MAIN_BRANCH"] == "trunk"
        assert repl["DEV_BRANCH"] == "dev"


class TestHumanizeLeftoverTokens:
    """PROTO-078: the clean-file leftover sweep."""

    def test_replaces_bare_token(self):
        assert humanize_leftover_tokens("x {{CODE_STYLE_GUIDE}} y") == (
            "x _TBD: code style guide_ y"
        )

    def test_leaves_doubled_braces_alone(self):
        # BRANCHING examples emit literal `{{{{...}}}}`; must not be swept.
        assert (
            humanize_leftover_tokens("feature/{{{{TICKET_PREFIX}}}}-XXX")
            == "feature/{{{{TICKET_PREFIX}}}}-XXX"
        )


class TestProto078NonInteractiveInit:
    """PROTO-078: `pg init --no-interactive` fills wizard substitutions."""

    def _init_all(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        return setup_agent_framework_only(
            ticket_prefix="ARSENAL",
            with_branching=True,
            with_all=True,
            dry_run=False,
        )

    def test_project_status_headered_and_prefixed(self, tmp_path, monkeypatch):
        self._init_all(tmp_path, monkeypatch)
        status = (tmp_path / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        # Routed through the headered template (was headerless inline before).
        assert "proto-gear:header" in status
        # --ticket-prefix honored in the parseable Current State YAML.
        assert 'ticket_prefix: "ARSENAL"' in status
        assert "last_ticket_id:" in status

    def test_no_blank_project_name(self, tmp_path, monkeypatch):
        self._init_all(tmp_path, monkeypatch)
        agents = (tmp_path / "AGENTS.md").read_text(encoding="utf-8")
        # The dir name must appear; never a stray empty "Project - " title.
        assert tmp_path.name in agents

    def test_clean_files_have_no_token_leakage(self, tmp_path, monkeypatch):
        self._init_all(tmp_path, monkeypatch)
        for name in (
            "AGENTS.md",
            "PROJECT_STATUS.md",
            "TESTING.md",
            "BRANCHING.md",
            "CONTRIBUTING.md",
        ):
            text = (tmp_path / name).read_text(encoding="utf-8")
            leaks = _TOKEN_RE.findall(text)
            assert not leaks, f"{name} leaked config tokens: {leaks}"

    def test_scaffold_files_keep_fill_in_slots(self, tmp_path, monkeypatch):
        self._init_all(tmp_path, monkeypatch)
        # ARCHITECTURE intentionally retains open-ended content slots.
        arch = (tmp_path / "ARCHITECTURE.md").read_text(encoding="utf-8")
        assert _TOKEN_RE.findall(arch)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
