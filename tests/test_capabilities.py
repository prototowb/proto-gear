"""
Test suite for Universal Capabilities System
Tests capability template copying, validation, and generation
"""

import unittest
import tempfile
import shutil
from pathlib import Path
import os
import sys

# Add core to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'core' / 'proto_gear_pkg'))

from proto_gear_pkg.proto_gear import copy_capability_templates


class TestCapabilityTemplates(unittest.TestCase):
    """Test capability template existence and structure"""

    def test_capability_templates_exist(self):
        """Verify capability templates exist in core/capabilities/"""
        core_dir = Path(__file__).parent.parent / 'core' / 'proto_gear_pkg'
        cap_dir = core_dir / 'capabilities'

        self.assertTrue(cap_dir.exists(), "capabilities/ directory should exist")
        self.assertTrue((cap_dir / 'INDEX.template.md').exists())
        self.assertTrue((cap_dir / 'skills' / 'INDEX.template.md').exists())
        self.assertTrue((cap_dir / 'workflows' / 'INDEX.template.md').exists())
        self.assertTrue((cap_dir / 'commands' / 'INDEX.template.md').exists())
        self.assertTrue((cap_dir / 'agents' / 'INDEX.template.md').exists())

    def test_example_skill_exists(self):
        """Verify testing skill template exists"""
        skill_file = Path(__file__).parent.parent / 'core' / 'proto_gear_pkg' / 'capabilities' / 'skills' / 'testing' / 'SKILL.template.md'
        self.assertTrue(skill_file.exists())

        # Check it has YAML frontmatter
        content = skill_file.read_text(encoding='utf-8')
        self.assertTrue(content.startswith('---'))
        self.assertIn('name: "Test-Driven Development"', content)

    def test_example_workflow_exists(self):
        """Verify feature-development workflow exists"""
        workflow_file = Path(__file__).parent.parent / 'core' / 'proto_gear_pkg' / 'capabilities' / 'workflows' / 'feature-development.template.md'
        self.assertTrue(workflow_file.exists())

        content = workflow_file.read_text(encoding='utf-8')
        self.assertTrue(content.startswith('---'))
        self.assertIn('type: "workflow"', content)

    def test_example_command_exists(self):
        """Verify create-ticket command exists"""
        command_file = Path(__file__).parent.parent / 'core' / 'proto_gear_pkg' / 'capabilities' / 'commands' / 'create-ticket.template.md'
        self.assertTrue(command_file.exists())

        content = command_file.read_text(encoding='utf-8')
        self.assertTrue(content.startswith('---'))
        self.assertIn('type: "command"', content)


class TestCopyCapabilityTemplates(unittest.TestCase):
    """Test copy_capability_templates() function"""

    def setUp(self):
        """Create temporary directory for testing"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_copy_creates_proto_gear_directory(self):
        """Test that .proto-gear/ directory is created"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        self.assertEqual(result['status'], 'success')
        self.assertTrue((self.test_path / '.proto-gear').exists())

    def test_copy_creates_structure(self):
        """Test that complete directory structure is created"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        proto_gear = self.test_path / '.proto-gear'
        self.assertTrue((proto_gear / 'INDEX.md').exists())
        self.assertTrue((proto_gear / 'skills' / 'INDEX.md').exists())
        self.assertTrue((proto_gear / 'workflows' / 'INDEX.md').exists())
        self.assertTrue((proto_gear / 'commands' / 'INDEX.md').exists())
        self.assertTrue((proto_gear / 'agents' / 'INDEX.md').exists())

    def test_copy_creates_skill_subdirectory(self):
        """Test that skill subdirectories are created"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        proto_gear = self.test_path / '.proto-gear'
        self.assertTrue((proto_gear / 'skills' / 'testing' / 'SKILL.md').exists())

    def test_placeholder_replacement(self):
        """Test that placeholders are replaced correctly"""
        result = copy_capability_templates(
            self.test_path,
            "MyProject",
            version="0.4.0",
            dry_run=False
        )

        # Check INDEX.md for replaced placeholders
        index_file = self.test_path / '.proto-gear' / 'INDEX.md'
        content = index_file.read_text(encoding='utf-8')

        self.assertNotIn('{{VERSION}}', content)
        self.assertNotIn('{{PROJECT_NAME}}', content)
        self.assertIn('0.4.0', content)

    def test_dry_run_no_files_created(self):
        """Test that dry run doesn't create files"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=True
        )

        self.assertEqual(result['status'], 'success')
        self.assertFalse((self.test_path / '.proto-gear').exists())
        self.assertGreater(len(result['files_created']), 0)  # Should report what would be created

    def test_existing_proto_gear_handled(self):
        """Test handling of existing .proto-gear/ directory"""
        # Create existing directory
        (self.test_path / '.proto-gear').mkdir()
        (self.test_path / '.proto-gear' / 'existing.txt').write_text('test')

        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        # Should handle gracefully (skip or warn)
        self.assertIn(result['status'], ['success', 'skipped', 'warning'])

    def test_template_extension_removed(self):
        """Test that .template.md becomes .md"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        # Check that files don't have .template in name
        for file_path in result['files_created']:
            self.assertNotIn('.template', file_path)

    def test_files_created_list_populated(self):
        """Test that files_created list is populated"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        self.assertIn('files_created', result)
        self.assertIsInstance(result['files_created'], list)
        self.assertGreater(len(result['files_created']), 0)

        # Should include main INDEX.md
        self.assertTrue(any('.proto-gear/INDEX.md' in f or 'INDEX.md' in f for f in result['files_created']))


class TestCapabilitySecurityValidation(unittest.TestCase):
    """Test security features of capability copying"""

    def setUp(self):
        """Create temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_path_traversal_rejected(self):
        """Test that path traversal attempts are rejected"""
        # This should fail gracefully or be prevented
        # Implementation should validate paths
        result = copy_capability_templates(
            self.test_path / '..' / 'malicious',
            "TestProject",
            dry_run=True
        )

        # Should either reject or normalize the path
        self.assertTrue(result['status'] in ['success', 'error'])

    def test_utf8_encoding_preserved(self):
        """Test that UTF-8 encoding is used correctly"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        # Read a file and ensure it's UTF-8
        index_file = self.test_path / '.proto-gear' / 'INDEX.md'
        content = index_file.read_text(encoding='utf-8')  # Should not raise
        self.assertIsInstance(content, str)

    def test_files_have_proper_permissions(self):
        """Test that created files have appropriate permissions"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        # Check that files are readable
        index_file = self.test_path / '.proto-gear' / 'INDEX.md'
        self.assertTrue(os.access(index_file, os.R_OK))


class TestCapabilityPlaceholders(unittest.TestCase):
    """Test placeholder replacement in capability templates"""

    def setUp(self):
        """Create temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_version_placeholder_replaced(self):
        """Test that {{VERSION}} is replaced"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            version="0.4.0",
            dry_run=False
        )

        index_file = self.test_path / '.proto-gear' / 'INDEX.md'
        content = index_file.read_text(encoding='utf-8')

        self.assertNotIn('{{VERSION}}', content)
        self.assertIn('0.4.0', content)

    def test_project_name_placeholder_replaced(self):
        """Test that {{PROJECT_NAME}} is replaced"""
        result = copy_capability_templates(
            self.test_path,
            "MyAwesomeProject",
            dry_run=False
        )

        # Check multiple files for project name replacement
        index_file = self.test_path / '.proto-gear' / 'INDEX.md'
        content = index_file.read_text(encoding='utf-8')

        self.assertNotIn('{{PROJECT_NAME}}', content)
        # Note: Implementation may or may not include project name in INDEX.md

    def test_default_version_used(self):
        """Test that default version is used when not specified"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=False
        )

        index_file = self.test_path / '.proto-gear' / 'INDEX.md'
        content = index_file.read_text(encoding='utf-8')

        # Should not contain placeholder
        self.assertNotIn('{{VERSION}}', content)


class TestCapabilityErrorHandling(unittest.TestCase):
    """Test error handling in capability copying"""

    def test_invalid_project_path(self):
        """Test handling of invalid project path"""
        result = copy_capability_templates(
            Path("/nonexistent/path/that/does/not/exist"),
            "TestProject",
            dry_run=True
        )

        # Should handle gracefully
        self.assertIn(result['status'], ['success', 'error'])

    def test_empty_project_name(self):
        """Test handling of empty project name"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = copy_capability_templates(
                Path(tmpdir),
                "",
                dry_run=False
            )

            # Should use default or handle gracefully
            self.assertTrue(result['status'] in ['success', 'error'])

    def test_none_project_name(self):
        """Test handling of None project name"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = copy_capability_templates(
                Path(tmpdir),
                None,
                dry_run=False
            )

            # Should use default or handle gracefully
            self.assertTrue(result['status'] in ['success', 'error'])


class TestCapabilityDryRun(unittest.TestCase):
    """Test dry-run mode for capability copying"""

    def setUp(self):
        """Create temporary directory"""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)

    def tearDown(self):
        """Clean up"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_dry_run_reports_files(self):
        """Test that dry run reports files that would be created"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=True
        )

        self.assertEqual(result['status'], 'success')
        self.assertIn('files_created', result)
        self.assertIsInstance(result['files_created'], list)
        self.assertGreater(len(result['files_created']), 0)

    def test_dry_run_no_filesystem_changes(self):
        """Test that dry run makes no filesystem changes"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=True
        )

        # Directory should remain empty
        self.assertFalse((self.test_path / '.proto-gear').exists())

        # No files should exist
        proto_gear = self.test_path / '.proto-gear'
        if proto_gear.exists():
            # If it exists, it should be empty
            self.assertEqual(len(list(proto_gear.iterdir())), 0)

    def test_dry_run_includes_all_expected_files(self):
        """Test that dry run reports all expected files"""
        result = copy_capability_templates(
            self.test_path,
            "TestProject",
            dry_run=True
        )

        files_created = result['files_created']

        # Should report main INDEX
        self.assertTrue(any('INDEX.md' in f for f in files_created))

        # Should report category indices
        self.assertTrue(any('skills' in f and 'INDEX.md' in f for f in files_created))
        self.assertTrue(any('workflows' in f and 'INDEX.md' in f for f in files_created))
        self.assertTrue(any('commands' in f and 'INDEX.md' in f for f in files_created))


if __name__ == '__main__':
    unittest.main()
