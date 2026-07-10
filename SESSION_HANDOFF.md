# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**Seam S1 is fully landed: a discipline's own capabilities now surface everywhere,
namespaced `<module>/<cap_id>` — in the listings, on disk under
`.proto-gear/<module>/`, and to the agent subsystem. CI is genuinely green for the
first time (pytest actually runs in CI now).** qa is the live proof
(`qa/workflows/release-signoff`).

1. **Merge PR #19 is DONE.** **PR #58 (PROTO-058, agent multi-source) is open** —
   merge on green, then `git checkout development && git pull`.
2. **Then pick the next thrust** (unticketed; file with `pg ticket create`):
   - **A 3rd discipline (DevOps/SRE)** — `modules/devops/` (deploy/incident queue +
     a `prod-approval` gate). Now the highest-value validation: it exercises the
     *complete* S1 machinery end-to-end (discovery → listings → on-disk subtree
     install → per-module INDEX → gate audit → agents) and must need **zero core
     edits**. `modules/qa/` is the reference pattern.
   - **Agent subsystem, deeper** — PROTO-058 made `AgentManager` *read* module caps;
     `AgentManager`/`agent_config`/`agent_wizard` are otherwise unchanged. If agents
     should *install into* module subtrees too, that's a follow-up.
   - **Phase D (Engineering OS)** — cross-discipline orchestration (engineering
     ticket ↔ qa sign-off ↔ release). Bigger; the S1 plumbing it needs now exists.

Branch off `development`, PR back. Run `pg status` / `pg ticket list` first.

## Current State

- `development` = `010eb88` (through PROTO-057, PR #19). **PR #58 open** (PROTO-058).
- **CI is green and deterministic.** `Tests` workflow now has a dedicated `lint`
  job (single ubuntu/py3.12, **`black==26.5.1` pinned**) + a pytest-only matrix.
  Before PROTO-055 the matrix `black --check` ran *before* pytest and always
  failed, so **pytest never actually executed in CI** — "green locally" hid real
  breakage. Reproduce CI parity locally with the **bare console script**
  `pytest tests/` (not `python -m pytest`, which puts cwd on `sys.path`).
- **767 tests pass; `pg doctor` 0/0/25 ok; `black --check` clean.**
- **Seam S1 complete (listings + on-disk + agents):**
  - Bundled loader: `module_host.load_bundled_capabilities()` /
    `merge_capability_sources()` — shared caps bare, module caps `<module>/<cap_id>`.
  - Listings: `pg suggest` (discovery), `pg capabilities list/search/show/tree`
    (with `_resolve_capability` accepting full id / `<type>/<name>` / unambiguous
    bare name). `pg capabilities list` is 24→25 (qa's release-signoff shows).
  - On-disk: `module_host.install_module_capabilities()` copies each
    `modules/<name>/capabilities/` → `.proto-gear/<name>/` (hardened; wired into
    `pg init` via `copy_capability_templates`).
  - INDEX: `sync_capability_indexes` partitions by module — shared root index is
    shared-only, each subtree gets its own INDEX (scaffolded on demand). `pg doctor`
    covers subtree index drift (`would_create` → ok).
  - Agents: `AgentManager._load_capabilities()` overlays module caps (namespaced).
- **Scope (PROTO-053):** proto-gear = software-engineering OS; departments are
  engineering disciplines (dev, qa, devops, security, docs, release/PM). No
  content/marketing — that's honk (`../_Plugins/honk/`), a separate product.

## Shipped this cycle (all merged unless noted)

- **PROTO-054** — QA/Test module (Phase C falsifier), zero core edits. PR #16.
- **PROTO-055** — CI green: pinned single lint job; fixed a latent test-import bug
  (4 modules imported `core.*`, only resolvable under `python -m pytest`); PROTO-053
  docstring scrubs. PR #17.
- **PROTO-056** — S1 listings multi-source, per-module namespaced. PR #18.
- **PROTO-057** — S1 on-disk per-module subtrees + per-module INDEX. PR #19.
- **PROTO-058** — S1 follow-up: agent subsystem reads module caps. **PR #58 open.**

## Pending / In Progress

- **PR #58 awaiting merge** (PROTO-058).
- **3rd discipline (DevOps)** / **Phase D** — next thrust (step 2).

## Conventions In Force

- **Scope discipline:** engineering-only. Anything content/marketing/sales/finance
  is out of scope by design (PROJECT_SPECIFICATIONS.md §8). Flag, don't build.
- **New discipline = zero core edits.** Drop `modules/<name>/` (manifest +
  optional `capabilities/` + state-surface template). It is auto-discovered,
  listed, installed into `.proto-gear/<name>/`, indexed, gate-audited, and
  agent-visible with no `module_core/`/`cli/` change. If it needs one, the
  abstraction is wrong — stop. `modules/qa/` is the reference.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower never
  imports higher. Module-generic behavior lives in `module_core` (e.g.
  `module_host.install_module_capabilities`), never in `modules/engineering/`.
- **Namespacing:** shared/engineering caps keep bare ids; a module's own caps are
  `<module>/<cap_id>` everywhere (gate audit, listings, on-disk subtree, agents).
- **Bundled resources:** resolve via `paths.package_root()`, never
  `Path(__file__).parent` arithmetic.
- **Testing:** business logic via argparse.Namespace + capsys + tmp dirs;
  interactive questionary wizards out of scope. Real bundled modules get an
  acceptance test (`test_qa_module.py` is the template). **Verify CI parity with
  bare `pytest tests/`.**
- **Git:** never commit to `main`/`development` directly; branch from
  `development`, PR back. CI runs on PRs to `main`/`development`. **Formatting is a
  hard CI gate now (pinned black) AND a pre-commit hook** (`git config
  core.hooksPath dev/hooks`). Fix: `black core/ tests/`.
- **Regen noise:** `AGENT_CONTEXT.md` / host configs carry a `Generated:` timestamp
  `pg` rewrites on any run — `git restore` them if the diff is timestamp-only.
- SESSION_HANDOFF.md is agent-owned; replace entirely at session end.

---
*Agent-maintained. Replace entirely at session end.*
