# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**The entire original backlog (PROTO-047→050) is done, plus PROTO-052 (seam S1
supervision half). PROTO-050 is in review as PR #14; everything else is merged.
There is no open ticket after #14 merges — pick from the follow-ups below.**

1. **Merge PR #14** (`chore/proto-050-coverage` → `development`), then
   `git checkout development && git pull`. It branches from `development` (which
   already has PROTO-052), so no conflict expected.
2. **Then choose the next thrust** (none are ticketed yet — file with
   `pg ticket create`):
   - **S1 listing half** — route the *host-side* capability surfaces
     (`discovery`/`pg suggest`, `sync_context`/AGENT_CONTEXT, `agent_config`,
     wizard) through `module_host.iter_capability_sources()`, so a module's own
     capabilities also surface in suggestions/context, not just the gate audit
     (PROTO-052 did the audit half). See `docs/dev/content-module-design.md` §6.
     Resolve the open question below first.
   - **Phase C success criterion** — an agent operates a real content item
     `draft → gate → publish` end-to-end with every gate hit logged. This is the
     spec's actual Phase C completion (PROTO-047/052 were entry + plumbing).
   - **Coverage keep-up** — now measurable via
     `pytest --cov=core/proto_gear_pkg --cov-report=term-missing` (70.04%).
     The interactive wizards (`interactive_wizard`, `agent_wizard`) are the big
     untested blocks if a higher bar is wanted; they need questionary mocking.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `d12aab6` (has PROTO-047/048/049/052). **PR #14 open** for
  PROTO-050.
- **748 tests green; coverage 70.04%; `pg doctor` 0 err / 0 warn / 25 ok;
  `black --check` clean; flake8 E9/F-gate clean.**
- The module platform is now end-to-end: manifest → discovery →
  `pg module list/show` → `pg --module <name> init-surface` → per-module bundled
  `capabilities/` with gate auditing. Content ships its own gated `publish`.
- **Coverage tooling now works.** `pytest.ini` had `[tool:pytest]` (wrong
  section for a pytest.ini file → all options silently ignored). Fixed to
  `[pytest]`; coverage is opt-in (`pytest --cov=...`), not in `addopts`, so the
  pre-commit hook stays fast. `pyproject.toml` has a `dev` extra
  (`pytest-cov`, `black`, `flake8`).

## Shipped this cycle (all merged unless noted)

- **PROTO-047** — Content module (2nd contract impl). PR #10.
- **PROTO-048** — multi-module hosting (`pg --module … init-surface`), seam S2. PR #11.
- **PROTO-049** — advertise `pg module` in AGENT_CONTEXT cheatsheet. PR #12.
- **PROTO-052** — manifest-driven capability sources (seam S1, supervision half);
  content's gated `publish`. PR #13.
- **PROTO-050** — core coverage 45%→70% + pytest config fix. **PR #14 open.**

## Pending / In Progress

- **PR #14 awaiting merge.**
- **Follow-ups (unticketed):** S1 listing half → Phase C end-to-end → coverage
  keep-up (see step 2).
- **Formatting enforced via git hook, not CI.** `dev/hooks/pre-commit` blocks
  commits failing `black --check` / flake8. Enable once per clone:
  `git config core.hooksPath dev/hooks` (already set here). Fix: `black core/
  tests/`.

## Conventions In Force

- **Layering:** `cli/` (top) → `module_core/` (generic) → `modules/<dept>/`
  (department). Lower never imports higher. Generic new capability = a
  `module_core` primitive (`module_host.py`), never engineering-routed. New
  department = a `modules/<name>/` directory (manifest + optional
  `capabilities/` + state-surface template) — **zero core edits** to add one.
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:`);
  `pg doctor` enforces structure + coverage across the shared root AND every
  module's own `capabilities/`.
- **Testing:** business logic is tested via argparse.Namespace + capsys + tmp
  dirs (see `tests/test_cli_*`, `test_status_commands`); interactive questionary
  wizards are out of scope. Measure coverage with `pytest --cov`.
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs only on PRs targeting `main`/`development`.
- **Regen noise:** `AGENT_CONTEXT.md` / host configs carry a `Generated:`
  timestamp `pg` rewrites on any run — `git restore` them if they show up as a
  diff with no content change.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions (for the S1 listing half)

- When host-side listings become multi-source, does the host's single
  `.proto-gear/` stay the shared `capabilities_root` for all modules, or does
  each module namespace its own subtree (e.g. `.proto-gear/content/`)? Both
  manifests currently declare `.proto-gear`. Decide before wiring the listing
  surfaces — it governs whether two modules' capability IDs can collide in
  `pg suggest` / AGENT_CONTEXT.

---
*Agent-maintained. Replace entirely at session end.*
