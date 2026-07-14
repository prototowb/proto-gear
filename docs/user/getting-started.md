# Getting Started with Proto Gear

**Version**: 0.3.0 (Alpha)
**Status**: Development/Experimentation Use

> ⚠️ **Alpha Software**: Proto Gear is currently in alpha development. Use for experimentation and development projects. Not recommended for production without thorough testing.

## What is Proto Gear?

Proto Gear is a **Python-based AI Agent Framework** that provides infrastructure ("rails") for external AI services to work consistently with development projects. Think of it as the organizational backbone that AI assistants like Claude, GPT, or custom agents use to maintain structure and consistency across development sessions.

### Core Philosophy

Proto Gear is **NOT** an AI system itself. It's the **framework** that external AI services use to:
- Maintain consistent project state
- Organize development workflows
- Track progress across sessions
- Coordinate multiple specialized agents
- Enforce development conventions

### Key Features

- 🤖 **Orchestration Paradigms**: a selectable pool (dynamic, solo, driver-reviewer, core-flex, pipeline, fan-out) — pick and switch on the fly, with a model tier per agent
- 📊 **Project State Management**: Single source of truth via PROJECT_STATUS.md
- 🎯 **Sprint-Based Configuration**: Agents adapt to sprint type (Feature Development, Bug Fixing, etc.)
- 🎫 **Ticket Generation**: Structured ticket creation with proper ID management
- 🌿 **Git Workflow Integration**: Automatic branch management for tickets
- 📋 **Documentation Consistency**: Ensures AGENTS.md hierarchy stays synchronized
- 🔍 **Auto-Detection**: Recognizes existing tech stack (Node.js, Python, etc.)
- 🎨 **Beautiful CLI**: Rich terminal interface with ANSI art

---

## Quick Start (5 Minutes)

### Prerequisites

- **Python**: 3.8 or higher
- **Git**: For branch management features
- **pip**: Python package manager

### Installation

#### Option 1: Install from PyPI (Recommended)

```bash
pip install proto-gear
```

#### Option 2: Install from Source (Development)

```bash
git clone https://github.com/proto-gear/proto-gear.git
cd proto-gear
pip install -e .
```

### Verify Installation

```bash
# Check that pg command is available
pg --help

# Should display:
# Proto Gear - AI Agent Framework for Development Workflows
```

---

## Initialize Your First Project

### 1. Navigate to Your Project

```bash
cd /path/to/your-existing-project
```

**Important**: Proto Gear works with **existing projects**. It does not scaffold new projects or make tech stack decisions. It adds AI workflow infrastructure to YOUR project.

### 2. Run Interactive Setup Wizard

```bash
pg init
```

Proto Gear will launch an **interactive wizard** that guides you through setup:

```
╔═════════════════════════════════════════════════════════════╗
║                                                             ║
║                  PROTO GEAR                                 ║
║                  🤖 AI Agent Framework v0.3 🤖              ║
║                                                             ║
╚═════════════════════════════════════════════════════════════╝

⚡ AI-Powered Development Workflow Framework ⚡

ProtoGear Interactive Setup Wizard
==========================================================

📊 Project Detection
------------------------------
Directory: my-nextjs-app
Type: Node.js Project
Framework: Next.js
Git: Initialized
Remote: origin

📋 Branching & Git Workflow
------------------------------
Proto Gear can generate a comprehensive branching strategy document
that defines Git workflow conventions and commit message standards.

This includes:
  • Branch naming conventions (feature/*, bugfix/*, hotfix/*)
  • Conventional commit message format
  • Workflow examples for AI agents
  • PR templates and merge strategies

✓ Git repository detected - branching strategy recommended

Generate BRANCHING.md? (y/n): y

🎫 Ticket Prefix Configuration
------------------------------
Tickets and branches use a prefix for identification.
Examples: PROJ-001, APP-042, MYAPP-123

Suggested prefix: MYNEXT

Enter ticket prefix (press Enter for 'MYNEXT'): APP
Using prefix: APP

📝 Configuration Summary
==========================================================
Project: my-nextjs-app
Type: Node.js Project
Framework: Next.js

Files to be created:
  ✓ AGENTS.md (AI agent integration guide)
  ✓ PROJECT_STATUS.md (Project state tracking)
  ✓ BRANCHING.md (Git workflow conventions)

Ticket Prefix: APP

Proceed with setup? (y/n): y

✅ SUCCESS: ProtoGear AI Agent Framework integrated!

📄 Files created:
  + AGENTS.md
  + PROJECT_STATUS.md
  + BRANCHING.md
```

**What just happened?**

1. **Project Detection**: Proto Gear analyzed your directory structure and detected your tech stack
2. **Branching Strategy**: You chose to generate BRANCHING.md with Git workflow conventions
3. **Ticket Configuration**: You set a custom prefix (APP) for ticket IDs like APP-001, APP-002
4. **File Generation**: Three files were created with project-specific content

### Alternative: Non-Interactive Setup

For automation or CI/CD environments, use command-line flags:

```bash
# Skip wizard, use defaults
pg init --no-interactive

# Skip wizard with custom configuration
pg init --no-interactive --with-branching --ticket-prefix MYAPP

# Preview without creating files
pg init --dry-run
```

### 3. Review Generated Files

#### AGENTS.md
This file provides context to AI assistants about your project:
- Detected project type and framework
- Orchestration doctrine (paradigm pool + per-agent model tiers)
- Workflow commands
- Instructions for AI assistants
- Reference to branching strategy (if enabled)

#### PROJECT_STATUS.md
Single source of truth for project state:
- Current project phase
- Active and completed tickets
- Project analysis
- Recent updates

#### BRANCHING.md (Optional)
Generated if you chose branching strategy during setup:
- Branch naming conventions (feature/PREFIX-XXX-description)
- Conventional commit format (type(scope): subject)
- Workflow examples for AI agents
- Remote vs. local Git workflows
- PR templates and merge strategies

**Important**: This document is customized for YOUR project with:
- Your chosen ticket prefix
- Your Git configuration (remote vs local-only)
- Your main and development branch names

---

## Using Proto Gear with AI Assistants

### With Claude (Recommended)

1. **Share AGENTS.md**: Provide the AGENTS.md file to Claude
2. **Reference PROJECT_STATUS.md**: Claude will read current state
3. **Work naturally**: Claude uses Proto Gear conventions automatically
4. **Tickets & Branches**: Claude creates tickets and branches following Proto Gear structure

### With GPT/Custom AI

1. **Read AGENTS.md**: Have your AI assistant read the file
2. **Follow conventions**: AI should respect AGENTS.md instructions
3. **Update PROJECT_STATUS.md**: AI updates state as work progresses
4. **Use workflow commands**: `pg workflow` to check consistency

---

## Core Concepts

### 1. Orchestration Paradigms

There is **no fixed agent roster**. For each task the overseer composes the
**minimal set of sub-agents** it needs and picks an **orchestration paradigm** —
a named pattern for how those sub-agents are distributed. The human (via the
interactive UI) or the overseeing agent selects a paradigm and **switches on the
fly** as circumstances change, optimizing for efficiency.

Browse the pool with `pg orchestration list` (`pg orchestration show <id>` for
detail):

| Paradigm | Use it for |
|----------|-----------|
| `dynamic` | **Default** — compose the minimal set per task; re-architect mid-flight |
| `solo` | Trivial, local, low-risk changes — one actor, no sub-agents |
| `driver-reviewer` | Risky/shared code — implementer plus an independent reviewer |
| `core-flex` | Sustained multi-domain sprints — a small persistent core plus situational flex (the former "4 core + 2 flex", now one option with open counts) |
| `pipeline` | Release-bound work — sequential discipline hand-off (eng → qa → devops) |
| `fan-out` | Decomposable breadth — parallel workers, then integrate |

#### Model tier per agent

Each agent (`pg agent`) can declare a **model tier** — `fast` (mechanical),
`balanced` (default), `deep` (judgment, architecture, review) — plus an optional
concrete override. Match the tier to the work: cheap models for mechanical
steps, strong models for judgment. See `pg agent show <name>`.

### 2. Sprint Types

Proto Gear adapts to different development phases:

- `FEATURE_DEVELOPMENT` - Building new functionality
- `BUG_FIXING` - Resolving issues
- `PERFORMANCE_OPTIMIZATION` - Speed improvements
- `DEPLOYMENT_PREP` - Release preparation
- `REFACTORING` - Code quality
- `RESEARCH_INTEGRATION` - New technologies

### 3. Project State Management

**PROJECT_STATUS.md** is the single source of truth:

```yaml
project_phase: "Development"
protogear_enabled: true
framework: "Next.js"
current_sprint: 1
```

Contains:
- 🎫 Active Tickets
- ✅ Completed Tickets
- 📊 Project Analysis
- 🔄 Recent Updates

### 4. Ticket Management

Tickets are automatically assigned IDs:

- **Format**: `PROJ/A-001` (agent-generated)
- **Format**: `PROJ-001` (human-created)
- **Types**: feature, bugfix, refactor, docs, test, chore
- **Status**: pending, in_progress, completed, blocked

### 5. Git Workflow Integration

When tickets are created, Proto Gear can:
- Create properly named branches
- Follow convention: `feature/proj-a-001-implement-auth`
- Track branch status in PROJECT_STATUS.md
- Support bugfix, hotfix, and feature types

---

## Workflow Commands

### Initialize Agent Framework

```bash
# Initialize in current project
pg init

# Preview without creating files
pg init --dry-run
```

### Run Workflow Orchestrator

```bash
# Execute Lead AI workflow
pg workflow
```

The orchestrator will:
1. Read PROJECT_STATUS.md
2. Detect sprint type
3. Configure agent slots
4. Check documentation consistency
5. Create Git branches for tickets
6. Report workflow status

### Show Help

```bash
# Display comprehensive help
pg help
```

---

## Configuration

### Basic Configuration

Proto Gear works with sensible defaults, but you can customize behavior with a config file:

**Create**: `agent-framework.config.yaml` in your project root

**Minimal Example**:
```yaml
agents:
  core:
    - id: backend
      name: "Backend Agent"
    - id: frontend
      name: "Frontend Agent"
    - id: testing
      name: "Testing Agent"
    - id: devops
      name: "DevOps Agent"

git:
  main_branch: "main"
  dev_branch: "development"

testing:
  framework: "pytest"
  coverage_threshold: 80

tickets:
  prefix: "MYPROJ"
```

### Complete Configuration

See comprehensive example:
```bash
examples/agent-framework.config.yaml
```

For detailed configuration options, see: [CONFIGURATION.md](CONFIGURATION.md)

---

## Working with AI Agents

### Before Starting Development

1. **Initialize Proto Gear**: Run `pg init` once
2. **Share AGENTS.md**: Provide to your AI assistant
3. **Reference PROJECT_STATUS.md**: AI reads current state
4. **Start Working**: AI follows Proto Gear conventions

### During Development

AI assistants should:
- ✅ Update PROJECT_STATUS.md as work progresses
- ✅ Create tickets with proper IDs
- ✅ Follow branch naming conventions
- ✅ Maintain documentation consistency
- ✅ Run `pg workflow` periodically to check state

### After Development Sessions

```bash
# Check workflow status
pg workflow

# Review PROJECT_STATUS.md
# Verify all tickets and branches are tracked
```

---

## Project Detection

Proto Gear automatically detects:

### Node.js Projects
- **Indicators**: package.json presence
- **Frameworks**: Next.js, React, Vue.js, Express.js
- **Action**: Analyzes dependencies

### Python Projects
- **Indicators**: requirements.txt, setup.py, pyproject.toml
- **Frameworks**: Django, FastAPI, Flask
- **Action**: Checks for manage.py (Django)

### Other Languages
Future support planned for:
- Ruby (Gemfile)
- Java (pom.xml, build.gradle)
- Go (go.mod)
- Rust (Cargo.toml)
- PHP (composer.json)

---

## Examples & Use Cases

### Example 1: Solo Developer with Claude

**Scenario**: Building a Next.js app with Claude's assistance

```bash
cd my-nextjs-app
pg init

# AGENTS.md now contains project context
# Share with Claude and start development
# Claude creates tickets, branches, and maintains PROJECT_STATUS.md
```

### Example 2: Small Team (2-4 Developers)

**Scenario**: Team using AI assistants for various features

```bash
pg init

# Each developer:
# 1. Reads AGENTS.md for project context
# 2. Uses AI assistant following Proto Gear conventions
# 3. Updates PROJECT_STATUS.md with tickets
# 4. Runs `pg workflow` to check consistency
```

### Example 3: Adding Tests to Existing Project

**Scenario**: Using Proto Gear to organize test coverage improvements

```bash
pg init
# Create tickets in PROJECT_STATUS.md for test coverage
# AI assistant generates tests following ticket structure
# Proto Gear creates branches automatically
# Track progress in PROJECT_STATUS.md
```

---

## Best Practices

### 1. Project Organization
- ✅ Run `pg init` once per project
- ✅ Keep AGENTS.md and PROJECT_STATUS.md in repo root
- ✅ Commit both files to version control
- ✅ Update PROJECT_STATUS.md regularly

### 2. Working with AI
- ✅ Always share AGENTS.md with AI assistants
- ✅ Reference PROJECT_STATUS.md for current state
- ✅ Let AI create tickets and branches
- ✅ Run `pg workflow` to verify consistency

### 3. Configuration
- ✅ Start with defaults
- ✅ Customize only what you need
- ✅ Use examples/ folder for reference
- ✅ Document custom configurations

### 4. Team Coordination
- ✅ Establish PROJECT_STATUS.md update cadence
- ✅ Use Git for conflict resolution
- ✅ Run `pg workflow` before major changes
- ✅ Keep AGENTS.md synchronized

---

## Troubleshooting

### "Command not found: pg"

**Solution**: Ensure Proto Gear is installed and in PATH

```bash
pip install --upgrade proto-gear
# or
pip install -e . # if installing from source
```

### "Not a Git repository"

**Solution**: Git workflow features require a Git repo

```bash
git init
# or work in an existing Git repository
```

### "Files already exist"

**Solution**: AGENTS.md or PROJECT_STATUS.md already present

```bash
# Backup existing files
mv AGENTS.md AGENTS.md.backup
mv PROJECT_STATUS.md PROJECT_STATUS.md.backup

# Re-run init
pg init
```

### AI Assistant Not Following Conventions

**Solution**: Ensure AI reads AGENTS.md at session start

```
"Please read AGENTS.md and follow the Proto Gear conventions
defined there for all development work in this project."
```

---

## Advanced Topics

### Custom Agent Behaviors

Future: Extend agent classes for custom logic

```python
from agent_framework import Agent

class CustomAgent(Agent):
    def execute(self, context):
        # Your custom logic
        return results
```

### Multi-Project Workspaces

Coming in future versions:
- Manage multiple projects
- Shared agent configurations
- Cross-project dependencies

### CI/CD Integration

Future: GitHub Actions and GitLab CI templates for Proto Gear workflows

---

## Getting Help

### Documentation
- 📘 [Branching Strategy](BRANCHING_STRATEGY.md) - Git workflow conventions
- 📘 [Configuration Reference](CONFIGURATION.md) - All config options
- 📘 [Readiness Assessment](READINESS_ASSESSMENT.md) - Current project status
- 📘 [Contributing Guide](../CONTRIBUTING.md) - How to contribute

### Support
- 🐛 [Report Issues](https://github.com/proto-gear/proto-gear/issues)
- 💬 [Discussions](https://github.com/proto-gear/proto-gear/discussions)
- 📧 Email: team@protogear.dev

### Community
- 💬 Discord: (Coming soon)
- 🐦 Twitter: @protogear (Coming soon)

---

## What's Next?

### Current Version (v0.3.0 Alpha)
- ✅ Core CLI functionality
- ✅ Agent system implementation
- ✅ Git workflow integration
- ✅ Project state management
- ⚠️ Alpha quality - use for development

### Roadmap to v0.4.0
- 🔄 Comprehensive test suite
- 🔄 Structured logging
- 🔄 Configuration validation
- 🔄 Improved error handling

### Roadmap to v1.0.0
- 🔄 Multi-project support
- 🔄 Plugin system
- 🔄 CI/CD templates
- 🔄 Monitoring dashboard
- 🔄 Production-ready stability

---

## Contributing

Proto Gear is open source and welcomes contributions!

See [CONTRIBUTING.md](../CONTRIBUTING.md) for:
- Branching strategy
- Commit message conventions
- Development workflow
- Testing guidelines

---

## License

MIT License - see [LICENSE](../LICENSE) for details.

---

## Quick Command Reference

```bash
# Installation
pip install proto-gear

# Initialize project
pg init

# Preview initialization
pg init --dry-run

# Run workflow orchestrator
pg workflow

# Show help
pg help

# Check version
pip show proto-gear
```

---

**Ready to get started?**

```bash
cd your-project
pg init
```

Let Proto Gear provide the structure while your AI assistants do the work! 🚀

---

*Proto Gear v0.3.0 (Alpha) - Infrastructure for AI-Assisted Development*
