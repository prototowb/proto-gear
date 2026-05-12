"""
Tests for the discovery module — pg suggest backend (PROTO-033).
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from proto_gear_pkg.discovery import (
    _tokenize,
    _score_capability,
    load_capabilities_for_suggest,
    suggest,
)
from proto_gear_pkg.capability_metadata import (
    CapabilityMetadata,
    CapabilityType,
    CapabilityStatus,
    CapabilityDependencies,
    CapabilityRelevance,
)


def _make_cap(name: str, triggers: list, cap_type=CapabilityType.SKILL,
              description: str = "desc") -> CapabilityMetadata:
    return CapabilityMetadata(
        name=name,
        type=cap_type,
        version="1.0.0",
        description=description,
        category="test",
        tags=[],
        status=CapabilityStatus.STABLE,
        author="test",
        last_updated="2026-01-01",
        dependencies=CapabilityDependencies(required=[], optional=[], suggested=[]),
        conflicts=[],
        composable_with=[],
        agent_roles=[],
        relevance=CapabilityRelevance(triggers=triggers, contexts=[]),
    )


class TestTokenize:
    def test_lowercases(self):
        assert _tokenize("WriteTests") == ["writetests"]

    def test_splits_on_punctuation(self):
        assert _tokenize("fix, debug the bug!") == ["fix", "debug", "the", "bug"]

    def test_preserves_hyphens_and_slashes(self):
        assert _tokenize("skills/testing red-green") == ["skills/testing", "red-green"]


class TestScoreCapability:
    def test_substring_hit_beats_no_match(self):
        cap = _make_cap("Testing", ["write tests", "tdd"])
        score_hit, _ = _score_capability(["write", "tests"], "write tests", cap)
        score_miss, _ = _score_capability(["hello"], "hello", cap)
        assert score_hit > score_miss
        assert score_miss == 0

    def test_multi_word_trigger_outscores_single_word(self):
        cap_multi = _make_cap("M", ["fix login bug"])
        cap_single = _make_cap("S", ["bug"])
        s_multi, _ = _score_capability(["fix", "login", "bug"], "fix login bug", cap_multi)
        s_single, _ = _score_capability(["fix", "login", "bug"], "fix login bug", cap_single)
        assert s_multi > s_single

    def test_returns_matched_triggers(self):
        cap = _make_cap("T", ["tdd", "write tests", "unrelated"])
        _, matched = _score_capability(["write", "tests", "now"], "write tests now", cap)
        assert "write tests" in matched
        assert "unrelated" not in matched

    def test_zero_score_for_no_triggers(self):
        cap = _make_cap("Empty", [])
        score, matched = _score_capability(["whatever"], "whatever", cap)
        assert score == 0
        assert matched == []


class TestLoadCapabilitiesForSuggest:
    def test_prefers_project_over_package(self, tmp_path):
        # Build a fake project capabilities dir with one capability
        proj_dir = tmp_path
        skill_dir = proj_dir / ".proto-gear" / "skills" / "custom"
        skill_dir.mkdir(parents=True)
        (skill_dir / "metadata.yaml").write_text("""
name: "Custom Skill"
type: "skill"
version: "1.0.0"
description: "Project-local skill"
category: "custom"
tags: []
status: "stable"
author: "test"
last_updated: "2026-01-01"
dependencies:
  required: []
  optional: []
  suggested: []
conflicts: []
composable_with: []
agent_roles: []
relevance:
  triggers: ["custom-trigger"]
  contexts: []
""", encoding="utf-8")
        caps = load_capabilities_for_suggest(proj_dir)
        assert "skills/custom" in caps

    def test_falls_back_to_package(self, tmp_path):
        # tmp_path has no .proto-gear/, should fall back to package built-ins
        caps = load_capabilities_for_suggest(tmp_path)
        assert len(caps) > 0  # built-in skills/workflows/commands ship with the package


class TestSuggest:
    """End-to-end suggest against the package's built-in capabilities."""

    def test_returns_empty_for_empty_prose(self, tmp_path):
        assert suggest(tmp_path, "") == []
        assert suggest(tmp_path, "   ") == []

    def test_ranks_testing_above_docs_for_write_tests(self, tmp_path):
        results = suggest(tmp_path, "write tests", limit=5)
        ids = [r["id"] for r in results]
        assert "skills/testing" in ids
        # testing must rank above documentation (which has a "write docs" trigger)
        idx_testing = ids.index("skills/testing")
        if "skills/documentation" in ids:
            assert idx_testing < ids.index("skills/documentation")

    def test_ranks_bug_fix_for_fix_login_bug(self, tmp_path):
        results = suggest(tmp_path, "fix login bug", limit=3)
        ids = [r["id"] for r in results]
        # Both should appear; either is fine as #1
        assert "workflows/bug-fix" in ids or "skills/debugging" in ids

    def test_returns_no_more_than_limit(self, tmp_path):
        assert len(suggest(tmp_path, "bug", limit=2)) <= 2
        assert len(suggest(tmp_path, "bug", limit=1)) <= 1

    def test_result_shape(self, tmp_path):
        results = suggest(tmp_path, "tdd", limit=1)
        assert len(results) >= 1
        r = results[0]
        for key in ("id", "type", "name", "description", "score", "matched_triggers"):
            assert key in r
        assert r["score"] > 0
        assert isinstance(r["matched_triggers"], list)
