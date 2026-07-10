# Production Deploy

Promote a validated change to production behind a mandatory human approval gate,
then verify and record it. This is the DevOps discipline's supervision gate — the
counterpart to qa's `qa-signoff`, and it composes *after* qa's release sign-off
and engineering's `release`.

## When to use

A change is staged and validated in pre-prod and must be promoted to production.
Triggers: _deploy to production, production deploy, promote to prod, ship to prod,
prod approval_.

## Supervision gate — `prod-approval`

**Mandatory and human.** A change may not reach production until a human owner
approves the promotion and records their name in `DEPLOY_QUEUE.md`'s **Approved
by** column. Silence is never consent (PROJECT_SPECIFICATIONS.md §4).

## Steps

1. Confirm the `DEPLOY_QUEUE.md` item is `staged` and its pre-prod validation is
   green (and, where applicable, qa's `release-signoff` has cleared).
2. Review the change set, rollout plan, and rollback path.
3. **Gate:** the human owner approves the production deploy and records their
   approval in **Approved by**. If they decline, record why in `SESSION_HANDOFF.md`.
4. Deploy to production; move the item to `deployed`.
5. Verify post-deploy checks/SLOs; move to `verified` and append to the Approval
   Log. If checks fail, open an incident and follow `workflows/incident-response`.

## Outputs

- A change live in production with an auditable production-deploy approval trail.
