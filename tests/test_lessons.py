"""
Tests for the lessons layer (steering-plan Phase 4):
parsing, loading, validation, and index sync.
"""

import pytest

from proto_gear_pkg.module_core import lessons as L

VALID = "# Title Here\n\n> A one-line summary.\n\nBody text.\n"


class TestParseLesson:
    def test_valid(self):
        assert L.parse_lesson(VALID) == ("Title Here", "A one-line summary.")

    def test_summary_directly_after_title(self):
        assert L.parse_lesson("# T\n> S\n") == ("T", "S")

    def test_missing_title(self):
        assert L.parse_lesson("Just prose\n> summary\n") is None

    def test_missing_summary(self):
        assert L.parse_lesson("# Title\n\nBody without a summary line.\n") is None

    def test_empty(self):
        assert L.parse_lesson("") is None

    def test_title_not_first_nonempty_line(self):
        assert L.parse_lesson("\n\nnot a heading\n# Title\n> s\n") is None


class TestIsLessonFile:
    @pytest.mark.parametrize("name", ["a.md", "ci-parity.md", "001-thing.md"])
    def test_lessons(self, name):
        assert L.is_lesson_file(name) is True

    @pytest.mark.parametrize("name", ["INDEX.md", "index.md", "README.md", "notes.txt"])
    def test_non_lessons(self, name):
        assert L.is_lesson_file(name) is False


class TestLoadAndValidate:
    def test_load_skips_infra_and_malformed(self, tmp_path):
        (tmp_path / "good.md").write_text(VALID, encoding="utf-8")
        (tmp_path / "bad.md").write_text("no title here\n", encoding="utf-8")
        (tmp_path / "README.md").write_text("# Readme\n> x\n", encoding="utf-8")
        (tmp_path / "INDEX.md").write_text("# Index\n> x\n", encoding="utf-8")
        loaded = L.load_lessons(tmp_path)
        assert [x.title for x in loaded] == ["Title Here"]

    def test_load_missing_dir(self, tmp_path):
        assert L.load_lessons(tmp_path / "nope") == []

    def test_validate_flags_malformed_only(self, tmp_path):
        (tmp_path / "good.md").write_text(VALID, encoding="utf-8")
        (tmp_path / "bad.md").write_text("oops\n", encoding="utf-8")
        problems = L.validate_lessons(tmp_path)
        assert len(problems) == 1
        assert problems[0][0].name == "bad.md"

    def test_validate_missing_dir_is_clean(self, tmp_path):
        assert L.validate_lessons(tmp_path / "nope") == []


class TestRenderIndexBlock:
    def test_empty(self):
        block = L.render_index_block([])
        assert L.BEGIN_MARKER in block and L.END_MARKER in block
        assert "No lessons recorded" in block

    def test_lists_lessons(self, tmp_path):
        (tmp_path / "a.md").write_text(VALID, encoding="utf-8")
        block = L.render_index_block(L.load_lessons(tmp_path))
        assert "Title Here" in block
        assert "A one-line summary." in block
        assert "(a.md)" in block


class TestSyncLessonsIndex:
    def _mk(self, tmp_path):
        d = tmp_path / ".proto-gear" / "lessons"
        d.mkdir(parents=True)
        return tmp_path / ".proto-gear", d

    def test_no_dir(self, tmp_path):
        (tmp_path / ".proto-gear").mkdir()
        assert L.sync_lessons_index(tmp_path / ".proto-gear")["status"] == "no-dir"

    def test_creates_index_when_absent(self, tmp_path):
        pg, d = self._mk(tmp_path)
        (d / "a.md").write_text(VALID, encoding="utf-8")
        assert L.sync_lessons_index(pg)["status"] == "created"
        assert "Title Here" in (d / "INDEX.md").read_text(encoding="utf-8")

    def test_missing_markers_left_untouched(self, tmp_path):
        pg, d = self._mk(tmp_path)
        (d / "INDEX.md").write_text("no markers\n", encoding="utf-8")
        assert L.sync_lessons_index(pg)["status"] == "missing-markers"

    def test_update_then_unchanged(self, tmp_path):
        pg, d = self._mk(tmp_path)
        (d / "INDEX.md").write_text(
            f"# Index\n\n{L.BEGIN_MARKER}\nstale\n{L.END_MARKER}\n", encoding="utf-8"
        )
        (d / "a.md").write_text(VALID, encoding="utf-8")
        assert L.sync_lessons_index(pg)["status"] == "updated"
        assert L.sync_lessons_index(pg)["status"] == "unchanged"

    def test_dry_run_would_update(self, tmp_path):
        pg, d = self._mk(tmp_path)
        (d / "INDEX.md").write_text(
            f"{L.BEGIN_MARKER}\nstale\n{L.END_MARKER}\n", encoding="utf-8"
        )
        (d / "a.md").write_text(VALID, encoding="utf-8")
        assert L.sync_lessons_index(pg, dry_run=True)["status"] == "would-update"
        # dry-run wrote nothing
        assert "stale" in (d / "INDEX.md").read_text(encoding="utf-8")
