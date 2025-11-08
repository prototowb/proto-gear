# Git Worktrees Workflow - Visual Guide

**Proto Gear v0.5.0 Parallel Development**

---

## Directory Structure

```
G:\Projects\
│
├── proto-gear\                                    # Main Repository
│   ├── .git\                                      # ← Shared by ALL worktrees
│   │   ├── worktrees\                             # Worktree metadata
│   │   │   ├── v0.5.0-templates\
│   │   │   ├── v0.5.0-skills\
│   │   │   └── v0.5.0-workflows\
│   │   └── ...
│   ├── core\
│   ├── docs\
│   ├── tests\
│   └── ...
│
└── proto-gear-worktrees\                          # Worktrees Directory
    │
    ├── v0.5.0-templates\                          # Worktree 1: Templates
    │   ├── .git                                   # ← Link to main .git
    │   ├── core\
    │   │   ├── CONTRIBUTING.template.md          # ← New file
    │   │   ├── SECURITY.template.md              # ← New file
    │   │   ├── ARCHITECTURE.template.md          # ← New file
    │   │   └── proto_gear.py                     # ← Modified
    │   ├── docs\
    │   │   └── user\
    │   │       └── template-guide.md             # ← Updated
    │   ├── tests\
    │   │   └── test_templates.py                 # ← New tests
    │   └── WORKSTREAM.md                          # ← Workstream notes
    │
    ├── v0.5.0-skills\                             # Worktree 2: Skills
    │   ├── .git                                   # ← Link to main .git
    │   ├── core\
    │   │   ├── skills\                            # ← New directory
    │   │   │   ├── debugging.skill.md
    │   │   │   ├── code-review.skill.md
    │   │   │   └── refactoring.skill.md
    │   │   └── proto_gear.py                     # ← Modified
    │   ├── docs\
    │   │   └── user\
    │   │       └── skills-guide.md               # ← New doc
    │   ├── tests\
    │   │   └── test_skills.py                    # ← New tests
    │   └── WORKSTREAM.md
    │
    └── v0.5.0-workflows\                          # Worktree 3: Workflows
        ├── .git                                   # ← Link to main .git
        ├── core\
        │   ├── workflows\                         # ← New directory
        │   │   ├── bug-fix.workflow.md
        │   │   ├── hotfix.workflow.md
        │   │   └── release.workflow.md
        │   └── proto_gear.py                     # ← Modified
        ├── docs\
        │   └── user\
        │       └── workflows-guide.md            # ← New doc
        ├── tests\
        │   └── test_workflows.py                 # ← New tests
        └── WORKSTREAM.md
```

---

## Branch Timeline

```
main
  │
  └── development ────────────────────────────────────────────────────┐
        │                                                               │
        ├── feature/v0.5.0-templates-core                             │
        │     │                                                         │
        │     ├── commit: Initialize templates workstream             │
        │     ├── commit: Add CONTRIBUTING template                   │
        │     ├── commit: Add SECURITY template                       │
        │     ├── commit: Add ARCHITECTURE template                   │
        │     ├── commit: Update template loader                      │
        │     └── commit: Add tests                                   │
        │                                                               │
        ├── feature/v0.5.0-skills-system                              │
        │     │                                                         │
        │     ├── commit: Initialize skills workstream               │
        │     ├── commit: Create skills directory                    │
        │     ├── commit: Implement debugging skill                  │
        │     ├── commit: Implement code-review skill                │
        │     ├── commit: Implement refactoring skill                │
        │     └── commit: Add tests                                   │
        │                                                               │
        └── feature/v0.5.0-workflows-engine                           │
              │                                                         │
              ├── commit: Initialize workflows workstream            │
              ├── commit: Create workflows directory                 │
              ├── commit: Implement bug-fix workflow                 │
              ├── commit: Implement hotfix workflow                  │
              ├── commit: Implement release workflow                 │
              └── commit: Add tests                                   │
                                                                        │
PARALLEL DEVELOPMENT ──────────────────────────────────────────────────┘
(All 3 workstreams work simultaneously)

INTEGRATION ───────────────────────────────────────────────────────────┐
                                                                        │
development                                                             │
  │                                                                     │
  ├── merge: feature/v0.5.0-templates-core  ← MERGE 1                 │
  │     │                                                               │
  │     └── Tests pass ✓                                               │
  │                                                                     │
  ├── merge: feature/v0.5.0-skills-system   ← MERGE 2                 │
  │     │                                                               │
  │     └── Tests pass ✓                                               │
  │                                                                     │
  └── merge: feature/v0.5.0-workflows-engine ← MERGE 3                │
        │                                                               │
        └── Tests pass ✓                                               │
                                                                        │
SEQUENTIAL INTEGRATION ────────────────────────────────────────────────┘

RELEASE ───────────────────────────────────────────────────────────────┐
                                                                        │
development                                                             │
  │                                                                     │
  ├── tag: v0.5.0                                                      │
  │                                                                     │
  └── merge to main ──────────────────────────────────────────────────┤
                                                                        │
main                                                                    │
  │                                                                     │
  └── v0.5.0 (production ready)                                        │
                                                                        │
RELEASE COMPLETE ──────────────────────────────────────────────────────┘
```

---

## Workflow States

### State 1: Initial Setup

```
┌─────────────────────────────────────────────────────────────────┐
│ Main Repository (G:\Projects\proto-gear)                        │
│                                                                  │
│ Branch: development                                              │
│ Commit: d0d8184                                                  │
│ Status: Clean                                                    │
│                                                                  │
│ [No worktrees yet]                                               │
└─────────────────────────────────────────────────────────────────┘

ACTION: Create worktrees
↓
```

### State 2: Worktrees Created

```
┌─────────────────────────────────────────────────────────────────┐
│ Main Repository                                                  │
│ Branch: development                                              │
└─────────────────────────────────────────────────────────────────┘
         │
         ├──────────────┬──────────────┬──────────────┐
         │              │              │              │
         ▼              ▼              ▼              ▼
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│ Templates  │  │   Skills   │  │  Workflows │  │ Main Repo  │
│ Worktree   │  │  Worktree  │  │  Worktree  │  │ (dev)      │
│            │  │            │  │            │  │            │
│ Branch:    │  │ Branch:    │  │ Branch:    │  │ Branch:    │
│ templates  │  │ skills     │  │ workflows  │  │ development│
│ -core      │  │ -system    │  │ -engine    │  │            │
└────────────┘  └────────────┘  └────────────┘  └────────────┘

ACTION: Work in parallel
↓
```

### State 3: Parallel Development

```
┌────────────────────────────────────────────────────────────────┐
│                    PARALLEL WORK PHASE                          │
└────────────────────────────────────────────────────────────────┘

Worktree 1: Templates          Worktree 2: Skills          Worktree 3: Workflows
┌─────────────────────┐       ┌─────────────────────┐       ┌─────────────────────┐
│ Developer A or      │       │ Developer B or      │       │ Developer C or      │
│ AI Agent 1          │       │ AI Agent 2          │       │ AI Agent 3          │
│                     │       │                     │       │                     │
│ • Add templates     │       │ • Create skills     │       │ • Build workflows   │
│ • Write tests       │       │ • Write tests       │       │ • Write tests       │
│ • Update docs       │       │ • Update docs       │       │ • Update docs       │
│                     │       │                     │       │                     │
│ Commits: 15         │       │ Commits: 12         │       │ Commits: 10         │
│ Status: Active      │       │ Status: Active      │       │ Status: Active      │
└─────────────────────┘       └─────────────────────┘       └─────────────────────┘
         │                             │                             │
         │                             │                             │
         └─────────────────────────────┴─────────────────────────────┘
                                       │
                                       ▼
                        [All commit to their branches]
                        [No interference with each other]

ACTION: Complete work, test thoroughly
↓
```

### State 4: Ready for Integration

```
┌────────────────────────────────────────────────────────────────┐
│                    READY FOR MERGE                              │
└────────────────────────────────────────────────────────────────┘

development branch                    Feature Branches
┌─────────────────────┐              ┌─────────────────────┐
│                     │              │ templates-core      │
│ Latest stable code  │              │ ✓ Tests pass        │
│                     │              │ ✓ Coverage 75%      │
│                     │              │ ✓ Lint clean        │
│                     │              │ ✓ Docs updated      │
│                     │              └─────────────────────┘
│                     │              ┌─────────────────────┐
│                     │              │ skills-system       │
│                     │              │ ✓ Tests pass        │
│                     │              │ ✓ Coverage 72%      │
│                     │              │ ✓ Lint clean        │
│                     │              │ ✓ Docs updated      │
│                     │              └─────────────────────┘
│                     │              ┌─────────────────────┐
│                     │              │ workflows-engine    │
│                     │              │ ✓ Tests pass        │
│                     │              │ ✓ Coverage 71%      │
│                     │              │ ✓ Lint clean        │
│                     │              │ ✓ Docs updated      │
└─────────────────────┘              └─────────────────────┘

ACTION: Merge sequentially
↓
```

### State 5: Sequential Integration

```
┌────────────────────────────────────────────────────────────────┐
│                    INTEGRATION PHASE                            │
└────────────────────────────────────────────────────────────────┘

Step 1: Merge Templates
─────────────────────────
development
  │
  ├─ merge templates-core ──> [Run tests] ──> ✓ PASS
  │
  └─ development (with Templates)

Step 2: Merge Skills
─────────────────────────
development (with Templates)
  │
  ├─ merge skills-system ──> [Run tests] ──> ✓ PASS
  │
  └─ development (with Templates + Skills)

Step 3: Merge Workflows
─────────────────────────
development (with Templates + Skills)
  │
  ├─ merge workflows-engine ──> [Run tests] ──> ✓ PASS
  │
  └─ development (with Templates + Skills + Workflows)

ACTION: Tag and release
↓
```

### State 6: Release

```
┌────────────────────────────────────────────────────────────────┐
│                    RELEASE v0.5.0                               │
└────────────────────────────────────────────────────────────────┘

development (all features integrated)
  │
  ├─ Create tag: v0.5.0
  │
  └─ Merge to main
       │
       └─ main (v0.5.0 released)

Worktrees:
  ├─ Remove templates worktree
  ├─ Remove skills worktree
  └─ Remove workflows worktree

Branches (optional cleanup):
  ├─ Delete templates-core
  ├─ Delete skills-system
  └─ Delete workflows-engine

FINAL STATE:
┌─────────────────────────────────────────────────────────────────┐
│ Main Repository                                                  │
│ Branches: main, development                                      │
│ Worktrees: None                                                  │
│ Version: v0.5.0                                                  │
│ Status: Ready for distribution                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Modification Heat Map

Shows which files each workstream modifies (red = high risk of conflict):

```
File/Directory                    │ Templates │ Skills │ Workflows │ Conflict Risk
──────────────────────────────────┼───────────┼────────┼───────────┼──────────────
core/proto_gear.py                │    🔴     │  🔴    │    🔴     │   VERY HIGH
core/*.template.md (new)          │    🟢     │  ⚪    │    ⚪     │   VERY LOW
core/skills/ (new)                │    ⚪     │  🟢    │    ⚪     │   VERY LOW
core/workflows/ (new)             │    ⚪     │  ⚪    │    🟢     │   VERY LOW
docs/user/getting-started.md      │    🟡     │  🟡    │    🟡     │   MEDIUM
docs/user/template-guide.md       │    🟢     │  ⚪    │    ⚪     │   VERY LOW
docs/user/skills-guide.md (new)   │    ⚪     │  🟢    │    ⚪     │   VERY LOW
docs/user/workflows-guide.md (new)│    ⚪     │  ⚪    │    🟢     │   VERY LOW
tests/test_templates.py           │    🟢     │  ⚪    │    ⚪     │   LOW
tests/test_skills.py (new)        │    ⚪     │  🟢    │    ⚪     │   VERY LOW
tests/test_workflows.py (new)     │    ⚪     │  ⚪    │    🟢     │   VERY LOW
pyproject.toml                    │    🟡     │  🟡    │    🟡     │   MEDIUM
README.md                         │    🟡     │  🟡    │    🟡     │   MEDIUM

Legend:
🟢 = Primary modification (this workstream owns it)
🟡 = Minor modification (updates documentation/config)
🔴 = Heavy modification (high conflict risk)
⚪ = No modification
```

**Conflict Mitigation Strategy**:
1. **Red files** (`proto_gear.py`): Use section markers, coordinate changes
2. **Yellow files**: Merge sequentially, review carefully
3. **Green files**: No conflicts expected
4. **White files**: Not touched by workstream

---

## Testing Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TESTING WORKFLOW                              │
└─────────────────────────────────────────────────────────────────┘

Each Worktree (Before Merge)
────────────────────────────
┌──────────────────┐
│ Write Code       │
│      ↓           │
│ Write Tests      │
│      ↓           │
│ Run Tests        │ ──→ FAIL? ──→ Fix code ──┐
│      ↓           │                           │
│     PASS         │ ←─────────────────────────┘
│      ↓           │
│ Check Coverage   │ ──→ < 70%? ──→ Add tests ─┐
│      ↓           │                            │
│    >= 70%        │ ←──────────────────────────┘
│      ↓           │
│ Run Linter       │ ──→ Errors? ──→ Fix lint ──┐
│      ↓           │                             │
│   No errors      │ ←───────────────────────────┘
│      ↓           │
│ Test CLI         │ ──→ Broken? ──→ Fix CLI ───┐
│      ↓           │                             │
│   Working        │ ←───────────────────────────┘
│      ↓           │
│ READY TO MERGE   │
└──────────────────┘

After Each Merge (Integration Testing)
──────────────────────────────────────
┌──────────────────┐
│ Merge Complete   │
│      ↓           │
│ Run Full Suite   │ ──→ FAIL? ──→ Fix issues ──┐
│      ↓           │                             │
│     PASS         │ ←───────────────────────────┘
│      ↓           │
│ Test Integration │ ──→ Broken? ──→ Fix ────────┐
│      ↓           │                              │
│   Working        │ ←────────────────────────────┘
│      ↓           │
│ Push to Remote   │
└──────────────────┘

Final Release Testing
─────────────────────
┌──────────────────┐
│ All Merged       │
│      ↓           │
│ Full Test Suite  │
│      ↓           │
│ Integration Test │
│      ↓           │
│ Performance Test │
│      ↓           │
│ User Acceptance  │
│      ↓           │
│ TAG & RELEASE    │
└──────────────────┘
```

---

## Conflict Resolution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONFLICT RESOLUTION                           │
└─────────────────────────────────────────────────────────────────┘

Scenario: Merging Skills after Templates
────────────────────────────────────────

development (with Templates merged)
  │
  └─ git merge feature/v0.5.0-skills-system
       │
       ├─ No conflicts ──────────────────────────┐
       │                                          │
       └─ CONFLICT in core/proto_gear.py ────┐   │
                                              │   │
                                              ▼   ▼
                                        ┌──────────────┐
                                        │ Git shows:   │
                                        │              │
                                        │ <<<<<<< HEAD │
                                        │ (Templates)  │
                                        │ =======      │
                                        │ (Skills)     │
                                        │ >>>>>>> ...  │
                                        └──────────────┘
                                              │
                                              ▼
                                        ┌──────────────┐
                                        │ Resolution:  │
                                        │              │
                                        │ Keep both!   │
                                        │              │
                                        │ # Templates  │
                                        │ def load()   │
                                        │              │
                                        │ # Skills     │
                                        │ def exec()   │
                                        └──────────────┘
                                              │
                                              ▼
                                        git add proto_gear.py
                                        git merge --continue
                                              │
                                              ▼
                                        Run tests
                                              │
                                              ▼
                                        ┌──────────────┐
                                        │ Tests pass?  │
                                        └──────────────┘
                                          │          │
                                    YES   │          │ NO
                                          ▼          ▼
                                    ┌─────────┐  ┌─────────┐
                                    │ Push to │  │ Fix and │
                                    │ remote  │  │ re-test │
                                    └─────────┘  └─────────┘
```

---

## Resource Management

```
┌─────────────────────────────────────────────────────────────────┐
│                    DISK SPACE USAGE                              │
└─────────────────────────────────────────────────────────────────┘

Main Repository
├── .git/                     ~50 MB  (shared)
├── core/                     ~5 MB
├── docs/                     ~10 MB
├── tests/                    ~3 MB
├── examples/                 ~2 MB
└── [other files]             ~2 MB
                              --------
Total:                        ~72 MB

Each Worktree (approximate)
├── core/                     ~5 MB   (physical copy)
├── docs/                     ~10 MB  (physical copy)
├── tests/                    ~3 MB   (physical copy)
├── examples/                 ~2 MB   (physical copy)
├── [other files]             ~2 MB   (physical copy)
└── .git                      <1 MB   (link to main .git)
                              --------
Total per worktree:           ~22 MB

Total Space for v0.5.0 Development:
────────────────────────────────────
Main repo:                    72 MB
Templates worktree:           22 MB
Skills worktree:              22 MB
Workflows worktree:           22 MB
                              --------
TOTAL:                        ~138 MB

After cleanup (worktrees removed):
───────────────────────────────────
Main repo only:               72 MB
Space saved:                  66 MB
```

---

## Timeline Estimate

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEVELOPMENT TIMELINE                          │
└─────────────────────────────────────────────────────────────────┘

Week 1: Setup & Templates
─────────────────────────
Day 1:  Setup worktrees, initial commits
Day 2:  Templates: CONTRIBUTING, SECURITY
Day 3:  Templates: ARCHITECTURE, CODE_OF_CONDUCT
Day 4:  Templates: API, DEPLOYMENT (optional)
Day 5:  Templates: Tests and documentation
Day 6:  Templates: Testing and refinement
Day 7:  Templates: MERGE to development ✓

Week 2: Skills Development
─────────────────────────
Day 8:  Skills: Directory structure, debugging skill
Day 9:  Skills: code-review skill
Day 10: Skills: refactoring skill
Day 11: Skills: performance skill (optional)
Day 12: Skills: Tests and documentation
Day 13: Skills: Testing and refinement
Day 14: Skills: MERGE to development ✓

Week 3: Workflows Development
─────────────────────────────
Day 15: Workflows: Directory structure, bug-fix workflow
Day 16: Workflows: hotfix workflow
Day 17: Workflows: release workflow
Day 18: Workflows: Tests and documentation
Day 19: Workflows: Testing and refinement
Day 20: Workflows: MERGE to development ✓
Day 21: Final integration testing

Week 4: Release
───────────────
Day 22: Full test suite, integration tests
Day 23: Documentation review
Day 24: User acceptance testing
Day 25: Bug fixes
Day 26: Release preparation
Day 27: Tag v0.5.0
Day 28: Release announcement

Total: 4 weeks (28 days)

Parallel work saves ~2 weeks compared to sequential!
```

---

**For complete workflow details, see**: `git-worktrees-workflow.md`
