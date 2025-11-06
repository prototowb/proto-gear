# Changelog

All notable changes to Proto Gear will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

[0.4.0]: https://github.com/anthropics/proto-gear/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/anthropics/proto-gear/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/anthropics/proto-gear/releases/tag/v0.2.0
