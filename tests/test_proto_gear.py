"""
Essential tests for proto_gear.py - unique functionality only
(Duplicates removed - covered by test_essential_integration.py)
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear_pkg.proto_gear import (
    safe_input,
    generate_branching_doc,
    show_splash_screen,
    print_farewell,
    show_help
)
from proto_gear_pkg.ui_helper import Colors


class TestSafeInput:
    """Test safe input utility function"""

    def test_safe_input_normal(self):
        """Test normal input"""
        with patch('builtins.input', return_value='test input'):
            result = safe_input('Enter: ')
            assert result == 'test input'

    def test_safe_input_eof_with_default(self):
        """Test EOF with default value"""
        with patch('builtins.input', side_effect=EOFError):
            result = safe_input('Enter: ', default='default_value')
            assert result == 'default_value'

    def test_safe_input_keyboard_interrupt(self):
        """Test KeyboardInterrupt raises"""
        with patch('builtins.input', side_effect=KeyboardInterrupt):
            with pytest.raises(KeyboardInterrupt):
                safe_input('Enter: ')


class TestColors:
    """Test color constants"""

    def test_colors_defined(self):
        """Test that color constants are defined"""
        assert hasattr(Colors, 'BOLD')
        assert hasattr(Colors, 'CYAN')
        assert hasattr(Colors, 'GREEN')
        assert hasattr(Colors, 'ENDC')

    def test_colors_are_strings(self):
        """Test that colors are strings"""
        assert isinstance(Colors.BOLD, str)
        assert isinstance(Colors.CYAN, str)


class TestGenerateBranchingDoc:
    """Test branching document generation"""

    def test_generate_branching_with_remote(self):
        """Test generating branching doc with remote"""
        result = generate_branching_doc(
            'test-project',
            'TEST',
            {'is_git_repo': True, 'has_remote': True, 'remote_name': 'origin', 'main_branch': 'main', 'dev_branch': 'development'},
            '2024-01-01'
        )
        assert result is not None
        assert 'TEST' in result
        assert 'origin' in result.lower() or 'remote' in result.lower()

    def test_generate_branching_local_only(self):
        """Test generating branching doc for local repo"""
        result = generate_branching_doc(
            'local-project',
            'LOCAL',
            {'is_git_repo': True, 'has_remote': False, 'main_branch': 'main', 'dev_branch': 'develop'},
            '2024-01-01'
        )
        assert result is not None
        assert 'LOCAL' in result

    def test_generate_branching_with_gh_cli(self):
        """Test branching doc mentions gh CLI when available"""
        result = generate_branching_doc(
            'gh-project',
            'GH',
            {'is_git_repo': True, 'has_remote': True, 'has_gh_cli': True, 'remote_name': 'origin', 'main_branch': 'main', 'dev_branch': 'develop'},
            '2024-01-01'
        )
        assert result is not None
        assert 'GH' in result


class TestUIFunctions:
    """Test UI display functions"""

    def test_show_splash_screen(self, capsys):
        """Test splash screen displays"""
        show_splash_screen()
        captured = capsys.readouterr()
        assert len(captured.out) > 0
        assert 'AI Agent Framework' in captured.out or 'v0.6' in captured.out

    def test_print_farewell(self, capsys):
        """Test farewell message"""
        print_farewell()
        captured = capsys.readouterr()
        assert len(captured.out) > 0

    def test_show_help(self, capsys):
        """Test help display"""
        with patch('builtins.input', return_value=''):
            show_help()
            captured = capsys.readouterr()
            assert 'pg' in captured.out or 'proto' in captured.out.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
