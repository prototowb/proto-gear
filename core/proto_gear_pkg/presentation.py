"""Terminal presentation helpers for Proto Gear.

Logo/splash/help rendering and low-level console input. Pure presentation —
no project detection, template, or init logic. Extracted from the
``proto_gear.py`` monolith (PROTO-042, ADR-001 Phase A) and re-exported there
for backwards compatibility.
"""

import os
import sys
import time
import random

from . import __version__
from .ui_helper import UIHelper, Colors

ui = UIHelper()


# ASCII Art for Proto Gear
def get_logo_v1():
    """Generate logo with dynamic version from __version__"""
    version_text = f"🤖 AI Agent Framework v{__version__} 🤖"
    # Center the version text within the 61-character width (║...║)
    # 61 total - 2 for borders = 59 usable, center the text
    padding = (59 - len(version_text)) // 2
    version_line = f"    ║{' ' * padding}{version_text}{' ' * (59 - padding - len(version_text))}║"

    return f"""
    ╔═════════════════════════════════════════════════════════════╗
    ║                                                             ║
    ║   ██████╗ ██████╗  ██████╗ ████████╗ ██████╗                ║
    ║   ██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗               ║
    ║   ██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║               ║
    ║   ██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║               ║
    ║   ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝               ║
    ║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝                ║
    ║                                                             ║
    ║    ██████╗ ███████╗ █████╗ ██████╗                          ║
    ║   ██╔════╝ ██╔════╝██╔══██╗██╔══██╗                         ║
    ║   ██║  ███╗█████╗  ███████║██████╔╝                         ║
    ║   ██║   ██║██╔══╝  ██╔══██║██╔══██╗                         ║
    ║   ╚██████╔╝███████╗██║  ██║██║  ██║                         ║
    ║    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝                         ║
{version_line}
    ║                                                             ║
    ╚═════════════════════════════════════════════════════════════╝
"""

PROTO_GEAR_LOGOS = [get_logo_v1]


def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')


def safe_input(prompt: str, default: str = "", handle_eof: bool = True) -> str:
    """Safely handle input with EOF and KeyboardInterrupt protection"""
    try:
        return input(prompt).strip()
    except EOFError:
        if handle_eof:
            print(default)
            return default
        else:
            raise
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
        raise


def print_centered(text: str, width: int = 80):
    """Print text centered within given width"""
    print(text.center(width))


def show_splash_screen():
    """Display the Proto Gear splash screen"""
    clear_screen()

    # Choose a random logo function and call it to get the logo string
    logo_func = random.choice(PROTO_GEAR_LOGOS)
    logo = logo_func()

    # Animated logo appearance (with encoding safety)
    print(Colors.CYAN + Colors.BOLD)
    try:
        for line in logo.split('\n'):
            print(line)
            time.sleep(0.05)
    except UnicodeEncodeError:
        # Fallback for terminals that don't support Unicode
        print("=" * 60)
        print(f" PROTO GEAR - AI Agent Framework v{__version__}")
        print("=" * 60)
    print(Colors.ENDC)

    # Tagline with typewriter effect
    print()
    try:
        tagline = "⚡ AI-Powered Development Workflow Framework ⚡"
        print_centered(Colors.YELLOW + tagline + Colors.ENDC)
    except UnicodeEncodeError:
        tagline = "AI-Powered Development Workflow Framework"
        print_centered(Colors.YELLOW + tagline + Colors.ENDC)

    time.sleep(0.5)
    print()
    print_centered(Colors.GRAY + "Powered by Adaptive AI Agent System" + Colors.ENDC)
    try:
        print_centered(Colors.GRAY + "Sprint Management • Ticket Generation • Git Workflow Integration" + Colors.ENDC)
    except UnicodeEncodeError:
        print_centered(Colors.GRAY + "Sprint Management | Ticket Generation | Git Workflow Integration" + Colors.ENDC)

    try:
        print("\n" + "─" * 80 + "\n")
    except UnicodeEncodeError:
        print("\n" + "-" * 80 + "\n")
    time.sleep(0.5)


def show_help():
    """Show help and documentation"""
    clear_screen()
    try:
        print(Colors.BOLD + Colors.CYAN + "📖 Proto Gear AI Agent Framework Documentation" + Colors.ENDC)
    except UnicodeEncodeError:
        print(Colors.BOLD + Colors.CYAN + "Proto Gear AI Agent Framework Documentation" + Colors.ENDC)

    try:
        print("\n" + "─" * 80 + "\n")
    except UnicodeEncodeError:
        print("\n" + "-" * 80 + "\n")

    sections = [
        ("What is Proto Gear?", [
            "Proto Gear is a template generator that creates collaboration environments",
            "for human and AI agents. It generates markdown templates that define patterns",
            "for workflows, testing (TDD), branching strategies, and agent coordination."
        ]),
        ("Core Templates Generated", [
            "- AGENTS.md: Agent patterns, roles, and collaboration workflows",
            "- PROJECT_STATUS.md: Single source of truth for project state",
            "- TESTING.md: TDD methodology and testing patterns (recommended)",
            "- BRANCHING.md: Git workflow and commit conventions (optional)",
            "- CONTRIBUTING.md: Contribution guidelines (optional)",
            "- SECURITY.md: Security policy and vulnerability reporting (optional)",
            "- ARCHITECTURE.md: System design documentation (optional)",
            "- CODE_OF_CONDUCT.md: Community guidelines (optional)",
            "- .proto-gear/: Universal capabilities system with modular patterns"
        ]),
        ("Key Features", [
            "+ Auto-detection of existing tech stack and frameworks",
            "+ Tech stack agnostic - works with any language or framework",
            "+ Natural language collaboration patterns for AI agents",
            "+ Beautiful interactive CLI wizard with arrow key navigation",
            "+ Comprehensive TDD workflow documentation",
            "+ Git branching strategy templates"
        ]),
        ("Getting Started", [
            "1. Navigate to your project directory",
            "2. Run 'pg init' to initialize agent templates (interactive wizard)",
            "3. Review generated files (AGENTS.md, PROJECT_STATUS.md, TESTING.md, etc.)",
            "4. Customize templates to match your project's workflow",
            "5. AI agents read templates and collaborate via natural language",
            "6. Update PROJECT_STATUS.md as work progresses"
        ]),
        ("Commands", [
            "pg init           - Initialize AI agent templates in current project",
            "pg init --dry-run - Preview what will be created",
            "pg help           - Show this help documentation"
        ])
    ]

    for title, content in sections:
        print(f"{Colors.YELLOW}{Colors.BOLD}{title}{Colors.ENDC}")
        for line in content:
            print(f"  {line}")
        print()

    print(f"{Colors.CYAN}Links:{Colors.ENDC}")
    print(f"  GitHub: {Colors.BLUE}github.com/proto-gear/proto-gear{Colors.ENDC}")
    print(f"  Docs:   {Colors.BLUE}protogear.dev/docs{Colors.ENDC}")
    print(f"  Discord: {Colors.BLUE}discord.gg/protogear{Colors.ENDC}")

    try:
        print("\n" + "─" * 80 + "\n")
    except UnicodeEncodeError:
        print("\n" + "-" * 80 + "\n")
    # Only pause for the user when stdin is a TTY. Under subprocess / CI,
    # stdin is closed and input() raises EOFError — `pg help | cat` should
    # exit cleanly, not crash.
    if sys.stdin.isatty():
        try:
            input(f"{Colors.GREEN}Press Enter to continue...{Colors.ENDC}")
        except EOFError:
            pass


def print_farewell():
    """Print farewell message"""
    print(f"\n{Colors.CYAN}👋 Thank you for using Proto Gear!{Colors.ENDC}")
    ui.farewell()
