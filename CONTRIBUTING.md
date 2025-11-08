# Contributing to Proto Gear

Thank you for your interest in contributing to Proto Gear! This document provides guidelines for contributing to the project.

**Version**: 0.3.0 (Alpha)
**Status**: Accepting Contributions

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Branching Strategy](#branching-strategy)
5. [Commit Message Conventions](#commit-message-conventions)
6. [Pull Request Process](#pull-request-process)
7. [Testing Guidelines](#testing-guidelines)
8. [Documentation](#documentation)
9. [Issue Reporting](#issue-reporting)

---

## Code of Conduct

Proto Gear follows a code of conduct to ensure a welcoming environment for all contributors:

- **Be respectful** and considerate in all interactions
- **Be collaborative** and help others learn
- **Be patient** with questions and different skill levels
- **Focus on constructive** feedback and solutions
- **Respect diverse** perspectives and experiences

Unacceptable behavior will not be tolerated. Report issues to team@protogear.dev.

---

## Getting Started

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: Version control
- **pip**: Python package manager
- **Text editor**: VS Code, PyCharm, vim, etc.

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR-USERNAME/proto-gear.git
cd proto-gear

# Add upstream remote
git remote add upstream https://github.com/proto-gear/proto-gear.git
```

### Development Installation

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
pg --help
```

### Development Dependencies

```bash
# Core dependencies (installed automatically)
# - pyyaml>=6.0
# - click>=8.0
# - rich>=13.0
# - pathlib>=1.0

# Dev dependencies (install with [dev])
# - pytest>=7.0
# - pytest-cov>=4.0
# - black>=23.0
# - flake8>=6.0
# - mypy>=1.0
```

---

## Development Workflow

### 1. Sync with Upstream

Before starting work, sync with the main repository:

```bash
git checkout development
git fetch upstream
git merge upstream/development
```

### 2. Create Feature Branch

Follow the branching strategy (see next section):

```bash
git checkout -b feature/PROTO-XXX-description
```

### 3. Make Changes

- Write code following style guidelines
- Add tests for new functionality
- Update documentation as needed
- Test your changes locally

### 4. Test Locally

```bash
# Run tests
python -m pytest

# Check code style
python -m flake8 core/

# Format code
python -m black core/

# Type checking
python -m mypy core/
```

### 5. Commit Changes

Follow commit message conventions (see below):

```bash
git add <files>
git commit -m "feat(scope): add new feature"
```

### 6. Push and Create PR

```bash
git push origin feature/PROTO-XXX-description
# Then create Pull Request on GitHub
```

---

## Branching Strategy

**IMPORTANT**: Proto Gear follows a strict branching strategy. See [docs/BRANCHING_STRATEGY.md](docs/BRANCHING_STRATEGY.md) for complete details.

### Protected Branches

- **`main`**: Production-ready code, no direct commits
- **`development`**: Integration branch, merge via PR

### Working Branches

| Pattern | Purpose | Example |
|---------|---------|---------|
| `feature/PROTO-XXX-description` | New features | `feature/PROTO-008-add-logging` |
| `bugfix/PROTO-XXX-description` | Bug fixes | `bugfix/PROTO-015-fix-parser` |
| `hotfix/vX.Y.Z-issue` | Critical fixes | `hotfix/v0.3.1-state-corruption` |
| `docs/topic` | Documentation | `docs/api-reference` |
| `refactor/component-description` | Refactoring | `refactor/state-validation` |

### Branch Naming Rules

✅ **Good**:
- `feature/PROTO-010-add-test-suite`
- `bugfix/PROTO-023-fix-unicode-error`
- `docs/configuration-guide`

❌ **Bad**:
- `my-feature` (no issue number)
- `fix-bug` (too vague)
- `PROTO-010` (missing type prefix)

---

## Commit Message Conventions

Proto Gear uses **Conventional Commits** format.

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Description | Example |
|------|-------------|---------|
| `feat` | New feature | `feat(cli): add --version flag` |
| `fix` | Bug fix | `fix(state): handle malformed YAML` |
| `docs` | Documentation | `docs(readme): update installation` |
| `style` | Code style | `style(core): apply black formatting` |
| `refactor` | Refactoring | `refactor(git): extract branch logic` |
| `perf` | Performance | `perf(parser): optimize YAML parsing` |
| `test` | Tests | `test(agent): add sprint config tests` |
| `build` | Build system | `build(deps): update pyyaml` |
| `ci` | CI/CD | `ci(github): add pytest workflow` |
| `chore` | Maintenance | `chore(version): bump to v0.3.1` |

### Scopes

Common scopes for Proto Gear:

- `cli` - Command-line interface
- `agent` - Agent framework
- `git` - Git workflow
- `test` - Testing workflow
- `state` - State management
- `config` - Configuration
- `docs` - Documentation
- `setup` - Package setup

### Subject Guidelines

- Use imperative mood: "add" not "added"
- Don't capitalize first letter
- No period at the end
- Maximum 50 characters

### Body (Optional but Recommended)

- Wrap at 72 characters
- Explain what and why, not how
- Separate from subject with blank line

### Footer (When Applicable)

- Reference issues: `Closes PROTO-XXX` or `Fixes #XXX`
- Breaking changes: `BREAKING CHANGE: description`
- Co-authors: `Co-authored-by: Name <email>`

### Examples

#### Simple Feature

```
feat(cli): add --version flag

Add --version flag to display Proto Gear version.

Closes PROTO-008
```

#### Bug Fix

```
fix(state): handle malformed PROJECT_STATUS.md gracefully

PROJECT_STATUS.md parsing failed when YAML block was malformed.

Changes:
- Add YAML validation before parsing
- Provide helpful error messages
- Fall back to default state

Fixes PROTO-023
```

#### Breaking Change

```
feat(config)!: add schema validation

BREAKING CHANGE: Config files now require specific schema.
Migration guide in docs/migration-guide.md.

Closes PROTO-030
```

---

## Pull Request Process

### Before Creating PR

1. ✅ All tests pass locally
2. ✅ Code follows style guidelines
3. ✅ Documentation updated
4. ✅ Commits follow convention
5. ✅ Branch synced with `development`

### PR Title

Use same format as commit message:

```
feat(cli): add --version flag
```

### PR Description

Use this template:

```markdown
## Summary
Brief description of changes

## Changes Made
- Bullet list of changes
- What was added/fixed/refactored

## Testing
- How was this tested?
- What test cases were added?

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed the code
- [ ] Added/updated tests
- [ ] Documentation updated
- [ ] No new warnings
- [ ] Commit messages follow convention

## Related Issues
Closes #XXX
```

### Review Process

1. **Automated checks** run (when CI/CD is set up)
2. **Maintainer review** - expect feedback
3. **Address feedback** - make requested changes
4. **Approval** - maintainer approves PR
5. **Merge** - maintainer merges to `development`

### After Merge

Your branch will be deleted. Update your local repository:

```bash
git checkout development
git pull upstream development
git branch -d feature/PROTO-XXX-description
```

---

## Testing Guidelines

### Current Status (v0.3.0)

⚠️ Test suite is currently minimal. We need help building comprehensive tests!

### Test Structure

```
tests/
├── test_cli.py              # CLI interface tests
├── test_agent_framework.py  # Agent system tests
├── test_git_workflow.py     # Git integration tests
├── test_state_management.py # State management tests
└── test_integration.py      # End-to-end tests
```

### Writing Tests

Use pytest:

```python
import pytest
from proto_gear import ProtoGear

def test_init_creates_files():
    """Test that pg init creates required files"""
    # Arrange
    pg = ProtoGear()

    # Act
    result = pg.init(dry_run=True)

    # Assert
    assert result['status'] == 'success'
    assert 'AGENTS.md' in result.get('files', [])
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=core --cov-report=html

# Run specific test file
python -m pytest tests/test_cli.py

# Run specific test
python -m pytest tests/test_cli.py::test_init_creates_files

# Run in verbose mode
python -m pytest -v
```

### Test Guidelines

1. **One test per function/behavior**
2. **Clear test names** describing what is tested
3. **AAA pattern**: Arrange, Act, Assert
4. **Use fixtures** for common setup
5. **Mock external dependencies** (Git, file system)
6. **Test edge cases** and error conditions

---

## Documentation

### What Needs Documentation

- **New features**: Update docs/getting-started.md
- **Configuration options**: Update docs/CONFIGURATION.md
- **API changes**: Update docstrings and examples
- **Breaking changes**: Migration guide

### Documentation Style

- **Clear and concise**
- **Examples included**
- **Step-by-step** for complex topics
- **Screenshots** for UI features (if applicable)

### Docstrings

Use Google-style docstrings:

```python
def create_ticket(self, title: str, ticket_type: str = "feature") -> Dict:
    """Create a new ticket with proper ID.

    Args:
        title: Ticket title/description
        ticket_type: Type of ticket (feature, bugfix, etc.)

    Returns:
        Dictionary containing ticket information with ID, status, etc.

    Raises:
        ValueError: If ticket_type is not valid

    Example:
        >>> ticket = manager.create_ticket("Add login", "feature")
        >>> print(ticket['id'])
        'PROTO/A-001'
    """
```

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues** - avoid duplicates
2. **Check documentation** - might be covered
3. **Test on latest version** - bug might be fixed

### Bug Reports

Use this template:

```markdown
**Describe the Bug**
Clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Ubuntu 22.04, macOS 13, Windows 11]
- Python version: [e.g., 3.10.5]
- Proto Gear version: [e.g., 0.3.0]

**Additional Context**
Screenshots, logs, etc.
```

### Feature Requests

```markdown
**Feature Description**
Clear description of the proposed feature.

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How do you envision this working?

**Alternatives Considered**
Other approaches you've thought about.

**Additional Context**
Examples, mockups, etc.
```

---

## Development Tips

### Local Testing

```bash
# Test CLI commands without installing
cd core
python proto_gear.py init --dry-run

# Test workflow orchestrator
python -c "from agent_framework import WorkflowOrchestrator; WorkflowOrchestrator().execute_workflow()"
```

### Code Style

Proto Gear follows PEP 8 with these tools:

```bash
# Format code
black core/

# Check style
flake8 core/

# Sort imports
isort core/
```

### Debug Mode

```python
# Enable verbose output
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Common Pitfalls

1. **Path issues**: Use `Path` from `pathlib`, not string concatenation
2. **Windows compatibility**: Test on Windows or use cross-platform paths
3. **Unicode handling**: Use `encoding='utf-8'` when reading/writing files
4. **Git operations**: Check if Git repo exists before Git commands

---

## Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md` (coming soon)
- Credited in release notes
- Given commit access after consistent contributions

---

## Questions?

- 💬 [Discussions](https://github.com/proto-gear/proto-gear/discussions)
- 📧 Email: team@protogear.dev
- 📘 [Documentation](docs/)

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to Proto Gear!** 🚀

*Proto Gear v0.3.0 (Alpha) - Contributing Guide*
