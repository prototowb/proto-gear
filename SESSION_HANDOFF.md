# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**The steering-framework action plan is fully shipped** (all 5 phases, PRs
#56–#59, on `development`). This reworked proto-gear's markdown steering surface
against the Claude Fable 5 prompting guidance — the thesis being *shrink
procedural prose, grow durable state and machine-checked boundaries*. Source of
truth for the arc: `proto-gear-steering-action-plan.md` (each phase checked off
in its Implementation Log).

What changed, phase by phase:

1. **PROTO-086 (#56) — slim generated context block.** Dropped the keyword
   `Trigger → Capability` table and the per-capability `_triggers:_` suffix from
   `AGENT_CONTEXT`; agents route off descriptions now. Rewrote the AGENTS.md
   "MANDATORY READING" wall as a conditional per-file table, reserving `NEVER`
   for the one true invariant. Added a token budget: `sync_context.estimate_tokens`
   + `AGENT_CONTEXT_TOKEN_BUDGET` (now **1800**), enforced by
   `doctor.check_agent_context_budget` (warns, never errors; offline estimate).
2. **PROTO-087 (#57) — capability output profiles.** `pg init --profile
   frontier|verbose`, **default frontier**. One canonical corpus (the verbose
   `*.template.md` bodies) rendered at two verbosities: `frontier` ships a slim
   stub generated from each capability's `metadata.yaml` (the 379-line TDD skill
   → 7-line stub); `verbose` ships the full playbooks. Chosen profile recorded in
   `.proto-gear/PROFILE`. Machinery: `module_core/capability_profile.py`; honored
   by both `copy_capability_templates` (defaults **verbose** at the library layer)
   and `module_host.install_module_capabilities`.
3. **PROTO-088 (#58) — lessons layer + grounding lines.** `.proto-gear/lessons/`
   agent-writable accumulated knowledge (bundled README + INDEX scaffold; one
   lesson per file: `# Title` + `> summary` + body). `module_core/lessons.py`
   parses/validates/indexes; `sync_lessons_index` wired into `pg sync-context` +
   `pg doctor --fix`; `doctor.check_lessons` flags malformed lessons / stale
   index. Plus a **Working Agreement** section in the generated context (audit
   progress claims; report-and-stop when the user describes a problem; pause only
   for destructive/scope/user-only decisions).
4. **PROTO-089 (#59) — enforce "never commit to `main`".** `pg guard branch`
   (`module_core/guard.py`) exits non-zero on a protected branch — a primitive
   for hooks/CI/agents; never rewrites history. `pg hooks install` (bundled
   `hooks/pre-commit`, `module_core/hooks.py`) drops a **no-clobber** branch-guard
   pre-commit hook. `.gitattributes` pins the hook to LF. BRANCHING documents
   `pg guard` / hook / CI as the *how*, keeping the prose as the *why*.

**No steering work pending.** Natural follow-ons if picking this thread back up:
a `standard` middle profile if a consumer needs it; a wizard prompt for the init
profile; a `pg lessons` interactive browser (mirrors the §5.7 pattern); a doctor
audit that the branch-guard hook is installed.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = through **PROTO-089** (PRs #56–#59). **1073 tests pass; `pg
  doctor` green (32 checks); `black --check` clean.** CI parity: bare
  `pytest tests/`.
- **Generated agent-context block is description-routed** (no keyword table),
  carries a Working Agreement section, and is budgeted (~1600–1650 tokens for
  this repo; warns >1800). The capability skim is the block's growth vector.
- **Capabilities are profile-tiered.** New `pg init` defaults to `frontier`
  (slim stubs); `verbose` ships the full corpus. `.proto-gear/PROFILE` records it.
- **Lessons layer is live** (`.proto-gear/lessons/`), doctor-validated,
  sync-indexed. Distinct from this file: SESSION_HANDOFF = current state; lessons
  = accumulated knowledge.
- **Branch invariant is enforced**, not just documented: `pg guard branch` +
  `pg hooks install`. This repo's own `.git/hooks/pre-commit` still runs tests;
  the guard installer correctly declines to clobber it (no-clobber path).
- **Five disciplines** ship (engineering, qa, devops, security, release) on the
  unmodified core; ADR-002 supervision primitives (actor/evidence/authority) are
  complete. (Unchanged this session — see git history / PROJECT_STATUS.)

## Shipped this cycle (recent)

- **PROTO-086–089** — the five-phase steering-framework rework (above), PRs
  #56–#59. Each phase its own reviewed, merge-on-green PR.
- (Earlier: ADR-002 arc PROTO-071–075, the 5th discipline PROTO-077, the §5.7
  interactive surfaces PROTO-080–082. See git history / PROJECT_STATUS.)

## Pending / In Progress

- **Nothing in flight.** All steering PRs merged to `development`. No release cut
  this session (these land in the next `development → main` release).

## Conventions In Force

- **Scope discipline:** engineering-only. Flag, don't build, anything else.
- **New discipline = zero core edits.** Drop `modules/<name>/`. If it needs a
  `module_core/`/`cli/` change, the abstraction is wrong — stop.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower
  never imports higher. Branch guard / profiles / lessons all live in
  `module_core/` (generic); engineering's installer calls them.
- **Steering philosophy (new this cycle):** conditions over keyword triggers;
  boundaries over behavioral micro-tuning; durable state (handoff, lessons,
  tickets, gates) over procedural prose; enforce invariants with exit codes
  (hooks/CI), not just NEVER-lines. Model-specific scaffolding belongs in the
  `verbose` profile, not the default.
- **Testing:** argparse.Namespace + capsys + tmp dirs; wizards out of scope.
  **Verify CI parity with bare `pytest tests/`** (not `python -m pytest`).
- **Git:** never commit to `main`/`development`; branch from `development`, PR
  back; **black is a hard CI gate**. Mark a ticket COMPLETED **in its own branch**
  so the status rides the PR.
- **Regen noise:** `AGENT_CONTEXT.md`/host configs carry a `Generated:` timestamp
  (and can pick up CRLF churn) — `git restore` when the diff is timestamp/EOL-only.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

---
*Agent-maintained. Replace entirely at session end.*
