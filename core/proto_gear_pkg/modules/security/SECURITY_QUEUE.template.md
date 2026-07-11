<!-- proto-gear | purpose: Security state surface — findings & remediations moving to sign-off | read-when: triaging a vuln or before a release | priority: required -->

# SECURITY_QUEUE — Findings & Remediations

> **Single source of truth** for Security/AppSec state (the security module's
> state surface, the counterpart to engineering's `PROJECT_STATUS.md`). One row
> per finding. Nothing reaches **signed-off** without a human security sign-off —
> see the `security-signoff` gate in `workflows/security-review`.

## Stages

`reported → triaged → in-remediation → remediated → signed-off`

- **reported** — a finding is logged (scan, pentest, disclosure), not yet triaged.
- **triaged** — severity assessed and owned; a fix ticket is linked (**Ref**).
- **in-remediation** — a fix is in progress.
- **remediated** — the fix has landed; awaiting security sign-off.
- **signed-off** — a human security owner has cleared it for release (gate).

## Findings Queue

| ID | Ref | Finding | Severity | Stage | Owner | Signed off by | Target |
|----|-----|---------|----------|-------|-------|---------------|--------|
| (example) SEC-001 | PROTO-054 | Reflected XSS on login | high | remediated | dana | _(pending gate)_ | v0.11 |

> The **Ref** column links a finding to the engineering ticket that fixes it (the
> cross-discipline correlation key — see `pg trace <ticket>`). The **Signed off
> by** column records the `security-signoff` gate approval.

## Sign-off Log

Append an item here when it clears the `security-signoff` gate, with the approver
and the release it was signed off for.

| ID | Finding | Signed off by | Release | Date |
|----|---------|---------------|---------|------|
