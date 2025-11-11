"""
Tests for ui_helper.py UI utility functions
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, call

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from proto_gear_pkg.ui_helper import UIHelper, Colors


class TestUIHelper:
    """Test UIHelper class"""

    def test_uihelper_initialization(self):
        """Test UIHelper can be initialized"""
        ui = UIHelper()
        assert ui is not None

    @patch('builtins.print')
    def test_success_message(self, mock_print):
        """Test success message printing"""
        ui = UIHelper()
        ui.success("Test success message")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_error_message(self, mock_print):
        """Test error message printing"""
        ui = UIHelper()
        ui.error("Test error message")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_warning_message(self, mock_print):
        """Test warning message printing"""
        ui = UIHelper()
        ui.warning("Test warning message")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_info_message(self, mock_print):
        """Test info message printing"""
        ui = UIHelper()
        ui.info("Test info message")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_header_message(self, mock_print):
        """Test header message printing"""
        ui = UIHelper()
        ui.header("Test Header")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_section_message(self, mock_print):
        """Test section message printing"""
        ui = UIHelper()
        ui.section("Test Section")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_step_message(self, mock_print):
        """Test step message printing"""
        ui = UIHelper()
        ui.step(1, "First step")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_list_item(self, mock_print):
        """Test list item printing"""
        ui = UIHelper()
        ui.list_item("List item text")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_gray_message(self, mock_print):
        """Test gray/dim message"""
        ui = UIHelper()
        ui.gray("Gray text")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_separator(self, mock_print):
        """Test separator printing"""
        ui = UIHelper()
        ui.separator()
        mock_print.assert_called()

    @patch('builtins.print')
    def test_blank_line(self, mock_print):
        """Test blank line printing"""
        ui = UIHelper()
        ui.blank_line()
        mock_print.assert_called_once_with()

    @patch('builtins.print')
    def test_farewell(self, mock_print):
        """Test farewell message"""
        ui = UIHelper()
        ui.farewell()
        mock_print.assert_called()

    @patch('builtins.print')
    def test_farewell_custom(self, mock_print):
        """Test farewell with custom message"""
        ui = UIHelper()
        ui.farewell("Custom goodbye")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_welcome(self, mock_print):
        """Test welcome message"""
        ui = UIHelper()
        ui.welcome("Welcome!", "Subtitle text")
        assert mock_print.call_count >= 2

    @patch('builtins.print')
    def test_command(self, mock_print):
        """Test command printing"""
        ui = UIHelper()
        ui.command("pg init", "Initialize project")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_file_created(self, mock_print):
        """Test file created message"""
        ui = UIHelper()
        ui.file_created("test.md")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_file_skipped(self, mock_print):
        """Test file skipped message"""
        ui = UIHelper()
        ui.file_skipped("test.md", "not needed")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_prompt(self, mock_print):
        """Test prompt message"""
        ui = UIHelper()
        ui.prompt("Enter value:")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_example(self, mock_print):
        """Test example text"""
        ui = UIHelper()
        ui.example("Example: pg init")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_next_steps_header(self, mock_print):
        """Test next steps header"""
        ui = UIHelper()
        ui.next_steps_header()
        mock_print.assert_called()

    @patch('builtins.print')
    def test_centered(self, mock_print):
        """Test centered text"""
        ui = UIHelper()
        ui.centered("Centered text")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_box_header(self, mock_print):
        """Test box header"""
        ui = UIHelper()
        ui.box_header("Test Header")
        assert mock_print.call_count >= 2  # Header + separator

    @patch('builtins.print')
    def test_validation_error(self, mock_print):
        """Test validation error"""
        ui = UIHelper()
        ui.validation_error("Invalid input")
        mock_print.assert_called()

    @patch('builtins.print')
    def test_section_with_content(self, mock_print):
        """Test section with content"""
        ui = UIHelper()
        items = ["Item 1", "Item 2"]
        ui.section_with_content("Test Section", items)
        assert mock_print.call_count >= len(items)

    @patch('builtins.print')
    def test_config_summary(self, mock_print):
        """Test config summary"""
        ui = UIHelper()
        config = {"key1": "value1", "key2": "value2"}
        ui.config_summary("Configuration", config)
        assert mock_print.call_count >= len(config)


class TestColors:
    """Test Colors class constants"""

    def test_all_colors_exist(self):
        """Test that all expected colors are defined"""
        expected_colors = [
            'HEADER', 'BLUE', 'CYAN', 'GREEN', 'YELLOW',
            'WARNING', 'FAIL', 'ENDC', 'BOLD',
            'UNDERLINE', 'GRAY', 'MAGENTA'
        ]

        for color in expected_colors:
            assert hasattr(Colors, color), f"Color {color} not found"

    def test_colors_are_ansi_strings(self):
        """Test that colors are ANSI escape sequences (strings)"""
        assert isinstance(Colors.GREEN, str)
        assert isinstance(Colors.FAIL, str)  # This is the "red" color
        assert isinstance(Colors.CYAN, str)
        assert isinstance(Colors.BOLD, str)
        assert isinstance(Colors.ENDC, str)

    def test_ansi_reset_exists(self):
        """Test that ANSI reset code exists"""
        assert hasattr(Colors, 'ENDC')
        assert Colors.ENDC is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
