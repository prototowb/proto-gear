"""
Lessons — the agent-writable accumulated-knowledge layer (steering-plan Phase 4).

`SESSION_HANDOFF.md` records *current state* (replace-not-append). Lessons record
*accumulated knowledge*: one lesson per file, written by agents as they learn —
corrections and confirmed approaches alike — and deleted when they turn out wrong.
Straight from the Fable 5 guidance: "provide a place to write notes… the model
does a good job of updating skills on the fly based on what it learns."

Structure is machine-validated (`doctor.check_lessons`) but the content is the
agent's to own. A lesson file lives under ``.proto-gear/lessons/`` and is:

    # <Title>

    > <one-line summary — used in the generated index>

    <body: the lesson, freely formatted>

``README.md`` and ``INDEX.md`` in the directory are infrastructure, not lessons,
and are skipped. The index is regenerated from the lesson files into a managed
block by ``sync_lessons_index`` (wired into ``pg sync-context``).
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

LESSONS_DIRNAME = "lessons"

BEGIN_MARKER = "<!-- proto-gear:lessons-index begin -->"
END_MARKER = "<!-- proto-gear:lessons-index end -->"

# Files in the lessons dir that are infrastructure, not lessons.
_NON_LESSON_NAMES = {"index.md", "readme.md"}

_H1 = re.compile(r"^#\s+(.+?)\s*$")
_SUMMARY = re.compile(r"^>\s*(.+?)\s*$")


@dataclass
class Lesson:
    path: Path
    title: str
    summary: str

    @property
    def filename(self) -> str:
        return self.path.name


def is_lesson_file(path) -> bool:
    """True for a markdown file under lessons/ that is an actual lesson."""
    p = Path(path)
    return p.suffix.lower() == ".md" and p.name.lower() not in _NON_LESSON_NAMES


def parse_lesson(text: str) -> Optional[Tuple[str, str]]:
    """Return ``(title, summary)`` for a well-formed lesson, else ``None``.

    A valid lesson leads with an ``# H1`` title and, as its next non-empty line,
    a ``> blockquote`` one-line summary. Kept deliberately small so agents can
    write lessons by hand without ceremony.
    """
    lines = text.splitlines()
    title = None
    idx = 0
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        m = _H1.match(line)
        if not m:
            return None  # first non-empty line must be the H1 title
        title = m.group(1).strip()
        idx = i + 1
        break
    if not title:
        return None

    for line in lines[idx:]:
        if not line.strip():
            continue
        m = _SUMMARY.match(line)
        if not m:
            return None  # next non-empty line must be the > summary
        return title, m.group(1).strip()
    return None  # no summary line found


def load_lessons(lessons_dir) -> List[Lesson]:
    """Load every well-formed lesson under ``lessons_dir`` (sorted by filename)."""
    lessons_dir = Path(lessons_dir)
    if not lessons_dir.exists():
        return []
    out: List[Lesson] = []
    for path in sorted(lessons_dir.glob("*.md")):
        if not is_lesson_file(path):
            continue
        try:
            parsed = parse_lesson(path.read_text(encoding="utf-8"))
        except OSError:
            continue
        if parsed is None:
            continue
        title, summary = parsed
        out.append(Lesson(path=path, title=title, summary=summary))
    return out


def validate_lessons(lessons_dir) -> List[Tuple[Path, str]]:
    """Return ``(path, problem)`` for each malformed lesson file (empty = all ok)."""
    lessons_dir = Path(lessons_dir)
    problems: List[Tuple[Path, str]] = []
    if not lessons_dir.exists():
        return problems
    for path in sorted(lessons_dir.glob("*.md")):
        if not is_lesson_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as e:
            problems.append((path, f"unreadable: {e}"))
            continue
        if parse_lesson(text) is None:
            problems.append(
                (path, "must lead with an `# H1` title then a `> summary` line")
            )
    return problems


def render_index_block(lessons: List[Lesson]) -> str:
    """Render the managed index block listing every lesson's title + summary."""
    lines = [BEGIN_MARKER]
    if not lessons:
        lines.append(
            "_No lessons recorded yet. Write one when you learn something worth "
            "keeping — see this directory's README._"
        )
    else:
        for lesson in lessons:
            lines.append(
                f"- **[{lesson.title}]({lesson.filename})** — {lesson.summary}"
            )
    lines.append(END_MARKER)
    return "\n".join(lines)


def _replace_managed_block(content: str, block: str) -> Optional[str]:
    pattern = re.compile(
        re.escape(BEGIN_MARKER) + r".*?" + re.escape(END_MARKER), re.DOTALL
    )
    if not pattern.search(content):
        return None
    return pattern.sub(block, content)


def sync_lessons_index(proto_gear_dir, dry_run: bool = False) -> dict:
    """Regenerate ``lessons/INDEX.md``'s managed block from the lesson files.

    Returns ``{"status": ...}``:
      - ``no-dir``       — no lessons directory (nothing to do)
      - ``missing-markers`` — INDEX.md lacks the managed block (left untouched)
      - ``unchanged`` / ``updated`` / ``would-update`` / ``created``
    """
    lessons_dir = Path(proto_gear_dir) / LESSONS_DIRNAME
    if not lessons_dir.exists():
        return {"status": "no-dir"}

    block = render_index_block(load_lessons(lessons_dir))
    index_path = lessons_dir / "INDEX.md"

    if not index_path.exists():
        if dry_run:
            return {"status": "would-create"}
        index_path.write_text(block + "\n", encoding="utf-8")
        return {"status": "created"}

    existing = index_path.read_text(encoding="utf-8")
    replaced = _replace_managed_block(existing, block)
    if replaced is None:
        return {"status": "missing-markers"}
    if replaced == existing:
        return {"status": "unchanged"}
    if dry_run:
        return {"status": "would-update"}
    index_path.write_text(replaced, encoding="utf-8")
    return {"status": "updated"}
