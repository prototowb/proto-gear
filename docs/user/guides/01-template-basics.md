# Template Basics

**Part of**: [Template-Based Collaboration Guide](../TEMPLATE_GUIDE.md)
**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04

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

````markdown
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
````

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
````markdown
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
````

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

## How Templates Enable Collaboration

### Shared Understanding

**Before Proto Gear**:
- Human: "Add authentication"
- AI: "How should I structure it? What's the git workflow? Testing approach?"
- Human: *Explains everything from scratch*

**With Proto Gear Templates**:
- Human: "Add authentication following our patterns"
- AI: *Reads AGENTS.md, BRANCHING.md, TESTING.md*
- AI: *Knows role, git conventions, TDD approach*
- AI: *Creates branch, writes tests, implements, commits with conventional format*

### Consistency

All agents (human and AI) follow the same patterns:
- Same branch naming
- Same commit message format
- Same testing approach
- Same state tracking

### Coordination

PROJECT_STATUS.md enables coordination:
- See what others are working on
- Avoid duplicate work
- Track dependencies
- Update progress

---

## Next Steps

Now that you understand the basics:

- **AI Agents**: Read [AI Agent Usage Guide](02-ai-agent-usage.md)
- **Humans**: Read [How Humans Use Templates](03-human-usage.md)
- **Examples**: Check [Workflow Examples](04-workflow-examples.md)
- **Issues**: See [Troubleshooting](05-troubleshooting.md)

---

[← Back to Template Guide](../TEMPLATE_GUIDE.md) | [Next: AI Agent Usage →](02-ai-agent-usage.md)
