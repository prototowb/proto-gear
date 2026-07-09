# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**All roadmap work through ADR-001 Phase B is merged to `development`. Begin the
backlog immediately with PROTO-047.**

1. **PROTO-047 — Phase C: ship a second (Content) module.** This is the real
   test of the module contract: create `core/proto_gear_pkg/modules/content/`
   with its own `module.yaml` (state surface = a content queue, e.g.
   `CONTENT_QUEUE.md`; publish gates as supervision points) and prove it loads +
   validates with **zero edits to `module_core/`** (the Phase B exit criterion,
   already covered by an acceptance test in `tests/test_module_manifest.py`).
   Start by reading `PROJECT_SPECIFICATIONS.md` §3/§6 and ADR-001 action item 7.
2. Then **PROTO-048** (multi-module hosting: `pg --module <name> <cmd>`; today
   the CLI implicitly assumes the engineering module), **PROTO-049** (surface
   `pg module` in `sync_context.CLI_COMMANDS` → AGENT_CONTEXT), **PROTO-050**
   (raise core coverage to ≥70%).

Branch off `development`, PR back to `development` (see Conventions). Run
`pg status` / `pg ticket list` first.

## Current State

- `development` (tip `782835b` + PR #8 formatting) holds the full
  monolith→module-platform refactor. **529 tests green; `pg doctor` 23/23;
  `black --check` clean; flake8 E9/F-gate clean.**
- Package layout: `cli/` (dispatch) · `module_core/` (7 generic modules:
  capability_metadata, capability_index_builder, sync_context, discovery,
  doctor, module_manifest, metadata_parser) · `modules/engineering/` (5
  engineering modules + `module.yaml`) · root (shared: ui_helper, presentation,
  cli_commands, agent_*, `paths.py`) + `proto_gear.py` (entry facade + init
  orchestration).
- All feature branches merged and deleted from the remote. No open tickets
  except the backlog (PROTO-047–050) + PROTO-051 follow-up below.

## Shipped this cycle (all MERGED to development)

- **PROTO-039/040/041** — vision (`PROJECT_SPECIFICATIONS.md`), ADR-001, wizard
  import-crash fix. (PRs #2)
- **PROTO-042** — monolith split, `proto_gear.py` 2,476→695 lines
  (`cli/`, `presentation`, `detection`, `templates`). (PR #7, replaced #3)
- **PROTO-045** — module contract: `module_manifest.py` +
  `modules/engineering/module.yaml` + `doctor.check_modules` + zero-core-edit
  acceptance test + `pg module list/show`. (PR #7)
- **PROTO-046** — re-home into `module_core/` + `modules/engineering/`;
  `paths.package_root()`. (PR #4)
- **PROTO-043** — supervision gates as data: `Gate` +
  `doctor.check_supervision_gates`; gates on release/complete-release/hotfix/
  code-review-process; shown in `pg capabilities show`. (PR #5)
- **PROTO-044** — repo hygiene: untracked stale backups, relocated root strays
  to `dev/scripts/` + `docs/dev/`, gitignored `*.backup`/`*.bak`. (PR #6)
- **PROTO-051** — black-formatted the whole repo (49 files) to green the CI
  `black --check` gate. (**PR #8 — merging now with this handoff update.**)

## Pending / In Progress

- **Backlog (start next session):** PROTO-047 (Phase C Content module) → 048
  (multi-module hosting) → 049 (cheatsheet sync) → 050 (coverage ≥70%).
- **PROTO-051 — formatting enforced via git hook, not CI.** This is a private
  repo without required-status-check / branch-protection support, so black
  can't be enforced server-side. Instead a version-controlled hook
  (`dev/hooks/pre-commit`) BLOCKS commits that fail `black --check` / flake8.
  **Enable once per clone:** `git config core.hooksPath dev/hooks` (already set
  in this checkout). If black flags a file: `black core/ tests/`.

## Conventions In Force

- **Layering:** `cli/` (top) → `module_core/` (generic) → `modules/<dept>/`
  (department). Lower never imports higher. Every non-trivial change asks:
  "generic core, or engineering-specific?" (ARCHITECTURE.md → Target
  Architecture). New department = new `modules/<name>/module.yaml` — **zero core
  edits** (enforced by the acceptance test).
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:`);
  `pg doctor` enforces structure + coverage. Release/deploy/publish workflows
  must declare a gate.
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI only runs on PRs targeting `main`/`development`, and
  **`--delete-branch` on a stacked-PR base auto-closes its dependents** — merge
  bottom-up, or retarget dependents to `development` before merging.
- **Formatting is gated by the pre-commit hook** (`dev/hooks/pre-commit`, via
  `core.hooksPath`) — commits fail on `black --check`. Run `black core/ tests/`
  to fix. Not enforceable in CI (private repo, no required checks).
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions (for PROTO-047)

- Content module state surface: single `CONTENT_QUEUE.md` table, or a
  `.proto-gear`-style structured queue? What are its capabilities (draft,
  review, schedule, publish) and their triggers?
- Does the toy/real second module expose any missing seam in `module_core`
  (the falsifier)? If it needs a core edit, the contract is wrong — capture it.

---
*Agent-maintained. Replace entirely at session end.*
