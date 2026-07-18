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
    get_safe_chars,
    QUESTIONARY_AVAILABLE,
    RICH_AVAILABLE,
)
from proto_gear_pkg.modules.engineering.init_planning import build_detected_plan
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


class TestDetectedPlanApplication:
    """The detection-driven plan that replaced the presets (ADR-004)."""

    def test_git_repo_plans_branching_and_prefix(self, tmp_path):
        plan = build_detected_plan({}, {"is_git_repo": True}, tmp_path)
        assert plan["with_branching"] is True
        assert plan["ticket_prefix"]
        assert plan["with_capabilities"] is True
        assert plan["profile"] == "frontier"

    def test_no_git_plans_no_branching(self, tmp_path):
        plan = build_detected_plan({}, {"is_git_repo": False}, tmp_path)
        assert plan["with_branching"] is False
        assert plan["ticket_prefix"] is None

    def test_tests_dir_plans_testing_template(self, tmp_path):
        (tmp_path / "tests").mkdir()
        plan = build_detected_plan({}, {}, tmp_path)
        assert plan["core_templates"].get("TESTING") is True
        assert "TESTING" in plan["reasons"]

    def test_remote_plans_contributing(self, tmp_path):
        plan = build_detected_plan(
            {}, {"is_git_repo": True, "has_remote": True}, tmp_path
        )
        assert plan["core_templates"].get("CONTRIBUTING") is True


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


class TestIntentCapture:
    """The planning-intake prompts (ADR-004 move 2) via the input fallback."""

    def _wizard_without_questionary(self, monkeypatch):
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        wizard = RichWizard()
        wizard.console = None  # plain-print path, no rich panels
        return wizard

    def test_all_skipped_returns_empty_intent(self, monkeypatch, tmp_path):
        wizard = self._wizard_without_questionary(monkeypatch)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "")
        assert wizard.ask_intent_capture(tmp_path) == {}

    def test_captures_description_boundaries_conventions(self, monkeypatch, tmp_path):
        wizard = self._wizard_without_questionary(monkeypatch)
        answers = iter(
            [
                "A CLI for widgets.",  # description
                "NEVER push to main",  # boundary 1
                "",  # end boundaries
                "All times are UTC",  # convention 1
                "Use uv, not pip",  # convention 2
                "",  # end conventions
            ]
        )
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(answers))
        intent = wizard.ask_intent_capture(tmp_path)
        assert intent["project_description"] == "A CLI for widgets."
        assert intent["boundaries"] == ["NEVER push to main"]
        assert intent["conventions"] == ["All times are UTC", "Use uv, not pip"]

    def test_existing_specs_skips_description_prompt(self, monkeypatch, tmp_path):
        """With PROJECT_SPECIFICATIONS.md present the description prompt is silent."""
        (tmp_path / "PROJECT_SPECIFICATIONS.md").write_text("# specs", encoding="utf-8")
        wizard = self._wizard_without_questionary(monkeypatch)
        answers = iter(["NEVER a", "", ""])  # boundaries then conventions
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(answers))
        intent = wizard.ask_intent_capture(tmp_path)
        assert "project_description" not in intent
        assert intent["boundaries"] == ["NEVER a"]


class TestPlanChoiceFallback:
    """ask_plan_choice input fallback."""

    def _wizard(self, monkeypatch):
        monkeypatch.setattr(wizard_mod, "QUESTIONARY_AVAILABLE", False)
        wizard = RichWizard()
        wizard.console = None
        return wizard

    def test_enter_accepts(self, monkeypatch):
        wizard = self._wizard(monkeypatch)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "")
        assert wizard.ask_plan_choice(offer_prefix=True) == "accept"

    def test_customize_and_cancel(self, monkeypatch):
        wizard = self._wizard(monkeypatch)
        monkeypatch.setattr("builtins.input", lambda *a, **k: "c")
        assert wizard.ask_plan_choice(offer_prefix=False) == "customize"
        monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
        assert wizard.ask_plan_choice(offer_prefix=False) is None

    def test_prefix_only_offered_when_branching(self, monkeypatch):
        wizard = self._wizard(monkeypatch)
        answers = iter(["p", "y"])  # 'p' invalid without prefix on offer → reprompt
        monkeypatch.setattr("builtins.input", lambda *a, **k: next(answers))
        assert wizard.ask_plan_choice(offer_prefix=False) == "accept"


class TestEnhancedWizardFlow:
    """run_enhanced_wizard wiring: intake → plan → accept/cancel."""

    def _run(self, monkeypatch, tmp_path, *, intent, choice):
        monkeypatch.setattr(RichWizard, "clear_screen", lambda self: None)
        monkeypatch.setattr(
            RichWizard, "ask_intent_capture", lambda self, d: dict(intent)
        )
        monkeypatch.setattr(RichWizard, "show_detected_plan", lambda self, p: None)
        monkeypatch.setattr(RichWizard, "ask_plan_choice", lambda self, **k: choice)
        return run_enhanced_wizard(
            {"detected": True, "type": "Python"},
            {"is_git_repo": True, "has_remote": False},
            tmp_path,
        )

    def test_accept_returns_confirmed_plan_with_intent(self, monkeypatch, tmp_path):
        config = self._run(
            monkeypatch,
            tmp_path,
            intent={"project_description": "X.", "boundaries": ["NEVER y"]},
            choice="accept",
        )
        assert config["confirmed"] is True
        assert config["with_branching"] is True
        assert config["with_capabilities"] is True
        assert config["profile"] == "frontier"
        assert config["project_description"] == "X."
        assert config["boundaries"] == ["NEVER y"]

    def test_cancel_returns_none(self, monkeypatch, tmp_path):
        assert self._run(monkeypatch, tmp_path, intent={}, choice=None) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
