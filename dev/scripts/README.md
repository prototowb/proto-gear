# Proto Gear Development Scripts

This directory contains automation scripts for Proto Gear v0.5.0 parallel development using Git worktrees.

## Available Scripts

### 1. worktree-setup.sh

**Purpose**: Automated setup of 3 worktrees for v0.5.0 parallel development

**Usage**:
```bash
bash dev/scripts/worktree-setup.sh
```

**What it does**:
1. Checks prerequisites (Git installed, on development branch, no uncommitted changes)
2. Enables Git rerere (reuse recorded resolution)
3. Creates worktrees directory: `G:\Projects\proto-gear-worktrees\`
4. Creates 3 worktrees:
   - `v0.5.0-templates` (feature/v0.5.0-templates-core)
   - `v0.5.0-skills` (feature/v0.5.0-skills-system)
   - `v0.5.0-workflows` (feature/v0.5.0-workflows-engine)
5. Makes initial commit in each worktree
6. Shows summary with next steps

**When to use**: Once at the beginning of v0.5.0 development

---

### 2. worktree-status.sh

**Purpose**: Check status of all worktrees and integration readiness

**Usage**:
```bash
bash dev/scripts/worktree-status.sh
```

**What it shows**:
- Main repository status
- Each worktree status (branch, uncommitted changes, commits ahead)
- Potential file conflicts between workstreams
- Test coverage overview
- Integration readiness for each workstream
- Summary with recommended next steps

**When to use**:
- Daily to monitor progress
- Before merging to check readiness
- To identify potential conflicts early

---

### 3. worktree-merge.sh

**Purpose**: Safely merge a workstream into development branch

**Usage**:
```bash
bash dev/scripts/worktree-merge.sh <workstream>

# Examples:
bash dev/scripts/worktree-merge.sh templates
bash dev/scripts/worktree-merge.sh skills
bash dev/scripts/worktree-merge.sh workflows
```

**What it does**:
1. Pre-merge checks (branch exists, no uncommitted changes, on development)
2. Runs tests in worktree (unit tests, coverage, linting, CLI)
3. Merges feature branch into development with --no-ff
4. Runs post-merge tests to ensure integration works
5. Optionally pushes to remote
6. Shows summary with next steps

**When to use**: When a workstream is complete and ready to integrate

**Recommended order**:
1. Templates (foundation)
2. Skills (builds on templates)
3. Workflows (uses both)

---

### 4. worktree-cleanup.sh

**Purpose**: Clean up worktrees and branches after successful merge

**Usage**:
```bash
bash dev/scripts/worktree-cleanup.sh <workstream>
bash dev/scripts/worktree-cleanup.sh all

# Examples:
bash dev/scripts/worktree-cleanup.sh templates   # Clean up templates only
bash dev/scripts/worktree-cleanup.sh all         # Clean up all worktrees
```

**What it does**:
1. Verifies branch is merged into development
2. Removes worktree directory
3. Deletes local feature branch
4. Optionally deletes remote feature branch
5. Shows final status

**When to use**:
- After successful merge and testing
- When ready to clean up (individually or all at once)

---

## Complete Workflow Example

### Phase 1: Setup

```bash
# Create all worktrees
bash dev/scripts/worktree-setup.sh
```

### Phase 2: Parallel Development

```bash
# Work in Templates worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-templates
# ... edit files, commit changes ...

# Work in Skills worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-skills
# ... edit files, commit changes ...

# Work in Workflows worktree
cd G:\Projects\proto-gear-worktrees\v0.5.0-workflows
# ... edit files, commit changes ...

# Check status periodically
bash dev/scripts/worktree-status.sh
```

### Phase 3: Integration (Sequential)

```bash
# Merge Templates first
bash dev/scripts/worktree-merge.sh templates

# Merge Skills second
bash dev/scripts/worktree-merge.sh skills

# Merge Workflows last
bash dev/scripts/worktree-merge.sh workflows
```

### Phase 4: Cleanup

```bash
# Option 1: Clean up individually after each merge
bash dev/scripts/worktree-cleanup.sh templates
bash dev/scripts/worktree-cleanup.sh skills
bash dev/scripts/worktree-cleanup.sh workflows

# Option 2: Clean up all at once after all merges
bash dev/scripts/worktree-cleanup.sh all
```

### Phase 5: Release

```bash
cd G:\Projects\proto-gear
git checkout development

# Tag release
git tag -a v0.5.0 -m "Release v0.5.0: Core Templates, Skills, and Workflows"

# Merge to main
git checkout main
git merge development --no-ff

# Push
git push origin main --tags
```

---

## Troubleshooting

### Script Permission Issues (Windows)

If scripts don't run on Windows:

```bash
# Use bash explicitly
bash dev/scripts/worktree-setup.sh

# Or run via Git Bash
```

### Script Not Found

Ensure you're in the main repository directory:

```bash
cd G:\Projects\proto-gear
bash dev/scripts/worktree-setup.sh
```

### Git Rerere Not Working

Manually enable:

```bash
git config rerere.enabled true
git config rerere.autoupdate true
```

### Merge Conflicts

If `worktree-merge.sh` encounters conflicts:

1. Script will show conflicted files
2. Edit files to resolve conflicts
3. Run:
   ```bash
   git add <resolved-files>
   git merge --continue
   python -m pytest  # Test after resolution
   ```

### Worktree Already Exists

If setup fails because worktree exists:

```bash
# Remove existing worktree
git worktree remove G:\Projects\proto-gear-worktrees\v0.5.0-templates --force

# Re-run setup
bash dev/scripts/worktree-setup.sh
```

---

## Script Customization

### Changing Paths

Edit the configuration section in each script:

```bash
# Configuration
MAIN_REPO="G:/Projects/proto-gear"
WORKTREES_DIR="G:/Projects/proto-gear-worktrees"
BASE_BRANCH="development"
```

### Adding New Workstreams

If adding a 4th workstream, edit the worktree definitions:

```bash
# Worktree definitions
declare -A WORKTREES
WORKTREES["templates"]="feature/v0.5.0-templates-core"
WORKTREES["skills"]="feature/v0.5.0-skills-system"
WORKTREES["workflows"]="feature/v0.5.0-workflows-engine"
WORKTREES["newfeature"]="feature/v0.5.0-newfeature-name"  # Add this
```

Then update all scripts with the new workstream.

---

## Best Practices

### Use Status Script Frequently

```bash
# Check status daily
bash dev/scripts/worktree-status.sh
```

This helps identify:
- Uncommitted changes
- Potential conflicts
- Integration readiness
- Test failures

### Test Before Merging

Always run tests in each worktree before merging:

```bash
cd G:\Projects\proto-gear-worktrees\v0.5.0-templates
python -m pytest
python -m pytest --cov=core --cov-report=term-missing
python -m flake8 core/
pg init --dry-run
```

Or let the merge script do it:

```bash
bash dev/scripts/worktree-merge.sh templates  # Tests automatically
```

### Merge Sequentially

Don't merge all at once. Merge in order:

1. Templates (foundation)
2. Skills (uses templates)
3. Workflows (uses both)

Test after each merge before proceeding.

### Clean Up Promptly

Remove worktrees after successful merge:

```bash
bash dev/scripts/worktree-cleanup.sh templates
```

This:
- Saves disk space
- Reduces confusion
- Keeps git worktree list clean

### Commit Frequently

In each worktree:

```bash
# Commit often (every logical change)
git add .
git commit -m "feat(templates): add CONTRIBUTING template"
```

This makes merge conflicts easier to resolve.

---

## Related Documentation

- **Full Workflow Guide**: `docs/dev/git-worktrees-workflow.md`
- **Quick Reference**: `docs/dev/worktrees-quick-reference.md`
- **Visual Diagrams**: `docs/dev/worktrees-workflow-diagram.md`
- **Branching Strategy**: `docs/dev/branching-strategy.md`

---

## Scripts Maintenance

### Testing Scripts

Before using scripts on actual worktrees:

1. Test on a separate Git repository
2. Verify paths are correct
3. Check error handling
4. Ensure rollback works

### Updating Scripts

When modifying scripts:

1. Update all 4 scripts if changing workstream definitions
2. Test changes in safe environment
3. Document changes in this README
4. Update version/date in script headers

### Contributing

When creating new scripts:

1. Follow existing naming convention: `worktree-<action>.sh`
2. Use consistent color coding
3. Add comprehensive error checking
4. Include help/usage functions
5. Document in this README

---

## Version History

### v1.0.0 (2025-11-08)

- Initial automation scripts for v0.5.0 development
- 4 core scripts: setup, status, merge, cleanup
- Full error handling and validation
- Integration with Git worktrees best practices

---

**Last Updated**: 2025-11-08
**For**: Proto Gear v0.5.0 Development
**Maintained By**: Proto Gear Development Team
