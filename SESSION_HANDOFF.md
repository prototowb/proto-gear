# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**v0.22.0 is shipped.** The release is cut, tagged, and live on GitHub; `main`
and `development` are **in sync** (0/0). There is **no teed-up next thrust**. The
natural candidates, in rough priority order:

1. **Dogfood the frontier-era init intake** (the standout): proto-gear's own
   `PROJECT_SPECIFICATIONS.md` still has no `## Boundaries & Invariants` section.
   Adding one pushes repo-specific boundaries into the generated Critical Rules
   of every host mirror via the sync bridge (`sync_context.read_project_boundaries`,
   heading constant `BOUNDARIES_HEADING`). Do this deliberately — it changes
   AGENT_CONTEXT.md for every agent. This is the first real consumer of the
   PROTO-100 machinery.
2. **A new capability thrust** — open a fresh PROTO ticket. No specific gap is
   pending; pick from product judgment.
3. Speculative-only backlog: a `standard` middle output profile between
   `frontier` and `verbose` — build only if a consumer needs it.

## Shipped this session — v0.22.0 release (PR #72)

Cut the accumulated `development` work (**PROTO-093 → PROTO-100**, PRs #64–#71)
into a minor release. Scope note for future reference: the v0.21.0 tag predated
PROTO-093, so v0.22.0 spans more than the "PROTO-096–100" the prior handoff
implied — it also includes PROTO-093 (init/update track more state files),
PROTO-094 (setup-test isolation), and PROTO-095 (existing-install guard, drop
aider), plus the whole interactive-shell arc (PROTO-096–099) and frontier-era
init planning (PROTO-100 / ADR-004).

Release mechanics done per `docs/dev/release-workflow.md`:
- Version `0.21.0 → 0.22.0` in `pyproject.toml` + `__init__.py`.
- `CHANGELOG.md` `[0.22.0]` entry; `PROJECT_STATUS.md` yaml + Releases row;
  `docs/dev/readiness-assessment.md` v0.22.0 update section.
- `pg sync-context` regenerated AGENT_CONTEXT.md + all four host mirrors (managed
  block now reads v0.22.0 / 2026-07-18).
- Removed the completed `proto-gear-steering-action-plan.md` (v0.21.0 work shipped).
- PR #72 → main; 16-job CI (macOS/Linux/Windows × 3.8–3.12 + lint + coverage) all
  green; merged (merge commit `d670295`); tagged `v0.22.0`; GitHub release live.
- `main` merged back to `development`; branches in sync.

## Current State

- **On `development`, in sync with `main`** (both at the v0.22.0 merge). Last
  release **v0.22.0** (2026-07-18). **1164 tests pass** (bare `pytest tests/`, CI
  parity); `black --check` clean; `pg doctor` green (32 checks).
- **The UI shell is the home surface** (PROTO-096–099): bare `pg` in a TTY →
  navigate/pick shell; Setup → Init fronts the real `pg init`, so the frontier-era
  init intake (PROTO-100) is reachable UI-first.
- **Init is a planning intake, not a template configurator** (ADR-004, Accepted):
  intent capture (description → boundaries → conventions) over one confirmable
  detected plan; intent lands in durable state (specs stub, `## Boundaries &
  Invariants` → Critical Rules via sync, seed lesson).
- **Five disciplines** ship on the unmodified core; ADR-002 supervision
  primitives complete. (Unchanged.)

## Pending / In Progress

- Nothing in flight (no open branches/PRs). The release branch `release/v0.22.0`
  remains on the remote — delete it if you want cleanup (`git push origin
  --delete release/v0.22.0`).
- Uncommitted local-only change: `.claude/settings.local.json` (added dev
  permission entries) — intentionally not part of the release; leave or commit
  locally as you prefer.

## Conventions In Force

- **UI-first:** every feature reachable via the navigate/pick shell first;
  commands are secondary shortcuts.
- **Merge-on-green autonomy:** one PR per thrust; branch → PR → CI →
  merge-on-green; confirm only at genuine forks. `development` is open for
  small/local commits; only `main` is PR-protected.
- **Steering philosophy (Fable-5):** conditions over keyword triggers;
  boundaries over behavioral micro-tuning; durable state over procedural prose;
  enforce invariants with exit codes. Project boundaries have a durable home:
  specs `## Boundaries & Invariants` → Critical Rules via sync.
- **Scope discipline:** engineering-only. New discipline = zero core edits.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower
  never imports higher.
- **Testing:** pure helpers unit-tested; interactive flows driven by scripted
  fakes/monkeypatched prompts. Verify CI parity with bare `pytest tests/`.
- **Releases:** follow `docs/dev/release-workflow.md`; GitHub release is
  mandatory after tagging; sync `main` back to `development`.
