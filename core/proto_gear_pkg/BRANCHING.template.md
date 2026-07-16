<!-- proto-gear:header
purpose: Git workflow — branch naming, commit format, merge strategy
read-when: Before creating branches or commits
priority: required-if-exists
defines:
  - branch-naming-convention
  - conventional-commit-format
  - workflow-mode
  - pr-creation
  - release-process
links:
  - AGENTS.md
  - PROJECT_STATUS.md
-->
# Branching & Commit Strategy

**Project**: {{PROJECT_NAME}}
**Ticket Prefix**: {{TICKET_PREFIX}}

---

## 📚 Related Documentation

- **AGENTS.md** - Agent workflows, collaboration patterns, and capability discovery
- **PROJECT_STATUS.md** - Current project state, active tickets, sprint info
- **TESTING.md** (if exists) - TDD methodology and testing patterns
- **.proto-gear/INDEX.md** (if exists) - Available capabilities and git workflows

---

## Workflow Mode

{{WORKFLOW_MODE}}
{{WORKFLOW_RECOMMENDATIONS}}

---

## Overview

This document defines the branching model and commit conventions for {{PROJECT_NAME}}.
Following these conventions ensures consistency across all contributors
(human and AI).

---

## Branch Structure

### Main Branches

#### `{{MAIN_BRANCH}}`
- **Purpose**: Production-ready code
- **Status**: Always stable, deployable
- **Protection**: No direct commits{{REMOTE_REQUIRES_PR}}

#### `{{DEV_BRANCH}}`
- **Purpose**: Integration branch for development
- **Status**: Should always build{{REMOTE_REQUIRES_TESTS}}
- **Merges from**: Feature, bugfix branches (locally)
- **Merges to**: `{{MAIN_BRANCH}}`{{REMOTE_VIA_PR}}{{PUSH_DEV_INFO}}

### Working Branches

#### Feature Branches: `feature/{{TICKET_PREFIX}}-{number}-{description}`

**Examples**:
```
feature/{{TICKET_PREFIX}}-001-implement-auth
feature/{{TICKET_PREFIX}}-002-add-dashboard
```

**Use for**: New features, enhancements, non-urgent improvements

**Lifecycle**:
1. Branch from: `{{DEV_BRANCH}}`
2. Work on feature
3. Merge to: `{{DEV_BRANCH}}`
4. Delete after merge

#### Bugfix Branches: `bugfix/{{TICKET_PREFIX}}-{number}-{description}`

**Examples**:
```
bugfix/{{TICKET_PREFIX}}-010-fix-login-error
bugfix/{{TICKET_PREFIX}}-011-resolve-crash
```

**Use for**: Bug fixes, error corrections, issue resolution

**Lifecycle**:
1. Branch from: `{{DEV_BRANCH}}`
2. Fix bug
3. Add regression test
4. Merge to: `{{DEV_BRANCH}}`
5. Delete after merge

#### Hotfix Branches: `hotfix/v{version}-{issue}`

**Examples**:
```
hotfix/v1.2.1-critical-security-fix
hotfix/v1.2.1-data-loss-bug
```

**Use for**: Critical production bugs, security vulnerabilities, data loss issues

**Lifecycle**:
1. Branch from: `{{MAIN_BRANCH}}`
2. Apply minimal fix
3. Merge to: `{{MAIN_BRANCH}}` AND `{{DEV_BRANCH}}`
4. Tag new version immediately
5. Delete after merge

---

## Starting New Work

### Critical Rule: Protect `{{MAIN_BRANCH}}`; `{{DEV_BRANCH}}` is open

**Never commit directly to `{{MAIN_BRANCH}}`** — it lands only via a reviewed PR.
**`{{DEV_BRANCH}}` is open**: commit to it directly when that's the simplest thing
(small fixes, docs, ticket bookkeeping). A feature branch + PR is still the norm
for substantial or shared work — it gives you CI and review — but it is no longer
required for everything. When in doubt on something sizeable, branch.

```bash
# Substantial/shared work: branch FROM development (regardless of current branch)
git checkout -b feature/{{TICKET_PREFIX}}-XXX-description {{DEV_BRANCH}}
```

**Example Workflow**:
```bash
git checkout -b feature/{{TICKET_PREFIX}}-042-add-search {{DEV_BRANCH}}

# Do your work
git add .
git commit -m "feat(search): implement search functionality"

# Merge back to development when done
git checkout {{DEV_BRANCH}}
git merge feature/{{TICKET_PREFIX}}-042-add-search
git branch -d feature/{{TICKET_PREFIX}}-042-add-search
{{EXAMPLE_POST_MERGE}}```

---

## Commit Message Convention

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(auth): add login functionality` |
| `fix` | Bug fix | `fix(api): handle null response` |
| `docs` | Documentation | `docs(readme): update setup instructions` |
| `style` | Code style | `style: apply formatting` |
| `refactor` | Refactoring | `refactor(db): optimize queries` |
| `perf` | Performance | `perf(api): cache responses` |
| `test` | Tests | `test(auth): add login tests` |
| `build` | Build system | `build: update dependencies` |
| `ci` | CI/CD | `ci: add test workflow` |
| `chore` | Maintenance | `chore: update version` |

### Subject Guidelines

- Use imperative mood: "add" not "added"
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### Body (Optional)

- Wrap at 72 characters
- Explain what and why, not how
- Separate from subject with blank line

### Footer (When Applicable)

- Reference issues: `Closes {{TICKET_PREFIX}}-XXX`
- Breaking changes: `BREAKING CHANGE: description`

### Examples

```
feat(dashboard): add user analytics widget

Add real-time analytics widget showing active users,
session duration, and conversion metrics.

Closes {{TICKET_PREFIX}}-042
```

```
fix(api): handle timeout errors gracefully

API calls were failing without proper error handling
when external service timed out.

Fixes {{TICKET_PREFIX}}-089
```

---

## Workflow for Contributors

### Before Starting Work

1. **Pull latest changes**: `git pull{{REMOTE_ORIGIN}} {{DEV_BRANCH}}`{{IF_REMOTE}}
2. **Create feature branch**: `git checkout -b feature/{{TICKET_PREFIX}}-XXX-description {{DEV_BRANCH}}`
3. **Verify branch name**: Follows convention exactly

### During Development

1. **Make focused commits**: One logical change per commit
2. **Write clear commit messages**: Follow convention above
3. **Test before committing**: Ensure code works
{{REMOTE_PUSH_DURING}}

### Before Merging

1. **Review all changes**: `git diff {{DEV_BRANCH}}`
2. **Ensure tests pass**: Run your test suite
3. **Update from {{DEV_BRANCH}}**: `git rebase {{DEV_BRANCH}}` (if behind)
{{BEFORE_MERGE_STEPS}}

---

## Working with AI Agents

### Conventions for AI Assistants

When working with AI assistants (Claude, GPT, etc.), ensure they:

**DO**:
- Create branches for all work
- Use descriptive branch names
- Write clear commit messages following convention
- Reference ticket numbers ({{TICKET_PREFIX}}-XXX)
- Test changes before committing
- Update documentation when behavior changes

**DON'T**:
- Commit directly to `{{MAIN_BRANCH}}` (PR only)
- Skip a feature branch + PR for substantial or shared work (direct-to-`{{DEV_BRANCH}}` is fine for small/local changes)
- Use vague commit messages
- Skip testing
- Force-push to shared branches

---

## Ticket Numbering

### Format: `{{TICKET_PREFIX}}-{number}`

- Start from: `{{TICKET_PREFIX}}-001`
- Increment sequentially
- Track in: {{TICKET_TRACKING}}

### Examples
```
{{TICKET_PREFIX}}-001: Implement user authentication
{{TICKET_PREFIX}}-002: Add dashboard widgets
{{TICKET_PREFIX}}-003: Fix login redirect issue
```

---

## Quick Reference

```
BRANCH PATTERNS:
feature/{{TICKET_PREFIX}}-XXX-description    → New features
bugfix/{{TICKET_PREFIX}}-XXX-description     → Bug fixes
hotfix/vX.Y.Z-issue                          → Critical fixes

COMMIT FORMAT:
<type>(<scope>): <subject>

TYPES:
feat, fix, docs, style, refactor, perf, test, build, ci, chore

ALWAYS:
✅ Branch from {{DEV_BRANCH}} for substantial/shared work
✅ Use descriptive names
✅ Write clear commits
✅ Test before committing
{{QUICK_REMOTE_RULES}}
NEVER:
❌ Commit to {{MAIN_BRANCH}} directly (PR only)
❌ Skip branch + PR for substantial or shared work ({{DEV_BRANCH}} is open for small/local commits)
❌ Use vague messages
❌ Skip testing
{{QUICK_NEVER_REMOTE}}```

{{REMOTE_HANDLING_SECTION}}

---

**Document Status**: Active
**Generated**: {{GENERATION_DATE}}
**Maintained By**: {{PROJECT_NAME}} team

---

## Automated Branch Enforcement

### Branch Creation Pattern

When creating tickets, branches should be automatically created following the naming convention:

```python
def enforce_branching_strategy(ticket):
    """
    Ensures proper branch creation and management.
    MANDATORY: Called automatically when any ticket is created.
    """
    ticket_id = ticket['id']

    # Determine branch name based on ticket type
    if ticket['type'] == 'feature':
        branch = f"feature/{ticket_id}-{ticket['slug']}"
    elif ticket['type'] == 'bugfix':
        branch = f"bugfix/{ticket_id}-{ticket['slug']}"
    elif ticket['type'] == 'hotfix':
        branch = f"hotfix/{ticket_id}-{ticket['slug']}"
    else:
        branch = f"task/{ticket_id}-{ticket['slug']}"

    # Create branch from development
    execute_command("git checkout {{DEV_BRANCH}}")
    execute_command(f"git checkout -b {branch}")

    # Update ticket with branch info
    ticket['branch'] = branch
    ticket['branch_created'] = True

    print(f"Created branch: {branch}")
    return branch
```

### Enforcement Rules

1. **Every ticket gets a branch** — no exceptions
2. **Branch names follow the convention** — `{type}/{ticket_id}-{slug}`
3. **Branches created from `{{DEV_BRANCH}}`** — never from `{{MAIN_BRANCH}}` (except hotfixes)
4. **Branches deleted after merge** — keep the branch list clean
5. **Test structure created alongside branch** — see TESTING.md for test enforcement

### Enforcing "never commit to `{{MAIN_BRANCH}}`"

The rule above is documentation; the enforcement is a check that returns a
non-zero exit code, so it can't be talked past:

- **`pg guard branch`** exits non-zero when HEAD is on a protected branch
  (`main`/`master` by default). It never rewrites history — it just refuses.
- **`pg hooks install`** drops a branch-guard `pre-commit` hook into
  `.git/hooks/` that runs `pg guard branch` before every commit (no-clobber: an
  existing hook is left alone with instructions to chain the guard). Run it once
  per clone.
- **CI**: add `pg guard branch` as a job step to enforce the same rule server-side.

Keep the prose rule as the *why*; `pg guard` / the hook / CI are the *how*.

---

*This branching strategy was generated by Proto Gear to help maintain consistency in AI-assisted development. Customize this file to match your team's specific needs.*
