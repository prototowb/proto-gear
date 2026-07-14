<!-- proto-gear | purpose: Release-management state surface — candidates moving to go/no-go | read-when: planning or shipping a release | priority: required -->

# RELEASE_QUEUE — Release Candidates & Go/No-Go

> **Single source of truth** for Release-Management state (the release module's
> state surface, the counterpart to engineering's `PROJECT_STATUS.md`). One row
> per release candidate, **keyed by its release label** (`v0.12`, `2026-07-r1`,
> …) in the **ID** column — the same label `pg release <label>` traces. Nothing
> ships without a human go decision — see the `go-no-go` gate in
> `release/workflows/go-no-go`.

## Stages

`planned → assembling → verifying → go → shipped`

- **planned** — the candidate has a label and a target window; scope is open.
- **assembling** — tickets are landing; scope is converging (**Ref** lists them).
- **verifying** — scope frozen; downstream sign-offs (qa, security, deploy)
  are being collected — watch `pg release <label>`.
- **go** — a human release owner has recorded the go decision (gate).
- **shipped** — the candidate is released; follow-ups tracked as new tickets.

## Release Queue

| ID | Ref | Stage | Owner | Window | Signed off by |
|----|-----|-------|-------|--------|---------------|
| (example) v0.12 | PROTO-054, PROTO-055 | verifying | rex | 2026-07-15 | _(pending gate)_ |

> The **ID** column carries the release label itself, so the `go-no-go` gate is
> **release-scoped**: `pg release <label>` evidences it once for the whole
> candidate, against this row's **Signed off by** cell. The **Ref** column lists
> the member tickets (the cross-discipline correlation key — `pg trace <ticket>`
> shows the candidate a change rides in).

## Decision Log

Append a row when a candidate clears (or fails) the `go-no-go` gate — the
auditable trail of who decided, and why a no-go was called.

| ID | Decision | Signed off by | Date | Notes |
|----|----------|---------------|------|-------|
