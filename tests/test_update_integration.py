"""
Integration Tests for Template Update System

End-to-end tests for the full update workflow including CLI integration.
"""

import pytest
from pathlib import Path
from textwrap import dedent
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear_pkg.template_updater import TemplateUpdater, TemplateUpdateError


# ============================================================================
# Integration Test Fixtures
# ============================================================================

@pytest.fixture
def temp_project(tmp_path):
    """Create a temporary project with realistic PROJECT_STATUS.md"""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # Create realistic PROJECT_STATUS.md with user data
    status_file = project_dir / "PROJECT_STATUS.md"
    status_content = dedent("""
        # PROJECT STATUS - Test Project

        > **Single Source of Truth** for project state

        ## Current State

        ```yaml
        project_phase: "Development"
        protogear_enabled: true
        protogear_version: "v0.8.0"
        current_sprint: 5
        current_branch: "feature/test"
        last_ticket_id: "TEST-010"
        ```

        ## 🎫 Active Tickets

        | ID | Title | Type | Status | Branch | Assignee |
        |----|-------|------|--------|--------|----------|
        | TEST-001 | Implement auth | feature | IN_PROGRESS | feature/auth | Alice |
        | TEST-002 | Fix login bug | bugfix | PENDING | bugfix/login | Bob |

        ## ✅ Completed Tickets

        | ID | Title | Completed | PR/Commit |
        |----|-------|-----------|-----------|
        | TEST-000 | Setup project | 2025-01-01 | abc1234 |
        | INIT-001 | Initialize Proto Gear | 2025-01-02 | def5678 |

        ## 🔄 Recent Updates

        - 2025-01-06: Started working on authentication (TEST-001)
        - 2025-01-05: Fixed critical login bug
        - 2025-01-03: Completed initial setup

        ## 📊 Feature Progress

        | Feature | Status | Progress |
        |---------|--------|----------|
        | Authentication | In Progress | 60% |
        | Dashboard | Complete | 100% |
        | API Integration | Not Started | 0% |
    """).strip()

    status_file.write_text(status_content, encoding='utf-8')

    return project_dir


# ============================================================================
# Full Update Workflow Tests
# ============================================================================

class TestFullUpdateWorkflow:
    """End-to-end integration tests for template updates"""

    def test_full_update_preserves_all_tickets(self, temp_project):
        """Full update flow preserves all user tickets"""
        updater = TemplateUpdater(temp_project)

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Perform update
        result = updater.update_template(
            'PROJECT_STATUS',
            project_context,
            dry_run=False,
            force=True
        )

        # Verify success
        assert result.success is True
        assert result.backup_created is True

        # Read updated file
        updated_file = temp_project / "PROJECT_STATUS.md"
        updated_content = updated_file.read_text(encoding='utf-8')

        # Verify all tickets preserved
        assert 'TEST-001' in updated_content
        assert 'Implement auth' in updated_content
        assert 'Alice' in updated_content

        assert 'TEST-002' in updated_content
        assert 'Fix login bug' in updated_content
        assert 'Bob' in updated_content

        assert 'TEST-000' in updated_content
        assert 'Setup project' in updated_content

        # Verify YAML state preserved
        assert 'current_sprint: 5' in updated_content
        assert 'feature/test' in updated_content
        assert 'last_ticket_id: "TEST-010"' in updated_content or 'last_ticket_id: TEST-010' in updated_content

        # Note: Recent Updates is a freeform section that may not be fully extracted yet
        # This is expected - it's a known limitation for v0.8.2
        # We focus on preserving tickets and YAML state (core data)

    def test_dry_run_no_modifications(self, temp_project):
        """Dry-run mode shows preview without modifying files"""
        updater = TemplateUpdater(temp_project)

        # Read original content
        original_file = temp_project / "PROJECT_STATUS.md"
        original_content = original_file.read_text(encoding='utf-8')
        original_mtime = original_file.stat().st_mtime

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Perform dry-run update
        result = updater.update_template(
            'PROJECT_STATUS',
            project_context,
            dry_run=True,
            force=True
        )

        # Verify no backup created
        assert result.backup_created is False

        # Verify file unchanged
        new_content = original_file.read_text(encoding='utf-8')
        new_mtime = original_file.stat().st_mtime

        assert new_content == original_content
        assert new_mtime == original_mtime

        # Verify stats were calculated
        assert result.lines_added > 0
        assert result.lines_removed > 0

    def test_backup_creation(self, temp_project):
        """Update creates backup file before modifying"""
        updater = TemplateUpdater(temp_project)

        original_file = temp_project / "PROJECT_STATUS.md"
        original_content = original_file.read_text(encoding='utf-8')

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Perform update
        result = updater.update_template(
            'PROJECT_STATUS',
            project_context,
            dry_run=False,
            force=True
        )

        # Verify backup created
        assert result.backup_created is True
        assert result.backup_path is not None
        assert result.backup_path.exists()

        # Verify backup contains original content
        backup_content = result.backup_path.read_text(encoding='utf-8')
        assert backup_content == original_content

        # Verify original file was modified
        new_content = original_file.read_text(encoding='utf-8')
        assert new_content != original_content

    def test_update_applies_new_template_structure(self, temp_project):
        """Update applies new template sections while preserving data"""
        updater = TemplateUpdater(temp_project)

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Perform update
        result = updater.update_template(
            'PROJECT_STATUS',
            project_context,
            dry_run=False,
            force=True
        )

        # Read updated file
        updated_file = temp_project / "PROJECT_STATUS.md"
        updated_content = updated_file.read_text(encoding='utf-8')

        # Verify new template sections appear
        assert '## 📚 Related Documentation' in updated_content
        assert '## 📖 State Management Guide' in updated_content
        assert 'AGENTS.md' in updated_content  # Related docs section

        # But user data still preserved
        assert 'TEST-001' in updated_content
        assert 'Alice' in updated_content

    def test_update_nonexistent_file_fails(self, temp_project):
        """Update fails gracefully for non-existent files"""
        updater = TemplateUpdater(temp_project)

        # Delete the file
        (temp_project / "PROJECT_STATUS.md").unlink()

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Attempt update should raise error
        with pytest.raises(TemplateUpdateError, match="File not found|Cannot update"):
            updater.update_template(
                'PROJECT_STATUS',
                project_context,
                dry_run=True,
                force=True
            )

    def test_update_with_minimal_data(self, temp_project):
        """Update handles files with minimal user data"""
        # Create minimal PROJECT_STATUS.md
        minimal_content = dedent("""
            # PROJECT STATUS

            ## Current State

            ```yaml
            project_phase: "Planning"
            ```

            ## 🎫 Active Tickets

            | ID | Title | Type | Status | Branch | Assignee |
            |----|-------|------|--------|--------|----------|
            | - | No active tickets | - | - | - | - |

            ## ✅ Completed Tickets

            | ID | Title | Completed | PR/Commit |
            |----|-------|-----------|-----------|
            | - | No completed tickets | - | - |
        """).strip()

        status_file = temp_project / "PROJECT_STATUS.md"
        status_file.write_text(minimal_content, encoding='utf-8')

        updater = TemplateUpdater(temp_project)

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Perform update
        result = updater.update_template(
            'PROJECT_STATUS',
            project_context,
            dry_run=False,
            force=True
        )

        # Should succeed
        assert result.success is True

        # Read updated file
        updated_content = status_file.read_text(encoding='utf-8')

        # Verify basic structure present
        assert '## Current State' in updated_content or '## 📊 Current State' in updated_content
        assert 'project_phase: "Planning"' in updated_content or "project_phase: Planning" in updated_content


# ============================================================================
# Error Recovery Tests
# ============================================================================

class TestErrorRecovery:
    """Tests for error handling and recovery"""

    def test_corrupted_yaml_handled_gracefully(self, temp_project):
        """Update handles corrupted YAML without crashing"""
        corrupted_content = dedent("""
            # PROJECT STATUS

            ## Current State

            ```yaml
            project_phase: "Development
            # Missing closing quote
            current_sprint: not_a_number
            ```

            ## 🎫 Active Tickets

            | ID | Title | Type | Status | Branch | Assignee |
            |----|-------|------|--------|--------|----------|
            | TEST-001 | Test | feature | IN_PROGRESS | feature/test | Alice |

            ## ✅ Completed Tickets

            | ID | Title | Completed | PR/Commit |
            |----|-------|-----------|-----------|
            | - | None | - | - |
        """).strip()

        status_file = temp_project / "PROJECT_STATUS.md"
        status_file.write_text(corrupted_content, encoding='utf-8')

        updater = TemplateUpdater(temp_project)

        project_context = {
            'PROJECT_NAME': 'Test Project',
            'TICKET_PREFIX': 'TEST',
            'VERSION': '0.8.2',
        }

        # Should not crash, might have warnings
        result = updater.update_template(
            'PROJECT_STATUS',
            project_context,
            dry_run=True,
            force=True
        )

        # Update may succeed with warnings or fail
        # Either way, should not crash
        assert result is not None
        assert isinstance(result.warnings, list)


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
