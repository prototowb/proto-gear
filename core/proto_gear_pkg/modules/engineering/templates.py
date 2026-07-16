"""Template generation and capability installation for Proto Gear.

The engineering-module template engine: safe file writing, BRANCHING.md
generation, host-template discovery/rendering, and .proto-gear/ capability
installation. Extracted from the proto_gear.py monolith (PROTO-042,
ADR-001 Phase A) and re-exported there for compatibility. Under ADR-001 this
is engineering-module-specific and will move to modules/engineering/ in Phase B.
"""

import os
import re
from datetime import datetime
from pathlib import Path

from proto_gear_pkg import __version__
from proto_gear_pkg.ui_helper import Colors
from proto_gear_pkg.module_core.metadata_parser import (
    MetadataParser,
    apply_conditional_content,
)
from proto_gear_pkg.module_core import capability_profile
from proto_gear_pkg.paths import package_root

# ---------------------------------------------------------------------------
# Defaulted replacement dictionary (PROTO-078)
#
# Host templates carry far more placeholders than the wizard ever asked about.
# Historically only the interactive path filled a handful (PROJECT_NAME,
# TICKET_PREFIX, DATE, ...), so `pg init --no-interactive` shipped files with
# raw `{{TOKEN}}` leakage and `--ticket-prefix` silently ignored. This builds
# the single defaulted replacement dict that *every* init path applies, keyed
# off project/git detection and honoring the caller's flags. Deep content
# scaffold slots (ARCHITECTURE diagrams, SECURITY threat scenarios) are
# intentionally NOT defaulted here — agents fill those in.
# ---------------------------------------------------------------------------

# Per-language tooling defaults for the command/coverage/source tokens.
# Detection yields a coarse "<Lang> Project" type string; we key off the
# language word and fall back to language-neutral `make`-style commands.
_LANGUAGE_PROFILES = {
    "python": {
        "LANGUAGE": "Python",
        "LANGUAGE_VERSION": "python-version",
        "SETUP_ACTION": "actions/setup-python@v5",
        "TEST_FRAMEWORK": "pytest",
        "TEST_COMMAND": "pytest",
        "RUN_ALL_TESTS": "pytest",
        "RUN_UNIT_TESTS": "pytest tests/unit",
        "RUN_INTEGRATION_TESTS": "pytest tests/integration",
        "RUN_SPECIFIC_TESTS": "pytest tests/unit/test_module.py",
        "RUN_WATCH_MODE": "pytest-watch",
        "RUN_WITH_COVERAGE": "pytest --cov",
        "RUN_COVERAGE": "pytest --cov --cov-report=html",
        "LINTER_COMMAND": "ruff check .",
        "RUN_LINTER": "ruff check .",
        "TYPE_CHECKER_COMMAND": "mypy .",
        "FORMAT_COMMAND": "black .",
        "AUTO_FIX_COMMAND": "ruff check --fix .",
        "VERIFY_COMMAND": "pytest && ruff check . && mypy .",
        "INSTALL_COMMAND": "pip install -e .[dev]",
        "SOURCE_DIR": "src",
    },
    "node": {
        "LANGUAGE": "JavaScript/TypeScript",
        "LANGUAGE_VERSION": "node-version",
        "SETUP_ACTION": "actions/setup-node@v4",
        "TEST_FRAMEWORK": "Jest",
        "TEST_COMMAND": "npm test",
        "RUN_ALL_TESTS": "npm test",
        "RUN_UNIT_TESTS": "npm run test:unit",
        "RUN_INTEGRATION_TESTS": "npm run test:integration",
        "RUN_SPECIFIC_TESTS": "npm test -- src/module.test.js",
        "RUN_WATCH_MODE": "npm test -- --watch",
        "RUN_WITH_COVERAGE": "npm test -- --coverage",
        "RUN_COVERAGE": "npm test -- --coverage",
        "LINTER_COMMAND": "npm run lint",
        "RUN_LINTER": "npm run lint",
        "TYPE_CHECKER_COMMAND": "npx tsc --noEmit",
        "FORMAT_COMMAND": "npm run format",
        "AUTO_FIX_COMMAND": "npm run lint -- --fix",
        "VERIFY_COMMAND": "npm test && npm run lint",
        "INSTALL_COMMAND": "npm install",
        "SOURCE_DIR": "src",
    },
    "generic": {
        "LANGUAGE": "your language",
        "LANGUAGE_VERSION": "language-version",
        "SETUP_ACTION": "actions/checkout@v4",
        "TEST_FRAMEWORK": "your test framework",
        "TEST_COMMAND": "make test",
        "RUN_ALL_TESTS": "make test",
        "RUN_UNIT_TESTS": "make test-unit",
        "RUN_INTEGRATION_TESTS": "make test-integration",
        "RUN_SPECIFIC_TESTS": "make test TEST=module",
        "RUN_WATCH_MODE": "make test-watch",
        "RUN_WITH_COVERAGE": "make coverage",
        "RUN_COVERAGE": "make coverage",
        "LINTER_COMMAND": "make lint",
        "RUN_LINTER": "make lint",
        "TYPE_CHECKER_COMMAND": "make typecheck",
        "FORMAT_COMMAND": "make format",
        "AUTO_FIX_COMMAND": "make lint-fix",
        "VERIFY_COMMAND": "make verify",
        "INSTALL_COMMAND": "make install",
        "SOURCE_DIR": "src",
    },
}


def _language_key(project_info: dict) -> str:
    """Map a detected project type string to a `_LANGUAGE_PROFILES` key."""
    ptype = (project_info or {}).get("type") or ""
    ptype = ptype.lower()
    if "python" in ptype:
        return "python"
    if "node" in ptype or "javascript" in ptype or "typescript" in ptype:
        return "node"
    return "generic"


def build_default_replacements(
    project_dir: Path,
    ticket_prefix: str = None,
    git_config: dict = None,
    project_info: dict = None,
) -> dict:
    """Build the defaulted replacement dict shared by every init path.

    Covers the project-config token surface (branch names, ticket prefix,
    dates, language/test/lint/coverage commands, repository URL, review/SLA
    times) with sensible, detection-aware defaults. Callers merge per-file
    extras on top. Genuinely open-ended content slots are left untouched for
    agents to fill (see `humanize_leftover_tokens` for the clean-file sweep).
    """
    project_dir = Path(project_dir)
    project_info = project_info or {}
    git_config = git_config or {}

    # Path(".").name is "" — always resolve so the project name is real.
    project_name = project_dir.resolve().name
    today = datetime.now().strftime("%Y-%m-%d")
    year = datetime.now().strftime("%Y")

    main_branch = git_config.get("main_branch", "main")
    dev_branch = git_config.get("dev_branch", "development")

    lang = dict(_LANGUAGE_PROFILES[_language_key(project_info)])

    repo_url = (
        git_config.get("remote_url") or f"https://github.com/OWNER/{project_name}"
    )

    replacements = {
        # Identity / meta
        "PROJECT_NAME": project_name,
        "PROJECT_ROOT": project_name,
        "TICKET_PREFIX": ticket_prefix or "PROJ",
        "VERSION": __version__,
        "YEAR": year,
        "DATE": today,
        "GENERATION_DATE": today,
        "PROJECT_TYPE": project_info.get("type", "Unknown"),
        "FRAMEWORK": project_info.get("framework", "Unknown"),
        "CODE_LANGUAGE": lang["LANGUAGE"],
        # Git / branches
        "MAIN_BRANCH": main_branch,
        "DEV_BRANCH": dev_branch,
        "CURRENT_BRANCH": main_branch,
        "REPOSITORY_URL": repo_url,
        # Coverage targets
        "COVERAGE_TARGET": "80",
        "MIN_COVERAGE": "80",
        "NEW_CODE_COVERAGE": "90",
        # Sprint cadence (AGENTS.md)
        "SPRINT_DURATION": "2 weeks",
        # Illustrative example fillers so shipped code samples read naturally
        "MODULE_NAME": "example",
        "module": "example",
        "WORKFLOW_NAME": "checkout",
        "workflow": "checkout",
        "WORKFLOW": "the checkout workflow",
        "FEATURE_NAME": "user login",
        "USER_JOURNEY": "the sign-up flow",
        "ACTION": "complete the primary flow",
        "ERROR_CONDITION": "invalid input gracefully",
        "EDGE_CASE_DESCRIPTION": "empty and boundary inputs are handled",
        "BASE_URL": "http://localhost:8000",
        # Review / response SLAs (CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md)
        "SECURITY_CONTACT": "the project maintainers",
        "ACKNOWLEDGMENT_TIME": "48 hours",
        "INITIAL_RESPONSE_TIME": "48 hours",
        "ASSESSMENT_TIME": "5 business days",
        "RESOLUTION_TIME": "30 days",
        "RESOLUTION_TARGET": "30 days",
        "ISSUE_RESPONSE_TIME": "2 business days",
        "PR_RESPONSE_TIME": "2 business days",
        "QUESTION_RESPONSE_TIME": "2 business days",
        "REVIEW_TURNAROUND": "2 business days",
        "CRITICAL_RESPONSE_TIME": "24 hours",
        "HIGH_RESPONSE_TIME": "48 hours",
        "MEDIUM_RESPONSE_TIME": "5 business days",
        "LOW_RESPONSE_TIME": "10 business days",
        "CRITICAL_FIX_TIME": "7 days",
        "HIGH_FIX_TIME": "30 days",
        "MEDIUM_FIX_TIME": "90 days",
        "LOW_FIX_TIME": "best effort",
    }
    replacements.update(lang)
    return replacements


# Matches a single `{{TOKEN}}` placeholder (letters/underscores only, so
# doubled `{{{{...}}}}` literals in code samples are left alone).
_LEFTOVER_TOKEN_RE = re.compile(r"(?<!\{)\{\{([A-Za-z_]+)\}\}(?!\})")


def humanize_leftover_tokens(content: str) -> str:
    """Replace any surviving `{{TOKEN}}` with a friendly `_TBD: token_` marker.

    Applied only to files that must ship leakage-free (AGENTS, PROJECT_STATUS,
    TESTING, CONTRIBUTING) as a safety net for config tokens without an
    explicit default. Scaffold files (ARCHITECTURE/SECURITY) are not swept.
    """

    def _repl(match: "re.Match") -> str:
        words = match.group(1).replace("_", " ").strip().lower()
        return f"_TBD: {words}_"

    return _LEFTOVER_TOKEN_RE.sub(_repl, content)


def safe_write_file(
    file_path: Path,
    content: str,
    dry_run: bool = False,
    force: bool = False,
    interactive: bool = True,
) -> tuple:
    """
    Safely write a file with existence checking and user prompts.

    Args:
        file_path: Path to file to write
        content: Content to write
        dry_run: If True, don't actually write files
        force: If True, overwrite without prompting
        interactive: If True and file exists, prompt user for action

    Returns:
        tuple: (action_taken: str, file_written: bool)
        action_taken can be: 'created', 'overwritten', 'skipped', 'backed_up'
    """
    if dry_run:
        return ("would_create", False)

    if not file_path.exists():
        file_path.write_text(content, encoding="utf-8")
        return ("created", True)

    # File exists - check what to do
    if force:
        file_path.write_text(content, encoding="utf-8")
        return ("overwritten", True)

    if not interactive:
        # Non-interactive mode: skip existing files by default
        return ("skipped", False)

    # Interactive mode: prompt user
    print(f"\n{Colors.YELLOW}File exists: {file_path.name}{Colors.ENDC}")
    print(f"{Colors.CYAN}Options:{Colors.ENDC}")
    print(f"  1. Overwrite (replace existing file)")
    print(f"  2. Skip (keep existing file)")
    print(f"  3. Backup (save as .bak and create new)")
    print(f"  4. View diff (show what would change)")

    while True:
        choice = input(f"{Colors.GREEN}Choose [1/2/3/4]: {Colors.ENDC}").strip()

        if choice == "1":
            file_path.write_text(content, encoding="utf-8")
            return ("overwritten", True)
        elif choice == "2":
            return ("skipped", False)
        elif choice == "3":
            # Create backup
            backup_path = file_path.with_suffix(".md.bak")
            backup_path.write_text(
                file_path.read_text(encoding="utf-8"), encoding="utf-8"
            )
            file_path.write_text(content, encoding="utf-8")
            print(f"{Colors.GREEN}✓ Backup created: {backup_path.name}{Colors.ENDC}")
            return ("backed_up", True)
        elif choice == "4":
            # Show diff
            print(f"\n{Colors.CYAN}=== Current Content ==={Colors.ENDC}")
            print(file_path.read_text(encoding="utf-8")[:500])
            print(f"{Colors.CYAN}=== New Content ==={Colors.ENDC}")
            print(content[:500])
            print(
                f"{Colors.YELLOW}(showing first 500 characters of each){Colors.ENDC}\n"
            )
            # Ask again
            continue
        else:
            print(
                f"{Colors.FAIL}Invalid choice. Please enter 1, 2, 3, or 4.{Colors.ENDC}"
            )


def generate_branching_doc(project_name, ticket_prefix, git_config, generation_date):
    """Generate BRANCHING.md from template"""
    template_path = package_root() / "BRANCHING.template.md"

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding="utf-8")

        # Generate workflow mode description
        workflow_mode_descriptions = {
            "no_git": "**No Git Repository** - Consider initializing Git for version control",
            "local_only": "**Local-Only Workflow** - No remote repository configured",
            "remote_manual": "**Remote Workflow (Manual PRs)** - Remote configured, GitHub CLI not detected",
            "remote_automated": "**Remote Workflow (Automated)** - Remote configured, GitHub CLI available",
        }

        workflow_mode_desc = workflow_mode_descriptions.get(
            git_config.get("workflow_mode", "local_only"), "Local-Only Workflow"
        )

        # Add workflow recommendations based on mode
        workflow_recommendations = ""
        if git_config.get("workflow_mode") == "remote_manual":
            workflow_recommendations = f"""
> **💡 Tip**: GitHub CLI (`gh`) is not detected. You can:
> - Install `gh` CLI for automated PR creation: https://cli.github.com
> - Continue using manual PR creation via web interface
> - Use local merges if you prefer
"""
        elif git_config.get("workflow_mode") == "remote_automated":
            workflow_recommendations = f"""
> **✅ GitHub CLI detected**: You can create PRs automatically with `gh pr create`
"""
        elif git_config.get("workflow_mode") == "local_only":
            workflow_recommendations = f"""
> **💡 Tip**: No remote repository detected. You can:
> - Continue with local-only development
> - Add a remote later with: `git remote add origin <url>`
"""

        # Determine values based on Git configuration
        dev = git_config["dev_branch"]
        main = git_config["main_branch"]
        if git_config["has_remote"]:
            remote_requires_pr = "\n- **Pull Requests**: Required for merging"
            remote_requires_tests = " and pass tests"
            remote_via_pr = " (via pull request)"
            remote_origin = f" origin"
            if_remote = ""
            push_dev_info = (
                f"\n- **Push**: `git push origin {dev}` after each feature merge"
            )
            remote_push_during = f"4. **Push to remote**: `git push -u origin your-branch-name` (enables backup)"
            example_post_merge = (
                f"git push origin {dev}\n\n"
                f"# Open a PR on GitHub: {dev} → {main}\n"
                f"# Never merge {main} locally — the PR merge on GitHub is the only path\n"
            )
            before_merge_steps = (
                f"\n4. **Merge to `{dev}`**: `git checkout {dev} && git merge feature-branch`"
                f"\n5. **Push development**: `git push origin {dev}`"
                f"\n6. **Ship to main**: Open a PR on GitHub from `{dev}` → `{main}`; merge there — never locally"
            )
            remote_handling_section = f"""## Working with Remote Repository

This project has a remote repository configured ({git_config['remote_name']}).

### Push Regularly
```bash
# Push your branch to backup work
git push -u origin feature/{ticket_prefix}-XXX-description

# Check remote status
git branch -vv
```

### Creating Pull Requests
1. Merge feature branch to `{dev}` locally
2. Push `{dev}` to remote: `git push origin {dev}`
3. Open a PR on GitHub from `{dev}` → `{main}`
4. Merge after approval — never merge `{main}` locally"""
            quick_remote_rules = (
                f"✅ Push origin {dev} after merging a feature branch\n"
                f"✅ Merge {dev} → {main} via PR on GitHub only\n"
            )
            quick_never_remote = (
                f"❌ Merge {main} locally (not even fast-forward)\n"
                f"❌ Force-push to {main} or {dev}\n"
            )
            ticket_tracking = "GitHub Issues or PROJECT_STATUS.md"
        else:
            # Local-only development
            remote_requires_pr = ""
            remote_requires_tests = ""
            remote_via_pr = ""
            remote_origin = ""
            if_remote = " (if remote configured)"
            push_dev_info = ""
            remote_push_during = ""
            example_post_merge = ""
            before_merge_steps = f"\n4. **Merge locally**: `git checkout {dev} && git merge feature-branch`"
            remote_handling_section = f"""## Local Development (No Remote)

This project does not have a remote repository configured.

### Local Workflow
```bash
# Work on your branch
git checkout -b feature/{ticket_prefix}-XXX-description

# When done, merge to development
git checkout {dev}
git merge feature/{ticket_prefix}-XXX-description

# Delete feature branch
git branch -d feature/{ticket_prefix}-XXX-description
```

### Adding a Remote Later
If you want to add a remote repository:
```bash
git remote add origin <repository-url>
git push -u origin {dev}
```"""
            quick_remote_rules = ""
            quick_never_remote = ""
            ticket_tracking = "PROJECT_STATUS.md"

        # Replace all placeholders
        content = template.replace("{{PROJECT_NAME}}", project_name)
        content = content.replace("{{VERSION}}", __version__)
        content = content.replace("{{TICKET_PREFIX}}", ticket_prefix)
        content = content.replace("{{MAIN_BRANCH}}", main)
        content = content.replace("{{DEV_BRANCH}}", dev)
        content = content.replace("{{GENERATION_DATE}}", generation_date)
        content = content.replace("{{WORKFLOW_MODE}}", workflow_mode_desc)
        content = content.replace(
            "{{WORKFLOW_RECOMMENDATIONS}}", workflow_recommendations
        )
        content = content.replace("{{REMOTE_REQUIRES_PR}}", remote_requires_pr)
        content = content.replace("{{REMOTE_REQUIRES_TESTS}}", remote_requires_tests)
        content = content.replace("{{REMOTE_VIA_PR}}", remote_via_pr)
        content = content.replace("{{REMOTE_ORIGIN}}", remote_origin)
        content = content.replace("{{IF_REMOTE}}", if_remote)
        content = content.replace("{{PUSH_DEV_INFO}}", push_dev_info)
        content = content.replace("{{REMOTE_PUSH_DURING}}", remote_push_during)
        content = content.replace("{{EXAMPLE_POST_MERGE}}", example_post_merge)
        content = content.replace("{{BEFORE_MERGE_STEPS}}", before_merge_steps)
        content = content.replace(
            "{{REMOTE_HANDLING_SECTION}}", remote_handling_section
        )
        content = content.replace("{{QUICK_REMOTE_RULES}}", quick_remote_rules)
        content = content.replace("{{QUICK_NEVER_REMOTE}}", quick_never_remote)
        content = content.replace("{{TICKET_TRACKING}}", ticket_tracking)

        return content
    except Exception as e:
        print(f"Error generating branching doc: {e}")
        return None


def discover_available_templates():
    """
    Auto-discover all template files in the package (v0.6.0 feature).

    Returns:
        Dict mapping template names to template info
    """
    template_dir = package_root()
    templates = {}

    try:
        for template_file in template_dir.glob("*.template.md"):
            # Extract template name (e.g., "TESTING.template.md" -> "TESTING")
            name = template_file.stem.replace(".template", "")

            templates[name] = {
                "path": template_file,
                "name": name,
                "filename": f"{name}.md",
            }
    except Exception as e:
        print(f"Error discovering templates: {e}")

    return templates


def generate_project_template(
    template_name,
    project_dir,
    context,
    dry_run=False,
    force=False,
    interactive=True,
    humanize_leftovers=False,
):
    """
    Generate a project template from the template file with metadata support.

    Args:
        template_name: Name of the template (e.g., 'TESTING', 'CONTRIBUTING')
        project_dir: Path to project directory
        context: Dictionary with placeholder values
        dry_run: If True, don't actually write files
        force: If True, overwrite existing files without prompting
        interactive: If True, prompt for overwrite decisions (unless force=True)

    Returns:
        tuple: (Path to created file or None if failed, action_taken: str)
    """
    try:
        # Get template file from package
        template_file = package_root() / f"{template_name}.template.md"

        if not template_file.exists():
            print(f"Warning: Template {template_name}.template.md not found")
            return None

        # Read template content
        full_content = template_file.read_text(encoding="utf-8")

        # Parse metadata from template
        metadata, content = MetadataParser.parse_template(full_content)

        # Check if template requirements are met (if metadata exists)
        if metadata.name:  # Has metadata
            project_info = {
                "project_type": context.get("PROJECT_TYPE", "Any"),
                "framework": context.get("FRAMEWORK", "Unknown"),
            }

            if not metadata.meets_requirements(project_info):
                print(
                    f"Info: Template {template_name} requirements not met for this project type"
                )
                # Still generate, but user should know

            # Get conditional content sections
            conditional_sections = metadata.get_conditional_content(project_info)

            # Apply conditional content to template
            if conditional_sections:
                content = apply_conditional_content(content, conditional_sections)

        # Replace placeholders
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            content = content.replace(placeholder, str(value))

        # For files that must ship leakage-free, turn any config token we
        # forgot to default into a friendly fill-in marker (PROTO-078).
        if humanize_leftovers:
            content = humanize_leftover_tokens(content)

        # Write to project directory
        output_file = project_dir / f"{template_name}.md"
        action, written = safe_write_file(
            output_file, content, dry_run=dry_run, force=force, interactive=interactive
        )

        if written or action == "would_create":
            return (output_file, action)
        else:
            return (None, action)

    except Exception as e:
        print(f"Error generating {template_name}: {e}")
        return (None, "error")


def copy_capability_templates(
    target_dir: Path,
    project_name: str,
    version: str = None,
    dry_run: bool = False,
    capabilities_config: dict = None,
    profile: str = "verbose",
) -> dict:
    """
    Copy capability templates to .proto-gear/ directory with security hardening

    Args:
        target_dir: Project directory (where .proto-gear/ will be created)
        project_name: Project name for placeholder replacement
        version: Proto Gear version for placeholder replacement
        dry_run: If True, don't create files, just report what would be done
        capabilities_config: Dict with granular capability selection (skills, workflows, commands)
                            If None, includes all capabilities
        profile: Output profile — "verbose" (full methodology bodies, the default
                 for library callers) or "frontier" (slim stubs generated from
                 metadata; the methodology is omitted for capable models). See
                 module_core.capability_profile.

    Returns:
        dict with 'status', 'files_created', 'errors'

    Security Features:
        - Path traversal prevention via normpath validation
        - Symlink detection and rejection
        - UTF-8 encoding enforcement
        - File permission management
    """
    import stat

    # Use package version if not specified
    if version is None:
        version = __version__

    profile = capability_profile.normalize_profile(profile)

    result = {"status": "success", "files_created": [], "errors": []}

    # Define source and destination
    source_dir = package_root() / "capabilities"
    dest_dir = target_dir / ".proto-gear"

    # Parse capabilities config (default to all if not specified)
    if capabilities_config is None:
        capabilities_config = {"skills": True, "workflows": True, "commands": True}

    include_skills = capabilities_config.get("skills", True)
    include_workflows = capabilities_config.get("workflows", True)
    include_commands = capabilities_config.get("commands", True)

    # Security check: Ensure source directory exists and is not a symlink
    if not source_dir.exists():
        result["status"] = "error"
        result["errors"].append(f"Source directory not found: {source_dir}")
        return result

    if source_dir.is_symlink():
        result["status"] = "error"
        result["errors"].append(
            f"Security: Source directory is a symlink: {source_dir}"
        )
        return result

    # Check if .proto-gear already exists
    if dest_dir.exists() and not dry_run:
        result["status"] = "warning"
        result["errors"].append(f".proto-gear directory already exists at {dest_dir}")
        return result

    if dry_run:
        print(
            f"\n{Colors.YELLOW}Dry run - capability files that would be created:{Colors.ENDC}"
        )
        print(f"  Directory: .proto-gear/")

    try:
        # Walk through source directory
        for source_path in source_dir.rglob("*"):
            # Skip directories and symlinks
            if source_path.is_dir():
                continue

            # Security check: Reject symlinks
            if source_path.is_symlink():
                result["errors"].append(f"Skipped symlink: {source_path}")
                continue

            # Calculate relative path from source directory
            rel_path = source_path.relative_to(source_dir)

            # Granular filtering based on capabilities_config
            path_parts = rel_path.parts
            if len(path_parts) > 0:
                category = path_parts[
                    0
                ]  # skills, workflows, commands, agents, or root INDEX.md

                # Skip based on configuration
                if category == "skills" and not include_skills:
                    continue
                elif category == "workflows" and not include_workflows:
                    continue
                elif category == "commands" and not include_commands:
                    continue
                # Always include 'agents' folder (just INDEX.md) and root INDEX.md

            # Security check: Validate path doesn't contain traversal attempts
            normalized_rel_path = Path(os.path.normpath(rel_path))
            if ".." in normalized_rel_path.parts or normalized_rel_path.is_absolute():
                result["errors"].append(f"Security: Invalid path detected: {rel_path}")
                continue

            # Determine destination path
            dest_path = dest_dir / normalized_rel_path

            # Handle .template.md extension (rename to .md)
            if dest_path.suffix == ".md" and dest_path.stem.endswith(".template"):
                dest_path = dest_path.parent / (
                    dest_path.stem.replace(".template", "") + ".md"
                )

            # Security check: Ensure destination stays within .proto-gear/
            try:
                dest_path.resolve().relative_to(dest_dir.resolve())
            except ValueError:
                result["errors"].append(
                    f"Security: Destination path escapes .proto-gear/: {dest_path}"
                )
                continue

            if dry_run:
                print(f"    - {dest_path.relative_to(target_dir)}")
                result["files_created"].append(str(dest_path.relative_to(target_dir)))
            else:
                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Set directory permissions (755)
                try:
                    dest_path.parent.chmod(
                        stat.S_IRWXU
                        | stat.S_IRGRP
                        | stat.S_IXGRP
                        | stat.S_IROTH
                        | stat.S_IXOTH
                    )
                except (OSError, NotImplementedError):
                    # Some platforms don't support chmod
                    pass

                # Frontier profile: ship a slim stub for capability bodies instead
                # of the full methodology doc. Metadata/INDEX files still copy
                # verbatim so routing + `pg suggest` keep working.
                stub = None
                if profile == "frontier" and capability_profile.is_capability_body(
                    rel_path
                ):
                    stub = capability_profile.frontier_stub_for_capability(source_path)

                if stub is not None:
                    content = stub
                else:
                    # Read source file with UTF-8 encoding
                    try:
                        content = source_path.read_text(encoding="utf-8")
                    except UnicodeDecodeError as e:
                        result["errors"].append(f"Encoding error in {source_path}: {e}")
                        continue

                # Replace placeholders
                content = content.replace("{{VERSION}}", version)
                content = content.replace("{{PROJECT_NAME}}", project_name)

                # Write to destination with UTF-8 encoding
                dest_path.write_text(content, encoding="utf-8")

                # Set file permissions (644)
                try:
                    dest_path.chmod(
                        stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
                    )
                except (OSError, NotImplementedError):
                    # Some platforms don't support chmod
                    pass

                result["files_created"].append(str(dest_path.relative_to(target_dir)))

        # Install each discipline's own capabilities under .proto-gear/<module>/
        # (seam S1, on-disk). Generic: a new module is picked up with no edit
        # here. Shared/engineering caps stay flat at the root above.
        from proto_gear_pkg.module_core import module_host

        module_result = module_host.install_module_capabilities(
            dest_dir,
            replacements={"VERSION": version, "PROJECT_NAME": project_name},
            dry_run=dry_run,
            profile=profile,
        )
        result["files_created"].extend(module_result["files_created"])
        result["errors"].extend(module_result["errors"])

        if dry_run:
            for rel in module_result["files_created"]:
                print(f"    - {rel}")

        # Install each discipline's own agents into .proto-gear/agents/ (seam S1,
        # agent side). Shared agents ride the recursive sweep above; this adds
        # modules/<name>/agents/. Generic: a new module is picked up with no edit.
        agent_result = module_host.install_module_agents(
            dest_dir,
            replacements={"VERSION": version, "PROJECT_NAME": project_name},
            dry_run=dry_run,
        )
        result["files_created"].extend(agent_result["files_created"])
        result["errors"].extend(agent_result["errors"])

        if dry_run:
            for rel in agent_result["files_created"]:
                print(f"    - {rel}")

        # Record the chosen profile so `pg`/doctor and re-runs can see it.
        if not dry_run:
            try:
                (dest_dir / "PROFILE").write_text(profile + "\n", encoding="utf-8")
                result["files_created"].append(
                    str((dest_dir / "PROFILE").relative_to(target_dir))
                )
            except OSError as e:
                result["errors"].append(f"Could not record profile: {e}")
        result["profile"] = profile

        if result["errors"]:
            result["status"] = "partial"

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Unexpected error: {str(e)}")

    return result
