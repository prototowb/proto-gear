"""Tests for the interactive orchestration-paradigm browser (PROTO-091, §5.7).

`cmd_orchestration_browse` is the UI-first entry for bare `pg orchestration`:
navigate the paradigm pool and view/install one. Without a TTY it falls back to
`pg orchestration list`. Data assembly is pure; the loop is driven with a
scripted fake `questionary`, mirroring test_agent_browse.py.
"""

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import cli_commands as cc


def _args(**kw):
    return argparse.Namespace(**kw)


class TestCollectParadigmEntries:
    def test_pool_entries_when_nothing_installed(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        entries = cc._collect_paradigm_entries(tmp_path)
        assert entries, "bundled paradigms should always be discoverable"
        assert all(e["installed"] is False for e in entries)
        ids = {e["id"] for e in entries}
        assert {"dynamic", "driver-reviewer"} <= ids

    def test_label_shows_roles_and_tiers(self):
        label = cc._paradigm_entry_label(
            {
                "id": "driver-reviewer",
                "name": "Driver–Reviewer",
                "description": "d",
                "roles": [("driver", "balanced"), ("reviewer", "deep")],
                "selectable_by": ["user", "agent"],
                "installed": False,
                "module": None,
            }
        )
        assert "driver-reviewer" in label
        assert "reviewer·deep" in label


class TestBrowseFallback:
    def test_non_interactive_falls_back_to_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        called = {}

        def fake_list(args):
            called["hit"] = True
            return 0

        monkeypatch.setattr(cc, "cmd_orchestration_list", fake_list)
        rc = cc.cmd_orchestration_browse(_args(orchestration_command=None))
        assert rc == 0 and called.get("hit") is True


# ── Scripted fake questionary ────────────────────────────────────────────────


class _FakeChoice:
    def __init__(self, title, value):
        self.title = title
        self.value = value


class _FakePrompt:
    def __init__(self, answer):
        self._answer = answer

    def ask(self):
        return self._answer


class _FakeQuestionary:
    Choice = _FakeChoice

    def __init__(self, selects, confirms):
        self._selects = list(selects)
        self._confirms = list(confirms)
        self.select_calls = 0
        self.confirm_calls = 0

    def select(self, *a, **k):
        self.select_calls += 1
        return _FakePrompt(self._selects.pop(0))

    def confirm(self, *a, **k):
        self.confirm_calls += 1
        return _FakePrompt(self._confirms.pop(0))


class TestBrowseInteractive:
    def _make_tty(self, monkeypatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    def test_view_then_quit(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        self._make_tty(monkeypatch)
        # View entry 0, decline install, then quit.
        fake = _FakeQuestionary(selects=[0, "__quit__"], confirms=[False])
        monkeypatch.setitem(sys.modules, "questionary", fake)

        rc = cc.cmd_orchestration_browse(_args(orchestration_command=None))
        out = capsys.readouterr().out
        assert rc == 0
        assert fake.select_calls == 2  # viewed once, re-prompted → quit
        assert "Roles:" in out  # a paradigm detail was rendered

    def test_install_dispatch_on_confirm(self, tmp_path, monkeypatch):
        (tmp_path / ".proto-gear").mkdir()
        monkeypatch.chdir(tmp_path)
        self._make_tty(monkeypatch)
        fake = _FakeQuestionary(selects=[0, "__quit__"], confirms=[True])
        monkeypatch.setitem(sys.modules, "questionary", fake)

        installed = {}

        def fake_install(args):
            installed["id"] = args.id
            return 0

        monkeypatch.setattr(cc, "cmd_orchestration_install", fake_install)
        rc = cc.cmd_orchestration_browse(_args(orchestration_command=None))
        assert rc == 0
        assert fake.confirm_calls == 1
        assert installed.get("id")  # install dispatched with a paradigm id


class TestHomeMenuRoute:
    """The home menu routes 'paradigms' → the paradigm browser (PROTO-091)."""

    def test_home_menu_paradigms_route(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

        recorder = {}

        class _HomeFake:
            Choice = _FakeChoice

            def __init__(self):
                self._selects = ["paradigms", "__quit__"]

            def select(self, *a, **k):
                return _FakePrompt(self._selects.pop(0))

        monkeypatch.setitem(sys.modules, "questionary", _HomeFake())
        monkeypatch.setattr(
            cc,
            "cmd_orchestration_browse",
            lambda args: recorder.setdefault("hit", True),
        )
        rc = cc.cmd_home_menu(_args())
        assert rc == 0
        assert recorder.get("hit") is True
