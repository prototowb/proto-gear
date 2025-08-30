# Getting Started with Agent Framework

Welcome to the Agent Framework - an adaptive AI orchestration system for autonomous project management.

## What is Agent Framework?

Agent Framework is a reusable system that provides:
- **Hybrid Agent Management**: 4 core agents + 2 flexible agents that adapt per sprint
- **Automated Workflows**: Sprint planning, ticket generation, branch management
- **Documentation Consistency**: Hierarchical AGENTS.md system with DRY principles
- **Quality Enforcement**: Test-driven development, coverage requirements
- **Project State Management**: Single source of truth tracking

## Quick Start (5 minutes)

### 1. Initialize Your Project

```bash
# Clone the framework
git clone https://github.com/your-org/agent-framework
cd your-project

# Run the initializer
./agent-framework/scripts/init-project.sh
```

The initializer will:
- Create AGENTS.md hierarchy
- Set up PROJECT_STATUS.md
- Generate configuration file
- Create project structure

### 2. Configure Your Agents

Edit `agent-framework.config.yaml`:

```yaml
project:
  name: "My Awesome App"
  type: "web-app"
  
agents:
  core:
    - id: "backend"
      name: "Backend API Developer"
      responsibilities:
        - "API development"
        - "Database design"
    # ... configure 4 core agents
```

### 3. Activate the Framework

Have an AI agent read the root `AGENTS.md` file:

```markdown
"Please read and execute AGENTS.md"
```

The Lead AI will:
1. Initialize the agent system
2. Configure agents for current sprint
3. Check documentation consistency
4. Generate development plan
5. Create tickets and branches

## Core Concepts

### 1. Adaptive Hybrid Agent System

```
┌─────────────────────────────────────┐
│         Lead AI (Orchestrator)       │
│    Product Owner + Tech Lead         │
└──────────────┬──────────────────────┘
               │
    ┌──────────┴──────────┐
    │                     │
┌───▼────┐          ┌────▼────┐
│  Core   │          │  Flex   │
│ Agents  │          │ Agents  │
│   (4)   │          │   (2)   │
└─────────┘          └─────────┘
Always Active        Sprint-Specific
```

### 2. AGENTS.md Hierarchy

```
/ (root AGENTS.md - master orchestrator)
├── /frontend/AGENTS.md (inherits from root)
├── /backend/AGENTS.md (inherits from root)
└── /docs/AGENTS.md (inherits from root)
```

**DRY Principle**: Child files only contain LOCAL context, never duplicate parent info.

### 3. Project State Management

`PROJECT_STATUS.md` is the single source of truth:

```yaml
project_phase: "Development"
current_sprint: 1
active_tickets: [...]
```

### 4. Workflow Automation

When AGENTS.md is read:
```
1. Initialize agents
2. Check documentation
3. Update status
4. Generate tickets
5. Create branches
6. Run tests
7. Request approval
```

## Common Use Cases

### Web Application Development

```yaml
# Configure for web app
agents:
  core:
    - backend: "API Development"
    - frontend: "UI Development"
    - testing: "Quality Assurance"
    - devops: "Infrastructure"
  
  sprint_configs:
    feature_development:
      flex_agents: ["documentation", "performance"]
```

### API Service

```yaml
# Configure for API
agents:
  core:
    - api: "API Development"
    - database: "Data Management"
    - testing: "API Testing"
    - security: "Security & Auth"
```

### Mobile App

```yaml
# Configure for mobile
agents:
  core:
    - ios: "iOS Development"
    - android: "Android Development"
    - testing: "Mobile Testing"
    - backend: "API Backend"
```

## Customization

### Custom Agent Behaviors

```python
from agent_framework import Agent

class CustomAgent(Agent):
    def execute(self, context):
        # Your custom logic
        return results

# Register custom agent
orchestrator.register_agent('custom', CustomAgent)
```

### Sprint Type Detection

```python
def custom_sprint_detector(state):
    if has_many_bugs(state):
        return SprintType.BUG_FIXING
    return SprintType.FEATURE_DEVELOPMENT
```

### Workflow Extensions

```python
class ExtendedOrchestrator(WorkflowOrchestrator):
    def execute_workflow(self):
        super().execute_workflow()
        # Add custom steps
        self.run_custom_checks()
```

## Best Practices

### 1. Configuration

- **Define all 4 core agents**: Cover your main development areas
- **List flex agents**: Include specialists for different sprint types
- **Set quality gates**: Define minimum test coverage, etc.

### 2. Documentation

- **Keep DRY**: Never duplicate between parent/child AGENTS.md
- **Update regularly**: Keep PROJECT_STATUS.md current
- **Link, don't copy**: Reference other docs instead of duplicating

### 3. Workflow

- **Let agents create branches**: Automatic branch creation per ticket
- **Enforce tests**: Every ticket gets test files
- **Regular sprints**: Consistent sprint duration (e.g., 14 days)

## Advanced Features

### Multi-Project Management

```yaml
# Configure for multiple projects
projects:
  - name: "Frontend"
    agents: [...]
  - name: "Backend"  
    agents: [...]
```

### Custom Quality Gates

```python
def custom_quality_check():
    return {
        'performance': check_performance_metrics(),
        'accessibility': check_wcag_compliance(),
        'security': run_security_scan()
    }
```

### Integration with CI/CD

```yaml
# GitHub Actions integration
on:
  push:
    branches: [main]
  
jobs:
  agent-framework:
    runs-on: ubuntu-latest
    steps:
      - uses: agent-framework/action@v1
```

## Troubleshooting

### Framework not activating?
- Check AGENTS.md has the trigger notice
- Verify configuration file exists
- Ensure Python/Node dependencies installed

### Agents not configured correctly?
- Verify exactly 4 core agents defined
- Check agent IDs are unique
- Confirm responsibilities are listed

### Documentation inconsistencies?
- Run consistency check manually
- Look for duplicate content
- Verify inheritance declarations

## Examples

### Example 1: E-Commerce Platform
See [examples/web-app-example.yaml](../examples/web-app-example.yaml)

### Example 2: SaaS API
See [examples/api-example.yaml](../examples/api-example.yaml)

### Example 3: Open Source Library
See [examples/library-example.yaml](../examples/library-example.yaml)

## Next Steps

1. **Initialize your project** with the framework
2. **Configure agents** for your specific needs
3. **Read AGENTS.md** to trigger the workflow
4. **Create tickets** in PROJECT_STATUS.md
5. **Let agents orchestrate** development

## Getting Help

- 📚 [Full Documentation](https://agent-framework.dev/docs)
- 💬 [Discord Community](https://discord.gg/agent-framework)
- 🐛 [Report Issues](https://github.com/your-org/agent-framework/issues)
- 🤝 [Contributing Guide](../CONTRIBUTING.md)

## License

MIT License - See [LICENSE](../LICENSE) for details.

---

Ready to start? Run `./agent-framework/scripts/init-project.sh` and let the agents handle the rest! 🚀