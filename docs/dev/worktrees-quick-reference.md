# Git Worktrees Quick Reference

**For v0.5.0 Parallel Development**

---

## Setup (Do Once)

```bash
# Enable Git rerere
git config rerere.enabled true
git config rerere.autoupdate true

# Create worktrees directory
mkdir G:\Projects\proto-gear-worktrees

# Create 3 worktrees
cd G:\Projects\proto-gear
git worktree add -b feature/v0.5.0-templates-core ../proto-gear-worktrees/v0.5.0-templates development
git worktree add -b feature/v0.5.0-skills-system ../proto-gear-worktrees/v0.5.0-skills development
git worktree add -b feature/v0.5.0-workflows-engine ../proto-gear-worktrees/v0.5.0-workflows development

# Verify
git worktree list
```

---

## Daily Workflow

```bash
# Work in Templates
cd G:\Projects\proto-gear-worktrees\v0.5.0-templates
# ... edit files ...
git add .
git commit -m "feat(templates): add CONTRIBUTING template"
git push origin feature/v0.5.0-templates-core

# Work in Skills
cd G:\Projects\proto-gear-worktrees\v0.5.0-skills
# ... edit files ...
git add .
git commit -m "feat(skills): implement debugging skill"
git push origin feature/v0.5.0-skills-system

# Work in Workflows
cd G:\Projects\proto-gear-worktrees\v0.5.0-workflows
# ... edit files ...
git add .
git commit -m "feat(workflows): add bug-fix workflow"
git push origin feature/v0.5.0-workflows-engine
```

---

## Testing Before Merge

```bash
cd G:\Projects\proto-gear-worktrees\v0.5.0-{workstream}

# Run tests
python -m pytest tests/ -v

# Check coverage
python -m pytest --cov=core --cov-report=term-missing

# Lint
python -m flake8 core/

# Test CLI
pg init --dry-run
```

---

## Integration (Sequential)

### 1. Merge Templates
```bash
cd G:\Projects\proto-gear
git checkout development
git pull origin development
git merge feature/v0.5.0-templates-core --no-ff
python -m pytest
git push origin development
```

### 2. Merge Skills
```bash
cd G:\Projects\proto-gear
git checkout development
git pull origin development
git merge feature/v0.5.0-skills-system --no-ff
python -m pytest
git push origin development
```

### 3. Merge Workflows
```bash
cd G:\Projects\proto-gear
git checkout development
git pull origin development
git merge feature/v0.5.0-workflows-engine --no-ff
python -m pytest
git push origin development
```

---

## Cleanup

```bash
# After successful merge
cd G:\Projects\proto-gear

# Remove worktrees
git worktree remove ../proto-gear-worktrees/v0.5.0-templates
git worktree remove ../proto-gear-worktrees/v0.5.0-skills
git worktree remove ../proto-gear-worktrees/v0.5.0-workflows

# Delete branches (optional)
git branch -d feature/v0.5.0-templates-core
git branch -d feature/v0.5.0-skills-system
git branch -d feature/v0.5.0-workflows-engine

# Delete remote branches (optional)
git push origin --delete feature/v0.5.0-templates-core
git push origin --delete feature/v0.5.0-skills-system
git push origin --delete feature/v0.5.0-workflows-engine

# Verify
git worktree list
```

---

## Troubleshooting

### Merge Conflict
```bash
git status                          # See conflicts
# Edit conflicted files
git add <resolved-files>
git merge --continue
python -m pytest                    # Test
```

### Abort Merge
```bash
git merge --abort
```

### Check Worktree Status
```bash
git worktree list
cd <worktree-path>
git status
git branch
```

### Force Remove Worktree
```bash
git worktree remove --force <path>
```

### View Changes
```bash
git log --oneline --graph --all --decorate
git diff development..feature/v0.5.0-templates-core
```

---

## Useful Commands

```bash
# List all worktrees
git worktree list

# List all branches
git branch -a

# View commit history across all branches
git log --oneline --graph --all

# Check current branch
git branch

# Pull latest from development
git fetch origin development
git merge origin/development

# See what files changed
git diff --name-only development..HEAD
```

---

## Best Practices

1. **Commit often** - Every logical change
2. **Test before merge** - All tests must pass
3. **Pull daily** - Stay synced with development
4. **Use section markers** - In shared files like `proto_gear.py`
5. **Sequential merge** - Templates → Skills → Workflows
6. **Clean up promptly** - Remove worktrees after merge

---

## Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: feat, fix, docs, test, refactor, chore
**Scopes**: templates, skills, workflows, cli, tests, docs

**Examples**:
```bash
git commit -m "feat(templates): add SECURITY template"
git commit -m "feat(skills): implement code-review skill"
git commit -m "test(workflows): add release workflow tests"
```

---

**Full Documentation**: See `docs/dev/git-worktrees-workflow.md`
