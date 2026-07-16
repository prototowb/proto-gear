"""Tests for the interactive lessons browser (`pg lessons`, §5.7).

`cmd_lessons_browse` is the UI-first entry for bare `pg lessons`: navigate the
accumulated-knowledge layer and read a lesson in full. Without a TTY it falls
back to `pg lessons list`. Data assembly is pure; the loop is driven with a
scripted fake `questionary`, mirroring test_orchestration_browse.py.
"""

import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import cli_commands as cc


def _args(**kw):
    return argparse.Namespace(**kw)


def _write_lesson(project_dir, filename, title, summary, body="Body text."):
    d = project_dir / ".proto-gear" / "lessons"
    d.mkdir(parents=True, exist_ok=True)
    (d / filename).write_text(f"# {title}\n\n> {summary}\n\n{body}\n", encoding="utf-8")
    return d / filename


class TestCollectLessonEntries:
    def test_empty_when_no_dir(self, tmp_path):
        assert cc._collect_lesson_entries(tmp_path) == []

    def test_entries_parsed_and_sorted(self, tmp_path):
        _write_lesson(tmp_path, "b.md", "Beta", "second")
        _write_lesson(tmp_path, "a.md", "Alpha", "first")
        entries = cc._collect_lesson_entries(tmp_path)
        assert [e["filename"] for e in entries] == ["a.md", "b.md"]
        assert entries[0]["title"] == "Alpha"
        assert entries[0]["summary"] == "first"
        assert entries[0]["path"].endswith("a.md")

    def test_malformed_lesson_skipped(self, tmp_path):
        d = tmp_path / ".proto-gear" / "lessons"
        d.mkdir(parents=True)
        (d / "bad.md").write_text("no title here\n", encoding="utf-8")
        _write_lesson(tmp_path, "good.md", "Good", "ok")
        entries = cc._collect_lesson_entries(tmp_path)
        assert [e["filename"] for e in entries] == ["good.md"]

    def test_index_and_readme_are_not_lessons(self, tmp_path):
        _write_lesson(tmp_path, "real.md", "Real", "s")
        d = tmp_path / ".proto-gear" / "lessons"
        (d / "INDEX.md").write_text("# Index\n> x\n", encoding="utf-8")
        (d / "README.md").write_text("# Readme\n> x\n", encoding="utf-8")
        entries = cc._collect_lesson_entries(tmp_path)
        assert [e["filename"] for e in entries] == ["real.md"]


class TestLessonEntryLabel:
    def test_label_includes_title_and_summary(self):
        label = cc._lesson_entry_label(
            {"filename": "a.md", "title": "My Lesson", "summary": "the gist"}
        )
        assert "My Lesson" in label
        assert "the gist" in label

    def test_label_without_summary(self):
        label = cc._lesson_entry_label(
            {"filename": "a.md", "title": "Bare", "summary": ""}
        )
        assert "Bare" in label


class TestResolveLesson:
    def _entries(self):
        return [
            {
                "filename": "verify-with-pytest.md",
                "title": "Prefer Pytest",
                "summary": "s",
            },
            {"filename": "other.md", "title": "Other", "summary": "s"},
        ]

    def test_by_exact_filename(self):
        e = cc._resolve_lesson("verify-with-pytest.md", self._entries())
        assert e["filename"] == "verify-with-pytest.md"

    def test_by_filename_without_extension(self):
        e = cc._resolve_lesson("verify-with-pytest", self._entries())
        assert e["filename"] == "verify-with-pytest.md"

    def test_by_title_case_insensitive(self):
        e = cc._resolve_lesson("prefer pytest", self._entries())
        assert e["filename"] == "verify-with-pytest.md"

    def test_no_match(self):
        assert cc._resolve_lesson("nope", self._entries()) is None


class TestLessonsList:
    def test_empty_message(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_lessons_list(_args(json=False))
        assert rc == 0
        assert "No lessons recorded yet" in capsys.readouterr().out

    def test_lists_titles(self, tmp_path, monkeypatch, capsys):
        _write_lesson(tmp_path, "a.md", "Alpha Lesson", "the alpha summary")
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_lessons_list(_args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Alpha Lesson" in out
        assert "the alpha summary" in out

    def test_json_output(self, tmp_path, monkeypatch, capsys):
        _write_lesson(tmp_path, "a.md", "Alpha", "s")
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_lessons_list(_args(json=True))
        out = capsys.readouterr().out
        assert rc == 0
        data = json.loads(out)
        assert data[0]["title"] == "Alpha"
        assert data[0]["filename"] == "a.md"


class TestLessonsShow:
    def test_prints_full_body(self, tmp_path, monkeypatch, capsys):
        _write_lesson(tmp_path, "a.md", "Alpha", "s", body="The full body here.")
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_lessons_show(_args(name="a"))
        out = capsys.readouterr().out
        assert rc == 0
        assert "The full body here." in out
        assert "# Alpha" in out  # the H1 from the file

    def test_missing_lesson_returns_1(self, tmp_path, monkeypatch, capsys):
        _write_lesson(tmp_path, "a.md", "Alpha", "s")
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_lessons_show(_args(name="nope"))
        assert rc == 1
        assert "No lesson matching" in capsys.readouterr().out

    def test_no_lessons_at_all(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = cc.cmd_lessons_show(_args(name="anything"))
        assert rc == 0
        assert "No lessons recorded yet" in capsys.readouterr().out


class TestBrowseFallback:
    def test_non_interactive_falls_back_to_list(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys.stdin, "isatty", lambda: False)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
        called = {}

        def fake_list(args):
            called["hit"] = True
            return 0

        monkeypatch.setattr(cc, "cmd_lessons_list", fake_list)
        rc = cc.cmd_lessons_browse(_args(lessons_command=None, json=False))
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

    def __init__(self, selects):
        self._selects = list(selects)
        self.select_calls = 0

    def select(self, *a, **k):
        self.select_calls += 1
        return _FakePrompt(self._selects.pop(0))


class TestBrowseInteractive:
    def _make_tty(self, monkeypatch):
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

    def test_empty_is_silent_and_ok(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        self._make_tty(monkeypatch)
        monkeypatch.setitem(sys.modules, "questionary", _FakeQuestionary(selects=[]))
        rc = cc.cmd_lessons_browse(_args(lessons_command=None, json=False))
        assert rc == 0
        assert "No lessons recorded yet" in capsys.readouterr().out

    def test_view_then_quit(self, tmp_path, monkeypatch, capsys):
        _write_lesson(tmp_path, "a.md", "Alpha", "s", body="Readable body.")
        monkeypatch.chdir(tmp_path)
        self._make_tty(monkeypatch)
        # View entry 0, then quit.
        fake = _FakeQuestionary(selects=[0, "__quit__"])
        monkeypatch.setitem(sys.modules, "questionary", fake)

        rc = cc.cmd_lessons_browse(_args(lessons_command=None, json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert fake.select_calls == 2  # viewed once, re-prompted → quit
        assert "Readable body." in out


class TestHomeMenuRoute:
    """The home menu routes 'lessons' → the lessons browser."""

    def test_home_menu_lessons_route(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(sys.stdin, "isatty", lambda: True)
        monkeypatch.setattr(sys.stdout, "isatty", lambda: True)

        recorder = {}

        class _HomeFake:
            Choice = _FakeChoice

            def __init__(self):
                self._selects = ["lessons", "__quit__"]

            def select(self, *a, **k):
                return _FakePrompt(self._selects.pop(0))

        monkeypatch.setitem(sys.modules, "questionary", _HomeFake())
        monkeypatch.setattr(
            cc, "cmd_lessons_browse", lambda args: recorder.setdefault("hit", True)
        )
        rc = cc.cmd_home_menu(_args())
        assert rc == 0
        assert recorder.get("hit") is True
