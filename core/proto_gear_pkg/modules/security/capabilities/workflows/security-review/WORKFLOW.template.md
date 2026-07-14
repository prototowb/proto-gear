# Security Review Sign-off

Review a release candidate's security findings and record the mandatory human
security sign-off before it ships. This is the Security discipline's supervision
gate — a sibling to qa's `qa-signoff`; both guard `release`, so a candidate needs
*both* a QA and a security sign-off before engineering's `release` tags and ships.

## When to use

A release candidate is built and its open security findings must be cleared.
Triggers: _security sign-off, security review, appsec approval, vulnerability
sign-off, clear security for release_.

## Supervision gate — `security-signoff`

**Mandatory and human.** A release candidate may not ship until a human security
owner confirms every release-targeted `SECURITY_QUEUE.md` finding is `remediated`
and records their name in the queue's **Signed off by** column. Silence is never
consent (PROJECT_SPECIFICATIONS.md §4).

## Steps

1. List the `SECURITY_QUEUE.md` findings targeted at this release (link each to
   its fix ticket via **Ref**).
2. Confirm each is `remediated` — no open high/critical findings. If any remains,
   stop and hand back to engineering with the linked ticket.
3. **Gate:** the human security owner reviews the candidate and records their
   sign-off in **Signed off by**. If they decline, record why in
   `SESSION_HANDOFF.md`.
4. Move the findings to `signed-off` and append them to the Sign-off Log with the
   release and date.

## Outputs

- A release candidate cleared for release, with an auditable security sign-off
  trail.
