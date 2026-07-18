# SESSION_HANDOFF — proto-gear

> **Read this before anything else.** This file captures what's true right now.
> **At session end**: replace the contents entirely — do not append.
> This is a rolling "current state" snapshot, not a log.

## ▶ Start here (next session)

**Phase 3/3 of the interactive-frontier effort: PROTO-100 — frontier-era init
planning.** Design is written and ready to execute: **`docs/dev/adr/ADR-004-frontier-era-init-planning.md`**
(Status: Proposed). The thesis: reframe fresh `pg init` from a **template
configurator** (Quick/Full/Minimal/Custom presets + "which .md files?") into a
**state-elicitation planning intake** — detect-and-default the mechanical
choices, spend the interaction capturing the durable non-derivable facts (what
the project is, its boundaries/invariants, house conventions → specs + seed
lesson), then hand off to the agent. It applies the same Fable-5 migration the
steering arc used (mechanical → durable) to the init *interaction model* itself,
and lives in the UI shell (Setup → Init), built on the PROTO-096 nav framework.

Read ADR-004's **Open questions** first — four decisions the implementing
session makes (how much intent to elicit; seed-a-lesson-or-not; native nav
screens vs. reuse the questionary wizard; replace-vs-fallback the old preset
flow). **Must not** disturb the guided re-init path (PROTO-099) or the
non-interactive `--flags` path.

Ticket **PROTO-100** is registered (PENDING). Branch off `development`, PR back,
merge-on-green.

## Shipped this session — the interactive navigate/pick shell (PROTO-096–099)

Turned the flat `pg` home menu into a real navigate-and-pick app. All four merged
to `development` (PRs #67–#70), full CI matrix green each time.

1. **PROTO-096 (#67) — nav framework.** New `module_core/nav.py`: framework-free
   navigation core (`MenuScreen`/`MenuItem` = leaf action or branch submenu;
   pure `format_breadcrumb`/`build_choices`; `run_menu` drives a breadcrumb
   stack). `cmd_home_menu` rebuilt on it — persistent header, breadcrumbs,
   back-nav. Flat home (Status, Capabilities, Agents, Orchestration, Lessons,
   Tickets, Doctor, Release); Tickets nests into list/create/update; Doctor
   carries a live drift badge; interactive ticket create/update.
2. **PROTO-097 (#68) — Setup actions + `python -m` entry.** Setup sub-screen
   (Init/re-init · Sync context · Install hook). Rows shell out to the real
   subcommand via `_run_pg` (`python -m proto_gear_pkg <cmd>`, inherits stdio so
   the init wizard keeps a TTY). New `__main__.py` makes `python -m
   proto_gear_pkg` a first-class entry point (no PATH dependency).
3. **PROTO-098 (#69) — single-page mode.** `run_menu` gained optional `clear`
   (before each render) + `pause` (after a leaf action); `cmd_home_menu` wires
   them so each screen redraws fresh and action output holds until Enter.
   Navigation never pauses. Both optional/default-None → plain scrolling still
   works. Defensive: clear no-ops on odd terminals, pause swallows
   EOF/interrupt/captured-stdin.
4. **PROTO-099 (#70) — guided init/re-init.** Setup → Init is UI-guided: fresh
   project → `pg init` wizard; already-initialised → install-state pane (files
   present/missing, caps, how many host files a Refresh would rewrite) then
   Refresh (re-sync) / Full re-init / Cancel. Reuses real subcommands; no
   re-implemented init logic. NOTE discovered mid-arc: a guided re-init wizard
   *already existed* (`run_incremental_wizard`, reached via `pg init` on an
   existing install) — PROTO-099 fronts it, doesn't replace it. The pane's
   "Refresh" count is re-sync scope (host mirrors always re-sync due to a
   regenerated timestamp), NOT `pg doctor` drift.

## Current State

- **On `development`, unreleased.** `development` is **ahead of `main`** by the
  whole PROTO-096–099 arc (PRs #67–#70) + their status commits. Last release was
  **v0.21.0** (2026-07-17, the Fable-5 steering arc); next will be **v0.22.0**
  (or a patch) once PROTO-100 lands, cut when you decide. **1140 tests pass**;
  `pg doctor` green; `black --check` clean. CI parity: bare `pytest tests/`.
- **The interactive shell is the UI-first home surface.** Bare `pg` in a TTY →
  `cmd_home_menu` (navigate/pick, single-page). Non-TTY → classic splash
  (scripts/CI unaffected). Extend the shell by adding `MenuItem`s/screens in
  `cli_commands.py`, not new command parsing.
- **Fable-5 steering surface (v0.21.0) is in force:** description-routed
  capabilities (no keyword table), `frontier|verbose` profile tiering, the
  agent-writable `.proto-gear/lessons/` layer, a Working Agreement grounding
  section in the generated context (budgeted, warns >1800 tokens), and an
  enforced branch invariant (`pg guard branch` + `pg hooks install`).
- **The one un-migrated Fable-5 surface is the init *planning* model** — the
  subject of PROTO-100 / ADR-004. Everything else on the markdown surface was
  migrated in the steering arc.
- **Five disciplines** ship on the unmodified core; ADR-002 supervision
  primitives complete. (Unchanged this session.)

## Pending / In Progress

- **PROTO-100 (PENDING)** — frontier-era init planning, per ADR-004. Next
  session's work; nothing in flight (no open branches/PRs).
- Speculative-only: a `standard` middle output profile — build only *if a
  consumer needs it*.

## Conventions In Force

- **UI-first:** every feature reachable via the navigate/pick shell first;
  commands are secondary shortcuts. New surface = nav `MenuItem`/screen.
- **Merge-on-green autonomy:** one PR per thrust; branch → PR → CI → merge-on-green;
  confirm only at genuine forks. `development` is open for small/local commits;
  only `main` is PR-protected.
- **Steering philosophy (Fable-5):** conditions over keyword triggers;
  boundaries over behavioral micro-tuning; durable state (handoff, lessons,
  tickets, gates) over procedural prose; enforce invariants with exit codes, not
  NEVER-lines. Model-specific scaffolding belongs in the `verbose` profile.
- **Scope discipline:** engineering-only. New discipline = zero core edits.
- **Layering:** `cli/` → `module_core/` (generic) → `modules/<dept>/`. Lower
  never imports higher. The nav framework lives in `module_core/nav.py` (generic).
- **Testing:** pure helpers unit-tested; interactive shells driven by a scripted
  fake `questionary` (see `test_nav.py`, `test_home_menu.py`). Verify CI parity
  with bare `pytest tests/`.
