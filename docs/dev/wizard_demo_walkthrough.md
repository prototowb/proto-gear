# Interactive Agent Creation Wizard - Demo Walkthrough

This document shows exactly what users experience when running `pg agent create`.

---

## Step 0: Launching the Wizard

```bash
$ pg agent create
```

**Output:**
```
🤖 Proto Gear Agent Creation Wizard

# 🤖 Agent Creation Wizard

Welcome to the Proto Gear Agent Builder!

## What are Agents?

Agents are **custom AI configurations** composed of:
- **Capabilities**: Skills, workflows, and commands
- **Context Priority**: What the agent should focus on
- **Instructions**: Specific behavioral guidelines
- **File Dependencies**: Required project files

## What You'll Do

1. ✏️  **Basic Info**: Name and describe your agent
2. 🎯 **Select Capabilities**: Choose from 20+ available capabilities
3. 📋 **Set Priorities**: Define what matters most
4. 📝 **Add Instructions**: Guide agent behavior
5. ✅ **Review & Save**: Preview and confirm

Let's get started!

? Ready to create your agent? (Y/n)
```

**User presses**: `Y`

---

## Step 1: Basic Information

```
=== Step 1: Basic Information ===

? Agent name: (e.g., 'My Testing Agent', 'Backend Developer Agent')
```

**User types**: `Backend Developer Agent`

```
? Short description: (one-line summary of what this agent does)
```

**User types**: `Specialized agent for backend API development with Node.js and databases`

```
? Author (optional): (your name or team name)
```

**User types**: `Development Team`

---

## Step 2: Select Capabilities

```
=== Step 2: Select Capabilities ===

Choose capabilities for your agent. You can select multiple items.
Tip: Use arrow keys to navigate, space to select, enter to confirm

Skills (core competencies):
? Select skills: (Use arrow keys, space to select, enter to confirm)
  ○ Code Review Best Practices - Systematic code review methodology for maintaining code quality
  ○ Debugging & Troubleshooting - Systematic debugging methodology for identifying and fixing issues
  ○ Technical Documentation - Writing clear, maintainable technical documentation
  ○ Performance Optimization - Optimizing code for better performance and resource usage
  ○ Code Refactoring - Improving code structure without changing functionality
  ○ Security Best Practices - Implementing security best practices to prevent vulnerabilities
  ○ Test-Driven Development - TDD methodology with red-green-refactor cycle
```

**User navigates with arrow keys, selects with space**:
- [x] Test-Driven Development
- [x] Debugging & Troubleshooting
- [x] Security Best Practices
- [x] Performance Optimization

**User presses**: `Enter`

```
Workflows (development processes):
? Select workflows: (Use arrow keys, space to select, enter to confirm)
  ○ Bug Fix Workflow - Systematic workflow for investigating and fixing defects
  ○ CI/CD Setup Workflow - Setting up continuous integration and deployment
  ○ Complete Release Workflow - Final release workflow with tagging and deployment
  ○ Dependency Update Workflow - Workflow for updating project dependencies safely
  ○ Documentation Update Workflow - Workflow for updating documentation
  ○ Feature Development Workflow - Complete workflow from planning to deployment
  ○ Finalize Release Workflow - Pre-release workflow for preparing releases
  ○ Hotfix Workflow - Emergency fix workflow for production issues
  ○ Monitoring Setup Workflow - Setting up monitoring and alerting
  ○ Release Workflow - Standard release workflow with testing and validation
```

**User selects**:
- [x] Feature Development Workflow
- [x] Bug Fix Workflow

**User presses**: `Enter`

```
Commands (automation tools):
? Select commands: (Use arrow keys, space to select, enter to confirm)
  ○ Analyze Test Coverage - Analyze test coverage and suggest improvements
  ○ Create Ticket - Create standardized tickets with proper formatting
  ○ Generate Changelog - Generate changelog from git commits
```

**User selects**:
- [x] Analyze Test Coverage

**User presses**: `Enter`

---

## Step 2b: Validation & Recommendations

```
Validating capability selections...
✓ Validation passed!

💡 Smart Recommendations
Based on your selections, you might also want:

  • Code Review Best Practices - Systematic code review methodology
  • Code Refactoring - Improving code structure without changing...
  • Technical Documentation - Writing clear, maintainable technical...
  • Generate Changelog - Generate changelog from git commits
  • Create Ticket - Create standardized tickets with proper format...

? Would you like to add any of these? (you can add them manually later) (y/N)
```

**User presses**: `N`

---

## Step 3: Context Priority

```
=== Step 3: Context Priority ===

Define what your agent should focus on (in order of importance).
Examples: 'Read README.md first', 'Check PROJECT_STATUS.md'

? Use default context priority template? (Y/n)
```

**User presses**: `N` (to customize)

```
Enter context priorities (empty line to finish):
? Priority 1: (or press enter to finish)
```

**User types**: `Read API documentation and OpenAPI specs`

```
? Priority 2: (or press enter to finish)
```

**User types**: `Check PROJECT_STATUS.md for current sprint goals`

```
? Priority 3: (or press enter to finish)
```

**User types**: `Review database schema and migration files`

```
? Priority 4: (or press enter to finish)
```

**User types**: `Examine existing API endpoints for patterns`

```
? Priority 5: (or press enter to finish)
```

**User presses**: `Enter` (finish)

---

## Step 4: Agent Instructions

```
=== Step 4: Agent Instructions ===

Define specific behavioral guidelines for your agent.
Examples: 'Follow TDD methodology', 'Update docs as you code'

? Use default instructions template? (Y/n)
```

**User presses**: `N` (to customize)

```
Enter agent instructions (empty line to finish):
? Instruction 1: (or press enter to finish)
```

**User types**: `Follow TDD: write tests before implementing features`

```
? Instruction 2: (or press enter to finish)
```

**User types**: `Validate all API inputs for security vulnerabilities`

```
? Instruction 3: (or press enter to finish)
```

**User types**: `Write comprehensive API documentation for all endpoints`

```
? Instruction 4: (or press enter to finish)
```

**User types**: `Optimize database queries for performance`

```
? Instruction 5: (or press enter to finish)
```

**User types**: `Update PROJECT_STATUS.md after completing each feature`

```
? Instruction 6: (or press enter to finish)
```

**User presses**: `Enter` (finish)

---

## Step 5: File Dependencies

```
=== Step 5: File Dependencies ===

Specify files your agent needs (optional).

? Add file dependencies? (y/N)
```

**User presses**: `Y`

```
Required files (must exist):
? Required file 1: (or press enter to skip)
```

**User types**: `PROJECT_STATUS.md`

```
? Required file 2: (or press enter to skip)
```

**User types**: `API_DOCUMENTATION.md`

```
? Required file 3: (or press enter to skip)
```

**User presses**: `Enter` (skip)

```
Optional files (nice to have):
? Optional file 1: (or press enter to skip)
```

**User types**: `ARCHITECTURE.md`

```
? Optional file 2: (or press enter to skip)
```

**User types**: `DATABASE_SCHEMA.md`

```
? Optional file 3: (or press enter to skip)
```

**User presses**: `Enter` (skip)

---

## Step 6: Preview & Confirm

```
=== Step 6: Preview & Confirm ===

Agent Configuration:
  Name: Backend Developer Agent
  Description: Specialized agent for backend API development with Node.js and databases
  Author: Development Team
  Version: 1.0.0
  Created: 2025-12-09

Capabilities:
  Skills (4): testing, debugging, security, performance
  Workflows (2): feature-development, bug-fix
  Commands (1): analyze-coverage

Context Priority:
  1. Read API documentation and OpenAPI specs
  2. Check PROJECT_STATUS.md for current sprint goals
  3. Review database schema and migration files
  4. Examine existing API endpoints for patterns

Agent Instructions:
  1. Follow TDD: write tests before implementing features
  2. Validate all API inputs for security vulnerabilities
  3. Write comprehensive API documentation for all endpoints
  4. Optimize database queries for performance
  5. Update PROJECT_STATUS.md after completing each feature

Required Files:
  - PROJECT_STATUS.md
  - API_DOCUMENTATION.md

Optional Files:
  - ARCHITECTURE.md
  - DATABASE_SCHEMA.md

? Create this agent? (Y/n)
```

**User presses**: `Y`

---

## Final Output

```
✓ Agent created successfully!

Saved to: .proto-gear/agents/backend-developer-agent.yaml

Next steps:
  1. Review: pg agent show backend-developer-agent
  2. Validate: pg agent validate backend-developer-agent
  3. Customize: Edit .proto-gear/agents/backend-developer-agent.yaml as needed
```

---

## Generated YAML File

**File**: `.proto-gear/agents/backend-developer-agent.yaml`

```yaml
name: Backend Developer Agent
version: 1.0.0
description: Specialized agent for backend API development with Node.js and databases
created: '2025-12-09'
author: Development Team

capabilities:
  skills:
  - testing
  - debugging
  - security
  - performance
  workflows:
  - feature-development
  - bug-fix
  commands:
  - analyze-coverage

context_priority:
- Read API documentation and OpenAPI specs
- Check PROJECT_STATUS.md for current sprint goals
- Review database schema and migration files
- Examine existing API endpoints for patterns

agent_instructions:
- 'Follow TDD: write tests before implementing features'
- Validate all API inputs for security vulnerabilities
- Write comprehensive API documentation for all endpoints
- Optimize database queries for performance
- Update PROJECT_STATUS.md after completing each feature

required_files:
- PROJECT_STATUS.md
- API_DOCUMENTATION.md

optional_files:
- ARCHITECTURE.md
- DATABASE_SCHEMA.md

tags: []
status: active
```

---

## Validating the Agent

```bash
$ pg agent validate backend-developer-agent
```

**Output:**
```
=== Validating Backend Developer Agent ===

✓ Agent configuration is valid!

💡 Recommended capabilities to add:
  - skills/code-review
  - skills/refactoring
  - skills/documentation
  - commands/create-ticket
  - commands/generate-changelog
  - workflows/hotfix
```

---

## Using the Agent

```bash
$ pg agent show backend-developer-agent
```

**Output:**
```
=== Backend Developer Agent ===

Version: 1.0.0
Status: active
Created: 2025-12-09
Author: Development Team

Description:
  Specialized agent for backend API development with Node.js and databases

Capabilities:
  Skills: testing, debugging, security, performance
  Workflows: feature-development, bug-fix
  Commands: analyze-coverage

Context Priority:
  1. Read API documentation and OpenAPI specs
  2. Check PROJECT_STATUS.md for current sprint goals
  3. Review database schema and migration files
  4. Examine existing API endpoints for patterns

Agent Instructions:
  1. Follow TDD: write tests before implementing features
  2. Validate all API inputs for security vulnerabilities
  3. Write comprehensive API documentation for all endpoints
  4. Optimize database queries for performance
  5. Update PROJECT_STATUS.md after completing each feature

Required Files:
  - PROJECT_STATUS.md
  - API_DOCUMENTATION.md

Optional Files:
  - ARCHITECTURE.md
  - DATABASE_SCHEMA.md

Tags: (none)
```

---

## Key Features Demonstrated

### ✅ **Multi-Select Capabilities**
- Arrow keys to navigate
- Space to select/deselect
- Visual checkboxes
- Grouped by type (skills, workflows, commands)

### ✅ **Real-Time Validation**
- Checks capabilities exist
- Detects circular dependencies
- Identifies conflicts
- Shows clear error messages

### ✅ **Smart Recommendations**
- Based on selected capabilities
- Uses composable_with metadata
- Suggests compatible additions
- Non-intrusive (user can decline)

### ✅ **Template Defaults**
- Quick setup for common patterns
- One-key selection (Y/n)
- Sensible defaults provided
- Full customization available

### ✅ **Clear Preview**
- Shows complete configuration
- Organized by section
- Easy to review before saving
- Option to cancel/restart

### ✅ **Helpful Next Steps**
- Shows where file was saved
- Suggests validation command
- Recommends customization
- Clear path forward

---

## Error Handling Examples

### Example 1: Missing Questionary Package

```bash
$ pg agent create
```

**Output:**
```
Interactive wizard requires 'questionary' package
Install with: pip install questionary
```

### Example 2: Keyboard Interrupt

```bash
$ pg agent create
[User presses Ctrl+C during wizard]
```

**Output:**
```
Agent creation cancelled by user
```

### Example 3: No Capabilities Selected

```bash
[User doesn't select any capabilities]
```

**Output:**
```
Agent creation cancelled - no capabilities selected
```

### Example 4: File Already Exists

```bash
$ pg agent create
[User creates agent named "backend-developer-agent"]
[Agent file already exists]
```

**Output:**
```
Agent file already exists. Overwrite? (yes/no): no
Agent not saved
```

---

## Comparison: Manual vs Wizard

### Manual Creation (Before)

1. Read schema documentation (5-10 min)
2. Find example agent (2-3 min)
3. Copy and edit YAML (10-15 min)
4. Remember all field names
5. Manually validate
6. Fix errors and repeat

**Total Time**: 20-30 minutes

### Wizard Creation (Now)

1. Run `pg agent create`
2. Follow 6 guided steps (3-5 min)
3. Select from menus
4. Real-time validation
5. Auto-saved with correct format

**Total Time**: 3-5 minutes

**Time Savings**: 75-85% faster! ⚡

---

## User Experience Highlights

### Excellent UX Elements

1. **Progressive Disclosure**
   - Shows information when needed
   - Doesn't overwhelm with options
   - Clear step-by-step flow

2. **Helpful Hints**
   - Inline examples
   - Keyboard shortcuts shown
   - Clear instructions

3. **Visual Feedback**
   - Color-coded output
   - Checkboxes for selections
   - Progress through steps

4. **Error Prevention**
   - Validation before saving
   - Clear error messages
   - Option to fix mistakes

5. **Smart Defaults**
   - One-key template selection
   - Sensible fallbacks
   - Customization available

---

*End of Wizard Demo Walkthrough*
