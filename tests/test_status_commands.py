"""Tests for pg status / pg ticket handlers (PROTO-050 coverage).

status_commands operates on PROJECT_STATUS.md as the single source of truth —
pure text parsing + mutation, non-interactive, safe for agents. These tests
exercise the parser, the row-mutation helpers, and all four command handlers
against a temp PROJECT_STATUS.md.
"""

import argparse
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.modules.engineering import status_commands as sc

STATUS_TEMPLATE = """# PROJECT STATUS

## Current State

```yaml
project_phase: "Production"
ticket_prefix: "PROTO"
last_ticket_id: 5
current_sprint: "3"
sprint_type: "feature_development"
```

## Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROTO-004 | Existing feature | feature | IN_PROGRESS | feature/x | ann |
| PROTO-005 | Another task | task | PENDING | task/y | |

## Blocked Tickets

| ID | Title | Status | Blocker |
|----|-------|--------|---------|
| PROTO-003 | Stuck item | BLOCKED | waiting on API |

## Completed Tickets

| ID | Title | Completed | PR/Commit |
|----|-------|-----------|-----------|
| PROTO-001 | First thing | 2026-01-01 | v0.1.0 |
"""


@pytest.fixture
def project(tmp_path, monkeypatch):
    (tmp_path / "PROJECT_STATUS.md").write_text(STATUS_TEMPLATE, encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return tmp_path


def _args(**kw):
    return argparse.Namespace(**kw)


class TestProjectState:
    def test_parses_yaml_and_tables(self, project):
        state = sc.ProjectState(project / "PROJECT_STATUS.md")
        assert state.ticket_prefix == "PROTO"
        assert state.last_ticket_id == 5
        assert state.project_phase == "Production"
        assert state.current_sprint == "3"
        assert len(state.active) == 2
        assert state.active[0]["ID"] == "PROTO-004"
        assert len(state.blocked) == 1
        assert len(state.completed) == 1

    def test_infers_prefix_from_table_when_missing(self, tmp_path):
        text = STATUS_TEMPLATE.replace('ticket_prefix: "PROTO"\n', "").replace(
            "last_ticket_id: 5\n", ""
        )
        p = tmp_path / "PROJECT_STATUS.md"
        p.write_text(text, encoding="utf-8")
        state = sc.ProjectState(p)
        assert state.ticket_prefix == "PROTO"
        assert state.last_ticket_id == 5  # inferred from highest ID seen

    def test_defaults_to_TICKET_when_no_ids(self, tmp_path):
        p = tmp_path / "PROJECT_STATUS.md"
        p.write_text("# empty\n\n## Active Tickets\n", encoding="utf-8")
        state = sc.ProjectState(p)
        assert state.ticket_prefix == "TICKET"
        assert state.active == []


class TestMutationHelpers:
    def test_set_last_ticket_id(self):
        assert "last_ticket_id: 9" in sc._set_last_ticket_id(
            "x\nlast_ticket_id: 5\ny", 9
        )

    def test_append_row_inserts_after_last(self, project):
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        new = sc._append_row(
            text, "Active Tickets", "| PROTO-006 | New | task | PENDING | b | |"
        )
        assert "PROTO-006" in new
        # inserted within the Active section, before Blocked
        assert new.index("PROTO-006") < new.index("Blocked Tickets")

    def test_remove_active_row_returns_removed(self, project):
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        new, removed = sc._remove_active_row(text, "PROTO-004")
        assert removed is not None
        assert removed["Title"] == "Existing feature"
        assert "PROTO-004" not in new

    def test_remove_active_row_missing(self, project):
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        new, removed = sc._remove_active_row(text, "PROTO-999")
        assert removed is None

    def test_update_status_inline(self, project):
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        new = sc._update_status_inline(text, "PROTO-005", "IN_PROGRESS")
        assert "| PROTO-005 | Another task | task | IN_PROGRESS |" in new


class TestCmdStatus:
    def test_text_output(self, project, capsys):
        rc = sc.cmd_status(_args(json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "Project Status" in out
        assert "PROTO-004" in out
        assert "PROTO-006" in out  # next id (last 5 + 1)

    def test_json_output(self, project, capsys):
        rc = sc.cmd_status(_args(json=True))
        out = capsys.readouterr().out
        assert rc == 0
        data = json.loads(out)
        assert data["ticket_prefix"] == "PROTO"
        assert data["next_ticket_id"] == "PROTO-006"
        assert data["completed_count"] == 1
        assert len(data["active"]) == 2

    def test_missing_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = sc.cmd_status(_args(json=False))
        assert rc == 1
        assert "not found" in capsys.readouterr().err


class TestCmdTicketCreate:
    def test_creates_and_prints_id(self, project, capsys):
        rc = sc.cmd_ticket_create(
            _args(title="Fix login", type="bugfix", assignee="bob")
        )
        out = capsys.readouterr().out.strip()
        assert rc == 0
        assert out == "PROTO-006"
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        assert "| PROTO-006 | Fix login | bugfix | PENDING |" in text
        assert "last_ticket_id: 6" in text

    def test_invalid_type(self, project, capsys):
        rc = sc.cmd_ticket_create(_args(title="X", type="nonsense", assignee=""))
        assert rc == 1
        assert "--type must be one of" in capsys.readouterr().err

    def test_missing_file(self, tmp_path, monkeypatch, capsys):
        monkeypatch.chdir(tmp_path)
        rc = sc.cmd_ticket_create(_args(title="X", type="task", assignee=""))
        assert rc == 1


class TestCmdTicketUpdate:
    def test_inline_status_change(self, project, capsys):
        rc = sc.cmd_ticket_update(_args(ticket_id="proto-005", status="IN_PROGRESS"))
        assert rc == 0
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        assert "| PROTO-005 | Another task | task | IN_PROGRESS |" in text

    def test_completed_moves_to_completed_table(self, project, capsys):
        rc = sc.cmd_ticket_update(_args(ticket_id="PROTO-004", status="COMPLETED"))
        assert rc == 0
        text = (project / "PROJECT_STATUS.md").read_text(encoding="utf-8")
        active = text.split("## Blocked")[0]
        assert "PROTO-004" not in active
        assert "PROTO-004" in text  # now in completed table

    def test_invalid_status(self, project, capsys):
        rc = sc.cmd_ticket_update(_args(ticket_id="PROTO-004", status="WAT"))
        assert rc == 1
        assert "--status must be one of" in capsys.readouterr().err

    def test_ticket_not_found(self, project, capsys):
        rc = sc.cmd_ticket_update(_args(ticket_id="PROTO-999", status="IN_PROGRESS"))
        assert rc == 1
        assert "not found" in capsys.readouterr().err

    def test_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert sc.cmd_ticket_update(_args(ticket_id="X-1", status="IN_PROGRESS")) == 1


class TestCmdTicketList:
    def test_all_active_and_blocked(self, project, capsys):
        rc = sc.cmd_ticket_list(_args(status="", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "PROTO-004" in out and "PROTO-003" in out

    def test_filter_by_status(self, project, capsys):
        rc = sc.cmd_ticket_list(_args(status="PENDING", json=False))
        out = capsys.readouterr().out
        assert "PROTO-005" in out
        assert "PROTO-004" not in out

    def test_completed_filter(self, project, capsys):
        rc = sc.cmd_ticket_list(_args(status="COMPLETED", json=True))
        data = json.loads(capsys.readouterr().out)
        assert any(t["ID"] == "PROTO-001" for t in data)

    def test_json_output(self, project, capsys):
        rc = sc.cmd_ticket_list(_args(status="", json=True))
        data = json.loads(capsys.readouterr().out)
        assert len(data) == 3  # 2 active + 1 blocked

    def test_empty(self, tmp_path, monkeypatch, capsys):
        (tmp_path / "PROJECT_STATUS.md").write_text(
            "# x\n\n## Active Tickets\n\n## Blocked Tickets\n", encoding="utf-8"
        )
        monkeypatch.chdir(tmp_path)
        rc = sc.cmd_ticket_list(_args(status="", json=False))
        assert rc == 0
        assert "No tickets found" in capsys.readouterr().out

    def test_missing_file(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert sc.cmd_ticket_list(_args(status="", json=False)) == 1


# ─────────────────────────────────────────────────────────────────────────────
# PROTO-078: fenced "**Example**:" rows must not parse/mutate as real tickets.
# The generated PROJECT_STATUS.md ships an example row inside a ```markdown
# fence, with the project's real prefix substituted in.
# ─────────────────────────────────────────────────────────────────────────────

FENCED_EXAMPLE_STATUS = """# PROJECT STATUS

## Current State

```yaml
project_phase: "Development"
ticket_prefix: "ARSENAL"
last_ticket_id: 0
```

## Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
_No active tickets yet._

**Example**:
```markdown
| ARSENAL-001 | Add user authentication | feature | IN_PROGRESS | feature/ARSENAL-001-add-user-auth | Lead AI |
```

## Completed Tickets

| ID | Title | Completed | PR | Reviewed by |
|----|-------|-----------|-----|-------------|
| INIT-001 | Proto Gear framework integrated | 2026-07-12 | - | - |
"""


class TestFencedExampleIgnored:
    def test_parse_skips_fenced_example(self, tmp_path):
        (tmp_path / "PROJECT_STATUS.md").write_text(
            FENCED_EXAMPLE_STATUS, encoding="utf-8"
        )
        state = sc.ProjectState(tmp_path / "PROJECT_STATUS.md")
        assert state.active == []  # fenced ARSENAL-001 must not count
        assert state.last_ticket_id == 0  # not inferred from the example

    def test_update_status_leaves_fenced_example_untouched(self):
        out = sc._update_status_inline(
            FENCED_EXAMPLE_STATUS, "ARSENAL-001", "COMPLETED"
        )
        # The example row inside the fence keeps its original IN_PROGRESS status.
        assert (
            "| ARSENAL-001 | Add user authentication | feature | IN_PROGRESS |" in out
        )
        assert "COMPLETED" not in out


class TestExtractToleratesInlineComments:
    """PROTO-078: Current State YAML ships inline `# comments`."""

    def test_prefix_and_id_parse_past_comments(self, tmp_path):
        text = (
            "# x\n\n## Current State\n\n```yaml\n"
            'project_phase: "Development"  # Planning, Development, ...\n'
            "current_sprint: null  # null for pre-development\n"
            "last_ticket_id: 0  # Next ticket will increment from this\n"
            'ticket_prefix: "ARSENAL"  # e.g., "PROJ", "MCP", etc.\n'
            "```\n\n## Active Tickets\n\n## Completed Tickets\n"
        )
        p = tmp_path / "PROJECT_STATUS.md"
        p.write_text(text, encoding="utf-8")
        state = sc.ProjectState(p)
        assert state.ticket_prefix == "ARSENAL"
        assert state.last_ticket_id == 0
