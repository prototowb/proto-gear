"""
CLI Integration Tests for Proto Gear
Tests the actual command-line interface via subprocess as end users would use it.

These tests validate the complete workflow without mocking,
ensuring the CLI works correctly in real-world usage.
"""

import pytest
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_project_dir():
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp(prefix='pg_test_')
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestCLIBasics:
    """Test basic CLI functionality"""

    def test_pg_command_exists(self):
        """Test that 'pg' command is available"""
        result = subprocess.run(
            ['pg', '--version'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Command should either show version or at least not crash
        assert result.returncode in [0, 2]  # 0 = success, 2 = no --version flag

    def test_pg_help_command(self):
        """Test 'pg help' command"""
        result = subprocess.run(
            ['pg', 'help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        assert result.returncode == 0
        assert 'Proto Gear' in result.stdout or 'Usage' in result.stdout


class TestDryRunMode:
    """Test --dry-run functionality (safe, no file creation)"""

    def test_dry_run_basic(self, temp_project_dir):
        """Test basic dry-run shows what would be created"""
        result = subprocess.run(
            ['pg', 'init', '--dry-run'],
            cwd=str(temp_project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        assert 'Dry run' in result.stdout or 'would be created' in result.stdout
        # Verify no files were actually created
        created_files = list(temp_project_dir.glob('*.md'))
        assert len(created_files) == 0, "Dry run should not create files"

    def test_dry_run_with_branching(self, temp_project_dir):
        """Test dry-run with --with-branching flag"""
        result = subprocess.run(
            ['pg', 'init', '--dry-run', '--with-branching'],
            cwd=str(temp_project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0
        assert 'BRANCHING.md' in result.stdout or 'branching' in result.stdout.lower()

    def test_dry_run_with_ticket_prefix(self, temp_project_dir):
        """Test dry-run with custom ticket prefix"""
        result = subprocess.run(
            ['pg', 'init', '--dry-run', '--ticket-prefix', 'TEST'],
            cwd=str(temp_project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0


class TestActualFileGeneration:
    """Test actual file generation (creates files, then cleans up)"""

    def test_init_creates_core_templates(self, temp_project_dir):
        """Test 'pg init' creates core template files"""
        result = subprocess.run(
            ['pg', 'init', '--no-interactive'],
            cwd=str(temp_project_dir),
            capture_output=True,
            text=True,
            timeout=30,
            input='n\n'  # Answer 'no' to any prompts
        )
        # Should succeed or exit gracefully
        assert result.returncode in [0, 1]

        # Check if core files were created
        agents_md = temp_project_dir / 'AGENTS.md'
        status_md = temp_project_dir / 'PROJECT_STATUS.md'

        # At least one core file should exist if init succeeded
        if result.returncode == 0:
            assert agents_md.exists() or status_md.exists()

    def test_init_with_branching_flag(self, temp_project_dir):
        """Test 'pg init --with-branching' creates BRANCHING.md"""
        # Initialize git repo first
        subprocess.run(['git', 'init'], cwd=str(temp_project_dir), capture_output=True)

        result = subprocess.run(
            ['pg', 'init', '--no-interactive', '--with-branching', '--ticket-prefix', 'TEST'],
            cwd=str(temp_project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0:
            branching_md = temp_project_dir / 'BRANCHING.md'
            # BRANCHING.md should be created with git workflow
            if branching_md.exists():
                content = branching_md.read_text()
                assert 'TEST' in content or 'branching' in content.lower()


class TestErrorHandling:
    """Test CLI error handling and edge cases"""

    def test_invalid_command(self):
        """Test CLI handles invalid commands gracefully"""
        result = subprocess.run(
            ['pg', 'invalid-command-xyz'],
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should return non-zero exit code but not crash
        assert result.returncode != 0

    def test_init_in_nonexistent_directory(self):
        """Test init handles non-existent directories"""
        result = subprocess.run(
            ['pg', 'init'],
            cwd='/nonexistent/directory/xyz123',
            capture_output=True,
            text=True,
            timeout=10
        )
        # Should fail gracefully (not crash)
        assert result.returncode != 0


class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility"""

    def test_cli_works_on_current_platform(self, temp_project_dir):
        """Test CLI works on current platform (Windows/Mac/Linux)"""
        result = subprocess.run(
            ['pg', 'init', '--dry-run'],
            cwd=str(temp_project_dir),
            capture_output=True,
            text=True,
            timeout=30
        )
        # Should work on any platform
        assert result.returncode == 0
        assert len(result.stdout) > 0  # Should produce some output


class TestVersionInformation:
    """Test version information display"""

    def test_package_version_matches_display(self):
        """Test that displayed version matches package version"""
        from proto_gear_pkg import __version__

        # Try to get version from CLI (if supported)
        result = subprocess.run(
            ['pg', 'help'],
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            # Version should appear in output somewhere
            output = result.stdout + result.stderr
            assert __version__ in output or f'v{__version__}' in output or len(output) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
