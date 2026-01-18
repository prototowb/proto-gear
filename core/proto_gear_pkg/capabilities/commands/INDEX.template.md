# Slash Commands Reference

> **For AI Agents**: When a human types `/command-name`, find the command here and execute it.

## Quick Reference

| Command | Shortcut | Syntax | Purpose |
|---------|----------|--------|---------|
| `/create-ticket` | `/ct` | `"title" [--type TYPE]` | Create ticket in PROJECT_STATUS.md |
| `/update-status` | `/us` | `<ID> <STATUS> [--reason]` | Update ticket status |
| `/analyze-coverage` | `/ac` | `[--path DIR]` | Analyze test coverage |
| `/generate-changelog` | `/gc` | `[--since VER]` | Generate CHANGELOG.md |

### Shortcuts

For faster invocation, use these shortcuts:

```
/ct  →  /create-ticket
/us  →  /update-status
/ac  →  /analyze-coverage
/gc  →  /generate-changelog
```

**Note**: Shortcuts expand to the full command. Arguments work the same way:
- `/ct "Add auth"` = `/create-ticket "Add auth"`
- `/us PROJ-043 COMPLETED` = `/update-status PROJ-043 COMPLETED`
- `/ac --path src/` = `/analyze-coverage --path src/`

---

## Available Slash Commands

### `/create-ticket`

**Syntax**:
```
/create-ticket "title" [--type TYPE] [--assignee NAME] [--priority LEVEL]
```

**Arguments**:
| Argument | Required | Default | Values |
|----------|----------|---------|--------|
| `title` | Yes | - | Any text in quotes |
| `--type` | No | task | feature, bugfix, hotfix, task |
| `--assignee` | No | Unassigned | Agent or person name |
| `--priority` | No | medium | low, medium, high, critical |

**Examples**:
```
/create-ticket "Add user authentication"
/create-ticket "Fix login bug" --type bugfix --priority high
/create-ticket "Refactor API layer" --type task --assignee "Backend Agent"
```

**File**: [create-ticket/COMMAND.md](create-ticket/COMMAND.md)

---

### `/update-status`

**Syntax**:
```
/update-status <TICKET_ID> <STATUS> [--reason REASON] [--branch BRANCH]
```

**Shortcut**: `/us`

**Arguments**:
| Argument | Required | Default | Values |
|----------|----------|---------|--------|
| `ticket_id` | Yes | - | Ticket ID (e.g., PROJ-043) |
| `status` | Yes | - | PENDING, IN_PROGRESS, COMPLETED, BLOCKED |
| `--reason` | No* | - | Reason for change (*required for BLOCKED) |
| `--branch` | No | auto | Branch name (for IN_PROGRESS) |

**Examples**:
```
/update-status PROJ-043 IN_PROGRESS
/update-status PROJ-043 COMPLETED
/update-status PROJ-043 BLOCKED --reason "Waiting for API spec"
/us PROJ-043 IN_PROGRESS --branch feature/PROJ-043-add-auth
```

**File**: [update-status/COMMAND.md](update-status/COMMAND.md)

---

### `/analyze-coverage`

**Syntax**:
```
/analyze-coverage [--path DIRECTORY] [--threshold NUMBER]
```

**Arguments**:
| Argument | Required | Default | Values |
|----------|----------|---------|--------|
| `--path` | No | . | Directory to analyze |
| `--threshold` | No | 70 | Minimum coverage % |

**Examples**:
```
/analyze-coverage
/analyze-coverage --path src/
/analyze-coverage --threshold 80
```

**File**: [analyze-coverage/COMMAND.md](analyze-coverage/COMMAND.md)

---

### `/generate-changelog`

**Syntax**:
```
/generate-changelog [--since VERSION] [--output FILE]
```

**Arguments**:
| Argument | Required | Default | Values |
|----------|----------|---------|--------|
| `--since` | No | last tag | Version to start from |
| `--output` | No | CHANGELOG.md | Output file path |

**Examples**:
```
/generate-changelog
/generate-changelog --since v1.0.0
/generate-changelog --output docs/CHANGES.md
```

**File**: [generate-changelog/COMMAND.md](generate-changelog/COMMAND.md)

---

## AI Execution Protocol

When you recognize a slash command (input starting with `/`):

### Step 1: Parse the Input

Extract:
- **Command name**: The word after `/` (e.g., `create-ticket`)
- **Required arguments**: Values in quotes or without flags
- **Optional flags**: `--flag value` pairs

**Example parsing**:
```
Input: /create-ticket "Add auth" --type feature --assignee "Backend Agent"

Command: create-ticket
Arguments:
  - title: "Add auth" (required)
  - --type: feature
  - --assignee: "Backend Agent"
```

### Step 2: Locate Command Documentation

Read the command file:
```
.proto-gear/commands/{command-name}/COMMAND.md
```

### Step 3: Validate Arguments

Check against the command's Arguments table:
- Are all required arguments present?
- Are optional values valid (e.g., --type must be feature|bugfix|hotfix|task)?

**If validation fails**: Return the error message from the command's Error Handling section.

### Step 4: Execute AI Execution Steps

Follow the numbered steps in the command's "AI Execution Steps" section exactly.

### Step 5: Confirm Completion

Report the result to the user as specified in the command's Step 6 (or equivalent).

---

## Slash Commands vs Skills

| Aspect | Slash Commands | Skills |
|--------|---------------|--------|
| **Invocation** | Explicit: Human types `/command` | Implicit: AI activates when relevant |
| **Syntax** | `/command-name "arg" --flag value` | No special syntax |
| **Nature** | Discrete, one-time action | Continuous expertise |
| **Duration** | Start → Finish → Done | Active throughout task |
| **Output** | Specific deliverable | Ongoing guidance |
| **Example** | `/create-ticket "Add login"` | "testing" skill active during TDD |

**Key Difference**:
- Slash commands are **explicit instructions** from the human
- Skills are **expertise you apply** based on context

---

## Error Handling

When a slash command fails, report clearly:

```
Error: {specific error message}
Usage: {correct syntax}
```

**Example**:
```
Error: Missing required argument 'title'
Usage: /create-ticket "title" [--type TYPE]
```

---

## Adding Custom Slash Commands

To add a new slash command:

1. **Create directory**: `commands/your-command/`
2. **Create COMMAND.md** with this structure:
   ```markdown
   ---
   name: "Your Command"
   type: "command"
   slash_command: "/your-command"
   arguments:
     required:
       - name: "arg1"
         type: "string"
     optional:
       - name: "--flag"
         type: "enum"
         values: ["a", "b", "c"]
         default: "a"
   ---

   # /your-command

   ## Invocation Syntax
   ## Arguments
   ## AI Execution Steps
   ## Completion Criteria
   ## Error Handling
   ```
3. **Update this INDEX.md** to list the new command

---

## Integration with Workflows

Slash commands are building blocks for workflows:

| Workflow | Uses Commands |
|----------|---------------|
| Feature Development | `/create-ticket` → `/update-status` → `/analyze-coverage` |
| Bug Fix | `/create-ticket` → `/update-status` → testing |
| Code Review Process | `/update-status` (after merge) |
| Release | `/generate-changelog` |
| Incident Response | `/create-ticket` (follow-ups) |
| Migration | `/create-ticket` → `/update-status` |

Workflows **orchestrate** multiple commands; commands are **atomic actions**.

---

*Proto Gear Slash Commands Reference v1.1*
