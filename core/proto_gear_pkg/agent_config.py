"""
Agent Configuration Management

This module handles loading, validating, and managing custom AI agent configurations.
Agents are compositions of capabilities (skills, workflows, commands) tailored for
specific development tasks.

Features:
- Load agent configurations from YAML files
- Validate agent configurations against schema
- Resolve agent capabilities using composition engine
- Detect conflicts and circular dependencies
- Provide recommendations for agent improvement
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml

from .capability_metadata import (
    load_all_capabilities,
    CompositionEngine,
    CapabilityValidator,
    CapabilityMetadata,
    ValidationError as CapabilityValidationError
)


class AgentValidationError(Exception):
    """Raised when agent configuration validation fails"""
    pass


@dataclass
class AgentCapabilities:
    """Agent capability composition"""
    skills: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    commands: List[str] = field(default_factory=list)

    def all_capabilities(self) -> List[str]:
        """Get all capabilities as full paths"""
        result = []
        result.extend([f"skills/{skill}" for skill in self.skills])
        result.extend([f"workflows/{workflow}" for workflow in self.workflows])
        result.extend([f"commands/{command}" for command in self.commands])
        return result

    def is_empty(self) -> bool:
        """Check if no capabilities are specified"""
        return not (self.skills or self.workflows or self.commands)

    def to_dict(self) -> Dict[str, List[str]]:
        """Convert to dictionary format"""
        return {
            "skills": self.skills,
            "workflows": self.workflows,
            "commands": self.commands
        }


@dataclass
class AgentConfiguration:
    """Complete agent configuration"""

    # Metadata
    name: str
    version: str
    description: str
    created: str
    author: str = ""

    # Capabilities
    capabilities: AgentCapabilities = field(default_factory=AgentCapabilities)

    # Behavior
    context_priority: List[str] = field(default_factory=list)
    agent_instructions: List[str] = field(default_factory=list)

    # Dependencies
    required_files: List[str] = field(default_factory=list)
    optional_files: List[str] = field(default_factory=list)

    # Metadata
    tags: List[str] = field(default_factory=list)
    status: str = "active"

    # Source
    source_file: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for serialization"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "created": self.created,
            "author": self.author,
            "capabilities": self.capabilities.to_dict(),
            "context_priority": self.context_priority,
            "agent_instructions": self.agent_instructions,
            "required_files": self.required_files,
            "optional_files": self.optional_files,
            "tags": self.tags,
            "status": self.status
        }


class AgentConfigParser:
    """Parser for agent configuration files"""

    VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+$')
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    @staticmethod
    def parse_agent_file(file_path: Path) -> AgentConfiguration:
        """
        Parse agent configuration from YAML file.

        Args:
            file_path: Path to agent YAML file

        Returns:
            AgentConfiguration object

        Raises:
            AgentValidationError: If configuration is invalid
            FileNotFoundError: If file doesn't exist
            yaml.YAMLError: If YAML is malformed
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Agent configuration file not found: {file_path}")

        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise AgentValidationError(
                f"Agent configuration must be YAML dictionary: {file_path}"
            )

        agent = AgentConfigParser._parse_agent_dict(data, str(file_path))
        agent.source_file = file_path
        return agent

    @staticmethod
    def _parse_agent_dict(data: Dict[str, Any], source: str = "") -> AgentConfiguration:
        """
        Parse agent configuration from dictionary.

        Args:
            data: Configuration dictionary
            source: Source file path (for error messages)

        Returns:
            AgentConfiguration object

        Raises:
            AgentValidationError: If configuration is invalid
        """
        # Validate required fields
        AgentConfigParser._validate_required_fields(data, source)

        # Parse metadata
        name = data["name"]
        version = data["version"]
        description = data["description"]
        created = data["created"]
        author = data.get("author", "")

        # Validate version format
        if not AgentConfigParser.VERSION_PATTERN.match(version):
            raise AgentValidationError(
                f"Invalid version format '{version}' in {source}. "
                f"Must match semantic versioning (e.g., 1.0.0)"
            )

        # Validate date format
        if not AgentConfigParser.DATE_PATTERN.match(created):
            raise AgentValidationError(
                f"Invalid date format '{created}' in {source}. "
                f"Must be YYYY-MM-DD"
            )

        # Parse capabilities
        capabilities_data = data.get("capabilities", {})
        capabilities = AgentCapabilities(
            skills=capabilities_data.get("skills", []),
            workflows=capabilities_data.get("workflows", []),
            commands=capabilities_data.get("commands", [])
        )

        # Validate at least one capability
        if capabilities.is_empty():
            raise AgentValidationError(
                f"Agent must have at least one capability in {source}"
            )

        # Parse behavior
        context_priority = data.get("context_priority", [])
        agent_instructions = data.get("agent_instructions", [])

        # Parse dependencies
        required_files = data.get("required_files", [])
        optional_files = data.get("optional_files", [])

        # Parse metadata
        tags = data.get("tags", [])
        status = data.get("status", "active")

        # Validate status
        valid_statuses = ["active", "inactive", "experimental"]
        if status not in valid_statuses:
            raise AgentValidationError(
                f"Invalid status '{status}' in {source}. "
                f"Must be one of: {valid_statuses}"
            )

        return AgentConfiguration(
            name=name,
            version=version,
            description=description,
            created=created,
            author=author,
            capabilities=capabilities,
            context_priority=context_priority,
            agent_instructions=agent_instructions,
            required_files=required_files,
            optional_files=optional_files,
            tags=tags,
            status=status
        )

    @staticmethod
    def _validate_required_fields(data: Dict[str, Any], source: str = ""):
        """Validate that all required fields are present"""
        required_fields = ["name", "version", "description", "created"]
        missing_fields = []

        for field in required_fields:
            if field not in data or not data[field]:
                missing_fields.append(field)

        if missing_fields:
            raise AgentValidationError(
                f"Missing required fields in {source}: {', '.join(missing_fields)}"
            )


class AgentValidator:
    """Validator for agent configurations"""

    @staticmethod
    def validate_agent(
        agent: AgentConfiguration,
        all_capabilities: Dict[str, CapabilityMetadata]
    ) -> Tuple[List[str], List[str]]:
        """
        Validate agent configuration completely.

        Args:
            agent: AgentConfiguration to validate
            all_capabilities: All available capabilities

        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []

        # Validate capabilities exist
        for cap_id in agent.capabilities.all_capabilities():
            if cap_id not in all_capabilities:
                errors.append(f"Capability not found: {cap_id}")

        # Stop here if capabilities don't exist
        if errors:
            return errors, warnings

        # Validate no circular dependencies
        try:
            for cap_id in agent.capabilities.all_capabilities():
                cycle = CapabilityValidator.detect_circular_dependencies(
                    cap_id, all_capabilities
                )
                if cycle:
                    errors.append(f"Circular dependency detected: {' -> '.join(cycle)}")
        except Exception as e:
            errors.append(f"Error checking circular dependencies: {e}")

        # Detect conflicts
        try:
            conflicts = CompositionEngine.detect_conflicts(
                agent.capabilities.all_capabilities(),
                all_capabilities
            )
            if conflicts:
                for c1, c2, reason in conflicts:
                    errors.append(f"Conflict: {c1} and {c2} - {reason}")
        except Exception as e:
            errors.append(f"Error checking conflicts: {e}")

        # Warnings for missing optional elements
        if not agent.context_priority:
            warnings.append("No context_priority specified - agent won't know what to focus on")

        if not agent.agent_instructions:
            warnings.append("No agent_instructions specified - agent won't have specific guidance")

        if not agent.author:
            warnings.append("No author specified")

        # Warn if too many capabilities
        try:
            resolved = CompositionEngine.resolve_dependencies(
                agent.capabilities.all_capabilities(),
                all_capabilities
            )
            if len(resolved) > 15:
                warnings.append(
                    f"Agent has {len(resolved)} capabilities (including dependencies). "
                    f"Consider reducing scope for better focus."
                )
        except Exception:
            pass  # Already have errors about missing capabilities

        return errors, warnings

    @staticmethod
    def get_recommendations(
        agent: AgentConfiguration,
        all_capabilities: Dict[str, CapabilityMetadata]
    ) -> List[str]:
        """
        Get capability recommendations for an agent.

        Args:
            agent: AgentConfiguration
            all_capabilities: All available capabilities

        Returns:
            List of recommended capability IDs
        """
        try:
            return CompositionEngine.get_recommended_capabilities(
                agent.capabilities.all_capabilities(),
                all_capabilities
            )
        except Exception:
            return []


class AgentManager:
    """Manager for agent configurations"""

    def __init__(self, agents_dir: Path, capabilities_dir: Path):
        """
        Initialize agent manager.

        Args:
            agents_dir: Directory containing agent configurations
            capabilities_dir: Directory containing capabilities
        """
        self.agents_dir = agents_dir
        self.capabilities_dir = capabilities_dir
        self._all_capabilities = None

    def _load_capabilities(self) -> Dict[str, CapabilityMetadata]:
        """Load all capabilities (cached)"""
        if self._all_capabilities is None:
            self._all_capabilities = load_all_capabilities(self.capabilities_dir)
        return self._all_capabilities

    def list_agents(self) -> List[AgentConfiguration]:
        """
        List all agent configurations in agents directory.

        Returns:
            List of AgentConfiguration objects
        """
        if not self.agents_dir.exists():
            return []

        agents = []
        for yaml_file in self.agents_dir.glob("*.yaml"):
            try:
                agent = AgentConfigParser.parse_agent_file(yaml_file)
                agents.append(agent)
            except (AgentValidationError, yaml.YAMLError) as e:
                # Skip invalid agents but log warning
                print(f"Warning: Failed to load {yaml_file}: {e}")

        return sorted(agents, key=lambda a: a.name)

    def load_agent(self, agent_name: str) -> AgentConfiguration:
        """
        Load specific agent by name.

        Args:
            agent_name: Agent name (without .yaml extension)

        Returns:
            AgentConfiguration object

        Raises:
            FileNotFoundError: If agent doesn't exist
            AgentValidationError: If agent configuration is invalid
        """
        agent_file = self.agents_dir / f"{agent_name}.yaml"
        return AgentConfigParser.parse_agent_file(agent_file)

    def validate_agent(self, agent: AgentConfiguration) -> Tuple[List[str], List[str]]:
        """
        Validate agent configuration.

        Args:
            agent: AgentConfiguration to validate

        Returns:
            Tuple of (errors, warnings)
        """
        all_caps = self._load_capabilities()
        return AgentValidator.validate_agent(agent, all_caps)

    def get_agent_capabilities(
        self, agent: AgentConfiguration, include_dependencies: bool = True
    ) -> List[str]:
        """
        Get all capabilities for an agent (with optional dependency resolution).

        Args:
            agent: AgentConfiguration
            include_dependencies: Whether to resolve and include dependencies

        Returns:
            List of capability IDs
        """
        all_caps = self._load_capabilities()
        cap_list = agent.capabilities.all_capabilities()

        if not include_dependencies:
            return cap_list

        try:
            resolved = CompositionEngine.resolve_dependencies(cap_list, all_caps)
            return sorted(resolved)
        except Exception:
            # Return original list if resolution fails
            return cap_list

    def get_recommendations(self, agent: AgentConfiguration) -> List[str]:
        """
        Get capability recommendations for an agent.

        Args:
            agent: AgentConfiguration

        Returns:
            List of recommended capability IDs
        """
        all_caps = self._load_capabilities()
        return AgentValidator.get_recommendations(agent, all_caps)

    def save_agent(self, agent: AgentConfiguration, agent_name: str):
        """
        Save agent configuration to file.

        Args:
            agent: AgentConfiguration to save
            agent_name: File name (without .yaml extension)
        """
        # Ensure agents directory exists
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # Save to file
        agent_file = self.agents_dir / f"{agent_name}.yaml"
        with open(agent_file, 'w', encoding='utf-8') as f:
            yaml.dump(agent.to_dict(), f, default_flow_style=False, sort_keys=False)

    def delete_agent(self, agent_name: str):
        """
        Delete agent configuration.

        Args:
            agent_name: Agent name (without .yaml extension)

        Raises:
            FileNotFoundError: If agent doesn't exist
        """
        agent_file = self.agents_dir / f"{agent_name}.yaml"
        if not agent_file.exists():
            raise FileNotFoundError(f"Agent not found: {agent_name}")
        agent_file.unlink()


def create_agent_template(
    name: str,
    description: str,
    capabilities: AgentCapabilities,
    author: str = ""
) -> AgentConfiguration:
    """
    Create a new agent configuration from template.

    Args:
        name: Agent name
        description: Agent description
        capabilities: Agent capabilities
        author: Author name

    Returns:
        AgentConfiguration object with sensible defaults
    """
    today = datetime.now().strftime("%Y-%m-%d")

    return AgentConfiguration(
        name=name,
        version="1.0.0",
        description=description,
        created=today,
        author=author,
        capabilities=capabilities,
        context_priority=[
            "Read PROJECT_STATUS.md for current work",
            "Review relevant files for the task",
            "Check for existing patterns in codebase"
        ],
        agent_instructions=[
            "Follow project conventions and best practices",
            "Update PROJECT_STATUS.md as work progresses",
            "Write clear, maintainable code"
        ],
        required_files=["PROJECT_STATUS.md"],
        optional_files=[],
        tags=[],
        status="active"
    )
