"""
Focused wizard tests to increase coverage from 44% to 81%+
Targets interactive_wizard.py which is currently at 17%
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from proto_gear_pkg.interactive_wizard import (
    RichWizard,
    run_enhanced_wizard,
    _apply_preset_config,
    PRESETS,
    get_safe_chars,
    QUESTIONARY_AVAILABLE,
    RICH_AVAILABLE
)


class TestWizardCoreFlow:
    """Test core wizard functionality"""

    def test_create_project_info_panel(self):
        """Test project info panel creation"""
        wizard = RichWizard()
        result = wizard.create_project_info_panel(
            {'detected': True, 'type': 'Python', 'framework': 'Flask'},
            {'is_git_repo': True, 'has_remote': True, 'remote_name': 'origin'},
            Path('.')
        )
        assert result is not None

    def test_safe_chars_function(self):
        """Test safe character mapping"""
        chars = get_safe_chars()
        assert isinstance(chars, dict)
        assert 'check' in chars
        assert 'cross' in chars
        assert 'bullet' in chars

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_preset_selection(self, mock_select):
        """Test preset selection"""
        mock_select.return_value.ask.return_value = 'full'
        wizard = RichWizard()
        result = wizard.ask_preset_selection(git_detected=True)
        assert result == 'full'

    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_show_preset_preview_confirm(self, mock_confirm):
        """Test preset preview confirmation"""
        mock_confirm.return_value.ask.return_value = True
        wizard = RichWizard()

        if QUESTIONARY_AVAILABLE and RICH_AVAILABLE:
            result = wizard.show_preset_preview('quick', True)
            assert result is True

    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    def test_ask_core_templates_selection(self, mock_checkbox):
        """Test core template selection"""
        mock_checkbox.return_value.ask.return_value = ['AGENTS', 'PROJECT_STATUS']
        wizard = RichWizard()
        result = wizard.ask_core_templates_selection()
        assert 'AGENTS' in result
        assert 'PROJECT_STATUS' in result

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.text')
    def test_ask_git_workflow_options(self, mock_text, mock_select):
        """Test git workflow options"""
        mock_select.return_value.ask.return_value = 'Yes, add git workflow templates'
        mock_text.return_value.ask.return_value = 'TEST'

        wizard = RichWizard()
        result = wizard.ask_git_workflow_options(
            {'is_git_repo': True, 'has_remote': True},
            Path('.')
        )
        assert result['with_branching'] is True
        assert result['ticket_prefix'] == 'TEST'

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_capabilities_selection_all(self, mock_select):
        """Test selecting all capabilities"""
        mock_select.return_value.ask.return_value = 'All capabilities'
        wizard = RichWizard()
        result = wizard.ask_capabilities_selection()
        assert result['enabled'] is True

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_capabilities_selection_none(self, mock_select):
        """Test selecting no capabilities"""
        mock_select.return_value.ask.return_value = 'No capabilities'
        wizard = RichWizard()
        result = wizard.ask_capabilities_selection()
        assert result['enabled'] is False

    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_show_configuration_summary(self, mock_confirm):
        """Test configuration summary"""
        mock_confirm.return_value.ask.return_value = True
        wizard = RichWizard()
        result = wizard.show_configuration_summary(
            {'preset': 'quick', 'with_branching': True},
            {'type': 'Python'},
            Path('.')
        )
        assert result is True

    def test_wizard_clear_screen(self):
        """Test clear screen method"""
        wizard = RichWizard()
        wizard.clear_screen()  # Should not raise error

    def test_wizard_print_panel(self):
        """Test print panel method"""
        wizard = RichWizard()
        wizard.print_panel("Test content", title="Test")  # Should not raise error

    def test_wizard_show_step_header(self):
        """Test step header display"""
        wizard = RichWizard()
        wizard.show_step_header(
            1, 3, "Test Step",
            {'type': 'Python'},
            Path('.')
        )  # Should not raise error


class TestPresetApplication:
    """Test preset configuration application"""

    def test_apply_full_preset_with_git(self, tmp_path):
        """Test full preset with git"""
        config = _apply_preset_config(
            PRESETS['full']['config'],
            git_detected=True,
            current_dir=tmp_path
        )
        assert config['with_all'] is True
        assert config['with_branching'] is True
        assert config['with_capabilities'] is True

    def test_apply_quick_preset_without_git(self, tmp_path):
        """Test quick preset without git"""
        config = _apply_preset_config(
            PRESETS['quick']['config'],
            git_detected=False,
            current_dir=tmp_path
        )
        assert config['with_branching'] is False  # auto becomes False

    def test_apply_minimal_preset_always_no_branching(self, tmp_path):
        """Test minimal preset never has branching"""
        config = _apply_preset_config(
            PRESETS['minimal']['config'],
            git_detected=True,  # Even with git
            current_dir=tmp_path
        )
        assert config['with_branching'] is False

    def test_preset_core_templates(self, tmp_path):
        """Test preset includes core templates"""
        config = _apply_preset_config(
            PRESETS['quick']['config'],
            git_detected=True,
            current_dir=tmp_path
        )
        assert 'core_templates' in config
        assert 'AGENTS' in config['core_templates']
        assert 'PROJECT_STATUS' in config['core_templates']


class TestWizardCustomFlow:
    """Test custom wizard flow"""

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_custom_preset_complete_flow(self, mock_confirm, mock_checkbox, mock_select):
        """Test complete custom preset flow"""
        mock_select.return_value.ask.side_effect = [
            'custom',  # Preset selection
            'Yes, add git workflow templates',  # Git workflow
            'All capabilities'  # Capabilities
        ]
        mock_checkbox.return_value.ask.return_value = ['AGENTS', 'PROJECT_STATUS', 'TESTING']
        mock_confirm.return_value.ask.return_value = True

        with patch('proto_gear_pkg.interactive_wizard.questionary.text') as mock_text:
            mock_text.return_value.ask.return_value = 'PROJ'

            result = run_enhanced_wizard(
                {'detected': True, 'type': 'Python'},
                {'is_git_repo': True, 'has_remote': True},
                Path('.')
            )

        assert result is not None
        assert result['preset'] == 'custom'
        assert result['confirmed'] is True

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.checkbox')
    def test_custom_wizard_keyboard_interrupt_templates(self, mock_checkbox, mock_select):
        """Test KeyboardInterrupt during template selection"""
        mock_select.return_value.ask.return_value = 'custom'
        mock_checkbox.return_value.ask.side_effect = KeyboardInterrupt()

        result = run_enhanced_wizard(
            {'detected': True, 'type': 'Node.js'},
            {'is_git_repo': True, 'has_remote': False},
            Path('.')
        )

        assert result is None


class TestWizardEdgeCases:
    """Test wizard edge cases"""

    def test_wizard_with_empty_project_info(self):
        """Test wizard with minimal project info"""
        wizard = RichWizard()
        panel = wizard.create_project_info_panel({}, {}, Path('.'))
        assert panel is not None

    def test_wizard_config_mutable(self):
        """Test wizard config can be modified"""
        wizard = RichWizard()
        wizard.config['test'] = 'value'
        assert wizard.config['test'] == 'value'

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_preset_rejection_loop(self, mock_confirm, mock_select):
        """Test rejecting preset and selecting another"""
        mock_select.return_value.ask.side_effect = ['quick', 'minimal']
        mock_confirm.return_value.ask.side_effect = [False, True]  # Reject first, accept second

        result = run_enhanced_wizard(
            {'detected': True, 'type': 'Python'},
            {'is_git_repo': True, 'has_remote': True},
            Path('.')
        )

        assert result is not None
        assert result['preset'] == 'minimal'

    def test_all_presets_have_required_config(self):
        """Test all presets have valid config"""
        for preset_key, preset in PRESETS.items():
            assert 'config' in preset
            config = preset['config']
            assert 'core' in config or 'with_all' in config

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_full_preset_flow(self, mock_confirm, mock_select):
        """Test full preset flow"""
        mock_select.return_value.ask.return_value = 'full'
        mock_confirm.return_value.ask.return_value = True

        result = run_enhanced_wizard(
            {'detected': True, 'type': 'JavaScript', 'framework': 'React'},
            {'is_git_repo': True, 'has_remote': True, 'remote_name': 'origin'},
            Path('test-project')
        )

        assert result is not None
        assert result['preset'] == 'full'
        assert result['with_all'] is True

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_minimal_preset_flow(self, mock_confirm, mock_select):
        """Test minimal preset flow"""
        mock_select.return_value.ask.return_value = 'minimal'
        mock_confirm.return_value.ask.return_value = True

        result = run_enhanced_wizard(
            {'detected': False},
            {'is_git_repo': False, 'has_remote': False},
            Path('.')
        )

        assert result is not None
        assert result['preset'] == 'minimal'
        assert result['with_capabilities'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
