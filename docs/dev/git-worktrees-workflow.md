# Git Worktrees Workflow for Parallel Development

**Document Version**: 1.0.0
**Last Updated**: 2025-11-08
**Target Release**: v0.5.0
**Status**: Active Development Guide

---

## Executive Summary

This document defines the optimized asynchronous Git worktrees workflow for Proto Gear v0.5.0 parallel development. Based on modern best practices (2024-2025) and lessons learned from v0.4.0 development, this workflow enables simultaneous work on three independent workstreams: Core Templates, Skills, and Workflows.

### Key Recommendations

1. **Use Dedicated Worktrees Directory**: Keep all worktrees in `G:\Projects\proto-gear-worktrees\` (sibling to main repo)
2. **One Worktree Per Workstream**: Create exactly 3 worktrees for the 3 v0.5.0 workstreams
3. **Branch Naming Convention**: `feature/v0.5.0-{workstream}-{component}`
4. **Sequential Integration**: Merge workstreams to `development` one at a time, not all at once
5. **Test Before Merge**: Each workstream must pass full test suite independently
6. **Enable Git Rerere**: Reuse recorded conflict resolutions for efficiency
7. **Regular Commits**: Commit frequently within each worktree to simplify conflict resolution
8. **Clean Up Promptly**: Remove worktrees immediately after successful merge

### When to Use Worktrees vs Sequential Development

**Use Worktrees When:**
- Features are truly independent (minimal file overlap)
- Need to work on multiple features simultaneously
- Features have different timelines or blockers
- Want to test different approaches in parallel

**Use Sequential Development When:**
- Features heavily overlap in files they modify
- Team is small (1-2 developers)
- Features are tightly coupled
- High risk of complex merge conflicts

For v0.5.0, worktrees are RECOMMENDED because:
- Three workstreams are largely independent
- Different file sets (templates, skills, workflows)
- Proven success in v0.4.0 development
- Parallel work accelerates development

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Setup Instructions](#setup-instructions)
3. [Working in Parallel](#working-in-parallel)
4. [Testing Strategy](#testing-strategy)
5. [Integration Strategy](#integration-strategy)
6. [Cleanup Procedures](#cleanup-procedures)
7. [Troubleshooting Guide](#troubleshooting-guide)
8. [Best Practices](#best-practices)
9. [Risk Assessment](#risk-assessment)

---

## Architecture Overview

### Directory Structure

```
G:\Projects\
├── proto-gear\                          # Main repository (on development branch)
│   ├── .git\                            # Git metadata (shared by all worktrees)
│   ├── core\
│   ├── docs\
│   ├── tests\
│   └── ...
│
└── proto-gear-worktrees\                # Worktrees directory
    ├── v0.5.0-templates\                # Workstream 1: Core Templates
    │   ├── core\
    │   ├── docs\
    │   ├── tests\
    │   └── ... (complete working tree)
    │
    ├── v0.5.0-skills\                   # Workstream 2: Skills
    │   ├── core\
    │   ├── docs\
    │   ├── tests\
    │   └── ... (complete working tree)
    │
    └── v0.5.0-workflows\                # Workstream 3: Workflows
        ├── core\
        ├── docs\
        ├── tests\
        └── ... (complete working tree)
```

### Branch Strategy

Each workstream gets its own feature branch:

```
development (base)
├── feature/v0.5.0-templates-core     # Workstream 1 branch
├── feature/v0.5.0-skills-system      # Workstream 2 branch
└── feature/v0.5.0-workflows-engine   # Workstream 3 branch
```

**Branch Naming Pattern**: `feature/v0.5.0-{workstream}-{description}`

### Workstream Definitions

#### Workstream 1: Core Templates (4-5 templates)
**Branch**: `feature/v0.5.0-templates-core`
**Worktree**: `G:\Projects\proto-gear-worktrees\v0.5.0-templates`
**Scope**:
- CONTRIBUTING.md template
- SECURITY.md template
- ARCHITECTURE.md template
- CODE_OF_CONDUCT.md template
- API.md template (optional)
- DEPLOYMENT.md template (optional)

**Primary Files**:
- `core/*.template.md` (new templates)
- `core/proto_gear.py` (template loading logic)
- `docs/user/template-guide.md` (documentation)
- `tests/test_templates.py` (tests)

#### Workstream 2: Skills System (3-4 skills)
**Branch**: `feature/v0.5.0-skills-system`
**Worktree**: `G:\Projects\proto-gear-worktrees\v0.5.0-skills`
**Scope**:
- debugging skill
- code-review skill
- refactoring skill
- performance skill (optional)

**Primary Files**:
- `core/skills/` (new directory)
- `core/skills/*.skill.md` (skill definitions)
- `core/proto_gear.py` (skill loading/execution)
- `docs/user/skills-guide.md` (documentation)
- `tests/test_skills.py` (tests)

#### Workstream 3: Workflows Engine (2-3 workflows)
**Branch**: `feature/v0.5.0-workflows-engine`
**Worktree**: `G:\Projects\proto-gear-worktrees\v0.5.0-workflows`
**Scope**:
- bug-fix workflow
- hotfix workflow
- release workflow

**Primary Files**:
- `core/workflows/` (new directory)
- `core/workflows/*.workflow.md` (workflow definitions)
- `core/proto_gear.py` (workflow execution)
- `docs/user/workflows-guide.md` (documentation)
- `tests/test_workflows.py` (tests)

### Independence Analysis

| File/Directory | Templates | Skills | Workflows | Conflict Risk |
|----------------|-----------|--------|-----------|---------------|
| `core/proto_gear.py` | Moderate | Moderate | Moderate | **HIGH** |
| `core/*.template.md` | Primary | None | None | Low |
| `core/skills/` | None | Primary | None | Low |
| `core/workflows/` | None | None | Primary | Low |
| `docs/user/` | Moderate | Moderate | Moderate | Medium |
| `tests/` | Moderate | Moderate | Moderate | Medium |
| `pyproject.toml` | Minor | Minor | Minor | Medium |
| `README.md` | Minor | Minor | Minor | Medium |

**Conflict Hot Spots**:
1. **`core/proto_gear.py`** - All three workstreams will modify this file
2. **`docs/user/getting-started.md`** - May be updated by all workstreams
3. **`pyproject.toml`** - Version bumps or dependency changes
4. **`README.md`** - Feature announcements

**Mitigation Strategy**:
- Merge workstreams sequentially (Templates → Skills → Workflows)
- Test integration after each merge
- Use clear section comments in `proto_gear.py` for each workstream
- Coordinate documentation updates to avoid overlap

---

## Setup Instructions

### Prerequisites

1. **Current State Verification**
   ```bash
   cd G:\Projects\proto-gear
   git status                    # Should be on development branch, clean
   git pull origin development   # Ensure latest code
   git worktree list            # Check for existing worktrees
   ```

2. **Enable Git Rerere** (Reuse Recorded Resolution)
   ```bash
   git config rerere.enabled true
   git config rerere.autoupdate true
   ```

   This will automatically remember conflict resolutions and reuse them.

3. **Create Worktrees Directory** (if not exists)
   ```bash
   mkdir G:\Projects\proto-gear-worktrees
   ```

### Step 1: Create Workstream 1 (Templates)

```bash
cd G:\Projects\proto-gear

# Create worktree with new branch from development
git worktree add -b feature/v0.5.0-templates-core ../proto-gear-worktrees/v0.5.0-templates development

# Verify creation
git worktree list
```

**Expected Output**:
```
G:/Projects/proto-gear                                d0d8184 [development]
G:/Projects/proto-gear-worktrees/v0.5.0-templates    d0d8184 [feature/v0.5.0-templates-core]
```

### Step 2: Create Workstream 2 (Skills)

```bash
cd G:\Projects\proto-gear

# Create worktree with new branch from development
git worktree add -b feature/v0.5.0-skills-system ../proto-gear-worktrees/v0.5.0-skills development

# Verify creation
git worktree list
```

### Step 3: Create Workstream 3 (Workflows)

```bash
cd G:\Projects\proto-gear

# Create worktree with new branch from development
git worktree add -b feature/v0.5.0-workflows-engine ../proto-gear-worktrees/v0.5.0-workflows development

# Verify creation
git worktree list
```

### Step 4: Verify Setup

```bash
# List all worktrees
git worktree list

# List all branches
git branch -a

# Verify each worktree is on correct branch
cd ../proto-gear-worktrees/v0.5.0-templates && git branch
cd ../v0.5.0-skills && git branch
cd ../v0.5.0-workflows && git branch
```

**Expected State**:
- Main repo on `development`
- 3 worktrees on their respective feature branches
- All starting from same commit (development HEAD)

### Step 5: Initial Commit in Each Worktree

To establish branch identity, make an initial commit in each:

```bash
# Workstream 1: Templates
cd G:\Projects\proto-gear-worktrees\v0.5.0-templates
echo "# Core Templates Development" > WORKSTREAM.md
git add WORKSTREAM.md
git commit -m "feat(templates): initialize core templates workstream

Starting development of CONTRIBUTING, SECURITY, ARCHITECTURE,
CODE_OF_CONDUCT, API, and DEPLOYMENT templates for v0.5.0.

Refs: v0.5.0 milestone"

# Workstream 2: Skills
cd G:\Projects\proto-gear-worktrees\v0.5.0-skills
echo "# Skills System Development" > WORKSTREAM.md
git add WORKSTREAM.md
git commit -m "feat(skills): initialize skills system workstream

Starting development of debugging, code-review, refactoring,
and performance skills for v0.5.0.

Refs: v0.5.0 milestone"

# Workstream 3: Workflows
cd G:\Projects\proto-gear-worktrees\v0.5.0-workflows
echo "# Workflows Engine Development" > WORKSTREAM.md
git add WORKSTREAM.md
git commit -m "feat(workflows): initialize workflows engine workstream

Starting development of bug-fix, hotfix, and release workflows
for v0.5.0.

Refs: v0.5.0 milestone"
```

### Setup Complete

You now have 3 independent worktrees ready for parallel development!

---

## Working in Parallel

### General Workflow for Each Workstream

1. **Switch to worktree directory**
   ```bash
   cd G:\Projects\proto-gear-worktrees\v0.5.0-{templates|skills|workflows}
   ```

2. **Work normally** - Edit files, add features, write tests

3. **Commit frequently**
   ```bash
   git add .
   git commit -m "feat(scope): description"
   ```

4. **Pull latest from development periodically**
   ```bash
   git fetch origin development
   git merge origin/development
   ```

5. **Run tests locally**
   ```bash
   python -m pytest
   pg init --dry-run
   ```

### Best Practices While Working

#### DO:
- Commit early and often (every logical change)
- Write descriptive commit messages following Conventional Commits
- Test your changes locally before pushing
- Pull from `development` daily to catch integration issues early
- Use clear section markers in shared files (especially `proto_gear.py`)
- Document new features in your workstream's docs
- Add tests for new functionality

#### DON'T:
- Don't modify files outside your workstream scope
- Don't merge between workstream branches directly
- Don't commit broken code (test first!)
- Don't let your branch drift too far from development
- Don't commit generated files or temp files
- Don't push directly to `development` or `main`

### Handling Shared File Conflicts

If multiple workstreams need to modify `core/proto_gear.py`:

#### Strategy 1: Section Markers (Recommended)

Add clear section markers:

```python
# proto_gear.py

# ============================================================
# TEMPLATES SYSTEM (Workstream 1)
# ============================================================
def load_templates():
    # Templates workstream code here
    pass

# ============================================================
# SKILLS SYSTEM (Workstream 2)
# ============================================================
def load_skills():
    # Skills workstream code here
    pass

# ============================================================
# WORKFLOWS ENGINE (Workstream 3)
# ============================================================
def execute_workflow():
    # Workflows workstream code here
    pass
```

This makes merge conflicts obvious and easier to resolve.

#### Strategy 2: Coordination via Comments

Before modifying shared files:

1. Check other worktrees to see if they're modifying same file
2. Coordinate via comments or PROJECT_STATUS.md
3. Agree on merge order (Templates → Skills → Workflows)
4. First workstream establishes structure, others adapt

### Pushing to Remote (Optional)

If working with a team or want backup:

```bash
# From each worktree
git push origin feature/v0.5.0-templates-core
git push origin feature/v0.5.0-skills-system
git push origin feature/v0.5.0-workflows-engine
```

### Viewing Changes Across Worktrees

```bash
# From main repo
git log --oneline --graph --all --decorate

# Compare branches
git diff development..feature/v0.5.0-templates-core
git diff development..feature/v0.5.0-skills-system
git diff development..feature/v0.5.0-workflows-engine

# See what files changed
git diff --name-only development..feature/v0.5.0-templates-core
```

---

## Testing Strategy

### Test Before Integration

Each workstream MUST pass full test suite before merging to `development`.

### Testing Checklist Per Workstream

#### 1. Unit Tests
```bash
cd G:\Projects\proto-gear-worktrees\v0.5.0-{workstream}
python -m pytest tests/ -v
```

**Pass Criteria**: All tests pass, no failures or errors

#### 2. Coverage Tests
```bash
python -m pytest --cov=core --cov-report=term-missing
```

**Pass Criteria**: Coverage >= 70% (project target)

#### 3. Linting
```bash
python -m flake8 core/
```

**Pass Criteria**: No linting errors

#### 4. Integration Tests
```bash
# Test CLI commands
pg init --dry-run
pg help

# Test with actual file generation
cd /tmp/test-project
pg init --with-branching --ticket-prefix TEST

# Verify generated files
cat AGENTS.md
cat PROJECT_STATUS.md
cat BRANCHING.md
```

**Pass Criteria**: Generated files are correct and complete

#### 5. Cross-Workstream Tests

After merging each workstream, test interactions:

```bash
# After merging Templates
pg init --dry-run  # Should show new templates

# After merging Skills
pg skills list     # Should show new skills
pg skills run debugging

# After merging Workflows
pg workflows list  # Should show new workflows
pg workflows run bug-fix
```

### Automated Testing Script

Create `dev/scripts/test-worktree.sh`:

```bash
#!/bin/bash
# Test a specific worktree before merge

WORKTREE_PATH=$1

if [ -z "$WORKTREE_PATH" ]; then
    echo "Usage: ./test-worktree.sh <worktree-path>"
    exit 1
fi

echo "Testing worktree: $WORKTREE_PATH"
cd "$WORKTREE_PATH"

echo "1. Running unit tests..."
python -m pytest tests/ -v || exit 1

echo "2. Checking coverage..."
python -m pytest --cov=core --cov-report=term-missing || exit 1

echo "3. Linting code..."
python -m flake8 core/ || exit 1

echo "4. Testing CLI..."
pg init --dry-run || exit 1

echo "All tests passed! ✓"
```

Usage:
```bash
bash dev/scripts/test-worktree.sh G:\Projects\proto-gear-worktrees\v0.5.0-templates
```

---

## Integration Strategy

### Overview

Merge workstreams to `development` **sequentially**, not simultaneously.

**Recommended Order**:
1. Templates (foundation for others)
2. Skills (builds on templates)
3. Workflows (uses both templates and skills)

### Pre-Integration Checklist

Before merging any workstream:

- [ ] All tests pass in worktree
- [ ] Coverage >= 70%
- [ ] No linting errors
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (in worktree)
- [ ] Code reviewed (if team workflow)
- [ ] Pulled latest from `development`
- [ ] Resolved any merge conflicts
- [ ] Tested integration with existing features

### Integration Process

#### Step 1: Merge Workstream 1 (Templates)

```bash
# Switch to main repo
cd G:\Projects\proto-gear

# Ensure on development branch
git checkout development
git pull origin development

# Merge templates workstream
git merge feature/v0.5.0-templates-core --no-ff

# If conflicts occur, resolve them:
git status                    # See conflicted files
# Edit files to resolve conflicts
git add <resolved-files>
git merge --continue

# Test after merge
python -m pytest
pg init --dry-run

# If tests pass, push to remote
git push origin development
```

**Verify**: `development` now has all template features

#### Step 2: Merge Workstream 2 (Skills)

```bash
cd G:\Projects\proto-gear

# Ensure on development (with Templates already merged)
git checkout development
git pull origin development

# Merge skills workstream
git merge feature/v0.5.0-skills-system --no-ff

# Resolve conflicts if any
git status
# Edit conflicted files
git add <resolved-files>
git merge --continue

# Test after merge
python -m pytest
pg init --dry-run
pg skills list    # New command from this workstream

# If tests pass, push
git push origin development
```

**Verify**: `development` now has Templates + Skills

#### Step 3: Merge Workstream 3 (Workflows)

```bash
cd G:\Projects\proto-gear

# Ensure on development (with Templates + Skills)
git checkout development
git pull origin development

# Merge workflows workstream
git merge feature/v0.5.0-workflows-engine --no-ff

# Resolve conflicts if any
git status
# Edit conflicted files
git add <resolved-files>
git merge --continue

# Test after merge
python -m pytest
pg init --dry-run
pg skills list
pg workflows list    # New command from this workstream

# If tests pass, push
git push origin development
```

**Verify**: `development` now has Templates + Skills + Workflows

### Step 4: Final Integration Testing

```bash
cd G:\Projects\proto-gear

# Full test suite
python -m pytest --cov=core --cov-report=term-missing

# Integration test in fresh project
cd /tmp/test-v0.5.0
pg init --with-branching --ticket-prefix TEST

# Verify all features work
cat AGENTS.md              # Should include new templates
cat CONTRIBUTING.md        # New template
cat SECURITY.md            # New template
cat ARCHITECTURE.md        # New template

pg skills list             # Should show all 4 skills
pg workflows list          # Should show all 3 workflows
```

### Step 5: Tag Release

```bash
cd G:\Projects\proto-gear
git checkout development

# Create release tag
git tag -a v0.5.0 -m "Release v0.5.0: Core Templates, Skills, and Workflows"

# Push tag
git push origin v0.5.0

# Merge to main
git checkout main
git merge development --no-ff
git push origin main
```

### Conflict Resolution Guidelines

When conflicts occur during merge:

1. **Understand the conflict**
   ```bash
   git status              # See conflicted files
   git diff --name-only --diff-filter=U  # List conflict files
   ```

2. **Examine conflict markers**
   ```
   <<<<<<< HEAD (development)
   existing code
   =======
   workstream code
   >>>>>>> feature/v0.5.0-templates-core
   ```

3. **Resolve strategically**
   - For new files: Usually keep workstream version
   - For modified files: Integrate both changes
   - For `proto_gear.py`: Use section markers to keep both
   - For docs: Merge content from both branches

4. **Test resolution**
   ```bash
   python -m pytest
   pg init --dry-run
   ```

5. **Complete merge**
   ```bash
   git add <resolved-files>
   git merge --continue
   ```

### Git Rerere (Reuse Recorded Resolution)

If you enabled `rerere` during setup, Git will remember conflict resolutions:

```bash
# Check rerere status
git config rerere.enabled   # Should be true

# View recorded resolutions
git rerere diff

# If same conflict happens again, Git auto-resolves it
```

This is especially useful when:
- Merging multiple workstreams with similar conflicts
- Rebasing branches
- Cherry-picking commits

---

## Cleanup Procedures

### When to Clean Up

Clean up worktrees immediately after successful integration:
- Tests pass on `development`
- Changes pushed to remote
- No pending work in worktree

### Step 1: Verify Merge Success

```bash
cd G:\Projects\proto-gear
git checkout development
git log --oneline -5    # Verify merge commit exists
```

### Step 2: Remove Worktree

```bash
# Remove Templates worktree (after successful merge)
git worktree remove ../proto-gear-worktrees/v0.5.0-templates

# Remove Skills worktree (after successful merge)
git worktree remove ../proto-gear-worktrees/v0.5.0-skills

# Remove Workflows worktree (after successful merge)
git worktree remove ../proto-gear-worktrees/v0.5.0-workflows
```

### Step 3: Delete Feature Branches (Optional)

After merging and verifying:

```bash
# Delete local branches
git branch -d feature/v0.5.0-templates-core
git branch -d feature/v0.5.0-skills-system
git branch -d feature/v0.5.0-workflows-engine

# Delete remote branches (if pushed)
git push origin --delete feature/v0.5.0-templates-core
git push origin --delete feature/v0.5.0-skills-system
git push origin --delete feature/v0.5.0-workflows-engine
```

### Step 4: Clean Up Worktree Directory

```bash
# Verify all worktrees removed
git worktree list

# Remove empty directory
rmdir G:\Projects\proto-gear-worktrees
```

### Force Removal (If Worktree Deleted Manually)

If you accidentally deleted worktree directory without using `git worktree remove`:

```bash
# Git will show error, force prune it
git worktree prune

# Verify cleanup
git worktree list
```

### Cleanup Checklist

After v0.5.0 integration:

- [ ] All workstreams merged to `development`
- [ ] All tests pass on `development`
- [ ] Changes pushed to remote
- [ ] All worktrees removed
- [ ] Feature branches deleted (local and remote)
- [ ] Worktrees directory removed
- [ ] `git worktree list` shows only main repo
- [ ] Release tagged (v0.5.0)
- [ ] `development` merged to `main`

---

## Troubleshooting Guide

### Problem: "Cannot create worktree: branch already exists"

**Cause**: Branch name already used

**Solution**:
```bash
# Check existing branches
git branch -a

# Either use different name
git worktree add -b feature/v0.5.0-templates-core-v2 ../proto-gear-worktrees/v0.5.0-templates

# Or delete old branch first
git branch -D feature/v0.5.0-templates-core
```

### Problem: "Worktree path already exists"

**Cause**: Directory already exists at target path

**Solution**:
```bash
# Check what's there
ls ../proto-gear-worktrees/v0.5.0-templates

# Remove it if safe
rm -rf ../proto-gear-worktrees/v0.5.0-templates

# Then create worktree
git worktree add -b feature/v0.5.0-templates-core ../proto-gear-worktrees/v0.5.0-templates
```

### Problem: "Cannot remove worktree: uncommitted changes"

**Cause**: Worktree has uncommitted changes

**Solution**:
```bash
# Go to worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-templates

# Check status
git status

# Either commit changes
git add .
git commit -m "feat(templates): save work in progress"

# Or stash them
git stash

# Or force remove (DANGER: loses changes)
cd G:\Projects\proto-gear
git worktree remove --force ../proto-gear-worktrees/v0.5.0-templates
```

### Problem: Merge conflicts in `proto_gear.py`

**Cause**: Multiple workstreams modified same sections

**Solution**:
```bash
# View conflict
git diff proto_gear.py

# Edit file manually, look for:
<<<<<<< HEAD
existing code
=======
new code
>>>>>>> feature/v0.5.0-templates-core

# Keep both sections using section markers:
# ============ TEMPLATES ============
existing code
# ============ END TEMPLATES ========

# ============ SKILLS ===============
new code
# ============ END SKILLS ===========

# Mark resolved
git add core/proto_gear.py
git merge --continue
```

### Problem: Tests fail after merge

**Cause**: Incompatible changes between workstreams

**Solution**:
```bash
# Identify failing tests
python -m pytest -v

# Check what changed
git diff HEAD~1..HEAD

# Fix issues in merged code
# Re-run tests
python -m pytest

# If needed, amend merge commit
git add <fixed-files>
git commit --amend
```

### Problem: Cannot switch between worktrees in terminal

**Cause**: Confusion about which worktree you're in

**Solution**:
```bash
# Check current location
pwd
git branch    # Shows current branch

# Use full paths
cd G:\Projects\proto-gear                              # Main repo
cd G:\Projects\proto-gear-worktrees\v0.5.0-templates   # Templates worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-skills      # Skills worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-workflows   # Workflows worktree

# Or use git worktree list to see paths
git worktree list
```

### Problem: Worktree shows "locked" status

**Cause**: Worktree was locked (usually for maintenance)

**Solution**:
```bash
# Unlock worktree
git worktree unlock G:\Projects\proto-gear-worktrees\v0.5.0-templates

# Verify
git worktree list
```

### Problem: Git rerere causing incorrect auto-resolutions

**Cause**: Previous resolution was wrong

**Solution**:
```bash
# Clear rerere cache
rm -rf .git/rr-cache

# Disable rerere temporarily
git config rerere.enabled false

# Resolve conflict manually
# Then re-enable
git config rerere.enabled true
```

### Problem: Accidentally committed to wrong worktree

**Cause**: Working in wrong directory

**Solution**:
```bash
# Check where you are
pwd
git branch

# If committed to wrong branch:
# 1. Create patch
git format-patch HEAD~1

# 2. Reset commit
git reset --hard HEAD~1

# 3. Switch to correct worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-{correct}

# 4. Apply patch
git am < /path/to/patch/file
```

### Problem: Disk space running out

**Cause**: Multiple worktrees use disk space

**Solution**:
```bash
# Check worktree sizes
du -sh G:\Projects\proto-gear-worktrees\*

# Remove worktrees not actively used
git worktree remove ../proto-gear-worktrees/v0.5.0-completed

# Clean build artifacts in each worktree
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
```

---

## Best Practices

### Commit Strategy

#### Commit Frequency
- **Commit often**: Every logical change (10-50 lines)
- **Commit atomically**: One feature/fix per commit
- **Commit before switching context**: Don't leave uncommitted work

#### Commit Messages
Follow Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Adding tests
- `refactor`: Code restructuring
- `perf`: Performance improvement
- `chore`: Maintenance

**Scopes** (workstream-specific):
- `templates`: Template system
- `skills`: Skills system
- `workflows`: Workflows engine
- `cli`: CLI interface
- `docs`: Documentation
- `tests`: Test suite

**Examples**:

```bash
# Good commits
git commit -m "feat(templates): add CONTRIBUTING.md template"
git commit -m "feat(skills): implement debugging skill"
git commit -m "test(workflows): add bug-fix workflow tests"
git commit -m "docs(templates): update template-guide.md with new templates"

# Bad commits (avoid these)
git commit -m "update stuff"
git commit -m "fixes"
git commit -m "WIP"
```

### Branch Management

#### Keep Branches Up to Date
```bash
# Daily: Pull from development
git fetch origin development
git merge origin/development

# Resolve conflicts immediately, don't let them pile up
```

#### Branch Naming
- Use descriptive names
- Include version number (v0.5.0)
- Include workstream identifier
- Keep consistent with team

### Testing Philosophy

#### Test-Driven Development (TDD)
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green

#### Test Coverage
- Aim for 70%+ coverage
- Focus on critical paths
- Test edge cases
- Don't test framework code

#### Test Isolation
Each worktree should have:
- Independent test suite
- No dependencies on other workstreams
- Mock external dependencies

### Documentation

#### Code Documentation
- Add docstrings to new functions
- Update existing docstrings if behavior changes
- Keep comments up to date

#### User Documentation
- Update user guides for new features
- Add examples to docs
- Update README.md if needed

#### Developer Documentation
- Document architectural decisions
- Update PROJECT_STATUS.md
- Add notes to WORKSTREAM.md in each worktree

### Communication

If working with team:

1. **Daily Standup** (async is fine)
   - What did you complete yesterday?
   - What will you work on today?
   - Any blockers?

2. **Conflict Coordination**
   - Notify team before modifying shared files
   - Document changes in PROJECT_STATUS.md
   - Coordinate merge order

3. **Code Reviews**
   - Review before merging to development
   - Check for conflicts with other workstreams
   - Verify tests pass

### Performance Optimization

#### Resource Management
- Close IDEs/editors not actively used
- Clean build artifacts regularly
- Use `git worktree prune` periodically

#### Build Optimization
- Use virtual environments per worktree
- Share package cache when possible
- Parallel test execution

### Security

#### Protect Sensitive Data
- Never commit secrets or credentials
- Use `.gitignore` consistently
- Check commits before pushing

#### Branch Protection
- Don't force push to shared branches
- Don't rewrite public history
- Use signed commits if required

---

## Risk Assessment

### High Risk Areas

#### 1. `core/proto_gear.py` Conflicts
**Risk Level**: HIGH

**Description**: All three workstreams will modify this file

**Mitigation**:
- Use section markers clearly
- Merge sequentially (Templates → Skills → Workflows)
- Test after each merge
- Code review for this file specifically

**Recovery**:
- If merge breaks: `git merge --abort`
- Fix conflicts in isolated branch
- Test thoroughly before re-merging

#### 2. Test Suite Fragmentation
**Risk Level**: MEDIUM

**Description**: Tests may become inconsistent across workstreams

**Mitigation**:
- Define test conventions upfront
- Share test utilities/fixtures
- Run full test suite before merge

**Recovery**:
- Identify failing tests
- Fix in feature branch
- Re-run full suite

#### 3. Documentation Divergence
**Risk Level**: MEDIUM

**Description**: Docs may contradict between workstreams

**Mitigation**:
- Assign doc ownership per workstream
- Review docs during merge
- Use consistent terminology

**Recovery**:
- Audit all docs after final merge
- Reconcile contradictions
- Update as needed

#### 4. Dependency Conflicts
**Risk Level**: LOW

**Description**: Different workstreams may need different dependencies

**Mitigation**:
- Coordinate dependency changes
- Test after adding dependencies
- Document in `pyproject.toml`

**Recovery**:
- Resolve in `pyproject.toml` during merge
- Test with clean virtual environment

### Low Risk Areas

#### 1. Template Files
**Risk Level**: LOW

Each workstream creates new, independent template files. No conflicts expected.

#### 2. Skills Directory
**Risk Level**: LOW

Skills workstream owns `core/skills/` exclusively. No conflicts.

#### 3. Workflows Directory
**Risk Level**: LOW

Workflows workstream owns `core/workflows/` exclusively. No conflicts.

### Failure Scenarios

#### Scenario 1: Merge Conflicts Too Complex

**Symptoms**:
- Too many conflicts to resolve manually
- Conflicts in critical files
- Tests failing after resolution

**Response**:
1. Abort merge: `git merge --abort`
2. Analyze conflict sources
3. Coordinate with workstream owners
4. Create intermediate integration branch
5. Resolve conflicts incrementally
6. Test at each step

**Prevention**:
- Pull from development daily
- Merge development into feature branch regularly
- Use section markers in shared files

#### Scenario 2: Tests Break After Integration

**Symptoms**:
- Tests pass individually but fail together
- Integration issues between workstreams
- Unexpected behavior

**Response**:
1. Identify failing tests
2. Bisect to find breaking commit
3. Fix in feature branch
4. Re-test integration
5. Update tests if needed

**Prevention**:
- Write integration tests
- Test with other workstreams before merge
- Use continuous integration (CI)

#### Scenario 3: Performance Degradation

**Symptoms**:
- Slow test suite
- High memory usage
- Slow CLI commands

**Response**:
1. Profile code to find bottlenecks
2. Optimize hot paths
3. Consider lazy loading
4. Use caching where appropriate

**Prevention**:
- Performance tests in each workstream
- Monitor resource usage
- Optimize early

#### Scenario 4: Lost Work Due to Worktree Deletion

**Symptoms**:
- Accidentally deleted worktree directory
- Uncommitted changes lost

**Response**:
1. Check if commits exist: `git log feature/v0.5.0-templates-core`
2. If committed: Recreate worktree and checkout branch
3. If uncommitted: Check for editor backups
4. Use `git reflog` to find lost commits

**Prevention**:
- Commit frequently
- Push to remote regularly
- Use editor auto-save
- Enable Git hooks for uncommitted changes

### Risk Mitigation Summary

| Risk | Level | Mitigation | Recovery |
|------|-------|------------|----------|
| `proto_gear.py` conflicts | HIGH | Section markers, sequential merge | `git merge --abort`, fix in branch |
| Test fragmentation | MEDIUM | Test conventions, shared fixtures | Fix failing tests, re-run suite |
| Doc divergence | MEDIUM | Doc ownership, review | Audit and reconcile after merge |
| Dependency conflicts | LOW | Coordinate changes | Resolve in `pyproject.toml` |
| Complex merge conflicts | HIGH | Daily pulls, incremental merges | Abort, create integration branch |
| Integration test failures | MEDIUM | Integration tests, CI | Bisect, fix, re-test |
| Performance issues | LOW | Profile early, optimize | Profile, optimize hot paths |
| Lost work | MEDIUM | Commit often, push regularly | `git reflog`, editor backups |

---

## Appendix

### Quick Reference Commands

#### Setup
```bash
git worktree add -b <branch> <path> development
git config rerere.enabled true
```

#### Working
```bash
cd <worktree-path>
git status
git add .
git commit -m "feat(scope): message"
git push origin <branch>
```

#### Integration
```bash
cd G:\Projects\proto-gear
git checkout development
git merge <feature-branch> --no-ff
python -m pytest
git push origin development
```

#### Cleanup
```bash
git worktree remove <path>
git branch -d <branch>
git push origin --delete <branch>
```

### Useful Aliases

Add to `.gitconfig`:

```ini
[alias]
    wt = worktree
    wtl = worktree list
    wta = worktree add
    wtr = worktree remove
    wtp = worktree prune

    # View all branches with worktrees
    wtbr = !git branch -a | grep -E 'v0.5.0'

    # Quick log across all worktrees
    wtlog = log --oneline --graph --all --decorate

    # Status of all worktrees
    wtstatus = !git worktree list | while read line; do echo $line; git -C $(echo $line | awk '{print $1}') status -s; done
```

Usage:
```bash
git wt list
git wta -b feature/v0.5.0-test ../proto-gear-worktrees/test development
git wtlog
```

### Resources

- [Git Worktree Documentation](https://git-scm.com/docs/git-worktree)
- [Git Rerere Documentation](https://git-scm.com/docs/git-rerere)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Proto Gear Branching Strategy](./branching-strategy.md)
- [Proto Gear Project Structure](./project-structure.md)

---

## Changelog

### v1.0.0 (2025-11-08)
- Initial workflow document for v0.5.0 development
- Based on modern best practices (2024-2025)
- Incorporates lessons from v0.4.0 worktree experience
- Comprehensive setup, working, integration, and cleanup procedures
- Risk assessment and troubleshooting guide

---

**Document Status**: Active
**Next Review**: After v0.5.0 release
**Maintained By**: Proto Gear Development Team

*This workflow guide is a living document. Update it as we learn from v0.5.0 development.*
