<!-- proto-gear:header
purpose: Current project state — sprint, tickets, blockers
read-when: Every session before starting work
priority: required
defines:
  - current-state-yaml
  - active-tickets-table
  - completed-tickets-table
  - project-analysis
  - recent-updates
links:
  - AGENTS.md
-->
# PROJECT STATUS - Single Source of Truth

> **For Agents**: This is the ONLY source of project state. All examples and test data should be ignored.
> **For Humans**: Current development status and progress tracking.

> **For Agents**: Use `pg` CLI commands to update this file — works with any AI that can run shell commands:
> - `pg ticket create "title" --type feature` — create a ticket, prints new ID to stdout
> - `pg ticket update TICKET-ID --status IN_PROGRESS` — change ticket status
> - `pg ticket list` — list active tickets
> - `pg status` — summarise current project state (add `--json` for structured output)

## 📚 Related Documentation

This file is part of the Proto Gear documentation system. For complete context, also review:

- **AGENTS.md** - Agent workflows, collaboration patterns, and capability discovery
- **BRANCHING.md** (if exists) - Git workflow, branch naming, commit conventions
- **TESTING.md** (if exists) - TDD methodology, test pyramid, coverage targets
- **.proto-gear/INDEX.md** (if exists) - Available capabilities, skills, and workflows
- **CONTRIBUTING.md** (if exists) - Contribution guidelines and standards
- **SECURITY.md** (if exists) - Security policy and vulnerability reporting
- **ARCHITECTURE.md** (if exists) - System design and architectural decisions
- **CODE_OF_CONDUCT.md** (if exists) - Community guidelines

**Agents**: Always read AGENTS.md first to understand the full workflow and available capabilities.

## 📖 State Management Guide

### Ticket Status Workflow

```
PENDING → IN_PROGRESS → COMPLETED
   ↓           ↓
BLOCKED ←──────┘
   ↓
CANCELLED
```

**Status Definitions:**
- **PENDING**: Ticket created, not started (in backlog)
- **IN_PROGRESS**: Actively being worked on (has branch)
- **COMPLETED**: Work finished, tests passing, merged
- **BLOCKED**: Cannot proceed due to dependency/blocker
- **CANCELLED**: No longer needed or  deprioritized

### Sprint Types → suggested paradigm

The kind of work in flight suggests an **orchestration paradigm** (see
`pg orchestration list`). These are starting points, not mandates — the user or
the overseeing agent picks and switches paradigms on the fly for efficiency.

| Sprint Type | Focus | Suggested paradigm |
|-------------|-------|--------------------|
| **feature_development** | Building new features | `dynamic` (or `core-flex` for a sustained multi-domain sprint) |
| **bug_fixing** | Resolving defects | `driver-reviewer` |
| **performance_optimization** | Speed/efficiency | `driver-reviewer` |
| **deployment_prep** | Release readiness | `pipeline` |
| **refactoring** | Code quality | `fan-out` (mechanical breadth) or `solo` |
| **research_integration** | New tech/libraries | `dynamic` |

### State Update Rules

**Agents should:**
1. **Always read** this file before making decisions
2. **Update immediately** when ticket status changes
3. **Never cache** state - always read fresh
4. **Verify branch exists** for IN_PROGRESS tickets
5. **Check blockers** before starting work

## 📊 Current State

```yaml
project_phase: "{{PHASE}}"  # Planning, Development, Testing, Production
current_sprint: {{SPRINT_NUMBER}}  # null for pre-development
current_branch: "{{CURRENT_BRANCH}}"
last_ticket_id: {{LAST_TICKET_ID}}  # Next ticket will increment from this
ticket_prefix: "{{TICKET_PREFIX}}"  # e.g., "PROJ", "MCP", etc.
```

## 🎫 Active Tickets

> **Ticket Structure**: Each ticket should have a unique ID, clear title, type (feature/bugfix/hotfix), current status, associated branch name, and optional assignee.

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
{{ACTIVE_TICKETS}}

**Example**:
```markdown
| {{TICKET_PREFIX}}-001 | Add user authentication | feature | IN_PROGRESS | feature/{{TICKET_PREFIX}}-001-add-user-auth | Lead AI |
```

## ✅ Completed Tickets

| ID | Title | Completed | PR | Reviewed by |
|----|-------|-----------|-----|-------------|
{{COMPLETED_TICKETS}}

## 🚧 Blocked Tickets

| ID | Title | Blocker | Since |
|----|-------|---------|-------|
{{BLOCKED_TICKETS}}

## 🚀 Releases

<!-- Release-scoped supervision gates (release-approval, announcement-approval)
     are cleared once per release here — `pg release <label>` reads this table,
     keyed by the release label in the ID column. Per-change gates stay in the
     tickets tables above. -->

| ID | Date | Release approved by | Announced by |
|----|------|---------------------|--------------|

## 📈 Feature Progress

| Feature | Status | Progress | Notes |
|---------|--------|----------|-------|
{{FEATURE_PROGRESS}}

## 🔄 Recent Updates
{{RECENT_UPDATES}}

## 🎯 Next Milestones

### Sprint {{NEXT_SPRINT}} Goals
{{SPRINT_GOALS}}

### Upcoming Features
{{UPCOMING_FEATURES}}

## 📊 Metrics

```yaml
velocity: {{VELOCITY}}  # points/sprint
test_coverage: {{COVERAGE}}%
documentation: {{DOC_COVERAGE}}%
tech_debt_ratio: {{TECH_DEBT}}%
```

## 🔍 Sprint Configuration

```yaml
sprint_type: "{{SPRINT_TYPE}}"       # feature_development, bug_fixing, etc.
orchestration_paradigm: "dynamic"    # see `pg orchestration list` — pick/switch on the fly
active_agents: []                    # the minimal set the current work needs (tier per agent)
```

---
*This file is the authoritative source for project state. Updated by Lead AI and Project Lead.*