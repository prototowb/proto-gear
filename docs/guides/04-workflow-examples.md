# Workflow Examples

**Part of**: [Template-Based Collaboration Guide](../TEMPLATE_GUIDE.md)
**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04

---

## Overview

This guide provides concrete examples of template-based workflows in action, showing how humans and AI agents collaborate using Proto Gear templates.

---

## Example 1: Starting New Feature (AI Agent)

**Scenario**: AI agent needs to implement user authentication

### Step 1: Read Context

```bash
$ cat PROJECT_STATUS.md
```

**Sees**:
```markdown
| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-001 | Add user auth | feature | PENDING | - | - |
```

### Step 2: Update Status

AI edits PROJECT_STATUS.md:
```markdown
| PROJ-001 | Add user auth | feature | IN_PROGRESS | feature/proj-001-add-user-auth | Backend Agent |
```

### Step 3: Create Branch (following BRANCHING.md)

```bash
$ git checkout -b feature/proj-001-add-user-auth
```

### Step 4: Follow TDD (following TESTING.md)

**RED Phase**:
```bash
$ cat > tests/test_auth.py
def test_user_can_login():
    user = User("alice", "password123")
    assert user.authenticate("password123") == True

def test_user_cannot_login_with_wrong_password():
    user = User("alice", "password123")
    assert user.authenticate("wrongpass") == False

$ pytest tests/test_auth.py
# Tests fail - RED ✗
```

**GREEN Phase**:
```bash
$ cat > src/auth.py
import bcrypt

class User:
    def __init__(self, username, password):
        self.username = username
        self.password_hash = bcrypt.hashpw(
            password.encode(), bcrypt.gensalt()
        )

    def authenticate(self, password):
        return bcrypt.checkpw(
            password.encode(), self.password_hash
        )

$ pytest tests/test_auth.py
# Tests pass - GREEN ✓
```

**REFACTOR Phase**:
```bash
# Add docstrings, type hints, error handling
$ pytest tests/test_auth.py
# Tests still pass ✓
```

### Step 5: Commit (following BRANCHING.md)

```bash
$ git add tests/test_auth.py src/auth.py
$ git commit -m "feat(auth): add user authentication system

Implements basic username/password authentication with bcrypt.
- User class with secure password hashing
- Authentication method with timing-safe comparison
- 100% test coverage

Closes PROJ-001"
```

### Step 6: Update State

AI edits PROJECT_STATUS.md:

**Move to Completed**:
```markdown
## ✅ Completed Tickets

| ID | Title | Completed | PR |
|----|-------|-----------|-----|
| PROJ-001 | Add user auth | 2025-11-04 | #42 |
```

**Add to Recent Updates**:
```markdown
## 🔄 Recent Updates
- 2025-11-04: Completed user authentication system (PROJ-001)
```

---

## Example 2: Bug Fix with TDD (Human + AI)

**Scenario**: User reports email validation bug, human asks AI to fix

### Human Request

```
"There's a bug in the login form - it doesn't validate email format.
Please fix this following our TDD workflow from TESTING.md and update
PROJECT_STATUS.md."
```

### AI Actions

**Step 1: Read Context**
```bash
$ cat TESTING.md  # Learn TDD workflow
$ cat PROJECT_STATUS.md  # Get next ticket ID
```

**Step 2: Create Ticket**

AI edits PROJECT_STATUS.md:
```markdown
| PROJ-006 | Fix email validation | bugfix | IN_PROGRESS | bugfix/proj-006-email-validation | AI Assistant |
```

**Step 3: Create Branch**
```bash
$ git checkout -b bugfix/proj-006-email-validation
```

**Step 4: Write Failing Test (RED)**
```bash
$ cat >> tests/test_auth.py
def test_email_validation_rejects_invalid():
    assert validate_email("invalid") == False
    assert validate_email("no-at-sign") == False
    assert validate_email("missing-domain@") == False

def test_email_validation_accepts_valid():
    assert validate_email("user@example.com") == True
    assert validate_email("test.user+tag@domain.co.uk") == True

$ pytest tests/test_auth.py::test_email_validation_rejects_invalid
# Test fails (bug reproduced) - RED ✗
```

**Step 5: Fix Bug (GREEN)**
```bash
$ cat > src/validators.py
import re

def validate_email(email):
    """Validate email format using RFC 5322 pattern"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

$ pytest tests/test_auth.py
# All tests pass - GREEN ✓
```

**Step 6: Commit**
```bash
$ git commit -m "fix(auth): add email format validation

Email validation was missing, allowing invalid email formats.
Added regex pattern validation for RFC 5322 format.

Closes PROJ-006"
```

**Step 7: Update State**

AI edits PROJECT_STATUS.md:
```markdown
## ✅ Completed Tickets
| PROJ-006 | Fix email validation | 2025-11-04 | #45 |

## 🔄 Recent Updates
- 2025-11-04: Fixed email validation bug (PROJ-006)
```

---

## Example 3: Sprint Planning (Team)

**Scenario**: Team starts new sprint focused on performance optimization

### Step 1: Update Sprint Configuration

Product Manager updates PROJECT_STATUS.md:
```yaml
project_phase: "Development"
current_sprint: 8
sprint_type: "performance_optimization"

active_agents:
  core:
    - Lead AI
    - Backend Agent
    - Frontend Agent
    - Testing Agent
  flex:
    - Performance Agent  # Activated for performance sprint
    - Monitoring Agent   # Activated for performance sprint
```

### Step 2: Create Performance Tickets

```markdown
## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-050 | Optimize DB queries | performance | PENDING | - | - |
| PROJ-051 | Reduce bundle size | performance | PENDING | - | - |
| PROJ-052 | Add performance tests | test | PENDING | - | - |
| PROJ-053 | Cache API responses | performance | PENDING | - | - |
```

### Step 3: Team Picks Tickets

**Backend Developer** (human):
```markdown
| PROJ-050 | Optimize DB queries | performance | IN_PROGRESS | perf/proj-050-optimize-queries | Alice |
```

**Frontend AI Agent**:
```markdown
| PROJ-051 | Reduce bundle size | performance | IN_PROGRESS | perf/proj-051-reduce-bundle | Frontend Agent |
```

**Performance AI Agent**:
```markdown
| PROJ-052 | Add performance tests | test | IN_PROGRESS | feature/proj-052-perf-tests | Performance Agent |
```

### Step 4: Coordinated Development

All agents read updated AGENTS.md to see Performance Agent patterns:
```markdown
## Performance Agent (Flex Slot)

Active during: performance_optimization sprints

Focus areas:
- Identify performance bottlenecks
- Optimize database queries
- Reduce bundle sizes
- Improve render performance
- Add performance monitoring
```

### Step 5: Weekly Review

Team reviews PROJECT_STATUS.md:
```markdown
## ✅ Completed Tickets (Sprint 8)
| PROJ-050 | Optimize DB queries | 2025-11-05 | #52 |
| PROJ-051 | Reduce bundle size | 2025-11-06 | #53 |
| PROJ-052 | Add performance tests | 2025-11-07 | #54 |
```

**Result**: 3 performance improvements completed with coordinated effort

---

## Example 4: Handling Blocked Ticket

**Scenario**: AI agent discovers missing API keys during implementation

### Step 1: Agent Discovers Blocker

While implementing PROJ-060 (Payment integration):
```bash
$ pytest tests/test_payment.py
# Error: STRIPE_API_KEY environment variable not set
```

### Step 2: Update State to BLOCKED

AI edits PROJECT_STATUS.md:
```markdown
## 🎫 Active Tickets
| PROJ-060 | Payment integration | feature | IN_PROGRESS | feature/proj-060-payment | Backend Agent |

↓ Changes to ↓

## 🚧 Blocked Tickets
| ID | Title | Blocker | Since |
|----|-------|---------|-------|
| PROJ-060 | Payment integration | Waiting for Stripe API keys from DevOps | 2025-11-04 |

## 🔄 Recent Updates
- 2025-11-04: PROJ-060 blocked - need Stripe API keys
```

### Step 3: Pick Different Ticket

AI reads PROJECT_STATUS.md again:
```markdown
| PROJ-061 | User dashboard | feature | PENDING | - | - |
```

Starts work on PROJ-061 instead.

### Step 4: Blocker Resolved

DevOps provides API keys. Human updates PROJECT_STATUS.md:
```markdown
## 🎫 Active Tickets
| PROJ-060 | Payment integration | feature | IN_PROGRESS | feature/proj-060-payment | Backend Agent |

## 🔄 Recent Updates
- 2025-11-05: PROJ-060 unblocked - API keys provided
```

### Step 5: AI Resumes Work

AI sees update, resumes PROJ-060:
```bash
$ git checkout feature/proj-060-payment
$ export STRIPE_API_KEY=sk_test_...
$ pytest tests/test_payment.py
# Tests pass ✓
```

---

## Example 5: Coordinated Feature (Multiple Agents)

**Scenario**: Implement user dashboard (requires backend + frontend)

### Step 1: Lead AI Breaks Down Feature

Reads PROJECT_STATUS.md, creates sub-tickets:
```markdown
| PROJ-070 | User dashboard | feature | IN_PROGRESS | - | Lead AI |
| PROJ-071 | Dashboard API endpoints | feature | PENDING | - | - |
| PROJ-072 | Dashboard UI components | feature | PENDING | - | - |
| PROJ-073 | Dashboard integration tests | test | PENDING | - | - |
```

### Step 2: Agents Pick Related Tickets

**Backend Agent**:
```markdown
| PROJ-071 | Dashboard API endpoints | feature | IN_PROGRESS | feature/proj-071-dashboard-api | Backend Agent |
```

**Frontend Agent**:
```markdown
| PROJ-072 | Dashboard UI components | feature | IN_PROGRESS | feature/proj-072-dashboard-ui | Frontend Agent |
```

**Testing Agent** (waits for others):
```markdown
| PROJ-073 | Dashboard integration tests | test | PENDING | - | - |
```

### Step 3: Parallel Development

**Backend Agent**:
```bash
$ git checkout -b feature/proj-071-dashboard-api
$ cat > src/api/dashboard.py
# API implementation
$ pytest tests/api/test_dashboard.py
$ git commit -m "feat(api): add dashboard endpoints"
```

**Frontend Agent** (simultaneously):
```bash
$ git checkout -b feature/proj-072-dashboard-ui
$ cat > src/components/Dashboard.tsx
# UI implementation
$ npm test src/components/Dashboard.test.tsx
$ git commit -m "feat(ui): add dashboard components"
```

### Step 4: Testing Agent Integrates

After both complete, Testing Agent:
```markdown
| PROJ-073 | Dashboard integration tests | test | IN_PROGRESS | feature/proj-073-dashboard-integration | Testing Agent |
```

```bash
$ git checkout -b feature/proj-073-dashboard-integration
$ cat > tests/integration/test_dashboard_full.py
# End-to-end tests
$ pytest tests/integration/test_dashboard_full.py
$ git commit -m "test(dashboard): add integration tests"
```

### Step 5: Lead AI Completes Parent

All sub-tickets done, Lead AI updates:
```markdown
## ✅ Completed Tickets
| PROJ-070 | User dashboard | 2025-11-08 | #60 |
| PROJ-071 | Dashboard API endpoints | 2025-11-06 | #57 |
| PROJ-072 | Dashboard UI components | 2025-11-07 | #58 |
| PROJ-073 | Dashboard integration tests | 2025-11-08 | #59 |
```

**Result**: Complex feature completed through coordinated effort

---

## Common Patterns Summary

### Starting Work
1. Read PROJECT_STATUS.md
2. Update ticket → IN_PROGRESS
3. Create branch
4. Follow TDD
5. Commit
6. Update state → COMPLETED

### Bug Fixing
1. Create/find bug ticket
2. Update → IN_PROGRESS
3. Write failing test (reproduce bug)
4. Fix bug
5. Commit with `fix(scope):`
6. Update → COMPLETED

### Blocked Work
1. Identify blocker
2. Update → BLOCKED
3. Document blocker reason
4. Pick different ticket
5. When resolved → IN_PROGRESS
6. Resume work

### Coordinated Features
1. Lead AI breaks down feature
2. Agents pick sub-tickets
3. Parallel development
4. Integration by Testing Agent
5. Lead AI completes parent

---

## Next Steps

- **Learn fundamentals**: [Template Basics](01-template-basics.md)
- **AI agent guide**: [AI Agent Usage](02-ai-agent-usage.md)
- **Human workflows**: [How Humans Use Templates](03-human-usage.md)
- **Having issues?**: [Troubleshooting](05-troubleshooting.md)

---

[← Back: Human Usage](03-human-usage.md) | [Template Guide](../TEMPLATE_GUIDE.md) | [Next: Troubleshooting →](05-troubleshooting.md)
