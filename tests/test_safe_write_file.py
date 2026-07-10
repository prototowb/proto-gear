"""Tests for templates.safe_write_file conflict handling (PROTO-050 coverage)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.modules.engineering import templates


def test_dry_run(tmp_path):
    action, written = templates.safe_write_file(tmp_path / "x.md", "hi", dry_run=True)
    assert action == "would_create" and written is False
    assert not (tmp_path / "x.md").exists()


def test_create_new(tmp_path):
    action, written = templates.safe_write_file(tmp_path / "x.md", "hi")
    assert action == "created" and written is True
    assert (tmp_path / "x.md").read_text(encoding="utf-8") == "hi"


def test_force_overwrite(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("old", encoding="utf-8")
    action, written = templates.safe_write_file(p, "new", force=True)
    assert action == "overwritten"
    assert p.read_text(encoding="utf-8") == "new"


def test_non_interactive_skips_existing(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("old", encoding="utf-8")
    action, written = templates.safe_write_file(p, "new", interactive=False)
    assert action == "skipped" and written is False
    assert p.read_text(encoding="utf-8") == "old"


def _answers(monkeypatch, seq):
    it = iter(seq)
    monkeypatch.setattr("builtins.input", lambda *a, **k: next(it, "2"))


def test_interactive_overwrite(tmp_path, monkeypatch, capsys):
    p = tmp_path / "x.md"
    p.write_text("old", encoding="utf-8")
    _answers(monkeypatch, ["1"])
    action, written = templates.safe_write_file(p, "new")
    assert action == "overwritten"
    assert p.read_text(encoding="utf-8") == "new"


def test_interactive_skip(tmp_path, monkeypatch, capsys):
    p = tmp_path / "x.md"
    p.write_text("old", encoding="utf-8")
    _answers(monkeypatch, ["2"])
    action, written = templates.safe_write_file(p, "new")
    assert action == "skipped"
    assert p.read_text(encoding="utf-8") == "old"


def test_interactive_backup(tmp_path, monkeypatch, capsys):
    p = tmp_path / "x.md"
    p.write_text("old", encoding="utf-8")
    _answers(monkeypatch, ["3"])
    action, written = templates.safe_write_file(p, "new")
    assert action == "backed_up"
    assert p.read_text(encoding="utf-8") == "new"
    assert (tmp_path / "x.md.bak").read_text(encoding="utf-8") == "old"


def test_interactive_diff_then_choice(tmp_path, monkeypatch, capsys):
    p = tmp_path / "x.md"
    p.write_text("old", encoding="utf-8")
    # "4" shows the diff and re-prompts, then "9" is invalid and re-prompts, then "2".
    _answers(monkeypatch, ["4", "9", "2"])
    action, written = templates.safe_write_file(p, "new")
    assert action == "skipped"
    out = capsys.readouterr().out
    assert "Current Content" in out
