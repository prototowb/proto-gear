# Dogfooding Update Guide

**Purpose**: Guide for updating Proto Gear's own template files when the templates are improved.

## When to Update

Update dogfooding files when:
- ✅ Template structure significantly changes
- ✅ New cross-references are added
- ✅ Critical workflows are updated
- ✅ Major version bumps (e.g., v0.5.0 → v0.7.2)
- ✅ New mandatory sections added

## Current Status (2025-12-07)

### ✅ Templates Updated
All 8 core templates have been updated with:
- Cross-reference networks
- Related documentation sections
- Capability discovery workflows
- Comprehensive file listings

### ⚠️ Dogfooding Files Status

| File | Current | Latest Template | Needs Update |
|------|---------|-----------------|--------------|
| AGENTS.md | v0.5.0 (59 lines) | v0.7.2 (691 lines) | ✅ YES |
| PROJECT_STATUS.md | Custom | Updated template | ⚠️ REVIEW |
| TESTING.md | Nov 22, 2024 | Updated (Dec 7) | ✅ YES |
| BRANCHING.md | Nov 22, 2024 | Updated (Dec 7) | ✅ YES |
| CONTRIBUTING.md | Nov 22, 2024 | Updated (Dec 7) | ✅ YES |
| SECURITY.md | Nov 22, 2024 | Updated (Dec 7) | ✅ YES |
| ARCHITECTURE.md | Nov 22, 2024 | Updated (Dec 7) | ✅ YES |
| CODE_OF_CONDUCT.md | Nov 22, 2024 | Updated (Dec 7) | ✅ YES |

## Safe Update Process

### Method 1: Manual Merge (Recommended)

```bash
# 1. Backup current files
cp AGENTS.md AGENTS.md.backup
cp PROJECT_STATUS.md PROJECT_STATUS.md.backup

# 2. Generate fresh templates in temp directory
mkdir /tmp/proto-gear-update
cd /tmp/proto-gear-update
pg init --with-branching --ticket-prefix PROTO --with-all

# 3. Compare and merge
# For each file, manually merge:
# - Keep custom content (our tickets, sprint info, custom agent configs)
# - Add new structure (cross-references, workflows, updated sections)
# - Update version numbers

# 4. Verify
git diff AGENTS.md  # Review changes
git diff PROJECT_STATUS.md

# 5. Commit
git add AGENTS.md PROJECT_STATUS.md ...
git commit -m "docs: update dogfooding templates to v0.7.2 structure"
```

### Method 2: Automated (Risky - May Lose Custom Content)

```bash
# ⚠️ WARNING: This will overwrite files!
# Only use if you've backed up custom content

# Delete old files
rm AGENTS.md PROJECT_STATUS.md

# Regenerate
pg init --with-branching --ticket-prefix PROTO --no-interactive

# Manually restore custom sections from backups
```

## What to Preserve

When updating, **always preserve**:

### AGENTS.md
- Custom agent configurations
- Project-specific workflows
- Specialized agent patterns
- Custom critical rules

### PROJECT_STATUS.md
- All active tickets
- Completed ticket history
- Sprint history
- Project metrics
- Custom sprint configurations

### Other Templates
- Project-specific examples
- Custom sections added by team
- Local conventions
- Tool-specific configurations

## What to Update

**Always update** to latest template structure:

- ✅ Cross-reference sections ("Related Documentation")
- ✅ Pre-flight checklists
- ✅ Capability discovery workflows
- ✅ Version numbers (v0.5.0 → v0.7.2)
- ✅ New mandatory sections
- ✅ Improved workflows and patterns

## Merge Strategy

### For AGENTS.md

```markdown
# New Template Structure
1. Title and metadata                 ← UPDATE: Version number
2. BEFORE ANY WORK section           ← UPDATE: Add new files (5 new ones)
3. Pre-Flight Checklist              ← UPDATE: New items for capabilities
4. Critical Rules                    ← UPDATE: Add capability check as #1
5. How to Use This Document          ← KEEP AS-IS
6. Universal Capabilities System     ← UPDATE: New 3-step workflow
7. Agent Configuration               ← MERGE: Keep custom, add structure
8. Workflows and patterns            ← MERGE: Keep custom, add improvements
```

### For PROJECT_STATUS.md

```markdown
# New Template Structure
1. Title and commands                ← KEEP: Custom commands
2. Related Documentation             ← ADD: New section with 8 file references
3. State Management Guide            ← UPDATE: Latest workflow
4. Current State                     ← KEEP: Our actual data
5. Active Tickets                    ← KEEP: Our tickets
6. Completed Tickets                 ← KEEP: Our history
7. Metrics                           ← KEEP: Our metrics
```

## Testing After Update

```bash
# 1. Verify files are valid
pg init --dry-run

# 2. Check cross-references work
grep -r "AGENTS.md" *.md  # Should find multiple references
grep -r ".proto-gear/INDEX.md" *.md  # Should find capability refs

# 3. Verify capability discovery
test -f .proto-gear/INDEX.md && echo "✓ Capabilities installed"

# 4. Lint markdown (if you have markdownlint)
markdownlint *.md

# 5. Test with AI agent
# Have an AI agent read AGENTS.md and verify it:
# - Finds all cross-references
# - Discovers capabilities
# - Follows workflows correctly
```

## Current Improvements (Dec 7, 2025)

### Added to All Templates

**Cross-Reference Network**:
- Every template now has "📚 Related Documentation" section
- Lists all 8 possible templates with descriptions
- Marks required vs optional files
- Creates documentation graph for easy navigation

**Capability Integration**:
- AGENTS.md: 3-step capability discovery workflow
- AGENTS.md: Capability check as Critical Rule #1
- AGENTS.md: Pre-flight checklist item #1 for capabilities
- All templates reference `.proto-gear/INDEX.md` when relevant

**File Coverage**:
- Added TESTING.md to pre-work reading (was missing)
- Added CONTRIBUTING.md references (was missing)
- Added SECURITY.md references (was missing)
- Added ARCHITECTURE.md references (was missing)
- Added CODE_OF_CONDUCT.md references (was missing)

### Template Line Counts

| Template | Old Lines | New Lines | Change |
|----------|-----------|-----------|---------|
| AGENTS.md | ~400 | 691 | +291 (+73%) |
| PROJECT_STATUS.md | ~90 | ~120 | +30 (+33%) |
| TESTING.md | ~280 | ~310 | +30 (+11%) |
| BRANCHING.md | ~180 | ~200 | +20 (+11%) |
| CONTRIBUTING.md | ~230 | ~250 | +20 (+9%) |
| SECURITY.md | ~150 | ~165 | +15 (+10%) |
| ARCHITECTURE.md | ~200 | ~215 | +15 (+8%) |
| CODE_OF_CONDUCT.md | ~180 | ~190 | +10 (+6%) |

## Next Steps

1. **Immediate**: Review this guide
2. **Soon**: Update AGENTS.md to v0.7.2 structure (biggest change)
3. **Following**: Update other templates with cross-references
4. **Ongoing**: Test with AI agents to verify improvements work
5. **Future**: Automate template synchronization detection

---

*Last Updated: 2025-12-07*
*Template Version: v0.7.2*
