"""
Tests for agent_framework.py
Following TDD principles - core agent system testing
"""

import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from agent_framework import (
    SprintType,
    TicketStatus,
    Agent,
    AdaptiveHybridSystem
)

# Try to import TicketGenerator (may fail due to dependencies)
try:
    from agent_framework import TicketGenerator
    TICKET_GENERATOR_AVAILABLE = True
except (ImportError, NameError):
    TICKET_GENERATOR_AVAILABLE = False


class TestSprintType:
    """Test SprintType enumeration"""

    def test_sprint_types_defined(self):
        """Test that all sprint types are defined"""
        assert SprintType.FEATURE_DEVELOPMENT
        assert SprintType.BUG_FIXING
        assert SprintType.PERFORMANCE_OPTIMIZATION
        assert SprintType.DEPLOYMENT_PREP
        assert SprintType.REFACTORING
        assert SprintType.RESEARCH_INTEGRATION

    def test_sprint_type_values(self):
        """Test sprint type values are correct"""
        assert SprintType.FEATURE_DEVELOPMENT.value == "feature_development"
        assert SprintType.BUG_FIXING.value == "bug_fixing"
        assert SprintType.PERFORMANCE_OPTIMIZATION.value == "performance_optimization"


class TestTicketStatus:
    """Test TicketStatus enumeration"""

    def test_ticket_statuses_defined(self):
        """Test that all ticket statuses are defined"""
        assert TicketStatus.PENDING
        assert TicketStatus.IN_PROGRESS
        assert TicketStatus.COMPLETED
        assert TicketStatus.BLOCKED
        assert TicketStatus.CANCELLED

    def test_ticket_status_values(self):
        """Test ticket status values"""
        assert TicketStatus.PENDING.value == "pending"
        assert TicketStatus.IN_PROGRESS.value == "in_progress"
        assert TicketStatus.COMPLETED.value == "completed"


class TestAgent:
    """Test Agent base class"""

    def test_agent_initialization(self):
        """Test agent can be initialized with proper attributes"""
        agent = Agent(
            agent_id="test-001",
            name="Test Agent",
            description="A test agent",
            responsibilities=["testing", "validation"]
        )

        assert agent.id == "test-001"
        assert agent.name == "Test Agent"
        assert agent.description == "A test agent"
        assert agent.responsibilities == ["testing", "validation"]
        assert agent.active is False
        assert agent.current_task is None
        assert agent.utilization == 0.0

    def test_agent_activation(self):
        """Test agent activation"""
        agent = Agent("test-001", "Test Agent", "Description", [])

        agent.activate()

        assert agent.active is True

    def test_agent_deactivation(self):
        """Test agent deactivation"""
        agent = Agent("test-001", "Test Agent", "Description", [])

        # Activate and assign task
        agent.activate()
        agent.assign_task({"id": "task-1", "name": "Test Task"})

        # Deactivate
        agent.deactivate()

        assert agent.active is False
        assert agent.current_task is None
        assert agent.utilization == 0.0

    def test_agent_assign_task(self):
        """Test task assignment to agent"""
        agent = Agent("test-001", "Test Agent", "Description", [])
        task = {"id": "task-1", "name": "Test Task", "priority": "high"}

        result = agent.assign_task(task)

        assert agent.current_task == task
        assert agent.utilization == 1.0
        assert "task-1" in result
        assert "Test Agent" in result

    def test_agent_execute_not_implemented(self):
        """Test that base agent execute raises NotImplementedError"""
        agent = Agent("test-001", "Test Agent", "Description", [])

        with pytest.raises(NotImplementedError):
            agent.execute({})


class TestAdaptiveHybridSystem:
    """Test AdaptiveHybridSystem"""

    def test_system_initialization(self):
        """Test adaptive hybrid system initialization"""
        # Use default config (no config file)
        system = AdaptiveHybridSystem("nonexistent.yaml")

        assert system is not None
        assert system.config is not None
        assert isinstance(system.core_agents, dict)
        assert isinstance(system.flex_agents, dict)
        assert isinstance(system.flex_pool, dict)

    def test_system_constants(self):
        """Test system constants are correct"""
        assert AdaptiveHybridSystem.MAX_AGENTS == 6
        assert AdaptiveHybridSystem.CORE_SLOTS == 4
        assert AdaptiveHybridSystem.FLEX_SLOTS == 2

    def test_system_uses_default_config_when_no_file(self):
        """Test system uses default config when file doesn't exist"""
        system = AdaptiveHybridSystem("nonexistent-config.yaml")

        assert system.config is not None
        # Should have default configuration


@pytest.mark.skipif(not TICKET_GENERATOR_AVAILABLE, reason="TicketGenerator not available due to dependencies")
class TestTicketGenerator:
    """Test TicketGenerator"""

    def test_ticket_generator_exists(self):
        """Test TicketGenerator class exists"""
        if TICKET_GENERATOR_AVAILABLE:
            assert TicketGenerator is not None


class TestAgentIntegration:
    """Integration tests for agent system"""

    def test_multiple_agents_can_coexist(self):
        """Test that multiple agents can be created and managed"""
        agents = [
            Agent(f"agent-{i}", f"Agent {i}", f"Description {i}", [f"task-{i}"])
            for i in range(4)
        ]

        assert len(agents) == 4
        for agent in agents:
            assert agent.active is False

        # Activate all
        for agent in agents:
            agent.activate()

        assert all(agent.active for agent in agents)

    def test_agent_task_workflow(self):
        """Test complete agent task workflow"""
        agent = Agent("test-001", "Test Agent", "Test", ["development"])

        # Start inactive
        assert agent.active is False

        # Activate
        agent.activate()
        assert agent.active is True

        # Assign task
        task = {"id": "task-1", "name": "Build feature", "priority": "high"}
        agent.assign_task(task)
        assert agent.current_task == task
        assert agent.utilization == 1.0

        # Deactivate (task complete)
        agent.deactivate()
        assert agent.active is False
        assert agent.current_task is None
        assert agent.utilization == 0.0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
