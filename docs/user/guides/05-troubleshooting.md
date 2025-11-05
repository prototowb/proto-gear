# Troubleshooting

**Part of**: [Template-Based Collaboration Guide](../TEMPLATE_GUIDE.md)
**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04

---

## Overview

This guide addresses common problems when using Proto Gear templates and provides solutions for humans and AI agents.

---

## Problem: AI Agent Tries to Import Proto Gear Modules

### Symptom

AI agent attempts to use Python imports:
```python
from proto_gear.agent_framework import WorkflowOrchestrator
# ImportError or ModuleNotFoundError
```

Or:
```python
from git_workflow import GitBranchManager
manager = GitBranchManager()
# Module not found
```

### Why This Happens

AI agent misunderstands that code blocks in templates are **patterns**, not executable code.

### Solution

**For Humans**: Remind the AI agent explicitly:
```
"The code blocks in AGENTS.md are patterns for decision-making, not
executable Python functions. Please read the 'How to Use This Document'
section at the top of AGENTS.md. Use native git commands instead."
```

**For AI Agents**: Re-read the template file headers. Look for:
```markdown
## 📖 How to Use This Document

**For AI Agents:**
This document defines **patterns and workflows** for natural language
collaboration. The code blocks are **illustrative patterns**, not executable code.
```

### Correct Approach

**❌ Wrong**:
```python
from git_workflow import create_branch
create_branch("feature/proj-001-auth")
```

**✅ Correct**:
```bash
# Read the pattern from BRANCHING.md
# Use native git command
$ git checkout -b feature/proj-001-auth
```

---

## Problem: PROJECT_STATUS.md Not Updated

### Symptom

- Tickets show as PENDING but work is done
- Recent Updates section is empty
- State doesn't match reality
- Team members don't know what's in progress

### Why This Happens

- Forgot to update after completing work
- Not following the workflow pattern
- Working in isolation

### Solution

**For Humans**: Establish update routine:
- Update status when starting work (→ IN_PROGRESS)
- Update status when completing (→ COMPLETED)
- Add to Recent Updates for significant changes
- Daily review of PROJECT_STATUS.md

**For AI Agents**: Always include state updates in workflow:
1. Start work → Update PROJECT_STATUS.md
2. Complete work → Update PROJECT_STATUS.md
3. Add to Recent Updates timeline

### Prevention Pattern

Add to AGENTS.md workflow patterns:
```markdown
## IMPORTANT: State Management

After completing ANY task:
1. Update ticket status in PROJECT_STATUS.md
2. Move completed ticket to Completed Tickets section
3. Add entry to Recent Updates
4. Push changes to repository
```

---

## Problem: Inconsistent Branch Naming

### Symptom

Mix of branch naming styles:
- `feature/add-auth` (missing ticket ID)
- `PROJ-001-auth` (missing type prefix)
- `fix_login_bug` (wrong separator, missing ticket)
- `proj-002-payment-feature` (wrong order)

### Why This Happens

- BRANCHING.md not read or followed
- No clear examples
- Team members unaware of conventions

### Solution

**Update BRANCHING.md** with clear examples:

````markdown
## Branch Naming Examples

✅ **CORRECT**:
- `feature/PROJ-001-add-user-auth`
- `bugfix/PROJ-042-fix-login-error`
- `hotfix/v1.2.3-security-patch`
- `refactor/PROJ-100-simplify-auth`

❌ **INCORRECT**:
- `feature/add-auth` (missing ticket ID)
- `PROJ-001-auth` (missing type prefix)
- `fix_login` (wrong separator, missing ticket)
- `feature-add-auth` (wrong separator)
````

**For Humans**: Share BRANCHING.md explicitly:
```
"Please read BRANCHING.md section 2 (Branch Naming Conventions) before
creating the branch. Use the pattern: type/PREFIX-XXX-description"
```

**For AI Agents**: Re-read BRANCHING.md before every branch creation.

---

## Problem: Template Patterns Are Unclear

### Symptom

- AI agents confused about what to do
- Humans uncertain about workflows
- Inconsistent execution of patterns
- Questions about interpretation

### Why This Happens

- Patterns too abstract
- Missing concrete examples
- Not enough context
- Ambiguous wording

### Solution

**Enhance Templates** with more examples:

**Before** (unclear):
````markdown
```python
def workflow():
    """Follow TDD workflow"""
    pass
```
````

**After** (clear):
````markdown
## TDD Workflow Pattern

```python
def tdd_workflow_pattern():
    """
    PATTERN for Test-Driven Development:

    1. RED Phase:
       - Write failing test first
       - Run test (should fail)
       - Example: $ pytest tests/test_auth.py

    2. GREEN Phase:
       - Write minimal code to pass test
       - Run test (should pass)

    3. REFACTOR Phase:
       - Improve code quality
       - Keep tests passing
    """
```

**Concrete Example**:
```bash
# RED: Write test
$ cat > tests/test_login.py
def test_user_login():
    assert login("user", "pass") == True

# Run (fails)
$ pytest tests/test_login.py
# AssertionError ✗

# GREEN: Implement
$ cat > src/auth.py
def login(user, password):
    return True  # Minimal implementation

# Run (passes)
$ pytest tests/test_login.py
# ✓

# REFACTOR: Improve
$ vim src/auth.py
# Add actual authentication logic
```
````

---

## Problem: Multiple Agents Working on Same Ticket

### Symptom

- Duplicate work
- Conflicting branches
- Wasted effort
- Merge conflicts

### Why This Happens

- PROJECT_STATUS.md not checked before starting
- State not updated when starting work
- Poor coordination

### Solution

**Workflow Pattern**:
```markdown
## Before Starting Any Work

1. Read PROJECT_STATUS.md
2. Check Active Tickets section
3. Verify ticket is PENDING (not IN_PROGRESS)
4. Update status to IN_PROGRESS with your name
5. THEN start work
```

**Example**:

**AI Agent A**:
```bash
$ cat PROJECT_STATUS.md
# Sees: | PROJ-020 | Add payment | feature | PENDING | - | - |

# Updates immediately:
| PROJ-020 | Add payment | feature | IN_PROGRESS | feature/proj-020-payment | Agent A |

# Now safe to start work
$ git checkout -b feature/proj-020-payment
```

**AI Agent B** (later):
```bash
$ cat PROJECT_STATUS.md
# Sees: | PROJ-020 | Add payment | feature | IN_PROGRESS | ... | Agent A |

# Sees it's taken, picks different ticket:
| PROJ-021 | User dashboard | feature | PENDING | - | - |
```

---

## Problem: Blocked Tickets Not Documented

### Symptom

- Tickets stuck without explanation
- Team unaware of blockers
- Can't help resolve issues
- Work stalls

### Why This Happens

- Blocker encountered but not documented
- PROJECT_STATUS.md not updated
- Missing Blocked Tickets section

### Solution

**When You Hit a Blocker**:

1. **Update ticket status**:
```markdown
Change:
| PROJ-030 | Payment API | feature | IN_PROGRESS | feature/proj-030-payment | Backend Agent |

To:
| PROJ-030 | Payment API | feature | BLOCKED | feature/proj-030-payment | Backend Agent |
```

2. **Add to Blocked Tickets section**:
```markdown
## 🚧 Blocked Tickets

| ID | Title | Blocker | Since |
|----|-------|---------|-------|
| PROJ-030 | Payment API | Waiting for Stripe API keys from DevOps | 2025-11-04 |
```

3. **Add to Recent Updates**:
```markdown
## 🔄 Recent Updates
- 2025-11-04: PROJ-030 blocked - need API keys from DevOps
```

4. **Pick different ticket** while waiting

---

## Problem: Tests Not Following TDD

### Symptom

- Tests written after implementation
- Low test coverage
- Tests don't catch bugs
- Not following Red-Green-Refactor

### Why This Happens

- TESTING.md not read
- TDD workflow unclear
- Shortcuts taken

### Solution

**Enforce TDD in Workflow Patterns**:

Add to AGENTS.md:
```markdown
## ⚠️ TDD is REQUIRED

ALWAYS follow Red-Green-Refactor cycle:

**STEP 1 - RED**: Write failing test FIRST
```bash
$ cat > tests/test_feature.py
def test_new_feature():
    assert feature() == expected

$ pytest tests/test_feature.py
# MUST FAIL ✗ (if it passes, test is wrong!)
```

**STEP 2 - GREEN**: Minimal implementation
```bash
$ cat > src/feature.py
def feature():
    return expected  # Minimal code

$ pytest tests/test_feature.py
# MUST PASS ✓
```

**STEP 3 - REFACTOR**: Improve while keeping tests green
```

**For Humans**: Code review checklist:
- [ ] Tests exist before implementation commit?
- [ ] Test committed first (RED phase)?
- [ ] Implementation commit second (GREEN phase)?
- [ ] Refactoring commit third (REFACTOR phase)?

---

## Problem: Commit Messages Don't Follow Convention

### Symptom

- Vague commit messages: "fix stuff", "updates"
- Missing type prefix: "add authentication" instead of "feat(auth): ..."
- Missing ticket references
- Inconsistent format

### Why This Happens

- BRANCHING.md not followed
- Conventions unclear
- No examples provided

### Solution

**Add Clear Examples to BRANCHING.md**:

```markdown
## Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

## Examples

✅ **CORRECT**:
```
feat(auth): add user authentication system

Implements username/password authentication with bcrypt hashing.
Includes session management and password reset flow.

Closes PROJ-001
```

```
fix(login): prevent email case sensitivity bug

Login was failing for emails with uppercase letters.
Now normalizes email to lowercase before validation.

Closes PROJ-025
```

❌ **INCORRECT**:
- "add auth" (no type, no scope, vague)
- "fixed bug" (no details, which bug?)
- "updates" (meaningless)
- "feat: stuff" (no scope, vague subject)
```

---

## Problem: Sprint Type Changes Not Reflected

### Symptom

- PROJECT_STATUS.md shows old sprint type
- Agents not adapting to new focus
- Flex agent slots not updated

### Why This Happens

- Forgot to update PROJECT_STATUS.md
- Agents not re-reading after change
- Team not notified

### Solution

**Sprint Change Workflow**:

1. **Update PROJECT_STATUS.md**:
```yaml
sprint_type: "bug_fixing"  # Changed from "feature_development"

active_agents:
  core:
    - Lead AI
    - Backend Agent
    - Frontend Agent
    - Testing Agent
  flex:
    - Debug Agent  # Changed for bug fixing sprint
    - Testing Agent  # Added for extra testing focus
```

2. **Announce to team**:
```
"Sprint 6 is now focused on bug fixing. Please read the updated
PROJECT_STATUS.md to see new agent configuration and priorities."
```

3. **All agents re-read**:
- AGENTS.md (for new flex agent patterns)
- PROJECT_STATUS.md (for new sprint type)

---

## Quick Troubleshooting Checklist

### For Humans

- [ ] Did you share template files with AI assistant?
- [ ] Did you reference specific template sections?
- [ ] Is PROJECT_STATUS.md up to date?
- [ ] Are conventions in BRANCHING.md being followed?
- [ ] Does TESTING.md have clear TDD examples?

### For AI Agents

- [ ] Did you read AGENTS.md before starting?
- [ ] Did you check PROJECT_STATUS.md for current state?
- [ ] Are you using native tools (git, pytest, npm)?
- [ ] Did you update PROJECT_STATUS.md after completing work?
- [ ] Are you following patterns with judgment, not executing template code?

---

## Getting More Help

**Still having issues?**

1. **Review related guides**:
   - [Template Basics](01-template-basics.md) - Understand foundations
   - [AI Agent Usage](02-ai-agent-usage.md) - AI workflow guidance
   - [Human Usage](03-human-usage.md) - Human workflow guidance
   - [Workflow Examples](04-workflow-examples.md) - See patterns in action

2. **Check template files**:
   - AGENTS.md - Agent patterns
   - PROJECT_STATUS.md - Current state
   - BRANCHING.md - Git conventions
   - TESTING.md - TDD workflow

3. **Open an issue**:
   - [GitHub Issues](https://github.com/proto-gear/proto-gear/issues)
   - Describe the problem
   - Include relevant template sections
   - Share what you've tried

4. **Review documentation**:
   - [README.md](../../README.md) - Project overview
   - [READINESS_ASSESSMENT.md](../READINESS_ASSESSMENT.md) - Current state
   - [CONTRIBUTING.md](../../CONTRIBUTING.md) - Contribution guidelines

---

[← Back: Workflow Examples](04-workflow-examples.md) | [Template Guide](../TEMPLATE_GUIDE.md)
