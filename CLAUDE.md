# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
Proto Gear is a Python-based project framework generator that creates production-ready projects with AI-powered configuration. It supports 200+ frameworks across web, mobile, and desktop platforms with integrated AI agent workflow systems.

## Development Commands

### Core Development
- **Install (development)**: `pip install -e .`
- **Build**: `python setup.py build`
- **Test**: `python -m pytest`
- **Lint**: `python -m flake8 core/`
- **Development test suite**: `bash dev-test.sh`

### Main Commands
- **Primary command**: `pg init` - The unified entry point for all functionality
- **Legacy commands**: `proto-gear`, `protogear`, `agent-framework` (all redirect to main interface)
- **Dry run testing**: `pg init --dry-run`
- **Direct Python execution**: `cd core && python proto_gear.py init --dry-run`

### Testing Specific Scenarios
```bash
# Test Agent Framework Only
echo "1" | pg init --dry-run

# Test Full Project Scaffolding
echo -e "2\ntest-project" | pg init --dry-run
```

## Architecture Overview

### Code Structure
- **`core/`** - Main package directory containing all Python modules
- **`proto_gear.py`** - Main entry point with CLI interface and wizard orchestration
- **`setup.py`** - Package configuration and dependencies
- **Entry points** - Multiple CLI aliases (`pg`, `proto-gear`, `protogear`, `agent-framework`)

### Core Components

#### Wizard System
- **`main_setup_wizard.py`** - Core setup wizard logic
- **`grouped_setup_wizard.py`** - Advanced grouped configuration wizard
- **`enhanced_setup_wizard.py`** - Enhanced wizard with additional features
- **`multiplatform_wizard.py`** - Cross-platform project setup

#### Agent Framework System
- **`agent_framework.py`** - Core agent system implementation with sprint management
- **`agent_framework_wizard.py`** - Agent setup wizard
- **`AGENTS.template.md`** - Template for AI agent integration guides
- **`PROJECT_STATUS.template.md`** - Template for project state tracking

#### Workflow Systems
- **`git_workflow.py`** - Git integration and branch management
- **`testing_workflow.py`** - Testing framework integration

### Key Templates
- **AGENTS.md** - AI agent activation guide with project-specific context
- **PROJECT_STATUS.md** - Single source of truth for project state tracking
- Generated files include auto-detection of technology stack and framework-specific configurations

## Development Workflow

### Two Main Operation Modes
1. **Agent Framework Only** - Adds ProtoGear's AI workflow to existing projects (creates AGENTS.md and PROJECT_STATUS.md)
2. **Full Project Scaffolding** - Complete project generation with 7-step wizard process

### Testing and Validation
- Use `dev-test.sh` for comprehensive testing during development
- All commands support `--dry-run` for safe testing
- Test suite covers help commands, agent framework, project scaffolding, and technology detection

### Package Management
- Uses setuptools with entry points for multiple CLI aliases
- Supports Python 3.8+ with core dependencies: pyyaml, click, rich
- Development dependencies include pytest, flake8, black, mypy

## Important Implementation Details
- Main executable is `proto_gear.py` in the `core/` directory
- CLI uses rich library for beautiful terminal interfaces with ASCII art logos
- Supports automatic technology stack detection for existing projects  
- Generates context-aware documentation based on detected frameworks
- All wizards support both interactive and programmatic (piped input) usage