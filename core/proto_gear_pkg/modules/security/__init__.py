"""Security / AppSec department module — the fourth engineering-discipline module.

A standing contract check (PROJECT_SPECIFICATIONS.md §3, §6): an arbitrary
engineering discipline the department-agnostic core discovers, lists, installs
(`.proto-gear/security/`), indexes, gate-audits, orchestrates (`pg pipeline`),
and traces (`pg trace`) through the *same* interfaces as engineering, qa, and
devops — with **zero** ``module_core/`` edits. It encodes vulnerability findings,
remediation tracking, and the security sign-off gate before a release ships.

The contract surfaces it manages are declared in ``module.yaml``; its bundled
capabilities live under ``capabilities/``.
"""
