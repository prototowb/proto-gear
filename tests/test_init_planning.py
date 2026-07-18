"""Tests for the frontier-era init planning intake (PROTO-100 / ADR-004).

Covers the pure planning helpers (detection-driven plan, specs stub, seed
lesson, handoff task), the boundaries → Critical Rules bridge in
sync_context, and an end-to-end init carrying captured intent.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from proto_gear_pkg import proto_gear as engine
from proto_gear_pkg.module_core import lessons as lessons_module
from proto_gear_pkg.module_core.sync_context import (
    BOUNDARIES_HEADING,
    read_project_boundaries,
    generate_agent_context,
)
from proto_gear_pkg.modules.engineering.init_planning import (
    build_detected_plan,
    build_handoff_pending,
    build_seed_lesson,
    build_specs_stub,
    derive_ticket_prefix,
    detect_test_signals,
    plan_files,
)


@pytest.fixture
def workdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return tmp_path


class TestDerivedDefaults:
    def test_prefix_from_name(self):
        assert derive_ticket_prefix("proto-gear") == "PROTOG"
        assert derive_ticket_prefix("my_app") == "MYAPP"

    def test_prefix_falls_back_when_too_short(self):
        assert derive_ticket_prefix("a") == "PROJ"
        assert derive_ticket_prefix("") == "PROJ"


class TestDetectTestSignals:
    def test_false_on_empty_dir(self, tmp_path):
        assert detect_test_signals(tmp_path) is False

    def test_tests_dir(self, tmp_path):
        (tmp_path / "tests").mkdir()
        assert detect_test_signals(tmp_path) is True

    def test_runner_config(self, tmp_path):
        (tmp_path / "pytest.ini").write_text("[pytest]", encoding="utf-8")
        assert detect_test_signals(tmp_path) is True

    def test_test_file_alone_is_not_a_dir_signal(self, tmp_path):
        (tmp_path / "test").write_text("not a dir", encoding="utf-8")
        assert detect_test_signals(tmp_path) is False


class TestPlanFiles:
    def test_always_files_present(self, tmp_path):
        plan = build_detected_plan({}, {}, tmp_path)
        names = [name for name, _ in plan_files(plan)]
        assert "AGENTS.md" in names
        assert "SESSION_HANDOFF.md" in names
        assert "PROJECT_STATUS.md" in names
        assert ".proto-gear/" in names

    def test_conditionals_follow_detection(self, tmp_path):
        (tmp_path / "tests").mkdir()
        plan = build_detected_plan(
            {}, {"is_git_repo": True, "has_remote": True}, tmp_path
        )
        names = [name for name, _ in plan_files(plan)]
        assert "BRANCHING.md" in names
        assert "TESTING.md" in names
        assert "CONTRIBUTING.md" in names


class TestSpecsStub:
    def test_carries_captured_intent(self):
        stub = build_specs_stub(
            project_description="A widget CLI.",
            boundaries=["NEVER push to main"],
            conventions=["All times UTC"],
        )
        assert "A widget CLI." in stub
        assert BOUNDARIES_HEADING in stub
        assert "- NEVER push to main" in stub
        assert "- All times UTC" in stub

    def test_empty_intent_leaves_placeholders(self):
        stub = build_specs_stub()
        assert BOUNDARIES_HEADING in stub
        assert "<!--" in stub  # placeholder comments, no bullets
        assert "\n- " not in stub.split(BOUNDARIES_HEADING)[1].split("##")[0]


class TestSeedLesson:
    def test_none_without_intent(self):
        assert build_seed_lesson() is None
        assert build_seed_lesson(boundaries=[], conventions=[]) is None

    def test_is_a_wellformed_lesson(self):
        content = build_seed_lesson(
            boundaries=["NEVER force-push"], conventions=["Use uv"]
        )
        parsed = lessons_module.parse_lesson(content)
        assert parsed is not None
        title, summary = parsed
        assert "captured at init" in title
        assert summary
        assert "- NEVER force-push" in content
        assert "- Use uv" in content


class TestHandoffPending:
    def test_no_intent_nothing_pending(self):
        assert build_handoff_pending(False, False) == "*Nothing pending.*"

    def test_intent_creates_first_agent_task(self):
        pending = build_handoff_pending(True, True)
        assert "PROJECT_SPECIFICATIONS.md" in pending
        assert "PROJECT_ARCHITECTURE.md" in pending


class TestBoundariesToCriticalRules:
    def test_read_missing_file_is_empty(self, tmp_path):
        assert read_project_boundaries(tmp_path) == []

    def test_reads_bullets_only_from_boundaries_section(self, tmp_path):
        (tmp_path / "PROJECT_SPECIFICATIONS.md").write_text(
            "\n".join(
                [
                    "# PROJECT_SPECIFICATIONS.md",
                    "",
                    BOUNDARIES_HEADING,
                    "",
                    "<!-- a placeholder comment -->",
                    "- NEVER commit secrets",
                    "* NEVER run migrations in CI",
                    "",
                    "## House Conventions",
                    "",
                    "- not a boundary",
                ]
            ),
            encoding="utf-8",
        )
        assert read_project_boundaries(tmp_path) == [
            "NEVER commit secrets",
            "NEVER run migrations in CI",
        ]

    def test_boundaries_land_in_generated_critical_rules(self, tmp_path):
        (tmp_path / "PROJECT_SPECIFICATIONS.md").write_text(
            f"{BOUNDARIES_HEADING}\n\n- NEVER edit generated fixtures\n",
            encoding="utf-8",
        )
        context = generate_agent_context(tmp_path)
        assert "- NEVER edit generated fixtures" in context

    def test_duplicate_base_rule_not_repeated(self, tmp_path):
        rule = "NEVER commit directly to `main` — it lands only via a reviewed PR"
        (tmp_path / "PROJECT_SPECIFICATIONS.md").write_text(
            f"{BOUNDARIES_HEADING}\n\n- {rule}\n", encoding="utf-8"
        )
        context = generate_agent_context(tmp_path)
        assert context.count(f"- {rule}") == 1


class TestInitCarriesIntent:
    def test_intent_flows_into_specs_handoff_and_lesson(self, workdir, capsys):
        result = engine.run_simple_protogear_init(
            force=True,
            with_capabilities=True,
            project_description="A widget CLI.",
            boundaries=["NEVER push to main"],
            conventions=["All times UTC"],
        )
        assert result["status"] == "success"

        specs = (workdir / "PROJECT_SPECIFICATIONS.md").read_text(encoding="utf-8")
        assert "A widget CLI." in specs
        assert "- NEVER push to main" in specs

        handoff = (workdir / "SESSION_HANDOFF.md").read_text(encoding="utf-8")
        assert "First agent task" in handoff

        seed = workdir / ".proto-gear" / "lessons" / "house-conventions.md"
        assert seed.exists()
        assert "- All times UTC" in seed.read_text(encoding="utf-8")

        # The captured boundary steers every session via the synced context.
        context = (workdir / "AGENT_CONTEXT.md").read_text(encoding="utf-8")
        assert "- NEVER push to main" in context

    def test_existing_specs_never_clobbered(self, workdir, capsys):
        (workdir / "PROJECT_SPECIFICATIONS.md").write_text(
            "# my precious specs", encoding="utf-8"
        )
        result = engine.run_simple_protogear_init(
            force=True,
            boundaries=["NEVER do X"],
        )
        assert result["status"] == "success"
        specs = (workdir / "PROJECT_SPECIFICATIONS.md").read_text(encoding="utf-8")
        assert specs == "# my precious specs"

    def test_no_intent_keeps_handoff_clean(self, workdir, capsys):
        result = engine.run_simple_protogear_init(force=True)
        assert result["status"] == "success"
        handoff = (workdir / "SESSION_HANDOFF.md").read_text(encoding="utf-8")
        assert "*Nothing pending.*" in handoff
