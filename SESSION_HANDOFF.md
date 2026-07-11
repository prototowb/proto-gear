# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**The department seam is complete end-to-end, and orchestration + change-tracing
+ release-readiness ship — proven across FOUR disciplines.** A discipline is
discovered, listed, installed (`.proto-gear/<module>/`), indexed, gate-audited,
agent-visible, orchestrated (`pg pipeline`), traceable (`pg trace` + gate
checklist), AND aggregated at the release level (`pg release`) — all from pure
declaration, with **zero core edits** per discipline. Four ship: `engineering`,
`qa`, `devops`, `security`. CI is genuinely green (pytest actually runs in CI).

1. **Everything through PROTO-066 is merged** (PRs #16–#34). No PR in flight
   (bar this handoff refresh). **The supervision-readiness loop is now closed
   end-to-end**: pipeline → per-change trace + gate checklist (evidenceable via
   per-gate `evidence:` columns) → release roll-up with **both** change-scoped
   (per-ticket) and release-scoped (once-per-release) gate evidence.
2. **Pick the next thrust** (unticketed; file with `pg ticket create`):
   - **Agent subsystem, deeper** — likely the highest-value frontier now. PROTO-058
     made `AgentManager` *read* module caps; installing/composing agents per
     discipline (a qa agent, a devops agent, …) is unbuilt. This is where the
     department model pays off for *running* work, not just auditing it.
   - **Another discipline (docs? release/PM?)** — contract well proven (4
     disciplines) and now exercises change- *and* release-scoped gates; a 5th is
     cheap. A `release/PM` discipline could *own* the Releases surface that
     PROTO-066 put in engineering's `PROJECT_STATUS` — a natural home for it.
   - **`pg release` polish** — aggregate a release trace across *disciplines'*
     release surfaces (today the Releases table lives in engineering); or a
     `--format` for release-notes generation from the cleared checklist.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `5e37596` (through PROTO-066, PR #34). **No PR in flight.**
- **CI is green and deterministic.** `Tests` workflow: a dedicated `lint` job
  (single ubuntu/py3.12, **`black==26.5.1` pinned**) + a pytest-only matrix.
  Before PROTO-055 the matrix `black --check` ran *before* pytest and always
  failed, so **pytest never actually executed in CI**. Reproduce CI parity
  locally with the **bare console script** `pytest tests/` (not `python -m
  pytest`, which puts cwd on `sys.path`).
- **839 tests pass; `pg doctor` 0/0/29 ok; `black --check` clean.**
- **Four disciplines ship:** `engineering`, `qa`, `devops`, `security` — all on
  the unmodified core. `security-signoff` and `qa-signoff` both guard `release`
  (a convergence point in `pg pipeline`).
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
  - Change trace (D-2/D-3): **`module_core/trace.py` + `pg trace <ticket> [--json]`**
    follow a change across discipline state surfaces via the ticket-id key (a
    `Ref` column each surface may carry), showing approval state per hop AND a
    required-approval checklist folded in from the pipeline gate chain
    (`gate_checklist`: cleared / pending / outstanding / untracked).
  - Release trace (D-4): **`module_core/release.py` + `pg release <label> [--json]`**
    aggregate the release's gate checklists into one readiness verdict.
    Membership is read from a release column (`PR/Commit`/`Release`/`Version`) —
    by column name, not discipline name. `ready` = ≥1 ticket AND no ticket has a
    pending/outstanding change-scoped gate AND no release-scoped gate blocks;
    unverifiable gates are reported, never counted.
  - Per-gate evidence (PROTO-065): a supervision gate may declare an optional
    **`evidence:`** column naming the state-surface cell that records *its own*
    sign-off; `gate_checklist` verifies against that column when present, else
    the discipline-level fallback (unchanged for single-gate disciplines). This
    made engineering's per-change `pr-review-approval` evidenceable (a `Reviewed
    by` column on the completed-tickets table) **without** false-clearing its
    release-level gates — a discipline can now carry >1 heterogeneous gate.
  - Gate scope (PROTO-066): a gate declares **`scope: change`** (default,
    per-ticket) or **`scope: release`** (once per release). `pg release`
    evaluates change-scoped gates per ticket and release-scoped gates
    (`release-approval`, `announcement-approval`) once — against the release
    label itself, via a `Releases` table keyed by the label in its `ID` column
    (reusing `gate_checklist(<label>)`, no new matching logic). Closes the
    readiness loop: a release with no recorded `release-approval` is *not ready*.
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
- **PROTO-062** — Phase D-3: `pg trace` gate checklist — required approvals
  cleared vs outstanding, folded in from the pipeline. PR #26.
- **PROTO-063** — Security/AppSec module, 4th discipline, zero core edits;
  auto-created the `release` convergence with qa. PR #28.
- **PROTO-064** — Phase D-4: release trace (`pg release`) — aggregate per-ticket
  gate checklists into a release readiness verdict; unverifiable gates reported
  honestly, not silently cleared. Pure `module_core` + CLI, zero `modules/`
  edits. PR #30.
- **PROTO-065** — per-gate `evidence:` column; engineering's per-change
  `pr-review-approval` now evidenceable via a `Reviewed by` column, without
  false-clearing release-level gates. Closes the `untracked` wart for the one
  gate that's genuinely per-ticket. PR #32.
- **PROTO-066** — gate `scope: change|release`; `pg release` now verifies
  release-scoped gates (`release-approval`, `announcement-approval`) once,
  against a `Releases` table keyed by the release label. Fully closes the
  readiness loop. PR #34.

## Pending / In Progress

- **Nothing in flight** (bar this handoff refresh). The D-series supervision arc
  is complete. Next thrust: the agent subsystem (install/compose agents per
  discipline), a 5th discipline (docs / release-PM), or `pg release` polish.

## Conventions In Force

- **Scope discipline:** engineering-only. Content/marketing/sales/finance is out
  of scope by design (PROJECT_SPECIFICATIONS.md §8). Flag, don't build.
- **New discipline = zero core edits.** Drop `modules/<name>/` (manifest +
  optional `capabilities/` + state-surface template). It is auto-discovered,
  listed, installed, indexed, gate-audited, agent-visible, joins `pg pipeline`
  (if it ships a gated workflow), and joins `pg trace` (if its state surface
  carries a `Ref` column) — with no `module_core/`/`cli/` change. If it needs
  one, the abstraction is wrong — stop. `modules/qa/`, `modules/devops/`, and
  `modules/security/` are the reference patterns (security carries `Ref` +
  approver columns, so it supports full `pg trace` + gate checklist).
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
