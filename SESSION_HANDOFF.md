# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**The department seam is complete end-to-end, and orchestration + change-tracing
ship.** A discipline is discovered, listed, installed (`.proto-gear/<module>/`),
indexed, gate-audited, agent-visible, orchestrated (`pg pipeline`), AND traceable
(`pg trace`) — all from pure declaration, with **zero core edits** per discipline.
Three disciplines ship: `engineering`, `qa`, `devops`. CI is genuinely green
(pytest actually runs in CI now).

1. **Everything through PROTO-061 is merged** (PRs #16–#24). No PR in flight.
2. **Pick the next thrust** (unticketed; file with `pg ticket create`):
   - **A 4th discipline (security? docs?)** — cheap contract exercise; `modules/qa`
     and `modules/devops` are the reference patterns. It would join `pg pipeline`
     automatically (if it ships a gated workflow) and `pg trace` (if its state
     surface carries a `Ref` column). The cleanest next validation.
   - **Agent subsystem, deeper** — PROTO-058 made `AgentManager` *read* module
     caps; installing/composing agents per discipline is unbuilt.
   - **Phase D-3 — richer trace/pipeline** — e.g. `pg trace` could fold in the
     pipeline gate chain to show which required approvals a change still lacks
     (not just the rows it has); or trace a release across all its tickets.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `1432f8b` (through PROTO-061, PR #24). **No PR in flight.**
- **CI is green and deterministic.** `Tests` workflow: a dedicated `lint` job
  (single ubuntu/py3.12, **`black==26.5.1` pinned**) + a pytest-only matrix.
  Before PROTO-055 the matrix `black --check` ran *before* pytest and always
  failed, so **pytest never actually executed in CI**. Reproduce CI parity
  locally with the **bare console script** `pytest tests/` (not `python -m
  pytest`, which puts cwd on `sys.path`).
- **804 tests pass; `pg doctor` 0/0/27 ok; `black --check` clean.**
- **The department seam, end to end** (all namespaced `<module>/<cap_id>`):
  - Discovery/manifest: `discover_modules()`, `module_host.resolve_module()`.
  - Listings (S1): `module_host.load_bundled_capabilities()`; `pg suggest`,
    `pg capabilities list/search/show/tree` (bare/`<type>/<name>`/namespaced
    resolution); agents via `AgentManager._load_capabilities()`.
  - On-disk: `module_host.install_module_capabilities()` → `.proto-gear/<name>/`
    (wired into `pg init`); `sync_capability_indexes` partitions by module →
    shared root index + per-module INDEX (scaffolded on demand); `pg doctor`
    covers subtree index drift.
  - Gates/orchestration: `doctor.check_supervision_gates` audits every
    discipline's gates; **`module_core/pipeline.py` + `pg pipeline [--json]`**
    compose them into the path to production, flagging convergence points.
  - Change trace (D-2): **`module_core/trace.py` + `pg trace <ticket> [--json]`**
    follow a change across discipline state surfaces via the ticket-id key (a
    `Ref` column each surface may carry), showing approval state per hop.
- **Scope (PROTO-053):** proto-gear = software-engineering OS; departments are
  engineering disciplines (dev, qa, devops, security, docs, release/PM). No
  content/marketing — that's honk (`../_Plugins/honk/`), a separate product.

## Shipped this cycle (all merged)

- **PROTO-054** — QA/Test module (Phase C falsifier), zero core edits. PR #16.
- **PROTO-055** — CI green: pinned single lint job; fixed a latent test-import
  bug (4 modules imported `core.*`, resolvable only under `python -m pytest`);
  PROTO-053 docstring scrubs. PR #17.
- **PROTO-056** — S1 listings multi-source, per-module namespaced. PR #18.
- **PROTO-057** — S1 on-disk per-module subtrees + per-module INDEX. PR #19.
- **PROTO-058** — S1 follow-up: agent subsystem reads module caps. PR #20.
- **PROTO-059** — DevOps/SRE module, 3rd discipline, zero core edits. PR #21.
- **PROTO-060** — Phase D: cross-discipline supervision pipeline (`pg pipeline`).
  PR #22.
- **PROTO-061** — Phase D-2: cross-discipline change trace (`pg trace`),
  ticket-id correlation via a `Ref` column. PR #24.

## Pending / In Progress

- **Nothing in flight.** Next thrust: a 4th discipline, or Phase D-3 — step 2.

## Conventions In Force

- **Scope discipline:** engineering-only. Content/marketing/sales/finance is out
  of scope by design (PROJECT_SPECIFICATIONS.md §8). Flag, don't build.
- **New discipline = zero core edits.** Drop `modules/<name>/` (manifest +
  optional `capabilities/` + state-surface template). It is auto-discovered,
  listed, installed, indexed, gate-audited, agent-visible, joins `pg pipeline`
  (if it ships a gated workflow), and joins `pg trace` (if its state surface
  carries a `Ref` column) — with no `module_core/`/`cli/` change. If it needs
  one, the abstraction is wrong — stop. `modules/qa/` and `modules/devops/` are
  the reference patterns.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower never
  imports higher. Module-generic behavior lives in `module_core` (e.g.
  `module_host.install_module_capabilities`, `pipeline.py`), never in
  `modules/engineering/`.
- **Namespacing:** shared/engineering caps keep bare ids; a module's own caps are
  `<module>/<cap_id>` everywhere (gate audit, listings, on-disk, agents, pipeline).
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:` with
  `before`/`approver`/`required`); a workflow with a risky output (release/
  deploy/publish) must declare one. They drive both the doctor audit and
  `pg pipeline`.
- **Testing:** business logic via argparse.Namespace + capsys + tmp dirs;
  interactive questionary wizards out of scope. Real bundled modules get an
  acceptance test (`test_qa_module.py` / `test_devops_module.py` are the
  templates). **Verify CI parity with bare `pytest tests/`.**
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs on PRs to `main`/`development`. **Formatting is a
  hard CI gate (pinned black) AND a pre-commit hook** (`git config core.hooksPath
  dev/hooks`). Fix: `black core/ tests/`. Mark a ticket COMPLETED **in its own
  branch** before merge, so the status rides the PR (avoids a dangling post-merge
  edit on `development`).
- **Regen noise:** `AGENT_CONTEXT.md` / host configs carry a `Generated:`
  timestamp `pg` rewrites on any run — `git restore` them if the diff is
  timestamp-only; commit them when a real content change (e.g. a new CLI command
  in `sync_context.CLI_COMMANDS`) is present.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

---
*Agent-maintained. Replace entirely at session end.*
