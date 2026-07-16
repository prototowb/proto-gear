"""Argparse construction for the ``pg`` CLI.

Pure command-line surface definition — no business logic. ``build_parser``
returns a fully-configured :class:`argparse.ArgumentParser`; dispatch on the
parsed args lives in :mod:`proto_gear_pkg.cli.app`.
"""

import argparse


def build_parser() -> argparse.ArgumentParser:
    """Build and return the top-level ``pg`` argument parser."""
    from .. import __version__
    from ..modules.engineering import status_commands

    parser = argparse.ArgumentParser(
        description="Proto Gear - AI Agent Framework for Development Workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pg init              Initialize AI agent templates in current project
  pg init --dry-run    Preview what will be created
  pg help              Show detailed help information

For more information, visit: https://github.com/proto-gear/proto-gear
        """,
    )

    # Add version argument
    parser.add_argument(
        "--version", action="version", version=f"Proto Gear v{__version__}"
    )

    # Global module selector (engineering-department modules — ADR-001 Phase B → C).
    # Names which engineering department a module-scoped command targets; omitted
    # means the default (engineering), so the single-module case needs no flag.
    parser.add_argument(
        "--module",
        type=str,
        default=None,
        metavar="NAME",
        help="Target engineering department module (e.g., qa). Default: engineering.",
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Main 'init' command
    init_parser = subparsers.add_parser(
        "init", help="Initialize AI Agent Framework in current project"
    )
    init_parser.add_argument(
        "--dry-run", action="store_true", help="Simulate without creating files"
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Force overwrite existing files without prompting",
    )
    init_parser.add_argument(
        "--with-branching",
        action="store_true",
        help="Generate BRANCHING.md with Git workflow conventions",
    )
    init_parser.add_argument(
        "--ticket-prefix",
        type=str,
        default=None,
        help="Ticket ID prefix (e.g., PROJ, MYAPP). Defaults to project name.",
    )
    init_parser.add_argument(
        "--with-capabilities",
        action="store_true",
        help="Generate .proto-gear/ capability system (skills, workflows, commands)",
    )
    init_parser.add_argument(
        "--profile",
        choices=["frontier", "verbose"],
        default="frontier",
        help=(
            "Capability verbosity: 'frontier' (default) ships slim stubs — the "
            "methodology is left to the model; 'verbose' ships the full playbooks "
            "for smaller/older models. Nothing is lost: re-init with --profile "
            "verbose for the full corpus."
        ),
    )
    init_parser.add_argument(
        "--all",
        action="store_true",
        help="Generate ALL available project templates (TESTING, BRANCHING, CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT)",
    )
    init_parser.add_argument(
        "--no-interactive",
        action="store_true",
        help="Skip interactive wizard (use for automated/scripted setup)",
    )

    # 'help' command for detailed documentation
    help_parser = subparsers.add_parser(
        "help", help="Show detailed help and documentation"
    )

    # 'init-surface' — materialise the selected module's state surface (the
    # generic, department-agnostic counterpart to engineering's `pg init`).
    # Targets the module named by the global --module flag (default engineering).
    init_surface_parser = subparsers.add_parser(
        "init-surface",
        help="Render the selected department module's declared state surface",
    )
    init_surface_parser.add_argument(
        "--force", action="store_true", help="Overwrite the surface if it exists"
    )
    init_surface_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview without writing the file",
    )

    # 'capabilities' command group
    capabilities_parser = subparsers.add_parser(
        "capabilities", help="Browse and search available capabilities"
    )
    capabilities_subparsers = capabilities_parser.add_subparsers(
        dest="capabilities_command", help="Capabilities commands"
    )

    # capabilities list
    capabilities_list_parser = capabilities_subparsers.add_parser(
        "list", help="List all available capabilities"
    )
    capabilities_list_parser.add_argument(
        "--type",
        type=str,
        choices=["skill", "workflow", "command"],
        help="Filter by capability type",
    )
    capabilities_list_parser.add_argument(
        "--tag", type=str, help="Filter by tag (e.g., testing, deployment)"
    )
    capabilities_list_parser.add_argument(
        "--role", type=str, help='Filter by agent role (e.g., "Backend Developer")'
    )
    capabilities_list_parser.add_argument(
        "--status",
        type=str,
        choices=["stable", "beta", "experimental"],
        help="Filter by status",
    )
    capabilities_list_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    # capabilities search
    capabilities_search_parser = capabilities_subparsers.add_parser(
        "search", help="Search capabilities by keyword"
    )
    capabilities_search_parser.add_argument(
        "query", type=str, help="Search query (keyword or phrase)"
    )

    # capabilities show
    capabilities_show_parser = capabilities_subparsers.add_parser(
        "show", help="Show detailed information about a capability"
    )
    capabilities_show_parser.add_argument(
        "name", type=str, help="Capability name (e.g., testing, bug-fix)"
    )

    # capabilities tree
    capabilities_tree_parser = capabilities_subparsers.add_parser(
        "tree", help="Show dependency tree for a capability"
    )
    capabilities_tree_parser.add_argument(
        "capability_id",
        type=str,
        help="Capability ID (e.g., testing, skills/debugging)",
    )

    # 'agent' command group
    agent_parser = subparsers.add_parser("agent", help="Manage agent configurations")
    agent_subparsers = agent_parser.add_subparsers(
        dest="agent_command", help="Agent commands"
    )

    # agent create
    agent_create_parser = agent_subparsers.add_parser(
        "create", help="Create a new agent configuration (interactive or quick mode)"
    )
    agent_create_parser.add_argument(
        "name",
        type=str,
        nargs="?",
        help="Agent name (required for quick/template mode, optional for interactive)",
    )
    agent_create_parser.add_argument(
        "--template",
        type=str,
        metavar="TEMPLATE",
        help="Create from template (e.g., backend-developer, testing-focused)",
    )
    agent_create_parser.add_argument(
        "--capabilities",
        type=str,
        metavar="CAPS",
        help="Comma-separated capabilities (e.g., testing,debugging,feature-development)",
    )
    agent_create_parser.add_argument(
        "--description", type=str, metavar="DESC", help="Agent description"
    )
    agent_create_parser.add_argument(
        "--author", type=str, metavar="AUTHOR", help="Agent author name"
    )
    agent_create_parser.add_argument(
        "--list-templates", action="store_true", help="List all available templates"
    )

    # agent list
    agent_list_parser = agent_subparsers.add_parser(
        "list", help="List configured agents and available bundled agents"
    )
    agent_list_parser.add_argument(
        "--available",
        action="store_true",
        help="Show only bundled agents not yet installed",
    )

    # agent install
    agent_install_parser = agent_subparsers.add_parser(
        "install", help="Install one bundled agent into .proto-gear/agents/"
    )
    agent_install_parser.add_argument(
        "name",
        type=str,
        help="Agent id (filename stem), or <module>/<id> to disambiguate",
    )

    # agent show
    agent_show_parser = agent_subparsers.add_parser(
        "show", help="Show detailed information about an agent"
    )
    agent_show_parser.add_argument(
        "name", type=str, help="Agent name (without .yaml extension)"
    )

    # agent validate
    agent_validate_parser = agent_subparsers.add_parser(
        "validate", help="Validate an agent configuration"
    )
    agent_validate_parser.add_argument(
        "name", type=str, help="Agent name (without .yaml extension)"
    )
    agent_validate_parser.add_argument(
        "--no-recommendations",
        action="store_true",
        help="Skip showing capability recommendations",
    )

    # agent delete
    agent_delete_parser = agent_subparsers.add_parser(
        "delete", help="Delete an agent configuration"
    )
    agent_delete_parser.add_argument(
        "name", type=str, help="Agent name (without .yaml extension)"
    )
    agent_delete_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )

    # agent clone
    agent_clone_parser = agent_subparsers.add_parser(
        "clone", help="Clone an existing agent with a new name"
    )
    agent_clone_parser.add_argument(
        "source", type=str, help="Source agent name to clone from"
    )
    agent_clone_parser.add_argument("destination", type=str, help="New agent name")
    agent_clone_parser.add_argument(
        "--description", type=str, help="Override description for cloned agent"
    )

    # 'orchestration' command group — the paradigm pool
    orchestration_parser = subparsers.add_parser(
        "orchestration",
        help="Browse orchestration paradigms (how sub-agents are distributed)",
        aliases=["paradigm"],
    )
    orchestration_subparsers = orchestration_parser.add_subparsers(
        dest="orchestration_command", help="Orchestration commands"
    )

    # orchestration list
    orchestration_list_parser = orchestration_subparsers.add_parser(
        "list", help="List orchestration paradigms in the pool"
    )
    orchestration_list_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    # orchestration show
    orchestration_show_parser = orchestration_subparsers.add_parser(
        "show", help="Show detailed information about a paradigm"
    )
    orchestration_show_parser.add_argument(
        "id", type=str, help="Paradigm id (e.g. dynamic, driver-reviewer)"
    )
    orchestration_show_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    # orchestration install
    orchestration_install_parser = orchestration_subparsers.add_parser(
        "install", help="Install one paradigm into .proto-gear/orchestration/"
    )
    orchestration_install_parser.add_argument(
        "id",
        type=str,
        help="Paradigm id (filename stem), or <module>/<id> to disambiguate",
    )

    # 'status' command
    status_parser = subparsers.add_parser(
        "status", help="Show project status from PROJECT_STATUS.md"
    )
    status_parser.add_argument(
        "--json", action="store_true", help="Output as JSON (for AI agent consumption)"
    )

    # 'ticket' command group
    ticket_parser = subparsers.add_parser(
        "ticket", help="Manage tickets in PROJECT_STATUS.md"
    )
    ticket_subparsers = ticket_parser.add_subparsers(
        dest="ticket_command", help="Ticket commands"
    )

    # ticket create
    ticket_create_parser = ticket_subparsers.add_parser(
        "create", help="Create a new ticket (prints ticket ID to stdout)"
    )
    ticket_create_parser.add_argument("title", type=str, help="Ticket title")
    ticket_create_parser.add_argument(
        "--type",
        type=str,
        default="task",
        choices=sorted(status_commands.VALID_TYPES),
        help="Ticket type (default: task)",
    )
    ticket_create_parser.add_argument(
        "--assignee", type=str, default="", help="Assignee name (optional)"
    )

    # ticket update
    ticket_update_parser = ticket_subparsers.add_parser(
        "update", help="Update ticket status"
    )
    ticket_update_parser.add_argument(
        "ticket_id", type=str, help="Ticket ID (e.g., PROJ-001)"
    )
    ticket_update_parser.add_argument(
        "--status",
        type=str,
        required=True,
        choices=sorted(status_commands.VALID_STATUSES),
        help="New status",
    )

    # ticket list
    ticket_list_parser = ticket_subparsers.add_parser("list", help="List tickets")
    ticket_list_parser.add_argument(
        "--status",
        type=str,
        default="",
        help="Filter by status (e.g., IN_PROGRESS, PENDING, COMPLETED)",
    )
    ticket_list_parser.add_argument(
        "--json", action="store_true", help="Output as JSON"
    )

    # 'update' command for template updates
    update_parser = subparsers.add_parser(
        "update", help="Update template files while preserving user data"
    )
    update_parser.add_argument(
        "templates",
        nargs="*",
        help="Specific templates to update (e.g., PROJECT_STATUS.md AGENTS.md). If omitted, updates all supported templates.",
    )
    update_parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without modifying files"
    )
    update_parser.add_argument(
        "--force", action="store_true", help="Skip confirmation prompt"
    )
    update_parser.add_argument(
        "--diff-only",
        action="store_true",
        help="Show diff and exit without applying changes",
    )

    # 'sync-context' command
    sync_context_parser = subparsers.add_parser(
        "sync-context",
        help="Regenerate AGENT_CONTEXT.md and mirror into host config files",
    )
    sync_context_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )

    # 'context' command
    context_parser = subparsers.add_parser(
        "context", help="Print AGENT_CONTEXT.md to stdout (for piping into agents)"
    )
    context_parser.add_argument(
        "--regenerate",
        action="store_true",
        help="Regenerate from current state instead of reading existing file",
    )

    # 'suggest' command
    suggest_parser = subparsers.add_parser(
        "suggest",
        help="Match user prose against capability triggers; return top matches",
    )
    suggest_parser.add_argument(
        "prose", nargs="+", help='Task description (e.g., "fix login bug")'
    )
    suggest_parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of suggestions (default: 3)",
    )
    suggest_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    # 'doctor' command
    doctor_parser = subparsers.add_parser(
        "doctor", help="Audit project for proto-gear sync drift"
    )
    doctor_parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON report (for AI agent consumption)",
    )
    doctor_parser.add_argument(
        "--fix",
        action="store_true",
        help="Automatically run `sync-context` to repair sync drift",
    )
    doctor_parser.add_argument(
        "--all", action="store_true", help="Show all checks including ones that passed"
    )

    # 'sync-indexes' command
    sync_indexes_parser = subparsers.add_parser(
        "sync-indexes",
        help="Regenerate .proto-gear/INDEX.md and per-type INDEX.md from metadata.yaml",
    )
    sync_indexes_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )

    # 'module' command group (departmental modules — ADR-001 Phase B)
    module_parser = subparsers.add_parser(
        "module", help="Inspect departmental modules (module.yaml manifests)"
    )
    module_subparsers = module_parser.add_subparsers(
        dest="module_command", help="Module commands"
    )

    module_list_parser = module_subparsers.add_parser(
        "list", help="List departmental modules discovered from module.yaml manifests"
    )
    module_list_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    module_show_parser = module_subparsers.add_parser(
        "show", help="Show a departmental module manifest"
    )
    module_show_parser.add_argument(
        "name", type=str, help="Module id (e.g., engineering)"
    )
    module_show_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    pipeline_parser = subparsers.add_parser(
        "pipeline",
        help="Show the cross-discipline supervision pipeline (path to production)",
    )
    pipeline_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    trace_parser = subparsers.add_parser(
        "trace",
        help="Trace a change (ticket id) across discipline state surfaces",
    )
    trace_parser.add_argument(
        "change_id", type=str, help="Engineering ticket id (e.g., PROTO-054)"
    )
    trace_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )

    release_parser = subparsers.add_parser(
        "release",
        help="Trace a release across its tickets — aggregate readiness verdict",
    )
    release_parser.add_argument(
        "release_id", type=str, help="Release label (e.g., v0.10.0)"
    )
    release_parser.add_argument(
        "--json", action="store_true", help="Emit JSON (for AI agent consumption)"
    )
    release_parser.add_argument(
        "--notes",
        action="store_true",
        help="Generate release notes from the cleared gate checklist",
    )

    return parser
