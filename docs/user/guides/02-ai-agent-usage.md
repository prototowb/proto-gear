# AI Agent Usage Guide

**Part of**: [Template-Based Collaboration Guide](../TEMPLATE_GUIDE.md)
**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04

---

## Overview

This guide explains how AI agents should read and use Proto Gear templates to collaborate with humans using native development tools.

**Key Point**: You are NOT calling Python functions. You are reading patterns and using native tools like git, pytest, and npm.

---

## Step 1: Initial Context Gathering

When starting work on a project, read these templates in order:

### 1. Read AGENTS.md
- Understand your role (Backend, Frontend, Testing, etc.)
- See decision-making patterns
- Learn coordination workflows
- **Critical**: Read the "How to Use This Document" section first

### 2. Read PROJECT_STATUS.md
- See current project state
- Identify active tickets
- Check sprint type and configuration
- Understand what others are working on

### 3. Read BRANCHING.md (if exists)
- Learn branch naming conventions
- Understand conventional commit format
- See workflow examples

### 4. Read TESTING.md (if exists)
- Understand TDD workflow
- Learn test pyramid structure
- Know coverage targets

---

## Step 2: Pattern Interpretation

### How to Read Template Patterns

**Template Pattern Example**:
````markdown
## Starting New Feature Work

```python
def start_feature_workflow():
    """
    PATTERN for starting new feature:
    1. Read PROJECT_STATUS.md to find pending tickets
    2. Select highest priority ticket
    3. Update ticket status to IN_PROGRESS
    4. Create branch: feature/PREFIX-XXX-description
    5. Follow TDD: write test first, then implementation
    6. Commit with conventional format
    7. Update PROJECT_STATUS.md when complete
    """
```
````

### How to Execute This Pattern

**Your Actions** (using native tools):

1. **Read State**:
```bash
$ cat PROJECT_STATUS.md
# You see tickets, identify PROJ-001 as next priority
```

2. **Update Status** (edit the file):
```markdown
Change:
| PROJ-001 | Add auth | feature | PENDING | - | - |

To:
| PROJ-001 | Add auth | feature | IN_PROGRESS | feature/proj-001-add-auth | AI Agent |
```

3. **Create Branch** (native git):
```bash
$ git checkout -b feature/proj-001-add-auth
```

4. **Follow TDD** (native tools):
```bash
# Write test
$ cat > tests/test_auth.py
def test_user_can_login():
    # Test code

# Run test (RED)
$ pytest tests/test_auth.py

# Write implementation
$ cat > src/auth.py
# Implementation code

# Run test (GREEN)
$ pytest tests/test_auth.py
```

5. **Commit** (native git, following BRANCHING.md):
```bash
$ git add .
$ git commit -m "feat(auth): add user login functionality

Implements basic authentication.
Test coverage: 100% for auth module.

Closes PROJ-001"
```

6. **Update State** (edit PROJECT_STATUS.md):
```markdown
Move ticket to Completed Tickets section
Add entry to Recent Updates
```

---

## Step 3: Using Native Tools

### Git Commands

You use git directly, NOT Python subprocess calls:

**✅ Correct**:
```bash
$ git checkout -b feature/proj-001-auth
$ git add src/auth.py tests/test_auth.py
$ git commit -m "feat(auth): add authentication"
$ git push origin feature/proj-001-auth
```

**❌ Wrong** (Don't do this):
```python
from git_workflow import GitBranchManager
manager = GitBranchManager()
manager.create_branch("feature/proj-001-auth")
```

### Testing Commands

**✅ Correct**:
```bash
$ pytest tests/test_auth.py
$ pytest --cov=src tests/
$ npm test
$ cargo test
```

**❌ Wrong**:
```python
from testing_workflow import TestRunner
runner = TestRunner()
runner.run_tests()
```

### Build/Run Commands

**✅ Correct**:
```bash
$ npm run build
$ docker-compose up
$ python manage.py runserver
$ cargo build --release
```

---

## Step 4: State Management

### When to Update PROJECT_STATUS.md

Update the state file:

1. **Starting work**: Change ticket from PENDING → IN_PROGRESS
2. **Creating branch**: Add branch name to ticket row
3. **Completing work**: Move ticket to Completed Tickets section
4. **Blocking**: Change status to BLOCKED with reason
5. **Significant changes**: Add entry to Recent Updates

### How to Update

**Edit the file directly** (you have file editing capabilities):

````markdown
## Before
| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-001 | Add auth | feature | PENDING | - | - |

## After (when starting work)
| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-001 | Add auth | feature | IN_PROGRESS | feature/proj-001-add-auth | AI Agent |
````

---

## Step 5: Coordination with Other Agents

### Reading Current Work

Before starting, check PROJECT_STATUS.md to see:
- What tickets are IN_PROGRESS (avoid duplicates)
- Who is working on what
- Any BLOCKED tickets that need help
- Current sprint type and active agents

### Communication via State

**Scenario**: You discover a blocker

**Action**: Update PROJECT_STATUS.md:
````markdown
## Blocked Tickets

| ID | Title | Blocker | Since |
|----|-------|---------|-------|
| PROJ-010 | Payment API | Waiting for API keys from client | 2025-11-04 |
````

Other agents will see this and can help resolve or work on other tickets.

---

## Best Practices for AI Agents

### DO ✅

1. **Always Read Templates First**
   - AGENTS.md for your role
   - PROJECT_STATUS.md for current state
   - BRANCHING.md and TESTING.md for conventions

2. **Use Native Tools**
   - Execute git, pytest, npm, docker commands directly
   - Don't try to import Proto Gear modules
   - Use your natural capabilities

3. **Update State Regularly**
   - Mark tickets IN_PROGRESS when starting
   - Update PROJECT_STATUS.md when completing
   - Add to Recent Updates timeline

4. **Follow Patterns with Judgment**
   - Interpret patterns based on context
   - Adapt to specific situations
   - Ask for clarification if unclear

5. **Coordinate via Documentation**
   - Check PROJECT_STATUS.md before starting work
   - Update state so others can see your progress
   - Communicate blockers clearly

### DON'T ❌

1. **Don't Try to Execute Template Code**
   ```python
   # ❌ WRONG - This won't work
   from agents_md import lead_ai_workflow
   lead_ai_workflow()
   ```

2. **Don't Import Proto Gear Modules**
   ```python
   # ❌ WRONG - These don't exist for agents to use
   from proto_gear.agent_framework import WorkflowOrchestrator
   from proto_gear.git_workflow import GitBranchManager
   ```

3. **Don't Skip State Updates**
   - Always update PROJECT_STATUS.md when changing ticket status
   - Don't leave stale IN_PROGRESS tickets
   - Keep Recent Updates current

4. **Don't Ignore Conventions**
   - Follow BRANCHING.md naming patterns
   - Use conventional commit format
   - Follow TESTING.md TDD workflow

5. **Don't Work in Isolation**
   - Check what others are doing
   - Update state so others can coordinate
   - Communicate via PROJECT_STATUS.md

---

## Common Patterns

### Pattern: Starting New Feature

1. Read PROJECT_STATUS.md → Find pending ticket
2. Update ticket status → IN_PROGRESS
3. Create branch → `git checkout -b feature/PROJ-XXX-description`
4. Write test → Follow TESTING.md patterns
5. Implement → Make test pass
6. Commit → Follow BRANCHING.md format
7. Update state → COMPLETED

### Pattern: Fixing Bug

1. Read PROJECT_STATUS.md → Find or create bug ticket
2. Update status → IN_PROGRESS
3. Create branch → `git checkout -b bugfix/PROJ-XXX-description`
4. Write failing test → Reproduce bug
5. Fix bug → Make test pass
6. Commit → `fix(scope): description`
7. Update state → COMPLETED

### Pattern: Blocked Work

1. Identify blocker while working
2. Update PROJECT_STATUS.md:
   - Change status to BLOCKED
   - Add to Blocked Tickets section with reason
   - Add entry to Recent Updates
3. Select different ticket to work on
4. When blocker resolved:
   - Update status back to IN_PROGRESS
   - Resume work

---

## Example: Complete Feature Implementation

**Scenario**: Implement user authentication

### Step 1: Read Context
```bash
$ cat AGENTS.md  # Understand role (Backend Agent)
$ cat PROJECT_STATUS.md  # See ticket PROJ-001: Add user auth
$ cat BRANCHING.md  # Learn conventions
$ cat TESTING.md  # Learn TDD workflow
```

### Step 2: Update State
Edit PROJECT_STATUS.md:
```markdown
| PROJ-001 | Add user auth | feature | IN_PROGRESS | feature/proj-001-add-user-auth | Backend Agent |
```

### Step 3: Create Branch
```bash
$ git checkout -b feature/proj-001-add-user-auth
```

### Step 4: Follow TDD (from TESTING.md)
```bash
# RED: Write failing test
$ cat > tests/test_auth.py
def test_user_login_success():
    user = User(username="test", password="pass123")
    assert user.authenticate("pass123") == True

def test_user_login_failure():
    user = User(username="test", password="pass123")
    assert user.authenticate("wrongpass") == False

$ pytest tests/test_auth.py
# Tests fail (RED)

# GREEN: Implement
$ cat > src/auth.py
class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = hash(password)

    def authenticate(self, password):
        return hash(password) == self.password_hash

$ pytest tests/test_auth.py
# Tests pass (GREEN)

# REFACTOR: Improve if needed
# (Use bcrypt instead of hash, add docstrings, etc.)
```

### Step 5: Commit (following BRANCHING.md)
```bash
$ git add tests/test_auth.py src/auth.py
$ git commit -m "feat(auth): add user authentication system

Implements basic username/password authentication.
- User class with password hashing
- Authentication method
- 100% test coverage

Closes PROJ-001"
```

### Step 6: Update State
Edit PROJECT_STATUS.md:
- Move PROJ-001 to Completed Tickets
- Add entry: "2025-11-04: Completed user authentication (PROJ-001)"

---

## Next Steps

- **See examples**: [Workflow Examples](04-workflow-examples.md)
- **Having issues?**: [Troubleshooting](05-troubleshooting.md)
- **Learn human workflows**: [How Humans Use Templates](03-human-usage.md)

---

[← Back: Template Basics](01-template-basics.md) | [Template Guide](../TEMPLATE_GUIDE.md) | [Next: Human Usage →](03-human-usage.md)
