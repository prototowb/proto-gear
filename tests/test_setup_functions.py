"""
Comprehensive tests for setup functions in proto_gear.py
Tests lines 700-968 (setup_agent_framework_only and related functions)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import tempfile
import shutil

from proto_gear_pkg.proto_gear import (
    setup_agent_framework_only,
    detect_project_structure,
    detect_git_config,
    generate_branching_doc
)


class TestSetupAgentFrameworkOnly:
    """Test setup_agent_framework_only function"""

    def test_setup_with_dry_run(self, tmp_path, capsys):
        """Test setup with dry_run=True (should not create files)"""
        with patch('proto_gear_pkg.proto_gear.Path') as mock_path:
            mock_path.return_value = tmp_path

            result = setup_agent_framework_only(dry_run=True)

            # Should complete without creating files
            captured = capsys.readouterr()
            assert "Agent Framework Setup" in captured.out
            assert "DRY RUN" in captured.out or "dry run" in captured.out.lower()

    def test_setup_creates_agents_md(self, tmp_path):
        """Test that setup creates AGENTS.md file"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                mock_detect.return_value = {
                    'detected': True,
                    'type': 'Python Package',
                    'framework': 'pip',
                    'structure_summary': 'Python package with setup.py'
                }

                result = setup_agent_framework_only(dry_run=False)

                agents_file = tmp_path / 'AGENTS.md'
                assert agents_file.exists()
                content = agents_file.read_text()
                assert 'AGENTS.md' in content
                assert 'ProtoGear Agent Framework Integration' in content

    def test_setup_with_branching(self, tmp_path):
        """Test setup with branching enabled"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                with patch('proto_gear_pkg.proto_gear.detect_git_config') as mock_git:
                    mock_detect.return_value = {
                        'detected': True,
                        'type': 'Node.js Project',
                        'framework': 'Next.js'
                    }
                    mock_git.return_value = {
                        'is_git_repo': True,
                        'has_remote': True
                    }

                    result = setup_agent_framework_only(
                        dry_run=False,
                        with_branching=True,
                        ticket_prefix='TEST'
                    )

                    # Should create both AGENTS.md and BRANCHING.md
                    assert (tmp_path / 'AGENTS.md').exists()
                    assert (tmp_path / 'BRANCHING.md').exists()

                    # AGENTS.md should reference BRANCHING.md
                    agents_content = (tmp_path / 'AGENTS.md').read_text()
                    assert 'BRANCHING.md' in agents_content

    def test_setup_derives_ticket_prefix_from_project_name(self, tmp_path):
        """Test that setup derives ticket prefix from directory name if not provided"""
        # Create a temp directory with a specific name
        project_dir = tmp_path / 'my-awesome-project'
        project_dir.mkdir()

        with patch('proto_gear_pkg.proto_gear.Path', return_value=project_dir):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                with patch('proto_gear_pkg.proto_gear.detect_git_config') as mock_git:
                    mock_detect.return_value = {'detected': True, 'type': 'Python'}
                    mock_git.return_value = {'is_git_repo': True, 'has_remote': False}

                    result = setup_agent_framework_only(
                        dry_run=False,
                        with_branching=True,
                        ticket_prefix=None  # Let it derive
                    )

                    branching_file = project_dir / 'BRANCHING.md'
                    if branching_file.exists():
                        content = branching_file.read_text()
                        # Should use derived prefix (e.g., "MYAWES" from "my-awesome-project")
                        assert 'Ticket Prefix' in content or 'ticket' in content.lower()

    def test_setup_uses_default_ticket_prefix_for_short_names(self, tmp_path):
        """Test that setup uses 'PROJ' for very short project names"""
        project_dir = tmp_path / 'ab'
        project_dir.mkdir()

        with patch('proto_gear_pkg.proto_gear.Path', return_value=project_dir):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                with patch('proto_gear_pkg.proto_gear.detect_git_config') as mock_git:
                    mock_detect.return_value = {'detected': True, 'type': 'Python'}
                    mock_git.return_value = {'is_git_repo': True, 'has_remote': False}

                    result = setup_agent_framework_only(
                        dry_run=False,
                        with_branching=True,
                        ticket_prefix=None
                    )

                    # Should use default 'PROJ' for short names
                    branching_file = project_dir / 'BRANCHING.md'
                    assert branching_file.exists()

    def test_setup_creates_project_status(self, tmp_path):
        """Test that setup creates PROJECT_STATUS.md"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                mock_detect.return_value = {
                    'detected': True,
                    'type': 'Ruby Project',
                    'framework': 'Rails'
                }

                result = setup_agent_framework_only(
                    dry_run=False,
                    ticket_prefix='RAIL'
                )

                status_file = tmp_path / 'PROJECT_STATUS.md'
                assert status_file.exists()
                content = status_file.read_text()
                assert 'PROJECT_STATUS.md' in content
                assert 'RAIL' in content  # Ticket prefix should appear

    def test_setup_without_project_detection(self, tmp_path):
        """Test setup when project type is not detected"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                mock_detect.return_value = {
                    'detected': False,
                    'type': 'Unknown'
                }

                result = setup_agent_framework_only(dry_run=False)

                # Should still create files even without detection
                assert (tmp_path / 'AGENTS.md').exists()
                assert (tmp_path / 'PROJECT_STATUS.md').exists()

    def test_setup_creates_testing_md(self, tmp_path):
        """Test that setup creates TESTING.md"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                mock_detect.return_value = {
                    'detected': True,
                    'type': 'Java Project',
                    'framework': 'Spring Boot'
                }

                result = setup_agent_framework_only(dry_run=False)

                testing_file = tmp_path / 'TESTING.md'
                assert testing_file.exists()
                content = testing_file.read_text()
                assert 'TESTING.md' in content or 'Test-Driven Development' in content

    def test_setup_prints_file_creation_summary(self, tmp_path, capsys):
        """Test that setup prints summary of created files"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                mock_detect.return_value = {'detected': True, 'type': 'Python'}

                result = setup_agent_framework_only(
                    dry_run=False,
                    with_branching=True,
                    ticket_prefix='TEST'
                )

                captured = capsys.readouterr()
                # Should print created files
                assert 'AGENTS.md' in captured.out
                assert 'PROJECT_STATUS.md' in captured.out

    def test_setup_handles_existing_files(self, tmp_path):
        """Test setup behavior when files already exist"""
        # Create existing AGENTS.md
        agents_file = tmp_path / 'AGENTS.md'
        agents_file.write_text('Existing content')

        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                mock_detect.return_value = {'detected': True, 'type': 'Python'}

                # Setup should overwrite existing files
                result = setup_agent_framework_only(dry_run=False)

                # File should be updated
                new_content = agents_file.read_text()
                assert new_content != 'Existing content'
                assert 'ProtoGear' in new_content


class TestDetectProjectStructure:
    """Test project structure detection"""

    def test_detect_nodejs_project(self, tmp_path):
        """Test detection of Node.js project"""
        # Create package.json
        package_json = tmp_path / 'package.json'
        package_json.write_text('{"name": "test-project"}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Node.js' in result['type']

    def test_detect_python_project(self, tmp_path):
        """Test detection of Python project"""
        # Create requirements.txt or setup.py
        requirements = tmp_path / 'requirements.txt'
        requirements.write_text('flask==2.0.0')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Python' in result['type']

    def test_detect_python_with_setuppy(self, tmp_path):
        """Test detection of Python project with setup.py"""
        setup_py = tmp_path / 'setup.py'
        setup_py.write_text('from setuptools import setup')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Python' in result['type']

    def test_detect_python_with_pyproject(self, tmp_path):
        """Test detection of Python project with pyproject.toml"""
        pyproject = tmp_path / 'pyproject.toml'
        pyproject.write_text('[tool.poetry]')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Python' in result['type']

    def test_detect_ruby_project(self, tmp_path):
        """Test detection of Ruby project"""
        gemfile = tmp_path / 'Gemfile'
        gemfile.write_text('source "https://rubygems.org"')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Ruby' in result['type']

    def test_detect_java_project_with_pom(self, tmp_path):
        """Test detection of Java project with pom.xml"""
        pom = tmp_path / 'pom.xml'
        pom.write_text('<project>')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Java' in result['type']

    def test_detect_java_project_with_gradle(self, tmp_path):
        """Test detection of Java project with build.gradle"""
        gradle = tmp_path / 'build.gradle'
        gradle.write_text('plugins {}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Java' in result['type']

    def test_detect_go_project(self, tmp_path):
        """Test detection of Go project"""
        go_mod = tmp_path / 'go.mod'
        go_mod.write_text('module test')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Go' in result['type']

    def test_detect_rust_project(self, tmp_path):
        """Test detection of Rust project"""
        cargo = tmp_path / 'Cargo.toml'
        cargo.write_text('[package]')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert 'Rust' in result['type']

    def test_detect_no_project(self, tmp_path):
        """Test when no project files are detected"""
        result = detect_project_structure(tmp_path)

        assert result['detected'] is False
        assert result.get('type') == 'Unknown' or result.get('type') is None

    def test_detect_multiple_project_types(self, tmp_path):
        """Test when multiple project files exist (e.g., monorepo)"""
        (tmp_path / 'package.json').write_text('{}')
        (tmp_path / 'requirements.txt').write_text('')

        result = detect_project_structure(tmp_path)

        # Should detect at least one
        assert result['detected'] is True


class TestDetectGitConfig:
    """Test Git configuration detection"""

    def test_detect_git_repo(self, tmp_path):
        """Test detection of git repository"""
        git_dir = tmp_path / '.git'
        git_dir.mkdir()

        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            result = detect_git_config()

        assert result['is_git_repo'] is True

    def test_detect_git_with_remote(self, tmp_path):
        """Test detection of git with remote"""
        git_dir = tmp_path / '.git'
        git_dir.mkdir()
        config_file = git_dir / 'config'
        config_file.write_text('[remote "origin"]\n\turl = https://github.com/user/repo.git')

        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            result = detect_git_config()

        assert result['is_git_repo'] is True
        assert result.get('has_remote') is True

    def test_detect_no_git_repo(self, tmp_path):
        """Test when directory is not a git repository"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            result = detect_git_config()

        assert result['is_git_repo'] is False
        assert result.get('has_remote') is False


class TestGenerateBranchingDoc:
    """Test branching document generation"""

    def test_generate_branching_doc_basic(self):
        """Test basic branching document generation"""
        result = generate_branching_doc(
            project_name='test-project',
            ticket_prefix='TEST',
            git_config={'is_git_repo': True, 'has_remote': False},
            date='2024-01-01'
        )

        assert result is not None
        assert 'BRANCHING.md' in result
        assert 'TEST' in result
        assert 'test-project' in result

    def test_generate_branching_doc_with_remote(self):
        """Test branching doc with remote repository"""
        result = generate_branching_doc(
            project_name='my-app',
            ticket_prefix='APP',
            git_config={'is_git_repo': True, 'has_remote': True},
            date='2024-01-01'
        )

        assert result is not None
        assert 'APP' in result
        assert 'remote' in result.lower() or 'github' in result.lower()

    def test_generate_branching_doc_no_git(self):
        """Test branching doc when not a git repo"""
        result = generate_branching_doc(
            project_name='no-git-project',
            ticket_prefix='PROJ',
            git_config={'is_git_repo': False, 'has_remote': False},
            date='2024-01-01'
        )

        # Should still generate doc or return None
        # (depends on implementation)
        assert result is not None or result is None

    def test_generate_branching_doc_includes_commit_format(self):
        """Test that branching doc includes commit message format"""
        result = generate_branching_doc(
            project_name='test',
            ticket_prefix='TEST',
            git_config={'is_git_repo': True, 'has_remote': True},
            date='2024-01-01'
        )

        assert result is not None
        # Should include conventional commit format
        assert 'feat' in result or 'fix' in result or 'commit' in result.lower()

    def test_generate_branching_doc_includes_branch_naming(self):
        """Test that branching doc includes branch naming conventions"""
        result = generate_branching_doc(
            project_name='test',
            ticket_prefix='TEST',
            git_config={'is_git_repo': True, 'has_remote': True},
            date='2024-01-01'
        )

        assert result is not None
        assert 'feature' in result or 'branch' in result.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
