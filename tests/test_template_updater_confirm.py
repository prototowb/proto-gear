"""Tests for TemplateUpdater confirm/backup helpers (PROTO-050 coverage)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.modules.engineering.template_updater import TemplateUpdater


def _updater(tmp_path):
    return TemplateUpdater(tmp_path)


def _stats():
    return {"lines_added": 3, "lines_removed": 1}


def test_create_backup(tmp_path):
    p = tmp_path / "AGENTS.md"
    p.write_text("original", encoding="utf-8")
    backup = _updater(tmp_path)._create_backup(p)
    assert backup.exists()
    assert backup.read_text(encoding="utf-8") == "original"


def test_confirm_update_yes(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "y")
    assert (
        _updater(tmp_path)._confirm_update("--- diff ---", _stats(), "AGENTS.md")
        is True
    )


def test_confirm_update_no(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "n")
    assert (
        _updater(tmp_path)._confirm_update("--- diff ---", _stats(), "AGENTS.md")
        is False
    )


def test_confirm_update_default_empty_is_no(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr("builtins.input", lambda *a, **k: "")
    assert _updater(tmp_path)._confirm_update("d", _stats(), "X.md") is False


def test_confirm_update_invalid_then_yes(tmp_path, monkeypatch, capsys):
    answers = iter(["huh", "y"])
    monkeypatch.setattr("builtins.input", lambda *a, **k: next(answers))
    assert _updater(tmp_path)._confirm_update("d", _stats(), "X.md") is True
    assert "Invalid choice" in capsys.readouterr().out
