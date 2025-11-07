# Commands Index

> **Single-action patterns** - Commands provide guidance for discrete, atomic tasks

## Available Commands

### Create Ticket
**File**: `create-ticket.md`
**Version**: 1.0.0
**Description**: Create and properly document a ticket in PROJECT_STATUS.md
**Tags**: ticket, planning, status, documentation, sprint
**Category**: project-management
**Status**: Stable

**Dependencies**:
- PROJECT_STATUS.md

**Related**:
- workflows/feature-development (uses this command in Step 1)

**Relevance**:
- Trigger keywords: "create ticket", "new ticket", "add ticket", "start work"
- Context: When starting any new work item (feature, bug fix, task)

---

## How to Use Commands

Commands are single-action patterns for discrete tasks. Unlike workflows, commands focus on one specific action.

### For AI Agents

1. **Identify the action** - What specific task do you need to accomplish?
2. **Find matching command** - Look for trigger keywords
3. **Check dependencies** - Ensure required files exist (e.g., PROJECT_STATUS.md)
4. **Follow the pattern** - Execute the steps described
5. **Verify completion** - Check that the action succeeded

### Command Structure

Each command contains:
- **Purpose** - Why this command exists
- **When to Use** - Specific scenarios
- **Prerequisites** - What must exist before running
- **Command Pattern** - Step-by-step instructions
- **Complete Example** - Before/after demonstration
- **Validation Checklist** - How to verify success

### Example: Using Create Ticket Command

```
Task: Document a new feature as a ticket

1. Read commands/create-ticket.md
2. Read PROJECT_STATUS.md to get last_ticket_id
3. Determine next ticket ID (e.g., PROJ-043)
4. Add ticket entry to Active Tickets table
5. Increment last_ticket_id in metadata
6. Verify ticket was created correctly
```

---

## Command vs. Workflow

**When to use a Command**:
- Single, atomic action
- Quick reference needed
- Part of a larger workflow
- No multiple decision points

**When to use a Workflow**:
- Multi-step process
- Multiple decision points
- Orchestrates several actions
- Takes significant time

**Example**:
- Command: "Create Ticket" (single action)
- Workflow: "Feature Development" (uses Create Ticket as Step 1 of 7)

---

## Commands Reference

### Project Management
- **create-ticket** - Document new work item in PROJECT_STATUS.md

### Git Workflow
- **create-branch** - Create feature branch (if available)
- **commit-changes** - Make conventional commit (if available)

### Testing
- **run-tests** - Execute test suite (if available)

### Status Updates
- **update-status** - Modify PROJECT_STATUS.md (if available)

*Additional commands available when using `--with-capabilities=full`*

---

## Adding Custom Commands

To add a new command to this project:

1. Create file: `commands/your-command-name.md`
2. Add YAML frontmatter:
   ```yaml
   ---
   name: "Your Command Name"
   type: "command"
   version: "1.0.0"
   description: "Brief description of what this command does"
   tags: ["keyword1", "keyword2"]
   category: "project-management"
   relevance:
     - trigger: "keywords that suggest this command"
     - context: "when to use this command"
   dependencies: ["PROJECT_STATUS.md"]
   related: ["workflows/feature-development"]
   status: "stable"
   ---
   ```
3. Write clear, actionable instructions
4. Include before/after examples
5. Add validation checklist
6. Update this INDEX.md to list your new command

---

## Integration with Workflows

Commands are often used as building blocks within larger workflows:

- **feature-development** workflow uses:
  - create-ticket (Step 1)
  - create-branch (Step 2)
  - run-tests (Steps 3-5)
  - commit-changes (Step 6)
  - update-status (Step 7)

This modular approach means:
- Commands can be used independently
- Workflows can reference commands
- Easy to customize individual steps
- Consistent patterns across workflows

---

*Proto Gear Commands Index*
