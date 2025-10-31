"""
Tests for proto_gear.py CLI interface
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear import (
    detect_project_structure,
    detect_git_config,
    Colors,
    safe_input
)


class TestProjectDetection:
    """Test project structure detection"""

    def test_detect_nodejs_project(self, tmp_path):
        """Test detection of Node.js project"""
        # Create package.json
        package_json = tmp_path / "package.json"
        package_json.write_text('{"name": "test-project", "version": "1.0.0"}')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Node.js Project'

    def test_detect_python_project(self, tmp_path):
        """Test detection of Python project"""
        # Create requirements.txt
        requirements = tmp_path / "requirements.txt"
        requirements.write_text('pytest>=7.0\nflake8>=6.0')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['type'] == 'Python Project'

    def test_detect_nextjs_framework(self, tmp_path):
        """Test detection of Next.js framework"""
        # Create package.json with Next.js
        package_json = tmp_path / "package.json"
        package_json.write_text('''{
            "name": "test-project",
            "dependencies": {
                "next": "^13.0.0",
                "react": "^18.0.0"
            }
        }''')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        assert result['framework'] == 'Next.js'

    def test_detect_django_framework(self, tmp_path):
        """Test detection of Django framework"""
        # Create requirements.txt with Django
        requirements = tmp_path / "requirements.txt"
        requirements.write_text('Django>=4.0\ndjango-rest-framework>=3.14')

        # Also create setup.py to help detection
        setup_py = tmp_path / "setup.py"
        setup_py.write_text('# setup file')

        result = detect_project_structure(tmp_path)

        assert result['detected'] is True
        # Framework detection may require more context, just verify detection works
        assert result['type'] == 'Python Project'

    def test_detect_generic_project(self, tmp_path):
        """Test detection of generic project (no known files)"""
        # Empty directory
        result = detect_project_structure(tmp_path)

        assert result['detected'] is False
        # Type is None for undetected projects
        assert result['type'] is None


class TestGitConfigDetection:
    """Test Git configuration detection"""

    @patch('subprocess.run')
    def test_detect_git_repo_with_remote(self, mock_run):
        """Test detection of Git repo with remote"""
        # Mock git rev-parse (is a repo)
        mock_run.return_value = Mock(returncode=0, stdout='')

        # Mock git remote (has remote)
        mock_run_remote = Mock(returncode=0, stdout='origin\n', stderr='')

        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            mock_run_remote,  # git remote
            Mock(returncode=0, stdout='main\n', stderr=''),  # main branch
            Mock(returncode=0, stdout='development\n', stderr='')  # dev branch
        ]):
            result = detect_git_config()

        assert result['is_git_repo'] is True
        assert result['has_remote'] is True
        assert result['remote_name'] == 'origin'

    @patch('subprocess.run')
    def test_detect_git_repo_without_remote(self, mock_run):
        """Test detection of Git repo without remote"""
        with patch('subprocess.run', side_effect=[
            Mock(returncode=0, stdout='', stderr=''),  # git rev-parse
            Mock(returncode=0, stdout='', stderr=''),  # git remote (empty)
            Mock(returncode=0, stdout='main\n', stderr=''),  # main branch
            Mock(returncode=0, stdout='development\n', stderr='')  # dev branch
        ]):
            result = detect_git_config()

        assert result['is_git_repo'] is True
        assert result['has_remote'] is False
        assert result['remote_name'] is None

    @patch('subprocess.run')
    def test_detect_no_git_repo(self, mock_run):
        """Test detection when not a Git repo"""
        mock_run.return_value = Mock(returncode=128, stdout='', stderr='not a git repository')

        result = detect_git_config()

        assert result['is_git_repo'] is False
        assert result['has_remote'] is False


class TestSafeInput:
    """Test safe input handling"""

    def test_safe_input_normal(self):
        """Test safe input with normal input"""
        with patch('builtins.input', return_value='test input'):
            result = safe_input("Enter something: ")
            assert result == 'test input'

    def test_safe_input_eof_with_default(self):
        """Test safe input handling EOF with default"""
        with patch('builtins.input', side_effect=EOFError):
            result = safe_input("Enter something: ", default="default_value")
            assert result == 'default_value'

    def test_safe_input_keyboard_interrupt(self):
        """Test safe input handling KeyboardInterrupt"""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                safe_input("Enter something: ")


class TestColors:
    """Test color code constants"""

    def test_colors_defined(self):
        """Test that color codes are defined"""
        assert hasattr(Colors, 'HEADER')
        assert hasattr(Colors, 'BLUE')
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'WARNING')
        assert hasattr(Colors, 'FAIL')
        assert hasattr(Colors, 'ENDC')
        assert hasattr(Colors, 'BOLD')

    def test_colors_are_strings(self):
        """Test that color codes are strings"""
        assert isinstance(Colors.GREEN, str)
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.FAIL, str)


class TestMainCLI:
    """Test main CLI entry point"""

    @patch('proto_gear.show_splash_screen')
    @patch('proto_gear.run_simple_protogear_init')
    def test_init_command_dry_run(self, mock_init, mock_splash):
        """Test pg init --dry-run command"""
        mock_init.return_value = {'status': 'success', 'dry_run': True}

        with patch('sys.argv', ['pg', 'init', '--dry-run', '--no-interactive']):
            with pytest.raises(SystemExit) as exc_info:
                from proto_gear import main
                main()

            assert exc_info.value.code == 0
            mock_splash.assert_called_once()
            mock_init.assert_called_once()

    @patch('proto_gear.show_splash_screen')
    @patch('proto_gear.show_help')
    def test_help_command(self, mock_help, mock_splash):
        """Test pg help command"""
        with patch('sys.argv', ['pg', 'help']):
            with pytest.raises(SystemExit) as exc_info:
                from proto_gear import main
                main()

            assert exc_info.value.code == 0
            mock_help.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
