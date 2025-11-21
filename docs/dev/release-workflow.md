# Release Workflow - Proto Gear

**Purpose**: This document defines the complete release process for Proto Gear, ensuring consistency and completeness for all releases.

**Audience**: Human and AI contributors performing releases

---

## 🚨 CRITICAL: GitHub Release is Mandatory

**Every tagged release MUST have a corresponding GitHub release with release notes.**

This is NOT optional. The release process is incomplete without it.

**Why?**
- Users rely on GitHub releases to track changes
- Release notes provide context and migration guidance
- Maintains professional project standards
- Enables automated notifications to watchers
- Provides a single source of truth for release history

**How to check if you forgot:**
```bash
# List all tags
git tag

# List all GitHub releases
gh release list

# If a tag exists but no release, create it immediately:
gh release create v0.X.X --title "v0.X.X - Title" --notes "Release notes..."
```

**For AI Agents**: After pushing a tag, immediately create the GitHub release. Do not wait. Do not skip this step. The release is not complete until the GitHub release exists.

---

## Prerequisites

Before performing any release:

1. **GitHub CLI installed**: `gh --version` should work
2. **Authenticated with GitHub**: `gh auth status` should show you're logged in
3. **On `main` branch**: `git branch --show-current` should show `main`
4. **Working tree clean**: `git status` should show no uncommitted changes
5. **All tests passing**: Run `pytest` to verify
6. **Up to date with remote**: `git pull origin main` completes without conflicts

---

## Release Types

### Patch Release (v0.X.Y → v0.X.Y+1)

**When to use**: Bug fixes, minor improvements, no new features

**Example**: v0.7.0 → v0.7.1

**Process**:

1. **Create hotfix branch** from `main`:
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/v0.7.1-bug-fixes
   ```

2. **Apply fixes** and commit with conventional commit messages

3. **Update version** in TWO places:
   ```bash
   # Edit pyproject.toml: version = "0.7.1"
   # Edit core/proto_gear_pkg/__init__.py: __version__ = "0.7.1"
   ```

4. **Update CHANGELOG.md**:
   ```markdown
   ## [0.7.1] - 2025-11-21

   ### Fixed
   - Bug fix 1
   - Bug fix 2
   ```

5. **Commit version bump**:
   ```bash
   git add pyproject.toml core/proto_gear_pkg/__init__.py CHANGELOG.md
   git commit -m "chore(version): bump version to 0.7.1"
   ```

6. **Merge to `main`** via PR or direct merge:
   ```bash
   git checkout main
   git merge hotfix/v0.7.1-bug-fixes
   ```

7. **Tag the release**:
   ```bash
   git tag -a v0.7.1 -m "Release v0.7.1: Brief description of fixes"
   ```

8. **Push tag to remote**:
   ```bash
   git push origin v0.7.1
   ```

9. **🚨 CRITICAL - Create GitHub release**:
   ```bash
   gh release create v0.7.1 \
     --title "v0.7.1 - Bug Fixes" \
     --notes "$(cat <<'EOF'
   # Proto Gear v0.7.1 - Bug Fixes

   **Release Date**: 2025-11-21

   ## 🐛 Bug Fixes
   - Fixed issue 1
   - Fixed issue 2

   ## 📊 Changes
   - X files changed
   - Y lines added/removed

   **Full Changelog**: https://github.com/prototowb/proto-gear/compare/v0.7.0...v0.7.1
   EOF
   )"
   ```

10. **Merge `main` back to `development`**:
    ```bash
    git checkout development
    git merge main
    git push origin development
    ```

11. **Update PROJECT_STATUS.md**:
    - Update version to v0.7.1
    - Update release_date
    - Add release notes to Recent Updates section

12. **Verify release**:
    ```bash
    gh release view v0.7.1
    ```

---

### Minor Release (v0.X.Y → v0.X+1.0)

**When to use**: New features, enhancements, backwards-compatible changes

**Example**: v0.7.0 → v0.8.0

**Process**:

1. **Feature freeze on `development`**:
   - Announce feature freeze to team
   - Only bug fixes and polish from this point

2. **Create release branch** from `development`:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b release/v0.8.0
   ```

3. **Final testing and bug fixes**:
   - Run full test suite
   - Test edge cases
   - Fix any issues found

4. **Update version** in TWO places:
   ```bash
   # Edit pyproject.toml: version = "0.8.0"
   # Edit core/proto_gear_pkg/__init__.py: __version__ = "0.8.0"
   ```

5. **Update CHANGELOG.md** with comprehensive notes:
   ```markdown
   ## [0.8.0] - 2025-11-25

   ### Added
   - New feature 1
   - New feature 2

   ### Changed
   - Enhancement 1
   - Enhancement 2

   ### Fixed
   - Bug fix 1
   ```

6. **Commit version bump**:
   ```bash
   git add pyproject.toml core/proto_gear_pkg/__init__.py CHANGELOG.md
   git commit -m "chore(version): bump version to 0.8.0"
   ```

7. **Merge to `main`** via PR:
   ```bash
   git checkout main
   git merge release/v0.8.0
   ```

8. **Tag the release**:
   ```bash
   git tag -a v0.8.0 -m "Release v0.8.0: Brief feature summary"
   ```

9. **Push tag to remote**:
   ```bash
   git push origin v0.8.0
   ```

10. **🚨 CRITICAL - Create GitHub release with comprehensive notes**:
    ```bash
    gh release create v0.8.0 \
      --title "v0.8.0 - Feature Name" \
      --notes "$(cat <<'EOF'
    # Proto Gear v0.8.0 - Feature Name

    **Release Date**: 2025-11-25

    ## 🚀 What's New

    ### Feature Category 1
    - Feature 1 description
    - Feature 2 description

    ### Feature Category 2
    - Enhancement 1
    - Enhancement 2

    ## 🐛 Bug Fixes
    - Fix 1
    - Fix 2

    ## 📊 Statistics
    - Lines Added: X lines
    - Test Coverage: Y%
    - Tests Added: Z tests

    ## 📚 Documentation
    - New documentation files
    - Updated guides

    ## 🔧 Technical Details
    [Detailed technical information]

    **Full Changelog**: https://github.com/prototowb/proto-gear/compare/v0.7.0...v0.8.0

    🤖 Generated with Claude Code
    EOF
    )"
    ```

11. **Merge `main` back to `development`**:
    ```bash
    git checkout development
    git merge main
    git push origin development
    ```

12. **Update PROJECT_STATUS.md**:
    - Update version to v0.8.0
    - Update release_date
    - Add comprehensive release notes
    - Update completed tickets section
    - Clear active tickets if needed

13. **Update readiness assessment** (`docs/dev/readiness-assessment.md`):
    - Update version and assessment date
    - Update scores and metrics
    - Document new features and improvements
    - Update test coverage statistics

14. **Clean up release branch**:
    ```bash
    git branch -d release/v0.8.0
    git push origin --delete release/v0.8.0
    ```

15. **Verify release**:
    ```bash
    gh release view v0.8.0
    ```

---

### Major Release (v0.X.Y → v1.0.0)

**When to use**: Breaking changes, major milestones, production readiness

**Example**: v0.9.0 → v1.0.0

**Process**:

1. **Comprehensive testing**:
   - Full test suite must pass
   - Manual testing of all features
   - Cross-platform testing
   - Performance testing

2. **Security audit**:
   - Review all code for security issues
   - Check dependencies for vulnerabilities
   - Review authentication/authorization
   - Validate input sanitization

3. **Documentation review**:
   - All user documentation up to date
   - All developer documentation current
   - Migration guides prepared
   - Breaking changes documented

4. **Create release branch** from `development`:
   ```bash
   git checkout development
   git pull origin development
   git checkout -b release/v1.0.0
   ```

5. **Create release candidate**:
   ```bash
   git tag -a v1.0.0-rc.1 -m "Release candidate 1 for v1.0.0"
   git push origin v1.0.0-rc.1
   ```

6. **Community testing period**:
   - Announce RC to users
   - Collect feedback
   - Monitor for issues

7. **Apply final fixes** based on feedback

8. **Update all documentation**:
   - README.md
   - User guides
   - Developer guides
   - Migration guides
   - CHANGELOG.md

9. **Update version** in TWO places:
   ```bash
   # Edit pyproject.toml: version = "1.0.0"
   # Edit core/proto_gear_pkg/__init__.py: __version__ = "1.0.0"
   ```

10. **Update CHANGELOG.md** with comprehensive release notes

11. **Commit version bump**:
    ```bash
    git add pyproject.toml core/proto_gear_pkg/__init__.py CHANGELOG.md
    git commit -m "chore(version): bump version to 1.0.0 - PRODUCTION READY"
    ```

12. **Merge to `main`** via PR with thorough review:
    ```bash
    git checkout main
    git merge release/v1.0.0
    ```

13. **Tag the release**:
    ```bash
    git tag -a v1.0.0 -m "Release v1.0.0: Production Ready"
    ```

14. **Push tag to remote**:
    ```bash
    git push origin v1.0.0
    ```

15. **🚨 CRITICAL - Create GitHub release** with comprehensive notes from file:
    ```bash
    # Create detailed release notes in a file first
    cat > /tmp/release-notes-v1.0.0.md <<'EOF'
    # Proto Gear v1.0.0 - Production Ready

    **Release Date**: 2025-12-01

    We're excited to announce Proto Gear v1.0.0 - our first production-ready release!

    ## 🎉 Highlights

    [Major achievements and highlights]

    ## 🚀 What's New

    [Comprehensive feature list]

    ## 💥 Breaking Changes

    [List all breaking changes with migration guidance]

    ## 🐛 Bug Fixes

    [Bug fixes since last version]

    ## 📊 Statistics

    [Comprehensive statistics]

    ## 📚 Documentation

    [Documentation updates]

    ## 🙏 Contributors

    [Acknowledge contributors]

    ## 🔗 Resources

    - [Documentation](https://github.com/prototowb/proto-gear/tree/main/docs)
    - [Getting Started Guide](https://github.com/prototowb/proto-gear/blob/main/docs/user/getting-started.md)
    - [Migration Guide](https://github.com/prototowb/proto-gear/blob/main/docs/MIGRATION.md)

    **Full Changelog**: https://github.com/prototowb/proto-gear/compare/v0.9.0...v1.0.0

    🤖 Generated with Claude Code
    EOF

    # Create the release
    gh release create v1.0.0 \
      --title "v1.0.0 - Production Ready 🎉" \
      --notes-file /tmp/release-notes-v1.0.0.md
    ```

16. **Merge `main` back to `development`**:
    ```bash
    git checkout development
    git merge main
    git push origin development
    ```

17. **Update PROJECT_STATUS.md**:
    - Update version to v1.0.0
    - Update project_phase to "Production"
    - Add comprehensive release notes
    - Update all relevant sections

18. **Update readiness assessment** (`docs/dev/readiness-assessment.md`):
    - Mark as v1.0.0 Production Ready
    - Final readiness score
    - Production recommendations
    - Future roadmap

19. **Clean up release branch and RC tags**:
    ```bash
    git branch -d release/v1.0.0
    git push origin --delete release/v1.0.0
    ```

20. **Announce the release**:
    - Social media
    - Blog post
    - Email newsletter (if applicable)
    - Community forums

21. **Verify release**:
    ```bash
    gh release view v1.0.0
    ```

---

## Post-Release Checklist

After **every** release, verify:

- [ ] GitHub release exists and is visible
- [ ] Release notes are comprehensive and clear
- [ ] Tag exists in repository: `git tag | grep v0.X.X`
- [ ] Tag pushed to remote: `git ls-remote --tags origin | grep v0.X.X`
- [ ] PROJECT_STATUS.md updated with new version
- [ ] CHANGELOG.md includes all changes
- [ ] Readiness assessment updated (minor/major releases)
- [ ] `main` and `development` branches are in sync
- [ ] All tests still passing after merge

---

## Emergency: Forgot to Create GitHub Release

If you tagged a release but forgot to create the GitHub release:

1. **Don't panic** - you can create it retroactively

2. **Check what's missing**:
   ```bash
   # List all tags
   git tag

   # List all GitHub releases
   gh release list

   # Find the missing release
   ```

3. **Create the release immediately**:
   ```bash
   gh release create v0.X.X \
     --title "v0.X.X - Title" \
     --notes "Release notes for v0.X.X..."
   ```

4. **Update documentation** to reflect the release was completed

5. **Review workflow** to understand why it was skipped

6. **Update this document** if the workflow was unclear

---

## Release Notes Template

Use this template for minor/major releases:

```markdown
# Proto Gear vX.Y.Z - Title

**Release Date**: YYYY-MM-DD

## 🚀 What's New

### Category 1
- Feature/change 1
- Feature/change 2

### Category 2
- Enhancement 1
- Enhancement 2

## 🐛 Bug Fixes
- Fix 1
- Fix 2

## 📊 Statistics
- Lines Added: X lines
- Test Coverage: Y%
- Tests Added: Z tests

## 📚 Documentation
- New documentation
- Updated guides

## 🔧 Technical Details
[Technical information for developers]

## 💥 Breaking Changes (if any)
- Breaking change 1 with migration guidance
- Breaking change 2 with migration guidance

**Full Changelog**: https://github.com/prototowb/proto-gear/compare/vA.B.C...vX.Y.Z

🤖 Generated with Claude Code
```

---

## Common Issues

### Issue: `gh` command not found

**Solution**: Install GitHub CLI
```bash
# Windows
winget install --id GitHub.cli

# macOS
brew install gh

# Linux
sudo apt install gh  # Debian/Ubuntu
```

### Issue: Not authenticated with GitHub

**Solution**: Authenticate
```bash
gh auth login
# Follow the prompts
```

### Issue: Permission denied when pushing tags

**Solution**: Check remote access
```bash
git remote -v
# Verify you have push access to the repository
```

### Issue: Tag already exists

**Solution**: Either delete and recreate (dangerous) or create a new version
```bash
# Option 1: Delete and recreate (ONLY if not pushed to remote)
git tag -d v0.X.X
git tag -a v0.X.X -m "Release v0.X.X: Description"

# Option 2: Create new version (safer)
git tag -a v0.X.Y -m "Release v0.X.Y: Description"
```

---

## Version Numbering

Proto Gear follows [Semantic Versioning](https://semver.org/):

**MAJOR.MINOR.PATCH** (e.g., 1.2.3)

- **MAJOR**: Incompatible API changes, breaking changes
- **MINOR**: New features, backwards-compatible
- **PATCH**: Bug fixes, backwards-compatible

**Pre-release versions**:
- Alpha: v0.X.Y-alpha.N (early testing)
- Beta: v0.X.Y-beta.N (feature complete, testing)
- RC: v0.X.Y-rc.N (release candidate, final testing)

---

**Last Updated**: 2025-11-21
**Maintained by**: Proto Gear Development Team
