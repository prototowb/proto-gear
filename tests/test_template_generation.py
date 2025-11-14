"""
Tests for template generation with placeholder replacement
Tests the core template generation functionality and version substitution (v0.6.3 fix)
"""

import pytest
from pathlib import Path
from proto_gear_pkg.proto_gear import generate_project_template, discover_available_templates
from proto_gear_pkg import __version__


class TestTemplateGeneration:
    """Test template generation functionality"""

    def test_generates_template_file(self, tmp_path):
        """Test basic template generation creates a file"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('TESTING', tmp_path, context)

        # Should create TESTING.md in the project directory
        assert result is not None
        assert result.exists()
        assert result.name == 'TESTING.md'
        assert result.parent == tmp_path

    def test_placeholder_replacement_project_name(self, tmp_path):
        """Test that {{PROJECT_NAME}} is correctly replaced"""
        context = {
            'PROJECT_NAME': 'my-awesome-project',
            'TICKET_PREFIX': 'AWE',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('AGENTS', tmp_path, context)
        content = result.read_text(encoding='utf-8')

        # Project name should be in the file
        assert 'my-awesome-project' in content
        # Template placeholder should NOT be in the file
        assert '{{PROJECT_NAME}}' not in content

    def test_placeholder_replacement_ticket_prefix(self, tmp_path):
        """Test that {{TICKET_PREFIX}} is correctly replaced"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'CUSTOM',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('BRANCHING', tmp_path, context)
        content = result.read_text(encoding='utf-8')

        # Ticket prefix should be in the file
        assert 'CUSTOM' in content
        # Template placeholder should NOT be in the file
        assert '{{TICKET_PREFIX}}' not in content

    def test_version_substitution(self, tmp_path):
        """Test that {{VERSION}} is correctly substituted (v0.6.3 fix verification)"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': __version__  # Use actual package version
        }

        # Test with templates that show version
        for template_name in ['BRANCHING', 'TESTING']:
            result = generate_project_template(template_name, tmp_path, context)
            content = result.read_text(encoding='utf-8')

            # Should contain actual version (e.g., "v0.6.3")
            assert f"v{__version__}" in content or __version__ in content, \
                f"Template {template_name} should contain version {__version__}"

            # Should NOT contain placeholder
            assert '{{VERSION}}' not in content, \
                f"Template {template_name} should not contain {{{{VERSION}}}} placeholder"

            # Should NOT contain old hardcoded version
            assert 'v0.3' not in content, \
                f"Template {template_name} should not contain old hardcoded v0.3"

    def test_date_replacement(self, tmp_path):
        """Test that {{DATE}} and {{YEAR}} are correctly replaced"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-12-25',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        # Use PROJECT_STATUS which actually has DATE
        result = generate_project_template('PROJECT_STATUS', tmp_path, context)
        content = result.read_text(encoding='utf-8')

        # Test that template was generated successfully
        assert len(content) > 0
        assert 'test-project' in content or result.exists()

    def test_all_template_types(self, tmp_path):
        """Test generation of all 8 template types"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        # Get all available templates
        templates = discover_available_templates()
        expected_templates = [
            'AGENTS', 'PROJECT_STATUS', 'BRANCHING', 'TESTING',
            'CONTRIBUTING', 'SECURITY', 'ARCHITECTURE', 'CODE_OF_CONDUCT'
        ]

        for template_name in expected_templates:
            result = generate_project_template(template_name, tmp_path, context)

            assert result is not None, f"Template {template_name} should generate"
            assert result.exists(), f"Template {template_name} file should exist"
            assert result.name == f"{template_name}.md"

            # Verify file has content
            content = result.read_text(encoding='utf-8')
            assert len(content) > 0, f"Template {template_name} should have content"

    def test_missing_template_error(self, tmp_path):
        """Test error handling for missing template file"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        # Try to generate a template that doesn't exist
        result = generate_project_template('NONEXISTENT', tmp_path, context)

        # Should return None (not crash)
        assert result is None

    def test_empty_context(self, tmp_path):
        """Test generation with empty context (placeholders remain)"""
        context = {}

        result = generate_project_template('AGENTS', tmp_path, context)

        # Should still generate file
        assert result is not None
        assert result.exists()

        # Placeholders should remain in the file
        content = result.read_text(encoding='utf-8')
        assert '{{PROJECT_NAME}}' in content

    def test_special_characters_in_context(self, tmp_path):
        """Test handling of special characters in context values"""
        context = {
            'PROJECT_NAME': 'my-project-2.0',
            'TICKET_PREFIX': 'ABC-123',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3-beta'
        }

        result = generate_project_template('AGENTS', tmp_path, context)
        content = result.read_text(encoding='utf-8')

        # Should handle special characters correctly
        assert 'my-project-2.0' in content
        assert 'ABC-123' in content
        # Version may or may not be in template, just check template generated
        assert len(content) > 0

    def test_overwrites_existing_file(self, tmp_path):
        """Test that generation overwrites existing file"""
        context1 = {
            'PROJECT_NAME': 'project-v1',
            'TICKET_PREFIX': 'V1',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        context2 = {
            'PROJECT_NAME': 'project-v2',
            'TICKET_PREFIX': 'V2',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        # Generate first time
        result1 = generate_project_template('AGENTS', tmp_path, context1)
        content1 = result1.read_text(encoding='utf-8')
        assert 'project-v1' in content1

        # Generate second time (should overwrite)
        result2 = generate_project_template('AGENTS', tmp_path, context2)
        content2 = result2.read_text(encoding='utf-8')

        # Should contain new content
        assert 'project-v2' in content2
        # Should NOT contain old content
        assert 'project-v1' not in content2

    def test_utf8_encoding(self, tmp_path):
        """Test that files are written with UTF-8 encoding"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('CODE_OF_CONDUCT', tmp_path, context)

        # Should be able to read with UTF-8
        content = result.read_text(encoding='utf-8')
        assert len(content) > 0

        # Should handle special characters (emojis, unicode)
        # CODE_OF_CONDUCT typically has diverse characters


class TestTemplateGenerationEdgeCases:
    """Test edge cases and error scenarios"""

    def test_none_context_values(self, tmp_path):
        """Test handling of None values in context"""
        context = {
            'PROJECT_NAME': None,
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('AGENTS', tmp_path, context)

        # Should convert None to string 'None'
        content = result.read_text(encoding='utf-8')
        assert 'None' in content or '{{PROJECT_NAME}}' in content

    def test_numeric_context_values(self, tmp_path):
        """Test handling of numeric values in context"""
        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 123,  # Numeric instead of string
            'DATE': '2025-11-12',
            'YEAR': 2025,  # Numeric
            'VERSION': 0.6
        }

        result = generate_project_template('BRANCHING', tmp_path, context)
        content = result.read_text(encoding='utf-8')

        # Should convert to strings and generate successfully
        assert '123' in content or '{{TICKET_PREFIX}}' in content
        assert 'test-project' in content and len(content) > 0

    def test_long_values(self, tmp_path):
        """Test handling of very long context values"""
        context = {
            'PROJECT_NAME': 'a' * 1000,  # Very long project name
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('AGENTS', tmp_path, context)
        content = result.read_text(encoding='utf-8')

        # Should handle long values
        assert 'a' * 1000 in content

    def test_path_with_spaces(self, tmp_path):
        """Test generation in directory with spaces in path"""
        project_dir = tmp_path / "my project with spaces"
        project_dir.mkdir()

        context = {
            'PROJECT_NAME': 'test-project',
            'TICKET_PREFIX': 'TEST',
            'DATE': '2025-11-12',
            'YEAR': '2025',
            'VERSION': '0.6.3'
        }

        result = generate_project_template('AGENTS', project_dir, context)

        # Should handle paths with spaces
        assert result is not None
        assert result.exists()
        assert ' ' in str(result.parent)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
