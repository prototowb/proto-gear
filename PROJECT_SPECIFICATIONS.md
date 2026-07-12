<!-- proto-gear:header
purpose: North-star vision and product specification — proto-gear as the operating system for software engineering, its disciplines shipped as AI-supervised modules
read-when: starting features or design work; any decision that trades short-term convenience against the module-platform direction
priority: required
defines:
  - vision-statement
  - the-software-engineering-os
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

> **North star**: Proto Gear is an operating system for **software engineering**.
> Each engineering discipline becomes an AI-supervised module; the generalist
> engineering module is #1 — and the reference implementation of the module
> pattern itself. Scope is the engineering circle only, not a whole business.

## 1. Vision Statement

Software engineering is a set of disciplines — development, testing/QA,
DevOps/SRE, security, documentation, release & project management — each with its
own workflows, artifacts, and institutional knowledge. Today that knowledge lives
in people's heads and scattered tools. The vision is a **software-engineering
operating system**: each discipline becomes a *module* (a "department" within the
engineering circle) that an AI agent can operate under human supervision, with the
discipline's knowledge encoded as structured, versioned, drift-checked
documentation and capabilities.

Proto Gear proves the pattern in the generalist core we know best: the software
development lifecycle. It already encodes tickets, branching, testing, releases,
code review, and incident response as capabilities an agent discovers and
follows. The next step is to harden that pattern into a **module contract** other
engineering disciplines can implement, so that "add a discipline" becomes
composition, not a rewrite.

**One sentence**: *Proto Gear turns an engineering discipline's way-of-working
into a machine-readable, self-auditing context that any AI agent host can load —
and the generalist engineering discipline is module #1.*

## 2. The Software-Engineering OS (target picture)

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
                │ ENGINEERING  │  │   QA / TEST  │  │  DEVOPS/SRE  │
                │ (proto-gear) │  │  (future)    │  │  (future)    │
                │ code · tests │  │ test plans · │  │ deploys ·    │
                │ releases     │  │ defect queue │  │ incidents    │
                └──────────────┘  └──────────────┘  └──────────────┘
```

Every department here is an **engineering** discipline. What stays constant
across them (the **core**): capability metadata schema, context generation/sync,
drift detection, state tracking (tickets), discovery (prose → capability), and
the supervision conventions. What varies per discipline (the **module**): the
capabilities themselves, the templates, the state artifacts, and the tool
integrations.

## 3. Module Contract (what makes something an engineering-discipline module)

A discipline module MUST provide:

1. **Capabilities** — skills / workflows / commands as `metadata.yaml` +
   markdown bundles under `.proto-gear/`, with triggers so agents discover them
   from task prose.
2. **State surface** — a single source of truth for the discipline's state
   (engineering: `PROJECT_STATUS.md` tickets; QA: e.g. a test-plan / defect
   queue), updatable via CLI and readable by agents.
3. **Context manifest** — an auto-generated, ≤120-line skim
   (`AGENT_CONTEXT.md` pattern) mirrored into whatever surface the agent host
   auto-loads.
4. **Drift detection** — `doctor`-style checks proving the manifest, state, and
   capabilities agree; every check auto-repairable or clearly triaged.
5. **Supervision points** — explicit human gates declared in workflows (e.g.
   "PR review before merge", "sign-off before release"), never implied.
6. **Handoff protocol** — a rolling `SESSION_HANDOFF.md` so any agent (or
   human) can resume mid-stream.

Proto Gear already satisfies 1–6 for the generalist engineering module
(supervision gates, item 5, are machine-declared in workflow metadata and
validated by `pg doctor`). Extracting 1–6 into a reusable core — and proving it
against a *second* engineering discipline — is the platform work.

## 4. Supervision Model

"AI supervised" cuts both ways, deliberately:

- **AI-supervised work**: agents run the discipline's workflows, keep state
  current, detect drift, and prepare artifacts (PRs, releases, reports).
- **Human-supervised AI**: every workflow declares its gates. The default
  posture is *agent proposes, human approves* at declared gates; routine
  low-risk steps run autonomously. Gates are data (in capability metadata),
  not prose — so tooling can enforce "this workflow has an unapproved gate"
  the same way `pg doctor` enforces context drift today.

Escalation rule: when a workflow hits an undeclared situation, the agent stops,
records state in SESSION_HANDOFF.md, and asks. Silence is never consent.

### 4.1 Graded authority — the capability-growth axis (ADR-002)

A gate declares three separate concerns (all data, all doctor-validated):

- **`actor`** — who is *accountable* for the guarded work: a discipline agent
  (`qa/qa-release-agent`), a human role, or unassigned. An agent can be the
  actor and the recommender; it is never the clearer.
- **`evidence`** — what *proves* the gate is satisfied: a declarative,
  provably non-executing predicate over a state-surface cell (`non-empty` —
  a sign-off is recorded; `equals` / `at-least` — a recorded fact matches a
  declared claim). A filled cell that fails the claim is pending, not cleared.
- **`authority`** — the *minimum authority required to clear* the gate, on a
  three-rung ladder ordered most → least human involvement:

  | Authority | Meaning |
  |-----------|---------|
  | `human` | A human signer clears (the default — identical to the base posture above). |
  | `human-on-recommendation` | An agent verifies + recommends; a **human ratifies**, recording the residual-risk acceptance. The **ceiling** for any judgment gate. |
  | `auto` | Cleared by the evidence predicate alone — reserved for deterministic, non-judgment facts (tests recorded green, coverage ≥ threshold). |

This is how the supervision model **scales with agent capability**: as a class
of verification becomes safe to delegate, that specific gate's `authority` is
lowered in its metadata — a one-line, reviewable, doctor-audited config change;
no workflow restructuring, no core edits (proven by dogfooding: engineering's
`pr-review-approval` runs at `human-on-recommendation`, PROTO-073). The
through-line is the separation of **verification** (mechanizable,
evidence-predicated, agent-ownable) from **risk acceptance** (retained by a
human at every judgment gate).

Sufficiency is audited, not assumed: `pg trace` / `pg release` check that each
cleared gate was signed by an identity of adequate authority (an agent signs
with its agent id or an `agent:` prefix; an agent-signed human-rung gate is
flagged). There is **no `agent` clearing rung** — an agent recording *itself*
as the clearer of a judgment gate is deferred until a track record justifies
revisiting (ADR-002, PROTO-069 amendment). The escalation rule above is
unchanged by all of this: silence is never consent.

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
6. **Composition over configuration.** New disciplines assemble core primitives;
   they don't fork the core.
7. **UI-first; navigation over command palette.** The human surface is a
   state-of-the-art **interactive CLI UI** — navigate, browse, pick-and-choose,
   modern CLI/TUI UX methodologies. **Every feature must be reachable through the
   UI first.** A dedicated command is a welcome convenience/shortcut, but it is
   never the *only* way in, and the command surface must not outpace the UI.
   "Don't grow a command palette" means *invest in navigation and UI*, not skip
   human UX — the human UX matters, it just lives in the UI, not in flags.
   (Agents are guided through the lifecycle by the harness; humans reach the same
   capabilities by navigating the UI.)

## 6. Roadmap

### Phase A — Harden the Engineering Module (v0.11.x) ✅
- Split the `proto_gear.py` monolith along the module boundaries ARCHITECTURE.md
  documents (CLI dispatch vs. init engine vs. template generation).
- Fix robustness gaps (e.g. optional-dependency import crash).
- Raise coverage on business logic; kill repo hygiene debt.
- Machine-declared supervision gates in workflow metadata (contract item 5).

### Phase B — Extract the Module Core (v0.12.x) ✅
- Factor the department-agnostic engine (capability schema, sync, doctor,
  discovery, state model) into a `module_core` package layer with the
  engineering module (`modules/engineering/`) as its first consumer.
- Module manifest: `module.yaml` declaring a module's state surface, gates,
  and capability roots — the doctor validates it.
- `pg` learns to host >1 module in one project (`pg --module <name> …`).

### Phase C — Second Engineering Discipline Proves the Contract (v0.13+)
- Ship a **second engineering-discipline module** (e.g. QA/Test or DevOps/SRE)
  as the second implementation — a discipline state surface (test-plan / defect
  queue) with its own supervision gates (e.g. sign-off before release).
- Contract v1.0: anything that satisfies the module contract runs on the core
  unmodified. Two independent engineering modules = the pattern is real.
- *(History: a Content/Marketing module was briefly built as the first Phase-C
  falsifier, then removed — content/marketing is out of scope for the
  engineering OS. See Non-Goals.)*

### Phase D — Engineering OS (v1.x)
- Cross-discipline orchestration: engineering ticket ↔ test run ↔ release
  links, an engineering-wide dashboard, per-discipline agents with a shared
  supervision inbox.

## 7. Success Criteria

- **Phase A**: 0 import-time crashes in any dependency configuration; no module
  >1,200 lines; `pg doctor` green including gate checks; coverage on core
  business logic ≥ 70%.
- **Phase B**: engineering module consumes the core through the same interfaces
  a future discipline module would; adding a toy second module requires **zero
  core edits**.
- **Phase C**: a second engineering-discipline module operated by an agent
  end-to-end (task → gate → done) with every gate hit logged.
- **Ongoing**: a fresh agent session reaches correct, current context in ≤1 file
  auto-load + ≤2 reads (the AGENT_CONTEXT promise, held across all modules).

## 8. Non-Goals (unchanged from ARCHITECTURE.md, restated for the platform)

- **Not a whole-business "agency OS."** Scope is the software-engineering circle
  only. Other business functions — content/marketing, sales, finance — are
  explicitly out; they belong to separate products, not proto-gear modules.
- Not a runtime or agent host — modules describe work; hosts execute agents.
- Not a scaffolder for the host project's tech stack.
- Not an LLM client; no model calls inside `pg`.
- Not a replacement for the tools engineers already use (GitHub, CI providers,
  cloud consoles) — modules *wrap* engineering practice, integrations stay thin.

---
*Owner: towb · Drafted 2026-07-07 (PROTO-039) · Reframed 2026-07-10 (PROTO-053: agency OS → software-engineering OS) · Living document — revise at each phase boundary.*
