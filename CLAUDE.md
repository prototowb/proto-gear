# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Proto Gear is a Python-based template generator that creates collaboration environments for human and AI agents working together via natural language. It generates structured templates (AGENTS.md, PROJECT_STATUS.md, BRANCHING.md, TESTING.md) that provide workflow patterns, sprint management, and development conventions - completely tech stack agnostic and designed to work with any programming language or framework.

## Project Structure

**IMPORTANT**: We maintain a clear separation between package files (distributed to users) and development files (contributors only).

### Directory Organization
- **`core/`** - PACKAGE: Main package (distributed via pip)
- **`tests/`** - DEVELOPMENT: Test suite
- **`docs/user/`** - DOCUMENTATION: End-user guides and tutorials
- **`docs/dev/`** - DOCUMENTATION: Contributor and design documents
- **`dev/analysis/`** - DEVELOPMENT: Archived code analysis and reports
- **`dev/scripts/`** - DEVELOPMENT: Development automation scripts
- **`examples/`** - EXAMPLES: Sample projects showing Proto Gear usage
- **`.github/`** - GITHUB: CI/CD workflows and templates
- **`.claude/`** - DEVELOPMENT: Claude Code configuration

**Complete Structure**: See `docs/dev/project-structure.md` for detailed breakdown

## Development Commands

### Core Development
- **Install (development)**: `pip install -e .`
- **Build**: `python setup.py build`
- **Test**: `python -m pytest`
- **Lint**: `python -m flake8 core/`
- **Coverage**: `python -m pytest --cov=core --cov-report=term-missing`

### Main Commands
- **Primary command**: `pg init` - Initialize AI agent templates in current project
- **Help command**: `pg help` - Show detailed documentation
- **Dry run testing**: `pg init --dry-run`
- **Direct Python execution**: `cd core && python proto_gear.py init --dry-run`

### Testing Specific Scenarios
```bash
# Test Template Generation
pg init --dry-run

# Test with all options
pg init --dry-run --with-branching --ticket-prefix TEST

# Run test suite with coverage
python -m pytest --cov=core --cov-report=term-missing
```

### Dogfooding Workflow

**IMPORTANT**: We use Proto Gear to develop Proto Gear itself!

Since Proto Gear is installed in editable mode (`pip install -e .`), we can use it on our own project:

#### Initial Setup (Already Done)
```bash
# Initialize Proto Gear templates in this project
pg init --with-branching --ticket-prefix PROTO

# This creates (if they don't exist):
# - AGENTS.md (AI agent coordination for Proto Gear development)
# - PROJECT_STATUS.md (Track PROTO-XXX tickets and sprints)
# - BRANCHING.md (Git workflow for contributors)
```

#### Using Interactive Mode
```bash
# Launch interactive wizard (beautiful UI with arrow key navigation)
pg init

# On Windows, if interactive fails with encoding error, use:
pg init --no-interactive --with-branching --ticket-prefix PROTO
```

**Interactive Features**:
- ✨ Arrow key navigation (↑↓ to select)
- 🎨 Rich formatted panels and tables
- ✅ Real-time input validation
- 🎯 Smart defaults based on project detection
- 🔄 Graceful fallback if rich/questionary unavailable

#### Agent Workflow: Keeping Dogfooding Updated

**When to Update Templates** (AI Agents should do this):
1. **After template changes** - If you modify `*.template.md` files
2. **When PROJECT_STATUS.md gets stale** - Templates might have new fields
3. **When starting a new sprint** - Ensure current format
4. **After major refactoring** - Templates might have improved

**How to Update**:
```bash
# Option 1: Regenerate (will show diff if files exist)
pg init --with-branching --ticket-prefix PROTO

# Option 2: Manual sync
# - Compare core/*.template.md with root AGENTS.md, etc.
# - Manually update sections that improved
# - Keep custom content (our tickets, status, etc.)
```

**Agent Checklist for Template Updates**:
1. Check if `core/*.template.md` files were modified recently
2. Read current `AGENTS.md`, `PROJECT_STATUS.md`, `BRANCHING.md`
3. Compare with templates to see what's new
4. Either:
   - Regenerate and merge (preserving our data)
   - Manually copy new sections
5. Update `PROJECT_STATUS.md` with a note about template sync

**Example Update Flow**:
```bash
# 1. Check what changed in templates
git log --oneline core/*.template.md

# 2. If templates improved, backup current files
cp AGENTS.md AGENTS.md.backup
cp PROJECT_STATUS.md PROJECT_STATUS.md.backup

# 3. Regenerate (answer 'yes' to overwrite)
pg init --with-branching --ticket-prefix PROTO

# 4. Manually restore our custom sections:
#    - Our tickets from PROJECT_STATUS.md.backup
#    - Our sprint status
#    - Our recent updates
#    - Any custom agent configurations

# 5. Clean up backups
rm *.backup
```

**Benefits**:
1. **Test in real time** - See changes immediately as we develop
2. **Self-documenting** - We use the templates we tell others to use
3. **Catch issues early** - Experience the user workflow firsthand
4. **Better design** - Feel pain points ourselves and fix them
5. **Templates stay current** - Our dogfooding files reflect latest improvements

**Development Cycle**:
1. Make changes to `core/proto_gear.py` or templates
2. Test immediately: `pg init --dry-run` (editable install means changes are live)
3. Run tests: `pytest`
4. **If templates changed**: Update our dogfooding files (see above)
5. Use Proto Gear templates to track our own work:
   - Create tickets in PROJECT_STATUS.md
   - Follow BRANCHING.md conventions
   - Apply TESTING.md TDD patterns
   - Coordinate via AGENTS.md
6. When shipping new version: bump version in `pyproject.toml`, reinstall: `pip install -e .`

## Architecture Overview

### Code Structure (Package)
- **`core/`** - Main package directory containing all Python modules
- **`proto_gear.py`** - Main entry point with CLI interface and wizard orchestration
- **`setup.py`** - Package configuration and dependencies
- **Entry points** - Multiple CLI aliases (`pg`, `proto-gear`, `protogear`, `agent-framework`)

### Core Components

#### CLI Interface
- **`proto_gear.py`** - Main CLI entry point
  - Commands: `init`, `help`
  - Project detection and auto-configuration
  - Beautiful terminal UI with rich formatting via `ui_helper.py`
- **`interactive_wizard.py`** - Interactive setup wizard with arrow key navigation
- **`ui_helper.py`** - Centralized UI/UX methods for consistent terminal output

#### Template System
- **`AGENTS.template.md`** - Template for AI agent collaboration guides
  - Contains patterns for 4 core + 2 flex agent roles
  - Describes decision-making workflows as natural language patterns
  - Code blocks are illustrative, not executable
- **`PROJECT_STATUS.template.md`** - Template for project state tracking
  - Ticket status workflow (PENDING → IN_PROGRESS → COMPLETED)
  - Sprint type configuration
  - State management rules for agents
- **`BRANCHING.template.md`** - Git workflow conventions
  - Branch naming patterns
  - Conventional commit format
  - Workflow examples
- **`TESTING.template.md`** - TDD workflow guide
  - Red-Green-Refactor cycle
  - Test pyramid structure
  - Coverage targets and best practices

### Generated Files
When users run `pg init`, these templates are customized with:
- **AGENTS.md** - Project-specific agent collaboration guide
- **PROJECT_STATUS.md** - Initialized project state tracker
- **BRANCHING.md** (optional) - Git workflow conventions
- **TESTING.md** (optional) - TDD patterns and practices

## Development Workflow

### Operation Mode
Proto Gear focuses exclusively on generating collaboration templates for existing projects. It does NOT scaffold new projects, make tech stack decisions, or execute code automatically.

**Template Generation Process**:
1. Run `pg init` in any existing project directory
2. Proto Gear detects the existing technology stack (Node.js, Python, etc.)
3. Creates customized template files (AGENTS.md, PROJECT_STATUS.md, etc.)
4. Templates provide patterns for AI agents to follow using native tools
5. Does NOT modify existing code - only adds documentation templates

**How AI Agents Use Templates**:
1. **Read Context**: AI agents read AGENTS.md and PROJECT_STATUS.md for project context
2. **Follow Patterns**: Code blocks in templates describe decision-making processes, not executable code
3. **Use Native Tools**: Agents execute git, pytest, npm, etc. using their own judgment
4. **Update State**: Agents modify PROJECT_STATUS.md as work progresses
5. **Natural Collaboration**: Humans and AI work together through shared documentation

### Testing and Validation
- All commands support `--dry-run` for safe testing
- Test suite covers initialization, template generation, and technology detection
- Current coverage: 38% (target: 70%+)
- Run tests: `pytest --cov=core --cov-report=term-missing`

### Package Management
- Uses setuptools with entry points for multiple CLI aliases
- Supports Python 3.8+ with core dependencies: pyyaml, click, rich
- Development dependencies include pytest, flake8, black, mypy
- Installed in editable mode: `pip install -e .`

## Important Implementation Details
- Main executable is `proto_gear.py` in the `core/` directory
- CLI uses `ui_helper.py` for consistent ANSI terminal formatting
- Supports automatic technology stack detection for existing projects
- Generates context-aware templates based on detected frameworks
- Completely tech stack agnostic - works with any programming language or framework
- Does NOT modify existing code - only generates template documentation
- Does NOT execute workflows automatically - templates guide AI agents to use native tools
- Agent patterns are adaptive: 4 core + 2 flex slots that change based on sprint type
- Template code blocks are illustrative patterns, not executable Python

## Branching and Commit Strategy

**IMPORTANT**: All contributors (human and AI) MUST follow the branching and commit conventions defined in `docs/dev/branching-strategy.md`.

### Quick Reference for AI Agents

#### Branch Naming
- **Feature**: `feature/PROTO-XXX-description`
- **Bugfix**: `bugfix/PROTO-XXX-description`
- **Hotfix**: `hotfix/vX.Y.Z-issue`
- **Docs**: `docs/topic`
- **Refactor**: `refactor/component-description`

#### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

**Scopes**: `cli`, `agent`, `git`, `test`, `state`, `config`, `docs`, `setup`, `structure`

#### Before Starting Work
1. Verify on `development` branch: `git checkout development`
2. Pull latest: `git pull origin development`
3. Create feature branch: `git checkout -b feature/PROTO-XXX-description`
4. Verify branch name follows convention

#### Making Commits
1. **DO**: Make atomic commits (one logical change)
2. **DO**: Write clear commit messages following convention
3. **DO**: Reference issue numbers: `Closes PROTO-XXX`
4. **DO**: Test before committing (minimum: `pg init --dry-run`)
5. **DON'T**: Commit directly to `main` or `development`
6. **DON'T**: Use vague messages like "fix stuff" or "updates"

#### Creating Pull Requests

**IMPORTANT**: Proto Gear now detects your workflow mode and provides appropriate guidance!

**Workflow Modes**:
- **Local-Only**: No remote configured - use local merges
- **Remote (Manual PRs)**: Remote configured, no `gh` CLI - create PRs via web interface
- **Remote (Automated)**: Remote configured with `gh` CLI - use `gh pr create`

Proto Gear automatically detects:
- Git repository status
- Remote repository configuration
- GitHub CLI (`gh`) availability

When `pg init --with-branching` is run, BRANCHING.md will include:
- Detected workflow mode
- Specific recommendations based on your setup
- Instructions for installing `gh` CLI if needed

**For AI Agents**: Read the "Workflow Mode" section in BRANCHING.md to understand the project's workflow capabilities before attempting to create PRs.

**PR Creation Guidelines**:
- **Title**: Same format as commit message (e.g., `feat(cli): add --version flag`)
- **Description**: Include summary, changes made, testing done, checklist
- **Reference**: Always reference related issue (e.g., `Closes PROTO-XXX`)

### Current Issue Tracking
- **Format**: `PROTO-{number}` (e.g., PROTO-001, PROTO-002)
- **Starting from**: PROTO-001
- **Track in**: PROJECT_STATUS.md (once we initialize dogfooding) or GitHub Issues

### Protected Branches
- **`main`**: Production-ready code, no direct commits, requires PR + review
- **`development`**: Integration branch, no direct commits for features, merge via PR

**For complete details, see**: `docs/dev/branching-strategy.md`

## Regular Assessment Practice

**IMPORTANT**: AI agents working on Proto Gear should perform regular readiness assessments to track progress and identify gaps.

### Assessment Guidelines

#### When to Perform Assessments
- **After major feature implementations** (3+ PRs merged)
- **After significant refactoring or architectural changes**
- **Monthly** (if active development continues)
- **Before release milestones** (v0.4.0, v0.5.0, v1.0.0, etc.)
- **On request** from project maintainers

#### Assessment Process
1. **Review Current State**: Examine all completed work since last assessment
2. **Update READINESS_ASSESSMENT.md**: Located in `docs/dev/readiness-assessment.md`
3. **Document Changes**: List all improvements, new features, and fixes
4. **Update Scores**: Recalculate readiness scores across all categories
5. **Identify Gaps**: Highlight critical blockers and remaining work
6. **Provide Recommendations**: Clear next steps for reaching production readiness

#### Assessment Structure
The readiness assessment should include:
- **Executive Summary**: Current status and key improvements
- **Feature Assessment**: What's working, what's missing
- **Architecture Evaluation**: Strengths and weaknesses
- **Readiness Score**: Numerical scores (0-10) for each category
- **Before/After Comparison**: Show progress since last assessment
- **Critical Gaps**: What blocks production use
- **Path to v1.0.0**: Clear roadmap with timeline
- **Recommendations**: For maintainers and users

#### Key Metrics to Track
```
| Category              | Score | Target |
|-----------------------|-------|--------|
| Core Functionality    | X/10  | 9/10   |
| Test Coverage         | X/10  | 9/10   |
| Documentation         | X/10  | 8/10   |
| Security              | X/10  | 8/10   |
| Performance           | X/10  | 7/10   |
| Error Handling        | X/10  | 8/10   |
| Deployment            | X/10  | 7/10   |
| Monitoring            | X/10  | 7/10   |
| Configuration         | X/10  | 8/10   |
| State Management      | X/10  | 8/10   |
| User Experience       | X/10  | 8/10   |
```

#### Critical Blocker Tracking
Always highlight the #1 critical blocker preventing production use:
- **Current**: Lack of automated test coverage (38% → target 70%+)
- **Priority**: CRITICAL - Blocks v1.0.0 release

#### Assessment Example
See `docs/dev/readiness-assessment.md` for the current comprehensive assessment. This file should be treated as a living document that evolves with the project.

**Last Assessment**: 2025-10-31
**Next Assessment Due**: After project restructuring OR significant feature work
**Assessment History**: Track progress over time to show velocity and improvement

### Benefits of Regular Assessments
1. **Transparency**: Honest evaluation of project state
2. **Progress Tracking**: Measure improvements over time
3. **Gap Identification**: Highlight what needs work
4. **User Guidance**: Help users make informed decisions
5. **Contributor Focus**: Clear priorities for next work
6. **Release Planning**: Know when ready for production

By performing regular assessments, we ensure Proto Gear maintains honest positioning and provides clear value to users while working toward production readiness.

## Key Documentation

### For Users
- **Getting Started**: `docs/user/getting-started.md` - First-time setup guide
- **Template Guide**: `docs/user/template-guide.md` - Understanding templates
- **Guides**: `docs/user/guides/` - Detailed usage tutorials

### For Contributors
- **Project Structure**: `docs/dev/project-structure.md` - File organization
- **Branching Strategy**: `docs/dev/branching-strategy.md` - Git workflow
- **Configuration**: `docs/dev/configuration.md` - Setup and configuration
- **Readiness Assessment**: `docs/dev/readiness-assessment.md` - Project status
- **Universal Capabilities Design**: `docs/dev/universal-capabilities-design.md` - Future features

### For Development
- **Analysis Archive**: `dev/analysis/` - Historical code analysis reports
- **Scripts**: `dev/scripts/` - Development automation (when created)

## Next Steps for New Contributors

1. **Install**: `pip install -e .`
2. **Run tests**: `pytest`
3. **Try it out**: `pg init --dry-run`
4. **Initialize dogfooding**: `pg init --with-branching --ticket-prefix PROTO`
5. **Read**: `docs/dev/branching-strategy.md` for Git workflow
6. **Review**: `docs/dev/project-structure.md` for organization
7. **Check**: `PROJECT_STATUS.md` for current tickets (once created)
8. **Start contributing**: Follow AGENTS.md patterns

---

*Proto Gear Development Guide - Updated 2025-11-04*
