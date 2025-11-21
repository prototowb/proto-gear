"""
Tests for template metadata parser functionality.
"""

import pytest
from pathlib import Path
from core.proto_gear_pkg.metadata_parser import (
    TemplateMetadata,
    MetadataParser,
    apply_conditional_content
)


class TestTemplateMetadata:
    """Tests for TemplateMetadata class."""

    def test_initialization_with_defaults(self):
        """Metadata should initialize with default values."""
        metadata = TemplateMetadata()

        assert metadata.name == ""
        assert metadata.version == "1.0.0"
        assert metadata.requires == {}
        assert metadata.conditional_sections == {}
        assert metadata.raw_metadata == {}

    def test_initialization_with_values(self):
        """Metadata should initialize with provided values."""
        metadata = TemplateMetadata(
            name="Test Template",
            version="2.0.0",
            requires={"project_type": ["Python"]},
            conditional_sections={"section1": {"condition": "test", "content": "content"}},
            raw_metadata={"key": "value"}
        )

        assert metadata.name == "Test Template"
        assert metadata.version == "2.0.0"
        assert metadata.requires == {"project_type": ["Python"]}
        assert metadata.conditional_sections == {"section1": {"condition": "test", "content": "content"}}
        assert metadata.raw_metadata == {"key": "value"}

    def test_meets_requirements_no_requirements(self):
        """Template with no requirements should always meet requirements."""
        metadata = TemplateMetadata()
        project_info = {"project_type": "Python"}

        assert metadata.meets_requirements(project_info) is True

    def test_meets_requirements_matching_type(self):
        """Template should meet requirements when project type matches."""
        metadata = TemplateMetadata(
            requires={"project_type": ["Python", "Node.js"]}
        )
        project_info = {"project_type": "Python"}

        assert metadata.meets_requirements(project_info) is True

    def test_meets_requirements_any_type(self):
        """Template with 'Any' should accept any project type."""
        metadata = TemplateMetadata(
            requires={"project_type": ["Any"]}
        )
        project_info = {"project_type": "Ruby"}

        assert metadata.meets_requirements(project_info) is True

    def test_meets_requirements_non_matching_type(self):
        """Template should not meet requirements when project type doesn't match."""
        metadata = TemplateMetadata(
            requires={"project_type": ["Python"]}
        )
        project_info = {"project_type": "Node.js"}

        assert metadata.meets_requirements(project_info) is False

    def test_evaluate_condition_simple_equality(self):
        """Should correctly evaluate simple equality conditions."""
        metadata = TemplateMetadata()

        # Test matching condition
        assert metadata._evaluate_condition(
            "project_type == 'Python'",
            {"project_type": "Python"}
        ) is True

        # Test non-matching condition
        assert metadata._evaluate_condition(
            "project_type == 'Python'",
            {"project_type": "Node.js"}
        ) is False

    def test_evaluate_condition_with_double_quotes(self):
        """Should handle conditions with double quotes."""
        metadata = TemplateMetadata()

        assert metadata._evaluate_condition(
            'project_type == "Python"',
            {"project_type": "Python"}
        ) is True

    def test_evaluate_condition_invalid_format(self):
        """Should return False for unrecognized condition formats."""
        metadata = TemplateMetadata()

        assert metadata._evaluate_condition(
            "project_type > 5",
            {"project_type": "Python"}
        ) is False

        assert metadata._evaluate_condition(
            "invalid condition",
            {"project_type": "Python"}
        ) is False

    def test_evaluate_condition_empty(self):
        """Should return False for empty conditions."""
        metadata = TemplateMetadata()

        assert metadata._evaluate_condition("", {"project_type": "Python"}) is False

    def test_get_conditional_content_matching(self):
        """Should return matching conditional sections."""
        metadata = TemplateMetadata(
            conditional_sections={
                "python_specific": {
                    "condition": "project_type == 'Python'",
                    "content": "Python content"
                },
                "nodejs_specific": {
                    "condition": "project_type == 'Node.js'",
                    "content": "Node.js content"
                }
            }
        )

        result = metadata.get_conditional_content({"project_type": "Python"})

        assert result == {"python_specific": "Python content"}

    def test_get_conditional_content_multiple_matches(self):
        """Should return all matching conditional sections."""
        metadata = TemplateMetadata(
            conditional_sections={
                "python_specific": {
                    "condition": "project_type == 'Python'",
                    "content": "Python content"
                },
                "framework_specific": {
                    "condition": "framework == 'Django'",
                    "content": "Django content"
                }
            }
        )

        result = metadata.get_conditional_content({
            "project_type": "Python",
            "framework": "Django"
        })

        assert result == {
            "python_specific": "Python content",
            "framework_specific": "Django content"
        }

    def test_get_conditional_content_no_matches(self):
        """Should return empty dict when no conditions match."""
        metadata = TemplateMetadata(
            conditional_sections={
                "python_specific": {
                    "condition": "project_type == 'Python'",
                    "content": "Python content"
                }
            }
        )

        result = metadata.get_conditional_content({"project_type": "Node.js"})

        assert result == {}


class TestMetadataParser:
    """Tests for MetadataParser class."""

    def test_parse_template_with_frontmatter(self):
        """Should correctly parse template with YAML frontmatter."""
        template = """---
name: "Test Template"
version: "1.0.0"
requires:
  project_type: ["Python"]
---

# Template Content

This is the template body.
"""

        metadata, content = MetadataParser.parse_template(template)

        assert metadata.name == "Test Template"
        assert metadata.version == "1.0.0"
        assert metadata.requires == {"project_type": ["Python"]}
        assert "# Template Content" in content
        assert "---" not in content

    def test_parse_template_without_frontmatter(self):
        """Should handle templates without frontmatter gracefully."""
        template = """# Template Content

This is a template without frontmatter.
"""

        metadata, content = MetadataParser.parse_template(template)

        assert metadata.name == ""
        assert metadata.version == "1.0.0"
        assert content == template

    def test_parse_template_malformed_yaml(self):
        """Should handle malformed YAML gracefully."""
        template = """---
name: "Test
invalid: yaml: content
---

# Template Content
"""

        metadata, content = MetadataParser.parse_template(template)

        # Should fall back to empty metadata
        assert metadata.name == ""
        assert content == template

    def test_parse_template_invalid_metadata_structure(self):
        """Should handle non-dict metadata gracefully."""
        template = """---
- item1
- item2
---

# Template Content
"""

        metadata, content = MetadataParser.parse_template(template)

        assert metadata.name == ""
        assert content == template

    def test_parse_template_complex_conditional_sections(self):
        """Should correctly parse complex conditional sections."""
        template = """---
name: "Testing Workflow"
conditional_sections:
  python_examples:
    condition: "project_type == 'Python'"
    content: |
      Python-specific content
      with multiple lines
  nodejs_examples:
    condition: "project_type == 'Node.js'"
    content: |
      Node.js content
---

# Template

{{python_examples}}

{{nodejs_examples}}
"""

        metadata, content = MetadataParser.parse_template(template)

        assert metadata.name == "Testing Workflow"
        assert "python_examples" in metadata.conditional_sections
        assert "nodejs_examples" in metadata.conditional_sections
        assert "Python-specific content" in metadata.conditional_sections["python_examples"]["content"]

    def test_parse_template_file_not_found(self):
        """Should handle file not found gracefully."""
        metadata, content = MetadataParser.parse_template_file("nonexistent_file.md")

        assert metadata.name == ""
        assert content == ""


class TestApplyConditionalContent:
    """Tests for apply_conditional_content function."""

    def test_apply_single_section(self):
        """Should replace single placeholder with content."""
        template = "Introduction\n\n{{python_examples}}\n\nConclusion"
        sections = {"python_examples": "Python content here"}

        result = apply_conditional_content(template, sections)

        assert result == "Introduction\n\nPython content here\n\nConclusion"
        assert "{{python_examples}}" not in result

    def test_apply_multiple_sections(self):
        """Should replace multiple placeholders."""
        template = "{{section1}}\n\nMiddle\n\n{{section2}}"
        sections = {
            "section1": "First section",
            "section2": "Second section"
        }

        result = apply_conditional_content(template, sections)

        assert result == "First section\n\nMiddle\n\nSecond section"

    def test_apply_removes_unreplaced_placeholders(self):
        """Should remove placeholders that don't have content."""
        template = "{{section1}}\n\nContent\n\n{{section2}}"
        sections = {"section1": "Only first"}

        result = apply_conditional_content(template, sections)

        assert "Only first" in result
        assert "{{section2}}" not in result

    def test_apply_no_sections(self):
        """Should remove all placeholders when no sections provided."""
        template = "{{section1}}\n\nContent\n\n{{section2}}"
        sections = {}

        result = apply_conditional_content(template, sections)

        assert "Content" in result
        assert "{{" not in result

    def test_apply_multiline_content(self):
        """Should correctly handle multiline content."""
        template = "Start\n\n{{examples}}\n\nEnd"
        sections = {
            "examples": """Line 1
Line 2
Line 3"""
        }

        result = apply_conditional_content(template, sections)

        assert "Line 1" in result
        assert "Line 2" in result
        assert "Line 3" in result


class TestIntegration:
    """Integration tests for complete metadata workflow."""

    def test_full_workflow_python_project(self):
        """Test complete workflow for Python project."""
        # Create template with metadata
        template = """---
name: "Testing Workflow"
requires:
  project_type: ["Python", "Any"]
conditional_sections:
  python_examples:
    condition: "project_type == 'Python'"
    content: "Use pytest for testing"
  nodejs_examples:
    condition: "project_type == 'Node.js'"
    content: "Use jest for testing"
---

# Testing Guide

{{python_examples}}

{{nodejs_examples}}

General testing advice.
"""

        # Parse metadata
        metadata, content = MetadataParser.parse_template(template)

        # Check requirements
        project_info = {"project_type": "Python"}
        assert metadata.meets_requirements(project_info)

        # Get conditional content
        conditional = metadata.get_conditional_content(project_info)
        assert "python_examples" in conditional
        assert "nodejs_examples" not in conditional

        # Apply conditional content
        result = apply_conditional_content(content, conditional)

        assert "Use pytest for testing" in result
        assert "Use jest for testing" not in result
        assert "General testing advice" in result

    def test_full_workflow_nodejs_project(self):
        """Test complete workflow for Node.js project."""
        template = """---
conditional_sections:
  python_examples:
    condition: "project_type == 'Python'"
    content: "pytest content"
  nodejs_examples:
    condition: "project_type == 'Node.js'"
    content: "jest content"
---

{{python_examples}}
{{nodejs_examples}}
"""

        metadata, content = MetadataParser.parse_template(template)
        project_info = {"project_type": "Node.js"}
        conditional = metadata.get_conditional_content(project_info)
        result = apply_conditional_content(content, conditional)

        assert "jest content" in result
        assert "pytest content" not in result

    def test_full_workflow_no_metadata(self):
        """Test workflow with template without metadata."""
        template = """# Simple Template

No metadata here.
"""

        metadata, content = MetadataParser.parse_template(template)
        project_info = {"project_type": "Python"}

        # Should work fine even without metadata
        assert metadata.meets_requirements(project_info)
        conditional = metadata.get_conditional_content(project_info)
        assert conditional == {}

        result = apply_conditional_content(content, conditional)
        assert result == content
