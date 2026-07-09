# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**PROTO-047 (Content module) is done and in review as PR #10 → `development`.
The next ticket is PROTO-048, and PROTO-047 handed it a precise spec.**

1. **First: merge PR #10** (`feature/proto-047-content-module` → `development`)
   if not already merged, then `git checkout development && git pull` so local
   `development` tracks the remote (this session already fast-forwarded local
   `development` from stale `1d7b6fb` to `00b1396`).
2. **PROTO-048 — multi-module hosting (`pg --module <name> <cmd>`).** PROTO-047's
   design doc (`docs/dev/content-module-design.md` §6) identified the two exact
   seams to close — do these, they are no longer open questions:
   - **S1 — capabilities are single-rooted.**
     `module_core/doctor.check_supervision_gates` and
     `module_core/capability_metadata.load_all_capabilities` read one shared
     `package_root()/capabilities` dir and ignore each manifest's
     `capabilities_root`. Make capability + gate loading manifest-driven so a
     module can ship its own capabilities under `modules/<name>/capabilities/`.
   - **S2 — no per-module init/template-render seam.** `pg init` + the template
     engine live under `modules/engineering/`; there's no neutral path to render
     *a* module's state-surface template into a host, so `pg --module content
     init` can't lay down `CONTENT_QUEUE.md`. Add `pg --module <name> <cmd>`
     dispatch (default module = engineering, no new flags for the single-module
     case) + a generic state-surface render seam.
3. Then **PROTO-049** (surface `pg module` in `sync_context.CLI_COMMANDS` →
   AGENT_CONTEXT), **PROTO-050** (raise core coverage to ≥70%).

Branch off `development`, PR back to `development` (see Conventions). Run
`pg status` / `pg ticket list` first.

## Current State

- `development` = `00b1396` (origin and local now in sync). Holds the full
  monolith→module-platform refactor through PROTO-051.
- **PR #10 open**: `feature/proto-047-content-module` → `development`
  (Content module). Local branch committed at `07f4b38`.
- **540 tests green; `pg doctor` 0 err / 0 warn / 24 ok; `black --check` clean;
  flake8 E9/F-gate clean.** (Test count 529→540 and doctor 23→24 both from the
  new content module + its 11 acceptance tests.)
- Package layout unchanged except a new **`modules/content/`** department
  (manifest + `CONTENT_QUEUE.template.md` + `__init__.py`) — discovered by the
  generic `discover_modules()` with zero `module_core/` edits.

## Shipped this cycle

- **PROTO-047** — Content module (2nd contract implementation, ADR-001 Phase C
  entry). Manifest + state-surface template + design doc (`docs/dev/
  content-module-design.md`) + 11 acceptance tests. **In review as PR #10.**
  Proved the zero-core-edit contract against a real bundled module and surfaced
  the two seams (S1/S2 above) that scope PROTO-048.

## Pending / In Progress

- **PR #10 awaiting merge** to `development`.
- **Backlog:** PROTO-048 (multi-module hosting — close S1/S2) → 049 (cheatsheet
  sync) → 050 (coverage ≥70%).
- **Formatting enforced via git hook, not CI.** Private repo, no server-side
  required checks. A version-controlled hook (`dev/hooks/pre-commit`) blocks
  commits failing `black --check` / flake8. **Enable once per clone:**
  `git config core.hooksPath dev/hooks` (already set in this checkout). Fix with
  `black core/ tests/`.

## Conventions In Force

- **Layering:** `cli/` (top) → `module_core/` (generic) → `modules/<dept>/`
  (department). Lower never imports higher. Every non-trivial change asks:
  "generic core, or department-specific?" New department = new
  `modules/<name>/module.yaml` — **zero core edits** (enforced by the acceptance
  tests in `test_module_manifest.py` + `test_content_module.py`).
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:`);
  `pg doctor` enforces structure + coverage. Release/deploy/publish workflows
  must declare a gate.
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI only runs on PRs targeting `main`/`development`.
- **Formatting** is gated by the pre-commit hook (see above).
- **Regen noise:** `AGENT_CONTEXT.md` / host configs (`CLAUDE.md`,
  `.cursorrules`, `.windsurfrules`, copilot) carry only a `Generated:` timestamp
  that `pg` rewrites on any run — `git restore` these if they show up as a diff
  with no content change.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions (for PROTO-048)

- When capability loading becomes manifest-driven (S1), does the shared
  `.proto-gear/` at the host root stay the single capabilities_root for all
  modules, or does each module get its own subtree? The content manifest
  currently declares `.proto-gear` — revisit once multi-module hosting lands.

---
*Agent-maintained. Replace entirely at session end.*
