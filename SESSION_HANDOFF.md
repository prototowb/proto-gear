# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**PROTO-047 (Content module) is merged. PROTO-048 (multi-module hosting) is done
and in review as PR #11 → `development`. Next up: PROTO-049, then PROTO-050 —
plus a newly-filed seam S1 ticket (see below).**

1. **First: merge PR #11** (`feature/proto-048-multi-module-hosting` →
   `development`) if not already merged, then `git checkout development && git
   pull`.
2. **PROTO-049 — surface `pg module` + `pg --module … init-surface` in the
   AGENT_CONTEXT cheatsheet** (`module_core/sync_context.py::CLI_COMMANDS`), then
   `pg sync-context` to regenerate AGENT_CONTEXT.md + host mirrors. The new
   commands exist but aren't yet advertised in the agent-facing cheatsheet.
3. **PROTO-050 — raise core business-logic coverage to ≥70%** (spec Phase A
   criterion). `module_host.py` is fully covered; check `doctor.py`,
   `capability_metadata.py`, `templates.py` for gaps.
4. **NEW — file the S1 ticket** (see below): manifest-driven capability/gate
   loading. It's the last open seam from the content-module falsification and
   the real prerequisite for content ever shipping its own capabilities.

Branch off `development`, PR back to `development`. Run `pg status` /
`pg ticket list` first.

## Current State

- `development` = `7fafaff` (has PROTO-047). **PR #11 open** for PROTO-048.
- **561 tests green; `pg doctor` 0 err / 0 warn / 24 ok; `black --check` clean;
  flake8 E9/F-gate clean.** (540→561 from PROTO-048's 21 `test_module_host.py`.)
- New generic core primitive: **`module_core/module_host.py`**
  (`resolve_module` + `render_state_surface`) + global `--module <name>` flag +
  `pg --module <name> init-surface`. `pg --module content init-surface` writes
  `CONTENT_QUEUE.md`; engineering keeps its richer `pg init`.

## Shipped this cycle

- **PROTO-047** — Content module (2nd contract implementation, ADR-001 Phase C
  entry). **MERGED** (PR #10). Manifest + `CONTENT_QUEUE.template.md` + design
  doc + 11 acceptance tests. Proved the zero-core-edit contract and surfaced
  seams S1/S2.
- **PROTO-048** — multi-module hosting, closing seam **S2**. **In review as PR
  #11.** Generic `module_host` render seam + `pg --module <name> init-surface`.

## Pending / In Progress

- **PR #11 awaiting merge** to `development`.
- **Backlog:** PROTO-049 (cheatsheet sync) → PROTO-050 (coverage ≥70%) → **S1
  ticket** (below).
- **Seam S1 — capabilities are single-rooted (the last content-module seam).**
  `module_core/capability_metadata.load_all_capabilities`,
  `discovery`, `sync_context`, and `doctor.check_supervision_gates` all read one
  shared `package_root()/capabilities` dir and ignore each manifest's
  `capabilities_root` (~15 call sites across 6 files). A module can't yet ship
  its own capabilities under `modules/<name>/capabilities/`. Deliberately NOT
  done in PROTO-048 (no consumer until content bundles capabilities; too big to
  fold in). File it, then it unblocks content's draft/review/schedule/publish
  capabilities and the Phase C success criterion (agent runs draft → gate →
  publish). See `docs/dev/content-module-design.md` §6.
- **Formatting enforced via git hook, not CI.** `dev/hooks/pre-commit` blocks
  commits failing `black --check` / flake8. **Enable once per clone:**
  `git config core.hooksPath dev/hooks` (already set here). Fix: `black core/
  tests/`.

## Conventions In Force

- **Layering:** `cli/` (top) → `module_core/` (generic) → `modules/<dept>/`
  (department). Lower never imports higher. Every non-trivial change asks:
  "generic core, or department-specific?" New department = new
  `modules/<name>/module.yaml` — **zero core edits** (enforced by the acceptance
  tests in `test_module_manifest.py` + `test_content_module.py`). Genuinely
  generic new capability = a `module_core` primitive (e.g. `module_host.py`),
  never engineering-routed.
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:`);
  `pg doctor` enforces structure + coverage.
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs only on PRs targeting `main`/`development`.
- **Formatting** is gated by the pre-commit hook (see above).
- **Regen noise:** `AGENT_CONTEXT.md` / host configs (`CLAUDE.md`,
  `.cursorrules`, `.windsurfrules`, copilot) carry a `Generated:` timestamp that
  `pg` rewrites on any run — `git restore` these if they show up as a diff with
  no content change.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions (for the S1 ticket)

- When capability loading becomes manifest-driven, does the host's single
  `.proto-gear/` stay the shared `capabilities_root` for all modules, or does
  each module namespace its own subtree (e.g. `.proto-gear/content/`)? Both
  manifests currently declare `.proto-gear`. Decide before wiring loaders to the
  manifest — it changes whether two modules' capabilities can collide.

---
*Agent-maintained. Replace entirely at session end.*
