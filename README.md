# Proto Gear

> Model-agnostic coordination scaffolding for human-AI development teams

[![Version](https://img.shields.io/badge/version-0.8.2-blue)](https://github.com/proto-gear/proto-gear)
[![Status](https://img.shields.io/badge/status-alpha-orange)](docs/dev/readiness-assessment.md)
[![Python](https://img.shields.io/badge/python-3.8%2B-green)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-purple)](LICENSE)

Proto Gear generates a small set of markdown files that give any AI agent — Claude, GPT-4, Cursor, Copilot, Aider, or anything that can read files — a shared understanding of your project's state, workflow conventions, and available tools. Once initialized, a `pg` CLI lets agents (and humans) manipulate that state reliably via shell commands.

**What it is**: A template generator + a thin state-management CLI.
**What it is not**: A workflow execution engine, an agent runtime, or a code generator.

---

## Install

```bash
pip install proto-gear
# or from source
pip install -e .
```

---

## Quick start

```bash
cd my-project
pg init                                          # interactive wizard
pg init --no-interactive --with-branching \
         --ticket-prefix PROJ                    # non-interactive
```

This writes 2–4 markdown files into your project root:

| File | Purpose |
|---|---|
| `AGENTS.md` | Roles, workflow patterns, pre-flight checklist |
| `PROJECT_STATUS.md` | Sprint state, active tickets, single source of truth |
| `BRANCHING.md` | Branch naming + commit conventions (optional) |
| `TESTING.md` | TDD patterns + coverage targets (optional) |

From that point, any AI agent that can read files can follow the coordination protocol — no model-specific plugins required.

---

## State management CLI

Once `PROJECT_STATUS.md` exists, `pg` provides reliable shell commands for reading and writing state. Any AI agent can call these:

```bash
# Show current project state
pg status
pg status --json                                 # machine-readable

# Create a ticket (prints new ID to stdout — capture with $())
pg ticket create "Add search endpoint" --type feature
ID=$(pg ticket create "Fix login redirect" --type bugfix)
echo "Working on $ID"

# Update ticket status
pg ticket update PROJ-001 --status IN_PROGRESS
pg ticket update PROJ-001 --status COMPLETED

# List tickets
pg ticket list
pg ticket list --status IN_PROGRESS
pg ticket list --json
```

The commands parse and write `PROJECT_STATUS.md` directly — no separate database or state file.

---

## How the coordination loop works

1. **Agent reads** `AGENTS.md` → understands roles, checklist, references
2. **Agent reads** `PROJECT_STATUS.md` → knows sprint, active tickets, next ID
3. **Agent calls** `pg ticket create "..."` → ticket ID is written to the file, printed to stdout
4. **Agent works**, commits following `BRANCHING.md` conventions
5. **Agent calls** `pg ticket update PROJ-XXX --status COMPLETED` → file updated
6. **Any other agent or human** runs `pg status` → sees current state

Because the protocol is markdown + shell commands, it works identically across Claude Code, Cursor, GitHub Copilot, Aider, and plain terminal sessions.

---

## Technology detection

`pg init` detects your existing stack and tailors placeholder values — it never modifies your code.

Detected stacks: Node.js (Next.js, React, Vue, Express), Python (Django, FastAPI, Flask), Rust, Go, Ruby, PHP, Java/Kotlin, C#.

---

## Other commands

```bash
pg capabilities list          # browse bundled skills/workflows
pg capabilities show testing  # details for a specific capability
pg agent create               # define a custom agent configuration
pg update                     # refresh templates while preserving ticket data
pg help                       # full documentation
```

---

## Development

```bash
pip install -e .
python -m pytest
pg init --dry-run             # smoke test template generation
```

See [CLAUDE.md](CLAUDE.md) for contributor conventions and [docs/dev/](docs/dev/) for design documents.

---

## License

MIT — see [LICENSE](LICENSE).
