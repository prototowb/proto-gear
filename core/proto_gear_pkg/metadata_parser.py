"""
Template Metadata Parser

This module provides functionality to parse YAML frontmatter from template files
and extract metadata and content separately.

YAML frontmatter format:
---
name: "Template Name"
version: "1.0.0"
requires:
  project_type: ["Python", "Node.js", "Any"]
conditional_sections:
  python_specific:
    condition: "project_type == 'Python'"
    content: |
      Python-specific content...
---

Template content here...
"""

import re
from typing import Dict, Any, Tuple, Optional
import yaml


class TemplateMetadata:
    """Represents parsed template metadata."""

    def __init__(
        self,
        name: str = "",
        version: str = "1.0.0",
        requires: Optional[Dict[str, Any]] = None,
        conditional_sections: Optional[Dict[str, Dict[str, str]]] = None,
        raw_metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize template metadata.

        Args:
            name: Template name
            version: Template version
            requires: Requirements dictionary (e.g., project_type)
            conditional_sections: Conditional content sections
            raw_metadata: Raw metadata dictionary for extensibility
        """
        self.name = name
        self.version = version
        self.requires = requires or {}
        self.conditional_sections = conditional_sections or {}
        self.raw_metadata = raw_metadata or {}

    def meets_requirements(self, project_info: Dict[str, Any]) -> bool:
        """
        Check if template requirements are met for the given project.

        Args:
            project_info: Dictionary with project information (e.g., {'project_type': 'Python'})

        Returns:
            True if requirements are met or no requirements specified
        """
        if not self.requires:
            return True

        for req_key, req_values in self.requires.items():
            project_value = project_info.get(req_key)

            # Special case: "Any" means any value is acceptable
            if "Any" in req_values:
                continue

            # Check if project value matches any required value
            if project_value not in req_values:
                return False

        return True

    def get_conditional_content(self, project_info: Dict[str, Any]) -> Dict[str, str]:
        """
        Get conditional content sections that match project conditions.

        Args:
            project_info: Dictionary with project information

        Returns:
            Dictionary of section_name -> content for matching sections
        """
        matching_sections = {}

        for section_name, section_data in self.conditional_sections.items():
            condition = section_data.get('condition', '')
            content = section_data.get('content', '')

            if self._evaluate_condition(condition, project_info):
                matching_sections[section_name] = content

        return matching_sections

    def _evaluate_condition(self, condition: str, project_info: Dict[str, Any]) -> bool:
        """
        Safely evaluate a condition string.

        Currently supports simple equality checks like:
        - project_type == 'Python'
        - framework == 'Django'

        Args:
            condition: Condition string to evaluate
            project_info: Project information dictionary

        Returns:
            True if condition is met, False otherwise
        """
        if not condition:
            return False

        # Parse simple equality conditions: "key == 'value'"
        match = re.match(r"(\w+)\s*==\s*['\"]([^'\"]+)['\"]", condition.strip())
        if match:
            key, expected_value = match.groups()
            actual_value = project_info.get(key)
            return actual_value == expected_value

        # For safety, return False for any condition we don't recognize
        return False


class MetadataParser:
    """Parser for extracting YAML frontmatter from template files."""

    FRONTMATTER_PATTERN = re.compile(
        r'^---\s*\n(.*?)\n---\s*\n',
        re.DOTALL | re.MULTILINE
    )

    @staticmethod
    def parse_template(template_content: str) -> Tuple[TemplateMetadata, str]:
        """
        Parse template content and extract metadata and content.

        Args:
            template_content: Full template file content

        Returns:
            Tuple of (TemplateMetadata, template_content_without_frontmatter)
        """
        match = MetadataParser.FRONTMATTER_PATTERN.match(template_content)

        if not match:
            # No frontmatter found - return empty metadata and full content
            return TemplateMetadata(), template_content

        frontmatter_text = match.group(1)
        content_without_frontmatter = template_content[match.end():]

        try:
            metadata_dict = yaml.safe_load(frontmatter_text)

            if not isinstance(metadata_dict, dict):
                # Invalid metadata format - treat as no metadata
                return TemplateMetadata(), template_content

            metadata = TemplateMetadata(
                name=metadata_dict.get('name', ''),
                version=metadata_dict.get('version', '1.0.0'),
                requires=metadata_dict.get('requires'),
                conditional_sections=metadata_dict.get('conditional_sections'),
                raw_metadata=metadata_dict
            )

            return metadata, content_without_frontmatter

        except yaml.YAMLError:
            # Malformed YAML - return empty metadata and full content (graceful fallback)
            return TemplateMetadata(), template_content

    @staticmethod
    def parse_template_file(file_path: str) -> Tuple[TemplateMetadata, str]:
        """
        Parse a template file and extract metadata and content.

        Args:
            file_path: Path to template file

        Returns:
            Tuple of (TemplateMetadata, template_content)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return MetadataParser.parse_template(content)
        except (IOError, OSError):
            # File read error - return empty metadata and empty content
            return TemplateMetadata(), ""


def apply_conditional_content(
    template_content: str,
    conditional_sections: Dict[str, str],
    placeholder_pattern: str = r'\{\{(\w+)\}\}'
) -> str:
    """
    Apply conditional content sections to template by replacing placeholders.

    Args:
        template_content: Template content with placeholders
        conditional_sections: Dict of section_name -> content
        placeholder_pattern: Regex pattern for placeholders (default: {{section_name}})

    Returns:
        Template content with placeholders replaced
    """
    result = template_content

    for section_name, section_content in conditional_sections.items():
        # Replace {{section_name}} with actual content
        placeholder = f"{{{{{section_name}}}}}"
        result = result.replace(placeholder, section_content)

    # Remove any remaining unreplaced placeholders (optional sections not provided)
    result = re.sub(placeholder_pattern, '', result)

    return result
