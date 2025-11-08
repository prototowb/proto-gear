"""
Tests for interactive_wizard.py module
"""

import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

try:
    from interactive_wizard import (
        RichWizard,
        run_enhanced_wizard,
        QUESTIONARY_AVAILABLE,
        RICH_AVAILABLE
    )
    WIZARD_MODULE_AVAILABLE = True
except ImportError:
    WIZARD_MODULE_AVAILABLE = False
    pytest.skip("interactive_wizard module not available", allow_module_level=True)


class TestRichWizard:
    """Test RichWizard class"""

    def test_wizard_initialization(self):
        """Test wizard can be initialized"""
        wizard = RichWizard()
        assert wizard is not None
        assert hasattr(wizard, 'config')
        assert isinstance(wizard.config, dict)

    def test_wizard_has_console_if_rich_available(self):
        """Test wizard has console if rich is available"""
        wizard = RichWizard()
        if RICH_AVAILABLE:
            assert wizard.console is not None
        else:
            assert wizard.console is None

    def test_print_panel_fallback(self):
        """Test print_panel works without rich"""
        wizard = RichWizard()
        # Should not raise an error
        wizard.print_panel("Test content", title="Test Title")

    def test_create_project_info_panel(self):
        """Test creating project info panel"""
        wizard = RichWizard()
        project_info = {
            'detected': True,
            'type': 'Node.js Project',
            'framework': 'Next.js'
        }
        git_config = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin'
        }
        current_dir = Path('.')

        result = wizard.create_project_info_panel(project_info, git_config, current_dir)

        # Should return either a string or a Rich object
        assert result is not None


class TestAskBranchingStrategy:
    """Test branching strategy prompts"""

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.select')
    def test_ask_branching_strategy_yes(self, mock_select):
        """Test asking for branching strategy - user says yes"""
        mock_select.return_value.ask.return_value = True

        wizard = RichWizard()
        git_config = {'is_git_repo': True, 'has_remote': True}

        result = wizard.ask_branching_strategy(git_config)

        assert result is True
        mock_select.assert_called_once()

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.select')
    def test_ask_branching_strategy_no(self, mock_select):
        """Test asking for branching strategy - user says no"""
        mock_select.return_value.ask.return_value = False

        wizard = RichWizard()
        git_config = {'is_git_repo': False, 'has_remote': False}

        result = wizard.ask_branching_strategy(git_config)

        assert result is False

    def test_ask_branching_fallback_without_questionary(self):
        """Test branching strategy fallback without questionary"""
        wizard = RichWizard()
        git_config = {'is_git_repo': True, 'has_remote': False}

        # Mock input for fallback
        with patch('builtins.input', return_value='y'):
            if not QUESTIONARY_AVAILABLE:
                result = wizard.ask_branching_strategy(git_config)
                assert result is True


class TestAskTicketPrefix:
    """Test ticket prefix prompts"""

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.text')
    def test_ask_ticket_prefix_custom(self, mock_text):
        """Test asking for ticket prefix - custom input"""
        mock_text.return_value.ask.return_value = 'CUSTOM'

        wizard = RichWizard()
        result = wizard.ask_ticket_prefix('SUGGESTED')

        assert result == 'CUSTOM'

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.text')
    def test_ask_ticket_prefix_default(self, mock_text):
        """Test asking for ticket prefix - use default"""
        mock_text.return_value.ask.return_value = ''

        wizard = RichWizard()
        result = wizard.ask_ticket_prefix('DEFAULT')

        assert result == 'DEFAULT'

    def test_ask_ticket_prefix_fallback(self):
        """Test ticket prefix fallback without questionary"""
        wizard = RichWizard()

        with patch('builtins.input', return_value=''):
            if not QUESTIONARY_AVAILABLE:
                result = wizard.ask_ticket_prefix('FALLBACK')
                assert result == 'FALLBACK'


class TestShowConfigurationSummary:
    """Test configuration summary display"""

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.confirm')
    def test_show_summary_confirmed(self, mock_confirm):
        """Test showing summary - user confirms"""
        mock_confirm.return_value.ask.return_value = True

        wizard = RichWizard()
        config = {'with_branching': True, 'ticket_prefix': 'TEST'}
        project_info = {'type': 'Node.js Project', 'framework': 'Next.js'}
        current_dir = Path('.')

        result = wizard.show_configuration_summary(config, project_info, current_dir)

        assert result is True

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.confirm')
    def test_show_summary_declined(self, mock_confirm):
        """Test showing summary - user declines"""
        mock_confirm.return_value.ask.return_value = False

        wizard = RichWizard()
        config = {'with_branching': False, 'ticket_prefix': None}
        project_info = {'type': 'Python Project'}
        current_dir = Path('.')

        result = wizard.show_configuration_summary(config, project_info, current_dir)

        assert result is False


class TestRunEnhancedWizard:
    """Test the main wizard runner function"""

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.select')
    @patch('questionary.confirm')
    def test_run_wizard_complete_flow(self, mock_confirm, mock_select):
        """Test complete wizard flow"""
        # Mock responses
        mock_select.return_value.ask.return_value = True  # Yes to branching
        mock_confirm.return_value.ask.return_value = True  # Confirm setup

        project_info = {
            'detected': True,
            'type': 'Node.js Project',
            'framework': 'Next.js'
        }
        git_config = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin'
        }
        current_dir = Path('test-project')

        with patch('questionary.text') as mock_text:
            mock_text.return_value.ask.return_value = 'MYAPP'

            result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['confirmed'] is True
        assert result['with_branching'] is True
        assert result['ticket_prefix'] == 'MYAPP'

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    def test_run_wizard_keyboard_interrupt(self):
        """Test wizard handles keyboard interrupt"""
        project_info = {'detected': True, 'type': 'Node.js Project'}
        git_config = {'is_git_repo': True, 'has_remote': False}
        current_dir = Path('.')

        with patch('questionary.select') as mock_select:
            mock_select.return_value.ask.side_effect = KeyboardInterrupt()

            result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is None

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('questionary.select')
    @patch('questionary.confirm')
    def test_run_wizard_user_cancels(self, mock_confirm, mock_select):
        """Test wizard when user cancels at confirmation"""
        mock_select.return_value.ask.return_value = False  # No to branching
        mock_confirm.return_value.ask.return_value = False  # Don't confirm

        project_info = {'detected': False, 'type': 'Generic Project'}
        git_config = {'is_git_repo': False, 'has_remote': False}
        current_dir = Path('.')

        result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['confirmed'] is False
        assert result['with_branching'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
