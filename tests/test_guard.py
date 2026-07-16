"""
Tests for the branch guard (steering-plan Phase 5).
"""

import subprocess

import pytest

from proto_gear_pkg.module_core import guard


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, check=True)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init")
    _git(tmp_path, "config", "user.email", "t@example.com")
    _git(tmp_path, "config", "user.name", "T")
    _git(tmp_path, "commit", "--allow-empty", "-m", "init")
    _git(tmp_path, "branch", "-M", "main")
    return tmp_path


class TestCurrentBranch:
    def test_returns_branch(self, repo):
        assert guard.current_branch(str(repo)) == "main"

    def test_none_outside_repo(self, tmp_path):
        assert guard.current_branch(str(tmp_path)) is None


class TestCheckProtectedBranch:
    def test_blocks_on_main(self, repo):
        result = guard.check_protected_branch(cwd=str(repo))
        assert result.ok is False
        assert result.exit_code == 1
        assert result.branch == "main"
        assert "protected branch 'main'" in result.message

    def test_allows_on_feature(self, repo):
        _git(repo, "switch", "-c", "feature/x")
        result = guard.check_protected_branch(cwd=str(repo))
        assert result.ok is True
        assert result.exit_code == 0
        assert result.branch == "feature/x"

    def test_custom_protected_list(self, repo):
        _git(repo, "switch", "-c", "release")
        result = guard.check_protected_branch(protected=["release"], cwd=str(repo))
        assert result.ok is False
        # 'main' is no longer protected under the custom list
        _git(repo, "switch", "main")
        assert guard.check_protected_branch(protected=["release"], cwd=str(repo)).ok

    def test_passes_when_not_a_repo(self, tmp_path):
        # Can't determine a branch → don't block (never false-positive).
        result = guard.check_protected_branch(cwd=str(tmp_path))
        assert result.ok is True
        assert result.branch is None
