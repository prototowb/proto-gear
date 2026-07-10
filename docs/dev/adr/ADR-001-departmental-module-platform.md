# ADR-001: Evolve Proto Gear into a Departmental Module Platform

**Status:** Proposed
**Date:** 2026-07-07
**Deciders:** towb
**Ticket:** PROTO-040
**Related:** PROJECT_SPECIFICATIONS.md (vision), ARCHITECTURE.md (current state)

## Context

Proto Gear v0.10.0 is a single-purpose CLI: it encodes the *generalist*
engineering practice (tickets, branching, testing, releases) as templates +
capabilities and keeps agent-facing context in sync. The new north star widens
the scope **within software engineering**: proto-gear becomes the **first of
several AI-supervised engineering-discipline modules** (QA/test, DevOps/SRE,
security, docs, …) that together form a **software-engineering operating
system**. Scope is the engineering circle only — not a whole-business "agency
OS" (content/marketing, sales, finance are out).

Forces at play:

- The department-agnostic machinery already exists but is **entangled with the
  engineering module**: `proto_gear.py` (2,476 lines) mixes CLI dispatch, init
  engine, template generation, and engineering-specific state handling.
- The capability schema, `sync_context`, `discovery`, and `doctor` are already
  generic — they operate on `metadata.yaml`, not on engineering concepts.
- The state model (`PROJECT_STATUS.md` tickets via `status_commands` /
  `template_updater`) and the 8 core templates are engineering-specific.
- Supervision gates (human approval points) exist only as prose in BRANCHING.md
  / workflow markdown, not as data — a future module can't declare or audit them.
- Team is one person + AI agents; anything requiring parallel repo maintenance
  or heavy infra is a non-starter.
- Constraint: **dogfooding must never break** — this repo runs on proto-gear
  throughout the migration.

## Decision

Adopt **Option B**: extract a department-agnostic **module core** as a package
layer inside the existing repo, define a **module contract** (`module.yaml` +
required surfaces), and re-home all engineering-specific code as the first
module implementation. One repo, one `pg` CLI, layered packages.

Target package layout (end of Phase B):

```
core/proto_gear_pkg/
├── cli/                  # argparse dispatch only; no business logic
├── module_core/          # department-agnostic engine
│   ├── capabilities/     #   schema, loading, index building (from capability_metadata, capability_index_builder)
│   ├── context/          #   sync_context, discovery
│   ├── diagnostics/      #   doctor + gate checks
│   ├── state/            #   generic state-surface interface
│   └── module_manifest.py#   module.yaml loading/validation
└── modules/
    └── engineering/      # first module: templates, ticket state, wizards
```

Module contract (validated by `pg doctor`): capabilities with triggers, a
declared state surface, an auto-generated context manifest, drift checks,
**machine-declared supervision gates** in workflow metadata, and a session
handoff file.

## Options Considered

### Option A: Stay a single-purpose engineering tool (status quo + cleanup)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Low |
| Cost | Lowest short-term |
| Scalability to new departments | None — each department is a fork or rewrite |
| Team familiarity | High |

**Pros:** No migration risk; all effort goes to engineering features.
**Cons:** The software-engineering-OS vision dies or becomes N divergent forks;
the generic machinery (sync/doctor/discovery) gets reimplemented per discipline;
drift lessons get re-learned N times.

### Option B: Layered module core + modules in one repo (chosen)

| Dimension | Assessment |
|-----------|------------|
| Complexity | Medium — refactor along boundaries ARCHITECTURE.md already documents |
| Cost | Moderate, incremental; each step ships behind green tests |
| Scalability to new departments | Good — new module = new package dir + module.yaml, zero core edits (acceptance test) |
| Team familiarity | High — same repo, same CLI, same test suite |

**Pros:** Preserves dogfooding continuously; the import-boundary rule ("lower
modules never import higher") already points this direction; single release
train; contract enforceable by the existing doctor pattern.
**Cons:** Repo grows; needs discipline to keep `modules/engineering` from
reaching into core internals; `pg` CLI must become module-aware.

### Option C: Split now into separate repos/packages per department (core + N module repos)

| Dimension | Assessment |
|-----------|------------|
| Complexity | High |
| Cost | High — versioned inter-repo dependencies, release coordination |
| Scalability to new departments | Good on paper, but each module repo needs its own CI/release |
| Team familiarity | Low — multi-repo overhead for a team of one |

**Pros:** Hard isolation; independent versioning.
**Cons:** Premature — we have exactly one module today and zero proven
contract; dependency hell before there's anything to depend on; slows the
feedback loop that dogfooding provides.

## Trade-off Analysis

The real choice is **when to pay the abstraction cost**. Option A never pays it
and forfeits the vision. Option C pays it before we know the contract is right
— classic speculative generality. Option B pays incrementally and uses a
second engineering-discipline module (Phase C) as the falsifier: if that module
needs core edits, the contract is wrong and we find out cheaply, in-repo.

Rule of three, adapted: extract with one concrete consumer (the generalist
engineering module) and one designed consumer (a second discipline, e.g.
QA/DevOps), promote to contract v1.0 only when the second consumer runs
unmodified.

## Consequences

**Easier:**
- Adding an engineering discipline becomes composition (`modules/<dept>/` +
  `module.yaml`).
- The proto_gear.py monolith split (already wanted for maintainability) gets a
  principled destination instead of an arbitrary one.
- Supervision gates become auditable data — `pg doctor` can flag workflows with
  missing/unapproved gates, same as context drift today.

**Harder:**
- Every core change must ask "is this generic or engineering-specific?" —
  slight tax on all future work.
- CLI surface grows (`pg --module …`); help/UX needs care to stay simple for
  the single-module case (default module = engineering, zero new flags needed
  until a second module exists).

**Revisit when:**
- Phase C completes → decide whether contract v1.0 justifies separate
  distribution (revisit Option C then, with evidence).
- If gate-as-data proves too rigid for some discipline's workflows, relax to
  gate-as-convention with doctor warnings instead of errors.

## Action Items

1. [ ] PROTO-041: fix optional-dependency import crash (blocks "0 import-time crashes" criterion)
2. [ ] Split `proto_gear.py`: extract CLI dispatch → `cli/`, init/template engine → module boundary prep (Phase A)
3. [ ] Add `gates:` field to workflow `metadata.yaml` schema + doctor check (Phase A)
4. [ ] Design `module.yaml` manifest schema; doctor validates (Phase B)
5. [ ] Move generic engine into `module_core/`, engineering specifics into `modules/engineering/` (Phase B)
6. [ ] Acceptance test: toy second module loads with zero core edits (Phase B exit)
7. [ ] Second engineering-discipline module design doc, e.g. QA/DevOps (Phase C entry). *(A Content/Marketing module was briefly built here as the first falsifier, then removed as out of scope — see PROJECT_SPECIFICATIONS.md §6/§8.)*
