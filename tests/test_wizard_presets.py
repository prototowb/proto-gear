"""
Comprehensive tests for interactive wizard preset system
Tests the new v0.5+ preset-based wizard flow
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from proto_gear_pkg.interactive_wizard import (
    RichWizard,
    run_enhanced_wizard,
    _apply_preset_config,
    PRESETS,
    QUESTIONARY_AVAILABLE,
    RICH_AVAILABLE
)


class TestPresetDefinitions:
    """Test preset configuration dictionaries"""

    def test_all_presets_exist(self):
        """Test that all expected presets are defined"""
        expected_presets = ['quick', 'full', 'minimal', 'custom']
        for preset_key in expected_presets:
            assert preset_key in PRESETS, f"Missing preset: {preset_key}"

    def test_preset_structure(self):
        """Test each preset has required fields"""
        required_fields = ['name', 'emoji', 'ascii', 'description', 'details', 'config']

        for preset_key, preset in PRESETS.items():
            for field in required_fields:
                assert field in preset, f"Preset {preset_key} missing {field}"

    def test_quick_preset_config(self):
        """Test quick preset configuration"""
        quick = PRESETS['quick']
        assert quick['name'] == 'Quick Start'
        assert 'AGENTS' in quick['config']['core']
        assert 'PROJECT_STATUS' in quick['config']['core']
        assert 'TESTING' in quick['config']['core']
        assert quick['config']['branching'] == 'auto'
        assert quick['config']['capabilities'] is True

    def test_full_preset_config(self):
        """Test full preset configuration"""
        full = PRESETS['full']
        assert full['name'] == 'Full Setup (All Templates)'
        assert full['config']['with_all'] is True
        assert full['config']['capabilities'] is True

    def test_minimal_preset_config(self):
        """Test minimal preset configuration"""
        minimal = PRESETS['minimal']
        assert minimal['name'] == 'Minimal'
        assert len(minimal['config']['core']) == 2  # Only AGENTS and PROJECT_STATUS
        assert minimal['config']['branching'] is False
        assert minimal['config']['capabilities'] is False

    def test_custom_preset_exists(self):
        """Test custom preset is defined"""
        assert 'custom' in PRESETS
        assert PRESETS['custom']['name'] == 'Custom'


class TestApplyPresetConfig:
    """Test _apply_preset_config function"""

    def test_apply_quick_preset_with_git(self, tmp_path):
        """Test applying quick preset with git detected"""
        preset_config = PRESETS['quick']['config']
        config = _apply_preset_config(preset_config, git_detected=True, current_dir=tmp_path)

        assert 'core_templates' in config
        assert 'AGENTS' in config['core_templates']
        assert 'PROJECT_STATUS' in config['core_templates']
        assert 'TESTING' in config['core_templates']
        assert config['with_branching'] is True  # auto becomes True with git
        assert config['with_capabilities'] is True

    def test_apply_quick_preset_without_git(self, tmp_path):
        """Test applying quick preset without git"""
        preset_config = PRESETS['quick']['config']
        config = _apply_preset_config(preset_config, git_detected=False, current_dir=tmp_path)

        assert config['with_branching'] is False  # auto becomes False without git

    def test_apply_full_preset(self, tmp_path):
        """Test applying full preset"""
        preset_config = PRESETS['full']['config']
        config = _apply_preset_config(preset_config, git_detected=True, current_dir=tmp_path)

        assert config['with_all'] is True
        assert config['with_branching'] is True
        assert config['with_capabilities'] is True

    def test_apply_minimal_preset(self, tmp_path):
        """Test applying minimal preset"""
        preset_config = PRESETS['minimal']['config']
        config = _apply_preset_config(preset_config, git_detected=True, current_dir=tmp_path)

        assert len(config['core_templates']) == 2
        assert config['with_branching'] is False
        assert config['with_capabilities'] is False


class TestRichWizardPresetFlow:
    """Test RichWizard preset selection methods"""

    def test_wizard_initialization(self):
        """Test wizard initializes with config dict"""
        wizard = RichWizard()
        assert hasattr(wizard, 'config')
        assert isinstance(wizard.config, dict)

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_preset_selection_quick(self, mock_select):
        """Test preset selection - user chooses quick"""
        mock_select.return_value.ask.return_value = 'quick'

        wizard = RichWizard()
        result = wizard.ask_preset_selection(git_detected=True)

        assert result == 'quick'
        mock_select.assert_called_once()

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_preset_selection_full(self, mock_select):
        """Test preset selection - user chooses full"""
        mock_select.return_value.ask.return_value = 'full'

        wizard = RichWizard()
        result = wizard.ask_preset_selection(git_detected=False)

        assert result == 'full'

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_preset_selection_custom(self, mock_select):
        """Test preset selection - user chooses custom"""
        mock_select.return_value.ask.return_value = 'custom'

        wizard = RichWizard()
        result = wizard.ask_preset_selection(git_detected=True)

        assert result == 'custom'

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_ask_preset_selection_returns_quick_on_none(self, mock_select):
        """Test preset selection defaults to quick if None returned"""
        mock_select.return_value.ask.return_value = None

        wizard = RichWizard()
        result = wizard.ask_preset_selection(git_detected=True)

        assert result == 'quick'

    def test_show_preset_preview_quick(self):
        """Test showing preset preview for quick"""
        wizard = RichWizard()

        # Mock input to return 'y' (yes)
        with patch('builtins.input', return_value='y'):
            if not RICH_AVAILABLE and not QUESTIONARY_AVAILABLE:
                result = wizard.show_preset_preview('quick', git_detected=True)
                assert result is True

    def test_show_preset_preview_invalid_key_raises(self):
        """Test invalid preset key raises KeyError"""
        wizard = RichWizard()

        with pytest.raises(KeyError):
            wizard.show_preset_preview('invalid_preset', git_detected=True)


class TestRunEnhancedWizardPresetFlow:
    """Test the main wizard with preset flow"""

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_quick_preset_flow(self, mock_confirm, mock_select):
        """Test complete wizard flow with quick preset"""
        # User selects quick preset
        mock_select.return_value.ask.return_value = 'quick'
        # User confirms preset
        mock_confirm.return_value.ask.return_value = True

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

        result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['preset'] == 'quick'
        assert result['confirmed'] is True
        assert 'core_templates' in result
        assert result['with_branching'] is True  # auto with git

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_full_preset_flow(self, mock_confirm, mock_select):
        """Test wizard flow with full preset"""
        mock_select.return_value.ask.return_value = 'full'
        mock_confirm.return_value.ask.return_value = True

        project_info = {'detected': True, 'type': 'Node.js Project'}
        git_config = {'is_git_repo': True, 'has_remote': False}
        current_dir = Path('.')

        result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['preset'] == 'full'
        assert result['with_all'] is True
        assert result['with_capabilities'] is True

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_minimal_preset_flow(self, mock_confirm, mock_select):
        """Test wizard flow with minimal preset"""
        mock_select.return_value.ask.return_value = 'minimal'
        mock_confirm.return_value.ask.return_value = True

        project_info = {'detected': False}
        git_config = {'is_git_repo': False, 'has_remote': False}
        current_dir = Path('.')

        result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['preset'] == 'minimal'
        assert result['with_branching'] is False
        assert result['with_capabilities'] is False

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_preset_rejection_loops_back(self, mock_confirm, mock_select):
        """Test that rejecting preset goes back to selection"""
        # First select quick, reject it, then select minimal, accept it
        mock_select.return_value.ask.side_effect = ['quick', 'minimal']
        mock_confirm.return_value.ask.side_effect = [False, True]  # Reject first, accept second

        project_info = {'detected': True, 'type': 'Python Package'}
        git_config = {'is_git_repo': True, 'has_remote': True}
        current_dir = Path('.')

        result = run_enhanced_wizard(project_info, git_config, current_dir)

        assert result is not None
        assert result['preset'] == 'minimal'  # Ended up with minimal
        assert mock_select.call_count == 2  # Called twice

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    def test_wizard_keyboard_interrupt_during_preset_selection(self):
        """Test KeyboardInterrupt during preset selection"""
        with patch('proto_gear_pkg.interactive_wizard.questionary.select') as mock_select:
            mock_select.return_value.ask.side_effect = KeyboardInterrupt()

            project_info = {'detected': True, 'type': 'Node.js Project'}
            git_config = {'is_git_repo': True, 'has_remote': True}
            current_dir = Path('.')

            result = run_enhanced_wizard(project_info, git_config, current_dir)

            assert result is None

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not available")
    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_wizard_keyboard_interrupt_during_preset_preview(self, mock_select):
        """Test KeyboardInterrupt during preset preview"""
        mock_select.return_value.ask.return_value = 'quick'

        with patch('proto_gear_pkg.interactive_wizard.questionary.confirm') as mock_confirm:
            mock_confirm.return_value.ask.side_effect = KeyboardInterrupt()

            project_info = {'detected': True, 'type': 'Python Package'}
            git_config = {'is_git_repo': False, 'has_remote': False}
            current_dir = Path('.')

            result = run_enhanced_wizard(project_info, git_config, current_dir)

            assert result is None


class TestPresetConfigBranching:
    """Test branching behavior with presets"""

    def test_quick_preset_auto_branching_with_git(self, tmp_path):
        """Test quick preset's auto branching with git"""
        preset_config = PRESETS['quick']['config']
        config = _apply_preset_config(preset_config, git_detected=True, current_dir=tmp_path)

        assert config['with_branching'] is True

    def test_quick_preset_auto_branching_without_git(self, tmp_path):
        """Test quick preset's auto branching without git"""
        preset_config = PRESETS['quick']['config']
        config = _apply_preset_config(preset_config, git_detected=False, current_dir=tmp_path)

        assert config['with_branching'] is False

    def test_full_preset_always_includes_branching(self, tmp_path):
        """Test full preset always includes branching"""
        preset_config = PRESETS['full']['config']

        # With git
        config_with_git = _apply_preset_config(preset_config, git_detected=True, current_dir=tmp_path)
        assert config_with_git['with_branching'] is True

        # Without git (still True for full preset)
        config_without_git = _apply_preset_config(preset_config, git_detected=False, current_dir=tmp_path)
        assert config_without_git['with_branching'] is True

    def test_minimal_preset_never_includes_branching(self, tmp_path):
        """Test minimal preset never includes branching"""
        preset_config = PRESETS['minimal']['config']

        # Even with git
        config = _apply_preset_config(preset_config, git_detected=True, current_dir=tmp_path)
        assert config['with_branching'] is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
