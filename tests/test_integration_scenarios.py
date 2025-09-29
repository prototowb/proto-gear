"""
Integration Tests for Real-World Project Scaffolding Scenarios
Tests complete workflows with actual file generation and validation
"""

import pytest
import tempfile
import json
import yaml
import subprocess
import sys
import shutil
from pathlib import Path
from unittest.mock import patch

# Add the core directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear import (
    create_project_from_config,
    setup_agent_framework_only,
    detect_project_structure
)


class TestRealWorldScenarios:
    """Test real-world project scaffolding scenarios"""

    def test_startup_mvp_scenario(self):
        """Test rapid MVP creation scenario"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Startup MVP configuration
                config = {
                    'name': 'startup-mvp',
                    'project_type': 'web-app',
                    'description': 'Rapid MVP for startup validation',
                    'frontend_framework': 'nextjs',
                    'css_framework': 'tailwind',
                    'backend_framework': 'nextjs-api',
                    'database': 'supabase',
                    'orm': 'prisma',
                    'package_manager': 'pnpm',
                    'testing_framework': 'playwright',
                    'features': ['typescript', 'auth', 'analytics'],
                    'deployment': 'vercel',
                    'agent_config': 'standard'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'
                project_path = Path(result['path'])

                # Verify MVP-specific files
                self._verify_basic_structure(project_path)
                self._verify_nextjs_setup(project_path)
                self._verify_typescript_setup(project_path)
                self._verify_agent_integration(project_path, 'startup-mvp')

                # Verify package.json has MVP-appropriate scripts
                package_json = json.loads((project_path / 'package.json').read_text())
                assert 'dev' in package_json['scripts']
                assert 'build' in package_json['scripts']
                assert package_json['name'] == 'startup-mvp'

            finally:
                os.chdir(original_dir)

    def test_enterprise_application_scenario(self):
        """Test enterprise application creation scenario"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Enterprise application configuration
                config = {
                    'name': 'enterprise-app',
                    'project_type': 'fullstack',
                    'description': 'Enterprise-grade application with compliance',
                    'frontend_framework': 'nextjs',
                    'css_framework': 'tailwind',
                    'backend_framework': 'express',
                    'database': 'postgresql',
                    'orm': 'prisma',
                    'package_manager': 'pnpm',
                    'testing_framework': 'jest',
                    'features': ['typescript', 'linting', 'git-hooks', 'docker', 'i18n'],
                    'deployment': 'docker',
                    'agent_config': 'complete'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'
                project_path = Path(result['path'])

                # Verify enterprise-specific files
                self._verify_basic_structure(project_path)
                self._verify_typescript_setup(project_path)
                self._verify_docker_setup(project_path)
                self._verify_agent_integration(project_path, 'enterprise-app')

                # Verify comprehensive documentation
                readme_content = (project_path / 'README.md').read_text()
                assert 'enterprise-app' in readme_content
                assert 'fullstack' in readme_content
                assert 'express' in readme_content
                assert 'postgresql' in readme_content

            finally:
                os.chdir(original_dir)

    def test_open_source_library_scenario(self):
        """Test open source library creation scenario"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Library configuration
                config = {
                    'name': 'my-awesome-library',
                    'project_type': 'library',
                    'description': 'An awesome open source library',
                    'frontend_framework': 'none',
                    'css_framework': 'none',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'jest',
                    'features': ['typescript', 'linting'],
                    'deployment': 'npm',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'
                project_path = Path(result['path'])

                # Verify library-specific structure
                self._verify_basic_structure(project_path)
                self._verify_typescript_setup(project_path)

                # Library should have minimal setup
                package_json = json.loads((project_path / 'package.json').read_text())
                assert package_json['name'] == 'my-awesome-library'
                assert 'protogear' in package_json['keywords']

            finally:
                os.chdir(original_dir)

    def test_existing_project_migration_scenario(self):
        """Test migrating existing project to ProtoGear"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Create existing project structure
                self._create_existing_react_project(Path(tmpdir))

                # Add ProtoGear to existing project
                result = setup_agent_framework_only(dry_run=False)

                assert result['status'] == 'success'
                assert 'AGENTS.md' in result['files_created']
                assert 'PROJECT_STATUS.md' in result['files_created']

                # Verify original files still exist
                assert Path('src/App.js').exists()
                assert Path('package.json').exists()
                assert Path('public/index.html').exists()

                # Verify ProtoGear integration
                assert Path('AGENTS.md').exists()
                assert Path('PROJECT_STATUS.md').exists()

                # Verify project detection worked
                agents_content = Path('AGENTS.md').read_text()
                assert 'React' in agents_content

            finally:
                os.chdir(original_dir)

    def test_monorepo_setup_scenario(self):
        """Test monorepo project setup scenario"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Monorepo configuration
                config = {
                    'name': 'my-monorepo',
                    'project_type': 'fullstack',
                    'description': 'Monorepo with multiple packages',
                    'frontend_framework': 'nextjs',
                    'css_framework': 'tailwind',
                    'backend_framework': 'express',
                    'database': 'postgresql',
                    'orm': 'prisma',
                    'package_manager': 'pnpm',
                    'testing_framework': 'jest',
                    'features': ['typescript', 'linting', 'git-hooks'],
                    'deployment': 'docker',
                    'agent_config': 'complete'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'
                project_path = Path(result['path'])

                # Verify monorepo structure can be extended
                self._verify_basic_structure(project_path)

                # Create packages directory structure for monorepo
                packages_dir = project_path / 'packages'
                packages_dir.mkdir()

                (packages_dir / 'frontend').mkdir()
                (packages_dir / 'backend').mkdir()
                (packages_dir / 'shared').mkdir()

                # Verify structure is suitable for monorepo
                assert (packages_dir / 'frontend').exists()
                assert (packages_dir / 'backend').exists()
                assert (packages_dir / 'shared').exists()

            finally:
                os.chdir(original_dir)

    def _verify_basic_structure(self, project_path: Path):
        """Verify basic project structure"""
        required_files = ['package.json', 'README.md', 'AGENTS.md', 'PROJECT_STATUS.md']
        required_dirs = ['src', 'tests', 'docs']

        for file in required_files:
            assert (project_path / file).exists(), f"Missing required file: {file}"

        for dir in required_dirs:
            assert (project_path / dir).exists(), f"Missing required directory: {dir}"

    def _verify_nextjs_setup(self, project_path: Path):
        """Verify Next.js specific setup"""
        package_json = json.loads((project_path / 'package.json').read_text())

        # Next.js projects should have appropriate scripts
        assert 'dev' in package_json['scripts']
        assert 'build' in package_json['scripts']
        assert 'start' in package_json['scripts']

    def _verify_typescript_setup(self, project_path: Path):
        """Verify TypeScript configuration"""
        assert (project_path / 'tsconfig.json').exists()

        tsconfig = json.loads((project_path / 'tsconfig.json').read_text())
        assert 'compilerOptions' in tsconfig
        assert 'include' in tsconfig

    def _verify_docker_setup(self, project_path: Path):
        """Verify Docker configuration"""
        assert (project_path / 'Dockerfile').exists()

        dockerfile_content = (project_path / 'Dockerfile').read_text()
        assert 'FROM node:' in dockerfile_content
        assert 'WORKDIR' in dockerfile_content

    def _verify_agent_integration(self, project_path: Path, project_name: str):
        """Verify ProtoGear agent integration"""
        agents_md = (project_path / 'AGENTS.md').read_text()
        status_md = (project_path / 'PROJECT_STATUS.md').read_text()

        assert project_name in agents_md
        assert 'ProtoGear Agent Framework' in agents_md
        assert project_name in status_md
        assert 'protogear_enabled: true' in status_md

    def _create_existing_react_project(self, base_path: Path):
        """Create a mock existing React project"""
        # Create package.json
        package_json = {
            "name": "existing-react-app",
            "version": "0.1.0",
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        (base_path / 'package.json').write_text(json.dumps(package_json, indent=2))

        # Create src directory and files
        src_dir = base_path / 'src'
        src_dir.mkdir()

        (src_dir / 'App.js').write_text("""
import React from 'react';

function App() {
  return (
    <div className="App">
      <h1>Existing React App</h1>
    </div>
  );
}

export default App;
""")

        (src_dir / 'index.js').write_text("""
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
""")

        # Create public directory
        public_dir = base_path / 'public'
        public_dir.mkdir()

        (public_dir / 'index.html').write_text("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <title>Existing React App</title>
</head>
<body>
    <div id="root"></div>
</body>
</html>
""")


class TestFileGenerationValidation:
    """Test validation of generated files"""

    def test_package_json_validation(self):
        """Test that generated package.json files are valid"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'validation-test',
                    'project_type': 'web-app',
                    'description': 'Test project for validation',
                    'frontend_framework': 'react',
                    'css_framework': 'tailwind',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'jest',
                    'features': ['typescript'],
                    'deployment': 'netlify',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)
                project_path = Path(result['path'])

                # Validate package.json structure
                package_json_path = project_path / 'package.json'
                assert package_json_path.exists()

                package_data = json.loads(package_json_path.read_text())

                # Required fields
                assert 'name' in package_data
                assert 'version' in package_data
                assert 'description' in package_data
                assert 'scripts' in package_data

                # Validate values
                assert package_data['name'] == 'validation-test'
                assert package_data['description'] == 'Test project for validation'
                assert 'protogear' in package_data['keywords']

            finally:
                os.chdir(original_dir)

    def test_tsconfig_validation(self):
        """Test that generated tsconfig.json files are valid"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'ts-validation-test',
                    'project_type': 'web-app',
                    'description': 'TypeScript validation test',
                    'frontend_framework': 'react',
                    'css_framework': 'none',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'jest',
                    'features': ['typescript'],
                    'deployment': 'netlify',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)
                project_path = Path(result['path'])

                # Validate tsconfig.json
                tsconfig_path = project_path / 'tsconfig.json'
                assert tsconfig_path.exists()

                tsconfig_data = json.loads(tsconfig_path.read_text())

                # Required fields
                assert 'compilerOptions' in tsconfig_data
                assert 'include' in tsconfig_data
                assert 'exclude' in tsconfig_data

                # Validate compiler options
                compiler_options = tsconfig_data['compilerOptions']
                assert 'target' in compiler_options
                assert 'moduleResolution' in compiler_options
                assert 'strict' in compiler_options

            finally:
                os.chdir(original_dir)

    def test_agents_md_content_validation(self):
        """Test that AGENTS.md content is properly formatted"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'agents-validation-test',
                    'project_type': 'fullstack',
                    'description': 'Agents validation test',
                    'frontend_framework': 'nextjs',
                    'css_framework': 'tailwind',
                    'backend_framework': 'express',
                    'database': 'postgresql',
                    'orm': 'prisma',
                    'package_manager': 'pnpm',
                    'testing_framework': 'playwright',
                    'features': ['typescript', 'linting'],
                    'deployment': 'vercel',
                    'agent_config': 'complete'
                }

                result = create_project_from_config(config, dry_run=False)
                project_path = Path(result['path'])

                # Validate AGENTS.md content
                agents_path = project_path / 'AGENTS.md'
                assert agents_path.exists()

                agents_content = agents_path.read_text()

                # Check required sections
                assert '# AGENTS.md' in agents_content
                assert 'ProtoGear Agent Framework Integration' in agents_content
                assert 'Technology Stack' in agents_content
                assert 'Agent Configuration: Complete' in agents_content
                assert 'Development Workflow' in agents_content

                # Check technology details
                assert 'nextjs' in agents_content
                assert 'express' in agents_content
                assert 'postgresql' in agents_content
                assert 'pnpm' in agents_content

            finally:
                os.chdir(original_dir)

    def test_project_status_yaml_validation(self):
        """Test that PROJECT_STATUS.md YAML blocks are valid"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'status-validation-test',
                    'project_type': 'api',
                    'description': 'Status validation test',
                    'frontend_framework': 'none',
                    'css_framework': 'none',
                    'backend_framework': 'fastapi',
                    'database': 'postgresql',
                    'orm': 'raw',
                    'package_manager': 'npm',
                    'testing_framework': 'pytest',
                    'features': ['docker'],
                    'deployment': 'docker',
                    'agent_config': 'standard'
                }

                result = create_project_from_config(config, dry_run=False)
                project_path = Path(result['path'])

                # Validate PROJECT_STATUS.md YAML
                status_path = project_path / 'PROJECT_STATUS.md'
                assert status_path.exists()

                status_content = status_path.read_text()

                # Extract YAML block
                yaml_start = status_content.find('```yaml')
                yaml_end = status_content.find('```', yaml_start + 7)
                assert yaml_start != -1 and yaml_end != -1

                yaml_content = status_content[yaml_start + 7:yaml_end].strip()

                # Parse YAML to validate structure
                try:
                    yaml_data = yaml.safe_load(yaml_content)
                    assert isinstance(yaml_data, dict)
                    assert 'project_phase' in yaml_data
                    assert 'protogear_enabled' in yaml_data
                    assert yaml_data['protogear_enabled'] is True
                except yaml.YAMLError:
                    pytest.fail("Invalid YAML in PROJECT_STATUS.md")

            finally:
                os.chdir(original_dir)


class TestErrorScenarios:
    """Test error handling in various scenarios"""

    def test_directory_already_exists_error(self):
        """Test error when project directory already exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Create directory that will conflict
                existing_dir = Path('existing-project')
                existing_dir.mkdir()

                config = {
                    'name': 'existing-project',
                    'project_type': 'web-app',
                    'description': 'This should fail',
                    'frontend_framework': 'react',
                    'css_framework': 'tailwind',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'jest',
                    'features': [],
                    'deployment': 'netlify',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'error'
                assert 'already exists' in result['error']

            finally:
                os.chdir(original_dir)

    def test_permission_error_handling(self):
        """Test handling of permission errors"""
        # This test is OS-dependent and may not work on all systems
        if sys.platform == "win32":
            pytest.skip("Permission testing not reliable on Windows")

        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                # Create a read-only directory
                readonly_dir = Path('readonly')
                readonly_dir.mkdir()
                readonly_dir.chmod(0o444)

                try:
                    config = {
                        'name': 'readonly/test-project',
                        'project_type': 'web-app',
                        'description': 'Should fail due to permissions',
                        'frontend_framework': 'react',
                        'css_framework': 'none',
                        'backend_framework': 'none',
                        'database': 'none',
                        'orm': 'none',
                        'package_manager': 'npm',
                        'testing_framework': 'jest',
                        'features': [],
                        'deployment': 'netlify',
                        'agent_config': 'basic'
                    }

                    result = create_project_from_config(config, dry_run=False)

                    # Should handle permission error gracefully
                    assert result['status'] == 'error'

                finally:
                    # Restore permissions for cleanup
                    readonly_dir.chmod(0o755)

            finally:
                os.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])