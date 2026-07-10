# QA Release Sign-off

Verify a release candidate against the QA queue and record the mandatory human
QA sign-off before it ships. This is the QA discipline's supervision gate — the
counterpart to engineering's `release-approval`, and it composes *before* the
engineering `release` workflow's tag-and-deploy step.

## When to use

A release candidate is built and QA must clear it. Triggers: _qa sign-off,
release sign-off, sign off release, qa approval_.

## Supervision gate — `qa-signoff`

**Mandatory and human.** A release candidate may not ship until a human QA owner
confirms every release-targeted `QA_QUEUE.md` item is `verified` and records
their name in the queue's **Signed off by** column. Silence is never consent
(PROJECT_SPECIFICATIONS.md §4).

## Steps

1. List the `QA_QUEUE.md` items targeted at this release.
2. Confirm each is `verified` (no open `failed` items). If any fails, stop and
   hand back to engineering with the linked ticket.
3. **Gate:** the human QA owner reviews the candidate and records their sign-off
   in **Signed off by**. If they decline, record why in `SESSION_HANDOFF.md`.
4. Move the items to `signed-off` and append them to the Sign-off Log with the
   release and date.

## Outputs

- A release candidate cleared for release, with an auditable QA sign-off trail.
