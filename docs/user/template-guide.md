# Template-Based Collaboration Guide

**Version**: Proto Gear v0.3.0
**Last Updated**: 2025-11-04
**Audience**: Developers, AI Agents, Project Managers

---

## Overview

Template-based collaboration is how Proto Gear enables humans and AI agents to work together naturally using structured markdown templates and native development tools.

**Proto Gear does NOT execute code automatically**. Instead, it generates templates that provide patterns, conventions, and shared context for natural collaboration.

---

## Quick Start (Choose Your Path)

### 👤 For Humans
- **New to Proto Gear?** → Start with [Template Basics](guides/01-template-basics.md)
- **Want to collaborate with AI?** → Read [How Humans Use Templates](guides/03-human-usage.md)
- **Need examples?** → Check [Workflow Examples](guides/04-workflow-examples.md)

### 🤖 For AI Agents
- **Understanding templates?** → Read [Template Basics](guides/01-template-basics.md)
- **Ready to work?** → Follow [AI Agent Usage Guide](guides/02-ai-agent-usage.md)
- **Need workflow examples?** → See [Workflow Examples](guides/04-workflow-examples.md)

### 🆘 Need Help?
- **Something not working?** → Check [Troubleshooting](guides/05-troubleshooting.md)

---

## Complete Guide Structure

### 1. [Template Basics](guides/01-template-basics.md)
- What is template-based collaboration?
- Core concepts
- Template files explained (AGENTS.md, PROJECT_STATUS.md, BRANCHING.md, TESTING.md)
- Template patterns vs. executable code

**Read this if**: You're new to Proto Gear or need to understand the foundation

### 2. [AI Agent Usage Guide](guides/02-ai-agent-usage.md)
- How AI agents read templates
- Pattern interpretation and execution
- Using native tools (git, pytest, npm, etc.)
- State management and coordination
- Best practices for AI agents

**Read this if**: You're an AI agent working with Proto Gear templates

### 3. [How Humans Use Templates](guides/03-human-usage.md)
- Solo developer workflows
- Team collaboration patterns
- Sharing context with AI assistants
- Maintaining templates
- Best practices for humans

**Read this if**: You're a human developer using Proto Gear

### 4. [Workflow Examples](guides/04-workflow-examples.md)
- Starting new features
- Fixing bugs with TDD
- Sprint planning and coordination
- Handling blocked tickets
- Common patterns in action

**Read this if**: You want concrete examples of template-based workflows

### 5. [Troubleshooting](guides/05-troubleshooting.md)
- Common problems and solutions
- AI agent confusion issues
- State synchronization problems
- Branch naming inconsistencies
- Template clarity improvements

**Read this if**: Something isn't working or needs clarification

---

## Key Principles

### Templates are Guides, Not Code
- ✅ Templates provide **patterns** for decision-making
- ✅ Code blocks are **illustrative**, not executable
- ✅ AI agents use **native tools** (git, pytest, npm)
- ❌ Do NOT try to import or execute template code

### Natural Language Collaboration
- **Shared Context**: Templates provide single source of truth
- **Judgment Required**: Agents adapt patterns to context
- **Native Tools**: Use git, pytest, npm, docker, etc. directly
- **State Tracking**: PROJECT_STATUS.md tracks progress

### Example Pattern

**Template Pattern** (from AGENTS.md):
```python
def lead_ai_workflow():
    """
    PATTERN for decision-making, not a function to call:
    1. Read PROJECT_STATUS.md
    2. Identify next ticket
    3. Create branch with native git
    """
```

**AI Agent Execution**:
```bash
$ cat PROJECT_STATUS.md  # Read state
$ git checkout -b feature/proj-001-auth  # Native tool
```

---

## Related Documentation

- [README.md](../README.md) - Project overview and quick start
- [AGENTS.template.md](../core/AGENTS.template.md) - Agent pattern template
- [PROJECT_STATUS.template.md](../core/PROJECT_STATUS.template.md) - State tracker template
- [BRANCHING.template.md](../core/BRANCHING.template.md) - Git workflow template
- [TESTING.template.md](../core/TESTING.template.md) - TDD pattern template
- [READINESS_ASSESSMENT.md](READINESS_ASSESSMENT.md) - Project maturity evaluation

---

## Contributing

Found an issue or have suggestions for improving the template guides?

- Open an issue on GitHub
- Review [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines
- Check [BRANCHING_STRATEGY.md](BRANCHING_STRATEGY.md) for commit conventions

---

**Document Version**: 2.0.0 (Split into focused guides)
**Created**: 2025-11-04
**Last Updated**: 2025-11-04
