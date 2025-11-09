#!/usr/bin/env python3
"""
Interactive Wizard Module for Proto Gear
Provides rich, beautiful CLI interactions with arrow key navigation
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

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
    from rich.layout import Layout
    from rich.text import Text
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


# Preset Configurations for v0.5.2+
PRESETS = {
    'quick': {
        'name': 'Quick Start',
        'emoji': '⚡',
        'ascii': '[QUICK]',
        'description': 'Recommended for most projects - Core templates + capabilities',
        'details': [
            'AGENTS.md - AI agent collaboration',
            'PROJECT_STATUS.md - State tracking',
            'TESTING.md - TDD patterns',
            'BRANCHING.md - If git detected',
            '.proto-gear/ - Full capability system'
        ],
        'config': {
            'core': ['AGENTS', 'PROJECT_STATUS', 'TESTING'],
            'branching': 'auto',  # Only if git detected
            'with_all': False,  # Individual templates
            'capabilities': True,
        }
    },
    'full': {
        'name': 'Full Setup (All Templates)',
        'emoji': '📦',
        'ascii': '[FULL]',
        'description': 'Everything - All 8 templates + full capabilities',
        'details': [
            'AGENTS.md + PROJECT_STATUS.md (always included)',
            'TESTING.md - TDD patterns',
            'BRANCHING.md - Git workflow conventions',
            'CONTRIBUTING.md - Contribution guidelines',
            'SECURITY.md - Security policy',
            'ARCHITECTURE.md - System design docs',
            'CODE_OF_CONDUCT.md - Community guidelines',
            '.proto-gear/ - Full capability system'
        ],
        'config': {
            'core': ['AGENTS', 'PROJECT_STATUS'],
            'branching': True,
            'with_all': True,  # Generate ALL templates
            'capabilities': True,
        }
    },
    'minimal': {
        'name': 'Minimal',
        'emoji': '🎯',
        'ascii': '[MINIMAL]',
        'description': 'Just the essentials - Core templates only',
        'details': [
            'AGENTS.md - AI agent collaboration',
            'PROJECT_STATUS.md - State tracking',
            'No additional templates',
            'No capabilities'
        ],
        'config': {
            'core': ['AGENTS', 'PROJECT_STATUS'],
            'branching': False,
            'with_all': False,
            'capabilities': False,
        }
    },
    'custom': {
        'name': 'Custom',
        'emoji': '🔧',
        'ascii': '[CUSTOM]',
        'description': 'Full control - Choose exactly what you want',
        'details': [
            'Step-by-step configuration',
            'Select individual templates',
            'Control all options',
            'Maximum flexibility'
        ],
        'config': None,  # Triggers custom wizard flow
    }
}


# Encoding-safe characters with fallbacks
def get_safe_chars():
    """Get encoding-safe characters for console output"""
    try:
        # Test if console supports Unicode
        sys.stdout.write("\u2713")
        sys.stdout.flush()
        # If successful, use Unicode characters
        return {
            'check': '✓',
            'cross': '✗',
            'bullet': '•',
            'line': '─',
            'wrench': '🔧',
            'clipboard': '📋',
            'ticket': '🎫',
            'memo': '📝',
            'chart': '📊',
        }
    except (UnicodeEncodeError, AttributeError):
        # Fallback to ASCII
        return {
            'check': '[Y]',
            'cross': '[N]',
            'bullet': '*',
            'line': '-',
            'wrench': '[SETUP]',
            'clipboard': '[GIT]',
            'ticket': '[TICKET]',
            'memo': '[CONFIG]',
            'chart': '[PROJECT]',
        }


# Get encoding-safe characters once at module load
CHARS = get_safe_chars()


# Custom style for questionary prompts - Clean UX without background colors
PROTO_GEAR_STYLE = Style([
    ('qmark', 'fg:#5f87d7 bold'),                    # Question mark color
    ('question', 'bold'),                             # Question text
    ('answer', 'fg:#00d787 bold'),                   # User's answer
    ('pointer', 'fg:#00d787 bold'),                  # Selection pointer (arrow)
    ('highlighted', 'fg:#00d787 bold noreverse'),    # Highlighted choice - NO background/reverse
    ('selected', 'fg:#00d787 noreverse'),            # Selected checkbox items - NO background/reverse
    ('separator', 'fg:#6c6c6c'),                     # Separator lines
    ('instruction', 'fg:#6c6c6c'),                   # Instructions
    ('text', ''),                                     # Plain text (default terminal color)
    ('disabled', 'fg:#858585 italic'),               # Disabled choices
    ('checkbox', 'fg:#00d787'),                      # Checkbox icon
    ('checkbox-selected', 'fg:#00d787 bold'),        # Selected checkbox icon
    # Additional prompt_toolkit classes to prevent backgrounds
    ('', 'noreverse'),                               # Global: no reverse video
])


class RichWizard:
    """Enhanced interactive wizard using Rich and Questionary"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.config = {}

    def clear_screen(self):
        """Clear the terminal screen for single-page app experience"""
        if self.console:
            self.console.clear()
        else:
            # Fallback: ANSI escape code or os-specific clear
            import os
            os.system('cls' if os.name == 'nt' else 'clear')

    def show_step_header(self, step: int, total_steps: int, step_name: str, project_info: Dict, current_dir: Path):
        """Show consistent step header with progress and project context"""
        if self.console:
            # Progress indicator
            self.console.print(f"\n[bold cyan]ProtoGear Setup[/bold cyan] [dim]│[/dim] Step {step} of {total_steps}: [bold]{step_name}[/bold]")
            self.console.print("[dim]" + "─" * 60 + "[/dim]")

            # Project context (compact)
            project_type = project_info.get('type', 'Generic')
            framework = project_info.get('framework', '')
            context = f"[dim]Project:[/dim] {current_dir.name} [dim]│[/dim] [dim]Type:[/dim] {project_type}"
            if framework:
                context += f" [dim]({framework})[/dim]"
            self.console.print(context)
            self.console.print()
        else:
            print(f"\n=== ProtoGear Setup - Step {step}/{total_steps}: {step_name} ===")
            print(f"Project: {current_dir.name} | Type: {project_info.get('type', 'Generic')}")
            if project_info.get('framework'):
                print(f"Framework: {project_info['framework']}")
            print()

    def print_panel(self, content, title: str = "", border_style: str = "cyan"):
        """Print content in a rich panel"""
        if self.console:
            panel = Panel(
                content,
                title=f"[bold]{title}[/bold]" if title else "",
                border_style=border_style,
                box=box.ROUNDED,
                padding=(1, 2)
            )
            self.console.print(panel)
        else:
            # Fallback to simple print
            if title:
                print(f"\n{title}")
                print("=" * 60)
            print(content)
            print()

    def create_project_info_panel(self, project_info: Dict, git_config: Dict, current_dir: Path) -> str:
        """Create formatted project information display"""
        if not RICH_AVAILABLE:
            # Fallback to simple formatting
            lines = []
            lines.append(f"Directory: {current_dir.absolute()}")
            if project_info.get('detected'):
                lines.append(f"Type: {project_info['type']}")
                if project_info.get('framework'):
                    lines.append(f"Framework: {project_info['framework']}")
            else:
                lines.append("Type: Generic Project")

            if git_config['is_git_repo']:
                lines.append(f"Git: {CHARS['check']} Initialized")
                if git_config['has_remote']:
                    lines.append(f"Remote: {CHARS['check']} {git_config['remote_name']}")
                else:
                    lines.append(f"Remote: {CHARS['cross']} None (local-only)")
            else:
                lines.append(f"Git: {CHARS['cross']} Not initialized")

            return "\n".join(lines)

        # Rich formatted output
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Directory", str(current_dir.name))

        if project_info.get('detected'):
            table.add_row("Type", project_info['type'])
            if project_info.get('framework'):
                table.add_row("Framework", project_info['framework'])
        else:
            table.add_row("Type", "[yellow]Generic Project[/yellow]")

        if git_config['is_git_repo']:
            table.add_row("Git", f"{CHARS['check']} Initialized")
            if git_config['has_remote']:
                table.add_row("Remote", f"{CHARS['check']} {git_config['remote_name']}")
            else:
                table.add_row("Remote", f"[yellow]{CHARS['cross']} None (local-only)[/yellow]")
        else:
            table.add_row("Git", f"[yellow]{CHARS['cross']} Not initialized[/yellow]")

        return table

    def ask_preset_selection(self, git_detected: bool) -> str:
        """
        Ask user to select a preset configuration
        Returns: preset key ('quick', 'full', 'minimal', 'custom')
        """
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple selection
            print(f"\n{CHARS['wrench']} Setup Configuration")
            print("-" * 60)
            print("\nChoose a preset:")
            print(f"1. {PRESETS['quick']['ascii']} {PRESETS['quick']['name']} (Recommended)")
            print(f"   {PRESETS['quick']['description']}")
            print(f"\n2. {PRESETS['full']['ascii']} {PRESETS['full']['name']}")
            print(f"   {PRESETS['full']['description']}")
            print(f"\n3. {PRESETS['minimal']['ascii']} {PRESETS['minimal']['name']}")
            print(f"   {PRESETS['minimal']['description']}")
            print(f"\n4. {PRESETS['custom']['ascii']} {PRESETS['custom']['name']}")
            print(f"   {PRESETS['custom']['description']}")

            while True:
                response = input("\nSelect preset (1-4, default=1): ").strip()
                if not response:
                    return 'quick'
                if response in ['1', 'quick']:
                    return 'quick'
                elif response in ['2', 'full']:
                    return 'full'
                elif response in ['3', 'minimal', 'min']:
                    return 'minimal'
                elif response in ['4', 'custom']:
                    return 'custom'
                else:
                    print("Invalid choice. Please enter 1-4.")

        # Enhanced questionary version
        description = [
            "",
            "Proto Gear can be configured in multiple ways.",
            "Choose a preset or customize your setup:",
            ""
        ]

        if self.console:
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['wrench']} Setup Configuration",
                border_style="cyan"
            )

        # Build choices with details
        choices = []
        for key in ['quick', 'full', 'minimal', 'custom']:
            preset = PRESETS[key]
            # Use emoji or ASCII fallback
            icon = preset['emoji'] if sys.stdout.encoding and 'UTF' in sys.stdout.encoding.upper() else preset['ascii']
            choice_text = f"{icon} {preset['name']} - {preset['description']}"
            choices.append(questionary.Choice(choice_text, value=key))

        answer = questionary.select(
            "Select configuration preset:",
            choices=choices,
            default=choices[0],  # Quick Start is default
            style=PROTO_GEAR_STYLE if QUESTIONARY_AVAILABLE else None
        ).ask()

        return answer if answer is not None else 'quick'

    def show_preset_preview(self, preset_key: str, git_detected: bool) -> bool:
        """
        Show what the preset will create and ask for confirmation
        Returns: True to continue, False to go back
        """
        preset = PRESETS[preset_key]

        if not RICH_AVAILABLE:
            # Fallback display
            print(f"\n{CHARS['memo']} Preset: {preset['name']}")
            print("=" * 60)
            print(f"\n{preset['description']}\n")
            print("What will be created:")
            for detail in preset['details']:
                print(f"  {CHARS['bullet']} {detail}")
            print()

            while True:
                response = input("Continue with this preset? (y/n, or 'b' to go back): ").lower()
                if response in ['y', 'yes', '']:
                    return True
                elif response in ['n', 'no']:
                    return False
                elif response == 'b':
                    return False
                else:
                    print("Please enter 'y', 'n', or 'b'")

        # Rich version
        icon = preset['emoji'] if sys.stdout.encoding and 'UTF' in sys.stdout.encoding.upper() else preset['ascii']

        # Build preview content
        content_lines = [
            f"[bold]{preset['description']}[/bold]",
            "",
            "[bold cyan]What will be created:[/bold cyan]",
            ""
        ]

        for detail in preset['details']:
            # Handle git-conditional branching
            if 'If git detected' in detail:
                if git_detected:
                    content_lines.append(f"  {CHARS['check']} {detail.replace('If git detected', 'Git detected')}")
                else:
                    content_lines.append(f"  [dim]{CHARS['cross']} {detail.replace('If git detected', 'No git repo')}")
            else:
                content_lines.append(f"  {CHARS['bullet']} {detail}")

        self.print_panel(
            "\n".join(content_lines),
            title=f"{icon} {preset['name']}",
            border_style="cyan"
        )

        answer = questionary.select(
            "What would you like to do?",
            choices=[
                questionary.Choice(f"{CHARS['check']} Continue with this preset", value='continue'),
                questionary.Choice(f"{CHARS['cross']} Go back to preset selection", value='back'),
            ],
            style=PROTO_GEAR_STYLE if QUESTIONARY_AVAILABLE else None
        ).ask()

        return answer == 'continue'

    def ask_capabilities_system(self) -> bool:
        """Ask user if they want Universal Capabilities System"""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple y/n prompt
            print(f"\n{CHARS['wrench']} Universal Capabilities System")
            print("-" * 30)
            print("Proto Gear can generate a modular capability system that allows")
            print("AI agents to dynamically load and use specialized capabilities.")
            while True:
                response = input("\nGenerate .proto-gear/ capability system? (y/n): ").lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                print("Please enter 'y' or 'n'")

        # Enhanced questionary prompt
        description = [
            "",
            "Proto Gear can generate a modular capability system that allows",
            "AI agents to dynamically load and use specialized capabilities.",
            "",
            "[dim]This includes:[/dim]",
            f"  {CHARS['bullet']} Capability module system (.proto-gear/capabilities/)",
            f"  {CHARS['bullet']} Dynamic capability loading and registration",
            f"  {CHARS['bullet']} Configuration management (config.yaml)",
            f"  {CHARS['bullet']} Built-in capabilities (git, testing, deployment)",
            ""
        ]

        if self.console:
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['wrench']} Universal Capabilities System",
                border_style="cyan"
            )

        answer = questionary.select(
            "Generate .proto-gear/ capability system?",
            choices=[
                questionary.Choice(f"{CHARS['check']} Yes - Generate capability system", value=True),
                questionary.Choice(f"{CHARS['cross']} No - Skip this step", value=False)
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys to navigate, Enter to select)"
        ).ask()

        return answer if answer is not None else False

    def ask_core_templates_selection(self) -> Dict[str, bool]:
        """
        Ask user which core templates to generate (Custom path)
        Returns dict with template selections
        """
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple prompts
            print(f"\n{CHARS['memo']} Template Selection")
            print("-" * 50)
            print("Select which templates to generate:")
            print(f"  {CHARS['bullet']} AGENTS.md and PROJECT_STATUS.md are always included")
            print("\nAdditional templates:")
            print("  1. TESTING.md - TDD workflow and testing patterns")
            print("  2. CONTRIBUTING.md - Contribution guidelines for open-source")
            print("  3. SECURITY.md - Security policy and vulnerability reporting")
            print("  4. ARCHITECTURE.md - System design documentation")
            print("  5. CODE_OF_CONDUCT.md - Community guidelines")
            print("  A. Select ALL additional templates")

            response = input("\nSelect templates (e.g., '1,2,5' or 'A' for all): ").strip().upper()

            if response == 'A':
                return {
                    'AGENTS': True,
                    'PROJECT_STATUS': True,
                    'TESTING': True,
                    'CONTRIBUTING': True,
                    'SECURITY': True,
                    'ARCHITECTURE': True,
                    'CODE_OF_CONDUCT': True,
                    'with_all': True
                }

            selected = set(response.replace(' ', '').split(','))
            return {
                'AGENTS': True,
                'PROJECT_STATUS': True,
                'TESTING': '1' in selected,
                'CONTRIBUTING': '2' in selected,
                'SECURITY': '3' in selected,
                'ARCHITECTURE': '4' in selected,
                'CODE_OF_CONDUCT': '5' in selected,
                'with_all': False
            }

        # Enhanced selection with questionary
        if self.console:
            description = [
                "",
                f"[dim]AGENTS.md and PROJECT_STATUS.md are always included (core functionality)[/dim]",
                "",
                "Select additional templates to generate:",
                ""
            ]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['memo']} Template Selection",
                border_style="cyan"
            )

        # Use checkbox for multi-select
        choices = questionary.checkbox(
            "Select additional templates:",
            choices=[
                questionary.Choice("TESTING.md - TDD workflow and testing patterns", value='TESTING', checked=True),
                questionary.Choice("CONTRIBUTING.md - Contribution guidelines for open-source", value='CONTRIBUTING', checked=False),
                questionary.Choice("SECURITY.md - Security policy and vulnerability reporting", value='SECURITY', checked=False),
                questionary.Choice("ARCHITECTURE.md - System design documentation", value='ARCHITECTURE', checked=False),
                questionary.Choice("CODE_OF_CONDUCT.md - Community guidelines", value='CODE_OF_CONDUCT', checked=False),
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)"
        ).ask()

        if choices is None:
            choices = []

        # Check if user selected all
        all_selected = len(choices) == 5

        return {
            'AGENTS': True,
            'PROJECT_STATUS': True,
            'TESTING': 'TESTING' in choices,
            'CONTRIBUTING': 'CONTRIBUTING' in choices,
            'SECURITY': 'SECURITY' in choices,
            'ARCHITECTURE': 'ARCHITECTURE' in choices,
            'CODE_OF_CONDUCT': 'CODE_OF_CONDUCT' in choices,
            'with_all': all_selected
        }

    def ask_git_workflow_options(self, git_config: Dict, current_dir: Path) -> Dict:
        """
        Ask user about Git workflow configuration options (Custom path)
        Returns dict with git-related configuration
        """
        git_detected = git_config.get('is_git_repo', False)

        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple prompts
            print(f"\n{CHARS['clipboard']} Git Workflow Configuration")
            print("-" * 50)

            if git_detected:
                print(f"{CHARS['check']} Git repository detected")
                branching = input("\nGenerate BRANCHING.md? (y/n): ").lower() in ['y', 'yes']

                if branching:
                    suggested_prefix = current_dir.name.upper().replace('-', '').replace('_', '')[:15]
                    if not suggested_prefix or len(suggested_prefix) < 2:
                        suggested_prefix = 'PROJ'

                    print(f"\nTicket prefix for branch naming (e.g., feature/{suggested_prefix}-123-description)")
                    prefix = input(f"Enter ticket prefix [{suggested_prefix}]: ").strip()
                    ticket_prefix = prefix if prefix else suggested_prefix
                else:
                    ticket_prefix = None
            else:
                print(f"{CHARS['cross']} No git repository detected - skipping Git workflow")
                branching = False
                ticket_prefix = None

            return {
                'with_branching': branching,
                'ticket_prefix': ticket_prefix
            }

        # Enhanced selection with questionary
        if self.console:
            status = f"[green]{CHARS['check']} Git detected[/green]" if git_detected else f"[yellow]{CHARS['cross']} No git repository[/yellow]"
            description = [
                "",
                status,
                "",
                "Configure Git workflow options:",
                ""
            ]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['clipboard']} Git Workflow",
                border_style="cyan"
            )

        if not git_detected:
            return {
                'with_branching': False,
                'ticket_prefix': None
            }

        # Ask about BRANCHING.md
        generate_branching = questionary.confirm(
            "Generate BRANCHING.md (branch naming & commit conventions)?",
            default=True,
            style=PROTO_GEAR_STYLE
        ).ask()

        if not generate_branching:
            return {
                'with_branching': False,
                'ticket_prefix': None
            }

        # Ask for ticket prefix
        suggested_prefix = current_dir.name.upper().replace('-', '').replace('_', '')[:15]
        if not suggested_prefix or len(suggested_prefix) < 2:
            suggested_prefix = 'PROJ'

        ticket_prefix = questionary.text(
            "Ticket prefix for branch naming:",
            default=suggested_prefix,
            validate=lambda text: len(text) > 0,
            style=PROTO_GEAR_STYLE,
            instruction=f"(Used in: feature/{suggested_prefix}-123-description)"
        ).ask()

        return {
            'with_branching': True,
            'ticket_prefix': ticket_prefix if ticket_prefix else suggested_prefix
        }

    def ask_capabilities_selection(self) -> Dict:
        """
        Ask user about capabilities with granular control (Custom path)
        Returns dict with capabilities configuration
        """
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple prompts
            print(f"\n{CHARS['wrench']} Universal Capabilities System")
            print("-" * 50)
            print("The capability system provides modular patterns for AI agents.")

            include = input("\nInclude capabilities? (y/n): ").lower() in ['y', 'yes']

            if not include:
                return {'enabled': False}

            # Ask about granular selection
            print("\nCapability categories:")
            print(f"  1. All categories (Skills, Workflows, Commands)")
            print(f"  2. Select specific categories")

            choice = input("\nChoice [1]: ").strip()

            if choice == '2':
                skills = input("Include Skills (TDD methodology)? (y/n): ").lower() in ['y', 'yes']
                workflows = input("Include Workflows (Feature development)? (y/n): ").lower() in ['y', 'yes']
                commands = input("Include Commands (Create ticket)? (y/n): ").lower() in ['y', 'yes']

                return {
                    'enabled': True,
                    'skills': skills,
                    'workflows': workflows,
                    'commands': commands
                }
            else:
                return {
                    'enabled': True,
                    'skills': True,
                    'workflows': True,
                    'commands': True
                }

        # Enhanced selection with questionary
        if self.console:
            description = [
                "",
                "The capability system provides modular, reusable patterns for AI agents.",
                "",
                "[dim]Categories available:[/dim]",
                f"  {CHARS['bullet']} [cyan]Skills[/cyan] - TDD methodology and testing patterns",
                f"  {CHARS['bullet']} [cyan]Workflows[/cyan] - Feature development process (7 steps)",
                f"  {CHARS['bullet']} [cyan]Commands[/cyan] - Ticket creation and documentation",
                ""
            ]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['wrench']} Universal Capabilities",
                border_style="cyan"
            )

        # Ask if user wants capabilities at all
        include_capabilities = questionary.confirm(
            "Include .proto-gear/ capability system?",
            default=True,
            style=PROTO_GEAR_STYLE
        ).ask()

        if not include_capabilities:
            return {'enabled': False}

        # Ask about granular selection
        selection_type = questionary.select(
            "How would you like to configure capabilities?",
            choices=[
                questionary.Choice(f"{CHARS['check']} All categories (Skills, Workflows, Commands)", value='all'),
                questionary.Choice(f"{CHARS['wrench']} Select specific categories", value='custom')
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys, Enter to select)"
        ).ask()

        if selection_type == 'all':
            return {
                'enabled': True,
                'skills': True,
                'workflows': True,
                'commands': True
            }

        # Custom category selection
        categories = questionary.checkbox(
            "Select capability categories:",
            choices=[
                questionary.Choice("Skills - TDD methodology", value='skills', checked=True),
                questionary.Choice("Workflows - Feature development", value='workflows', checked=True),
                questionary.Choice("Commands - Ticket creation", value='commands', checked=True)
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)"
        ).ask()

        if categories is None:
            categories = []

        return {
            'enabled': True,
            'skills': 'skills' in categories,
            'workflows': 'workflows' in categories,
            'commands': 'commands' in categories
        }

    def ask_branching_strategy(self, git_config: Dict) -> bool:
        """Ask user if they want branching strategy with arrow key selection"""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple y/n prompt
            print(f"\n{CHARS['clipboard']} Branching & Git Workflow")
            print("-" * 30)
            print("Proto Gear can generate a comprehensive branching strategy document")
            print("that defines Git workflow conventions and commit message standards.")
            while True:
                response = input("\nGenerate BRANCHING.md? (y/n): ").lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                print("Please enter 'y' or 'n'")

        # Enhanced questionary prompt
        description = [
            "",
            "Proto Gear can generate a comprehensive branching strategy document",
            "that defines Git workflow conventions and commit message standards.",
            "",
            "[dim]This includes:[/dim]",
            f"  {CHARS['bullet']} Branch naming conventions (feature/*, bugfix/*, hotfix/*)",
            f"  {CHARS['bullet']} Conventional commit message format",
            f"  {CHARS['bullet']} Workflow examples for AI agents",
            f"  {CHARS['bullet']} PR templates and merge strategies",
            ""
        ]

        if git_config['is_git_repo']:
            description.append(f"[green]{CHARS['check']} Git repository detected - branching strategy recommended[/green]")
        else:
            description.append("[yellow]! No Git repository - you can still generate the strategy for future use[/yellow]")

        if self.console:
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['clipboard']} Branching & Git Workflow",
                border_style="cyan"
            )

        answer = questionary.select(
            "Generate BRANCHING.md?",
            choices=[
                questionary.Choice(f"{CHARS['check']} Yes - Generate branching strategy", value=True),
                questionary.Choice(f"{CHARS['cross']} No - Skip this step", value=False)
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys to navigate, Enter to select)"
        ).ask()

        return answer if answer is not None else False

    def ask_ticket_prefix(self, suggested_prefix: str) -> str:
        """Ask for ticket prefix with validation"""
        if not QUESTIONARY_AVAILABLE:
            # Fallback
            print(f"\n{CHARS['ticket']} Ticket Prefix Configuration")
            print("-" * 30)
            print(f"Suggested prefix: {suggested_prefix}")
            response = input(f"Enter ticket prefix (press Enter for '{suggested_prefix}'): ").strip().upper()

            if response:
                if response.isalnum() and 2 <= len(response) <= 10:
                    return response
                else:
                    print(f"Invalid prefix. Using suggested: {suggested_prefix}")
                    return suggested_prefix
            return suggested_prefix

        # Enhanced questionary prompt
        if self.console:
            description = [
                "",
                "Tickets and branches use a prefix for identification.",
                "[dim]Examples: PROJ-001, APP-042, MYAPP-123[/dim]",
                "",
                f"[green]Suggested prefix: {suggested_prefix}[/green]",
                ""
            ]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['ticket']} Ticket Prefix Configuration",
                border_style="cyan"
            )

        def validate_prefix(text):
            if not text:
                return True  # Empty is OK (will use default)
            if not text.isalnum():
                return "Prefix must be alphanumeric (no spaces or special characters)"
            if len(text) < 2 or len(text) > 10:
                return "Prefix must be between 2 and 10 characters"
            return True

        answer = questionary.text(
            f"Enter ticket prefix (or press Enter for '{suggested_prefix}'):",
            validate=validate_prefix,
            style=PROTO_GEAR_STYLE,
            instruction=f"Press Enter for default ({suggested_prefix})"
        ).ask()

        if answer and answer.strip():
            result = answer.strip().upper()
            if self.console:
                self.console.print(f"[green]{CHARS['check']} Using prefix: {result}[/green]\n")
            return result
        else:
            if self.console:
                self.console.print(f"[green]{CHARS['check']} Using suggested prefix: {suggested_prefix}[/green]\n")
            return suggested_prefix

    def show_configuration_summary(self, config: Dict, project_info: Dict, current_dir: Path) -> bool:
        """Display configuration summary and ask for confirmation"""
        preset = config.get('preset', 'custom')

        if not RICH_AVAILABLE:
            # Fallback
            print(f"\n{CHARS['memo']} Configuration Summary")
            print("=" * 60)
            if preset != 'custom':
                preset_info = PRESETS.get(preset, {})
                print(f"Preset: {preset_info.get('ascii', '')} {preset_info.get('name', preset)}")
            print(f"Project: {current_dir.name}")
            print(f"Type: {project_info.get('type', 'Generic')}")
            if project_info.get('framework'):
                print(f"Framework: {project_info['framework']}")

            print("\nFiles to be created:")
            print(f"  {CHARS['check']} AGENTS.md (AI agent integration guide)")
            print(f"  {CHARS['check']} PROJECT_STATUS.md (Project state tracking)")

            if config.get('with_branching'):
                print(f"  {CHARS['check']} BRANCHING.md (Git workflow conventions)")
                print(f"\nTicket Prefix: {config['ticket_prefix']}")
            else:
                print(f"  {CHARS['cross']} BRANCHING.md (not selected)")

            if config.get('with_capabilities'):
                print(f"  {CHARS['check']} .proto-gear/ (Universal Capabilities System)")
            else:
                print(f"  {CHARS['cross']} .proto-gear/ (not selected)")

            while True:
                response = input("\nProceed with setup? (y/n): ").lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                print("Please enter 'y' or 'n'")

        # Rich formatted summary
        table = Table(show_header=True, box=box.ROUNDED, title="Configuration", title_style="bold cyan")
        table.add_column("Setting", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="green")

        # Show preset if not custom
        if preset != 'custom':
            preset_info = PRESETS.get(preset, {})
            preset_display = f"{preset_info.get('emoji', '')} {preset_info.get('name', preset)}"
            table.add_row("Preset", preset_display)

        table.add_row("Project", current_dir.name)
        table.add_row("Type", project_info.get('type', 'Generic'))
        if project_info.get('framework'):
            table.add_row("Framework", project_info['framework'])
        table.add_row("Branching", f"{CHARS['check']} Enabled" if config.get('with_branching') else f"{CHARS['cross']} Disabled")
        if config.get('with_branching'):
            table.add_row("Ticket Prefix", config.get('ticket_prefix', 'N/A'))
        table.add_row("Capabilities", f"{CHARS['check']} Enabled" if config.get('with_capabilities') else f"{CHARS['cross']} Disabled")

        files_list = [
            f"{CHARS['check']} AGENTS.md (AI agent integration guide)",
            f"{CHARS['check']} PROJECT_STATUS.md (Project state tracking)"
        ]

        # Handle with_all flag (v0.5.2+)
        with_all = config.get('with_all', False)

        if with_all:
            # All templates selected
            files_list.append(f"{CHARS['check']} TESTING.md (TDD workflow)")
            files_list.append(f"{CHARS['check']} BRANCHING.md (Git workflow conventions)")
            files_list.append(f"{CHARS['check']} CONTRIBUTING.md (Contribution guidelines)")
            files_list.append(f"{CHARS['check']} SECURITY.md (Security policy)")
            files_list.append(f"{CHARS['check']} ARCHITECTURE.md (System design docs)")
            files_list.append(f"{CHARS['check']} CODE_OF_CONDUCT.md (Community guidelines)")
        else:
            # Handle custom core templates
            core_templates = config.get('core_templates', {})
            if core_templates.get('TESTING'):
                files_list.append(f"{CHARS['check']} TESTING.md (TDD workflow)")
            elif preset == 'custom':
                files_list.append(f"[dim]{CHARS['cross']} TESTING.md (not selected)[/dim]")

            if config.get('with_branching'):
                files_list.append(f"{CHARS['check']} BRANCHING.md (Git workflow conventions)")
            else:
                files_list.append(f"[dim]{CHARS['cross']} BRANCHING.md (not selected)[/dim]")

            # Show other templates if selected in custom path
            if core_templates.get('CONTRIBUTING'):
                files_list.append(f"{CHARS['check']} CONTRIBUTING.md (Contribution guidelines)")
            elif preset == 'custom':
                files_list.append(f"[dim]{CHARS['cross']} CONTRIBUTING.md (not selected)[/dim]")

            if core_templates.get('SECURITY'):
                files_list.append(f"{CHARS['check']} SECURITY.md (Security policy)")
            elif preset == 'custom':
                files_list.append(f"[dim]{CHARS['cross']} SECURITY.md (not selected)[/dim]")

            if core_templates.get('ARCHITECTURE'):
                files_list.append(f"{CHARS['check']} ARCHITECTURE.md (System design docs)")
            elif preset == 'custom':
                files_list.append(f"[dim]{CHARS['cross']} ARCHITECTURE.md (not selected)[/dim]")

            if core_templates.get('CODE_OF_CONDUCT'):
                files_list.append(f"{CHARS['check']} CODE_OF_CONDUCT.md (Community guidelines)")
            elif preset == 'custom':
                files_list.append(f"[dim]{CHARS['cross']} CODE_OF_CONDUCT.md (not selected)[/dim]")

        # Handle granular capabilities
        capabilities_config = config.get('capabilities_config', {})

        if config.get('with_capabilities'):
            if capabilities_config and capabilities_config.get('enabled'):
                # Granular selection (custom path)
                cap_parts = []
                if capabilities_config.get('skills'):
                    cap_parts.append("Skills")
                if capabilities_config.get('workflows'):
                    cap_parts.append("Workflows")
                if capabilities_config.get('commands'):
                    cap_parts.append("Commands")

                if cap_parts:
                    cap_desc = ", ".join(cap_parts)
                    files_list.append(f"{CHARS['check']} .proto-gear/ ({cap_desc})")
                else:
                    files_list.append(f"[dim]{CHARS['cross']} .proto-gear/ (no categories selected)[/dim]")
            else:
                # Preset path (all capabilities) or empty config
                files_list.append(f"{CHARS['check']} .proto-gear/ (Universal Capabilities System)")
        else:
            files_list.append(f"[dim]{CHARS['cross']} .proto-gear/ (not selected)[/dim]")

        files_text = "\n".join(files_list)

        # Print table first
        if self.console:
            self.console.print(f"\n{CHARS['memo']} [bold cyan]Configuration Summary[/bold cyan]")
            self.console.print(table)
            self.console.print()  # Empty line

        # Then print files panel
        files_panel_content = f"[bold]Files to create:[/bold]\n\n{files_text}"
        self.print_panel(
            files_panel_content,
            title=f"{CHARS['memo']} Files",
            border_style="cyan"
        )

        if not QUESTIONARY_AVAILABLE:
            # Fallback if questionary unavailable
            while True:
                response = input("\nProceed with setup? (y/n): ").lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                print("Please enter 'y' or 'n'")

        answer = questionary.confirm(
            "Proceed with setup?",
            default=True,
            style=PROTO_GEAR_STYLE
        ).ask()

        return answer if answer is not None else False


def run_enhanced_wizard(project_info: Dict, git_config: Dict, current_dir: Path) -> Optional[Dict]:
    """
    Run the enhanced interactive wizard with rich UI (v0.4.1 with presets)
    Returns configuration dict or None if cancelled
    """
    wizard = RichWizard()

    # Clear screen for single-page app experience
    wizard.clear_screen()

    # Print header
    if wizard.console:
        wizard.console.print("\n[bold cyan]ProtoGear Interactive Setup Wizard[/bold cyan]")
        wizard.console.print("[dim]" + "=" * 60 + "[/dim]\n")
        wizard.console.print("[dim]Let's configure AI-powered development workflow for your project[/dim]\n")
    else:
        print("\nProtoGear Interactive Setup Wizard")
        print("=" * 60)
        print("Let's configure AI-powered development workflow for your project\n")

    # Show project detection
    project_panel = wizard.create_project_info_panel(project_info, git_config, current_dir)
    wizard.print_panel(project_panel, title=f"{CHARS['chart']} Project Detection", border_style="cyan")

    git_detected = git_config.get('is_git_repo', False)

    # NEW: Ask for preset selection
    while True:
        try:
            preset_key = wizard.ask_preset_selection(git_detected)
        except KeyboardInterrupt:
            return None

        # If custom, skip preview and go to detailed wizard
        if preset_key == 'custom':
            break

        # Show preset preview and get confirmation
        try:
            continue_with_preset = wizard.show_preset_preview(preset_key, git_detected)
            if continue_with_preset:
                # User confirmed preset, apply configuration
                preset_config = PRESETS[preset_key]['config']
                config = _apply_preset_config(preset_config, git_detected, current_dir)
                config['preset'] = preset_key
                config['confirmed'] = True
                return config
            else:
                # User wants to go back, loop to preset selection again
                continue
        except KeyboardInterrupt:
            return None

    # CUSTOM PATH: Granular selection wizard
    config = {'preset': 'custom'}

    # Stage 1: Core Templates Selection
    wizard.clear_screen()
    wizard.show_step_header(1, 3, "Core Templates", project_info, current_dir)
    try:
        core_templates = wizard.ask_core_templates_selection()
        config['core_templates'] = core_templates
    except KeyboardInterrupt:
        return None

    # Stage 2: Git Workflow Configuration
    wizard.clear_screen()
    wizard.show_step_header(2, 3, "Git Workflow", project_info, current_dir)
    try:
        git_options = wizard.ask_git_workflow_options(git_config, current_dir)
        config.update(git_options)
    except KeyboardInterrupt:
        return None

    # Stage 3: Capabilities Selection (granular)
    wizard.clear_screen()
    wizard.show_step_header(3, 3, "Capabilities", project_info, current_dir)
    try:
        capabilities_config = wizard.ask_capabilities_selection()
        config['capabilities_config'] = capabilities_config
        config['with_capabilities'] = capabilities_config.get('enabled', False)
    except KeyboardInterrupt:
        return None

    # Show configuration summary and get confirmation
    wizard.clear_screen()
    try:
        confirmed = wizard.show_configuration_summary(config, project_info, current_dir)
        config['confirmed'] = confirmed
    except KeyboardInterrupt:
        return None

    return config


def _apply_preset_config(preset_config: Dict, git_detected: bool, current_dir: Path) -> Dict:
    """
    Convert preset configuration to actual config dict
    """
    config = {}

    # Handle branching
    if preset_config['branching'] == 'auto':
        config['with_branching'] = git_detected
    else:
        config['with_branching'] = preset_config['branching']

    # Set ticket prefix if branching enabled
    if config['with_branching']:
        suggested_prefix = current_dir.name.upper().replace('-', '').replace('_', '')[:6]
        if not suggested_prefix or len(suggested_prefix) < 2:
            suggested_prefix = 'PROJ'
        config['ticket_prefix'] = suggested_prefix
    else:
        config['ticket_prefix'] = None

    # Capabilities
    config['with_capabilities'] = preset_config['capabilities']

    # All templates flag (v0.5.2+)
    config['with_all'] = preset_config.get('with_all', False)

    # Core templates (for custom path compatibility)
    config['core_templates'] = preset_config.get('core', {})

    return config
