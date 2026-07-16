<!-- proto-gear:agent-context begin -->
<!-- proto-gear | role: agent-context | regenerate: pg sync-context -->

# Agent Context — proto-gear

> Auto-generated index every agent should read on session start.
> Regenerate with `pg sync-context`. **Do not hand-edit** between the BEGIN/END markers — your changes will be overwritten.

## 📋 Reference Index

| File | Purpose | Read When |
|------|---------|-----------|
| `AGENTS.md` | Agent orchestration, roles, pre-flight checklist | First session or unclear on process |
| `SESSION_HANDOFF.md` | Rolling session handoff — what just shipped, what's pending | Start of every session — before anything else |
| `PROJECT_STATUS.md` | Current sprint, active tickets, project state | Every session before starting work |
| `PROJECT_SPECIFICATIONS.md` | Project planning doc — source for architecture | Starting features or design work (if exists) |
| `PROJECT_ARCHITECTURE.md` *(not present)* | Project-specific architecture (agent-extracted) | Design decisions (if exists) |
| `BRANCHING.md` | Git workflow, branch naming, commit format | Before any git operations |
| `TESTING.md` | TDD patterns, test pyramid, coverage targets | When writing tests |
| `.proto-gear/INDEX.md` | Capability catalog (full reference) | When the skim below is insufficient |

## 🛠 Available Capabilities

Load a capability when its description fits the task in front of you — route by
judgment, not keyword match. Each is optional; skip any that doesn't earn its place.

### **Skills** — apply to any task

- `skills/code-review` — Systematic code review methodology for maintaining code quality and knowledge sharing
- `skills/debugging` — Systematic debugging methodology for identifying and fixing software issues
- `skills/documentation` — Writing clear, maintainable technical documentation for code and projects
- `skills/performance` — Systematic performance optimization and profiling techniques
- `skills/refactoring` — Systematic code refactoring techniques for improving code quality without changing behavior
- `skills/security` — Security best practices and vulnerability prevention techniques
- `skills/testing` — TDD methodology with red-green-refactor cycle for quality code

### **Workflows** — multi-step processes

- `workflows/bug-fix` — Systematic workflow for investigating and fixing software defects
- `workflows/cicd-setup` — Setting up continuous integration and deployment pipelines
- `workflows/code-review-process` — Complete PR creation, review, approval, and merge workflow
- `workflows/complete-release` — End-to-end release workflow combining all release phases
- `workflows/dependency-update` — Systematic workflow for updating project dependencies safely
- `workflows/documentation-update` — Systematic workflow for maintaining and updating project documentation
- `workflows/feature-development` — Complete workflow for developing new features from planning to deployment
- `workflows/finalize-release` — Final steps for completing and announcing a release
- `workflows/hotfix` — Emergency workflow for critical production issues requiring immediate fixes
- `workflows/incident-response` — Production issue handling from detection through resolution and post-mortem
- `workflows/migration` — Breaking change and data migration workflow with rollback planning
- `workflows/monitoring-setup` — Setting up monitoring, logging, and alerting for production systems
- `workflows/release` — Complete release process from preparation to deployment

### **Commands** — slash-command-style actions

- `commands/analyze-coverage` — Run and analyze test coverage for the project
- `commands/create-ticket` — Create and properly document a ticket in PROJECT_STATUS.md
- `commands/generate-changelog` — Generate or update CHANGELOG.md from git history
- `commands/update-status` — Update ticket status in PROJECT_STATUS.md

## 🚨 Critical Rules

- NEVER commit directly to `main` — it lands only via a reviewed PR
- `development` is open: commit to it directly when it helps; feature branch + PR is still the norm for substantial or shared work, not a requirement
- Run `pg status` before starting work to see active tickets and current sprint
- Use `pg ticket create "title" --type feature` to register new work
- Use `pg ticket update ID --status IN_PROGRESS` when starting a ticket

## 🤖 CLI Commands

- `pg status` — Version, sprint, active tickets
- `pg context [--regenerate]` — Print this Agent Context to stdout
- `pg suggest "<task prose>" [--json]` — Match task prose to capabilities
- `pg ticket create/update/list` — Manage tickets in PROJECT_STATUS.md
- `pg capabilities list [--type ...] [--json]` — List capabilities (--json for agents)
- `pg capabilities show <name>` — Show a capability's details
- `pg capabilities tree <name>` — Show a capability's dependency tree
- `pg agent list [--available]` — List configured + installable agents
- `pg agent install <name>` — Install a bundled agent
- `pg orchestration list [--json]` — Browse orchestration paradigms
- `pg orchestration show <id>` — Show a paradigm's roles + model tiers
- `pg module list/show [<name>]` — List/inspect department modules
- `pg --module <name> init-surface` — Render a module's state surface
- `pg pipeline [--json]` — Show the supervision pipeline to production
- `pg trace <ticket-id> [--json]` — Trace a ticket across disciplines to production
- `pg release <label> [--json]` — Aggregate a release's readiness verdict
- `pg sync-context` — Regenerate Agent Context + host files
- `pg sync-indexes` — Regenerate capability INDEX.md files
- `pg doctor [--fix] [--json]` — Audit for sync drift (--fix repairs)
- `pg help` — Full CLI help

## 🌐 Project

- **Project**: proto-gear
- **Tech / type**: Python
- **Proto Gear version**: v0.20.0
- **Last release**: 2026-07-14
- **Capabilities installed**: 7 skills, 13 workflows, 4 commands
- **Generated**: 2026-07-16 18:02

<!-- proto-gear:agent-context end -->

---

# CLAUDE.md — Claude Code Host Config

This file is what Claude Code auto-loads. **AGENTS.md is the canonical entry point** for any agent working in this repository. Everything below the managed block above only points back to canonical sources — do not add project guidance, conventions, or architecture content here. It will drift.

## Where to find things

| Topic                       | Read                                              |
|-----------------------------|---------------------------------------------------|
| 🤖 Auto-loaded quick index  | AGENT_CONTEXT.md (mirrored in the block above)    |
| Agent orchestration (full)  | AGENTS.md                                         |
| Project state, tickets      | PROJECT_STATUS.md                                 |
| Architecture, modules       | ARCHITECTURE.md                                   |
| Dev setup, branches, PRs    | CONTRIBUTING.md                                   |
| Git workflow full spec      | BRANCHING.md + docs/dev/branching-strategy.md     |
| Test patterns               | TESTING.md                                        |
| 🚨 Release procedure        | docs/dev/release-workflow.md                      |
| Readiness assessment        | docs/dev/readiness-assessment.md                  |

Run `pg context` to print the agent index. Run `pg doctor` to check drift. Run `pg sync-context` (or `pg doctor --fix`) to repair.
