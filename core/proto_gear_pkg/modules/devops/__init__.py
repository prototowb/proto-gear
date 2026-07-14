"""DevOps / SRE department module — the third engineering-discipline module.

A standing contract check (PROJECT_SPECIFICATIONS.md §3, §6): an arbitrary
engineering discipline the department-agnostic core discovers, loads, lists,
installs (`.proto-gear/devops/`), indexes, and gate-audits through the *same*
interfaces as engineering and qa — with **zero** ``module_core/`` edits. It
encodes deployment tracking, incident state, and the production-deploy approval
gate before a change reaches prod.

The contract surfaces it manages are declared in ``module.yaml``; its bundled
capabilities live under ``capabilities/``.
"""
