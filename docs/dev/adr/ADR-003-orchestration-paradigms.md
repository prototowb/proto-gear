# ADR-003: Orchestration Paradigms + Per-Agent Model Tiers — Loosening the Fixed Roster

**Status:** Accepted (2026-07-14)
**Date:** 2026-07-14
**Deciders:** towb
**Ticket:** PROTO-083 (model tier), PROTO-084 (paradigm pool), PROTO-085 (doctrine)
**Related:** ADR-002 (supervision primitives — graded authority), ADR-001 (departmental module platform), PROJECT_SPECIFICATIONS.md §4 (supervision model), PROTO-067/076 (agent seam + bundled-agent surfacing)

## Context

`AGENTS.md` encoded a **fixed orchestration posture**: a mandated "4 Core + 2
Flex" agent roster plus an "EXECUTE IMMEDIATELY / ON_AGENTS_MD_READ" trigger that
told every agent to *activate* that roster on session start. In the dogfood
`AGENTS.md` the roster's `{{CORE_AGENT_*}}` placeholders were never even filled —
the doctrine commanded activation of agents that did not exist.

Two things this posture could not express, both central as AI capability grows:

1. **Which model a sub-agent runs on.** There was no lever to say "run the
   reviewer on a deep model, the mechanical refactor on a fast one." The agent
   schema (`AgentConfiguration`) had no model field at all.
2. **A different orchestration *shape* when circumstances demand it.** "4 core +
   2 flex" is one pattern; a trivial fix wants none of it, a release wants a
   discipline pipeline, a broad mechanical change wants parallel fan-out. The
   doctrine offered no way for the orchestrating party to *choose* — let alone
   *switch* — the shape.

The forcing function (as in ADR-002) is **rapid AI capability growth**: the
orchestrating party — a human via the interactive UI, or the overseeing agent —
must be able to (re)architect the roster and the model assignment *on the fly*,
optimizing for efficiency, without editing doctrine or code each time.

**The hard invariant is ADR-002's Principle 4:** the core *audits and declares;
it does not execute — agents act, `pg` audits*. ADR-002 explicitly **rejected
Option C** ("build an autonomous multi-agent execution/orchestration runtime").
Any loosening here must stay declarative.

## Decision

Introduce two declarative surfaces and loosen the doctrine around them. Nothing
here executes agents; it changes what an agent config and the doctrine *declare*
and what `pg` *surfaces*.

### 1. Per-agent model tier

An agent may declare `model: { tier, override? }` where `tier ∈ {fast, balanced,
deep}` (default `balanced`) and `override` optionally pins a concrete host model
id. The tier expresses **intent** (efficiency), not a vendor's model name; the
host maps it. Optional and backward-compatible — an absent block is `balanced`,
so the entire existing corpus is unchanged. Surfaced via `pg agent show/list`.

### 2. Orchestration paradigms — a selectable pool

An **orchestration paradigm** is a named, declarative pattern for *how* the
overseer distributes and coordinates sub-agents. Proto Gear ships a **pool** of
them (`dynamic`, `solo`, `driver-reviewer`, `core-flex`, `pipeline`, `fan-out`),
discovered exactly like bundled agents (seam S1: shared + per-discipline
`orchestration/` dirs). The orchestrating party **selects a paradigm and switches
on the fly** as work changes; a project may `pg orchestration install <id>` to
customise one. Surfaced via `pg orchestration list/show [--json]` and an
interactive browser + home-menu entry (UI-first).

The former "4 Core + 2 Flex" survives as **exactly one paradigm** (`core-flex`),
with the counts opened up — no longer a mandate, just an option.

### 3. Doctrine loosening

`AGENTS.md` drops the fixed-roster mandate and the auto-execute trigger for:
*compose the minimal set of sub-agents each task needs; pick and switch
paradigms and model tiers for efficiency; becoming more minimal never needs
approval.* The `agent-roles-4-core-2-flex` frontmatter concern becomes
`orchestration-paradigms`.

## Options Considered

### Option A: Keep the fixed roster; add a model field only
Cheapest, but leaves the autonomy *shape* hardcoded in prose — the exact
ossification ADR-002 warned about, one layer up. Rejected.

### Option B: Paradigms + model tiers as declarative, audited surfaces (chosen)
Reuses the bundled-capability/agent discovery machinery and the existing
`list/show/browse` surfaces; backward compatible (defaults reproduce today);
dogfoodable one paradigm/agent at a time. Preserves Principle 4 — declaration and
audit only.

### Option C: An orchestration *runtime* that assigns models and runs agents
Already rejected by ADR-002 (its Option C). Violates the audit-not-execute
boundary that keeps the framework host-agnostic and safe. Not reconsidered.

## Consequences

**Easier:**
- The orchestrating user *or* agent trades roster shape and model tier for
  efficiency as a first-class, reviewable choice — no doctrine/code edit per shift.
- The agent seam (PROTO-067) deepens: an agent config now carries an efficiency
  lever (tier), and paradigms give roles a place to slot agents.
- The dogfood `AGENTS.md` placeholder rot is resolved — dynamic doctrine needs no
  per-project agent names.

**Harder / watch:**
- The paradigm pool is *guidance the overseer follows*, not something enforced —
  its value depends on agents actually consulting it. (Consistent with the whole
  harness: docs are the API.)
- Two tier vocabularies now exist (agent `model.tier` and paradigm
  `roles[].model_tier`); they share the same enum and must stay aligned.

**Deliberately deferred:**
- **No paradigm INDEX generator.** Bundled paradigms are discovered *live* (like
  bundled agents via `pg agent list --available`); they earn a project INDEX
  entry only if installed. A bespoke generator would emit near-empty files and
  add drift-check surface for no discoverability gain.
- **No execution/assignment runtime** (Principle 4). Revisit only alongside
  ADR-002's deferred `agent` clearing rung, if a track record justifies it.
