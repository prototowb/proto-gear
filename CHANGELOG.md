# Changelog

All notable changes to Proto Gear will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.2] - 2025-11-09

### Added
- `--all` flag to generate all available project templates
- Generic `generate_project_template()` function for template generation

### Fixed
- v0.5.0/v0.5.1 templates (CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT) now accessible via `--all` flag
- Template generation no longer requires manual CLI integration

### Changed
- Improved template generation to support all 8 templates
- Backward compatible with existing `--with-branching` flag

## [0.5.1] - 2025-11-09

### Fixed
- **Critical**: Eliminated duplicate file structure that prevented v0.5.0 features from being available
  - Consolidated all package files into `core/proto_gear_pkg/` (single source of truth)
  - Removed duplicate files from `core/` that were causing sync issues
  - All v0.5.0 capabilities (skills, workflows, templates) now properly available
- Updated version strings in correct location (`proto_gear_pkg/proto_gear.py`)
- Added finalize-release workflow for post-release verification
- Updated documentation to prevent future duplication issues

### Changed
- Package structure: `core/` now only contains `proto_gear_pkg/` and build artifacts
- Status: Alpha → Beta

## [0.5.0] - 2025-11-08

### Added - Universal Capabilities System

**Major Feature Release**: Complete capabilities system with skills, workflows, and templates for comprehensive AI-human collaboration.

#### New Skills (3)
- **Debugging & Troubleshooting** (`skills/debugging/`) - 757 lines
  - 8-step scientific method for systematic debugging
  - Debugging techniques: rubber duck, binary search, divide-and-conquer
  - Common scenarios: intermittent bugs, production-only issues, performance problems
  - Tool guidance: pdb, debugger, logging frameworks

- **Code Review** (`skills/code-review/`) - 510 lines
  - 7-point review checklist: functionality, tests, design, readability, performance, security, documentation
  - Guidelines for reviewers and authors
  - Constructive feedback patterns with examples
  - Review process workflow

- **Refactoring** (`skills/refactoring/`) - 623 lines
  - Code smells identification: long method, duplicate code, large class, magic numbers
  - Refactoring patterns: extract method, rename, extract variable, replace conditional with polymorphism
  - Red-green-refactor cycle integration
  - Real-world refactoring examples

#### New Workflows (3)
- **Bug Fix** (`workflows/bug-fix.template.md`) - 820 lines
  - 8-step systematic debugging and fix process
  - Follows scientific method: reproduce, isolate, hypothesize, test, fix, verify, prevent
  - Regression testing requirements
  - Post-fix prevention strategies

- **Hotfix** (`workflows/hotfix.template.md`) - 900 lines
  - 9-step emergency workflow for critical production issues
  - Severity decision tree (when to use hotfix vs. regular bug fix)
  - Branch from main (production) not development
  - Minimal fixes with technical debt tracking
  - Post-deployment monitoring and incident documentation

- **Release** (`workflows/release.template.md`) - 1,050 lines
  - 10-step complete release management process
  - Semantic versioning guidelines (major/minor/patch)
  - Changelog generation from conventional commits
  - Full testing suite requirements (unit, integration, e2e, security)
  - Staging deployment and QA sign-off workflow
  - Production deployment with monitoring and rollback plans

#### New Templates (4)
- **CONTRIBUTING.template.md** - 12K
  - Complete contribution guidelines with 10-step workflow
  - Development setup and testing requirements
  - Code review process and standards
  - Issue and PR creation guidelines

- **SECURITY.template.md** - 10K
  - Vulnerability reporting procedures
  - Security policies and timelines
  - Supported versions table
  - Security best practices and tools

- **ARCHITECTURE.template.md** - 11K
  - System design documentation structure
  - Architecture Decision Records (ADR) template
  - Component, data, and infrastructure architecture sections
  - Design patterns and tech stack documentation

- **CODE_OF_CONDUCT.template.md** - 12K
  - Based on Contributor Covenant v2.1
  - Community guidelines and standards
  - Enforcement procedures
  - Conflict resolution mechanisms

#### Updated Capabilities Indexes
- **skills/INDEX.template.md** - Updated with 3 new skills
- **workflows/INDEX.template.md** - Updated with 3 new workflows and decision tree

### Documentation
- **Git Worktrees Workflow** (`docs/dev/git-worktrees-workflow.md`)
  - Complete guide for parallel development using Git worktrees
  - Three-workstream approach (Templates, Skills, Workflows)
  - Branch management and merge strategies

- **Integration Documentation** for templates
  - `INTEGRATION_NOTES.md` - Step-by-step manual integration guide
  - `integrate_templates.py` - Automation script for CLI integration
  - `DEVELOPMENT_SUMMARY.md` - Complete development session summary

### Technical Details
- **Total additions**: ~6,266 lines of production-ready documentation
- **New capability files**: 10 (7 capabilities + 3 templates)
- **Total templates**: 8 (4 core + 4 new)
- **Total capabilities**: 14 files (skills, workflows, commands)
- **Development approach**: Three parallel worktree branches merged to development

### Notes
- Templates CLI integration pending (documented in `INTEGRATION_NOTES.md`)
- All capabilities follow established YAML frontmatter pattern
- Skills and workflows include comprehensive examples and anti-patterns
- Tech-stack agnostic design applies to all new capabilities


### Added - Preset-Based Wizard & Enhanced UX

**Major UX Release**: Completely redesigned interactive wizard with preset-based configuration and single-page CLI experience.

#### Preset System
- **4 Configuration Presets** for different user needs:
  - ⚡ **Quick Start** - Recommended for most projects (core templates + capabilities)
  - 📦 **Full Setup** - All features enabled
  - 🎯 **Minimal** - Just essentials (AGENTS.md, PROJECT_STATUS.md)
  - 🔧 **Custom** - Full granular control over every option

#### Custom Wizard Path
- **Stage 1: Core Templates** - Select additional templates individually
- **Stage 2: Git Workflow** - Configure BRANCHING.md and ticket prefix
- **Stage 3: Capabilities** - Granular selection:
  - Option to select all capabilities at once
  - OR choose specific categories: Skills, Workflows, Commands

#### Single-Page CLI Experience
- Screen clearing between wizard steps for focused UX
- Progress indicators showing current step (Step X of Y)
- Project context always visible in compact header
- No scrollback clutter - feels like modern single-page app

#### Improved Selection UX
- Removed confusing background colors from checkboxes
- Clear visual indicators using only:
  - ✅ Checkbox icon changes (☐ → ☑)
  - 🎨 Text color changes (white → green)
  - No reverse video or background highlighting
- Used `noreverse` attribute for clean questionary prompts

#### Documentation
- **Capabilities Roadmap** (`docs/dev/capabilities-roadmap.md`) - Comprehensive 12-month plan
  - Vision: Users assemble custom AI sub-agents from capabilities
  - Philosophy: Quality over quantity
  - 3 Phases: Foundation (v0.5.0) → Expansion (v0.7.0) → Composition (v1.0.0)
  - Timeline to v1.0.0 with sub-agent builder
  - Quality standards for all capabilities

### Changed
- Configuration summary now displays as proper table (not object reference)
- Capabilities display shows selected categories correctly
- Questionary style improved with explicit `noreverse` for cleaner UX

### Fixed
- Configuration summary table rendering (was showing `<rich.table.Table object>`)
- Capabilities display logic (was showing "no categories selected" when items were selected)
- Package relative imports for proto_gear_pkg

### Technical Details

**New Files**:
- `.github/workflows/release.yml` - Automated release workflow
- `docs/dev/capabilities-roadmap.md` - Comprehensive roadmap document
- `docs/dev/wizard-ux-redesign.md` - Design proposal (implemented)

**Modified Files**:
- `core/interactive_wizard.py` (+450 lines) - Preset system, custom wizard, UX improvements
- `core/proto_gear.py` (+45 lines) - Capabilities config parameter threading
- `pyproject.toml` - Version bump to 0.4.1

**New Methods**:
- `RichWizard.clear_screen()` - Clear terminal for single-page experience
- `RichWizard.show_step_header()` - Consistent step progress display
- `RichWizard.ask_preset_selection()` - Preset selection screen
- `RichWizard.show_preset_preview()` - Preview files before generation
- `RichWizard.ask_core_templates_selection()` - Granular template selection
- `RichWizard.ask_git_workflow_options()` - Git workflow configuration
- `RichWizard.ask_capabilities_selection()` - Granular capabilities selection

**Functions Enhanced**:
- `copy_capability_templates()` - Now accepts `capabilities_config` for granular filtering
- `setup_agent_framework_only()` - Supports capabilities_config parameter
- `run_simple_protogear_init()` - Threads capabilities_config through

### Breaking Changes
- None - Fully backward compatible with v0.4.0

### Usage

```bash
# Interactive wizard with presets
pg init

# Select preset and see exactly what will be created
# Then confirm or go back to choose different preset

# Custom path gives full control:
# 1. Choose which templates to include
# 2. Configure Git workflow
# 3. Select specific capability categories

# Non-interactive mode still works
pg init --with-capabilities --with-branching --ticket-prefix MYPROJ
```

### Related Tickets
- PROTO-023: Preset-based wizard system
- PROTO-024: Custom wizard path with granular control
- PROTO-025: Single-page CLI experience
- PROTO-026: Capabilities roadmap documentation

---

## [0.4.0] - 2025-11-06

### Added - Universal Capabilities System (Phase 1)

**Major Feature Release**: Introducing the Universal Capabilities System - a modular, discoverable pattern library for AI agents.

#### Core Features
- **Universal Capabilities System** - Modular capability templates for AI agent collaboration
  - `.proto-gear/` directory structure with organized capabilities
  - Progressive disclosure pattern (master INDEX → category → details)
  - Four capability types: Skills, Workflows, Commands, and Agents
  - YAML frontmatter metadata for all capabilities

#### CLI Enhancements
- **New Flag**: `--with-capabilities` option for `pg init` command
- Interactive wizard now includes capability system question
- Dry-run mode shows capability files that would be created
- Full support for non-interactive mode with capabilities

#### Template Library (Included)
- **Skills**: `testing/SKILL.md` - TDD methodology with red-green-refactor cycle
- **Workflows**: `feature-development.md` - 7-step feature development process
- **Commands**: `create-ticket.md` - Ticket creation and documentation patterns
- **Indexes**: Master and category-level indexes for capability discovery

#### Template Updates
- `AGENTS.template.md` - Added capability discovery section
- `PROJECT_STATUS.template.md` - Added capability command references
- All templates now reference `.proto-gear/` for extended functionality

#### Security & Quality
- **Path Traversal Prevention** - Validates all file paths during capability deployment
- **Symlink Protection** - Detects and rejects symlinks in template directory
- **UTF-8 Encoding** - Enforced across all file operations
- **File Permissions** - Proper permissions set (755 for dirs, 644 for files)
- **24 New Tests** - Comprehensive test suite for capability system
- **116 Total Tests** - Up from 90 tests (29% increase)
- **81% Coverage** - Maintained above 70% target

#### Documentation
- **Research Report**: Comprehensive design validation (8.5/10 rating)
  - 753-line analysis validating architecture decisions
  - Security analysis and recommendations
  - Industry comparison (OpenAI, Claude MCP, Google Gemini)
  - Identified alignment with emerging protocols (MCP, A2A, ACP)
- **Updated README**: New capability system documentation
- **Template Guide**: Usage instructions for all capabilities

#### Development Workflow
- **Git Worktrees**: Used for true parallel development
- **Parallel Implementation**: 6 sub-tickets completed simultaneously
- **Specialized Agents**: Research, Backend, Documentation, Testing agents

### Technical Details

**New Files**:
- `core/capabilities/INDEX.template.md`
- `core/capabilities/skills/INDEX.template.md`
- `core/capabilities/skills/testing/SKILL.template.md`
- `core/capabilities/workflows/INDEX.template.md`
- `core/capabilities/workflows/feature-development.template.md`
- `core/capabilities/commands/INDEX.template.md`
- `core/capabilities/commands/create-ticket.template.md`
- `core/capabilities/agents/INDEX.template.md`
- `tests/test_capabilities.py` (397 lines, 24 tests)
- `dev/analysis/capability-system-research-2025-11-06.md` (753 lines)

**Modified Files**:
- `core/proto_gear.py` (+355 lines) - Capability deployment logic
- `core/interactive_wizard.py` (+67 lines) - Wizard integration
- `core/AGENTS.template.md` (+31 lines)
- `core/PROJECT_STATUS.template.md` (+4 lines)
- `tests/test_proto_gear.py` (+74 lines) - Integration tests

**Functions Added**:
- `copy_capability_templates()` - Security-hardened template deployment

### Breaking Changes
- None - Fully backward compatible with v0.3.0

### Migration Guide
No migration needed. New `--with-capabilities` flag is optional. Existing functionality unchanged.

### Usage

```bash
# Initialize project with capabilities
pg init --with-capabilities

# Preview what will be created
pg init --dry-run --with-capabilities

# Combined with other options
pg init --with-capabilities --with-branching --ticket-prefix MYPROJ

# Interactive wizard (includes capability question)
pg init
```

### Related Tickets
- PROTO-003: [EPIC] Universal Capabilities System
- PROTO-017: Research and design validation
- PROTO-018: CLI integration
- PROTO-019: Deployment logic implementation
- PROTO-020: AGENTS template updates
- PROTO-021: PROJECT_STATUS template updates
- PROTO-022: Comprehensive test suite

---

## [0.3.0] - 2025-11-05

### Added
- Interactive wizard with rich UI and questionary integration
- Encoding-safe terminal output for Windows compatibility
- Local vs remote workflow detection in BRANCHING.md
- GitHub CLI detection for automated PR creation
- Comprehensive test suite (90 tests, 81% coverage)

### Changed
- Reorganized project structure (dev/package separation)
- Removed workflow execution modules (templates only)
- Updated all documentation paths and references

### Fixed
- Unicode encoding issues on Windows
- Interactive wizard fallback for terminals without rich/questionary
- BRANCHING.md now detects workflow mode (local/remote/automated)

---

## [0.2.0] - 2025-10-30

### Added
- Initial release with core template generation
- AGENTS.md, PROJECT_STATUS.md, TESTING.md templates
- Project type detection (Python, Node.js, etc.)
- Basic CLI with `pg init` and `pg help` commands

---

[0.4.1]: https://github.com/anthropics/proto-gear/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/anthropics/proto-gear/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/anthropics/proto-gear/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anthropics/proto-gear/releases/tag/v0.2.0
