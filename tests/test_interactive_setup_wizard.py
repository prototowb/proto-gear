"""Tests for the simple input()-based setup wizard (PROTO-050 coverage).

interactive_setup_wizard() is the non-questionary fallback wizard. It is driven
purely through safe_input(), so feeding a canned answer sequence exercises every
branch (branching yes/no, prefix valid/invalid/default, confirm/cancel, invalid
retries) without any real terminal.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import proto_gear as engine


def _feed(monkeypatch, tmp_path, answers):
    """Point the wizard at tmp_path and feed it the given answers in order."""
    monkeypatch.chdir(tmp_path)
    it = iter(answers)
    monkeypatch.setattr(engine, "safe_input", lambda *a, **k: next(it, ""))


class TestInteractiveSetupWizard:
    def test_full_with_branching(self, tmp_path, monkeypatch, capsys):
        _feed(monkeypatch, tmp_path, ["My cool project", "y", "APP", "y"])
        cfg = engine.interactive_setup_wizard()
        assert cfg["project_description"] == "My cool project"
        assert cfg["with_branching"] is True
        assert cfg["ticket_prefix"] == "APP"
        assert cfg["confirmed"] is True

    def test_no_branching(self, tmp_path, monkeypatch, capsys):
        _feed(monkeypatch, tmp_path, ["", "n", "y"])
        cfg = engine.interactive_setup_wizard()
        assert cfg["with_branching"] is False
        assert cfg["ticket_prefix"] is None
        assert cfg["confirmed"] is True
        assert "project_description" not in cfg  # blank description skipped

    def test_invalid_prefix_falls_back_to_suggested(
        self, tmp_path, monkeypatch, capsys
    ):
        _feed(monkeypatch, tmp_path, ["", "y", "!!", "y"])
        cfg = engine.interactive_setup_wizard()
        assert cfg["with_branching"] is True
        # "!!" is invalid → suggested prefix used instead
        assert cfg["ticket_prefix"] and cfg["ticket_prefix"].isalnum()

    def test_blank_prefix_uses_suggested(self, tmp_path, monkeypatch, capsys):
        _feed(monkeypatch, tmp_path, ["", "y", "", "y"])
        cfg = engine.interactive_setup_wizard()
        assert cfg["ticket_prefix"]  # non-empty suggested default

    def test_invalid_yesno_then_valid(self, tmp_path, monkeypatch, capsys):
        # "maybe" is rejected and re-prompted until a valid y/n is given.
        _feed(monkeypatch, tmp_path, ["", "maybe", "n", "y"])
        cfg = engine.interactive_setup_wizard()
        assert cfg["with_branching"] is False

    def test_cancel(self, tmp_path, monkeypatch, capsys):
        _feed(monkeypatch, tmp_path, ["", "n", "n"])
        cfg = engine.interactive_setup_wizard()
        assert cfg["confirmed"] is False
