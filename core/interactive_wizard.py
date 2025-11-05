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
        }
    except (UnicodeEncodeError, AttributeError):
        # Fallback to ASCII
        return {
            'check': '[Y]',
            'cross': '[N]',
            'bullet': '*',
            'line': '-',
        }


# Get encoding-safe characters once at module load
CHARS = get_safe_chars()


# Custom style for questionary prompts
PROTO_GEAR_STYLE = Style([
    ('qmark', 'fg:#5f87d7 bold'),           # Question mark color
    ('question', 'bold'),                    # Question text
    ('answer', 'fg:#00d787 bold'),          # User's answer
    ('pointer', 'fg:#00d787 bold'),         # Selection pointer
    ('highlighted', 'fg:#00d787 bold'),     # Highlighted choice
    ('selected', 'fg:#5f87d7'),             # Selected items
    ('separator', 'fg:#6c6c6c'),            # Separator lines
    ('instruction', 'fg:#6c6c6c'),          # Instructions
    ('text', ''),                            # Plain text
    ('disabled', 'fg:#858585 italic')       # Disabled choices
])


class RichWizard:
    """Enhanced interactive wizard using Rich and Questionary"""

    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.config = {}

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

    def ask_branching_strategy(self, git_config: Dict) -> bool:
        """Ask user if they want branching strategy with arrow key selection"""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple y/n prompt
            print("\n📋 Branching & Git Workflow")
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
                title="📋 Branching & Git Workflow",
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
            print(f"\n🎫 Ticket Prefix Configuration")
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
                title="🎫 Ticket Prefix Configuration",
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
        if not RICH_AVAILABLE:
            # Fallback
            print("\n📝 Configuration Summary")
            print("=" * 60)
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

        table.add_row("Project", current_dir.name)
        table.add_row("Type", project_info.get('type', 'Generic'))
        if project_info.get('framework'):
            table.add_row("Framework", project_info['framework'])
        table.add_row("Branching", f"{CHARS['check']} Enabled" if config.get('with_branching') else f"{CHARS['cross']} Disabled")
        if config.get('with_branching'):
            table.add_row("Ticket Prefix", config.get('ticket_prefix', 'N/A'))

        files_list = [
            f"{CHARS['check']} AGENTS.md (AI agent integration guide)",
            f"{CHARS['check']} PROJECT_STATUS.md (Project state tracking)"
        ]

        if config.get('with_branching'):
            files_list.append(f"{CHARS['check']} BRANCHING.md (Git workflow conventions)")
        else:
            files_list.append(f"[dim]{CHARS['cross']} BRANCHING.md (not selected)[/dim]")

        files_text = "\n".join(files_list)

        panel_content = f"{table}\n\n[bold]Files to create:[/bold]\n{files_text}"

        self.print_panel(
            panel_content,
            title="📝 Configuration Summary",
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
    Run the enhanced interactive wizard with rich UI
    Returns configuration dict or None if cancelled
    """
    wizard = RichWizard()

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
    wizard.print_panel(project_panel, title="📊 Project Detection", border_style="cyan")

    # Ask about branching strategy
    try:
        with_branching = wizard.ask_branching_strategy(git_config)
    except KeyboardInterrupt:
        return None

    config = {'with_branching': with_branching}

    # Ask for ticket prefix if branching enabled
    if with_branching:
        try:
            suggested_prefix = current_dir.name.upper().replace('-', '').replace('_', '')[:6]
            if not suggested_prefix or len(suggested_prefix) < 2:
                suggested_prefix = 'PROJ'

            ticket_prefix = wizard.ask_ticket_prefix(suggested_prefix)
            config['ticket_prefix'] = ticket_prefix
        except KeyboardInterrupt:
            return None
    else:
        config['ticket_prefix'] = None

    # Show configuration summary and get confirmation
    try:
        confirmed = wizard.show_configuration_summary(config, project_info, current_dir)
        config['confirmed'] = confirmed
    except KeyboardInterrupt:
        return None

    return config
