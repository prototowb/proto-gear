# PROTO-023: Implement Template Auto-Discovery System

**Status**: Ready for Implementation
**Priority**: HIGH
**Type**: Feature / Bug Fix
**Estimated Time**: 2-3 hours
**Assigned**: Next development session

## Problem Statement

Currently, adding a new template requires manual CLI integration:
1. Create the `.template.md` file ✅ (easy)
2. Add a CLI flag like `--with-contributing` ❌ (manual, error-prone)
3. Add a generation function ❌ (boilerplate)
4. Wire it into the init flow ❌ (easy to forget)

**Result**: Templates exist in the package but don't work until manual integration.

**This happened in v0.5.0/v0.5.1**:
- 4 templates added (CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT)
- But they don't generate because steps 2-4 weren't completed
- Users install v0.5.1 and don't see these features

## Desired Behavior

**User expectation**: `pg init` generates ALL available templates.

**Developer expectation**: Add a `.template.md` file → It's immediately available, no code changes needed.

## Proposed Solution

### Phase 1: Template Discovery (Immediate)

Create a template registry system:

```python
def discover_templates():
    """Auto-discover all template files in the package"""
    template_dir = Path(__file__).parent
    templates = {}

    for template_file in template_dir.glob("*.template.md"):
        name = template_file.stem.replace(".template", "")
        templates[name] = {
            'path': template_file,
            'name': name.upper(),
            'description': extract_description(template_file)
        }

    return templates

def generate_all_templates(project_dir, context):
    """Generate all discovered templates"""
    templates = discover_templates()

    for name, info in templates.items():
        # Skip custom-generated ones
        if name in ['AGENTS', 'PROJECT_STATUS']:
            continue

        # Read template and replace placeholders
        content = info['path'].read_text()
        content = replace_placeholders(content, context)

        # Write to project
        output_file = project_dir / f"{name}.md"
        output_file.write_text(content)
```

### Phase 2: Smart Defaults (v0.6.0)

Make common templates generate by default:
- ✅ **Always**: AGENTS.md, PROJECT_STATUS.md, TESTING.md
- ✅ **If Git repo**: BRANCHING.md, CONTRIBUTING.md
- ✅ **If public/OSS**: SECURITY.md, CODE_OF_CONDUCT.md, ARCHITECTURE.md

### Phase 3: CLI Auto-Generation (v0.6.0)

Dynamically generate CLI flags from template metadata:

```markdown
---
name: "Contributing Guidelines"
flag: "contributing"
description: "Contribution guidelines for open-source projects"
default: true  # Generate by default if conditions met
conditions:
  - git_repo: true
  - public: true
---
```

Then auto-generate CLI:
- `--with-contributing` (auto-generated from template metadata)
- `--no-contributing` (opt-out if default: true)

## Implementation Plan

### Step 1: Quick Fix for v0.5.2 (30 minutes)

Add `--all` flag that generates everything:

```python
init_parser.add_argument(
    '--all',
    action='store_true',
    help='Generate ALL available templates (TESTING, BRANCHING, CONTRIBUTING, etc.)'
)
```

Then in `setup_agent_framework_only()`:

```python
if args.all or with_all_templates:
    # Generate all non-custom templates
    generate_template_file(current_dir, 'TESTING', context)
    generate_template_file(current_dir, 'BRANCHING', context)
    generate_template_file(current_dir, 'CONTRIBUTING', context)
    generate_template_file(current_dir, 'SECURITY', context)
    generate_template_file(current_dir, 'ARCHITECTURE', context)
    generate_template_file(current_dir, 'CODE_OF_CONDUCT', context)
```

### Step 2: Template Discovery (v0.6.0 - 2 hours)

Implement full auto-discovery as described in Phase 1.

### Step 3: Smart Defaults (v0.6.0 - 1 hour)

Implement conditional generation based on project context.

## Testing Plan

```bash
# Test v0.5.2 fix
pg init --all --dry-run
# Should show: AGENTS, PROJECT_STATUS, TESTING, BRANCHING,
#              CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT

# Test specific template
pg init --with-testing --dry-run

# Test default behavior (after v0.6.0)
pg init --dry-run
# Should auto-include common templates
```

## Success Criteria

- [ ] v0.5.2: `pg init --all` generates all 8 templates
- [ ] v0.6.0: Templates are auto-discovered from package
- [ ] v0.6.0: Smart defaults based on project type
- [ ] v0.6.0: Adding new template requires ZERO code changes

## Migration Path

1. v0.5.2: Add `--all` flag (backward compatible)
2. v0.6.0: Auto-discovery (backward compatible)
3. v0.7.0: Change default to generate more templates (document in changelog)

## Related Issues

- TEMPLATES_INTEGRATION_TICKET.md (can be closed after v0.5.2)
- Structure consolidation (completed in v0.5.1)

## Documentation Updates Needed

- Update CLAUDE.md with new template addition process
- Update user guides to explain `--all` flag
- Add template development guide

---

**Created**: 2025-11-09
**Type**: Feature + Bug Fix
**Milestone**: v0.5.2 (quick fix), v0.6.0 (full solution)
