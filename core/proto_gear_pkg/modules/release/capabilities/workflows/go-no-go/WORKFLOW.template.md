# Release Go/No-Go

Verify a release candidate's cross-discipline readiness and record the human go
decision before it ships. This is the Release-Management discipline's supervision
gate — it guards the same `release` action qa's `qa-signoff` and security's
`security-signoff` do, but at **release scope**: one decision for the whole
candidate, recorded against its label.

## When to use

A candidate's scope is frozen and someone must decide whether it ships.
Triggers: _go no go, go/no-go, release decision, ship it, release readiness
decision_.

## Supervision gate — `go-no-go`

**Mandatory, human, release-scoped.** A candidate may not ship until a human
release owner records their name in the **Signed off by** cell of the
`RELEASE_QUEUE.md` row keyed by the release label. `pg release <label>` verifies
this gate once for the whole candidate — not per ticket. Silence is never
consent (PROJECT_SPECIFICATIONS.md §4).

## Steps

1. Freeze the candidate: confirm the `RELEASE_QUEUE.md` row's **Ref** column
   lists every member ticket, and move the row to `verifying`.
2. Run `pg release <label>`. Every required gate must be cleared — per-ticket
   sign-offs (qa, security, deploy) and the release-scoped approvals. Chase
   each *blocking* gate with its discipline's owner; treat *unverified* gates
   as questions, not passes.
3. **Gate:** the human release owner weighs the readiness report and any
   residual risk, then records the go decision in the row's **Signed off by**
   cell. A no-go is recorded in the Decision Log with the reason, and the row
   returns to `assembling`.
4. On go: move the row to `go`, ship via the release workflow, then mark it
   `shipped` and append the decision to the Decision Log.

## Outputs

- A release candidate with an auditable, label-keyed go decision — visible to
  `pg release <label>` as the cleared `go-no-go` gate.
