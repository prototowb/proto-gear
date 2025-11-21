# Proto Gear - Branching & Commit Strategy for AI Agents

**Version**: 1.0
**Effective Date**: 2025-10-30
**Purpose**: Define clear conventions for AI agents and developers working on Proto Gear

---

## Overview

This document defines the branching model, commit conventions, and workflow that **all contributors** (human and AI) must follow when working on Proto Gear. This ensures consistency, traceability, and safe collaboration.

---

## Branch Structure

### Protected Branches

#### `main`
- **Purpose**: Production-ready code
- **Status**: Always stable, deployable
- **Protection**: No direct commits, requires PR + review
- **Version tags**: All releases tagged here (v0.3.0, v0.4.0, etc.)

#### `development`
- **Purpose**: Integration branch for next release
- **Status**: Should always build and pass tests
- **Protection**: No direct commits for major changes
- **Merges from**: Feature, bugfix, hotfix branches
- **Merges to**: `main` (via release PR)

### Working Branches

#### Feature Branches: `feature/<issue-id>-<short-description>`
**Pattern**: `feature/PROTO-{number}-{kebab-case-description}`

**Examples**:
```
feature/PROTO-001-add-test-suite
feature/PROTO-002-config-validation
feature/PROTO-003-structured-logging
```

**Use for**:
- New features
- Enhancements to existing features
- Non-urgent improvements

**Lifecycle**:
1. Branch from: `development`
2. Work on feature
3. Merge to: `development` (via PR)
4. Delete after merge

#### Bugfix Branches: `bugfix/<issue-id>-<short-description>`
**Pattern**: `bugfix/PROTO-{number}-{kebab-case-description}`

**Examples**:
```
bugfix/PROTO-010-state-parsing-error
bugfix/PROTO-011-git-auth-failure
bugfix/PROTO-012-unicode-terminal-crash
```

**Use for**:
- Bug fixes
- Error corrections
- Issue resolution

**Lifecycle**:
1. Branch from: `development`
2. Fix bug
3. Add test to prevent regression
4. Merge to: `development` (via PR)
5. Delete after merge

#### Hotfix Branches: `hotfix/<version>-<issue-id>`
**Pattern**: `hotfix/v{version}-{issue-id}`

**Examples**:
```
hotfix/v0.3.1-critical-state-corruption
hotfix/v0.3.1-cli-crash
```

**Use for**:
- Critical production bugs
- Security vulnerabilities
- Data loss issues

**Lifecycle**:
1. Branch from: `main`
2. Apply minimal fix
3. Merge to: `main` AND `development`
4. Tag new version immediately
5. Delete after merge

#### Documentation Branches: `docs/<topic>`
**Pattern**: `docs/{topic-kebab-case}`

**Examples**:
```
docs/api-reference
docs/configuration-guide
docs/troubleshooting
```

**Use for**:
- Documentation updates
- README improvements
- Example additions

**Lifecycle**:
1. Branch from: `development`
2. Update documentation
3. Merge to: `development` (via PR)
4. Delete after merge

#### Refactor Branches: `refactor/<component>-<description>`
**Pattern**: `refactor/{component}-{description}`

**Examples**:
```
refactor/state-manager-validation
refactor/git-workflow-error-handling
refactor/cli-logging
```

**Use for**:
- Code refactoring (no behavior change)
- Performance improvements
- Technical debt reduction

**Lifecycle**:
1. Branch from: `development`
2. Refactor with tests to prove no regression
3. Merge to: `development` (via PR)
4. Delete after merge

---

## Commit Message Convention

### Format: Conventional Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(cli): add --version flag` |
| `fix` | Bug fix | `fix(state): handle malformed YAML gracefully` |
| `docs` | Documentation only | `docs(readme): update installation instructions` |
| `style` | Code style (formatting, no logic change) | `style(core): apply black formatting` |
| `refactor` | Code refactoring | `refactor(git): extract branch naming logic` |
| `perf` | Performance improvement | `perf(parser): optimize YAML parsing` |
| `test` | Add or update tests | `test(agent): add unit tests for sprint config` |
| `build` | Build system/dependencies | `build(deps): update pyyaml to 6.0.2` |
| `ci` | CI/CD changes | `ci(github): add pytest workflow` |
| `chore` | Maintenance tasks | `chore(version): bump to v0.3.1` |
| `revert` | Revert previous commit | `revert: feat(cli): add --version flag` |

### Scopes

Common scopes for Proto Gear:

- `cli` - Command-line interface (proto_gear.py)
- `agent` - Agent framework (agent_framework.py)
- `git` - Git workflow (git_workflow.py)
- `test` - Testing workflow (testing_workflow.py)
- `state` - State management (PROJECT_STATUS.md handling)
- `config` - Configuration management
- `docs` - Documentation
- `setup` - Package setup/installation

### Subject Guidelines

- Use imperative mood: "add" not "added" or "adds"
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters
- Clear and concise

### Body Guidelines (Optional but Recommended)

- Wrap at 72 characters
- Explain **what** and **why**, not **how**
- Separate from subject with blank line
- Use bullet points for multiple items

### Footer Guidelines (When Applicable)

- Reference issues: `Closes #123` or `Fixes PROTO-456`
- Breaking changes: `BREAKING CHANGE: <description>`
- Co-authors: `Co-authored-by: Name <email>`

### Examples

#### Simple Feature
```
feat(cli): add --version flag

Add --version flag to display current Proto Gear version.
Uses version string from setup.py.

Closes PROTO-015
```

#### Bug Fix with Details
```
fix(state): handle malformed PROJECT_STATUS.md gracefully

PROJECT_STATUS.md parsing was failing silently when YAML block
was malformed, causing workflow orchestrator to crash.

Changes:
- Add YAML validation before parsing
- Provide helpful error message with line number
- Fall back to default state on parse failure

Fixes PROTO-018
```

#### Breaking Change
```
feat(config)!: add schema validation for config files

BREAKING CHANGE: Configuration files now require specific schema.
Old config files will fail validation. Migration guide available
in docs/migration-guide.md.

- Add pydantic models for config validation
- Provide clear error messages for invalid configs
- Add examples/valid-config.yaml

Closes PROTO-020
```

#### Refactor
```
refactor(git): extract branch naming to separate method

No behavior change. Extracted branch name sanitization logic
from create_ticket_branch() to _sanitize_branch_name() for
better testability.
```

#### Documentation
```
docs(branching): add branching strategy for AI agents

Create comprehensive branching and commit strategy document
to ensure consistency across all contributors.

Co-authored-by: Claude <noreply@anthropic.com>
```

---

## Workflow for AI Agents

### Before Starting Work

1. **Check current branch**: Verify you're on `development`
2. **Pull latest changes**: `git pull origin development` (if remote configured)
3. **Create feature branch**: `git checkout -b feature/PROTO-XXX-description`
4. **Verify branch name**: Follows convention exactly

### During Development

1. **Make focused commits**: One logical change per commit
2. **Write good commit messages**: Follow convention above
3. **Test before committing**: Ensure code works
4. **Commit frequently**: Small commits are better than large ones
5. **Push to remote (optional)**: `git push -u origin feature/PROTO-XXX-description` (if remote configured, enables backup and collaboration)

### Before Creating PR

1. **Review all changes**: `git diff development`
2. **Ensure tests pass**: Run test suite if available
3. **Rebase if needed**: `git rebase development` (if behind)
4. **Push branch to remote**: `git push -u origin feature/PROTO-XXX-description` (required for PR)
5. **Verify remote**: `git branch -vv` (check tracking branch is set)

### Creating Pull Request

**PR Title**: Same format as commit message
```
feat(cli): add --version flag
```

**PR Description Template**:
```markdown
## Summary
Brief description of changes

## Changes Made
- Bullet list of changes
- What was added/fixed/refactored

## Testing
- How was this tested?
- What test cases were added?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Added/updated tests
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Commit messages follow convention

## Related Issues
Closes #XXX
```

---

## Issue Numbering

### Format: `PROTO-{number}`

- Start from: `PROTO-001`
- Increment sequentially
- Track in: GitHub Issues or PROJECT_STATUS.md

### Examples
```
PROTO-001: Add comprehensive test suite
PROTO-002: Implement config validation
PROTO-003: Add structured logging
PROTO-004: Update version to v0.3.0
PROTO-005: Create configuration examples
```

---

## AI Agent Specific Guidelines

### When You (AI Agent) Are Working

#### DO ✅

- **Always create a branch** for your work (never commit to `main` or `development` directly)
- **Use descriptive branch names** that clearly indicate the purpose
- **Write clear commit messages** following the convention
- **Make atomic commits** (one logical change per commit)
- **Reference issue numbers** in commits and PRs
- **Ask before breaking changes** if uncertain
- **Test your changes** before committing (at minimum, run `pg init --dry-run`)
- **Update documentation** when changing behavior
- **Add comments** for complex logic
- **Push to remote regularly** if remote is configured (enables backup and team visibility)
- **Check remote status** before creating PR (`git branch -vv`)

#### DON'T ❌

- **Don't commit directly to `main`** - ever
- **Don't commit directly to `development`** for features/refactors (only via PR)
- **Don't make huge commits** - break them down
- **Don't use vague commit messages** like "fix stuff" or "updates"
- **Don't skip testing** - even basic manual testing
- **Don't ignore merge conflicts** - resolve them properly
- **Don't delete branches** that others might be using
- **Don't force push** to shared branches

### Communication Protocol

When working as an AI agent, communicate your branching strategy:

```markdown
I'm going to:
1. Create branch: feature/PROTO-XXX-add-test-suite
2. Add test files for core modules
3. Commit with message: "test(agent): add unit tests for sprint configuration"
4. Push to remote (if configured): git push -u origin feature/PROTO-XXX-add-test-suite
5. Create PR (if remote exists)

Does this approach work for you?
```

#### Handling Remote Repositories

**If remote is configured**:
- Push regularly during development for backup
- Push before creating PR (required)
- Use `-u` flag on first push to set tracking branch

**If no remote configured** (local-only development):
- Work normally with local commits
- Merge to `development` locally
- No PR process needed

**Check remote status**:
```bash
# Check if remote exists
git remote -v

# Check tracking branch status
git branch -vv

# Check if branch is pushed
git status
```

---

## Version Numbering

### Semantic Versioning: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v0.x.x → v1.0.0)
- **MINOR**: New features, non-breaking (v0.3.x → v0.4.0)
- **PATCH**: Bug fixes, minor changes (v0.3.0 → v0.3.1)

### Pre-release Versions
- **Alpha**: `v0.3.0-alpha.1`
- **Beta**: `v0.4.0-beta.1`
- **RC**: `v1.0.0-rc.1`

### Current Version Strategy
- Currently: `v0.3.0` (should be updated from v3.0.0)
- Next: `v0.3.1` (patch fixes)
- Then: `v0.4.0` (test suite added)
- Future: `v1.0.0` (production-ready)

---

## Release Process

### 🚨 CRITICAL: GitHub Release is Mandatory

**Every tagged release MUST have a corresponding GitHub release with release notes.**

This is NOT optional. The release process is incomplete without it.

**Why?**
- Users rely on GitHub releases to track changes
- Release notes provide context and migration guidance
- Maintains professional project standards
- Enables automated notifications to watchers

**How to check if you forgot:**
```bash
# List all tags
git tag

# List all GitHub releases
gh release list

# If a tag exists but no release, create it immediately:
gh release create v0.X.X --title "v0.X.X - Title" --notes "Release notes..."
```

**For AI Agents**: After pushing a tag, immediately create the GitHub release. Do not wait. Do not skip this step.

---

### Patch Release (v0.3.0 → v0.3.1)

1. Create hotfix branch: `hotfix/v0.3.1-fixes`
2. Apply fixes
3. Update version in `setup.py` and `core/proto_gear_pkg/__init__.py`
4. Update `CHANGELOG.md`
5. Merge to `main` via PR
6. Tag: `git tag -a v0.3.1 -m "Release v0.3.1: Brief description"`
7. Push tags: `git push origin v0.3.1`
8. **🚨 CRITICAL**: Create GitHub release with `gh release create v0.3.1 --title "v0.3.1 - Title" --notes "Release notes..."`
9. Merge `main` back to `development`
10. Update PROJECT_STATUS.md with release details

### Minor Release (v0.3.x → v0.4.0)

1. Feature freeze on `development`
2. Create release branch: `release/v0.4.0`
3. Final testing and bug fixes
4. Update version in `pyproject.toml` and `core/proto_gear_pkg/__init__.py`
5. Update `CHANGELOG.md`
6. Merge to `main` via PR
7. Tag: `git tag -a v0.4.0 -m "Release v0.4.0: Brief description"`
8. Push tags: `git push origin v0.4.0`
9. **🚨 CRITICAL**: Create GitHub release with `gh release create v0.4.0 --title "v0.4.0 - Title" --notes "$(cat <<'EOF'
   # Release Notes
   ## Features
   - Feature 1
   - Feature 2
   ## Bug Fixes
   - Fix 1
   EOF
   )"`
10. Merge `main` back to `development`
11. Update PROJECT_STATUS.md with release details
12. Update readiness assessment (docs/dev/readiness-assessment.md)

### Major Release (v0.x.x → v1.0.0)

1. Comprehensive testing
2. Security audit
3. Documentation review
4. Create release branch: `release/v1.0.0`
5. Release candidate: `v1.0.0-rc.1`
6. Community testing period
7. Final fixes
8. Update all documentation
9. Update version in `pyproject.toml` and `core/proto_gear_pkg/__init__.py`
10. Update `CHANGELOG.md` with comprehensive release notes
11. Merge to `main` via PR
12. Tag: `git tag -a v1.0.0 -m "Release v1.0.0: Production Ready"`
13. Push tags: `git push origin v1.0.0`
14. **🚨 CRITICAL**: Create GitHub release with comprehensive notes:
    ```bash
    gh release create v1.0.0 \
      --title "v1.0.0 - Production Ready" \
      --notes-file RELEASE_NOTES_v1.0.0.md
    ```
15. Merge `main` back to `development`
16. Update PROJECT_STATUS.md with release details
17. Update readiness assessment (docs/dev/readiness-assessment.md)
18. Announce on social media, blog, etc.

---

## Tools & Automation

### Pre-commit Hooks

**.git/hooks/pre-commit** (auto-generated by Proto Gear):
```bash
#!/bin/sh
# Check commit message format
# Run linting (if configured)
# Run tests (if available)
```

### Commit Message Validation

Consider adding commitlint:
```bash
npm install -g @commitlint/cli @commitlint/config-conventional
echo "module.exports = {extends: ['@commitlint/config-conventional']}" > commitlint.config.js
```

### Branch Protection Rules (GitHub)

Recommended settings:
- `main`: Require PR, require reviews, require status checks
- `development`: Require PR for major changes, allow fast-forward merges

---

## Examples of Full Workflows

### Example 1: Adding Test Suite (Feature)

```bash
# 1. Start from development
git checkout development
git pull origin development

# 2. Create feature branch
git checkout -b feature/PROTO-001-add-test-suite

# 3. Create test files
mkdir -p tests
touch tests/test_cli.py
# ... write tests ...

# 4. Commit incrementally
git add tests/test_cli.py
git commit -m "test(cli): add tests for pg init command"

git add tests/test_agent_framework.py
git commit -m "test(agent): add tests for sprint configuration"

# 5. Push branch to remote (if remote configured)
git push -u origin feature/PROTO-001-add-test-suite

# 6. Create PR on GitHub (if remote exists)
# Title: "test(all): add comprehensive test suite"
# Description: Reference PROTO-001, explain coverage

# OR if no remote: Merge locally
# git checkout development
# git merge feature/PROTO-001-add-test-suite --no-ff
```

### Example 2: Fixing Bug (Bugfix)

```bash
# 1. Start from development
git checkout development
git pull origin development

# 2. Create bugfix branch
git checkout -b bugfix/PROTO-010-state-parsing-error

# 3. Fix the bug
# Edit agent_framework.py

# 4. Add regression test
# Edit tests/test_state_management.py

# 5. Commit with clear message
git add agent_framework.py tests/test_state_management.py
git commit -m "fix(state): handle malformed PROJECT_STATUS.md gracefully

Added validation before YAML parsing to prevent crashes.
Provides helpful error messages with line numbers.

Fixes PROTO-010"

# 6. Push and create PR
git push -u origin bugfix/PROTO-010-state-parsing-error
```

### Example 3: Documentation Update (Docs)

```bash
# 1. Start from development
git checkout development
git pull origin development

# 2. Create docs branch
git checkout -b docs/configuration-guide

# 3. Add documentation
touch docs/CONFIGURATION.md
# ... write documentation ...

# 4. Commit
git add docs/CONFIGURATION.md
git commit -m "docs(config): add configuration reference guide

Complete guide covering all configuration options with examples."

# 5. Push and create PR
git push -u origin docs/configuration-guide
```

---

## Enforcement

### For Human Contributors
- CI/CD will validate commit messages
- PRs without proper branch names will be rejected
- Maintainers will request changes if conventions not followed

### For AI Agents
- This document is the source of truth
- AI agents should reference this before starting work
- Non-compliant commits may be reverted
- Pattern matching will be used to validate AI contributions

---

## Quick Reference Card

```
BRANCH PATTERNS:
feature/PROTO-XXX-description    → New features
bugfix/PROTO-XXX-description     → Bug fixes
hotfix/vX.Y.Z-issue              → Critical fixes
docs/topic                       → Documentation
refactor/component-description   → Refactoring

COMMIT FORMAT:
<type>(<scope>): <subject>

TYPES:
feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert

ALWAYS:
✅ Branch from development
✅ Use descriptive names
✅ Write clear commits
✅ Test before pushing
✅ Push to remote (if configured)
✅ Create PR for review (if remote)

NEVER:
❌ Commit to main directly
❌ Use vague messages
❌ Skip testing
❌ Force push shared branches
❌ Forget to push to remote before PR
```

---

**Document Status**: Active
**Last Updated**: 2025-10-30
**Version**: 1.1 (Added remote repository handling)
**Maintained By**: Proto Gear Team
**Enforced By**: All contributors (human and AI)
