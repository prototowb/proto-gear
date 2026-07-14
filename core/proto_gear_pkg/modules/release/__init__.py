"""Release Management / PM department module — the fifth engineering-discipline module.

A standing contract check (PROJECT_SPECIFICATIONS.md §3, §6): an arbitrary
engineering discipline the department-agnostic core discovers, lists, installs
(`.proto-gear/release/`), indexes, gate-audits, orchestrates (`pg pipeline`),
and traces (`pg trace` / `pg release`) through the *same* interfaces as
engineering, qa, devops, and security — with **zero** ``module_core/`` edits.
It owns the release queue: one row per candidate keyed by its release label,
the go/no-go decision, and the release-scoped ``go-no-go`` gate — the first
``modules/`` discipline to declare ``scope: release`` (PROTO-066; engineering's
release-level gates live in the shared bundle) — and it ships its own agent
(``agents/release-coordinator-agent.yaml``) via the PROTO-067 seam.

The contract surfaces it manages are declared in ``module.yaml``; its bundled
capabilities live under ``capabilities/``.
"""
