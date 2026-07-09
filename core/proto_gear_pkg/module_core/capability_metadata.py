"""
Capability Metadata Parser and Validator

This module provides functionality for parsing and validating capability metadata
files (metadata.yaml) used by the v0.8.0 composition engine.

Supports:
- Loading metadata.yaml files (v2.0 schema)
- Fallback to template frontmatter (v1.0 schema)
- Metadata validation
- Dependency resolution
- Conflict detection
"""

import re
from pathlib import Path
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import yaml


class CapabilityType(Enum):
    """Types of capabilities"""
    SKILL = "skill"
    WORKFLOW = "workflow"
    COMMAND = "command"
    AGENT = "agent"


class CapabilityStatus(Enum):
    """Status of a capability"""
    STABLE = "stable"
    BETA = "beta"
    EXPERIMENTAL = "experimental"
    DEPRECATED = "deprecated"


@dataclass
class CapabilityDependencies:
    """Structured capability dependencies"""
    required: List[str] = field(default_factory=list)
    optional: List[str] = field(default_factory=list)
    suggested: List[str] = field(default_factory=list)

    def all_dependencies(self) -> List[str]:
        """Get all dependencies (required + optional + suggested)"""
        return self.required + self.optional + self.suggested

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format"""
        return {
            "required": self.required,
            "optional": self.optional,
            "suggested": self.suggested
        }


@dataclass
class CapabilityRelevance:
    """When and where a capability is relevant"""
    triggers: List[str] = field(default_factory=list)
    contexts: List[str] = field(default_factory=list)

    def matches_trigger(self, query: str) -> bool:
        """Check if query matches any trigger pattern"""
        query_lower = query.lower()
        return any(trigger.lower() in query_lower for trigger in self.triggers)

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format"""
        return {
            "triggers": self.triggers,
            "contexts": self.contexts
        }


@dataclass
class WorkflowMetadata:
    """Workflow-specific metadata"""
    steps: int = 0
    estimated_duration: str = ""
    outputs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "steps": self.steps,
            "estimated_duration": self.estimated_duration,
            "outputs": self.outputs
        }


@dataclass
class CommandMetadata:
    """Command-specific metadata"""
    idempotent: bool = True
    side_effects: List[str] = field(default_factory=list)
    prerequisites: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "idempotent": self.idempotent,
            "side_effects": self.side_effects,
            "prerequisites": self.prerequisites
        }


@dataclass
class CapabilityMetadata:
    """Complete capability metadata (v2.0 schema)"""

    # Core fields (required)
    name: str
    type: CapabilityType
    version: str
    description: str
    category: str
    tags: List[str]
    status: CapabilityStatus
    author: str
    last_updated: str

    # Composition fields (required for v0.8.0)
    dependencies: CapabilityDependencies
    conflicts: List[str]
    composable_with: List[str]
    agent_roles: List[str]

    # Discovery fields (optional but recommended)
    relevance: Optional[CapabilityRelevance] = None
    usage_notes: str = ""
    required_files: List[str] = field(default_factory=list)
    optional_files: List[str] = field(default_factory=list)

    # Type-specific fields
    workflow: Optional[WorkflowMetadata] = None
    command: Optional[CommandMetadata] = None

    # Raw metadata for extensibility
    raw_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization"""
        result = {
            "name": self.name,
            "type": self.type.value,
            "version": self.version,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "status": self.status.value,
            "author": self.author,
            "last_updated": self.last_updated,
            "dependencies": self.dependencies.to_dict(),
            "conflicts": self.conflicts,
            "composable_with": self.composable_with,
            "agent_roles": self.agent_roles,
            "usage_notes": self.usage_notes,
            "required_files": self.required_files,
            "optional_files": self.optional_files
        }

        if self.relevance:
            result["relevance"] = self.relevance.to_dict()

        if self.workflow:
            result["workflow"] = self.workflow.to_dict()

        if self.command:
            result["command"] = self.command.to_dict()

        return result


class ValidationError(Exception):
    """Raised when metadata validation fails"""
    pass


class CapabilityMetadataParser:
    """Parser for capability metadata files"""

    REQUIRED_FIELDS = [
        "name", "type", "version", "description", "category",
        "tags", "status", "author", "last_updated"
    ]

    COMPOSITION_FIELDS = [
        "dependencies", "conflicts", "composable_with", "agent_roles"
    ]

    VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')

    @staticmethod
    def parse_metadata_file(file_path: Path) -> CapabilityMetadata:
        """
        Parse metadata.yaml file and return CapabilityMetadata object.

        Args:
            file_path: Path to metadata.yaml file

        Returns:
            CapabilityMetadata object

        Raises:
            ValidationError: If metadata is invalid
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValidationError(f"Metadata file must contain YAML dictionary: {file_path}")

        return CapabilityMetadataParser._parse_metadata_dict(data, str(file_path))

    @staticmethod
    def _parse_metadata_dict(data: Dict[str, Any], source: str = "") -> CapabilityMetadata:
        """
        Parse metadata dictionary into CapabilityMetadata object.

        Args:
            data: Metadata dictionary
            source: Source file path (for error messages)

        Returns:
            CapabilityMetadata object

        Raises:
            ValidationError: If metadata is invalid
        """
        # Validate required fields
        CapabilityMetadataParser._validate_required_fields(data, source)

        # Parse core fields
        name = data["name"]
        type_str = data["type"]
        version = data["version"]
        description = data["description"]
        category = data["category"]
        tags = data.get("tags", [])
        status_str = data["status"]
        author = data["author"]
        last_updated = data["last_updated"]

        # Validate and convert enums
        try:
            capability_type = CapabilityType(type_str)
        except ValueError:
            valid_types = [t.value for t in CapabilityType]
            raise ValidationError(
                f"Invalid type '{type_str}' in {source}. "
                f"Must be one of: {valid_types}"
            )

        try:
            capability_status = CapabilityStatus(status_str)
        except ValueError:
            valid_statuses = [s.value for s in CapabilityStatus]
            raise ValidationError(
                f"Invalid status '{status_str}' in {source}. "
                f"Must be one of: {valid_statuses}"
            )

        # Validate version format
        if not CapabilityMetadataParser.VERSION_PATTERN.match(version):
            raise ValidationError(
                f"Invalid version format '{version}' in {source}. "
                f"Must match semantic versioning (e.g., 1.0.0)"
            )

        # Parse dependencies
        dependencies_data = data.get("dependencies", {})
        dependencies = CapabilityDependencies(
            required=dependencies_data.get("required", []),
            optional=dependencies_data.get("optional", []),
            suggested=dependencies_data.get("suggested", [])
        )

        # Parse composition fields
        conflicts = data.get("conflicts", [])
        composable_with = data.get("composable_with", [])
        agent_roles = data.get("agent_roles", [])

        # Parse relevance
        relevance_data = data.get("relevance")
        relevance = None
        if relevance_data:
            relevance = CapabilityRelevance(
                triggers=relevance_data.get("triggers", []),
                contexts=relevance_data.get("contexts", [])
            )

        # Parse type-specific metadata
        workflow = None
        command = None

        if capability_type == CapabilityType.WORKFLOW:
            workflow_data = data.get("workflow", {})
            workflow = WorkflowMetadata(
                steps=workflow_data.get("steps", 0),
                estimated_duration=workflow_data.get("estimated_duration", ""),
                outputs=workflow_data.get("outputs", [])
            )

        if capability_type == CapabilityType.COMMAND:
            command_data = data.get("command", {})
            command = CommandMetadata(
                idempotent=command_data.get("idempotent", True),
                side_effects=command_data.get("side_effects", []),
                prerequisites=command_data.get("prerequisites", [])
            )

        return CapabilityMetadata(
            name=name,
            type=capability_type,
            version=version,
            description=description,
            category=category,
            tags=tags,
            status=capability_status,
            author=author,
            last_updated=last_updated,
            dependencies=dependencies,
            conflicts=conflicts,
            composable_with=composable_with,
            agent_roles=agent_roles,
            relevance=relevance,
            usage_notes=data.get("usage_notes", ""),
            required_files=data.get("required_files", []),
            optional_files=data.get("optional_files", []),
            workflow=workflow,
            command=command,
            raw_metadata=data
        )

    @staticmethod
    def _validate_required_fields(data: Dict[str, Any], source: str = ""):
        """Validate that all required fields are present"""
        missing_fields = []

        for field in CapabilityMetadataParser.REQUIRED_FIELDS:
            if field not in data:
                missing_fields.append(field)

        if missing_fields:
            raise ValidationError(
                f"Missing required fields in {source}: {', '.join(missing_fields)}"
            )

        # Validate that composition fields exist (can be empty)
        for field in CapabilityMetadataParser.COMPOSITION_FIELDS:
            if field not in data:
                # Provide default empty values
                if field == "dependencies":
                    data[field] = {"required": [], "optional": [], "suggested": []}
                else:
                    data[field] = []


class CapabilityValidator:
    """Validator for capability metadata and compositions"""

    @staticmethod
    def validate_metadata(metadata: CapabilityMetadata) -> List[str]:
        """
        Validate capability metadata for common issues.

        Args:
            metadata: CapabilityMetadata to validate

        Returns:
            List of validation warnings (empty if valid)
        """
        warnings = []

        # Check for empty required fields
        if not metadata.name:
            warnings.append("Name is empty")
        if not metadata.description:
            warnings.append("Description is empty")
        if not metadata.category:
            warnings.append("Category is empty")

        # Check for empty lists that should have values
        if not metadata.tags:
            warnings.append("Tags list is empty (recommended to have at least one tag)")
        if not metadata.agent_roles:
            warnings.append("Agent roles list is empty (which agents benefit from this?)")

        # Validate workflow-specific requirements
        if metadata.type == CapabilityType.WORKFLOW:
            if not metadata.workflow:
                warnings.append("Workflow type but no workflow metadata")
            elif metadata.workflow.steps == 0:
                warnings.append("Workflow has 0 steps")

        # Validate command-specific requirements
        if metadata.type == CapabilityType.COMMAND:
            if not metadata.command:
                warnings.append("Command type but no command metadata")

        return warnings

    @staticmethod
    def validate_dependencies(
        capability_id: str,
        metadata: CapabilityMetadata,
        all_capabilities: Dict[str, CapabilityMetadata]
    ) -> List[str]:
        """
        Validate that all dependencies exist and are resolvable.

        Args:
            capability_id: ID of the capability being validated
            metadata: CapabilityMetadata to validate
            all_capabilities: Dict of all available capabilities

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        all_deps = metadata.dependencies.all_dependencies()

        for dep in all_deps:
            if dep not in all_capabilities:
                errors.append(f"Dependency '{dep}' not found in available capabilities")

        return errors

    @staticmethod
    def detect_circular_dependencies(
        capability_id: str,
        all_capabilities: Dict[str, CapabilityMetadata]
    ) -> Optional[List[str]]:
        """
        Detect circular dependency chains.

        Args:
            capability_id: ID of capability to check
            all_capabilities: Dict of all available capabilities

        Returns:
            List forming circular dependency chain if found, None otherwise
        """
        def find_cycle(current: str, visited: Set[str], path: List[str]) -> Optional[List[str]]:
            if current in visited:
                # Found cycle - return the cycle path
                cycle_start = path.index(current)
                return path[cycle_start:] + [current]

            if current not in all_capabilities:
                return None

            visited.add(current)
            path.append(current)

            metadata = all_capabilities[current]
            for dep in metadata.dependencies.required:
                cycle = find_cycle(dep, visited.copy(), path.copy())
                if cycle:
                    return cycle

            return None

        return find_cycle(capability_id, set(), [])


class CompositionEngine:
    """Engine for composing capabilities with dependency resolution and conflict detection"""

    @staticmethod
    def resolve_dependencies(
        capabilities: List[str],
        all_capabilities: Dict[str, CapabilityMetadata],
        include_optional: bool = False
    ) -> Set[str]:
        """
        Resolve all dependencies for a list of capabilities.

        Args:
            capabilities: List of capability IDs
            all_capabilities: Dict of all available capabilities
            include_optional: Whether to include optional dependencies

        Returns:
            Set of all capability IDs (including resolved dependencies)

        Raises:
            ValidationError: If dependencies cannot be resolved
        """
        resolved = set(capabilities)
        to_process = list(capabilities)

        while to_process:
            current = to_process.pop(0)

            if current not in all_capabilities:
                raise ValidationError(f"Capability not found: {current}")

            metadata = all_capabilities[current]

            # Process required dependencies
            for dep in metadata.dependencies.required:
                if dep not in resolved:
                    resolved.add(dep)
                    to_process.append(dep)

            # Process optional dependencies if requested
            if include_optional:
                for dep in metadata.dependencies.optional:
                    if dep not in resolved and dep in all_capabilities:
                        resolved.add(dep)
                        to_process.append(dep)

        return resolved

    @staticmethod
    def detect_conflicts(
        capabilities: List[str],
        all_capabilities: Dict[str, CapabilityMetadata]
    ) -> List[Tuple[str, str, str]]:
        """
        Detect conflicts between capabilities.

        Args:
            capabilities: List of capability IDs
            all_capabilities: Dict of all available capabilities

        Returns:
            List of tuples: (capability1, capability2, reason)
        """
        conflicts = []

        for i, cap1 in enumerate(capabilities):
            if cap1 not in all_capabilities:
                continue

            metadata1 = all_capabilities[cap1]

            for cap2 in capabilities[i + 1:]:
                if cap2 in metadata1.conflicts:
                    reason = f"'{cap1}' conflicts with '{cap2}'"
                    conflicts.append((cap1, cap2, reason))

        return conflicts

    @staticmethod
    def get_recommended_capabilities(
        capabilities: List[str],
        all_capabilities: Dict[str, CapabilityMetadata]
    ) -> List[str]:
        """
        Get recommended capabilities based on composable_with metadata.

        Args:
            capabilities: List of capability IDs
            all_capabilities: Dict of all available capabilities

        Returns:
            List of recommended capability IDs (not already included)
        """
        recommended = set()

        for cap in capabilities:
            if cap not in all_capabilities:
                continue

            metadata = all_capabilities[cap]

            for composable in metadata.composable_with:
                if composable not in capabilities and composable in all_capabilities:
                    recommended.add(composable)

        return sorted(recommended)


def load_all_capabilities(capabilities_dir: Path) -> Dict[str, CapabilityMetadata]:
    """
    Load all capability metadata from a capabilities directory.

    Args:
        capabilities_dir: Path to capabilities directory

    Returns:
        Dict mapping capability ID to CapabilityMetadata
    """
    capabilities = {}

    # Scan for metadata.yaml files
    for metadata_file in capabilities_dir.rglob("metadata.yaml"):
        try:
            metadata = CapabilityMetadataParser.parse_metadata_file(metadata_file)

            # Generate capability ID from path (e.g., "skills/testing")
            rel_path = metadata_file.parent.relative_to(capabilities_dir)
            cap_id = str(rel_path).replace('\\', '/')

            capabilities[cap_id] = metadata

        except (ValidationError, yaml.YAMLError) as e:
            # Log error but continue loading other capabilities
            print(f"Warning: Failed to load {metadata_file}: {e}")

    return capabilities
