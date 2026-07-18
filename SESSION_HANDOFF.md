# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**The interactive-frontier effort is complete (3/3 phases).** PROTO-100 shipped
(PR #71, squash `fdf97f0`); ADR-004 is **Accepted** with all four open
questions decided in the ADR itself. There is **no teed-up next thrust** — the
natural candidates, in rough priority order:

1. **Cut the next release** (v0.22.0): `development` is ahead of `main` by the
   whole PROTO-096–100 arc (PRs #67–#71). Follow `docs/dev/release-workflow.md`
   when ready.
2. Dogfood the new intake: proto-gear's own `PROJECT_SPECIFICATIONS.md` has no
   `## Boundaries & Invariants` section yet — adding one would push repo-specific
   boundaries into every host mirror via the new sync bridge (do this
   deliberately; it changes AGENT_CONTEXT.md for every agent).
3. Speculative-only backlog: a `standard` middle output profile — build only if
   a consumer needs it.

## Shipped this session — PROTO-100: frontier-era init planning (PR #71)

Fresh `pg init` reframed from **template configurator** (Quick/Full/Minimal
presets + "which .md files?") to **state-elicitation planning intake** per
ADR-004. What exists now:

- **`modules/engineering/init_planning.py`** (new, pure): detection-driven plan
  (git → BRANCHING, tests → TESTING, remote → CONTRIBUTING, capabilities always,
  `frontier` profile, derived prefix), `plan_files` display rows, specs-stub /
  seed-lesson / handoff-pending builders. All unit-tested directly.
- **`run_enhanced_wizard` is the intake**: skippable intent capture (one-liner →
  boundaries loop → conventions loop) → one confirmable detected-plan summary →
  Accept / Change prefix / Customize (advanced) / Cancel. The Quick/Full/Minimal
  preset front and `PRESETS`/`_apply_preset_config` are **deleted**; the
  granular Custom path survives as Customize. Non-interactive `--flags` and
  guided re-init (`run_incremental_wizard`, PROTO-099) untouched.
- **Where intent lands**: description → specs stub; boundaries → specs
  `## Boundaries & Invariants` (**parsed by `sync_context.read_project_boundaries`
  into the generated Critical Rules on every sync** — the heading constant
  `BOUNDARIES_HEADING` lives in sync_context, imported by init_planning so
  writer/reader can't drift); conventions → specs + seed lesson
  `.proto-gear/lessons/house-conventions.md` (indexed). Fresh SESSION_HANDOFF
  gets a "First agent task" line pointing at the intake.
- **Engine contract fix**: an explicitly-passed *empty* `core_templates`
  selection no longer falls through to the legacy branching→TESTING branch
  (`if core_templates is not None:`), so init writes exactly what the accepted
  plan showed. Existing PROJECT_SPECIFICATIONS.md is never clobbered.

## Current State

- **On `development`, unreleased.** Ahead of `main` by PROTO-096–100 (PRs
  #67–#71) + status commits. Last release **v0.21.0** (2026-07-17); next will be
  **v0.22.0**, cut when you decide. **1164 tests pass** (bare `pytest tests/`,
  CI parity); full 14-job matrix + coverage green on #71; `black --check` clean;
  `pg doctor` green.
- **The UI shell is the home surface** (PROTO-096–099): bare `pg` in a TTY →
  navigate/pick shell; Setup → Init fronts the real `pg init` subprocess, so the
  new intake is reachable UI-first with zero shell changes.
- **Fable-5 steering surface fully migrated**: v0.21.0 did the content
  (description-routed capabilities, profile tiering, lessons layer, working
  agreement, branch guard); PROTO-100 did the last surface — the init planning
  model itself. Nothing pre-Fable-5 remains on the markdown/init surface.
- **Five disciplines** ship on the unmodified core; ADR-002 supervision
  primitives complete. (Unchanged this session.)

## Pending / In Progress

- Nothing in flight (no open branches/PRs). Release cut is the next decision.

## Conventions In Force

- **UI-first:** every feature reachable via the navigate/pick shell first;
  commands are secondary shortcuts.
- **Merge-on-green autonomy:** one PR per thrust; branch → PR → CI →
  merge-on-green; confirm only at genuine forks. `development` is open for
  small/local commits; only `main` is PR-protected.
- **Steering philosophy (Fable-5):** conditions over keyword triggers;
  boundaries over behavioral micro-tuning; durable state over procedural prose;
  enforce invariants with exit codes. Project boundaries now have a durable
  home: specs `## Boundaries & Invariants` → Critical Rules via sync.
- **Scope discipline:** engineering-only. New discipline = zero core edits.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower
  never imports higher (init_planning imports sync_context's heading constant —
  higher importing lower, correct direction).
- **Testing:** pure helpers unit-tested; interactive flows driven by scripted
  fakes/monkeypatched prompts (see `test_init_planning.py`,
  `test_wizard_focused.py`). Verify CI parity with bare `pytest tests/`.
