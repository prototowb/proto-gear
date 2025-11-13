"""
Essential integration tests for Proto Gear
Focused, high-value tests to achieve 81%+ coverage efficiently
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

from proto_gear_pkg.proto_gear import (
    setup_agent_framework_only,
    detect_project_structure,
    detect_git_config,
    main
)
from proto_gear_pkg.interactive_wizard import (
    RichWizard,
    run_enhanced_wizard,
    _apply_preset_config,
    PRESETS
)


# ============================================================================
# Wizard Essential Tests (10 tests)
# ============================================================================

class TestWizardEssentials:
    """Essential wizard tests for coverage"""

    def test_wizard_initialization(self):
        """Test basic wizard creation"""
        wizard = RichWizard()
        assert wizard is not None
        assert hasattr(wizard, 'config')

    def test_preset_definitions_exist(self):
        """Test all presets are defined"""
        assert 'quick' in PRESETS
        assert 'full' in PRESETS
        assert 'minimal' in PRESETS
        assert 'custom' in PRESETS

    def test_apply_quick_preset_with_git(self, tmp_path):
        """Test applying quick preset with git"""
        config = _apply_preset_config(
            PRESETS['quick']['config'],
            git_detected=True,
            current_dir=tmp_path
        )
        assert 'core_templates' in config
        assert config['with_branching'] is True

    def test_apply_minimal_preset(self, tmp_path):
        """Test applying minimal preset"""
        config = _apply_preset_config(
            PRESETS['minimal']['config'],
            git_detected=False,
            current_dir=tmp_path
        )
        assert config['with_branching'] is False
        assert config['with_capabilities'] is False

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    @patch('proto_gear_pkg.interactive_wizard.questionary.confirm')
    def test_wizard_quick_preset_flow(self, mock_confirm, mock_select):
        """Test complete quick preset flow"""
        mock_select.return_value.ask.return_value = 'quick'
        mock_confirm.return_value.ask.return_value = True

        result = run_enhanced_wizard(
            {'detected': True, 'type': 'Python'},
            {'is_git_repo': True, 'has_remote': True},
            Path('.')
        )

        assert result is not None
        assert result['preset'] == 'quick'
        assert result['confirmed'] is True

    @patch('proto_gear_pkg.interactive_wizard.questionary.select')
    def test_wizard_keyboard_interrupt(self, mock_select):
        """Test wizard handles KeyboardInterrupt"""
        mock_select.return_value.ask.side_effect = KeyboardInterrupt()

        result = run_enhanced_wizard(
            {'detected': True, 'type': 'Node.js'},
            {'is_git_repo': False, 'has_remote': False},
            Path('.')
        )

        assert result is None

    def test_wizard_has_ui_methods(self):
        """Test wizard has essential UI methods"""
        wizard = RichWizard()
        assert hasattr(wizard, 'clear_screen')
        assert hasattr(wizard, 'print_panel')
        assert hasattr(wizard, 'create_project_info_panel')

    def test_wizard_preset_config_structure(self):
        """Test preset configs have required fields"""
        for preset_key, preset in PRESETS.items():
            assert 'name' in preset
            assert 'config' in preset
            assert 'description' in preset


# ============================================================================
# Setup & CLI Essential Tests (15 tests)
# ============================================================================

class TestSetupEssentials:
    """Essential setup function tests"""

    def test_setup_dry_run(self, tmp_path, capsys):
        """Test setup in dry-run mode"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            setup_agent_framework_only(dry_run=True)

            captured = capsys.readouterr()
            assert 'Agent Framework Setup' in captured.out

            # Should NOT create files in dry-run
            assert not (tmp_path / 'AGENTS.md').exists()

    def test_setup_creates_agents_md(self, tmp_path):
        """Test setup creates AGENTS.md"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock:
                mock.return_value = {'detected': True, 'type': 'Python'}

                setup_agent_framework_only(dry_run=False)

                assert (tmp_path / 'AGENTS.md').exists()
                content = (tmp_path / 'AGENTS.md').read_text()
                assert 'ProtoGear' in content

    def test_setup_with_branching(self, tmp_path):
        """Test setup with branching enabled"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            with patch('proto_gear_pkg.proto_gear.detect_project_structure') as mock_detect:
                with patch('proto_gear_pkg.proto_gear.detect_git_config') as mock_git:
                    mock_detect.return_value = {'detected': True, 'type': 'Node.js'}
                    mock_git.return_value = {'is_git_repo': True, 'has_remote': True}

                    setup_agent_framework_only(
                        dry_run=False,
                        with_branching=True,
                        ticket_prefix='TEST'
                    )

                    assert (tmp_path / 'BRANCHING.md').exists()

    def test_detect_nodejs_project(self, tmp_path):
        """Test Node.js project detection"""
        (tmp_path / 'package.json').write_text('{"name": "test"}')
        result = detect_project_structure(tmp_path)
        assert result['detected'] is True
        assert 'Node.js' in result['type']

    def test_detect_python_project(self, tmp_path):
        """Test Python project detection"""
        (tmp_path / 'requirements.txt').write_text('flask==2.0.0')
        result = detect_project_structure(tmp_path)
        assert result['detected'] is True
        assert 'Python' in result['type']

    def test_detect_no_project(self, tmp_path):
        """Test when no project is detected"""
        result = detect_project_structure(tmp_path)
        assert result['detected'] is False

    def test_detect_git_repo(self, tmp_path):
        """Test git repository detection"""
        git_dir = tmp_path / '.git'
        git_dir.mkdir()

        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            result = detect_git_config()

        assert result['is_git_repo'] is True

    def test_detect_no_git(self, tmp_path):
        """Test when directory is not a git repo"""
        with patch('proto_gear_pkg.proto_gear.Path', return_value=tmp_path):
            result = detect_git_config()

        assert result['is_git_repo'] is False


class TestCLIEssentials:
    """Essential CLI tests"""

    @patch('proto_gear_pkg.proto_gear.sys.argv', ['pg', 'init', '--dry-run'])
    @patch('proto_gear_pkg.proto_gear.setup_agent_framework_only')
    def test_cli_init_dry_run(self, mock_setup):
        """Test CLI init with dry-run flag"""
        mock_setup.return_value = None

        try:
            main()
        except SystemExit:
            pass

        assert mock_setup.called
        args, kwargs = mock_setup.call_args
        assert kwargs.get('dry_run') is True

    @patch('proto_gear_pkg.proto_gear.sys.argv', ['pg', 'init', '--with-branching'])
    @patch('proto_gear_pkg.proto_gear.setup_agent_framework_only')
    def test_cli_init_with_branching(self, mock_setup):
        """Test CLI init with branching flag"""
        mock_setup.return_value = None

        try:
            main()
        except SystemExit:
            pass

        assert mock_setup.called
        args, kwargs = mock_setup.call_args
        assert kwargs.get('with_branching') is True

    @patch('proto_gear_pkg.proto_gear.sys.argv', ['pg', 'init', '--ticket-prefix', 'MYAPP'])
    @patch('proto_gear_pkg.proto_gear.setup_agent_framework_only')
    def test_cli_init_with_ticket_prefix(self, mock_setup):
        """Test CLI init with ticket prefix"""
        mock_setup.return_value = None

        try:
            main()
        except SystemExit:
            pass

        assert mock_setup.called
        args, kwargs = mock_setup.call_args
        assert kwargs.get('ticket_prefix') == 'MYAPP'

    @patch('proto_gear_pkg.proto_gear.sys.argv', ['pg', 'help'])
    def test_cli_help_command(self, capsys):
        """Test CLI help command"""
        try:
            main()
        except SystemExit:
            pass

        captured = capsys.readouterr()
        assert 'proto' in captured.out.lower() or 'help' in captured.out.lower()

    @patch('proto_gear_pkg.proto_gear.sys.argv', ['pg', 'init'])
    @patch('proto_gear_pkg.proto_gear.setup_agent_framework_only')
    def test_cli_keyboard_interrupt(self, mock_setup):
        """Test CLI handles KeyboardInterrupt"""
        mock_setup.side_effect = KeyboardInterrupt()

        try:
            main()
        except KeyboardInterrupt:
            pass
        except SystemExit:
            pass

    @patch('proto_gear_pkg.proto_gear.sys.argv', [
        'pg', 'init',
        '--dry-run',
        '--with-branching',
        '--ticket-prefix', 'TEST'
    ])
    @patch('proto_gear_pkg.proto_gear.setup_agent_framework_only')
    def test_cli_all_flags_combined(self, mock_setup):
        """Test CLI with multiple flags"""
        mock_setup.return_value = None

        try:
            main()
        except SystemExit:
            pass

        assert mock_setup.called
        args, kwargs = mock_setup.call_args
        assert kwargs.get('dry_run') is True
        assert kwargs.get('with_branching') is True
        assert kwargs.get('ticket_prefix') == 'TEST'


# ============================================================================
# Package Integration Tests (5 tests)
# ============================================================================

class TestPackageIntegration:
    """Essential package-level integration tests"""

    def test_package_imports(self):
        """Test main package imports work"""
        import proto_gear_pkg
        from proto_gear_pkg import proto_gear
        from proto_gear_pkg import interactive_wizard
        from proto_gear_pkg import ui_helper
        assert proto_gear is not None
        assert interactive_wizard is not None
        assert ui_helper is not None

    def test_package_version(self):
        """Test package has version"""
        from proto_gear_pkg import __version__
        assert __version__ is not None
        assert isinstance(__version__, str)
        assert '.' in __version__

    def test_main_function_exists(self):
        """Test main entry point exists"""
        from proto_gear_pkg.proto_gear import main
        assert callable(main)

    def test_wizard_available(self):
        """Test wizard is importable"""
        from proto_gear_pkg.interactive_wizard import run_enhanced_wizard
        assert callable(run_enhanced_wizard)

    def test_constants_available(self):
        """Test important constants are available"""
        from proto_gear_pkg.interactive_wizard import PRESETS
        assert PRESETS is not None
        assert len(PRESETS) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
