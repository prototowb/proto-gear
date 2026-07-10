# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**Scope was corrected this session: Proto Gear is an OS for the *software-
engineering circle*, whose "departments" are engineering disciplines (dev, QA,
DevOps, security, docs, release/PM) — NOT a whole-business "agency OS."
Content/marketing is out (that's honk, a separate product). PROTO-053 removed the
content module and reframed the vision accordingly; it's in review as PR #15.**

1. **Merge PR #15** (`chore/PROTO-053-engineering-only-teardown` → `development`),
   then `git checkout development && git pull`. Branches from `development`
   (which has PROTO-047–052); the content module it removes was added there.
2. **Then Phase C is open again, correctly scoped:** ship a **second engineering-
   discipline module** (e.g. QA/Test or DevOps/SRE) as the contract falsifier —
   its own state surface (test-plan / defect queue) + supervision gates, with
   **zero core edits**. See `PROJECT_SPECIFICATIONS.md` §6 (Phase C) and
   `docs/dev/adr/ADR-001` action item 7. File with `pg ticket create`.
3. **Other open follow-up:** the S1 *listing* half — route host-side capability
   surfaces (`discovery`/`pg suggest`, `sync_context`/AGENT_CONTEXT,
   `agent_config`, wizard) through `module_host.iter_capability_sources()` so a
   department's own capabilities surface in suggestions/context, not just the
   gate audit. Resolve the open question below first.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `4a3caaa` (has PROTO-047–052). **PR #15 open** for PROTO-053.
- **736 tests green; `pg doctor` 0 err / 0 warn / 23 ok; `black --check` clean.**
  (748→736: −12 content/obsolete tests. 25→23 doctor checks: content's manifest +
  gate checks correctly gone.) Coverage still measurable via
  `pytest --cov=core/proto_gear_pkg --cov-report=term-missing` (was 70% at #14).
- **Vision (reframed, PROTO-053):** proto-gear = **software-engineering OS**.
  Engineering is module #1 (the generalist SDLC discipline); future modules are
  engineering disciplines. The departmental *platform* (`module_core/`,
  `modules/engineering/`, `module.yaml`, `module_host`, `module_manifest`,
  `pg --module` / `pg module` / `init-surface`, supervision gates) **stays** — it
  was kept, only rescoped. Only the content/marketing module was removed.
- **honk** (`../_Plugins/honk/`) is the real content/marketing product — a mature
  Node pipeline (queue, `policy-gate.js`, social adapters). It is NOT a proto-gear
  module; do not reintroduce content features here. (honk was also mid-`git rm
  --cached` refactor when checked — don't touch it without care.)

## Shipped this cycle (all merged unless noted)

- **PROTO-047** — Content module (Phase-C falsifier). Merged, then **removed by
  PROTO-053**.
- **PROTO-048** — multi-module hosting (`pg --module … init-surface`), seam S2. Merged.
- **PROTO-049** — advertise `pg module` in AGENT_CONTEXT cheatsheet. Merged.
- **PROTO-052** — manifest-driven capability sources (seam S1, supervision half).
  Merged; its content *demo* removed by PROTO-053, the machinery kept.
- **PROTO-050** — core coverage 45%→70% + pytest config fix. Merged (PR #14).
- **PROTO-053** — engineering-only reframe: remove content module, rescope vision
  agency→software-engineering OS. **PR #15 open.**

## Pending / In Progress

- **PR #15 awaiting merge.**
- **Phase C (rescoped):** second *engineering* discipline module — see step 2.
- **S1 listing half** — see step 3 (not ticketed).
- **Formatting enforced via git hook, not CI.** `dev/hooks/pre-commit` blocks
  commits failing `black --check` / flake8. Enable once per clone:
  `git config core.hooksPath dev/hooks` (already set here). Fix: `black core/
  tests/`.

## Conventions In Force

- **Scope discipline:** proto-gear is engineering-only. "Departments" = engineering
  disciplines. Anything content/marketing/sales/finance is out of scope by design
  (PROJECT_SPECIFICATIONS.md §8). If a request implies a non-engineering
  department, flag it rather than build it.
- **Layering:** `cli/` (top) → `module_core/` (generic) → `modules/<dept>/`
  (discipline). Lower never imports higher. Generic new capability = a
  `module_core` primitive; new discipline = a `modules/<name>/` dir (manifest +
  optional `capabilities/` + state-surface template) — **zero core edits**.
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:`);
  `pg doctor` enforces structure + coverage across the shared root AND every
  module's own `capabilities/`.
- **Testing:** business logic via argparse.Namespace + capsys + tmp dirs;
  interactive questionary wizards out of scope. Platform tests use a neutral `qa`
  toy department or engineering (not a bundled second module). Measure coverage
  with `pytest --cov`.
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs only on PRs targeting `main`/`development`.
- **Regen noise:** `AGENT_CONTEXT.md` / host configs carry a `Generated:`
  timestamp `pg` rewrites on any run — `git restore` them if they show up as a
  diff with no content change.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions (for the S1 listing half)

- When host-side listings become multi-source, does the host's single
  `.proto-gear/` stay the shared `capabilities_root` for all modules, or does
  each discipline namespace its own subtree (e.g. `.proto-gear/qa/`)? Decide
  before wiring the listing surfaces — it governs whether two disciplines'
  capability IDs can collide in `pg suggest` / AGENT_CONTEXT.

---
*Agent-maintained. Replace entirely at session end.*
