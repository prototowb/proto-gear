# Content Module — Design (Phase C Entry)

> **Status**: Design + manifest scaffold (PROTO-047). This is the ADR-001
> action-item-7 design doc and the entry point for Phase C
> (PROJECT_SPECIFICATIONS.md §6). It ships the Content module as a **pure
> manifest + templates + design** to falsify the module contract; the
> end-to-end agent operation (draft → gate → publish) is Phase C's *success
> criterion*, tracked separately.
>
> **Owner**: towb · **Ticket**: PROTO-047 · **Supersedes**: nothing · **Links**:
> [PROJECT_SPECIFICATIONS.md](../../PROJECT_SPECIFICATIONS.md) §3/§6,
> [ADR-001](adr/ADR-001-departmental-module-platform.md).

## 1. Why a second module now

Phase B extracted a department-agnostic `module_core/` with the engineering
module as its only consumer. A single consumer can't prove the boundary is real
— the core could be quietly engineering-shaped and no test would catch it. The
Content module is the **falsifier**: a department whose only artifact is a
`module.yaml` + templates must be discovered, loaded, and audited through the
exact same interfaces as engineering, with **zero edits to `module_core/`**
(Phase B exit criterion / Phase C entry).

Content was chosen (over ops/finance) because the agency already runs content
tooling that a later phase can integrate, and because its workflow (draft →
review → schedule → publish) has a *natural, non-engineering* supervision gate
— approval before anything goes public — which stresses the gate-as-data model
against a genuinely different shape than "PR review before merge".

## 2. Contract mapping

How the Content module satisfies each of the six contract surfaces
(PROJECT_SPECIFICATIONS.md §3). Delivered = present in this ticket.

| # | Contract item | Content module | Delivered |
|---|---------------|----------------|-----------|
| 1 | Capabilities | draft / review / schedule / publish (see §4) | Design only — see seam S1 |
| 2 | State surface | `CONTENT_QUEUE.md` (draft→review→scheduled→published) | ✅ template |
| 3 | Context manifest | `AGENT_CONTEXT.md` (shared pattern) | ✅ (core-provided) |
| 4 | Drift detection | `pg doctor` `check_modules` validates the manifest | ✅ (core-provided) |
| 5 | Supervision points | `content-approval` gate before publish (see §5) | Design only — see seam S1 |
| 6 | Handoff protocol | `SESSION_HANDOFF.md` (shared pattern) | ✅ (core-provided) |

Items 2/3/4/6 work **today, unmodified** — the manifest declares the surfaces
and the core validates them. That is the zero-core-edit proof. Items 1 and 5
are designed here but not yet *bundled*, because bundling them exposes a real
core seam (§6) that belongs to PROTO-048, not to this proof.

## 3. State surface — `CONTENT_QUEUE.md`

The content analogue of engineering's `PROJECT_STATUS.md`. One file, one truth.
Template: `core/proto_gear_pkg/modules/content/CONTENT_QUEUE.template.md`.

- **Pipeline**: `draft → review → scheduled → published`, strictly ordered; an
  item never skips a stage.
- **Queue table**: `ID · Title · Channel · Stage · Owner · Approved by · Target
  date`. The `Approved by` column is the machine-checkable record of the gate.
- **Published log**: append-only record of what shipped, by whom, with the
  permalink — the audit trail Phase C's success criterion ("every gate hit
  logged") reads from.

## 4. Capabilities (designed; bundled in PROTO-048)

Mirrors engineering's skill/workflow/command split, content-flavoured:

| Capability | Type | Triggers (prose → capability) |
|------------|------|-------------------------------|
| `draft` | workflow | draft, write post, new content, outline |
| `review` | workflow | review content, edit, proofread, brand check |
| `schedule` | command | schedule, queue post, set publish date |
| `publish` | workflow | publish, go live, ship post, release content |

`publish` produces a "publish" output — which the existing
`doctor.check_supervision_gates` already treats as a risk output requiring a
declared gate (its `_RISK_OUTPUT_TOKENS` includes `"publish"`). So the gate
model is *already* department-agnostic at the token level; only the capability
*location* is not (§6, S1).

## 5. Supervision gate — `content-approval`

One gate, declared as data the same way engineering declares "PR review":

```yaml
# (target shape once content capabilities are bundled — PROTO-048)
gates:
  - id: content-approval
    description: >-
      A human editor approves copy, brand fit, and legal before an item leaves
      review. Nothing reaches `scheduled`/`published` without a name recorded
      in the queue's "Approved by" column.
    before: schedule
```

This is the non-engineering gate that proves the model generalises: not a merge
gate, but a *publish* gate, keyed on a different risk output, recorded in a
different state surface — yet expressed in the identical `gates:` schema.

## 6. Seams this module surfaces (the falsifier's payoff)

The open question from the handoff: *does the second module expose a missing
seam in `module_core`?* **Yes — two, and finding them is the point.** Neither is
fixed here, because fixing them would be a core edit and would defeat the
zero-core-edit proof this ticket exists to make. They are the concrete backlog
for PROTO-048.

- **S1 — capabilities are single-rooted, not per-module.**
  `doctor.check_supervision_gates` and `capability_metadata.load_all_capabilities`
  read from one shared `package_root()/capabilities` directory. A module cannot
  yet ship its own capabilities under `modules/<name>/capabilities/` and have
  them discovered/gated. The manifest *declares* `capabilities_root`, but the
  loaders ignore it. → **PROTO-048**: make capability + gate loading manifest-
  driven (honour `capabilities_root` per module).

- **S2 — no per-module init / template rendering seam.**
  `pg init` and the template engine live under `modules/engineering/`
  (`interactive_wizard`, `detection`, `templates`). There is no generic "render
  *this* module's state-surface template into a host project" path, so
  `pg --module content init` can't yet lay down `CONTENT_QUEUE.md`. The
  engineering engine is correctly *not* in the core, but the core also offers no
  neutral rendering seam a module can plug into. → **PROTO-048** multi-module
  hosting (`pg --module <name> <cmd>`).

Both seams are consistent with the contract *as specified* — the manifest surface
is honoured; it's the *capability plumbing* that's still engineering-routed. That
is exactly the discovery Phase C is meant to produce before v0.13 declares
contract v1.0.

## 7. Scope: this ticket vs. Phase C completion

**PROTO-047 (this ticket) delivers**: the `content` manifest, the
`CONTENT_QUEUE.md` state-surface template, this design doc, and an acceptance
test proving the bundled content module is discovered + validated by the core
with zero `module_core/` edits (alongside engineering).

**Deferred** (Phase C success criterion, not entry): bundling the four
capabilities under a manifest-driven `capabilities_root` (needs S1),
`pg --module content` hosting (needs S2), and an agent operating a real item
draft → gate → publish with every gate hit logged.

---
*Living document — revise when S1/S2 land in PROTO-048.*
