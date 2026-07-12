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

1. **Everything through PROTO-073 is merged** (PROTO-068/069 = ADR-002
   proposed/accepted, PROTO-070 = UI-first principle §5.7, PROTO-071 = gate
   schema `actor` + `authority` PR #41, PROTO-072 = evidence-predicate
   vocabulary PR #42, PROTO-073 = dogfood falsifier PR #43 — **the falsifier
   held: metadata-only migration, zero core edits**).
2. **Pick the next thrust** (unticketed; file with `pg ticket create`) — the
   ADR-002 action items are the arc (docs/dev/adr/ADR-002-…md §Action Items):
   - **Item 3 — authority sufficiency in `pg trace`/`pg release`**: the
     checklist entries already carry `authority`; report whether each cleared
     gate's signer had *sufficient* authority (needs a signer-identity
     convention on the state surface). No new commands.
   - **Item 4 — DONE (PROTO-073)**: `pr-review-approval` runs at
     `human-on-recommendation` with actor `code-review-agent` and mapping-form
     evidence. Zero core edits — the primitives are proven.
   - **Item 5 — PROJECT_SPECIFICATIONS §4**: describe graded authority as the
     supervision model's capability-growth axis.
   - Still open from before: `pg agent list --available` / `pg agent install`
     (surfacing pre-install discipline agents), a 5th discipline (docs /
     release-PM), `pg release` polish. Remember PROTO-070: every new feature
     must be reachable via the interactive UI first — commands are shortcuts.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = through PROTO-073 (PR #43). **No PR in flight** (bar this
  one if you're reading it pre-merge).
- **882 tests pass; `black --check` clean.** CI parity: bare `pytest tests/`.
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
- (Earlier: PROTO-054–067 — module seam S1, pipeline/trace/release D-series,
  per-gate evidence + scope, agent seam. See git history.)

## Pending / In Progress

- **Nothing in flight** beyond PR #43 (PROTO-073). Next: ADR-002 item 3
  (authority sufficiency in trace/release) and item 5 (spec §4 graded
  authority) — see "Start here".

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
