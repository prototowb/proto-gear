# 🤖 Proto Gear

> AI Agent Framework for Intelligent Development Workflows

[![Version](https://img.shields.io/badge/version-0.3.0-blue)](https://github.com/proto-gear/proto-gear)
[![Status](https://img.shields.io/badge/status-alpha-orange)](docs/READINESS_ASSESSMENT.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)
[![Tech Stack Agnostic](https://img.shields.io/badge/stack-agnostic-orange)](docs/features.md)

> ⚠️ **Alpha Software**: Proto Gear v0.3.0 is alpha-quality software suitable for development and experimentation. Not recommended for production use without thorough testing. See [Readiness Assessment](docs/READINESS_ASSESSMENT.md) for details.

## ⚡ What is Proto Gear?

Proto Gear is an AI-powered development workflow framework that integrates intelligent agents into your existing projects. It provides **adaptive agent orchestration**, **sprint management**, **ticket generation**, and **Git workflow automation** - completely tech stack agnostic and designed to work with any programming language or framework.

**Key Philosophy**: Proto Gear doesn't make tech stack decisions for you. It focuses purely on adding AI-powered development workflows to YOUR existing projects.

## ✨ Core Features

- 🤖 **Adaptive Hybrid Agent System**: 4 permanent core agents + 2 flexible sprint-based agents
- 📊 **Project State Management**: Single source of truth via PROJECT_STATUS.md
- 🎯 **Sprint-Based Configuration**: Agents adapt to Feature Development, Bug Fixing, Performance, etc.
- 🎫 **Intelligent Ticket Generation**: Automated ticket creation and tracking
- 🌿 **Git Workflow Integration**: Automatic branch management for tickets and features
- 📋 **Documentation Consistency**: Ensures AGENTS.md hierarchy stays synchronized
- 🔍 **Auto-Detection**: Recognizes your existing tech stack (Node.js, Python, etc.)
- 🎨 **Beautiful CLI**: Rich terminal interface with ANSI art and colors

## 🎬 Quick Start

### Installation

```bash
# Install Proto Gear globally
pip install proto-gear

# Or install from source
git clone https://github.com/proto-gear/proto-gear.git
cd proto-gear
pip install -e .
```

### Usage

```bash
# Navigate to your existing project
cd my-project

# Initialize AI Agent Framework (interactive wizard)
pg init

# Or use non-interactive mode with flags
pg init --with-branching --ticket-prefix MYAPP

# Run the agent workflow orchestrator
pg workflow

# Get help
pg help
```

### Interactive Setup Wizard

When you run `pg init`, Proto Gear launches an **interactive wizard** that:

1. **Detects your project** - Automatically identifies your tech stack and framework
2. **Asks about branching strategy** - Choose whether to generate BRANCHING.md
3. **Configures ticket prefix** - Set your custom ticket ID format (e.g., MYAPP-001)
4. **Shows confirmation summary** - Review what will be created before proceeding

**Example:**
```
📊 Project Detection
------------------------------
Directory: my-nextjs-app
Type: Node.js Project
Framework: Next.js
Git: Initialized
Remote: origin

📋 Branching & Git Workflow
------------------------------
Generate BRANCHING.md? (y/n): y

🎫 Ticket Prefix Configuration
------------------------------
Enter ticket prefix (press Enter for 'MYNEXT'): APP

📝 Configuration Summary
==========================================================
Files to be created:
  ✓ AGENTS.md (AI agent integration guide)
  ✓ PROJECT_STATUS.md (Project state tracking)
  ✓ BRANCHING.md (Git workflow conventions)

Ticket Prefix: APP

Proceed with setup? (y/n): y
```

### What Gets Created?

Proto Gear creates 2-3 key files depending on your configuration:

1. **`AGENTS.md`** - AI agent integration guide with:
   - Detected project type and framework
   - Agent configuration (core + flex agents)
   - Workflow commands
   - Context-aware instructions for AI assistants

2. **`PROJECT_STATUS.md`** - Single source of truth containing:
   - Current project phase and sprint
   - Active and completed tickets
   - Project analysis and component status
   - Recent updates and changes

3. **`BRANCHING.md`** (optional) - Git workflow conventions including:
   - Branch naming patterns (feature/*, bugfix/*, hotfix/*)
   - Conventional commit format
   - Workflow examples for AI agents
   - PR templates and merge strategies

## 🏗️ Architecture

### Adaptive Hybrid Agent System

Proto Gear uses a **4 + 2 agent model**:

#### Core Agents (Always Active)
- **Backend Agent**: Server-side logic, APIs, database integration
- **Frontend Agent**: UI/UX, component development, styling
- **Testing Agent**: Test creation, coverage analysis, quality assurance
- **DevOps Agent**: CI/CD, deployment, infrastructure management

#### Flex Agents (Sprint-Based)
Two slots that automatically configure based on sprint type:
- **Documentation Agent**: For feature development and refactoring sprints
- **Performance Agent**: For performance optimization sprints
- **Security Agent**: For security-focused sprints
- **Refactoring Agent**: For code quality improvement sprints

### Sprint Types

Proto Gear adapts to different development phases:
- `FEATURE_DEVELOPMENT` - Building new functionality
- `BUG_FIXING` - Resolving issues
- `PERFORMANCE_OPTIMIZATION` - Speed and efficiency improvements
- `DEPLOYMENT_PREP` - Preparing for release
- `REFACTORING` - Code quality improvements
- `RESEARCH_INTEGRATION` - Exploring new technologies

## 📋 Workflow Commands

```bash
# Initialize AI agents (interactive wizard)
pg init

# Initialize with non-interactive mode (for automation)
pg init --no-interactive --with-branching --ticket-prefix MYAPP

# Preview what will be created (dry run)
pg init --dry-run

# Run agent workflow orchestrator
pg workflow

# Show detailed documentation
pg help
```

### Command Line Options

**`pg init` options:**
- `--dry-run` - Preview files without creating them
- `--with-branching` - Generate BRANCHING.md (skips interactive wizard)
- `--ticket-prefix PREFIX` - Set custom ticket prefix (skips interactive wizard)
- `--no-interactive` - Skip wizard completely (use defaults)

## 🤖 How It Works

1. **Detection Phase**
   - Proto Gear scans your project directory
   - Detects package.json, requirements.txt, etc.
   - Identifies your tech stack (Node.js, Python, etc.)

2. **Integration Phase**
   - Creates AGENTS.md with project-specific context
   - Creates PROJECT_STATUS.md for state tracking
   - Does NOT modify your existing code

3. **Orchestration Phase**
   - Run `pg workflow` to activate the orchestrator
   - Agents analyze project state
   - Tickets are generated and tracked
   - Git branches created automatically
   - Documentation consistency checked

## 📊 PROJECT_STATUS.md Structure

```yaml
project_phase: "Development"
protogear_enabled: true
framework: "Next.js"
project_type: "Node.js Project"
current_sprint: 1
```

**Sections**:
- 🎫 Active Tickets
- ✅ Completed Tickets
- 📊 Project Analysis
- 🔄 Recent Updates

## 🎫 Ticket Management

Proto Gear automatically generates tickets with:
- Unique IDs (e.g., `PROJ/A-001` for agent-generated tickets)
- Type classification (feature, bugfix, refactor, etc.)
- Status tracking (pending, in_progress, completed, blocked)
- Git branch association
- Test file tracking

## 🌿 Git Workflow Integration

When tickets are created, Proto Gear:
- Creates properly named feature branches
- Follows convention: `feature/proj-a-001-implement-auth`
- Tracks branch status in PROJECT_STATUS.md
- Supports bugfix, hotfix, and feature branch types

## 🔧 Technology Detection

Proto Gear automatically detects:

### Node.js Projects
- package.json presence
- Frameworks: Next.js, React, Vue.js, Express.js
- Dependencies analysis

### Python Projects
- requirements.txt, setup.py, pyproject.toml
- Frameworks: Django, FastAPI, Flask
- manage.py for Django projects

### Future Support
- Ruby (Gemfile)
- Java (pom.xml, build.gradle)
- Go (go.mod)
- Rust (Cargo.toml)
- PHP (composer.json)

## 🧪 Development & Testing

### For Proto Gear Developers

```bash
# Install in editable mode
pip install -e .

# Run development tests
bash dev-test.sh

# Test agent framework initialization
pg init --dry-run

# Test workflow orchestrator
cd core && python agent_framework.py

# Run linting
python -m flake8 core/

# Run tests
python -m pytest
```

### Direct Python Testing

```bash
cd proto-gear/core
python proto_gear.py init --dry-run
python proto_gear.py workflow
python proto_gear.py help
```

## 📖 Example: Adding to Existing Project

```bash
# Navigate to your project
cd my-nextjs-app

# Initialize Proto Gear
$ pg init

╔═════════════════════════════════════════════════════════════╗
║   PROTO GEAR - AI Agent Framework v0.3                     ║
╚═════════════════════════════════════════════════════════════╝

⚡ AI-Powered Development Workflow Framework ⚡

Agent Framework Setup
------------------------------
Current directory: /Users/dev/my-nextjs-app
Detected: Node.js Project
Framework: Next.js

✅ SUCCESS: ProtoGear AI Agent Framework integrated!

📄 Files created:
  + AGENTS.md
  + PROJECT_STATUS.md

🚀 Next steps:
  1. Review AGENTS.md to understand AI agent capabilities
  2. Check PROJECT_STATUS.md for project state tracking
  3. Start development with AI-powered assistance
  4. Run 'pg workflow' to activate the agent workflow orchestrator
```

## 🤝 Contributing

We welcome contributions! Proto Gear is focused on being the best AI agent framework for development workflows.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🔗 Links

- [Documentation](https://protogear.dev/docs)
- [GitHub](https://github.com/proto-gear/proto-gear)
- [Discord Community](https://discord.gg/protogear)
- [Issues](https://github.com/proto-gear/proto-gear/issues)

## 🙏 Credits

Proto Gear evolved from the Agent Framework project, now focused exclusively on providing intelligent AI-powered development workflows for any project, regardless of tech stack.

---

<p align="center">
  Made with ❤️ by the Proto Gear Team
</p>

<p align="center">
  <i>May your sprints be productive and your agents be intelligent!</i>
</p>
