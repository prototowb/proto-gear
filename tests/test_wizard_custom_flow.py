"""
Tests for custom wizard flow and granular selection
Tests the detailed wizard when user selects 'custom' preset
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from proto_gear_pkg.interactive_wizard import (
    RichWizard,
    run_enhanced_wizard,
    QUESTIONARY_AVAILABLE,
    RICH_AVAILABLE
)


class TestCustomWizardFlow:
    """Test custom preset wizard flow with granular selection"""

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_custom_wizard_complete_flow(self, mock_confirm, mock_checkbox, mock_select):
        """Test complete custom wizard flow"""
        # User selects custom preset
        mock_select.return_value.ask.side_effect = [
            'custom',  # Preset selection
            'Yes, add git workflow templates',  # Git workflow
            'All capabilities',  # Capabilities selection
        ]

        # Core templates selection
        mock_checkbox.return_value.ask.return_value = ['AGENTS', 'PROJECT_STATUS', 'TESTING']

        # Final confirmation
        mock_confirm.return_value.ask.side_effect = [
            True,  # Confirm configuration
        ]

        project_info = {
            'detected': True,
            'type': 'Python Package',
            'framework': 'pip'
        }
        git_config = {
            'is_git_repo': True,
            'has_remote': True
        }
        current_dir = Path('test-project')

        with patch('proto_gear_pkg.interactive_wizard.questionary.text') as mock_text:
            mock_text.return_value.ask.return_value = 'MYPROJ'

            result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['preset'] == 'custom'
        assert result['confirmed'] is True
        assert 'core_templates' in result

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    def test_custom_wizard_keyboard_interrupt_during_template_selection(self):
        """Test KeyboardInterrupt during template selection in custom flow"""
        with patch('proto_gear_pkg.interactive_wizard.questionary.select') as mock_select:
            mock_select.return_value.ask.return_value = 'custom'

            with patch('proto_gear_pkg.interactive_wizard.questionary.checkbox') as mock_checkbox:
                mock_checkbox.return_value.ask.side_effect = KeyboardInterrupt()

                project_info = {'detected': True, 'type': 'Node.js Project'}
                git_config = {'is_git_repo': True, 'has_remote': True}
                current_dir = Path('.')

                result = run_enhanced_wizard(project_info, git_config, current_dir)

                assert result is None


class TestWizardCoreTemplatesSelection:
    """Test core templates selection in custom wizard"""

    def test_wizard_has_ask_core_templates_method(self):
        """Test wizard has method for asking core templates"""
        wizard = RichWizard()
        assert hasattr(wizard, 'ask_core_templates_selection')

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    def test_ask_core_templates_all_selected(self, mock_checkbox):
        """Test selecting all core templates"""
        mock_checkbox.return_value.ask.return_value = [
            'AGENTS',
            'PROJECT_STATUS',
            'TESTING',
            'BRANCHING'
        ]

        wizard = RichWizard()
        result = wizard.ask_core_templates_selection()

        assert 'AGENTS' in result
        assert 'PROJECT_STATUS' in result
        assert 'TESTING' in result
        assert 'BRANCHING' in result

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    def test_ask_core_templates_minimal_selection(self, mock_checkbox):
        """Test selecting only required templates"""
        mock_checkbox.return_value.ask.return_value = ['AGENTS', 'PROJECT_STATUS']

        wizard = RichWizard()
        result = wizard.ask_core_templates_selection()

        assert len(result) == 2
        assert 'AGENTS' in result
        assert 'PROJECT_STATUS' in result


class TestWizardGitWorkflowOptions:
    """Test git workflow options in custom wizard"""

    def test_wizard_has_ask_git_workflow_method(self):
        """Test wizard has method for asking git workflow"""
        wizard = RichWizard()
        assert hasattr(wizard, 'ask_git_workflow_options')

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.text')
    def test_ask_git_workflow_yes_with_ticket_prefix(self, mock_text, mock_select):
        """Test git workflow - user says yes and provides ticket prefix"""
        mock_select.return_value.ask.return_value = 'Yes, add git workflow templates'
        mock_text.return_value.ask.return_value = 'PROJ'

        wizard = RichWizard()
        git_config = {'is_git_repo': True, 'has_remote': True}
        current_dir = Path('.')

        result = wizard.ask_git_workflow_options(git_config, current_dir)

        assert result['with_branching'] is True
        assert result['ticket_prefix'] == 'PROJ'

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_git_workflow_no(self, mock_select):
        """Test git workflow - user says no"""
        mock_select.return_value.ask.return_value = 'No, skip git workflow templates'

        wizard = RichWizard()
        git_config = {'is_git_repo': False, 'has_remote': False}
        current_dir = Path('.')

        result = wizard.ask_git_workflow_options(git_config, current_dir)

        assert result['with_branching'] is False
        assert result.get('ticket_prefix') is None


class TestWizardCapabilitiesSelection:
    """Test capabilities selection in custom wizard"""

    def test_wizard_has_ask_capabilities_method(self):
        """Test wizard has method for asking capabilities"""
        wizard = RichWizard()
        assert hasattr(wizard, 'ask_capabilities_selection')

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_capabilities_all(self, mock_select):
        """Test selecting all capabilities"""
        mock_select.return_value.ask.return_value = 'All capabilities'

        wizard = RichWizard()
        result = wizard.ask_capabilities_selection()

        assert result['enabled'] is True
        assert result['mode'] == 'all'

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_capabilities_none(self, mock_select):
        """Test selecting no capabilities"""
        mock_select.return_value.ask.return_value = 'No capabilities'

        wizard = RichWizard()
        result = wizard.ask_capabilities_selection()

        assert result['enabled'] is False

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    def test_ask_capabilities_by_category(self, mock_checkbox, mock_select):
        """Test selecting capabilities by category"""
        mock_select.return_value.ask.side_effect = [
            'Select by category',
            'Done - Apply selection'
        ]
        mock_checkbox.return_value.ask.return_value = ['Skills', 'Workflows']

        wizard = RichWizard()
        result = wizard.ask_capabilities_selection()

        assert result['enabled'] is True
        assert result['mode'] == 'category'
        assert 'categories' in result


class TestWizardUIHelpers:
    """Test wizard UI helper methods"""

    def test_wizard_has_clear_screen_method(self):
        """Test wizard has clear screen method"""
        wizard = RichWizard()
        assert hasattr(wizard, 'clear_screen')

        # Should not raise error
        wizard.clear_screen()

    def test_wizard_has_print_panel_method(self):
        """Test wizard has print panel method"""
        wizard = RichWizard()
        assert hasattr(wizard, 'print_panel')

        # Should not raise error
        wizard.print_panel("Test content", title="Test")

    def test_wizard_has_show_step_header_method(self):
        """Test wizard has step header method"""
        wizard = RichWizard()
        assert hasattr(wizard, 'show_step_header')

        project_info = {'detected': True, 'type': 'Python Package'}
        current_dir = Path('.')

        # Should not raise error
        wizard.show_step_header(1, 3, "Test Step", project_info, current_dir)

    def test_create_project_info_panel(self):
        """Test creating project info panel"""
        wizard = RichWizard()

        project_info = {
            'detected': True,
            'type': 'Python Package',
            'framework': 'pip'
        }
        git_config = {
            'is_git_repo': True,
            'has_remote': True,
            'remote_name': 'origin'
        }
        current_dir = Path('test-project')

        result = wizard.create_project_info_panel(project_info, git_config, current_dir)

        # Should return content (either string or Rich object)
        assert result is not None

    def test_create_project_info_panel_no_detection(self):
        """Test project info panel with no detection"""
        wizard = RichWizard()

        project_info = {'detected': False}
        git_config = {'is_git_repo': False, 'has_remote': False}
        current_dir = Path('.')

        result = wizard.create_project_info_panel(project_info, git_config, current_dir)

        assert result is not None


class TestWizardConfigurationSummary:
    """Test configuration summary display"""

    def test_wizard_has_show_summary_method(self):
        """Test wizard has show configuration summary method"""
        wizard = RichWizard()
        assert hasattr(wizard, 'show_configuration_summary')

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_show_summary_confirmed(self, mock_confirm):
        """Test configuration summary - user confirms"""
        mock_confirm.return_value.ask.return_value = True

        wizard = RichWizard()
        config = {
            'preset': 'custom',
            'core_templates': ['AGENTS', 'PROJECT_STATUS'],
            'with_branching': True,
            'ticket_prefix': 'TEST'
        }
        project_info = {'type': 'Node.js Project'}
        current_dir = Path('.')

        result = wizard.show_configuration_summary(config, project_info, current_dir)

        assert result is True

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_show_summary_declined(self, mock_confirm):
        """Test configuration summary - user declines"""
        mock_confirm.return_value.ask.return_value = False

        wizard = RichWizard()
        config = {
            'preset': 'quick',
            'with_branching': False
        }
        project_info = {'type': 'Python Project'}
        current_dir = Path('.')

        result = wizard.show_configuration_summary(config, project_info, current_dir)

        assert result is False


class TestWizardFallbackMode:
    """Test wizard fallback without rich/questionary"""

    def test_wizard_works_without_rich(self):
        """Test wizard can be created without rich"""
        wizard = RichWizard()

        # Should have console attribute (may be None)
        assert hasattr(wizard, 'console')

        # Should be able to call UI methods without errors
        wizard.clear_screen()
        wizard.print_panel("Test", title="Test")

    def test_wizard_fallback_preset_selection(self):
        """Test preset selection fallback without questionary"""
        if QUESTIONARY_AVAILABLE:
            pytest.skip("Questionary is available, skipping fallback test")

        wizard = RichWizard()

        # Mock input to return '1' (quick preset)
        with patch('builtins.input', return_value='1'):
            result = wizard.ask_preset_selection(git_detected=True)
            assert result in ['quick', 'full', 'minimal', 'custom']


class TestWizardEdgeCases:
    """Test wizard edge cases and error handling"""

    def test_wizard_with_empty_project_info(self):
        """Test wizard with minimal project info"""
        wizard = RichWizard()
        project_info = {}
        git_config = {}
        current_dir = Path('.')

        # Should not raise error
        panel = wizard.create_project_info_panel(project_info, git_config, current_dir)
        assert panel is not None

    def test_wizard_config_is_mutable(self):
        """Test wizard config can be modified"""
        wizard = RichWizard()
        initial_config = wizard.config.copy()

        wizard.config['test_key'] = 'test_value'
        assert wizard.config['test_key'] == 'test_value'
        assert 'test_key' not in initial_config

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_handles_empty_template_selection(self, mock_confirm, mock_checkbox, mock_select):
        """Test wizard when user selects no templates (edge case)"""
        mock_select.return_value.ask.return_value = 'custom'
        mock_checkbox.return_value.ask.return_value = []  # No templates selected
        mock_confirm.return_value.ask.return_value = True

        # The wizard should handle empty selection gracefully
        # (Implementation may add default templates or allow empty)
        wizard = RichWizard()
        # Test that it doesn't crash with empty selection


class TestWizardSafeChars:
    """Test safe character handling for fallback mode"""

    def test_get_safe_chars_function_exists(self):
        """Test get_safe_chars function is importable"""
        from proto_gear_pkg.interactive_wizard import get_safe_chars
        assert callable(get_safe_chars)

    def test_get_safe_chars_returns_dict(self):
        """Test get_safe_chars returns a dictionary"""
        from proto_gear_pkg.interactive_wizard import get_safe_chars
        chars = get_safe_chars()
        assert isinstance(chars, dict)

    def test_safe_chars_has_required_keys(self):
        """Test safe chars has all required emoji/character keys"""
        from proto_gear_pkg.interactive_wizard import get_safe_chars
        chars = get_safe_chars()

        # Common keys that should exist
        expected_keys = ['check', 'cross', 'bullet', 'arrow', 'memo']
        for key in expected_keys:
            assert key in chars, f"Missing character: {key}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
