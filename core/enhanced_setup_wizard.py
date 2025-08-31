"""
Enhanced Setup Wizard for Agent Framework
Supports modern web frameworks, TypeScript, i18n, and more
"""

import os
import json
import yaml
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import re
from enum import Enum


class ProjectType(Enum):
    """Extended project types"""
    WEB_APP = "web-app"
    STATIC_SITE = "static-site"
    BLOG = "blog"
    API = "api"
    CLI = "cli"
    LIBRARY = "library"
    MICROSERVICE = "microservice"
    FULLSTACK = "fullstack"
    MOBILE = "mobile"
    DESKTOP = "desktop"


class Framework(Enum):
    """Modern web frameworks"""
    ASTRO = "astro"
    NEXTJS = "nextjs"
    NUXT = "nuxt"
    SVELTEKIT = "sveltekit"
    REMIX = "remix"
    GATSBY = "gatsby"
    VITE = "vite"
    EXPRESS = "express"
    FASTAPI = "fastapi"
    DJANGO = "django"
    RAILS = "rails"
    NONE = "none"


class UIFramework(Enum):
    """UI component frameworks"""
    REACT = "react"
    VUE = "vue"
    SVELTE = "svelte"
    SOLID = "solid"
    PREACT = "preact"
    ALPINE = "alpine"
    NONE = "none"


class CSSFramework(Enum):
    """CSS frameworks and tools"""
    TAILWIND = "tailwind"
    BOOTSTRAP = "bootstrap"
    BULMA = "bulma"
    MATERIAL = "material-ui"
    CHAKRA = "chakra-ui"
    MANTINE = "mantine"
    CSS_MODULES = "css-modules"
    STYLED_COMPONENTS = "styled-components"
    SASS = "sass"
    POSTCSS = "postcss"
    NONE = "none"


class PackageManager(Enum):
    """Package managers"""
    NPM = "npm"
    PNPM = "pnpm"
    YARN = "yarn"
    BUN = "bun"
    

class TestFramework(Enum):
    """Testing frameworks"""
    VITEST = "vitest"
    JEST = "jest"
    PLAYWRIGHT = "playwright"
    CYPRESS = "cypress"
    PYTEST = "pytest"
    MOCHA = "mocha"
    NONE = "none"


class CMSOption(Enum):
    """CMS options"""
    KEYSTATIC = "keystatic"
    STRAPI = "strapi"
    SANITY = "sanity"
    CONTENTFUL = "contentful"
    DIRECTUS = "directus"
    PAYLOAD = "payload"
    MDX = "mdx"
    CONTENTLAYER = "contentlayer"
    NONE = "none"


class DeploymentTarget(Enum):
    """Deployment platforms"""
    VERCEL = "vercel"
    NETLIFY = "netlify"
    CLOUDFLARE = "cloudflare-pages"
    GITHUB_PAGES = "github-pages"
    HEROKU = "heroku"
    AWS = "aws"
    DOCKER = "docker"
    VPS = "vps"
    NONE = "none"


class EnhancedProjectConfig:
    """Enhanced project configuration with modern options"""
    
    def __init__(self):
        self.name = ""
        self.project_type = ProjectType.WEB_APP
        self.description = ""
        self.version = "0.1.0"
        self.author = ""
        self.license = "MIT"
        
        # Language settings
        self.language = "typescript"  # typescript or javascript
        self.strict_mode = True
        
        # Framework choices
        self.framework = Framework.NONE
        self.ui_framework = UIFramework.NONE
        self.css_framework = CSSFramework.TAILWIND
        
        # Package management
        self.package_manager = PackageManager.NPM
        
        # Testing
        self.test_framework = TestFramework.VITEST
        self.e2e_framework = TestFramework.PLAYWRIGHT
        self.coverage_threshold = 80
        
        # i18n
        self.i18n_enabled = False
        self.default_locale = "en"
        self.locales = ["en"]
        
        # CMS
        self.cms = CMSOption.NONE
        
        # Database
        self.database = None  # postgresql, mysql, sqlite, mongodb, etc.
        self.orm = None  # prisma, drizzle, typeorm, etc.
        
        # Deployment
        self.deployment_target = DeploymentTarget.NONE
        
        # Git
        self.git_enabled = True
        self.github_actions = False
        
        # Additional features
        self.pwa = False
        self.docker = False
        self.eslint = True
        self.prettier = True
        self.husky = True
        self.commitlint = False
        
        # Compliance
        self.gdpr = False
        self.accessibility_level = "AA"  # WCAG 2.1 level
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "project": {
                "name": self.name,
                "type": self.project_type.value,
                "description": self.description,
                "version": self.version,
                "author": self.author,
                "license": self.license
            },
            "tech_stack": {
                "language": self.language,
                "strict_mode": self.strict_mode,
                "framework": self.framework.value,
                "ui_framework": self.ui_framework.value,
                "css_framework": self.css_framework.value,
                "package_manager": self.package_manager.value
            },
            "testing": {
                "framework": self.test_framework.value,
                "e2e": self.e2e_framework.value,
                "coverage_threshold": self.coverage_threshold
            },
            "i18n": {
                "enabled": self.i18n_enabled,
                "default_locale": self.default_locale,
                "locales": self.locales
            },
            "cms": self.cms.value,
            "database": {
                "type": self.database,
                "orm": self.orm
            },
            "deployment": {
                "target": self.deployment_target.value,
                "docker": self.docker
            },
            "development": {
                "git": self.git_enabled,
                "github_actions": self.github_actions,
                "eslint": self.eslint,
                "prettier": self.prettier,
                "husky": self.husky,
                "commitlint": self.commitlint
            },
            "features": {
                "pwa": self.pwa,
                "gdpr": self.gdpr,
                "accessibility": self.accessibility_level
            }
        }


class EnhancedSetupWizard:
    """Enhanced interactive setup wizard with modern web development support"""
    
    def __init__(self, base_path: str = ".", dry_run: bool = False):
        """
        Initialize the enhanced setup wizard
        
        Args:
            base_path: Base directory for project creation
            dry_run: If True, don't create actual files
        """
        self.base_path = Path(base_path)
        self.dry_run = dry_run
        self.config = EnhancedProjectConfig()
        self.templates_path = Path(__file__).parent.parent / "templates"
    
    def run_interactive(self) -> Dict[str, Any]:
        """Run the enhanced wizard in interactive mode"""
        print("\n" + "=" * 60)
        print("🧙 Enhanced Agent Framework Setup Wizard")
        print("=" * 60)
        
        try:
            # Project basics
            self._configure_basics()
            
            # Framework selection
            self._configure_framework()
            
            # Language and tooling
            self._configure_language()
            
            # Styling
            self._configure_styling()
            
            # Testing
            self._configure_testing()
            
            # i18n
            self._configure_i18n()
            
            # CMS
            self._configure_cms()
            
            # Database
            self._configure_database()
            
            # Deployment
            self._configure_deployment()
            
            # Additional features
            self._configure_features()
            
            # Show summary
            self._show_summary()
            
            # Confirm and create
            confirm = input("\n🚀 Create project with this configuration? (y/n) [y]: ") or 'y'
            if confirm.lower() not in ['y', 'yes']:
                return {'status': 'cancelled'}
            
            # Create the project
            result = self.create_project()
            
            if result['status'] == 'success':
                print(f"\n✅ Project created successfully!")
                print(f"📁 Location: {result.get('path')}")
                self._show_next_steps()
            
            return result
            
        except KeyboardInterrupt:
            print("\n\n⚠️  Setup cancelled by user")
            return {'status': 'cancelled'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _configure_basics(self):
        """Configure basic project settings"""
        print("\n📝 Project Configuration")
        print("-" * 40)
        
        # Project name
        name = input("Project name: ")
        self.config.name = self._sanitize_name(name)
        
        # Project type
        print("\n📦 Project type:")
        for i, ptype in enumerate(ProjectType, 1):
            print(f"  {i}. {ptype.value}")
        
        choice = input("Choice (1-10) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(ProjectType):
            self.config.project_type = list(ProjectType)[int(choice) - 1]
        
        # Description
        self.config.description = input("\nProject description (optional): ") or ""
        
        # Author
        self.config.author = input("Author name (optional): ") or ""
    
    def _configure_framework(self):
        """Configure framework selection"""
        print("\n🛠️  Framework Selection")
        print("-" * 40)
        
        # Show relevant frameworks based on project type
        if self.config.project_type in [ProjectType.WEB_APP, ProjectType.STATIC_SITE, ProjectType.BLOG]:
            print("Frontend framework:")
            frameworks = [Framework.ASTRO, Framework.NEXTJS, Framework.NUXT, 
                         Framework.SVELTEKIT, Framework.REMIX, Framework.GATSBY, 
                         Framework.VITE, Framework.NONE]
        elif self.config.project_type == ProjectType.API:
            print("Backend framework:")
            frameworks = [Framework.EXPRESS, Framework.FASTAPI, Framework.DJANGO, 
                         Framework.RAILS, Framework.NONE]
        else:
            frameworks = [Framework.NONE]
        
        for i, fw in enumerate(frameworks, 1):
            print(f"  {i}. {fw.value}")
        
        choice = input(f"Choice (1-{len(frameworks)}) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(frameworks):
            self.config.framework = frameworks[int(choice) - 1]
        
        # UI framework for certain main frameworks
        if self.config.framework in [Framework.ASTRO, Framework.VITE]:
            print("\n🎨 UI Framework (for interactive components):")
            ui_frameworks = [UIFramework.VUE, UIFramework.REACT, UIFramework.SVELTE, 
                            UIFramework.SOLID, UIFramework.PREACT, UIFramework.NONE]
            
            for i, ui in enumerate(ui_frameworks, 1):
                print(f"  {i}. {ui.value}")
            
            choice = input(f"Choice (1-{len(ui_frameworks)}) [1]: ") or "1"
            if choice.isdigit() and 1 <= int(choice) <= len(ui_frameworks):
                self.config.ui_framework = ui_frameworks[int(choice) - 1]
    
    def _configure_language(self):
        """Configure language and package manager"""
        print("\n💻 Language & Tools")
        print("-" * 40)
        
        # Language choice
        lang = input("Language (typescript/javascript) [typescript]: ") or "typescript"
        self.config.language = lang.lower()
        
        if self.config.language == "typescript":
            strict = input("Strict TypeScript mode? (y/n) [y]: ") or "y"
            self.config.strict_mode = strict.lower() in ['y', 'yes']
        
        # Package manager
        print("\n📦 Package manager:")
        for i, pm in enumerate(PackageManager, 1):
            print(f"  {i}. {pm.value}")
        
        choice = input("Choice (1-4) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(PackageManager):
            self.config.package_manager = list(PackageManager)[int(choice) - 1]
    
    def _configure_styling(self):
        """Configure CSS framework"""
        print("\n🎨 Styling")
        print("-" * 40)
        
        print("CSS Framework:")
        css_frameworks = list(CSSFramework)
        
        for i, css in enumerate(css_frameworks, 1):
            print(f"  {i}. {css.value}")
        
        choice = input(f"Choice (1-{len(css_frameworks)}) [1]: ") or "1"
        if choice.isdigit() and 1 <= int(choice) <= len(css_frameworks):
            self.config.css_framework = css_frameworks[int(choice) - 1]
    
    def _configure_testing(self):
        """Configure testing frameworks"""
        print("\n🧪 Testing Configuration")
        print("-" * 40)
        
        enable = input("Enable testing? (y/n) [y]: ") or "y"
        
        if enable.lower() in ['y', 'yes']:
            # Unit testing
            if self.config.language == "typescript" or self.config.framework != Framework.NONE:
                test_frameworks = [TestFramework.VITEST, TestFramework.JEST, 
                                 TestFramework.MOCHA, TestFramework.NONE]
            else:
                test_frameworks = [TestFramework.PYTEST, TestFramework.NONE]
            
            print("\nUnit testing framework:")
            for i, tf in enumerate(test_frameworks, 1):
                print(f"  {i}. {tf.value}")
            
            choice = input(f"Choice (1-{len(test_frameworks)}) [1]: ") or "1"
            if choice.isdigit() and 1 <= int(choice) <= len(test_frameworks):
                self.config.test_framework = test_frameworks[int(choice) - 1]
            
            # E2E testing
            if self.config.project_type in [ProjectType.WEB_APP, ProjectType.FULLSTACK]:
                print("\nE2E testing framework:")
                e2e_frameworks = [TestFramework.PLAYWRIGHT, TestFramework.CYPRESS, 
                                TestFramework.NONE]
                
                for i, e2e in enumerate(e2e_frameworks, 1):
                    print(f"  {i}. {e2e.value}")
                
                choice = input(f"Choice (1-{len(e2e_frameworks)}) [3]: ") or "3"
                if choice.isdigit() and 1 <= int(choice) <= len(e2e_frameworks):
                    self.config.e2e_framework = e2e_frameworks[int(choice) - 1]
            
            # Coverage threshold
            coverage = input("\nCode coverage threshold (%) [80]: ") or "80"
            self.config.coverage_threshold = int(coverage)
    
    def _configure_i18n(self):
        """Configure internationalization"""
        print("\n🌍 Internationalization (i18n)")
        print("-" * 40)
        
        enable = input("Enable i18n? (y/n) [n]: ") or "n"
        
        if enable.lower() in ['y', 'yes']:
            self.config.i18n_enabled = True
            
            # Default locale
            default = input("Default locale (e.g., en, de, fr) [en]: ") or "en"
            self.config.default_locale = default
            
            # Additional locales
            additional = input("Additional locales (comma-separated, e.g., de,fr): ") or ""
            if additional:
                self.config.locales = [self.config.default_locale] + \
                                     [l.strip() for l in additional.split(',')]
            else:
                self.config.locales = [self.config.default_locale]
    
    def _configure_cms(self):
        """Configure CMS"""
        print("\n📝 Content Management")
        print("-" * 40)
        
        if self.config.project_type in [ProjectType.WEB_APP, ProjectType.STATIC_SITE, 
                                       ProjectType.BLOG, ProjectType.FULLSTACK]:
            print("CMS Option:")
            cms_options = list(CMSOption)
            
            for i, cms in enumerate(cms_options, 1):
                print(f"  {i}. {cms.value}")
            
            choice = input(f"Choice (1-{len(cms_options)}) [{len(cms_options)}]: ") or str(len(cms_options))
            if choice.isdigit() and 1 <= int(choice) <= len(cms_options):
                self.config.cms = cms_options[int(choice) - 1]
    
    def _configure_database(self):
        """Configure database"""
        print("\n💾 Database Configuration")
        print("-" * 40)
        
        if self.config.project_type in [ProjectType.WEB_APP, ProjectType.API, 
                                       ProjectType.FULLSTACK, ProjectType.MICROSERVICE]:
            need_db = input("Configure database? (y/n) [n]: ") or "n"
            
            if need_db.lower() in ['y', 'yes']:
                print("\nDatabase type:")
                databases = ["postgresql", "mysql", "sqlite", "mongodb", "redis", "none"]
                
                for i, db in enumerate(databases, 1):
                    print(f"  {i}. {db}")
                
                choice = input("Choice (1-6) [1]: ") or "1"
                if choice.isdigit() and 1 <= int(choice) <= len(databases):
                    db_choice = databases[int(choice) - 1]
                    self.config.database = db_choice if db_choice != "none" else None
                
                # ORM for SQL databases
                if self.config.database in ["postgresql", "mysql", "sqlite"]:
                    print("\nORM/Query Builder:")
                    orms = ["prisma", "drizzle", "typeorm", "sequelize", "none"]
                    
                    for i, orm in enumerate(orms, 1):
                        print(f"  {i}. {orm}")
                    
                    choice = input("Choice (1-5) [1]: ") or "1"
                    if choice.isdigit() and 1 <= int(choice) <= len(orms):
                        orm_choice = orms[int(choice) - 1]
                        self.config.orm = orm_choice if orm_choice != "none" else None
    
    def _configure_deployment(self):
        """Configure deployment target"""
        print("\n🚀 Deployment Configuration")
        print("-" * 40)
        
        print("Deployment target:")
        targets = list(DeploymentTarget)
        
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target.value}")
        
        choice = input(f"Choice (1-{len(targets)}) [{len(targets)}]: ") or str(len(targets))
        if choice.isdigit() and 1 <= int(choice) <= len(targets):
            self.config.deployment_target = targets[int(choice) - 1]
        
        # Docker
        if self.config.deployment_target in [DeploymentTarget.AWS, DeploymentTarget.VPS, 
                                            DeploymentTarget.DOCKER]:
            docker = input("\nGenerate Docker configuration? (y/n) [y]: ") or "y"
            self.config.docker = docker.lower() in ['y', 'yes']
    
    def _configure_features(self):
        """Configure additional features"""
        print("\n⚙️  Additional Features")
        print("-" * 40)
        
        # Git
        git = input("Initialize Git repository? (y/n) [y]: ") or "y"
        self.config.git_enabled = git.lower() in ['y', 'yes']
        
        if self.config.git_enabled:
            actions = input("Setup GitHub Actions? (y/n) [n]: ") or "n"
            self.config.github_actions = actions.lower() in ['y', 'yes']
        
        # Code quality
        print("\n📋 Code Quality Tools:")
        
        eslint = input("  ESLint? (y/n) [y]: ") or "y"
        self.config.eslint = eslint.lower() in ['y', 'yes']
        
        prettier = input("  Prettier? (y/n) [y]: ") or "y"
        self.config.prettier = prettier.lower() in ['y', 'yes']
        
        husky = input("  Husky (Git hooks)? (y/n) [y]: ") or "y"
        self.config.husky = husky.lower() in ['y', 'yes']
        
        if self.config.husky:
            commitlint = input("  Commitlint? (y/n) [n]: ") or "n"
            self.config.commitlint = commitlint.lower() in ['y', 'yes']
        
        # PWA
        if self.config.project_type in [ProjectType.WEB_APP, ProjectType.FULLSTACK]:
            pwa = input("\n📱 Enable PWA features? (y/n) [n]: ") or "n"
            self.config.pwa = pwa.lower() in ['y', 'yes']
        
        # Compliance
        print("\n🔒 Compliance & Standards:")
        
        gdpr = input("  GDPR compliance setup? (y/n) [n]: ") or "n"
        self.config.gdpr = gdpr.lower() in ['y', 'yes']
        
        a11y = input("  WCAG accessibility level (A/AA/AAA) [AA]: ") or "AA"
        self.config.accessibility_level = a11y.upper()
    
    def _show_summary(self):
        """Show configuration summary"""
        print("\n" + "=" * 60)
        print("📋 Configuration Summary")
        print("=" * 60)
        
        print(f"\n🎯 Project: {self.config.name}")
        print(f"   Type: {self.config.project_type.value}")
        print(f"   Description: {self.config.description or 'N/A'}")
        
        print(f"\n🛠️  Stack:")
        print(f"   Language: {self.config.language}")
        print(f"   Framework: {self.config.framework.value}")
        if self.config.ui_framework != UIFramework.NONE:
            print(f"   UI Framework: {self.config.ui_framework.value}")
        print(f"   CSS: {self.config.css_framework.value}")
        print(f"   Package Manager: {self.config.package_manager.value}")
        
        print(f"\n🧪 Testing:")
        print(f"   Unit: {self.config.test_framework.value}")
        if self.config.e2e_framework != TestFramework.NONE:
            print(f"   E2E: {self.config.e2e_framework.value}")
        print(f"   Coverage: {self.config.coverage_threshold}%")
        
        if self.config.i18n_enabled:
            print(f"\n🌍 i18n:")
            print(f"   Default: {self.config.default_locale}")
            print(f"   Locales: {', '.join(self.config.locales)}")
        
        if self.config.cms != CMSOption.NONE:
            print(f"\n📝 CMS: {self.config.cms.value}")
        
        if self.config.database:
            print(f"\n💾 Database: {self.config.database}")
            if self.config.orm:
                print(f"   ORM: {self.config.orm}")
        
        print(f"\n🚀 Deployment: {self.config.deployment_target.value}")
        
        features = []
        if self.config.git_enabled: features.append("Git")
        if self.config.github_actions: features.append("GitHub Actions")
        if self.config.eslint: features.append("ESLint")
        if self.config.prettier: features.append("Prettier")
        if self.config.husky: features.append("Husky")
        if self.config.pwa: features.append("PWA")
        if self.config.gdpr: features.append("GDPR")
        if self.config.docker: features.append("Docker")
        
        if features:
            print(f"\n⚙️  Features: {', '.join(features)}")
        
        print("=" * 60)
    
    def _show_next_steps(self):
        """Show next steps based on configuration"""
        print("\n🎯 Next Steps:")
        print("-" * 40)
        
        steps = []
        
        # Change directory
        steps.append(f"cd {self.config.name}")
        
        # Install dependencies
        if self.config.package_manager == PackageManager.NPM:
            steps.append("npm install")
        elif self.config.package_manager == PackageManager.PNPM:
            steps.append("pnpm install")
        elif self.config.package_manager == PackageManager.YARN:
            steps.append("yarn install")
        elif self.config.package_manager == PackageManager.BUN:
            steps.append("bun install")
        
        # Framework-specific commands
        if self.config.framework == Framework.ASTRO:
            steps.append("npm run dev  # Start development server")
        elif self.config.framework == Framework.NEXTJS:
            steps.append("npm run dev  # Start Next.js dev server")
        elif self.config.framework == Framework.NUXT:
            steps.append("npm run dev  # Start Nuxt dev server")
        
        # Database setup
        if self.config.orm == "prisma":
            steps.append("npx prisma migrate dev  # Setup database")
        
        # Testing
        if self.config.test_framework != TestFramework.NONE:
            steps.append("npm test  # Run tests")
        
        for i, step in enumerate(steps, 1):
            print(f"  {i}. {step}")
    
    def _sanitize_name(self, name: str) -> str:
        """Sanitize project name"""
        # Remove special characters, keep only alphanumeric and hyphens
        sanitized = re.sub(r'[^a-zA-Z0-9-]', '-', name.lower())
        # Remove multiple consecutive hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        # Remove leading/trailing hyphens
        return sanitized.strip('-')
    
    def create_project(self) -> Dict[str, Any]:
        """Create the project with enhanced configuration"""
        if self.dry_run:
            print("\n🔍 Dry run - no files created")
            return {
                'status': 'success',
                'dry_run': True,
                'config': self.config.to_dict()
            }
        
        project_path = self.base_path / self.config.name
        
        # Check if project already exists
        if project_path.exists():
            return {
                'status': 'error',
                'error': f'Project directory already exists: {project_path}'
            }
        
        try:
            # Create project directory
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Generate project based on framework
            self._generate_project_structure(project_path)
            
            # Create configuration files
            self._create_config_files(project_path)
            
            # Initialize Git if enabled
            if self.config.git_enabled:
                self._initialize_git(project_path)
            
            # Create marker file
            marker_file = project_path / ".agent-framework-initialized"
            marker_file.write_text(
                f"Initialized on {datetime.now().isoformat()}\n"
                f"Framework version: 2.0.0\n"
                f"Enhanced wizard used: yes\n"
            )
            
            return {
                'status': 'success',
                'path': str(project_path),
                'config': self.config.to_dict()
            }
            
        except Exception as e:
            # Rollback - remove project directory
            if project_path.exists():
                shutil.rmtree(project_path)
            
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_project_structure(self, project_path: Path):
        """Generate project structure based on framework"""
        # This would generate framework-specific files
        # For now, create basic structure
        
        # Create source directory
        if self.config.framework in [Framework.ASTRO, Framework.NEXTJS, Framework.NUXT]:
            src_dir = project_path / "src"
            src_dir.mkdir(exist_ok=True)
            
            # Create subdirectories
            (src_dir / "pages").mkdir(exist_ok=True)
            (src_dir / "components").mkdir(exist_ok=True)
            (src_dir / "styles").mkdir(exist_ok=True)
            
            if self.config.i18n_enabled:
                for locale in self.config.locales:
                    (src_dir / "locales" / locale).mkdir(parents=True, exist_ok=True)
        
        # Create public directory
        (project_path / "public").mkdir(exist_ok=True)
        
        # Create test directory
        if self.config.test_framework != TestFramework.NONE:
            (project_path / "tests").mkdir(exist_ok=True)
    
    def _create_config_files(self, project_path: Path):
        """Create configuration files"""
        # Save agent-framework config
        config_file = project_path / f"{self.config.name}.config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(self.config.to_dict(), f, default_flow_style=False)
        
        # Create package.json for JS/TS projects
        if self.config.framework != Framework.NONE or self.config.language in ["typescript", "javascript"]:
            self._create_package_json(project_path)
        
        # Create TypeScript config
        if self.config.language == "typescript":
            self._create_tsconfig(project_path)
        
        # Create framework-specific configs
        self._create_framework_configs(project_path)
        
        # Create linting configs
        if self.config.eslint:
            self._create_eslint_config(project_path)
        
        if self.config.prettier:
            self._create_prettier_config(project_path)
        
        # Create Docker files
        if self.config.docker:
            self._create_docker_files(project_path)
    
    def _create_package_json(self, project_path: Path):
        """Create package.json"""
        package = {
            "name": self.config.name,
            "version": self.config.version,
            "description": self.config.description,
            "author": self.config.author,
            "license": self.config.license,
            "scripts": {},
            "dependencies": {},
            "devDependencies": {}
        }
        
        # Add scripts based on framework
        if self.config.framework == Framework.ASTRO:
            package["scripts"] = {
                "dev": "astro dev",
                "build": "astro build",
                "preview": "astro preview"
            }
        elif self.config.framework == Framework.NEXTJS:
            package["scripts"] = {
                "dev": "next dev",
                "build": "next build",
                "start": "next start"
            }
        
        # Add test scripts
        if self.config.test_framework == TestFramework.VITEST:
            package["scripts"]["test"] = "vitest"
            package["scripts"]["test:coverage"] = "vitest --coverage"
        elif self.config.test_framework == TestFramework.JEST:
            package["scripts"]["test"] = "jest"
            package["scripts"]["test:watch"] = "jest --watch"
        
        package_file = project_path / "package.json"
        with open(package_file, 'w') as f:
            json.dump(package, f, indent=2)
    
    def _create_tsconfig(self, project_path: Path):
        """Create tsconfig.json"""
        tsconfig = {
            "compilerOptions": {
                "target": "ES2022",
                "module": "ESNext",
                "moduleResolution": "node",
                "strict": self.config.strict_mode,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True,
                "resolveJsonModule": True,
                "allowJs": True,
                "noEmit": True
            },
            "include": ["src"],
            "exclude": ["node_modules", "dist", "build"]
        }
        
        # Framework-specific adjustments
        if self.config.framework == Framework.ASTRO:
            tsconfig["extends"] = "astro/tsconfigs/strict"
        elif self.config.framework == Framework.NEXTJS:
            tsconfig["compilerOptions"]["jsx"] = "preserve"
        
        tsconfig_file = project_path / "tsconfig.json"
        with open(tsconfig_file, 'w') as f:
            json.dump(tsconfig, f, indent=2)
    
    def _create_framework_configs(self, project_path: Path):
        """Create framework-specific configuration files"""
        if self.config.framework == Framework.ASTRO:
            self._create_astro_config(project_path)
        elif self.config.framework == Framework.NEXTJS:
            self._create_nextjs_config(project_path)
        elif self.config.framework == Framework.NUXT:
            self._create_nuxt_config(project_path)
        
        # Create Tailwind config if selected
        if self.config.css_framework == CSSFramework.TAILWIND:
            self._create_tailwind_config(project_path)
    
    def _create_astro_config(self, project_path: Path):
        """Create astro.config.mjs"""
        config_content = """import { defineConfig } from 'astro/config';
"""
        
        # Add integrations
        integrations = []
        
        if self.config.ui_framework == UIFramework.VUE:
            config_content += "import vue from '@astrojs/vue';\n"
            integrations.append("vue()")
        elif self.config.ui_framework == UIFramework.REACT:
            config_content += "import react from '@astrojs/react';\n"
            integrations.append("react()")
        
        if self.config.css_framework == CSSFramework.TAILWIND:
            config_content += "import tailwind from '@astrojs/tailwind';\n"
            integrations.append("tailwind()")
        
        config_content += "\n// https://astro.build/config\n"
        config_content += "export default defineConfig({\n"
        
        if integrations:
            config_content += f"  integrations: [{', '.join(integrations)}],\n"
        
        if self.config.i18n_enabled:
            config_content += f"  i18n: {{\n"
            config_content += f"    defaultLocale: '{self.config.default_locale}',\n"
            config_content += f"    locales: {self.config.locales},\n"
            config_content += f"  }},\n"
        
        config_content += "});\n"
        
        config_file = project_path / "astro.config.mjs"
        config_file.write_text(config_content)
    
    def _create_nextjs_config(self, project_path: Path):
        """Create next.config.js"""
        config_content = """/** @type {import('next').NextConfig} */
const nextConfig = {
"""
        
        if self.config.i18n_enabled:
            config_content += f"  i18n: {{\n"
            config_content += f"    defaultLocale: '{self.config.default_locale}',\n"
            config_content += f"    locales: {self.config.locales},\n"
            config_content += f"  }},\n"
        
        config_content += """  reactStrictMode: true,
}

module.exports = nextConfig
"""
        
        config_file = project_path / "next.config.js"
        config_file.write_text(config_content)
    
    def _create_nuxt_config(self, project_path: Path):
        """Create nuxt.config.ts"""
        config_content = """// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
"""
        
        if self.config.css_framework == CSSFramework.TAILWIND:
            config_content += "  modules: ['@nuxtjs/tailwindcss'],\n"
        
        if self.config.i18n_enabled:
            config_content += "  modules: ['@nuxtjs/i18n'],\n"
            config_content += f"  i18n: {{\n"
            config_content += f"    defaultLocale: '{self.config.default_locale}',\n"
            config_content += f"    locales: {self.config.locales},\n"
            config_content += f"  }},\n"
        
        config_content += "})\n"
        
        config_file = project_path / "nuxt.config.ts"
        config_file.write_text(config_content)
    
    def _create_tailwind_config(self, project_path: Path):
        """Create tailwind.config.js"""
        config_content = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx,vue}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
"""
        
        config_file = project_path / "tailwind.config.js"
        config_file.write_text(config_content)
    
    def _create_eslint_config(self, project_path: Path):
        """Create .eslintrc.json"""
        config = {
            "extends": [],
            "rules": {},
            "env": {
                "browser": True,
                "es2022": True,
                "node": True
            }
        }
        
        if self.config.language == "typescript":
            config["extends"].append("plugin:@typescript-eslint/recommended")
            config["parser"] = "@typescript-eslint/parser"
        
        if self.config.framework == Framework.NEXTJS:
            config["extends"].append("next/core-web-vitals")
        elif self.config.framework == Framework.ASTRO:
            config["extends"].append("plugin:astro/recommended")
        
        config_file = project_path / ".eslintrc.json"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_prettier_config(self, project_path: Path):
        """Create .prettierrc"""
        config = {
            "semi": True,
            "trailingComma": "es5",
            "singleQuote": True,
            "printWidth": 100,
            "tabWidth": 2
        }
        
        config_file = project_path / ".prettierrc"
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_docker_files(self, project_path: Path):
        """Create Docker configuration"""
        # Create Dockerfile
        dockerfile_content = f"""FROM node:18-alpine AS base

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN {self.config.package_manager.value} install

# Build application
COPY . .
RUN {self.config.package_manager.value} run build

# Production image
FROM node:18-alpine AS production
WORKDIR /app

COPY --from=base /app/dist ./dist
COPY --from=base /app/node_modules ./node_modules
COPY --from=base /app/package*.json ./

EXPOSE 3000

CMD ["{self.config.package_manager.value}", "start"]
"""
        
        dockerfile = project_path / "Dockerfile"
        dockerfile.write_text(dockerfile_content)
        
        # Create docker-compose.yml
        compose_content = f"""version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
"""
        
        if self.config.database == "postgresql":
            compose_content += """
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: ${self.config.name}
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
"""
        
        compose_file = project_path / "docker-compose.yml"
        compose_file.write_text(compose_content)
    
    def _initialize_git(self, project_path: Path):
        """Initialize Git repository"""
        os.chdir(project_path)
        
        # Initialize repository
        subprocess.run(["git", "init"], capture_output=True)
        
        # Create .gitignore
        gitignore_content = """# Dependencies
node_modules/
.pnp
.pnp.js

# Testing
coverage/
.nyc_output

# Production
build/
dist/
out/
.next/
.nuxt/

# Misc
.DS_Store
*.pem
.env*.local

# Debug
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# IDE
.vscode/
.idea/
*.swp
*.swo

# Vercel
.vercel

# TypeScript
*.tsbuildinfo
"""
        
        gitignore = project_path / ".gitignore"
        gitignore.write_text(gitignore_content)
        
        # Initial commit
        subprocess.run(["git", "add", "-A"], capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit from Enhanced Agent Framework"], 
                      capture_output=True)


# Make it backward compatible
SetupWizard = EnhancedSetupWizard  # Alias for compatibility


if __name__ == "__main__":
    wizard = EnhancedSetupWizard()
    result = wizard.run_interactive()
    
    if result['status'] == 'success':
        print("\n🎉 Project setup complete!")
    else:
        print(f"\n❌ Setup failed: {result.get('error', 'Unknown error')}")