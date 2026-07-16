"""
Focused wizard tests to increase coverage from 44% to 81%+
Targets interactive_wizard.py which is currently at 17%
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import proto_gear_pkg.modules.engineering.interactive_wizard as wizard_mod
from proto_gear_pkg.modules.engineering.interactive_wizard import (
    RichWizard,
    run_enhanced_wizard,
    _apply_preset_config,
    PRESETS,
    get_safe_chars,
    QUESTIONARY_AVAILABLE,
    RICH_AVAILABLE,
)
from proto_gear_pkg.module_core.capability_profile import (
    CAPABILITY_PROFILES,
    DEFAULT_PROFILE,
)


class TestWizardCoreFlow:
    """Test core wizard functionality"""

    def test_create_project_info_panel(self):
        """Test project info panel creation"""
        wizard = RichWizard()
        result = wizard.create_project_info_panel(
            {"detected": True, "type": "Python", "framework": "Flask"},
            {"is_git_repo": True, "has_remote": True, "remote_name": "origin"},
            Path("."),
        )
        assert result is not None

    def test_safe_chars_function(self):
        """Test safe character mapping"""
        chars = get_safe_chars()
        assert isinstance(chars, dict)
        assert "check" in chars
        assert "cross" in chars
        assert "bullet" in chars

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
            1, 3, "Test Step", {"type": "Python"}, Path(".")
        )  # Should not raise error


class TestPresetApplication:
    """Test preset configuration application"""

    def test_apply_full_preset_with_git(self, tmp_path):
        """Test full preset with git"""
        config = _apply_preset_config(
            PRESETS["full"]["config"], git_detected=True, current_dir=tmp_path
        )
        assert config["with_all"] is True
        assert config["with_branching"] is True
        assert config["with_capabilities"] is True

    def test_apply_quick_preset_without_git(self, tmp_path):
        """Test quick preset without git"""
        config = _apply_preset_config(
            PRESETS["quick"]["config"], git_detected=False, current_dir=tmp_path
        )
        assert config["with_branching"] is False  # auto becomes False

    def test_apply_minimal_preset_always_no_branching(self, tmp_path):
        """Test minimal preset never has branching"""
        config = _apply_preset_config(
            PRESETS["minimal"]["config"],
            git_detected=True,  # Even with git
            current_dir=tmp_path,
        )
        assert config["with_branching"] is False

    def test_preset_core_templates(self, tmp_path):
        """Test preset includes core templates"""
        config = _apply_preset_config(
            PRESETS["quick"]["config"], git_detected=True, current_dir=tmp_path
        )
        assert "core_templates" in config
        assert "AGENTS" in config["core_templates"]
        assert "PROJECT_STATUS" in config["core_templates"]


class TestWizardCustomFlow:
    """Test custom wizard flow"""

    def test_wizard_handles_custom_config(self):
        """Test wizard can accept custom configuration"""
        wizard = RichWizard()
        wizard.config["custom_key"] = "custom_value"
        assert wizard.config["custom_key"] == "custom_value"


class TestWizardEdgeCases:
    """Test wizard edge cases"""

    def test_wizard_config_mutable(self):
        """Test wizard config can be modified"""
        wizard = RichWizard()
        wizard.config["test"] = "value"
        assert wizard.config["test"] == "value"

    def test_all_presets_have_required_config(self):
        """Test all presets have valid config"""
        for preset_key, preset in PRESETS.items():
            assert "config" in preset
            config = preset["config"]
            # Check that config exists and is a dictionary (or None for custom preset)
            if config is not None:
                assert isinstance(config, dict)
                assert len(config) >= 0

    def test_preset_config_full_has_with_all(self):
        """Test full preset has with_all"""
        assert PRESETS["full"]["config"].get("with_all") is True

    def test_preset_config_minimal_no_capabilities(self):
        """Test minimal preset has no capabilities"""
        minimal_config = PRESETS["minimal"]["config"]
        # Check for capabilities configuration (can be 'capabilities' or 'with_capabilities')
        has_capabilities = minimal_config.get(
            "with_capabilities", minimal_config.get("capabilities", False)
        )
        assert has_capabilities is False

    def test_wizard_initialization_creates_empty_config(self):
        """Test wizard starts with empty config"""
        wizard = RichWizard()
        assert wizard.config == {}


class TestAskCapabilityProfile:
    """The init-time frontier/verbose profile prompt (PROTO follow-on)."""

    def test_fallback_empty_input_returns_default(self, monkeypatch):
        """No questionary + blank answer → the default profile."""
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "")
        wizard = RichWizard()
        assert wizard.ask_capability_profile() == DEFAULT_PROFILE

    def test_fallback_empty_input_respects_passed_default(self, monkeypatch):
        """A blank answer honours the caller's default, not just frontier."""
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "")
        wizard = RichWizard()
        assert wizard.ask_capability_profile(default="verbose") == "verbose"

    def test_fallback_selects_verbose(self, monkeypatch):
        """Typing 'verbose' returns verbose."""
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "verbose")
        wizard = RichWizard()
        assert wizard.ask_capability_profile() == "verbose"

    def test_fallback_reprompts_on_invalid(self, monkeypatch):
        """Invalid input loops until a valid profile is given."""
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        answers = iter(["bogus", "frontier"])
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(answers))
        wizard = RichWizard()
        assert wizard.ask_capability_profile() == "frontier"

    def test_result_is_always_a_valid_profile(self, monkeypatch):
        """Whatever the path, the return value is a known profile name."""
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "verbose")
        wizard = RichWizard()
        assert wizard.ask_capability_profile() in CAPABILITY_PROFILES

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not installed")
    def test_questionary_path_returns_selection(self, monkeypatch):
        """The rich path returns whatever questionary.select yields."""
        fake_prompt = Mock()
        fake_prompt.ask.return_value = "verbose"
        monkeypatch.setattr(
            wizard_mod.questionary, "select", lambda *a, **k: fake_prompt
        )
        wizard = RichWizard()
        wizard.console = None  # skip the rich panel render
        assert wizard.ask_capability_profile() == "verbose"

    @pytest.mark.skipif(not QUESTIONARY_AVAILABLE, reason="questionary not installed")
    def test_questionary_cancel_falls_back_to_default(self, monkeypatch):
        """Ctrl-C / cancel (ask() → None) yields the default, not None."""
        fake_prompt = Mock()
        fake_prompt.ask.return_value = None
        monkeypatch.setattr(
            wizard_mod.questionary, "select", lambda *a, **k: fake_prompt
        )
        wizard = RichWizard()
        wizard.console = None
        assert wizard.ask_capability_profile(default="verbose") == "verbose"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
