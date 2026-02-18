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

### Sprint Types

Your project may be in different sprint types that affect agent focus:

| Sprint Type | Focus | Flex Agents Suggested |
|-------------|-------|----------------------|
| **feature_development** | Building new features | UI/UX, Integration |
| **bug_fixing** | Resolving defects | Testing, Debug |
| **performance_optimization** | Speed/efficiency | Performance, Profiling |
| **deployment_prep** | Release readiness | DevOps, Documentation |
| **refactoring** | Code quality | Architecture, Testing |
| **research_integration** | New tech/libraries | Research, Prototyping |

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

| ID | Title | Completed | PR |
|----|-------|-----------|-----|
{{COMPLETED_TICKETS}}

## 🚧 Blocked Tickets

| ID | Title | Blocker | Since |
|----|-------|---------|-------|
{{BLOCKED_TICKETS}}

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
sprint_type: "{{SPRINT_TYPE}}"  # feature_development, bug_fixing, etc.
active_agents:
  core:
    {{CORE_AGENTS}}
  flex:
    {{FLEX_AGENTS}}
```

---
*This file is the authoritative source for project state. Updated by Lead AI and Project Lead.*