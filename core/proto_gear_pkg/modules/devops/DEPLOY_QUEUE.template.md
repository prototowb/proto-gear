<!-- proto-gear | purpose: DevOps state surface — deployments & incidents moving to production | read-when: shipping a deploy or handling an incident | priority: required -->

# DEPLOY_QUEUE — Deployments & Incidents

> **Single source of truth** for DevOps/SRE state (the DevOps module's state
> surface, the counterpart to engineering's `PROJECT_STATUS.md`). One row per
> deployment or incident. Nothing reaches **deployed** without a human
> production-deploy approval — see the `prod-approval` gate in
> `workflows/deploy`.

## Stages

`queued → staged → approved → deployed → verified` · incidents: `open → mitigated → resolved`

- **queued** — change is ready, not yet promoted.
- **staged** — deployed to a pre-prod environment, under validation.
- **approved** — a human has approved the production deploy (gate).
- **deployed** — live in production.
- **verified** — post-deploy checks/SLOs green.
- **incidents** — `open → mitigated → resolved`; link the deploy that triggered it.

## Deploy Queue

| ID | Change | Environment | Stage | Owner | Approved by | Target |
|----|--------|-------------|-------|-------|-------------|--------|
| (example) DEP-001 | Ship auth service v2 | prod | staged | sam | _(pending gate)_ | 2026-07-15 |

## Incident Log

| ID | Summary | Severity | Stage | Linked deploy | Owner | Date |
|----|---------|----------|-------|---------------|-------|------|
| (example) INC-001 | Elevated 5xx after v2 | SEV2 | resolved | DEP-001 | sam | 2026-07-15 |

## Approval Log

Append an item here when it clears the `prod-approval` gate, with the approver
and the environment it was approved for.

| ID | Change | Approved by | Environment | Date |
|----|--------|-------------|-------------|------|
