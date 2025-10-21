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