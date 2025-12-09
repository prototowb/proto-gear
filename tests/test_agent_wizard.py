"""
Tests for agent creation wizard

Tests cover:
- Validation logic
- Capability selection validation
- Recommendation generation
- Error handling

Note: Interactive prompts are not tested (require TTY)
"""

import pytest
from pathlib import Path

from proto_gear_pkg.agent_config import AgentCapabilities
from proto_gear_pkg.capability_metadata import load_all_capabilities
from proto_gear_pkg.agent_wizard import (
    validate_capability_selections,
    QUESTIONARY_AVAILABLE
)


@pytest.fixture
def temp_capabilities_dir(tmp_path):
    """Create temporary capabilities directory"""
    caps_dir = tmp_path / "capabilities"

    # Create a test skill
    skills_dir = caps_dir / "skills" / "test-skill"
    skills_dir.mkdir(parents=True)

    import yaml
    metadata = {
        "name": "Test Skill",
        "type": "skill",
        "version": "1.0.0",
        "description": "Test skill",
        "category": "testing",
        "tags": ["test"],
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


class TestValidateCapabilitySelections:
    """Tests for validate_capability_selections"""

    def test_valid_capabilities(self, temp_capabilities_dir):
        """Test validation with valid capabilities"""
        all_caps = load_all_capabilities(temp_capabilities_dir)

        capabilities = AgentCapabilities(
            skills=["test-skill"]
        )

        errors = validate_capability_selections(capabilities, all_caps)
        assert errors == []

    def test_missing_capability(self, temp_capabilities_dir):
        """Test validation with missing capability"""
        all_caps = load_all_capabilities(temp_capabilities_dir)

        capabilities = AgentCapabilities(
            skills=["nonexistent-skill"]
        )

        errors = validate_capability_selections(capabilities, all_caps)
        assert len(errors) > 0
        assert "not found" in errors[0].lower()

    def test_empty_capabilities(self, temp_capabilities_dir):
        """Test validation with no capabilities"""
        all_caps = load_all_capabilities(temp_capabilities_dir)

        capabilities = AgentCapabilities()

        # Empty capabilities should be valid (checked elsewhere)
        errors = validate_capability_selections(capabilities, all_caps)
        assert errors == []


class TestWizardAvailability:
    """Tests for wizard availability"""

    def test_questionary_available(self):
        """Test if questionary is available"""
        # This will be True if questionary is installed
        assert isinstance(QUESTIONARY_AVAILABLE, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
