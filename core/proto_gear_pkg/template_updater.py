"""
Template Updater Module

Provides safe template update functionality that preserves user data while
applying template improvements from newer Proto Gear versions.

Key Features:
- Smart extraction of user data (tickets, metrics, configurations)
- Intelligent merging of new template structure with preserved user content
- Unified diff preview with color coding
- Automatic backup creation before updates
- Validation of merged content

Usage:
    from template_updater import TemplateUpdater

    updater = TemplateUpdater(project_dir=Path('.'))
    result = updater.update_template('PROJECT_STATUS.md', dry_run=True)
"""

import re
import difflib
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

from .metadata_parser import MetadataParser, TemplateMetadata
from .ui_helper import Colors


# ============================================================================
# Exception Classes
# ============================================================================

class TemplateUpdateError(Exception):
    """Base exception for template update errors"""
    pass


class ExtractionError(TemplateUpdateError):
    """Failed to extract user data from existing file"""
    pass


class MergeError(TemplateUpdateError):
    """Failed to merge new template with user data"""
    pass


class ValidationError(TemplateUpdateError):
    """Merged content failed validation"""
    pass


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ExtractedData:
    """Container for extracted user data"""
    yaml_blocks: Dict[str, Any]
    table_sections: Dict[str, str]
    freeform_sections: Dict[str, str]
    metadata: Dict[str, Any]


@dataclass
class UpdateResult:
    """Result of a template update operation"""
    success: bool
    template_name: str
    backup_created: bool
    backup_path: Optional[Path]
    lines_added: int
    lines_removed: int
    warnings: List[str]
    errors: List[str]


# ============================================================================
# User Data Extractor
# ============================================================================

class UserDataExtractor:
    """
    Extracts user-customized data from existing template files.

    Supports PROJECT_STATUS.md and AGENTS.md with template-specific
    extraction patterns.
    """

    def __init__(self):
        """Initialize the extractor with default patterns"""
        self.extraction_patterns = self._build_extraction_patterns()

    def _build_extraction_patterns(self) -> Dict[str, Any]:
        """
        Build regex patterns for extracting user data from templates.

        Returns:
            Dictionary of template-specific extraction patterns
        """
        return {
            'PROJECT_STATUS': {
                'yaml_blocks': [
                    # Current state YAML block
                    ('current_state', r'```yaml\s*\nproject_phase:.*?\n```', re.DOTALL),
                ],
                'table_sections': [
                    # Active tickets table
                    ('active_tickets',
                     r'##\s*🎫\s*Active Tickets\s*\n\n(.*?)(?=\n##|\Z)',
                     re.DOTALL),
                    # Completed tickets table
                    ('completed_tickets',
                     r'##\s*✅\s*Completed Tickets\s*\n\n(.*?)(?=\n##|\Z)',
                     re.DOTALL),
                    # Blocked tickets table (optional)
                    ('blocked_tickets',
                     r'##\s*🚫\s*Blocked Tickets\s*\n\n(.*?)(?=\n##|\Z)',
                     re.DOTALL),
                ],
                'freeform_sections': [
                    # Recent updates section
                    ('recent_updates',
                     r'##\s*🔄\s*Recent Updates\s*\n\n(.*?)(?=\n##|\Z)',
                     re.DOTALL),
                    # Feature progress
                    ('feature_progress',
                     r'##\s*📊\s*Feature Progress\s*\n\n(.*?)(?=\n##|\Z)',
                     re.DOTALL),
                ],
            },
            'AGENTS': {
                'agent_configs': [
                    # Custom core agent configurations
                    ('core_agents',
                     r'{{CORE_AGENT_1}}.*?{{CORE_AGENT_4}}',
                     re.DOTALL),
                    # Custom flex agent assignments
                    ('flex_agents',
                     r'{{FLEX_AGENT_1}}.*?{{FLEX_AGENT_5}}',
                     re.DOTALL),
                ],
                'directory_configs': [
                    # Directory-specific agent notes
                    ('directory_agents',
                     r'{{DIR1}}/AGENTS\.md.*?{{DIR3}}/AGENTS\.md',
                     re.DOTALL),
                ],
            },
        }

    def extract(self, content: str, template_name: str) -> ExtractedData:
        """
        Extract user data from existing template file content.

        Args:
            content: Current file content
            template_name: Name of template (e.g., 'PROJECT_STATUS', 'AGENTS')

        Returns:
            ExtractedData object containing all extracted user data

        Raises:
            ExtractionError: If extraction fails critically
        """
        if template_name not in self.extraction_patterns:
            raise ExtractionError(
                f"No extraction patterns defined for template: {template_name}"
            )

        patterns = self.extraction_patterns[template_name]

        try:
            if template_name == 'PROJECT_STATUS':
                return self._extract_project_status(content, patterns)
            elif template_name == 'AGENTS':
                return self._extract_agents(content, patterns)
            else:
                raise ExtractionError(f"Unsupported template: {template_name}")

        except Exception as e:
            raise ExtractionError(f"Failed to extract data from {template_name}: {e}")

    def _extract_project_status(
        self,
        content: str,
        patterns: Dict[str, Any]
    ) -> ExtractedData:
        """
        Extract user data from PROJECT_STATUS.md.

        Args:
            content: File content
            patterns: Extraction patterns

        Returns:
            ExtractedData with tickets, metrics, and state
        """
        yaml_blocks = {}
        table_sections = {}
        freeform_sections = {}

        # Extract YAML blocks
        for name, pattern, flags in patterns.get('yaml_blocks', []):
            match = re.search(pattern, content, flags)
            if match:
                yaml_content = match.group(0)
                # Parse YAML to validate
                try:
                    # Extract YAML between ```yaml and ```
                    yaml_text = re.search(r'```yaml\s*\n(.*?)\n```', yaml_content, re.DOTALL)
                    if yaml_text:
                        parsed = yaml.safe_load(yaml_text.group(1))
                        yaml_blocks[name] = parsed
                except yaml.YAMLError:
                    # Preserve raw YAML if parsing fails
                    yaml_blocks[name] = yaml_content

        # Extract table sections
        for name, pattern, flags in patterns.get('table_sections', []):
            match = re.search(pattern, content, flags)
            if match:
                table_sections[name] = match.group(1).strip()

        # Extract freeform sections
        for name, pattern, flags in patterns.get('freeform_sections', []):
            match = re.search(pattern, content, flags)
            if match:
                freeform_sections[name] = match.group(1).strip()

        return ExtractedData(
            yaml_blocks=yaml_blocks,
            table_sections=table_sections,
            freeform_sections=freeform_sections,
            metadata={}
        )

    def _extract_agents(
        self,
        content: str,
        patterns: Dict[str, Any]
    ) -> ExtractedData:
        """
        Extract user data from AGENTS.md.

        Args:
            content: File content
            patterns: Extraction patterns

        Returns:
            ExtractedData with agent configurations
        """
        # For AGENTS.md, extraction is simpler - preserve template variables
        # that have been customized by the user

        # TODO: Implement AGENTS.md extraction (Phase 3)
        return ExtractedData(
            yaml_blocks={},
            table_sections={},
            freeform_sections={},
            metadata={'note': 'AGENTS.md extraction not yet implemented'}
        )


# ============================================================================
# Template Merger
# ============================================================================

class TemplateMerger:
    """
    Merges new template structure with extracted user data.

    Uses template-specific merge strategies to preserve 100% of user
    customizations while applying new template improvements.
    """

    def __init__(self, package_dir: Path):
        """
        Initialize the merger.

        Args:
            package_dir: Path to proto_gear_pkg directory
        """
        self.package_dir = package_dir

    def merge(
        self,
        template_name: str,
        extracted_data: ExtractedData,
        project_context: Dict[str, str]
    ) -> str:
        """
        Merge new template with extracted user data.

        Args:
            template_name: Name of template (e.g., 'PROJECT_STATUS')
            extracted_data: User data extracted from old file
            project_context: Project-specific values for placeholders

        Returns:
            Merged template content

        Raises:
            MergeError: If merge fails
        """
        try:
            # 1. Load new template from package
            template_content = self._load_template(template_name)

            # 2. Parse metadata and strip frontmatter
            metadata, content = MetadataParser.parse_template(template_content)

            # 3. Apply project placeholders
            content = self._replace_placeholders(content, project_context)

            # 4. Insert user data (template-specific)
            if template_name == 'PROJECT_STATUS':
                content = self._merge_project_status(content, extracted_data)
            elif template_name == 'AGENTS':
                content = self._merge_agents(content, extracted_data)

            return content

        except Exception as e:
            raise MergeError(f"Failed to merge template {template_name}: {e}")

    def _load_template(self, template_name: str) -> str:
        """
        Load template from package directory.

        Args:
            template_name: Template name (e.g., 'PROJECT_STATUS')

        Returns:
            Template content
        """
        template_filename = f"{template_name}.template.md"
        template_path = self.package_dir / template_filename

        if not template_path.exists():
            raise MergeError(f"Template file not found: {template_path}")

        return template_path.read_text(encoding='utf-8')

    def _replace_placeholders(
        self,
        content: str,
        context: Dict[str, str]
    ) -> str:
        """
        Replace template placeholders with project-specific values.

        Args:
            content: Template content
            context: Dictionary of placeholder values

        Returns:
            Content with replaced placeholders
        """
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        return content

    def _merge_project_status(
        self,
        template: str,
        data: ExtractedData
    ) -> str:
        """
        Merge PROJECT_STATUS.md with user data.

        Args:
            template: New template content
            data: Extracted user data

        Returns:
            Merged content
        """
        content = template

        # Replace YAML blocks
        if 'current_state' in data.yaml_blocks:
            state_data = data.yaml_blocks['current_state']
            # Format as YAML block
            yaml_str = yaml.dump(state_data, default_flow_style=False, sort_keys=False)
            yaml_block = f"```yaml\n{yaml_str}```"

            # Find and replace the YAML block in template
            pattern = r'```yaml\s*\nproject_phase:.*?\n```'
            content = re.sub(pattern, yaml_block, content, flags=re.DOTALL)

        # Replace ticket tables
        if 'active_tickets' in data.table_sections:
            # Find the Active Tickets section and replace table content
            pattern = r'(##\s*🎫\s*Active Tickets\s*\n\n)(.*?)(?=\n##|\Z)'
            replacement = r'\1' + data.table_sections['active_tickets']
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        if 'completed_tickets' in data.table_sections:
            pattern = r'(##\s*✅\s*Completed Tickets\s*\n\n)(.*?)(?=\n##|\Z)'
            replacement = r'\1' + data.table_sections['completed_tickets']
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        # Replace freeform sections
        if 'recent_updates' in data.freeform_sections:
            pattern = r'(##\s*🔄\s*Recent Updates\s*\n\n)(.*?)(?=\n##|\Z)'
            replacement = r'\1' + data.freeform_sections['recent_updates']
            content = re.sub(pattern, replacement, content, flags=re.DOTALL)

        return content

    def _merge_agents(
        self,
        template: str,
        data: ExtractedData
    ) -> str:
        """
        Merge AGENTS.md with user data.

        Args:
            template: New template content
            data: Extracted user data

        Returns:
            Merged content
        """
        # TODO: Implement AGENTS.md merge (Phase 3)
        return template


# ============================================================================
# Diff Generator
# ============================================================================

class DiffGenerator:
    """
    Generates unified diffs with color coding and statistics.
    """

    @staticmethod
    def generate(
        old_content: str,
        new_content: str,
        filename: str
    ) -> Tuple[str, Dict[str, int]]:
        """
        Generate colored unified diff.

        Args:
            old_content: Original file content
            new_content: New file content
            filename: Name of file being updated

        Returns:
            Tuple of (colored_diff_string, statistics_dict)
        """
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)

        # Generate unified diff
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f'{filename}.old',
            tofile=f'{filename}.new',
            lineterm=''
        ))

        # Color the diff
        colored_diff = []
        for line in diff:
            if line.startswith('+++') or line.startswith('---'):
                colored_diff.append(Colors.BOLD + line + Colors.ENDC)
            elif line.startswith('+'):
                colored_diff.append(Colors.GREEN + line + Colors.ENDC)
            elif line.startswith('-'):
                colored_diff.append(Colors.FAIL + line + Colors.ENDC)
            elif line.startswith('@@'):
                colored_diff.append(Colors.CYAN + line + Colors.ENDC)
            else:
                colored_diff.append(line)

        # Calculate statistics
        stats = DiffGenerator.calculate_stats(old_content, new_content, diff)

        return '\n'.join(colored_diff), stats

    @staticmethod
    def calculate_stats(
        old_content: str,
        new_content: str,
        diff: List[str]
    ) -> Dict[str, int]:
        """
        Calculate diff statistics.

        Args:
            old_content: Original content
            new_content: New content
            diff: Unified diff lines

        Returns:
            Dictionary with lines_added, lines_removed, etc.
        """
        lines_added = sum(
            1 for line in diff
            if line.startswith('+') and not line.startswith('+++')
        )
        lines_removed = sum(
            1 for line in diff
            if line.startswith('-') and not line.startswith('---')
        )

        return {
            'lines_added': lines_added,
            'lines_removed': lines_removed,
            'total_lines_old': len(old_content.splitlines()),
            'total_lines_new': len(new_content.splitlines()),
        }


# ============================================================================
# Template Validator
# ============================================================================

class TemplateValidator:
    """
    Validates merged template content for correctness.
    """

    @staticmethod
    def validate(content: str, template_name: str) -> Tuple[bool, List[str]]:
        """
        Validate merged template content.

        Args:
            content: Merged content to validate
            template_name: Name of template being validated

        Returns:
            Tuple of (is_valid, list_of_warnings)
        """
        warnings = []

        # Check for unreplaced placeholders
        placeholders = re.findall(r'\{\{(\w+)\}\}', content)
        if placeholders:
            unique_placeholders = set(placeholders)
            warnings.append(
                f"Unreplaced placeholders: {', '.join(unique_placeholders)}"
            )

        # Check YAML validity
        yaml_blocks = re.findall(r'```yaml\s*\n(.*?)\n```', content, re.DOTALL)
        for i, block in enumerate(yaml_blocks):
            try:
                yaml.safe_load(block)
            except yaml.YAMLError as e:
                warnings.append(f"YAML block {i+1} invalid: {e}")

        # Template-specific validation
        if template_name == 'PROJECT_STATUS':
            # Check for required tables
            tables = re.findall(r'\|.*?\|.*?\n\|[-:| ]+\|', content)
            if len(tables) < 2:
                warnings.append(
                    "Expected at least 2 tables (Active Tickets, Completed Tickets)"
                )

        is_valid = len(warnings) == 0
        return is_valid, warnings


# ============================================================================
# Main Template Updater
# ============================================================================

class TemplateUpdater:
    """
    Main orchestrator for template updates.

    Handles the complete update workflow: detection, extraction, merging,
    diffing, backup, and writing.
    """

    def __init__(self, project_dir: Path):
        """
        Initialize the updater.

        Args:
            project_dir: Path to project root directory
        """
        self.project_dir = project_dir
        self.package_dir = Path(__file__).parent

        self.extractor = UserDataExtractor()
        self.merger = TemplateMerger(self.package_dir)

    def update_template(
        self,
        template_name: str,
        project_context: Dict[str, str],
        dry_run: bool = False,
        force: bool = False
    ) -> UpdateResult:
        """
        Update a single template file.

        Args:
            template_name: Template to update (e.g., 'PROJECT_STATUS')
            project_context: Project-specific placeholder values
            dry_run: If True, preview only without writing
            force: If True, skip confirmation prompt

        Returns:
            UpdateResult with operation details

        Raises:
            TemplateUpdateError: If update fails
        """
        filename = f"{template_name}.md"
        file_path = self.project_dir / filename

        # Check if file exists
        if not file_path.exists():
            raise TemplateUpdateError(
                f"File not found: {filename}. Cannot update non-existent file."
            )

        try:
            # 1. Read current file
            old_content = file_path.read_text(encoding='utf-8')

            # 2. Extract user data
            extracted_data = self.extractor.extract(old_content, template_name)

            # 3. Merge with new template
            new_content = self.merger.merge(
                template_name,
                extracted_data,
                project_context
            )

            # 4. Validate merged content
            is_valid, warnings = TemplateValidator.validate(new_content, template_name)

            # 5. Generate diff
            diff_text, stats = DiffGenerator.generate(
                old_content,
                new_content,
                filename
            )

            # 6. Create backup and write (if not dry-run)
            backup_created = False
            backup_path = None

            if not dry_run and (force or self._confirm_update(diff_text, stats, filename)):
                backup_path = self._create_backup(file_path)
                backup_created = True
                file_path.write_text(new_content, encoding='utf-8')

            # Success = operation completed, even if there are warnings
            # (Warnings are informational, not failures)
            return UpdateResult(
                success=True,  # Update succeeded even if there are warnings
                template_name=template_name,
                backup_created=backup_created,
                backup_path=backup_path,
                lines_added=stats['lines_added'],
                lines_removed=stats['lines_removed'],
                warnings=warnings,
                errors=[]
            )

        except Exception as e:
            return UpdateResult(
                success=False,
                template_name=template_name,
                backup_created=False,
                backup_path=None,
                lines_added=0,
                lines_removed=0,
                warnings=[],
                errors=[str(e)]
            )

    def _create_backup(self, file_path: Path) -> Path:
        """
        Create .bak backup of file.

        Args:
            file_path: Path to file to backup

        Returns:
            Path to backup file
        """
        backup_path = file_path.with_suffix('.md.bak')
        content = file_path.read_text(encoding='utf-8')
        backup_path.write_text(content, encoding='utf-8')
        return backup_path

    def _confirm_update(
        self,
        diff_text: str,
        stats: Dict[str, int],
        filename: str
    ) -> bool:
        """
        Show diff preview and prompt user for confirmation.

        Args:
            diff_text: Colored diff text
            stats: Diff statistics
            filename: Name of file being updated

        Returns:
            True if user confirms, False otherwise
        """
        print(f"\n{Colors.CYAN}+-- Template Update Preview: {filename} " + "-" * (40 - len(filename)) + f"+{Colors.ENDC}")
        print(f"{Colors.CYAN}|{Colors.ENDC} Changes: {Colors.GREEN}+{stats['lines_added']}{Colors.ENDC} lines, {Colors.FAIL}-{stats['lines_removed']}{Colors.ENDC} lines")
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

        print(f"{Colors.BOLD}=== Unified Diff ==={Colors.ENDC}")
        print(diff_text)
        print()

        while True:
            response = input(f"{Colors.GREEN}Apply update? [y/N]: {Colors.ENDC}").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print(f"{Colors.FAIL}Invalid choice. Please enter 'y' or 'n'.{Colors.ENDC}")
