"""
Tests for git hook installation (steering-plan Phase 5).
"""

import subprocess

import pytest

from proto_gear_pkg.module_core import hooks


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, check=True)


@pytest.fixture
def repo(tmp_path):
    _git(tmp_path, "init")
    return tmp_path


class TestGitHooksDir:
    def test_resolves_in_repo(self, repo):
        d = hooks.git_hooks_dir(str(repo))
        assert d is not None
        assert d.name == "hooks"

    def test_none_outside_repo(self, tmp_path):
        assert hooks.git_hooks_dir(str(tmp_path)) is None


class TestInstallPreCommit:
    def test_not_a_repo(self, tmp_path):
        assert hooks.install_pre_commit(cwd=str(tmp_path))["status"] == "not-a-repo"

    def test_fresh_install(self, repo):
        result = hooks.install_pre_commit(cwd=str(repo))
        assert result["status"] == "installed"
        from pathlib import Path

        content = Path(result["path"]).read_text(encoding="utf-8")
        assert hooks.BRANCH_GUARD_MARKER in content
        assert "pg guard branch" in content

    def test_idempotent(self, repo):
        hooks.install_pre_commit(cwd=str(repo))
        assert hooks.install_pre_commit(cwd=str(repo))["status"] == "already-present"

    def test_existing_different_hook_not_clobbered(self, repo):
        from pathlib import Path

        hooks_dir = hooks.git_hooks_dir(str(repo))
        hook = hooks_dir / "pre-commit"
        hook.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
        result = hooks.install_pre_commit(cwd=str(repo))
        assert result["status"] == "exists-different"
        # unchanged
        assert "echo custom" in hook.read_text(encoding="utf-8")

    def test_force_overwrites_with_backup(self, repo):
        from pathlib import Path

        hooks_dir = hooks.git_hooks_dir(str(repo))
        hook = hooks_dir / "pre-commit"
        hook.write_text("#!/bin/sh\necho custom\n", encoding="utf-8")
        result = hooks.install_pre_commit(cwd=str(repo), force=True)
        assert result["status"] == "overwritten"
        assert hooks.BRANCH_GUARD_MARKER in hook.read_text(encoding="utf-8")
        backup = hooks_dir / "pre-commit.pre-guard.bak"
        assert "echo custom" in backup.read_text(encoding="utf-8")
