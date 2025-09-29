#!/usr/bin/env python3
"""
Proto Gear - The Ultimate Project Framework Generator
Main entry point with interactive wizard selection and beautiful CLI UX
"""

import sys
import os
import time
import random
from pathlib import Path
from typing import Optional
import argparse # Added argparse

# ASCII Art variations for Proto Gear
# Define logos as separate variables to ensure correct parsing
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
    ║                             ⚙️ Framework Generator v3.0 ⚙️ ║
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


def print_with_delay(text: str, delay: float = 0.02):
    """Print text with typewriter effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def print_centered(text: str, width: int = 80):
    """Print text centered within given width"""
    print(text.center(width))


def show_splash_screen():
    """Display the Proto Gear splash screen"""
    clear_screen()
    
    # Choose a random logo
    logo = random.choice(PROTO_GEAR_LOGOS)
    
    # Animated logo appearance
    print(Colors.CYAN + Colors.BOLD)
    for line in logo.split('\n'):
        print(line)
        time.sleep(0.05)
    print(Colors.ENDC)
    
    # Tagline with typewriter effect
    print()
    tagline = "⚡ The Ultimate Project Framework Generator ⚡"
    print_centered(Colors.YELLOW + tagline + Colors.ENDC)
    
    time.sleep(0.5)
    print()
    print_centered(Colors.GRAY + "Powered by advanced AI configuration" + Colors.ENDC)
    print_centered(Colors.GRAY + "200+ frameworks • 40+ platforms • Infinite possibilities" + Colors.ENDC)
    
    print("\n" + "─" * 80 + "\n")
    time.sleep(0.5)


def show_wizard_menu():
    """Show interactive wizard selection menu"""
    print(Colors.BOLD + Colors.GREEN + "🎯 Choose Your Adventure" + Colors.ENDC)
    print("\nWhat kind of project would you like to create?\n")
    
    wizards = [
        {
            'name': 'Quick Start',
            'icon': '⚡',
            'description': 'Simple and fast - perfect for prototypes',
            'coverage': '17%',
            'time': '5 min',
            'wizard': 'basic'
        },
        {
            'name': 'Modern Web',
            'icon': '🌐',
            'description': 'Full-stack web apps with latest frameworks',
            'coverage': '71%',
            'time': '10 min',
            'wizard': 'enhanced'
        },
        {
            'name': 'Enterprise',
            'icon': '🏢',
            'description': 'Complete setup with compliance & monitoring',
            'coverage': '100%',
            'time': '15 min',
            'wizard': 'ultimate'
        },
        {
            'name': 'Multi-Platform',
            'icon': '📱',
            'description': 'Mobile, Desktop & Cross-platform apps',
            'coverage': '100%+',
            'time': '20 min',
            'wizard': 'multiplatform'
        },
        {
            'name': 'AI Assistant',
            'icon': '🤖',
            'description': 'Let AI recommend the best setup for you',
            'coverage': 'Auto',
            'time': 'Varies',
            'wizard': 'ai'
        },
        {
            'name': 'Agent Framework Only',
            'icon': '⚙️',
            'description': 'Add AI agent workflow to an existing project',
            'coverage': 'N/A',
            'time': '2 min',
            'wizard': 'agent_framework_only'
        },
        {
            'name': 'Browse Templates',
            'icon': '📚',
            'description': 'Start from pre-configured project templates',
            'coverage': 'N/A',
            'time': 'Varies',
            'wizard': 'templates'
        },
        {
            'name': 'Help & Documentation',
            'icon': '❓',
            'description': 'Learn more about Proto Gear',
            'coverage': 'N/A',
            'time': 'N/A',
            'wizard': 'help'
        }
    ]
    
    for i, wizard in enumerate(wizards, 1):
        print(f"{Colors.CYAN}{i}.{Colors.ENDC} {wizard['icon']}  {Colors.BOLD}{wizard['name']}{Colors.ENDC}")
        print(f"    {Colors.GRAY}{wizard['description']}{Colors.ENDC}")
        print(f"    {Colors.YELLOW}Coverage: {wizard['coverage']} • Time: {wizard['time']}{Colors.ENDC}")
        print()
    
    print(f"{Colors.CYAN}0.{Colors.ENDC} 🚪  {Colors.BOLD}Exit{Colors.ENDC}")
    print(f"    {Colors.GRAY}Exit Proto Gear{Colors.ENDC}")
    
    print("\n" + "─" * 80 + "\n")
    
    while True:
        try:
            choice = input(f"{Colors.GREEN}Enter your choice (0-{len(wizards)}): {Colors.ENDC}").strip()
            
            if choice == '0':
                print_farewell()
                sys.exit(0)
            elif choice.isdigit() and 1 <= int(choice) <= len(wizards):
                selected_wizard = wizards[int(choice) - 1]['wizard']
                if selected_wizard == 'help':
                    show_help()
                else:
                    return selected_wizard
            else:
                print(f"{Colors.FAIL}Invalid choice. Please enter a number between 0 and {len(wizards)}.{Colors.ENDC}")
        except KeyboardInterrupt:
            print_farewell()
            sys.exit(0)


def show_templates_menu():
    """Show project templates menu"""
    clear_screen()
    print(Colors.BOLD + Colors.MAGENTA + "📚 Project Templates Gallery" + Colors.ENDC)
    print("\n" + "─" * 80 + "\n")
    
    categories = {
        'General': [
            ('Blog', 'Content-focused site with MDX'),
            ('E-commerce', 'Online store with payments'),
            ('SaaS', 'Software as a Service starter'),
            ('Landing Page', 'Marketing & conversion focused'),
            ('Documentation', 'Technical docs with search'),
            ('Portfolio', 'Showcase your work'),
            ('Dashboard', 'Admin panel with charts'),
            ('Social Network', 'Community platform')
        ],
        'Healthcare': [
            ('Patient Portal', 'HIPAA-compliant patient access'),
            ('Medical Practice', 'Clinic management system'),
            ('Telehealth', 'Video consultation platform'),
            ('Health Tracker', 'Personal health monitoring'),
            ('Clinical Trials', 'Research study management')
        ],
        'Industry': [
            ('Fintech', 'Financial services platform'),
            ('EdTech', 'Educational technology'),
            ('PropTech', 'Real estate technology'),
            ('LegalTech', 'Legal services platform')
        ]
    }
    
    template_num = 1
    template_map = {}
    
    for category, templates in categories.items():
        print(f"{Colors.CYAN}{Colors.BOLD}{category}:{Colors.ENDC}")
        for name, description in templates:
            print(f"  {Colors.YELLOW}{template_num}.{Colors.ENDC} {name}")
            print(f"      {Colors.GRAY}{description}{Colors.ENDC}")
            template_map[str(template_num)] = name.lower().replace(' ', '-')
            template_num += 1
        print()
    
    print(f"{Colors.CYAN}0.{Colors.ENDC} ← Back to main menu")
    print("\n" + "─" * 80 + "\n")
    
    choice = input(f"{Colors.GREEN}Select template (0-{template_num-1}): {Colors.ENDC}").strip()
    
    if choice == '0':
        return None
    elif choice in template_map:
        return template_map[choice]
    else:
        print(f"{Colors.WARNING}Invalid choice. Returning to main menu.{Colors.ENDC}")
        time.sleep(1)
        return None


def show_ai_assistant():
    """Show AI-powered project recommendation"""
    clear_screen()
    print(Colors.BOLD + Colors.MAGENTA + "🤖 Proto Gear AI Assistant" + Colors.ENDC)
    print("\n" + "─" * 80 + "\n")
    
    print("I'll help you choose the perfect setup for your project.")
    print("Please answer a few questions:\n")
    
    # Question 1: Project Type
    print(f"{Colors.CYAN}1. What are you building?{Colors.ENDC}")
    print("   a) Website or web application")
    print("   b) Mobile app (iOS/Android)")
    print("   c) Desktop application")
    print("   d) API or backend service")
    print("   e) Library or package")
    print("   f) Something else")
    
    project_type = input(f"\n{Colors.GREEN}Your choice (a-f): {Colors.ENDC}").strip().lower()
    
    # Question 2: Team Size
    print(f"\n{Colors.CYAN}2. Team size?{Colors.ENDC}")
    print("   a) Just me")
    print("   b) Small team (2-5)")
    print("   c) Medium team (6-20)")
    print("   d) Large team (20+)")
    
    team_size = input(f"\n{Colors.GREEN}Your choice (a-d): {Colors.ENDC}").strip().lower()
    
    # Question 3: Timeline
    print(f"\n{Colors.CYAN}3. Project timeline?{Colors.ENDC}")
    print("   a) Prototype/MVP (< 1 month)")
    print("   b) Short-term (1-3 months)")
    print("   c) Medium-term (3-12 months)")
    print("   d) Long-term (1+ years)")
    
    timeline = input(f"\n{Colors.GREEN}Your choice (a-d): {Colors.ENDC}").strip().lower()
    
    # Question 4: Special Requirements
    print(f"\n{Colors.CYAN}4. Any special requirements? (select all that apply){Colors.ENDC}")
    print("   [ ] Authentication & user management")
    print("   [ ] Real-time features (chat, notifications)")
    print("   [ ] Payment processing")
    print("   [ ] Compliance (GDPR, HIPAA, etc.)")
    print("   [ ] Multi-language support")
    print("   [ ] Offline functionality")
    
    requirements = input(f"\n{Colors.GREEN}Enter requirements (comma-separated) or press Enter to skip: {Colors.ENDC}").strip()
    
    # AI Logic (simplified)
    print(f"\n{Colors.YELLOW}🧠 Analyzing your requirements...{Colors.ENDC}")
    time.sleep(2)
    
    # Recommendation based on answers
    if project_type in ['b', 'c']:
        recommended = 'multiplatform'
        reason = "You need multi-platform support for mobile/desktop development"
    elif team_size in ['c', 'd'] or 'compliance' in requirements.lower():
        recommended = 'ultimate'
        reason = "Large team or compliance requirements need enterprise features"
    elif timeline == 'a':
        recommended = 'basic'
        reason = "Quick prototypes benefit from minimal setup"
    else:
        recommended = 'enhanced'
        reason = "Modern web development with good feature coverage"
    
    print(f"\n{Colors.GREEN}✨ Recommendation:{Colors.ENDC}")
    print(f"   Based on your requirements, I recommend the {Colors.BOLD}{recommended.title()} Wizard{Colors.ENDC}")
    print(f"   {Colors.GRAY}Reason: {reason}{Colors.ENDC}")
    
    print(f"\n{Colors.CYAN}Would you like to:{Colors.ENDC}")
    print("   1. Use recommended wizard")
    print("   2. Choose a different wizard")
    print("   3. Return to main menu")
    
    ai_choice = input(f"\n{Colors.GREEN}Your choice (1-3): {Colors.ENDC}").strip()
    
    if ai_choice == '1':
        return recommended
    elif ai_choice == '2':
        return None  # Will show main menu
    else:
        return None


def show_help():
    """Show help and documentation"""
    clear_screen()
    print(Colors.BOLD + Colors.CYAN + "📖 Proto Gear Documentation" + Colors.ENDC)
    print("\n" + "─" * 80 + "\n")
    
    sections = [
        ("What is Proto Gear?", [
            "Proto Gear is an advanced project framework generator that helps you",
            "bootstrap any type of application with production-ready configurations.",
            "It supports 200+ frameworks and 40+ platforms out of the box."
        ]),
        ("Wizard Types", [
            "• Quick Start: Basic setup for simple projects (5 features)",
            "• Modern Web: Full-stack web development (20 features)",
            "• Enterprise: Complete setup with compliance (28+ features)",
            "• Multi-Platform: Mobile, desktop, and cross-platform (40+ features)"
        ]),
        ("Key Features", [
            "✓ Interactive configuration with smart defaults",
            "✓ 19 pre-configured project templates",
            "✓ Support for all major frameworks and platforms",
            "✓ Built-in testing, CI/CD, and deployment configs",
            "✓ Medical/healthcare compliance options",
            "✓ Monorepo and microservices support"
        ]),
        ("Getting Started", [
            "1. Choose a wizard based on your project needs",
            "2. Answer the interactive questions",
            "3. Review the configuration",
            "4. Let Proto Gear generate your project",
            "5. Follow the custom next-steps guide"
        ])
    ]
    
    for title, content in sections:
        print(f"{Colors.YELLOW}{Colors.BOLD}{title}{Colors.ENDC}")
        for line in content:
            print(f"  {line}")
        print()
    
    print(f"{Colors.CYAN}Links:{Colors.ENDC}")
    print(f"  GitHub: {Colors.BLUE}github.com/proto-gear{Colors.ENDC}")
    print(f"  Docs:   {Colors.BLUE}protogear.dev/docs{Colors.ENDC}")
    print(f"  Discord: {Colors.BLUE}discord.gg/protogear{Colors.ENDC}")
    
    print("\n" + "─" * 80 + "\n")
    input(f"{Colors.GREEN}Press Enter to return to main menu...{Colors.ENDC}")


def print_farewell():
    """Print farewell message"""
    print(f"\n{Colors.CYAN}👋 Thank you for using Proto Gear!{Colors.ENDC}")
    print(f"{Colors.GRAY}Happy coding! May your builds be swift and your bugs be few.{Colors.ENDC}\n")


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

## Next Steps

1. Review this file to understand agent capabilities
2. Check PROJECT_STATUS.md for current project state  
3. Start development with AI-powered assistance

---
*Powered by ProtoGear Agent Framework v3.0*
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
```

## Active Tickets
*No active tickets yet - ProtoGear will track development progress here*

## Completed Tickets
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


def setup_full_project_scaffolding(dry_run=False):
    """Set up complete project scaffolding with ProtoGear"""
    from datetime import datetime
    import json
    
    print(f"\n{Colors.CYAN}Full Project Scaffolding{Colors.ENDC}")
    print("-" * 30)
    
    print("Running the complete 7-step project scaffolding wizard...")
    
    # Run the 7-step project scaffolding wizard
    return run_seven_step_wizard(dry_run)


def run_seven_step_wizard(dry_run=False):
    """Run a complete 7-step project scaffolding wizard"""
    from datetime import datetime
    import json
    
    print(f"\n{Colors.BOLD}=== 7-Step Project Setup Wizard ==={Colors.ENDC}")
    print("This will guide you through creating a complete project with all configurations.")
    print()
    
    config = {}
    
    # Step 1: Project Basics
    print(f"{Colors.CYAN}Step 1/7: Project Basics{Colors.ENDC}")
    print("-" * 30)
    
    config['name'] = safe_input("Project name: ", "test-project")
    if not config['name']:
        config['name'] = "my-protogear-project"
    
    print("\nProject type:")
    print("1. Web Application")
    print("2. API/Backend Service") 
    print("3. Full-Stack Application")
    print("4. Static Site")
    print("5. Desktop Application")
    
    project_type_choice = safe_input("\nChoose (1-5): ", "1")
    project_types = {
        '1': 'web-app',
        '2': 'api',
        '3': 'fullstack', 
        '4': 'static-site',
        '5': 'desktop'
    }
    config['project_type'] = project_types.get(project_type_choice, 'web-app')
    
    config['description'] = safe_input(f"Description (optional): ", "")
    if not config['description']:
        config['description'] = f"A {config['project_type']} project created with ProtoGear"
    
    # Step 2: Frontend Stack
    print(f"\n{Colors.CYAN}Step 2/7: Frontend Stack{Colors.ENDC}")
    print("-" * 30)
    
    if config['project_type'] in ['web-app', 'fullstack', 'static-site']:
        print("Frontend Framework:")
        print("1. Next.js (React)")
        print("2. Nuxt.js (Vue)")
        print("3. SvelteKit")
        print("4. Astro")
        print("5. React (Vite)")
        print("6. Vue.js")
        print("7. Vanilla JavaScript")
        
        frontend_choice = safe_input("\nChoose (1-7): ", "1")
        frontend_frameworks = {
            '1': 'nextjs',
            '2': 'nuxt', 
            '3': 'sveltekit',
            '4': 'astro',
            '5': 'react',
            '6': 'vue',
            '7': 'vanilla'
        }
        config['frontend_framework'] = frontend_frameworks.get(frontend_choice, 'nextjs')
        
        print("\nCSS Framework:")
        print("1. Tailwind CSS")
        print("2. Bootstrap")
        print("3. Material-UI/MUI")
        print("4. Chakra UI")
        print("5. CSS Modules")
        print("6. Styled Components")
        print("7. Plain CSS")
        
        css_choice = safe_input("\nChoose (1-7): ", "1")
        css_frameworks = {
            '1': 'tailwind',
            '2': 'bootstrap',
            '3': 'mui',
            '4': 'chakra',
            '5': 'css-modules',
            '6': 'styled-components',
            '7': 'plain-css'
        }
        config['css_framework'] = css_frameworks.get(css_choice, 'tailwind')
    else:
        config['frontend_framework'] = 'none'
        config['css_framework'] = 'none'
    
    # Step 3: Backend & Data
    print(f"\n{Colors.CYAN}Step 3/7: Backend & Data{Colors.ENDC}")
    print("-" * 30)
    
    if config['project_type'] in ['api', 'fullstack']:
        print("Backend Framework:")
        print("1. Express.js (Node.js)")
        print("2. FastAPI (Python)")
        print("3. Django (Python)")
        print("4. Next.js API Routes")
        print("5. Nuxt Server API")
        print("6. None")
        
        backend_choice = safe_input("\nChoose (1-6): ", "1")
        backend_frameworks = {
            '1': 'express',
            '2': 'fastapi',
            '3': 'django', 
            '4': 'nextjs-api',
            '5': 'nuxt-api',
            '6': 'none'
        }
        config['backend_framework'] = backend_frameworks.get(backend_choice, 'express')
        
        if config['backend_framework'] != 'none':
            print("\nDatabase:")
            print("1. PostgreSQL")
            print("2. MySQL")
            print("3. SQLite")
            print("4. MongoDB")
            print("5. Supabase")
            print("6. None")
            
            db_choice = safe_input("\nChoose (1-6): ", "1")
            databases = {
                '1': 'postgresql',
                '2': 'mysql',
                '3': 'sqlite',
                '4': 'mongodb',
                '5': 'supabase',
                '6': 'none'
            }
            config['database'] = databases.get(db_choice, 'postgresql')
            
            if config['database'] != 'none':
                print("\nORM/Query Builder:")
                print("1. Prisma")
                print("2. Drizzle")
                print("3. TypeORM")
                print("4. Sequelize")
                print("5. Mongoose (for MongoDB)")
                print("6. Raw SQL")
                
                orm_choice = safe_input("\nChoose (1-6): ", "1")
                orms = {
                    '1': 'prisma',
                    '2': 'drizzle',
                    '3': 'typeorm',
                    '4': 'sequelize',
                    '5': 'mongoose',
                    '6': 'raw'
                }
                config['orm'] = orms.get(orm_choice, 'prisma')
            else:
                config['orm'] = 'none'
        else:
            config['database'] = 'none'
            config['orm'] = 'none'
    else:
        config['backend_framework'] = 'none'
        config['database'] = 'none'
        config['orm'] = 'none'
    
    # Step 4: Development Tools
    print(f"\n{Colors.CYAN}Step 4/7: Development Tools{Colors.ENDC}")
    print("-" * 30)
    
    print("Package Manager:")
    print("1. npm")
    print("2. pnpm")
    print("3. yarn")
    print("4. bun")
    
    pm_choice = safe_input("\nChoose (1-4): ", "1")
    package_managers = {
        '1': 'npm',
        '2': 'pnpm',
        '3': 'yarn',
        '4': 'bun'
    }
    config['package_manager'] = package_managers.get(pm_choice, 'npm')
    
    print("\nTesting Framework:")
    print("1. Vitest")
    print("2. Jest")
    print("3. Playwright")
    print("4. Cypress")
    print("5. None")
    
    test_choice = safe_input("\nChoose (1-5): ", "1")
    test_frameworks = {
        '1': 'vitest',
        '2': 'jest',
        '3': 'playwright',
        '4': 'cypress',
        '5': 'none'
    }
    config['testing_framework'] = test_frameworks.get(test_choice, 'vitest')
    
    # Step 5: Features & Services
    print(f"\n{Colors.CYAN}Step 5/7: Features & Services{Colors.ENDC}")
    print("-" * 30)
    
    print("Additional Features (enter numbers separated by commas, or 'none'):")
    print("1. TypeScript")
    print("2. ESLint + Prettier")
    print("3. Husky (Git hooks)")
    print("4. Docker")
    print("5. PWA Support")
    print("6. i18n (Internationalization)")
    print("7. Analytics")
    print("8. Authentication")
    
    features_input = safe_input("\nChoose features (e.g., '1,2,3' or 'none'): ", "1,2")
    features = []
    if features_input.lower() != 'none':
        feature_map = {
            '1': 'typescript',
            '2': 'linting',
            '3': 'git-hooks',
            '4': 'docker',
            '5': 'pwa',
            '6': 'i18n',
            '7': 'analytics',
            '8': 'auth'
        }
        for num in features_input.split(','):
            num = num.strip()
            if num in feature_map:
                features.append(feature_map[num])
    
    config['features'] = features
    
    # Step 6: Deployment
    print(f"\n{Colors.CYAN}Step 6/7: Deployment{Colors.ENDC}")
    print("-" * 30)
    
    print("Deployment Target:")
    print("1. Vercel")
    print("2. Netlify")
    print("3. GitHub Pages")
    print("4. Heroku")
    print("5. Docker")
    print("6. Custom/Self-hosted")
    print("7. None (local development only)")
    
    deploy_choice = safe_input("\nChoose (1-7): ", "1")
    deployment_targets = {
        '1': 'vercel',
        '2': 'netlify',
        '3': 'github-pages',
        '4': 'heroku',
        '5': 'docker',
        '6': 'custom',
        '7': 'none'
    }
    config['deployment'] = deployment_targets.get(deploy_choice, 'vercel')
    
    # Step 7: ProtoGear Agent Framework
    print(f"\n{Colors.CYAN}Step 7/7: ProtoGear Agent Framework{Colors.ENDC}")
    print("-" * 30)
    
    print("Agent Workflow Configuration:")
    print("1. Basic - Essential agents only")
    print("2. Standard - Development-focused agents")  
    print("3. Complete - Full agent ecosystem")
    
    agent_choice = safe_input("\nChoose (1-3): ", "2")
    agent_configs = {
        '1': 'basic',
        '2': 'standard',
        '3': 'complete'
    }
    config['agent_config'] = agent_configs.get(agent_choice, 'standard')
    
    # Show configuration summary
    print(f"\n{Colors.BOLD}=== Configuration Summary ==={Colors.ENDC}")
    print(f"Project: {config['name']} ({config['project_type']})")
    print(f"Frontend: {config.get('frontend_framework', 'none')}")
    print(f"Backend: {config.get('backend_framework', 'none')}")
    print(f"Database: {config.get('database', 'none')}")
    print(f"Package Manager: {config['package_manager']}")
    print(f"Features: {', '.join(config['features']) if config['features'] else 'none'}")
    print(f"Deployment: {config['deployment']}")
    print(f"Agent Config: {config['agent_config']}")
    
    if not dry_run:
        confirm = safe_input(f"\n{Colors.GREEN}Create project with this configuration? (Y/n): {Colors.ENDC}", "Y")
        if confirm.lower() in ['n', 'no']:
            return {'status': 'cancelled'}
    
    # Create the project
    return create_project_from_config(config, dry_run)


def create_project_from_config(config, dry_run=False):
    """Create project based on wizard configuration"""
    from datetime import datetime
    import json
    
    if dry_run:
        print(f"\n{Colors.YELLOW}=== DRY RUN - Files that would be created ==={Colors.ENDC}")
        print(f"Project: {config['name']}/")
        print("  src/")
        print("  tests/")
        print("  docs/")
        print("  package.json")
        print("  README.md") 
        print("  AGENTS.md")
        print("  PROJECT_STATUS.md")
        
        if 'typescript' in config['features']:
            print("  tsconfig.json")
        if 'docker' in config['features']:
            print("  Dockerfile")
            print("  docker-compose.yml")
        if 'linting' in config['features']:
            print("  .eslintrc.js")
            print("  .prettierrc")
        
        return {
            'status': 'success',
            'dry_run': True,
            'config': config
        }
    
    project_path = Path(config['name'])
    
    if project_path.exists():
        print(f"{Colors.WARNING}Directory '{config['name']}' already exists.{Colors.ENDC}")
        return {'status': 'error', 'error': 'Directory already exists'}
    
    try:
        # Create project directory
        project_path.mkdir()
        
        # Create basic structure
        (project_path / "src").mkdir()
        (project_path / "tests").mkdir()
        (project_path / "docs").mkdir()
        
        # Create package.json
        package_json = {
            "name": config['name'],
            "version": "0.1.0",
            "description": config['description'],
            "main": "src/index.js",
            "scripts": {
                "dev": "echo 'Add your dev script here'",
                "build": "echo 'Add your build script here'",
                "start": "echo 'Add your start script here'",
                "test": "echo 'Add your test script here'"
            },
            "keywords": ["protogear"],
            "author": "",
            "license": "MIT"
        }
        
        # Add framework-specific scripts
        if config['frontend_framework'] == 'nextjs':
            package_json['scripts'].update({
                "dev": "next dev",
                "build": "next build", 
                "start": "next start"
            })
        elif config['frontend_framework'] == 'nuxt':
            package_json['scripts'].update({
                "dev": "nuxt dev",
                "build": "nuxt build",
                "start": "nuxt preview"
            })
        
        with open(project_path / "package.json", 'w') as f:
            json.dump(package_json, f, indent=2)
        
        # Create README
        readme_content = f"""# {config['name']}

{config['description']}

## Technology Stack

- **Type**: {config['project_type']}
- **Frontend**: {config.get('frontend_framework', 'none')}
- **Backend**: {config.get('backend_framework', 'none')}
- **Database**: {config.get('database', 'none')}
- **Package Manager**: {config['package_manager']}

## Features

{chr(10).join(f"- {feature}" for feature in config['features']) if config['features'] else "- Basic setup"}

## Getting Started

```bash
{config['package_manager']} install
{config['package_manager']} run dev
```

## ProtoGear Integration

This project includes ProtoGear's AI agent workflow system:

- `AGENTS.md` - AI agent integration guide
- `PROJECT_STATUS.md` - Project state tracking

---

*Created with ProtoGear v3.0*
"""
        
        (project_path / "README.md").write_text(readme_content)
        
        # Create ProtoGear agent files
        agents_content = f"""# AGENTS.md - {config['name']}

> **ProtoGear Agent Framework Integration**
> **Project Type**: {config['project_type']}
> **Frontend**: {config.get('frontend_framework', 'none')}
> **Backend**: {config.get('backend_framework', 'none')}

## Framework Activation

This project was created with ProtoGear's 7-step wizard and includes full AI agent workflow integration.

## Technology Stack

- Frontend: {config.get('frontend_framework', 'none')}
- Backend: {config.get('backend_framework', 'none')}
- Database: {config.get('database', 'none')}
- Package Manager: {config['package_manager']}
- Features: {', '.join(config['features']) if config['features'] else 'none'}

## Agent Configuration: {config['agent_config'].title()}

{get_agent_description(config['agent_config'])}

## Development Workflow

1. Make changes to source code
2. AI agents analyze changes based on your technology stack
3. Receive context-aware suggestions and improvements
4. Run tests and quality checks
5. Update documentation automatically

---
*Powered by ProtoGear Agent Framework v3.0*
"""
        
        (project_path / "AGENTS.md").write_text(agents_content)
        
        # Create PROJECT_STATUS.md
        status_content = f"""# PROJECT STATUS - {config['name']}

> **Single Source of Truth** for project state

## Current State

```yaml
project_phase: "Setup Complete"
protogear_enabled: true
frontend_framework: "{config.get('frontend_framework', 'none')}"
backend_framework: "{config.get('backend_framework', 'none')}"
database: "{config.get('database', 'none')}"
project_type: "{config['project_type']}"
creation_date: "{datetime.now().strftime('%Y-%m-%d')}"
agent_config: "{config['agent_config']}"
```

## Technology Configuration

| Component | Selection | Status |
|-----------|-----------|--------|
| Frontend | {config.get('frontend_framework', 'none')} | Configured |
| Backend | {config.get('backend_framework', 'none')} | Configured |
| Database | {config.get('database', 'none')} | Configured |
| Package Manager | {config['package_manager']} | Configured |
| Testing | {config.get('testing_framework', 'none')} | Configured |
| Deployment | {config['deployment']} | Configured |

## Features Enabled

{chr(10).join(f"- {feature}" for feature in config['features']) if config['features'] else "- Basic setup only"}

## Completed Tasks

- [x] 7-step wizard configuration completed
- [x] Project structure created
- [x] Package.json configured
- [x] ProtoGear Agent Framework integrated
- [x] Documentation generated

## Next Steps

1. Run `{config['package_manager']} install` to install dependencies
2. Configure your chosen frameworks and databases
3. Start development with `{config['package_manager']} run dev`
4. Review and customize agent configuration in AGENTS.md

---
*Created with ProtoGear 7-Step Wizard v3.0*
"""
        
        (project_path / "PROJECT_STATUS.md").write_text(status_content)
        
        # Create additional config files based on selections
        if 'typescript' in config['features']:
            tsconfig = {
                "compilerOptions": {
                    "target": "es5",
                    "lib": ["dom", "dom.iterable", "es6"],
                    "allowJs": True,
                    "skipLibCheck": True,
                    "esModuleInterop": True,
                    "allowSyntheticDefaultImports": True,
                    "strict": True,
                    "forceConsistentCasingInFileNames": True,
                    "moduleResolution": "node",
                    "resolveJsonModule": True,
                    "isolatedModules": True,
                    "noEmit": True,
                    "jsx": "react-jsx"
                },
                "include": ["src", "tests"],
                "exclude": ["node_modules"]
            }
            with open(project_path / "tsconfig.json", 'w') as f:
                json.dump(tsconfig, f, indent=2)
        
        if 'docker' in config['features']:
            dockerfile_content = """FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"""
            (project_path / "Dockerfile").write_text(dockerfile_content)
        
        return {
            'status': 'success',
            'path': str(project_path.absolute()),
            'project_name': config['name'],
            'config': config
        }
        
    except Exception as e:
        # Clean up on error
        if project_path.exists():
            import shutil
            shutil.rmtree(project_path)
        return {'status': 'error', 'error': str(e)}


def get_agent_description(agent_config):
    """Get agent configuration description"""
    descriptions = {
        'basic': """**Basic Agent Setup**
- Code Analyzer: Reviews code quality and suggests improvements
- Documentation Agent: Maintains README and code documentation
- Testing Assistant: Helps with test creation and maintenance""",
        
        'standard': """**Standard Agent Setup**  
- Architect Agent: Analyzes project structure and suggests improvements
- Frontend Developer: Specializes in UI/UX and frontend technologies
- Backend Developer: Handles server-side logic and API development
- Quality Assurance: Ensures code quality and testing standards
- Documentation Agent: Maintains comprehensive project documentation""",
        
        'complete': """**Complete Agent Ecosystem**
- Architect Agent: System design and architecture decisions
- Frontend Developer Agent: UI/UX implementation and optimization
- Backend Developer Agent: Server-side development and APIs
- DevOps Engineer Agent: Deployment and infrastructure management
- Security Specialist Agent: Security analysis and hardening
- Performance Engineer Agent: Optimization and monitoring
- Quality Assurance Agent: Testing and quality control
- Technical Writer Agent: Documentation and user guides
- Product Manager Agent: Feature planning and user experience"""
    }
    return descriptions.get(agent_config, descriptions['standard'])


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


def run_simple_protogear_init(dry_run=False):
    """Simple ProtoGear initialization function"""
    from datetime import datetime
    
    print(f"\n{Colors.BOLD}ProtoGear Project Initialization{Colors.ENDC}")
    print("=" * 50)
    
    print(f"\n{Colors.CYAN}What would you like to do?{Colors.ENDC}")
    print("1. Agent Framework Only - Add ProtoGear to existing project")
    print("2. Full Project Scaffolding - Create complete project from scratch")
    
    while True:
        try:
            choice = safe_input(f"\n{Colors.GREEN}Choice (1/2): {Colors.ENDC}", "1")

            if choice == '1':
                result = setup_agent_framework_only(dry_run=dry_run)
                break
            elif choice == '2':
                result = setup_full_project_scaffolding(dry_run=dry_run)
                break
            elif choice.lower() in ['q', 'quit', 'exit']:
                return {'status': 'cancelled'}
            else:
                print(f"{Colors.WARNING}Please enter 1 or 2 (or 'q' to quit){Colors.ENDC}")
        except KeyboardInterrupt:
            return {'status': 'cancelled'}
    
    # Show results
    if result['status'] == 'success':
        if result.get('dry_run'):
            print(f"\n{Colors.GREEN}SUCCESS: Dry run completed successfully!{Colors.ENDC}")
        else:
            print(f"\n{Colors.GREEN}SUCCESS: ProtoGear setup completed successfully!{Colors.ENDC}")
            
            if result.get('files_created'):
                print(f"\n{Colors.CYAN}Files created:{Colors.ENDC}")
                for file in result['files_created']:
                    print(f"  + {file}")
            
            if result.get('path'):
                print(f"\n{Colors.CYAN}Project location:{Colors.ENDC} {result['path']}")
                
            print(f"\n{Colors.YELLOW}Next steps:{Colors.ENDC}")
            if result.get('mode') == 'agent-framework-only':
                print("  1. Review AGENTS.md to understand AI agent capabilities")
                print("  2. Check PROJECT_STATUS.md for project state tracking")
                print("  3. Continue development with AI-powered assistance")
            elif result.get('mode') == 'full-project':
                print(f"  1. cd {result.get('project_name', 'your-project')}")
                print("  2. npm install")
                print("  3. npm start")
                print("  4. Review AGENTS.md for AI development assistance")
    
    return result


def run_wizard(wizard_type: str, template: Optional[str] = None):
    """Run the selected wizard"""
    try:
        # Import the appropriate wizard
        if wizard_type == 'basic':
            from .setup_wizard import SetupWizard
            print(f"\n{Colors.YELLOW}⚡ Starting Quick Start Wizard...{Colors.ENDC}\n")
            wizard = SetupWizard()
        elif wizard_type == 'enhanced':
            from .enhanced_setup_wizard import EnhancedSetupWizard
            print(f"\n{Colors.YELLOW}🌐 Starting Modern Web Wizard...{Colors.ENDC}\n")
            wizard = EnhancedSetupWizard()
        elif wizard_type == 'ultimate':
            from .ultimate_setup_wizard import UltimateSetupWizard
            print(f"\n{Colors.YELLOW}🏢 Starting Enterprise Wizard...{Colors.ENDC}\n")
            wizard = UltimateSetupWizard()
        elif wizard_type == 'multiplatform':
            from .multiplatform_wizard import MultiPlatformSetupWizard
            print(f"\n{Colors.YELLOW}📱 Starting Multi-Platform Wizard...{Colors.ENDC}\n")
            wizard = MultiPlatformSetupWizard()
        elif wizard_type == 'agent_framework_only':
            from .agent_framework_wizard import AgentFrameworkWizard
            print(f"\n{Colors.YELLOW}⚙️ Starting Agent Framework Wizard...{Colors.ENDC}\n")
            wizard = AgentFrameworkWizard()
        else:
            print(f"{Colors.FAIL}Unknown wizard type: {wizard_type}{Colors.ENDC}")
            return False
        
        # Run the wizard
        result = wizard.run_interactive()
        
        if result['status'] == 'success':
            print(f"\n{Colors.GREEN}{'=' * 80}{Colors.ENDC}")
            print(f"{Colors.GREEN}{Colors.BOLD}✨ Project Created Successfully!{Colors.ENDC}")
            print(f"{Colors.GREEN}{'=' * 80}{Colors.ENDC}")
            
            if result.get('path'):
                print(f"\n📁 Location: {Colors.CYAN}{result['path']}{Colors.ENDC}")
            
            print(f"\n{Colors.YELLOW}🚀 Your project is ready!{Colors.ENDC}")
            print(f"{Colors.GRAY}Check the project directory for next steps and documentation.{Colors.ENDC}")
            
            return True
        else:
            if result['status'] == 'cancelled':
                print(f"\n{Colors.YELLOW}Setup cancelled by user.{Colors.ENDC}")
            else:
                print(f"\n{Colors.FAIL}Setup failed: {result.get('error', 'Unknown error')}{Colors.ENDC}")
            return False
            
    except ImportError as e:
        print(f"{Colors.FAIL}Error loading wizard: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Make sure all Proto Gear components are installed.{Colors.ENDC}")
        return False
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Setup interrupted by user.{Colors.ENDC}")
        return False
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        print(f"{Colors.YELLOW}Please report this issue on GitHub.{Colors.ENDC}")
        return False


def main():
    """Main entry point for Proto Gear"""
    # Add argument parsing
    parser = argparse.ArgumentParser(description="Proto Gear - The Ultimate Project Framework Generator")
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Main 'init' command
    init_parser = subparsers.add_parser('init', help='Initialize a new project')
    init_parser.add_argument('--dry-run', action='store_true', help='Simulate without creating files')
    
    # Legacy wizard argument for backward compatibility
    parser.add_argument(
        "--wizard", 
        type=str, 
        help="Directly run a specific wizard (e.g., 'agent_framework_only')",
        choices=['basic', 'enhanced', 'ultimate', 'multiplatform', 'ai', 'templates', 'agent_framework_only']
    )
    
    args = parser.parse_args()

    try:
        # Handle 'init' command
        if args.command == 'init':
            # Run the new unified ProtoGear wizard
            try:
                # Import the simple ProtoGear init function
                result = run_simple_protogear_init(dry_run=args.dry_run)
                
                if result['status'] == 'success':
                    print(f"\n{Colors.GREEN}ProtoGear initialization complete!{Colors.ENDC}")
                else:
                    print(f"\n{Colors.FAIL}Initialization failed: {result.get('error', 'Unknown error')}{Colors.ENDC}")
                    sys.exit(1)
                    
            except ImportError as e:
                print(f"{Colors.FAIL}Error loading ProtoGear wizard: {e}{Colors.ENDC}")
                sys.exit(1)
            
            sys.exit(0)
        
        # Show splash screen only if not running a direct wizard
        if not args.wizard:
            show_splash_screen()
        
        # Welcome message
        print(f"{Colors.GREEN}Welcome to Proto Gear!{Colors.ENDC}")
        print(f"{Colors.GRAY}Let's create something amazing together.{Colors.ENDC}")
        print()
        
        if args.wizard:
            # Run specific wizard directly
            if args.wizard == 'templates':
                template = show_templates_menu()
                if template:
                    run_wizard('ultimate', template)
            elif args.wizard == 'ai':
                ai_recommendation = show_ai_assistant()
                if ai_recommendation:
                    run_wizard(ai_recommendation)
            else:
                run_wizard(args.wizard)
            
            # Exit after running direct wizard
            print_farewell()
            sys.exit(0)

        # Main interaction loop (if not using direct wizard)
        while True:
            # Show wizard selection menu
            wizard_choice = show_wizard_menu()
            
            if wizard_choice == 'agent_framework_only':
                # Show Agent Framework Only wizard
                run_wizard('agent_framework_only')
                break
            elif wizard_choice == 'templates': 
                template = show_templates_menu()
                if template:
                    run_wizard('ultimate', template)
                    break
            elif wizard_choice == 'help': 
                show_help()
            elif wizard_choice == 'ai': # Moved AI assistant handling here
                ai_recommendation = show_ai_assistant()
                if ai_recommendation:
                    run_wizard(ai_recommendation)
                    break
            elif wizard_choice:
                # Run selected wizard
                if run_wizard(wizard_choice):
                    break
            
            # Ask if user wants to create another project
            print()
            another = input(f"{Colors.GREEN}Would you like to create another project? (y/n) [{Colors.ENDC}n{Colors.GREEN}]: {Colors.ENDC}").strip().lower()
            if another not in ['y', 'yes']:
                break
            clear_screen()
        
        # Farewell
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