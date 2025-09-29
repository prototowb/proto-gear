"""
Main Setup Wizard for ProtoGear
Unified entry point with initial choice between Agent Framework only or Full Project Scaffolding
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

try:
    from .grouped_setup_wizard import (
        GroupedSetupWizard, GroupedProjectConfig, StepGroup, ConfigStep, WizardOption
    )
except ImportError:
    from grouped_setup_wizard import (
        GroupedSetupWizard, GroupedProjectConfig, StepGroup, ConfigStep, WizardOption
    )

try:
    from .enhanced_setup_wizard import (
        ProjectType, Framework, UIFramework, CSSFramework, PackageManager,
        TestFramework, CMSOption, DeploymentTarget
    )
    from .ultimate_setup_wizard import AuthProvider, AnalyticsProvider
except ImportError:
    from enhanced_setup_wizard import (
        ProjectType, Framework, UIFramework, CSSFramework, PackageManager,
        TestFramework, CMSOption, DeploymentTarget
    )
    from ultimate_setup_wizard import AuthProvider, AnalyticsProvider


class ProtoGearWizard(GroupedSetupWizard):
    """Main ProtoGear setup wizard with unified entry point"""
    
    def __init__(self, base_path: str = ".", dry_run: bool = False):
        """Initialize the ProtoGear wizard"""
        super().__init__(base_path, dry_run)
        self.wizard_mode = None  # 'agent-only' or 'full-project'
        
    def run_interactive(self) -> Dict[str, Any]:
        """Run the unified wizard with initial choice"""
        print("\n" + "=" * 70)
        print("ProtoGear Project Initialization")
        print("=" * 70)
        
        try:
            # Step 0: Initial choice
            self._show_welcome()
            if not self._get_initial_choice():
                return {'status': 'cancelled'}
            
            if self.wizard_mode == 'agent-only':
                return self._setup_agent_framework_only()
            else:
                return self._run_full_project_setup()
                
        except KeyboardInterrupt:
            print("\n\nSetup cancelled by user")
            return {'status': 'cancelled'}
        except Exception as e:
            return {'status': 'error', 'error': str(e)}
    
    def _show_welcome(self):
        """Show welcome message and explanation"""
        print("\nWelcome to ProtoGear!")
        print("ProtoGear helps you set up modern development projects with integrated AI agent workflows.")
        print("\nYou can choose between:")
        print("1. Agent Framework Only - Just add ProtoGear's agent workflow to an existing project")
        print("2. Full Project Scaffolding - Create a complete project from scratch with ProtoGear integration")
        print()
    
    def _get_initial_choice(self) -> bool:
        """Get the user's initial choice"""
        while True:
            choice = input("What would you like to do? (1/2): ").strip()
            
            if choice == '1':
                self.wizard_mode = 'agent-only'
                return True
            elif choice == '2':
                self.wizard_mode = 'full-project'
                return True
            elif choice.lower() in ['q', 'quit', 'exit']:
                return False
            else:
                print("Please enter 1 or 2 (or 'q' to quit)")
    
    def _setup_agent_framework_only(self) -> Dict[str, Any]:
        """Set up only the ProtoGear agent framework"""
        print("\n" + "─" * 50)
        print("Agent Framework Setup")
        print("─" * 50)
        
        # Detect current project structure
        current_dir = Path(self.base_path)
        project_info = self._detect_project_structure(current_dir)
        
        print(f"\nDetected project structure:")
        if project_info['type']:
            print(f"  Project type: {project_info['type']}")
        if project_info['framework']:
            print(f"  Framework: {project_info['framework']}")
        if project_info['package_manager']:
            print(f"  Package manager: {project_info['package_manager']}")
        
        # Set up minimal config for agent framework
        self.config.name = project_info.get('name', current_dir.name)
        
        # Create agent framework files
        result = self._create_agent_framework_files(current_dir, project_info)
        
        if result['status'] == 'success':
            print(f"\nAgent Framework initialized successfully!")
            print(f"Created:")
            for file in result.get('files_created', []):
                print(f"  - {file}")
            print(f"\nNext steps:")
            print(f"  1. Review AGENTS.md to understand your project structure")
            print(f"  2. Check PROJECT_STATUS.md for current project state")
            print(f"  3. Start development with AI-powered workflow assistance")
        
        return result
    
    def _run_full_project_setup(self) -> Dict[str, Any]:
        """Run the full project scaffolding wizard"""
        print("\n" + "─" * 50)
        print("Full Project Setup")
        print("─" * 50)
        
        # Reinitialize step groups with updated structure
        self.step_groups = self._initialize_updated_step_groups()
        
        # Show wizard overview
        self._show_wizard_overview()
        
        # Process each group
        for group in sorted(self.step_groups, key=lambda g: g.order):
            if group.conditional and not group.conditional(self.config):
                continue
            
            if not self._process_step_group(group):
                return {'status': 'cancelled'}
        
        # Apply all selections to config
        self.config.apply_selections()
        
        # Show final summary
        self._show_final_summary()
        
        # Confirm creation
        confirm = input("\nCreate project with this configuration? (Y/n): ").lower()
        if confirm in ['n', 'no']:
            return {'status': 'cancelled'}
        
        # Create the project
        result = self.create_project()
        
        if result['status'] == 'success':
            print(f"\nProject '{self.config.name}' created successfully!")
            if result.get('path'):
                print(f"Location: {result['path']}")
            self._show_next_steps()
        
        return result
    
    def _initialize_updated_step_groups(self) -> list:
        """Initialize step groups with updated structure including backend frameworks"""
        return [
            self._create_project_basics_group(),
            self._create_frontend_stack_group(),
            self._create_backend_data_group_updated(),  # Updated version
            self._create_dev_tools_group(),
            self._create_features_group(),
            self._create_deployment_group(),
            self._create_agent_framework_group(),  # New final step
        ]
    
    def _create_backend_data_group_updated(self) -> StepGroup:
        """Create the updated backend and data layer group with backend frameworks"""
        steps = [
            ConfigStep(
                id='backend_framework',
                name='Backend Framework',
                prompt='Choose a backend framework:',
                step_type='single',
                options=[
                    WizardOption('express', 'Express.js', 'Fast Node.js web framework'),
                    WizardOption('fastapi', 'FastAPI', 'Modern Python API framework'),
                    WizardOption('django', 'Django', 'Full-featured Python web framework'),
                    WizardOption('nextjs-api', 'Next.js API Routes', 'Built-in API with Next.js'),
                    WizardOption('nuxt-api', 'Nuxt Server API', 'Built-in API with Nuxt'),
                    WizardOption('astro-api', 'Astro API Routes', 'Built-in API with Astro'),
                    WizardOption('none', 'None', 'No backend framework needed'),
                ],
                conditional=lambda config: config.get_selection('project_type') in ['web-app', 'api', 'fullstack'],
                default='none'
            ),
            ConfigStep(
                id='database',
                name='Database',
                prompt='Choose a database:',
                step_type='single',
                options=[
                    WizardOption('postgresql', 'PostgreSQL', 'Powerful open-source database'),
                    WizardOption('mysql', 'MySQL', 'Popular relational database'),
                    WizardOption('sqlite', 'SQLite', 'Lightweight file-based database'),
                    WizardOption('mongodb', 'MongoDB', 'NoSQL document database'),
                    WizardOption('supabase', 'Supabase', 'Open source Firebase alternative'),
                    WizardOption('planetscale', 'PlanetScale', 'Serverless MySQL platform'),
                    WizardOption('none', 'None', 'No database needed'),
                ],
                conditional=lambda config: config.get_selection('project_type') in ['web-app', 'api', 'fullstack'],
                default='none'
            ),
            ConfigStep(
                id='orm',
                name='ORM/Query Builder',
                prompt='Choose an ORM or query builder:',
                step_type='single',
                options=[
                    WizardOption('prisma', 'Prisma', 'Next-generation ORM'),
                    WizardOption('drizzle', 'Drizzle', 'Lightweight TypeScript ORM'),
                    WizardOption('typeorm', 'TypeORM', 'Feature-rich ORM'),
                    WizardOption('sequelize', 'Sequelize', 'Promise-based ORM'),
                    WizardOption('mongoose', 'Mongoose', 'MongoDB object modeling', requires=['mongodb']),
                    WizardOption('none', 'None', 'Raw SQL queries'),
                ],
                conditional=lambda config: config.get_selection('database') not in ['none', None],
                default='prisma'
            ),
        ]
        
        return StepGroup(
            id='backend_data',
            name='Backend & Data',
            emoji='🗄️',
            description='Configure your backend framework and data layer',
            steps=steps,
            conditional=lambda config: config.get_selection('project_type') in ['web-app', 'api', 'fullstack'],
            order=3
        )
    
    def _create_agent_framework_group(self) -> StepGroup:
        """Create the ProtoGear Agent Framework configuration step"""
        steps = [
            ConfigStep(
                id='agent_workflow_orchestration',
                name='Workflow Orchestration',
                prompt='How should agents coordinate work?',
                step_type='single',
                options=[
                    WizardOption('sequential', 'Sequential', 'Agents work one after another'),
                    WizardOption('parallel', 'Parallel', 'Agents work simultaneously when possible'),
                    WizardOption('hybrid', 'Hybrid', 'Mix of sequential and parallel based on dependencies'),
                ],
                default='hybrid'
            ),
            ConfigStep(
                id='agent_roles',
                name='Agent Roles',
                prompt='Which agent roles do you need?',
                step_type='multiple',
                options=[
                    WizardOption('architect', 'Architect', 'System design and architecture decisions'),
                    WizardOption('frontend-dev', 'Frontend Developer', 'UI/UX implementation'),
                    WizardOption('backend-dev', 'Backend Developer', 'Server-side logic and APIs'),
                    WizardOption('devops', 'DevOps Engineer', 'Deployment and infrastructure'),
                    WizardOption('tester', 'Quality Assurance', 'Testing and quality control'),
                    WizardOption('security', 'Security Specialist', 'Security analysis and hardening'),
                    WizardOption('performance', 'Performance Engineer', 'Optimization and monitoring'),
                    WizardOption('documentation', 'Technical Writer', 'Documentation and guides'),
                ],
                default=['architect', 'frontend-dev', 'backend-dev', 'tester']
            ),
            ConfigStep(
                id='agent_responsibilities',
                name='Responsibility Assignment',
                prompt='How should responsibilities be distributed?',
                step_type='single',
                options=[
                    WizardOption('by-feature', 'By Feature', 'Each agent owns complete features'),
                    WizardOption('by-layer', 'By Layer', 'Each agent specializes in tech stack layers'),
                    WizardOption('by-phase', 'By Phase', 'Each agent handles project phases'),
                    WizardOption('flexible', 'Flexible', 'Dynamic assignment based on current needs'),
                ],
                default='flexible'
            )
        ]
        
        return StepGroup(
            id='agent_framework',
            name='ProtoGear Agent Framework',
            emoji='🤖',
            description='Configure AI agent workflow integration',
            steps=steps,
            order=7
        )
    
    def _detect_project_structure(self, project_path: Path) -> Dict[str, Any]:
        """Detect existing project structure and technologies"""
        info = {
            'name': project_path.name,
            'type': None,
            'framework': None,
            'package_manager': None,
            'has_backend': False,
            'has_frontend': False,
            'directories': [],
            'config_files': []
        }
        
        # Check for package.json
        package_json = project_path / 'package.json'
        if package_json.exists():
            try:
                with open(package_json) as f:
                    package_data = json.load(f)
                    deps = {**package_data.get('dependencies', {}), **package_data.get('devDependencies', {})}
                    
                    # Detect framework
                    if 'next' in deps:
                        info['framework'] = 'Next.js'
                        info['type'] = 'web-app'
                    elif 'nuxt' in deps:
                        info['framework'] = 'Nuxt.js'
                        info['type'] = 'web-app'
                    elif 'astro' in deps:
                        info['framework'] = 'Astro'
                        info['type'] = 'static-site'
                    elif 'express' in deps:
                        info['framework'] = 'Express.js'
                        info['type'] = 'api'
                        info['has_backend'] = True
                    elif 'react' in deps:
                        info['framework'] = 'React'
                        info['type'] = 'web-app'
                        info['has_frontend'] = True
                    elif 'vue' in deps:
                        info['framework'] = 'Vue.js'
                        info['type'] = 'web-app'
                        info['has_frontend'] = True
            except:
                pass
        
        # Check for Python files
        if any(project_path.glob('*.py')) or (project_path / 'requirements.txt').exists():
            if not info['type']:
                info['type'] = 'api'
                info['has_backend'] = True
            
            # Check for specific Python frameworks
            requirements_file = project_path / 'requirements.txt'
            if requirements_file.exists():
                try:
                    requirements = requirements_file.read_text()
                    if 'fastapi' in requirements.lower():
                        info['framework'] = 'FastAPI'
                    elif 'django' in requirements.lower():
                        info['framework'] = 'Django'
                    elif 'flask' in requirements.lower():
                        info['framework'] = 'Flask'
                except:
                    pass
        
        # Detect package manager
        if (project_path / 'pnpm-lock.yaml').exists():
            info['package_manager'] = 'pnpm'
        elif (project_path / 'yarn.lock').exists():
            info['package_manager'] = 'yarn'
        elif (project_path / 'bun.lockb').exists():
            info['package_manager'] = 'bun'
        elif package_json.exists():
            info['package_manager'] = 'npm'
        
        # Scan directories
        for item in project_path.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                info['directories'].append(item.name)
                
                # Detect structure patterns
                if item.name in ['src', 'app', 'pages']:
                    info['has_frontend'] = True
                elif item.name in ['api', 'server', 'backend']:
                    info['has_backend'] = True
        
        # Scan for config files
        config_extensions = ['.json', '.js', '.ts', '.yaml', '.yml', '.toml']
        for file in project_path.iterdir():
            if file.is_file() and any(file.name.endswith(ext) for ext in config_extensions):
                if any(keyword in file.name.lower() for keyword in ['config', 'settings', '.env']):
                    info['config_files'].append(file.name)
        
        return info
    
    def _create_agent_framework_files(self, project_path: Path, project_info: Dict) -> Dict[str, Any]:
        """Create ProtoGear agent framework files based on detected project structure"""
        try:
            files_created = []
            
            # Create AGENTS.md with project-specific structure
            agents_content = self._generate_agents_md(project_info)
            agents_file = project_path / 'AGENTS.md'
            agents_file.write_text(agents_content)
            files_created.append('AGENTS.md')
            
            # Create PROJECT_STATUS.md
            status_content = self._generate_project_status_md(project_info)
            status_file = project_path / 'PROJECT_STATUS.md'
            status_file.write_text(status_content)
            files_created.append('PROJECT_STATUS.md')
            
            # Create agent workflow configuration
            config_content = self._generate_agent_config(project_info)
            config_file = project_path / 'protogear.config.yaml'
            config_file.write_text(config_content)
            files_created.append('protogear.config.yaml')
            
            # Create .protogear directory for internal files
            protogear_dir = project_path / '.protogear'
            protogear_dir.mkdir(exist_ok=True)
            
            # Create workflow templates
            workflow_content = self._generate_workflow_templates(project_info)
            workflow_file = protogear_dir / 'workflows.yaml'
            workflow_file.write_text(workflow_content)
            files_created.append('.protogear/workflows.yaml')
            
            return {
                'status': 'success',
                'files_created': files_created
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _generate_agents_md(self, project_info: Dict) -> str:
        """Generate AGENTS.md file based on project structure"""
        framework = project_info.get('framework', 'Unknown')
        project_type = project_info.get('type', 'Unknown')
        directories = project_info.get('directories', [])
        
        content = f"""# AGENTS.md - {project_info['name']}

> **ProtoGear Agent Framework Integration**
> **Project Type**: {project_type}
> **Framework**: {framework}
> **Configuration**: `protogear.config.yaml`

## Framework Activation

When this file is read by an AI agent, it should:

1. Load the ProtoGear Agent Framework
2. Use configuration from `protogear.config.yaml`
3. Check `PROJECT_STATUS.md` for current state
4. Execute the agent workflow based on project structure

## Project Structure Analysis

**Detected Structure:**
"""
        
        if directories:
            for directory in directories:
                content += f"- `{directory}/` - "
                if directory in ['src', 'app']:
                    content += "Main application source code\n"
                elif directory == 'pages':
                    content += "Page components and routing\n"
                elif directory == 'api':
                    content += "Backend API endpoints\n"
                elif directory == 'components':
                    content += "Reusable UI components\n"
                elif directory == 'lib' or directory == 'utils':
                    content += "Utility functions and libraries\n"
                elif directory == 'styles':
                    content += "Styling and CSS files\n"
                elif directory == 'public':
                    content += "Static assets and public files\n"
                elif directory == 'tests' or directory == 'test':
                    content += "Test files and testing utilities\n"
                elif directory == 'docs':
                    content += "Documentation and guides\n"
                else:
                    content += "Project-specific directory\n"
        
        content += f"""
## Agent Workflow Configuration

**Primary Agents:**
- **Architect Agent**: Analyzes project structure and suggests improvements
- **Development Agent**: Handles code implementation based on detected framework
- **Quality Agent**: Ensures code quality and testing standards
- **Documentation Agent**: Maintains project documentation

**Framework-Specific Workflow:**
"""
        
        if framework == 'Next.js':
            content += """- React/Next.js component development
- API route implementation
- SSR/SSG optimization
- Performance monitoring"""
        elif framework == 'FastAPI':
            content += """- Python API development
- OpenAPI documentation
- Database integration
- Testing automation"""
        elif framework == 'Django':
            content += """- Django model and view development
- Admin interface configuration
- Template and static file management
- Migration handling"""
        else:
            content += """- General web development practices
- Code quality maintenance
- Testing and deployment
- Documentation updates"""
        
        content += f"""

## Integration Commands

```python
# Framework activation
from protogear import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator('protogear.config.yaml')
orchestrator.analyze_project_structure()
orchestrator.execute_workflow()
```

---

*Powered by ProtoGear Agent Framework*
"""
        
        return content
    
    def _generate_project_status_md(self, project_info: Dict) -> str:
        """Generate PROJECT_STATUS.md file"""
        return f"""# PROJECT STATUS - {project_info['name']}

> **Single Source of Truth** for project state

## 📊 Current State

```yaml
project_phase: "Analysis"
framework: "{project_info.get('framework', 'Unknown')}"
project_type: "{project_info.get('type', 'Unknown')}"
protogear_initialized: true
initialization_date: "{datetime.now().strftime('%Y-%m-%d')}"
```

## 🎫 Active Tickets
*No active tickets yet - ProtoGear will populate this based on workflow*

## ✅ Completed Tickets
- INIT-001: ProtoGear Agent Framework initialized

## 📈 Project Analysis

| Component | Status | Notes |
|-----------|--------|-------|
| Project Structure | ✅ Analyzed | {len(project_info.get('directories', []))} directories detected |
| Framework Detection | ✅ Complete | {project_info.get('framework', 'Unknown')} detected |
| Package Manager | {'✅ Detected' if project_info.get('package_manager') else '❓ Unknown'} | {project_info.get('package_manager', 'Not detected')} |

## 🔄 Recent Updates
- {datetime.now().strftime('%Y-%m-%d')}: ProtoGear Agent Framework integrated

---
*Maintained by ProtoGear Agent Framework*
"""
    
    def _generate_agent_config(self, project_info: Dict) -> str:
        """Generate protogear.config.yaml"""
        config = {
            'project': {
                'name': project_info['name'],
                'type': project_info.get('type', 'unknown'),
                'framework': project_info.get('framework', 'unknown'),
                'package_manager': project_info.get('package_manager', 'npm')
            },
            'agents': {
                'enabled': True,
                'workflow_mode': 'adaptive',
                'primary_agents': [
                    {'role': 'architect', 'priority': 1},
                    {'role': 'developer', 'priority': 2},
                    {'role': 'tester', 'priority': 3},
                    {'role': 'documentation', 'priority': 4}
                ]
            },
            'workflows': {
                'auto_analysis': True,
                'continuous_monitoring': True,
                'quality_gates': True
            },
            'integration': {
                'directories': project_info.get('directories', []),
                'config_files': project_info.get('config_files', [])
            }
        }
        
        import yaml
        return yaml.dump(config, default_flow_style=False, sort_keys=False)
    
    def _generate_workflow_templates(self, project_info: Dict) -> str:
        """Generate workflow templates"""
        workflows = {
            'analysis_workflow': {
                'name': 'Project Analysis',
                'triggers': ['file_change', 'manual'],
                'steps': [
                    'scan_project_structure',
                    'analyze_dependencies',
                    'check_code_quality',
                    'update_status'
                ]
            },
            'development_workflow': {
                'name': 'Development Support',
                'triggers': ['code_change'],
                'steps': [
                    'review_changes',
                    'suggest_improvements',
                    'run_tests',
                    'update_documentation'
                ]
            },
            'deployment_workflow': {
                'name': 'Deployment Pipeline',
                'triggers': ['manual', 'schedule'],
                'steps': [
                    'run_full_tests',
                    'build_project',
                    'deploy_to_staging',
                    'validate_deployment'
                ]
            }
        }
        
        import yaml
        return yaml.dump(workflows, default_flow_style=False)


# Export for CLI usage
def run_protogear_init(base_path: str = ".", dry_run: bool = False) -> Dict[str, Any]:
    """Main entry point for 'pg init' command"""
    wizard = ProtoGearWizard(base_path=base_path, dry_run=dry_run)
    return wizard.run_interactive()


if __name__ == "__main__":
    import sys
    
    # For testing
    dry_run = '--dry-run' in sys.argv
    result = run_protogear_init(dry_run=dry_run)
    
    if result['status'] == 'success':
        print("\nProtoGear initialization successful!")
    else:
        print(f"\nInitialization failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)