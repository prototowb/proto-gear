# Proto Gear Configuration Reference

**Version**: 0.3.0 (Alpha)
**Last Updated**: 2025-10-30

Complete reference for configuring Proto Gear's behavior via `agent-framework.config.yaml`.

---

## Configuration File Location

Place your configuration file in the project root:

```
your-project/
├── agent-framework.config.yaml  ← Configuration file
├── AGENTS.md
├── PROJECT_STATUS.md
└── ...
```

Proto Gear automatically loads `agent-framework.config.yaml` if present. If not found, sensible defaults are used.

---

## Quick Start

### Minimal Configuration

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

tickets:
  prefix: "PROJ"
```

### Using Examples

```bash
# Copy minimal example
cp examples/minimal-config.yaml agent-framework.config.yaml

# Or copy comprehensive example
cp examples/agent-framework.config.yaml agent-framework.config.yaml
```

---

## Configuration Sections

### 1. Agents Configuration

Define core agents (always active) and flex agents (sprint-specific).

#### Core Agents (Required - Exactly 4)

```yaml
agents:
  core:
    - id: backend           # Unique identifier
      name: "Backend Agent" # Display name
      description: "Server-side logic, APIs, database integration"
      responsibilities:     # Optional list
        - "API development"
        - "Database schema"
        - "Authentication"

    - id: frontend
      name: "Frontend Agent"
      # ... 3 more required
```

**Rules**:
- Must define exactly 4 core agents
- IDs must be unique
- Recommended IDs: `backend`, `frontend`, `testing`, `devops`

#### Flex Agent Pool (Optional)

```yaml
agents:
  flex_pool:
    - id: documentation
      name: "Documentation Agent"
      description: "Documentation creation and maintenance"

    - id: performance
      name: "Performance Agent"

    - id: security
      name: "Security Agent"

    - id: refactoring
      name: "Refactoring Agent"
```

**Purpose**: Pool of specialist agents dynamically assigned based on sprint type.

#### Sprint-Specific Configuration

```yaml
agents:
  sprint_configs:
    feature_development:
      flex_agents:
        - documentation
        - security
      description: "Building new features"

    bug_fixing:
      flex_agents:
        - testing
        - security
      description: "Resolving bugs"

    performance_optimization:
      flex_agents:
        - performance
        - testing
      description: "Optimizing performance"

    # ... other sprint types
```

**Available Sprint Types**:
- `feature_development`
- `bug_fixing`
- `performance_optimization`
- `deployment_prep`
- `refactoring`
- `research_integration`

---

### 2. Git Workflow Configuration

Configure Git branch management and conventions.

```yaml
git:
  # Main branches
  main_branch: "main"       # Production branch
  dev_branch: "development" # Integration branch

  # Branch prefixes
  branch_prefix:
    feature: "feature/"
    bugfix: "bugfix/"
    hotfix: "hotfix/"
    release: "release/"
    experimental: "experimental/"

  # Commit conventions
  commit_convention: "conventional"  # Options: conventional, angular, custom

  # Git hooks
  hooks:
    pre_commit:
      enabled: true
      run_linting: true
      run_tests: true

    commit_msg:
      enabled: true
      validate_format: true

    pre_push:
      enabled: false
      run_tests: false
```

**Branch Naming**:
- Feature: `feature/PROTO-001-implement-auth`
- Bugfix: `bugfix/PROTO-010-fix-login`
- Hotfix: `hotfix/v0.3.1-critical-fix`

---

### 3. Testing Configuration

Configure test framework and coverage requirements.

```yaml
testing:
  # Test framework
  framework: "pytest"  # Options: pytest, unittest, nose2

  # Test directories
  test_directory: "tests"
  test_pattern: "test_*.py"

  # Coverage
  coverage_enabled: true
  coverage_threshold: 80  # Minimum percentage
  coverage_report_format: "html"  # Options: html, xml, term, json

  # Test types
  test_types:
    unit:
      enabled: true
      marker: "unit"
      timeout: 60

    integration:
      enabled: true
      marker: "integration"
      timeout: 300

    e2e:
      enabled: true
      marker: "e2e"
      timeout: 600

    performance:
      enabled: false
      marker: "performance"
      timeout: 900

  # TDD workflow
  tdd:
    enforce: true
    verify_tests_first: true
```

**Test Markers**:
Use pytest markers to categorize tests:

```python
@pytest.mark.unit
def test_function():
    pass

@pytest.mark.integration
def test_api_endpoint():
    pass
```

---

### 4. Ticket Management

Configure ticket ID format and workflow.

```yaml
tickets:
  # Ticket ID format
  prefix: "PROTO"          # e.g., PROTO-001
  start_number: 1
  zero_padding: 3          # Number of digits (001, 002, ...)

  # Agent-generated tickets
  agent_suffix: "/A"       # e.g., PROTO/A-001

  # Ticket types
  types:
    - feature
    - bugfix
    - hotfix
    - refactor
    - docs
    - test
    - chore

  # Status workflow
  statuses:
    - pending
    - in_progress
    - review
    - testing
    - completed
    - blocked
    - cancelled
```

**Ticket ID Examples**:
- Human-created: `PROTO-001`, `PROTO-002`
- Agent-generated: `PROTO/A-001`, `PROTO/A-002`

---

### 5. Project State Management

Configure PROJECT_STATUS.md behavior.

```yaml
project_state:
  # Status file
  status_file: "PROJECT_STATUS.md"

  # Update frequency
  auto_update: true
  update_on_commit: true

  # State validation
  validate_schema: true
  schema_version: "1.0"
```

---

### 6. Documentation Settings

Configure AGENTS.md hierarchy and consistency checking.

```yaml
documentation:
  # AGENTS.md files
  agents_file: "AGENTS.md"
  enforce_hierarchy: true
  check_duplicates: true

  # Auto-generation
  auto_generate: true
  template_path: "core/AGENTS.template.md"
```

---

### 7. Workflow Orchestration

Configure workflow orchestrator behavior.

```yaml
workflow:
  # Orchestrator behavior
  auto_detect_sprint: true
  auto_configure_agents: true

  # Consistency checks
  run_consistency_checks: true
  enforce_documentation: true

  # Git integration
  auto_create_branches: true
  auto_update_status: true

  # Quality checks
  run_quality_checks: true
  quality_gates:
    - linting
    - testing
    - coverage
    - documentation
```

---

### 8. Logging (Future)

```yaml
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
  format: "json"  # Options: json, text
  output: "proto-gear.log"
  max_size: "10MB"
  backup_count: 5
```

**Note**: Logging configuration planned for v0.4.0.

---

### 9. Performance Settings

```yaml
performance:
  # Caching
  cache_enabled: true
  cache_dir: ".proto-gear/cache"

  # Parallelization
  parallel_execution: true
  max_workers: 4
```

---

### 10. Advanced Settings (Future)

```yaml
advanced:
  # Plugin system (Future)
  plugins_enabled: false
  plugins_dir: "plugins"

  # Custom scripts
  custom_scripts:
    pre_workflow: null
    post_workflow: null

  # Experimental features
  experimental:
    multi_project: false
    ai_suggestions: false
    auto_ticketing: false
```

---

## Complete Example

See `examples/agent-framework.config.yaml` for a fully documented example with all available options.

---

## Configuration Validation

### Current Status (v0.3.0)

⚠️ Configuration validation not yet implemented. Proto Gear loads YAML without schema validation.

### Planned (v0.4.0)

- Schema validation with clear error messages
- Required field checking
- Type validation
- Default value filling

---

## Environment-Specific Configuration

### Development

```yaml
# agent-framework.dev.yaml
testing:
  coverage_threshold: 70  # Lower threshold for dev

logging:
  level: "DEBUG"
```

### Production

```yaml
# agent-framework.prod.yaml
testing:
  coverage_threshold: 90  # Higher threshold for production

logging:
  level: "WARNING"
```

**Usage** (Future):
```bash
pg workflow --config agent-framework.prod.yaml
```

---

## Configuration Migration

### Future Versions

When configuration format changes, migration guides will be provided:

```bash
# Future command
pg config migrate --from 1.0 --to 2.0
```

---

## Troubleshooting

### Configuration Not Loading

**Check**:
1. File named exactly `agent-framework.config.yaml`
2. File in project root (same directory as AGENTS.md)
3. Valid YAML syntax (use YAML validator)

### Defaults Being Used

Proto Gear falls back to defaults if:
- No config file found
- Config file has errors
- Required sections missing

**Solution**: Check Proto Gear output for warnings about config issues.

### Invalid YAML Syntax

**Common Issues**:
```yaml
# ❌ Wrong - no colon
agents
  core

# ✅ Correct - colon after key
agents:
  core:

# ❌ Wrong - inconsistent indentation
agents:
  core:
   - id: backend
    name: "Backend"

# ✅ Correct - consistent indentation (2 spaces)
agents:
  core:
    - id: backend
      name: "Backend"
```

---

## Best Practices

### 1. Start Simple

Begin with minimal config, add options as needed:

```yaml
# Minimal working config
agents:
  core: [...]

git:
  main_branch: "main"
  dev_branch: "development"
```

### 2. Use Examples

Copy from `examples/` folder:
- `minimal-config.yaml` - Bare minimum
- `agent-framework.config.yaml` - Complete example

### 3. Document Custom Settings

Add comments to explain project-specific choices:

```yaml
tickets:
  prefix: "MCAS"  # Mast Cell Activation Syndrome project

testing:
  coverage_threshold: 95  # Medical software requires high coverage
```

### 4. Version Control

Commit configuration to Git:

```bash
git add agent-framework.config.yaml
git commit -m "feat(config): add Proto Gear configuration"
```

### 5. Team Alignment

Ensure team agrees on:
- Branch naming conventions
- Ticket ID format
- Coverage thresholds
- Quality gates

---

## Related Documentation

- [Getting Started](getting-started.md) - Basic usage
- [Branching Strategy](BRANCHING_STRATEGY.md) - Git conventions
- [Examples](../examples/) - Configuration examples

---

*Proto Gear v0.3.0 (Alpha) - Configuration Reference*
