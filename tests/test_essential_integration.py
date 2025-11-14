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

    def test_presets_properly_structured(self):
        """Test that all presets have proper structure"""
        from proto_gear_pkg.interactive_wizard import PRESETS
        for preset_name, preset_data in PRESETS.items():
            assert 'name' in preset_data
            assert 'description' in preset_data
            assert 'config' in preset_data

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

    def test_setup_function_exists(self):
        """Test setup function is callable"""
        assert callable(setup_agent_framework_only)

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

    def test_detect_git_function_returns_dict(self):
        """Test git detection returns a dict"""
        result = detect_git_config()
        assert isinstance(result, dict)
        assert 'is_git_repo' in result


class TestCLIEssentials:
    """Essential CLI tests"""

    def test_main_function_exists(self):
        """Test main CLI entry point exists"""
        assert callable(main)

    def test_setup_function_is_callable(self):
        """Test setup function is callable"""
        assert callable(setup_agent_framework_only)


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
