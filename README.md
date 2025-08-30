# 🤖 Agent Framework

A powerful, autonomous AI agent framework for project management and development automation.

## ✨ Features

- **Autonomous Sprint Management** - AI agents that manage development sprints
- **TDD Workflow Integration** - Built-in Test-Driven Development support
- **Git Workflow Automation** - Automatic branch creation and management
- **Adaptive Agent System** - Core and flex agents adapt to project needs
- **Project State Management** - Single source of truth with PROJECT_STATUS.md
- **Interactive Setup Wizard** - Easy project initialization

## 🚀 Quick Start

### Installation

```bash
pip install agent-framework
```

Or from source:

```bash
git clone https://github.com/yourusername/agent-framework.git
cd agent-framework
pip install -e .
```

### Initialize a New Project

```bash
agent-framework init
```

This will start the interactive setup wizard to configure your project.

### Using in Existing Projects

1. Create an `AGENTS.md` file in your project root:

```markdown
# AI Agents Configuration

Execute this file to activate the AI agent framework.

\```python
from agent_framework import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator('your-project.config.yaml')
orchestrator.execute_workflow()
\```
```

2. Run the framework:

```bash
python -c "exec(open('AGENTS.md').read())"
```

## 📁 Project Structure

```
your-project/
├── AGENTS.md                 # Entry point for AI agents
├── PROJECT_STATUS.md         # Project state tracking
├── your-project.config.yaml  # Framework configuration
└── .agent-framework-initialized  # Initialization marker
```

## 🔧 Configuration

Example `config.yaml`:

```yaml
project:
  name: "your-project"
  type: "web-app"
  description: "Your project description"

git:
  enabled: true
  default_branch: "main"
  branch_naming:
    feature: "feature/{ticket_id}-{title}"
    bugfix: "bugfix/{ticket_id}-{title}"

testing:
  framework: "pytest"
  test_directory: "tests"
  coverage_threshold: 80
  tdd_enforced: true

agents:
  core_agents:
    - product_owner
    - tech_lead
    - developer
  flex_agents:
    - qa_engineer
    - devops
```

## 🧪 TDD Workflow

The framework enforces Test-Driven Development:

1. **RED** - Write failing tests first
2. **GREEN** - Implement code to pass tests
3. **REFACTOR** - Improve code while keeping tests green

## 🌿 Git Workflow

Automatic branch management for tickets:
- Creates feature branches for each ticket
- Commits when tests pass
- Switches to next ticket's branch automatically

## 📚 Documentation

- [Getting Started](docs/getting-started.md)
- [Configuration Guide](docs/configuration.md)
- [Agent System](docs/agents.md)
- [TDD Workflow](docs/tdd-workflow.md)
- [API Reference](docs/api.md)

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with ❤️ for autonomous development workflows.
