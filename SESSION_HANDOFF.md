# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**Phase C is proven. The QA/Test module (PROTO-054) shipped as the second
engineering-discipline module with ZERO `module_core/` edits — the module
contract is real (contract v1.0). It's in review as PR #16. Scope reminder:
proto-gear is engineering-only; "departments" = engineering disciplines.**

1. **Merge PR #16** (`feature/PROTO-054-qa-module` → `development`), then
   `git checkout development && git pull`. It only adds `modules/qa/` + a test
   (+ PROJECT_STATUS) — no core edits, so no conflict risk.
2. **Then pick the next thrust** (unticketed; file with `pg ticket create`):
   - **S1 listing half** — route the host-side capability surfaces
     (`discovery`/`pg suggest`, `sync_context`/AGENT_CONTEXT, `agent_config`,
     wizard) through `module_host.iter_capability_sources()` so a discipline's
     own capabilities surface in suggestions/context, not just the gate audit.
     Now that qa ships a real capability (`release-signoff`), this has a live
     consumer. Resolve the open question below first.
   - **A third discipline (DevOps/SRE)** — deploy/incident queue + a
     `prod-approval` gate; more contract exercise, still zero core edits.
   - **Phase D (Engineering OS)** — cross-discipline orchestration (engineering
     ticket ↔ qa sign-off ↔ release). Bigger; only after S1 listing lands.
3. **Tiny cleanup** (noticed, deliberately not done to keep #16 a clean
   zero-core-edit proof): `module_core/module_manifest.py` docstring line 3 still
   says "(engineering, content, ops, …)" — a leftover PROTO-053 scrub miss.
   Fold into the next core-touching PR.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `b88f6b3` (PROTO-047–053). **PR #16 open** for PROTO-054 (qa).
- On the PR branch: **750 tests green; `pg doctor` 0/0/25 ok; `black --check`
  clean.** `pg module list` shows **engineering + qa**. Coverage measurable via
  `pytest --cov=core/proto_gear_pkg --cov-report=term-missing`.
- **Contract proven (v1.0):** two independent engineering-discipline modules
  (`engineering`, `qa`) run on the department-agnostic core unmodified. Adding
  `qa` was dropping `modules/qa/` in — the core discovered, validated, and
  gate-audited it (doctor 23→25) with no code change. This is the ADR-001
  Phase C exit criterion, met.
- **Scope (PROTO-053):** proto-gear = software-engineering OS; departments are
  engineering disciplines (dev, qa, devops, security, docs, release/PM). No
  content/marketing — that's honk (`../_Plugins/honk/`), a separate product.

## Shipped this cycle (all merged unless noted)

- **PROTO-050** — core coverage 45%→70% + pytest config fix. PR #14.
- **PROTO-053** — engineering-only reframe: remove content module, rescope vision
  agency→software-engineering OS. PR #15.
- **PROTO-054** — QA/Test module (Phase C falsifier), zero core edits, contract
  v1.0. **PR #16 open.**

## Pending / In Progress

- **PR #16 awaiting merge.**
- **S1 listing half** (now has a live consumer: qa's `release-signoff`) — step 2.
- **3rd discipline (DevOps)** / **Phase D** — later (step 2).
- **Formatting enforced via git hook, not CI.** `dev/hooks/pre-commit` blocks
  commits failing `black --check` / flake8. Enable per clone:
  `git config core.hooksPath dev/hooks` (already set here). Fix: `black core/
  tests/`.

## Conventions In Force

- **Scope discipline:** proto-gear is engineering-only. "Departments" = engineering
  disciplines. Anything content/marketing/sales/finance is out of scope by design
  (PROJECT_SPECIFICATIONS.md §8). Flag such requests rather than build them.
- **New discipline = zero core edits.** Drop a `modules/<name>/` dir (manifest +
  optional `capabilities/` + state-surface template). If it needs a `module_core/`
  or `cli/` change, the contract abstraction is wrong — stop and reconsider.
  `modules/qa/` is the reference pattern; `modules/engineering/` is the generalist.
- **Layering:** `cli/` (top) → `module_core/` (generic) → `modules/<dept>/`
  (discipline). Lower never imports higher.
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Supervision gates** are data in workflow `metadata.yaml` (`gates:`);
  `pg doctor` enforces structure + coverage across the shared root AND every
  module's own `capabilities/` (targets namespaced `<module>/<cap_id>`).
- **Testing:** business logic via argparse.Namespace + capsys + tmp dirs;
  interactive questionary wizards out of scope. Real bundled modules get an
  acceptance test (`test_qa_module.py` is the template); synthetic platform
  tests use a neutral `qa` toy or engineering.
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs only on PRs targeting `main`/`development`.
- **Regen noise:** `AGENT_CONTEXT.md` / host configs carry a `Generated:`
  timestamp `pg` rewrites on any run — `git restore` them if the diff is
  timestamp-only.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

## Open Questions (for the S1 listing half)

- When host-side listings become multi-source, does the host's single
  `.proto-gear/` stay the shared `capabilities_root` for all modules, or does
  each discipline namespace its own subtree (e.g. `.proto-gear/qa/`)? Both
  manifests declare `.proto-gear`. Decide before wiring the listing surfaces — it
  governs whether two disciplines' capability IDs can collide in `pg suggest` /
  AGENT_CONTEXT. (The gate audit already namespaces as `<module>/<cap_id>`; the
  listing surfaces should follow the same convention.)

---
*Agent-maintained. Replace entirely at session end.*
