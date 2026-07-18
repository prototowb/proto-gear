# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**v0.22.0 is shipped; PROTO-101 (dogfood) and PROTO-102 (supervision inbox) have
landed on `development`.** The release is live on GitHub; `development` is now
ahead of `main` by the post-release feature accumulation (handoff + PROTO-101 +
PROTO-102). There is **no teed-up next thrust**. Candidates, rough priority:

1. **A new capability thrust** — open a fresh PROTO ticket. No specific gap is
   pending; pick from product judgment. (A natural inbox follow-on: a
   *supervision-breach* view — rows already past a gate that was never signed,
   e.g. deployed-without-approval. The inbox deliberately scopes to "awaiting",
   not "breached"; the breach view is the complement.)
2. **Cut v0.23.0 eventually** — once enough post-v0.22.0 work accumulates on
   `development`. Two feature tickets now sit unreleased.
3. Speculative-only backlog: a `standard` middle output profile between
   `frontier` and `verbose` — build only if a consumer needs it.

## Just shipped — PROTO-102: supervision inbox (PR #74)

The cross-discipline "what needs a human right now?" cockpit — the supervision
surface the product was missing. `module_core/inbox.py::collect_inbox` makes a
single generic pass over every discipline's state surface and returns each row
sitting at a **pending, required, human** gate, reusing
`pipeline.collect_supervision_gates` + `trace`'s cell helpers (zero code per new
discipline). Keyed by the row itself so an ID+Ref row counts once.
`_is_terminal` filters historical/shipped rows (terminal Stage or a filled
completion-date column) so long-closed tickets with legacy-empty evidence don't
masquerade as pending — this is what made the live inbox read "clear" instead of
16 false items. Surfaced as `pg inbox [--json]` **and** a Home-menu item with a
live pending-count badge (UI-first per the PROTO-101 boundary). 13 new tests;
suite **1177 passing**; AGENT_CONTEXT held at 1800/1800 (trimmed sibling CLI
descriptions to fit the new cheatsheet line).

## Shipped earlier this session — PROTO-101: dogfood the Boundaries & Invariants bridge (PR #73)

First real consumer of the PROTO-100 sync bridge. Added a curated
`## Boundaries & Invariants` section to proto-gear's own
`PROJECT_SPECIFICATIONS.md`; its **four** top-level bullets now fold into the
generated **Critical Rules** (`sync_context._build_critical_rules`) and mirror
into every host config on `pg sync-context`. Promoted set (kept deliberately
small): engineering-scope-only, layering, zero-core-edits, UI-first.

**Design note worth keeping**: promoting all six candidate boundaries pushed the
generated block ~128 tokens over `AGENT_CONTEXT_TOKEN_BUDGET` (1800). The
disciplined resolution — dogfooding the block's own "keep the skim a skim"
philosophy — was to promote only invariants an agent doing real work could
*cross*, and leave lower-risk ones (`pg` executes nothing from bundles; AGENTS.md
single entry point) documented in Principles/Non-Goals. Block now sits at exactly
**1800/1800**; `pg doctor` green (32 checks, 0 warnings). The section intro
records this rationale so a future editor doesn't naively re-expand it.

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
