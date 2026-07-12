# ADR-002: Supervision Primitives for Autonomous Agents — Actor, Evidence, Graded Authority

**Status:** Accepted (2026-07-11) — with amendment: the `agent` authority rung is **deferred**, not part of the contract yet (see §3).
**Date:** 2026-07-11
**Deciders:** towb
**Ticket:** PROTO-068 (proposed), PROTO-069 (accepted + amended)
**Related:** ADR-001 (departmental module platform), PROJECT_SPECIFICATIONS.md §4 (supervision model), PROTO-060–066 (pipeline/trace/release + gates-as-data), PROTO-067 (agent seam)

## Context

Proto Gear is an **agent-guidance harness for the software-development
lifecycle**, not a human-convenience CLI. Its job is to guide and *supervise*
increasingly capable AI agents through engineering work — not to run a command
palette for a person, and not to execute agents itself (Principle 4: *the core
executes nothing from bundles; agents act, `pg` audits*).

The supervision machinery is now real and proven end-to-end:

- **Gates are data** (`gates:` in workflow `metadata.yaml`: `id`, `before`,
  `approver`, `required`, optional `scope: change|release`, optional
  `evidence:` column). `pg doctor` audits them; `pg pipeline` composes them into
  the path to production; `pg trace`/`pg release` verify them per change and per
  release.
- **Agents are declarable and composable per discipline** (PROTO-067): a
  discipline ships `modules/<name>/agents/` and the core discovers, installs,
  and validates them with zero core edits — and an agent can compose its own
  department's capabilities.

**The forcing function is rapid AI capability growth.** The current supervision
model encodes a *fixed* posture — PROJECT_SPECIFICATIONS §4's "agent proposes,
human approves" — and every gate hardcodes `approver: "human"`. That was the
right default for today. It will not age well: as agents get materially more
capable, three things shift, and the architecture currently has no seam for any
of them.

1. **More of the lifecycle is both executed *and verified* by agents.** Routine
   verification (did tests pass? is coverage met? is every finding remediated?)
   is mechanizable and increasingly agent-ownable. Human attention should
   concentrate at the few high-stakes gates — irreversible actions, genuine risk
   acceptance — not at every checkbox.
2. **The autonomy boundary must move per-gate, by configuration, tracking
   capability** — not by rewriting workflows or editing the core each time a
   class of work becomes safe to delegate.
3. **A gate actually bundles three distinct concerns the current schema
   conflates:**
   - *who does the guarded work* — unrepresented (only loose `agent_roles:`
     metadata on capabilities);
   - *what proves the work is acceptable* — partially represented (the
     `evidence:` column), but as "a cell to eyeball," not a checkable predicate;
   - *who has authority to clear it* — represented, but only as the literal
     string `"human"`.

Two invariants must survive any change: **Principle 4** (the core audits, it
does not execute — no runtime that "runs agents through gates") and the
**§4 escalation rule** (on an undeclared situation the agent stops and asks;
*silence is never consent*).

## Decision

Promote three **supervision primitives** to first-class in the gate contract,
and **grade authority** so the model scales *with* capability by declaration,
not by code. This stays entirely within the audit posture — it changes what a
gate *declares* and what `pg` *checks*, never what the core *runs*.

### 1. Actor — who is accountable for the guarded work

A gate may name an **actor**: the entity accountable for producing the work the
gate guards. An actor is a discipline agent (`qa/qa-release-agent`), a human
role, or unassigned. This is distinct from the approver (who *clears*) and gives
the PROTO-067 agent seam operational meaning: an agent is no longer only
*declarable*, it is *accountable* — traceable as the party that did the work a
gate checks. Note the deliberate asymmetry (see §3): an agent may be the
**actor** and may **recommend**, but it does not yet hold **clearing**
authority.

### 2. Evidence as predicate — what proves the gate is satisfied

Today's `evidence:` names a column to look at. Promote it: a gate clears iff a
**machine-checkable predicate over the state surface holds** — e.g. "the
`Reviewed by` cell for this ticket is non-empty and names a recognized
approver." The predicate *reads* markdown; it executes nothing (docs remain the
API, Principle 1 & 4 intact). This turns `pg trace`/`pg release` from "is there
a name in the cell?" into "does the evidence predicate for this gate hold?" —
the same surfaces, a firmer contract.

### 3. Graded authority — the capability-growth axis

Each gate declares the **minimum authority** required to clear it. The ladder as
adopted has three active rungs, ordered most→least human involvement:

| Authority | Meaning |
|-----------|---------|
| `human` | Requires a **human** signer (default — unchanged from §4). |
| `human-on-recommendation` | An agent verifies + recommends; a **human ratifies**, recording the residual-risk acceptance. The current **ceiling** for any gate involving judgment. |
| `auto` | Cleared by the evidence predicate alone — reserved for **deterministic, non-judgment facts** (e.g. "tests recorded green," "coverage ≥ threshold"). Not for anything requiring judgment. |

**Amendment (PROTO-069): the `agent` rung is deferred.** The originally proposed
`agent` rung — an agent as the accountable *clearer*, exercising judgment and
recording *itself* as signer — is **not** part of the contract. An agent may be
the **actor** (does the work) and may **recommend** under
`human-on-recommendation`, but a human retains clearing authority for every
judgment gate. The rung remains a documented future extension, revisited only
once there is a track record justifying it (see *Revisit when*); until then the
ceiling is `human-on-recommendation`.

The default remains `human`, so the entire existing corpus is unchanged.
**Capability growth is expressed by lowering a specific gate's required authority
in its metadata — a one-line config change, zero core or workflow-structure
edits** — but, per the amendment, only as far down as `human-on-recommendation`
for judgment gates. `pg doctor`/`pg trace`/`pg release` gain an authority
dimension for free: they can report whether each cleared gate was cleared by a
signer of *sufficient* authority.

The through-line is the separation of **verification** (mechanizable,
evidence-predicated, agent-ownable) from **risk acceptance** (retained by a
human). That separation is what lets autonomy expand *safely*: agents take over
more of the *verification and recommendation*, while a human still *ratifies*
the residual risk at every judgment gate.

## Options Considered

### Option A: Keep `approver: human`; add agents as loose metadata

| Dimension | Assessment |
|-----------|------------|
| Complexity | Lowest |
| Scales with capability | No — the autonomy boundary stays hardcoded in prose |
| Auditability | Can't answer "is this gate's verification safe to delegate yet?" |

**Cons:** every capability step-change means hand-editing `approver`/prose across
workflows; no way to audit or govern the human→agent handoff; the agent seam
stays decorative in supervision.

### Option B: Actor + evidence-predicate + graded authority as contract primitives (chosen)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — schema + predicate vocabulary + audit extension |
| Scales with capability | Yes — migration is per-gate config, doctor-audited |
| Auditability | High — sufficiency of authority is checkable |
| Principle 4 | Preserved — declarative + audit only, no execution |

**Pros:** scales with capability by declaration; reuses the existing
pipeline/trace/release/doctor surfaces (no new human-facing CLI — aligns with the
harness-not-palette vision); backward compatible (defaults reproduce §4);
dogfoodable one gate at a time.
**Cons:** the gate schema grows (needs careful defaults so single-gate
disciplines stay trivial); the evidence-predicate vocabulary must stay
declarative and safe (never a code-execution surface); "authority" must be
defined crisply to avoid security theater.

### Option C: Build an autonomous multi-agent execution/orchestration runtime now

| Dimension | Assessment |
|-----------|------------|
| Complexity | High |
| Principle 4 | **Violated** — the core would execute agents through gates |
| Maturity fit | Premature — primitives unproven; hosts run agents, we guide them |

**Cons:** contradicts the audit-not-execute boundary; enormous surface before the
supervision primitives are proven; couples proto-gear to a specific runtime when
its value is host-agnostic guidance.

## Trade-off Analysis

The real choice is **when to pay, and for what**. Option A never pays and lets
the autonomy boundary ossify as prose. Option C pays for an execution engine
before the primitives that engine would need are proven — and breaks the audit
boundary that makes the framework host-agnostic and safe. Option B pays only for
the **contract**: the declarative primitives and their audit, provable by
dogfooding on the engineering + qa gates before promotion to contract v1.

Graded authority is specifically a **hedge against an unknown**: we cannot
predict *when* a given gate's verification becomes safe to delegate. So we make
that transition a one-line, doctor-audited config change rather than a code
change — the architecture accommodates capability growth it cannot forecast,
while keeping a human on residual-risk acceptance (the `agent` clearing rung
stays deferred until evidence justifies it).

## Consequences

**Easier:**
- A gate expresses *who acts / what proves / who clears* explicitly, instead of
  smuggling all three into `approver: human`.
- Moving a gate's *verification* to an agent (up to `human-on-recommendation`)
  becomes reviewable config, audited by `pg doctor` — a governed handoff, not a
  silent edit — while a human still ratifies.
- The PROTO-067 agent seam gains operational meaning: agents become accountable
  **actors** and **recommenders** within `pg trace`/`pg release`; clearing stays
  with a human.

**Harder:**
- The gate schema grows; defaults must keep single-gate disciplines trivial.
- The evidence-predicate vocabulary must be small, declarative, and provably
  non-executing — a design constraint, not an afterthought.
- "Authority" needs a crisp definition (what an `auto`-cleared or
  `human-on-recommendation` gate actually guarantees) or it becomes theater.

- **The deferred `agent` clearing rung** — revisit only once there is a track
  record of `human-on-recommendation` gates where the human ratification was
  consistently a rubber stamp, *and* a decision that the residual risk is
  acceptable to delegate. Until then, `human-on-recommendation` is the ceiling.
- Evidence predicates strain markdown-as-API — reconsider a typed state surface
  (in tension with Principle 1, "docs are the API").
- If the actor/approver split proves to add ceremony without leverage on
  single-owner disciplines, collapse it back with a doctor warning.

## Action Items

Architecture, phased — not a build commitment. Each ships behind green tests,
dogfooded, and surfaces through existing commands (no new human-facing palette).

1. [x] Spec the gate-schema extension — `actor`, `authority` (with §4-preserving
       defaults), and evidence-as-predicate; `pg doctor` validates.
       *(PROTO-071 — `actor` + three-rung `authority` in the gate schema,
       doctor-validated: deferred/unknown rungs are errors, `auto` requires an
       `evidence` column, a namespaced actor must name a shipped agent. The v1
       evidence predicate is the implicit "cell non-empty and not 'pending'"
       check `pg trace` already applies; the richer vocabulary is item 2.)*
2. [x] Define the evidence-predicate vocabulary — declarative checks over
       state-surface columns; provably non-executing.
       *(PROTO-072 — `GATE_EVIDENCE_PREDICATES = non-empty | equals |
       at-least`; in YAML `evidence:` is a plain column string (non-empty) or
       a `{column, predicate, value}` mapping. Pure string/number comparison
       over a markdown cell — nothing can name or run code; an unknown
       predicate never clears and the doctor rejects it. `pg trace`/`pg
       release` evaluate the predicate; a filled cell that fails the claim is
       pending, never cleared.)*
3. [ ] Extend `pg trace`/`pg release` to report **authority sufficiency** (was
       each cleared gate cleared by a signer of adequate authority?) — reuse the
       surfaces, add no commands.
4. [x] Dogfood falsifier: migrate exactly one engineering gate to an evidence
       predicate + `human-on-recommendation` (agent verifies + recommends, human
       ratifies); keep pure-human gates human. No `agent` clearing rung. If it
       needs a core edit, the primitive is wrong — stop.
       *(PROTO-073 — `pr-review-approval` migrated: actor
       `code-review-agent`, authority `human-on-recommendation`, evidence in
       mapping form (explicit non-empty over "Reviewed by"). **The falsifier
       held**: the entire migration is the workflow's own metadata.yaml — zero
       `module_core`/`cli` edits — and doctor/pipeline/trace/release picked it
       up unchanged. All other gates remain pure `human`.)*
5. [ ] Update PROJECT_SPECIFICATIONS §4 to describe **graded authority** as the
       supervision model's capability-growth axis.
