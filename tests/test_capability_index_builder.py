"""
Tests for capability_index_builder — PROTO-036.

Covers:
  - rendering helpers (formatting triggers, deps, type filters)
  - per-type and top-level INDEX block shape
  - sync_capability_indexes file replacement (managed block contract)
  - missing-markers / missing-file / unchanged paths
"""

import shutil
import pytest
from pathlib import Path

from proto_gear_pkg.capability_index_builder import (
    BEGIN_MARKER,
    END_MARKER,
    render_top_index_block,
    render_type_index_block,
    sync_capability_indexes,
    extract_managed_block,
    _replace_or_warn,
)
from proto_gear_pkg.capability_metadata import (
    CapabilityMetadata,
    CapabilityType,
    CapabilityStatus,
    CapabilityDependencies,
    CapabilityRelevance,
    load_all_capabilities,
)


PACKAGE_CAPS_ROOT = Path(__file__).parent.parent / "core" / "proto_gear_pkg" / "capabilities"


def _make_cap(name, cap_type=CapabilityType.SKILL, triggers=None, deps=None,
              version="1.0.0", description="desc", category="test", tags=None):
    return CapabilityMetadata(
        name=name,
        type=cap_type,
        version=version,
        description=description,
        category=category,
        tags=tags or [],
        status=CapabilityStatus.STABLE,
        author="t",
        last_updated="2026-01-01",
        dependencies=deps or CapabilityDependencies(required=[], optional=[], suggested=[]),
        conflicts=[],
        composable_with=[],
        agent_roles=[],
        relevance=CapabilityRelevance(triggers=triggers or [], contexts=[]),
    )


# ---------- shape tests on the package's own capabilities ----------

class TestRenderingAgainstPackage:
    """The package ships 7 skills + 13 workflows + 4 commands. Render and inspect."""

    @pytest.fixture
    def caps(self):
        return load_all_capabilities(PACKAGE_CAPS_ROOT)

    def test_top_block_wraps_in_markers(self, caps):
        block = render_top_index_block(caps)
        assert block.startswith(BEGIN_MARKER)
        assert block.endswith(END_MARKER)

    def test_top_block_mentions_each_type(self, caps):
        block = render_top_index_block(caps)
        assert "### Skills (7)" in block
        assert "### Workflows (13)" in block
        assert "### Slash Commands (4)" in block

    def test_top_block_contains_known_capability_id(self, caps):
        block = render_top_index_block(caps)
        assert "`skills/testing`" in block

    def test_skills_block_mentions_all_seven_skills(self, caps):
        block = render_type_index_block(caps, CapabilityType.SKILL)
        # Each shipped skill's display name should appear.
        names = [c.name for c in caps.values() if c.type == CapabilityType.SKILL]
        for n in names:
            assert n in block, f"Skill {n!r} missing from rendered block"

    def test_workflow_block_includes_steps_when_present(self, caps):
        block = render_type_index_block(caps, CapabilityType.WORKFLOW)
        # feature-development declares steps=7 in metadata.
        assert "Steps" in block

    def test_empty_type_renders_placeholder(self, caps):
        # Package ships no agents.
        block = render_type_index_block(caps, CapabilityType.AGENT)
        assert "No agents installed" in block or "_None_" in block or "(0)" in block


# ---------- rendering helpers in isolation ----------

class TestRenderingPureHelpers:
    def test_skill_block_lists_trigger_strings(self):
        cap = _make_cap("Test Skill", triggers=["alpha", "beta"])
        block = render_type_index_block({"skills/t": cap}, CapabilityType.SKILL)
        assert '"alpha"' in block
        assert '"beta"' in block

    def test_no_relevance_yields_none_declared(self):
        cap = _make_cap("Bare")
        cap.relevance = None
        block = render_type_index_block({"skills/b": cap}, CapabilityType.SKILL)
        assert "_none declared_" in block

    def test_filters_by_type(self):
        s = _make_cap("S")
        w = _make_cap("W", cap_type=CapabilityType.WORKFLOW)
        caps = {"skills/s": s, "workflows/w": w}
        skills_block = render_type_index_block(caps, CapabilityType.SKILL)
        wf_block = render_type_index_block(caps, CapabilityType.WORKFLOW)
        assert "skills/s" in skills_block
        assert "workflows/w" not in skills_block
        assert "workflows/w" in wf_block
        assert "skills/s" not in wf_block

    def test_dependencies_rendered(self):
        deps = CapabilityDependencies(
            required=["skills/foo"],
            optional=["workflows/bar"],
            suggested=[],
        )
        cap = _make_cap("D", deps=deps)
        block = render_type_index_block({"skills/d": cap}, CapabilityType.SKILL)
        assert "required: `skills/foo`" in block
        assert "optional: `workflows/bar`" in block


# ---------- sync_capability_indexes (file IO) ----------

class TestSyncCapabilityIndexes:
    @pytest.fixture
    def synced_caps_root(self, tmp_path):
        """Copy the package capabilities into tmp_path and rename INDEX
        templates to INDEX.md, mimicking what pg init produces."""
        dest = tmp_path / "proto-gear"
        shutil.copytree(PACKAGE_CAPS_ROOT, dest)
        for f in dest.rglob("INDEX.template.md"):
            f.rename(f.parent / "INDEX.md")
        return dest

    def test_first_sync_marks_files_updated(self, synced_caps_root):
        # Freshly-copied INDEX files have markers but old content.
        results = sync_capability_indexes(synced_caps_root, dry_run=False)
        assert results["INDEX.md"] == "updated"
        assert results["skills/INDEX.md"] == "updated"
        assert results["workflows/INDEX.md"] == "updated"
        assert results["commands/INDEX.md"] == "updated"

    def test_second_sync_is_idempotent(self, synced_caps_root):
        sync_capability_indexes(synced_caps_root, dry_run=False)
        results = sync_capability_indexes(synced_caps_root, dry_run=False)
        # Every file we touched should now report unchanged or missing.
        for rel, action in results.items():
            assert action in ("unchanged", "missing-markers", "missing-file"), \
                f"{rel} -> {action}"

    def test_dry_run_reports_would_update_without_writing(self, synced_caps_root):
        idx_top = synced_caps_root / "INDEX.md"
        before = idx_top.read_text(encoding="utf-8")
        results = sync_capability_indexes(synced_caps_root, dry_run=True)
        assert results["INDEX.md"] == "would_update"
        assert idx_top.read_text(encoding="utf-8") == before

    def test_missing_markers_does_not_modify_file(self, synced_caps_root):
        # agents/INDEX.md ships with no markers — should be skipped.
        agents_idx = synced_caps_root / "agents" / "INDEX.md"
        before = agents_idx.read_text(encoding="utf-8") if agents_idx.exists() else None
        results = sync_capability_indexes(synced_caps_root, dry_run=False)
        # Either missing file or missing markers; both leave the file untouched.
        assert results["agents/INDEX.md"] in ("missing-file", "missing-markers")
        if before is not None:
            assert agents_idx.read_text(encoding="utf-8") == before

    def test_returns_error_for_nonexistent_root(self, tmp_path):
        result = sync_capability_indexes(tmp_path / "nope", dry_run=True)
        assert "error" in result

    def test_outside_content_preserved(self, synced_caps_root):
        skills_idx = synced_caps_root / "skills" / "INDEX.md"
        before = skills_idx.read_text(encoding="utf-8")
        # The "## How to Use Skills" prose lives outside the managed block.
        marker_text = "## How to Use Skills"
        assert marker_text in before
        sync_capability_indexes(synced_caps_root, dry_run=False)
        after = skills_idx.read_text(encoding="utf-8")
        assert marker_text in after


# ---------- _replace_or_warn helper ----------

class TestReplaceOrWarn:
    def test_missing_file_reported(self, tmp_path):
        action = _replace_or_warn(tmp_path / "nope.md", "block", dry_run=True)
        assert action == "missing-file"

    def test_missing_markers_reported(self, tmp_path):
        f = tmp_path / "x.md"
        f.write_text("no markers here\n", encoding="utf-8")
        action = _replace_or_warn(f, BEGIN_MARKER + "\nnew\n" + END_MARKER, dry_run=True)
        assert action == "missing-markers"

    def test_replace_round_trip(self, tmp_path):
        f = tmp_path / "x.md"
        f.write_text(
            f"prose\n{BEGIN_MARKER}\nold\n{END_MARKER}\nmore prose\n",
            encoding="utf-8",
        )
        new_block = f"{BEGIN_MARKER}\nfresh\n{END_MARKER}"
        action = _replace_or_warn(f, new_block, dry_run=False)
        assert action == "updated"
        text = f.read_text(encoding="utf-8")
        assert "fresh" in text
        assert "old" not in text
        assert "prose" in text and "more prose" in text

    def test_extract_managed_block(self):
        text = f"head\n{BEGIN_MARKER}\nbody\n{END_MARKER}\ntail"
        block = extract_managed_block(text)
        assert block is not None
        assert "body" in block
        assert "head" not in block

    def test_extract_returns_none_when_absent(self):
        assert extract_managed_block("plain text") is None
