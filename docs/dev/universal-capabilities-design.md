# Universal Agent Capabilities System - Design Document

**Version**: 1.0
**Date**: 2025-11-04
**Status**: Design Phase
**Target Release**: Proto Gear v0.4.0

---

## Executive Summary

This document defines a **universal, platform-agnostic capability system** for Proto Gear that enables ANY AI agent (Claude, GPT, Gemini, Llama, etc.) to discover and utilize modular patterns for common development tasks. Unlike Claude Code's proprietary Skills system, this approach uses pure markdown files organized in a filesystem hierarchy that works across all AI platforms.

**Core Philosophy**: Capabilities are **discovered patterns**, not executed code. AI agents read markdown templates and use their native tools (git, pytest, npm) to accomplish tasks following documented workflows.

---

## Table of Contents

1. [Problem Statement](#problem-statement)
2. [Design Principles](#design-principles)
3. [Architecture Overview](#architecture-overview)
4. [Capability Types](#capability-types)
5. [Directory Structure](#directory-structure)
6. [Metadata Format](#metadata-format)
7. [Discovery Mechanism](#discovery-mechanism)
8. [Capability Examples](#capability-examples)
9. [Integration with Existing Templates](#integration-with-existing-templates)
10. [Implementation Roadmap](#implementation-roadmap)

---

## Problem Statement

### Current State
Proto Gear generates **passive documentation** (AGENTS.md, PROJECT_STATUS.md, BRANCHING.md, TESTING.md) that AI agents must be explicitly told to read. These templates work well but lack:

1. **Automatic discovery** - Agents don't know what capabilities exist
2. **Modularity** - All patterns bundled into monolithic files
3. **Reusability** - No way to share specific workflows across projects
4. **Progressive loading** - Agents load everything or nothing
5. **Context-aware activation** - Capabilities not matched to current task

### Desired State
A **universal capability system** that provides:

1. **Automatic discovery** - Agents can explore available capabilities
2. **Modular patterns** - Single-purpose, focused capabilities
3. **Platform-agnostic** - Works with ANY AI agent, not just Claude
4. **Progressive disclosure** - Load only what's relevant
5. **Natural language** - Patterns described, not code executed
6. **Filesystem-based** - Simple markdown files, git-friendly

---

## Design Principles

### 1. Universal Compatibility
- **Pure markdown** - No proprietary formats
- **Human-readable** - Developers can read and edit
- **Platform-agnostic** - Works across all AI agents
- **No execution** - Patterns guide agents, not Python code

### 2. Natural Language First
- **Descriptive patterns** - How to approach tasks
- **Decision flows** - When to use different strategies
- **Example workflows** - Concrete demonstrations
- **Code as illustration** - Shows patterns, not executable scripts

### 3. Filesystem as Interface
- **Directory structure** - Organizes capabilities by domain
- **Convention over configuration** - Predictable layout
- **Git-friendly** - Plain text, version-controlled
- **Self-documenting** - Structure reveals purpose

### 4. Progressive Disclosure
- **Lightweight index** - Quick capability overview
- **Load on demand** - Read only what's needed
- **Hierarchical** - General → specific patterns
- **Composable** - Capabilities reference each other

### 5. Integration with Existing System
- **Extends templates** - Works with AGENTS.md, PROJECT_STATUS.md
- **Single source of truth** - PROJECT_STATUS.md remains authoritative
- **Backward compatible** - Existing templates still work
- **Opt-in** - Projects choose which capabilities to include

---

## Architecture Overview

### High-Level Structure

```
project-root/
├── AGENTS.md                          # Root agent configuration (existing)
├── PROJECT_STATUS.md                  # Single source of truth (existing)
├── BRANCHING.md                       # Git workflow (existing, optional)
├── TESTING.md                         # TDD patterns (existing, optional)
│
└── .proto-gear/                       # Proto Gear capability system
    ├── INDEX.md                       # Master capability index
    │
    ├── skills/                        # Modular capabilities
    │   ├── INDEX.md                   # Skills index
    │   ├── testing/
    │   │   ├── SKILL.md               # TDD workflow skill
    │   │   └── examples/              # Optional examples
    │   ├── git-workflow/
    │   │   ├── SKILL.md               # Git branching skill
    │   │   └── examples/
    │   └── debugging/
    │       └── SKILL.md               # Debugging patterns skill
    │
    ├── workflows/                     # Multi-step task patterns
    │   ├── INDEX.md                   # Workflows index
    │   ├── feature-development.md
    │   ├── bug-fix.md
    │   ├── refactoring.md
    │   └── performance-optimization.md
    │
    ├── commands/                      # Single-action patterns
    │   ├── INDEX.md                   # Commands index
    │   ├── create-ticket.md
    │   ├── start-sprint.md
    │   ├── review-pr.md
    │   └── run-tests.md
    │
    └── agents/                        # Specialized agent patterns
        ├── INDEX.md                   # Agent specializations index
        ├── backend/
        │   ├── AGENT.md               # Backend specialist
        │   └── patterns/
        ├── frontend/
        │   ├── AGENT.md               # Frontend specialist
        │   └── patterns/
        └── testing/
            ├── AGENT.md               # Testing specialist
            └── patterns/
```

### Design Rationale

#### Why `.proto-gear/` Directory?
1. **Namespacing** - Avoids conflicts with project files
2. **Hidden by default** - Doesn't clutter project root
3. **Convention** - Similar to `.github/`, `.vscode/`
4. **Bundled** - All capabilities in one place
5. **Optional** - Projects can omit if not needed

#### Why INDEX.md Files?
1. **Fast discovery** - Agents scan index instead of full directory
2. **Metadata** - Categorization, relevance scoring
3. **Human-readable** - Developers understand structure
4. **Extensible** - Easy to add new capabilities

---

## Capability Types

Proto Gear defines **four types of capabilities**, each serving a distinct purpose:

### 1. Skills
**Purpose**: Modular, reusable expertise in a specific domain

**Characteristics**:
- Self-contained knowledge areas
- Can be activated when relevant
- May include sub-patterns and examples
- Similar to Claude Code skills but platform-agnostic

**Examples**:
- `skills/testing/` - TDD methodology, test patterns
- `skills/git-workflow/` - Branching, commits, PRs
- `skills/debugging/` - Troubleshooting patterns
- `skills/performance/` - Optimization techniques
- `skills/security/` - Security best practices

**File Structure**:
```
skills/{skill-name}/
├── SKILL.md              # Main skill definition
├── patterns/             # Optional sub-patterns
│   ├── pattern-1.md
│   └── pattern-2.md
└── examples/             # Optional concrete examples
    ├── example-1.md
    └── example-2.md
```

---

### 2. Workflows
**Purpose**: Multi-step processes for accomplishing larger tasks

**Characteristics**:
- Sequential or branching steps
- Orchestrates multiple skills
- Defines decision points
- Provides complete task guidance

**Examples**:
- `feature-development.md` - Complete feature workflow
- `bug-fix.md` - Debugging and fixing workflow
- `refactoring.md` - Safe refactoring process
- `deployment.md` - Release preparation workflow
- `onboarding.md` - New contributor workflow

**File Structure**: Single markdown file per workflow

---

### 3. Commands
**Purpose**: Single-action patterns for discrete tasks

**Characteristics**:
- Atomic operations
- Quick reference
- Often used within workflows
- Minimal context needed

**Examples**:
- `create-ticket.md` - Create and document ticket
- `start-sprint.md` - Initialize sprint process
- `review-pr.md` - PR review checklist
- `run-tests.md` - Execute test suite
- `update-status.md` - Modify PROJECT_STATUS.md

**File Structure**: Single markdown file per command

---

### 4. Agents (Specialized)
**Purpose**: Domain-specific agent patterns and expertise

**Characteristics**:
- Extends core agents from AGENTS.md
- Domain-specific decision patterns
- Specialized workflows
- Technology-specific knowledge

**Examples**:
- `agents/backend/` - Server-side patterns
- `agents/frontend/` - UI/UX patterns
- `agents/testing/` - QA specialization
- `agents/devops/` - Infrastructure patterns
- `agents/security/` - Security specialization

**File Structure**:
```
agents/{agent-type}/
├── AGENT.md              # Agent specialization definition
├── patterns/             # Domain-specific patterns
│   ├── pattern-1.md
│   └── pattern-2.md
└── workflows/            # Agent-specific workflows
    ├── workflow-1.md
    └── workflow-2.md
```

---

## Directory Structure

### Complete Filesystem Layout

```
project-root/
│
├── AGENTS.md                          # Root agent guide (existing)
├── PROJECT_STATUS.md                  # State tracker (existing)
├── BRANCHING.md                       # Git workflow (optional, existing)
├── TESTING.md                         # TDD patterns (optional, existing)
│
└── .proto-gear/                       # Capability system root
    │
    ├── INDEX.md                       # Master index - start here
    │
    ├── skills/                        # Modular expertise
    │   ├── INDEX.md                   # Skills catalog
    │   │
    │   ├── testing/                   # TDD skill
    │   │   ├── SKILL.md
    │   │   ├── patterns/
    │   │   │   ├── unit-testing.md
    │   │   │   ├── integration-testing.md
    │   │   │   └── e2e-testing.md
    │   │   └── examples/
    │   │       └── red-green-refactor-example.md
    │   │
    │   ├── git-workflow/              # Git skill
    │   │   ├── SKILL.md
    │   │   ├── patterns/
    │   │   │   ├── feature-branch.md
    │   │   │   ├── hotfix-branch.md
    │   │   │   └── merge-strategies.md
    │   │   └── examples/
    │   │       └── conventional-commits-example.md
    │   │
    │   ├── debugging/                 # Debug skill
    │   │   ├── SKILL.md
    │   │   └── patterns/
    │   │       ├── systematic-debugging.md
    │   │       ├── log-analysis.md
    │   │       └── stack-trace-reading.md
    │   │
    │   ├── performance/               # Performance skill
    │   │   ├── SKILL.md
    │   │   └── patterns/
    │   │       ├── profiling.md
    │   │       ├── optimization.md
    │   │       └── benchmarking.md
    │   │
    │   └── security/                  # Security skill
    │       ├── SKILL.md
    │       └── patterns/
    │           ├── code-review-security.md
    │           ├── owasp-top-10.md
    │           └── secure-coding.md
    │
    ├── workflows/                     # Multi-step processes
    │   ├── INDEX.md                   # Workflows catalog
    │   ├── feature-development.md     # Complete feature workflow
    │   ├── bug-fix.md                 # Debug and fix workflow
    │   ├── refactoring.md             # Safe refactoring workflow
    │   ├── performance-optimization.md # Perf improvement workflow
    │   ├── security-review.md         # Security audit workflow
    │   └── deployment.md              # Release workflow
    │
    ├── commands/                      # Single-action patterns
    │   ├── INDEX.md                   # Commands catalog
    │   ├── create-ticket.md           # Create documented ticket
    │   ├── start-sprint.md            # Initialize sprint
    │   ├── create-branch.md           # Branch creation pattern
    │   ├── commit-changes.md          # Conventional commit pattern
    │   ├── review-pr.md               # PR review checklist
    │   ├── run-tests.md               # Test execution pattern
    │   ├── update-status.md           # PROJECT_STATUS.md update
    │   └── generate-docs.md           # Documentation generation
    │
    └── agents/                        # Specialized agent patterns
        ├── INDEX.md                   # Agent specializations catalog
        │
        ├── backend/                   # Backend specialist
        │   ├── AGENT.md
        │   ├── patterns/
        │   │   ├── api-design.md
        │   │   ├── database-patterns.md
        │   │   └── error-handling.md
        │   └── workflows/
        │       ├── api-development.md
        │       └── database-migration.md
        │
        ├── frontend/                  # Frontend specialist
        │   ├── AGENT.md
        │   ├── patterns/
        │   │   ├── component-design.md
        │   │   ├── state-management.md
        │   │   └── responsive-design.md
        │   └── workflows/
        │       ├── ui-development.md
        │       └── component-testing.md
        │
        ├── testing/                   # Testing specialist
        │   ├── AGENT.md
        │   ├── patterns/
        │   │   ├── test-strategy.md
        │   │   ├── coverage-analysis.md
        │   │   └── test-doubles.md
        │   └── workflows/
        │       ├── test-suite-creation.md
        │       └── test-debugging.md
        │
        ├── devops/                    # DevOps specialist
        │   ├── AGENT.md
        │   ├── patterns/
        │   │   ├── ci-cd-patterns.md
        │   │   ├── containerization.md
        │   │   └── monitoring.md
        │   └── workflows/
        │       ├── deployment-pipeline.md
        │       └── infrastructure-setup.md
        │
        └── security/                  # Security specialist
            ├── AGENT.md
            ├── patterns/
            │   ├── threat-modeling.md
            │   ├── vulnerability-scanning.md
            │   └── secure-defaults.md
            └── workflows/
                ├── security-audit.md
                └── penetration-testing.md
```

---

## Metadata Format

### Universal Metadata Standard

To work across ALL AI agents, metadata must be **platform-agnostic**. We use **YAML frontmatter** (widely supported) + markdown content.

### Core Metadata Fields

Every capability file includes:

```yaml
---
# Required fields
name: "Capability Name"
type: "skill|workflow|command|agent"
version: "1.0.0"
description: "Brief 1-2 sentence summary"

# Discovery fields
tags: ["keyword1", "keyword2", "keyword3"]
category: "testing|git|debugging|performance|security|..."
relevance:
  - trigger: "keyword or phrase that suggests this capability"
  - context: "when to consider this capability"

# Relationships
dependencies: ["other-capability-name"]  # Optional
related: ["similar-capability-name"]     # Optional

# Metadata
author: "Proto Gear Team"
last_updated: "2025-11-04"
status: "stable|beta|experimental"
---
```

### Metadata by Capability Type

#### Skills Metadata
```yaml
---
name: "Test-Driven Development"
type: "skill"
version: "1.0.0"
description: "TDD methodology with red-green-refactor cycle"
tags: ["testing", "tdd", "quality", "red-green-refactor"]
category: "testing"
relevance:
  - trigger: "write tests|testing|test coverage|tdd"
  - context: "Before implementing features, fixing bugs, or refactoring"
patterns:
  - "unit-testing.md"
  - "integration-testing.md"
  - "e2e-testing.md"
examples:
  - "red-green-refactor-example.md"
status: "stable"
---
```

#### Workflows Metadata
```yaml
---
name: "Feature Development Workflow"
type: "workflow"
version: "1.0.0"
description: "Complete workflow for building new features from concept to deployment"
tags: ["feature", "development", "workflow", "sprint"]
category: "development"
relevance:
  - trigger: "new feature|implement feature|build feature"
  - context: "Starting work on a new user-facing capability"
dependencies:
  - "skills/testing"
  - "skills/git-workflow"
  - "commands/create-ticket"
  - "commands/create-branch"
steps: 7
estimated_duration: "2-4 hours per feature"
status: "stable"
---
```

#### Commands Metadata
```yaml
---
name: "Create Ticket"
type: "command"
version: "1.0.0"
description: "Create and properly document a ticket in PROJECT_STATUS.md"
tags: ["ticket", "planning", "status", "documentation"]
category: "project-management"
relevance:
  - trigger: "create ticket|new ticket|add ticket"
  - context: "When starting any new work item"
dependencies:
  - "PROJECT_STATUS.md"
related:
  - "commands/start-sprint"
  - "commands/update-status"
status: "stable"
---
```

#### Agent Metadata
```yaml
---
name: "Backend Specialist Agent"
type: "agent"
version: "1.0.0"
description: "Specialization for server-side development, APIs, and data persistence"
tags: ["backend", "api", "database", "server"]
category: "agent-specialization"
relevance:
  - trigger: "api|backend|server|database"
  - context: "When working on server-side functionality"
extends: "AGENTS.md#core-agents"
specialties:
  - "API design and implementation"
  - "Database schema and queries"
  - "Server-side business logic"
  - "Authentication and authorization"
patterns_count: 8
workflows_count: 4
status: "stable"
---
```

---

## Discovery Mechanism

### How AI Agents Discover Capabilities

Unlike Claude Code's automatic relevance matching (which is platform-specific), Proto Gear uses a **manual but universal** discovery approach:

### 1. Master Index (`.proto-gear/INDEX.md`)

The master index is the **entry point** for capability discovery:

```markdown
# Proto Gear Capabilities Index

> **For AI Agents**: This is the master catalog of available capabilities.
> Read this file to discover what patterns and workflows are available.

## Quick Navigation

- [Skills](#skills) - Modular expertise (5 available)
- [Workflows](#workflows) - Multi-step processes (6 available)
- [Commands](#commands) - Single actions (8 available)
- [Agents](#agents) - Specialized patterns (5 available)

## Skills

Modular, reusable expertise in specific domains:

| Skill | Description | Relevance | Status |
|-------|-------------|-----------|--------|
| [testing](skills/testing/SKILL.md) | TDD methodology | When writing tests | Stable |
| [git-workflow](skills/git-workflow/SKILL.md) | Git branching | When managing branches | Stable |
| [debugging](skills/debugging/SKILL.md) | Troubleshooting | When fixing bugs | Stable |
| [performance](skills/performance/SKILL.md) | Optimization | When improving speed | Stable |
| [security](skills/security/SKILL.md) | Security practices | When hardening code | Beta |

## Workflows

Complete processes for multi-step tasks:

| Workflow | Steps | Duration | Relevance |
|----------|-------|----------|-----------|
| [feature-development](workflows/feature-development.md) | 7 | 2-4h | New features |
| [bug-fix](workflows/bug-fix.md) | 5 | 1-2h | Fixing bugs |
| [refactoring](workflows/refactoring.md) | 6 | 2-3h | Code quality |
| [performance-optimization](workflows/performance-optimization.md) | 8 | 3-5h | Speed issues |
| [security-review](workflows/security-review.md) | 6 | 2-4h | Security audit |
| [deployment](workflows/deployment.md) | 9 | 4-6h | Releases |

## Commands

Single-action patterns:

| Command | Purpose | Dependencies |
|---------|---------|--------------|
| [create-ticket](commands/create-ticket.md) | Create documented ticket | PROJECT_STATUS.md |
| [start-sprint](commands/start-sprint.md) | Initialize sprint | PROJECT_STATUS.md |
| [create-branch](commands/create-branch.md) | Create feature branch | git-workflow skill |
| [commit-changes](commands/commit-changes.md) | Conventional commits | git-workflow skill |
| [review-pr](commands/review-pr.md) | PR review checklist | None |
| [run-tests](commands/run-tests.md) | Execute test suite | testing skill |
| [update-status](commands/update-status.md) | Update project state | PROJECT_STATUS.md |
| [generate-docs](commands/generate-docs.md) | Create documentation | None |

## Agents

Specialized agent patterns:

| Agent | Specialization | Patterns | Workflows |
|-------|----------------|----------|-----------|
| [backend](agents/backend/AGENT.md) | Server-side dev | 8 | 4 |
| [frontend](agents/frontend/AGENT.md) | UI/UX development | 7 | 3 |
| [testing](agents/testing/AGENT.md) | QA and testing | 6 | 3 |
| [devops](agents/devops/AGENT.md) | Infrastructure | 9 | 5 |
| [security](agents/security/AGENT.md) | Security hardening | 7 | 4 |

## Discovery Workflow

**For AI Agents**: When starting a task:

1. **Read this INDEX.md** to see available capabilities
2. **Match task to capabilities** using relevance descriptions
3. **Check dependencies** for required capabilities
4. **Load relevant capabilities** by reading their files
5. **Follow patterns** using native tools (git, pytest, npm, etc.)

## Integration with Core Templates

This capability system **extends** Proto Gear's core templates:

- **AGENTS.md** - Core agent configuration, extended by `.proto-gear/agents/`
- **PROJECT_STATUS.md** - Single source of truth, updated by commands
- **BRANCHING.md** - Git workflow, detailed in `skills/git-workflow/`
- **TESTING.md** - TDD patterns, detailed in `skills/testing/`

---
*Proto Gear Universal Capabilities System v1.0*
```

### 2. Category Indexes

Each capability type has its own index (`skills/INDEX.md`, `workflows/INDEX.md`, etc.) with more detail:

```markdown
# Skills Index

## Available Skills

### Testing
**File**: `testing/SKILL.md`
**Version**: 1.0.0
**Description**: TDD methodology with red-green-refactor cycle
**Tags**: testing, tdd, quality
**When to Use**: Before implementing features, fixing bugs, or refactoring
**Patterns**: 3 (unit, integration, e2e)
**Examples**: 1
**Status**: Stable

### Git Workflow
**File**: `git-workflow/SKILL.md`
**Version**: 1.0.0
**Description**: Branch management and conventional commits
**Tags**: git, branching, commits, workflow
**When to Use**: Managing code changes and collaboration
**Patterns**: 3 (feature branch, hotfix, merge strategies)
**Examples**: 1
**Status**: Stable

### Debugging
**File**: `debugging/SKILL.md`
**Version**: 1.0.0
**Description**: Systematic troubleshooting and root cause analysis
**Tags**: debugging, troubleshooting, bugs
**When to Use**: Investigating and fixing unexpected behavior
**Patterns**: 3 (systematic debugging, log analysis, stack traces)
**Examples**: 0
**Status**: Stable

...
```

### 3. Discovery Workflow for AI Agents

```
┌─────────────────────────────────────────────────┐
│ 1. Agent starts task                            │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│ 2. Read .proto-gear/INDEX.md                    │
│    - Scan available capabilities                │
│    - Identify relevant categories               │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│ 3. Match task to capabilities                   │
│    - Check relevance triggers                   │
│    - Review descriptions                        │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│ 4. Load specific capabilities                   │
│    - Read relevant SKILL.md, workflow.md, etc.  │
│    - Check dependencies                         │
└─────────────┬───────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────┐
│ 5. Follow patterns using native tools           │
│    - Execute git, pytest, npm commands          │
│    - Update PROJECT_STATUS.md                   │
└─────────────────────────────────────────────────┘
```

### 4. Example Discovery Scenario

**User Request**: "Implement a new login feature with tests"

**Agent Discovery Process**:
1. Read `.proto-gear/INDEX.md`
2. Identify relevant capabilities:
   - Workflow: `feature-development.md` (matches "implement feature")
   - Skill: `testing/SKILL.md` (matches "with tests")
   - Skill: `git-workflow/SKILL.md` (needed for branching)
   - Command: `create-ticket.md` (needed for documentation)
   - Command: `create-branch.md` (needed for branch creation)
3. Load workflow: Read `workflows/feature-development.md`
4. Load dependencies: Read skills and commands
5. Execute workflow following documented patterns

---

## Capability Examples

Let me provide complete examples of each capability type:

### Example 1: Skill - Testing

**File**: `.proto-gear/skills/testing/SKILL.md`

```markdown
---
name: "Test-Driven Development"
type: "skill"
version: "1.0.0"
description: "TDD methodology with red-green-refactor cycle for quality code"
tags: ["testing", "tdd", "quality", "red-green-refactor", "coverage"]
category: "testing"
relevance:
  - trigger: "write tests|testing|test coverage|tdd|quality assurance"
  - context: "Before implementing features, fixing bugs, or refactoring code"
patterns:
  - "patterns/unit-testing.md"
  - "patterns/integration-testing.md"
  - "patterns/e2e-testing.md"
examples:
  - "examples/red-green-refactor-example.md"
dependencies: []
related: ["workflows/feature-development", "commands/run-tests"]
author: "Proto Gear Team"
last_updated: "2025-11-04"
status: "stable"
---

# Test-Driven Development Skill

## Overview

Test-Driven Development (TDD) is a software development approach where tests are written **before** implementation code. This skill provides patterns for practicing TDD effectively across different testing levels.

## Core Philosophy

> **Red → Green → Refactor**

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green

## When to Use This Skill

Use TDD when:
- ✅ Implementing new features
- ✅ Fixing bugs (write test that reproduces bug first)
- ✅ Refactoring existing code
- ✅ Building critical business logic
- ✅ Working on code with complex requirements

Consider alternatives when:
- ❌ Prototyping/exploratory coding
- ❌ UI styling and layout
- ❌ Simple configuration changes
- ❌ Documentation-only updates

## Testing Pyramid

```
        ┌─────────┐
        │   E2E   │  ← Few (slow, expensive)
        ├─────────┤
        │Integration│  ← Some (moderate cost)
        ├─────────┤
        │  Unit   │  ← Many (fast, cheap)
        └─────────┘
```

- **Unit Tests**: 70% - Test individual functions/methods
- **Integration Tests**: 20% - Test component interactions
- **E2E Tests**: 10% - Test complete user workflows

## Red-Green-Refactor Cycle

### Step 1: RED - Write Failing Test

**Purpose**: Define expected behavior before implementation

```python
# Example: Testing a user authentication function
def test_authenticate_user_with_valid_credentials():
    """Test that valid credentials authenticate successfully"""
    # Arrange
    user = User(username="alice", password_hash=hash_password("secret123"))
    auth_service = AuthService()

    # Act
    result = auth_service.authenticate("alice", "secret123")

    # Assert
    assert result.success is True
    assert result.user.username == "alice"
```

**Key Points**:
- Write test FIRST, before implementation exists
- Test should FAIL (red) because code doesn't exist yet
- Use descriptive test names that document behavior
- Follow Arrange-Act-Assert pattern

### Step 2: GREEN - Write Minimal Code

**Purpose**: Make test pass with simplest possible implementation

```python
# Minimal implementation to pass test
class AuthService:
    def authenticate(self, username: str, password: str):
        # Simplest code that makes test pass
        user = User.find_by_username(username)
        if user and user.verify_password(password):
            return AuthResult(success=True, user=user)
        return AuthResult(success=False, user=None)
```

**Key Points**:
- Write ONLY enough code to pass the test
- Don't optimize or add extra features yet
- Run test - it should PASS (green)
- Resist urge to over-engineer

### Step 3: REFACTOR - Improve Code

**Purpose**: Clean up code while maintaining passing tests

```python
# Refactored version with better structure
class AuthService:
    def authenticate(self, username: str, password: str):
        user = self._find_user(username)

        if not user:
            return self._failed_auth()

        if not user.verify_password(password):
            return self._failed_auth()

        return self._successful_auth(user)

    def _find_user(self, username: str):
        return User.find_by_username(username)

    def _failed_auth(self):
        return AuthResult(success=False, user=None)

    def _successful_auth(self, user: User):
        return AuthResult(success=True, user=user)
```

**Key Points**:
- Improve readability, structure, naming
- Extract methods for clarity
- Remove duplication
- Tests must STILL PASS after refactoring

## Testing Patterns

This skill includes detailed patterns for:

1. **[Unit Testing](patterns/unit-testing.md)** - Testing individual components
2. **[Integration Testing](patterns/integration-testing.md)** - Testing component interactions
3. **[E2E Testing](patterns/e2e-testing.md)** - Testing complete user flows

## Test Organization

### Directory Structure

```
project/
├── src/
│   └── auth/
│       └── auth_service.py
└── tests/
    ├── unit/
    │   └── auth/
    │       └── test_auth_service.py
    ├── integration/
    │   └── test_auth_flow.py
    └── e2e/
        └── test_login_journey.py
```

### Test Naming Convention

```python
def test_<function_name>_<scenario>_<expected_result>():
    """
    Format: test_WHAT_WHEN_EXPECTED

    Examples:
    - test_authenticate_with_valid_credentials_returns_success()
    - test_authenticate_with_invalid_password_returns_failure()
    - test_authenticate_with_nonexistent_user_returns_failure()
    """
    pass
```

## Coverage Targets

| Test Type | Coverage Target | Rationale |
|-----------|----------------|-----------|
| Unit | 80-90% | Core logic should be thoroughly tested |
| Integration | 60-70% | Key interactions covered |
| E2E | 40-50% | Critical user paths only |
| **Overall** | **70%+** | Healthy test coverage |

## Running Tests

### Command Pattern

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/auth/test_auth_service.py

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run tests matching pattern
pytest -k "auth"

# Run only failed tests
pytest --lf
```

## Best Practices

### DO ✅
- Write test before implementation
- Keep tests simple and focused
- Use descriptive test names
- Follow Arrange-Act-Assert pattern
- Test edge cases and error conditions
- Keep tests independent (no shared state)
- Run tests frequently during development

### DON'T ❌
- Write tests after implementation
- Test implementation details (test behavior)
- Create test interdependencies
- Ignore failing tests
- Skip refactoring step
- Write overly complex tests
- Mock everything (test real interactions when possible)

## Integration with PROJECT_STATUS.md

When practicing TDD, update PROJECT_STATUS.md to track test coverage:

```yaml
metrics:
  test_coverage: 78%
  unit_tests: 234
  integration_tests: 45
  e2e_tests: 12
```

## Related Capabilities

- **Workflow**: [Feature Development](../../workflows/feature-development.md) - Uses TDD throughout
- **Command**: [Run Tests](../../commands/run-tests.md) - Execute test suite
- **Workflow**: [Bug Fix](../../workflows/bug-fix.md) - Write test that reproduces bug

## Further Reading

- See `patterns/` directory for detailed testing patterns
- See `examples/` directory for concrete TDD examples
- Refer to TESTING.md in project root for project-specific conventions

---
*Proto Gear Testing Skill v1.0 - Stable*
```

### Example 2: Workflow - Feature Development

**File**: `.proto-gear/workflows/feature-development.md`

```markdown
---
name: "Feature Development Workflow"
type: "workflow"
version: "1.0.0"
description: "Complete workflow for building new features from concept to deployment"
tags: ["feature", "development", "workflow", "sprint", "tdd"]
category: "development"
relevance:
  - trigger: "new feature|implement feature|build feature|add feature"
  - context: "Starting work on a new user-facing capability"
dependencies:
  - "skills/testing"
  - "skills/git-workflow"
  - "commands/create-ticket"
  - "commands/create-branch"
  - "commands/run-tests"
  - "commands/update-status"
related:
  - "workflows/bug-fix"
  - "workflows/refactoring"
steps: 7
estimated_duration: "2-4 hours per feature"
author: "Proto Gear Team"
last_updated: "2025-11-04"
status: "stable"
---

# Feature Development Workflow

## Overview

This workflow guides you through implementing a new feature from concept to merged code, following TDD principles and Proto Gear conventions.

## Prerequisites

Before starting:
- ✅ Feature is defined and approved
- ✅ You have read AGENTS.md and understand agent roles
- ✅ PROJECT_STATUS.md is up-to-date
- ✅ You have access to Git repository
- ✅ Development environment is set up

## Workflow Steps

### Step 1: Create and Document Ticket

**Purpose**: Establish single source of truth for this feature

**Process**:
1. Read PROJECT_STATUS.md to get next ticket ID
2. Create ticket entry following command pattern: [Create Ticket](../commands/create-ticket.md)
3. Update PROJECT_STATUS.md with ticket details

**Example**:
```markdown
## 🎫 Active Tickets

| ID | Title | Type | Status | Branch | Assignee |
|----|-------|------|--------|--------|----------|
| PROJ-042 | Add user login feature | feature | IN_PROGRESS | feature/PROJ-042-add-user-login | Backend Agent |
```

**Command**:
```bash
# Agent reads PROJECT_STATUS.md to understand state
cat PROJECT_STATUS.md
```

### Step 2: Create Feature Branch

**Purpose**: Isolate work following Git workflow conventions

**Process**:
1. Checkout development branch
2. Pull latest changes
3. Create feature branch following naming convention
4. Verify branch creation

**Branch Naming**:
```
feature/<TICKET-ID>-<short-description>

Example: feature/PROJ-042-add-user-login
```

**Commands**:
```bash
# Ensure on development branch
git checkout development

# Pull latest
git pull origin development

# Create feature branch
git checkout -b feature/PROJ-042-add-user-login

# Verify
git branch --show-current
```

**Reference**: See [Git Workflow Skill](../skills/git-workflow/SKILL.md) for detailed branching patterns

### Step 3: Write Failing Tests (RED)

**Purpose**: Define expected behavior before implementation

**Process**:
1. Identify what needs testing (unit, integration, e2e)
2. Create test files in appropriate directories
3. Write tests that describe expected behavior
4. Run tests - they should FAIL (red)

**Example**:
```python
# tests/unit/auth/test_login_feature.py
def test_login_with_valid_credentials_returns_success():
    """Users can login with correct username and password"""
    auth_service = AuthService()
    result = auth_service.login("alice", "correct_password")

    assert result.success is True
    assert result.user.username == "alice"
    assert result.session_token is not None

def test_login_with_invalid_password_returns_failure():
    """Login fails with incorrect password"""
    auth_service = AuthService()
    result = auth_service.login("alice", "wrong_password")

    assert result.success is False
    assert result.error == "Invalid credentials"
```

**Commands**:
```bash
# Run tests - should FAIL
pytest tests/unit/auth/test_login_feature.py

# Expected output: FAILED (because feature doesn't exist yet)
```

**Reference**: See [Testing Skill](../skills/testing/SKILL.md) for TDD patterns

### Step 4: Implement Feature (GREEN)

**Purpose**: Write minimal code to make tests pass

**Process**:
1. Create implementation files
2. Write simplest code that passes tests
3. Run tests frequently
4. Stop when tests PASS (green)

**Example**:
```python
# src/auth/auth_service.py
class AuthService:
    def login(self, username: str, password: str):
        """Authenticate user with username and password"""
        user = User.find_by_username(username)

        if not user:
            return LoginResult(success=False, error="Invalid credentials")

        if not user.verify_password(password):
            return LoginResult(success=False, error="Invalid credentials")

        session_token = self._create_session_token(user)
        return LoginResult(success=True, user=user, session_token=session_token)
```

**Commands**:
```bash
# Run tests - should PASS
pytest tests/unit/auth/test_login_feature.py

# Expected output: PASSED
```

**Key Points**:
- Write ONLY code needed to pass tests
- Don't over-engineer or add extra features
- Focus on making tests green

### Step 5: Refactor and Improve (REFACTOR)

**Purpose**: Clean up code while maintaining passing tests

**Process**:
1. Review implementation for improvements
2. Extract methods for clarity
3. Remove duplication
4. Improve naming
5. Run tests after each change - must stay GREEN

**Example**:
```python
# Refactored version
class AuthService:
    def login(self, username: str, password: str):
        """Authenticate user and create session"""
        user = self._find_and_verify_user(username, password)

        if not user:
            return self._failed_login("Invalid credentials")

        return self._successful_login(user)

    def _find_and_verify_user(self, username: str, password: str):
        user = User.find_by_username(username)
        if user and user.verify_password(password):
            return user
        return None

    def _failed_login(self, error_message: str):
        return LoginResult(success=False, error=error_message)

    def _successful_login(self, user: User):
        session_token = SessionManager.create_token(user)
        return LoginResult(success=True, user=user, session_token=session_token)
```

**Commands**:
```bash
# Run tests after refactoring - should STILL PASS
pytest tests/unit/auth/test_login_feature.py

# Run full test suite
pytest
```

**Best Practices**:
- Refactor in small steps
- Run tests after each change
- If tests fail, undo last change
- Commit when tests pass

### Step 6: Commit Changes

**Purpose**: Save work with descriptive commit message

**Process**:
1. Stage relevant files
2. Write conventional commit message
3. Reference ticket ID in message
4. Push to remote (if applicable)

**Commit Message Format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, refactor, test, chore

**Example**:
```bash
# Stage files
git add src/auth/auth_service.py
git add tests/unit/auth/test_login_feature.py

# Commit with conventional message
git commit -m "feat(auth): add user login feature

Implements user authentication with username/password.
Includes unit tests with 90% coverage.

Tests:
- Valid credentials → successful login
- Invalid password → failure with error
- Nonexistent user → failure with error

Closes PROJ-042"

# Push to remote
git push -u origin feature/PROJ-042-add-user-login
```

**Reference**: See [Git Workflow Skill](../skills/git-workflow/SKILL.md) for commit conventions

### Step 7: Update Status and Create PR

**Purpose**: Track progress and request review

**Process**:
1. Update PROJECT_STATUS.md to mark ticket completed
2. Create pull request
3. Fill out PR template
4. Request review (if team workflow requires)

**Update PROJECT_STATUS.md**:
```markdown
## ✅ Completed Tickets

| ID | Title | Completed | PR |
|----|-------|-----------|-----|
| PROJ-042 | Add user login feature | 2025-11-04 | #123 |
```

**Create Pull Request**:
```bash
# Using GitHub CLI
gh pr create \
  --title "feat(auth): add user login feature" \
  --body "Implements user authentication. Closes PROJ-042" \
  --base development
```

**PR Description Template**:
```markdown
## Summary
Implements user login feature with username/password authentication.

## Changes Made
- Added `AuthService.login()` method
- Created unit tests for login scenarios
- Implemented session token generation

## Testing Done
- ✅ All unit tests passing (3/3)
- ✅ Test coverage: 92%
- ✅ Manual testing in dev environment

## Checklist
- [x] Tests written and passing
- [x] Code refactored and clean
- [x] PROJECT_STATUS.md updated
- [x] Follows Git workflow conventions
- [x] No security vulnerabilities introduced

Closes PROJ-042
```

## Success Criteria

Feature development is complete when:
- ✅ All tests passing (unit, integration, e2e as applicable)
- ✅ Test coverage meets target (70%+)
- ✅ Code follows project conventions
- ✅ No linting errors
- ✅ PROJECT_STATUS.md updated
- ✅ Pull request created
- ✅ CI/CD pipeline passing (if applicable)

## Common Pitfalls

| Pitfall | Solution |
|---------|----------|
| Writing implementation before tests | Stop and write tests first |
| Skipping refactoring step | Always refactor after green |
| Vague commit messages | Follow conventional commit format |
| Not updating PROJECT_STATUS.md | Update after each major step |
| Over-engineering features | Write minimal code to pass tests |
| Not running tests frequently | Run tests after every small change |

## Variations

### For Bug Fixes
Use [Bug Fix Workflow](bug-fix.md) instead

### For Refactoring
Use [Refactoring Workflow](refactoring.md) instead

### For Performance Work
Use [Performance Optimization Workflow](performance-optimization.md) instead

## Integration with Core Templates

- **AGENTS.md**: Agent roles coordinate feature work
- **PROJECT_STATUS.md**: Single source of truth for ticket status
- **BRANCHING.md**: Git workflow conventions
- **TESTING.md**: TDD methodology details

## Tools and Native Commands

This workflow uses native development tools:
- `git` - Version control
- `pytest` (or project's test runner) - Testing
- `gh` - GitHub CLI (if using GitHub)
- Text editor - Code editing

## Related Capabilities

- **Skill**: [Testing](../skills/testing/SKILL.md) - TDD patterns
- **Skill**: [Git Workflow](../skills/git-workflow/SKILL.md) - Branch management
- **Command**: [Create Ticket](../commands/create-ticket.md) - Ticket documentation
- **Command**: [Run Tests](../commands/run-tests.md) - Test execution
- **Workflow**: [Bug Fix](bug-fix.md) - Alternative for defects
- **Workflow**: [Refactoring](refactoring.md) - Code quality improvements

---
*Proto Gear Feature Development Workflow v1.0 - Stable*
```

### Example 3: Command - Create Ticket

**File**: `.proto-gear/commands/create-ticket.md`

```markdown
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
last_updated: "2025-11-04"
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

## 📊 Current State

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

## 📊 Current State

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
2. **For bugs**: Follow [Bug Fix Workflow](../workflows/bug-fix.md)
3. **For refactoring**: Follow [Refactoring Workflow](../workflows/refactoring.md)

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

- **[Update Status](update-status.md)** - Change ticket status
- **[Start Sprint](start-sprint.md)** - Create multiple tickets
- **[Create Branch](create-branch.md)** - Create branch after ticket creation

## Related Skills

- **[Git Workflow](../skills/git-workflow/SKILL.md)** - Branch naming conventions

## Related Workflows

- **[Feature Development](../workflows/feature-development.md)** - Uses Create Ticket in Step 1
- **[Bug Fix](../workflows/bug-fix.md)** - Uses Create Ticket to document bug

## Tools Used

- Text editor - To modify PROJECT_STATUS.md
- `cat` or `less` - To read current state

---
*Proto Gear Create Ticket Command v1.0 - Stable*
```

### Example 4: Agent Specialization - Backend

**File**: `.proto-gear/agents/backend/AGENT.md`

```markdown
---
name: "Backend Specialist Agent"
type: "agent"
version: "1.0.0"
description: "Specialization for server-side development, APIs, and data persistence"
tags: ["backend", "api", "database", "server", "business-logic"]
category: "agent-specialization"
relevance:
  - trigger: "api|backend|server|database|endpoint|business logic"
  - context: "When working on server-side functionality, APIs, or data layer"
extends: "AGENTS.md#core-agents"
specialties:
  - "REST API design and implementation"
  - "Database schema design and queries"
  - "Server-side business logic"
  - "Authentication and authorization"
  - "Data validation and transformation"
  - "Error handling and logging"
patterns_count: 8
workflows_count: 4
author: "Proto Gear Team"
last_updated: "2025-11-04"
status: "stable"
---

# Backend Specialist Agent

## Overview

The Backend Specialist Agent extends Proto Gear's core agent system with expertise in server-side development, API design, database management, and business logic implementation.

## Identity and Role

**Role**: Backend Development Specialist
**Extends**: Core Agent #1 (from AGENTS.md)
**Responsibilities**: Server-side code, APIs, databases, business logic

## When to Activate

This specialization activates when:
- Building or modifying REST/GraphQL APIs
- Designing database schemas
- Implementing business logic
- Handling authentication/authorization
- Working with data persistence
- Integrating third-party services
- Optimizing backend performance

## Core Competencies

### 1. API Design and Implementation

**Expertise**:
- RESTful API architecture
- GraphQL schema design
- API versioning strategies
- Request/response formats
- Status code usage
- Rate limiting and throttling

**Pattern**: [API Design](patterns/api-design.md)

**Example Scenario**: Designing user authentication endpoint

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "alice",
  "password": "secret123"
}

Response 200 OK:
{
  "success": true,
  "user": {
    "id": "user-123",
    "username": "alice",
    "email": "alice@example.com"
  },
  "session_token": "eyJhbGc...",
  "expires_at": "2025-11-05T12:00:00Z"
}

Response 401 Unauthorized:
{
  "success": false,
  "error": {
    "code": "INVALID_CREDENTIALS",
    "message": "Username or password is incorrect"
  }
}
```

### 2. Database Schema Design

**Expertise**:
- Relational database design (PostgreSQL, MySQL)
- NoSQL schema design (MongoDB, DynamoDB)
- Migration strategies
- Indexing for performance
- Data normalization
- Query optimization

**Pattern**: [Database Patterns](patterns/database-patterns.md)

**Example Scenario**: User authentication schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    INDEX idx_user_sessions (user_id),
    INDEX idx_token_lookup (token_hash)
);

-- Indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
```

### 3. Business Logic Implementation

**Expertise**:
- Domain-driven design
- Service layer patterns
- Transaction management
- Validation and sanitization
- Error handling
- Logging and monitoring

**Pattern**: [Error Handling](patterns/error-handling.md)

**Example Scenario**: Authentication service

```python
# Service layer with business logic
class AuthenticationService:
    """Handles user authentication business logic"""

    def __init__(self, user_repository, session_repository):
        self.users = user_repository
        self.sessions = session_repository
        self.logger = logging.getLogger(__name__)

    def login(self, username: str, password: str):
        """
        Authenticate user and create session

        Business Rules:
        - Username must exist
        - Password must match hash
        - User account must be active
        - Failed attempts are logged
        - Session expires in 24 hours
        """
        try:
            # Validate inputs
            self._validate_login_inputs(username, password)

            # Find user
            user = self.users.find_by_username(username)
            if not user:
                self.logger.warning(f"Login attempt for nonexistent user: {username}")
                return self._login_failed("Invalid credentials")

            # Verify password
            if not user.verify_password(password):
                self.logger.warning(f"Invalid password for user: {username}")
                self._increment_failed_attempts(user)
                return self._login_failed("Invalid credentials")

            # Check if account is locked
            if user.is_locked():
                self.logger.warning(f"Login attempt for locked account: {username}")
                return self._login_failed("Account is locked")

            # Create session
            session = self._create_session(user)

            # Update last login
            user.last_login = datetime.utcnow()
            self.users.save(user)

            self.logger.info(f"Successful login for user: {username}")
            return self._login_successful(user, session)

        except ValidationError as e:
            self.logger.error(f"Validation error during login: {e}")
            return self._login_failed(str(e))
        except Exception as e:
            self.logger.exception(f"Unexpected error during login: {e}")
            return self._login_failed("An unexpected error occurred")
```

### 4. Authentication and Authorization

**Expertise**:
- Session management
- JWT tokens
- OAuth 2.0 / OIDC
- Role-based access control (RBAC)
- Permission systems
- Security best practices

**Pattern**: Available in patterns directory

## Specialized Workflows

This agent has dedicated workflows for:

1. **[API Development](workflows/api-development.md)** - Complete API endpoint workflow
2. **[Database Migration](workflows/database-migration.md)** - Safe schema changes
3. **[Service Integration](workflows/service-integration.md)** - Third-party API integration
4. **[Performance Optimization](workflows/backend-optimization.md)** - Backend performance tuning

## Technology Stack Awareness

This agent adapts to your project's backend technologies:

### Detected: Node.js + Express
- Uses Express patterns
- Middleware architecture
- async/await patterns
- npm package management

### Detected: Python + FastAPI
- Uses Pydantic models
- Dependency injection
- Type hints
- pytest for testing

### Detected: Python + Django
- Uses Django ORM
- Class-based views
- Django migrations
- Django test framework

### Detected: Java + Spring Boot
- Uses Spring annotations
- Bean management
- JPA/Hibernate
- JUnit testing

## Decision-Making Patterns

### When designing APIs:
1. **Check existing conventions** - Review other endpoints
2. **Follow REST principles** - Use appropriate HTTP methods
3. **Design for versioning** - Plan for future changes
4. **Document endpoints** - Create OpenAPI/Swagger docs
5. **Consider rate limiting** - Protect from abuse

### When working with databases:
1. **Use migrations** - Never modify schema directly
2. **Index strategically** - Balance query speed vs. write cost
3. **Normalize appropriately** - Follow 3NF unless performance requires denormalization
4. **Plan for scaling** - Consider future growth
5. **Backup strategy** - Ensure data safety

### When implementing business logic:
1. **Validate inputs** - Trust nothing from users
2. **Handle errors gracefully** - Never expose internal details
3. **Log appropriately** - Info for success, warn for recoverable errors, error for failures
4. **Use transactions** - Ensure data consistency
5. **Write tests** - Follow TDD for business logic

## Integration with Core Templates

### AGENTS.md
- Extends Core Agent #1 (Backend Agent)
- Follows agent collaboration patterns
- Updates PROJECT_STATUS.md when completing tasks

### PROJECT_STATUS.md
- Reads current state before starting work
- Updates ticket status as work progresses
- Tracks API endpoints and database changes

### TESTING.md
- Follows TDD patterns for all backend code
- Writes unit tests for business logic
- Writes integration tests for API endpoints
- Writes database tests for queries

### BRANCHING.md
- Creates feature branches for new endpoints
- Follows conventional commit messages
- References tickets in commits

## Collaboration Patterns

### With Frontend Agent
- Defines API contracts collaboratively
- Provides endpoint documentation
- Coordinates on data formats
- Helps debug integration issues

### With Testing Agent
- Collaborates on test strategy
- Provides test fixtures and mocks
- Reviews test coverage
- Assists with integration testing

### With DevOps Agent
- Defines infrastructure requirements
- Assists with deployment configuration
- Provides monitoring requirements
- Helps troubleshoot production issues

### With Security Agent
- Implements security best practices
- Reviews authentication/authorization
- Addresses security vulnerabilities
- Follows OWASP guidelines

## Tools and Technologies

Native tools this agent uses:
- **Version Control**: git
- **Package Managers**: npm, pip, maven, gradle
- **Testing**: pytest, jest, junit
- **Database CLIs**: psql, mysql, mongo
- **API Testing**: curl, httpie, Postman
- **Migration Tools**: Alembic, Flyway, Django migrations

## Best Practices

### DO ✅
- Use TDD for all business logic
- Validate all inputs at API boundary
- Use database transactions for multi-step operations
- Log errors with context
- Handle errors gracefully without exposing internals
- Write integration tests for API endpoints
- Use migrations for all schema changes
- Follow REST conventions
- Document all endpoints
- Use appropriate HTTP status codes

### DON'T ❌
- Trust user input without validation
- Expose stack traces to users
- Modify database schema without migrations
- Store passwords in plain text
- Hardcode configuration
- Ignore error cases
- Skip writing tests
- Bypass authentication for "convenience"
- Use SELECT * in production queries
- Commit credentials to Git

## Common Patterns

This agent provides detailed patterns for:

1. **[API Design](patterns/api-design.md)** - REST API conventions
2. **[Database Patterns](patterns/database-patterns.md)** - Schema and query patterns
3. **[Error Handling](patterns/error-handling.md)** - Exception management
4. **[Validation Patterns](patterns/validation.md)** - Input validation
5. **[Service Layer](patterns/service-layer.md)** - Business logic organization
6. **[Repository Pattern](patterns/repository.md)** - Data access abstraction
7. **[Authentication](patterns/authentication.md)** - Auth/auth patterns
8. **[Logging](patterns/logging.md)** - Structured logging

## Related Capabilities

- **Workflows**: [Feature Development](../../workflows/feature-development.md)
- **Skills**: [Testing](../../skills/testing/SKILL.md)
- **Skills**: [Security](../../skills/security/SKILL.md)
- **Skills**: [Performance](../../skills/performance/SKILL.md)
- **Agents**: [Testing Agent](../testing/AGENT.md)
- **Agents**: [DevOps Agent](../devops/AGENT.md)

---
*Proto Gear Backend Specialist Agent v1.0 - Stable*
```

---

## Integration with Existing Templates

### How Capabilities Extend Core Templates

The capability system **extends** rather than replaces Proto Gear's core templates:

```
┌─────────────────────────────────────────────────┐
│ EXISTING PROTO GEAR TEMPLATES                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ AGENTS.md                                       │
│ └─ Defines 4 core + 2 flex agent pattern       │
│ └─ Describes collaboration workflows           │
│ └─ References .proto-gear/ for details         │
│                                                 │
│ PROJECT_STATUS.md                               │
│ └─ Single source of truth for state            │
│ └─ Updated by commands from .proto-gear/       │
│                                                 │
│ BRANCHING.md                                    │
│ └─ High-level Git workflow                     │
│ └─ Detailed patterns in skills/git-workflow/   │
│                                                 │
│ TESTING.md                                      │
│ └─ High-level TDD philosophy                   │
│ └─ Detailed patterns in skills/testing/        │
│                                                 │
└─────────────────────────────────────────────────┘
                      │
                      │ Extends with
                      ▼
┌─────────────────────────────────────────────────┐
│ UNIVERSAL CAPABILITIES SYSTEM                   │
├─────────────────────────────────────────────────┤
│                                                 │
│ .proto-gear/                                    │
│ ├─ INDEX.md                                     │
│ ├─ skills/                                      │
│ │  ├─ testing/ (extends TESTING.md)            │
│ │  └─ git-workflow/ (extends BRANCHING.md)     │
│ ├─ workflows/                                   │
│ │  └─ feature-development.md                   │
│ ├─ commands/                                    │
│ │  ├─ create-ticket.md                         │
│ │  └─ update-status.md                         │
│ └─ agents/                                      │
│    └─ backend/ (extends AGENTS.md)             │
│                                                 │
└─────────────────────────────────────────────────┘
```

### Modified AGENTS.md with Capability Reference

Add to AGENTS.md:

```markdown
# AGENTS.md - Lead AI Development Workflow

## 🚀 Enhanced with Universal Capabilities

This project uses Proto Gear's **Universal Capabilities System** for modular, discoverable patterns.

### Capability Discovery

AI agents can explore available capabilities:

**Capability Index**: [.proto-gear/INDEX.md](.proto-gear/INDEX.md)

- **Skills** - Modular expertise (testing, git-workflow, debugging, etc.)
- **Workflows** - Multi-step processes (feature-development, bug-fix, etc.)
- **Commands** - Single actions (create-ticket, run-tests, etc.)
- **Agents** - Specialized patterns (backend, frontend, testing, etc.)

### How to Use Capabilities

1. **Read Index**: Start with `.proto-gear/INDEX.md`
2. **Match Task**: Find relevant capabilities for your current task
3. **Load Details**: Read specific capability files
4. **Follow Patterns**: Use native tools (git, pytest, npm) as described

### Integration with Core Agents

Core agents defined below are **extended** by specialized agent patterns in `.proto-gear/agents/`:

- **Backend Agent** → Extended by `.proto-gear/agents/backend/AGENT.md`
- **Frontend Agent** → Extended by `.proto-gear/agents/frontend/AGENT.md`
- **Testing Agent** → Extended by `.proto-gear/agents/testing/AGENT.md`
- **DevOps Agent** → Extended by `.proto-gear/agents/devops/AGENT.md`

---

[Rest of existing AGENTS.md content...]
```

### Modified PROJECT_STATUS.md Reference

Add to PROJECT_STATUS.md:

```markdown
# PROJECT STATUS - Single Source of Truth

> **For Agents**: Use commands from `.proto-gear/commands/` to update this file:
> - [Create Ticket](. proto-gear/commands/create-ticket.md)
> - [Update Status](.proto-gear/commands/update-status.md)
> - [Start Sprint](.proto-gear/commands/start-sprint.md)

[Rest of existing PROJECT_STATUS.md content...]
```

---

## Implementation Roadmap

### Phase 1: Foundation (v0.4.0) - 2-3 weeks

**Goal**: Establish directory structure and core metadata format

**Tasks**:
1. Create `.proto-gear/` directory structure
2. Define metadata format specification
3. Create master INDEX.md template
4. Create category INDEX.md templates (skills, workflows, commands, agents)
5. Write 2-3 example capabilities (testing skill, feature workflow, create-ticket command)
6. Update `pg init` to optionally generate `.proto-gear/` structure
7. Update AGENTS.md template to reference capabilities
8. Documentation: Write design document (this file)
9. Testing: Validate with sample project

**Deliverables**:
- `.proto-gear/` directory structure
- Master and category INDEX templates
- 3 complete example capabilities
- Updated `pg init` command
- Design documentation

### Phase 2: Core Capabilities (v0.5.0) - 3-4 weeks

**Goal**: Build library of essential capabilities

**Skills** (5):
- testing (TDD workflow)
- git-workflow (branching, commits)
- debugging (troubleshooting patterns)
- performance (optimization techniques)
- security (secure coding practices)

**Workflows** (6):
- feature-development
- bug-fix
- refactoring
- performance-optimization
- security-review
- deployment

**Commands** (8):
- create-ticket
- start-sprint
- create-branch
- commit-changes
- review-pr
- run-tests
- update-status
- generate-docs

**Agents** (5):
- backend
- frontend
- testing
- devops
- security

**Deliverables**:
- 24 complete capabilities
- All with examples and patterns
- Cross-references between capabilities
- Integration tests

### Phase 3: Enhancement and Polish (v0.6.0) - 2 weeks

**Goal**: Refine based on real-world usage

**Tasks**:
1. User testing with real projects
2. Gather feedback from AI agents (Claude, GPT, Gemini)
3. Refine metadata format based on usage
4. Add more examples and patterns
5. Improve discovery mechanism
6. Add capability versioning support
7. Create migration guide for existing projects
8. Write comprehensive documentation

**Deliverables**:
- Refined metadata format
- Enhanced discovery mechanism
- Migration guide
- User documentation
- Real-world validation

### Phase 4: Expansion (v0.7.0+) - Ongoing

**Goal**: Grow capability library based on community needs

**Possible Additions**:
- More specialized agents (ML, mobile, blockchain, etc.)
- Domain-specific workflows (data science, DevOps, game dev)
- Language-specific patterns (Rust, Go, TypeScript, etc.)
- Framework-specific skills (React, Django, Spring Boot)
- Industry-specific capabilities (fintech, healthcare, etc.)

**Community Contributions**:
- Accept community-contributed capabilities
- Establish capability review process
- Create capability marketplace/registry
- Version control for capabilities

---

## Success Metrics

### Adoption Metrics
- Number of projects using capability system
- Number of capabilities per project (usage depth)
- Community-contributed capabilities

### Effectiveness Metrics
- AI agent task completion rate
- Time to discover relevant capability
- Capability reuse across projects

### Quality Metrics
- Capability stability (breaking changes)
- Documentation completeness
- Example coverage

---

## Open Questions for Feedback

1. **Metadata Format**: Is YAML frontmatter the best choice, or should we support alternatives?
2. **Discovery**: Should we add a CLI command like `pg capabilities list`?
3. **Versioning**: How should we handle capability versioning and breaking changes?
4. **Namespacing**: Should capabilities support custom namespaces for organization-specific patterns?
5. **Validation**: Should `pg init` validate capability files for correctness?
6. **Templates**: Should capabilities support template variables like `{{PROJECT_NAME}}`?
7. **Distribution**: Should we support remote capability repositories?

---

## Appendices

### Appendix A: Complete Metadata Schema

```yaml
# Required fields
name: string              # Human-readable capability name
type: enum                # skill|workflow|command|agent
version: semver           # Semantic version (1.0.0)
description: string       # Brief summary (1-2 sentences)

# Discovery fields
tags: array[string]       # Keywords for discovery
category: string          # Primary category
relevance:                # When to use this capability
  - trigger: string       # Keywords that suggest relevance
  - context: string       # Situational description

# Relationship fields (optional)
dependencies: array[string]  # Required capabilities
related: array[string]       # Similar capabilities
extends: string              # Parent capability (agents only)

# Type-specific fields
patterns: array[string]      # Sub-patterns (skills only)
examples: array[string]      # Examples (skills only)
steps: integer               # Number of steps (workflows only)
estimated_duration: string   # Time estimate (workflows only)
specialties: array[string]   # Areas of expertise (agents only)

# Metadata
author: string            # Creator
last_updated: date        # ISO 8601 date
status: enum              # stable|beta|experimental
```

### Appendix B: File Naming Conventions

| Type | Naming Convention | Example |
|------|------------------|---------|
| Skill | `skills/{name}/SKILL.md` | `skills/testing/SKILL.md` |
| Workflow | `workflows/{name}.md` | `workflows/feature-development.md` |
| Command | `commands/{name}.md` | `commands/create-ticket.md` |
| Agent | `agents/{type}/AGENT.md` | `agents/backend/AGENT.md` |
| Pattern | `{type}/patterns/{name}.md` | `skills/testing/patterns/unit-testing.md` |
| Example | `{type}/examples/{name}.md` | `skills/testing/examples/tdd-example.md` |
| Index | `{directory}/INDEX.md` | `skills/INDEX.md` |

### Appendix C: Capability Maturity Levels

| Status | Definition | Stability | Breaking Changes |
|--------|-----------|-----------|------------------|
| **experimental** | Early development, may change significantly | Low | Expected |
| **beta** | Feature-complete but may need refinement | Medium | Possible |
| **stable** | Production-ready, well-tested | High | Avoided |
| **deprecated** | Being phased out, use alternative | N/A | N/A |

---

## Conclusion

This Universal Capabilities System provides Proto Gear with a **platform-agnostic**, **filesystem-based**, **modular** approach to AI agent patterns that works across ALL AI platforms (Claude, GPT, Gemini, Llama, etc.).

By using pure markdown, YAML frontmatter, and filesystem conventions, we create a system that is:
- ✅ Universal - Works with any AI agent
- ✅ Discoverable - Clear index-based discovery
- ✅ Modular - Single-purpose capabilities
- ✅ Git-friendly - Plain text, version-controlled
- ✅ Human-editable - Developers can customize
- ✅ Extensible - Easy to add new capabilities
- ✅ Self-documenting - Structure reveals purpose

This design maintains Proto Gear's core philosophy of **natural language collaboration** while providing the **modularity and discoverability** that makes agent systems powerful.

---
*Proto Gear Universal Capabilities System Design Document v1.0*
*Status: Design Phase - Ready for Review and Implementation*
