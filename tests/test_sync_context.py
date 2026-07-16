"""
Tests for sync_context module — Agent Context manifest generation
and host config mirroring (PROTO-031).
"""

import pytest
from pathlib import Path

from proto_gear_pkg.module_core.sync_context import (
    AGENT_CONTEXT_TOKEN_BUDGET,
    BEGIN_MARKER,
    END_MARKER,
    HOST_FILES,
    _extract_managed_block,
    _update_host_file,
    estimate_tokens,
    generate_agent_context,
    managed_block,
    sync_context,
)


@pytest.fixture
def project(tmp_path):
    """Empty project dir with a minimal PROJECT_STATUS.md so meta extraction works."""
    (tmp_path / "PROJECT_STATUS.md").write_text(
        'project_type: "Python"\nprotogear_version: "v0.9.0"\nrelease_date: "2026-02-19"\n',
        encoding="utf-8",
    )
    return tmp_path


class TestExtractManagedBlock:
    def test_finds_block_between_markers(self):
        content = f"prefix\n{BEGIN_MARKER}\ninner\n{END_MARKER}\nsuffix"
        result = _extract_managed_block(content)
        assert BEGIN_MARKER in result
        assert END_MARKER in result
        assert "inner" in result
        assert "prefix" not in result
        assert "suffix" not in result

    def test_returns_empty_when_missing_markers(self):
        assert _extract_managed_block("no markers here") == ""

    def test_handles_multiline_block(self):
        content = f"{BEGIN_MARKER}\nline1\nline2\nline3\n{END_MARKER}"
        result = _extract_managed_block(content)
        assert "line1" in result and "line2" in result and "line3" in result


class TestUpdateHostFile:
    def test_creates_file_when_missing(self, tmp_path):
        path = tmp_path / "missing.md"
        block = f"{BEGIN_MARKER}\nhello\n{END_MARKER}"
        action = _update_host_file(path, block, dry_run=False)
        assert action == "created"
        assert path.exists()
        assert "hello" in path.read_text(encoding="utf-8")

    def test_dry_run_does_not_write(self, tmp_path):
        path = tmp_path / "missing.md"
        block = f"{BEGIN_MARKER}\nhello\n{END_MARKER}"
        action = _update_host_file(path, block, dry_run=True)
        assert action == "would_create"
        assert not path.exists()

    def test_replaces_existing_managed_region(self, tmp_path):
        path = tmp_path / "host.md"
        old = f"# Title\n\n{BEGIN_MARKER}\nold-content\n{END_MARKER}\n\nuser-content"
        path.write_text(old, encoding="utf-8")
        new_block = f"{BEGIN_MARKER}\nnew-content\n{END_MARKER}"
        action = _update_host_file(path, new_block, dry_run=False)
        assert action == "updated"
        result = path.read_text(encoding="utf-8")
        assert "new-content" in result
        assert "old-content" not in result
        assert "user-content" in result  # outside the block is preserved
        assert "# Title" in result

    def test_prepends_block_when_markers_absent(self, tmp_path):
        path = tmp_path / "host.md"
        path.write_text("just user content", encoding="utf-8")
        block = f"{BEGIN_MARKER}\nblock\n{END_MARKER}"
        action = _update_host_file(path, block, dry_run=False)
        assert action == "updated"
        result = path.read_text(encoding="utf-8")
        assert result.startswith(BEGIN_MARKER)
        assert "just user content" in result

    def test_unchanged_when_block_already_matches(self, tmp_path):
        path = tmp_path / "host.md"
        block = f"{BEGIN_MARKER}\nstatic\n{END_MARKER}"
        path.write_text(block, encoding="utf-8")
        action = _update_host_file(path, block, dry_run=False)
        assert action == "unchanged"


class TestGenerateAgentContext:
    def test_uses_project_dir_name(self, project):
        content = generate_agent_context(project)
        assert project.name in content

    def test_resolves_dot_to_actual_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "PROJECT_STATUS.md").write_text(
            'project_type: "Python"\n', encoding="utf-8"
        )
        content = generate_agent_context(Path("."))
        assert tmp_path.name in content
        # the literal token "{{PROJECT_NAME}}" must never leak through
        assert "{{PROJECT_NAME}}" not in content

    def test_no_unresolved_placeholders(self, project):
        content = generate_agent_context(project)
        for placeholder in (
            "{{PROJECT_NAME}}",
            "{{REFERENCE_INDEX}}",
            "{{CAPABILITIES_SKIM}}",
            "{{CRITICAL_RULES}}",
            "{{WORKING_AGREEMENT}}",
            "{{CLI_COMMANDS}}",
            "{{PROJECT_META}}",
        ):
            assert placeholder not in content, f"Unresolved placeholder: {placeholder}"

    def test_contains_markers(self, project):
        content = generate_agent_context(project)
        assert BEGIN_MARKER in content
        assert END_MARKER in content

    def test_cheatsheet_lists_module_commands(self, project):
        # PROTO-049: pg module + pg --module init-surface must be advertised in
        # the agent-facing CLI cheatsheet, not just implemented.
        content = generate_agent_context(project)
        assert "pg module list/show" in content
        assert "pg --module <name> init-surface" in content

    def test_reads_version_from_status(self, project):
        content = generate_agent_context(project)
        assert "v0.9.0" in content

    def test_marks_missing_files_as_not_present(self, project):
        # project fixture has only PROJECT_STATUS.md
        content = generate_agent_context(project)
        assert "(not present)" in content

    def test_no_capabilities_section_when_dir_missing(self, project):
        content = generate_agent_context(project)
        assert "No capabilities installed" in content

    def test_no_keyword_trigger_table(self, project):
        # PROTO-086: keyword-routing table removed — agents route off descriptions.
        content = generate_agent_context(project)
        assert "Trigger → Capability" not in content
        assert "If user says" not in content

    def test_capability_skim_has_no_keyword_triggers(self):
        # PROTO-086: skim entries carry the description, not a keyword list.
        from proto_gear_pkg.module_core.sync_context import _build_capabilities_skim
        from proto_gear_pkg.module_core.capability_metadata import (
            CapabilityMetadata,
            CapabilityType,
            CapabilityStatus,
            CapabilityDependencies,
            CapabilityRelevance,
        )

        cap = CapabilityMetadata(
            name="testing",
            type=CapabilityType.SKILL,
            version="1.0.0",
            description="TDD methodology",
            category="test",
            tags=[],
            status=CapabilityStatus.STABLE,
            author="test",
            last_updated="2026-01-01",
            dependencies=CapabilityDependencies(required=[], optional=[], suggested=[]),
            conflicts=[],
            composable_with=[],
            agent_roles=[],
            relevance=CapabilityRelevance(triggers=["write tests", "tdd"], contexts=[]),
        )
        skim = _build_capabilities_skim({"skills/testing": cap})
        assert "TDD methodology" in skim
        assert "_triggers:_" not in skim
        assert "write tests" not in skim


class TestTokenBudget:
    def test_estimate_tokens_scales_with_length(self):
        assert estimate_tokens("") == 0
        assert estimate_tokens("word " * 100) > estimate_tokens("word " * 10)

    def test_estimate_tokens_floored_at_word_count(self):
        text = "a b c d e"  # 5 short words, chars//4 == 2
        assert estimate_tokens(text) >= 5

    def test_managed_block_returns_only_block(self, project):
        block = managed_block(project)
        assert block.startswith(BEGIN_MARKER)
        assert block.rstrip().endswith(END_MARKER)

    def test_generated_block_within_budget(self, project):
        # The slim generated block must stay under the shipped budget.
        assert estimate_tokens(managed_block(project)) <= AGENT_CONTEXT_TOKEN_BUDGET


class TestSyncContext:
    def test_creates_all_files_on_fresh_project(self, project):
        results = sync_context(project, dry_run=False)
        assert results["AGENT_CONTEXT.md"] == "created"
        for hf in HOST_FILES:
            assert results[hf] == "created"
            assert (project / hf).exists()

    def test_idempotent(self, project):
        sync_context(project, dry_run=False)
        results = sync_context(project, dry_run=False)
        assert results["AGENT_CONTEXT.md"] == "unchanged"
        for hf in HOST_FILES:
            assert results[hf] == "unchanged"

    def test_dry_run_creates_nothing(self, project):
        results = sync_context(project, dry_run=False)  # first real run
        # touch user content in a host file
        (project / "CLAUDE.md").write_text(
            (project / "CLAUDE.md").read_text(encoding="utf-8") + "\n\n# user note",
            encoding="utf-8",
        )
        # mutate trigger by writing a fake new template? No — just verify dry-run reports
        # something without writing. Simulate by deleting AGENT_CONTEXT.md.
        (project / "AGENT_CONTEXT.md").unlink()
        results = sync_context(project, dry_run=True)
        assert results["AGENT_CONTEXT.md"] == "would_create"
        assert not (project / "AGENT_CONTEXT.md").exists()

    def test_preserves_user_content_outside_block(self, project):
        sync_context(project, dry_run=False)
        claude = project / "CLAUDE.md"
        original = claude.read_text(encoding="utf-8")
        # append user content
        claude.write_text(original + "\n\n# my custom notes\n", encoding="utf-8")
        # re-sync
        sync_context(project, dry_run=False)
        assert "# my custom notes" in claude.read_text(encoding="utf-8")

    def test_handles_nested_github_path(self, project):
        sync_context(project, dry_run=False)
        copilot = project / ".github" / "copilot-instructions.md"
        assert copilot.exists()
        assert BEGIN_MARKER in copilot.read_text(encoding="utf-8")
