<!-- proto-gear:header
purpose: North-star vision and product specification — proto-gear as the first AI-supervised departmental module of the agency operating system
read-when: starting features or design work; any decision that trades short-term convenience against the module-platform direction
priority: required
defines:
  - vision-statement
  - the-agency-os
  - module-contract
  - supervision-model
  - roadmap-phases
  - success-criteria
  - non-goals
links:
  - ARCHITECTURE.md
  - docs/dev/adr/ADR-001-departmental-module-platform.md
  - PROJECT_STATUS.md
-->

# PROJECT SPECIFICATIONS — Proto Gear

> **North star**: Proto Gear is the first of a set of AI-supervised departmental
> modules that will run our agency. It is the **Engineering Department module** —
> and the reference implementation of the module pattern itself.

## 1. Vision Statement

An agency is a set of departments — engineering, content, operations, finance —
each with its own workflows, artifacts, and institutional knowledge. Today that
knowledge lives in people's heads and scattered tools. The vision is an
**agency operating system**: each department becomes a *module* that an AI agent
can operate under human supervision, with the department's knowledge encoded as
structured, versioned, drift-checked documentation and capabilities.

Proto Gear proves the pattern in the department we know best: engineering. It
already encodes tickets, branching, testing, releases, code review, and incident
response as capabilities an agent discovers and follows. The next step is to
harden that pattern into a **module contract** other departments can implement,
so that "add a department" becomes composition, not a rewrite.

**One sentence**: *Proto Gear turns a department's way-of-working into a
machine-readable, self-auditing context that any AI agent host can load — and
the engineering department is module #1.*

## 2. The Agency OS (target picture)

```
                    ┌────────────────────────────────────────────┐
                    │              HUMAN SUPERVISION              │
                    │   (review gates, approvals, escalation)     │
                    └──────────────────────┬─────────────────────┘
                                           │
                    ┌──────────────────────▼─────────────────────┐
                    │            SHARED MODULE CORE               │
                    │  capability schema · context sync · doctor  │
                    │  ticket/state model · discovery · templates │
                    └──────┬──────────────┬──────────────┬───────┘
                           │              │              │
                ┌──────────▼───┐  ┌───────▼──────┐  ┌────▼─────────┐
                │ ENGINEERING  │  │   CONTENT    │  │   OPS / PM   │
                │ (proto-gear) │  │  (future)    │  │  (future)    │
                │ code · tests │  │ posts · brand│  │ clients ·    │
                │ releases     │  │ campaigns    │  │ scheduling   │
                └──────────────┘  └──────────────┘  └──────────────┘
```

What stays constant across departments (the **core**): capability metadata
schema, context generation/sync, drift detection, state tracking (tickets),
discovery (prose → capability), and the supervision conventions. What varies
per department (the **module**): the capabilities themselves, the templates,
the state artifacts, and the tool integrations.

## 3. Module Contract (what makes something a departmental module)

A departmental module MUST provide:

1. **Capabilities** — skills / workflows / commands as `metadata.yaml` +
   markdown bundles under `.proto-gear/`, with triggers so agents discover them
   from task prose.
2. **State surface** — a single source of truth for department state
   (engineering: `PROJECT_STATUS.md` tickets; content: e.g. a content queue),
   updatable via CLI and readable by agents.
3. **Context manifest** — an auto-generated, ≤120-line skim
   (`AGENT_CONTEXT.md` pattern) mirrored into whatever surface the agent host
   auto-loads.
4. **Drift detection** — `doctor`-style checks proving the manifest, state, and
   capabilities agree; every check auto-repairable or clearly triaged.
5. **Supervision points** — explicit human gates declared in workflows (e.g.
   "PR review before merge", "content approval before publish"), never implied.
6. **Handoff protocol** — a rolling `SESSION_HANDOFF.md` so any agent (or
   human) can resume mid-stream.

Proto Gear v0.10.0 already satisfies 1–4 and 6 for engineering; 5 exists as
convention (BRANCHING.md review gates) but is not yet machine-declared. Closing
that gap — and extracting 1–6 into a reusable core — is the platform work.

## 4. Supervision Model

"AI supervised" cuts both ways, deliberately:

- **AI-supervised work**: agents run the department's workflows, keep state
  current, detect drift, and prepare artifacts (PRs, releases, reports).
- **Human-supervised AI**: every workflow declares its gates. The default
  posture is *agent proposes, human approves* at declared gates; routine
  low-risk steps run autonomously. Gates are data (in capability metadata),
  not prose — so tooling can enforce "this workflow has an unapproved gate"
  the same way `pg doctor` enforces context drift today.

Escalation rule: when a workflow hits an undeclared situation, the agent stops,
records state in SESSION_HANDOFF.md, and asks. Silence is never consent.

## 5. Product Principles (extends ARCHITECTURE.md design principles)

1. **Docs are the API.** Modules encode knowledge as markdown + YAML that both
   humans and agents read. No opaque runtime state.
2. **Drift is the enemy; doctor is the immune system.** Every new surface ships
   with a check. If it can go stale silently, it's not done.
3. **Host-agnostic.** Claude Code, Cursor, Windsurf, Copilot — the module
   mirrors context into whatever the host auto-loads. No host lock-in.
4. **The core executes nothing from bundles.** Capabilities remain
   documentation; agents act, `pg` audits. (Security boundary — unchanged.)
5. **Dogfood or it didn't happen.** proto-gear runs on proto-gear. Every module
   pattern must be proven here before it's declared part of the contract.
6. **Composition over configuration.** New departments assemble core primitives;
   they don't fork the core.

## 6. Roadmap

### Phase A — Harden the Engineering Module (v0.11.x)
- Split the `proto_gear.py` monolith along the module boundaries ARCHITECTURE.md
  already documents (CLI dispatch vs. init engine vs. template generation).
- Fix robustness gaps (e.g. optional-dependency import crash, PROTO-041).
- Raise coverage on business logic; kill repo hygiene debt (tracked build
  artifacts, backup files).
- Machine-declared supervision gates in workflow metadata (contract item 5).

### Phase B — Extract the Module Core (v0.12.x)
- Factor the department-agnostic engine (capability schema, sync, doctor,
  discovery, state model) into a `module core` package layer with the
  engineering module as its first consumer.
- Module manifest: `module.yaml` declaring a module's state surface, gates,
  and capability roots — the doctor validates it.
- `pg` learns to host >1 module in one project (`pg --module content status`).

### Phase C — Second Department Proves the Contract (v0.13+)
- Ship the **Content/Marketing module** as the second implementation (content
  queue as state surface; publish gates as supervision points) — chosen because
  the agency already runs content tooling that can back it.
- Contract v1.0: anything that satisfies the module contract runs on the core
  unmodified. Two independent modules = the pattern is real.

### Phase D — Agency OS (v1.x)
- Cross-module orchestration: engineering ticket ↔ content campaign links,
  agency-level dashboard, per-department agents with a shared supervision
  inbox.

## 7. Success Criteria

- **Phase A**: 0 import-time crashes in any dependency configuration; no module
  >1,200 lines; `pg doctor` green including new gate checks; coverage on core
  business logic ≥ 70%.
- **Phase B**: engineering module consumes the core through the same interfaces
  a future module would; adding a toy second module requires **zero core edits**.
- **Phase C**: content module operated by an agent end-to-end (draft → gate →
  publish) with every gate hit logged.
- **Ongoing**: a fresh agent session reaches correct, current context in ≤1 file
  auto-load + ≤2 reads (the AGENT_CONTEXT promise, held across all modules).

## 8. Non-Goals (unchanged from ARCHITECTURE.md, restated for the platform)

- Not a runtime or agent host — modules describe work; hosts execute agents.
- Not a scaffolder for the host project's tech stack.
- Not an LLM client; no model calls inside `pg`.
- Not a replacement for the tools departments already use (GitHub, socials,
  accounting) — modules *wrap* department practice, integrations stay thin.

---
*Owner: towb · Drafted 2026-07-07 (PROTO-039) · Living document — revise at each phase boundary.*
