#!/usr/bin/env python3
"""
Interactive Agent Creation Wizard

Guides users through creating custom AI agent configurations with:
- Capability selection (with search and recommendations)
- Context priority definition
- Agent instruction specification
- File dependency configuration
- Real-time validation and preview
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

try:
    import questionary
    from questionary import Style
    QUESTIONARY_AVAILABLE = True
except ImportError:
    QUESTIONARY_AVAILABLE = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .agent_config import (
    AgentConfiguration,
    AgentCapabilities,
    AgentManager,
    AgentValidator,
    create_agent_template
)
from .capability_metadata import (
    load_all_capabilities,
    CapabilityMetadata,
    CapabilityType,
    CompositionEngine
)
from .ui_helper import UIHelper, Colors

ui = UIHelper()


# Custom style for questionary
custom_style = Style([
    ('question', 'bold'),
    ('answer', 'fg:#00ff00 bold'),
    ('pointer', 'fg:#00ff00 bold'),
    ('highlighted', 'fg:#00ff00 bold'),
    ('selected', 'fg:#00ff00'),
    ('separator', 'fg:#cc5454'),
    ('instruction', ''),
    ('text', ''),
])


def run_agent_creation_wizard(agents_dir: Path, capabilities_dir: Path) -> Optional[AgentConfiguration]:
    """
    Run interactive agent creation wizard.

    Args:
        agents_dir: Directory where agent will be saved
        capabilities_dir: Directory containing capabilities

    Returns:
        AgentConfiguration if successful, None if cancelled
    """
    if not QUESTIONARY_AVAILABLE:
        print(f"{Colors.FAIL}Interactive wizard requires 'questionary' package{Colors.ENDC}")
        print(f"Install with: pip install questionary")
        return None

    if RICH_AVAILABLE:
        console = Console()
    else:
        console = None

    try:
        # Load all capabilities
        all_caps = load_all_capabilities(capabilities_dir)

        # Step 1: Welcome
        if not show_welcome(console):
            return None

        # Step 1.5: Template or Custom?
        template_name, use_template = ask_template_or_custom(console)

        # If using template, create from template and allow customization
        if use_template and template_name:
            from .agent_templates import create_agent_from_template

            # Get agent name
            print(f"\n{Colors.HEADER}=== Customize Template ==={Colors.ENDC}\n")
            name = questionary.text(
                "Agent name:",
                instruction=f"(press Enter to use default: '{template_name.replace('-', ' ').title()}')",
                default="",
                style=custom_style
            ).ask()

            # Create agent from template
            agent = create_agent_from_template(template_name, name if name else None, None)

            # Ask if user wants to customize further
            customize = questionary.confirm(
                "Would you like to customize this template further?",
                default=False,
                style=custom_style
            ).ask()

            if not customize:
                return agent

            # User wants to customize - continue with rest of wizard using template as starting point
            description = agent.description
            author = agent.author if agent.author else ""
            capabilities = agent.capabilities

            print(f"\n{Colors.CYAN}You can now modify the template...{Colors.ENDC}")
        else:
            # Step 2: Basic Information
            name, description, author = get_basic_info()
            if not name:
                return None

            # Step 3: Capability Selection (most important)
            capabilities = select_capabilities(all_caps, console)
            if not capabilities or capabilities.is_empty():
                print(f"\n{Colors.YELLOW}Agent creation cancelled - no capabilities selected{Colors.ENDC}")
                return None

        # Step 4: Validate selections
        print(f"\n{Colors.CYAN}Validating capability selections...{Colors.ENDC}")
        validation_errors = validate_capability_selections(capabilities, all_caps)
        if validation_errors:
            print(f"\n{Colors.FAIL}Validation errors found:{Colors.ENDC}")
            for error in validation_errors:
                print(f"  - {error}")

            fix = questionary.confirm(
                "Would you like to go back and fix the selections?",
                default=True,
                style=custom_style
            ).ask()

            if fix:
                return run_agent_creation_wizard(agents_dir, capabilities_dir)
            else:
                return None

        # Show recommendations
        show_recommendations(capabilities, all_caps, console)

        # Step 5: Context Priority
        context_priority = get_context_priority()

        # Step 6: Agent Instructions
        agent_instructions = get_agent_instructions()

        # Step 7: File Dependencies
        required_files, optional_files = get_file_dependencies()

        # Step 8: Preview & Confirm
        agent = AgentConfiguration(
            name=name,
            version="1.0.0",
            description=description,
            created=datetime.now().strftime("%Y-%m-%d"),
            author=author,
            capabilities=capabilities,
            context_priority=context_priority,
            agent_instructions=agent_instructions,
            required_files=required_files,
            optional_files=optional_files,
            tags=[],
            status="active"
        )

        if not preview_and_confirm(agent, console):
            retry = questionary.confirm(
                "Would you like to start over?",
                default=False,
                style=custom_style
            ).ask()

            if retry:
                return run_agent_creation_wizard(agents_dir, capabilities_dir)
            else:
                return None

        return agent

    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Agent creation cancelled by user{Colors.ENDC}")
        return None


def show_welcome(console: Optional[Console]) -> bool:
    """Show welcome screen and explanation"""

    welcome_text = """
# 🤖 Agent Creation Wizard

Welcome to the Proto Gear Agent Builder!

## What are Agents?

Agents are **custom AI configurations** composed of:
- **Capabilities**: Skills, workflows, and commands
- **Context Priority**: What the agent should focus on
- **Instructions**: Specific behavioral guidelines
- **File Dependencies**: Required project files

## Quick Start Options

**Use a Template**: Start from pre-configured agent (faster!)
- 7 templates: Backend, Frontend, Full-Stack, DevOps, QA, Testing, Minimal

**Build from Scratch**: Customize everything step-by-step
- Full control over all options

Let's get started!
"""

    if console:
        console.print(Panel(Markdown(welcome_text), border_style="cyan"))
    else:
        print(welcome_text)

    print()
    proceed = questionary.confirm(
        "Ready to create your agent?",
        default=True,
        style=custom_style
    ).ask()

    return proceed if proceed is not None else False


def ask_template_or_custom(console: Optional[Console]) -> Tuple[Optional[str], bool]:
    """
    Ask if user wants to use a template or build from scratch.

    Returns:
        Tuple of (template_name, use_template) where template_name is the chosen template
        or None if building from scratch, and use_template is True if using a template.
    """
    from .agent_templates import list_templates, get_template_description

    print(f"\n{Colors.HEADER}=== Choose Starting Point ==={Colors.ENDC}\n")

    # Build choices
    choices = [
        questionary.Choice(
            title="Build from scratch - Full customization (recommended for advanced users)",
            value="custom"
        ),
        questionary.Separator("--- OR START FROM TEMPLATE ---"),
    ]

    # Add template choices
    templates = list_templates()
    for idx, template_name in enumerate(templates, 1):
        desc = get_template_description(template_name)
        choices.append(
            questionary.Choice(
                title=f"{template_name:20} - {desc[:50]}...",
                value=template_name
            )
        )

    choice = questionary.select(
        "How would you like to start?",
        choices=choices,
        style=custom_style
    ).ask()

    if not choice or choice == "custom":
        print(f"\n{Colors.CYAN}Building custom agent from scratch...{Colors.ENDC}")
        return None, False
    else:
        print(f"\n{Colors.GREEN}Using template: {choice}{Colors.ENDC}")
        return choice, True


def get_basic_info() -> Tuple[str, str, str]:
    """Get basic agent information"""

    print(f"\n{Colors.HEADER}=== Step 1: Basic Information ==={Colors.ENDC}\n")

    # Agent name
    name = questionary.text(
        "Agent name:",
        instruction="(e.g., 'My Testing Agent', 'Backend Developer Agent')",
        style=custom_style
    ).ask()

    if not name:
        return "", "", ""

    # Description
    description = questionary.text(
        "Short description:",
        instruction="(one-line summary of what this agent does)",
        style=custom_style
    ).ask()

    if not description:
        return "", "", ""

    # Author (optional)
    author = questionary.text(
        "Author (optional):",
        instruction="(your name or team name)",
        default="",
        style=custom_style
    ).ask()

    return name or "", description or "", author or ""


def select_capabilities(
    all_caps: Dict[str, CapabilityMetadata],
    console: Optional[Console]
) -> AgentCapabilities:
    """Interactive capability selection"""

    print(f"\n{Colors.HEADER}=== Step 2: Select Capabilities ==={Colors.ENDC}\n")
    print("Choose capabilities for your agent. You can select multiple items.")
    print(f"{Colors.GRAY}Tip: Use arrow keys to navigate, space to select, enter to confirm{Colors.ENDC}\n")

    # Group capabilities
    skills = {k: v for k, v in all_caps.items() if v.type == CapabilityType.SKILL}
    workflows = {k: v for k, v in all_caps.items() if v.type == CapabilityType.WORKFLOW}
    commands = {k: v for k, v in all_caps.items() if v.type == CapabilityType.COMMAND}

    # Select skills
    print(f"{Colors.CYAN}Skills{Colors.ENDC} (core competencies):")
    skill_choices = [
        questionary.Choice(
            title=f"{v.name} - {v.description[:60]}...",
            value=k.replace("skills/", ""),
            checked=False
        )
        for k, v in sorted(skills.items())
    ]

    selected_skills = questionary.checkbox(
        "Select skills:",
        choices=skill_choices,
        style=custom_style
    ).ask()

    if selected_skills is None:
        return AgentCapabilities()

    # Select workflows
    print(f"\n{Colors.CYAN}Workflows{Colors.ENDC} (development processes):")
    workflow_choices = [
        questionary.Choice(
            title=f"{v.name} - {v.description[:60]}...",
            value=k.replace("workflows/", ""),
            checked=False
        )
        for k, v in sorted(workflows.items())
    ]

    selected_workflows = questionary.checkbox(
        "Select workflows:",
        choices=workflow_choices,
        style=custom_style
    ).ask()

    if selected_workflows is None:
        return AgentCapabilities()

    # Select commands
    print(f"\n{Colors.CYAN}Commands{Colors.ENDC} (automation tools):")
    command_choices = [
        questionary.Choice(
            title=f"{v.name} - {v.description[:60]}...",
            value=k.replace("commands/", ""),
            checked=False
        )
        for k, v in sorted(commands.items())
    ]

    selected_commands = questionary.checkbox(
        "Select commands:",
        choices=command_choices,
        style=custom_style
    ).ask()

    if selected_commands is None:
        return AgentCapabilities()

    return AgentCapabilities(
        skills=selected_skills,
        workflows=selected_workflows,
        commands=selected_commands
    )


def validate_capability_selections(
    capabilities: AgentCapabilities,
    all_caps: Dict[str, CapabilityMetadata]
) -> List[str]:
    """Validate capability selections"""

    errors = []

    # Check all capabilities exist
    for cap_id in capabilities.all_capabilities():
        if cap_id not in all_caps:
            errors.append(f"Capability not found: {cap_id}")

    if errors:
        return errors

    # Check for circular dependencies
    try:
        from .capability_metadata import CapabilityValidator
        for cap_id in capabilities.all_capabilities():
            cycle = CapabilityValidator.detect_circular_dependencies(cap_id, all_caps)
            if cycle:
                errors.append(f"Circular dependency: {' -> '.join(cycle)}")
    except Exception as e:
        errors.append(f"Error checking dependencies: {e}")

    # Check for conflicts
    try:
        conflicts = CompositionEngine.detect_conflicts(
            capabilities.all_capabilities(),
            all_caps
        )
        if conflicts:
            for c1, c2, reason in conflicts:
                errors.append(f"Conflict between {c1} and {c2}: {reason}")
    except Exception as e:
        errors.append(f"Error checking conflicts: {e}")

    return errors


def show_recommendations(
    capabilities: AgentCapabilities,
    all_caps: Dict[str, CapabilityMetadata],
    console: Optional[Console]
):
    """Show smart capability recommendations"""

    try:
        recommendations = CompositionEngine.get_recommended_capabilities(
            capabilities.all_capabilities(),
            all_caps
        )

        if recommendations:
            print(f"\n{Colors.CYAN}💡 Smart Recommendations{Colors.ENDC}")
            print(f"Based on your selections, you might also want:\n")

            for rec in recommendations[:5]:
                metadata = all_caps[rec]
                print(f"  • {metadata.name} - {metadata.description[:50]}...")

            if len(recommendations) > 5:
                print(f"  ... and {len(recommendations) - 5} more")

            add_recommended = questionary.confirm(
                "\nWould you like to add any of these? (you can add them manually later)",
                default=False,
                style=custom_style
            ).ask()

            if add_recommended:
                print(f"{Colors.YELLOW}Note: Manually edit the agent file to add these capabilities{Colors.ENDC}")

    except Exception:
        pass  # Recommendations are optional


def get_context_priority() -> List[str]:
    """Get context priority list"""

    print(f"\n{Colors.HEADER}=== Step 3: Context Priority ==={Colors.ENDC}\n")
    print("Define what your agent should focus on (in order of importance).")
    print(f"{Colors.GRAY}Examples: 'Read README.md first', 'Check PROJECT_STATUS.md'{Colors.ENDC}\n")

    use_template = questionary.confirm(
        "Use default context priority template?",
        default=True,
        style=custom_style
    ).ask()

    if use_template:
        return [
            "Read PROJECT_STATUS.md for current work",
            "Review relevant files for the task",
            "Check for existing patterns in codebase"
        ]
    else:
        priorities = []
        print("\nEnter context priorities (empty line to finish):")

        for i in range(1, 6):  # Max 5 priorities
            priority = questionary.text(
                f"Priority {i}:",
                instruction="(or press enter to finish)",
                style=custom_style
            ).ask()

            if not priority:
                break

            priorities.append(priority)

        return priorities


def get_agent_instructions() -> List[str]:
    """Get agent instruction list"""

    print(f"\n{Colors.HEADER}=== Step 4: Agent Instructions ==={Colors.ENDC}\n")
    print("Define specific behavioral guidelines for your agent.")
    print(f"{Colors.GRAY}Examples: 'Follow TDD methodology', 'Update docs as you code'{Colors.ENDC}\n")

    use_template = questionary.confirm(
        "Use default instructions template?",
        default=True,
        style=custom_style
    ).ask()

    if use_template:
        return [
            "Follow project conventions and best practices",
            "Update PROJECT_STATUS.md as work progresses",
            "Write clear, maintainable code"
        ]
    else:
        instructions = []
        print("\nEnter agent instructions (empty line to finish):")

        for i in range(1, 8):  # Max 7 instructions
            instruction = questionary.text(
                f"Instruction {i}:",
                instruction="(or press enter to finish)",
                style=custom_style
            ).ask()

            if not instruction:
                break

            instructions.append(instruction)

        return instructions


def get_file_dependencies() -> Tuple[List[str], List[str]]:
    """Get file dependency lists"""

    print(f"\n{Colors.HEADER}=== Step 5: File Dependencies ==={Colors.ENDC}\n")
    print("Specify files your agent needs (optional).\n")

    add_files = questionary.confirm(
        "Add file dependencies?",
        default=False,
        style=custom_style
    ).ask()

    if not add_files:
        return ["PROJECT_STATUS.md"], []

    # Required files
    required = []
    print("\nRequired files (must exist):")
    for i in range(1, 4):
        file = questionary.text(
            f"Required file {i}:",
            instruction="(or press enter to skip)",
            style=custom_style
        ).ask()

        if not file:
            break
        required.append(file)

    # Optional files
    optional = []
    print("\nOptional files (nice to have):")
    for i in range(1, 4):
        file = questionary.text(
            f"Optional file {i}:",
            instruction="(or press enter to skip)",
            style=custom_style
        ).ask()

        if not file:
            break
        optional.append(file)

    return required or ["PROJECT_STATUS.md"], optional


def preview_and_confirm(agent: AgentConfiguration, console: Optional[Console]) -> bool:
    """Show preview and get confirmation"""

    print(f"\n{Colors.HEADER}=== Step 6: Preview & Confirm ==={Colors.ENDC}\n")

    # Show summary
    print(f"{Colors.CYAN}Agent Configuration:{Colors.ENDC}")
    print(f"  Name: {agent.name}")
    print(f"  Description: {agent.description}")
    print(f"  Author: {agent.author or '(not specified)'}")
    print(f"  Version: {agent.version}")
    print(f"  Created: {agent.created}")
    print(f"\n{Colors.CYAN}Capabilities:{Colors.ENDC}")
    print(f"  Skills ({len(agent.capabilities.skills)}): {', '.join(agent.capabilities.skills) or 'none'}")
    print(f"  Workflows ({len(agent.capabilities.workflows)}): {', '.join(agent.capabilities.workflows) or 'none'}")
    print(f"  Commands ({len(agent.capabilities.commands)}): {', '.join(agent.capabilities.commands) or 'none'}")
    print(f"\n{Colors.CYAN}Context Priority:{Colors.ENDC}")
    for i, priority in enumerate(agent.context_priority, 1):
        print(f"  {i}. {priority}")
    print(f"\n{Colors.CYAN}Agent Instructions:{Colors.ENDC}")
    for i, instruction in enumerate(agent.agent_instructions, 1):
        print(f"  {i}. {instruction}")

    if agent.required_files:
        print(f"\n{Colors.CYAN}Required Files:{Colors.ENDC}")
        for file in agent.required_files:
            print(f"  - {file}")

    print()

    confirm = questionary.confirm(
        "Create this agent?",
        default=True,
        style=custom_style
    ).ask()

    return confirm if confirm is not None else False
