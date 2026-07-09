# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**PROTO-047 & 048 are merged. Two PRs are open for review: #12 (PROTO-049
cheatsheet sync) and #13 (PROTO-052 manifest-driven capability sources). Only
PROTO-050 remains from the original backlog.**

1. **Merge the open PRs** (both branch from `development`, independent):
   - **PR #12** — PROTO-049 (advertise `pg module` commands in the cheatsheet).
   - **PR #13** — PROTO-052 (S1 supervision half; content ships its own gated
     `publish`).
   ⚠️ **Merge-order conflict**: both touch `PROJECT_STATUS.md` (completed table +
   a details section). Merge one, then the second will conflict there — resolve
   by **keeping both** details sections and both completed-table rows. No code
   conflict (disjoint files).
   After merging: `git checkout development && git pull`.
2. **PROTO-050 — raise core coverage to ≥70%** (spec Phase A criterion).
   ⚠️ **Tooling gap**: `coverage`/`pytest-cov` are NOT installed and
   `pytest.ini`'s `--cov` addopts aren't taking effect (the suite runs without
   any coverage output — pytest is reading config elsewhere or ignoring it).
   First `pip install pytest-cov`, confirm `pytest --cov=core` actually reports,
   then measure the baseline (last recorded 47%) and target the biggest gaps
   (`capability_metadata.py`, `templates.py`, `doctor.py`, the wizards).
3. **Follow-up — S1 listing half** (not yet ticketed): route the *host-side*
   capability surfaces (`discovery`/`pg suggest`, `sync_context`/AGENT_CONTEXT,
   `agent_config`, wizard) through `module_host.iter_capability_sources()` so a
   module's capabilities also surface in suggestions/context — not just the gate
   audit. Deferred until a module ships non-gate capabilities that need listing.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `0932fe6` (has PROTO-047 + 048). **PRs #12 and #13 open.**
- **566 tests green; `pg doctor` 0 err / 0 warn / 25 ok; `black --check` clean;
  flake8 E9/F-gate clean.** (562→566 from PROTO-052 tests; doctor 24→25 from the
  content `publish` gate.)
- Multi-module platform now spans: manifest (`module.yaml`) → discovery →
  `pg module list/show` → `pg --module <name> init-surface` (state surface) →
  per-module bundled `capabilities/` with gate auditing. A department is now a
  directory of data the core hosts end-to-end.

## Shipped this cycle

- **PROTO-047** — Content module (2nd contract impl). **MERGED** (PR #10).
- **PROTO-048** — multi-module hosting (`pg --module … init-surface`), closes
  seam **S2**. **MERGED** (PR #11).
- **PROTO-049** — advertise `pg module` commands in AGENT_CONTEXT cheatsheet.
  **PR #12 open.**
- **PROTO-052** — manifest-driven capability sources, closes seam **S1**
  (supervision half); content ships its own gated `publish` workflow.
  **PR #13 open.**

## Pending / In Progress

- **PRs #12 + #13 awaiting merge** (mind the PROJECT_STATUS.md conflict above).
- **PROTO-050** — coverage ≥70% (tooling gap — see step 2).
- **S1 listing half** — see step 3 (not ticketed yet).
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
  module's own `capabilities/` (PROTO-052).
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs only on PRs targeting `main`/`development`.
- **Regen noise:** `AGENT_CONTEXT.md` / host configs carry a `Generated:`
  timestamp `pg` rewrites on any run — `git restore` them if they show up as a
  diff with no content change. (Exception: PROTO-049 intentionally changed their
  *content* — the module commands.)
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions

- **S1 listing half**: when host-side listings become multi-source, does the
  host's single `.proto-gear/` stay the shared capabilities_root, or does each
  module namespace its own subtree? Both manifests declare `.proto-gear`. Decide
  before wiring the listing surfaces (it governs whether two modules' capability
  IDs can collide in `pg suggest` / AGENT_CONTEXT).

---
*Agent-maintained. Replace entirely at session end.*
