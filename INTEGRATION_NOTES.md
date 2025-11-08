# Integration Notes for v0.5.0 Templates

**Date**: 2025-11-08
**Workstream**: Templates (v0.5.0)
**Status**: Templates Created, Integration Pending

---

## Completed

✅ Created 4 comprehensive template files (2,079 lines):
- `core/CONTRIBUTING.template.md` - Contribution guidelines
- `core/SECURITY.template.md` - Security policies
- `core/ARCHITECTURE.template.md` - System design docs
- `core/CODE_OF_CONDUCT.template.md` - Community guidelines

✅ All templates follow existing format:
- Use `{{VARIABLE}}` placeholders
- Comprehensive yet adaptable
- Tech-stack agnostic
- Professional and complete

---

## Pending Integration into proto_gear.py

### 1. Add CLI Flags

**Location**: Lines 1035-1044 in `core/proto_gear.py`

**Add after `--with-capabilities` and before `--no-interactive`**:

```python
    init_parser.add_argument(
        '--with-contributing',
        action='store_true',
        help='Generate CONTRIBUTING.md with contribution guidelines'
    )
    init_parser.add_argument(
        '--with-security',
        action='store_true',
        help='Generate SECURITY.md with security policies'
    )
    init_parser.add_argument(
        '--with-architecture',
        action='store_true',
        help='Generate ARCHITECTURE.md with system design documentation'
    )
    init_parser.add_argument(
        '--with-coc',
        action='store_true',
        help='Generate CODE_OF_CONDUCT.md with community guidelines'
    )
```

### 2. Create Template Generation Functions

**Location**: After `generate_branching_doc()` function (around line 456)

**Add these 4 functions** (following the pattern of `generate_branching_doc`):

```python
def generate_contributing_doc(project_name, ticket_prefix, git_config, generation_date, framework):
    """Generate CONTRIBUTING.md from template"""
    template_path = Path(__file__).parent / 'CONTRIBUTING.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = content.replace('{{TICKET_PREFIX}}', ticket_prefix)
        content = content.replace('{{GENERATION_DATE}}', generation_date)
        content = content.replace('{{FRAMEWORK}}', framework or 'Generic')

        # TODO: Add framework-specific placeholders
        # - {{PREREQUISITES}}
        # - {{SETUP_INSTRUCTIONS}}
        # - {{VERIFY_COMMAND}}
        # - {{RUN_TESTS}}
        # - {{COVERAGE_TARGET}}
        # - etc.

        return content
    except Exception as e:
        print(f"Error generating contributing doc: {e}")
        return None


def generate_security_doc(project_name, generation_date):
    """Generate SECURITY.md from template"""
    template_path = Path(__file__).parent / 'SECURITY.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = template.replace('{{GENERATION_DATE}}', generation_date)

        # TODO: Add security-specific placeholders
        # - {{SECURITY_CONTACT}}
        # - {{SUPPORTED_VERSIONS_TABLE}}
        # - {{SECURITY_REPORTING_CHANNEL}}
        # - {{ACKNOWLEDGMENT_TIME}}
        # - etc.

        return content
    except Exception as e:
        print(f"Error generating security doc: {e}")
        return None


def generate_architecture_doc(project_name, framework, generation_date):
    """Generate ARCHITECTURE.md from template"""
    template_path = Path(__file__).parent / 'ARCHITECTURE.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = template.replace('{{FRAMEWORK}}', framework or 'Generic')
        content = template.replace('{{GENERATION_DATE}}', generation_date)

        # TODO: Add architecture-specific placeholders
        # - {{ARCHITECTURE_STYLE}}
        # - {{COMPONENT_1_NAME}}
        # - {{LAYER_1_NAME}}
        # - etc.

        return content
    except Exception as e:
        print(f"Error generating architecture doc: {e}")
        return None


def generate_code_of_conduct_doc(project_name, generation_date):
    """Generate CODE_OF_CONDUCT.md from template"""
    template_path = Path(__file__).parent / 'CODE_OF_CONDUCT.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Basic placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = template.replace('{{GENERATION_DATE}}', generation_date)

        # TODO: Add CoC-specific placeholders
        # - {{CONDUCT_CONTACT}}
        # - {{COMMUNICATION_CHANNELS}}
        # - {{ACKNOWLEDGMENT_TIME}}
        # - etc.

        return content
    except Exception as e:
        print(f"Error generating code of conduct: {e}")
        return None
```

### 3. Update `run_simple_protogear_init()` Function

**Location**: Around lines 650-800

**Add parameters to function signature**:
```python
def run_simple_protogear_init(dry_run=False, with_branching=False, ticket_prefix=None,
                              with_capabilities=False, capabilities_config=None,
                              with_contributing=False, with_security=False,
                              with_architecture=False, with_coc=False):
```

**Add template generation calls** (after BRANCHING.md generation, around line 780):

```python
            # Generate CONTRIBUTING.md if requested
            if with_contributing:
                contributing_content = generate_contributing_doc(
                    project_name, ticket_prefix, git_config, generation_date,
                    project_info.get('framework', '')
                )
                if contributing_content:
                    contrib_file = current_dir / 'CONTRIBUTING.md'
                    contrib_file.write_text(contributing_content, encoding='utf-8')
                    files_created.append('CONTRIBUTING.md')
                    print(f"{Colors.GREEN}+ CONTRIBUTING.md created{Colors.ENDC}")

            # Generate SECURITY.md if requested
            if with_security:
                security_content = generate_security_doc(project_name, generation_date)
                if security_content:
                    security_file = current_dir / 'SECURITY.md'
                    security_file.write_text(security_content, encoding='utf-8')
                    files_created.append('SECURITY.md')
                    print(f"{Colors.GREEN}+ SECURITY.md created{Colors.ENDC}")

            # Generate ARCHITECTURE.md if requested
            if with_architecture:
                arch_content = generate_architecture_doc(
                    project_name, project_info.get('framework', ''), generation_date
                )
                if arch_content:
                    arch_file = current_dir / 'ARCHITECTURE.md'
                    arch_file.write_text(arch_content, encoding='utf-8')
                    files_created.append('ARCHITECTURE.md')
                    print(f"{Colors.GREEN}+ ARCHITECTURE.md created{Colors.ENDC}")

            # Generate CODE_OF_CONDUCT.md if requested
            if with_coc:
                coc_content = generate_code_of_conduct_doc(project_name, generation_date)
                if coc_content:
                    coc_file = current_dir / 'CODE_OF_CONDUCT.md'
                    coc_file.write_text(coc_content, encoding='utf-8')
                    files_created.append('CODE_OF_CONDUCT.md')
                    print(f"{Colors.GREEN}+ CODE_OF_CONDUCT.md created{Colors.ENDC}")
```

### 4. Update Dry-Run Output

**Location**: Around line 795

**Add to dry-run output**:
```python
        if with_contributing:
            print("  - CONTRIBUTING.md (contribution guidelines)")
        if with_security:
            print("  - SECURITY.md (security policies)")
        if with_architecture:
            print("  - ARCHITECTURE.md (system design)")
        if with_coc:
            print("  - CODE_OF_CONDUCT.md (community guidelines)")
```

### 5. Update CLI Argument Passing

**Location**: Lines 1088-1105

**Update both wizard and CLI paths**:

```python
# For wizard path (line 1088):
result = run_simple_protogear_init(
    dry_run=args.dry_run,
    with_branching=wizard_config.get('with_branching', False),
    ticket_prefix=wizard_config.get('ticket_prefix'),
    with_capabilities=wizard_config.get('with_capabilities', False),
    capabilities_config=wizard_config.get('capabilities_config'),
    with_contributing=wizard_config.get('with_contributing', False),
    with_security=wizard_config.get('with_security', False),
    with_architecture=wizard_config.get('with_architecture', False),
    with_coc=wizard_config.get('with_coc', False)
)

# For CLI path (line 1100):
result = run_simple_protogear_init(
    dry_run=args.dry_run,
    with_branching=args.with_branching,
    ticket_prefix=args.ticket_prefix,
    with_capabilities=args.with_capabilities,
    with_contributing=args.with_contributing,
    with_security=args.with_security,
    with_architecture=args.with_architecture,
    with_coc=args.with_coc
)
```

### 6. Update Interactive Wizard (Optional)

**File**: `core/interactive_wizard.py`

Add options for new templates in the wizard UI.

---

## Testing Commands

After integration:

```bash
# Test dry-run with all templates
pg init --dry-run --with-contributing --with-security --with-architecture --with-coc

# Test actual generation
pg init --with-branching --with-contributing --ticket-prefix TEST

# Test single template
pg init --with-security --dry-run
```

---

## Template Variable Mapping

Each template has many `{{VARIABLE}}` placeholders that need values. Here's a suggested approach:

### Phase 1: Basic Generation (Minimal viable)
- Replace only essential variables (PROJECT_NAME, GENERATION_DATE, TICKET_PREFIX)
- Leave advanced variables as-is for users to fill manually

### Phase 2: Framework-Specific (Future enhancement)
- Detect framework and populate framework-specific variables
- Example: For Python projects, set {{RUN_TESTS}} to "pytest"
- Example: For Node projects, set {{RUN_TESTS}} to "npm test"

### Phase 3: Interactive Prompts (Future enhancement)
- Prompt users for additional details (security contact, CoC contact, etc.)
- Store preferences for reuse

---

## Next Steps

1. Apply integration changes listed above to `proto_gear.py`
2. Test template generation with `--dry-run`
3. Add basic variable substitution
4. Add tests for new templates
5. Update documentation
6. Merge to development

---

**Note**: These templates are production-ready. The integration work is straightforward pattern-following of existing `generate_branching_doc()` function.
