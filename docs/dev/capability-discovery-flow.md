# Capability Discovery Flow

**Purpose**: Visual documentation of how AI agents discover and use Proto Gear capabilities.

## Overview

Proto Gear's capability system is **opt-in** and **self-discovering**. When capabilities are installed, agents automatically find and use them through a structured workflow.

## Discovery Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Agent Starts Task                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         Step 1: Read AGENTS.md (Master Entry Point)         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ⚠️ BEFORE ANY WORK - MANDATORY READING              │    │
│  │                                                      │    │
│  │ 1. PROJECT_STATUS.md (REQUIRED)                     │    │
│  │ 2. BRANCHING.md (if exists)                         │    │
│  │ 3. TESTING.md (RECOMMENDED)                         │    │
│  │ 4. .proto-gear/INDEX.md (if exists) ← CAPABILITY!  │    │
│  │ 5-8. Other templates (if exist)                     │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│         ✅ Pre-Flight Checklist (Item #1)                   │
│                                                              │
│  [ ] FIRST: Check if .proto-gear/INDEX.md exists           │
│      └─→ If YES: Read it to discover capabilities           │
│      └─→ If NO: Skip capability system                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
               ┌───────┴────────┐
               │                │
          ┌────▼────┐      ┌────▼────┐
          │ EXISTS  │      │ MISSING │
          └────┬────┘      └────┬────┘
               │                │
               │                ↓
               │           ┌──────────────────────┐
               │           │ Skip Capability      │
               │           │ System - Use Only    │
               │           │ Core Templates       │
               │           └──────────────────────┘
               │
               ↓
┌─────────────────────────────────────────────────────────────┐
│   Step 2: Read .proto-gear/INDEX.md (Capability Catalog)   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ # Proto Gear Capabilities Index                    │    │
│  │                                                      │    │
│  │ ## Quick Navigation                                 │    │
│  │ - Skills (4): testing, debugging, code-review, ...  │    │
│  │ - Workflows (5): feature-dev, bug-fix, hotfix, ...  │    │
│  │ - Commands (3): create-ticket, analyze-coverage,... │    │
│  │ - Agents (0-N): backend, frontend, testing, ...     │    │
│  │                                                      │    │
│  │ ## Skills                                            │    │
│  │ | Skill    | Description | Relevance | Status |     │    │
│  │ | testing  | TDD method  | When...   | Stable |     │    │
│  │ | ...      | ...         | ...       | ...    |     │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│    Step 3: Match Task to Relevant Capabilities              │
│                                                              │
│  Agent's Task: "Implement new login feature"                │
│                                                              │
│  Matching Process:                                           │
│  ┌────────────────────────────────────────────────────┐    │
│  │ 1. Check INDEX.md "Relevance" column               │    │
│  │ 2. Find: "feature-development" workflow            │    │
│  │    Relevance: "Building new features from          │    │
│  │               concept to deployment"                │    │
│  │ 3. Match: ✓ This is my task!                       │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│   Step 4: Load Specific Capability File                     │
│                                                              │
│  Read: .proto-gear/workflows/feature-development.md         │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │ # Feature Development Workflow                     │    │
│  │                                                      │    │
│  │ ## 7-Step Process                                   │    │
│  │ 1. Plan - Define requirements, break down tasks    │    │
│  │ 2. Design - Architecture, data models, APIs        │    │
│  │ 3. Implement - Write code following TDD            │    │
│  │ 4. Test - Unit, integration, e2e tests             │    │
│  │ 5. Review - Code review checklist                  │    │
│  │ 6. Document - Update docs, comments, changelog     │    │
│  │ 7. Deploy - Merge, CI/CD, monitor                  │    │
│  │                                                      │    │
│  │ ## Dependencies                                     │    │
│  │ - skills/testing (for step 3)                      │    │
│  │ - commands/create-ticket (for planning)            │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│   Step 5: Follow Pattern Using Native Tools                 │
│                                                              │
│  Agent executes workflow steps using:                        │
│  ┌────────────────────────────────────────────────────┐    │
│  │ ✓ git (for branching, commits, merges)            │    │
│  │ ✓ pytest/jest/etc (for testing)                   │    │
│  │ ✓ Read/Write tools (for code changes)             │    │
│  │ ✓ PROJECT_STATUS.md (for state updates)           │    │
│  │                                                      │    │
│  │ NOT using Proto Gear-specific commands             │    │
│  │ (Proto Gear just provides the pattern!)            │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│                    Task Completed                            │
│                                                              │
│  ✓ Used capability workflow                                 │
│  ✓ Followed consistent pattern                              │
│  ✓ Updated PROJECT_STATUS.md                                │
│  ✓ Maintained quality standards                             │
└─────────────────────────────────────────────────────────────┘
```

## Flow Variants

### Variant A: Capabilities Installed

```
AGENTS.md → Check INDEX.md → EXISTS → Load workflows → Execute
    │
    └─→ Fast, consistent, high-quality
```

### Variant B: Capabilities NOT Installed

```
AGENTS.md → Check INDEX.md → MISSING → Use core templates → Execute
    │
    └─→ Still works, just without specialized patterns
```

### Variant C: Task-Specific Capability

```
Task: "Fix bug in authentication"
  ↓
INDEX.md → Find "bug-fix" workflow
  ↓
.proto-gear/workflows/bug-fix.md
  ↓
6-step debugging process:
  1. Reproduce
  2. Diagnose
  3. Fix
  4. Test
  5. Verify
  6. Document
```

## Critical Rules Integration

The capability discovery is enforced through **Critical Rule #1** in AGENTS.md:

```markdown
### 🚨 Critical Rules

1. **ALWAYS check `.proto-gear/INDEX.md` first** - if capabilities exist, use them for your task
2. NEVER commit directly to `main` or `development`
3. ALWAYS update PROJECT_STATUS.md when starting/completing tickets
...
```

This makes capability discovery **mandatory** when capabilities are installed.

## Pre-Flight Checklist Integration

Item #1 in the pre-flight checklist:

```markdown
### ✅ Pre-Flight Checklist

Before starting ANY development task, verify:
- [ ] **FIRST**: Check if `.proto-gear/INDEX.md` exists - if yes, read it to discover available capabilities
- [ ] Read PROJECT_STATUS.md - know current sprint and active tickets
- [ ] Read BRANCHING.md (if exists) - understand git workflow
...
```

## Example: Real Agent Flow

### Scenario: Agent Receives Task "Add User Profile Page"

```
1. Agent reads AGENTS.md
   └→ Sees: "FIRST: Check if .proto-gear/INDEX.md exists"

2. Agent checks: Read(file_path=".proto-gear/INDEX.md")
   └→ File exists! (Capabilities installed)

3. Agent scans INDEX.md:
   ┌────────────────────────────────────────┐
   │ Workflows:                             │
   │ - feature-development: "Building new   │
   │   features from concept to deployment" │
   │ - bug-fix: "Systematic bug resolution" │
   │ - hotfix: "Emergency production fixes" │
   │ - release: "Version release workflow"  │
   └────────────────────────────────────────┘

4. Agent matches task:
   "Add User Profile Page" → NEW FEATURE → feature-development ✓

5. Agent reads: .proto-gear/workflows/feature-development.md

6. Agent follows 7-step process:
   Step 1 (Plan):
   - Read PROJECT_STATUS.md for context
   - Create ticket: PROJ-042
   - Break down: header, bio, settings, avatar

   Step 2 (Design):
   - Design component structure
   - Define state management
   - Plan API endpoints

   Step 3 (Implement):
   - Read .proto-gear/skills/testing/SKILL.md (TDD)
   - Write tests FIRST (Red)
   - Implement component (Green)
   - Refactor (Blue)

   ... continues through all 7 steps

7. Result:
   ✓ Consistent quality
   ✓ Complete documentation
   ✓ Proper testing
   ✓ Following project conventions
```

## Benefits of This Flow

### For Consistency
- ✅ All agents follow same patterns
- ✅ Predictable outcomes
- ✅ Reduced variability

### For Quality
- ✅ Built-in best practices
- ✅ TDD enforcement
- ✅ Complete testing coverage
- ✅ Proper documentation

### For Discoverability
- ✅ No hidden patterns
- ✅ Self-documenting system
- ✅ Easy to extend with new capabilities
- ✅ Clear relationship between task types and workflows

### For Flexibility
- ✅ Works with OR without capabilities
- ✅ Graceful degradation
- ✅ No hard dependencies
- ✅ User choice (minimal vs full setup)

## Capability Categories

### Skills (Reusable Expertise)
- testing: TDD methodology
- debugging: Systematic troubleshooting
- code-review: Review checklist
- refactoring: Safe code improvements
- performance: Optimization techniques
- security: Security best practices

### Workflows (Multi-Step Processes)
- feature-development: 7-step new feature process
- bug-fix: 6-step bug resolution
- hotfix: Emergency fix workflow
- release: Version release process
- finalize-release: Post-release verification

### Commands (Single Actions)
- create-ticket: Generate ticket in PROJECT_STATUS.md
- analyze-coverage: Check test coverage
- generate-changelog: Create CHANGELOG.md

### Agents (Specialized Patterns)
- backend: Server-side patterns
- frontend: UI/UX patterns
- testing: QA patterns
- devops: Infrastructure patterns

## Extension Points

Users can add custom capabilities by:

1. Creating new files in `.proto-gear/`
2. Following naming conventions
3. Using YAML frontmatter metadata
4. Updating INDEX.md to list new capability
5. Agents automatically discover via INDEX.md

Example:
```bash
# Add custom workflow
touch .proto-gear/workflows/ml-model-training.md
# Edit INDEX.md to add entry
# Agents now discover it automatically!
```

---

*Last Updated: 2025-12-07*
*Template Version: v0.7.2*
