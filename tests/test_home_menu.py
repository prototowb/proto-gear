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

    def test_setup_hooks_route(self, monkeypatch):
        # Init/re-init is guided (see TestReinit); hooks still shells out plainly.
        rec = []
        calls = []
        monkeypatch.setattr(cc, "_run_pg", lambda *a: calls.append(a))
        fake = _FakeQuestionary(selects=["setup", "hooks", "__back__", "__quit__"])
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert calls == [("hooks", "install")]

    def test_release_blank_label_skips(self, monkeypatch):
        rec = []
        fake = _FakeQuestionary(selects=["release", "__quit__"], texts=["   "])
        self._install(monkeypatch, fake, rec)
        assert cc.cmd_home_menu(_args(command=None)) == 0
        assert rec == []  # blank label → no release dispatch


class TestReinitSummary:
    """Pure install-state summary shown before the guided re-init choice."""

    def test_counts_present_and_missing(self):
        expected = ["A.md", "B.md", "C.md"]
        env = {
            "existing_files": ["A.md", "C.md", "X.md"],
            "existing_capabilities": True,
        }
        s = cc._reinit_summary(env, expected, {})
        assert s["present"] == 2  # A, C — X.md is outside the expected set
        assert s["total"] == 3
        assert s["missing"] == ["B.md"]
        assert s["capabilities"] is True
        assert s["resync"] == 0

    def test_resync_counts_sync_actions(self):
        env = {"existing_files": [], "existing_capabilities": False}
        preview = {
            "CLAUDE.md": "would_update",
            "AGENTS.md": "unchanged",
            ".cursorrules": "would_create",
        }
        s = cc._reinit_summary(env, ["AGENTS.md"], preview)
        assert s["resync"] == 2
        assert s["capabilities"] is False


class TestReinit:
    """Guided init/re-init action: fresh → wizard; existing → pane + choice."""

    def _patch_existing(self, monkeypatch, existing, calls, choice):
        from proto_gear_pkg.modules.engineering import detection

        monkeypatch.setattr(
            detection, "detect_existing_environment", lambda p: existing
        )
        monkeypatch.setattr(cc, "_sync_dry_run_preview", lambda: {})
        monkeypatch.setattr(cc, "_run_pg", lambda *a: calls.append(a))
        monkeypatch.setitem(sys.modules, "questionary", _FakeQuestionary([choice]))

    def test_fresh_project_runs_init_wizard(self, monkeypatch):
        from proto_gear_pkg.modules.engineering import detection

        calls = []
        monkeypatch.setattr(
            detection,
            "detect_existing_environment",
            lambda p: {
                "is_existing": False,
                "existing_files": [],
                "existing_capabilities": False,
            },
        )
        monkeypatch.setattr(cc, "_run_pg", lambda *a: calls.append(a))
        # No questionary prompt should be reached on the fresh path.
        monkeypatch.setitem(sys.modules, "questionary", _FakeQuestionary([]))
        cc._action_init_or_reinit()
        assert calls == [("init",)]

    def test_reinit_refresh_resyncs(self, monkeypatch):
        calls = []
        env = {
            "is_existing": True,
            "existing_files": ["AGENTS.md"],
            "existing_capabilities": True,
        }
        self._patch_existing(monkeypatch, env, calls, "refresh")
        cc._action_init_or_reinit()
        assert calls == [("sync-context",)]

    def test_reinit_full_runs_wizard(self, monkeypatch):
        calls = []
        env = {
            "is_existing": True,
            "existing_files": [],
            "existing_capabilities": False,
        }
        self._patch_existing(monkeypatch, env, calls, "reinit")
        cc._action_init_or_reinit()
        assert calls == [("init",)]

    def test_reinit_cancel_does_nothing(self, monkeypatch):
        calls = []
        env = {
            "is_existing": True,
            "existing_files": [],
            "existing_capabilities": False,
        }
        self._patch_existing(monkeypatch, env, calls, "cancel")
        cc._action_init_or_reinit()
        assert calls == []
