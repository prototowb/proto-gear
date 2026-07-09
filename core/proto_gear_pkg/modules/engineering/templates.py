"""Template generation and capability installation for Proto Gear.

The engineering-module template engine: safe file writing, BRANCHING.md
generation, host-template discovery/rendering, and .proto-gear/ capability
installation. Extracted from the proto_gear.py monolith (PROTO-042,
ADR-001 Phase A) and re-exported there for compatibility. Under ADR-001 this
is engineering-module-specific and will move to modules/engineering/ in Phase B.
"""

import os
from pathlib import Path

from proto_gear_pkg import __version__
from proto_gear_pkg.ui_helper import Colors
from proto_gear_pkg.module_core.metadata_parser import (
    MetadataParser,
    apply_conditional_content,
)
from proto_gear_pkg.paths import package_root


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
git push -u origin feature/{{{{TICKET_PREFIX}}}}-XXX-description

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
            remote_handling_section = """## Local Development (No Remote)

This project does not have a remote repository configured.

### Local Workflow
```bash
# Work on your branch
git checkout -b feature/{{TICKET_PREFIX}}-XXX-description

# When done, merge to development
git checkout {{DEV_BRANCH}}
git merge feature/{{TICKET_PREFIX}}-XXX-description

# Delete feature branch
git branch -d feature/{{TICKET_PREFIX}}-XXX-description
```

### Adding a Remote Later
If you want to add a remote repository:
```bash
git remote add origin <repository-url>
git push -u origin {{DEV_BRANCH}}
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
    template_name, project_dir, context, dry_run=False, force=False, interactive=True
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

        if result["errors"]:
            result["status"] = "partial"

    except Exception as e:
        result["status"] = "error"
        result["errors"].append(f"Unexpected error: {str(e)}")

    return result
