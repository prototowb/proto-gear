# Agent Configuration Schema

**Version**: 1.0.0
**For**: Proto Gear v0.8.0 Sub-Agent Builder
**Created**: 2025-12-09
**Status**: Specification

---

## Overview

This document defines the YAML schema for configuring custom AI sub-agents in Proto Gear. Agents are compositions of capabilities (skills, workflows, commands) tailored for specific development tasks.

## Core Concept

**Agent = Capabilities + Instructions + Context Priority**

An agent configuration specifies:
1. **Which capabilities** to include (skills, workflows, commands)
2. **How to prioritize** information (context priority)
3. **What to focus on** (agent-specific instructions)
4. **Required files** for the agent to function

---

## Schema Definition

### Complete Structure

```yaml
# .proto-gear/agents/my-agent.yaml

# Agent Metadata
name: "Agent Name"
version: "1.0.0"
description: "What this agent does"
created: "2025-12-09"
author: "Your Name"

# Capability Composition
capabilities:
  skills:
    - "skill-name"
    - "another-skill"
  workflows:
    - "workflow-name"
  commands:
    - "command-name"

# Agent Behavior
context_priority:
  - "What to read/focus on first"
  - "Secondary priorities"
  - "Tertiary priorities"

agent_instructions:
  - "Specific instruction 1"
  - "Specific instruction 2"
  - "Specific instruction 3"

# File Dependencies
required_files:
  - "FILE.md"
  - "other-file.txt"

optional_files:
  - "optional-file.md"

# Agent Metadata
tags: ["tag1", "tag2"]
status: "active"  # active | inactive | experimental
```

### Field Descriptions

#### Metadata Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Human-readable agent name |
| `version` | string | Yes | Semantic version (e.g., "1.0.0") |
| `description` | string | Yes | Brief description of agent purpose |
| `created` | string | Yes | Creation date (YYYY-MM-DD) |
| `author` | string | No | Creator name |
| `tags` | list[string] | No | Searchable tags |
| `status` | string | No | Agent status (default: "active") |

#### Capabilities Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `capabilities.skills` | list[string] | No | Skills to include (e.g., ["testing", "debugging"]) |
| `capabilities.workflows` | list[string] | No | Workflows to include |
| `capabilities.commands` | list[string] | No | Commands to include |

**Notes**:
- Capability names are relative to category (e.g., "testing" not "skills/testing")
- At least one capability must be specified
- Dependencies are automatically resolved by composition engine

#### Behavior Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `context_priority` | list[string] | No | Ordered list of what agent should focus on |
| `agent_instructions` | list[string] | No | Specific behavioral instructions for agent |

#### Dependencies Section

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `required_files` | list[string] | No | Files that must exist for agent to function |
| `optional_files` | list[string] | No | Files that enhance agent functionality |

---

## Complete Examples

### Example 1: Testing Agent

```yaml
# .proto-gear/agents/testing-agent.yaml

name: "Testing Agent"
version: "1.0.0"
description: "Specialized agent for TDD, test automation, and quality assurance"
created: "2025-12-09"
author: "Proto Gear Team"

capabilities:
  skills:
    - "testing"
    - "debugging"
    - "code-review"
  workflows:
    - "feature-development"
    - "bug-fix"
  commands:
    - "analyze-coverage"

context_priority:
  - "Read TESTING.md for project-specific test conventions"
  - "Check test coverage reports in coverage/"
  - "Review recent test failures in PROJECT_STATUS.md"
  - "Examine test files before implementation files"
  - "Check CI/CD pipeline status"

agent_instructions:
  - "Always follow TDD: write tests before implementation"
  - "Aim for 80%+ test coverage for new code"
  - "Run full test suite before committing"
  - "Write descriptive test names that document behavior"
  - "Use Arrange-Act-Assert pattern in all tests"
  - "Add regression tests for every bug fix"

required_files:
  - "TESTING.md"
  - "PROJECT_STATUS.md"

optional_files:
  - "BRANCHING.md"
  - ".proto-gear/INDEX.md"

tags: ["testing", "tdd", "quality", "automation"]
status: "active"
```

**Capabilities Resolved**:
- Skills: testing, debugging, code-review
- Workflows: feature-development, bug-fix (+ their required dependencies)
- Commands: analyze-coverage
- **Total**: ~5-6 capabilities after dependency resolution

### Example 2: Bug Fix Agent

```yaml
# .proto-gear/agents/bug-fix-agent.yaml

name: "Bug Fix Agent"
version: "1.0.0"
description: "Specialized agent for investigating and fixing software defects"
created: "2025-12-09"
author: "Proto Gear Team"

capabilities:
  skills:
    - "debugging"
    - "testing"
  workflows:
    - "bug-fix"
  commands:
    - "create-ticket"

context_priority:
  - "Read bug reports in PROJECT_STATUS.md"
  - "Examine error logs and stack traces"
  - "Review recent commits that might have introduced the bug"
  - "Check related test files"
  - "Look for similar past bugs in git history"

agent_instructions:
  - "Always reproduce the bug before attempting a fix"
  - "Write a failing test that captures the bug (RED phase)"
  - "Fix the root cause, not just the symptom"
  - "Verify fix with both new test and manual testing"
  - "Update PROJECT_STATUS.md after completing fix"

required_files:
  - "PROJECT_STATUS.md"
  - "TESTING.md"

optional_files:
  - "BRANCHING.md"
  - "AGENTS.md"

tags: ["debugging", "bug-fix", "maintenance"]
status: "active"
```

### Example 3: Code Review Agent

```yaml
# .proto-gear/agents/code-review-agent.yaml

name: "Code Review Agent"
version: "1.0.0"
description: "Specialized agent for thorough code review and quality checks"
created: "2025-12-09"
author: "Proto Gear Team"

capabilities:
  skills:
    - "code-review"
    - "testing"
    - "security"
    - "performance"
  workflows: []
  commands: []

context_priority:
  - "Read pull request description and linked issues"
  - "Review changed files in order of importance"
  - "Check test coverage for changed code"
  - "Examine CONTRIBUTING.md for project standards"
  - "Review recent similar PRs for consistency"

agent_instructions:
  - "Check for correctness, maintainability, and performance"
  - "Ensure adequate test coverage (80%+ for new code)"
  - "Look for security vulnerabilities (OWASP top 10)"
  - "Verify naming follows project conventions"
  - "Provide constructive, specific feedback"
  - "Flag potential performance issues"

required_files: []

optional_files:
  - "CONTRIBUTING.md"
  - "SECURITY.md"
  - "TESTING.md"

tags: ["code-review", "quality", "security"]
status: "active"
```

### Example 4: Documentation Agent

```yaml
# .proto-gear/agents/documentation-agent.yaml

name: "Documentation Agent"
version: "1.0.0"
description: "Specialized agent for writing and maintaining technical documentation"
created: "2025-12-09"
author: "Proto Gear Team"

capabilities:
  skills:
    - "documentation"
  workflows:
    - "documentation-update"
  commands: []

context_priority:
  - "Read existing documentation first"
  - "Review code changes that need documentation"
  - "Check API changes that affect docs"
  - "Examine user feedback on documentation"

agent_instructions:
  - "Write clear, concise documentation for non-experts"
  - "Include code examples for all public APIs"
  - "Keep README.md, API docs, and inline comments synchronized"
  - "Use diagrams for complex architectures"
  - "Update docs as part of every feature"

required_files: []

optional_files:
  - "README.md"
  - "CONTRIBUTING.md"
  - "ARCHITECTURE.md"

tags: ["documentation", "technical-writing"]
status: "active"
```

### Example 5: Release Manager Agent

```yaml
# .proto-gear/agents/release-manager-agent.yaml

name: "Release Manager Agent"
version: "1.0.0"
description: "Specialized agent for managing software releases and deployments"
created: "2025-12-09"
author: "Proto Gear Team"

capabilities:
  skills:
    - "testing"
    - "documentation"
  workflows:
    - "release"
    - "finalize-release"
    - "complete-release"
  commands:
    - "generate-changelog"

context_priority:
  - "Review PROJECT_STATUS.md for completed features"
  - "Check all tests are passing"
  - "Verify CHANGELOG.md is up to date"
  - "Review branch status and merges"
  - "Check deployment readiness"

agent_instructions:
  - "Ensure all features are documented in CHANGELOG.md"
  - "Verify version numbers are correct everywhere"
  - "Run full test suite before releasing"
  - "Create GitHub release with comprehensive notes"
  - "Update PROJECT_STATUS.md after release"

required_files:
  - "PROJECT_STATUS.md"
  - "CHANGELOG.md"

optional_files:
  - "BRANCHING.md"
  - "TESTING.md"

tags: ["release", "deployment", "versioning"]
status: "active"
```

---

## Validation Rules

### Required Validations

1. **Agent must have valid metadata**:
   - `name` is non-empty string
   - `version` matches semantic versioning pattern
   - `description` is non-empty string
   - `created` is valid date (YYYY-MM-DD)

2. **Agent must have at least one capability**:
   - At least one of: skills, workflows, or commands must be non-empty

3. **All capabilities must exist**:
   - Each listed capability must be available in the system

4. **No circular dependencies**:
   - Resolved capability set must not contain circular dependencies

5. **No conflicts**:
   - Resolved capability set must not contain conflicting capabilities

### Optional Validations (Warnings)

1. **Empty instructions**: Warn if `agent_instructions` is empty
2. **No context priority**: Warn if `context_priority` is empty
3. **Missing recommended capabilities**: Suggest compatible capabilities
4. **Large capability set**: Warn if total capabilities > 15 (may be too broad)

---

## Directory Structure

```
project-root/
├── .proto-gear/
│   ├── INDEX.md
│   ├── agents/
│   │   ├── testing-agent.yaml
│   │   ├── bug-fix-agent.yaml
│   │   ├── code-review-agent.yaml
│   │   ├── documentation-agent.yaml
│   │   └── release-manager-agent.yaml
│   ├── skills/
│   ├── workflows/
│   └── commands/
└── ...
```

---

## Agent Lifecycle

### 1. Creation
```bash
# Interactive wizard
pg agent create my-agent

# From template
pg agent create my-agent --template testing-agent

# Manual creation
# Edit .proto-gear/agents/my-agent.yaml
```

### 2. Validation
```bash
# Validate agent configuration
pg agent validate my-agent

# Shows:
# - Missing capabilities
# - Circular dependencies
# - Conflicts
# - Recommendations
```

### 3. Usage
```bash
# List available agents
pg agent list

# Show agent details
pg agent show my-agent

# Use agent (future: agent activation)
# Currently: read agent config to understand focus
```

### 4. Updates
```bash
# Edit agent
pg agent edit my-agent

# Re-validates automatically
```

### 5. Deletion
```bash
# Remove agent
pg agent delete my-agent
```

---

## Agent vs Capabilities

| Feature | Capabilities | Agents |
|---------|-------------|---------|
| **What** | Building blocks | Compositions |
| **Purpose** | Reusable patterns | Task-specific configurations |
| **Location** | Package (proto_gear_pkg/) | Project (.proto-gear/agents/) |
| **Scope** | Universal | Project-specific |
| **Customization** | Fixed (template-based) | Fully customizable |
| **Dependencies** | Defined in metadata | Auto-resolved from capabilities |

---

## Best Practices

### 1. Agent Naming
- Use descriptive names: "Testing Agent" not "Agent 1"
- Follow role-based naming: "{Purpose} Agent"
- Be specific: "Backend Testing Agent" > "Testing Agent"

### 2. Capability Selection
- **Start minimal**: Include only essential capabilities
- **Let dependencies work**: Don't manually add transitive dependencies
- **Use recommendations**: Check `pg agent validate` suggestions

### 3. Instructions
- **Be specific**: "Run tests before commit" > "Test well"
- **Use measurable targets**: "80%+ coverage" > "Good coverage"
- **Order by priority**: Most important instructions first

### 4. Context Priority
- **Be explicit**: What files/sections to read first
- **Order matters**: First item is highest priority
- **Be practical**: Don't list 20+ items

### 5. Versioning
- **Increment on changes**: Update version when modifying agent
- **Use semantic versioning**: 1.0.0 → 1.1.0 (minor change) → 2.0.0 (major change)

---

## Future Enhancements (v0.9.0+)

### Agent Templates
```yaml
template: "testing-agent"  # Inherit from template
extends:  # Override specific fields
  agent_instructions:
    - "Additional instruction"
```

### Agent Inheritance
```yaml
extends: "base-developer-agent"  # Inherit configuration
capabilities:
  skills: ["+performance"]  # Add to inherited capabilities
```

### Dynamic Capabilities
```yaml
capabilities:
  auto: true  # Auto-select based on project detection
  include_recommended: true  # Include all recommendations
```

---

## References

- **Capability Metadata Schema**: `docs/dev/capability-metadata-schema-v2.md`
- **v0.8.0 Kickoff**: `docs/dev/v0.8.0-composition-engine-kickoff.md`
- **Composition Engine**: `core/proto_gear_pkg/capability_metadata.py`

---

*Last Updated: 2025-12-09*
*Status: Specification (ready for implementation)*
*Next: Implement agent_config.py module and CLI commands*
