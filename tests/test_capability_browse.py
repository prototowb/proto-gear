"""Tests for the interactive capability browser — bare `pg capabilities` (§5.7).

Mirrors the agent-browser contract (PROTO-080): pure `_collect_*` data, a
non-TTY fallback to `pg capabilities list`, and an interactive loop driven by a
scripted fake `questionary`.
"""

import argparse
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import cli_commands as cc


def _args(**kw):
    return argparse.Namespace(**kw)


class TestCollectCapabilityEntries:
    def test_grouped_and_nonempty(self):
        entries = cc._collect_capability_entries()
        assert entries
        types = [e["type"] for e in entries]
        # Skills first, then workflows, then commands (stable group order).
        assert types == sorted(
            types, key=lambda t: {"skill": 0, "workflow": 1, "command": 2}.get(t, 9)
        )
        assert {"skill", "workflow", "command"} <= set(types)

    def test_label_has_type_and_short_id(self):
        label = cc._capability_entry_label(
            {
                "id": "skills/testing",
                "short_id": "testing",
                "type": "skill",
                "name": "TDD",
                "status": "stable",
            }
        )
        assert "skill" in label and "testing" in label


class TestBrowseFallback:
    def test_non_interactive_falls_back_to_list(self, monkeypatch):
        called = {}

        def fake_list(args):
            called["hit"] = True
            return 0

        monkeypatch.setattr(cc, "cmd_capabilities_list", fake_list)
        rc = cc.cmd_capabilities_browse(_args(capabilities_command=None))
        assert rc == 0 and called.get("hit") is True


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

    def test_view_then_quit(self, monkeypatch, capsys):
        self._make_tty(monkeypatch)
        fake = _FakeQuestionary(selects=[0, "__quit__"], confirms=[False])
        monkeypatch.setitem(sys.modules, "questionary", fake)
        rc = cc.cmd_capabilities_browse(_args(capabilities_command=None))
        out = capsys.readouterr().out
        assert rc == 0
        assert fake.select_calls == 2  # viewed one, re-prompted, quit
        assert "===" in out  # capability detail header was shown

    def test_tree_dispatch_on_confirm(self, monkeypatch):
        self._make_tty(monkeypatch)
        fake = _FakeQuestionary(selects=[0, "__quit__"], confirms=[True])
        monkeypatch.setitem(sys.modules, "questionary", fake)

        tree_seen = {}

        def fake_tree(args):
            tree_seen["id"] = args.capability_id
            return 0

        monkeypatch.setattr(cc, "cmd_capabilities_tree", fake_tree)
        rc = cc.cmd_capabilities_browse(_args(capabilities_command=None))
        assert rc == 0
        assert fake.confirm_calls == 1
        assert tree_seen.get("id")  # tree dispatched with a capability id
