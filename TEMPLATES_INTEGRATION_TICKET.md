# Templates CLI Integration Ticket

**Ticket**: POST-V050-001
**Priority**: Medium
**Status**: Ready for Implementation
**Estimated Time**: 30-45 minutes

## Overview

Complete CLI integration for the 4 new templates added in v0.5.0:
- CONTRIBUTING.template.md
- SECURITY.template.md
- ARCHITECTURE.template.md
- CODE_OF_CONDUCT.template.md

## Resources

All integration code and documentation is ready:
- **Integration Script**: `integrate_templates.py` (complete, tested)
- **Manual Guide**: `INTEGRATION_NOTES.md` (step-by-step instructions)
- **Development Summary**: `DEVELOPMENT_SUMMARY.md` (context and decisions)

## Automated Approach (Recommended)

When Python environment is available:

```bash
cd /path/to/proto-gear
python integrate_templates.py
```

This script automatically:
1. Adds 4 CLI flags to `proto_gear.py`
2. Adds 4 template generation functions
3. Updates function signatures with new parameters
4. Updates argument passing in wizard and CLI paths

## Manual Approach

Follow `INTEGRATION_NOTES.md` sections 1-6:

### 1. Add CLI Flags (Lines 1040-1059)
Add after `--with-capabilities` and before `--no-interactive`

### 2. Add Generation Functions (After line 456)
Copy 4 functions from `integrate_templates.py`:
- `generate_contributing_doc()`
- `generate_security_doc()`
- `generate_architecture_doc()`
- `generate_code_of_conduct_doc()`

### 3. Update run_simple_protogear_init() Signature
Add 4 new boolean parameters

### 4. Add Template Generation Calls
Add calls when corresponding flags are set

### 5. Update Argument Passing
Update both wizard and CLI code paths

### 6. Test Integration
```bash
pg init --dry-run --with-contributing
pg init --dry-run --with-security
pg init --dry-run --with-architecture
pg init --dry-run --with-coc
```

## Testing Checklist

- [ ] CLI flags added without syntax errors
- [ ] Generation functions work correctly
- [ ] `pg init --dry-run` executes without errors
- [ ] Individual flags generate correct templates
- [ ] All flags together work
- [ ] Wizard path includes new options
- [ ] Template placeholders are replaced correctly

## Expected Outcome

After integration, users can run:

```bash
# Generate all new templates
pg init --with-contributing --with-security --with-architecture --with-coc

# Or selectively
pg init --with-contributing  # Just contribution guidelines
pg init --with-security      # Just security policy
```

## Notes

- Templates are production-ready (already in v0.5.0)
- CLI integration is the only pending item
- Can be completed anytime without blocking users
- Users can manually copy templates until integration is complete

## Success Criteria

✅ CLI flags functional
✅ Templates generate correctly
✅ No regressions in existing functionality
✅ Tests pass
✅ Documentation updated

---

**Created**: 2025-11-08
**Updated**: 2025-11-08
**Related**: v0.5.0 Release, Templates Workstream
