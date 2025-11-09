# Wizard-Template Sync Issue - Root Cause Analysis

**Date**: 2025-11-09
**Issue**: Interactive wizard keeps missing new features added to CLI
**Impact**: Users using interactive mode don't see v0.5.0+ templates

## The Problem

Proto Gear has **TWO independent code paths** for initialization:

1. **CLI Direct Path** (`proto_gear.py`):
   - Handles `--all`, `--with-branching`, `--with-capabilities` flags
   - Up-to-date with v0.5.2 features
   - Generates all 8 templates when using `--all`

2. **Interactive Wizard Path** (`interactive_wizard.py`):
   - Separate module with hardcoded PRESETS
   - **Frozen at v0.4.1 feature set**
   - Only knows about 3 templates: AGENTS, PROJECT_STATUS, TESTING (partial), BRANCHING
   - Missing 4 v0.5.0 templates: CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT
   - No awareness of `--all` flag

## Why This Keeps Happening

### Architectural Issue
```
proto_gear.py (main CLI)
├─ Command-line args (--all, --with-branching, etc.)
├─ Calls: run_simple_protogear_init()
└─ Direct template generation

interactive_wizard.py (wizard module)
├─ PRESETS dictionary (hardcoded config from v0.4.1)
├─ Calls: run_simple_protogear_init() with wizard config
└─ BUT: wizard config doesn't include new options!
```

**The disconnect:**
- When we add a new CLI flag (like `--all`), we update `proto_gear.py`
- But we **forget to update** `interactive_wizard.py` PRESETS
- Wizard users never see the new features

## Historical Pattern

### v0.4.0
- Added capabilities system
- ✅ Updated wizard presets
- ✅ Works

### v0.5.0 (2025-11-08)
- Added 4 new templates: CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT
- ❌ **FORGOT to update wizard**
- ❌ Wizard still shows v0.4.1 presets

### v0.5.2 (2025-11-09)
- Added `--all` flag for complete template generation
- ❌ **FORGOT to update wizard**
- ❌ Wizard has no way to select `--all`

## What's Currently Broken

### Preset "Full Setup" (line 50-67)
```python
'full': {
    'name': 'Full Setup',
    'description': 'Everything enabled - All templates and capabilities',
    'details': [
        'AGENTS.md + PROJECT_STATUS.md',
        'BRANCHING.md - Always included',
        'TESTING.md - TDD patterns',         # ← Partial implementation
        '.proto-gear/ - Full capability system (8 files)'
    ],
    'config': {
        'core': ['AGENTS', 'PROJECT_STATUS', 'TESTING'],
        'branching': True,
        'testing': True,
        'capabilities': True,
    }
}
```

**Issues:**
1. Says "Everything enabled - All templates" but only has 4 templates
2. Missing CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT
3. No `with_all` flag passed to generation function

### Custom Path (lines 1003-1042)
```python
# Stage 1: Core Templates Selection
core_templates = wizard.ask_core_templates_selection()
# ← Only asks about TESTING.md, not the 4 new templates!
```

**Issues:**
1. Only lets user select TESTING.md as additional template
2. No checkboxes for CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT
3. No option to "select all templates"

## The Fix

### Immediate (v0.5.3)

1. **Update PRESETS dictionary** (lines 31-99):
   - Add `with_all` option to presets
   - Update "Full Setup" to actually include ALL templates
   - Add descriptions for new templates

2. **Update `ask_core_templates_selection()`** (lines 447-499):
   - Add checkboxes for all 4 new templates
   - Add "Select All" option

3. **Update `_apply_preset_config()`** (lines 1045-1072):
   - Pass `with_all=True` for "Full Setup" preset
   - Handle new template selections

### Long-term Solution (v0.6.0)

**Make wizard auto-discover templates** instead of hardcoding:

```python
def discover_available_templates():
    """Auto-discover all templates in package"""
    template_dir = Path(__file__).parent
    templates = {}

    for template_file in template_dir.glob("*.template.md"):
        name = template_file.stem.replace(".template", "")
        # Read metadata from template file (YAML frontmatter)
        metadata = extract_template_metadata(template_file)
        templates[name] = metadata

    return templates

# Then in wizard:
def ask_template_selection(self):
    """Dynamically generate template choices from discovered templates"""
    templates = discover_available_templates()

    choices = []
    for name, metadata in templates.items():
        if name in ['AGENTS', 'PROJECT_STATUS']:
            continue  # Always included

        choices.append(questionary.Choice(
            f"{metadata['name']} - {metadata['description']}",
            value=name,
            checked=metadata.get('default', False)
        ))

    selected = questionary.checkbox(
        "Select templates to generate:",
        choices=choices
    ).ask()

    return selected
```

**Benefits:**
- Adding a new template = zero code changes needed
- Wizard automatically shows all available templates
- No more sync issues between CLI and wizard

## Prevention Strategy

### For Contributors (Human & AI)

**WHENEVER you add a new template or CLI flag, you MUST:**

1. ✅ Add the template file (e.g., `NEWFILE.template.md`)
2. ✅ Update CLI in `proto_gear.py` (if needed)
3. ✅ **UPDATE WIZARD** in `interactive_wizard.py`:
   - Add to PRESETS dictionary
   - Add to `ask_core_templates_selection()` checkboxes
   - Add to `_apply_preset_config()` handling
4. ✅ Test both CLI and interactive wizard
5. ✅ Update CHANGELOG noting both paths work

### Checklist Template

```markdown
## New Template Checklist

- [ ] Created `TEMPLATE_NAME.template.md` in `core/proto_gear_pkg/`
- [ ] CLI: Added flag to `proto_gear.py` (if applicable)
- [ ] CLI: Updated `run_simple_protogear_init()` to handle new template
- [ ] **WIZARD: Updated PRESETS in `interactive_wizard.py`**
- [ ] **WIZARD: Added checkbox in `ask_core_templates_selection()`**
- [ ] **WIZARD: Updated `_apply_preset_config()` to pass new option**
- [ ] Tested: `pg init --dry-run` (CLI path)
- [ ] Tested: `pg init` with interactive wizard (wizard path)
- [ ] Both paths generate the same files
- [ ] Updated CHANGELOG.md
- [ ] Updated documentation
```

## Testing Strategy

After any template addition, run BOTH tests:

```bash
# Test 1: CLI direct path
pg init --all --dry-run
# Should list ALL templates including new ones

# Test 2: Interactive wizard path
pg init
# Select "Full Setup" preset
# Should offer ALL templates including new ones

# Verify both generate the same files
```

## Summary

**Root Cause:** Two independent code paths (CLI and wizard) that must be manually kept in sync

**Why it keeps happening:** Forgetting to update wizard when adding CLI features

**Immediate fix:** Update wizard presets and selection functions to match v0.5.2 CLI

**Long-term fix:** Template auto-discovery system (PROTO-023, planned for v0.6.0)

**Prevention:** Always update BOTH paths when adding features, use checklist

---

*This document should be reviewed before any template or CLI feature addition*
