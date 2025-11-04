# Template-Based Collaboration Guide

**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04
**Audience**: Developers, AI Agents, Project Managers

---

## Table of Contents

1. [What is Template-Based Collaboration?](#what-is-template-based-collaboration)
2. [Core Concepts](#core-concepts)
3. [Template Files Explained](#template-files-explained)
4. [How AI Agents Use Templates](#how-ai-agents-use-templates)
5. [How Humans Use Templates](#how-humans-use-templates)
6. [Template Patterns vs. Executable Code](#template-patterns-vs-executable-code)
7. [Workflow Examples](#workflow-examples)
8. [Best Practices](#best-practices)
9. [Common Patterns](#common-patterns)
10. [Troubleshooting](#troubleshooting)

---

## What is Template-Based Collaboration?

Template-based collaboration is a paradigm where **structured markdown templates** provide shared context and patterns that enable humans and AI agents to work together naturally using native development tools.

### Key Principle

**Proto Gear does NOT execute code automatically**. Instead, it generates templates that:
- Describe decision-making patterns
- Provide workflow guidance
- Define conventions and standards
- Track project state
- Enable natural language collaboration

### The Shift

**❌ Old Approach (Python Orchestration)**:
```python
# AI agents call Python functions
orchestrator = WorkflowOrchestrator()
orchestrator.run_workflow()
```

**✅ New Approach (Template-Based)**:
```markdown
# AI agents read patterns and use native tools
## Workflow Pattern

1. Read PROJECT_STATUS.md for context
2. Use git to create branch
3. Follow TDD patterns from TESTING.md
4. Update state in PROJECT_STATUS.md
```

---

## Core Concepts

### 1. Templates as Shared Context

Templates provide a **single source of truth** that both humans and AI agents read to understand:
- What roles exist (AGENTS.md)
- What work is in progress (PROJECT_STATUS.md)
- How to use git (BRANCHING.md)
- How to write tests (TESTING.md)

### 2. Natural Language Patterns

Code blocks in templates are **illustrative patterns**, not executable Python:

```markdown
## Example Pattern (from AGENTS.md)

```python
def lead_ai_workflow():
    """
    This is a PATTERN for decision-making, not a function to call.
    Lead AI should:
    1. Read PROJECT_STATUS.md
    2. Identify next highest-priority ticket
    3. Update ticket status to IN_PROGRESS
    4. Create git branch using native tools
    """
```
```

**Key**: AI agents read this pattern and use their judgment to execute equivalent actions with native tools.

### 3. Native Tools

AI agents use **native development tools** like:
- `git checkout -b feature/PROJ-001-description`
- `pytest --cov=src tests/`
- `npm run build`
- `docker-compose up`

They do NOT call Proto Gear's Python APIs.

### 4. State Tracking

PROJECT_STATUS.md is updated manually by agents as work progresses:
- Ticket status changes (PENDING → IN_PROGRESS → COMPLETED)
- Sprint type updates
- Recent updates log

---

## Template Files Explained

### AGENTS.md - Agent Role Patterns

**Purpose**: Defines agent roles and decision-making patterns

**Structure**:
```markdown
# AI Agent Integration Guide

## 📖 How to Use This Document
(Explains that code blocks are patterns, not executable code)

## 🤖 Agent System Architecture
(Describes 4 core + 2 flex agent model)

## 🎯 Core Agents
(Lead AI, Backend, Frontend, Testing patterns)

## 🔄 Flex Agent Slots
(Sprint-based agent patterns)

## 📋 Lead AI Workflow
(Decision-making patterns for coordination)
```

**Key Sections**:
1. **How to Use** - Critical clarification about patterns
2. **Agent Roles** - What each agent focuses on
3. **Decision Patterns** - How agents make choices
4. **Workflow Examples** - Common scenarios

**AI agents use this to**:
- Understand their role
- See decision-making patterns
- Coordinate with other agents
- Follow project-specific conventions

### PROJECT_STATUS.md - State Tracker

**Purpose**: Single source of truth for project state

**Structure**:
```yaml
# Current State
project_phase: "Development"
current_sprint: 1
current_branch: "feature/PROJ-001-auth"
last_ticket_id: 5
ticket_prefix: "PROJ"
```

**Sections**:
1. **Active Tickets** - What's being worked on now
2. **Completed Tickets** - What's done
3. **Blocked Tickets** - What's stuck and why
4. **Sprint Configuration** - Current sprint type and agents
5. **Recent Updates** - Timeline of changes

**AI agents use this to**:
- Understand current work
- See what's available to work on
- Update status as they complete tasks
- Coordinate with other agents

### BRANCHING.md - Git Workflow Patterns

**Purpose**: Git conventions and workflow patterns

**Structure**:
```markdown
# Branch Naming Conventions
feature/PREFIX-XXX-description
bugfix/PREFIX-XXX-description
hotfix/vX.Y.Z-issue

# Conventional Commit Format
type(scope): subject

# Workflow Examples
(Step-by-step patterns for common tasks)
```

**AI agents use this to**:
- Name branches correctly
- Write conventional commit messages
- Follow git workflow patterns
- Create proper pull requests

### TESTING.md - TDD Patterns

**Purpose**: Testing conventions and TDD workflow

**Structure**:
```markdown
# Red-Green-Refactor Cycle
(Step-by-step TDD pattern)

# Test Pyramid
Unit Tests (many)
Integration Tests (some)
E2E Tests (few)

# Coverage Targets
(Project-specific coverage goals)

# CI/CD Integration
(Testing in automation)
```

**AI agents use this to**:
- Follow TDD workflow
- Write appropriate test types
- Meet coverage targets
- Integrate with CI/CD

---

## How AI Agents Use Templates

### Step 1: Initial Context Gathering

When starting work, AI agents read:
1. **AGENTS.md** - Understand role and patterns
2. **PROJECT_STATUS.md** - See current state
3. **BRANCHING.md** (if exists) - Learn git conventions
4. **TESTING.md** (if exists) - Understand test requirements

### Step 2: Pattern Following

AI agents interpret patterns and execute with judgment:

**Template Pattern**:
```markdown
## Starting New Feature Work

1. Read PROJECT_STATUS.md to find pending tickets
2. Select highest priority ticket
3. Update ticket status to IN_PROGRESS
4. Create branch: feature/PREFIX-XXX-description
5. Follow TDD: write test first, then implementation
6. Commit with conventional format
7. Update PROJECT_STATUS.md when complete
```

**AI Agent Actions**:
```bash
# Agent reads PROJECT_STATUS.md (native file read)
$ cat PROJECT_STATUS.md

# Agent decides ticket PROJ-001 is next

# Agent updates PROJECT_STATUS.md (native file edit)
# Changes: | PROJ-001 | Add auth | feature | PENDING | - | - |
# To:      | PROJ-001 | Add auth | feature | IN_PROGRESS | feature/proj-001-add-auth | Agent AI |

# Agent creates branch (native git)
$ git checkout -b feature/proj-001-add-auth

# Agent writes test (native file creation)
$ cat > tests/test_auth.py
def test_user_login():
    # Test implementation

# Agent runs test (native pytest)
$ pytest tests/test_auth.py

# ... continues following TDD pattern
```

### Step 3: State Updates

As work progresses, agents update PROJECT_STATUS.md:
- Mark tickets IN_PROGRESS when starting
- Add branch names when created
- Mark COMPLETED when done
- Add to recent updates timeline

### Step 4: Coordination

Multiple agents coordinate via PROJECT_STATUS.md:
- See what others are working on
- Avoid duplicate work
- Track dependencies
- Follow sprint type patterns

---

## How Humans Use Templates

### For Solo Developers

1. **Share context with AI assistant**:
   ```
   "I've set up Proto Gear. Please read AGENTS.md and PROJECT_STATUS.md
   to understand the project state."
   ```

2. **Request work following patterns**:
   ```
   "Following the patterns in TESTING.md, please implement authentication
   with TDD workflow."
   ```

3. **Track progress**:
   - Review PROJECT_STATUS.md for current state
   - Update tickets as you complete work
   - Keep recent updates log current

### For Teams

1. **Shared understanding**:
   - All team members read same templates
   - Humans and AI agents follow same conventions
   - PROJECT_STATUS.md tracks everyone's work

2. **Consistent workflows**:
   - BRANCHING.md ensures consistent git usage
   - TESTING.md ensures consistent test quality
   - AGENTS.md defines clear responsibilities

3. **Collaboration**:
   - Humans update PROJECT_STATUS.md
   - AI agents read and follow
   - Everyone uses native tools

---

## Template Patterns vs. Executable Code

### Understanding the Difference

**Executable Code** (What Proto Gear Does NOT Do):
```python
# This is actual Python code that gets executed
class WorkflowOrchestrator:
    def run(self):
        ticket = self.get_next_ticket()
        branch = self.create_branch(ticket)
        subprocess.run(['git', 'checkout', '-b', branch])
```

**Template Pattern** (What Proto Gear Does):
```markdown
## Workflow Pattern

```python
def workflow_pattern():
    """
    PATTERN for AI agents to follow:
    1. Read PROJECT_STATUS.md to find next ticket
    2. Determine appropriate branch name
    3. Use native git to create branch
    """
```

AI agents see this and execute:
```bash
$ cat PROJECT_STATUS.md  # Read state
$ git checkout -b feature/proj-001-auth  # Native tool
```
```

### Why Patterns Instead of Code?

1. **Flexibility**: AI agents use judgment based on context
2. **Tool Agnostic**: Works with git, pytest, npm, docker, etc.
3. **Natural**: AI agents already excel at following natural language instructions
4. **Maintainability**: Easier to update markdown than Python APIs
5. **Accessibility**: Non-programmers can read and understand patterns

### Key Indicators of Patterns

When you see these in templates, they're patterns:

- ✅ **Docstrings** explaining intent: `"""This describes a pattern..."""`
- ✅ **Step-by-step lists**: `1. Do this, 2. Then this`
- ✅ **Pseudocode**: `function_name()` without actual implementation
- ✅ **Examples**: "For instance, run: `git checkout -b ...`"
- ✅ **Decision trees**: "If X, then Y, else Z"

When you see these, they're executable:

- ❌ **Imports**: `from module import Class`
- ❌ **Actual implementations**: `subprocess.run(['git', 'checkout'])`
- ❌ **Class instantiation**: `obj = MyClass()`
- ❌ **Function calls**: `result = do_something()`

---

## Workflow Examples

### Example 1: Starting New Feature (AI Agent)

**Scenario**: AI agent needs to start working on authentication feature

**Steps**:

1. **Read Context**:
```bash
$ cat PROJECT_STATUS.md
# Sees: | PROJ-001 | Add user auth | feature | PENDING | - | - |
```

2. **Update Status**:
```bash
# AI edits PROJECT_STATUS.md
# Changes PENDING → IN_PROGRESS
# Adds branch name and assignee
```

3. **Create Branch** (follows BRANCHING.md pattern):
```bash
$ git checkout -b feature/proj-001-add-user-auth
```

4. **Follow TDD** (follows TESTING.md pattern):
```bash
# Write test first
$ cat > tests/test_auth.py
def test_user_can_login():
    # Test implementation

# Run test (expect RED)
$ pytest tests/test_auth.py

# Write implementation
$ cat > src/auth.py
class AuthService:
    # Implementation

# Run test (expect GREEN)
$ pytest tests/test_auth.py

# Refactor if needed
```

5. **Commit** (follows BRANCHING.md pattern):
```bash
$ git add tests/test_auth.py src/auth.py
$ git commit -m "feat(auth): add user login functionality

Implements basic authentication with username and password.
Test coverage: 100% for auth module.

Closes PROJ-001"
```

6. **Update State**:
```bash
# AI edits PROJECT_STATUS.md
# Moves ticket to Completed Tickets section
# Adds entry to Recent Updates
```

### Example 2: Bug Fix (Human with AI Assistant)

**Scenario**: Human developer finds bug, asks AI assistant to fix

**Human**:
```
"There's a bug in the login form - it doesn't validate email format.
Please fix this following our TDD workflow from TESTING.md and update PROJECT_STATUS.md."
```

**AI Assistant Actions**:

1. Reads TESTING.md to understand TDD pattern
2. Reads PROJECT_STATUS.md to get next ticket ID
3. Creates new ticket entry in PROJECT_STATUS.md:
   ```
   | PROJ-006 | Fix email validation | bugfix | IN_PROGRESS | bugfix/proj-006-email-validation | AI Assistant |
   ```
4. Creates branch following BRANCHING.md pattern:
   ```bash
   $ git checkout -b bugfix/proj-006-email-validation
   ```
5. Follows TDD (RED-GREEN-REFACTOR):
   ```bash
   # Write failing test
   $ cat >> tests/test_auth.py
   def test_email_validation():
       assert validate_email("invalid") == False
       assert validate_email("valid@example.com") == True

   # Run test (RED)
   $ pytest tests/test_auth.py::test_email_validation

   # Fix implementation
   $ vim src/auth.py

   # Run test (GREEN)
   $ pytest tests/test_auth.py::test_email_validation
   ```
6. Commits following convention:
   ```bash
   $ git commit -m "fix(auth): add email format validation

   Email validation was missing, allowing invalid email formats.
   Added regex pattern validation for RFC 5322 format.

   Closes PROJ-006"
   ```
7. Updates PROJECT_STATUS.md to COMPLETED

### Example 3: Sprint Planning (Team)

**Scenario**: Team starts new sprint focused on performance

**Steps**:

1. **Update PROJECT_STATUS.md**:
```yaml
sprint_type: "performance_optimization"
active_agents:
  core:
    - Lead AI
    - Backend Agent
    - Frontend Agent
    - Testing Agent
  flex:
    - Performance Agent  # Activated for this sprint
    - Monitoring Agent   # Activated for this sprint
```

2. **Performance Agent Pattern** (from AGENTS.md):
```markdown
## Performance Agent (Flex Slot)

Active during: performance_optimization sprints

Focus areas:
- Identify performance bottlenecks
- Optimize database queries
- Reduce bundle sizes
- Improve render performance
- Add performance tests
```

3. **All agents** (human and AI) now follow performance-focused patterns:
- Review AGENTS.md to see Performance Agent is active
- Prioritize performance-related tickets
- Use performance testing tools
- Follow performance best practices

---

## Best Practices

### For Template Creators

1. **Be Clear About Patterns**:
   - Always include "How to Use" sections
   - Clarify when code blocks are patterns
   - Provide concrete examples

2. **Use Consistent Structure**:
   - Follow established template formats
   - Use clear section headings
   - Include table of contents for long docs

3. **Keep Templates Updated**:
   - Update PROJECT_STATUS.md regularly
   - Keep Recent Updates current
   - Archive old completed tickets

4. **Provide Context**:
   - Explain why patterns exist
   - Give examples of correct usage
   - Show anti-patterns to avoid

### For AI Agents

1. **Always Read First**:
   - Read AGENTS.md for role clarity
   - Read PROJECT_STATUS.md for current state
   - Read workflow templates before starting work

2. **Use Native Tools**:
   - Execute git, pytest, npm, docker directly
   - Don't try to import Proto Gear modules
   - Use your judgment and capabilities

3. **Update State Regularly**:
   - Mark tickets IN_PROGRESS when starting
   - Update PROJECT_STATUS.md when completing work
   - Add to Recent Updates timeline

4. **Follow Patterns, Not Code**:
   - Interpret patterns with context
   - Adapt to specific situations
   - Ask for clarification if unclear

### For Humans

1. **Share Templates with AI**:
   - Provide template files to AI assistants
   - Reference specific sections when requesting work
   - Keep templates in project repository

2. **Maintain State**:
   - Update PROJECT_STATUS.md when you complete work
   - Keep ticket status current
   - Log significant changes

3. **Follow Conventions**:
   - Use BRANCHING.md conventions in your own work
   - Follow TESTING.md patterns
   - Maintain consistency

4. **Communicate Changes**:
   - Update templates when workflows change
   - Document new patterns
   - Share updates with team and AI assistants

---

## Common Patterns

### Pattern: Coordinated Feature Development

**Scenario**: Multiple agents working on related features

**Pattern** (from AGENTS.md):
```markdown
## Coordinated Development Pattern

1. Lead AI reviews PROJECT_STATUS.md
2. Identifies related tickets that can be parallelized
3. Assigns tickets to appropriate agents
4. Each agent:
   - Updates status to IN_PROGRESS
   - Creates branch
   - Follows TDD workflow
   - Commits with conventional format
5. Lead AI coordinates integration
6. All agents update PROJECT_STATUS.md when complete
```

**Implementation**:
- Backend Agent works on API endpoints
- Frontend Agent works on UI components
- Testing Agent writes integration tests
- All follow same BRANCHING.md and TESTING.md patterns
- PROJECT_STATUS.md shows all parallel work

### Pattern: Blocked Ticket Management

**Pattern** (from PROJECT_STATUS.md):
```markdown
## Blocked Ticket Workflow

PENDING → IN_PROGRESS → BLOCKED
   ↓
(Blocker resolved)
   ↓
IN_PROGRESS → COMPLETED
```

**Implementation**:
```markdown
| ID | Title | Blocker | Since |
|----|-------|---------|-------|
| PROJ-010 | Add payment | Waiting for API keys | 2025-11-01 |
```

When blocker is resolved:
1. Update status back to IN_PROGRESS
2. Add note in Recent Updates
3. Resume work following patterns

### Pattern: Sprint Type Change

**Pattern** (from PROJECT_STATUS.md):
```markdown
## Sprint Type Changes

When sprint type changes:
1. Update sprint_type in PROJECT_STATUS.md
2. Update flex agent slots based on new type
3. All agents read updated AGENTS.md
4. Agents adapt focus areas to new sprint type
```

**Example**:
```yaml
# Change from feature_development to bug_fixing
sprint_type: "bug_fixing"
active_agents:
  flex:
    - Testing Agent (moved to flex for extra testing focus)
    - Debug Agent (activated for bug fixing)
```

---

## Troubleshooting

### Problem: AI Agent Tries to Import Proto Gear Modules

**Symptom**:
```python
from proto_gear.agent_framework import WorkflowOrchestrator
# ImportError or ModuleNotFoundError
```

**Solution**:
1. Remind the AI agent that code blocks in templates are patterns
2. Point to the "How to Use This Document" section in AGENTS.md
3. Clarify that native tools should be used instead

**Correct Approach**:
```bash
# AI reads patterns from AGENTS.md
# AI uses native git commands
$ git checkout -b feature/proj-001-auth
```

### Problem: PROJECT_STATUS.md Not Updated

**Symptom**:
- Tickets show as PENDING but work is done
- Recent Updates section is empty
- State doesn't match reality

**Solution**:
1. Review completed work
2. Manually update PROJECT_STATUS.md
3. Establish pattern of updating state regularly
4. Add reminders in AGENTS.md workflow patterns

**Prevention**:
```markdown
## Workflow Pattern (from AGENTS.md)

IMPORTANT: After completing ANY task:
1. Update ticket status in PROJECT_STATUS.md
2. Add entry to Recent Updates
3. Move completed ticket to Completed Tickets section
```

### Problem: Inconsistent Branch Naming

**Symptom**:
- Some branches follow pattern, others don't
- Ticket IDs missing from branch names
- Mixed conventions (kebab-case vs snake_case)

**Solution**:
1. Review BRANCHING.md conventions
2. Ensure all team members (human and AI) read it
3. Update existing branches if needed
4. Add examples to BRANCHING.md

**Example** (from BRANCHING.md):
```markdown
## Branch Naming Examples

✅ CORRECT:
- feature/PROJ-001-add-user-auth
- bugfix/PROJ-042-fix-login-error
- hotfix/v1.2.3-security-patch

❌ INCORRECT:
- feature/add-auth (missing ticket ID)
- PROJ-001-auth (missing type prefix)
- fix_login (wrong separator, missing ticket)
```

### Problem: Template Patterns Unclear

**Symptom**:
- AI agents confused about what to do
- Humans uncertain about workflows
- Inconsistent execution

**Solution**:
1. Add more examples to templates
2. Clarify that code blocks are patterns
3. Provide step-by-step workflows
4. Include anti-patterns (what NOT to do)

**Template Improvement**:
```markdown
## ❌ Anti-Pattern: Do NOT Try to Execute Template Code

```python
# This is a PATTERN, not executable code
def workflow():
    """Do NOT try to run this function"""
    pass

# ❌ WRONG: Trying to execute
from templates import workflow
workflow()  # This won't work!
```

## ✅ Correct Pattern: Read and Use Native Tools

```bash
# Read the pattern
$ cat AGENTS.md

# Use native tools based on pattern
$ git checkout -b feature/proj-001
$ pytest tests/
```
```

---

## Summary

Template-based collaboration enables humans and AI agents to work together naturally by:

1. **Shared Context**: Templates provide single source of truth
2. **Natural Language**: Patterns described in markdown
3. **Native Tools**: AI agents use git, pytest, npm, etc.
4. **Flexible Execution**: Agents apply judgment and adapt
5. **State Tracking**: PROJECT_STATUS.md tracks progress

**Key Principles**:
- ✅ Templates are guides, not executable code
- ✅ Code blocks in templates are illustrative patterns
- ✅ AI agents use native development tools
- ✅ PROJECT_STATUS.md is the single source of truth
- ✅ Humans and AI follow same conventions

**Benefits**:
- Consistency across human and AI work
- Clear communication via shared documentation
- Flexibility to adapt patterns to context
- Tool-agnostic workflows
- Natural language collaboration

---

**For More Information**:
- [README.md](../README.md) - Project overview
- [AGENTS.template.md](../core/AGENTS.template.md) - Agent pattern template
- [PROJECT_STATUS.template.md](../core/PROJECT_STATUS.template.md) - State tracking template
- [BRANCHING.template.md](../core/BRANCHING.template.md) - Git workflow patterns
- [TESTING.template.md](../core/TESTING.template.md) - TDD workflow patterns
- [READINESS_ASSESSMENT.md](./READINESS_ASSESSMENT.md) - Current project state

**Questions or Issues?**
- Check [Troubleshooting](#troubleshooting) section above
- Review template examples in templates
- Open an issue on GitHub

---

**Document Version**: 1.0.0
**Created**: 2025-11-04
**Last Updated**: 2025-11-04
