"""
Setup Wizard for Agent Framework
Interactive project initialization with TDD support
"""

import os
import json
import yaml
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import re


class WizardStep:
    """Represents a single step in the setup wizard"""
    
    def __init__(self, 
                 name: str,
                 prompt: str,
                 validator: Optional[Callable] = None,
                 processor: Optional[Callable] = None,
                 options: Optional[List[str]] = None,
                 default: Optional[Any] = None):
        """
        Initialize a wizard step
        
        Args:
            name: Step identifier
            prompt: Prompt to display to user
            validator: Function to validate input
            processor: Function to process input
            options: List of valid options
            default: Default value
        """
        self.name = name
        self.prompt = prompt
        self.validator = validator or (lambda x: True)
        self.processor = processor or (lambda x: x)
        self.options = options
        self.default = default
    
    def validate(self, value: Any) -> bool:
        """Validate input value"""
        return self.validator(value)
    
    def process(self, value: Any) -> Any:
        """Process input value"""
        return self.processor(value)
    
    def execute(self) -> Any:
        """Execute the step interactively"""
        if self.options:
            print(f"\n{self.prompt}")
            for i, option in enumerate(self.options, 1):
                print(f"  {i}. {option}")
            
        while True:
            value = input(f"{self.prompt} " if not self.options else "Choice: ")
            
            if not value and self.default is not None:
                value = self.default
            
            if self.validate(value):
                return self.process(value)
            else:
                print("Invalid input. Please try again.")


class ProjectConfig:
    """Configuration for a new project"""
    
    def __init__(self,
                 name: str = "",
                 project_type: str = "",
                 git_enabled: bool = False,
                 testing_enabled: bool = True,
                 coverage_threshold: int = 80):
        """
        Initialize project configuration
        
        Args:
            name: Project name
            project_type: Type of project
            git_enabled: Enable Git repository
            testing_enabled: Enable testing (default True for TDD)
            coverage_threshold: Test coverage threshold
        """
        self.name = name
        self.project_type = project_type
        self.git_enabled = git_enabled
        self.testing_enabled = testing_enabled
        self.coverage_threshold = coverage_threshold
        self.agents_config = {
            'core_agents': ['backend', 'frontend', 'testing', 'devops'],
            'flex_pool': ['documentation', 'performance']
        }
    
    def validate(self) -> bool:
        """Validate the configuration"""
        if not self.name:
            return False
        
        valid_types = ['web-app', 'api', 'cli', 'library', 'microservice']
        if self.project_type not in valid_types:
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            'project': {
                'name': self.name,
                'type': self.project_type,
                'description': f'{self.name} - Created with Agent Framework',
                'repository': ''
            },
            'git': {
                'enabled': self.git_enabled,
                'main_branch': 'main',
                'dev_branch': 'development',
                'branch_prefix': {
                    'feature': 'feature/',
                    'bugfix': 'bugfix/',
                    'hotfix': 'hotfix/'
                }
            },
            'testing': {
                'enabled': self.testing_enabled,
                'framework': 'pytest',
                'test_directory': 'tests',
                'coverage_threshold': self.coverage_threshold,
                'coverage_enabled': True,
                'tdd_enforced': True
            },
            'agents': {
                'core': [
                    {'id': agent, 'name': f'{agent.title()} Agent'}
                    for agent in self.agents_config['core_agents']
                ],
                'flex_pool': [
                    {'id': agent, 'name': f'{agent.title()} Agent'}
                    for agent in self.agents_config['flex_pool']
                ]
            },
            'quality': {
                'test_coverage_minimum': self.coverage_threshold,
                'documentation_required': True
            },
            'workflows': {
                'auto_create_branch': True,
                'auto_create_tests': True,
                'auto_update_docs': True
            }
        }


class SetupWizard:
    """Interactive setup wizard for Agent Framework projects"""
    
    VALID_PROJECT_TYPES = ['web-app', 'api', 'cli', 'library', 'microservice']
    
    def __init__(self, base_path: str = ".", dry_run: bool = False):
        """
        Initialize the setup wizard
        
        Args:
            base_path: Base directory for project creation
            dry_run: If True, don't create actual files
        """
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.current_step = 0
        self.config = ProjectConfig()
        self.steps = self._initialize_steps()
        
        # State
        self.project_name = ""
        self.project_type = ""
        self.git_enabled = False
        self.testing_enabled = True
        self.coverage_threshold = 80
    
    def _initialize_steps(self) -> List[WizardStep]:
        """Initialize wizard steps"""
        return [
            WizardStep(
                name='project_name',
                prompt='Enter project name:',
                validator=self.validate_project_name,
                processor=lambda x: x.strip()
            ),
            WizardStep(
                name='project_type',
                prompt='Select project type:',
                options=self.VALID_PROJECT_TYPES,
                validator=lambda x: x in ['1', '2', '3', '4', '5'],
                processor=lambda x: self.VALID_PROJECT_TYPES[int(x) - 1]
            ),
            WizardStep(
                name='agents_config',
                prompt='Configure agents (press Enter for defaults):',
                default='default'
            ),
            WizardStep(
                name='git_config',
                prompt='Enable Git repository? (y/n):',
                validator=lambda x: x.lower() in ['y', 'n', 'yes', 'no'],
                processor=lambda x: x.lower() in ['y', 'yes'],
                default='y'
            ),
            WizardStep(
                name='testing_config',
                prompt='Enable testing? (y/n):',
                validator=lambda x: x.lower() in ['y', 'n', 'yes', 'no'],
                processor=lambda x: x.lower() in ['y', 'yes'],
                default='y'
            ),
            WizardStep(
                name='review',
                prompt='Review configuration',
                processor=lambda x: x
            ),
            WizardStep(
                name='create',
                prompt='Create project',
                processor=lambda x: x
            )
        ]
    
    def validate_project_name(self, name: str) -> bool:
        """Validate project name"""
        if not name:
            return False
        
        # Check for valid characters
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_-]*$', name):
            return False
        
        return True
    
    def set_project_name(self, name: str) -> bool:
        """Set project name"""
        if self.validate_project_name(name):
            self.project_name = name
            self.config.name = name
            return True
        return False
    
    def set_project_type(self, project_type: str) -> bool:
        """Set project type"""
        if project_type in self.VALID_PROJECT_TYPES:
            self.project_type = project_type
            self.config.project_type = project_type
            return True
        return False
    
    def set_git_enabled(self, enabled: bool):
        """Enable/disable Git"""
        self.git_enabled = enabled
        self.config.git_enabled = enabled
    
    def set_testing_enabled(self, enabled: bool, coverage_threshold: int = 80):
        """Enable/disable testing"""
        self.testing_enabled = enabled
        self.coverage_threshold = coverage_threshold
        self.config.testing_enabled = enabled
        self.config.coverage_threshold = coverage_threshold
    
    def configure_agents(self, agents_config: Dict[str, List[str]]):
        """Configure agents"""
        self.config.agents_config = agents_config
    
    def get_steps(self) -> List[WizardStep]:
        """Get wizard steps"""
        return self.steps
    
    def validate(self) -> bool:
        """Validate current configuration"""
        # Update config from current state
        self.config.name = self.project_name
        self.config.project_type = self.project_type
        # Now validate
        return self.config.validate()
    
    def generate_configuration(self) -> Dict[str, Any]:
        """Generate project configuration"""
        return self.config.to_dict()
    
    def create_project(self) -> Dict[str, Any]:
        """Create the project with all files"""
        if self.dry_run:
            return {
                'status': 'success',
                'dry_run': True,
                'message': 'Dry run completed successfully'
            }
        
        project_path = self.base_path / self.project_name
        
        # Check if project already exists
        if project_path.exists():
            return {
                'status': 'error',
                'error': f'Project directory already exists: {project_path}'
            }
        
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create configuration file
            self._create_config_file(project_path)
            
            # Create AGENTS.md
            self._create_agents_file(project_path)
            
            # Create PROJECT_STATUS.md
            self._create_project_status_file(project_path)
            
            # Create project structure
            self._create_project_structure(project_path)
            
            # Initialize Git if enabled
            if self.git_enabled:
                self._initialize_git(project_path)
            
            # Create test structure if enabled
            if self.testing_enabled:
                self._create_test_structure(project_path)
            
            # Create marker file to indicate framework initialization
            marker_file = project_path / ".agent-framework-initialized"
            marker_file.write_text(f"Initialized on {datetime.now().isoformat()}\nFramework version: 1.0.0\n")
            
            return {
                'status': 'success',
                'path': str(project_path),
                'message': f'Project created successfully at {project_path}'
            }
            
        except Exception as e:
            # Rollback - remove project directory
            if project_path.exists():
                shutil.rmtree(project_path)
            
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _create_config_file(self, project_path: Path):
        """Create agents.config.yaml"""
        config_file = project_path / "agents.config.yaml"
        config = self.generate_configuration()
        
        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def _create_agents_file(self, project_path: Path):
        """Create AGENTS.md"""
        agents_file = project_path / "AGENTS.md"
        
        content = f"""# AGENTS.md - {self.project_name}

> **Framework**: Using Agent Framework v1.0
> **Configuration**: `agents.config.yaml`
> **Project Type**: {self.project_type}

## Framework Activation

When this file is read by an AI agent, it should:

1. Load the Agent Framework
2. Use configuration from `agents.config.yaml`
3. Check `PROJECT_STATUS.md` for current state
4. Execute the framework workflow

```python
# Framework activation
from agent_framework.core.agent_framework import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator('agents.config.yaml')
orchestrator.execute_workflow()
```

## Project Context

This is a {self.project_type} project created with Agent Framework.

Features:
- 🤖 Automated agent workflow
- 🧪 TDD with {self.coverage_threshold}% coverage requirement
- 🌿 Git workflow integration
- 📊 Progress tracking

---

*Powered by Agent Framework*
"""
        
        with open(agents_file, 'w') as f:
            f.write(content)
    
    def _create_project_status_file(self, project_path: Path):
        """Create PROJECT_STATUS.md"""
        status_file = project_path / "PROJECT_STATUS.md"
        
        content = f"""# PROJECT STATUS - {self.project_name}

> **Single Source of Truth** for project state

## 📊 Current State

```yaml
project_phase: "Planning"
current_sprint: null
current_branch: "main"
last_ticket_id: 0
```

## 🎫 Active Tickets
*No active tickets yet*

## ✅ Completed Tickets
*None yet*

## 📈 Feature Progress

| Feature | Status | Progress | Notes |
|---------|--------|----------|-------|
| Project Setup | Complete | 100% | Framework initialized |

## 🔄 Recent Updates
- {datetime.now().strftime('%Y-%m-%d')}: Project created with Agent Framework

---
*Updated by Agent Framework*
"""
        
        with open(status_file, 'w') as f:
            f.write(content)
    
    def _create_project_structure(self, project_path: Path):
        """Create project directory structure"""
        # Create basic directories
        directories = ['src', 'tests', 'docs']
        
        # Add type-specific directories
        if self.project_type == 'web-app':
            directories.extend(['frontend', 'backend', 'public'])
        elif self.project_type == 'api':
            directories.extend(['app', 'api', 'models'])
        
        for dir_name in directories:
            (project_path / dir_name).mkdir(exist_ok=True)
        
        # Create __init__.py files for Python packages
        if self.project_type in ['api', 'library', 'cli']:
            for dir_name in ['src', 'tests']:
                init_file = project_path / dir_name / '__init__.py'
                init_file.touch()
    
    def _initialize_git(self, project_path: Path):
        """Initialize Git repository"""
        # Initialize git
        subprocess.run(['git', 'init'], cwd=project_path, check=True)
        
        # Create .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.env

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
test-results.json

# Node (for web projects)
node_modules/
dist/
build/

# OS
.DS_Store
Thumbs.db

# Project specific
*.log
*.db
.cache/
"""
        
        gitignore_file = project_path / ".gitignore"
        with open(gitignore_file, 'w') as f:
            f.write(gitignore_content)
        
        # Create initial commit
        subprocess.run(['git', 'add', '.'], cwd=project_path, check=True)
        subprocess.run(
            ['git', 'commit', '-m', 'Initial commit - Project created with Agent Framework'],
            cwd=project_path, 
            check=True
        )
        
        # Create development branch
        subprocess.run(['git', 'checkout', '-b', 'development'], cwd=project_path, check=True)
    
    def _create_test_structure(self, project_path: Path):
        """Create test structure for TDD"""
        tests_dir = project_path / 'tests'
        tests_dir.mkdir(exist_ok=True)
        
        # Create conftest.py for pytest
        conftest_file = tests_dir / 'conftest.py'
        conftest_content = """\"\"\"
Pytest configuration for {self.project_name}
\"\"\"

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))


@pytest.fixture
def sample_data():
    \"\"\"Sample data for tests\"\"\"
    return {
        'test': 'data'
    }
"""
        
        with open(conftest_file, 'w') as f:
            f.write(conftest_content)
        
        # Create pytest.ini
        pytest_ini = project_path / 'pytest.ini'
        pytest_content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --cov=src --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
"""
        
        with open(pytest_ini, 'w') as f:
            f.write(pytest_content)
        
        # Create requirements-test.txt
        requirements_test = project_path / 'requirements-test.txt'
        requirements_content = """pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
"""
        
        with open(requirements_test, 'w') as f:
            f.write(requirements_content)
    
    def run_interactive(self) -> Dict[str, Any]:
        """Run the wizard in interactive mode"""
        print("\n" + "=" * 60)
        print("🧙 Agent Framework Setup Wizard")
        print("=" * 60)
        
        try:
            # Project name
            name = input("\n📝 Enter project name: ")
            if not self.set_project_name(name):
                return {'status': 'error', 'error': 'Invalid project name'}
            
            # Project type
            print("\n📦 Select project type:")
            for i, ptype in enumerate(self.VALID_PROJECT_TYPES, 1):
                print(f"  {i}. {ptype}")
            
            choice = input("Choice (1-5): ")
            if choice.isdigit() and 1 <= int(choice) <= 5:
                self.set_project_type(self.VALID_PROJECT_TYPES[int(choice) - 1])
            else:
                return {'status': 'error', 'error': 'Invalid project type'}
            
            # Git
            git_choice = input("\n🌿 Enable Git repository? (y/n) [y]: ") or 'y'
            self.set_git_enabled(git_choice.lower() in ['y', 'yes'])
            
            # Testing
            test_choice = input("\n🧪 Enable testing? (y/n) [y]: ") or 'y'
            if test_choice.lower() in ['y', 'yes']:
                coverage = input("  Coverage threshold (%) [80]: ") or '80'
                self.set_testing_enabled(True, int(coverage))
            else:
                self.set_testing_enabled(False)
            
            # Remote repository
            remote_choice = input("\n☁️  Configure remote repository? (y/n) [n]: ") or 'n'
            
            # Create project
            print("\n" + "=" * 60)
            print("📋 Configuration Summary:")
            print(f"  Project: {self.project_name}")
            print(f"  Type: {self.project_type}")
            print(f"  Git: {'✅' if self.git_enabled else '❌'}")
            print(f"  Testing: {'✅' if self.testing_enabled else '❌'}")
            if self.testing_enabled:
                print(f"  Coverage: {self.coverage_threshold}%")
            print("=" * 60)
            
            confirm = input("\n🚀 Create project? (y/n) [y]: ") or 'y'
            if confirm.lower() not in ['y', 'yes']:
                return {
                    'status': 'cancelled', 
                    'message': 'Project creation cancelled',
                    'project_name': self.project_name,
                    'project_type': self.project_type,
                    'git_enabled': self.git_enabled,
                    'testing_enabled': self.testing_enabled
                }
            
            # Create the project
            result = self.create_project()
            
            if result['status'] == 'success':
                print(f"\n✅ Project created successfully!")
                print(f"📁 Location: {result.get('path')}")
                print("\n🎯 Next steps:")
                print("  1. cd " + self.project_name)
                print("  2. Read AGENTS.md to start development")
                print("  3. Use TDD - write tests first!")
            else:
                print(f"\n❌ Error: {result.get('error')}")
            
            # Always return the configuration info
            return {
                'status': result['status'],
                'project_name': self.project_name,
                'project_type': self.project_type,
                'git_enabled': self.git_enabled,
                'testing_enabled': self.testing_enabled,
                'path': result.get('path'),
                'error': result.get('error'),
                'message': result.get('message')
            }
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user")
            return {'status': 'cancelled'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def execute(self) -> Dict[str, Any]:
        """Execute the wizard (wrapper for create_project)"""
        if not self.validate():
            return {'status': 'error', 'error': 'Invalid configuration'}
        
        return self.create_project()


# CLI entry point
if __name__ == "__main__":
    import sys
    
    # Check if running in interactive mode
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        wizard = SetupWizard(dry_run=True)
    else:
        wizard = SetupWizard()
    
    # Run interactive wizard
    result = wizard.run_interactive()
    
    # Exit with appropriate code
    sys.exit(0 if result['status'] == 'success' else 1)