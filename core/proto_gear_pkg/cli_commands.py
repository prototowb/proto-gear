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

    # Apply filters
    filtered_caps = all_caps.copy()

    # Filter by type
    if hasattr(args, 'type') and args.type:
        filtered_caps = {
            k: v for k, v in filtered_caps.items()
            if v.type.value == args.type
        }

    # Filter by tag
    if hasattr(args, 'tag') and args.tag:
        tag_lower = args.tag.lower()
        filtered_caps = {
            k: v for k, v in filtered_caps.items()
            if any(tag_lower in tag.lower() for tag in v.tags)
        }

    # Filter by role
    if hasattr(args, 'role') and args.role:
        role_lower = args.role.lower()
        filtered_caps = {
            k: v for k, v in filtered_caps.items()
            if v.agent_roles and any(role_lower in role.lower() for role in v.agent_roles)
        }

    # Filter by status
    if hasattr(args, 'status') and args.status:
        filtered_caps = {
            k: v for k, v in filtered_caps.items()
            if v.status.value == args.status
        }

    if not filtered_caps:
        print(f"{Colors.YELLOW}No capabilities match the specified filters{Colors.ENDC}")
        print(f"\nTry: pg capabilities list (without filters)")
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
        print(f"{Colors.CYAN}+-- SKILLS ({len(skills)}) " + "-" * 45 + f"+{Colors.ENDC}")
        for cap_id in sorted(skills.keys()):
            metadata = skills[cap_id]
            # Extract short ID (e.g., "skills/testing" -> "testing")
            short_id = cap_id.split('/')[-1]
            status_icon = "[OK]" if metadata.status.value == "stable" else "[!]"
            status_color = Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            # Format: | [OK] short-id          Full Name
            print(f"{Colors.CYAN}|{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} " +
                  f"{Colors.CYAN}{short_id:18}{Colors.ENDC} {metadata.name}")
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

    if workflows:
        # Box header
        print(f"{Colors.CYAN}+-- WORKFLOWS ({len(workflows)}) " + "-" * 42 + f"+{Colors.ENDC}")
        for cap_id in sorted(workflows.keys()):
            metadata = workflows[cap_id]
            short_id = cap_id.split('/')[-1]
            status_icon = "[OK]" if metadata.status.value == "stable" else "[!]"
            status_color = Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            print(f"{Colors.CYAN}|{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} " +
                  f"{Colors.CYAN}{short_id:18}{Colors.ENDC} {metadata.name}")
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

    if commands:
        # Box header
        print(f"{Colors.CYAN}+-- COMMANDS ({len(commands)}) " + "-" * 43 + f"+{Colors.ENDC}")
        for cap_id in sorted(commands.keys()):
            metadata = commands[cap_id]
            short_id = cap_id.split('/')[-1]
            status_icon = "[OK]" if metadata.status.value == "stable" else "[!]"
            status_color = Colors.GREEN if metadata.status.value == "stable" else Colors.WARNING
            print(f"{Colors.CYAN}|{Colors.ENDC} {status_color}{status_icon}{Colors.ENDC} " +
                  f"{Colors.CYAN}{short_id:18}{Colors.ENDC} {metadata.name}")
        print(f"{Colors.CYAN}+{'-' * 60}+{Colors.ENDC}\n")

    # Summary
    filters_applied = []
    if hasattr(args, 'type') and args.type:
        filters_applied.append(f"type={args.type}")
    if hasattr(args, 'tag') and args.tag:
        filters_applied.append(f"tag={args.tag}")
    if hasattr(args, 'role') and args.role:
        filters_applied.append(f"role={args.role}")
    if hasattr(args, 'status') and args.status:
        filters_applied.append(f"status={args.status}")

    if filters_applied:
        print(f"{Colors.BOLD}Showing: {len(filtered_caps)} of {len(all_caps)} capabilities{Colors.ENDC}")
        print(f"{Colors.GRAY}Filters: {', '.join(filters_applied)}{Colors.ENDC}")
    else:
        print(f"{Colors.BOLD}Total: {len(all_caps)} capabilities{Colors.ENDC}")

    print(f"{Colors.GRAY}Use 'pg capabilities show <name>' to see details{Colors.ENDC}")

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

    # Print header with box
    print(f"\n{Colors.CYAN}+-- Configured Agents ({len(agents)}) " + "-" * 40 + f"+{Colors.ENDC}")
    print(f"{Colors.CYAN}|{Colors.ENDC}")

    # Print table header
    print(f"{Colors.CYAN}|{Colors.ENDC} {Colors.BOLD}NAME{' ' * 16}CAPABILITIES  STATUS{Colors.ENDC}        ")
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
        print(f"{Colors.CYAN}|{Colors.ENDC} {Colors.CYAN}{name_display}{Colors.ENDC}"
              f"{name_padding}{cap_text}{cap_padding}{status_icon} {status_text}")

    # Print footer
    print(f"{Colors.CYAN}|{Colors.ENDC}")
    print(f"{Colors.CYAN}+-- " + "-" * 60 + f"+{Colors.ENDC}")

    # Print quick actions
    print(f"\n{Colors.BOLD}Quick actions:{Colors.ENDC}")
    print(f"  pg agent show <name>      - View configuration details")
    print(f"  pg agent validate <name>  - Check for configuration issues")
    print(f"  pg agent clone <src> <dst> - Duplicate an agent")

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


def _create_from_template(args, agents_dir: Path, caps_dir: Path) -> Optional[AgentConfiguration]:
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
    agent_name = args.name if hasattr(args, 'name') and args.name else None
    author = args.author if hasattr(args, 'author') and args.author else None
    description = args.description if hasattr(args, 'description') and args.description else None

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

        print(f"\n{Colors.GREEN}[OK] Agent created from template: {template_name}{Colors.ENDC}")
        print(f"  Name: {agent.name}")
        print(f"  Capabilities: {len(agent.capabilities.all_capabilities())}")

        return agent

    except Exception as e:
        print(f"{Colors.FAIL}Error creating agent from template: {e}{Colors.ENDC}")
        return None


def _create_quick_agent(args, agents_dir: Path, caps_dir: Path) -> Optional[AgentConfiguration]:
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
    if not hasattr(args, 'name') or not args.name:
        print(f"{Colors.FAIL}Agent name is required in quick mode{Colors.ENDC}")
        print(f"Usage: pg agent create <name> --capabilities cap1,cap2,cap3")
        return None

    if not args.capabilities:
        print(f"{Colors.FAIL}At least one capability is required{Colors.ENDC}")
        print(f"Usage: pg agent create {args.name} --capabilities cap1,cap2,cap3")
        return None

    # Parse capabilities (comma-separated)
    cap_list = [c.strip() for c in args.capabilities.split(',')]

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
                short_name = cap.split('/')[-1] if '/' in cap else cap
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
    description = args.description if hasattr(args, 'description') and args.description else \
                 f"Custom agent with {len(cap_list)} capabilities"

    # Get author
    author = args.author if hasattr(args, 'author') and args.author else "User"

    # Create agent configuration
    agent = AgentConfiguration(
        name=args.name,
        version="1.0.0",
        description=description,
        created=datetime.now().strftime("%Y-%m-%d"),
        author=author,
        capabilities=AgentCapabilities(
            skills=skills,
            workflows=workflows,
            commands=commands
        ),
        context_priority=["PROJECT_STATUS.md", "AGENTS.md"],
        agent_instructions=[],
        required_files=["PROJECT_STATUS.md", "AGENTS.md"],
        optional_files=[],
        tags=["custom", "quick-create"],
        status="active"
    )

    print(f"\n{Colors.GREEN}[OK] Quick agent created{Colors.ENDC}")
    print(f"  Name: {agent.name}")
    print(f"  Capabilities: {len(agent.capabilities.all_capabilities())} " +
          f"({len(skills)} skills, {len(workflows)} workflows, {len(commands)} commands)")

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
            description=args.description if hasattr(args, 'description') and args.description else f"Cloned from {source_name}",
            created=datetime.now().strftime("%Y-%m-%d"),
            author=source_agent.author,
            capabilities=source_agent.capabilities,
            context_priority=source_agent.context_priority.copy() if source_agent.context_priority else [],
            agent_instructions=source_agent.agent_instructions.copy() if source_agent.agent_instructions else [],
            required_files=source_agent.required_files.copy() if source_agent.required_files else [],
            optional_files=source_agent.optional_files.copy() if source_agent.optional_files else [],
            tags=source_agent.tags.copy() if source_agent.tags else [],
            status=source_agent.status
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
    if hasattr(args, 'list_templates') and args.list_templates:
        from .agent_templates import print_available_templates
        print_available_templates()
        return 0

    # Quick mode: --template or --capabilities
    if hasattr(args, 'template') and args.template:
        agent = _create_from_template(args, agents_dir, caps_dir)
        if not agent:
            return 1
    elif hasattr(args, 'capabilities') and args.capabilities:
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
        overwrite = input(f"\n{Colors.WARNING}Agent file already exists. Overwrite? (yes/no): {Colors.ENDC}").strip().lower()
        if overwrite != 'yes':
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
