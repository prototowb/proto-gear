"""Tests for cross-discipline change trace (PROTO-061, Phase D-2).

`module_core.trace` follows a change (engineering ticket id) through each
discipline's declared state surface via a `Ref` column — the ticket-id
correlation key. Generic: a discipline joins tracing by carrying a `Ref` column,
no code change here.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg.module_core import trace


def _args(**kw):
    return argparse.Namespace(**kw)


def _write_surfaces(root: Path, *, qa_ref="PROTO-054", dep_ref="PROTO-054, PROTO-055"):
    (root / "PROJECT_STATUS.md").write_text(
        "# Status\n\n| ID | Title | Type | Status | Branch | Assignee |\n"
        "|----|-------|------|--------|--------|----------|\n"
        "| PROTO-054 | QA module | feature | DONE | - | towb |\n",
        encoding="utf-8",
    )
    (root / "QA_QUEUE.md").write_text(
        "# QA\n\n| ID | Ref | Title | Area | Stage | Owner | Signed off by | Target |\n"
        "|----|-----|-------|------|-------|-------|---------------|--------|\n"
        f"| QA-007 | {qa_ref} | sweep | auth | signed-off | ann | ann | v0.11 |\n",
        encoding="utf-8",
    )
    (root / "DEPLOY_QUEUE.md").write_text(
        "# Deploy\n\n| ID | Ref | Change | Environment | Stage | Owner | Approved by | Target |\n"
        "|----|-----|--------|-------------|-------|-------|-------------|--------|\n"
        f"| DEP-003 | {dep_ref} | ship v2 | prod | deployed | sam | sam | v0.11 |\n"
        "| DEP-004 | PROTO-099 | other | prod | staged | sam | _(pending gate)_ | v0.11 |\n",
        encoding="utf-8",
    )


class TestParseMarkdownTables:
    def test_parses_rows_as_header_keyed_dicts(self):
        text = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n"
        tables = trace.parse_markdown_tables(text)
        assert tables == [[{"A": "1", "B": "2"}, {"A": "3", "B": "4"}]]

    def test_ignores_non_table_prose(self):
        text = "# Title\n\nsome prose\n\n| X |\n|---|\n| v |\n\nmore prose\n"
        tables = trace.parse_markdown_tables(text)
        assert tables == [[{"X": "v"}]]


class TestTraceChange:
    def test_matches_ticket_across_disciplines(self, tmp_path):
        _write_surfaces(tmp_path)
        hits = trace.trace_change("PROTO-054", tmp_path)
        by_disc = {h["discipline"]: h for h in hits}
        assert by_disc["engineering"]["id"] == "PROTO-054"  # matched by ID
        assert by_disc["qa"]["id"] == "QA-007"  # matched by Ref
        assert by_disc["devops"]["id"] == "DEP-003"

    def test_engineering_listed_first(self, tmp_path):
        _write_surfaces(tmp_path)
        hits = trace.trace_change("PROTO-054", tmp_path)
        assert hits[0]["discipline"] == "engineering"

    def test_comma_separated_ref_matches(self, tmp_path):
        # DEP-003 ships "PROTO-054, PROTO-055" — tracing either finds it.
        _write_surfaces(tmp_path)
        hits = trace.trace_change("PROTO-055", tmp_path)
        assert any(h["id"] == "DEP-003" for h in hits)

    def test_approval_state_cleared_vs_pending(self, tmp_path):
        _write_surfaces(tmp_path)
        cleared = trace.trace_change("PROTO-054", tmp_path)
        assert {h["discipline"]: h["approval_state"] for h in cleared}[
            "qa"
        ] == "cleared"
        pending = trace.trace_change("PROTO-099", tmp_path)
        assert pending[0]["approval_state"] == "pending"

    def test_no_match_returns_empty(self, tmp_path):
        _write_surfaces(tmp_path)
        assert trace.trace_change("PROTO-777", tmp_path) == []

    def test_missing_surfaces_are_skipped(self, tmp_path):
        # No state surfaces at all → no hits, no error.
        assert trace.trace_change("PROTO-054", tmp_path) == []


class TestGateChecklist:
    """Phase D-3: fold the pipeline gate chain into the trace — which required
    approvals a change has cleared vs still lacks."""

    def test_evidenced_gates_cleared(self, tmp_path):
        _write_surfaces(tmp_path)  # qa signed-off; DEP-003 deployed + approved
        by_gate = {
            g["gate"]: g["status"] for g in trace.gate_checklist("PROTO-054", tmp_path)
        }
        assert by_gate["qa-signoff"] == "cleared"
        assert by_gate["prod-approval"] == "cleared"

    def test_checklist_entries_carry_authority(self, tmp_path):
        # ADR-002: every checklist entry reports the gate's required authority
        # (all-human across the bundled corpus), so trace/release surfaces can
        # report authority sufficiency without re-reading workflow metadata.
        _write_surfaces(tmp_path)
        entries = trace.gate_checklist("PROTO-054", tmp_path)
        assert entries and all(g["authority"] == "human" for g in entries)

    def test_engineering_gates_untracked(self, tmp_path):
        # engineering's PROJECT_STATUS has no approval column → gates are reached
        # (the ticket exists) but not evidenceable, not silently "outstanding".
        _write_surfaces(tmp_path)
        eng = [
            g
            for g in trace.gate_checklist("PROTO-054", tmp_path)
            if g["discipline"] == "engineering"
        ]
        assert eng and all(g["status"] == "untracked" for g in eng)

    def test_outstanding_when_change_has_not_reached_discipline(self, tmp_path):
        # A ticket present only in engineering: downstream gates are outstanding.
        (tmp_path / "PROJECT_STATUS.md").write_text(
            "| ID | Title | Type | Status | Branch | Assignee |\n"
            "|----|-------|------|--------|--------|----------|\n"
            "| PROTO-080 | new | feature | IN_PROGRESS | - | towb |\n",
            encoding="utf-8",
        )
        by_gate = {
            g["gate"]: g["status"] for g in trace.gate_checklist("PROTO-080", tmp_path)
        }
        assert by_gate["qa-signoff"] == "outstanding"
        assert by_gate["prod-approval"] == "outstanding"

    def test_pending_when_reached_but_awaiting_approval(self, tmp_path):
        _write_surfaces(tmp_path)  # DEP-004 refs PROTO-099, approval pending
        by_gate = {
            g["gate"]: g["status"] for g in trace.gate_checklist("PROTO-099", tmp_path)
        }
        assert by_gate["prod-approval"] == "pending"


def _write_status_with_review(root: Path, reviewer: str):
    """Engineering completed-tickets table carrying the per-gate 'Reviewed by'
    evidence column that pr-review-approval names."""
    (root / "PROJECT_STATUS.md").write_text(
        "# Status\n\n## Completed Tickets\n\n"
        "| ID | Title | Completed | PR | Reviewed by |\n"
        "|----|-------|-----------|----|-------------|\n"
        f"| PROTO-054 | QA module | 2026-07-11 | | {reviewer} |\n",
        encoding="utf-8",
    )


class TestGateSpecificEvidence:
    """PROTO-065: a gate that names an ``evidence`` column is verified against
    THAT column, so engineering's per-change pr-review-approval becomes
    evidenceable without falsely clearing its release-level gates."""

    def test_pr_review_cleared_from_reviewed_by_column(self, tmp_path):
        _write_status_with_review(tmp_path, "ann")
        by_gate = {
            g["gate"]: g["status"] for g in trace.gate_checklist("PROTO-054", tmp_path)
        }
        assert by_gate["pr-review-approval"] == "cleared"

    def test_pr_review_pending_when_column_present_but_empty(self, tmp_path):
        _write_status_with_review(tmp_path, "")
        by_gate = {
            g["gate"]: g["status"] for g in trace.gate_checklist("PROTO-054", tmp_path)
        }
        assert by_gate["pr-review-approval"] == "pending"

    def test_release_level_gates_not_falsely_cleared(self, tmp_path):
        # The "Reviewed by" evidence must NOT bleed into engineering's other
        # gates: release-approval is a release-level gate, unverifiable per ticket.
        _write_status_with_review(tmp_path, "ann")
        eng = {
            g["gate"]: g["status"]
            for g in trace.gate_checklist("PROTO-054", tmp_path)
            if g["discipline"] == "engineering" and g["gate"] != "pr-review-approval"
        }
        assert eng  # there are other engineering gates
        assert all(status != "cleared" for status in eng.values())


class TestGateEvidenceShipped:
    """The bundled pr-review-approval gate ships its evidence column."""

    def test_pr_review_gate_declares_reviewed_by(self):
        from proto_gear_pkg.module_core import pipeline

        gate = next(
            g
            for s in pipeline.build_pipeline()
            for g in s["gates"]
            if g["gate"] == "pr-review-approval"
        )
        assert gate["evidence"] == "Reviewed by"


class TestTraceCLI:
    def test_trace_renders(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        _write_surfaces(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_trace(_args(change_id="PROTO-054", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "PROTO-054" in out and "QA-007" in out and "DEP-003" in out
        assert "approved: ann" in out
        # Phase D-3: the required-approval checklist folds in the pipeline gates.
        assert "Required approvals" in out
        assert "qa-signoff" in out and "cleared" in out

    def test_trace_json(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        _write_surfaces(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_trace(_args(change_id="PROTO-054", json=True))
        data = json.loads(capsys.readouterr().out)
        assert rc == 0
        assert data["change"] == "PROTO-054"
        assert {h["discipline"] for h in data["hits"]} == {
            "engineering",
            "qa",
            "devops",
        }

    def test_trace_no_match_message(self, tmp_path, monkeypatch, capsys):
        from proto_gear_pkg import cli_commands

        _write_surfaces(tmp_path)
        monkeypatch.chdir(tmp_path)
        rc = cli_commands.cmd_trace(_args(change_id="PROTO-777", json=False))
        out = capsys.readouterr().out
        assert rc == 0
        assert "No state-surface rows reference" in out


class TestStateSurfacesCarryRefColumn:
    """The bundled qa/devops surfaces ship the Ref correlation column."""

    def test_qa_and_devops_templates_have_ref(self):
        from proto_gear_pkg.module_core.module_manifest import default_modules_root

        qa = (default_modules_root() / "qa" / "QA_QUEUE.template.md").read_text(
            encoding="utf-8"
        )
        devops = (
            default_modules_root() / "devops" / "DEPLOY_QUEUE.template.md"
        ).read_text(encoding="utf-8")
        assert "| ID | Ref |" in qa
        assert "| ID | Ref |" in devops
