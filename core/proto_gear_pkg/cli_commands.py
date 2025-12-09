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

from .ui_helper import UIHelper, Colors
from .agent_config import (
    AgentManager,
    AgentConfiguration,
    AgentCapabilities,
    AgentValidationError,
    create_agent_template
)
from .capability_metadata import (
    load_all_capabilities,
    CapabilityMetadata,
    CapabilityType
)

ui = UIHelper()


def get_capabilities_dir() -> Path:
    """Get capabilities directory (package location)"""
    pkg_dir = Path(__file__).parent
    return pkg_dir / "capabilities"


def get_agents_dir() -> Path:
    """Get agents directory (project location)"""
    proto_gear_dir = Path(".proto-gear")
    agents_dir = proto_gear_dir / "agents"
    return agents_dir


# ============================================================================
# Capabilities Commands
# ============================================================================

def cmd_capabilities_list(args):
    """List all available capabilities"""
    caps_dir = get_capabilities_dir()

    try:
        all_caps = load_all_capabilities(caps_dir)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    if not all_caps:
        print(f"{Colors.YELLOW}No capabilities found{Colors.ENDC}")
        return 0

    # Group by type
    skills = {}
    workflows = {}
    commands = {}

    for cap_id, metadata in all_caps.items():
        if metadata.type == CapabilityType.SKILL:
            skills[cap_id] = metadata
        elif metadata.type == CapabilityType.WORKFLOW:
            workflows[cap_id] = metadata
        elif metadata.type == CapabilityType.COMMAND:
            commands[cap_id] = metadata

    # Display
    print(f"\n{Colors.HEADER}=== Proto Gear Capabilities ==={Colors.ENDC}\n")

    if skills:
        print(f"{Colors.CYAN}SKILLS ({len(skills)}):{Colors.ENDC}")
        for cap_id in sorted(skills.keys()):
            metadata = skills[cap_id]
            status_color = Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            print(f"  - {metadata.name:40} [{status_color}{metadata.status.value}{Colors.ENDC}]")
        print()

    if workflows:
        print(f"{Colors.CYAN}WORKFLOWS ({len(workflows)}):{Colors.ENDC}")
        for cap_id in sorted(workflows.keys()):
            metadata = workflows[cap_id]
            status_color = Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            print(f"  - {metadata.name:40} [{status_color}{metadata.status.value}{Colors.ENDC}]")
        print()

    if commands:
        print(f"{Colors.CYAN}COMMANDS ({len(commands)}):{Colors.ENDC}")
        for cap_id in sorted(commands.keys()):
            metadata = commands[cap_id]
            status_color = Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            print(f"  - {metadata.name:40} [{status_color}{metadata.status.value}{Colors.ENDC}]")
        print()

    print(f"Total: {len(all_caps)} capabilities")
    print(f"\nUse 'pg capabilities show <name>' to see details")

    return 0


def cmd_capabilities_search(args):
    """Search capabilities by keyword"""
    query = args.query.lower()
    caps_dir = get_capabilities_dir()

    try:
        all_caps = load_all_capabilities(caps_dir)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    # Search in name, description, tags, and trigger keywords
    matches = []
    for cap_id, metadata in all_caps.items():
        if (query in metadata.name.lower() or
            query in metadata.description.lower() or
            any(query in tag.lower() for tag in metadata.tags) or
            (metadata.relevance and metadata.relevance.matches_trigger(query))):
            matches.append((cap_id, metadata))

    if not matches:
        print(f"{Colors.YELLOW}No capabilities found matching '{query}'{Colors.ENDC}")
        return 0

    print(f"\n{Colors.HEADER}=== Search Results for '{query}' ({len(matches)} found) ==={Colors.ENDC}\n")

    for cap_id, metadata in sorted(matches, key=lambda x: x[0]):
        print(f"{Colors.CYAN}{metadata.name}{Colors.ENDC} ({cap_id})")
        print(f"  {metadata.description}")
        print(f"  Status: {metadata.status.value} | Tags: {', '.join(metadata.tags[:5])}")
        print()

    return 0


def cmd_capabilities_show(args):
    """Show detailed information about a capability"""
    name = args.name
    caps_dir = get_capabilities_dir()

    try:
        all_caps = load_all_capabilities(caps_dir)
    except Exception as e:
        print(f"{Colors.FAIL}Error loading capabilities: {e}{Colors.ENDC}")
        return 1

    # Find capability (support both short name and full path)
    metadata = None
    cap_id = None

    # Try exact match first
    if name in all_caps:
        cap_id = name
        metadata = all_caps[name]
    else:
        # Try searching in each category
        for category in ["skills", "workflows", "commands"]:
            test_id = f"{category}/{name}"
            if test_id in all_caps:
                cap_id = test_id
                metadata = all_caps[test_id]
                break

    if not metadata:
        print(f"{Colors.FAIL}Capability not found: {name}{Colors.ENDC}")
        print(f"\nUse 'pg capabilities list' to see all capabilities")
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

    return 0


# ============================================================================
# Agent Commands
# ============================================================================

def cmd_agent_list(args):
    """List all configured agents"""
    agents_dir = get_agents_dir()
    caps_dir = get_capabilities_dir()

    if not agents_dir.exists():
        print(f"{Colors.YELLOW}No agents directory found.{Colors.ENDC}")
        print(f"Create agents with: pg agent create <name>")
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
        return 0

    print(f"\n{Colors.HEADER}=== Configured Agents ==={Colors.ENDC}\n")

    for agent in agents:
        status_color = Colors.GREEN if agent.status == "active" else Colors.WARNING
        print(f"{Colors.CYAN}{agent.name}{Colors.ENDC} (v{agent.version}) [{status_color}{agent.status}{Colors.ENDC}]")
        print(f"  {agent.description}")

        # Show capability count
        cap_count = len(agent.capabilities.all_capabilities())
        print(f"  Capabilities: {cap_count} ({len(agent.capabilities.skills)} skills, "
              f"{len(agent.capabilities.workflows)} workflows, {len(agent.capabilities.commands)} commands)")
        print()

    print(f"Total: {len(agents)} agents")
    print(f"\nUse 'pg agent show <name>' to see details")

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
        print(f"{Colors.FAIL}Agent not found: {agent_name}{Colors.ENDC}")
        print(f"\nUse 'pg agent list' to see all agents")
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
        print(f"{Colors.FAIL}Agent not found: {agent_name}{Colors.ENDC}")
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
        print(f"{Colors.GREEN}Agent configuration is valid (with warnings){Colors.ENDC}")
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
        print(f"{Colors.WARNING}Are you sure you want to delete agent '{agent_name}'?{Colors.ENDC}")
        response = input(f"Type 'yes' to confirm: ").strip().lower()
        if response != 'yes':
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


def cmd_agent_create(args):
    """Create a new agent (interactive wizard - TODO)"""
    print(f"{Colors.WARNING}Interactive agent creation wizard is not yet implemented.{Colors.ENDC}")
    print(f"\nFor now, create agent configurations manually in .proto-gear/agents/")
    print(f"See: docs/dev/agent-configuration-schema.md for schema documentation")
    return 1
