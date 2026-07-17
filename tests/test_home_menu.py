"""Tests for the top-level interactive home menu — bare `pg` (PROTO-082, §5.7).

The menu routes to the sub-views (status, browsers, tickets, release). It is
only reached in a TTY with `questionary`; here we drive it with a scripted fake
`questionary` and assert each selection dispatches to the right handler. The
non-TTY fallback (classic splash) lives in cli.app and is covered there.
"""

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import cli_commands as cc


def _args(**kw):
    return argparse.Namespace(**kw)


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

    def __init__(self, selects, texts=None):
        self._selects = list(selects)
        self._texts = list(texts or [])

    def select(self, *a, **k):
        return _FakePrompt(self._selects.pop(0))

    def text(self, *a, **k):
        return _FakePrompt(self._texts.pop(0))


class TestHomeMenu:
    def _install(self, monkeypatch, fake, recorder):
        monkeypatch.setitem(sys.modules, "questionary", fake)
        # Stub the leaf handlers so we assert routing without side effects.
        from proto_gear_pkg.modules.engineering import status_commands as sc

        monkeypatch.setattr(sc, "cmd_status", lambda a: recorder.append("status") or 0)
        monkeypatch.setattr(
            sc, "cmd_ticket_list", lambda a: recorder.append("tickets") or 0
        )
        monkeypatch.setattr(
            cc, "cmd_capabilities_browse", lambda a: recorder.append("caps") or 0
        )
        monkeypatch.setattr(
            cc, "cmd_agent_browse", lambda a: recorder.append("agents") or 0
        )
        monkeypatch.setattr(
            cc, "cmd_release", lambda a: recorder.append(("release", a.release_id)) or 0
        )

    def test_quit_immediately(self, monkeypatch):
        rec = []
        self._install(monkeypatch, _FakeQuestionary(selects=["__quit__"]), rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert rec == []

    def test_routes_each_destination(self, monkeypatch):
        rec = []
        # Capabilities/Agents stay top-level; Tickets is now a sub-screen, so
        # reaching the list means: tickets → list → Back → quit.
        fake = _FakeQuestionary(
            selects=[
                "status",
                "capabilities",
                "agents",
                "tickets",
                "list",
                "__back__",
                "__quit__",
            ]
        )
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert rec == ["status", "caps", "agents", "tickets"]

    def test_back_from_submenu_returns_to_root(self, monkeypatch):
        # Enter Tickets, go Back without acting, then quit from the root.
        rec = []
        fake = _FakeQuestionary(selects=["tickets", "__back__", "__quit__"])
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert rec == []

    def test_release_prompts_for_label(self, monkeypatch):
        rec = []
        fake = _FakeQuestionary(selects=["release", "__quit__"], texts=["v0.10.0"])
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert rec == [("release", "v0.10.0")]

    def test_setup_sync_shells_out(self, monkeypatch):
        # Setup is a sub-screen; each row spawns the real subcommand via _run_pg.
        rec = []
        calls = []
        monkeypatch.setattr(cc, "_run_pg", lambda *a: calls.append(a))
        fake = _FakeQuestionary(selects=["setup", "sync", "__back__", "__quit__"])
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert calls == [("sync-context",)]

    def test_setup_init_and_hooks_route(self, monkeypatch):
        rec = []
        calls = []
        monkeypatch.setattr(cc, "_run_pg", lambda *a: calls.append(a))
        fake = _FakeQuestionary(
            selects=["setup", "init", "hooks", "__back__", "__quit__"]
        )
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert calls == [("init",), ("hooks", "install")]

    def test_release_blank_label_skips(self, monkeypatch):
        rec = []
        fake = _FakeQuestionary(selects=["release", "__quit__"], texts=["   "])
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert rec == []  # blank label → no release dispatch
