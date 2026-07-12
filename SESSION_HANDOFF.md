# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**ADR-002 (supervision primitives) is Accepted and its first slice is code.**
The gate contract now carries the three ADR-002 primitives: **actor** (who is
accountable for the guarded work), **evidence** (what proves it — v1 predicate
is the implicit "cell non-empty and not 'pending'" check), and **authority**
(minimum authority to clear, three-rung ladder: `human` →
`human-on-recommendation` → `auto`; the `agent` clearing rung is **deferred**
per the PROTO-069 amendment and the doctor rejects it). Defaults reproduce §4
exactly — the whole bundled corpus is unchanged, all-human.

**The ADR-002 arc is COMPLETE** — all five action items shipped (PROTO-071
schema, PROTO-072 evidence predicates, PROTO-073 dogfood falsifier [held,
zero core edits], PROTO-074 authority sufficiency, PROTO-075 spec §4.1).
The supervision contract now separates actor / evidence / authority, with a
three-rung graded-authority ladder, doctor validation, trace/release
sufficiency auditing, and one live `human-on-recommendation` gate.

1. **Everything through PROTO-077 is merged** (PRs #41–#47). **FIVE
   disciplines ship**: engineering, qa, devops, security, **release**
   (Release Management / PM, PROTO-077) — the 5th landed with zero core
   edits, again. `release` owns RELEASE_QUEUE.md (rows keyed by the release
   *label*), ships the first `modules/` **release-scoped** gate
   (`go-no-go`, before `release` — a three-way convergence with qa +
   security), and ships `release-coordinator-agent` via the PROTO-067 seam.
   `pg release <label>` now requires a recorded human go decision.
2. **Post-ADR-002 backlog — now largely worked through** (PRs #49–#51):
   - **PROTO-078** — `pg init --no-interactive` substitution gaps: shared
     defaulted-replacement dict on every init path, PROJECT_STATUS via the
     headered template, `--force` refresh, fence-aware + comment-tolerant
     `pg status` parsing. **Prod-verified in `../arsenal-gear/`** (86→0 leaks).
   - **PROTO-079** — **`pg release --notes`**: release notes generated from the
     cleared gate checklist (tickets grouped Features/Fixes/Changes + approvers
     per discipline; draft caveat when not ready). Reuses `trace_release`.
   - **PROTO-080** — **interactive agent browser (§5.7 first slice)**: bare
     `pg agent` → navigate/select installed + available agents (view + install
     on pick), `questionary`-driven, falls back to `pg agent list` without a
     TTY. First non-wizard interactive surface.
   - **Remaining §5.7 slices** (not started): interactive **capability browser**
     (`pg capabilities` no-arg) and a top-level **home menu** (`pg` no-arg).
     Reuse the `cmd_agent_browse` pattern — pure `_collect_*` data + a thin
     `questionary` loop with a non-TTY fallback.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = through PROTO-080 (PRs #49–#51). **951 tests pass; `pg
  doctor` green.** The init/release/agent-browser work rides those PRs; run
  `pg status` / `pg ticket list` for the live picture.
- **Five disciplines**: `modules/release/` = module.yaml +
  RELEASE_QUEUE.template.md (stages planned→…→go→shipped; ID = release
  label; Ref = member tickets; no Release/Version column, so the label row
  never reads as ticket membership) + `workflows/go-no-go` (gate: human,
  required, `scope: release`, evidence "Signed off by") +
  `agents/release-coordinator-agent.yaml`. Fixtures in test_release.py
  gained `_write_release_queue`; a ready release now needs the go row.
- **892 tests pass; `black --check` clean.** CI parity: bare `pytest tests/`.
- **Authority sufficiency (PROTO-074, ADR-002 item 3)**: checklist entries
  carry `signed_by` + `authority_ok`. Signer convention: an agent signs with
  its agent id (config filename stem, optionally namespaced) or `agent:`
  prefix; anything else is presumed human. Cleared human-rung gate with only
  agent signers → flagged `!!` in trace/release + counted in the release
  report's `authority_insufficient_total`. Reported, never blocking. `auto`
  needs no signer; a signature-less comparison clear is `None` (unjudgeable).
- **The corpus is no longer all-default**: `pr-review-approval`
  (workflows/code-review-process) carries `actor: code-review-agent`,
  `authority: human-on-recommendation`, evidence as a mapping. Tests encode
  this: exactly ONE gate deviates from §4 defaults (test_pipeline /
  test_trace assert it by name). Every other gate stays pure `human`.
- **Gate schema (capability_metadata.Gate)**: `id`, `description`, `before`,
  `approver`, `required`, `evidence` (+ `evidence_predicate`,
  `evidence_value`), `scope: change|release`, **`actor`** (discipline agent
  `<module>/<agent-slug>`, human role, or "" = unassigned), **`authority`**
  (`GATE_AUTHORITY_LADDER = human | human-on-recommendation | auto`;
  `GATE_DEFERRED_AUTHORITIES = agent`). All defaults §4-preserving.
- **Evidence predicates (PROTO-072, ADR-002 §2)**:
  `GATE_EVIDENCE_PREDICATES = non-empty | equals | at-least`. YAML `evidence:`
  is a plain column string (predicate non-empty) or a
  `{column, predicate, value}` mapping. `trace._predicate_holds` evaluates
  comparisons (pure string/number checks over a markdown cell — provably
  non-executing; unknown predicates never clear). A filled cell that fails
  the claim is `pending`, never `cleared`. Doctor: predicate must be in the
  vocabulary; equals/at-least need column + value; at-least value numeric.
- **Doctor gate audit** (`check_supervision_gates`) now enforces:
  `gate-authority-deferred` (error — `agent` rung, ADR-002 amendment),
  `gate-authority-invalid` (error), `gate-auto-needs-evidence` (error — an
  `auto` gate clears by evidence alone), `gate-actor-unknown` (warning — a
  namespaced actor must match a `modules/<name>/agents/*.yaml` stem).
- **Plumbing**: `pipeline.collect_supervision_gates` records and
  `trace.gate_checklist` entries carry `actor`/`authority`; `pg pipeline` and
  `pg capabilities show` render them only when non-default (all-human corpus
  renders unchanged). `pg trace`/`pg release` JSON gains the fields for free.
- **Four disciplines ship:** `engineering`, `qa`, `devops`, `security` — all on
  the unmodified core; agent seam (PROTO-067) proven with qa + devops agents.
- **Scope (PROTO-053):** proto-gear = software-engineering OS; no
  content/marketing — that's honk (`../_Plugins/honk/`), a separate product.
- **UI-first (PROTO-070, §5.7):** every feature reachable through the
  interactive CLI UI first; a dedicated command is a shortcut, never the only
  way in.

## Shipped this cycle (recent)

- **PROTO-068/069** — ADR-002 proposed, then **Accepted with amendment**: the
  `agent` clearing rung is deferred; `human-on-recommendation` is the ceiling
  for judgment gates; `auto` reserved for deterministic non-judgment facts.
  PRs #38, #39.
- **PROTO-070** — UI-first product principle (§5.7). PR #40.
- **PROTO-071** — ADR-002 action item 1: gate schema `actor` + graded
  `authority`, doctor validation, plumbed through pipeline/trace/CLI. Zero
  behavior change for the existing all-default corpus. PR #41.
- **PROTO-072** — ADR-002 action item 2: declarative evidence-predicate
  vocabulary (non-empty/equals/at-least), doctor-validated, evaluated by
  `gate_checklist` (so `pg trace` AND `pg release` get it). PR #42.
- **PROTO-073** — ADR-002 action item 4, the dogfood falsifier:
  `pr-review-approval` migrated to `human-on-recommendation` + actor +
  mapping-form evidence, in the workflow's metadata.yaml alone. PR #43.
- **PROTO-074** — ADR-002 action item 3: authority-sufficiency reporting in
  `pg trace`/`pg release` (signers + `authority_ok`), no new commands. PR #44.
- **PROTO-075** — ADR-002 action item 5: PROJECT_SPECIFICATIONS §4.1 describes
  graded authority as the capability-growth axis. **Closes the ADR-002 action
  list.** PR #45.
- **PROTO-076** — agent surfacing: `module_host.list_bundled_agents` +
  `install_bundled_agent`; `pg agent list [--available]` + `pg agent
  install <name>`. PR #46.
- **PROTO-077** — Release Management / PM, the 5th discipline: RELEASE_QUEUE
  surface keyed by release label, release-scoped `go-no-go` gate (three-way
  `release` convergence), discipline agent. Zero core edits. PR #47.
- (Earlier: PROTO-054–067 — module seam S1, pipeline/trace/release D-series,
  per-gate evidence + scope, agent seam. See git history.)

## Pending / In Progress

- **Nothing in flight** beyond PR #47 (PROTO-077). **Paused by the user**
  before the remaining backlog (release polish / interactive UI) — see
  "Start here".

## Conventions In Force

- **Scope discipline:** engineering-only. Flag, don't build, anything else.
- **New discipline = zero core edits.** Drop `modules/<name>/` (manifest +
  capabilities + state surface). If it needs a `module_core/`/`cli/` change,
  the abstraction is wrong — stop. `modules/qa|devops|security/` are reference.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower
  never imports higher.
- **Namespacing:** shared/engineering caps bare; module caps `<module>/<cap_id>`
  everywhere. Discipline agents install flat as `<agent-slug>.yaml`; a gate's
  namespaced `actor` is `<module>/<agent-slug>`.
- **Bundled resources:** resolve via `paths.package_root()`.
- **Supervision gates are data** (workflow `metadata.yaml` `gates:`); a workflow
  with a risky output (release/deploy/publish) must declare one. ADR-002
  primitives: `actor` / `evidence` / `authority` — ceiling for judgment gates is
  `human-on-recommendation`; never introduce an `agent` clearing rung.
- **Testing:** argparse.Namespace + capsys + tmp dirs; wizards out of scope.
  **Verify CI parity with bare `pytest tests/`** (not `python -m pytest`).
- **Git:** never commit to `main`/`development`; branch from `development`, PR
  back; **black is a hard CI gate** (`black core/ tests/`) + pre-commit hook.
  Mark a ticket COMPLETED **in its own branch** so the status rides the PR.
- **Regen noise:** `AGENT_CONTEXT.md`/host configs carry a `Generated:`
  timestamp — `git restore` when the diff is timestamp-only.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

---
*Agent-maintained. Replace entirely at session end.*
