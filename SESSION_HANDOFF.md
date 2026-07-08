# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## What Just Shipped

Branches (stack, oldest first — each rebases onto the previous once merged):
`feature/PROTO-039` (docs) → `chore/PROTO-042-split-monolith` →
`chore/PROTO-046-rehome-module-core` →
**`feature/PROTO-043-supervision-gates` (current HEAD)**.
PRs open: #2 (039→development), #3 (042→039), #4 (046→042). PROTO-043 is a new
branch off PROTO-046, PR to be opened stacked on #4.

**PROTO-043 — supervision gates as data (contract item 5) — COMPLETE.**
- `0a986e6` `Gate` dataclass + `WorkflowMetadata.gates`; `doctor.
  check_supervision_gates` (structural: gate needs id+description → error;
  coverage: release/deploy/publish output with no gate → warning). Dogfooded
  gates on release, complete-release, hotfix, code-review-process. Gates render
  in `pg capabilities show`. pg doctor 23/23. 529 tests.

**PROTO-046 — module_core + modules/engineering re-homing (ADR-001 Phase B
item 5) — COMPLETE.** The package is now cleanly layered:
- `cli/` — dispatch · `module_core/` — 7 generic modules (capability_metadata,
  capability_index_builder, sync_context, discovery, doctor, module_manifest,
  metadata_parser) · `modules/engineering/` — 5 engineering modules (templates,
  detection, status_commands, template_updater, interactive_wizard) +
  module.yaml · root — shared (ui_helper, presentation, cli_commands, agent_*)
  + `proto_gear.py` (entry facade + init orchestration) + `paths.py`.
- `af99831` module_core move; `370fe79` engineering move. `git mv` preserved
  history throughout; all importers + test import/patch targets updated at the
  source (no shims). New `paths.package_root()` is the single depth-independent
  anchor for bundled resources (capabilities/, modules/, *.template.md) — no
  more `Path(__file__).parent` arithmetic. `interactive_wizard`'s facade
  inversion untangled to a sibling `.templates` import.
- Note: init orchestration (`setup_agent_framework_only` etc.) deliberately
  stays in `proto_gear.py` — it's the pyproject entry point and the test-patch
  anchor (`patch('proto_gear_pkg.proto_gear.detect_*')`); moving it buys little
  and breaks those tests. `agent_*` left at root as a shared subsystem.

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

- **PROTO-044** (next): repo hygiene (tracked `.backup` files, root strays:
  `integrate_templates.py`, `test_composition_engine.py`,
  `wizard_demo_walkthrough.md`).
- **PR stack** (#2 → #3 → #4, + PROTO-043 PR stacked on #4) awaits review; merge
  bottom-up. GitHub auto-retargets each base as the one below merges.
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
