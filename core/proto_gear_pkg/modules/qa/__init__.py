"""QA / Test department module — the second engineering-discipline module.

The Phase-C contract falsifier (ADR-001 / PROJECT_SPECIFICATIONS.md §3, §6): a
brand-new engineering discipline the department-agnostic core discovers, loads,
and audits through the *same* interfaces as engineering — with **zero**
``module_core/`` edits. It encodes test planning, defect triage, and the QA
sign-off gate before a release goes out.

The contract surfaces it manages are declared in ``module.yaml``; its bundled
capabilities live under ``capabilities/``.
"""
