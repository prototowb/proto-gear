#!/usr/bin/env python3
"""
Interactive Wizard Module for Proto Gear
Provides rich, beautiful CLI interactions with arrow key navigation
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Import template discovery from proto_gear module
try:
    from .templates import (
        discover_available_templates,
        CORE_ALWAYS_FILES,
        SYNC_GENERATED_FILES,
        OPTIONAL_TEMPLATE_FILES,
        NON_SELECTABLE_TEMPLATES,
    )
except ImportError:
    # Fallback if running standalone
    discover_available_templates = None
    CORE_ALWAYS_FILES = ["AGENTS.md", "SESSION_HANDOFF.md", "PROJECT_STATUS.md"]
    SYNC_GENERATED_FILES = [
        "AGENT_CONTEXT.md",
        "CLAUDE.md",
        ".cursorrules",
        ".windsurfrules",
        ".github/copilot-instructions.md",
    ]
    OPTIONAL_TEMPLATE_FILES = [
        "TESTING.md",
        "BRANCHING.md",
        "CONTRIBUTING.md",
        "SECURITY.md",
        "ARCHITECTURE.md",
        "CODE_OF_CONDUCT.md",
    ]
    NON_SELECTABLE_TEMPLATES = frozenset(
        {"AGENTS", "PROJECT_STATUS", "SESSION_HANDOFF", "AGENT_CONTEXT"}
    )

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


# Capability metadata - what's actually available
CAPABILITIES_METADATA = {
    "skills": {
        "testing": {
            "name": "Testing (TDD)",
            "description": "Test-Driven Development methodology",
            "details": "Red-Green-Refactor cycle, test pyramid, coverage targets",
        },
        "debugging": {
            "name": "Debugging & Troubleshooting",
            "description": "Systematic debugging approach",
            "details": "8-step scientific method, rubber duck debugging, binary search",
        },
        "code-review": {
            "name": "Code Review",
            "description": "Structured code review process",
            "details": "Review checklist, feedback patterns, security checks",
        },
        "refactoring": {
            "name": "Refactoring",
            "description": "Safe code refactoring techniques",
            "details": "Extract method, rename, simplify conditionals, remove duplication",
        },
    },
    "workflows": {
        "feature-development": {
            "name": "Feature Development",
            "description": "7-step feature development process",
            "details": "Plan → Design → Implement → Test → Review → Document → Deploy",
        },
        "bug-fix": {
            "name": "Bug Fix",
            "description": "Systematic bug resolution workflow",
            "details": "Reproduce → Diagnose → Fix → Test → Verify → Document",
        },
        "hotfix": {
            "name": "Hotfix",
            "description": "Emergency production fix workflow",
            "details": "Fast-track critical fixes with minimal risk",
        },
        "release": {
            "name": "Release",
            "description": "Version release workflow",
            "details": "Version bump → Changelog → Tag → Build → Publish",
        },
        "finalize-release": {
            "name": "Finalize Release",
            "description": "Post-release verification workflow",
            "details": "Verify deployment, update docs, notify stakeholders",
        },
    },
    "commands": {
        "create-ticket": {
            "name": "Create Ticket",
            "description": "Generate project tickets",
            "details": "Structured ticket creation with templates",
        }
    },
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
            "check": "✓",
            "cross": "✗",
            "bullet": "•",
            "line": "─",
            "wrench": "🔧",
            "clipboard": "📋",
            "ticket": "🎫",
            "memo": "📝",
            "chart": "📊",
            "plus": "➕",
            "gear": "⚙️",
            "refresh": "🔄",
        }
    except (UnicodeEncodeError, AttributeError):
        # Fallback to ASCII
        return {
            "check": "[Y]",
            "cross": "[N]",
            "bullet": "*",
            "line": "-",
            "wrench": "[SETUP]",
            "clipboard": "[GIT]",
            "ticket": "[TICKET]",
            "memo": "[CONFIG]",
            "chart": "[PROJECT]",
            "plus": "[+]",
            "gear": "[GEAR]",
            "refresh": "[UPDATE]",
        }


# Get encoding-safe characters once at module load
CHARS = get_safe_chars()


# Custom style for questionary prompts - Clean UX without background colors
# Guarded: without questionary installed, `Style` doesn't exist and an
# unconditional module-level call crashes the entire package import
# (PROTO-041). Fallback paths only need the flag, never the style object.
PROTO_GEAR_STYLE = (
    None
    if not QUESTIONARY_AVAILABLE
    else Style(
        [
            ("qmark", "fg:#5f87d7 bold"),  # Question mark color
            ("question", "bold"),  # Question text
            ("answer", "fg:#00d787 bold"),  # User's answer
            ("pointer", "fg:#00d787 bold"),  # Selection pointer (arrow)
            (
                "highlighted",
                "fg:#00d787 bold noreverse",
            ),  # Highlighted choice - NO background/reverse
            (
                "selected",
                "fg:#00d787 noreverse",
            ),  # Selected checkbox items - NO background/reverse
            ("separator", "fg:#6c6c6c"),  # Separator lines
            ("instruction", "fg:#6c6c6c"),  # Instructions
            ("text", ""),  # Plain text (default terminal color)
            ("disabled", "fg:#858585 italic"),  # Disabled choices
            ("checkbox", "fg:#00d787"),  # Checkbox icon
            ("checkbox-selected", "fg:#00d787 bold"),  # Selected checkbox icon
            # Additional prompt_toolkit classes to prevent backgrounds
            ("", "noreverse"),  # Global: no reverse video
        ]
    )
)


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

            os.system("cls" if os.name == "nt" else "clear")

    def show_step_header(
        self,
        step: int,
        total_steps: int,
        step_name: str,
        project_info: Dict,
        current_dir: Path,
    ):
        """Show consistent step header with progress and project context"""
        if self.console:
            # Progress indicator
            self.console.print(
                f"\n[bold cyan]ProtoGear Setup[/bold cyan] [dim]│[/dim] Step {step} of {total_steps}: [bold]{step_name}[/bold]"
            )
            self.console.print("[dim]" + "─" * 60 + "[/dim]")

            # Project context (compact)
            project_type = project_info.get("type", "Generic")
            framework = project_info.get("framework", "")
            context = f"[dim]Project:[/dim] {current_dir.name} [dim]│[/dim] [dim]Type:[/dim] {project_type}"
            if framework:
                context += f" [dim]({framework})[/dim]"
            self.console.print(context)
            self.console.print()
        else:
            print(f"\n=== ProtoGear Setup - Step {step}/{total_steps}: {step_name} ===")
            print(
                f"Project: {current_dir.name} | Type: {project_info.get('type', 'Generic')}"
            )
            if project_info.get("framework"):
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
                padding=(1, 2),
            )
            self.console.print(panel)
        else:
            # Fallback to simple print
            if title:
                print(f"\n{title}")
                print("=" * 60)
            print(content)
            print()

    def create_project_info_panel(
        self, project_info: Dict, git_config: Dict, current_dir: Path
    ) -> str:
        """Create formatted project information display"""
        if not RICH_AVAILABLE:
            # Fallback to simple formatting
            lines = []
            lines.append(f"Directory: {current_dir.absolute()}")
            if project_info.get("detected"):
                lines.append(f"Type: {project_info['type']}")
                if project_info.get("framework"):
                    lines.append(f"Framework: {project_info['framework']}")
            else:
                lines.append("Type: Generic Project")

            if git_config["is_git_repo"]:
                lines.append(f"Git: {CHARS['check']} Initialized")
                if git_config["has_remote"]:
                    lines.append(
                        f"Remote: {CHARS['check']} {git_config['remote_name']}"
                    )
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

        if project_info.get("detected"):
            table.add_row("Type", project_info["type"])
            if project_info.get("framework"):
                table.add_row("Framework", project_info["framework"])
        else:
            table.add_row("Type", "[yellow]Generic Project[/yellow]")

        if git_config["is_git_repo"]:
            table.add_row("Git", f"{CHARS['check']} Initialized")
            if git_config["has_remote"]:
                table.add_row("Remote", f"{CHARS['check']} {git_config['remote_name']}")
            else:
                table.add_row(
                    "Remote", f"[yellow]{CHARS['cross']} None (local-only)[/yellow]"
                )
        else:
            table.add_row("Git", f"[yellow]{CHARS['cross']} Not initialized[/yellow]")

        return table

    def show_detected_plan(self, plan: Dict) -> None:
        """Show the detection-driven init plan as a confirmable summary.

        Everything the harness can infer is *shown*, not asked (ADR-004):
        detected template set with per-file reasons, capabilities, profile,
        ticket prefix. The operator accepts or drops into Customize.
        """
        from .init_planning import plan_files

        rows = plan_files(plan)

        if not RICH_AVAILABLE or not self.console:
            print(f"\n{CHARS['memo']} Detected Plan")
            print("=" * 60)
            for filename, reason in rows:
                print(f"  {CHARS['check']} {filename}  ({reason})")
            if plan.get("ticket_prefix"):
                print(f"\nTicket prefix: {plan['ticket_prefix']}")
            return

        table = Table(
            show_header=True,
            box=box.ROUNDED,
            title="Detected Plan",
            title_style="bold cyan",
        )
        table.add_column("Will create", style="bold green", no_wrap=True)
        table.add_column("Why", style="dim")
        for filename, reason in rows:
            table.add_row(filename, reason)
        self.console.print(table)
        if plan.get("ticket_prefix"):
            self.console.print(
                f"[dim]Ticket prefix:[/dim] [bold]{plan['ticket_prefix']}[/bold]"
                "  [dim](adjustable below)[/dim]"
            )
        self.console.print()

    def ask_plan_choice(self, *, offer_prefix: bool) -> Optional[str]:
        """Accept the detected plan, adjust the prefix, customize, or cancel."""
        if not QUESTIONARY_AVAILABLE:
            options = "y = accept, c = customize, n = cancel" + (
                ", p = change ticket prefix" if offer_prefix else ""
            )
            while True:
                response = input(f"Proceed with this plan? ({options}): ").lower()
                if response in ["y", "yes", ""]:
                    return "accept"
                if response in ["c", "custom", "customize"]:
                    return "customize"
                if offer_prefix and response in ["p", "prefix"]:
                    return "prefix"
                if response in ["n", "no", "q"]:
                    return None
                print(f"Please enter one of: {options}")

        choices = [
            questionary.Choice(
                f"{CHARS['check']} Looks right — scaffold it", value="accept"
            )
        ]
        if offer_prefix:
            choices.append(
                questionary.Choice(
                    f"{CHARS['ticket']} Change the ticket prefix", value="prefix"
                )
            )
        choices.append(
            questionary.Choice(
                f"{CHARS['wrench']} Customize (advanced — pick files and toggles)",
                value="customize",
            )
        )
        choices.append(questionary.Choice(f"{CHARS['cross']} Cancel", value=None))

        return questionary.select(
            "Proceed with this plan?",
            choices=choices,
            style=PROTO_GEAR_STYLE,
        ).ask()

    def _ask_intent_list(self, prompt: str, instruction: str) -> list:
        """Collect short free-text items until the operator submits a blank line."""
        items = []
        while True:
            if QUESTIONARY_AVAILABLE:
                answer = questionary.text(
                    prompt if not items else f"{prompt} (another?)",
                    style=PROTO_GEAR_STYLE,
                    instruction=instruction if not items else "Enter to finish",
                ).ask()
            else:
                answer = input(f"{prompt} (Enter to finish): ")
            if answer is None:  # cancelled prompt — treat as done, not as abort
                break
            answer = answer.strip()
            if not answer:
                break
            items.append(answer)
        return items

    def ask_intent_capture(self, current_dir: Path) -> Dict:
        """The planning intake: capture the durable, non-derivable facts.

        Three progressive prompts — what the project *is*, what an agent must
        *never* do, and the non-obvious house conventions. Every prompt is
        skippable (plain Enter) so init never gets heavier than the old flow;
        whatever is captured seeds PROJECT_SPECIFICATIONS.md, the Critical
        Rules, and a first lesson (ADR-004).
        """
        if self.console:
            self.print_panel(
                "\n".join(
                    [
                        "",
                        "The mechanical choices are detected — the next few prompts",
                        "capture what an agent [bold]cannot derive[/bold] from the code.",
                        "",
                        "[dim]Every prompt is optional: press Enter to skip.[/dim]",
                        "",
                    ]
                ),
                title=f"{CHARS['memo']} Planning Intake",
                border_style="cyan",
            )
        else:
            print(f"\n{CHARS['memo']} Planning Intake")
            print("-" * 50)
            print(
                "Capture what an agent cannot derive. Press Enter to skip any prompt."
            )

        intent: Dict = {}

        description = self.ask_project_specifications(current_dir)
        if description:
            intent["project_description"] = description

        boundaries = self._ask_intent_list(
            "Boundary / invariant — what must an agent NEVER do here?",
            "e.g. 'NEVER commit generated fixtures' — becomes a Critical Rule",
        )
        if boundaries:
            intent["boundaries"] = boundaries

        conventions = self._ask_intent_list(
            "House convention — a non-obvious rule of this codebase?",
            "e.g. 'all timestamps are UTC ints' — seeds specs + a first lesson",
        )
        if conventions:
            intent["conventions"] = conventions

        return intent

    def ask_capabilities_system(self) -> bool:
        """Ask user if they want Universal Capabilities System"""
        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple y/n prompt
            print(f"\n{CHARS['wrench']} Universal Capabilities System")
            print("-" * 30)
            print("Proto Gear can generate a modular capability system that allows")
            print("AI agents to dynamically load and use specialized capabilities.")
            while True:
                response = input(
                    "\nGenerate .proto-gear/ capability system? (y/n): "
                ).lower()
                if response in ["y", "yes"]:
                    return True
                elif response in ["n", "no"]:
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
            "",
        ]

        if self.console:
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['wrench']} Universal Capabilities System",
                border_style="cyan",
            )

        answer = questionary.select(
            "Generate .proto-gear/ capability system?",
            choices=[
                questionary.Choice(
                    f"{CHARS['check']} Yes - Generate capability system", value=True
                ),
                questionary.Choice(
                    f"{CHARS['cross']} No - Skip this step", value=False
                ),
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys to navigate, Enter to select)",
        ).ask()

        return answer if answer is not None else False

    def ask_capability_profile(self, default: Optional[str] = None) -> str:
        """
        Ask which capability output profile to install.

        Only meaningful once capabilities are being generated: ``frontier``
        ships slim stubs (title, when-to-use, a pointer to the host docs — the
        generic methodology is left to the model), ``verbose`` ships the full
        playbooks for smaller / local / older models. Returns a name from
        ``CAPABILITY_PROFILES``. Nothing is lost either way — re-init with the
        other profile swaps the corpus.
        """
        from proto_gear_pkg.module_core.capability_profile import (
            CAPABILITY_PROFILES,
            normalize_profile,
        )

        default = normalize_profile(default)

        if not QUESTIONARY_AVAILABLE:
            # Fallback to a simple text prompt
            print(f"\n{CHARS['gear']} Capability Profile")
            print("-" * 30)
            print("  frontier - slim stubs (recommended for frontier models)")
            print("  verbose  - full playbooks (for smaller/older models)")
            while True:
                response = (
                    input(
                        f"\nCapability profile [frontier/verbose] "
                        f"(Enter for '{default}'): "
                    )
                    .strip()
                    .lower()
                )
                if not response:
                    return default
                if response in CAPABILITY_PROFILES:
                    return response
                print("Please enter 'frontier' or 'verbose'")

        # Enhanced questionary prompt
        description = [
            "",
            "How verbose should the installed capabilities be?",
            "",
            "[bold]frontier[/bold] - slim stubs: title, when-to-use, a pointer to",
            "  the host docs. The generic methodology is left to the model.",
            "  Best for frontier models (fewer per-session tokens).",
            "",
            "[bold]verbose[/bold] - the full playbooks: methodology, worked",
            "  examples, checklists. Best for smaller / local / older models,",
            "  or humans who want the whole guide.",
            "",
            "[dim]Nothing is lost either way — re-init with the other profile "
            "swaps the corpus.[/dim]",
            "",
        ]
        if self.console:
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['gear']} Capability Profile",
                border_style="cyan",
            )

        choices = [
            questionary.Choice(
                f"{CHARS['check']} frontier - slim stubs (recommended for frontier models)",
                value="frontier",
            ),
            questionary.Choice(
                f"{CHARS['bullet']} verbose - full playbooks (for smaller/older models)",
                value="verbose",
            ),
        ]
        # Pre-select the caller's default by putting it first
        if default == "verbose":
            choices = list(reversed(choices))

        answer = questionary.select(
            "Capability profile:",
            choices=choices,
            default=choices[0],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys, Enter to select)",
        ).ask()

        return normalize_profile(answer) if answer else default

    def ask_core_templates_selection(self) -> Dict[str, bool]:
        """
        Ask user which core templates to generate (Custom path)
        Uses auto-discovery to show all available templates (v0.6.0)
        Returns dict with template selections
        """
        # Discover available templates
        available_templates = {}
        if discover_available_templates:
            discovered = discover_available_templates()
            # Filter out files that are always written or regenerated by
            # sync_context (AGENTS, PROJECT_STATUS, SESSION_HANDOFF,
            # AGENT_CONTEXT) — offering them as optional templates was wrong;
            # the user cannot opt out and sync_context overwrites them anyway.
            available_templates = {
                k: v for k, v in discovered.items() if k not in NON_SELECTABLE_TEMPLATES
            }
        else:
            # Fallback to hardcoded list
            available_templates = {
                "TESTING": {"name": "TESTING", "filename": "TESTING.md"},
                "BRANCHING": {"name": "BRANCHING", "filename": "BRANCHING.md"},
                "CONTRIBUTING": {"name": "CONTRIBUTING", "filename": "CONTRIBUTING.md"},
                "SECURITY": {"name": "SECURITY", "filename": "SECURITY.md"},
                "ARCHITECTURE": {"name": "ARCHITECTURE", "filename": "ARCHITECTURE.md"},
                "CODE_OF_CONDUCT": {
                    "name": "CODE_OF_CONDUCT",
                    "filename": "CODE_OF_CONDUCT.md",
                },
            }

        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple prompts
            print(f"\n{CHARS['memo']} Template Selection")
            print("-" * 50)
            print("Select which templates to generate:")
            print(
                f"  {CHARS['bullet']} AGENTS.md and PROJECT_STATUS.md are always included"
            )
            print(f"\nAdditional templates ({len(available_templates)} available):")

            for idx, (name, info) in enumerate(sorted(available_templates.items()), 1):
                print(f"  {idx}. {info['filename']}")

            print("  A. Select ALL additional templates")

            response = (
                input(f"\nSelect templates (e.g., '1,2' or 'A' for all): ")
                .strip()
                .upper()
            )

            result = {
                "AGENTS": True,
                "PROJECT_STATUS": True,
            }

            if response == "A":
                # Select all
                for name in available_templates:
                    result[name] = True
                result["with_all"] = True
            else:
                # Parse selection
                selected_indices = set(response.replace(" ", "").split(","))
                template_list = sorted(available_templates.keys())

                for idx_str in selected_indices:
                    if idx_str.isdigit():
                        idx = int(idx_str) - 1
                        if 0 <= idx < len(template_list):
                            result[template_list[idx]] = True

                result["with_all"] = len(
                    [v for v in result.values() if v is True]
                ) - 2 == len(available_templates)

            return result

        # Enhanced selection with questionary
        if self.console:
            description = [
                "",
                f"[dim]AGENTS.md and PROJECT_STATUS.md are always included (core functionality)[/dim]",
                "",
                f"Select additional templates to generate ([cyan]{len(available_templates)} available[/cyan]):",
                "",
            ]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['memo']} Template Selection",
                border_style="cyan",
            )

        # Build choices dynamically from discovered templates
        choices = []
        template_descriptions = {
            "TESTING": "TDD workflow and testing patterns",
            "BRANCHING": "Git workflow conventions",
            "CONTRIBUTING": "Contribution guidelines for open-source",
            "SECURITY": "Security policy and vulnerability reporting",
            "ARCHITECTURE": "System design documentation",
            "CODE_OF_CONDUCT": "Community guidelines",
        }

        for name in sorted(available_templates.keys()):
            desc = template_descriptions.get(name, "Project template")
            # Default TESTING to checked, others unchecked
            checked = name == "TESTING"
            choices.append(
                questionary.Choice(f"{name}.md - {desc}", value=name, checked=checked)
            )

        selected = questionary.checkbox(
            "Select additional templates:",
            choices=choices,
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)",
        ).ask()

        if selected is None:
            selected = []

        # Build result dict
        result = {
            "AGENTS": True,
            "PROJECT_STATUS": True,
        }

        for name in available_templates:
            result[name] = name in selected

        # Check if user selected all
        result["with_all"] = len(selected) == len(available_templates)

        return result

    def ask_git_workflow_options(self, git_config: Dict, current_dir: Path) -> Dict:
        """
        Ask user about Git workflow configuration options (Custom path)
        Returns dict with git-related configuration
        """
        git_detected = git_config.get("is_git_repo", False)

        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple prompts
            print(f"\n{CHARS['clipboard']} Git Workflow Configuration")
            print("-" * 50)

            if git_detected:
                print(f"{CHARS['check']} Git repository detected")
                branching = input("\nGenerate BRANCHING.md? (y/n): ").lower() in [
                    "y",
                    "yes",
                ]

                if branching:
                    suggested_prefix = (
                        current_dir.name.upper().replace("-", "").replace("_", "")[:15]
                    )
                    if not suggested_prefix or len(suggested_prefix) < 2:
                        suggested_prefix = "PROJ"

                    print(
                        f"\nTicket prefix for branch naming (e.g., feature/{suggested_prefix}-123-description)"
                    )
                    prefix = input(
                        f"Enter ticket prefix [{suggested_prefix}]: "
                    ).strip()
                    ticket_prefix = prefix if prefix else suggested_prefix
                else:
                    ticket_prefix = None
            else:
                print(
                    f"{CHARS['cross']} No git repository detected - skipping Git workflow"
                )
                branching = False
                ticket_prefix = None

            return {"with_branching": branching, "ticket_prefix": ticket_prefix}

        # Enhanced selection with questionary
        if self.console:
            status = (
                f"[green]{CHARS['check']} Git detected[/green]"
                if git_detected
                else f"[yellow]{CHARS['cross']} No git repository[/yellow]"
            )
            description = ["", status, "", "Configure Git workflow options:", ""]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['clipboard']} Git Workflow",
                border_style="cyan",
            )

        if not git_detected:
            return {"with_branching": False, "ticket_prefix": None}

        # Ask about BRANCHING.md
        generate_branching = questionary.confirm(
            "Generate BRANCHING.md (branch naming & commit conventions)?",
            default=True,
            style=PROTO_GEAR_STYLE,
        ).ask()

        if not generate_branching:
            return {"with_branching": False, "ticket_prefix": None}

        # Ask for ticket prefix
        suggested_prefix = (
            current_dir.name.upper().replace("-", "").replace("_", "")[:15]
        )
        if not suggested_prefix or len(suggested_prefix) < 2:
            suggested_prefix = "PROJ"

        ticket_prefix = questionary.text(
            "Ticket prefix for branch naming:",
            default=suggested_prefix,
            validate=lambda text: len(text) > 0,
            style=PROTO_GEAR_STYLE,
            instruction=f"(Used in: feature/{suggested_prefix}-123-description)",
        ).ask()

        return {
            "with_branching": True,
            "ticket_prefix": ticket_prefix if ticket_prefix else suggested_prefix,
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

            include = input("\nInclude capabilities? (y/n): ").lower() in ["y", "yes"]

            if not include:
                return {"enabled": False}

            # Show detailed info
            print("\nAvailable capabilities:")
            print(f"\n  [SKILLS] - 4 skills available:")
            for key, skill in CAPABILITIES_METADATA["skills"].items():
                print(f"    - {skill['name']}: {skill['description']}")

            print(f"\n  [WORKFLOWS] - 5 workflows available:")
            for key, workflow in CAPABILITIES_METADATA["workflows"].items():
                print(f"    - {workflow['name']}: {workflow['description']}")

            print(f"\n  [COMMANDS] - 1 command available:")
            for key, cmd in CAPABILITIES_METADATA["commands"].items():
                print(f"    - {cmd['name']}: {cmd['description']}")

            # Ask about selection level
            print("\nSelection options:")
            print(f"  1. All capabilities (4 skills + 5 workflows + 1 command)")
            print(f"  2. Select by category (Skills, Workflows, Commands)")
            print(f"  3. Select individual capabilities (granular)")

            choice = input("\nChoice [1]: ").strip()

            if choice == "3":
                # Granular selection
                return self._ask_granular_capabilities_fallback()
            elif choice == "2":
                # Category selection
                skills = input("Include all Skills? (y/n): ").lower() in ["y", "yes"]
                workflows = input("Include all Workflows? (y/n): ").lower() in [
                    "y",
                    "yes",
                ]
                commands = input("Include all Commands? (y/n): ").lower() in [
                    "y",
                    "yes",
                ]

                return {
                    "enabled": True,
                    "skills": skills,
                    "workflows": workflows,
                    "commands": commands,
                }
            else:
                # All capabilities
                return {
                    "enabled": True,
                    "skills": True,
                    "workflows": True,
                    "commands": True,
                }

        # Enhanced selection with questionary
        if self.console:
            # Show detailed breakdown
            description = [
                "",
                "The capability system provides modular, reusable patterns for AI agents.",
                "",
                "[bold cyan]Available Capabilities:[/bold cyan]",
                "",
                "[yellow]Skills (4):[/yellow]",
            ]
            for key, skill in CAPABILITIES_METADATA["skills"].items():
                description.append(
                    f"  {CHARS['bullet']} {skill['name']} - {skill['description']}"
                )

            description.append("")
            description.append("[yellow]Workflows (5):[/yellow]")
            for key, workflow in CAPABILITIES_METADATA["workflows"].items():
                description.append(
                    f"  {CHARS['bullet']} {workflow['name']} - {workflow['description']}"
                )

            description.append("")
            description.append("[yellow]Commands (1):[/yellow]")
            for key, cmd in CAPABILITIES_METADATA["commands"].items():
                description.append(
                    f"  {CHARS['bullet']} {cmd['name']} - {cmd['description']}"
                )

            description.append("")

            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['wrench']} Universal Capabilities System",
                border_style="cyan",
            )

        # Ask if user wants capabilities at all
        include_capabilities = questionary.confirm(
            "Include .proto-gear/ capability system?",
            default=True,
            style=PROTO_GEAR_STYLE,
        ).ask()

        if not include_capabilities:
            return {"enabled": False}

        # Ask about selection level
        selection_type = questionary.select(
            "How would you like to configure capabilities?",
            choices=[
                questionary.Choice(
                    f"{CHARS['check']} All capabilities (4 skills + 5 workflows + 1 command)",
                    value="all",
                ),
                questionary.Choice(
                    f"{CHARS['wrench']} Select by category (Skills, Workflows, Commands)",
                    value="category",
                ),
                questionary.Choice(
                    f"🔍 Select individual capabilities (granular)", value="granular"
                ),
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys, Enter to select)",
        ).ask()

        if selection_type == "all":
            return {
                "enabled": True,
                "skills": True,
                "workflows": True,
                "commands": True,
            }
        elif selection_type == "granular":
            return self._ask_granular_capabilities()

        # Category selection
        categories = questionary.checkbox(
            "Select capability categories:",
            choices=[
                questionary.Choice(
                    f"Skills (4) - TDD, Debugging, Code Review, Refactoring",
                    value="skills",
                    checked=True,
                ),
                questionary.Choice(
                    f"Workflows (5) - Feature Dev, Bug Fix, Hotfix, Release, Finalize",
                    value="workflows",
                    checked=True,
                ),
                questionary.Choice(
                    f"Commands (1) - Create Ticket", value="commands", checked=True
                ),
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)",
        ).ask()

        if categories is None:
            categories = []

        return {
            "enabled": True,
            "skills": "skills" in categories,
            "workflows": "workflows" in categories,
            "commands": "commands" in categories,
        }

    def _ask_granular_capabilities(self) -> Dict:
        """Ask user to select individual capabilities"""
        if self.console:
            self.console.print(
                f"\n[bold cyan]Select individual capabilities:[/bold cyan]\n"
            )

        # Select individual skills
        skill_choices = []
        for key, skill in CAPABILITIES_METADATA["skills"].items():
            skill_choices.append(
                questionary.Choice(
                    f"{skill['name']} - {skill['details']}", value=key, checked=True
                )
            )

        selected_skills = questionary.checkbox(
            "Skills to include:",
            choices=skill_choices,
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)",
        ).ask()

        if selected_skills is None:
            selected_skills = []

        # Select individual workflows
        workflow_choices = []
        for key, workflow in CAPABILITIES_METADATA["workflows"].items():
            workflow_choices.append(
                questionary.Choice(
                    f"{workflow['name']} - {workflow['details']}",
                    value=key,
                    checked=True,
                )
            )

        selected_workflows = questionary.checkbox(
            "Workflows to include:",
            choices=workflow_choices,
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)",
        ).ask()

        if selected_workflows is None:
            selected_workflows = []

        # Select individual commands
        command_choices = []
        for key, cmd in CAPABILITIES_METADATA["commands"].items():
            command_choices.append(
                questionary.Choice(
                    f"{cmd['name']} - {cmd['details']}", value=key, checked=True
                )
            )

        selected_commands = questionary.checkbox(
            "Commands to include:",
            choices=command_choices,
            style=PROTO_GEAR_STYLE,
            instruction="(Space to select/deselect, Enter to confirm)",
        ).ask()

        if selected_commands is None:
            selected_commands = []

        return {
            "enabled": True,
            "skills": selected_skills if selected_skills else False,
            "workflows": selected_workflows if selected_workflows else False,
            "commands": selected_commands if selected_commands else False,
            "granular": True,  # Flag to indicate granular selection
        }

    def _ask_granular_capabilities_fallback(self) -> Dict:
        """Fallback for granular capability selection without questionary"""
        print("\n[SKILLS] Select skills to include:")
        selected_skills = []
        for key, skill in CAPABILITIES_METADATA["skills"].items():
            response = input(f"  Include {skill['name']}? (y/n): ").lower()
            if response in ["y", "yes"]:
                selected_skills.append(key)

        print("\n[WORKFLOWS] Select workflows to include:")
        selected_workflows = []
        for key, workflow in CAPABILITIES_METADATA["workflows"].items():
            response = input(f"  Include {workflow['name']}? (y/n): ").lower()
            if response in ["y", "yes"]:
                selected_workflows.append(key)

        print("\n[COMMANDS] Select commands to include:")
        selected_commands = []
        for key, cmd in CAPABILITIES_METADATA["commands"].items():
            response = input(f"  Include {cmd['name']}? (y/n): ").lower()
            if response in ["y", "yes"]:
                selected_commands.append(key)

        return {
            "enabled": True,
            "skills": selected_skills if selected_skills else False,
            "workflows": selected_workflows if selected_workflows else False,
            "commands": selected_commands if selected_commands else False,
            "granular": True,
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
                if response in ["y", "yes"]:
                    return True
                elif response in ["n", "no"]:
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
            "",
        ]

        if git_config["is_git_repo"]:
            description.append(
                f"[green]{CHARS['check']} Git repository detected - branching strategy recommended[/green]"
            )
        else:
            description.append(
                "[yellow]! No Git repository - you can still generate the strategy for future use[/yellow]"
            )

        if self.console:
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['clipboard']} Branching & Git Workflow",
                border_style="cyan",
            )

        answer = questionary.select(
            "Generate BRANCHING.md?",
            choices=[
                questionary.Choice(
                    f"{CHARS['check']} Yes - Generate branching strategy", value=True
                ),
                questionary.Choice(
                    f"{CHARS['cross']} No - Skip this step", value=False
                ),
            ],
            style=PROTO_GEAR_STYLE,
            instruction="(Use arrow keys to navigate, Enter to select)",
        ).ask()

        return answer if answer is not None else False

    def ask_ticket_prefix(self, suggested_prefix: str) -> str:
        """Ask for ticket prefix with validation"""
        if not QUESTIONARY_AVAILABLE:
            # Fallback
            print(f"\n{CHARS['ticket']} Ticket Prefix Configuration")
            print("-" * 30)
            print(f"Suggested prefix: {suggested_prefix}")
            response = (
                input(f"Enter ticket prefix (press Enter for '{suggested_prefix}'): ")
                .strip()
                .upper()
            )

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
                "",
            ]
            self.print_panel(
                "\n".join(description),
                title=f"{CHARS['ticket']} Ticket Prefix Configuration",
                border_style="cyan",
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
            instruction=f"Press Enter for default ({suggested_prefix})",
        ).ask()

        if answer and answer.strip():
            result = answer.strip().upper()
            if self.console:
                self.console.print(
                    f"[green]{CHARS['check']} Using prefix: {result}[/green]\n"
                )
            return result
        else:
            if self.console:
                self.console.print(
                    f"[green]{CHARS['check']} Using suggested prefix: {suggested_prefix}[/green]\n"
                )
            return suggested_prefix

    def ask_project_specifications(self, current_dir: Path):
        """
        If PROJECT_SPECIFICATIONS.md already exists, return None silently — the agent
        will handle it (architecture extraction task in AGENTS.md).

        If it does not exist, prompt the user for a short project description.
        Returns the description string, or None to skip.
        """
        specs_dest = current_dir / "PROJECT_SPECIFICATIONS.md"
        if specs_dest.exists():
            return None  # Agent will extract architecture per AGENTS.md instructions

        if not QUESTIONARY_AVAILABLE:
            # Fallback to simple prompt
            print(f"\n{CHARS['memo']} Project Description")
            print("-" * 50)
            print("No PROJECT_SPECIFICATIONS.md found.")
            print("Enter a brief description of your project (1-3 sentences).")
            print(
                "Proto Gear will create a PROJECT_SPECIFICATIONS.md stub for agents to expand."
            )
            description = input(
                "\nProject description (or press Enter to skip): "
            ).strip()
            return description if description else None

        if self.console:
            self.print_panel(
                "\n".join(
                    [
                        "",
                        "No [bold]PROJECT_SPECIFICATIONS.md[/bold] found.",
                        "Enter a brief description — Proto Gear will generate a structured stub.",
                        "",
                        "[dim]Agents will expand it and extract architecture into PROJECT_ARCHITECTURE.md.[/dim]",
                        "",
                    ]
                ),
                title=f"{CHARS['memo']} Project Description",
                border_style="cyan",
            )

        description = questionary.text(
            "Project description (1-3 sentences, or Enter to skip):",
            style=PROTO_GEAR_STYLE,
            instruction="Agents will use this as a starting point",
        ).ask()

        return description.strip() if description and description.strip() else None

    def show_configuration_summary(
        self, config: Dict, project_info: Dict, current_dir: Path
    ) -> bool:
        """Display configuration summary and ask for confirmation"""
        # Only the custom path reaches this summary since ADR-004 (the
        # detected-plan path confirms on the plan itself); "custom" governs
        # whether unselected templates are shown as dimmed rows.
        preset = config.get("preset", "custom")

        if not RICH_AVAILABLE:
            # Fallback
            print(f"\n{CHARS['memo']} Configuration Summary")
            print("=" * 60)
            print(f"Project: {current_dir.name}")
            print(f"Type: {project_info.get('type', 'Generic')}")
            if project_info.get("framework"):
                print(f"Framework: {project_info['framework']}")

            print("\nFiles to be created:")
            print(f"  {CHARS['check']} AGENTS.md (AI agent integration guide)")
            print(f"  {CHARS['check']} PROJECT_STATUS.md (Project state tracking)")

            if config.get("with_branching"):
                print(f"  {CHARS['check']} BRANCHING.md (Git workflow conventions)")
                print(f"\nTicket Prefix: {config['ticket_prefix']}")
            else:
                print(f"  {CHARS['cross']} BRANCHING.md (not selected)")

            if config.get("with_capabilities"):
                print(
                    f"  {CHARS['check']} .proto-gear/ (Universal Capabilities System)"
                )
                if config.get("profile"):
                    print(f"      Profile: {config['profile']}")
            else:
                print(f"  {CHARS['cross']} .proto-gear/ (not selected)")

            while True:
                response = input("\nProceed with setup? (y/n): ").lower()
                if response in ["y", "yes"]:
                    return True
                elif response in ["n", "no"]:
                    return False
                print("Please enter 'y' or 'n'")

        # Rich formatted summary
        table = Table(
            show_header=True,
            box=box.ROUNDED,
            title="Configuration",
            title_style="bold cyan",
        )
        table.add_column("Setting", style="bold cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Project", current_dir.name)
        table.add_row("Type", project_info.get("type", "Generic"))
        if project_info.get("framework"):
            table.add_row("Framework", project_info["framework"])
        table.add_row(
            "Branching",
            (
                f"{CHARS['check']} Enabled"
                if config.get("with_branching")
                else f"{CHARS['cross']} Disabled"
            ),
        )
        if config.get("with_branching"):
            table.add_row("Ticket Prefix", config.get("ticket_prefix", "N/A"))
        table.add_row(
            "Capabilities",
            (
                f"{CHARS['check']} Enabled"
                if config.get("with_capabilities")
                else f"{CHARS['cross']} Disabled"
            ),
        )
        if config.get("with_capabilities") and config.get("profile"):
            table.add_row("Profile", config["profile"])

        # Always-written core files (created regardless of template selection).
        files_list = [
            f"{CHARS['check']} AGENTS.md (AI agent integration guide)",
            f"{CHARS['check']} SESSION_HANDOFF.md (rolling session handoff)",
            f"{CHARS['check']} PROJECT_STATUS.md (Project state tracking)",
        ]

        # Handle with_all flag (v0.5.2+)
        with_all = config.get("with_all", False)

        if with_all:
            # All templates selected
            files_list.append(f"{CHARS['check']} TESTING.md (TDD workflow)")
            files_list.append(
                f"{CHARS['check']} BRANCHING.md (Git workflow conventions)"
            )
            files_list.append(
                f"{CHARS['check']} CONTRIBUTING.md (Contribution guidelines)"
            )
            files_list.append(f"{CHARS['check']} SECURITY.md (Security policy)")
            files_list.append(f"{CHARS['check']} ARCHITECTURE.md (System design docs)")
            files_list.append(
                f"{CHARS['check']} CODE_OF_CONDUCT.md (Community guidelines)"
            )
        else:
            # Handle custom core templates
            core_templates = config.get("core_templates", {})
            if core_templates.get("TESTING"):
                files_list.append(f"{CHARS['check']} TESTING.md (TDD workflow)")
            elif preset == "custom":
                files_list.append(
                    f"[dim]{CHARS['cross']} TESTING.md (not selected)[/dim]"
                )

            if config.get("with_branching"):
                files_list.append(
                    f"{CHARS['check']} BRANCHING.md (Git workflow conventions)"
                )
            else:
                files_list.append(
                    f"[dim]{CHARS['cross']} BRANCHING.md (not selected)[/dim]"
                )

            # Show other templates if selected in custom path
            if core_templates.get("CONTRIBUTING"):
                files_list.append(
                    f"{CHARS['check']} CONTRIBUTING.md (Contribution guidelines)"
                )
            elif preset == "custom":
                files_list.append(
                    f"[dim]{CHARS['cross']} CONTRIBUTING.md (not selected)[/dim]"
                )

            if core_templates.get("SECURITY"):
                files_list.append(f"{CHARS['check']} SECURITY.md (Security policy)")
            elif preset == "custom":
                files_list.append(
                    f"[dim]{CHARS['cross']} SECURITY.md (not selected)[/dim]"
                )

            if core_templates.get("ARCHITECTURE"):
                files_list.append(
                    f"{CHARS['check']} ARCHITECTURE.md (System design docs)"
                )
            elif preset == "custom":
                files_list.append(
                    f"[dim]{CHARS['cross']} ARCHITECTURE.md (not selected)[/dim]"
                )

            if core_templates.get("CODE_OF_CONDUCT"):
                files_list.append(
                    f"{CHARS['check']} CODE_OF_CONDUCT.md (Community guidelines)"
                )
            elif preset == "custom":
                files_list.append(
                    f"[dim]{CHARS['cross']} CODE_OF_CONDUCT.md (not selected)[/dim]"
                )

        # Agent context + host-config mirrors are always generated by
        # sync_context. Surface them so the summary matches what init writes.
        files_list.append(f"{CHARS['check']} AGENT_CONTEXT.md (auto-loaded agent skim)")
        host_mirrors = ", ".join(
            f for f in SYNC_GENERATED_FILES if f != "AGENT_CONTEXT.md"
        )
        files_list.append(
            f"{CHARS['check']} Host configs synced ([dim]{host_mirrors}[/dim])"
        )

        # Handle granular capabilities
        capabilities_config = config.get("capabilities_config", {})

        if config.get("with_capabilities"):
            if capabilities_config and capabilities_config.get("enabled"):
                # Check if granular selection was used
                if capabilities_config.get("granular"):
                    # Granular individual selection
                    selected_items = []

                    skills = capabilities_config.get("skills", [])
                    if isinstance(skills, list) and skills:
                        skill_names = [
                            CAPABILITIES_METADATA["skills"][k]["name"]
                            for k in skills
                            if k in CAPABILITIES_METADATA["skills"]
                        ]
                        selected_items.append(f"Skills: {', '.join(skill_names)}")

                    workflows = capabilities_config.get("workflows", [])
                    if isinstance(workflows, list) and workflows:
                        workflow_names = [
                            CAPABILITIES_METADATA["workflows"][k]["name"]
                            for k in workflows
                            if k in CAPABILITIES_METADATA["workflows"]
                        ]
                        selected_items.append(f"Workflows: {', '.join(workflow_names)}")

                    commands = capabilities_config.get("commands", [])
                    if isinstance(commands, list) and commands:
                        command_names = [
                            CAPABILITIES_METADATA["commands"][k]["name"]
                            for k in commands
                            if k in CAPABILITIES_METADATA["commands"]
                        ]
                        selected_items.append(f"Commands: {', '.join(command_names)}")

                    if selected_items:
                        files_list.append(
                            f"{CHARS['check']} .proto-gear/ capability system:"
                        )
                        for item in selected_items:
                            files_list.append(f"  [dim]{CHARS['bullet']} {item}[/dim]")
                    else:
                        files_list.append(
                            f"[dim]{CHARS['cross']} .proto-gear/ (no capabilities selected)[/dim]"
                        )
                else:
                    # Category selection (Skills, Workflows, Commands)
                    cap_parts = []
                    if capabilities_config.get("skills"):
                        cap_parts.append("Skills (4)")
                    if capabilities_config.get("workflows"):
                        cap_parts.append("Workflows (5)")
                    if capabilities_config.get("commands"):
                        cap_parts.append("Commands (1)")

                    if cap_parts:
                        cap_desc = ", ".join(cap_parts)
                        files_list.append(f"{CHARS['check']} .proto-gear/ ({cap_desc})")
                    else:
                        files_list.append(
                            f"[dim]{CHARS['cross']} .proto-gear/ (no categories selected)[/dim]"
                        )
            else:
                # Preset path (all capabilities) or empty config
                files_list.append(
                    f"{CHARS['check']} .proto-gear/ (All capabilities: 4 skills + 5 workflows + 1 command)"
                )
        else:
            files_list.append(
                f"[dim]{CHARS['cross']} .proto-gear/ (not selected)[/dim]"
            )

        files_text = "\n".join(files_list)

        # Print table first
        if self.console:
            self.console.print(
                f"\n{CHARS['memo']} [bold cyan]Configuration Summary[/bold cyan]"
            )
            self.console.print(table)
            self.console.print()  # Empty line

        # Then print files panel
        files_panel_content = f"[bold]Files to create:[/bold]\n\n{files_text}"
        self.print_panel(
            files_panel_content, title=f"{CHARS['memo']} Files", border_style="cyan"
        )

        if not QUESTIONARY_AVAILABLE:
            # Fallback if questionary unavailable
            while True:
                response = input("\nProceed with setup? (y/n): ").lower()
                if response in ["y", "yes"]:
                    return True
                elif response in ["n", "no"]:
                    return False
                print("Please enter 'y' or 'n'")

        answer = questionary.confirm(
            "Proceed with setup?", default=True, style=PROTO_GEAR_STYLE
        ).ask()

        return answer if answer is not None else False


def run_enhanced_wizard(
    project_info: Dict, git_config: Dict, current_dir: Path
) -> Optional[Dict]:
    """Fresh-init planning intake (ADR-004 / PROTO-100).

    The interaction is inverted from the old preset configurator: the
    mechanical choices (which files, which toggles) are *detected* and shown
    as one confirmable plan, while the prompts capture the durable,
    non-derivable facts — what the project is, its boundaries/invariants, and
    house conventions. ``Customize`` keeps the old granular wizard as the
    advanced escape hatch. Returns a configuration dict or None if cancelled.
    """
    from .init_planning import build_detected_plan

    wizard = RichWizard()

    # Clear screen for single-page app experience
    wizard.clear_screen()

    # Print header
    if wizard.console:
        wizard.console.print("\n[bold cyan]ProtoGear Planning Intake[/bold cyan]")
        wizard.console.print("[dim]" + "=" * 60 + "[/dim]\n")
        wizard.console.print(
            "[dim]Detect the mechanical setup, capture the durable intent[/dim]\n"
        )
    else:
        print("\nProtoGear Planning Intake")
        print("=" * 60)
        print("Detect the mechanical setup, capture the durable intent\n")

    # Show project detection
    project_panel = wizard.create_project_info_panel(
        project_info, git_config, current_dir
    )
    wizard.print_panel(
        project_panel, title=f"{CHARS['chart']} Project Detection", border_style="cyan"
    )

    # The intake spine: durable, non-derivable facts first (ADR-004 move 2).
    config: Dict = {}
    try:
        config.update(wizard.ask_intent_capture(current_dir))
    except KeyboardInterrupt:
        return None

    # Detection-driven plan, presented as one confirmable summary (move 1).
    plan = build_detected_plan(project_info, git_config, current_dir)
    while True:
        wizard.clear_screen()
        wizard.show_detected_plan(plan)
        try:
            choice = wizard.ask_plan_choice(
                offer_prefix=bool(plan.get("with_branching"))
            )
        except KeyboardInterrupt:
            return None

        if choice is None:
            return None
        if choice == "prefix":
            try:
                plan["ticket_prefix"] = wizard.ask_ticket_prefix(
                    plan.get("ticket_prefix") or "PROJ"
                )
            except KeyboardInterrupt:
                return None
            continue  # redraw the plan with the new prefix
        if choice == "accept":
            config.update(
                {
                    "with_branching": plan["with_branching"],
                    "ticket_prefix": plan["ticket_prefix"],
                    "with_capabilities": plan["with_capabilities"],
                    "profile": plan["profile"],
                    "core_templates": dict(plan["core_templates"]),
                    "confirmed": True,
                }
            )
            return config
        if choice == "customize":
            break

    # CUSTOM PATH: Granular selection wizard (the advanced escape hatch).
    config = {
        "preset": "custom",
        **{
            k: v
            for k, v in config.items()
            if k in ("project_description", "boundaries", "conventions")
        },
    }

    # Stage 1: Core Templates Selection
    wizard.clear_screen()
    wizard.show_step_header(1, 3, "Core Templates", project_info, current_dir)
    try:
        core_templates = wizard.ask_core_templates_selection()
        config["core_templates"] = core_templates
    except KeyboardInterrupt:
        return None

    # Stage 2: Git Workflow Configuration
    wizard.clear_screen()
    wizard.show_step_header(2, 3, "Git Workflow", project_info, current_dir)
    try:
        # Check if BRANCHING was selected in Stage 1 - if so, sync it
        if core_templates.get("BRANCHING"):
            # User selected BRANCHING in template selection
            # Ask for ticket prefix using wizard method
            if git_config.get("is_git_repo"):
                suggested_prefix = (
                    current_dir.name.upper().replace("-", "").replace("_", "")[:15]
                )
                if not suggested_prefix or len(suggested_prefix) < 2:
                    suggested_prefix = "PROJ"

                ticket_prefix = wizard.ask_ticket_prefix(suggested_prefix)
                config["with_branching"] = True
                config["ticket_prefix"] = ticket_prefix
            else:
                # No git repo but BRANCHING selected - still enable it, still ask for prefix
                suggested_prefix = (
                    current_dir.name.upper().replace("-", "").replace("_", "")[:15]
                )
                if not suggested_prefix or len(suggested_prefix) < 2:
                    suggested_prefix = "PROJ"
                ticket_prefix = wizard.ask_ticket_prefix(suggested_prefix)
                config["with_branching"] = True
                config["ticket_prefix"] = ticket_prefix
        else:
            # BRANCHING not selected in Stage 1, ask via git workflow options
            git_options = wizard.ask_git_workflow_options(git_config, current_dir)
            config.update(git_options)
    except KeyboardInterrupt:
        return None

    # Stage 3: Capabilities Selection (granular)
    wizard.clear_screen()
    wizard.show_step_header(3, 3, "Capabilities", project_info, current_dir)
    try:
        capabilities_config = wizard.ask_capabilities_selection()
        config["capabilities_config"] = capabilities_config
        config["with_capabilities"] = capabilities_config.get("enabled", False)
        if config["with_capabilities"]:
            config["profile"] = wizard.ask_capability_profile()
    except KeyboardInterrupt:
        return None

    # Show configuration summary and get confirmation
    wizard.clear_screen()
    try:
        confirmed = wizard.show_configuration_summary(config, project_info, current_dir)
        config["confirmed"] = confirmed
    except KeyboardInterrupt:
        return None

    return config


def run_incremental_wizard(
    existing_env: Dict, project_info: Dict, git_config: Dict, current_dir: Path
) -> Optional[Dict]:
    """
    Run wizard for updating an existing Proto Gear environment.

    Args:
        existing_env: Output from detect_existing_environment()
        project_info: Project detection info
        git_config: Git configuration info
        current_dir: Current directory path

    Returns:
        Configuration dict or None if cancelled
    """
    wizard = RichWizard()
    wizard.clear_screen()

    # Print header
    if wizard.console:
        wizard.console.print("\n[bold cyan]ProtoGear Environment Update[/bold cyan]")
        wizard.console.print("[dim]" + "=" * 60 + "[/dim]\n")
        wizard.console.print(
            "[yellow]Proto Gear is already initialized in this project![/yellow]\n"
        )
    else:
        print("\nProtoGear Environment Update")
        print("=" * 60)
        print("Proto Gear is already initialized in this project!\n")

    # Show what's currently installed
    if wizard.console:
        # Create rich table showing existing files
        from rich.table import Table

        table = Table(title="Current Installation", box=box.ROUNDED)
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="green")

        # Core files (always written by init; missing == red, they should exist)
        for template in CORE_ALWAYS_FILES + ["AGENT_CONTEXT.md"]:
            status = (
                "✓ Installed"
                if template in existing_env["existing_files"]
                else "✗ Missing"
            )
            style = "green" if template in existing_env["existing_files"] else "red"
            table.add_row(template, f"[{style}]{status}[/{style}]")

        # Host-config mirrors (generated/refreshed by sync_context)
        for template in [f for f in SYNC_GENERATED_FILES if f != "AGENT_CONTEXT.md"]:
            status = (
                "✓ Installed"
                if template in existing_env["existing_files"]
                else "✗ Missing"
            )
            style = "green" if template in existing_env["existing_files"] else "red"
            table.add_row(template, f"[{style}]{status}[/{style}]")

        # Optional templates
        for template in OPTIONAL_TEMPLATE_FILES:
            status = (
                "✓ Installed"
                if template in existing_env["existing_files"]
                else "✗ Missing"
            )
            style = "green" if template in existing_env["existing_files"] else "dim"
            table.add_row(template, f"[{style}]{status}[/{style}]")

        # Capabilities
        cap_status = (
            "✓ Installed"
            if existing_env["existing_capabilities"]
            else "✗ Not installed"
        )
        cap_style = "green" if existing_env["existing_capabilities"] else "dim"
        table.add_row(
            ".proto-gear/ (capabilities)", f"[{cap_style}]{cap_status}[/{cap_style}]"
        )

        wizard.console.print(table)
        wizard.console.print()
    else:
        # Fallback text output with encoding-safe characters
        print("Current Installation:")
        print("-" * 60)
        for f in CORE_ALWAYS_FILES + SYNC_GENERATED_FILES + OPTIONAL_TEMPLATE_FILES:
            try:
                status = "✓" if f in existing_env["existing_files"] else "✗"
                print(f"  {status} {f}")
            except UnicodeEncodeError:
                status = "[x]" if f in existing_env["existing_files"] else "[ ]"
                print(f"  {status} {f}")
        try:
            cap_status = "✓" if existing_env["existing_capabilities"] else "✗"
            print(f"  {cap_status} .proto-gear/ (capabilities)")
        except UnicodeEncodeError:
            cap_status = "[x]" if existing_env["existing_capabilities"] else "[ ]"
            print(f"  {cap_status} .proto-gear/ (capabilities)")
        print()

    # Ask about project specifications document (if not already present)
    try:
        specs_source = wizard.ask_project_specifications(current_dir)
        if specs_source:
            specs_config = {"project_description": specs_source}
        else:
            specs_config = {}
    except KeyboardInterrupt:
        return None

    # Ask what to do
    if QUESTIONARY_AVAILABLE:
        action_choices = []

        # Find missing files. Only optional templates are passed to setup as
        # template *selections*; the always-written core files and the
        # sync_context-generated mirrors (AGENT_CONTEXT.md, CLAUDE.md, …) are
        # self-healed by setup_agent_framework_only regardless of selection, so
        # they only need to count toward the "something is missing" trigger.
        missing_templates = [
            t
            for t in OPTIONAL_TEMPLATE_FILES
            if t not in existing_env["existing_files"]
        ]
        missing_core = [
            t
            for t in (CORE_ALWAYS_FILES + SYNC_GENERATED_FILES)
            if t not in existing_env["existing_files"]
        ]
        total_missing = len(missing_templates) + len(missing_core)

        if total_missing:
            action_choices.append(
                {
                    "name": f"{CHARS['plus']} Add missing files ({total_missing} missing)",
                    "value": "add_missing",
                }
            )

        if not existing_env["existing_capabilities"]:
            action_choices.append(
                {
                    "name": f"{CHARS['gear']} Add capabilities system (.proto-gear/)",
                    "value": "add_capabilities",
                }
            )

        action_choices.extend(
            [
                {
                    "name": f"{CHARS['refresh']} Update all templates to latest version",
                    "value": "update_all",
                },
                {
                    "name": f"{CHARS['check']} Custom selection (choose specific items)",
                    "value": "custom",
                },
                {"name": f"{CHARS['cross']} Cancel (no changes)", "value": "cancel"},
            ]
        )

        try:
            action = questionary.select(
                "What would you like to do?",
                choices=action_choices,
                style=PROTO_GEAR_STYLE,
            ).ask()
        except KeyboardInterrupt:
            return None

        if action == "cancel" or action is None:
            return None

        # Build configuration based on action
        config = {
            "with_branching": "BRANCHING.md" in existing_env["existing_files"],
            "ticket_prefix": None,
            "with_capabilities": existing_env["existing_capabilities"],
            "capabilities_config": None,
            "with_all": False,
            "core_templates": [],
            "confirmed": True,
        }

        if action == "add_missing":
            # Add all missing templates
            config["core_templates"] = missing_templates
            if "BRANCHING.md" in missing_templates:
                config["with_branching"] = True
                # Ask for ticket prefix
                suggested_prefix = (
                    current_dir.name.upper().replace("-", "").replace("_", "")[:6]
                )
                if not suggested_prefix or len(suggested_prefix) < 2:
                    suggested_prefix = "PROJ"

                try:
                    ticket_prefix = questionary.text(
                        "Ticket prefix for branch names?",
                        default=suggested_prefix,
                        style=PROTO_GEAR_STYLE,
                    ).ask()
                    config["ticket_prefix"] = (
                        ticket_prefix if ticket_prefix else suggested_prefix
                    )
                except KeyboardInterrupt:
                    return None

        elif action == "add_capabilities":
            config["with_capabilities"] = True
            # Ask for capabilities configuration
            try:
                capabilities_config = wizard.ask_capabilities_selection()
                config["capabilities_config"] = capabilities_config
                config["with_capabilities"] = capabilities_config.get("enabled", False)
                if config["with_capabilities"]:
                    config["profile"] = wizard.ask_capability_profile()
            except KeyboardInterrupt:
                return None

        elif action == "update_all":
            # Update all existing files
            config["core_templates"] = existing_env["existing_files"]
            config["with_branching"] = "BRANCHING.md" in existing_env["existing_files"]
            # Keep existing capabilities setting

        elif action == "custom":
            # Let user choose specific templates (optional templates only; core
            # and sync-generated files are always managed by init/sync_context).
            template_choices = []
            for t in OPTIONAL_TEMPLATE_FILES:
                if t in existing_env["existing_files"]:
                    template_choices.append(
                        {"name": f"{t} (update existing)", "value": t, "checked": False}
                    )
                else:
                    template_choices.append(
                        {"name": f"{t} (add new)", "value": t, "checked": False}
                    )

            try:
                selected = questionary.checkbox(
                    "Select templates to add/update:",
                    choices=template_choices,
                    style=PROTO_GEAR_STYLE,
                ).ask()
            except KeyboardInterrupt:
                return None

            if selected is None:
                return None

            config["core_templates"] = selected
            if (
                "BRANCHING.md" in selected
                and "BRANCHING.md" not in existing_env["existing_files"]
            ):
                config["with_branching"] = True
                # Ask for ticket prefix
                suggested_prefix = (
                    current_dir.name.upper().replace("-", "").replace("_", "")[:6]
                )
                if not suggested_prefix or len(suggested_prefix) < 2:
                    suggested_prefix = "PROJ"

                try:
                    ticket_prefix = questionary.text(
                        "Ticket prefix for branch names?",
                        default=suggested_prefix,
                        style=PROTO_GEAR_STYLE,
                    ).ask()
                    config["ticket_prefix"] = (
                        ticket_prefix if ticket_prefix else suggested_prefix
                    )
                except KeyboardInterrupt:
                    return None

            # Ask about capabilities if not installed
            if not existing_env["existing_capabilities"]:
                try:
                    add_caps = questionary.confirm(
                        "Add capabilities system (.proto-gear/)?",
                        default=False,
                        style=PROTO_GEAR_STYLE,
                    ).ask()
                except KeyboardInterrupt:
                    return None

                if add_caps:
                    try:
                        capabilities_config = wizard.ask_capabilities_selection()
                        config["capabilities_config"] = capabilities_config
                        config["with_capabilities"] = capabilities_config.get(
                            "enabled", False
                        )
                        if config["with_capabilities"]:
                            config["profile"] = wizard.ask_capability_profile()
                    except KeyboardInterrupt:
                        return None

        config.update(specs_config)
        return config

    else:
        # Fallback for no questionary - simple text prompts
        print("Options:")
        print("1. Add missing templates")
        print("2. Add capabilities system")
        print("3. Update all templates")
        print("4. Cancel")

        choice = input("Choose an option [1-4]: ").strip()

        if choice == "4" or not choice:
            return None

        config = {
            "with_branching": "BRANCHING.md" in existing_env["existing_files"],
            "ticket_prefix": None,
            "with_capabilities": existing_env["existing_capabilities"],
            "capabilities_config": None,
            "with_all": False,
            "core_templates": [],
            "confirmed": True,
        }

        if choice == "1":
            # Only optional templates are passed as selections; core and
            # sync-generated files are self-healed by setup regardless.
            missing_templates = [
                t
                for t in OPTIONAL_TEMPLATE_FILES
                if t not in existing_env["existing_files"]
            ]
            config["core_templates"] = missing_templates

        elif choice == "2":
            config["with_capabilities"] = True

        elif choice == "3":
            config["core_templates"] = existing_env["existing_files"]

        config.update(specs_config)
        return config

    return config
