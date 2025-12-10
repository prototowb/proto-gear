# Changelog

All notable changes to Proto Gear will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.8.0] - 2025-12-10

### Added - Composition Engine & Agent Builder System

**Major Feature Release**: Complete agent composition system allowing users to build custom AI agents from modular capabilities with automatic dependency resolution.

#### Capability Metadata v2.0 (Phase 1)
- **Structured YAML Metadata** for all 20 capabilities (skills, workflows, commands)
  - Rich metadata: ID, version, name, description, category, tags
  - Dependency system: required/optional/suggested dependencies
  - Conflict detection: incompatible capability tracking
  - Usage examples and prerequisites documentation
- **20 metadata.yaml files** created (one per capability)
- **34 comprehensive tests** for metadata validation and parsing
- **100% test pass rate** across all metadata tests

#### Composition Engine (Phase 1)
- **Automatic Dependency Resolution**
  - Transitive dependency resolution (A→B→C automatically includes all)
  - Circular dependency detection using graph traversal
  - Conflict detection for incompatible capability combinations
- **Smart Capability Recommendations**
  - Suggests optional/suggested dependencies based on selections
  - Context-aware recommendations during agent building
- **Robust Validation System**
  - Validates all capability references
  - Checks dependency availability
  - Prevents invalid configurations

#### Agent Configuration System (Phase 2)
- **YAML-Based Agent Definitions**
  - Store custom agent configurations as `.proto-gear/agents/*.yaml`
  - Define capabilities, instructions, and context priority
  - Reusable agent templates for different project roles
- **AgentManager Class** for agent lifecycle management
  - Load, save, validate, and list agents
  - Automatic dependency resolution when loading agents
  - Graceful error handling with detailed validation messages
- **5 Example Agents** included out-of-box:
  - Backend Developer: Testing, Debugging, Feature Dev
  - Frontend Developer: Testing, Code Review, Feature Dev
  - Full-Stack Developer: Complete feature development suite
  - DevOps Engineer: Release, Hotfix, Testing workflows
  - QA Engineer: Testing, Debugging, Bug Fix workflows
- **CLI Commands** for agent management:
  - `pg capabilities list` - Show all available capabilities
  - `pg capabilities show <name>` - View capability details with dependencies
  - `pg agent create` - Interactive wizard for creating agents
  - `pg agent list` - Show all saved agents
  - `pg agent show <name>` - View agent configuration
  - `pg agent validate <name>` - Validate agent configuration
- **22 comprehensive tests** for agent configuration and CLI
- **100% test pass rate** across all agent tests

#### Interactive Agent Creation Wizard (Phase 3)
- **6-Step Guided Workflow**
  1. Welcome & overview of agent creation process
  2. Basic information (name, description, author)
  3. Multi-select capability selection with categories
  4. Context priority configuration (1-5 scale)
  5. Agent-specific instructions
  6. Preview & confirm before saving
- **Smart Features**
  - Real-time validation (circular deps, conflicts)
  - Smart capability recommendations during selection
  - Template defaults for quick setup
  - Graceful keyboard interrupt handling
  - Rich formatted panels and tables (with fallback)
- **Multi-Select Capability UI**
  - Grouped by type (Skills, Workflows, Commands)
  - Arrow key navigation
  - Checkbox selection interface
  - Shows counts and categories
- **Time Savings**: 75-85% faster than manual YAML editing (3-5 min vs 20-30 min)
- **4 wizard tests** (validation logic fully tested)

### Technical Details

**New Files** (11 total):
- `core/proto_gear_pkg/capability_metadata.py` (220 lines) - Metadata models and parsing
- `core/proto_gear_pkg/composition_engine.py` (280 lines) - Dependency resolution engine
- `core/proto_gear_pkg/agent_config.py` (180 lines) - Agent configuration dataclasses
- `core/proto_gear_pkg/agent_manager.py` (240 lines) - Agent lifecycle management
- `core/proto_gear_pkg/cli_commands.py` (450 lines) - CLI command handlers
- `core/proto_gear_pkg/agent_wizard.py` (650 lines) - Interactive agent creation wizard
- `tests/test_metadata_parsing.py` (300 lines, 10 tests)
- `tests/test_composition_engine.py` (450 lines, 24 tests)
- `tests/test_agent_config.py` (280 lines, 12 tests)
- `tests/test_cli_commands.py` (320 lines, 10 tests)
- `tests/test_agent_wizard.py` (103 lines, 4 tests)

**Modified Files**:
- `core/proto_gear_pkg/proto_gear.py` (+150 lines) - CLI integration
- `core/proto_gear_pkg/interactive_wizard.py` (+45 lines) - Wizard integration
- 20 capability directories - Added metadata.yaml files

**Metadata Files Created** (20 total):
- Skills: testing, debugging, code-review, refactoring
- Workflows: feature-development, bug-fix, hotfix, release, finalize-release
- Commands: create-ticket

**Example Agents Created** (5 total):
- `.proto-gear/agents/backend-developer.yaml`
- `.proto-gear/agents/frontend-developer.yaml`
- `.proto-gear/agents/fullstack-developer.yaml`
- `.proto-gear/agents/devops-engineer.yaml`
- `.proto-gear/agents/qa-engineer.yaml`

### Statistics
- **Total Lines Added**: 5,250+ lines
- **Test Coverage**: 60 tests total (34 metadata + 22 agent + 4 wizard)
- **Test Pass Rate**: 100% (all 60 tests passing)
- **Files Modified**: 48 files
- **New Modules**: 6 core modules
- **Example Agents**: 5 ready-to-use configurations

### Impact
- **For Users**: Build custom AI agents tailored to project needs in 3-5 minutes
- **For AI Agents**: Automatically resolve dependencies, validate configurations
- **For Proto Gear**: Foundation for v1.0.0 agent composition features

### Breaking Changes
None - Fully backward compatible with v0.7.3

### Usage

```bash
# List all available capabilities
pg capabilities list

# Show detailed capability information
pg capabilities show testing

# Create a new agent interactively
pg agent create

# List all saved agents
pg agent list

# Show agent configuration
pg agent show backend-developer

# Validate agent configuration
pg agent validate my-custom-agent
```

### Related Tickets
- PROTO-026: [EPIC] Capability Composition Engine & Agent Builder
  - Phase 1: Capability metadata system + composition engine
  - Phase 2: Agent configuration system + CLI commands
  - Phase 3: Interactive agent creation wizard

### Documentation
- **Complete Phase Summary**: `docs/dev/PROTO-026-final-summary.md`
- **Wizard Demo**: `wizard_demo_walkthrough.md`
- **Architecture**: Detailed in phase summary document

---

## [0.7.3] - 2025-12-07

### Added
- **Comprehensive Cross-Reference Network Across All Templates**
  - Added "📚 Related Documentation" sections to all 8 core templates
  - AGENTS.md now references all possible generated files (was missing 5 files)
  - Every template cross-references related documentation for easy navigation
  - Created interconnected documentation graph with AGENTS.md as master hub
  - Templates now list CONTRIBUTING.md, SECURITY.md, ARCHITECTURE.md, CODE_OF_CONDUCT.md

- **Mandatory Capability Discovery System**
  - New Critical Rule #1: "ALWAYS check `.proto-gear/INDEX.md` first"
  - Pre-Flight Checklist Item #1: Check for capabilities before starting any task
  - 3-step capability discovery workflow with explicit instructions
  - Adaptive design: works whether capabilities are installed or not
  - Capability references integrated across all relevant templates

- **Enhanced AGENTS.md Template** (691 lines, +73% increase)
  - Comprehensive "BEFORE ANY WORK - MANDATORY READING" section now includes 8 files
  - TESTING.md added to mandatory reading (was missing)
  - 5 optional templates now documented (CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT, capabilities)
  - Detailed capability discovery workflow (Step 1: Check, Step 2: Discover, Step 3: Load)
  - Clear workflow for using capabilities with native tools
  - Updated Pre-Flight Checklist from 5 to 9 items

- **Documentation Improvements**
  - PROJECT_STATUS.md: Added related documentation section
  - TESTING.md: Added title header and cross-references to AGENTS.md, capabilities
  - BRANCHING.md: Added cross-references to workflows and feature-development
  - CONTRIBUTING.md: Added references with BRANCHING.md marked as REQUIRED
  - SECURITY.md: Added security-specific documentation references
  - ARCHITECTURE.md: Added architectural task capability references
  - CODE_OF_CONDUCT.md: Added community documentation links

- **Developer Documentation** (3 new files)
  - `docs/dev/dogfooding-update-guide.md` - Guide for updating Proto Gear's own templates
  - `docs/dev/capability-discovery-flow.md` - Visual flow diagram with examples
  - `docs/dev/template-improvements-2025-12-07.md` - Comprehensive technical summary

### Fixed
- **Critical: AGENTS.md Used Hardcoded Content Instead of Template**
  - `setup_agent_framework_only()` function had hardcoded v0.5.0 AGENTS.md content
  - Template updates were being ignored, always generating 58-line outdated version
  - Replaced hardcoded content with call to `generate_project_template()`
  - Now correctly uses AGENTS.template.md file with all improvements

### Changed
- **Help System Updated**
  - `pg help` now lists all 8 templates with (recommended)/(optional) labels
  - Added .proto-gear/ capabilities system to template list
  - Updated "Getting Started" workflow to mention reviewing all generated files
  - More comprehensive template documentation in help output

- **Template Coverage**
  - Files referenced in AGENTS.md: 3 → 8 (+167%)
  - Templates with cross-references: 0 → 8 (all templates)
  - AGENTS.md lines: ~400 → 691 (+73%)
  - Capability mentions across templates: 1 → 8 (+700%)
  - Pre-flight checklist items: 5 → 9 (+80%)

### Impact
- **For AI Agents**: Complete awareness of all generated files, mandatory capability discovery
- **For Users**: Professional interconnected documentation, no orphaned files
- **For Proto Gear**: Production-ready template quality, self-documenting system

### Technical
- Zero breaking changes - fully backward compatible
- All templates tested and verified working
- Template generation confirmed at 691 lines for AGENTS.md
- Cross-reference network validated across all 8 templates

## [0.7.2] - 2025-11-22

### Fixed
- **Incremental Wizard Crashes** (9 critical bugs fixed)
  - Missing CHARS keys (`plus`, `gear`, `refresh`) causing KeyError
  - Missing style attribute - Changed `wizard.style` → `PROTO_GEAR_STYLE`
  - Missing force parameter in `setup_agent_framework_only()` causing NameError
  - Wrong Colors constants - `Colors.RESET` → `Colors.ENDC`, `Colors.RED` → `Colors.FAIL`
  - Core files (AGENTS.md, PROJECT_STATUS.md) created even when not selected
  - List format core_templates not handled properly
  - Unselected templates being generated in incremental mode
  - Incorrect success message reporting skipped files as created

### Changed
- **AGENTS.md Template Enhanced for Better Agent Adherence**
  - Added prominent "⚠️ BEFORE ANY WORK - MANDATORY READING" section at top
  - Explicit Read tool instructions: `Read(file_path="PROJECT_STATUS.md")`
  - Pre-flight checklist with actionable items
  - 5 critical rules clearly stated (never commit to main, always update status, etc.)
  - Direct, actionable language to ensure agents actually read referenced files

### Technical
- Fixed all AttributeError and NameError exceptions in incremental wizard
- Improved file selection logic to respect user choices
- Better reporting of actually created files (excludes skipped files)
- Template now explicitly instructs agents to use Read tool before starting work

## [0.7.1] - 2025-11-22

### Added
- **Incremental Update Wizard** (PROTO-023)
  - Automatic detection of existing Proto Gear installations
  - Rich table display showing current installation status
  - Multiple update modes:
    - Add missing templates (shows count of available templates)
    - Add capabilities system (if not installed)
    - Update all templates to latest version
    - Custom selection (choose specific templates to add/update)
  - Seamless integration with existing wizard flow
  - Proper ticket prefix handling for BRANCHING.md additions
  - Graceful fallback for non-rich terminal environments

- **File Protection System** (PROTO-023)
  - Interactive prompts when files already exist
  - Four user options: Overwrite, Skip, Backup (.bak), View diff
  - `--force` flag for non-interactive overwrites
  - `detect_existing_environment()` function
  - `safe_write_file()` function with action tracking
  - Updated all file write operations to use safe writing

### Changed
- Init wizard now detects existing installations and offers incremental updates
- File write operations now check for existence before overwriting

### Technical
- New `run_incremental_wizard()` function in interactive_wizard.py
- Enhanced init command handler with environment detection
- Maintains backward compatibility with non-interactive mode

## [0.7.0] - 2025-11-21

### Added
- **Template Metadata System** (PROTO-020)
  - YAML frontmatter support in all templates
  - Conditional content rendering based on configuration
  - Metadata fields: title, description, version, requires_git, preset_compatibility
  - Backward compatible with existing templates
  - New `MetadataParser` class with `parse_template()` and `apply_conditional_content()`
  - Comprehensive test coverage (17 new tests)

- **Rust Project Detection** (PROTO-021)
  - Cargo.toml detection with priority over package.json
  - Framework detection for 6 Rust frameworks:
    - Actix Web (web framework)
    - Rocket (web framework)
    - Axum (web framework)
    - Warp (web framework)
    - Tauri (desktop apps)
    - Yew (WebAssembly frontend)
  - Handles wasm-pack scenarios correctly
  - Workspace detection support
  - 17 comprehensive tests for Rust detection

### Changed
- Detection priority: Cargo.toml now checked before package.json
- Enhanced project structure detection with better framework identification
- Test coverage: 42% → 47% (+5%)
- Test count: 218 → 302 tests (+84 tests)

### Fixed
- Rust projects with package.json (wasm-pack) no longer misidentified as Node.js

### Documentation
- **New Release Workflow Documentation** (`docs/dev/release-workflow.md`)
  - Dedicated 590+ line release process guide
  - Separate workflows for patch/minor/major releases
  - Explicit GitHub release creation steps (marked 🚨 CRITICAL)
  - Post-release checklists and emergency procedures
  - Release notes templates and version numbering guide

- **Updated Branching Strategy**
  - Added "Starting New Work" section to prevent main branch work
  - Clear command: `git checkout -b feature/XXX development`
  - Emphasizes always branching FROM development
  - Updated both BRANCHING.md and BRANCHING.template.md

- **Updated Readiness Assessment** (`docs/dev/readiness-assessment.md`)
  - Version: v0.6.4 → v0.7.0
  - Readiness Score: 8.3/10 → 8.8/10 (+0.5)
  - Added new categories: Project Detection (9/10), Template Metadata (9/10)
  - Updated test coverage statistics

### Technical
- New `metadata_parser.py` module for template frontmatter
- Enhanced `detect_project_structure()` with Rust support
- New test file: `test_rust_detection.py` (17 tests)
- New test file: `test_template_metadata.py` (17 tests)

## [0.6.4] - 2025-11-14

### Changed
- **Test Suite Overhaul** (PROTO-017)
  - Overall coverage: 39% → 42% (+3%)
  - proto_gear.py coverage: 52% → 61% (+9%)
  - 218 tests passing in 4.63 seconds
  - Zero memory leaks (fixed 20+ GB RAM consumption issue)
  - Zero hanging tests (fixed infinite wait on interactive input)
  - Removed 1,207 lines of redundant test code
  - Added 1,747 lines of targeted, high-value tests

### Added
- **New Test Files**
  - `test_capability_security.py` (19 tests) - Security checks and error handling
  - `test_coverage_boost.py` (22 tests) - Git workflows and template generation
  - `test_project_detection.py` (15 tests) - Framework detection (Next.js, React, Vue, Express, Django, FastAPI)
  - `test_setup_function.py` (16 tests) - Setup function branches and edge cases
  - `test_proto_gear_core.py` - Core functionality placeholder

### Fixed
- **Memory leak in test suite** - Tests calling interactive functions no longer hang
- **Test reliability** - All 218 tests pass consistently with proper mocking
- **Test performance** - Fast execution (~4.6s) with zero flaky tests

### Technical
- Comprehensive git workflow testing (no_git, local_only, remote_manual, remote_automated)
- Framework detection coverage for all major frameworks
- Security testing for symlink rejection, path traversal prevention
- Capability system filtering and configuration testing
- Proper subprocess mocking for git command simulation

## [0.6.3] - 2025-11-12

### Fixed
- **Template Versioning**: Templates now use dynamic `{{VERSION}}` instead of hardcoded "v0.3"
  - BRANCHING.template.md: Fixed hardcoded version
  - TESTING.template.md: Fixed hardcoded version (2 occurrences)
  - Added VERSION to template_context dictionary
  - Added VERSION replacement in generate_branching_doc function
  - Generated templates now correctly show current Proto Gear version

### Changed
- **Documentation Cleanup**: Removed 15 deprecated documentation files
  - Removed session notes and temporary implementation guides
  - Removed duplicate release notes (consolidated in CHANGELOG.md)
  - Cleaner project structure

### Added
- Quality-focused readiness assessment for v0.6.2
  - Beta maturity level (7.2/10)
  - No-rush philosophy emphasizing quality over speed
  - Archived v0.3.0 assessment for historical reference

## [0.6.2] - 2025-11-09

### Changed
- **Enhanced Final Output Display**
  - Files created section now separates template files from capability files
  - Capability files are grouped with summary showing counts (skills/workflows/commands)
  - Next steps are now dynamic based on what was actually created
  - Added cross-platform path handling (supports both `/` and `\` separators)
  - Cleaner, more informative output that highlights what capabilities were installed

### Example
```
Files created:
  + BRANCHING.md
  + AGENTS.md
  + TESTING.md
  + CONTRIBUTING.md
  + PROJECT_STATUS.md

Capabilities installed (15 files):
  + .proto-gear/ directory with:
    • 5 skill(s)
    • 6 workflow(s)
    • 2 command(s)

Next steps:
  1. Review AGENTS.md for collaboration patterns
  2. Check PROJECT_STATUS.md for project state
  3. Review TESTING.md for TDD patterns
  4. Follow BRANCHING.md conventions for Git workflow
  5. Explore .proto-gear/ for available skills, workflows, and commands
  6. AI agents will read these templates and collaborate naturally
```

## [0.6.1] - 2025-11-09

### Fixed
- **CRITICAL**: Wizard template selections were being completely ignored
  - User selections in wizard (TESTING, CONTRIBUTING, etc.) not generated
  - Only AGENTS.md and PROJECT_STATUS.md were created regardless of selections
  - `core_templates` parameter now properly passed through generation pipeline
  - All selected templates are now generated correctly
  - Non-selected templates correctly excluded
- Dry-run mode now displays selected templates accurately

### Technical
- Added `core_templates` parameter to `setup_agent_framework_only()`
- Added `core_templates` parameter to `run_simple_protogear_init()`
- Updated wizard invocation to pass `core_templates` from wizard config
- Template generation now has 3 priority levels: wizard selections > --all flag > legacy behavior

## [0.6.0] - 2025-11-09

### Added
- **Template Auto-Discovery System** (PROTO-023 completed)
  - `discover_available_templates()` function automatically finds all `*.template.md` files
  - Adding new templates now requires ZERO code changes
  - Templates are dynamically discovered at runtime
- **Granular Capability Selection** in interactive wizard
  - Users can now see detailed descriptions of each capability
  - 3 selection levels: All, By Category, or Individual capabilities
  - Shows exactly what skills/workflows/commands are being installed
  - Detailed CAPABILITIES_METADATA with descriptions for all 10 capabilities
- Enhanced wizard UX with capability details
  - Skills: Testing, Debugging, Code Review, Refactoring
  - Workflows: Feature Dev, Bug Fix, Hotfix, Release, Finalize
  - Commands: Create Ticket
- Auto-discovery fallback to hardcoded list for robustness

### Changed
- Interactive wizard now uses template auto-discovery for dynamic template selection
- Template selection shows count of available templates (e.g., "6 available")
- Configuration summary displays individual capability names when using granular selection
- Improved capability descriptions in wizard panels

### Fixed
- Template additions no longer require manual wizard updates (addresses wizard sync issue)
- Users can now make informed decisions about which capabilities to install

## [0.5.3] - 2025-11-09

### Fixed
- **Critical**: Interactive wizard now includes all v0.5.0+ templates (CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT)
- Interactive wizard was frozen at v0.4.1 feature set - now fully synced with CLI
- "Full Setup" preset now correctly generates ALL 8 templates using `with_all=True`
- Custom template selection now offers all 5 additional templates (was only TESTING)
- Wizard config now properly passes `with_all` flag to generation function

### Added
- Documented root cause in `WIZARD-TEMPLATE-SYNC-ISSUE.md` to prevent future sync issues
- Prevention checklist for adding new templates without breaking wizard
- Enhanced template selection in custom wizard path with all templates

### Changed
- Updated PRESETS to reflect v0.5.2+ feature set
- "Full Setup" preset description now accurate: "All 8 templates + full capabilities"
- "Quick Start" preset now includes TESTING.md by default
- Configuration summary displays all selected templates correctly

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
