"""Tests for terminal presentation helpers (PROTO-050 coverage)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import presentation


def test_get_logo_v1_nonempty():
    assert isinstance(presentation.get_logo_v1(), str)
    assert presentation.get_logo_v1().strip()


def test_show_splash_screen(capsys):
    presentation.show_splash_screen()
    assert capsys.readouterr().out


def test_show_help(capsys):
    presentation.show_help()
    out = capsys.readouterr().out
    assert "pg" in out.lower()


def test_print_farewell(capsys):
    presentation.print_farewell()
    assert capsys.readouterr().out


def test_print_centered(capsys):
    presentation.print_centered("hi", width=20)
    assert "hi" in capsys.readouterr().out


def test_safe_input_returns_default_on_eof(monkeypatch):
    def _raise(_prompt=""):
        raise EOFError()

    monkeypatch.setattr("builtins.input", _raise)
    assert presentation.safe_input("q: ", default="fallback") == "fallback"
