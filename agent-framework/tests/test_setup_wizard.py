"""
Tests for Setup Wizard
TDD - Red, Green, Refactor cycle
Written BEFORE implementation as per TDD principles
"""

import pytest
from pathlib import Path
import sys
import tempfile
import json
import yaml
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# This import will fail initially (RED phase) until we implement the module
try:
    from core.setup_wizard import SetupWizard, WizardStep, ProjectConfig
except ImportError:
    # Expected to fail in RED phase
    SetupWizard = None
    WizardStep = None
    ProjectConfig = None


class TestSetupWizard:
    """Test suite for Setup Wizard following TDD principles"""
    
    # RED Phase: Write failing tests first
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_wizard_initialization(self):
        """Test that wizard can be initialized"""
        wizard = SetupWizard()
        assert wizard is not None
        assert wizard.current_step == 0
        assert len(wizard.steps) > 0
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_project_name_validation(self):
        """Test project name validation"""
        wizard = SetupWizard()
        
        # Valid names
        assert wizard.validate_project_name("my-project") == True
        assert wizard.validate_project_name("MyProject123") == True
        assert wizard.validate_project_name("test_project") == True
        
        # Invalid names
        assert wizard.validate_project_name("") == False
        assert wizard.validate_project_name("my project") == False  # No spaces
        assert wizard.validate_project_name("123project") == False  # Can't start with number
        assert wizard.validate_project_name("-project") == False  # Can't start with dash
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_project_type_selection(self):
        """Test project type selection"""
        wizard = SetupWizard()
        
        # Valid types
        assert wizard.set_project_type("web-app") == True
        assert wizard.set_project_type("api") == True
        assert wizard.set_project_type("cli") == True
        assert wizard.set_project_type("library") == True
        assert wizard.set_project_type("microservice") == True
        
        # Invalid type
        assert wizard.set_project_type("invalid-type") == False
        assert wizard.set_project_type("") == False
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_configuration_generation(self):
        """Test configuration file generation"""
        wizard = SetupWizard()
        wizard.set_project_name("test-project")
        wizard.set_project_type("web-app")
        
        config = wizard.generate_configuration()
        
        assert config is not None
        assert config['project']['name'] == "test-project"
        assert config['project']['type'] == "web-app"
        assert 'agents' in config
        assert 'git' in config
        assert 'testing' in config
        assert config['testing']['framework'] == 'pytest'
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_file_creation(self):
        """Test that wizard creates necessary files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            wizard.set_project_name("test-project")
            wizard.set_project_type("web-app")
            
            result = wizard.create_project()
            
            assert result['status'] == 'success'
            assert Path(tmpdir, "test-project").exists()
            assert Path(tmpdir, "test-project", "AGENTS.md").exists()
            assert Path(tmpdir, "test-project", "PROJECT_STATUS.md").exists()
            assert Path(tmpdir, "test-project", "agents.config.yaml").exists()
            
            # Check AGENTS.md content
            agents_file = Path(tmpdir, "test-project", "AGENTS.md")
            content = agents_file.read_text()
            assert "test-project" in content
            assert "Agent Framework" in content
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_git_initialization(self):
        """Test Git repository initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            wizard.set_project_name("test-project")
            wizard.set_project_type("web-app")
            wizard.set_git_enabled(True)
            
            result = wizard.create_project()
            
            assert Path(tmpdir, "test-project", ".git").exists()
            assert Path(tmpdir, "test-project", ".gitignore").exists()
            
            # Check .gitignore content
            gitignore = Path(tmpdir, "test-project", ".gitignore")
            content = gitignore.read_text()
            assert "__pycache__" in content
            assert ".env" in content
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    @patch('builtins.input')
    def test_interactive_mode(self, mock_input):
        """Test interactive wizard mode"""
        # Mock user inputs
        mock_input.side_effect = [
            "my-awesome-project",  # Project name
            "2",  # Project type (API)
            "y",  # Enable Git
            "y",  # Enable testing
            "80",  # Coverage threshold
            "n",  # No remote repository
            "y",  # Confirm creation
        ]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            result = wizard.run_interactive()
            
            assert result['project_name'] == "my-awesome-project"
            assert result['project_type'] == "api"
            assert result['git_enabled'] == True
            assert result['testing_enabled'] == True
            assert result['status'] == 'success'
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_template_copying(self):
        """Test that templates are copied correctly"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            wizard.set_project_name("test-project")
            wizard.set_project_type("web-app")
            
            wizard.create_project()
            
            # Check web-app specific structure
            project_path = Path(tmpdir, "test-project")
            
            # Should have basic directories
            assert Path(project_path, "src").exists() or Path(project_path, "app").exists()
            assert Path(project_path, "tests").exists()
            
            # Should have configuration files
            assert Path(project_path, "agents.config.yaml").exists()
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_agent_configuration(self):
        """Test agent configuration customization"""
        wizard = SetupWizard()
        wizard.set_project_name("test-project")
        
        # Configure agents
        wizard.configure_agents({
            'core_agents': ['backend', 'frontend', 'testing'],
            'flex_pool': ['documentation', 'performance']
        })
        
        config = wizard.generate_configuration()
        assert len(config['agents']['core']) >= 3
        assert len(config['agents']['flex_pool']) >= 2
        
        # Check agent names
        core_names = [agent['id'] for agent in config['agents']['core']]
        assert 'backend' in core_names
        assert 'frontend' in core_names
        assert 'testing' in core_names
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_wizard_steps_order(self):
        """Test that wizard steps are executed in correct order"""
        wizard = SetupWizard()
        
        steps = wizard.get_steps()
        step_names = [s.name for s in steps]
        
        # Essential steps must be present
        assert 'project_name' in step_names
        assert 'project_type' in step_names
        assert 'create' in step_names
        
        # project_name should come before project_type
        assert step_names.index('project_name') < step_names.index('project_type')
        # create should be last
        assert step_names.index('create') == len(step_names) - 1
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_rollback_on_failure(self):
        """Test that wizard can rollback on failure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            wizard.set_project_name("test-project")
            wizard.set_project_type("web-app")
            
            # Simulate failure by patching a method
            with patch.object(wizard, '_create_config_file', side_effect=Exception("Config creation failed")):
                result = wizard.create_project()
                
                assert result['status'] == 'error'
                assert 'Config creation failed' in result.get('error', '')
                # Project directory should be cleaned up
                assert not Path(tmpdir, "test-project").exists()
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_dry_run_mode(self):
        """Test dry run mode doesn't create files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir, dry_run=True)
            wizard.set_project_name("test-project")
            wizard.set_project_type("api")
            
            result = wizard.create_project()
            
            assert result['status'] == 'success'
            assert result.get('dry_run') == True
            # No files should be created in dry run
            assert not Path(tmpdir, "test-project").exists()
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_project_exists_error(self):
        """Test error when project already exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create existing project
            existing = Path(tmpdir, "existing-project")
            existing.mkdir()
            
            wizard = SetupWizard(base_path=tmpdir)
            wizard.set_project_name("existing-project")
            wizard.set_project_type("web-app")
            
            result = wizard.create_project()
            
            assert result['status'] == 'error'
            assert 'already exists' in result.get('error', '').lower()
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    @pytest.fixture
    def wizard_with_config(self):
        """Fixture providing configured wizard"""
        wizard = SetupWizard()
        wizard.set_project_name("fixture-project")
        wizard.set_project_type("api")
        wizard.set_git_enabled(True)
        wizard.set_testing_enabled(True)
        return wizard
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_validation_with_fixture(self, wizard_with_config):
        """Test validation using fixture"""
        assert wizard_with_config.validate() == True
        
        # Test invalid state
        wizard_with_config.project_name = ""
        assert wizard_with_config.validate() == False
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    def test_config_file_content(self):
        """Test that generated config file has correct content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            wizard.set_project_name("test-project")
            wizard.set_project_type("api")
            wizard.set_testing_enabled(True, coverage_threshold=85)
            
            result = wizard.create_project()
            
            config_file = Path(tmpdir, "test-project", "agents.config.yaml")
            assert config_file.exists()
            
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            assert config['project']['name'] == "test-project"
            assert config['project']['type'] == "api"
            assert config['testing']['coverage_threshold'] == 85
            assert config['testing']['framework'] == 'pytest'


class TestWizardStep:
    """Test the WizardStep class"""
    
    @pytest.mark.skipif(WizardStep is None, reason="WizardStep not yet implemented")
    def test_step_creation(self):
        """Test creating a wizard step"""
        step = WizardStep(
            name="test_step",
            prompt="Enter test value:",
            validator=lambda x: len(x) > 0,
            processor=lambda x: x.upper()
        )
        
        assert step.name == "test_step"
        assert step.prompt == "Enter test value:"
        assert step.validate("test") == True
        assert step.validate("") == False
        assert step.process("test") == "TEST"
    
    @pytest.mark.skipif(WizardStep is None, reason="WizardStep not yet implemented")
    def test_step_execution(self):
        """Test executing a wizard step"""
        step = WizardStep(
            name="test_step",
            prompt="Enter value:",
            validator=lambda x: x.isdigit(),
            processor=int
        )
        
        with patch('builtins.input', return_value='42'):
            result = step.execute()
            assert result == 42
    
    @pytest.mark.skipif(WizardStep is None, reason="WizardStep not yet implemented")
    def test_step_with_options(self):
        """Test step with multiple choice options"""
        step = WizardStep(
            name="choice_step",
            prompt="Select option:",
            options=['option1', 'option2', 'option3'],
            validator=lambda x: x in ['1', '2', '3'],
            processor=lambda x: f'option{x}'
        )
        
        assert step.options == ['option1', 'option2', 'option3']
        assert step.validate('1') == True
        assert step.validate('4') == False
        assert step.process('2') == 'option2'


class TestProjectConfig:
    """Test the ProjectConfig class"""
    
    @pytest.mark.skipif(ProjectConfig is None, reason="ProjectConfig not yet implemented")
    def test_config_creation(self):
        """Test creating a project configuration"""
        config = ProjectConfig(
            name="test-project",
            project_type="web-app"
        )
        
        assert config.name == "test-project"
        assert config.project_type == "web-app"
        assert config.git_enabled == False  # Default
        assert config.testing_enabled == True  # Default for TDD
    
    @pytest.mark.skipif(ProjectConfig is None, reason="ProjectConfig not yet implemented")
    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = ProjectConfig(
            name="test-project",
            project_type="api",
            git_enabled=True,
            testing_enabled=True,
            coverage_threshold=90
        )
        
        config_dict = config.to_dict()
        
        assert config_dict['project']['name'] == "test-project"
        assert config_dict['project']['type'] == "api"
        assert config_dict['git']['enabled'] == True
        assert config_dict['testing']['enabled'] == True
        assert config_dict['testing']['coverage_threshold'] == 90
    
    @pytest.mark.skipif(ProjectConfig is None, reason="ProjectConfig not yet implemented")
    def test_config_validation(self):
        """Test configuration validation"""
        # Valid config
        config = ProjectConfig(
            name="valid-project",
            project_type="cli"
        )
        assert config.validate() == True
        
        # Invalid config - no name
        config = ProjectConfig(
            name="",
            project_type="cli"
        )
        assert config.validate() == False
        
        # Invalid config - invalid type
        config = ProjectConfig(
            name="test",
            project_type="invalid"
        )
        assert config.validate() == False


# Integration tests
class TestSetupWizardIntegration:
    """Integration tests for the complete wizard flow"""
    
    @pytest.mark.skipif(SetupWizard is None, reason="SetupWizard not yet implemented")
    @pytest.mark.integration
    def test_complete_project_creation(self):
        """Test complete project creation flow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = SetupWizard(base_path=tmpdir)
            
            # Configure project
            wizard.set_project_name("integration-test")
            wizard.set_project_type("web-app")
            wizard.set_git_enabled(True)
            wizard.set_testing_enabled(True, coverage_threshold=75)
            wizard.configure_agents({
                'core_agents': ['backend', 'frontend', 'testing', 'devops'],
                'flex_pool': ['documentation', 'security']
            })
            
            # Create project
            result = wizard.create_project()
            
            assert result['status'] == 'success'
            
            # Verify all files created
            project_path = Path(tmpdir, "integration-test")
            assert project_path.exists()
            assert (project_path / "AGENTS.md").exists()
            assert (project_path / "PROJECT_STATUS.md").exists()
            assert (project_path / "agents.config.yaml").exists()
            assert (project_path / ".git").exists()
            assert (project_path / ".gitignore").exists()
            assert (project_path / "tests").exists()
            
            # Verify config content
            with open(project_path / "agents.config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            
            assert config['project']['name'] == "integration-test"
            assert config['testing']['coverage_threshold'] == 75
            assert len(config['agents']['core']) == 4
            assert len(config['agents']['flex_pool']) == 2