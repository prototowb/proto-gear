"""
Comprehensive Tests for ProtoGear Project Scaffolding
Tests all project scaffolding options and wizard configurations
"""

import pytest
import tempfile
import json
import yaml
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the core directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear import (
    run_simple_protogear_init,
    setup_agent_framework_only,
    setup_full_project_scaffolding,
    run_seven_step_wizard,
    create_project_from_config,
    detect_project_structure,
    safe_input
)


class TestAgentFrameworkOnly:
    """Test Agent Framework Only mode"""

    def test_agent_framework_dry_run(self):
        """Test agent framework setup in dry run mode"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                Path(tmpdir).chmod(0o755)
                import os
                os.chdir(tmpdir)

                result = setup_agent_framework_only(dry_run=True)

                assert result['status'] == 'success'
                assert result['dry_run'] is True

            finally:
                os.chdir(original_dir)

    def test_agent_framework_file_creation(self):
        """Test actual file creation in agent framework mode"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                result = setup_agent_framework_only(dry_run=False)

                assert result['status'] == 'success'
                assert 'files_created' in result
                assert 'AGENTS.md' in result['files_created']
                assert 'PROJECT_STATUS.md' in result['files_created']

                # Verify files exist
                assert Path('AGENTS.md').exists()
                assert Path('PROJECT_STATUS.md').exists()

                # Verify content
                agents_content = Path('AGENTS.md').read_text()
                assert 'ProtoGear Agent Framework Integration' in agents_content
                assert 'Framework Activation' in agents_content

                status_content = Path('PROJECT_STATUS.md').read_text()
                assert 'Single Source of Truth' in status_content
                assert 'protogear_enabled: true' in status_content

            finally:
                os.chdir(original_dir)

    def test_project_structure_detection_nodejs(self):
        """Test detection of Node.js projects"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create package.json for Node.js project
            package_json = {
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "react": "^18.0.0",
                    "next": "^13.0.0"
                }
            }
            (tmpdir_path / "package.json").write_text(json.dumps(package_json, indent=2))

            info = detect_project_structure(tmpdir_path)

            assert info['detected'] is True
            assert info['type'] == 'Node.js Project'
            assert info['framework'] == 'Next.js'

    def test_project_structure_detection_python(self):
        """Test detection of Python projects"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)

            # Create Python files
            (tmpdir_path / "main.py").write_text("print('hello')")
            (tmpdir_path / "requirements.txt").write_text("django>=3.0.0")
            (tmpdir_path / "manage.py").write_text("# Django management")

            info = detect_project_structure(tmpdir_path)

            assert info['detected'] is True
            assert info['type'] == 'Python Project'
            assert info['framework'] == 'Django'


class TestSevenStepWizard:
    """Test the 7-step project scaffolding wizard"""

    def test_config_generation_web_app(self):
        """Test configuration generation for web app"""
        # Mock inputs for a web application
        test_inputs = [
            "test-webapp",     # Project name
            "1",               # Web Application
            "",                # Description (empty)
            "1",               # Next.js
            "1",               # Tailwind CSS
            "1",               # npm
            "1",               # Vitest
            "1,2",             # TypeScript, ESLint + Prettier
            "1",               # Vercel
            "2",               # Standard agent config
            "Y"                # Confirm
        ]

        with patch('core.proto_gear.safe_input', side_effect=test_inputs):
            config = {}

            # Simulate running through the wizard steps
            config['name'] = "test-webapp"
            config['project_type'] = 'web-app'
            config['description'] = "A web-app project created with ProtoGear"
            config['frontend_framework'] = 'nextjs'
            config['css_framework'] = 'tailwind'
            config['backend_framework'] = 'none'
            config['database'] = 'none'
            config['orm'] = 'none'
            config['package_manager'] = 'npm'
            config['testing_framework'] = 'vitest'
            config['features'] = ['typescript', 'linting']
            config['deployment'] = 'vercel'
            config['agent_config'] = 'standard'

            # Test project creation in dry run mode
            result = create_project_from_config(config, dry_run=True)

            assert result['status'] == 'success'
            assert result['dry_run'] is True
            assert result['config']['name'] == 'test-webapp'
            assert result['config']['frontend_framework'] == 'nextjs'
            assert 'typescript' in result['config']['features']

    def test_config_generation_fullstack(self):
        """Test configuration generation for fullstack app"""
        config = {
            'name': 'test-fullstack',
            'project_type': 'fullstack',
            'description': 'A fullstack project',
            'frontend_framework': 'nextjs',
            'css_framework': 'tailwind',
            'backend_framework': 'express',
            'database': 'postgresql',
            'orm': 'prisma',
            'package_manager': 'pnpm',
            'testing_framework': 'jest',
            'features': ['typescript', 'linting', 'docker'],
            'deployment': 'vercel',
            'agent_config': 'complete'
        }

        result = create_project_from_config(config, dry_run=True)

        assert result['status'] == 'success'
        assert result['config']['backend_framework'] == 'express'
        assert result['config']['database'] == 'postgresql'
        assert 'docker' in result['config']['features']

    def test_actual_project_creation(self):
        """Test actual project file creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'test-creation',
                    'project_type': 'web-app',
                    'description': 'Test project for creation',
                    'frontend_framework': 'react',
                    'css_framework': 'tailwind',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'vitest',
                    'features': ['typescript'],
                    'deployment': 'netlify',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'
                assert 'path' in result

                project_path = Path(result['path'])
                assert project_path.exists()
                assert (project_path / 'package.json').exists()
                assert (project_path / 'README.md').exists()
                assert (project_path / 'AGENTS.md').exists()
                assert (project_path / 'PROJECT_STATUS.md').exists()
                assert (project_path / 'src').exists()
                assert (project_path / 'tests').exists()
                assert (project_path / 'docs').exists()

                # Check TypeScript config since it's in features
                assert (project_path / 'tsconfig.json').exists()

                # Verify package.json content
                package_content = json.loads((project_path / 'package.json').read_text())
                assert package_content['name'] == 'test-creation'
                assert package_content['description'] == 'Test project for creation'

                # Verify AGENTS.md content
                agents_content = (project_path / 'AGENTS.md').read_text()
                assert 'test-creation' in agents_content
                assert 'web-app' in agents_content
                assert 'react' in agents_content

            finally:
                os.chdir(original_dir)


class TestWizardTypes:
    """Test different wizard types and their imports"""

    def test_all_wizard_imports(self):
        """Test that all wizard modules can be imported"""
        try:
            from setup_wizard import SetupWizard
            from enhanced_setup_wizard import EnhancedSetupWizard
            from ultimate_setup_wizard import UltimateSetupWizard
            from multiplatform_wizard import MultiPlatformSetupWizard
            from agent_framework_wizard import AgentFrameworkWizard
            from grouped_setup_wizard import GroupedSetupWizard
            from main_setup_wizard import ProtoGearWizard

            # Test that classes can be instantiated
            basic_wizard = SetupWizard()
            enhanced_wizard = EnhancedSetupWizard()

            assert basic_wizard is not None
            assert enhanced_wizard is not None

        except ImportError as e:
            pytest.fail(f"Failed to import wizard modules: {e}")

    def test_wizard_enums_and_constants(self):
        """Test that wizard enums and constants are accessible"""
        from enhanced_setup_wizard import (
            ProjectType, Framework, UIFramework, CSSFramework,
            PackageManager, TestFramework, CMSOption, DeploymentTarget
        )
        from ultimate_setup_wizard import AuthProvider, AnalyticsProvider

        # Test enum values
        assert ProjectType.WEB_APP.value == "web-app"
        assert Framework.NEXTJS.value == "nextjs"
        assert UIFramework.REACT.value == "react"
        assert CSSFramework.TAILWIND.value == "tailwind"
        assert PackageManager.NPM.value == "npm"
        assert TestFramework.VITEST.value == "vitest"
        assert AuthProvider.NEXTAUTH.value == "nextauth"
        assert AnalyticsProvider.PLAUSIBLE.value == "plausible"


class TestCommandLineInterface:
    """Test the CLI interface with various inputs"""

    def test_cli_agent_framework_only(self):
        """Test CLI with agent framework only option"""
        # Test with subprocess to ensure real CLI behavior
        cmd = ["python", "core/proto_gear.py", "init", "--dry-run"]
        input_data = "1\n"  # Choose agent framework only

        result = subprocess.run(
            cmd,
            input=input_data,
            text=True,
            capture_output=True,
            cwd=Path(__file__).parent.parent
        )

        assert result.returncode == 0
        assert "Agent Framework Setup" in result.stdout
        assert "AGENTS.md" in result.stdout
        assert "PROJECT_STATUS.md" in result.stdout

    def test_cli_full_project_scaffolding(self):
        """Test CLI with full project scaffolding"""
        cmd = ["python", "core/proto_gear.py", "init", "--dry-run"]
        # Provide inputs for all wizard steps
        input_data = "2\ntest-cli-project\n1\n\n1\n1\n1\n1\n1,2\n1\n2\nY\n"

        result = subprocess.run(
            cmd,
            input=input_data,
            text=True,
            capture_output=True,
            cwd=Path(__file__).parent.parent,
            timeout=30
        )

        assert result.returncode == 0
        assert "7-Step Project Setup Wizard" in result.stdout
        assert "Configuration Summary" in result.stdout
        assert "test-cli-project" in result.stdout

    def test_safe_input_function(self):
        """Test the safe_input helper function"""
        # Test normal input
        with patch('builtins.input', return_value='test'):
            result = safe_input("Test prompt: ", "default")
            assert result == 'test'

        # Test EOF handling
        with patch('builtins.input', side_effect=EOFError):
            result = safe_input("Test prompt: ", "default")
            assert result == 'default'

        # Test KeyboardInterrupt handling
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                safe_input("Test prompt: ", "default")


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""

    def test_complete_nextjs_project_workflow(self):
        """Test complete Next.js project creation workflow"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Configuration for a typical Next.js project
                config = {
                    'name': 'nextjs-integration-test',
                    'project_type': 'fullstack',
                    'description': 'Next.js integration test project',
                    'frontend_framework': 'nextjs',
                    'css_framework': 'tailwind',
                    'backend_framework': 'nextjs-api',
                    'database': 'postgresql',
                    'orm': 'prisma',
                    'package_manager': 'pnpm',
                    'testing_framework': 'playwright',
                    'features': ['typescript', 'linting', 'git-hooks', 'i18n'],
                    'deployment': 'vercel',
                    'agent_config': 'complete'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'

                project_path = Path(result['path'])

                # Verify all expected files and directories
                expected_files = [
                    'package.json',
                    'README.md',
                    'AGENTS.md',
                    'PROJECT_STATUS.md',
                    'tsconfig.json'
                ]

                expected_dirs = ['src', 'tests', 'docs']

                for file in expected_files:
                    assert (project_path / file).exists(), f"Missing file: {file}"

                for dir in expected_dirs:
                    assert (project_path / dir).exists(), f"Missing directory: {dir}"

                # Verify content quality
                package_json = json.loads((project_path / 'package.json').read_text())
                assert package_json['name'] == 'nextjs-integration-test'
                assert 'protogear' in package_json['keywords']

                agents_md = (project_path / 'AGENTS.md').read_text()
                assert 'Complete Agent Ecosystem' in agents_md
                assert 'nextjs' in agents_md.lower()
                assert 'postgresql' in agents_md.lower()

                status_md = (project_path / 'PROJECT_STATUS.md').read_text()
                assert 'nextjs-api' in status_md
                assert 'postgresql' in status_md
                assert 'complete' in status_md

            finally:
                os.chdir(original_dir)

    def test_existing_project_agent_integration(self):
        """Test adding agent framework to existing project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Create a fake existing project
                (Path(tmpdir) / 'index.js').write_text('console.log("existing project");')
                package_json = {
                    "name": "existing-project",
                    "version": "1.0.0",
                    "dependencies": {"express": "^4.18.0"}
                }
                (Path(tmpdir) / 'package.json').write_text(json.dumps(package_json))

                # Add agent framework
                result = setup_agent_framework_only(dry_run=False)

                assert result['status'] == 'success'

                # Verify agent files were created
                assert Path('AGENTS.md').exists()
                assert Path('PROJECT_STATUS.md').exists()

                # Verify original files still exist
                assert Path('index.js').exists()
                assert Path('package.json').exists()

                # Verify agent integration detected the project
                agents_content = Path('AGENTS.md').read_text()
                assert 'Node.js Project' in agents_content

            finally:
                os.chdir(original_dir)

    def test_error_handling_invalid_project_name(self):
        """Test error handling for invalid project names"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Create a directory that already exists
                existing_dir = Path(tmpdir) / 'existing-project'
                existing_dir.mkdir()

                config = {
                    'name': 'existing-project',  # This directory already exists
                    'project_type': 'web-app',
                    'description': 'Test project',
                    'frontend_framework': 'react',
                    'css_framework': 'tailwind',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'vitest',
                    'features': [],
                    'deployment': 'netlify',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'error'
                assert 'already exists' in result['error']

            finally:
                os.chdir(original_dir)


if __name__ == '__main__':
    # Allow running tests directly
    pytest.main([__file__, '-v'])