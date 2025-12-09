# Capability Metadata Schema v2.0

**Version**: 2.0.0
**For**: Proto Gear v0.8.0 Composition Engine
**Created**: 2025-12-09
**Status**: Draft

---

## Overview

This document defines the enhanced metadata schema for Proto Gear capabilities, enabling the v0.8.0 composition engine to support:

1. **Dependency Resolution** - Automatically include required capabilities
2. **Conflict Detection** - Warn about incompatible capability combinations
3. **Smart Composition** - Suggest compatible capabilities
4. **Agent Type Mapping** - Match capabilities to agent roles
5. **Usage Guidance** - Provide context for effective composition

## Schema Evolution

### v1.0 (Current - Pre-v0.8.0)

Capabilities use YAML frontmatter embedded in template files:

```yaml
---
name: "Test-Driven Development"
type: "skill"
version: "1.0.0"
description: "TDD methodology with red-green-refactor cycle"
tags: ["testing", "tdd", "quality"]
category: "testing"
relevance:
  - trigger: "write tests|testing|test coverage"
  - context: "Before implementing features"
dependencies: []
related: ["workflows/feature-development"]
author: "Proto Gear Team"
last_updated: "2025-11-05"
status: "stable"
---
```

**Limitations**:
- Dependencies are simple string arrays (no required/optional distinction)
- No conflict detection
- No composability metadata
- No agent role mapping

### v2.0 (Target - v0.8.0+)

Enhanced schema with composition engine support via **separate metadata.yaml files**.

---

## Design Decision: Separate metadata.yaml Files

### Why Separate Files?

**Option 1: Enhanced Frontmatter** (REJECTED)
```yaml
---
# In SKILL.template.md
name: "Testing Skill"
dependencies:
  required: ["workflows/bug-fix"]
  optional: ["skills/debugging"]
# ... more fields ...
---
```

**Problems**:
- Templates become cluttered with composition metadata
- Users see implementation details when reading templates
- Hard to update metadata without touching template content

**Option 2: Separate metadata.yaml** (CHOSEN ✅)
```yaml
# In skills/testing/metadata.yaml
name: "Testing Skill"
dependencies:
  required: ["workflows/bug-fix"]
  optional: ["skills/debugging"]
# ... composition fields ...
```

**Benefits**:
- Clean separation of concerns (content vs metadata)
- Templates remain focused on patterns and examples
- Easier to update metadata independently
- Composition engine can load metadata without parsing templates
- Future-proof for additional composition features

### Migration Path

1. **Backward Compatibility**: Templates keep existing frontmatter (v1.0 schema)
2. **New Metadata**: Add metadata.yaml alongside each capability
3. **Dual Support**: Composition engine reads both (metadata.yaml takes precedence)
4. **Future**: Consider removing frontmatter in v1.0.0 (keep templates pure markdown)

---

## metadata.yaml Schema

### Core Fields (Required)

```yaml
# Basic Information
name: "Test-Driven Development"  # Human-readable name
type: "skill"  # skill | workflow | command | agent
version: "1.0.0"  # Semantic versioning
description: "Short one-line description"

# Categorization
category: "testing"  # Primary category (testing, git, debugging, etc.)
tags: ["testing", "tdd", "quality", "red-green-refactor"]  # Searchable tags

# Status
status: "stable"  # stable | beta | experimental | deprecated
author: "Proto Gear Team"
last_updated: "2025-12-09"
```

### Composition Fields (Required for v0.8.0)

```yaml
# Dependencies - structured with types
dependencies:
  required: []  # Must have these capabilities
  optional: []  # Enhance functionality if present
  suggested: []  # Recommended but not required

# Conflicts - incompatible capabilities
conflicts: []  # Cannot use with these capabilities

# Composability - capabilities that work well together
composable_with: []  # Explicitly compatible capabilities

# Agent Roles - which agent types benefit from this
agent_roles:
  - "Testing Agent"
  - "Quality Assurance Agent"
  - "Full-Stack Developer Agent"
```

### Discovery Fields (Optional but Recommended)

```yaml
# Relevance - when to use this capability
relevance:
  triggers:  # Keywords/patterns that suggest this capability
    - "write tests"
    - "testing"
    - "test coverage"
    - "tdd"
  contexts:  # Situations when this is relevant
    - "Before implementing features"
    - "Fixing bugs"
    - "Refactoring code"

# Usage notes
usage_notes: |
  This capability works best when combined with a testing workflow
  and debugging skills. Ensure TESTING.md exists in the project.

# Integration requirements
required_files:  # Files that must exist
  - "TESTING.md"
  - "PROJECT_STATUS.md"

optional_files:  # Files that enhance functionality
  - "BRANCHING.md"
  - ".proto-gear/INDEX.md"
```

### Workflow-Specific Fields

```yaml
# Only for type: "workflow"
workflow:
  steps: 8  # Number of steps in workflow
  estimated_duration: "1-3 hours"  # Human-readable estimate
  outputs:  # What the workflow produces
    - "type: code"
    - "type: documentation"
    - "type: tests"
```

### Command-Specific Fields

```yaml
# Only for type: "command"
command:
  idempotent: true  # Can be run multiple times safely
  side_effects:  # What the command modifies
    - "PROJECT_STATUS.md"
  prerequisites:  # What must exist before running
    - "PROJECT_STATUS.md initialized"
```

---

## Complete Examples

### Example 1: Skill with Dependencies

```yaml
# skills/testing/metadata.yaml
name: "Test-Driven Development"
type: "skill"
version: "1.0.0"
description: "TDD methodology with red-green-refactor cycle for quality code"

category: "testing"
tags: ["testing", "tdd", "quality", "red-green-refactor", "coverage"]

status: "stable"
author: "Proto Gear Team"
last_updated: "2025-12-09"

dependencies:
  required: []
  optional:
    - "workflows/feature-development"
    - "workflows/bug-fix"
  suggested:
    - "skills/debugging"
    - "commands/analyze-coverage"

conflicts: []

composable_with:
  - "skills/debugging"
  - "skills/code-review"
  - "workflows/feature-development"
  - "workflows/bug-fix"
  - "workflows/refactoring"

agent_roles:
  - "Testing Agent"
  - "Quality Assurance Agent"
  - "Full-Stack Developer Agent"
  - "Backend Agent"
  - "Frontend Agent"

relevance:
  triggers:
    - "write tests"
    - "testing"
    - "test coverage"
    - "tdd"
    - "quality assurance"
  contexts:
    - "Before implementing features"
    - "Fixing bugs"
    - "Refactoring code"
    - "Building critical business logic"

usage_notes: |
  Test-Driven Development is a core practice that benefits most development tasks.
  Works best when combined with feature-development or bug-fix workflows.
  Requires TESTING.md to exist in the project for project-specific conventions.

required_files:
  - "TESTING.md"

optional_files:
  - "PROJECT_STATUS.md"
  - ".proto-gear/INDEX.md"
```

### Example 2: Workflow with Required Dependencies

```yaml
# workflows/bug-fix/metadata.yaml
name: "Bug Fix Workflow"
type: "workflow"
version: "1.0.0"
description: "Systematic workflow for investigating and fixing software defects"

category: "maintenance"
tags: ["bug", "fix", "debugging", "workflow", "testing"]

status: "stable"
author: "Proto Gear Team"
last_updated: "2025-12-09"

dependencies:
  required:
    - "skills/debugging"
    - "skills/testing"
  optional:
    - "commands/create-ticket"
    - "skills/code-review"
  suggested:
    - "commands/analyze-coverage"

conflicts: []

composable_with:
  - "skills/debugging"
  - "skills/testing"
  - "skills/code-review"
  - "commands/create-ticket"

agent_roles:
  - "Bug Fix Agent"
  - "Maintenance Agent"
  - "Full-Stack Developer Agent"
  - "Backend Agent"
  - "Frontend Agent"

relevance:
  triggers:
    - "bug"
    - "defect"
    - "error"
    - "issue"
    - "broken"
    - "not working"
    - "failing"
  contexts:
    - "When existing functionality is broken"
    - "After bug reports"
    - "When tests are failing"

usage_notes: |
  Bug fix workflow combines debugging skills with TDD practices.
  Always write a regression test before fixing the bug (RED phase).
  Requires debugging and testing skills to function properly.

required_files:
  - "PROJECT_STATUS.md"
  - "TESTING.md"

optional_files:
  - "BRANCHING.md"
  - "AGENTS.md"

workflow:
  steps: 9
  estimated_duration: "1-3 hours per bug"
  outputs:
    - "type: code"
    - "type: tests"
    - "type: documentation"
```

### Example 3: Command with Side Effects

```yaml
# commands/create-ticket/metadata.yaml
name: "Create Ticket"
type: "command"
version: "1.0.0"
description: "Create and properly document a ticket in PROJECT_STATUS.md"

category: "project-management"
tags: ["ticket", "planning", "status", "documentation", "sprint"]

status: "stable"
author: "Proto Gear Team"
last_updated: "2025-12-09"

dependencies:
  required: []
  optional:
    - "workflows/feature-development"
    - "workflows/bug-fix"
  suggested: []

conflicts: []

composable_with:
  - "workflows/feature-development"
  - "workflows/bug-fix"
  - "workflows/hotfix"
  - "workflows/release"

agent_roles:
  - "Project Manager Agent"
  - "All Agents"  # All agents can create tickets

relevance:
  triggers:
    - "create ticket"
    - "new ticket"
    - "add ticket"
    - "start work"
    - "new feature"
    - "bug report"
  contexts:
    - "When starting any new work item"
    - "Before beginning features"
    - "After discovering bugs"

usage_notes: |
  Create ticket command should be used before starting any trackable work.
  Integrates with feature-development and bug-fix workflows as Step 1.
  Updates PROJECT_STATUS.md to maintain single source of truth.

required_files:
  - "PROJECT_STATUS.md"

optional_files: []

command:
  idempotent: false  # Creates new ticket each time
  side_effects:
    - "PROJECT_STATUS.md (adds ticket, increments last_ticket_id)"
  prerequisites:
    - "PROJECT_STATUS.md must exist and have valid YAML metadata"
```

### Example 4: Capability with Conflicts

```yaml
# skills/cowboy-coding/metadata.yaml (hypothetical example)
name: "Cowboy Coding"
type: "skill"
version: "1.0.0"
description: "Move fast and break things - minimal planning approach"

category: "experimental"
tags: ["fast", "prototyping", "mvp", "exploratory"]

status: "experimental"
author: "Proto Gear Team"
last_updated: "2025-12-09"

dependencies:
  required: []
  optional: []
  suggested: []

conflicts:
  - "skills/testing"  # TDD conflicts with no-test approach
  - "skills/code-review"  # No review in cowboy mode
  - "workflows/feature-development"  # Too structured

composable_with:
  - "workflows/prototyping"  # If it existed

agent_roles:
  - "Rapid Prototyping Agent"
  - "Hackathon Agent"

relevance:
  triggers:
    - "quick prototype"
    - "mvp"
    - "proof of concept"
  contexts:
    - "Hackathons"
    - "Exploratory prototypes"
    - "Throwaway code"

usage_notes: |
  WARNING: This approach intentionally skips testing and code review.
  Only use for disposable prototypes or learning experiments.
  NEVER use for production code.

required_files: []
optional_files: []
```

---

## Validation Rules

### Required Field Validation

```python
# Pseudo-code for validation
REQUIRED_FIELDS = [
    "name",
    "type",
    "version",
    "description",
    "category",
    "tags",
    "status",
    "author",
    "last_updated",
    "dependencies",
    "conflicts",
    "composable_with",
    "agent_roles"
]

def validate_metadata(metadata):
    for field in REQUIRED_FIELDS:
        if field not in metadata:
            raise ValidationError(f"Missing required field: {field}")
```

### Type Validation

```python
TYPE_VALIDATORS = {
    "name": str,
    "type": lambda x: x in ["skill", "workflow", "command", "agent"],
    "version": lambda x: re.match(r"^\d+\.\d+\.\d+$", x),
    "dependencies": lambda x: all(k in ["required", "optional", "suggested"]
                                   for k in x.keys()),
    "conflicts": list,
    "composable_with": list,
    "agent_roles": list,
    "tags": list,
    "status": lambda x: x in ["stable", "beta", "experimental", "deprecated"]
}
```

### Dependency Validation

- All dependency references must exist as capabilities
- Circular dependencies not allowed
- Required dependencies must be satisfiable

### Conflict Validation

- Conflicts must reference existing capabilities
- Conflicts must be bidirectional (if A conflicts with B, B must conflict with A)

---

## Directory Structure

```
core/proto_gear_pkg/capabilities/
├── INDEX.template.md
├── skills/
│   ├── INDEX.template.md
│   ├── testing/
│   │   ├── SKILL.template.md          # Template content
│   │   └── metadata.yaml              # NEW: Composition metadata
│   ├── debugging/
│   │   ├── SKILL.template.md
│   │   └── metadata.yaml
│   └── ...
├── workflows/
│   ├── INDEX.template.md
│   ├── feature-development/
│   │   ├── WORKFLOW.template.md       # Template content
│   │   └── metadata.yaml              # NEW: Composition metadata
│   ├── bug-fix/
│   │   ├── WORKFLOW.template.md
│   │   └── metadata.yaml
│   └── ...
└── commands/
    ├── INDEX.template.md
    ├── create-ticket/
    │   ├── COMMAND.template.md        # Template content
    │   └── metadata.yaml              # NEW: Composition metadata
    └── ...
```

**Note**: Some capabilities are currently single files (e.g., `bug-fix.template.md`). We'll need to reorganize into directories to accommodate metadata.yaml.

---

## Backward Compatibility

### Phase 1: Dual Support (v0.8.0)

- Templates keep existing frontmatter (v1.0 schema)
- Add new metadata.yaml files (v2.0 schema)
- Composition engine reads both:
  - metadata.yaml takes precedence if exists
  - Falls back to frontmatter for older capabilities

### Phase 2: Migration (v0.8.x)

- Update all 20 capabilities with metadata.yaml
- Mark frontmatter as deprecated in documentation
- Provide migration tool: `pg migrate-metadata`

### Phase 3: Deprecation (v0.9.0+)

- Remove frontmatter from templates (keep pure markdown)
- Composition engine only reads metadata.yaml
- Templates focus solely on patterns and examples

---

## Usage in Composition Engine

### Loading Metadata

```python
def load_capability_metadata(capability_path):
    """Load metadata from metadata.yaml or fallback to frontmatter"""
    metadata_file = capability_path / "metadata.yaml"

    if metadata_file.exists():
        # v2.0 schema (preferred)
        return yaml.safe_load(metadata_file.read_text())
    else:
        # v1.0 schema (fallback)
        template_file = find_template_file(capability_path)
        return extract_frontmatter(template_file)
```

### Dependency Resolution

```python
def resolve_dependencies(capabilities):
    """Recursively resolve all required dependencies"""
    resolved = set(capabilities)

    for cap in capabilities:
        metadata = load_capability_metadata(cap)
        required = metadata["dependencies"]["required"]

        for dep in required:
            if dep not in resolved:
                resolved.add(dep)
                resolved.update(resolve_dependencies([dep]))

    return resolved
```

### Conflict Detection

```python
def detect_conflicts(capabilities):
    """Check for conflicting capabilities"""
    conflicts = []

    for cap in capabilities:
        metadata = load_capability_metadata(cap)
        cap_conflicts = metadata["conflicts"]

        for other_cap in capabilities:
            if other_cap in cap_conflicts:
                conflicts.append((cap, other_cap))

    return conflicts
```

---

## Future Enhancements (v0.9.0+)

### Capability Versioning

```yaml
compatibility:
  min_protogear_version: "0.8.0"
  max_protogear_version: null
  deprecated_in: null
  removed_in: null
```

### Performance Metadata

```yaml
performance:
  context_size: "large"  # small | medium | large
  load_priority: 1  # 1=highest, 10=lowest
```

### Multi-language Support

```yaml
i18n:
  supported_languages: ["en", "es", "fr"]
  default_language: "en"
```

---

## Migration Checklist

### For Each Capability (20 total)

- [ ] Create directory if single-file (e.g., `bug-fix/`)
- [ ] Move template into directory (e.g., `WORKFLOW.template.md`)
- [ ] Create `metadata.yaml` with v2.0 schema
- [ ] Populate all required fields
- [ ] Define dependencies (required/optional/suggested)
- [ ] Identify conflicts (if any)
- [ ] List composable_with capabilities
- [ ] Map to agent_roles
- [ ] Add usage_notes
- [ ] Validate metadata against schema
- [ ] Test with composition engine
- [ ] Update INDEX.template.md if needed

---

## References

- **v0.8.0 Kickoff Document**: `docs/dev/v0.8.0-composition-engine-kickoff.md`
- **Template Metadata Schema (v1.0)**: `docs/dev/template-metadata-schema.md`
- **Capabilities Roadmap**: `docs/dev/capabilities-roadmap.md`

---

*Last Updated: 2025-12-09*
*Status: Draft (for review)*
*Next: Implement validation logic and create metadata for 20 capabilities*
