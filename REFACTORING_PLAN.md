# Proto Gear Refactoring Plan - Vision Alignment
**Date:** 2025-11-02
**Goal:** Align codebase with true vision - Template Generator for Agent Collaboration

---

## The Vision: Natural Language Agent Collaboration

**Proto Gear is NOT:**
- ❌ A workflow execution engine (Python orchestrating tasks)
- ❌ A Git automation tool (Python running git commands)
- ❌ A test runner (Python executing pytest)

**Proto Gear IS:**
- ✅ A **template generator** that creates collaboration environments
- ✅ A **pattern documentation system** for agents (human + AI)
- ✅ An **initialization wizard** that detects context and generates guides
- ✅ A **foundation** for natural language workflows

**Key Philosophy:**
> "Create an environment where all agents (human and AI) work via natural language with patterns like workflows, skills, commands, sub-agents, git-worktrees, etc., guided by templates."

---

## Current State vs. Desired State

### Current Codebase (v0.3.0)

| Component | Lines | Purpose | Keep? |
|-----------|-------|---------|-------|
| proto_gear.py | 905 | CLI + wizard + `pg init` + `pg workflow` | ✅ (modified) |
| interactive_wizard.py | 364 | Beautiful CLI for setup | ✅ (keep) |
| agent_framework.py | 583 | Workflow orchestration engine | ❌ REMOVE |
| git_workflow.py | 686 | Git automation code | ❌ REMOVE |
| testing_workflow.py | 570 | Test automation code | ❌ REMOVE |
| **TOTAL** | **3,108** | | |

### Desired Codebase (v0.4.0)

| Component | Lines | Purpose |
|-----------|-------|---------|
| proto_gear.py | ~400 | CLI + wizard + `pg init` only |
| interactive_wizard.py | 364 | Beautiful CLI for setup |
| ui_helper.py | ~100 | Consolidated print/logging (new) |
| **TOTAL** | **~864** | **72% reduction!** |

### Template Files (The Real Product)

| Template | Exists? | Purpose |
|----------|---------|---------|
| AGENTS.template.md | ✅ Yes | Agent hierarchy and responsibilities |
| PROJECT_STATUS.template.md | ✅ Yes | Project state tracking |
| BRANCHING.template.md | ✅ Yes | Git workflow patterns |
| TESTING.template.md | ❌ **CREATE** | Testing patterns and TDD guidance |

---

## What Gets Removed (1,839 lines)

### 1. agent_framework.py (583 lines)

**What it does:**
- WorkflowOrchestrator - executes `pg workflow`
- AdaptiveHybridSystem - manages agent slots
- ProjectStateManager - reads/writes PROJECT_STATUS.md
- TicketGenerator - creates tickets programmatically
- DocumentationConsistencyEngine - checks AGENTS.md hierarchy

**Why remove:**
- Agents don't need Python orchestration
- Templates + natural language communication is sufficient
- Adds complexity without enabling agent collaboration

**What to preserve:**
- Patterns → Document in templates
- Agent slot concept → Explain in AGENTS.template.md
- State management → Explain in PROJECT_STATUS.template.md

### 2. git_workflow.py (686 lines)

**What it does:**
- GitBranchManager - creates branches via Python
- GitWorkflowIntegration - automates git commands
- tdd_development_cycle() - Python-driven TDD workflow
- Branch cleanup, PR templates, Git hooks

**Why remove:**
- Agents can use git directly (humans already do)
- BRANCHING.template.md provides the patterns
- Python wrapper adds no value for agent collaboration

**What to preserve:**
- Branch naming conventions → BRANCHING.template.md (already exists!)
- TDD workflow pattern → TESTING.template.md (create)
- PR template → `.github/pull_request_template.md` (already created!)

### 3. testing_workflow.py (570 lines)

**What it does:**
- TDDWorkflow - Python test orchestration
- TestRunner - executes pytest via Python
- Test result parsing and reporting

**Why remove:**
- Agents can run pytest directly
- TESTING.template.md will provide TDD patterns
- Python wrapper doesn't enable collaboration

**What to preserve:**
- TDD methodology → TESTING.template.md
- Test-first patterns → Documentation
- Coverage targets → Template guidelines

---

## Impact Analysis

### Code Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total lines** | 3,108 | ~864 | -72% |
| **Executable statements** | 1,412 | ~400 | -72% |
| **Print statements** | 246 | ~50 | -80% |
| **Test coverage** | 37% | ~90% | +53% |
| **Core files** | 5 | 3 | -40% |

### Test Impact

**Current tests that will break:**
- `tests/test_agent_framework.py` (15 tests) - DELETE
- `tests/test_git_workflow.py` (30 tests) - DELETE
- Total: 45 tests removed

**Tests that remain:**
- `tests/test_proto_gear.py` (15 tests) - ✅ Keep (modify)
- `tests/test_interactive_wizard.py` (15 tests) - ✅ Keep

**New coverage:**
- 30 tests for ~400 statements = ~90% coverage potential!

---

## Migration Plan - 5 Phases

### Phase 1: Create Missing Template ✅ LOW RISK

**Create TESTING.template.md** with:
- TDD workflow explanation (Red-Green-Refactor)
- Test-first methodology
- Coverage targets and guidelines
- Example test structures
- Integration with CI/CD

**Files to create:**
- `core/TESTING.template.md`

**Risk:** ZERO - only adding documentation

---

### Phase 2: Document Preserved Patterns ✅ LOW RISK

**Update existing templates** with patterns from removed code:

1. **AGENTS.template.md** - Add:
   - Agent slot concept (4 core + 2 flex)
   - Sprint-based agent allocation
   - Role descriptions from AdaptiveHybridSystem

2. **PROJECT_STATUS.template.md** - Add:
   - Ticket structure and status workflow
   - Sprint tracking patterns
   - State management guidelines

3. **BRANCHING.template.md** - Already complete! ✅

**Risk:** ZERO - documentation only

---

### Phase 3: Remove Workflow Modules ⚠️ MEDIUM RISK

**Step 3.1: Remove the modules**

Delete:
- `core/agent_framework.py`
- `core/git_workflow.py`
- `core/testing_workflow.py`
- `tests/test_agent_framework.py`
- `tests/test_git_workflow.py`

**Step 3.2: Update proto_gear.py**

Remove:
- `pg workflow` command (lines ~870-876)
- Import of WorkflowOrchestrator
- Update help text

**Step 3.3: Run tests**

```bash
python -m pytest tests/ -v --cov=core
```

Expected: 30 tests passing (down from 75)

**Risk:** MEDIUM - Breaking changes, but intentional

---

### Phase 4: Create UI Helper Class ✅ LOW RISK

**Create `core/ui_helper.py`** to consolidate 246 print statements:

```python
class UIHelper:
    """Centralized UI/UX for Proto Gear CLI"""

    @staticmethod
    def header(title: str):
        """Print formatted header"""

    @staticmethod
    def success(message: str):
        """Print success message with ✅"""

    @staticmethod
    def error(message: str):
        """Print error message with ❌"""

    # ... etc
```

**Refactor proto_gear.py and interactive_wizard.py** to use UIHelper

**Benefits:**
- Reduce from 246 → ~50 print statements
- Same visual output
- Easier to test
- Consistent formatting

**Risk:** LOW - gradual refactor, preserves UI

---

### Phase 5: Update Documentation 📚 LOW RISK

**Update:**
- README.md - Remove `pg workflow` references
- CLAUDE.md - Update development commands
- docs/getting-started.md - Simplify workflow
- docs/READINESS_ASSESSMENT.md - Update metrics

**Add:**
- docs/TEMPLATE_GUIDE.md - Explain how templates enable collaboration
- docs/AGENT_PATTERNS.md - Document collaboration patterns

**Risk:** ZERO - documentation only

---

## Safety Measures

### Before Each Phase:

1. ✅ Create git branch: `refactor/PROTO-015-remove-workflow-modules`
2. ✅ Commit current state
3. ✅ Run full test suite
4. ✅ Document expected changes

### After Each Phase:

1. ✅ Run tests: `pytest tests/ -v --cov=core`
2. ✅ Test `pg init` manually
3. ✅ Verify templates are generated correctly
4. ✅ Commit with clear message
5. ✅ Get user approval before next phase

---

## Rollback Plan

Each phase is a separate commit. If issues arise:

```bash
# View commits
git log --oneline

# Rollback to before Phase N
git reset --hard <commit-hash>

# Or revert specific commit
git revert <commit-hash>
```

---

## Expected Outcome

### v0.4.0: Template-Focused Proto Gear

**What users get:**
```bash
pg init
```

**Output:**
1. ✅ AGENTS.md - Agent collaboration guide
2. ✅ PROJECT_STATUS.md - Project state tracking
3. ✅ BRANCHING.md - Git workflow patterns
4. ✅ TESTING.md - TDD and testing guidance
5. ✅ .github/pull_request_template.md - PR template

**What agents (human + AI) do:**
- Read the templates
- Follow the patterns
- Communicate via natural language
- Use native tools (git, pytest, etc.)
- Update PROJECT_STATUS.md manually/via AI

**What Proto Gear does:**
- Beautiful interactive wizard
- Project detection (Node.js, Python, etc.)
- Template generation
- **That's it!**

---

## Timeline

**Recommended execution:**

| Phase | Time | Risk | User Approval? |
|-------|------|------|----------------|
| Phase 1 | 30 min | Low | Optional |
| Phase 2 | 1 hour | Low | Optional |
| Phase 3 | 2 hours | Medium | **Required** |
| Phase 4 | 3 hours | Low | Optional |
| Phase 5 | 1 hour | Low | Optional |

**Total:** ~7-8 hours of work

**Suggested approach:**
1. Execute Phases 1-2 (documentation) first
2. Get user approval + testing
3. Execute Phase 3 (big removal) with supervision
4. Execute Phases 4-5 (polish)

---

## Questions for User

Before proceeding, please confirm:

1. ✅ Remove `pg workflow` command entirely?
2. ✅ Delete agent_framework.py, git_workflow.py, testing_workflow.py?
3. ✅ Focus Proto Gear as template generator only?
4. ✅ Agents use native tools (git, pytest) guided by templates?
5. ❓ Should we keep any workflow code for future extensibility?
6. ❓ Any templates beyond AGENTS/STATUS/BRANCHING/TESTING?

**Ready to proceed with Phase 1?** (Create TESTING.template.md)
