# Proto Gear Project Structure

**Version**: 1.0
**Date**: 2025-11-04
**Purpose**: Define clear separation between development files and package distribution files

---

## Overview

This document establishes a clear organizational structure for Proto Gear development, separating:
1. **Package files** - Distributed to users via `pip install proto-gear`
2. **Development files** - Used only for developing Proto Gear itself
3. **Generated files** - Created by build/test processes
4. **Documentation files** - User-facing vs. contributor-facing

---

## Directory Structure

```
proto-gear/
├── core/                           # PACKAGE: Main package (distributed)
│   ├── __init__.py                 # Package initialization
│   ├── proto_gear.py               # Main CLI entry point
│   ├── ui_helper.py                # UI/UX utilities
│   ├── interactive_wizard.py       # Interactive setup wizard
│   ├── AGENTS.template.md          # Agent configuration template
│   ├── PROJECT_STATUS.template.md  # Status tracking template
│   ├── BRANCHING.template.md       # Git workflow template
│   ├── TESTING.template.md         # TDD methodology template
│   └── agent-framework.config.yaml # Default configuration
│
├── tests/                          # DEVELOPMENT: Test suite
│   ├── unit/                       # Unit tests
│   ├── integration/                # Integration tests
│   └── fixtures/                   # Test fixtures
│
├── docs/                           # DOCUMENTATION: Split into user/dev
│   ├── user/                       # USER DOCS: End-user documentation
│   │   ├── getting-started.md
│   │   ├── template-guide.md
│   │   └── guides/
│   │       ├── 01-template-basics.md
│   │       ├── 02-ai-agent-usage.md
│   │       ├── 03-human-usage.md
│   │       ├── 04-workflow-examples.md
│   │       └── 05-troubleshooting.md
│   │
│   └── dev/                        # DEV DOCS: Contributor documentation
│       ├── branching-strategy.md
│       ├── configuration.md
│       ├── readiness-assessment.md
│       ├── universal-capabilities-design.md
│       └── project-structure.md (this file)
│
├── dev/                            # DEVELOPMENT: Development tools/files
│   ├── analysis/                   # Code analysis reports (archived)
│   │   ├── code-analysis-report.md
│   │   ├── dead-code-analysis.md
│   │   └── refactoring-plan.md
│   │
│   ├── scripts/                    # Development scripts
│   │   ├── build.sh
│   │   ├── test.sh
│   │   └── release.sh
│   │
│   └── workflows/                  # GitHub Actions workflows (symlink to .github/workflows)
│
├── examples/                       # EXAMPLES: Sample projects
│   ├── nodejs-example/
│   ├── python-example/
│   └── mixed-stack-example/
│
├── .github/                        # GITHUB: GitHub-specific files
│   ├── workflows/                  # CI/CD workflows
│   ├── ISSUE_TEMPLATE/
│   └── PULL_REQUEST_TEMPLATE.md
│
├── .claude/                        # DEVELOPMENT: Claude Code settings
│   └── commands/
│
├── scripts/                        # PACKAGE: Installation scripts (distributed)
│   └── post-install.sh             # Post-installation setup
│
├── CLAUDE.md                       # DEVELOPMENT: AI agent instructions for development
├── CONTRIBUTING.md                 # DEVELOPMENT: Contributor guide
├── README.md                       # PACKAGE: User-facing README
├── LICENSE                         # PACKAGE: License file
├── setup.py                        # PACKAGE: Package configuration
├── requirements.txt                # DEVELOPMENT: Dev dependencies
├── pytest.ini                      # DEVELOPMENT: Test configuration
├── .gitignore                      # DEVELOPMENT: Git ignore rules
│
└── [GENERATED FILES]               # Build artifacts (gitignored)
    ├── .coverage                   # Test coverage data
    ├── __pycache__/                # Python cache
    ├── .pytest_cache/              # Pytest cache
    ├── dist/                       # Build distributions
    ├── build/                      # Build artifacts
    └── *.egg-info/                 # Package metadata
```

---

## File Categories

### 1. PACKAGE Files (Distributed to Users)

**Location**: Included in `pip install proto-gear`

```
core/
├── __init__.py
├── proto_gear.py
├── ui_helper.py
├── interactive_wizard.py
├── AGENTS.template.md
├── PROJECT_STATUS.template.md
├── BRANCHING.template.md
├── TESTING.template.md
└── agent-framework.config.yaml

scripts/
└── post-install.sh (if needed)

README.md
LICENSE
setup.py
```

**Criteria**:
- Required for Proto Gear to function
- Users need these files after installation
- Templates, core modules, CLI entry points

### 2. DEVELOPMENT Files (Contributors Only)

**Location**: Only in git repository, not distributed

```
tests/                  # Test suite
dev/                    # Development tools and archives
.github/                # GitHub workflows
.claude/                # Claude Code settings
CLAUDE.md               # AI agent development instructions
CONTRIBUTING.md         # Contributor guide
requirements.txt        # Dev dependencies
pytest.ini              # Test configuration
.gitignore              # Git ignore rules
```

**Criteria**:
- Used for developing Proto Gear itself
- Not needed by end users
- CI/CD, testing, analysis tools

### 3. DOCUMENTATION Files

#### User Documentation (Public)
```
docs/user/
├── getting-started.md
├── template-guide.md
└── guides/
    ├── 01-template-basics.md
    ├── 02-ai-agent-usage.md
    ├── 03-human-usage.md
    ├── 04-workflow-examples.md
    └── 05-troubleshooting.md
```

**Criteria**:
- End-user facing
- How to use Proto Gear
- May be hosted on docs site

#### Developer Documentation (Contributors)
```
docs/dev/
├── branching-strategy.md
├── configuration.md
├── readiness-assessment.md
├── universal-capabilities-design.md
└── project-structure.md
```

**Criteria**:
- Contributor facing
- How to develop Proto Gear
- Design documents, architecture

### 4. GENERATED Files (Ignored)

**Location**: Created by build/test, never committed

```
.coverage               # Test coverage
__pycache__/            # Python bytecode
.pytest_cache/          # Pytest cache
dist/                   # Build distributions
build/                  # Build artifacts
*.egg-info/             # Package metadata
```

**Criteria**:
- Generated during development
- Listed in `.gitignore`
- Recreated by build/test commands

---

## Reorganization Plan

### Step 1: Create New Structure

```bash
# Create new directories
mkdir -p dev/analysis
mkdir -p dev/scripts
mkdir -p docs/user
mkdir -p docs/dev
```

### Step 2: Move Files

**Move analysis files** (root → dev/analysis):
```bash
mv CODE_ANALYSIS_REPORT.md dev/analysis/
mv DEAD_CODE_ANALYSIS.md dev/analysis/
mv REFACTORING_PLAN.md dev/analysis/
```

**Move user docs** (docs → docs/user):
```bash
mv docs/getting-started.md docs/user/
mv docs/TEMPLATE_GUIDE.md docs/user/template-guide.md
mv docs/guides docs/user/
```

**Move developer docs** (docs → docs/dev):
```bash
mv docs/BRANCHING_STRATEGY.md docs/dev/branching-strategy.md
mv docs/CONFIGURATION.md docs/dev/configuration.md
mv docs/READINESS_ASSESSMENT.md docs/dev/readiness-assessment.md
mv docs/UNIVERSAL_CAPABILITIES_DESIGN.md docs/dev/universal-capabilities-design.md
cp docs/PROJECT_STRUCTURE.md docs/dev/project-structure.md
```

**Move development scripts**:
```bash
# If any exist in scripts/ that are dev-only
# Keep scripts/ for package distribution scripts
```

### Step 3: Update .gitignore

Ensure these patterns exist:
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Testing
.pytest_cache/
.coverage
.coverage.*
htmlcov/
.tox/
.nox/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Proto Gear specific
core/.coverage
```

### Step 4: Update References

Update file paths in:
- `CLAUDE.md` - Point to new doc locations
- `README.md` - Update documentation links
- `CONTRIBUTING.md` - Update file references

---

## Dogfooding Workflow

### Using Proto Gear to Develop Itself

Since Proto Gear is installed in editable mode (`pip install -e .`), we can use it on itself:

```bash
# 1. Navigate to proto-gear directory
cd G:/Projects/proto-gear

# 2. Initialize Proto Gear templates in the project itself
pg init --with-branching --ticket-prefix PROTO

# This creates:
# - AGENTS.md (AI agent coordination for Proto Gear development)
# - PROJECT_STATUS.md (Track PROTO tickets and sprints)
# - BRANCHING.md (Git workflow for contributors)
# - TESTING.md (TDD patterns for developing Proto Gear)
```

**Benefits**:
1. **Test in real time** - See changes immediately
2. **Self-documenting** - Use templates we tell others to use
3. **Catch issues early** - Experience user workflow firsthand
4. **Better design** - Feel pain points ourselves

### Development Workflow with Dogfooding

```bash
# 1. Make changes to core/proto_gear.py
vim core/proto_gear.py

# 2. Test changes immediately (editable install)
pg init --dry-run

# 3. Run tests
pytest

# 4. Use Proto Gear templates for tracking work
# - Create ticket in PROJECT_STATUS.md
# - Follow BRANCHING.md conventions
# - Apply TESTING.md TDD patterns
# - Coordinate via AGENTS.md

# 5. Update package version when shipping
vim setup.py  # Bump version

# 6. Reinstall to test fresh install
pip install -e .
```

---

## Package Distribution

### What Gets Distributed

When users run `pip install proto-gear`, they get:

```
site-packages/
└── proto_gear/
    ├── __init__.py
    ├── proto_gear.py
    ├── ui_helper.py
    ├── interactive_wizard.py
    ├── AGENTS.template.md
    ├── PROJECT_STATUS.template.md
    ├── BRANCHING.template.md
    ├── TESTING.template.md
    └── agent-framework.config.yaml
```

### What's Excluded

Not distributed to users:
- Tests (`tests/`)
- Development files (`dev/`)
- Analysis reports (`dev/analysis/`)
- CI/CD configs (`.github/`)
- IDE settings (`.claude/`, `.vscode/`)
- Development docs (`docs/dev/`)

Controlled by `setup.py` `packages` and `package_data` directives.

---

## Setup.py Configuration

Current distribution setup:

```python
setup(
    name='proto-gear',
    version='0.3.0',
    packages=['core'],
    package_data={
        'core': [
            '*.md',
            '*.yaml',
            '*.yml'
        ]
    },
    entry_points={
        'console_scripts': [
            'pg=core.proto_gear:main',
            'proto-gear=core.proto_gear:main',
            'protogear=core.proto_gear:main',
            'agent-framework=core.proto_gear:main'
        ]
    }
)
```

Only `core/` package and its data files are distributed.

---

## Best Practices

### For Package Files
- ✅ Keep minimal - only what users need
- ✅ Well-documented - docstrings, type hints
- ✅ Tested thoroughly - high coverage
- ✅ Stable APIs - avoid breaking changes

### For Development Files
- ✅ Organize by purpose (analysis, scripts, docs)
- ✅ Archive old analysis (don't delete)
- ✅ Keep development docs up-to-date
- ✅ Document development workflows

### For Documentation
- ✅ Split user/developer docs clearly
- ✅ User docs: How to use Proto Gear
- ✅ Dev docs: How to contribute to Proto Gear
- ✅ Keep examples up-to-date

### For Dogfooding
- ✅ Use Proto Gear templates on Proto Gear itself
- ✅ Follow our own branching/commit conventions
- ✅ Track work in PROJECT_STATUS.md
- ✅ Practice TDD from TESTING.md

---

## Maintenance Checklist

### Before Each Release
- [ ] Update version in `setup.py`
- [ ] Run full test suite: `pytest`
- [ ] Test fresh install: `pip install -e .`
- [ ] Test `pg init` in sample project
- [ ] Update README.md with changes
- [ ] Update CHANGELOG.md (if exists)
- [ ] Archive old analysis to `dev/analysis/`
- [ ] Clean up generated files
- [ ] Update documentation if needed

### Regular Maintenance
- [ ] Review and archive old analysis files monthly
- [ ] Update READINESS_ASSESSMENT.md after major changes
- [ ] Keep CLAUDE.md in sync with project structure
- [ ] Update examples when templates change
- [ ] Review .gitignore for new patterns

---

## File Movement Summary

**TO CREATE**:
```
dev/
dev/analysis/
docs/user/
docs/dev/
```

**TO MOVE**:
```
CODE_ANALYSIS_REPORT.md → dev/analysis/code-analysis-report.md
DEAD_CODE_ANALYSIS.md → dev/analysis/dead-code-analysis.md
REFACTORING_PLAN.md → dev/analysis/refactoring-plan.md
docs/getting-started.md → docs/user/getting-started.md
docs/TEMPLATE_GUIDE.md → docs/user/template-guide.md
docs/guides/ → docs/user/guides/
docs/BRANCHING_STRATEGY.md → docs/dev/branching-strategy.md
docs/CONFIGURATION.md → docs/dev/configuration.md
docs/READINESS_ASSESSMENT.md → docs/dev/readiness-assessment.md
docs/UNIVERSAL_CAPABILITIES_DESIGN.md → docs/dev/universal-capabilities-design.md
```

**TO UPDATE**:
```
CLAUDE.md (update file paths)
README.md (update doc links)
CONTRIBUTING.md (update references)
.gitignore (verify patterns)
```

---

## Next Steps

1. **Execute reorganization** - Move files as outlined
2. **Initialize dogfooding** - Run `pg init` on proto-gear itself
3. **Update references** - Fix broken links
4. **Test package** - Ensure distribution still works
5. **Document in CONTRIBUTING.md** - Explain structure to contributors

---

*Proto Gear Project Structure v1.0*
*Established: 2025-11-04*
