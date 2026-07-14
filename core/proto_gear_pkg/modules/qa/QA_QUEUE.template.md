<!-- proto-gear | purpose: QA state surface — test plans & defects moving to release sign-off | read-when: managing QA work or before a release | priority: required -->

# QA_QUEUE — Test Plans & Defects

> **Single source of truth** for QA state (the QA module's state surface, the
> counterpart to engineering's `PROJECT_STATUS.md`). One row per test plan or
> defect. Nothing reaches **signed-off** without a human QA sign-off — see the
> `qa-signoff` gate in `workflows/release-signoff`.

## Stages

`planned → in-test → failed → verified → signed-off`

- **planned** — scoped, not yet executed.
- **in-test** — actively being exercised.
- **failed** — a defect is open; back to engineering (link the ticket).
- **verified** — passed; awaiting release sign-off.
- **signed-off** — a human QA owner has approved it for release (gate).

## Queue

| ID | Ref | Title | Area | Stage | Owner | Signed off by | Target |
|----|-----|-------|------|-------|-------|---------------|--------|
| (example) QA-001 | PROTO-054 | Login regression sweep | auth | verified | ann | _(pending gate)_ | 2026-07-15 |

> The **Ref** column links this item to the engineering ticket it validates (the
> cross-discipline correlation key — see `pg trace <ticket>`). Leave blank for
> QA work with no originating ticket.

## Sign-off Log

Append an item here when it clears the `qa-signoff` gate, with the approver and
the release it was signed off for.

| ID | Title | Signed off by | Release | Date |
|----|-------|---------------|---------|------|
