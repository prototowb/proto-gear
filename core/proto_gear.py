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

# ASCII Art variations for Proto Gear
PROTO_GEAR_LOGOS = [
    """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   ██████╗ ██████╗  ██████╗ ████████╗ ██████╗                ║
    ║   ██╔══██╗██╔══██╗██╔═══██╗╚══██╔══╝██╔═══██╗               ║
    ║   ██████╔╝██████╔╝██║   ██║   ██║   ██║   ██║               ║
    ║   ██╔═══╝ ██╔══██╗██║   ██║   ██║   ██║   ██║               ║
    ║   ██║     ██║  ██║╚██████╔╝   ██║   ╚██████╔╝               ║
    ║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝    ╚═╝    ╚═════╝                ║
    ║                                                               ║
    ║    ██████╗ ███████╗ █████╗ ██████╗                          ║
    ║   ██╔════╝ ██╔════╝██╔══██╗██╔══██╗                         ║
    ║   ██║  ███╗█████╗  ███████║██████╔╝                         ║
    ║   ██║   ██║██╔══╝  ██╔══██║██╔══██╗                         ║
    ║   ╚██████╔╝███████╗██║  ██║██║  ██║                         ║
    ║    ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝                         ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """,
    """
    ┌─────────────────────────────────────────────────────────────┐
    │                                                             │
    │   ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄     │
    │  ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌    │
    │  ▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌ ▀▀▀▀█░█▀▀▀▀     │
    │  ▐░▌       ▐░▌▐░▌       ▐░▌▐░▌       ▐░▌     ▐░▌         │
    │  ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌     ▐░▌         │
    │  ▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌     ▐░▌         │
    │  ▐░█▀▀▀▀▀▀▀▀▀ ▐░█▀▀▀▀█░█▀▀ ▐░▌       ▐░▌     ▐░▌         │
    │  ▐░▌          ▐░▌     ▐░▌  ▐░▌       ▐░▌     ▐░▌         │
    │  ▐░▌          ▐░▌      ▐░▌ ▐░█▄▄▄▄▄▄▄█░▌     ▐░▌         │
    │  ▐░▌          ▐░▌       ▐░▌▐░░░░░░░░░░░▌     ▐░▌         │
    │   ▀            ▀         ▀  ▀▀▀▀▀▀▀▀▀▀▀       ▀          │
    │                                                             │
    │     G E A R   ⚙️  Framework Generator v3.0                  │
    │                                                             │
    └─────────────────────────────────────────────────────────────┘
    """
]

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
        }
    ]
    
    for i, wizard in enumerate(wizards, 1):
        print(f"{Colors.CYAN}{i}.{Colors.ENDC} {wizard['icon']}  {Colors.BOLD}{wizard['name']}{Colors.ENDC}")
        print(f"    {Colors.GRAY}{wizard['description']}{Colors.ENDC}")
        print(f"    {Colors.YELLOW}Coverage: {wizard['coverage']} • Time: {wizard['time']}{Colors.ENDC}")
        print()
    
    print(f"{Colors.CYAN}6.{Colors.ENDC} 📚  {Colors.BOLD}Browse Templates{Colors.ENDC}")
    print(f"    {Colors.GRAY}Start from pre-configured project templates{Colors.ENDC}")
    print()
    
    print(f"{Colors.CYAN}7.{Colors.ENDC} ❓  {Colors.BOLD}Help & Documentation{Colors.ENDC}")
    print(f"    {Colors.GRAY}Learn more about Proto Gear{Colors.ENDC}")
    print()
    
    print(f"{Colors.CYAN}0.{Colors.ENDC} 🚪  {Colors.BOLD}Exit{Colors.ENDC}")
    print(f"    {Colors.GRAY}Exit Proto Gear{Colors.ENDC}")
    
    print("\n" + "─" * 80 + "\n")
    
    while True:
        try:
            choice = input(f"{Colors.GREEN}Enter your choice (0-7): {Colors.ENDC}").strip()
            
            if choice == '0':
                print_farewell()
                sys.exit(0)
            elif choice in ['1', '2', '3', '4']:
                return wizards[int(choice) - 1]['wizard']
            elif choice == '5':
                return 'ai'
            elif choice == '6':
                return 'templates'
            elif choice == '7':
                show_help()
                return show_wizard_menu()  # Show menu again after help
            else:
                print(f"{Colors.WARNING}Please enter a valid choice (0-7){Colors.ENDC}")
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
        print(f"{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        return False


def main():
    """Main entry point for Proto Gear"""
    try:
        # Show splash screen
        show_splash_screen()
        
        # Welcome message
        print(f"{Colors.GREEN}Welcome to Proto Gear!{Colors.ENDC}")
        print(f"{Colors.GRAY}Let's create something amazing together.{Colors.ENDC}")
        print()
        
        # Main interaction loop
        while True:
            # Show wizard selection menu
            wizard_choice = show_wizard_menu()
            
            if wizard_choice == 'templates':
                # Show templates menu
                template = show_templates_menu()
                if template:
                    # Use ultimate wizard with selected template
                    run_wizard('ultimate', template)
                    break
            elif wizard_choice == 'ai':
                # Show AI assistant
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