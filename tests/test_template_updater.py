"""
Unit Tests for Template Updater Module

Tests extraction, merging, validation, and diff generation for safe
template updates.
"""

import pytest
import yaml
from pathlib import Path
from textwrap import dedent

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear_pkg.template_updater import (
    UserDataExtractor,
    TemplateMerger,
    DiffGenerator,
    TemplateValidator,
    TemplateUpdater,
    ExtractedData,
    ExtractionError,
    MergeError,
    ValidationError,
)


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def sample_project_status_content():
    """Sample PROJECT_STATUS.md with user data"""
    return dedent("""
        # PROJECT STATUS - My Project

        > **Single Source of Truth** for project state

        ## Current State

        ```yaml
        project_phase: "Development"
        protogear_enabled: true
        protogear_version: "v0.8.0"
        current_sprint: 42
        current_branch: "feature/test"
        ```

        ## 🎫 Active Tickets

        | ID | Title | Type | Status | Branch | Assignee |
        |----|-------|------|--------|--------|----------|
        | TEST-001 | Add feature X | feature | IN_PROGRESS | feature/test | Alice |
        | TEST-002 | Fix bug Y | bugfix | PENDING | bugfix/fix-y | Bob |

        ## ✅ Completed Tickets

        | ID | Title | Completed | PR/Commit |
        |----|-------|-----------|-----------|
        | TEST-000 | Initial setup | 2025-01-01 | abc1234 |

        ## 🔄 Recent Updates

        - 2025-01-05: Added feature X (TEST-001)
        - 2025-01-03: Fixed critical bug (TEST-000)

        ## 📊 Feature Progress

        | Feature | Status | Progress |
        |---------|--------|----------|
        | Authentication | In Progress | 75% |
        | Dashboard | Complete | 100% |
    """).strip()


@pytest.fixture
def sample_project_context():
    """Sample project context for placeholders"""
    return {
        'PROJECT_NAME': 'Test Project',
        'TICKET_PREFIX': 'TEST',
        'VERSION': '0.8.2',
        'MAIN_BRANCH': 'main',
        'DEV_BRANCH': 'development',
    }


# ============================================================================
# UserDataExtractor Tests
# ============================================================================

class TestUserDataExtractor:
    """Tests for UserDataExtractor class"""

    def test_extract_project_status_yaml_blocks(self, sample_project_status_content):
        """Extract YAML blocks from PROJECT_STATUS.md"""
        extractor = UserDataExtractor()
        result = extractor.extract(sample_project_status_content, 'PROJECT_STATUS')

        assert 'current_state' in result.yaml_blocks
        state = result.yaml_blocks['current_state']
        assert state['project_phase'] == 'Development'
        assert state['current_sprint'] == 42
        assert state['current_branch'] == 'feature/test'

    def test_extract_active_tickets_table(self, sample_project_status_content):
        """Extract Active Tickets table"""
        extractor = UserDataExtractor()
        result = extractor.extract(sample_project_status_content, 'PROJECT_STATUS')

        assert 'active_tickets' in result.table_sections
        active_tickets = result.table_sections['active_tickets']
        assert 'TEST-001' in active_tickets
        assert 'TEST-002' in active_tickets
        assert 'Add feature X' in active_tickets
        assert 'Alice' in active_tickets

    def test_extract_completed_tickets_table(self, sample_project_status_content):
        """Extract Completed Tickets table"""
        extractor = UserDataExtractor()
        result = extractor.extract(sample_project_status_content, 'PROJECT_STATUS')

        assert 'completed_tickets' in result.table_sections
        completed = result.table_sections['completed_tickets']
        assert 'TEST-000' in completed
        assert 'Initial setup' in completed
        assert '2025-01-01' in completed

    def test_extract_recent_updates(self, sample_project_status_content):
        """Extract Recent Updates section"""
        extractor = UserDataExtractor()
        result = extractor.extract(sample_project_status_content, 'PROJECT_STATUS')

        assert 'recent_updates' in result.freeform_sections
        updates = result.freeform_sections['recent_updates']
        assert '2025-01-05' in updates
        assert 'Added feature X' in updates

    def test_extract_feature_progress(self, sample_project_status_content):
        """Extract Feature Progress table"""
        extractor = UserDataExtractor()
        result = extractor.extract(sample_project_status_content, 'PROJECT_STATUS')

        assert 'feature_progress' in result.freeform_sections
        progress = result.freeform_sections['feature_progress']
        assert 'Authentication' in progress
        assert '75%' in progress

    def test_extraction_handles_missing_sections(self):
        """Gracefully handle missing optional sections"""
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

        extractor = UserDataExtractor()
        result = extractor.extract(minimal_content, 'PROJECT_STATUS')

        # Should extract what's present
        assert 'current_state' in result.yaml_blocks
        assert 'active_tickets' in result.table_sections

        # Missing sections should be absent (not error)
        assert 'recent_updates' not in result.freeform_sections
        assert 'feature_progress' not in result.freeform_sections

    def test_extraction_handles_corrupted_yaml(self):
        """Preserve raw YAML if parsing fails"""
        corrupted_content = dedent("""
            # PROJECT STATUS

            ## Current State

            ```yaml
            project_phase: "Development
            # Missing closing quote
            current_sprint: invalid_number
            ```

            ## 🎫 Active Tickets

            | ID | Title | Type | Status | Branch | Assignee |
            |----|-------|------|--------|--------|----------|
            | - | No tickets | - | - | - | - |

            ## ✅ Completed Tickets

            | ID | Title | Completed | PR/Commit |
            |----|-------|-----------|-----------|
            | - | No tickets | - | - |
        """).strip()

        extractor = UserDataExtractor()
        result = extractor.extract(corrupted_content, 'PROJECT_STATUS')

        # Should still extract YAML block (as raw string)
        assert 'current_state' in result.yaml_blocks

    def test_unsupported_template_raises_error(self):
        """Raise error for unsupported template"""
        extractor = UserDataExtractor()

        with pytest.raises(ExtractionError, match="No extraction patterns"):
            extractor.extract("content", "UNSUPPORTED")

    def test_extract_agents_not_implemented(self):
        """AGENTS.md extraction returns placeholder (Phase 3)"""
        extractor = UserDataExtractor()
        result = extractor.extract("# AGENTS.md content", "AGENTS")

        # Currently returns empty data with note
        assert result.metadata.get('note') == 'AGENTS.md extraction not yet implemented'


# ============================================================================
# TemplateMerger Tests
# ============================================================================

class TestTemplateMerger:
    """Tests for TemplateMerger class"""

    def test_merge_preserves_all_tickets(self, tmp_path, sample_project_context):
        """Merged content preserves all user tickets"""
        # Create a minimal template
        template_content = dedent("""
            # PROJECT STATUS - {{PROJECT_NAME}}

            ## Current State

            ```yaml
            project_phase: "Production"
            protogear_version: "{{VERSION}}"
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

        # Create template file
        template_dir = tmp_path / 'templates'
        template_dir.mkdir()
        template_file = template_dir / 'PROJECT_STATUS.template.md'
        template_file.write_text(template_content, encoding='utf-8')

        # Extracted user data
        extracted_data = ExtractedData(
            yaml_blocks={'current_state': {
                'project_phase': 'Development',
                'protogear_version': 'v0.8.1',
                'current_sprint': 42,
            }},
            table_sections={
                'active_tickets': dedent("""
                    | ID | Title | Type | Status | Branch | Assignee |
                    |----|-------|------|--------|--------|----------|
                    | TEST-001 | Feature X | feature | IN_PROGRESS | feature/x | Alice |
                """).strip(),
                'completed_tickets': dedent("""
                    | ID | Title | Completed | PR/Commit |
                    |----|-------|-----------|-----------|
                    | TEST-000 | Setup | 2025-01-01 | abc123 |
                """).strip(),
            },
            freeform_sections={},
            metadata={}
        )

        merger = TemplateMerger(template_dir)
        merged = merger.merge('PROJECT_STATUS', extracted_data, sample_project_context)

        # Verify tickets preserved
        assert 'TEST-001' in merged
        assert 'Feature X' in merged
        assert 'Alice' in merged
        assert 'TEST-000' in merged
        assert 'Setup' in merged

        # Verify YAML preserved
        assert 'current_sprint: 42' in merged

        # Verify placeholders replaced
        assert '{{PROJECT_NAME}}' not in merged
        assert 'Test Project' in merged

    def test_merge_updates_static_sections(self, tmp_path, sample_project_context):
        """Merged content uses new template structure"""
        # Template with new section
        template_content = dedent("""
            # PROJECT STATUS - {{PROJECT_NAME}}

            ## NEW SECTION: State Management Guide

            This is a new section that didn't exist before.

            ## Current State

            ```yaml
            project_phase: "Production"
            ```

            ## 🎫 Active Tickets

            | ID | Title | Type | Status | Branch | Assignee |
            |----|-------|------|--------|--------|----------|
            | - | No tickets | - | - | - | - |

            ## ✅ Completed Tickets

            | ID | Title | Completed | PR/Commit |
            |----|-------|-----------|-----------|
            | - | No tickets | - | - |
        """).strip()

        template_dir = tmp_path / 'templates'
        template_dir.mkdir()
        template_file = template_dir / 'PROJECT_STATUS.template.md'
        template_file.write_text(template_content, encoding='utf-8')

        extracted_data = ExtractedData(
            yaml_blocks={'current_state': {'project_phase': 'Development'}},
            table_sections={
                'active_tickets': '| ID | Title | Type | Status | Branch | Assignee |\n|----|-------|------|--------|--------|----------|\n| - | No tickets | - | - | - | - |',
                'completed_tickets': '| ID | Title | Completed | PR/Commit |\n|----|-------|-----------|-----------|',
            },
            freeform_sections={},
            metadata={}
        )

        merger = TemplateMerger(template_dir)
        merged = merger.merge('PROJECT_STATUS', extracted_data, sample_project_context)

        # New section should appear
        assert 'NEW SECTION: State Management Guide' in merged
        assert "This is a new section that didn't exist before" in merged

    def test_merge_handles_missing_template(self, tmp_path, sample_project_context):
        """Raise error if template file not found"""
        merger = TemplateMerger(tmp_path)

        with pytest.raises(MergeError, match="Template file not found"):
            merger.merge('NONEXISTENT', ExtractedData({}, {}, {}, {}), sample_project_context)


# ============================================================================
# DiffGenerator Tests
# ============================================================================

class TestDiffGenerator:
    """Tests for DiffGenerator class"""

    def test_generate_unified_diff(self):
        """Generate proper unified diff format"""
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2 Modified\nLine 3\nLine 4"

        diff, stats = DiffGenerator.generate(old_content, new_content, 'test.md')

        # Check diff contains expected markers
        assert '---' in diff  # Old file marker
        assert '+++' in diff  # New file marker
        assert 'Line 2 Modified' in diff
        assert 'Line 4' in diff

    def test_diff_summary_counts_changes(self):
        """Accurately count added/removed lines"""
        old_content = "Line 1\nLine 2\nLine 3"
        new_content = "Line 1\nLine 2 Modified\nLine 3\nLine 4"

        _, stats = DiffGenerator.generate(old_content, new_content, 'test.md')

        # Unified diff counts context lines too, so actual counts may vary
        assert stats['lines_added'] >= 2  # At least Line 2 Modified and Line 4
        assert stats['lines_removed'] >= 1  # At least old Line 2
        assert stats['total_lines_old'] == 3
        assert stats['total_lines_new'] == 4

    def test_diff_handles_empty_content(self):
        """Handle empty old or new content"""
        old_content = ""
        new_content = "New Line 1\nNew Line 2"

        diff, stats = DiffGenerator.generate(old_content, new_content, 'test.md')

        assert stats['lines_added'] == 2
        assert stats['lines_removed'] == 0


# ============================================================================
# TemplateValidator Tests
# ============================================================================

class TestTemplateValidator:
    """Tests for TemplateValidator class"""

    def test_validation_detects_unreplaced_placeholders(self):
        """Warn about unreplaced placeholders"""
        content = dedent("""
            # PROJECT STATUS - {{PROJECT_NAME}}

            Version: {{VERSION}}

            ## Active Tickets

            | ID | Title |
            |----|-------|
            | - | None |

            ## Completed Tickets

            | ID | Title |
            |----|-------|
            | - | None |
        """).strip()

        is_valid, warnings = TemplateValidator.validate(content, 'PROJECT_STATUS')

        assert not is_valid
        assert len(warnings) == 1
        assert 'Unreplaced placeholders' in warnings[0]
        assert 'PROJECT_NAME' in warnings[0]
        assert 'VERSION' in warnings[0]

    def test_validation_checks_yaml_syntax(self):
        """Detect invalid YAML blocks"""
        content = dedent("""
            # PROJECT STATUS

            ```yaml
            project_phase: "Development
            # Missing closing quote
            current_sprint: not_a_number
            ```
        """).strip()

        is_valid, warnings = TemplateValidator.validate(content, 'PROJECT_STATUS')

        assert not is_valid
        assert any('YAML block' in w for w in warnings)

    def test_validation_checks_table_count(self):
        """Check for minimum required tables in PROJECT_STATUS"""
        content = dedent("""
            # PROJECT STATUS

            ```yaml
            project_phase: "Development"
            ```

            ## Active Tickets

            | ID | Title |
            |----|-------|
            | - | None |
        """).strip()

        is_valid, warnings = TemplateValidator.validate(content, 'PROJECT_STATUS')

        assert not is_valid
        assert any('Expected at least 2 tables' in w for w in warnings)

    def test_validation_passes_for_valid_content(self):
        """Valid content passes validation"""
        content = dedent("""
            # PROJECT STATUS

            ```yaml
            project_phase: "Development"
            current_sprint: 42
            ```

            ## Active Tickets

            | ID | Title | Status |
            |----|-------|--------|
            | TEST-001 | Test | IN_PROGRESS |

            ## Completed Tickets

            | ID | Title | Completed |
            |----|-------|-----------|
            | TEST-000 | Done | 2025-01-01 |
        """).strip()

        is_valid, warnings = TemplateValidator.validate(content, 'PROJECT_STATUS')

        assert is_valid
        assert len(warnings) == 0


# ============================================================================
# TemplateUpdater Integration Tests (Basic)
# ============================================================================

class TestTemplateUpdaterBasic:
    """Basic integration tests for TemplateUpdater"""

    def test_updater_initialization(self, tmp_path):
        """TemplateUpdater initializes correctly"""
        updater = TemplateUpdater(tmp_path)

        assert updater.project_dir == tmp_path
        assert updater.extractor is not None
        assert updater.merger is not None

    def test_update_nonexistent_file_raises_error(self, tmp_path):
        """Raise error if file to update doesn't exist"""
        updater = TemplateUpdater(tmp_path)

        with pytest.raises(Exception, match="File not found|Cannot update non-existent"):
            updater.update_template(
                'PROJECT_STATUS',
                {'PROJECT_NAME': 'Test'},
                dry_run=True
            )


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
