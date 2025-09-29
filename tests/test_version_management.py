"""
Tests for ProtoGear Version Management System
Tests dependency version resolution, compatibility, and generation
"""

import pytest
import tempfile
import json
import sys
from pathlib import Path
from unittest.mock import patch

# Add the core directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from version_config import (
    VersionManager, FrameworkVersions, VersionStrategy,
    create_package_json_with_versions
)
from proto_gear import create_project_from_config


class TestFrameworkVersions:
    """Test framework version configurations"""

    def test_framework_versions_structure(self):
        """Test that framework versions are properly structured"""
        versions = FrameworkVersions()

        # Test that all required frameworks are present
        assert 'nextjs' in versions.FRONTEND_FRAMEWORKS
        assert 'react' in versions.FRONTEND_FRAMEWORKS
        assert 'vue' in versions.FRONTEND_FRAMEWORKS
        assert 'sveltekit' in versions.FRONTEND_FRAMEWORKS

        # Test that Next.js has required dependencies
        nextjs_deps = versions.FRONTEND_FRAMEWORKS['nextjs']
        assert 'next' in nextjs_deps
        assert 'react' in nextjs_deps
        assert 'react-dom' in nextjs_deps

        # Test version format (should be semantic versions with range)
        assert nextjs_deps['next'].startswith('^') or nextjs_deps['next'].startswith('~')
        assert '.' in nextjs_deps['next']  # Contains dot for semantic version

    def test_css_framework_versions(self):
        """Test CSS framework version configurations"""
        versions = FrameworkVersions()

        # Test Tailwind CSS dependencies
        tailwind_deps = versions.CSS_FRAMEWORKS['tailwind']
        assert 'tailwindcss' in tailwind_deps
        assert 'autoprefixer' in tailwind_deps
        assert 'postcss' in tailwind_deps

        # Test Material-UI dependencies
        mui_deps = versions.CSS_FRAMEWORKS['mui']
        assert '@mui/material' in mui_deps
        assert '@emotion/react' in mui_deps

    def test_backend_framework_versions(self):
        """Test backend framework version configurations"""
        versions = FrameworkVersions()

        # Test Express.js dependencies
        express_deps = versions.BACKEND_FRAMEWORKS['express']
        assert 'express' in express_deps
        assert '@types/express' in express_deps
        assert 'cors' in express_deps

        # Test FastAPI dependencies (Python)
        fastapi_deps = versions.BACKEND_FRAMEWORKS['fastapi']
        assert 'fastapi' in fastapi_deps
        assert 'uvicorn' in fastapi_deps
        assert '>=' in fastapi_deps['fastapi']  # Python uses >= syntax

    def test_testing_framework_versions(self):
        """Test testing framework version configurations"""
        versions = FrameworkVersions()

        # Test Vitest dependencies
        vitest_deps = versions.TESTING_FRAMEWORKS['vitest']
        assert 'vitest' in vitest_deps
        assert '@vitest/ui' in vitest_deps

        # Test Jest dependencies
        jest_deps = versions.TESTING_FRAMEWORKS['jest']
        assert 'jest' in jest_deps
        assert '@types/jest' in jest_deps


class TestVersionManager:
    """Test version manager functionality"""

    def test_version_manager_initialization(self):
        """Test version manager initialization"""
        vm = VersionManager()
        assert vm.strategy == VersionStrategy.LATEST
        assert vm.versions is not None

        vm_exact = VersionManager(VersionStrategy.EXACT)
        assert vm_exact.strategy == VersionStrategy.EXACT

    def test_dependency_resolution_nextjs(self):
        """Test dependency resolution for Next.js project"""
        vm = VersionManager()
        config = {
            'name': 'test-nextjs',
            'frontend_framework': 'nextjs',
            'css_framework': 'tailwind',
            'features': ['typescript', 'linting'],
            'testing_framework': 'vitest'
        }

        deps = vm.get_dependencies_for_config(config)

        # Check that Next.js dependencies are included
        assert 'next' in deps['dependencies']
        assert 'react' in deps['dependencies']
        assert 'react-dom' in deps['dependencies']

        # Check that Tailwind dependencies are included
        assert 'tailwindcss' in deps['dependencies']
        assert 'autoprefixer' in deps['dependencies']

        # Check that TypeScript is in dev dependencies
        assert 'typescript' in deps['devDependencies']
        assert '@types/node' in deps['devDependencies']

        # Check that testing dependencies are included
        assert 'vitest' in deps['devDependencies']

    def test_dependency_resolution_react_vue(self):
        """Test dependency resolution for React and Vue projects"""
        vm = VersionManager()

        # React project
        react_config = {
            'frontend_framework': 'react',
            'css_framework': 'mui',
            'features': ['typescript'],
            'testing_framework': 'jest'
        }

        react_deps = vm.get_dependencies_for_config(react_config)
        assert 'react' in react_deps['dependencies']
        assert 'vite' in react_deps['dependencies']
        assert '@mui/material' in react_deps['dependencies']
        assert 'jest' in react_deps['devDependencies']

        # Vue project
        vue_config = {
            'frontend_framework': 'vue',
            'css_framework': 'bootstrap',
            'features': ['typescript'],
            'testing_framework': 'vitest'
        }

        vue_deps = vm.get_dependencies_for_config(vue_config)
        assert 'vue' in vue_deps['dependencies']
        assert 'bootstrap' in vue_deps['dependencies']
        assert 'vitest' in vue_deps['devDependencies']

    def test_fullstack_dependency_resolution(self):
        """Test dependency resolution for fullstack projects"""
        vm = VersionManager()
        config = {
            'frontend_framework': 'nextjs',
            'backend_framework': 'express',
            'database': 'postgresql',
            'orm': 'prisma',
            'features': ['typescript', 'auth'],
            'auth_provider': 'nextauth'
        }

        deps = vm.get_dependencies_for_config(config)

        # Frontend dependencies
        assert 'next' in deps['dependencies']
        assert 'react' in deps['dependencies']

        # Backend dependencies
        assert 'express' in deps['dependencies']
        assert '@types/express' in deps['dependencies']

        # Database dependencies
        assert 'pg' in deps['dependencies']
        assert '@types/pg' in deps['dependencies']

        # ORM dependencies
        assert 'prisma' in deps['dependencies']
        assert '@prisma/client' in deps['dependencies']

        # Auth dependencies
        assert 'next-auth' in deps['dependencies']

    def test_python_requirements_generation(self):
        """Test Python requirements.txt generation"""
        vm = VersionManager()

        # FastAPI project
        fastapi_config = {
            'backend_framework': 'fastapi',
            'testing_framework': 'pytest'
        }

        fastapi_reqs = vm.get_python_requirements(fastapi_config)
        assert any('fastapi>=' in req for req in fastapi_reqs)
        assert any('uvicorn>=' in req for req in fastapi_reqs)
        assert any('pytest>=' in req for req in fastapi_reqs)

        # Django project
        django_config = {
            'backend_framework': 'django',
            'testing_framework': 'pytest'
        }

        django_reqs = vm.get_python_requirements(django_config)
        assert any('Django>=' in req for req in django_reqs)
        assert any('djangorestframework>=' in req for req in django_reqs)

    def test_version_strategy_application(self):
        """Test different version strategies"""
        vm_exact = VersionManager(VersionStrategy.EXACT)
        vm_compatible = VersionManager(VersionStrategy.COMPATIBLE)
        vm_latest = VersionManager(VersionStrategy.LATEST)

        version = "^15.5.0"

        assert vm_exact.apply_version_strategy(version) == "15.5.0"
        assert vm_compatible.apply_version_strategy(version) == "~15.5.0"
        assert vm_latest.apply_version_strategy(version) == "^15.5.0"

    def test_package_manager_info(self):
        """Test package manager information retrieval"""
        vm = VersionManager()

        npm_info = vm.get_package_manager_info('npm')
        assert 'min_version' in npm_info
        assert 'recommended' in npm_info

        pnpm_info = vm.get_package_manager_info('pnpm')
        assert 'min_version' in pnpm_info
        assert 'recommended' in pnpm_info

    def test_compatibility_validation(self):
        """Test framework compatibility validation"""
        vm = VersionManager()

        config = {
            'frontend_framework': 'nextjs',
            'backend_framework': 'express'
        }

        warnings = vm.validate_compatibility(config)
        # Should return a list (empty or with warnings)
        assert isinstance(warnings, list)

    def test_version_lock_info_generation(self):
        """Test version lock information generation"""
        vm = VersionManager()

        config = {
            'frontend_framework': 'nextjs',
            'features': ['typescript']
        }

        lock_info = vm.generate_version_lock_info(config)

        assert 'protogear_version' in lock_info
        assert 'config_version' in lock_info
        assert 'strategy' in lock_info
        assert 'generated_at' in lock_info
        assert 'node_version_required' in lock_info


class TestPackageJsonGeneration:
    """Test package.json generation with versions"""

    def test_create_package_json_basic(self):
        """Test basic package.json creation"""
        config = {
            'name': 'test-basic',
            'description': 'Test basic project',
            'frontend_framework': 'react',
            'css_framework': 'tailwind',
            'features': ['typescript'],
            'testing_framework': 'vitest'
        }

        package_json = create_package_json_with_versions(config)

        assert package_json['name'] == 'test-basic'
        assert package_json['description'] == 'Test basic project'
        assert 'dependencies' in package_json
        assert 'devDependencies' in package_json
        assert 'scripts' in package_json

        # Check that React dependencies are present
        assert 'react' in package_json['dependencies']
        assert 'react-dom' in package_json['dependencies']

        # Check that scripts are appropriate for React
        assert 'dev' in package_json['scripts']
        assert 'vite' in package_json['scripts']['dev']

    def test_create_package_json_nextjs(self):
        """Test Next.js package.json creation"""
        config = {
            'name': 'test-nextjs',
            'description': 'Test Next.js project',
            'frontend_framework': 'nextjs',
            'css_framework': 'tailwind',
            'features': ['typescript', 'linting'],
            'testing_framework': 'jest'
        }

        package_json = create_package_json_with_versions(config)

        # Check Next.js specific dependencies
        assert 'next' in package_json['dependencies']
        assert 'eslint-config-next' in package_json['dependencies']

        # Check Next.js specific scripts
        assert package_json['scripts']['dev'] == 'next dev'
        assert package_json['scripts']['build'] == 'next build'
        assert package_json['scripts']['lint'] == 'next lint'

        # Check testing setup
        assert 'jest' in package_json['devDependencies']
        assert package_json['scripts']['test'] == 'jest'

    def test_create_package_json_vue(self):
        """Test Vue.js package.json creation"""
        config = {
            'name': 'test-vue',
            'description': 'Test Vue project',
            'frontend_framework': 'vue',
            'css_framework': 'bootstrap',
            'features': ['typescript'],
            'testing_framework': 'vitest'
        }

        package_json = create_package_json_with_versions(config)

        # Check Vue specific dependencies
        assert 'vue' in package_json['dependencies']
        assert 'vite' in package_json['dependencies']

        # Check Vue specific scripts
        assert 'vite' in package_json['scripts']['dev']

    def test_package_json_without_features(self):
        """Test package.json creation without optional features"""
        config = {
            'name': 'test-minimal',
            'description': 'Minimal project',
            'frontend_framework': 'react',
            'css_framework': 'none',
            'features': [],
            'testing_framework': 'none'
        }

        package_json = create_package_json_with_versions(config)

        # Should have basic React dependencies
        assert 'react' in package_json['dependencies']

        # Should not have TypeScript
        assert 'typescript' not in package_json.get('devDependencies', {})

        # Should not have testing framework
        assert 'vitest' not in package_json.get('devDependencies', {})
        assert 'jest' not in package_json.get('devDependencies', {})


class TestProjectCreationWithVersions:
    """Test complete project creation with version management"""

    def test_project_creation_with_versions(self):
        """Test that project creation includes proper versions"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'version-test-project',
                    'project_type': 'web-app',
                    'description': 'Test project with versions',
                    'frontend_framework': 'nextjs',
                    'css_framework': 'tailwind',
                    'backend_framework': 'none',
                    'database': 'none',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'vitest',
                    'features': ['typescript', 'linting'],
                    'deployment': 'vercel',
                    'agent_config': 'standard'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'

                project_path = Path(result['path'])
                package_json_path = project_path / 'package.json'

                assert package_json_path.exists()

                package_data = json.loads(package_json_path.read_text())

                # Verify dependencies have versions
                assert 'dependencies' in package_data
                assert 'devDependencies' in package_data

                # Check specific dependencies with versions
                deps = package_data['dependencies']
                assert 'next' in deps
                assert deps['next'].startswith('^')  # Should have caret range
                assert 'react' in deps
                assert deps['react'].startswith('^')

                # Check dev dependencies
                dev_deps = package_data['devDependencies']
                assert 'typescript' in dev_deps
                assert dev_deps['typescript'].startswith('^')

            finally:
                os.chdir(original_dir)

    def test_python_project_creation(self):
        """Test Python project creation with requirements.txt"""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = Path.cwd()
            try:
                import os
                os.chdir(tmpdir)

                config = {
                    'name': 'python-test-project',
                    'project_type': 'api',
                    'description': 'Test Python project',
                    'frontend_framework': 'none',
                    'css_framework': 'none',
                    'backend_framework': 'fastapi',
                    'database': 'postgresql',
                    'orm': 'none',
                    'package_manager': 'npm',
                    'testing_framework': 'pytest',
                    'features': [],
                    'deployment': 'docker',
                    'agent_config': 'basic'
                }

                result = create_project_from_config(config, dry_run=False)

                assert result['status'] == 'success'

                project_path = Path(result['path'])
                requirements_path = project_path / 'requirements.txt'

                assert requirements_path.exists()

                requirements_content = requirements_path.read_text()

                # Check that FastAPI dependencies are present
                assert 'fastapi>=' in requirements_content
                assert 'uvicorn>=' in requirements_content
                assert 'pytest>=' in requirements_content

            finally:
                os.chdir(original_dir)


class TestVersionConfigUpdates:
    """Test version configuration maintenance and updates"""

    def test_version_update_tracking(self):
        """Test that version updates are tracked"""
        vm = VersionManager()
        update_date = vm.get_version_update_date()

        # Should be a valid date string
        assert isinstance(update_date, str)
        assert len(update_date) == 10  # YYYY-MM-DD format
        assert '-' in update_date

    def test_framework_compatibility_matrix(self):
        """Test framework compatibility matrix"""
        vm = VersionManager()
        compatibility = vm.get_compatibility_matrix()

        assert isinstance(compatibility, dict)
        assert 'nextjs' in compatibility
        assert 'react' in compatibility['nextjs']

    def test_latest_versions_access(self):
        """Test access to latest version configurations"""
        from version_config import get_latest_versions

        versions = get_latest_versions()
        assert isinstance(versions, FrameworkVersions)
        assert hasattr(versions, 'FRONTEND_FRAMEWORKS')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])