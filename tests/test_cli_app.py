"""Tests for pg dispatch — cli.app.main() (PROTO-050 coverage).

Drives main() by setting sys.argv, the same surface a shell invocation hits.
Covers the command routing branches for the non-interactive commands (init's
interactive wizard path is out of scope — exercised via --no-interactive only).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.cli import app


def run(argv, monkeypatch):
    """Invoke main() with argv; return its exit code (0 if it returns normally)."""
    monkeypatch.setattr(sys, "argv", ["pg"] + argv)
    try:
        app.main()
        return 0
    except SystemExit as e:
        if e.code is None:
            return 0
        return e.code if isinstance(e.code, int) else 1


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / "PROJECT_STATUS.md").write_text(
        '## Current State\n\n```yaml\nticket_prefix: "P"\nlast_ticket_id: 0\n```\n\n'
        "## Active Tickets\n\n| ID | Title | Type | Status | Branch | Assignee |\n"
        "|----|----|----|----|----|----|\n\n## Completed Tickets\n",
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestDispatch:
    def test_no_command_shows_welcome(self, monkeypatch, capsys):
        assert run([], monkeypatch) == 0
        assert "Proto Gear" in capsys.readouterr().out

    def test_help(self, monkeypatch, capsys):
        assert run(["help"], monkeypatch) == 0

    def test_version(self, monkeypatch, capsys):
        assert run(["--version"], monkeypatch) == 0
        assert "Proto Gear" in capsys.readouterr().out

    def test_capabilities_list(self, monkeypatch, capsys):
        assert run(["capabilities", "list"], monkeypatch) == 0

    def test_capabilities_no_subcommand(self, monkeypatch, capsys):
        assert run(["capabilities"], monkeypatch) == 1

    def test_agent_no_subcommand(self, monkeypatch, capsys):
        assert run(["agent"], monkeypatch) == 1

    def test_module_list(self, monkeypatch, capsys):
        assert run(["module", "list"], monkeypatch) == 0
        assert "engineering" in capsys.readouterr().out

    def test_module_show(self, monkeypatch, capsys):
        assert run(["module", "show", "engineering"], monkeypatch) == 0

    def test_module_no_subcommand(self, monkeypatch, capsys):
        assert run(["module"], monkeypatch) == 1

    def test_status(self, project, monkeypatch, capsys):
        assert run(["status"], monkeypatch) == 0

    def test_status_missing_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        assert run(["status"], monkeypatch) == 1

    def test_ticket_list(self, project, monkeypatch, capsys):
        assert run(["ticket", "list"], monkeypatch) == 0

    def test_ticket_no_subcommand(self, project, monkeypatch, capsys):
        assert run(["ticket"], monkeypatch) == 1

    def test_ticket_create_then_status(self, project, monkeypatch, capsys):
        assert run(["ticket", "create", "Hello", "--type", "task"], monkeypatch) == 0
        assert "P-001" in capsys.readouterr().out

    def test_suggest(self, project, monkeypatch, capsys):
        assert run(["suggest", "write", "tests"], monkeypatch) == 0

    def test_suggest_json(self, project, monkeypatch, capsys):
        assert run(["suggest", "deploy", "--json"], monkeypatch) == 0

    def test_doctor(self, project, monkeypatch, capsys):
        # exit code may be 0 or 1 depending on drift; just ensure it runs
        rc = run(["doctor"], monkeypatch)
        assert rc in (0, 1)

    def test_doctor_json(self, project, monkeypatch, capsys):
        rc = run(["doctor", "--json"], monkeypatch)
        assert rc in (0, 1)

    def test_context_regenerate(self, project, monkeypatch, capsys):
        assert run(["context", "--regenerate"], monkeypatch) == 0

    def test_sync_indexes_missing(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        assert run(["sync-indexes"], monkeypatch) == 1

    def test_sync_context(self, project, monkeypatch, capsys):
        assert run(["sync-context", "--dry-run"], monkeypatch) == 0

    def test_init_surface_engineering(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        assert run(["--module", "engineering", "init-surface"], monkeypatch) == 0
        assert (tmp_path / "PROJECT_STATUS.md").exists()

    def test_init_dry_run_non_interactive(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = run(["init", "--no-interactive", "--dry-run"], monkeypatch)
        assert rc == 0


class TestSyncPaths:
    """Commands that operate on a fully-initialised project (.proto-gear/ present)."""

    @pytest.fixture
    def initialised(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Full init with capabilities lays down .proto-gear/ + host files.
        run(["init", "--no-interactive", "--with-capabilities"], monkeypatch)
        return tmp_path

    def test_sync_context_updates_hosts(self, initialised, monkeypatch, capsys):
        assert run(["sync-context"], monkeypatch) == 0

    def test_sync_indexes_present(self, initialised, monkeypatch, capsys):
        assert run(["sync-indexes"], monkeypatch) == 0

    def test_doctor_fix(self, initialised, monkeypatch, capsys):
        rc = run(["doctor", "--fix"], monkeypatch)
        assert rc in (0, 1)
