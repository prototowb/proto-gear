# Test Plan - Phase 1: Fix Failing Tests & Test Critical Features

**Goal**: Get to 100% passing tests + test auto-discovery feature
**Timeline**: Current session
**Target Coverage**: 40%

---

## Task 1: Fix Import Errors (30 minutes)

### Files to Fix
- `tests/test_proto_gear.py`
- `tests/test_capabilities.py`
- `tests/test_ui_helper.py`

### Changes Needed
Already partially fixed, need to verify all imports use `proto_gear_pkg.` prefix

### Validation
```bash
pytest tests/ -v --tb=short
# Should show 0 import errors
```

---

## Task 2: Fix Capability Path Issues (15 minutes)

### Tests Affected
- `test_capability_templates_exist`
- `test_example_command_exists`
- `test_example_skill_exists`
- `test_example_workflow_exists`

### Root Cause
Tests looking for `capabilities/` in wrong location

### Fix
Update path to: `core/proto_gear_pkg/capabilities/`

---

## Task 3: Test Auto-Discovery Feature (1-2 hours)

### New Test File: `tests/test_template_discovery.py`

```python
"""
Tests for template auto-discovery system (v0.6.0 feature)
"""

import pytest
from pathlib import Path
from proto_gear_pkg.proto_gear import discover_available_templates

class TestTemplateDiscovery:
    def test_discovers_all_templates(self, tmp_path):
        """Test that all .template.md files are discovered"""
        # Should discover AGENTS, PROJECT_STATUS, BRANCHING, etc.
        pass

    def test_template_name_extraction(self):
        """Test correct extraction of template names"""
        # TESTING.template.md → TESTING
        pass

    def test_empty_directory(self, tmp_path):
        """Test behavior with no templates"""
        pass

    def test_malformed_filenames(self, tmp_path):
        """Test handling of non-template files"""
        pass
```

### Coverage Target
- Lines 478-494 in `proto_gear.py`
- **+5% overall coverage**

---

## Task 4: Test Template Generation (1-2 hours)

### New Test File: `tests/test_template_generation.py`

```python
"""
Tests for template generation with placeholder replacement
"""

import pytest
from pathlib import Path
from proto_gear_pkg.proto_gear import generate_project_template

class TestTemplateGeneration:
    def test_generates_template_file(self, tmp_path):
        """Test basic template generation"""
        pass

    def test_placeholder_replacement(self, tmp_path):
        """Test that {{VERSION}}, {{PROJECT_NAME}}, etc. are replaced"""
        pass

    def test_all_template_types(self, tmp_path):
        """Test generation of all 8 template types"""
        pass

    def test_missing_template_error(self, tmp_path):
        """Test error handling for missing template file"""
        pass

    def test_version_substitution(self, tmp_path):
        """Test that VERSION is correctly substituted (bug fix verification)"""
        # This specifically tests the v0.6.3 fix!
        pass
```

### Coverage Target
- Lines 509-533 in `proto_gear.py`
- **+3% overall coverage**

---

## Task 5: Enhance Capability Tests (30 minutes)

### File: `tests/test_capabilities.py`

### Add Tests
- Test granular selection (all/category/individual)
- Test capability metadata
- Test dry-run mode for capabilities

### Coverage Target
- Lines 583-690 in `proto_gear.py`
- **+2% overall coverage**

---

## Expected Results

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Passing Tests | 71 | 100+ | +29+ |
| Failing Tests | 30 | 0 | -30 |
| Coverage | 32% | 40% | +8% |

---

## Success Criteria

- ✅ Zero test failures
- ✅ Auto-discovery feature 100% tested
- ✅ Template generation 100% tested
- ✅ Version substitution verified (v0.6.3 fix)
- ✅ 40%+ coverage achieved

---

*Created: 2025-11-12*
*Phase: 1 of 5*
