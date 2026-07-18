# ADR-004: Frontier-Era Init Planning — From Template Configurator to State Elicitation

**Status:** Accepted (2026-07-18) — implemented in PROTO-100
**Date:** 2026-07-18
**Deciders:** towb
**Ticket:** PROTO-100 (implementation)
**Related:** `proto-gear-steering-action-plan.md` (the Fable 5 steering arc, PROTO-086–092), ADR-003 (orchestration paradigms — UI-first selection), PROTO-096–099 (interactive navigate/pick shell), the [Prompting Claude Fable 5 guide](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)

## Context

The steering-framework arc (PROTO-086–092, v0.21.0) reworked proto-gear's
markdown surface against the Fable 5 guidance: description-routed capabilities, a
`frontier|verbose` profile-tiered corpus, an agent-writable lessons layer,
long-run grounding, and an enforced branch invariant. It fixed **what init
installs** and **how the generated context reads**.

It did **not** touch **how `pg init` plans** — the interactive wizard's
*interaction model*. That is still the pre-Fable-5 shape:

- Four **presets** — Quick / Full / Minimal / Custom (`interactive_wizard.py`
  `PRESETS`) — framed as "how much scaffolding do you want?"
- A **template-selection** step: check which of ~8 `*.md` files to generate.
- Capability category/granular toggles.
- `ask_capability_profile` (frontier/verbose) and `ask_project_specifications`
  (a single optional description prompt) bolted onto that flow.

The wizard is a **template configurator**: its questions are about *mechanical,
model-derivable choices* (which files, which toggles). This is exactly the class
of prose/scaffolding the Fable 5 migration says has aged out — it asks a frontier
model's operator to hand-pick things the harness could detect or default, and it
spends almost none of the interaction capturing the **non-derivable, durable
facts** the docs say Fable 5 thrives on:

> "Provide a place to write notes… record lessons." — and, on steering: state
> the goals, the constraints, and the boundaries; skip the procedural
> micro-management.

Two enabling facts are now true that were not when the wizard was written:

1. **The UI-first shell exists** (PROTO-096–099): a navigate/pick nav framework
   with a guided Setup → Init/re-init entry. Init planning has a native home.
2. **A guided re-init already exists** (`run_incremental_wizard` + the PROTO-099
   pane). This ADR is about the **fresh-init planning** path; it must not
   duplicate the re-init surface.

**Forcing function:** rapid model capability growth. Every generation needs
*less* mechanical configuration and rewards *more* captured intent. An init flow
built around template checkboxes penalizes the strongest models and produces the
weakest steering artifacts.

## Decision (proposed)

Reframe fresh `pg init` from a **template configurator** to a **state-elicitation
planning intake**. Invert what the interaction spends time on:

> **From "which templates do you want?" (mechanical, derivable) → to "what is
> true, intended, and forbidden here?" (durable, non-derivable).** Files become a
> byproduct of detection + intent, not the subject of the conversation.

Three concrete moves:

### 1. Detect-and-default the mechanical choices

Everything the harness can infer, it infers and *shows* rather than *asks*:
project type/framework (`detect_project_structure`), git + ticket prefix
(`detect_git_config`), and a **detection-driven template set** (git repo →
BRANCHING; tests present → TESTING; etc.). Profile stays `frontier` by default.
Present these as a confirmable summary, not a sequence of prompts. The
Quick/Full/Minimal/Custom presets collapse into: **smart default** (accept the
detected plan) with **Customize** as an advanced escape hatch, not the main path.

### 2. Spend the interaction on the durable, non-derivable facts

The core of the flow becomes a short, progressive **intent capture** — the
things a model genuinely cannot derive and that Fable 5 steering wants:

- **What is this project?** (1–3 sentences → seeds `PROJECT_SPECIFICATIONS.md`)
- **Boundaries / invariants** — what must an agent *never* do here? (→ the
  `NEVER`/Critical-Rules lines, the one class of prose the steering arc keeps)
- **House conventions & constraints** — non-obvious, non-derivable (→ specs +
  an optional seed lesson in `.proto-gear/lessons/`)

Each prompt is skippable; the flow degrades to "just scaffold it" for users in a
hurry. This is the inversion — the *durable state* is the product.

### 3. Hand off to the agent, don't finish in the wizard

Per the Fable 5 posture "let agents maintain the framework," init ends by
**writing a task, not by pretending completeness**: seed `SESSION_HANDOFF.md` /
a lessons entry instructing the agent to expand `PROJECT_SPECIFICATIONS.md` and
extract architecture into `PROJECT_ARCHITECTURE.md` from the captured intent.
The hook partially exists (`ask_project_specifications`); make it the spine.

**Home:** this flow lives in the UI shell (Setup → Init), built on the PROTO-096
nav framework, consistent with the UI-first vision — `--flags` remain the
scriptable path.

## Options considered

- **A — Keep the preset wizard (do nothing).** Rejected: leaves the one
  un-migrated Fable-5 surface; the opening motivation for this whole arc.
- **B — Add a fifth "Frontier/Planning" preset.** Rejected as the *primary*
  answer: bolts intent-capture onto the configurator without inverting it; two
  competing philosophies in one wizard.
- **C — Reframe to state-elicitation, presets become an advanced mode.**
  **Chosen (proposed).** Applies the exact Fable 5 migration (mechanical →
  durable) to init itself; reuses the nav shell; keeps `verbose`/Customize for
  the audience that still wants knobs.

## Consequences

- **Positive:** init produces better steering artifacts (captured intent,
  boundaries, seed lessons) instead of empty templates; fewer prompts for the
  common path; the last pre-Fable-5 surface is migrated; dogfoods the nav shell.
- **Cost / risk:** touches a sensitive, well-tested subsystem (`interactive_wizard.py`,
  `run_enhanced_wizard`, `run_simple_protogear_init`). Must preserve the
  non-interactive `--flags` path and the `verbose`/Custom escape hatch, and must
  not disturb the guided re-init (PROTO-099) path. Intent prompts must be
  genuinely skippable so init never becomes *heavier* than today.
- **Neutral:** re-init is unchanged; only fresh init's planning model changes.

## Open questions — resolved by the implementing session (PROTO-100)

1. **How much intent to elicit by default** — minimal + progressive: three
   prompts (one-liner description → boundaries loop → conventions loop), every
   one skippable with a plain Enter. No goals/constraints interview; the specs
   stub carries placeholder sections for the agent to expand.
2. **Seed a lesson on init?** — **Yes.** Captured boundaries/conventions become
   `.proto-gear/lessons/house-conventions.md` (well-formed lesson, indexed),
   when capabilities are installed. Boundaries additionally flow into the
   generated Critical Rules: the stub's `## Boundaries & Invariants` bullets
   are parsed by `sync_context` into every host mirror on each sync.
3. **Native nav screens vs. questionary wizard** — **reuse the questionary
   wizard.** The shell's Setup → Init already fronts the real `pg init`
   subprocess (PROTO-099), so the new intake lands in the UI shell with zero
   shell changes, and the wizard keeps its TTY.
4. **Migration** — **replace outright.** The Quick/Full/Minimal preset front is
   gone; the granular Custom path survives as the `Customize (advanced)` escape
   hatch, and the non-interactive `--flags` path is untouched.

**Implementation notes:** pure planning helpers live in
`modules/engineering/init_planning.py` (detected plan, specs stub, seed lesson,
handoff task); `run_enhanced_wizard` is the intake (intent capture → detected
plan → accept / adjust prefix / customize / cancel); `setup_agent_framework_only`
gained `boundaries`/`conventions` and treats an explicitly-passed empty template
selection as "none" (the accepted plan is a contract — no legacy fall-through).
An existing PROJECT_SPECIFICATIONS.md is never clobbered; intent then lands in
the seed lesson and the handoff task only. A fresh SESSION_HANDOFF.md carries a
"First agent task" pointing at the captured intent (hand off, don't pretend
completeness). Re-init (`run_incremental_wizard`) is unchanged.

*Prepared 2026-07-18; implemented the same day (PROTO-100). Phase 3/3 of the
interactive-frontier effort; the steering arc (PROTO-086–092) migrated the
content, the shell arc (PROTO-096–099) built the surface, and this migrated the
init planning model itself.*
