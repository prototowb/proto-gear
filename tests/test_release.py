"""Tests for release trace (PROTO-064, Phase D-4).

`module_core.release` aggregates each ticket's gate checklist (Phase D-3) into a
single release-level readiness verdict. Membership is read from a release column
(PR/Commit / Release / Version) in the disciplines' state surfaces; the verdict
distinguishes cleared / blocking / unverifiable gates.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core import release


def _args(**kw):
    return argparse.Namespace(**kw)


def _write_status(root: Path, rows: str, releases: str = None):
    """Engineering state surface: completed-tickets table with a PR/Commit column,
    plus an optional Releases table (release-scoped gate evidence, keyed by the
    release label in the ID column)."""
    text = (
        "# Status\n\n| ID | Title | Completed | PR/Commit |\n"
        "|----|-------|-----------|-----------|\n" + rows
    )
    if releases is not None:
        text += (
            "\n## Releases\n\n"
            "| ID | Date | Release approved by | Announced by |\n"
            "|----|------|---------------------|--------------|\n" + releases
        )
    (root / "PROJECT_STATUS.md").write_text(text, encoding="utf-8")


def _write_qa(root: Path, rows: str):
    (root / "QA_QUEUE.md").write_text(
        "# QA\n\n| ID | Ref | Title | Area | Stage | Owner | Signed off by | Target |\n"
        "|----|-----|-------|------|-------|-------|---------------|--------|\n" + rows,
        encoding="utf-8",
    )


def _write_devops(root: Path, rows: str):
    (root / "DEPLOY_QUEUE.md").write_text(
        "# Deploy\n\n| ID | Ref | Change | Environment | Stage | Owner | Approved by | Target |\n"
        "|----|-----|--------|-------------|-------|-------|-------------|--------|\n"
        + rows,
        encoding="utf-8",
    )


def _write_security(root: Path, rows: str):
    (root / "SECURITY_QUEUE.md").write_text(
        "# Security\n\n| ID | Ref | Finding | Severity | Stage | Owner | Signed off by | Target |\n"
        "|----|-----|---------|----------|-------|-------|---------------|--------|\n"
        + rows,
        encoding="utf-8",
    )


def _write_release_queue(root: Path, rows: str):
    """Release-management surface (PROTO-077): rows keyed by the release label,
    evidencing the release-scoped go-no-go gate."""
    (root / "RELEASE_QUEUE.md").write_text(
        "# Releases\n\n| ID | Ref | Stage | Owner | Window | Signed off by |\n"
        "|----|-----|-------|-------|--------|---------------|\n" + rows,
        encoding="utf-8",
    )


def _full_release(root: Path):
    """A two-ticket release: PROTO-A fully cleared downstream, PROTO-B still blocked."""
    _write_status(
        root,
        "| PROTO-A | first | 2026-07-11 | v0.11 |\n"
        "| PROTO-B | second | 2026-07-11 | v0.11 |\n"
        "| PROTO-C | other | 2026-07-01 | v0.10 |\n",
    )
    _write_qa(
        root,
        "| QA-1 | PROTO-A | a | auth | signed-off | ann | ann | v0.11 |\n"
        "| QA-2 | PROTO-B | b | api | in-test | ann | _(pending gate)_ | v0.11 |\n",
    )
    _write_devops(
        root,
        "| DEP-1 | PROTO-A | ship a | prod | deployed | sam | sam | v0.11 |\n",
    )
    _write_security(
        root,
        "| SEC-1 | PROTO-A | a finding | low | signed-off | eve | eve | v0.11 |\n",
    )


class TestFindReleaseTickets:
    def test_matches_tickets_by_release_column(self, tmp_path):
        _full_release(tmp_path)
        tickets = release.find_release_tickets("v0.11", tmp_path)
        assert tickets == ["PROTO-A", "PROTO-B"]  # PROTO-C is v0.10, excluded

    def test_no_match_returns_empty(self, tmp_path):
        _full_release(tmp_path)
        assert release.find_release_tickets("v9.9", tmp_path) == []

    def test_missing_surfaces_are_skipped(self, tmp_path):
        assert release.find_release_tickets("v0.11", tmp_path) == []

    def test_target_column_is_not_release_membership(self, tmp_path):
        # qa/devops surfaces carry a "Target" version column; it must NOT be read
        # as release membership (those are downstream items, not release tickets).
        _write_qa(
            tmp_path,
            "| QA-9 | PROTO-Z | z | auth | in-test | ann | | v0.11 |\n",
        )
        assert release.find_release_tickets("v0.11", tmp_path) == []


class TestTraceRelease:
    def test_blocked_when_a_ticket_has_outstanding_gates(self, tmp_path):
        _full_release(tmp_path)
        report = release.trace_release("v0.11", tmp_path)
        assert report["ticket_count"] == 2
        assert report["ready"] is False  # PROTO-B blocks
        by_ticket = {e["ticket"]: e for e in report["tickets"]}
        assert by_ticket["PROTO-A"]["ready"] is True
        assert by_ticket["PROTO-B"]["ready"] is False
        assert report["blocking_total"] > 0

    def test_cleared_gates_counted_per_ticket(self, tmp_path):
        _full_release(tmp_path)
        report = release.trace_release("v0.11", tmp_path)
        a = next(e for e in report["tickets"] if e["ticket"] == "PROTO-A")
        cleared_gates = {g["gate"] for g in a["cleared"]}
        assert {"qa-signoff", "prod-approval", "security-signoff"} <= cleared_gates

    def _ready_release(self, root):
        """One ticket, all change-scoped downstream gates cleared, a Releases
        row clearing engineering's release-scoped gates, and a RELEASE_QUEUE
        row clearing release-management's go-no-go (PROTO-077)."""
        _write_status(
            root,
            "| PROTO-A | first | 2026-07-11 | v0.11 |\n",
            releases="| v0.11 | 2026-07-11 | tobias | tobias |\n",
        )
        _write_qa(
            root, "| QA-1 | PROTO-A | a | auth | signed-off | ann | ann | v0.11 |\n"
        )
        _write_devops(
            root, "| DEP-1 | PROTO-A | ship a | prod | deployed | sam | sam | v0.11 |\n"
        )
        _write_security(
            root, "| SEC-1 | PROTO-A | f | low | signed-off | eve | eve | v0.11 |\n"
        )
        _write_release_queue(
            root, "| v0.11 | PROTO-A | go | rex | 2026-07-15 | tobias |\n"
        )

    def test_ready_when_change_and_release_gates_cleared(self, tmp_path):
        self._ready_release(tmp_path)
        report = release.trace_release("v0.11", tmp_path)
        assert report["ready"] is True
        assert report["blocking_total"] == 0
        # engineering's per-change pr-review-approval (no Reviewed by) is
        # unverifiable but must not block.
        assert report["unverified_total"] > 0

    def test_release_scoped_gates_evaluated_once(self, tmp_path):
        self._ready_release(tmp_path)
        report = release.trace_release("v0.11", tmp_path)
        cleared = {g["gate"] for g in report["release_gates"]["cleared"]}
        assert "release-approval" in cleared
        assert "announcement-approval" in cleared
        assert "go-no-go" in cleared  # release-management's gate (PROTO-077)

    def test_blocked_when_release_approval_missing(self, tmp_path):
        # Everything per-ticket clears, but no Releases row → release-scoped
        # gates are outstanding → the release is not ready.
        _write_status(tmp_path, "| PROTO-A | first | 2026-07-11 | v0.11 |\n")
        _write_qa(
            tmp_path, "| QA-1 | PROTO-A | a | auth | signed-off | ann | ann | v0.11 |\n"
        )
        _write_devops(
            tmp_path,
            "| DEP-1 | PROTO-A | ship a | prod | deployed | sam | sam | v0.11 |\n",
        )
        _write_security(
            tmp_path, "| SEC-1 | PROTO-A | f | low | signed-off | eve | eve | v0.11 |\n"
        )
        report = release.trace_release("v0.11", tmp_path)
        assert report["ready"] is False
        assert report["release_gates"]["blocking"]  # release-approval outstanding

    def test_empty_release_is_not_ready(self, tmp_path):
        _full_release(tmp_path)
        report = release.trace_release("v9.9", tmp_path)
        assert report["ticket_count"] == 0
        assert report["ready"] is False


class TestReleaseCLI:
    def test_release_renders(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        _full_release(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_release(_args(release_id="v0.11", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "PROTO-A" in out and "PROTO-B" in out
        assert "BLOCKED" in out  # PROTO-B blocks the release

    def test_release_json(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        _full_release(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_release(_args(release_id="v0.11", json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert data["release"] == "v0.11"
        assert data["ticket_count"] == 2
        assert data["ready"] is False

    def test_release_no_match_message(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        _full_release(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_release(_args(release_id="v9.9", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "No tickets reference release" in out


class TestAuthoritySufficiencyRollup:
    """ADR-002 action item 3: the release report counts cleared gates whose
    only signer is an agent identity while the gate demands a human rung.
    Reported, never blocking — the readiness verdict is unchanged."""

    def test_agent_signed_gate_is_counted_not_blocking(self, tmp_path):
        _write_status(tmp_path, "| PROTO-A | first | 2026-07-11 | v0.11 |\n")
        # qa-release-agent is a real bundled agent id — an agent signature on
        # the human-authority qa-signoff gate.
        _write_qa(
            tmp_path,
            "| QA-1 | PROTO-A | a | auth | signed-off | ann | qa-release-agent | v0.11 |\n",
        )
        report = release.trace_release("v0.11", tmp_path)
        assert report["authority_insufficient_total"] >= 1
        insufficient = report["tickets"][0]["insufficient"]
        assert any(g["gate"] == "qa-signoff" for g in insufficient)
        # Not blocking: readiness semantics unchanged (the gate IS cleared).
        assert not any(
            g["gate"] == "qa-signoff" for g in report["tickets"][0]["blocking"]
        )

    def test_human_signed_release_reports_zero_insufficient(self, tmp_path):
        _full_release(tmp_path)
        report = release.trace_release("v0.11", tmp_path)
        assert report["authority_insufficient_total"] == 0


class TestReleaseNotes:
    """PROTO-079: `pg release --notes` renders notes from the cleared checklist."""

    def _ready_release(self, root):
        _write_status(
            root,
            "| PROTO-A | first | 2026-07-11 | v0.11 |\n",
            releases="| v0.11 | 2026-07-11 | tobias | tobias |\n",
        )
        _write_qa(
            root, "| QA-1 | PROTO-A | a | auth | signed-off | ann | ann | v0.11 |\n"
        )
        _write_devops(
            root, "| DEP-1 | PROTO-A | ship a | prod | deployed | sam | sam | v0.11 |\n"
        )
        _write_security(
            root, "| SEC-1 | PROTO-A | f | low | signed-off | eve | eve | v0.11 |\n"
        )
        _write_release_queue(
            root, "| v0.11 | PROTO-A | go | rex | 2026-07-15 | tobias |\n"
        )

    def test_build_notes_ready_release(self, tmp_path):
        self._ready_release(tmp_path)
        data = release.build_release_notes("v0.11", tmp_path)
        assert data["ready"] is True
        assert data["date"] == "2026-07-11"  # read from the Releases table
        # One member ticket, no Type column → default "Changes" section.
        assert data["ticket_count"] == 1
        section = data["sections"][0]
        assert section["heading"] == "Changes"
        assert section["tickets"] == [{"id": "PROTO-A", "title": "first"}]
        # Cleared downstream gates recorded their signers.
        signers = {s for a in data["approvals"] for s in a["signers"]}
        assert {"ann", "sam", "eve"} <= signers

    def test_render_ready_notes_markdown(self, tmp_path):
        self._ready_release(tmp_path)
        md = release.render_release_notes(
            release.build_release_notes("v0.11", tmp_path)
        )
        assert md.startswith("## v0.11 — 2026-07-11")
        assert "### Changes" in md
        assert "- PROTO-A  first" in md
        assert "**Approvals:**" in md
        assert "_Generated from cleared gate evidence._" in md
        assert "Draft" not in md  # ready → no draft caveat

    def test_render_draft_when_blocked(self, tmp_path):
        # PROTO-B has no downstream sign-offs → release blocked → draft caveat.
        _write_status(
            tmp_path,
            "| PROTO-A | first | 2026-07-11 | v0.11 |\n"
            "| PROTO-B | second | 2026-07-11 | v0.11 |\n",
        )
        md = release.render_release_notes(
            release.build_release_notes("v0.11", tmp_path)
        )
        assert "⚠ **Draft**" in md
        assert "still blocking" in md

    def test_type_column_groups_into_sections(self, tmp_path):
        # A surface with both Type and a Release column exercises grouping.
        (tmp_path / "PROJECT_STATUS.md").write_text(
            "# Status\n\n| ID | Title | Type | Status | Release |\n"
            "|----|-------|------|--------|--------|\n"
            "| PROTO-A | shiny thing | feature | done | v0.11 |\n"
            "| PROTO-B | squash it | bugfix | done | v0.11 |\n",
            encoding="utf-8",
        )
        data = release.build_release_notes("v0.11", tmp_path)
        headings = [s["heading"] for s in data["sections"]]
        assert headings == ["Features", "Fixes"]  # stable section order
        feats = next(s for s in data["sections"] if s["heading"] == "Features")
        assert feats["tickets"] == [{"id": "PROTO-A", "title": "shiny thing"}]

    def test_no_tickets_message(self, tmp_path):
        _write_status(tmp_path, "| PROTO-A | first | 2026-07-11 | v0.10 |\n")
        md = release.render_release_notes(release.build_release_notes("v9.9", tmp_path))
        assert "No tickets reference this release" in md

    def test_cli_notes_renders(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        self._ready_release(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_release(_args(release_id="v0.11", json=False, notes=True))
        assert rc == 0
        out = capsys.readouterr().out
        assert "## v0.11" in out and "- PROTO-A  first" in out

    def test_cli_notes_json(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        self._ready_release(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_release(_args(release_id="v0.11", json=True, notes=True))
        assert rc == 0
        data = json.loads(capsys.readouterr().out)
        assert data["release"] == "v0.11" and data["ready"] is True
