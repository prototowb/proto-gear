---
name: "Create Ticket"
type: "command"
version: "1.0.0"
description: "Create and properly document a ticket in PROJECT_STATUS.md"
tags: ["ticket", "planning", "status", "documentation", "sprint"]
category: "project-management"
relevance:
  - trigger: "create ticket|new ticket|add ticket|start work"
  - context: "When starting any new work item (feature, bug fix, task)"
dependencies:
  - "PROJECT_STATUS.md"
related:
  - "commands/start-sprint"
  - "commands/update-status"
  - "workflows/feature-development"
author: "Proto Gear Team"
last_updated: "2025-11-05"
status: "stable"
---

# Create Ticket Command

## Purpose

Creates a properly documented ticket in PROJECT_STATUS.md, establishing it as a trackable work item with a unique ID, clear description, and metadata.

## When to Use

Use this command when:
- ✅ Starting a new feature
- ✅ Documenting a bug to fix
- ✅ Planning a refactoring task
- ✅ Creating any trackable work item
- ✅ Beginning a sprint

## Prerequisites

- PROJECT_STATUS.md exists in project root
- You understand ticket types (feature, bugfix, hotfix, task)
- You have a clear description of the work

## Command Pattern

### Step 1: Read Current State

Read PROJECT_STATUS.md to determine next ticket ID:

```bash
# Read PROJECT_STATUS.md
cat PROJECT_STATUS.md
```

Look for:
```yaml
last_ticket_id: 42
ticket_prefix: "PROJ"
```

Next ticket will be: `PROJ-043`

### Step 2: Determine Ticket Type

Choose appropriate type:

| Type | Use Case | Branch Prefix |
|------|----------|---------------|
| **feature** | New functionality | `feature/` |
| **bugfix** | Fixing defects | `bugfix/` |
| **hotfix** | Emergency production fix | `hotfix/` |
| **task** | Non-feature work (refactor, docs, etc.) | `task/` |

### Step 3: Create Ticket Entry

Add ticket to "Active Tickets" section in PROJECT_STATUS.md:

```markdown
## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-043 | Add user authentication | feature | PENDING | - | Backend Agent |
```

**Field Definitions**:
- **ID**: `{PREFIX}-{NUMBER}` (e.g., PROJ-043)
- **Title**: Clear, concise description (verb + object)
- **Type**: feature|bugfix|hotfix|task
- **Status**: PENDING (always start here)
- **Branch**: `-` (no branch yet, created when work starts)
- **Assignee**: Agent or person responsible

### Step 4: Update Metadata

Update project metadata:

```yaml
last_ticket_id: 43  # Increment from previous
```

### Step 5: Add Details (Optional)

For complex tickets, add expanded details:

```markdown
## 🎫 Active Tickets

...

### PROJ-043: Add User Authentication (Details)

**Description**: Implement username/password authentication for users

**Acceptance Criteria**:
- [ ] Users can login with username and password
- [ ] Invalid credentials show error message
- [ ] Successful login creates session token
- [ ] Sessions expire after 24 hours

**Technical Notes**:
- Use bcrypt for password hashing
- Store sessions in Redis
- Follow OWASP authentication guidelines

**Dependencies**:
- Database schema must include users table
- Redis must be configured

**Estimated Effort**: 4 hours
```

## Complete Example

### Before

```markdown
# PROJECT STATUS

## Current State

```yaml
last_ticket_id: 42
ticket_prefix: "PROJ"
```

## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-041 | Fix homepage load time | bugfix | IN_PROGRESS | bugfix/PROJ-041-fix-homepage-load | Performance Agent |
```

### After

```markdown
# PROJECT STATUS

## Current State

```yaml
last_ticket_id: 43  # ← UPDATED
ticket_prefix: "PROJ"
```

## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-041 | Fix homepage load time | bugfix | IN_PROGRESS | bugfix/PROJ-041-fix-homepage-load | Performance Agent |
| PROJ-043 | Add user authentication | feature | PENDING | - | Backend Agent |  # ← NEW TICKET
```

## Ticket Status Workflow

```
PENDING → IN_PROGRESS → COMPLETED
   ↓           ↓
BLOCKED ←──────┘
   ↓
CANCELLED
```

**Status Transitions**:
- **PENDING**: Ticket created, not started
- **IN_PROGRESS**: Work has begun (branch created)
- **BLOCKED**: Cannot proceed (dependency, blocker)
- **COMPLETED**: Work finished, tests passing, merged
- **CANCELLED**: No longer needed

## Ticket Naming Conventions

### Good Ticket Titles ✅
- "Add user authentication"
- "Fix memory leak in image processor"
- "Refactor database connection pooling"
- "Update API documentation for v2.0"

**Pattern**: `<Verb> <Object> [Context]`

### Poor Ticket Titles ❌
- "Auth stuff" (vague)
- "Bug" (not descriptive)
- "Do the thing we talked about" (unclear)
- "URGENT!!!" (not descriptive)

## Integration with Workflows

After creating ticket, typically:

1. **For features**: Follow [Feature Development Workflow](../workflows/feature-development.md)
2. **For bugs**: Follow [Bug Fix Workflow](../workflows/bug-fix.md) (if available)
3. **For refactoring**: Follow [Refactoring Workflow](../workflows/refactoring.md) (if available)

## Common Scenarios

### Scenario 1: Creating Multiple Tickets

```markdown
## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-043 | Add user authentication | feature | PENDING | - | Backend Agent |
| PROJ-044 | Create login UI form | feature | PENDING | - | Frontend Agent |
| PROJ-045 | Add authentication tests | task | PENDING | - | Testing Agent |
```

### Scenario 2: Epic with Sub-tickets

```markdown
## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-043 | [EPIC] Complete user management | epic | IN_PROGRESS | - | Lead Agent |
| PROJ-044 | └─ Add user authentication | feature | IN_PROGRESS | feature/PROJ-044 | Backend Agent |
| PROJ-045 | └─ Add user registration | feature | PENDING | - | Backend Agent |
| PROJ-046 | └─ Add password reset | feature | PENDING | - | Backend Agent |
```

### Scenario 3: Ticket with Dependencies

```markdown
### PROJ-045: Add Password Reset (Details)

**Dependencies**:
- PROJ-044 (authentication) must be completed first
- Email service must be configured

**Status**: BLOCKED (waiting on PROJ-044)
```

## Validation Checklist

Before considering ticket created:
- [ ] Unique ticket ID assigned
- [ ] Clear, descriptive title
- [ ] Appropriate type selected (feature/bugfix/hotfix/task)
- [ ] Status set to PENDING
- [ ] Assignee identified
- [ ] Added to Active Tickets table
- [ ] `last_ticket_id` incremented in metadata
- [ ] Dependencies noted (if any)

## Related Commands

- **[Update Status](update-status.md)** - Change ticket status (if available)
- **[Start Sprint](start-sprint.md)** - Create multiple tickets (if available)
- **[Create Branch](create-branch.md)** - Create branch after ticket creation (if available)

## Related Workflows

- **[Feature Development](../workflows/feature-development.md)** - Uses Create Ticket in Step 1
- **[Bug Fix](../workflows/bug-fix.md)** - Uses Create Ticket to document bug (if available)

## Tools Used

- Text editor - To modify PROJECT_STATUS.md
- `cat` or `less` - To read current state

## Tips for AI Agents

1. **Always read first**: Check PROJECT_STATUS.md before creating tickets
2. **Increment properly**: Ensure last_ticket_id is updated
3. **Be descriptive**: Titles should clearly convey what work is being done
4. **Set realistic status**: New tickets always start as PENDING
5. **Track everything**: Every work item should have a ticket

---
*Proto Gear Create Ticket Command v1.0 - Stable*
