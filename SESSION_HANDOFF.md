# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## What Just Shipped

Branches (stack, oldest first — each rebases onto the previous once merged):
`feature/PROTO-039` (docs, unmerged) → `chore/PROTO-042-split-monolith` →
**`chore/PROTO-046-rehome-module-core` (current HEAD)**.

**PROTO-046 — module_core re-homing (ADR-001 Phase B item 5) — PART 1 DONE
(IN_PROGRESS).**
- `af99831` moved the 7 department-agnostic modules into `module_core/`
  (capability_metadata, capability_index_builder, sync_context, discovery,
  doctor, module_manifest, metadata_parser). `git mv` preserved history; all
  importers + every test's import/patch target updated (no shims); fixed the
  moved modules' `Path(__file__).parent` → `.parent.parent` for package-root
  resources (capabilities/, modules/, AGENT_CONTEXT.template.md). 519 green,
  doctor 19/19, CLI verified.
- **Remaining (PROTO-046 part 2):** re-home the engineering leaves
  (`templates`, `detection`, `status_commands`, `template_updater`,
  `interactive_wizard`) into `modules/engineering/`. **Do this first:** add a
  `package_root()` helper (returns `Path(proto_gear_pkg.__file__).parent`) and
  route every bundled-resource lookup through it — `templates.py` alone has 4
  `Path(__file__).parent` refs to root `.template.md` files + `capabilities/`,
  which at 2 levels deep would otherwise need brittle `.parent.parent.parent`.
  Also untangle `interactive_wizard`'s `from .proto_gear import
  discover_available_templates` inversion into a sibling `from .templates`
  import. Direct test importers to repoint: test_template_updater,
  test_update_integration (template_updater); test_essential_integration,
  test_wizard_focused (interactive_wizard). Use absolute imports
  (`from proto_gear_pkg.X`) inside moved engineering modules.

### Earlier this session (on `chore/PROTO-042-split-monolith`)

**PROTO-042 — monolith split (ADR-001 Phase A) — COMPLETE.** `proto_gear.py`
went 2,476 → 695 lines across four commits, each behind green tests with zero
test changes (the engine re-exports every moved symbol, so
`proto_gear_pkg.proto_gear.*` patch targets still resolve):
- `205db27` `cli/` package — `parser.py` (argparse) + `app.py` (dispatch)
- `5768afb` `presentation.py` — logos, splash, help, console input
- `19352ef` `detection.py` — project/env/git detection
- `e1e0a56` `templates.py` — template gen + capability install
- Remaining engine (`setup_agent_framework_only`, `interactive_setup_wizard`,
  `run_simple_protogear_init`) + compat facade stays in `proto_gear.py`.

**PROTO-045 — module contract (ADR-001 Phase B foundation) — COMPLETE.**
- `94fc6ae` `module_manifest.py` — `ModuleManifest` schema + load/discover/
  validate; `modules/engineering/module.yaml` (module #1, dogfooded);
  `doctor.check_modules`; `setup.py` ships `modules/**/*.yaml`. **Acceptance
  test passes**: a toy second module loads with zero core edits (ADR-001 item 6).
- `1fc12ca` `pg module list` / `pg module show` (+ `--json`) — CLI is now
  module-aware.

**Tests**: 519 passing (was 489 at session start). `pg doctor`: 19/19 green.

## Pending / In Progress

- **PROTO-046 part 2** (next): engineering-leaf re-homing — see "What Just
  Shipped" for the exact plan (`package_root()` helper first, then move the 5
  leaves into `modules/engineering/`).
- **PROTO-043**: supervision gates as data (contract item 5) — `gates:` in
  workflow metadata + doctor check.
- **PROTO-044**: repo hygiene (tracked `.backup` files, root strays).
- **PROTO-039** (docs: PROJECT_SPECIFICATIONS + ADR-001 + wizard fix) still
  needs its PR (feature → development → main). This branch stacks on it.
- **Deferred polish**: add `pg module` to `sync_context.CLI_COMMANDS` so it
  appears in AGENT_CONTEXT.md — skipped here to avoid dogfood host-file churn;
  fold into the next sync/release pass.

## Conventions In Force

- **Monolith-split invariant**: `proto_gear.py` re-exports moved symbols; the
  patched-and-invoked orchestrators (`setup_*`, `run_simple_*`) stayed in the
  engine so `patch('proto_gear_pkg.proto_gear.X')` keeps working. This trick
  ends at PROTO-046 (callers move → update patch targets in tests).
- ADRs live in `docs/dev/adr/`. Every non-trivial change asks: "generic module
  core, or engineering-module specific?" (ARCHITECTURE.md → Target Architecture).
- New department = new `modules/<name>/module.yaml` — zero core edits.
- SESSION_HANDOFF.md remains agent-owned; replace entirely at session end.

## Open Questions

- PROTO-046 boundary calls: is `detection.py` generic (module_core) or
  engineering (project tech-stack detection is engineering-flavoured)? Is
  `presentation.py`/`ui_helper.py` core or shared-util? Draw these before moving.
- Gates-as-data granularity (PROTO-043): per-workflow-step or per-workflow?

---
*Agent-maintained. Replace entirely at session end.*
