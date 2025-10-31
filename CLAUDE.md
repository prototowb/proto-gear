# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Proto Gear is a Python-based AI Agent Framework that integrates intelligent development workflows into existing projects. It provides adaptive agent orchestration, sprint management, ticket generation, and Git workflow automation - completely tech stack agnostic and designed to work with any programming language or framework.

## Development Commands

### Core Development
- **Install (development)**: `pip install -e .`
- **Build**: `python setup.py build`
- **Test**: `python -m pytest`
- **Lint**: `python -m flake8 core/`
- **Development test suite**: `bash dev-test.sh`

### Main Commands
- **Primary command**: `pg init` - Initialize AI agent framework in current project
- **Workflow command**: `pg workflow` - Run the agent workflow orchestrator
- **Help command**: `pg help` - Show detailed documentation
- **Dry run testing**: `pg init --dry-run`
- **Direct Python execution**: `cd core && python proto_gear.py init --dry-run`

### Testing Specific Scenarios
```bash
# Test Agent Framework Initialization
pg init --dry-run

# Test Workflow Orchestrator
cd core && python agent_framework.py
```

## Architecture Overview

### Code Structure
- **`core/`** - Main package directory containing all Python modules
- **`proto_gear.py`** - Main entry point with CLI interface and wizard orchestration
- **`setup.py`** - Package configuration and dependencies
- **Entry points** - Multiple CLI aliases (`pg`, `proto-gear`, `protogear`, `agent-framework`)

### Core Components

#### Agent Framework System
- **`agent_framework.py`** - Core agent system implementation with adaptive hybrid orchestration
  - `AdaptiveHybridSystem`: 4 core + 2 flex agent slots
  - `SprintType`: Defines sprint types (Feature, Bug Fix, Performance, etc.)
  - `WorkflowOrchestrator`: Main execution loop for Lead AI
  - `TicketGenerator`: Creates and manages development tickets
- **`AGENTS.template.md`** - Template for AI agent integration guides
- **`PROJECT_STATUS.template.md`** - Template for project state tracking

#### Workflow Systems
- **`git_workflow.py`** - Git integration and branch management
  - Automatic branch creation for tickets
  - Branch naming conventions
  - Git workflow status tracking
- **`testing_workflow.py`** - Testing framework integration

#### CLI Interface
- **`proto_gear.py`** - Main CLI entry point
  - Commands: `init`, `workflow`, `help`
  - Project detection and auto-configuration
  - Beautiful terminal UI with rich formatting

### Key Templates
- **AGENTS.md** - AI agent activation guide with project-specific context
- **PROJECT_STATUS.md** - Single source of truth for project state tracking
- Generated files include auto-detection of technology stack and framework-specific configurations

## Development Workflow

### Operation Mode
Proto Gear focuses exclusively on adding AI agent workflows to existing projects. It does NOT scaffold new projects or make tech stack decisions.

**Agent Framework Integration**:
1. Run `pg init` in any existing project directory
2. ProtoGear detects the existing technology stack (Node.js, Python, etc.)
3. Creates AGENTS.md and PROJECT_STATUS.md files
4. Integrates adaptive agent system without modifying existing code
5. Ready to use `pg workflow` for orchestration

### Testing and Validation
- Use `dev-test.sh` for comprehensive testing during development
- All commands support `--dry-run` for safe testing
- Test suite covers initialization, workflow orchestration, and technology detection

### Package Management
- Uses setuptools with entry points for multiple CLI aliases
- Supports Python 3.8+ with core dependencies: pyyaml, click, rich
- Development dependencies include pytest, flake8, black, mypy

## Important Implementation Details
- Main executable is `proto_gear.py` in the `core/` directory
- CLI uses ANSI escape codes for beautiful terminal interfaces with ASCII art logos
- Supports automatic technology stack detection for existing projects
- Generates context-aware AGENTS.md and PROJECT_STATUS.md based on detected frameworks
- Completely tech stack agnostic - works with any programming language or framework
- Does NOT modify existing code - only adds workflow documentation and tracking
- Agent system is adaptive: 4 core agents + 2 flex agents that change based on sprint type

## Branching and Commit Strategy

**IMPORTANT**: All contributors (human and AI) MUST follow the branching and commit conventions defined in `docs/BRANCHING_STRATEGY.md`.

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

**Scopes**: `cli`, `agent`, `git`, `test`, `state`, `config`, `docs`, `setup`

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
- **Title**: Same format as commit message (e.g., `feat(cli): add --version flag`)
- **Description**: Include summary, changes made, testing done, checklist
- **Reference**: Always reference related issue (e.g., `Closes PROTO-XXX`)

### Current Issue Tracking
- **Format**: `PROTO-{number}` (e.g., PROTO-001, PROTO-002)
- **Starting from**: PROTO-001
- **Track in**: GitHub Issues or PROJECT_STATUS.md

### Protected Branches
- **`main`**: Production-ready code, no direct commits, requires PR + review
- **`development`**: Integration branch, no direct commits for features, merge via PR

**For complete details, see**: `docs/BRANCHING_STRATEGY.md`

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
2. **Update READINESS_ASSESSMENT.md**: Located in `docs/READINESS_ASSESSMENT.md`
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
- **Current**: Lack of automated test coverage (0% → target 70%+)
- **Priority**: CRITICAL - Blocks v1.0.0 release

#### Assessment Example
See `docs/READINESS_ASSESSMENT.md` for the current comprehensive assessment. This file should be treated as a living document that evolves with the project.

**Last Assessment**: 2025-10-31
**Next Assessment Due**: After test suite implementation OR significant feature work
**Assessment History**: Track progress over time to show velocity and improvement

### Benefits of Regular Assessments
1. **Transparency**: Honest evaluation of project state
2. **Progress Tracking**: Measure improvements over time
3. **Gap Identification**: Highlight what needs work
4. **User Guidance**: Help users make informed decisions
5. **Contributor Focus**: Clear priorities for next work
6. **Release Planning**: Know when ready for production

By performing regular assessments, we ensure Proto Gear maintains honest positioning and provides clear value to users while working toward production readiness.