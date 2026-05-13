"""
Tests for the doctor module — pg doctor drift detector (PROTO-034).
"""

import pytest
from pathlib import Path

from proto_gear_pkg.doctor import (
    Finding,
    DiagnosticsReport,
    check_agent_context_sync,
    check_host_files,
    check_core_doc_headers,
    check_capabilities,
    check_capability_indexes,
    run_diagnostics,
    fixable_by_sync,
    _normalize,
    CORE_DOC_FILES,
)
from proto_gear_pkg.sync_context import (
    BEGIN_MARKER,
    END_MARKER,
    HOST_FILES,
    generate_agent_context,
    sync_context,
)


@pytest.fixture
def synced_project(tmp_path):
    """A project where sync-context has already been run. Should be drift-free."""
    (tmp_path / "PROJECT_STATUS.md").write_text(
        "<!-- proto-gear:header\n"
        "purpose: project status\n"
        "read-when: every session\n"
        "priority: required\n"
        "-->\n\n"
        'project_type: "Python"\nprotogear_version: "v0.9.0"\nrelease_date: "2026-02-19"\n',
        encoding="utf-8",
    )
    sync_context(tmp_path, dry_run=False)
    return tmp_path


# ---------- Finding / DiagnosticsReport ----------

class TestFinding:
    def test_to_dict_round_trip(self):
        f = Finding(id="x", severity="warning", target="a.md",
                    message="m", fix_hint="hint")
        d = f.to_dict()
        assert d == {"id": "x", "severity": "warning", "target": "a.md",
                     "message": "m", "fix_hint": "hint"}


class TestDiagnosticsReport:
    def test_counts(self):
        r = DiagnosticsReport(findings=[
            Finding("a", "ok", "x", "m"),
            Finding("b", "warning", "y", "m"),
            Finding("c", "warning", "z", "m"),
            Finding("d", "error", "w", "m"),
        ])
        assert r.ok == 1
        assert r.warnings == 2
        assert r.errors == 1

    def test_to_dict_shape(self):
        r = DiagnosticsReport(findings=[Finding("a", "ok", "x", "m")])
        d = r.to_dict()
        assert d["summary"] == {"ok": 1, "warnings": 0, "errors": 0}
        assert len(d["findings"]) == 1


class TestNormalize:
    def test_strips_generated_line(self):
        text = "head\n- **Generated**: 2026-05-13 00:44\ntail"
        out = _normalize(text)
        assert "Generated" not in out
        assert "head" in out
        assert "tail" in out


# ---------- check_agent_context_sync ----------

class TestAgentContextSync:
    def test_missing_file_is_error(self, tmp_path):
        findings = check_agent_context_sync(tmp_path)
        assert len(findings) == 1
        assert findings[0].severity == "error"
        assert findings[0].id == "agent-context-missing"

    def test_in_sync_after_generation(self, synced_project):
        findings = check_agent_context_sync(synced_project)
        assert len(findings) == 1
        assert findings[0].severity == "ok"
        assert findings[0].id == "agent-context-sync"

    def test_drift_detected_when_modified(self, synced_project):
        canon = synced_project / "AGENT_CONTEXT.md"
        canon.write_text(canon.read_text(encoding="utf-8") + "\nMANUAL EDIT\n",
                         encoding="utf-8")
        findings = check_agent_context_sync(synced_project)
        assert any(f.id == "agent-context-drift" for f in findings)
        assert all(f.severity == "warning" for f in findings if f.id == "agent-context-drift")

    def test_timestamp_only_change_is_not_drift(self, synced_project):
        canon = synced_project / "AGENT_CONTEXT.md"
        text = canon.read_text(encoding="utf-8")
        # Replace the generated line with a stale timestamp; should still be in sync.
        bumped = text.replace("Generated**: ", "Generated**: 1999-01-01 ")
        canon.write_text(bumped, encoding="utf-8")
        findings = check_agent_context_sync(synced_project)
        assert findings[0].id == "agent-context-sync"


# ---------- check_host_files ----------

class TestHostFiles:
    def test_synced_project_has_no_drift(self, synced_project):
        findings = check_host_files(synced_project)
        # All host files should be in sync.
        for hf in HOST_FILES:
            matches = [f for f in findings if f.target == hf]
            assert matches, f"Expected a finding for {hf}"
            assert all(f.severity == "ok" for f in matches), f"{hf} should be in sync: {matches}"

    def test_missing_host_file_warns(self, synced_project):
        (synced_project / "CLAUDE.md").unlink()
        findings = check_host_files(synced_project)
        claude = [f for f in findings if f.target == "CLAUDE.md"]
        assert len(claude) == 1
        assert claude[0].id == "host-file-missing"
        assert claude[0].severity == "warning"

    def test_host_without_managed_block_warns(self, synced_project):
        (synced_project / "CLAUDE.md").write_text("only unmanaged content\n",
                                                   encoding="utf-8")
        findings = check_host_files(synced_project)
        claude = [f for f in findings if f.target == "CLAUDE.md"]
        assert any(f.id == "host-block-missing" for f in claude)

    def test_drift_detected_in_host_block(self, synced_project):
        path = synced_project / "CLAUDE.md"
        text = path.read_text(encoding="utf-8")
        tampered = text.replace(BEGIN_MARKER, BEGIN_MARKER + "\nINJECTED\n", 1)
        path.write_text(tampered, encoding="utf-8")
        findings = check_host_files(synced_project)
        claude = [f for f in findings if f.target == "CLAUDE.md"]
        assert any(f.id == "host-block-drift" for f in claude)


# ---------- check_core_doc_headers ----------

class TestCoreDocHeaders:
    def test_silent_when_no_core_docs_present(self, tmp_path):
        findings = check_core_doc_headers(tmp_path)
        assert findings == []

    def test_warns_when_header_missing(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# AGENTS\n\nno header here\n",
                                             encoding="utf-8")
        findings = check_core_doc_headers(tmp_path)
        assert len(findings) == 1
        assert findings[0].id == "missing-proto-gear-header"
        assert findings[0].severity == "warning"

    def test_ok_when_header_present(self, tmp_path):
        header = (
            "<!-- proto-gear:header\n"
            "purpose: agent orchestration\n"
            "read-when: session start\n"
            "priority: required\n"
            "-->\n\n# AGENTS\n"
        )
        (tmp_path / "AGENTS.md").write_text(header, encoding="utf-8")
        findings = check_core_doc_headers(tmp_path)
        assert len(findings) == 1
        assert findings[0].severity == "ok"
        assert findings[0].id == "proto-gear-header-ok"


# ---------- check_capabilities ----------

class TestCapabilities:
    def test_silent_when_proto_gear_dir_missing(self, tmp_path):
        assert check_capabilities(tmp_path) == []

    def test_empty_dir_warns(self, tmp_path):
        (tmp_path / ".proto-gear").mkdir()
        findings = check_capabilities(tmp_path)
        assert any(f.id == "capabilities-empty" for f in findings)

    def test_capability_without_triggers_warns(self, tmp_path):
        skill = tmp_path / ".proto-gear" / "skills" / "no-triggers"
        skill.mkdir(parents=True)
        (skill / "metadata.yaml").write_text(
            'name: "No Triggers Skill"\n'
            'type: "skill"\n'
            'version: "1.0.0"\n'
            'description: "Skill with no triggers"\n'
            'category: "test"\n'
            'tags: []\n'
            'status: "stable"\n'
            'author: "test"\n'
            'last_updated: "2026-01-01"\n'
            'dependencies:\n  required: []\n  optional: []\n  suggested: []\n'
            'conflicts: []\n'
            'composable_with: []\n'
            'agent_roles: []\n'
            'relevance:\n  triggers: []\n  contexts: []\n',
            encoding="utf-8",
        )
        findings = check_capabilities(tmp_path)
        assert any(f.id == "capability-no-triggers" for f in findings)


# ---------- check_capability_indexes ----------

class TestCheckCapabilityIndexes:
    def test_silent_when_proto_gear_dir_missing(self, tmp_path):
        assert check_capability_indexes(tmp_path) == []

    def test_in_sync_after_sync_indexes(self, tmp_path):
        import shutil
        from proto_gear_pkg.capability_index_builder import sync_capability_indexes
        pkg_caps = (
            Path(__file__).parent.parent / "core" / "proto_gear_pkg" / "capabilities"
        )
        caps_root = tmp_path / ".proto-gear"
        shutil.copytree(pkg_caps, caps_root)
        for f in caps_root.rglob("INDEX.template.md"):
            f.rename(f.parent / "INDEX.md")
        sync_capability_indexes(caps_root, dry_run=False)
        findings = check_capability_indexes(tmp_path)
        # No drift findings expected for files that have markers.
        assert not any(f.id == "capability-index-drift" for f in findings)

    def test_drift_detected_when_index_modified(self, tmp_path):
        import shutil
        from proto_gear_pkg.capability_index_builder import (
            sync_capability_indexes, BEGIN_MARKER,
        )
        pkg_caps = (
            Path(__file__).parent.parent / "core" / "proto_gear_pkg" / "capabilities"
        )
        caps_root = tmp_path / ".proto-gear"
        shutil.copytree(pkg_caps, caps_root)
        for f in caps_root.rglob("INDEX.template.md"):
            f.rename(f.parent / "INDEX.md")
        sync_capability_indexes(caps_root, dry_run=False)
        # Tamper with the skills INDEX inside the managed block.
        skills_idx = caps_root / "skills" / "INDEX.md"
        text = skills_idx.read_text(encoding="utf-8")
        skills_idx.write_text(
            text.replace(BEGIN_MARKER, BEGIN_MARKER + "\nINJECTED LINE\n", 1),
            encoding="utf-8",
        )
        findings = check_capability_indexes(tmp_path)
        assert any(f.id == "capability-index-drift" for f in findings)


# ---------- run_diagnostics + fixable_by_sync ----------

class TestRunDiagnostics:
    def test_synced_project_has_no_warnings_or_errors(self, synced_project):
        report = run_diagnostics(synced_project)
        assert report.errors == 0
        # No core docs (AGENTS.md etc.) in the fixture, so warnings should be 0 too.
        assert report.warnings == 0

    def test_returns_report_object(self, synced_project):
        report = run_diagnostics(synced_project)
        assert isinstance(report, DiagnosticsReport)
        assert isinstance(report.findings, list)

    def test_to_dict_serializable(self, synced_project):
        import json
        report = run_diagnostics(synced_project)
        # Must round-trip through JSON without error.
        json.dumps(report.to_dict())


class TestFixableBySync:
    def test_true_when_drift_finding_present(self):
        report = DiagnosticsReport(findings=[
            Finding("agent-context-drift", "warning", "AGENT_CONTEXT.md", "m"),
        ])
        assert fixable_by_sync(report) is True

    def test_true_when_capability_index_drift_present(self):
        report = DiagnosticsReport(findings=[
            Finding("capability-index-drift", "warning",
                    ".proto-gear/skills/INDEX.md", "m"),
        ])
        assert fixable_by_sync(report) is True

    def test_false_when_only_unrelated_findings(self):
        report = DiagnosticsReport(findings=[
            Finding("capability-no-triggers", "warning", "skills/x", "m"),
        ])
        assert fixable_by_sync(report) is False

    def test_false_when_empty(self):
        assert fixable_by_sync(DiagnosticsReport()) is False
