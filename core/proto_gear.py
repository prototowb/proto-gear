#!/usr/bin/env python3
"""
Proto Gear - AI Agent Framework for Project Development
Main entry point for integrating AI-powered development workflows
"""

import sys
import os
import time
import random
from pathlib import Path
from typing import Optional
import argparse

# ASCII Art for Proto Gear
LOGO_V1 = """
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
    ║                        🤖 AI Agent Framework v0.3 🤖       ║
    ║                                                             ║
    ╚═════════════════════════════════════════════════════════════╝
"""

PROTO_GEAR_LOGOS = [LOGO_V1]

# Colorful ANSI escape codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    GRAY = '\033[90m'
    YELLOW = '\033[93m'
    MAGENTA = '\033[95m'


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

    # Choose a random logo
    logo = random.choice(PROTO_GEAR_LOGOS)

    # Animated logo appearance (with encoding safety)
    print(Colors.CYAN + Colors.BOLD)
    try:
        for line in logo.split('\n'):
            print(line)
            time.sleep(0.05)
    except UnicodeEncodeError:
        # Fallback for terminals that don't support Unicode
        print("=" * 60)
        print(" PROTO GEAR - AI Agent Framework v0.3")
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
            "Proto Gear is an AI-powered development workflow framework that integrates",
            "intelligent agents into your existing projects. It provides sprint management,",
            "ticket generation, Git workflow integration, and adaptive agent orchestration."
        ]),
        ("Core Components", [
            "- Adaptive Hybrid Agent System: 4 core + 2 flexible sprint-based agents",
            "- Project State Management: Single source of truth via PROJECT_STATUS.md",
            "- Workflow Orchestrator: Automated sprint planning and task distribution",
            "- Git Integration: Automatic branch management for tickets and features",
            "- Documentation Engine: Ensures consistency across AGENTS.md files"
        ]),
        ("Key Features", [
            "+ Auto-detection of existing tech stack and frameworks",
            "+ Sprint-based agent configuration (Feature, Bug Fix, Performance, etc.)",
            "+ Intelligent ticket generation and tracking",
            "+ Git workflow automation with branch management",
            "+ Documentation consistency checking",
            "+ Supports any programming language or framework"
        ]),
        ("Getting Started", [
            "1. Navigate to your project directory",
            "2. Run 'pg init' to initialize the agent framework",
            "3. Review the generated AGENTS.md and PROJECT_STATUS.md",
            "4. Run 'pg workflow' to activate the orchestrator",
            "5. Let AI agents manage your development workflow"
        ]),
        ("Commands", [
            "pg init           - Initialize AI agents in current project",
            "pg init --dry-run - Preview what will be created",
            "pg workflow       - Run the agent workflow orchestrator",
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
    input(f"{Colors.GREEN}Press Enter to continue...{Colors.ENDC}")


def print_farewell():
    """Print farewell message"""
    print(f"\n{Colors.CYAN}👋 Thank you for using Proto Gear!{Colors.ENDC}")
    print(f"{Colors.GRAY}Happy coding! May your builds be swift and your bugs be few.{Colors.ENDC}\n")


def detect_project_structure(project_path):
    """Detect existing project structure and technologies"""
    import json

    info = {
        'detected': False,
        'type': None,
        'framework': None,
        'directories': [],
        'structure_summary': ''
    }

    try:
        # Check for package.json (Node.js project)
        package_json = project_path / 'package.json'
        if package_json.exists():
            info['detected'] = True
            info['type'] = 'Node.js Project'

            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}

                    if 'next' in deps:
                        info['framework'] = 'Next.js'
                    elif 'react' in deps:
                        info['framework'] = 'React'
                    elif 'vue' in deps:
                        info['framework'] = 'Vue.js'
                    elif 'express' in deps:
                        info['framework'] = 'Express.js'
            except:
                pass

        # Check for Python files
        elif any(project_path.glob('*.py')) or (project_path / 'requirements.txt').exists():
            info['detected'] = True
            info['type'] = 'Python Project'

            if (project_path / 'manage.py').exists():
                info['framework'] = 'Django'
            elif any('fastapi' in f.name.lower() for f in project_path.glob('*.py')):
                info['framework'] = 'FastAPI'

        # Scan directories
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                info['directories'].append(item.name)

        # Create structure summary
        if info['directories']:
            info['structure_summary'] = f"Project contains: {', '.join(info['directories'])}"
        else:
            info['structure_summary'] = "Basic project structure"

    except Exception:
        pass

    return info


def setup_agent_framework_only(dry_run=False):
    """Set up ProtoGear agent framework in existing project"""
    from datetime import datetime

    print(f"\n{Colors.CYAN}Agent Framework Setup{Colors.ENDC}")
    print("-" * 30)

    current_dir = Path(".")
    print(f"Current directory: {current_dir.absolute()}")

    # Detect project structure
    project_info = detect_project_structure(current_dir)

    if project_info['detected']:
        print(f"Detected: {project_info['type']} project")
        if project_info.get('framework'):
            print(f"Framework: {project_info['framework']}")

    if not dry_run:
        try:
            files_created = []

            # Create AGENTS.md
            agents_file = current_dir / 'AGENTS.md'
            agents_content = f"""# AGENTS.md - {current_dir.name}

> **ProtoGear Agent Framework Integration**
> **Project Type**: {project_info.get('type', 'Unknown')}
> **Framework**: {project_info.get('framework', 'Unknown')}

## Framework Activation

This project is now integrated with ProtoGear's AI agent workflow system.

When this file is read by an AI agent, it should:

1. Analyze the current project structure
2. Understand the technology stack in use
3. Provide context-aware development assistance
4. Follow the project's established patterns

## Project Structure

{project_info.get('structure_summary', 'Basic project structure detected')}

## Agent Configuration

Proto Gear uses an adaptive hybrid system with 4 permanent core agents and 2 flexible
sprint-specific slots that adapt based on current development needs.

### Core Agents (Always Active)
- **Backend Agent**: Server-side logic, APIs, database integration
- **Frontend Agent**: UI/UX, component development, styling
- **Testing Agent**: Test creation, coverage analysis, quality assurance
- **DevOps Agent**: CI/CD, deployment, infrastructure management

### Flex Agents (Sprint-Based)
Automatically configured based on sprint type:
- Documentation Agent
- Performance Agent
- Security Agent
- Refactoring Agent

## Workflow Commands

```bash
# Initialize agent framework (already done)
pg init

# Run agent workflow orchestrator
pg workflow

# Show help and documentation
pg help
```

## Next Steps

1. Review this file to understand agent capabilities
2. Check PROJECT_STATUS.md for current project state
3. Run 'pg workflow' to activate the orchestrator
4. Start development with AI-powered assistance

---
*Powered by ProtoGear Agent Framework v0.3 (Alpha)*
"""
            agents_file.write_text(agents_content)
            files_created.append('AGENTS.md')

            # Create PROJECT_STATUS.md
            status_file = current_dir / 'PROJECT_STATUS.md'
            status_content = f"""# PROJECT STATUS - {current_dir.name}

> **Single Source of Truth** for project state

## Current State

```yaml
project_phase: "Initialized"
protogear_enabled: true
framework: "{project_info.get('framework', 'Unknown')}"
project_type: "{project_info.get('type', 'Unknown')}"
initialization_date: "{datetime.now().strftime('%Y-%m-%d')}"
current_sprint: null
```

## 🎫 Active Tickets
*No active tickets yet - ProtoGear will track development progress here*

## ✅ Completed Tickets
- INIT-001: ProtoGear Agent Framework integrated

## Project Analysis

| Component | Status | Notes |
|-----------|--------|-------|
| ProtoGear Integration | Complete | Agent framework active |
| Project Structure | Analyzed | {len(project_info.get('directories', []))} directories detected |

## Recent Updates
- {datetime.now().strftime('%Y-%m-%d')}: ProtoGear Agent Framework integrated

---
*Maintained by ProtoGear Agent Framework*
"""
            status_file.write_text(status_content)
            files_created.append('PROJECT_STATUS.md')

            return {
                'status': 'success',
                'files_created': files_created,
                'mode': 'agent-framework-only'
            }

        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    else:
        print(f"\n{Colors.YELLOW}Dry run - files that would be created:{Colors.ENDC}")
        print("  - AGENTS.md (AI agent integration guide)")
        print("  - PROJECT_STATUS.md (project state tracker)")

        return {'status': 'success', 'dry_run': True}


def run_simple_protogear_init(dry_run=False):
    """Initialize ProtoGear AI Agent Framework in current project"""
    from datetime import datetime

    print(f"\n{Colors.BOLD}ProtoGear AI Agent Framework Initialization{Colors.ENDC}")
    print("=" * 60)
    print(f"{Colors.GRAY}Adding AI-powered development workflow to your project{Colors.ENDC}")
    print("=" * 60)

    # Directly run agent framework setup (no menu)
    try:
        result = setup_agent_framework_only(dry_run=dry_run)
    except KeyboardInterrupt:
        return {'status': 'cancelled'}

    # Show results
    if result['status'] == 'success':
        if result.get('dry_run'):
            print(f"\n{Colors.GREEN}SUCCESS: Dry run completed successfully!{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}SUCCESS: ProtoGear AI Agent Framework integrated!{Colors.ENDC}")

            if result.get('files_created'):
                print(f"\n{Colors.CYAN}Files created:{Colors.ENDC}")
                for file in result['files_created']:
                    print(f"  + {file}")

            print(f"\n{Colors.YELLOW}Next steps:{Colors.ENDC}")
            print("  1. Review AGENTS.md to understand AI agent capabilities")
            print("  2. Check PROJECT_STATUS.md for project state tracking")
            print("  3. Start development with AI-powered assistance")
            print("  4. Run 'pg workflow' to activate the agent workflow orchestrator")

    return result


def main():
    """Main entry point for Proto Gear AI Agent Framework"""
    # Add argument parsing
    parser = argparse.ArgumentParser(
        description="Proto Gear - AI Agent Framework for Development Workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pg init              Initialize AI agents in current project
  pg init --dry-run    Preview what will be created
  pg workflow          Run agent workflow orchestrator
  pg help              Show detailed help information

For more information, visit: https://github.com/proto-gear/proto-gear
        """
    )

    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Main 'init' command
    init_parser = subparsers.add_parser(
        'init',
        help='Initialize AI Agent Framework in current project'
    )
    init_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate without creating files'
    )

    # 'workflow' command to run the orchestrator
    workflow_parser = subparsers.add_parser(
        'workflow',
        help='Run AI Agent workflow orchestrator'
    )

    # 'help' command for detailed documentation
    help_parser = subparsers.add_parser(
        'help',
        help='Show detailed help and documentation'
    )

    args = parser.parse_args()

    try:
        # Handle 'init' command
        if args.command == 'init':
            show_splash_screen()
            result = run_simple_protogear_init(dry_run=args.dry_run)

            if result['status'] == 'success':
                print(f"\n{Colors.GREEN}ProtoGear AI Agent Framework initialized!{Colors.ENDC}")
            elif result['status'] == 'cancelled':
                print(f"\n{Colors.YELLOW}Initialization cancelled by user.{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}Initialization failed: {result.get('error', 'Unknown error')}{Colors.ENDC}")
                sys.exit(1)

            sys.exit(0)

        # Handle 'workflow' command
        elif args.command == 'workflow':
            from agent_framework import WorkflowOrchestrator
            print(f"{Colors.CYAN}🤖 Starting AI Agent Workflow Orchestrator...{Colors.ENDC}\n")
            orchestrator = WorkflowOrchestrator()
            result = orchestrator.execute_workflow()
            sys.exit(0)

        # Handle 'help' command
        elif args.command == 'help':
            show_help()
            sys.exit(0)

        # No command provided - show help
        else:
            show_splash_screen()
            print(f"{Colors.GREEN}Welcome to Proto Gear AI Agent Framework!{Colors.ENDC}")
            print(f"{Colors.GRAY}Intelligent development workflows powered by adaptive AI agents{Colors.ENDC}\n")
            print(f"{Colors.CYAN}Available Commands:{Colors.ENDC}")
            print(f"  {Colors.BOLD}pg init{Colors.ENDC}         - Initialize AI agents in your project")
            print(f"  {Colors.BOLD}pg workflow{Colors.ENDC}    - Run agent workflow orchestrator")
            print(f"  {Colors.BOLD}pg help{Colors.ENDC}        - Show detailed documentation")
            print(f"\n{Colors.GRAY}Run 'pg --help' for more options{Colors.ENDC}\n")
            print_farewell()

    except KeyboardInterrupt:
        print_farewell()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please report this issue on GitHub.{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
