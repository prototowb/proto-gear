<!-- proto-gear:header
purpose: how proto-gear is built — components, data flow, design principles
read-when: making non-trivial changes to the package, designing new commands, or auditing module boundaries
priority: recommended
defines:
  - what-proto-gear-is
  - components
  - data-flow
  - templates-and-capabilities
  - design-principles
  - non-goals
links:
  - CONTRIBUTING.md
  - docs/dev/project-structure.md
  - docs/dev/universal-capabilities-design.md
-->

# Proto Gear — Architecture

## What Proto Gear Is

Proto Gear is a small Python CLI (`pg`) that does two things:

1. **Generates markdown templates** — `AGENTS.md`, `PROJECT_STATUS.md`, `BRANCHING.md`, `TESTING.md`, etc. — into existing projects so humans and AI agents can collaborate against a shared, structured doc set.
2. **Indexes and surfaces "capabilities"** — skills, workflows, commands, and agent profiles stored as YAML+markdown bundles under `.proto-gear/`. The index is built into `AGENT_CONTEXT.md` and mirrored into host config files (CLAUDE.md, .cursorrules, etc.) so the agent reads it without being prompted.

It is **not** a project scaffolder, a runtime, or an LLM client. It does not execute code that lives in capability bundles; capabilities are documentation an agent reads, not Python it runs.

## Components

```
core/proto_gear_pkg/
├── proto_gear.py              # CLI entry point + argparse + dispatch
├── __init__.py                # canonical __version__ (single source of truth)
│
├── interactive_wizard.py      # `pg init` UI: questionary/rich-based prompts
├── ui_helper.py               # ANSI colour + terminal helpers (Windows-safe)
│
├── cli_commands.py            # handlers for `pg capabilities ...`
├── status_commands.py         # handlers for `pg status` and `pg ticket ...`
│
├── metadata_parser.py         # YAML frontmatter + `proto-gear:header` blocks
├── capability_metadata.py     # loads `.proto-gear/**/metadata.yaml`
├── template_updater.py        # in-place edits to user files (e.g. PROJECT_STATUS)
│
├── sync_context.py            # generates AGENT_CONTEXT.md and mirrors managed block
├── discovery.py               # `pg suggest`: prose → capability ranking
├── doctor.py                  # `pg doctor`: drift detection across context surfaces
│
├── agent_config.py            # `pg agent ...`: load + validate agent profiles
├── agent_wizard.py            # interactive UI for `pg agent create`
├── agent_templates.py         # built-in agent profile templates
│
└── *.template.md              # source-of-truth templates that get customized
                               # on `pg init` (8 core docs + AGENT_CONTEXT)
```

### Module boundaries

| Module | Reads | Writes | Other modules it imports |
|--------|-------|--------|--------------------------|
| `proto_gear.py` | argv | logs to stdout | everything |
| `metadata_parser.py` | text | nothing | `yaml` only |
| `capability_metadata.py` | `.proto-gear/**/metadata.yaml` | nothing | `metadata_parser` |
| `sync_context.py` | `capability_metadata` + project files | AGENT_CONTEXT.md + host configs | `capability_metadata` |
| `discovery.py` | `capability_metadata` | nothing | `capability_metadata` |
| `doctor.py` | everything above | nothing | `sync_context`, `metadata_parser`, `capability_metadata` |

Lower modules never import higher ones. `proto_gear.py` is the only module that calls `sys.exit`.

## Data Flow

### `pg init`

```
argv ─▶ proto_gear.py ─▶ interactive_wizard (or flags)
                              │
                              ▼
                     detect_project_structure()
                     detect_git_config()
                              │
                              ▼
                  read core/proto_gear_pkg/*.template.md
                              │
                              ▼
                 substitute placeholders (project_name,
                 ticket_prefix, generation_date, …)
                              │
                              ▼
                 safe_write_file() to project root
                              │
                              ▼
                 sync_context.sync_context(project_dir)
```

### `pg sync-context`

```
project state ─▶ generate_agent_context() ─▶ AGENT_CONTEXT.md (canonical)
                          │
                          ▼
                _extract_managed_block()
                          │
                          ▼
   for each host file: replace BEGIN..END region; preserve outside content
```

The managed region is fenced by `<!-- proto-gear:agent-context begin -->` / `<!-- proto-gear:agent-context end -->`. Content outside the markers is untouched.

### `pg suggest "<prose>"`

```
prose ─▶ _tokenize()
            │
            ▼
   load_capabilities_for_suggest(project_dir)
   (prefers project's .proto-gear/, falls back to package built-ins)
            │
            ▼
   _score_capability(tokens, prose, cap) for each capability
   scoring: substring trigger match = 3 + len(trigger_tokens)
            single-token overlap     = count of matching tokens
            │
            ▼
   sort desc by score, slice to --limit
            │
            ▼
   stdout (table) or JSON
```

### `pg doctor`

```
                ┌─ check_agent_context_sync     (regenerate, compare, ignore timestamp)
                ├─ check_host_files             (managed block == canonical?)
project_dir ─▶  ├─ check_core_doc_headers       (each .md has proto-gear:header?)
                └─ check_capabilities           (metadata.yaml loads? triggers present?)
                              │
                              ▼
                       DiagnosticsReport
                              │
                  ┌───────────┼──────────────────┐
                  ▼           ▼                  ▼
               stdout    --json output    --fix → sync-context
```

## Templates and Capabilities

### Templates (`*.template.md`)

Eight files in `core/proto_gear_pkg/` are *templates*: text with placeholder tokens like `{{PROJECT_NAME}}` and optional YAML frontmatter for conditional sections. `pg init` reads each, substitutes, and writes to the user's project root. Templates also carry a `proto-gear:header` block that survives substitution and tells future agents what each generated file contains.

### Capabilities (`.proto-gear/<type>/<name>/`)

A capability is a directory containing:

- `metadata.yaml` — name, type (`skill` / `workflow` / `command` / `agent`), version, description, triggers, contexts, dependencies, status.
- One or more markdown files — the content the agent actually reads when the capability fires.

Triggers are the bridge between user prose ("fix login bug") and capability invocation. `pg suggest` and the trigger map in `AGENT_CONTEXT.md` both derive from `metadata.yaml::relevance.triggers`.

## Design Principles

1. **Tech-stack agnostic.** Proto Gear is Python; the projects it serves can be anything. Templates carry no language-specific content beyond what the user asks for via flags or detected project signals.
2. **No code execution from capability bundles.** Capabilities are markdown + YAML. `pg` never `exec`s or `eval`s their contents. Agents may *read* them and act on them; that is the agent's responsibility, not Proto Gear's.
3. **Managed regions, not whole-file rewrites.** When `pg sync-context` updates a host config file, it only modifies content between BEGIN/END markers. Hand-written content outside the markers is preserved.
4. **Templates are documentation, not config.** Generated files like AGENTS.md describe collaboration patterns; they are not loaded by `pg` at runtime. The package itself depends only on `core/proto_gear_pkg/` Python and the template files it ships.
5. **Single source of truth for version.** `pyproject.toml` and `__init__.py::__version__` carry the version literal; every CLI banner and template substitution reads from `__version__`. No hardcoded `"v0.X.Y"` strings.
6. **Single source of truth for the agent index.** `AGENT_CONTEXT.md` is generated from project state on demand. Drift between it, host configs, and templates is surfaced by `pg doctor`, not by silent staleness.
7. **Drift is visible, repairable, and the agent's first signal.** Adding new context surfaces (more host files, more checks) means more potential drift; the answer is always: detect with `doctor`, repair with `sync-context`.

## Non-Goals

- **Project scaffolding.** Proto Gear does not create `package.json`, `pyproject.toml`, or any source code for the host project. Other tools do that better.
- **Tech-stack opinions.** Proto Gear will not tell you to use Poetry over pip, or React over Svelte. It detects what you already have and adapts.
- **Runtime orchestration.** Proto Gear does not start agent processes, route messages, or hold conversation state. AGENTS.md describes patterns; the agent host (Claude Code, Cursor, etc.) executes them.
- **Mandatory CI infrastructure.** Generated `BRANCHING.md` describes conventions; it does not install GitHub Actions or git hooks unless the user runs `/workflows/cicd-setup` on their own.

## Where to Look Next

- **Adding a new CLI command**: `proto_gear.py` (subparser + dispatch) + a handler module + tests. See PROTO-031 / PROTO-033 / PROTO-034 in `PROJECT_STATUS.md` for recent examples.
- **Adding a new template**: drop the file into `core/proto_gear_pkg/*.template.md`, include a `proto-gear:header` block, register placeholders, wire it into the init flow.
- **Adding a new capability check**: extend `doctor.py::run_diagnostics` with a new `check_*` function returning `List[Finding]`.
- **Capability schema design history**: `docs/dev/universal-capabilities-design.md`.
- **Release procedure**: `docs/dev/release-workflow.md`.
