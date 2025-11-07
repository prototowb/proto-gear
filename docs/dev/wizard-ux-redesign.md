# Interactive Wizard UX Redesign - Proto Gear v0.5.0

**Date**: 2025-11-07
**Status**: Design Proposal
**Target**: v0.5.0 or v0.4.1

---

## Current State Analysis

### Current Wizard Flow (v0.4.0)

```
1. Project Detection (auto, shown)
2. Branching Strategy? (y/n)
   └─ If yes: Ticket Prefix?
3. Capabilities System? (y/n)
4. Configuration Summary
5. Confirm & Generate
```

### Current Limitations

1. **All-or-nothing for capabilities** - Can't select individual skills/workflows/commands
2. **No template customization** - AGENTS.md, PROJECT_STATUS.md always generated
3. **Limited testing options** - TESTING.md only via CLI flag, not in wizard
4. **No preview** - Can't see what files will contain before generating
5. **Linear flow** - Can't go back to change selections
6. **Missing advanced options**:
   - Custom agent roles
   - Specific capability templates
   - Alternative workflow patterns

---

## Proposed UX Improvements

### Design Goals

1. **Granular Control** - Let users pick exactly what they want
2. **Sensible Defaults** - Quick path for common use cases
3. **Progressive Disclosure** - Simple first, advanced options available
4. **Flexibility** - Easy to add/remove selections
5. **Transparency** - Show what will be created before confirming

---

## Option 1: Preset-Based Wizard (Recommended)

### Step 1: Choose Preset

```
╔═══════════════════════════════════════════════════════════╗
║         [CONFIG] Setup Configuration                       ║
╚═══════════════════════════════════════════════════════════╝

Choose a preset configuration or customize:

  ❯ ⚡ Quick Start (Recommended)
    📦 Full Setup (All features)
    🎯 Minimal (Core templates only)
    🔧 Custom (Choose what you want)
```

**Presets Defined**:

#### ⚡ Quick Start (Default)
- Core templates: AGENTS.md, PROJECT_STATUS.md
- Branching: If git detected
- Capabilities: Included
- Testing: Not included

#### 📦 Full Setup
- All core templates
- Branching: Always
- Capabilities: All categories
- Testing: Included
- Additional: GitHub templates (.github/)

#### 🎯 Minimal
- Core templates only: AGENTS.md, PROJECT_STATUS.md
- No branching
- No capabilities
- No testing

#### 🔧 Custom
- Proceeds to detailed customization

### Step 2a: Quick Path (If preset chosen)

```
╔═══════════════════════════════════════════════════════════╗
║         [CONFIG] Quick Start Configuration                 ║
╚═══════════════════════════════════════════════════════════╝

Selected preset: ⚡ Quick Start

What will be created:
  [Y] AGENTS.md - AI agent collaboration guide
  [Y] PROJECT_STATUS.md - Project state tracker
  [Y] BRANCHING.md - Git workflow (git detected)
  [Y] .proto-gear/ - Universal capabilities (8 files)

Ticket prefix: VUE-COURSE-APP

  ❯ ✓ Continue with this setup
    ← Back to preset selection
    🔧 Customize options
```

### Step 2b: Custom Path (If custom chosen)

#### Stage 1: Core Templates

```
╔═══════════════════════════════════════════════════════════╗
║         [CONFIG] Core Templates                            ║
╚═══════════════════════════════════════════════════════════╝

Select core templates to generate:

  [✓] AGENTS.md - AI agent collaboration guide (always included)
  [✓] PROJECT_STATUS.md - Project state tracker (always included)
  [ ] TESTING.md - TDD workflow and testing patterns
  [ ] CONTRIBUTING.md - Contributor guidelines
  [ ] CODE_OF_CONDUCT.md - Community standards

  ❯ Continue
    ← Back
```

#### Stage 2: Git Workflow

```
╔═══════════════════════════════════════════════════════════╗
║         [GIT] Git Workflow Configuration                   ║
╚═══════════════════════════════════════════════════════════╝

[Y] Git repository detected

Configure Git workflow:

  [✓] BRANCHING.md - Branch naming & commit conventions
      └─ Ticket prefix: [VUE-COURSE-APP___________]

  [ ] .github/pull_request_template.md
  [ ] .github/ISSUE_TEMPLATE/ (bug, feature, question)
  [ ] .gitignore enhancements

  ❯ Continue
    ← Back
    ⊗ Skip Git configuration
```

#### Stage 3: Universal Capabilities

```
╔═══════════════════════════════════════════════════════════╗
║         [SETUP] Universal Capabilities System              ║
╚═══════════════════════════════════════════════════════════╝

The capability system provides modular patterns for AI agents.

Select categories to include:

  [✓] Skills (1 template)
      └─ [✓] Testing/TDD - Red-green-refactor cycle

  [✓] Workflows (1 template)
      └─ [✓] Feature Development - 7-step process

  [✓] Commands (1 template)
      └─ [✓] Create Ticket - Ticket documentation

  [✓] Agents (index only)

  [ ] ⊗ Skip capabilities entirely

  ❯ Continue
    ← Back
    🔍 Preview capability files
```

##### Expanded View (Optional)

```
[✓] Skills (Select individual templates)
    [✓] Testing/TDD - Red-green-refactor cycle
    [ ] Debugging - Systematic debugging approach
    [ ] Code Review - Review checklist and patterns
    [ ] Refactoring - Safe refactoring strategies
    [ ] Performance - Profiling and optimization

[✓] Workflows
    [✓] Feature Development - 7-step process
    [ ] Bug Fix - Issue triage to deployment
    [ ] Hotfix - Emergency patch workflow
    [ ] Release - Version bump to publish

[✓] Commands
    [✓] Create Ticket - Ticket documentation
    [ ] Update Status - Status tracking
    [ ] Create Branch - Branch from ticket
    [ ] Close Ticket - Completion checklist
```

#### Stage 4: Configuration Summary

```
╔═══════════════════════════════════════════════════════════╗
║         [CONFIG] Configuration Summary                     ║
╚═══════════════════════════════════════════════════════════╝

Project: vue-course-app
Type: Node.js Project (Vue.js)

Core Templates (3):
  [Y] AGENTS.md
  [Y] PROJECT_STATUS.md
  [Y] TESTING.md

Git Workflow (2):
  [Y] BRANCHING.md (prefix: VUE-COURSE-APP)
  [Y] .github/pull_request_template.md

Capabilities (5 files in .proto-gear/):
  [Y] Skills: testing/SKILL.md
  [Y] Workflows: feature-development.md
  [Y] Commands: create-ticket.md
  [Y] Index files: INDEX.md (x4)

Total: 10 files

  ❯ ✓ Generate files
    ← Back to modify
    🔍 Preview files
    ⊗ Cancel
```

---

## Option 2: Checklist-Based Wizard

Single screen with expandable sections:

```
╔═══════════════════════════════════════════════════════════╗
║         [CONFIG] Proto Gear Setup                          ║
╚═══════════════════════════════════════════════════════════╝

Select what to include (Space to toggle, Enter to confirm):

  ▼ Core Templates
    [✓] AGENTS.md - AI agent collaboration
    [✓] PROJECT_STATUS.md - State tracker
    [ ] TESTING.md - TDD patterns
    [ ] CONTRIBUTING.md

  ▼ Git Workflow
    [✓] BRANCHING.md (Ticket prefix: VUE-COURSE___)
    [ ] GitHub templates (.github/)
    [ ] Enhanced .gitignore

  ▼ Universal Capabilities (.proto-gear/)
    [✓] All capabilities (8 files)
    [ ] Custom selection →

  ❯ ✓ Continue
    ⊗ Cancel

Use ↑↓ arrows, Space to select, Enter to confirm
Press 'h' for help
```

---

## Option 3: Multi-Select with Categories

```
╔═══════════════════════════════════════════════════════════╗
║         [CONFIG] Select Templates                          ║
╚═══════════════════════════════════════════════════════════╝

Select all templates you want to generate:
(Space to toggle, 'a' to select all, 'n' to select none)

CORE TEMPLATES:
  [✓] AGENTS.md - AI agent collaboration guide
  [✓] PROJECT_STATUS.md - Project state tracker
  [ ] TESTING.md - TDD workflow patterns
  [ ] CONTRIBUTING.md - Contribution guidelines

GIT WORKFLOW:
  [✓] BRANCHING.md - Branch naming & conventions
  [ ] .github/pull_request_template.md
  [ ] .github/ISSUE_TEMPLATE/

CAPABILITIES:
  [✓] .proto-gear/skills/ (TDD methodology)
  [✓] .proto-gear/workflows/ (Feature development)
  [✓] .proto-gear/commands/ (Create ticket)

  ❯ Continue (8 files selected)
    Back
```

---

## Recommended Approach: Option 1 (Preset-Based)

### Why Preset-Based is Best

1. **New users** → Quick Start preset (zero decisions)
2. **Power users** → Custom path (full control)
3. **Team leads** → Full Setup preset (everything)
4. **Minimalists** → Minimal preset

### Implementation Strategy

#### Phase 1: Add Presets (v0.4.1 or v0.5.0)

```python
PRESETS = {
    'quick': {
        'name': 'Quick Start',
        'emoji': '⚡',
        'description': 'Core templates + capabilities (recommended)',
        'config': {
            'core': ['AGENTS', 'PROJECT_STATUS'],
            'branching': 'auto',  # Only if git detected
            'testing': False,
            'capabilities': True,
            'github_templates': False,
        }
    },
    'full': {
        'name': 'Full Setup',
        'emoji': '📦',
        'description': 'All features enabled',
        'config': {
            'core': ['AGENTS', 'PROJECT_STATUS', 'TESTING', 'CONTRIBUTING'],
            'branching': True,
            'testing': True,
            'capabilities': True,
            'github_templates': True,
        }
    },
    'minimal': {
        'name': 'Minimal',
        'emoji': '🎯',
        'description': 'Just the essentials',
        'config': {
            'core': ['AGENTS', 'PROJECT_STATUS'],
            'branching': False,
            'testing': False,
            'capabilities': False,
            'github_templates': False,
        }
    },
    'custom': {
        'name': 'Custom',
        'emoji': '🔧',
        'description': 'Choose exactly what you want',
        'config': None,  # Triggers custom wizard flow
    }
}
```

#### Phase 2: Granular Capabilities (v0.5.0)

```python
CAPABILITY_TEMPLATES = {
    'skills': {
        'testing': {'name': 'TDD Methodology', 'included': True},
        'debugging': {'name': 'Systematic Debugging', 'included': False},
        'code_review': {'name': 'Code Review Patterns', 'included': False},
        'refactoring': {'name': 'Safe Refactoring', 'included': False},
    },
    'workflows': {
        'feature_development': {'name': 'Feature Development', 'included': True},
        'bug_fix': {'name': 'Bug Fix Process', 'included': False},
        'hotfix': {'name': 'Hotfix Workflow', 'included': False},
        'release': {'name': 'Release Process', 'included': False},
    },
    'commands': {
        'create_ticket': {'name': 'Create Ticket', 'included': True},
        'update_status': {'name': 'Update Status', 'included': False},
        'create_branch': {'name': 'Create Branch', 'included': False},
        'close_ticket': {'name': 'Close Ticket', 'included': False},
    }
}
```

---

## Additional Enhancements

### 1. Preview Mode

Allow users to preview file contents before generating:

```
? Preview AGENTS.md content? (y/n) y

╔═══════════════════════════════════════════════════════════╗
║         Preview: AGENTS.md (first 20 lines)                ║
╚═══════════════════════════════════════════════════════════╝

# AGENTS - AI Agent Collaboration Framework

> **Framework**: Proto Gear Agent Framework
> **Project**: vue-course-app
> **Sprint**: Feature Development

## Agent Roles

### 1. Planning Agent
Responsibilities:
- Break down epics into tickets
[...]

Press 'q' to close preview
```

### 2. Dry Run from Wizard

Add option to run in dry-run mode directly from wizard:

```
  ❯ ✓ Generate files
    🔍 Dry run (preview only, don't create files)
    ← Back to modify
```

### 3. Save/Load Presets

Allow users to save custom configurations:

```
  ❯ ✓ Generate files
    💾 Save this configuration as preset
    📂 Load saved preset
    ← Back
```

### 4. Help System

Context-sensitive help for each option:

```
Press 'h' for help on current screen
Press '?' next to any option for details
```

---

## Migration Path

### v0.4.0 → v0.4.1 (Minor)
- Add preset selection as first step
- Keep existing detailed flow as "Custom" preset
- Maintain backward compatibility with CLI flags

### v0.5.0 (Major)
- Full granular capability selection
- Additional templates (CONTRIBUTING.md, etc.)
- GitHub templates integration
- Preview mode
- Save/load presets

---

## Implementation Estimate

### Phase 1: Preset System (v0.4.1)
- **Effort**: 4-6 hours
- **Files**: `interactive_wizard.py`, add preset selection
- **Breaking**: None (additive)

### Phase 2: Granular Capabilities (v0.5.0)
- **Effort**: 8-12 hours
- **Files**: `interactive_wizard.py`, `proto_gear.py`, new capability templates
- **Breaking**: Minor (additional templates)

---

## User Feedback Questions

Before implementing, consider asking users:

1. Do you prefer presets or granular selection?
2. How often do you want ALL capabilities vs. selective ones?
3. Would you use saved presets for different project types?
4. Is preview mode important before generating?
5. Should AGENTS.md and PROJECT_STATUS.md ever be optional?

---

## Recommendation

**Implement Option 1 (Preset-Based) in two phases:**

1. **v0.4.1**: Add preset selection with 4 presets (quick, full, minimal, custom)
2. **v0.5.0**: Add granular capability selection within "custom" path

This provides:
- **Immediate value** for new users (quick start)
- **Flexibility** for power users (custom)
- **Future-proof** architecture (easy to add more options)

