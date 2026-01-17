# Proto Gear Capabilities Index

> **For AI Agents**: This is the master catalog of available capabilities.
> Read this file to discover slash commands, skills, and workflows.

## Quick Navigation

- [Slash Commands](#slash-commands) - **Explicit invocation** via `/command-name`
- [Skills](#skills) - Implicit expertise (always active when relevant)
- [Workflows](#workflows) - Multi-step processes
- [Agents](#agents) - Specialized agent patterns

---

## Slash Commands

> **Explicit invocation** - Human types `/command-name` to trigger

| Command | Syntax | Purpose |
|---------|--------|---------|
| `/create-ticket` | `/create-ticket "title" [--type TYPE]` | Create ticket in PROJECT_STATUS.md |
| `/analyze-coverage` | `/analyze-coverage [--path DIR]` | Analyze test coverage |
| `/generate-changelog` | `/generate-changelog [--since VER]` | Generate CHANGELOG.md |

**Full reference**: [commands/INDEX.md](commands/INDEX.md)

### How AI Agents Execute Slash Commands

When you see a human type `/command-name`:

1. **Recognize**: Input starts with `/` followed by command name
2. **Locate**: Read `commands/{command-name}/COMMAND.md`
3. **Parse**: Extract arguments from user input
4. **Validate**: Check required args are present, optional values are valid
5. **Execute**: Follow the "AI Execution Steps" in the command file exactly
6. **Confirm**: Report completion to user

### Example

```
User: /create-ticket "Add dark mode" --type feature

AI Action:
1. Read commands/create-ticket/COMMAND.md
2. Parse: title="Add dark mode", --type=feature
3. Read PROJECT_STATUS.md, find last_ticket_id=42
4. Calculate next ID: PROJ-043
5. Add ticket to Active Tickets table
6. Increment last_ticket_id to 43
7. Confirm: "Created ticket PROJ-043: Add dark mode"
```

---

## Skills

> **Implicit activation** - AI applies when contextually relevant (no `/` prefix)

Modular, reusable expertise in specific domains:

| Skill | Description | When Active |
|-------|-------------|-------------|
| [testing](skills/testing/SKILL.md) | TDD methodology with red-green-refactor | Writing tests, implementing features, fixing bugs |

**Note**: Skills are NOT invoked with `/`. They're expertise you apply based on context.

---

## Workflows

> **Multi-step processes** - May use slash commands as building blocks

| Workflow | Steps | Relevance |
|----------|-------|-----------|
| [feature-development](workflows/feature-development/WORKFLOW.md) | 7 | Building new features from concept to deployment |

Workflows orchestrate multiple commands and skills together.

---

## Agents

Specialized agent patterns:

*No specialized agents included in this configuration.*

To add specialized agent patterns, re-run `pg init` with the `--with-agents` option.

---

## Slash Commands vs Skills vs Workflows

| Type | Invocation | Nature | Example |
|------|------------|--------|---------|
| **Slash Command** | `/command-name` (explicit) | Discrete action | `/create-ticket "Add auth"` |
| **Skill** | Automatic (implicit) | Continuous expertise | "testing" skill during TDD |
| **Workflow** | Context-based | Multi-step process | "feature-development" for new features |

**Key Insight**:
- **Commands** = Human says "do this specific thing now"
- **Skills** = Expertise AI applies throughout a task
- **Workflows** = Orchestrated sequences (may include commands)

---

## Discovery Workflow

**For AI Agents**: When starting a task:

1. **Check for slash commands** - Did user type `/something`? Execute it.
2. **Read this INDEX.md** - Discover available capabilities
3. **Match task to capabilities** - Find relevant skills/workflows
4. **Load relevant files** - Read the specific .md files
5. **Follow patterns** - Use native tools (git, pytest, npm, etc.)
6. **Update status** - Use `/create-ticket`, `/update-status` as needed

---

## Integration with Core Templates

This capability system **extends** Proto Gear's core templates:

- **AGENTS.md** - Core agent configuration, extended by `.proto-gear/agents/`
- **PROJECT_STATUS.md** - Updated by `/create-ticket`, `/update-status`
- **BRANCHING.md** - Git workflow conventions
- **TESTING.md** - TDD patterns, detailed in `skills/testing/`

---

## Adding Custom Capabilities

### Adding a Slash Command

1. Create `commands/your-command/COMMAND.md`
2. Include: Invocation Syntax, Arguments, AI Execution Steps, Error Handling
3. Update `commands/INDEX.md` to list it
4. Update this INDEX.md Quick Reference table

### Adding a Skill

1. Create `skills/your-skill/SKILL.md`
2. Skills are implicit - describe when to activate
3. Update `skills/INDEX.md` to list it

### Adding a Workflow

1. Create `workflows/your-workflow/WORKFLOW.md`
2. Reference commands and skills used
3. Update `workflows/INDEX.md` to list it

---

## Need More Capabilities?

This is a minimal set. For a complete capability library:

```bash
pg init --with-capabilities=full
```

Includes:
- Additional skills (debugging, code-review, security, performance)
- More workflows (bug-fix, hotfix, release)
- Additional commands (update-status, create-branch)
- Specialized agents (backend, frontend, testing, devops)

---

*Proto Gear Universal Capabilities System v1.1*
*Generated by Proto Gear {{VERSION}}*
