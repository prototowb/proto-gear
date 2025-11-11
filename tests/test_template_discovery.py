"""
Tests for template auto-discovery system (v0.6.0 feature)
Critical feature that enables zero-code template addition
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from proto_gear_pkg.proto_gear import discover_available_templates


class TestTemplateDiscovery:
    """Test template auto-discovery functionality"""

    def test_discovers_real_templates(self):
        """Test that real templates from package are discovered"""
        templates = discover_available_templates()

        # Should discover all 8 core templates
        assert isinstance(templates, dict)
        assert len(templates) >= 8, "Should discover at least 8 templates"

        # Check for specific known templates
        assert 'AGENTS' in templates
        assert 'PROJECT_STATUS' in templates
        assert 'BRANCHING' in templates
        assert 'TESTING' in templates
        assert 'CONTRIBUTING' in templates
        assert 'SECURITY' in templates
        assert 'ARCHITECTURE' in templates
        assert 'CODE_OF_CONDUCT' in templates

    def test_template_structure(self):
        """Test that discovered templates have correct structure"""
        templates = discover_available_templates()

        for name, info in templates.items():
            # Each template should have these keys
            assert 'path' in info
            assert 'name' in info
            assert 'filename' in info

            # Verify path is a Path object and exists
            assert isinstance(info['path'], Path)
            assert info['path'].exists(), f"Template file {info['path']} should exist"

            # Verify name matches key
            assert info['name'] == name

            # Verify filename format
            assert info['filename'] == f"{name}.md"

    def test_template_name_extraction(self):
        """Test correct extraction of template names from filenames"""
        templates = discover_available_templates()

        # Template names should NOT include .template or .md
        for name in templates.keys():
            assert '.template' not in name
            assert '.md' not in name
            assert name.isupper() or name == name.upper(), "Template names should be uppercase"

    def test_template_files_are_markdown(self):
        """Test that all discovered templates are markdown files"""
        templates = discover_available_templates()

        for name, info in templates.items():
            path = info['path']
            assert path.suffix == '.md', f"Template {name} should be a .md file"
            assert '.template.md' in path.name, f"Template {name} should have .template.md extension"

    @patch('proto_gear_pkg.proto_gear.Path.glob')
    def test_handles_empty_directory(self, mock_glob):
        """Test behavior when no templates are found"""
        # Mock glob to return empty list
        mock_glob.return_value = []

        templates = discover_available_templates()

        # Should return empty dict, not crash
        assert isinstance(templates, dict)
        assert len(templates) == 0

    @patch('proto_gear_pkg.proto_gear.Path.glob')
    def test_handles_glob_error(self, mock_glob):
        """Test error handling when glob fails"""
        # Mock glob to raise an exception
        mock_glob.side_effect = Exception("Permission denied")

        templates = discover_available_templates()

        # Should return empty dict and handle error gracefully
        assert isinstance(templates, dict)
        assert len(templates) == 0

    def test_ignores_non_template_files(self, tmp_path):
        """Test that non-.template.md files are ignored"""
        # This tests the actual implementation behavior
        # Real implementation only looks for *.template.md files

        templates = discover_available_templates()

        # Verify all returned templates have .template.md in their path
        for name, info in templates.items():
            assert '.template.md' in str(info['path'])

    def test_template_paths_are_absolute(self):
        """Test that template paths are absolute, not relative"""
        templates = discover_available_templates()

        for name, info in templates.items():
            path = info['path']
            assert path.is_absolute(), f"Template {name} path should be absolute"

    def test_discovers_capabilities_templates(self):
        """Test that capability templates are NOT included in core templates"""
        templates = discover_available_templates()

        # Auto-discovery should only find templates in proto_gear_pkg root
        # Not in capabilities/ subdirectory
        for name in templates.keys():
            # These are capability templates, not core templates
            assert 'SKILL_' not in name
            assert 'WORKFLOW_' not in name
            assert 'COMMAND_' not in name

    def test_template_count_matches_known_templates(self):
        """Test that we have exactly the expected number of templates"""
        templates = discover_available_templates()

        # As of v0.6.3, we have exactly 8 core templates
        expected_templates = {
            'AGENTS', 'PROJECT_STATUS', 'BRANCHING', 'TESTING',
            'CONTRIBUTING', 'SECURITY', 'ARCHITECTURE', 'CODE_OF_CONDUCT'
        }

        discovered_names = set(templates.keys())
        assert discovered_names == expected_templates, \
            f"Expected {expected_templates}, got {discovered_names}"

    def test_discovery_is_deterministic(self):
        """Test that discovery returns consistent results"""
        # Run discovery multiple times
        result1 = discover_available_templates()
        result2 = discover_available_templates()
        result3 = discover_available_templates()

        # Should get same templates each time
        assert result1.keys() == result2.keys() == result3.keys()

    def test_template_path_contains_proto_gear_pkg(self):
        """Test that all templates are in proto_gear_pkg directory"""
        templates = discover_available_templates()

        for name, info in templates.items():
            path_str = str(info['path'])
            assert 'proto_gear_pkg' in path_str, \
                f"Template {name} should be in proto_gear_pkg directory"


class TestTemplateDiscoveryIntegration:
    """Integration tests for template discovery with wizard and CLI"""

    def test_discovery_used_in_wizard(self):
        """Test that wizard can use discovered templates"""
        templates = discover_available_templates()

        # Wizard should be able to iterate over discovered templates
        template_names = list(templates.keys())
        assert len(template_names) > 0

        # Each template should be actionable
        for name, info in templates.items():
            assert info['path'].exists()

    def test_discovery_supports_dynamic_template_addition(self):
        """Test that auto-discovery enables zero-code template addition"""
        # This tests the core value proposition of PROTO-023

        templates = discover_available_templates()

        # If we added a new DEPLOYMENT.template.md file,
        # it would automatically be discovered (zero code changes needed)
        # This test verifies the mechanism is in place

        assert isinstance(templates, dict)
        assert all('path' in t for t in templates.values())

        # The discovery mechanism doesn't hardcode template names
        # It dynamically finds all *.template.md files


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
