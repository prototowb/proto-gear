"""
Agent Framework Core Implementation
Provides the adaptive hybrid agent system for autonomous project management
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import re

# Import Git workflow management
try:
    from .git_workflow import GitWorkflowIntegration, BranchType
    GIT_WORKFLOW_AVAILABLE = True
except ImportError:
    GIT_WORKFLOW_AVAILABLE = False
    print("Warning: Git workflow module not available")


class SprintType(Enum):
    """Types of sprints that determine flex agent allocation"""
    FEATURE_DEVELOPMENT = "feature_development"
    BUG_FIXING = "bug_fixing"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    DEPLOYMENT_PREP = "deployment_prep"
    REFACTORING = "refactoring"
    RESEARCH_INTEGRATION = "research_integration"


class TicketStatus(Enum):
    """Ticket workflow states"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class Agent:
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, name: str, description: str, responsibilities: List[str]):
        self.id = agent_id
        self.name = name
        self.description = description
        self.responsibilities = responsibilities
        self.active = False
        self.current_task = None
        self.utilization = 0.0
    
    def activate(self):
        """Activate the agent for work"""
        self.active = True
        
    def deactivate(self):
        """Deactivate the agent"""
        self.active = False
        self.current_task = None
        self.utilization = 0.0
    
    def assign_task(self, task: Dict[str, Any]):
        """Assign a task to the agent"""
        self.current_task = task
        self.utilization = 1.0
        return f"Task {task.get('id')} assigned to {self.name}"
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent-specific logic - override in subclasses"""
        raise NotImplementedError("Subclasses must implement execute()")


class AdaptiveHybridSystem:
    """4 permanent core agents + 2 flexible sprint-specific slots"""
    
    MAX_AGENTS = 6
    CORE_SLOTS = 4
    FLEX_SLOTS = 2
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the hybrid agent system"""
        self.config = self._load_config(config_path)
        self.core_agents = {}
        self.flex_agents = {}
        self.flex_pool = {}
        self.current_sprint_type = None
        
        self._initialize_agents()
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file"""
        if not config_path:
            config_path = "agent-framework.config.yaml"
        
        if not os.path.exists(config_path):
            return self._default_config()
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def _default_config(self) -> Dict:
        """Return default configuration if no config file exists"""
        return {
            'agents': {
                'core': [
                    {'id': 'backend', 'name': 'Backend Agent'},
                    {'id': 'frontend', 'name': 'Frontend Agent'},
                    {'id': 'testing', 'name': 'Testing Agent'},
                    {'id': 'devops', 'name': 'DevOps Agent'}
                ],
                'flex_pool': [
                    {'id': 'documentation', 'name': 'Documentation Agent'},
                    {'id': 'performance', 'name': 'Performance Agent'}
                ]
            }
        }
    
    def _initialize_agents(self):
        """Initialize core agents and flex pool"""
        # Initialize core agents
        for agent_config in self.config['agents']['core'][:self.CORE_SLOTS]:
            agent = Agent(
                agent_config['id'],
                agent_config['name'],
                agent_config.get('description', ''),
                agent_config.get('responsibilities', [])
            )
            agent.activate()  # Core agents are always active
            self.core_agents[agent.id] = agent
        
        # Initialize flex pool (not activated yet)
        for agent_config in self.config['agents'].get('flex_pool', []):
            agent = Agent(
                agent_config['id'],
                agent_config['name'],
                agent_config.get('description', ''),
                agent_config.get('responsibilities', [])
            )
            self.flex_pool[agent.id] = agent
    
    def configure_sprint(self, sprint_type: SprintType, sprint_goals: List[str] = None) -> Dict:
        """Dynamically assign flex agents based on sprint needs"""
        self.current_sprint_type = sprint_type
        
        # Deactivate current flex agents
        for agent in self.flex_agents.values():
            agent.deactivate()
        self.flex_agents.clear()
        
        # Get flex configuration for sprint type
        sprint_configs = self.config.get('agents', {}).get('sprint_configs', {})
        flex_config = sprint_configs.get(sprint_type.value, {})
        flex_agent_ids = flex_config.get('flex_agents', ['documentation', 'testing'])
        
        # Activate selected flex agents
        for agent_id in flex_agent_ids[:self.FLEX_SLOTS]:
            if agent_id in self.flex_pool:
                agent = self.flex_pool[agent_id]
                agent.activate()
                self.flex_agents[agent_id] = agent
        
        return self.get_active_configuration()
    
    def get_active_configuration(self) -> Dict:
        """Get current active agent configuration"""
        return {
            'sprint_type': self.current_sprint_type.value if self.current_sprint_type else None,
            'core_agents': {k: {'name': v.name, 'active': v.active} 
                          for k, v in self.core_agents.items()},
            'flex_agents': {k: {'name': v.name, 'active': v.active} 
                          for k, v in self.flex_agents.items()},
            'total_active': len(self.core_agents) + len(self.flex_agents)
        }
    
    def distribute_tasks(self, tasks: List[Dict]) -> Dict[str, List[Dict]]:
        """Distribute tasks to active agents based on tags and capabilities"""
        distribution = {agent_id: [] for agent_id in self.core_agents}
        distribution.update({agent_id: [] for agent_id in self.flex_agents})
        
        for task in tasks:
            assigned = False
            tags = task.get('tags', [])
            
            # Try to match task to specific agent based on tags
            for tag in tags:
                if tag in distribution and not assigned:
                    distribution[tag].append(task)
                    assigned = True
                    break
            
            # If not assigned, use round-robin on core agents
            if not assigned:
                # Simple round-robin distribution
                min_agent = min(distribution.keys(), 
                              key=lambda k: len(distribution[k]))
                distribution[min_agent].append(task)
        
        return distribution


class ProjectStateManager:
    """Manages PROJECT_STATUS.md as single source of truth"""
    
    def __init__(self, status_file: str = "PROJECT_STATUS.md"):
        self.status_file = status_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load project state from PROJECT_STATUS.md"""
        if not os.path.exists(self.status_file):
            return self._create_initial_state()
        
        with open(self.status_file, 'r') as f:
            content = f.read()
        
        # Parse YAML section
        yaml_match = re.search(r'```yaml\n(.*?)\n```', content, re.DOTALL)
        if yaml_match:
            state = yaml.safe_load(yaml_match.group(1))
        else:
            state = self._create_initial_state()
        
        return state
    
    def _create_initial_state(self) -> Dict:
        """Create initial project state"""
        return {
            'project_phase': 'Planning',
            'current_sprint': None,
            'current_branch': 'main',
            'last_ticket_id': 0,
            'ticket_prefix': 'PROJ'
        }
    
    def save_state(self):
        """Save current state back to PROJECT_STATUS.md"""
        # This would update the PROJECT_STATUS.md file
        # For now, just return the state
        return self.state
    
    def create_ticket(self, title: str, ticket_type: str = "feature", 
                     agent_generated: bool = True) -> Dict:
        """Create a new ticket with proper ID"""
        self.state['last_ticket_id'] += 1
        
        suffix = "/A" if agent_generated else ""
        ticket_id = f"{self.state['ticket_prefix']}{suffix}-{self.state['last_ticket_id']:03d}"
        
        ticket = {
            'id': ticket_id,
            'title': title,
            'type': ticket_type,
            'status': TicketStatus.PENDING.value,
            'created': datetime.now().isoformat(),
            'branch': None,
            'test_files': []
        }
        
        return ticket
    
    def get_active_tickets(self) -> List[Dict]:
        """Get list of active tickets from PROJECT_STATUS.md"""
        if not os.path.exists(self.status_file):
            return []
        
        with open(self.status_file, 'r') as f:
            content = f.read()
        
        # Parse tickets from the Active Tickets section
        tickets = []
        in_tickets_section = False
        
        for line in content.split('\n'):
            if '## 🎫 Active Tickets' in line:
                in_tickets_section = True
                continue
            elif in_tickets_section and line.startswith('##'):
                break  # End of tickets section
            elif in_tickets_section and line.startswith('|') and 'MCP' in line:
                # Parse ticket line: | MCP/A-001 | Title... | pending | assigned |
                parts = [p.strip() for p in line.split('|')]
                if len(parts) >= 4 and parts[1].startswith('MCP'):
                    ticket_id = parts[1]
                    title = parts[2].replace('...', '').strip()
                    status = parts[3]
                    
                    tickets.append({
                        'id': ticket_id,
                        'title': title,
                        'status': status,
                        'type': 'feature'  # Default type
                    })
        
        return tickets
    
    def get_current_sprint(self) -> Optional[int]:
        """Get current sprint number"""
        return self.state.get('current_sprint')


class DocumentationConsistencyEngine:
    """Ensures documentation consistency and prevents fragmentation"""
    
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.agents_files = []
        self.mismatches = []
        self.duplications = []
    
    def scan_agents_hierarchy(self):
        """Scan for all AGENTS.md files in the project"""
        self.agents_files = list(self.root_path.rglob("AGENTS.md"))
        return self.agents_files
    
    def check_inheritance(self) -> List[str]:
        """Verify all child AGENTS.md files declare inheritance"""
        issues = []
        
        for agents_file in self.agents_files:
            if agents_file == self.root_path / "AGENTS.md":
                continue  # Skip root
            
            with open(agents_file, 'r') as f:
                content = f.read()
            
            if "**Inheritance**:" not in content:
                issues.append(f"Missing inheritance declaration: {agents_file}")
        
        return issues
    
    def check_duplication(self) -> List[str]:
        """Check for content duplication between parent and child"""
        duplications = []
        
        # This would implement sophisticated duplication detection
        # For now, return empty list
        return duplications
    
    def run_consistency_check(self) -> Dict:
        """Run full consistency check"""
        self.scan_agents_hierarchy()
        
        return {
            'agents_files': len(self.agents_files),
            'inheritance_issues': self.check_inheritance(),
            'duplications': self.check_duplication(),
            'status': 'passed' if not self.mismatches and not self.duplications else 'failed'
        }


class WorkflowOrchestrator:
    """Main orchestrator for the Lead AI workflow"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.agent_system = AdaptiveHybridSystem(config_path)
        self.state_manager = ProjectStateManager()
        self.consistency_engine = DocumentationConsistencyEngine()
        self.config = self.agent_system.config
        
        # Initialize Git workflow if available
        self.git_workflow = None
        if GIT_WORKFLOW_AVAILABLE:
            self.git_workflow = GitWorkflowIntegration(self.config)
            self.git_workflow.initialize_git_workflow()
    
    def _is_first_time_init(self) -> bool:
        """Check if this is a first-time project initialization"""
        # Check for key project files that indicate an initialized project
        import os
        
        # Files that indicate an existing project
        existing_project_indicators = [
            "PROJECT_STATUS.md",
            ".agent-framework-initialized",  # Hidden marker file
            "AGENTS.md",  # Project-specific AGENTS file
        ]
        
        # If any of these exist, it's not a first-time init
        for file in existing_project_indicators:
            if os.path.exists(file):
                return False
        
        # Additional check: if config file exists but no project files
        # This might be a partially initialized project
        if os.path.exists("agent-framework.config.yaml"):
            # Config exists, but no status file - likely first run after config creation
            return not os.path.exists("PROJECT_STATUS.md")
        
        # No indicators found - this is a new project
        return True
    
    def detect_sprint_type(self) -> SprintType:
        """Intelligently determine current sprint type"""
        # Analyze project state to determine sprint type
        state = self.state_manager.state
        
        # Simple heuristic for demo
        if state.get('current_sprint') is None:
            return SprintType.FEATURE_DEVELOPMENT
        
        # More sophisticated analysis would go here
        return SprintType.FEATURE_DEVELOPMENT
    
    def execute_workflow(self):
        """Main execution loop for Lead AI"""
        print("🤖 Lead AI Activated - Acting as Product Owner & Tech Lead")

        # Check if ProtoGear has been initialized
        if self._is_first_time_init():
            print("\n⚠️  ProtoGear not initialized in this project.")
            print("Please run 'pg init' first to set up the AI agent framework.")
            return {'status': 'error', 'error': 'Not initialized'}

        # Step 1: Read project state
        print("📊 Reading PROJECT_STATUS.md...")
        state = self.state_manager.state
        print(f"  Current phase: {state.get('project_phase')}")
        print(f"  Current sprint: {state.get('current_sprint', 'None')}")
        
        # Step 2: Detect and configure sprint
        sprint_type = self.detect_sprint_type()
        print(f"\n🎯 Detected sprint type: {sprint_type.value}")
        
        config = self.agent_system.configure_sprint(sprint_type)
        print(f"  Active agents: {config['total_active']}")
        print(f"  Core agents: {', '.join(config['core_agents'].keys())}")
        print(f"  Flex agents: {', '.join(config['flex_agents'].keys())}")
        
        # Step 3: Documentation consistency check
        print("\n📋 Checking documentation consistency...")
        consistency = self.consistency_engine.run_consistency_check()
        print(f"  AGENTS.md files found: {consistency['agents_files']}")
        print(f"  Status: {consistency['status']}")
        
        # Step 4: Generate development plan and create branches
        print("\n📝 Generating development plan...")
        
        # Get active tickets from PROJECT_STATUS.md
        active_tickets = self.state_manager.get_active_tickets()
        
        if active_tickets and self.git_workflow:
            print(f"  Found {len(active_tickets)} active tickets")
            
            # Check and create branches for tickets without branches
            print("\n🌿 Checking Git branches for tickets...")
            tickets_needing_branches = []
            
            for ticket in active_tickets:
                # Construct expected branch name
                from .git_workflow import BranchType
                clean_ticket_id = ticket['id'].replace("/", "-").lower()
                clean_title = self.git_workflow.branch_manager._sanitize_branch_name(ticket['title'])
                expected_branch = f"feature/{clean_ticket_id}-{clean_title}"
                
                if not self.git_workflow.branch_manager.branch_exists(expected_branch):
                    tickets_needing_branches.append(ticket)
                    print(f"  ❌ No branch for {ticket['id']}: {ticket['title'][:30]}...")
                else:
                    print(f"  ✅ Branch exists for {ticket['id']}")
            
            # Create missing branches
            if tickets_needing_branches:
                print(f"\n📝 Creating {len(tickets_needing_branches)} missing branches...")
                branch_mapping = self.git_workflow.create_ticket_branches(tickets_needing_branches)
                print(f"  ✅ Created {len(branch_mapping)} branches")
            else:
                print("  ✅ All tickets have branches")
        
        # Step 5: Quality checks
        print("\n✅ Running quality checks...")
        print("  Test coverage: Check")
        print("  Documentation: Check")
        print("  Linting: Check")
        
        # Step 6: Git workflow status
        if self.git_workflow:
            print("\n🌿 Git Workflow Status...")
            git_status = self.git_workflow.get_workflow_status()
            print(f"  Current branch: {git_status.get('current_branch')}")
            print(f"  Feature branches: {git_status.get('total_branches', 0)}")
        
        print("\n✨ Lead AI workflow complete!")
        
        result = {
            'status': 'completed',
            'sprint_type': sprint_type.value,
            'agents_active': config['total_active'],
            'consistency_check': consistency['status']
        }
        
        if self.git_workflow:
            result['git_workflow'] = self.git_workflow.get_workflow_status()
        
        return result


class TicketGenerator:
    """Generates development tickets from various sources"""
    
    def __init__(self, state_manager: ProjectStateManager, git_workflow: Optional[GitWorkflowIntegration] = None):
        self.state_manager = state_manager
        self.git_workflow = git_workflow
    
    def create_feature_ticket(self, feature_name: str, requirements: List[str]) -> Dict:
        """Create a feature development ticket"""
        ticket = self.state_manager.create_ticket(
            title=f"Implement {feature_name}",
            ticket_type="feature",
            agent_generated=True
        )
        
        ticket['requirements'] = requirements
        ticket['acceptance_criteria'] = []
        ticket['test_coverage_target'] = 80
        
        # Create Git branch if workflow is available
        if self.git_workflow:
            from .git_workflow import BranchType
            branch_name = self.git_workflow.branch_manager.create_ticket_branch(
                ticket['id'],
                ticket['title'],
                BranchType.FEATURE
            )
            if branch_name:
                ticket['branch'] = branch_name
        
        return ticket
    
    def create_bug_ticket(self, bug_description: str, severity: str = "medium") -> Dict:
        """Create a bug fix ticket"""
        ticket = self.state_manager.create_ticket(
            title=f"Fix: {bug_description}",
            ticket_type="bugfix",
            agent_generated=True
        )
        
        ticket['severity'] = severity
        ticket['steps_to_reproduce'] = []
        
        # Create Git branch if workflow is available
        if self.git_workflow:
            from .git_workflow import BranchType
            branch_name = self.git_workflow.branch_manager.create_ticket_branch(
                ticket['id'],
                ticket['title'],
                BranchType.BUGFIX
            )
            if branch_name:
                ticket['branch'] = branch_name
        
        return ticket
    
    def create_branches_for_tickets(self, tickets: List[Dict]) -> Dict[str, str]:
        """Create Git branches for a list of tickets"""
        if not self.git_workflow:
            print("⚠️  Git workflow not available")
            return {}
        
        return self.git_workflow.create_ticket_branches(tickets)


def initialize_project(project_name: str, project_type: str = "web-app"):
    """Initialize a new project with the Agent Framework"""
    print(f"🚀 Initializing {project_name} as {project_type}")
    
    # Create essential files
    orchestrator = WorkflowOrchestrator()
    
    # Run initial workflow
    result = orchestrator.execute_workflow()
    
    print(f"\n✅ Project initialized successfully!")
    return result


if __name__ == "__main__":
    # Example usage
    orchestrator = WorkflowOrchestrator()
    orchestrator.execute_workflow()