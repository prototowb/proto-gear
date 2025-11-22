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

# Import version from package
from . import __version__

# Import UI helper for consistent terminal output
from .ui_helper import UIHelper, Colors
ui = UIHelper()

# Import metadata parser for template frontmatter support
from .metadata_parser import MetadataParser, apply_conditional_content
# Try to import enhanced wizard module
try:
    from .interactive_wizard import run_enhanced_wizard, run_incremental_wizard, QUESTIONARY_AVAILABLE, RICH_AVAILABLE
    ENHANCED_WIZARD_AVAILABLE = True
except ImportError:
    ENHANCED_WIZARD_AVAILABLE = False
    QUESTIONARY_AVAILABLE = False
    RICH_AVAILABLE = False
    run_incremental_wizard = None

# File handling helpers
def detect_existing_environment(project_dir: Path) -> dict:
    """
    Detect if Proto Gear files already exist in the project.

    Returns dict with:
    - is_existing: bool - True if any Proto Gear files exist
    - existing_files: list - List of existing Proto Gear files
    - existing_capabilities: bool - True if .proto-gear/ directory exists
    """
    proto_gear_files = ['AGENTS.md', 'PROJECT_STATUS.md', 'BRANCHING.md', 'TESTING.md',
                        'CONTRIBUTING.md', 'SECURITY.md', 'ARCHITECTURE.md', 'CODE_OF_CONDUCT.md']

    existing_files = []
    for filename in proto_gear_files:
        if (project_dir / filename).exists():
            existing_files.append(filename)

    capabilities_dir = project_dir / '.proto-gear'

    return {
        'is_existing': len(existing_files) > 0 or capabilities_dir.exists(),
        'existing_files': existing_files,
        'existing_capabilities': capabilities_dir.exists()
    }


def safe_write_file(file_path: Path, content: str, dry_run: bool = False, force: bool = False, interactive: bool = True) -> tuple:
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
        return ('would_create', False)

    if not file_path.exists():
        file_path.write_text(content, encoding='utf-8')
        return ('created', True)

    # File exists - check what to do
    if force:
        file_path.write_text(content, encoding='utf-8')
        return ('overwritten', True)

    if not interactive:
        # Non-interactive mode: skip existing files by default
        return ('skipped', False)

    # Interactive mode: prompt user
    print(f"\n{Colors.YELLOW}File exists: {file_path.name}{Colors.RESET}")
    print(f"{Colors.CYAN}Options:{Colors.RESET}")
    print(f"  1. Overwrite (replace existing file)")
    print(f"  2. Skip (keep existing file)")
    print(f"  3. Backup (save as .bak and create new)")
    print(f"  4. View diff (show what would change)")

    while True:
        choice = input(f"{Colors.GREEN}Choose [1/2/3/4]: {Colors.RESET}").strip()

        if choice == '1':
            file_path.write_text(content, encoding='utf-8')
            return ('overwritten', True)
        elif choice == '2':
            return ('skipped', False)
        elif choice == '3':
            # Create backup
            backup_path = file_path.with_suffix('.md.bak')
            backup_path.write_text(file_path.read_text(encoding='utf-8'), encoding='utf-8')
            file_path.write_text(content, encoding='utf-8')
            print(f"{Colors.GREEN}✓ Backup created: {backup_path.name}{Colors.RESET}")
            return ('backed_up', True)
        elif choice == '4':
            # Show diff
            print(f"\n{Colors.CYAN}=== Current Content ==={Colors.RESET}")
            print(file_path.read_text(encoding='utf-8')[:500])
            print(f"{Colors.CYAN}=== New Content ==={Colors.RESET}")
            print(content[:500])
            print(f"{Colors.YELLOW}(showing first 500 characters of each){Colors.RESET}\n")
            # Ask again
            continue
        else:
            print(f"{Colors.RED}Invalid choice. Please enter 1, 2, 3, or 4.{Colors.RESET}")


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
            "- BRANCHING.md: Git workflow and commit conventions",
            "- TESTING.md: TDD methodology and testing patterns",
            "- .github/pull_request_template.md: PR template"
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
            "2. Run 'pg init' to initialize agent templates",
            "3. Review the generated AGENTS.md, PROJECT_STATUS.md, and TESTING.md",
            "4. AI agents read templates and collaborate via natural language",
            "5. Update PROJECT_STATUS.md as work progresses"
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
    input(f"{Colors.GREEN}Press Enter to continue...{Colors.ENDC}")


def print_farewell():
    """Print farewell message"""
    print(f"\n{Colors.CYAN}👋 Thank you for using Proto Gear!{Colors.ENDC}")
    ui.farewell()


def detect_project_structure(project_path):
    """Detect existing project structure and technologies

    Supports detection for:
    - Node.js projects (Angular, Svelte, Next.js, React, Vue.js, Express)
    - Python projects (Django, FastAPI)
    - Ruby projects (Ruby on Rails)
    - PHP projects (Laravel)
    - Java projects (Spring Boot)
    - C# projects (ASP.NET)
    """
    import json

    info = {
        'detected': False,
        'type': None,
        'framework': None,
        'directories': [],
        'structure_summary': ''
    }

    try:
        # Check for Angular (angular.json)
        if (project_path / 'angular.json').exists():
            info['detected'] = True
            info['type'] = 'Node.js Project'
            info['framework'] = 'Angular'

        # Check for Svelte/SvelteKit (svelte.config.js)
        elif (project_path / 'svelte.config.js').exists():
            info['detected'] = True
            info['type'] = 'Node.js Project'
            info['framework'] = 'SvelteKit'

        # Check for Rust (Cargo.toml)
        elif (project_path / 'Cargo.toml').exists():
            info['detected'] = True
            info['type'] = 'Rust Project'

            # Try to detect specific frameworks/patterns
            try:
                with open(project_path / 'Cargo.toml') as f:
                    cargo_content = f.read()
                    if 'actix-web' in cargo_content:
                        info['framework'] = 'Actix Web'
                    elif 'rocket' in cargo_content:
                        info['framework'] = 'Rocket'
                    elif 'axum' in cargo_content:
                        info['framework'] = 'Axum'
                    elif 'warp' in cargo_content:
                        info['framework'] = 'Warp'
                    elif 'tauri' in cargo_content:
                        info['framework'] = 'Tauri'
                    elif 'yew' in cargo_content:
                        info['framework'] = 'Yew'
            except:
                pass

        # Check for package.json (Node.js project)
        elif (project_path / 'package.json').exists():
            package_json = project_path / 'package.json'
            info['detected'] = True
            info['type'] = 'Node.js Project'

            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}

                    # Check for specific frameworks (ordered by specificity)
                    if 'next' in deps:
                        info['framework'] = 'Next.js'
                    elif '@angular/core' in deps:
                        info['framework'] = 'Angular'
                    elif 'svelte' in deps:
                        info['framework'] = 'Svelte'
                    elif 'react' in deps:
                        info['framework'] = 'React'
                    elif 'vue' in deps:
                        info['framework'] = 'Vue.js'
                    elif 'express' in deps:
                        info['framework'] = 'Express.js'
            except:
                pass

        # Check for Ruby on Rails (Gemfile + config/application.rb)
        elif (project_path / 'Gemfile').exists():
            info['detected'] = True
            info['type'] = 'Ruby Project'

            # Check for Rails
            if (project_path / 'config' / 'application.rb').exists():
                info['framework'] = 'Ruby on Rails'
            else:
                try:
                    with open(project_path / 'Gemfile') as f:
                        gemfile_content = f.read()
                        if 'rails' in gemfile_content.lower():
                            info['framework'] = 'Ruby on Rails'
                except:
                    pass

        # Check for Laravel (composer.json + artisan)
        elif (project_path / 'composer.json').exists():
            info['detected'] = True
            info['type'] = 'PHP Project'

            # Check for Laravel
            if (project_path / 'artisan').exists():
                info['framework'] = 'Laravel'
            else:
                try:
                    with open(project_path / 'composer.json') as f:
                        composer_data = json.load(f)
                        requires = composer_data.get('require', {})
                        if 'laravel/framework' in requires:
                            info['framework'] = 'Laravel'
                except:
                    pass

        # Check for Spring Boot (pom.xml or build.gradle)
        elif (project_path / 'pom.xml').exists() or (project_path / 'build.gradle').exists():
            info['detected'] = True
            info['type'] = 'Java Project'

            # Check for Spring Boot in pom.xml
            if (project_path / 'pom.xml').exists():
                try:
                    with open(project_path / 'pom.xml') as f:
                        pom_content = f.read()
                        if 'spring-boot' in pom_content.lower():
                            info['framework'] = 'Spring Boot'
                except:
                    pass

            # Check for Spring Boot in build.gradle
            if not info['framework'] and (project_path / 'build.gradle').exists():
                try:
                    with open(project_path / 'build.gradle') as f:
                        gradle_content = f.read()
                        if 'spring-boot' in gradle_content.lower() or 'org.springframework.boot' in gradle_content:
                            info['framework'] = 'Spring Boot'
                except:
                    pass

        # Check for ASP.NET (*.csproj)
        elif any(project_path.glob('*.csproj')):
            info['detected'] = True
            info['type'] = 'C# Project'

            # Check for ASP.NET in csproj files
            try:
                for csproj in project_path.glob('*.csproj'):
                    with open(csproj) as f:
                        csproj_content = f.read()
                        if 'Microsoft.AspNetCore' in csproj_content or 'Microsoft.NET.Sdk.Web' in csproj_content:
                            info['framework'] = 'ASP.NET'
                            break
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


def detect_git_config():
    """Detect Git configuration and workflow capabilities"""
    import subprocess

    config = {
        'is_git_repo': False,
        'has_remote': False,
        'remote_name': None,
        'main_branch': 'main',
        'dev_branch': 'development',
        'has_gh_cli': False,
        'workflow_mode': 'local_only'  # local_only, remote_manual, remote_automated
    }

    try:
        # Check if it's a Git repo
        result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                              capture_output=True, text=True, timeout=5)
        config['is_git_repo'] = result.returncode == 0

        if config['is_git_repo']:
            # Check for remote
            result = subprocess.run(['git', 'remote'],
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0 and result.stdout.strip():
                config['has_remote'] = True
                config['remote_name'] = result.stdout.strip().split()[0]

        # Check for GitHub CLI (gh)
        try:
            result = subprocess.run(['gh', '--version'],
                                  capture_output=True, text=True, timeout=5)
            config['has_gh_cli'] = result.returncode == 0
        except FileNotFoundError:
            config['has_gh_cli'] = False

        # Determine workflow mode
        if not config['is_git_repo']:
            config['workflow_mode'] = 'no_git'
        elif not config['has_remote']:
            config['workflow_mode'] = 'local_only'
        elif config['has_remote'] and config['has_gh_cli']:
            config['workflow_mode'] = 'remote_automated'
        elif config['has_remote'] and not config['has_gh_cli']:
            config['workflow_mode'] = 'remote_manual'
    except:
        pass

    return config


def generate_branching_doc(project_name, ticket_prefix, git_config, generation_date):
    """Generate BRANCHING.md from template"""
    template_path = Path(__file__).parent / 'BRANCHING.template.md'

    if not template_path.exists():
        return None

    try:
        template = template_path.read_text(encoding='utf-8')

        # Generate workflow mode description
        workflow_mode_descriptions = {
            'no_git': '**No Git Repository** - Consider initializing Git for version control',
            'local_only': '**Local-Only Workflow** - No remote repository configured',
            'remote_manual': '**Remote Workflow (Manual PRs)** - Remote configured, GitHub CLI not detected',
            'remote_automated': '**Remote Workflow (Automated)** - Remote configured, GitHub CLI available'
        }

        workflow_mode_desc = workflow_mode_descriptions.get(
            git_config.get('workflow_mode', 'local_only'),
            'Local-Only Workflow'
        )

        # Add workflow recommendations based on mode
        workflow_recommendations = ""
        if git_config.get('workflow_mode') == 'remote_manual':
            workflow_recommendations = f"""
> **💡 Tip**: GitHub CLI (`gh`) is not detected. You can:
> - Install `gh` CLI for automated PR creation: https://cli.github.com
> - Continue using manual PR creation via web interface
> - Use local merges if you prefer
"""
        elif git_config.get('workflow_mode') == 'remote_automated':
            workflow_recommendations = f"""
> **✅ GitHub CLI detected**: You can create PRs automatically with `gh pr create`
"""
        elif git_config.get('workflow_mode') == 'local_only':
            workflow_recommendations = f"""
> **💡 Tip**: No remote repository detected. You can:
> - Continue with local-only development
> - Add a remote later with: `git remote add origin <url>`
"""

        # Determine values based on Git configuration
        if git_config['has_remote']:
            remote_requires_pr = "\n- **Pull Requests**: Required for merging"
            remote_requires_tests = " and pass tests"
            remote_via_pr = " (via pull request)"
            merge_method = " (via pull request)"
            remote_origin = f" origin"
            if_remote = ""
            remote_push_during = "5. **Push to remote**: `git push -u origin your-branch-name` (enables backup)"
            remote_push_before_pr = "\n4. **Push to remote**: `git push -u origin feature-branch`\n5. **Create pull request**: On GitHub/GitLab"
            local_merge_steps = ""
            remote_push_step = "\n5. Push to remote: git push -u origin feature/branch"
            remote_create_pr_or_local_merge = "\n6. Create pull request on GitHub/GitLab"
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
1. Push your branch to remote
2. Go to your repository on GitHub/GitLab
3. Create pull request from your branch to `{{{{DEV_BRANCH}}}}`
4. Request review if required
5. Merge after approval"""
            remote_push_reminder = "\n✅ Push to remote regularly"
            remote_create_pr_reminder = "\n✅ Create PR for review"
            remote_force_push_reminder = "\n❌ Force push to shared branches"
            ticket_tracking = "GitHub Issues or PROJECT_STATUS.md"
        else:
            # Local-only development
            remote_requires_pr = ""
            remote_requires_tests = ""
            remote_via_pr = ""
            merge_method = " (locally)"
            remote_origin = ""
            if_remote = " (if remote configured)"
            remote_push_during = ""
            remote_push_before_pr = ""
            local_merge_steps = "\n4. **Merge locally**: `git checkout {{DEV_BRANCH}} && git merge feature-branch --no-ff`"
            remote_push_step = ""
            remote_create_pr_or_local_merge = "\n6. Merge locally to {{DEV_BRANCH}}"
            remote_handling_section = """## Local Development (No Remote)

This project does not have a remote repository configured.

### Local Workflow
```bash
# Work on your branch
git checkout -b feature/{{TICKET_PREFIX}}-XXX-description

# When done, merge to development
git checkout {{DEV_BRANCH}}
git merge feature/{{TICKET_PREFIX}}-XXX-description --no-ff

# Delete feature branch
git branch -d feature/{{TICKET_PREFIX}}-XXX-description
```

### Adding a Remote Later
If you want to add a remote repository:
```bash
git remote add origin <repository-url>
git push -u origin {{DEV_BRANCH}}
```"""
            remote_push_reminder = ""
            remote_create_pr_reminder = ""
            remote_force_push_reminder = ""
            ticket_tracking = "PROJECT_STATUS.md"

        # Replace all placeholders
        content = template.replace('{{PROJECT_NAME}}', project_name)
        content = content.replace('{{VERSION}}', __version__)
        content = content.replace('{{TICKET_PREFIX}}', ticket_prefix)
        content = content.replace('{{MAIN_BRANCH}}', git_config['main_branch'])
        content = content.replace('{{DEV_BRANCH}}', git_config['dev_branch'])
        content = content.replace('{{GENERATION_DATE}}', generation_date)
        content = content.replace('{{WORKFLOW_MODE}}', workflow_mode_desc)
        content = content.replace('{{WORKFLOW_RECOMMENDATIONS}}', workflow_recommendations)
        content = content.replace('{{REMOTE_REQUIRES_PR}}', remote_requires_pr)
        content = content.replace('{{REMOTE_REQUIRES_TESTS}}', remote_requires_tests)
        content = content.replace('{{REMOTE_VIA_PR}}', remote_via_pr)
        content = content.replace('{{MERGE_METHOD}}', merge_method)
        content = content.replace('{{REMOTE_ORIGIN}}', remote_origin)
        content = content.replace('{{IF_REMOTE}}', if_remote)
        content = content.replace('{{REMOTE_PUSH_DURING}}', remote_push_during)
        content = content.replace('{{REMOTE_PUSH_BEFORE_PR}}', remote_push_before_pr)
        content = content.replace('{{LOCAL_MERGE_STEPS}}', local_merge_steps)
        content = content.replace('{{REMOTE_PUSH_STEP}}', remote_push_step)
        content = content.replace('{{REMOTE_CREATE_PR_OR_LOCAL_MERGE}}', remote_create_pr_or_local_merge)
        content = content.replace('{{REMOTE_HANDLING_SECTION}}', remote_handling_section)
        content = content.replace('{{REMOTE_PUSH_REMINDER}}', remote_push_reminder)
        content = content.replace('{{REMOTE_CREATE_PR_REMINDER}}', remote_create_pr_reminder)
        content = content.replace('{{REMOTE_FORCE_PUSH_REMINDER}}', remote_force_push_reminder)
        content = content.replace('{{TICKET_TRACKING}}', ticket_tracking)

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
    template_dir = Path(__file__).parent
    templates = {}

    try:
        for template_file in template_dir.glob("*.template.md"):
            # Extract template name (e.g., "TESTING.template.md" -> "TESTING")
            name = template_file.stem.replace(".template", "")

            templates[name] = {
                'path': template_file,
                'name': name,
                'filename': f"{name}.md"
            }
    except Exception as e:
        print(f"Error discovering templates: {e}")

    return templates


def generate_project_template(template_name, project_dir, context, dry_run=False, force=False, interactive=True):
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
        template_file = Path(__file__).parent / f"{template_name}.template.md"

        if not template_file.exists():
            print(f"Warning: Template {template_name}.template.md not found")
            return None

        # Read template content
        full_content = template_file.read_text(encoding='utf-8')

        # Parse metadata from template
        metadata, content = MetadataParser.parse_template(full_content)

        # Check if template requirements are met (if metadata exists)
        if metadata.name:  # Has metadata
            project_info = {
                'project_type': context.get('PROJECT_TYPE', 'Any'),
                'framework': context.get('FRAMEWORK', 'Unknown')
            }

            if not metadata.meets_requirements(project_info):
                print(f"Info: Template {template_name} requirements not met for this project type")
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
        action, written = safe_write_file(output_file, content, dry_run=dry_run, force=force, interactive=interactive)

        if written or action == 'would_create':
            return (output_file, action)
        else:
            return (None, action)

    except Exception as e:
        print(f"Error generating {template_name}: {e}")
        return (None, 'error')



def copy_capability_templates(target_dir: Path, project_name: str, version: str = None, dry_run: bool = False, capabilities_config: dict = None) -> dict:
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

    result = {
        'status': 'success',
        'files_created': [],
        'errors': []
    }

    # Define source and destination
    source_dir = Path(__file__).parent / 'capabilities'
    dest_dir = target_dir / '.proto-gear'

    # Parse capabilities config (default to all if not specified)
    if capabilities_config is None:
        capabilities_config = {'skills': True, 'workflows': True, 'commands': True}

    include_skills = capabilities_config.get('skills', True)
    include_workflows = capabilities_config.get('workflows', True)
    include_commands = capabilities_config.get('commands', True)

    # Security check: Ensure source directory exists and is not a symlink
    if not source_dir.exists():
        result['status'] = 'error'
        result['errors'].append(f"Source directory not found: {source_dir}")
        return result

    if source_dir.is_symlink():
        result['status'] = 'error'
        result['errors'].append(f"Security: Source directory is a symlink: {source_dir}")
        return result

    # Check if .proto-gear already exists
    if dest_dir.exists() and not dry_run:
        result['status'] = 'warning'
        result['errors'].append(f".proto-gear directory already exists at {dest_dir}")
        return result

    if dry_run:
        print(f"\n{Colors.YELLOW}Dry run - capability files that would be created:{Colors.ENDC}")
        print(f"  Directory: .proto-gear/")

    try:
        # Walk through source directory
        for source_path in source_dir.rglob('*'):
            # Skip directories and symlinks
            if source_path.is_dir():
                continue

            # Security check: Reject symlinks
            if source_path.is_symlink():
                result['errors'].append(f"Skipped symlink: {source_path}")
                continue

            # Calculate relative path from source directory
            rel_path = source_path.relative_to(source_dir)

            # Granular filtering based on capabilities_config
            path_parts = rel_path.parts
            if len(path_parts) > 0:
                category = path_parts[0]  # skills, workflows, commands, agents, or root INDEX.md

                # Skip based on configuration
                if category == 'skills' and not include_skills:
                    continue
                elif category == 'workflows' and not include_workflows:
                    continue
                elif category == 'commands' and not include_commands:
                    continue
                # Always include 'agents' folder (just INDEX.md) and root INDEX.md

            # Security check: Validate path doesn't contain traversal attempts
            normalized_rel_path = Path(os.path.normpath(rel_path))
            if '..' in normalized_rel_path.parts or normalized_rel_path.is_absolute():
                result['errors'].append(f"Security: Invalid path detected: {rel_path}")
                continue

            # Determine destination path
            dest_path = dest_dir / normalized_rel_path

            # Handle .template.md extension (rename to .md)
            if dest_path.suffix == '.md' and dest_path.stem.endswith('.template'):
                dest_path = dest_path.parent / (dest_path.stem.replace('.template', '') + '.md')

            # Security check: Ensure destination stays within .proto-gear/
            try:
                dest_path.resolve().relative_to(dest_dir.resolve())
            except ValueError:
                result['errors'].append(f"Security: Destination path escapes .proto-gear/: {dest_path}")
                continue

            if dry_run:
                print(f"    - {dest_path.relative_to(target_dir)}")
                result['files_created'].append(str(dest_path.relative_to(target_dir)))
            else:
                # Create parent directories
                dest_path.parent.mkdir(parents=True, exist_ok=True)

                # Set directory permissions (755)
                try:
                    dest_path.parent.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                except (OSError, NotImplementedError):
                    # Some platforms don't support chmod
                    pass

                # Read source file with UTF-8 encoding
                try:
                    content = source_path.read_text(encoding='utf-8')
                except UnicodeDecodeError as e:
                    result['errors'].append(f"Encoding error in {source_path}: {e}")
                    continue

                # Replace placeholders
                content = content.replace('{{VERSION}}', version)
                content = content.replace('{{PROJECT_NAME}}', project_name)

                # Write to destination with UTF-8 encoding
                dest_path.write_text(content, encoding='utf-8')

                # Set file permissions (644)
                try:
                    dest_path.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
                except (OSError, NotImplementedError):
                    # Some platforms don't support chmod
                    pass

                result['files_created'].append(str(dest_path.relative_to(target_dir)))

        if result['errors']:
            result['status'] = 'partial'

    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(f"Unexpected error: {str(e)}")

    return result


def setup_agent_framework_only(dry_run=False, force=False, with_branching=False, ticket_prefix=None, with_capabilities=False, capabilities_config=None, with_all=False, core_templates=None):
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

            # Determine ticket prefix
            if not ticket_prefix:
                # Try to derive from project name
                project_name = current_dir.name.upper().replace('-', '').replace('_', '')[:6]
                ticket_prefix = project_name if project_name else 'PROJ'

            # Optionally create BRANCHING.md
            branching_reference = ""
            if with_branching:
                git_config = detect_git_config()
                branching_content = generate_branching_doc(
                    current_dir.name,
                    ticket_prefix,
                    git_config,
                    datetime.now().strftime('%Y-%m-%d')
                )

                if branching_content:
                    branching_file = current_dir / 'BRANCHING.md'
                    action, written = safe_write_file(branching_file, branching_content, dry_run=dry_run, force=force, interactive=True)
                    if written or action == 'would_create':
                        files_created.append('BRANCHING.md')
                    branching_reference = f"\n> **📋 Branching Strategy**: See [BRANCHING.md](BRANCHING.md) for Git workflow and commit conventions\n"

            # Create AGENTS.md
            agents_file = current_dir / 'AGENTS.md'
            agents_content = f"""# AGENTS.md - {current_dir.name}

> **ProtoGear Agent Framework Integration**
> **Project Type**: {project_info.get('type', 'Unknown')}
> **Framework**: {project_info.get('framework', 'Unknown')}
{branching_reference}
## Framework Activation

This project is now integrated with ProtoGear's AI agent workflow system.

When this file is read by an AI agent, it should:

1. Analyze the current project structure
2. Understand the technology stack in use
3. Provide context-aware development assistance
4. Follow the project's established patterns{'5. Follow branching and commit conventions in BRANCHING.md' if with_branching else ''}

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
# Initialize agent templates (already done)
pg init

# Show help and documentation
pg help
```

## Next Steps

1. Review this file to understand agent patterns and workflows
2. Check PROJECT_STATUS.md for current project state{'3. Review BRANCHING.md for Git workflow conventions' if with_branching else '3. Review TESTING.md for TDD patterns'}
{'4. Review TESTING.md for TDD patterns' if with_branching else '4. Start development with AI agents reading templates'}
{'5. Start development with AI agents reading templates' if with_branching else ''}

---
*Powered by ProtoGear Agent Framework v0.5.0 (Beta)*
"""
            action, written = safe_write_file(agents_file, agents_content, dry_run=dry_run, force=force, interactive=True)
            if written or action == 'would_create':
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
            action, written = safe_write_file(status_file, status_content, dry_run=dry_run, force=force, interactive=True)
            if written or action == 'would_create':
                files_created.append('PROJECT_STATUS.md')

            # Generate additional templates based on selections
            template_context = {
                'PROJECT_NAME': current_dir.name,
                'TICKET_PREFIX': ticket_prefix,
                'DATE': datetime.now().strftime('%Y-%m-%d'),
                'YEAR': datetime.now().strftime('%Y'),
                'VERSION': __version__
            }

            templates_to_generate = []

            # Priority 1: Use core_templates if provided (from wizard)
            if core_templates and isinstance(core_templates, dict):
                # Generate templates that were explicitly selected
                for template_name, should_generate in core_templates.items():
                    if should_generate and template_name not in ['AGENTS', 'PROJECT_STATUS']:
                        # Skip if already created (e.g., BRANCHING from with_branching flag)
                        if f"{template_name}.md" not in files_created:
                            templates_to_generate.append(template_name)

            # Priority 2: Handle --all flag (CLI)
            elif with_all:
                templates_to_generate.extend([
                    'TESTING',
                    'BRANCHING',
                    'CONTRIBUTING',
                    'SECURITY',
                    'ARCHITECTURE',
                    'CODE_OF_CONDUCT'
                ])

            # Priority 3: Legacy behavior for with_branching
            elif with_branching:
                templates_to_generate.append('TESTING')
                if 'BRANCHING' not in [f.replace('.md', '') for f in files_created]:
                    templates_to_generate.append('BRANCHING')

            # Generate all selected templates
            for template_name in templates_to_generate:
                output_file, action = generate_project_template(
                    template_name,
                    current_dir,
                    template_context,
                    dry_run=dry_run,
                    force=force,
                    interactive=True
                )

                if output_file or action == 'would_create':
                    files_created.append(f"{template_name}.md")

            files_created.append('PROJECT_STATUS.md')

            # Create capabilities if requested
            if with_capabilities:
                capability_result = copy_capability_templates(
                    current_dir,
                    current_dir.name,
                    dry_run=False,
                    capabilities_config=capabilities_config
                )

                if capability_result['status'] == 'success':
                    files_created.extend(capability_result['files_created'])
                    print(f"{Colors.GREEN}+ Capability system created in .proto-gear/{Colors.ENDC}")
                elif capability_result['status'] == 'warning':
                    print(f"{Colors.YELLOW}! {capability_result['errors'][0]}{Colors.ENDC}")
                else:
                    print(f"{Colors.YELLOW}! Capability creation had issues: {capability_result.get('errors')}{Colors.ENDC}")

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
        if with_branching:
            print("  - BRANCHING.md (Git workflow and commit conventions)")

        # Show additional templates based on selections
        templates_shown = []

        # Priority 1: Use core_templates if provided (from wizard)
        if core_templates and isinstance(core_templates, dict):
            for template_name, should_generate in core_templates.items():
                if should_generate and template_name not in ['AGENTS', 'PROJECT_STATUS', 'BRANCHING']:
                    templates_shown.append(template_name)

        # Priority 2: Handle --all flag (CLI)
        elif with_all:
            templates_shown = ['TESTING', 'CONTRIBUTING', 'SECURITY', 'ARCHITECTURE', 'CODE_OF_CONDUCT']
            if with_branching:
                # BRANCHING already shown above
                pass
            else:
                templates_shown.insert(0, 'BRANCHING')

        # Show template descriptions
        template_descriptions = {
            'TESTING': 'TDD patterns and best practices',
            'BRANCHING': 'Git workflow and commit conventions',
            'CONTRIBUTING': 'Contribution guidelines',
            'SECURITY': 'Security policy and vulnerability reporting',
            'ARCHITECTURE': 'System design documentation',
            'CODE_OF_CONDUCT': 'Community guidelines'
        }

        for template_name in templates_shown:
            desc = template_descriptions.get(template_name, 'Project template')
            print(f"  - {template_name}.md ({desc})")

        # Show capability files if requested
        if with_capabilities:
            capability_result = copy_capability_templates(
                current_dir,
                current_dir.name,
                dry_run=True,
                capabilities_config=capabilities_config
            )

        return {'status': 'success', 'dry_run': True}


def interactive_setup_wizard():
    """Interactive wizard for configuring ProtoGear setup"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}ProtoGear Interactive Setup Wizard{Colors.ENDC}")
    print("=" * 60)
    print(f"{Colors.GRAY}Let's configure AI-powered development workflow for your project{Colors.ENDC}")
    print("=" * 60)

    config = {}

    # Detect current project
    current_dir = Path(".")
    project_info = detect_project_structure(current_dir)

    print(f"\n{Colors.CYAN}📊 Project Detection{Colors.ENDC}")
    print("-" * 30)
    print(f"Directory: {Colors.BOLD}{current_dir.absolute()}{Colors.ENDC}")

    if project_info['detected']:
        print(f"Type: {Colors.GREEN}{project_info['type']}{Colors.ENDC}")
        if project_info.get('framework'):
            print(f"Framework: {Colors.GREEN}{project_info['framework']}{Colors.ENDC}")
    else:
        print(f"Type: {Colors.YELLOW}Generic Project{Colors.ENDC}")

    # Check Git configuration
    git_config = detect_git_config()
    if git_config['is_git_repo']:
        print(f"Git: {Colors.GREEN}Initialized{Colors.ENDC}")
        if git_config['has_remote']:
            print(f"Remote: {Colors.GREEN}{git_config['remote_name']}{Colors.ENDC}")
            # Show GitHub CLI status
            if git_config['has_gh_cli']:
                print(f"GitHub CLI: {Colors.GREEN}Installed{Colors.ENDC} (automated PRs available)")
            else:
                print(f"GitHub CLI: {Colors.YELLOW}Not detected{Colors.ENDC} (manual PRs via web)")
        else:
            print(f"Remote: {Colors.YELLOW}None (local-only){Colors.ENDC}")

        # Display workflow mode
        workflow_modes = {
            'local_only': (Colors.YELLOW, 'Local-Only Workflow'),
            'remote_manual': (Colors.CYAN, 'Remote Workflow (Manual PRs)'),
            'remote_automated': (Colors.GREEN, 'Remote Workflow (Automated PRs)')
        }
        mode_color, mode_desc = workflow_modes.get(
            git_config.get('workflow_mode', 'local_only'),
            (Colors.GRAY, 'Unknown')
        )
        print(f"Workflow Mode: {mode_color}{mode_desc}{Colors.ENDC}")
    else:
        print(f"Git: {Colors.YELLOW}Not initialized{Colors.ENDC}")

    # Question 1: Branching Strategy
    print(f"\n{Colors.CYAN}📋 Branching & Git Workflow{Colors.ENDC}")
    print("-" * 30)
    print("Proto Gear can generate a comprehensive branching strategy document")
    print("that defines Git workflow conventions and commit message standards.")
    print(f"\n{Colors.GRAY}This includes:{Colors.ENDC}")
    print("  • Branch naming conventions (feature/*, bugfix/*, hotfix/*)")
    print("  • Conventional commit message format")
    print("  • Workflow examples for AI agents")
    print("  • PR templates and merge strategies")

    if git_config['is_git_repo']:
        print(f"\n{Colors.GREEN}✓ Git repository detected - branching strategy recommended{Colors.ENDC}")
    else:
        print(f"\n{Colors.YELLOW}⚠ No Git repository - you can still generate the strategy for future use{Colors.ENDC}")

    while True:
        response = safe_input(f"\n{Colors.BOLD}Generate BRANCHING.md? (y/n): {Colors.ENDC}").lower()
        if response in ['y', 'yes']:
            config['with_branching'] = True
            break
        elif response in ['n', 'no']:
            config['with_branching'] = False
            break
        else:
            print(f"{Colors.YELLOW}Please enter 'y' or 'n'{Colors.ENDC}")

    # Question 2: Ticket Prefix (only if branching enabled)
    if config['with_branching']:
        print(f"\n{Colors.CYAN}🎫 Ticket Prefix Configuration{Colors.ENDC}")
        print("-" * 30)
        print("Tickets and branches use a prefix for identification.")
        print(f"{Colors.GRAY}Examples: PROJ-001, APP-042, MYAPP-123{Colors.ENDC}")

        # Suggest a prefix based on project name
        suggested_prefix = current_dir.name.upper().replace('-', '').replace('_', '')[:6]
        if not suggested_prefix or len(suggested_prefix) < 2:
            suggested_prefix = 'PROJ'

        print(f"\nSuggested prefix: {Colors.GREEN}{suggested_prefix}{Colors.ENDC}")

        response = safe_input(f"{Colors.BOLD}Enter ticket prefix (press Enter for '{suggested_prefix}'): {Colors.ENDC}").strip().upper()

        if response:
            # Validate prefix (alphanumeric, 2-10 chars)
            if response.isalnum() and 2 <= len(response) <= 10:
                config['ticket_prefix'] = response
            else:
                print(f"{Colors.YELLOW}Invalid prefix. Using suggested: {suggested_prefix}{Colors.ENDC}")
                config['ticket_prefix'] = suggested_prefix
        else:
            config['ticket_prefix'] = suggested_prefix

        print(f"Using prefix: {Colors.GREEN}{config['ticket_prefix']}{Colors.ENDC}")
    else:
        config['ticket_prefix'] = None

    # Summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}📝 Configuration Summary{Colors.ENDC}")
    print("=" * 60)
    print(f"Project: {Colors.BOLD}{current_dir.name}{Colors.ENDC}")
    print(f"Type: {project_info.get('type', 'Generic')}")
    if project_info.get('framework'):
        print(f"Framework: {project_info['framework']}")

    print(f"\n{Colors.CYAN}Files to be created:{Colors.ENDC}")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} AGENTS.md (AI agent integration guide)")
    print(f"  {Colors.GREEN}✓{Colors.ENDC} PROJECT_STATUS.md (Project state tracking)")

    if config['with_branching']:
        print(f"  {Colors.GREEN}✓{Colors.ENDC} BRANCHING.md (Git workflow conventions)")
        print(f"\nTicket Prefix: {Colors.BOLD}{config['ticket_prefix']}{Colors.ENDC}")
    else:
        print(f"  {Colors.GRAY}⊘ BRANCHING.md (not selected){Colors.ENDC}")

    # Confirmation
    print()
    while True:
        response = safe_input(f"{Colors.BOLD}Proceed with setup? (y/n): {Colors.ENDC}").lower()
        if response in ['y', 'yes']:
            config['confirmed'] = True
            break
        elif response in ['n', 'no']:
            config['confirmed'] = False
            break
        else:
            print(f"{Colors.YELLOW}Please enter 'y' or 'n'{Colors.ENDC}")

    return config


def run_simple_protogear_init(dry_run=False, force=False, with_branching=False, ticket_prefix=None, with_capabilities=False, capabilities_config=None, with_all=False, core_templates=None):
    """
    Initialize ProtoGear AI Agent Framework in current project

    Args:
        dry_run: If True, don't actually write files
        force: If True, overwrite existing files without prompting
        with_branching: Generate BRANCHING.md
        ticket_prefix: Ticket ID prefix
        with_capabilities: Generate .proto-gear/ directory
        capabilities_config: Configuration for capabilities
        with_all: Generate all available templates
        core_templates: List of specific core templates to generate
    """
    from datetime import datetime

    print(f"\n{Colors.BOLD}ProtoGear AI Agent Framework Initialization{Colors.ENDC}")
    print("=" * 60)
    print(f"{Colors.GRAY}Adding AI-powered development workflow to your project{Colors.ENDC}")
    print("=" * 60)

    # Directly run agent framework setup (no menu)
    try:
        result = setup_agent_framework_only(
            dry_run=dry_run,
            force=force,
            with_branching=with_branching,
            ticket_prefix=ticket_prefix,
            with_capabilities=with_capabilities,
            capabilities_config=capabilities_config,
            with_all=with_all,
            core_templates=core_templates
        )
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

                # Separate template files from capability files
                template_files = []
                capability_files = []

                for file in result['files_created']:
                    # Handle both forward and backslash separators
                    if file.startswith('.proto-gear/') or file.startswith('.proto-gear\\'):
                        capability_files.append(file)
                    else:
                        template_files.append(file)

                # Show templates
                for file in template_files:
                    print(f"  + {file}")

                # Show capabilities summary if any
                if capability_files:
                    print(f"\n{Colors.CYAN}Capabilities installed ({len(capability_files)} files):{Colors.ENDC}")
                    print(f"  + .proto-gear/ directory with:")

                    # Categorize capability files (handle both separators)
                    skills = [f for f in capability_files if '/skills/' in f or '\\skills\\' in f]
                    workflows = [f for f in capability_files if '/workflows/' in f or '\\workflows\\' in f]
                    commands = [f for f in capability_files if '/commands/' in f or '\\commands\\' in f]

                    if skills:
                        print(f"    • {len(skills)} skill(s)")
                    if workflows:
                        print(f"    • {len(workflows)} workflow(s)")
                    if commands:
                        print(f"    • {len(commands)} command(s)")

            # Dynamic next steps based on what was created
            print(f"\n{Colors.YELLOW}Next steps:{Colors.ENDC}")
            files = result.get('files_created', [])
            step = 1

            if 'AGENTS.md' in files:
                print(f"  {step}. Review AGENTS.md to understand AI agent patterns and workflows")
                step += 1

            if 'PROJECT_STATUS.md' in files:
                print(f"  {step}. Check PROJECT_STATUS.md for project state tracking")
                step += 1

            if 'TESTING.md' in files:
                print(f"  {step}. Review TESTING.md for TDD methodology")
                step += 1

            if 'BRANCHING.md' in files:
                print(f"  {step}. Follow BRANCHING.md conventions for Git workflow")
                step += 1

            # Check if capabilities were installed
            has_capabilities = any(f.startswith('.proto-gear/') or f.startswith('.proto-gear\\') for f in files)
            if has_capabilities:
                print(f"  {step}. Explore .proto-gear/ for available skills, workflows, and commands")
                step += 1

            print(f"  {step}. AI agents will read these templates and collaborate naturally")

    return result


def main():
    """Main entry point for Proto Gear AI Agent Framework"""
    # Add argument parsing
    parser = argparse.ArgumentParser(
        description="Proto Gear - AI Agent Framework for Development Workflows",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pg init              Initialize AI agent templates in current project
  pg init --dry-run    Preview what will be created
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
    init_parser.add_argument(
        '--force',
        action='store_true',
        help='Force overwrite existing files without prompting'
    )
    init_parser.add_argument(
        '--with-branching',
        action='store_true',
        help='Generate BRANCHING.md with Git workflow conventions'
    )
    init_parser.add_argument(
        '--ticket-prefix',
        type=str,
        default=None,
        help='Ticket ID prefix (e.g., PROJ, MYAPP). Defaults to project name.'
    )
    init_parser.add_argument(
        '--with-capabilities',
        action='store_true',
        help='Generate .proto-gear/ capability system (skills, workflows, commands)'
    )
    init_parser.add_argument(
        '--all',
        action='store_true',
        help='Generate ALL available project templates (TESTING, BRANCHING, CONTRIBUTING, SECURITY, ARCHITECTURE, CODE_OF_CONDUCT)'
    )
    init_parser.add_argument(
        '--no-interactive',
        action='store_true',
        help='Skip interactive wizard (use for automated/scripted setup)'
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

            # Check if Proto Gear is already initialized
            current_dir = Path(".")
            existing_env = detect_existing_environment(current_dir)

            # Determine if we should use interactive wizard
            # Use interactive if no flags provided (except --dry-run and --force)
            use_interactive = not args.no_interactive and not args.with_branching and args.ticket_prefix is None and not args.with_capabilities

            if use_interactive:
                # Run interactive wizard
                try:
                    # Check if this is an incremental update (Proto Gear already initialized)
                    if existing_env['is_existing'] and ENHANCED_WIZARD_AVAILABLE and run_incremental_wizard:
                        # Run incremental wizard for updating existing environment
                        project_info = detect_project_structure(current_dir)
                        git_config = detect_git_config()

                        wizard_config = run_incremental_wizard(existing_env, project_info, git_config, current_dir)

                        if wizard_config is None or not wizard_config.get('confirmed'):
                            print(f"\n{Colors.YELLOW}Update cancelled by user.{Colors.ENDC}")
                            sys.exit(0)

                    # Fresh initialization - use enhanced wizard if available
                    elif ENHANCED_WIZARD_AVAILABLE and QUESTIONARY_AVAILABLE:
                        # Get project info for enhanced wizard
                        project_info = detect_project_structure(current_dir)
                        git_config = detect_git_config()

                        wizard_config = run_enhanced_wizard(project_info, git_config, current_dir)

                        if wizard_config is None or not wizard_config.get('confirmed'):
                            print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
                            sys.exit(0)
                    else:
                        # Fallback to simple wizard
                        wizard_config = interactive_setup_wizard()

                        if not wizard_config.get('confirmed'):
                            print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
                            sys.exit(0)

                    # Run setup with wizard configuration
                    result = run_simple_protogear_init(
                        dry_run=args.dry_run,
                        force=args.force if hasattr(args, 'force') else False,
                        with_branching=wizard_config.get('with_branching', False),
                        ticket_prefix=wizard_config.get('ticket_prefix'),
                        with_capabilities=wizard_config.get('with_capabilities', False),
                        capabilities_config=wizard_config.get('capabilities_config'),
                        with_all=wizard_config.get('with_all', False),
                        core_templates=wizard_config.get('core_templates')
                    )
                except KeyboardInterrupt:
                    print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
                    sys.exit(0)
            else:
                # Run with CLI flags (non-interactive)
                result = run_simple_protogear_init(
                    dry_run=args.dry_run,
                    force=args.force if hasattr(args, 'force') else False,
                    with_branching=args.with_branching,
                    ticket_prefix=args.ticket_prefix,
                    with_capabilities=args.with_capabilities,
                    with_all=args.all if hasattr(args, 'all') else False
                    )

            if result['status'] == 'success':
                print(f"\n{Colors.GREEN}ProtoGear AI Agent Framework initialized!{Colors.ENDC}")
            elif result['status'] == 'cancelled':
                print(f"\n{Colors.YELLOW}Initialization cancelled by user.{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}Initialization failed: {result.get('error', 'Unknown error')}{Colors.ENDC}")
                sys.exit(1)

            sys.exit(0)

        # Handle 'help' command
        elif args.command == 'help':
            show_help()
            sys.exit(0)

        # No command provided - show help
        else:
            show_splash_screen()
            print(f"{Colors.GREEN}Welcome to Proto Gear AI Agent Framework!{Colors.ENDC}")
            print(f"{Colors.GRAY}Template generator for AI-powered development collaboration{Colors.ENDC}\n")
            print(f"{Colors.CYAN}Available Commands:{Colors.ENDC}")
            print(f"  {Colors.BOLD}pg init{Colors.ENDC}         - Initialize AI agent templates in your project")
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
