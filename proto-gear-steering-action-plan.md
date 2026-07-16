# Proto Gear — Steering-Framework Action Plan

**Context:** Assessment of proto-gear's markdown steering surface against the
Claude Fable 5 prompting guidance
(https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
and the general capability trend of frontier models.

**Verdict in one line:** Markdown steering frameworks remain the right idea, but
their value has migrated from *teaching agents how to work* (methodology,
routing, rituals) to *telling agents what is true here* (state, memory,
boundaries, non-derivable facts). Proto-gear contains both halves; this plan
shifts weight to the durable one.

Two lines from the Fable 5 docs anchor everything below:

> "Skills developed for prior models are often too prescriptive for Claude
> Fable 5 and can degrade output quality."

> "Claude Fable 5 performs particularly well when it can record lessons from
> previous runs and reference them. Provide a place to write notes, as simple
> as a Markdown file."

---

## What to keep (and lean into)

| Asset | Why it's durable |
|---|---|
| `SESSION_HANDOFF.md` (rolling replace-not-append snapshot) | Exactly the memory pattern the Fable 5 docs recommend; worth *more* as runs get longer and more autonomous |
| `PROJECT_STATUS.md` + `pg` CLI as the state surface | Deterministic commands beat prose for reliability; the CLI is genuinely non-derivable knowledge |
| Pointer architecture (`CLAUDE.md` holds no content, points to canonical sources; `pg sync-context` prevents drift) | Progressive disclosure — same principle as the SKILL.md format; survives every model generation |
| Reference Index with the "Read When" column | Conditional loading beats mandatory loading; already the right shape |
| Hard invariants ("NEVER commit directly to `main`") | "State the boundaries" is explicitly recommended — capable models take unrequested-but-adjacent actions without them |

## What has aged out

| Asset | Problem |
|---|---|
| Bundled methodology skills (~12.5k lines; e.g. 738-line debugging skill, 379-line TDD tutorial) | Teaches frontier models what they already know better; docs say this *degrades* output; burns context |
| Keyword trigger table (`CLAUDE.md:57-86`) | Keyword routing was a crutch for weak routing judgment; over-fires (any "error" summons a 587-line workflow); duplicates the capability list above it |
| "MANDATORY READING — READ THESE FILES FIRST" walls (`AGENTS.md`) | Literal instruction-following means 8 forced file reads before a one-line fix; ALL-CAPS imperatives over-trigger on 4.6+ models |
| Same generated block duplicated into `.cursorrules` / `.windsurfrules` / `AGENT_CONTEXT.md` / `CLAUDE.md` | Managed by `pg sync-context`, so tolerable — but candidates for shrinking to pure pointers as tools converge on `AGENTS.md` |

---

## Action plan

### Phase 1 — Slim the generated context block (low effort, immediate win)

1. **Drop the Trigger → Capability table.** Keep the capability list, but give
   each entry a one-line *condition* instead of keywords:
   `skills/testing — use when writing or restructuring tests; enforces this
   repo's coverage targets`. Modern models route by judgment off descriptions;
   conditions in descriptions measurably improve should-use rates.
2. **Convert reading rituals to conditions.** Replace "MANDATORY READING /
   READ FIRST" with per-file conditions (the Reference Index already does
   this). Reserve ALL-CAPS/NEVER for true invariants only (branch protection,
   destructive actions). Rule of thumb from Anthropic's migration guides:
   `CRITICAL: YOU MUST…` written to overcome old-model reluctance now causes
   over-triggering.
3. **Set a token budget for the generated block** (e.g. ≤1,500 tokens),
   measured with the `count_tokens` API, and make `pg doctor` warn when the
   block exceeds it. Every line is a per-session tax on attention.

### Phase 2 — Refactor bundled capabilities from lessons to deltas

4. **Cut each skill/workflow to its project-specific delta.** The generic
   methodology (scientific debugging, red-green-refactor lecture) goes; what
   stays is the ~20 lines a model cannot derive: coverage targets, ticket
   integration, house conventions, release gates. Target: order-of-magnitude
   size reduction per capability.
5. **Adopt SKILL.md-style frontmatter** (name, one-line description, trigger
   condition) as the canonical capability header. This aligns proto-gear
   capabilities with the emerging cross-tool skill format, so they load
   natively in Claude Code and stay portable elsewhere.

### Phase 3 — Tier by agent capability (the model-agnostic answer)

6. **Introduce output profiles**, e.g. `pg init --profile frontier|standard|verbose`:
   - *frontier*: state files + boundaries + capability index only;
   - *verbose*: today's full scaffolding, for small/local/older models that
     still benefit from training wheels.
   This resolves proto-gear's strategic tension: "model-agnostic" currently
   means "written for the weakest model," which penalizes the strongest.
   Default new inits to the slim profile; keep verbose as opt-in.

### Phase 4 — Add the memory layer (the new high-value steering content)

7. **Ship a lessons directory** (`.proto-gear/lessons/` or similar), agent-
   writable, with the format from the Fable 5 docs: one lesson per file,
   one-line summary at top, corrections and confirmed approaches alike, delete
   what turns out wrong. `pg doctor` validates structure; `pg sync-context`
   surfaces the index. `SESSION_HANDOFF.md` stays the *current-state* snapshot;
   lessons are the *accumulated* knowledge.
8. **Add long-run grounding lines to the generated agent context** (small,
   high-leverage, straight from the docs): audit progress claims against tool
   results; when the user is describing a problem rather than requesting a
   change, report findings and stop; pause only for destructive actions, scope
   changes, or input only the user can provide.

### Phase 5 — Move invariants from prose to enforcement

9. **Where an invariant matters, enforce it outside the prompt**: branch
   protection via git hooks/CI rather than (only) a NEVER-line; ticket-status
   hygiene via `pg doctor --fix`; gate checks via the existing supervision
   pipeline. Prose compliance is model-dependent; hooks and CI are not. Keep
   the prose line as documentation of the rule, not as its enforcement.

---

## Future-proofing principles

**Design for shrinking prose, growing state.** Every model generation since
Claude 4 has needed *less* procedural instruction and rewarded *more* durable
state and memory. Any line that explains a general technique is on a
depreciation schedule; any file that records what happened, what was decided,
and what is true is appreciating. Bias the roadmap accordingly.

**Don't couple to one model's quirks.** Write steering that degrades
gracefully: conditions instead of keyword triggers, goals and constraints
instead of step enumerations, boundaries instead of behavioral micro-tuning.
Model-specific workarounds (anti-refusal phrasing, forced-progress scaffolding,
"think step by step") should live — if anywhere — in the verbose profile,
clearly marked, so they can be deleted per tier without archaeology.

**Bet on the converging standards.** `AGENTS.md` is becoming the cross-tool
entry point and SKILL.md-style progressive disclosure the cross-tool capability
format. Proto-gear's differentiation is not the markdown itself (any model can
write markdown) but the *state machinery around it*: sync, drift detection
(`pg doctor`), tickets, gates, traceability. Investing there is safe against
any model release; investing in richer prose templates is not.

**Let agents maintain the framework.** The Fable 5 docs note the model "does a
good job of updating skills on the fly based on what it learns." The
future-proof posture is agent-writable-by-default (lessons, handoffs, status)
with machine validation (doctor, schemas, sync markers) guarding structure —
rather than human-authored prose guarded by "do not hand-edit" comments.

**Expect the floor to keep rising.** The verbose profile's audience (models
that need methodology scaffolding) shrinks every quarter, but it won't hit zero
soon — cheap local models are proliferating at the same time. Tiering is
therefore not a transition plan but a permanent architecture: one canonical
capability source, rendered at different verbosity per consumer.

---

*Prepared 2026-07-16, based on proto-gear @ main (v0.20.0) and the Claude
Fable 5 prompting guide.*

---

## Implementation log

- **Phase 1 — DONE** (PROTO-086, PR #56). Dropped the keyword `Trigger →
  Capability` table and the per-capability `_triggers:_` suffix from the
  generated block; agents route off descriptions now. Rewrote the AGENTS.md
  "MANDATORY READING" wall as a conditional "read what the task calls for"
  table, reserving `NEVER` for the one true invariant. Added
  `estimate_tokens` + `AGENT_CONTEXT_TOKEN_BUDGET` (1500) enforced by
  `doctor.check_agent_context_budget`; the dogfood block sits at ~1486/1500.

- **Phases 2 + 3 — DONE** (PROTO-087). Merged per the "cut, but preserve via
  profiles" decision: rather than hand-fencing 15k lines, proto-gear keeps the
  verbose `*.template.md` bodies as the single source and *renders* them per
  profile. `pg init --profile frontier|verbose` (default **frontier**):
  `frontier` ships a slim stub generated from each capability's `metadata.yaml`
  (title, description, when-to-use, pointer to host docs) in place of the
  methodology; `verbose` ships the full playbooks unchanged. Nothing is lost —
  `verbose` is one flag away. The chosen profile is recorded in
  `.proto-gear/PROFILE`. Machinery lives in
  `module_core/capability_profile.py`; both the shared installer and the
  per-module installer honour it. This makes tiering a permanent architecture
  (one source, rendered at different verbosity), not a one-off deletion.

- **Phase 4 — DONE** (PROTO-088). Shipped the agent-writable lessons layer:
  `.proto-gear/lessons/` (bundled README + INDEX scaffold), one lesson per file
  (`# Title` + `> summary` + body), machine-validated by `doctor.check_lessons`
  and indexed by `sync_lessons_index` (wired into `pg sync-context`).
  `SESSION_HANDOFF.md` stays current-state; lessons are accumulated knowledge.
  Also added the three long-run grounding lines (item 8) as a **Working
  Agreement** section in the generated context — audit progress claims against
  tool results; report-and-stop when the user is describing a problem; pause only
  for destructive actions / scope changes / user-only decisions. Machinery in
  `module_core/lessons.py`; budget recalibrated to 1800 (fully-loaded project).

- **Phase 5 — DONE** (PROTO-089). Moved the one hard invariant from prose to
  enforcement: **`pg guard branch`** exits non-zero when HEAD is on a protected
  branch (`main`/`master`), a deterministic check a hook/CI/agent can call
  (`module_core/guard.py`). **`pg hooks install`** drops a no-clobber branch-guard
  `pre-commit` hook (bundled `hooks/pre-commit`, calls `pg guard branch`;
  `module_core/hooks.py`). BRANCHING documents `pg guard` / the hook / CI as the
  *how*, keeping the NEVER prose as the *why*. Gate checks (the other enforcement
  axis) already ship via the ADR-002 supervision pipeline. Prose compliance is
  model-dependent; a non-zero exit code is not.

**All five phases of this plan are shipped.** The steering surface now leans on
durable state and machine-checked boundaries rather than procedural prose:
description-routed capabilities, a profile-tiered corpus, an agent-writable
lessons layer, long-run grounding, and an enforced branch invariant.
