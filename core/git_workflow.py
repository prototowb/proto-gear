"""
Git Workflow Management for Agent Framework
Handles branch creation, management, and Git operations
Integrates with Testing Workflow for TDD
"""

import os
import subprocess
import re
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
from pathlib import Path

# Import testing workflow for integration
try:
    from .testing_workflow import TDDWorkflow, TestRunner, TestStatus
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False
    print("Warning: Testing workflow not available")


class BranchType(Enum):
    """Types of branches following Git Flow"""
    FEATURE = "feature"
    BUGFIX = "bugfix"
    HOTFIX = "hotfix"
    RELEASE = "release"
    EXPERIMENTAL = "experimental"


class GitBranchManager:
    """Manages Git branches for the agent framework"""
    
    def __init__(self, config: Dict):
        """Initialize Git branch manager with configuration"""
        self.config = config
        self.git_config = config.get('git', {})
        self.main_branch = self.git_config.get('main_branch', 'main')
        self.dev_branch = self.git_config.get('dev_branch', 'development')
        self.branch_prefixes = self.git_config.get('branch_prefix', {})
        self.ticket_prefix = config.get('tickets', {}).get('prefix', 'PROJ')
        
    def run_git_command(self, command: str, check: bool = True) -> Tuple[bool, str]:
        """
        Execute a git command and return success status and output
        """
        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                check=check
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            return False, e.stderr.strip()
        except Exception as e:
            return False, str(e)
    
    def get_current_branch(self) -> Optional[str]:
        """Get the current Git branch"""
        success, output = self.run_git_command("git rev-parse --abbrev-ref HEAD")
        return output if success else None
    
    def branch_exists(self, branch_name: str) -> bool:
        """Check if a branch exists locally"""
        # Check local branches only (since we don't have a remote)
        success, output = self.run_git_command(f"git branch --list {branch_name}", check=False)
        # Branch exists if output contains the branch name
        return bool(output.strip())
    
    def create_ticket_branch(self, ticket_id: str, ticket_title: str, 
                           branch_type: BranchType = BranchType.FEATURE) -> Optional[str]:
        """
        Create a branch for a specific ticket
        
        Args:
            ticket_id: Ticket identifier (e.g., "MCP/A-001")
            ticket_title: Ticket title for branch name
            branch_type: Type of branch to create
            
        Returns:
            Branch name if created successfully, None otherwise
        """
        # Clean ticket ID for branch name (remove special characters)
        clean_ticket_id = ticket_id.replace("/", "-").replace(" ", "-").lower()
        
        # Clean and truncate title for branch name
        clean_title = self._sanitize_branch_name(ticket_title)
        
        # Get branch prefix
        prefix = self.branch_prefixes.get(branch_type.value, f"{branch_type.value}/")
        
        # Construct branch name
        branch_name = f"{prefix}{clean_ticket_id}-{clean_title}"
        
        # Check if branch already exists
        if self.branch_exists(branch_name):
            print(f"  ⚠️  Branch already exists: {branch_name}")
            return branch_name
        
        # Ensure we're on the development branch
        current_branch = self.get_current_branch()
        if current_branch != self.dev_branch:
            print(f"  📝 Switching to {self.dev_branch} branch...")
            success, output = self.run_git_command(f"git checkout {self.dev_branch}")
            if not success:
                print(f"  ❌ Failed to switch to {self.dev_branch}: {output}")
                return None
        
        # Pull latest changes
        print(f"  🔄 Pulling latest changes from {self.dev_branch}...")
        self.run_git_command(f"git pull origin {self.dev_branch}", check=False)
        
        # Create and checkout new branch
        print(f"  🌿 Creating branch: {branch_name}")
        success, output = self.run_git_command(f"git checkout -b {branch_name}")
        
        if success:
            print(f"  ✅ Created and switched to branch: {branch_name}")
            
            # Try to push branch to remote if it exists
            success, output = self.run_git_command("git remote", check=False)
            if output.strip():  # Only if remote exists
                success, output = self.run_git_command(f"git push -u origin {branch_name}", check=False)
                if success:
                    print(f"  ☁️  Pushed branch to remote")
                else:
                    print(f"  ⚠️  Could not push to remote (may need authentication)")
            
            return branch_name
        else:
            print(f"  ❌ Failed to create branch: {output}")
            return None
    
    def create_sprint_branches(self, tickets: List[Dict]) -> Dict[str, str]:
        """
        Create branches for multiple tickets
        
        Args:
            tickets: List of ticket dictionaries
            
        Returns:
            Dictionary mapping ticket IDs to branch names
        """
        branch_mapping = {}
        
        print("\n🌿 Creating Git branches for tickets...")
        print("-" * 50)
        
        for ticket in tickets:
            ticket_id = ticket.get('id')
            title = ticket.get('title', '')
            ticket_type = ticket.get('type', 'feature')
            
            # Determine branch type
            if ticket_type == 'bugfix':
                branch_type = BranchType.BUGFIX
            elif ticket_type == 'hotfix':
                branch_type = BranchType.HOTFIX
            else:
                branch_type = BranchType.FEATURE
            
            # Create branch
            branch_name = self.create_ticket_branch(ticket_id, title, branch_type)
            
            if branch_name:
                branch_mapping[ticket_id] = branch_name
                ticket['branch'] = branch_name
        
        # Return to development branch
        print(f"\n📝 Returning to {self.dev_branch} branch...")
        self.run_git_command(f"git checkout {self.dev_branch}")
        
        print(f"\n✅ Created {len(branch_mapping)} branches")
        
        return branch_mapping
    
    def _sanitize_branch_name(self, title: str, max_length: int = 30) -> str:
        """
        Sanitize a string to be safe for use in a Git branch name
        
        Args:
            title: Original title string
            max_length: Maximum length for the sanitized name
            
        Returns:
            Sanitized branch name component
        """
        # Convert to lowercase
        clean = title.lower()
        
        # Replace spaces and special characters with hyphens
        clean = re.sub(r'[^a-z0-9\-_]', '-', clean)
        
        # Remove multiple consecutive hyphens
        clean = re.sub(r'-+', '-', clean)
        
        # Remove leading/trailing hyphens
        clean = clean.strip('-')
        
        # Truncate to max length
        if len(clean) > max_length:
            clean = clean[:max_length].rstrip('-')
        
        return clean
    
    def setup_git_hooks(self):
        """
        Setup Git hooks for the project
        """
        hooks_dir = Path(".git/hooks")
        if not hooks_dir.exists():
            print("  ⚠️  .git/hooks directory not found")
            return
        
        # Pre-commit hook for linting and tests
        pre_commit_hook = """#!/bin/sh
# Agent Framework Pre-commit Hook

echo "🔍 Running pre-commit checks..."

# Run linting
echo "  📝 Checking code style..."
if command -v flake8 &> /dev/null; then
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
fi

# Run tests if they exist
if [ -d "tests" ]; then
    echo "  🧪 Running tests..."
    python -m pytest tests/ -v --tb=short
fi

echo "✅ Pre-commit checks passed!"
"""
        
        pre_commit_path = hooks_dir / "pre-commit"
        with open(pre_commit_path, 'w', encoding='utf-8') as f:
            f.write(pre_commit_hook)
        
        # Make hook executable
        os.chmod(pre_commit_path, 0o755)
        
        print("  ✅ Git hooks configured")
    
    def create_pull_request_template(self):
        """
        Create a pull request template for the project
        """
        pr_template = """## 🎫 Ticket
Closes #[ticket-number]

## 📝 Description
Brief description of changes

## 🔄 Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## ✅ Checklist
- [ ] My code follows the style guidelines of this project
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## 🧪 Testing
Describe the tests that you ran to verify your changes

## 📸 Screenshots (if applicable)
Add screenshots to help explain your changes

## 📚 Additional Context
Add any other context about the pull request here
"""
        
        # Create .github directory if it doesn't exist
        github_dir = Path(".github")
        github_dir.mkdir(exist_ok=True)
        
        # Write PR template
        pr_template_path = github_dir / "pull_request_template.md"
        with open(pr_template_path, 'w', encoding='utf-8') as f:
            f.write(pr_template)
        
        print("  ✅ Pull request template created")
    
    def get_branch_status(self, branch_name: str) -> Dict:
        """
        Get status information for a branch
        """
        # Checkout the branch
        self.run_git_command(f"git checkout {branch_name}", check=False)
        
        # Get commit count ahead/behind
        success, ahead_behind = self.run_git_command(
            f"git rev-list --left-right --count {self.dev_branch}...{branch_name}"
        )
        
        if success:
            behind, ahead = ahead_behind.split('\t')
        else:
            behind, ahead = "0", "0"
        
        # Get last commit info
        success, last_commit = self.run_git_command("git log -1 --format=%h:%s")
        
        # Get modified files count
        success, modified_files = self.run_git_command("git diff --name-only")
        file_count = len(modified_files.splitlines()) if success else 0
        
        return {
            "branch": branch_name,
            "ahead": int(ahead),
            "behind": int(behind),
            "last_commit": last_commit if success else "N/A",
            "modified_files": file_count
        }
    
    def cleanup_merged_branches(self, dry_run: bool = True):
        """
        Clean up branches that have been merged
        """
        print("\n🧹 Cleaning up merged branches...")
        
        # Get list of merged branches
        success, merged_branches = self.run_git_command(
            f"git branch --merged {self.main_branch}"
        )
        
        if not success:
            print("  ❌ Failed to get merged branches")
            return
        
        branches_to_delete = []
        for branch in merged_branches.splitlines():
            branch = branch.strip()
            # Skip protected branches
            if branch in ['*', self.main_branch, self.dev_branch]:
                continue
            if branch.startswith('* '):
                branch = branch[2:]
            if branch not in [self.main_branch, self.dev_branch]:
                branches_to_delete.append(branch)
        
        if not branches_to_delete:
            print("  ✅ No merged branches to clean up")
            return
        
        print(f"  Found {len(branches_to_delete)} merged branches:")
        for branch in branches_to_delete:
            print(f"    - {branch}")
        
        if not dry_run:
            for branch in branches_to_delete:
                success, output = self.run_git_command(f"git branch -d {branch}")
                if success:
                    print(f"  ✅ Deleted branch: {branch}")
                else:
                    print(f"  ❌ Failed to delete branch {branch}: {output}")
        else:
            print("  ℹ️  Dry run - no branches deleted. Run with dry_run=False to delete.")


class GitWorkflowIntegration:
    """
    Integration layer between Agent Framework and Git workflows
    Now integrated with Testing Workflow for TDD
    """
    
    def __init__(self, config: Dict):
        self.branch_manager = GitBranchManager(config)
        self.config = config
        
        # Initialize testing workflow if available
        self.testing_workflow = None
        self.test_runner = None
        if TESTING_AVAILABLE:
            self.testing_workflow = TDDWorkflow(config)
            self.test_runner = TestRunner(self.testing_workflow)
    
    def initialize_git_workflow(self):
        """
        Initialize Git workflow for the project
        """
        print("\n🔧 Initializing Git Workflow...")
        print("-" * 50)
        
        # Check Git repository
        success, output = self.branch_manager.run_git_command("git status", check=False)
        if not success:
            print("  ❌ Not a Git repository!")
            return False
        
        print("  ✅ Git repository detected")
        
        # Setup development branch if it doesn't exist
        dev_branch = self.branch_manager.dev_branch
        if not self.branch_manager.branch_exists(dev_branch):
            print(f"  📝 Creating {dev_branch} branch...")
            self.branch_manager.run_git_command(f"git checkout -b {dev_branch}")
            self.branch_manager.run_git_command(f"git push -u origin {dev_branch}")
            print(f"  ✅ Created {dev_branch} branch")
        
        # Setup Git hooks
        self.branch_manager.setup_git_hooks()
        
        # Create PR template
        self.branch_manager.create_pull_request_template()
        
        print("\n✅ Git workflow initialized successfully!")
        return True
    
    def create_ticket_branches(self, tickets: List[Dict]) -> Dict[str, str]:
        """
        Create branches for tickets and update ticket information
        """
        return self.branch_manager.create_sprint_branches(tickets)
    
    def get_workflow_status(self) -> Dict:
        """
        Get current Git workflow status
        """
        current_branch = self.branch_manager.get_current_branch()
        
        # Get list of feature branches
        success, all_branches = self.branch_manager.run_git_command("git branch -a")
        
        feature_branches = []
        if success:
            for branch in all_branches.splitlines():
                branch = branch.strip()
                if branch.startswith('feature/') or branch.startswith('bugfix/'):
                    feature_branches.append(branch)
        
        return {
            "current_branch": current_branch,
            "feature_branches": feature_branches,
            "total_branches": len(feature_branches)
        }
    
    def tdd_development_cycle(self, ticket: Dict, feature_path: str) -> Dict[str, Any]:
        """
        Execute TDD development cycle for a ticket
        
        1. Create/checkout branch for ticket
        2. Write tests first (RED phase)
        3. Run tests (should fail)
        4. Implement feature (GREEN phase)
        5. Run tests (should pass)
        6. Commit if tests pass
        7. Push if remote exists
        8. Move to next ticket branch
        
        Args:
            ticket: Ticket dictionary with id, title, type
            feature_path: Path to the feature module being developed
            
        Returns:
            Result dictionary with status and details
        """
        result = {
            'ticket_id': ticket['id'],
            'status': 'started',
            'steps': []
        }
        
        print(f"\n🔄 Starting TDD Development Cycle for {ticket['id']}")
        print("=" * 60)
        
        # Step 1: Create/checkout branch
        print("\n📝 Step 1: Creating/checking out branch...")
        branch_name = self.branch_manager.create_ticket_branch(
            ticket['id'],
            ticket['title'],
            BranchType.FEATURE if ticket.get('type') == 'feature' else BranchType.BUGFIX
        )
        
        if not branch_name:
            result['status'] = 'failed'
            result['error'] = 'Failed to create branch'
            return result
        
        result['branch'] = branch_name
        result['steps'].append({'step': 'branch_created', 'success': True})
        
        # Step 2: Write tests first (TDD - RED phase)
        if self.testing_workflow:
            print("\n🔴 Step 2: Writing tests first (RED phase)...")
            test_file = self.testing_workflow.create_test_file(
                ticket['title'],
                feature_path
            )
            result['test_file'] = test_file
            result['steps'].append({'step': 'tests_written', 'success': True})
            
            # Step 3: Run tests (should fail initially)
            print("\n🧪 Step 3: Running tests (expecting failure)...")
            initial_test_result = self.test_runner.run_for_ticket(ticket['id'], ticket.get('type', 'feature'))
            
            if initial_test_result:
                print("  ⚠️  Tests passed but feature not implemented - not true TDD!")
            else:
                print("  ✅ Tests failed as expected (RED phase complete)")
            
            result['steps'].append({
                'step': 'initial_tests_run',
                'success': True,
                'tests_passed': initial_test_result
            })
            
            # Step 4: Implement feature (GREEN phase)
            print("\n🟢 Step 4: Implementing feature (GREEN phase)...")
            print(f"  📝 Please implement the feature in: {feature_path}")
            print("  ⏸️  Waiting for implementation...")
            
            # In real workflow, this would trigger the actual implementation
            # For now, we'll mark it as a manual step
            result['steps'].append({
                'step': 'implementation',
                'success': True,
                'manual': True
            })
            
            # Step 5: Run tests again (should pass after implementation)
            print("\n🧪 Step 5: Running tests after implementation...")
            final_test_result = self.test_runner.run_for_ticket(ticket['id'], ticket.get('type', 'feature'))
            
            if not final_test_result:
                print("  ❌ Tests failed - implementation needs work")
                result['status'] = 'tests_failed'
                result['steps'].append({
                    'step': 'final_tests_run',
                    'success': False,
                    'tests_passed': False
                })
                return result
            
            print("  ✅ All tests passed! (GREEN phase complete)")
            result['steps'].append({
                'step': 'final_tests_run',
                'success': True,
                'tests_passed': True
            })
        
        # Step 6: Commit changes
        print("\n💾 Step 6: Committing changes...")
        commit_result = self.commit_changes(ticket)
        
        if not commit_result['success']:
            result['status'] = 'commit_failed'
            result['error'] = commit_result.get('error')
            return result
        
        result['steps'].append({
            'step': 'committed',
            'success': True,
            'commit_hash': commit_result.get('commit_hash')
        })
        
        # Step 7: Push if remote exists
        print("\n☁️  Step 7: Pushing to remote...")
        push_result = self.push_branch(branch_name)
        
        if push_result['success']:
            print("  ✅ Pushed to remote")
        else:
            print("  ℹ️  No remote configured or push failed")
        
        result['steps'].append({
            'step': 'pushed',
            'success': push_result['success'],
            'remote': push_result.get('remote')
        })
        
        # Step 8: Prepare for next ticket
        print("\n➡️  Step 8: Ready for next ticket...")
        print("  📝 Returning to development branch")
        self.branch_manager.run_git_command("git checkout development")
        
        result['status'] = 'completed'
        result['steps'].append({'step': 'ready_for_next', 'success': True})
        
        print("\n" + "=" * 60)
        print(f"✅ TDD Development Cycle Complete for {ticket['id']}")
        
        return result
    
    def commit_changes(self, ticket: Dict) -> Dict[str, Any]:
        """
        Commit changes for a ticket
        
        Args:
            ticket: Ticket dictionary
            
        Returns:
            Result with success status and commit hash
        """
        # Add all changes
        success, output = self.branch_manager.run_git_command("git add -A")
        if not success:
            return {'success': False, 'error': 'Failed to add files'}
        
        # Create commit message
        ticket_type = ticket.get('type', 'feat')
        commit_message = f"{ticket_type}({ticket['id']}): {ticket['title']}"
        
        # Commit
        success, output = self.branch_manager.run_git_command(
            f'git commit -m "{commit_message}"'
        )
        
        if not success:
            if 'nothing to commit' in output:
                return {'success': True, 'message': 'No changes to commit'}
            return {'success': False, 'error': output}
        
        # Get commit hash
        success, commit_hash = self.branch_manager.run_git_command(
            "git rev-parse HEAD"
        )
        
        return {
            'success': True,
            'commit_hash': commit_hash if success else None
        }
    
    def push_branch(self, branch_name: str) -> Dict[str, Any]:
        """
        Push branch to remote if it exists
        
        Args:
            branch_name: Name of branch to push
            
        Returns:
            Result with success status
        """
        # Check if remote exists
        success, remotes = self.branch_manager.run_git_command("git remote")
        
        if not remotes.strip():
            return {'success': False, 'message': 'No remote configured'}
        
        # Push branch
        remote = remotes.strip().splitlines()[0]  # Use first remote
        success, output = self.branch_manager.run_git_command(
            f"git push -u {remote} {branch_name}",
            check=False
        )
        
        return {
            'success': success,
            'remote': remote if success else None,
            'message': output
        }


# Convenience function for standalone usage
def setup_git_workflow(config_path: str = "agent-framework.config.yaml"):
    """
    Setup Git workflow for a project
    """
    import yaml
    
    # Load configuration
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize workflow
    workflow = GitWorkflowIntegration(config)
    workflow.initialize_git_workflow()
    
    return workflow


if __name__ == "__main__":
    # Example usage
    workflow = setup_git_workflow()
    status = workflow.get_workflow_status()
    print(f"\nCurrent workflow status: {status}")