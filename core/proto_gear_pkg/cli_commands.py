#!/usr/bin/env python3
"""
CLI command handlers for Proto Gear capabilities and agents

Provides:
- pg capabilities list/search/show - Browse available capabilities
- pg agent create/list/show/validate/delete - Manage agent configurations
"""

from pathlib import Path
from typing import Optional, List
import sys
import difflib

from .ui_helper import UIHelper, Colors
from .agent_config import (
    AgentManager,
    AgentConfiguration,
    AgentCapabilities,
    AgentValidationError,
    create_agent_template,
)
from .module_core.capability_metadata import (
    load_all_capabilities,
    CapabilityMetadata,
    CapabilityType,
)

ui = UIHelper()


def get_capabilities_dir() -> Path:
    """Get capabilities directory (package location)"""
    pkg_dir = Path(__file__).parent
    return pkg_dir / "capabilities"


def _load_bundled_capabilities():
    """All bundled capabilities across every discipline (seam S1).

    The shared/engineering bundle plus each module's own ``capabilities/``,
    namespaced ``<module>/<cap_id>`` (see ``module_host.load_bundled_capabilities``).
    Browse commands use this so a discipline's capabilities (e.g. qa's
    ``qa/workflows/release-signoff``) are visible, not just engineering's.
    """
    from .module_core import module_host

    return module_host.load_bundled_capabilities()


def _resolve_capability(name, all_caps):
    """Resolve a user-supplied capability name to ``(cap_id, metadata)``.

    Accepts a full id (``skills/testing``, ``qa/workflows/release-signoff``), a
    ``<type>/<name>`` shorthand for shared caps, or a bare trailing name
    (``release-signoff``) when it is unambiguous across disciplines. Returns
    ``(None, candidates)`` when nothing matches (``candidates == []``) or the
    bare name is ambiguous (``len(candidates) > 1``), so the caller can report.
    """
    if name in all_caps:
        return name, all_caps[name]
    for category in ("skills", "workflows", "commands"):
        test_id = f"{category}/{name}"
        if test_id in all_caps:
            return test_id, all_caps[test_id]
    candidates = sorted(
        cid for cid in all_caps if cid == name or cid.endswith(f"/{name}")
    )
    if len(candidates) == 1:
        return candidates[0], all_caps[candidates[0]]
    return None, candidates


def get_agents_dir() -> Path:
    """Get agents directory (project location)"""
    proto_gear_dir = Path(".proto-gear")
    agents_dir = proto_gear_dir / "agents"
    return agents_dir


def get_close_matches(
    query: str, options: List[str], n: int = 3, cutoff: float = 0.6
) -> List[str]:
    """
    Get close matches for a query string using fuzzy matching.

    Args:
        query: The string to match
        options: List of possible matches
        n: Maximum number of suggestions to return
        cutoff: Similarity threshold (0.0 to 1.0)

    Returns:
        List of close matches
    """
    # Use difflib for fuzzy matching
    matches = difflib.get_close_matches(query, options, n=n, cutoff=cutoff)
    return matches


# ============================================================================
# Capabilities Commands
# ============================================================================


def cmd_capabilities_list(args):
    """List all available capabilities"""
    try:
        all_caps = _load_bundled_capabilities()
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    if not all_caps:
        print(f"{Colors.YELLOW}No capabilities found{Colors.ENDC}")
        return 0

    # Apply filters
    filtered_caps = all_caps.copy()

    # Filter by type
    if hasattr(args, "type") and args.type:
        filtered_caps = {
            k: v for k, v in filtered_caps.items() if v.type.value == args.type
        }

    # Filter by tag
    if hasattr(args, "tag") and args.tag:
        tag_lower = args.tag.lower()
        filtered_caps = {
            k: v
            for k, v in filtered_caps.items()
            if any(tag_lower in tag.lower() for tag in v.tags)
        }

    # Filter by role
    if hasattr(args, "role") and args.role:
        role_lower = args.role.lower()
        filtered_caps = {
            k: v
            for k, v in filtered_caps.items()
            if v.agent_roles
            and any(role_lower in role.lower() for role in v.agent_roles)
        }

    # Filter by status
    if hasattr(args, "status") and args.status:
        filtered_caps = {
            k: v for k, v in filtered_caps.items() if v.status.value == args.status
        }

    if not filtered_caps:
        if getattr(args, "json", False):
            import json

            print(json.dumps({"capabilities": []}, indent=2))
            return 0
        print(
            f"{Colors.YELLOW}No capabilities match the specified filters{Colors.ENDC}"
        )
        print(f"\nTry: pg capabilities list (without filters)")
        return 0

    # JSON output path (for AI agent consumption)
    if getattr(args, "json", False):
        import json

        items = []
        for cap_id in sorted(filtered_caps.keys()):
            cap = filtered_caps[cap_id]
            triggers = []
            contexts = []
            if cap.relevance:
                triggers = list(cap.relevance.triggers or [])
                contexts = list(cap.relevance.contexts or [])
            items.append(
                {
                    "id": cap_id,
                    "type": (
                        cap.type.value if hasattr(cap.type, "value") else str(cap.type)
                    ),
                    "name": cap.name,
                    "description": cap.description,
                    "category": cap.category,
                    "status": (
                        cap.status.value
                        if hasattr(cap.status, "value")
                        else str(cap.status)
                    ),
                    "version": cap.version,
                    "tags": list(cap.tags or []),
                    "agent_roles": list(cap.agent_roles or []),
                    "triggers": triggers,
                    "contexts": contexts,
                }
            )
        print(json.dumps({"capabilities": items}, indent=2))
        return 0

    # Group by type
    skills = {}
    workflows = {}
    commands = {}

    for cap_id, metadata in filtered_caps.items():
        if metadata.type == CapabilityType.SKILL:
            skills[cap_id] = metadata
        elif metadata.type == CapabilityType.WORKFLOW:
            workflows[cap_id] = metadata
        elif metadata.type == CapabilityType.COMMAND:
            commands[cap_id] = metadata

    # Display with enhanced formatting
    print(f"\n{Colors.HEADER}=== Proto Gear Capabilities ==={Colors.ENDC}\n")

    if skills:
        # Box header
        print(
            f"{Colors.CYAN}+-- SKILLS ({len(skills)}) " + "-" * 45 + f"+{Colors.ENDC}"
        )
        for cap_id in sorted(skills.keys()):
            metadata = skills[cap_id]
            # Extract short ID (e.g., "skills/testing" -> "testing")
            short_id = cap_id.split("/")[-1]
            status_icon = "[OK]" if metadata.status.value == "stable" else "[!]"
            status_color = (
                Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            )
            # Format: | [OK] short-id          Full Name
            print(
                f"{Colors.CYAN}|{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} "
                + f"{Colors.CYAN}{short_id:18}{Colors.ENDC} {metadata.name}"
            )
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

    if workflows:
        # Box header
        print(
            f"{Colors.CYAN}+-- WORKFLOWS ({len(workflows)}) "
            + "-" * 42
            + f"+{Colors.ENDC}"
        )
        for cap_id in sorted(workflows.keys()):
            metadata = workflows[cap_id]
            short_id = cap_id.split("/")[-1]
            status_icon = "[OK]" if metadata.status.value == "stable" else "[!]"
            status_color = (
                Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            )
            print(
                f"{Colors.CYAN}|{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} "
                + f"{Colors.CYAN}{short_id:18}{Colors.ENDC} {metadata.name}"
            )
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

    if commands:
        # Box header
        print(
            f"{Colors.CYAN}+-- COMMANDS ({len(commands)}) "
            + "-" * 43
            + f"+{Colors.ENDC}"
        )
        for cap_id in sorted(commands.keys()):
            metadata = commands[cap_id]
            short_id = cap_id.split("/")[-1]
            status_icon = "[OK]" if metadata.status.value == "stable" else "[!]"
            status_color = (
                Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            )
            print(
                f"{Colors.CYAN}|{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} "
                + f"{Colors.CYAN}{short_id:18}{Colors.ENDC} {metadata.name}"
            )
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

    # Summary
    filters_applied = []
    if hasattr(args, "type") and args.type:
        filters_applied.append(f"type={args.type}")
    if hasattr(args, "tag") and args.tag:
        filters_applied.append(f"tag={args.tag}")
    if hasattr(args, "role") and args.role:
        filters_applied.append(f"role={args.role}")
    if hasattr(args, "status") and args.status:
        filters_applied.append(f"status={args.status}")

    if filters_applied:
        print(
            f"{Colors.BOLD}Showing: {len(filtered_caps)} of {len(all_caps)} capabilities{Colors.ENDC}"
        )
        print(f"{Colors.GRAY}Filters: {', '.join(filters_applied)}{Colors.ENDC}")
    else:
        print(f"{Colors.BOLD}Total: {len(all_caps)} capabilities{Colors.ENDC}")

    print(f"{Colors.GRAY}Use 'pg capabilities show <name>' to see details{Colors.ENDC}")

    return 0


def _collect_capability_entries() -> List[dict]:
    """Assemble the browse list of capabilities, grouped skills → workflows →
    commands then sorted by id within each group.

    Pure data (no prompts), so it is unit-testable. Each entry:
    ``id`` (full), ``short_id`` (trailing segment), ``type`` (``skill`` /
    ``workflow`` / ``command``), ``name``, ``description``, ``status``.
    """
    all_caps = _load_bundled_capabilities()

    type_order = {
        CapabilityType.SKILL: 0,
        CapabilityType.WORKFLOW: 1,
        CapabilityType.COMMAND: 2,
    }

    def _sort_key(cap_id):
        meta = all_caps[cap_id]
        return (type_order.get(meta.type, 9), cap_id)

    entries: List[dict] = []
    for cap_id in sorted(all_caps.keys(), key=_sort_key):
        meta = all_caps[cap_id]
        entries.append(
            {
                "id": cap_id,
                "short_id": cap_id.split("/")[-1],
                "type": (
                    meta.type.value if hasattr(meta.type, "value") else str(meta.type)
                ),
                "name": meta.name,
                "description": meta.description or "",
                "status": (
                    meta.status.value
                    if hasattr(meta.status, "value")
                    else str(meta.status)
                ),
            }
        )
    return entries


def _capability_entry_label(entry: dict) -> str:
    """One-line label for a capability entry in the browse list."""
    badge = (
        f"{Colors.GREEN}[OK]{Colors.ENDC}"
        if entry["status"] == "stable"
        else f"{Colors.WARNING}[!]{Colors.ENDC}"
    )
    tail = f" — {entry['name']}" if entry["name"] else ""
    return (
        f"{badge} {Colors.GRAY}{entry['type']:<8}{Colors.ENDC} "
        f"{Colors.CYAN}{entry['short_id']}{Colors.ENDC}{tail}"
    )


def cmd_capabilities_browse(args):
    """Interactive browse/select UI over the capability catalog (§5.7).

    UI-first entry point for ``pg capabilities`` with no subcommand: navigate
    skills / workflows / commands and pick one to view its detail (and, on
    request, its dependency tree). Degrades to the classic ``pg capabilities
    list`` without a TTY or without ``questionary``, so scripts/CI are
    unaffected.
    """
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    try:
        import questionary
    except Exception:
        questionary = None

    if not interactive or questionary is None:
        return cmd_capabilities_list(args)

    try:
        entries = _collect_capability_entries()
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    if not entries:
        print(f"{Colors.YELLOW}No capabilities found.{Colors.ENDC}")
        return 0

    while True:
        choices = [
            questionary.Choice(_capability_entry_label(e), value=i)
            for i, e in enumerate(entries)
        ]
        choices.append(questionary.Choice("Quit", value="__quit__"))
        selection = questionary.select(
            "Capabilities — skills, workflows, commands (select to view):",
            choices=choices,
        ).ask()

        if selection is None or selection == "__quit__":
            return 0

        entry = entries[selection]
        cmd_capabilities_show(_args_ns(name=entry["id"]))
        view_tree = questionary.confirm(
            f"Show dependency tree for '{entry['short_id']}'?",
            default=False,
        ).ask()
        if view_tree:
            cmd_capabilities_tree(_args_ns(capability_id=entry["id"]))


def cmd_capabilities_search(args):
    """Search capabilities by keyword"""
    query = args.query.lower()

    try:
        all_caps = _load_bundled_capabilities()
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    # Search in name, description, tags, and trigger keywords
    matches = []
    for cap_id, metadata in all_caps.items():
        if (
            query in metadata.name.lower()
            or query in metadata.description.lower()
            or any(query in tag.lower() for tag in metadata.tags)
            or (metadata.relevance and metadata.relevance.matches_trigger(query))
        ):
            matches.append((cap_id, metadata))

    if not matches:
        print(f"{Colors.YELLOW}No capabilities found matching '{query}'{Colors.ENDC}")
        return 0

    print(
        f"\n{Colors.HEADER}=== Search Results for '{query}' ({len(matches)} found) ==={Colors.ENDC}\n"
    )

    for cap_id, metadata in sorted(matches, key=lambda x: x[0]):
        print(f"{Colors.CYAN}{metadata.name}{Colors.ENDC} ({cap_id})")
        print(f"  {metadata.description}")
        print(
            f"  Status: {metadata.status.value} | Tags: {', '.join(metadata.tags[:5])}"
        )
        print()

    return 0


def cmd_capabilities_show(args):
    """Show detailed information about a capability"""
    name = args.name

    try:
        all_caps = _load_bundled_capabilities()
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    # Resolve name → id: full id, <type>/<name> shorthand, or an unambiguous
    # bare trailing name across disciplines (e.g. qa/workflows/release-signoff).
    cap_id, resolved = _resolve_capability(name, all_caps)
    if cap_id is not None:
        metadata = resolved
    else:
        metadata = None
        candidates = resolved  # list of colliding ids (empty if no match)
        if len(candidates) > 1:
            print(
                f"{Colors.YELLOW}Ambiguous capability '{name}' — "
                f"matches multiple disciplines:{Colors.ENDC}"
            )
            for cid in candidates:
                print(f"  {cid}")
            print(
                f"\n{Colors.GRAY}Qualify it, e.g. "
                f"'pg capabilities show {candidates[0]}'{Colors.ENDC}"
            )
            return 1

    if not metadata:
        print(f"{Colors.FAIL}Capability not found: '{name}'{Colors.ENDC}\n")

        # Suggest similar capabilities using fuzzy matching
        all_cap_ids = list(all_caps.keys())
        # Also extract short names for matching
        short_names = [cap_id.split("/")[-1] for cap_id in all_cap_ids]
        all_searchable = all_cap_ids + short_names

        suggestions = get_close_matches(name, all_searchable, n=3, cutoff=0.6)
        if suggestions:
            print(f"{Colors.BOLD}Did you mean:{Colors.ENDC}")
            for suggestion in suggestions[:3]:
                # If it's a short name, find the full ID
                if "/" not in suggestion:
                    matching_ids = [
                        cid for cid in all_cap_ids if cid.endswith(f"/{suggestion}")
                    ]
                    full_id = matching_ids[0] if matching_ids else suggestion
                else:
                    full_id = suggestion

                if full_id in all_caps:
                    cap_name = all_caps[full_id].name
                    print(f"  - {suggestion} ({cap_name})")
                else:
                    print(f"  - {suggestion}")
            print()

        print(f"Use 'pg capabilities list' to see all capabilities")
        return 1

    # Display detailed information
    print(f"\n{Colors.HEADER}=== {metadata.name} ==={Colors.ENDC}\n")
    print(f"ID: {cap_id}")
    print(f"Type: {metadata.type.value}")
    print(f"Version: {metadata.version}")
    print(f"Status: {metadata.status.value}")
    print(f"\n{Colors.CYAN}Description:{Colors.ENDC}")
    print(f"  {metadata.description}")

    if metadata.category:
        print(f"\nCategory: {metadata.category}")

    if metadata.tags:
        print(f"Tags: {', '.join(metadata.tags)}")

    if metadata.agent_roles:
        print(f"\n{Colors.CYAN}Recommended for:{Colors.ENDC}")
        for role in metadata.agent_roles[:5]:
            print(f"  - {role}")
        if len(metadata.agent_roles) > 5:
            print(f"  ... and {len(metadata.agent_roles) - 5} more")

    # Dependencies
    if metadata.dependencies.required:
        print(f"\n{Colors.CYAN}Required Dependencies:{Colors.ENDC}")
        for dep in metadata.dependencies.required:
            print(f"  - {dep}")

    if metadata.dependencies.optional:
        print(f"\n{Colors.CYAN}Optional Dependencies:{Colors.ENDC}")
        for dep in metadata.dependencies.optional:
            print(f"  - {dep}")

    if metadata.dependencies.suggested:
        print(f"\n{Colors.CYAN}Suggested With:{Colors.ENDC}")
        for dep in metadata.dependencies.suggested:
            print(f"  - {dep}")

    if metadata.composable_with:
        print(f"\n{Colors.CYAN}Composable With:{Colors.ENDC}")
        for comp in metadata.composable_with[:10]:
            print(f"  - {comp}")
        if len(metadata.composable_with) > 10:
            print(f"  ... and {len(metadata.composable_with) - 10} more")

    if metadata.conflicts:
        print(f"\n{Colors.WARNING}Conflicts With:{Colors.ENDC}")
        for conflict in metadata.conflicts:
            print(f"  - {conflict}")

    # Supervision gates (workflows) — explicit human approval points
    if metadata.workflow and metadata.workflow.gates:
        print(f"\n{Colors.CYAN}Supervision Gates (human approval):{Colors.ENDC}")
        for g in metadata.workflow.gates:
            req = "required" if g.required else "optional"
            loc = f", before {g.before}" if g.before else ""
            # ADR-002 primitives shown only when they deviate from §4 defaults,
            # so the common all-human gate stays a one-glance line.
            auth = f", authority: {g.authority}" if g.authority != "human" else ""
            actor = f", actor: {g.actor}" if g.actor else ""
            ev = (
                f", evidence: {g.evidence} {g.evidence_predicate} {g.evidence_value}"
                if g.evidence_predicate != "non-empty"
                else ""
            )
            print(
                f"  - {Colors.BOLD}{g.id}{Colors.ENDC} "
                f"({g.approver}, {req}{loc}{auth}{actor}{ev})"
            )
            print(f"      {g.description}")

    return 0


def cmd_capabilities_tree(args):
    """Show dependency tree for a capability"""
    cap_id = args.capability_id

    # Load all capabilities
    try:
        all_caps = _load_bundled_capabilities()
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    # Resolve name → id (full id, <type>/<name>, or unambiguous bare name).
    full_id, resolved = _resolve_capability(cap_id, all_caps)
    if full_id is not None:
        metadata = resolved
    else:
        metadata = None
        candidates = resolved  # list of colliding ids (empty if no match)
        if len(candidates) > 1:
            print(
                f"{Colors.YELLOW}Ambiguous capability '{cap_id}' — "
                f"matches multiple disciplines:{Colors.ENDC}"
            )
            for cid in candidates:
                print(f"  {cid}")
            print(
                f"\n{Colors.GRAY}Qualify it, e.g. "
                f"'pg capabilities tree {candidates[0]}'{Colors.ENDC}"
            )
            return 1

    if not metadata:
        print(f"{Colors.FAIL}Capability not found: '{cap_id}'{Colors.ENDC}\n")

        # Suggest similar capabilities using fuzzy matching
        all_cap_ids = list(all_caps.keys())
        # Also extract short names for matching
        short_names = [cid.split("/")[-1] for cid in all_cap_ids]
        all_searchable = all_cap_ids + short_names

        suggestions = get_close_matches(cap_id, all_searchable, n=3, cutoff=0.6)
        if suggestions:
            print(f"{Colors.BOLD}Did you mean:{Colors.ENDC}")
            for suggestion in suggestions[:3]:
                # If it's a short name, find the full ID
                if "/" not in suggestion:
                    matching_ids = [
                        cid for cid in all_cap_ids if cid.endswith(f"/{suggestion}")
                    ]
                    full_id = matching_ids[0] if matching_ids else suggestion
                else:
                    full_id = suggestion

                if full_id in all_caps:
                    cap_name = all_caps[full_id].name
                    print(f"  - {suggestion} ({cap_name})")
                else:
                    print(f"  - {suggestion}")
            print()

        print(f"Use 'pg capabilities list' to see all capabilities")
        return 1

    # Print header with box
    print(
        f"\n{Colors.CYAN}+-- Dependency Tree: {metadata.name} "
        + "-" * (40 - len(metadata.name))
        + f"+{Colors.ENDC}"
    )
    print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Show capability info
    print(
        f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}{full_id}{Colors.ENDC} - {metadata.description}"
    )
    print(
        f"{Colors.CYAN}|{Colors.ENDC} Type: {metadata.type.value} | Status: {metadata.status.value}"
    )
    print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Show dependencies
    has_dependencies = False

    if metadata.dependencies.required:
        has_dependencies = True
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}Required Dependencies:{Colors.ENDC}"
        )
        for dep in metadata.dependencies.required:
            dep_name = all_caps[dep].name if dep in all_caps else dep
            print(f"{Colors.CYAN}|{Colors.ENDC}   - {dep} ({dep_name})")
        print(f"{Colors.CYAN}|{Colors.ENDC}")

    if metadata.dependencies.optional:
        has_dependencies = True
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}Optional Dependencies:{Colors.ENDC}"
        )
        for dep in metadata.dependencies.optional:
            dep_name = all_caps[dep].name if dep in all_caps else dep
            print(f"{Colors.CYAN}|{Colors.ENDC}   - {dep} ({dep_name})")
        print(f"{Colors.CYAN}|{Colors.ENDC}")

    if metadata.dependencies.suggested:
        has_dependencies = True
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}Suggested Capabilities:{Colors.ENDC}"
        )
        for dep in metadata.dependencies.suggested:
            dep_name = all_caps[dep].name if dep in all_caps else dep
            print(f"{Colors.CYAN}|{Colors.ENDC}   - {dep} ({dep_name})")
        print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Show composable capabilities
    if metadata.composable_with:
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}Composable With:{Colors.ENDC} {len(metadata.composable_with)} capabilities"
        )
        for comp in metadata.composable_with[:5]:
            comp_name = all_caps[comp].name if comp in all_caps else comp
            print(f"{Colors.CYAN}|{Colors.ENDC}   - {comp} ({comp_name})")
        if len(metadata.composable_with) > 5:
            print(
                f"{Colors.CYAN}|{Colors.ENDC}   ... and {len(metadata.composable_with) - 5} more"
            )
        print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Show conflicts
    if metadata.conflicts:
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.WARNING}Conflicts With:{Colors.ENDC}"
        )
        for conflict in metadata.conflicts:
            conflict_name = (
                all_caps[conflict].name if conflict in all_caps else conflict
            )
            print(f"{Colors.CYAN}|{Colors.ENDC}   - {conflict} ({conflict_name})")
        print(f"{Colors.CYAN}|{Colors.ENDC}")

    if not has_dependencies and not metadata.composable_with and not metadata.conflicts:
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.GRAY}No dependencies or relationships defined{Colors.ENDC}"
        )
        print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Print footer
    print(f"{Colors.CYAN}+-- " + "-" * 60 + f"+{Colors.ENDC}")

    # Show usage tip
    print(f"\n{Colors.BOLD}Quick actions:{Colors.ENDC}")
    print(f"  pg capabilities show {cap_id}  - View full details")
    print(f"  pg agent create --capabilities {cap_id},...  - Use in new agent")

    return 0


# ============================================================================
# Agent Commands
# ============================================================================


def _print_available_agents(agents_dir: Path) -> None:
    """Render the bundled agents not yet installed in this host (PROTO-076).

    Surfaces discoverable agents *before* install — previously a discipline's
    agent appeared only after `pg init` swept it in. Silent when everything
    discoverable is already installed.
    """
    from .module_core import module_host

    installed = (
        {p.stem for p in agents_dir.glob("*.yaml")} if agents_dir.exists() else set()
    )
    available = [
        r for r in module_host.list_bundled_agents() if r["name"] not in installed
    ]
    if not available:
        return

    print(f"\n{Colors.BOLD}Available bundled agents (not installed):{Colors.ENDC}")
    for r in available:
        source = r["module"] or "shared"
        desc = f" — {r['description']}" if r["description"] else ""
        print(
            f"  {Colors.CYAN}{r['name']:<24}{Colors.ENDC} "
            f"{Colors.GRAY}[{source}]{Colors.ENDC}{desc}"
        )
    print(f"\n  Install one with: pg agent install <name>")


def cmd_agent_list(args):
    """List configured agents, plus the bundled ones available to install."""
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    if getattr(args, "available", False):
        # Filtered view: only what could be installed.
        _print_available_agents(agents_dir)
        return 0

    if not agents_dir.exists():
        print(f"{Colors.YELLOW}No agents directory found.{Colors.ENDC}")
        print(f"Create agents with: pg agent create <name>")
        _print_available_agents(agents_dir)
        return 0

    try:
        manager = AgentManager(agents_dir, caps_dir)
        agents = manager.list_agents()
    except Exception as e:
        print(f"{Colors.FAIL}Error loading agents: {e}{Colors.ENDC}")
        return 1

    if not agents:
        print(f"{Colors.YELLOW}No agents configured.{Colors.ENDC}")
        print(f"Create agents with: pg agent create <name>")
        _print_available_agents(agents_dir)
        return 0

    # Print header with box
    print(
        f"\n{Colors.CYAN}+-- Configured Agents ({len(agents)}) "
        + "-" * 40
        + f"+{Colors.ENDC}"
    )
    print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Print table header
    print(
        f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}NAME{' ' * 16}CAPABILITIES  STATUS{Colors.ENDC}        "
    )
    print(f"{Colors.CYAN}|{Colors.ENDC} " + "-" * 54)

    # Print agents in table format
    for agent in agents:
        # Calculate capabilities count
        cap_count = len(agent.capabilities.all_capabilities())
        cap_text = f"{cap_count} caps"

        # Validate agent to get status
        try:
            errors, warnings = manager.validate_agent(agent)
            if errors:
                status_icon = f"{Colors.FAIL}[X]{Colors.ENDC}"
                status_text = "Invalid"
            elif warnings:
                status_icon = f"{Colors.WARNING}[!]{Colors.ENDC}"
                status_text = "Warnings"
            else:
                status_icon = f"{Colors.GREEN}[OK]{Colors.ENDC}"
                status_text = "Valid"
        except Exception:
            status_icon = f"{Colors.FAIL}[X]{Colors.ENDC}"
            status_text = "Error"

        # Format name column (20 chars wide)
        name_display = agent.name[:18] if len(agent.name) > 18 else agent.name
        name_padding = " " * (20 - len(name_display))

        # Format capabilities column (14 chars wide)
        cap_padding = " " * (14 - len(cap_text))

        # Print row
        print(
            f"{Colors.CYAN}|{Colors.ENDC} {Colors.CYAN}{name_display}{Colors.ENDC}"
            f"{name_padding}{cap_text}{cap_padding}{status_icon} {status_text}"
        )

    # Print footer
    print(f"{Colors.CYAN}|{Colors.ENDC}")
    print(f"{Colors.CYAN}+-- " + "-" * 60 + f"+{Colors.ENDC}")

    # Print quick actions
    print(f"\n{Colors.BOLD}Quick actions:{Colors.ENDC}")
    print(f"  pg agent show <name>      - View configuration details")
    print(f"  pg agent validate <name>  - Check for configuration issues")
    print(f"  pg agent clone <src> <dst> - Duplicate an agent")

    # Discoverable-but-not-installed bundled agents ride the same view, so a
    # discipline's agent is visible before `pg init`/install (UI-first, §5.7).
    _print_available_agents(agents_dir)

    return 0


def _pg_version() -> str:
    """Installed Proto Gear version, or ``""`` if it can't be read."""
    try:
        from proto_gear_pkg import __version__

        return __version__
    except Exception:
        return ""


def _rich_console_or_none():
    """A ``rich`` Console if the library is importable, else ``None``.

    The shell degrades to plain ``print`` without rich — the header is chrome,
    never load-bearing.
    """
    try:
        from rich.console import Console

        return Console()
    except Exception:
        return None


def _clear_screen(console) -> None:
    """Clear the terminal for the single-page shell. Guarded — a clear that
    can't run (unusual terminal) degrades to no-op rather than crashing."""
    try:
        if console is not None:
            console.clear()
        else:
            import os

            os.system("cls" if os.name == "nt" else "clear")
    except Exception:
        pass


def _pause() -> None:
    """Hold an action's output on screen until the user acknowledges, so the
    next clear-and-redraw doesn't wipe it unread. EOF/interrupt just continue."""
    try:
        input(f"\n{Colors.GRAY}  ↵  Enter to return to the menu…{Colors.ENDC}")
    except (EOFError, KeyboardInterrupt, OSError):
        # EOF/interrupt, or a non-interactive stdin (e.g. captured under tests).
        pass


def _render_home_header(console, crumb: str) -> None:
    """Persistent frame drawn above each menu: version, project, breadcrumb."""
    version = _pg_version()
    project = Path.cwd().name
    tag = f"v{version}" if version else ""
    if console is not None:
        try:
            from rich.rule import Rule

            console.print()
            console.print(
                f"[bold cyan]Proto Gear[/bold cyan] [dim]{tag}[/dim]"
                f"[dim]{'   ' + project if project else ''}[/dim]"
            )
            if crumb:
                console.print(f"[dim]{crumb}[/dim]")
            console.print(Rule(style="dim"))
            return
        except Exception:
            # Chrome must never crash the menu (e.g. a legacy Windows console
            # that can't encode box-drawing). Fall through to plain ASCII.
            pass
    print(f"\nProto Gear {tag}   {project}".rstrip())
    if crumb:
        print(crumb)
    print("-" * 50)


def _doctor_badge() -> str:
    """A short drift-status badge for the Doctor row (``2 warnings`` / ``ok``).

    Runs the same diagnostics as ``pg doctor`` once, when the home screen is
    built. Fully guarded: any failure (e.g. run outside an initialised project)
    yields no badge rather than breaking the menu.
    """
    try:
        from .module_core import doctor

        report = doctor.run_diagnostics(Path("."))
    except Exception:
        return ""
    if report.errors:
        return f"{report.errors} error{'s' if report.errors != 1 else ''}"
    if report.warnings:
        return f"{report.warnings} warning{'s' if report.warnings != 1 else ''}"
    return "ok"


def _action_doctor() -> None:
    """Run the drift audit and print a concise, coloured summary."""
    try:
        from .module_core import doctor

        report = doctor.run_diagnostics(Path("."))
    except Exception as exc:  # pragma: no cover - defensive
        print(f"{Colors.FAIL}Doctor could not run: {exc}{Colors.ENDC}")
        return

    icon = {
        "ok": f"{Colors.GREEN}✓{Colors.ENDC}",
        "warning": f"{Colors.YELLOW}!{Colors.ENDC}",
        "error": f"{Colors.FAIL}✗{Colors.ENDC}",
    }
    print(
        f"\n{Colors.BOLD}Doctor{Colors.ENDC}  "
        f"{Colors.GREEN}{report.ok} ok{Colors.ENDC}  "
        f"{Colors.YELLOW}{report.warnings} warn{Colors.ENDC}  "
        f"{Colors.FAIL}{report.errors} error{Colors.ENDC}"
    )
    for finding in report.findings:
        if finding.severity == "ok":
            continue
        mark = icon.get(finding.severity, "-")
        print(
            f"  {mark} {finding.target}{Colors.GRAY} — {finding.message}{Colors.ENDC}"
        )
        if finding.fix_hint:
            print(f"      {Colors.GRAY}fix: {finding.fix_hint}{Colors.ENDC}")
    if report.warnings == 0 and report.errors == 0:
        print(f"  {Colors.GREEN}No drift — everything in sync.{Colors.ENDC}")


def _action_ticket_create() -> None:
    """Pick-and-fill a new ticket, then dispatch to ``cmd_ticket_create``."""
    import questionary
    from .modules.engineering import status_commands as sc

    title = questionary.text("Ticket title:").ask()
    if not title or not title.strip():
        return
    ticket_type = questionary.select(
        "Type:", choices=sorted(sc.VALID_TYPES), default="task"
    ).ask()
    if ticket_type is None:
        return
    sc.cmd_ticket_create(_args_ns(title=title.strip(), type=ticket_type, assignee=None))


def _action_ticket_update() -> None:
    """Pick an active ticket and a new status, then dispatch the update."""
    import questionary
    from .modules.engineering import status_commands as sc

    path = sc._find_status_file()
    active = sc.ProjectState(path).active if path else []
    if not active:
        print(f"{Colors.GRAY}No active tickets to update.{Colors.ENDC}")
        return

    ticket = questionary.select(
        "Which ticket?",
        choices=[
            questionary.Choice(
                f"{t.get('ID', '?')} — {t.get('Title', '')}", value=t.get("ID")
            )
            for t in active
        ],
    ).ask()
    if not ticket:
        return
    status = questionary.select("New status:", choices=sorted(sc.VALID_STATUSES)).ask()
    if not status:
        return
    sc.cmd_ticket_update(_args_ns(ticket_id=ticket, status=status))


def _tickets_screen():
    """Tickets sub-screen: list / create / update (the multi-level example)."""
    from .module_core import nav
    from .modules.engineering import status_commands as sc

    return nav.MenuScreen(
        title="Tickets",
        prompt="Tickets —",
        items=[
            nav.MenuItem(
                "list",
                "List",
                "active + blocked",
                action=lambda: sc.cmd_ticket_list(_args_ns(status="", json=False)),
            ),
            nav.MenuItem(
                "create", "Create", "new ticket", action=_action_ticket_create
            ),
            nav.MenuItem(
                "update", "Update", "change status", action=_action_ticket_update
            ),
        ],
    )


def _action_release() -> None:
    """Prompt for a release label and show its readiness verdict."""
    import questionary

    label = questionary.text("Release label (e.g. v0.10.0):").ask()
    if label and label.strip():
        cmd_release(_args_ns(release_id=label.strip(), json=False, notes=False))


def _run_pg(*pg_args: str) -> None:
    """Spawn the real ``pg`` subcommand in this terminal, then return.

    Setup actions (the ``init`` wizard, ``sync-context``, ``hooks install``)
    reuse the exact CLI code path rather than reimplementing its rendering. The
    child inherits this process's stdio, so the interactive init wizard keeps a
    real TTY. Invoked via ``python -m proto_gear_pkg`` so it never depends on the
    ``pg`` script being on ``PATH``.
    """
    import subprocess

    try:
        subprocess.run([sys.executable, "-m", "proto_gear_pkg", *pg_args])
    except Exception as exc:  # pragma: no cover - defensive
        joined = " ".join(pg_args)
        print(f"{Colors.FAIL}Could not run 'pg {joined}': {exc}{Colors.ENDC}")


def _setup_screen():
    """Setup sub-screen: init/re-init, sync context, install branch-guard hook.

    Each row shells out to the real subcommand (see :func:`_run_pg`) so behaviour
    matches ``pg init`` / ``pg sync-context`` / ``pg hooks install`` exactly.
    """
    from .module_core import nav

    return nav.MenuScreen(
        title="Setup",
        prompt="Setup —",
        items=[
            nav.MenuItem(
                "init",
                "Init / re-init",
                "scaffold or refresh this project",
                action=lambda: _run_pg("init"),
            ),
            nav.MenuItem(
                "sync",
                "Sync context",
                "regenerate AGENT_CONTEXT + host configs",
                action=lambda: _run_pg("sync-context"),
            ),
            nav.MenuItem(
                "hooks",
                "Install hook",
                "branch-guard pre-commit hook",
                action=lambda: _run_pg("hooks", "install"),
            ),
        ],
    )


def _build_home_screen():
    """Assemble the root screen. Badges are computed once, here."""
    from .module_core import nav
    from .modules.engineering import status_commands as sc

    return nav.MenuScreen(
        title="Home",
        prompt="Proto Gear — where to?",
        items=[
            nav.MenuItem(
                "status",
                "Status",
                "current project state",
                action=lambda: sc.cmd_status(_args_ns(json=False)),
            ),
            nav.MenuItem(
                "capabilities",
                "Capabilities",
                "skills / workflows / commands",
                action=lambda: cmd_capabilities_browse(
                    _args_ns(capabilities_command=None)
                ),
            ),
            nav.MenuItem(
                "agents",
                "Agents",
                "installed + available",
                action=lambda: cmd_agent_browse(_args_ns(agent_command=None)),
            ),
            nav.MenuItem(
                "paradigms",
                "Orchestration",
                "how sub-agents are distributed",
                action=lambda: cmd_orchestration_browse(
                    _args_ns(orchestration_command=None)
                ),
            ),
            nav.MenuItem(
                "lessons",
                "Lessons",
                "accumulated knowledge",
                action=lambda: cmd_lessons_browse(
                    _args_ns(lessons_command=None, json=False)
                ),
            ),
            nav.MenuItem(
                "tickets", "Tickets", "list · create · update", submenu=_tickets_screen
            ),
            nav.MenuItem(
                "setup", "Setup", "init · sync context · hooks", submenu=_setup_screen
            ),
            nav.MenuItem(
                "doctor",
                "Doctor",
                "drift audit",
                badge=_doctor_badge(),
                action=_action_doctor,
            ),
            nav.MenuItem(
                "release", "Release", "readiness for a label", action=_action_release
            ),
        ],
    )


def cmd_home_menu(args):
    """Top-level interactive home menu (§5.7) — bare ``pg`` in a TTY.

    The UI-first entry point to the whole tool: a navigable *navigate-and-pick*
    shell (single-page: clear-and-redraw each screen, persistent header,
    breadcrumbs, back-nav) over project state, the
    capability/agent/orchestration/lessons browsers, ticket actions, a drift
    audit, and release readiness — instead of a static command list. The caller
    (``cli.app``) only routes here when interactive and ``questionary`` is
    importable; without a TTY it keeps the classic splash, so scripts/CI are
    unaffected.
    """
    from .module_core import nav

    console = _rich_console_or_none()
    return nav.run_menu(
        _build_home_screen(),
        render_header=lambda crumb: _render_home_header(console, crumb),
        clear=lambda: _clear_screen(console),
        pause=_pause,
    )


# ============================================================================
# Lessons — the agent-writable accumulated-knowledge layer (§5.7 browser)
# ============================================================================


def _collect_lesson_entries(project_dir: Optional[Path] = None) -> List[dict]:
    """Assemble the lessons list for browse/list. Pure data (unit-testable).

    Each entry: ``filename``, ``title``, ``summary``, ``path`` (str), sorted by
    filename (``load_lessons`` sorts). Empty when no lessons directory exists or
    it holds no well-formed lessons.
    """
    from .module_core import lessons as lessons_module

    base = Path(project_dir) if project_dir is not None else Path(".")
    lessons_dir = base / ".proto-gear" / lessons_module.LESSONS_DIRNAME

    entries: List[dict] = []
    for lesson in lessons_module.load_lessons(lessons_dir):
        entries.append(
            {
                "filename": lesson.filename,
                "title": lesson.title,
                "summary": lesson.summary,
                "path": str(lesson.path),
            }
        )
    return entries


def _lesson_entry_label(entry: dict) -> str:
    """One-line label for a lesson in the browse list."""
    tail = (
        f" {Colors.GRAY}— {entry['summary']}{Colors.ENDC}" if entry["summary"] else ""
    )
    return f"{Colors.CYAN}{entry['title']}{Colors.ENDC}{tail}"


def _resolve_lesson(slug, entries: List[dict]) -> Optional[dict]:
    """Resolve a slug to a lesson entry: filename (with or without ``.md``), or
    a case-insensitive exact title match. Returns the entry, or ``None``."""
    s_lower = str(slug).strip().lower()
    for entry in entries:
        fn_lower = entry["filename"].lower()
        if s_lower == fn_lower or s_lower + ".md" == fn_lower:
            return entry
    for entry in entries:
        if s_lower == entry["title"].lower():
            return entry
    return None


def cmd_lessons_list(args):
    """List accumulated lessons (title + summary). ``--json`` for agents."""
    entries = _collect_lesson_entries()

    if getattr(args, "json", False):
        import json

        print(json.dumps(entries, indent=2))
        return 0

    if not entries:
        print(
            f"{Colors.YELLOW}No lessons recorded yet.{Colors.ENDC} "
            f"{Colors.GRAY}Write one under .proto-gear/lessons/ when you learn "
            f"something worth keeping.{Colors.ENDC}"
        )
        return 0

    print(f"\n{Colors.HEADER}=== Lessons ({len(entries)}) ==={Colors.ENDC}\n")
    for entry in entries:
        print(
            f"{Colors.CYAN}{entry['title']}{Colors.ENDC} "
            f"{Colors.GRAY}({entry['filename']}){Colors.ENDC}"
        )
        if entry["summary"]:
            print(f"  {entry['summary']}")
        print()
    print(
        f"{Colors.GRAY}Use 'pg lessons show <name>' to read one in full.{Colors.ENDC}"
    )
    return 0


def cmd_lessons_show(args):
    """Print a lesson's full content, resolved by filename or title."""
    entries = _collect_lesson_entries()
    if not entries:
        print(f"{Colors.YELLOW}No lessons recorded yet.{Colors.ENDC}")
        return 0

    entry = _resolve_lesson(args.name, entries)
    if entry is None:
        print(f"{Colors.YELLOW}No lesson matching '{args.name}'.{Colors.ENDC}")
        print(
            f"{Colors.GRAY}Try 'pg lessons list' to see available lessons.{Colors.ENDC}"
        )
        return 1

    try:
        body = Path(entry["path"]).read_text(encoding="utf-8")
    except OSError as e:
        print(f"{Colors.FAIL}Could not read {entry['filename']}: {e}{Colors.ENDC}")
        return 1

    print(f"\n{Colors.GRAY}# {entry['filename']}{Colors.ENDC}\n")
    print(body.rstrip())
    return 0


def cmd_lessons_browse(args):
    """Interactive browse/select UI over the lessons layer (§5.7).

    Bare ``pg lessons`` in a TTY: pick a lesson to read its full body. Degrades
    to ``pg lessons list`` without a TTY or without ``questionary``, so
    scripts/CI are unaffected.
    """
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    try:
        import questionary
    except Exception:
        questionary = None

    if not interactive or questionary is None:
        return cmd_lessons_list(args)

    entries = _collect_lesson_entries()
    if not entries:
        print(
            f"{Colors.YELLOW}No lessons recorded yet.{Colors.ENDC} "
            f"{Colors.GRAY}Write one under .proto-gear/lessons/.{Colors.ENDC}"
        )
        return 0

    while True:
        choices = [
            questionary.Choice(_lesson_entry_label(e), value=i)
            for i, e in enumerate(entries)
        ]
        choices.append(questionary.Choice("Quit", value="__quit__"))
        selection = questionary.select(
            "Lessons — accumulated knowledge (select to read):",
            choices=choices,
        ).ask()

        if selection is None or selection == "__quit__":
            return 0

        entry = entries[selection]
        cmd_lessons_show(_args_ns(name=entry["filename"]))


# ============================================================================
# Orchestration Paradigm Commands (the paradigm pool)
# ============================================================================


def _collect_paradigm_entries(project_dir: Optional[Path] = None) -> List[dict]:
    """Assemble the paradigm pool for browse/list. Pure data (unit-testable).

    Each entry: ``id``, ``name``, ``description``, ``roles`` (list of
    ``(role, model_tier)``), ``selectable_by``, ``installed`` (bool — a project
    copy exists under ``.proto-gear/orchestration/``), ``module`` (source).
    """
    from . import orchestration_config
    from .module_core import module_host

    project_dir = Path(project_dir) if project_dir is not None else Path(".")
    installed_dir = project_dir / ".proto-gear" / "orchestration"
    installed_stems = (
        {p.stem for p in installed_dir.glob("*.yaml")}
        if installed_dir.is_dir()
        else set()
    )
    source_module = {
        r["name"]: r["module"] for r in module_host.list_bundled_paradigms()
    }

    entries: List[dict] = []
    for p in orchestration_config.load_paradigms(project_dir=project_dir):
        entries.append(
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "roles": [(r.role, r.model_tier) for r in p.roles],
                "selectable_by": p.selectable_by,
                "installed": p.id in installed_stems,
                "module": source_module.get(p.id),
            }
        )
    return entries


def _paradigm_entry_label(entry: dict) -> str:
    """One-line label for a paradigm in the browse list."""
    roles = ", ".join(f"{role}·{tier}" for role, tier in entry["roles"])
    installed = f" {Colors.GRAY}[installed]{Colors.ENDC}" if entry["installed"] else ""
    tail = f" — {entry['description']}" if entry["description"] else ""
    return f"{Colors.CYAN}{entry['id']}{Colors.ENDC} {Colors.GRAY}({roles}){Colors.ENDC}{installed}{tail}"


def cmd_orchestration_list(args):
    """List orchestration paradigms in the pool (bundled + installed overrides)."""
    import json as _json

    entries = _collect_paradigm_entries()

    if getattr(args, "json", False):
        print(_json.dumps({"paradigms": entries}, indent=2))
        return 0

    if not entries:
        print(f"{Colors.YELLOW}No orchestration paradigms found.{Colors.ENDC}")
        return 0

    print(
        f"\n{Colors.HEADER}Orchestration paradigms{Colors.ENDC} "
        f"{Colors.GRAY}(how sub-agents are distributed — pick and switch on the fly){Colors.ENDC}\n"
    )
    for e in entries:
        print(f"  {_paradigm_entry_label(e)}")
    print(f"\n{Colors.GRAY}pg orchestration show <id>   - full details{Colors.ENDC}")
    return 0


def cmd_orchestration_show(args):
    """Show detailed information about one orchestration paradigm."""
    import json as _json
    from . import orchestration_config

    paradigm_id = args.id
    pool = {p.id: p for p in orchestration_config.load_paradigms(project_dir=Path("."))}
    paradigm = pool.get(paradigm_id)

    if paradigm is None:
        print(f"{Colors.FAIL}Paradigm not found: '{paradigm_id}'{Colors.ENDC}\n")
        suggestions = get_close_matches(paradigm_id, list(pool), n=3, cutoff=0.5)
        if suggestions:
            print(f"{Colors.BOLD}Did you mean:{Colors.ENDC}")
            for s in suggestions:
                print(f"  - {s}")
            print()
        print("Use 'pg orchestration list' to see the pool")
        return 1

    if getattr(args, "json", False):
        print(_json.dumps(paradigm.to_dict(), indent=2))
        return 0

    print(f"\n{Colors.HEADER}=== {paradigm.name} ({paradigm.id}) ==={Colors.ENDC}\n")
    print(f"{paradigm.description}\n")

    if paradigm.roles:
        print(f"{Colors.CYAN}Roles:{Colors.ENDC}")
        for r in paradigm.roles:
            slot = f" [agent: {r.agent}]" if r.agent else ""
            print(
                f"  - {r.role} {Colors.GRAY}(tier: {r.model_tier}){Colors.ENDC}{slot}"
            )
            if r.responsibility:
                print(f"      {r.responsibility}")

    if paradigm.when_to_use:
        print(f"\n{Colors.CYAN}When to use:{Colors.ENDC}")
        for item in paradigm.when_to_use:
            print(f"  + {item}")
    if paradigm.avoid_when:
        print(f"\n{Colors.CYAN}Avoid when:{Colors.ENDC}")
        for item in paradigm.avoid_when:
            print(f"  - {item}")
    if paradigm.coordination:
        print(
            f"\n{Colors.CYAN}Coordination:{Colors.ENDC}\n  {paradigm.coordination.strip()}"
        )
    if paradigm.efficiency:
        print(
            f"\n{Colors.CYAN}Efficiency:{Colors.ENDC}\n  {paradigm.efficiency.strip()}"
        )
    print(
        f"\n{Colors.GRAY}Selectable by: {', '.join(paradigm.selectable_by)}{Colors.ENDC}"
    )
    return 0


def cmd_orchestration_install(args):
    """Install one bundled paradigm into .proto-gear/orchestration/ to customise."""
    from .module_core import module_host

    proto_gear_dir = Path(".proto-gear")
    if not proto_gear_dir.is_dir():
        print(f"{Colors.FAIL}No .proto-gear/ here — run 'pg init' first.{Colors.ENDC}")
        return 1

    result = module_host.install_bundled_paradigm(args.id, proto_gear_dir)
    for err in result["errors"]:
        print(f"{Colors.FAIL}{err}{Colors.ENDC}")
    if result["errors"]:
        print(f"\nUse 'pg orchestration list' to see the pool")
        return 1

    print(f"{Colors.GREEN}Installed paradigm: {result['installed']}{Colors.ENDC}")
    print(f"  pg orchestration show {Path(result['installed']).stem}  - view it")
    return 0


def cmd_orchestration_browse(args):
    """Interactive browse/select UI over the orchestration paradigm pool (§5.7).

    UI-first entry for bare ``pg orchestration``: navigate the pool and inspect a
    paradigm (and install it for project customisation). Degrades to the static
    ``pg orchestration list`` without a TTY or ``questionary``.
    """
    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    try:
        import questionary
    except Exception:
        questionary = None

    if not interactive or questionary is None:
        return cmd_orchestration_list(args)

    while True:
        entries = _collect_paradigm_entries()
        if not entries:
            print(f"{Colors.YELLOW}No orchestration paradigms found.{Colors.ENDC}")
            return 0

        choices = [
            questionary.Choice(_paradigm_entry_label(e), value=i)
            for i, e in enumerate(entries)
        ]
        choices.append(questionary.Choice("Quit", value="__quit__"))
        selection = questionary.select(
            "Orchestration paradigms — pick one to view:",
            choices=choices,
        ).ask()

        if selection is None or selection == "__quit__":
            return 0

        entry = entries[selection]
        cmd_orchestration_show(_args_ns(id=entry["id"], json=False))
        if not entry["installed"]:
            confirm = questionary.confirm(
                f"Install '{entry['id']}' into .proto-gear/orchestration/ to customise?",
                default=False,
            ).ask()
            if confirm:
                cmd_orchestration_install(_args_ns(id=entry["id"]))


def _collect_agent_entries(agents_dir: Path, caps_dir: Path) -> List[dict]:
    """Assemble the unified browse list: installed agents + available bundled ones.

    Pure data (no I/O prompts) so it is unit-testable. Each entry is a dict:
    ``kind`` (``installed`` | ``available``), ``name``, ``description``,
    ``module`` (source, ``None`` for shared/installed) and, for installed
    agents, a validation ``status`` (``valid`` / ``warnings`` / ``invalid`` /
    ``error``). Installed first, then available — mirroring `pg agent list`.
    """
    from .module_core import module_host

    entries: List[dict] = []

    if agents_dir.exists():
        try:
            manager = AgentManager(agents_dir, caps_dir)
            for agent in manager.list_agents():
                try:
                    errors, warnings = manager.validate_agent(agent)
                    status = (
                        "invalid" if errors else "warnings" if warnings else "valid"
                    )
                except Exception:
                    status = "error"
                entries.append(
                    {
                        "kind": "installed",
                        "name": agent.name,
                        "description": agent.description or "",
                        "module": None,
                        "status": status,
                        "tier": agent.model.tier,
                    }
                )
        except Exception:
            pass  # a broken agents dir shouldn't hide the available ones

    installed_stems = (
        {p.stem for p in agents_dir.glob("*.yaml")} if agents_dir.exists() else set()
    )
    for r in module_host.list_bundled_agents():
        if r["name"] in installed_stems:
            continue
        entries.append(
            {
                "kind": "available",
                "name": r["name"],
                "description": r["description"] or "",
                "module": r["module"],
                "status": None,
            }
        )
    return entries


def _agent_entry_label(entry: dict) -> str:
    """One-line label for an agent entry in the browse list."""
    if entry["kind"] == "installed":
        badge = {
            "valid": f"{Colors.GREEN}[OK]{Colors.ENDC}",
            "warnings": f"{Colors.WARNING}[!]{Colors.ENDC}",
            "invalid": f"{Colors.FAIL}[X]{Colors.ENDC}",
            "error": f"{Colors.FAIL}[X]{Colors.ENDC}",
        }.get(entry["status"], "")
        tier = entry.get("tier")
        tier_badge = f" {Colors.GRAY}·{tier}{Colors.ENDC}" if tier else ""
        tail = f" — {entry['description']}" if entry["description"] else ""
        return f"{badge} {entry['name']}{tier_badge}{tail}"
    source = entry["module"] or "shared"
    tail = f" — {entry['description']}" if entry["description"] else ""
    return f"{Colors.CYAN}+ {entry['name']}{Colors.ENDC} {Colors.GRAY}[{source}, not installed]{Colors.ENDC}{tail}"


def cmd_agent_browse(args):
    """Interactive browse/select UI over installed + available agents (§5.7).

    UI-first entry point for ``pg agent`` with no subcommand: navigate the
    catalog and pick an agent to inspect (and install, if it's a bundled one not
    yet here). Degrades gracefully — without a TTY or without ``questionary``
    it falls back to the classic ``pg agent list`` so scripts/CI are unaffected.
    """
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    interactive = sys.stdin.isatty() and sys.stdout.isatty()
    try:
        import questionary
    except Exception:
        questionary = None

    # Non-interactive (piped/CI) or no questionary: the static list is correct.
    if not interactive or questionary is None:
        return cmd_agent_list(args)

    while True:
        entries = _collect_agent_entries(agents_dir, caps_dir)
        if not entries:
            print(
                f"{Colors.YELLOW}No agents installed or available.{Colors.ENDC} "
                f"Run 'pg init' to scaffold, or 'pg agent create <name>'."
            )
            return 0

        choices = [
            questionary.Choice(_agent_entry_label(e), value=i)
            for i, e in enumerate(entries)
        ]
        choices.append(questionary.Choice("Quit", value="__quit__"))
        selection = questionary.select(
            "Agents — installed + available (select to view):",
            choices=choices,
        ).ask()

        if selection is None or selection == "__quit__":
            return 0

        entry = entries[selection]
        if entry["kind"] == "installed":
            cmd_agent_show(_args_ns(name=entry["name"]))
        else:
            _show_available_agent(entry)
            confirm = questionary.confirm(
                f"Install '{entry['name']}' into .proto-gear/agents/?",
                default=False,
            ).ask()
            if confirm:
                cmd_agent_install(_args_ns(name=entry["name"]))


def _show_available_agent(entry: dict) -> None:
    """Print the summary of a bundled agent that isn't installed yet."""
    source = entry["module"] or "shared"
    print(f"\n{Colors.HEADER}=== {entry['name']} ==={Colors.ENDC}\n")
    print(f"Source: {source}")
    print(f"Status: {Colors.YELLOW}not installed{Colors.ENDC}")
    if entry["description"]:
        print(f"\n{Colors.CYAN}Description:{Colors.ENDC}\n  {entry['description']}")
    print()


def _args_ns(**kw):
    """Small argparse.Namespace shim for dispatching to sibling handlers."""
    import argparse

    return argparse.Namespace(**kw)


def cmd_agent_install(args):
    """Install one bundled agent (shared or discipline-shipped) on demand."""
    from .module_core import module_host

    proto_gear_dir = Path(".proto-gear")
    if not proto_gear_dir.is_dir():
        print(f"{Colors.FAIL}No .proto-gear/ here — run 'pg init' first.{Colors.ENDC}")
        return 1

    result = module_host.install_bundled_agent(args.name, proto_gear_dir)
    for err in result["errors"]:
        print(f"{Colors.FAIL}{err}{Colors.ENDC}")
    if result["errors"]:
        print(f"\nUse 'pg agent list --available' to see installable agents")
        return 1

    print(f"{Colors.GREEN}Installed agent: {result['installed']}{Colors.ENDC}")
    print(f"  pg agent show {Path(result['installed']).stem}  - view it")
    return 0


def cmd_agent_show(args):
    """Show detailed information about an agent"""
    agent_name = args.name
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    try:
        manager = AgentManager(agents_dir, caps_dir)
        agent = manager.load_agent(agent_name)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Agent not found: '{agent_name}'{Colors.ENDC}\n")

        # Suggest similar agents using fuzzy matching
        try:
            all_agents = manager.list_agents()
            agent_names = [a.name for a in all_agents]
            suggestions = get_close_matches(agent_name, agent_names, n=3, cutoff=0.6)

            if suggestions:
                print(f"{Colors.BOLD}Did you mean:{Colors.ENDC}")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
                print()
        except Exception:
            pass  # If we can't load agents for suggestions, just skip

        print(f"Use 'pg agent list' to see all agents")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}Error loading agent: {e}{Colors.ENDC}")
        return 1

    # Display detailed information
    print(f"\n{Colors.HEADER}=== {agent.name} ==={Colors.ENDC}\n")
    print(f"Version: {agent.version}")
    print(f"Status: {agent.status}")
    print(f"Created: {agent.created}")
    if agent.author:
        print(f"Author: {agent.author}")

    print(f"\n{Colors.CYAN}Description:{Colors.ENDC}")
    print(f"  {agent.description}")

    # Model (declared tier the host honours; optional concrete override)
    model_line = f"  Tier: {agent.model.tier}"
    if agent.model.override:
        model_line += f"  (override: {agent.model.override})"
    print(f"\n{Colors.CYAN}Model:{Colors.ENDC}")
    print(model_line)

    # Capabilities
    print(f"\n{Colors.CYAN}Capabilities:{Colors.ENDC}")
    if agent.capabilities.skills:
        print(f"  Skills: {', '.join(agent.capabilities.skills)}")
    if agent.capabilities.workflows:
        print(f"  Workflows: {', '.join(agent.capabilities.workflows)}")
    if agent.capabilities.commands:
        print(f"  Commands: {', '.join(agent.capabilities.commands)}")

    # Context priority
    if agent.context_priority:
        print(f"\n{Colors.CYAN}Context Priority:{Colors.ENDC}")
        for i, priority in enumerate(agent.context_priority, 1):
            print(f"  {i}. {priority}")

    # Instructions
    if agent.agent_instructions:
        print(f"\n{Colors.CYAN}Agent Instructions:{Colors.ENDC}")
        for i, instruction in enumerate(agent.agent_instructions, 1):
            print(f"  {i}. {instruction}")

    # Files
    if agent.required_files:
        print(f"\n{Colors.CYAN}Required Files:{Colors.ENDC}")
        for file in agent.required_files:
            print(f"  - {file}")

    if agent.optional_files:
        print(f"\n{Colors.CYAN}Optional Files:{Colors.ENDC}")
        for file in agent.optional_files:
            print(f"  - {file}")

    if agent.tags:
        print(f"\nTags: {', '.join(agent.tags)}")

    return 0


def cmd_agent_validate(args):
    """Validate an agent configuration"""
    agent_name = args.name
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    try:
        manager = AgentManager(agents_dir, caps_dir)
        agent = manager.load_agent(agent_name)
    except FileNotFoundError:
        print(f"{Colors.FAIL}Agent not found: '{agent_name}'{Colors.ENDC}\n")

        # Suggest similar agents using fuzzy matching
        try:
            all_agents = manager.list_agents()
            agent_names = [a.name for a in all_agents]
            suggestions = get_close_matches(agent_name, agent_names, n=3, cutoff=0.6)

            if suggestions:
                print(f"{Colors.BOLD}Did you mean:{Colors.ENDC}")
                for suggestion in suggestions:
                    print(f"  - {suggestion}")
                print()
        except Exception:
            pass  # If we can't load agents for suggestions, just skip

        print(f"Use 'pg agent list' to see all agents")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}Error loading agent: {e}{Colors.ENDC}")
        return 1

    print(f"\n{Colors.HEADER}=== Validating {agent.name} ==={Colors.ENDC}\n")

    # Validate
    errors, warnings = manager.validate_agent(agent)

    if errors:
        print(f"{Colors.FAIL}ERRORS:{Colors.ENDC}")
        for error in errors:
            print(f"  - {error}")
        print()

    if warnings:
        print(f"{Colors.WARNING}WARNINGS:{Colors.ENDC}")
        for warning in warnings:
            print(f"  - {warning}")
        print()

    if not errors and not warnings:
        print(f"{Colors.GREEN}Agent configuration is valid!{Colors.ENDC}")
    elif not errors:
        print(
            f"{Colors.GREEN}Agent configuration is valid (with warnings){Colors.ENDC}"
        )
    else:
        print(f"{Colors.FAIL}Agent configuration has errors{Colors.ENDC}")
        return 1

    # Show recommendations
    if not args.no_recommendations:
        recommendations = manager.get_recommendations(agent)
        if recommendations:
            print(f"\n{Colors.CYAN}Recommended capabilities to add:{Colors.ENDC}")
            for rec in recommendations[:10]:
                print(f"  - {rec}")
            if len(recommendations) > 10:
                print(f"  ... and {len(recommendations) - 10} more")

    return 0


def cmd_agent_delete(args):
    """Delete an agent configuration"""
    agent_name = args.name
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    # Confirm deletion unless --force
    if not args.force:
        print(
            f"{Colors.WARNING}Are you sure you want to delete agent '{agent_name}'?{Colors.ENDC}"
        )
        response = input(f"Type 'yes' to confirm: ").strip().lower()
        if response != "yes":
            print(f"{Colors.YELLOW}Deletion cancelled.{Colors.ENDC}")
            return 0

    try:
        manager = AgentManager(agents_dir, caps_dir)
        manager.delete_agent(agent_name)
        print(f"{Colors.GREEN}Agent '{agent_name}' deleted successfully{Colors.ENDC}")
        return 0
    except FileNotFoundError:
        print(f"{Colors.FAIL}Agent not found: {agent_name}{Colors.ENDC}")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}Error deleting agent: {e}{Colors.ENDC}")
        return 1


def _create_from_template(
    args, agents_dir: Path, caps_dir: Path
) -> Optional[AgentConfiguration]:
    """
    Create agent from template.

    Args:
        args: Arguments with template name and optional agent_name
        agents_dir: Directory for agents
        caps_dir: Directory for capabilities

    Returns:
        AgentConfiguration or None on error
    """
    from .agent_templates import create_agent_from_template, get_template

    template_name = args.template
    agent_name = args.name if hasattr(args, "name") and args.name else None
    author = args.author if hasattr(args, "author") and args.author else None
    description = (
        args.description if hasattr(args, "description") and args.description else None
    )

    # Check if template exists
    template = get_template(template_name)
    if not template:
        print(f"{Colors.FAIL}Template not found: {template_name}{Colors.ENDC}")
        print(f"\nUse 'pg agent create --list-templates' to see available templates")
        return None

    try:
        # Create agent from template
        agent = create_agent_from_template(template_name, agent_name, author)

        # Override description if provided
        if description:
            agent.description = description

        print(
            f"\n{Colors.GREEN}[OK] Agent created from template: {template_name}{Colors.ENDC}"
        )
        print(f"  Name: {agent.name}")
        print(f"  Capabilities: {len(agent.capabilities.all_capabilities())}")

        return agent

    except Exception as e:
        print(f"{Colors.FAIL}Error creating agent from template: {e}{Colors.ENDC}")
        return None


def _create_quick_agent(
    args, agents_dir: Path, caps_dir: Path
) -> Optional[AgentConfiguration]:
    """
    Create agent from command-line arguments (quick mode).

    Args:
        args: Arguments with name, capabilities, description
        agents_dir: Directory for agents
        caps_dir: Directory for capabilities

    Returns:
        AgentConfiguration or None on error
    """
    from datetime import datetime

    # Validate required arguments
    if not hasattr(args, "name") or not args.name:
        print(f"{Colors.FAIL}Agent name is required in quick mode{Colors.ENDC}")
        print(f"Usage: pg agent create <name> --capabilities cap1,cap2,cap3")
        return None

    if not args.capabilities:
        print(f"{Colors.FAIL}At least one capability is required{Colors.ENDC}")
        print(f"Usage: pg agent create {args.name} --capabilities cap1,cap2,cap3")
        return None

    # Parse capabilities (comma-separated)
    cap_list = [c.strip() for c in args.capabilities.split(",")]

    # Load all capabilities for validation
    try:
        all_caps = load_all_capabilities(caps_dir)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return None

    # Categorize capabilities
    skills = []
    workflows = []
    commands = []

    for cap in cap_list:
        # Try to find capability (support short names)
        found = False
        for category in ["skills", "workflows", "commands"]:
            full_id = f"{category}/{cap}"
            if full_id in all_caps:
                if category == "skills":
                    skills.append(cap)  # Use short name, not full_id
                elif category == "workflows":
                    workflows.append(cap)  # Use short name, not full_id
                elif category == "commands":
                    commands.append(cap)  # Use short name, not full_id
                found = True
                break
            # Also try exact match
            if cap in all_caps:
                metadata = all_caps[cap]
                # Extract short name from full path if needed
                short_name = cap.split("/")[-1] if "/" in cap else cap
                if metadata.type.value == "skill":
                    skills.append(short_name)
                elif metadata.type.value == "workflow":
                    workflows.append(short_name)
                elif metadata.type.value == "command":
                    commands.append(short_name)
                found = True
                break

        if not found:
            print(f"{Colors.WARNING}Warning: Capability not found: {cap}{Colors.ENDC}")
            print(f"  Use 'pg capabilities list' to see available capabilities")

    if not skills and not workflows and not commands:
        print(f"{Colors.FAIL}No valid capabilities found{Colors.ENDC}")
        return None

    # Get description
    description = (
        args.description
        if hasattr(args, "description") and args.description
        else f"Custom agent with {len(cap_list)} capabilities"
    )

    # Get author
    author = args.author if hasattr(args, "author") and args.author else "User"

    # Create agent configuration
    agent = AgentConfiguration(
        name=args.name,
        version="1.0.0",
        description=description,
        created=datetime.now().strftime("%Y-%m-%d"),
        author=author,
        capabilities=AgentCapabilities(
            skills=skills, workflows=workflows, commands=commands
        ),
        context_priority=["PROJECT_STATUS.md", "AGENTS.md"],
        agent_instructions=[],
        required_files=["PROJECT_STATUS.md", "AGENTS.md"],
        optional_files=[],
        tags=["custom", "quick-create"],
        status="active",
    )

    print(f"\n{Colors.GREEN}[OK] Quick agent created{Colors.ENDC}")
    print(f"  Name: {agent.name}")
    print(
        f"  Capabilities: {len(agent.capabilities.all_capabilities())} "
        + f"({len(skills)} skills, {len(workflows)} workflows, {len(commands)} commands)"
    )

    return agent


def cmd_agent_clone(args):
    """Clone an existing agent"""
    source_name = args.source
    dest_name = args.destination
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    try:
        manager = AgentManager(agents_dir, caps_dir)

        # Load source agent
        source_agent = manager.load_agent(source_name)

        # Create cloned agent with new name
        from datetime import datetime

        cloned_agent = AgentConfiguration(
            name=dest_name,
            version=source_agent.version,
            description=(
                args.description
                if hasattr(args, "description") and args.description
                else f"Cloned from {source_name}"
            ),
            created=datetime.now().strftime("%Y-%m-%d"),
            author=source_agent.author,
            capabilities=source_agent.capabilities,
            model=source_agent.model,
            context_priority=(
                source_agent.context_priority.copy()
                if source_agent.context_priority
                else []
            ),
            agent_instructions=(
                source_agent.agent_instructions.copy()
                if source_agent.agent_instructions
                else []
            ),
            required_files=(
                source_agent.required_files.copy()
                if source_agent.required_files
                else []
            ),
            optional_files=(
                source_agent.optional_files.copy()
                if source_agent.optional_files
                else []
            ),
            tags=source_agent.tags.copy() if source_agent.tags else [],
            status=source_agent.status,
        )

        # Save cloned agent
        manager.save_agent(cloned_agent, dest_name)

        print(f"\n{Colors.GREEN}[OK] Agent cloned successfully!{Colors.ENDC}")
        print(f"  Source: {source_name}")
        print(f"  New agent: {dest_name}")
        print(f"  Capabilities: {len(cloned_agent.capabilities.all_capabilities())}")
        print(f"\n{Colors.CYAN}Next steps:{Colors.ENDC}")
        print(f"  1. Review: pg agent show {dest_name}")
        print(f"  2. Customize: Edit .proto-gear/agents/{dest_name}.yaml")

        return 0

    except FileNotFoundError:
        print(f"{Colors.FAIL}Source agent not found: {source_name}{Colors.ENDC}")
        print(f"\nUse 'pg agent list' to see available agents")
        return 1
    except Exception as e:
        print(f"{Colors.FAIL}Error cloning agent: {e}{Colors.ENDC}")
        return 1


def cmd_agent_create(args):
    """Create a new agent (interactive wizard or quick mode)"""
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    # Ensure agents directory exists
    agents_dir.mkdir(parents=True, exist_ok=True)

    # Handle --list-templates flag
    if hasattr(args, "list_templates") and args.list_templates:
        from .agent_templates import print_available_templates

        print_available_templates()
        return 0

    # Quick mode: --template or --capabilities
    if hasattr(args, "template") and args.template:
        agent = _create_from_template(args, agents_dir, caps_dir)
        if not agent:
            return 1
    elif hasattr(args, "capabilities") and args.capabilities:
        agent = _create_quick_agent(args, agents_dir, caps_dir)
        if not agent:
            return 1
    else:
        # Interactive wizard mode (default)
        try:
            from .agent_wizard import run_agent_creation_wizard
        except ImportError:
            print(f"{Colors.FAIL}Agent wizard not available{Colors.ENDC}")
            return 1

        print(f"\n{Colors.HEADER}🤖 Proto Gear Agent Creation Wizard{Colors.ENDC}\n")

        # Run wizard
        agent = run_agent_creation_wizard(agents_dir, caps_dir)

        if not agent:
            print(f"\n{Colors.YELLOW}Agent creation cancelled{Colors.ENDC}")
            return 0

    # Generate filename from agent name
    agent_filename = agent.name.lower().replace(" ", "-")
    if not agent_filename.endswith(".yaml"):
        agent_filename += ".yaml"

    # Check if file already exists
    agent_file = agents_dir / agent_filename
    if agent_file.exists():
        overwrite = (
            input(
                f"\n{Colors.WARNING}Agent file already exists. Overwrite? (yes/no): {Colors.ENDC}"
            )
            .strip()
            .lower()
        )
        if overwrite != "yes":
            print(f"{Colors.YELLOW}Agent not saved{Colors.ENDC}")
            return 0

    # Save agent
    try:
        manager = AgentManager(agents_dir, caps_dir)
        agent_name = agent_filename.replace(".yaml", "")
        manager.save_agent(agent, agent_name)

        print(f"\n{Colors.GREEN}[OK] Agent created successfully!{Colors.ENDC}")
        print(f"\nSaved to: {agent_file}")
        print(f"\n{Colors.CYAN}Next steps:{Colors.ENDC}")
        print(f"  1. Review: pg agent show {agent_name}")
        print(f"  2. Validate: pg agent validate {agent_name}")
        print(f"  3. Customize: Edit {agent_file} as needed")

        return 0

    except Exception as e:
        print(f"\n{Colors.FAIL}Error saving agent: {e}{Colors.ENDC}")
        return 1


# ============================================================================
# Template Update Commands
# ============================================================================


def cmd_template_update(args):
    """
    Update template files while preserving user data.

    Safely updates AGENTS.md and PROJECT_STATUS.md to latest template
    versions while preserving tickets, metrics, and custom configurations.
    """
    from .modules.engineering.template_updater import (
        TemplateUpdater,
        TemplateUpdateError,
    )
    import os

    # Get templates to update
    if args.templates and len(args.templates) > 0:
        # User specified which templates
        template_names = [t.replace(".md", "") for t in args.templates]
    else:
        # Update all supported templates
        template_names = ["PROJECT_STATUS", "AGENTS"]

    # Build project context for placeholders
    project_dir = Path.cwd()
    project_context = {
        "PROJECT_NAME": project_dir.name,
        "TICKET_PREFIX": _detect_ticket_prefix(project_dir),
        "VERSION": _get_protogear_version(),
        "MAIN_BRANCH": "main",
        "DEV_BRANCH": "development",
    }

    # Initialize updater
    updater = TemplateUpdater(project_dir)

    # Track results
    updated_count = 0
    skipped_count = 0
    error_count = 0

    print(f"\n{Colors.CYAN}=== Template Update ==={Colors.ENDC}")
    print(f"Project: {project_context['PROJECT_NAME']}")
    print(f"Templates: {', '.join(template_names)}")
    print()

    # Update each template
    for template_name in template_names:
        filename = f"{template_name}.md"
        file_path = project_dir / filename

        # Check if file exists
        if not file_path.exists():
            print(f"{Colors.WARNING}[SKIP] {filename} - File not found{Colors.ENDC}")
            skipped_count += 1
            continue

        try:
            # Perform update
            result = updater.update_template(
                template_name, project_context, dry_run=args.dry_run, force=args.force
            )

            # Report result
            if result.success:
                if args.dry_run:
                    print(
                        f"{Colors.CYAN}[DRY RUN] {filename} - Would update{Colors.ENDC}"
                    )
                    print(
                        f"  Changes: {Colors.GREEN}+{result.lines_added}{Colors.ENDC} / {Colors.FAIL}-{result.lines_removed}{Colors.ENDC} lines"
                    )
                else:
                    print(
                        f"{Colors.GREEN}[OK] {filename} - Updated successfully{Colors.ENDC}"
                    )
                    print(
                        f"  Changes: {Colors.GREEN}+{result.lines_added}{Colors.ENDC} / {Colors.FAIL}-{result.lines_removed}{Colors.ENDC} lines"
                    )
                    if result.backup_created:
                        print(f"  Backup: {result.backup_path.name}")

                # Show warnings if any
                if result.warnings:
                    print(f"  {Colors.WARNING}Warnings:{Colors.ENDC}")
                    for warning in result.warnings:
                        print(f"    - {warning}")

                updated_count += 1
            else:
                print(f"{Colors.FAIL}[ERROR] {filename} - Update failed{Colors.ENDC}")
                for error in result.errors:
                    print(f"  - {error}")
                error_count += 1

        except TemplateUpdateError as e:
            print(f"{Colors.FAIL}[ERROR] {filename} - {e}{Colors.ENDC}")
            error_count += 1
        except Exception as e:
            print(
                f"{Colors.FAIL}[ERROR] {filename} - Unexpected error: {e}{Colors.ENDC}"
            )
            error_count += 1

    # Summary
    print(f"\n{Colors.CYAN}=== Summary ==={Colors.ENDC}")
    if args.dry_run:
        print(f"Mode: {Colors.CYAN}DRY RUN{Colors.ENDC} (no files modified)")
    print(f"Updated: {Colors.GREEN}{updated_count}{Colors.ENDC}")
    if skipped_count > 0:
        print(f"Skipped: {Colors.WARNING}{skipped_count}{Colors.ENDC}")
    if error_count > 0:
        print(f"Errors: {Colors.FAIL}{error_count}{Colors.ENDC}")

    print()

    if args.dry_run and updated_count > 0:
        print(f"{Colors.CYAN}Tip:{Colors.ENDC} Run without --dry-run to apply changes")

    return 0 if error_count == 0 else 1


def _detect_ticket_prefix(project_dir: Path) -> str:
    """
    Detect ticket prefix from PROJECT_STATUS.md if it exists.

    Args:
        project_dir: Project root directory

    Returns:
        Ticket prefix (e.g., "PROTO", "TEST") or "TICKET" as default
    """
    status_file = project_dir / "PROJECT_STATUS.md"
    if status_file.exists():
        try:
            content = status_file.read_text(encoding="utf-8")
            # Look for ticket IDs in completed tickets table
            import re

            matches = re.findall(r"\|\s*([A-Z]+-\d+)\s*\|", content)
            if matches:
                # Extract prefix from first match
                prefix = matches[0].split("-")[0]
                return prefix
        except Exception:
            pass
    return "TICKET"


def _get_protogear_version() -> str:
    """
    Get current Proto Gear version.

    Returns:
        Version string (e.g., "0.8.2")
    """
    try:
        from . import __version__

        return __version__
    except Exception:
        return "0.8.1"  # Fallback


# ---------------------------------------------------------------------------
# Departmental modules (ADR-001 Phase B)
# ---------------------------------------------------------------------------


def cmd_module_list(args):
    """List departmental modules discovered from module.yaml manifests."""
    from .module_core import module_manifest

    try:
        modules = module_manifest.discover_modules()
    except module_manifest.ModuleManifestError as e:
        print(f"{Colors.FAIL}Error loading module manifests: {e}{Colors.ENDC}")
        return 1

    if getattr(args, "json", False):
        import json

        print(json.dumps([m.to_dict() for m in modules], indent=2))
        return 0

    if not modules:
        print(f"{Colors.YELLOW}No departmental modules found.{Colors.ENDC}")
        return 0

    print(f"{Colors.BOLD}{Colors.CYAN}Departmental modules{Colors.ENDC}")
    for m in modules:
        print(
            f"  {Colors.GREEN}{m.module}{Colors.ENDC} "
            f"{Colors.GRAY}v{m.version}{Colors.ENDC} — {m.name}"
        )
        if m.description:
            print(f"      {Colors.GRAY}{m.description.strip()}{Colors.ENDC}")
    return 0


def cmd_module_show(args):
    """Show a single departmental module's manifest details."""
    from .module_core import module_manifest

    try:
        modules = module_manifest.discover_modules()
    except module_manifest.ModuleManifestError as e:
        print(f"{Colors.FAIL}Error loading module manifests: {e}{Colors.ENDC}")
        return 1

    by_id = {m.module: m for m in modules}
    manifest = by_id.get(args.name)
    if manifest is None:
        print(f"{Colors.FAIL}Module '{args.name}' not found.{Colors.ENDC}")
        available = ", ".join(sorted(by_id)) or "(none)"
        print(f"{Colors.GRAY}Available: {available}{Colors.ENDC}")
        return 1

    if getattr(args, "json", False):
        import json

        print(json.dumps(manifest.to_dict(), indent=2))
        return 0

    print(
        f"{Colors.BOLD}{Colors.CYAN}{manifest.name}{Colors.ENDC} "
        f"{Colors.GRAY}({manifest.module} v{manifest.version}){Colors.ENDC}"
    )
    if manifest.description:
        print(f"  {manifest.description.strip()}")
    print(f"\n  {Colors.BOLD}Contract surfaces{Colors.ENDC}")
    print(f"    capabilities_root : {manifest.capabilities_root}")
    print(
        f"    state_surface     : {manifest.state_surface or Colors.GRAY + '(none)' + Colors.ENDC}"
    )
    print(f"    context_manifest  : {manifest.context_manifest}")
    print(
        f"    handoff           : {manifest.handoff or Colors.GRAY + '(none)' + Colors.ENDC}"
    )
    return 0


def cmd_pipeline(args):
    """Show the cross-discipline supervision pipeline (Phase D).

    Composes every discipline's declared supervision gates into the org's path
    to production, grouped by the action each gate guards — surfacing where
    disciplines converge on the same control point.
    """
    from .module_core import pipeline

    try:
        stages = pipeline.build_pipeline()
    except Exception as e:
        print(f"{Colors.FAIL}Error building pipeline: {e}{Colors.ENDC}")
        return 1

    if getattr(args, "json", False):
        import json

        print(json.dumps({"stages": stages}, indent=2))
        return 0

    if not stages:
        print(f"{Colors.YELLOW}No supervision gates declared.{Colors.ENDC}")
        return 0

    disciplines = sorted({g["discipline"] for s in stages for g in s["gates"]})
    print(
        f"{Colors.BOLD}{Colors.CYAN}Supervision pipeline{Colors.ENDC} — path to production"
    )
    print(
        f"{Colors.GRAY}Human approval gates across {len(disciplines)} disciplines "
        f"({', '.join(disciplines)}), grouped by the action they guard.{Colors.ENDC}\n"
    )
    for stage in stages:
        gates = stage["gates"]
        converge = (
            f"  {Colors.YELLOW}← {len({g['discipline'] for g in gates})} disciplines converge{Colors.ENDC}"
            if len({g["discipline"] for g in gates}) > 1
            else ""
        )
        print(f"{Colors.BOLD}before {stage['action']}{Colors.ENDC}{converge}")
        for g in gates:
            req = "required" if g["required"] else "optional"
            auth = g.get("authority", "human")
            auth_note = f", authority: {auth}" if auth != "human" else ""
            actor_note = f", actor: {g['actor']}" if g.get("actor") else ""
            print(
                f"  {Colors.GREEN}{g['gate']}{Colors.ENDC} "
                f"{Colors.GRAY}[{g['discipline']}]{Colors.ENDC} "
                f"— {g['approver']}, {req}{auth_note}{actor_note} "
                f"{Colors.GRAY}({g['workflow']}){Colors.ENDC}"
            )
        print()
    return 0


def cmd_trace(args):
    """Trace a change (engineering ticket id) across discipline state surfaces.

    Phase D-2: follows the ticket-id correlation key through each discipline's
    declared state_surface, showing where the change stands (engineering ticket
    → qa sign-off → prod deploy) and which supervision approvals have cleared.
    """
    from .module_core import trace

    change_id = args.change_id
    try:
        hits = trace.trace_change(change_id, Path("."))
        checklist = trace.gate_checklist(change_id, Path("."))
    except Exception as e:
        print(f"{Colors.FAIL}Error tracing change: {e}{Colors.ENDC}")
        return 1

    if getattr(args, "json", False):
        import json

        print(
            json.dumps(
                {"change": change_id, "hits": hits, "gates": checklist}, indent=2
            )
        )
        return 0

    print(
        f"{Colors.BOLD}{Colors.CYAN}Trace {change_id}{Colors.ENDC} "
        f"{Colors.GRAY}— cross-discipline{Colors.ENDC}"
    )
    if not hits:
        print(
            f"\n{Colors.YELLOW}No state-surface rows reference '{change_id}'.{Colors.ENDC}"
        )
        print(
            f"{Colors.GRAY}Downstream disciplines link a change via a 'Ref' column "
            f"in their state surface.{Colors.ENDC}"
        )
        return 0

    for h in hits:
        mark = ""
        if h["approval_state"] == "cleared":
            mark = f"  {Colors.GREEN}[approved: {h['approval'].strip()}]{Colors.ENDC}"
        elif h["approval_state"] == "pending":
            mark = f"  {Colors.YELLOW}[approval pending]{Colors.ENDC}"
        row_id = h["id"] or "(no id)"
        stage = h["stage"] or "—"
        print(
            f"  {Colors.GREEN}{h['discipline']:<12}{Colors.ENDC} "
            f"{row_id:<14} {stage:<12}{mark} "
            f"{Colors.GRAY}({h['surface']}){Colors.ENDC}"
        )

    # Required-approval checklist: which gates on the path to production this
    # change has cleared vs still lacks (Phase D-3). Release-scoped gates aren't
    # a single ticket's to clear — they're verified once via `pg release`.
    required = [g for g in checklist if g["required"] and g.get("scope") != "release"]
    release_scoped = [
        g for g in checklist if g["required"] and g.get("scope") == "release"
    ]
    if required:
        cleared = sum(1 for g in required if g["status"] == "cleared")
        print(
            f"\n{Colors.BOLD}Required approvals{Colors.ENDC} "
            f"{Colors.GRAY}(path to production){Colors.ENDC} "
            f"— {Colors.GREEN}{cleared}{Colors.ENDC}/{len(required)} cleared"
        )
        _marks = {
            "cleared": f"{Colors.GREEN}[x]{Colors.ENDC}",
            "pending": f"{Colors.YELLOW}[~]{Colors.ENDC}",
            "outstanding": f"{Colors.GRAY}[ ]{Colors.ENDC}",
            "untracked": f"{Colors.GRAY}[-]{Colors.ENDC}",
        }
        _labels = {
            "cleared": "cleared",
            "pending": "pending",
            "outstanding": "not reached",
            "untracked": "not recorded in surface",
        }
        for g in required:
            # ADR-002 item 3: a cleared gate whose only signers are agent
            # identities, when the gate demands a human rung, is flagged.
            insufficient = (
                f" {Colors.WARNING}!! agent-signed ({', '.join(g['signed_by'])}) "
                f"— requires {g['authority']}{Colors.ENDC}"
                if g.get("authority_ok") is False
                else ""
            )
            print(
                f"  {_marks[g['status']]} {g['gate']:<22} "
                f"{Colors.GRAY}[{g['discipline']}, before {g['action']}]{Colors.ENDC} "
                f"— {_labels[g['status']]}{insufficient}"
            )
    if release_scoped:
        gates = ", ".join(sorted({g["gate"] for g in release_scoped}))
        print(
            f"\n{Colors.GRAY}Release-scoped gates ({gates}) are cleared per "
            f"release, not per ticket — verify with `pg release <label>`.{Colors.ENDC}"
        )
    return 0


def cmd_release(args):
    """Trace a whole release across its tickets (Phase D-4).

    A release ships only when every one of its tickets has cleared every required
    approval on the path to production. This aggregates each ticket's gate
    checklist (`pg trace`) into a single readiness verdict, listing which tickets
    still block and on which gates. Membership is read from the disciplines'
    state surfaces via a release column (PR/Commit / Release / Version).
    """
    from .module_core import release

    release_id = args.release_id

    # --notes: generate a release-notes block from the cleared gate checklist.
    if getattr(args, "notes", False):
        try:
            notes = release.build_release_notes(release_id, Path("."))
        except Exception as e:
            print(f"{Colors.FAIL}Error building release notes: {e}{Colors.ENDC}")
            return 1
        if getattr(args, "json", False):
            import json

            print(json.dumps(notes, indent=2))
        else:
            print(release.render_release_notes(notes))
        return 0

    try:
        report = release.trace_release(release_id, Path("."))
    except Exception as e:
        print(f"{Colors.FAIL}Error tracing release: {e}{Colors.ENDC}")
        return 1

    if getattr(args, "json", False):
        import json

        print(json.dumps(report, indent=2))
        return 0

    print(
        f"{Colors.BOLD}{Colors.CYAN}Release {release_id}{Colors.ENDC} "
        f"{Colors.GRAY}— readiness across {report['ticket_count']} ticket(s){Colors.ENDC}"
    )
    if not report["tickets"]:
        print(
            f"\n{Colors.YELLOW}No tickets reference release '{release_id}'.{Colors.ENDC}"
        )
        print(
            f"{Colors.GRAY}A ticket joins a release via a 'PR/Commit', 'Release', "
            f"or 'Version' column in a discipline's state surface.{Colors.ENDC}"
        )
        return 0

    _mark = {
        "cleared": f"{Colors.GREEN}[x]{Colors.ENDC}",
        "pending": f"{Colors.YELLOW}[~]{Colors.ENDC}",
        "outstanding": f"{Colors.GRAY}[ ]{Colors.ENDC}",
        "untracked": f"{Colors.GRAY}[-]{Colors.ENDC}",
    }
    for e in report["tickets"]:
        # Per-ticket rows show change-scoped gates only; release-scoped gates are
        # listed once for the whole release below.
        required = [g for g in e["gates"] if g["required"] and g["scope"] != "release"]
        n_cleared = len(e["cleared"])
        verdict = (
            f"{Colors.GREEN}ready{Colors.ENDC}"
            if e["ready"]
            else f"{Colors.FAIL}blocked{Colors.ENDC}"
        )
        print(
            f"\n{Colors.BOLD}{e['ticket']}{Colors.ENDC} "
            f"{Colors.GRAY}({n_cleared}/{e['required_total']} required cleared){Colors.ENDC} "
            f"— {verdict}"
        )
        for g in required:
            insufficient = (
                f" {Colors.WARNING}!! agent-signed — requires {g['authority']}{Colors.ENDC}"
                if g.get("authority_ok") is False
                else ""
            )
            print(
                f"  {_mark[g['status']]} {g['gate']:<22} "
                f"{Colors.GRAY}[{g['discipline']}, before {g['action']}]{Colors.ENDC}"
                f"{insufficient}"
            )

    # Release-scoped gates — cleared once for the whole release (not per ticket).
    rg = report.get("release_gates", {})
    release_scoped = (
        rg.get("cleared", []) + rg.get("blocking", []) + rg.get("unverified", [])
    )
    if release_scoped:
        print(f"\n{Colors.BOLD}Release-scoped gates{Colors.ENDC}")
        for g in sorted(release_scoped, key=lambda g: g["gate"]):
            print(
                f"  {_mark[g['status']]} {g['gate']:<22} "
                f"{Colors.GRAY}[{g['discipline']}, before {g['action']}]{Colors.ENDC}"
            )

    # Release-level verdict.
    if report["ready"]:
        head = f"{Colors.BOLD}{Colors.GREEN}READY TO SHIP{Colors.ENDC}"
        if report["unverified_total"]:
            head += (
                f" {Colors.YELLOW}({report['unverified_total']} required approval(s) "
                f"unverifiable — discipline records no sign-off column){Colors.ENDC}"
            )
    else:
        head = (
            f"{Colors.BOLD}{Colors.FAIL}BLOCKED{Colors.ENDC} "
            f"{Colors.GRAY}— {report['blocking_total']} required gate(s) not cleared"
            f"{Colors.ENDC}"
        )
    if report.get("authority_insufficient_total"):
        head += (
            f" {Colors.WARNING}!! {report['authority_insufficient_total']} cleared "
            f"gate(s) signed with insufficient authority (agent-signed, human "
            f"required){Colors.ENDC}"
        )
    print(f"\n{Colors.BOLD}Release {release_id}:{Colors.ENDC} {head}")
    return 0


def cmd_module_init_surface(args):
    """Materialise the selected module's declared state surface into the project.

    Department-agnostic: renders ``<module>``'s state-surface template (e.g.
    ``FOO.template.md`` → ``FOO.md``) via the module_host seam. The target
    module comes from the global ``--module`` flag (default engineering). This
    is a manifest-only department's counterpart to engineering's richer
    ``pg init`` (PROTO-048, closes seam S2).
    """
    from .module_core import module_host
    from .module_core.module_manifest import ModuleManifestError

    try:
        manifest = module_host.resolve_module(getattr(args, "module", None))
    except ModuleManifestError as e:
        print(f"{Colors.FAIL}{e}{Colors.ENDC}")
        return 1

    result = module_host.render_state_surface(
        manifest,
        Path("."),
        force=getattr(args, "force", False),
        dry_run=getattr(args, "dry_run", False),
    )
    status = result["status"]
    target = result["target"]

    if status == "no-state-surface":
        print(
            f"{Colors.YELLOW}Module '{manifest.module}' declares no state surface — "
            f"nothing to initialise.{Colors.ENDC}"
        )
        return 0
    if status == "no-template":
        print(
            f"{Colors.FAIL}No template found for '{target}' in module "
            f"'{manifest.module}'.{Colors.ENDC}"
        )
        return 1
    if status == "exists":
        print(
            f"{Colors.YELLOW}{target} already exists — pass --force to "
            f"overwrite.{Colors.ENDC}"
        )
        return 1

    verb = {
        "created": "Created",
        "overwritten": "Overwrote",
        "would-create": "Would create",
        "would-overwrite": "Would overwrite",
    }.get(status, status)
    print(
        f"{Colors.GREEN}{verb} {target}{Colors.ENDC} "
        f"{Colors.GRAY}(module: {manifest.module}){Colors.ENDC}"
    )

    if result["unresolved"]:
        tokens = ", ".join(result["unresolved"])
        print(
            f"{Colors.YELLOW}Note: unresolved placeholders remain ({tokens}). "
            f"This module's state surface needs a richer init than the generic "
            f"renderer provides.{Colors.ENDC}"
        )
    return 0
