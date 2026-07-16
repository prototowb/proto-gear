# Lessons — accumulated knowledge

This directory is **yours to write to.** When you learn something worth keeping —
a correction, a confirmed approach, a non-obvious gotcha about this project —
record it here as one lesson per file. Delete a lesson when it turns out wrong.

This is different from `SESSION_HANDOFF.md`: that file is *current state* (replace
it every session); lessons are *accumulated knowledge* that persists across
sessions.

## Format

One lesson per markdown file. Lead with an `# H1` title, then a `> ` one-line
summary (this is what shows up in `INDEX.md`), then the body:

```markdown
# Prefer bare `pytest tests/` for CI parity

> The pre-commit hook and CI both run bare `pytest tests/`; `python -m pytest`
> can pass locally while CI fails on import paths.

Longer explanation, links, examples…
```

Name files with a short kebab-case slug (e.g. `ci-parity-pytest.md`).

## Index

`INDEX.md` is regenerated from the lesson files by `pg sync-context`
(inside the managed markers). Don't hand-edit the managed block.
