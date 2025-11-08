# How Humans Use Templates

**Part of**: [Template-Based Collaboration Guide](../TEMPLATE_GUIDE.md)
**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04

---

## Overview

This guide explains how human developers use Proto Gear templates to collaborate with AI assistants and maintain consistent workflows.

---

## For Solo Developers

### Initial Setup

1. **Generate templates** in your project:
```bash
cd your-project
pg init
```

2. **Review generated files**:
- AGENTS.md - Agent roles and patterns
- PROJECT_STATUS.md - State tracking
- BRANCHING.md (optional) - Git conventions
- TESTING.md (optional) - TDD patterns

3. **Customize** if needed:
- Update ticket prefix
- Adjust sprint type
- Add project-specific patterns

### Working with AI Assistants

**Scenario 1: Starting New Feature**

```
Human: "I've set up Proto Gear in this project. Please read AGENTS.md and
PROJECT_STATUS.md to understand the project state, then implement the
authentication feature following our TDD workflow from TESTING.md."
```

**What Happens**:
1. AI reads AGENTS.md → Understands role patterns
2. AI reads PROJECT_STATUS.md → Sees current state
3. AI reads TESTING.md → Learns TDD workflow
4. AI implements following patterns
5. AI updates PROJECT_STATUS.md

**Scenario 2: Fixing Bug**

```
Human: "There's a bug in the login form - email validation is missing.
Please fix this following our branching conventions and TDD workflow."
```

**What Happens**:
1. AI reads BRANCHING.md → Learns conventions
2. AI creates bugfix branch with proper naming
3. AI follows TDD: write test, fix, refactor
4. AI commits with conventional format
5. AI updates PROJECT_STATUS.md

### Maintaining Templates

**Keep PROJECT_STATUS.md Current**:
- Update ticket status when you complete work
- Add entries to Recent Updates
- Move completed tickets to Completed section

**Update Templates When Workflows Change**:
- Modify BRANCHING.md if git conventions change
- Update TESTING.md if coverage targets change
- Adjust AGENTS.md if agent roles change

---

## For Teams

### Shared Understanding

**Benefits**:
- All team members (human + AI) follow same conventions
- PROJECT_STATUS.md tracks everyone's work
- BRANCHING.md ensures consistent git usage
- TESTING.md ensures consistent test quality

**Setup**:
1. One person runs `pg init` in the project
2. Commit generated files to repository
3. Team reviews and customizes templates
4. Everyone follows the documented patterns

### Team Workflows

**Sprint Planning**:

1. **Update PROJECT_STATUS.md**:
```yaml
sprint_type: "feature_development"
current_sprint: 5
```

2. **Create tickets**:
```markdown
| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-020 | Add payment | feature | PENDING | - | - |
| PROJ-021 | User dashboard | feature | PENDING | - | - |
| PROJ-022 | Email notifications | feature | PENDING | - | - |
```

3. **Team members** (human + AI) pick tickets and update status

**Daily Standup**:
- Review PROJECT_STATUS.md for current work
- Check blocked tickets
- See recent updates

**Code Review**:
- Verify BRANCHING.md conventions followed
- Check TESTING.md patterns used
- Ensure PROJECT_STATUS.md updated

### Coordination

**Scenario: Parallel Development**

**Developer A** (human):
- Picks PROJ-020 (Add payment)
- Updates status to IN_PROGRESS
- Adds their name as assignee

**Developer B** (AI assistant):
- Reads PROJECT_STATUS.md
- Sees PROJ-020 is taken
- Picks PROJ-021 (User dashboard)
- Updates status to IN_PROGRESS

**Result**: No duplicate work, clear visibility

---

## Best Practices for Humans

### DO ✅

1. **Share Templates with AI Assistants**
```
"Please read AGENTS.md, PROJECT_STATUS.md, BRANCHING.md, and TESTING.md
to understand our project conventions before starting work."
```

2. **Reference Specific Sections**
```
"Follow the TDD workflow from TESTING.md section 3 (Red-Green-Refactor cycle)"
```

3. **Keep State Current**
- Update PROJECT_STATUS.md when you complete work
- Mark tickets IN_PROGRESS when starting
- Move to COMPLETED when done

4. **Follow Your Own Conventions**
- Use BRANCHING.md conventions in your own work
- Follow TESTING.md patterns
- Maintain consistency

5. **Update Templates**
- Modify templates when workflows change
- Add new patterns as they emerge
- Keep templates in sync with reality

### DON'T ❌

1. **Don't Let State Get Stale**
- ❌ Leaving old IN_PROGRESS tickets
- ❌ Empty Recent Updates section
- ❌ Completed work not reflected

2. **Don't Skip Documentation Updates**
- ❌ Changing git workflow without updating BRANCHING.md
- ❌ New testing patterns not in TESTING.md
- ❌ Modified agent roles not in AGENTS.md

3. **Don't Assume AI Knows Everything**
- ❌ "Just implement authentication"
- ✅ "Read our patterns and implement authentication"

4. **Don't Work in Isolation**
- ❌ Not updating PROJECT_STATUS.md
- ❌ Not checking what others are doing
- ❌ Creating duplicate work

---

## Common Workflows

### Workflow 1: Feature Request from Product

**Steps**:

1. **Create ticket** in PROJECT_STATUS.md:
```markdown
| PROJ-030 | Dark mode toggle | feature | PENDING | - | - |
```

2. **Assign to AI assistant**:
```
"Please implement PROJ-030 (dark mode toggle) following our patterns.
Read AGENTS.md for context and TESTING.md for TDD workflow."
```

3. **AI implements**:
- Creates branch: `feature/proj-030-dark-mode-toggle`
- Follows TDD workflow
- Commits with conventional format
- Updates PROJECT_STATUS.md

4. **Human reviews**:
- Check branch follows BRANCHING.md
- Verify tests exist (TESTING.md)
- Review implementation
- Merge when approved

### Workflow 2: Bug Report from User

**Steps**:

1. **Create bug ticket**:
```markdown
| PROJ-031 | Email validation broken | bugfix | PENDING | - | - |
```

2. **Investigate** (human or AI):
```
"Please investigate PROJ-031 and fix following our TDD workflow."
```

3. **AI fixes**:
- Creates branch: `bugfix/proj-031-email-validation`
- Writes failing test (reproduces bug)
- Fixes bug
- Commits: `fix(auth): add email format validation`
- Updates PROJECT_STATUS.md

### Workflow 3: Sprint Type Change

**Steps**:

1. **Update PROJECT_STATUS.md**:
```yaml
# Change from feature_development to bug_fixing
sprint_type: "bug_fixing"
active_agents:
  core:
    - Lead AI
    - Backend Agent
    - Frontend Agent
    - Testing Agent
  flex:
    - Debug Agent  # Activated for bug fixing
    - Testing Agent  # Extra testing focus
```

2. **Inform team**:
```
"Sprint 6 focus is bug fixing. Read updated PROJECT_STATUS.md for
new agent configuration. Prioritize bugfix tickets."
```

3. **AI assistants adapt**:
- Read updated PROJECT_STATUS.md
- See sprint type changed to bug_fixing
- Adjust focus to bugs

---

## Tips for Effective Collaboration

### Be Specific
**❌ Vague**:
```
"Add authentication"
```

**✅ Specific**:
```
"Implement PROJ-025 (user authentication) following patterns from AGENTS.md.
Use the TDD workflow from TESTING.md and create branch following BRANCHING.md
conventions. Update PROJECT_STATUS.md when complete."
```

### Provide Context
**❌ No Context**:
```
"Fix the login bug"
```

**✅ With Context**:
```
"Create ticket for login email validation bug. Read PROJECT_STATUS.md
for next ticket ID. Fix following our TDD workflow (TESTING.md) and
update the ticket when done."
```

### Give Feedback
**When AI Doesn't Follow Patterns**:
```
"The branch name should follow BRANCHING.md format: bugfix/PROJ-XXX-description.
Please review section 2.1 of BRANCHING.md and recreate the branch."
```

### Keep Templates Updated
**When Workflows Evolve**:
```
"We've changed our git workflow. Please help me update BRANCHING.md
to reflect that we now use 'develop' as our default branch instead of 'main'."
```

---

## Troubleshooting

### Problem: AI Not Following Patterns

**Solution**: Be explicit about reading templates:
```
"Before starting, please read these files to understand our conventions:
1. AGENTS.md - Your role and patterns
2. PROJECT_STATUS.md - Current project state
3. BRANCHING.md - Git conventions
4. TESTING.md - TDD workflow

Then implement the feature following these patterns."
```

### Problem: State Gets Out of Sync

**Solution**: Regular state reviews:
- Daily: Review PROJECT_STATUS.md
- Weekly: Update completed tickets
- Monthly: Archive old completed tickets

### Problem: Templates Not Helping

**Solution**: Add more examples:
- Real workflow examples in TESTING.md
- Actual commit message examples in BRANCHING.md
- Common scenarios in AGENTS.md

---

## Next Steps

- **See examples**: [Workflow Examples](04-workflow-examples.md)
- **Learn AI patterns**: [AI Agent Usage Guide](02-ai-agent-usage.md)
- **Having issues?**: [Troubleshooting](05-troubleshooting.md)

---

[← Back: AI Agent Usage](02-ai-agent-usage.md) | [Template Guide](../TEMPLATE_GUIDE.md) | [Next: Workflow Examples →](04-workflow-examples.md)
