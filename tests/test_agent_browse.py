"""Tests for the interactive agent browser — bare `pg agent` (PROTO-080, §5.7).

`cmd_agent_browse` is the UI-first entry point: it assembles installed +
available agents and, in a TTY with `questionary`, lets the user navigate and
pick one to view/install. Without a TTY (tests, CI, pipes) it must fall back to
the static `pg agent list`. The data assembly is pure and unit-tested; the
interactive loop is driven with a scripted fake `questionary`.
"""

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import cli_commands as cc


def _args(**kw):
    return argparse.Namespace(**kw)


class TestCollectAgentEntries:
    def test_available_only_when_nothing_installed(self, tmp_path, monkeypatch):
        # No .proto-gear here → no installed agents; entries are the real
        # bundled agents, all marked available.
        monkeypatch.chdir(tmp_path)
        entries = cc._collect_agent_entries(
            cc.get_agents_dir(), cc.get_capabilities_dir()
        )
        assert entries, "bundled agents should always be discoverable"
        assert all(e["kind"] == "available" for e in entries)
        assert all(e["status"] is None for e in entries)

    def test_label_marks_available_not_installed(self):
        label = cc._agent_entry_label(
            {
                "kind": "available",
                "name": "deploy-agent",
                "module": "devops",
                "description": "d",
                "status": None,
            }
        )
        assert "deploy-agent" in label and "not installed" in label


class TestBrowseFallback:
    def test_non_interactive_falls_back_to_list(self, tmp_path, monkeypatch):
        # pytest stdio is not a TTY → browse must delegate to cmd_agent_list.
        monkeypatch.chdir(tmp_path)
        called = {}

        def fake_list(args):
            called["hit"] = True
            return 0

        monkeypatch.setattr(cc, "cmd_agent_list", fake_list)
        rc = cc.cmd_agent_browse(_args(agent_command=None))
        assert rc == 0 and called.get("hit") is True


# ── Scripted fake questionary to drive the interactive loop ──────────────────


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
    """Returns scripted answers for successive select()/confirm() calls."""

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

    def test_view_available_then_quit(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        self._make_tty(monkeypatch)
        # Select entry 0 (an available bundled agent), decline install, then quit.
        fake = _FakeQuestionary(selects=[0, "__quit__"], confirms=[False])
        monkeypatch.setitem(sys.modules, "questionary", fake)

        rc = cc.cmd_agent_browse(_args(agent_command=None))
        out = capsys.readouterr().out
        assert rc == 0
        assert fake.select_calls == 2  # viewed once, then re-prompted → quit
        assert "not installed" in out  # available-agent detail was shown

    def test_install_dispatch_on_confirm(self, tmp_path, monkeypatch):
        # A real .proto-gear/agents so install succeeds, then quit.
        (tmp_path / ".proto-gear" / "agents").mkdir(parents=True)
        monkeypatch.chdir(tmp_path)
        self._make_tty(monkeypatch)
        fake = _FakeQuestionary(selects=[0, "__quit__"], confirms=[True])
        monkeypatch.setitem(sys.modules, "questionary", fake)

        installed = {}

        def fake_install(args):
            installed["name"] = args.name
            return 0

        monkeypatch.setattr(cc, "cmd_agent_install", fake_install)
        rc = cc.cmd_agent_browse(_args(agent_command=None))
        assert rc == 0
        assert fake.confirm_calls == 1
        assert installed.get("name")  # install was dispatched with a name
