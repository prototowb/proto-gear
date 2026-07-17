"""``pg`` entry point: parse arguments and dispatch to the engine.

This module owns argument parsing and command dispatch only. All business
logic lives in :mod:`proto_gear_pkg.proto_gear` (the engine) and the command
handler modules (``cli_commands``, ``status_commands``, ``sync_context``,
``discovery``, ``doctor``, ``capability_index_builder``).

Engine functions are reached through the module object (``engine.foo``) rather
than direct imports so that tests patching ``proto_gear_pkg.proto_gear.foo``
still affect dispatch, and so importing this module never eagerly pulls in the
engine at definition time (avoiding an import cycle with ``proto_gear.py``,
which re-exports :func:`main`).
"""

import sys
from pathlib import Path

from .parser import build_parser


def main():
    """Main entry point for Proto Gear AI Agent Framework"""
    # Force UTF-8 on stdout/stderr so emoji and box-drawing characters
    # work under subprocess capture on Windows (default cp1252 chokes on
    # bytes like 0x9d). reconfigure() is Python 3.7+; the try/except
    # tolerates streams that don't support it (e.g. already-replaced
    # io.StringIO under some test harnesses).
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

    # Imported here (not at module top) so this module can be imported and
    # re-exported by proto_gear.py without triggering a circular import.
    from .. import proto_gear as engine
    from .. import cli_commands
    from ..modules.engineering import status_commands
    from ..ui_helper import Colors

    parser = build_parser()
    args = parser.parse_args()

    try:
        # Handle 'init' command
        if args.command == "init":
            engine.show_splash_screen()

            # Check if Proto Gear is already initialized
            current_dir = Path(".")
            existing_env = engine.detect_existing_environment(current_dir)

            # Determine if we should use interactive wizard
            # Use interactive if no flags provided (except --dry-run and --force)
            # Auto-detect when we're running under subprocess / CI / piped
            # output and skip the rich wizard. Checking both streams covers
            # `pg init` under `subprocess.run(capture_output=True)` (stdin
            # may be inherited TTY, but stdout is a pipe) as well as
            # genuine non-TTY shells.
            terminal_is_interactive = sys.stdin.isatty() and sys.stdout.isatty()
            use_interactive = (
                not args.no_interactive
                and not args.with_branching
                and args.ticket_prefix is None
                and not args.with_capabilities
                and terminal_is_interactive
            )

            if use_interactive:
                # Run interactive wizard
                try:
                    # Check if this is an incremental update (Proto Gear already initialized)
                    if (
                        existing_env["is_existing"]
                        and engine.ENHANCED_WIZARD_AVAILABLE
                        and engine.run_incremental_wizard
                    ):
                        # Run incremental wizard for updating existing environment
                        project_info = engine.detect_project_structure(current_dir)
                        git_config = engine.detect_git_config()

                        wizard_config = engine.run_incremental_wizard(
                            existing_env, project_info, git_config, current_dir
                        )

                        if wizard_config is None or not wizard_config.get("confirmed"):
                            print(
                                f"\n{Colors.YELLOW}Update cancelled by user.{Colors.ENDC}"
                            )
                            sys.exit(0)

                    # Fresh initialization - use enhanced wizard if available
                    elif (
                        engine.ENHANCED_WIZARD_AVAILABLE
                        and engine.QUESTIONARY_AVAILABLE
                    ):
                        # Get project info for enhanced wizard
                        project_info = engine.detect_project_structure(current_dir)
                        git_config = engine.detect_git_config()

                        wizard_config = engine.run_enhanced_wizard(
                            project_info, git_config, current_dir
                        )

                        if wizard_config is None or not wizard_config.get("confirmed"):
                            print(
                                f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}"
                            )
                            sys.exit(0)
                    else:
                        # Fallback to simple wizard
                        wizard_config = engine.interactive_setup_wizard()

                        if not wizard_config.get("confirmed"):
                            print(
                                f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}"
                            )
                            sys.exit(0)

                    # Run setup with wizard configuration
                    result = engine.run_simple_protogear_init(
                        dry_run=args.dry_run,
                        force=args.force if hasattr(args, "force") else False,
                        with_branching=wizard_config.get("with_branching", False),
                        ticket_prefix=wizard_config.get("ticket_prefix"),
                        with_capabilities=wizard_config.get("with_capabilities", False),
                        capabilities_config=wizard_config.get("capabilities_config"),
                        with_all=wizard_config.get("with_all", False),
                        core_templates=wizard_config.get("core_templates"),
                        project_description=wizard_config.get("project_description"),
                        profile=wizard_config.get(
                            "profile", getattr(args, "profile", "frontier")
                        ),
                        # `pg init` is a deliberate human action — opt in to
                        # updating an existing install (see setup guard).
                        allow_reinit=True,
                    )
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
                    sys.exit(0)
            else:
                # Run with CLI flags (non-interactive)
                ticket_prefix = args.ticket_prefix

                # If branching is requested but no ticket prefix was given, prompt for one
                if (
                    args.with_branching
                    and not ticket_prefix
                    and not args.no_interactive
                ):
                    current_dir = Path(".")
                    suggested_prefix = (
                        current_dir.name.upper().replace("-", "").replace("_", "")[:6]
                    )
                    if not suggested_prefix or len(suggested_prefix) < 2:
                        suggested_prefix = "PROJ"

                    print(f"\n{Colors.CYAN}🎫 Ticket Prefix Configuration{Colors.ENDC}")
                    print("-" * 30)
                    print(
                        f"Suggested prefix: {Colors.GREEN}{suggested_prefix}{Colors.ENDC}"
                    )
                    print(
                        f"{Colors.GRAY}Examples: PROJ-001, APP-042, MYAPP-123{Colors.ENDC}"
                    )

                    response = (
                        engine.safe_input(
                            f"{Colors.BOLD}Enter ticket prefix (press Enter for '{suggested_prefix}'): {Colors.ENDC}"
                        )
                        .strip()
                        .upper()
                    )

                    if response and response.isalnum() and 2 <= len(response) <= 10:
                        ticket_prefix = response
                    elif response:
                        print(
                            f"{Colors.YELLOW}Invalid prefix, using suggested: {suggested_prefix}{Colors.ENDC}"
                        )
                        ticket_prefix = suggested_prefix
                    else:
                        ticket_prefix = suggested_prefix

                    print(f"Using prefix: {Colors.GREEN}{ticket_prefix}{Colors.ENDC}")

                result = engine.run_simple_protogear_init(
                    dry_run=args.dry_run,
                    force=args.force if hasattr(args, "force") else False,
                    with_branching=args.with_branching,
                    ticket_prefix=ticket_prefix,
                    with_capabilities=args.with_capabilities,
                    with_all=args.all if hasattr(args, "all") else False,
                    profile=getattr(args, "profile", "frontier"),
                    # Explicit `pg init` invocation — opt in to reinit.
                    allow_reinit=True,
                )

            if result["status"] == "success":
                print(
                    f"\n{Colors.GREEN}ProtoGear AI Agent Framework initialized!{Colors.ENDC}"
                )
            elif result["status"] == "cancelled":
                print(
                    f"\n{Colors.YELLOW}Initialization cancelled by user.{Colors.ENDC}"
                )
            else:
                print(
                    f"\n{Colors.FAIL}Initialization failed: {result.get('error', 'Unknown error')}{Colors.ENDC}"
                )
                sys.exit(1)

            sys.exit(0)

        # Handle 'help' command
        elif args.command == "help":
            engine.show_help()
            sys.exit(0)

        # Handle 'init-surface' command (module-scoped; honours --module)
        elif args.command == "init-surface":
            sys.exit(cli_commands.cmd_module_init_surface(args))

        # Handle 'capabilities' command
        elif args.command == "capabilities":
            if args.capabilities_command == "list":
                sys.exit(cli_commands.cmd_capabilities_list(args))
            elif args.capabilities_command == "search":
                sys.exit(cli_commands.cmd_capabilities_search(args))
            elif args.capabilities_command == "show":
                sys.exit(cli_commands.cmd_capabilities_show(args))
            elif args.capabilities_command == "tree":
                sys.exit(cli_commands.cmd_capabilities_tree(args))
            elif args.capabilities_command is None:
                # Bare `pg capabilities` → interactive browse/select UI (§5.7),
                # falling back to the static list when non-interactive.
                sys.exit(cli_commands.cmd_capabilities_browse(args))
            else:
                print(
                    f"{Colors.YELLOW}Use 'pg capabilities --help' to see available commands{Colors.ENDC}"
                )
                sys.exit(1)

        # Handle 'lessons' command
        elif args.command == "lessons":
            if args.lessons_command == "list":
                sys.exit(cli_commands.cmd_lessons_list(args))
            elif args.lessons_command == "show":
                sys.exit(cli_commands.cmd_lessons_show(args))
            elif args.lessons_command is None:
                # Bare `pg lessons` → interactive browse/select UI (§5.7),
                # falling back to the static list when non-interactive.
                sys.exit(cli_commands.cmd_lessons_browse(args))
            else:
                print(
                    f"{Colors.YELLOW}Use 'pg lessons --help' to see available commands{Colors.ENDC}"
                )
                sys.exit(1)

        # Handle 'agent' command
        elif args.command == "agent":
            if args.agent_command == "create":
                sys.exit(cli_commands.cmd_agent_create(args))
            elif args.agent_command == "list":
                sys.exit(cli_commands.cmd_agent_list(args))
            elif args.agent_command == "install":
                sys.exit(cli_commands.cmd_agent_install(args))
            elif args.agent_command == "show":
                sys.exit(cli_commands.cmd_agent_show(args))
            elif args.agent_command == "validate":
                sys.exit(cli_commands.cmd_agent_validate(args))
            elif args.agent_command == "delete":
                sys.exit(cli_commands.cmd_agent_delete(args))
            elif args.agent_command == "clone":
                sys.exit(cli_commands.cmd_agent_clone(args))
            elif args.agent_command is None:
                # Bare `pg agent` → interactive browse/select UI (§5.7),
                # falling back to the static list when non-interactive.
                sys.exit(cli_commands.cmd_agent_browse(args))
            else:
                print(
                    f"{Colors.YELLOW}Use 'pg agent --help' to see available commands{Colors.ENDC}"
                )
                sys.exit(1)

        # Handle 'orchestration' command (alias: 'paradigm')
        elif args.command in ("orchestration", "paradigm"):
            if args.orchestration_command == "list":
                sys.exit(cli_commands.cmd_orchestration_list(args))
            elif args.orchestration_command == "show":
                sys.exit(cli_commands.cmd_orchestration_show(args))
            elif args.orchestration_command == "install":
                sys.exit(cli_commands.cmd_orchestration_install(args))
            elif args.orchestration_command is None:
                # Bare `pg orchestration` → interactive browse/select UI (§5.7),
                # falling back to the static list when non-interactive.
                sys.exit(cli_commands.cmd_orchestration_browse(args))
            else:
                print(
                    f"{Colors.YELLOW}Use 'pg orchestration --help' to see available commands{Colors.ENDC}"
                )
                sys.exit(1)

        # Handle 'module' command
        elif args.command == "module":
            if args.module_command == "list":
                sys.exit(cli_commands.cmd_module_list(args))
            elif args.module_command == "show":
                sys.exit(cli_commands.cmd_module_show(args))
            else:
                print(
                    f"{Colors.YELLOW}Use 'pg module --help' to see available commands{Colors.ENDC}"
                )
                sys.exit(1)

        elif args.command == "pipeline":
            sys.exit(cli_commands.cmd_pipeline(args))

        elif args.command == "trace":
            sys.exit(cli_commands.cmd_trace(args))

        elif args.command == "release":
            sys.exit(cli_commands.cmd_release(args))

        # Handle 'update' command
        elif args.command == "update":
            sys.exit(cli_commands.cmd_template_update(args))

        # Handle 'status' command
        elif args.command == "status":
            sys.exit(status_commands.cmd_status(args))

        # Handle 'ticket' command
        elif args.command == "ticket":
            if args.ticket_command == "create":
                sys.exit(status_commands.cmd_ticket_create(args))
            elif args.ticket_command == "update":
                sys.exit(status_commands.cmd_ticket_update(args))
            elif args.ticket_command == "list":
                sys.exit(status_commands.cmd_ticket_list(args))
            else:
                print("Use 'pg ticket --help' to see available commands")
                sys.exit(1)

        # Handle 'context' command
        elif args.command == "context":
            from ..module_core import sync_context as sync_context_module

            project_dir = Path(".")
            canon = project_dir / "AGENT_CONTEXT.md"
            if canon.exists() and not args.regenerate:
                content = canon.read_text(encoding="utf-8")
            else:
                content = sync_context_module.generate_agent_context(project_dir)
            # Force UTF-8 so emoji/Unicode work on Windows consoles.
            buffer = getattr(sys.stdout, "buffer", None)
            if buffer is not None:
                buffer.write(content.encode("utf-8"))
            else:
                sys.stdout.write(content)
            sys.exit(0)

        # Handle 'suggest' command
        elif args.command == "suggest":
            from ..module_core import discovery

            prose = " ".join(args.prose)
            matches = discovery.suggest(Path("."), prose, limit=args.limit)
            if args.json:
                import json

                print(json.dumps({"prose": prose, "matches": matches}, indent=2))
            else:
                if not matches:
                    print(
                        f"{Colors.YELLOW}No matching capabilities for: {prose!r}{Colors.ENDC}"
                    )
                    sys.exit(0)
                print(f"{Colors.CYAN}Top matches for {prose!r}:{Colors.ENDC}")
                for i, m in enumerate(matches, 1):
                    triggers_hit = ", ".join(f"`{t}`" for t in m["matched_triggers"])
                    print(
                        f"  {i}. {Colors.GREEN}{m['id']}{Colors.ENDC} "
                        f"(score {m['score']}) — {m['description']}"
                    )
                    if triggers_hit:
                        print(f"     {Colors.GRAY}matched: {triggers_hit}{Colors.ENDC}")
            sys.exit(0)

        # Handle 'doctor' command
        elif args.command == "doctor":
            from ..module_core import doctor as doctor_module

            project_dir = Path(".")
            report = doctor_module.run_diagnostics(project_dir)

            if args.json:
                import json

                print(json.dumps(report.to_dict(), indent=2))
                sys.exit(0 if report.errors == 0 else 1)

            visible = (
                report.findings
                if args.all
                else [f for f in report.findings if f.severity != "ok"]
            )

            if not visible:
                print(f"{Colors.GREEN}OK — no proto-gear drift detected.{Colors.ENDC}")
                print(f"{Colors.GRAY}  ({report.ok} checks passed){Colors.ENDC}")
                sys.exit(0)

            print(f"{Colors.CYAN}pg doctor — diagnostics{Colors.ENDC}")
            for f in visible:
                if f.severity == "error":
                    badge = f"{Colors.FAIL}ERROR{Colors.ENDC}"
                elif f.severity == "warning":
                    badge = f"{Colors.YELLOW}WARN {Colors.ENDC}"
                else:
                    badge = f"{Colors.GREEN}OK   {Colors.ENDC}"
                print(f"  [{badge}] {f.target}: {f.message}")
                if f.fix_hint:
                    print(f"         {Colors.GRAY}-> {f.fix_hint}{Colors.ENDC}")

            print(
                f"\n{report.errors} error(s), {report.warnings} warning(s), "
                f"{report.ok} ok"
            )

            if args.fix and doctor_module.fixable_by_sync(report):
                print(f"\n{Colors.CYAN}Running sync to repair drift...{Colors.ENDC}")
                from ..module_core import sync_context as sync_context_module
                from ..module_core import capability_index_builder

                results = sync_context_module.sync_context(project_dir, dry_run=False)
                for path_str, action in results.items():
                    print(f"  {Colors.GREEN}{action}{Colors.ENDC}: {path_str}")
                caps_root = project_dir / ".proto-gear"
                if caps_root.exists():
                    idx_results = capability_index_builder.sync_capability_indexes(
                        caps_root, dry_run=False
                    )
                    for rel, action in idx_results.items():
                        print(
                            f"  {Colors.GREEN}{action}{Colors.ENDC}: .proto-gear/{rel}"
                        )
                    from ..module_core import lessons as lessons_module

                    lessons_result = lessons_module.sync_lessons_index(
                        caps_root, dry_run=False
                    )
                    print(
                        f"  {Colors.GREEN}{lessons_result['status']}{Colors.ENDC}: "
                        f".proto-gear/lessons/INDEX.md"
                    )
                print(f"{Colors.GREEN}Re-run `pg doctor` to verify.{Colors.ENDC}")

            sys.exit(0 if report.errors == 0 else 1)

        # Handle 'sync-context' command
        elif args.command == "sync-context":
            from ..module_core import sync_context as sync_context_module
            from ..module_core import capability_index_builder

            project_dir = Path(".")
            results = sync_context_module.sync_context(
                project_dir, dry_run=args.dry_run
            )
            if "error" in results:
                print(f"{Colors.FAIL}Error: {results['error']}{Colors.ENDC}")
                sys.exit(1)
            label = "Would sync" if args.dry_run else "Synced"
            print(f"{Colors.CYAN}{label} Agent Context:{Colors.ENDC}")
            for path_str, action in results.items():
                icon = {
                    "created": "+",
                    "updated": "~",
                    "unchanged": "=",
                    "would_create": "+ (dry)",
                    "would_update": "~ (dry)",
                }.get(action, "?")
                colour = (
                    Colors.GREEN
                    if action in ("created", "updated", "would_create", "would_update")
                    else Colors.GRAY
                )
                print(f"  {colour}{icon} {path_str}{Colors.ENDC}  [{action}]")

            # Also sync capability indexes if .proto-gear/ exists
            caps_root = project_dir / ".proto-gear"
            if caps_root.exists():
                idx_results = capability_index_builder.sync_capability_indexes(
                    caps_root, dry_run=args.dry_run
                )
                if idx_results and "error" not in idx_results:
                    print(f"{Colors.CYAN}{label} Capability Indexes:{Colors.ENDC}")
                    for rel, action in idx_results.items():
                        colour = (
                            Colors.GREEN
                            if action
                            in ("created", "updated", "would_create", "would_update")
                            else Colors.GRAY
                        )
                        print(f"  {colour}.proto-gear/{rel}{Colors.ENDC}  [{action}]")

                # Also refresh the lessons index (Phase 4)
                from ..module_core import lessons as lessons_module

                lessons_result = lessons_module.sync_lessons_index(
                    caps_root, dry_run=args.dry_run
                )
                if lessons_result["status"] not in ("no-dir", "missing-markers"):
                    print(
                        f"{Colors.CYAN}{label} Lessons Index:{Colors.ENDC}\n"
                        f"  {Colors.GRAY}.proto-gear/lessons/INDEX.md{Colors.ENDC}  "
                        f"[{lessons_result['status']}]"
                    )
            sys.exit(0)

        # Handle 'sync-indexes' command
        elif args.command == "sync-indexes":
            from ..module_core import capability_index_builder

            caps_root = Path(".") / ".proto-gear"
            if not caps_root.exists():
                print(
                    f"{Colors.YELLOW}No .proto-gear/ directory in current project — "
                    f"run `pg init --with-capabilities` first.{Colors.ENDC}"
                )
                sys.exit(1)
            results = capability_index_builder.sync_capability_indexes(
                caps_root, dry_run=args.dry_run
            )
            if "error" in results:
                print(f"{Colors.FAIL}Error: {results['error']}{Colors.ENDC}")
                sys.exit(1)
            label = "Would sync" if args.dry_run else "Synced"
            print(f"{Colors.CYAN}{label} Capability Indexes:{Colors.ENDC}")
            for rel, action in results.items():
                colour = (
                    Colors.GREEN
                    if action in ("created", "updated", "would_create", "would_update")
                    else Colors.GRAY
                )
                hint = ""
                if action == "missing-markers":
                    hint = "  (no proto-gear:capability-index markers — file skipped)"
                elif action == "missing-file":
                    hint = "  (INDEX.md not present)"
                print(f"  {colour}.proto-gear/{rel}{Colors.ENDC}  [{action}]{hint}")
            sys.exit(0)

        # Handle 'guard' command — enforce a repo invariant (for hooks/CI).
        elif args.command == "guard":
            from ..module_core import guard as guard_module

            aspect = getattr(args, "aspect", "branch") or "branch"
            if aspect == "branch":
                result = guard_module.check_protected_branch(
                    protected=getattr(args, "protected", None)
                )
                colour = Colors.GREEN if result.ok else Colors.FAIL
                icon = "OK" if result.ok else "BLOCKED"
                print(f"{colour}[{icon}]{Colors.ENDC} {result.message}")
                sys.exit(result.exit_code)
            print(f"{Colors.FAIL}Unknown guard aspect: {aspect}{Colors.ENDC}")
            sys.exit(2)

        # Handle 'hooks' command — install the branch-guard pre-commit hook.
        elif args.command == "hooks":
            from ..module_core import hooks as hooks_module

            if getattr(args, "hooks_command", None) != "install":
                print(f"{Colors.YELLOW}Usage: pg hooks install [--force]{Colors.ENDC}")
                sys.exit(2)

            result = hooks_module.install_pre_commit(
                cwd=".", force=getattr(args, "force", False)
            )
            status = result["status"]
            if status in ("installed", "overwritten"):
                print(
                    f"{Colors.GREEN}+ Branch-guard pre-commit hook installed{Colors.ENDC} "
                    f"({result['path']})"
                )
                if status == "overwritten":
                    print(
                        f"{Colors.GRAY}  Previous hook backed up to "
                        f"pre-commit.pre-guard.bak{Colors.ENDC}"
                    )
                sys.exit(0)
            elif status == "already-present":
                print(
                    f"{Colors.GRAY}Branch-guard hook already installed "
                    f"({result['path']}).{Colors.ENDC}"
                )
                sys.exit(0)
            elif status == "exists-different":
                print(
                    f"{Colors.YELLOW}A pre-commit hook already exists "
                    f"({result['path']}).{Colors.ENDC}\n"
                    f"{Colors.GRAY}  Add `pg guard branch || exit 1` near its top, "
                    f"or run `pg hooks install --force` to replace it (a backup is "
                    f"kept).{Colors.ENDC}"
                )
                sys.exit(1)
            else:  # not-a-repo
                print(
                    f"{Colors.YELLOW}Not a git repository — nothing to install."
                    f"{Colors.ENDC}"
                )
                sys.exit(1)

        # No command provided - show help
        else:
            # Bare `pg`: in an interactive terminal with questionary, open the
            # top-level home menu (§5.7, UI-first). Otherwise keep the classic
            # splash + command list so pipes/CI/scripts are unaffected.
            interactive = sys.stdin.isatty() and sys.stdout.isatty()
            try:
                import questionary  # noqa: F401

                has_questionary = True
            except Exception:
                has_questionary = False

            if interactive and has_questionary:
                sys.exit(cli_commands.cmd_home_menu(args))

            engine.show_splash_screen()
            print(
                f"{Colors.GREEN}Welcome to Proto Gear AI Agent Framework!{Colors.ENDC}"
            )
            print(
                f"{Colors.GRAY}Template generator for AI-powered development collaboration{Colors.ENDC}\n"
            )
            print(f"{Colors.CYAN}Available Commands:{Colors.ENDC}")
            print(
                f"  {Colors.BOLD}pg init{Colors.ENDC}              - Initialize AI agent templates in your project"
            )
            print(
                f"  {Colors.BOLD}pg status{Colors.ENDC}            - Show project status from PROJECT_STATUS.md"
            )
            print(
                f"  {Colors.BOLD}pg ticket{Colors.ENDC}            - Manage tickets  (create / update / list)"
            )
            print(
                f"  {Colors.BOLD}pg capabilities{Colors.ENDC}      - Browse and search available capabilities"
            )
            print(
                f"  {Colors.BOLD}pg agent{Colors.ENDC}             - Manage agent configurations"
            )
            print(
                f"  {Colors.BOLD}pg orchestration{Colors.ENDC}     - Browse orchestration paradigms"
            )
            print(
                f"  {Colors.BOLD}pg help{Colors.ENDC}              - Show detailed documentation"
            )
            print(f"\n{Colors.GRAY}Run 'pg --help' for more options{Colors.ENDC}\n")
            engine.print_farewell()

    except KeyboardInterrupt:
        engine.print_farewell()
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.FAIL}An unexpected error occurred: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please report this issue on GitHub.{Colors.ENDC}")
        sys.exit(1)
