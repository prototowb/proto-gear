"""Tests for the supervision inbox (PROTO-102, Phase D).

`module_core.inbox` scans every discipline's declared state surface for rows
sitting at a pending, required, human supervision gate — the cross-discipline
"what needs a human right now?" cockpit. Like `trace`/`release`, these tests
write real state surfaces into a tmp project and rely on the real bundled module
gates (qa-signoff, prod-approval, security-signoff, go-no-go, engineering's
pr-review/release approvals). Generic: a discipline joins the inbox by declaring
a required human gate + carrying its evidence column, no code change here.
"""

import argparse
import io
import json
import sys
from contextlib import redirect_stdout
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core import inbox


def _args(**kw):
    return argparse.Namespace(**kw)


def _qa(root: Path, rows: str):
    (root / "QA_QUEUE.md").write_text(
        "# QA\n\n| ID | Ref | Title | Area | Stage | Owner | Signed off by | Target |\n"
        "|----|-----|-------|------|-------|-------|---------------|--------|\n" + rows,
        encoding="utf-8",
    )


def _deploy(root: Path, rows: str):
    (root / "DEPLOY_QUEUE.md").write_text(
        "# Deploy\n\n| ID | Ref | Change | Environment | Stage | Owner | Approved by | Target |\n"
        "|----|-----|--------|-------------|-------|-------|-------------|--------|\n"
        + rows,
        encoding="utf-8",
    )


class TestCollectInbox:
    def test_pending_gate_surfaces_as_item(self, tmp_path):
        _qa(
            tmp_path,
            "| QA-1 | PROTO-1 | sweep | auth | in-test | ann | _(pending)_ | v1 |\n"
            "| QA-2 | PROTO-2 | done | api | signed-off | ann | ann | v1 |\n",
        )
        items = inbox.collect_inbox(tmp_path)
        assert len(items) == 1
        it = items[0]
        assert it["change"] == "QA-1"
        assert it["discipline"] == "qa"
        assert it["gate"] == "qa-signoff"
        assert it["ref"] == "PROTO-1"
        assert it["authority"] == "human"

    def test_signed_rows_are_not_in_inbox(self, tmp_path):
        _qa(
            tmp_path,
            "| QA-2 | PROTO-2 | done | api | signed-off | ann | ann | v1 |\n",
        )
        assert inbox.collect_inbox(tmp_path) == []

    def test_empty_evidence_cell_is_pending(self, tmp_path):
        # A blank Signed-off cell (not the literal "pending") still awaits a human.
        _qa(tmp_path, "| QA-3 | PROTO-3 | x | auth | in-test | ann |  | v1 |\n")
        items = inbox.collect_inbox(tmp_path)
        assert [i["change"] for i in items] == ["QA-3"]

    def test_row_with_id_and_ref_counted_once(self, tmp_path):
        # DEP-9 carries both its own ID and an upstream Ref; a naive per-id
        # checklist would surface it twice (by ID and by Ref). Direct scan: once.
        _deploy(
            tmp_path,
            "| DEP-9 | PROTO-9 | ship | prod | staged | sam | _(pending gate)_ | v1 |\n",
        )
        items = inbox.collect_inbox(tmp_path)
        assert len(items) == 1
        assert items[0]["change"] == "DEP-9"
        assert items[0]["ref"] == "PROTO-9"
        assert items[0]["discipline"] == "devops"

    def test_multiple_disciplines_ordered_by_path_to_production(self, tmp_path):
        # deploy is later than release in the pipeline order, so the qa (before
        # release) item sorts ahead of the devops (before deploy) item.
        _qa(tmp_path, "| QA-1 | P-1 | s | auth | in-test | ann | _(pending)_ | v1 |\n")
        _deploy(
            tmp_path,
            "| DEP-1 | P-1 | ship | prod | staged | sam | _(pending)_ | v1 |\n",
        )
        items = inbox.collect_inbox(tmp_path)
        disciplines = [i["discipline"] for i in items]
        assert disciplines == ["qa", "devops"]

    def test_release_scoped_gate_surfaces_with_scope(self, tmp_path):
        (tmp_path / "RELEASE_QUEUE.md").write_text(
            "# Releases\n\n| ID | Candidate | Stage | Owner | Signed off by |\n"
            "|----|-----------|-------|-------|---------------|\n"
            "| REL-1 | v1.0 | go-review | pm | _(pending)_ |\n",
            encoding="utf-8",
        )
        items = inbox.collect_inbox(tmp_path)
        assert len(items) == 1
        assert items[0]["gate"] == "go-no-go"
        assert items[0]["scope"] == "release"

    def test_completed_rows_are_historical_not_inbox(self, tmp_path):
        # A completed-tickets row carries a filled "Completed" date — it has moved
        # past active supervision. An empty legacy "Reviewed by" cell on such a row
        # is history, not an actionable pending gate, so it must NOT surface.
        (tmp_path / "PROJECT_STATUS.md").write_text(
            "# Status\n\n## Completed\n\n"
            "| ID | Title | Completed | PR/Commit | Reviewed by |\n"
            "|----|-------|-----------|-----------|-------------|\n"
            "| PROTO-A | a | 2026-07-18 | #1 |  |\n"
            "| PROTO-B | b | 2026-07-18 | #2 | towb |\n",
            encoding="utf-8",
        )
        assert inbox.collect_inbox(tmp_path) == []

    def test_terminal_stage_row_is_skipped(self, tmp_path):
        # A qa row whose stage is terminal ("done") with an empty sign-off cell is
        # historical; an in-flight one ("in-test") with an empty cell is pending.
        _qa(
            tmp_path,
            "| QA-D | P-D | old | auth | done | ann |  | v1 |\n"
            "| QA-L | P-L | live | auth | in-test | ann |  | v1 |\n",
        )
        items = inbox.collect_inbox(tmp_path)
        assert [i["change"] for i in items] == ["QA-L"]

    def test_column_absent_is_untracked_not_pending(self, tmp_path):
        # The active-tickets table has no "Reviewed by" column, so pr-review is
        # untracked there (absent), never pending — no false inbox item.
        (tmp_path / "PROJECT_STATUS.md").write_text(
            "# Status\n\n## Active\n\n"
            "| ID | Title | Type | Status | Branch | Assignee |\n"
            "|----|-------|------|--------|--------|----------|\n"
            "| PROTO-C | c | feature | IN_PROGRESS | dev | towb |\n",
            encoding="utf-8",
        )
        items = inbox.collect_inbox(tmp_path)
        assert [i for i in items if i["gate"] == "pr-review-approval"] == []

    def test_empty_project_is_empty_inbox(self, tmp_path):
        assert inbox.collect_inbox(tmp_path) == []


class TestCmdInbox:
    def test_renders_pending_items(self, tmp_path, monkeypatch):
        from proto_gear_pkg import cli_commands

        _qa(tmp_path, "| QA-1 | P-1 | s | auth | in-test | ann | _(pending)_ | v1 |\n")
        monkeypatch.chdir(tmp_path)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_commands.cmd_inbox(_args(json=False))
        out = buf.getvalue()
        assert rc == 0
        assert "QA-1" in out
        assert "qa-signoff" in out

    def test_clean_inbox_message(self, tmp_path, monkeypatch):
        from proto_gear_pkg import cli_commands

        monkeypatch.chdir(tmp_path)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_commands.cmd_inbox(_args(json=False))
        assert rc == 0
        assert "nothing" in buf.getvalue().lower() or "clear" in buf.getvalue().lower()

    def test_json_output(self, tmp_path, monkeypatch):
        from proto_gear_pkg import cli_commands

        _qa(tmp_path, "| QA-1 | P-1 | s | auth | in-test | ann | _(pending)_ | v1 |\n")
        monkeypatch.chdir(tmp_path)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = cli_commands.cmd_inbox(_args(json=True))
        data = json.loads(buf.getvalue())
        assert rc == 0
        assert data["count"] == 1
        assert data["items"][0]["change"] == "QA-1"
