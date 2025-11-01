"""
Tests for git_workflow.py
Testing Git branch management and workflow integration
"""

import sys
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Add core to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from git_workflow import (
    BranchType,
    GitBranchManager,
    GitWorkflowIntegration
)


class TestBranchType:
    """Test BranchType enumeration"""

    def test_branch_types_defined(self):
        """Test that all branch types are defined"""
        assert BranchType.FEATURE
        assert BranchType.BUGFIX
        assert BranchType.HOTFIX
        assert BranchType.RELEASE
        assert BranchType.EXPERIMENTAL

    def test_branch_type_values(self):
        """Test branch type values are correct"""
        assert BranchType.FEATURE.value == "feature"
        assert BranchType.BUGFIX.value == "bugfix"
        assert BranchType.HOTFIX.value == "hotfix"
        assert BranchType.RELEASE.value == "release"
        assert BranchType.EXPERIMENTAL.value == "experimental"


class TestGitBranchManager:
    """Test GitBranchManager class"""

    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            'git': {
                'main_branch': 'main',
                'dev_branch': 'development',
                'branch_prefix': {
                    'feature': 'feature/',
                    'bugfix': 'bugfix/'
                }
            },
            'tickets': {
                'prefix': 'PROTO'
            }
        }

    @pytest.fixture
    def manager(self, config):
        """Create GitBranchManager instance"""
        return GitBranchManager(config)

    def test_initialization(self, manager):
        """Test GitBranchManager initialization"""
        assert manager.main_branch == 'main'
        assert manager.dev_branch == 'development'
        assert manager.ticket_prefix == 'PROTO'

    def test_sanitize_branch_name(self, manager):
        """Test branch name sanitization"""
        # Test basic sanitization
        result = manager._sanitize_branch_name("Add New Feature")
        assert result == "add-new-feature"

        # Test special characters
        result = manager._sanitize_branch_name("Fix: Bug in API!")
        assert result == "fix-bug-in-api"

        # Test multiple spaces/hyphens
        result = manager._sanitize_branch_name("Fix   Multiple   Spaces")
        assert result == "fix-multiple-spaces"

        # Test length truncation
        long_title = "This is a very long title that should be truncated to fit max length"
        result = manager._sanitize_branch_name(long_title, max_length=30)
        assert len(result) <= 30

        # Test leading/trailing hyphens removed
        result = manager._sanitize_branch_name("-Leading and Trailing-")
        assert not result.startswith('-')
        assert not result.endswith('-')

    @patch('subprocess.run')
    def test_run_git_command_success(self, mock_run, manager):
        """Test successful git command execution"""
        mock_run.return_value = Mock(
            stdout="output text",
            stderr="",
            returncode=0
        )

        success, output = manager.run_git_command("git status")
        assert success is True
        assert output == "output text"

    @patch('subprocess.run')
    def test_run_git_command_failure(self, mock_run, manager):
        """Test failed git command execution"""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(
            returncode=1,
            cmd="git status",
            stderr="error message"
        )

        success, output = manager.run_git_command("git status")
        assert success is False
        assert "error message" in output

    @patch('subprocess.run')
    def test_get_current_branch(self, mock_run, manager):
        """Test getting current branch"""
        mock_run.return_value = Mock(
            stdout="feature/test-branch\n",
            returncode=0
        )

        branch = manager.get_current_branch()
        assert branch == "feature/test-branch"

    @patch('subprocess.run')
    def test_branch_exists_true(self, mock_run, manager):
        """Test branch exists check when branch exists"""
        mock_run.return_value = Mock(
            stdout="  feature/test-branch",
            returncode=0
        )

        exists = manager.branch_exists("feature/test-branch")
        assert exists is True

    @patch('subprocess.run')
    def test_branch_exists_false(self, mock_run, manager):
        """Test branch exists check when branch doesn't exist"""
        mock_run.return_value = Mock(
            stdout="",
            returncode=0
        )

        exists = manager.branch_exists("nonexistent-branch")
        assert exists is False

    @patch.object(GitBranchManager, 'branch_exists')
    @patch.object(GitBranchManager, 'run_git_command')
    def test_create_ticket_branch_already_exists(self, mock_run_cmd, mock_exists, manager):
        """Test creating ticket branch when it already exists"""
        mock_exists.return_value = True

        result = manager.create_ticket_branch("PROTO-001", "Add feature")

        # Should return branch name even if exists
        assert "proto-001" in result.lower()
        assert "add-feature" in result.lower()

    @patch.object(GitBranchManager, 'branch_exists')
    @patch.object(GitBranchManager, 'get_current_branch')
    @patch.object(GitBranchManager, 'run_git_command')
    def test_create_ticket_branch_success(self, mock_run_cmd, mock_get_branch, mock_exists, manager):
        """Test successful ticket branch creation"""
        mock_exists.return_value = False
        mock_get_branch.return_value = "development"
        mock_run_cmd.return_value = (True, "")

        result = manager.create_ticket_branch("PROTO-001", "Add new feature", BranchType.FEATURE)

        assert result is not None
        assert "feature/" in result
        assert "proto-001" in result
        assert "add-new-feature" in result

    @patch.object(GitBranchManager, 'branch_exists')
    @patch.object(GitBranchManager, 'get_current_branch')
    @patch.object(GitBranchManager, 'run_git_command')
    def test_create_ticket_branch_switch_to_dev_fails(self, mock_run_cmd, mock_get_branch, mock_exists, manager):
        """Test branch creation when switching to dev branch fails"""
        mock_exists.return_value = False
        mock_get_branch.return_value = "main"  # Not on development

        # First call (checkout development) fails
        mock_run_cmd.side_effect = [(False, "error"), (True, "")]

        result = manager.create_ticket_branch("PROTO-001", "Add feature")

        assert result is None

    @patch.object(GitBranchManager, 'create_ticket_branch')
    @patch.object(GitBranchManager, 'run_git_command')
    def test_create_sprint_branches(self, mock_run_cmd, mock_create_branch, manager):
        """Test creating multiple sprint branches"""
        mock_create_branch.side_effect = [
            "feature/proto-001-feature-one",
            "bugfix/proto-002-fix-bug"
        ]
        mock_run_cmd.return_value = (True, "")

        tickets = [
            {'id': 'PROTO-001', 'title': 'Feature One', 'type': 'feature'},
            {'id': 'PROTO-002', 'title': 'Fix Bug', 'type': 'bugfix'}
        ]

        result = manager.create_sprint_branches(tickets)

        assert len(result) == 2
        assert 'PROTO-001' in result
        assert 'PROTO-002' in result
        assert tickets[0]['branch'] == "feature/proto-001-feature-one"
        assert tickets[1]['branch'] == "bugfix/proto-002-fix-bug"

    def test_create_sprint_branches_with_hotfix(self, manager):
        """Test branch type determination for hotfix"""
        with patch.object(manager, 'create_ticket_branch') as mock_create:
            with patch.object(manager, 'run_git_command') as mock_run:
                mock_create.return_value = "hotfix/proto-003-critical"
                mock_run.return_value = (True, "")

                tickets = [
                    {'id': 'PROTO-003', 'title': 'Critical Fix', 'type': 'hotfix'}
                ]

                manager.create_sprint_branches(tickets)

                # Verify hotfix branch type was used
                mock_create.assert_called_once_with(
                    'PROTO-003',
                    'Critical Fix',
                    BranchType.HOTFIX
                )

    @patch('subprocess.run')
    def test_get_branch_status(self, mock_run, manager):
        """Test getting branch status"""
        # Mock multiple git commands
        mock_run.side_effect = [
            Mock(stdout="", returncode=0),  # checkout
            Mock(stdout="2\t3", returncode=0),  # rev-list
            Mock(stdout="abc123:Test commit", returncode=0),  # log
            Mock(stdout="file1.py\nfile2.py", returncode=0)  # diff
        ]

        status = manager.get_branch_status("feature/test")

        assert status['branch'] == "feature/test"
        assert status['ahead'] == 3
        assert status['behind'] == 2
        assert status['last_commit'] == "abc123:Test commit"
        assert status['modified_files'] == 2

    @patch('subprocess.run')
    def test_cleanup_merged_branches_dry_run(self, mock_run, manager):
        """Test cleanup of merged branches in dry run mode"""
        mock_run.return_value = Mock(
            stdout="  feature/old-branch\n  bugfix/fixed-bug\n  * development",
            returncode=0
        )

        # Should not delete in dry run
        manager.cleanup_merged_branches(dry_run=True)

        # Verify no delete commands were run
        delete_calls = [call for call in mock_run.call_args_list
                       if 'branch -d' in str(call)]
        assert len(delete_calls) == 0

    @patch('subprocess.run')
    def test_cleanup_merged_branches_no_branches(self, mock_run, manager):
        """Test cleanup when no branches need cleaning"""
        mock_run.return_value = Mock(
            stdout="  * development\n  main",
            returncode=0
        )

        manager.cleanup_merged_branches(dry_run=False)

        # Should not attempt to delete protected branches


class TestGitWorkflowIntegration:
    """Test GitWorkflowIntegration class"""

    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            'git': {
                'main_branch': 'main',
                'dev_branch': 'development'
            },
            'tickets': {
                'prefix': 'PROTO'
            }
        }

    @pytest.fixture
    def workflow(self, config):
        """Create GitWorkflowIntegration instance"""
        return GitWorkflowIntegration(config)

    def test_initialization(self, workflow):
        """Test GitWorkflowIntegration initialization"""
        assert workflow.branch_manager is not None
        assert workflow.config is not None

    @patch.object(GitBranchManager, 'run_git_command')
    @patch.object(GitBranchManager, 'branch_exists')
    def test_initialize_git_workflow_success(self, mock_exists, mock_run_cmd, workflow):
        """Test successful Git workflow initialization"""
        mock_run_cmd.return_value = (True, "clean working tree")
        mock_exists.return_value = True

        result = workflow.initialize_git_workflow()

        assert result is True

    @patch.object(GitBranchManager, 'run_git_command')
    def test_initialize_git_workflow_not_git_repo(self, mock_run_cmd, workflow):
        """Test initialization when not a Git repository"""
        mock_run_cmd.return_value = (False, "not a git repository")

        result = workflow.initialize_git_workflow()

        assert result is False

    @patch.object(GitBranchManager, 'create_sprint_branches')
    def test_create_ticket_branches(self, mock_create_sprint, workflow):
        """Test creating ticket branches"""
        tickets = [{'id': 'PROTO-001', 'title': 'Test'}]
        mock_create_sprint.return_value = {'PROTO-001': 'feature/proto-001-test'}

        result = workflow.create_ticket_branches(tickets)

        assert 'PROTO-001' in result
        mock_create_sprint.assert_called_once_with(tickets)

    @patch.object(GitBranchManager, 'get_current_branch')
    @patch.object(GitBranchManager, 'run_git_command')
    def test_get_workflow_status(self, mock_run_cmd, mock_get_branch, workflow):
        """Test getting workflow status"""
        mock_get_branch.return_value = "development"
        mock_run_cmd.return_value = (True, "  feature/test-1\n  bugfix/test-2")

        status = workflow.get_workflow_status()

        assert status['current_branch'] == "development"
        assert len(status['feature_branches']) == 2
        assert status['total_branches'] == 2

    @patch.object(GitBranchManager, 'run_git_command')
    def test_commit_changes_success(self, mock_run_cmd, workflow):
        """Test successful commit"""
        mock_run_cmd.side_effect = [
            (True, ""),  # git add
            (True, ""),  # git commit
            (True, "abc123def")  # get commit hash
        ]

        ticket = {'id': 'PROTO-001', 'title': 'Test Feature', 'type': 'feat'}
        result = workflow.commit_changes(ticket)

        assert result['success'] is True
        assert result['commit_hash'] == "abc123def"

    @patch.object(GitBranchManager, 'run_git_command')
    def test_commit_changes_nothing_to_commit(self, mock_run_cmd, workflow):
        """Test commit when there are no changes"""
        mock_run_cmd.side_effect = [
            (True, ""),  # git add
            (False, "nothing to commit")  # git commit
        ]

        ticket = {'id': 'PROTO-001', 'title': 'Test', 'type': 'feat'}
        result = workflow.commit_changes(ticket)

        assert result['success'] is True
        assert result['message'] == 'No changes to commit'

    @patch.object(GitBranchManager, 'run_git_command')
    def test_commit_changes_add_fails(self, mock_run_cmd, workflow):
        """Test commit when git add fails"""
        mock_run_cmd.return_value = (False, "error adding files")

        ticket = {'id': 'PROTO-001', 'title': 'Test', 'type': 'feat'}
        result = workflow.commit_changes(ticket)

        assert result['success'] is False
        assert 'Failed to add files' in result['error']

    @patch.object(GitBranchManager, 'run_git_command')
    def test_push_branch_success(self, mock_run_cmd, workflow):
        """Test successful branch push"""
        mock_run_cmd.side_effect = [
            (True, "origin"),  # git remote
            (True, "pushed")   # git push
        ]

        result = workflow.push_branch("feature/test")

        assert result['success'] is True
        assert result['remote'] == "origin"

    @patch.object(GitBranchManager, 'run_git_command')
    def test_push_branch_no_remote(self, mock_run_cmd, workflow):
        """Test push when no remote exists"""
        mock_run_cmd.return_value = (True, "")

        result = workflow.push_branch("feature/test")

        assert result['success'] is False
        assert 'No remote configured' in result['message']

    @patch.object(GitBranchManager, 'run_git_command')
    def test_push_branch_push_fails(self, mock_run_cmd, workflow):
        """Test push when git push fails"""
        mock_run_cmd.side_effect = [
            (True, "origin"),  # git remote
            (False, "authentication failed")  # git push
        ]

        result = workflow.push_branch("feature/test")

        assert result['success'] is False
        assert result['remote'] is None


class TestGitHooks:
    """Test Git hooks setup"""

    @pytest.fixture
    def config(self):
        return {
            'git': {'main_branch': 'main', 'dev_branch': 'development'},
            'tickets': {'prefix': 'PROTO'}
        }

    @pytest.fixture
    def manager(self, config):
        return GitBranchManager(config)

    def test_setup_git_hooks_no_git_dir(self, manager, capsys):
        """Test setup hooks when .git/hooks doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                manager.setup_git_hooks()
                captured = capsys.readouterr()
                assert "not found" in captured.out
            finally:
                os.chdir(original_dir)

    def test_create_pull_request_template(self, manager):
        """Test PR template creation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            import os
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                manager.create_pull_request_template()

                # Check if template was created
                pr_template_path = Path(".github/pull_request_template.md")
                assert pr_template_path.exists()

                # Check content
                content = pr_template_path.read_text(encoding='utf-8')
                assert "## 🎫 Ticket" in content
                assert "## ✅ Checklist" in content
                assert "## 🧪 Testing" in content
            finally:
                os.chdir(original_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
