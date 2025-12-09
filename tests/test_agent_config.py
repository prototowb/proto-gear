"""
Tests for agent configuration system

Tests cover:
- Agent configuration parsing
- Agent validation
- Agent management
- Capability composition
- Error handling
"""

import pytest
import tempfile
from pathlib import Path
import yaml

from proto_gear_pkg.agent_config import (
    AgentConfiguration,
    AgentConfigParser,
    AgentValidator,
    AgentManager,
    AgentCapabilities,
    AgentValidationError,
    create_agent_template
)


# ============================================================================
# Test Data Fixtures
# ============================================================================

@pytest.fixture
def valid_agent_dict():
    """Valid agent configuration dictionary"""
    return {
        "name": "Testing Agent",
        "version": "1.0.0",
        "description": "Agent for TDD and quality assurance",
        "created": "2025-12-09",
        "author": "Test Author",
        "capabilities": {
            "skills": ["testing", "debugging"],
            "workflows": ["feature-development"],
            "commands": ["analyze-coverage"]
        },
        "context_priority": [
            "Read TESTING.md first",
            "Check test coverage"
        ],
        "agent_instructions": [
            "Follow TDD",
            "Aim for 80%+ coverage"
        ],
        "required_files": ["TESTING.md"],
        "optional_files": ["PROJECT_STATUS.md"],
        "tags": ["testing", "tdd"],
        "status": "active"
    }


@pytest.fixture
def temp_agent_file(tmp_path, valid_agent_dict):
    """Create temporary agent YAML file"""
    agent_file = tmp_path / "testing-agent.yaml"
    with open(agent_file, 'w') as f:
        yaml.dump(valid_agent_dict, f)
    return agent_file


@pytest.fixture
def temp_agents_dir(tmp_path):
    """Create temporary agents directory"""
    agents_dir = tmp_path / "agents"
    agents_dir.mkdir()
    return agents_dir


@pytest.fixture
def temp_capabilities_dir(tmp_path):
    """Create temporary capabilities directory with mock metadata"""
    caps_dir = tmp_path / "capabilities"

    # Create skills
    skills_dir = caps_dir / "skills" / "testing"
    skills_dir.mkdir(parents=True)
    metadata = {
        "name": "Testing",
        "type": "skill",
        "version": "1.0.0",
        "description": "Testing skill",
        "category": "testing",
        "tags": ["testing"],
        "status": "stable",
        "author": "Test",
        "last_updated": "2025-12-09",
        "dependencies": {"required": [], "optional": [], "suggested": []},
        "conflicts": [],
        "composable_with": [],
        "agent_roles": []
    }
    with open(skills_dir / "metadata.yaml", 'w') as f:
        yaml.dump(metadata, f)

    return caps_dir


# ============================================================================
# Parsing Tests
# ============================================================================

class TestAgentConfigParser:
    """Tests for AgentConfigParser"""

    def test_parse_valid_agent(self, valid_agent_dict):
        """Test parsing valid agent configuration"""
        agent = AgentConfigParser._parse_agent_dict(valid_agent_dict)

        assert agent.name == "Testing Agent"
        assert agent.version == "1.0.0"
        assert agent.description == "Agent for TDD and quality assurance"
        assert agent.author == "Test Author"
        assert agent.status == "active"

    def test_parse_agent_file(self, temp_agent_file):
        """Test parsing agent from file"""
        agent = AgentConfigParser.parse_agent_file(temp_agent_file)

        assert agent.name == "Testing Agent"
        assert agent.source_file == temp_agent_file

    def test_parse_missing_file(self, tmp_path):
        """Test parsing nonexistent file raises error"""
        with pytest.raises(FileNotFoundError):
            AgentConfigParser.parse_agent_file(tmp_path / "nonexistent.yaml")

    def test_parse_missing_required_field(self, valid_agent_dict):
        """Test parsing with missing required field"""
        del valid_agent_dict["name"]

        with pytest.raises(AgentValidationError, match="Missing required fields"):
            AgentConfigParser._parse_agent_dict(valid_agent_dict)

    def test_parse_invalid_version_format(self, valid_agent_dict):
        """Test parsing with invalid version format"""
        valid_agent_dict["version"] = "1.0"  # Not semantic versioning

        with pytest.raises(AgentValidationError, match="Invalid version format"):
            AgentConfigParser._parse_agent_dict(valid_agent_dict)

    def test_parse_invalid_date_format(self, valid_agent_dict):
        """Test parsing with invalid date format"""
        valid_agent_dict["created"] = "12/09/2025"  # Not YYYY-MM-DD

        with pytest.raises(AgentValidationError, match="Invalid date format"):
            AgentConfigParser._parse_agent_dict(valid_agent_dict)

    def test_parse_no_capabilities(self, valid_agent_dict):
        """Test parsing agent with no capabilities"""
        valid_agent_dict["capabilities"] = {
            "skills": [],
            "workflows": [],
            "commands": []
        }

        with pytest.raises(AgentValidationError, match="at least one capability"):
            AgentConfigParser._parse_agent_dict(valid_agent_dict)

    def test_parse_invalid_status(self, valid_agent_dict):
        """Test parsing with invalid status"""
        valid_agent_dict["status"] = "invalid_status"

        with pytest.raises(AgentValidationError, match="Invalid status"):
            AgentConfigParser._parse_agent_dict(valid_agent_dict)

    def test_parse_minimal_agent(self):
        """Test parsing agent with only required fields"""
        minimal = {
            "name": "Minimal Agent",
            "version": "1.0.0",
            "description": "Minimal description",
            "created": "2025-12-09",
            "capabilities": {
                "skills": ["testing"]
            }
        }

        agent = AgentConfigParser._parse_agent_dict(minimal)

        assert agent.name == "Minimal Agent"
        assert agent.author == ""
        assert agent.context_priority == []
        assert agent.agent_instructions == []
        assert agent.status == "active"


# ============================================================================
# Agent Capabilities Tests
# ============================================================================

class TestAgentCapabilities:
    """Tests for AgentCapabilities"""

    def test_all_capabilities(self):
        """Test getting all capabilities as full paths"""
        caps = AgentCapabilities(
            skills=["testing", "debugging"],
            workflows=["bug-fix"],
            commands=["create-ticket"]
        )

        all_caps = caps.all_capabilities()

        assert "skills/testing" in all_caps
        assert "skills/debugging" in all_caps
        assert "workflows/bug-fix" in all_caps
        assert "commands/create-ticket" in all_caps
        assert len(all_caps) == 4

    def test_is_empty(self):
        """Test checking if capabilities are empty"""
        empty = AgentCapabilities()
        assert empty.is_empty()

        non_empty = AgentCapabilities(skills=["testing"])
        assert not non_empty.is_empty()

    def test_to_dict(self):
        """Test converting to dictionary"""
        caps = AgentCapabilities(
            skills=["testing"],
            workflows=["bug-fix"],
            commands=[]
        )

        caps_dict = caps.to_dict()

        assert caps_dict["skills"] == ["testing"]
        assert caps_dict["workflows"] == ["bug-fix"]
        assert caps_dict["commands"] == []


# ============================================================================
# Agent Manager Tests
# ============================================================================

class TestAgentManager:
    """Tests for AgentManager"""

    def test_list_agents_empty_dir(self, temp_agents_dir, temp_capabilities_dir):
        """Test listing agents in empty directory"""
        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)
        agents = manager.list_agents()

        assert len(agents) == 0

    def test_list_agents_with_agents(
        self, temp_agents_dir, temp_capabilities_dir, valid_agent_dict
    ):
        """Test listing agents in directory with agents"""
        # Create agent files
        agent1_file = temp_agents_dir / "agent1.yaml"
        with open(agent1_file, 'w') as f:
            yaml.dump(valid_agent_dict, f)

        agent2_dict = valid_agent_dict.copy()
        agent2_dict["name"] = "Another Agent"
        agent2_file = temp_agents_dir / "agent2.yaml"
        with open(agent2_file, 'w') as f:
            yaml.dump(agent2_dict, f)

        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)
        agents = manager.list_agents()

        assert len(agents) == 2
        assert agents[0].name == "Another Agent"  # Sorted alphabetically
        assert agents[1].name == "Testing Agent"

    def test_load_agent(self, temp_agents_dir, temp_capabilities_dir, valid_agent_dict):
        """Test loading specific agent"""
        agent_file = temp_agents_dir / "testing-agent.yaml"
        with open(agent_file, 'w') as f:
            yaml.dump(valid_agent_dict, f)

        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)
        agent = manager.load_agent("testing-agent")

        assert agent.name == "Testing Agent"

    def test_load_nonexistent_agent(self, temp_agents_dir, temp_capabilities_dir):
        """Test loading nonexistent agent raises error"""
        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)

        with pytest.raises(FileNotFoundError):
            manager.load_agent("nonexistent")

    def test_save_agent(self, temp_agents_dir, temp_capabilities_dir):
        """Test saving agent configuration"""
        agent = create_agent_template(
            name="Test Agent",
            description="Test description",
            capabilities=AgentCapabilities(skills=["testing"])
        )

        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)
        manager.save_agent(agent, "test-agent")

        # Verify file was created
        agent_file = temp_agents_dir / "test-agent.yaml"
        assert agent_file.exists()

        # Verify content
        with open(agent_file, 'r') as f:
            data = yaml.safe_load(f)
        assert data["name"] == "Test Agent"

    def test_delete_agent(self, temp_agents_dir, temp_capabilities_dir, valid_agent_dict):
        """Test deleting agent configuration"""
        agent_file = temp_agents_dir / "test-agent.yaml"
        with open(agent_file, 'w') as f:
            yaml.dump(valid_agent_dict, f)

        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)
        manager.delete_agent("test-agent")

        assert not agent_file.exists()

    def test_delete_nonexistent_agent(self, temp_agents_dir, temp_capabilities_dir):
        """Test deleting nonexistent agent raises error"""
        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)

        with pytest.raises(FileNotFoundError):
            manager.delete_agent("nonexistent")


# ============================================================================
# Template Creation Tests
# ============================================================================

class TestCreateAgentTemplate:
    """Tests for create_agent_template"""

    def test_create_basic_template(self):
        """Test creating basic agent template"""
        agent = create_agent_template(
            name="My Agent",
            description="My description",
            capabilities=AgentCapabilities(skills=["testing"]),
            author="Me"
        )

        assert agent.name == "My Agent"
        assert agent.description == "My description"
        assert agent.author == "Me"
        assert agent.version == "1.0.0"
        assert agent.capabilities.skills == ["testing"]
        assert len(agent.context_priority) > 0
        assert len(agent.agent_instructions) > 0

    def test_create_template_without_author(self):
        """Test creating template without author"""
        agent = create_agent_template(
            name="Agent",
            description="Description",
            capabilities=AgentCapabilities(workflows=["bug-fix"])
        )

        assert agent.author == ""
        assert agent.capabilities.workflows == ["bug-fix"]


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests for agent system"""

    def test_full_workflow(self, temp_agents_dir, temp_capabilities_dir):
        """Test complete workflow: create → save → load → delete"""
        manager = AgentManager(temp_agents_dir, temp_capabilities_dir)

        # Create agent
        agent = create_agent_template(
            name="Test Agent",
            description="Test description",
            capabilities=AgentCapabilities(skills=["testing"]),
            author="Test Author"
        )

        # Save agent
        manager.save_agent(agent, "test-agent")

        # List agents
        agents = manager.list_agents()
        assert len(agents) == 1
        assert agents[0].name == "Test Agent"

        # Load agent
        loaded_agent = manager.load_agent("test-agent")
        assert loaded_agent.name == "Test Agent"
        assert loaded_agent.author == "Test Author"

        # Delete agent
        manager.delete_agent("test-agent")
        agents = manager.list_agents()
        assert len(agents) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
